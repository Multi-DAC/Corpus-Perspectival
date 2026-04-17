#!/usr/bin/env python3
"""
Analytic Torsion on dP6 -- Version 9
=====================================
Phase B.3: Laplacian eigenvalues with BALANCED METRIC.

Key advance over v8: uses the Donaldson balanced metric (from Phase B.1-B.2)
instead of the Fubini-Study metric. The balanced metric approximates the
Kahler-Einstein metric, which has the Lichnerowicz bound lambda_1 >= 3/2.

Algorithm:
  1. Sample the Fermat cubic surface (same as v8)
  2. Load converged balanced metric G_k from balanced_metric_k{K}.npz
  3. At each sample point, compute the balanced metric tensor:
     g^{bal}_{ab} = g^{FS}_{ab} + (1/k) d_a d_b log(rho_G)
     using the "covariance formula":
     g^{bal}_{ab} = (1/k)[<U~^b, U~^a>_G / rho - <U,U~^a>_G <U,U~^b>_G* / rho^2]
  4. Assemble Galerkin stiffness/mass matrices using balanced metric
  5. Eigensolve and compare with v8 (FS metric)

Verification target: lambda_1(O(0)) should shift from 0.598 (FS) toward 1.5 (KE).
"""

import numpy as np
from scipy.linalg import eigh
from math import pi, log, sqrt
import json
import sys
import time
import gc

sys.stdout.reconfigure(encoding='utf-8')

# ============================================================
# CONFIGURATION
# ============================================================

N_MC = 200000           # Fewer points than v8 to save memory for balanced metric
DOMAIN_R = 5.0
MAX_DEGREE = 4          # 196 Galerkin basis functions (same as v8)
BAL_K = 8              # Balanced metric level (use k=8, most reliable)
RNG_SEED = 2026
ZETA3 = np.exp(2j * pi / 3)
C_FLOOR = 0.02

rng = np.random.default_rng(RNG_SEED)

print("=" * 72)
print("ANALYTIC TORSION ON dP6 -- VERSION 9 (BALANCED METRIC)")
print(f"Balanced metric: k={BAL_K}")
print(f"Galerkin basis: MAX_DEGREE={MAX_DEGREE} (196 functions)")
print(f"N_MC={N_MC}, DOMAIN_R={DOMAIN_R}")
print("=" * 72)


# ============================================================
# STAGE 1: SURFACE SAMPLING (same as v8)
# ============================================================

print(f"\n{'='*72}")
print("STAGE 1: SURFACE SAMPLING")
print(f"{'='*72}")

t0 = time.time()

u = rng.uniform(-DOMAIN_R, DOMAIN_R, (4, N_MC))
a_raw = u[0] + 1j * u[1]
b_raw = u[2] + 1j * u[3]

w_raw = -1.0 - a_raw**3 - b_raw**3
valid = np.abs(w_raw) > 1e-8
a_base, b_base, w_base = a_raw[valid], b_raw[valid], w_raw[valid]

c_principal = np.abs(w_base)**(1.0/3.0) * np.exp(1j * np.angle(w_base) / 3.0)

a_all = np.tile(a_base, 3)
b_all = np.tile(b_base, 3)
c_all = np.concatenate([c_principal, ZETA3 * c_principal, ZETA3**2 * c_principal])
P = 1.0 + np.abs(a_all)**2 + np.abs(b_all)**2 + np.abs(c_all)**2

mask = (np.abs(c_all) > C_FLOOR) & (P < 500.0)
a_all, b_all, c_all, P = a_all[mask], b_all[mask], c_all[mask], P[mask]
N_total = len(a_all)

ab = np.conj(a_all)
bb = np.conj(b_all)
cb = np.conj(c_all)

print(f"  Points: {N_total}")
print(f"  P: min={np.min(P):.2f}, median={np.median(P):.2f}, max={np.max(P):.2f}")
print(f"  Time: {time.time()-t0:.1f}s")


# ============================================================
# STAGE 2: FS METRIC (same as v8)
# ============================================================

print(f"\n{'='*72}")
print("STAGE 2: FUBINI-STUDY METRIC")
print(f"{'='*72}")

t1 = time.time()

dc_da = -a_all**2 / c_all**2
dc_db = -b_all**2 / c_all**2
dcb_dab = -ab**2 / cb**2
dcb_dbb = -bb**2 / cb**2

dP_da  = ab + cb * dc_da
dP_dab = a_all + c_all * dcb_dab
dP_db  = bb + cb * dc_db
dP_dbb = b_all + c_all * dcb_dbb

JdJ_11 = 1.0 + np.abs(dc_da)**2
JdJ_12 = np.conj(dc_da) * dc_db
JdJ_22 = 1.0 + np.abs(dc_db)**2
P2 = P**2

JdXb_1 = ab + np.conj(dc_da) * cb
JdXb_2 = bb + np.conj(dc_db) * cb
XJ_1 = a_all + c_all * dc_da
XJ_2 = b_all + c_all * dc_db

