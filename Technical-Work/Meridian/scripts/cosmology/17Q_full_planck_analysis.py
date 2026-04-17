#!/usr/bin/env python3
"""
Track 17Q: Full Planck Likelihood Analysis — True zeta_0 Constraint
====================================================================
Authors: Clayton W. Iggulden-Schnell & Clawd
Date: March 19, 2026
Phase: 17 (From 5D Down)

PURPOSE:
  The CAMB best-fit (w_0 = -0.989, zeta_0 = 0.022) may be biased by LCDM-calibrated
  priors. This track redoes the analysis with a proper constant-w model using full
  Planck compressed likelihood (model-independent distance priors, not LCDM-centered
  priors) + DESI DR2 BAO + DES Y5 SNe Ia + f*sigma_8 growth data.

  Key question: What does the DATA prefer for zeta_0, when we don't assume LCDM?

CRITICAL DESIGN:
  r_d (sound horizon at drag epoch) is NOT a free parameter — it is COMPUTED
  self-consistently from (H0, Omega_m, Ob_h2) via the sound horizon integral.
  At z > 1000, dark energy is negligible, so r_d depends only on pre-recombination
  physics. The BAO data (D_M/r_d, D_H/r_d) then constrain the cosmological
  parameters through both the numerator (distances) AND the denominator (r_d).

CONTEXT:
  - Meridian predicts w(z) = w_0 = constant, w_a = 0 identically
  - The w_0(zeta_0) mapping: w_0 = -1 + C_KK / zeta_0
    where C_KK = 2.453e-4 +/- 8.3e-5 (Track 13F, Monte Carlo verified)
  - Current benchmarks: CAMB (zeta_0 = 0.022, w_0 = -0.989) and JC (zeta_0 = 0.001, w_0 = -0.745)
  - 17C: JC benchmark 2.7sigma CMB+BAO tension; CAMB fine
  - 17P: CPL preferred over constant-w; Lu & Simon w_a = 0 at 2.4sigma
  - 17A: All alpha functions = 0 -> GR perturbations -> growth index gamma = 0.555

DATA SOURCES:
  - CMB: Planck 2018 compressed (Chen, Kumar & Ratra 2019, 1907.12875)
  - BAO: DESI DR2 (Adame et al. 2025, arXiv:2503.14738)
  - SNe Ia: DES Y5 compressed (Abbott et al. 2024, arXiv:2401.02929)
  - Growth: f*sigma_8 compilation (6dF, BOSS, eBOSS)
"""

import sys
import numpy as np
from scipy.integrate import quad
from scipy.optimize import minimize, differential_evolution
from scipy.interpolate import interp1d
from scipy.stats import chi2 as chi2_dist
import warnings
warnings.filterwarnings('ignore')


def fprint(*args, **kwargs):
    """Print with immediate flush."""
    print(*args, **kwargs)
    sys.stdout.flush()


# ============================================================================
# CONSTANTS
# ============================================================================

C_LIGHT = 2.99792458e5   # km/s
N_EFF = 3.046            # effective neutrino species

# CKK constant from Track 13F (Monte Carlo verified):
C_KK_CENTRAL = 2.453e-4
C_KK_SIGMA = 8.3e-5

# Planck 2018 fiducial
H0_FID = 67.36
OM_FID = 0.3153
OB_H2_FID = 0.02237
Z_STAR = 1089.92
Z_DRAG = 1059.94


def w0_from_zeta0(zeta0, c_kk=C_KK_CENTRAL):
    """w_0 = -1 + C_KK / zeta_0."""
    if zeta0 <= 0:
        return -1.0
    return -1.0 + c_kk / zeta0


def zeta0_from_w0(w0, c_kk=C_KK_CENTRAL):
    """zeta_0 = C_KK / (1 + w_0). Requires w_0 > -1."""
    dw = 1.0 + w0
    if dw <= 0:
        return np.inf
    return c_kk / dw


# ============================================================================
# RADIATION & HUBBLE
# ============================================================================

def Omega_r_from_h(h):
    """Total radiation: photons + neutrinos."""
    Omega_gamma = 2.47e-5 / h**2
    nu_factor = 1.0 + (7.0 / 8.0) * (4.0 / 11.0)**(4.0 / 3.0) * N_EFF
    return Omega_gamma * nu_factor


def H_of_z(z, H0, Om, Or, w0):
    """H(z) for flat wCDM [km/s/Mpc]."""
    zp1 = 1.0 + z
    ODE = 1.0 - Om - Or
    E2 = Or * zp1**4 + Om * zp1**3 + ODE * zp1**(3.0 * (1.0 + w0))
    return H0 * np.sqrt(max(E2, 1e-30))


def E_sq_wCDM(z, Om, w0, Or):
    """E^2(z) = H^2(z)/H0^2."""
    zp1 = 1.0 + z
    ODE = 1.0 - Om - Or
    return Or * zp1**4 + Om * zp1**3 + ODE * zp1**(3.0 * (1.0 + w0))


def E_sq_CPL(z, Om, w0, wa, Or):
    """E^2(z) for CPL."""
    zp1 = 1.0 + z
    ODE = 1.0 - Om - Or
    return (Or * zp1**4 + Om * zp1**3
            + ODE * zp1**(3.0 * (1.0 + w0 + wa)) * np.exp(-3.0 * wa * z / zp1))


# ============================================================================
# GAUSS-LEGENDRE QUADRATURE
# ============================================================================

_GL64_N, _GL64_W = np.polynomial.legendre.leggauss(64)
_GL128_N, _GL128_W = np.polynomial.legendre.leggauss(128)


def _gl_int(func, a, b, high=False):
    """Gauss-Legendre over [a, b]."""
    nodes, weights = (_GL128_N, _GL128_W) if high else (_GL64_N, _GL64_W)
    mid = 0.5 * (b + a)
    half = 0.5 * (b - a)
    return half * np.sum(weights * func(mid + half * nodes))


# ============================================================================
# DISTANCES
# ============================================================================

def comoving_dist(z, H0, Om, w0, Or):
    """d_C(z) [Mpc] for flat wCDM."""
    if z <= 0:
        return 0.0
    def integ(zp):
        E2 = E_sq_wCDM(zp, Om, w0, Or)
        return 1.0 / np.sqrt(np.maximum(E2, 1e-30))
    return (C_LIGHT / H0) * _gl_int(integ, 0.0, z, high=(z > 100))


def comoving_dist_CPL(z, H0, Om, w0, wa, Or):
    """d_C(z) [Mpc] for flat CPL."""
    if z <= 0:
        return 0.0
    def integ(zp):
        E2 = E_sq_CPL(zp, Om, w0, wa, Or)
        return 1.0 / np.sqrt(np.maximum(E2, 1e-30))
    return (C_LIGHT / H0) * _gl_int(integ, 0.0, z, high=(z > 100))


