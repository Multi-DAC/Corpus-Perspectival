"""
Project Meridian — Phase 7: Extended Cuscuton Solver
Clayton & Clawd, March 2026

Extended Friedmann equation with braiding:
    E² = Ω_m a⁻³ + Ω_r a⁻⁴ + v₀ E^{2γ_r} + λ₀ E^{-2α_b}

where:
    v₀ + λ₀ = Ω_DE  (flatness condition)
    v₀ E^{2γ_r}     = radion drift (quintessence, w > -1)
    λ₀ E^{-2α_b}    = braiding (phantom, w < -1)

Solves for E(a), computes distances, growth, w(a), CPL fit, and χ².
Optimizes {ζ₀, γ_r, α_b} (with λ₀ = Ω_DE - v₀) against DESI+growth+CMB+H&K.
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import numpy as np
from scipy.optimize import brentq, minimize

# ============================================================
# COSMOLOGICAL CONSTANTS
# ============================================================

OMEGA_M0 = 0.315
OMEGA_R0 = 9.1e-5
OMEGA_DE0 = 1.0 - OMEGA_M0 - OMEGA_R0
H0_FIDUCIAL = 67.4   # km/s/Mpc (Planck ΛCDM)
Z_STAR = 1089.92
SIGMA8_FID = 0.811
C_OVER_H0 = 299792.458 / H0_FIDUCIAL  # c/H₀ in Mpc
R_D_FID = 147.09  # Fiducial sound horizon in Mpc

# DESI DR1 BAO data: (z_eff, value, sigma, type)
DESI_BAO_DATA = [
    (0.295,  7.93, 0.15, 'DV'),  # BGS — D_V/r_d
    (0.510, 13.62, 0.25, 'DM'),  # LRG1 — D_M/r_d
    (0.706, 17.86, 0.33, 'DM'),  # LRG2 — D_M/r_d
    (0.930, 21.71, 0.28, 'DM'),  # LRG3+ELG1 — D_M/r_d
    (1.317, 27.79, 0.69, 'DM'),  # ELG2 — D_M/r_d
    (1.491, 30.69, 1.00, 'DM'),  # QSO — D_M/r_d
    (2.330, 39.71, 0.94, 'DM'),  # Lyα — D_M/r_d
]

# fσ₈ growth data
FSIGMA8_DATA = [
    (0.02, 0.428, 0.0465),
    (0.15, 0.490, 0.145),
    (0.38, 0.497, 0.045),
    (0.51, 0.459, 0.038),
    (0.61, 0.436, 0.034),
    (0.70, 0.448, 0.043),
    (0.85, 0.315, 0.095),
    (0.978, 0.379, 0.176),
    (1.48, 0.462, 0.045),
]

# H₀ and H&K constraints
H0_OBS = 67.36
H0_SIGMA = 0.54
BETA_HK_CENTER = -0.037
SIGMA_HK = (0.047 - 0.028) / 2.0  # ~0.0095

# w₀/wₐ prior from CMB+SN (independent of BAO — avoids double-counting)
# Source: Approximate consensus from Planck CMB + Pantheon+/Union3/DES-SN5YR (no BAO)
# Conservative errors (slightly wider than published) to account for partial
# CMB overlap with our H₀ constraint.
W0_SN_CMB = -0.82       # Central value from SN+CMB (no BAO)
W0_SN_CMB_SIGMA = 0.15  # Conservative uncertainty
WA_SN_CMB = -0.75       # Central value from SN+CMB (no BAO)
WA_SN_CMB_SIGMA = 0.60  # Conservative uncertainty
RHO_W0_WA = -0.65       # Anti-correlation (standard in w₀-wₐ plane)


# ============================================================
# EXTENDED MERIDIAN MODEL SOLVER
# ============================================================

def E_extended(a, gamma_r, alpha_b, lambda0, eps0=0.0):
    """
    E(a) = H(a)/H₀ for the extended Meridian model.

    Solves: E² = Ω_m a⁻³ + Ω_r a⁻⁴ + v₀ E^{2γ_r} + λ₀ E^{-2α_b}

    where v₀ = Ω_DE - λ₀.

    The equation is implicit in E when γ_r > 0 or α_b > 0.
    """
    Om_mat = OMEGA_M0 * a**(-3) + OMEGA_R0 * a**(-4)
    v0 = OMEGA_DE0 - lambda0

    # Special case: ΛCDM (no drift, no braiding)
    if abs(gamma_r) < 1e-12 and abs(alpha_b) < 1e-12:
        return np.sqrt(Om_mat + v0 + lambda0)

    # Special case: minimal Meridian (no braiding)
    if abs(lambda0) < 1e-15 and abs(alpha_b) < 1e-12:
        def f_min(E):
            return E**2 - Om_mat - v0 * E**(2*gamma_r)
        try:
            return brentq(f_min, 0.01, 200.0, xtol=1e-12, rtol=1e-12)
        except ValueError:
            return np.sqrt(Om_mat + v0)

    # General case: implicit equation
    # f(E) = E² - Ω_mat - v₀ E^{2γ_r} - λ₀ E^{-2α_b} = 0
    def f(E):
        return E**2 - Om_mat - v0 * E**(2*gamma_r) - lambda0 * E**(-2*alpha_b)

    try:
        return brentq(f, 0.01, 200.0, xtol=1e-12, rtol=1e-12)
    except ValueError:
        # Fallback: Newton's method from ΛCDM guess
        E = np.sqrt(Om_mat + OMEGA_DE0)
        for _ in range(100):
            fE = f(E)
            # f'(E) = 2E - 2γ_r v₀ E^{2γ_r-1} + 2α_b λ₀ E^{-2α_b-1}
            fpE = 2*E - 2*gamma_r*v0*E**(2*gamma_r-1) + 2*alpha_b*lambda0*E**(-2*alpha_b-1)
            if abs(fpE) < 1e-30:
                break
            E_new = E - fE / fpE
            if E_new <= 0:
                E_new = E / 2
            if abs(E_new - E) < 1e-14 * abs(E):
                break
            E = E_new
        return max(E, 1e-10)


def E_lcdm(a):
    """ΛCDM E(a) for reference."""
    return np.sqrt(OMEGA_M0 * a**(-3) + OMEGA_R0 * a**(-4) + OMEGA_DE0)


# ============================================================
# DISTANCE AND OBSERVABLE COMPUTATIONS
# ============================================================

def _comoving_chi(z, gamma_r, alpha_b, lambda0, n_int=500):
    """χ = ∫₀ᶻ dz'/E(z') in c/H₀ units."""
    z_arr = np.linspace(0, z, n_int + 1)
    inv_E = np.zeros(n_int + 1)
    for i, zi in enumerate(z_arr):
        ai = 1.0 / (1.0 + zi)
        inv_E[i] = 1.0 / E_extended(ai, gamma_r, alpha_b, lambda0)
    return np.trapezoid(inv_E, z_arr)


def compute_DM_rd(z, gamma_r, alpha_b, lambda0, n_int=500):
    """D_M(z)/r_d = comoving distance / sound horizon."""
    chi = _comoving_chi(z, gamma_r, alpha_b, lambda0, n_int)
    return chi * C_OVER_H0 / R_D_FID


def compute_DV_rd(z, gamma_r, alpha_b, lambda0, n_int=500):
    """D_V(z)/r_d = [z D_M² / E(z)]^{1/3} / r_d."""
    chi = _comoving_chi(z, gamma_r, alpha_b, lambda0, n_int)
    a_z = 1.0 / (1.0 + z)
    E_z = E_extended(a_z, gamma_r, alpha_b, lambda0)
    D_V = (z * chi**2 / E_z) ** (1.0 / 3.0)
    return D_V * C_OVER_H0 / R_D_FID


def compute_H0_CMB(gamma_r, alpha_b, lambda0, n_int=2000):
    """H₀ from CMB angular distance constraint (θ_* = const)."""
    a_star = 1.0 / (1.0 + Z_STAR)
    a_arr = np.linspace(a_star, 1.0, n_int + 1)

    integrand_model = np.zeros(n_int + 1)
    integrand_lcdm = np.zeros(n_int + 1)

    for i, a in enumerate(a_arr):
        E_mod = E_extended(a, gamma_r, alpha_b, lambda0)
        E_ref = E_lcdm(a)
        integrand_model[i] = 1.0 / (a**2 * E_mod)
        integrand_lcdm[i] = 1.0 / (a**2 * E_ref)

    I_model = np.trapezoid(integrand_model, a_arr)
    I_lcdm = np.trapezoid(integrand_lcdm, a_arr)

    return H0_FIDUCIAL * I_lcdm / I_model


def compute_fsigma8(z, zeta0, gamma_r, alpha_b, lambda0):
    """fσ₈(z) using Linder growth approximation with modified gravity correction."""
    a = 1.0 / (1.0 + z)
    E2 = E_extended(a, gamma_r, alpha_b, lambda0)**2
    Om_z = OMEGA_M0 * a**(-3) / E2

    gamma_growth = 0.55 - zeta0 / 2.0
    f_growth = Om_z ** gamma_growth

    # Growth factor D(z)/D(0)
    n_growth = 200
    a_arr = np.linspace(a, 1.0, n_growth + 1)
    integrand = np.zeros(n_growth + 1)

    for i, ai in enumerate(a_arr):
        Ei2 = E_extended(ai, gamma_r, alpha_b, lambda0)**2
        Omi = OMEGA_M0 * ai**(-3) / Ei2
        fi = Omi ** gamma_growth
        integrand[i] = (fi - 1.0) / ai

    ln_D_ratio = np.trapezoid(integrand, a_arr)
    D_ratio = a * np.exp(-ln_D_ratio)

    sigma8_z = SIGMA8_FID * D_ratio
    return f_growth * sigma8_z


# ============================================================
# EQUATION OF STATE COMPUTATIONS
# ============================================================

def w_DE(a, gamma_r, alpha_b, lambda0, da=0.005):
    """
    Effective dark energy equation of state at scale factor a.

    w = -1 - (1/3) d(ln ρ_DE)/d(ln a)

    Computed via numerical differentiation of ρ_DE(a) = E² - Ω_m a⁻³ - Ω_r a⁻⁴.
    """
    a_p = a * (1 + da)
    a_m = a * (1 - da)

    E2 = E_extended(a, gamma_r, alpha_b, lambda0)**2
    E2_p = E_extended(a_p, gamma_r, alpha_b, lambda0)**2
    E2_m = E_extended(a_m, gamma_r, alpha_b, lambda0)**2

    rho = E2 - OMEGA_M0 * a**(-3) - OMEGA_R0 * a**(-4)
    rho_p = E2_p - OMEGA_M0 * a_p**(-3) - OMEGA_R0 * a_p**(-4)
    rho_m = E2_m - OMEGA_M0 * a_m**(-3) - OMEGA_R0 * a_m**(-4)

    if rho <= 0 or rho_p <= 0 or rho_m <= 0:
        return -1.0  # Fallback

    dln_rho = np.log(rho_p / rho_m) / np.log(a_p / a_m)
    return -1.0 - dln_rho / 3.0


def w_trajectory(gamma_r, alpha_b, lambda0, z_arr=None):
    """Compute w(z) at an array of redshifts."""
    if z_arr is None:
        z_arr = np.array([0.0, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0])
    w_arr = np.zeros(len(z_arr))
    for i, z in enumerate(z_arr):
        a = 1.0 / (1.0 + z)
        w_arr[i] = w_DE(a, gamma_r, alpha_b, lambda0)
    return z_arr, w_arr


def fit_CPL(gamma_r, alpha_b, lambda0, a_range=(0.3, 1.0), n_pts=50):
    """
    Fit the Meridian w(a) to the CPL form w = w₀ + wₐ(1-a) over a_range.

    Returns (w0, wa, chi2_fit) where chi2_fit measures the CPL approximation quality.
    """
    a_arr = np.linspace(a_range[0], a_range[1], n_pts)
    w_arr = np.array([w_DE(a, gamma_r, alpha_b, lambda0) for a in a_arr])

    # Linear regression: w = w₀ + wₐ(1-a)
    # Let x = 1-a, y = w. Then y = w₀ + wₐ x.
    x = 1.0 - a_arr
    y = w_arr

    # Least squares: [w₀, wₐ] = (X^T X)^{-1} X^T y
    X = np.column_stack([np.ones(n_pts), x])
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    w0, wa = beta[0], beta[1]

    # Fit quality
    w_fit = w0 + wa * x
    residuals = w_arr - w_fit
    rms = np.sqrt(np.mean(residuals**2))

    return w0, wa, rms


def find_phantom_crossing(gamma_r, alpha_b, lambda0, z_range=(0.01, 5.0)):
    """Find the redshift where w_DE = -1 (phantom crossing)."""
    v0 = OMEGA_DE0 - lambda0
    if lambda0 < 1e-15:
        return None  # No braiding, no crossing

    # Analytic estimate from D7.2 eq 4.3
    if gamma_r > 0 and alpha_b > 0:
        ratio = (alpha_b * lambda0) / (gamma_r * v0)
        if ratio > 0:
            E_c = ratio ** (1.0 / (2.0 * (gamma_r + alpha_b)))
            # E_c corresponds to some z_c; for now just check numerically
        else:
            return None

    # Numerical search
    def w_minus_m1(z):
        a = 1.0 / (1.0 + z)
        return w_DE(a, gamma_r, alpha_b, lambda0) + 1.0

    # Check sign at endpoints
    w_low = w_minus_m1(z_range[0])
    w_high = w_minus_m1(z_range[1])

    if w_low * w_high > 0:
        return None  # No crossing in range

    try:
        z_c = brentq(w_minus_m1, z_range[0], z_range[1], xtol=1e-4)
        return z_c
    except ValueError:
        return None


# ============================================================
# CHI-SQUARED COMPUTATION
# ============================================================

def chi2_components(zeta0, gamma_r, alpha_b, lambda0):
    """
    Compute all χ² components for the extended Meridian model.

    Returns: dict with chi2_D, chi2_f, chi2_H, chi2_HK, chi2_total
    """
    # 1. DESI BAO distances
    chi2_D = 0.0
    for z_eff, obs, sigma, dtype in DESI_BAO_DATA:
        if dtype == 'DV':
            model = compute_DV_rd(z_eff, gamma_r, alpha_b, lambda0)
        else:
            model = compute_DM_rd(z_eff, gamma_r, alpha_b, lambda0)
        chi2_D += ((model - obs) / sigma) ** 2

    # 2. fσ₈ growth data
    chi2_f = 0.0
    for z_eff, fs8_obs, sigma in FSIGMA8_DATA:
        fs8_model = compute_fsigma8(z_eff, zeta0, gamma_r, alpha_b, lambda0)
        chi2_f += ((fs8_model - fs8_obs) / sigma) ** 2

    # 3. H₀ from CMB
    H0_model = compute_H0_CMB(gamma_r, alpha_b, lambda0)
    chi2_H = ((H0_model - H0_OBS) / H0_SIGMA) ** 2

    # 4. H&K consistency
    eps_SW = zeta0 / (1.0 + zeta0) if zeta0 > 0 else 0.0
    beta_HK_model = -eps_SW
    chi2_HK = ((beta_HK_model - BETA_HK_CENTER) / SIGMA_HK) ** 2

    # 5. w₀/wₐ from CMB+SN (independent of BAO — no double-counting)
    w0_model, wa_model, cpl_rms = fit_CPL(gamma_r, alpha_b, lambda0)
    # 2D Gaussian with correlation
    det = 1.0 - RHO_W0_WA**2
    dw0 = (w0_model - W0_SN_CMB) / W0_SN_CMB_SIGMA
    dwa = (wa_model - WA_SN_CMB) / WA_SN_CMB_SIGMA
    chi2_w = (dw0**2 - 2.0 * RHO_W0_WA * dw0 * dwa + dwa**2) / det

    total = chi2_D + chi2_f + chi2_H + chi2_HK + chi2_w
    return {
        'chi2_D': chi2_D, 'chi2_f': chi2_f,
        'chi2_H': chi2_H, 'chi2_HK': chi2_HK,
        'chi2_w': chi2_w,
        'chi2_total': total,
        'H0': H0_model, 'beta_HK': beta_HK_model,
        'w0': w0_model, 'wa': wa_model, 'cpl_rms': cpl_rms,
    }


def chi2_total_func(theta):
    """χ² as function of θ = [ζ₀, γ_r, α_b]."""
    zeta0, gamma_r, alpha_b = theta
    if zeta0 < 0 or gamma_r < 0 or alpha_b < 0:
        return 1e10
    lambda0 = max(OMEGA_DE0 - OMEGA_DE0 / (1.0 + 1e-10), 0)  # need v0 > 0

    # v₀ is determined by the model; λ₀ is a function of the other params
    # For optimization, parameterize as: λ₀ = Ω_DE × f_b where f_b ∈ [0,1]
    # But for simplicity, let's add lambda0 as a derived parameter
    # Actually: we need to either optimize over λ₀ too or fix it.
    # Let's optimize over [ζ₀, γ_r, α_b, λ₀] with constraint v₀ + λ₀ = Ω_DE
    # This means λ₀ is free and v₀ = Ω_DE - λ₀
    # But the function signature has 3 params... let me fix this.
    return 1e10  # placeholder


def chi2_4param(theta):
    """χ² as function of θ = [ζ₀, γ_r, α_b, λ₀]."""
    zeta0, gamma_r, alpha_b, lambda0 = theta
    if zeta0 < 0 or gamma_r < 0 or alpha_b < 0 or lambda0 < 0:
        return 1e10
    if lambda0 >= OMEGA_DE0:
        return 1e10  # v₀ must be positive
    result = chi2_components(zeta0, gamma_r, alpha_b, lambda0)
    return result['chi2_total']


# ============================================================
# OPTIMIZATION
# ============================================================

def optimize_extended(n_starts=8, verbose=True):
    """
    Find the best-fit extended Meridian parameters.

    Optimizes {ζ₀, γ_r, α_b, λ₀} with constraint v₀ = Ω_DE - λ₀ > 0.
    """
    if verbose:
        print("\n  Optimizing extended Meridian model...")
        print(f"  Parameters: ζ₀, γ_r, α_b, λ₀ (v₀ = Ω_DE - λ₀)")

    bounds = [
        (0.001, 0.15),   # ζ₀
        (0.01, 0.95),    # γ_r (allow near-zero)
        (0.01, 5.0),     # α_b (allow wider range)
        (0.0, 0.55),     # λ₀ (allow zero; must be < Ω_DE ≈ 0.685)
    ]

    best_result = None
    best_chi2 = 1e10

    # Multiple Nelder-Mead starts
    np.random.seed(42)
    for trial in range(n_starts):
        x0 = np.array([
            np.random.uniform(bounds[0][0], bounds[0][1]),
            np.random.uniform(bounds[1][0], bounds[1][1]),
            np.random.uniform(bounds[2][0], bounds[2][1]),
            np.random.uniform(bounds[3][0], bounds[3][1]),
        ])

        result = minimize(chi2_4param, x0, method='Nelder-Mead',
                         options={'maxiter': 5000, 'xatol': 1e-6, 'fatol': 1e-4})

        if result.fun < best_chi2:
            best_chi2 = result.fun
            best_result = result

        if verbose:
            print(f"    Trial {trial+1}/{n_starts}: χ² = {result.fun:.2f}  "
                  f"[ζ₀={result.x[0]:.4f}, γ_r={result.x[1]:.4f}, "
                  f"α_b={result.x[2]:.4f}, λ₀={result.x[3]:.4f}]")

    return best_result


# ============================================================
# FISHER MATRIX FOR EXTENDED MODEL
# ============================================================

def fisher_matrix_extended(theta0, step_frac=0.01):
    """
    Fisher matrix at θ₀ = [ζ₀, γ_r, α_b, λ₀].
    F_ij = ½ ∂²χ²/∂θ_i∂θ_j via central differences.
    """
    n = len(theta0)
    theta0 = np.array(theta0, dtype=float)
    h = np.array([max(abs(t) * step_frac, 0.001) for t in theta0])

    F = np.zeros((n, n))
    chi2_0 = chi2_4param(theta0)

    for i in range(n):
        for j in range(i, n):
            if i == j:
                tp = theta0.copy(); tp[i] += h[i]
                tm = theta0.copy(); tm[i] -= h[i]
                F[i, i] = 0.5 * (chi2_4param(tp) - 2*chi2_0 + chi2_4param(tm)) / h[i]**2
            else:
                hi, hj = h[i], h[j]
                pp = theta0.copy(); pp[i] += hi; pp[j] += hj
                pm = theta0.copy(); pm[i] += hi; pm[j] -= hj
                mp = theta0.copy(); mp[i] -= hi; mp[j] += hj
                mm = theta0.copy(); mm[i] -= hi; mm[j] -= hj
                F[i, j] = 0.5 * (chi2_4param(pp) - chi2_4param(pm)
                                  - chi2_4param(mp) + chi2_4param(mm)) / (4*hi*hj)
                F[j, i] = F[i, j]

    try:
        cov = np.linalg.inv(F)
        sigmas = np.sqrt(np.maximum(np.diag(cov), 0))
    except np.linalg.LinAlgError:
        cov = np.full((n, n), np.inf)
        sigmas = np.full(n, np.inf)

    return F, cov, sigmas


# ============================================================
# MAIN ANALYSIS
# ============================================================

def main():
    print("=" * 80)
    print("  PROJECT MERIDIAN — PHASE 7: EXTENDED CUSCUTON ANALYSIS")
    print("=" * 80)

    # ============================================================
    # STEP 0: ΛCDM reference
    # ============================================================
    print("\n  STEP 0: ΛCDM reference χ²")
    ref = chi2_components(0.0, 0.0, 0.0, 0.0)
    print(f"    χ²_D (BAO)  = {ref['chi2_D']:.2f}")
    print(f"    χ²_f (fσ₈)  = {ref['chi2_f']:.2f}")
    print(f"    χ²_H (H₀)   = {ref['chi2_H']:.2f}")
    print(f"    χ²_HK       = {ref['chi2_HK']:.2f}")
    print(f"    χ²_w (w₀wₐ) = {ref['chi2_w']:.2f}")
    print(f"    χ²_total     = {ref['chi2_total']:.2f}")
    print(f"    H₀ = {ref['H0']:.2f} km/s/Mpc")
    print(f"    w₀ = {ref['w0']:.4f}, wₐ = {ref['wa']:.4f}")

    # ============================================================
    # STEP 1: Minimal Meridian reference (D6.5 fiducial)
    # ============================================================
    print("\n  STEP 1: Minimal Meridian (λ₀ = 0) reference")
    min_ref = chi2_components(0.0446, 0.3987, 0.0, 0.0)
    print(f"    χ²_D (BAO)  = {min_ref['chi2_D']:.2f}")
    print(f"    χ²_f (fσ₈)  = {min_ref['chi2_f']:.2f}")
    print(f"    χ²_H (H₀)   = {min_ref['chi2_H']:.2f}")
    print(f"    χ²_HK       = {min_ref['chi2_HK']:.2f}")
    print(f"    χ²_w (w₀wₐ) = {min_ref['chi2_w']:.2f}")
    print(f"    χ²_total     = {min_ref['chi2_total']:.2f}")
    print(f"    H₀ = {min_ref['H0']:.2f} km/s/Mpc")
    print(f"    w₀ = {min_ref['w0']:.4f}, wₐ = {min_ref['wa']:.4f}")

    # ============================================================
    # STEP 2: w(a) and CPL for minimal model
    # ============================================================
    print("\n  STEP 2: Minimal Meridian w(a) trajectory")
    z_pts, w_pts = w_trajectory(0.3987, 0.0, 0.0)
    for z, w in zip(z_pts, w_pts):
        print(f"    z = {z:.1f}:  w = {w:.4f}")
    w0_min, wa_min, rms_min = fit_CPL(0.3987, 0.0, 0.0)
    print(f"    CPL fit: w₀ = {w0_min:.4f}, wₐ = {wa_min:.4f} (RMS = {rms_min:.6f})")

    # ============================================================
    # STEP 3: Parameter scan — effect of braiding
    # ============================================================
    print("\n  STEP 3: Braiding parameter scan")
    print(f"    Fixed: γ_r = 0.40, ζ₀ = 0.045")
    print(f"    {'α_b':>6s}  {'λ₀':>6s}  {'v₀':>6s}  {'w₀':>8s}  {'wₐ':>8s}  "
          f"{'z_c':>6s}  {'χ²_D':>7s}  {'χ²_tot':>7s}")
    print(f"    {'─'*6}  {'─'*6}  {'─'*6}  {'─'*8}  {'─'*8}  {'─'*6}  {'─'*7}  {'─'*7}")

    gamma_r_scan = 0.40
    for alpha_b in [0.3, 0.5, 0.8, 1.0, 1.5, 2.0]:
        for lambda0 in [0.02, 0.05, 0.10, 0.15, 0.20]:
            v0 = OMEGA_DE0 - lambda0
            if v0 < 0.1:
                continue
            w0, wa, _ = fit_CPL(gamma_r_scan, alpha_b, lambda0)
            z_c = find_phantom_crossing(gamma_r_scan, alpha_b, lambda0)
            z_c_str = f"{z_c:.2f}" if z_c is not None else "  —  "
            res = chi2_components(0.045, gamma_r_scan, alpha_b, lambda0)
            print(f"    {alpha_b:6.2f}  {lambda0:6.3f}  {v0:6.3f}  {w0:8.4f}  {wa:8.4f}  "
                  f"{z_c_str:>6s}  {res['chi2_D']:7.2f}  {res['chi2_total']:7.2f}")

    # ============================================================
    # STEP 4: Full optimization (now including w₀/wₐ from CMB+SN)
    # ============================================================
    print("\n  STEP 4: Full 4-parameter optimization (BAO + fσ₈ + H₀ + H&K + w₀wₐ)")
    print(f"    w₀/wₐ prior: w₀ = {W0_SN_CMB} ± {W0_SN_CMB_SIGMA}, "
          f"wₐ = {WA_SN_CMB} ± {WA_SN_CMB_SIGMA}, ρ = {RHO_W0_WA}")
    result = optimize_extended(n_starts=16, verbose=True)

    if result is not None:
        zeta0_opt, gamma_r_opt, alpha_b_opt, lambda0_opt = result.x
        v0_opt = OMEGA_DE0 - lambda0_opt

        print(f"\n  ═══════════════════════════════════════════════════════")
        print(f"  BEST-FIT EXTENDED MERIDIAN")
        print(f"  ═══════════════════════════════════════════════════════")
        print(f"    ζ₀     = {zeta0_opt:.4f}")
        print(f"    γ_r    = {gamma_r_opt:.4f}")
        print(f"    α_b    = {alpha_b_opt:.4f}")
        print(f"    λ₀     = {lambda0_opt:.4f}")
        print(f"    v₀     = {v0_opt:.4f}")
        print(f"    χ²     = {result.fun:.2f}")

        # Detailed breakdown
        opt_res = chi2_components(zeta0_opt, gamma_r_opt, alpha_b_opt, lambda0_opt)
        print(f"\n    χ² breakdown:")
        print(f"      BAO:    {opt_res['chi2_D']:.2f}  (ΛCDM: {ref['chi2_D']:.2f})")
        print(f"      fσ₈:   {opt_res['chi2_f']:.2f}  (ΛCDM: {ref['chi2_f']:.2f})")
        print(f"      H₀:    {opt_res['chi2_H']:.2f}  (ΛCDM: {ref['chi2_H']:.2f})")
        print(f"      H&K:   {opt_res['chi2_HK']:.2f}  (ΛCDM: {ref['chi2_HK']:.2f})")
        print(f"      w₀wₐ:  {opt_res['chi2_w']:.2f}  (ΛCDM: {ref['chi2_w']:.2f})")
        print(f"      Total: {opt_res['chi2_total']:.2f}  (ΛCDM: {ref['chi2_total']:.2f})")
        print(f"      Δχ² = {opt_res['chi2_total'] - ref['chi2_total']:.2f}")
        print(f"      H₀ = {opt_res['H0']:.2f} km/s/Mpc")

        # w(a) trajectory
        print(f"\n    w(a) trajectory:")
        z_pts, w_pts = w_trajectory(gamma_r_opt, alpha_b_opt, lambda0_opt)
        for z, w in zip(z_pts, w_pts):
            print(f"      z = {z:.1f}:  w = {w:.4f}")

        # CPL fit (already computed in chi2_components)
        w0_opt = opt_res['w0']
        wa_opt = opt_res['wa']
        rms_opt = opt_res['cpl_rms']
        print(f"\n    CPL fit: w₀ = {w0_opt:.4f}, wₐ = {wa_opt:.4f}")
        print(f"    CPL RMS: {rms_opt:.6f}")
        print(f"    CMB+SN prior: w₀ = {W0_SN_CMB} ± {W0_SN_CMB_SIGMA}, wₐ = {WA_SN_CMB} ± {WA_SN_CMB_SIGMA}")
        print(f"    DESI DR2 (full): w₀ = -0.752 ± 0.058, wₐ = -0.86 ± 0.27")
        print(f"    w₀ pull vs CMB+SN: {(w0_opt - W0_SN_CMB)/W0_SN_CMB_SIGMA:.1f}σ")
        print(f"    wₐ pull vs CMB+SN: {(wa_opt - WA_SN_CMB)/WA_SN_CMB_SIGMA:.1f}σ")
        print(f"    w₀ pull vs DESI: {(w0_opt - (-0.752))/0.058:.1f}σ")
        print(f"    wₐ pull vs DESI: {(wa_opt - (-0.86))/0.27:.1f}σ")

        # Phantom crossing
        z_c = find_phantom_crossing(gamma_r_opt, alpha_b_opt, lambda0_opt)
        if z_c is not None:
            print(f"\n    Phantom crossing at z_c = {z_c:.3f}")
        else:
            print(f"\n    No phantom crossing found in z ∈ [0, 5]")

        # ============================================================
        # STEP 5: Fisher matrix at optimum
        # ============================================================
        print(f"\n  STEP 5: Fisher matrix at optimum")
        theta_opt = [zeta0_opt, gamma_r_opt, alpha_b_opt, lambda0_opt]
        F, cov, sigmas = fisher_matrix_extended(theta_opt)

        param_names = ['ζ₀', 'γ_r', 'α_b', 'λ₀']
        print(f"    Parameter uncertainties:")
        for i, name in enumerate(param_names):
            if sigmas[i] < 1e10:
                print(f"      {name} = {theta_opt[i]:.4f} ± {sigmas[i]:.4f}")
            else:
                print(f"      {name} = {theta_opt[i]:.4f} ± ∞ (unconstrained)")

        # Model comparison
        print(f"\n  ═══════════════════════════════════════════════════════")
        print(f"  MODEL COMPARISON")
        print(f"  ═══════════════════════════════════════════════════════")

        k_ext = 10   # 6 base + 4 Meridian
        k_min = 8    # 6 base + 2 Meridian
        k_lcdm = 6
        N = 20       # 7 BAO + 9 fσ₈ + 1 H₀ + 1 H&K + 2 w₀wₐ

        for label, chi2_m, k_m in [
            ("Extended Meridian", opt_res['chi2_total'], k_ext),
            ("Minimal Meridian", min_ref['chi2_total'], k_min),
        ]:
            dAIC = (chi2_m + 2*k_m) - (ref['chi2_total'] + 2*k_lcdm)
            dBIC = (chi2_m + k_m*np.log(N)) - (ref['chi2_total'] + k_lcdm*np.log(N))
            print(f"\n    {label} vs ΛCDM:")
            print(f"      Δχ²  = {chi2_m - ref['chi2_total']:+.2f}")
            print(f"      ΔAIC = {dAIC:+.2f}")
            print(f"      ΔBIC = {dBIC:+.2f}")

    print(f"\n{'=' * 80}")
    print(f"  ANALYSIS COMPLETE")
    print(f"{'=' * 80}")


if __name__ == '__main__':
    main()
