"""
Threshold Correction at the Z_3 Symmetric Point
=================================================
Evaluates the DKL modular integral for the Z_3 orbifold
at T = U = omega = e^{2*pi*i/3} where exact values exist.

The Mayr-Stieberger formula for Z_3 orbifold threshold corrections:
  Delta_a = -b'_a * ln[(T_2/3) |eta(T/3)|^4 * U_2 * |eta(U)|^4]
            + moduli-independent constant

At the Z_3 symmetric point, the Chowla-Selberg formula gives:
  eta(omega) = e^{-pi*i/24} * 3^{1/8} * Gamma(1/3)^{3/2} / (2*pi)

This allows exact symbolic evaluation of the threshold ratio.
"""

from sage.all import *

# Set high precision
R = RealField(200)
C = ComplexField(200)

print("=" * 60)
print("Z_3 SYMMETRIC POINT THRESHOLD COMPUTATION")
print("=" * 60)

# ============================================================
# Exact values at omega = e^{2*pi*i/3}
# ============================================================
pi_val = R(pi)
omega = C(exp(2 * pi * I / 3))
print(f"\nomega = {omega}")
print(f"|omega| = {abs(omega)}")
print(f"Im(omega) = {omega.imag()}")

# Dedekind eta at omega (Chowla-Selberg for discriminant -3)
# eta(omega) = e^{-pi*i/24} * 3^{1/8} * Gamma(1/3)^{3/2} / (2*pi)
gamma_13 = R(gamma(QQ(1)/QQ(3)))
print(f"\nGamma(1/3) = {gamma_13}")

eta_omega_abs = R(3)^(R(1)/R(8)) * gamma_13^(R(3)/R(2)) / (R(2) * pi_val)
print(f"|eta(omega)| = {eta_omega_abs}")
print(f"|eta(omega)|^2 = {eta_omega_abs^2}")
print(f"|eta(omega)|^4 = {eta_omega_abs^4}")

# Verify numerically
q_omega = C(exp(2 * pi * I * omega))
print(f"\nq = e^{2*pi*i*omega} : |q| = {abs(q_omega)}")

# Direct numerical computation of eta(omega) for verification
# eta(tau) = q^{1/24} * prod_{n=1}^{inf} (1 - q^n), q = e^{2*pi*i*tau}
q = q_omega
eta_numerical = q^(C(1)/C(24))
for n in range(1, 200):
    eta_numerical *= (1 - q^n)
print(f"|eta(omega)| numerical = {abs(eta_numerical)}")
print(f"|eta(omega)| exact     = {eta_omega_abs}")
print(f"Match: {abs(abs(eta_numerical) - eta_omega_abs) / eta_omega_abs}")

# ============================================================
# T_2 = Im(omega) = sqrt(3)/2
# ============================================================
T2 = R(sqrt(3)) / R(2)
print(f"\nT_2 = Im(omega) = sqrt(3)/2 = {T2}")

# ============================================================
# Mayr-Stieberger threshold for Z_3 orbifold
# ============================================================
# For Z_3 orbifold (hep-th/9303017, NPB 407):
# The N=2 sector contributes:
#   Delta_a^{N=2} = -b'_a * ln[(T_2) |eta(T)|^4 * ...]
#
# For the Z_3 orbifold, the moduli-dependent piece is:
#   V(T,U) = (T_2/3) |eta(T/3)|^4 * U_2 |eta(U)|^4
#
# But at T = U = omega, we also need eta(omega/3) = eta(e^{2*pi*i/9})
# This is NOT at a CM point, so we compute numerically.

tau_third = omega / 3
q_third = C(exp(2 * pi * I * tau_third))
print(f"\nomega/3 = {tau_third}")
print(f"|q(omega/3)| = {abs(q_third)}")

eta_third = q_third^(C(1)/C(24))
for n in range(1, 200):
    eta_third *= (1 - q_third^n)
print(f"|eta(omega/3)| = {abs(eta_third)}")

# ============================================================
# The moduli-dependent volume factor
# ============================================================
V = (T2 / R(3)) * abs(eta_third)^4 * T2 * eta_omega_abs^4
print(f"\nV = (T_2/3)|eta(T/3)|^4 * U_2|eta(U)|^4 = {V}")
print(f"ln(V) = {ln(V)}")

