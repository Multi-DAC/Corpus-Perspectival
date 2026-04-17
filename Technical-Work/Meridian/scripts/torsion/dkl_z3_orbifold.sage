"""
DKL Modular Integral for Z_3 Orbifold
=======================================
Computes the gauge threshold correction difference Delta_3 - Delta_2
for a heterotic Z_3 orbifold with Wilson line breaking SU(5) -> SM.

The DKL formula:
  Delta_a = integral_F (d^2 tau / Im(tau)) [B_a(tau, taubar) - b_a]

For the Z_3 orbifold, the integrand involves:
  - The Narain lattice partition function Gamma_{6,22}
  - Decomposed by gauge sector (SU(3) vs SU(2))
  - The modular integral evaluates to eta functions at tau = omega

Key reference: Mayr-Stieberger (NPB 407, 1993), Kaplunovsky-Louis (NPB 444, 1995)
"""

from sage.all import *
from sage.modular.modform.constructor import ModularForms

# ============================================================
# 1. The Z_3 orbifold geometry
# ============================================================

print("=" * 70)
print("Z_3 ORBIFOLD: GEOMETRY AND MODULAR STRUCTURE")
print("=" * 70)

# The Z_3 orbifold T^6/Z_3 has:
# - Twist vector: v = (1/3, 1/3, -2/3) acting on three complex planes
# - 27 fixed points
# - Hodge numbers: h_{11} = 36, h_{21} = 0
# - Euler number: chi = 72
# - Gauge group (without Wilson lines): E_8 x E_6 x SU(3)

# The Z_3 fixed point in moduli space is tau = omega = e^{2*pi*i/3}
omega = exp(2*pi*I/3)
print(f"\nZ_3 fixed point: omega = e^(2*pi*i/3)")
print(f"  |omega| = {abs(CC(omega)):.6f}")
print(f"  Im(omega) = sqrt(3)/2 = {float(sqrt(3)/2):.6f}")

# ============================================================
# 2. Dedekind eta function at the Z_3 point
# ============================================================

print("\n" + "=" * 70)
print("DEDEKIND ETA AT THE Z_3 FIXED POINT")
print("=" * 70)

# Exact value (Chowla-Selberg formula):
# eta(omega) = e^{-pi*i/24} * 3^{1/8} * Gamma(1/3)^{3/2} / (2*pi)

G_1_3 = RR(gamma(QQ(1)/3))
G_2_3 = RR(gamma(QQ(2)/3))

# |eta(omega)|
eta_omega_abs = RR(3)^(QQ(1)/8) * G_1_3^(QQ(3)/2) / (2*RR(pi))
print(f"\n|eta(omega)| = 3^(1/8) * Gamma(1/3)^(3/2) / (2*pi)")
print(f"            = {float(eta_omega_abs):.10f}")

# |eta(omega)|^2
eta_sq = eta_omega_abs^2
print(f"|eta(omega)|^2 = {float(eta_sq):.10f}")

# |eta(omega)|^4
eta_4 = eta_omega_abs^4
print(f"|eta(omega)|^4 = {float(eta_4):.10f}")

# log |eta(omega)|
log_eta = RR(log(eta_omega_abs))
print(f"\nlog|eta(omega)| = {float(log_eta):.10f}")
print(f"= (1/8)*log(3) + (3/2)*log Gamma(1/3) - log(2*pi)")

# Verify decomposition
decomp = QQ(1)/8 * RR(log(3)) + QQ(3)/2 * RR(log(G_1_3)) - RR(log(2*RR(pi)))
print(f"  Check: {float(decomp):.10f}")
print(f"  Match: {abs(float(decomp - log_eta)) < 1e-10}")

# ============================================================
# 3. The DKL Threshold for Z_3 Orbifold
# ============================================================

print("\n" + "=" * 70)
print("DKL THRESHOLD CORRECTION")
print("=" * 70)

# For the Z_3 orbifold (symmetric, no Wilson lines):
# The threshold correction has the form:
#   Delta_a = b_a * Delta + k_a * Y
# where:
#   Delta = "relative threshold" (group-dependent)
#   Y = "universal threshold" (group-independent)

