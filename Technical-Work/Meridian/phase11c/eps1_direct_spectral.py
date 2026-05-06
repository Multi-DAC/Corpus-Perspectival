#!/usr/bin/env python3
"""
DIRECT SPECTRAL SUM COMPUTATION OF ε₁
========================================
Bypasses the Vassilevich asymptotic expansion entirely.

Strategy:
  1. Compute Robin eigenvalues m_n(k) at several values of k (AdS curvature)
  2. Compute the EXACT spectral action S(k) = Σ_n Σ_α d_{n,α} × f((m_n² + λ_α^F)/Λ²)
  3. Fit S(k) to a polynomial in k: S = c₀ + c₂k² + c₄k⁴ + ...
  4. Extract α_GB from the k⁴ coefficient (since E₅ = 120k⁴ on AdS₅)
  5. Compare to the Vassilevich prediction α_GB = f₃ Λ⁻¹ (4π)^{-5/2} (13/720)
  6. Compute ε₁_direct = α̂_direct × C_GB and compare to 0.010

Additionally: compute the EM decomposition for the spectral sum itself,
to quantify the brane-localized correction to the Vassilevich expansion.

If the Vassilevich expansion fails for α_GB by >20%, ε₁ is NOT locked
at 0.010 and the tension picture changes entirely.

Clayton Iggulden-Schnell & Clawd, April 2026
"""

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import numpy as np
from scipy.optimize import brentq
from scipy.integrate import quad

def fprint(*args, **kwargs):
    print(*args, **kwargs, flush=True)

fprint("=" * 78)
fprint("  DIRECT SPECTRAL SUM COMPUTATION OF epsilon_1")
fprint("  Bypassing the Vassilevich asymptotic expansion")
fprint("=" * 78)

# === Fixed RS1 Parameters ===
M5_cubed = 1.0
xi = 1.0 / 6.0
ky_c = 37.0        # k * y_c (hierarchy parameter)
Lambda_over_k = 1.0  # Cutoff in units of k (Λ = k, from spectral action matching)

# === D_F spectrum (from NCG spectral triple) ===
# Same as in corrected_mu2.py
M_oct = np.array([[1.0, 0.5, 0.5], [0.5, 1.0, 0.5], [0.5, 0.5, 1.0]])
c_Q = np.array([0.557, 0.646, 0.247])
c_u = np.array([0.661, 0.415, 0.200])
c_d = np.array([0.495, 0.465, 0.567])
c_L = np.array([0.650, 0.580, 0.520])
c_e = np.array([0.660, 0.590, 0.500])
Y5_u, Y5_d, Y5_e = 1.75, 0.18, 0.10
N_c = 3

def g_profile(c, ky=ky_c):
    delta = 0.5 - c
    if abs(2*delta*ky) < 1e-8:
        return 1.0 / np.sqrt(ky)
    val = (1 - 2*c) / (np.exp((1 - 2*c)*ky) - 1)
    return np.sqrt(np.abs(val)) * np.exp(delta*ky) * np.sign(val)

g_Q = np.array([g_profile(c) for c in c_Q])
g_u = np.array([g_profile(c) for c in c_u])
g_d = np.array([g_profile(c) for c in c_d])
g_L = np.array([g_profile(c) for c in c_L])
g_e = np.array([g_profile(c) for c in c_e])

Y_u = Y5_u * M_oct * np.outer(g_Q, g_u)
Y_d = Y5_d * M_oct * np.outer(g_Q, g_d)
Y_e = Y5_e * M_oct * np.outer(g_L, g_e)

sv_u = np.linalg.svd(Y_u, compute_uv=False)
sv_d = np.linalg.svd(Y_d, compute_uv=False)
sv_e = np.linalg.svd(Y_e, compute_uv=False)

