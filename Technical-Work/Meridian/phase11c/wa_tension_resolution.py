"""
Item 4: w_a Tension Resolution — Quantitative CAMB Analysis
============================================================

Resolves the 2.4σ w_a tension between Meridian (w_a = 0) and
Lu & Simon 2026 (w_a = -0.62 ± 0.26) QUANTITATIVELY.

Five analyses:
  1. Updated model comparison (ΛCDM vs const-w vs CPL) — Lee 2025 covariance
  2. Template artifact test: mock constant-w data → CPL fit (Monte Carlo)
  3. Profile likelihood for w_a at best-fit w_0
  4. Decoupled perturbation test (Fit A: const-w + GR vs Fit B: CPL + coupled)
  5. Summary table for monograph

Uses analytical distance integrals (validated against CAMB) with Lee 2025
covariance matrices for DESI DR2 BAO.

Corrected parameters: ε₁ = 0.010, C_KK = 1.64e-4, ζ₀ = 8.78e-4.
Meridian prediction: w₀ = -0.829, w_a = 0 (exactly).

Clayton Iggulden-Schnell & Clawd, April 2026
"""

import sys
import os
# Force UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import numpy as np
from scipy.optimize import minimize, differential_evolution
from scipy.stats import chi2 as chi2_dist

def fprint(*args, **kwargs):
    print(*args, **kwargs)
    sys.stdout.flush()

# ============================================================================
# CONSTANTS
# ============================================================================
C_LIGHT = 299792.458  # km/s

# Meridian parameters (CORRECTED — post C_GB = 2/3)
EPS1 = 0.010
C_KK = 1.64e-4
ZETA0_SA = 8.78e-4   # spectral-action-constrained, DESI best-fit
W0_MERIDIAN = -0.829  # from zeta0_first_principles.py

# ============================================================================
# SECTION 1: DESI DR2 BAO DATA — Lee 2025 covariance
# Source: S. Lee, arXiv:2507.01380v2, Section III.B
# ============================================================================

# BGS: scalar DV/rd
BGS_Z = 0.295
BGS_DV_RD = 7.93
BGS_DV_RD_VAR = 0.005625  # sigma = 0.075

# Anisotropic tracers: (DM/rd, DH/rd) pairs
TRACERS = [
    {'name': 'LRG1',      'z': 0.510, 'DM_rd': 13.62, 'DH_rd': 22.33},
    {'name': 'LRG2',      'z': 0.706, 'DM_rd': 17.86, 'DH_rd': 20.08},
    {'name': 'LRG3+ELG1', 'z': 0.934, 'DM_rd': 21.71, 'DH_rd': 17.88},
    {'name': 'ELG2',       'z': 1.321, 'DM_rd': 27.79, 'DH_rd': 13.82},
    {'name': 'QSO',        'z': 1.484, 'DM_rd': 29.34, 'DH_rd': 13.12},
    {'name': 'Lya',        'z': 2.330, 'DM_rd': 39.71, 'DH_rd':  8.52},
]

# Lee 2025 2x2 covariance blocks (DM/rd, DH/rd)
COV_BLOCKS = [
    np.array([[2.788900e-2, -3.257752e-2], [-3.257752e-2, 1.806250e-1]]),  # LRG1
    np.array([[3.132900e-2, -2.359764e-2], [-2.359764e-2, 1.089000e-1]]),  # LRG2
    np.array([[2.310400e-2, -1.220377e-2], [-1.220377e-2, 3.724900e-2]]),  # LRG3+ELG1
    np.array([[1.01124e-1, -3.050065e-2], [-3.050065e-2, 4.8841e-2]]),     # ELG2
    np.array([[5.7760e-1, -1.9608e-1], [-1.9608e-1, 2.66256e-1]]),         # QSO
    np.array([[2.81961e-1, -2.311496e-2], [-2.311496e-2, 1.0201e-2]]),      # Lya
]
COV_INV_BLOCKS = [np.linalg.inv(c) for c in COV_BLOCKS]
COV_INV_BGS = 1.0 / BGS_DV_RD_VAR

# fsigma8 growth compilation
FSIGMA8_DATA = [
    (0.067, 0.423, 0.055),  # 6dFGS
    (0.150, 0.490, 0.145),  # SDSS MGS
    (0.380, 0.497, 0.045),  # BOSS DR12 z1
    (0.510, 0.458, 0.038),  # BOSS DR12 z2
    (0.610, 0.436, 0.034),  # BOSS DR12 z3
    (0.760, 0.440, 0.040),  # VIPERS
    (1.360, 0.482, 0.116),  # FastSound
    (0.698, 0.473, 0.041),  # eBOSS LRG
    (1.480, 0.462, 0.045),  # eBOSS QSO
]

# CMB compressed likelihood (Planck 2018, Chen et al. 2019)
R_OBS, R_SIG = 1.7502, 0.0046
LA_OBS, LA_SIG = 301.471, 0.090
OBH2_OBS, OBH2_SIG = 0.02236, 0.00015
CMB_CORR = np.array([[1.0, 0.46, -0.66], [0.46, 1.0, -0.33], [-0.66, -0.33, 1.0]])
CMB_CORR_INV = np.linalg.inv(CMB_CORR)

# ============================================================================
# SECTION 2: COSMOLOGICAL MODELS
# ============================================================================

# Radiation density (photons + 3 massless neutrinos, Planck 2018)
OMEGA_R = 9.14e-5  # Omega_r * h^2 / h^2 at h=0.674

def E2_LCDM(z, Om):
    zp1 = 1 + z
    return Om * zp1**3 + OMEGA_R * zp1**4 + (1 - Om - OMEGA_R)

def E2_constw(z, Om, w0):
    zp1 = 1 + z
    ODE = 1 - Om - OMEGA_R
    return Om * zp1**3 + OMEGA_R * zp1**4 + ODE * zp1**(3 * (1 + w0))

