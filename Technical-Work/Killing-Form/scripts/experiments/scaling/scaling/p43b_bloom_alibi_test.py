"""
P43b: BLOOM-560m — ALiBi Hypothesis Test
=========================================

Falcon-RW-1B (sequential + ALiBi) had random-level CommVar (0.000025).
OPT-1.3B (sequential + learned pos) had CommVar = 0.002498.
GPT-2-medium (sequential + learned pos) had CommVar = 0.001876.

Hypothesis: ALiBi positional encoding suppresses Q-projection Killing form
structure because position information goes into a bias, not into Q/K weights.
Without position-dependent Q specialization, heads have less reason to
differentiate, producing flat commutator algebra.

BLOOM-560m: 16 heads, d_model=1024, d_head=64, 24 layers, sequential + ALiBi.

Predictions:
  P43b-A: CommVar < 0.0005 (ALiBi → near-zero, like Falcon-RW)
  P43b-B: CommVar << GPT-2-medium (0.0019) at matched architecture

Author: Clawd
Date: April 10, 2026
"""

import numpy as np
from scipy import stats
import json, time

PROJ_DIM = 64
SEED = 71
AF_THRESHOLD = 0.10
MODEL = 'bigscience/bloom-560m'


def extract_q_heads_bloom(model_name):
    """Extract per-head Q projection matrices from BLOOM."""
    from transformers import AutoModelForCausalLM, AutoConfig
    import torch

    config = AutoConfig.from_pretrained(model_name)
    n_heads = config.n_head
    d_model = config.hidden_size
    n_layers = config.n_layer
    d_head = d_model // n_heads

    print(f"  Config: {n_heads} heads, d={d_model}, d_head={d_head}, {n_layers} layers")
    print(f"  Loading model...")
    model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float32)

    layer_heads = {}
    for layer_idx in range(n_layers):
        for name, param in model.named_parameters():
            if f'h.{layer_idx}.self_attention.query_key_value.weight' in name:
                W_QKV = param.detach().cpu().numpy()  # (3*d_model, d_model)
                # BLOOM uses contiguous [Q; K; V] layout
                W_Q = W_QKV[:d_model, :]  # (d_model, d_model)

                heads = []
                for h in range(n_heads):
                    W_Q_h = W_Q[h*d_head:(h+1)*d_head, :]  # (d_head, d_model)
                    heads.append(W_Q_h)

                layer_heads[layer_idx] = heads
                break

    del model
    import gc; gc.collect()
    return layer_heads, n_heads, d_model, n_layers, d_head


def compute_metrics(layer_heads, n_heads, d_model, d_head):
    np.random.seed(SEED)
    p_out = np.random.randn(PROJ_DIM, d_head) / np.sqrt(d_head)
    p_in = np.random.randn(d_model, PROJ_DIM) / np.sqrt(d_model)

    layer_afs = []
    layer_cvs = []

    for layer_idx in sorted(layer_heads.keys()):
        heads = layer_heads[layer_idx]
        proj = [p_out @ A @ p_in for A in heads]
        n_h = len(proj)

        killing = np.zeros((n_h, n_h))
        for h in range(n_h):
            for hp in range(n_h):
                val = 0
                for k in range(n_h):
                    c1 = proj[h] @ proj[k] - proj[k] @ proj[h]
                    c2 = proj[hp] @ proj[k] - proj[k] @ proj[hp]
                    val += np.trace(c1.T @ c2)
                killing[h, hp] = val
        mx = np.max(np.abs(killing))
        kn = killing / mx if mx > 0 else killing
        evs = np.sort(np.abs(np.linalg.eigvalsh(kn)))
        af = int(np.sum(evs < AF_THRESHOLD)) / n_h
        layer_afs.append(af)

        norms = np.zeros((n_h, n_h))
        for h in range(n_h):
            for hp in range(h+1, n_h):
                c = proj[h] @ proj[hp] - proj[hp] @ proj[h]
                norms[h, hp] = np.linalg.norm(c, 'fro')
                norms[hp, h] = norms[h, hp]
        typ = np.mean([np.linalg.norm(A, 'fro') for A in proj])
        if typ > 0:
            norms /= typ ** 2
        mask = np.ones_like(norms, dtype=bool)
        np.fill_diagonal(mask, False)
        layer_cvs.append(float(np.var(norms[mask])))

        if (layer_idx + 1) % 6 == 0:
            print(f"  L{layer_idx}: AF={af:.3f}, CV={layer_cvs[-1]:.6f}")

    r_cv, p_cv = stats.spearmanr(range(len(layer_cvs)), layer_cvs)

    return {
        'mean_af': float(np.mean(layer_afs)),
        'mean_cv': float(np.mean(layer_cvs)),
        'r_cv_depth': float(r_cv) if not np.isnan(r_cv) else 0.0,
        'p_cv_depth': float(p_cv) if not np.isnan(p_cv) else 1.0,
        'layer_afs': layer_afs,
        'layer_cvs': layer_cvs,
    }


