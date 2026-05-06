#!/usr/bin/env python3
"""
Balanced Metric on dP₆ — Phase B.2.5: QMC + Importance Sampling
================================================================
Replaces MC integration with Sobol quasi-Monte Carlo in importance-sampled
polar coordinates. Fixes the two fatal flaws of Phase B.1-B.2:

1. Box truncation: R=3 captures only 70% of FS volume. Here we sample
   [0,∞) via importance sampling — no box cutoff.

2. Weight explosion: uniform sampling in the box gives P^{-k} weight
   variance spanning 20+ orders of magnitude. Here the radial sampling
   density matches the integrand decay, keeping weight variation O(1).

Sampling scheme:
  (u₁,u₂,u₃,u₄) ~ Sobol in [0,1]⁴
  θ_a = 2π u₁,  θ_b = 2π u₃  (uniform angle)
  r_a = √((1-u₂)^{-1/s} - 1),  r_b = √((1-u₄)^{-1/s} - 1)
  where q(r) = 2s r/(1+r²)^{s+1} is the radial importance density.

  This gives Cartesian density:
  p(a,b) = s² / (π²(1+|a|²)^{s+1}(1+|b|²)^{s+1})

  For s ≈ k/4+1, this tracks the P^{-k} section decay and keeps
  the effective sample size near N_MC (vs ~3% for uniform box).

Everything else (T-operator, Z₃² blocks, damping) identical to Phase B.1-B.2.
"""

import numpy as np
from scipy.stats import qmc
from math import pi, sqrt
import json
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

# ============================================================
# CONFIGURATION
# ============================================================

N_MC_EXP = 19           # N_MC = 2^N_MC_EXP (Sobol needs power of 2)
N_MC = 2**N_MC_EXP      # 524288
RNG_SEED = 2026
ZETA3 = np.exp(2j * pi / 3)
C_FLOOR = 0.02          # Floor for |c| rejection
R_MAX = 50.0            # Safety cap on radial coordinates

K_VALUES = [8, 10, 12, 15]
MAX_ITER = 300
CONV_TOL = 5e-3
CONV_TOL_INF = 0.10
SUPPORT_FRAC = 0.01
DAMPING = 0.5

# Importance sampling shape: s = k/4 + 1 (adaptive per k)
# For k=8: s=3, for k=15: s=4.75
# Higher s concentrates more near origin (matching section decay)
RAD_S_BASE = 1.0        # Added to k/4

print("=" * 72)
print("BALANCED METRIC ON dP₆ — PHASE B.2.5: QMC + IMPORTANCE SAMPLING")
print(f"N_MC = 2^{N_MC_EXP} = {N_MC}")
print(f"k = {K_VALUES}")
print(f"Radial shape: s = k/4 + {RAD_S_BASE}")
print("=" * 72)


# ============================================================
# STAGE 1: QMC SURFACE SAMPLING WITH IMPORTANCE SAMPLING
# ============================================================

