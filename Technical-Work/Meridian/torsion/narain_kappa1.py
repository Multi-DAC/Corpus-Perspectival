"""
Narain Lattice Computation: kappa_1
====================================
The Wilson line deformation coefficient.
Determines v from the gap: v^2 = |delta_z| / kappa_1

Strategy:
  1. Compute the gauge threshold as a function of the continuous Wilson line phi
  2. Add the blow-up anomaly polynomial contribution (proportional to v^2)
  3. Find how the minimum shifts -> kappa_1

Key simplifications:
  - V . W1 = 0 (shift orthogonal to Wilson line)
  - P_hol(W1) = 0 (Wilson line invisible to holonomy)
  - At tau = omega, the Narain sum reduces to theta functions

Phase 22, Track alpha — FINAL COMPUTATION
2026-03-25
"""

import numpy as np
from itertools import combinations
from mpmath import (mp, mpf, mpc, pi, sqrt, log, exp, jtheta, diff,
                    findroot, fabs, nstr, gamma, re as mpre)

mp.dps = 50

print("=" * 70)
print("NARAIN LATTICE: kappa_1 (Wilson line deformation coefficient)")
print("=" * 70)

# === E8 ROOT SYSTEM ===
e8_roots = []
for i, j in combinations(range(8), 2):
    for si in [1, -1]:
        for sj in [1, -1]:
            r = np.zeros(8); r[i] = si; r[j] = sj
            e8_roots.append(r)
for bits in range(256):
    signs = np.array([(-1 if (bits >> i) & 1 else 1) for i in range(8)])
    if np.sum(signs < 0) % 2 == 0:
        e8_roots.append(signs * 0.5)
e8_roots = np.array(e8_roots)
assert len(e8_roots) == 240

# === VECTORS ===
V = np.array([0, 0, 0, 0, 0, 2/3, -1/3, -1/3])
W1_dir = np.array([1, 1, -2, 0, 0, 0, 0, 0])  # Wilson line DIRECTION

# SU(3) factor simple roots
factors = {
    'C': (np.array([1,-1,0,0,0,0,0,0]), np.array([0,1,-1,0,0,0,0,0])),
    'A': (np.array([0,0,0,1,1,0,0,0]), np.array([0.5,0.5,0.5,-0.5,-0.5,0.5,0.5,0.5])),
    'B': (np.array([0,0,0,1,-1,0,0,0]), np.array([0.5,0.5,0.5,-0.5,0.5,-0.5,-0.5,-0.5])),
    'hol': (np.array([0,0,0,0,0,1,-1,0]), np.array([0,0,0,0,0,0,1,-1])),
}

def proj_sq(vec, s1, s2):
    """Squared projection of vec onto SU(3) root space spanned by s1, s2."""
    d1 = np.dot(vec, s1); d2 = np.dot(vec, s2)
    g11 = np.dot(s1,s1); g12 = np.dot(s1,s2); g22 = np.dot(s2,s2)
    det = g11*g22 - g12**2
    c1 = (g22*d1 - g12*d2)/det
    c2 = (g11*d2 - g12*d1)/det
    return c1*d1 + c2*d2  # = |proj|^2

def DKL_a(Veff, factor_name):
    """DKL trace for gauge factor a: sum_alpha (Veff.alpha)^2 |P_a(alpha)|^2"""
    s1, s2 = factors[factor_name]
    return sum(np.dot(Veff, alpha)**2 * proj_sq(alpha, s1, s2) for alpha in e8_roots)


# === VERIFY ORTHOGONALITY ===
print("\n--- Orthogonality Checks ---")
print(f"V . W1_dir = {np.dot(V, W1_dir):.10f} (should be 0)")
print(f"|P_hol(W1_dir)|^2 = {proj_sq(W1_dir, *factors['hol']):.10f} (should be 0)")
print(f"|P_C(W1_dir)|^2 = {proj_sq(W1_dir, *factors['C']):.6f}")
print(f"|P_A(W1_dir)|^2 = {proj_sq(W1_dir, *factors['A']):.10f} (should be 0)")
print(f"|P_B(W1_dir)|^2 = {proj_sq(W1_dir, *factors['B']):.10f} (should be 0)")


# === STEP 1: DKL TRACES AS FUNCTION OF phi ===
print("\n--- Step 1: DKL Traces vs Wilson Line ---")
print()

phi_orb = 1.0/3  # orbifold value
dphi = 0.001  # step for numerical derivatives

