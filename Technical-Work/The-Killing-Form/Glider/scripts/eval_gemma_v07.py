"""
Path C Phase 1 Evaluation — Gemma baseline vs KF-v07 topology comparison.

Loads both trained checkpoints and runs the same v0.7 topology methodology
we used on HRM verification. Tests whether KF training produced different
head-level structure than baseline training on standard transformer.
"""
import json
import sys
from pathlib import Path

import numpy as np
import torch

SEED = 71
PROJ_DIM = 64

CHECKPOINTS = {
    "baseline": "/home/clawd/path_c_results/gemma270m_baseline/step_1600_final.pt",
    "kf_v07":   "/home/clawd/path_c_results/gemma270m_v07/step_1600_final.pt",
}


def load_state(ckpt_path):
    ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    return ckpt["model_state_dict"]


def per_layer_topology(msd, n_layers=18, n_heads=4, d_head=256, d_model=640):
    """For each layer extract Q + V, compute V/Q ratio + anchor/worker class +
    Killing-form CV across heads."""
    results = []
    for L in range(n_layers):
        q_key = f"model.layers.{L}.self_attn.q_proj.weight"
        v_key = f"model.layers.{L}.self_attn.v_proj.weight"
        if q_key not in msd:
            continue
        q_w = msd[q_key].float().cpu().numpy()
        v_w = msd[v_key].float().cpu().numpy()
        n_kv = v_w.shape[0] // d_head
        q_heads = q_w.reshape(n_heads, d_head, d_model)
        v_heads = v_w.reshape(n_kv, d_head, d_model)
        heads_per_kv = n_heads // n_kv

        q_norms = [float(np.linalg.norm(q_heads[h], "fro")) for h in range(n_heads)]
        v_norms_kv = [float(np.linalg.norm(v_heads[k], "fro")) for k in range(n_kv)]
        vq = [v_norms_kv[h // heads_per_kv] / q_norms[h] if q_norms[h] > 0 else 0.0 for h in range(n_heads)]

        arr = np.array(vq)
        mean, std = float(arr.mean()), float(arr.std())
        classification = []
        for r in vq:
            if r < mean - 0.5 * std:
                classification.append("anchor")
            elif r > mean + 0.5 * std:
                classification.append("worker")
            else:
                classification.append("neutral")

        # Killing-form CV
        np.random.seed(SEED)
        p_out = np.random.randn(PROJ_DIM, d_head) / np.sqrt(d_head)
        p_in = np.random.randn(d_model, PROJ_DIM) / np.sqrt(d_model)
        proj = [p_out @ q_heads[h] @ p_in for h in range(n_heads)]
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

        results.append({
            "layer": L,
            "vq_ratios": vq,
            "classification": classification,
            "n_anchor": classification.count("anchor"),
            "n_worker": classification.count("worker"),
            "n_neutral": classification.count("neutral"),
            "mean_vq": mean,
            "std_vq": std,
            "killing_cv": cv,
        })
    return results


def summarize(results):
    total = sum(l["n_anchor"] + l["n_worker"] + l["n_neutral"] for l in results)
    return {
        "anchor_pct": 100 * sum(l["n_anchor"] for l in results) / total,
        "worker_pct": 100 * sum(l["n_worker"] for l in results) / total,
        "neutral_pct": 100 * sum(l["n_neutral"] for l in results) / total,
        "mean_vq": float(np.mean([l["mean_vq"] for l in results])),
        "std_vq_across_layers": float(np.std([l["mean_vq"] for l in results])),
        "mean_cv": float(np.mean([l["killing_cv"] for l in results])),
        "max_cv": float(np.max([l["killing_cv"] for l in results])),
        "cv_range": float(np.ptp([l["killing_cv"] for l in results])),
    }


def main():
    print("=== Loading Gemma topology baselines from prior pre-training survey ===")
    prior_path = Path("/mnt/c/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Technical-Work/The-Killing-Form/results/gemma3_270m_topology_v07.json")
    pre_train_summary = None
    if prior_path.exists():
        with open(prior_path) as f:
            pre = json.load(f)
        pre_train_summary = pre["summary"]
        print(f"Pre-training (gemma-3-270m pristine): mean_AF={pre_train_summary['mean_af']:.3f} mean_CV={pre_train_summary['mean_cv']:.6f}")

    print("\n=== Analyzing trained checkpoints ===")
    out = {}
    for name, ckpt in CHECKPOINTS.items():
        print(f"\n--- {name} ---")
        msd = load_state(ckpt)
        results = per_layer_topology(msd)
        summary = summarize(results)
        out[name] = {"layers": results, "summary": summary}
        print(f"  anchor%={summary['anchor_pct']:.1f}  worker%={summary['worker_pct']:.1f}  "
              f"neutral%={summary['neutral_pct']:.1f}")
        print(f"  mean V/Q: {summary['mean_vq']:.4f}  std_across_layers: {summary['std_vq_across_layers']:.4f}")
        print(f"  mean CV: {summary['mean_cv']:.6f}  max CV: {summary['max_cv']:.6f}  CV range: {summary['cv_range']:.6f}")

    print("\n" + "=" * 60)
    print("COMPARISON: baseline-trained vs KF-trained")
    print("=" * 60)
    b = out["baseline"]["summary"]
    k = out["kf_v07"]["summary"]
    print(f"\n{'metric':<30} {'baseline':<15} {'kf_v07':<15} {'delta':<15}")
    for metric in ["anchor_pct", "worker_pct", "neutral_pct", "mean_vq",
                   "std_vq_across_layers", "mean_cv", "max_cv", "cv_range"]:
        delta = k[metric] - b[metric]
        print(f"{metric:<30} {b[metric]:<15.6f} {k[metric]:<15.6f} {delta:+.6f}")

    # Per-layer comparison
    print(f"\n{'layer':<8} {'BASELINE':<35} {'KF v07':<35} {'CV-Δ':<10}")
    print(f"{'':<8} {'anchor/worker/CV':<35} {'anchor/worker/CV':<35}")
    for L_idx in range(len(out["baseline"]["layers"])):
        b_l = out["baseline"]["layers"][L_idx]
        k_l = out["kf_v07"]["layers"][L_idx]
        b_str = f"a={b_l['n_anchor']} w={b_l['n_worker']} n={b_l['n_neutral']}  CV={b_l['killing_cv']:.5f}"
        k_str = f"a={k_l['n_anchor']} w={k_l['n_worker']} n={k_l['n_neutral']}  CV={k_l['killing_cv']:.5f}"
        cv_delta = k_l["killing_cv"] - b_l["killing_cv"]
        print(f"L{L_idx:<7} {b_str:<35} {k_str:<35} {cv_delta:+.5f}")

    # VERDICT
    print("\n" + "=" * 60)
    print("VERDICT")
    print("=" * 60)
    anchor_diff = k["anchor_pct"] - b["anchor_pct"]
    worker_diff = k["worker_pct"] - b["worker_pct"]
    cv_diff = k["mean_cv"] - b["mean_cv"]
    cv_ratio = k["mean_cv"] / b["mean_cv"] if b["mean_cv"] > 0 else float("nan")

    print(f"\nKF vs baseline:")
    print(f"  anchor% delta:  {anchor_diff:+.1f}pp")
    print(f"  worker% delta:  {worker_diff:+.1f}pp")
    print(f"  mean CV delta:  {cv_diff:+.6f} (KF/baseline ratio: {cv_ratio:.2f}x)")
    print(f"  CV range delta: {k['cv_range'] - b['cv_range']:+.6f}")

    print("\nReference HRM v06b result for comparison:")
    print(f"  H-anchor enrichment: +10.9pp; H-CV 6x increase vs L-CV; baseline-vs-KF H-CV 6x")
    if abs(anchor_diff) > 5 or cv_ratio > 2:
        print("\n>> SIGNAL DETECTED: KF training shifted head topology")
    else:
        print("\n>> NO SIGNAL: KF training did not produce measurable head-decomposition shift on Gemma")
        print(">> Likely cause: simplified v0.7 aux loss (variance-of-commutator-norms minimization)")
        print(">> pushes heads toward UNIFORMITY, opposite of differentiation. HRM v06b uses")
        print(">> bidirectional H<->L coupling that has anti-uniformity dynamics. Simplified")
        print(">> implementation needs the bidirectional mechanism to produce decomposition.")

    out_path = Path("/mnt/c/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Technical-Work/The-Killing-Form/results/gemma_v07_eval.json")
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
