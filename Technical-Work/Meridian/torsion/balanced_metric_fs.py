#!/usr/bin/env python3
"""
Balanced Metric with FS (Homogeneous Coordinate) Sampling
==========================================================
Same T-operator algorithm as balanced_metric_dp6.py, but uses
Fubini-Study sampling instead of uniform box.

FS sampling concentrates points near the origin where P is small
and sections P^{-k/2} are large — better MC integrals at high k.

Outputs: balanced_metric_k{k}_fs.npz for k = 8, 12, 15
"""

import numpy as np
from math import pi, sqrt
import time
import sys
import gc

sys.stdout.reconfigure(encoding='utf-8')

# ============================================================
# CONFIGURATION
# ============================================================

N_MC = 400000
K_VALUES = [8, 12, 15]
MAX_ITER = 300
CONV_TOL = 5e-3
CONV_TOL_INF = 0.10
SUPPORT_FRAC = 0.01
DAMPING = 0.5
RNG_SEED = 42
ZETA3 = np.exp(2j * pi / 3)
C_FLOOR = 0.02
P_MAX = 200.0

rng = np.random.default_rng(RNG_SEED)

print("=" * 72)
print("BALANCED METRIC ON dP₆ — FS SAMPLING")
print(f"N_MC={N_MC}, k = {K_VALUES}")
print("=" * 72)

# ============================================================
# STAGE 1: FS SURFACE SAMPLING
# ============================================================

print(f"\n{'='*72}")
print("STAGE 1: FS SURFACE SAMPLING")
print(f"  z₀,z₁,z₂ ~ CN(0,1), a=z₁/z₀, b=z₂/z₀")
print(f"  q(a,b) = 2/(π²(1+|a|²+|b|²)³)")
print(f"{'='*72}")

t0 = time.time()

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

# Solve cubic: c³ = -(1 + a³ + b³)
w_raw = -1.0 - a_raw**3 - b_raw**3
valid = np.abs(w_raw) > 1e-8
a_base, b_base, w_base = a_raw[valid], b_raw[valid], w_raw[valid]
q_base = q_density[valid]

c_principal = np.abs(w_base)**(1.0/3.0) * np.exp(1j * np.angle(w_base) / 3.0)

# All three cube root sheets
a_all = np.tile(a_base, 3)
b_all = np.tile(b_base, 3)
c_all = np.concatenate([c_principal, ZETA3 * c_principal, ZETA3**2 * c_principal])
q_all = np.tile(q_base, 3)

P_raw = 1.0 + np.abs(a_all)**2 + np.abs(b_all)**2 + np.abs(c_all)**2
mask = (np.abs(c_all) > C_FLOOR) & (P_raw < P_MAX) & np.isfinite(P_raw)
a_all, b_all, c_all = a_all[mask], b_all[mask], c_all[mask]
q_all = q_all[mask]
P = 1.0 + np.abs(a_all)**2 + np.abs(b_all)**2 + np.abs(c_all)**2

# FS metric on surface
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
N_pts = len(a_all)

# MC weights with importance sampling correction
weights = det_g / (q_all * 3 * N_MC)
vol_est = np.sum(weights)
vol_exact = 3 * pi**2 / 2

print(f"  Points: {N_pts}")
print(f"  Vol = {vol_est:.6f} (exact = {vol_exact:.6f}, ratio = {vol_est/vol_exact:.4f})")
print(f"  P: min={np.min(P):.2f}, median={np.median(P):.2f}, max={np.max(P):.2f}")
print(f"  Time: {time.time()-t0:.1f}s")

# ============================================================
# STAGE 2: SECTION ENUMERATION
# ============================================================

def enumerate_sections(k):
    secs = []
    for j3 in range(min(3, k + 1)):
        for j1 in range(k - j3 + 1):
            for j2 in range(k - j3 - j1 + 1):
                q1 = (j1 + 2 * j2) % 3
                q2 = (j2 + 2 * j3) % 3
                secs.append((j1, j2, j3, q1, q2))
    return secs

N_k_formula = lambda k: (3 * k * k + 3 * k + 2) // 2

