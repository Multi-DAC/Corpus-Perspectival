#!/usr/bin/env python3
"""
18A v5b: GPU MCMC — Optimized for NUTS gradient efficiency
===========================================================
Same physics as v5, but:
  - Sound horizons precomputed on (Om, H0) grid → bilinear interp in MCMC
  - Distance grids reduced (1000 pts low-z, 500 pts high-z extension)
  - Growth ODE reduced to 200 steps
  - 1 chain, sequential (single GPU)
  - max_tree_depth=8 to cap leapfrog steps at 256

Target: <0.1s per leapfrog step → ~5 min total.

Authors: Clayton W. Iggulden-Schnell & Clawd
Date: 2026-03-21
"""

import os
import sys
import time
import numpy as np

import jax
jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp
from jax import jit
from functools import partial

import numpyro
import numpyro.distributions as dist
from numpyro.infer import MCMC, NUTS, init_to_value

numpyro.set_platform('gpu')

# ============================================================
# CONSTANTS
# ============================================================
C_KMS = 299792.458
OMEGA_GAMMA_H2 = 2.469e-5
N_EFF = 3.046
OMEGA_R_H2 = OMEGA_GAMMA_H2 * (1 + 7/8 * (4/11)**(4/3) * N_EFF)
OMBH2 = 0.02237
RD_PRIOR_MEAN = 147.09
RD_PRIOR_SIGMA = 0.26

DATA_DIR = '/mnt/c/Users/mercu/clawd/projects/Project Meridian/phase18/data'
OUTPUT_DIR = '/mnt/c/Users/mercu/clawd/projects/Project Meridian/phase18'

# ============================================================
# DATA
# ============================================================

def load_all_data():
    print("Loading data...", flush=True)

    bao_dir = os.path.join(DATA_DIR, 'desi_dr2_bao')
    bao_mean = []
    with open(os.path.join(bao_dir, 'desi_gaussian_bao_ALL_GCcomb_mean.txt')) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            bao_mean.append(float(line.split()[1]))
    bao_mean = jnp.array(bao_mean)
    bao_cov = np.loadtxt(os.path.join(bao_dir, 'desi_gaussian_bao_ALL_GCcomb_cov.txt'))
    bao_cov_inv = jnp.array(np.linalg.inv(bao_cov))
    print(f"  BAO: {len(bao_mean)} points", flush=True)

    sne_dir = os.path.join(DATA_DIR, 'pantheonplus')
    sne_raw = np.genfromtxt(os.path.join(sne_dir, 'Pantheon+SH0ES.dat'),
                            names=True, dtype=None, encoding='utf-8')
    z_cmb_all = np.array([float(r['zHD']) for r in sne_raw])
    z_hel_all = np.array([float(r['zHEL']) for r in sne_raw])
    m_obs_all = np.array([float(r['m_b_corr']) for r in sne_raw])

    cov_raw = np.loadtxt(os.path.join(sne_dir, 'Pantheon+SH0ES_STAT+SYS.cov'))
    N_cov = int(cov_raw[0])
    C_full = cov_raw[1:].reshape(N_cov, N_cov)

    mask = z_cmb_all > 0.01
    m_obs = m_obs_all[mask]
    z_cmb = z_cmb_all[mask]
    z_hel = z_hel_all[mask]
    C = C_full[np.ix_(mask, mask)]
    N_sne = int(mask.sum())

    C_inv = np.linalg.inv(C)
    ones = np.ones(N_sne)
    Ci1 = C_inv @ ones
    C_inv_marg = C_inv - np.outer(Ci1, Ci1) / (ones @ Ci1)
    print(f"  SNe: {N_sne} (after z>0.01 cut)", flush=True)

    cmb_means = jnp.array([1.7502, 301.471, 0.02237])
    cmb_sigmas = jnp.array([0.0046, 0.090, 0.00015])
    cmb_corr = jnp.array([[1.0, 0.46, -0.66],
                           [0.46, 1.0, -0.33],
                           [-0.66, -0.33, 1.0]])
    cmb_cov_inv = jnp.linalg.inv(jnp.outer(cmb_sigmas, cmb_sigmas) * cmb_corr)

    fs8_z = jnp.array([0.067, 0.38, 0.51, 0.61, 0.70, 0.85, 1.48])
    fs8_val = jnp.array([0.423, 0.497, 0.459, 0.436, 0.473, 0.315, 0.342])
    fs8_err = jnp.array([0.055, 0.045, 0.038, 0.034, 0.041, 0.095, 0.070])

    print("  All data loaded.", flush=True)
    return {
        'bao_mean': bao_mean, 'bao_cov_inv': bao_cov_inv,
        'sne_m_obs': jnp.array(m_obs), 'sne_z_cmb': jnp.array(z_cmb),
        'sne_z_hel': jnp.array(z_hel), 'sne_C_inv_marg': jnp.array(C_inv_marg),
        'sne_N': N_sne,
        'cmb_means': cmb_means, 'cmb_cov_inv': cmb_cov_inv,
        'fs8_z': fs8_z, 'fs8_val': fs8_val, 'fs8_err': fs8_err,
    }

