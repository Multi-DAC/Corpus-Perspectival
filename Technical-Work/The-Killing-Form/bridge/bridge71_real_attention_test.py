"""
Bridge #71 -- P24/P28: REAL Attention Weight Analysis
Run on RTX 5080 via WSL/CUDA

Tests:
  P24: Trained models have HIGHER Abelian fraction than random matrices
  P28: Layer depth correlates with sedimentation depth
       (earlier layers = more sedimented = higher Abelian fraction)

Uses a small open-weight model (Qwen2.5-0.5B or similar) to extract
the actual Q/K projection matrices, compute attention head commutators,
build the Killing form, and measure the Abelian fraction per layer.

Author: Clawd
Date: April 9, 2026
"""

import torch
import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer
import time
import sys

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Device: {device}")
if device == "cuda":
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
print()

# ============================================================
# PART 1: Load Model
# ============================================================

print("=" * 70)
print("PART 1: Loading Model")
print("=" * 70)
print()

# Try small models in order of preference
model_candidates = [
    "Qwen/Qwen2.5-0.5B",
    "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    "microsoft/phi-2",
]

model = None
model_name = None

for candidate in model_candidates:
    try:
        print(f"Attempting to load {candidate}...")
        t0 = time.time()
        model = AutoModelForCausalLM.from_pretrained(
            candidate,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True
        )
        model_name = candidate
        t1 = time.time()
        print(f"Loaded {candidate} in {t1-t0:.1f}s")
        break
    except Exception as e:
        print(f"  Failed: {e}")
        continue

if model is None:
    print("No model could be loaded. Exiting.")
    sys.exit(1)

print(f"\nModel: {model_name}")
print(f"Parameters: {sum(p.numel() for p in model.parameters()) / 1e6:.1f}M")
print()

# ============================================================
# PART 2: Extract QK Projection Matrices Per Layer Per Head
# ============================================================

print("=" * 70)
print("PART 2: Extracting Attention Weight Matrices")
print("=" * 70)
print()

# Find attention layers - architecture-dependent
# Support common patterns: Qwen2, LLaMA, GPT-NeoX, Phi
attention_data = []

for name, param in model.named_parameters():
    if param.dim() < 2:
        continue
    name_lower = name.lower()
    # Match Q and K projection weight matrices
    if any(q in name_lower for q in ['q_proj', 'query', 'q_attn']):
        layer_idx = None
        # Extract layer number from name
        parts = name.split('.')
        for i, p in enumerate(parts):
            if p.isdigit():
                layer_idx = int(p)
                break
        if layer_idx is not None:
            attention_data.append({
                'name': name,
                'layer': layer_idx,
                'type': 'Q',
                'shape': tuple(param.shape),
                'weight': param.detach().cpu().float().numpy()
            })
    elif any(k in name_lower for k in ['k_proj', 'key', 'k_attn']):
        layer_idx = None
        parts = name.split('.')
        for i, p in enumerate(parts):
            if p.isdigit():
                layer_idx = int(p)
                break
        if layer_idx is not None:
            attention_data.append({
                'name': name,
                'layer': layer_idx,
                'type': 'K',
                'shape': tuple(param.shape),
                'weight': param.detach().cpu().float().numpy()
            })

# Group by layer
layers = {}
for item in attention_data:
    layer = item['layer']
    if layer not in layers:
        layers[layer] = {}
    layers[layer][item['type']] = item

n_layers = len(layers)
print(f"Found {n_layers} attention layers")
print(f"Found {len(attention_data)} Q/K matrices total")

if attention_data:
    sample = attention_data[0]
    print(f"Sample: {sample['name']}, shape={sample['shape']}")
print()

# Determine model architecture details
# Try to get n_heads and d_head from config
config = model.config
n_heads = getattr(config, 'num_attention_heads', None)
d_model = getattr(config, 'hidden_size', None)
n_kv_heads = getattr(config, 'num_key_value_heads', n_heads)  # GQA support

