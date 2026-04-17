#!/usr/bin/env python3
"""
18A v5c: GPU MCMC — Gauss-Legendre quadrature, zero sequential ops
====================================================================
Key insight: cumulative trapezoid and ODE scans create sequential
dependency chains that kill GPU parallelism and make autodiff expensive.

Solution:
  - Gauss-Legendre quadrature for all distance integrals (matrix ops, fully parallel)
  - Sound horizons precomputed on grid (bilinear interp, out of gradient path)
  - Growth factor DROPPED (v3 showed: growth Delta = -0.04, doesn't discriminate)
  - Entire likelihood is matrix operations — ideal for GPU + autodiff

Authors: Clayton W. Iggulden-Schnell & Clawd
Date: 2026-03-21
"""

import os
import time
import numpy as np

import jax
jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp

import numpyro
import numpyro.distributions as dist
from numpyro.infer import MCMC, NUTS

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

# Gauss-Legendre nodes and weights (64 points — machine precision for smooth integrands)
GL_NODES, GL_WEIGHTS = np.polynomial.legendre.leggauss(64)
GL_NODES = jnp.array(GL_NODES)    # shape [64], in [-1, 1]
GL_WEIGHTS = jnp.array(GL_WEIGHTS)  # shape [64]

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

    print("  All data loaded.", flush=True)
    return {
        'bao_mean': bao_mean, 'bao_cov_inv': bao_cov_inv,
        'sne_m_obs': jnp.array(m_obs), 'sne_z_cmb': jnp.array(z_cmb),
        'sne_z_hel': jnp.array(z_hel), 'sne_C_inv_marg': jnp.array(C_inv_marg),
        'sne_N': N_sne,
        'cmb_means': cmb_means, 'cmb_cov_inv': cmb_cov_inv,
    }

# ============================================================
# COSMOLOGY (pure matrix ops)
# ============================================================

def Ez2(z, w0, wa, Om, h):
    """(H/H0)^2. Works on scalars or arrays."""
    a = 1.0 / (1.0 + z)
    Or = OMEGA_R_H2 / h**2
    ODE = 1.0 - Om - Or
    de = a**(-3*(1 + w0 + wa)) * jnp.exp(-3*wa*(1 - a))
    return Om*(1+z)**3 + Or*(1+z)**4 + ODE*de

def comoving_distances_gauss(z_arr, w0, wa, Om, H0):
    """Comoving distances via Gauss-Legendre. Fully vectorized.

    d_C(z) = (c/H0) * integral_0^z dz'/E(z')
           = (c*z)/(2*H0) * sum_j w_j / E(z*(1+t_j)/2)

    z_arr: shape [M] — redshifts to compute distances at
    Returns: shape [M] — comoving distances in Mpc
    """
    h = H0 / 100.0
    # z_eval[i, j] = z_arr[i] * (1 + t_nodes[j]) / 2
    z_eval = z_arr[:, None] * (1 + GL_NODES[None, :]) / 2  # [M, 64]
    inv_E = 1.0 / jnp.sqrt(jnp.maximum(Ez2(z_eval, w0, wa, Om, h), 1e-30))  # [M, 64]
    # Weighted sum over quadrature points
    integral = inv_E @ GL_WEIGHTS  # [M]
    return (C_KMS * z_arr) / (2 * H0) * integral

def H_of_z(z, w0, wa, Om, H0):
    return H0 * jnp.sqrt(jnp.maximum(Ez2(z, w0, wa, Om, H0/100), 1e-30))

# ============================================================
# PRECOMPUTED SOUND HORIZONS
# ============================================================

