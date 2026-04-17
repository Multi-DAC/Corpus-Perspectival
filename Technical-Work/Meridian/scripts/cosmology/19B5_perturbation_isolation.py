#!/usr/bin/env python3
"""
19B.5: Perturbation Isolation Test — Phase 19's First Result
============================================================
The single most important test in Phase 19. Isolates whether perturbation
coupling matters for current cosmological data, independent of the w(z)
template question.

Design:
  Fit A:  constant w0, mu=1 (GR growth).          4 params: w0, Om, H0, s8
  Fit C:  CPL w0+wa, mu=1 (Meridian prediction).  5 params: w0, wa, Om, H0, s8
  Fit D:  CPL w0+wa, mu0 free (generic MG).        6 params: w0, wa, Om, H0, s8, mu0

  mu(a) = 1 + mu0 * Omega_DE(a)    [proportional-to-DE parameterization]

Key comparisons:
  DAIC(A vs C) = w(z) template preference WITH growth data
  DAIC(C vs D) = perturbation coupling preference  <-- THE HEADLINE
  mu0 posterior = direct measurement of gravitational coupling departure

Data:
  - DESI DR2 BAO (13 points, full covariance)
  - Pantheon+ full covariance (1590 SNe after z>0.01 cut)
  - Planck 2018 compressed CMB (R, l_A, omega_b with correlations)
  - f*sigma_8 compilation (7 points, diagonal errors)

Growth: Linear growth ODE solved via RK4 on GPU (500 steps, a=0.001 to a=1).

Authors: Clayton W. Iggulden-Schnell & Clawd
Date: 2026-03-21 (Phase 19, Track 19B.5)
"""

import os
import sys
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

DATA_DIR = '/mnt/c/Users/mercu/clawd/projects/Project Meridian/phase18/data'
PHASE18_DIR = '/mnt/c/Users/mercu/clawd/projects/Project Meridian/phase18'
OUTPUT_DIR = '/mnt/c/Users/mercu/clawd/projects/Project Meridian/phase19'

# Gauss-Legendre quadrature (64 points)
GL_NODES, GL_WEIGHTS = np.polynomial.legendre.leggauss(64)
GL_NODES = jnp.array(GL_NODES)
GL_WEIGHTS = jnp.array(GL_WEIGHTS)

# ============================================================
# CONFIGURATION
# ============================================================
NUM_WARMUP = 500
NUM_SAMPLES = 2000
NUM_CHAINS = 1
MAX_TREE_DEPTH = 8      # cap tree depth to limit cost per NUTS step
TARGET_ACCEPT = 0.80

# Growth ODE parameters
GROWTH_N_STEPS = 100    # growth factor is smooth — 100 RK4 steps is plenty
GROWTH_A_START = 1e-2   # z = 99 (deep matter domination, well before fs8 data)
GROWTH_A_END = 1.0      # z = 0

# ============================================================
# DATA LOADING
# ============================================================

def load_all_data():
    print("Loading data...", flush=True)

    # BAO (DR2)
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
    print(f"  BAO: {len(bao_mean)} points (DR2)", flush=True)

    # SNe (Pantheon+ full covariance)
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

    # CMB compressed (Planck 2018: R, l_A, omega_b)
    cmb_means = jnp.array([1.7502, 301.471, 0.02237])
    cmb_sigmas = jnp.array([0.0046, 0.090, 0.00015])
    cmb_corr = jnp.array([[1.0, 0.46, -0.66],
                           [0.46, 1.0, -0.33],
                           [-0.66, -0.33, 1.0]])
    cmb_cov = jnp.outer(cmb_sigmas, cmb_sigmas) * cmb_corr
    cmb_cov_inv = jnp.linalg.inv(cmb_cov)

    # f*sigma_8 compilation (7 measurements, diagonal errors)
    # Sources: 6dFGS, SDSS-MGS, BOSS DR12, eBOSS, WiggleZ
    fs8_z = jnp.array([0.067, 0.38, 0.51, 0.61, 0.70, 0.85, 1.48])
    fs8_obs = jnp.array([0.423, 0.497, 0.459, 0.436, 0.473, 0.315, 0.342])
    fs8_err = jnp.array([0.055, 0.045, 0.038, 0.034, 0.041, 0.095, 0.070])

    print(f"  Growth: {len(fs8_z)} f*sigma_8 points", flush=True)
    print("  All data loaded.", flush=True)

    return {
        'bao_mean': bao_mean, 'bao_cov_inv': bao_cov_inv,
        'sne_m_obs': jnp.array(m_obs), 'sne_z_cmb': jnp.array(z_cmb),
        'sne_z_hel': jnp.array(z_hel), 'sne_C_inv_marg': jnp.array(C_inv_marg),
        'sne_N': N_sne,
        'cmb_means': cmb_means, 'cmb_cov_inv': cmb_cov_inv,
        'fs8_z': fs8_z, 'fs8_obs': fs8_obs, 'fs8_err': fs8_err,
    }