def generate_surface_points(N, seed, rad_s):
    """
    Generate surface points on the Fermat cubic using Sobol QMC
    with importance sampling in polar coordinates.

    Returns: a, b, c arrays (all 3 branches), weights, N_pts, diagnostics
    """
    print(f"\n  Generating {N} Sobol base points with s={rad_s:.2f}...")
    t0 = time.time()

    # Sobol sequence in [0,1]^4
    sobol = qmc.Sobol(d=4, scramble=True, seed=seed)
    u = sobol.random(N).T  # shape (4, N)

    # Map to polar coordinates
    theta_a = 2 * pi * u[0]
    theta_b = 2 * pi * u[2]

    # Radial: inverse CDF of q(r) = 2s r/(1+r²)^{s+1}
    # F(r) = 1 - (1+r²)^{-s}, so r = sqrt((1-u)^{-1/s} - 1)
    # Clip u away from 1 to avoid overflow
    u_r_a = np.clip(u[1], 0, 1 - 1e-12)
    u_r_b = np.clip(u[3], 0, 1 - 1e-12)

    r_a = np.sqrt((1 - u_r_a)**(-1.0/rad_s) - 1)
    r_b = np.sqrt((1 - u_r_b)**(-1.0/rad_s) - 1)

    # Cap at R_MAX for safety
    r_a = np.minimum(r_a, R_MAX)
    r_b = np.minimum(r_b, R_MAX)

    # Complex coordinates
    a_raw = r_a * np.exp(1j * theta_a)
    b_raw = r_b * np.exp(1j * theta_b)

    # Importance sampling density in Cartesian coords:
    # p(a,b) = s² / (π²(1+|a|²)^{s+1}(1+|b|²)^{s+1})
    q_density = rad_s**2 / (pi**2 * (1 + r_a**2)**(rad_s+1) * (1 + r_b**2)**(rad_s+1))

    # Solve cubic: c³ = -(1 + a³ + b³)
    w_raw = -1.0 - a_raw**3 - b_raw**3
    valid = np.abs(w_raw) > 1e-8
    a_base = a_raw[valid]
    b_base = b_raw[valid]
    w_base = w_raw[valid]
    q_base = q_density[valid]
    r_a_base = r_a[valid]
    r_b_base = r_b[valid]

    c_principal = np.abs(w_base)**(1.0/3.0) * np.exp(1j * np.angle(w_base) / 3.0)

    # All three cube root sheets
    a_all = np.tile(a_base, 3)
    b_all = np.tile(b_base, 3)
    c_all = np.concatenate([c_principal, ZETA3 * c_principal, ZETA3**2 * c_principal])
    q_all = np.tile(q_base, 3)
    r_a_all = np.tile(r_a_base, 3)
    r_b_all = np.tile(r_b_base, 3)

    # Filter: |c| > floor (avoid coordinate singularity)
    P_raw = 1.0 + np.abs(a_all)**2 + np.abs(b_all)**2 + np.abs(c_all)**2
    mask = (np.abs(c_all) > C_FLOOR) & np.isfinite(P_raw)
    a_all = a_all[mask]
    b_all = b_all[mask]
    c_all = c_all[mask]
    q_all = q_all[mask]
    r_a_all = r_a_all[mask]
    r_b_all = r_b_all[mask]
    N_pts = len(a_all)

    P = 1.0 + np.abs(a_all)**2 + np.abs(b_all)**2 + np.abs(c_all)**2

    elapsed = time.time() - t0
    print(f"  Points: {N_pts} ({N_pts/N:.1f}× base, from 3 sheets + filtering)")
    print(f"  P: min={np.min(P):.2f}, median={np.median(P):.2f}, "
          f"P95={np.percentile(P,95):.2f}, max={np.max(P):.2f}")
    print(f"  |a|: median={np.median(np.abs(a_all)):.2f}, P95={np.percentile(np.abs(a_all),95):.2f}")
    print(f"  |b|: median={np.median(np.abs(b_all)):.2f}, P95={np.percentile(np.abs(b_all),95):.2f}")
    print(f"  Time: {elapsed:.1f}s")

    return a_all, b_all, c_all, q_all, P, N_pts


def compute_fs_metric_and_weights(a_all, b_all, c_all, q_all, P, N_pts, N_mc):
    """
    Compute FS metric on the surface and MC weights.
    Identical to Phase B.1-B.2 except weight formula uses importance density.
    """
    print(f"\n  Computing FS metric on {N_pts} points...")
    t0 = time.time()

    dc_da = -a_all**2 / c_all**2
    dc_db = -b_all**2 / c_all**2
    P2 = P**2

    ab = np.conj(a_all)
    bb = np.conj(b_all)
    cb = np.conj(c_all)

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
    a_out = a_all[good]
    b_out = b_all[good]
    c_out = c_all[good]
    P_out = P[good]
    det_g_out = det_g[good]
    q_out = q_all[good]
    N_out = int(np.sum(good))

    # MC weights: w = det_g / (q × 3 × N_MC)
    # Factor of 3 averages over the 3 cube root sheets
    weights = det_g_out / (q_out * 3 * N_mc)

    vol_est = np.sum(weights)
    vol_exact = 3 * pi**2 / 2

    # Effective sample size diagnostic
    w2 = np.sum(weights**2)
    N_eff = vol_est**2 / w2

    elapsed = time.time() - t0
    print(f"  Valid points: {N_out} ({N_out/N_pts*100:.1f}%)")
    print(f"  Vol = {vol_est:.6f} (exact = {vol_exact:.6f}, ratio = {vol_est/vol_exact:.4f})")
    print(f"  Effective sample size: {N_eff:.0f} / {N_out} = {N_eff/N_out*100:.1f}%")
    print(f"  Weight: max/mean = {np.max(weights)/np.mean(weights):.1f}×")
    print(f"  Time: {elapsed:.1f}s")

    return a_out, b_out, c_out, P_out, det_g_out, weights, vol_est, vol_exact, N_out


