"""
Step 2: The Chamseddine-Connes-Marcolli (CCM) Spectral Action Higgs Mass Prediction.

The CCM spectral action for the noncommutative geometry of the SM gives:
  S = Tr(f(D_A/Lambda))

Expanding in powers of Lambda^{-1} using Seeley-DeWitt coefficients:
  S = f_4 * Lambda^4 * a_0 + f_2 * Lambda^2 * a_2 + f_0 * a_4 + ...

The key BOUNDARY CONDITIONS at the cutoff Lambda:

1. Gauge coupling unification:
   g_1^2(Lambda) = g_2^2(Lambda) = g_3^2(Lambda) = g^2
   [where g1 is in GUT normalization, so sin^2(theta_W) = 3/8]

2. Higgs quartic coupling:
   lambda(Lambda) = (pi^2 / (2 * f_0)) * (b / a^2)

   where a = Tr(Y_nu^dag Y_nu + Y_e^dag Y_e + 3(Y_u^dag Y_u + Y_d^dag Y_d))
   and   b = Tr((Y_nu^dag Y_nu)^2 + (Y_e^dag Y_e)^2 + 3(Y_u^dag Y_u)^2 + 3(Y_d^dag Y_d)^2)

   and f_0 is the zeroth moment of the spectral function, related to gauge coupling by:
   g^2 = pi^2 / (2 * f_0)    [for the normalization Tr(T_a T_b) = delta_ab/2]

   Wait — let me be more careful. The relation is:

   From the gauge kinetic term:
     (f_0 / (2*pi^2)) * (1/4) * integral F_uv F^uv

   Comparing with the standard gauge kinetic term (1/(4*g^2)) * F^2:
     f_0 / (2*pi^2) = 1/g^2
     => f_0 = 2*pi^2 / g^2

   So: lambda(Lambda) = (pi^2 / (2 * f_0)) * (b / a^2)
                       = (pi^2 / (2 * 2*pi^2/g^2)) * (b / a^2)
                       = (g^2 / 4) * (b / a^2)

   Wait, that's not right either. Let me derive from the original paper.

The CORRECT derivation from Chamseddine-Connes-Marcolli (2007), eq. (3.46):

The bosonic spectral action gives:
  S_bos = (48*f_4*Lambda^4 - f_2*Lambda^2*c + f_0/4 * d) * (1/pi^2) + ...
        + f_0/(2*pi^2) * [a*|D_mu H|^2 - b*|H|^4 + ...]

Actually, the computation is cleaner from the "Resilience" paper (Chamseddine-Connes 2012).

The key relation is the HIGGS MASS FORMULA from the spectral action.

From CCM 2007, the Higgs mass relation (after proper normalization of the Higgs field) is:

  m_H^2 = (2*b/a) * M_W^2 * (1/g_2^2) * lambda_phys

No wait. Let me just use the SIMPLEST correct statement.

The spectral action gives TWO independent relations:
(A) lambda(Lambda) = g^2(Lambda) * b / a^2     [up to known numerical factors]
(B) Gauge unification: all g_i^2 are equal at Lambda

With top-quark dominance (Y_u ≈ diag(0,0,y_t)):
  a = 3*y_t^2    (factor 3 from color)
  b = 3*y_t^4

  b/a^2 = 3*y_t^4 / (9*y_t^4) = 1/3

So: lambda(Lambda) = g^2(Lambda) / (4*3) = g^2(Lambda)/12

Wait, I need to be careful about factors of pi.

Let me just use the SPECIFIC formula from the literature that leads to the Higgs mass.

=== THE CORRECT CCM RELATION ===

From Chamseddine & Connes, "Resilience of the Spectral Standard Model" (2012),
and also from Devastato, Lizzi, Martinetti (2014):

The spectral action gives the tree-level relation at the cutoff Lambda:

  m_H^2 / m_W^2 = 2*R

where R = Tr(k_nu^4 + k_e^4 + 3*k_u^4 + 3*k_d^4) / [Tr(k_nu^2 + k_e^2 + 3*k_u^2 + 3*k_d^2)]^2

and k_f are the Yukawa coupling MATRICES (not dimensionless yt, but the matrices Y_f).

With top dominance: R = 3*y_t^4 / (3*y_t^2)^2 = 1/3

=> m_H = m_W * sqrt(2/3) ≈ 80.4 * 0.8165 ≈ 65.6 GeV  (way too low!)

Hmm, that gives 65.6 GeV, not 170 GeV. Something is wrong.

Actually, from Chamseddine-Connes 2012, the relation BEFORE running is:

  lambda_unif = pi^2 * b / (2*f_0 * a^2)

and from the gauge coupling: 1/g^2 = f_0 / (2*pi^2)

=> lambda_unif = g^2 * b / (4*a^2) ???

No. Let me look at this more carefully.

The relation from the original CCM paper (hep-th/0610241), equations around (3.45)-(3.50):

The scalar potential from the spectral action is:
  V(H) = -mu^2 |H|^2 + lambda_CCM |H|^4

where (after normalization of H to have canonical kinetic term):
  lambda_CCM = pi^2 * b / (2 * f_0 * a^2)

With f_0 = 2*pi^2/g^2 at unification:
  lambda_CCM = pi^2 * b / (2 * (2*pi^2/g^2) * a^2) = g^2 * b / (4 * a^2)

With b/a^2 = 1/3 (top dominance):
  lambda_CCM = g^2 / 12

At the GUT scale, g^2 ≈ 0.52^2 ≈ 0.27 (from our running):
  lambda_CCM ≈ 0.27/12 ≈ 0.022

But from our running, lambda at 10^13 GeV is -0.028 (NEGATIVE).

The Higgs mass is: m_H^2 = 2*lambda*v^2
If lambda = 0.022 at the GUT scale, we need to run it DOWN to the EW scale.

BUT the original CCM result was m_H ≈ 170 GeV (tree-level, no running).
This came from:
  m_H^2 = 4*lambda_CCM * v^2   (note: factor 4, not 2, from their conventions)
  m_H^2 = 4 * (g^2/12) * v^2 = g^2 * v^2 / 3

Ah wait — in CCM conventions, the potential is V = lambda*|phi|^4 (no factor of 1/4),
and m_H^2 = 2*lambda*v^2 with v^2 = <phi>^2 / 2... Convention-dependent.

Let me just compute directly.

The DEFINITIVE statement from the literature:

Chamseddine-Connes (2012): The spectral action TREE-LEVEL prediction gives m_H ≈ 170 GeV.
This comes from lambda = pi^2/(2*f_0) * b/a^2 with top dominance.

The value 170 GeV arises from:
  m_H^2 = 8 * lambda * v^2 / 4   ... different H normalization

Actually, the 170 GeV result is well-known and came from:
  m_H = sqrt(8*R) * m_W  where R = b/a^2 = 1/3 with top dominance
  m_H = sqrt(8/3) * 80.4 = 1.633 * 80.4 = 131 GeV ??? That's not 170 either.

OK, I am going in circles. Let me just compute BOTH possible interpretations and see
which one matches the literature value of 170 GeV.
"""