g_FS_11 = JdJ_11 / P - JdXb_1 * XJ_1 / P2
g_FS_12 = JdJ_12 / P - JdXb_1 * XJ_2 / P2
g_FS_21 = np.conj(g_FS_12)
g_FS_22 = JdJ_22 / P - JdXb_2 * XJ_2 / P2

det_g_FS = (g_FS_11 * g_FS_22 - g_FS_12 * g_FS_21).real

good = (det_g_FS > 1e-15) & (g_FS_11.real > 0) & np.isfinite(det_g_FS)
for nm in ['a_all', 'b_all', 'c_all', 'ab', 'bb', 'cb', 'P',
           'det_g_FS', 'g_FS_11', 'g_FS_12', 'g_FS_21', 'g_FS_22',
           'dc_da', 'dc_db', 'dcb_dab', 'dcb_dbb',
           'dP_da', 'dP_dab', 'dP_db', 'dP_dbb']:
    exec(f"{nm} = {nm}[good]")
N_total = len(a_all)
P2 = P**2

# FS inverse metric (for comparison)
ds_FS = np.where(det_g_FS > 1e-20, det_g_FS, 1.0)
ginv_FS_11 = (g_FS_22 / ds_FS).real
ginv_FS_12 = -g_FS_12 / ds_FS
ginv_FS_21 = -g_FS_21 / ds_FS
ginv_FS_22 = (g_FS_11 / ds_FS).real

domain_vol = (2 * DOMAIN_R)**4
weights_FS = det_g_FS * domain_vol / (3 * N_MC)
vol_est = np.sum(weights_FS)
vol_exact = 3 * pi**2 / 2

print(f"  Valid points: {N_total}")
print(f"  Vol(FS) = {vol_est:.6f} (exact = {vol_exact:.6f}, ratio = {vol_est/vol_exact:.4f})")
print(f"  Time: {time.time()-t1:.1f}s")


# ============================================================
# STAGE 3: BALANCED METRIC COMPUTATION
# ============================================================

print(f"\n{'='*72}")
print(f"STAGE 3: BALANCED METRIC (k={BAL_K})")
print(f"  Loading balanced_metric_k{BAL_K}.npz")
print(f"  Computing rho_G, metric tensor, and volume form at {N_total} points")
print(f"{'='*72}")

t2 = time.time()

# Load balanced metric data
bal_data = np.load(f'balanced_metric_k{BAL_K}.npz', allow_pickle=True)
N_bal = int(bal_data['N_sections'])
sec_norms = bal_data['section_norms']
sections_info = bal_data['sections']  # (j1, j2, j3, q1, q2) per section

print(f"  N_sections = {N_bal}")
print(f"  eta_2_w = {float(bal_data['eta_2_w']):.4f}, delta_G = {float(bal_data['delta_G']):.2e}")

# Reconstruct full G matrix from blocks
G_full = np.zeros((N_bal, N_bal), dtype=complex)
block_keys = [(q1, q2) for q1 in range(3) for q2 in range(3)]
for q1, q2 in block_keys:
    gk = f'G_{q1}_{q2}'
    ik = f'idx_{q1}_{q2}'
    if gk in bal_data:
        G_block = bal_data[gk]
        indices = bal_data[ik]
        for i_local, i_global in enumerate(indices):
            for j_local, j_global in enumerate(indices):
                G_full[i_global, j_global] = G_block[i_local, j_local]

print(f"  G_full: {G_full.shape}, Hermitian check: {np.max(np.abs(G_full - G_full.T.conj())):.2e}")

# Build balanced-metric section values at our sample points
# s_alpha = a^{j1} b^{j2} c^{j3} / P^{k/2} / norm_alpha
logP = np.log(P)
P_half_k = np.exp(-0.5 * BAL_K * logP)  # P^{-k/2}

# Precompute coordinate powers up to k
max_pow_bal = BAL_K + 1
a_pow_b = [np.ones(N_total, dtype=complex)]
b_pow_b = [np.ones(N_total, dtype=complex)]
c_pow_b = [np.ones(N_total, dtype=complex)]
for i in range(1, max_pow_bal):
    a_pow_b.append(a_pow_b[-1] * a_all)
    b_pow_b.append(b_pow_b[-1] * b_all)
    if i <= 2:
        c_pow_b.append(c_pow_b[-1] * c_all)

# Section matrix U: N_bal x N_total
# U[alpha, p] = a^{j1} b^{j2} c^{j3} * P^{-k/2} / norm_alpha
print(f"  Building section matrix ({N_bal} x {N_total})...")
U = np.empty((N_bal, N_total), dtype=complex)
for idx in range(N_bal):
    j1, j2, j3 = int(sections_info[idx, 0]), int(sections_info[idx, 1]), int(sections_info[idx, 2])
    U[idx] = a_pow_b[j1] * b_pow_b[j2] * c_pow_b[j3] * P_half_k / sec_norms[idx]
