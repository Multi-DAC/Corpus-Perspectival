"""
STEP 1: Spectral Action Coupling Ratios from Seeley-DeWitt Coefficients

The spectral action S = Tr(f(D^2/Lambda^2)) expanded via heat kernel gives:
S ~ sum_n f_n Lambda^(d-2n) int a_n(x,D^2) sqrt(g) d^dx

For the squared Dirac operator D^2 on a 4D spin manifold.
"""

import sympy as sp
from sympy import Rational, symbols, expand, simplify, sqrt, pi, latex

R, Ric2, Riem2, boxR = symbols('R Ric2 Riem2 boxR')
C2, E4 = symbols('C2 E4')

print("=" * 70)
print("SPECTRAL ACTION: HEAT KERNEL COEFFICIENTS FOR D^2 ON SPIN MANIFOLD")
print("=" * 70)

# Spinor dimension in d=4 (Euclidean)
N_s = 4

# For a general Laplace-type operator P = -(g^{mn} nabla_m nabla_n + E):
# a_0(x,P) = (4pi)^{-d/2} tr(I)
# a_2(x,P) = (4pi)^{-d/2} tr(R/6 I - E)
# a_4(x,P) = (4pi)^{-d/2} (1/360) tr(
#     2 Riem2 I - 2 Ric2 I + 5 R^2 I
#     - 12 boxR I + 60 R E - 180 E^2 + 60 boxE
#     + 30 Omega_{mn} Omega^{mn}
# )
# (Vassilevich, hep-th/0306138, eq. 4.1 and 4.3)

# For D^2 on spin manifold (Lichnerowicz formula):
# D^2 = nabla^dagger nabla + R/4
# So in the Laplace-type form: E = -R/4 * I_{N_s}

# Traces (in spinor space):
tr_I = N_s  # = 4
tr_E = Rational(-1, 4) * R * N_s  # = -R
tr_E2 = Rational(1, 16) * R**2 * N_s  # = R^2/4
tr_RE = R * Rational(-1, 4) * R * N_s  # = -R^2
tr_boxE = Rational(-1, 4) * boxR * N_s  # = -boxR

# Spin connection curvature:
# Omega_{mn} = (1/4) R_{mn}^{ab} gamma_a gamma_b
# tr(Omega_{mn} Omega^{mn}) = (1/16) R_{mnab} R^{mncd} tr(gamma^a gamma^b gamma_c gamma_d)
#
# tr(gamma^a gamma^b gamma^c gamma^d) = 4(d^{ab}d^{cd} - d^{ac}d^{bd} + d^{ad}d^{bc})
#
# Contracting with R_{mnab} R^{mncd}:
# Term 1: d^{ab} d^{cd} -> R_{mna}^a R^{mnc}_c = 0 (Riemann antisymmetric in last pair)
# Term 2: -d^{ac} d^{bd} -> -R_{mnab} R^{mnab} = -Riem2
# Term 3: d^{ad} d^{bc} -> R_{mnab} R^{mnba} = -Riem2 (antisymmetry)
#
# Result: (1/16) * 4 * (0 - Riem2 - Riem2) = -(1/2) Riem2
tr_Om2 = Rational(-1, 2) * Riem2

print("\n--- Traces for D^2 (spin bundle, d=4) ---")
print(f"tr(I)           = {tr_I}")
print(f"tr(E)           = {tr_E}")
print(f"tr(E^2)         = {tr_E2}")
print(f"tr(R*E)         = {tr_RE}")
print(f"tr(box E)       = {tr_boxE}")
print(f"tr(Omega^2)     = {tr_Om2}")

# Build the content of a_4 (everything inside (4pi)^{-2} * (1/360) * [...])
a4_content = (
    2 * Riem2 * tr_I        # 2 * Riem2 * 4 = 8 Riem2
    - 2 * Ric2 * tr_I       # -2 * Ric2 * 4 = -8 Ric2
    + 5 * R**2 * tr_I       # 5 * R^2 * 4 = 20 R^2
    - 12 * boxR * tr_I      # -12 * boxR * 4 = -48 boxR
    + 60 * tr_RE            # 60 * (-R^2) = -60 R^2
    - 180 * tr_E2           # -180 * R^2/4 = -45 R^2
    + 60 * tr_boxE          # 60 * (-boxR) = -60 boxR
    + 30 * tr_Om2           # 30 * (-Riem2/2) = -15 Riem2
)