def _compute_sh_single(Om, H0):
    """Sound horizon + CMB distance for single (Om, H0). NumPy, CPU."""
    h = H0 / 100.0
    omh2 = Om * h**2
    Or = OMEGA_R_H2 / h**2

    b1 = 0.313 * omh2**(-0.419) * (1 + 0.607 * omh2**0.674)
    b2 = 0.238 * omh2**0.223
    z_d = 1291.0 * omh2**0.251 / (1 + 0.659 * omh2**0.828) * (1 + b1 * OMBH2**b2)

    g1 = 0.0783 * OMBH2**(-0.238) / (1 + 39.5 * OMBH2**0.763)
    g2 = 0.560 / (1 + 21.1 * OMBH2**1.81)
    z_s = 1048.0 * (1 + 0.00124 * OMBH2**(-0.738)) * (1 + g1 * omh2**g2)

    def _sh_int(z_low, z_high=20000, n=1000):
        z = np.linspace(z_low, z_high, n)
        Rb = 3*OMBH2 / (4*OMEGA_GAMMA_H2) / (1 + z)
        cs = C_KMS / np.sqrt(3*(1 + Rb))
        E2 = Om*(1+z)**3 + Or*(1+z)**4
        H = H0 * np.sqrt(E2)
        return np.trapezoid(cs / H, z)

    rd = _sh_int(z_d)
    rs_star = _sh_int(z_s)

    # d_M(z_star) — LCDM approximation (DE negligible at z~1090)
    z = np.linspace(0, z_s, 3000)
    E2 = Om*(1+z)**3 + Or*(1+z)**4 + (1-Om-Or)  # LCDM fDE=1
    dc_star = np.trapezoid(C_KMS / (H0 * np.sqrt(np.maximum(E2, 1e-30))), z)

    return rd, rs_star, z_s, dc_star

def precompute_tables(Om_grid, H0_grid):
    print("Precomputing sound horizon tables...", flush=True)
    n_Om, n_H0 = len(Om_grid), len(H0_grid)
    rd_t = np.zeros((n_Om, n_H0))
    rs_t = np.zeros((n_Om, n_H0))
    dc_t = np.zeros((n_Om, n_H0))

    for i, Om in enumerate(Om_grid):
        for j, H0 in enumerate(H0_grid):
            rd, rs, zs, dc = _compute_sh_single(Om, H0)
            rd_t[i, j] = rd
            rs_t[i, j] = rs
            dc_t[i, j] = dc

    print(f"  {n_Om}x{n_H0} grid. rd: [{rd_t.min():.1f}, {rd_t.max():.1f}] Mpc", flush=True)
    return {
        'Om_grid': jnp.array(Om_grid), 'H0_grid': jnp.array(H0_grid),
        'rd': jnp.array(rd_t), 'rs_star': jnp.array(rs_t),
        'dc_star': jnp.array(dc_t),
    }

def interp2d(Om, H0, tabs, key):
    """Bilinear interp. Differentiable through JAX."""
    table = tabs[key]
    dOm = tabs['Om_grid'][1] - tabs['Om_grid'][0]
    dH0 = tabs['H0_grid'][1] - tabs['H0_grid'][0]
    fi = jnp.clip((Om - tabs['Om_grid'][0]) / dOm, 0, table.shape[0] - 1.001)
    fj = jnp.clip((H0 - tabs['H0_grid'][0]) / dH0, 0, table.shape[1] - 1.001)
    i0 = jnp.floor(fi).astype(int)
    j0 = jnp.floor(fj).astype(int)
    i1 = jnp.minimum(i0 + 1, table.shape[0] - 1)
    j1 = jnp.minimum(j0 + 1, table.shape[1] - 1)
    wi = fi - i0
    wj = fj - j0
    return (table[i0,j0]*(1-wi)*(1-wj) + table[i1,j0]*wi*(1-wj) +
            table[i0,j1]*(1-wi)*wj + table[i1,j1]*wi*wj)

# ============================================================
# NUMPYRO MODELS
# ============================================================