import numpy as np

M_W = 80.377  # GeV
v = 246.22    # GeV
M_H_obs = 125.25  # GeV

print("=== CCM Higgs Mass Prediction: All Possible Formulas ===\n")

# The ratio R with top-quark dominance
# a = Tr(Y_nu^dag Y_nu + Y_e^dag Y_e + 3(Y_u^dag Y_u + Y_d^dag Y_d))
# b = Tr((Y_nu^dag Y_nu)^2 + (Y_e^dag Y_e)^2 + 3(Y_u^dag Y_u)^2 + 3(Y_d^dag Y_d)^2)
# With only top: a = 3*y_t^2, b = 3*y_t^4
# R = b/a^2 = 1/3

R = 1.0/3.0
print(f"R = b/a^2 = {R:.6f} (top-quark dominance)")

# If there is a Dirac neutrino with large Yukawa y_nu ~ y_t:
# a = y_nu^2 + 3*y_t^2, b = y_nu^4 + 3*y_t^4
# For y_nu = y_t: a = 4*y_t^2, b = 4*y_t^4
# R = 4*y_t^4 / (16*y_t^4) = 1/4

R_with_nu = 1.0/4.0
print(f"R = b/a^2 = {R_with_nu:.6f} (with y_nu = y_t, as in CCM seesaw)")

# But CCM actually uses a Majorana neutrino with seesaw.
# In the 2007 paper, they have 3 right-handed neutrinos with Majorana mass matrix.
# The relevant Yukawa for the Higgs mass is still the top + the heaviest neutrino.
# With the see-saw constraint, the neutrino Yukawa can be O(1).

# CCM 2007 used Dirac condition at unification: y_nu = y_t
# This gives R = 1/4, NOT 1/3

print(f"\n=== Formula 1: m_H^2 = 8*R * M_W^2 ===")
for R_val, label in [(1/3, "top only"), (1/4, "top + nu (CCM)")]:
    m_H = M_W * np.sqrt(8 * R_val)
    print(f"  R={R_val:.4f} ({label}): m_H = {m_H:.1f} GeV")

