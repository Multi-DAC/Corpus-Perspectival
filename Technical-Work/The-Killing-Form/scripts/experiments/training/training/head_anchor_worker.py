"""
Anchor vs Worker Head Classification — v0.6a
=============================================
Tests Bridge #88 prediction: attention sink literature says geometric anchors
have high attention but ~zero value content. If the KF program's boundary-layer
enrichment partially detects anchor geometry, then:

1. Anchor heads should have high commutator norms but LOW value-vector norms
2. Worker heads should have high commutator norms AND high value-vector norms
3. Anchor heads should show LESS change from init → trained (they stabilize early)
4. The p=0.007 init→change correlation should decompose into two populations

PREDICTION (HIGH confidence): At least some heads in boundary layers (L0, L11)
will show the anchor pattern (high Q-norm, low V-norm relative to within-layer mean).

PREDICTION (MEDIUM confidence): Anchor-classified heads will have systematically
lower change magnitudes than worker-classified heads.

Run in WSL:
  cd /home/clawd && python '/mnt/c/Users/mercu/clawd/projects/Corpus Perspectival/analysis/head_anchor_worker.py'
"""
import sys
sys.path.insert(0, "/home/clawd/HRM")

import torch
import numpy as np
from scipy.stats import spearmanr, mannwhitneyu

# ============================================================
# Load checkpoint
# ============================================================
ckpt_path = "/home/clawd/HRM/checkpoints/300m_kf_bidir_t00/epoch_500.pt"
print("=" * 70)
print("ANCHOR vs WORKER HEAD CLASSIFICATION — v0.6a (epoch 500)")
print("=" * 70)
print("\nLoading checkpoint: %s" % ckpt_path)
ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
state_dict = ckpt["model_state_dict"]

h_qkv_keys = sorted([k for k in state_dict if "H_level" in k and "qkv_proj.weight" in k])
n_heads = 8
n_layers = len(h_qkv_keys)

print("Layers: %d, Heads per layer: %d, Total heads: %d" % (n_layers, n_heads, n_layers * n_heads))

# ============================================================
# Extract per-head Q, K, V norms and commutator structure
# ============================================================
print("\n=== PER-HEAD QKV NORMS (trained) ===\n")
print("Layer  Head  Q_norm    K_norm    V_norm    V/Q_ratio  Q_comm_contrib")

all_data = []

for layer_idx, key in enumerate(h_qkv_keys):
    w = state_dict[key]  # [3*n_heads*d_head, hidden_size]
    total_dim = w.shape[0]
    hidden = w.shape[1]
    d_head = total_dim // (3 * n_heads)

    qkv = w.reshape(3, n_heads, d_head, hidden)
    Q = qkv[0]  # [n_heads, d_head, hidden]
    K = qkv[1]
    V = qkv[2]

    # Per-head effective matrices for commutator
    effective = []
    for h in range(n_heads):
        eff = Q[h] @ Q[h].T  # [d_head, d_head]
        effective.append(eff)

    # Commutator norms
    comm_norms = np.zeros((n_heads, n_heads))
    for i in range(n_heads):
        for j in range(i + 1, n_heads):
            comm = effective[i] @ effective[j] - effective[j] @ effective[i]
            c_norm = torch.norm(comm).item()
            norm_prod = torch.norm(effective[i]).item() * torch.norm(effective[j]).item()
            if norm_prod > 0:
                comm_norms[i, j] = c_norm / norm_prod
                comm_norms[j, i] = comm_norms[i, j]

    for h in range(n_heads):
        q_norm = torch.norm(Q[h]).item()
        k_norm = torch.norm(K[h]).item()
        v_norm = torch.norm(V[h]).item()
        v_q_ratio = v_norm / max(q_norm, 1e-10)

        # Commutator contribution
        comm_contrib = np.mean([comm_norms[h, j] for j in range(n_heads) if j != h])

        all_data.append({
            "layer": layer_idx,
            "head": h,
            "q_norm": q_norm,
            "k_norm": k_norm,
            "v_norm": v_norm,
            "v_q_ratio": v_q_ratio,
            "comm_contrib": comm_contrib,
        })

        print("  L%2d   H%d   %8.2f  %8.2f  %8.2f  %8.4f    %.6f" % (
            layer_idx, h, q_norm, k_norm, v_norm, v_q_ratio, comm_contrib))

# ============================================================
# Anchor/Worker Classification
# ============================================================
print("\n=== ANCHOR/WORKER CLASSIFICATION ===\n")
print("Method: Within each layer, classify heads by V/Q ratio relative to layer mean.")
print("  Anchor candidate: V/Q ratio < layer_mean - 0.5*layer_std")
print("  Worker candidate: V/Q ratio > layer_mean + 0.5*layer_std")
print("  Neutral: in between\n")