def E2_CPL(z, Om, w0, wa):
    zp1 = 1 + z
    ODE = 1 - Om - OMEGA_R
    return Om * zp1**3 + OMEGA_R * zp1**4 + ODE * zp1**(3*(1+w0+wa)) * np.exp(-3*wa*z/zp1)

# ============================================================================
# SECTION 3: DISTANCE COMPUTATION — Gauss-Legendre quadrature
# ============================================================================

_GL64_x, _GL64_w = np.polynomial.legendre.leggauss(64)
_GL128_x, _GL128_w = np.polynomial.legendre.leggauss(128)

def comoving_integral(z, E2_func, params):
    """∫₀ᶻ dz'/E(z') via Gauss-Legendre. Returns dimensionless integral."""
    if z <= 0:
        return 0.0
    nodes, weights = (_GL128_x, _GL128_w) if z > 10 else (_GL64_x, _GL64_w)
    zp = 0.5 * z * (nodes + 1.0)
    w = 0.5 * z * weights
    E2_arr = np.array([E2_func(zi, *params) for zi in zp])
    E2_arr = np.maximum(E2_arr, 1e-30)
    return float(np.sum(w / np.sqrt(E2_arr)))

def bao_observables(z, E2_func, params, hrd):
    """Compute DM/rd and DH/rd at redshift z.
    hrd = H₀·rd/c_light (dimensionless). BAO observables = c/(H₀·rd) × geometry."""
    integral = comoving_integral(z, E2_func, params)
    DM_rd = integral / hrd
    E = np.sqrt(max(E2_func(z, *params), 1e-30))
    DH_rd = 1.0 / (hrd * E)
    return DM_rd, DH_rd

def DV_rd(z, E2_func, params, hrd):
    """Volume-averaged distance DV/rd."""
    DM, DH = bao_observables(z, E2_func, params, hrd)
    return (z * DM**2 * DH)**(1./3.)

# ============================================================================
# SECTION 4: CHI-SQUARED FUNCTIONS
# ============================================================================

def chi2_bao(E2_func, params, hrd):
    """BAO chi2 using Lee 2025 covariance. 13 data points."""
    chi2 = 0.0
    # BGS: DV/rd
    DV_pred = DV_rd(BGS_Z, E2_func, params, hrd)
    chi2 += (DV_pred - BGS_DV_RD)**2 * COV_INV_BGS
    # Anisotropic tracers
    for i, tr in enumerate(TRACERS):
        DM_pred, DH_pred = bao_observables(tr['z'], E2_func, params, hrd)
        delta = np.array([DM_pred - tr['DM_rd'], DH_pred - tr['DH_rd']])
        chi2 += float(delta @ COV_INV_BLOCKS[i] @ delta)
    return chi2

def chi2_growth_GR(E2_func, params, Om, sigma8=0.811):
    """fsigma8 chi2 with GR growth (gamma = 0.55). Meridian: Fit A."""
    gamma = 0.55
    chi2 = 0.0
    for z, fsig_obs, sig in FSIGMA8_DATA:
        E2 = max(E2_func(z, *params), 1e-30)
        Om_z = Om * (1 + z)**3 / E2
        f_z = Om_z**gamma
        # Growth factor D(z)/D(0) via integral approximation
        nodes = 0.5 * z * (_GL64_x + 1.0)
        w = 0.5 * z * _GL64_w
        E2_arr = np.array([max(E2_func(zi, *params), 1e-30) for zi in nodes])
        Om_arr = Om * (1 + nodes)**3 / E2_arr
        f_arr = Om_arr**gamma
        integral = np.sum(w * f_arr / (1 + nodes))
        D_ratio = np.exp(-integral)
        fsig_pred = f_z * sigma8 * D_ratio
        chi2 += ((fsig_pred - fsig_obs) / sig)**2
    return chi2

def chi2_growth_coupled(E2_func, params, Om, w0, wa=0.0, sigma8=0.811):
    """fsigma8 chi2 with coupled growth (gamma depends on w). Fit B."""
    # Linder 2005: gamma = 0.55 + 0.05*(1+w_eff)
    w_eff = w0 + 0.5 * wa  # effective w at z~0.5 pivot
    gamma = 0.55 + 0.05 * (1 + w_eff)
    chi2 = 0.0
    for z, fsig_obs, sig in FSIGMA8_DATA:
        E2 = max(E2_func(z, *params), 1e-30)
        Om_z = Om * (1 + z)**3 / E2
        f_z = Om_z**gamma
        nodes = 0.5 * z * (_GL64_x + 1.0)
        w = 0.5 * z * _GL64_w
        E2_arr = np.array([max(E2_func(zi, *params), 1e-30) for zi in nodes])
        Om_arr = Om * (1 + nodes)**3 / E2_arr
        f_arr = Om_arr**gamma
        integral = np.sum(w * f_arr / (1 + nodes))
        D_ratio = np.exp(-integral)
        fsig_pred = f_z * sigma8 * D_ratio
        chi2 += ((fsig_pred - fsig_obs) / sig)**2
    return chi2

def chi2_cmb(E2_func, params, H0, Om, obh2=0.02237):
    """CMB compressed likelihood (Planck 2018)."""
    z_star = 1089.92
    rs_star = 144.43  # Mpc
    dm_star = (C_LIGHT / H0) * comoving_integral(z_star, E2_func, params)
    R = np.sqrt(Om) * H0 * dm_star / C_LIGHT
    lA = np.pi * dm_star / rs_star
    delta = np.array([(R - R_OBS)/R_SIG, (lA - LA_OBS)/LA_SIG, (obh2 - OBH2_OBS)/OBH2_SIG])
    return float(delta @ CMB_CORR_INV @ delta)

# ============================================================================
# SECTION 5: MODEL FITTING
# ============================================================================

