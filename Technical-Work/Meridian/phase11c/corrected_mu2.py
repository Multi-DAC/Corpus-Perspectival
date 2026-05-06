#!/usr/bin/env python3
"""
CORRECTED mu^2: Warped Eigenvalues with V_bulk = 0
====================================================

DISCOVERY: The GW scalar (Delta=2) on RS1 has a conformal transformation
psi = e^{2ky} chi that converts the 5D operator to:
  -chi'' = lambda chi  with Robin BCs: chi'(0) = -2k chi(0), chi'(y_c) = 2k chi(y_c)

The effective bulk potential is V_bulk = 4k^2 + m_Phi^2 = 4k^2 - 4k^2 = 0.

The PREVIOUS computation used V_bulk = (2/3)k^2, which was WRONG.
With V_bulk = 0:
  - Eigenvalues: lambda_n ~ (n pi/y_c)^2 (no offset)
  - More modes below cutoff: n up to ~12 (vs ~7 with V_bulk = 2/3)
  - Less cutoff suppression for low modes

This script:
1. Solves the Robin eigenvalue equation analytically
2. Recomputes the EM decomposition with correct eigenvalues
3. Finds the self-consistent solution
4. Compares to DESI

Clayton Iggulden-Schnell & Clawd, April 2026
"""

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq

print("=" * 78)
print("  CORRECTED mu^2: V_bulk = 0 (Warped RS1 Exact)")
print("=" * 78)

# === RS1 Parameters ===
k = 1.0
M5_cubed = 1.0
sigma_UV = 6.0 * M5_cubed * k
xi = 1.0 / 6.0
ky_c = 37.0
y_c = ky_c / k
Lambda = k
epsilon_GW = 2.0
alpha_UV_SA = -5.02e-4

eps_1 = 0.010
Omega_DE = 0.685
q0 = -0.5275
C_KK = (1 + q0)**2 * Omega_DE * eps_1 / (4 * (1 - q0)**2)

# === Robin eigenvalues ===
# The eigenvalue condition: tan(sqrt(lambda) y_c) = 4k sqrt(lambda)/(4k^2 - lambda)
# For lambda < 4k^2.
# For lambda > 4k^2: tan(sqrt(lambda) y_c) = -4k sqrt(lambda)/(lambda - 4k^2)

def robin_eigenvalue_condition(lam, yc, kval):
    """F(lambda) = 0 at eigenvalues."""
    if lam <= 0:
        # Bound state: use hyperbolic functions
        kappa = np.sqrt(-lam)
        return np.tanh(kappa * yc) - 4*kval*kappa / (kappa**2 + 4*kval**2)
    sqrtl = np.sqrt(lam)
    theta = sqrtl * yc
    if abs(4*kval**2 - lam) < 1e-10:
        return np.cos(theta)  # Degenerate case: tan must be infinite
    return np.tan(theta) - 4*kval*sqrtl / (4*kval**2 - lam)


# Find eigenvalues numerically
print("\n--- Robin eigenvalues on [0, y_c] with S = 2k ---")
print(f"  y_c = {y_c}, k = {k}")

# The eigenvalues are approximately:
#   lambda_0 = -4k^2 (bound state, exact for large ky_c)
#   lambda_n ~ (n pi/y_c)^2 for n >= 1 (with Robin corrections)
# We need n=1, 2, ... for the spectral sum (bound state doesn't contribute to mu^2)

robin_eigenvalues = []

# First, find the bound state
try:
    lam0 = brentq(lambda l: robin_eigenvalue_condition(l, y_c, k), -5*k**2, -0.01)
    robin_eigenvalues.append(lam0)
    print(f"  Bound state: lambda_0 = {lam0:.6f} k^2 (expected: -4k^2 = -4.0)")
except:
    print(f"  Bound state: not found numerically (exponentially close to -4k^2)")
    robin_eigenvalues.append(-4.0 * k**2)

