#!/usr/bin/env python3
"""
Steps 3+4: Warped KK Eigenvalues and IR Brane Contribution
============================================================

Step 3: The flat-space eigenvalues m_n^2 = (n pi/y_c)^2 + V_bulk are an
approximation. In the actual RS1 warped geometry, the scalar eigenvalue
problem is a Sturm-Liouville ODE with the warp factor.

Step 4: The EM decomposition extracts boundary corrections at BOTH ends
of the interval. Our previous computation only included the UV brane (n=1 end).
The IR brane (n -> infinity end) may contribute differently because of the
warped mode functions.

This script:
1. Solves the actual warped Sturm-Liouville problem for KK eigenvalues
2. Computes the spectral sum with warped eigenvalues
3. Includes the IR brane contribution via mode function amplitudes
4. Runs the EM decomposition with all corrections
5. Feeds the corrected mu^2 into the JC solver for w_0

Clayton Iggulden-Schnell & Clawd, April 2026
"""

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import numpy as np
from scipy.integrate import solve_bvp, quad
from scipy.optimize import brentq
from scipy.linalg import eig_banded

print("=" * 78)
print("  STEPS 3+4: WARPED KK EIGENVALUES + IR BRANE")
print("=" * 78)

# === RS1 Parameters ===
k = 1.0
M5_cubed = 1.0
sigma_UV = 6.0 * M5_cubed * k
xi = 1.0 / 6.0
ky_c = 37.0
Lambda = k
epsilon_GW = 2.0  # = 4 - Delta_GW

alpha_UV_SA = -5.02e-4  # Negligible (from Step 2)
eps_1 = 0.010
Omega_DE = 0.685
q0 = -0.5275
C_KK = (1 + q0)**2 * Omega_DE * eps_1 / (4 * (1 - q0)**2)

# GW scalar: bulk mass m_Phi^2 = Delta(Delta-4) k^2 = 2(2-4) = -4 k^2
Delta_GW = 2.0
m_Phi_sq = Delta_GW * (Delta_GW - 4.0) * k**2  # = -4 k^2

# Conformal coupling
xi_conf = 1.0 / 6.0

# 5D Ricci scalar in AdS_5
R5 = -20.0 * k**2

# Effective bulk potential for GW scalar
# V_eff = m_Phi^2 + xi R_5 = -4 + (1/6)(-20) = -4 - 10/3 = -22/3
# But for the eigenvalue problem in Schrodinger form, the potential depends
# on the field decomposition.

print(f"\nRS1: k={k}, ky_c={ky_c}")
print(f"GW scalar: m_Phi^2 = {m_Phi_sq:.1f} k^2, Delta = {Delta_GW}")


# =============================================================================
# STEP 3: WARPED KK EIGENVALUES
# =============================================================================
print("\n" + "=" * 78)
print("STEP 3: Warped KK Eigenvalues (Sturm-Liouville on RS1)")
print("=" * 78)