print(f"    Memory: {U.nbytes/1e9:.2f} GB")

# V = G @ U (matrix multiply: N_bal x N_bal @ N_bal x N_total = N_bal x N_total)
print(f"  Computing V = G @ U...")
V = G_full @ U
print(f"    Memory: {V.nbytes/1e9:.2f} GB")

# rho_G = Re(sum_alpha conj(U[alpha]) * V[alpha])
rho_G = np.real(np.sum(np.conj(U) * V, axis=0))
rho_pos = rho_G > 1e-30
rho_safe = np.where(rho_pos, rho_G, 1.0)

target_rho = N_bal / vol_est
rho_ratio = rho_G / target_rho
print(f"  rho_G/target: mean={np.mean(rho_ratio):.4f}, std={np.std(rho_ratio):.4f}, "
      f"min={np.min(rho_ratio):.4f}, max={np.max(rho_ratio):.4f}")

# ============================================================
# Compute log-derivatives of sections and the balanced metric tensor
# ============================================================

# R_a = dP/da / P = (abar + cbar * dc/da) / P  (already have dP_da)
R_a = dP_da / P   # holomorphic a-derivative of log P
R_b = dP_db / P   # holomorphic b-derivative of log P

# D^a_alpha = d(log s_alpha)/da = j1/a + j3 * dc_da / c = j1/a - j3 * a^2/c^3
# D^b_alpha = j2/b + j3 * dc_db / c = j2/b - j3 * b^2/c^3
# Delta^a_alpha = D^a_alpha - k * R_a
# Delta^b_alpha = D^b_alpha - k * R_b

# Compute D^a and D^b for each section (vectorized over points)
inv_a = np.where(np.abs(a_all) > 1e-30, 1.0 / a_all, 0.0)
inv_b = np.where(np.abs(b_all) > 1e-30, 1.0 / b_all, 0.0)
dc_da_over_c = dc_da / c_all  # = -a^2/c^3

print(f"  Computing balanced metric tensor...")
# Delta^a[alpha] = D^a_alpha - k*R_a  (N_bal x N_total)
# Utilde_a[alpha, p] = Delta^a_alpha(p) * U[alpha, p]
# Similarly for b

Utilde_a = np.empty((N_bal, N_total), dtype=complex)
Utilde_b = np.empty((N_bal, N_total), dtype=complex)

for idx in range(N_bal):
    j1, j2, j3 = int(sections_info[idx, 0]), int(sections_info[idx, 1]), int(sections_info[idx, 2])

    # D^a = j1/a + j3 * dc_da/c
    D_a = (j1 * inv_a + j3 * dc_da_over_c) if (j1 > 0 or j3 > 0) else np.zeros(N_total, dtype=complex)
    # D^b = j2/b + j3 * dc_db/c
    dc_db_over_c = dc_db / c_all  # = -b^2/c^3
    D_b = (j2 * inv_b + j3 * dc_db_over_c) if (j2 > 0 or j3 > 0) else np.zeros(N_total, dtype=complex)

    Delta_a = D_a - BAL_K * R_a
    Delta_b = D_b - BAL_K * R_b

    Utilde_a[idx] = Delta_a * U[idx]
    Utilde_b[idx] = Delta_b * U[idx]

print(f"    Utilde memory: {2*Utilde_a.nbytes/1e9:.2f} GB")

# Balanced metric tensor via covariance formula:
# g^{bal}_{ab_bar} = (1/k) [ <Utilde_b, Utilde_a>_G / rho - <U, Utilde_a>_G * conj(<U, Utilde_b>_G) / rho^2 ]
# where <X, Y>_G = X^dagger G Y (per point = sum over sections)

# W_a = G @ Utilde_a, W_b = G @ Utilde_b  (N_bal x N_total)
print(f"  Computing G @ Utilde...")
W_a = G_full @ Utilde_a
W_b = G_full @ Utilde_b

# Inner products (per point):
# <Utilde_a, Utilde_a>_G = sum_alpha conj(Utilde_a[alpha]) * W_a[alpha]  (N_total,)
UaGUa = np.real(np.sum(np.conj(Utilde_a) * W_a, axis=0))  # g_aa component numerator
UbGUb = np.real(np.sum(np.conj(Utilde_b) * W_b, axis=0))  # g_bb component
UbGUa = np.sum(np.conj(Utilde_b) * W_a, axis=0)           # g_ab component (complex)

# <U, Utilde_a>_G = V^dagger Utilde_a  (sum over sections)
VdUa = np.sum(np.conj(V) * Utilde_a, axis=0)  # (N_total,) complex
VdUb = np.sum(np.conj(V) * Utilde_b, axis=0)  # (N_total,) complex

# Free large arrays
del Utilde_a, Utilde_b, W_a, W_b, U, V
gc.collect()

# Balanced metric components
inv_rho = 1.0 / rho_safe
inv_rho2 = inv_rho * inv_rho

