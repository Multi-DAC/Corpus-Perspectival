#!/usr/bin/env python3
"""
Balanced Metric on dP₆ via Donaldson T-operator — Phase B.1-B.2
================================================================
Phase 26 — Precision analytic torsion computation.

The Fermat cubic S = {x₀³+x₁³+x₂³+x₃³=0} ⊂ CP³ is dP₆.
Its Kähler-Einstein metric is approximated by the balanced metric at level k.

Algorithm (Donaldson 2001, Douglas-Karp-Lukic-Reinbacher 2006):
  Given a basis {s_α} of H⁰(S, O_S(k)), N_k = (3k²+3k+2)/2:
  1. Start: G = I_{N_k} (or L²-normalized diagonal)
  2. Iterate: T(G)_αβ = (N_k/V) ∫_S ŝ̄_α ŝ_β / ρ_G · dA_FS
     where ŝ_α = s_α/P^{k/2} (FS-normalized section)
     ρ_G = Σ G_αβ ŝ̄_α ŝ_β (Bergman function)
  3. Converge when ρ_G → N_k/V (constant = balanced condition)

The converged G_k defines the balanced metric:
  ω_bal = ω_FS + (1/k)(i/2π) ∂∂̄ log ρ_G
As k → ∞, ω_bal → ω_KE (Tian's theorem for dP degree ≤ 6).

Z₃² symmetry (B.2): Fermat cubic has (Z/3)² phase symmetry
  (a,b,c) → (ωa, ω²b, c) and (a,b,c) → (a, ωb, ω²c), ω=e^{2πi/3}.
  Section charges: q₁ = (j₁+2j₂) mod 3, q₂ = (j₂+2j₃) mod 3.
  T-operator preserves charge blocks → iterate within each block separately.
  Reduces 9 blocks of ~N_k/9 vs one block of N_k (faster + eliminates noise).

Output: converged G matrices for k = 8, 10, 12, 15.
These are input to Phase B.3 (Laplacian eigenvalues with balanced metric).
"""

import numpy as np
from math import pi, sqrt, log
import json
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

# ============================================================
# CONFIGURATION
# ============================================================

N_MC = 300000           # Monte Carlo samples
SAMPLING = 'box'        # 'box' = uniform box (reliable), 'FS' = Fubini-Study (experimental)
DOMAIN_R = 3.0          # Box radius — R=3 captures ~85% FS volume, good section coverage
P_MAX = 200.0           # Rejection cutoff for FS sampling
RNG_SEED = 2026
ZETA3 = np.exp(2j * pi / 3)
C_FLOOR = 0.02          # Floor for |c| rejection

K_VALUES = [8, 10, 12, 15]  # Balanced metric levels
MAX_ITER = 300          # Maximum T-operator iterations per level
CONV_TOL = 5e-3         # WEIGHTED L² convergence tolerance for σ/target - 1
CONV_TOL_INF = 0.10     # L∞ convergence (over support only)
SUPPORT_FRAC = 0.01     # Points with ρ < SUPPORT_FRAC * target are "outside support"
DAMPING = 0.5           # Damping parameter: G_{n+1} = (1-α)G_n + α T(G_n)
                        # Prevents period-2 oscillations from eigenvalue -1 of DT

rng = np.random.default_rng(RNG_SEED)

print("=" * 72)
print("BALANCED METRIC ON dP₆ — DONALDSON T-OPERATOR")
print(f"Phase B.1-B.2: T-operator + Z₃² decomposition")
print(f"N_MC={N_MC}, sampling={SAMPLING}")
print(f"k = {K_VALUES}")
print("=" * 72)


# ============================================================
# STAGE 1: SURFACE SAMPLING
# ============================================================

print(f"\n{'='*72}")
print("STAGE 1: SURFACE SAMPLING")
print(f"  Fermat cubic {{x₀³+x₁³+x₂³+x₃³=0}} in CP³")
print(f"  Sampling: {SAMPLING}")
if SAMPLING == 'FS':
    print(f"  (a,b) = (z₁/z₀, z₂/z₀), z_i ~ CN(0,1)")
    print(f"  Density: q(a,b) = 2/(π²(1+|a|²+|b|²)³) — concentrates near origin")
