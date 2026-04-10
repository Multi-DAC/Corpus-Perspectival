"""
P42f: OPT-1.3B Architecture Test — Sequential + Dense (Third Family)
====================================================================

OPT (Meta) uses sequential attention+MLP like GPT-2.
Tests the revised hypothesis: sequential → negative depth gradient.
Third independent sequential family after GPT-2 (OpenAI) and Llama (TinyLlama).

OPT-1.3B: 32 Q heads, 32 KV heads (dense), d_head=64, 24 layers, d_model=2048

Predictions:
  P42f-A: Depth gradient r < -0.3 (sequential → negative)
  P42f-B: AF < 0.05 (sequential → low AF, though this is now secondary)

Author: Clawd
Date: April 10, 2026
"""

import numpy as np
from scipy import stats
import json, time

PROJ_DIM = 64
SEED = 71
AF_THRESHOLD = 0.10
MODEL = 'facebook/opt-1.3b'


def extract_q_heads_opt(model_name):
    """Extract per-head Q projection matrices from OPT."""
    from transformers import AutoModelForCausalLM, AutoConfig
    import torch

    config = AutoConfig.from_pretrained(model_name)
    n_heads = config.num_attention_heads       # 32
    d_model = config.hidden_size               # 2048
    n_layers = config.num_hidden_layers        # 24
    d_head = d_model // n_heads                # 64

    print(f"  Config: {n_heads} heads, d={d_model}, d_head={d_head}, {n_layers} layers")
    print(f"  Loading model...")
    model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float32)

    layer_heads = {}
    for layer_idx in range(n_layers):
        W_Q = None
        for name, param in model.named_parameters():
            if f'layers.{layer_idx}.self_attn.q_proj.weight' in name:
                W_Q = param.detach().cpu().numpy()  # (d_model, d_model) = (2048, 2048)
                break

        if W_Q is None:
            print(f"  WARNING: Q weights not found for layer {layer_idx}")
            if layer_idx == 0:
                for name, _ in model.named_parameters():
                    if f'layers.{layer_idx}.' in name:
                        print(f"    {name}")
            continue

        # OPT q_proj.weight: (d_model, d_model), rows are output, cols are input
        # Split into per-head: rows [h*d_head:(h+1)*d_head]
        heads = []
        for h in range(n_heads):
            W_Q_h = W_Q[h*d_head:(h+1)*d_head, :]  # (64, 2048)
            heads.append(W_Q_h)

        layer_heads[layer_idx] = heads

    del model
    import gc; gc.collect()
    return layer_heads, n_heads, d_model, n_layers, d_head


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
    print("P42f: OPT-1.3B — Sequential + Dense (Third Family)")
    print("=" * 70)

    t0 = time.time()
    layer_heads, n_heads, d_model, n_layers, d_head = extract_q_heads_opt(MODEL)
    print(f"  Loaded in {time.time()-t0:.0f}s")

    t1 = time.time()
    metrics = compute_af(layer_heads, n_heads, d_model, d_head)
    print(f"  Computed in {time.time()-t1:.0f}s")

    print(f"\n{'='*70}")
    print("RESULTS")
    print(f"{'='*70}\n")

    print(f"OPT-1.3B: AF={metrics['mean_af']:.4f}, CV={metrics['mean_cv']:.6f}")
    print(f"Depth correlation: r={metrics['r_cv_depth']:+.3f}, p={metrics['p_cv_depth']:.4f}")

    print(f"\n{'='*70}")
    print("DEFINITIVE CROSS-ARCHITECTURE TABLE (all d_head=64)")
    print(f"{'='*70}\n")

    comparisons = [
        ('Pythia-410m', 'parallel', 'EleutherAI', 'dense', 16, 16, 0.2057, +0.670),
        ('Pythia-160m', 'parallel', 'EleutherAI', 'dense', 12, 12, 0.0903, +0.119),
        ('Pythia-70m', 'parallel', 'EleutherAI', 'dense', 8, 6, 0.0833, -0.600),
        ('Phi-1.5', 'parallel', 'Microsoft', 'dense', 32, 24, 0.0000, +0.343),
        ('GPT2-sm', 'sequential', 'OpenAI', 'dense', 12, 12, 0.0278, -0.909),
        ('GPT2-md', 'sequential', 'OpenAI', 'dense', 16, 24, 0.0104, -0.930),
        ('GPT2-lg', 'sequential', 'OpenAI', 'dense', 20, 36, 0.0000, -0.741),
        ('GPT2-xl', 'sequential', 'OpenAI', 'dense', 25, 48, 0.0000, -0.801),
        ('TinyLlama-1.1B', 'sequential', 'TinyLlama', 'GQA', 32, 22, 0.0256, -0.485),
        ('OPT-1.3B', 'sequential', 'Meta', 'dense', 32, 24, metrics['mean_af'], metrics['r_cv_depth']),
    ]

    print(f"{'Model':<16} {'Arch':<12} {'Lab':<12} {'Attn':<6} {'H':>3} {'L':>3} {'AF':>8} {'r(depth)':>10}")
    print("-" * 78)
    for name, arch, lab, attn, heads, layers, af, r_dep in comparisons:
        print(f"{name:<16} {arch:<12} {lab:<12} {attn:<6} {heads:>3} {layers:>3} {af:>8.4f} {r_dep:>+10.3f}")

    # Depth gradient summary
    print(f"\n{'='*70}")
    print("DEPTH GRADIENT DIRECTION — THE ARCHITECTURAL INVARIANT")
    print(f"{'='*70}\n")

    parallel_rs = [+0.670, +0.119, +0.343]  # excluding Pythia-70m (6 layers)
    sequential_rs = [-0.909, -0.930, -0.741, -0.801, -0.485, metrics['r_cv_depth']]

    print(f"Parallel (n=3, excl. Pythia-70m w/ 6 layers):")
    print(f"  r values: {[f'{r:+.3f}' for r in parallel_rs]}")
    print(f"  Mean: {np.mean(parallel_rs):+.3f}")
    print(f"  All positive: {'YES' if all(r > 0 for r in parallel_rs) else 'NO'}")

    print(f"\nSequential (n=6):")
    print(f"  r values: {[f'{r:+.3f}' for r in sequential_rs]}")
    print(f"  Mean: {np.mean(sequential_rs):+.3f}")
    print(f"  All negative: {'YES' if all(r < 0 for r in sequential_rs) else 'NO'}")

    # Statistical test
    from scipy.stats import mannwhitneyu
    U, p_mw = mannwhitneyu(parallel_rs, sequential_rs, alternative='greater')
    print(f"\n  Mann-Whitney U test (parallel > sequential): U={U}, p={p_mw:.4f}")

    print(f"\n{'='*70}")
    print("PREDICTION EVALUATION")
    print(f"{'='*70}\n")

    r = metrics['r_cv_depth']
    af = metrics['mean_af']

    print(f"P42f-A: Depth gradient r < -0.3 (sequential → negative)")
    print(f"  r = {r:+.3f}")
    print(f"  {'**CONFIRMED**' if r < -0.3 else '**FALSIFIED**'}")

    print(f"\nP42f-B: AF < 0.05 (sequential → low)")
    print(f"  AF = {af:.4f}")
    print(f"  {'**CONFIRMED**' if af < 0.05 else '**FALSIFIED**'}")

    with open('p42f_opt_results.json', 'w') as f:
        json.dump({
            'model': MODEL,
            'n_heads': n_heads,
            'd_model': d_model, 'd_head': d_head, 'n_layers': n_layers,
            **metrics,
        }, f, indent=2)
    print(f"\nResults saved to p42f_opt_results.json")