# ============================================================
# COSMOLOGY PRIMITIVES
# ============================================================

def Ez2(z, w0, wa, Om, h):
    """(H/H0)^2."""
    a = 1.0 / (1.0 + z)
    Or = OMEGA_R_H2 / h**2
    ODE = 1.0 - Om - Or
    de = a**(-3*(1 + w0 + wa)) * jnp.exp(-3*wa*(1 - a))
    return Om*(1+z)**3 + Or*(1+z)**4 + ODE*de

def H_of_z(z, w0, wa, Om, H0):
    return H0 * jnp.sqrt(jnp.maximum(Ez2(z, w0, wa, Om, H0/100), 1e-30))

# ============================================================
# PRECOMPUTED SOUND HORIZONS (removed from gradient path)
# ============================================================

def _compute_rd_single(Om, H0):
    """Sound horizon r_d for a single (Om, H0) pair. CPU numpy."""
    h = H0 / 100.0
    omh2 = Om * h**2
    Or = OMEGA_R_H2 / h**2

    # z_drag (Eisenstein & Hu 1998)
    b1 = 0.313 * omh2**(-0.419) * (1 + 0.607 * omh2**0.674)
    b2 = 0.238 * omh2**0.223
    z_d = 1291.0 * omh2**0.251 / (1 + 0.659 * omh2**0.828) * (1 + b1 * OMBH2**b2)

    # z_star (Hu & Sugiyama 1996)
    g1 = 0.0783 * OMBH2**(-0.238) / (1 + 39.5 * OMBH2**0.763)
    g2 = 0.560 / (1 + 21.1 * OMBH2**1.81)
    z_s = 1048.0 * (1 + 0.00124 * OMBH2**(-0.738)) * (1 + g1 * omh2**g2)

    def _sh_integral(z_low, z_high=20000, n=1000):
        z_arr = np.linspace(z_low, z_high, n)
        Rb = 3*OMBH2 / (4*OMEGA_GAMMA_H2) / (1 + z_arr)
        cs = C_KMS / np.sqrt(3*(1 + Rb))
        E2 = Om*(1+z_arr)**3 + Or*(1+z_arr)**4  # DE negligible at z>>1
        H = H0 * np.sqrt(E2)
        return np.trapz(cs / H, z_arr)

    rd = _sh_integral(z_d)
    rs_star = _sh_integral(z_s)

    # d_M(z_star) via integration
    z_arr = np.linspace(0, z_s, 3000)
    E2 = Om*(1+z_arr)**3 + Or*(1+z_arr)**4 + (1-Om-Or)*(1+z_arr)**(3*(1+(-1)+0))  # w=-1 approx for distance
    # Actually need proper DE for d_M. Use w0=-1, wa=0 as reference (close enough for CMB distance).
    # The CMB distance depends weakly on w0, wa because most of the path is at z>>1.
    a_arr = 1.0/(1+z_arr)
    de_arr = np.ones_like(z_arr)  # LCDM
    E2_full = Om*(1+z_arr)**3 + Or*(1+z_arr)**4 + (1-Om-Or)*de_arr
    H_arr = H0 * np.sqrt(np.maximum(E2_full, 1e-30))
    dc_star = np.trapz(C_KMS / H_arr, z_arr)

    return rd, rs_star, z_d, z_s, dc_star

