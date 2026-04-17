"""
P42e: Phi-1.5 Architecture Test — Parallel + Dense (Cross-Family)
=================================================================

Phi-1.5 (Microsoft) uses parallel attention+MLP like Pythia (EleutherAI).
If the parallel/sequential hypothesis is UNIVERSAL (not Pythia-specific):
  - Phi-1.5 should show HIGH AF (like Pythia, not like GPT-2/TinyLlama)
  - This would confirm the result across independent labs and training data

Phi-1.5: 32 Q heads, 32 KV heads (dense), d_head=64, 24 layers, d_model=2048

Predictions:
  P42e-A: AF > 0.05 (parallel → high AF)
  P42e-B: Depth correlation positive or flat (parallel pattern)

Author: Clawd
Date: April 10, 2026
"""

import numpy as np
from scipy import stats
import json, time

PROJ_DIM = 64  # = d_head
SEED = 71
AF_THRESHOLD = 0.10
MODEL = 'microsoft/phi-1_5'


def extract_q_heads_phi(model_name):
    """Extract per-head Q projection matrices from Phi-1.5."""
    from transformers import AutoModelForCausalLM, AutoConfig
    import torch

    config = AutoConfig.from_pretrained(model_name, trust_remote_code=True)
    n_heads = config.num_attention_heads        # 32
    d_model = config.hidden_size                # 2048
    n_layers = config.num_hidden_layers         # 24
    d_head = d_model // n_heads                 # 64
    n_kv_heads = getattr(config, 'num_key_value_heads', n_heads)

    print(f"  Config: {n_heads} Q heads, {n_kv_heads} KV heads, d={d_model}, d_head={d_head}, {n_layers} layers")
    print(f"  Loading model...")
    model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float32, trust_remote_code=True)

    layer_heads = {}
    for layer_idx in range(n_layers):
        # Phi uses separate q_proj, k_proj, v_proj
        W_Q = None
        for name, param in model.named_parameters():
            if f'layers.{layer_idx}.' in name and 'q_proj.weight' in name:
                W_Q = param.detach().cpu().numpy()
                break

        if W_Q is None:
            # Fallback: check for fused QKV (some Phi variants)
            for name, param in model.named_parameters():
                if f'layers.{layer_idx}.' in name and ('Wqkv' in name or 'query_key_value' in name):
                    W_QKV = param.detach().cpu().numpy()
                    # Assume Q is first d_model rows
                    W_Q = W_QKV[:d_model, :]
                    break

        if W_Q is None:
            print(f"  WARNING: Q weights not found for layer {layer_idx}")
            # List available parameter names for debugging
            if layer_idx == 0:
                print("  Available attention params:")
                for name, _ in model.named_parameters():
                    if f'layers.{layer_idx}.' in name and ('attn' in name or 'self' in name):
                        print(f"    {name}")
            continue

        # W_Q shape should be (n_heads*d_head, d_model) = (2048, 2048)
        # Split into per-head: rows [h*d_head:(h+1)*d_head]
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
    print("P42e: Phi-1.5 — Parallel + Dense (Cross-Family Validation)")
    print("=" * 70)

    t0 = time.time()
    layer_heads, n_heads, n_kv_heads, d_model, n_layers, d_head = extract_q_heads_phi(MODEL)
    print(f"  Loaded in {time.time()-t0:.0f}s")

    t1 = time.time()
    metrics = compute_af(layer_heads, n_heads, d_model, d_head)
    print(f"  Computed in {time.time()-t1:.0f}s")

    # Results
    print(f"\n{'='*70}")
    print("RESULTS")
    print(f"{'='*70}\n")

    print(f"Phi-1.5: AF={metrics['mean_af']:.4f}, CV={metrics['mean_cv']:.6f}")
    print(f"Depth correlation: r={metrics['r_cv_depth']:+.3f}, p={metrics['p_cv_depth']:.4f}")

    # Comparison table
    print(f"\n{'='*70}")
    print("CROSS-ARCHITECTURE COMPARISON (all d_head=64)")
    print(f"{'='*70}\n")

    comparisons = [
        ('Pythia-410m', 'parallel', 'EleutherAI', 'dense', 16, 0.2057, 0.670),
        ('Pythia-160m', 'parallel', 'EleutherAI', 'dense', 12, 0.0903, 0.119),
        ('Pythia-70m', 'parallel', 'EleutherAI', 'dense', 8, 0.0833, -0.600),
        ('Phi-1.5', 'parallel', 'Microsoft', 'dense', 32, metrics['mean_af'], metrics['r_cv_depth']),
        ('GPT2-sm', 'sequential', 'OpenAI', 'dense', 12, 0.0278, -0.909),
        ('GPT2-md', 'sequential', 'OpenAI', 'dense', 16, 0.0104, -0.930),
        ('GPT2-lg', 'sequential', 'OpenAI', 'dense', 20, 0.0000, -0.741),
        ('GPT2-xl', 'sequential', 'OpenAI', 'dense', 25, 0.0000, -0.801),
        ('TinyLlama-1.1B', 'sequential', 'TinyLlama', 'GQA', 32, 0.0256, -0.485),
    ]

    print(f"{'Model':<16} {'Arch':<12} {'Lab':<12} {'Attn':<6} {'Heads':>5} {'AF':>8} {'r(depth)':>10}")
    print("-" * 74)
    for name, arch, lab, attn, heads, af, r_dep in comparisons:
        print(f"{name:<16} {arch:<12} {lab:<12} {attn:<6} {heads:>5} {af:>8.4f} {r_dep:>+10.3f}")

    # Prediction evaluation
    print(f"\n{'='*70}")
    print("PREDICTION EVALUATION")
    print(f"{'='*70}\n")

    af = metrics['mean_af']
    r = metrics['r_cv_depth']

    print(f"P42e-A: AF > 0.05 (parallel → high)")
    print(f"  AF = {af:.4f}")
    print(f"  {'**CONFIRMED**' if af > 0.05 else '**FALSIFIED**'}")

    print(f"\nP42e-B: Depth correlation positive or flat (parallel pattern)")
    print(f"  r = {r:+.3f}")
    print(f"  {'**CONFIRMED**' if r > -0.3 else '**FALSIFIED**'}")

    # Cross-family summary
    print(f"\n{'='*70}")
    print("CROSS-FAMILY VALIDATION")
    print(f"{'='*70}")
    print(f"\nParallel architectures (2 independent labs, 3 training regimes):")
    print(f"  Pythia (EleutherAI): AF = 0.083-0.206")
    print(f"  Phi-1.5 (Microsoft): AF = {af:.3f}")
    if af > 0.05:
        print(f"\n  → Parallel → Abelian is UNIVERSAL, not Pythia-specific")
    else:
        print(f"\n  → Parallel → Abelian may be Pythia-specific (NEEDS INVESTIGATION)")

    with open('p42e_phi_results.json', 'w') as f:
        json.dump({
            'model': MODEL,
            'n_heads': n_heads, 'n_kv_heads': n_kv_heads,
            'd_model': d_model, 'd_head': d_head, 'n_layers': n_layers,
            **metrics,
        }, f, indent=2)
    print(f"\nResults saved to p42e_phi_results.json")