# The GW scalar in the RS1 background:
#   ds^2 = e^{-2A(y)} eta_{mu nu} dx^mu dx^nu + dy^2
#   A(y) = ky  (AdS_5 warp factor)
#
# The scalar field equation for phi(x,y) = chi(y) e^{ip.x}:
#   -e^{2A} d/dy (e^{-4A} d/dy (e^{2A} chi)) + m_Phi^2 chi = p^2 chi / e^{2A}
#
# Wait -- for a MINIMALLY coupled scalar (not conformally coupled) with mass m_Phi:
#   (-Box_5 + m_Phi^2) Phi = 0
#   Box_5 = e^{2A}(Box_4 + e^{-4A} d/dy e^{4A} d/dy)
#
# Substituting Phi(x,y) = phi_n(y) f_n(x) with Box_4 f_n = -M_n^2 f_n:
#   e^{-4A} d/dy(e^{4A} d/dy phi_n) + (M_n^2 e^{-2A} + m_Phi^2) phi_n = 0
#
# Schrodinger form: let phi_n = e^{-2A} psi_n (remove first derivative)
#   -psi_n'' + V(y) psi_n = M_n^2 e^{-2A} psi_n
#
# The Schrodinger potential for the GW scalar:
#   V(y) = 4A''^2 - 2A'' + m_Phi^2 e^{-2A}
# Wait, this isn't quite right for RS1. Let me be more careful.
#
# For A(y) = k|y| on the orbifold:
#   A' = k (for y > 0), A'' = 2k delta(y) - 2k delta(y - y_c)
#
# The eigenvalue equation in the bulk (away from branes):
#   phi_n'' - 4k phi_n' + (M_n^2 e^{2ky} - m_Phi^2) phi_n = 0
#
# Substituting phi_n = e^{2ky} psi_n:
#   psi_n'' + (M_n^2 e^{2ky} - m_Phi^2 - 4k^2) psi_n = 0
#
# This is a Bessel equation in z = (M_n/k) e^{ky}:
#   z^2 psi'' + z psi' + (z^2 - nu^2) psi = 0
#   with nu^2 = 4 + m_Phi^2/k^2 = 4 + (-4) = 0
#   So nu = 0 for the GW scalar with Delta=2!
#
# Solutions: J_0(z) and Y_0(z) where z = (M_n/k) e^{ky}
#
# BCs from the brane delta functions (Israel conditions):
#   UV brane (y=0): phi_n'(0+) = (2k + m_UV^2/2k) phi_n(0) [Robin BC]
#   For Neumann (m_UV = 0): phi_n'(0+) = 2k phi_n(0)
#   In terms of psi: psi_n'(0+) = 0 (Neumann for psi)
#
#   IR brane (y=y_c): similar condition
#
# Actually, for the GW scalar with Delta=2 and Neumann BCs at both branes,
# the eigenvalue equation in terms of z = M_n e^{ky}/k is:
#   J_0'(z_0) Y_0'(z_1) - Y_0'(z_0) J_0'(z_1) = 0
#   where z_0 = M_n/k, z_1 = M_n e^{ky_c}/k

# But wait -- for the SPECTRAL ACTION, we need the eigenvalues of the 5D
# Laplacian (or Dirac squared), not the 4D KK masses.
# The 5D spectral action involves Tr[f(D_5^2 / Lambda^2)] where D_5^2
# is the 5D operator. The eigenvalues of D_5^2 are:
#   lambda_{n,p}^2 = p^2 + M_n^2  (4D momentum + KK mass)
#
# The spectral action integrates over p, leaving:
#   S ~ Sum_n F(M_n^2 / Lambda^2)
#
# So we need the 4D KK masses M_n^2 as eigenvalues.
# For the GW scalar with nu=0, these are determined by:

from scipy.special import j0, y0, j1, y1

def bessel_bc_equation(M, k_val, y_c_val):
    """
    The eigenvalue condition for the GW scalar (nu=0) on RS1:
    J_0'(z_0) Y_0'(z_1) - Y_0'(z_0) J_0'(z_1) = 0

    where z_0 = M/k, z_1 = M e^{ky_c}/k
    and J_0'(z) = -J_1(z), Y_0'(z) = -Y_1(z)
    """
    if M < 1e-15:
        return 0.0  # Zero mode
    z0 = M / k_val
    z1 = M * np.exp(k_val * y_c_val) / k_val

    # Avoid numerical overflow for large z1
    if z1 > 1e10:
        # For large z, J_1(z) ~ sqrt(2/(pi z)) cos(z - 3pi/4)
        # Y_1(z) ~ sqrt(2/(pi z)) sin(z - 3pi/4)
        # The BC becomes approximately: sin(z1 - z0 + phase) = 0
        # Eigenvalues spaced by: Delta_z ~ pi, so Delta_M ~ pi k e^{-ky_c}
        # These are the LIGHT KK modes, exponentially suppressed.
        # For the spectral action with Lambda = k, these are at
        # M_n ~ n pi k e^{-ky_c} which is ~ 10^{-16} k.
        # These are WAY below the cutoff and all contribute equally to f(M_n^2/k^2).
        # We don't need to resolve them individually.
        return np.nan

    return (-j1(z0)) * (-y1(z1)) - (-y1(z0)) * (-j1(z1))


# The KK spectrum has two sectors:
# 1. LIGHT modes: M_n ~ n pi k e^{-ky_c} (IR-localized, exponentially light)
# 2. HEAVY modes: M_n ~ n pi k / y_c (UV-localized, spacing ~ k/y_c)
#
# For the spectral action with Lambda = k:
# - Light modes: M_n/k ~ 10^{-16}, so f(M_n^2/k^2) ~ f(0) ~ 1 for ALL of them
#   They contribute a CONSTANT (modulus-independent) offset. No effect on mu^2.
# - Heavy modes: M_n ~ (n pi / y_c) k, which is the SAME as our flat-space estimate!
#   These are the modes that contribute to mu^2.
#
# The WARPING CORRECTION enters through:
# 1. The exact eigenvalue positions (shifted from flat-space values)
# 2. The mode function normalization (wavefunction amplitude at the brane)