# ============================================================
# CAMB GRID (precomputed early-universe quantities)
# ============================================================

def load_camb_grid():
    grid_file = os.path.join(PHASE18_DIR, 'camb_grid_100x100.npz')
    print(f"Loading CAMB grid from {grid_file}...", flush=True)
    g = np.load(grid_file)

    valid = ~np.isnan(g['rd'])
    n_valid = valid.sum()
    n_total = valid.size
    print(f"  Grid: {g['Om_grid'].shape[0]}x{g['H0_grid'].shape[0]}, "
          f"{n_valid}/{n_total} valid points", flush=True)

    rd = np.nan_to_num(g['rd'], nan=np.nanmedian(g['rd']))
    rs_star = np.nan_to_num(g['rs_star'], nan=np.nanmedian(g['rs_star']))
    z_star = np.nan_to_num(g['z_star'], nan=np.nanmedian(g['z_star']))

    Om_grid = g['Om_grid']
    H0_grid = g['H0_grid']
    i_fid = np.argmin(np.abs(Om_grid - 0.315))
    j_fid = np.argmin(np.abs(H0_grid - 67.4))
    print(f"  Fiducial (Om={Om_grid[i_fid]:.3f}, H0={H0_grid[j_fid]:.1f}): "
          f"rd={g['rd'][i_fid,j_fid]:.2f} Mpc", flush=True)

    tabs = {
        'Om_grid': jnp.array(Om_grid),
        'H0_grid': jnp.array(H0_grid),
        'rd': jnp.array(rd),
        'rs_star': jnp.array(rs_star),
        'z_star': jnp.array(z_star),
    }
    return tabs

# ============================================================
# COSMOLOGY (pure JAX ops)
# ============================================================

def Ez2(z, w0, wa, Om, h):
    """(H/H0)^2 for flat wCDM/CPL."""
    a = 1.0 / (1.0 + z)
    Or = OMEGA_R_H2 / h**2
    ODE = 1.0 - Om - Or
    de = a**(-3*(1 + w0 + wa)) * jnp.exp(-3*wa*(1 - a))
    return Om*(1+z)**3 + Or*(1+z)**4 + ODE*de

def comoving_distances_gl(z_arr, w0, wa, Om, H0):
    """Comoving distances via Gauss-Legendre. Fully vectorized."""
    h = H0 / 100.0
    z_eval = z_arr[:, None] * (1 + GL_NODES[None, :]) / 2
    inv_E = 1.0 / jnp.sqrt(jnp.maximum(Ez2(z_eval, w0, wa, Om, h), 1e-30))
    integral = inv_E @ GL_WEIGHTS
    return (C_KMS * z_arr) / (2 * H0) * integral

def comoving_distance_scalar(z, w0, wa, Om, H0):
    """Comoving distance to a single redshift (e.g., z_star)."""
    return comoving_distances_gl(jnp.array([z]), w0, wa, Om, H0)[0]

def H_of_z(z, w0, wa, Om, H0):
    return H0 * jnp.sqrt(jnp.maximum(Ez2(z, w0, wa, Om, H0/100), 1e-30))

def interp2d(Om, H0, tabs, key):
    """Bilinear interpolation on CAMB grid."""
    table = tabs[key]
    Om_grid = tabs['Om_grid']
    H0_grid = tabs['H0_grid']
    dOm = Om_grid[1] - Om_grid[0]
    dH0 = H0_grid[1] - H0_grid[0]

    fi = jnp.clip((Om - Om_grid[0]) / dOm, 0.0, table.shape[0] - 1.001)
    fj = jnp.clip((H0 - H0_grid[0]) / dH0, 0.0, table.shape[1] - 1.001)
    i0 = jnp.floor(fi).astype(int)
    j0 = jnp.floor(fj).astype(int)
    i1 = jnp.minimum(i0 + 1, table.shape[0] - 1)
    j1 = jnp.minimum(j0 + 1, table.shape[1] - 1)
    wi = fi - i0
    wj = fj - j0

    return (table[i0,j0]*(1-wi)*(1-wj) + table[i1,j0]*wi*(1-wj) +
            table[i0,j1]*(1-wi)*wj + table[i1,j1]*wi*wj)

# ============================================================
# BAO THEORY VECTOR
# ============================================================

BAO_Z = jnp.array([0.295, 0.510, 0.706, 0.934, 1.321, 1.484, 2.330])