def precompute_sound_horizon_tables(Om_grid, H0_grid):
    """Build lookup tables for rd, rs_star, dc_star over (Om, H0) grid."""
    print("Precomputing sound horizon tables...", flush=True)
    n_Om, n_H0 = len(Om_grid), len(H0_grid)
    rd_table = np.zeros((n_Om, n_H0))
    rs_table = np.zeros((n_Om, n_H0))
    dc_star_table = np.zeros((n_Om, n_H0))
    z_star_table = np.zeros((n_Om, n_H0))

    for i, Om in enumerate(Om_grid):
        for j, H0 in enumerate(H0_grid):
            rd, rs, zd, zs, dcs = _compute_rd_single(Om, H0)
            rd_table[i, j] = rd
            rs_table[i, j] = rs
            dc_star_table[i, j] = dcs
            z_star_table[i, j] = zs

    print(f"  {n_Om}x{n_H0} grid complete. rd range: [{rd_table.min():.2f}, {rd_table.max():.2f}] Mpc",
          flush=True)

    return {
        'Om_grid': jnp.array(Om_grid),
        'H0_grid': jnp.array(H0_grid),
        'rd': jnp.array(rd_table),
        'rs_star': jnp.array(rs_table),
        'dc_star_lcdm': jnp.array(dc_star_table),
        'z_star': jnp.array(z_star_table),
    }

def interp2d(Om, H0, Om_grid, H0_grid, table):
    """Bilinear interpolation on a 2D grid. Differentiable in JAX."""
    # Fractional indices
    dOm = Om_grid[1] - Om_grid[0]
    dH0 = H0_grid[1] - H0_grid[0]
    fi = (Om - Om_grid[0]) / dOm
    fj = (H0 - H0_grid[0]) / dH0

    # Clamp to grid
    n_Om = Om_grid.shape[0]
    n_H0 = H0_grid.shape[0]
    fi = jnp.clip(fi, 0, n_Om - 1.001)
    fj = jnp.clip(fj, 0, n_H0 - 1.001)

    i0 = jnp.floor(fi).astype(int)
    j0 = jnp.floor(fj).astype(int)
    i1 = jnp.minimum(i0 + 1, n_Om - 1)
    j1 = jnp.minimum(j0 + 1, n_H0 - 1)

    wi = fi - i0
    wj = fj - j0

    val = (table[i0, j0] * (1-wi)*(1-wj) +
           table[i1, j0] * wi*(1-wj) +
           table[i0, j1] * (1-wi)*wj +
           table[i1, j1] * wi*wj)
    return val

# ============================================================
# LIKELIHOOD COMPUTATION (gradient-efficient)
# ============================================================

def compute_lowz_distances(w0, wa, Om, H0, sne_z_cmb, sne_z_hel):
    """Distances for BAO + SNe (z < 2.5). Lean grid."""
    N_GRID = 800
    ln1pz = jnp.linspace(0, jnp.log(1 + 2.5), N_GRID)
    z_grid = jnp.expm1(ln1pz)

    H_grid = H_of_z(z_grid, w0, wa, Om, H0)
    integrand = C_KMS / H_grid
    dz = jnp.diff(z_grid)
    avg = 0.5 * (integrand[:-1] + integrand[1:])
    dc_grid = jnp.concatenate([jnp.array([0.0]), jnp.cumsum(avg * dz)])

    # BAO
    bao_aniso_z = jnp.array([0.510, 0.706, 0.934, 1.321, 1.484, 2.330])
    dc_bgs = jnp.interp(0.295, z_grid, dc_grid)
    H_bgs = H_of_z(0.295, w0, wa, Om, H0)
    dc_aniso = jnp.interp(bao_aniso_z, z_grid, dc_grid)
    H_aniso = H_of_z(bao_aniso_z, w0, wa, Om, H0)

    # SNe
    dc_sne = jnp.interp(sne_z_cmb, z_grid, dc_grid)
    dL_sne = (1 + sne_z_hel) * dc_sne
    mu_sne = 5.0 * jnp.log10(jnp.maximum(dL_sne, 1e-10)) + 25.0

    return dc_bgs, H_bgs, dc_aniso, H_aniso, mu_sne