# Positive eigenvalues: search near (n pi/y_c)^2 for n >= 1
for n in range(1, 60):
    # Search in the interval ((n-1/2)^2 pi^2/y_c^2, (n+1/2)^2 pi^2/y_c^2)
    # Avoiding the tan(theta) singularities at theta = (m+1/2)pi
    lo = ((n - 0.49) * np.pi / y_c)**2
    hi = ((n + 0.49) * np.pi / y_c)**2

    try:
        lam_n = brentq(lambda l: robin_eigenvalue_condition(l, y_c, k), lo, hi)
        robin_eigenvalues.append(lam_n)
    except:
        # Fall back to Neumann approximation
        robin_eigenvalues.append((n * np.pi / y_c)**2)

robin_eigenvalues = np.array(robin_eigenvalues)

# Compare with Neumann (flat) and V_bulk-shifted eigenvalues
V_bulk_old = 2.0 / 3.0 * k**2

print(f"\n  {'n':>4} {'Robin (exact)':>14} {'Neumann':>14} {'Neum+V_bulk':>14} {'Rob/Neum':>10}")
print("-" * 62)

for n in range(min(15, len(robin_eigenvalues))):
    rob = robin_eigenvalues[n]
    neum = (n * np.pi / y_c)**2
    neum_vb = neum + V_bulk_old
    ratio = rob / neum if abs(neum) > 1e-30 else float('inf')
    print(f"  {n:4d} {rob:14.6f} {neum:14.6f} {neum_vb:14.6f} {ratio:10.4f}")

# Modes below cutoff
n_below_robin = sum(1 for l in robin_eigenvalues if 0 < l < k**2)
n_below_flat = sum(1 for n in range(60) if (n*np.pi/y_c)**2 + V_bulk_old < k**2)
print(f"\n  Modes below cutoff (Lambda=k): Robin = {n_below_robin}, flat(+V_bulk) = {n_below_flat}")


# === D_F^2 spectrum ===
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

df2_eig = np.concatenate([sv_u**2, sv_d**2, sv_e**2])
df2_mult = np.array([4*N_c]*3 + [4*N_c]*3 + [4]*3)
N_F = 84
N_zero = N_F - int(sum(df2_mult))
if N_zero > 0:
    df2_eig = np.append(df2_eig, 0.0)
    df2_mult = np.append(df2_mult, N_zero)


# === Spectral sum with Robin eigenvalues ===
print("\n" + "=" * 78)
print("SPECTRAL SUM WITH ROBIN EIGENVALUES (V_bulk = 0)")
print("=" * 78)

# Use eigenvalues lambda_n for n >= 1 (bound state doesn't contribute to mu^2
# because d(lambda_0)/dy_c = 0 — the bound state is at -4k^2 independent of y_c)

# Robin eigenvalue derivatives d(lambda_n)/dy_c
# For lambda_n ~ (n pi/y_c)^2 with Robin correction:
# d(lambda_n)/dy_c = -2(n pi)^2 / y_c^3 * (1 + Robin correction derivative)
# The Robin correction is ~ 2/(ky_c), so d/dy_c adds a term of order 1/y_c^2

# Compute numerically
delta_yc = 0.01
robin_eig_plus = []
robin_eig_minus = []

for n in range(1, 60):
    lo_p = ((n - 0.49) * np.pi / (y_c + delta_yc))**2
    hi_p = ((n + 0.49) * np.pi / (y_c + delta_yc))**2
    lo_m = ((n - 0.49) * np.pi / (y_c - delta_yc))**2
    hi_m = ((n + 0.49) * np.pi / (y_c - delta_yc))**2
    try:
        lam_p = brentq(lambda l: robin_eigenvalue_condition(l, y_c + delta_yc, k), lo_p, hi_p)
        lam_m = brentq(lambda l: robin_eigenvalue_condition(l, y_c - delta_yc, k), lo_m, hi_m)
        robin_eig_plus.append(lam_p)
        robin_eig_minus.append(lam_m)
    except:
        robin_eig_plus.append((n * np.pi / (y_c + delta_yc))**2)
        robin_eig_minus.append((n * np.pi / (y_c - delta_yc))**2)