print(f"\n=== Formula 2: m_H^2 = 4*R * (2*M_W)^2 = 16*R * M_W^2 ===")
for R_val, label in [(1/3, "top only"), (1/4, "top + nu (CCM)")]:
    m_H = M_W * np.sqrt(16 * R_val)
    print(f"  R={R_val:.4f} ({label}): m_H = {m_H:.1f} GeV")

# Actually, the standard result from CCM 2007/2010/2012 is:
# lambda(Lambda) = pi^2/(2*f_0) * b/a^2
# g^2(Lambda) = pi^2 / f_0   [this is the correct relation]
# => lambda(Lambda) = g^2/(2) * b/a^2 = g^2 * R / 2

# Then: m_H^2 = 2*lambda * v^2 (standard convention, V = lambda(phi^dag phi - v^2/2)^2)
# => m_H^2 = g^2 * R * v^2

print(f"\n=== Formula 3: lambda = g^2*R/2, m_H^2 = 2*lambda*v^2 = g^2*R*v^2 ===")
# At the unification scale, all g_i equal.
# From our RG running, g_unified ≈ 0.52 at ~10^14-10^16 GeV
g_unif_values = [0.52, 0.55, 0.544]
for g_val in g_unif_values:
    for R_val, label in [(1/3, "top only"), (1/4, "top + nu (CCM)")]:
        lam = g_val**2 * R_val / 2
        m_H = v * np.sqrt(2 * lam)
        print(f"  g={g_val}, R={R_val:.4f} ({label}): lambda={lam:.5f}, m_H = {m_H:.1f} GeV")

# Hmm none of these give 170. Let me try the OTHER normalization.
# Some authors use: g^2 = 2*pi^2/f_0 (with different trace convention)
# => lambda = (pi^2/(2*f_0)) * b/a^2 = (g^2/4) * b/a^2 = g^2*R/4
# m_H^2 = 2*lambda*v^2 = g^2*R*v^2/2

print(f"\n=== Formula 4: lambda = g^2*R/4, m_H^2 = g^2*R*v^2/2 ===")
for g_val in g_unif_values:
    for R_val, label in [(1/3, "top only"), (1/4, "top + nu (CCM)")]:
        lam = g_val**2 * R_val / 4
        m_H = v * np.sqrt(g_val**2 * R_val / 2)
        print(f"  g={g_val}, R={R_val:.4f} ({label}): lambda={lam:.5f}, m_H = {m_H:.1f} GeV")

# THE ACTUAL CCM RESULT: They get m_H ≈ 170 GeV.
# 170 GeV corresponds to: m_H^2 = 170^2 = 28900
# v^2 = 246.22^2 = 60624
# lambda = m_H^2/(2*v^2) = 28900/121248 = 0.2384
# That's a HUGE quartic. In the SM, lambda(M_Z) = 0.129.

# Looking at this differently: The 170 GeV came from the TREE-LEVEL relation
# applied at LOW energies (not running lambda down).
# The relation is: m_H = sqrt(2*lambda) * v where lambda is the NCG value.

# FROM THE CCM PAPER (reading more carefully):
# They get: m_H^2 / (4*M_W^2) = b/a^2 = R
# => m_H^2 = 4*R * (80.4)^2

print(f"\n=== Formula 5: m_H^2 = 4*R * (2*M_W^2) = 4*R*4*M_W^2 ===")
# No that's too many factors. Let me try:
# m_H^2 = 4*M_W^2 * b/a^2
print(f"\n=== Formula 6: m_H^2 = 4*M_W^2 * R ===")
for R_val, label in [(1/3, "top only"), (1/4, "top + nu (CCM)")]:
    m_H = 2 * M_W * np.sqrt(R_val)
    print(f"  R={R_val:.4f} ({label}): m_H = {m_H:.1f} GeV")

# OK that gives 92.8 for top only and 80.4 for top+nu. Not 170.

# Let me think about this differently.
# The CORRECT statement from Stephan (2006), eq (4.37):
# m_H^2 = 4*y_t^2 * M_W^2 / g_2^2 * (b/a^2) * a^2/(3*y_t^2)^2 ...
# No, that's getting confused.

# DIRECT FROM FIRST PRINCIPLES:
# Spectral action gives potential V = -mu^2|H|^2 + lambda|H|^4
# where the PHYSICAL Higgs field h = sqrt(2)*Re(H^0) after EWSB
# V(h) = (1/2)*m_H^2*h^2 + ... with m_H^2 = 2*lambda*v^2

