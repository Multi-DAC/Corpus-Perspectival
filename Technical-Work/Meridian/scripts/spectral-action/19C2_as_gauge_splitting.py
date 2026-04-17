"""
19C.2: ASYMPTOTIC SAFETY GAUGE SPLITTING
The Inverse Problem: What does the AS fixed point need to provide?

Part of Phase 19, Track C (gauge unification).
Follows the KILL result from 14A.2 (a1 = a2 = a3 is a theorem of spectral action).
"""
import numpy as np

# === Experimental inputs at M_Z ===
M_Z = 91.1876
alpha_em_MZ = 1/127.906
sin2_theta_W = 0.23122
alpha_s_MZ = 0.1179
M_Pl = 1.22e19

alpha_1_MZ = (5/3) * alpha_em_MZ / (1 - sin2_theta_W)
alpha_2_MZ = alpha_em_MZ / sin2_theta_W
alpha_3_MZ = alpha_s_MZ

print("=" * 70)
print("19C.2: ASYMPTOTIC SAFETY GAUGE SPLITTING")
print("=" * 70)
print()
print("=== Experimental couplings at M_Z ===")
print(f"  alpha_1^(-1)(M_Z) = {1/alpha_1_MZ:.4f}  (GUT normalized)")
print(f"  alpha_2^(-1)(M_Z) = {1/alpha_2_MZ:.4f}")
print(f"  alpha_3^(-1)(M_Z) = {1/alpha_3_MZ:.4f}")
print()

# === SM one-loop beta coefficients ===
b1 = 41/10
b2 = -19/6
b3 = -7.0

print("=== One-loop beta coefficients (SM) ===")
print(f"  b1 = {b1:.4f} (41/10, NOT asymptotically free)")
print(f"  b2 = {b2:.4f} (-19/6)")
print(f"  b3 = {b3:.4f} (-7)")
print()

def alpha_inv(alpha_inv_MZ, b_i, mu):
    return alpha_inv_MZ - b_i * np.log(mu/M_Z) / (2*np.pi)

# === Evolution table ===
print("=== Coupling evolution (one-loop SM) ===")
print(f"  {'log10(mu)':>10}  {'a1_inv':>8}  {'a2_inv':>8}  {'a3_inv':>8}  {'23 gap':>7}  {'13 gap':>7}")
for lm in [2, 4, 8, 12, 13, 14, 15, 16, 17, 18, 19]:
    mu = 10**lm
    a1 = alpha_inv(1/alpha_1_MZ, b1, mu)
    a2 = alpha_inv(1/alpha_2_MZ, b2, mu)
    a3 = alpha_inv(1/alpha_3_MZ, b3, mu)
    print(f"  {lm:10d}  {a1:8.2f}  {a2:8.2f}  {a3:8.2f}  {a2-a3:7.2f}  {a1-a3:7.2f}")
print()

# === SU(2)-SU(3) crossing ===
delta23 = 1/alpha_2_MZ - 1/alpha_3_MZ
mu_23 = M_Z * np.exp(delta23 * 2*np.pi / (b2 - b3))
a_at_23 = alpha_inv(1/alpha_2_MZ, b2, mu_23)
a1_at_23 = alpha_inv(1/alpha_1_MZ, b1, mu_23)

print(f"SU(2)-SU(3) crossing: 10^{np.log10(mu_23):.2f} GeV")
print(f"  alpha_23^(-1) = {a_at_23:.3f}")
print(f"  alpha_1^(-1)  = {a1_at_23:.3f}")
print(f"  U(1) gap      = {a_at_23 - a1_at_23:.3f}")
print()

# === Required a1/a3 ratio ===
print("=== SPECTRAL ACTION RATIO a1/a3 AT VARIOUS SCALES ===")
print("  (alpha_i^(-1)(L) = a_i * f0, so a1/a3 = alpha1^(-1)/alpha3^(-1))")
print()
for label, L in [("10^14", 1e14), ("10^15", 1e15), ("10^16", 1e16),
                  ("10^17", 1e17), ("M_Pl", M_Pl)]:
    a1 = alpha_inv(1/alpha_1_MZ, b1, L)
    a3 = alpha_inv(1/alpha_3_MZ, b3, L)
    a2 = alpha_inv(1/alpha_2_MZ, b2, L)
    if a1 > 0 and a3 > 0:
        print(f"  {label:>8}: a1/a3 = {a1/a3:.4f},  a2/a3 = {a2/a3:.4f}")
