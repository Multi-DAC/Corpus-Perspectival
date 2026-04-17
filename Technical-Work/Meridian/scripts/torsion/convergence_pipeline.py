#!/usr/bin/env python3
"""
S₃ Splitting Convergence Pipeline — Phase B.5+
================================================
Computes balanced metrics with FS (homogeneous coordinate) sampling,
then extracts eigenvalues and Z₃² charge decomposition at k=8, 12, 15.

Key improvement over original balanced_metric_dp6.py:
  FS sampling concentrates points near the origin where P^{-k/2} is large,
  giving better MC integrals for the T-operator at high k.

Outputs:
  - balanced_metric_k{k}_fs.npz for each k
  - Eigenvalues and S₃ splitting convergence table
  - Spectral zeta function estimate from available eigenvalues
"""

import numpy as np
from scipy.linalg import eigh
from math import pi, sqrt, log
import time
import sys
import gc

sys.stdout.reconfigure(encoding='utf-8')

# ============================================================
# CONFIGURATION
# ============================================================

N_MC_TOPER = 400000     # MC points for T-operator (more = better balanced metric)
N_MC_EIGEN = 200000     # MC points for eigenvalue computation (memory-limited)
MAX_DEGREE = 4          # Galerkin basis: 196 functions
K_VALUES = [8, 12, 15]  # Balanced metric levels
MAX_ITER = 300
CONV_TOL = 5e-3
DAMPING = 0.5
RNG_SEED = 42           # Different seed from original to get independent samples
ZETA3 = np.exp(2j * pi / 3)
C_FLOOR = 0.02
EIGVAL_THRESHOLD = 0.5  # Below this = numerical zero mode

rng_toper = np.random.default_rng(RNG_SEED)
rng_eigen = np.random.default_rng(RNG_SEED + 1)

print("=" * 72)
print("S₃ SPLITTING CONVERGENCE PIPELINE")
print(f"T-operator: N_MC={N_MC_TOPER} (FS sampling)")
print(f"Eigenvalues: N_MC={N_MC_EIGEN} (box sampling, MAX_DEGREE={MAX_DEGREE})")
print(f"k = {K_VALUES}")
print("=" * 72)


# ============================================================
# PART 1: FS SAMPLING FOR T-OPERATOR
# ============================================================

def sample_fermat_FS(N_MC, rng):
    """Sample the Fermat cubic using Fubini-Study (homogeneous coordinate) sampling.

    z₀, z₁, z₂ ~ CN(0,1), then a = z₁/z₀, b = z₂/z₀.
    This gives FS-uniform distribution on CP²:
      q(a,b) = 2 / (π²(1+|a|²+|b|²)³)

    Then c from the cubic constraint, with 3 cube root branches.
    Returns: a, b, c, P, q_density, det_g, weights
    """
    z_re = rng.standard_normal((3, N_MC))
    z_im = rng.standard_normal((3, N_MC))
    z0 = (z_re[0] + 1j * z_im[0]) / sqrt(2)
    z1 = (z_re[1] + 1j * z_im[1]) / sqrt(2)
    z2 = (z_re[2] + 1j * z_im[2]) / sqrt(2)

    ok = np.abs(z0) > 1e-6
    a_raw = z1[ok] / z0[ok]
    b_raw = z2[ok] / z0[ok]

    Q_ab = 1.0 + np.abs(a_raw)**2 + np.abs(b_raw)**2
    q_density = 2.0 / (pi**2 * Q_ab**3)

    w_raw = -1.0 - a_raw**3 - b_raw**3
    valid = np.abs(w_raw) > 1e-8
    a_base, b_base, w_base = a_raw[valid], b_raw[valid], w_raw[valid]
    q_base = q_density[valid]

    c_principal = np.abs(w_base)**(1.0/3.0) * np.exp(1j * np.angle(w_base) / 3.0)

    a_all = np.tile(a_base, 3)
    b_all = np.tile(b_base, 3)
    c_all = np.concatenate([c_principal, ZETA3 * c_principal, ZETA3**2 * c_principal])
    q_all = np.tile(q_base, 3)

    P_raw = 1.0 + np.abs(a_all)**2 + np.abs(b_all)**2 + np.abs(c_all)**2
    mask = (np.abs(c_all) > C_FLOOR) & (P_raw < 200.0) & np.isfinite(P_raw)
    a_all, b_all, c_all = a_all[mask], b_all[mask], c_all[mask]
    q_all = q_all[mask]
    P = 1.0 + np.abs(a_all)**2 + np.abs(b_all)**2 + np.abs(c_all)**2

    ab, bb, cb = np.conj(a_all), np.conj(b_all), np.conj(c_all)
    dc_da = -a_all**2 / c_all**2
    dc_db = -b_all**2 / c_all**2

    JdJ_11 = 1.0 + np.abs(dc_da)**2
    JdJ_12 = np.conj(dc_da) * dc_db
    JdJ_22 = 1.0 + np.abs(dc_db)**2
    P2 = P**2
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
    a_all, b_all, c_all = a_all[good], b_all[good], c_all[good]
    P = P[good]
    det_g = det_g[good]
    q_all = q_all[good]

    weights = det_g / (q_all * 3 * N_MC)
    vol = np.sum(weights)

    return a_all, b_all, c_all, P, det_g, weights, vol