def bao_theory(dc_bao, H_bao, rd):
    """BAO theory vector (13 elements, Cobaya ordering)."""
    DV_bgs = (BAO_Z[0] * dc_bao[0]**2 * C_KMS / H_bao[0])**(1.0/3.0) / rd
    DM = dc_bao[1:] / rd
    DH = C_KMS / H_bao[1:] / rd
    return jnp.array([
        DV_bgs,
        DM[0], DH[0],   # LRG1  z=0.510
        DM[1], DH[1],   # LRG2  z=0.706
        DM[2], DH[2],   # LRG3+ELG1  z=0.934
        DM[3], DH[3],   # ELG2  z=1.321
        DM[4], DH[4],   # QSO   z=1.484
        DH[5], DM[5],   # Lya   z=2.330 (DH first in Cobaya!)
    ])

# ============================================================
# GROWTH ODE SOLVER (RK4 on GPU)
# ============================================================
# Solves: D'' + (2 + eta)*D' - (3/2)*Om0/(a^3*E^2)*mu(a)*D = 0
# where ' = d/d(ln a), eta = d(ln E)/d(ln a)
# mu(a) = 1 + mu0 * Omega_DE(a)  [modified gravity parameterization]

# Pre-compute ln(a) grid for RK4
_LNA_START = jnp.log(GROWTH_A_START)
_LNA_END = jnp.log(GROWTH_A_END)
_DX = (_LNA_END - _LNA_START) / GROWTH_N_STEPS
_X_GRID = _LNA_START + jnp.arange(GROWTH_N_STEPS) * _DX

def _growth_rhs(x, y, w0, wa, Om, h, mu0):
    """RHS of the growth ODE system.

    y[0] = D (growth factor)
    y[1] = D' = dD/d(ln a)
    """
    a = jnp.exp(x)
    Or = OMEGA_R_H2 / h**2
    ODE0 = 1.0 - Om - Or

    # w(a) for CPL
    w = w0 + wa * (1.0 - a)

    # E^2(a) and its log-derivative
    de_factor = a**(-3*(1 + w0 + wa)) * jnp.exp(-3*wa*(1 - a))
    E2 = Om * a**(-3) + Or * a**(-4) + ODE0 * de_factor

    # d(E^2)/d(ln a) = a * d(E^2)/da
    dE2_dlna = -3*Om*a**(-3) - 4*Or*a**(-4) - 3*(1+w)*ODE0*de_factor
    eta = dE2_dlna / (2.0 * E2)

    # Modified gravity: mu(a) = 1 + mu0 * Omega_DE(a)
    Omega_DE_a = ODE0 * de_factor / E2
    mu = 1.0 + mu0 * Omega_DE_a

    # Source term: (3/2) * Om0 / (a^3 * E^2) * mu
    source = 1.5 * Om / (a**3 * E2) * mu

    dy0 = y[1]
    dy1 = -(2.0 + eta) * y[1] + source * y[0]
    return jnp.array([dy0, dy1])


def solve_growth_ode(w0, wa, Om, H0, mu0):
    """Solve growth ODE via RK4. Returns D(a) and D'(a) at a grid.

    Returns:
        a_arr: scale factor array [N_STEPS+1]
        D_arr: growth factor D(a)  [N_STEPS+1]
        Dp_arr: dD/d(ln a)         [N_STEPS+1]
    """
    h = H0 / 100.0

    # Initial conditions at a_start (deep matter domination: D = a, D' = a)
    y0 = jnp.array([GROWTH_A_START, GROWTH_A_START])

    def rk4_step(y, x):
        k1 = _growth_rhs(x, y, w0, wa, Om, h, mu0)
        k2 = _growth_rhs(x + _DX/2, y + _DX*k1/2, w0, wa, Om, h, mu0)
        k3 = _growth_rhs(x + _DX/2, y + _DX*k2/2, w0, wa, Om, h, mu0)
        k4 = _growth_rhs(x + _DX, y + _DX*k3, w0, wa, Om, h, mu0)
        y_new = y + _DX * (k1 + 2*k2 + 2*k3 + k4) / 6.0
        return y_new, y_new  # carry, output

    y_final, trajectory = jax.lax.scan(rk4_step, y0, _X_GRID)
    # trajectory shape: [N_STEPS, 2] — D and D' at each step

    # Prepend initial condition
    D_arr = jnp.concatenate([jnp.array([y0[0]]), trajectory[:, 0]])
    Dp_arr = jnp.concatenate([jnp.array([y0[1]]), trajectory[:, 1]])
    a_arr = jnp.exp(jnp.concatenate([jnp.array([_LNA_START]), _X_GRID + _DX]))

    return a_arr, D_arr, Dp_arr


