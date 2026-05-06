#!/usr/bin/env python3
"""
Z3^2 Charge Analysis of Balanced-Metric Eigenvectors on dP6
============================================================
Tests the prediction: lambda_1 ~ lambda_2 near-degeneracy on the balanced
metric arises from S3-related Z3^2 charge sectors. On the exact KE metric,
these would be exactly degenerate (same irrep of Aut(S)).

Strategy: Re-run O(0) eigensolve from v9 with eigenvectors, then project
onto Z3^2 charge sectors.

Key insight: c is Z3^2-invariant on the Fermat cubic, so
charge(a^i1 a_bar^j1 b^i2 b_bar^j2 c^i3 c_bar^j3 / P^k) = ((i1-j1)%3, (i2-j2)%3)
"""

import numpy as np
from scipy.linalg import eigh
from math import pi
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Configuration — MUST match v9
N_MC = 200000
DOMAIN_R = 5.0
MAX_DEGREE = 4
BAL_K = 8
RNG_SEED = 2026
ZETA3 = np.exp(2j * pi / 3)
C_FLOOR = 0.02

rng = np.random.default_rng(RNG_SEED)

print("=" * 72)
print("Z3^2 CHARGE ANALYSIS OF BALANCED-METRIC EIGENVECTORS")
print("=" * 72)

# ============================================================
# STAGE 1: SAMPLE SURFACE (identical to v9)
# ============================================================
print("\nStage 1: Sampling Fermat cubic...")
t0 = time.time()

a_all_list, b_all_list, c_all_list = [], [], []

for _ in range(3):
    a_re = rng.uniform(-DOMAIN_R, DOMAIN_R, N_MC)
    a_im = rng.uniform(-DOMAIN_R, DOMAIN_R, N_MC)
    b_re = rng.uniform(-DOMAIN_R, DOMAIN_R, N_MC)
    b_im = rng.uniform(-DOMAIN_R, DOMAIN_R, N_MC)
    a = a_re + 1j * a_im
    b = b_re + 1j * b_im
    w_raw = -(a**3 + b**3 + 1)
    r = np.abs(w_raw) ** (1.0 / 3.0)
    theta = np.angle(w_raw) / 3.0
    c = r * np.exp(1j * theta)
    valid = np.abs(c**3 + a**3 + b**3 + 1) < 0.01 * (1 + np.abs(a)**3 + np.abs(b)**3)
    valid &= np.abs(c) > C_FLOOR
    a_all_list.append(a[valid])
    b_all_list.append(b[valid])
    c_all_list.append(c[valid])

a_all = np.concatenate(a_all_list)
b_all = np.concatenate(b_all_list)
c_all = np.concatenate(c_all_list)
N_total = len(a_all)
ab = np.conj(a_all)
bb = np.conj(b_all)
cb = np.conj(c_all)
P = 1 + np.abs(a_all)**2 + np.abs(b_all)**2 + np.abs(c_all)**2

print(f"  Points: {N_total}")
print(f"  Time: {time.time()-t0:.1f}s")

# ============================================================
# STAGE 2: FS METRIC + DERIVATIVES (identical to v9)
# ============================================================
print("\nStage 2: FS metric + derivatives...")
t1 = time.time()

dc_da = -(a_all**2) / (c_all**2)
dc_db = -(b_all**2) / (c_all**2)
dcb_dab = np.conj(dc_da)
dcb_dbb = np.conj(dc_db)

dP_da = ab + cb * dc_da
dP_db = bb + cb * dc_db
dP_dab = a_all + c_all * dcb_dab
dP_dbb = b_all + c_all * dcb_dbb

g_FS_11 = (P * (1 + np.abs(dc_da)**2) - np.abs(dP_da)**2) / P**2
g_FS_12 = (P * dc_db * np.conj(dc_da) - dP_db * np.conj(dP_da)) / P**2
g_FS_21 = np.conj(g_FS_12)
g_FS_22 = (P * (1 + np.abs(dc_db)**2) - np.abs(dP_db)**2) / P**2

ds_FS = (g_FS_11 * g_FS_22 - g_FS_12 * g_FS_21)
det_g_FS = np.abs(ds_FS)

ginv_FS_11 = (g_FS_22 / ds_FS).real
ginv_FS_12 = (-g_FS_12 / ds_FS).real
ginv_FS_21 = (-g_FS_21 / ds_FS).real
ginv_FS_22 = (g_FS_11 / ds_FS).real

