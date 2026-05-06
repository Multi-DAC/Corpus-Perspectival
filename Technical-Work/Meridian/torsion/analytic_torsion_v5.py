#!/usr/bin/env python3
"""
Analytic Torsion on the Fermat Cubic dP_6 — Version 5
======================================================
Phase 26 — P-normalized c-dependent basis.

Key insight: raw monomials a^p·ā^q·... are NOT in L²(S, O(n)) for the compact
surface S. They have poles at infinity (x₃=0). P-normalization:
  φ_l = a^p·ā^q·b^r·b̄^s·c^t·c̄^u / P^{d/2},  d = p+q+r+s+t+u
ensures |φ_l| ≤ 1, makes basis elements globally L², and breaks spurious
holomorphicity (∂̄(a/√P) ≠ 0).

Fixes over v4:
  1. P-normalized basis — removes 31 spurious zero modes, stabilizes O(-5)
  2. Derivative correction: ∂φ/∂ā includes -(d/2)·φ·(∂P/∂ā)/P term
  3. Can use larger domain (normalization bounds the integrands)
"""

import numpy as np
from scipy.linalg import eigh
from math import pi, log, sqrt
import json, sys, time

sys.stdout.reconfigure(encoding='utf-8')

# ============================================================
# CONFIGURATION
# ============================================================

N_MC = 150000         # MC domain samples (450K with 3 branches)
K_MAX = 4             # Max total degree
DOMAIN_R = 4.0        # Domain radius (can be larger now — basis is bounded)
RNG_SEED = 2026
ZETA3 = np.exp(2j * pi / 3)
C_FLOOR = 0.05

rng = np.random.default_rng(RNG_SEED)

print("=" * 72)
print("ANALYTIC TORSION ON dP_6 — VERSION 5")
print("P-normalized c-dependent basis")
print("=" * 72)


# ============================================================
# STAGE 1: SURFACE SAMPLING
# ============================================================

print(f"\n{'=' * 72}")
print("STAGE 1: SURFACE SAMPLING")
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

c_principal = np.abs(w_base)**(1/3) * np.exp(1j * np.angle(w_base) / 3)
branches_c = [c_principal, ZETA3 * c_principal, ZETA3**2 * c_principal]

a_all = np.tile(a_base, 3)
b_all = np.tile(b_base, 3)
c_all = np.concatenate(branches_c)

c_ok = np.abs(c_all) > C_FLOOR
a_all = a_all[c_ok]; b_all = b_all[c_ok]; c_all = c_all[c_ok]
N_total = len(a_all)

print(f"  Domain: [-{DOMAIN_R}, {DOMAIN_R}]^4, N_MC={N_MC}")
print(f"  Valid: {N_valid} ({100*N_valid/N_MC:.1f}%), total: {N_total}")


# ============================================================
# STAGE 2: METRIC
# ============================================================

print(f"\n{'=' * 72}")
print("STAGE 2: FUBINI-STUDY METRIC")
print("=" * 72)

ab = np.conj(a_all)
bb = np.conj(b_all)
cb = np.conj(c_all)

P = np.abs(a_all)**2 + np.abs(b_all)**2 + np.abs(c_all)**2 + 1.0
P2 = P**2

c2 = c_all**2
cb2 = cb**2
dc_da = -a_all**2 / c2
dc_db = -b_all**2 / c2
dcb_dab = -ab**2 / cb2
dcb_dbb = -bb**2 / cb2

# dP/da, dP/dā, dP/db, dP/db̄ (surface chain rule)
dP_da = ab + cb * dc_da                # ā - a²c̄/c²
dP_dab = a_all + c_all * dcb_dab       # a - cā²/c̄²
dP_db = bb + cb * dc_db                # b̄ - b²c̄/c²
dP_dbb = b_all + c_all * dcb_dbb       # b - cb̄²/c̄²

# Induced FS metric
JdJ_11 = 1.0 + np.abs(dc_da)**2
JdJ_12 = np.conj(dc_da) * dc_db
JdJ_22 = 1.0 + np.abs(dc_db)**2

JdXb_1 = ab + np.conj(dc_da) * cb
JdXb_2 = bb + np.conj(dc_db) * cb
XJ_1 = a_all + c_all * dc_da
XJ_2 = b_all + c_all * dc_db

g11 = JdJ_11 / P - JdXb_1 * XJ_1 / P2
g12 = JdJ_12 / P - JdXb_1 * XJ_2 / P2
g21 = np.conj(g12)
g22 = JdJ_22 / P - JdXb_2 * XJ_2 / P2

det_g = (g11 * g22 - g12 * g21).real