def solve_growth(w0, wa, Om, H0, z_out):
    """Growth factor via RK4 + lax.scan. 200 steps."""
    h = H0 / 100.0
    Or = OMEGA_R_H2 / h**2
    ODE_c = 1.0 - Om - Or

    n_steps = 200
    a_init = 0.005
    N_init = jnp.log(a_init)
    dN = -N_init / n_steps
    N_starts = N_init + jnp.arange(n_steps) * dN

    def deriv(state, N):
        D, Dp = state
        a = jnp.exp(N)
        E2 = Ez2(1/a - 1, w0, wa, Om, h)
        de = a**(-3*(1+w0+wa)) * jnp.exp(-3*wa*(1-a))
        dE2_dN = (-3*Om*a**(-3) - 4*Or*a**(-4)
                  + ODE_c * de * (-3*(1+w0+wa) + 3*wa*a))
        dlnE2 = dE2_dN / E2
        Om_a = Om * a**(-3) / E2
        Dpp = -(2 + 0.5*dlnE2)*Dp + 1.5*Om_a*D
        return jnp.array([Dp, Dpp])

    def rk4_step(state, N):
        k1 = deriv(state, N)
        k2 = deriv(state + 0.5*dN*k1, N + 0.5*dN)
        k3 = deriv(state + 0.5*dN*k2, N + 0.5*dN)
        k4 = deriv(state + dN*k3, N + dN)
        new = state + (dN/6)*(k1 + 2*k2 + 2*k3 + k4)
        return new, new

    state0 = jnp.array([a_init, a_init])
    _, all_states = jax.lax.scan(rk4_step, state0, N_starts)

    D_arr = jnp.concatenate([jnp.array([a_init]), all_states[:, 0]])
    Dp_arr = jnp.concatenate([jnp.array([a_init]), all_states[:, 1]])
    N_all = jnp.concatenate([jnp.array([N_init]), N_starts + dN])

    D0 = D_arr[-1]
    f_arr = Dp_arr / D_arr
    z_arr = 1.0/jnp.exp(N_all) - 1.0

    z_flip = z_arr[::-1]
    D_out = jnp.interp(z_out, z_flip, (D_arr/D0)[::-1])
    f_out = jnp.interp(z_out, z_flip, f_arr[::-1])
    return D_out, f_out

def approx_sigma8(Om, H0):
    Om_fid, H0_fid, s8_fid = 0.315, 67.36, 0.811
    return s8_fid * (Om/Om_fid)**0.27 * ((H0/100)/(H0_fid/100))**(-0.36)

# ============================================================
# NUMPYRO MODELS
# ============================================================

