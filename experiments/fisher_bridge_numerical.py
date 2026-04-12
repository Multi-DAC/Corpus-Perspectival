"""
Fisher Bridge Computation — Numerical Verification
====================================================
Does ||Fisher cross-term between heads|| correlate with ||[M1, M2]||_F?

Tests 5 model configurations:
  1. 1-layer parallel, linear attention (heads summed, never composed)
  2. 1-layer parallel, softmax attention (nonlinear but still parallel)
  3. 2-layer parallel + ReLU FFN (nonlinear second layer)
  4. 2-layer sequential, linear attention (head 2 operates on head 1's output)
  5. 2-layer sequential, softmax attention (most transformer-like)

Analytical prediction before running:
  - Models 1-3: Fisher cross-term should NOT correlate with commutator
    (parallel heads never compose, so [M1,M2] is invisible)
  - Models 4-5: Fisher cross-term SHOULD correlate with commutator
    (sequential composition creates M1*M2 products in the gradient)

Author: Clawd
Date: April 12, 2026
"""

import torch
import torch.nn.functional as F
import numpy as np
import json
import sys

torch.set_default_dtype(torch.float64)

# ============================================================
# Configuration
# ============================================================
d = 4          # embedding dimension
vocab = 16     # vocabulary size
n = 5          # sequence length
n_thetas = 25  # angular resolution
n_inputs = 8   # number of random inputs to average over
seed = 42

# ============================================================
# Utilities
# ============================================================

def rotation_matrix(d, theta, plane=(0, 1)):
    """Rotation in d dimensions, acting in the specified 2D plane."""
    R = torch.eye(d)
    c, s = np.cos(theta), np.sin(theta)
    i, j = plane
    R[i, i] = c; R[i, j] = -s; R[j, i] = s; R[j, j] = c
    return R


def commutator_norm(A, B):
    """||[A, B]||_F = ||AB - BA||_F"""
    return torch.norm(A @ B - B @ A).item()


def fisher_cross_norm(model_fn, M1, M2, V):
    """
    Compute ||F_{M1,M2}||_F for a model that takes (M1, M2) -> logits.

    F_{M1,M2}[i,j] = sum_v p(v) * (dlog p(v)/dM1_i) * (dlog p(v)/dM2_j)

    where dlog p(v)/dM_i = dℓ_v/dM_i - E_p[dℓ/dM_i]
    """
    d2 = M1.numel()

    with torch.no_grad():
        logits = model_fn(M1, M2)
        probs = F.softmax(logits, dim=0)

    # Jacobians: dℓ_v / d(vec(Mh)) for each v
    J1 = torch.zeros(V, d2)
    J2 = torch.zeros(V, d2)

    for v in range(V):
        m1 = M1.clone().detach().requires_grad_(True)
        m2 = M2.clone().detach().requires_grad_(True)
        out = model_fn(m1, m2)
        out[v].backward()
        J1[v] = m1.grad.flatten()
        J2[v] = m2.grad.flatten()

    # Center: dlog p(v)/dθ = dℓ_v/dθ - E_p[dℓ/dθ]
    mean_J1 = probs @ J1  # (d2,)
    mean_J2 = probs @ J2
    C1 = J1 - mean_J1.unsqueeze(0)
    C2 = J2 - mean_J2.unsqueeze(0)

    # Fisher cross-block: F12 = sum_v p(v) C1[v] (x) C2[v]
    # ||F12||_F^2 = sum_v sum_w p(v)p(w) (C1[v]·C1[w])(C2[v]·C2[w])
    # Direct computation (d2 is small):
    F12 = torch.zeros(d2, d2)
    for v in range(V):
        F12 += probs[v] * torch.outer(C1[v], C2[v])

    frob = torch.norm(F12).item()
    trace = torch.trace(F12).item()

    return frob, trace


# ============================================================
# Model definitions
# ============================================================

