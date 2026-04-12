"""
P42: Abelian Fraction Scaling Law
=================================

Does AF depend on head count or model size? Pythia suite disentangles:
- 70m: 8 heads, 6 layers
- 160m: 12 heads, 12 layers (already measured: AF=0.090)
- 410m: 16 heads, 24 layers (already measured: AF=0.206)
- 1b: 8 heads, 16 layers (KEY: big model, few heads)
- 1.4b: 16 heads, 24 layers (KEY: same heads as 410m, bigger)
- 2.8b: 32 heads, 32 layers (extends range)

Pre-registered predictions:
  P42-A: AF(1b, 8h) < AF(160m, 12h) — heads matter more than size
  P42-B: AF(1.4b, 16h) ≈ AF(410m, 16h) — same heads → same AF
  P42-C: AF scales as power law in n_heads

Author: Clawd
Date: April 10, 2026
"""

import numpy as np
from scipy import stats, optimize
import json, time

PROJ_DIM = 64
SEED = 71
AF_THRESHOLD = 0.10

MODELS = [
    ('EleutherAI/pythia-70m-deduped', '70m', 8, 6),
    # ('EleutherAI/pythia-160m-deduped', '160m', 12, 12),  # already have
    # ('EleutherAI/pythia-410m-deduped', '410m', 16, 24),  # already have
    ('EleutherAI/pythia-1b-deduped', '1b', 8, 16),
    ('EleutherAI/pythia-1.4b-deduped', '1.4b', 16, 24),
    ('EleutherAI/pythia-2.8b-deduped', '2.8b', 32, 32),
]


def extract_q_heads_pythia(model_name):
    from transformers import AutoModelForCausalLM, AutoConfig
    import torch

    config = AutoConfig.from_pretrained(model_name)
    n_heads = config.num_attention_heads
    d_model = config.hidden_size
    n_layers = config.num_hidden_layers
    d_head = d_model // n_heads

    print(f"  Loading {model_name} ({n_heads}h, {n_layers}L, d={d_model})...")
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


def compute_af_for_model(layer_heads, n_heads, d_model, d_head):
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

    layers = list(range(len(layer_afs)))
    r_cv, p_cv = stats.spearmanr(layers, layer_cvs) if len(layers) > 3 else (0, 1)

    return {
        'mean_af': float(np.mean(layer_afs)),
        'mean_cv': float(np.mean(layer_cvs)),
        'r_cv_depth': float(r_cv) if not np.isnan(r_cv) else 0.0,
        'p_cv_depth': float(p_cv) if not np.isnan(p_cv) else 1.0,
        'layer_afs': layer_afs,
        'layer_cvs': layer_cvs,
    }