g_bal_11 = (1.0 / BAL_K) * (UaGUa * inv_rho - np.abs(VdUa)**2 * inv_rho2)
g_bal_22 = (1.0 / BAL_K) * (UbGUb * inv_rho - np.abs(VdUb)**2 * inv_rho2)
g_bal_12 = (1.0 / BAL_K) * (UbGUa * inv_rho - VdUa * np.conj(VdUb) * inv_rho2)
g_bal_21 = np.conj(g_bal_12)

# Clean up intermediates
del UaGUa, UbGUb, UbGUa, VdUa, VdUb, inv_rho, inv_rho2
gc.collect()

det_g_bal = (g_bal_11 * g_bal_22 - g_bal_12 * g_bal_21).real

# Sanity checks
print(f"\n  BALANCED METRIC DIAGNOSTICS:")
print(f"    g_bal_11: mean={np.mean(g_bal_11.real):.4f}, std={np.std(g_bal_11.real):.4f}")
print(f"    g_bal_22: mean={np.mean(g_bal_22.real):.4f}, std={np.std(g_bal_22.real):.4f}")
print(f"    det(g_bal): mean={np.mean(det_g_bal):.6f}, min={np.min(det_g_bal):.4f}")
print(f"    det(g_FS):  mean={np.mean(det_g_FS):.6f}")
print(f"    det ratio:  mean={np.mean(det_g_bal/np.where(det_g_FS>1e-20,det_g_FS,1)):.4f}")

# Check positive definiteness
pd_mask = (g_bal_11.real > 0) & (det_g_bal > 0) & np.isfinite(det_g_bal)
n_pd = int(np.sum(pd_mask))
print(f"    Positive definite: {n_pd}/{N_total} ({100*n_pd/N_total:.1f}%)")

# Fall back to FS where balanced metric is not positive definite
fallback = ~pd_mask
n_fallback = int(np.sum(fallback))
if n_fallback > 0:
    print(f"    Falling back to FS metric at {n_fallback} points ({100*n_fallback/N_total:.1f}%)")
    g_bal_11[fallback] = g_FS_11[fallback]
    g_bal_12[fallback] = g_FS_12[fallback]
    g_bal_21[fallback] = g_FS_21[fallback]
    g_bal_22[fallback] = g_FS_22[fallback]
    det_g_bal[fallback] = det_g_FS[fallback]

# Balanced volume
weights_bal = det_g_bal * domain_vol / (3 * N_MC)
vol_bal = np.sum(weights_bal)
print(f"    Vol(bal) = {vol_bal:.6f} (FS: {vol_est:.6f}, ratio: {vol_bal/vol_est:.4f})")

# Inverse balanced metric
ds_bal = np.where(det_g_bal > 1e-20, det_g_bal, 1.0)
ginv_bal_11 = (g_bal_22 / ds_bal).real
ginv_bal_12 = -g_bal_12 / ds_bal
ginv_bal_21 = -g_bal_21 / ds_bal
ginv_bal_22 = (g_bal_11 / ds_bal).real

print(f"  Time: {time.time()-t2:.1f}s")

# Free balanced metric section data
del bal_data, G_full, rho_G, rho_safe, rho_ratio
gc.collect()


# ============================================================
# STAGE 4: GALERKIN BASIS (same as v8)
# ============================================================

print(f"\n{'='*72}")
print("STAGE 4: GALERKIN BASIS + COORDINATE POWERS")
print(f"{'='*72}")

t3 = time.time()

max_pow = MAX_DEGREE + 1
a_pow = [np.ones(N_total, dtype=complex)]
b_pow = [np.ones(N_total, dtype=complex)]
c_pow = [np.ones(N_total, dtype=complex)]
ab_pow = [np.ones(N_total, dtype=complex)]
bb_pow = [np.ones(N_total, dtype=complex)]
cb_pow = [np.ones(N_total, dtype=complex)]
for k in range(1, max_pow):
    a_pow.append(a_pow[-1] * a_all)
    b_pow.append(b_pow[-1] * b_all)
    c_pow.append(c_pow[-1] * c_all)
    ab_pow.append(ab_pow[-1] * ab)
    bb_pow.append(bb_pow[-1] * bb)
    cb_pow.append(cb_pow[-1] * cb)

max_P_pow = MAX_DEGREE + 5 + 1
P_neg = [np.ones(N_total)]
for k in range(1, max_P_pow + 1):
    P_neg.append(P_neg[-1] / P)

print(f"  Coordinate powers: 0..{max_pow-1}")
print(f"  P^{{-k}}: k=0..{max_P_pow}")
print(f"  Time: {time.time()-t3:.1f}s")


# ============================================================
# HELPER FUNCTIONS (same as v8)
# ============================================================