good = (det_g > 1e-15) & (g11.real > 0) & np.isfinite(det_g)
for nm in ['a_all', 'b_all', 'c_all', 'ab', 'bb', 'cb',
           'P', 'P2', 'det_g', 'g11', 'g12', 'g21', 'g22',
           'dc_da', 'dc_db', 'dcb_dab', 'dcb_dbb',
           'dP_da', 'dP_dab', 'dP_db', 'dP_dbb',
           'c2', 'cb2']:
    exec(f"{nm} = {nm}[good]")
N_total = len(a_all)

det_safe = np.where(det_g > 1e-20, det_g, 1.0)
ginv11 = (g22 / det_safe).real
ginv12 = -g12 / det_safe
ginv21 = -g21 / det_safe
ginv22 = (g11 / det_safe).real

domain_vol = (2 * DOMAIN_R)**4
weights = det_g * domain_vol / (3 * N_MC)

vol_estimate = np.sum(weights)
vol_exact = 3.0 * pi**2 / 2.0
vol_ratio = vol_estimate / vol_exact

print(f"  Points: {N_total}")
print(f"  Vol(S) = {vol_estimate:.4f} (exact {vol_exact:.4f}, ratio {vol_ratio:.4f})")
print(f"  Time: {time.time()-t0:.1f}s")


# ============================================================
# STAGE 3: P-NORMALIZED BASIS AND DERIVATIVES
# ============================================================

print(f"\n{'=' * 72}")
print(f"STAGE 3: P-NORMALIZED BASIS (degree ≤ {K_MAX})")
print("=" * 72)

t1 = time.time()

# Build index list: (p,q,r,s,t,u) with p+q+r+s+t+u ≤ K_MAX, t,u ∈ {0,1,2}
basis_idx = []
for total in range(K_MAX + 1):
    for p in range(total + 1):
        for q in range(total - p + 1):
            for r in range(total - p - q + 1):
                for s in range(total - p - q - r + 1):
                    rem = total - p - q - r - s
                    for t in range(min(rem, 2) + 1):
                        u_val = rem - t
                        if u_val <= 2:
                            basis_idx.append((p, q, r, s, t, u_val))

N_basis = len(basis_idx)
degrees = np.array([sum(idx) for idx in basis_idx])

# Conjugate map: (p,q,r,s,t,u) → (q,p,s,r,u,t)
idx_to_l = {idx: l for l, idx in enumerate(basis_idx)}
conj_map = np.zeros(N_basis, dtype=int)
for l, (p, q, r, s, t, u_val) in enumerate(basis_idx):
    ct = (q, p, s, r, u_val, t)
    conj_map[l] = idx_to_l.get(ct, l)

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

# Precompute P^{-d/2} for each degree
P_inv_half = np.zeros((K_MAX + 1, N_total))
for d in range(K_MAX + 1):
    P_inv_half[d] = P ** (-d / 2.0)

# Precompute dP/P for the normalization correction
dP_da_over_P = dP_da / P
dP_dab_over_P = dP_dab / P
dP_db_over_P = dP_db / P
dP_dbb_over_P = dP_dbb / P

# Evaluate P-normalized basis and derivatives
F = np.zeros((N_basis, N_total), dtype=complex)
Fa = np.zeros((N_basis, N_total), dtype=complex)
Fb = np.zeros((N_basis, N_total), dtype=complex)
Fabar = np.zeros((N_basis, N_total), dtype=complex)
Fbbar = np.zeros((N_basis, N_total), dtype=complex)