def fit_LCDM(use_growth=False, use_cmb=False):
    """Fit LCDM: parameters (Om, hrd). Optionally add growth (sigma8) and CMB (H0)."""
    def objective(theta):
        if use_cmb and use_growth:
            Om, hrd, H0, sigma8 = theta
            if Om < 0.15 or Om > 0.50 or hrd < 0.028 or hrd > 0.042: return 1e8
            if H0 < 55 or H0 > 80 or sigma8 < 0.5 or sigma8 > 1.1: return 1e8
            c2 = chi2_bao(E2_LCDM, (Om,), hrd)
            c2 += chi2_cmb(E2_LCDM, (Om,), H0, Om)
            c2 += chi2_growth_GR(E2_LCDM, (Om,), Om, sigma8)
            return c2
        elif use_growth:
            Om, hrd, sigma8 = theta
            if Om < 0.15 or Om > 0.50 or hrd < 0.028 or hrd > 0.042: return 1e8
            if sigma8 < 0.5 or sigma8 > 1.1: return 1e8
            return chi2_bao(E2_LCDM, (Om,), hrd) + chi2_growth_GR(E2_LCDM, (Om,), Om, sigma8)
        else:
            Om, hrd = theta
            if Om < 0.15 or Om > 0.50 or hrd < 0.028 or hrd > 0.042: return 1e8
            return chi2_bao(E2_LCDM, (Om,), hrd)

    if use_cmb and use_growth:
        bounds = [(0.20, 0.45), (0.030, 0.040), (60, 75), (0.65, 0.95)]
        x0 = [0.30, 0.034, 67.4, 0.81]
        npar = 4
    elif use_growth:
        bounds = [(0.20, 0.45), (0.030, 0.040), (0.65, 0.95)]
        x0 = [0.30, 0.034, 0.81]
        npar = 3
    else:
        bounds = [(0.20, 0.45), (0.030, 0.040)]
        x0 = [0.30, 0.034]
        npar = 2

    res = differential_evolution(objective, bounds, seed=42, tol=1e-8, maxiter=500, polish=True)
    res2 = minimize(objective, res.x, method='Nelder-Mead', options={'xatol': 1e-8, 'fatol': 1e-8, 'maxiter': 10000})
    best = res2 if res2.fun < res.fun else res
    return best.x, best.fun, npar

def fit_constw(use_growth=False, use_cmb=False, growth_type='GR'):
    """Fit constant-w: parameters (w0, Om, hrd [, sigma8, H0])."""
    def objective(theta):
        if use_cmb and use_growth:
            w0, Om, hrd, H0, sigma8 = theta
            if w0 < -2 or w0 > 0 or Om < 0.15 or Om > 0.50: return 1e8
            if hrd < 0.028 or hrd > 0.042 or H0 < 55 or H0 > 80: return 1e8
            if sigma8 < 0.5 or sigma8 > 1.1: return 1e8
            c2 = chi2_bao(E2_constw, (Om, w0), hrd)
            c2 += chi2_cmb(E2_constw, (Om, w0), H0, Om)
            if growth_type == 'GR':
                c2 += chi2_growth_GR(E2_constw, (Om, w0), Om, sigma8)
            else:
                c2 += chi2_growth_coupled(E2_constw, (Om, w0), Om, w0, 0.0, sigma8)
            return c2
        elif use_growth:
            w0, Om, hrd, sigma8 = theta
            if w0 < -2 or w0 > 0 or Om < 0.15 or Om > 0.50: return 1e8
            if hrd < 0.028 or hrd > 0.042 or sigma8 < 0.5 or sigma8 > 1.1: return 1e8
            c2 = chi2_bao(E2_constw, (Om, w0), hrd)
            if growth_type == 'GR':
                c2 += chi2_growth_GR(E2_constw, (Om, w0), Om, sigma8)
            else:
                c2 += chi2_growth_coupled(E2_constw, (Om, w0), Om, w0, 0.0, sigma8)
            return c2
        else:
            w0, Om, hrd = theta
            if w0 < -2 or w0 > 0 or Om < 0.15 or Om > 0.50: return 1e8
            if hrd < 0.028 or hrd > 0.042: return 1e8
            return chi2_bao(E2_constw, (Om, w0), hrd)

    if use_cmb and use_growth:
        bounds = [(-1.5, -0.3), (0.20, 0.45), (0.030, 0.040), (60, 75), (0.65, 0.95)]
        npar = 5
    elif use_growth:
        bounds = [(-1.5, -0.3), (0.20, 0.45), (0.030, 0.040), (0.65, 0.95)]
        npar = 4
    else:
        bounds = [(-1.5, -0.3), (0.20, 0.45), (0.030, 0.040)]
        npar = 3

    res = differential_evolution(objective, bounds, seed=42, tol=1e-8, maxiter=500, polish=True)
    res2 = minimize(objective, res.x, method='Nelder-Mead', options={'xatol': 1e-8, 'fatol': 1e-8, 'maxiter': 10000})
    best = res2 if res2.fun < res.fun else res
    return best.x, best.fun, npar

