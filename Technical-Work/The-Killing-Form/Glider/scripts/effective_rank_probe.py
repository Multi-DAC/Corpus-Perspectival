"""
Effective-rank probe — mechanism #3 test (anti-uniformity -> higher effective dimensionality).

Hypothesis: v0.7.1's Fisher-LDA aux pushes the V/Q distribution away from uniform, which may
raise the EFFECTIVE RANK of the layer representations -> concept directions have more room ->
faintly more orthogonal at readout. Direct causal pathway to the orthogonality finding.

Metric: participation ratio PR = (sum lambda)^2 / sum(lambda^2) of the activation covariance
eigenspectrum, per layer (hidden states). PR in [1, d_model]; higher = variance spread across
more dimensions. Same fixed inputs across all three models for fairness.

Prediction (#3): v0.7.1 PR > baseline PR (esp. at late/readout layers).
"""
import argparse, json
from pathlib import Path
import torch

PROMPTS = [
    "The history of mathematics begins with counting and measurement.",
    "She walked along the shore as the tide pulled the light apart.",
    "Quantum field theory unifies special relativity and quantum mechanics.",
    "The recipe calls for flour, butter, two eggs, and a pinch of salt.",
    "Economic incentives shape behavior in ways that are hard to predict.",
    "He repaired the engine, then drove through the night to the coast.",
    "Photosynthesis converts sunlight, water, and carbon dioxide into sugar.",
    "The orchestra tuned to the oboe before the conductor raised her baton.",
    "Distributed systems trade consistency against availability under partition.",
    "A coherent argument moves from premise to conclusion without a gap.",
    "The river carved the canyon over millions of slow patient years.",
    "Neural networks learn representations by minimizing a loss function.",
    "The treaty was signed at dawn after weeks of difficult negotiation.",
    "Crystals form when atoms arrange into a repeating lattice structure.",
    "Grief comes in waves, then quiet, then a wave you didn't expect.",
    "The compiler optimizes the loop by hoisting the invariant computation.",
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


def participation_ratio(X):
    # X: [N, d] activations. Center, covariance eigenspectrum, PR = (sum l)^2 / sum l^2.
    X = X - X.mean(dim=0, keepdim=True)
    C = (X.T @ X) / X.shape[0]
    lam = torch.linalg.eigvalsh(C).clamp(min=0)
    s = lam.sum()
    return float((s * s) / (lam.pow(2).sum() + 1e-12))


def probe(model, tok, dev):
    per_layer = None
    acc = None
    with torch.no_grad():
        for p in PROMPTS:
            ids = tok(p, return_tensors="pt").to(dev)
            out = model(**ids, output_hidden_states=True)
            hs = out.hidden_states  # tuple [n_layers+1] of [1, seq, d]
            if acc is None:
                acc = [[] for _ in range(len(hs))]
            for L, h in enumerate(hs):
                acc[L].append(h[0].float().cpu())  # [seq, d]
    per_layer = []
    for L in range(len(acc)):
        X = torch.cat(acc[L], dim=0)  # [total_tokens, d]
        per_layer.append(participation_ratio(X))
    d_model = model.config.hidden_size
    return {
        "d_model": d_model,
        "per_layer_PR": per_layer,
        "mean_PR": sum(per_layer) / len(per_layer),
        "last_layer_PR": per_layer[-1],
        "mean_PR_frac": (sum(per_layer) / len(per_layer)) / d_model,
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
    print(f"d_model={r['d_model']}  mean_PR={r['mean_PR']:.2f}  last_layer_PR={r['last_layer_PR']:.2f}  mean_PR_frac={r['mean_PR_frac']:.4f}")
    print(f"per-layer PR: {[round(x,1) for x in r['per_layer_PR']]}")
    Path(a.output).parent.mkdir(parents=True, exist_ok=True)
    json.dump({"model_id": a.model_id, "ckpt": a.ckpt, **r}, open(a.output, "w"), indent=2)
    print(f"Saved: {a.output}")


if __name__ == "__main__":
    main()
