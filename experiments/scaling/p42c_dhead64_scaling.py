"""
P42c: AF Scaling Law — d_head=64 Family Only
=============================================

P42/P42b showed d_head is the dominant variable. Within d_head=64:
  Pythia-70m (8h): AF=0.083
  Pythia-160m (12h): AF=0.090
  Pythia-410m (16h): AF=0.206

GPT-2 also has d_head=64 across ALL sizes:
  GPT-2 small: 12h, d=768
  GPT-2 medium: 16h, d=1024
  GPT-2 large: 20h, d=1280
  GPT-2 XL: 25h, d=1600

7 data points, 5 head counts, 2 architectures, all d_head=64.

Predictions:
  P42c-A: AF increases with n_heads (power law alpha ≈ 1.0-1.5)
  P42c-B: GPT-2 and Pythia give similar AF at same head count

Author: Clawd
Date: April 10, 2026
"""

import numpy as np
from scipy import stats
import json, time

SEED = 71
AF_THRESHOLD = 0.10
PROJ_DIM = 64  # = d_head, so full rank

# GPT-2 family (all d_head=64)
GPT2_MODELS = [
    ('openai-community/gpt2', 'GPT2-sm', 12, 12),          # 768/12=64
    ('openai-community/gpt2-medium', 'GPT2-md', 16, 24),    # 1024/16=64
    ('openai-community/gpt2-large', 'GPT2-lg', 20, 36),     # 1280/20=64
    ('openai-community/gpt2-xl', 'GPT2-xl', 25, 48),        # 1600/25=64
]


def extract_q_heads_gpt2(model_name):
    """Extract Q heads from GPT-2 (separate Q/K/V projections via conv1d)."""
    from transformers import AutoModelForCausalLM, AutoConfig
    import torch

    config = AutoConfig.from_pretrained(model_name)
    n_heads = config.n_head
    d_model = config.n_embd
    n_layers = config.n_layer
    d_head = d_model // n_heads

    print(f"  Loading {model_name} ({n_heads}h, {n_layers}L, d={d_model}, d_head={d_head})...")
    model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float32)

    layer_heads = {}
    for layer_idx in range(n_layers):
        # GPT-2 uses a single c_attn weight: (d_model, 3*d_model)
        key = f"transformer.h.{layer_idx}.attn.c_attn.weight"
        W_attn = None
        for name, param in model.named_parameters():
            if name == key:
                W_attn = param.detach().cpu().numpy()  # (d_model, 3*d_model)
                break

        if W_attn is None:
            print(f"  WARNING: {key} not found")
            continue

        # GPT-2 c_attn: (d_model, 3*d_model) where columns are [Q, K, V]
        # Q columns: [:, 0:d_model]
        W_Q = W_attn[:, :d_model]  # (d_model, d_model)

        # Split Q into per-head: each head gets d_head columns
        # W_Q[:, h*d_head:(h+1)*d_head] gives (d_model, d_head)
        # Transpose to get (d_head, d_model) to match Pythia convention
        heads = []
        for h in range(n_heads):
            W_Q_h = W_Q[:, h*d_head:(h+1)*d_head].T  # (d_head, d_model)
            heads.append(W_Q_h)

        layer_heads[layer_idx] = heads

    del model
    import gc; gc.collect()
    return layer_heads, n_heads, d_model, n_layers, d_head


def compute_af(layer_heads, n_heads, d_model, d_head):
    """Compute AF with PROJ_DIM=d_head=64."""
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

    # Depth correlation
    layers = list(range(len(layer_afs)))
    r_cv, p_cv = stats.spearmanr(layers, layer_cvs) if len(layers) > 3 else (0, 1)

    return {
        'mean_af': float(np.mean(layer_afs)),
        'mean_cv': float(np.mean(layer_cvs)),
        'r_cv_depth': float(r_cv) if not np.isnan(r_cv) else 0.0,
        'layer_afs': layer_afs,
    }