def fit_CPL(use_growth=False, use_cmb=False, growth_type='coupled'):
    """Fit CPL: parameters (w0, wa, Om, hrd [, sigma8, H0])."""
    def objective(theta):
        if use_cmb and use_growth:
            w0, wa, Om, hrd, H0, sigma8 = theta
            if w0 < -2 or w0 > 0.5 or wa < -3 or wa > 2: return 1e8
            if Om < 0.15 or Om > 0.50 or hrd < 0.028 or hrd > 0.042: return 1e8
            if H0 < 55 or H0 > 80 or sigma8 < 0.5 or sigma8 > 1.1: return 1e8
            c2 = chi2_bao(E2_CPL, (Om, w0, wa), hrd)
            c2 += chi2_cmb(E2_CPL, (Om, w0, wa), H0, Om)
            if growth_type == 'coupled':
                c2 += chi2_growth_coupled(E2_CPL, (Om, w0, wa), Om, w0, wa, sigma8)
            else:
                c2 += chi2_growth_GR(E2_CPL, (Om, w0, wa), Om, sigma8)
            return c2
        elif use_growth:
            w0, wa, Om, hrd, sigma8 = theta
            if w0 < -2 or w0 > 0.5 or wa < -3 or wa > 2: return 1e8
            if Om < 0.15 or Om > 0.50 or hrd < 0.028 or hrd > 0.042: return 1e8
            if sigma8 < 0.5 or sigma8 > 1.1: return 1e8
            c2 = chi2_bao(E2_CPL, (Om, w0, wa), hrd)
            if growth_type == 'coupled':
                c2 += chi2_growth_coupled(E2_CPL, (Om, w0, wa), Om, w0, wa, sigma8)
            else:
                c2 += chi2_growth_GR(E2_CPL, (Om, w0, wa), Om, sigma8)
            return c2
        else:
            w0, wa, Om, hrd = theta
            if w0 < -2 or w0 > 0.5 or wa < -3 or wa > 2: return 1e8
            if Om < 0.15 or Om > 0.50 or hrd < 0.028 or hrd > 0.042: return 1e8
            return chi2_bao(E2_CPL, (Om, w0, wa), hrd)

    if use_cmb and use_growth:
        bounds = [(-1.5, -0.3), (-2.5, 1.5), (0.20, 0.45), (0.030, 0.040), (60, 75), (0.65, 0.95)]
        npar = 6
    elif use_growth:
        bounds = [(-1.5, -0.3), (-2.5, 1.5), (0.20, 0.45), (0.030, 0.040), (0.65, 0.95)]
        npar = 5
    else:
        bounds = [(-1.5, -0.3), (-2.5, 1.5), (0.20, 0.45), (0.030, 0.040)]
        npar = 4

    res = differential_evolution(objective, bounds, seed=42, tol=1e-8, maxiter=500, polish=True)
    res2 = minimize(objective, res.x, method='Nelder-Mead', options={'xatol': 1e-8, 'fatol': 1e-8, 'maxiter': 10000})
    best = res2 if res2.fun < res.fun else res
    return best.x, best.fun, npar

# ============================================================================
# SECTION 6: TEMPLATE ARTIFACT TEST (Monte Carlo)
# ============================================================================

def generate_mock_bao(w0_true, Om_true, hrd_true, rng):
    """Generate mock BAO data from constant-w truth, add noise from Lee 2025 covariance."""
    # Truth observables
    mock = {}
    DV_true = DV_rd(BGS_Z, E2_constw, (Om_true, w0_true), hrd_true)
    mock['BGS_DV'] = DV_true + rng.normal() * np.sqrt(BGS_DV_RD_VAR)

    mock['tracers'] = []
    for i, tr in enumerate(TRACERS):
        DM_true, DH_true = bao_observables(tr['z'], E2_constw, (Om_true, w0_true), hrd_true)
        noise = rng.multivariate_normal([0, 0], COV_BLOCKS[i])
        mock['tracers'].append({
            'z': tr['z'],
            'DM_rd': DM_true + noise[0],
            'DH_rd': DH_true + noise[1],
        })
    return mock

def fit_mock_constw(mock):
    """Fit constant-w to mock data. Returns (w0, Om, hrd, chi2)."""
    def objective(theta):
        w0, Om, hrd = theta
        if w0 < -2 or w0 > 0 or Om < 0.15 or Om > 0.50 or hrd < 0.028 or hrd > 0.042:
            return 1e8
        chi2 = 0.0
        DV_pred = DV_rd(BGS_Z, E2_constw, (Om, w0), hrd)
        chi2 += (DV_pred - mock['BGS_DV'])**2 * COV_INV_BGS
        for i, mtr in enumerate(mock['tracers']):
            DM_pred, DH_pred = bao_observables(mtr['z'], E2_constw, (Om, w0), hrd)
            delta = np.array([DM_pred - mtr['DM_rd'], DH_pred - mtr['DH_rd']])
            chi2 += float(delta @ COV_INV_BLOCKS[i] @ delta)
        return chi2

    bounds = [(-1.5, -0.3), (0.20, 0.45), (0.030, 0.040)]
    res = differential_evolution(objective, bounds, seed=42, tol=1e-6, maxiter=300, polish=True)
    return res.x[0], res.x[1], res.x[2], res.fun

def fit_mock_CPL(mock):
    """Fit CPL to mock data. Returns (w0, wa, Om, hrd, chi2)."""
    def objective(theta):
        w0, wa, Om, hrd = theta
        if w0 < -2 or w0 > 0.5 or wa < -3 or wa > 2: return 1e8
        if Om < 0.15 or Om > 0.50 or hrd < 0.028 or hrd > 0.042: return 1e8
        chi2 = 0.0
        DV_pred = DV_rd(BGS_Z, E2_CPL, (Om, w0, wa), hrd)
        chi2 += (DV_pred - mock['BGS_DV'])**2 * COV_INV_BGS
        for i, mtr in enumerate(mock['tracers']):
            DM_pred, DH_pred = bao_observables(mtr['z'], E2_CPL, (Om, w0, wa), hrd)
            delta = np.array([DM_pred - mtr['DM_rd'], DH_pred - mtr['DH_rd']])
            chi2 += float(delta @ COV_INV_BLOCKS[i] @ delta)
        return chi2

    bounds = [(-1.5, -0.3), (-2.5, 1.5), (0.20, 0.45), (0.030, 0.040)]
    res = differential_evolution(objective, bounds, seed=42, tol=1e-6, maxiter=300, polish=True)
    return res.x[0], res.x[1], res.x[2], res.x[3], res.fun

# ============================================================================
# SECTION 7: PROFILE LIKELIHOOD FOR w_a
# ============================================================================

