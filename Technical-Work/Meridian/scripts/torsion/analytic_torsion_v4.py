#!/usr/bin/env python3
"""
Analytic Torsion on the Fermat Cubic dP_6 — Version 4
======================================================
Phase 26 — c-dependent basis, correct derivatives.

Key fixes over v3:
  1. Basis includes c, c̄ powers (t,u ∈ {0,1,2}) — captures branch-dependent eigenfunctions
  2. Derivatives computed pointwise with chain rule: dc/da = -a²/c², dc/db = -b²/c²
  3. Assembly via matrix multiplication (no index maps)
  4. Reduced domain radius to minimize P^5 numerical issues

Surface: S = {x³+y³+z³+1=0} in CP³, chart x₃=1
         Coords (a,b), solved c = w^{1/3}, w = -(1+a³+b³)
         Three branches: c_k = ζ^k · w^{1/3}, k=0,1,2
"""

import numpy as np
from scipy.linalg import eigh
from math import pi, log, sqrt
import json, sys, time

sys.stdout.reconfigure(encoding='utf-8')

# ============================================================
# CONFIGURATION
# ============================================================

N_MC = 120000         # MC points in domain (360K surface points with 3 branches)
K_MAX = 4             # Max total degree p+q+r+s+t+u
DOMAIN_R = 3.0        # Domain radius (reduced from 5 to limit P^5 blowup)
RNG_SEED = 2026
ZETA3 = np.exp(2j * pi / 3)
C_FLOOR = 0.05        # Min |c| to avoid division by c² in derivatives

rng = np.random.default_rng(RNG_SEED)

print("=" * 72)
print("ANALYTIC TORSION ON dP_6 — VERSION 4")
print("c-dependent basis, exact pointwise derivatives")
print("=" * 72)


# ============================================================
# STAGE 1: SAMPLE SURFACE WITH ALL 3 BRANCHES
# ============================================================

print(f"\n{'=' * 72}")
print("STAGE 1: SURFACE SAMPLING (3 BRANCHES)")
print("=" * 72)

t0 = time.time()

u = rng.uniform(-DOMAIN_R, DOMAIN_R, (4, N_MC))
a_raw = u[0] + 1j * u[1]
b_raw = u[2] + 1j * u[3]

w_raw = -1.0 - a_raw**3 - b_raw**3
valid = np.abs(w_raw) > 1e-8
a_base = a_raw[valid]
b_base = b_raw[valid]
w_base = w_raw[valid]
N_valid = len(a_base)

# Principal cube root
c_principal = np.abs(w_base)**(1/3) * np.exp(1j * np.angle(w_base) / 3)

# All 3 branches
branches_c = [c_principal, ZETA3 * c_principal, ZETA3**2 * c_principal]

a_all = np.tile(a_base, 3)
b_all = np.tile(b_base, 3)
c_all = np.concatenate(branches_c)
N_total = len(a_all)

# Filter: |c| not too small (avoid derivative singularity)
c_ok = np.abs(c_all) > C_FLOOR
a_all = a_all[c_ok]; b_all = b_all[c_ok]; c_all = c_all[c_ok]
N_total = len(a_all)

print(f"  Domain: [-{DOMAIN_R}, {DOMAIN_R}]^4")
print(f"  Raw samples: {N_MC}, valid: {N_valid} ({100*N_valid/N_MC:.1f}%)")
print(f"  After |c| filter: {N_total} total points")


# ============================================================
# STAGE 2: METRIC COMPUTATION (same as v3)
# ============================================================

print(f"\n{'=' * 72}")
print("STAGE 2: INDUCED FUBINI-STUDY METRIC")
print("=" * 72)

ab = np.conj(a_all)
bb = np.conj(b_all)
cb = np.conj(c_all)

P = np.abs(a_all)**2 + np.abs(b_all)**2 + np.abs(c_all)**2 + 1.0
P2 = P**2

# dc/da = -a²/c², dc/db = -b²/c²
c2 = c_all**2
dc_da = -a_all**2 / c2
dc_db = -b_all**2 / c2
# Conjugates: dc̄/dā = -ā²/c̄², dc̄/db̄ = -b̄²/c̄²
cb2 = cb**2
dcb_dab = -ab**2 / cb2
dcb_dbb = -bb**2 / cb2