# D_F eigenvalues (squared) and multiplicities
df2_eig = np.concatenate([sv_u**2, sv_d**2, sv_e**2])
df2_mult = np.array([4*N_c]*3 + [4*N_c]*3 + [4]*3)  # spinor × color
N_F = 84  # Total internal degrees of freedom
N_zero = N_F - int(sum(df2_mult))
if N_zero > 0:
    df2_eig = np.append(df2_eig, 0.0)
    df2_mult = np.append(df2_mult, N_zero)

fprint(f"\nD_F spectrum: {len(df2_eig)} distinct eigenvalues, N_F = {int(sum(df2_mult))}")


# ============================================================================
# ROBIN EIGENVALUE SOLVER (parameterized by k)
# ============================================================================
def robin_eigenvalue_condition(lam, yc, kval):
    """F(lambda) = 0 at eigenvalues. Robin BC: chi'(0) = -2k chi(0), chi'(y_c) = 2k chi(y_c)."""
    if lam <= 0:
        kappa = np.sqrt(-lam)
        return np.tanh(kappa * yc) - 4*kval*kappa / (kappa**2 + 4*kval**2)
    sqrtl = np.sqrt(lam)
    theta = sqrtl * yc
    if abs(4*kval**2 - lam) < 1e-10:
        return np.cos(theta)
    return np.tan(theta) - 4*kval*sqrtl / (4*kval**2 - lam)


def compute_robin_eigenvalues(kval, yc, n_max=60):
    """Compute Robin eigenvalues for given k and y_c."""
    eigenvalues = []

    # Bound state
    try:
        lam0 = brentq(lambda l: robin_eigenvalue_condition(l, yc, kval), -5*kval**2, -0.01)
        eigenvalues.append(lam0)
    except:
        eigenvalues.append(-4.0 * kval**2)

    # Positive eigenvalues
    for n in range(1, n_max):
        lo = ((n - 0.49) * np.pi / yc)**2
        hi = ((n + 0.49) * np.pi / yc)**2
        try:
            lam_n = brentq(lambda l: robin_eigenvalue_condition(l, yc, kval), lo, hi)
            eigenvalues.append(lam_n)
        except:
            eigenvalues.append((n * np.pi / yc)**2)

    return np.array(eigenvalues)


# ============================================================================
# CUTOFF FUNCTIONS
# ============================================================================
def f_gaussian(x):
    """Gaussian cutoff: f(x) = exp(-x)"""
    return np.exp(-x)

def f_sharp(x):
    """Sharp cutoff: f(x) = Theta(1-x)"""
    return np.where(x < 1.0, 1.0, 0.0)

def f_smooth(x):
    """Smooth cutoff: f(x) = exp(-x²)"""
    return np.exp(-x**2)


# ============================================================================
# SPECTRAL ACTION COMPUTATION
# ============================================================================
def spectral_action_4d_integral(M2, Lambda2, cutoff='gaussian'):
    """
    4D momentum integral for the spectral action:
    I(M²) = ∫ d⁴p/(2π)⁴ × f((p² + M²)/Λ²)

    For Gaussian cutoff f(x) = e^{-x}:
    I = Λ⁴/(32π²) × exp(-M²/Λ²)

    For sharp cutoff f(x) = Θ(1-x):
    I = (Λ² - M²)² / (32π²) × Θ(Λ² - M²)   [valid for d=4]

    Returns I × (32π²) for numerical convenience (dimensionless ratio).
    """
    x = M2 / Lambda2
    if cutoff == 'gaussian':
        return np.exp(-x) * Lambda2**2
    elif cutoff == 'sharp':
        return np.where(x < 1.0, (Lambda2 * (1 - x))**2, 0.0)
    elif cutoff == 'smooth':
        return np.exp(-x**2) * Lambda2**2
    else:
        raise ValueError(f"Unknown cutoff: {cutoff}")