else:
    print(f"  Uniform box: [-{DOMAIN_R}, {DOMAIN_R}]⁴")
print(f"{'='*72}")

t0 = time.time()

if SAMPLING == 'FS':
    # Homogeneous coordinate sampling (Headrick method)
    # z₀, z₁, z₂ ~ CN(0,1), then a = z₁/z₀, b = z₂/z₀
    # This gives FS-uniform distribution on CP², density:
    # q(a,b) = 2 / (π² (1 + |a|² + |b|²)³)
    z_re = rng.standard_normal((3, N_MC))
    z_im = rng.standard_normal((3, N_MC))
    z0 = (z_re[0] + 1j * z_im[0]) / sqrt(2)
    z1 = (z_re[1] + 1j * z_im[1]) / sqrt(2)
    z2 = (z_re[2] + 1j * z_im[2]) / sqrt(2)

    # Reject |z₀| too small (coordinate singularity)
    ok = np.abs(z0) > 1e-6
    a_raw = z1[ok] / z0[ok]
    b_raw = z2[ok] / z0[ok]

    # Proposal density q(a,b) for importance weights
    Q_ab = 1.0 + np.abs(a_raw)**2 + np.abs(b_raw)**2  # = (1+|a|²+|b|²)
    q_density = 2.0 / (pi**2 * Q_ab**3)

else:
    # Uniform box sampling (original method)
    u = rng.uniform(-DOMAIN_R, DOMAIN_R, (4, N_MC))
    a_raw = u[0] + 1j * u[1]
    b_raw = u[2] + 1j * u[3]
    q_density = np.ones(len(a_raw)) / (2 * DOMAIN_R)**4

# Solve cubic constraint: c³ = -(1 + a³ + b³)
w_raw = -1.0 - a_raw**3 - b_raw**3
valid = np.abs(w_raw) > 1e-8
a_base = a_raw[valid]
b_base = b_raw[valid]
w_base = w_raw[valid]
q_base = q_density[valid] if SAMPLING == 'FS' else q_density[valid]

c_principal = np.abs(w_base)**(1.0/3.0) * np.exp(1j * np.angle(w_base) / 3.0)

# All three cube root sheets
a_all = np.tile(a_base, 3)
b_all = np.tile(b_base, 3)
c_all = np.concatenate([c_principal, ZETA3 * c_principal, ZETA3**2 * c_principal])
q_all = np.tile(q_base, 3)

# Reject points with |c| too small or P too large
P_raw = 1.0 + np.abs(a_all)**2 + np.abs(b_all)**2 + np.abs(c_all)**2
mask = (np.abs(c_all) > C_FLOOR) & (P_raw < P_MAX)
a_all, b_all, c_all = a_all[mask], b_all[mask], c_all[mask]
q_all = q_all[mask]
N_pts = len(a_all)

P = 1.0 + np.abs(a_all)**2 + np.abs(b_all)**2 + np.abs(c_all)**2

print(f"  Points: {N_pts}")
print(f"  P: min={np.min(P):.2f}, median={np.median(P):.2f}, max={np.max(P):.2f}")
print(f"  Time: {time.time()-t0:.1f}s")


# ============================================================
# STAGE 2: FS METRIC AND MC WEIGHTS
# ============================================================

print(f"\n{'='*72}")
print("STAGE 2: FUBINI-STUDY METRIC ON THE SURFACE")
print(f"{'='*72}")

t1 = time.time()

ab = np.conj(a_all)
bb = np.conj(b_all)
cb = np.conj(c_all)

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
for nm in ['a_all', 'b_all', 'c_all', 'ab', 'bb', 'cb', 'P',
           'det_g', 'g11', 'g12', 'g21', 'g22',
           'dc_da', 'dc_db', 'q_all']:
    exec(f"{nm} = {nm}[good]")
N_pts = len(a_all)
P2 = P**2