robin_eig_plus = np.array(robin_eig_plus)
robin_eig_minus = np.array(robin_eig_minus)
d_robin_dyc = (robin_eig_plus - robin_eig_minus) / (2.0 * delta_yc)

# Positive eigenvalues only (skip bound state)
robin_pos = robin_eigenvalues[1:]  # n=1, 2, 3, ...
N_modes = len(robin_pos)

print(f"\nUsing {N_modes} positive Robin eigenvalues (n=1 to {N_modes})")
print(f"Bound state lambda_0 = {robin_eigenvalues[0]:.4f} excluded (d/dy_c = 0)")


def g_summand_robin(n_idx, Phi_0):
    """Summand for mu^2 using Robin eigenvalues. n_idx is 0-based (= mode n-1)."""
    if n_idx < 0 or n_idx >= len(robin_pos):
        return 0.0
    lam_n = robin_pos[n_idx]
    dlam_dPhi = d_robin_dyc[n_idx] / (epsilon_GW * Phi_0)
    total = 0.0
    for lam2, mult in zip(df2_eig, df2_mult):
        x = (lam_n + lam2) / Lambda**2
        total += mult * (-np.exp(-x)) * dlam_dPhi / Lambda**2
    return total


def g_summand_flat_corrected(n_cont, Phi_0):
    """Continuous extension using flat eigenvalues with V_bulk = 0."""
    if n_cont < 0.5:
        return 0.0
    mn2 = (n_cont * np.pi / y_c)**2  # V_bulk = 0 now!
    dmn2_dPhi = -2.0 * (n_cont * np.pi)**2 / (y_c**3 * epsilon_GW * Phi_0)
    total = 0.0
    for lam2, mult in zip(df2_eig, df2_mult):
        x = (mn2 + lam2) / Lambda**2
        total += mult * (-np.exp(-x)) * dmn2_dPhi / Lambda**2
    return total


def compute_mu2_corrected(Phi_0):
    """EM decomposition with Robin eigenvalues and V_bulk = 0."""
    # Discrete sum over Robin eigenvalues
    mu2_sum = sum(g_summand_robin(i, Phi_0) for i in range(N_modes))

    # Integral (bulk part) with V_bulk = 0
    def integrand(n_cont):
        return g_summand_flat_corrected(n_cont, Phi_0)

    mu2_int, _ = quad(integrand, 0.5, N_modes + 0.5, limit=500, epsrel=1e-12)
    # Tail beyond computed eigenvalues
    mu2_tail, _ = quad(integrand, N_modes + 0.5, 3 * N_modes, limit=200, epsrel=1e-10)
    mu2_int += mu2_tail

    return mu2_sum, mu2_int, mu2_sum - mu2_int


# === Compare old (V_bulk = 2/3) and new (V_bulk = 0) ===
print(f"\n{'Phi_0':>10} {'old (Vb=2/3)':>14} {'new (Vb=0)':>14} {'ratio':>10}")
print("-" * 55)

Phi0_vals = [0.01, 0.02, 0.04, 0.073, 0.1, 0.2, 0.5]

for phi0 in Phi0_vals:
    # Old value (V_bulk = 2/3, from verified computation)
    old_brane = 0.05820 * (0.0436 / phi0)  # Scales as 1/Phi_0

    # New value (V_bulk = 0, Robin eigenvalues)
    _, _, new_brane = compute_mu2_corrected(phi0)

    ratio = new_brane / old_brane if abs(old_brane) > 1e-30 else float('nan')
    print(f"{phi0:10.4f} {old_brane:14.6e} {new_brane:14.6e} {ratio:10.4f}")


# === Self-consistent solution ===
print("\n" + "=" * 78)
print("SELF-CONSISTENT SOLUTION (V_bulk = 0, Robin eigenvalues)")
print("=" * 78)