# The CCM spectral action coefficient of |H|^4:
# -f_0/(2*pi^2) * b * |H|^4 (from the a_4 term)
# where b = Tr((Y^dag Y)^2) and H is the UNNORMALIZED Higgs doublet.

# The Higgs kinetic term coefficient:
# f_0/(2*pi^2) * a * |D_mu H|^2

# To get canonically normalized Higgs: H_phys = sqrt(f_0*a/(2*pi^2)) * H
# So |H|^4 = (2*pi^2/(f_0*a))^2 * |H_phys|^4

# lambda_phys = (f_0*b)/(2*pi^2) * (2*pi^2/(f_0*a))^2 = (2*pi^2*b)/(f_0*a^2)

# With f_0 = pi^2/g^2 (from gauge kinetic):
# Wait, which convention? The gauge kinetic term from the spectral action is:
# (f_0/(2*pi^2)) * (1/4) * c_gauge * Tr(F^2)
# Matching (1/(4*g^2))*Tr(F^2) gives: f_0*c_gauge/(2*pi^2) = 1/g^2
# The gauge normalization constant c_gauge depends on the algebra.
# For SU(2): c_gauge = 1 (with adjoint trace), so f_0 = 2*pi^2/g_2^2
# For SU(3): same, f_0 = 2*pi^2/g_3^2 (requires g_2 = g_3 at Lambda)
# For U(1): f_0 = 2*pi^2/(g_1^2 * 5/3) [in GUT normalization]

# So at unification where g_1 = g_2 = g_3 = g:
# f_0 = 2*pi^2/g^2

# And lambda_phys = 2*pi^2*b / (f_0*a^2) = 2*pi^2*b / ((2*pi^2/g^2)*a^2)
#                = g^2 * b / a^2 = g^2 * R

# Hmm, that gives lambda = g^2 * R
# With g=0.54, R=1/4: lambda = 0.073, m_H = sqrt(2*0.073)*246 = 94 GeV
# With g=0.54, R=1/3: lambda = 0.097, m_H = sqrt(2*0.097)*246 = 108 GeV
# Still not 170!

# THE RESOLUTION: The CCM 2007 paper uses a DIFFERENT normalization.
# Let me trace through equation by equation.

# From CCM 2007 (arXiv:0706.3688), Section 3:
# The Higgs potential terms from the spectral action expansion (eq 3.38):
#   ... - (a*f_2*Lambda^2)/(pi^2) |phi|^2 + (f_0*b)/(2*pi^2) |phi|^4 + ...
# where phi is related to the internal fluctuation, NOT the physical Higgs.
# The physical Higgs H is related to phi by the rescaling that makes the kinetic
# term canonical. The kinetic term is:
#   (f_0*a)/(8*pi^2) * |D_mu phi|^2    (eq 3.38 kinetic term)
# So phi_phys = sqrt(f_0*a/(8*pi^2)) * phi (WAIT - could be 4pi^2 not 8pi^2)

# Let me just use the KNOWN RESULT. The CCM prediction is:
#   m_H^2 = 4 * (sum_gen y_f^4) / (sum_gen y_f^2) * (M_W/g_2)^2
#         = 4 * b/a * (v/2)^2   ??? No.

# Actually the cleanest statement (from van Suijlekom's textbook, Chapter 11):
# At the unification scale:
#   lambda_H = 24*f_0^{-1} * pi^2 * b / a^2   ??? Different again.

# OK, I will compute the NUMBER that gives 170 GeV and work backwards.
# 170 GeV => lambda = 170^2/(2*246.22^2) = 0.2384
# We need: lambda = ?? * g^2(Lambda) * R
# 0.2384 = x * 0.544^2 * 1/4 = x * 0.074
# x = 3.22
# Or with R = 1/3: 0.2384 = x * 0.544^2 * 1/3 = x * 0.099
# x = 2.41

# Hmm, that doesn't correspond to any simple numerical factor.

# ACTUALLY: The 170 GeV was obtained NOT from the full running,
# but from a TREE-LEVEL relation. In many papers, the relation is:
#
# m_H = 2*M_W * sqrt(a*e/b*c)    where a,b,c,e are specific coefficients
#
# But in the SIMPLEST formulation (top-dominant, tree-level):
# m_H ≈ sqrt(8/3) * m_t ≈ 1.633 * 174 = 284 GeV
# No, that's too big.
# m_H ≈ sqrt(8*R) * m_t with R=1/4: sqrt(2) * 174 = 246 GeV
# Still too big.
# m_H ≈ 2*m_t * sqrt(b/a^2) * sqrt(a_param) ... too many unknowns.

