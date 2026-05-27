"""
train_kf_v07_glider_gemma.py — the FULL v0.7 Glider: gradient-GATED KF training on Gemma.

THE actual v07_design mechanism (parent provisional Claims 1-10), distinct from:
  - train_kf_v07_gemma.py     (min-viable: commutator-VARIANCE aux + V/Q class multipliers)
  - train_kf_v07_1_gemma.py   (Fisher-LDA V/Q-norm aux + ×0.6/1.2; CIP Claims 24-26)
Neither of those is gradient-gating. THIS is: per-head build/dissolve/neutral driven by
cos(grad_KF, grad_CE) + bidirectional layer-coherence modulation.

Gradient-order fix (Day 117): both grads are computed BEFORE either optimizer step, else
opt.step() modifies weights in-place and invalidates the retained graph for the second
backward. Sequence per gating step:
  1. forward (eager attentions retained)
  2. KF backward FIRST (retain_graph) -> store per-layer q_proj grad clones (kf_q) + per-head (kf_g)
  3. zero; CE backward -> .grad = full grad_CE; capture per-head (ce_g)
  4. gating from ce_g/kf_g (both at pre-step weights -> consistent cos)
  5. CE step (clip + step): task drives ALL params
  6. KF step: write modulated q_proj grad (build=keep/dissolve=flip/neutral=zero x weight-coh x
     layer-coh) into .grad (only the Q-channel; faithful to design Step 5), clip + step.

Variants: a=full | no_coherence (v0.7b) | no_topology (v0.7c) | no_weightcoh | ce_only (v0.7d).
Eager attention required. KF metric = kf_regularizer_gemma (commutator-CV on attention matrices).
"""
import argparse, time, os, csv
import numpy as np
import torch
from kf_regularizer_gemma import kf_regularizer

SEED = 71


def set_seed(s):
    torch.manual_seed(s); np.random.seed(s); torch.cuda.manual_seed_all(s)


