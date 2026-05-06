"""
Project Meridian — D6.5: Fisher Matrix and Statistical Analysis
Clayton & Clawd, March 2026

Computes:
  1. Fisher information matrix at the global optimum (eps0→0, zeta0=0.045, gamma_r=0.40)
  2. Parameter uncertainties and correlations
  3. Model comparison statistics (AIC, BIC, Bayesian evidence ratio)
  4. Future survey forecasts (DESI full, Euclid, LSST)
  5. Derived observable uncertainties (w0, wa, H0, mu, Sigma)

Uses the meridian_cosmology.py solver for all computations.
"""

import sys
import os
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add the phase3 directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'phase3'))

import numpy as np
from scipy.optimize import brentq

# ============================================================
# COSMOLOGICAL CONSTANTS (from meridian_cosmology.py)
# ============================================================

OMEGA_M0 = 0.315
OMEGA_R0 = 9.1e-5
OMEGA_DE0 = 1.0 - OMEGA_M0 - OMEGA_R0
H0_FIDUCIAL = 67.4   # km/s/Mpc (Planck LCDM)
Z_STAR = 1089.92
SIGMA8_FID = 0.811

# DESI DR1 BAO distance data
# BGS uses D_V/r_d; all others report D_M/r_d and D_H/r_d separately.
# Format: (z_eff, value, sigma, type) where type = 'DV' or 'DM'
DESI_BAO_DATA = [
    (0.295,  7.93, 0.15, 'DV'),  # DESI BGS — D_V/r_d
    (0.510, 13.62, 0.25, 'DM'),  # DESI LRG1 — D_M/r_d
    (0.706, 17.86, 0.33, 'DM'),  # DESI LRG2 — D_M/r_d
    (0.930, 21.71, 0.28, 'DM'),  # DESI LRG3+ELG1 — D_M/r_d
    (1.317, 27.79, 0.69, 'DM'),  # DESI ELG2 — D_M/r_d
    (1.491, 30.69, 1.00, 'DM'),  # DESI QSO — D_M/r_d
    (2.330, 39.71, 0.94, 'DM'),  # DESI Lya — D_M/r_d
]

# fσ₈ data (compiled from BOSS, eBOSS, 6dFGS, VIPERS, FastSound)
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

# H₀ constraint
H0_OBS = 67.36     # Planck 2018
H0_SIGMA = 0.54    # Planck 2018

# Hubble-Killing (expansion-growth consistency)
BETA_HK_CENTER = -0.037
SIGMA_HK = (0.047 - 0.028) / 2.0  # ~0.0095


# ============================================================
# MERIDIAN MODEL SOLVER (self-contained for Fisher matrix)
# ============================================================

def E_meridian(a, zeta0, gamma_r, eps0=0.0001):
    """
    E(a) = H(a)/H₀ for the combined Meridian model.

    Solves: E⁴ - Ω_mat(a)·E² - v₀·E^{2+2γ_r} - κ₀ = 0
    """
    Om = OMEGA_M0
    Or = OMEGA_R0
    Ode = OMEGA_DE0

    # Normalization: ζ₀ does NOT enter background E(a)
    # (it affects perturbations/growth only, via F(a) = 1 - ζ₀(ψ²-1))
    v0 = Ode / (1.0 + eps0)
    kappa0 = eps0 * v0

    Om_mat = Om * a**(-3) + Or * a**(-4)

    if gamma_r < 1e-12 and kappa0 < 1e-15:
        # ΛCDM-like: E² = Ω_mat + v₀
        return np.sqrt(Om_mat + v0)

    def f(E):
        return E**4 - Om_mat * E**2 - v0 * E**(2 + 2*gamma_r) - kappa0

    try:
        return brentq(f, 0.01, 200.0, xtol=1e-12, rtol=1e-12)
    except ValueError:
        R = Om_mat + v0
        disc = R**2 + 4.0 * kappa0
        return np.sqrt(0.5 * (R + np.sqrt(max(disc, 0.0))))


