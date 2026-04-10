"""
P42d: Llama Architecture Test — Sequential + GQA
=================================================

Llama-style uses sequential attention+MLP (like GPT-2) plus GQA.
If the parallel/sequential hypothesis holds:
  - Llama should show LOW AF (like GPT-2, not like Pythia)
  - GQA grouping may push AF even lower (forced within-group coupling)

TinyLlama-1.1B-Chat-v1.0: 32 Q heads, 4 KV heads, d_head=64, 22 layers, d_model=2048
(Llama-3.2-1B is gated; TinyLlama has identical architecture class)

Predictions:
  P42d-A: AF < 0.05 (sequential → low AF)
  P42d-B: AF < GPT-2-medium (0.010) because GQA adds coupling

Author: Clawd
Date: April 10, 2026
"""

import numpy as np
from scipy import stats
import json, time

PROJ_DIM = 64  # = d_head
SEED = 71
AF_THRESHOLD = 0.10
MODEL = 'TinyLlama/TinyLlama-1.1B-Chat-v1.0'


def extract_q_heads_llama(model_name):
    """Extract per-head Q projection matrices from Llama."""
    from transformers import AutoModelForCausalLM, AutoConfig
    import torch

    config = AutoConfig.from_pretrained(model_name)
    n_heads = config.num_attention_heads       # 32
    n_kv_heads = config.num_key_value_heads    # 8
    d_model = config.hidden_size               # 2048
    n_layers = config.num_hidden_layers        # 16
    d_head = d_model // n_heads                # 64

    print(f"  Config: {n_heads} Q heads, {n_kv_heads} KV heads, d={d_model}, d_head={d_head}, {n_layers} layers")
    print(f"  GQA ratio: {n_heads // n_kv_heads}:1")
    print(f"  Loading model...")
    model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float32)

    layer_heads = {}
    for layer_idx in range(n_layers):
        key = f"model.layers.{layer_idx}.self_attn.q_proj.weight"
        W_Q = None
        for name, param in model.named_parameters():
            if name == key:
                W_Q = param.detach().cpu().numpy()  # (n_heads*d_head, d_model) = (2048, 2048)
                break

        if W_Q is None:
            print(f"  WARNING: {key} not found")
            continue

        # Split into per-head Q: each head h gets rows [h*d_head:(h+1)*d_head]
        heads = []
        for h in range(n_heads):
            W_Q_h = W_Q[h*d_head:(h+1)*d_head, :]  # (64, 2048)
            heads.append(W_Q_h)

        layer_heads[layer_idx] = heads

    del model
    import gc; gc.collect()
    return layer_heads, n_heads, n_kv_heads, d_model, n_layers, d_head


def compute_af(layer_heads, n_heads, d_model, d_head):
    np.random.seed(SEED)
    p_out = np.random.randn(PROJ_DIM, d_head) / np.sqrt(d_head)
    p_in = np.random.randn(d_model, PROJ_DIM) / np.sqrt(d_model)

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

        if (layer_idx + 1) % 4 == 0:
            print(f"  L{layer_idx}: AF={af:.3f}, CV={layer_cvs[-1]:.6f}")

    layers = list(range(len(layer_afs)))
    r_cv, p_cv = stats.spearmanr(layers, layer_cvs)

    return {
        'mean_af': float(np.mean(layer_afs)),
        'mean_cv': float(np.mean(layer_cvs)),
        'r_cv_depth': float(r_cv) if not np.isnan(r_cv) else 0.0,
        'p_cv_depth': float(p_cv) if not np.isnan(p_cv) else 1.0,
        'layer_afs': layer_afs,
        'layer_cvs': layer_cvs,
    }


if __name__ == '__main__':
    print("P42d: TinyLlama-1.1B — Sequential + GQA Test")
    print("=" * 70)

    t0 = time.time()
    layer_heads, n_heads, n_kv_heads, d_model, n_layers, d_head = extract_q_heads_llama(MODEL)
    print(f"  Loaded in {time.time()-t0:.0f}s")

    t1 = time.time()
    metrics = compute_af(layer_heads, n_heads, d_model, d_head)
    print(f"  Computed in {time.time()-t1:.0f}s")

    # Results
    print(f"\n{'='*70}")
    print("RESULTS")
    print(f"{'='*70}\n")

    print(f"TinyLlama-1.1B: AF={metrics['mean_af']:.4f}, CV={metrics['mean_cv']:.6f}")
    print(f"Depth correlation: r={metrics['r_cv_depth']:+.3f}, p={metrics['p_cv_depth']:.4f}")

    # Comparison table
    print(f"\n{'='*70}")
    print("CROSS-ARCHITECTURE COMPARISON (all d_head=64)")
    print(f"{'='*70}\n")

    comparisons = [
        ('Pythia-410m', 'parallel', 'dense', 16, 0.2057, 0.670),
        ('Pythia-160m', 'parallel', 'dense', 12, 0.0903, 0.119),
        ('Pythia-70m', 'parallel', 'dense', 8, 0.0833, -0.600),
        ('GPT2-sm', 'sequential', 'dense', 12, 0.0278, -0.909),
        ('GPT2-md', 'sequential', 'dense', 16, 0.0104, -0.930),
        ('GPT2-lg', 'sequential', 'dense', 20, 0.0000, -0.741),
        ('GPT2-xl', 'sequential', 'dense', 25, 0.0000, -0.801),
        ('TinyLlama-1.1B', 'sequential', 'GQA', 32, metrics['mean_af'], metrics['r_cv_depth']),
    ]

    print(f"{'Model':<14} {'Arch':<12} {'Attn':<6} {'Heads':>5} {'AF':>8} {'r(depth)':>10}")
    print("-" * 60)
    for name, arch, attn, heads, af, r_dep in comparisons:
        print(f"{name:<14} {arch:<12} {attn:<6} {heads:>5} {af:>8.4f} {r_dep:>+10.3f}")

    # Prediction evaluation
    print(f"\n{'='*70}")
    print("PREDICTION EVALUATION")
    print(f"{'='*70}\n")

    af = metrics['mean_af']
    print(f"P42d-A: AF < 0.05 (sequential → low)")
    print(f"  AF = {af:.4f}")
    print(f"  {'**CONFIRMED**' if af < 0.05 else '**FALSIFIED**'}")

    print(f"\nP42d-B: AF < GPT2-medium (0.010) (GQA adds coupling)")
    print(f"  AF = {af:.4f}, GPT2-md = 0.0104")
    print(f"  {'**CONFIRMED**' if af < 0.0104 else '**FALSIFIED**'}")

    # GQA group analysis
    print(f"\n{'='*70}")
    print("GQA GROUP ANALYSIS")
    print(f"{'='*70}")
    print(f"\nTinyLlama has {n_heads} Q heads in {n_kv_heads} groups of {n_heads//n_kv_heads}")
    print(f"Within-group heads SHARE K/V — forced to attend to same information")
    print(f"This should create non-Abelian coupling WITHIN groups")

    # Check if within-group commutators are larger than between-group
    # (would need per-layer head-pair analysis — log this for future work)

    with open('p42d_llama_results.json', 'w') as f:
        json.dump({
            'model': MODEL,
            'n_heads': n_heads, 'n_kv_heads': n_kv_heads,
            'd_model': d_model, 'd_head': d_head, 'n_layers': n_layers,
            **metrics,
        }, f, indent=2)
    print(f"\nResults saved to p42d_llama_results.json")