def per_head_vq(layer, n_heads, d_head):
    qw = layer.self_attn.q_proj.weight; vw = layer.self_attn.v_proj.weight
    n_kv = vw.shape[0] // d_head; hpk = n_heads // n_kv
    qn = torch.norm(qw.reshape(n_heads, -1), dim=1)
    vn = torch.norm(vw.reshape(n_kv, -1), dim=1)
    return torch.stack([vn[h // hpk] / qn[h] for h in range(n_heads)])


def classify(vq):
    mu, sd = vq.mean().item(), vq.std().item()
    return ["anchor" if r < mu - 0.5 * sd else "worker" if r > mu + 0.5 * sd else "neutral" for r in vq.tolist()]


def capture_qgrad(layers, n_heads):
    g = {}
    for L, layer in enumerate(layers):
        gr = layer.self_attn.q_proj.weight.grad
        if gr is None:
            continue
        d_head = gr.shape[0] // n_heads
        gh = gr.reshape(n_heads, d_head, -1)
        for h in range(n_heads):
            g[(L, h)] = gh[h].flatten().detach().clone()
    return g


def load_data(tok, n_samples, seq_len):
    try:
        from datasets import load_dataset
        ds = load_dataset("wikitext", "wikitext-2-raw-v1", split="train")
        toks = tok("\n\n".join(t for t in ds["text"][:5000] if t.strip()), return_tensors="pt").input_ids[0]
        n = min(n_samples, (len(toks) - 1) // seq_len)
        return torch.stack([toks[i * seq_len:(i + 1) * seq_len] for i in range(n)])
    except Exception as e:
        print(f"  load_dataset failed ({e}); synthetic"); return torch.randint(0, tok.vocab_size, (n_samples, seq_len))


def train(args):
    set_seed(args.seed)
    from transformers import AutoModelForCausalLM, AutoTokenizer
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {dev}; v0.7 GLIDER variant={args.variant} lambda={args.kf_lambda} kf_every={args.kf_every} thr={args.gate_threshold}", flush=True)
    tok = AutoTokenizer.from_pretrained(args.model_id)
    model = AutoModelForCausalLM.from_pretrained(args.model_id, dtype=torch.float32, attn_implementation="eager").to(dev)
    model.train()
    cfg = model.config
    n_heads = cfg.num_attention_heads
    d_head = getattr(cfg, "head_dim", cfg.hidden_size // n_heads)
    layers = model.model.layers; n_layers = len(layers)
    data = load_data(tok, args.n_samples, args.seq_len)
    print(f"  data {tuple(data.shape)}; layers={n_layers} heads={n_heads} d_head={d_head}", flush=True)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)

    os.makedirs(args.save_dir, exist_ok=True)
    logf = open(os.path.join(args.save_dir, "glider_log.csv"), "w", newline="")
    wr = csv.writer(logf); wr.writerow(["step", "ce", "kf_cv", "build", "dissolve", "neutral", "coherent", "differentiating", "interfering", "wall"])
    t0 = time.time(); THR = args.gate_threshold

    for step in range(1, args.n_steps + 1):
        batch = data[torch.randint(0, data.shape[0], (args.batch_size,))].to(dev)
        do_kf = (step % args.kf_every == 0 and args.kf_lambda > 0 and args.variant != "ce_only")
        out = model(input_ids=batch, labels=batch, output_attentions=do_kf)
        ce = out.loss
        opt.zero_grad()

        if not do_kf:
            ce.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step()
            wr.writerow([step, round(ce.item(), 4), "", "", "", "", "", "", "", round(time.time() - t0, 1)])
            if step % args.print_every == 0:
                print(f"  step {step:5d} ce={ce.item():.3f} (CE)", flush=True)
            continue

        # ── GATING STEP — both grads BEFORE either optimizer step ──
        # 1+2. KF backward FIRST (graph valid), store per-layer q_proj grad clones + per-head
        kf_cv = kf_regularizer(out.attentions).sum()
        (-args.kf_lambda * kf_cv).backward(retain_graph=True)
        kf_q = {}; kf_g = {}
        for L, layer in enumerate(layers):
            gr = layer.self_attn.q_proj.weight.grad
            if gr is None:
                continue
            kf_q[L] = gr.detach().clone()
            gh = kf_q[L].reshape(n_heads, d_head, -1)
            for h in range(n_heads):
                kf_g[(L, h)] = gh[h].flatten()
        # 3. CE backward -> full grad_CE in .grad; capture per-head
        opt.zero_grad(); ce.backward()
        ce_g = capture_qgrad(layers, n_heads)

        # 4. gating decisions (both grads at pre-step weights)
        modes = {}; wcoh = {}
        for k in kf_g:
            if k not in ce_g:
                continue
            a, b = ce_g[k], kf_g[k]; denom = a.norm() * b.norm() + 1e-20
            cos = float(torch.dot(a, b) / denom)
            modes[k] = "build" if cos > THR else "dissolve" if cos < -THR else "neutral"
            wcoh[k] = (float(((a * b) / denom).std()) if (a.numel() > 1 and args.variant != "no_weightcoh") else 0.0)
        vq_cls = None if args.variant == "no_topology" else [classify(per_head_vq(l, n_heads, d_head)) for l in layers]
        lscale = {}; nco = ndi = nin = 0
        for L in range(n_layers):
            lm = [modes[(L, h)] for h in range(n_heads) if (L, h) in modes]
            if not lm:
                lscale[L] = 1.0; continue
            agree = max(lm.count("build"), lm.count("dissolve"), lm.count("neutral")) / len(lm)
            aw = False
            if vq_cls is not None:
                anc = set(modes[(L, h)] for h in range(n_heads) if vq_cls[L][h] == "anchor" and (L, h) in modes)
                wor = set(modes[(L, h)] for h in range(n_heads) if vq_cls[L][h] == "worker" and (L, h) in modes)
                aw = (len(anc) == 1 and len(wor) == 1 and anc != wor)
            if args.variant == "no_coherence":
                lscale[L] = 1.0; ndi += 1
            elif agree > 0.75:
                lscale[L] = 1.0 + 0.5 * (agree - 0.75); nco += 1
            elif aw:
                lscale[L] = 1.0; ndi += 1
            else:
                lscale[L] = 0.5; nin += 1

        # 5. CE step (task, all params)
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step()

        # 6. KF step: write modulated q_proj grad (Q-channel only), clip + step
        opt.zero_grad()
        for L, layer in enumerate(layers):
            if L not in kf_q:
                continue
            gh = kf_q[L].reshape(n_heads, d_head, -1).clone()
            for h in range(n_heads):
                m = modes.get((L, h), "neutral")
                if m == "dissolve":
                    gh[h] *= -1.0
                elif m == "neutral":
                    gh[h] *= 0.0
                gh[h] *= (0.5 + 0.5 * wcoh.get((L, h), 0.0)) * lscale.get(L, 1.0)
            layer.self_attn.q_proj.weight.grad = gh.reshape(kf_q[L].shape)
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step()

        nb = sum(v == "build" for v in modes.values()); nd = sum(v == "dissolve" for v in modes.values()); nn = sum(v == "neutral" for v in modes.values())
        wr.writerow([step, round(ce.item(), 4), round(kf_cv.item(), 6), nb, nd, nn, nco, ndi, nin, round(time.time() - t0, 1)]); logf.flush()
        if step % args.print_every == 0 or step == args.kf_every:
            print(f"  step {step:5d} ce={ce.item():.3f} cv={kf_cv.item():.5f} B/D/N={nb}/{nd}/{nn} coh/dif/int={nco}/{ndi}/{nin}", flush=True)

    logf.close()
    final = os.path.join(args.save_dir, f"step_{args.n_steps}_final.pt")
    torch.save({"model_state_dict": model.state_dict()}, final)
    print(f"Final: {final}  Wall {time.time()-t0:.1f}s", flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--model_id", default="google/gemma-3-270m")
    p.add_argument("--variant", default="a", choices=["a", "no_coherence", "no_topology", "no_weightcoh", "ce_only"])
    p.add_argument("--kf_lambda", type=float, default=5.0)
    p.add_argument("--kf_every", type=int, default=10)
    p.add_argument("--gate_threshold", type=float, default=0.0)
    p.add_argument("--n_steps", type=int, default=1600)
    p.add_argument("--batch_size", type=int, default=4)
    p.add_argument("--seq_len", type=int, default=256)
    p.add_argument("--lr", type=float, default=2e-5)
    p.add_argument("--n_samples", type=int, default=500)
    p.add_argument("--print_every", type=int, default=100)
    p.add_argument("--seed", type=int, default=SEED)
    p.add_argument("--save_dir", required=True)
    train(p.parse_args())