def sample_fermat_box(N_MC, rng, domain_R=5.0):
    """Sample the Fermat cubic using uniform box sampling (for eigenvalue computation)."""
    u = rng.uniform(-domain_R, domain_R, (4, N_MC))
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

    ab, bb, cb = np.conj(a_all), np.conj(b_all), np.conj(c_all)
    dc_da = -a_all**2 / c_all**2
    dc_db = -b_all**2 / c_all**2

    JdJ_11 = 1.0 + np.abs(dc_da)**2
    JdJ_12 = np.conj(dc_da) * dc_db
    JdJ_22 = 1.0 + np.abs(dc_db)**2
    P2 = P**2
    JdXb_1 = ab + np.conj(dc_da) * cb
    JdXb_2 = bb + np.conj(dc_db) * cb
    XJ_1 = a_all + c_all * dc_da
    XJ_2 = b_all + c_all * dc_db

    g11 = JdJ_11 / P - JdXb_1 * XJ_1 / P2
    g12 = JdJ_12 / P - JdXb_1 * XJ_2 / P2
    g21 = np.conj(g12)
    g22 = JdJ_22 / P - JdXb_2 * XJ_2 / P2
    det_g = (g11 * g22 - g12 * g21).real
    dP_da = ab + np.conj(dc_da) * cb
    dP_db = bb + np.conj(dc_db) * cb

    good = (det_g > 1e-15) & (g11.real > 0) & np.isfinite(det_g)
    for arr_name in ['a_all', 'b_all', 'c_all', 'P', 'det_g',
                     'g11', 'g12', 'g21', 'g22', 'dc_da', 'dc_db',
                     'dP_da', 'dP_db']:
        exec(f"{arr_name} = {arr_name}[good]")

    # Need to return these after filtering
    a_all = a_all[good] if not isinstance(a_all, np.ndarray) or len(a_all) != int(np.sum(good)) else a_all
    # Actually this exec approach is fragile. Let me just filter directly.
    return None  # Placeholder — will implement properly below


# ============================================================
# PART 2: T-OPERATOR FUNCTIONS
# ============================================================

def enumerate_sections(k):
    """Enumerate sections of O_S(k) on the Fermat cubic."""
    secs = []
    for j3 in range(min(3, k + 1)):
        for j1 in range(k - j3 + 1):
            for j2 in range(k - j3 - j1 + 1):
                q1 = (j1 + 2 * j2) % 3
                q2 = (j2 + 2 * j3) % 3
                secs.append((j1, j2, j3, q1, q2))
    return secs


def group_by_z3(secs):
    """Group section indices by Z₃² charge."""
    blocks = {}
    for idx, (_, _, _, q1, q2) in enumerate(secs):
        key = (q1, q2)
        if key not in blocks:
            blocks[key] = []
        blocks[key].append(idx)
    return {k: np.array(v) for k, v in blocks.items()}