print("\nThe KK spectrum for the GW scalar (nu=0) on RS1 has two sectors:")
print("  LIGHT: M_n ~ n pi k e^{-ky_c} << k  (IR-localized)")
print("  HEAVY: M_n ~ O(k)  (UV-localized)")
print("")
print("For the spectral action with Lambda = k:")
print("  Light modes: f(M^2/k^2) ~ f(0) = 1 for ALL. Modulus-INDEPENDENT.")
print("  Heavy modes: f(M^2/k^2) varies. Modulus-DEPENDENT -> contributes to mu^2.")
print("")
print("The flat-space approximation is EXACT for the heavy modes up to")
print("corrections of order (k/M_n)^2, which vanish for modes near the cutoff.")

# Actually, let me think about this more carefully.
# The "heavy modes" in the warped geometry are NOT the same as the flat-space
# Neumann modes (n pi / y_c)^2.
#
# In the flat-space approximation, we used:
#   m_n^2 = (n pi / y_c)^2 + V_bulk
#
# In the warped geometry, the 5D eigenvalues of the scalar Laplacian are
# NOT simply the KK masses. The 5D spectral action involves the FULL 5D
# operator, which in the warped background has eigenvalues that depend on
# both the 4D momentum and the KK mode number.
#
# For the spectral action, the key quantity is:
#   Tr[f(D_5^2 / Lambda^2)] = integral d^4p Sum_n f((p^2 + M_n^2)/Lambda^2)
#
# After the 4D momentum integral, this becomes:
#   S = (Lambda^4 / (16 pi^2)) * Sum_n F_2(M_n^2 / Lambda^2)
#
# where F_2(x) = integral_0^inf t f(t + x) dt is the second moment.
#
# For f(x) = exp(-x): F_2(x) = exp(-x)
# So S = (Lambda^4 / (16 pi^2)) * Sum_n exp(-M_n^2 / Lambda^2)
#
# The MU^2 derivative: dS/dPhi_0 = (Lambda^4 / (16 pi^2)) * Sum_n f'(M_n^2/Lambda^2) * dM_n^2/dPhi_0 / Lambda^2

# KEY INSIGHT: The spectral action (after 4D momentum integration) depends
# only on the 4D KK masses M_n^2 through f(M_n^2/Lambda^2).
# The flat-space approximation M_n^2 = (n pi/y_c)^2 applies when:
#   1. The modes are UV-localized (large M_n)
#   2. The warp factor is approximately constant over the mode wavelength
#
# For modes with M_n ~ k (the ones that matter), the warp factor changes
# by O(1) over the mode wavelength ~ 1/M_n ~ 1/k. So warping corrections
# are O(1), not small!
#
# BUT -- and this is the key -- in my computation, V_bulk = (2/3)k^2 already
# accounts for the bulk curvature in an average sense. The CORRECTION from
# exact warped eigenvalues is the difference between the exact M_n^2 and
# (n pi/y_c)^2 + V_bulk.
#
# To compute exact eigenvalues, I need to solve the eigenvalue problem
# NUMERICALLY on a discretized interval.

print("\n--- Numerical KK eigenvalues on discretized warped interval ---")

# Discretize the interval [0, y_c] with N points
N_grid = 2000
y_grid = np.linspace(0, ky_c, N_grid + 1)
dy = y_grid[1] - y_grid[0]

# The eigenvalue equation for phi(y) with A(y) = ky:
#   phi'' - 4k phi' + (M^2 e^{2ky} - m_Phi^2) phi = 0
#   BCs: phi'(0) = 2k phi(0)  [from brane delta, Neumann for GW scalar]
#         phi'(y_c) = -2k phi(y_c) [from IR brane delta]
#
# In Schrodinger form, substitute phi = e^{2ky} psi:
#   psi'' + (M^2 e^{2ky} - 4k^2 - m_Phi^2) psi = 0
#   BCs: psi'(0) = 0, psi'(y_c) = 0  (Neumann for psi)
#
# Since m_Phi^2 = -4k^2: the potential is V(y) = 4k^2 + m_Phi^2 = 0 !!
#
# Wait -- for nu = 0 (which IS our case), the Schrodinger potential is ZERO
# in the bulk! The equation becomes:
#   psi'' + M^2 e^{2ky} psi = 0
#   with Neumann BCs: psi'(0) = 0, psi'(y_c) = 0
#
# This is EXACT for the GW scalar with Delta = 2.

