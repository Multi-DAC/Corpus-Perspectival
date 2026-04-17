#!/usr/bin/env python3
"""
Analytic Torsion on the Fermat Cubic dP_6 — Version 3
======================================================
Phase 26 — Clean rewrite with correct approach.

Key fixes over v1/v2:
  1. All 3 cube root branches (each chart only covers 1/3 with principal branch)
  2. Simple monomial basis with EXACT analytic derivatives
  3. Efficient assembly via pre-computed weight matrices
  4. Correct volume normalization

Surface: S = {x^3 + y^3 + z^3 + 1 = 0} in CP^3, chart x_3=1
         Coords (a,b) = (x_0, x_1), solved x_2 = c(a,b)
         Three branches: c_k = zeta^k * w^{1/3}, k=0,1,2, zeta=e^{2pi*i/3}
"""

import numpy as np
from scipy.linalg import eigh
from math import pi, log, sqrt
import json, sys, time

sys.stdout.reconfigure(encoding='utf-8')

# ============================================================
# CONFIGURATION
# ============================================================

N_MC = 300000         # MC points in domain (900K surface points with 3 branches)
K_MAX = 6             # Max total degree of monomials (reduced for conditioning)
DOMAIN_R = 5.0        # Domain radius in each real coordinate
RNG_SEED = 2026
ZETA3 = np.exp(2j * pi / 3)  # Primitive cube root of unity

rng = np.random.default_rng(RNG_SEED)

print("=" * 72)
print("ANALYTIC TORSION ON dP_6 — VERSION 3")
print("Single chart, 3 branches, exact monomial derivatives")
print("=" * 72)


# ============================================================
# STAGE 1: SAMPLE SURFACE WITH ALL 3 BRANCHES
# ============================================================

print("\n" + "=" * 72)
print("STAGE 1: SURFACE SAMPLING (3 BRANCHES)")
print("=" * 72)

t0 = time.time()

# Sample (a, b) uniformly in [-R, R]^4
u = rng.uniform(-DOMAIN_R, DOMAIN_R, (4, N_MC))
a_raw = u[0] + 1j * u[1]
b_raw = u[2] + 1j * u[3]

w_raw = -1.0 - a_raw**3 - b_raw**3
valid = np.abs(w_raw) > 0.01
a_base = a_raw[valid]
b_base = b_raw[valid]
w_base = w_raw[valid]
N_valid = len(a_base)

# Principal cube root
c_principal = np.abs(w_base)**(1/3) * np.exp(1j * np.angle(w_base) / 3)

# All 3 branches
branches_c = [c_principal, ZETA3 * c_principal, ZETA3**2 * c_principal]

# Tile (a, b) for 3 branches
a_all = np.tile(a_base, 3)
b_all = np.tile(b_base, 3)
c_all = np.concatenate(branches_c)
N_total = len(a_all)

print(f"  Domain: [-{DOMAIN_R}, {DOMAIN_R}]^4")
print(f"  Raw samples: {N_MC}, valid: {N_valid} ({100*N_valid/N_MC:.1f}%)")
print(f"  With 3 branches: {N_total} total points")


# ============================================================
# STAGE 2: METRIC COMPUTATION
# ============================================================

print("\n" + "=" * 72)
print("STAGE 2: INDUCED FUBINI-STUDY METRIC")
print("=" * 72)

# Homogeneous coords: X = (a, b, c, 1) in chart x_3 = 1
# P = |X|^2 = |a|^2 + |b|^2 + |c|^2 + 1
P = np.abs(a_all)**2 + np.abs(b_all)**2 + np.abs(c_all)**2 + 1.0
P2 = P**2

# Derivatives: dc/da = -a^2/c^2, dc/db = -b^2/c^2
c2 = c_all**2
c2_safe = np.where(np.abs(c2) > 1e-12, c2, 1.0)
dc_da = np.where(np.abs(c2) > 1e-12, -a_all**2 / c2_safe, 0.0)
dc_db = np.where(np.abs(c2) > 1e-12, -b_all**2 / c2_safe, 0.0)