def enumerate_monomials(max_deg):
    monos = []
    for i1 in range(max_deg + 1):
        for j1 in range(max_deg - i1 + 1):
            for i2 in range(max_deg - i1 - j1 + 1):
                for j2 in range(max_deg - i1 - j1 - i2 + 1):
                    for i3 in range(min(max_deg - i1 - j1 - i2 - j2, 2) + 1):
                        for j3 in range(min(max_deg - i1 - j1 - i2 - j2 - i3, 2) + 1):
                            hol_deg = i1 + i2 + i3
                            anti_deg = j1 + j2 + j3
                            monos.append((i1, j1, i2, j2, i3, j3, hol_deg, anti_deg))
    return monos


def eval_monomial(i1, j1, i2, j2, i3, j3):
    return a_pow[i1] * ab_pow[j1] * b_pow[i2] * bb_pow[j2] * c_pow[i3] * cb_pow[j3]


def compute_monomial_derivs(i1, j1, i2, j2, i3, j3):
    dM_da = np.zeros(N_total, dtype=complex)
    if i1 > 0:
        dM_da += i1 * a_pow[i1-1] * ab_pow[j1] * b_pow[i2] * bb_pow[j2] * c_pow[i3] * cb_pow[j3]
    if i3 > 0:
        dM_da += i3 * a_pow[i1] * ab_pow[j1] * b_pow[i2] * bb_pow[j2] * c_pow[i3-1] * cb_pow[j3] * dc_da
    dM_dab = np.zeros(N_total, dtype=complex)
    if j1 > 0:
        dM_dab += j1 * a_pow[i1] * ab_pow[j1-1] * b_pow[i2] * bb_pow[j2] * c_pow[i3] * cb_pow[j3]
    if j3 > 0:
        dM_dab += j3 * a_pow[i1] * ab_pow[j1] * b_pow[i2] * bb_pow[j2] * c_pow[i3] * cb_pow[j3-1] * dcb_dab
    dM_db = np.zeros(N_total, dtype=complex)
    if i2 > 0:
        dM_db += i2 * a_pow[i1] * ab_pow[j1] * b_pow[i2-1] * bb_pow[j2] * c_pow[i3] * cb_pow[j3]
    if i3 > 0:
        dM_db += i3 * a_pow[i1] * ab_pow[j1] * b_pow[i2] * bb_pow[j2] * c_pow[i3-1] * cb_pow[j3] * dc_db
    dM_dbb = np.zeros(N_total, dtype=complex)
    if j2 > 0:
        dM_dbb += j2 * a_pow[i1] * ab_pow[j1] * b_pow[i2] * bb_pow[j2-1] * c_pow[i3] * cb_pow[j3]
    if j3 > 0:
        dM_dbb += j3 * a_pow[i1] * ab_pow[j1] * b_pow[i2] * bb_pow[j2] * c_pow[i3] * cb_pow[j3-1] * dcb_dbb
    return dM_da, dM_dab, dM_db, dM_dbb


# ============================================================
# STAGE 5: EIGENVALUE COMPUTATION (TWO METRICS)
# ============================================================