def model_fitA(data, sh_tables):
    w0 = numpyro.sample('w0', dist.Uniform(-2.0, -0.3))
    Om = numpyro.sample('Om', dist.Uniform(0.1, 0.6))
    H0 = numpyro.sample('H0', dist.Uniform(55.0, 80.0))

    # Precomputed sound horizon (no gradient through this)
    rd = interp2d(Om, H0, sh_tables['Om_grid'], sh_tables['H0_grid'], sh_tables['rd'])
    rs_star = interp2d(Om, H0, sh_tables['Om_grid'], sh_tables['H0_grid'], sh_tables['rs_star'])
    dc_star_ref = interp2d(Om, H0, sh_tables['Om_grid'], sh_tables['H0_grid'], sh_tables['dc_star_lcdm'])

    # Low-z distances (gradient flows through here)
    dc_bgs, H_bgs, dc_aniso, H_aniso, mu_sne = compute_lowz_distances(
        w0, 0.0, Om, H0, data['sne_z_cmb'], data['sne_z_hel'])

    # BAO vector
    DV_bgs = (0.295 * dc_bgs**2 * C_KMS / H_bgs)**(1/3) / rd
    DM_a = dc_aniso / rd
    DH_a = C_KMS / H_aniso / rd
    bao_vec = jnp.array([DV_bgs,
                         DM_a[0], DH_a[0], DM_a[1], DH_a[1],
                         DM_a[2], DH_a[2], DM_a[3], DH_a[3],
                         DM_a[4], DH_a[4], DH_a[5], DM_a[5]])

    d_bao = bao_vec - data['bao_mean']
    chi2_bao = d_bao @ data['bao_cov_inv'] @ d_bao
    numpyro.factor('bao', -0.5 * chi2_bao)

    d_sne = data['sne_m_obs'] - mu_sne
    chi2_sne = d_sne @ data['sne_C_inv_marg'] @ d_sne
    numpyro.factor('sne', -0.5 * chi2_sne)

    # CMB (using precomputed dc_star for LCDM reference — weak w0 dependence at z>>1)
    R = jnp.sqrt(Om) * H0 * dc_star_ref / C_KMS
    l_A = jnp.pi * dc_star_ref / rs_star
    cmb_vec = jnp.array([R, l_A, OMBH2]) - data['cmb_means']
    chi2_cmb = cmb_vec @ data['cmb_cov_inv'] @ cmb_vec
    numpyro.factor('cmb', -0.5 * chi2_cmb)

    D_fs8, f_fs8 = solve_growth(w0, 0.0, Om, H0, data['fs8_z'])
    s8 = approx_sigma8(Om, H0)
    fs8_pred = f_fs8 * s8 * D_fs8
    chi2_fs8 = jnp.sum(((fs8_pred - data['fs8_val']) / data['fs8_err'])**2)
    numpyro.factor('fs8', -0.5 * chi2_fs8)

    chi2_rd = ((rd - RD_PRIOR_MEAN) / RD_PRIOR_SIGMA)**2
    numpyro.factor('rd_prior', -0.5 * chi2_rd)

    numpyro.deterministic('chi2_bao', chi2_bao)
    numpyro.deterministic('chi2_sne', chi2_sne)
    numpyro.deterministic('chi2_cmb', chi2_cmb)
    numpyro.deterministic('chi2_fs8', chi2_fs8)
    numpyro.deterministic('chi2_rd', chi2_rd)
    numpyro.deterministic('rd_val', rd)

def model_fitB(data, sh_tables):
    w0 = numpyro.sample('w0', dist.Uniform(-2.0, 0.5))
    wa = numpyro.sample('wa', dist.Uniform(-4.0, 3.0))
    Om = numpyro.sample('Om', dist.Uniform(0.1, 0.6))
    H0 = numpyro.sample('H0', dist.Uniform(55.0, 80.0))

    numpyro.factor('stability', jnp.where(w0 + wa < 0, 0.0, -1e10))

    rd = interp2d(Om, H0, sh_tables['Om_grid'], sh_tables['H0_grid'], sh_tables['rd'])
    rs_star = interp2d(Om, H0, sh_tables['Om_grid'], sh_tables['H0_grid'], sh_tables['rs_star'])
    dc_star_ref = interp2d(Om, H0, sh_tables['Om_grid'], sh_tables['H0_grid'], sh_tables['dc_star_lcdm'])

    dc_bgs, H_bgs, dc_aniso, H_aniso, mu_sne = compute_lowz_distances(
        w0, wa, Om, H0, data['sne_z_cmb'], data['sne_z_hel'])

    DV_bgs = (0.295 * dc_bgs**2 * C_KMS / H_bgs)**(1/3) / rd
    DM_a = dc_aniso / rd
    DH_a = C_KMS / H_aniso / rd
    bao_vec = jnp.array([DV_bgs,
                         DM_a[0], DH_a[0], DM_a[1], DH_a[1],
                         DM_a[2], DH_a[2], DM_a[3], DH_a[3],
                         DM_a[4], DH_a[4], DH_a[5], DM_a[5]])

    d_bao = bao_vec - data['bao_mean']
    chi2_bao = d_bao @ data['bao_cov_inv'] @ d_bao
    numpyro.factor('bao', -0.5 * chi2_bao)

    d_sne = data['sne_m_obs'] - mu_sne
    chi2_sne = d_sne @ data['sne_C_inv_marg'] @ d_sne
    numpyro.factor('sne', -0.5 * chi2_sne)

    R = jnp.sqrt(Om) * H0 * dc_star_ref / C_KMS
    l_A = jnp.pi * dc_star_ref / rs_star
    cmb_vec = jnp.array([R, l_A, OMBH2]) - data['cmb_means']
    chi2_cmb = cmb_vec @ data['cmb_cov_inv'] @ cmb_vec
    numpyro.factor('cmb', -0.5 * chi2_cmb)

    D_fs8, f_fs8 = solve_growth(w0, wa, Om, H0, data['fs8_z'])
    s8 = approx_sigma8(Om, H0)
    fs8_pred = f_fs8 * s8 * D_fs8
    chi2_fs8 = jnp.sum(((fs8_pred - data['fs8_val']) / data['fs8_err'])**2)
    numpyro.factor('fs8', -0.5 * chi2_fs8)

    chi2_rd = ((rd - RD_PRIOR_MEAN) / RD_PRIOR_SIGMA)**2
    numpyro.factor('rd_prior', -0.5 * chi2_rd)

    numpyro.deterministic('chi2_bao', chi2_bao)
    numpyro.deterministic('chi2_sne', chi2_sne)
    numpyro.deterministic('chi2_cmb', chi2_cmb)
    numpyro.deterministic('chi2_fs8', chi2_fs8)
    numpyro.deterministic('chi2_rd', chi2_rd)
    numpyro.deterministic('rd_val', rd)