# Jacobian: J = [[1, 0], [0, 1], [dc/da, dc/db], [0, 0]]
# (rows = x_0, x_1, x_2, x_3; cols = da, db)
# J^dag J:
JdJ_11 = 1.0 + np.abs(dc_da)**2
JdJ_12 = np.conj(dc_da) * dc_db
JdJ_22 = 1.0 + np.abs(dc_db)**2

# J^dag X_bar (X = (a, b, c, 1)):
JdXb_1 = np.conj(a_all) + np.conj(dc_da) * np.conj(c_all)
JdXb_2 = np.conj(b_all) + np.conj(dc_db) * np.conj(c_all)

# X^T J:
XJ_1 = a_all + c_all * dc_da
XJ_2 = b_all + c_all * dc_db

# Induced metric: g_{ab_bar} = JdJ/P - JdXb * XJ / P^2
g11 = JdJ_11 / P - JdXb_1 * XJ_1 / P2
g12 = JdJ_12 / P - JdXb_1 * XJ_2 / P2
g21 = np.conj(g12)  # Hermitian
g22 = JdJ_22 / P - JdXb_2 * XJ_2 / P2

det_g = (g11 * g22 - g12 * g21).real

# Filter: positive definite
good = (det_g > 1e-15) & (g11.real > 0) & np.isfinite(det_g)
a_all = a_all[good]; b_all = b_all[good]; c_all = c_all[good]
P = P[good]; det_g = det_g[good]
g11 = g11[good]; g12 = g12[good]; g21 = g21[good]; g22 = g22[good]
N_total = len(a_all)

# Inverse metric
det_safe = np.where(det_g > 1e-20, det_g, 1.0)
ginv11 = (g22 / det_safe).real
ginv12 = -g12 / det_safe
ginv21 = -g21 / det_safe
ginv22 = (g11 / det_safe).real

# MC weights: det(g) * domain_vol / N_MC (per-branch)
domain_vol = (2 * DOMAIN_R)**4
weights = det_g * domain_vol / (3 * N_MC)  # 3 branches → divide by 3*N_MC

# Volume estimate
vol_estimate = np.sum(weights)
vol_exact = 3.0 * pi**2 / 2.0  # deg(S) * Vol(CP^2) = 3 * pi^2/2
vol_ratio = vol_estimate / vol_exact

print(f"  Points after filtering: {N_total}")
print(f"  Estimated Vol(S) = {vol_estimate:.4f}")
print(f"  Exact Vol(dP_6, FS) = 3*pi^2/2 = {vol_exact:.4f}")
print(f"  Ratio: {vol_ratio:.4f}")
print(f"  Time: {time.time()-t0:.1f}s")

if 0.85 < vol_ratio < 1.15:
    print("  GOOD: Volume within 15% of exact")
elif 0.7 < vol_ratio < 1.3:
    print("  OK: Volume within 30% — usable but not ideal")
else:
    print("  WARNING: Volume far from exact — results unreliable")


# ============================================================
# STAGE 3: MONOMIAL BASIS
# ============================================================

print("\n" + "=" * 72)
print(f"STAGE 3: MONOMIAL BASIS (degree <= {K_MAX})")
print("=" * 72)

# Basis: a^p * abar^q * b^r * bbar^s with p+q+r+s <= K_MAX
basis_idx = []
for total in range(K_MAX + 1):
    for p in range(total + 1):
        for q in range(total - p + 1):
            for r in range(total - p - q + 1):
                s = total - p - q - r
                basis_idx.append((p, q, r, s))

N_basis = len(basis_idx)
print(f"  Basis size: {N_basis}")

# Index lookup: (p,q,r,s) -> l
idx_to_l = {}
for l, (p, q, r, s) in enumerate(basis_idx):
    idx_to_l[(p, q, r, s)] = l

# Precompute powers
ab = np.conj(a_all)
bb = np.conj(b_all)

max_p = K_MAX
a_pow = [np.ones(N_total, dtype=complex)]
ab_pow = [np.ones(N_total, dtype=complex)]
b_pow = [np.ones(N_total, dtype=complex)]
bb_pow = [np.ones(N_total, dtype=complex)]
for k in range(1, max_p + 1):
    a_pow.append(a_pow[-1] * a_all)
    ab_pow.append(ab_pow[-1] * ab)
    b_pow.append(b_pow[-1] * b_all)
    bb_pow.append(bb_pow[-1] * bb)