# MC weights: w = det_g / q(a,b) / (3 * N_MC)
# For FS sampling: q = 2/(π²(1+|a|²+|b|²)³), so w = det_g * π²(1+|a|²+|b|²)³ / (6*N_MC)
# For box sampling: q = 1/(2R)⁴, so w = det_g * (2R)⁴ / (3*N_MC)
# The factor of 3 accounts for averaging over the 3 cube root sheets.
weights = det_g / (q_all[good] * 3 * N_MC)
vol_est = np.sum(weights)
vol_exact = 3 * pi**2 / 2

print(f"  Valid points: {N_pts}")
print(f"  Vol = {vol_est:.6f} (exact = {vol_exact:.6f}, ratio = {vol_est/vol_exact:.4f})")
print(f"  Time: {time.time()-t1:.1f}s")


# ============================================================
# STAGE 3: SECTION ENUMERATION + Z₃² DECOMPOSITION
# ============================================================

print(f"\n{'='*72}")
print("STAGE 3: SECTION ENUMERATION WITH Z₃² DECOMPOSITION")
print(f"  O_S(k): a^j₁ b^j₂ c^j₃ with j₁+j₂+j₃ ≤ k, j₃ ≤ 2")
print(f"  (c³ = -1-a³-b³ eliminates higher c powers on the surface)")
print(f"  N_k = (3k²+3k+2)/2")
print(f"{'='*72}")


def enumerate_sections(k):
    """
    Enumerate sections of O_S(k) on the Fermat cubic surface.

    In affine coords (x₀=1): s = a^{j₁} b^{j₂} c^{j₃}
    with j₁+j₂+j₃ ≤ k, j₃ ∈ {0,1,2}.
    (Comes from homogeneous sections x₀^{k-j₁-j₂-j₃} x₁^{j₁} x₂^{j₂} x₃^{j₃}
     restricted to S, with x₃^m for m≥3 reduced via x₃³=-(x₀³+x₁³+x₂³).)

    Returns list of (j₁, j₂, j₃, q₁, q₂) with Z₃² charges.
    """
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
    N_expected = N_k_formula(k)
    assert len(secs) == N_expected, f"k={k}: {len(secs)} != {N_expected}"

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
# STAGE 4: T-OPERATOR ITERATION
# ============================================================

print(f"\n{'='*72}")
print("STAGE 4: DONALDSON T-OPERATOR ITERATION")
print(f"  T(G)_αβ = (N/V) Σ_p ŝ̄_α(p) ŝ_β(p) / ρ_G(p) · w_p")
print(f"  ŝ_α = s_α / P^{{k/2}} (FS-normalized)")
print(f"  ρ_G = Σ G_αβ ŝ̄_α ŝ_β → N/V (balanced condition)")
print(f"{'='*72}")


def build_section_matrix(k, secs):
    """
    Build the N_k × N_pts matrix of FS-normalized section values.
    ŝ_α(p) = a^{j₁} b^{j₂} c^{j₃} / P^{k/2}

    Uses log(P) for numerical stability at large k.
    """
    N_k = len(secs)
    P_half_k = np.exp(-0.5 * k * logP)  # P^{-k/2}

    S = np.empty((N_k, N_pts), dtype=complex)
    for idx, (j1, j2, j3, _, _) in enumerate(secs):
        S[idx] = a_pow[j1] * b_pow[j2] * c_pow[j3] * P_half_k
    return S


def group_by_z3(secs):
    """Group section indices by Z₃² charge (q₁, q₂)."""
    blocks = {}
    for idx, (_, _, _, q1, q2) in enumerate(secs):
        key = (q1, q2)
        if key not in blocks:
            blocks[key] = []
        blocks[key].append(idx)
    return {k: np.array(v) for k, v in blocks.items()}


def normalize_sections(S, block_indices):
    """
    L²-normalize each section for numerical stability.
    Returns normalized S and the norms (for reconstructing G later).
    """
    norms = np.sqrt(np.sum(np.abs(S)**2 * weights[np.newaxis, :], axis=1).real)
    norms = np.where(norms > 1e-30, norms, 1.0)
    S_norm = S / norms[:, np.newaxis]
    return S_norm, norms


