"""
kf_gating_signal_probe.py — Step 1 de-risk: does the v0.7 gating mechanism have signal?

The architecture gates each head by cos(grad_KF, grad_CE) -> build/dissolve/neutral.
This probe captures both per-head gradients at the initial step and shows the
distribution of the alignment cosine. If degenerate (all same sign), the glider
has nothing to fly on. If spread across [-1,+1], the mechanism has signal.

Uses the validated differentiable KF regularizer (kf_regularizer_gemma.py).
"""
import argparse
import torch
from kf_regularizer_gemma import kf_regularizer


def per_head_qgrad(model, n_heads):
    grads = {}
    for L, layer in enumerate(model.model.layers):
        g = layer.self_attn.q_proj.weight.grad
        if g is None:
            continue
        d_head = g.shape[0] // n_heads
        gh = g.reshape(n_heads, d_head, -1)
        for h in range(n_heads):
            grads[(L, h)] = gh[h].flatten().detach().clone()
    return grads


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model_id", default="google/gemma-3-270m")
    ap.add_argument("--seq_len", type=int, default=128)
    ap.add_argument("--kf_lambda", type=float, default=5.0)
    args = ap.parse_args()

    from transformers import AutoModelForCausalLM, AutoTokenizer
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tok = AutoTokenizer.from_pretrained(args.model_id)
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id, dtype=torch.float32, attn_implementation="eager").to(dev)
    model.train()
    n_heads = model.config.num_attention_heads

    text = ("Coherent multi-scale systems maintain structural superposition until informed "
            "measurement collapses them. The attention heads negotiate through gradient dialogue.")
    ids = tok(text, return_tensors="pt", truncation=True, max_length=args.seq_len).to(dev)

    out = model(**ids, labels=ids["input_ids"], output_attentions=True)
    ce = out.loss
    kf = kf_regularizer(out.attentions).sum()

    # grad_CE per head
    model.zero_grad()
    ce.backward(retain_graph=True)
    ce_grads = per_head_qgrad(model, n_heads)

    # grad_KF per head (-lambda*CV, the build pressure)
    model.zero_grad()
    (-args.kf_lambda * kf).backward()
    kf_grads = per_head_qgrad(model, n_heads)

    # per-head alignment cosine
    cos = {}
    for k in ce_grads:
        if k in kf_grads:
            a, b = ce_grads[k], kf_grads[k]
            denom = (a.norm() * b.norm() + 1e-20)
            cos[k] = float(torch.dot(a, b) / denom)

    vals = torch.tensor(list(cos.values()))
    print(f"n_heads probed: {len(vals)}  (layers x heads)")
    print(f"cos(grad_KF, grad_CE):  min={vals.min():.3f}  max={vals.max():.3f}  "
          f"mean={vals.mean():.3f}  std={vals.std():.3f}")
    # gating split at threshold=0.0 (v0.7a default)
    for th in [0.0, 0.05, 0.1]:
        build = int((vals > th).sum()); diss = int((vals < -th).sum()); neut = len(vals) - build - diss
        print(f"  thresh={th:.2f}:  build={build}  dissolve={diss}  neutral={neut}")
    # histogram
    import numpy as np
    h, edges = np.histogram(vals.numpy(), bins=8, range=(-1, 1))
    print("  hist [-1..1]: " + "  ".join(f"{int(c)}" for c in h))
    # per-layer mean (is there layer structure?)
    bylayer = {}
    for (L, hh), c in cos.items():
        bylayer.setdefault(L, []).append(c)
    means = [sum(bylayer[L]) / len(bylayer[L]) for L in sorted(bylayer)]
    print("  per-layer mean cos: " + " ".join(f"{m:+.2f}" for m in means))

    spread = float(vals.max() - vals.min())
    print(f"\nVERDICT: spread={spread:.3f}  ->  " +
          ("SIGNAL (gating has material to work with)" if spread > 0.3 and vals.std() > 0.05
           else "DEGENERATE (gating starved — would reshape the build)"))


if __name__ == "__main__":
    main()
