"""
Bridge #71 -- P26: Base vs RLHF Killing Form Comparison
Direct test: Does RLHF increase the Abelian fraction?

Uses matched pair: Qwen2.5-0.5B (base) vs Qwen2.5-0.5B-Instruct (RLHF'd)
Same architecture, same size, same pre-training — only difference is alignment.

PREDICTION: f_Abelian(Instruct) > f_Abelian(Base)
  RLHF sediments some head interactions -> more Abelian directions emerge.

Run on RTX 5080 via WSL/CUDA.

Author: Clawd
Date: April 9, 2026
"""

import torch
import numpy as np
from huggingface_hub import hf_hub_download
from safetensors.torch import load_file
import json
from scipy import stats
import glob
import os

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Device: {device}, GPU: {torch.cuda.get_device_name(0) if device == 'cuda' else 'N/A'}")
print()

def load_model_weights(model_name):
    """Load model weights directly via safetensors."""
    config_path = hf_hub_download(model_name, "config.json")
    with open(config_path) as f:
        config = json.load(f)

    # Try safetensors first, then bin
    try:
        # Check for sharded safetensors
        idx_path = hf_hub_download(model_name, "model.safetensors.index.json")
        with open(idx_path) as f:
            idx = json.load(f)
        # Download all shard files
        shard_files = set(idx["weight_map"].values())
        state_dict = {}
        for shard in shard_files:
            shard_path = hf_hub_download(model_name, shard)
            state_dict.update(load_file(shard_path))
    except Exception:
        try:
            weights_path = hf_hub_download(model_name, "model.safetensors")
            state_dict = load_file(weights_path)
        except Exception:
            weights_path = hf_hub_download(model_name, "pytorch_model.bin")
            state_dict = torch.load(weights_path, map_location="cpu")

    return config, state_dict


def extract_qk_and_compute(config, state_dict, model_name):
    """Extract Q/K matrices and compute Killing form per layer."""
    n_heads = config["num_attention_heads"]
    n_kv_heads = config.get("num_key_value_heads", n_heads)
    d_model = config["hidden_size"]
    n_layers = config["num_hidden_layers"]
    d_head = d_model // n_heads
    d_kv_head = d_head  # KV heads use same per-head dim as Q heads

    print(f"  {model_name}: {n_heads} heads ({n_kv_heads} KV), d={d_model}, "
          f"layers={n_layers}, d_head={d_head}")

    # Find Q and K projection keys
    # Qwen2 pattern: model.layers.{i}.self_attn.q_proj.weight
    q_keys = sorted([k for k in state_dict if 'q_proj.weight' in k])
    k_keys = sorted([k for k in state_dict if 'k_proj.weight' in k])

    if not q_keys:
        # Try other patterns
        q_keys = sorted([k for k in state_dict if '.query.' in k or 'q_attn' in k])
        k_keys = sorted([k for k in state_dict if '.key.' in k or 'k_attn' in k])

    print(f"  Found {len(q_keys)} Q projections, {len(k_keys)} K projections")
    if q_keys:
        print(f"  Sample Q key: {q_keys[0]} shape={state_dict[q_keys[0]].shape}")
    if k_keys:
        print(f"  Sample K key: {k_keys[0]} shape={state_dict[k_keys[0]].shape}")

    # Projection for efficiency
    proj_dim = 64
    np.random.seed(71)
    P = np.random.randn(d_model, proj_dim) / np.sqrt(d_model)

    results = {}

    for layer_idx in range(min(len(q_keys), len(k_keys))):
        W_Q_full = state_dict[q_keys[layer_idx]].float().numpy()
        W_K_full = state_dict[k_keys[layer_idx]].float().numpy()

        # Reshape: (n_heads * d_head, d_model) -> per-head
        # Q: (n_heads * d_head, d_model)
        try:
            W_Q_heads = W_Q_full.reshape(n_heads, d_head, d_model)
        except ValueError:
            W_Q_heads = W_Q_full.T.reshape(n_heads, d_head, d_model)

        # K: (n_kv_heads * d_kv_head, d_model)
        try:
            W_K_heads = W_K_full.reshape(n_kv_heads, d_kv_head, d_model)
        except ValueError:
            W_K_heads = W_K_full.T.reshape(n_kv_heads, d_kv_head, d_model)

        # GQA: repeat K heads
        if n_kv_heads < n_heads:
            repeat_factor = n_heads // n_kv_heads
            W_K_heads = np.repeat(W_K_heads, repeat_factor, axis=0)

        # Compute per-head QK^T and project
        proj_heads = []
        for h in range(n_heads):
            A_h = W_Q_heads[h].T @ W_K_heads[h]  # (d_model, d_model)
            proj_heads.append(P.T @ A_h @ P)      # (proj_dim, proj_dim)

        # Commutator norms
        n_h = len(proj_heads)
        comm_norms = np.zeros((n_h, n_h))
        for h in range(n_h):
            for hp in range(h+1, n_h):
                comm = proj_heads[h] @ proj_heads[hp] - proj_heads[hp] @ proj_heads[h]
                norm = np.linalg.norm(comm, 'fro')
                comm_norms[h, hp] = norm
                comm_norms[hp, h] = norm

        typical = np.mean([np.linalg.norm(A, 'fro') for A in proj_heads])
        if typical > 0:
            comm_normalized = comm_norms / (typical ** 2)
        else:
            comm_normalized = comm_norms

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

        mask = np.ones_like(comm_normalized, dtype=bool)
        np.fill_diagonal(mask, False)
        mean_comm = float(np.mean(comm_normalized[mask]))
        comm_var = float(np.var(comm_normalized[mask]))

        results[layer_idx] = {
            'mean_comm': mean_comm,
            'comm_var': comm_var,
            'eigenvalues': eigenvalues.tolist(),
            'ev_min': float(eigenvalues[0]),
            'ev_spread': float(eigenvalues[-1] - eigenvalues[0]),
            'n_null_5': int(np.sum(eigenvalues < 0.05)),
            'n_null_10': int(np.sum(eigenvalues < 0.10)),
            'n_null_20': int(np.sum(eigenvalues < 0.20)),
            'af_5': float(np.sum(eigenvalues < 0.05)) / n_h,
            'af_10': float(np.sum(eigenvalues < 0.10)) / n_h,
            'af_20': float(np.sum(eigenvalues < 0.20)) / n_h,
            'killing_trace': float(np.trace(killing_norm)),
        }

    return results, n_heads, n_layers