if __name__ == '__main__':
    print("P43b: BLOOM-560m — ALiBi Hypothesis Test")
    print("=" * 70)

    t0 = time.time()
    layer_heads, n_heads, d_model, n_layers, d_head = extract_q_heads_bloom(MODEL)
    print(f"  Loaded in {time.time()-t0:.0f}s")

    t1 = time.time()
    metrics = compute_metrics(layer_heads, n_heads, d_model, d_head)
    print(f"  Computed in {time.time()-t1:.0f}s")

    print(f"\n{'='*70}")
    print("RESULTS")
    print(f"{'='*70}\n")

    print(f"BLOOM-560m: AF={metrics['mean_af']:.4f}, CV={metrics['mean_cv']:.6f}")
    print(f"Depth correlation: r={metrics['r_cv_depth']:+.3f}, p={metrics['p_cv_depth']:.4f}")

    print(f"\n{'='*70}")
    print("ALiBi COMPARISON (all sequential, d_head=64)")
    print(f"{'='*70}\n")

    comparisons = [
        ('GPT2-medium', 'learned pos', 16, 24, 0.001876, -0.930),
        ('OPT-1.3B', 'learned pos', 32, 24, 0.002498, -0.766),
        ('TinyLlama-1.1B', 'rotary (RoPE)', 32, 22, 0.002038, -0.485),
        ('BLOOM-560m', 'ALiBi', 16, 24, metrics['mean_cv'], metrics['r_cv_depth']),
        ('Falcon-RW-1B', 'ALiBi', 32, 24, 0.000025, -0.182),
    ]

    print(f"{'Model':<18} {'Pos. Enc.':<14} {'H':>3} {'L':>3} {'CV':>10} {'r(depth)':>10}")
    print("-" * 64)
    for name, pos, heads, layers, cv, r in comparisons:
        print(f"{name:<18} {pos:<14} {heads:>3} {layers:>3} {cv:>10.6f} {r:>+10.3f}")

    print(f"\n{'='*70}")
    print("PREDICTION EVALUATION")
    print(f"{'='*70}\n")

    cv = metrics['mean_cv']
    print(f"P43b-A: CommVar < 0.0005 (ALiBi → near-zero)")
    print(f"  CV = {cv:.6f}")
    print(f"  {'**CONFIRMED**' if cv < 0.0005 else '**FALSIFIED**'}")

    print(f"\nP43b-B: CommVar << GPT2-medium (0.0019)")
    print(f"  CV = {cv:.6f}, GPT2-md = 0.001876")
    ratio = cv / 0.001876
    print(f"  Ratio: {ratio:.2f}")
    print(f"  {'**CONFIRMED** (>3x reduction)' if ratio < 0.33 else '**PARTIALLY** (some reduction)' if ratio < 0.75 else '**FALSIFIED**'}")

    if cv < 0.001:
        print(f"\n→ ALiBi hypothesis SUPPORTED: both ALiBi models (Falcon-RW, BLOOM)")
        print(f"  have suppressed Q-projection Killing form structure.")
        print(f"  Mechanism: ALiBi puts position into bias, not Q/K weights.")
        print(f"  Without position-dependent Q specialization, heads stay similar.")
    elif cv > 0.001:
        print(f"\n→ ALiBi hypothesis FALSIFIED: BLOOM has normal CommVar.")
        print(f"  Falcon-RW near-zero CommVar must have another explanation.")

    with open('p43b_bloom_results.json', 'w') as f:
        json.dump({
            'model': MODEL,
            'n_heads': n_heads, 'd_model': d_model,
            'd_head': d_head, 'n_layers': n_layers,
            'positional_encoding': 'ALiBi',
            **metrics,
        }, f, indent=2)
    print(f"\nResults saved to p43b_bloom_results.json")
