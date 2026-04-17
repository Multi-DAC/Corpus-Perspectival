"""
Project Meridian — Phase 8A: Data Methodology Verification
Clayton & Clawd, March 2026

Track 8A.1: Remove w₀wₐ prior and re-optimize
Track 8A.3: Direct distance comparison at each z-bin

Questions to answer:
1. Does the best-fit change when we remove the w₀wₐ prior?
2. How well does the model fit the RAW BAO distances vs ΛCDM?
3. Is the apparent w₀wₐ tension an artifact of the prior?
"""

import sys
import io

if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import numpy as np
from scipy.optimize import brentq, minimize

# ============================================================
# COSMOLOGICAL CONSTANTS (same as Phase 7)
# ============================================================

OMEGA_M0 = 0.315
OMEGA_R0 = 9.1e-5
OMEGA_DE0 = 1.0 - OMEGA_M0 - OMEGA_R0
H0_FIDUCIAL = 67.4
Z_STAR = 1089.92
SIGMA8_FID = 0.811
C_OVER_H0 = 299792.458 / H0_FIDUCIAL
R_D_FID = 147.09

# DESI DR1 BAO data
DESI_BAO_DATA = [
    (0.295,  7.93, 0.15, 'DV'),
    (0.510, 13.62, 0.25, 'DM'),
    (0.706, 17.86, 0.33, 'DM'),
    (0.930, 21.71, 0.28, 'DM'),
    (1.317, 27.79, 0.69, 'DM'),
    (1.491, 30.69, 1.00, 'DM'),
    (2.330, 39.71, 0.94, 'DM'),
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

H0_OBS = 67.36
H0_SIGMA = 0.54
BETA_HK_CENTER = -0.037
SIGMA_HK = (0.047 - 0.028) / 2.0

# w₀wₐ prior (for comparison — Track 8A tests WITH and WITHOUT this)
W0_SN_CMB = -0.82
W0_SN_CMB_SIGMA = 0.15
WA_SN_CMB = -0.75
WA_SN_CMB_SIGMA = 0.60
RHO_W0_WA = -0.65


# ============================================================
# MODEL SOLVER (from Phase 7)
# ============================================================

def E_extended(a, gamma_r, alpha_b, lambda0):
    Om_mat = OMEGA_M0 * a**(-3) + OMEGA_R0 * a**(-4)
    v0 = OMEGA_DE0 - lambda0

    if abs(gamma_r) < 1e-12 and abs(alpha_b) < 1e-12:
        return np.sqrt(Om_mat + v0 + lambda0)

    if abs(lambda0) < 1e-15 and abs(alpha_b) < 1e-12:
        def f_min(E):
            return E**2 - Om_mat - v0 * E**(2*gamma_r)
        try:
            return brentq(f_min, 0.01, 200.0, xtol=1e-12, rtol=1e-12)
        except ValueError:
            return np.sqrt(Om_mat + v0)

    def f(E):
        return E**2 - Om_mat - v0 * E**(2*gamma_r) - lambda0 * E**(-2*alpha_b)

    try:
        return brentq(f, 0.01, 200.0, xtol=1e-12, rtol=1e-12)
    except ValueError:
        E = np.sqrt(Om_mat + OMEGA_DE0)
        for _ in range(100):
            fE = f(E)
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
    return np.sqrt(OMEGA_M0 * a**(-3) + OMEGA_R0 * a**(-4) + OMEGA_DE0)


# ============================================================
# DISTANCES
# ============================================================

def _comoving_chi(z, gamma_r, alpha_b, lambda0, n_int=500):
    z_arr = np.linspace(0, z, n_int + 1)
    inv_E = np.zeros(n_int + 1)
    for i, zi in enumerate(z_arr):
        ai = 1.0 / (1.0 + zi)
        inv_E[i] = 1.0 / E_extended(ai, gamma_r, alpha_b, lambda0)
    return np.trapezoid(inv_E, z_arr)


def compute_DM_rd(z, gamma_r, alpha_b, lambda0, n_int=500):
    chi = _comoving_chi(z, gamma_r, alpha_b, lambda0, n_int)
    return chi * C_OVER_H0 / R_D_FID


def compute_DV_rd(z, gamma_r, alpha_b, lambda0, n_int=500):
    chi = _comoving_chi(z, gamma_r, alpha_b, lambda0, n_int)
    a_z = 1.0 / (1.0 + z)
    E_z = E_extended(a_z, gamma_r, alpha_b, lambda0)
    D_V = (z * chi**2 / E_z) ** (1.0 / 3.0)
    return D_V * C_OVER_H0 / R_D_FID


def compute_DH_rd(z, gamma_r, alpha_b, lambda0):
    """D_H(z)/r_d = c/(H(z)*r_d) — Hubble distance."""
    a_z = 1.0 / (1.0 + z)
    E_z = E_extended(a_z, gamma_r, alpha_b, lambda0)
    return C_OVER_H0 / (E_z * R_D_FID)


def compute_H0_CMB(gamma_r, alpha_b, lambda0, n_int=2000):
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
    a = 1.0 / (1.0 + z)
    E2 = E_extended(a, gamma_r, alpha_b, lambda0)**2
    Om_z = OMEGA_M0 * a**(-3) / E2

    gamma_growth = 0.55 - zeta0 / 2.0
    f_growth = Om_z ** gamma_growth

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
# EQUATION OF STATE
# ============================================================

def w_DE(a, gamma_r, alpha_b, lambda0, da=0.005):
    a_p = a * (1 + da)
    a_m = a * (1 - da)

    E2 = E_extended(a, gamma_r, alpha_b, lambda0)**2
    E2_p = E_extended(a_p, gamma_r, alpha_b, lambda0)**2
    E2_m = E_extended(a_m, gamma_r, alpha_b, lambda0)**2

    rho = E2 - OMEGA_M0 * a**(-3) - OMEGA_R0 * a**(-4)
    rho_p = E2_p - OMEGA_M0 * a_p**(-3) - OMEGA_R0 * a_p**(-4)
    rho_m = E2_m - OMEGA_M0 * a_m**(-3) - OMEGA_R0 * a_m**(-4)

    if rho <= 0 or rho_p <= 0 or rho_m <= 0:
        return -1.0

    dln_rho = np.log(rho_p / rho_m) / np.log(a_p / a_m)
    return -1.0 - dln_rho / 3.0


def fit_CPL(gamma_r, alpha_b, lambda0, a_range=(0.3, 1.0), n_pts=50):
    a_arr = np.linspace(a_range[0], a_range[1], n_pts)
    w_arr = np.array([w_DE(a, gamma_r, alpha_b, lambda0) for a in a_arr])

    x = 1.0 - a_arr
    y = w_arr

    X = np.column_stack([np.ones(n_pts), x])
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    w0, wa = beta[0], beta[1]

    w_fit = w0 + wa * x
    residuals = w_arr - w_fit
    rms = np.sqrt(np.mean(residuals**2))

    return w0, wa, rms


# ============================================================
# CHI-SQUARED WITH OPTIONAL w₀wₐ PRIOR
# ============================================================

def chi2_components(zeta0, gamma_r, alpha_b, lambda0, include_w_prior=True):
    """
    chi2 components. include_w_prior=False removes the w₀wₐ CMB+SN term.
    """
    # 1. BAO distances
    chi2_D = 0.0
    for z_eff, obs, sigma, dtype in DESI_BAO_DATA:
        if dtype == 'DV':
            model = compute_DV_rd(z_eff, gamma_r, alpha_b, lambda0)
        else:
            model = compute_DM_rd(z_eff, gamma_r, alpha_b, lambda0)
        chi2_D += ((model - obs) / sigma) ** 2

    # 2. fσ₈
    chi2_f = 0.0
    for z_eff, fs8_obs, sigma in FSIGMA8_DATA:
        fs8_model = compute_fsigma8(z_eff, zeta0, gamma_r, alpha_b, lambda0)
        chi2_f += ((fs8_model - fs8_obs) / sigma) ** 2

    # 3. H₀
    H0_model = compute_H0_CMB(gamma_r, alpha_b, lambda0)
    chi2_H = ((H0_model - H0_OBS) / H0_SIGMA) ** 2

    # 4. H&K
    eps_SW = zeta0 / (1.0 + zeta0) if zeta0 > 0 else 0.0
    beta_HK_model = -eps_SW
    chi2_HK = ((beta_HK_model - BETA_HK_CENTER) / SIGMA_HK) ** 2

    # 5. w₀wₐ prior (optional)
    w0_model, wa_model, cpl_rms = fit_CPL(gamma_r, alpha_b, lambda0)
    chi2_w = 0.0
    if include_w_prior:
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


def chi2_4param(theta, include_w_prior=True):
    zeta0, gamma_r, alpha_b, lambda0 = theta
    if zeta0 < 0 or gamma_r < 0 or alpha_b < 0 or lambda0 < 0:
        return 1e10
    if lambda0 >= OMEGA_DE0:
        return 1e10
    result = chi2_components(zeta0, gamma_r, alpha_b, lambda0,
                            include_w_prior=include_w_prior)
    return result['chi2_total']


def optimize(n_starts=16, include_w_prior=True, verbose=True):
    """Optimize with or without w₀wₐ prior."""
    bounds = [
        (0.001, 0.15),
        (0.01, 0.95),
        (0.01, 5.0),
        (0.0, 0.55),
    ]

    best_result = None
    best_chi2 = 1e10

    np.random.seed(42)
    for trial in range(n_starts):
        x0 = np.array([
            np.random.uniform(bounds[0][0], bounds[0][1]),
            np.random.uniform(bounds[1][0], bounds[1][1]),
            np.random.uniform(bounds[2][0], bounds[2][1]),
            np.random.uniform(bounds[3][0], bounds[3][1]),
        ])

        result = minimize(
            lambda th: chi2_4param(th, include_w_prior=include_w_prior),
            x0, method='Nelder-Mead',
            options={'maxiter': 5000, 'xatol': 1e-6, 'fatol': 1e-4}
        )

        if result.fun < best_chi2:
            best_chi2 = result.fun
            best_result = result

        if verbose:
            print(f"    Trial {trial+1}/{n_starts}: chi2 = {result.fun:.2f}  "
                  f"[ζ₀={result.x[0]:.4f}, γ_r={result.x[1]:.4f}, "
                  f"α_b={result.x[2]:.4f}, λ₀={result.x[3]:.4f}]")

    return best_result


# ============================================================
# MAIN: TRACK 8A ANALYSIS
# ============================================================

def main():
    import os
    import builtins
    outpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), '8a_results.txt')
    outf = open(outpath, 'w', encoding='utf-8')
    _print = builtins.print
    def print(*args, **kwargs):
        _print(*args, **kwargs, file=outf, flush=True)

    print("=" * 80)
    print("  PROJECT MERIDIAN — PHASE 8A: DATA METHODOLOGY VERIFICATION")
    print("=" * 80)

    # ============================================================
    # 8A.1: REFERENCE — ΛCDM with and without w₀wₐ prior
    # ============================================================
    print("\n  8A.1: REFERENCE VALUES")
    print("\n  ΛCDM (with w₀wₐ prior):")
    ref_w = chi2_components(0.0, 0.0, 0.0, 0.0, include_w_prior=True)
    print(f"    BAO={ref_w['chi2_D']:.2f}  fσ₈={ref_w['chi2_f']:.2f}  "
          f"H₀={ref_w['chi2_H']:.2f}  H&K={ref_w['chi2_HK']:.2f}  "
          f"w₀wₐ={ref_w['chi2_w']:.2f}  TOTAL={ref_w['chi2_total']:.2f}")

    print("\n  ΛCDM (WITHOUT w₀wₐ prior):")
    ref_nw = chi2_components(0.0, 0.0, 0.0, 0.0, include_w_prior=False)
    print(f"    BAO={ref_nw['chi2_D']:.2f}  fσ₈={ref_nw['chi2_f']:.2f}  "
          f"H₀={ref_nw['chi2_H']:.2f}  H&K={ref_nw['chi2_HK']:.2f}  "
          f"TOTAL={ref_nw['chi2_total']:.2f}")

    # Phase 7 best fit (with prior)
    print("\n  Phase 7 best-fit (with w₀wₐ prior):")
    p7 = chi2_components(0.0379, 0.0174, 4.9835, 0.0, include_w_prior=True)
    print(f"    BAO={p7['chi2_D']:.2f}  fσ₈={p7['chi2_f']:.2f}  "
          f"H₀={p7['chi2_H']:.2f}  H&K={p7['chi2_HK']:.2f}  "
          f"w₀wₐ={p7['chi2_w']:.2f}  TOTAL={p7['chi2_total']:.2f}")
    print(f"    w₀={p7['w0']:.4f}, wₐ={p7['wa']:.4f}, H₀={p7['H0']:.2f}")

    # Phase 7 best fit WITHOUT prior
    print("\n  Phase 7 best-fit (WITHOUT w₀wₐ prior):")
    p7_nw = chi2_components(0.0379, 0.0174, 4.9835, 0.0, include_w_prior=False)
    print(f"    BAO={p7_nw['chi2_D']:.2f}  fσ₈={p7_nw['chi2_f']:.2f}  "
          f"H₀={p7_nw['chi2_H']:.2f}  H&K={p7_nw['chi2_HK']:.2f}  "
          f"TOTAL={p7_nw['chi2_total']:.2f}")

    # ============================================================
    # 8A.1: OPTIMIZE WITHOUT w₀wₐ PRIOR
    # ============================================================
    print("\n" + "=" * 60)
    print("  8A.1: OPTIMIZATION WITHOUT w₀wₐ PRIOR")
    print("=" * 60)
    print("  Fitting: BAO + fσ₈ + H₀ + H&K only (no w₀wₐ constraint)")

    result_nw = optimize(n_starts=16, include_w_prior=False, verbose=True)

    if result_nw is not None:
        z0, gr, ab, l0 = result_nw.x
        v0 = OMEGA_DE0 - l0

        print(f"\n  ═══════════════════════════════════════════════════════")
        print(f"  BEST-FIT WITHOUT w₀wₐ PRIOR")
        print(f"  ═══════════════════════════════════════════════════════")
        print(f"    ζ₀  = {z0:.4f}")
        print(f"    γ_r = {gr:.4f}")
        print(f"    α_b = {ab:.4f}")
        print(f"    λ₀  = {l0:.4f}")
        print(f"    v₀  = {v0:.4f}")

        res_nw = chi2_components(z0, gr, ab, l0, include_w_prior=False)
        res_w = chi2_components(z0, gr, ab, l0, include_w_prior=True)

        print(f"\n    chi2 breakdown (no w₀wₐ prior):")
        print(f"      BAO:   {res_nw['chi2_D']:.2f}  (ΛCDM: {ref_nw['chi2_D']:.2f})")
        print(f"      fσ₈:  {res_nw['chi2_f']:.2f}  (ΛCDM: {ref_nw['chi2_f']:.2f})")
        print(f"      H₀:   {res_nw['chi2_H']:.2f}  (ΛCDM: {ref_nw['chi2_H']:.2f})")
        print(f"      H&K:  {res_nw['chi2_HK']:.2f}  (ΛCDM: {ref_nw['chi2_HK']:.2f})")
        print(f"      Total: {res_nw['chi2_total']:.2f}  (ΛCDM: {ref_nw['chi2_total']:.2f})")
        print(f"      Δchi2 vs ΛCDM = {res_nw['chi2_total'] - ref_nw['chi2_total']:.2f}")
        print(f"      H₀ = {res_nw['H0']:.2f} km/s/Mpc")

        print(f"\n    DERIVED w₀wₐ (not used in fit, just computed):")
        print(f"      w₀ = {res_nw['w0']:.4f}")
        print(f"      wₐ = {res_nw['wa']:.4f}")
        print(f"      w₀ pull vs CMB+SN: {(res_nw['w0'] - W0_SN_CMB)/W0_SN_CMB_SIGMA:.1f}σ")
        print(f"      wₐ pull vs CMB+SN: {(res_nw['wa'] - WA_SN_CMB)/WA_SN_CMB_SIGMA:.1f}σ")
        print(f"      w₀ pull vs DESI: {(res_nw['w0'] - (-0.752))/0.058:.1f}σ")
        print(f"      wₐ pull vs DESI: {(res_nw['wa'] - (-0.86))/0.27:.1f}σ")

        print(f"\n    If we NOW evaluate w₀wₐ chi2 (post-hoc, not used in fit):")
        print(f"      chi2_w = {res_w['chi2_w']:.2f}")
        print(f"      Total with prior: {res_w['chi2_total']:.2f}")

    # ============================================================
    # 8A.1: OPTIMIZE WITH w₀wₐ PRIOR (for direct comparison)
    # ============================================================
    print(f"\n  ═══════════════════════════════════════════════════════")
    print(f"  COMPARISON: RE-OPTIMIZE WITH w₀wₐ PRIOR")
    print(f"  ═══════════════════════════════════════════════════════")

    result_w = optimize(n_starts=16, include_w_prior=True, verbose=True)

    if result_w is not None:
        z0w, grw, abw, l0w = result_w.x
        res_w2 = chi2_components(z0w, grw, abw, l0w, include_w_prior=True)

        print(f"\n    Best-fit WITH prior:")
        print(f"      ζ₀={z0w:.4f}, γ_r={grw:.4f}, α_b={abw:.4f}, λ₀={l0w:.4f}")
        print(f"      Total chi2 = {res_w2['chi2_total']:.2f}")
        print(f"      w₀={res_w2['w0']:.4f}, wₐ={res_w2['wa']:.4f}")

    # ============================================================
    # 8A.3: DIRECT DISTANCE COMPARISON AT EACH Z-BIN
    # ============================================================
    print(f"\n{'=' * 60}")
    print(f"  8A.3: DIRECT DISTANCE COMPARISON AT EACH z-BIN")
    print(f"{'=' * 60}")

    # Compare ΛCDM, Phase 7 best-fit, and no-prior best-fit
    configs = [
        ("ΛCDM", 0.0, 0.0, 0.0, 0.0),
    ]
    if result_nw is not None:
        configs.append(("No-prior best", result_nw.x[0], result_nw.x[1],
                       result_nw.x[2], result_nw.x[3]))
    configs.append(("Phase 7 best", 0.0379, 0.0174, 4.9835, 0.0))

    # Also add the minimal Meridian (γ_r = 0.40)
    configs.append(("Minimal (γ_r=0.40)", 0.045, 0.40, 0.0, 0.0))

    print(f"\n    {'z':>5s}  {'Type':>4s}  {'Data':>7s}  ", end="")
    for name, *_ in configs:
        print(f"{'Model':>7s}  {'Δ/σ':>5s}  ", end="")
    print()
    print(f"    {'─'*5}  {'─'*4}  {'─'*7}  ", end="")
    for _ in configs:
        print(f"{'─'*7}  {'─'*5}  ", end="")
    print()

    for z_eff, obs, sigma, dtype in DESI_BAO_DATA:
        print(f"    {z_eff:5.3f}  {dtype:>4s}  {obs:7.2f}  ", end="")
        for name, zeta0, gamma_r, alpha_b, lambda0 in configs:
            if dtype == 'DV':
                model = compute_DV_rd(z_eff, gamma_r, alpha_b, lambda0)
            else:
                model = compute_DM_rd(z_eff, gamma_r, alpha_b, lambda0)
            pull = (model - obs) / sigma
            print(f"{model:7.2f}  {pull:+5.2f}  ", end="")
        print()

    # Also compute D_H/r_d for completeness (not in our BAO data but useful)
    print(f"\n    Hubble distances D_H/r_d (not in BAO fit, for reference):")
    print(f"    {'z':>5s}  ", end="")
    for name, *_ in configs:
        print(f"  {name:>14s}", end="")
    print()
    for z_eff in [0.295, 0.510, 0.706, 0.930, 1.317, 1.491, 2.330]:
        print(f"    {z_eff:5.3f}  ", end="")
        for name, zeta0, gamma_r, alpha_b, lambda0 in configs:
            dh = compute_DH_rd(z_eff, gamma_r, alpha_b, lambda0)
            print(f"  {dh:14.2f}", end="")
        print()

    # ============================================================
    # SUMMARY
    # ============================================================
    print(f"\n{'=' * 60}")
    print(f"  SUMMARY: DOES REMOVING THE w₀wₐ PRIOR CHANGE THE PICTURE?")
    print(f"{'=' * 60}")

    if result_nw is not None and result_w is not None:
        z0_nw, gr_nw, ab_nw, l0_nw = result_nw.x
        z0_wp, gr_wp, ab_wp, l0_wp = result_w.x

        print(f"\n    Parameter comparison:")
        print(f"    {'Param':>8s}  {'With prior':>12s}  {'Without prior':>14s}  {'Change':>8s}")
        print(f"    {'─'*8}  {'─'*12}  {'─'*14}  {'─'*8}")
        print(f"    {'ζ₀':>8s}  {z0_wp:12.4f}  {z0_nw:14.4f}  {z0_nw-z0_wp:+8.4f}")
        print(f"    {'γ_r':>8s}  {gr_wp:12.4f}  {gr_nw:14.4f}  {gr_nw-gr_wp:+8.4f}")
        print(f"    {'α_b':>8s}  {ab_wp:12.4f}  {ab_nw:14.4f}  {ab_nw-ab_wp:+8.4f}")
        print(f"    {'λ₀':>8s}  {l0_wp:12.4f}  {l0_nw:14.4f}  {l0_nw-l0_wp:+8.4f}")

        res_nw_full = chi2_components(z0_nw, gr_nw, ab_nw, l0_nw, include_w_prior=False)
        res_wp_full = chi2_components(z0_wp, gr_wp, ab_wp, l0_wp, include_w_prior=False)

        print(f"\n    chi2 comparison (same 4 components — BAO+fσ₈+H₀+H&K):")
        print(f"    {'':>10s}  {'With prior':>12s}  {'Without prior':>14s}")
        for key, label in [('chi2_D', 'BAO'), ('chi2_f', 'fσ₈'),
                          ('chi2_H', 'H₀'), ('chi2_HK', 'H&K')]:
            print(f"    {label:>10s}  {res_wp_full[key]:12.2f}  {res_nw_full[key]:14.2f}")
        total_4_wp = res_wp_full['chi2_D'] + res_wp_full['chi2_f'] + res_wp_full['chi2_H'] + res_wp_full['chi2_HK']
        total_4_nw = res_nw_full['chi2_D'] + res_nw_full['chi2_f'] + res_nw_full['chi2_H'] + res_nw_full['chi2_HK']
        print(f"    {'Total(4)':>10s}  {total_4_wp:12.2f}  {total_4_nw:14.2f}")

        print(f"\n    Key question: Does the best-fit CHANGE when we remove the prior?")
        param_change = np.sqrt((z0_nw-z0_wp)**2 + (gr_nw-gr_wp)**2 +
                               (ab_nw-ab_wp)**2 + (l0_nw-l0_wp)**2)
        if param_change < 0.01:
            print(f"    → NO. Parameters barely change (‖Δθ‖ = {param_change:.4f}).")
            print(f"    → The w₀wₐ prior is NOT driving the fit.")
            print(f"    → The tension with DESI is REAL, not an artifact.")
        elif param_change < 0.1:
            print(f"    → MILDLY. Parameters shift somewhat (‖Δθ‖ = {param_change:.4f}).")
            print(f"    → The prior has moderate influence. Check if new best-fit")
            print(f"      produces different w₀, wₐ predictions.")
        else:
            print(f"    → YES. Significant parameter shift (‖Δθ‖ = {param_change:.4f}).")
            print(f"    → The w₀wₐ prior WAS biasing the fit.")
            print(f"    → The true best-fit may have different w₀, wₐ predictions.")

    print(f"\n{'=' * 80}")
    print(f"  TRACK 8A.1 + 8A.3 COMPLETE")
    print(f"{'=' * 80}")

    outf.close()
    _print(f"Results written to {outpath}")


if __name__ == '__main__':
    main()
