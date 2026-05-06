#!/usr/bin/env python3
"""
Brane-Localized mu^2 via Euler-Maclaurin Decomposition
========================================================

The spectral action sum S = Sum_n g(n) decomposes via Euler-Maclaurin:

  Sum_{n=0}^{inf} g(n) = integral_0^inf g(x)dx + g(0)/2 + Sum_{k=1}^p B_{2k}/(2k)! g^{(2k-1)}(0) + ...

The INTEGRAL part is the BULK contribution (smooth, extended over the interval).
The BOUNDARY corrections (g(0)/2, derivatives at 0, ...) are BRANE-LOCALIZED.

This script:
1. Computes the full spectral sum (= total mu^2)
2. Subtracts the integral part (= bulk mu^2)
3. The remainder is the brane-localized mu^2 for the junction conditions.

This is the correct way to extract boundary contributions from a discrete spectrum
when the asymptotic (Vassilevich) expansion is unreliable (Lambda ~ k, few modes below cutoff).
"""

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import numpy as np
from scipy.optimize import brentq
from scipy.integrate import quad

print("=" * 78)
print("  BRANE-LOCALIZED mu^2 VIA EULER-MACLAURIN DECOMPOSITION")
print("=" * 78)

# === RS1 Parameters (identical to product_heat_kernel.py) ===
k = 1.0
M5_cubed = 1.0
sigma_UV = 6.0 * M5_cubed * k
xi = 1.0 / 6.0
ky_c = 37.0
Lambda = k

R5 = -20.0 * k**2
K_UV = -4.0 * k
E5 = xi * R5  # = -(10/3)k^2

Delta_GW = 2.0
epsilon_GW = 4.0 - Delta_GW  # = 2

alpha_UV_SA = -5.02e-4
eps_1 = 0.010
Omega_DE = 0.685
q0 = -0.5275
C_KK = (1 + q0)**2 * Omega_DE * eps_1 / (4 * (1 - q0)**2)

V_bulk = 2.0 / 3.0 * k**2  # Bulk curvature contribution

# === Yukawa spectrum (from octonionic mass matrix + 16C) ===
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

# D_F^2 spectrum with multiplicities
df2_eig = np.concatenate([sv_u**2, sv_d**2, sv_e**2])
df2_mult = np.array([4*N_c]*3 + [4*N_c]*3 + [4]*3)  # 12,12,12,12,12,12,4,4,4
N_F = 84
N_zero = N_F - int(sum(df2_mult))
if N_zero > 0:
    df2_eig = np.append(df2_eig, 0.0)
    df2_mult = np.append(df2_mult, N_zero)

print(f"\nRS1: k={k}, ky_c={ky_c}, V_bulk={V_bulk:.4f}")
print(f"D_F^2: 9 eigenvalues, {int(sum(df2_mult))} total modes")
print(f"Top Yukawa: y_t^2 = {sv_u[0]**2:.6f}")
print(f"C_KK = {C_KK:.4e}")

# === Cutoff function ===
def f_cut(x):
    return np.exp(-x)

def f_cut_prime(x):
    return -np.exp(-x)

def f_cut_pp(x):
    return np.exp(-x)


# =============================================================================
# THE EULER-MACLAURIN DECOMPOSITION
# =============================================================================
print("\n" + "=" * 78)
print("EULER-MACLAURIN DECOMPOSITION OF THE SPECTRAL SUM")
print("=" * 78)

