#!/usr/bin/env python3
"""
18A v5 DR1 Isolation Test
=========================
IDENTICAL to v5 (18A_v5_camb_gpu.py) except:
  - DESI DR1 BAO (6 bins, diagonal errors) instead of DR2 (13 pts, full cov)

Purpose: Isolate whether DAIC drop from +7.23 (v3) to +1.10 (v5) is driven
by the data change (DR1→DR2) vs methodology change (emcee→NUTS, etc).

If DAIC ≈ +7 here → data is the story (DR2 weakens CPL preference)
If DAIC ≈ +1 here → methodology is the story (something else changed)

Authors: Clayton W. Iggulden-Schnell & Clawd
Date: 2026-03-21 (Phase 19 — Isolation Test #1)
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
OUTPUT_DIR = '/mnt/c/Users/mercu/clawd/projects/Project Meridian/phase18'

# Gauss-Legendre quadrature (64 points)
GL_NODES, GL_WEIGHTS = np.polynomial.legendre.leggauss(64)
GL_NODES = jnp.array(GL_NODES)
GL_WEIGHTS = jnp.array(GL_WEIGHTS)

# ============================================================
# CONFIGURATION
# ============================================================
USE_RD_PRIOR = False
RD_PRIOR_MEAN = 147.09
RD_PRIOR_SIGMA = 0.26

NUM_WARMUP = 500
NUM_SAMPLES = 2000
NUM_CHAINS = 1
MAX_TREE_DEPTH = 10
TARGET_ACCEPT = 0.85

# ============================================================
# DESI DR1 BAO DATA (arXiv:2404.03002, Table 1)
# ============================================================
# 6 bins, diagonal errors (no covariance matrix)
DR1_Z = jnp.array([0.30, 0.51, 0.71, 0.93, 1.32, 2.33])
DR1_DM_RD = jnp.array([7.93, 13.62, 17.86, 21.71, 27.79, 39.71])
DR1_DM_RD_ERR = jnp.array([0.15, 0.25, 0.33, 0.28, 0.69, 0.94])
DR1_DH_RD = jnp.array([20.0, 22.3, 20.1, 17.88, 13.82, 8.52])
DR1_DH_RD_ERR = jnp.array([1.0, 0.6, 0.5, 0.35, 0.42, 0.17])
N_BAO = 12  # 6 DM/rd + 6 DH/rd

# ============================================================
# DATA LOADING
# ============================================================

def load_all_data():
    print("Loading data...", flush=True)
    print(f"  BAO: DESI DR1 (6 bins, diagonal errors)", flush=True)

    # SNe (identical to v5)
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

    # CMB compressed (identical to v5)
    cmb_means = jnp.array([1.7502, 301.471, 0.02237])
    cmb_sigmas = jnp.array([0.0046, 0.090, 0.00015])
    cmb_corr = jnp.array([[1.0, 0.46, -0.66],
                           [0.46, 1.0, -0.33],
                           [-0.66, -0.33, 1.0]])
    cmb_cov = jnp.outer(cmb_sigmas, cmb_sigmas) * cmb_corr
    cmb_cov_inv = jnp.linalg.inv(cmb_cov)

    print("  All data loaded.", flush=True)
    return {
        'sne_m_obs': jnp.array(m_obs), 'sne_z_cmb': jnp.array(z_cmb),
        'sne_z_hel': jnp.array(z_hel), 'sne_C_inv_marg': jnp.array(C_inv_marg),
        'sne_N': N_sne,
        'cmb_means': cmb_means, 'cmb_cov_inv': cmb_cov_inv,
    }

# ============================================================
# CAMB GRID (precomputed — identical to v5)
# ============================================================

def load_camb_grid():
    grid_file = os.path.join(OUTPUT_DIR, 'camb_grid_100x100.npz')
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
# COSMOLOGY (identical to v5)
# ============================================================

def Ez2(z, w0, wa, Om, h):
    a = 1.0 / (1.0 + z)
    Or = OMEGA_R_H2 / h**2
    ODE = 1.0 - Om - Or
    de = a**(-3*(1 + w0 + wa)) * jnp.exp(-3*wa*(1 - a))
    return Om*(1+z)**3 + Or*(1+z)**4 + ODE*de

def comoving_distances_gl(z_arr, w0, wa, Om, H0):
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
# DR1 BAO LIKELIHOOD (diagonal — matches v3 approach)
# ============================================================

def bao_chi2_dr1(w0, wa, Om, H0, rd):
    """BAO chi2 using DR1 data with diagonal errors."""
    dc = comoving_distances_gl(DR1_Z, w0, wa, Om, H0)
    H = H_of_z(DR1_Z, w0, wa, Om, H0)
    DM_rd_theory = dc / rd
    DH_rd_theory = C_KMS / H / rd
    chi2_DM = jnp.sum(((DM_rd_theory - DR1_DM_RD) / DR1_DM_RD_ERR)**2)
    chi2_DH = jnp.sum(((DH_rd_theory - DR1_DH_RD) / DR1_DH_RD_ERR)**2)
    return chi2_DM + chi2_DH

# ============================================================
# NUMPYRO MODELS
# ============================================================

def model_fitA(data, tabs):
    """Fit A: constant w0, GR perturbations."""
    w0 = numpyro.sample('w0', dist.Uniform(-2.5, 0.0))
    Om = numpyro.sample('Om', dist.Uniform(0.15, 0.55))
    H0 = numpyro.sample('H0', dist.Uniform(55.0, 80.0))

    rd = interp2d(Om, H0, tabs, 'rd')
    rs_star = interp2d(Om, H0, tabs, 'rs_star')
    z_star = interp2d(Om, H0, tabs, 'z_star')
    dc_star = comoving_distance_scalar(z_star, w0, 0.0, Om, H0)

    # BAO (DR1, diagonal)
    chi2_bao = bao_chi2_dr1(w0, 0.0, Om, H0, rd)
    numpyro.factor('bao', -0.5 * chi2_bao)

    # SNe (identical to v5)
    dc_sne = comoving_distances_gl(data['sne_z_cmb'], w0, 0.0, Om, H0)
    dL = (1 + data['sne_z_hel']) * dc_sne
    mu = 5.0 * jnp.log10(jnp.maximum(dL, 1e-10)) + 25.0
    d_sne = data['sne_m_obs'] - mu
    chi2_sne = d_sne @ data['sne_C_inv_marg'] @ d_sne
    numpyro.factor('sne', -0.5 * chi2_sne)

    # CMB compressed
    R = jnp.sqrt(Om) * H0 * dc_star / C_KMS
    l_A = jnp.pi * dc_star / rs_star
    cmb_vec = jnp.array([R, l_A, OMBH2]) - data['cmb_means']
    chi2_cmb = cmb_vec @ data['cmb_cov_inv'] @ cmb_vec
    numpyro.factor('cmb', -0.5 * chi2_cmb)

    if USE_RD_PRIOR:
        chi2_rd = ((rd - RD_PRIOR_MEAN) / RD_PRIOR_SIGMA)**2
        numpyro.factor('rd_prior', -0.5 * chi2_rd)
        numpyro.deterministic('chi2_rd', chi2_rd)

    numpyro.deterministic('chi2_bao', chi2_bao)
    numpyro.deterministic('chi2_sne', chi2_sne)
    numpyro.deterministic('chi2_cmb', chi2_cmb)
    numpyro.deterministic('rd_val', rd)

def model_fitB(data, tabs):
    """Fit B: CPL w0+wa, coupled perturbations."""
    w0 = numpyro.sample('w0', dist.Uniform(-2.5, 0.5))
    wa = numpyro.sample('wa', dist.Uniform(-4.0, 3.0))
    Om = numpyro.sample('Om', dist.Uniform(0.15, 0.55))
    H0 = numpyro.sample('H0', dist.Uniform(55.0, 80.0))

    rd = interp2d(Om, H0, tabs, 'rd')
    rs_star = interp2d(Om, H0, tabs, 'rs_star')
    z_star = interp2d(Om, H0, tabs, 'z_star')
    dc_star = comoving_distance_scalar(z_star, w0, wa, Om, H0)

    numpyro.factor('stability', jnp.where(w0 + wa < 0, 0.0, -1e10))

    # BAO (DR1, diagonal)
    chi2_bao = bao_chi2_dr1(w0, wa, Om, H0, rd)
    numpyro.factor('bao', -0.5 * chi2_bao)

    # SNe (identical to v5)
    dc_sne = comoving_distances_gl(data['sne_z_cmb'], w0, wa, Om, H0)
    dL = (1 + data['sne_z_hel']) * dc_sne
    mu = 5.0 * jnp.log10(jnp.maximum(dL, 1e-10)) + 25.0
    d_sne = data['sne_m_obs'] - mu
    chi2_sne = d_sne @ data['sne_C_inv_marg'] @ d_sne
    numpyro.factor('sne', -0.5 * chi2_sne)

    # CMB compressed (identical to v5)
    R = jnp.sqrt(Om) * H0 * dc_star / C_KMS
    l_A = jnp.pi * dc_star / rs_star
    cmb_vec = jnp.array([R, l_A, OMBH2]) - data['cmb_means']
    chi2_cmb = cmb_vec @ data['cmb_cov_inv'] @ cmb_vec
    numpyro.factor('cmb', -0.5 * chi2_cmb)

    if USE_RD_PRIOR:
        chi2_rd = ((rd - RD_PRIOR_MEAN) / RD_PRIOR_SIGMA)**2
        numpyro.factor('rd_prior', -0.5 * chi2_rd)
        numpyro.deterministic('chi2_rd', chi2_rd)

    numpyro.deterministic('chi2_bao', chi2_bao)
    numpyro.deterministic('chi2_sne', chi2_sne)
    numpyro.deterministic('chi2_cmb', chi2_cmb)
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

def analyze(mcmc_A, mcmc_B, data):
    sA = mcmc_A.get_samples()
    sB = mcmc_B.get_samples()

    probes = ['bao', 'sne', 'cmb']
    if USE_RD_PRIOR:
        probes.append('rd')

    tot_A = sum(sA[f'chi2_{p}'] for p in probes)
    tot_B = sum(sB[f'chi2_{p}'] for p in probes)

    chi2_A = float(jnp.min(tot_A))
    chi2_B = float(jnp.min(tot_B))

    npar_A, npar_B = 3, 4
    # DR1: 12 BAO points + (N_sne - 1) + 3 CMB
    n_data = N_BAO + (data['sne_N'] - 1) + 3

    AIC_A = chi2_A + 2*npar_A
    AIC_B = chi2_B + 2*npar_B
    DAIC = AIC_A - AIC_B

    BIC_A = chi2_A + npar_A * np.log(n_data)
    BIC_B = chi2_B + npar_B * np.log(n_data)
    DBIC = BIC_A - BIC_B

    best_A = int(jnp.argmin(tot_A))
    best_B = int(jnp.argmin(tot_B))

    print(f"\n{'='*70}", flush=True)
    print(f"18A v5 DR1 ISOLATION TEST — RESULTS", flush=True)
    print(f"{'='*70}", flush=True)
    print(f"  BAO data: DESI DR1 (6 bins, diagonal errors)")
    print(f"  rd prior: {'ON (147.09 +/- 0.26)' if USE_RD_PRIOR else 'OFF'}")

    print(f"\nFit A (constant w, GR):")
    for k in ['w0', 'Om', 'H0']:
        v = float(sA[k][best_A])
        m, s = float(jnp.mean(sA[k])), float(jnp.std(sA[k]))
        print(f"  {k} = {v:.4f}  (mean={m:.4f} +/- {s:.4f})")
    print(f"  rd = {float(sA['rd_val'][best_A]):.2f} Mpc "
          f"(mean={float(jnp.mean(sA['rd_val'])):.2f} +/- {float(jnp.std(sA['rd_val'])):.2f})")
    print(f"  chi2 = {chi2_A:.2f}")

    print(f"\nFit B (CPL, coupled):")
    for k in ['w0', 'wa', 'Om', 'H0']:
        v = float(sB[k][best_B])
        m, s = float(jnp.mean(sB[k])), float(jnp.std(sB[k]))
        print(f"  {k} = {v:.4f}  (mean={m:.4f} +/- {s:.4f})")
    print(f"  rd = {float(sB['rd_val'][best_B]):.2f} Mpc "
          f"(mean={float(jnp.mean(sB['rd_val'])):.2f} +/- {float(jnp.std(sB['rd_val'])):.2f})")
    print(f"  chi2 = {chi2_B:.2f}")

    print(f"\n--- Model Comparison ---")
    print(f"  DAIC = {DAIC:+.2f}  (positive = CPL preferred)")
    print(f"  DBIC = {DBIC:+.2f}")
    print(f"  v3 reference (DR1, emcee+CAMB): DAIC = +7.23")
    print(f"  v5 reference (DR2, NUTS+CAMB):  DAIC = +1.10")

    print(f"\n--- Probe Decomposition ---")
    header = f"  {'Probe':<10} {'Fit A':>10} {'Fit B':>10} {'Delta':>10}"
    print(header)
    for p in probes:
        vA = float(sA[f'chi2_{p}'][best_A])
        vB = float(sB[f'chi2_{p}'][best_B])
        print(f"  {p:<10} {vA:>10.2f} {vB:>10.2f} {vA-vB:>+10.2f}")

    # wa posterior
    wa = np.array(sB['wa'])
    q16, q50, q84 = np.percentile(wa, [16, 50, 84])
    print(f"\n--- wa Posterior ---")
    print(f"  Mean +/- std: {wa.mean():.3f} +/- {wa.std():.3f}")
    print(f"  Median: {q50:.3f} [{q16:.3f}, {q84:.3f}]")
    tension = abs(wa.mean()) / wa.std() if wa.std() > 0 else 0
    print(f"  Tension with wa=0: {tension:.1f}sigma")

    # Sound horizon check
    rd_A = np.array(sA['rd_val'])
    rd_B = np.array(sB['rd_val'])
    print(f"\n--- Sound Horizon ---")
    print(f"  Fit A: rd = {rd_A.mean():.2f} +/- {rd_A.std():.2f} Mpc")
    print(f"  Fit B: rd = {rd_B.mean():.2f} +/- {rd_B.std():.2f} Mpc")
    print(f"  (CAMB fiducial: 147.09 Mpc)")

    # Convergence diagnostics
    print(f"\n--- Convergence ---")
    for fit_name, mcmc in [('Fit A', mcmc_A), ('Fit B', mcmc_B)]:
        samples = mcmc.get_samples()
        for k in ['w0', 'Om', 'H0'] + (['wa'] if 'wa' in samples else []):
            ess = float(numpyro.diagnostics.effective_sample_size(
                samples[k][None, :]))
            print(f"  {fit_name} {k}: ESS = {ess:.0f}")

    # Interpretation
    print(f"\n--- Isolation Test Interpretation ---")
    if DAIC > 5:
        print(f"  DAIC = {DAIC:+.2f} ≈ v3 (+7.23) → DATA is the story")
        print(f"  DR1→DR2 transition explains the DAIC drop")
        print(f"  Method change (emcee→NUTS) is NOT the driver")
    elif DAIC < 3:
        print(f"  DAIC = {DAIC:+.2f} ≈ v5 (+1.10) → METHODOLOGY is the story")
        print(f"  Something other than DR1→DR2 explains the drop")
    else:
        print(f"  DAIC = {DAIC:+.2f} — intermediate, both factors contribute")

    if DAIC > 10:
        verdict = "STRONG CPL preference"
    elif DAIC > 6:
        verdict = "MODERATE CPL preference"
    elif DAIC > 2:
        verdict = "WEAK CPL preference"
    else:
        verdict = "NO significant preference"
    print(f"\n  VERDICT: {verdict} (DAIC = {DAIC:+.2f})")

    return {'DAIC': DAIC, 'DBIC': DBIC, 'chi2_A': chi2_A, 'chi2_B': chi2_B}


# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    t_start = time.time()

    print("=" * 70, flush=True)
    print("18A v5 DR1 ISOLATION TEST", flush=True)
    print(f"Platform: {jax.default_backend()}", flush=True)
    print(f"Devices: {jax.devices()}", flush=True)
    print(f"BAO: DESI DR1 (6 bins, diagonal errors)", flush=True)
    print(f"rd prior: {'ON' if USE_RD_PRIOR else 'OFF'}", flush=True)
    print("=" * 70, flush=True)

    # Load
    data = load_all_data()
    tabs = load_camb_grid()

    # Run
    mcmc_A, t_A = run_fit(model_fitA, data, tabs, "Fit A (constant w, GR) — DR1 BAO")
    mcmc_B, t_B = run_fit(model_fitB, data, tabs, "Fit B (CPL, coupled) — DR1 BAO")

    # Analyze
    results = analyze(mcmc_A, mcmc_B, data)

    t_total = time.time() - t_start
    print(f"\nTotal time: {t_total:.1f}s ({t_total/60:.1f} min)", flush=True)

    # Save results summary
    results_file = os.path.join(OUTPUT_DIR, '18A_v5_dr1_results.md')
    with open(results_file, 'w') as f:
        f.write(f"# 18A v5 DR1 Isolation Test Results\n\n")
        f.write(f"**Purpose:** Isolate DR1→DR2 effect on DAIC\n")
        f.write(f"**Platform:** {jax.default_backend()}, {jax.devices()}\n")
        f.write(f"**Runtime:** Fit A = {t_A:.1f}s, Fit B = {t_B:.1f}s, Total = {t_total:.1f}s\n")
        f.write(f"**BAO data:** DESI DR1 (6 bins, diagonal errors)\n")
        f.write(f"**rd prior:** {'ON (147.09 +/- 0.26)' if USE_RD_PRIOR else 'OFF'}\n\n")
        f.write(f"**DAIC = {results['DAIC']:+.2f}**\n")
        f.write(f"**DBIC = {results['DBIC']:+.2f}**\n\n")
        f.write(f"chi2_A = {results['chi2_A']:.2f}\n")
        f.write(f"chi2_B = {results['chi2_B']:.2f}\n\n")
        f.write(f"| Run | BAO | DAIC |\n")
        f.write(f"|-----|-----|------|\n")
        f.write(f"| v3 (emcee+CAMB) | DR1 | +7.23 |\n")
        f.write(f"| v5 (NUTS+CAMB) | DR2 | +1.10 |\n")
        f.write(f"| **This test** (NUTS+CAMB) | **DR1** | **{results['DAIC']:+.2f}** |\n\n")
        if results['DAIC'] > 5:
            f.write(f"**Conclusion:** DR1→DR2 explains the DAIC drop. Data is the story.\n")
        elif results['DAIC'] < 3:
            f.write(f"**Conclusion:** Methodology change drives the DAIC drop, not data.\n")
        else:
            f.write(f"**Conclusion:** Both data and methodology contribute.\n")
    print(f"\nResults saved to {results_file}", flush=True)
    print("\n🦞🧍💜🔥♾️", flush=True)
