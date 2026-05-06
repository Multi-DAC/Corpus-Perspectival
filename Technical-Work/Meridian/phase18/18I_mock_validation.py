#!/usr/bin/env python3
"""
18I -- Mock-Data Validation of the Decoupled Perturbation Test

Generates mock cosmological data from a Meridian-truth universe (constant w, GR perturbations)
and fits with both the correct model (constant w) and a CPL model (w0 + wa*z/(1+z)) to test
whether CPL analysis manufactures phantom crossing as a compromise artifact.

Strategy:
  - Use CAMB for truth-model observables
  - Build CAMB-calibrated fast forward models for fitting (Gauss-Legendre quadrature)
  - Pre-compute fsigma8 grids via CAMB, interpolate during fitting
  - Fit 200 realizations with scipy.optimize.minimize (Powell)
  - Analyze whether CPL produces spurious w_a < 0

Author: Clawd (Phase 18I, Project Meridian)
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
from scipy.interpolate import RegularGridInterpolator
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time
import os

# =============================================================================
# CONSTANTS
# =============================================================================
C_KM_S = 299792.458  # speed of light in km/s

# Meridian truth cosmology
H0_TRUE = 67.36
OMBH2_TRUE = 0.02237
OMCH2_TRUE = 0.1200
TAU_TRUE = 0.0544
NS_TRUE = 0.9649
AS_TRUE = 2.1e-9
W0_TRUE = -0.746   # Meridian JC benchmark
WA_TRUE = 0.0       # constant w -- the whole point

# Derived
H0_100 = H0_TRUE / 100.0
OM_TRUE = (OMBH2_TRUE + OMCH2_TRUE) / H0_100**2  # total matter

# Survey redshifts
Z_BAO = np.array([0.30, 0.51, 0.70, 0.93, 1.32, 1.49, 2.33])
Z_SNE = np.linspace(0.01, 1.5, 20)
Z_FSG8 = np.array([0.15, 0.38, 0.51, 0.70, 0.85, 1.48])
Z_STAR = 1089.92

N_REALIZATIONS = 200

# Gauss-Legendre nodes (64-point for high accuracy, vectorized)
_GL_N = 64
_GL_X, _GL_W = np.polynomial.legendre.leggauss(_GL_N)

# =============================================================================
# CAMB-based truth computation
# =============================================================================

def get_camb_observables(H0, ombh2, omch2, w0, wa, de_model='fluid'):
    """Compute all observables from CAMB."""
    pars = camb.CAMBparams()
    pars.set_cosmology(H0=H0, ombh2=ombh2, omch2=omch2, tau=TAU_TRUE)
    pars.InitPower.set_params(ns=NS_TRUE, As=AS_TRUE)
    pars.set_dark_energy(w=w0, wa=wa, dark_energy_model=de_model)

    all_z = sorted(set(list(Z_FSG8) + [0.0]))
    pars.set_matter_power(redshifts=all_z, kmax=2.0)
    pars.WantTransfer = True

    results = camb.get_results(pars)
    derived = results.get_derived_params()

    rd = derived['rdrag']
    rs_star = derived['rstar']
    zstar = derived['zstar']

    DM_bao = np.array([results.comoving_radial_distance(z) for z in Z_BAO])
    DH_bao = np.array([C_KM_S / results.hubble_parameter(z) for z in Z_BAO])

    DL_sne = np.array([results.luminosity_distance(z) for z in Z_SNE])
    mu_sne = 5.0 * np.log10(DL_sne) + 25.0

    all_z_rev = sorted(all_z, reverse=True)
    fsigma8 = results.get_fsigma8()
    fs8_dict = dict(zip(all_z_rev, fsigma8))
    fs8_vals = np.array([fs8_dict[z] for z in Z_FSG8])

    DM_star = results.comoving_radial_distance(zstar)
    Om = (ombh2 + omch2) / (H0 / 100)**2
    R_cmb = np.sqrt(Om * H0**2) * DM_star / C_KM_S
    la_cmb = np.pi * DM_star / rs_star

    return {
        'DM_rd': DM_bao / rd, 'DH_rd': DH_bao / rd,
        'mu_sne': mu_sne,
        'fs8': fs8_vals,
        'R_cmb': R_cmb, 'la_cmb': la_cmb, 'ob_cmb': ombh2,
        'rd': rd, 'rs_star': rs_star, 'zstar': zstar,
    }


# =============================================================================
# Fast forward model (Gauss-Legendre, vectorized, no scipy.integrate)
# =============================================================================

def _E_z_vec(z, Om, w0, wa):
    """Vectorized E(z) = H(z)/H0 for flat wCDM/CPL. z can be array."""
    z = np.asarray(z, dtype=np.float64)
    a = 1.0 / (1.0 + z)
    Ode = 1.0 - Om
    Or = 4.153e-5 / H0_100**2  # radiation density (fixed by T_CMB)

    if abs(wa) < 1e-12:
        de_factor = a**(-3.0 * (1.0 + w0))
    else:
        de_factor = a**(-3.0 * (1.0 + w0 + wa)) * np.exp(-3.0 * wa * (1.0 - a))

    E2 = Om * (1 + z)**3 + Or * (1 + z)**4 + Ode * de_factor
    return np.sqrt(np.maximum(E2, 1e-30))


def _comoving_dist_GL(z_arr, H0, Om, w0, wa):
    """
    Comoving distance D_M(z) in Mpc for an array of redshifts.
    Uses fixed 64-point Gauss-Legendre quadrature. Fully vectorized.
    """
    z_arr = np.asarray(z_arr, dtype=np.float64)
    n_z = len(z_arr)

    # Transform GL nodes from [-1,1] to [0, z_i] for each z_i
    # z' = z_i/2 * (x + 1), dz' = z_i/2 * dx
    # integral_0^z_i 1/E(z') dz' = sum_j w_j * z_i/2 * 1/E(z_i/2*(x_j+1))
    half_z = z_arr / 2.0  # shape (n_z,)

    # GL nodes mapped to integration variable: shape (n_z, n_GL)
    z_eval = half_z[:, None] * (_GL_X[None, :] + 1.0)  # (n_z, 64)

    # Evaluate 1/E at all points
    inv_E = 1.0 / _E_z_vec(z_eval.ravel(), Om, w0, wa)  # (n_z * 64,)
    inv_E = inv_E.reshape(n_z, _GL_N)  # (n_z, 64)

    # Quadrature
    integrals = np.sum(_GL_W[None, :] * inv_E, axis=1) * half_z  # (n_z,)

    return C_KM_S / H0 * integrals


# Calibration offsets (computed once against CAMB truth)
_CALIB = {}


def calibrate_fast_model(camb_truth):
    """
    Compute offsets between fast analytic model and CAMB truth at truth cosmology.
    These offsets are applied during fitting to eliminate systematic bias.
    """
    global _CALIB

    # Fast model at truth
    DM_bao_fast = _comoving_dist_GL(Z_BAO, H0_TRUE, OM_TRUE, W0_TRUE, 0.0)
    DH_bao_fast = C_KM_S / (H0_TRUE * _E_z_vec(Z_BAO, OM_TRUE, W0_TRUE, 0.0))
    rd_fast = _sound_horizon_EH98(OMBH2_TRUE, OMCH2_TRUE)

    DM_rd_fast = DM_bao_fast / rd_fast
    DH_rd_fast = DH_bao_fast / rd_fast

    DL_sne_fast = _comoving_dist_GL(Z_SNE, H0_TRUE, OM_TRUE, W0_TRUE, 0.0) * (1 + Z_SNE)
    mu_sne_fast = 5.0 * np.log10(np.maximum(DL_sne_fast, 1e-10)) + 25.0

    zstar_fast = _zstar_HS96(OMBH2_TRUE, OMCH2_TRUE)
    rs_star_fast = rd_fast * 0.9819
    DM_star_fast = _comoving_dist_GL(np.array([zstar_fast]), H0_TRUE, OM_TRUE, W0_TRUE, 0.0)[0]
    R_fast = np.sqrt(OM_TRUE * H0_TRUE**2) * DM_star_fast / C_KM_S
    la_fast = np.pi * DM_star_fast / rs_star_fast

    # Multiplicative calibration factors: CAMB_value = factor * fast_value
    _CALIB['DM_rd_factor'] = camb_truth['DM_rd'] / DM_rd_fast
    _CALIB['DH_rd_factor'] = camb_truth['DH_rd'] / DH_rd_fast
    _CALIB['mu_offset'] = camb_truth['mu_sne'] - mu_sne_fast  # additive for magnitudes
    _CALIB['R_factor'] = camb_truth['R_cmb'] / R_fast
    _CALIB['la_factor'] = camb_truth['la_cmb'] / la_fast
    _CALIB['rd_factor'] = camb_truth['rd'] / rd_fast
    _CALIB['zstar'] = camb_truth['zstar']
    _CALIB['rs_star'] = camb_truth['rs_star']

    print(f"  Calibration factors:")
    print(f"    DM/rd: {_CALIB['DM_rd_factor']}")
    print(f"    DH/rd: {_CALIB['DH_rd_factor']}")
    print(f"    mu offset range: [{np.min(_CALIB['mu_offset']):.5f}, {np.max(_CALIB['mu_offset']):.5f}]")
    print(f"    R factor: {_CALIB['R_factor']:.6f}")
    print(f"    la factor: {_CALIB['la_factor']:.6f}")


def _sound_horizon_EH98(ombh2, omch2):
    """Eisenstein & Hu 1998 fitting formula for sound horizon at drag epoch."""
    omh2 = ombh2 + omch2
    return 44.5 * np.log(9.83 / omh2) / np.sqrt(1 + 10 * ombh2**0.75)


def _zstar_HS96(ombh2, omch2):
    """Hu & Sugiyama 1996 fitting formula for recombination redshift."""
    omh2 = ombh2 + omch2
    g1 = 0.0783 * ombh2**(-0.238) / (1 + 39.5 * ombh2**0.763)
    g2 = 0.560 / (1 + 21.1 * ombh2**1.81)
    return 1048 * (1 + 0.00124 * ombh2**(-0.738)) * (1 + g1 * omh2**g2)


def fast_observables(H0, Om, w0, wa, fs8_interp):
    """
    Fast forward model calibrated against CAMB truth.
    Returns dict of observables or None if unphysical.
    """
    h = H0 / 100.0
    omch2 = Om * h**2 - OMBH2_TRUE
    if omch2 < 0.01 or omch2 > 0.25:
        return None
    if Om < 0.05 or Om > 0.7:
        return None

    # BAO distances
    DM_bao = _comoving_dist_GL(Z_BAO, H0, Om, w0, wa)
    DH_bao = C_KM_S / (H0 * _E_z_vec(Z_BAO, Om, w0, wa))
    rd = _sound_horizon_EH98(OMBH2_TRUE, omch2)
    DM_rd = (DM_bao / rd) * _CALIB['DM_rd_factor']
    DH_rd = (DH_bao / rd) * _CALIB['DH_rd_factor']

    # SNe distance moduli
    DL_sne = _comoving_dist_GL(Z_SNE, H0, Om, w0, wa) * (1 + Z_SNE)
    mu_sne = 5.0 * np.log10(np.maximum(DL_sne, 1e-10)) + 25.0 + _CALIB['mu_offset']

    # fσ8 from interpolation
    if fs8_interp is not None:
        fs8 = fs8_interp(Om, w0, wa)
    else:
        fs8 = None

    # CMB compressed parameters
    # Use CAMB's zstar (fixed) — the dominant sensitivity is through DM(z*)
    zstar = _CALIB['zstar']
    DM_star = _comoving_dist_GL(np.array([zstar]), H0, Om, w0, wa)[0]
    # Use ratio-based calibration for R and l_a
    rd_truth = rd * _CALIB['rd_factor']
    rs_star_approx = rd_truth * (_CALIB['rs_star'] / _CALIB.get('rd_truth', _CALIB['rs_star']))

    R_cmb = np.sqrt(Om * H0**2) * DM_star / C_KM_S * _CALIB['R_factor']
    # For la, use the ratio to the truth
    la_cmb = np.pi * DM_star / _CALIB['rs_star'] * _CALIB['la_factor']
    # Actually simpler: just compute relative to truth reference
    # la = pi * DM(z*) / r_s(z*). The r_s(z*) is nearly fixed if ombh2 is fixed.
    # So la scales as DM(z*), and R scales as sqrt(Om)*H0*DM(z*).

    return {
        'DM_rd': DM_rd, 'DH_rd': DH_rd,
        'mu_sne': mu_sne,
        'fs8': fs8,
        'R_cmb': R_cmb, 'la_cmb': la_cmb, 'ob_cmb': OMBH2_TRUE,
    }


# =============================================================================
# fsigma8 interpolation grid
# =============================================================================

def build_fsigma8_grid(de_model='fluid', verbose=True):
    """Build interpolation grid for fsigma8 using CAMB."""
    Om_grid = np.linspace(0.25, 0.38, 7)
    w0_grid = np.linspace(-1.1, -0.5, 7)

    if de_model == 'ppf':
        wa_grid = np.linspace(-1.5, 0.8, 7)
    else:
        wa_grid = np.array([0.0])

    n_om, n_w0, n_wa = len(Om_grid), len(w0_grid), len(wa_grid)
    n_z = len(Z_FSG8)
    fs8_grid = np.full((n_om, n_w0, n_wa, n_z), np.nan)

    all_z_sorted = sorted(set(list(Z_FSG8) + [0.0]))
    all_z_rev = sorted(all_z_sorted, reverse=True)

    total = n_om * n_w0 * n_wa
    count = 0

    for i, Om in enumerate(Om_grid):
        for j, w0 in enumerate(w0_grid):
            for k, wa in enumerate(wa_grid):
                count += 1
                h = H0_TRUE / 100
                omch2 = Om * h**2 - OMBH2_TRUE
                if omch2 < 0.01:
                    continue

                try:
                    pars = camb.CAMBparams()
                    pars.set_cosmology(H0=H0_TRUE, ombh2=OMBH2_TRUE, omch2=omch2, tau=TAU_TRUE)
                    pars.InitPower.set_params(ns=NS_TRUE, As=AS_TRUE)

                    use_model = de_model
                    # fluid can't cross -1
                    if de_model == 'fluid' and abs(wa) > 1e-10:
                        if (w0 < -1 and w0 + wa > -1) or (w0 > -1 and w0 + wa < -1):
                            use_model = 'ppf'

                    pars.set_dark_energy(w=w0, wa=wa, dark_energy_model=use_model)
                    pars.set_matter_power(redshifts=all_z_sorted, kmax=2.0)
                    pars.WantTransfer = True
                    results = camb.get_results(pars)
                    fsigma8 = results.get_fsigma8()
                    fs8_dict = dict(zip(all_z_rev, fsigma8))
                    fs8_grid[i, j, k, :] = [fs8_dict[z] for z in Z_FSG8]
                except:
                    pass

        if verbose:
            print(f"    Grid row {i+1}/{n_om} done ({count}/{total} evaluations)", flush=True)

    # Fill NaNs with nearest valid value
    for iz in range(n_z):
        arr = fs8_grid[:, :, :, iz]
        mask = np.isnan(arr)
        if mask.any() and not mask.all():
            arr[mask] = np.nanmean(arr)
            fs8_grid[:, :, :, iz] = arr

    return Om_grid, w0_grid, wa_grid, fs8_grid


class FSigma8Interpolator:
    """Fast interpolator for fsigma8."""

    def __init__(self, Om_grid, w0_grid, wa_grid, fs8_grid):
        self.n_z = fs8_grid.shape[-1]
        self.Om_range = (Om_grid[0], Om_grid[-1])
        self.w0_range = (w0_grid[0], w0_grid[-1])
        self.wa_range = (wa_grid[0], wa_grid[-1])
        self.constant_w = (len(wa_grid) == 1)
        self.interpolators = []

        for iz in range(self.n_z):
            if self.constant_w:
                interp = RegularGridInterpolator(
                    (Om_grid, w0_grid), fs8_grid[:, :, 0, iz],
                    method='linear', bounds_error=False, fill_value=None)
            else:
                interp = RegularGridInterpolator(
                    (Om_grid, w0_grid, wa_grid), fs8_grid[:, :, :, iz],
                    method='linear', bounds_error=False, fill_value=None)
            self.interpolators.append(interp)

    def __call__(self, Om, w0, wa=0.0):
        Om_c = np.clip(Om, *self.Om_range)
        w0_c = np.clip(w0, *self.w0_range)
        result = np.zeros(self.n_z)
        for iz in range(self.n_z):
            if self.constant_w:
                result[iz] = float(self.interpolators[iz]((Om_c, w0_c)))
            else:
                wa_c = np.clip(wa, *self.wa_range)
                result[iz] = float(self.interpolators[iz]((Om_c, w0_c, wa_c)))
        return result


# =============================================================================
# Mock data generation
# =============================================================================

def generate_uncertainties():
    """Realistic survey uncertainties."""
    return {
        'sig_DM_frac': np.array([0.015, 0.012, 0.015, 0.020, 0.025, 0.028, 0.030]),
        'sig_DH_frac': np.array([0.025, 0.020, 0.025, 0.035, 0.040, 0.045, 0.050]),
        'sig_mu': 0.01 + 0.04 * (Z_SNE / 1.5)**0.5,
        'sig_fs8_frac': np.array([0.12, 0.08, 0.06, 0.07, 0.10, 0.15]),
        'sig_R': 0.006,
        'sig_la': 0.1,
        'sig_ob': 0.00015,
    }


def generate_mock_data(truth, unc, rng):
    """One mock dataset: truth + Gaussian noise."""
    sig_DM = truth['DM_rd'] * unc['sig_DM_frac']
    sig_DH = truth['DH_rd'] * unc['sig_DH_frac']
    sig_fs8 = truth['fs8'] * unc['sig_fs8_frac']

    return {
        'DM_rd': truth['DM_rd'] + rng.normal(0, sig_DM),
        'DH_rd': truth['DH_rd'] + rng.normal(0, sig_DH),
        'sig_DM': sig_DM, 'sig_DH': sig_DH,
        'mu_sne': truth['mu_sne'] + rng.normal(0, unc['sig_mu']),
        'sig_mu': unc['sig_mu'],
        'fs8': truth['fs8'] + rng.normal(0, sig_fs8),
        'sig_fs8': sig_fs8,
        'R_cmb': truth['R_cmb'] + rng.normal(0, unc['sig_R']),
        'la_cmb': truth['la_cmb'] + rng.normal(0, unc['sig_la']),
        'ob_cmb': truth['ob_cmb'] + rng.normal(0, unc['sig_ob']),
        'sig_R': unc['sig_R'], 'sig_la': unc['sig_la'], 'sig_ob': unc['sig_ob'],
    }


# =============================================================================
# Chi-squared computation
# =============================================================================

def chi2_components(obs, model):
    """Chi-squared split by probe."""
    if model is None:
        return {'total': 1e10, 'bao': 1e10, 'sne': 1e10, 'fs8': 1e10, 'cmb': 1e10}

    # BAO
    chi2_bao = np.sum(((obs['DM_rd'] - model['DM_rd']) / obs['sig_DM'])**2)
    chi2_bao += np.sum(((obs['DH_rd'] - model['DH_rd']) / obs['sig_DH'])**2)

    # SNe with analytic marginalization over absolute magnitude M
    delta_mu = obs['mu_sne'] - model['mu_sne']
    w = 1.0 / obs['sig_mu']**2
    A = np.sum(w * delta_mu)
    B = np.sum(w)
    C_val = np.sum(w * delta_mu**2)
    chi2_sne = C_val - A**2 / B

    # fsigma8
    chi2_fs8 = 0.0
    if model['fs8'] is not None:
        chi2_fs8 = np.sum(((obs['fs8'] - model['fs8']) / obs['sig_fs8'])**2)

    # CMB compressed
    chi2_cmb = ((obs['R_cmb'] - model['R_cmb']) / obs['sig_R'])**2
    chi2_cmb += ((obs['la_cmb'] - model['la_cmb']) / obs['sig_la'])**2
    chi2_cmb += ((obs['ob_cmb'] - model['ob_cmb']) / obs['sig_ob'])**2

    return {
        'total': chi2_bao + chi2_sne + chi2_fs8 + chi2_cmb,
        'bao': chi2_bao, 'sne': chi2_sne, 'fs8': chi2_fs8, 'cmb': chi2_cmb,
    }


# =============================================================================
# Fitting
# =============================================================================

def fit_constant_w(obs, fs8_interp):
    """Fit A: constant w. Free: w0, Om, H0."""
    def objective(params):
        w0, Om, H0 = params
        if Om < 0.15 or Om > 0.55 or H0 < 58 or H0 > 78 or w0 < -1.8 or w0 > -0.3:
            return 1e10
        try:
            model = fast_observables(H0, Om, w0, 0.0, fs8_interp)
            return chi2_components(obs, model)['total'] if model else 1e10
        except:
            return 1e10

    best = None
    for x0 in [
        [W0_TRUE, OM_TRUE, H0_TRUE],
        [-0.85, 0.30, 68.0],
        [-0.65, 0.33, 67.0],
    ]:
        res = minimize(objective, x0, method='Powell',
                      options={'maxiter': 2000, 'ftol': 1e-8, 'maxfev': 5000})
        if best is None or res.fun < best.fun:
            best = res

    w0, Om, H0 = best.x
    model = fast_observables(H0, Om, w0, 0.0, fs8_interp)
    chi2 = chi2_components(obs, model)
    return {'w0': w0, 'wa': 0.0, 'Om': Om, 'H0': H0, 'chi2': chi2,
            'nfev': best.nfev}


def fit_cpl(obs, fs8_interp):
    """Fit B: CPL w0+wa. Free: w0, wa, Om, H0."""
    def objective(params):
        w0, wa, Om, H0 = params
        if Om < 0.15 or Om > 0.55 or H0 < 58 or H0 > 78:
            return 1e10
        if w0 < -1.8 or w0 > -0.3 or wa < -2.5 or wa > 2.0:
            return 1e10
        try:
            model = fast_observables(H0, Om, w0, wa, fs8_interp)
            return chi2_components(obs, model)['total'] if model else 1e10
        except:
            return 1e10

    best = None
    for x0 in [
        [W0_TRUE, 0.0, OM_TRUE, H0_TRUE],
        [-0.85, -0.5, 0.30, 68.0],
        [-0.70, -0.8, 0.32, 67.0],
        [-0.95, -0.3, 0.31, 67.5],
    ]:
        res = minimize(objective, x0, method='Powell',
                      options={'maxiter': 3000, 'ftol': 1e-8, 'maxfev': 8000})
        if best is None or res.fun < best.fun:
            best = res

    w0, wa, Om, H0 = best.x
    model = fast_observables(H0, Om, w0, wa, fs8_interp)
    chi2 = chi2_components(obs, model)
    return {'w0': w0, 'wa': wa, 'Om': Om, 'H0': H0, 'chi2': chi2,
            'nfev': best.nfev}


# =============================================================================
# Analysis
# =============================================================================

def analyze_results(results_A, results_B):
    """Full statistical analysis."""
    n = len(results_A)
    wa_B = np.array([r['wa'] for r in results_B])
    w0_A = np.array([r['w0'] for r in results_A])
    w0_B = np.array([r['w0'] for r in results_B])
    Om_A = np.array([r['Om'] for r in results_A])
    Om_B = np.array([r['Om'] for r in results_B])
    H0_A = np.array([r['H0'] for r in results_A])
    H0_B = np.array([r['H0'] for r in results_B])

    chi2_A = np.array([r['chi2']['total'] for r in results_A])
    chi2_B = np.array([r['chi2']['total'] for r in results_B])
    k_A, k_B = 3, 4
    aic_A = chi2_A + 2 * k_A
    aic_B = chi2_B + 2 * k_B
    daic = aic_A - aic_B

    chi2_bao_A = np.array([r['chi2']['bao'] for r in results_A])
    chi2_bao_B = np.array([r['chi2']['bao'] for r in results_B])
    chi2_sne_A = np.array([r['chi2']['sne'] for r in results_A])
    chi2_sne_B = np.array([r['chi2']['sne'] for r in results_B])
    chi2_fs8_A = np.array([r['chi2']['fs8'] for r in results_A])
    chi2_fs8_B = np.array([r['chi2']['fs8'] for r in results_B])
    chi2_cmb_A = np.array([r['chi2']['cmb'] for r in results_A])
    chi2_cmb_B = np.array([r['chi2']['cmb'] for r in results_B])

    dchi2_expansion = ((chi2_bao_A + chi2_sne_A + chi2_cmb_A) -
                       (chi2_bao_B + chi2_sne_B + chi2_cmb_B))
    dchi2_growth = chi2_fs8_A - chi2_fs8_B

    print("\n" + "=" * 70)
    print("18I MOCK-DATA VALIDATION -- RESULTS")
    print("=" * 70)
    print(f"\nMeridian truth: w0={W0_TRUE}, wa={WA_TRUE}, Om={OM_TRUE:.5f}, H0={H0_TRUE}")
    print(f"Realizations: {n}")

    print(f"\n--- Fit A (constant w, GR -- TRUE model, 3 params) ---")
    print(f"  w0:  mean={np.mean(w0_A):.4f} +/- {np.std(w0_A):.4f}, median={np.median(w0_A):.4f}")
    print(f"  Om:  mean={np.mean(Om_A):.5f} +/- {np.std(Om_A):.5f}")
    print(f"  H0:  mean={np.mean(H0_A):.3f} +/- {np.std(H0_A):.3f}")
    print(f"  chi2: mean={np.mean(chi2_A):.2f} +/- {np.std(chi2_A):.2f}")

    print(f"\n--- Fit B (CPL w0+wa -- WRONG model, 4 params) ---")
    print(f"  w0:  mean={np.mean(w0_B):.4f} +/- {np.std(w0_B):.4f}, median={np.median(w0_B):.4f}")
    print(f"  wa:  mean={np.mean(wa_B):.4f} +/- {np.std(wa_B):.4f}, median={np.median(wa_B):.4f}")
    print(f"  Om:  mean={np.mean(Om_B):.5f} +/- {np.std(Om_B):.5f}")
    print(f"  H0:  mean={np.mean(H0_B):.3f} +/- {np.std(H0_B):.3f}")
    print(f"  chi2: mean={np.mean(chi2_B):.2f} +/- {np.std(chi2_B):.2f}")

    frac_wa_neg = np.mean(wa_B < 0)
    wa_sigma = np.std(wa_B)
    frac_wa_2sig = np.mean(np.abs(wa_B) > 2 * wa_sigma) if wa_sigma > 0.001 else 0.0
    frac_daic_pos = np.mean(daic > 0)
    frac_split = np.mean((dchi2_expansion > 0) & (dchi2_growth < 0))

    print(f"\n--- KEY DIAGNOSTICS ---")
    print(f"  Fraction wa < 0:                    {frac_wa_neg:.3f} ({frac_wa_neg*100:.1f}%)")
    print(f"  Median wa:                          {np.median(wa_B):.4f}")
    print(f"  Mean |wa|:                          {np.mean(np.abs(wa_B)):.4f}")
    print(f"  Std(wa):                            {wa_sigma:.4f}")
    print(f"  Fraction |wa| > 2*std(wa):          {frac_wa_2sig:.3f} ({frac_wa_2sig*100:.1f}%)")
    print(f"  Mean DAIC (A-B):                    {np.mean(daic):.3f} +/- {np.std(daic):.3f}")
    print(f"  Fraction DAIC > 0 (CPL preferred):  {frac_daic_pos:.3f} ({frac_daic_pos*100:.1f}%)")
    print(f"  Probe split (growth->A, exp->B):    {frac_split:.3f} ({frac_split*100:.1f}%)")
    print(f"  Mean dchi2_expansion (A-B):         {np.mean(dchi2_expansion):.3f}")
    print(f"  Mean dchi2_growth (A-B):            {np.mean(dchi2_growth):.3f}")

    # Probe-by-probe breakdown
    print(f"\n--- PROBE-BY-PROBE chi2 (mean, Fit A vs Fit B) ---")
    print(f"  BAO:  {np.mean(chi2_bao_A):.2f} vs {np.mean(chi2_bao_B):.2f}  (delta={np.mean(chi2_bao_A - chi2_bao_B):.3f})")
    print(f"  SNe:  {np.mean(chi2_sne_A):.2f} vs {np.mean(chi2_sne_B):.2f}  (delta={np.mean(chi2_sne_A - chi2_sne_B):.3f})")
    print(f"  fs8:  {np.mean(chi2_fs8_A):.2f} vs {np.mean(chi2_fs8_B):.2f}  (delta={np.mean(chi2_fs8_A - chi2_fs8_B):.3f})")
    print(f"  CMB:  {np.mean(chi2_cmb_A):.2f} vs {np.mean(chi2_cmb_B):.2f}  (delta={np.mean(chi2_cmb_A - chi2_cmb_B):.3f})")

    # Verdict
    print(f"\n--- VERDICT ---")
    artifact_detected = False
    reasons = []

    if frac_wa_neg > 0.5:
        artifact_detected = True
        reasons.append(f"CPL produces wa < 0 in {frac_wa_neg*100:.1f}% (>50%)")
    if frac_daic_pos > 0.3:
        artifact_detected = True
        reasons.append(f"CPL preferred (DAIC > 0) in {frac_daic_pos*100:.1f}% (>30%)")
    if frac_split > 0.3:
        artifact_detected = True
        reasons.append(f"Probe split in {frac_split*100:.1f}% (>30%)")

    if np.mean(np.abs(wa_B)) < 0.05:
        print("  VALIDATION FAILS: CPL recovers wa ~ 0 consistently (mean |wa| < 0.05)")
        print("  The artifact hypothesis does NOT hold for this data combination.")
    elif artifact_detected:
        print("  VALIDATION PASSES: Compromise artifact detected!")
        for r in reasons:
            print(f"    * {r}")
    else:
        print("  VALIDATION INCONCLUSIVE:")
        print(f"    wa<0 in {frac_wa_neg*100:.1f}% (need >50%)")
        print(f"    DAIC>0 in {frac_daic_pos*100:.1f}% (need >30%)")
        print(f"    Probe split in {frac_split*100:.1f}% (need >30%)")
        print(f"    Mean |wa| = {np.mean(np.abs(wa_B)):.4f}")

    return {
        'wa_B': wa_B, 'w0_A': w0_A, 'w0_B': w0_B,
        'daic': daic,
        'dchi2_expansion': dchi2_expansion, 'dchi2_growth': dchi2_growth,
        'chi2_bao_A': chi2_bao_A, 'chi2_bao_B': chi2_bao_B,
        'chi2_sne_A': chi2_sne_A, 'chi2_sne_B': chi2_sne_B,
        'chi2_fs8_A': chi2_fs8_A, 'chi2_fs8_B': chi2_fs8_B,
        'chi2_cmb_A': chi2_cmb_A, 'chi2_cmb_B': chi2_cmb_B,
    }


# =============================================================================
# Visualization
# =============================================================================

def make_figure(analysis, outpath):
    """4-panel results figure."""
    wa = analysis['wa_B']
    daic = analysis['daic']
    dchi2_exp = analysis['dchi2_expansion']
    dchi2_gro = analysis['dchi2_growth']
    n = len(wa)

    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    fig.suptitle(
        f'18I: Mock-Data Validation -- Decoupled Perturbation Test\n'
        f'Truth: w0={W0_TRUE}, wa=0 (Meridian), {n} realizations',
        fontsize=14, fontweight='bold')

    # Panel 1: wa histogram
    ax = axes[0, 0]
    ax.hist(wa, bins=30, color='steelblue', edgecolor='black', alpha=0.8, density=True)
    ax.axvline(0, color='red', ls='--', lw=2, label='Truth (wa=0)')
    ax.axvline(np.median(wa), color='orange', ls='-', lw=2,
               label=f'Median={np.median(wa):.3f}')
    frac_neg = np.mean(wa < 0) * 100
    ax.set_xlabel('Best-fit wa (CPL)', fontsize=12)
    ax.set_ylabel('Density', fontsize=12)
    ax.set_title(f'CPL wa Distribution ({frac_neg:.1f}% < 0)', fontsize=12)
    ax.legend(fontsize=10)

    # Panel 2: DAIC distribution
    ax = axes[0, 1]
    ax.hist(daic, bins=30, color='coral', edgecolor='black', alpha=0.8, density=True)
    ax.axvline(0, color='black', ls='-', lw=1)
    ax.axvline(np.mean(daic), color='darkred', ls='--', lw=2,
               label=f'Mean={np.mean(daic):.2f}')
    frac_pos = np.mean(daic > 0) * 100
    ax.set_xlabel('DAIC = AIC_const - AIC_CPL', fontsize=12)
    ax.set_ylabel('Density', fontsize=12)
    ax.set_title(f'DAIC Distribution ({frac_pos:.1f}% > 0 = CPL preferred)', fontsize=12)
    ax.legend(fontsize=10)

    # Panel 3: wa vs DAIC
    ax = axes[1, 0]
    scatter = ax.scatter(wa, daic, c=np.abs(wa), cmap='viridis',
                        alpha=0.5, s=20, edgecolors='none')
    ax.axhline(0, color='gray', ls='--', lw=1)
    ax.axvline(0, color='gray', ls='--', lw=1)
    ax.set_xlabel('Best-fit wa', fontsize=12)
    ax.set_ylabel('DAIC', fontsize=12)
    ax.set_title('wa vs DAIC', fontsize=12)
    plt.colorbar(scatter, ax=ax, label='|wa|')
    ax.text(0.05, 0.95, 'wa<0, CPL preferred\n(artifact zone)',
            transform=ax.transAxes, fontsize=8, va='top',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

    # Panel 4: Probe-split
    ax = axes[1, 1]
    ax.scatter(dchi2_exp, dchi2_gro, alpha=0.5, s=20, c='teal', edgecolors='none')
    ax.axhline(0, color='gray', ls='--', lw=1)
    ax.axvline(0, color='gray', ls='--', lw=1)
    ax.set_xlabel('dchi2 expansion (A-B)', fontsize=12)
    ax.set_ylabel('dchi2 growth (A-B)', fontsize=12)
    ax.set_title('Probe-Split: Expansion vs Growth Preference', fontsize=12)
    n_artifact = np.sum((dchi2_exp > 0) & (dchi2_gro < 0))
    ax.text(0.95, 0.05, f'Expansion->CPL\nGrowth->const-w\n({n_artifact}/{n})',
            transform=ax.transAxes, fontsize=9, ha='right', va='bottom',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

    plt.tight_layout(rect=[0, 0, 1, 0.93])
    plt.savefig(outpath, dpi=150, bbox_inches='tight')
    print(f"\nFigure saved to: {outpath}")
    plt.close()


# =============================================================================
# MAIN
# =============================================================================

def main():
    t_start = time.time()

    print("=" * 70)
    print("18I: MOCK-DATA VALIDATION -- DECOUPLED PERTURBATION TEST")
    print("=" * 70)
    print(f"\nMeridian truth: w0={W0_TRUE}, wa={WA_TRUE}")
    print(f"Realizations: {N_REALIZATIONS}")

    # Step 1: CAMB truth
    print("\n[Step 1] Computing truth observables with CAMB...")
    truth = get_camb_observables(H0_TRUE, OMBH2_TRUE, OMCH2_TRUE, W0_TRUE, WA_TRUE)
    print(f"  BAO D_M/r_d: {truth['DM_rd']}")
    print(f"  BAO D_H/r_d: {truth['DH_rd']}")
    print(f"  SNe mu range: [{truth['mu_sne'][0]:.2f}, {truth['mu_sne'][-1]:.2f}]")
    print(f"  fsigma8: {truth['fs8']}")
    print(f"  CMB: R={truth['R_cmb']:.5f}, la={truth['la_cmb']:.2f}, ob={truth['ob_cmb']:.5f}")
    print(f"  r_d = {truth['rd']:.4f} Mpc, r_s* = {truth['rs_star']:.4f} Mpc")

    # Calibrate fast model
    print("\n[Step 1b] Calibrating fast forward model against CAMB truth...")
    calibrate_fast_model(truth)

    # Verify calibration
    test_model = fast_observables(H0_TRUE, OM_TRUE, W0_TRUE, 0.0, None)
    print(f"  Post-calibration DM/rd residual: {np.max(np.abs(test_model['DM_rd'] - truth['DM_rd'])):.6f}")
    print(f"  Post-calibration DH/rd residual: {np.max(np.abs(test_model['DH_rd'] - truth['DH_rd'])):.6f}")
    print(f"  Post-calibration mu residual: {np.max(np.abs(test_model['mu_sne'] - truth['mu_sne'])):.6f}")

    # Speed test
    print("\n[Step 1c] Speed test...")
    t0 = time.time()
    for _ in range(1000):
        fast_observables(67.5, 0.31, -0.8, -0.3, None)
    dt = time.time() - t0
    print(f"  1000 forward model evaluations: {dt:.3f}s ({dt*1000:.1f}ms total, {dt:.4f}ms per call)")
    print(f"  Estimated time for 200 realizations x 2 fits x 200 evals: {200*2*200*dt/1000:.0f}s")

    # Build fsigma8 grids
    print("\n[Step 1d] Building fsigma8 grid (constant-w)...")
    t0 = time.time()
    Om_g, w0_g, wa_g, fs8_g = build_fsigma8_grid(de_model='fluid')
    fs8_interp_A = FSigma8Interpolator(Om_g, w0_g, wa_g, fs8_g)
    print(f"  Done in {time.time()-t0:.1f}s")

    # Validate
    fs8_test = fs8_interp_A(OM_TRUE, W0_TRUE, 0.0)
    print(f"  fsigma8 at truth (interpolated): {fs8_test}")
    print(f"  fsigma8 at truth (CAMB):         {truth['fs8']}")
    print(f"  Max residual: {np.max(np.abs(fs8_test - truth['fs8'])):.5f}")

    print("\n[Step 1e] Building fsigma8 grid (CPL/ppf)...")
    t0 = time.time()
    Om_g2, w0_g2, wa_g2, fs8_g2 = build_fsigma8_grid(de_model='ppf')
    fs8_interp_B = FSigma8Interpolator(Om_g2, w0_g2, wa_g2, fs8_g2)
    print(f"  Done in {time.time()-t0:.1f}s")

    # Step 2: Uncertainties
    unc = generate_uncertainties()
    print(f"\n[Step 2] Uncertainties defined.")

    # Step 3: Fit realizations
    print(f"\n[Step 3] Fitting {N_REALIZATIONS} realizations...")
    rng = np.random.default_rng(seed=42)
    results_A, results_B = [], []

    for i in range(N_REALIZATIONS):
        if (i + 1) % 20 == 0 or i == 0:
            elapsed = time.time() - t_start
            if i > 0:
                per_real = elapsed / (i + 1)
                eta = per_real * (N_REALIZATIONS - i - 1)
            else:
                eta = 0
            print(f"  Realization {i+1}/{N_REALIZATIONS} "
                  f"(elapsed: {elapsed:.0f}s, ETA: {eta:.0f}s)", flush=True)

        mock = generate_mock_data(truth, unc, rng)

        try:
            res_A = fit_constant_w(mock, fs8_interp_A)
        except Exception as e:
            print(f"  Fit A failed #{i}: {e}")
            continue

        try:
            res_B = fit_cpl(mock, fs8_interp_B)
        except Exception as e:
            print(f"  Fit B failed #{i}: {e}")
            continue

        results_A.append(res_A)
        results_B.append(res_B)

    print(f"\n  Successful fits: {len(results_A)}/{N_REALIZATIONS}")

    # Step 4: Analysis
    analysis = analyze_results(results_A, results_B)

    # Step 5: Visualization
    outpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), '18I_results.png')
    make_figure(analysis, outpath)

    elapsed_total = time.time() - t_start
    print(f"\nTotal runtime: {elapsed_total:.1f}s ({elapsed_total/60:.1f} min)")
    print("\n" + "=" * 70)
    print("18I COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    main()