# Define g(n) = Sum_i mult_i * f'(x_{n,i}) * dm_n^2/dy_c / Lambda^2
# where x_{n,i} = (m_n^2 + lam_i^2) / Lambda^2
# and dm_n^2/dy_c = -2n^2 pi^2 / y_c^3
#
# Then dS/dy_c = Sum_{n>=1} g(n)
#
# Note: n=0 has dm_0^2/dy_c = 0, so g(0) = 0 for Channel 1.
# The Euler-Maclaurin formula applies to the sum starting from n=1.
#
# For the DERIVATIVE with respect to y_c:
# g(n) = Sum_i mult_i * f'((m_n^2+lam_i^2)/Lambda^2) * (-2n^2 pi^2 / y_c^3) / Lambda^2
#
# The Euler-Maclaurin decomposition of Sum_{n=1}^{inf} g(n):
#
# Sum = integral_1^inf g(x)dx + g(1)/2 + (1/12)*g'(1) - (1/720)*g'''(1) + ...
#
# BULK part: integral_1^inf g(x)dx (smooth contribution from all KK modes)
# UV BRANE part: g(1)/2 + (1/12)*g'(1) - ... (localized corrections from discrete spectrum)
#
# Alternatively, we can shift: let h(n) = g(n+1), then Sum_{n=0}^inf h(n)
# and apply standard EM to h.

# Numerically, we'll compute:
# 1. Full sum (up to N_KK)
# 2. Integral (numerical quadrature)
# 3. Brane part = full sum - integral

N_KK = 200  # Use more modes for accuracy of the integral

def g_func(n, y_c, Phi_0):
    """The summand for dS/dPhi_0 at mode number n (continuous extension)."""
    if n < 1e-10:
        return 0.0  # n=0 does not contribute
    mn2 = (n * np.pi / y_c)**2 + V_bulk
    dmn2_dPhi = -2.0 * (n * np.pi)**2 / (y_c**3 * epsilon_GW * Phi_0)
    total = 0.0
    for lam2, mult in zip(df2_eig, df2_mult):
        x = (mn2 + lam2) / Lambda**2
        total += mult * f_cut_prime(x) * dmn2_dPhi / Lambda**2
    return total


def compute_decomposition(Phi_0):
    """
    Decompose mu^2 = dS/dPhi_0 into bulk and brane parts.

    Returns: (mu2_total, mu2_bulk, mu2_brane, details)
    """
    y_c = ky_c

    # 1. Full discrete sum
    mu2_total = 0.0
    for n in range(1, N_KK):
        mu2_total += g_func(n, y_c, Phi_0)

    # 2. Integral (bulk contribution)
    # integral from n=0.5 to N_KK of g(x) dx  [midpoint to match discrete sum]
    # Actually, the standard EM: Sum_{n=1}^{N} ~ integral_1^N + boundary corrections
    # The integral from 1 to infinity of g(x) dx gives the bulk part.

    def g_integrand(n):
        return g_func(n, y_c, Phi_0)

    # Numerical integration from 1 to a large cutoff
    mu2_bulk, bulk_err = quad(g_integrand, 1.0, N_KK, limit=200, epsrel=1e-10)
    # Add the tail from N_KK to infinity (exponentially suppressed)
    if N_KK < 500:
        mu2_tail, _ = quad(g_integrand, N_KK, 2*N_KK, limit=100, epsrel=1e-8)
        mu2_bulk += mu2_tail

    # 3. Brane-localized part = total - bulk
    mu2_brane = mu2_total - mu2_bulk

    # 4. Euler-Maclaurin boundary corrections (for comparison)
    # EM: Sum = Integral + g(1)/2 + g(N)/2 + (1/12)[g'(1) - g'(N)] + ...
    # For our semi-infinite sum, g(N) -> 0, so:
    # Sum - Integral = g(1)/2 + (1/12) g'(1) + ...
    g1 = g_func(1, y_c, Phi_0)
    # Numerical derivative g'(1)
    dn = 0.001
    g1_prime = (g_func(1 + dn, y_c, Phi_0) - g_func(1 - dn, y_c, Phi_0)) / (2 * dn)
    # g'''(1)
    g1_ppp = (g_func(1+2*dn, y_c, Phi_0) - 2*g_func(1+dn, y_c, Phi_0) + 2*g_func(1-dn, y_c, Phi_0) - g_func(1-2*dn, y_c, Phi_0)) / (2*dn**3)

    em_leading = g1 / 2.0
    em_first_corr = g1_prime / 12.0
    em_second_corr = -g1_ppp / 720.0

    details = {
        'g1': g1, 'g1_prime': g1_prime, 'g1_ppp': g1_ppp,
        'em_leading': em_leading, 'em_first_corr': em_first_corr,
        'em_second_corr': em_second_corr,
        'em_total': em_leading + em_first_corr + em_second_corr
    }

    return mu2_total, mu2_bulk, mu2_brane, details


