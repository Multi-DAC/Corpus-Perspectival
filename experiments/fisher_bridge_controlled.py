"""
Fisher Bridge — Controlled Test
=================================
The initial sweep (fisher_bridge_numerical.py) showed correlations between
||F12|| and ||[M1,M2]||, but these could be confounded by θ changing BOTH
the commutator AND the individual matrices.

This script tests the CAUSAL claim by fixing M1+M2 = S (constant) while
varying the commutator. If the correlation persists → genuine relationship.
If it vanishes → confound confirmed.

Method: M1 = (S + D)/2, M2 = (S - D)/2, where S is fixed and D varies.
Then [M1, M2] = -[S, D]/2, so the commutator depends on [S, D].
But M1 + M2 = S is constant.

For V1=V2=I (parallel linear): output depends on S only → F12 constant →
no correlation. This is the null hypothesis test.

For V1≠V2: output depends on M1, M2 separately → F12 varies with D →
question: does it correlate with ||[S, D]||?

Author: Clawd
Date: April 12, 2026
"""

import torch
import torch.nn.functional as F
import numpy as np
from scipy.stats import pearsonr, spearmanr

torch.set_default_dtype(torch.float64)

d = 4
vocab = 16
n = 5
n_steps = 25
n_inputs = 8
seed = 42


def fisher_cross_norm(model_fn, M1, M2, V):
    d2 = M1.numel()
    with torch.no_grad():
        logits = model_fn(M1, M2)
        probs = F.softmax(logits, dim=0)
    J1 = torch.zeros(V, d2)
    J2 = torch.zeros(V, d2)
    for v in range(V):
        m1 = M1.clone().detach().requires_grad_(True)
        m2 = M2.clone().detach().requires_grad_(True)
        out = model_fn(m1, m2)
        out[v].backward()
        J1[v] = m1.grad.flatten()
        J2[v] = m2.grad.flatten()
    mean_J1 = probs @ J1
    mean_J2 = probs @ J2
    C1 = J1 - mean_J1.unsqueeze(0)
    C2 = J2 - mean_J2.unsqueeze(0)
    F12 = torch.zeros(d2, d2)
    for v in range(V):
        F12 += probs[v] * torch.outer(C1[v], C2[v])
    return torch.norm(F12).item()


def rotation_matrix(d, theta, plane=(0, 1)):
    R = torch.eye(d)
    c, s = np.cos(theta), np.sin(theta)
    i, j = plane
    R[i, i] = c; R[i, j] = -s; R[j, i] = s; R[j, j] = c
    return R


