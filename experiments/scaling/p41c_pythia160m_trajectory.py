"""
P41c: Cross-Architecture — Pythia-160m Training Trajectory
==========================================================

Pythia-160m: 12 heads (same as GPT-2), 12 layers, d_model=768, d_head=64
Does the depth gradient reversal occur in a smaller model with fewer heads?

If yes → universal phenomenon
If no → scale/head-count dependent

Also checks: does GPT-2-like head count produce GPT-2-like depth profile?

Author: Clawd
Date: April 10, 2026
"""

import numpy as np
from scipy import stats
import json, time

PROJ_DIM = 64
SEED = 71
AF_THRESHOLD = 0.10
MODEL = 'EleutherAI/pythia-160m-deduped'

# Key checkpoints: early, crossover region (scaled from 410m), late
# 410m reversal at 31.5% = step45000/143000
# 160m trained for same 143000 steps, so check same region
CHECKPOINTS = [
    'step1', 'step512', 'step4000', 'step20000',
    'step35000', 'step45000', 'step55000',
    'step70000', 'step100000', 'step143000'
]


def extract_q_heads_pythia(model_name, revision):
    from transformers import AutoModelForCausalLM, AutoConfig
    import torch

    config = AutoConfig.from_pretrained(model_name, revision=revision)
    n_heads = config.num_attention_heads
    d_model = config.hidden_size
    n_layers = config.num_hidden_layers
    d_head = d_model // n_heads

    model = AutoModelForCausalLM.from_pretrained(model_name, dtype=torch.float32, revision=revision)

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


def compute_metrics(layer_heads, n_heads, d_model, d_head):
    np.random.seed(SEED)
    p_out = np.random.randn(PROJ_DIM, d_head) / np.sqrt(d_head)
    p_in = np.random.randn(d_model, PROJ_DIM) / np.sqrt(d_model)

    per_layer = {}
    for layer_idx in sorted(layer_heads.keys()):
        heads = layer_heads[layer_idx]
        proj_heads = [p_out @ A @ p_in for A in heads]
        n_h = len(proj_heads)

        comm_norms = np.zeros((n_h, n_h))
        for h in range(n_h):
            for hp in range(h+1, n_h):
                comm = proj_heads[h] @ proj_heads[hp] - proj_heads[hp] @ proj_heads[h]
                comm_norms[h, hp] = np.linalg.norm(comm, 'fro')
                comm_norms[hp, h] = comm_norms[h, hp]
        typical = np.mean([np.linalg.norm(A, 'fro') for A in proj_heads])
        if typical > 0:
            comm_norms /= (typical ** 2)
        mask = np.ones_like(comm_norms, dtype=bool)
        np.fill_diagonal(mask, False)
        cv = float(np.var(comm_norms[mask]))

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

        per_layer[layer_idx] = {'cv': cv, 'af': af}

    layers = sorted(per_layer.keys())
    cvs = [per_layer[l]['cv'] for l in layers]
    afs = [per_layer[l]['af'] for l in layers]

    r_cv, p_cv = stats.spearmanr(range(len(cvs)), cvs)
    try:
        r_af, p_af = stats.spearmanr(range(len(afs)), afs)
    except:
        r_af, p_af = float('nan'), float('nan')

    return {
        'r_cv': float(r_cv) if not np.isnan(r_cv) else 0.0,
        'p_cv': float(p_cv) if not np.isnan(p_cv) else 1.0,
        'r_af': float(r_af) if not np.isnan(r_af) else 0.0,
        'mean_af': float(np.mean(afs)),
        'mean_cv': float(np.mean(cvs)),
        'per_layer': {str(k): v for k, v in per_layer.items()},
    }


if __name__ == '__main__':
    print(f"P41c: Pythia-160m-deduped Training Trajectory")
    print(f"Architecture: 12 heads, 12 layers, d_model=768, d_head=64")
    print("=" * 70)

    results = {}
    for ckpt in CHECKPOINTS:
        t0 = time.time()
        print(f"{ckpt}...", end=' ', flush=True)
        layer_heads, n_heads, d_model, n_layers, d_head = extract_q_heads_pythia(
            MODEL, revision=ckpt)
        metrics = compute_metrics(layer_heads, n_heads, d_model, d_head)
        elapsed = time.time() - t0

        sign = '+' if metrics['r_cv'] >= 0 else ''
        print(f"r_cv={sign}{metrics['r_cv']:.3f} (p={metrics['p_cv']:.4f}), "
              f"AF={metrics['mean_af']:.4f}, CV={metrics['mean_cv']:.6f} [{elapsed:.0f}s]")

        results[ckpt] = metrics
        del layer_heads

    # Summary
    print(f"\n{'='*70}")
    print("PYTHIA-160m TRAINING TRAJECTORY")
    print(f"{'='*70}\n")

    print(f"{'Checkpoint':<14} {'r(CV,depth)':>12} {'p-value':>10} {'mean_AF':>10} {'mean_CV':>12}")
    print("-" * 62)
    for ckpt in CHECKPOINTS:
        m = results[ckpt]
        sign = '+' if m['r_cv'] >= 0 else ''
        print(f"{ckpt:<14} {sign}{m['r_cv']:>11.3f} {m['p_cv']:>10.4f} "
              f"{m['mean_af']:>10.4f} {m['mean_cv']:>12.6f}")

    # Check for reversal
    ckpt_list = list(results.keys())
    for i in range(len(ckpt_list) - 1):
        r1 = results[ckpt_list[i]]['r_cv']
        r2 = results[ckpt_list[i+1]]['r_cv']
        if r1 * r2 < 0:
            s1 = int(ckpt_list[i].replace('step', ''))
            s2 = int(ckpt_list[i+1].replace('step', ''))
            print(f"\n*** REVERSAL between {ckpt_list[i]} and {ckpt_list[i+1]} ***")
            print(f"    r_cv: {r1:+.3f} → {r2:+.3f}")
            break
    else:
        signs = ['+' if results[c]['r_cv'] >= 0 else '-' for c in ckpt_list]
        print(f"\nNo reversal detected. Sign sequence: {' '.join(signs)}")

    # Compare with 410m
    print(f"\n{'='*70}")
    print("CROSS-ARCHITECTURE COMPARISON")
    print(f"{'='*70}")
    print(f"\nPythia-410m reversal: step~45000 (31.5%)")
    print(f"Pythia-410m final: r_cv=+0.670, AF=0.206, 16 heads")
    m_final = results['step143000']
    print(f"Pythia-160m final: r_cv={m_final['r_cv']:+.3f}, AF={m_final['mean_af']:.3f}, 12 heads")

    # Depth profile at final checkpoint
    print(f"\nPythia-160m final depth profile:")
    per = results['step143000']['per_layer']
    for l in sorted(per.keys(), key=int):
        af = per[l]['af']
        bar = '#' * int(af * 20)
        print(f"  L{int(l):>2}: AF={af:.3f} {bar}")

    with open('p41c_pythia160m_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to p41c_pythia160m_results.json")