if __name__ == '__main__':
    print("P42c: AF Scaling Law — d_head=64 Family")
    print("=" * 70)

    # Previous Pythia results (d_head=64)
    all_data = {
        'Py-70m':  {'n_heads': 8,  'n_layers': 6,  'd_model': 512,  'mean_af': 0.0833, 'mean_cv': 0.011220, 'arch': 'pythia'},
        'Py-160m': {'n_heads': 12, 'n_layers': 12, 'd_model': 768,  'mean_af': 0.0903, 'mean_cv': 0.007223, 'arch': 'pythia'},
        'Py-410m': {'n_heads': 16, 'n_layers': 24, 'd_model': 1024, 'mean_af': 0.2057, 'mean_cv': 0.013141, 'arch': 'pythia'},
    }

    # Run GPT-2 models
    for model_name, label, n_heads_expected, n_layers_expected in GPT2_MODELS:
        t0 = time.time()
        layer_heads, n_heads, d_model, n_layers, d_head = extract_q_heads_gpt2(model_name)
        load_time = time.time() - t0
        assert n_heads == n_heads_expected, f"Expected {n_heads_expected} heads, got {n_heads}"
        assert d_head == 64, f"Expected d_head=64, got {d_head}"

        t1 = time.time()
        metrics = compute_af(layer_heads, n_heads, d_model, d_head)
        comp_time = time.time() - t1

        print(f"  {label}: AF={metrics['mean_af']:.4f}, CV={metrics['mean_cv']:.6f}, "
              f"r_depth={metrics['r_cv_depth']:+.3f} [{load_time:.0f}s + {comp_time:.0f}s]")

        all_data[label] = {
            'n_heads': n_heads, 'n_layers': n_layers,
            'd_model': d_model, **metrics, 'arch': 'gpt2',
        }
        del layer_heads

    # ============================================================
    # RESULTS
    # ============================================================
    print(f"\n{'='*70}")
    print("ALL d_head=64 MODELS")
    print(f"{'='*70}\n")

    items = sorted(all_data.items(), key=lambda x: x[1]['n_heads'])
    print(f"{'Model':<10} {'Arch':<8} {'Heads':>5} {'Layers':>6} {'AF':>8} {'CV':>12}")
    print("-" * 54)
    for label, d in items:
        print(f"{label:<10} {d['arch']:<8} {d['n_heads']:>5} {d.get('n_layers','?'):>6} "
              f"{d['mean_af']:>8.4f} {d['mean_cv']:>12.6f}")

    # ============================================================
    # SCALING LAW
    # ============================================================
    heads = np.array([d['n_heads'] for _, d in items])
    afs = np.array([d['mean_af'] for _, d in items])

    print(f"\n{'='*70}")
    print("SCALING LAW ANALYSIS")
    print(f"{'='*70}\n")

    # Spearman correlation
    r_sp, p_sp = stats.spearmanr(heads, afs)
    print(f"Spearman (AF vs n_heads): r={r_sp:+.3f}, p={p_sp:.4f}")

    # Power law fit: log(AF) = alpha * log(n_heads) + C
    mask = afs > 0
    if np.sum(mask) >= 3:
        log_h = np.log(heads[mask])
        log_af = np.log(afs[mask])
        slope, intercept, r_val, p_val, std_err = stats.linregress(log_h, log_af)
        print(f"Power law: AF ~ n_heads^{slope:.3f} (r²={r_val**2:.4f}, p={p_val:.4f})")
        print(f"  alpha = {slope:.3f} ± {std_err:.3f}")

        # Predicted AF for each model
        print(f"\n  {'Model':<10} {'Heads':>5} {'AF_obs':>8} {'AF_pred':>8} {'Ratio':>8}")
        print("  " + "-" * 43)
        for label, d in items:
            if d['mean_af'] > 0:
                pred = np.exp(intercept + slope * np.log(d['n_heads']))
                ratio = d['mean_af'] / pred
                print(f"  {label:<10} {d['n_heads']:>5} {d['mean_af']:>8.4f} {pred:>8.4f} {ratio:>8.3f}")

    # ============================================================
    # CROSS-ARCHITECTURE COMPARISON
    # ============================================================
    print(f"\n{'='*70}")
    print("CROSS-ARCHITECTURE: GPT-2 vs PYTHIA at same head count")
    print(f"{'='*70}\n")

    # 12 heads: GPT2-sm vs Py-160m
    if 'GPT2-sm' in all_data and 'Py-160m' in all_data:
        g = all_data['GPT2-sm']['mean_af']
        p = all_data['Py-160m']['mean_af']
        print(f"12 heads: GPT2-sm AF={g:.4f}, Pythia-160m AF={p:.4f}, ratio={g/p:.3f}")

    # 16 heads: GPT2-md vs Py-410m
    if 'GPT2-md' in all_data and 'Py-410m' in all_data:
        g = all_data['GPT2-md']['mean_af']
        p = all_data['Py-410m']['mean_af']
        print(f"16 heads: GPT2-md AF={g:.4f}, Pythia-410m AF={p:.4f}, ratio={g/p:.3f}")

    # ============================================================
    # PREDICTION EVALUATION
    # ============================================================
    print(f"\n{'='*70}")
    print("PREDICTION EVALUATION")
    print(f"{'='*70}\n")

    print(f"P42c-A: AF increases with n_heads (power law)")
    print(f"  Spearman r={r_sp:+.3f}, p={p_sp:.4f}")
    if p_sp < 0.05 and r_sp > 0:
        print(f"  **CONFIRMED** — monotonic increase, p < 0.05")
    elif r_sp > 0:
        print(f"  Direction correct but not significant (p={p_sp:.3f})")
    else:
        print(f"  **FALSIFIED**")

    print(f"\nP42c-B: Same AF at same head count across architectures")
    if 'GPT2-sm' in all_data and 'Py-160m' in all_data:
        g12 = all_data['GPT2-sm']['mean_af']
        p12 = all_data['Py-160m']['mean_af']
        ratio_12 = g12 / p12 if p12 > 0 else float('inf')
        close_12 = 0.5 < ratio_12 < 2.0
        print(f"  12h: GPT2={g12:.4f}, Pythia={p12:.4f}, ratio={ratio_12:.3f} {'✓' if close_12 else '✗'}")
    if 'GPT2-md' in all_data and 'Py-410m' in all_data:
        g16 = all_data['GPT2-md']['mean_af']
        p16 = all_data['Py-410m']['mean_af']
        ratio_16 = g16 / p16 if p16 > 0 else float('inf')
        close_16 = 0.5 < ratio_16 < 2.0
        print(f"  16h: GPT2={g16:.4f}, Pythia={p16:.4f}, ratio={ratio_16:.3f} {'✓' if close_16 else '✗'}")

    with open('p42c_dhead64_results.json', 'w') as f:
        json.dump(all_data, f, indent=2)
    print(f"\nResults saved to p42c_dhead64_results.json")