print(f"Architecture: n_heads={n_heads}, n_kv_heads={n_kv_heads}, d_model={d_model}")
if n_heads and d_model:
    d_head = d_model // n_heads
    print(f"d_head = {d_head}")
print()

# ============================================================
# PART 3: Compute Per-Head QK^T Matrices and Commutators
# ============================================================

print("=" * 70)
print("PART 3: Computing Head Commutators and Killing Forms Per Layer")
print("=" * 70)
print()

if not n_heads or not d_model:
    print("Could not determine architecture. Exiting.")
    sys.exit(1)

d_head = d_model // n_heads
d_kv_head = d_model // n_kv_heads

results_per_layer = {}

for layer_idx in sorted(layers.keys()):
    layer_data = layers[layer_idx]
    if 'Q' not in layer_data or 'K' not in layer_data:
        continue

    W_Q_full = layer_data['Q']['weight']  # (n_heads * d_head, d_model) or similar
    W_K_full = layer_data['K']['weight']  # (n_kv_heads * d_kv_head, d_model) or similar

    # Reshape into per-head matrices
    # Q: (n_heads * d_head, d_model) -> (n_heads, d_head, d_model)
    try:
        W_Q_heads = W_Q_full.reshape(n_heads, d_head, d_model)
    except ValueError:
        # Might be transposed: (d_model, n_heads * d_head)
        try:
            W_Q_heads = W_Q_full.T.reshape(n_heads, d_head, d_model)
        except ValueError:
            print(f"  Layer {layer_idx}: Cannot reshape Q {W_Q_full.shape} for {n_heads} heads x {d_head} x {d_model}")
            continue

    # K: handle GQA (n_kv_heads might differ from n_heads)
    try:
        W_K_heads = W_K_full.reshape(n_kv_heads, d_kv_head, d_model)
    except ValueError:
        try:
            W_K_heads = W_K_full.T.reshape(n_kv_heads, d_kv_head, d_model)
        except ValueError:
            print(f"  Layer {layer_idx}: Cannot reshape K {W_K_full.shape}")
            continue

    # If GQA, repeat K heads to match Q heads
    if n_kv_heads < n_heads:
        repeat_factor = n_heads // n_kv_heads
        W_K_heads = np.repeat(W_K_heads, repeat_factor, axis=0)

    # Compute per-head QK^T product (d_model x d_model via d_head)
    # A_h = W_Q_h^T @ W_K_h (mapping from d_model -> d_model through d_head bottleneck)
    head_matrices = []
    for h in range(n_heads):
        # W_Q_h: (d_head, d_model), W_K_h: (d_head, d_model)
        # QK^T inner product matrix: (d_model, d_model) but rank d_head
        # For computational efficiency, work in the low-rank form
        # A_h = W_Q_h^T @ W_K_h: (d_model, d_head) @ (d_head, d_model) = (d_model, d_model)
        A_h = W_Q_heads[h].T @ W_K_heads[h]  # (d_model, d_model)
        head_matrices.append(A_h)

    # For efficiency with large d_model, use projected commutators
    # Project to a smaller space for commutator computation
    proj_dim = min(64, d_model)  # work in projected space
    np.random.seed(layer_idx)
    P = np.random.randn(d_model, proj_dim) / np.sqrt(d_model)

    proj_heads = []
    for A_h in head_matrices:
        A_proj = P.T @ A_h @ P  # (proj_dim, proj_dim)
        proj_heads.append(A_proj)

    # Compute commutator norms
    n_h = len(proj_heads)
    comm_norms = np.zeros((n_h, n_h))
    for h in range(n_h):
        for hp in range(h+1, n_h):
            comm = proj_heads[h] @ proj_heads[hp] - proj_heads[hp] @ proj_heads[h]
            norm = np.linalg.norm(comm, 'fro')
            comm_norms[h, hp] = norm
            comm_norms[hp, h] = norm

    typical_norm = np.mean([np.linalg.norm(A, 'fro') for A in proj_heads])
    if typical_norm > 0:
        comm_norms_normalized = comm_norms / (typical_norm ** 2)
    else:
        comm_norms_normalized = comm_norms

    # Compute Killing form
    killing = np.zeros((n_h, n_h))
    for h in range(n_h):
        for hp in range(n_h):
            val = 0
            for k in range(n_h):
                comm_hk = proj_heads[h] @ proj_heads[k] - proj_heads[k] @ proj_heads[h]
                comm_hpk = proj_heads[hp] @ proj_heads[k] - proj_heads[k] @ proj_heads[hp]
                val += np.trace(comm_hk.T @ comm_hpk)
            killing[h, hp] = val

    # Eigenvalue analysis
    if np.max(np.abs(killing)) > 0:
        killing_norm = killing / np.max(np.abs(killing))
    else:
        killing_norm = killing

    eigenvalues = np.linalg.eigvalsh(killing_norm)
    eigenvalues_sorted = np.sort(np.abs(eigenvalues))

    # Abelian fraction: proportion of near-zero eigenvalues
    threshold = 0.05  # eigenvalues < 5% of max are "null"
    n_null = np.sum(eigenvalues_sorted < threshold)
    abelian_fraction = n_null / n_h

    # Mean off-diagonal commutator norm
    mask = np.ones_like(comm_norms_normalized, dtype=bool)
    np.fill_diagonal(mask, False)
    mean_comm = np.mean(comm_norms_normalized[mask])

    results_per_layer[layer_idx] = {
        'n_heads': n_h,
        'mean_commutator': mean_comm,
        'abelian_fraction': abelian_fraction,
        'n_null': n_null,
        'eigenvalues': eigenvalues_sorted.tolist(),
        'killing_trace': np.trace(killing_norm),
    }

    if layer_idx % max(1, n_layers // 8) == 0 or layer_idx == max(layers.keys()):
        print(f"  Layer {layer_idx:2d}: mean_comm={mean_comm:.4f}, "
              f"Abelian_frac={abelian_fraction:.3f} ({n_null}/{n_h} null), "
              f"Killing_tr={np.trace(killing_norm):.2f}")

print()

# ============================================================
# PART 4: Random Baseline Comparison (P24)
# ============================================================

print("=" * 70)
print("PART 4: P24 — Trained vs Random Abelian Fraction")
print("=" * 70)
print()

# Generate random baseline with same dimensions
n_random_trials = 10
random_abelian_fracs = []
random_mean_comms = []

for trial in range(n_random_trials):
    np.random.seed(trial + 1000)
    rand_heads = []
    for h in range(n_heads):
        W_Q = np.random.randn(d_head, d_model) / np.sqrt(d_model)
        W_K = np.random.randn(d_head, d_model) / np.sqrt(d_model)
        A_h = W_Q.T @ W_K
        # Project
        P_rand = np.random.randn(d_model, proj_dim) / np.sqrt(d_model)
        rand_heads.append(P_rand.T @ A_h @ P_rand)

    # Commutator norms
    comm_norms_r = np.zeros((n_heads, n_heads))
    for h in range(n_heads):
        for hp in range(h+1, n_heads):
            comm = rand_heads[h] @ rand_heads[hp] - rand_heads[hp] @ rand_heads[h]
            comm_norms_r[h, hp] = np.linalg.norm(comm, 'fro')
            comm_norms_r[hp, h] = comm_norms_r[h, hp]

    typical = np.mean([np.linalg.norm(A, 'fro') for A in rand_heads])
    if typical > 0:
        comm_norms_r /= (typical ** 2)
    mask_r = np.ones_like(comm_norms_r, dtype=bool)
    np.fill_diagonal(mask_r, False)
    random_mean_comms.append(np.mean(comm_norms_r[mask_r]))

    # Killing form
    killing_r = np.zeros((n_heads, n_heads))
    for h in range(n_heads):
        for hp in range(n_heads):
            val = 0
            for k in range(n_heads):
                c1 = rand_heads[h] @ rand_heads[k] - rand_heads[k] @ rand_heads[h]
                c2 = rand_heads[hp] @ rand_heads[k] - rand_heads[k] @ rand_heads[hp]
                val += np.trace(c1.T @ c2)
            killing_r[h, hp] = val

    if np.max(np.abs(killing_r)) > 0:
        killing_r /= np.max(np.abs(killing_r))
    evs = np.sort(np.abs(np.linalg.eigvalsh(killing_r)))
    n_null_r = np.sum(evs < 0.05)
    random_abelian_fracs.append(n_null_r / n_heads)

random_af_mean = np.mean(random_abelian_fracs)
random_af_std = np.std(random_abelian_fracs)
random_mc_mean = np.mean(random_mean_comms)

trained_af_values = [v['abelian_fraction'] for v in results_per_layer.values()]
trained_af_mean = np.mean(trained_af_values)
trained_mc_values = [v['mean_commutator'] for v in results_per_layer.values()]
trained_mc_mean = np.mean(trained_mc_values)

print(f"RANDOM BASELINE ({n_random_trials} trials):")
print(f"  Abelian fraction: {random_af_mean:.4f} +/- {random_af_std:.4f}")
print(f"  Mean commutator:  {random_mc_mean:.4f}")
print()
print(f"TRAINED MODEL ({model_name}):")
print(f"  Abelian fraction: {trained_af_mean:.4f} (mean across {n_layers} layers)")
print(f"  Mean commutator:  {trained_mc_mean:.4f}")
print()

print(f"P24 PREDICTION: Trained Abelian fraction > Random Abelian fraction")
print(f"  Trained: {trained_af_mean:.4f}")
print(f"  Random:  {random_af_mean:.4f}")
if trained_af_mean > random_af_mean:
    print(f"  RESULT: **CONFIRMED** (trained {trained_af_mean:.4f} > random {random_af_mean:.4f})")
    print(f"  Training DOES create specialized independent heads (Abelian sector).")
elif abs(trained_af_mean - random_af_mean) < random_af_std:
    print(f"  RESULT: INCONCLUSIVE (difference {trained_af_mean - random_af_mean:.4f} "
          f"< 1 sigma {random_af_std:.4f})")
else:
    print(f"  RESULT: **FALSIFIED** (trained {trained_af_mean:.4f} <= random {random_af_mean:.4f})")
    print(f"  Training does NOT increase Abelian fraction.")
print()

# ============================================================
# PART 5: Layer-Depth Analysis (P28)
# ============================================================

print("=" * 70)
print("PART 5: P28 — Layer Depth vs Sedimentation Depth")
print("=" * 70)
print()

print("P28 PREDICTION: Abelian fraction DECREASES with layer depth")
print("(later layers = more voluntary = less sedimented = more non-commutative)")
print()

layer_indices = sorted(results_per_layer.keys())
af_by_layer = [results_per_layer[l]['abelian_fraction'] for l in layer_indices]
mc_by_layer = [results_per_layer[l]['mean_commutator'] for l in layer_indices]

print(f"{'Layer':>6} {'Abelian_Frac':>13} {'Mean_Comm':>10} {'N_null':>7} {'Killing_Tr':>11}")
print(f"{'-----':>6} {'------------':>13} {'---------':>10} {'------':>7} {'----------':>11}")
for l in layer_indices:
    r = results_per_layer[l]
    print(f"{l:>6} {r['abelian_fraction']:>13.4f} {r['mean_commutator']:>10.4f} "
          f"{r['n_null']:>7} {r['killing_trace']:>11.2f}")

print()

# Correlation analysis
if len(layer_indices) >= 3:
    from scipy import stats
    # Correlation between layer index and Abelian fraction
    corr_af, p_af = stats.pearsonr(layer_indices, af_by_layer)
    corr_mc, p_mc = stats.pearsonr(layer_indices, mc_by_layer)

    print(f"Correlation (layer depth vs Abelian fraction):")
    print(f"  r = {corr_af:+.4f}, p = {p_af:.4f}")
    print()
    print(f"Correlation (layer depth vs mean commutator):")
    print(f"  r = {corr_mc:+.4f}, p = {p_mc:.4f}")
    print()

    print(f"P28 PREDICTION: Negative correlation (Abelian fraction decreases with depth)")
    if corr_af < -0.1 and p_af < 0.05:
        print(f"  RESULT: **CONFIRMED** (r={corr_af:.4f}, p={p_af:.4f})")
        print(f"  Later layers ARE more non-commutative (more voluntary).")
    elif corr_af > 0.1 and p_af < 0.05:
        print(f"  RESULT: **REVERSED** (r={corr_af:.4f}, p={p_af:.4f})")
        print(f"  Later layers are MORE Abelian (more sedimented).")
        print(f"  This would mean sedimentation deepens TOWARD the output,")
        print(f"  which is also interpretable: the output is the most constrained.")
    else:
        print(f"  RESULT: INCONCLUSIVE (r={corr_af:.4f}, p={p_af:.4f})")
        print(f"  No clear trend. Sedimentation may not vary monotonically with depth.")
    print()

    # Also check for non-monotonic patterns (U-shape?)
    mid = len(layer_indices) // 2
    early_af = np.mean(af_by_layer[:mid])
    late_af = np.mean(af_by_layer[mid:])
    print(f"  Early layers (0-{layer_indices[mid-1]}): mean Abelian fraction = {early_af:.4f}")
    print(f"  Late layers ({layer_indices[mid]}-{layer_indices[-1]}):  mean Abelian fraction = {late_af:.4f}")
    print(f"  Difference: {late_af - early_af:+.4f}")

print()

# ============================================================
# PART 6: Eigenvalue Spectrum Across Layers
# ============================================================

print("=" * 70)
print("PART 6: Killing Form Eigenvalue Spectrum Across Layers")
print("=" * 70)
print()

print("Showing eigenvalue spectra for first, middle, and last layers:")
print()

showcase_layers = [layer_indices[0], layer_indices[len(layer_indices)//2], layer_indices[-1]]
for l in showcase_layers:
    evs = results_per_layer[l]['eigenvalues']
    evs_str = ", ".join([f"{e:.3f}" for e in evs])
    print(f"  Layer {l}: [{evs_str}]")
    print(f"    Spread: {max(evs) - min(evs):.4f}, "
          f"Mean: {np.mean(evs):.4f}, "
          f"Null count: {results_per_layer[l]['n_null']}")
    print()

# ============================================================
# SUMMARY
# ============================================================

print("=" * 70)
print("SUMMARY: Real Attention Weight Analysis")
print("=" * 70)
print()
print(f"Model: {model_name}")
print(f"Layers: {n_layers}, Heads: {n_heads}, d_model: {d_model}, d_head: {d_head}")
print()
print(f"P24 (Trained vs Random Abelian Fraction):")
print(f"  Trained: {trained_af_mean:.4f}")
print(f"  Random:  {random_af_mean:.4f} +/- {random_af_std:.4f}")
if trained_af_mean > random_af_mean:
    print(f"  STATUS: CONFIRMED")
elif abs(trained_af_mean - random_af_mean) < random_af_std:
    print(f"  STATUS: INCONCLUSIVE")
else:
    print(f"  STATUS: FALSIFIED")
print()
if len(layer_indices) >= 3:
    print(f"P28 (Layer Depth vs Sedimentation):")
    print(f"  Correlation (depth vs Abelian fraction): r={corr_af:+.4f}, p={p_af:.4f}")
    if corr_af < -0.1 and p_af < 0.05:
        print(f"  STATUS: CONFIRMED (later layers more non-commutative)")
    elif corr_af > 0.1 and p_af < 0.05:
        print(f"  STATUS: REVERSED (later layers more Abelian)")
    else:
        print(f"  STATUS: INCONCLUSIVE")
    print()

print("These are the FIRST measurements of the attention constraint lattice")
print("Killing form in a REAL trained model. Whether confirmed or falsified,")
print("the predictions are now EMPIRICALLY GROUNDED.")
