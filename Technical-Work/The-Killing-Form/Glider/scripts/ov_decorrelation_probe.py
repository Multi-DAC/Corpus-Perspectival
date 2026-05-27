"""
OV-decorrelation probe — mechanistic test for the v0.7.1 -> orthogonality link.

Hypothesis (MECHANISTIC_INTERP_v07_1.md, mechanism #2): Fisher-separating per-head
V/Q norm ratios decorrelates OV-circuit write-directions across heads, which would
orthogonalize residual contributions and hence readout concept geometry.

Measure: per layer, the per-head OV write-operator  M_h = W_O^h @ W_V^{kv(h)}
(d_model x d_model; the residual->residual map the head writes through).
Decorrelation = mean pairwise |cosine| of vec(M_h) across head pairs.
LOWER mean |cos| = more decorrelated write-operators = consistent with mechanism #2.

Prediction: v0.7.1 mean |cos| < baseline mean |cos|.

CAVEATS (stated, not hidden):
- GQA handled by mapping each query head to its kv group for W_V.
- W_O enters only via CE (aux/gating touch q_proj/v_proj); decorrelation via this metric
  would be partly CE-mediated. This is a FIRST probe, not a mechanism proof.
- Weight-space metric (not activation-weighted); a follow-up could weight by activation stats.
"""
import argparse, json
from pathlib import Path
import numpy as np
import torch


def load(model_id, ckpt=None):
    from transformers import AutoModelForCausalLM
    m = AutoModelForCausalLM.from_pretrained(model_id, dtype=torch.float32)
    if ckpt:
        c = torch.load(ckpt, map_location="cpu", weights_only=False)
        m.load_state_dict(c["model_state_dict"])
    m.eval()
    return m


def probe(model):
    cfg = model.config
    d_model = cfg.hidden_size
    n_heads = cfg.num_attention_heads
    n_kv = getattr(cfg, "num_key_value_heads", n_heads)
    d_head = getattr(cfg, "head_dim", d_model // n_heads)
    heads_per_kv = n_heads // n_kv
    layers = model.model.layers

    per_layer_meancos = []
    for L, layer in enumerate(layers):
        Wo = layer.self_attn.o_proj.weight.detach()  # [d_model, n_heads*d_head]
        Wv = layer.self_attn.v_proj.weight.detach()   # [n_kv*d_head, d_model]
        vecs = []
        for h in range(n_heads):
            Wo_h = Wo[:, h * d_head:(h + 1) * d_head]              # [d_model, d_head]
            kv = h // heads_per_kv
            Wv_kv = Wv[kv * d_head:(kv + 1) * d_head, :]           # [d_head, d_model]
            M = (Wo_h @ Wv_kv).reshape(-1)                          # [d_model*d_model]
            n = M.norm()
            vecs.append((M / n) if n > 0 else M)
        V = torch.stack(vecs)                                      # [n_heads, D]
        cos = V @ V.T                                              # [n_heads, n_heads]
        off = cos[~torch.eye(n_heads, dtype=bool)]
        per_layer_meancos.append(float(off.abs().mean()))

    return {
        "dims": {"d_model": d_model, "n_heads": n_heads, "n_kv": n_kv, "d_head": d_head},
        "per_layer_mean_abs_cos": per_layer_meancos,
        "mean_abs_cos": float(np.mean(per_layer_meancos)),
        "max_abs_cos": float(np.max(per_layer_meancos)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model_id", required=True)
    ap.add_argument("--ckpt", default=None)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    m = load(args.model_id, args.ckpt)
    r = probe(m)
    print(f"Model: {args.model_id} (ckpt: {args.ckpt or 'pristine'})")
    print(f"dims: {r['dims']}")
    print(f"mean |cos| of OV write-operators (lower=more decorrelated): {r['mean_abs_cos']:.4f}")
    print(f"per-layer: {[round(x,3) for x in r['per_layer_mean_abs_cos']]}")
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    json.dump({"model_id": args.model_id, "ckpt": args.ckpt, **r}, open(args.output, "w"), indent=2)
    print(f"Saved: {args.output}")


if __name__ == "__main__":
    main()
