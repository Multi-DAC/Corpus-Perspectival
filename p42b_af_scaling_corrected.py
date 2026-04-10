"""
P42b: AF Scaling Law — CORRECTED (Adaptive Projection Dimension)
================================================================

P42 had a methodological artifact: PROJ_DIM=64 was designed for d_head=64.
For models with d_head > 64, the projection loses information and artificially
suppresses commutator structure.

Fix: use PROJ_DIM = d_head for each model. This preserves full rank.

Author: Clawd
Date: April 10, 2026
"""

import numpy as np
from scipy import stats
import json, time

SEED = 71
AF_THRESHOLD = 0.10

MODELS = [
    ('EleutherAI/pythia-70m-deduped', '70m'),
    ('EleutherAI/pythia-160m-deduped', '160m'),
    ('EleutherAI/pythia-410m-deduped', '410m'),
    ('EleutherAI/pythia-1b-deduped', '1b'),
    ('EleutherAI/pythia-1.4b-deduped', '1.4b'),
    ('EleutherAI/pythia-2.8b-deduped', '2.8b'),
]


def extract_q_heads_pythia(model_name):
    from transformers import AutoModelForCausalLM, AutoConfig
    import torch

    config = AutoConfig.from_pretrained(model_name)
    n_heads = config.num_attention_heads
    d_model = config.hidden_size
    n_layers = config.num_hidden_layers
    d_head = d_model // n_heads

    model = AutoModelForCausalLM.from_pretrained(model_name, dtype=torch.float32)

    layer_heads = {}
    for layer_idx in range(n_layers):
        key = f"gpt_neox.layers.{layer_idx}.attention.query_key_value.weight"
        for name, param in model.named_parameters():
            if name == key:
                W_QKV = param.detach().cpu().numpy()
                heads = []
                for h in range(n_heads):
                    offset = h * 3 * d_head
                    heads.append(W_QKV[offset:offset + d_head, :])
                layer_heads[layer_idx] = heads
                break

    del model
    import gc; gc.collect()
    return layer_heads, n_heads, d_model, n_layers, d_head


def compute_af_adaptive(layer_heads, n_heads, d_model, d_head):
    """Compute AF with PROJ_DIM = d_head (full rank preservation)."""
    proj_dim = d_head  # KEY CHANGE: match projection to head dimension

    np.random.seed(SEED)
    p_out = np.random.randn(proj_dim, d_head) / np.sqrt(d_head)
    p_in = np.random.randn(d_model, proj_dim) / np.sqrt(d_model)

    layer_afs = []
    layer_cvs = []

    for layer_idx in sorted(layer_heads.keys()):
        heads = layer_heads[layer_idx]
        proj_heads = [p_out @ A @ p_in for A in heads]
        n_h = len(proj_heads)

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
        kn = killing / max_k if max_k > 0 else killing
        evs = np.sort(np.abs(np.linalg.eigvalsh(kn)))
        af = int(np.sum(evs < AF_THRESHOLD)) / n_h
        layer_afs.append(af)

        # CommVar
        comm_norms = np.zeros((n_h, n_h))
        for h in range(n_h):
            for hp in range(h+1, n_h):
                comm = proj_heads[h] @ proj_heads[hp] - proj_heads[hp] @ proj_heads[h]
                comm_norms[h, hp] = np.linalg.norm(comm, 'fro')
                comm_norms[hp, h] = comm_norms[h, hp]
        typical = np.mean([np.linalg.norm(A, 'fro') for A in proj_heads])
        if typical > 0:
            comm_norms /= typical ** 2
        mask = np.ones_like(comm_norms, dtype=bool)
        np.fill_diagonal(mask, False)
        layer_cvs.append(float(np.var(comm_norms[mask])))

    return {
        'mean_af': float(np.mean(layer_afs)),
        'mean_cv': float(np.mean(layer_cvs)),
        'layer_afs': layer_afs,
        'proj_dim_used': proj_dim,
    }


