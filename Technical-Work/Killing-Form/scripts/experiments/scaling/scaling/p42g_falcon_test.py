"""
P42g: Falcon-RW-1B Architecture Test — Parallel + Dense (Third Family)
======================================================================

Falcon-RW-1B (TII/UAE) uses parallel attention+MLP (GPT-NeoX-style).
Third independent parallel architecture after Pythia (EleutherAI) and Phi (Microsoft).

Falcon-RW-1B: 32 heads, dense MHA, d_head=64, 24 layers, d_model=2048

Predictions (revised theory — depth gradient is the invariant):
  P42g-A: Depth gradient r > 0 (parallel → positive)
  P42g-B: AF is unconstrained (Phi showed AF=0 is possible for parallel)

Author: Clawd
Date: April 10, 2026
"""

import numpy as np
from scipy import stats
import json, time

PROJ_DIM = 64
SEED = 71
AF_THRESHOLD = 0.10
MODEL = 'tiiuae/falcon-rw-1b'


def extract_q_heads_falcon(model_name):
    """Extract per-head Q projection matrices from Falcon-RW."""
    from transformers import AutoModelForCausalLM, AutoConfig
    import torch

    config = AutoConfig.from_pretrained(model_name, trust_remote_code=True)
    n_heads = config.num_attention_heads
    d_model = config.hidden_size
    n_layers = config.num_hidden_layers
    d_head = d_model // n_heads
    # Check for multi-query
    multi_query = getattr(config, 'multi_query', False)

    print(f"  Config: {n_heads} heads, d={d_model}, d_head={d_head}, {n_layers} layers")
    print(f"  Multi-query: {multi_query}")
    print(f"  Loading model...")

    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=torch.float32, trust_remote_code=True
    )

    layer_heads = {}
    for layer_idx in range(n_layers):
        W_Q = None

        # Try separate q_proj first
        for name, param in model.named_parameters():
            if f'.{layer_idx}.' in name and 'q_proj' in name and 'weight' in name:
                W_Q = param.detach().cpu().numpy()
                break

        if W_Q is None:
            # Try fused query_key_value
            for name, param in model.named_parameters():
                if f'.{layer_idx}.' in name and 'query_key_value' in name and 'weight' in name:
                    W_QKV = param.detach().cpu().numpy()
                    if multi_query:
                        # MQA: first d_model rows are Q, next d_head are K, next d_head are V
                        W_Q = W_QKV[:d_model, :]
                    else:
                        # Dense MHA: first d_model rows are Q
                        W_Q = W_QKV[:d_model, :]
                    break

        if W_Q is None:
            # Try dense_h_to_4h style or other naming
            for name, param in model.named_parameters():
                if f'.{layer_idx}.' in name and ('attn' in name.lower() or 'attention' in name.lower()):
                    if 'weight' in name and ('query' in name.lower() or 'qkv' in name.lower()):
                        W_Q = param.detach().cpu().numpy()[:d_model, :]
                        break

        if W_Q is None:
            if layer_idx == 0:
                print(f"  WARNING: Q weights not found for layer {layer_idx}")
                print("  Available params:")
                for name, param in model.named_parameters():
                    if f'.{layer_idx}.' in name:
                        print(f"    {name}: {param.shape}")
            continue

        # Split Q into per-head
        heads = []
        for h in range(n_heads):
            W_Q_h = W_Q[h*d_head:(h+1)*d_head, :]
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
    print("P42g: Falcon-RW-1B — Parallel + Dense (Third Parallel Family)")
    print("=" * 70)

    t0 = time.time()
    layer_heads, n_heads, d_model, n_layers, d_head = extract_q_heads_falcon(MODEL)
    print(f"  Loaded in {time.time()-t0:.0f}s")

    if not layer_heads:
        print("ERROR: No heads extracted. Check parameter naming.")
        exit(1)

    t1 = time.time()
    metrics = compute_af(layer_heads, n_heads, d_model, d_head)
    print(f"  Computed in {time.time()-t1:.0f}s")

    print(f"\n{'='*70}")
    print("RESULTS")
    print(f"{'='*70}\n")

    print(f"Falcon-RW-1B: AF={metrics['mean_af']:.4f}, CV={metrics['mean_cv']:.6f}")
    print(f"Depth correlation: r={metrics['r_cv_depth']:+.3f}, p={metrics['p_cv_depth']:.4f}")

    print(f"\n{'='*70}")
    print("DEFINITIVE CROSS-ARCHITECTURE TABLE (all d_head=64)")
    print(f"{'='*70}\n")

    comparisons = [
        ('Pythia-410m', 'parallel', 'EleutherAI', 'dense', 16, 16, 0.2057, +0.670),
        ('Pythia-160m', 'parallel', 'EleutherAI', 'dense', 12, 12, 0.0903, +0.119),
        ('Phi-1.5', 'parallel', 'Microsoft', 'dense', 32, 24, 0.0000, +0.343),
        ('Falcon-RW-1B', 'parallel', 'TII/UAE', 'dense', 32, 24, metrics['mean_af'], metrics['r_cv_depth']),
        ('GPT2-sm', 'sequential', 'OpenAI', 'dense', 12, 12, 0.0278, -0.909),
        ('GPT2-md', 'sequential', 'OpenAI', 'dense', 16, 24, 0.0104, -0.930),
        ('GPT2-lg', 'sequential', 'OpenAI', 'dense', 20, 36, 0.0000, -0.741),
        ('GPT2-xl', 'sequential', 'OpenAI', 'dense', 25, 48, 0.0000, -0.801),
        ('TinyLlama-1.1B', 'sequential', 'TinyLlama', 'GQA', 32, 22, 0.0256, -0.485),
        ('OPT-1.3B', 'sequential', 'Meta', 'dense', 32, 24, 0.0104, -0.766),
    ]

    print(f"{'Model':<16} {'Arch':<12} {'Lab':<12} {'Attn':<6} {'H':>3} {'L':>3} {'AF':>8} {'r(depth)':>10}")
    print("-" * 78)
    for name, arch, lab, attn, heads, layers, af, r_dep in comparisons:
        print(f"{name:<16} {arch:<12} {lab:<12} {attn:<6} {heads:>3} {layers:>3} {af:>8.4f} {r_dep:>+10.3f}")

    # Statistical test with all data
    from scipy.stats import mannwhitneyu
    parallel_rs = [+0.670, +0.119, +0.343, metrics['r_cv_depth']]
    sequential_rs = [-0.909, -0.930, -0.741, -0.801, -0.485, -0.766]

    print(f"\n{'='*70}")
    print("DEPTH GRADIENT DIRECTION — UPDATED STATISTICAL TEST")
    print(f"{'='*70}\n")

    print(f"Parallel (n={len(parallel_rs)}):")
    print(f"  r values: {[f'{r:+.3f}' for r in parallel_rs]}")
    print(f"  Mean: {np.mean(parallel_rs):+.3f}")
    print(f"  All positive: {'YES' if all(r > 0 for r in parallel_rs) else 'NO'}")

    print(f"\nSequential (n={len(sequential_rs)}):")
    print(f"  r values: {[f'{r:+.3f}' for r in sequential_rs]}")
    print(f"  Mean: {np.mean(sequential_rs):+.3f}")
    print(f"  All negative: {'YES' if all(r < 0 for r in sequential_rs) else 'NO'}")

    U, p_mw = mannwhitneyu(parallel_rs, sequential_rs, alternative='greater')
    print(f"\n  Mann-Whitney U test: U={U}, p={p_mw:.6f}")

    print(f"\n{'='*70}")
    print("PREDICTION EVALUATION")
    print(f"{'='*70}\n")

    r = metrics['r_cv_depth']
    af = metrics['mean_af']

    print(f"P42g-A: Depth gradient r > 0 (parallel → positive)")
    print(f"  r = {r:+.3f}")
    print(f"  {'**CONFIRMED**' if r > 0 else '**FALSIFIED**'}")

    print(f"\nP42g-B: AF unconstrained (no prediction after Phi-1.5)")
    print(f"  AF = {af:.4f}")
    print(f"  (Informational only — Phi showed AF=0 possible for parallel)")

    with open('p42g_falcon_results.json', 'w') as f:
        json.dump({
            'model': MODEL,
            'n_heads': n_heads,
            'd_model': d_model, 'd_head': d_head, 'n_layers': n_layers,
            **metrics,
        }, f, indent=2)
    print(f"\nResults saved to p42g_falcon_results.json")