# Evaluate basis
F = np.zeros((N_basis, N_total), dtype=complex)
for l, (p, q, r, s) in enumerate(basis_idx):
    F[l] = a_pow[p] * ab_pow[q] * b_pow[r] * bb_pow[s]

print(f"  Basis evaluated at {N_total} points")
print(f"  Memory: {F.nbytes / 1e9:.2f} GiB")


# ============================================================
# STAGE 4: DERIVATIVE INDEX MAPS
# ============================================================

# For the Dirichlet form Q_{ij} = integral g^{ab} (d fbar_i / dz^a)(d f_j / dzbar^b) h dV
#
# d(f_j)/d(abar) = q_j * f_{(p,q-1,r,s)}
# d(f_j)/d(bbar) = s_j * f_{(p,q,r,s-1)}
# d(fbar_i)/d(a) = q_i * f_{(q-1,p,s,r)}   [conjugate-swapped index]
# d(fbar_i)/d(b) = s_i * f_{(q,p,s-1,r)}

# Build derivative maps
# For f_j derivatives (antiholomorphic):
abar_coeff = np.zeros(N_basis)  # coefficient q_j
abar_target = np.zeros(N_basis, dtype=int)  # target index for d/dabar
bbar_coeff = np.zeros(N_basis)  # coefficient s_j
bbar_target = np.zeros(N_basis, dtype=int)

# For fbar_i derivatives (holomorphic):
bar_a_coeff = np.zeros(N_basis)  # coefficient q_i (from conjugate)
bar_a_target = np.zeros(N_basis, dtype=int)
bar_b_coeff = np.zeros(N_basis)  # coefficient s_i
bar_b_target = np.zeros(N_basis, dtype=int)

# Conjugate map: (p,q,r,s) -> (q,p,s,r)
conj_map = np.zeros(N_basis, dtype=int)

for l, (p, q, r, s) in enumerate(basis_idx):
    # d f_l / d abar
    if q > 0:
        target = (p, q-1, r, s)
        if target in idx_to_l:
            abar_coeff[l] = q
            abar_target[l] = idx_to_l[target]

    # d f_l / d bbar
    if s > 0:
        target = (p, q, r, s-1)
        if target in idx_to_l:
            bbar_coeff[l] = s
            bbar_target[l] = idx_to_l[target]

    # d fbar_l / d a: q_l * basis at (q-1, p, s, r)
    if q > 0:
        target = (q-1, p, s, r)
        if target in idx_to_l:
            bar_a_coeff[l] = q
            bar_a_target[l] = idx_to_l[target]

    # d fbar_l / d b: s_l * basis at (q, p, s-1, r)
    if s > 0:
        target = (q, p, s-1, r)
        if target in idx_to_l:
            bar_b_coeff[l] = s
            bar_b_target[l] = idx_to_l[target]

    # Conjugate map
    conj_target = (q, p, s, r)
    if conj_target in idx_to_l:
        conj_map[l] = idx_to_l[conj_target]

print("  Derivative index maps computed")


# ============================================================
# STAGE 5: ASSEMBLE WEIGHT MATRICES
# ============================================================

print("\n" + "=" * 72)
print("STAGE 5: WEIGHT MATRIX ASSEMBLY")
print("=" * 72)

def compute_W(F, w_vec):
    """Compute W[l,l'] = sum_m w_m * F[l,m] * F[l',m] (NOT conjugated)."""
    # W = F @ diag(w) @ F^T  (transpose, not hermitian conjugate)
    Fw = F * w_vec[np.newaxis, :]
    return Fw @ F.T