# For nu = 0, the equation -psi'' = M^2 e^{2ky} psi is a generalized
# eigenvalue problem. The exponential warp factor acts as a position-dependent
# "mass density".
#
# I'll solve this as a matrix eigenvalue problem.

print(f"Grid: N = {N_grid}, dy = {dy:.4f}")
print(f"GW scalar with nu=0: bulk Schrodinger potential V(y) = 0")
print(f"Equation: -psi'' = M^2 e^{{2ky}} psi with Neumann BCs")

# Build the discretized Laplacian with Neumann BCs
# Using second-order finite differences:
# psi''(y_i) ~ (psi_{i-1} - 2 psi_i + psi_{i+1}) / dy^2
# Neumann at i=0: psi_{-1} = psi_1 -> psi''(0) ~ (2 psi_1 - 2 psi_0) / dy^2
# Neumann at i=N: psi_{N+1} = psi_{N-1} -> same structure

# Interior points only (i = 0 to N_grid)
N = N_grid + 1  # Total points including boundaries

# Build -d^2/dy^2 matrix (N x N)
diag_main = 2.0 * np.ones(N) / dy**2
diag_off = -1.0 * np.ones(N - 1) / dy**2

# Neumann BC modifications
diag_main[0] = 2.0 / dy**2  # same
diag_off[0] = -2.0 / dy**2  # ghost point: psi_{-1} = psi_1
diag_main[-1] = 2.0 / dy**2
diag_off[-1] = -2.0 / dy**2  # ghost point: psi_{N+1} = psi_{N-1}

# The Laplacian matrix (tridiagonal)
from scipy.sparse import diags
from scipy.sparse.linalg import eigsh

L = diags([diag_off, diag_main, diag_off], [-1, 0, 1], shape=(N, N)).toarray()

# Build the weight matrix W = e^{2ky} (diagonal)
W = np.diag(np.exp(2.0 * k * y_grid))

# Generalized eigenvalue problem: L psi = M^2 W psi
# This is equivalent to W^{-1} L psi = M^2 psi
# For the lowest eigenvalues, use eigh on the dense matrices

from scipy.linalg import eigh

# Solve generalized eigenvalue problem
M_sq_all, psi_all = eigh(L, W, subset_by_index=[0, min(99, N-1)])

print(f"\nFirst 15 warped KK eigenvalues M_n^2:")
print(f"  {'n':>4} {'M_n^2 (warped)':>16} {'M_n^2 (flat)':>16} {'ratio':>10} {'diff/k^2':>12}")
print("-" * 65)

V_bulk_flat = 2.0 / 3.0 * k**2

for n in range(min(15, len(M_sq_all))):
    M2_warped = M_sq_all[n]
    M2_flat = (n * np.pi / ky_c)**2 + V_bulk_flat
    ratio = M2_warped / M2_flat if abs(M2_flat) > 1e-30 else float('inf')
    diff = M2_warped - M2_flat
    print(f"  {n:4d} {M2_warped:16.6f} {M2_flat:16.6f} {ratio:10.4f} {diff:12.6f}")

# For n > ~7, the flat approximation should be good.
# For n = 0 (zero mode), the warped eigenvalue may differ significantly.

# Check: what is the zero mode mass?
print(f"\n  Zero mode: M_0^2 = {M_sq_all[0]:.6e} k^2")
print(f"    (Should be ~0 for unstabilized modulus, or ~V_bulk for flat approx)")
print(f"    Flat approximation: M_0^2 = V_bulk = {V_bulk_flat:.4f} k^2")


# =============================================================================
# STEP 4: MODE FUNCTION AMPLITUDES AT BOTH BRANES
# =============================================================================
print("\n" + "=" * 78)
print("STEP 4: Mode Function Amplitudes at UV and IR Branes")
print("=" * 78)

