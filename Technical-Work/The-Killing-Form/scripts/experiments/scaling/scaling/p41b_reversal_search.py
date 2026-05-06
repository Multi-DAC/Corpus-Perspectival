"""
P41b: Binary Search for Depth Gradient Reversal Point
=====================================================

P41 showed: at step20000, CommVar vs depth is NEGATIVE (r=-0.703).
At step143000, it REVERSES to POSITIVE (r=+0.670).

This script finds WHERE the reversal happens by sampling checkpoints
between step20000 and step143000.

Phase 1: Coarse search (8 checkpoints, ~30k apart)
Phase 2: Fine search (around the flip point)

Author: Clawd
Date: April 10, 2026
"""

import numpy as np
from scipy import stats
import json, time, sys

PROJ_DIM = 64
SEED = 71
AF_THRESHOLD = 0.10
MODEL_BASE = 'EleutherAI/pythia-410m-deduped'

# Phase 1: Coarse search
COARSE_CHECKPOINTS = [
    'step20000', 'step30000', 'step40000', 'step50000',
    'step70000', 'step90000', 'step110000', 'step130000', 'step143000'
]


def extract_q_heads_pythia(model_name, revision=None):
    """Extract per-head Q projection matrices from a Pythia model."""
    from transformers import AutoModelForCausalLM, AutoConfig
    import torch

    kwargs = {'revision': revision} if revision else {}
    config = AutoConfig.from_pretrained(model_name, **kwargs)
    n_heads = config.num_attention_heads
    d_model = config.hidden_size
    n_layers = config.num_hidden_layers
    d_head = d_model // n_heads

    model = AutoModelForCausalLM.from_pretrained(model_name, dtype=torch.float32, **kwargs)

    layer_heads = {}
    for layer_idx in range(n_layers):
        key = f"gpt_neox.layers.{layer_idx}.attention.query_key_value.weight"
        W_QKV = None
        for name, param in model.named_parameters():
            if name == key:
                W_QKV = param.detach().cpu().numpy()
                break
        if W_QKV is None:
            continue

        heads = []
        for h in range(n_heads):
            offset = h * 3 * d_head
            W_Q_h = W_QKV[offset:offset + d_head, :]
            heads.append(W_Q_h)
        layer_heads[layer_idx] = heads

    del model
    import gc; gc.collect()
    return layer_heads, n_heads, d_model, n_layers, d_head


def compute_depth_correlation(layer_heads, n_heads, d_model, d_head):
    """Compute CommVar at each layer, return depth correlation."""
    np.random.seed(SEED)
    p_out = np.random.randn(PROJ_DIM, d_head) / np.sqrt(d_head)
    p_in = np.random.randn(d_model, PROJ_DIM) / np.sqrt(d_model)

    layer_metrics = {}
    for layer_idx in sorted(layer_heads.keys()):
        heads = layer_heads[layer_idx]
        proj_heads = [p_out @ A @ p_in for A in heads]
        n_h = len(proj_heads)

        # Commutator norms (normalized)
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
        comm_var = float(np.var(comm_norms[mask]))

        # Killing form eigenvalues for AF
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
        n_null = int(np.sum(eigenvalues < AF_THRESHOLD))
        af = n_null / n_h

        layer_metrics[layer_idx] = {'comm_var': comm_var, 'af': af}

    layers = sorted(layer_metrics.keys())
    cvs = [layer_metrics[l]['comm_var'] for l in layers]
    afs = [layer_metrics[l]['af'] for l in layers]

    r_cv, p_cv = stats.spearmanr(list(range(len(layers))), cvs)
    try:
        r_af, p_af = stats.spearmanr(list(range(len(layers))), afs)
    except:
        r_af, p_af = float('nan'), float('nan')

    return {
        'r_cv': float(r_cv) if not np.isnan(r_cv) else 0.0,
        'p_cv': float(p_cv) if not np.isnan(p_cv) else 1.0,
        'r_af': float(r_af) if not np.isnan(r_af) else 0.0,
        'p_af': float(p_af) if not np.isnan(p_af) else 1.0,
        'mean_cv': float(np.mean(cvs)),
        'mean_af': float(np.mean(afs)),
        'layer_metrics': {str(k): v for k, v in layer_metrics.items()},
    }