def assemble_QM(n_twist, F, weights, ginv11, ginv12, ginv21, ginv22, P,
                abar_coeff, abar_target, bbar_coeff, bbar_target,
                bar_a_coeff, bar_a_target, bar_b_coeff, bar_b_target,
                conj_map, N_basis):
    """
    Assemble Laplacian (Dirichlet form) Q and mass matrix M for O(n_twist).
    """
    # Bundle metric: h = P^{-n}
    h = P ** (-n_twist)
    w = h * weights

    t0 = time.time()

    # Weight matrices for each metric component
    W11 = compute_W(F, w * ginv11)
    W12 = compute_W(F, w * ginv12)
    W21 = compute_W(F, w * ginv21)
    W22 = compute_W(F, w * ginv22)
    dt_W = time.time() - t0

    # Assemble Q using derivative maps
    # Q[i,j] = bar_a_coeff[i] * abar_coeff[j] * W11[bar_a_target[i], abar_target[j]]
    #         + bar_a_coeff[i] * bbar_coeff[j] * W12[bar_a_target[i], bbar_target[j]]
    #         + bar_b_coeff[i] * abar_coeff[j] * W21[bar_b_target[i], abar_target[j]]
    #         + bar_b_coeff[i] * bbar_coeff[j] * W22[bar_b_target[i], bbar_target[j]]

    Q = np.zeros((N_basis, N_basis), dtype=complex)

    # Vectorized assembly using fancy indexing
    ci = bar_a_coeff[:, None] * abar_coeff[None, :]
    Q += ci * W11[bar_a_target[:, None], abar_target[None, :]]

    ci = bar_a_coeff[:, None] * bbar_coeff[None, :]
    Q += ci * W12[bar_a_target[:, None], bbar_target[None, :]]

    ci = bar_b_coeff[:, None] * abar_coeff[None, :]
    Q += ci * W21[bar_b_target[:, None], abar_target[None, :]]

    ci = bar_b_coeff[:, None] * bbar_coeff[None, :]
    Q += ci * W22[bar_b_target[:, None], bbar_target[None, :]]

    # Mass matrix: M[i,j] = integral h * fbar_i * f_j dV
    # M[i,j] = sum_m w_m * conj(F[i,m]) * F[j,m]
    # = (conj(F) * w) @ F^T — Hermitian by construction
    Fw = F * w[np.newaxis, :]
    M = np.conj(Fw) @ F.T

    # Hermitianize
    Q = 0.5 * (Q + Q.T.conj())
    M = 0.5 * (M + M.T.conj())

    dt = time.time() - t0
    return Q, M, dt_W, dt


for n_twist, label in [(0, "O(0)"), (5, "O(5)"), (-5, "O(-5)")]:
    Q, M, dt_W, dt_total = assemble_QM(
        n_twist, F, weights, ginv11, ginv12, ginv21, ginv22, P,
        abar_coeff, abar_target, bbar_coeff, bbar_target,
        bar_a_coeff, bar_a_target, bar_b_coeff, bar_b_target,
        conj_map, N_basis)

    Q_imag = np.max(np.abs(Q.imag))
    M_imag = np.max(np.abs(M.imag))
    print(f"\n  {label}: W matrices {dt_W:.1f}s, total {dt_total:.1f}s")
    print(f"    Q: {Q.shape}, imag max = {Q_imag:.2e}")
    print(f"    M: {M.shape}, imag max = {M_imag:.2e}")

    # Take real part if imaginary is small
    Q_use = Q.real if Q_imag < 0.01 * np.max(np.abs(Q.real)) else Q
    M_use = M.real if M_imag < 0.01 * np.max(np.abs(M.real)) else M

    if n_twist == 0: Q0, M0 = Q_use, M_use
    elif n_twist == 5: Q5, M5 = Q_use, M_use
    elif n_twist == -5: Qm5, Mm5 = Q_use, M_use


# ============================================================
# STAGE 6: EIGENVALUE COMPUTATION
# ============================================================

print("\n" + "=" * 72)
print("STAGE 6: EIGENVALUES AND CONSISTENCY CHECKS")
print("=" * 72)