if __name__ == '__main__':
    print("P42: Abelian Fraction Scaling Law")
    print("=" * 70)

    # Include previous results
    all_data = {
        '160m': {'n_heads': 12, 'n_layers': 12, 'd_model': 768, 'mean_af': 0.0903, 'mean_cv': 0.007223,
                 'r_cv_depth': 0.119, 'source': 'p41c'},
        '410m': {'n_heads': 16, 'n_layers': 24, 'd_model': 1024, 'mean_af': 0.2057, 'mean_cv': 0.013141,
                 'r_cv_depth': 0.670, 'source': 'p41'},
    }

    for model_name, label, n_heads_expected, n_layers_expected in MODELS:
        t0 = time.time()
        layer_heads, n_heads, d_model, n_layers, d_head = extract_q_heads_pythia(model_name)
        load_time = time.time() - t0
        assert n_heads == n_heads_expected, f"Expected {n_heads_expected} heads, got {n_heads}"

        t1 = time.time()
        metrics = compute_af_for_model(layer_heads, n_heads, d_model, d_head)
        comp_time = time.time() - t1

        print(f"  {label}: AF={metrics['mean_af']:.4f}, CV={metrics['mean_cv']:.6f}, "
              f"r_depth={metrics['r_cv_depth']:+.3f} [load={load_time:.0f}s, compute={comp_time:.0f}s]")

        all_data[label] = {
            'n_heads': n_heads,
            'n_layers': n_layers,
            'd_model': d_model,
            **metrics,
            'source': 'p42',
        }
        del layer_heads

    # ============================================================
    # SCALING ANALYSIS
    # ============================================================
    print(f"\n{'='*70}")
    print("ABELIAN FRACTION vs HEAD COUNT")
    print(f"{'='*70}\n")

    # Sort by head count
    items = sorted(all_data.items(), key=lambda x: (x[1]['n_heads'], x[1].get('n_layers', 0)))

    print(f"{'Model':<8} {'Heads':>5} {'Layers':>6} {'d_model':>7} {'AF':>8} {'CV':>12} {'r(depth)':>10}")
    print("-" * 62)
    for label, d in items:
        print(f"{label:<8} {d['n_heads']:>5} {d.get('n_layers','?'):>6} {d.get('d_model','?'):>7} "
              f"{d['mean_af']:>8.4f} {d['mean_cv']:>12.6f} {d.get('r_cv_depth',0):>+10.3f}")

    # ============================================================
    # PREDICTION EVALUATION
    # ============================================================
    print(f"\n{'='*70}")
    print("PREDICTION EVALUATION")
    print(f"{'='*70}\n")

    # P42-A: AF(1b, 8h) < AF(160m, 12h)
    af_1b = all_data['1b']['mean_af']
    af_160m = all_data['160m']['mean_af']
    print(f"P42-A: AF(1b, 8h) < AF(160m, 12h)")
    print(f"  AF(1b) = {af_1b:.4f}, AF(160m) = {af_160m:.4f}")
    if af_1b < af_160m:
        print(f"  **CONFIRMED** — heads matter more than model size")
    else:
        print(f"  **FALSIFIED** — model size matters more than heads")
    print()

    # P42-B: AF(1.4b, 16h) ≈ AF(410m, 16h)
    af_14b = all_data['1.4b']['mean_af']
    af_410m = all_data['410m']['mean_af']
    ratio = af_14b / af_410m if af_410m > 0 else float('inf')
    print(f"P42-B: AF(1.4b, 16h) ≈ AF(410m, 16h)")
    print(f"  AF(1.4b) = {af_14b:.4f}, AF(410m) = {af_410m:.4f}, ratio = {ratio:.3f}")
    if 0.7 < ratio < 1.3:
        print(f"  **CONFIRMED** — same heads → similar AF (within 30%)")
    else:
        direction = "higher" if ratio > 1.3 else "lower"
        print(f"  **FALSIFIED** — 1.4b is {direction} despite same head count")
    print()

    # P42-C: Power law fit
    heads = np.array([d['n_heads'] for _, d in items])
    afs = np.array([d['mean_af'] for _, d in items])

    # Only fit on points with AF > 0
    mask = afs > 0
    if np.sum(mask) >= 3:
        log_h = np.log(heads[mask])
        log_af = np.log(afs[mask])
        slope, intercept, r_val, p_val, std_err = stats.linregress(log_h, log_af)
        print(f"P42-C: Power law fit AF ~ n_heads^alpha")
        print(f"  alpha = {slope:.3f} ± {std_err:.3f}")
        print(f"  r² = {r_val**2:.4f}, p = {p_val:.4f}")
        if p_val < 0.05:
            print(f"  **CONFIRMED** — power law with exponent {slope:.2f}")
        else:
            print(f"  Inconclusive (p > 0.05)")

        # Also test: does model size (params) predict AF?
        # Use n_layers * d_model^2 as proxy for params
        params_proxy = np.array([d.get('n_layers',1) * d.get('d_model',1)**2 for _, d in items])
        log_p = np.log(params_proxy[mask])
        slope_p, _, r_p, p_p, _ = stats.linregress(log_p, log_af)
        print(f"\n  Comparison: AF ~ params^beta")
        print(f"  beta = {slope_p:.3f}, r² = {r_p**2:.4f}, p = {p_p:.4f}")
        print(f"  {'Heads' if r_val**2 > r_p**2 else 'Params'} is the better predictor")

    # ============================================================
    # SIZE-MATCHED COMPARISON
    # ============================================================
    print(f"\n{'='*70}")
    print("SIZE-MATCHED COMPARISONS")
    print(f"{'='*70}\n")

    # Same heads, different size
    print("Same heads (16), different size:")
    print(f"  410m: AF={af_410m:.4f}")
    print(f"  1.4b: AF={af_14b:.4f}")
    print(f"  Ratio: {af_14b/af_410m:.3f}" if af_410m > 0 else "")

    # Different heads, compare
    if '70m' in all_data and '1b' in all_data:
        af_70m = all_data['70m']['mean_af']
        print(f"\nSame heads (8), different size:")
        print(f"  70m: AF={af_70m:.4f}")
        print(f"  1b:  AF={af_1b:.4f}")
        if af_70m > 0:
            print(f"  Ratio: {af_1b/af_70m:.3f}")

    # Save
    with open('p42_scaling_results.json', 'w') as f:
        json.dump(all_data, f, indent=2)
    print(f"\nResults saved to p42_scaling_results.json")