# Let me try yet another approach. The tree-level "big desert" prediction:
# lambda(Lambda) is set by NCG. Run it DOWN to M_Z.
# If we start with lambda(Lambda) ~ 0.02-0.10 at ~10^{13-17} GeV,
# the running INCREASES lambda as we come down (because y_t^4 term).
# In fact, let me just DO that: pick a value of lambda(Lambda) and run it down.

print(f"\n=== APPROACH: RG running from NCG boundary condition ===")
print(f"From Step 1, we found:")
print(f"  sin^2(theta_W) = 3/8 at Lambda_NCG ≈ 1.03e13 GeV")
print(f"  At that scale: g_unified = 0.5443")
print(f"  y_t(Lambda_NCG) = 0.4935")

# At Lambda_NCG:
g_unif = 0.5443
yt_Lambda = 0.4935

# Compute a, b with top-quark dominance only
a_top = 3 * yt_Lambda**2
b_top = 3 * yt_Lambda**4
R_top = b_top / a_top**2
print(f"  a = 3*y_t^2 = {a_top:.6f}")
print(f"  b = 3*y_t^4 = {b_top:.6f}")
print(f"  R = b/a^2 = {R_top:.6f} (= 1/3 always for top-only)")

# With neutrino Yukawa (CCM assumption: y_nu ~ y_t at Lambda):
# This is the original CCM assumption from 2007.
y_nu = yt_Lambda  # Dirac condition
a_nu = y_nu**2 + 3 * yt_Lambda**2  # 1 generation nu + 3 colors top
b_nu = y_nu**4 + 3 * yt_Lambda**4
R_nu = b_nu / a_nu**2
print(f"\n  With y_nu = y_t:")
print(f"  a = {a_nu:.6f}")
print(f"  b = {b_nu:.6f}")
print(f"  R = b/a^2 = {R_nu:.6f} (= 1/4 for y_nu = y_t)")

# The various possible boundary conditions for lambda:
print(f"\n=== Possible lambda(Lambda_NCG) from spectral action ===")
formulas = {
    "lambda = g^2 * R": lambda g, R: g**2 * R,
    "lambda = g^2 * R / 2": lambda g, R: g**2 * R / 2,
    "lambda = g^2 * R / 4": lambda g, R: g**2 * R / 4,
    "lambda = pi^2 * R / (2*f_0) [f_0=2pi^2/g^2]": lambda g, R: g**2 * R / 4,
    "lambda = g^2 * R * 2": lambda g, R: g**2 * R * 2,
    "lambda = g^2 * R * 4": lambda g, R: g**2 * R * 4,
}

for label, func in formulas.items():
    for R_val, R_label in [(1/3, "top-only"), (1/4, "top+nu")]:
        lam = func(g_unif, R_val)
        m_H_tree = 246.22 * np.sqrt(2 * lam)
        print(f"  {label:50s}  R={R_val:.3f} ({R_label:8s}): lambda={lam:.5f}, m_H(tree)={m_H_tree:.1f} GeV")

# The KNOWN result is m_H ≈ 170-176 GeV from tree-level CCM.
# 170 GeV => lambda = 0.238
# This corresponds to lambda ≈ g^2 * R * factor
# 0.238 / (0.544^2 * 1/4) = 3.21
# So factor ≈ pi (3.14)? Or 4?

# AH WAIT. I think the issue is the NORMALIZATION of the trace.
# In NCG, the trace is over the FULL internal space:
#   3 generations x (2 for L/R) x (colored/uncolored)
# The factor a includes ALL generations, not just top.
# And the Yukawa trace is Tr(Y^dag Y) where Y is the FULL Yukawa matrix
# over the internal Hilbert space.
# For the original CCM with 3 generations of quarks and leptons + nu_R:
# a = Tr(Y_nu^dag Y_nu) + Tr(Y_e^dag Y_e) + 3*Tr(Y_u^dag Y_u) + 3*Tr(Y_d^dag Y_d)
# With top dominance AND y_nu ≈ y_t for the heaviest generation:
# a = y_nu^2 + 3*y_t^2  (sum over generations picks heaviest)
# Wait no — sum over ALL generations.
# a = sum_i (y_nu_i^2 + y_e_i^2 + 3*y_u_i^2 + 3*y_d_i^2)
# ≈ y_t^2 * (1 + 3) = 4*y_t^2  [with y_nu3 = y_t, others negligible]
# b = y_nu3^4 + 3*y_t^4 = 4*y_t^4
# R = 4*y_t^4 / (4*y_t^2)^2 = 4/(16) = 1/4

# DIFFERENT FORMULA: from van den Dungen & van Suijlekom review:
# The Higgs mass at the TREE level is:
# m_H^2 = 8*M_W^2 * (b/a^2) * (a * g^2) / g^2 ... no

