"""
kf_glider_stability_probe.py — is the per-layer 'proto-glider' structure real or input-noise?

Tonight's gating-signal probe showed per-layer mean cos(grad_KF, grad_CE) varies (some
layers build-leaning, some dissolve-leaning). Question: is that pattern a property of the
WEIGHTS (stable across inputs -> latent structure the architecture exploits) or an artifact
of one forward pass (input-dependent -> the glider is dynamically created by gating)?

Test: compute the per-layer mean-cos vector for several diverse inputs; report pairwise
Pearson correlation across inputs. High corr -> stable/weight-property. Low -> input-driven.
"""
import argparse
import torch
import numpy as np
from kf_regularizer_gemma import kf_regularizer
from kf_gating_signal_probe import per_head_qgrad

TEXTS = [
    "Coherent multi-scale systems maintain structural superposition until measurement collapses them.",
    "The quick brown fox jumps over the lazy dog near the riverbank at dawn.",
    "import numpy as np; def solve(graph): return shortest_path(graph, source, target)",
    "She had never seen the ocean before, and now it stretched past every horizon she knew.",
    "The mitochondria generate ATP through oxidative phosphorylation across the inner membrane.",
]


def per_layer_meancos(model, tok, dev, text, n_heads, kf_lambda):
    ids = tok(text, return_tensors="pt", truncation=True, max_length=128).to(dev)
    out = model(**ids, labels=ids["input_ids"], output_attentions=True)
    ce = out.loss
    kf = kf_regularizer(out.attentions).sum()
    model.zero_grad(); ce.backward(retain_graph=True)
    ce_g = per_head_qgrad(model, n_heads)
    model.zero_grad(); (-kf_lambda * kf).backward()
    kf_g = per_head_qgrad(model, n_heads)
    bylayer = {}
    for k in ce_g:
        if k in kf_g:
            a, b = ce_g[k], kf_g[k]
            c = float(torch.dot(a, b) / (a.norm() * b.norm() + 1e-20))
            bylayer.setdefault(k[0], []).append(c)
    return np.array([np.mean(bylayer[L]) for L in sorted(bylayer)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model_id", default="google/gemma-3-270m")
    ap.add_argument("--kf_lambda", type=float, default=5.0)
    args = ap.parse_args()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tok = AutoTokenizer.from_pretrained(args.model_id)
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id, dtype=torch.float32, attn_implementation="eager").to(dev)
    model.train()
    n_heads = model.config.num_attention_heads

    patterns = []
    for i, t in enumerate(TEXTS):
        p = per_layer_meancos(model, tok, dev, t, n_heads, args.kf_lambda)
        patterns.append(p)
        print(f"text {i} ({t[:35]!r}...): " + " ".join(f"{x:+.2f}" for x in p))

    P = np.stack(patterns)  # [n_texts, n_layers]
    n = len(TEXTS)
    corrs = []
    for i in range(n):
        for j in range(i + 1, n):
            c = np.corrcoef(P[i], P[j])[0, 1]
            corrs.append(c)
    corrs = np.array(corrs)
    print(f"\npairwise Pearson r across inputs: mean={corrs.mean():.3f}  "
          f"min={corrs.min():.3f}  max={corrs.max():.3f}")
    # per-layer consistency: std across inputs per layer (low = stable lean)
    layer_std = P.std(axis=0)
    layer_mean = P.mean(axis=0)
    print("per-layer mean lean: " + " ".join(f"{m:+.2f}" for m in layer_mean))
    print("per-layer std(input): " + " ".join(f"{s:.2f}" for s in layer_std))
    # sign-stability: fraction of layers whose lean sign is consistent across all inputs
    sign_consistent = np.mean([len(set(np.sign(P[:, L]))) == 1 for L in range(P.shape[1])])
    print(f"fraction of layers with sign-consistent lean across all {n} inputs: {sign_consistent:.2f}")

    print(f"\nVERDICT: mean r={corrs.mean():.3f} -> " +
          ("STABLE structure (weight-property; architecture exploits pre-existing layer lean)"
           if corrs.mean() > 0.5 else
           "INPUT-DEPENDENT (glider dynamically created by gating, not pre-existing)"
           if corrs.mean() < 0.25 else "MIXED (partial stability)"))


if __name__ == "__main__":
    main()
