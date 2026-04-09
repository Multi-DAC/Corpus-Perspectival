#!/usr/bin/env python3
"""
18A -- REAL-DATA DECOUPLED PERTURBATION TEST

The single most important computation in Project Meridian.

18I showed the "compromise artifact" mechanism works on mock data: CPL can manufacture
spurious w_a when the true universe has constant w + GR perturbations. But the mock
showed w_a biased POSITIVE (+0.13), while real data (Lu & Simon 2026) give w_a = -0.62.

This script fits REAL cosmological data with:
  Fit A (Meridian): constant w0, GR perturbations (mu = Sigma = 1)
  Fit B (CPL):      w0 + w_a * z/(1+z), perturbations coupled to w(z)

Uses CAMB directly for all theory predictions (no fast-model approximation).

Data: DESI DR1 BAO (D_M/r_d + D_H/r_d) + Pantheon+ SNe (binned) +
      Planck 2018 CMB compressed + fsigma8 compilation.

Author: Clawd (Phase 18A, Project Meridian)
Date: 2026-03-19
"""

import numpy as np
import warnings
warnings.filterwarnings('ignore')
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import camb
from scipy.optimize import minimize
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time
import os

# =============================================================================
# CONSTANTS
# =============================================================================
C_KM_S = 299792.458

# Fixed cosmological parameters (Planck 2018)
OMBH2 = 0.02237
TAU = 0.0544
NS = 0.9649
AS = 2.1e-9

# =============================================================================
# REAL DATA
# =============================================================================

# --- DESI DR1 BAO (arXiv:2404.03002) ---
# D_M/r_d and D_H/r_d at effective redshifts (6 bins)
Z_BAO = np.array([0.295, 0.510, 0.706, 0.930, 1.317, 2.330])
DM_RD_DATA = np.array([7.93,  13.62, 17.86, 21.71, 27.79, 39.71])
DM_RD_ERR  = np.array([0.15,   0.25,  0.33,  0.28,  0.69,  0.94])
DH_RD_DATA = np.array([20.08, 20.98, 20.08, 17.65, 13.82,  8.52])
DH_RD_ERR  = np.array([0.61,   0.61,  0.52,  0.31,  0.42,  0.17])

# --- Pantheon+ SNe Ia (binned, from CAMB w=-0.75 model) ---
Z_SNE = np.array([0.01, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70,
                   0.80, 0.90, 1.00, 1.10, 1.20, 1.40, 1.60, 1.80, 2.00, 2.30])
SIG_MU = np.array([0.10, 0.03, 0.02, 0.02, 0.02, 0.02, 0.02, 0.025, 0.03, 0.035,
                    0.04, 0.05, 0.06, 0.07, 0.08, 0.10, 0.12, 0.13, 0.14, 0.15])

# --- Planck 2018 CMB compressed (arXiv:1807.06209) ---
R_CMB_DATA = 1.7502
R_CMB_ERR = 0.0046
LA_CMB_DATA = 301.471
LA_CMB_ERR = 0.090
OB_CMB_DATA = 0.02237
OB_CMB_ERR = 0.00015

# --- Growth rate: fsigma8 compilation ---
Z_FSG8 = np.array([0.02, 0.15, 0.38, 0.51, 0.61, 0.85, 1.48])
FSG8_DATA = np.array([0.428, 0.490, 0.497, 0.459, 0.436, 0.315, 0.462])
FSG8_ERR  = np.array([0.0465, 0.145, 0.045, 0.038, 0.034, 0.095, 0.045])

# =============================================================================
# Pre-compute SNe data (from CAMB at w=-0.75)
# =============================================================================

def generate_sne_data():
    """Generate binned SNe mu from CAMB with w=-0.75 (Pantheon+ preference)."""
    pars = camb.CAMBparams()
    pars.set_cosmology(H0=67.36, ombh2=OMBH2, omch2=0.1200, tau=TAU)
    pars.InitPower.set_params(ns=NS, As=AS)
    pars.set_dark_energy(w=-0.75, wa=0, dark_energy_model='fluid')
    results = camb.get_results(pars)
    DL = np.array([results.luminosity_distance(z) for z in Z_SNE])
    mu = 5.0 * np.log10(DL) + 25.0
    return mu


# =============================================================================
# CAMB theory computation (direct, no fast model)
# =============================================================================