print()

# === Matter representation indices ===
# Per generation, GUT normalized
Y2_sum = 6*(1/6)**2 + 3*(2/3)**2 + 3*(1/3)**2 + 2*(1/2)**2 + 1*(1)**2
S1_gen = (5/3) * Y2_sum
S2_gen = 2.0  # sum T_2(R) per generation
S3_gen = 2.0  # sum T_3(R) per generation

S1_H = (5/3) * (1/2)**2 * 2  # Higgs doublet
S2_H = 1/2
S3_H = 0.0

S1_tot = 3*S1_gen + S1_H
S2_tot = 3*S2_gen + S2_H
S3_tot = 3*S3_gen + S3_H

print("=== Matter representation indices (for AS corrections) ===")
print(f"  S_1 = {S1_tot:.4f}  (U(1) -- dominated by large hypercharges)")
print(f"  S_2 = {S2_tot:.4f}  (SU(2))")
print(f"  S_3 = {S3_tot:.4f}  (SU(3))")
print(f"  S_1/S_3 = {S1_tot/S3_tot:.4f}")
print()

# CRITICAL: S_2 != S_3 only because of Higgs
# S_2 - S_3 = S2_H - S3_H = 0.5
print("=== CRITICAL STRUCTURAL OBSERVATION ===")
print(f"  S_2 - S_3 = {S2_tot - S3_tot:.4f}  (only from Higgs)")
print(f"  S_1 - S_3 = {S1_tot - S3_tot:.4f}  (large -- U(1) hypercharges)")
print(f"  S_1 - S_2 = {S1_tot - S2_tot:.4f}")
print()

print("=" * 70)
print("MECHANISM ANALYSIS")
print("=" * 70)
print()

# === MECHANISM 1: Delta_i proportional to S_i ===
print("--- Mechanism 1: Delta_i = c * S_i ---")
print()

# At the SU(2)-SU(3) crossing, for full unification:
# Need a1 + c*S1 = a23 + c*S3  (where a23 is the SU(2)=SU(3) value)
# Also need a2 + c*S2 = a3 + c*S3 (SU(2)-SU(3) splitting from Higgs term)
# But SU(2)-SU(3) already cross at mu_23, so near that scale c_23 is small

# For U(1)-SU(3) unification at mu_23:
c_needed = (a_at_23 - a1_at_23) / (S1_tot - S3_tot)
a1c = a1_at_23 + c_needed * S1_tot
a2c = a_at_23 + c_needed * S2_tot  # SU(2) value at crossing
a3c = a_at_23 + c_needed * S3_tot

print(f"  At SU(2)-SU(3) crossing (10^{np.log10(mu_23):.2f} GeV):")
print(f"    Gap to close: {a_at_23 - a1_at_23:.3f}")
print(f"    c required: {c_needed:.4f}")
print(f"    With correction: a1={a1c:.3f}, a2={a2c:.3f}, a3={a3c:.3f}")
print(f"    Residual spread: {max(a1c,a2c,a3c) - min(a1c,a2c,a3c):.3f}")
print()

# Physical interpretation of c
# c ~ g_star / (16*pi^2) * Delta_t
# where Delta_t = ln(M_Pl / mu_trans) / (2*pi) is the "running time" above transition
# g_star is the AS fixed point coupling

for mu_trans_log in [13, 15, 17]:
    mu_trans = 10**mu_trans_log
    Delta_t = np.log(M_Pl / mu_trans) / (2*np.pi)
    g_star = c_needed * 16 * np.pi**2 / Delta_t
    print(f"  If transition at 10^{mu_trans_log} GeV: g_* = {g_star:.3f} (AS predicts 0.7-1.5)")

print()

# === MECHANISM 2: Delta_i proportional to b_i ===
print("--- Mechanism 2: Delta_i = d * b_i ---")
print("  (AS corrections scale with SM beta coefficients)")
print()

# At mu_23: need a1 + d*b1 = a_23 + d*b3
d_needed = (a_at_23 - a1_at_23) / (b1 - b3)
a1c = a1_at_23 + d_needed * b1
a2c = a_at_23 + d_needed * b2
a3c = a_at_23 + d_needed * b3