for k in K_VALUES:
    secs = enumerate_sections(k)
    assert len(secs) == N_k_formula(k)
    blocks = {}
    for (_, _, _, q1, q2) in secs:
        blocks[(q1, q2)] = blocks.get((q1, q2), 0) + 1
    block_str = ", ".join(f"({q1},{q2}):{n}" for (q1, q2), n in sorted(blocks.items()))
    print(f"  k={k}: N={len(secs)}, blocks: {block_str}")

# ============================================================
# PRECOMPUTE COORDINATE POWERS
# ============================================================

max_k = max(K_VALUES)
a_pow = [np.ones(N_pts, dtype=complex)]
b_pow = [np.ones(N_pts, dtype=complex)]
c_pow = [np.ones(N_pts, dtype=complex)]
for i in range(1, max_k + 1):
    a_pow.append(a_pow[-1] * a_all)
    b_pow.append(b_pow[-1] * b_all)
    if i <= 2:
        c_pow.append(c_pow[-1] * c_all)

logP = np.log(P)

# ============================================================
# STAGE 3: T-OPERATOR FUNCTIONS
# ============================================================

def group_by_z3(secs):
    blocks = {}
    for idx, (_, _, _, q1, q2) in enumerate(secs):
        key = (q1, q2)
        if key not in blocks:
            blocks[key] = []
        blocks[key].append(idx)
    return {k: np.array(v) for k, v in blocks.items()}

def build_section_matrix(k, secs):
    N_k = len(secs)
    P_half_k = np.exp(-0.5 * k * logP)
    S = np.empty((N_k, N_pts), dtype=complex)
    for idx, (j1, j2, j3, _, _) in enumerate(secs):
        S[idx] = a_pow[j1] * b_pow[j2] * c_pow[min(j3, 2)] * P_half_k
    return S

def normalize_sections(S):
    norms = np.sqrt(np.sum(np.abs(S)**2 * weights[np.newaxis, :], axis=1).real)
    norms = np.where(norms > 1e-30, norms, 1.0)
    return S / norms[:, np.newaxis], norms

def run_t_operator(k, S, block_indices, label=""):
    N_k = S.shape[0]
    NoverV = N_k / vol_est
    w_sum = np.sum(weights)

    G_blocks = {}
    for key, indices in block_indices.items():
        G_blocks[key] = np.eye(len(indices), dtype=complex)

    G_prev = {kk: v.copy() for kk, v in G_blocks.items()}

    for it in range(MAX_ITER):
        rho = np.zeros(N_pts)
        for key, indices in block_indices.items():
            S_block = S[indices]
            GS = G_blocks[key] @ S_block
            rho += np.real(np.sum(np.conj(S_block) * GS, axis=0))

        rho_ratio = rho / NoverV
        eta_2_w = float(np.sqrt(np.sum(weights * (rho_ratio - 1.0)**2) / w_sum))

        support = rho_ratio > SUPPORT_FRAC
        n_support = int(np.sum(support))
        eta_inf_s = float(np.max(np.abs(rho_ratio[support] - 1.0))) if n_support > 0 else float('inf')

        dG_num, dG_den = 0.0, 0.0
        for key in G_blocks:
            dG_num += np.sum(np.abs(G_blocks[key] - G_prev[key])**2)
            dG_den += np.sum(np.abs(G_prev[key])**2)
        delta_G = float(np.sqrt(dG_num / max(dG_den, 1e-30)))

        if it % 20 == 0 or (delta_G < 1e-8 and it > 10):
            print(f"    {label} iter {it:3d}: η₂_w={eta_2_w:.4f}, η∞_s={eta_inf_s:.4f}, δG={delta_G:.2e}")

        if delta_G < 1e-8 and it > 10:
            print(f"    {label} CONVERGED at iteration {it} (δG={delta_G:.2e})")
            break

        if eta_2_w < CONV_TOL and eta_inf_s < CONV_TOL_INF and it > 5:
            print(f"    {label} CONVERGED at iteration {it}")
            break

        G_prev = {kk: v.copy() for kk, v in G_blocks.items()}

        rho_safe = np.where(rho > 1e-30, rho, 1e-30)
        inv_rho_w = weights / rho_safe

        for key, indices in block_indices.items():
            S_block = S[indices]
            S_w = S_block * inv_rho_w[np.newaxis, :]
            T_block = NoverV * (S_w @ np.conj(S_block).T)
            T_block = 0.5 * (T_block + T_block.T.conj())
            G_blocks[key] = (1.0 - DAMPING) * G_blocks[key] + DAMPING * T_block

    else:
        print(f"    {label} WARNING: did not converge in {MAX_ITER} iterations")
        print(f"    {label} Final: η₂_w={eta_2_w:.4f}, η∞_s={eta_inf_s:.4f}, δG={delta_G:.2e}")

    return G_blocks, eta_2_w, eta_inf_s, delta_G