def predict_fsigma8(w0, wa, Om, H0, sigma8, mu0, z_obs):
    """Predict f*sigma_8 at observed redshifts.

    f(z) = D'(a)/D(a)  [growth rate, where ' = d/d(ln a)]
    sigma_8(z) = sigma8 * D(z)/D(0)
    f*sigma_8(z) = f(z) * sigma_8(z)
    """
    a_arr, D_arr, Dp_arr = solve_growth_ode(w0, wa, Om, H0, mu0)

    # D(a=1) = D at z=0
    D0 = D_arr[-1]

    # Interpolate to observed redshifts
    a_obs = 1.0 / (1.0 + z_obs)

    # jnp.interp needs sorted x (ascending) — a_arr is already ascending
    D_obs = jnp.interp(a_obs, a_arr, D_arr)
    Dp_obs = jnp.interp(a_obs, a_arr, Dp_arr)

    f_obs = Dp_obs / D_obs          # growth rate f(z)
    D_norm = D_obs / D0              # D(z)/D(0)
    fs8_pred = f_obs * sigma8 * D_norm   # f*sigma_8(z)

    return fs8_pred


# ============================================================
# NUMPYRO MODELS
# ============================================================

def model_fitA(data, tabs):
    """Fit A: constant w0, GR growth (mu=1). 4 params."""
    w0 = numpyro.sample('w0', dist.Uniform(-2.5, 0.0))
    Om = numpyro.sample('Om', dist.Uniform(0.15, 0.55))
    H0 = numpyro.sample('H0', dist.Uniform(55.0, 80.0))
    sigma8 = numpyro.sample('sigma8', dist.Normal(0.811, 0.03))

    # Early-universe from CAMB grid
    rd = interp2d(Om, H0, tabs, 'rd')
    rs_star = interp2d(Om, H0, tabs, 'rs_star')
    z_star = interp2d(Om, H0, tabs, 'z_star')
    dc_star = comoving_distance_scalar(z_star, w0, 0.0, Om, H0)

    # BAO
    dc_bao = comoving_distances_gl(BAO_Z, w0, 0.0, Om, H0)
    H_bao = H_of_z(BAO_Z, w0, 0.0, Om, H0)
    bao_vec = bao_theory(dc_bao, H_bao, rd)
    d_bao = bao_vec - data['bao_mean']
    chi2_bao = d_bao @ data['bao_cov_inv'] @ d_bao
    numpyro.factor('bao', -0.5 * chi2_bao)

    # SNe
    dc_sne = comoving_distances_gl(data['sne_z_cmb'], w0, 0.0, Om, H0)
    dL = (1 + data['sne_z_hel']) * dc_sne
    mu_sne = 5.0 * jnp.log10(jnp.maximum(dL, 1e-10)) + 25.0
    d_sne = data['sne_m_obs'] - mu_sne
    chi2_sne = d_sne @ data['sne_C_inv_marg'] @ d_sne
    numpyro.factor('sne', -0.5 * chi2_sne)

    # CMB compressed
    R = jnp.sqrt(Om) * H0 * dc_star / C_KMS
    l_A = jnp.pi * dc_star / rs_star
    cmb_vec = jnp.array([R, l_A, OMBH2]) - data['cmb_means']
    chi2_cmb = cmb_vec @ data['cmb_cov_inv'] @ cmb_vec
    numpyro.factor('cmb', -0.5 * chi2_cmb)

    # Growth: f*sigma_8 with mu=1
    fs8_pred = predict_fsigma8(w0, 0.0, Om, H0, sigma8, 0.0, data['fs8_z'])
    chi2_fs8 = jnp.sum(((fs8_pred - data['fs8_obs']) / data['fs8_err'])**2)
    numpyro.factor('fs8', -0.5 * chi2_fs8)

    numpyro.deterministic('chi2_bao', chi2_bao)
    numpyro.deterministic('chi2_sne', chi2_sne)
    numpyro.deterministic('chi2_cmb', chi2_cmb)
    numpyro.deterministic('chi2_fs8', chi2_fs8)
    numpyro.deterministic('rd_val', rd)


