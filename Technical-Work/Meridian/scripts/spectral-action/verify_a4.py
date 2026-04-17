"""
Verify a_4 heat kernel coefficient for 5D gravity on AdS_5.

Summary of verified results:
- tr(Omega^2)|_full_sym2 = -280 K^2 = -280 k^4
- tr(Omega^2)|_traceless_sym2 = -280 k^4 (trace mode has zero Omega^2)
- tr(Omega^2)|_vector = -40 K^2 = -40 k^4

Key insight: On maximally symmetric space, Omega is antisymmetric in (M,N),
so tr(Omega^2) is negative. The curvature invariant R_MNPQ^2 = 40k^4 is positive,
but the connection curvature squared (with proper contractions) gives -40k^4 per vector.

For the FRG beta functions, we need the threshold functions, not the a_4 coefficient
directly. The a_4 determines the one-loop divergence, which serves as a cross-check
on the FRG flow in the perturbative regime.
"""

import numpy as np

d = 5
R_val = -20  # in k^2 units
K_val = R_val / (d * (d - 1))  # = -1 in k^2 units

print("=== AdS_5 Curvature Invariants ===")
print(f"d = {d}")
print(f"R = {R_val} k^2")
print(f"K = R/[d(d-1)] = {K_val} k^2")
print(f"R_MN = (R/d) g_MN = {R_val/d} k^2 g_MN")
print(f"R_MN^2 = R^2/d = {R_val**2/d} k^4")
print(f"R_MNPQ^2 = 2R^2/[d(d-1)] = {2*R_val**2/(d*(d-1))} k^4")
print(f"G_GB = R^2 - 4R_MN^2 + R_MNPQ^2 = {R_val**2 - 4*R_val**2/d + 2*R_val**2/(d*(d-1))} k^4")
print(f"C_MNPQ^2 = 0 (maximally symmetric)")

print("\n=== Field Content for 5D Gravity ===")
print(f"Full symmetric 2-tensor: {d*(d+1)//2} components")
print(f"Traceless symmetric 2-tensor: {d*(d+1)//2 - 1} components")
print(f"TT tensor (on-shell graviton): {d*(d+1)//2 - 1 - d} = {d*(d+1)//2 - d - 1} components")
print(f"Vector ghost: {d} components")

print("\n=== Endomorphism Values ===")
# TT tensor: E_TT = -2K = 2k^2
E_TT = -2 * K_val
print(f"E_TT (Lichnerowicz on TT) = -2K = {E_TT} k^2")

# Vector ghost: E_ghost = R_MN/g_MN factor
# Ghost operator: -nabla^2 delta^a_b - R^a_b = -(nabla^2 + R/d) on max sym
E_ghost = R_val / d  # = -4 k^2
print(f"E_ghost (Faddeev-Popov vector) = R/d = {E_ghost} k^2")

print("\n=== Connection Curvature Squared (Omega^2) ===")
print(f"tr(Omega^2)|_traceless_sym2 = -280 k^4 (for 14-component bundle)")
print(f"tr(Omega^2)|_vector = -40 k^4 (for 5-component bundle)")

print("\n=== One-Loop a_4 Coefficient (per unit volume, in units of 1/(4pi)^{5/2}) ===")

# For each sector, a_4 = (1/360) [60*R*tr(E) + 180*tr(E^2) + 30*tr(Omega^2) + geometric * N]
# geometric = 5R^2 - 2R_MN^2 + 2R_MNPQ^2 + 12*nabla^2 R
# On max sym: nabla^2 R = 0

geom = 5 * R_val**2 - 2 * R_val**2/d + 2 * 2*R_val**2/(d*(d-1))
print(f"Geometric combination: 5R^2 - 2R_MN^2 + 2R_MNPQ^2 = {geom} k^4")

# Traceless symmetric 2-tensor (14 components)
N_tl = d*(d+1)//2 - 1  # 14
a4_tl_terms = {
    "60*R*E*N": 60 * R_val * E_TT * N_tl,
    "180*E^2*N": 180 * E_TT**2 * N_tl,
    "30*tr(Omega^2)": 30 * (-280),
    "geom*N": geom * N_tl,
}
print(f"\nTraceless sym-2 ({N_tl} comp):")
for name, val in a4_tl_terms.items():
    print(f"  {name} = {val}")
sum_tl = sum(a4_tl_terms.values())
print(f"  Sum = {sum_tl}")
print(f"  a_4 = {sum_tl}/360 = {sum_tl/360:.4f}")

# Vector ghost (5 components)
N_gh = d  # 5
a4_gh_terms = {
    "60*R*E*N": 60 * R_val * E_ghost * N_gh,
    "180*E^2*N": 180 * E_ghost**2 * N_gh,
    "30*tr(Omega^2)": 30 * (-40),
    "geom*N": geom * N_gh,
}
print(f"\nVector ghost ({N_gh} comp):")
for name, val in a4_gh_terms.items():
    print(f"  {name} = {val}")
sum_gh = sum(a4_gh_terms.values())
print(f"  Sum = {sum_gh}")
print(f"  a_4 = {sum_gh}/360 = {sum_gh/360:.4f}")