def solve_eigs(Q, M, label, n_twist=0):
    """Solve Q v = lambda M v with regularization."""
    # SVD-based regularization of M
    N = M.shape[0]
    if np.iscomplexobj(M):
        eigM = np.linalg.eigvalsh(M.real)
    else:
        eigM = np.linalg.eigvalsh(M)

    # Count effective rank
    M_max = eigM[-1]
    rank = np.sum(eigM > 1e-8 * M_max)
    print(f"\n  {label}:")
    print(f"    M rank: {rank}/{N} (threshold 1e-8 * max)")

    # Regularize M
    M_reg = M + 1e-8 * M_max * np.eye(N)
    if np.iscomplexobj(M_reg):
        M_reg = M_reg.real  # take real part if small imaginary

    Q_real = Q.real if np.iscomplexobj(Q) else Q

    try:
        eigvals = eigh(Q_real, M_reg, eigvals_only=True)
        eigvals = np.sort(eigvals)
    except Exception as e:
        print(f"    ERROR: {e}")
        return None

    n_neg = np.sum(eigvals < -0.5)
    n_zero = np.sum(np.abs(eigvals) < 0.5)
    n_pos = np.sum(eigvals > 0.5)
    pos = eigvals[eigvals > 0.5]

    print(f"    Eigenvalues: {len(eigvals)} total")
    print(f"    Neg (<-0.5): {n_neg}, Zero (|λ|<0.5): {n_zero}, Pos (>0.5): {n_pos}")
    if len(pos) > 0:
        print(f"    Min positive: {pos[0]:.4f}")
        print(f"    Max: {pos[-1]:.2f}")
        print(f"    First 8: {pos[:8].round(3)}")

    # Consistency checks
    if n_twist == 0:
        print(f"\n    ZERO MODE CHECK: {n_zero} (expect ~1)")
        if n_zero < 5:
            print("    GOOD: Few zero modes — basis reasonably independent")
        else:
            print("    NOTE: Many zero modes — some linear dependencies")

    if n_twist == -5 and len(pos) > 0:
        print(f"\n    WEITZENBOCK CHECK: min λ = {pos[0]:.4f} (expect ≥ 10)")
        if pos[0] > 7:
            print("    PASSED")
        elif pos[0] > 3:
            print("    PARTIAL — close, FS metric differs from KE")
        else:
            print("    FAILED — eigenvalues still wrong")

    return eigvals


eigs_0 = solve_eigs(Q0, M0, "O(0) scalar Laplacian", 0)
eigs_5 = solve_eigs(Q5, M5, "O(5)", 5)
eigs_m5 = solve_eigs(Qm5, Mm5, "O(-5)", -5)


# ============================================================
# STAGE 7: ANALYTIC TORSION
# ============================================================

print("\n" + "=" * 72)
print("STAGE 7: ZETA REGULARIZATION AND TORSION")
print("=" * 72)

def zeta_prime_0(eigvals, vol_S, label):
    """Compute zeta'(0) with Weyl tail correction."""
    pos = eigvals[eigvals > 0.5]
    if len(pos) == 0:
        print(f"  {label}: No eigenvalues > 0.5")
        return None

    # Computed part
    zp_comp = -np.sum(np.log(pos))

    # Weyl law: N(λ) ~ Vol · λ^2 / (16π^2) for scalar Laplacian on 4D
    # rho(λ) = dN/dλ = Vol · λ / (8π^2)
    # Tail: zeta_tail(s) = C · L^{2-s}/(2-s), C = Vol/(8π^2)
    # zeta'_tail(0) = C · (-L^2 log L / 2 + L^2 / 4)
    L = pos[-1]
    C = vol_S / (8 * pi**2)
    N_weyl = vol_S * L**2 / (16 * pi**2)
    tail = C * (-L**2 * log(L) / 2 + L**2 / 4)
    total = zp_comp + tail

    ratio = abs(tail / zp_comp) if abs(zp_comp) > 1e-10 else float('inf')

    print(f"\n  {label}:")
    print(f"    N_eigs = {len(pos)}, N_weyl(λ_max) = {N_weyl:.0f}")
    print(f"    λ range: [{pos[0]:.3f}, {pos[-1]:.1f}]")
    print(f"    ζ'(computed) = {zp_comp:.4f}")
    print(f"    Weyl tail    = {tail:.4f}")
    print(f"    ζ'(0)        = {total:.4f}")
    print(f"    |tail/comp|  = {ratio:.1f}")

    return {'total': total, 'computed': zp_comp, 'tail': tail,
            'N_eigs': len(pos), 'N_weyl': N_weyl}