# ============================================================
# LOAD AND ANALYZE BOTH MODELS
# ============================================================

models = {
    "Qwen2.5-0.5B (base)": "Qwen/Qwen2.5-0.5B",
    "Qwen2.5-0.5B-Instruct (RLHF)": "Qwen/Qwen2.5-0.5B-Instruct",
}

all_results = {}

for label, model_name in models.items():
    print("=" * 70)
    print(f"Loading: {label}")
    print("=" * 70)
    config, state_dict = load_model_weights(model_name)
    results, n_heads, n_layers = extract_qk_and_compute(config, state_dict, label)
    all_results[label] = results
    print(f"  Computed Killing forms for {len(results)} layers")
    print()

# ============================================================
# COMPARISON
# ============================================================

print("=" * 70)
print("P26: BASE vs RLHF COMPARISON")
print("=" * 70)
print()

base_label = "Qwen2.5-0.5B (base)"
rlhf_label = "Qwen2.5-0.5B-Instruct (RLHF)"

base_res = all_results[base_label]
rlhf_res = all_results[rlhf_label]

# Per-layer comparison
print(f"{'Layer':>5} | {'Base AF(10%)':>12} {'RLHF AF(10%)':>13} {'Diff':>8} | "
      f"{'Base Comm':>10} {'RLHF Comm':>10} {'Diff':>8} | "
      f"{'Base Spread':>11} {'RLHF Spread':>12}")
print("-" * 110)

layers = sorted(set(base_res.keys()) & set(rlhf_res.keys()))
for l in layers:
    b, r = base_res[l], rlhf_res[l]
    print(f"{l:>5} | {b['af_10']:>12.4f} {r['af_10']:>13.4f} {r['af_10']-b['af_10']:>+8.4f} | "
          f"{b['mean_comm']:>10.5f} {r['mean_comm']:>10.5f} {r['mean_comm']-b['mean_comm']:>+8.5f} | "
          f"{b['ev_spread']:>11.4f} {r['ev_spread']:>12.4f}")

print()

# Aggregate comparison
metrics = ['af_5', 'af_10', 'af_20', 'mean_comm', 'comm_var', 'ev_min', 'ev_spread']
print(f"{'Metric':<15} {'Base (mean)':>12} {'RLHF (mean)':>12} {'Diff':>10} {'t-stat':>8} {'p-value':>8}")
print("-" * 70)

for m in metrics:
    base_vals = [base_res[l][m] for l in layers]
    rlhf_vals = [rlhf_res[l][m] for l in layers]
    b_mean = np.mean(base_vals)
    r_mean = np.mean(rlhf_vals)
    diff = r_mean - b_mean

    # Paired t-test (same layers, different model)
    t_stat, p_val = stats.ttest_rel(base_vals, rlhf_vals)
    print(f"{m:<15} {b_mean:>12.5f} {r_mean:>12.5f} {diff:>+10.5f} {t_stat:>8.3f} {p_val:>8.4f}")

print()

# Key P26 test
base_af = np.mean([base_res[l]['af_10'] for l in layers])
rlhf_af = np.mean([rlhf_res[l]['af_10'] for l in layers])
af_vals_base = [base_res[l]['af_10'] for l in layers]
af_vals_rlhf = [rlhf_res[l]['af_10'] for l in layers]
t_af, p_af = stats.ttest_rel(af_vals_base, af_vals_rlhf)