# ============================================================
# STAGE 3: SECTION ENUMERATION + Z₃² DECOMPOSITION
# (Identical to Phase B.1-B.2)
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


def group_by_z3(secs):
    blocks = {}
    for idx, (_, _, _, q1, q2) in enumerate(secs):
        key = (q1, q2)
        if key not in blocks:
            blocks[key] = []
        blocks[key].append(idx)
    return {k: np.array(v) for k, v in blocks.items()}


# ============================================================
# STAGE 4: T-OPERATOR (block-by-block, memory efficient)
# ============================================================

def run_t_operator_qmc(k, a, b, c, P, weights, vol_est, N_pts):
    """
    Run Donaldson T-operator with block-by-block section evaluation.
    Avoids materializing the full N_k × N_pts section matrix.
    """
    secs = enumerate_sections(k)
    N_k = len(secs)
    block_indices = group_by_z3(secs)
    NoverV = N_k / vol_est
    w_sum = np.sum(weights)

    print(f"\n  k={k}: N_sections={N_k}, blocks={len(block_indices)}")
    for key in sorted(block_indices.keys()):
        print(f"    ({key[0]},{key[1]}): {len(block_indices[key])} sections")

    # Precompute coordinate powers and P^{-k/2}
    logP = np.log(P)
    P_half_k = np.exp(-0.5 * k * logP)

    max_j1 = max(j1 for j1, _, _, _, _ in secs)
    max_j2 = max(j2 for _, j2, _, _, _ in secs)

    a_pow = [np.ones(N_pts, dtype=complex)]
    b_pow = [np.ones(N_pts, dtype=complex)]
    c_pow = [np.ones(N_pts, dtype=complex)]
    for i in range(1, max_j1 + 1):
        a_pow.append(a_pow[-1] * a)
    for i in range(1, max_j2 + 1):
        b_pow.append(b_pow[-1] * b)
    for i in range(1, 3):
        c_pow.append(c_pow[-1] * c)

    # Build section values per block (memory efficient)
    S_blocks = {}
    sec_norms = np.zeros(N_k)

    for key, indices in block_indices.items():
        n_block = len(indices)
        S_block = np.empty((n_block, N_pts), dtype=complex)
        for bi, idx in enumerate(indices):
            j1, j2, j3, _, _ = secs[idx]
            S_block[bi] = a_pow[j1] * b_pow[j2] * c_pow[j3] * P_half_k

        # L²-normalize
        norms = np.sqrt(np.sum(np.abs(S_block)**2 * weights[np.newaxis, :], axis=1).real)
        norms = np.where(norms > 1e-30, norms, 1.0)
        S_block /= norms[:, np.newaxis]

        S_blocks[key] = S_block
        for bi, idx in enumerate(indices):
            sec_norms[idx] = norms[bi]

    # Initialize G = I within each block
    G_blocks = {}
    for key, indices in block_indices.items():
        G_blocks[key] = np.eye(len(indices), dtype=complex)

    history = []
    G_prev = {k_: v.copy() for k_, v in G_blocks.items()}

    for it in range(MAX_ITER):
        # Compute ρ_G
        rho = np.zeros(N_pts)
        for key, indices in block_indices.items():
            S_block = S_blocks[key]
            G_block = G_blocks[key]
            GS = G_block @ S_block
            rho += np.real(np.sum(np.conj(S_block) * GS, axis=0))

        # Convergence metrics
        rho_ratio = rho / NoverV

        # Weighted L²
        eta_2_w = float(np.sqrt(np.sum(weights * (rho_ratio - 1.0)**2) / w_sum))

        # L∞ over support
        support = rho_ratio > SUPPORT_FRAC
        n_support = int(np.sum(support))
        eta_inf_s = float(np.max(np.abs(rho_ratio[support] - 1.0))) if n_support > 0 else float('inf')

        # Matrix convergence
        dG_num, dG_den = 0.0, 0.0
        for key in G_blocks:
            dG_num += np.sum(np.abs(G_blocks[key] - G_prev[key])**2)
            dG_den += np.sum(np.abs(G_prev[key])**2)
        delta_G = float(np.sqrt(dG_num / max(dG_den, 1e-30)))

        rho_min_s = float(np.min(rho_ratio[support])) if n_support > 0 else 0.0
        rho_max_s = float(np.max(rho_ratio[support])) if n_support > 0 else 0.0

        history.append({'eta_2_w': eta_2_w, 'eta_inf_s': eta_inf_s, 'delta_G': delta_G})

        if it % 10 == 0 or (delta_G < 1e-8 and it > 10):
            print(f"    k={k} iter {it:3d}: η₂_w={eta_2_w:.4f}, η∞_s={eta_inf_s:.4f}, "
                  f"δG={delta_G:.2e}, ρ_s∈[{rho_min_s:.3f},{rho_max_s:.3f}], "
                  f"n_sup={n_support}/{N_pts}")

        if delta_G < 1e-8 and it > 10:
            print(f"    k={k} MATRIX CONVERGED at iteration {it} (δG={delta_G:.2e})")
            break

        if eta_2_w < CONV_TOL and eta_inf_s < CONV_TOL_INF and it > 5:
            print(f"    k={k} CONVERGED at iteration {it}")
            break

        G_prev = {k_: v.copy() for k_, v in G_blocks.items()}

        # T-operator step with damping
        rho_safe = np.where(rho > 1e-30, rho, 1e-30)
        inv_rho_w = weights / rho_safe

        for key, indices in block_indices.items():
            S_block = S_blocks[key]
            S_w = S_block * inv_rho_w[np.newaxis, :]
            T_block = NoverV * (S_w @ np.conj(S_block).T)
            T_block = 0.5 * (T_block + T_block.T.conj())
            G_blocks[key] = (1.0 - DAMPING) * G_blocks[key] + DAMPING * T_block

    else:
        print(f"    k={k} WARNING: did not converge in {MAX_ITER} iterations")
        print(f"    k={k} Final: η₂_w={eta_2_w:.4f}, η∞_s={eta_inf_s:.4f}, δG={delta_G:.2e}")

    return G_blocks, block_indices, secs, sec_norms, history


