"""
Per-Head Topology Analysis — v0.6a Initial vs Final
====================================================
Computes per-head commutator structure at init and after training.
Tests whether initial head topology predicts crystallization patterns.

Run in WSL with HRM conda env:
  cd /home/clawd && python /mnt/c/Users/mercu/clawd/projects/Corpus\ Perspectival/analysis/head_topology.py
"""
import sys
sys.path.insert(0, "/home/clawd/HRM")

import torch
import numpy as np
from scipy.stats import spearmanr
import json

# ============================================================
# Load the v0.6a trajectory (has init and final per-layer CV)
# ============================================================
traj_path = "/mnt/c/Users/mercu/clawd/projects/Corpus Perspectival/kf_trajectory_300m_scheduled.json"
with open(traj_path) as f:
    traj = json.load(f)

init_entry = traj[0]
final_entry = traj[-1]

print("=" * 70)
print("HEAD TOPOLOGY ANALYSIS — v0.6a (bidirectional, threshold=0.0)")
print("=" * 70)
print()

# ============================================================
# Load the trained checkpoint to inspect head-level structure
# ============================================================
ckpt_path = "/home/clawd/HRM/checkpoints/300m_kf_bidir_t00/epoch_500.pt"
print("Loading checkpoint: %s" % ckpt_path)
ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)

# Extract model state dict
state_dict = ckpt["model_state_dict"]

# Find QKV projection weights for H-module layers
h_qkv_keys = sorted([k for k in state_dict if "H_level" in k and "qkv_proj.weight" in k])
l_qkv_keys = sorted([k for k in state_dict if "L_level" in k and "qkv_proj.weight" in k])

print("H-module QKV layers: %d" % len(h_qkv_keys))
print("L-module QKV layers: %d" % len(l_qkv_keys))
print()

# ============================================================
# Per-Head Commutator Analysis
# ============================================================
def analyze_heads(qkv_weight, n_heads, label):
    """
    Given a QKV projection weight [3*n_heads*d_head, hidden_size],
    extract per-head Q/K/V projection matrices and compute:
    - Per-head weight norms
    - Per-head-pair commutator norms (using Q projections)
    - Per-head contribution to layer CV
    """
    # QKV weight shape: [3 * n_heads * d_head, hidden_size]
    total_dim = qkv_weight.shape[0]
    hidden = qkv_weight.shape[1]
    d_head = total_dim // (3 * n_heads)

    # Split into Q, K, V blocks
    qkv = qkv_weight.reshape(3, n_heads, d_head, hidden)
    Q = qkv[0]  # [n_heads, d_head, hidden]
    K = qkv[1]
    V = qkv[2]

    # Per-head analysis using Q projections (these define the attention geometry)
    head_norms = []
    for h in range(n_heads):
        head_norms.append(torch.norm(Q[h]).item())

    # Per-head-pair commutator norms
    # Commutator of Q_i and Q_j: [Q_i, Q_j] = Q_i @ Q_j^T - Q_j @ Q_i^T
    # (using d_head x d_head effective matrices: Q_h @ Q_h^T)
    effective = []
    for h in range(n_heads):
        # Q_h is [d_head, hidden] -> Q_h @ Q_h^T is [d_head, d_head]
        eff = Q[h] @ Q[h].T
        effective.append(eff)

    commutator_norms = np.zeros((n_heads, n_heads))
    for i in range(n_heads):
        for j in range(i + 1, n_heads):
            comm = effective[i] @ effective[j] - effective[j] @ effective[i]
            c_norm = torch.norm(comm).item()
            # Normalize by product of norms
            norm_prod = torch.norm(effective[i]).item() * torch.norm(effective[j]).item()
            if norm_prod > 0:
                commutator_norms[i, j] = c_norm / norm_prod
                commutator_norms[j, i] = commutator_norms[i, j]

    # Per-head contribution to CV: how much does each head contribute to commutator variance?
    # Head i's contribution = mean of c_{ij} for all j != i
    head_contribution = np.zeros(n_heads)
    for i in range(n_heads):
        vals = [commutator_norms[i, j] for j in range(n_heads) if j != i]
        head_contribution[i] = np.mean(vals) if vals else 0

    # Layer CV (variance of off-diagonal commutator norms)
    off_diag = [commutator_norms[i, j] for i in range(n_heads) for j in range(i + 1, n_heads)]
    layer_cv = np.var(off_diag) if off_diag else 0

    return {
        "head_norms": head_norms,
        "commutator_norms": commutator_norms,
        "head_contribution": head_contribution,
        "layer_cv": layer_cv,
        "effective_matrices": effective,
    }


# ============================================================
# Analyze H-module (trained checkpoint)
# ============================================================
print("=== H-MODULE HEAD TOPOLOGY (trained, epoch 500) ===\n")

h_results_trained = []
for layer_idx, key in enumerate(h_qkv_keys):
    w = state_dict[key]
    n_heads = 8  # 300M HRM has 8 heads
    result = analyze_heads(w, n_heads, "H-L%d" % layer_idx)
    h_results_trained.append(result)
    print("Layer %2d: CV=%.6e  head_contributions: %s" % (
        layer_idx, result["layer_cv"],
        "  ".join("H%d=%.4f" % (h, c) for h, c in enumerate(result["head_contribution"]))))

# ============================================================
# Now analyze the INIT state
# We need the initial model. Check if there's an init checkpoint.
# ============================================================
print("\n=== INITIAL HEAD TOPOLOGY ===\n")