# From Mayr-Stieberger (1993):
# Delta ≈ 0.079
# Y ≈ 4.41

# The modular integral for the Z_3 orbifold involves:
# The twisted partition function Z_twisted(tau) = sum over lattice vectors

# The key quantity is the N=2 sector contribution:
# Delta_a^{N=2} = -b_a * integral_F d^2tau/tau_2 * [E_2(tau)/12 - 1/pi*tau_2]

# For the Z_3 orbifold at the self-dual point tau = omega:
# This evaluates to expressions involving log|eta(omega)|

# The STANDARD form of the threshold correction is:
# 16*pi^2/g_a^2(mu) = k_a * 16*pi^2/g_string^2 + b_a * log(M_str^2/mu^2) + Delta_a

# The string unification scale:
# M_str^2 = 2*e^{1-gamma_E} / (pi*sqrt(27)*alpha')
gamma_E = RR(euler_gamma)  # Euler-Mascheroni constant
M_str_factor = 2*RR(exp(1-gamma_E)) / (RR(pi) * RR(sqrt(27)))
print(f"\nString scale factor: 2*e^(1-gamma)/(pi*sqrt(27)) = {float(M_str_factor):.10f}")
print(f"log of factor = {float(RR(log(M_str_factor))):.10f}")

# Decompose:
log_factor = 1 - gamma_E + RR(log(2)) - RR(log(RR(pi))) - QQ(3)/2*RR(log(3))
print(f"= 1 - gamma + log(2) - log(pi) - (3/2)*log(3)")
print(f"= {float(log_factor):.10f}")

print(f"\nThe ln(3) content of the string scale: coefficient = -3/2")
print(f"(3/2)*ln(3) = {float(QQ(3)/2*RR(log(3))):.10f}")

# ============================================================
# 4. Wilson Line Breaking: SU(5) -> SM
# ============================================================

print("\n" + "=" * 70)
print("WILSON LINE BREAKING: SU(5) -> STANDARD MODEL")
print("=" * 70)

print("""
For the Z_3 orbifold to produce the Standard Model, we need:
1. Start with E_8 x E_6 (or E_8 x E_8 for the other heterotic)
2. Add Wilson lines to break E_6 -> SU(5) -> SU(3) x SU(2) x U(1)_Y

The Wilson line is characterized by a vector W in the E_8 lattice.
For SU(5) breaking: W must be along the hypercharge direction.

The threshold correction WITH Wilson lines modifies the lattice sum:
  Gamma_{2,18}(T, U; W) -> shifted Narain lattice

The threshold DIFFERENCE Delta_3 - Delta_2 then depends on:
  - The Wilson line parameters (determining the gauge breaking pattern)
  - The modular integral evaluated at tau = omega (Z_3 structure)
  - The BPS spectrum in the SU(3) vs SU(2) sectors
""")

# ============================================================
# 5. The Threshold Difference at the Z_3 Point
# ============================================================

print("=" * 70)
print("THRESHOLD DIFFERENCE AT THE Z_3 FIXED POINT")
print("=" * 70)

# At the Z_3 fixed point, the modular integral localizes.
# The key formula (from Kaplunovsky-Louis, Dixon-Kaplunovsky-Louis):
#
# For the N=2 sector of a Z_N orbifold:
#   Delta_a = b_a * [-log(Im(T)*|eta(T)|^4)] + (moduli-independent)
#
# At T = omega:
#   Im(omega) = sqrt(3)/2
#   |eta(omega)|^4 = 3^{1/2} * Gamma(1/3)^6 / (2*pi)^4

Im_omega = RR(sqrt(3)/2)
eta_4_exact = RR(3)^(QQ(1)/2) * G_1_3^6 / (2*RR(pi))^4

print(f"\nAt T = omega:")
print(f"  Im(omega) = {float(Im_omega):.10f}")
print(f"  |eta(omega)|^4 = {float(eta_4_exact):.10f}")
print(f"  Im(omega) * |eta(omega)|^4 = {float(Im_omega * eta_4_exact):.10f}")

