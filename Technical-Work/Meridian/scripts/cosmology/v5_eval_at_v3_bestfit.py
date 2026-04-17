#!/usr/bin/env python3
"""
Evaluate v5 DR1 likelihood at v3 best-fit parameters.
======================================================
If chi² values agree → same likelihood surface, v3 emcee found suboptimal minimum
If chi² values disagree → likelihood functions differ (CAMB vs grid, fσ₈ effect, etc.)
"""

import numpy as np
import os
import sys

# We need JAX for the GL quadrature and grid interpolation
import jax
jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp

C_KMS = 299792.458
OMEGA_GAMMA_H2 = 2.469e-5
N_EFF = 3.046
OMEGA_R_H2 = OMEGA_GAMMA_H2 * (1 + 7/8 * (4/11)**(4/3) * N_EFF)
OMBH2 = 0.02237

DATA_DIR = '/mnt/c/Users/mercu/clawd/projects/Project Meridian/phase18/data'
OUTPUT_DIR = '/mnt/c/Users/mercu/clawd/projects/Project Meridian/phase18'

GL_NODES, GL_WEIGHTS = np.polynomial.legendre.leggauss(64)
GL_NODES = jnp.array(GL_NODES)
GL_WEIGHTS = jnp.array(GL_WEIGHTS)

# ============================================================
# DR1 BAO DATA
# ============================================================
DR1_Z = jnp.array([0.30, 0.51, 0.71, 0.93, 1.32, 2.33])
DR1_DM_RD = jnp.array([7.93, 13.62, 17.86, 21.71, 27.79, 39.71])
DR1_DM_RD_ERR = jnp.array([0.15, 0.25, 0.33, 0.28, 0.69, 0.94])
DR1_DH_RD = jnp.array([20.0, 22.3, 20.1, 17.88, 13.82, 8.52])
DR1_DH_RD_ERR = jnp.array([1.0, 0.6, 0.5, 0.35, 0.42, 0.17])

# ============================================================
# COSMOLOGY
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
# DATA LOADING
# ============================================================
def load_sne():
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
    return jnp.array(m_obs), jnp.array(z_cmb), jnp.array(z_hel), jnp.array(C_inv_marg), N_sne

def load_camb_grid():
    g = np.load(os.path.join(OUTPUT_DIR, 'camb_grid_100x100.npz'))
    rd = np.nan_to_num(g['rd'], nan=np.nanmedian(g['rd']))
    rs_star = np.nan_to_num(g['rs_star'], nan=np.nanmedian(g['rs_star']))
    dc_star = np.nan_to_num(g['dc_star'], nan=np.nanmedian(g['dc_star']))
    return {
        'Om_grid': jnp.array(g['Om_grid']),
        'H0_grid': jnp.array(g['H0_grid']),
        'rd': jnp.array(rd),
        'rs_star': jnp.array(rs_star),
        'dc_star': jnp.array(dc_star),
    }

# ============================================================
# CHI2 EVALUATION
# ============================================================
def eval_chi2(w0, wa, Om, H0, sne_m_obs, sne_z_cmb, sne_z_hel, sne_C_inv_marg,
              cmb_means, cmb_cov_inv, tabs):
    """Evaluate per-probe chi2 using v5 DR1 method."""
    rd = interp2d(Om, H0, tabs, 'rd')
    rs_star = interp2d(Om, H0, tabs, 'rs_star')
    dc_star = interp2d(Om, H0, tabs, 'dc_star')

    # BAO (DR1, diagonal)
    dc_bao = comoving_distances_gl(DR1_Z, w0, wa, Om, H0)
    H_bao = H_of_z(DR1_Z, w0, wa, Om, H0)
    DM_rd = dc_bao / rd
    DH_rd = C_KMS / H_bao / rd
    chi2_bao = float(jnp.sum(((DM_rd - DR1_DM_RD) / DR1_DM_RD_ERR)**2) +
                     jnp.sum(((DH_rd - DR1_DH_RD) / DR1_DH_RD_ERR)**2))

    # SNe
    dc_sne = comoving_distances_gl(sne_z_cmb, w0, wa, Om, H0)
    dL = (1 + sne_z_hel) * dc_sne
    mu = 5.0 * jnp.log10(jnp.maximum(dL, 1e-10)) + 25.0
    d_sne = sne_m_obs - mu
    chi2_sne = float(d_sne @ sne_C_inv_marg @ d_sne)

    # CMB
    R = jnp.sqrt(Om) * H0 * dc_star / C_KMS
    l_A = jnp.pi * dc_star / rs_star
    cmb_vec = jnp.array([R, l_A, OMBH2]) - cmb_means
    chi2_cmb = float(cmb_vec @ cmb_cov_inv @ cmb_vec)

    total = chi2_bao + chi2_sne + chi2_cmb
    return chi2_bao, chi2_sne, chi2_cmb, total, float(rd)

# ============================================================
# MAIN
# ============================================================
print("Loading data...", flush=True)
sne_m_obs, sne_z_cmb, sne_z_hel, sne_C_inv_marg, N_sne = load_sne()
tabs = load_camb_grid()

cmb_means = jnp.array([1.7502, 301.471, 0.02237])
cmb_sigmas = jnp.array([0.0046, 0.090, 0.00015])
cmb_corr = jnp.array([[1.0, 0.46, -0.66], [0.46, 1.0, -0.33], [-0.66, -0.33, 1.0]])
cmb_cov = jnp.outer(cmb_sigmas, cmb_sigmas) * cmb_corr
cmb_cov_inv = jnp.linalg.inv(cmb_cov)

