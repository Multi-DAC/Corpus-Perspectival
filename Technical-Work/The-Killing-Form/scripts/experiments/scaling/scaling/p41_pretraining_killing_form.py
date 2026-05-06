"""
P41: Killing Form Evolution Through Pretraining
================================================

P26/P26-followup showed the Killing form is RLHF-invariant (both Q and O).
This script tests whether the Killing form evolves during PRETRAINING.

Uses Pythia-410m (16 heads, 24 layers, dense MHA) with checkpoints:
  step1    — near-random (after 1 gradient step)
  step64   — very early
  step512  — early structure emerging
  step4000 — mid-early training
  step20000 — mid training
  step143000 — fully trained (main)

Prediction: Abelian fraction should INCREASE during training as heads
specialize and differentiate. Step1 should resemble random (AF ≈ 0).

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

# Log-spaced through training trajectory
CHECKPOINTS = ['step1', 'step64', 'step512', 'step4000', 'step20000', 'step143000']


def extract_q_heads_pythia(model_name, revision=None):
    """Extract per-head Q projection matrices from a Pythia model."""
    from transformers import AutoModelForCausalLM, AutoConfig
    import torch

    kwargs = {'revision': revision} if revision else {}
    config = AutoConfig.from_pretrained(model_name, **kwargs)
    n_heads = config.num_attention_heads      # 16
    d_model = config.hidden_size              # 1024
    n_layers = config.num_hidden_layers       # 24
    d_head = d_model // n_heads               # 64

    model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float32, **kwargs)

    layer_heads = {}
    for layer_idx in range(n_layers):
        # Pythia uses GPT-NeoX style: query_key_value fused projection
        # Shape: (3 * d_model, d_model) = (3072, 1024)
        key = f"gpt_neox.layers.{layer_idx}.attention.query_key_value.weight"
        W_QKV = None
        for name, param in model.named_parameters():
            if name == key:
                W_QKV = param.detach().cpu().numpy()
                break

        if W_QKV is None:
            print(f"  WARNING: {key} not found")
            continue

        # GPT-NeoX interleaves Q, K, V per head:
        # [Q_h0, K_h0, V_h0, Q_h1, K_h1, V_h1, ...]
        # Each block is d_head rows
        heads = []
        for h in range(n_heads):
            offset = h * 3 * d_head
            W_Q_h = W_QKV[offset:offset + d_head, :]  # (d_head, d_model)
            heads.append(W_Q_h)

        layer_heads[layer_idx] = heads

    del model
    import gc; gc.collect()

    return layer_heads, n_heads, d_model, n_layers, d_head


def compute_killing_form(heads, proj):
    """Compute Killing form from head matrices."""
    n_h = len(heads)
    p_out, p_in = proj
    proj_heads = [p_out @ A @ p_in for A in heads]

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
    killing_norm = killing / max_k if max_k > 0 else killing
    eigenvalues = np.sort(np.abs(np.linalg.eigvalsh(killing_norm)))
    n_null = int(np.sum(eigenvalues < AF_THRESHOLD))

    # Commutator variance
    comm_norms = np.zeros((n_h, n_h))
    for h in range(n_h):
        for hp in range(h+1, n_h):
            comm = proj_heads[h] @ proj_heads[hp] - proj_heads[hp] @ proj_heads[h]
            comm_norms[h, hp] = np.linalg.norm(comm, 'fro')
            comm_norms[hp, h] = comm_norms[h, hp]

    typical = np.mean([np.linalg.norm(A, 'fro') for A in proj_heads])
    comm_normalized = comm_norms / (typical ** 2) if typical > 0 else comm_norms
    mask = np.ones_like(comm_normalized, dtype=bool)
    np.fill_diagonal(mask, False)

    return {
        'abelian_frac': n_null / n_h,
        'comm_var': float(np.var(comm_normalized[mask])),
        'mean_comm': float(np.mean(comm_normalized[mask])),
        'ev_spread': float(eigenvalues[-1] - eigenvalues[0]),
        'eigenvalues': eigenvalues.tolist(),
        'n_null': n_null,
    }


if __name__ == '__main__':
    print("P41: Killing Form Evolution Through Pretraining")
    print(f"Model: {MODEL_BASE}")
    print(f"Checkpoints: {CHECKPOINTS}")
    print("=" * 70)

    all_results = {}

    for ckpt in CHECKPOINTS:
        print(f"\n{'='*70}")
        print(f"Checkpoint: {ckpt}")
        print(f"{'='*70}")

        t0 = time.time()
        rev = ckpt if ckpt != 'step143000' else None  # main branch = fully trained
        layer_heads, n_heads, d_model, n_layers, d_head = extract_q_heads_pythia(
            MODEL_BASE, revision=rev)
        print(f"  Loaded: {n_heads} heads, {n_layers} layers, d_head={d_head} ({time.time()-t0:.1f}s)")

        # Same projection for all checkpoints
        np.random.seed(SEED)
        p_out = np.random.randn(PROJ_DIM, d_head) / np.sqrt(d_head)
        p_in = np.random.randn(d_model, PROJ_DIM) / np.sqrt(d_model)
        proj = (p_out, p_in)

        ckpt_results = {}
        t1 = time.time()
        for layer_idx in sorted(layer_heads.keys()):
            ckpt_results[layer_idx] = compute_killing_form(layer_heads[layer_idx], proj)

        # Summary stats
        af_mean = np.mean([ckpt_results[l]['abelian_frac'] for l in ckpt_results])
        cv_mean = np.mean([ckpt_results[l]['comm_var'] for l in ckpt_results])
        mc_mean = np.mean([ckpt_results[l]['mean_comm'] for l in ckpt_results])
        sp_mean = np.mean([ckpt_results[l]['ev_spread'] for l in ckpt_results])

        print(f"  AF={af_mean:.4f}, CommVar={cv_mean:.6f}, MeanComm={mc_mean:.4f}, "
              f"Spread={sp_mean:.4f} ({time.time()-t1:.1f}s)")

        all_results[ckpt] = {
            'per_layer': {str(k): v for k, v in ckpt_results.items()},
            'summary': {
                'af_mean': float(af_mean),
                'comm_var_mean': float(cv_mean),
                'mean_comm': float(mc_mean),
                'ev_spread_mean': float(sp_mean),
            }
        }

    # ============================================================
    # TRAINING TRAJECTORY
    # ============================================================
    print(f"\n{'='*70}")
    print("KILLING FORM EVOLUTION THROUGH PRETRAINING")
    print(f"{'='*70}\n")

    print(f"{'Checkpoint':<12} {'AF':>8} {'CommVar':>12} {'MeanComm':>10} {'Spread':>10}")
    print("-" * 56)
    for ckpt in CHECKPOINTS:
        s = all_results[ckpt]['summary']
        print(f"{ckpt:<12} {s['af_mean']:>8.4f} {s['comm_var_mean']:>12.6f} "
              f"{s['mean_comm']:>10.4f} {s['ev_spread_mean']:>10.4f}")

    # Test for monotonic trend
    af_values = [all_results[ckpt]['summary']['af_mean'] for ckpt in CHECKPOINTS]
    cv_values = [all_results[ckpt]['summary']['comm_var_mean'] for ckpt in CHECKPOINTS]
    steps = list(range(len(CHECKPOINTS)))

    r_af, p_af = stats.spearmanr(steps, af_values)
    r_cv, p_cv = stats.spearmanr(steps, cv_values)

    print(f"\nMonotonic trend (Spearman):")
    print(f"  AF vs training progress: r={r_af:+.3f}, p={p_af:.4f}")
    print(f"  CommVar vs training progress: r={r_cv:+.3f}, p={p_cv:.4f}")

    # Layer depth profile at each checkpoint
    print(f"\n{'='*70}")
    print("LAYER DEPTH PROFILE AT EACH CHECKPOINT")
    print(f"{'='*70}\n")

    for ckpt in [CHECKPOINTS[0], CHECKPOINTS[-1]]:
        per_layer = all_results[ckpt]['per_layer']
        layers = sorted(per_layer.keys(), key=int)
        af_vals = [per_layer[l]['abelian_frac'] for l in layers]
        r, p = stats.spearmanr(list(range(len(layers))), af_vals)
        print(f"{ckpt}: AF vs depth r={r:+.3f}, p={p:.4f}")
        # Show first/last 3 layers
        for l in layers[:3] + ['...'] + layers[-3:]:
            if l == '...':
                print(f"    ...")
            else:
                print(f"    L{l:>2}: AF={per_layer[l]['abelian_frac']:.3f}")

    # Save
    with open('p41_pretraining_results.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f"\nResults saved to p41_pretraining_results.json")