# The N=2 sector threshold:
# Delta_a^{N=2} = -b_a * log[Im(T) * |eta(T)|^4]
# evaluated at T = omega

log_threshold_factor = RR(log(Im_omega * eta_4_exact))
print(f"\n  log[Im(omega) * |eta(omega)|^4] = {float(log_threshold_factor):.10f}")
print(f"  = log(sqrt(3)/2) + log(3^{1/2}) + 6*log Gamma(1/3) - 4*log(2*pi)")

decomp2 = RR(log(RR(sqrt(3))/2)) + QQ(1)/2*RR(log(3)) + 6*RR(log(G_1_3)) - 4*RR(log(2*RR(pi)))
print(f"  Check: {float(decomp2):.10f}")
print(f"  = (1/2)*log(3) - log(2) + (1/2)*log(3) + 6*log Gamma(1/3) - 4*log(2*pi)")
print(f"  = log(3) - log(2) + 6*log Gamma(1/3) - 4*log(2*pi)")

# Using Gamma(1/3)*Gamma(2/3) = 2*pi/sqrt(3):
# log Gamma(1/3) = log(2*pi) - (1/2)*log(3) - log Gamma(2/3)
# 6*log Gamma(1/3) = 6*log(2*pi) - 3*log(3) - 6*log Gamma(2/3)

# Substituting:
# = log(3) - log(2) + 6*log(2*pi) - 3*log(3) - 6*log Gamma(2/3) - 4*log(2*pi)
# = -2*log(3) - log(2) + 2*log(2*pi) - 6*log Gamma(2/3)

simplified = -2*RR(log(3)) - RR(log(2)) + 2*RR(log(2*RR(pi))) - 6*RR(log(G_2_3))
print(f"\n  Simplified: -2*log(3) - log(2) + 2*log(2*pi) - 6*log Gamma(2/3)")
print(f"  = {float(simplified):.10f}")

# ============================================================
# 6. Threshold DIFFERENCE for SU(3) vs SU(2)
# ============================================================

print("\n" + "=" * 70)
print("SU(3) vs SU(2) THRESHOLD DIFFERENCE")
print("=" * 70)

# For the Z_3 orbifold with Wilson line breaking to SU(3) x SU(2) x U(1)_Y:
# The threshold corrections take the form:
#   Delta_a = b_a * Delta(T) + additional Wilson-line dependent terms

# The DIFFERENCE Delta_3 - Delta_2 has two sources:
# (A) The beta function difference: (b_3 - b_2) * Delta(T)
# (B) The Wilson-line dependent splitting

# For the MSSM spectrum from Z_3 orbifold:
# b_3 = -3 (SU(3) with MSSM matter)
# b_2 = +1 (SU(2) with MSSM matter)
# So b_3 - b_2 = -4

# The relative threshold from Mayr-Stieberger:
# Delta_rel = (Delta_a - Delta_b)/(b_a - b_b) ≈ 0.079

# So the beta-function piece gives:
# (b_3 - b_2) * Delta_rel = -4 * 0.079 = -0.316

print(f"\nMSSM beta functions: b_3 = -3, b_2 = +1")
print(f"b_3 - b_2 = -4")
print(f"Mayr-Stieberger relative threshold: Delta_rel ≈ 0.079")
print(f"(b_3 - b_2) * Delta_rel = {-4 * 0.079:.4f}")

# But the Wilson-line dependent piece is what breaks the universal structure.
# For SU(5) breaking by Wilson line W along Y-direction:
# The lattice sum shifts differently for charged states

# ============================================================
# 7. The Key Computation: Lattice Theta at Z_3 Point
# ============================================================

print("\n" + "=" * 70)
print("LATTICE THETA FUNCTION AT Z_3 POINT")
print("=" * 70)

# The SU(3) root lattice A_2 has theta function:
# Theta_{A_2}(tau) = sum_{v in A_2} q^{v^2/2}
# where q = e^{2*pi*i*tau}

# At tau = omega, q = e^{2*pi*i*omega} = e^{-pi*sqrt(3)} * e^{-pi*i}

