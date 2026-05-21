"""
Path C' Extension — HRM Training-Trajectory Topology Evolution

Following the baseline-vs-KF comparison that showed KF training produces
H/L anchor/worker decomposition (+10.9pp anchor enrichment in H at
epoch 500), this script analyzes the TRAJECTORY: when in training does
the decomposition emerge? Is it gradual or sudden? Does timing differ
between baseline and KF training?

Method: run v0.7 topology survey on epochs 100, 200, 300, 400, 500
for both baseline and KF-bidirectional checkpoints. Track H/L anchor
enrichment, V/Q ratio difference, and Killing CV by epoch.

Implication for Gemma port: tells us how many training steps to expect
before decomposition appears, when to start measuring emergent structure,
and whether v0.7 architecture should adjust λ schedule by training phase.
"""
import json
import time
import sys
from pathlib import Path

import numpy as np
import torch

SEED = 71
AF_THRESHOLD = 0.10
PROJ_DIM = 64

CHECKPOINT_BASES = {
    "baseline": "/home/clawd/HRM/checkpoints/300m_baseline",
    "kf_bidir": "/home/clawd/HRM/checkpoints/300m_kf_bidir_t00",
}
EPOCHS = [100, 200, 300, 400, 500]


def load_hrm_state_dict(ckpt_path):
    ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    return ckpt["model_state_dict"]


def extract_qkv_per_head(msd, module, layer_idx, n_heads=16, d_head=64, d_model=1024):
    key = f"inner.{module}_level.layers.{layer_idx}.self_attn.qkv_proj.weight"
    if key not in msd:
        return None
    w = msd[key].float().cpu().numpy()
    q_block = w[:d_model, :]
    v_block = w[2*d_model:3*d_model, :]
    q_heads = q_block.reshape(n_heads, d_head, d_model)
    v_heads = v_block.reshape(n_heads, d_head, d_model)
    return {"q": q_heads, "v": v_heads}


def per_head_vq(layer_data, n_heads):
    q_norms = [float(np.linalg.norm(layer_data["q"][h], "fro")) for h in range(n_heads)]
    v_norms = [float(np.linalg.norm(layer_data["v"][h], "fro")) for h in range(n_heads)]
    ratios = [v_norms[h] / q_norms[h] if q_norms[h] > 0 else 0.0 for h in range(n_heads)]
    return ratios


def classify(vq):
    arr = np.array(vq)
    mean, std = float(np.mean(arr)), float(np.std(arr))
    return [("anchor" if r < mean - 0.5*std else "worker" if r > mean + 0.5*std else "neutral") for r in arr]


def compute_killing(layer_data, n_heads, proj_dim=PROJ_DIM):
    np.random.seed(SEED)
    d_head = layer_data["q"].shape[1]
    d_model = layer_data["q"].shape[2]
    p_out = np.random.randn(proj_dim, d_head) / np.sqrt(d_head)
    p_in = np.random.randn(d_model, proj_dim) / np.sqrt(d_model)
    proj = [p_out @ layer_data["q"][h] @ p_in for h in range(n_heads)]
    norms = np.zeros((n_heads, n_heads))
    for h in range(n_heads):
        for hp in range(h + 1, n_heads):
            c = proj[h] @ proj[hp] - proj[hp] @ proj[h]
            norms[h, hp] = np.linalg.norm(c, "fro")
            norms[hp, h] = norms[h, hp]
    typ = np.mean([np.linalg.norm(A, "fro") for A in proj])
    if typ > 0:
        norms /= typ ** 2
    mask = np.ones_like(norms, dtype=bool)
    np.fill_diagonal(mask, False)
    cv = float(np.var(norms[mask]))
    return cv


def analyze_epoch(ckpt_path, n_heads=16, d_head=64, d_model=1024, n_layers=12):
    msd = load_hrm_state_dict(ckpt_path)
    results = {"H": [], "L": []}
    for module in ["H", "L"]:
        for L in range(n_layers):
            ldata = extract_qkv_per_head(msd, module, L, n_heads, d_head, d_model)
            if ldata is None:
                continue
            vq = per_head_vq(ldata, n_heads)
            cls = classify(vq)
            cv = compute_killing(ldata, n_heads)
            results[module].append({
                "layer": L,
                "n_anchor": cls.count("anchor"),
                "n_worker": cls.count("worker"),
                "n_neutral": cls.count("neutral"),
                "mean_vq": float(np.mean(vq)),
                "std_vq": float(np.std(vq)),
                "killing_cv": cv,
            })
    return results