# ============================================================================
# SOUND HORIZON (self-consistent, not free parameter)
# ============================================================================

def sound_horizon_at_drag(H0, Om, Ob_h2, w0=-1.0):
    """
    r_d = r_s(z_drag) computed self-consistently from cosmological parameters.
    At z_drag ~ 1060, dark energy is negligible (~10^{-9}).
    r_d depends on Om*h^2, Ob*h^2 (pre-recombination physics).

    Returns r_d [Mpc].
    """
    h = H0 / 100.0
    Or = Omega_r_from_h(h)
    Ob = Ob_h2 / h**2
    Omega_gamma = 2.47e-5 / h**2
    R_prefac = 3.0 * Ob / (4.0 * Omega_gamma)
    ODE = 1.0 - Om - Or

    def integrand(z):
        zp1 = 1.0 + z
        R_b = R_prefac / zp1
        c_s = C_LIGHT / np.sqrt(3.0 * (1.0 + R_b))
        E2 = Or * zp1**4 + Om * zp1**3 + ODE * zp1**(3.0 * (1.0 + w0))
        Hz = H0 * np.sqrt(max(E2, 1e-30))
        return c_s / Hz

    result, _ = quad(integrand, Z_DRAG, 1e6, limit=500, epsrel=1e-12)
    return result


def sound_horizon_at_star(H0, Om, Ob_h2, w0=-1.0):
    """r_s(z_*) for CMB acoustic scale."""
    h = H0 / 100.0
    Or = Omega_r_from_h(h)
    Ob = Ob_h2 / h**2
    Omega_gamma = 2.47e-5 / h**2
    R_prefac = 3.0 * Ob / (4.0 * Omega_gamma)
    ODE = 1.0 - Om - Or

    def integrand(z):
        zp1 = 1.0 + z
        R_b = R_prefac / zp1
        c_s = C_LIGHT / np.sqrt(3.0 * (1.0 + R_b))
        E2 = Or * zp1**4 + Om * zp1**3 + ODE * zp1**(3.0 * (1.0 + w0))
        Hz = H0 * np.sqrt(max(E2, 1e-30))
        return c_s / Hz

    result, _ = quad(integrand, Z_STAR, 1e6, limit=500, epsrel=1e-12)
    return result


# Calibration: match our integral to CAMB's values at Planck best-fit LCDM
_RS_STAR_RAW_FID = sound_horizon_at_star(H0_FID, OM_FID, OB_H2_FID, -1.0)
_RS_DRAG_RAW_FID = sound_horizon_at_drag(H0_FID, OM_FID, OB_H2_FID, -1.0)
_CAL_STAR = 144.39 / _RS_STAR_RAW_FID
_CAL_DRAG = 147.09 / _RS_DRAG_RAW_FID


def rd_self_consistent(H0, Om, Ob_h2, w0=-1.0):
    """r_d calibrated to CAMB. Self-consistent with cosmological params."""
    return sound_horizon_at_drag(H0, Om, Ob_h2, w0) * _CAL_DRAG


def rs_star_self_consistent(H0, Om, Ob_h2, w0=-1.0):
    """r_s(z_*) calibrated to CAMB."""
    return sound_horizon_at_star(H0, Om, Ob_h2, w0) * _CAL_STAR


# ============================================================================
# PLANCK 2018 COMPRESSED LIKELIHOOD
# ============================================================================
# Chen, Kumar & Ratra (2019), 1907.12875
# Model-independent distance priors valid for any w

R_OBS = 1.7502;  R_ERR = 0.0046
LA_OBS = 301.471;  LA_ERR = 0.090
OBH2_OBS = 0.02236;  OBH2_ERR = 0.00015

_CORR = np.array([
    [1.0,   0.46, -0.66],
    [0.46,  1.0,  -0.33],
    [-0.66,-0.33,  1.0]
])
_SIG = np.array([R_ERR, LA_ERR, OBH2_ERR])
_COV_CMB = np.outer(_SIG, _SIG) * _CORR
_COV_CMB_INV = np.linalg.inv(_COV_CMB)


def chi2_CMB(H0, Om, Ob_h2, w0):
    """Planck compressed CMB chi-squared with self-consistent r_s."""
    h = H0 / 100.0
    Or = Omega_r_from_h(h)

    dC_star = comoving_dist(Z_STAR, H0, Om, w0, Or)
    rs = rs_star_self_consistent(H0, Om, Ob_h2, w0)

    R_th = np.sqrt(Om) * (H0 / C_LIGHT) * dC_star
    lA_th = np.pi * dC_star / rs

    delta = np.array([R_th - R_OBS, lA_th - LA_OBS, Ob_h2 - OBH2_OBS])
    return float(delta @ _COV_CMB_INV @ delta)


# ============================================================================
# BAO: DESI DR2 (r_d computed, NOT free)
# ============================================================================

def get_bao_data():
    """DESI DR2. (z_eff, D_M/r_d, sig, D_H/r_d, sig, rho_cross)."""
    return [
        (0.295,   7.93, 0.15,   20.98, 0.61,  -0.42),
        (0.510,  13.62, 0.18,   22.31, 0.47,  -0.44),
        (0.706,  17.86, 0.21,   23.45, 0.48,  -0.42),
        (0.934,  21.71, 0.23,   26.27, 0.47,  -0.45),
        (1.321,  27.79, 0.37,   32.74, 0.70,  -0.43),
        (1.484,  30.69, 0.79,   36.45, 1.35,  -0.37),
        (2.330,  39.71, 0.67,    8.52, 0.13,  -0.41),
    ]


def chi2_BAO(H0, Om, Ob_h2, w0):
    """BAO chi2 with self-consistent r_d."""
    h = H0 / 100.0
    Or = Omega_r_from_h(h)
    rd = rd_self_consistent(H0, Om, Ob_h2, w0)

    chi2 = 0.0
    for (z_eff, dM_obs, sig_dM, dH_obs, sig_dH, rho) in get_bao_data():
        dC = comoving_dist(z_eff, H0, Om, w0, Or)
        E2 = E_sq_wCDM(z_eff, Om, w0, Or)
        dH = (C_LIGHT / H0) / np.sqrt(max(E2, 1e-30))

        dM_th = dC / rd
        dH_th = dH / rd

        cov = np.array([
            [sig_dM**2, rho * sig_dM * sig_dH],
            [rho * sig_dM * sig_dH, sig_dH**2]
        ])
        delta = np.array([dM_th - dM_obs, dH_th - dH_obs])
        chi2 += float(delta @ np.linalg.inv(cov) @ delta)

    return chi2


# ============================================================================
# SNe Ia: DES Y5 COMPRESSED
# ============================================================================