if __name__ == '__main__':
    phase = int(sys.argv[1]) if len(sys.argv) > 1 else 1

    if phase == 1:
        checkpoints = COARSE_CHECKPOINTS
        print("P41b Phase 1: COARSE SEARCH for depth gradient reversal")
    else:
        # Phase 2: read coarse results, pick fine range
        with open('p41b_coarse_results.json') as f:
            coarse = json.load(f)
        # Find sign flip
        ckpts = list(coarse.keys())
        for i in range(len(ckpts) - 1):
            r1 = coarse[ckpts[i]]['r_cv']
            r2 = coarse[ckpts[i+1]]['r_cv']
            if r1 * r2 < 0:  # sign flip
                step1 = int(ckpts[i].replace('step', ''))
                step2 = int(ckpts[i+1].replace('step', ''))
                break
        # Fine grid between flip points
        interval = (step2 - step1) // 6
        checkpoints = [f'step{step1 + interval * j}' for j in range(7)]
        print(f"P41b Phase 2: FINE SEARCH between {ckpts[i]} and {ckpts[i+1]}")
        print(f"  Checkpoints: {checkpoints}")

    print(f"Model: {MODEL_BASE}")
    print("=" * 70)

    results = {}
    for ckpt in checkpoints:
        t0 = time.time()
        step_num = int(ckpt.replace('step', ''))
        rev = ckpt

        print(f"\n{ckpt}...", end=' ', flush=True)
        layer_heads, n_heads, d_model, n_layers, d_head = extract_q_heads_pythia(
            MODEL_BASE, revision=rev)
        load_time = time.time() - t0

        t1 = time.time()
        metrics = compute_depth_correlation(layer_heads, n_heads, d_model, d_head)
        comp_time = time.time() - t1

        r_cv = metrics['r_cv']
        sign = '+' if r_cv > 0 else '-'
        print(f"r_cv={sign}{abs(r_cv):.3f} (p={metrics['p_cv']:.4f}), "
              f"mean_AF={metrics['mean_af']:.4f}, "
              f"load={load_time:.0f}s, compute={comp_time:.1f}s")

        results[ckpt] = metrics
        del layer_heads  # Free memory between checkpoints

    # Summary
    print(f"\n{'='*70}")
    print("DEPTH GRADIENT EVOLUTION")
    print(f"{'='*70}\n")

    print(f"{'Checkpoint':<14} {'r(CV,depth)':>12} {'p-value':>10} {'mean_AF':>10} {'mean_CV':>12}")
    print("-" * 62)
    for ckpt in checkpoints:
        m = results[ckpt]
        sign = '+' if m['r_cv'] >= 0 else ''
        print(f"{ckpt:<14} {sign}{m['r_cv']:>11.3f} {m['p_cv']:>10.4f} "
              f"{m['mean_af']:>10.4f} {m['mean_cv']:>12.6f}")

    # Find reversal
    ckpt_list = list(results.keys())
    reversal_found = False
    for i in range(len(ckpt_list) - 1):
        r1 = results[ckpt_list[i]]['r_cv']
        r2 = results[ckpt_list[i+1]]['r_cv']
        if r1 < 0 and r2 > 0:
            s1 = int(ckpt_list[i].replace('step', ''))
            s2 = int(ckpt_list[i+1].replace('step', ''))
            print(f"\n*** REVERSAL between {ckpt_list[i]} and {ckpt_list[i+1]} ***")
            print(f"    r_cv flips from {r1:+.3f} to {r2:+.3f}")
            print(f"    Training step range: {s1} - {s2} ({s2-s1} steps apart)")
            reversal_found = True
            break

    if not reversal_found:
        # Check if all same sign
        signs = ['+' if results[c]['r_cv'] >= 0 else '-' for c in ckpt_list]
        print(f"\nNo clean reversal found. Signs: {' '.join(signs)}")

    # Save
    outfile = f'p41b_{"coarse" if phase == 1 else "fine"}_results.json'
    with open(outfile, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {outfile}")