# FROM FIRST PRINCIPLES, CAREFULLY:
# The spectral action (after expansion) contains:
#   (f_0/(2*pi^2)) * [-a*|phi|^2*R_scalar/6 + b*|phi|^4 + a*|D_mu phi|^2/2 + ...]
#   (using Euclidean signature conventions from CCM 2007)
# Here phi is the UNNORMALIZED scalar field from the inner fluctuations.
# After rescaling to get canonical kinetic term: phi_can = sqrt(f_0*a/(4*pi^2)) * phi
# Wait, the kinetic term has coefficient f_0*a/(4*pi^2), so:
# phi_can = sqrt(f_0*a/(4*pi^2)) * phi
# Then |phi|^4 = (4*pi^2/(f_0*a))^2 * |phi_can|^4
# And the quartic coefficient becomes:
# lambda = f_0*b/(2*pi^2) * (4*pi^2/(f_0*a))^2 = 8*pi^2*b/(f_0*a^2)

# With f_0 = 2*pi^2/g^2:
# lambda = 8*pi^2*b / ((2*pi^2/g^2)*a^2) = 4*g^2*b/a^2 = 4*g^2*R

print(f"\n=== CORRECTED: lambda = 4*g^2*R ===")
for R_val, R_label in [(1/3, "top-only"), (1/4, "top+nu")]:
    lam = 4 * g_unif**2 * R_val
    m_H_tree = 246.22 * np.sqrt(2 * lam)
    print(f"  R={R_val:.4f} ({R_label}): lambda={lam:.5f}, m_H(tree)={m_H_tree:.1f} GeV")

# With R=1/4: lambda = 4*0.296*0.25 = 0.296, m_H = 246*sqrt(0.592) = 189 GeV. Closer!
# With R=1/3: lambda = 4*0.296*0.333 = 0.395, m_H = 246*sqrt(0.789) = 219 GeV. Too big.

# Hmm, 189 is closer to 170 but not exact. Let me try:
# lambda = 2*g^2*R:
print(f"\n=== lambda = 2*g^2*R ===")
for R_val, R_label in [(1/3, "top-only"), (1/4, "top+nu")]:
    lam = 2 * g_unif**2 * R_val
    m_H_tree = 246.22 * np.sqrt(2 * lam)
    print(f"  R={R_val:.4f} ({R_label}): lambda={lam:.5f}, m_H(tree)={m_H_tree:.1f} GeV")

# lambda = 3*g^2*R:
print(f"\n=== lambda = 3*g^2*R ===")
for R_val, R_label in [(1/3, "top-only"), (1/4, "top+nu")]:
    lam = 3 * g_unif**2 * R_val
    m_H_tree = 246.22 * np.sqrt(2 * lam)
    print(f"  R={R_val:.4f} ({R_label}): lambda={lam:.5f}, m_H(tree)={m_H_tree:.1f} GeV")

# 170 GeV:
lam_170 = 170**2 / (2 * 246.22**2)
factor_170 = lam_170 / (g_unif**2 * 0.25)  # R=1/4
print(f"\n=== Reverse-engineer: 170 GeV needs ===")
print(f"  lambda = {lam_170:.5f}")
print(f"  factor * g^2 * R = {factor_170:.4f} * g^2 * R  (with R=1/4)")
print(f"  factor = {factor_170:.4f}")

# 4/pi ≈ 1.27, pi/2 ≈ 1.57, no.
# 170/80 ≈ 2.12 = sqrt(4.5) ≈ sqrt(9/2)?
# m_H^2 / M_W^2 = 170^2/80.4^2 = 4.47 ≈ 9/2

# BINGO: m_H = sqrt(2) * 2*M_W = 2*sqrt(2)*80.4 = 227? No.
# m_H = m_t (at tree level, in some papers the prediction is m_H = m_t ≈ 173)
print(f"\n=== Is the tree-level prediction just m_H ≈ m_t? ===")
print(f"  m_t(pole) = 172.76 GeV")
print(f"  Close to 170 but not exact.")

# The ACTUAL CCM 2007 result (from their paper):
# Using m_t = 180 GeV (the value used in 2007), they got m_H ≈ 170 GeV.
# So it's NOT m_H = m_t. It's a relation that with 2007 inputs gives 170.

# In the 2012 "Resilience" paper, they found m_H ≈ 170 GeV with the ORIGINAL
# boundary condition, and showed that the spectral action is "resilient" — the
# observed 125 GeV can be accommodated by adding a real scalar singlet sigma.

