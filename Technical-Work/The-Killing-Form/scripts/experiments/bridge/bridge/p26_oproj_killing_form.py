"""
P26 Extension: O-Projection Killing Form — Base vs Instruct
============================================================

P26 showed Q-projection Killing form is identical between base/instruct.
P26 follow-up showed O-proj changes 2x more than Q-proj under RLHF.

This script computes the Killing form using O-projection matrices instead
of Q-projections. If RLHF sedimentation operates on the output manifold,
the O-projection Killing form should differ between base and instruct.

Qwen2.5-1.5B O-projection: (d_model, d_model) = (1536, 1536)
Split into 12 heads: each maps from d_head=128 to d_model=1536
O_proj[h] = O[:, h*d_head:(h+1)*d_head]  shape: (1536, 128)

Author: Clawd
Date: April 10, 2026
"""

import numpy as np
from scipy import stats
import json, time

PROJ_DIM = 64
SEED = 71
AF_THRESHOLD = 0.10

def extract_o_heads(model_name):
    """Extract per-head O projection matrices."""
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
        key = f"model.layers.{layer_idx}.self_attn.o_proj.weight"
        W_O = None
        for name, param in model.named_parameters():
            if name == key:
                W_O = param.detach().cpu().numpy()  # (1536, 1536)
                break

        if W_O is None:
            print(f"  WARNING: {key} not found")
            continue

        # O-projection maps concatenated head outputs back to residual stream
        # Shape: (d_model, d_model) = (1536, 1536)
        # Each head h contributes columns [h*d_head : (h+1)*d_head]
        # So O_h = W_O[:, h*d_head:(h+1)*d_head] has shape (1536, 128)
        heads = []
        for h in range(n_heads):
            O_h = W_O[:, h*d_head:(h+1)*d_head]  # (1536, 128)
            heads.append(O_h)

        layer_heads[layer_idx] = heads

    del model
    import gc; gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    return layer_heads, n_heads, d_model, n_layers, d_head


def compute_killing_form(heads, proj):
    """Compute Killing form from a list of head matrices."""
    n_h = len(heads)
    p_out, p_in = proj

    # heads are (1536, 128) for O-proj
    # Project: p_out (PROJ_DIM, 1536) @ A (1536, 128) @ p_in (128, PROJ_DIM)
    proj_heads = [p_out @ A @ p_in for A in heads]  # each (PROJ_DIM, PROJ_DIM)

    # Commutator norms
    comm_norms = np.zeros((n_h, n_h))
    for h in range(n_h):
        for hp in range(h+1, n_h):
            comm = proj_heads[h] @ proj_heads[hp] - proj_heads[hp] @ proj_heads[h]
            norm = np.linalg.norm(comm, 'fro')
            comm_norms[h, hp] = norm
            comm_norms[hp, h] = norm

    typical = np.mean([np.linalg.norm(A, 'fro') for A in proj_heads])
    comm_normalized = comm_norms / (typical ** 2) if typical > 0 else comm_norms

    # Killing form
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
    eigenvalues = np.sort(np.abs(np.linalg.eigvalsh(killing_norm)))

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
    """Full O-projection analysis for one model."""
    print(f"\n{'='*70}")
    print(f"O-PROJ Analysis: {label} ({model_name})")
    print(f"{'='*70}")

    t0 = time.time()
    layer_heads, n_heads, d_model, n_layers, d_head = extract_o_heads(model_name)
    print(f"  Extracted {n_heads} O-heads from {n_layers} layers in {time.time()-t0:.1f}s")

    # Projection matrices — NOTE: dimensions differ from Q-proj
    # O-heads are (d_model, d_head) = (1536, 128)
    # Need: p_out (PROJ_DIM, d_model), p_in (d_head, PROJ_DIM)
    np.random.seed(SEED)
    p_out = np.random.randn(PROJ_DIM, d_model) / np.sqrt(d_model)
    p_in = np.random.randn(d_head, PROJ_DIM) / np.sqrt(d_head)
    proj = (p_out, p_in)

    results = {}
    t1 = time.time()
    for layer_idx in sorted(layer_heads.keys()):
        results[layer_idx] = compute_killing_form(layer_heads[layer_idx], proj)
        if (layer_idx + 1) % 7 == 0:
            elapsed = time.time() - t1
            print(f"  Layer {layer_idx}: AF={results[layer_idx]['abelian_frac']:.3f}, "
                  f"CommVar={results[layer_idx]['comm_var']:.6f} ({elapsed:.1f}s)")

    print(f"  All layers analyzed in {time.time()-t1:.1f}s")
    return results, n_heads