domain_vol = (2 * DOMAIN_R)**4
weights_FS = det_g_FS * domain_vol / (3 * N_MC)
print(f"  Time: {time.time()-t1:.1f}s")

# ============================================================
# STAGE 3: BALANCED METRIC (identical to v9)
# ============================================================
print("\nStage 3: Balanced metric...")
t2 = time.time()

bal_data = np.load(f'balanced_metric_k{BAL_K}.npz', allow_pickle=True)
N_bal = int(bal_data['N_sections'])
sec_norms = bal_data['section_norms']
sections_info = bal_data['sections']  # (j1, j2, j3, q1, q2) per section

print(f"  N_sections = {N_bal}")

# Reconstruct full G matrix from Z3^2 blocks
G_full = np.zeros((N_bal, N_bal), dtype=complex)
for q1 in range(3):
    for q2 in range(3):
        gk = f'G_{q1}_{q2}'
        ik = f'idx_{q1}_{q2}'
        if gk in bal_data:
            G_block = bal_data[gk]
            indices = bal_data[ik]
            for i_local, i_global in enumerate(indices):
                for j_local, j_global in enumerate(indices):
                    G_full[int(i_global), int(j_global)] = G_block[i_local, j_local]

# Section values at sample points
k = BAL_K
logP = np.log(P)
P_half_k = np.exp(-0.5 * k * logP)

max_pow_bal = k + 1
a_pow_b = [np.ones(N_total, dtype=complex)]
b_pow_b = [np.ones(N_total, dtype=complex)]
c_pow_b = [np.ones(N_total, dtype=complex)]
for i in range(1, max_pow_bal):
    a_pow_b.append(a_pow_b[-1] * a_all)
    b_pow_b.append(b_pow_b[-1] * b_all)
    if i <= 2:
        c_pow_b.append(c_pow_b[-1] * c_all)

U = np.empty((N_bal, N_total), dtype=complex)
for idx in range(N_bal):
    j1, j2, j3 = int(sections_info[idx, 0]), int(sections_info[idx, 1]), int(sections_info[idx, 2])
    U[idx] = a_pow_b[j1] * b_pow_b[j2] * c_pow_b[j3] * P_half_k / sec_norms[idx]

V = G_full @ U
rho_G = np.real(np.sum(np.conj(U) * V, axis=0))
rho_safe = np.maximum(rho_G, 1e-30)

# Log-derivatives (matching v9 exactly)
R_a = dP_da / P
R_b = dP_db / P

inv_a = np.where(np.abs(a_all) > 1e-30, 1.0 / a_all, 0.0)
inv_b = np.where(np.abs(b_all) > 1e-30, 1.0 / b_all, 0.0)
dc_da_over_c = dc_da / c_all

D_a = np.zeros((N_bal, N_total), dtype=complex)
D_b = np.zeros((N_bal, N_total), dtype=complex)
for alpha in range(N_bal):
    j1 = int(sections_info[alpha, 0])
    j2 = int(sections_info[alpha, 1])
    j3 = int(sections_info[alpha, 2])
    if j1 > 0:
        D_a[alpha] += j1 * inv_a
    if j3 > 0:
        D_a[alpha] += j3 * dc_da_over_c
    if j2 > 0:
        D_b[alpha] += j2 * inv_b
    if j3 > 0:
        D_b[alpha] += j3 * dc_db / c_all

Utilde_a = (D_a - k * R_a[np.newaxis, :]) * U
Utilde_b = (D_b - k * R_b[np.newaxis, :]) * U

rho_ratio = 1.0 / rho_safe

rho_inv = 1.0 / rho_safe

GUa = G_full @ Utilde_a
GUb = G_full @ Utilde_b
VtUa_full = np.sum(np.conj(V) * Utilde_a, axis=0)
VtUb_full = np.sum(np.conj(V) * Utilde_b, axis=0)

# Covariance formula: g_{ab̄} = (1/k)[⟨Ũ_b,Ũ_a⟩_G/ρ - ⟨U,Ũ_a⟩_G·⟨U,Ũ_b⟩*_G/ρ²]
# Note: second term is VdUa * conj(VdUb), NOT VdUb * conj(VdUa)
g_bal_11 = ((1.0 / k) * (np.sum(np.conj(GUa) * Utilde_a, axis=0) * rho_inv - np.abs(VtUa_full)**2 * rho_inv**2)).real
g_bal_12 = (1.0 / k) * (np.sum(np.conj(GUb) * Utilde_a, axis=0) * rho_inv - VtUa_full * np.conj(VtUb_full) * rho_inv**2)
g_bal_21 = np.conj(g_bal_12)
g_bal_22 = ((1.0 / k) * (np.sum(np.conj(GUb) * Utilde_b, axis=0) * rho_inv - np.abs(VtUb_full)**2 * rho_inv**2)).real

