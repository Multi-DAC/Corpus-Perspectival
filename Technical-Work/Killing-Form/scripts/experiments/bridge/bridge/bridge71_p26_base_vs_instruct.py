"""
Bridge #71 — P26: Base vs Instruct Killing Form Comparison
==========================================================

Tests whether RLHF/instruction-tuning changes the attention Killing form.
Compares Qwen2.5-1.5B (base) vs Qwen2.5-1.5B-Instruct (chat).

Pre-registered predictions (memory/p26_predictions.md):
  P26-A: AF(instruct) > AF(base) by >= 0.01
  P26-B: Difference concentrated in middle layers
  P26-C: Commutator variance ratio >= 1.5x
  P26-D: Wider eigenvalue spread in instruct
  P26-E: Qwen2.5-1.5B AF in range 0.02-0.10

Architecture: 28 layers, 12 Q-heads, 2 KV-heads (GQA), d_model=1536, d_head=128
Uses Q projections for Killing form (12 heads, full structure).

Author: Clawd
Date: April 10, 2026
Pre-registered: April 10, 2026 5:30 AM PST (before any data)
"""

import numpy as np
from scipy import stats
import json, time, sys

# ============================================================
# CONFIGURATION
# ============================================================
MODELS = {
    'base': 'Qwen/Qwen2.5-1.5B',
    'instruct': 'Qwen/Qwen2.5-1.5B-Instruct',
}
PROJ_DIM = 64          # Projection dimension for efficiency
SEED = 71              # Bridge 71
N_RANDOM_TRIALS = 20   # For random baseline
AF_THRESHOLD = 0.10    # Abelian fraction threshold (eigenvalue < 10% of max)

# ============================================================
# HELPER FUNCTIONS (from bridge71_real_attention_v2.py)
# ============================================================

def extract_q_heads(model_name):
    """Extract per-head Q projection matrices from a Qwen2.5 model."""
    from transformers import AutoModelForCausalLM, AutoConfig
    import torch

    config = AutoConfig.from_pretrained(model_name)
    n_heads = config.num_attention_heads      # 12
    d_model = config.hidden_size              # 1536
    n_layers = config.num_hidden_layers       # 28
    d_head = d_model // n_heads               # 128

    print(f"  Loading {model_name}...")
    model = AutoModelForCausalLM.from_pretrained(model_name, dtype=torch.float32)

    layer_heads = {}
    for layer_idx in range(n_layers):
        key = f"model.layers.{layer_idx}.self_attn.q_proj.weight"
        W_Q = None
        for name, param in model.named_parameters():
            if name == key:
                W_Q = param.detach().cpu().numpy()  # (1536, 1536)
                break

        if W_Q is None:
            print(f"  WARNING: {key} not found")
            continue

        # Split into per-head: (1536, 1536) -> 12 heads of (d_head, d_model)
        # Qwen stores Q as (n_heads * d_head, d_model) = (1536, 1536)
        # Each head h gets rows [h*d_head : (h+1)*d_head]
        heads = []
        for h in range(n_heads):
            W_Q_h = W_Q[h*d_head:(h+1)*d_head, :]  # (128, 1536)
            # Form the attention-like matrix: W_Q_h^T @ W_Q_h (1536, 1536) is too big
            # Instead use W_Q_h directly as the head operator (128, 1536)
            # The commutator structure lives in the output space
            heads.append(W_Q_h)

        layer_heads[layer_idx] = heads

    del model  # Free memory
    import gc; gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    return layer_heads, n_heads, d_model, n_layers, d_head