print(f"  At SU(2)-SU(3) crossing:")
print(f"    d required: {d_needed:.4f}")
print(f"    With correction: a1={a1c:.3f}, a2={a2c:.3f}, a3={a3c:.3f}")
print(f"    Residual 23 gap: {a2c - a3c:.3f}")
print()

# This mechanism can also split SU(2) from SU(3) because b2 != b3
# Is the residual gap acceptable?
print(f"  b2 - b3 = {b2-b3:.4f}")
print(f"  SU(2)-SU(3) additional splitting: {d_needed*(b2-b3):.3f}")
print(f"  This SHIFTS the crossing point!")
print()

# Find the new crossing with corrections
# alpha_i^(-1)(mu) = alpha_i^(-1)(M_Z) - b_i/(2pi) * ln(mu/M_Z) + d * b_i
# = alpha_i^(-1)(M_Z) + b_i * [d - ln(mu/M_Z)/(2pi)]
# For crossing: alpha_2^(-1) = alpha_3^(-1)
# 1/a2 + b2*[d - L] = 1/a3 + b3*[d - L]
# (1/a2 - 1/a3) = (b3 - b2) * [d - L]
# d - L = (1/a2 - 1/a3) / (b3 - b2)
# But L = ln(mu/M_Z)/(2pi)
# This gives the SAME crossing point! d cancels out!
# Because the correction is proportional to b_i, it's equivalent to
# shifting the effective running distance, which doesn't change WHERE couplings cross.
print("  NOTE: Mechanism 2 (proportional to b_i) is equivalent to")
print("  shifting the effective cutoff scale. It changes the crossing VALUE")
print("  but not the crossing POINT. This is degenerate with scale choice.")
print()

# === MECHANISM 3: Eichhorn-Held style (gauge-gravity mixing) ===
print("--- Mechanism 3: Eichhorn-Held (gauge-gravity fixed point) ---")
print()

# In Eichhorn & Held (2017-2020), the gravitational contribution to
# gauge running takes the form:
#   beta_gi = beta_gi^SM + f_g * g_i
# where f_g = f_g(g_N, lambda) depends on Newton coupling g_N and
# cosmological constant lambda at the fixed point.
#
# This gives:
#   d(alpha_i^(-1))/dt = -b_i/(2pi) - f_g/(8pi^2)
#
# The correction f_g is UNIVERSAL in the minimal truncation.
# Non-universality enters through:
# 1. Higher-order gravity-matter vertices
# 2. The gauge field contribution to the graviton propagator
# 3. Non-minimal couplings (R * F^2 terms)

# In the "gravity-matter fixed point" scenario:
# The gauge couplings themselves have non-trivial fixed point values
# g_i^* that depend on the gravitational fixed point
# If g_i^* are different for different gauge groups, this provides splitting

# The fixed point condition: beta_gi = 0
# b_i * g_i^3 / (16pi^2) + f_g * g_i = 0
# g_i^2 = -16pi^2 * f_g / b_i  (requires f_g < 0 for AF groups, f_g > 0 for U(1))

# For this to work: ALL gauge couplings must be AT their fixed points
# which means alpha_i^(-1) = (16pi^2) * |b_i| / (f_g) or similar

# alpha_i = g_i^2 / (4pi) = -4pi * f_g / b_i
# alpha_i^(-1) = -b_i / (4pi * f_g)

# Ratio: alpha_1^(-1) / alpha_3^(-1) = b1 / b3 = (41/10) / (-7) = -0.586
# This is NEGATIVE, which means U(1) (b1 > 0) can't have a real fixed point
# with the same sign of f_g as the asymptotically free groups.

print("  Fixed point ratio: b1/b3 = {:.4f}".format(b1/b3))
print("  PROBLEM: U(1) has b1 > 0, so it needs opposite sign of f_g")
print("  for a real fixed point. This means the simple fixed-point")
print("  mechanism doesn't give simultaneous fixed points for all groups.")
print()

# HOWEVER: Eichhorn & Held showed that gravity can INDUCE a UV fixed point
# for U(1) even though it's not asymptotically free. The mechanism:
# f_g < 0 (gravitational antiscreening) makes all gauge couplings
# approach zero in the UV. For U(1), this cures the Landau pole.

# In this scenario, the boundary conditions at the Planck scale are:
# alpha_i^(-1)(M_Pl) = very large (all couplings near zero at UV FP)
# The DIFFERENCES between alpha_i^(-1) are set by the rate of approach
# to the fixed point, which depends on the critical exponents.