def run_t_operator(k, S, block_indices, label=""):
    """
    Run the Donaldson T-operator iteration for level k.

    Convergence is measured three ways:
    1. η₂_w: weighted RMS of (ρ/target - 1) — the T-operator integral metric
    2. η∞_s: L∞ over support (points where ρ > SUPPORT_FRAC * target)
    3. δG: relative Frobenius change in G between iterations

    Returns: G_blocks dict, convergence history.
    """
    N_k = S.shape[0]
    NoverV = N_k / vol_est
    w_sum = np.sum(weights)

    # Initialize G = I within each block
    G_blocks = {}
    for key, indices in block_indices.items():
        n_block = len(indices)
        G_blocks[key] = np.eye(n_block, dtype=complex)

    history = []
    G_prev = {k: v.copy() for k, v in G_blocks.items()}

    for it in range(MAX_ITER):
        # Compute ρ_G = Σ_blocks Σ_{α,β ∈ block} G_αβ ŝ̄_α ŝ_β
        rho = np.zeros(N_pts)
        for key, indices in block_indices.items():
            S_block = S[indices]
            G_block = G_blocks[key]
            GS = G_block @ S_block
            rho += np.real(np.sum(np.conj(S_block) * GS, axis=0))

        # Convergence metrics
        rho_ratio = rho / NoverV

        # 1. Weighted L² (the natural T-operator metric)
        eta_2_w = float(np.sqrt(np.sum(weights * (rho_ratio - 1.0)**2) / w_sum))

        # 2. L∞ over support (where ρ is non-negligible)
        support = rho_ratio > SUPPORT_FRAC
        n_support = int(np.sum(support))
        if n_support > 0:
            eta_inf_s = float(np.max(np.abs(rho_ratio[support] - 1.0)))
        else:
            eta_inf_s = float('inf')

        # 3. Matrix convergence: ||G_new - G_old|| / ||G_old||
        dG_num, dG_den = 0.0, 0.0
        for key in G_blocks:
            dG_num += np.sum(np.abs(G_blocks[key] - G_prev[key])**2)
            dG_den += np.sum(np.abs(G_prev[key])**2)
        delta_G = float(np.sqrt(dG_num / max(dG_den, 1e-30)))

        rho_min_s = float(np.min(rho_ratio[support])) if n_support > 0 else 0.0
        rho_max_s = float(np.max(rho_ratio[support])) if n_support > 0 else 0.0

        history.append({'eta_2_w': eta_2_w, 'eta_inf_s': eta_inf_s, 'delta_G': delta_G})

        if it % 20 == 0 or (eta_2_w < CONV_TOL and it > 0):
            print(f"    {label} iter {it:3d}: η₂_w={eta_2_w:.2e}, η∞_s={eta_inf_s:.2e}, "
                  f"δG={delta_G:.2e}, ρ_s∈[{rho_min_s:.3f},{rho_max_s:.3f}], "
                  f"n_sup={n_support}")

        if delta_G < 1e-8 and it > 10:
            print(f"    {label} MATRIX CONVERGED at iteration {it} (δG={delta_G:.2e})")
            break

        if eta_2_w < CONV_TOL and eta_inf_s < CONV_TOL_INF and it > 5:
            print(f"    {label} CONVERGED at iteration {it}")
            break

        # Save current G for convergence tracking
        G_prev = {k: v.copy() for k, v in G_blocks.items()}

        # T-operator with damping: G_{n+1} = (1-α)G_n + α T(G_n)
        # Damping prevents period-2 oscillations (DT eigenvalue ≈ -1)
        rho_safe = np.where(rho > 1e-30, rho, 1e-30)
        inv_rho_w = weights / rho_safe

        for key, indices in block_indices.items():
            S_block = S[indices]
            S_w = S_block * inv_rho_w[np.newaxis, :]
            T_block = NoverV * (S_w @ np.conj(S_block).T)
            T_block = 0.5 * (T_block + T_block.T.conj())  # Hermitianize
            # Damped update
            G_blocks[key] = (1.0 - DAMPING) * G_blocks[key] + DAMPING * T_block

    else:
        print(f"    {label} WARNING: did not converge in {MAX_ITER} iterations")
        print(f"    {label} Final: η₂_w={eta_2_w:.2e}, η∞_s={eta_inf_s:.2e}, δG={delta_G:.2e}")

    return G_blocks, history