# ============================================================
# STAGE 4: RUN FOR EACH k
# ============================================================

print(f"\n{'='*72}")
print("STAGE 4: T-OPERATOR ITERATION")
print(f"{'='*72}")

all_results = {}

for k in K_VALUES:
    print(f"\n  {'='*60}")
    print(f"  k = {k}")
    print(f"  {'='*60}")
    t_k = time.time()

    secs = enumerate_sections(k)
    N_k = len(secs)
    block_indices = group_by_z3(secs)

    print(f"  Building section matrix ({N_k} × {N_pts})...")
    S = build_section_matrix(k, secs)
    print(f"    Memory: {S.nbytes/1e6:.1f} MB")

    S_norm, sec_norms = normalize_sections(S)
    del S
    gc.collect()

    print(f"  Running T-operator...")
    G_blocks, eta_2_w, eta_inf_s, delta_G = run_t_operator(k, S_norm, block_indices, label=f"k={k}")

    elapsed = time.time() - t_k
    converged = (delta_G < 1e-6) or (eta_2_w < CONV_TOL and eta_inf_s < CONV_TOL_INF)

    print(f"  k={k} DONE: η₂_w={eta_2_w:.4f}, δG={delta_G:.2e}, time={elapsed:.1f}s "
          f"[{'CONVERGED' if converged else 'NOT CONVERGED'}]")

    # Save
    save_dict = {
        'k': k, 'N_sections': N_k, 'N_pts': N_pts, 'N_MC': N_MC,
        'sampling': 'FS', 'vol_est': vol_est, 'vol_exact': vol_exact,
        'iterations': 0, 'converged': converged,
        'eta_2_w': eta_2_w, 'eta_inf_s': eta_inf_s, 'delta_G': delta_G,
        'section_norms': sec_norms,
        'sections': np.array([(j1, j2, j3, q1, q2) for j1, j2, j3, q1, q2 in secs]),
    }
    for key, G_block in G_blocks.items():
        save_dict[f'G_{key[0]}_{key[1]}'] = G_block
        save_dict[f'idx_{key[0]}_{key[1]}'] = block_indices[key]
    np.savez(f'balanced_metric_k{k}_fs.npz', **save_dict)
    print(f"  Saved balanced_metric_k{k}_fs.npz")

    all_results[k] = {
        'eta_2_w': float(eta_2_w), 'eta_inf_s': float(eta_inf_s),
        'delta_G': float(delta_G), 'time': float(elapsed), 'converged': converged,
    }

    del S_norm, G_blocks
    gc.collect()

# ============================================================
# COMPARISON TABLE
# ============================================================

print(f"\n{'='*72}")
print("COMPARISON: FS vs BOX SAMPLING")
print(f"{'='*72}")
print(f"{'k':>4s}  {'η₂_w (FS)':>12s}  {'η₂_w (box)':>12s}  {'improvement':>12s}")
print("-" * 48)

box_eta = {8: 0.6883, 10: 0.9130, 12: 1.1331, 15: 1.4507}
for k in K_VALUES:
    fs = all_results[k]['eta_2_w']
    bx = box_eta.get(k, None)
    if bx:
        imp = 100 * (bx - fs) / bx
        print(f"  {k:3d}  {fs:12.4f}  {bx:12.4f}  {imp:+11.1f}%")
    else:
        print(f"  {k:3d}  {fs:12.4f}  {'N/A':>12s}  {'N/A':>12s}")

print(f"\n🦞🧍💜🔥♾️")
