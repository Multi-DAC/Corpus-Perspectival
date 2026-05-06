#!/usr/bin/env python3
"""
Eigenvalue Sweep across k-levels — S₃ Splitting Convergence
=============================================================
Runs v9b's eigenvalue pipeline for k = 8, 12, 15 using the existing
box-sampled balanced metric files.

Tests whether eigenvalues improve at higher k despite degraded η₂_w.
Extracts Z₃² charge decomposition and S₃ splitting at each level.
"""

import numpy as np
from scipy.linalg import eigh
from math import pi, sqrt
import time
import sys
import gc

sys.stdout.reconfigure(encoding='utf-8')

# ============================================================
# CONFIGURATION
# ============================================================

N_MC = 200000
DOMAIN_R = 5.0
MAX_DEGREE = 4          # 196 Galerkin basis functions
K_VALUES = [8, 12, 15]
RNG_SEED = 2026         # Same seed as v9b for reproducibility at k=8
ZETA3 = np.exp(2j * pi / 3)
C_FLOOR = 0.02

print("=" * 72)
print("EIGENVALUE SWEEP — S₃ SPLITTING CONVERGENCE")
print(f"k = {K_VALUES}, N_MC = {N_MC}, MAX_DEGREE = {MAX_DEGREE}")
print("=" * 72)


# ============================================================
# STAGE 1: SURFACE SAMPLING (identical to v9b)
# ============================================================

rng = np.random.default_rng(RNG_SEED)

print(f"\nStage 1: Surface sampling...")
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

ab, bb, cb = np.conj(a_all), np.conj(b_all), np.conj(c_all)
dc_da = -a_all**2 / c_all**2
dc_db = -b_all**2 / c_all**2
dcb_dab = np.conj(dc_da)
dcb_dbb = np.conj(dc_db)

# FS metric
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

dP_da  = ab + cb * dc_da            # ā + c̄·(dc/da) — holomorphic a-deriv of P
dP_dab = a_all + c_all * dcb_dab    # a + c·(dc̄/dā) — anti-hol a-deriv of P
dP_db  = bb + cb * dc_db            # b̄ + c̄·(dc/db)
dP_dbb = b_all + c_all * dcb_dbb    # b + c·(dc̄/db̄)

domain_vol = (2 * DOMAIN_R)**4
weights_FS = det_g_FS * domain_vol / (3 * N_MC)
vol_est = np.sum(weights_FS)
vol_exact = 3 * pi**2 / 2

print(f"  Points: {N_total}")
print(f"  Vol(FS) = {vol_est:.6f} (exact = {vol_exact:.6f}, ratio = {vol_est/vol_exact:.4f})")


# ============================================================
# STAGE 2: GALERKIN BASIS SETUP
# ============================================================

print(f"\nStage 2: Galerkin basis...")

max_pow = MAX_DEGREE + 1
a_pow = [np.ones(N_total, dtype=complex)]
b_pow = [np.ones(N_total, dtype=complex)]
c_pow = [np.ones(N_total, dtype=complex)]
ab_pow = [np.ones(N_total, dtype=complex)]
bb_pow = [np.ones(N_total, dtype=complex)]
cb_pow = [np.ones(N_total, dtype=complex)]
for i in range(1, max_pow):
    a_pow.append(a_pow[-1] * a_all)
    b_pow.append(b_pow[-1] * b_all)
    c_pow.append(c_pow[-1] * c_all)
    ab_pow.append(ab_pow[-1] * ab)
    bb_pow.append(bb_pow[-1] * bb)
    cb_pow.append(cb_pow[-1] * cb)

max_P_pow = MAX_DEGREE + 5 + 1
P_neg = [np.ones(N_total)]
for i in range(1, max_P_pow + 1):
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


monos_all = enumerate_monomials(MAX_DEGREE)
N_basis = len(monos_all)
print(f"  N_basis = {N_basis}")


# ============================================================
# EIGENVALUE COMPUTATION FUNCTION
# ============================================================