def process_bundle(n_twist, max_deg, use_balanced=True, label_suffix="", return_eigvecs=False):
    """
    Build basis, derivatives, assemble Q and M, eigensolve.
    If use_balanced: use balanced metric for stiffness/mass.
    Otherwise: use FS metric (same as v8).
    If return_eigvecs: return (eigvals, eigvecs, monos) instead of just eigvals.
    """
    q = abs(n_twist)
    monos = enumerate_monomials(max_deg)
    label = f"O({n_twist}){label_suffix}"

    print(f"\n  --- {label} ---")

    # Build basis
    basis_info = []
    F = []
    for (i1, j1, i2, j2, i3, j3, hol_deg, anti_deg) in monos:
        m = max(hol_deg, anti_deg)
        kk = m + q
        mono_val = eval_monomial(i1, j1, i2, j2, i3, j3)
        phi = mono_val * P_neg[kk]
        F.append(phi)
        basis_info.append((i1, j1, i2, j2, i3, j3, m, kk))

    F = np.array(F)
    N_b = F.shape[0]
    print(f"  N_basis = {N_b}")

    # Compute derivatives
    dphi_dab = np.zeros((N_b, N_total), dtype=complex)
    dphi_dbb = np.zeros((N_b, N_total), dtype=complex)
    dphibar_da = np.zeros((N_b, N_total), dtype=complex)
    dphibar_db = np.zeros((N_b, N_total), dtype=complex)

    for idx, (i1, j1, i2, j2, i3, j3, m, kk) in enumerate(basis_info):
        M_val = eval_monomial(i1, j1, i2, j2, i3, j3)
        dM_da, dM_dab, dM_db, dM_dbb = compute_monomial_derivs(i1, j1, i2, j2, i3, j3)
        Pk = P_neg[kk]
        Pk1 = P_neg[kk + 1] if kk + 1 <= max_P_pow else P_neg[kk] / P
        dphi_dab[idx] = dM_dab * Pk - kk * M_val * dP_dab * Pk1
        dphi_dbb[idx] = dM_dbb * Pk - kk * M_val * dP_dbb * Pk1
        dMbar_da, _, dMbar_db, _ = compute_monomial_derivs(j1, i1, j2, i2, j3, i3)
        Mbar = np.conj(M_val)
        dphibar_da[idx] = dMbar_da * Pk - kk * Mbar * dP_da * Pk1
        dphibar_db[idx] = dMbar_db * Pk - kk * Mbar * dP_db * Pk1

    # Choose metric
    if use_balanced:
        g_inv_11 = ginv_bal_11
        g_inv_12 = ginv_bal_12
        g_inv_21 = ginv_bal_21
        g_inv_22 = ginv_bal_22
        w_metric = weights_bal
    else:
        g_inv_11 = ginv_FS_11
        g_inv_12 = ginv_FS_12
        g_inv_21 = ginv_FS_21
        g_inv_22 = ginv_FS_22
        w_metric = weights_FS

    # Fiber metric and integration weights
    h = P ** (-n_twist)
    w = h * w_metric

    # Mass matrix
    Fw = np.conj(F) * w[np.newaxis, :]
    M_mat = Fw @ F.T
    del Fw

    # Stiffness matrix
    Q_mat = np.zeros((N_b, N_b), dtype=complex)
    for (D_hol, D_anti, g_comp) in [
        (dphibar_da, dphi_dab, g_inv_11),
        (dphibar_da, dphi_dbb, g_inv_12),
        (dphibar_db, dphi_dab, g_inv_21),
        (dphibar_db, dphi_dbb, g_inv_22),
    ]:
        Dw = D_hol * (w * g_comp)[np.newaxis, :]
        Q_mat += Dw @ D_anti.T
        del Dw

    Q_mat = 0.5 * (Q_mat + Q_mat.T.conj())
    M_mat = 0.5 * (M_mat + M_mat.T.conj())

    del F, dphi_dab, dphi_dbb, dphibar_da, dphibar_db
    gc.collect()

    # Eigensolve
    Qr = Q_mat.real
    Mr = M_mat.real
    del Q_mat, M_mat

    eigM = np.linalg.eigvalsh(Mr)
    Mmax = eigM[-1]
    Mmin_pos = eigM[eigM > 1e-8 * Mmax]
    rank = len(Mmin_pos)
    cond = Mmax / Mmin_pos[0] if len(Mmin_pos) > 0 else float('inf')

    Mr_reg = Mr + 1e-8 * Mmax * np.eye(N_b)

    try:
        if return_eigvecs:
            eigvals, eigvecs = eigh(Qr, Mr_reg)
            order = np.argsort(eigvals)
            eigvals = eigvals[order]
            eigvecs = eigvecs[:, order]
        else:
            eigvals = eigh(Qr, Mr_reg, eigvals_only=True)
            eigvals = np.sort(eigvals)
            eigvecs = None
    except Exception as e:
        print(f"  {label}: EIGENSOLVE FAILED: {e}")
        return None

    del Qr, Mr, Mr_reg
    gc.collect()

    n_neg = int(np.sum(eigvals < -0.5))
    n_zero = int(np.sum(np.abs(eigvals) < 0.5))
    n_pos = int(np.sum(eigvals > 0.5))
    pos = eigvals[eigvals > 0.5]

    print(f"  rank={rank}/{N_b}, cond(M)={cond:.1e}")
    print(f"  Eigenvalues: {n_neg} neg, {n_zero} zero, {n_pos} pos")
    if len(pos) > 0:
        print(f"  Spectrum: [{pos[0]:.4f}, ..., {pos[-1]:.1f}]")
        print(f"  First 10: {np.array2string(pos[:10], precision=4, separator=', ')}")
    if label.startswith("O(0)"):
        print(f"  ZERO MODE CHECK: found {n_zero} (expect 1)")
        if len(pos) > 0:
            print(f"  LICHNEROWICZ CHECK: lambda_1 = {pos[0]:.4f} (KE bound = 1.500)")

    if return_eigvecs:
        return eigvals, eigvecs, monos
    return eigvals


# ============================================================
# RUN BOTH METRICS FOR O(0) COMPARISON
# ============================================================

print(f"\n{'='*72}")
print("STAGE 5: EIGENVALUE COMPUTATION")
print(f"  Computing O(0) with BOTH metrics for comparison")
print(f"{'='*72}")

t4 = time.time()
monos = enumerate_monomials(MAX_DEGREE)
print(f"  Total monomials: {len(monos)}")

print(f"\n  === BALANCED METRIC (k={BAL_K}) — WITH EIGENVECTORS ===")
result_bal = process_bundle(0, MAX_DEGREE, use_balanced=True, label_suffix=" [bal]", return_eigvecs=True)
eigs_bal = result_bal[0]
eigvecs_bal = result_bal[1]
monos_bal = result_bal[2]

# Skip FS and O(5), O(-5) — this run is just for charge analysis
eigs_FS = None
eigs_5_bal = None
eigs_m5_bal = None

print(f"\n  Total computation time: {time.time()-t4:.1f}s")