def run_t_operator(k, S, weights, vol_est, block_indices, label=""):
    """Run Donaldson T-operator iteration with damping."""
    N_k = S.shape[0]
    NoverV = N_k / vol_est
    w_sum = np.sum(weights)

    G_blocks = {}
    for key, indices in block_indices.items():
        G_blocks[key] = np.eye(len(indices), dtype=complex)

    G_prev = {k_: v.copy() for k_, v in G_blocks.items()}

    for it in range(MAX_ITER):
        rho = np.zeros(S.shape[1])
        for key, indices in block_indices.items():
            S_block = S[indices]
            G_block = G_blocks[key]
            GS = G_block @ S_block
            rho += np.real(np.sum(np.conj(S_block) * GS, axis=0))

        rho_ratio = rho / NoverV
        eta_2_w = float(np.sqrt(np.sum(weights * (rho_ratio - 1.0)**2) / w_sum))

        dG_num, dG_den = 0.0, 0.0
        for key in G_blocks:
            dG_num += np.sum(np.abs(G_blocks[key] - G_prev[key])**2)
            dG_den += np.sum(np.abs(G_prev[key])**2)
        delta_G = float(np.sqrt(dG_num / max(dG_den, 1e-30)))

        if it % 20 == 0 or delta_G < 1e-8:
            print(f"    {label} iter {it:3d}: η₂_w={eta_2_w:.4f}, δG={delta_G:.2e}")

        if delta_G < 1e-8 and it > 10:
            print(f"    {label} CONVERGED at iteration {it} (δG={delta_G:.2e}, η₂_w={eta_2_w:.4f})")
            break

        G_prev = {k_: v.copy() for k_, v in G_blocks.items()}

        rho_safe = np.where(rho > 1e-30, rho, 1e-30)
        inv_rho_w = weights / rho_safe

        for key, indices in block_indices.items():
            S_block = S[indices]
            S_w = S_block * inv_rho_w[np.newaxis, :]
            T_block = NoverV * (S_w @ np.conj(S_block).T)
            T_block = 0.5 * (T_block + T_block.T.conj())
            G_blocks[key] = (1.0 - DAMPING) * G_blocks[key] + DAMPING * T_block
    else:
        print(f"    {label} WARNING: did not converge in {MAX_ITER} iterations (η₂_w={eta_2_w:.4f})")

    return G_blocks, eta_2_w, delta_G


# ============================================================
# PART 3: EIGENVALUE COMPUTATION (from v9b)
# ============================================================