results = {}
if eigs_0 is not None:
    results['O0'] = zeta_prime_0(eigs_0, vol_estimate, "O(0)")
if eigs_5 is not None:
    results['O5'] = zeta_prime_0(eigs_5, vol_estimate, "O(5)")
if eigs_m5 is not None:
    results['Om5'] = zeta_prime_0(eigs_m5, vol_estimate, "O(-5)")


# ============================================================
# STAGE 8: THRESHOLD CORRECTION
# ============================================================

print("\n" + "=" * 72)
print("STAGE 8: THE NUMBER")
print("=" * 72)

target = log(3) / sqrt(2)
print(f"\n  Target: ln(3)/√2 = {target:.10f}")

if all(k in results and results[k] is not None for k in ['O0', 'O5', 'Om5']):
    f0 = results['O0']['total']
    f5 = results['O5']['total']
    fm5 = results['Om5']['total']

    print(f"\n  ζ'(0) values:")
    print(f"    f(O)    = {f0:.4f}")
    print(f"    f(L^5)  = {f5:.4f}")
    print(f"    f(L^-5) = {fm5:.4f}")

    # Threshold: Δ_3 - Δ_2 = f(O) + (5/12)[f(L^5) + f(L^{-5})]
    threshold = f0 + (5.0/12.0) * (f5 + fm5)
    print(f"\n  Threshold = {threshold:.4f}")

    if abs(f0) > 1e-6:
        print(f"\n  Ratios:")
        print(f"    f(L^5)/f(O) = {f5/f0:.4f}")
        print(f"    f(L^-5)/f(O) = {fm5/f0:.4f}")
        print(f"    [f(L^5)+f(L^-5)] / [2·f(O)] = {(f5+fm5)/(2*f0):.4f}")

    # SPECTRAL SHIFT ANALYSIS (more robust than absolute torsion)
    # From Weitzenbock: Δ^{O(n)} = nabla*nabla + 2n (on KE surface)
    # So Spec(O(n)) = {μ_k + 2n} where μ_k = Spec(nabla*nabla_n)
    # The log-det shifts: log det'(Δ^{O(n)}) = sum log(μ_k + 2n)
    #
    # For the RATIO of determinants:
    # log[det'(Δ^{O(-5)}) / det'(Δ^{O(5)})]
    # = sum_k [log(μ_k + 10) - log(μ_k - 10)]  (using n=-5 and n=5)
    # If μ_k >> 10: ≈ sum_k [20/μ_k + ...]
    #
    # For the KE metric with the Weitzenbock shift:
    # f(-5) - f(5) should be positive (O(-5) has higher eigenvalues)

    print(f"\n  f(L^-5) - f(L^5) = {fm5 - f5:.4f}")
    print(f"  (Positive indicates correct Weitzenbock ordering)")

# Save results
output = {
    'version': 3,
    'surface': 'Fermat_cubic_dP6',
    'metric': 'Fubini-Study',
    'K_MAX': K_MAX,
    'N_basis': N_basis,
    'N_MC': N_MC,
    'N_total': N_total,
    'domain_R': DOMAIN_R,
    'vol_estimate': float(vol_estimate),
    'vol_exact': float(vol_exact),
    'vol_ratio': float(vol_ratio),
    'target': float(target),
}

for label, eigs in [('O0', eigs_0), ('O5', eigs_5), ('Om5', eigs_m5)]:
    if eigs is not None:
        pos = eigs[eigs > 0.5]
        output[f'{label}_N_pos'] = int(len(pos))
        if len(pos) > 0:
            output[f'{label}_min'] = float(pos[0])
            output[f'{label}_max'] = float(pos[-1])
            output[f'{label}_first10'] = pos[:10].tolist()

for k, v in results.items():
    if v is not None:
        output[f'zeta_{k}'] = v

outpath = 'analytic_torsion_v3_results.json'
with open(outpath, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\n  Results saved to {outpath}")
print(f"\n{'=' * 72}")
print("COMPUTATION COMPLETE")
print(f"{'=' * 72}")