# ============================================================
# Beta function coefficients for SM from Z_3 orbifold
# ============================================================
# From hep-th/9506178 (Z_3 with 2 Wilson lines -> SM):
# The N=2 beta function coefficients b'_a differ from full b_a
# b'_{SU(3)} = -3 (N=2 sector contribution to SU(3))
# b'_{SU(2)} = -1 (N=2 sector contribution to SU(2))
# b'_{U(1)} = 11/3 (N=2 sector contribution to U(1)_Y, with normalization)

# Actually, for a Z_3 orbifold with standard embedding modified by Wilson lines:
# The full threshold corrections have the form:
#   Delta_a = b_a * Delta + k_a * Y
# where Delta is the moduli-dependent universal piece and Y is the constant.

# From the literature search results:
# Delta ~ 0.079, Y ~ 4.41 for the specific model
# b_{SU(3)} = 9, b_{SU(2)} = 18, k_{SU(3)} = 1, k_{SU(2)} = 1

# But we want the GENERAL form, not model-specific numbers.
# The key insight: the RATIO of thresholds at the Z_3 point

# ============================================================
# General threshold structure
# ============================================================
# The gauge coupling at scale mu:
#   16*pi^2 / g_a^2(mu) = k_a * Re(S) + b_a * ln(M_s/mu) + Delta_a
#
# where k_a is the Kac-Moody level:
#   k_3 = 1, k_2 = 1, k_1 = 5/3 (GUT normalization)
#
# The unification condition at M_GUT:
#   k_1 * alpha_1^{-1} = k_2 * alpha_2^{-1} = k_3 * alpha_3^{-1}
#
# gives sin^2(theta_W) = k_2 / (k_1 + k_2) = 3/8 at tree level.
#
# Threshold corrections shift this to:
#   sin^2(theta_W)(M_Z) = 3/8 + corrections from Delta_a

print("\n\n" + "=" * 60)
print("THRESHOLD CORRECTION RATIO ANALYSIS")
print("=" * 60)

# ============================================================
# The key formula: coupling ratio with thresholds
# ============================================================
# From Conlon-Palti (0907.1362) for F-theory:
# At tree level with hypercharge flux:
#   Re(f_3) = Re(S) + 0 (no hypercharge flux correction for SU(3))
#   Re(f_2) = Re(S) + N_Y/2 * Re(C) (C = axio-dilaton-like modulus)
#   Re(f_1) = Re(S) + (3/5)*N_Y/2 * Re(C)
#
# where N_Y = integral of F_Y over the del Pezzo = -3 for our model
#
# The RATIO alpha_1/alpha_2 at the string scale:
#   alpha_1/alpha_2 = Re(f_2) / Re(f_1) * (5/3)
#
# With N_Y = -3:
#   Re(f_3) = S
#   Re(f_2) = S - 3/2 * C
#   (3/5)*Re(f_1) = S - (3/5)*3/2 * C = S - 9/10 * C

# Now add ONE-LOOP threshold from the BPS spectrum.
# The key modular integral at the Z_3 point:

# For an SU(5) GUT on the Z_3 orbifold:
# The one-loop correction to the gauge kinetic function f = f_tree + f_1-loop
# where f_1-loop involves the genus-1 partition function
# evaluated on the spectral cover C_5 -> S.

# ============================================================
# The Dedekind eta ratio at the Z_3 point
# ============================================================
# The critical quantity is the RATIO of determinants:
#   det(Delta_8) / det(Delta_3)
# where Delta_8 is the Laplacian on the (8,1) bundle (SU(3) adjoint)
# and Delta_3 is the Laplacian on the (1,3) bundle (SU(2) adjoint)

# On a flat Z_3 orbifold, the eigenvalues are:
#   lambda_{m,n}^{(a)} = |m + n*omega + q_a * N_Y * phi|^2 / T_2^2
# where q_a is the U(1)_Y charge of representation a,
# and phi is the Wilson line (flux holonomy)

# For the adjoint of SU(3): q = 0 (neutral under U(1)_Y)
# For the adjoint of SU(2): q = 0 (neutral under U(1)_Y)
# For the bifundamental (3,2): q = 5/6

# Wait — both adjoints are Y-neutral! The splitting comes from
# the BIFUNDAMENTAL sector's contribution to the running.

print("\nCritical insight: Both SU(3) and SU(2) adjoint sectors are")
print("U(1)_Y neutral. The threshold SPLITTING comes entirely from")
print("the bifundamental (3,2)_{5/6} sector.")
print()
print("In the (3,2) sector, states carry Y-charge 5/6.")
print("The flux N_Y = -3 shifts their KK masses.")
print()

