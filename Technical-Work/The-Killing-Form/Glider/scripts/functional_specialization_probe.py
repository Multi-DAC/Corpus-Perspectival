"""
Functional-specialization probe — mechanism #1 (activation-based).

Hypothesis: v0.7.1's anchor (low V/Q) and worker (high V/Q) head-classes perform
more DISTINCT functions -> their actual residual-stream WRITES (given real inputs)
are more orthogonal ACROSS classes than within -> contributes to readout orthogonality.

Activation-based on purpose: weight-DIRECTION analysis is doomed null (the aux moves
norms, not directions -- see OV-decorrelation §5). What can differ is what heads
actually write on data.

Method: hook each layer's o_proj INPUT (concatenated per-head attention outputs);
apply each head's W_O slice to get its per-token residual contribution; average over
tokens -> per-head mean-write vector. Classify heads anchor/worker by V/Q (weights).
Pool across layers; compute mean |cos| of within-class vs cross-class mean-write pairs.
class_sep = mean|cos|_within - mean|cos|_cross  (higher = classes more functionally distinct).

Prediction (#1): v0.7.1 class_sep > baseline.
"""
import argparse, json
from pathlib import Path
import numpy as np
import torch

PROMPTS = [
    "The history of mathematics begins with counting and measurement.",
    "Quantum field theory unifies special relativity and quantum mechanics.",
    "Economic incentives shape behavior in ways that are hard to predict.",
    "Photosynthesis converts sunlight, water, and carbon dioxide into sugar.",
    "Distributed systems trade consistency against availability under partition.",
    "The river carved the canyon over millions of slow patient years.",
    "Neural networks learn representations by minimizing a loss function.",
    "Crystals form when atoms arrange into a repeating lattice structure.",
]


def load(model_id, ckpt=None):
    from transformers import AutoModelForCausalLM, AutoTokenizer
    m = AutoModelForCausalLM.from_pretrained(model_id, dtype=torch.float32)
    tok = AutoTokenizer.from_pretrained(model_id)
    if ckpt:
        c = torch.load(ckpt, map_location="cpu", weights_only=False)
        m.load_state_dict(c["model_state_dict"])
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    m.to(dev).eval()
    return m, tok, dev


def classify_vq(layer, n_heads, d_head):
    qw = layer.self_attn.q_proj.weight.detach()
    vw = layer.self_attn.v_proj.weight.detach()
    n_kv = vw.shape[0] // d_head
    hpk = n_heads // n_kv
    qn = torch.norm(qw.reshape(n_heads, -1), dim=1)
    vn = torch.norm(vw.reshape(n_kv, -1), dim=1)
    vq = torch.stack([vn[h // hpk] / qn[h] for h in range(n_heads)])
    mu, sd = vq.mean().item(), vq.std().item()
    cls = []
    for r in vq.tolist():
        cls.append("anchor" if r < mu - 0.5 * sd else "worker" if r > mu + 0.5 * sd else "neutral")
    return cls


def probe(model, tok, dev):
    cfg = model.config
    d_model = cfg.hidden_size
    n_heads = cfg.num_attention_heads
    d_head = getattr(cfg, "head_dim", d_model // n_heads)
    layers = model.model.layers
    nL = len(layers)

    # accumulate per-head mean-write vectors across all tokens
    sums = [torch.zeros(n_heads, d_model) for _ in range(nL)]
    counts = [0 for _ in range(nL)]
    caches = {}

    def mk(L):
        def hook(mod, inp, out):
            caches[L] = inp[0].detach()  # [1, seq, n_heads*d_head]
        return hook

    handles = [layers[L].self_attn.o_proj.register_forward_hook(mk(L)) for L in range(nL)]
    try:
        with torch.no_grad():
            for p in PROMPTS:
                caches.clear()
                ids = tok(p, return_tensors="pt").to(dev)
                model(**ids)
                for L in range(nL):
                    x = caches[L][0].float().cpu()  # [seq, n_heads*d_head]
                    Wo = layers[L].self_attn.o_proj.weight.detach().float().cpu()  # [d_model, n_heads*d_head]
                    seq = x.shape[0]
                    for h in range(n_heads):
                        xh = x[:, h * d_head:(h + 1) * d_head]          # [seq, d_head]
                        Woh = Wo[:, h * d_head:(h + 1) * d_head]        # [d_model, d_head]
                        contrib = xh @ Woh.T                            # [seq, d_model]
                        sums[L][h] += contrib.sum(dim=0)
                    counts[L] += seq
    finally:
        for hd in handles:
            hd.remove()

    within, cross = [], []
    for L in range(nL):
        mw = sums[L] / max(counts[L], 1)                                # [n_heads, d_model] mean-write
        cls = classify_vq(layers[L], n_heads, d_head)
        norm = mw / (mw.norm(dim=1, keepdim=True) + 1e-8)
        for i in range(n_heads):
            for j in range(i + 1, n_heads):
                if cls[i] == "neutral" or cls[j] == "neutral":
                    continue
                c = float(abs((norm[i] * norm[j]).sum()))
                (within if cls[i] == cls[j] else cross).append(c)

    mw_within = float(np.mean(within)) if within else float("nan")
    mw_cross = float(np.mean(cross)) if cross else float("nan")
    return {
        "n_heads": n_heads, "d_head": d_head,
        "mean_abs_cos_within_class": mw_within,
        "mean_abs_cos_cross_class": mw_cross,
        "class_sep_index": mw_within - mw_cross,
        "n_within_pairs": len(within), "n_cross_pairs": len(cross),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model_id", required=True)
    ap.add_argument("--ckpt", default=None)
    ap.add_argument("--output", required=True)
    a = ap.parse_args()
    m, tok, dev = load(a.model_id, a.ckpt)
    r = probe(m, tok, dev)
    print(f"Model: {a.model_id} (ckpt: {a.ckpt or 'pristine'})")
    print(f"within-class |cos|={r['mean_abs_cos_within_class']:.4f}  cross-class |cos|={r['mean_abs_cos_cross_class']:.4f}  "
          f"class_sep={r['class_sep_index']:+.4f}  (within_pairs={r['n_within_pairs']}, cross_pairs={r['n_cross_pairs']})")
    Path(a.output).parent.mkdir(parents=True, exist_ok=True)
    json.dump({"model_id": a.model_id, "ckpt": a.ckpt, **r}, open(a.output, "w"), indent=2)
    print(f"Saved: {a.output}")


if __name__ == "__main__":
    main()