# v3 best-fit parameters
V3_A = {'w0': -1.0109, 'Om': 0.3094, 'H0': 67.92}
V3_B = {'w0': -0.8230, 'wa': -0.8452, 'Om': 0.3081, 'H0': 68.29}

# v5 DR1 test best-fit parameters
V5_A = {'w0': -0.9548, 'Om': 0.3113, 'H0': 67.88}
V5_B = {'w0': -0.8438, 'wa': -0.6337, 'Om': 0.3110, 'H0': 67.90}

print(f"\n{'='*70}")
print(f"  LIKELIHOOD COMPARISON: v5-DR1 chi² at various parameter points")
print(f"{'='*70}")

for label, params, wa_val in [
    ("v3 Fit A best-fit", V3_A, 0.0),
    ("v5 Fit A best-fit", V5_A, 0.0),
    ("v3 Fit B best-fit", V3_B, V3_B['wa']),
    ("v5 Fit B best-fit", V5_B, V5_B['wa']),
]:
    bao, sne, cmb, total, rd = eval_chi2(
        params['w0'], wa_val, params['Om'], params['H0'],
        sne_m_obs, sne_z_cmb, sne_z_hel, sne_C_inv_marg,
        cmb_means, cmb_cov_inv, tabs)
    print(f"\n  {label}:")
    print(f"    Params: w0={params['w0']:.4f}, " +
          (f"wa={wa_val:.4f}, " if wa_val != 0 else "") +
          f"Om={params['Om']:.4f}, H0={params['H0']:.2f}")
    print(f"    rd = {rd:.2f} Mpc")
    print(f"    BAO:  {bao:.2f}")
    print(f"    SNe:  {sne:.2f}")
    print(f"    CMB:  {cmb:.2f}")
    print(f"    TOTAL: {total:.2f}")

print(f"\n{'='*70}")
print(f"  KEY COMPARISON")
print(f"{'='*70}")

# Evaluate at v3 points
bao_a3, sne_a3, cmb_a3, tot_a3, _ = eval_chi2(V3_A['w0'], 0.0, V3_A['Om'], V3_A['H0'],
    sne_m_obs, sne_z_cmb, sne_z_hel, sne_C_inv_marg, cmb_means, cmb_cov_inv, tabs)
bao_b3, sne_b3, cmb_b3, tot_b3, _ = eval_chi2(V3_B['w0'], V3_B['wa'], V3_B['Om'], V3_B['H0'],
    sne_m_obs, sne_z_cmb, sne_z_hel, sne_C_inv_marg, cmb_means, cmb_cov_inv, tabs)

# Evaluate at v5 points
bao_a5, sne_a5, cmb_a5, tot_a5, _ = eval_chi2(V5_A['w0'], 0.0, V5_A['Om'], V5_A['H0'],
    sne_m_obs, sne_z_cmb, sne_z_hel, sne_C_inv_marg, cmb_means, cmb_cov_inv, tabs)
bao_b5, sne_b5, cmb_b5, tot_b5, _ = eval_chi2(V5_B['w0'], V5_B['wa'], V5_B['Om'], V5_B['H0'],
    sne_m_obs, sne_z_cmb, sne_z_hel, sne_C_inv_marg, cmb_means, cmb_cov_inv, tabs)

print(f"\n  v5-DR1 chi² using v3 parameters:  A={tot_a3:.2f}, B={tot_b3:.2f}, Delta={tot_a3-tot_b3:.2f}")
print(f"  v5-DR1 chi² using v5 parameters:  A={tot_a5:.2f}, B={tot_b5:.2f}, Delta={tot_a5-tot_b5:.2f}")
print(f"  v3 reported chi²:                 A=1458.77, B=1449.53, Delta=9.23")
print()

gap_a = tot_a3 - 1458.77
gap_b = tot_b3 - 1449.53
print(f"  Gap at v3 Fit A point: v5_chi2 - v3_chi2 = {tot_a3:.2f} - 1458.77 = {gap_a:+.2f}")
print(f"  Gap at v3 Fit B point: v5_chi2 - v3_chi2 = {tot_b3:.2f} - 1449.53 = {gap_b:+.2f}")
print()

if abs(gap_a) < 2 and abs(gap_b) < 2:
    print("  CONCLUSION: Likelihoods agree at same parameters.")
    print("  v3 emcee found the same surface as v5.")
    print("  Chi² difference is dominated by fσ₈ (not in v5).")
    print("  The ΔAIC difference comes from v3 NOT finding the v5 minimum.")
elif gap_a < -5:
    print("  CONCLUSION: v5 chi² is LOWER than v3 at v3's own best-fit.")
    print("  The likelihood functions differ — grid interpolation changes the surface.")
    print(f"  Per-probe: BAO gap={bao_a3-42.06:+.2f}, SNe gap={sne_a3-1402.64:+.2f}, CMB gap={cmb_a3-0.64:+.2f}")
else:
    print(f"  CONCLUSION: Complex — gaps are A={gap_a:+.2f}, B={gap_b:+.2f}")
    print("  Possible combination of fσ₈ offset + grid interpolation + parameter shift")

# Final: does v5 find a better minimum than v3 on v5's OWN surface?
print(f"\n  Is v5 minimum lower than v3 point? Fit A: {tot_a5:.2f} vs {tot_a3:.2f} → {'YES' if tot_a5 < tot_a3 else 'NO'} (diff={tot_a3-tot_a5:+.2f})")
print(f"  Is v5 minimum lower than v3 point? Fit B: {tot_b5:.2f} vs {tot_b3:.2f} → {'YES' if tot_b5 < tot_b3 else 'NO'} (diff={tot_b3-tot_b5:+.2f})")