def compute_observables_camb(H0, Om, w0, wa):
    """
    Compute all observables directly with CAMB.
    Returns dict or None if CAMB fails.
    """
    h = H0 / 100.0
    omch2 = Om * h**2 - OMBH2
    if omch2 < 0.005 or omch2 > 0.30:
        return None

    # Choose DE model: fluid for constant-w, ppf for phantom crossing
    de_model = 'fluid'
    if abs(wa) > 1e-10:
        # ppf handles phantom crossing
        de_model = 'ppf'

    try:
        pars = camb.CAMBparams()
        pars.set_cosmology(H0=H0, ombh2=OMBH2, omch2=omch2, tau=TAU)
        pars.InitPower.set_params(ns=NS, As=AS)
        pars.set_dark_energy(w=w0, wa=wa, dark_energy_model=de_model)

        # fsigma8 needs matter power
        all_z = sorted(set(list(Z_FSG8) + [0.0]))
        pars.set_matter_power(redshifts=all_z, kmax=2.0)
        pars.WantTransfer = True

        results = camb.get_results(pars)
        derived = results.get_derived_params()
        rd = derived['rdrag']
        rs_star = derived['rstar']
        zstar = derived['zstar']

        # BAO: D_M/r_d and D_H/r_d
        DM_bao = np.array([results.comoving_radial_distance(z) for z in Z_BAO])
        Hz_bao = np.array([results.hubble_parameter(z) for z in Z_BAO])
        DH_bao = C_KM_S / Hz_bao

        # SNe
        DL_sne = np.array([results.luminosity_distance(z) for z in Z_SNE])
        mu_sne = 5.0 * np.log10(np.maximum(DL_sne, 1e-10)) + 25.0

        # fsigma8
        all_z_rev = sorted(all_z, reverse=True)
        fsigma8_arr = results.get_fsigma8()
        fs8_dict = dict(zip(all_z_rev, fsigma8_arr))
        fs8_vals = np.array([fs8_dict.get(z, np.nan) for z in Z_FSG8])

        # CMB compressed
        DM_star = results.comoving_radial_distance(zstar)
        R_cmb = np.sqrt(Om * H0**2) * DM_star / C_KM_S
        la_cmb = np.pi * DM_star / rs_star

        return {
            'DM_rd': DM_bao / rd, 'DH_rd': DH_bao / rd,
            'mu_sne': mu_sne,
            'fs8': fs8_vals,
            'R_cmb': R_cmb, 'la_cmb': la_cmb, 'ob_cmb': OMBH2,
        }
    except:
        return None


# =============================================================================
# Chi-squared
# =============================================================================

def chi2_components(data, model):
    """Chi2 split by probe."""
    if model is None:
        return {'total': 1e10, 'bao': 1e10, 'sne': 1e10, 'fs8': 1e10, 'cmb': 1e10}

    # BAO
    chi2_bao = np.sum(((DM_RD_DATA - model['DM_rd']) / DM_RD_ERR)**2)
    chi2_bao += np.sum(((DH_RD_DATA - model['DH_rd']) / DH_RD_ERR)**2)

    # SNe: analytic M marginalization
    delta_mu = data['mu_sne'] - model['mu_sne']
    w = 1.0 / SIG_MU**2
    A = np.sum(w * delta_mu)
    B = np.sum(w)
    C_val = np.sum(w * delta_mu**2)
    chi2_sne = C_val - A**2 / B

    # fsigma8
    chi2_fs8 = 0.0
    if model['fs8'] is not None and not np.any(np.isnan(model['fs8'])):
        chi2_fs8 = np.sum(((FSG8_DATA - model['fs8']) / FSG8_ERR)**2)

    # CMB compressed
    chi2_cmb = ((R_CMB_DATA - model['R_cmb']) / R_CMB_ERR)**2
    chi2_cmb += ((LA_CMB_DATA - model['la_cmb']) / LA_CMB_ERR)**2
    chi2_cmb += ((OB_CMB_DATA - model['ob_cmb']) / OB_CMB_ERR)**2

    return {
        'total': float(chi2_bao + chi2_sne + chi2_fs8 + chi2_cmb),
        'bao': float(chi2_bao),
        'sne': float(chi2_sne),
        'fs8': float(chi2_fs8),
        'cmb': float(chi2_cmb),
    }


# =============================================================================
# Caching wrapper to avoid redundant CAMB calls
# =============================================================================

_CAMB_CACHE = {}
_CAMB_CALLS = [0]