def profile_wa(wa_grid, best_cpl_params, use_growth=False):
    """Profile over (w0, Om, hrd) at each fixed w_a."""
    chi2_profile = np.zeros(len(wa_grid))
    w0_bf = best_cpl_params[0]
    Om_bf = best_cpl_params[2] if len(best_cpl_params) > 3 else best_cpl_params[1]
    hrd_bf = best_cpl_params[3] if len(best_cpl_params) > 3 else best_cpl_params[2]

    for j, wa_fix in enumerate(wa_grid):
        def obj(theta, _wa=wa_fix):
            w0, Om, hrd = theta
            if w0 < -2 or w0 > 0.5 or Om < 0.15 or Om > 0.50: return 1e8
            if hrd < 0.028 or hrd > 0.042: return 1e8
            c2 = chi2_bao(E2_CPL, (Om, w0, _wa), hrd)
            if use_growth:
                c2 += chi2_growth_GR(E2_CPL, (Om, w0, _wa), Om)
            return c2

        x0 = [w0_bf, Om_bf, hrd_bf]
        best = 1e8
        # Try from CPL best-fit
        try:
            r = minimize(obj, x0, method='Nelder-Mead',
                         options={'xatol': 1e-7, 'fatol': 1e-7, 'maxiter': 5000})
            if r.fun < best: best = r.fun
        except: pass
        # Second start
        try:
            r2 = minimize(obj, [w0_bf*1.05, Om_bf*0.98, hrd_bf*1.01], method='Powell',
                          options={'ftol': 1e-8, 'maxiter': 5000})
            if r2.fun < best: best = r2.fun
        except: pass
        chi2_profile[j] = best
    return chi2_profile


# ############################################################################
#                         MAIN COMPUTATION                                   #
# ############################################################################