if __name__ == '__main__':
    models = {
        'base': 'Qwen/Qwen2.5-1.5B',
        'instruct': 'Qwen/Qwen2.5-1.5B-Instruct',
    }

    print("P26 Extension: O-Projection Killing Form")
    print("=" * 70)

    base_results, n_heads = analyze_model(models['base'], 'Base')
    inst_results, _ = analyze_model(models['instruct'], 'Instruct')

    # Comparison
    print(f"\n{'='*70}")
    print("O-PROJECTION KILLING FORM: Base vs Instruct")
    print(f"{'='*70}\n")

    layer_indices = sorted(base_results.keys())

    print(f"{'Layer':>5} {'AF_base':>8} {'AF_inst':>8} {'Diff':>8} "
          f"{'CV_base':>10} {'CV_inst':>10} {'CV_ratio':>9}")
    print("-" * 65)

    for l in layer_indices:
        b = base_results[l]
        i = inst_results[l]
        cv_ratio = i['comm_var'] / b['comm_var'] if b['comm_var'] > 0 else float('inf')
        print(f"{l:>5} {b['abelian_frac']:>8.3f} {i['abelian_frac']:>8.3f} "
              f"{i['abelian_frac']-b['abelian_frac']:>+8.3f} "
              f"{b['comm_var']:>10.6f} {i['comm_var']:>10.6f} {cv_ratio:>9.3f}")

    # Global averages
    def avg(results, key):
        return np.mean([results[l][key] for l in results])

    print(f"\n{'Metric':<20} {'Base':>12} {'Instruct':>12} {'Diff':>12}")
    print("-" * 60)
    for k in ['abelian_frac', 'comm_var', 'mean_comm', 'ev_spread']:
        b_val = avg(base_results, k)
        i_val = avg(inst_results, k)
        print(f"{k:<20} {b_val:>12.5f} {i_val:>12.5f} {i_val-b_val:>+12.5f}")

    # Statistical tests
    print(f"\nStatistical tests (paired by layer):")
    for k in ['abelian_frac', 'comm_var', 'ev_spread']:
        b_vals = [base_results[l][k] for l in layer_indices]
        i_vals = [inst_results[l][k] for l in layer_indices]
        t_stat, p_val = stats.ttest_rel(b_vals, i_vals)
        print(f"  {k}: t={t_stat:.3f}, p={p_val:.4f}")

    # Compare with Q-projection results
    print(f"\n{'='*70}")
    print("Q-PROJ vs O-PROJ COMPARISON")
    print(f"{'='*70}")
    print(f"\nQ-proj AF (from P26): base=0.00893, instruct=0.00893, diff=0.0000")
    print(f"O-proj AF: base={avg(base_results, 'abelian_frac'):.5f}, "
          f"instruct={avg(inst_results, 'abelian_frac'):.5f}, "
          f"diff={avg(inst_results, 'abelian_frac') - avg(base_results, 'abelian_frac'):+.5f}")

    # Save
    output = {
        'base': {str(k): v for k, v in base_results.items()},
        'instruct': {str(k): v for k, v in inst_results.items()},
    }
    with open('p26_oproj_results.json', 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to p26_oproj_results.json")