# ============================================================
# RUN FOR EACH k
# ============================================================

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

    # L²-normalize for numerical stability
    S_norm, sec_norms = normalize_sections(S, block_indices)

    # Diagnostic: section magnitude stats
    s_abs = np.abs(S_norm)
    print(f"    |ŝ| (normalized): mean={np.mean(s_abs):.2e}, "
          f"max={np.max(s_abs):.2e}, min nonzero={np.min(s_abs[s_abs>0]):.2e}")

    # Initial Bergman function diagnostic (G=I after normalization)
    rho_init = np.sum(np.abs(S_norm)**2, axis=0)
    NoverV = N_k / vol_est
    print(f"    Initial ρ/target: mean={np.mean(rho_init)/NoverV:.4f}, "
          f"std={np.std(rho_init)/NoverV:.4f}")

    # Run T-operator
    print(f"  Running T-operator...")
    G_blocks, history = run_t_operator(k, S_norm, block_indices, label=f"k={k}")

    elapsed = time.time() - t_k
    final_eta2w = history[-1]['eta_2_w']
    final_etainfs = history[-1]['eta_inf_s']
    final_dG = history[-1]['delta_G']
    converged = (final_dG < 1e-6) or (final_eta2w < CONV_TOL and final_etainfs < CONV_TOL_INF)

    print(f"  k={k} DONE: iters={len(history)}, η₂_w={final_eta2w:.2e}, "
          f"η∞_s={final_etainfs:.2e}, δG={final_dG:.2e}, time={elapsed:.1f}s "
          f"[{'CONVERGED' if converged else 'NOT CONVERGED'}]")

    # Block diagnostics: eigenvalues of each G block
    print(f"  Block eigenvalue diagnostics:")
    for key in sorted(G_blocks.keys()):
        G_block = G_blocks[key]
        eigs = np.linalg.eigvalsh(G_block.real)
        print(f"    ({key[0]},{key[1]}): {G_block.shape[0]}×{G_block.shape[0]}, "
              f"eig ∈ [{eigs[0]:.4e}, {eigs[-1]:.4e}], cond={eigs[-1]/max(eigs[0],1e-30):.1e}")

    # Save converged G blocks + metadata
    save_dict = {
        'k': k,
        'N_sections': N_k,
        'N_pts': N_pts,
        'N_MC': N_MC,
        'DOMAIN_R': DOMAIN_R,
        'vol_est': vol_est,
        'vol_exact': vol_exact,
        'iterations': len(history),
        'converged': converged,
        'eta_2_w': final_eta2w,
        'eta_inf_s': final_etainfs,
        'delta_G': final_dG,
    }
    for key, G_block in G_blocks.items():
        save_dict[f'G_{key[0]}_{key[1]}'] = G_block
        save_dict[f'idx_{key[0]}_{key[1]}'] = block_indices[key]
    save_dict['section_norms'] = sec_norms
    save_dict['sections'] = np.array([(j1, j2, j3, q1, q2)
                                       for j1, j2, j3, q1, q2 in secs])
    np.savez(f'balanced_metric_k{k}.npz', **save_dict)
    print(f"  Saved balanced_metric_k{k}.npz")

    all_results[k] = {
        'N_sections': N_k,
        'iterations': len(history),
        'eta_2_w': float(final_eta2w),
        'eta_inf_s': float(final_etainfs),
        'delta_G': float(final_dG),
        'time': float(elapsed),
        'converged': converged,
        'history_eta2w': [h['eta_2_w'] for h in history[::10]],  # every 10th
        'history_dG': [h['delta_G'] for h in history[::10]],
    }


# ============================================================
# STAGE 5: CONVERGENCE SUMMARY
# ============================================================

print(f"\n{'='*72}")
print("STAGE 5: CONVERGENCE SUMMARY")
print(f"{'='*72}")