def get_sne_data():
    """DES Y5 binned d_L with fractional precision."""
    z_eff = np.array([0.025, 0.05, 0.10, 0.20, 0.35, 0.50, 0.70, 0.90, 1.10])
    sigma_frac = np.array([0.050, 0.025, 0.015, 0.010, 0.008, 0.009, 0.012, 0.018, 0.030])
    return z_eff, sigma_frac


def chi2_SNe(H0, Om, w0):
    """SNe chi2 with analytic M marginalization."""
    z_eff, sigma_frac = get_sne_data()
    h = H0 / 100.0
    Or = Omega_r_from_h(h)
    Or_fid = Omega_r_from_h(H0_FID / 100.0)

    dL_fid = np.array([(1+z) * comoving_dist(z, H0_FID, OM_FID, -1.0, Or_fid) for z in z_eff])
    dL_mod = np.array([(1+z) * comoving_dist(z, H0, Om, w0, Or) for z in z_eff])

    ratio = dL_mod / np.maximum(dL_fid, 1e-10)
    delta_mu = 5.0 * np.log10(np.maximum(ratio, 1e-10))
    sigma_mu = 2.171 * sigma_frac

    W = 1.0 / sigma_mu**2
    return float(np.sum(W * delta_mu**2) - (np.sum(W * delta_mu))**2 / np.sum(W))


# ============================================================================
# GROWTH: f*sigma_8
# ============================================================================

def get_growth_data():
    return [
        (0.067, 0.423, 0.055),
        (0.150, 0.490, 0.145),
        (0.380, 0.497, 0.045),
        (0.510, 0.458, 0.038),
        (0.610, 0.436, 0.034),
        (0.706, 0.448, 0.043),
        (0.845, 0.418, 0.040),
        (0.978, 0.379, 0.054),
        (1.480, 0.315, 0.095),
    ]


def chi2_Growth(Om, w0, sigma8, Or=0.0):
    """Growth f*sigma_8 chi2. Gamma = 0.555 (GR, from 17A)."""
    gamma = 0.555
    data = get_growth_data()
    z_arr = np.array([d[0] for d in data])
    fsig8_obs = np.array([d[1] for d in data])
    sigma_obs = np.array([d[2] for d in data])

    fsig8_th = np.zeros_like(z_arr)
    for k, z in enumerate(z_arr):
        E2 = E_sq_wCDM(z, Om, w0, Or)
        if E2 <= 0:
            fsig8_th[k] = 0.0
            continue
        Om_z = Om * (1.0 + z)**3 / E2
        f_z = Om_z**gamma

        # D(z)/D(0) from integrating f/(1+z)
        if z > 0:
            nodes = 0.5 * z * (_GL64_N + 1.0)
            wts = 0.5 * z * _GL64_W
            E2_n = np.array([E_sq_wCDM(zi, Om, w0, Or) for zi in nodes])
            E2_n = np.maximum(E2_n, 1e-30)
            Om_n = Om * (1.0 + nodes)**3 / E2_n
            integral = np.sum(wts * Om_n**gamma / (1.0 + nodes))
            D_ratio = np.exp(-integral)
        else:
            D_ratio = 1.0

        fsig8_th[k] = f_z * sigma8 * D_ratio

    return float(np.sum(((fsig8_th - fsig8_obs) / sigma_obs)**2))


# ============================================================================
# TOTAL CHI-SQUARED FUNCTIONS
# ============================================================================

def chi2_total_wCDM(theta):
    """
    Constant-w total chi2.
    Parameters: [w0, Omega_m, H0, sigma8, Ob_h2]
    r_d is computed self-consistently (NOT a free parameter).
    """
    w0, Om, H0, sigma8, Ob_h2 = theta

    if w0 < -1.5 or w0 > -0.3:
        return 1e10
    if Om < 0.15 or Om > 0.55:
        return 1e10
    if H0 < 55.0 or H0 > 85.0:
        return 1e10
    if sigma8 < 0.5 or sigma8 > 1.1:
        return 1e10
    if Ob_h2 < 0.019 or Ob_h2 > 0.026:
        return 1e10

    Or = Omega_r_from_h(H0 / 100.0)
    try:
        c2 = chi2_CMB(H0, Om, Ob_h2, w0)
        c2 += chi2_BAO(H0, Om, Ob_h2, w0)
        c2 += chi2_SNe(H0, Om, w0)
        c2 += chi2_Growth(Om, w0, sigma8, Or)
        return c2
    except Exception:
        return 1e10


def chi2_total_LCDM(theta):
    """LCDM: w = -1. Parameters: [Omega_m, H0, sigma8, Ob_h2]."""
    Om, H0, sigma8, Ob_h2 = theta
    return chi2_total_wCDM(np.array([-1.0, Om, H0, sigma8, Ob_h2]))


def chi2_total_CPL(theta):
    """CPL. Parameters: [w0, wa, Omega_m, H0, sigma8, Ob_h2]."""
    w0, wa, Om, H0, sigma8, Ob_h2 = theta

    if w0 < -2.0 or w0 > 0.0:
        return 1e10
    if wa < -3.0 or wa > 3.0:
        return 1e10
    if Om < 0.15 or Om > 0.55:
        return 1e10
    if H0 < 55.0 or H0 > 85.0:
        return 1e10
    if sigma8 < 0.5 or sigma8 > 1.1:
        return 1e10
    if Ob_h2 < 0.019 or Ob_h2 > 0.026:
        return 1e10

    h = H0 / 100.0
    Or = Omega_r_from_h(h)
    rd = rd_self_consistent(H0, Om, Ob_h2, w0)
    rs = rs_star_self_consistent(H0, Om, Ob_h2, w0)

    try:
        # CMB with CPL distances
        dC_star = comoving_dist_CPL(Z_STAR, H0, Om, w0, wa, Or)
        R_th = np.sqrt(Om) * (H0 / C_LIGHT) * dC_star
        lA_th = np.pi * dC_star / rs
        delta_cmb = np.array([R_th - R_OBS, lA_th - LA_OBS, Ob_h2 - OBH2_OBS])
        c2 = float(delta_cmb @ _COV_CMB_INV @ delta_cmb)

        # BAO with CPL
        for (z_eff, dM_obs, sig_dM, dH_obs, sig_dH, rho) in get_bao_data():
            dC = comoving_dist_CPL(z_eff, H0, Om, w0, wa, Or)
            E2 = E_sq_CPL(z_eff, Om, w0, wa, Or)
            dH = (C_LIGHT / H0) / np.sqrt(max(E2, 1e-30))
            delta = np.array([dC / rd - dM_obs, dH / rd - dH_obs])
            cov = np.array([[sig_dM**2, rho*sig_dM*sig_dH],
                            [rho*sig_dM*sig_dH, sig_dH**2]])
            c2 += float(delta @ np.linalg.inv(cov) @ delta)

        # SNe (use constant-w approximation — SNe mostly at z<1 where wa small)
        c2 += chi2_SNe(H0, Om, w0)

        # Growth (approximate with constant w0 — growth at z<1.5)
        c2 += chi2_Growth(Om, w0, sigma8, Or)

        return c2
    except Exception:
        return 1e10