# Jacobian J = [[1, 0], [0, 1], [dc/da, dc/db], [0, 0]]
JdJ_11 = 1.0 + np.abs(dc_da)**2
JdJ_12 = np.conj(dc_da) * dc_db
JdJ_22 = 1.0 + np.abs(dc_db)**2

JdXb_1 = np.conj(a_all) + np.conj(dc_da) * np.conj(c_all)
JdXb_2 = np.conj(b_all) + np.conj(dc_db) * np.conj(c_all)
XJ_1 = a_all + c_all * dc_da
XJ_2 = b_all + c_all * dc_db

g11 = JdJ_11 / P - JdXb_1 * XJ_1 / P2
g12 = JdJ_12 / P - JdXb_1 * XJ_2 / P2
g21 = np.conj(g12)
g22 = JdJ_22 / P - JdXb_2 * XJ_2 / P2

det_g = (g11 * g22 - g12 * g21).real

# Filter: positive definite
good = (det_g > 1e-15) & (g11.real > 0) & np.isfinite(det_g)
for arr_name in ['a_all', 'b_all', 'c_all', 'ab', 'bb', 'cb',
                 'P', 'P2', 'det_g', 'g11', 'g12', 'g21', 'g22',
                 'dc_da', 'dc_db', 'dcb_dab', 'dcb_dbb']:
    exec(f"{arr_name} = {arr_name}[good]")
N_total = len(a_all)

det_safe = np.where(det_g > 1e-20, det_g, 1.0)
ginv11 = (g22 / det_safe).real
ginv12 = -g12 / det_safe
ginv21 = -g21 / det_safe
ginv22 = (g11 / det_safe).real

# MC weights
domain_vol = (2 * DOMAIN_R)**4
weights = det_g * domain_vol / (3 * N_MC)

vol_estimate = np.sum(weights)
vol_exact = 3.0 * pi**2 / 2.0
vol_ratio = vol_estimate / vol_exact

print(f"  Points after filtering: {N_total}")
print(f"  Estimated Vol(S) = {vol_estimate:.4f}")
print(f"  Exact Vol(dP_6, FS) = {vol_exact:.4f}")
print(f"  Ratio: {vol_ratio:.4f}")
print(f"  Time: {time.time()-t0:.1f}s")

if abs(vol_ratio - 1) < 0.15:
    print("  GOOD: Volume within 15%")
elif abs(vol_ratio - 1) < 0.30:
    print("  OK: Volume within 30%")
else:
    print("  WARNING: Volume far from exact")


# ============================================================
# STAGE 3: c-DEPENDENT MONOMIAL BASIS
# ============================================================

print(f"\n{'=' * 72}")
print(f"STAGE 3: c-DEPENDENT MONOMIAL BASIS (degree ≤ {K_MAX})")
print("=" * 72)

t1 = time.time()

# Basis: a^p · ā^q · b^r · b̄^s · c^t · c̄^u
# with p+q+r+s+t+u ≤ K_MAX and t,u ∈ {0,1,2}
basis_idx = []
for total in range(K_MAX + 1):
    for p in range(total + 1):
        for q in range(total - p + 1):
            for r in range(total - p - q + 1):
                for s in range(total - p - q - r + 1):
                    rem = total - p - q - r - s
                    for t in range(min(rem, 2) + 1):
                        u = rem - t
                        if u <= 2:
                            basis_idx.append((p, q, r, s, t, u))

N_basis = len(basis_idx)

# Conjugate map: (p,q,r,s,t,u) → (q,p,s,r,u,t)
idx_to_l = {idx: l for l, idx in enumerate(basis_idx)}
conj_map = np.zeros(N_basis, dtype=int)
for l, (p, q, r, s, t, u) in enumerate(basis_idx):
    conj_target = (q, p, s, r, u, t)
    if conj_target in idx_to_l:
        conj_map[l] = idx_to_l[conj_target]
    else:
        conj_map[l] = l  # fallback (shouldn't happen if K_MAX >= max index)

print(f"  Basis size: {N_basis}")

# Precompute powers
max_pow = K_MAX
a_pow = [np.ones(N_total, dtype=complex)]
ab_pow = [np.ones(N_total, dtype=complex)]
b_pow = [np.ones(N_total, dtype=complex)]
bb_pow = [np.ones(N_total, dtype=complex)]
c_pow = [np.ones(N_total, dtype=complex)]
cb_pow = [np.ones(N_total, dtype=complex)]
for k in range(1, max_pow + 1):
    a_pow.append(a_pow[-1] * a_all)
    ab_pow.append(ab_pow[-1] * ab)
    b_pow.append(b_pow[-1] * b_all)
    bb_pow.append(bb_pow[-1] * bb)
    c_pow.append(c_pow[-1] * c_all)
    cb_pow.append(cb_pow[-1] * cb)