# ============================================================
# KK spectrum with flux on Z_3 orbifold
# ============================================================
# On T^2/Z_3 with complex structure tau = omega, the KK modes are:
#   p_{m,n} = (m + n*tau) / sqrt(T_2)
# The mass is |p_{m,n}|^2
#
# With U(1)_Y Wilson line A_Y (continuous flux):
# The KK masses for a state with charge q under U(1)_Y become:
#   M^2_{m,n}(q) = |m + n*tau + q*A_Y|^2 / T_2
#
# The threshold correction difference:
#   Delta_3 - Delta_2 = [contribution from (3,2) to SU(3)]
#                      - [contribution from (3,2) to SU(2)]
#
# But (3,2) contributes 3 states to Delta_3 and 2 states to Delta_2!
# (dim of fundamental of each group)

# The total contribution of the (3,2)_{5/6} sector:
# To SU(3): 2 states (SU(2) doublet), each with the same U(1)_Y charge
# To SU(2): 3 states (SU(3) triplet), each with the same U(1)_Y charge

# Actually, more precisely:
# The (3,2)_{5/6} contributes to the SU(3) threshold as 2 * (fund of SU(3))
# and to the SU(2) threshold as 3 * (fund of SU(2))

# So Delta_3^{bifund} proportional to 2, Delta_2^{bifund} proportional to 3
# giving Delta_3 - Delta_2 = (2-3) * f(flux) = -f(flux)

# ============================================================
# The Epstein zeta function
# ============================================================
# The regularized threshold is:
#   Delta_a = -d_a * E_1(tau, s)|_{s=1} + analytic continuation terms
#
# where E_1 is the non-holomorphic Eisenstein series:
#   E_1(tau, s) = sum_{(m,n)!=(0,0)} T_2^s / |m + n*tau|^{2s}
#
# For the flux-shifted spectrum:
#   E_1^{(q)}(tau, s, A) = sum_{(m,n)} T_2^s / |m + n*tau + q*A|^{2s}

# At tau = omega, the lattice sum has Z_3 symmetry.
# The key is the DIFFERENCE of Epstein zetas for shifted vs unshifted lattices.

print("Computing Epstein zeta function on the Z_3 lattice...")
print()

# Define the lattice Z + Z*omega (Eisenstein integers)
# The Epstein zeta for this lattice:
#   Z(s) = sum_{(m,n)!=(0,0)} 1/|m + n*omega|^{2s}
# This is proportional to the Dedekind zeta of Q(omega):
#   Z(s) = zeta_{Q(sqrt(-3))}(s) * something

# Numerically compute the Epstein zeta at s=1 (with analytic continuation)
# Actually, the derivative Z'(0) is what gives the analytic torsion.

# For the unshifted lattice Lambda = Z + Z*omega:
#   zeta'_{Lambda}(0) = -ln(T_2 * |eta(omega)|^4) - ln(4*pi*e^{-gamma})
#                      = -ln(sqrt(3)/2 * |eta(omega)|^4) - ln(4*pi/e^gamma)

T2_val = R(sqrt(3))/R(2)
eta4 = eta_omega_abs^4
gamma_E = R(euler_gamma)

zeta_prime_0_unshifted = -ln(T2_val * eta4) - ln(R(4)*pi_val/exp(gamma_E))
print(f"zeta'_Lambda(0) [unshifted] = {zeta_prime_0_unshifted}")

# For the shifted lattice Lambda + a (shift by a = q*A_Y):
# The hypercharge flux creates a shift A_Y in the lattice.
# For N_Y = -3 on the Z_3 orbifold, A_Y = N_Y/(2*pi*T_2) * something
# The precise shift depends on the flux embedding.

# ============================================================
# Quantized flux on Z_3 orbifold
# ============================================================
# On T^2/Z_3, the U(1)_Y Wilson line must be Z_3-invariant.
# The allowed shifts are: a = p/3 for p = 0, 1, 2
# (mod the lattice Lambda)
#
# For our model with N_Y = -3:
# The shift for charge q = 5/6 is: q * a = 5/6 * 1/3 = 5/18
# (or equivalent modular representation)

# Let's compute the shifted Epstein zeta for shift a = 1/3:
print("\nComputing shifted Epstein zeta for a = 1/3 on Z_3 lattice...")