def make_models(X, V1, V2, W_out, W_ff):
    """Return dict of model functions, each mapping (M1, M2) -> logits."""
    _n = X.shape[0]
    _d = X.shape[1]
    _t = _n - 1
    _xt = X[_t]
    _sd = np.sqrt(_d)

    def parallel_linear(M1, M2):
        s1 = X @ M1.T @ _xt
        s2 = X @ M2.T @ _xt
        z1 = (s1.unsqueeze(1) * (X @ V1.T)).sum(0)
        z2 = (s2.unsqueeze(1) * (X @ V2.T)).sum(0)
        return W_out @ (z1 + z2 + _xt)

    def parallel_softmax(M1, M2):
        s1 = F.softmax(X @ M1.T @ _xt / _sd, dim=0)
        s2 = F.softmax(X @ M2.T @ _xt / _sd, dim=0)
        z1 = (s1.unsqueeze(1) * (X @ V1.T)).sum(0)
        z2 = (s2.unsqueeze(1) * (X @ V2.T)).sum(0)
        return W_out @ (z1 + z2 + _xt)

    def parallel_ffn(M1, M2):
        s1 = X @ M1.T @ _xt
        s2 = X @ M2.T @ _xt
        z1 = (s1.unsqueeze(1) * (X @ V1.T)).sum(0)
        z2 = (s2.unsqueeze(1) * (X @ V2.T)).sum(0)
        h1 = z1 + z2 + _xt
        h2 = torch.relu(W_ff @ h1)
        return W_out @ h2

    def sequential_linear(M1, M2):
        # Layer 1: head 1 processes all positions
        scores1 = X @ M1 @ X.T  # (n, n)
        Z1 = scores1 @ (X @ V1.T)  # (n, d)
        H1 = Z1 + X  # residual
        # Layer 2: head 2 at position t, attending to H1
        h1t = H1[_t]
        s2 = H1 @ M2.T @ h1t  # (n,)
        z2 = (s2.unsqueeze(1) * (H1 @ V2.T)).sum(0)
        return W_out @ (z2 + h1t)

    def sequential_softmax(M1, M2):
        # Layer 1: head 1 with softmax
        scores1_raw = X @ M1 @ X.T / _sd  # (n, n)
        scores1 = F.softmax(scores1_raw, dim=1)  # softmax over keys (dim=1)
        Z1 = scores1 @ (X @ V1.T)
        H1 = Z1 + X
        # Layer 2: head 2 with softmax
        h1t = H1[_t]
        s2 = F.softmax(H1 @ M2.T @ h1t / _sd, dim=0)
        z2 = (s2.unsqueeze(1) * (H1 @ V2.T)).sum(0)
        return W_out @ (z2 + h1t)

    return {
        '1L-par-lin': parallel_linear,
        '1L-par-sfx': parallel_softmax,
        '2L-par-ffn': parallel_ffn,
        '2L-seq-lin': sequential_linear,
        '2L-seq-sfx': sequential_softmax,
    }


# ============================================================
# Main computation
# ============================================================