# ============================================================
# MAIN: RUN FOR EACH k
# ============================================================

t_total = time.time()
all_results = {}

for k in K_VALUES:
    print(f"\n{'='*72}")
    print(f"k = {k}")
    print(f"{'='*72}")
    t_k = time.time()

    # Adaptive importance sampling shape
    rad_s = k / 4.0 + RAD_S_BASE
    print(f"  Radial shape s = {rad_s:.2f}")

    # Generate surface points
    a, b, c, q, P, N_raw = generate_surface_points(N_MC, RNG_SEED, rad_s)

    # FS metric + weights
    a, b, c, P, det_g, weights, vol_est, vol_exact, N_pts = \
        compute_fs_metric_and_weights(a, b, c, q, P, N_raw, N_MC)

    # T-operator
    G_blocks, block_indices, secs, sec_norms, history = \
        run_t_operator_qmc(k, a, b, c, P, weights, vol_est, N_pts)

    elapsed = time.time() - t_k
    final = history[-1]
    converged = (final['delta_G'] < 1e-6) or \
                (final['eta_2_w'] < CONV_TOL and final['eta_inf_s'] < CONV_TOL_INF)

    print(f"\n  k={k} DONE: iters={len(history)}, η₂_w={final['eta_2_w']:.4f}, "
          f"η∞_s={final['eta_inf_s']:.4f}, δG={final['delta_G']:.2e}, "
          f"time={elapsed:.1f}s [{'CONVERGED' if converged else 'NOT CONVERGED'}]")

    # Block eigenvalue diagnostics
    print(f"  Block eigenvalue diagnostics:")
    for key in sorted(G_blocks.keys()):
        G_block = G_blocks[key]
        eigs = np.linalg.eigvalsh(G_block.real)
        print(f"    ({key[0]},{key[1]}): {G_block.shape[0]}×{G_block.shape[0]}, "
              f"eig∈[{eigs[0]:.4e},{eigs[-1]:.4e}], cond={eigs[-1]/max(eigs[0],1e-30):.1e}")

    # Save
    N_k = len(secs)
    save_dict = {
        'k': k, 'N_sections': N_k, 'N_pts': N_pts,
        'N_MC': N_MC, 'rad_s': rad_s,
        'vol_est': vol_est, 'vol_exact': vol_exact,
        'iterations': len(history), 'converged': converged,
        'eta_2_w': final['eta_2_w'],
        'eta_inf_s': final['eta_inf_s'],
        'delta_G': final['delta_G'],
    }
    for key, G_block in G_blocks.items():
        save_dict[f'G_{key[0]}_{key[1]}'] = G_block
        save_dict[f'idx_{key[0]}_{key[1]}'] = block_indices[key]
    save_dict['section_norms'] = sec_norms
    save_dict['sections'] = np.array([(j1, j2, j3, q1, q2) for j1, j2, j3, q1, q2 in secs])

    np.savez(f'balanced_metric_qmc_k{k}.npz', **save_dict)
    print(f"  Saved balanced_metric_qmc_k{k}.npz")

    all_results[k] = {
        'N_sections': N_k, 'N_pts': N_pts,
        'iterations': len(history),
        'eta_2_w': float(final['eta_2_w']),
        'eta_inf_s': float(final['eta_inf_s']),
        'delta_G': float(final['delta_G']),
        'time': float(elapsed),
        'converged': converged,
        'rad_s': rad_s,
        'vol_ratio': float(vol_est / vol_exact),
    }