if __name__ == '__main__':
    print("P42b: AF Scaling Law — CORRECTED (Adaptive Projection)")
    print("Fix: PROJ_DIM = d_head (full rank for each model)")
    print("=" * 70)

    all_data = {}
    for model_name, label in MODELS:
        t0 = time.time()
        print(f"\n{label}:", end=' ', flush=True)
        layer_heads, n_heads, d_model, n_layers, d_head = extract_q_heads_pythia(model_name)
        print(f"{n_heads}h, {n_layers}L, d_head={d_head}", end=' ', flush=True)
        load_time = time.time() - t0

        t1 = time.time()
        metrics = compute_af_adaptive(layer_heads, n_heads, d_model, d_head)
        comp_time = time.time() - t1

        print(f"→ AF={metrics['mean_af']:.4f}, CV={metrics['mean_cv']:.6f} "
              f"[load={load_time:.0f}s, compute={comp_time:.0f}s]")

        all_data[label] = {
            'n_heads': n_heads, 'n_layers': n_layers,
            'd_model': d_model, 'd_head': d_head,
            **metrics,
        }
        del layer_heads

    # ============================================================
    # RESULTS
    # ============================================================
    print(f"\n{'='*70}")
    print("CORRECTED AF vs HEAD COUNT")
    print(f"{'='*70}\n")

    items = sorted(all_data.items(), key=lambda x: x[1]['n_heads'])
    print(f"{'Model':<8} {'Heads':>5} {'d_head':>6} {'Layers':>6} {'AF':>8} {'CV':>12} {'proj_dim':>8}")
    print("-" * 58)
    for label, d in items:
        print(f"{label:<8} {d['n_heads']:>5} {d['d_head']:>6} {d['n_layers']:>6} "
              f"{d['mean_af']:>8.4f} {d['mean_cv']:>12.6f} {d['proj_dim_used']:>8}")

    # ============================================================
    # SCALING ANALYSIS
    # ============================================================
    heads = np.array([d['n_heads'] for _, d in items])
    afs = np.array([d['mean_af'] for _, d in items])
    d_heads = np.array([d['d_head'] for _, d in items])
    n_layers_arr = np.array([d['n_layers'] for _, d in items])

    print(f"\n{'='*70}")
    print("CORRELATION ANALYSIS")
    print(f"{'='*70}\n")

    # AF vs various predictors
    for name, var in [('n_heads', heads), ('d_head', d_heads),
                       ('n_layers', n_layers_arr), ('n_heads/d_head', heads/d_heads),
                       ('n_heads*n_layers', heads*n_layers_arr)]:
        mask = afs > 0
        if np.sum(mask) >= 3:
            r, p = stats.spearmanr(var[mask], afs[mask])
            print(f"  AF vs {name:<16}: r={r:+.3f}, p={p:.4f}")
        r_all, p_all = stats.spearmanr(var, afs)
        print(f"  AF vs {name:<16} (all): r={r_all:+.3f}, p={p_all:.4f}")

    # P42-A re-evaluation
    print(f"\n{'='*70}")
    print("PREDICTION RE-EVALUATION (corrected)")
    print(f"{'='*70}\n")

    af_1b = all_data['1b']['mean_af']
    af_160m = all_data['160m']['mean_af']
    print(f"P42-A: AF(1b, 8h, d_head=256) vs AF(160m, 12h, d_head=64)")
    print(f"  AF(1b) = {af_1b:.4f}, AF(160m) = {af_160m:.4f}")
    print(f"  {'CONFIRMED' if af_1b < af_160m else 'FALSIFIED'}")

    af_14b = all_data['1.4b']['mean_af']
    af_410m = all_data['410m']['mean_af']
    ratio = af_14b / af_410m if af_410m > 0 else float('inf')
    print(f"\nP42-B: AF(1.4b, 16h, d_head=128) vs AF(410m, 16h, d_head=64)")
    print(f"  AF(1.4b) = {af_14b:.4f}, AF(410m) = {af_410m:.4f}, ratio = {ratio:.3f}")
    print(f"  {'CONFIRMED (within 30%)' if 0.7 < ratio < 1.3 else 'FALSIFIED'}")

    af_70m = all_data['70m']['mean_af']
    print(f"\nSize-matched (8 heads): 70m AF={af_70m:.4f}, 1b AF={af_1b:.4f}")
    print(f"Size-matched (16 heads): 410m AF={af_410m:.4f}, 1.4b AF={af_14b:.4f}")

    with open('p42b_corrected_results.json', 'w') as f:
        json.dump(all_data, f, indent=2)
    print(f"\nResults saved to p42b_corrected_results.json")