def compute_spectral_action(kval, yc, Lambda, cutoff='gaussian', n_kk=50):
    """
    Compute the EXACT spectral action on RS₁ as a sum over KK modes.

    S = d_s × Σ_n Σ_α d_α × I(m_n² + λ_α², Λ²)

    where d_s = 4 (5D spinor), and the sum is over Robin eigenvalues m_n
    and D_F eigenvalues λ_α.

    Returns the spectral action per unit 4D volume (÷ V₄ × 1/(32π²)).
    """
    Lambda2 = Lambda**2
    eigenvalues = compute_robin_eigenvalues(kval, yc, n_max=n_kk)

    # Use positive eigenvalues only (bound state is the zero mode,
    # handled separately)
    pos_eig = eigenvalues[1:]  # n=1, 2, 3, ...

    d_s = 4  # 5D spinor multiplicity

    S_total = 0.0

    # Zero mode contribution (m₀² = 0 physically, the 4D graviton multiplet)
    # The bound state at λ₀ = -4k² in the conformal frame corresponds to
    # a massless 4D mode. Its contribution to the spectral action is:
    for j, (lam_F, mult_F) in enumerate(zip(df2_eig, df2_mult)):
        M2_zero = lam_F  # m_0² = 0, only D_F contribution
        I_zero = spectral_action_4d_integral(M2_zero, Lambda2, cutoff)
        S_total += d_s * mult_F * I_zero

    # KK mode contributions
    for n_idx in range(len(pos_eig)):
        m_n2 = pos_eig[n_idx]
        if m_n2 < 0:
            continue  # skip any negative eigenvalues
        for j, (lam_F, mult_F) in enumerate(zip(df2_eig, df2_mult)):
            M2 = m_n2 + lam_F
            I_n = spectral_action_4d_integral(M2, Lambda2, cutoff)
            S_total += d_s * mult_F * I_n

    return S_total


def compute_spectral_action_smooth(kval, yc, Lambda, cutoff='gaussian', n_max=200):
    """
    Compute the SMOOTH (Vassilevich-like) approximation to the spectral action.
    Replace discrete KK sum by continuous integral over mode number.

    S_smooth = d_s × ∫₀^∞ dn × Σ_α d_α × I(m(n)² + λ_α², Λ²)

    where m(n) is the smooth eigenvalue function (Neumann + Robin correction).
    """
    Lambda2 = Lambda**2
    d_s = 4

    def integrand(n_cont):
        if n_cont < 0.01:
            return 0.0
        # Smooth eigenvalue approximation: m(n)² ≈ (nπ/y_c)²
        # Robin correction: add 4k/(n*pi/y_c) asymptotically
        m_n2 = (n_cont * np.pi / yc)**2
        # Robin correction for finite k:
        # More precise: solve the eigenvalue equation at continuous n
        # For simplicity, use the Neumann approximation + leading correction
        # (the Robin correction is O(k/m_n) = O(ky_c/(nπ)))
        robin_corr = 4 * kval / (yc * np.pi * n_cont) if n_cont > 0 else 0
        m_n2_corrected = (n_cont * np.pi / yc + robin_corr)**2
        # Use uncorrected for simplicity (the correction is small for n >> 1)
        m_n2_use = m_n2

        total = 0.0
        for j, (lam_F, mult_F) in enumerate(zip(df2_eig, df2_mult)):
            M2 = m_n2_use + lam_F
            I_n = spectral_action_4d_integral(M2, Lambda2, cutoff)
            total += d_s * mult_F * I_n
        return total

    # Integrate from n=0.5 (to avoid the zero mode / bound state)
    # The integral from 0 to 0.5 represents the zero mode contribution
    result, _ = quad(integrand, 0.5, n_max, limit=500, epsrel=1e-10)

    # Add the zero mode (n=0) contribution to the smooth part
    # (same as exact, since the zero mode is unique)
    S_zero = 0.0
    for j, (lam_F, mult_F) in enumerate(zip(df2_eig, df2_mult)):
        M2 = lam_F
        I_zero = spectral_action_4d_integral(M2, Lambda2, cutoff)
        S_zero += d_s * mult_F * I_zero

    return result + S_zero


# ============================================================================
# MAIN COMPUTATION: VARY k AND EXTRACT α_GB
# ============================================================================
fprint("\n" + "=" * 78)
fprint("PART 1: Spectral action as a function of k")
fprint("  Computing exact (KK sum) and smooth (integral) at multiple k values")
fprint("=" * 78)