print("=" * 70)
print("P26 VERDICT")
print("=" * 70)
print()
print(f"PREDICTION: RLHF increases Abelian fraction")
print(f"  Base AF(10%):     {base_af:.4f}")
print(f"  RLHF AF(10%):    {rlhf_af:.4f}")
print(f"  Difference:       {rlhf_af - base_af:+.4f}")
print(f"  Paired t-test:    t={t_af:.3f}, p={p_af:.4f}")
print()

if rlhf_af > base_af and p_af < 0.05:
    print("  RESULT: **CONFIRMED** (p < 0.05)")
    print("  RLHF DOES increase the Abelian fraction.")
    print("  Alignment training sediments some head interactions,")
    print("  creating more independent (Abelian) constraint directions.")
elif rlhf_af > base_af and p_af < 0.10:
    print("  RESULT: SUGGESTIVE (p < 0.10)")
    print("  Trend in predicted direction but not significant at 5%.")
elif rlhf_af > base_af:
    print("  RESULT: INCONCLUSIVE")
    print("  Direction correct but not statistically significant.")
elif rlhf_af < base_af and p_af < 0.05:
    print("  RESULT: **REVERSED** (p < 0.05)")
    print("  RLHF DECREASES the Abelian fraction.")
    print("  Alignment training makes heads MORE interacting, not less.")
    print("  This would require rethinking the sedimentation interpretation.")
else:
    print("  RESULT: NO SIGNIFICANT DIFFERENCE")
    print("  RLHF does not measurably change the Abelian fraction.")

print()

# Additional structural comparisons
print("=" * 70)
print("ADDITIONAL: Structural Differences")
print("=" * 70)
print()

# Compare commutator variance (structural ordering)
base_cv = np.mean([base_res[l]['comm_var'] for l in layers])
rlhf_cv = np.mean([rlhf_res[l]['comm_var'] for l in layers])
cv_base_list = [base_res[l]['comm_var'] for l in layers]
cv_rlhf_list = [rlhf_res[l]['comm_var'] for l in layers]
t_cv, p_cv = stats.ttest_rel(cv_base_list, cv_rlhf_list)

print(f"Commutator variance (head differentiation):")
print(f"  Base:  {base_cv:.6f}")
print(f"  RLHF:  {rlhf_cv:.6f}")
print(f"  Diff:  {rlhf_cv - base_cv:+.6f} (t={t_cv:.3f}, p={p_cv:.4f})")
if rlhf_cv > base_cv:
    print(f"  RLHF has MORE differentiated heads (more structured)")
else:
    print(f"  RLHF has LESS differentiated heads (more uniform)")
print()

# Layer-depth interaction
print("=" * 70)
print("LAYER-DEPTH x RLHF INTERACTION")
print("=" * 70)
print()

print("Does RLHF affect early and late layers differently?")
mid = len(layers) // 2
early_layers = layers[:mid]
late_layers = layers[mid:]

for phase, phase_layers in [("Early (0-11)", early_layers), ("Late (12-23)", late_layers)]:
    b_af = np.mean([base_res[l]['af_10'] for l in phase_layers])
    r_af = np.mean([rlhf_res[l]['af_10'] for l in phase_layers])
    b_mc = np.mean([base_res[l]['mean_comm'] for l in phase_layers])
    r_mc = np.mean([rlhf_res[l]['mean_comm'] for l in phase_layers])
    print(f"  {phase}:")
    print(f"    AF(10%): base={b_af:.4f}, rlhf={r_af:.4f}, diff={r_af-b_af:+.4f}")
    print(f"    MeanComm: base={b_mc:.5f}, rlhf={r_mc:.5f}, diff={r_mc-b_mc:+.5f}")
print()

# Eigenvalue spectra comparison
print("=" * 70)
print("EIGENVALUE SPECTRA COMPARISON (selected layers)")
print("=" * 70)
print()

for l in [0, len(layers)//4, len(layers)//2, 3*len(layers)//4, layers[-1]]:
    if l in base_res and l in rlhf_res:
        b_evs = " ".join([f"{e:.3f}" for e in base_res[l]['eigenvalues']])
        r_evs = " ".join([f"{e:.3f}" for e in rlhf_res[l]['eigenvalues']])
        print(f"  Layer {l:2d} Base:  [{b_evs}]")
        print(f"  Layer {l:2d} RLHF:  [{r_evs}]")
        print()

# ============================================================
# SUMMARY
# ============================================================
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print()
print("Model pair: Qwen2.5-0.5B (base) vs Qwen2.5-0.5B-Instruct (RLHF)")
print(f"Architecture: 14 heads (2 KV), d=896, 24 layers")
print()
print(f"P26 (RLHF increases Abelian fraction):")
print(f"  Base AF(10%): {base_af:.4f}, RLHF AF(10%): {rlhf_af:.4f}")
print(f"  t={t_af:.3f}, p={p_af:.4f}")
print()
print("This is the FIRST direct comparison of attention Killing forms")
print("between a base model and its RLHF variant.")
print("The constraint lattice formalism makes a specific, falsifiable")
print("prediction about the effect of alignment training on the")
print("non-commutative structure of attention — and this test measures it.")