def compute_killing_form(heads, proj_matrix):
    """Compute Killing form from a list of head matrices."""
    n_h = len(heads)

    # Project to smaller space: A_h -> P^T @ A_h @ P  won't work for (128, 1536)
    # Instead project both dims: heads are (128, 1536), project to (proj_dim, proj_dim)
    # Use two projectors: P_out (proj_dim, 128), P_in (1536, proj_dim)
    p_out, p_in = proj_matrix
    proj_heads = [p_out @ A @ p_in for A in heads]  # each (proj_dim, proj_dim)

    # Commutator norms
    comm_norms = np.zeros((n_h, n_h))
    for h in range(n_h):
        for hp in range(h+1, n_h):
            comm = proj_heads[h] @ proj_heads[hp] - proj_heads[hp] @ proj_heads[h]
            norm = np.linalg.norm(comm, 'fro')
            comm_norms[h, hp] = norm
            comm_norms[hp, h] = norm

    typical = np.mean([np.linalg.norm(A, 'fro') for A in proj_heads])
    if typical > 0:
        comm_normalized = comm_norms / (typical ** 2)
    else:
        comm_normalized = comm_norms

    # Killing form: kappa_{ab} = sum_k Tr([W_a,W_k][W_b,W_k])
    killing = np.zeros((n_h, n_h))
    for h in range(n_h):
        for hp in range(n_h):
            val = 0
            for k in range(n_h):
                c1 = proj_heads[h] @ proj_heads[k] - proj_heads[k] @ proj_heads[h]
                c2 = proj_heads[hp] @ proj_heads[k] - proj_heads[k] @ proj_heads[hp]
                val += np.trace(c1.T @ c2)
            killing[h, hp] = val

    max_k = np.max(np.abs(killing))
    killing_norm = killing / max_k if max_k > 0 else killing

    # Eigenvalues
    eigenvalues = np.sort(np.abs(np.linalg.eigvalsh(killing_norm)))

    # Metrics
    mask = np.ones_like(comm_normalized, dtype=bool)
    np.fill_diagonal(mask, False)

    n_null = int(np.sum(eigenvalues < AF_THRESHOLD))

    return {
        'mean_comm': float(np.mean(comm_normalized[mask])),
        'comm_var': float(np.var(comm_normalized[mask])),
        'killing_trace': float(np.trace(killing_norm)),
        'eigenvalues': eigenvalues.tolist(),
        'ev_min': float(eigenvalues[0]),
        'ev_max': float(eigenvalues[-1]),
        'ev_spread': float(eigenvalues[-1] - eigenvalues[0]),
        'n_null': n_null,
        'abelian_frac': n_null / n_h,
    }


def analyze_model(model_name, label):
    """Full analysis pipeline for one model."""
    print(f"\n{'='*70}")
    print(f"Analyzing: {label} ({model_name})")
    print(f"{'='*70}")

    t0 = time.time()
    layer_heads, n_heads, d_model, n_layers, d_head = extract_q_heads(model_name)
    print(f"  Extracted {n_heads} heads from {n_layers} layers in {time.time()-t0:.1f}s")

    # Create projection matrices (same seed for both models!)
    np.random.seed(SEED)
    p_out = np.random.randn(PROJ_DIM, d_head) / np.sqrt(d_head)
    p_in = np.random.randn(d_model, PROJ_DIM) / np.sqrt(d_model)
    proj = (p_out, p_in)

    results = {}
    t1 = time.time()
    for layer_idx in sorted(layer_heads.keys()):
        results[layer_idx] = compute_killing_form(layer_heads[layer_idx], proj)
        if (layer_idx + 1) % 7 == 0:
            elapsed = time.time() - t1
            print(f"  Layer {layer_idx}: AF={results[layer_idx]['abelian_frac']:.3f}, "
                  f"CommVar={results[layer_idx]['comm_var']:.6f} ({elapsed:.1f}s)")

    print(f"  All {n_layers} layers analyzed in {time.time()-t1:.1f}s")
    return results, n_heads, d_model, n_layers, d_head