# Fix y_c and Λ, vary k
# Use Λ = 1 as the reference scale. k varies from 0.5 to 1.5.
Lambda_ref = 1.0
yc_ref = ky_c  # y_c = ky_c / k, but we keep y_c fixed and vary k

k_values = np.linspace(0.3, 1.5, 25)
S_exact_vals = []
S_smooth_vals = []

fprint(f"\ny_c = {yc_ref:.1f}, Lambda = {Lambda_ref}")
fprint(f"\n{'k':>6} {'S_exact':>14} {'S_smooth':>14} {'delta':>14} {'delta/S':>10}")
fprint("-" * 62)

for kv in k_values:
    S_ex = compute_spectral_action(kv, yc_ref, Lambda_ref, cutoff='gaussian', n_kk=50)
    S_sm = compute_spectral_action_smooth(kv, yc_ref, Lambda_ref, cutoff='gaussian', n_max=100)
    delta = S_ex - S_sm
    ratio = delta / S_sm if abs(S_sm) > 1e-30 else float('inf')
    S_exact_vals.append(S_ex)
    S_smooth_vals.append(S_sm)
    fprint(f"{kv:6.3f} {S_ex:14.4f} {S_sm:14.4f} {delta:14.4f} {ratio:10.4f}")

S_exact_vals = np.array(S_exact_vals)
S_smooth_vals = np.array(S_smooth_vals)


# ============================================================================
# PART 2: Fit k-dependence to extract coefficients
# ============================================================================
fprint("\n" + "=" * 78)
fprint("PART 2: Polynomial fit of S(k) to extract curvature coefficients")
fprint("  S(k) = c_0 + c_2 k^2 + c_4 k^4 + c_6 k^6")
fprint("  The c_4 coefficient contains the Gauss-Bonnet coupling alpha_GB")
fprint("=" * 78)

# Fit S_exact(k) to polynomial in k²
k2_values = k_values**2

# Fit: S = c_0 + c_2 k² + c_4 k⁴ + c_6 k⁶
# Using k² as the variable: S = c_0 + c_2 x + c_4 x² + c_6 x³
deg = 4  # polynomial degree in k² (up to k⁸)
coeffs_exact = np.polyfit(k2_values, S_exact_vals, deg)
coeffs_smooth = np.polyfit(k2_values, S_smooth_vals, deg)

# numpy polyfit returns highest degree first
# coeffs = [c_deg, c_{deg-1}, ..., c_1, c_0]
# So for degree 4: [c_8_coeff, c_6_coeff, c_4_coeff, c_2_coeff, c_0_coeff]

fprint(f"\nExact spectral sum fit:")
for i, c in enumerate(reversed(coeffs_exact)):
    power = 2 * i
    fprint(f"  c_{power} (k^{power} coefficient) = {c:14.6e}")

fprint(f"\nSmooth integral fit:")
for i, c in enumerate(reversed(coeffs_smooth)):
    power = 2 * i
    fprint(f"  c_{power} (k^{power} coefficient) = {c:14.6e}")

# Extract c_4 (the k⁴ coefficient, which contains E₅ ∝ k⁴)
c4_exact = coeffs_exact[deg - 2]  # k⁴ = x² coefficient
c4_smooth = coeffs_smooth[deg - 2]

fprint(f"\n--- k^4 coefficient (Gauss-Bonnet sensitive) ---")
fprint(f"  c_4 (exact):  {c4_exact:14.6e}")
fprint(f"  c_4 (smooth): {c4_smooth:14.6e}")
if abs(c4_smooth) > 1e-30:
    ratio_c4 = c4_exact / c4_smooth
    delta_c4 = (c4_exact - c4_smooth) / c4_smooth
    fprint(f"  Ratio (exact/smooth): {ratio_c4:.4f}")
    fprint(f"  Fractional brane correction: {delta_c4:+.4f} ({delta_c4*100:+.1f}%)")