# The 2012 paper is key. Let me state the DEFINITIVE formula:
# From Chamseddine-Connes-van Suijlekom (2013), "Beyond the Spectral Standard Model":
# The Higgs mass from the spectral action (without running) is:
# m_H^2 = (2*f_2*Lambda^2 / f_0) * (1 - (b*f_2*Lambda^2)/(a^2*f_0*pi^2) + ...)
# This is the tree-level WITH the scalar mass parameter.
# At the CUTOFF, the NCG boundary condition is basically lambda and mu^2.

# ENOUGH with the tree-level formula. The CLAIM to verify is about RUNNING.
# The claim: "NCG predicts m_H = 124.5 GeV when using running Yukawa couplings at Lambda = M_Pl"
# This means: take the NCG boundary condition lambda(Lambda),
# RG-run down to the EW scale, and compute m_H.

# The clean computational approach:
# 1. Use the NCG boundary condition at some scale Lambda
# 2. Run ALL couplings from Lambda to M_Z
# 3. Compute m_H

# The NCG boundary condition is:
# lambda(Lambda) = numerical_factor * g^2(Lambda) * b/a^2

# Given the literature, the factor that reproduces m_H ≈ 170 GeV tree-level
# with m_t = 173 is clearly NOT a simple small number.

# Actually, the simplest statement (see Sakellariadou review, eq 4.8):
# y_t^2(Lambda) = 4*g_3^2(Lambda) * (a^2/b)  [gauge-Yukawa relation]
# This gives: y_t = 2*g_3 * a/sqrt(b)
# With a=4*y_t^2 and b=4*y_t^4:
# y_t = 2*g_3 * 4*y_t^2 / sqrt(4*y_t^4) = 2*g_3 * 4*y_t^2/(2*y_t^2) = 4*g_3
# That gives y_t = 4*g_3 ≈ 4*0.54 = 2.16 which is perturbatively insane.

# OK the CORRECT simple formula from the spectral action is simply:
# At the unification scale Lambda:
# lambda(Lambda) = R * g^2(Lambda)  ...times some O(1) factor from the algebra.

# Let me just parametrize it and sweep, then RUN.
print(f"\n" + "="*60)
print(f"=== SWEEP: Try different lambda(Lambda) boundary conditions ===")
print(f"=== and RG-run down to find which gives m_H = 125.25 GeV ===")
print(f"="*60)

# This tells us what boundary condition is NEEDED, regardless of which
# normalization convention gives it.

# We need to run the RGE from Lambda_NCG down to M_Z.
from scipy.integrate import solve_ivp

M_Z = 91.1876
M_Pl = 2.435e18
Lambda_NCG = 1.03e13  # where sin^2(theta_W) = 3/8

# Use the couplings at Lambda_NCG from Step 1
g1_L = 0.5443
g2_L = 0.5443
g3_L = 0.5841
yt_L = 0.4935

def beta_SM_1loop(t, y):
    g1, g2, g3, yt, lam = y
    g1sq = g1**2
    g2sq = g2**2
    g3sq = g3**2
    ytsq = yt**2
    b1, b2, b3 = 41.0/10.0, -19.0/6.0, -7.0
    dg1 = g1**3 * b1 / (16 * np.pi**2)
    dg2 = g2**3 * b2 / (16 * np.pi**2)
    dg3 = g3**3 * b3 / (16 * np.pi**2)
    dyt = yt / (16 * np.pi**2) * (
        (9.0/2.0) * ytsq - (17.0/20.0) * g1sq - (9.0/4.0) * g2sq - 8.0 * g3sq
    )
    dlam = 1.0 / (16 * np.pi**2) * (
        24 * lam**2 - lam * ((9.0/5.0) * g1sq + 9.0 * g2sq)
        + 12.0 * lam * ytsq
        + (27.0/200.0) * g1sq**2 + (9.0/20.0) * g1sq * g2sq + (9.0/8.0) * g2sq**2
        - 6.0 * ytsq**2
    )
    return [dg1, dg2, dg3, dyt, dlam]

# Run from Lambda_NCG DOWN to M_t, then to M_Z
t_Lambda = np.log(Lambda_NCG / M_Z)
t_Mt = np.log(172.76 / M_Z)

print(f"\nBoundary conditions at Lambda_NCG = {Lambda_NCG:.2e} GeV:")
print(f"  g1 = {g1_L}, g2 = {g2_L}, g3 = {g3_L}, y_t = {yt_L}")

lambda_trials = np.linspace(0.001, 0.50, 500)
m_H_results = []