# Compute DKL for each (n1, phi, factor)
def total_DKL_sum(phi):
    """Sum of DKL_C + DKL_A + DKL_B over all 27 fixed points at Wilson line phi."""
    total = 0
    for n1 in [0, 1, 2]:
        Veff = V + n1 * phi * W1_dir
        for a in ['C', 'A', 'B']:
            total += 9 * DKL_a(Veff, a)  # 9 fps per class
    return total

def DKL_diff_CA(phi):
    """Sum of (DKL_C - DKL_A) over all 27 fixed points."""
    total = 0
    for n1 in [0, 1, 2]:
        Veff = V + n1 * phi * W1_dir
        total += 9 * (DKL_a(Veff, 'C') - DKL_a(Veff, 'A'))
    return total

# Table: DKL values at orbifold
print("DKL traces at phi = 1/3 (orbifold point):")
print(f"{'n1':>3} | {'DKL_C':>10} | {'DKL_A':>10} | {'DKL_B':>10} | {'DKL_hol':>10} | {'C-A':>8}")
print("-" * 65)
for n1 in [0, 1, 2]:
    Veff = V + n1 * phi_orb * W1_dir
    vals = {a: DKL_a(Veff, a) for a in ['C', 'A', 'B', 'hol']}
    print(f"{n1:3d} | {vals['C']:10.4f} | {vals['A']:10.4f} | {vals['B']:10.4f} | {vals['hol']:10.4f} | {vals['C']-vals['A']:8.4f}")

print(f"\nTotal DKL_sum at phi=1/3: {total_DKL_sum(phi_orb):.4f}")
print(f"Total C-A at phi=1/3: {DKL_diff_CA(phi_orb):.4f}")


# === STEP 2: NUMERICAL DERIVATIVES ===
print("\n--- Step 2: Derivatives w.r.t. z ---")

# z = (5/6) * phi, so dz = (5/6) dphi, d/dz = (6/5) d/dphi
z_factor = 5.0/6  # dz/dphi

# d(DKL_sum)/dphi at phi = 1/3
dDKL_sum_dphi = (total_DKL_sum(phi_orb + dphi) - total_DKL_sum(phi_orb - dphi)) / (2*dphi)
d2DKL_sum_dphi2 = (total_DKL_sum(phi_orb + dphi) - 2*total_DKL_sum(phi_orb) + total_DKL_sum(phi_orb - dphi)) / dphi**2

# Convert to z derivatives
dDKL_sum_dz = dDKL_sum_dphi / z_factor  # d/dz = (1/z_factor) d/dphi
d2DKL_sum_dz2 = d2DKL_sum_dphi2 / z_factor**2

print(f"d(DKL_C+A+B)/dz at z=5/18:   {dDKL_sum_dz:.6f}")
print(f"d^2(DKL_C+A+B)/dz^2:         {d2DKL_sum_dz2:.4f}")

# d(DKL_C - DKL_A)/dphi
dDKL_CA_dphi = (DKL_diff_CA(phi_orb + dphi) - DKL_diff_CA(phi_orb - dphi)) / (2*dphi)
dDKL_CA_dz = dDKL_CA_dphi / z_factor
print(f"\nd(DKL_C - DKL_A)/dz at z=5/18: {dDKL_CA_dz:.6f}")


# === STEP 3: ANALYTICAL CHECK ===
print("\n--- Step 3: Analytical Cross-Check ---")

# From the DKL decomposition theorem:
# DKL_a(n1, phi) = 24[|V + n1*phi*W1_dir|^2 + |P_a(V + n1*phi*W1_dir)|^2]
# d/dphi = 24[2(V+n1*phi*W) . (n1*W) + 2 P_a(V+n1*phi*W) . P_a(n1*W)]
# At phi=1/3: Veff = V + n1/3 * W1_dir

# V.W1_dir = 0, so Veff.W1_dir = n1*phi*|W1_dir|^2 = n1*(1/3)*6 = 2*n1
# d(|Veff|^2)/dphi = 2*Veff.(n1*W1_dir) = 2*n1*(2*n1) = 4*n1^2

# For the sum C+A+B: need d/dphi of sum_a P_a(Veff).P_a(n1*W1_dir)
# Using P_C(W1_dir) = 6, P_A(W1_dir) = 0, P_B(W1_dir) = 0, P_hol(W1_dir) = 0