print(f"\n  {'k':>3s}  {'N':>5s}  {'iters':>5s}  {'η₂_w':>10s}  {'η∞_s':>10s}  {'δG':>10s}  {'time':>8s}  status")
print(f"  {'---':>3s}  {'---':>5s}  {'---':>5s}  {'---':>10s}  {'---':>10s}  {'---':>10s}  {'---':>8s}  ------")
for k in K_VALUES:
    r = all_results[k]
    status = "OK" if r['converged'] else "FAIL"
    print(f"  {k:3d}  {r['N_sections']:5d}  {r['iterations']:5d}  "
          f"{r['eta_2_w']:10.2e}  {r['eta_inf_s']:10.2e}  {r['delta_G']:10.2e}  "
          f"{r['time']:7.1f}s  {status}")

# Convergence rate analysis
print(f"\n  Convergence rate (δG decay):")
for k in K_VALUES:
    h = all_results[k]['history_dG']
    if len(h) >= 3:
        rates = [h[i+1]/h[i] for i in range(len(h)-1) if h[i] > 1e-15]
        if rates:
            avg_rate = np.mean(rates)
            print(f"    k={k}: avg δG decay factor per 10 iters = {avg_rate:.3f}")


# ============================================================
# STAGE 6: SIGMA PROFILE DIAGNOSTICS
# ============================================================

print(f"\n{'='*72}")
print("STAGE 6: FINAL BERGMAN FUNCTION PROFILE")
print(f"  (ρ/target should be 1.0 everywhere for perfect balanced metric)")
print(f"{'='*72}")

# Recompute σ for the last k value for detailed diagnostics
k_last = K_VALUES[-1]
secs_last = enumerate_sections(k_last)
S_last = build_section_matrix(k_last, secs_last)
_, norms_last = normalize_sections(S_last, group_by_z3(secs_last))
S_last_norm = S_last / norms_last[:, np.newaxis]

block_idx_last = group_by_z3(secs_last)
data_last = np.load(f'balanced_metric_k{k_last}.npz', allow_pickle=True)

rho_final = np.zeros(N_pts)
for key, indices in block_idx_last.items():
    G_block = data_last[f'G_{key[0]}_{key[1]}']
    S_block = S_last_norm[indices]
    GS = G_block @ S_block
    rho_final += np.real(np.sum(np.conj(S_block) * GS, axis=0))

NoverV_last = len(secs_last) / vol_est
rho_ratio = rho_final / NoverV_last

pctiles = np.percentile(rho_ratio, [1, 5, 25, 50, 75, 95, 99])
print(f"  k={k_last}: ρ/target percentiles:")
print(f"    1%={pctiles[0]:.5f}, 5%={pctiles[1]:.5f}, 25%={pctiles[2]:.5f}")
print(f"    50%={pctiles[3]:.5f} (median)")
print(f"    75%={pctiles[4]:.5f}, 95%={pctiles[5]:.5f}, 99%={pctiles[6]:.5f}")
print(f"    std={np.std(rho_ratio):.5f}")


# ============================================================
# SAVE SUMMARY
# ============================================================

print(f"\n{'='*72}")
print("SAVING SUMMARY")
print(f"{'='*72}")

summary = {
    'description': 'Balanced metric on dP6 via Donaldson T-operator',
    'algorithm': 'T(G) = (N/V) S diag(w/rho) S^H, Z3^2 block decomposition',
    'N_MC': N_MC,
    'N_pts': int(N_pts),
    'DOMAIN_R': DOMAIN_R,
    'vol_est': float(vol_est),
    'vol_exact': float(vol_exact),
    'vol_ratio': float(vol_est / vol_exact),
    'k_values': K_VALUES,
    'results': {str(k): v for k, v in all_results.items()},
}

with open('balanced_metric_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)
print("  Saved balanced_metric_summary.json")

total_time = time.time() - t0
print(f"\n{'='*72}")
print(f"COMPLETE in {total_time:.1f}s")
for k in K_VALUES:
    r = all_results[k]
    tag = "✓" if r['converged'] else "✗"
    print(f"  k={k}: N={r['N_sections']}, η₂_w={r['eta_2_w']:.2e}, δG={r['delta_G']:.2e} {tag}")
print(f"{'='*72}")