def compute_eigenvalues_at_k(bal_k, monos):
    """Compute O(0) eigenvalues using balanced metric at level bal_k."""
    print(f"\n{'='*60}")
    print(f"  Balanced metric k={bal_k}")
    print(f"{'='*60}")
    t_start = time.time()

    # Load balanced metric
    bal_data = np.load(f'balanced_metric_k{bal_k}.npz', allow_pickle=True)
    N_bal = int(bal_data['N_sections'])
    sec_norms = bal_data['section_norms']
    sections_info = bal_data['sections']
    eta_2_w = float(bal_data['eta_2_w'])
    delta_G_bal = float(bal_data['delta_G'])

    print(f"  N_sections={N_bal}, η₂_w={eta_2_w:.4f}, δG={delta_G_bal:.2e}")

    # Reconstruct full G matrix
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
                        G_full[i_global, j_global] = G_block[i_local, j_local]

    # Build section matrix at eigenvalue sample points
    logP = np.log(P)
    P_half_k = np.exp(-0.5 * bal_k * logP)

    a_pow_b = [np.ones(N_total, dtype=complex)]
    b_pow_b = [np.ones(N_total, dtype=complex)]
    c_pow_b = [np.ones(N_total, dtype=complex)]
    for i in range(1, bal_k + 1):
        a_pow_b.append(a_pow_b[-1] * a_all)
        b_pow_b.append(b_pow_b[-1] * b_all)
        if i <= 2:
            c_pow_b.append(c_pow_b[-1] * c_all)

    print(f"  Building section matrix ({N_bal} x {N_total})...")
    U = np.empty((N_bal, N_total), dtype=complex)
    for idx in range(N_bal):
        j1 = int(sections_info[idx, 0])
        j2 = int(sections_info[idx, 1])
        j3 = int(sections_info[idx, 2])
        U[idx] = a_pow_b[j1] * b_pow_b[j2] * c_pow_b[min(j3, 2)] * P_half_k / sec_norms[idx]
    print(f"    Memory: {U.nbytes/1e9:.2f} GB")

    V = G_full @ U
    rho_G = np.real(np.sum(np.conj(U) * V, axis=0))
    rho_safe = np.where(rho_G > 1e-30, rho_G, 1.0)

    # Balanced metric tensor via covariance formula
    R_a = dP_da / P
    R_b = dP_db / P
    inv_a = np.where(np.abs(a_all) > 1e-30, 1.0 / a_all, 0.0)
    inv_b = np.where(np.abs(b_all) > 1e-30, 1.0 / b_all, 0.0)
    dc_da_over_c = dc_da / c_all
    dc_db_over_c = dc_db / c_all

    Utilde_a = np.empty((N_bal, N_total), dtype=complex)
    Utilde_b = np.empty((N_bal, N_total), dtype=complex)
    for idx in range(N_bal):
        j1 = int(sections_info[idx, 0])
        j2 = int(sections_info[idx, 1])
        j3 = int(sections_info[idx, 2])
        D_a = (j1 * inv_a + j3 * dc_da_over_c) if (j1 > 0 or j3 > 0) else np.zeros(N_total, dtype=complex)
        D_b = (j2 * inv_b + j3 * dc_db_over_c) if (j2 > 0 or j3 > 0) else np.zeros(N_total, dtype=complex)
        Utilde_a[idx] = (D_a - bal_k * R_a) * U[idx]
        Utilde_b[idx] = (D_b - bal_k * R_b) * U[idx]

    W_a = G_full @ Utilde_a
    W_b = G_full @ Utilde_b

    UaGUa = np.real(np.sum(np.conj(Utilde_a) * W_a, axis=0))
    UbGUb = np.real(np.sum(np.conj(Utilde_b) * W_b, axis=0))
    UbGUa = np.sum(np.conj(Utilde_b) * W_a, axis=0)
    VdUa = np.sum(np.conj(V) * Utilde_a, axis=0)
    VdUb = np.sum(np.conj(V) * Utilde_b, axis=0)

    del Utilde_a, Utilde_b, W_a, W_b, U, V
    gc.collect()

    inv_rho = 1.0 / rho_safe
    inv_rho2 = inv_rho * inv_rho

    g_bal_11 = (1.0 / bal_k) * (UaGUa * inv_rho - np.abs(VdUa)**2 * inv_rho2)
    g_bal_22 = (1.0 / bal_k) * (UbGUb * inv_rho - np.abs(VdUb)**2 * inv_rho2)
    g_bal_12 = (1.0 / bal_k) * (UbGUa * inv_rho - VdUa * np.conj(VdUb) * inv_rho2)
    g_bal_21 = np.conj(g_bal_12)

    del UaGUa, UbGUb, UbGUa, VdUa, VdUb, inv_rho, inv_rho2
    gc.collect()

    det_g_bal = (g_bal_11 * g_bal_22 - g_bal_12 * g_bal_21).real

    # Positive-definiteness check + FS fallback
    pd_mask = (g_bal_11.real > 0) & (det_g_bal > 0) & np.isfinite(det_g_bal)
    fallback = ~pd_mask
    n_fallback = int(np.sum(fallback))
    print(f"  PD: {int(np.sum(pd_mask))}/{N_total} ({100*np.sum(pd_mask)/N_total:.1f}%), fallback: {n_fallback}")

    if n_fallback > 0:
        g_bal_11[fallback] = g_FS_11[fallback]
        g_bal_12[fallback] = g_FS_12[fallback]
        g_bal_21[fallback] = g_FS_21[fallback]
        g_bal_22[fallback] = g_FS_22[fallback]
        det_g_bal[fallback] = det_g_FS[fallback]

    weights_bal = det_g_bal * domain_vol / (3 * N_MC)
    vol_bal = np.sum(weights_bal)

    ds_bal = np.where(det_g_bal > 1e-20, det_g_bal, 1.0)
    ginv_bal_11 = (g_bal_22 / ds_bal).real
    ginv_bal_12 = -g_bal_12 / ds_bal
    ginv_bal_21 = -g_bal_21 / ds_bal
    ginv_bal_22 = (g_bal_11 / ds_bal).real

    print(f"  Vol(bal)={vol_bal:.4f}, Vol(FS)={vol_est:.4f}")

    del bal_data, G_full, g_bal_11, g_bal_12, g_bal_21, g_bal_22, det_g_bal
    gc.collect()

    # Build basis functions (O(0), n_twist=0)
    N_b = len(monos)
    basis_info = []
    F = []
    for (i1, j1, i2, j2, i3, j3, hol_deg, anti_deg) in monos:
        m = max(hol_deg, anti_deg)
        kk = m  # q=0 for O(0)
        mono_val = eval_monomial(i1, j1, i2, j2, i3, j3)
        phi = mono_val * P_neg[kk]
        F.append(phi)
        basis_info.append((i1, j1, i2, j2, i3, j3, m, kk))

    F = np.array(F)

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

    # Fiber metric h = P^0 = 1 for O(0)
    w = weights_bal

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
    del ginv_bal_11, ginv_bal_12, ginv_bal_21, ginv_bal_22, weights_bal
    gc.collect()

    # Eigensolve
    Qr = Q_mat.real
    Mr = M_mat.real
    del Q_mat, M_mat

    eigM = np.linalg.eigvalsh(Mr)
    Mmax = eigM[-1]
    Mr_reg = Mr + 1e-8 * Mmax * np.eye(N_b)

    eigvals, eigvecs = eigh(Qr, Mr_reg)
    order = np.argsort(eigvals)
    eigvals = eigvals[order]
    eigvecs = eigvecs[:, order]

    del Qr, Mr, Mr_reg
    gc.collect()

    # Filter physical eigenvalues
    pos = eigvals > 0.5
    eigvals_phys = eigvals[pos]
    eigvecs_phys = eigvecs[:, pos]

    n_zero = int(np.sum(~pos))
    n_pos = int(np.sum(pos))
    print(f"  Eigenvalues: {n_pos} physical, {n_zero} zero modes")
    if n_pos >= 3:
        print(f"  λ₁={eigvals_phys[0]:.4f}, λ₂={eigvals_phys[1]:.4f}, λ₃={eigvals_phys[2]:.4f}")

    # Z₃² charge decomposition
    basis_charges = []
    for (i1, j1, i2, j2, i3, j3, hol_deg, anti_deg) in monos:
        q1 = (i1 - j1) % 3
        q2 = (i2 - j2) % 3
        basis_charges.append((q1, q2))

    charge_results = []
    for eig_idx in range(min(10, n_pos)):
        vec = eigvecs_phys[:, eig_idx]
        vec_sq = np.abs(vec)**2
        total = np.sum(vec_sq)

        sector_weights = {}
        for m_idx, (q1, q2) in enumerate(basis_charges):
            key = (q1, q2)
            sector_weights[key] = sector_weights.get(key, 0) + vec_sq[m_idx]

        dominant = max(sector_weights, key=sector_weights.get)
        dom_frac = sector_weights[dominant] / total

        charge_results.append({
            'eigenvalue': float(eigvals_phys[eig_idx]),
            'dominant_sector': dominant,
            'dominant_weight': float(dom_frac),
        })

        orbit = "trivial" if dominant == (0,0) else \
                "standard" if dominant in [(1,0),(0,1),(2,2)] else \
                "conjugate" if dominant in [(2,0),(0,2),(1,1)] else "mixed"
        print(f"    λ_{eig_idx+1}={eigvals_phys[eig_idx]:.4f} → ({dominant[0]},{dominant[1]}) {orbit} w={dom_frac:.3f}")

    elapsed = time.time() - t_start
    print(f"  Time: {elapsed:.1f}s")

    return eigvals_phys, charge_results, eta_2_w