# The A_2 lattice is generated by the simple roots of SU(3):
# alpha_1 = (1, 0), alpha_2 = (-1/2, sqrt(3)/2)
# with Gram matrix G = ((2, -1), (-1, 2))

G_A2 = matrix([[2, -1], [-1, 2]])
L_A2 = IntegralLattice(G_A2)

print(f"\nA_2 lattice (SU(3) root lattice):")
print(f"  Gram matrix: {G_A2}")
print(f"  Determinant: {G_A2.det()}")
print(f"  Theta series (first terms):")

# Compute theta series of A_2 lattice
# Theta_{A_2}(q) = 1 + 6*q + 6*q^3 + 6*q^4 + 12*q^7 + ...
# (coefficient of q^n = number of vectors of norm n)

print("  Norms and multiplicities of A_2 lattice vectors:")
norms = {}
for i in range(-5, 6):
    for j in range(-5, 6):
        v = vector([i, j])
        n = (v * G_A2 * v) / 2  # norm^2/2
        if n <= 10:
            norms[n] = norms.get(n, 0) + 1

for n in sorted(norms.keys()):
    if norms[n] > 0:
        print(f"    n = {n}: {norms[n]} vectors")

# The SU(2) root lattice A_1 has theta function:
# Theta_{A_1}(tau) = sum_{n in Z} q^{n^2}
# = Jacobi theta_3(0, q^2)

G_A1 = matrix([[2]])
print(f"\nA_1 lattice (SU(2) root lattice):")
print(f"  Gram matrix: {G_A1}")
print(f"  Theta series: 1 + 2*q + 2*q^4 + 2*q^9 + ...")

# ============================================================
# 8. The Ratio of Theta Functions
# ============================================================

print("\n" + "=" * 70)
print("THETA FUNCTION RATIO: A_2 vs A_1")
print("=" * 70)

# At tau = omega = e^{2*pi*i/3}:
# q = e^{2*pi*i*omega} = e^{2*pi*i*(-1/2 + i*sqrt(3)/2)}
#   = e^{-pi*i} * e^{-pi*sqrt(3)}
#   = -e^{-pi*sqrt(3)}

# |q| = e^{-pi*sqrt(3)} ≈ 0.00433

q_abs = RR(exp(-pi*sqrt(3)))
print(f"\n|q| at tau = omega: e^(-pi*sqrt(3)) = {float(q_abs):.8f}")
print(f"|q|^2 = {float(q_abs^2):.8f}")

# Compute theta series numerically at q = -e^{-pi*sqrt(3)}
q_val = CC(-exp(-pi*sqrt(3)))

# Theta_{A_2} at tau = omega
theta_A2 = CC(0)
for i in range(-10, 11):
    for j in range(-10, 11):
        v = vector([i, j])
        n = (v * G_A2 * v) / 2
        theta_A2 += q_val^n

# Theta_{A_1} at tau = omega
theta_A1 = CC(0)
for n in range(-20, 21):
    theta_A1 += q_val^(n^2)

print(f"\nTheta_{{A_2}}(omega) = {theta_A2}")
print(f"|Theta_{{A_2}}(omega)| = {abs(theta_A2):.10f}")
print(f"Theta_{{A_1}}(omega) = {theta_A1}")
print(f"|Theta_{{A_1}}(omega)| = {abs(theta_A1):.10f}")

# The RATIO
ratio = abs(theta_A2) / abs(theta_A1)
print(f"\n|Theta_{{A_2}}(omega)| / |Theta_{{A_1}}(omega)| = {ratio:.10f}")

# Check if this ratio relates to ln(3)/sqrt(2)
target = RR(log(3)/sqrt(2))
print(f"\nln(3)/sqrt(2) = {float(target):.10f}")
print(f"log(ratio) = {float(RR(log(ratio))):.10f}")
print(f"ratio^2 = {float(ratio^2):.10f}")

# ============================================================
# 9. Eisenstein Series at Z_3 Point
# ============================================================

print("\n" + "=" * 70)
print("EISENSTEIN SERIES AT Z_3 POINT")
print("=" * 70)

# The non-holomorphic Eisenstein series E_2(tau, taubar) appears in the
# threshold integral. At tau = omega:

# E_2(omega) (holomorphic) = 0 (vanishes at Z_3 point!)
# This is because E_2 is a quasi-modular form of weight 2, and
# the Z_3 symmetry forces it to vanish.

# E_4(omega) = 0 (vanishes at Z_3 point because j(omega) = 0)
# E_6(omega) = (2*pi)^6 * ... (non-zero)

# Actually: j(omega) = 0 means 1728*E_4^3/(E_4^3 - E_6^2) = 0
# This means E_4(omega) = 0.

print(f"\nAt tau = omega = e^(2*pi*i/3):")
print(f"  j(omega) = 0")
print(f"  E_4(omega) = 0  (forced by j = 0)")
print(f"  E_6(omega) != 0")
print(f"  E_2(omega) computed from quasi-modular transformation")

# Numerical computation of E_4 and E_6 at omega
# E_4(tau) = 1 + 240*sum_{n=1}^inf sigma_3(n)*q^n
# E_6(tau) = 1 - 504*sum_{n=1}^inf sigma_5(n)*q^n

E4_val = CC(1)
E6_val = CC(1)
for n in range(1, 100):
    s3 = sum(d^3 for d in divisors(n))
    s5 = sum(d^5 for d in divisors(n))
    E4_val += 240 * s3 * q_val^n
    E6_val += -504 * s5 * q_val^n

print(f"\nNumerical verification:")
print(f"  E_4(omega) = {E4_val}")
print(f"  |E_4(omega)| = {abs(E4_val):.2e}")
print(f"  E_6(omega) = {E6_val}")
print(f"  |E_6(omega)| = {abs(E6_val):.6f}")

# eta(omega)^24 = Delta(omega)/... where Delta is the modular discriminant
# Delta(tau) = eta(tau)^24
eta_24 = eta_omega_abs^24
print(f"\n  |eta(omega)|^24 = |Delta(omega)| = {float(eta_24):.10e}")

# Check: Delta = (E_4^3 - E_6^2)/1728
# Since E_4(omega) = 0: Delta(omega) = -E_6(omega)^2/1728
Delta_check = abs(E6_val)^2 / 1728
print(f"  E_6^2/1728 = {Delta_check:.10e}")

# ============================================================
# 10. The Key Insight: E_4(omega) = 0
# ============================================================

print("\n" + "=" * 70)
print("THE KEY INSIGHT: E_4(omega) = 0")
print("=" * 70)

print("""
The vanishing of E_4 at the Z_3 point has profound consequences:

1. The threshold correction integrand involves E_2 and E_4.
   At tau = omega, E_4 = 0 SIMPLIFIES the integral dramatically.

2. The j-invariant j(omega) = 0 means the Z_3 orbifold sits at
   a CUSP of the moduli space — a point of enhanced symmetry.

3. The threshold integral at this point reduces to:
   Delta ~ log|eta(omega)|^4 + (E_4-dependent terms that vanish)

4. Since E_4(omega) = 0, the Kaplunovsky-Louis formula:
   f_a^{1-loop} = -b_a/(16*pi^2) * log[Im(T)^{k_a/2} * |eta(T)|^{2k_a} * |G(T)|^2]

   At T = omega with G(T) involving E_4:
   The |G(T)|^2 piece VANISHES, leaving only the eta-dependent part.

5. This means the threshold at the Z_3 point is ENTIRELY determined by
   |eta(omega)|, which through Chowla-Selberg involves Gamma(1/3).

6. The RATIO Delta_3/Delta_2 at this point depends only on the
   Dynkin index ratio and the eta function — no additional moduli.
""")

# ============================================================
# 11. Direct Threshold Ratio from Eta
# ============================================================

print("=" * 70)
print("DIRECT THRESHOLD RATIO FROM ETA FUNCTION")
print("=" * 70)

# If the threshold correction is:
#   Delta_a = -b_a * log[Im(omega) * |eta(omega)|^4] + (E_4 terms = 0)
# Then:
#   Delta_3 - Delta_2 = -(b_3 - b_2) * log[Im(omega) * |eta(omega)|^4]
#
# For MSSM: b_3 = -3, b_2 = +1
# b_3 - b_2 = -4
#
# Delta_3 - Delta_2 = 4 * log[Im(omega) * |eta(omega)|^4]