C_OVER_H0 = 299792.458 / H0_FIDUCIAL  # c/H₀ in Mpc = 4448.0
R_D_FID = 147.09  # Fiducial sound horizon in Mpc


def _comoving_chi(z, zeta0, gamma_r, eps0=0.0001, n_int=500):
    """Compute χ = ∫₀ᶻ dz'/E(z') (comoving distance in c/H₀ units)."""
    z_arr = np.linspace(0, z, n_int + 1)
    inv_E = np.zeros(n_int + 1)
    for i, zi in enumerate(z_arr):
        ai = 1.0 / (1.0 + zi)
        inv_E[i] = 1.0 / E_meridian(ai, zeta0, gamma_r, eps0)
    return np.trapezoid(inv_E, z_arr)


def compute_DM_rd(z, zeta0, gamma_r, eps0=0.0001, n_int=500):
    """Compute D_M(z)/r_d = comoving distance / sound horizon."""
    chi = _comoving_chi(z, zeta0, gamma_r, eps0, n_int)
    return chi * C_OVER_H0 / R_D_FID


def compute_DV_rd(z, zeta0, gamma_r, eps0=0.0001, n_int=500):
    """Compute D_V(z)/r_d = [z D_M² / E(z)]^{1/3} / r_d."""
    chi = _comoving_chi(z, zeta0, gamma_r, eps0, n_int)
    a_z = 1.0 / (1.0 + z)
    E_z = E_meridian(a_z, zeta0, gamma_r, eps0)
    D_V = (z * chi**2 / E_z) ** (1.0 / 3.0)
    return D_V * C_OVER_H0 / R_D_FID


def compute_H0_CMB(zeta0, gamma_r, eps0=0.0001, n_int=2000):
    """
    Compute H₀ from CMB angular distance constraint.

    The CMB fixes θ_* = r_s(z*)/D_A(z*). For a model with different E(z),
    H₀ shifts to keep θ_* = const:

    H₀_model / H₀_ΛCDM = ∫_ΛCDM / ∫_model

    where ∫ = ∫_{a*}^1 da/(a² E(a))
    """
    a_star = 1.0 / (1.0 + Z_STAR)

    # Model integral
    a_arr = np.linspace(a_star, 1.0, n_int + 1)
    integrand_model = np.zeros(n_int + 1)
    integrand_lcdm = np.zeros(n_int + 1)

    for i, a in enumerate(a_arr):
        E_mod = E_meridian(a, zeta0, gamma_r, eps0)
        E_lcdm = E_meridian(a, 0.0, 0.0, 0.0001)
        integrand_model[i] = 1.0 / (a**2 * E_mod)
        integrand_lcdm[i] = 1.0 / (a**2 * E_lcdm)

    I_model = np.trapezoid(integrand_model, a_arr)
    I_lcdm = np.trapezoid(integrand_lcdm, a_arr)

    return H0_FIDUCIAL * I_lcdm / I_model