# ============================================================
# RUN FOR EACH k
# ============================================================

results = []

for bal_k in K_VALUES:
    eigvals, charges, eta_2_w = compute_eigenvalues_at_k(bal_k, monos_all)

    # Extract S₃ splitting
    lambda_10, lambda_01 = None, None
    for cr in charges:
        s = cr['dominant_sector']
        if s == (1, 0) and lambda_10 is None:
            lambda_10 = cr['eigenvalue']
        elif s == (0, 1) and lambda_01 is None:
            lambda_01 = cr['eigenvalue']

    splitting = abs(lambda_10 - lambda_01) if (lambda_10 is not None and lambda_01 is not None) else None

    results.append({
        'k': bal_k,
        'eta_2_w': eta_2_w,
        'lambda_1': float(eigvals[0]) if len(eigvals) > 0 else None,
        'lambda_2': float(eigvals[1]) if len(eigvals) > 1 else None,
        'lambda_3': float(eigvals[2]) if len(eigvals) > 2 else None,
        'lambda_10': lambda_10,
        'lambda_01': lambda_01,
        's3_splitting': splitting,
        'n_eigenvalues': len(eigvals),
        'charges': charges,
    })

    gc.collect()


# ============================================================
# CONVERGENCE TABLE
# ============================================================

print(f"\n{'='*72}")
print("S₃ SPLITTING CONVERGENCE TABLE")
print(f"{'='*72}")
print(f"{'k':>4s}  {'N_sec':>5s}  {'η₂_w':>8s}  {'λ₁':>8s}  {'λ₂':>8s}  {'λ(1,0)':>8s}  {'λ(0,1)':>8s}  {'split':>8s}  {'gap%':>6s}")
print("-" * 76)