def solve_jc(sigma_uv, alpha_uv, mu_sq, xi_val, M5c):
    def residual(Phi_0):
        F_0 = M5c - xi_val * Phi_0**2
        if F_0 <= 0:
            return 1e10
        Aprime = -(sigma_uv + alpha_uv * Phi_0**2) / (12.0 * F_0)
        return 2.0 * mu_sq + 32.0 * xi_val * Phi_0 * Aprime + 4.0 * alpha_uv * Phi_0
    for lo, hi in [(1e-8, 0.5), (0.5, 2.0), (1e-10, 0.1), (0.01, 5.0)]:
        try:
            if residual(lo) * residual(hi) < 0:
                Phi_0 = brentq(residual, lo, hi, xtol=1e-15)
                F_0 = M5c - xi_val * Phi_0**2
                if F_0 <= 0: continue
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


# Iterate
print("\nIterating to self-consistency...")
phi0_iter = 0.04
for it in range(50):
    _, _, mu2_b = compute_mu2_corrected(phi0_iter)
    if np.isnan(mu2_b) or mu2_b <= 0:
        print(f"  iter {it}: mu2_brane = {mu2_b}, phi0 = {phi0_iter}")
        break
    jc = solve_jc(sigma_UV, alpha_UV_SA, mu2_b, xi, M5_cubed)
    if jc[0] is None:
        print(f"  iter {it}: JC failed for mu2 = {mu2_b}")
        break
    phi0_new = jc[0]
    res = abs(phi0_new - phi0_iter) / max(abs(phi0_iter), 1e-15)
    if it % 5 == 0 or res < 1e-8:
        zeta0 = jc[3]
        w0 = w0_from_zeta0(zeta0)
        print(f"  iter {it:2d}: Phi_0={phi0_new:.8f}, mu2={mu2_b:.6e}, z0={zeta0:.6e}, w0={w0:.6f}, res={res:.2e}")
    if res < 1e-10:
        zeta0_final = jc[3]
        w0_final = w0_from_zeta0(zeta0_final)
        mu2_final = mu2_b
        phi0_final = phi0_new
        print(f"\n  CONVERGED in {it+1} iterations!")
        break
    phi0_iter = 0.5 * phi0_iter + 0.5 * phi0_new
else:
    print(f"  Did not converge.")
    zeta0_final = jc[3] if jc[0] is not None else np.nan
    w0_final = w0_from_zeta0(zeta0_final)
    mu2_final = mu2_b
    phi0_final = phi0_iter


# === FINAL RESULTS ===
print(f"\n{'='*78}")
print(f"FINAL RESULTS — CORRECTED PREDICTION")
print(f"{'='*78}")
print(f"""
  OLD (V_bulk = 2/3 k^2, Neumann BCs):
    mu^2  = 0.0582 k^2
    Phi_0 = 0.0436
    zeta_0 = 3.17e-4
    w_0   = -0.589
    Gap to DESI: 1.7x

  NEW (V_bulk = 0, Robin BCs from warped geometry):
    mu^2  = {mu2_final:.4e} k^2
    Phi_0 = {phi0_final:.6f}
    zeta_0 = {zeta0_final:.4e}
    w_0   = {w0_final:.6f}

  DESI DR2: w_0 = -0.83 +/- 0.06

  Correction factor: {mu2_final / 0.0582:.4f}x
  New gap to DESI: {0.097 / mu2_final:.2f}x (was 1.7x)
""")

# What w_0 does DESI need?
print("--- What mu^2 matches DESI? ---")
for mu2_test in np.linspace(0.05, 0.15, 200):
    jc = solve_jc(sigma_UV, alpha_UV_SA, mu2_test, xi, M5_cubed)
    if jc[0] is not None and jc[3] > 0 and jc[3] < 1:
        w0_test = w0_from_zeta0(jc[3])
        if abs(w0_test - (-0.83)) < 0.002:
            print(f"  mu^2 = {mu2_test:.6f}, Phi_0 = {jc[0]:.6f}, zeta_0 = {jc[3]:.6e}, w_0 = {w0_test:.4f}")

print("\nDone.")