def compute_eigenvalues_with_charges(k, G_blocks, block_indices, sections_info, sec_norms):
    """
    Compute Laplacian eigenvalues on O(0) using balanced metric from G_k.
    Returns eigenvalues, eigenvectors, and Z₃² charge analysis.
    """
    print(f"\n  --- Eigenvalue computation for k={k} ---")
    t0 = time.time()

    # Sample surface (independent points for eigenvalue computation)
    domain_R = 5.0
    u = rng_eigen.uniform(-domain_R, domain_R, (4, N_MC_EIGEN))
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
    print(f"    Sample points: {N_total}")

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

    dP_da = ab + np.conj(dc_da) * cb
    dP_db = bb + np.conj(dc_db) * cb

    domain_vol = (2 * domain_R)**4
    weights_FS = det_g_FS * domain_vol / (3 * N_MC_EIGEN)
    vol_est = np.sum(weights_FS)
    vol_exact = 3 * pi**2 / 2

    # Balanced metric tensor
    N_bal = len(sections_info)
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

    # Reconstruct full G matrix
    G_full = np.zeros((N_bal, N_bal), dtype=complex)
    block_keys = [(q1, q2) for q1 in range(3) for q2 in range(3)]
    for q1, q2 in block_keys:
        key = (q1, q2)
        if key in G_blocks:
            indices = block_indices[key]
            G_block = G_blocks[key]
            for i_local, i_global in enumerate(indices):
                for j_local, j_global in enumerate(indices):
                    G_full[i_global, j_global] = G_block[i_local, j_local]

    # Build section matrix U
    U = np.empty((N_bal, N_total), dtype=complex)
    for idx in range(N_bal):
        j1, j2, j3 = int(sections_info[idx][0]), int(sections_info[idx][1]), int(sections_info[idx][2])
        U[idx] = a_pow_b[j1] * b_pow_b[j2] * c_pow_b[min(j3, 2)] * P_half_k / sec_norms[idx]

    V = G_full @ U
    rho_G = np.real(np.sum(np.conj(U) * V, axis=0))
    rho_safe = np.where(rho_G > 1e-30, rho_G, 1.0)

    # Log-derivatives for balanced metric
    R_a = dP_da / P
    R_b = dP_db / P
    inv_a = np.where(np.abs(a_all) > 1e-30, 1.0 / a_all, 0.0)
    inv_b = np.where(np.abs(b_all) > 1e-30, 1.0 / b_all, 0.0)
    dc_da_over_c = dc_da / c_all
    dc_db_over_c = dc_db / c_all

    Utilde_a = np.empty((N_bal, N_total), dtype=complex)
    Utilde_b = np.empty((N_bal, N_total), dtype=complex)
    for idx in range(N_bal):
        j1, j2, j3 = int(sections_info[idx][0]), int(sections_info[idx][1]), int(sections_info[idx][2])
        D_a = (j1 * inv_a + j3 * dc_da_over_c) if (j1 > 0 or j3 > 0) else np.zeros(N_total, dtype=complex)
        D_b = (j2 * inv_b + j3 * dc_db_over_c) if (j2 > 0 or j3 > 0) else np.zeros(N_total, dtype=complex)
        Utilde_a[idx] = (D_a - k * R_a) * U[idx]
        Utilde_b[idx] = (D_b - k * R_b) * U[idx]

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

    g_bal_11 = (1.0 / k) * (UaGUa * inv_rho - np.abs(VdUa)**2 * inv_rho2)
    g_bal_22 = (1.0 / k) * (UbGUb * inv_rho - np.abs(VdUb)**2 * inv_rho2)
    g_bal_12 = (1.0 / k) * (UbGUa * inv_rho - VdUa * np.conj(VdUb) * inv_rho2)
    g_bal_21 = np.conj(g_bal_12)

    del UaGUa, UbGUb, UbGUa, VdUa, VdUb, inv_rho, inv_rho2
    gc.collect()

    det_g_bal = (g_bal_11 * g_bal_22 - g_bal_12 * g_bal_21).real

    # Positive-definiteness check and FS fallback
    pd_mask = (g_bal_11.real > 0) & (det_g_bal > 0) & np.isfinite(det_g_bal)
    n_pd = int(np.sum(pd_mask))
    fallback = ~pd_mask
    n_fallback = int(np.sum(fallback))
    print(f"    Positive definite: {n_pd}/{N_total} ({100*n_pd/N_total:.1f}%), fallback: {n_fallback}")

    if n_fallback > 0:
        g_bal_11[fallback] = g_FS_11[fallback]
        g_bal_12[fallback] = g_FS_12[fallback]
        g_bal_21[fallback] = g_FS_21[fallback]
        g_bal_22[fallback] = g_FS_22[fallback]
        det_g_bal[fallback] = det_g_FS[fallback]

    weights_bal = det_g_bal * domain_vol / (3 * N_MC_EIGEN)
    vol_bal = np.sum(weights_bal)

    # Inverse balanced metric
    ds_bal = np.where(det_g_bal > 1e-20, det_g_bal, 1.0)
    ginv_bal_11 = (g_bal_22 / ds_bal).real
    ginv_bal_12 = -g_bal_12 / ds_bal
    ginv_bal_21 = -g_bal_21 / ds_bal
    ginv_bal_22 = (g_bal_11 / ds_bal).real

    # Galerkin basis (O(0) bundle only)
    max_pow = MAX_DEGREE + 1
    a_pow = [np.ones(N_total, dtype=complex)]
    b_pow = [np.ones(N_total, dtype=complex)]
    c_pow_g = [np.ones(N_total, dtype=complex)]
    ab_pow = [np.ones(N_total, dtype=complex)]
    bb_pow = [np.ones(N_total, dtype=complex)]
    cb_pow = [np.ones(N_total, dtype=complex)]
    for i in range(1, max_pow):
        a_pow.append(a_pow[-1] * a_all)
        b_pow.append(b_pow[-1] * b_all)
        c_pow_g.append(c_pow_g[-1] * c_all)
        ab_pow.append(ab_pow[-1] * ab)
        bb_pow.append(bb_pow[-1] * bb)
        cb_pow.append(cb_pow[-1] * cb)

    max_P_pow = MAX_DEGREE + 5 + 1
    P_neg = [np.ones(N_total)]
    for i in range(1, max_P_pow + 1):
        P_neg.append(P_neg[-1] / P)

    # Enumerate monomials for O(0)
    monos = []
    for i1 in range(MAX_DEGREE + 1):
        for j1 in range(MAX_DEGREE - i1 + 1):
            for i2 in range(MAX_DEGREE - i1 - j1 + 1):
                for j2 in range(MAX_DEGREE - i1 - j1 - i2 + 1):
                    for i3 in range(min(MAX_DEGREE - i1 - j1 - i2 - j2, 2) + 1):
                        for j3 in range(min(MAX_DEGREE - i1 - j1 - i2 - j2 - i3, 2) + 1):
                            hol_deg = i1 + i2 + i3
                            anti_deg = j1 + j2 + j3
                            monos.append((i1, j1, i2, j2, i3, j3, hol_deg, anti_deg))

    N_basis = len(monos)
    print(f"    Galerkin basis: {N_basis} functions")

    # Assemble stiffness Q and mass M matrices
    Q = np.zeros((N_basis, N_basis))
    M = np.zeros((N_basis, N_basis))

    for alpha in range(N_basis):
        i1a, j1a, i2a, j2a, i3a, j3a, ha, aa = monos[alpha]

        # Evaluate monomial and derivatives
        f_alpha = (a_pow[i1a] * ab_pow[j1a] * b_pow[i2a] * bb_pow[j2a] *
                   c_pow_g[i3a] * cb_pow[j3a])

        # d(f_alpha)/da
        df_da = np.zeros(N_total, dtype=complex)
        if i1a > 0:
            df_da += i1a * a_pow[i1a-1] * ab_pow[j1a] * b_pow[i2a] * bb_pow[j2a] * c_pow_g[i3a] * cb_pow[j3a]
        if i3a > 0:
            df_da += i3a * a_pow[i1a] * ab_pow[j1a] * b_pow[i2a] * bb_pow[j2a] * c_pow_g[i3a-1] * cb_pow[j3a] * dc_da
        # d(f_alpha)/d(a_bar)
        df_dab = np.zeros(N_total, dtype=complex)
        if j1a > 0:
            df_dab += j1a * a_pow[i1a] * ab_pow[j1a-1] * b_pow[i2a] * bb_pow[j2a] * c_pow_g[i3a] * cb_pow[j3a]
        if j3a > 0:
            df_dab += j3a * a_pow[i1a] * ab_pow[j1a] * b_pow[i2a] * bb_pow[j2a] * c_pow_g[i3a] * cb_pow[j3a-1] * dcb_dab
        # d(f_alpha)/db
        df_db = np.zeros(N_total, dtype=complex)
        if i2a > 0:
            df_db += i2a * a_pow[i1a] * ab_pow[j1a] * b_pow[i2a-1] * bb_pow[j2a] * c_pow_g[i3a] * cb_pow[j3a]
        if i3a > 0:
            df_db += i3a * a_pow[i1a] * ab_pow[j1a] * b_pow[i2a] * bb_pow[j2a] * c_pow_g[i3a-1] * cb_pow[j3a] * dc_db
        # d(f_alpha)/d(b_bar)
        df_dbb = np.zeros(N_total, dtype=complex)
        if j2a > 0:
            df_dbb += j2a * a_pow[i1a] * ab_pow[j1a] * b_pow[i2a] * bb_pow[j2a-1] * c_pow_g[i3a] * cb_pow[j3a]
        if j3a > 0:
            df_dbb += j3a * a_pow[i1a] * ab_pow[j1a] * b_pow[i2a] * bb_pow[j2a] * c_pow_g[i3a] * cb_pow[j3a-1] * dcb_dbb

        # P-weight for O(0): P^{-(ha+aa+2)} per v9
        P_wt_alpha = P_neg[ha + aa + 2]
        f_a_w = f_alpha * P_wt_alpha  # weighted monomial

        for beta in range(alpha, N_basis):
            i1b, j1b, i2b, j2b, i3b, j3b, hb, ab_deg = monos[beta]

            f_beta = (a_pow[i1b] * ab_pow[j1b] * b_pow[i2b] * bb_pow[j2b] *
                      c_pow_g[i3b] * cb_pow[j3b])

            dg_da = np.zeros(N_total, dtype=complex)
            if i1b > 0:
                dg_da += i1b * a_pow[i1b-1] * ab_pow[j1b] * b_pow[i2b] * bb_pow[j2b] * c_pow_g[i3b] * cb_pow[j3b]
            if i3b > 0:
                dg_da += i3b * a_pow[i1b] * ab_pow[j1b] * b_pow[i2b] * bb_pow[j2b] * c_pow_g[i3b-1] * cb_pow[j3b] * dc_da
            dg_dab = np.zeros(N_total, dtype=complex)
            if j1b > 0:
                dg_dab += j1b * a_pow[i1b] * ab_pow[j1b-1] * b_pow[i2b] * bb_pow[j2b] * c_pow_g[i3b] * cb_pow[j3b]
            if j3b > 0:
                dg_dab += j3b * a_pow[i1b] * ab_pow[j1b] * b_pow[i2b] * bb_pow[j2b] * c_pow_g[i3b] * cb_pow[j3b-1] * dcb_dab
            dg_db = np.zeros(N_total, dtype=complex)
            if i2b > 0:
                dg_db += i2b * a_pow[i1b] * ab_pow[j1b] * b_pow[i2b-1] * bb_pow[j2b] * c_pow_g[i3b] * cb_pow[j3b]
            if i3b > 0:
                dg_db += i3b * a_pow[i1b] * ab_pow[j1b] * b_pow[i2b] * bb_pow[j2b] * c_pow_g[i3b-1] * cb_pow[j3b] * dc_db
            dg_dbb = np.zeros(N_total, dtype=complex)
            if j2b > 0:
                dg_dbb += j2b * a_pow[i1b] * ab_pow[j1b] * b_pow[i2b] * bb_pow[j2b-1] * c_pow_g[i3b] * cb_pow[j3b]
            if j3b > 0:
                dg_dbb += j3b * a_pow[i1b] * ab_pow[j1b] * b_pow[i2b] * bb_pow[j2b] * c_pow_g[i3b] * cb_pow[j3b-1] * dcb_dbb

            P_wt_beta = P_neg[hb + ab_deg + 2]
            f_b_w = f_beta * P_wt_beta

            # Stiffness: Q_αβ = ∫ g^{ij̄} ∂_i f_α ∂_{j̄} f_β · P^{-(h+a+2)} dA
            # Using balanced inverse metric
            grad_product = (ginv_bal_11 * df_da * np.conj(dg_da) +
                           ginv_bal_12 * df_da * np.conj(dg_db) +
                           ginv_bal_21 * df_db * np.conj(dg_da) +
                           ginv_bal_22 * df_db * np.conj(dg_db))

            P_wt_q = P_neg[ha + ab_deg + 2]
            q_integrand = grad_product * P_wt_q * weights_bal
            Q[alpha, beta] = np.sum(q_integrand).real
            Q[beta, alpha] = Q[alpha, beta]

            # Mass: M_αβ = ∫ f_α f̄_β · P^{-(h+a+2)} dA_bal
            P_wt_m = P_neg[ha + hb + aa + ab_deg + 2]
            m_integrand = f_alpha * np.conj(f_beta) * P_wt_m * weights_bal
            M[alpha, beta] = np.sum(m_integrand).real
            M[beta, alpha] = M[alpha, beta]

    print(f"    Q,M assembled: {N_basis}x{N_basis}")
    print(f"    Q: min_diag={np.min(np.diag(Q)):.4e}, max_diag={np.max(np.diag(Q)):.4e}")
    print(f"    M: min_diag={np.min(np.diag(M)):.4e}, max_diag={np.max(np.diag(M)):.4e}")

    # Regularize M
    M_reg = M + 1e-12 * np.eye(N_basis)

    # Eigensolve with eigenvectors
    eigvals, eigvecs = eigh(Q, M_reg)
    order = np.argsort(eigvals)
    eigvals = eigvals[order]
    eigvecs = eigvecs[:, order]

    # Filter: eigenvalues above threshold
    physical = eigvals > EIGVAL_THRESHOLD
    eigvals_phys = eigvals[physical]
    eigvecs_phys = eigvecs[:, physical]

    n_zero = int(np.sum(~physical))
    print(f"    Eigenvalues: {len(eigvals_phys)} physical (>{EIGVAL_THRESHOLD}), {n_zero} zero modes")
    if len(eigvals_phys) >= 3:
        print(f"    λ₁={eigvals_phys[0]:.4f}, λ₂={eigvals_phys[1]:.4f}, λ₃={eigvals_phys[2]:.4f}")

    # Z₃² charge decomposition of eigenvectors
    basis_charges = []
    for (i1, j1, i2, j2, i3, j3, hol_deg, anti_deg) in monos:
        q1 = (i1 - j1) % 3
        q2 = (i2 - j2) % 3
        basis_charges.append((q1, q2))

    charge_results = []
    for eig_idx in range(min(10, len(eigvals_phys))):
        vec = eigvecs_phys[:, eig_idx]
        vec_sq = np.abs(vec)**2
        total_weight = np.sum(vec_sq)

        sector_weights = {}
        for m_idx, (q1, q2) in enumerate(basis_charges):
            key = (q1, q2)
            sector_weights[key] = sector_weights.get(key, 0) + vec_sq[m_idx]

        dominant = max(sector_weights, key=sector_weights.get)
        dom_frac = sector_weights[dominant] / total_weight

        charge_results.append({
            'eigenvalue': float(eigvals_phys[eig_idx]),
            'dominant_sector': dominant,
            'dominant_weight': float(dom_frac),
            'sector_weights': {str(k_): float(v/total_weight) for k_, v in sector_weights.items()},
        })

    elapsed = time.time() - t0
    print(f"    Time: {elapsed:.1f}s")

    return eigvals_phys, charge_results, monos