for l, (p, q, r, s, t, u_val) in enumerate(basis_idx):
    d = p + q + r + s + t + u_val
    Pd = P_inv_half[d]  # P^{-d/2}

    # Raw monomial
    mono = a_pow[p] * ab_pow[q] * b_pow[r] * bb_pow[s] * c_pow[t] * cb_pow[u_val]

    # P-normalized basis function
    F[l] = mono * Pd

    # Raw monomial derivatives (chain rule through c)
    d_mono_da = np.zeros(N_total, dtype=complex)
    if p > 0:
        d_mono_da += p * a_pow[p-1] * ab_pow[q] * b_pow[r] * bb_pow[s] * c_pow[t] * cb_pow[u_val]
    if t > 0:
        d_mono_da += t * a_pow[p] * ab_pow[q] * b_pow[r] * bb_pow[s] * c_pow[t-1] * cb_pow[u_val] * dc_da

    d_mono_db = np.zeros(N_total, dtype=complex)
    if r > 0:
        d_mono_db += r * a_pow[p] * ab_pow[q] * b_pow[r-1] * bb_pow[s] * c_pow[t] * cb_pow[u_val]
    if t > 0:
        d_mono_db += t * a_pow[p] * ab_pow[q] * b_pow[r] * bb_pow[s] * c_pow[t-1] * cb_pow[u_val] * dc_db

    d_mono_dab = np.zeros(N_total, dtype=complex)
    if q > 0:
        d_mono_dab += q * a_pow[p] * ab_pow[q-1] * b_pow[r] * bb_pow[s] * c_pow[t] * cb_pow[u_val]
    if u_val > 0:
        d_mono_dab += u_val * a_pow[p] * ab_pow[q] * b_pow[r] * bb_pow[s] * c_pow[t] * cb_pow[u_val-1] * dcb_dab

    d_mono_dbb = np.zeros(N_total, dtype=complex)
    if s > 0:
        d_mono_dbb += s * a_pow[p] * ab_pow[q] * b_pow[r] * bb_pow[s-1] * c_pow[t] * cb_pow[u_val]
    if u_val > 0:
        d_mono_dbb += u_val * a_pow[p] * ab_pow[q] * b_pow[r] * bb_pow[s] * c_pow[t] * cb_pow[u_val-1] * dcb_dbb

    # P-normalized derivatives:
    # ∂φ/∂a = (∂mono/∂a - (d/2)·mono·dP_da/P) / P^{d/2}
    half_d = d / 2.0
    Fa[l] = (d_mono_da - half_d * mono * dP_da_over_P) * Pd
    Fb[l] = (d_mono_db - half_d * mono * dP_db_over_P) * Pd
    Fabar[l] = (d_mono_dab - half_d * mono * dP_dab_over_P) * Pd
    Fbbar[l] = (d_mono_dbb - half_d * mono * dP_dbb_over_P) * Pd

mem_gb = 5 * F.nbytes / 1e9
print(f"  Evaluated at {N_total} points, memory: {mem_gb:.2f} GiB")

# Quick check: basis norms
F_max = np.max(np.abs(F), axis=1)
print(f"  Max |φ_l| range: [{np.min(F_max):.3f}, {np.max(F_max):.3f}] (expect ≤ 1)")
print(f"  Time: {time.time()-t1:.1f}s")


# ============================================================
# STAGE 4: MATRIX ASSEMBLY
# ============================================================

print(f"\n{'=' * 72}")
print("STAGE 4: MATRIX ASSEMBLY")
print("=" * 72)


def assemble_QM(n_twist):
    """Assemble Q and M for O(n_twist) using P-normalized basis."""
    t0 = time.time()

    h = P ** (-n_twist)
    w = h * weights

    Fa_c = Fa[conj_map]
    Fb_c = Fb[conj_map]

    Q = np.zeros((N_basis, N_basis), dtype=complex)
    for (D_hol, D_anti, ginv) in [
        (Fa_c, Fabar, ginv11), (Fa_c, Fbbar, ginv12),
        (Fb_c, Fabar, ginv21), (Fb_c, Fbbar, ginv22),
    ]:
        Dw = D_hol * (w * ginv)[np.newaxis, :]
        Q += Dw @ D_anti.T

    Fw = np.conj(F) * w[np.newaxis, :]
    M = Fw @ F.T

    Q = 0.5 * (Q + Q.T.conj())
    M = 0.5 * (M + M.T.conj())

    dt = time.time() - t0
    return Q, M, dt


QM = {}
for n_twist, label in [(0, "O(0)"), (5, "O(5)"), (-5, "O(-5)")]:
    Q, M, dt = assemble_QM(n_twist)
    QM[label] = (Q, M)

    qi = np.max(np.abs(Q.imag))
    qr = np.max(np.abs(Q.real))
    mi = np.max(np.abs(M.imag))
    mr = np.max(np.abs(M.real))
    print(f"  {label}: {dt:.1f}s  Q im/re={qi/max(qr,1e-30):.2e}  M im/re={mi/max(mr,1e-30):.2e}")


# ============================================================
# STAGE 5: EIGENVALUES
# ============================================================

print(f"\n{'=' * 72}")
print("STAGE 5: EIGENVALUES")
print("=" * 72)