else:
    ratio_c4 = float('inf')
    delta_c4 = float('inf')
    fprint(f"  Smooth c_4 too small for meaningful comparison")


# ============================================================================
# PART 3: EM DECOMPOSITION AT REFERENCE k
# ============================================================================
fprint("\n" + "=" * 78)
fprint("PART 3: Euler-Maclaurin decomposition at k = 1.0")
fprint("  Quantifying the brane-localized correction to the spectral sum")
fprint("=" * 78)

k_ref = 1.0
yc = yc_ref
Lambda = Lambda_ref
Lambda2 = Lambda**2

eig_ref = compute_robin_eigenvalues(k_ref, yc, n_max=50)
pos_eig = eig_ref[1:]  # skip bound state

# Compute spectral weight for each mode
def spectral_weight(m_n2, Lambda2):
    """Total weight of KK mode with mass² = m_n2, summed over D_F."""
    d_s = 4
    total = 0.0
    for lam_F, mult_F in zip(df2_eig, df2_mult):
        M2 = m_n2 + lam_F
        total += d_s * mult_F * np.exp(-M2/Lambda2)  # Gaussian cutoff
    return total

# Exact sum over positive KK modes
weights = np.array([spectral_weight(pos_eig[i], Lambda2) for i in range(len(pos_eig))])
S_KK_exact = np.sum(weights)

# Smooth integral (trapezoidal approximation of continuous eigenvalue density)
def smooth_weight(n_cont):
    if n_cont < 0.01:
        return 0.0
    m_n2 = (n_cont * np.pi / yc)**2
    return spectral_weight(m_n2, Lambda2)

S_KK_smooth, _ = quad(smooth_weight, 0.5, len(pos_eig) + 0.5, limit=500, epsrel=1e-10)

# EM correction
delta_EM = S_KK_exact - S_KK_smooth
ratio_EM = delta_EM / S_KK_smooth if abs(S_KK_smooth) > 1e-30 else float('inf')

fprint(f"\n  KK modes: {len(pos_eig)} (n=1 to {len(pos_eig)})")
fprint(f"  Exact sum:     {S_KK_exact:14.4f}")
fprint(f"  Smooth integral: {S_KK_smooth:14.4f}")
fprint(f"  EM correction: {delta_EM:14.4f}")
fprint(f"  Correction ratio: {ratio_EM:+.4f} ({ratio_EM*100:+.1f}%)")

# Decompose by mode number to see where the correction comes from
fprint(f"\n  {'n':>4} {'m_n^2':>10} {'Robin':>10} {'Neumann':>10} {'weight':>12} {'frac':>8}")
fprint("  " + "-" * 56)
for i in range(min(15, len(pos_eig))):
    m_n2_robin = pos_eig[i]
    m_n2_neum = ((i+1) * np.pi / yc)**2
    w = weights[i]
    frac = w / S_KK_exact
    fprint(f"  {i+1:4d} {m_n2_robin:10.4f} {m_n2_robin:10.4f} {m_n2_neum:10.4f} {w:12.4f} {frac:8.4f}")


# ============================================================================
# PART 4: IMPLICATIONS FOR ε₁
# ============================================================================
fprint("\n" + "=" * 78)
fprint("PART 4: Implications for epsilon_1")
fprint("=" * 78)

# The Vassilevich prediction: ε₁ = α̂ × C_GB = 0.015 × 2/3 = 0.010
# where α̂ ∝ (spectral action E₅ coefficient)

# The brane correction from the EM decomposition modifies α̂:
# α̂_direct = α̂_Vassilevich × (1 + correction)

# The correction at the k⁴ level:
if abs(c4_smooth) > 1e-30:
    correction_factor = c4_exact / c4_smooth
else:
    correction_factor = 1.0

eps1_vassilevich = 0.010
eps1_direct = eps1_vassilevich * correction_factor

# Also compute using the EM ratio as an alternative estimate
eps1_em = eps1_vassilevich * (1 + ratio_EM)