a4_content = expand(a4_content)

print("\n--- a_4 content (before 1/360 factor) ---")
print(f"a_4 content = {a4_content}")

# Extract coefficients
c_Riem2 = a4_content.coeff(Riem2)
c_Ric2 = a4_content.coeff(Ric2)
c_R2 = a4_content.coeff(R, 2)
c_boxR = a4_content.coeff(boxR)

print(f"\nCoefficients inside (4pi)^{{-2}} * (1/360) * [...]:")
print(f"  Riem2:  {c_Riem2}")
print(f"  Ric2:   {c_Ric2}")
print(f"  R^2:    {c_R2}")
print(f"  box R:  {c_boxR}")

# Verify by hand:
# Riem2: 2*4 - 15 = 8 - 15 = -7
# Ric2: -2*4 = -8
# R^2: 5*4 - 60 - 45 = 20 - 60 - 45 = -85
# boxR: -12*4 - 60 = -48 - 60 = -108
print(f"\nVerification:")
print(f"  Riem2: 2*4 + 30*(-1/2) = 8 - 15 = -7  CHECK: {c_Riem2 == -7}")
print(f"  Ric2:  -2*4 = -8                       CHECK: {c_Ric2 == -8}")
print(f"  R^2:   5*4 - 60 - 45 = -85             CHECK: {c_R2 == -85}")
print(f"  boxR:  -12*4 - 60 = -108               CHECK: {c_boxR == -108}")

print("\n" + "=" * 70)
print("a_2 COEFFICIENT (EINSTEIN-HILBERT)")
print("=" * 70)

# a_2(x, D^2) = (4pi)^{-2} * tr(R/6 * I - E)
# = (4pi)^{-2} * [R/6 * 4 - (-R/4 * 4)]
# = (4pi)^{-2} * [2R/3 + R]
# = (4pi)^{-2} * (5R/3)
a2_coeff = Rational(2,3) + 1  # = 5/3
print(f"a_2 = (4pi)^{{-2}} * (R/6 * 4 + R/4 * 4) = (4pi)^{{-2}} * ({Rational(2,3)} + 1) R = (4pi)^{{-2}} * {Rational(5,3)} R")

print("\n" + "=" * 70)
print("THE SPECTRAL ACTION (PURE GRAVITY, 4D SPIN MANIFOLD)")
print("=" * 70)

print("""
S_spec = (1/(16 pi^2)) int d^4x sqrt(g) [
    4 f_0 Lambda^4                                           (cosmological constant)
  + (5/3) f_2 Lambda^2  R                                   (Einstein-Hilbert)
  + f_4 (1/360) (-7 Riem^2 - 8 Ric^2 - 85 R^2)            (higher curvature)
]

Dropping the total derivative box R term.
""")

print("=" * 70)
print("CONVERTING TO (C^2, E_4, R^2) BASIS")
print("=" * 70)

# Weyl: C^2 = Riem2 - 2 Ric2 + (1/3) R^2
# Gauss-Bonnet: E_4 = Riem2 - 4 Ric2 + R^2
#
# Inverting:
# Riem2 = C^2 + 2 Ric2 - (1/3) R^2
# From E_4 = C^2 + 2 Ric2 - (1/3) R^2 - 4 Ric2 + R^2 = C^2 - 2 Ric2 + (2/3) R^2
# => Ric2 = (C^2 - E_4 + (2/3) R^2) / 2
# => Riem2 = C^2 + (C^2 - E_4 + (2/3) R^2) - (1/3) R^2
#          = 2 C^2 - E_4 + (1/3) R^2

# Substituting:
# c_Riem2 * Riem2 + c_Ric2 * Ric2 + c_R2 * R^2
# = c_Riem2 * (2C^2 - E4 + R^2/3) + c_Ric2 * (C^2 - E4 + 2R^2/3)/2 + c_R2 * R^2