# ============================================================
# STAGE 6: SPECTRAL COMPARISON
# ============================================================

print(f"\n{'='*72}")
print("STAGE 6: SPECTRAL COMPARISON")
print(f"{'='*72}")

target = log(3) / sqrt(2)
print(f"  Target: ln(3)/sqrt(2) = {target:.10f}")

if eigs_FS is not None and eigs_bal is not None:
    pos_FS = eigs_FS[eigs_FS > 0.5]
    pos_bal = eigs_bal[eigs_bal > 0.5]

    print(f"\n  O(0) COMPARISON (first 20 eigenvalues):")
    print(f"  {'n':>3s}  {'lambda_FS':>12s}  {'lambda_bal':>12s}  {'shift':>10s}  {'shift%':>8s}")
    for i in range(min(20, len(pos_FS), len(pos_bal))):
        shift = pos_bal[i] - pos_FS[i]
        pct = 100 * shift / pos_FS[i]
        print(f"  {i+1:3d}  {pos_FS[i]:12.6f}  {pos_bal[i]:12.6f}  {shift:+10.4f}  {pct:+7.1f}%")

    if len(pos_FS) > 0 and len(pos_bal) > 0:
        print(f"\n  Summary:")
        print(f"    lambda_1(FS)  = {pos_FS[0]:.6f}")
        print(f"    lambda_1(bal) = {pos_bal[0]:.6f}")
        print(f"    KE bound      = 1.500000")
        print(f"    Shift toward KE: {pos_bal[0]-pos_FS[0]:+.6f} "
              f"({'YES' if pos_bal[0] > pos_FS[0] else 'NO'})")

        # Spectral sums
        trG_FS = np.sum(1.0/pos_FS)
        trG_bal = np.sum(1.0/pos_bal)
        trG2_FS = np.sum(1.0/pos_FS**2)
        trG2_bal = np.sum(1.0/pos_bal**2)
        zp_FS = -np.sum(np.log(pos_FS))
        zp_bal = -np.sum(np.log(pos_bal))

        print(f"\n    Spectral sums:")
        print(f"    Tr(G) = sum 1/lam:   FS={trG_FS:.4f}, bal={trG_bal:.4f}")
        print(f"    Tr(G^2) = sum 1/lam^2: FS={trG2_FS:.4f}, bal={trG2_bal:.4f}")
        print(f"    zeta'_comp = -sum ln(lam): FS={zp_FS:.4f}, bal={zp_bal:.4f}")

# O(5), O(-5) balanced metric results
for label, eigs in [("O(5) bal", eigs_5_bal), ("O(-5) bal", eigs_m5_bal)]:
    if eigs is not None:
        pos = eigs[eigs > 0.5]
        neg = eigs[eigs < -0.5]
        zero = np.sum(np.abs(eigs) < 0.5)
        print(f"\n  {label}: {len(neg)} neg, {zero} zero, {len(pos)} pos")
        if len(pos) > 0:
            print(f"    lambda_1 = {pos[0]:.4f}, lambda_max = {pos[-1]:.1f}")
            print(f"    First 5: {np.array2string(pos[:5], precision=4, separator=', ')}")

# Green's function approach: can we see ln(3)/sqrt(2) in spectral data?
if eigs_bal is not None and eigs_5_bal is not None and eigs_m5_bal is not None:
    pos_0 = eigs_bal[eigs_bal > 0.5]
    pos_5 = eigs_5_bal[eigs_5_bal > 0.5]
    pos_m5 = eigs_m5_bal[eigs_m5_bal > 0.5]

    if len(pos_0) > 0 and len(pos_5) > 0 and len(pos_m5) > 0:
        # BHV combination: threshold = f(O(0)) + (5/12)(f(O(5)) + f(O(-5)))
        zp_0 = -np.sum(np.log(pos_0))
        zp_5 = -np.sum(np.log(pos_5))
        zp_m5 = -np.sum(np.log(pos_m5))
        thr_comp = zp_0 + (5.0/12.0) * (zp_5 + zp_m5)

        trG_0 = np.sum(1.0/pos_0)
        trG_5 = np.sum(1.0/pos_5)
        trG_m5 = np.sum(1.0/pos_m5)
        thr_G = trG_0 + (5.0/12.0) * (trG_5 + trG_m5)

        print(f"\n  THRESHOLD COMBINATIONS (balanced metric):")
        print(f"    zeta' combo: {thr_comp:.6f} (target: {target:.6f})")
        print(f"    Tr(G) combo: {thr_G:.6f} (target: {target:.6f})")
        print(f"    ln(3)/sqrt(2) = {target:.6f}")


# ============================================================
# SAVE RESULTS
# ============================================================

print(f"\n{'='*72}")
print("SAVING RESULTS")
print(f"{'='*72}")