def model_fitA(data, tabs):
    w0 = numpyro.sample('w0', dist.Uniform(-2.0, -0.3))
    Om = numpyro.sample('Om', dist.Uniform(0.1, 0.6))
    H0 = numpyro.sample('H0', dist.Uniform(55.0, 80.0))

    rd = interp2d(Om, H0, tabs, 'rd')
    rs_star = interp2d(Om, H0, tabs, 'rs_star')
    dc_star = interp2d(Om, H0, tabs, 'dc_star')

    # BAO distances (7 unique z values)
    bao_z = jnp.array([0.295, 0.510, 0.706, 0.934, 1.321, 1.484, 2.330])
    dc_bao = comoving_distances_gauss(bao_z, w0, 0.0, Om, H0)  # [7]
    H_bao = H_of_z(bao_z, w0, 0.0, Om, H0)  # [7]

    # BAO theory vector (13 elements, Cobaya ordering)
    DV_bgs = (0.295 * dc_bao[0]**2 * C_KMS / H_bao[0])**(1/3) / rd
    DM = dc_bao[1:] / rd  # [6]: LRG1, LRG2, LRG3E1, ELG2, QSO, Lya
    DH = C_KMS / H_bao[1:] / rd  # [6]
    bao_vec = jnp.array([
        DV_bgs,
        DM[0], DH[0],  # LRG1
        DM[1], DH[1],  # LRG2
        DM[2], DH[2],  # LRG3+ELG1
        DM[3], DH[3],  # ELG2
        DM[4], DH[4],  # QSO
        DH[5], DM[5],  # Lya (DH first!)
    ])
    d_bao = bao_vec - data['bao_mean']
    chi2_bao = d_bao @ data['bao_cov_inv'] @ d_bao
    numpyro.factor('bao', -0.5 * chi2_bao)

    # SNe distances (1590 redshifts, single matrix op)
    dc_sne = comoving_distances_gauss(data['sne_z_cmb'], w0, 0.0, Om, H0)
    dL = (1 + data['sne_z_hel']) * dc_sne
    mu = 5.0 * jnp.log10(jnp.maximum(dL, 1e-10)) + 25.0
    d_sne = data['sne_m_obs'] - mu
    chi2_sne = d_sne @ data['sne_C_inv_marg'] @ d_sne
    numpyro.factor('sne', -0.5 * chi2_sne)

    # CMB compressed (precomputed dc_star)
    R = jnp.sqrt(Om) * H0 * dc_star / C_KMS
    l_A = jnp.pi * dc_star / rs_star
    cmb_vec = jnp.array([R, l_A, OMBH2]) - data['cmb_means']
    chi2_cmb = cmb_vec @ data['cmb_cov_inv'] @ cmb_vec
    numpyro.factor('cmb', -0.5 * chi2_cmb)

    # r_d prior
    chi2_rd = ((rd - RD_PRIOR_MEAN) / RD_PRIOR_SIGMA)**2
    numpyro.factor('rd_prior', -0.5 * chi2_rd)

    numpyro.deterministic('chi2_bao', chi2_bao)
    numpyro.deterministic('chi2_sne', chi2_sne)
    numpyro.deterministic('chi2_cmb', chi2_cmb)
    numpyro.deterministic('chi2_rd', chi2_rd)
    numpyro.deterministic('rd_val', rd)