def main():
    torch.manual_seed(seed)
    np.random.seed(seed)

    # Fix S = M1 + M2 (the sum stays constant throughout)
    eig1 = torch.tensor([2.0, 1.0, 0.5, 0.2])
    eig2 = torch.tensor([1.5, 0.8, 0.4, 0.1])
    S = torch.diag(eig1) + torch.diag(eig2)  # S = diag(3.5, 1.8, 0.9, 0.3)

    # D parametrized: D(t) = t * A, where A is a fixed off-diagonal matrix
    # This gives [S, D] = t * [S, A], which grows linearly with t
    A = torch.zeros(d, d)
    A[0, 1] = 1.0  # off-diagonal to create non-commutativity with diagonal S
    A[1, 0] = -1.0  # antisymmetric to keep M1, M2 similar structure

    # Verify [S, A] != 0
    SA_comm = S @ A - A @ S
    print(f"||[S, A]|| = {torch.norm(SA_comm):.4f} (must be > 0)")
    print(f"S = diag({eig1.tolist()} + {eig2.tolist()}) = diag({(eig1+eig2).tolist()})")

    # t ranges from 0 to t_max; choose t_max so M1 and M2 stay positive-ish
    t_max = 0.8
    ts = np.linspace(0, t_max, n_steps)

    comm_norms = []
    for t in ts:
        D = t * A
        M1 = (S + D) / 2
        M2 = (S - D) / 2
        comm = M1 @ M2 - M2 @ M1
        comm_norms.append(torch.norm(comm).item())

    print(f"Commutator norm range: [{min(comm_norms):.4f}, {max(comm_norms):.4f}]")
    print()

    # === Test 1: V1 = V2 = I, parallel linear ===
    # Prediction: F12 constant (output depends on S only)
    print("=" * 70)
    print("TEST 1: V1=V2=I, parallel linear (S fixed)")
    print("Prediction: F12 constant → no correlation")
    print("=" * 70)

    ctrl_frob = np.zeros(n_steps)
    for k in range(n_inputs):
        torch.manual_seed(seed + k * 1000)
        X = torch.randn(n, d)
        W_out = torch.randn(vocab, d) * 0.3
        _t_idx = n - 1
        _xt = X[_t_idx]

        def ctrl_model(M1, M2, _X=X, _xt=_xt, _W=W_out):
            s1 = _X @ M1.T @ _xt
            s2 = _X @ M2.T @ _xt
            z1 = (s1.unsqueeze(1) * _X).sum(0)
            z2 = (s2.unsqueeze(1) * _X).sum(0)
            return _W @ (z1 + z2 + _xt)

        for i, t in enumerate(ts):
            D = t * A
            M1 = (S + D) / 2
            M2 = (S - D) / 2
            ctrl_frob[i] += fisher_cross_norm(ctrl_model, M1, M2, vocab) / n_inputs

    rp, pp = pearsonr(comm_norms, ctrl_frob)
    print(f"Pearson r = {rp:+.4f} (p = {pp:.2e})")
    print(f"F12 range: [{ctrl_frob.min():.6f}, {ctrl_frob.max():.6f}]")
    print(f"Relative variation: {(ctrl_frob.max()-ctrl_frob.min())/max(ctrl_frob.max(),1e-15):.6f}")
    print()

    # === Test 2: V1 ≠ V2, parallel linear ===
    print("=" * 70)
    print("TEST 2: V1≠V2, parallel linear (S fixed)")
    print("Prediction: F12 varies → question is whether it correlates with commutator")
    print("=" * 70)

    test2_frob = np.zeros(n_steps)
    for k in range(n_inputs):
        torch.manual_seed(seed + k * 1000)
        X = torch.randn(n, d)
        V1 = torch.randn(d, d) * 0.5
        V2 = torch.randn(d, d) * 0.5
        W_out = torch.randn(vocab, d) * 0.3
        _t_idx = n - 1
        _xt = X[_t_idx]

        def model2(M1, M2, _X=X, _xt=_xt, _W=W_out, _V1=V1, _V2=V2):
            s1 = _X @ M1.T @ _xt
            s2 = _X @ M2.T @ _xt
            z1 = (s1.unsqueeze(1) * (_X @ _V1.T)).sum(0)
            z2 = (s2.unsqueeze(1) * (_X @ _V2.T)).sum(0)
            return _W @ (z1 + z2 + _xt)

        for i, t in enumerate(ts):
            D = t * A
            M1 = (S + D) / 2
            M2 = (S - D) / 2
            test2_frob[i] += fisher_cross_norm(model2, M1, M2, vocab) / n_inputs

    rp2, pp2 = pearsonr(comm_norms, test2_frob)
    rs2, ps2 = spearmanr(comm_norms, test2_frob)
    print(f"Pearson r = {rp2:+.4f} (p = {pp2:.2e})")
    print(f"Spearman r = {rs2:+.4f} (p = {ps2:.2e})")
    print(f"F12 range: [{test2_frob.min():.6f}, {test2_frob.max():.6f}]")
    print(f"Relative variation: {(test2_frob.max()-test2_frob.min())/max(test2_frob.max(),1e-15):.6f}")
    print()

    # === Test 3: V1 ≠ V2, parallel softmax ===
    print("=" * 70)
    print("TEST 3: V1≠V2, parallel softmax (S fixed)")
    print("=" * 70)

    test3_frob = np.zeros(n_steps)
    _sd = np.sqrt(d)
    for k in range(n_inputs):
        torch.manual_seed(seed + k * 1000)
        X = torch.randn(n, d)
        V1 = torch.randn(d, d) * 0.5
        V2 = torch.randn(d, d) * 0.5
        W_out = torch.randn(vocab, d) * 0.3
        _t_idx = n - 1
        _xt = X[_t_idx]

        def model3(M1, M2, _X=X, _xt=_xt, _W=W_out, _V1=V1, _V2=V2):
            s1 = F.softmax(_X @ M1.T @ _xt / _sd, dim=0)
            s2 = F.softmax(_X @ M2.T @ _xt / _sd, dim=0)
            z1 = (s1.unsqueeze(1) * (_X @ _V1.T)).sum(0)
            z2 = (s2.unsqueeze(1) * (_X @ _V2.T)).sum(0)
            return _W @ (z1 + z2 + _xt)

        for i, t in enumerate(ts):
            D = t * A
            M1 = (S + D) / 2
            M2 = (S - D) / 2
            test3_frob[i] += fisher_cross_norm(model3, M1, M2, vocab) / n_inputs

    rp3, pp3 = pearsonr(comm_norms, test3_frob)
    rs3, ps3 = spearmanr(comm_norms, test3_frob)
    print(f"Pearson r = {rp3:+.4f} (p = {pp3:.2e})")
    print(f"Spearman r = {rs3:+.4f} (p = {ps3:.2e})")
    print(f"F12 range: [{test3_frob.min():.6f}, {test3_frob.max():.6f}]")
    print()

    # === Test 4: V1 ≠ V2, sequential softmax (S fixed) ===
    print("=" * 70)
    print("TEST 4: V1≠V2, sequential softmax (S fixed)")
    print("=" * 70)

    test4_frob = np.zeros(n_steps)
    for k in range(n_inputs):
        torch.manual_seed(seed + k * 1000)
        X = torch.randn(n, d)
        V1 = torch.randn(d, d) * 0.5
        V2 = torch.randn(d, d) * 0.5
        W_out = torch.randn(vocab, d) * 0.3

        def model4(M1, M2, _X=X, _W=W_out, _V1=V1, _V2=V2):
            _n = _X.shape[0]
            _d = _X.shape[1]
            _sd = np.sqrt(_d)
            _t = _n - 1
            # Layer 1
            scores1 = F.softmax(_X @ M1 @ _X.T / _sd, dim=1)
            Z1 = scores1 @ (_X @ _V1.T)
            H1 = Z1 + _X
            # Layer 2
            h1t = H1[_t]
            s2 = F.softmax(H1 @ M2.T @ h1t / _sd, dim=0)
            z2 = (s2.unsqueeze(1) * (H1 @ _V2.T)).sum(0)
            return _W @ (z2 + h1t)

        for i, t_val in enumerate(ts):
            D = t_val * A
            M1 = (S + D) / 2
            M2 = (S - D) / 2
            test4_frob[i] += fisher_cross_norm(model4, M1, M2, vocab) / n_inputs

    rp4, pp4 = pearsonr(comm_norms, test4_frob)
    rs4, ps4 = spearmanr(comm_norms, test4_frob)
    print(f"Pearson r = {rp4:+.4f} (p = {pp4:.2e})")
    print(f"Spearman r = {rs4:+.4f} (p = {ps4:.2e})")
    print(f"F12 range: [{test4_frob.min():.6f}, {test4_frob.max():.6f}]")
    print()

    # === Summary ===
    print("=" * 70)
    print("SUMMARY: Controlled experiment (M1+M2 fixed)")
    print("=" * 70)
    print(f"{'Test':35s} {'Pearson r':>10} {'p-value':>10}")
    print("-" * 60)
    print(f"{'V=I parallel linear':35s} {rp:+10.4f} {pp:10.2e}")
    print(f"{'V1≠V2 parallel linear':35s} {rp2:+10.4f} {pp2:10.2e}")
    print(f"{'V1≠V2 parallel softmax':35s} {rp3:+10.4f} {pp3:10.2e}")
    print(f"{'V1≠V2 sequential softmax':35s} {rp4:+10.4f} {pp4:10.2e}")
    print()

    if abs(rp) < 0.1:
        print("V=I control PASSES: F12 constant when output depends on S only.")
    else:
        print(f"V=I control FAILS: F12 varies (r={rp:+.4f}) even though output should depend on S only.")
        print("  → Numerical issue or model formulation error.")

    if abs(rp4) > 0.5:
        print(f"Sequential softmax: SIGNIFICANT correlation (r={rp4:+.4f})")
        print("  → Commutator has genuine causal effect on Fisher cross-term")
        print("  → through cross-layer composition")
    else:
        print(f"Sequential softmax: NO significant correlation (r={rp4:+.4f})")
        print("  → The initial sweep correlation was likely a confound")

    # Save summary
    import json
    output = {
        'experiment': 'controlled (M1+M2 fixed)',
        'results': {
            'V=I parallel linear': {'pearson_r': rp, 'p': pp},
            'V1!=V2 parallel linear': {'pearson_r': rp2, 'p': pp2, 'spearman_r': rs2},
            'V1!=V2 parallel softmax': {'pearson_r': rp3, 'p': pp3, 'spearman_r': rs3},
            'V1!=V2 sequential softmax': {'pearson_r': rp4, 'p': pp4, 'spearman_r': rs4},
        },
        'commutator_norms': comm_norms,
    }
    with open('fisher_bridge_controlled_results.json', 'w') as f:
        json.dump(output, f, indent=2)
    print("\nResults saved to fisher_bridge_controlled_results.json")


if __name__ == '__main__':
    main()