# P_C(Veff).P_C(n1*W1_dir):
# P_C(Veff) = P_C(V) + n1*phi*P_C(W1_dir)
# P_C(V): V is entirely in hol subspace, so P_C(V) = 0 if C and hol are orthogonal
# Check:
PC_V = proj_sq(V, *factors['C'])
PA_V = proj_sq(V, *factors['A'])
PB_V = proj_sq(V, *factors['B'])
Phol_V = proj_sq(V, *factors['hol'])
print(f"|P_C(V)|^2 = {PC_V:.10f} (should be ~0)")
print(f"|P_A(V)|^2 = {PA_V:.10f}")
print(f"|P_B(V)|^2 = {PB_V:.10f}")
print(f"|P_hol(V)|^2 = {Phol_V:.6f}")
print(f"Sum = {PC_V + PA_V + PB_V + Phol_V:.6f} vs |V|^2 = {np.dot(V,V):.6f}")

# Projection of W1_dir onto each factor
PCW = proj_sq(W1_dir, *factors['C'])
PAW = proj_sq(W1_dir, *factors['A'])
PBW = proj_sq(W1_dir, *factors['B'])
PholW = proj_sq(W1_dir, *factors['hol'])
print(f"\n|P_C(W1_dir)|^2 = {PCW:.6f}")
print(f"|P_A(W1_dir)|^2 = {PAW:.10f}")
print(f"|P_B(W1_dir)|^2 = {PBW:.10f}")
print(f"|P_hol(W1_dir)|^2 = {PholW:.10f}")
print(f"Sum = {PCW + PAW + PBW + PholW:.6f} vs |W1_dir|^2 = {np.dot(W1_dir,W1_dir):.6f}")


# === STEP 4: THE THRESHOLD AS A FUNCTION OF z AND v ===
print("\n--- Step 4: Combined Potential V(z, v) ---")

# The one-loop gauge threshold for factor a:
# Delta_a(z, v) = Delta_a^orb(z) + delta_Delta_a(z, v)
#
# The orbifold threshold depends on z through theta functions.
# The blow-up threshold depends on z through the DKL traces.
#
# For the ANOMALY POLYNOMIAL contribution (proportional to v^2):
# delta_Delta_a^anom = (c_2 / 8pi^2) * v^2 * sum_i DKL_a(i, z) / Tr_norm
#
# With c_2 = -6 and Tr_norm = the trace normalization.
#
# The potential V(z, v) = sum_a w_a * Delta_a(z, v)
# For equal-weight trinification: w_C = w_A = w_B = w
#
# Minimum in z:
# dV/dz = w * [d(Delta_C + Delta_A + Delta_B)/dz] = 0
# = w * [d(orbifold)/dz + v^2 * d(anomaly)/dz] = 0
#
# At v=0: d(orbifold)/dz = 0 at z = 5/18 (by discrete symmetry)
#
# For small v:
# delta_z = -v^2 * [d(anomaly sum)/dz] / [d^2(orbifold sum)/dz^2]

# The orbifold potential curvature (from theta functions)
omega = mpc(-1, sqrt(3)) / 2
q_omega = exp(mpc(0, 1) * pi * omega)
z_tree = mpf(5) / 18
target_theta = log(mpf(3)) / sqrt(mpf(2))
gamma_13 = gamma(mpf(1) / 3)
eta_abs = mpf(3) ** (mpf(1) / 8) * gamma_13 ** (mpf(3) / 2) / (2 * pi)

def theta1_abs(z):
    return fabs(jtheta(1, pi * z, q_omega))

def f_DKL(z):
    """f(z) = ln|theta_1(pi*z, q)/eta|^2"""
    return 2 * log(theta1_abs(z) / eta_abs)

# The orbifold threshold for the trinification:
# Delta_C^orb(z) = Delta_A^orb(z) = Delta_B^orb(z) = universal + f(z) * coeff
# For the Z3 model, the non-universal threshold involves f(z) at specific z values.
#
# From track_c_dkl.py: the threshold difference Delta_3 - Delta_2 involves
# f(5/18) and f(5/9). For the TRINIFICATION, the relevant z values are
# determined by the Wilson line sectors.
#
# At the orbifold: all three trinification factors get the SAME threshold
# (S3 symmetry). The z-dependent part is:
# Delta_a^NU(phi) = sum_{n1} 9 * f_a(n1, phi)
# where f_a involves the DKL-weighted theta functions.
#
# For the EQUAL-WEIGHT trinification potential:
# V^orb(phi) proportional to sum_a Delta_a(phi) = 3 * Delta_any(phi)
# The curvature: d^2V^orb/dz^2 proportional to d^2f/dz^2 * (representation coefficient)