def summarize(epoch_results):
    """Aggregate per-module stats across all layers of one epoch."""
    summary = {}
    for module in ["H", "L"]:
        layers = epoch_results[module]
        if not layers:
            summary[module] = None
            continue
        total = sum(l["n_anchor"] + l["n_worker"] + l["n_neutral"] for l in layers)
        summary[module] = {
            "anchor_pct": 100 * sum(l["n_anchor"] for l in layers) / total,
            "worker_pct": 100 * sum(l["n_worker"] for l in layers) / total,
            "neutral_pct": 100 * sum(l["n_neutral"] for l in layers) / total,
            "mean_vq": float(np.mean([l["mean_vq"] for l in layers])),
            "mean_cv": float(np.mean([l["killing_cv"] for l in layers])),
        }
    return summary


def run_trajectory():
    trajectory = {}
    for name, base in CHECKPOINT_BASES.items():
        print(f"\n=== {name} ===")
        trajectory[name] = {}
        for ep in EPOCHS:
            ckpt = f"{base}/epoch_{ep}.pt"
            try:
                t0 = time.time()
                epoch_results = analyze_epoch(ckpt)
                summary = summarize(epoch_results)
                trajectory[name][ep] = summary
                h = summary["H"]; l = summary["L"]
                anchor_diff = h["anchor_pct"] - l["anchor_pct"]
                print(f"  epoch {ep:3d}: H anchor={h['anchor_pct']:5.1f}% L anchor={l['anchor_pct']:5.1f}% "
                      f"DIFF={anchor_diff:+5.1f}pp  H_CV={h['mean_cv']:.5f} L_CV={l['mean_cv']:.5f}  "
                      f"({time.time()-t0:.1f}s)")
            except FileNotFoundError:
                print(f"  epoch {ep}: NOT FOUND ({ckpt})")
            except Exception as e:
                print(f"  epoch {ep}: ERROR {e}")
    return trajectory


def report(trajectory):
    print("\n" + "=" * 70)
    print("TRAJECTORY SUMMARY")
    print("=" * 70)
    print(f"\n{'Epoch':<10} {'Baseline H-L anchor diff':<30} {'KF H-L anchor diff':<25}")
    for ep in EPOCHS:
        b = trajectory["baseline"].get(ep)
        k = trajectory["kf_bidir"].get(ep)
        b_diff = f"{b['H']['anchor_pct'] - b['L']['anchor_pct']:+.1f}pp" if b else "-"
        k_diff = f"{k['H']['anchor_pct'] - k['L']['anchor_pct']:+.1f}pp" if k else "-"
        print(f"{ep:<10} {b_diff:<30} {k_diff:<25}")

    # Killing CV trajectory
    print(f"\n{'Epoch':<10} {'Baseline H_CV / L_CV':<30} {'KF H_CV / L_CV':<25}")
    for ep in EPOCHS:
        b = trajectory["baseline"].get(ep)
        k = trajectory["kf_bidir"].get(ep)
        b_cv = f"{b['H']['mean_cv']:.5f} / {b['L']['mean_cv']:.5f}" if b else "-"
        k_cv = f"{k['H']['mean_cv']:.5f} / {k['L']['mean_cv']:.5f}" if k else "-"
        print(f"{ep:<10} {b_cv:<30} {k_cv:<25}")

    # Verdict
    print("\nKey finding:")
    kf_traj = [trajectory["kf_bidir"][ep]["H"]["anchor_pct"] -
               trajectory["kf_bidir"][ep]["L"]["anchor_pct"] for ep in EPOCHS if ep in trajectory["kf_bidir"]]
    if len(kf_traj) >= 2:
        slope = (kf_traj[-1] - kf_traj[0]) / (EPOCHS[len(kf_traj)-1] - EPOCHS[0])
        print(f"  KF anchor-diff slope: {slope:+.3f} pp/epoch  ({kf_traj[0]:+.1f} -> {kf_traj[-1]:+.1f})")
        if slope > 0.01:
            print("  Decomposition appears GRADUALLY through KF training")
        elif slope > 0:
            print("  Decomposition appears slowly through KF training")
        else:
            print("  Decomposition does not gradually emerge — may be discrete/sudden or absent")


if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent.parent.parent / "results"
    out_dir.mkdir(parents=True, exist_ok=True)

    trajectory = run_trajectory()
    report(trajectory)

    out_path = out_dir / "hrm_trajectory_v07.json"
    with open(out_path, "w") as f:
        json.dump(trajectory, f, indent=2)
    print(f"\nSaved: {out_path}")