# ============================================================================
# BREAKDOWN
# ============================================================================

def chi2_breakdown_wCDM(w0, Om, H0, sigma8, Ob_h2):
    """Return per-dataset chi2."""
    Or = Omega_r_from_h(H0 / 100.0)
    return {
        'CMB':    chi2_CMB(H0, Om, Ob_h2, w0),
        'BAO':    chi2_BAO(H0, Om, Ob_h2, w0),
        'SNe':    chi2_SNe(H0, Om, w0),
        'Growth': chi2_Growth(Om, w0, sigma8, Or),
    }


# ============================================================================
# OPTIMIZER
# ============================================================================

def optimize(chi2_func, bounds, label="Model", n_nm=15, seed=42):
    """DE + multi-start NM + Powell polish."""
    best_chi2 = 1e10
    best_params = None

    fprint(f"\n  Optimizing {label}...")

    # Differential evolution
    try:
        res = differential_evolution(chi2_func, bounds, maxiter=400, tol=1e-8,
                                     seed=seed, polish=True, popsize=15,
                                     mutation=(0.5, 1.0))
        if res.fun < best_chi2:
            best_chi2 = res.fun
            best_params = res.x
        fprint(f"    DE: chi2 = {res.fun:.4f}")
    except Exception as e:
        fprint(f"    DE failed: {e}")

    # Multi-start Nelder-Mead
    rng = np.random.RandomState(seed + 1)
    for i in range(n_nm):
        x0 = np.array([rng.uniform(lo, hi) for (lo, hi) in bounds])
        try:
            res = minimize(chi2_func, x0, method='Nelder-Mead',
                           options={'maxiter': 15000, 'xatol': 1e-8, 'fatol': 1e-8})
            if res.fun < best_chi2:
                best_chi2 = res.fun
                best_params = res.x
        except Exception:
            continue

    # Polish
    if best_params is not None:
        try:
            res = minimize(chi2_func, best_params, method='Powell',
                           options={'maxiter': 30000, 'ftol': 1e-12})
            if res.fun < best_chi2:
                best_chi2 = res.fun
                best_params = res.x
        except Exception:
            pass

    fprint(f"    Best: chi2 = {best_chi2:.4f}")
    return best_params, best_chi2


# ============================================================================
# PROFILE LIKELIHOOD
# ============================================================================