# The shifted lattice sum:
# Z_a(s) = sum_{(m,n)} 1/|m + n*omega + a|^{2s}
# This is an Epstein-Hurwitz zeta.

# For the Z_3 lattice, the shifted zeta can be expressed in terms of
# the Hecke L-function of the Eisenstein integers with character.

# Specifically, for shift a = 1/3:
# Z_{1/3}(s) involves the Hurwitz zeta of Q(sqrt(-3))

# Numerical computation (sufficient for testing the conjecture):
shift_a = R(1) / R(3)  # Wilson line shift

# Compute shifted lattice sum truncated at large N
N_max = 100
shifted_sum = R(0)
unshifted_sum = R(0)

for m in range(-N_max, N_max + 1):
    for n in range(-N_max, N_max + 1):
        if m == 0 and n == 0:
            # Unshifted: skip (0,0)
            pass
        else:
            # Unshifted lattice point
            z_unsft = C(m) + C(n) * omega
            unshifted_sum += R(1) / abs(z_unsft)^2

        # Shifted lattice point (always include (0,0) term)
        z_sft = C(m) + C(n) * omega + C(shift_a)
        shifted_sum += R(1) / abs(z_sft)^2

# These are divergent at s=1, but the DIFFERENCE converges:
# Z_{1/3}(1) - Z_0(1) = finite (the shift removes the pole)

# Actually, let's compute the regulated difference using s > 1:
print("\nRegulated Epstein zeta difference (shifted - unshifted):")

s_values = [R(1.5), R(1.2), R(1.1), R(1.05), R(1.01)]

for s in s_values:
    shifted = R(0)
    unshifted = R(0)
    for m in range(-N_max, N_max + 1):
        for n in range(-N_max, N_max + 1):
            if not (m == 0 and n == 0):
                z_unsft = C(m) + C(n) * omega
                unshifted += R(1) / abs(z_unsft)^(2*s)
            z_sft = C(m) + C(n) * omega + C(shift_a)
            shifted += R(1) / abs(z_sft)^(2*s)

    diff = shifted - unshifted
    print(f"  s = {float(s):.2f}: Z_{{1/3}}(s) - Z_0(s) = {float(diff):.10f}")

# ============================================================
# The threshold ratio via the Kronecker limit formula
# ============================================================
print("\n\n" + "=" * 60)
print("KRONECKER LIMIT FORMULA AT Z_3 POINT")
print("=" * 60)

# The second Kronecker limit formula gives:
# Z_a(s) = pi/(s-1) + 2*pi*[gamma_E - ln(2) - ln(|theta_1(a|omega)|^2 / |eta(omega)|^2)] + O(s-1)
#
# where theta_1(a|tau) is the Jacobi theta function.
# The FINITE part at s=1 for the shifted lattice:
#   Z_a^{reg}(1) = -2*pi*ln(|theta_1(a|omega)|^2 / |eta(omega)|^2) + const

# Compute theta_1(1/3 | omega)
# theta_1(z|tau) = 2 * sum_{n=0}^inf (-1)^n q^{(n+1/2)^2/2} sin((2n+1)*pi*z)
# where q = e^{2*pi*i*tau}

z_val = R(1) / R(3)  # a = 1/3
q_val = C(exp(2 * pi * I * omega))

theta1 = C(0)
for n in range(200):
    sign = (-1)^n
    q_power = (n + R(1)/R(2))^2
    sine_arg = (2*n + 1) * pi_val * z_val
    theta1 += C(sign) * q_val^(q_power/R(2)) * C(sin(sine_arg))
theta1 *= C(2)

print(f"\ntheta_1(1/3 | omega) = {theta1}")
print(f"|theta_1(1/3 | omega)| = {abs(theta1)}")
print(f"|theta_1(1/3 | omega)|^2 = {abs(theta1)^2}")

# The ratio |theta_1/eta|^2:
ratio_theta_eta = abs(theta1)^2 / eta_omega_abs^2
print(f"\n|theta_1(1/3|omega)/eta(omega)|^2 = {ratio_theta_eta}")
print(f"ln(|theta_1/eta|^2) = {ln(ratio_theta_eta)}")