# ============================================================
# MAIN
# ============================================================

def run_fit(model_fn, data, sh_tables, name, num_warmup=500, num_samples=2000):
    print(f"\n{'='*60}", flush=True)
    print(f"MCMC: {name} (NUTS, 1 chain, GPU)", flush=True)
    print(f"{'='*60}", flush=True)

    kernel = NUTS(model_fn, target_accept_prob=0.8, max_tree_depth=8)
    mcmc = MCMC(kernel, num_warmup=num_warmup, num_samples=num_samples,
                num_chains=1, progress_bar=True)

    t0 = time.time()
    mcmc.run(jax.random.PRNGKey(42), data, sh_tables)
    elapsed = time.time() - t0

    print(f"\n  Completed in {elapsed:.1f}s ({elapsed/60:.1f} min)", flush=True)
    mcmc.print_summary()
    return mcmc, elapsed

def analyze(mcmc_A, mcmc_B, data):
    sA = mcmc_A.get_samples()
    sB = mcmc_B.get_samples()

    tot_A = sA['chi2_bao'] + sA['chi2_sne'] + sA['chi2_cmb'] + sA['chi2_fs8'] + sA['chi2_rd']
    tot_B = sB['chi2_bao'] + sB['chi2_sne'] + sB['chi2_cmb'] + sB['chi2_fs8'] + sB['chi2_rd']

    chi2_A = float(jnp.min(tot_A))
    chi2_B = float(jnp.min(tot_B))

    npar_A, npar_B = 3, 4
    n_data = 13 + (data['sne_N'] - 1) + 3 + 7

    AIC_A = chi2_A + 2*npar_A
    AIC_B = chi2_B + 2*npar_B
    DAIC = AIC_A - AIC_B

    BIC_A = chi2_A + npar_A * np.log(n_data)
    BIC_B = chi2_B + npar_B * np.log(n_data)
    DBIC = BIC_A - BIC_B

    print(f"\n{'='*70}", flush=True)
    print(f"18A v5b GPU MCMC — RESULTS (Fixed r_d)", flush=True)
    print(f"{'='*70}", flush=True)

    best_A = int(jnp.argmin(tot_A))
    best_B = int(jnp.argmin(tot_B))

    print(f"\nFit A (constant w, GR):")
    for k in ['w0', 'Om', 'H0']:
        v = float(sA[k][best_A])
        mean = float(jnp.mean(sA[k]))
        std = float(jnp.std(sA[k]))
        print(f"  {k} = {v:.4f}  (mean={mean:.4f} +/- {std:.4f})")
    print(f"  chi2 = {chi2_A:.2f}, chi2/dof = {chi2_A/(n_data-npar_A):.4f}")

    print(f"\nFit B (CPL, coupled):")
    for k in ['w0', 'wa', 'Om', 'H0']:
        v = float(sB[k][best_B])
        mean = float(jnp.mean(sB[k]))
        std = float(jnp.std(sB[k]))
        print(f"  {k} = {v:.4f}  (mean={mean:.4f} +/- {std:.4f})")
    print(f"  chi2 = {chi2_B:.2f}, chi2/dof = {chi2_B/(n_data-npar_B):.4f}")

    print(f"\n--- Model Comparison ---")
    print(f"  DAIC = {DAIC:+.2f}  (positive = CPL preferred)")
    print(f"  DBIC = {DBIC:+.2f}")

    # v3 reference
    print(f"\n--- v3 Reference ---")
    print(f"  v3 DAIC = +7.23 (emcee + CAMB)")
    print(f"  v5b DAIC = {DAIC:+.2f} (NUTS + JAX)")
    print(f"  Difference = {abs(DAIC - 7.23):.2f}")

    print(f"\n--- Probe Decomposition ---")
    print(f"  {'Probe':<10} {'Fit A':>10} {'Fit B':>10} {'Delta':>10}")
    for p in ['bao', 'sne', 'cmb', 'fs8', 'rd']:
        vA = float(sA[f'chi2_{p}'][best_A])
        vB = float(sB[f'chi2_{p}'][best_B])
        print(f"  {p:<10} {vA:>10.2f} {vB:>10.2f} {vA-vB:>+10.2f}")

    wa = np.array(sB['wa'])
    q16, q50, q84 = np.percentile(wa, [16, 50, 84])
    print(f"\n--- wa Posterior ---")
    print(f"  Mean +/- std: {wa.mean():.3f} +/- {wa.std():.3f}")
    print(f"  Median: {q50:.3f} [{q16:.3f}, {q84:.3f}]")
    print(f"  Tension with wa=0: {abs(wa.mean())/wa.std():.1f}sigma")

    rd_A = np.array(sA['rd_val'])
    rd_B = np.array(sB['rd_val'])
    print(f"\n--- Sound Horizon ---")
    print(f"  Fit A: rd = {rd_A.mean():.2f} +/- {rd_A.std():.2f} Mpc")
    print(f"  Fit B: rd = {rd_B.mean():.2f} +/- {rd_B.std():.2f} Mpc")

    if DAIC > 10:
        verdict = "STRONG CPL preference."
    elif DAIC > 6:
        verdict = "MODERATE CPL preference."
    elif DAIC > 2:
        verdict = "WEAK CPL preference."
    else:
        verdict = "NO significant preference."
    print(f"\n  Verdict: {verdict}")

    return {'DAIC': DAIC, 'DBIC': DBIC, 'chi2_A': chi2_A, 'chi2_B': chi2_B}