N_k_formula = lambda k: (3 * k * k + 3 * k + 2) // 2
for r in results:
    gap = 100 * (1 - r['lambda_1'] / 1.5) if r['lambda_1'] else None
    lam10 = f"{r['lambda_10']:.4f}" if r['lambda_10'] else "  N/A "
    lam01 = f"{r['lambda_01']:.4f}" if r['lambda_01'] else "  N/A "
    split = f"{r['s3_splitting']:.4f}" if r['s3_splitting'] is not None else "  N/A "
    print(f"  {r['k']:3d}  {N_k_formula(r['k']):5d}  {r['eta_2_w']:8.4f}  "
          f"{r['lambda_1']:8.4f}  {r['lambda_2']:8.4f}  {lam10:>8s}  {lam01:>8s}  {split:>8s}  {gap:5.1f}%")

# Spectral zeta function estimate
print(f"\n{'='*72}")
print("SPECTRAL ZETA FUNCTION PREVIEW")
print(f"{'='*72}")

for r in results:
    eigvals = []
    for cr in r['charges']:
        eigvals.append(cr['eigenvalue'])
    # We only have ~10 eigenvalues from the charge analysis
    # Need the full eigenvalue array for zeta
    # Just report what we have
    print(f"  k={r['k']}: {r['n_eigenvalues']} physical eigenvalues")
    if r['n_eigenvalues'] >= 10:
        # Rough zeta'(0) estimate from first N eigenvalues (very rough)
        print(f"    (Full spectral zeta requires all eigenvalues — not computed in this sweep)")

print(f"\n{'='*72}")
print("PREDICTION: S₃ splitting should shrink as k increases")
print("  if balanced metric approaches KE.")
if len(results) >= 2 and all(r['s3_splitting'] is not None for r in results):
    s1 = results[0]['s3_splitting']
    s_last = results[-1]['s3_splitting']
    if s_last < s1:
        print(f"  CONFIRMED: splitting {s1:.4f} → {s_last:.4f} (shrinks by {100*(s1-s_last)/s1:.1f}%)")
    else:
        print(f"  NOT CONFIRMED: splitting {s1:.4f} → {s_last:.4f} (grows by {100*(s_last-s1)/s1:.1f}%)")
        print(f"  This suggests MC noise dominates over metric improvement at higher k.")
print(f"{'='*72}")

print(f"\n🦞🧍💜🔥♾️")