d2f_dz2 = float(diff(f_DKL, z_tree, 2))
df_dz = float(diff(f_DKL, z_tree))

print(f"Theta function derivatives at z = 5/18:")
print(f"  df/dz = {df_dz:.8f}")
print(f"  d^2f/dz^2 = {d2f_dz2:.6f}")


# === STEP 5: COMPUTE kappa_1 ===
print("\n--- Step 5: kappa_1 ---")

# The anomaly contribution coefficient:
# delta_Delta_a^anom(z, v) = (6 / 8pi^2) * v^2 * sum_{n1} 9 * DKL_a(n1, z) / Tr_norm
#
# Tr_norm: the normalization of the DKL trace.
# For E8 with 240 roots: sum_alpha |alpha|^2 = 240 * 2 = 480
# For a single SU(3): sum_alpha |P_a(alpha)|^2 = 120 (verified numerically)
# Use Tr_norm = 120 (consistent with DKL convention)

Tr_norm = sum(proj_sq(alpha, *factors['C']) for alpha in e8_roots)
print(f"Tr_norm (SU(3)_C) = {Tr_norm:.4f}")

# The anomaly coefficient for factor a at fixed point class n1:
# gamma_a(n1, phi) = (6 / (8*pi^2 * Tr_norm)) * DKL_a(n1, phi)

# The potential tilt from blow-up:
# d(gamma_C + gamma_A + gamma_B)/dphi = (6 / (8*pi^2*Tr_norm)) * d(DKL_sum)/dphi

coeff_anomaly = 6.0 / (8 * np.pi**2 * Tr_norm)
print(f"Anomaly coefficient: 6/(8*pi^2*Tr_norm) = {coeff_anomaly:.8f}")

# Numerator of kappa_1 (in phi):
# -d(gamma_sum)/dphi = -coeff_anomaly * d(DKL_sum)/dphi
numerator_phi = -coeff_anomaly * dDKL_sum_dphi

# Denominator of kappa_1 (in phi):
# d^2(V_orb_sum)/dphi^2
# The orbifold threshold sum Delta_C + Delta_A + Delta_B depends on phi
# through the theta functions. Since all three are equal at the orbifold:
# d^2(3*Delta_a)/dphi^2 = 3 * d^2(Delta_a)/dphi^2
#
# Delta_a depends on phi through the Narain lattice at tau = omega.
# The non-universal threshold: Delta_a^NU = sum_sectors f(z_sector(phi))
# For the Z3 model with Wilson line, the sectors give:
#   z_sector = n1 * phi * (5/6)  [hypercharge times Wilson line]
#   contribution = 9 * f(z_sector) for each n1 class
#
# Wait - this is the STANDARD MODEL threshold, not the trinification.
# For the trinification, all three factors get the SAME threshold (S3).
# So Delta_C(phi) = Delta_A(phi) = Delta_B(phi) = Delta_any(phi).
#
# Delta_any(phi) involves f at the hypercharge-weighted z values.
# But for the trinification, the "hypercharge" is different.
#
# In fact, the trinification threshold depends on phi through the
# FULL Narain lattice sum at tau = omega.
#
# Key insight: the Narain lattice sum at tau = omega gives the threshold
# as a sum over E8 lattice points. The phi dependence comes through V_eff.
# We can compute the FULL phi-dependent threshold from the partition function.

# Let me compute the partition function approach.
# The gauge-dependent part of the threshold at tau = omega:
# Z_a(omega; phi) = sum_alpha (V_eff.alpha)^2 * |P_a(alpha)|^2 * |q|^{|alpha+V_eff|^2}

# Wait, this isn't quite right. The partition function involves the full
# lattice sum, not just the root contribution. But the dominant contribution
# at tau = omega (where |q| ~ 0.066) comes from the lightest states.

# Let me compute the FULL lattice sum including exponential weights.

q_abs = float(fabs(exp(mpc(0, 1) * pi * omega)))  # |q| = exp(-pi*sqrt(3)/2)
print(f"\n|q_omega| = {q_abs:.8f}")
print(f"|q|^2 = {q_abs**2:.8f}")