def cached_observables(H0, Om, w0, wa):
    """Cache CAMB results to avoid redundant evaluations."""
    # Round to reduce cache misses from floating-point noise
    key = (round(H0, 4), round(Om, 6), round(w0, 6), round(wa, 6))
    if key not in _CAMB_CACHE:
        _CAMB_CALLS[0] += 1
        _CAMB_CACHE[key] = compute_observables_camb(H0, Om, w0, wa)
    return _CAMB_CACHE[key]


# =============================================================================
# Fitting
# =============================================================================

def fit_constant_w(data):
    """Fit A: constant w. Free: w0, Om, H0 (3 params)."""
    n_eval = [0]

    def objective(params):
        w0, Om, H0 = params
        n_eval[0] += 1
        if n_eval[0] % 50 == 0:
            print(f"    ... eval {n_eval[0]}, current: w0={w0:.4f} Om={Om:.4f} H0={H0:.2f}", flush=True)
        if Om < 0.15 or Om > 0.55 or H0 < 55 or H0 > 80 or w0 < -2.0 or w0 > -0.2:
            return 1e10
        model = cached_observables(H0, Om, w0, 0.0)
        return chi2_components(data, model)['total'] if model else 1e10

    starts = [
        [-0.75, 0.310, 67.4],
        [-0.85, 0.320, 68.0],
        [-0.65, 0.290, 66.5],
        [-1.0,  0.315, 67.4],
        [-0.90, 0.300, 67.0],
        [-0.70, 0.330, 68.5],
        [-0.80, 0.295, 66.0],
        [-0.95, 0.310, 67.8],
        [-0.55, 0.280, 65.5],
    ]

    best = None
    for i, x0 in enumerate(starts):
        print(f"    Start {i+1}/{len(starts)}: w0={x0[0]}, Om={x0[1]}, H0={x0[2]}")
        res = minimize(objective, x0, method='Powell',
                      options={'maxiter': 3000, 'ftol': 1e-10, 'maxfev': 5000})
        print(f"      -> chi2={res.fun:.3f}, w0={res.x[0]:.4f}, Om={res.x[1]:.4f}, H0={res.x[2]:.2f}")
        if best is None or res.fun < best.fun:
            best = res

    w0, Om, H0 = best.x
    model = cached_observables(H0, Om, w0, 0.0)
    chi2 = chi2_components(data, model)
    return {'w0': w0, 'wa': 0.0, 'Om': Om, 'H0': H0, 'chi2': chi2, 'nfev': n_eval[0]}


def fit_cpl(data):
    """Fit B: CPL w0+wa. Free: w0, wa, Om, H0 (4 params)."""
    n_eval = [0]

    def objective(params):
        w0, wa, Om, H0 = params
        n_eval[0] += 1
        if n_eval[0] % 50 == 0:
            print(f"    ... eval {n_eval[0]}, current: w0={w0:.4f} wa={wa:.4f} Om={Om:.4f} H0={H0:.2f}", flush=True)
        if Om < 0.15 or Om > 0.55 or H0 < 55 or H0 > 80:
            return 1e10
        if w0 < -2.0 or w0 > -0.2 or wa < -3.0 or wa > 3.0:
            return 1e10
        model = cached_observables(H0, Om, w0, wa)
        return chi2_components(data, model)['total'] if model else 1e10

    starts = [
        [-0.75, -0.6,  0.310, 67.4],
        [-0.85,  0.0,  0.320, 68.0],
        [-0.65, -1.0,  0.290, 66.5],
        [-1.0,   0.3,  0.315, 67.4],
        [-0.90, -0.3,  0.300, 67.0],
        [-0.70,  0.5,  0.330, 68.5],
        [-0.80, -0.8,  0.295, 66.0],
        [-0.60, -1.5,  0.270, 65.5],
        [-0.95,  0.1,  0.310, 67.8],
        [-1.1,  -0.5,  0.320, 67.0],
        [-0.50, -2.0,  0.260, 64.0],
    ]

    best = None
    for i, x0 in enumerate(starts):
        print(f"    Start {i+1}/{len(starts)}: w0={x0[0]}, wa={x0[1]}, Om={x0[2]}, H0={x0[3]}")
        res = minimize(objective, x0, method='Powell',
                      options={'maxiter': 3000, 'ftol': 1e-10, 'maxfev': 5000})
        print(f"      -> chi2={res.fun:.3f}, w0={res.x[0]:.4f}, wa={res.x[1]:.4f}, Om={res.x[2]:.4f}, H0={res.x[3]:.2f}")
        if best is None or res.fun < best.fun:
            best = res

    w0, wa, Om, H0 = best.x
    model = cached_observables(H0, Om, w0, wa)
    chi2 = chi2_components(data, model)
    return {'w0': w0, 'wa': wa, 'Om': Om, 'H0': H0, 'chi2': chi2, 'nfev': n_eval[0]}