# === Compute at various Phi_0 ===
print(f"\n{'Phi_0':>10} {'mu2_total':>14} {'mu2_bulk':>14} {'mu2_brane':>14} {'brane/total':>12}")
print("-" * 70)

Phi0_values = [0.005, 0.01, 0.02, 0.03, 0.05, 0.073, 0.1, 0.15, 0.2, 0.3, 0.5]

brane_results = []
for phi0 in Phi0_values:
    mu2_tot, mu2_bulk, mu2_brane, details = compute_decomposition(phi0)
    ratio = mu2_brane / mu2_tot if abs(mu2_tot) > 1e-30 else float('nan')
    print(f"{phi0:10.3f} {mu2_tot:14.6e} {mu2_bulk:14.6e} {mu2_brane:14.6e} {ratio:12.4f}")
    brane_results.append({
        'Phi0': phi0, 'mu2_total': mu2_tot, 'mu2_bulk': mu2_bulk,
        'mu2_brane': mu2_brane, 'details': details
    })

# === Detailed analysis at Phi_0 ~ 0.073 (DESI target) ===
phi0_desi = 0.073
mu2_tot, mu2_bulk, mu2_brane, details = compute_decomposition(phi0_desi)

print(f"\n{'='*60}")
print(f"DETAILED ANALYSIS AT Phi_0 = {phi0_desi} (DESI target region)")
print(f"{'='*60}")
print(f"  mu^2(total)    = {mu2_tot:.6e} k^2  (full spectral sum)")
print(f"  mu^2(bulk)     = {mu2_bulk:.6e} k^2  (integral = smooth part)")
print(f"  mu^2(brane)    = {mu2_brane:.6e} k^2  (discrete - integral)")
print(f"  Target:          0.097 k^2")
print(f"  Naive (bulk xi R): {-E5:.4f} k^2")
print(f"")
print(f"  Euler-Maclaurin boundary corrections:")
print(f"    g(1)/2         = {details['em_leading']:.6e}")
print(f"    g'(1)/12       = {details['em_first_corr']:.6e}")
print(f"    -g'''(1)/720   = {details['em_second_corr']:.6e}")
print(f"    EM sum         = {details['em_total']:.6e}")
print(f"    Exact (sum-int)= {mu2_brane:.6e}")
print(f"    EM/Exact       = {details['em_total']/mu2_brane:.4f}" if abs(mu2_brane) > 1e-30 else "")


# === Junction condition solution with BRANE mu^2 ===
print(f"\n{'='*60}")
print(f"JUNCTION CONDITIONS WITH BRANE-LOCALIZED mu^2")
print(f"{'='*60}")

def solve_jc(sigma_uv, alpha_uv, mu_sq, xi_val, M5c):
    def residual(Phi_0):
        F_0 = M5c - xi_val * Phi_0**2
        if F_0 <= 0:
            return 1e10
        Aprime = -(sigma_uv + alpha_uv * Phi_0**2) / (12.0 * F_0)
        return 2.0 * mu_sq + 32.0 * xi_val * Phi_0 * Aprime + 4.0 * alpha_uv * Phi_0

    for lo, hi in [(1e-8, 0.5), (0.5, 2.0), (1e-10, 0.1), (0.01, 5.0), (1e-12, 1e-4)]:
        try:
            if residual(lo) * residual(hi) < 0:
                Phi_0 = brentq(residual, lo, hi, xtol=1e-15)
                F_0 = M5c - xi_val * Phi_0**2
                if F_0 <= 0:
                    continue
                Aprime = -(sigma_uv + alpha_uv * Phi_0**2) / (12.0 * F_0)
                zeta_0 = xi_val * Phi_0**2 / M5c
                return Phi_0, F_0, Aprime, zeta_0
        except (ValueError, RuntimeError):
            continue
    return None, None, None, None