ds_bal = g_bal_11 * g_bal_22 - g_bal_12 * g_bal_21
det_g_bal = np.abs(ds_bal)

fallback = (g_bal_11 <= 0) | (det_g_bal <= 0)
n_fb = np.sum(fallback)
print(f"  Fallback to FS: {n_fb}/{N_total} ({100*n_fb/N_total:.1f}%)")

if n_fb > 0:
    g_bal_11[fallback] = g_FS_11[fallback]
    g_bal_12[fallback] = g_FS_12[fallback]
    g_bal_21[fallback] = g_FS_21[fallback]
    g_bal_22[fallback] = g_FS_22[fallback]
    ds_bal[fallback] = ds_FS[fallback]
    det_g_bal[fallback] = det_g_FS[fallback]

# Inverse metric: use det_g_bal (real, positive) as denominator, matching v9
ds_safe = np.where(det_g_bal > 1e-20, det_g_bal, 1.0)
ginv_bal_11 = (g_bal_22 / ds_safe).real
ginv_bal_12 = -g_bal_12 / ds_safe   # MUST stay complex
ginv_bal_21 = -g_bal_21 / ds_safe   # MUST stay complex
ginv_bal_22 = (g_bal_11 / ds_safe).real

weights_bal = det_g_bal * domain_vol / (3 * N_MC)

del bal_data, G_full, rho_G, rho_safe, rho_inv, GUa, GUb, VtUa_full, VtUb_full
del U, V, Utilde_a, Utilde_b, D_a, D_b
import gc; gc.collect()

print(f"  Time: {time.time()-t2:.1f}s")

# ============================================================
# STAGE 4: GALERKIN BASIS WITH Z3^2 CHARGES
# ============================================================
print("\nStage 4: Galerkin basis + Z3^2 charges...")
t3 = time.time()

max_pow = MAX_DEGREE + 1
a_pow = [np.ones(N_total, dtype=complex)]
b_pow = [np.ones(N_total, dtype=complex)]
c_pow = [np.ones(N_total, dtype=complex)]
ab_pow = [np.ones(N_total, dtype=complex)]
bb_pow = [np.ones(N_total, dtype=complex)]
cb_pow = [np.ones(N_total, dtype=complex)]
for kk in range(1, max_pow):
    a_pow.append(a_pow[-1] * a_all)
    b_pow.append(b_pow[-1] * b_all)
    c_pow.append(c_pow[-1] * c_all)
    ab_pow.append(ab_pow[-1] * ab)
    bb_pow.append(bb_pow[-1] * bb)
    cb_pow.append(cb_pow[-1] * cb)

max_P_pow = MAX_DEGREE + 5 + 1
P_neg = [np.ones(N_total)]
for kk in range(1, max_P_pow + 1):
    P_neg.append(P_neg[-1] / P)

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

# Enumerate basis with Z3^2 charge labels
monos = enumerate_monomials(MAX_DEGREE)
basis_charges = []
for (i1, j1, i2, j2, i3, j3, hol_deg, anti_deg) in monos:
    q1 = (i1 - j1) % 3
    q2 = (i2 - j2) % 3
    basis_charges.append((q1, q2))

N_b = len(monos)
print(f"  N_basis = {N_b}")
print(f"  Time: {time.time()-t3:.1f}s")

# ============================================================
# STAGE 5: ASSEMBLE O(0) MATRICES WITH BALANCED METRIC
# ============================================================
print("\nStage 5: Assembling O(0) Galerkin matrices (balanced metric)...")
t4 = time.time()

n_twist = 0
q = 0

# Build basis functions
F = np.zeros((N_b, N_total), dtype=complex)
basis_info = []
for idx, (i1, j1, i2, j2, i3, j3, hol_deg, anti_deg) in enumerate(monos):
    m = max(hol_deg, anti_deg)
    kk = m + q
    F[idx] = eval_monomial(i1, j1, i2, j2, i3, j3) * P_neg[kk]
    basis_info.append((i1, j1, i2, j2, i3, j3, m, kk))

# Derivatives
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

# Balanced metric
h = P ** (-n_twist)  # = 1 for O(0)
w = h * weights_bal

# Mass matrix
Fw = np.conj(F) * w[np.newaxis, :]
M_mat = Fw @ F.T
del Fw