def narain_threshold_sum(phi, factor_name):
    """
    Compute the gauge-dependent Narain lattice sum at tau = omega
    for the trinification factor 'factor_name', summed over all 27 fps.

    This is: sum_{n1=0,1,2} 9 * sum_{alpha in E8}
             (V_eff.alpha)^2 * |P_a(alpha)|^2 * q_abs^{|alpha|^2}

    (Note: |alpha|^2 = 2 for all E8 roots, so the q-weighting is the same
    for all roots. The exponential factor is just q_abs^2 for all roots.)

    For the THRESHOLD INTEGRAL, we need the difference from the massless contribution.
    But for the PHI DEPENDENCE, the massless contribution is phi-independent,
    so it drops out of derivatives.
    """
    s1, s2 = factors[factor_name]
    total = 0.0
    for n1 in [0, 1, 2]:
        Veff = V + n1 * phi * W1_dir
        for alpha in e8_roots:
            VdotA = np.dot(Veff, alpha)
            PsqA = proj_sq(alpha, s1, s2)
            # Weight by q^{|alpha + Veff|^2 - 2/3} for twisted sector
            # or q^{|alpha + Veff|^2} for untwisted
            # For the root contribution: all roots have |alpha|^2 = 2
            # The Veff shift changes the mass: |alpha + Veff|^2
            mass_sq = np.dot(alpha + Veff, alpha + Veff)
            weight = q_abs ** mass_sq
            total += 9 * VdotA**2 * PsqA * weight
    return total

def narain_total(phi):
    """Sum over C, A, B of the Narain threshold."""
    return sum(narain_threshold_sum(phi, a) for a in ['C', 'A', 'B'])

# Compute at orbifold and nearby points
Z_orb = narain_total(phi_orb)
Z_plus = narain_total(phi_orb + dphi)
Z_minus = narain_total(phi_orb - dphi)

dZ_dphi = (Z_plus - Z_minus) / (2 * dphi)
d2Z_dphi2 = (Z_plus - 2*Z_orb + Z_minus) / dphi**2

dZ_dz = dZ_dphi / z_factor
d2Z_dz2 = d2Z_dphi2 / z_factor**2

print(f"\nNarain lattice sum at phi = 1/3:")
print(f"  Z(phi=1/3) = {Z_orb:.8f}")
print(f"  dZ/dz = {dZ_dz:.8f}")
print(f"  d^2Z/dz^2 = {d2Z_dz2:.6f}")

# Now compute the FULL kappa_1
# delta_z = -v^2 * [coeff * dDKL_sum/dz] / [d^2Z/dz^2]
#
# But actually, we should use the NARAIN-WEIGHTED derivative in the denominator too.
# The potential curvature comes from the Narain sum, not just f(z).

print("\n--- KAPPA_1 COMPUTATION ---")
print()

# Method 1: Using DKL derivatives (analytical) for numerator, Narain for denominator
# Numerator: d(anomaly contribution to potential)/dz
# = coeff_anomaly * d(DKL_C + DKL_A + DKL_B)/dz
anom_tilt = coeff_anomaly * dDKL_sum_dz
print(f"Anomaly tilt: coeff * d(DKL_sum)/dz = {anom_tilt:.8f}")

# Denominator: d^2(Narain threshold)/dz^2
# This is the curvature of the orbifold potential
print(f"Potential curvature: d^2Z/dz^2 = {d2Z_dz2:.6f}")

# kappa_1 = -anom_tilt / d2Z_dz2
kappa_1_method1 = -anom_tilt / d2Z_dz2
print(f"\nkappa_1 (Method 1) = {kappa_1_method1:.8f}")

# Method 2: Use pure Narain sums for BOTH numerator and denominator
# The numerator is the MIXED derivative d^2Z/dz dv^2
# The denominator is d^2Z/dz^2
# These should give the same ratio if the DKL trace correctly captures
# the v^2 anomaly contribution.

# Method 3: Direct perturbation
# Compute Z(phi + delta_phi, v) - Z(phi, v) directly
# where the v-dependence enters through the mass correction
# m^2 -> m^2 + v^2 * (blow-up mass)^2

# For the blow-up modes, the mass correction is:
# delta(m^2) = v^2 * |c_2| * |P_a(V_eff)|^2 / normalization
# This modifies the q-weighting: q^{m^2} -> q^{m^2 + delta_m^2}