def w0_from_zeta0(zeta0):
    if zeta0 <= 0 or zeta0 > 1:
        return np.nan
    kappa0 = C_KK * Omega_DE / (2.0 * zeta0)
    return -1.0 + 2.0 * kappa0 / (kappa0 + Omega_DE)


# Self-consistent solution: mu^2_brane(Phi_0) from EM decomposition, Phi_0 from JC
print(f"\nSelf-consistency scan with BRANE-LOCALIZED mu^2:")
print(f"{'Phi_0':>10} {'mu2_brane':>14} {'JC->Phi_0':>12} {'zeta_0':>14} {'w_0':>10} {'residual':>10}")
print("-" * 75)

best_sc = None
best_res = float('inf')

Phi0_scan = np.logspace(-4, 0, 150)
sc_results = []

for phi0 in Phi0_scan:
    _, _, mu2_b, _ = compute_decomposition(phi0)
    if np.isnan(mu2_b) or mu2_b <= 0:
        continue

    jc = solve_jc(sigma_UV, alpha_UV_SA, mu2_b, xi, M5_cubed)
    if jc[0] is None:
        continue

    phi0_jc = jc[0]
    zeta0_jc = jc[3]
    w0_jc = w0_from_zeta0(zeta0_jc)
    res = abs(phi0_jc - phi0) / phi0

    sc_results.append({
        'Phi0_in': phi0, 'mu2_brane': mu2_b, 'Phi0_JC': phi0_jc,
        'zeta0': zeta0_jc, 'w0': w0_jc, 'residual': res
    })

    if res < best_res:
        best_res = res
        best_sc = sc_results[-1]

# Print every 15th result
for r in sc_results[::15]:
    res_str = f"{r['residual']*100:.1f}%" if r['residual'] > 0.01 else "< 1%"
    print(f"{r['Phi0_in']:10.4f} {r['mu2_brane']:14.6e} {r['Phi0_JC']:12.6f} "
          f"{r['zeta0']:14.6e} {r['w0']:10.4f} {res_str:>10}")

# Refine best match
if best_sc is not None:
    print(f"\n--- Refining self-consistent solution (initial residual = {best_res*100:.2f}%) ---")
    phi0_iter = best_sc['Phi0_in']
    for it in range(50):
        _, _, mu2_b, _ = compute_decomposition(phi0_iter)
        if np.isnan(mu2_b) or mu2_b <= 0:
            print(f"  Failed: mu2_brane = {mu2_b} at Phi_0 = {phi0_iter}")
            break
        jc = solve_jc(sigma_UV, alpha_UV_SA, mu2_b, xi, M5_cubed)
        if jc[0] is None:
            print(f"  Failed: JC has no solution for mu2 = {mu2_b}")
            break
        phi0_new = jc[0]
        res = abs(phi0_new - phi0_iter) / max(abs(phi0_iter), 1e-15)
        if res < 1e-10:
            zeta0 = jc[3]
            w0 = w0_from_zeta0(zeta0)
            print(f"  Converged in {it+1} iterations:")
            print(f"    Phi_0    = {phi0_new:.10f}")
            print(f"    mu^2_br  = {mu2_b:.6e} k^2")
            print(f"    zeta_0   = {zeta0:.6e}")
            print(f"    w_0      = {w0:.6f}")
            best_sc = {'Phi0': phi0_new, 'mu2_brane': mu2_b,
                       'zeta0': zeta0, 'w0': w0, 'iterations': it+1}
            break
        phi0_iter = 0.5 * phi0_iter + 0.5 * phi0_new
    else:
        print(f"  Did not converge (residual = {res:.2e})")