def compute_fsigma8(z, zeta0, gamma_r, eps0=0.0001, n_int=500):
    """
    Compute f·σ₈(z) for the Meridian model.

    Growth equation: δ'' + (2 + E'/E)δ' - (3/2)Ω_m a⁻³ μ(a)/E² δ = 0
    where μ(a) = 1/F(a) (modified gravity from non-minimal coupling)

    F(a) = 1 - ζ₀(ψ²(a) - 1) ≈ 1 for eps0 → 0, small ζ₀.
    For eps0 → 0: ψ(a) ≈ 1 + small corrections, so μ ≈ 1/(1 - small).

    Simplified: use the Linder approximation with modification
    f(z) ≈ Ω_m(z)^γ where γ = 0.55 + (1-F₀)/2 for modified gravity
    """
    # Omega_m(z)
    a = 1.0 / (1.0 + z)
    E2 = E_meridian(a, zeta0, gamma_r, eps0)**2
    Om_z = OMEGA_M0 * a**(-3) / E2

    # Modified gravity correction to growth index
    # F(a=1) = 1 by construction, but F varies with a
    # For small eps0: the variation of F is through ψ(a)
    # At the linear level: Δγ ≈ ζ₀ × correction
    # Use the Horndeski result: γ ≈ 0.55 + 0.05(1+w) for standard quintessence
    # Modified gravity: γ ≈ 0.55 - ζ₀/2 (leading correction from Pogosian & Silvestri 2016)
    gamma_growth = 0.55 - zeta0 / 2.0

    f_growth = Om_z ** gamma_growth

    # σ₈ normalization: solve growth ODE numerically
    # For the Fisher matrix, use the linear perturbation theory result:
    # σ₈(z) = σ₈(0) × D(z)/D(0)
    # where D(z) is the growth factor

    # Simplified growth factor (Linder 2005 approximation):
    # D(a) ≈ a × exp(∫₀^a [Ω_m(a')^γ - 1] da'/a')

    # Compute growth factor ratio D(z)/D(0)
    n_growth = 200
    a_arr = np.linspace(a, 1.0, n_growth + 1)
    integrand = np.zeros(n_growth + 1)

    for i, ai in enumerate(a_arr):
        Ei2 = E_meridian(ai, zeta0, gamma_r, eps0)**2
        Omi = OMEGA_M0 * ai**(-3) / Ei2
        fi = Omi ** gamma_growth
        integrand[i] = (fi - 1.0) / ai

    ln_D_ratio = np.trapezoid(integrand, a_arr)
    D_ratio = a * np.exp(-ln_D_ratio)  # D(z)/D(0), note the sign

    sigma8_z = SIGMA8_FID * D_ratio
    return f_growth * sigma8_z


# ============================================================
# CHI-SQUARED COMPUTATION
# ============================================================

def chi2_components(zeta0, gamma_r, eps0=0.0001):
    """
    Compute all χ² components for the Meridian model.

    Returns: (chi2_D, chi2_f, chi2_H, chi2_HK, chi2_total)
    """
    # 1. DESI BAO distances (D_V or D_M depending on tracer)
    chi2_D = 0.0
    for z_eff, obs, sigma, dtype in DESI_BAO_DATA:
        if dtype == 'DV':
            model = compute_DV_rd(z_eff, zeta0, gamma_r, eps0)
        else:
            model = compute_DM_rd(z_eff, zeta0, gamma_r, eps0)
        chi2_D += ((model - obs) / sigma) ** 2

    # 2. fσ₈ growth data
    chi2_f = 0.0
    for z_eff, fs8_obs, sigma in FSIGMA8_DATA:
        fs8_model = compute_fsigma8(z_eff, zeta0, gamma_r, eps0)
        chi2_f += ((fs8_model - fs8_obs) / sigma) ** 2

    # 3. H₀ from CMB
    H0_model = compute_H0_CMB(zeta0, gamma_r, eps0)
    chi2_H = ((H0_model - H0_OBS) / H0_SIGMA) ** 2

    # 4. Hubble-Killing consistency
    # The H&K parameter β_HK = -ε_SW where ε_SW = ζ₀/(1+ζ₀)
    eps_SW = zeta0 / (1.0 + zeta0) if zeta0 > 0 else 0.0
    beta_HK_model = -eps_SW
    chi2_HK = ((beta_HK_model - BETA_HK_CENTER) / SIGMA_HK) ** 2

    return chi2_D, chi2_f, chi2_H, chi2_HK, chi2_D + chi2_f + chi2_H + chi2_HK


def chi2_total(theta):
    """Total χ² as a function of parameter vector θ = (ζ₀, γ_r)."""
    zeta0, gamma_r = theta
    if zeta0 < 0 or gamma_r < 0:
        return 1e10
    _, _, _, _, total = chi2_components(zeta0, gamma_r)
    return total


# ============================================================
# FISHER MATRIX COMPUTATION
# ============================================================