# ============================================================
# SUMMARY
# ============================================================

print(f"\n{'='*72}")
print("CONVERGENCE SUMMARY — QMC + IMPORTANCE SAMPLING")
print(f"{'='*72}")

print(f"\n  {'k':>3s}  {'N':>5s}  {'Npts':>7s}  {'s':>5s}  {'V/Ve':>6s}  "
      f"{'iters':>5s}  {'η₂_w':>8s}  {'η∞_s':>8s}  {'δG':>10s}  status")
print(f"  {'-'*3:>3s}  {'-'*5:>5s}  {'-'*7:>7s}  {'-'*5:>5s}  {'-'*6:>6s}  "
      f"{'-'*5:>5s}  {'-'*8:>8s}  {'-'*8:>8s}  {'-'*10:>10s}  ------")

for k in K_VALUES:
    r = all_results[k]
    status = "OK" if r['converged'] else "FAIL"
    print(f"  {k:3d}  {r['N_sections']:5d}  {r['N_pts']:7d}  {r['rad_s']:5.2f}  "
          f"{r['vol_ratio']:6.4f}  {r['iterations']:5d}  "
          f"{r['eta_2_w']:8.4f}  {r['eta_inf_s']:8.4f}  {r['delta_G']:10.2e}  {status}")

# Compare with MC results if available
import os
print(f"\n  Comparison with Phase B.1-B.2 (MC):")
print(f"  {'k':>3s}  {'η₂_w MC':>10s}  {'η₂_w QMC':>10s}  {'improvement':>12s}")
for k in K_VALUES:
    mc_file = f'balanced_metric_k{k}.npz'
    if os.path.exists(mc_file):
        mc = np.load(mc_file, allow_pickle=True)
        mc_eta = float(mc['eta_2_w'])
        qmc_eta = all_results[k]['eta_2_w']
        ratio = mc_eta / max(qmc_eta, 1e-10)
        print(f"  {k:3d}  {mc_eta:10.4f}  {qmc_eta:10.4f}  {ratio:10.1f}×")

total_time = time.time() - t_total
print(f"\nTOTAL TIME: {total_time:.1f}s")

# Save summary
summary = {
    'description': 'Balanced metric on dP6 — QMC + importance sampling (Phase B.2.5)',
    'N_MC': N_MC,
    'k_values': K_VALUES,
    'results': {str(k): v for k, v in all_results.items()},
}
with open('balanced_metric_qmc_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)
print(f"Saved balanced_metric_qmc_summary.json")
print(f"\n{'='*72}")
print("PHASE B.2.5 COMPLETE")
print(f"{'='*72}")