# The v-dependent Narain sum:
def narain_with_blowup(phi, v_sq, factor_name):
    """Narain sum including blow-up mass correction."""
    s1, s2 = factors[factor_name]
    total = 0.0
    for n1 in [0, 1, 2]:
        Veff = V + n1 * phi * W1_dir
        VeffSq = np.dot(Veff, Veff)
        # Blow-up mass correction for this fixed point class
        # delta_m^2 proportional to v^2 * DKL_a / normalization
        # Using the anomaly formula: delta_m^2 = 6 * v^2 * |P_a(Veff)|^2 / (8*pi^2)
        Peff_sq = proj_sq(Veff, s1, s2)
        blowup_mass = 6.0 * v_sq * (VeffSq + Peff_sq) / (8 * np.pi**2)

        for alpha in e8_roots:
            VdotA = np.dot(Veff, alpha)
            PsqA = proj_sq(alpha, s1, s2)
            mass_sq = np.dot(alpha + Veff, alpha + Veff)
            # Include blow-up mass shift
            eff_mass = mass_sq + blowup_mass
            weight = q_abs ** eff_mass
            total += 9 * VdotA**2 * PsqA * weight
    return total

def narain_total_blowup(phi, v_sq):
    """Sum over C, A, B including blow-up."""
    return sum(narain_with_blowup(phi, v_sq, a) for a in ['C', 'A', 'B'])

# Find the minimum of the potential as a function of phi at various v^2
print("\n--- Step 6: z_eff(v) by Numerical Minimization ---")
print()
print(f"{'v^2':>10} | {'phi_min':>12} | {'z_eff':>12} | {'delta_z':>12} | {'kappa_1_eff':>12}")
print("-" * 70)

z_tree_float = 5.0/18

from scipy.optimize import minimize_scalar

for v_sq in [0.0, 0.001, 0.005, 0.01, 0.02, 0.05, 0.10, 0.20]:
    # Find phi that minimizes the Narain sum
    def neg_potential(phi):
        return -narain_total_blowup(phi, v_sq)  # minimize = find min of -Z

    # Actually, the threshold potential is minimized when the lattice sum is maximized
    # (heavier states = lower coupling = deeper potential well)
    # OR: the true moduli potential depends on details we don't have.
    # Let's instead track WHERE the maximum of the lattice sum is.

    result = minimize_scalar(neg_potential, bounds=(0.25, 0.40), method='bounded')
    phi_min = result.x
    z_min = phi_min * z_factor
    delta_z_v = z_min - z_tree_float
    kappa_eff = delta_z_v / v_sq if v_sq > 0 else float('nan')

    print(f"{v_sq:10.4f} | {phi_min:12.8f} | {z_min:12.8f} | {delta_z_v:12.8f} | {kappa_eff:12.6f}")

# Read off kappa_1 from the v^2 -> 0 limit
print()
print("kappa_1 = lim_{v^2 -> 0} delta_z / v^2")
print("Read from table above (small v^2 rows)")


# === STEP 7: PHYSICAL RESULT ===
print("\n--- Step 7: Physical Result ---")

# Required: delta_z = -0.000698
delta_z_required = -0.000698

# From table, extract kappa_1 at small v^2
# Compute at very small v^2
v_sq_small = 0.001
result_small = minimize_scalar(lambda phi: -narain_total_blowup(phi, v_sq_small),
                                bounds=(0.25, 0.40), method='bounded')
delta_z_small = result_small.x * z_factor - z_tree_float
kappa_1_numerical = delta_z_small / v_sq_small

print(f"kappa_1 (numerical, v^2=0.001) = {kappa_1_numerical:.8f}")
print(f"kappa_1 (analytical, Method 1)  = {kappa_1_method1:.8f}")

if abs(kappa_1_numerical) > 1e-10:
    v_sq_physical = abs(delta_z_required / kappa_1_numerical)
    v_physical = np.sqrt(v_sq_physical)
    print(f"\nRequired delta_z = {delta_z_required}")
    print(f"v^2 = |delta_z| / |kappa_1| = {v_sq_physical:.6f}")
    print(f"v = {v_physical:.6f} = {v_physical*100:.2f}% of compactification scale")

    # C-A split at this v
    CA_split = DKL_diff_CA(phi_orb) * coeff_anomaly * v_sq_physical
    print(f"\nPredicted C-A coupling split: delta(1/g_C^2 - 1/g_A^2) = {CA_split:.8f}")
else:
    print(f"\nkappa_1 ~ 0: blow-up does not shift Wilson line in this model!")
    print("The gap closure must come from a DIFFERENT mechanism.")