def main():
    torch.manual_seed(seed)
    np.random.seed(seed)

    # Fixed eigenvalues for M1 and M2
    eig1 = torch.tensor([2.0, 1.0, 0.5, 0.2])
    eig2 = torch.tensor([1.5, 0.8, 0.4, 0.1])
    M1 = torch.diag(eig1)

    thetas = np.linspace(0, np.pi/2, n_thetas)

    # Storage: averaged over random inputs
    model_names = ['1L-par-lin', '1L-par-sfx', '2L-par-ffn', '2L-seq-lin', '2L-seq-sfx']
    frob_avg = {name: np.zeros(n_thetas) for name in model_names}
    trace_avg = {name: np.zeros(n_thetas) for name in model_names}
    comm_norms = np.zeros(n_thetas)

    # Compute commutator norms (these don't depend on input)
    for i, theta in enumerate(thetas):
        R = rotation_matrix(d, theta)
        M2 = R @ torch.diag(eig2) @ R.T
        comm_norms[i] = commutator_norm(M1, M2)

    print(f"Fisher Bridge Numerical Verification", flush=True)
    print(f"d={d}, vocab={vocab}, n={n}, n_thetas={n_thetas}, n_inputs={n_inputs}", flush=True)
    print(f"Eigenvalues M1: {eig1.tolist()}", flush=True)
    print(f"Eigenvalues M2: {eig2.tolist()}", flush=True)
    print(f"Commutator norm range: [{comm_norms.min():.4f}, {comm_norms.max():.4f}]", flush=True)
    print(flush=True)

    for k in range(n_inputs):
        torch.manual_seed(seed + k * 1000)
        X = torch.randn(n, d)
        V1 = torch.randn(d, d) * 0.5
        V2 = torch.randn(d, d) * 0.5
        W_out = torch.randn(vocab, d) * 0.3
        W_ff = torch.randn(d, d) * 0.3

        models = make_models(X, V1, V2, W_out, W_ff)

        for i, theta in enumerate(thetas):
            R = rotation_matrix(d, theta)
            M2 = R @ torch.diag(eig2) @ R.T

            for name in model_names:
                frob, tr = fisher_cross_norm(models[name], M1, M2, vocab)
                frob_avg[name][i] += frob / n_inputs
                trace_avg[name][i] += tr / n_inputs

        print(f"  Input {k+1}/{n_inputs} done", flush=True)

    # ============================================================
    # Analysis
    # ============================================================

    from scipy.stats import pearsonr, spearmanr

    print("\n" + "=" * 80)
    print("RESULTS: Fisher Cross-Block Frobenius Norm vs Commutator Norm")
    print("=" * 80)

    # Table header
    header = f"{'theta':>6} {'||[M1,M2]||':>12}"
    for name in model_names:
        header += f" {name:>12}"
    print(header)
    print("-" * (20 + 13 * len(model_names)))

    for i in range(n_thetas):
        row = f"{thetas[i]:6.3f} {comm_norms[i]:12.6f}"
        for name in model_names:
            row += f" {frob_avg[name][i]:12.6f}"
        print(row)

    print("\n" + "=" * 80)
    print("CORRELATIONS: ||F12||_F vs ||[M1,M2]||_F (averaged over inputs)")
    print("=" * 80)

    print(f"{'Model':15s} {'Pearson r':>10} {'p-val':>10} {'Spearman r':>11} {'p-val':>10} {'Verdict':>10}")
    print("-" * 70)

    results_json = {}

    for name in model_names:
        rp, pp = pearsonr(comm_norms, frob_avg[name])
        rs, ps = spearmanr(comm_norms, frob_avg[name])

        if abs(rp) > 0.8 and pp < 0.01:
            verdict = "STRONG"
        elif abs(rp) > 0.5 and pp < 0.05:
            verdict = "MODERATE"
        elif abs(rp) > 0.3 and pp < 0.05:
            verdict = "WEAK"
        else:
            verdict = "NONE"

        print(f"{name:15s} {rp:+10.4f} {pp:10.2e} {rs:+11.4f} {ps:10.2e} {verdict:>10}")

        results_json[name] = {
            'frob_values': frob_avg[name].tolist(),
            'trace_values': trace_avg[name].tolist(),
            'pearson_r': rp,
            'pearson_p': pp,
            'spearman_r': rs,
            'spearman_p': ps,
            'verdict': verdict,
        }

    # Also report relative variation
    print(f"\n{'Model':15s} {'F12(θ=0)':>12} {'F12(θ=π/4)':>12} {'F12(θ=π/2)':>12} {'Rel Δ':>10}")
    print("-" * 65)
    for name in model_names:
        f0 = frob_avg[name][0]
        fmid = frob_avg[name][n_thetas // 2]
        fend = frob_avg[name][-1]
        rel = (fend - f0) / max(f0, 1e-15)
        print(f"{name:15s} {f0:12.6f} {fmid:12.6f} {fend:12.6f} {rel:+10.4f}")

    # ============================================================
    # Control: V1 = V2 = I (parallel linear should fully decouple)
    # ============================================================

    print("\n" + "=" * 80)
    print("CONTROL: V1 = V2 = I (tests analytical prediction)")
    print("=" * 80)

    I_d = torch.eye(d)
    ctrl_frob = np.zeros(n_thetas)

    for k in range(n_inputs):
        torch.manual_seed(seed + k * 1000)
        X = torch.randn(n, d)
        W_out_ctrl = torch.randn(vocab, d) * 0.3

        _n, _d = X.shape
        _t = _n - 1
        _xt = X[_t]

        def ctrl_model(M1, M2, _X=X, _xt=_xt, _W=W_out_ctrl):
            s1 = _X @ M1.T @ _xt
            s2 = _X @ M2.T @ _xt
            z1 = (s1.unsqueeze(1) * _X).sum(0)  # V = I
            z2 = (s2.unsqueeze(1) * _X).sum(0)
            return _W @ (z1 + z2 + _xt)

        for i, theta in enumerate(thetas):
            R = rotation_matrix(d, theta)
            M2 = R @ torch.diag(eig2) @ R.T
            frob, _ = fisher_cross_norm(ctrl_model, M1, M2, vocab)
            ctrl_frob[i] += frob / n_inputs

    rp, pp = pearsonr(comm_norms, ctrl_frob)
    rs, ps = spearmanr(comm_norms, ctrl_frob)
    print(f"V=I parallel linear: Pearson r={rp:+.4f} (p={pp:.2e}), Spearman r={rs:+.4f} (p={ps:.2e})")
    print(f"  Range: [{ctrl_frob.min():.8f}, {ctrl_frob.max():.8f}]")
    print(f"  Relative variation: {(ctrl_frob.max()-ctrl_frob.min())/max(ctrl_frob.max(),1e-15):.6f}")

    # ============================================================
    # Save results
    # ============================================================

    output = {
        'config': {
            'd': d, 'vocab': vocab, 'n': n,
            'n_thetas': n_thetas, 'n_inputs': n_inputs, 'seed': seed,
            'eigenvalues_M1': eig1.tolist(),
            'eigenvalues_M2': eig2.tolist(),
        },
        'thetas': thetas.tolist(),
        'commutator_norms': comm_norms.tolist(),
        'models': results_json,
        'control_V_identity': {
            'frob_values': ctrl_frob.tolist(),
            'pearson_r': pearsonr(comm_norms, ctrl_frob)[0],
            'spearman_r': spearmanr(comm_norms, ctrl_frob)[0],
        }
    }

    outpath = 'fisher_bridge_results.json'
    with open(outpath, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {outpath}")

    # ============================================================
    # Interpretation
    # ============================================================

    print("\n" + "=" * 80)
    print("INTERPRETATION")
    print("=" * 80)

    seq_corr = any(abs(results_json[n]['pearson_r']) > 0.5 for n in ['2L-seq-lin', '2L-seq-sfx'])
    par_corr = any(abs(results_json[n]['pearson_r']) > 0.5 for n in ['1L-par-lin', '1L-par-sfx'])

    if seq_corr and not par_corr:
        print("CONFIRMED: Commutator-Fisher correlation requires SEQUENTIAL composition.")
        print("  Parallel heads: commutator invisible (no correlation)")
        print("  Sequential heads: commutator visible (correlation detected)")
        print("  Implication: In real transformers, the CommVar-Fisher connection")
        print("  works through CROSS-LAYER interaction, not within-layer.")
    elif seq_corr and par_corr:
        print("STRONGER THAN EXPECTED: Correlation in both parallel and sequential cases.")
        print("  The output softmax creates sufficient coupling even for parallel heads.")
    elif not seq_corr and not par_corr:
        print("NO CORRELATION in any configuration.")
        print("  The Fisher-CommVar connection may be more indirect than hypothesized.")
    else:
        print("UNEXPECTED PATTERN: parallel correlates but sequential doesn't.")
        print("  This would be very surprising. Check computation for bugs.")


if __name__ == '__main__':
    main()
