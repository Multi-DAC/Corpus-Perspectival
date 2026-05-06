"""
Compute tr(Omega_MN Omega^MN) for various tensor decompositions on
a maximally symmetric d-dimensional space.

R_ABCD = K (g_AC g_BD - g_AD g_BC)
K = R / [d(d-1)]
For AdS_5: R = -20k^2, K = -k^2

The connection curvature on symmetric 2-tensors:
(Omega_{MN} h)_{ab} = R^c_{MaN} h_{cb} + R^c_{MbN} h_{ac}
                    = K [2 delta_{MN} h_{ab} - delta_{Ma} h_{Nb} - delta_{Mb} h_{Na}]
"""

import numpy as np

d = 5
K_val = 1.0  # compute in units of K^2, then multiply by k^4

# Symmetric pairs (a,b) with a <= b
pairs = [(i, j) for i in range(d) for j in range(i, d)]
N_pairs = len(pairs)
print(f"d = {d}, N_pairs = {N_pairs}")

def build_omega(M, N, d, pairs):
    """Build Omega_{MN} matrix on symmetric 2-tensor space."""
    n = len(pairs)
    Omega = np.zeros((n, n))
    for idx1, (a, b) in enumerate(pairs):
        for idx2, (c, e) in enumerate(pairs):
            val = 0.0
            # Term: 2 * delta_{MN} * h_{ab}
            if (a == c and b == e) or (a == e and b == c):
                val += 2 * (1 if M == N else 0)
            # Term: -delta_{Ma} * h_{Nb}
            if M == a:
                if (N == c and b == e) or (N == e and b == c):
                    val -= 1.0
            # Term: -delta_{Mb} * h_{Na}
            if M == b:
                if (a == c and N == e) or (a == e and N == c):
                    val -= 1.0
            Omega[idx1, idx2] = val
    return Omega

# Compute tr(Omega_MN Omega^MN) for full symmetric 2-tensor
total_full = 0.0
for M in range(d):
    for N in range(d):
        Om = build_omega(M, N, d, pairs)
        total_full += np.trace(Om @ Om)

print(f"\ntr(Omega^2)|_full_sym2 = {total_full} K^2")
print(f"  = {total_full} k^4  (since K^2 = k^4)")

# Build traceless projector
P_TL = np.eye(N_pairs)
for idx1, (a, b) in enumerate(pairs):
    for idx2, (c, e) in enumerate(pairs):
        if a == b and c == e:
            P_TL[idx1, idx2] -= 1.0 / d

rank_TL = np.linalg.matrix_rank(P_TL, tol=1e-10)
print(f"\nTraceless projector rank: {rank_TL}")

# tr(Omega^2) on traceless symmetric 2-tensors
total_traceless = 0.0
for M in range(d):
    for N in range(d):
        Om = build_omega(M, N, d, pairs)
        POm = P_TL @ Om @ P_TL
        total_traceless += np.trace(POm @ POm)

print(f"tr(Omega^2)|_traceless_sym2 = {total_traceless:.4f} K^2")

# Trace sector contribution
total_trace = total_full - total_traceless
print(f"tr(Omega^2)|_trace = {total_trace:.4f} K^2")

# Expected trace: 4(d-1)^2/d
expected_trace = 4 * (d-1)**2 / d
print(f"Expected trace sector: 4(d-1)^2/d = {expected_trace:.4f} K^2")

# For the ghost (vector field):
# (Omega_{MN})^a_b = R^a_{bMN} = K(delta^a_b delta_{MN} - delta^a_N delta_{bM})
# tr(Omega_MN Omega^MN)|_vec = sum_{M,N} sum_a (Omega_{MN})^a_b (Omega^{MN})^b_a
total_vec = 0.0
for M in range(d):
    for N in range(d):
        Om_vec = np.zeros((d, d))
        for a in range(d):
            for b in range(d):
                Om_vec[a, b] = (1 if a == b else 0) * (1 if M == N else 0) - (1 if a == N else 0) * (1 if b == M else 0)
        total_vec += np.trace(Om_vec @ Om_vec)

print(f"\ntr(Omega^2)|_vector = {total_vec} K^2")
print(f"Should equal R_MNPQ^2 = 2d(d-1) K^2 = {2*d*(d-1)} K^2")

# Scalar (no indices): Omega = 0
print(f"tr(Omega^2)|_scalar = 0")

# Summary
print(f"\n=== SUMMARY for d={d}, AdS_5 ===")
print(f"R = -20k^2, K = -k^2, K^2 = k^4")
print(f"R_MNPQ R^MNPQ = 40 k^4")
print(f"")
print(f"tr(Omega^2) contributions (in k^4):")
print(f"  Full symmetric 2-tensor (15 comp): {total_full}")
print(f"  Traceless symmetric 2-tensor (14 comp): {total_traceless:.1f}")
print(f"  Trace (scalar, 1 comp): {total_trace:.1f}")
print(f"  Vector (ghost, 5 comp): {total_vec}")
print(f"  Scalar (0 comp Omega): 0")

print(f"\n=== a_4 COEFFICIENT (bulk, per unit volume) ===")
# For the full graviton sector (traceless sym-2 minus vector ghost):
# a_4 = (1/360) * [geometric terms + Omega terms + E terms]
#
# Traceless sector (14 components):
R_val = -20  # in k^2 units
E_traceless = 2  # k^2 (from Lichnerowicz on max sym, E = -2K = 2k^2)
N_traceless = 14

t1_tl = 60 * R_val * E_traceless * N_traceless
t2_tl = 180 * E_traceless**2 * N_traceless
t3_tl = 30 * total_traceless
t4_tl = (5 * R_val**2 - 2 * 80 + 2 * 40) * N_traceless

print(f"Traceless symmetric 2-tensor sector (N={N_traceless}):")
print(f"  60*R*E*N = {t1_tl}")
print(f"  180*E^2*N = {t2_tl}")
print(f"  30*tr(Omega^2) = {t3_tl:.1f}")
print(f"  (5R^2-2R_MN^2+2R_MNPQ^2)*N = {t4_tl}")
sum_tl = t1_tl + t2_tl + t3_tl + t4_tl
print(f"  Total (360 * (4pi)^{d}/2 * a_4) = {sum_tl:.1f}")

# Vector ghost sector (5 components):
# For vector ghost: E_ghost = R_MN type correction
# On max sym: the ghost operator is -nabla^2 delta^a_b - R^a_b = -nabla^2 - R/d
# So E_ghost = R/d = -4k^2
E_ghost = R_val / d
N_ghost = d

t1_gh = 60 * R_val * E_ghost * N_ghost
t2_gh = 180 * E_ghost**2 * N_ghost
t3_gh = 30 * total_vec
t4_gh = (5 * R_val**2 - 2 * 80 + 2 * 40) * N_ghost

print(f"\nVector ghost sector (N={N_ghost}):")
print(f"  60*R*E*N = {t1_gh}")
print(f"  180*E^2*N = {t2_gh}")
print(f"  30*tr(Omega^2) = {t3_gh}")
print(f"  (5R^2-2R_MN^2+2R_MNPQ^2)*N = {t4_gh}")
sum_gh = t1_gh + t2_gh + t3_gh + t4_gh
print(f"  Total = {sum_gh}")

print(f"\nCombined a_4 (graviton - ghost) proportional to:")
print(f"  {sum_tl:.1f} - {sum_gh:.1f} = {sum_tl - sum_gh:.1f}")
print(f"  a_4 = {(sum_tl - sum_gh)/360:.4f} / (4pi)^(5/2)")