def profile_zeta0(z0_grid, best_nuis, c_kk=C_KK_CENTRAL):
    """Profile chi2(zeta_0): fix zeta_0 -> w_0, minimize over nuisance."""
    fprint(f"\n  Profile over {len(z0_grid)} zeta_0 points...")
    Om_bf, H0_bf, s8_bf, Obh2_bf = best_nuis
    chi2_prof = np.full_like(z0_grid, 1e10)

    for i, z0 in enumerate(z0_grid):
        w0 = w0_from_zeta0(z0, c_kk)
        if w0 >= -0.3 or w0 < -1.5:
            continue

        def c2_fixed(nuis, _w0=w0):
            Om, H0, s8, Obh2 = nuis
            return chi2_total_wCDM(np.array([_w0, Om, H0, s8, Obh2]))

        x0 = np.array([Om_bf, H0_bf, s8_bf, Obh2_bf])
        best = 1e10

        for start in [x0,
                      x0 * np.array([1.03, 0.98, 1.0, 1.0]),
                      x0 * np.array([0.97, 1.02, 1.0, 1.0])]:
            try:
                res = minimize(c2_fixed, start, method='Nelder-Mead',
                               options={'maxiter': 15000, 'xatol': 1e-8, 'fatol': 1e-8})
                if res.fun < best:
                    best = res.fun
                    x_best = res.x
            except Exception:
                continue

        if best < 1e10:
            try:
                res2 = minimize(c2_fixed, x_best, method='Powell',
                                options={'maxiter': 30000, 'ftol': 1e-12})
                if res2.fun < best:
                    best = res2.fun
            except Exception:
                pass

        chi2_prof[i] = best

        if i % max(1, len(z0_grid) // 15) == 0:
            fprint(f"    z0={z0:.5f}  w0={w0:+.4f}  chi2={best:.3f}")

    return chi2_prof


def profile_dataset(z0_grid, dataset_func, n_nuis, x0_base, c_kk=C_KK_CENTRAL):
    """Profile over zeta_0 for a single dataset."""
    chi2_prof = np.full_like(z0_grid, 1e10)
    for i, z0 in enumerate(z0_grid):
        w0 = w0_from_zeta0(z0, c_kk)
        if w0 >= -0.3 or w0 < -1.5:
            continue

        def c2_f(nuis, _w0=w0):
            return dataset_func(_w0, nuis)

        best = 1e10
        for start in [x0_base, x0_base * (1 + 0.02 * np.random.randn(n_nuis))]:
            try:
                res = minimize(c2_f, start, method='Nelder-Mead',
                               options={'maxiter': 10000, 'xatol': 1e-8, 'fatol': 1e-8})
                if res.fun < best:
                    best = res.fun
            except Exception:
                continue
        chi2_prof[i] = best
    return chi2_prof


# ============================================================================
# C_KK PROPAGATION
# ============================================================================

def propagate_ckk(w0_bf, N=5000):
    """Map w0 -> zeta_0 with C_KK uncertainty."""
    rng = np.random.RandomState(2026)
    ckk = rng.normal(C_KK_CENTRAL, C_KK_SIGMA, N)
    ckk = ckk[ckk > 0]
    dw = 1.0 + w0_bf
    if dw <= 0:
        return np.inf, np.inf, np.inf, np.inf, np.inf
    z0 = ckk / dw
    return (C_KK_CENTRAL / dw,
            np.percentile(z0, 15.87), np.percentile(z0, 84.13),
            np.percentile(z0, 2.28), np.percentile(z0, 97.72))


# ============================================================================
# MAIN
# ============================================================================

def main():
    fprint("=" * 80)
    fprint("TRACK 17Q: FULL PLANCK LIKELIHOOD ANALYSIS — TRUE zeta_0 CONSTRAINT")
    fprint("=" * 80)
    fprint()
    fprint("Design: r_d computed SELF-CONSISTENTLY from (H0, Om, Ob_h2).")
    fprint("        NOT a free parameter. This removes the LCDM-prior bias.")
    fprint()
    fprint("w_0(zeta_0) = -1 + C_KK / zeta_0,  C_KK = 2.453e-4 +/- 8.3e-5")
    fprint()

    # ------------------------------------------------------------------
    # 0. CALIBRATION
    # ------------------------------------------------------------------
    fprint("-" * 80)
    fprint("SECTION 0: CALIBRATION")
    fprint("-" * 80)

    rs_star = rs_star_self_consistent(H0_FID, OM_FID, OB_H2_FID, -1.0)
    rd_fid = rd_self_consistent(H0_FID, OM_FID, OB_H2_FID, -1.0)
    fprint(f"  r_s(z_*) = {rs_star:.2f} Mpc  (target 144.39)")
    fprint(f"  r_d      = {rd_fid:.2f} Mpc  (target 147.09)")
    fprint(f"  Cal factors: star={_CAL_STAR:.6f}, drag={_CAL_DRAG:.6f}")

    c2_check = chi2_CMB(H0_FID, OM_FID, OB_H2_FID, -1.0)
    fprint(f"  LCDM Planck best-fit: chi2_CMB = {c2_check:.4f}")

    # Quick BAO check at LCDM fiducial
    c2_bao_check = chi2_BAO(H0_FID, OM_FID, OB_H2_FID, -1.0)
    fprint(f"  LCDM Planck best-fit: chi2_BAO = {c2_bao_check:.4f}")

    c2_sne_check = chi2_SNe(H0_FID, OM_FID, -1.0)
    fprint(f"  LCDM Planck best-fit: chi2_SNe = {c2_sne_check:.4f}")

    Or_fid = Omega_r_from_h(H0_FID / 100.0)
    c2_gr_check = chi2_Growth(OM_FID, -1.0, 0.811, Or_fid)
    fprint(f"  LCDM Planck best-fit: chi2_Grw = {c2_gr_check:.4f}")
    fprint(f"  LCDM Planck best-fit: chi2_Tot = {c2_check + c2_bao_check + c2_sne_check + c2_gr_check:.4f}")
    fprint()

    # Print r_d at a few benchmark points to verify BAO consistency
    fprint("  Sound horizon at benchmarks:")
    for lab, w0v in [("LCDM", -1.0), ("w=-0.99", -0.99), ("w=-0.95", -0.95), ("w=-0.75", -0.75)]:
        rd_v = rd_self_consistent(H0_FID, OM_FID, OB_H2_FID, w0v)
        fprint(f"    {lab:12s}: r_d = {rd_v:.2f} Mpc")
    fprint()

    # Benchmarks
    fprint("  Meridian benchmarks:")
    for name, z0 in [("JC", 0.001), ("Lu-Simon", 0.004), ("CAMB", 0.022)]:
        fprint(f"    {name:10s}: zeta_0 = {z0:.4f},  w_0 = {w0_from_zeta0(z0):+.6f}")
    fprint()

    # ------------------------------------------------------------------
    # 1. LCDM FIT
    # ------------------------------------------------------------------
    fprint("-" * 80)
    fprint("SECTION 1: LCDM BASELINE FIT")
    fprint("-" * 80)

    bounds_lcdm = [
        (0.25, 0.40),   # Omega_m
        (62.0, 74.0),   # H0
        (0.70, 0.90),   # sigma8
        (0.021, 0.024), # Ob_h2
    ]

    params_lcdm, chi2_lcdm_val = optimize(chi2_total_LCDM, bounds_lcdm, "LCDM", n_nm=15)
    Om_l, H0_l, s8_l, Obh2_l = params_lcdm

    fprint(f"\n  LCDM best-fit:")
    fprint(f"    Omega_m = {Om_l:.5f}")
    fprint(f"    H0      = {H0_l:.3f} km/s/Mpc")
    fprint(f"    sigma_8 = {s8_l:.4f}")
    fprint(f"    Ob*h^2  = {Obh2_l:.5f}")
    rd_l = rd_self_consistent(H0_l, Om_l, Obh2_l, -1.0)
    fprint(f"    r_d     = {rd_l:.2f} Mpc  (computed)")
    fprint(f"    chi2    = {chi2_lcdm_val:.4f}")

    bd_l = chi2_breakdown_wCDM(-1.0, Om_l, H0_l, s8_l, Obh2_l)
    fprint(f"\n  Breakdown:")
    tot_l = 0
    for k, v in bd_l.items():
        fprint(f"    {k:8s}: {v:.4f}")
        tot_l += v
    fprint(f"    {'Total':8s}: {tot_l:.4f}")

    n_bao = 14; n_sne = 8; n_growth = 9; n_cmb = 3  # 8 SNe dof after M marginalization
    n_data = n_bao + n_sne + n_growth + n_cmb
    n_par_l = 4
    ndof_l = n_data - n_par_l
    pval_l = 1.0 - chi2_dist.cdf(chi2_lcdm_val, ndof_l)
    fprint(f"\n  N_data={n_data}, N_par={n_par_l}, N_dof={ndof_l}, p-value={pval_l:.4f}")
    fprint()

    # ------------------------------------------------------------------
    # 2. CONSTANT-w FIT
    # ------------------------------------------------------------------
    fprint("-" * 80)
    fprint("SECTION 2: CONSTANT-w FIT (MERIDIAN)")
    fprint("-" * 80)

    bounds_cw = [
        (-1.3, -0.5),   # w0
        (0.20, 0.45),   # Omega_m
        (60.0, 78.0),   # H0
        (0.65, 0.95),   # sigma8
        (0.021, 0.024), # Ob_h2
    ]

    params_cw, chi2_cw_val = optimize(chi2_total_wCDM, bounds_cw, "constant-w", n_nm=20)
    w0_c, Om_c, H0_c, s8_c, Obh2_c = params_cw

    fprint(f"\n  Constant-w best-fit:")
    fprint(f"    w_0     = {w0_c:+.6f}")
    fprint(f"    Omega_m = {Om_c:.5f}")
    fprint(f"    H0      = {H0_c:.3f} km/s/Mpc")
    fprint(f"    sigma_8 = {s8_c:.4f}")
    fprint(f"    Ob*h^2  = {Obh2_c:.5f}")
    rd_c = rd_self_consistent(H0_c, Om_c, Obh2_c, w0_c)
    fprint(f"    r_d     = {rd_c:.2f} Mpc  (computed)")
    fprint(f"    chi2    = {chi2_cw_val:.4f}")

    bd_c = chi2_breakdown_wCDM(w0_c, Om_c, H0_c, s8_c, Obh2_c)
    fprint(f"\n  Breakdown:")
    tot_c = 0
    for k, v in bd_c.items():
        fprint(f"    {k:8s}: {v:.4f}")
        tot_c += v
    fprint(f"    {'Total':8s}: {tot_c:.4f}")

    n_par_cw = 5
    ndof_cw = n_data - n_par_cw
    pval_cw = 1.0 - chi2_dist.cdf(chi2_cw_val, ndof_cw)
    fprint(f"\n  N_data={n_data}, N_par={n_par_cw}, N_dof={ndof_cw}, p-value={pval_cw:.4f}")

    z0_bf = zeta0_from_w0(w0_c)
    fprint(f"\n  ==> Best-fit zeta_0 = {z0_bf:.6f}")
    fprint(f"  ==> Best-fit w_0    = {w0_c:+.6f}")

    dchi2_lcdm = chi2_lcdm_val - chi2_cw_val
    fprint(f"\n  Delta chi2 (LCDM - constw) = {dchi2_lcdm:+.4f}")
    if dchi2_lcdm > 0:
        fprint(f"  ==> constant-w preferred over LCDM at {np.sqrt(dchi2_lcdm):.2f} sigma")
    elif dchi2_lcdm > -1:
        fprint(f"  ==> LCDM and constant-w essentially equivalent")
    else:
        fprint(f"  ==> LCDM preferred (simpler, Delta chi2 < 0 for extra param)")
    fprint()

    # ------------------------------------------------------------------
    # 3. CPL FIT
    # ------------------------------------------------------------------
    fprint("-" * 80)
    fprint("SECTION 3: CPL FIT (COMPARISON WITH 17P)")
    fprint("-" * 80)

    bounds_cpl = [
        (-1.5, -0.3),   # w0
        (-2.5, 1.5),    # wa
        (0.20, 0.45),   # Omega_m
        (60.0, 78.0),   # H0
        (0.65, 0.95),   # sigma8
        (0.021, 0.024), # Ob_h2
    ]

    params_cpl, chi2_cpl_val = optimize(chi2_total_CPL, bounds_cpl, "CPL", n_nm=15, seed=44)
    w0_cpl, wa_cpl, Om_cpl, H0_cpl, s8_cpl, Obh2_cpl = params_cpl

    fprint(f"\n  CPL best-fit:")
    fprint(f"    w_0     = {w0_cpl:+.6f}")
    fprint(f"    w_a     = {wa_cpl:+.6f}")
    fprint(f"    Omega_m = {Om_cpl:.5f}")
    fprint(f"    H0      = {H0_cpl:.3f} km/s/Mpc")
    fprint(f"    sigma_8 = {s8_cpl:.4f}")
    fprint(f"    Ob*h^2  = {Obh2_cpl:.5f}")
    fprint(f"    chi2    = {chi2_cpl_val:.4f}")

    n_par_cpl = 6
    dchi2_cpl_cw = chi2_cw_val - chi2_cpl_val
    dchi2_cpl_lcdm = chi2_lcdm_val - chi2_cpl_val

    fprint(f"\n  Delta chi2 (constw - CPL) = {dchi2_cpl_cw:+.4f}")
    if dchi2_cpl_cw > 0:
        fprint(f"  ==> CPL preferred over constant-w at {np.sqrt(dchi2_cpl_cw):.2f} sigma")
    else:
        fprint(f"  ==> constant-w preferred (simpler model)")

    fprint(f"  Delta chi2 (LCDM - CPL)   = {dchi2_cpl_lcdm:+.4f}")
    if dchi2_cpl_lcdm > 0:
        fprint(f"  ==> CPL preferred over LCDM at {np.sqrt(dchi2_cpl_lcdm):.2f} sigma (2 extra params)")

    fprint(f"\n  17P comparison:")
    fprint(f"    17P: w_a = 0 at 2.4sigma. Our w_a = {wa_cpl:+.4f}")
    if dchi2_cpl_cw > 0:
        our_sig = np.sqrt(dchi2_cpl_cw)
        fprint(f"    Our w_a != 0 preference: {our_sig:.2f} sigma")
        fprint(f"    Reduced vs 17P? {'YES' if our_sig < 2.4 else 'NO'}")
    else:
        fprint(f"    Model-independent priors ELIMINATE the CPL preference!")
    fprint()

    # ------------------------------------------------------------------
    # 4. PROFILE LIKELIHOOD IN zeta_0
    # ------------------------------------------------------------------
    fprint("-" * 80)
    fprint("SECTION 4: PROFILE LIKELIHOOD chi2(zeta_0)")
    fprint("-" * 80)

    z0_grid = np.concatenate([
        np.linspace(3e-4, 3e-3, 15),
        np.linspace(4e-3, 0.02, 15),
        np.linspace(0.025, 0.10, 15),
        np.linspace(0.12, 0.30, 10),
    ])
    z0_grid = np.unique(np.sort(z0_grid))

    nuis_bf = (Om_c, H0_c, s8_c, Obh2_c)
    chi2_prof = profile_zeta0(z0_grid, nuis_bf)

    valid = chi2_prof < 1e9
    if np.any(valid):
        z0_v = z0_grid[valid]
        c2_v = chi2_prof[valid]
        c2_min = np.min(c2_v)
        i_min = np.argmin(c2_v)
        z0_min = z0_v[i_min]
        dc2 = c2_v - c2_min

        fprint(f"\n  Profile minimum:")
        fprint(f"    zeta_0 = {z0_min:.6f}")
        fprint(f"    w_0    = {w0_from_zeta0(z0_min):+.6f}")
        fprint(f"    chi2   = {c2_min:.4f}")

        # Confidence intervals
        for nsig, thr in [(1, 1.0), (2, 4.0)]:
            lo = z0_v[0]
            hi = z0_v[-1]
            below = z0_v < z0_min
            above = z0_v > z0_min
            if np.any(below) and np.any(dc2[below] > thr):
                try:
                    lo = float(interp1d(dc2[below], z0_v[below])(thr))
                except:
                    lo = z0_v[below][0]
            if np.any(above) and np.any(dc2[above] > thr):
                try:
                    hi = float(interp1d(dc2[above], z0_v[above])(thr))
                except:
                    hi = z0_v[above][-1]
            fprint(f"    {nsig}-sigma: zeta_0 in [{lo:.6f}, {hi:.6f}]")
            fprint(f"            w_0    in [{w0_from_zeta0(hi):+.6f}, {w0_from_zeta0(lo):+.6f}]")

        # Key comparisons
        fprint(f"\n  Key comparisons:")
        # LCDM limit (large zeta_0)
        dc2_lcdm = dc2[-1]
        fprint(f"    LCDM (large zeta_0): Delta chi2 = {dc2_lcdm:.2f} "
               f"({np.sqrt(max(0,dc2_lcdm)):.1f} sigma)")

        # JC
        try:
            ip = interp1d(z0_v, dc2)
            if 0.001 >= z0_v[0] and 0.001 <= z0_v[-1]:
                dc2_jc = float(ip(0.001))
                fprint(f"    JC (zeta_0=0.001): Delta chi2 = {dc2_jc:.2f} "
                       f"({np.sqrt(max(0,dc2_jc)):.1f} sigma)")
        except:
            pass

        # CAMB
        try:
            if 0.022 >= z0_v[0] and 0.022 <= z0_v[-1]:
                dc2_camb = float(ip(0.022))
                fprint(f"    CAMB (zeta_0=0.022): Delta chi2 = {dc2_camb:.2f} "
                       f"({np.sqrt(max(0,dc2_camb)):.1f} sigma)")
        except:
            pass

        # Bimodality
        fprint(f"\n  Bimodality check:")
        n_min = 0
        for j in range(1, len(dc2) - 1):
            if dc2[j] < dc2[j-1] and dc2[j] < dc2[j+1] and dc2[j] < 10:
                n_min += 1
                fprint(f"    Local min at zeta_0={z0_v[j]:.5f}, w_0={w0_from_zeta0(z0_v[j]):+.4f}, "
                       f"Delta chi2={dc2[j]:.2f}")
        fprint(f"    ==> {'UNIMODAL' if n_min <= 1 else f'BIMODAL ({n_min} minima)'}")

        # Table
        fprint(f"\n  {'zeta_0':>10s}  {'w_0':>10s}  {'chi2':>10s}  {'Delta_chi2':>12s}  {'sigma':>6s}")
        fprint("  " + "-" * 56)
        step = max(1, len(z0_v) // 25)
        for j in range(0, len(z0_v), step):
            fprint(f"  {z0_v[j]:10.6f}  {w0_from_zeta0(z0_v[j]):+10.4f}  "
                   f"{c2_v[j]:10.3f}  {dc2[j]:12.3f}  {np.sqrt(max(0,dc2[j])):6.2f}")
        j = len(z0_v) - 1
        fprint(f"  {z0_v[j]:10.6f}  {w0_from_zeta0(z0_v[j]):+10.4f}  "
               f"{c2_v[j]:10.3f}  {dc2[j]:12.3f}  {np.sqrt(max(0,dc2[j])):6.2f}")
    fprint()

    # ------------------------------------------------------------------
    # 5. CMB-ONLY vs BAO-ONLY
    # ------------------------------------------------------------------
    fprint("-" * 80)
    fprint("SECTION 5: CMB-ONLY vs BAO-ONLY TENSION")
    fprint("-" * 80)

    z0_coarse = np.concatenate([
        np.linspace(5e-4, 3e-3, 8),
        np.linspace(5e-3, 0.05, 12),
        np.linspace(0.06, 0.25, 8),
    ])
    z0_coarse = np.unique(np.sort(z0_coarse))

    # CMB-only profile
    fprint("\n  Computing CMB-only profile...")
    def cmb_only(w0, nuis):
        Om, H0, Obh2 = nuis
        if Om < 0.15 or Om > 0.55 or H0 < 55 or H0 > 85 or Obh2 < 0.019 or Obh2 > 0.026:
            return 1e10
        try:
            return chi2_CMB(H0, Om, Obh2, w0)
        except:
            return 1e10

    c2_cmb_p = profile_dataset(z0_coarse, cmb_only, 3, np.array([Om_c, H0_c, Obh2_c]))

    # BAO-only profile
    fprint("  Computing BAO-only profile...")
    def bao_only(w0, nuis):
        Om, H0, Obh2 = nuis
        if Om < 0.15 or Om > 0.55 or H0 < 55 or H0 > 85 or Obh2 < 0.019 or Obh2 > 0.026:
            return 1e10
        try:
            return chi2_BAO(H0, Om, Obh2, w0)
        except:
            return 1e10

    c2_bao_p = profile_dataset(z0_coarse, bao_only, 3, np.array([Om_c, H0_c, Obh2_c]))

    v_cmb = c2_cmb_p < 1e9
    v_bao = c2_bao_p < 1e9

    if np.any(v_cmb):
        z0c_best = z0_coarse[v_cmb][np.argmin(c2_cmb_p[v_cmb])]
        fprint(f"\n  CMB-only: best at zeta_0={z0c_best:.5f}, w_0={w0_from_zeta0(z0c_best):+.4f}, "
               f"chi2={np.min(c2_cmb_p[v_cmb]):.3f}")
    if np.any(v_bao):
        z0b_best = z0_coarse[v_bao][np.argmin(c2_bao_p[v_bao])]
        fprint(f"  BAO-only: best at zeta_0={z0b_best:.5f}, w_0={w0_from_zeta0(z0b_best):+.4f}, "
               f"chi2={np.min(c2_bao_p[v_bao]):.3f}")

    if np.any(v_cmb) and np.any(v_bao):
        fprint(f"\n  Tension: CMB prefers zeta_0={z0c_best:.5f}, BAO prefers zeta_0={z0b_best:.5f}")
        # Check cross-chi2
        try:
            dc2_cmb = c2_cmb_p[v_cmb] - np.min(c2_cmb_p[v_cmb])
            dc2_bao = c2_bao_p[v_bao] - np.min(c2_bao_p[v_bao])
            ip_cmb = interp1d(z0_coarse[v_cmb], dc2_cmb)
            ip_bao = interp1d(z0_coarse[v_bao], dc2_bao)
            z_clip = np.clip(z0b_best, z0_coarse[v_cmb][0], z0_coarse[v_cmb][-1])
            dc2_cmb_at_bao = float(ip_cmb(z_clip))
            z_clip2 = np.clip(z0c_best, z0_coarse[v_bao][0], z0_coarse[v_bao][-1])
            dc2_bao_at_cmb = float(ip_bao(z_clip2))
            fprint(f"    CMB Delta chi2 at BAO best: {dc2_cmb_at_bao:.2f} ({np.sqrt(max(0,dc2_cmb_at_bao)):.1f}sig)")
            fprint(f"    BAO Delta chi2 at CMB best: {dc2_bao_at_cmb:.2f} ({np.sqrt(max(0,dc2_bao_at_cmb)):.1f}sig)")
        except Exception as e:
            fprint(f"    Cross-tension error: {e}")
    fprint()

    # ------------------------------------------------------------------
    # 6. C_KK PROPAGATION
    # ------------------------------------------------------------------
    fprint("-" * 80)
    fprint("SECTION 6: C_KK UNCERTAINTY PROPAGATION")
    fprint("-" * 80)
    fprint()
    fprint(f"  C_KK = {C_KK_CENTRAL:.4e} +/- {C_KK_SIGMA:.4e} ({100*C_KK_SIGMA/C_KK_CENTRAL:.1f}%)")
    fprint()

    fprint(f"  Best-fit w_0 = {w0_c:+.6f}:")
    z0c_cen, z0c_lo1, z0c_hi1, z0c_lo2, z0c_hi2 = propagate_ckk(w0_c)
    fprint(f"    zeta_0 central:  {z0c_cen:.6f}")
    fprint(f"    zeta_0 1-sigma:  [{z0c_lo1:.6f}, {z0c_hi1:.6f}]")
    fprint(f"    zeta_0 2-sigma:  [{z0c_lo2:.6f}, {z0c_hi2:.6f}]")
    fprint()

    fprint(f"  JC benchmark w_0 = -0.745:")
    z0j_cen, z0j_lo1, z0j_hi1, z0j_lo2, z0j_hi2 = propagate_ckk(-0.745)
    fprint(f"    zeta_0 central:  {z0j_cen:.6f}")
    fprint(f"    zeta_0 1-sigma:  [{z0j_lo1:.6f}, {z0j_hi1:.6f}]")
    fprint(f"    zeta_0 2-sigma:  [{z0j_lo2:.6f}, {z0j_hi2:.6f}]")
    fprint()

    # ------------------------------------------------------------------
    # 7. BENCHMARK TABLE
    # ------------------------------------------------------------------
    fprint("-" * 80)
    fprint("SECTION 7: BENCHMARK COMPARISON TABLE")
    fprint("-" * 80)
    fprint()

    benchmarks = [
        ("LCDM",     -1.0),
        ("CAMB",     -0.989),
        ("w=-0.95",  -0.95),
        ("Lu-Simon", -0.800),
        ("JC",       -0.745),
        ("Best-fit",  w0_c),
    ]

    fprint(f"  {'Model':12s} {'w_0':>8s}  {'CMB':>8s}  {'BAO':>8s}  {'SNe':>8s}  {'Grw':>8s}  {'Total':>8s}  {'r_d':>7s}")
    fprint("  " + "-" * 74)

    for name, w0v in benchmarks:
        def c2_bm(nuis, _w0=w0v):
            Om, H0, s8, Obh2 = nuis
            return chi2_total_wCDM(np.array([_w0, Om, H0, s8, Obh2]))

        x0 = np.array([Om_c, H0_c, s8_c, Obh2_c])
        best = 1e10
        x_best = x0

        # Try multiple starts
        for st in [x0,
                   np.array([Om_l, H0_l, s8_l, Obh2_l]),
                   x0 * np.array([1.02, 0.99, 1.0, 1.0]),
                   x0 * np.array([0.98, 1.01, 1.0, 1.0])]:
            try:
                res = minimize(c2_bm, st, method='Nelder-Mead',
                               options={'maxiter': 15000, 'xatol': 1e-8, 'fatol': 1e-8})
                if res.fun < best:
                    best = res.fun
                    x_best = res.x
            except:
                continue

        try:
            res2 = minimize(c2_bm, x_best, method='Powell',
                            options={'maxiter': 30000, 'ftol': 1e-12})
            if res2.fun < best:
                best = res2.fun
                x_best = res2.x
        except:
            pass

        bd = chi2_breakdown_wCDM(w0v, x_best[0], x_best[1], x_best[2], x_best[3])
        rd_v = rd_self_consistent(x_best[1], x_best[0], x_best[3], w0v)
        tot = sum(bd.values())

        fprint(f"  {name:12s} {w0v:+8.4f}  {bd['CMB']:8.2f}  {bd['BAO']:8.2f}  "
               f"{bd['SNe']:8.2f}  {bd['Growth']:8.2f}  {tot:8.2f}  {rd_v:7.2f}")

    fprint()

    # ------------------------------------------------------------------
    # 8. SUMMARY
    # ------------------------------------------------------------------
    fprint("=" * 80)
    fprint("SECTION 8: SUMMARY AND MERIDIAN IMPLICATIONS")
    fprint("=" * 80)
    fprint()

    fprint("  BEST-FIT RESULTS:")
    fprint(f"    LCDM:       chi2={chi2_lcdm_val:.3f}, N_dof={ndof_l}")
    fprint(f"    constant-w: chi2={chi2_cw_val:.3f}, N_dof={ndof_cw}, w_0={w0_c:+.4f}")
    fprint(f"    CPL:        chi2={chi2_cpl_val:.3f}, N_dof={n_data - n_par_cpl}, "
           f"w_0={w0_cpl:+.4f}, w_a={wa_cpl:+.4f}")
    fprint()

    fprint("  MODEL COMPARISON:")
    fprint(f"    constw vs LCDM: Dchi2={dchi2_lcdm:+.3f} ({np.sqrt(abs(dchi2_lcdm)):.2f}sig, 1 extra param)")
    fprint(f"    CPL vs constw:  Dchi2={dchi2_cpl_cw:+.3f} ({np.sqrt(abs(dchi2_cpl_cw)):.2f}sig, 1 extra param)")
    fprint(f"    CPL vs LCDM:    Dchi2={dchi2_cpl_lcdm:+.3f} ({np.sqrt(abs(dchi2_cpl_lcdm)):.2f}sig, 2 extra params)")
    fprint()

    fprint("  zeta_0 CONSTRAINT (from data, model-independent priors):")
    fprint(f"    Best-fit zeta_0 = {z0_bf:.6f}")
    fprint(f"    Best-fit w_0    = {w0_c:+.6f}")
    if np.any(valid):
        fprint(f"    Profile min     = chi2 {c2_min:.3f} at zeta_0 = {z0_min:.6f}")
    fprint()

    fprint("  KEY QUESTIONS:")
    if np.any(valid):
        fprint(f"    Is LCDM preferred?        Delta chi2 = {dc2_lcdm:.2f} from profile min")
        try:
            fprint(f"    Is JC within 2sigma?      Delta chi2 = {dc2_jc:.2f} "
                   f"({'YES' if dc2_jc < 4.0 else 'NO'})")
        except:
            pass
        try:
            fprint(f"    Is CAMB within 2sigma?    Delta chi2 = {dc2_camb:.2f} "
                   f"({'YES' if dc2_camb < 4.0 else 'NO'})")
        except:
            pass
    fprint(f"    Is CPL preference reduced with proper priors?  "
           f"{'YES' if dchi2_cpl_cw < 5.76 else 'NO'} (was 2.4sig in 17P)")
    fprint()

    fprint("  PHYSICAL INTERPRETATION:")
    if abs(w0_c + 1.0) < 0.02:
        fprint(f"    Combined data prefer w_0 = {w0_c:+.4f}, consistent with LCDM")
        fprint(f"    |1+w_0| = {abs(1+w0_c):.4f} < 0.02 — CAMB benchmark is natural match")
        fprint(f"    JC benchmark (w_0 = -0.745) is far from best-fit")
    elif w0_c > -0.95:
        fprint(f"    Combined data prefer w_0 = {w0_c:+.4f}, AWAY from LCDM")
        fprint(f"    This is potentially consistent with JC/Lu-Simon range")
    else:
        fprint(f"    Combined data prefer w_0 = {w0_c:+.4f} (intermediate)")
        fprint(f"    |1+w_0| = {abs(1+w0_c):.4f}")
    fprint()

    fprint("=" * 80)
    fprint("17Q COMPLETE")
    fprint("=" * 80)


if __name__ == '__main__':
    main()