a4_new = (c_Riem2 * (2*C2 - E4 + Rational(1,3)*R**2)
        + c_Ric2 * (C2 - E4 + Rational(2,3)*R**2) / 2
        + c_R2 * R**2)

a4_new = expand(a4_new)

new_c_C2 = a4_new.coeff(C2)
new_c_E4 = a4_new.coeff(E4)
new_c_R2 = a4_new.coeff(R, 2)

print(f"\nIn the (C^2, E_4, R^2) basis:")
print(f"  C^2 coefficient:  {new_c_C2}")
print(f"  E_4 coefficient:  {new_c_E4}")
print(f"  R^2 coefficient:  {new_c_R2}")

# Verify:
# C^2: c_Riem2 * 2 + c_Ric2 / 2 = -7*2 + (-8)/2 = -14 - 4 = -18
# E_4: -c_Riem2 - c_Ric2 / 2 = 7 + 4 = 11... wait
# Actually: -c_Riem2 + c_Ric2 * (-1/2) = -(-7) + (-8)*(-1/2) = 7 + 4 = 11
# Hmm, let me recalculate
# E_4 coeff: c_Riem2 * (-1) + c_Ric2 * (-1/2) = (-7)(-1) + (-8)(-1/2) = 7 + 4 = 11
# R^2 coeff: c_Riem2 * (1/3) + c_Ric2 * (1/3) + c_R2 = (-7)/3 + (-8)/3 + (-85) = -5 + (-85) = -90
# = -7/3 - 8/3 - 85 = -15/3 - 85 = -5 - 85 = -90

print(f"\nVerification:")
print(f"  C^2: -7*2 + (-8)/2 = -14 - 4 = -18      CHECK: {new_c_C2 == -18}")
print(f"  E_4: -(-7)*1 + (-8)*(-1/2) = 7 + 4 = 11 CHECK: {new_c_E4}")
print(f"  R^2: (-7)/3 + (-8)/3 + (-85) = -5-85=-90 CHECK: {new_c_R2}")

print(f"\nSo a_4(D^2) = (4pi)^{{-2}} * (1/360) * [{new_c_C2} C^2 + ({new_c_E4}) E_4 + ({new_c_R2}) R^2]")

print("\n" + "=" * 70)
print("RATIOS (THE KEY RESULT)")
print("=" * 70)

print(f"""
The spectral action (pure gravity on 4D spin manifold) gives:

S_higher = f_4 / (16 pi^2 * 360) * int d^4x sqrt(g) [
    {new_c_C2} C_mnrs^2 + {new_c_E4} E_4 + {new_c_R2} R^2
]
""")

# In the standard parametrization:
# S = int d^4x sqrt(g) [ alpha_EH * R + alpha_CC * C^2 + alpha_E * E_4 + alpha_R * R^2 ]
#
# alpha_EH = f_2 Lambda^2 * 5/(3 * 16 pi^2)
# alpha_CC = f_4 * (-18) / (360 * 16 pi^2) = -f_4 / (320 pi^2)
# alpha_E  = f_4 * 11 / (360 * 16 pi^2) = 11 f_4 / (5760 pi^2)
# alpha_R  = f_4 * (-90) / (360 * 16 pi^2) = -f_4 / (64 pi^2)

alpha_EH = sp.Symbol('alpha_EH')
alpha_CC = Rational(new_c_C2, 360)
alpha_E = Rational(new_c_E4, 360)
alpha_R = Rational(new_c_R2, 360)

print("Couplings (in units of f_4 / (16 pi^2)):")
print(f"  alpha_CC (Weyl^2) = {alpha_CC} = {float(alpha_CC):.6f}")
print(f"  alpha_E  (E_4)    = {alpha_E} = {float(alpha_E):.6f}")
print(f"  alpha_R  (R^2)    = {alpha_R} = {float(alpha_R):.6f}")

print(f"\nRATIOS among higher-curvature terms:")
ratio_C2_R2 = Rational(new_c_C2, new_c_R2)
ratio_E4_R2 = Rational(new_c_E4, new_c_R2)
ratio_C2_E4 = Rational(new_c_C2, new_c_E4)

