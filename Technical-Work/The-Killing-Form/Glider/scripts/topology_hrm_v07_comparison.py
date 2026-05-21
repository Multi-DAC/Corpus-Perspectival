"""
Path C' — HRM v0.7 Topology Comparison

Tests the methodological question raised by Clayton: did Finding #80 (+1.37pp
gradient-gated KF EXCEEDS baseline at 300M) work because of HRM's hard-
architected H/L module separation, OR can v0.7's topology-emergent anchor/
worker classification substitute for it?

Method: run v0.7 anchor/worker topology survey on BOTH:
- 300m_baseline (HRM without KF training)
- 300m_bidir_coupled_v06b (HRM after v06b coupled-bidirectional KF training)

Key test: do anchor/worker labels distribute systematically by H/L module?
If H-layers cluster as one class and L-layers as the other (especially after
KF training), topology-emergent decomposition recovers the architected
separation → safe to port to Gemma. If not, substrate-matters → revisit.

HRM v2 structure: 16 heads/layer, 12 H-layers + 12 L-layers, hidden_size=1024,
head_dim=64. Q/K/V projection is FUSED at (3*1024, 1024) — split needed.
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

CHECKPOINTS = {
    "baseline": "/home/clawd/HRM/checkpoints/300m_baseline/epoch_500.pt",
    "kf_bidir": "/home/clawd/HRM/checkpoints/300m_kf_bidir_t00/epoch_500.pt",
}


def load_hrm_state_dict(ckpt_path):
    """Load HRM checkpoint and return model_state_dict."""
    ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    return ckpt["model_state_dict"]


def find_h_l_layers(msd):
    """Identify H-layer and L-layer indices present in state dict."""
    h_layers = sorted({int(k.split(".")[3]) for k in msd.keys() if "H_level.layers." in k and "qkv_proj.weight" in k})
    l_layers = sorted({int(k.split(".")[3]) for k in msd.keys() if "L_level.layers." in k and "qkv_proj.weight" in k})
    return h_layers, l_layers


def extract_qkv_per_head(msd, module, layer_idx, n_heads=16, d_head=64, d_model=1024):
    """Extract per-head Q, K, V projection matrices for one layer.

    HRM fused qkv_proj: shape [3*d_model, d_model] (rows are concat of Q rows, K rows, V rows).
    For 16 heads × 64 head_dim = 1024 dimension per Q/K/V block.
    """
    key = f"inner.{module}_level.layers.{layer_idx}.self_attn.qkv_proj.weight"
    if key not in msd:
        return None
    w = msd[key].float().cpu().numpy()  # [3072, 1024]
    # Split into Q, K, V blocks
    q_block = w[:d_model, :]              # [1024, 1024]
    k_block = w[d_model:2*d_model, :]     # [1024, 1024]
    v_block = w[2*d_model:3*d_model, :]   # [1024, 1024]
    # Per-head reshape (head_idx is along output dim)
    q_heads = q_block.reshape(n_heads, d_head, d_model)
    k_heads = k_block.reshape(n_heads, d_head, d_model)
    v_heads = v_block.reshape(n_heads, d_head, d_model)
    return {"q": q_heads, "k": k_heads, "v": v_heads}


def per_head_vq_ratio(layer_data, n_heads):
    """V/Q norm ratio per head (anchor=low, worker=high)."""
    q_norms = [float(np.linalg.norm(layer_data["q"][h], "fro")) for h in range(n_heads)]
    v_norms = [float(np.linalg.norm(layer_data["v"][h], "fro")) for h in range(n_heads)]
    ratios = [v_norms[h] / q_norms[h] if q_norms[h] > 0 else 0.0 for h in range(n_heads)]
    return ratios, q_norms, v_norms


def classify_anchor_worker(vq_ratios):
    """Per v0.7 spec Claim 3: anchor below mean - 0.5σ, worker above mean + 0.5σ."""
    arr = np.array(vq_ratios)
    mean, std = float(np.mean(arr)), float(np.std(arr))
    classification = []
    for r in arr:
        if r < mean - 0.5 * std:
            classification.append("anchor")
        elif r > mean + 0.5 * std:
            classification.append("worker")
        else:
            classification.append("neutral")
    return classification, mean, std


def compute_layer_killing(layer_data, n_heads, proj_dim=PROJ_DIM):
    """Killing-form CV + AF + per-head commutator contribution."""
    np.random.seed(SEED)
    d_head = layer_data["q"].shape[1]
    d_model = layer_data["q"].shape[2]
    p_out = np.random.randn(proj_dim, d_head) / np.sqrt(d_head)
    p_in = np.random.randn(d_model, proj_dim) / np.sqrt(d_model)
    proj = [p_out @ layer_data["q"][h] @ p_in for h in range(n_heads)]

    killing = np.zeros((n_heads, n_heads))
    for h in range(n_heads):
        for hp in range(n_heads):
            val = 0.0
            for k in range(n_heads):
                c1 = proj[h] @ proj[k] - proj[k] @ proj[h]
                c2 = proj[hp] @ proj[k] - proj[k] @ proj[hp]
                val += np.trace(c1.T @ c2)
            killing[h, hp] = val
    mx = np.max(np.abs(killing))
    kn = killing / mx if mx > 0 else killing
    evs = np.sort(np.abs(np.linalg.eigvalsh(kn)))
    af = float(int(np.sum(evs < AF_THRESHOLD)) / n_heads)

    head_contributions = []
    for h in range(n_heads):
        c_sum = 0.0
        for hp in range(n_heads):
            if hp == h:
                continue
            c = proj[h] @ proj[hp] - proj[hp] @ proj[h]
            c_sum += np.linalg.norm(c, "fro") ** 2
        head_contributions.append(float(c_sum))

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
    return {"af": af, "cv": cv, "head_contributions": head_contributions}


def analyze_checkpoint(ckpt_path, name, n_heads=16, d_head=64, d_model=1024):
    """Full v0.7 topology analysis on one HRM checkpoint."""
    print(f"\n=== {name}: {ckpt_path} ===")
    t0 = time.time()
    msd = load_hrm_state_dict(ckpt_path)
    print(f"loaded {len(msd)} tensors in {time.time()-t0:.1f}s")

    h_layers, l_layers = find_h_l_layers(msd)
    print(f"H-layers: {len(h_layers)} (indices {h_layers[0]}..{h_layers[-1]})  "
          f"L-layers: {len(l_layers)} (indices {l_layers[0]}..{l_layers[-1]})")

    results = {"checkpoint": ckpt_path, "name": name, "n_heads": n_heads, "layers": []}

    for module in ["H", "L"]:
        layer_indices = h_layers if module == "H" else l_layers
        for L in layer_indices:
            ldata = extract_qkv_per_head(msd, module, L, n_heads, d_head, d_model)
            if ldata is None:
                continue
            vq, q_norms, v_norms = per_head_vq_ratio(ldata, n_heads)
            classification, mean_vq, std_vq = classify_anchor_worker(vq)
            killing = compute_layer_killing(ldata, n_heads)
            n_anchor = classification.count("anchor")
            n_worker = classification.count("worker")
            n_neutral = classification.count("neutral")
            results["layers"].append({
                "module": module,
                "layer": L,
                "vq_ratios": vq,
                "classification": classification,
                "n_anchor": n_anchor,
                "n_worker": n_worker,
                "n_neutral": n_neutral,
                "mean_vq": mean_vq,
                "std_vq": std_vq,
                "killing_af": killing["af"],
                "killing_cv": killing["cv"],
                "head_contributions": killing["head_contributions"],
            })
            print(f"  {module}{L:2d}: AF={killing['af']:.3f} CV={killing['cv']:.4f} "
                  f"anchor={n_anchor:2d} worker={n_worker:2d} neutral={n_neutral:2d} "
                  f"mean_vq={mean_vq:.3f}")

    return results


def compare(baseline, v06b):
    """Compare distributions of anchor/worker by H vs L module, before/after KF."""
    print("\n" + "=" * 70)
    print("COMPARISON: anchor/worker distribution across H vs L modules")
    print("=" * 70)

    def aggregate(results, module):
        total_anchor = sum(l["n_anchor"] for l in results["layers"] if l["module"] == module)
        total_worker = sum(l["n_worker"] for l in results["layers"] if l["module"] == module)
        total_neutral = sum(l["n_neutral"] for l in results["layers"] if l["module"] == module)
        total = total_anchor + total_worker + total_neutral
        if total == 0:
            return {"anchor_pct": 0, "worker_pct": 0, "neutral_pct": 0, "total": 0}
        return {
            "anchor_pct": 100 * total_anchor / total,
            "worker_pct": 100 * total_worker / total,
            "neutral_pct": 100 * total_neutral / total,
            "total": total,
        }

    print(f"\n{'':<25} {'BASELINE':<30} {'v06b TRAINED':<30}")
    print(f"{'':<25} {'H mod':<10}{'L mod':<10}{'diff':<10} {'H mod':<10}{'L mod':<10}{'diff':<10}")

    for cls in ["anchor", "worker", "neutral"]:
        b_h = aggregate(baseline, "H")[f"{cls}_pct"]
        b_l = aggregate(baseline, "L")[f"{cls}_pct"]
        v_h = aggregate(v06b, "H")[f"{cls}_pct"]
        v_l = aggregate(v06b, "L")[f"{cls}_pct"]
        print(f"{cls + '%':<25} {b_h:>6.1f}    {b_l:>6.1f}    {b_h-b_l:>+6.1f}    "
              f"{v_h:>6.1f}    {v_l:>6.1f}    {v_h-v_l:>+6.1f}")

    # Per-layer means of V/Q ratio by module — is there a systematic difference?
    def module_mean_vq(results, module):
        vqs = [l["mean_vq"] for l in results["layers"] if l["module"] == module]
        return float(np.mean(vqs)) if vqs else None

    print(f"\n{'mean V/Q ratio per module:':<30}")
    print(f"  BASELINE  H: {module_mean_vq(baseline, 'H'):.3f}   L: {module_mean_vq(baseline, 'L'):.3f}")
    print(f"  v06b      H: {module_mean_vq(v06b, 'H'):.3f}   L: {module_mean_vq(v06b, 'L'):.3f}")

    # Killing-form metrics by module
    def module_mean_af_cv(results, module):
        afs = [l["killing_af"] for l in results["layers"] if l["module"] == module]
        cvs = [l["killing_cv"] for l in results["layers"] if l["module"] == module]
        return (float(np.mean(afs)) if afs else None, float(np.mean(cvs)) if cvs else None)

    print(f"\n{'mean AF, CV per module:':<30}")
    b_h_af, b_h_cv = module_mean_af_cv(baseline, "H")
    b_l_af, b_l_cv = module_mean_af_cv(baseline, "L")
    v_h_af, v_h_cv = module_mean_af_cv(v06b, "H")
    v_l_af, v_l_cv = module_mean_af_cv(v06b, "L")
    print(f"  BASELINE  H: AF={b_h_af:.3f} CV={b_h_cv:.4f}   L: AF={b_l_af:.3f} CV={b_l_cv:.4f}")
    print(f"  v06b      H: AF={v_h_af:.3f} CV={v_h_cv:.4f}   L: AF={v_l_af:.3f} CV={v_l_cv:.4f}")

    # KEY VERDICT
    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)
    baseline_h_l_anchor_diff = (aggregate(baseline, "H")["anchor_pct"] -
                                aggregate(baseline, "L")["anchor_pct"])
    v06b_h_l_anchor_diff = (aggregate(v06b, "H")["anchor_pct"] -
                            aggregate(v06b, "L")["anchor_pct"])
    sharpening = abs(v06b_h_l_anchor_diff) - abs(baseline_h_l_anchor_diff)
    print(f"\nAnchor-pct H-vs-L diff (baseline): {baseline_h_l_anchor_diff:+.1f} percentage points")
    print(f"Anchor-pct H-vs-L diff (v06b):     {v06b_h_l_anchor_diff:+.1f} percentage points")
    print(f"Sharpening from baseline -> v06b:  {sharpening:+.1f} pp (positive = KF training sharpened H/L distinction)")

    if abs(v06b_h_l_anchor_diff) > 10:
        print("\n>> STRONG H/L correspondence in v06b: topology-emergent classification ALIGNS with hard-architected separation")
        print(">> Implication: topology-emergent decomposition is a viable substitute for Gemma port")
    elif sharpening > 5:
        print("\n>> MODERATE sharpening from KF training: topology-emergent decomposition partially aligned with H/L")
        print(">> Implication: viable but expect some performance gap on Gemma vs HRM")
    else:
        print("\n>> NO clear H/L correspondence: topology-emergent classification orthogonal to module-architecture")
        print(">> Implication: SUBSTRATE MATTERS — Gemma port needs additional structural priors")


if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent.parent.parent / "results"
    out_dir.mkdir(parents=True, exist_ok=True)

    baseline_results = analyze_checkpoint(CHECKPOINTS["baseline"], "BASELINE")
    kf_results = analyze_checkpoint(CHECKPOINTS["kf_bidir"], "KF_BIDIR")

    compare(baseline_results, kf_results)

    combined = {"baseline": baseline_results, "kf_bidir": kf_results}
    out_path = out_dir / "hrm_topology_v07_comparison.json"
    with open(out_path, "w") as f:
        json.dump(combined, f, indent=2)
    print(f"\nSaved: {out_path}")
