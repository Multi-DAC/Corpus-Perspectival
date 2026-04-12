"""
P41b Fine Search: Reversal between step35000 and step55000
==========================================================

Coarse search found reversal between step40000 (r=-0.056) and step50000 (r=+0.215).
This runs every 2000 steps through the crossover region.

Checkpoints available at every 1000 steps.

Author: Clawd
Date: April 10, 2026
"""

import numpy as np
from scipy import stats
import json, time

PROJ_DIM = 64
SEED = 71
AF_THRESHOLD = 0.10
MODEL_BASE = 'EleutherAI/pythia-410m-deduped'

CHECKPOINTS = [
    'step35000', 'step37000', 'step39000', 'step41000',
    'step43000', 'step45000', 'step47000', 'step49000',
    'step51000', 'step53000', 'step55000'
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


def compute_depth_correlation(layer_heads, n_heads, d_model, d_head):
    np.random.seed(SEED)
    p_out = np.random.randn(PROJ_DIM, d_head) / np.sqrt(d_head)
    p_in = np.random.randn(d_model, PROJ_DIM) / np.sqrt(d_model)

    cvs = []
    afs = []
    for layer_idx in sorted(layer_heads.keys()):
        heads = layer_heads[layer_idx]
        proj_heads = [p_out @ A @ p_in for A in heads]
        n_h = len(proj_heads)

        # Commutator variance
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
        cvs.append(float(np.var(comm_norms[mask])))

        # Killing form AF
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
        afs.append(int(np.sum(evs < AF_THRESHOLD)) / n_h)

    r_cv, p_cv = stats.spearmanr(range(len(cvs)), cvs)
    return float(r_cv), float(p_cv), np.mean(afs), np.mean(cvs)


if __name__ == '__main__':
    print("P41b FINE SEARCH: Crossover region step35000-step55000")
    print(f"Model: {MODEL_BASE}")
    print("=" * 70)

    results = {}
    for ckpt in CHECKPOINTS:
        t0 = time.time()
        print(f"{ckpt}...", end=' ', flush=True)
        layer_heads, n_heads, d_model, n_layers, d_head = extract_q_heads_pythia(
            MODEL_BASE, revision=ckpt)
        r_cv, p_cv, mean_af, mean_cv = compute_depth_correlation(
            layer_heads, n_heads, d_model, d_head)
        elapsed = time.time() - t0

        sign = '+' if r_cv >= 0 else ''
        print(f"r_cv={sign}{r_cv:.3f} (p={p_cv:.4f}), AF={mean_af:.4f}, CV={mean_cv:.6f} [{elapsed:.0f}s]")

        results[ckpt] = {
            'r_cv': r_cv, 'p_cv': p_cv,
            'mean_af': mean_af, 'mean_cv': mean_cv,
        }
        del layer_heads

    # Summary
    print(f"\n{'='*70}")
    print("CROSSOVER REGION")
    print(f"{'='*70}\n")

    print(f"{'Step':<14} {'r(CV,depth)':>12} {'p-value':>10} {'mean_AF':>10}")
    print("-" * 48)
    for ckpt in CHECKPOINTS:
        m = results[ckpt]
        sign = '+' if m['r_cv'] >= 0 else ''
        marker = ' <-- ZERO CROSSING' if abs(m['r_cv']) < 0.05 else ''
        print(f"{ckpt:<14} {sign}{m['r_cv']:>11.3f} {m['p_cv']:>10.4f} {m['mean_af']:>10.4f}{marker}")

    # Interpolate zero crossing
    ckpt_list = list(results.keys())
    steps = [int(c.replace('step','')) for c in ckpt_list]
    r_values = [results[c]['r_cv'] for c in ckpt_list]

    for i in range(len(r_values) - 1):
        if r_values[i] * r_values[i+1] < 0:
            # Linear interpolation
            s1, s2 = steps[i], steps[i+1]
            r1, r2 = r_values[i], r_values[i+1]
            zero_step = s1 + (s2 - s1) * (-r1) / (r2 - r1)
            print(f"\nInterpolated zero crossing: ~step{int(zero_step)}")
            print(f"  ({s1/143000*100:.1f}% - {s2/143000*100:.1f}% through training)")
            break

    with open('p41b_fine_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to p41b_fine_results.json")