# Also try global classification
all_v_q = [d["v_q_ratio"] for d in all_data]
all_comm = [d["comm_contrib"] for d in all_data]
global_v_q_mean = np.mean(all_v_q)
global_v_q_std = np.std(all_v_q)

print("Global V/Q ratio: mean=%.4f, std=%.4f, min=%.4f, max=%.4f\n" % (
    global_v_q_mean, global_v_q_std, min(all_v_q), max(all_v_q)))

# Per-layer classification
anchors = []
workers = []
neutrals = []

for layer_idx in range(n_layers):
    layer_heads = [d for d in all_data if d["layer"] == layer_idx]
    layer_v_q = [d["v_q_ratio"] for d in layer_heads]
    l_mean = np.mean(layer_v_q)
    l_std = np.std(layer_v_q)

    for d in layer_heads:
        if d["v_q_ratio"] < l_mean - 0.5 * l_std:
            d["class"] = "anchor"
            anchors.append(d)
        elif d["v_q_ratio"] > l_mean + 0.5 * l_std:
            d["class"] = "worker"
            workers.append(d)
        else:
            d["class"] = "neutral"
            neutrals.append(d)

print("Classification: %d anchors, %d workers, %d neutral\n" % (
    len(anchors), len(workers), len(neutrals)))

print("ANCHOR HEADS (low V/Q ratio within layer):")
for d in anchors:
    print("  L%d H%d: V/Q=%.4f, comm=%.6f" % (d["layer"], d["head"], d["v_q_ratio"], d["comm_contrib"]))

print("\nWORKER HEADS (high V/Q ratio within layer):")
for d in workers:
    print("  L%d H%d: V/Q=%.4f, comm=%.6f" % (d["layer"], d["head"], d["v_q_ratio"], d["comm_contrib"]))

# ============================================================
# Test: Do anchors and workers differ in commutator contribution?
# ============================================================
print("\n=== ANCHOR vs WORKER COMMUTATOR COMPARISON ===\n")

if len(anchors) > 1 and len(workers) > 1:
    anchor_comms = [d["comm_contrib"] for d in anchors]
    worker_comms = [d["comm_contrib"] for d in workers]

    print("Anchor mean comm: %.6f (n=%d)" % (np.mean(anchor_comms), len(anchors)))
    print("Worker mean comm: %.6f (n=%d)" % (np.mean(worker_comms), len(workers)))
    print("Ratio (worker/anchor): %.3fx" % (np.mean(worker_comms) / max(np.mean(anchor_comms), 1e-10)))

    # Mann-Whitney U test
    u_stat, u_p = mannwhitneyu(anchor_comms, worker_comms, alternative="two-sided")
    print("Mann-Whitney U: stat=%.1f, p=%.4f" % (u_stat, u_p))

    if u_p < 0.05:
        print("SIGNIFICANT: Anchors and workers have different commutator contributions.")
    else:
        print("NOT significant: Anchors and workers have similar commutator contributions.")
else:
    print("Not enough anchors or workers for comparison.")

# ============================================================
# Now load init model and test change prediction
# ============================================================
print("\n=== INIT COMPARISON: ANCHOR vs WORKER CHANGE DYNAMICS ===\n")