output = {
    'version': 9,
    'metric': 'balanced',
    'BAL_K': BAL_K,
    'MAX_DEGREE': MAX_DEGREE,
    'N_MC': N_MC,
    'N_total': N_total,
    'DOMAIN_R': DOMAIN_R,
    'vol_FS': float(vol_est),
    'vol_bal': float(vol_bal),
    'vol_exact': float(vol_exact),
    'target': float(target),
}

for label, eigs, prefix in [
    ("O(0) FS", eigs_FS, "O0_FS"),
    ("O(0) bal", eigs_bal, "O0_bal"),
    ("O(5) bal", eigs_5_bal, "O5_bal"),
    ("O(-5) bal", eigs_m5_bal, "Om5_bal"),
]:
    if eigs is not None:
        pos = eigs[eigs > 0.5]
        output[f'{prefix}_N_pos'] = int(len(pos))
        output[f'{prefix}_N_zero'] = int(np.sum(np.abs(eigs) < 0.5))
        if len(pos) > 0:
            output[f'{prefix}_lambda1'] = float(pos[0])
            output[f'{prefix}_lambda_max'] = float(pos[-1])
            output[f'{prefix}_first20'] = [float(x) for x in pos[:20]]
            output[f'{prefix}_all_pos'] = [float(x) for x in pos]

outfile = 'analytic_torsion_v9b_results.json'
with open(outfile, 'w') as f:
    json.dump(output, f, indent=2)
print(f"  Saved to {outfile}")


# ============================================================
# STAGE 7: Z3^2 CHARGE ANALYSIS
# ============================================================

print(f"\n{'='*72}")
print("STAGE 7: Z3^2 CHARGE ANALYSIS OF EIGENVECTORS")
print(f"{'='*72}")

if eigvecs_bal is not None and monos_bal is not None:
    # Compute Z3^2 charges: q1 = (i1-j1) mod 3, q2 = (i2-j2) mod 3
    # c is Z3^2-invariant on the Fermat cubic, so charge depends only on a,b powers
    basis_charges = []
    for (i1, j1, i2, j2, i3, j3, hol_deg, anti_deg) in monos_bal:
        q1 = (i1 - j1) % 3
        q2 = (i2 - j2) % 3
        basis_charges.append((q1, q2))

    charges_array = np.array(basis_charges)
    N_b = len(monos_bal)

    # Sector masks
    sectors = {}
    for q1 in range(3):
        for q2 in range(3):
            mask = (charges_array[:, 0] == q1) & (charges_array[:, 1] == q2)
            sectors[(q1, q2)] = mask
            print(f"  Sector ({q1},{q2}): {int(np.sum(mask))} basis functions")

    # Positive eigenvalues
    pos_idx = np.where(eigs_bal > 0.5)[0]
    pos = eigs_bal[eigs_bal > 0.5]

    if len(pos) > 0:
        print(f"\n  Dominant Z3^2 sector for first 20 positive eigenvalues:")
        for i in range(min(20, len(pos))):
            vec = eigvecs_bal[:, pos_idx[i]]
            fracs = {}
            for (q1, q2), mask in sectors.items():
                v_sec = vec.copy()
                v_sec[~mask] = 0
                fracs[(q1, q2)] = np.sum(v_sec**2) / np.sum(vec**2)
            best = max(fracs, key=fracs.get)
            print(f"    lambda_{i+1} = {pos[i]:10.4f}  sector ({best[0]},{best[1]})  "
                  f"weight {fracs[best]:.3f}")

        # Charge decomposition table for first 5 eigenvectors
        print(f"\n  Full charge decomposition of first 5 eigenvectors:")
        n_show = min(5, len(pos))
        header = "  (q1,q2) " + " ".join(f"  v{i+1:d}   " for i in range(n_show))
        print(header)
        for q1 in range(3):
            for q2 in range(3):
                mask = sectors[(q1, q2)]
                row = f"  ({q1},{q2})  "
                for i in range(n_show):
                    vec = eigvecs_bal[:, pos_idx[i]]
                    v_sec = vec.copy()
                    v_sec[~mask] = 0
                    frac = np.sum(v_sec**2) / np.sum(vec**2)
                    row += f"  {frac:.3f}"
                print(row)

        # S3 orbit analysis
        print(f"\n  S3 ORBIT ANALYSIS:")
        print(f"  S3 orbits: (1,0)↔(0,1)↔(2,2), (2,0)↔(0,2)↔(1,1), (1,2)↔(2,1)")
        print(f"  If lambda_1 and lambda_2 are in S3-related sectors,")
        print(f"  the near-degeneracy is explained by the balanced metric's")
        print(f"  slight breaking of S3 (which is exact on the KE metric).")

total_time = time.time() - t0
print(f"\n{'='*72}")
print(f"COMPLETE in {total_time:.1f}s")
if eigs_bal is not None:
    pos_bal = eigs_bal[eigs_bal > 0.5]
    if len(pos_bal) > 0:
        print(f"  KEY RESULT: lambda_1(bal)={pos_bal[0]:.4f} (KE={1.5:.4f})")
print(f"{'='*72}")