# Stiffness matrix
Q_mat = np.zeros((N_b, N_b), dtype=complex)
for (D_hol, D_anti, g_comp) in [
    (dphibar_da, dphi_dab, ginv_bal_11),
    (dphibar_da, dphi_dbb, ginv_bal_12),
    (dphibar_db, dphi_dab, ginv_bal_21),
    (dphibar_db, dphi_dbb, ginv_bal_22),
]:
    Dw = D_hol * (w * g_comp)[np.newaxis, :]
    Q_mat += Dw @ D_anti.T
    del Dw

Q_mat = 0.5 * (Q_mat + Q_mat.T.conj())
M_mat = 0.5 * (M_mat + M_mat.T.conj())

del F, dphi_dab, dphi_dbb, dphibar_da, dphibar_db
gc.collect()

Qr = Q_mat.real
Mr = M_mat.real
del Q_mat, M_mat

print(f"  Time: {time.time()-t4:.1f}s")

# ============================================================
# STAGE 6: FULL EIGENSOLVE WITH EIGENVECTORS
# ============================================================
print("\nStage 6: Full eigensolve with eigenvectors...")
t5 = time.time()

eigM = np.linalg.eigvalsh(Mr)
Mmax = eigM[-1]
Mr_reg = Mr + 1e-8 * Mmax * np.eye(N_b)

eigvals, eigvecs = eigh(Qr, Mr_reg)
order = np.argsort(eigvals)
eigvals = eigvals[order]
eigvecs = eigvecs[:, order]

# Use same threshold as v9: eigenvalues < 0.5 are "zero modes" (numerical artifacts)
threshold = 0.5
n_neg = int(np.sum(eigvals < -threshold))
n_zero = int(np.sum(np.abs(eigvals) < threshold))
n_pos = int(np.sum(eigvals > threshold))
pos = eigvals[eigvals > threshold]
pos_idx = np.where(eigvals > threshold)[0]

print(f"  Eigenvalue decomposition: {n_neg} neg, {n_zero} zero, {n_pos} pos")
if len(pos) > 0:
    print(f"  lambda_1 = {pos[0]:.6f}")
    print(f"  lambda_2 = {pos[1]:.6f}")
    print(f"  lambda_3 = {pos[2]:.6f}")
    print(f"  First 10: {np.array2string(pos[:10], precision=4, separator=', ')}")
print(f"  Time: {time.time()-t5:.1f}s")

# ============================================================
# STAGE 7: Z3^2 CHARGE DECOMPOSITION OF EIGENVECTORS
# ============================================================
print(f"\n{'='*72}")
print("STAGE 7: Z3^2 CHARGE DECOMPOSITION")
print(f"{'='*72}")

# For each eigenvector, compute the fraction of weight in each Z3^2 sector
charges_array = np.array(basis_charges)  # shape (N_b, 2)

# Build sector masks
sectors = {}
for q1 in range(3):
    for q2 in range(3):
        mask = (charges_array[:, 0] == q1) & (charges_array[:, 1] == q2)
        sectors[(q1, q2)] = mask

if len(pos) == 0:
    print("  NO POSITIVE EIGENVALUES — something is wrong")
else:
    # Analyze first 10 positive eigenvectors
    n_show = min(10, len(pos))
    print(f"\nCharge decomposition of first {n_show} positive eigenvectors:")
    print(f"  (q1,q2) " + "".join(f"  v{i+1:d}   " for i in range(n_show)))
    print(f"  ------- " + "------" * n_show)

    for q1 in range(3):
        for q2 in range(3):
            mask = sectors[(q1, q2)]
            row = f"  ({q1},{q2})  "
            for i in range(n_show):
                vec = eigvecs[:, pos_idx[i]]
                vec_sector = vec.copy()
                vec_sector[~mask] = 0
                frac = np.sum(vec_sector**2) / np.sum(vec**2)
                row += f"  {frac:.3f}"
            print(row)

    # Dominant sector for each positive eigenvector
    print(f"\nDominant Z3^2 sector for each positive eigenvalue:")
    for i in range(min(20, len(pos))):
        vec = eigvecs[:, pos_idx[i]]
        best_frac = 0
        best_sector = None
        for (q1, q2), mask in sectors.items():
            vec_s = vec.copy()
            vec_s[~mask] = 0
            frac = np.sum(vec_s**2) / np.sum(vec**2)
            if frac > best_frac:
                best_frac = frac
                best_sector = (q1, q2)
        print(f"  lambda_{i+1} = {pos[i]:10.4f}  sector ({best_sector[0]},{best_sector[1]})  weight {best_frac:.3f}")