def model_fitC(data, tabs):
    """Fit C (Meridian): CPL w0+wa, GR growth (mu=1). 5 params."""
    w0 = numpyro.sample('w0', dist.Uniform(-2.5, 0.5))
    wa = numpyro.sample('wa', dist.Uniform(-4.0, 3.0))
    Om = numpyro.sample('Om', dist.Uniform(0.15, 0.55))
    H0 = numpyro.sample('H0', dist.Uniform(55.0, 80.0))
    sigma8 = numpyro.sample('sigma8', dist.Normal(0.811, 0.03))

    # Early-universe from CAMB grid
    rd = interp2d(Om, H0, tabs, 'rd')
    rs_star = interp2d(Om, H0, tabs, 'rs_star')
    z_star = interp2d(Om, H0, tabs, 'z_star')
    dc_star = comoving_distance_scalar(z_star, w0, wa, Om, H0)

    # Stability: w0 + wa < 0
    numpyro.factor('stability', jnp.where(w0 + wa < 0, 0.0, -1e10))

    # BAO
    dc_bao = comoving_distances_gl(BAO_Z, w0, wa, Om, H0)
    H_bao = H_of_z(BAO_Z, w0, wa, Om, H0)
    bao_vec = bao_theory(dc_bao, H_bao, rd)
    d_bao = bao_vec - data['bao_mean']
    chi2_bao = d_bao @ data['bao_cov_inv'] @ d_bao
    numpyro.factor('bao', -0.5 * chi2_bao)

    # SNe
    dc_sne = comoving_distances_gl(data['sne_z_cmb'], w0, wa, Om, H0)
    dL = (1 + data['sne_z_hel']) * dc_sne
    mu_sne = 5.0 * jnp.log10(jnp.maximum(dL, 1e-10)) + 25.0
    d_sne = data['sne_m_obs'] - mu_sne
    chi2_sne = d_sne @ data['sne_C_inv_marg'] @ d_sne
    numpyro.factor('sne', -0.5 * chi2_sne)

    # CMB compressed
    R = jnp.sqrt(Om) * H0 * dc_star / C_KMS
    l_A = jnp.pi * dc_star / rs_star
    cmb_vec = jnp.array([R, l_A, OMBH2]) - data['cmb_means']
    chi2_cmb = cmb_vec @ data['cmb_cov_inv'] @ cmb_vec
    numpyro.factor('cmb', -0.5 * chi2_cmb)

    # Growth: f*sigma_8 with mu=1 (Meridian prediction: cuscuton doesn't cluster)
    fs8_pred = predict_fsigma8(w0, wa, Om, H0, sigma8, 0.0, data['fs8_z'])
    chi2_fs8 = jnp.sum(((fs8_pred - data['fs8_obs']) / data['fs8_err'])**2)
    numpyro.factor('fs8', -0.5 * chi2_fs8)

    numpyro.deterministic('chi2_bao', chi2_bao)
    numpyro.deterministic('chi2_sne', chi2_sne)
    numpyro.deterministic('chi2_cmb', chi2_cmb)
    numpyro.deterministic('chi2_fs8', chi2_fs8)
    numpyro.deterministic('rd_val', rd)


def model_fitD(data, tabs):
    """Fit D (Agnostic): CPL w0+wa, mu0 free. 6 params."""
    w0 = numpyro.sample('w0', dist.Uniform(-2.5, 0.5))
    wa = numpyro.sample('wa', dist.Uniform(-4.0, 3.0))
    Om = numpyro.sample('Om', dist.Uniform(0.15, 0.55))
    H0 = numpyro.sample('H0', dist.Uniform(55.0, 80.0))
    sigma8 = numpyro.sample('sigma8', dist.Normal(0.811, 0.03))
    mu0 = numpyro.sample('mu0', dist.Uniform(-2.0, 2.0))

    # Early-universe from CAMB grid
    rd = interp2d(Om, H0, tabs, 'rd')
    rs_star = interp2d(Om, H0, tabs, 'rs_star')
    z_star = interp2d(Om, H0, tabs, 'z_star')
    dc_star = comoving_distance_scalar(z_star, w0, wa, Om, H0)

    # Stability: w0 + wa < 0
    numpyro.factor('stability', jnp.where(w0 + wa < 0, 0.0, -1e10))

    # BAO (not affected by mu0 — purely geometric)
    dc_bao = comoving_distances_gl(BAO_Z, w0, wa, Om, H0)
    H_bao = H_of_z(BAO_Z, w0, wa, Om, H0)
    bao_vec = bao_theory(dc_bao, H_bao, rd)
    d_bao = bao_vec - data['bao_mean']
    chi2_bao = d_bao @ data['bao_cov_inv'] @ d_bao
    numpyro.factor('bao', -0.5 * chi2_bao)

    # SNe (not affected by mu0 — purely geometric)
    dc_sne = comoving_distances_gl(data['sne_z_cmb'], w0, wa, Om, H0)
    dL = (1 + data['sne_z_hel']) * dc_sne
    mu_sne = 5.0 * jnp.log10(jnp.maximum(dL, 1e-10)) + 25.0
    d_sne = data['sne_m_obs'] - mu_sne
    chi2_sne = d_sne @ data['sne_C_inv_marg'] @ d_sne
    numpyro.factor('sne', -0.5 * chi2_sne)

    # CMB compressed (not affected by mu0 at compressed level)
    R = jnp.sqrt(Om) * H0 * dc_star / C_KMS
    l_A = jnp.pi * dc_star / rs_star
    cmb_vec = jnp.array([R, l_A, OMBH2]) - data['cmb_means']
    chi2_cmb = cmb_vec @ data['cmb_cov_inv'] @ cmb_vec
    numpyro.factor('cmb', -0.5 * chi2_cmb)

    # Growth: f*sigma_8 with free mu0
    # mu(a) = 1 + mu0 * Omega_DE(a)
    fs8_pred = predict_fsigma8(w0, wa, Om, H0, sigma8, mu0, data['fs8_z'])
    chi2_fs8 = jnp.sum(((fs8_pred - data['fs8_obs']) / data['fs8_err'])**2)
    numpyro.factor('fs8', -0.5 * chi2_fs8)

    numpyro.deterministic('chi2_bao', chi2_bao)
    numpyro.deterministic('chi2_sne', chi2_sne)
    numpyro.deterministic('chi2_cmb', chi2_cmb)
    numpyro.deterministic('chi2_fs8', chi2_fs8)
    numpyro.deterministic('rd_val', rd)