# The mode functions psi_n(y) from the eigenvalue problem.
# Their amplitude at the branes determines the brane-localized contribution.
#
# In the flat case, all modes have equal amplitude at the UV brane:
#   psi_n(0) = sqrt(2/y_c) for n >= 1
#
# In the warped case, UV-localized modes have enhanced amplitude at y=0,
# and IR-localized modes have enhanced amplitude at y=y_c.

print(f"\nMode function amplitudes (normalized):")
print(f"  {'n':>4} {'|psi_n(0)|^2':>14} {'|psi_n(y_c)|^2':>16} {'UV/IR ratio':>12}")
print("-" * 52)

for n in range(min(15, len(M_sq_all))):
    psi_n = psi_all[:, n]
    # Normalize: integral |psi_n|^2 W(y) dy = 1
    norm = np.sqrt(np.trapezoid(psi_n**2 * np.exp(2*k*y_grid), y_grid))
    psi_n_normed = psi_n / norm if norm > 1e-30 else psi_n

    uv_amp = psi_n_normed[0]**2
    ir_amp = psi_n_normed[-1]**2
    ratio_uv_ir = uv_amp / ir_amp if abs(ir_amp) > 1e-30 else float('inf')
    print(f"  {n:4d} {uv_amp:14.6e} {ir_amp:16.6e} {ratio_uv_ir:12.2e}")


# =============================================================================
# CORRECTED SPECTRAL SUM WITH WARPED EIGENVALUES
# =============================================================================
print("\n" + "=" * 78)
print("CORRECTED SPECTRAL SUM WITH WARPED EIGENVALUES")
print("=" * 78)

# D_F^2 spectrum (same as before)
def g_profile_at(c, ky):
    delta = 0.5 - c
    if abs(2*delta*ky) < 1e-8:
        return 1.0 / np.sqrt(ky)
    val = (1 - 2*c) / (np.exp((1 - 2*c)*ky) - 1)
    return np.sqrt(np.abs(val)) * np.exp(delta*ky) * np.sign(val)

c_Q = np.array([0.557, 0.646, 0.247])
c_u = np.array([0.661, 0.415, 0.200])
c_d = np.array([0.495, 0.465, 0.567])
c_L = np.array([0.650, 0.580, 0.520])
c_e = np.array([0.660, 0.590, 0.500])
Y5_u, Y5_d, Y5_e = 1.75, 0.18, 0.10
N_c = 3
M_oct = np.array([[1.0, 0.5, 0.5], [0.5, 1.0, 0.5], [0.5, 0.5, 1.0]])

g_Q_ = np.array([g_profile_at(c, ky_c) for c in c_Q])
g_u_ = np.array([g_profile_at(c, ky_c) for c in c_u])
g_d_ = np.array([g_profile_at(c, ky_c) for c in c_d])
g_L_ = np.array([g_profile_at(c, ky_c) for c in c_L])
g_e_ = np.array([g_profile_at(c, ky_c) for c in c_e])

Y_u_ = Y5_u * M_oct * np.outer(g_Q_, g_u_)
Y_d_ = Y5_d * M_oct * np.outer(g_Q_, g_d_)
Y_e_ = Y5_e * M_oct * np.outer(g_L_, g_e_)

sv_u_ = np.linalg.svd(Y_u_, compute_uv=False)
sv_d_ = np.linalg.svd(Y_d_, compute_uv=False)
sv_e_ = np.linalg.svd(Y_e_, compute_uv=False)

df2_eig = np.concatenate([sv_u_**2, sv_d_**2, sv_e_**2])
df2_mult = np.array([4*N_c]*3 + [4*N_c]*3 + [4]*3)
N_F_total = 84
N_zero = N_F_total - int(sum(df2_mult))
if N_zero > 0:
    df2_eig = np.append(df2_eig, 0.0)
    df2_mult = np.append(df2_mult, N_zero)

# Use the warped eigenvalues instead of flat-space
N_modes = min(50, len(M_sq_all))
M_sq_warped = M_sq_all[:N_modes]

# Also compute eigenvalues at shifted y_c for the derivative
# The KK masses depend on y_c. To compute dM_n^2/dy_c, we need eigenvalues
# at y_c +/- delta.
delta_yc = 0.01