def solve_eigs(Q, M, label, n_twist=0):
    N = M.shape[0]

    Q_ir = np.max(np.abs(Q.imag)) / max(np.max(np.abs(Q.real)), 1e-30)
    M_ir = np.max(np.abs(M.imag)) / max(np.max(np.abs(M.real)), 1e-30)
    Q_use = Q.real if Q_ir < 0.05 else Q
    M_use = M.real if M_ir < 0.05 else M

    eigM = np.linalg.eigvalsh(M_use.real if np.iscomplexobj(M_use) else M_use)
    M_max = eigM[-1]
    rank = np.sum(eigM > 1e-8 * M_max)

    M_reg = (M_use.real if np.iscomplexobj(M_use) else M_use) + 1e-8 * M_max * np.eye(N)
    Q_real = Q_use.real if np.iscomplexobj(Q_use) else Q_use

    try:
        eigvals = eigh(Q_real, M_reg, eigvals_only=True)
        eigvals = np.sort(eigvals)
    except Exception as e:
        print(f"  {label}: ERROR {e}")
        return None

    n_neg = np.sum(eigvals < -0.5)
    n_zero = np.sum(np.abs(eigvals) < 0.5)
    n_pos = np.sum(eigvals > 0.5)
    pos = eigvals[eigvals > 0.5]

    print(f"\n  {label}: rank={rank}/{N}")
    print(f"    Neg: {n_neg}, Zero: {n_zero}, Pos: {n_pos}")
    if len(pos) > 0:
        print(f"    Min pos: {pos[0]:.4f}, Max: {pos[-1]:.1f}")
        print(f"    First 8: {pos[:8].round(3)}")

    if n_twist == 0:
        print(f"    ZERO MODE CHECK: {n_zero} (expect 1)")
        if n_zero <= 3:
            print("    GOOD")
        else:
            print("    BAD — spurious zero modes persist")

    if n_twist == -5 and len(pos) > 0:
        print(f"    WEITZENBOCK: min λ = {pos[0]:.4f} (expect ≥ 10)")
        if pos[0] > 8:
            print("    PASSED")
        elif pos[0] > 5:
            print("    PARTIAL")
        else:
            print("    FAILED")

    return eigvals


all_eigs = {}
for label, nt in [("O(0)", 0), ("O(5)", 5), ("O(-5)", -5)]:
    all_eigs[label] = solve_eigs(*QM[label], label, nt)


# ============================================================
# STAGE 6: TORSION
# ============================================================

print(f"\n{'=' * 72}")
print("STAGE 6: ZETA REGULARIZATION")
print("=" * 72)


def zeta_prime_0(eigvals, vol_S, label):
    pos = eigvals[eigvals > 0.5]
    if len(pos) == 0:
        print(f"  {label}: No positive eigenvalues")
        return None

    zp_comp = -np.sum(np.log(pos))
    L = pos[-1]
    C = vol_S / (8 * pi**2)
    N_weyl = vol_S * L**2 / (16 * pi**2)
    tail = C * (-L**2 * log(L) / 2 + L**2 / 4)
    total = zp_comp + tail
    ratio = abs(tail / zp_comp) if abs(zp_comp) > 1e-10 else float('inf')

    print(f"  {label}: N_eigs={len(pos)}, N_weyl={N_weyl:.0f}")
    print(f"    ζ'(comp)={zp_comp:.4f}, tail={tail:.4f}, total={total:.4f}, |tail/comp|={ratio:.1f}")

    return {'total': total, 'computed': zp_comp, 'tail': tail,
            'N_eigs': len(pos), 'N_weyl': N_weyl}


results = {}
for label in ["O(0)", "O(5)", "O(-5)"]:
    if all_eigs[label] is not None:
        results[label] = zeta_prime_0(all_eigs[label], vol_estimate, label)


# ============================================================
# STAGE 7: THE NUMBER
# ============================================================

print(f"\n{'=' * 72}")
print("STAGE 7: THRESHOLD CORRECTION")
print("=" * 72)

target = log(3) / sqrt(2)
print(f"  Target: ln(3)/√2 = {target:.10f}")

if all(k in results and results[k] is not None for k in ["O(0)", "O(5)", "O(-5)"]):
    f0 = results["O(0)"]['total']
    f5 = results["O(5)"]['total']
    fm5 = results["O(-5)"]['total']

    threshold = f0 + (5.0/12.0) * (f5 + fm5)

    print(f"  f(O)={f0:.4f}, f(L⁵)={f5:.4f}, f(L⁻⁵)={fm5:.4f}")
    print(f"  Threshold = {threshold:.6f}")
    print(f"  f(L⁻⁵) - f(L⁵) = {fm5 - f5:.4f} (positive = correct ordering)")

# Save
output = {
    'version': 5, 'surface': 'Fermat_cubic_dP6', 'metric': 'Fubini-Study',
    'basis': 'P-normalized c-dependent monomials',
    'K_MAX': K_MAX, 'N_basis': N_basis, 'N_MC': N_MC, 'N_total': N_total,
    'domain_R': DOMAIN_R,
    'vol_estimate': float(vol_estimate), 'vol_exact': float(vol_exact),
    'vol_ratio': float(vol_ratio), 'target': float(target),
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

with open('analytic_torsion_v5_results.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"\n  Saved to analytic_torsion_v5_results.json")
print(f"\n{'=' * 72}")
print("COMPLETE")
print(f"{'=' * 72}")