print(f"  C^2 / R^2 = {new_c_C2}/{new_c_R2} = {ratio_C2_R2} = {float(ratio_C2_R2):.6f}")
print(f"  E_4 / R^2 = {new_c_E4}/{new_c_R2} = {ratio_E4_R2} = {float(ratio_E4_R2):.6f}")
print(f"  C^2 / E_4 = {new_c_C2}/{new_c_E4} = {ratio_C2_E4} = {float(ratio_C2_E4):.6f}")

print("\n" + "=" * 70)
print("EQUIVALENT: (Riem^2, Ric^2, R^2) RATIOS")
print("=" * 70)

ratio_Riem_R2 = Rational(c_Riem2, c_R2)
ratio_Ric_R2 = Rational(c_Ric2, c_R2)

print(f"  Riem^2 / R^2 = {c_Riem2}/{c_R2} = {ratio_Riem_R2} = {float(ratio_Riem_R2):.6f}")
print(f"  Ric^2 / R^2  = {c_Ric2}/{c_R2} = {ratio_Ric_R2} = {float(ratio_Ric_R2):.6f}")
print(f"  Riem^2 / Ric^2 = {c_Riem2}/{c_Ric2} = {Rational(c_Riem2, c_Ric2)} = {float(Rational(c_Riem2, c_Ric2)):.6f}")

print("\n" + "=" * 70)
print("IMPORTANT: SIGN CHECK")
print("=" * 70)
print("""
The NEGATIVE signs in the a_4 coefficients are significant:
  -7 Riem^2 - 8 Ric^2 - 85 R^2

This means the spectral action generates NEGATIVE higher-curvature couplings
(since f_4 > 0 for any reasonable cutoff function).

In the (C^2, E_4, R^2) basis:
  -18 C^2 + 11 E_4 - 90 R^2

The Weyl^2 term has NEGATIVE coefficient -> conformal gravity with WRONG SIGN
(relative to the standard positive C^2 in Stelle gravity).
The E_4 term has POSITIVE coefficient -> standard topological term.
The R^2 term has NEGATIVE coefficient.

For AS comparison, the SIGNS matter as much as the ratios.
""")

print("\n" + "=" * 70)
print("DIMENSIONLESS COUPLING RATIOS FOR AS COMPARISON")
print("=" * 70)

print("""
In asymptotic safety, one typically parametrizes the effective action as:
  Gamma_k = int d^4x sqrt(g) [
    -Lambda_k/(8 pi G_k) + R/(16 pi G_k) + alpha_k R^2 + beta_k R_{mn}^2
  ]

or equivalently:
  Gamma_k = int d^4x sqrt(g) [
    -2 lambda_k k^2 / (16 pi g_k) + R/(16 pi g_k) + omega_k C^2 + theta_k E_4 + sigma_k R^2
  ]

where g_k = k^2 G_k and lambda_k = Lambda_k / k^2 are dimensionless.

From the spectral action, treating Lambda as the AS cutoff k:

The R^2 truncation couplings from spectral action are:
  alpha (R^2 coupling) = f_4 * (-90) / (360 * 16 pi^2) = -f_4/(64 pi^2)
  beta (Ric^2 coupling) = f_4 * (-8) / (360 * 16 pi^2) = -f_4/(720 pi^2)

Ratio: beta/alpha = (-8)/(-90) = 4/45 = 0.0889

If we use the (omega, theta) parametrization:
  omega (C^2 coupling) = f_4 * (-18) / (360 * 16 pi^2) = -f_4/(320 pi^2)
  sigma (R^2 coupling) = f_4 * (-90) / (360 * 16 pi^2) = -f_4/(64 pi^2)

Ratio: omega/sigma = (-18)/(-90) = 1/5 = 0.200
""")

print(f"  beta/alpha = Ric^2/R^2 = {Rational(c_Ric2, c_R2)} = {float(Rational(c_Ric2, c_R2)):.6f}")
print(f"  omega/sigma = C^2/R^2 = {Rational(new_c_C2, new_c_R2)} = {float(Rational(new_c_C2, new_c_R2)):.6f}")

print("\n\nDONE with Step 1.")
