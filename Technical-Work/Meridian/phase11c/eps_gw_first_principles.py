#!/usr/bin/env python3
"""
epsilon_GW FROM FIRST PRINCIPLES: Spectral Action Stabilization
================================================================

Does the spectral action S[D] on M_5 x F naturally stabilize y_c?

Computation:
  1. For each y_c in a range around ky_c = 37:
     - Compute Robin eigenvalues lambda_n(y_c) [from warped geometry BCs]
     - Compute D_F eigenvalues lambda_alpha(y_c) [from fermion profiles]
     - Compute S(y_c) = sum_{n,alpha} mult_alpha * f((lambda_n + lambda_alpha^2)/Lambda^2)
  2. If S(y_c) has a minimum -> spectral action stabilizes -> extract epsilon_GW
  3. If S(y_c) is monotonic -> epsilon_GW is genuinely external

The key physics: the BULK spectral action grows with y_c (more modes fit below cutoff).
Stabilization requires the BOUNDARY contribution (EM correction) to provide a restoring force.
The D_F eigenvalues also depend on y_c (through fermion profiles) — this is the NCG contribution.

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
fprint("  epsilon_GW FROM FIRST PRINCIPLES: Spectral Action Stabilization")
fprint("=" * 78)

# =============================================================================
# PARAMETERS
# =============================================================================
k = 1.0
Lambda = k  # cutoff
M5_cubed = 1.0

# NCG D_F spectrum
M_oct = np.array([[1.0, 0.5, 0.5], [0.5, 1.0, 0.5], [0.5, 0.5, 1.0]])
c_Q = np.array([0.557, 0.646, 0.247])
c_u = np.array([0.661, 0.415, 0.200])
c_d = np.array([0.495, 0.465, 0.567])
c_L = np.array([0.650, 0.580, 0.520])
c_e = np.array([0.660, 0.590, 0.500])
Y5_u, Y5_d, Y5_e = 1.75, 0.18, 0.10
N_c = 3
N_F = 84


def g_profile(c, ky):
    """5D fermion zero-mode profile at UV brane."""
    delta = 0.5 - c
    if abs(2 * delta * ky) < 1e-8:
        return 1.0 / np.sqrt(ky)
    val = (1 - 2 * c) / (np.exp((1 - 2 * c) * ky) - 1)
    return np.sqrt(np.abs(val)) * np.exp(delta * ky) * np.sign(val)


def compute_df_spectrum(ky_val):
    """Compute D_F^2 eigenvalues and multiplicities at given ky_c."""
    gQ = np.array([g_profile(c, ky_val) for c in c_Q])
    gu = np.array([g_profile(c, ky_val) for c in c_u])
    gd = np.array([g_profile(c, ky_val) for c in c_d])
    gL = np.array([g_profile(c, ky_val) for c in c_L])
    ge = np.array([g_profile(c, ky_val) for c in c_e])

    Yu = Y5_u * M_oct * np.outer(gQ, gu)
    Yd = Y5_d * M_oct * np.outer(gQ, gd)
    Ye = Y5_e * M_oct * np.outer(gL, ge)

    sv_u = np.linalg.svd(Yu, compute_uv=False)
    sv_d = np.linalg.svd(Yd, compute_uv=False)
    sv_e = np.linalg.svd(Ye, compute_uv=False)

    df2_eig = np.concatenate([sv_u**2, sv_d**2, sv_e**2])
    df2_mult = np.array([4 * N_c] * 3 + [4 * N_c] * 3 + [4] * 3)

    N_zero = N_F - int(sum(df2_mult))
    if N_zero > 0:
        df2_eig = np.append(df2_eig, 0.0)
        df2_mult = np.append(df2_mult, N_zero)

    return df2_eig, df2_mult


# =============================================================================
# ROBIN EIGENVALUE SOLVER
# =============================================================================
def robin_condition(lam, yc, kval):
    if lam <= 0:
        kappa = np.sqrt(-lam)
        return np.tanh(kappa * yc) - 4 * kval * kappa / (kappa**2 + 4 * kval**2)
    sqrtl = np.sqrt(lam)
    theta = sqrtl * yc
    if abs(4 * kval**2 - lam) < 1e-10:
        return np.cos(theta)
    return np.tan(theta) - 4 * kval * sqrtl / (4 * kval**2 - lam)


def compute_robin_eigenvalues(kval, yc, n_max=60):
    eigenvalues = []
    try:
        lam0 = brentq(lambda l: robin_condition(l, yc, kval), -5 * kval**2, -0.01)
        eigenvalues.append(lam0)
    except:
        eigenvalues.append(-4.0 * kval**2)
    for n in range(1, n_max):
        lo = ((n - 0.49) * np.pi / yc)**2
        hi = ((n + 0.49) * np.pi / yc)**2
        try:
            lam_n = brentq(lambda l: robin_condition(l, yc, kval), lo, hi)
            eigenvalues.append(lam_n)
        except:
            eigenvalues.append((n * np.pi / yc)**2)
    return np.array(eigenvalues)


# =============================================================================
# PART 1: S(y_c) — FULL SPECTRAL ACTION vs y_c
# =============================================================================
fprint("\n" + "=" * 78)
fprint("PART 1: Spectral action S(y_c) = sum_n,alpha f((lambda_n + lambda_alpha^2)/Lambda^2)")
fprint("  Full product geometry: KK modes x D_F eigenvalues")
fprint("  Robin BCs, y_c-dependent fermion profiles")
fprint("=" * 78)

def compute_spectral_action(ky_val, Lam=Lambda, n_max=60):
    """
    Compute the spectral action at a given ky_c.

    S(ky_c) = sum_{n=0}^{n_max} sum_alpha mult_alpha * f((lambda_n + lambda_alpha^2)/Lambda^2)

    f(x) = exp(-x) (Gaussian cutoff)

    Returns: S_total, S_bulk_only (lambda_alpha=0 contribution), S_df (D_F contribution)
    """
    yc = ky_val / k
    Lam2 = Lam**2

    # Robin eigenvalues at this y_c
    eigs = compute_robin_eigenvalues(k, yc, n_max=n_max)

    # D_F eigenvalues at this ky_c
    df2, df_mult = compute_df_spectrum(ky_val)

    S_total = 0.0

    # Include bound state (n=0, negative eigenvalue) and positive modes
    for lam_n in eigs:
        for lam2, mult in zip(df2, df_mult):
            x = (lam_n + lam2) / Lam2
            if x > -50:  # avoid overflow
                S_total += mult * np.exp(-x) * Lam2  # Lam^4 / Lam^2 per mode

    return S_total


def compute_spectral_action_em(ky_val, Lam=Lambda, n_max=60):
    """
    Compute the spectral action decomposed into bulk (smooth) and boundary (EM correction).

    S = S_smooth + S_EM

    S_smooth = integral approximation (Neumann eigenvalues)
    S_EM = discrete (Robin) - smooth (Neumann) = boundary-localized contribution

    Returns: S_discrete, S_smooth, S_EM
    """
    yc = ky_val / k
    Lam2 = Lam**2

    # Robin eigenvalues (discrete)
    eigs_robin = compute_robin_eigenvalues(k, yc, n_max=n_max)
    pos_robin = eigs_robin[1:]  # skip bound state

    # D_F eigenvalues
    df2, df_mult = compute_df_spectrum(ky_val)

    # Discrete sum (Robin, positive modes only — bound state is brane-localized anyway)
    S_discrete = 0.0
    for lam_n in pos_robin:
        for lam2, mult in zip(df2, df_mult):
            x = (lam_n + lam2) / Lam2
            S_discrete += mult * np.exp(-x) * Lam2

    # Bound state contribution (purely brane-localized)
    S_bound = 0.0
    lam_bound = eigs_robin[0]
    for lam2, mult in zip(df2, df_mult):
        x = (lam_bound + lam2) / Lam2
        S_bound += mult * np.exp(-x) * Lam2

    # Smooth integral (Neumann eigenvalues as continuum approximation)
    def smooth_integrand(n_cont):
        mn2 = (n_cont * np.pi / yc)**2
        total = 0.0
        for lam2, mult in zip(df2, df_mult):
            x = (mn2 + lam2) / Lam2
            total += mult * np.exp(-x) * Lam2
        return total

    S_smooth, _ = quad(smooth_integrand, 0.5, n_max + 0.5, limit=500, epsrel=1e-12)
    tail, _ = quad(smooth_integrand, n_max + 0.5, 3 * n_max, limit=200, epsrel=1e-10)
    S_smooth += tail

    S_EM = S_discrete - S_smooth  # boundary correction

    return S_discrete + S_bound, S_smooth, S_EM + S_bound


# Scan y_c
fprint("\nScanning ky_c from 20 to 55...")
ky_values = np.linspace(20, 55, 71)
S_disc_arr = []
S_smooth_arr = []
S_em_arr = []
S_total_arr = []

fprint(f"\n{'ky_c':>8} {'S_total':>14} {'S_smooth':>14} {'S_EM':>14} {'S_EM/S_total':>12}")
fprint("-" * 66)

for ky in ky_values:
    S_d, S_s, S_e = compute_spectral_action_em(ky)
    S_disc_arr.append(S_d)
    S_smooth_arr.append(S_s)
    S_em_arr.append(S_e)
    S_total_arr.append(S_d)
    if abs(ky - round(ky)) < 0.3 or abs(ky - 37) < 0.3:
        fprint(f"{ky:8.1f} {S_d:14.4f} {S_s:14.4f} {S_e:14.4f} {S_e/S_d:12.6f}")

S_disc_arr = np.array(S_disc_arr)
S_smooth_arr = np.array(S_smooth_arr)
S_em_arr = np.array(S_em_arr)
S_total_arr = np.array(S_total_arr)


# =============================================================================
# PART 2: dS/dy_c — Is there a minimum?
# =============================================================================
fprint("\n" + "=" * 78)
fprint("PART 2: Numerical derivative dS/dy_c — looking for a minimum")
fprint("=" * 78)

dky = ky_values[1] - ky_values[0]
dS_total = np.gradient(S_total_arr, dky)
dS_smooth = np.gradient(S_smooth_arr, dky)
dS_em = np.gradient(S_em_arr, dky)

fprint(f"\n{'ky_c':>8} {'dS_total/dky':>14} {'dS_smooth/dky':>14} {'dS_EM/dky':>14}")
fprint("-" * 56)

for i, ky in enumerate(ky_values):
    if abs(ky - round(ky)) < 0.3 or abs(ky - 37) < 0.3:
        fprint(f"{ky:8.1f} {dS_total[i]:14.4f} {dS_smooth[i]:14.4f} {dS_em[i]:14.4f}")

# Check for sign changes in dS_total
sign_changes = []
for i in range(len(dS_total) - 1):
    if dS_total[i] * dS_total[i+1] < 0:
        # Linear interpolation
        ky_zero = ky_values[i] - dS_total[i] * dky / (dS_total[i+1] - dS_total[i])
        sign_changes.append(ky_zero)

if sign_changes:
    fprint(f"\n  SIGN CHANGE in dS/dy_c found at ky_c = {sign_changes}")
    fprint(f"  This indicates a MINIMUM or MAXIMUM in S(y_c).")
    for ky_sc in sign_changes:
        # Check second derivative
        idx = np.argmin(np.abs(ky_values - ky_sc))
        d2S = np.gradient(dS_total, dky)[idx]
        fprint(f"    ky_c = {ky_sc:.2f}: d2S/dky_c2 = {d2S:.4f} ({'MIN' if d2S > 0 else 'MAX'})")
else:
    fprint(f"\n  NO sign change in dS/dy_c: S(y_c) is MONOTONIC in [{ky_values[0]}, {ky_values[-1]}].")
    fprint(f"  dS/dy_c range: [{min(dS_total):.4f}, {max(dS_total):.4f}]")
    fprint(f"  The spectral action ALONE does not stabilize y_c in this range.")


# =============================================================================
# PART 3: EM CORRECTION ANALYSIS — The brane contribution
# =============================================================================
fprint("\n" + "=" * 78)
fprint("PART 3: EM correction (boundary contribution) behavior")
fprint("=" * 78)

# The key question: does the EM correction (brane part) have a different
# y_c-dependence than the smooth (bulk) part?
fprint(f"\n  S_EM as fraction of S_total:")
for i, ky in enumerate(ky_values):
    if abs(ky - round(ky * 2) / 2) < 0.3 or abs(ky - 37) < 0.3:
        if i >= 2:
            fprint(f"    ky_c = {ky:.1f}: S_EM/S = {S_em_arr[i]/S_total_arr[i]*100:.4f}%, "
                   f"dS_EM/dky = {dS_em[i]:.6f}")

# Check if EM correction has a sign change in its derivative
sign_changes_em = []
for i in range(len(dS_em) - 1):
    if dS_em[i] * dS_em[i+1] < 0:
        ky_zero = ky_values[i] - dS_em[i] * dky / (dS_em[i+1] - dS_em[i])
        sign_changes_em.append(ky_zero)

if sign_changes_em:
    fprint(f"\n  EM derivative sign change at ky_c = {sign_changes_em}")
else:
    fprint(f"\n  EM derivative: no sign change, range [{min(dS_em):.6f}, {max(dS_em):.6f}]")


# =============================================================================
# PART 4: EFFECTIVE V_eff EXTRACTION
# =============================================================================
fprint("\n" + "=" * 78)
fprint("PART 4: Can we extract V_eff from S(y_c) behavior?")
fprint("=" * 78)

# If S(y_c) is monotonic, there's no minimum. But we can still ask:
# what ADDITIONAL potential would be needed to stabilize at ky_c = 37?
#
# V_stab(y_c) = -S(y_c) + V_0  (needs to have a minimum)
# At ky_c = 37: dV_stab/dy_c = -dS/dy_c = 0 requires dS/dy_c = 0
# Since dS/dy_c > 0 (monotonically increasing), we need an EXTERNAL
# contribution with dV_ext/dy_c = -dS/dy_c < 0.
#
# The GW mechanism provides this: V_GW(y_c) = A e^{-2(4+epsilon)ky_c}
# Its derivative: dV_GW/dy_c = -2(4+epsilon)k * V_GW < 0

# At ky_c = 37, what is dS/dy_c?
idx_37 = np.argmin(np.abs(ky_values - 37.0))
dS_at_37 = dS_total[idx_37]
S_at_37 = S_total_arr[idx_37]

fprint(f"\n  At ky_c = 37.0:")
fprint(f"    S(37)      = {S_at_37:.4f}")
fprint(f"    dS/d(ky_c) = {dS_at_37:.6f}")
fprint(f"    d2S/d(ky_c)2 = {np.gradient(dS_total, dky)[idx_37]:.6f}")

fprint(f"\n  For the GW mechanism V_GW = A * exp(-2(4+eps)*ky_c):")
fprint(f"  Stabilization requires: dV_GW/d(ky_c) = -dS/d(ky_c) at ky_c = 37")
fprint(f"  i.e., -2(4+eps)*k * V_GW(37) = -dS/d(ky_c)|_37 = {-dS_at_37:.6f}")

# The GW potential with boundary conditions:
# V_GW(y_c) = v_uv^2 * [exp(-2*eps*k*y_c) - (v_ir/v_uv)^2 * exp(-2*(4+eps)*k*y_c)]
# Standard result: eps = Delta - 2 is determined by the bulk scalar mass.
#
# From the spectral action perspective, the question is:
# does the D_F sector (NCG) determine a PREFERRED y_c?

# The D_F contribution to S(y_c) comes from the y_c-dependence of Yukawa profiles.
# Let's isolate it.

fprint("\n  Isolating the D_F (NCG) contribution to dS/dy_c:")

# Compute S with and without D_F y_c-dependence
# With: df2, df_mult vary with ky_c
# Without: df2, df_mult fixed at ky_c = 37

df2_fixed, dfm_fixed = compute_df_spectrum(37.0)

def compute_S_fixed_df(ky_val, n_max=60):
    """S with D_F fixed at ky_c=37 (only KK modes change)."""
    yc = ky_val / k
    Lam2 = Lambda**2
    eigs = compute_robin_eigenvalues(k, yc, n_max=n_max)
    S = 0.0
    for lam_n in eigs:
        for lam2, mult in zip(df2_fixed, dfm_fixed):
            x = (lam_n + lam2) / Lam2
            if x > -50:
                S += mult * np.exp(-x) * Lam2
    return S

S_fixdf_arr = np.array([compute_S_fixed_df(ky) for ky in ky_values])
dS_fixdf = np.gradient(S_fixdf_arr, dky)

# The NCG contribution = S_full - S_fixedDF
S_ncg = S_total_arr - S_fixdf_arr
dS_ncg = dS_total - dS_fixdf

fprint(f"\n{'ky_c':>8} {'dS_total':>12} {'dS_KK_only':>12} {'dS_NCG':>12} {'NCG/total':>10}")
fprint("-" * 56)
for i, ky in enumerate(ky_values):
    if abs(ky - round(ky * 2) / 2) < 0.3 or abs(ky - 37) < 0.3:
        if i >= 2:
            frac = dS_ncg[i] / dS_total[i] * 100 if abs(dS_total[i]) > 1e-15 else 0
            fprint(f"{ky:8.1f} {dS_total[i]:12.6f} {dS_fixdf[i]:12.6f} {dS_ncg[i]:12.6f} {frac:9.4f}%")


# =============================================================================
# PART 5: RADION MASS FROM SPECTRAL ACTION CURVATURE
# =============================================================================
fprint("\n" + "=" * 78)
fprint("PART 5: Effective epsilon_GW from spectral action curvature")
fprint("=" * 78)

# Even if S(y_c) doesn't have a minimum by itself, the CURVATURE d2S/dy_c2
# tells us the spectral action's contribution to the radion mass.
# The total radion potential is V_rad = V_GW + V_SA
# The spectral action provides V_SA(y_c) proportional to S(y_c).
# At the GW minimum, m_rad^2 = d2V_GW/dy_c^2 + d2V_SA/dy_c^2

d2S_total = np.gradient(dS_total, dky)

fprint(f"\n  d2S/d(ky_c)^2 at ky_c = 37: {d2S_total[idx_37]:.6f}")
fprint(f"  This is the spectral action's CONTRIBUTION to the radion mass squared.")
fprint(f"  Sign: {'POSITIVE (stabilizing)' if d2S_total[idx_37] > 0 else 'NEGATIVE (destabilizing)'}")

# In the GW mechanism, the radion mass is:
# m_rad^2 / k^2 = 2 * eps * (4 + eps) * (ky_c)^2 * exp(-2(4+eps)*ky_c) * [boundary terms]
#
# We can compare the spectral action's d2S/dy_c^2 to the GW contribution.
# If d2S is significant compared to d2V_GW, the spectral action modifies epsilon_GW.

# Effective eps_GW from matching:
# d2S/d(ky_c)^2 generates a contribution to the effective V_eff seen by KK modes.
# V_eff = eps(4+eps)k^2 shifts all eigenvalues.
# We can solve: what eps would produce the same d2S?

# Actually, let's be more direct.
# The spectral action curvature tells us whether it helps or hurts stabilization.
# If positive: spectral action reinforces GW stabilization -> smaller eps_GW needed
# If negative: spectral action fights GW -> larger eps_GW needed

fprint(f"\n  Spectral action curvature decomposition:")
d2S_KK = np.gradient(dS_fixdf, dky)
d2S_NCG = np.gradient(dS_ncg, dky)
fprint(f"    KK only:  d2S/d(ky_c)^2 = {d2S_KK[idx_37]:.6f}")
fprint(f"    NCG only: d2S/d(ky_c)^2 = {d2S_NCG[idx_37]:.6f}")
fprint(f"    Total:    d2S/d(ky_c)^2 = {d2S_total[idx_37]:.6f}")


# =============================================================================
# PART 6: WHAT THE SPECTRAL ACTION ACTUALLY DETERMINES
# =============================================================================
fprint("\n" + "=" * 78)
fprint("PART 6: What the spectral action determines about epsilon_GW")
fprint("=" * 78)

# The GW mechanism: V_GW(y_c) = v_UV^2 [e^{-2eps*ky_c} - (v_IR/v_UV)^2 e^{-2(4+eps)*ky_c}]
# Minimum at: e^{-2*4*ky_c} = eps/(4+eps) * (v_UV/v_IR)^2
# -> ky_c = [ln(v_UV/v_IR)^2 + ln((4+eps)/eps)] / 8
#
# For ky_c = 37: 8*37 = 296 = 2*ln(v_UV/v_IR) + ln((4+eps)/eps)
# With v_UV/v_IR ~ e^{ky_c} ~ e^{37}: 2*37 = 74 accounts for 74 of 296.
# Remaining: 296 - 74 = 222 = ln((4+eps)/eps)
# -> (4+eps)/eps = e^{222} -> eps ~ 4*e^{-222} ~ 0 (impossibly small)
#
# This is the STANDARD hierarchy problem — GW alone at ky_c=37 needs eps~0.
# The spectral action can rescue this if its y_c dependence is strong enough.

# More physically: in our framework, the spectral action determines eps_GW through
# the Seeley-DeWitt coefficients. Specifically, the a_1 coefficient on the warped
# orbifold gives the bulk mass term for the GW scalar.

# Let's compute: what V_eff is implied by the spectral action's y_c dependence?
# If we parameterize S(y_c) ~ S_0 + S_1 * y_c + (1/2) * S_2 * y_c^2 + ...
# Then the effective "force" is -dS/dy_c = -S_1 - S_2 * y_c + ...
# And the effective "spring constant" is -d2S/dy_c^2 = -S_2

# The V_eff that would produce the same spring constant in our mu^2 framework:
# d(mu^2)/d(V_eff) * V_eff = (spectral action contribution to radion mass^2)

fprint("\n  Fitting S(y_c) to polynomial near ky_c = 37:")

# Fit to quadratic in a window around 37
mask = np.abs(ky_values - 37) < 10
coeffs = np.polyfit(ky_values[mask] - 37, S_total_arr[mask], 3)
fprint(f"  S(ky_c) = S_0 + a*(ky-37) + b*(ky-37)^2 + c*(ky-37)^3")
fprint(f"    a (slope)     = {coeffs[2]:.8f}")
fprint(f"    b (curvature) = {coeffs[1]:.8f}")
fprint(f"    c (cubic)     = {coeffs[0]:.8f}")

# The spectral action slope at ky_c = 37 relative to the total
rel_slope = coeffs[2] / S_at_37 * 100
fprint(f"\n  Relative slope: (dS/d(ky_c))/S = {rel_slope:.4f}% per unit ky_c")
fprint(f"  Over the range ky_c = [30, 44]: S changes by {(S_total_arr[mask][-1] - S_total_arr[mask][0])/S_at_37*100:.2f}%")

# The effective V_eff from spectral action
# In the mu^2 computation, V_eff = eps*(4+eps)*k^2 shifts eigenvalues uniformly.
# The spectral action's y_c-dependence is NOT equivalent to a uniform eigenvalue shift.
# But we can compute: at ky_c = 37, how much does d(mu^2)/d(ky_c) change?
# This gives the spectral action's effective contribution to stabilization.

# Key insight: the spectral action generates a y_c-dependent BACKGROUND.
# The GW scalar Phi has a 5D mass determined by the spectral action's Seeley-DeWitt
# coefficients. Specifically, from a_1 on the RS1 orbifold:
#   m^2_GW = R_5/6 = -20k^2/3 (from the 5D warped Ricci scalar)
#   -> Delta(Delta-4) = m^2_GW/k^2 = -20/3
#   -> Delta = 2 + eps, eps(eps+4-4) = eps^2 ≈ -20/3 (NO real solution!)
#
# This is wrong — the 5D conformal coupling is R/6, but the GW scalar is NOT
# conformally coupled. Its mass comes from the scalar potential in the spectral action.

# Let's compute what the spectral action gives for the GW scalar mass directly.
# The Seeley-DeWitt coefficient a_1 for a scalar on the RS1 orbifold:
#   a_1 = (1/6)(R_5 - 6*V_scalar) * volume_factor
# where R_5 = -20k^2 for AdS_5 and V_scalar is the scalar potential from the NCG.

fprint("\n  Direct computation: GW scalar mass from spectral action")
fprint("  -------------------------------------------------------")

# From the monograph: the spectral action a_2 coefficient gives the scalar potential
# V(Phi) = c * Phi (linear tadpole, Axiom A6)
# The GW scalar is the radion mode of the 5D metric.
# Its bulk equation of motion is: (-Box_5 + m^2_GW) Phi_GW = 0
# where m^2_GW comes from the curvature of the radion potential at the minimum.

# In the RS1 framework with NCG spectral action:
# The effective potential for the radion is generated by one-loop Casimir energy
# of the KK spectrum + the classical brane tensions.
# V_Casimir(y_c) propto sum_n (-1)^F * m_n(y_c)^4 * ln(m_n(y_c)/mu)
# This has been computed by many authors (Garriga et al. 2003, Hofmann et al. 2001)

# Our spectral action computation gives S(y_c) directly — no need for one-loop Casimir.
# The spectral action IS the regulated one-loop determinant.

# From our numerical results:
fprint(f"\n  Numerical: S(y_c) polynomial coefficients:")
fprint(f"    S_0 = {coeffs[3]:.4f} (value at ky_c=37)")
fprint(f"    S_1 = {coeffs[2]:.8f} (slope)")
fprint(f"    S_2 = {coeffs[1]:.8f} (curvature / 2)")

# The radion mass squared (in units of k^2) from the spectral action curvature:
# m_rad^2 / k^2 = (2 * S_2) / (normalization factor)
# The normalization depends on the kinetic term for the radion in the 4D EFT.
# In RS1: T_radion = (6 M_5^3 / k) * (e^{2ky_c} - 1) * (d phi)^2
# At ky_c = 37: T ~ 6 M_5^3 / k * e^{74}
# So m_rad^2 = 2 * k^2 * S_2 / (6 * M_5^3 * e^{74} / k)

# But this is exponentially suppressed — the warp factor makes the radion light.
# This is EXPECTED in GW: m_rad ~ epsilon * k * e^{-ky_c} for small epsilon.

kinetic_norm = 6 * M5_cubed / k * np.exp(2 * 37)
m_rad_sq_over_k2 = 2 * coeffs[1] / kinetic_norm
fprint(f"\n  Radion kinetic normalization: 6*M5^3/k * e^(2*ky_c) = {kinetic_norm:.4e}")
fprint(f"  m_rad^2 / k^2 (spectral action) = {m_rad_sq_over_k2:.4e}")
fprint(f"  m_rad / k = {np.sqrt(abs(m_rad_sq_over_k2)):.4e}")

# For comparison: GW with eps=0.275 gives
eps_gw_desi = 0.275
m_rad_gw = eps_gw_desi * k * np.exp(-37) * np.sqrt(2 * (4 + eps_gw_desi) * 37)
fprint(f"  m_rad / k (GW, eps=0.275) = {m_rad_gw:.4e}")
fprint(f"  m_rad / k (GW formula) = eps * sqrt(2*(4+eps)*ky_c) * e^(-ky_c)")


# =============================================================================
# PART 7: THE DEFINITIVE ANSWER
# =============================================================================
fprint("\n" + "=" * 78)
fprint("PART 7: DEFINITIVE ANSWER")
fprint("=" * 78)

# Is S(y_c) monotonic?
is_monotonic = len(sign_changes) == 0

if is_monotonic:
    fprint("""
  The spectral action S(y_c) is MONOTONIC in the range ky_c = [20, 55].

  This means: the spectral action ALONE does not stabilize y_c.
  epsilon_GW is NOT determined by the spectral action.
  epsilon_GW is a FREE PARAMETER of the GW stabilization sector.

  What the spectral action DOES determine:
  - mu^2(Phi_0, V_eff) for each value of V_eff = eps*(4+eps)*k^2
  - alpha_UV = -5.02e-4 (from the Gauss-Bonnet coefficient)
  - eps_1 = 0.010 (from the curvature coefficient ratio)

  What remains external:
  - epsilon_GW (GW scalar bulk mass parameter)
  - Equivalently: the GW scalar potential V(Phi_GW) on the branes

  The DESI constraint w_0 = -0.83 +/- 0.06 determines:
  - epsilon_GW = 0.275 (+0.072 / -0.106) [from OP#8 scan]
  - Equivalently: Delta_GW = 2.275
""")
else:
    fprint(f"\n  S(y_c) has extrema at ky_c = {sign_changes}")
    fprint(f"  The spectral action DOES contribute to y_c stabilization.")

fprint("  Summary:")
fprint(f"    S(37)           = {S_at_37:.4f}")
fprint(f"    dS/d(ky_c)|_37  = {dS_at_37:.6f}")
fprint(f"    d2S/d(ky_c)^2   = {d2S_total[idx_37]:.6f}")
fprint(f"    NCG fraction of slope: {dS_ncg[idx_37]/dS_total[idx_37]*100:.2f}%")

fprint("\nDone.")