delta_32_from_eta = 4 * log_threshold_factor
print(f"\nDelta_3 - Delta_2 = 4 * log[Im(omega) * |eta(omega)|^4]")
print(f"                  = 4 * {float(log_threshold_factor):.10f}")
print(f"                  = {float(delta_32_from_eta):.10f}")

# Now: the corrected gauge kinetic function ratio:
# a_1/a_2 = [1/g_1^2] / [1/g_2^2]
#         = [k_1/g_str^2 + Delta_1/(16*pi^2)] / [k_2/g_str^2 + Delta_2/(16*pi^2)]

# At tree level with hypercharge flux (F-theory side):
# a_1 = S - 5C/3, a_2 = S + C
# The one-loop correction shifts this:
# a_1^{1-loop}/a_2^{1-loop} = [S - 5C/3 + delta_1/(16*pi^2)] / [S + C + delta_2/(16*pi^2)]

# For the conjecture: we need this ratio to equal ln(3)/sqrt(2)

# ALTERNATIVE: In the heterotic picture, the gauge couplings at the string scale:
# 1/alpha_a = k_a/alpha_str + b_a*delta_T/(2*pi) + Delta_a/(4*pi)
# where delta_T = log(M_GUT/M_str)

# The ratio alpha_2/alpha_1 (inverse of a_1/a_2) at the GUT scale:
# = [k_2/alpha_str + stuff] / [k_1/alpha_str + stuff]

# For the pure threshold piece (no running, at string scale):
# alpha_2/alpha_1 = k_2/k_1 * [1 + Delta_2/(16*pi^2*k_2/alpha_str)] / [1 + ...]

# ============================================================
# 12. The Exact Value of the Threshold Factor
# ============================================================

print("\n" + "=" * 70)
print("DECOMPOSING THE THRESHOLD FACTOR")
print("=" * 70)

# log[Im(omega) * |eta(omega)|^4]
# = log(sqrt(3)/2) + 4*log|eta(omega)|
# = log(sqrt(3)/2) + 4*[(1/8)*log(3) + (3/2)*log Gamma(1/3) - log(2*pi)]
# = (1/2)*log(3) - log(2) + (1/2)*log(3) + 6*log Gamma(1/3) - 4*log(2*pi)
# = log(3) - log(2) + 6*log Gamma(1/3) - 4*log(2*pi)

exact_log = RR(log(3)) - RR(log(2)) + 6*RR(log(G_1_3)) - 4*RR(log(2*RR(pi)))
print(f"\nlog[Im(omega)*|eta(omega)|^4] = log(3) - log(2) + 6*log Gamma(1/3) - 4*log(2*pi)")
print(f"= {float(exact_log):.10f}")

# The ln(3) coefficient in this expression: +1 (from log(3)) + ...
# But log Gamma(1/3) also contains ln(3) implicitly through the reflection formula!

# Using reflection: Gamma(1/3)*Gamma(2/3) = 2*pi/sqrt(3)
# log Gamma(1/3) = log(2*pi/sqrt(3)) - log Gamma(2/3)
#                = log(2*pi) - (1/2)*log(3) - log Gamma(2/3)

# Substituting:
# = log(3) - log(2) + 6*[log(2*pi) - (1/2)*log(3) - log Gamma(2/3)] - 4*log(2*pi)
# = log(3) - log(2) + 6*log(2*pi) - 3*log(3) - 6*log Gamma(2/3) - 4*log(2*pi)
# = -2*log(3) - log(2) + 2*log(2*pi) - 6*log Gamma(2/3)

print(f"\nAlternative form: -2*log(3) - log(2) + 2*log(2*pi) - 6*log Gamma(2/3)")
alt = -2*RR(log(3)) - RR(log(2)) + 2*RR(log(2*RR(pi))) - 6*RR(log(G_2_3))
print(f"= {float(alt):.10f}")