# ============================================================
# The threshold splitting
# ============================================================
# For the bifundamental (3,2)_{5/6} with Wilson line shift a = q * phi:
# The threshold correction to SU(3) from this sector:
#   Delta_3^{(3,2)} = 2 * [-ln(|theta_1(q*phi | tau)|^2/|eta|^2) + const]
# The threshold correction to SU(2) from this sector:
#   Delta_2^{(3,2)} = 3 * [-ln(|theta_1(q*phi | tau)|^2/|eta|^2) + const]
#
# Wait, the SAME theta function appears in both!
# The splitting comes from the MULTIPLICITY (dim of fundamental).
#
# Delta_3 - Delta_2 = (2 - 3) * [-ln(|theta_1/eta|^2) + const]
#                   = +ln(|theta_1(5*phi/6 | omega)/eta(omega)|^2) - const
#
# But we also need the ADJOINT sector contributions:
# (8,1)_0 contributes to Delta_3 only: 8 neutral states
# (1,3)_0 contributes to Delta_2 only: 3 neutral states
#
# The Y=0 sectors see no flux shift, so:
#   Delta_3^{adj} = 8 * [unshifted contribution] = 8 * (-ln(T_2 |eta|^4) + const)
#   Delta_2^{adj} = 3 * [unshifted contribution] = 3 * (-ln(T_2 |eta|^4) + const)

# Actually, we need dim(adj) not dim(fund):
# dim(adj(SU(3))) = 8 contributes to Delta_3
# dim(adj(SU(2))) = 3 contributes to Delta_2
# These are the states that don't carry U(1)_Y charge.

# For the (3,2) bifundamental:
# It transforms as fund of SU(3) (dim 3) and fund of SU(2) (dim 2)
# Its contribution to running of SU(3) is Dynkin index = 1/2 per doublet = 2 * 1/2 = 1
# Its contribution to running of SU(2) is Dynkin index = 1/2 per triplet = 3 * 1/2 = 3/2

# Plus conjugate (3bar, 2)_{-5/6}: same Dynkin indices

# Total from bifundamental + conjugate:
# b'_3(bifund) = 2 * C_2(fund_3) * dim(fund_2) = 2 * 1/2 * 2 = 2
# b'_2(bifund) = 2 * C_2(fund_2) * dim(fund_3) = 2 * 1/2 * 3 = 3

# The threshold difference from the bifundamental sector:
# Delta_3^{bifund} - Delta_2^{bifund} = (b'_3 - b'_2) * ln(...) + ...

# With the flux shift a = 5/6 * phi:
# For the bifundamental, the KK spectrum is shifted by q*phi = 5/6 * phi
# For the conjugate, the shift is -5/6 * phi

# Choose phi such that N_Y = -3 corresponds to flux through the cycle:
# phi = N_Y / (2*pi*T_2) * (lattice dual) but quantized on Z_3 orbifold
# On Z_3, phi = 1/3 (the smallest Z_3-invariant Wilson line)

# Then q*phi = 5/6 * 1/3 = 5/18 for the (3,2)
# and q*phi = -5/6 * 1/3 = -5/18 for the (3bar,2)

phi = R(1) / R(3)
q_Y = R(5) / R(6)
shift_plus = q_Y * phi   # = 5/18
shift_minus = -q_Y * phi  # = -5/18

print(f"\nWilson line phi = {float(phi)}")
print(f"Bifund shift: q*phi = {float(shift_plus)}")
print(f"Conjugate shift: -q*phi = {float(shift_minus)}")

# Compute theta_1 at these shifts
def compute_theta1(z, tau, N_terms=200):
    """Compute theta_1(z|tau)."""
    q = C(exp(2 * pi * I * tau))
    result = C(0)
    for n in range(N_terms):
        sign = (-1)^n
        q_pow = (n + R(1)/R(2))^2 / R(2)
        s_arg = (2*n + 1) * R(pi) * R(z)
        result += C(sign) * q^q_pow * C(sin(s_arg))
    return 2 * result

theta_plus = compute_theta1(shift_plus, omega)
theta_minus = compute_theta1(shift_minus, omega)

print(f"\n|theta_1(5/18 | omega)| = {abs(theta_plus)}")
print(f"|theta_1(-5/18 | omega)| = {abs(theta_minus)}")

# By the property theta_1(-z) = -theta_1(z), so |theta_1(-z)| = |theta_1(z)|
print(f"Check: |theta_+| = |theta_-|? {abs(abs(theta_plus) - abs(theta_minus)) < 1e-30}")

# ============================================================
# Full threshold computation
# ============================================================
print("\n\n" + "=" * 60)
print("FULL THRESHOLD RATIO")
print("=" * 60)