# ============================================================
# STAGE 8: BLOCK-DIAGONAL EIGENSOLVE (VERIFICATION)
# ============================================================
print(f"\n{'='*72}")
print("STAGE 8: BLOCK-DIAGONAL EIGENSOLVE (by charge sector)")
print(f"{'='*72}")

# Solve within each Z3^2 block separately
sector_eigenvalues = {}
for (q1, q2), mask in sectors.items():
    idx_sector = np.where(mask)[0]
    n_sec = len(idx_sector)
    if n_sec == 0:
        continue
    Q_block = Qr[np.ix_(idx_sector, idx_sector)]
    M_block = Mr_reg[np.ix_(idx_sector, idx_sector)]
    try:
        evals_block = eigh(Q_block, M_block, eigvals_only=True)
        evals_block = np.sort(evals_block)
        sector_eigenvalues[(q1, q2)] = evals_block
        # Lowest positive eigenvalue
        pos = evals_block[evals_block > threshold]
        if len(pos) > 0:
            print(f"  ({q1},{q2}): dim={n_sec:3d}, lambda_min = {pos[0]:.4f}, lambda_2 = {pos[1]:.4f}" + (f", lambda_3 = {pos[2]:.4f}" if len(pos) > 2 else ""))
        else:
            print(f"  ({q1},{q2}): dim={n_sec:3d}, all below threshold")
    except Exception as e:
        print(f"  ({q1},{q2}): FAILED: {e}")

# Find the overall lowest positive eigenvalue across all sectors
print(f"\nLowest eigenvalue by sector:")
all_sector_mins = []
for (q1, q2), evals in sector_eigenvalues.items():
    pos = evals[evals > threshold]
    if len(pos) > 0:
        all_sector_mins.append(((q1, q2), pos[0]))

all_sector_mins.sort(key=lambda x: x[1])
for (q1, q2), lam in all_sector_mins[:9]:
    marker = " <-- lambda_1" if abs(lam - all_sector_mins[0][1]) < 0.01 else ""
    marker2 = " <-- lambda_2" if abs(lam - all_sector_mins[1][1]) < 0.01 and marker == "" else ""
    print(f"  ({q1},{q2}): {lam:.6f}{marker}{marker2}")

# S3 orbit analysis
print(f"\n{'='*72}")
print("S3 ORBIT ANALYSIS")
print(f"{'='*72}")
# S3 orbits of Z3^2 charges (permuting a,b,c):
# Under S3, (1,0) <-> (0,1) <-> (2,2) [standard rep]
# (2,0) <-> (0,2) <-> (1,1) [conjugate]
# (1,2) <-> (2,1) [mixed]
# (0,0) [trivial]
orbits = {
    'trivial': [(0,0)],
    'standard': [(1,0), (0,1), (2,2)],
    'conjugate': [(2,0), (0,2), (1,1)],
    'mixed': [(1,2), (2,1)],
}

for name, charges_in_orbit in orbits.items():
    print(f"\n  {name} orbit: {charges_in_orbit}")
    for (q1, q2) in charges_in_orbit:
        if (q1, q2) in sector_eigenvalues:
            pos = sector_eigenvalues[(q1, q2)][sector_eigenvalues[(q1, q2)] > threshold]
            if len(pos) > 0:
                print(f"    ({q1},{q2}): lambda_1={pos[0]:.4f}, lambda_2={pos[1]:.4f}" + (f", lambda_3={pos[2]:.4f}" if len(pos) > 2 else ""))

# Test: are lambda_1 values in S3-related sectors close?
print(f"\n  S3-splitting test (should be ~0 on exact KE):")
for name, charges_in_orbit in orbits.items():
    if len(charges_in_orbit) < 2:
        continue
    mins = []
    for (q1, q2) in charges_in_orbit:
        if (q1, q2) in sector_eigenvalues:
            pos = sector_eigenvalues[(q1, q2)][sector_eigenvalues[(q1, q2)] > threshold]
            if len(pos) > 0:
                mins.append(pos[0])
    if len(mins) >= 2:
        spread = max(mins) - min(mins)
        mean = np.mean(mins)
        print(f"    {name}: min eigenvalues = {[f'{m:.4f}' for m in mins]}, spread = {spread:.4f} ({100*spread/mean:.1f}% of mean)")

total_time = time.time() - t0
print(f"\nTotal time: {total_time:.1f}s")
print(f"\n{'='*72}")
print("DONE")
print(f"{'='*72}")