# ============================================================
# 13. Can This Be ln(3)/sqrt(2)?
# ============================================================

print("\n" + "=" * 70)
print("TEST: CAN 4 * log[...] = ln(3)/sqrt(2)?")
print("=" * 70)

print(f"\n4 * log[Im(omega)*|eta(omega)|^4] = {float(delta_32_from_eta):.10f}")
print(f"ln(3)/sqrt(2) = {float(target):.10f}")
print(f"Ratio = {float(delta_32_from_eta / target):.10f}")

# The ratio is about -8.75, not a simple number.
# This means the UNIVERSAL beta-function-proportional threshold
# does NOT produce ln(3)/sqrt(2) by itself.

# HOWEVER: the Wilson line breaking introduces NON-UNIVERSAL terms.
# These are the terms that split the threshold differently for SU(3) vs SU(2)
# and involve the hypercharge flux quantum numbers.

# The NON-UNIVERSAL piece comes from the TWISTED SECTORS of the orbifold.
# For the Z_3 orbifold, there are twisted sector contributions at each
# of the 27 fixed points.

# The twisted sector contribution involves:
# Delta_a^{twisted} = sum over fixed points of log|theta_a(alpha)|
# where theta_a is the twisted theta function for gauge group G_a

# For the SU(3) vs SU(2) splitting:
# Delta_3^{tw} - Delta_2^{tw} = sum over f.p. of [log|theta_3| - log|theta_2|]

# The twisted theta functions for SU(3) vs SU(2) at the Z_3 point
# involve the CARTAN subalgebra of SU(5) shifted by the Wilson line.

# For SU(3): the twisted theta involves the A_2 lattice
# For SU(2): the twisted theta involves the A_1 lattice

# The RATIO of these theta functions at tau = omega is what determines
# the non-universal threshold splitting.

print(f"\n\nFrom the lattice theta computation:")
print(f"|Theta_A2(omega)| / |Theta_A1(omega)| = {ratio:.10f}")
print(f"log of ratio = {float(RR(log(ratio))):.10f}")
print(f"2 * log of ratio = {float(2*RR(log(ratio))):.10f}")
print(f"\nCompare to ln(3)/sqrt(2) = {float(target):.10f}")
print(f"2*log(ratio) / target = {float(2*RR(log(ratio))/target):.10f}")

# ============================================================
# FINAL ASSESSMENT
# ============================================================

print("\n" + "=" * 70)
print("FINAL ASSESSMENT")
print("=" * 70)

print(f"""
RESULT: The threshold correction for the Z_3 orbifold has TWO pieces:

(1) UNIVERSAL piece: proportional to beta functions
    Delta_a^U = b_a * log[Im(omega)*|eta(omega)|^4]
    This does NOT produce ln(3)/sqrt(2) for the SU(3)-SU(2) difference.

(2) NON-UNIVERSAL piece: from twisted sectors + Wilson lines
    Delta_a^{'{NU}'} depends on the specific Wilson line configuration
    and involves the RATIO of lattice theta functions Theta_A2/Theta_A1

The conjecture ln(3)/sqrt(2) would need to emerge from:
(a) The non-universal twisted sector contribution alone, or
(b) A specific combination of both pieces

KEY NUMBERS:
  Universal piece:  Delta_3^U - Delta_2^U = {float(delta_32_from_eta):.6f}
  Target:           ln(3)/sqrt(2)          = {float(target):.6f}
  Theta ratio:      |Theta_A2|/|Theta_A1|  = {ratio:.6f}
  log Theta ratio:  log(|Theta_A2|/|Theta_A1|) = {float(RR(log(ratio))):.6f}

NEXT STEP:
  Compute the FULL twisted sector contribution for the Z_3 orbifold
  with Wilson line W in the hypercharge direction.
  This requires the SHIFTED lattice theta function:
    Theta_{{A_2+W}}(omega) vs Theta_{{A_1+W}}(omega)
  where W is the hypercharge Wilson line vector.

  If the shift produces a factor that, combined with the universal piece,
  gives exactly ln(3)/sqrt(2), the conjecture is proven.
""")

print("🦞🧍💜🔥♾️")