# The threshold correction to gauge coupling g_a:
# 1/g_a^2(mu) = k_a * S + b_a * ln(Lambda/mu) + Delta_a
#
# At the Z_3 point, the one-loop threshold is:
#   Delta_a = -b'_a(adj) * ln(T_2 |eta(omega)|^4)
#             -b'_a(bifund+) * ln(|theta_1(q*phi|omega)|^2 / |eta(omega)|^2)
#             -b'_a(bifund-) * ln(|theta_1(-q*phi|omega)|^2 / |eta(omega)|^2)
#             + universal constant

# b_a coefficients:
# N=2 beta from adjoint:
b3_adj = R(8)   # dim(adj SU(3)) = 8, but actually it's the Dynkin index C_2(adj)
b2_adj = R(3)   # dim(adj SU(2)) = 3, actually C_2(adj(SU(2))) = 2
# Let me be more careful. The one-loop contribution from a multiplet R is:
# b_a(R) = T(R) = Dynkin index = dim(R) * C_2(R) / dim(adj)
# For the adjoint: T(adj) = C_2(adj) = N for SU(N)
# So: T(adj SU(3)) = 3, T(adj SU(2)) = 2
# But the adjoint of one group is a singlet of the other,
# so the FULL contribution to gauge coupling a is just T(adj_a).

# For the (8,1)_0 sector:
# Contributes T_3(8) = 3 to SU(3) running, T_2(1) = 0 to SU(2)
# For the (1,3)_0 sector:
# Contributes T_3(1) = 0 to SU(3), T_2(3) = 2 to SU(2)
# For the (3,2)_{5/6}:
# T_3(3) * dim(2) = 1/2 * 2 = 1 to SU(3)
# T_2(2) * dim(3) = 1/2 * 3 = 3/2 to SU(2)

# Adjoint contribution (Y=0, same for both, but different b'):
T3_adj = R(3)  # From (8,1) only
T2_adj = R(2)  # From (1,3) only

# Bifundamental contribution (Y=5/6):
T3_bifund = R(1)     # T_3(fund) * dim(fund_2) = 1/2 * 2
T2_bifund = R(3)/R(2)  # T_2(fund) * dim(fund_3) = 1/2 * 3

# Including conjugate (same Dynkin indices):
T3_bifund_total = 2 * T3_bifund  # = 2
T2_bifund_total = 2 * T2_bifund  # = 3

print(f"Dynkin indices:")
print(f"  SU(3) from adjoint: T_3(adj) = {T3_adj}")
print(f"  SU(2) from adjoint: T_2(adj) = {T2_adj}")
print(f"  SU(3) from bifund+cc: T_3(bifund) = {T3_bifund_total}")
print(f"  SU(2) from bifund+cc: T_2(bifund) = {T2_bifund_total}")

# The threshold corrections:
ln_adj_factor = ln(T2_val * eta_omega_abs^4)
ln_bifund_factor = ln(abs(theta_plus)^2 / eta_omega_abs^2)

print(f"\nln(T_2 |eta|^4) = {float(ln_adj_factor):.15f}")
print(f"ln(|theta_1(5/18|omega)/eta|^2) = {float(ln_bifund_factor):.15f}")

# Delta_3 = -T3_adj * ln_adj - T3_bifund_total * ln_bifund + const
# Delta_2 = -T2_adj * ln_adj - T2_bifund_total * ln_bifund + const

Delta_3 = -T3_adj * ln_adj_factor - T3_bifund_total * ln_bifund_factor
Delta_2 = -T2_adj * ln_adj_factor - T2_bifund_total * ln_bifund_factor

print(f"\nDelta_3 = {float(Delta_3):.15f}")
print(f"Delta_2 = {float(Delta_2):.15f}")

diff = Delta_3 - Delta_2
print(f"\nDelta_3 - Delta_2 = {float(diff):.15f}")

# The ratio:
ratio = Delta_3 / Delta_2
print(f"Delta_3 / Delta_2 = {float(ratio):.15f}")

# ============================================================
# Compare to ln(3)/sqrt(2)
# ============================================================
target = ln(R(3)) / sqrt(R(2))
print(f"\nln(3)/sqrt(2) = {float(target):.15f}")