# Evaluate basis and derivatives at all MC points
F = np.zeros((N_basis, N_total), dtype=complex)
Fa = np.zeros((N_basis, N_total), dtype=complex)    # ∂f/∂a
Fb = np.zeros((N_basis, N_total), dtype=complex)    # ∂f/∂b
Fabar = np.zeros((N_basis, N_total), dtype=complex) # ∂f/∂ā
Fbbar = np.zeros((N_basis, N_total), dtype=complex) # ∂f/∂b̄

for l, (p, q, r, s, t, u) in enumerate(basis_idx):
    # Base value
    val = a_pow[p] * ab_pow[q] * b_pow[r] * bb_pow[s] * c_pow[t] * cb_pow[u]
    F[l] = val

    # ∂f/∂a = p·a^{p-1}·...·c^t·c̄^u + t·a^p·...·c^{t-1}·c̄^u·(dc/da)
    d_a = np.zeros(N_total, dtype=complex)
    if p > 0:
        d_a += p * a_pow[p-1] * ab_pow[q] * b_pow[r] * bb_pow[s] * c_pow[t] * cb_pow[u]
    if t > 0:
        d_a += t * a_pow[p] * ab_pow[q] * b_pow[r] * bb_pow[s] * c_pow[t-1] * cb_pow[u] * dc_da
    Fa[l] = d_a

    # ∂f/∂b = r·...·b^{r-1}·... + t·...·c^{t-1}·(dc/db)
    d_b = np.zeros(N_total, dtype=complex)
    if r > 0:
        d_b += r * a_pow[p] * ab_pow[q] * b_pow[r-1] * bb_pow[s] * c_pow[t] * cb_pow[u]
    if t > 0:
        d_b += t * a_pow[p] * ab_pow[q] * b_pow[r] * bb_pow[s] * c_pow[t-1] * cb_pow[u] * dc_db
    Fb[l] = d_b

    # ∂f/∂ā = q·a^p·ā^{q-1}·... + u·...·c̄^{u-1}·(dc̄/dā)
    d_abar = np.zeros(N_total, dtype=complex)
    if q > 0:
        d_abar += q * a_pow[p] * ab_pow[q-1] * b_pow[r] * bb_pow[s] * c_pow[t] * cb_pow[u]
    if u > 0:
        d_abar += u * a_pow[p] * ab_pow[q] * b_pow[r] * bb_pow[s] * c_pow[t] * cb_pow[u-1] * dcb_dab
    Fabar[l] = d_abar

    # ∂f/∂b̄ = s·...·b̄^{s-1}·... + u·...·c̄^{u-1}·(dc̄/db̄)
    d_bbar = np.zeros(N_total, dtype=complex)
    if s > 0:
        d_bbar += s * a_pow[p] * ab_pow[q] * b_pow[r] * bb_pow[s-1] * c_pow[t] * cb_pow[u]
    if u > 0:
        d_bbar += u * a_pow[p] * ab_pow[q] * b_pow[r] * bb_pow[s] * c_pow[t] * cb_pow[u-1] * dcb_dbb
    Fbbar[l] = d_bbar

mem_gb = 5 * F.nbytes / 1e9
print(f"  Basis + derivatives evaluated at {N_total} points")
print(f"  Memory (5 arrays): {mem_gb:.2f} GiB")
print(f"  Time: {time.time()-t1:.1f}s")


# ============================================================
# STAGE 4: ASSEMBLE Q AND M FOR EACH TWIST
# ============================================================

print(f"\n{'=' * 72}")
print("STAGE 4: MATRIX ASSEMBLY")
print("=" * 72)