def fisher_matrix(theta0, step_sizes=None):
    """
    Compute the Fisher information matrix at θ₀ via numerical second derivatives.

    F_ij = ½ ∂²χ²/∂θ_i∂θ_j

    Uses central differences for numerical stability.

    Parameters:
        theta0: array-like, fiducial parameter values [zeta0, gamma_r]
        step_sizes: array-like, step sizes for numerical derivatives

    Returns:
        F: 2×2 Fisher matrix
        cov: 2×2 covariance matrix (F⁻¹)
        sigmas: 1σ marginalized uncertainties
        rho: correlation coefficient
    """
    n_params = len(theta0)
    theta0 = np.array(theta0, dtype=float)

    if step_sizes is None:
        # Use ~1% of parameter value or 0.001 if near zero
        step_sizes = np.array([max(abs(t) * 0.01, 0.001) for t in theta0])

    F = np.zeros((n_params, n_params))

    # Compute second derivatives using central differences
    chi2_0 = chi2_total(theta0)

    for i in range(n_params):
        for j in range(i, n_params):
            if i == j:
                # Diagonal: d²χ²/dθ_i² = [χ²(θ+h) - 2χ²(θ) + χ²(θ-h)] / h²
                h = step_sizes[i]
                theta_p = theta0.copy(); theta_p[i] += h
                theta_m = theta0.copy(); theta_m[i] -= h

                chi2_p = chi2_total(theta_p)
                chi2_m = chi2_total(theta_m)

                F[i, i] = 0.5 * (chi2_p - 2*chi2_0 + chi2_m) / h**2
            else:
                # Off-diagonal: d²χ²/dθ_idθ_j
                # = [χ²(++)-χ²(+-)-χ²(-+)+χ²(--)] / (4h_ih_j)
                hi = step_sizes[i]
                hj = step_sizes[j]

                theta_pp = theta0.copy(); theta_pp[i] += hi; theta_pp[j] += hj
                theta_pm = theta0.copy(); theta_pm[i] += hi; theta_pm[j] -= hj
                theta_mp = theta0.copy(); theta_mp[i] -= hi; theta_mp[j] += hj
                theta_mm = theta0.copy(); theta_mm[i] -= hi; theta_mm[j] -= hj

                chi2_pp = chi2_total(theta_pp)
                chi2_pm = chi2_total(theta_pm)
                chi2_mp = chi2_total(theta_mp)
                chi2_mm = chi2_total(theta_mm)

                F[i, j] = 0.5 * (chi2_pp - chi2_pm - chi2_mp + chi2_mm) / (4 * hi * hj)
                F[j, i] = F[i, j]  # Symmetric

    # Covariance matrix
    try:
        cov = np.linalg.inv(F)
        sigmas = np.sqrt(np.diag(cov))
        rho = cov[0, 1] / (sigmas[0] * sigmas[1]) if sigmas[0] > 0 and sigmas[1] > 0 else 0.0
    except np.linalg.LinAlgError:
        cov = np.full((n_params, n_params), np.inf)
        sigmas = np.full(n_params, np.inf)
        rho = 0.0

    return F, cov, sigmas, rho