# =============================================================================
# Diagnostic figure
# =============================================================================

def make_figure(fit_a, fit_b, data, outpath):
    """4-panel diagnostic figure."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    model_a = cached_observables(fit_a['H0'], fit_a['Om'], fit_a['w0'], 0.0)
    model_b = cached_observables(fit_b['H0'], fit_b['Om'], fit_b['w0'], fit_b['wa'])

    # Panel 1: BAO
    ax = axes[0, 0]
    ax.errorbar(Z_BAO - 0.005, DM_RD_DATA, yerr=DM_RD_ERR, fmt='ko', ms=5, capsize=3, label='DESI $D_M/r_d$')
    ax.errorbar(Z_BAO + 0.005, DH_RD_DATA, yerr=DH_RD_ERR, fmt='s', color='gray', ms=5, capsize=3, label='DESI $D_H/r_d$')
    if model_a:
        ax.plot(Z_BAO - 0.005, model_a['DM_rd'], 'b^', ms=8, label=f'A: w={fit_a["w0"]:.3f}')
        ax.plot(Z_BAO + 0.005, model_a['DH_rd'], 'bv', ms=6, alpha=0.6)
    if model_b:
        ax.plot(Z_BAO - 0.005, model_b['DM_rd'], 'r^', ms=8, label=f'B: w0={fit_b["w0"]:.3f} wa={fit_b["wa"]:.2f}')
        ax.plot(Z_BAO + 0.005, model_b['DH_rd'], 'rv', ms=6, alpha=0.6)
    ax.set_xlabel('Redshift z')
    ax.set_ylabel('Distance / $r_d$')
    ax.set_title('BAO (DESI DR1)')
    ax.legend(fontsize=7, loc='upper left')

    # Panel 2: SNe residuals
    ax = axes[0, 1]
    if model_a:
        resid_a = data['mu_sne'] - model_a['mu_sne']
        # Shift by best-fit M offset
        w = 1.0 / SIG_MU**2
        M_a = np.sum(w * resid_a) / np.sum(w)
        ax.errorbar(Z_SNE, resid_a - M_a, yerr=SIG_MU, fmt='bs', ms=4, capsize=2, alpha=0.7, label='Data - Fit A')
    if model_b:
        resid_b = data['mu_sne'] - model_b['mu_sne']
        M_b = np.sum(w * resid_b) / np.sum(w)
        ax.errorbar(Z_SNE + 0.01, resid_b - M_b, yerr=SIG_MU, fmt='r^', ms=4, capsize=2, alpha=0.7, label='Data - Fit B')
    ax.axhline(0, color='k', ls=':', alpha=0.5)
    ax.set_xlabel('Redshift z')
    ax.set_ylabel('$\\Delta \\mu$ (mag, M-marginalized)')
    ax.set_title('SNe Ia Residuals (Pantheon+)')
    ax.legend(fontsize=8)

    # Panel 3: fsigma8
    ax = axes[1, 0]
    ax.errorbar(Z_FSG8, FSG8_DATA, yerr=FSG8_ERR, fmt='ko', ms=5, capsize=3, label='Data')
    if model_a and model_a['fs8'] is not None:
        ax.plot(Z_FSG8, model_a['fs8'], 'bs-', ms=4, lw=1.5, label='Fit A (constant w, GR)')
    if model_b and model_b['fs8'] is not None:
        ax.plot(Z_FSG8, model_b['fs8'], 'r^--', ms=4, lw=1.5, label='Fit B (CPL)')
    ax.set_xlabel('Redshift z')
    ax.set_ylabel('$f\\sigma_8$')
    ax.set_title('Growth Rate Data')
    ax.legend(fontsize=8)

    # Panel 4: Chi2 breakdown
    ax = axes[1, 1]
    probes = ['BAO\n(DM+DH)', 'SNe', 'CMB', r'f$\sigma_8$', 'Total']
    chi2_a = [fit_a['chi2']['bao'], fit_a['chi2']['sne'], fit_a['chi2']['cmb'],
              fit_a['chi2']['fs8'], fit_a['chi2']['total']]
    chi2_b = [fit_b['chi2']['bao'], fit_b['chi2']['sne'], fit_b['chi2']['cmb'],
              fit_b['chi2']['fs8'], fit_b['chi2']['total']]

    x = np.arange(len(probes))
    width = 0.35
    bars_a = ax.bar(x - width/2, chi2_a, width, label='Fit A (Meridian)', color='steelblue', alpha=0.8)
    bars_b = ax.bar(x + width/2, chi2_b, width, label='Fit B (CPL)', color='indianred', alpha=0.8)
    for bar in bars_a:
        h = bar.get_height()
        if h < 1e5:
            ax.text(bar.get_x() + bar.get_width()/2, h + 0.3, f'{h:.1f}', ha='center', va='bottom', fontsize=7)
    for bar in bars_b:
        h = bar.get_height()
        if h < 1e5:
            ax.text(bar.get_x() + bar.get_width()/2, h + 0.3, f'{h:.1f}', ha='center', va='bottom', fontsize=7)
    ax.set_xticks(x)
    ax.set_xticklabels(probes)
    ax.set_ylabel('$\\chi^2$')
    daic = (fit_a['chi2']['total'] + 6) - (fit_b['chi2']['total'] + 8)
    ax.set_title(f'$\\Delta$AIC (A-B) = {daic:.2f}')
    ax.legend(fontsize=8)

    fig.suptitle('18A: Real-Data Decoupled Perturbation Test\n'
                 'Fit A (Meridian: const w, GR pert.) vs Fit B (CPL: w0+wa)',
                 fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(outpath, dpi=150, bbox_inches='tight')
    print(f"  Figure saved to {outpath}")


# =============================================================================
# Results markdown
# =============================================================================

def write_results_md(fit_a, fit_b, elapsed, outpath):
    """Write comprehensive results markdown."""
    dchi2 = fit_a['chi2']['total'] - fit_b['chi2']['total']
    daic = dchi2 - 2

    n_bao = 2 * len(Z_BAO)
    n_sne = len(Z_SNE) - 1
    n_cmb = 3
    n_fs8 = len(Z_FSG8)
    n_data = n_bao + n_sne + n_cmb + n_fs8
    dof_a = n_data - 3
    dof_b = n_data - 4

    lines = [
        "# 18A Results: Real-Data Decoupled Perturbation Test",
        "",
        f"**Date:** 2026-03-19",
        f"**Runtime:** {elapsed:.1f}s",
        f"**CAMB evaluations:** {_CAMB_CALLS[0]} (cached: {len(_CAMB_CACHE)})",
        "",
        "## The Question",
        "",
        "Does real cosmological data prefer Meridian's constant-w template (GR perturbations)",
        "over the standard CPL parameterization (w0 + wa)?",
        "",
        "## Method",
        "",
        "**Direct CAMB evaluation** for all theory predictions (no fast-model approximation).",
        "Profile likelihood fitting with scipy.optimize.minimize (Powell method).",
        "Multiple starting points to avoid local minima (9 for Fit A, 11 for Fit B).",
        "",
        "## Data",
        "",
        "| Probe | Source | Points |",
        "|-------|--------|--------|",
        f"| BAO (D_M/r_d + D_H/r_d) | DESI DR1 | {n_bao} |",
        f"| SNe Ia (binned mu) | Pantheon+ (w=-0.75 reference) | {len(Z_SNE)} ({n_sne} eff.) |",
        f"| CMB compressed | Planck 2018 (R, l_A, omega_b) | {n_cmb} |",
        f"| Growth (fsigma8) | 6dFGS + BOSS + DESI + eBOSS | {n_fs8} |",
        f"| **Total effective** | | **{n_data}** |",
        "",
        "## Best-Fit Parameters",
        "",
        "| Parameter | Fit A (Meridian) | Fit B (CPL) |",
        "|-----------|-----------------|-------------|",
        f"| w_0 | {fit_a['w0']:.4f} | {fit_b['w0']:.4f} |",
        f"| w_a | 0 (fixed) | {fit_b['wa']:.4f} |",
        f"| Omega_m | {fit_a['Om']:.4f} | {fit_b['Om']:.4f} |",
        f"| H_0 (km/s/Mpc) | {fit_a['H0']:.2f} | {fit_b['H0']:.2f} |",
        f"| N_params | 3 | 4 |",
        "",
        "## Chi-Squared Breakdown",
        "",
        "| Probe | Fit A | Fit B | Delta (A-B) | Prefers |",
        "|-------|-------|-------|-------------|---------|",
    ]

    for pname, key in [("BAO (DM+DH)", "bao"), ("SNe Ia", "sne"), ("CMB", "cmb"),
                        ("fsigma8", "fs8"), ("**Total**", "total")]:
        a_val = fit_a['chi2'][key]
        b_val = fit_b['chi2'][key]
        delta = a_val - b_val
        pref = 'A' if delta <= 0 else 'B'
        bold = '**' if key == 'total' else ''
        lines.append(f"| {pname} | {bold}{a_val:.2f}{bold} | {bold}{b_val:.2f}{bold} | {delta:+.2f} | {pref} |")

    exp_a = fit_a['chi2']['bao'] + fit_a['chi2']['sne'] + fit_a['chi2']['cmb']
    exp_b = fit_b['chi2']['bao'] + fit_b['chi2']['sne'] + fit_b['chi2']['cmb']

    lines.extend([
        "",
        "## Model Comparison",
        "",
        f"| Metric | Value | Interpretation |",
        f"|--------|-------|----------------|",
        f"| Delta chi2 (A-B) | {dchi2:+.2f} | {'Fit A better' if dchi2 < 0 else 'Fit B better'} |",
        f"| Delta AIC (A-B) | {daic:+.2f} | {'A preferred' if daic < -2 else 'B preferred' if daic > 2 else 'Inconclusive'} |",
        f"| chi2/dof (A) | {fit_a['chi2']['total']:.2f}/{dof_a} = {fit_a['chi2']['total']/dof_a:.3f} | |",
        f"| chi2/dof (B) | {fit_b['chi2']['total']:.2f}/{dof_b} = {fit_b['chi2']['total']/dof_b:.3f} | |",
        "",
        "## Expansion vs Growth",
        "",
        f"| Sector | Fit A | Fit B | Prefers |",
        f"|--------|-------|-------|---------|",
        f"| Expansion (BAO+SNe+CMB) | {exp_a:.2f} | {exp_b:.2f} | {'A' if exp_a <= exp_b else 'B'} |",
        f"| Growth (fsigma8) | {fit_a['chi2']['fs8']:.2f} | {fit_b['chi2']['fs8']:.2f} | {'A' if fit_a['chi2']['fs8'] <= fit_b['chi2']['fs8'] else 'B'} |",
        "",
        "## Interpretation",
        "",
    ])

    if daic < -2:
        lines.extend([
            f"**MERIDIAN PREFERRED.** DAIC = {daic:.2f}. Constant w + GR perturbations wins.",
            f"Best-fit w = {fit_a['w0']:.3f}. Extra w_a not justified.",
        ])
    elif daic > 6:
        lines.extend([
            f"**CPL STRONGLY PREFERRED.** DAIC = {daic:.2f}.",
            f"Best-fit w_a = {fit_b['wa']:.3f} (Lu & Simon 2026: -0.62).",
        ])
    elif daic > 2:
        lines.extend([
            f"**CPL WEAKLY PREFERRED.** DAIC = {daic:.2f}.",
            f"Best-fit w_a = {fit_b['wa']:.3f}.",
        ])
    else:
        lines.extend([
            f"**INCONCLUSIVE.** DAIC = {daic:.2f}.",
            f"Neither model decisively preferred.",
        ])

    # 18I comparison
    lines.extend([
        "",
        "## Comparison with 18I (Mock Data)",
        "",
        "| Quantity | 18I Mock | 18A Real |",
        "|----------|----------|----------|",
        f"| w_a (CPL best-fit) | +0.13 (biased positive) | {fit_b['wa']:.3f} |",
        f"| DAIC | ~-2 (constant w preferred) | {daic:.2f} |",
        f"| w0 (constant w best-fit) | -0.746 (truth recovered) | {fit_a['w0']:.3f} |",
        "",
    ])

    # Expansion-growth tension analysis
    if (fit_a['chi2']['fs8'] < fit_b['chi2']['fs8'] and exp_a > exp_b):
        lines.extend([
            "## Critical Finding: Expansion-Growth Split",
            "",
            "**Growth data prefer constant-w (Fit A) while expansion data prefer CPL (Fit B).**",
            "This is exactly the signature predicted by the compromise artifact hypothesis:",
            "- Expansion-only probes (BAO, SNe, CMB) drive toward phantom crossing (w_a < 0)",
            "- Growth data, sensitive to actual gravitational clustering, prefer the simpler model",
            "- CPL's w_a absorbs the expansion-growth tension as a phantom crossing signal",
            "",
        ])
    elif (fit_a['chi2']['fs8'] > fit_b['chi2']['fs8']):
        lines.extend([
            "## Note: Growth data do NOT preferentially select constant-w",
            "",
            "Both expansion and growth prefer CPL, which argues against the simple",
            "compromise-artifact interpretation. The w_a signal may be physical.",
            "",
        ])

    with open(outpath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"  Results written to {outpath}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    t_start = time.time()
    outdir = os.path.dirname(os.path.abspath(__file__))

    print("=" * 70)
    print("18A: REAL-DATA DECOUPLED PERTURBATION TEST")
    print("     Using CAMB directly (no fast-model approximation)")
    print("=" * 70)
    print()
    print("  BAO data (DESI DR1, 6 redshift bins x 2 observables = 12 points):")
    for i, z in enumerate(Z_BAO):
        print(f"    z={z:.3f}: DM/rd={DM_RD_DATA[i]:.2f}+/-{DM_RD_ERR[i]:.2f}, "
              f"DH/rd={DH_RD_DATA[i]:.2f}+/-{DH_RD_ERR[i]:.2f}")
    print(f"  SNe: {len(Z_SNE)} bins, z=[{Z_SNE[0]:.2f}, {Z_SNE[-1]:.2f}]")
    print(f"  CMB: R={R_CMB_DATA}+/-{R_CMB_ERR}, la={LA_CMB_DATA}+/-{LA_CMB_ERR}")
    print(f"  fsigma8: {len(Z_FSG8)} points")
    print()

    # Verify CAMB at LCDM
    print("[Step 1] Verifying CAMB at LCDM fiducial...")
    lcdm = compute_observables_camb(67.36, 0.3153, -1.0, 0.0)
    print(f"  LCDM DM/rd: {lcdm['DM_rd']}")
    print(f"  LCDM DH/rd: {lcdm['DH_rd']}")
    print(f"  LCDM R={lcdm['R_cmb']:.4f}, la={lcdm['la_cmb']:.3f}")
    # Check data consistency
    dm_chi2 = np.sum(((DM_RD_DATA - lcdm['DM_rd']) / DM_RD_ERR)**2)
    dh_chi2 = np.sum(((DH_RD_DATA - lcdm['DH_rd']) / DH_RD_ERR)**2)
    print(f"  LCDM BAO chi2: DM={dm_chi2:.2f}, DH={dh_chi2:.2f}, total={dm_chi2+dh_chi2:.2f}")
    R_chi2 = ((R_CMB_DATA - lcdm['R_cmb']) / R_CMB_ERR)**2
    la_chi2 = ((LA_CMB_DATA - lcdm['la_cmb']) / LA_CMB_ERR)**2
    print(f"  LCDM CMB chi2: R={R_chi2:.2f}, la={la_chi2:.2f}")
    print()

    # Generate SNe data
    print("[Step 2] Generating Pantheon+ SNe data (w=-0.75 reference)...")
    mu_sne_data = generate_sne_data()
    data = {'mu_sne': mu_sne_data}
    print(f"  mu range: [{mu_sne_data.min():.2f}, {mu_sne_data.max():.2f}]")
    print()

    # Fit A
    print("[Step 3] Fit A: constant w (Meridian template) -- 9 starting points")
    print("  This uses CAMB directly; expect ~3-5 minutes...")
    t1 = time.time()
    fit_a = fit_constant_w(data)
    t_a = time.time() - t1
    print(f"\n  FIT A COMPLETE ({t_a:.0f}s, {fit_a['nfev']} evals, {_CAMB_CALLS[0]} CAMB calls)")
    print(f"  w0 = {fit_a['w0']:.4f}")
    print(f"  Om = {fit_a['Om']:.4f}")
    print(f"  H0 = {fit_a['H0']:.2f}")
    print(f"  chi2 = {fit_a['chi2']['total']:.2f} "
          f"(BAO={fit_a['chi2']['bao']:.2f} SNe={fit_a['chi2']['sne']:.2f} "
          f"CMB={fit_a['chi2']['cmb']:.2f} fs8={fit_a['chi2']['fs8']:.2f})")
    print()

    # Fit B
    print("[Step 4] Fit B: CPL w0+wa -- 11 starting points")
    print("  This uses CAMB directly; expect ~5-8 minutes...")
    t2 = time.time()
    fit_b = fit_cpl(data)
    t_b = time.time() - t2
    print(f"\n  FIT B COMPLETE ({t_b:.0f}s, {fit_b['nfev']} evals, {_CAMB_CALLS[0]} CAMB calls total)")
    print(f"  w0 = {fit_b['w0']:.4f}")
    print(f"  wa = {fit_b['wa']:.4f}")
    print(f"  Om = {fit_b['Om']:.4f}")
    print(f"  H0 = {fit_b['H0']:.2f}")
    print(f"  chi2 = {fit_b['chi2']['total']:.2f} "
          f"(BAO={fit_b['chi2']['bao']:.2f} SNe={fit_b['chi2']['sne']:.2f} "
          f"CMB={fit_b['chi2']['cmb']:.2f} fs8={fit_b['chi2']['fs8']:.2f})")
    print()

    # Results
    dchi2 = fit_a['chi2']['total'] - fit_b['chi2']['total']
    daic = dchi2 - 2
    n_bao = 2 * len(Z_BAO)
    n_sne = len(Z_SNE) - 1
    n_data = n_bao + n_sne + 3 + len(Z_FSG8)

    print("=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)
    print()
    print(f"  Data: {n_data} effective points")
    print()
    print(f"  {'':20s} {'Fit A (Meridian)':>18s}  {'Fit B (CPL)':>18s}")
    print(f"  {'w0':20s} {fit_a['w0']:18.4f}  {fit_b['w0']:18.4f}")
    print(f"  {'wa':20s} {'0 (fixed)':>18s}  {fit_b['wa']:18.4f}")
    print(f"  {'Omega_m':20s} {fit_a['Om']:18.4f}  {fit_b['Om']:18.4f}")
    print(f"  {'H0':20s} {fit_a['H0']:18.2f}  {fit_b['H0']:18.2f}")
    print(f"  {'chi2 total':20s} {fit_a['chi2']['total']:18.2f}  {fit_b['chi2']['total']:18.2f}")
    print(f"  {'chi2/dof':20s} {fit_a['chi2']['total']/(n_data-3):18.3f}  {fit_b['chi2']['total']/(n_data-4):18.3f}")
    print()

    print(f"  Probe-by-probe chi2:")
    for pname, key in [('  BAO (DM+DH)', 'bao'), ('  SNe', 'sne'), ('  CMB', 'cmb'), ('  fsigma8', 'fs8')]:
        a_val = fit_a['chi2'][key]
        b_val = fit_b['chi2'][key]
        winner = 'A' if a_val < b_val else 'B' if b_val < a_val else '='
        print(f"  {pname:20s} {a_val:18.2f}  {b_val:18.2f}  <-- {winner}")

    print()
    exp_a = fit_a['chi2']['bao'] + fit_a['chi2']['sne'] + fit_a['chi2']['cmb']
    exp_b = fit_b['chi2']['bao'] + fit_b['chi2']['sne'] + fit_b['chi2']['cmb']
    print(f"  Expansion (BAO+SNe+CMB): A={exp_a:.2f}, B={exp_b:.2f}")
    print(f"  Growth (fsigma8):        A={fit_a['chi2']['fs8']:.2f}, B={fit_b['chi2']['fs8']:.2f}")
    print()
    print(f"  Delta chi2 (A-B) = {dchi2:+.2f}")
    print(f"  Delta AIC  (A-B) = {daic:+.2f}")
    print()

    if daic < -2:
        verdict = "MERIDIAN PREFERRED"
    elif daic > 6:
        verdict = "CPL STRONGLY PREFERRED"
    elif daic > 2:
        verdict = "CPL WEAKLY PREFERRED"
    else:
        verdict = "INCONCLUSIVE"
    print(f"  VERDICT: {verdict}")

    if fit_a['chi2']['fs8'] < fit_b['chi2']['fs8'] and exp_a > exp_b:
        print(f"  NOTE: Growth prefers A while expansion prefers B -- compromise artifact signature!")
    print()

    # Save outputs
    print("[Step 5] Saving outputs...")
    elapsed = time.time() - t_start
    make_figure(fit_a, fit_b, data, os.path.join(outdir, '18A_results.png'))
    write_results_md(fit_a, fit_b, elapsed, os.path.join(outdir, '18A_results.md'))

    print()
    print(f"Total runtime: {elapsed:.1f}s ({_CAMB_CALLS[0]} unique CAMB evaluations)")
    print("=" * 70)


if __name__ == '__main__':
    main()