for lam_trial in lambda_trials:
    y0 = [g1_L, g2_L, g3_L, yt_L, lam_trial]
    # Run DOWN from Lambda to M_t
    sol = solve_ivp(beta_SM_1loop, (t_Lambda, t_Mt), y0, method='RK45',
                    rtol=1e-10, atol=1e-12)
    if sol.success:
        lam_Mt = sol.y[4, -1]
        m_H = v * np.sqrt(2 * lam_Mt) if lam_Mt > 0 else 0
        m_H_results.append((lam_trial, lam_Mt, m_H))

print(f"\n{'lambda(Lambda)':>15s}  {'lambda(M_t)':>12s}  {'m_H (GeV)':>10s}")
print("-" * 42)
# Print a selection
for lam_trial, lam_Mt, m_H in m_H_results[::25]:
    print(f"{lam_trial:15.5f}  {lam_Mt:12.6f}  {m_H:10.2f}")

# Find which lambda(Lambda) gives m_H = 125.25
target_mH = 125.25
best_idx = min(range(len(m_H_results)), key=lambda i: abs(m_H_results[i][2] - target_mH))
lam_best, lam_Mt_best, mH_best = m_H_results[best_idx]
print(f"\n=== m_H ≈ {target_mH} GeV requires lambda(Lambda_NCG) ≈ {lam_best:.5f} ===")
print(f"  lambda(M_t) = {lam_Mt_best:.6f}")
print(f"  m_H = {mH_best:.2f} GeV")

# Compare with NCG prediction lambda(Lambda) = g^2*R * numerical_factor
print(f"\n  For reference: g^2(Lambda_NCG) * R(top) = {g_unif**2 * 1/3:.5f}")
print(f"  For reference: g^2(Lambda_NCG) * R(nu) = {g_unif**2 * 1/4:.5f}")
print(f"  Ratio needed/predicted(top): {lam_best/(g_unif**2/3):.4f}")
print(f"  Ratio needed/predicted(nu): {lam_best/(g_unif**2/4):.4f}")

# Now also check: what about running from M_Pl instead?
print(f"\n" + "="*60)
print(f"=== ALSO: Run from M_Pl with various lambda(M_Pl) ===")
print(f"="*60)

# At M_Pl from Step 1:
g1_Pl = 0.604939
g2_Pl = 0.508245
g3_Pl = 0.498244
yt_Pl = 0.411945

t_Pl = np.log(M_Pl / M_Z)

lambda_trials_Pl = np.linspace(-0.05, 0.30, 700)
m_H_results_Pl = []

for lam_trial in lambda_trials_Pl:
    y0 = [g1_Pl, g2_Pl, g3_Pl, yt_Pl, lam_trial]
    sol = solve_ivp(beta_SM_1loop, (t_Pl, t_Mt), y0, method='RK45',
                    rtol=1e-10, atol=1e-12)
    if sol.success:
        lam_Mt = sol.y[4, -1]
        m_H = v * np.sqrt(2 * abs(lam_Mt)) if lam_Mt > 0 else -v * np.sqrt(2 * abs(lam_Mt))
        m_H_results_Pl.append((lam_trial, lam_Mt, m_H))

print(f"\n{'lambda(M_Pl)':>15s}  {'lambda(M_t)':>12s}  {'m_H (GeV)':>10s}")
print("-" * 42)
for lam_trial, lam_Mt, m_H in m_H_results_Pl[::35]:
    print(f"{lam_trial:15.5f}  {lam_Mt:12.6f}  {m_H:10.2f}")

best_idx_Pl = min(range(len(m_H_results_Pl)), key=lambda i: abs(m_H_results_Pl[i][2] - target_mH))
lam_best_Pl, lam_Mt_best_Pl, mH_best_Pl = m_H_results_Pl[best_idx_Pl]
print(f"\n=== m_H ≈ {target_mH} GeV requires lambda(M_Pl) ≈ {lam_best_Pl:.5f} ===")
print(f"  lambda(M_t) = {lam_Mt_best_Pl:.6f}")
print(f"  m_H = {mH_best_Pl:.2f} GeV")

# KEY CHECK: what if lambda(M_Pl) = 0 (near-criticality)?
# The SM is known to have lambda ≈ 0 near M_Pl (vacuum stability boundary)
idx_zero = min(range(len(m_H_results_Pl)), key=lambda i: abs(m_H_results_Pl[i][0]))
lam_zero, lam_Mt_zero, mH_zero = m_H_results_Pl[idx_zero]
print(f"\n=== lambda(M_Pl) ≈ 0: m_H = {mH_zero:.2f} GeV ===")
print(f"  (This is the 'near-criticality' prediction)")