def fisher_forecast(theta0, scale_factors, label=""):
    """
    Forecast parameter constraints for scaled data.

    scale_factors: dict with keys 'D', 'f', 'H', 'HK' giving the
    improvement factor for each observable (e.g., 0.5 = half the error bars).
    """
    # This is done by scaling the Fisher matrix elements
    # Each observable contributes additively to the Fisher matrix
    # Scaling errors by factor s scales Fisher contribution by 1/s²

    # Compute individual Fisher matrices from each data type
    n = len(theta0)
    F_D = np.zeros((n, n))
    F_f = np.zeros((n, n))
    F_H = np.zeros((n, n))
    F_HK = np.zeros((n, n))

    theta0 = np.array(theta0, dtype=float)
    h = np.array([max(abs(t) * 0.01, 0.001) for t in theta0])

    # We'll compute each contribution separately using the component chi2s
    for i in range(n):
        for j in range(i, n):
            if i == j:
                hi = h[i]
                tp = theta0.copy(); tp[i] += hi
                tm = theta0.copy(); tm[i] -= hi

                dD, df, dH, dHK, _ = chi2_components(tp[0], tp[1])
                mD, mf, mH, mHK, _ = chi2_components(tm[0], tm[1])
                cD, cf, cH, cHK, _ = chi2_components(theta0[0], theta0[1])

                F_D[i, i] = 0.5 * (dD - 2*cD + mD) / hi**2
                F_f[i, i] = 0.5 * (df - 2*cf + mf) / hi**2
                F_H[i, i] = 0.5 * (dH - 2*cH + mH) / hi**2
                F_HK[i, i] = 0.5 * (dHK - 2*cHK + mHK) / hi**2
            else:
                hi, hj = h[i], h[j]
                pp = theta0.copy(); pp[i] += hi; pp[j] += hj
                pm = theta0.copy(); pm[i] += hi; pm[j] -= hj
                mp = theta0.copy(); mp[i] -= hi; mp[j] += hj
                mm = theta0.copy(); mm[i] -= hi; mm[j] -= hj

                ppD, ppf, ppH, ppHK, _ = chi2_components(pp[0], pp[1])
                pmD, pmf, pmH, pmHK, _ = chi2_components(pm[0], pm[1])
                mpD, mpf, mpH, mpHK, _ = chi2_components(mp[0], mp[1])
                mmD, mmf, mmH, mmHK, _ = chi2_components(mm[0], mm[1])

                for F_x, xpp, xpm, xmp, xmm in [
                    (F_D, ppD, pmD, mpD, mmD),
                    (F_f, ppf, pmf, mpf, mmf),
                    (F_H, ppH, pmH, mpH, mmH),
                    (F_HK, ppHK, pmHK, mpHK, mmHK),
                ]:
                    val = 0.5 * (xpp - xpm - xmp + xmm) / (4*hi*hj)
                    F_x[i, j] = val
                    F_x[j, i] = val

    # Scale and combine
    sD = scale_factors.get('D', 1.0)
    sf = scale_factors.get('f', 1.0)
    sH = scale_factors.get('H', 1.0)
    sHK = scale_factors.get('HK', 1.0)

    F_total = F_D / sD**2 + F_f / sf**2 + F_H / sH**2 + F_HK / sHK**2

    try:
        cov = np.linalg.inv(F_total)
        sigmas = np.sqrt(np.diag(cov))
        rho = cov[0, 1] / (sigmas[0] * sigmas[1]) if sigmas[0] > 0 and sigmas[1] > 0 else 0.0
    except np.linalg.LinAlgError:
        cov = np.full((n, n), np.inf)
        sigmas = np.full(n, np.inf)
        rho = 0.0

    return F_total, cov, sigmas, rho


# ============================================================
# DERIVED OBSERVABLE UNCERTAINTIES
# ============================================================

def derived_uncertainties(theta0, cov, eps0=0.0001):
    """
    Propagate parameter uncertainties to derived observables.

    Uses the Jacobian: σ²_O = J^T · Cov · J
    where J_i = ∂O/∂θ_i
    """
    theta0 = np.array(theta0, dtype=float)
    h = np.array([max(abs(t) * 0.01, 0.001) for t in theta0])

    results = {}

    # w₀ = effective dark energy equation of state
    def w0_func(zeta0, gamma_r):
        a = 1.0
        E = E_meridian(a, zeta0, gamma_r, eps0)
        Om_a = OMEGA_M0
        rho_DE = E**2 - Om_a - OMEGA_R0
        # Numerical derivative for w via E at a=0.99 and a=1.01
        a_p = 1.01; a_m = 0.99
        E_p = E_meridian(a_p, zeta0, gamma_r, eps0)
        E_m = E_meridian(a_m, zeta0, gamma_r, eps0)
        rho_p = E_p**2 - OMEGA_M0*a_p**(-3) - OMEGA_R0*a_p**(-4)
        rho_m = E_m**2 - OMEGA_M0*a_m**(-3) - OMEGA_R0*a_m**(-4)
        dln_rho = np.log(rho_p/rho_m) / np.log(a_p/a_m)
        return -1.0 - dln_rho / 3.0

    # H₀
    def H0_func(zeta0, gamma_r):
        return compute_H0_CMB(zeta0, gamma_r, eps0)

    # fσ₈(z=0.5)
    def fs8_func(zeta0, gamma_r):
        return compute_fsigma8(0.5, zeta0, gamma_r, eps0)

    for name, func in [('w0', w0_func), ('H0', H0_func), ('fsigma8_05', fs8_func)]:
        # Jacobian via central differences
        J = np.zeros(len(theta0))
        for i in range(len(theta0)):
            tp = theta0.copy(); tp[i] += h[i]
            tm = theta0.copy(); tm[i] -= h[i]
            J[i] = (func(tp[0], tp[1]) - func(tm[0], tm[1])) / (2*h[i])

        sigma_O = np.sqrt(J @ cov @ J)
        val = func(theta0[0], theta0[1])
        results[name] = (val, sigma_O)

    return results