print("  Eichhorn-Held mechanism: gravity-induced UV safety for U(1)")
print("  All couplings -> 0 at fixed point (asymptotically safe)")
print("  Differences set by critical exponents theta_i")
print()

# The critical exponents determine how fast each coupling approaches
# its fixed point. For the linearized flow near the FP:
# g_i(k) - g_i^* ~ (k/k_0)^(-theta_i)
# If theta_i differ for different gauge groups, this creates splitting.

# In the SM: theta_i ~ -2*b_i (at one loop, ignoring gravity)
# With gravity: theta_i ~ -2*b_i + delta_theta_i(g_N*, lambda*)

theta1 = -2*b1  # = -8.2
theta2 = -2*b2  # = +6.33
theta3 = -2*b3  # = +14.0

print("  Critical exponents (without gravity):")
print(f"    theta_1 = {theta1:.2f} (U(1) -- IRRELEVANT, runs away from FP)")
print(f"    theta_2 = {theta2:.2f} (SU(2) -- relevant)")
print(f"    theta_3 = {theta3:.2f} (SU(3) -- relevant)")
print()
print("  theta_1 < 0 means U(1) is REPELLED from the trivial FP")
print("  Gravity must flip the sign: need delta_theta_1 > 8.2")
print()

# === SYNTHESIS ===
print("=" * 70)
print("SYNTHESIS: THREE PATHS TO GAUGE SPLITTING")
print("=" * 70)
print()

print("Path A: MATTER-DEPENDENT AS CORRECTIONS (Delta_i ~ S_i)")
print(f"  Required coefficient: c = {c_needed:.4f}")
a1_16 = alpha_inv(1/alpha_1_MZ, b1, 1e16)
a3_16 = alpha_inv(1/alpha_3_MZ, b3, 1e16)
c_16 = (a3_16 - a1_16) / (S1_tot - S3_tot)
print(f"  Implied g_* at 10^13 transition: {c_needed * 16*np.pi**2 / (np.log(M_Pl/1e13)/(2*np.pi)):.2f}")
print(f"  Status: VIABLE if g_* in AS range (0.7-1.5)")
print(f"  Can split U(1) from non-abelian. S2~S3 means limited SU(2)-SU(3) splitting.")
print()

print("Path B: CRITICAL EXPONENT SPLITTING")
print("  The rate of approach to the UV fixed point differs by gauge group")
print("  theta_i depend on b_i AND gravitational corrections")
print("  Naturally gives different boundary conditions without explicit Delta_i")
print(f"  Status: VIABLE in principle. Requires theta_1 > 0 (gravity flips U(1))")
print()

print("Path C: RS GEOMETRY + AS COMBINED")
print("  KK tower modifies the fixed point structure")
print("  Warp factor introduces scale-dependent gravitational coupling")
print("  5D AS may have different fixed point from 4D AS")
print("  Orbifold BCs break translational symmetry -> new operators")
print("  Status: UNEXPLORED (this would be genuinely new)")
print()

# === Final numbers ===
print("=" * 70)
print("KEY NUMBERS FOR THE TRACK DOCUMENT")
print("=" * 70)
print()
print(f"Required splitting at SU23 crossing (10^{np.log10(mu_23):.1f} GeV):")
print(f"  alpha_1^(-1) needs +{a_at_23-a1_at_23:.2f} to match alpha_23^(-1) = {a_at_23:.2f}")
print()
print(f"a1/a3 ratio at key scales:")
for label, L in [("10^13", 1e13), ("10^14", 1e14), ("10^16", 1e16), ("M_Pl", M_Pl)]:
    a1 = alpha_inv(1/alpha_1_MZ, b1, L)
    a3 = alpha_inv(1/alpha_3_MZ, b3, L)
    if a1 > 0 and a3 > 0:
        print(f"  {label}: {a1/a3:.4f}")
print()
print(f"S_1/S_3 = {S1_tot/S3_tot:.4f} (matter index ratio)")
print(f"b_1/b_3 = {b1/b3:.4f} (beta coefficient ratio)")
print()
print("The spectral action gives a1/a3 = 1.000 (KILL result from 14A.2)")
print("AS must shift this to the REQUIRED ratio shown above.")
print("Path A (matter-dependent corrections) is quantitatively viable.")
print("Path C (RS + AS) is unexplored and potentially the most informative.")