# === COMPARISON: all three approaches ===
print(f"\n{'='*78}")
print(f"COMPARISON OF THREE APPROACHES TO mu^2")
print(f"{'='*78}")

# Approach 1: Naive bulk (xi R_5)
mu2_naive = -E5
jc_naive = solve_jc(sigma_UV, alpha_UV_SA, mu2_naive, xi, M5_cubed)
w0_naive = w0_from_zeta0(jc_naive[3]) if jc_naive[0] is not None else np.nan

# Approach 2: Full KK spectral sum (at self-consistent Phi_0 from that approach)
# Use Phi_0 = 1.566 from the product_heat_kernel.py result
phi0_full = 1.566
mu2_full_tot, _, _, _ = compute_decomposition(phi0_full)

# Approach 3: Brane-localized (EM decomposition)
mu2_brane_sc = best_sc['mu2_brane'] if best_sc is not None else np.nan
w0_brane = best_sc['w0'] if best_sc is not None else np.nan

print(f"""
  Approach          |  mu^2 / k^2  |  Phi_0    |  zeta_0       |  w_0
  ------------------|--------------|-----------|---------------|--------
  Naive (xi R_5)    |  {mu2_naive:.4f}     |  {jc_naive[0]:.4f}    |  {jc_naive[3]:.4e}  |  {w0_naive:.4f}
  Full KK sum       |  {mu2_full_tot:.4f}     |  1.566     |  4.09e-01      |  -0.9996
  Brane (EM decomp) |  {mu2_brane_sc:.4e}  |  {best_sc['Phi0']:.4e} |  {best_sc['zeta0']:.4e}  |  {w0_brane:.4f}
  DESI target       |  ~0.097      |  ~0.073   |  ~8.9e-04     |  -0.83
""" if best_sc is not None else "\n  Brane approach: no solution found\n")

# What mu^2_brane WOULD give DESI?
print("--- What brane mu^2 would match DESI? ---")
# Scan mu^2 directly through JC
for mu2_test in np.logspace(-4, 1, 200):
    jc = solve_jc(sigma_UV, alpha_UV_SA, mu2_test, xi, M5_cubed)
    if jc[0] is not None and jc[3] > 0 and jc[3] < 1:
        w0_test = w0_from_zeta0(jc[3])
        if abs(w0_test - (-0.83)) < 0.001:
            print(f"  mu^2 = {mu2_test:.6f} k^2 -> Phi_0 = {jc[0]:.6f}, "
                  f"zeta_0 = {jc[3]:.6e}, w_0 = {w0_test:.4f}")

# What is the gap?
print(f"\n--- THE MAGNITUDE GAP ---")
if best_sc is not None:
    print(f"  mu^2_brane (EM decomp) = {best_sc['mu2_brane']:.4e} k^2")
print(f"  mu^2_DESI (required)   = 0.097 k^2")
if best_sc is not None:
    gap = 0.097 / best_sc['mu2_brane'] if best_sc['mu2_brane'] > 0 else float('inf')
    print(f"  Gap factor: {gap:.1f}x")
print(f"  mu^2_bulk (full sum)   = {mu2_full_tot:.4f} k^2")
print(f"")
print(f"  The brane-localized spectral action is too SMALL for DESI.")
print(f"  The full KK sum (including bulk) is too LARGE for DESI.")
print(f"  DESI's mu^2 = 0.097 k^2 lies in the gap between these limits.")
print(f"")
print(f"  Possible resolutions:")
print(f"    1. Non-perturbative brane corrections (D-brane instantons)")
print(f"    2. Higher-order Vassilevich terms (b_{{7/2}}, b_{{9/2}})")
print(f"    3. Warped running of f_0/f_2 spectral moments")
print(f"    4. Brane kinetic terms from KK mode integration")
print(f"    5. The epsilon_1 (GB) parameter is larger than assumed")

print(f"\n{'='*78}")
print(f"COMPUTATION COMPLETE")
print(f"{'='*78}")
print(f"Done.")