# ============================================================
# MODEL COMPARISON STATISTICS
# ============================================================

def model_comparison(chi2_meridian, chi2_lcdm, k_meridian=8, k_lcdm=6, N_data=30):
    """
    Compute AIC, BIC, and Bayesian evidence estimates.

    k = number of parameters (6 base + 2 Meridian = 8 for Meridian)
    N_data = number of data points
    """
    # AIC
    AIC_m = chi2_meridian + 2 * k_meridian
    AIC_l = chi2_lcdm + 2 * k_lcdm
    delta_AIC = AIC_m - AIC_l

    # AICc (corrected for small samples)
    AICc_m = AIC_m + 2*k_meridian*(k_meridian+1) / max(N_data - k_meridian - 1, 1)
    AICc_l = AIC_l + 2*k_lcdm*(k_lcdm+1) / max(N_data - k_lcdm - 1, 1)
    delta_AICc = AICc_m - AICc_l

    # BIC
    BIC_m = chi2_meridian + k_meridian * np.log(N_data)
    BIC_l = chi2_lcdm + k_lcdm * np.log(N_data)
    delta_BIC = BIC_m - BIC_l

    # Akaike weight (probability of being the better model)
    w_m = np.exp(-0.5 * delta_AIC) / (1 + np.exp(-0.5 * delta_AIC))

    # Jeffreys scale for BIC
    if abs(delta_BIC) < 2:
        jeffreys = "Not worth more than a bare mention"
    elif abs(delta_BIC) < 6:
        jeffreys = "Positive evidence"
    elif abs(delta_BIC) < 10:
        jeffreys = "Strong evidence"
    else:
        jeffreys = "Very strong evidence"

    return {
        'AIC_meridian': AIC_m, 'AIC_lcdm': AIC_l, 'delta_AIC': delta_AIC,
        'AICc_meridian': AICc_m, 'AICc_lcdm': AICc_l, 'delta_AICc': delta_AICc,
        'BIC_meridian': BIC_m, 'BIC_lcdm': BIC_l, 'delta_BIC': delta_BIC,
        'akaike_weight': w_m,
        'jeffreys': jeffreys,
        'favored': 'Meridian' if delta_BIC < 0 else 'ΛCDM',
    }


# ============================================================
# MAIN ANALYSIS
# ============================================================