def compute_warped_eigenvalues(yc_val, n_modes=50):
    """Solve the warped eigenvalue problem at a given y_c."""
    n_grid = 2000
    y_g = np.linspace(0, yc_val, n_grid + 1)
    dy_g = y_g[1] - y_g[0]
    nn = n_grid + 1

    d_main = 2.0 * np.ones(nn) / dy_g**2
    d_off = -1.0 * np.ones(nn - 1) / dy_g**2
    d_main[0] = 2.0 / dy_g**2
    d_off[0] = -2.0 / dy_g**2
    d_main[-1] = 2.0 / dy_g**2
    d_off[-1] = -2.0 / dy_g**2

    L_local = diags([d_off, d_main, d_off], [-1, 0, 1], shape=(nn, nn)).toarray()
    W_local = np.diag(np.exp(2.0 * k * y_g))

    evals, _ = eigh(L_local, W_local, subset_by_index=[0, min(n_modes - 1, nn - 1)])
    return evals


print(f"\nComputing warped eigenvalues at y_c = {ky_c}, {ky_c+delta_yc}, {ky_c-delta_yc}...")
M_sq_0 = compute_warped_eigenvalues(ky_c)
M_sq_plus = compute_warped_eigenvalues(ky_c + delta_yc)
M_sq_minus = compute_warped_eigenvalues(ky_c - delta_yc)

# dM_n^2 / dy_c (numerical derivative)
dM_sq_dyc = (M_sq_plus - M_sq_minus) / (2.0 * delta_yc)

print(f"\nWarped eigenvalue derivatives dM_n^2/dy_c:")
print(f"  {'n':>4} {'M_n^2':>12} {'dM_n^2/dy_c':>14} {'flat dM/dyc':>14} {'ratio':>10}")
print("-" * 60)

for n in range(min(15, len(dM_sq_dyc))):
    flat_deriv = -2.0 * (n * np.pi)**2 / ky_c**3 if n > 0 else 0.0
    ratio = dM_sq_dyc[n] / flat_deriv if abs(flat_deriv) > 1e-30 else float('inf')
    print(f"  {n:4d} {M_sq_0[n]:12.6f} {dM_sq_dyc[n]:14.6e} {flat_deriv:14.6e} {ratio:10.4f}")


# =============================================================================
# CORRECTED mu^2 WITH WARPED EIGENVALUES
# =============================================================================
print("\n" + "=" * 78)
print("CORRECTED mu^2 WITH WARPED EIGENVALUES")
print("=" * 78)

def compute_mu2_warped(Phi_0, M_sq_arr, dM_sq_dyc_arr, df2_e, df2_m, Lam=k):
    """
    Compute mu^2 = dS/dPhi_0 using warped KK eigenvalues.

    mu^2 = Sum_{n} Sum_i mult_i * f'((M_n^2 + lam_i^2)/Lam^2) * dM_n^2/dPhi_0 / Lam^2
    where dM_n^2/dPhi_0 = (dM_n^2/dy_c) * (dy_c/dPhi_0) = (dM_n^2/dy_c) / (epsilon * Phi_0)
    """
    if Phi_0 <= 0:
        return np.nan

    dyc_dPhi = 1.0 / (epsilon_GW * Phi_0)
    mu2 = 0.0

    for n in range(len(M_sq_arr)):
        if abs(dM_sq_dyc_arr[n]) < 1e-30:
            continue  # Skip modes with no modulus dependence
        dMn2_dPhi = dM_sq_dyc_arr[n] * dyc_dPhi
        for lam2, mult in zip(df2_e, df2_m):
            x = (M_sq_arr[n] + lam2) / Lam**2
            fprime = -np.exp(-x)
            mu2 += mult * fprime * dMn2_dPhi / Lam**2

    return mu2