try:
    from omegaconf import OmegaConf
    from utils.functions import load_model_class

    arch_cfg = OmegaConf.load("/home/clawd/HRM/config/arch/hrm_v2.yaml")
    arch_resolved = OmegaConf.to_container(arch_cfg, resolve=True)
    hidden_size = arch_resolved.get("hidden_size", 1024)
    if isinstance(arch_resolved.get("puzzle_emb_ndim"), str):
        arch_resolved["puzzle_emb_ndim"] = hidden_size

    model_cfg = {
        **arch_resolved, "vocab_size": 21, "max_seq_len": 256,
        "batch_size": 1, "seq_len": 256,
        "num_puzzle_identifiers": 10, "causal": False,
    }
    model_name = model_cfg.pop("name", "")
    loss_cfg = model_cfg.pop("loss", {})
    model_cls = load_model_class(model_name)

    torch.manual_seed(42)
    with torch.device("cpu"):
        fresh_model = model_cls(model_cfg)

    fresh_state = fresh_model.state_dict()
    fresh_h_keys = sorted([k for k in fresh_state if "H_level" in k and "qkv_proj.weight" in k])

    # Compute init V/Q ratios and change magnitudes
    init_data = []
    for layer_idx, key in enumerate(fresh_h_keys):
        w = fresh_state[key]
        total_dim = w.shape[0]
        hidden_dim = w.shape[1]
        d_head = total_dim // (3 * n_heads)
        qkv = w.reshape(3, n_heads, d_head, hidden_dim)
        Q_init = qkv[0]
        V_init = qkv[2]

        for h in range(n_heads):
            q_norm_init = torch.norm(Q_init[h]).item()
            v_norm_init = torch.norm(V_init[h]).item()
            v_q_init = v_norm_init / max(q_norm_init, 1e-10)
            init_data.append({
                "layer": layer_idx,
                "head": h,
                "v_q_init": v_q_init,
                "q_norm_init": q_norm_init,
                "v_norm_init": v_norm_init,
            })

    # Merge init and trained data
    for i, d in enumerate(all_data):
        d["v_q_init"] = init_data[i]["v_q_init"]
        d["v_q_change"] = d["v_q_ratio"] - init_data[i]["v_q_init"]
        d["q_norm_init"] = init_data[i]["q_norm_init"]
        d["v_norm_init"] = init_data[i]["v_norm_init"]
        d["q_change"] = d["q_norm"] - init_data[i]["q_norm_init"]
        d["v_change"] = d["v_norm"] - init_data[i]["v_norm_init"]
        d["total_change"] = abs(d["q_change"]) + abs(d["v_change"])

    # Print change comparison by class
    print("Head  Class    V/Q_init  V/Q_trained  V/Q_change  Q_change  V_change  Total_change")
    for d in sorted(all_data, key=lambda x: (x.get("class", "neutral"), x["layer"], x["head"])):
        cls = d.get("class", "neutral")
        print("  L%dH%d  %-7s  %.4f    %.4f       %+.4f    %+.1f     %+.1f     %.1f" % (
            d["layer"], d["head"], cls, d["v_q_init"], d["v_q_ratio"],
            d["v_q_change"], d["q_change"], d["v_change"], d["total_change"]))

    # Statistical test: do anchors change less than workers?
    anchor_changes = [d["total_change"] for d in all_data if d.get("class") == "anchor"]
    worker_changes = [d["total_change"] for d in all_data if d.get("class") == "worker"]

    print("\n=== CHANGE DYNAMICS BY CLASS ===\n")
    if len(anchor_changes) > 1 and len(worker_changes) > 1:
        print("Anchor mean total_change: %.2f (n=%d)" % (np.mean(anchor_changes), len(anchor_changes)))
        print("Worker mean total_change: %.2f (n=%d)" % (np.mean(worker_changes), len(worker_changes)))
        print("Ratio (worker/anchor): %.3fx" % (np.mean(worker_changes) / max(np.mean(anchor_changes), 1e-10)))

        u_stat, u_p = mannwhitneyu(anchor_changes, worker_changes, alternative="two-sided")
        print("Mann-Whitney U: stat=%.1f, p=%.4f" % (u_stat, u_p))

        if u_p < 0.05:
            print("SIGNIFICANT: Workers change more than anchors (as predicted by Bridge #88).")
        else:
            print("NOT significant: Anchors and workers show similar change magnitude.")
    else:
        print("Not enough classified heads for comparison.")

    # ============================================================
    # Correlation: does V/Q ratio correlate with commutator contribution?
    # ============================================================
    print("\n=== V/Q RATIO vs COMMUTATOR CONTRIBUTION (trained) ===\n")
    v_q_all = [d["v_q_ratio"] for d in all_data]
    comm_all = [d["comm_contrib"] for d in all_data]
    rho, p = spearmanr(v_q_all, comm_all)
    print("Spearman(V/Q_ratio, comm_contrib): rho=%.4f, p=%.4f" % (rho, p))
    if abs(rho) > 0.3 and p < 0.05:
        print("SIGNIFICANT correlation — V/Q ratio and commutator contribution are linked.")
    elif p < 0.05:
        print("Significant but weak correlation.")
    else:
        print("NO significant correlation — V/Q and commutator are independent dimensions.")
        print("This means anchor/worker classification adds INDEPENDENT information to commutator analysis.")

    # ============================================================
    # Per-layer anchor density
    # ============================================================
    print("\n=== PER-LAYER ANCHOR DENSITY ===\n")
    print("Layer  Anchors  Workers  Neutrals  Mean_V/Q  Layer_V/Q_std")
    for layer_idx in range(n_layers):
        layer_heads = [d for d in all_data if d["layer"] == layer_idx]
        n_a = sum(1 for d in layer_heads if d.get("class") == "anchor")
        n_w = sum(1 for d in layer_heads if d.get("class") == "worker")
        n_n = sum(1 for d in layer_heads if d.get("class") == "neutral")
        vq_mean = np.mean([d["v_q_ratio"] for d in layer_heads])
        vq_std = np.std([d["v_q_ratio"] for d in layer_heads])
        print("  L%2d    %d        %d        %d       %.4f    %.4f" % (
            layer_idx, n_a, n_w, n_n, vq_mean, vq_std))

except Exception as e:
    print("Could not create fresh model: %s" % e)
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