def main():
    print("=" * 80)
    print("  PROJECT MERIDIAN — D6.5: FISHER MATRIX & STATISTICAL ANALYSIS")
    print("=" * 80)

    # ---- Global optimum from D5.7 ----
    theta0 = [0.0446, 0.3987]  # [zeta0, gamma_r]
    param_names = ['ζ₀', 'γ_r']

    print(f"\n  Fiducial parameters (D5.7 global optimum):")
    print(f"    ε₀ = 0.0001 (fixed → 0)")
    for i, name in enumerate(param_names):
        print(f"    {name} = {theta0[i]:.4f}")

    # ---- Step 1: Verify χ² at fiducial ----
    print(f"\n  STEP 1: Verifying χ² at fiducial point...")
    chi2_D, chi2_f, chi2_H, chi2_HK, chi2_tot = chi2_components(theta0[0], theta0[1])
    print(f"    χ²_D (DESI BAO) = {chi2_D:.2f}")
    print(f"    χ²_f (fσ₈)     = {chi2_f:.2f}")
    print(f"    χ²_H (H₀)      = {chi2_H:.2f}")
    print(f"    χ²_HK (H&K)    = {chi2_HK:.2f}")
    print(f"    χ²_total        = {chi2_tot:.2f}")

    # ΛCDM reference
    chi2_D_l, chi2_f_l, chi2_H_l, chi2_HK_l, chi2_tot_l = chi2_components(0.0, 0.0)
    print(f"\n    ΛCDM reference:")
    print(f"    χ²_total (ΛCDM) = {chi2_tot_l:.2f}")
    print(f"    Δχ² = {chi2_tot - chi2_tot_l:.2f}")

    # ---- Step 2: Fisher Matrix ----
    print(f"\n  STEP 2: Computing Fisher matrix...")
    print(f"    Using central differences with h = 1% of parameter value")

    F, cov, sigmas, rho = fisher_matrix(theta0)

    print(f"\n    Fisher matrix F:")
    print(f"      F_11 (∂²χ²/∂ζ₀²)    = {F[0,0]:.1f}")
    print(f"      F_22 (∂²χ²/∂γ_r²)   = {F[1,1]:.1f}")
    print(f"      F_12 (∂²χ²/∂ζ₀∂γ_r) = {F[0,1]:.1f}")

    print(f"\n    Covariance matrix (F⁻¹):")
    print(f"      Cov_11 = {cov[0,0]:.6f}")
    print(f"      Cov_22 = {cov[1,1]:.6f}")
    print(f"      Cov_12 = {cov[0,1]:.6f}")

    print(f"\n    1σ marginalized uncertainties:")
    for i, name in enumerate(param_names):
        print(f"      σ({name}) = {sigmas[i]:.4f}  →  {name} = {theta0[i]:.4f} ± {sigmas[i]:.4f}")

    print(f"\n    Correlation coefficient:")
    print(f"      ρ(ζ₀, γ_r) = {rho:.3f}")

    if abs(rho) > 0.7:
        print(f"      → STRONG correlation — parameters are partially degenerate")
    elif abs(rho) > 0.3:
        print(f"      → MODERATE correlation")
    else:
        print(f"      → WEAK correlation — parameters are approximately independent")

    # ---- Step 3: Model Comparison ----
    print(f"\n  STEP 3: Model comparison statistics")

    N_data = len(DESI_BAO_DATA) + len(FSIGMA8_DATA) + 1 + 1  # BAO + fσ₈ + H₀ + H&K
    comp = model_comparison(chi2_tot, chi2_tot_l, k_meridian=8, k_lcdm=6, N_data=N_data)

    print(f"\n    N_data = {N_data}")
    print(f"    k_Meridian = 8 (6 base + ζ₀ + γ_r)")
    print(f"    k_ΛCDM = 6 (base)")
    print(f"\n    AIC:")
    print(f"      AIC_Meridian = {comp['AIC_meridian']:.2f}")
    print(f"      AIC_ΛCDM    = {comp['AIC_lcdm']:.2f}")
    print(f"      ΔAIC = {comp['delta_AIC']:.2f}  (< -10: decisive)")
    print(f"\n    AICc (small-sample corrected):")
    print(f"      ΔAICc = {comp['delta_AICc']:.2f}")
    print(f"\n    BIC:")
    print(f"      BIC_Meridian = {comp['BIC_meridian']:.2f}")
    print(f"      BIC_ΛCDM    = {comp['BIC_lcdm']:.2f}")
    print(f"      ΔBIC = {comp['delta_BIC']:.2f}")
    print(f"      Jeffreys scale: {comp['jeffreys']}")
    print(f"      Favored model: {comp['favored']}")
    print(f"\n    Akaike weight for Meridian: {comp['akaike_weight']:.4f}")

    # ---- Step 4: Derived observable uncertainties ----
    print(f"\n  STEP 4: Derived observable uncertainties")

    derived = derived_uncertainties(theta0, cov)

    for name, (val, sig) in derived.items():
        if name == 'w0':
            print(f"    w₀ = {val:.4f} ± {sig:.4f}")
        elif name == 'H0':
            print(f"    H₀ = {val:.2f} ± {sig:.2f} km/s/Mpc")
        elif name == 'fsigma8_05':
            print(f"    fσ₈(z=0.5) = {val:.4f} ± {sig:.4f}")

    # ---- Step 5: Future survey forecasts ----
    print(f"\n  STEP 5: Future survey forecasts")

    forecasts = {
        'Current (DESI Y1)': {'D': 1.0, 'f': 1.0, 'H': 1.0, 'HK': 1.0},
        'DESI Y5 (full)':    {'D': 0.4, 'f': 0.5, 'H': 0.9, 'HK': 0.5},
        'Euclid + DESI':     {'D': 0.25, 'f': 0.3, 'H': 0.7, 'HK': 0.3},
        'Stage V (2035+)':   {'D': 0.15, 'f': 0.2, 'H': 0.5, 'HK': 0.2},
    }

    print(f"\n    {'Survey':>25} | {'σ(ζ₀)':>8} | {'σ(γ_r)':>8} | {'σ(w₀)':>8} | {'ρ(ζ₀,γ_r)':>10}")
    print(f"    {'-'*70}")

    for label, scales in forecasts.items():
        F_fc, cov_fc, sigmas_fc, rho_fc = fisher_forecast(theta0, scales, label)
        # Propagate to w₀
        h_arr = np.array([max(abs(t)*0.01, 0.001) for t in theta0])
        J_w0 = np.zeros(2)
        for i in range(2):
            tp = np.array(theta0, dtype=float); tp[i] += h_arr[i]
            tm = np.array(theta0, dtype=float); tm[i] -= h_arr[i]
            a = 1.0
            # Approximate w₀ from E(z) structure
            E_p = E_meridian(0.99, tp[0], tp[1])
            E_m = E_meridian(0.99, tm[0], tm[1])
            E0_p = E_meridian(1.0, tp[0], tp[1])
            E0_m = E_meridian(1.0, tm[0], tm[1])
            rho_p = E_p**2 - OMEGA_M0*0.99**(-3) - OMEGA_R0*0.99**(-4)
            rho_m = E_m**2 - OMEGA_M0*0.99**(-3) - OMEGA_R0*0.99**(-4)
            rho0_p = E0_p**2 - OMEGA_M0 - OMEGA_R0
            rho0_m = E0_m**2 - OMEGA_M0 - OMEGA_R0
            w_p = -1.0 - np.log(rho_p/rho0_p) / (3.0*np.log(0.99))
            w_m = -1.0 - np.log(rho_m/rho0_m) / (3.0*np.log(0.99))
            J_w0[i] = (w_p - w_m) / (2*h_arr[i])

        sigma_w0 = np.sqrt(max(J_w0 @ cov_fc @ J_w0, 0))
        print(f"    {label:>25} | {sigmas_fc[0]:8.4f} | {sigmas_fc[1]:8.4f} | {sigma_w0:8.4f} | {rho_fc:10.3f}")

    # ---- Summary ----
    print(f"\n  {'='*80}")
    print(f"  SUMMARY")
    print(f"  {'='*80}")
    print(f"\n  Global optimum: ζ₀ = {theta0[0]:.4f} ± {sigmas[0]:.4f}, γ_r = {theta0[1]:.4f} ± {sigmas[1]:.4f}")
    print(f"  Correlation: ρ = {rho:.3f}")
    print(f"  Δχ² vs ΛCDM: {chi2_tot - chi2_tot_l:.2f} ({2} extra parameters)")
    print(f"  ΔBIC: {comp['delta_BIC']:.2f} ({comp['jeffreys']})")
    print(f"  Detection significance: {np.sqrt(abs(chi2_tot_l - chi2_tot)):.1f}σ")
    print(f"\n  🦞🧍💜🔥♾️")

    return {
        'F': F, 'cov': cov, 'sigmas': sigmas, 'rho': rho,
        'chi2': chi2_tot, 'chi2_lcdm': chi2_tot_l,
        'comparison': comp, 'derived': derived,
    }


if __name__ == '__main__':
    main()