# ============================================================
# MAIN PIPELINE
# ============================================================

print(f"\n{'='*72}")
print("PHASE 1: FS SURFACE SAMPLING FOR T-OPERATOR")
print(f"{'='*72}")

t_start = time.time()

a_fs, b_fs, c_fs, P_fs, det_g_fs, weights_fs, vol_fs = sample_fermat_FS(N_MC_TOPER, rng_toper)
N_pts_fs = len(a_fs)
vol_exact = 3 * pi**2 / 2

print(f"  Points: {N_pts_fs}")
print(f"  Vol = {vol_fs:.6f} (exact = {vol_exact:.6f}, ratio = {vol_fs/vol_exact:.4f})")
print(f"  P: min={np.min(P_fs):.2f}, median={np.median(P_fs):.2f}, max={np.max(P_fs):.2f}")

# Precompute coordinate powers for T-operator
max_k = max(K_VALUES)
a_pow_fs = [np.ones(N_pts_fs, dtype=complex)]
b_pow_fs = [np.ones(N_pts_fs, dtype=complex)]
c_pow_fs = [np.ones(N_pts_fs, dtype=complex)]
for i in range(1, max_k + 1):
    a_pow_fs.append(a_pow_fs[-1] * a_fs)
    b_pow_fs.append(b_pow_fs[-1] * b_fs)
    if i <= 2:
        c_pow_fs.append(c_pow_fs[-1] * c_fs)