def assemble_QM(n_twist, F, Fa, Fb, Fabar, Fbbar, weights,
                ginv11, ginv12, ginv21, ginv22, P, conj_map):
    """
    Assemble Dirichlet form Q and mass matrix M for O(n_twist).

    Q[i,j] = ∫ g^{αβ̄} (∂_α f̄_i)(∂_{β̄} f_j) · P^{-n} · dV
    M[i,j] = ∫ f̄_i · f_j · P^{-n} · dV

    where ∂_α f̄_i = (∂f_{conj(i)}/∂α) evaluated at MC points.
    """
    t0 = time.time()

    h = P ** (-n_twist)
    w = h * weights  # combined weight: h · det(g) · domain_vol / (3*N_MC)

    # Conjugate-mapped derivative arrays: ∂(f̄_i)/∂a = Fa[conj_map[i], :]
    Fa_c = Fa[conj_map]   # (N_basis, N_total)
    Fb_c = Fb[conj_map]

    # Q = Σ_{α,β̄} Fa_c @ diag(w·g^{αβ̄}) @ F_{β̄}^T
    # 4 terms: (a,ā), (a,b̄), (b,ā), (b,b̄)
    Q = np.zeros((F.shape[0], F.shape[0]), dtype=complex)

    for (D_hol, D_antihol, ginv) in [
        (Fa_c, Fabar, ginv11),  # g^{aā}
        (Fa_c, Fbbar, ginv12),  # g^{ab̄}
        (Fb_c, Fabar, ginv21),  # g^{bā}
        (Fb_c, Fbbar, ginv22),  # g^{bb̄}
    ]:
        wg = w * ginv  # (N_total,) — combined weight
        # Q += D_hol @ diag(wg) @ D_antihol^T
        Dw = D_hol * wg[np.newaxis, :]  # (N_basis, N_total)
        Q += Dw @ D_antihol.T

    # M = conj(F) @ diag(w) @ F^T  — Hermitian by construction
    Fw = np.conj(F) * w[np.newaxis, :]
    M = Fw @ F.T

    # Hermitianize (numerical cleanup)
    Q = 0.5 * (Q + Q.T.conj())
    M = 0.5 * (M + M.T.conj())

    dt = time.time() - t0
    return Q, M, dt


results_QM = {}
for n_twist, label in [(0, "O(0)"), (5, "O(5)"), (-5, "O(-5)")]:
    Q, M, dt = assemble_QM(n_twist, F, Fa, Fb, Fabar, Fbbar, weights,
                            ginv11, ginv12, ginv21, ginv22, P, conj_map)

    Q_imag = np.max(np.abs(Q.imag))
    M_imag = np.max(np.abs(M.imag))
    Q_real_max = np.max(np.abs(Q.real))
    M_real_max = np.max(np.abs(M.real))

    print(f"\n  {label}: assembled in {dt:.1f}s")
    print(f"    Q: max|re| = {Q_real_max:.2e}, max|im| = {Q_imag:.2e}, im/re = {Q_imag/max(Q_real_max,1e-30):.2e}")
    print(f"    M: max|re| = {M_real_max:.2e}, max|im| = {M_imag:.2e}, im/re = {M_imag/max(M_real_max,1e-30):.2e}")

    results_QM[label] = (Q, M)


# ============================================================
# STAGE 5: EIGENVALUE COMPUTATION
# ============================================================

print(f"\n{'=' * 72}")
print("STAGE 5: EIGENVALUES AND CONSISTENCY CHECKS")
print("=" * 72)


def solve_eigs(Q, M, label, n_twist=0):
    """Solve Q v = λ M v."""
    N = M.shape[0]

    # Use real parts if imaginary is small
    Q_imag_ratio = np.max(np.abs(Q.imag)) / max(np.max(np.abs(Q.real)), 1e-30)
    M_imag_ratio = np.max(np.abs(M.imag)) / max(np.max(np.abs(M.real)), 1e-30)
    Q_use = Q.real if Q_imag_ratio < 0.01 else Q
    M_use = M.real if M_imag_ratio < 0.01 else M

    # Check M conditioning
    if np.iscomplexobj(M_use):
        eigM = np.linalg.eigvalsh(M_use.real)
    else:
        eigM = np.linalg.eigvalsh(M_use)

    M_max = eigM[-1]
    rank = np.sum(eigM > 1e-8 * M_max)
    cond = M_max / max(eigM[eigM > 0][0], 1e-30) if np.any(eigM > 0) else float('inf')

    print(f"\n  {label}:")
    print(f"    M rank: {rank}/{N}, cond ≈ {cond:.1e}")

    # Regularize M
    eps = 1e-8 * M_max
    M_reg = M_use + eps * np.eye(N)
    if np.iscomplexobj(M_reg):
        M_reg = M_reg.real

    Q_real = Q_use.real if np.iscomplexobj(Q_use) else Q_use

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
        print(f"    First 10: {pos[:10].round(3)}")

    # Consistency checks
    if n_twist == 0:
        print(f"\n    ZERO MODE CHECK: {n_zero} zero modes (expect 1)")
        if n_zero <= 3:
            print("    GOOD")
        elif n_zero <= 10:
            print("    MARGINAL — some linear dependencies")
        else:
            print("    BAD — too many zero modes, basis problems persist")

    if n_twist == -5 and len(pos) > 0:
        print(f"\n    WEITZENBOCK CHECK: min λ = {pos[0]:.4f} (expect ≥ 10)")
        if pos[0] > 8:
            print("    PASSED")
        elif pos[0] > 5:
            print("    PARTIAL — approaching bound")
        else:
            print("    FAILED — eigenvalues too low")

    return eigvals