def model_fitB(data, tabs):
    w0 = numpyro.sample('w0', dist.Uniform(-2.0, 0.5))
    wa = numpyro.sample('wa', dist.Uniform(-4.0, 3.0))
    Om = numpyro.sample('Om', dist.Uniform(0.1, 0.6))
    H0 = numpyro.sample('H0', dist.Uniform(55.0, 80.0))

    numpyro.factor('stability', jnp.where(w0 + wa < 0, 0.0, -1e10))

    rd = interp2d(Om, H0, tabs, 'rd')
    rs_star = interp2d(Om, H0, tabs, 'rs_star')
    dc_star = interp2d(Om, H0, tabs, 'dc_star')

    bao_z = jnp.array([0.295, 0.510, 0.706, 0.934, 1.321, 1.484, 2.330])
    dc_bao = comoving_distances_gauss(bao_z, w0, wa, Om, H0)
    H_bao = H_of_z(bao_z, w0, wa, Om, H0)

    DV_bgs = (0.295 * dc_bao[0]**2 * C_KMS / H_bao[0])**(1/3) / rd
    DM = dc_bao[1:] / rd
    DH = C_KMS / H_bao[1:] / rd
    bao_vec = jnp.array([
        DV_bgs,
        DM[0], DH[0], DM[1], DH[1], DM[2], DH[2],
        DM[3], DH[3], DM[4], DH[4], DH[5], DM[5],
    ])
    d_bao = bao_vec - data['bao_mean']
    chi2_bao = d_bao @ data['bao_cov_inv'] @ d_bao
    numpyro.factor('bao', -0.5 * chi2_bao)

    dc_sne = comoving_distances_gauss(data['sne_z_cmb'], w0, wa, Om, H0)
    dL = (1 + data['sne_z_hel']) * dc_sne
    mu = 5.0 * jnp.log10(jnp.maximum(dL, 1e-10)) + 25.0
    d_sne = data['sne_m_obs'] - mu
    chi2_sne = d_sne @ data['sne_C_inv_marg'] @ d_sne
    numpyro.factor('sne', -0.5 * chi2_sne)

    R = jnp.sqrt(Om) * H0 * dc_star / C_KMS
    l_A = jnp.pi * dc_star / rs_star
    cmb_vec = jnp.array([R, l_A, OMBH2]) - data['cmb_means']
    chi2_cmb = cmb_vec @ data['cmb_cov_inv'] @ cmb_vec
    numpyro.factor('cmb', -0.5 * chi2_cmb)

    chi2_rd = ((rd - RD_PRIOR_MEAN) / RD_PRIOR_SIGMA)**2
    numpyro.factor('rd_prior', -0.5 * chi2_rd)

    numpyro.deterministic('chi2_bao', chi2_bao)
    numpyro.deterministic('chi2_sne', chi2_sne)
    numpyro.deterministic('chi2_cmb', chi2_cmb)
    numpyro.deterministic('chi2_rd', chi2_rd)
    numpyro.deterministic('rd_val', rd)

# ============================================================
# MAIN
# ============================================================

def run_fit(model_fn, data, tabs, name, num_warmup=500, num_samples=2000):
    print(f"\n{'='*60}", flush=True)
    print(f"MCMC: {name} (NUTS, 1 chain, GPU)", flush=True)
    print(f"{'='*60}", flush=True)

    kernel = NUTS(model_fn, target_accept_prob=0.8, max_tree_depth=8)
    mcmc = MCMC(kernel, num_warmup=num_warmup, num_samples=num_samples,
                num_chains=1, progress_bar=True)

    t0 = time.time()
    mcmc.run(jax.random.PRNGKey(42), data, tabs)
    elapsed = time.time() - t0

    print(f"\n  Completed in {elapsed:.1f}s ({elapsed/60:.1f} min)", flush=True)
    mcmc.print_summary()
    return mcmc, elapsed