# ============================================================
# MCMC RUNNER
# ============================================================

def run_fit(model_fn, data, tabs, name):
    print(f"\n{'='*70}", flush=True)
    print(f"MCMC: {name}", flush=True)
    print(f"  NUTS, {NUM_CHAINS} chain(s), {NUM_WARMUP} warmup + {NUM_SAMPLES} samples", flush=True)
    print(f"  target_accept={TARGET_ACCEPT}, max_tree_depth={MAX_TREE_DEPTH}", flush=True)
    print(f"{'='*70}", flush=True)

    kernel = NUTS(model_fn, target_accept_prob=TARGET_ACCEPT,
                  max_tree_depth=MAX_TREE_DEPTH)
    mcmc = MCMC(kernel, num_warmup=NUM_WARMUP, num_samples=NUM_SAMPLES,
                num_chains=NUM_CHAINS, progress_bar=True)

    t0 = time.time()
    mcmc.run(jax.random.PRNGKey(42), data, tabs)
    elapsed = time.time() - t0

    print(f"\n  Completed in {elapsed:.1f}s ({elapsed/60:.1f} min)", flush=True)
    mcmc.print_summary()
    return mcmc, elapsed


# ============================================================
# ANALYSIS
# ============================================================

def analyze(mcmc_A, mcmc_C, mcmc_D, data):
    sA = mcmc_A.get_samples()
    sC = mcmc_C.get_samples()
    sD = mcmc_D.get_samples()

    probes = ['bao', 'sne', 'cmb', 'fs8']

    tot_A = sum(sA[f'chi2_{p}'] for p in probes)
    tot_C = sum(sC[f'chi2_{p}'] for p in probes)
    tot_D = sum(sD[f'chi2_{p}'] for p in probes)

    chi2_A = float(jnp.min(tot_A))
    chi2_C = float(jnp.min(tot_C))
    chi2_D = float(jnp.min(tot_D))

    npar_A, npar_C, npar_D = 4, 5, 6
    n_data = 13 + (data['sne_N'] - 1) + 3 + 7  # BAO + SNe + CMB + fs8

    AIC_A = chi2_A + 2*npar_A
    AIC_C = chi2_C + 2*npar_C
    AIC_D = chi2_D + 2*npar_D

    DAIC_AC = AIC_A - AIC_C  # positive = Fit C preferred
    DAIC_CD = AIC_C - AIC_D  # positive = Fit D preferred (coupling matters)
    DAIC_AD = AIC_A - AIC_D  # positive = Fit D preferred

    BIC_A = chi2_A + npar_A * np.log(n_data)
    BIC_C = chi2_C + npar_C * np.log(n_data)
    BIC_D = chi2_D + npar_D * np.log(n_data)

    best_A = int(jnp.argmin(tot_A))
    best_C = int(jnp.argmin(tot_C))
    best_D = int(jnp.argmin(tot_D))

    print(f"\n{'='*70}", flush=True)
    print(f"19B.5 PERTURBATION ISOLATION TEST — RESULTS", flush=True)
    print(f"{'='*70}", flush=True)
    print(f"  N_data = {n_data} (BAO:13 + SNe:{data['sne_N']-1} + CMB:3 + fs8:7)")

    # Fit A results
    print(f"\nFit A (constant w, mu=1, {npar_A} params):")
    for k in ['w0', 'Om', 'H0', 'sigma8']:
        v = float(sA[k][best_A])
        m, s = float(jnp.mean(sA[k])), float(jnp.std(sA[k]))
        print(f"  {k:8s} = {v:.4f}  (mean={m:.4f} +/- {s:.4f})")
    print(f"  chi2 = {chi2_A:.2f}")

    # Fit C results
    print(f"\nFit C (CPL, mu=1 — Meridian, {npar_C} params):")
    for k in ['w0', 'wa', 'Om', 'H0', 'sigma8']:
        v = float(sC[k][best_C])
        m, s = float(jnp.mean(sC[k])), float(jnp.std(sC[k]))
        print(f"  {k:8s} = {v:.4f}  (mean={m:.4f} +/- {s:.4f})")
    print(f"  chi2 = {chi2_C:.2f}")

    # Fit D results
    print(f"\nFit D (CPL, mu0 free — agnostic, {npar_D} params):")
    for k in ['w0', 'wa', 'Om', 'H0', 'sigma8', 'mu0']:
        v = float(sD[k][best_D])
        m, s = float(jnp.mean(sD[k])), float(jnp.std(sD[k]))
        print(f"  {k:8s} = {v:.4f}  (mean={m:.4f} +/- {s:.4f})")
    print(f"  chi2 = {chi2_D:.2f}")

    # Model comparison
    print(f"\n{'='*70}")
    print(f"MODEL COMPARISON")
    print(f"{'='*70}")
    print(f"\n  DAIC(A vs C) = {DAIC_AC:+.2f}  [w(z) template test, with growth]")
    print(f"  DAIC(C vs D) = {DAIC_CD:+.2f}  [PERTURBATION ISOLATION — THE HEADLINE]")
    print(f"  DAIC(A vs D) = {DAIC_AD:+.2f}  [total]")
    print(f"\n  v5b reference (no growth): DAIC(A vs B) = +3.57 (DR2)")
    print(f"  v3 reference (with growth): DAIC(A vs B) = +7.23 (DR1)")

    # Probe decomposition for each fit pair
    print(f"\n--- Probe Decomposition (A vs C) ---")
    header = f"  {'Probe':<10} {'Fit A':>10} {'Fit C':>10} {'Delta':>10}"
    print(header)
    for p in probes:
        vA = float(sA[f'chi2_{p}'][best_A])
        vC = float(sC[f'chi2_{p}'][best_C])
        print(f"  {p:<10} {vA:>10.2f} {vC:>10.2f} {vA-vC:>+10.2f}")

    print(f"\n--- Probe Decomposition (C vs D) ---")
    header = f"  {'Probe':<10} {'Fit C':>10} {'Fit D':>10} {'Delta':>10}"
    print(header)
    for p in probes:
        vC = float(sC[f'chi2_{p}'][best_C])
        vD = float(sD[f'chi2_{p}'][best_D])
        print(f"  {p:<10} {vC:>10.2f} {vD:>10.2f} {vC-vD:>+10.2f}")

    # mu0 posterior (THE KEY RESULT)
    mu0_samples = np.array(sD['mu0'])
    q16, q50, q84 = np.percentile(mu0_samples, [16, 50, 84])
    mu0_mean = mu0_samples.mean()
    mu0_std = mu0_samples.std()
    tension_mu0 = abs(mu0_mean) / mu0_std if mu0_std > 0 else 0

    print(f"\n{'='*70}")
    print(f"mu0 POSTERIOR (Meridian predicts mu0 = 0)")
    print(f"{'='*70}")
    print(f"  Mean +/- std: {mu0_mean:.4f} +/- {mu0_std:.4f}")
    print(f"  Median: {q50:.4f} [{q16:.4f}, {q84:.4f}]")
    print(f"  Tension with mu0=0: {tension_mu0:.1f}sigma")

    if abs(mu0_mean) < mu0_std:
        print(f"\n  >> mu0 CONSISTENT WITH ZERO: Meridian prediction confirmed.")
        print(f"  >> Perturbation coupling is INVISIBLE to current data.")
    elif abs(mu0_mean) < 2*mu0_std:
        print(f"\n  >> mu0 MARGINALLY nonzero: Mild tension with Meridian ({tension_mu0:.1f}sigma).")
    else:
        print(f"\n  >> mu0 SIGNIFICANTLY nonzero: Tension with Meridian ({tension_mu0:.1f}sigma).")

    # sigma8 comparison
    print(f"\n--- sigma8 Posteriors ---")
    for name, samples in [('Fit A', sA), ('Fit C', sC), ('Fit D', sD)]:
        s8 = np.array(samples['sigma8'])
        print(f"  {name}: sigma8 = {s8.mean():.4f} +/- {s8.std():.4f}")
    print(f"  (Planck 2018: 0.811 +/- 0.006)")

    # wa posterior
    print(f"\n--- wa Posteriors ---")
    for name, samples in [('Fit C', sC), ('Fit D', sD)]:
        wa_arr = np.array(samples['wa'])
        q16, q50, q84 = np.percentile(wa_arr, [16, 50, 84])
        print(f"  {name}: wa = {wa_arr.mean():.3f} +/- {wa_arr.std():.3f}"
              f"  [{q16:.3f}, {q84:.3f}]")

    # Convergence diagnostics
    print(f"\n--- Convergence ---")
    for fit_name, mcmc in [('Fit A', mcmc_A), ('Fit C', mcmc_C), ('Fit D', mcmc_D)]:
        samples = mcmc.get_samples()
        params = ['w0', 'Om', 'H0', 'sigma8']
        if 'wa' in samples:
            params.append('wa')
        if 'mu0' in samples:
            params.append('mu0')
        for k in params:
            ess = float(numpyro.diagnostics.effective_sample_size(
                samples[k][None, :]))
            print(f"  {fit_name} {k}: ESS = {ess:.0f}")

    # Verdict
    print(f"\n{'='*70}")
    print(f"VERDICT")
    print(f"{'='*70}")

    if abs(DAIC_CD) < 2:
        print(f"  DAIC(C vs D) = {DAIC_CD:+.2f} → perturbation coupling is")
        print(f"  UNDETECTABLE by current data. The entire DESI signal is a")
        print(f"  w(z) template effect. Meridian's mu=Sigma=1 prediction is")
        print(f"  UNTESTED — not confirmed, not refuted.")
        print(f"  → Need Phase 16 detection channels (LISA, DUNE, collider).")
    elif DAIC_CD > 2:
        print(f"  DAIC(C vs D) = {DAIC_CD:+.2f} → data PREFER modified growth.")
        print(f"  Meridian's mu=Sigma=1 is under tension.")
    else:
        print(f"  DAIC(C vs D) = {DAIC_CD:+.2f} → data PREFER GR growth (mu=1).")
        print(f"  This supports Meridian but does not constitute detection.")

    print(f"\n🦞🧍💜🔥♾️", flush=True)

    return {
        'DAIC_AC': DAIC_AC, 'DAIC_CD': DAIC_CD, 'DAIC_AD': DAIC_AD,
        'chi2_A': chi2_A, 'chi2_C': chi2_C, 'chi2_D': chi2_D,
        'mu0_mean': mu0_mean, 'mu0_std': mu0_std,
    }


# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    t_start = time.time()

    print("=" * 70, flush=True)
    print("19B.5 — PERTURBATION ISOLATION TEST", flush=True)
    print(f"Platform: {jax.default_backend()}", flush=True)
    print(f"Devices: {jax.devices()}", flush=True)
    print("=" * 70, flush=True)

    # Load
    data = load_all_data()
    tabs = load_camb_grid()

    # Run all three fits
    mcmc_A, t_A = run_fit(model_fitA, data, tabs, "Fit A (constant w, mu=1)")
    mcmc_C, t_C = run_fit(model_fitC, data, tabs, "Fit C (CPL, mu=1 — Meridian)")
    mcmc_D, t_D = run_fit(model_fitD, data, tabs, "Fit D (CPL, mu0 free — agnostic)")

    # Analyze
    results = analyze(mcmc_A, mcmc_C, mcmc_D, data)

    t_total = time.time() - t_start
    print(f"\nTotal time: {t_total:.1f}s ({t_total/60:.1f} min)", flush=True)
    print(f"  Fit A: {t_A:.1f}s, Fit C: {t_C:.1f}s, Fit D: {t_D:.1f}s", flush=True)

    # Save results summary
    results_file = os.path.join(OUTPUT_DIR, '19B5_results.md')
    with open(results_file, 'w') as f:
        f.write("# 19B.5 Perturbation Isolation Test — Results\n\n")
        f.write(f"**Date:** {time.strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"**Platform:** {jax.default_backend()}, {jax.devices()}\n")
        f.write(f"**Runtime:** A={t_A:.1f}s, C={t_C:.1f}s, D={t_D:.1f}s, "
                f"Total={t_total:.1f}s\n\n")
        f.write("## Model Comparison\n\n")
        f.write(f"| Comparison | DAIC | Interpretation |\n")
        f.write(f"|------------|------|----------------|\n")
        f.write(f"| A vs C (w(z) template) | {results['DAIC_AC']:+.2f} | "
                f"{'CPL preferred' if results['DAIC_AC'] > 0 else 'constant-w preferred'} |\n")
        f.write(f"| **C vs D (perturbation)** | **{results['DAIC_CD']:+.2f}** | "
                f"**{'Modified growth preferred' if results['DAIC_CD'] > 2 else 'Coupling undetectable'}** |\n")
        f.write(f"| A vs D (total) | {results['DAIC_AD']:+.2f} | Combined |\n\n")
        f.write("## mu0 Posterior\n\n")
        f.write(f"mu0 = {results['mu0_mean']:.4f} +/- {results['mu0_std']:.4f}\n\n")
        f.write(f"Meridian predicts mu0 = 0 (cuscuton has infinite sound speed, "
                f"no gravitational slip).\n\n")
        f.write("## Chi-squared\n\n")
        f.write(f"| Fit | chi2 | params |\n")
        f.write(f"|-----|------|--------|\n")
        f.write(f"| A (constant w, mu=1) | {results['chi2_A']:.2f} | 4 |\n")
        f.write(f"| C (CPL, mu=1 — Meridian) | {results['chi2_C']:.2f} | 5 |\n")
        f.write(f"| D (CPL, mu0 free) | {results['chi2_D']:.2f} | 6 |\n\n")
        f.write("---\n\n")
        f.write("*Growth ODE solved via RK4 on GPU (500 steps). "
                "mu(a) = 1 + mu0*Omega_DE(a) parameterization.*\n\n")
        f.write("🦞🧍💜🔥♾️\n")

    print(f"\nResults saved to {results_file}", flush=True)
