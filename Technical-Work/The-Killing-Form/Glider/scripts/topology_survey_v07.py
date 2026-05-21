"""
Path C Phase 1 Step 2: v0.7 Topology Survey on Gemma 3 270m

Maps the complete internal geometry of Gemma-3-270m at three resolution levels
per v0.7 GEMMA_PROGRAM specification:

- LAYER level: per-layer Killing-form CV, AF, commutator variance distribution
- HEAD level: per-head V/Q ratio (anchor/worker classification),
              per-head commutator contribution
- WEIGHT level: weight kurtosis, Q/K/V correlation structure

Outputs:
- JSON summary at results/gemma3_270m_topology_v07.json
- Per-head anchor/worker labels for training-time gating decisions
- Per-layer coherence prior (used by v0.7 layer-level gating)

Run from WSL with: python3 topology_survey_v07.py
"""
import numpy as np
import torch
import gc
import json
import time
import sys
from pathlib import Path

SEED = 71
AF_THRESHOLD = 0.10
PROJ_DIM = 64

MODEL_ID = "google/gemma-3-270m"
# Gemma-3-270m specs (from p45_gemma_sweep.py + verification): 4 heads, 18 layers, 640 d_model, 256 d_head
N_HEADS = 4
N_KV_HEADS = 1
N_LAYERS = 18
D_MODEL = 640
D_HEAD = 256


def load_model_state():
    """Load Gemma-3-270m and return state_dict."""
    from transformers import AutoModelForCausalLM, AutoConfig
    print(f"Loading {MODEL_ID}...", end=" ", flush=True)
    t0 = time.time()
    cfg = AutoConfig.from_pretrained(MODEL_ID)
    print(f"config: hidden={cfg.hidden_size}, heads={cfg.num_attention_heads}, "
          f"layers={cfg.num_hidden_layers}, head_dim={getattr(cfg, 'head_dim', cfg.hidden_size//cfg.num_attention_heads)}")
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, dtype=torch.float32, low_cpu_mem_usage=True)
    state_dict = {k: v.cpu().numpy() for k, v in model.state_dict().items()}
    del model
    gc.collect()
    torch.cuda.empty_cache()
    print(f"  loaded in {time.time()-t0:.1f}s; {len(state_dict)} tensors")
    return state_dict, cfg


def extract_per_head_projections(state_dict, n_layers, n_heads, n_kv_heads, d_head, d_model):
    """Extract Q, K, V per-head projection matrices for all layers.

    Returns dict: layer_idx -> {'q': [n_heads x d_head x d_model], 'k': ..., 'v': ...}
    Note: Gemma uses grouped-query attention so K and V have n_kv_heads, not n_heads.
    """
    layers = {}
    for L in range(n_layers):
        q_key = f"model.layers.{L}.self_attn.q_proj.weight"
        k_key = f"model.layers.{L}.self_attn.k_proj.weight"
        v_key = f"model.layers.{L}.self_attn.v_proj.weight"

        if q_key not in state_dict:
            # Try alternative naming
            candidates = [k for k in state_dict.keys() if f"layers.{L}" in k and "q_proj" in k]
            if not candidates:
                print(f"  layer {L}: q_proj not found; available keys: {[k for k in state_dict.keys() if f'layers.{L}' in k][:5]}")
                continue
            q_key = candidates[0]
            k_key = q_key.replace("q_proj", "k_proj")
            v_key = q_key.replace("q_proj", "v_proj")

        q_w = state_dict[q_key]  # [n_heads * d_head, d_model]
        k_w = state_dict[k_key]  # [n_kv_heads * d_head, d_model]
        v_w = state_dict[v_key]  # [n_kv_heads * d_head, d_model]

        # Per-head reshape
        q_heads = q_w.reshape(n_heads, d_head, d_model)
        k_heads = k_w.reshape(n_kv_heads, d_head, d_model)
        v_heads = v_w.reshape(n_kv_heads, d_head, d_model)

        layers[L] = {"q": q_heads, "k": k_heads, "v": v_heads}
    return layers


def per_head_vq_ratio(layer_data, n_heads, n_kv_heads):
    """Per-head V/Q norm ratio for anchor/worker classification.

    Anchor heads: low V/Q ratio (stability-favoring, weight-norm dominant in Q)
    Worker heads: high V/Q ratio (task-loss-favoring, weight-norm dominant in V)

    With GQA, KV heads are shared across query heads. For Gemma-3-270m
    (n_heads=4, n_kv_heads=1), all 4 query heads share the same V head.
    V/Q ratio per query head = ||V_shared||_F / ||Q_h||_F.
    """
    q_norms = [float(np.linalg.norm(layer_data["q"][h], "fro")) for h in range(n_heads)]
    v_norms_kv = [float(np.linalg.norm(layer_data["v"][k], "fro")) for k in range(n_kv_heads)]
    # Each query head h maps to KV head h // (n_heads // n_kv_heads)
    heads_per_kv = n_heads // n_kv_heads
    vq_ratios = []
    for h in range(n_heads):
        kv_idx = h // heads_per_kv
        ratio = v_norms_kv[kv_idx] / q_norms[h] if q_norms[h] > 0 else 0.0
        vq_ratios.append(ratio)
    return vq_ratios, q_norms, v_norms_kv


def classify_anchor_worker(vq_ratios):
    """Classify heads as anchor / worker / neutral based on within-layer V/Q ratio.

    Per v0.7 spec Claim 3: anchor below mean - 0.5*std, worker above mean + 0.5*std.
    """
    ratios = np.array(vq_ratios)
    mean = float(np.mean(ratios))
    std = float(np.std(ratios))
    classification = []
    for r in ratios:
        if r < mean - 0.5 * std:
            classification.append("anchor")
        elif r > mean + 0.5 * std:
            classification.append("worker")
        else:
            classification.append("neutral")
    return classification, mean, std