# Various combinations:
print(f"\nDelta_3 - Delta_2 = {float(diff):.15f}")
print(f"ln(3)/sqrt(2) = {float(target):.15f}")
print(f"Ratio (diff / target) = {float(diff / target):.15f}")
print(f"Ratio (diff / ln(3)) = {float(diff / ln(R(3))):.15f}")
print(f"Ratio (diff / sqrt(2)) = {float(diff / sqrt(R(2))):.15f}")

# The COUPLING ratio from thresholds:
# alpha_1/alpha_2 at M_Z from RGE:
# (alpha_1/alpha_2)(M_Z) = (alpha_1/alpha_2)(M_GUT) * exp(-(b_1-b_2)*ln(M_GUT/M_Z)/(2*pi) + (Delta_1-Delta_2)/(8*pi^2))
#
# If we parametrize the GUT-scale ratio as:
#   (k_1*alpha_1^{-1} - k_2*alpha_2^{-1})(M_s) = (Delta_1 - Delta_2)/(8*pi^2)
# and this ratio determines sin^2(theta_W)

# The sin^2(theta_W) correction:
# delta(sin^2 theta) = alpha/(4*pi) * (5/3) * (Delta_2 - Delta_1) / (b_2 - b_1)
# where b_1 = 41/10, b_2 = -19/6 are SM beta coefficients

# But what we really want is whether the GEOMETRY produces ln(3)/sqrt(2)
# The geometric quantity is:
geometric_ratio = diff  # = Delta_3 - Delta_2

print(f"\n\n{'='*60}")
print(f"THE TEST: Does the Z_3 orbifold threshold produce ln(3)/sqrt(2)?")
print(f"{'='*60}")
print(f"\nGeometric quantity (Delta_3 - Delta_2): {float(geometric_ratio):.15f}")
print(f"Target ln(3)/sqrt(2):                   {float(target):.15f}")
print(f"\nDirect match: {'YES' if abs(float(geometric_ratio) - float(target)) / float(target) < 0.01 else 'NO'}")

# Try other ratios:
print(f"\n--- Searching for ln(3)/sqrt(2) in various combinations ---")
for name, val in [
    ("Delta_3 - Delta_2", diff),
    ("Delta_3 / Delta_2", ratio),
    ("(Delta_3 - Delta_2) / (4*pi^2)", diff / (4*pi_val^2)),
    ("(Delta_3 - Delta_2) / (8*pi^2)", diff / (8*pi_val^2)),
    ("ln(|theta_1(5/18|omega)|)", ln(abs(theta_plus))),
    ("ln(|theta_1(5/18|omega)/eta(omega)|)", ln(abs(theta_plus)/eta_omega_abs)),
    ("ln(T_2 * |eta|^4)", ln_adj_factor),
    ("2*ln(|eta(omega)|)", 2*ln(eta_omega_abs)),
    ("-ln(T_2 |eta|^4) / ln(|theta/eta|^2)", -ln_adj_factor / ln_bifund_factor if ln_bifund_factor != 0 else R(0)),
]:
    v = float(val)
    if abs(float(target)) > 0:
        pct = abs(v - float(target)) / float(target) * 100
        print(f"  {name:<45} = {v:>15.10f}  ({pct:>8.3f}% from target)")

# Also check if the theta/eta ratio itself has structure:
print(f"\n--- Special values ---")
print(f"|theta_1(5/18 | omega)| = {float(abs(theta_plus)):.15f}")
print(f"|eta(omega)| = {float(eta_omega_abs):.15f}")
print(f"|theta_1/eta| = {float(abs(theta_plus)/eta_omega_abs):.15f}")
print(f"|theta_1/eta|^2 = {float(abs(theta_plus)^2/eta_omega_abs^2):.15f}")
print(f"ln(|theta_1/eta|^2) = {float(ln_bifund_factor):.15f}")

# Check if the theta_1 value relates to Gamma(1/3):
print(f"\nGamma(1/3) = {float(gamma_13):.15f}")
print(f"Gamma(1/3)^{3/2} = {float(gamma_13^(R(3)/R(2))):.15f}")
print(f"3^{1/8} = {float(R(3)^(R(1)/R(8))):.15f}")
print(f"|theta_1(5/18|omega)| / (3^{1/8} * Gamma(1/3)^{3/2} / (2*pi)) = {float(abs(theta_plus) / eta_omega_abs):.15f}")

print(f"\n{'='*60}")
print(f"COMPUTATION COMPLETE")
print(f"{'='*60}")