# ============================================================
# MAIN ANALYSIS
# ============================================================
if __name__ == '__main__':
    print("Bridge #71 — P26: Base vs Instruct Killing Form")
    print("Pre-registered predictions at memory/p26_predictions.md")
    print(f"Projection dim: {PROJ_DIM}, AF threshold: {AF_THRESHOLD}")
    print()

    # Analyze both models
    base_results, n_heads, d_model, n_layers, d_head = analyze_model(
        MODELS['base'], 'Qwen2.5-1.5B (Base)')
    instruct_results, _, _, _, _ = analyze_model(
        MODELS['instruct'], 'Qwen2.5-1.5B (Instruct)')

    # ============================================================
    # COMPARISON
    # ============================================================
    print(f"\n{'='*70}")
    print("P26 COMPARISON: Base vs Instruct")
    print(f"{'='*70}\n")

    # Per-layer comparison
    print(f"{'Layer':>5} {'AF_base':>8} {'AF_inst':>8} {'Diff':>8} "
          f"{'CV_base':>10} {'CV_inst':>10} {'CV_ratio':>9}")
    print("-" * 65)

    layer_indices = sorted(base_results.keys())
    for l in layer_indices:
        b = base_results[l]
        i = instruct_results[l]
        cv_ratio = i['comm_var'] / b['comm_var'] if b['comm_var'] > 0 else float('inf')
        print(f"{l:>5} {b['abelian_frac']:>8.3f} {i['abelian_frac']:>8.3f} "
              f"{i['abelian_frac']-b['abelian_frac']:>+8.3f} "
              f"{b['comm_var']:>10.6f} {i['comm_var']:>10.6f} {cv_ratio:>9.3f}")

    # Global averages
    def avg(results, key):
        return np.mean([results[l][key] for l in results])

    print(f"\n{'Metric':<20} {'Base':>10} {'Instruct':>10} {'Diff':>10} {'Ratio':>8}")
    print("-" * 62)
    for k in ['abelian_frac', 'comm_var', 'mean_comm', 'ev_spread', 'ev_min']:
        b_val = avg(base_results, k)
        i_val = avg(instruct_results, k)
        ratio = i_val / b_val if b_val != 0 else float('inf')
        print(f"{k:<20} {b_val:>10.5f} {i_val:>10.5f} {i_val-b_val:>+10.5f} {ratio:>8.3f}")

    # ============================================================
    # STATISTICAL TESTS
    # ============================================================
    print(f"\n{'='*70}")
    print("STATISTICAL TESTS")
    print(f"{'='*70}\n")

    for k in ['abelian_frac', 'comm_var', 'ev_spread']:
        b_vals = [base_results[l][k] for l in layer_indices]
        i_vals = [instruct_results[l][k] for l in layer_indices]
        t_stat, p_val = stats.ttest_rel(b_vals, i_vals)  # paired by layer
        direction = "HIGHER" if np.mean(i_vals) > np.mean(b_vals) else "LOWER"
        print(f"  {k}: instruct is {direction} (paired t={t_stat:.3f}, p={p_val:.4f})")

    # ============================================================
    # PREDICTION EVALUATION
    # ============================================================
    print(f"\n{'='*70}")
    print("PRE-REGISTERED PREDICTION EVALUATION")
    print(f"{'='*70}\n")

    af_base = avg(base_results, 'abelian_frac')
    af_inst = avg(instruct_results, 'abelian_frac')
    af_diff = af_inst - af_base

    cv_base = avg(base_results, 'comm_var')
    cv_inst = avg(instruct_results, 'comm_var')
    cv_ratio = cv_inst / cv_base if cv_base > 0 else float('inf')

    sp_base = avg(base_results, 'ev_spread')
    sp_inst = avg(instruct_results, 'ev_spread')

    # P26-A: AF(instruct) > AF(base) by >= 0.01
    print(f"P26-A: AF(instruct) > AF(base) by >= 0.01")
    print(f"  AF(base) = {af_base:.4f}, AF(instruct) = {af_inst:.4f}, diff = {af_diff:+.4f}")
    if af_diff >= 0.01:
        print(f"  RESULT: **CONFIRMED**")
    elif af_diff > 0:
        print(f"  RESULT: DIRECTION CORRECT but below 0.01 threshold")
    else:
        print(f"  RESULT: **FALSIFIED** (instruct AF is not higher)")
    print()

    # P26-B: Difference concentrated in middle layers
    early = layer_indices[:7]
    mid = layer_indices[7:21]
    late = layer_indices[21:]
    diff_early = np.mean([instruct_results[l]['abelian_frac'] - base_results[l]['abelian_frac'] for l in early])
    diff_mid = np.mean([instruct_results[l]['abelian_frac'] - base_results[l]['abelian_frac'] for l in mid])
    diff_late = np.mean([instruct_results[l]['abelian_frac'] - base_results[l]['abelian_frac'] for l in late])

    print(f"P26-B: Difference concentrated in middle layers")
    print(f"  Early (0-6): {diff_early:+.4f}")
    print(f"  Middle (7-20): {diff_mid:+.4f}")
    print(f"  Late (21-27): {diff_late:+.4f}")
    if abs(diff_mid) > abs(diff_early) and abs(diff_mid) > abs(diff_late):
        print(f"  RESULT: **CONFIRMED** (middle layers show largest difference)")
    else:
        max_region = 'early' if abs(diff_early) >= max(abs(diff_mid), abs(diff_late)) else \
                     ('late' if abs(diff_late) >= abs(diff_mid) else 'middle')
        print(f"  RESULT: **FALSIFIED** (largest difference in {max_region} layers)")
    print()

    # P26-C: Commutator variance ratio >= 1.5x
    print(f"P26-C: Commutator variance ratio >= 1.5x")
    print(f"  CV(base) = {cv_base:.6f}, CV(instruct) = {cv_inst:.6f}, ratio = {cv_ratio:.3f}")
    if cv_ratio >= 1.5:
        print(f"  RESULT: **CONFIRMED**")
    elif cv_ratio > 1.0:
        print(f"  RESULT: DIRECTION CORRECT but below 1.5x threshold")
    else:
        print(f"  RESULT: **FALSIFIED** (ratio < 1.0)")
    print()

    # P26-D: Wider eigenvalue spread in instruct
    print(f"P26-D: Wider eigenvalue spread in instruct")
    print(f"  Spread(base) = {sp_base:.4f}, Spread(instruct) = {sp_inst:.4f}")
    if sp_inst > sp_base:
        print(f"  RESULT: **CONFIRMED**")
    else:
        print(f"  RESULT: **FALSIFIED**")
    print()

    # P26-E: Qwen2.5-1.5B AF in range 0.02-0.10
    print(f"P26-E: Qwen2.5-1.5B base AF in range [0.02, 0.10]")
    print(f"  AF(base) = {af_base:.4f}")
    if 0.02 <= af_base <= 0.10:
        print(f"  RESULT: **CONFIRMED**")
    else:
        print(f"  RESULT: **FALSIFIED** (outside predicted range)")
    print()

    # P26-META: At least one of A-D falsified
    confirmed = sum([
        af_diff >= 0.01,
        abs(diff_mid) > abs(diff_early) and abs(diff_mid) > abs(diff_late),
        cv_ratio >= 1.5,
        sp_inst > sp_base,
    ])
    falsified = 4 - confirmed

    print(f"P26-META: At least one of A-D falsified")
    print(f"  Confirmed: {confirmed}/4, Falsified: {falsified}/4")
    if falsified >= 1:
        print(f"  RESULT: **CONFIRMED** (meta-prediction correct)")
    else:
        print(f"  RESULT: **FALSIFIED** (all predictions confirmed — surprisingly good)")
    print()

    # Layer depth correlation for both models
    print(f"{'='*70}")
    print("LAYER DEPTH CORRELATIONS (P28 replication)")
    print(f"{'='*70}\n")

    for label, res in [('Base', base_results), ('Instruct', instruct_results)]:
        af_vals = [res[l]['abelian_frac'] for l in layer_indices]
        corr, p = stats.pearsonr(layer_indices, af_vals)
        print(f"  {label}: AF vs depth r={corr:+.4f}, p={p:.4f}")

    # Save results
    output = {
        'base': {str(k): v for k, v in base_results.items()},
        'instruct': {str(k): v for k, v in instruct_results.items()},
        'config': {
            'n_heads': n_heads, 'd_model': d_model, 'n_layers': n_layers,
            'd_head': d_head, 'proj_dim': PROJ_DIM, 'af_threshold': AF_THRESHOLD,
        },
        'summary': {
            'af_base': af_base, 'af_instruct': af_inst, 'af_diff': af_diff,
            'cv_base': cv_base, 'cv_instruct': cv_inst, 'cv_ratio': cv_ratio,
            'sp_base': sp_base, 'sp_instruct': sp_inst,
        }
    }

    with open('p26_results.json', 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to p26_results.json")
    print(f"\nDone.")