# Try to create a fresh model with the same config
try:
    from omegaconf import OmegaConf
    arch_cfg_path = "/home/clawd/HRM/config/arch/hrm_v2.yaml"
    arch_cfg = OmegaConf.load(arch_cfg_path)
    arch_resolved = OmegaConf.to_container(arch_cfg, resolve=True)
    hidden_size = arch_resolved.get("hidden_size", 1024)
    if isinstance(arch_resolved.get("puzzle_emb_ndim"), str):
        arch_resolved["puzzle_emb_ndim"] = hidden_size

    from utils.functions import load_model_class
    model_cfg = {
        **arch_resolved, "vocab_size": 21, "max_seq_len": 256,
        "batch_size": 1, "seq_len": 256,
        "num_puzzle_identifiers": 10, "causal": False,
    }
    model_name = model_cfg.pop("name", "")
    loss_cfg = model_cfg.pop("loss", {})
    model_cls = load_model_class(model_name)

    # Create fresh model (random init)
    torch.manual_seed(42)
    with torch.device("cpu"):
        fresh_model = model_cls(model_cfg)

    # Extract QKV weights from fresh model
    fresh_state = fresh_model.state_dict()
    fresh_h_keys = sorted([k for k in fresh_state if "H_level" in k and "qkv_proj.weight" in k])

    h_results_init = []
    for layer_idx, key in enumerate(fresh_h_keys):
        w = fresh_state[key]
        result = analyze_heads(w, 8, "H-L%d-init" % layer_idx)
        h_results_init.append(result)
        print("Layer %2d: CV=%.6e  head_contributions: %s" % (
            layer_idx, result["layer_cv"],
            "  ".join("H%d=%.4f" % (h, c) for h, c in enumerate(result["head_contribution"]))))

    print("\n=== INIT → TRAINED HEAD CONTRIBUTION CHANGE ===\n")
    print("Layer  Head  Init_Contrib  Trained_Contrib  Change  Change_Ratio")
    all_init_contribs = []
    all_trained_contribs = []
    all_changes = []

    for layer_idx in range(len(h_results_init)):
        for h in range(8):
            init_c = h_results_init[layer_idx]["head_contribution"][h]
            trained_c = h_results_trained[layer_idx]["head_contribution"][h]
            change = trained_c - init_c
            ratio = trained_c / max(init_c, 1e-10)
            all_init_contribs.append(init_c)
            all_trained_contribs.append(trained_c)
            all_changes.append(change)
            print("  L%2d   H%d    %.6f      %.6f      %+.6f   %.2fx" % (
                layer_idx, h, init_c, trained_c, change, ratio))

    # Correlation: does initial contribution predict final contribution?
    rho, p = spearmanr(all_init_contribs, all_trained_contribs)
    print("\nSpearman(init_contribution, trained_contribution): rho=%.4f, p=%.4f" % (rho, p))

    # Correlation: does initial contribution predict CHANGE?
    rho2, p2 = spearmanr(all_init_contribs, all_changes)
    print("Spearman(init_contribution, change): rho=%.4f, p=%.4f" % (rho2, p2))

    # Per-layer: does init CV predict trained CV enrichment?
    init_layer_cvs = [r["layer_cv"] for r in h_results_init]
    trained_layer_cvs = [r["layer_cv"] for r in h_results_trained]
    enrichments = [t / max(i, 1e-20) for t, i in zip(trained_layer_cvs, init_layer_cvs)]
    rho3, p3 = spearmanr(init_layer_cvs, enrichments)
    print("\nSpearman(init_layer_CV, enrichment_ratio): rho=%.4f, p=%.4f" % (rho3, p3))

    # Comparison with trajectory data
    print("\n=== CROSS-CHECK WITH TRAJECTORY DATA ===\n")
    print("Layer  Traj_Init_CV    Head_Init_CV    Traj_Final_CV   Head_Final_CV   Traj_Enrichment  Head_Enrichment")
    for i in range(min(12, len(h_results_init))):
        traj_init = init_entry["H"]["per_layer"][str(i)]["cv"]
        traj_final = final_entry["H"]["per_layer"][str(i)]["cv"]
        head_init_cv = h_results_init[i]["layer_cv"]
        head_final_cv = h_results_trained[i]["layer_cv"]
        traj_enrich = traj_final / max(traj_init, 1e-20)
        head_enrich = head_final_cv / max(head_init_cv, 1e-20)
        print("  L%2d  %.4e    %.4e    %.4e    %.4e    %8.1fx         %8.1fx" % (
            i, traj_init, head_init_cv, traj_final, head_final_cv, traj_enrich, head_enrich))

except Exception as e:
    print("Could not create fresh model: %s" % e)
    print("Continuing with trained-only analysis...")
    import traceback
    traceback.print_exc()

# ============================================================
# Head heterogeneity within layers
# ============================================================
print("\n=== WITHIN-LAYER HEAD HETEROGENEITY (trained) ===\n")
print("Layer  CV_of_contribs  Max_contrib  Min_contrib  Max/Min_ratio  Most_active_head")
for layer_idx, result in enumerate(h_results_trained):
    contribs = result["head_contribution"]
    cv_contribs = np.std(contribs) / max(np.mean(contribs), 1e-10)
    max_c = max(contribs)
    min_c = min(contribs)
    max_h = np.argmax(contribs)
    ratio = max_c / max(min_c, 1e-10)
    print("  L%2d    %.4f         %.6f     %.6f     %.2fx            H%d" % (
        layer_idx, cv_contribs, max_c, min_c, ratio, max_h))

print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