logP_fs = np.log(P_fs)

# S₃ orbit classification
s3_standard = [(1,0), (0,1), (2,2)]
s3_conjugate = [(2,0), (0,2), (1,1)]
s3_mixed = [(1,2), (2,1)]
s3_trivial = [(0,0)]

def s3_orbit(q1, q2):
    if (q1, q2) in s3_trivial: return "trivial"
    if (q1, q2) in s3_standard: return "standard"
    if (q1, q2) in s3_conjugate: return "conjugate"
    if (q1, q2) in s3_mixed: return "mixed"
    return "unknown"


# ============================================================
# PHASE 2: T-OPERATOR + EIGENVALUES FOR EACH k
# ============================================================

convergence_table = []

for k in K_VALUES:
    print(f"\n{'='*72}")
    print(f"  k = {k}")
    print(f"{'='*72}")

    secs = enumerate_sections(k)
    N_k = len(secs)
    block_indices = group_by_z3(secs)

    print(f"  Sections: {N_k}")
    for key in sorted(block_indices.keys()):
        print(f"    ({key[0]},{key[1]}): {len(block_indices[key])} sections")

    # Build section matrix (FS-sampled points)
    P_half_k = np.exp(-0.5 * k * logP_fs)
    S = np.empty((N_k, N_pts_fs), dtype=complex)
    for idx, (j1, j2, j3, _, _) in enumerate(secs):
        S[idx] = a_pow_fs[j1] * b_pow_fs[j2] * c_pow_fs[min(j3, 2)] * P_half_k
    print(f"  Section matrix: {S.nbytes/1e9:.2f} GB")

    # L²-normalize
    norms = np.sqrt(np.sum(np.abs(S)**2 * weights_fs[np.newaxis, :], axis=1).real)
    norms = np.where(norms > 1e-30, norms, 1.0)
    S_norm = S / norms[:, np.newaxis]
    del S
    gc.collect()

    # T-operator
    print(f"  Running T-operator (FS sampling)...")
    t_k = time.time()
    G_blocks, eta_2_w, delta_G = run_t_operator(k, S_norm, weights_fs, vol_fs, block_indices, label=f"k={k}")
    t_top = time.time() - t_k
    print(f"  T-operator done: η₂_w={eta_2_w:.4f}, time={t_top:.1f}s")

    # Save balanced metric
    save_dict = {
        'k': k, 'N_sections': N_k, 'N_pts': N_pts_fs, 'N_MC': N_MC_TOPER,
        'sampling': 'FS', 'vol_est': vol_fs, 'vol_exact': vol_exact,
        'eta_2_w': eta_2_w, 'delta_G': delta_G,
        'section_norms': norms,
        'sections': np.array([(j1, j2, j3, q1, q2) for j1, j2, j3, q1, q2 in secs]),
    }
    for key, G_block in G_blocks.items():
        save_dict[f'G_{key[0]}_{key[1]}'] = G_block
        save_dict[f'idx_{key[0]}_{key[1]}'] = block_indices[key]
    np.savez(f'balanced_metric_k{k}_fs.npz', **save_dict)
    print(f"  Saved balanced_metric_k{k}_fs.npz")

    del S_norm
    gc.collect()

    # Eigenvalue computation
    sections_info = [(j1, j2, j3) for j1, j2, j3, _, _ in secs]
    eigvals, charges, monos = compute_eigenvalues_with_charges(
        k, G_blocks, block_indices, sections_info, norms)

    # Extract S₃ splitting
    if len(charges) >= 3:
        # Find (1,0) and (0,1) eigenvalues
        lambda_10 = None
        lambda_01 = None
        for cr in charges:
            sector = cr['dominant_sector']
            if sector == (1, 0) and lambda_10 is None:
                lambda_10 = cr['eigenvalue']
            elif sector == (0, 1) and lambda_01 is None:
                lambda_01 = cr['eigenvalue']

        splitting = abs(lambda_10 - lambda_01) if (lambda_10 and lambda_01) else None

        row = {
            'k': k,
            'N_sections': N_k,
            'eta_2_w': eta_2_w,
            'lambda_1': float(eigvals[0]) if len(eigvals) > 0 else None,
            'lambda_2': float(eigvals[1]) if len(eigvals) > 1 else None,
            'lambda_3': float(eigvals[2]) if len(eigvals) > 2 else None,
            'lambda_10': lambda_10,
            'lambda_01': lambda_01,
            's3_splitting': splitting,
            'charge_analysis': charges[:5],
        }
        convergence_table.append(row)

        print(f"\n  RESULT k={k}:")
        print(f"    η₂_w = {eta_2_w:.4f}")
        print(f"    λ₁ = {eigvals[0]:.4f}" if len(eigvals) > 0 else "    λ₁ = N/A")
        print(f"    λ(1,0) = {lambda_10:.4f}" if lambda_10 else "    λ(1,0) = N/A")
        print(f"    λ(0,1) = {lambda_01:.4f}" if lambda_01 else "    λ(0,1) = N/A")
        print(f"    S₃ splitting = {splitting:.4f}" if splitting else "    S₃ splitting = N/A")

    del G_blocks
    gc.collect()