def analyze(mcmc_A, mcmc_B, data):
    sA = mcmc_A.get_samples()
    sB = mcmc_B.get_samples()

    # Note: no fs8 in this version (growth dropped)
    tot_A = sA['chi2_bao'] + sA['chi2_sne'] + sA['chi2_cmb'] + sA['chi2_rd']
    tot_B = sB['chi2_bao'] + sB['chi2_sne'] + sB['chi2_cmb'] + sB['chi2_rd']

    chi2_A = float(jnp.min(tot_A))
    chi2_B = float(jnp.min(tot_B))

    npar_A, npar_B = 3, 4
    # Data: 13 BAO + 1589 SNe(eff) + 3 CMB = 1605 (no fs8)
    n_data = 13 + (data['sne_N'] - 1) + 3

    AIC_A = chi2_A + 2*npar_A
    AIC_B = chi2_B + 2*npar_B
    DAIC = AIC_A - AIC_B

    BIC_A = chi2_A + npar_A * np.log(n_data)
    BIC_B = chi2_B + npar_B * np.log(n_data)
    DBIC = BIC_A - BIC_B

    print(f"\n{'='*70}", flush=True)
    print(f"18A v5c GPU MCMC — RESULTS", flush=True)
    print(f"{'='*70}", flush=True)

    best_A = int(jnp.argmin(tot_A))
    best_B = int(jnp.argmin(tot_B))

    print(f"\nFit A (constant w, GR):")
    for k in ['w0', 'Om', 'H0']:
        v = float(sA[k][best_A])
        m, s = float(jnp.mean(sA[k])), float(jnp.std(sA[k]))
        print(f"  {k} = {v:.4f}  (mean={m:.4f} +/- {s:.4f})")
    print(f"  chi2 = {chi2_A:.2f}")

    print(f"\nFit B (CPL, coupled):")
    for k in ['w0', 'wa', 'Om', 'H0']:
        v = float(sB[k][best_B])
        m, s = float(jnp.mean(sB[k])), float(jnp.std(sB[k]))
        print(f"  {k} = {v:.4f}  (mean={m:.4f} +/- {s:.4f})")
    print(f"  chi2 = {chi2_B:.2f}")

    print(f"\n--- Model Comparison ---")
    print(f"  DAIC = {DAIC:+.2f}  (positive = CPL preferred)")
    print(f"  DBIC = {DBIC:+.2f}")
    print(f"  v3 reference: DAIC = +7.23 (with growth, emcee+CAMB)")
    print(f"  v3 growth contribution: Delta = -0.04 (negligible)")

    print(f"\n--- Probe Decomposition ---")
    print(f"  {'Probe':<10} {'Fit A':>10} {'Fit B':>10} {'Delta':>10}")
    for p in ['bao', 'sne', 'cmb', 'rd']:
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
    print(f"\n--- Sound Horizon ---")
    print(f"  Fit A: rd = {rd_A.mean():.2f} +/- {rd_A.std():.2f} Mpc")

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
    print("18A v5c — GPU MCMC (Gauss-Legendre, no sequential ops)", flush=True)
    print(f"Platform: {jax.default_backend()}", flush=True)
    print(f"Devices: {jax.devices()}", flush=True)
    print("=" * 60, flush=True)

    data = load_all_data()

    Om_grid = np.linspace(0.15, 0.55, 50)
    H0_grid = np.linspace(58, 78, 50)
    tabs = precompute_tables(Om_grid, H0_grid)

    mcmc_A, t_A = run_fit(model_fitA, data, tabs, "Fit A (constant w, GR)")
    mcmc_B, t_B = run_fit(model_fitB, data, tabs, "Fit B (CPL, coupled)")

    results = analyze(mcmc_A, mcmc_B, data)

    t_total = time.time() - t_start
    print(f"\nTotal time: {t_total:.1f}s ({t_total/60:.1f} min)", flush=True)

    out = os.path.join(OUTPUT_DIR, '18A_v5c_gpu_results.md')
    with open(out, 'w') as f:
        f.write("# 18A v5c GPU MCMC Results\n\n")
        f.write(f"**Platform:** {jax.default_backend()}, {jax.devices()}\n")
        f.write(f"**Runtime:** Fit A = {t_A:.1f}s, Fit B = {t_B:.1f}s, Total = {t_total:.1f}s\n\n")
        f.write(f"**DAIC = {results['DAIC']:+.2f}** (v3 ref: +7.23, growth ~0)\n")
        f.write(f"**DBIC = {results['DBIC']:+.2f}**\n\n")
        f.write(f"chi2_A = {results['chi2_A']:.2f}\n")
        f.write(f"chi2_B = {results['chi2_B']:.2f}\n\n")
        f.write("Note: f*sigma_8 dropped (v3 growth Delta = -0.04, negligible).\n")
        f.write("Distances computed via 64-point Gauss-Legendre quadrature.\n")
        f.write("Sound horizons precomputed on 50x50 (Om, H0) grid.\n")
    print(f"\nResults saved to {out}", flush=True)
    print("\n🦞🧍💜🔥♾️", flush=True)