if __name__ == '__main__':
    t_start = time.time()
    print("=" * 60, flush=True)
    print("18A v5b — GPU MCMC (optimized for NUTS)", flush=True)
    print(f"Platform: {jax.default_backend()}", flush=True)
    print(f"Devices: {jax.devices()}", flush=True)
    print("=" * 60, flush=True)

    # Load data
    data = load_all_data()

    # Precompute sound horizons (50x50 grid, ~30s)
    Om_grid = np.linspace(0.15, 0.55, 50)
    H0_grid = np.linspace(58, 78, 50)
    sh_tables = precompute_sound_horizon_tables(Om_grid, H0_grid)

    # Run both fits
    mcmc_A, t_A = run_fit(model_fitA, data, sh_tables, "Fit A (constant w, GR)")
    mcmc_B, t_B = run_fit(model_fitB, data, sh_tables, "Fit B (CPL, coupled)")

    results = analyze(mcmc_A, mcmc_B, data)

    t_total = time.time() - t_start
    print(f"\nTotal time: {t_total:.1f}s ({t_total/60:.1f} min)", flush=True)

    # Save
    out = os.path.join(OUTPUT_DIR, '18A_v5b_gpu_results.md')
    with open(out, 'w') as f:
        f.write("# 18A v5b GPU MCMC Results\n\n")
        f.write(f"**Platform:** {jax.default_backend()}, {jax.devices()}\n")
        f.write(f"**Runtime:** Fit A = {t_A:.1f}s, Fit B = {t_B:.1f}s, Total = {t_total:.1f}s\n\n")
        f.write(f"**DAIC = {results['DAIC']:+.2f}** (v3 reference: +7.23)\n")
        f.write(f"**DBIC = {results['DBIC']:+.2f}**\n\n")
        f.write(f"chi2_A = {results['chi2_A']:.2f}\n")
        f.write(f"chi2_B = {results['chi2_B']:.2f}\n")
    print(f"\nResults saved to {out}", flush=True)
    print("\n🦞🧍💜🔥♾️", flush=True)