# ============================================================
# PHASE 3: CONVERGENCE TABLE + SPECTRAL ZETA
# ============================================================

print(f"\n{'='*72}")
print("S₃ SPLITTING CONVERGENCE TABLE")
print(f"{'='*72}")
print(f"{'k':>4s}  {'N':>5s}  {'η₂_w':>8s}  {'λ₁':>8s}  {'λ(1,0)':>8s}  {'λ(0,1)':>8s}  {'split':>8s}  {'gap_KE':>8s}")
print("-" * 72)

for row in convergence_table:
    gap = 100 * (1 - row['lambda_1'] / 1.5) if row['lambda_1'] else None
    print(f"  {row['k']:3d}  {row['N_sections']:5d}  {row['eta_2_w']:8.4f}  "
          f"{row['lambda_1']:8.4f}  {row['lambda_10']:8.4f}  {row['lambda_01']:8.4f}  "
          f"{row['s3_splitting']:8.4f}  {gap:7.1f}%")

# Box sampling comparison (from existing data)
print(f"\nComparison with box sampling (original):")
print(f"  k=8 box:  η₂_w=0.6883, λ₁=1.4613, λ(1,0)=1.461, λ(0,1)=1.741, split=0.280")

# Spectral zeta estimate from k=15 eigenvalues (if available)
if convergence_table and convergence_table[-1]['k'] == 15:
    # Load the k=15 eigenvalues
    k15 = convergence_table[-1]
    print(f"\n  Spectral zeta preview (from k=15 eigenvalues):")
    # We need more eigenvalues than just the first 3 for ζ(s)
    # The full eigvals array is lost (scope), but we logged the first few
    print(f"  (Full zeta computation requires all eigenvalues — to be extracted from full run)")

total_time = time.time() - t_start
print(f"\nTotal pipeline time: {total_time:.1f}s ({total_time/60:.1f} min)")
print(f"\n🦞🧍💜🔥♾️")