def compute_layer_killing(layer_data, n_heads, proj_dim=PROJ_DIM):
    """Compute Killing form CV and AF for the layer (head-pairwise commutator analysis).

    Adapted from p45_gemma_sweep.py compute_layer_metrics.
    """
    np.random.seed(SEED)
    d_head = layer_data["q"].shape[1]
    d_model = layer_data["q"].shape[2]

    p_out = np.random.randn(proj_dim, d_head) / np.sqrt(d_head)
    p_in = np.random.randn(d_model, proj_dim) / np.sqrt(d_model)
    # Project each head's Q to small matrix
    proj = [p_out @ layer_data["q"][h] @ p_in for h in range(n_heads)]

    # Killing form
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
    af = int(np.sum(evs < AF_THRESHOLD)) / n_heads

    # Per-head commutator contribution
    head_contributions = []
    for h in range(n_heads):
        contribution = 0.0
        for hp in range(n_heads):
            if hp == h:
                continue
            c = proj[h] @ proj[hp] - proj[hp] @ proj[h]
            contribution += np.linalg.norm(c, "fro") ** 2
        head_contributions.append(float(contribution))

    # Layer-level commutator variance
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

    return {"af": float(af), "cv": cv, "head_contributions": head_contributions}


def weight_kurtosis(matrix):
    """Excess kurtosis of flattened matrix (outlier-structure indicator)."""
    flat = matrix.flatten()
    mean = np.mean(flat)
    std = np.std(flat)
    if std == 0:
        return 0.0
    z = (flat - mean) / std
    return float(np.mean(z ** 4) - 3)


def survey():
    """Run complete v0.7 topology survey."""
    state_dict, cfg = load_model_state()

    # Detect actual values from config (override defaults if Gemma 3 270m differs)
    n_heads = cfg.num_attention_heads
    n_kv_heads = getattr(cfg, "num_key_value_heads", n_heads)
    n_layers = cfg.num_hidden_layers
    d_model = cfg.hidden_size
    d_head = getattr(cfg, "head_dim", d_model // n_heads)
    print(f"Resolved: heads={n_heads}, kv_heads={n_kv_heads}, layers={n_layers}, "
          f"d_model={d_model}, d_head={d_head}")

    print("\nExtracting per-head projections...", flush=True)
    layers = extract_per_head_projections(state_dict, n_layers, n_heads, n_kv_heads, d_head, d_model)
    print(f"  extracted {len(layers)} layers")

    del state_dict
    gc.collect()

    survey_data = {"model": MODEL_ID, "n_heads": n_heads, "n_kv_heads": n_kv_heads,
                   "n_layers": n_layers, "d_model": d_model, "d_head": d_head,
                   "layers": []}

    print("\nProcessing layers...")
    for L in sorted(layers.keys()):
        ldata = layers[L]
        vq_ratios, q_norms, v_norms = per_head_vq_ratio(ldata, n_heads, n_kv_heads)
        classification, mean_vq, std_vq = classify_anchor_worker(vq_ratios)
        killing = compute_layer_killing(ldata, n_heads)

        q_kurt = float(np.mean([weight_kurtosis(ldata["q"][h]) for h in range(n_heads)]))
        layer_data = {
            "layer": L,
            "vq_ratios": vq_ratios,
            "q_norms": q_norms,
            "v_norms_kv": v_norms,
            "anchor_worker_class": classification,
            "mean_vq": mean_vq,
            "std_vq": std_vq,
            "killing_af": killing["af"],
            "killing_cv": killing["cv"],
            "head_commutator_contributions": killing["head_contributions"],
            "q_weight_kurtosis_mean": q_kurt,
        }
        survey_data["layers"].append(layer_data)
        n_anchor = classification.count("anchor")
        n_worker = classification.count("worker")
        n_neutral = classification.count("neutral")
        print(f"  L{L:2d}: AF={killing['af']:.3f}  CV={killing['cv']:.4f}  "
              f"anchor={n_anchor} worker={n_worker} neutral={n_neutral}  "
              f"q_kurt={q_kurt:.2f}")

    # Aggregate
    afs = [l["killing_af"] for l in survey_data["layers"]]
    cvs = [l["killing_cv"] for l in survey_data["layers"]]
    survey_data["summary"] = {
        "mean_af": float(np.mean(afs)),
        "mean_cv": float(np.mean(cvs)),
        "depth_af_gradient_slope": float(np.polyfit(range(len(afs)), afs, 1)[0]),
        "depth_cv_gradient_slope": float(np.polyfit(range(len(cvs)), cvs, 1)[0]),
        "total_anchor_heads": sum(l["anchor_worker_class"].count("anchor") for l in survey_data["layers"]),
        "total_worker_heads": sum(l["anchor_worker_class"].count("worker") for l in survey_data["layers"]),
        "total_neutral_heads": sum(l["anchor_worker_class"].count("neutral") for l in survey_data["layers"]),
    }

    return survey_data


if __name__ == "__main__":
    out = survey()
    # Save to results directory
    out_dir = Path(__file__).resolve().parent.parent.parent / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "gemma3_270m_topology_v07.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\n=== Survey complete ===")
    print(f"Saved: {out_path}")
    s = out["summary"]
    print(f"Mean AF: {s['mean_af']:.3f}  Mean CV: {s['mean_cv']:.4f}")
    print(f"Depth gradients: AF slope={s['depth_af_gradient_slope']:+.4f}/layer, "
          f"CV slope={s['depth_cv_gradient_slope']:+.6f}/layer")
    print(f"Heads: anchor={s['total_anchor_heads']}  worker={s['total_worker_heads']}  "
          f"neutral={s['total_neutral_heads']}")