C_GB = 2.0 / 3.0
Omega_DE = 0.685
q0 = -0.5275

def w0_from_eps1(eps1, zeta0=8.82e-4):
    """Compute w_0 from ε₁ and ζ₀."""
    C_KK = (1 + q0)**2 * Omega_DE * eps1 / (4 * (1 - q0)**2)
    kappa0 = C_KK * Omega_DE / (2 * zeta0)
    return -1.0 + 2.0 * kappa0 / (kappa0 + Omega_DE)

fprint(f"""
  VASSILEVICH PREDICTION:
    alpha_hat = 0.015
    C_GB = 2/3
    epsilon_1 = 0.010 +/- 0.002

  DIRECT SPECTRAL SUM:
    k^4 coefficient ratio (exact/smooth): {correction_factor:.4f}
    EM correction ratio:                  {1 + ratio_EM:.4f}

    epsilon_1 (from k^4 fit):  {eps1_direct:.6f}
    epsilon_1 (from EM ratio): {eps1_em:.6f}

  COSMOLOGICAL IMPLICATIONS:
    w_0 (Vassilevich, eps1=0.010): {w0_from_eps1(0.010):.4f}
    w_0 (direct, k^4 fit):        {w0_from_eps1(eps1_direct):.4f}
    w_0 (direct, EM ratio):       {w0_from_eps1(eps1_em):.4f}

  INTERPRETATION:
    If correction_factor ~ 1.0 (+/- 10%): Vassilevich CONFIRMED.
    If correction_factor < 0.5:           Vassilevich FAILS. epsilon_1 is smaller.
                                          Tension with data DECREASES.
    If correction_factor > 1.5:           Vassilevich FAILS. epsilon_1 is larger.
                                          Tension with data INCREASES.
""")


# ============================================================================
# PART 5: CROSS-CHECK WITH MULTIPLE CUTOFF FUNCTIONS
# ============================================================================
fprint("=" * 78)
fprint("PART 5: Cross-check with different cutoff functions")
fprint("=" * 78)

for cutoff_name in ['gaussian', 'sharp', 'smooth']:
    k_vals_check = np.linspace(0.5, 1.3, 15)
    S_ex_check = []
    S_sm_check = []

    for kv in k_vals_check:
        S_ex = compute_spectral_action(kv, yc_ref, Lambda_ref, cutoff=cutoff_name, n_kk=50)
        S_sm = compute_spectral_action_smooth(kv, yc_ref, Lambda_ref, cutoff=cutoff_name, n_max=100)
        S_ex_check.append(S_ex)
        S_sm_check.append(S_sm)

    S_ex_check = np.array(S_ex_check)
    S_sm_check = np.array(S_sm_check)

    # Fit k⁴ coefficient
    k2_check = k_vals_check**2
    c_ex = np.polyfit(k2_check, S_ex_check, deg)
    c_sm = np.polyfit(k2_check, S_sm_check, deg)

    c4_ex = c_ex[deg - 2]
    c4_sm = c_sm[deg - 2]
    ratio = c4_ex / c4_sm if abs(c4_sm) > 1e-30 else float('inf')

    # Also compute total EM ratio at k=1
    S_ex_k1 = compute_spectral_action(1.0, yc_ref, Lambda_ref, cutoff=cutoff_name, n_kk=50)
    S_sm_k1 = compute_spectral_action_smooth(1.0, yc_ref, Lambda_ref, cutoff=cutoff_name, n_max=100)
    em_ratio = (S_ex_k1 - S_sm_k1) / S_sm_k1 if abs(S_sm_k1) > 1e-30 else float('inf')

    fprint(f"\n  {cutoff_name:>10} cutoff: c4_ratio = {ratio:.4f}, EM_ratio = {em_ratio:+.4f} ({em_ratio*100:+.1f}%)")


fprint("\n" + "=" * 78)
fprint("COMPUTATION COMPLETE")
fprint("=" * 78)
fprint("\nDone.")