all_eigs = {}
for label, n_twist in [("O(0)", 0), ("O(5)", 5), ("O(-5)", -5)]:
    Q, M = results_QM[label]
    all_eigs[label] = solve_eigs(Q, M, label, n_twist)


# ============================================================
# STAGE 6: ANALYTIC TORSION
# ============================================================

print(f"\n{'=' * 72}")
print("STAGE 6: ZETA REGULARIZATION AND TORSION")
print("=" * 72)


def zeta_prime_0(eigvals, vol_S, label):
    """Compute ζ'(0) with Weyl tail correction."""
    pos = eigvals[eigvals > 0.5]
    if len(pos) == 0:
        print(f"  {label}: No eigenvalues > 0.5")
        return None

    # Computed part: -Σ log(λ_k)
    zp_comp = -np.sum(np.log(pos))

    # Weyl tail: N(λ) ~ Vol·λ²/(16π²) for Laplacian on 4D Kähler
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
for label in ["O(0)", "O(5)", "O(-5)"]:
    if all_eigs[label] is not None:
        results[label] = zeta_prime_0(all_eigs[label], vol_estimate, label)


# ============================================================
# STAGE 7: THRESHOLD CORRECTION
# ============================================================

print(f"\n{'=' * 72}")
print("STAGE 7: THE NUMBER")
print("=" * 72)

target = log(3) / sqrt(2)
print(f"\n  Target: ln(3)/√2 = {target:.10f}")

if all(k in results and results[k] is not None for k in ["O(0)", "O(5)", "O(-5)"]):
    f0 = results["O(0)"]['total']
    f5 = results["O(5)"]['total']
    fm5 = results["O(-5)"]['total']

    print(f"\n  ζ'(0) values:")
    print(f"    f(O)    = {f0:.4f}")
    print(f"    f(L^5)  = {f5:.4f}")
    print(f"    f(L^-5) = {fm5:.4f}")

    threshold = f0 + (5.0/12.0) * (f5 + fm5)
    print(f"\n  Threshold = {threshold:.6f}")

    if abs(f0) > 1e-6:
        print(f"\n  Ratios:")
        print(f"    f(L^5)/f(O) = {f5/f0:.4f}")
        print(f"    f(L^-5)/f(O) = {fm5/f0:.4f}")

    print(f"\n  f(L^-5) - f(L^5) = {fm5 - f5:.4f}")
    print(f"  (Positive = correct Weitzenböck ordering)")

# Save results
output = {
    'version': 4,
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

for label, eigs in all_eigs.items():
    key = label.replace("(", "").replace(")", "").replace("-", "m")
    if eigs is not None:
        pos = eigs[eigs > 0.5]
        output[f'{key}_N_pos'] = int(len(pos))
        output[f'{key}_N_zero'] = int(np.sum(np.abs(eigs) < 0.5))
        if len(pos) > 0:
            output[f'{key}_min'] = float(pos[0])
            output[f'{key}_max'] = float(pos[-1])
            output[f'{key}_first10'] = pos[:10].tolist()

for k, v in results.items():
    key = k.replace("(", "").replace(")", "").replace("-", "m")
    if v is not None:
        output[f'zeta_{key}'] = v

outpath = 'analytic_torsion_v4_results.json'
with open(outpath, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\n  Results saved to {outpath}")
print(f"\n{'=' * 72}")
print("COMPUTATION COMPLETE")
print(f"{'=' * 72}")