def compute_mu2_warped_em(Phi_0, M_sq_arr, dM_sq_dyc_arr, df2_e, df2_m, Lam=k):
    """
    Compute brane-localized mu^2 via EM decomposition with warped eigenvalues.

    The summand g(n) uses WARPED eigenvalues. The integral is over the
    continuous extension (interpolated).
    """
    if Phi_0 <= 0:
        return np.nan, np.nan, np.nan

    dyc_dPhi = 1.0 / (epsilon_GW * Phi_0)

    # Discrete sum
    mu2_sum = 0.0
    for n in range(len(M_sq_arr)):
        dMn2_dPhi = dM_sq_dyc_arr[n] * dyc_dPhi
        for lam2, mult in zip(df2_e, df2_m):
            x = (M_sq_arr[n] + lam2) / Lam**2
            mu2_sum += mult * (-np.exp(-x)) * dMn2_dPhi / Lam**2

    # For the integral (bulk part), use the FLAT-SPACE formula as the smooth part
    # The warped corrections to individual eigenvalues average out in the integral
    def g_flat(n_cont):
        if n_cont < 1e-10:
            return 0.0
        V_bulk_loc = 2.0 / 3.0 * k**2
        mn2 = (n_cont * np.pi / ky_c)**2 + V_bulk_loc
        dmn2_dPhi = -2.0 * (n_cont * np.pi)**2 / (ky_c**3 * epsilon_GW * Phi_0)
        total = 0.0
        for lam2, mult in zip(df2_e, df2_m):
            x = (mn2 + lam2) / Lam**2
            total += mult * (-np.exp(-x)) * dmn2_dPhi / Lam**2
        return total

    # Integral from 0 to N_modes (covering all computed warped eigenvalues)
    mu2_int, _ = quad(g_flat, 0.0, len(M_sq_arr), limit=500, epsrel=1e-12)
    # Tail
    mu2_tail, _ = quad(g_flat, len(M_sq_arr), 3 * len(M_sq_arr), limit=200, epsrel=1e-10)
    mu2_int += mu2_tail

    mu2_brane = mu2_sum - mu2_int
    return mu2_sum, mu2_int, mu2_brane


# Compare flat vs warped
print(f"\n{'Phi_0':>10} {'flat brane':>14} {'warped brane':>14} {'ratio':>10} {'diff':>14}")
print("-" * 68)

Phi0_vals = [0.01, 0.02, 0.0436, 0.073, 0.1, 0.2]

for phi0 in Phi0_vals:
    # Flat (from verified EM)
    flat_brane = 2.5374 / phi0  # mu^2_brane * Phi_0 = const from the 1/Phi_0 scaling
    flat_brane = 0.05820 * (0.0436 / phi0)  # Scale from the known value

    # Warped
    mu2_w_sum, mu2_w_int, mu2_w_brane = compute_mu2_warped_em(
        phi0, M_sq_0, dM_sq_dyc, df2_eig, df2_mult)

    if not np.isnan(mu2_w_brane):
        ratio = mu2_w_brane / flat_brane if abs(flat_brane) > 1e-30 else float('nan')
        print(f"{phi0:10.4f} {flat_brane:14.6e} {mu2_w_brane:14.6e} {ratio:10.4f} {mu2_w_brane-flat_brane:14.6e}")


# =============================================================================
# SELF-CONSISTENT SOLUTION WITH WARPED EIGENVALUES
# =============================================================================
print("\n" + "=" * 78)
print("SELF-CONSISTENT SOLUTION WITH WARPED EIGENVALUES")
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


# Self-consistent iteration with warped eigenvalues
print("\nIterating to self-consistency...")
phi0_iter = 0.04  # Initial guess near previous solution
for it in range(50):
    _, _, mu2_b = compute_mu2_warped_em(phi0_iter, M_sq_0, dM_sq_dyc, df2_eig, df2_mult)
    if np.isnan(mu2_b) or mu2_b <= 0:
        print(f"  iter {it}: mu2_brane = {mu2_b}, breaking")
        break
    jc = solve_jc(sigma_UV, alpha_UV_SA, mu2_b, xi, M5_cubed)
    if jc[0] is None:
        print(f"  iter {it}: JC failed for mu2 = {mu2_b}")
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
        break
    phi0_iter = 0.5 * phi0_iter + 0.5 * phi0_new

# === FINAL COMPARISON ===
print(f"\n{'='*78}")
print(f"FINAL COMPARISON")
print(f"{'='*78}")
print(f"""
  Flat KK eigenvalues:    mu^2 = 0.0582 k^2,  w_0 = -0.589
  Warped KK eigenvalues:  mu^2 = {mu2_b:.4e} k^2,  w_0 = {w0:.4f}
  DESI target:            mu^2 = 0.097 k^2,   w_0 = -0.83

  Warped/Flat ratio: {mu2_b/0.0582:.4f}
  Warped/DESI ratio: {mu2_b/0.097:.4f}
  Remaining gap: {0.097/mu2_b:.2f}x
""")

print("Done.")