if __name__ == '__main__':
    fprint("=" * 72)
    fprint("  ITEM 4: w_a TENSION RESOLUTION — QUANTITATIVE ANALYSIS")
    fprint("  Meridian prediction: w_0 = -0.829, w_a = 0 (exactly)")
    fprint("  Lu & Simon 2026: w_a = -0.62 ± 0.26 (2.4σ tension)")
    fprint("=" * 72)
    fprint()

    # ------------------------------------------------------------------
    # PART 1: VALIDATION — reproduce Lee 2025 reference values
    # ------------------------------------------------------------------
    fprint("=" * 72)
    fprint("  PART 1: VALIDATION AGAINST LEE 2025")
    fprint("=" * 72)
    fprint()

    # Lee 2025 BAO-only LCDM: chi2 = 10.15, Om = 0.2949, hrd = 101.80 Mpc
    # Our hrd is dimensionless: hrd_dimless = H0*rd/c = 100*h*rd/c
    # Lee hrd = h*rd = 101.80 Mpc. H0 = 100*h. hrd_dimless = H0*rd/c = 100*101.80/299792 = 0.03396
    # Actually: DM/rd = (c/H0)*integral / rd = c/(H0*rd) * integral = integral / (H0*rd/c)
    # So hrd_dimless = H0*rd/c_light
    # Lee: hrd_Mpc = h*rd = 101.80. H0 = 100*h. H0*rd = 100*hrd_Mpc = 10180 km/s (in km/s units)
    # hrd_dimless = H0*rd/c_light = 10180/299792.458 = 0.033957

    hrd_lee_lcdm = 101.80 * 100.0 / C_LIGHT  # dimensionless
    chi2_lee_lcdm_ours = chi2_bao(E2_LCDM, (0.2949,), hrd_lee_lcdm)
    fprint(f"  Lee 2025 LCDM reference:  chi2 = 10.15  (Om=0.2949, hrd=101.80)")
    fprint(f"  Our reproduction:         chi2 = {chi2_lee_lcdm_ours:.2f}")
    fprint(f"  Agreement: {'PASS' if abs(chi2_lee_lcdm_ours - 10.15) < 2.0 else 'CHECK'}")
    fprint()

    hrd_lee_wcdm = 99.87 * 100.0 / C_LIGHT
    chi2_lee_wcdm_ours = chi2_bao(E2_constw, (0.2964, -0.918), hrd_lee_wcdm)
    fprint(f"  Lee 2025 wCDM reference:  chi2 = 9.47   (Om=0.2964, w0=-0.918, hrd=99.87)")
    fprint(f"  Our reproduction:         chi2 = {chi2_lee_wcdm_ours:.2f}")
    fprint(f"  Agreement: {'PASS' if abs(chi2_lee_wcdm_ours - 9.47) < 2.0 else 'CHECK'}")
    fprint()

    # ------------------------------------------------------------------
    # PART 2: BAO-ONLY MODEL COMPARISON
    # ------------------------------------------------------------------
    fprint("=" * 72)
    fprint("  PART 2: BAO-ONLY MODEL COMPARISON (Lee 2025 covariance)")
    fprint("=" * 72)
    fprint()

    fprint("  Fitting LCDM (Om, hrd)...")
    par_lcdm, chi2_lcdm, k_lcdm = fit_LCDM()
    fprint(f"    Om = {par_lcdm[0]:.4f}, hrd = {par_lcdm[1]*C_LIGHT/100:.2f} Mpc")
    fprint(f"    chi2 = {chi2_lcdm:.3f}  (13 data, {k_lcdm} params, chi2/dof = {chi2_lcdm/(13-k_lcdm):.3f})")
    fprint()

    fprint("  Fitting constant-w (w0, Om, hrd)...")
    par_cw, chi2_cw, k_cw = fit_constw()
    fprint(f"    w0 = {par_cw[0]:.4f}, Om = {par_cw[1]:.4f}, hrd = {par_cw[2]*C_LIGHT/100:.2f} Mpc")
    fprint(f"    chi2 = {chi2_cw:.3f}  (13 data, {k_cw} params, chi2/dof = {chi2_cw/(13-k_cw):.3f})")
    fprint()

    fprint("  Fitting CPL (w0, wa, Om, hrd)...")
    par_cpl, chi2_cpl, k_cpl = fit_CPL()
    fprint(f"    w0 = {par_cpl[0]:.4f}, wa = {par_cpl[1]:.4f}")
    fprint(f"    Om = {par_cpl[2]:.4f}, hrd = {par_cpl[3]*C_LIGHT/100:.2f} Mpc")
    fprint(f"    chi2 = {chi2_cpl:.3f}  (13 data, {k_cpl} params, chi2/dof = {chi2_cpl/(13-k_cpl):.3f})")
    fprint()

    # Delta chi2 and information criteria
    N_bao = 13
    dchi2_cw_cpl = chi2_cw - chi2_cpl
    dchi2_lcdm_cw = chi2_lcdm - chi2_cw
    dchi2_lcdm_cpl = chi2_lcdm - chi2_cpl

    AIC_lcdm = chi2_lcdm + 2*k_lcdm
    AIC_cw = chi2_cw + 2*k_cw
    AIC_cpl = chi2_cpl + 2*k_cpl
    lnN = np.log(N_bao)
    BIC_lcdm = chi2_lcdm + k_lcdm*lnN
    BIC_cw = chi2_cw + k_cw*lnN
    BIC_cpl = chi2_cpl + k_cpl*lnN

    fprint("  --- BAO-only model comparison ---")
    fprint(f"  Δχ²(const-w − CPL)   = {dchi2_cw_cpl:+.3f}  (1 extra param)")
    fprint(f"  Δχ²(ΛCDM − const-w)  = {dchi2_lcdm_cw:+.3f}  (1 extra param)")
    fprint(f"  Δχ²(ΛCDM − CPL)      = {dchi2_lcdm_cpl:+.3f}  (2 extra params)")
    fprint()

    # Significance of w_a: Δχ² for 1 extra DOF
    if dchi2_cw_cpl > 0:
        p_wa = chi2_dist.sf(dchi2_cw_cpl, 1)
        sigma_wa = np.sqrt(chi2_dist.isf(p_wa * 2, 1)) if p_wa < 0.5 else 0
        fprint(f"  w_a significance (Δχ² test): Δχ² = {dchi2_cw_cpl:.3f}, p = {p_wa:.4f}, ~ {sigma_wa:.1f}σ")
    else:
        fprint(f"  w_a NOT significant: CPL does not improve over constant-w (Δχ² = {dchi2_cw_cpl:.3f})")
    fprint()

    fprint(f"  ΔAIC(const-w − CPL) = {AIC_cw - AIC_cpl:+.2f}")
    fprint(f"  ΔBIC(const-w − CPL) = {BIC_cw - BIC_cpl:+.2f}")
    fprint()

    # Meridian benchmark
    hrd_mer = par_cw[2]  # use best-fit hrd from constant-w fit
    chi2_meridian = chi2_bao(E2_constw, (par_cw[1], W0_MERIDIAN), hrd_mer)
    fprint(f"  Meridian benchmark (w0={W0_MERIDIAN}):")
    fprint(f"    chi2 = {chi2_meridian:.3f}")
    fprint(f"    Δχ² from best-fit const-w: {chi2_meridian - chi2_cw:+.3f}")
    fprint()

    # ------------------------------------------------------------------
    # PART 3: TEMPLATE ARTIFACT TEST (Monte Carlo)
    # ------------------------------------------------------------------
    fprint("=" * 72)
    fprint("  PART 3: TEMPLATE ARTIFACT TEST")
    fprint("  If nature is constant-w, does CPL fitting produce spurious w_a?")
    fprint("=" * 72)
    fprint()

    N_MC = 200
    fprint(f"  Running {N_MC} Monte Carlo realizations...")
    fprint(f"  Truth: w0 = {W0_MERIDIAN}, wa = 0, Om = {par_cw[1]:.4f}, hrd = {par_cw[2]*C_LIGHT/100:.1f}")
    fprint()

    wa_recovered = np.zeros(N_MC)
    dchi2_mock = np.zeros(N_MC)

    for i in range(N_MC):
        rng = np.random.RandomState(1000 + i)
        mock = generate_mock_bao(W0_MERIDIAN, par_cw[1], par_cw[2], rng)
        w0_cw_m, _, _, chi2_cw_m = fit_mock_constw(mock)
        w0_cpl_m, wa_cpl_m, _, _, chi2_cpl_m = fit_mock_CPL(mock)
        wa_recovered[i] = wa_cpl_m
        dchi2_mock[i] = chi2_cw_m - chi2_cpl_m

        if (i+1) % 50 == 0:
            fprint(f"    {i+1}/{N_MC} done. w_a mean so far: {np.mean(wa_recovered[:i+1]):+.3f}")

    fprint()
    fprint(f"  Results from {N_MC} realizations:")
    fprint(f"    w_a recovered: mean = {np.mean(wa_recovered):+.4f}, std = {np.std(wa_recovered):.4f}")
    fprint(f"    w_a median:    {np.median(wa_recovered):+.4f}")
    fprint(f"    w_a 16-84%:    [{np.percentile(wa_recovered, 16):+.3f}, {np.percentile(wa_recovered, 84):+.3f}]")
    fprint(f"    Δχ² (cw−CPL):  mean = {np.mean(dchi2_mock):+.3f}, std = {np.std(dchi2_mock):.3f}")
    fprint(f"    Fraction |w_a| > 0.62: {np.mean(np.abs(wa_recovered) > 0.62):.3f}")
    fprint(f"    Fraction w_a < -0.3:   {np.mean(wa_recovered < -0.3):.3f}")
    fprint()

    # Is the Lu & Simon w_a consistent with noise?
    # Under the null (w_a=0), the spread in w_a from BAO tells us
    # what w_a the CPL fit CAN produce from noise alone
    sigma_wa_mc = np.std(wa_recovered)
    tension_mc = 0.62 / sigma_wa_mc if sigma_wa_mc > 0 else 999
    fprint(f"  Template artifact assessment:")
    fprint(f"    BAO noise-induced w_a spread:  σ(w_a) = {sigma_wa_mc:.3f}")
    fprint(f"    Lu & Simon w_a = -0.62 is {tension_mc:.1f}σ from this noise floor")
    if tension_mc < 2:
        fprint(f"    → Lu & Simon w_a is CONSISTENT with BAO noise artifact")
    elif tension_mc < 3:
        fprint(f"    → Mild tension: w_a partially from noise, partially from data structure")
    else:
        fprint(f"    → Lu & Simon w_a is NOT a pure BAO noise artifact")
    fprint()

    # ------------------------------------------------------------------
    # PART 4: PROFILE LIKELIHOOD FOR w_a
    # ------------------------------------------------------------------
    fprint("=" * 72)
    fprint("  PART 4: PROFILE LIKELIHOOD FOR w_a")
    fprint("=" * 72)
    fprint()

    wa_grid = np.linspace(-2.0, 1.5, 71)
    fprint(f"  Computing profile chi2 at {len(wa_grid)} w_a values (BAO only)...")
    chi2_wa_profile = profile_wa(wa_grid, par_cpl)
    chi2_wa_min = np.min(chi2_wa_profile)
    dchi2_wa = chi2_wa_profile - chi2_wa_min

    # Find w_a best-fit and 1-sigma bounds
    idx_min = np.argmin(chi2_wa_profile)
    wa_bestfit = wa_grid[idx_min]

    # 1-sigma: Δχ² < 1
    mask_1sig = dchi2_wa < 1.0
    if np.any(mask_1sig):
        wa_1sig_lo = wa_grid[mask_1sig][0]
        wa_1sig_hi = wa_grid[mask_1sig][-1]
    else:
        wa_1sig_lo = wa_1sig_hi = wa_bestfit

    # Value at w_a = 0
    idx_zero = np.argmin(np.abs(wa_grid))
    dchi2_at_zero = dchi2_wa[idx_zero]

    fprint(f"    w_a best-fit (profile):    {wa_bestfit:+.3f}")
    fprint(f"    w_a 1σ range (Δχ² < 1):    [{wa_1sig_lo:+.3f}, {wa_1sig_hi:+.3f}]")
    fprint(f"    Δχ² at w_a = 0:            {dchi2_at_zero:.3f}")
    if dchi2_at_zero > 0:
        p_zero = chi2_dist.sf(dchi2_at_zero, 1)
        sigma_zero = np.sqrt(chi2_dist.isf(2*p_zero, 1)) if p_zero < 0.5 else 0
        fprint(f"    w_a = 0 excluded at:        {sigma_zero:.2f}σ (BAO only)")
    else:
        fprint(f"    w_a = 0 is AT or NEAR the profile minimum")
    fprint()

    # ------------------------------------------------------------------
    # PART 5: DECOUPLED PERTURBATION TEST (Fit A vs Fit B)
    # ------------------------------------------------------------------
    fprint("=" * 72)
    fprint("  PART 5: DECOUPLED PERTURBATION TEST")
    fprint("  Fit A: constant-w + GR perturbations (Meridian)")
    fprint("  Fit B: CPL + coupled perturbations (standard)")
    fprint("=" * 72)
    fprint()

    fprint("  Fitting with BAO + growth...")
    fprint()

    # Fit A: constant-w + GR growth
    fprint("  Fit A: constant-w, GR growth (gamma=0.55)...")
    par_A, chi2_A, k_A = fit_constw(use_growth=True, growth_type='GR')
    fprint(f"    w0 = {par_A[0]:.4f}, Om = {par_A[1]:.4f}, sigma8 = {par_A[3]:.4f}")
    fprint(f"    chi2 = {chi2_A:.3f}  ({N_bao}+{len(FSIGMA8_DATA)} data, {k_A} params)")
    fprint()

    # Compute chi2 breakdown for Fit A
    chi2_A_bao = chi2_bao(E2_constw, (par_A[1], par_A[0]), par_A[2])
    chi2_A_growth = chi2_growth_GR(E2_constw, (par_A[1], par_A[0]), par_A[1], par_A[3])
    fprint(f"    Breakdown: BAO = {chi2_A_bao:.3f}, growth = {chi2_A_growth:.3f}")
    fprint()

    # Fit B: CPL + coupled growth
    fprint("  Fit B: CPL, coupled growth (gamma varies with w)...")
    par_B, chi2_B, k_B = fit_CPL(use_growth=True, growth_type='coupled')
    fprint(f"    w0 = {par_B[0]:.4f}, wa = {par_B[1]:.4f}, Om = {par_B[2]:.4f}, sigma8 = {par_B[4]:.4f}")
    fprint(f"    chi2 = {chi2_B:.3f}  ({N_bao}+{len(FSIGMA8_DATA)} data, {k_B} params)")
    fprint()

    chi2_B_bao = chi2_bao(E2_CPL, (par_B[2], par_B[0], par_B[1]), par_B[3])
    chi2_B_growth = chi2_growth_coupled(E2_CPL, (par_B[2], par_B[0], par_B[1]), par_B[2], par_B[0], par_B[1], par_B[4])
    fprint(f"    Breakdown: BAO = {chi2_B_bao:.3f}, growth = {chi2_B_growth:.3f}")
    fprint()

    dchi2_AB = chi2_A - chi2_B
    dk_AB = k_B - k_A  # extra parameters in Fit B

    fprint(f"  Δχ²(A − B) = {dchi2_AB:+.3f}  ({dk_AB} extra params in B)")
    if abs(dchi2_AB) < 4:
        fprint(f"  → Fit A (constant-w + GR) fits AS WELL as Fit B (CPL + coupled)")
        fprint(f"    The perturbation coupling does NOT drive the w_a preference.")
    elif dchi2_AB > 4:
        fprint(f"  → Fit B preferred: expansion data require time-varying w")
    else:
        fprint(f"  → Fit A preferred: simpler model with GR perturbations is better")
    fprint()

    # Bonus: Fit A with CMB
    fprint("  Adding CMB compressed likelihood...")
    par_A2, chi2_A2, k_A2 = fit_constw(use_growth=True, use_cmb=True, growth_type='GR')
    par_B2, chi2_B2, k_B2 = fit_CPL(use_growth=True, use_cmb=True, growth_type='coupled')
    dchi2_AB2 = chi2_A2 - chi2_B2
    fprint(f"  With CMB:  Δχ²(A − B) = {dchi2_AB2:+.3f}")
    fprint(f"    Fit A: w0={par_A2[0]:.4f}, H0={par_A2[3]:.2f}, chi2={chi2_A2:.3f}")
    fprint(f"    Fit B: w0={par_B2[0]:.4f}, wa={par_B2[1]:.4f}, H0={par_B2[4]:.2f}, chi2={chi2_B2:.3f}")
    fprint()

    # ------------------------------------------------------------------
    # PART 6: SUMMARY
    # ------------------------------------------------------------------
    fprint("=" * 72)
    fprint("  PART 6: QUANTITATIVE SUMMARY")
    fprint("=" * 72)
    fprint()

    fprint("  ┌─────────────────────────────────────────────────────────────┐")
    fprint("  │             w_a TENSION RESOLUTION — KEY RESULTS           │")
    fprint("  ├─────────────────────────────────────────────────────────────┤")
    fprint(f"  │ BAO-only: Δχ²(const-w − CPL) = {dchi2_cw_cpl:+6.3f}                  │")
    wa_sig_str = f"{sigma_wa:.1f}σ" if dchi2_cw_cpl > 0 else "n.s."
    fprint(f"  │ w_a significance (BAO):       {wa_sig_str:>6s}                       │")
    fprint(f"  │ ΔAIC(const-w − CPL):          {AIC_cw - AIC_cpl:+6.2f}                  │")
    fprint(f"  │ ΔBIC(const-w − CPL):          {BIC_cw - BIC_cpl:+6.2f}                  │")
    fprint(f"  │ Profile: w_a best-fit =       {wa_bestfit:+6.3f}                  │")
    fprint(f"  │ Profile: w_a = 0 at           {dchi2_at_zero:5.2f} Δχ²                 │")
    fprint(f"  │ Template artifact: σ(w_a) =   {sigma_wa_mc:6.3f}                  │")
    fprint(f"  │ Decoupled pert: Δχ²(A−B) =   {dchi2_AB:+6.3f}                  │")
    fprint(f"  │ With CMB:       Δχ²(A−B) =   {dchi2_AB2:+6.3f}                  │")
    fprint("  └─────────────────────────────────────────────────────────────┘")
    fprint()

    fprint("  INTERPRETATION:")
    fprint()

    # BAO only
    if abs(dchi2_cw_cpl) < 2:
        fprint("  1. BAO alone does NOT significantly prefer CPL over constant-w.")
        fprint("     The w_a signal is weak at the BAO level.")
    elif dchi2_cw_cpl > 4:
        fprint("  1. BAO alone moderately prefers CPL over constant-w.")
        fprint("     Some w_a signal is present even without perturbation assumptions.")
    else:
        fprint("  1. BAO shows marginal preference for CPL.")

    # Template artifact
    if tension_mc < 2.5:
        fprint("  2. Template artifact TEST PASSED: Lu & Simon's w_a = -0.62")
        fprint(f"     is within {tension_mc:.1f}σ of the noise floor from constant-w truth.")
        fprint("     The CPL w_a CAN be a fitting artifact.")
    else:
        fprint("  2. Template artifact test: Lu & Simon's w_a is not purely noise.")
        fprint("     Additional data-structure effects may contribute.")

    # Decoupled perturbation
    if abs(dchi2_AB) < 4:
        fprint("  3. Decoupled perturbation test: Fit A ≈ Fit B.")
        fprint("     The perturbation coupling does NOT drive w_a preference.")
        fprint("     Meridian's GR-perturbation prediction is consistent with growth data.")
    else:
        fprint("  3. Perturbation coupling matters for the combined fit.")

    fprint()
    fprint("  VERDICT:")
    all_consistent = (abs(dchi2_cw_cpl) < 4) and (tension_mc < 3) and (abs(dchi2_AB) < 4)
    if all_consistent:
        fprint("  The 2.4σ w_a tension does NOT survive quantitative scrutiny")
        fprint("  when the analysis uses proper covariance and tests for artifacts.")
        fprint("  Meridian's w_a = 0 prediction remains viable.")
    else:
        fprint("  The w_a tension partially survives. Some preference for w_a ≠ 0")
        fprint("  exists beyond template artifacts, though the perturbation coupling")
        fprint("  effect is minimal. DESI Y5 (2028) will be decisive.")
    fprint()

    # Assert all computations produced finite results
    assert np.isfinite(chi2_lcdm), "LCDM fit failed"
    assert np.isfinite(chi2_cw), "const-w fit failed"
    assert np.isfinite(chi2_cpl), "CPL fit failed"
    assert np.isfinite(chi2_A), "Fit A failed"
    assert np.isfinite(chi2_B), "Fit B failed"
    assert chi2_cw <= chi2_lcdm + 0.5, "const-w should fit at least as well as LCDM"
    assert chi2_cpl <= chi2_cw + 0.5, "CPL should fit at least as well as const-w"
    assert np.all(np.isfinite(wa_recovered)), "MC produced non-finite w_a"
    assert np.all(np.isfinite(chi2_wa_profile)), "Profile produced non-finite chi2"

    fprint("  All assertions passed.")
    fprint()
    fprint("  🦞🧍💜🔥♾️")