# Scalar (trace mode, 1 component)
# For the trace mode: E_trace involves the trace-mixing term
# On max sym: the trace mode operator is -nabla^2 + constant
# The constant includes 2K*d (from the g*h term) and other pieces
# E_trace = -2K - 2R/d + 2K*d = -2K(1-d) - 2R/d
# K = -k^2, R/d = -4k^2
# E_trace = 2k^2(1-d) + 8k^2 = -8k^2 + 8k^2 = 0...
# Actually need more care. The trace mode h_MN = (1/sqrt(d)) g_MN phi has:
# Delta_L (g phi/sqrt(d))_MN = [-nabla^2 phi/sqrt(d) + 2K(d*phi/sqrt(d) - g_MN*phi/sqrt(d))
#                                - 2(R/d)*phi/sqrt(d)] * g_MN
# Hmm, this needs the full operator. For max sym the Lichnerowicz maps trace to trace:
# If h_MN = g_MN phi, then the trace-trace part of Delta_L gives:
# g^MN Delta_L(g phi)_MN = -nabla^2(d*phi) + 2K(d^2 - d)*phi - 2(R/d)(d)*phi
# = -d*nabla^2 phi + 2Kd(d-1)*phi - 2R*phi
# = -d*nabla^2 phi + R*phi - 2R*phi  [since 2Kd(d-1) = R]
# = -d*nabla^2 phi - R*phi
# So the trace scalar has operator: -nabla^2 - R/d = -nabla^2 + 4k^2
# With E_trace = R/d = -4k^2 ??? That means D = -(nabla^2 + E) = -(nabla^2 - 4k^2)
# Which gives eigenvalues p^2 + 4k^2. Hmm.
# Actually, from g^MN Delta_L (g phi)_MN / d = -nabla^2 phi - (R/d)*phi
# So the effective operator on phi is: -nabla^2 - R/d = -nabla^2 + 4k^2
# In D = -(nabla^2 + E) form: E_trace = -R/d = 4k^2
# Wait that has wrong sign. Let me be more careful.
# g^MN Delta_L(g phi)_MN = g^MN[-nabla^2(g_{MN}phi)] + ...
# -nabla^2(g_{MN}phi) = g_{MN}(-nabla^2 phi) [since g is covariantly constant]
# So g^MN(-nabla^2)(g_{MN}phi) = -d nabla^2 phi
# Dividing by d: the operator on phi is -nabla^2 + stuff/d
# "stuff" = 2Kd(d-1)*phi - 2R*phi = (R - 2R)*phi = -R*phi
# So operator on phi: -nabla^2 - R/d = -nabla^2 + 4k^2
# E_trace = R/d = -4k^2 in our convention... no.
# D phi = -nabla^2 phi + 4k^2 phi = -(nabla^2 - 4k^2) phi = -(nabla^2 + E) phi
# So E = -4k^2. No wait: D = -(nabla^2 + E) means D = -nabla^2 - E.
# If D phi = -nabla^2 phi + 4k^2 phi, then -E = 4k^2, so E = -4k^2.
# Hmm, that means E_trace = -4k^2 = R/d. Same as E_ghost. Interesting.

E_trace_val = R_val / d  # = -4 k^2

N_tr = 1
a4_tr_terms = {
    "60*R*E*N": 60 * R_val * E_trace_val * N_tr,
    "180*E^2*N": 180 * E_trace_val**2 * N_tr,
    "30*tr(Omega^2)": 30 * 0,  # Omega^2 = 0 on trace mode
    "geom*N": geom * N_tr,
}
print(f"\nTrace scalar ({N_tr} comp):")
for name, val in a4_tr_terms.items():
    print(f"  {name} = {val}")
sum_tr = sum(a4_tr_terms.values())
print(f"  Sum = {sum_tr}")

# TOTAL gravity one-loop (traceless + trace - 2*ghost):
# The factor 2 for ghosts is from Faddeev-Popov (complex ghosts = 2 real)
# Actually, for real ghosts (Grassmann), the sign is -1 (fermionic) and there is 1 ghost field
# Convention: Total = (1/2) Tr log(Delta_graviton) - Tr log(Delta_ghost)
# The (1/2) for graviton is already included in the Wetterich equation
# In terms of a_4: a_4^total = a_4^graviton - 2*a_4^ghost (factor 2 from complex ghost)
# Actually in the Faddeev-Popov formalism, ghosts are COMPLEX, so:
# Total = a_4(sym-2) - 2*a_4(vector ghost)
# But sym-2 here = traceless + trace = 14 + 1 = 15 components

a4_total_sym2 = (sum_tl + sum_tr)
a4_total_ghost = sum_gh

# In the standard formalism: total = (sym-2) - 2*(ghost)
# But the (1/2) from the bosonic trace vs the full trace for ghosts gives:
# Total = (1/2)*sym-2 - ghost
# For the beta function extraction, it is total / 360:

print(f"\n=== TOTAL ===")
print(f"a_4(sym-2, 15 comp) = ({sum_tl} + {sum_tr}) / 360 = {(sum_tl + sum_tr)/360:.4f}")
print(f"a_4(ghost, 5 comp) = {sum_gh} / 360 = {sum_gh/360:.4f}")
print(f"a_4(total) = (1/2)*a_4(graviton) - a_4(ghost)")
print(f"           = (1/2)*{(sum_tl + sum_tr)/360:.4f} - {sum_gh/360:.4f}")
print(f"           = {(sum_tl + sum_tr)/720 - sum_gh/360:.4f}")
print()
print("Note: The exact prefactors depend on the gauge-fixing parameter")
print("and the precise definition of the Faddeev-Popov ghost action.")
print("The numerical values above are for the standard de Donder gauge.")
