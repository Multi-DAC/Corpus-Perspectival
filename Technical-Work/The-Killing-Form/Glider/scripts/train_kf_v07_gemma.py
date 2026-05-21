"""
Path C Phase 1 — Minimum-Viable v0.7 KF Training on Gemma-3-270m

First runnable v0.7 implementation on a standard transformer. Initializes
uniform anchor/worker priors per Path C' finding (KF training PRODUCES
decomposition rather than depending on pre-existing decomposition).

Scope of THIS version (minimum-viable; subsequent iterations add the
rest of the v0.7 design):
- Standard causal LM training loop (CE loss)
- KF auxiliary gradient: per-layer Killing-form-derived regularizer
  computed via random projection (proj_dim=64), pushing heads toward
  controlled heterogeneity
- Per-head V/Q ratio reclassification every K steps (anchor/worker/neutral)
- Per-head multiplicative gradient modulation:
    anchor heads: gradient * 0.8 (stability-favoring; slower update)
    worker heads: gradient * 1.0 (full gradient)
    neutral heads: gradient * 0.9
- Log-spaced checkpoint saves (steps 50, 100, 200, 400, 800, 1600)
- CSV log of per-layer CV + per-head V/Q over training

DEFERRED to subsequent v0.7 iterations:
- Bidirectional cross-level coordination (weight ↔ head ↔ layer)
- Glider dynamics tracking
- Lambda scheduling
- Mixed training data
- CNA-style probing evaluation (separate script)

Usage:
    python3 train_kf_v07_gemma.py --kf_lambda 0 --save_dir checkpoints/gemma270m_baseline
    python3 train_kf_v07_gemma.py --kf_lambda 1.0 --save_dir checkpoints/gemma270m_v07
"""
import argparse
import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader

# Reduce noise
os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

MODEL_ID = "google/gemma-3-270m"
PROJ_DIM = 64
SEED = 71
CHECKPOINT_STEPS = [50, 100, 200, 400, 800, 1600]


def set_seed(seed):
    torch.manual_seed(seed)
    np.random.seed(seed)
    torch.cuda.manual_seed_all(seed)


def get_per_head_qv(layer, n_heads, d_head):
    """Extract per-head Q and V weights from a Gemma attention layer.

    Gemma attention has q_proj, k_proj, v_proj as separate Linear layers.
    q_proj: [n_heads * d_head, d_model]
    v_proj: [n_kv_heads * d_head, d_model] (with GQA)
    """
    q_w = layer.self_attn.q_proj.weight.data
    v_w = layer.self_attn.v_proj.weight.data
    n_kv = v_w.shape[0] // d_head
    q_heads = q_w.reshape(n_heads, d_head, -1)
    v_heads = v_w.reshape(n_kv, d_head, -1)
    return q_heads, v_heads, n_kv


def classify_heads_for_layer(layer, n_heads, d_head):
    """Per-head V/Q ratio classification (anchor / worker / neutral).

    Returns: list of n_heads strings.
    """
    q_heads, v_heads, n_kv = get_per_head_qv(layer, n_heads, d_head)
    heads_per_kv = n_heads // n_kv
    q_norms = torch.norm(q_heads.reshape(n_heads, -1), dim=1).float()
    v_norms_kv = torch.norm(v_heads.reshape(n_kv, -1), dim=1).float()
    ratios = []
    for h in range(n_heads):
        kv_idx = h // heads_per_kv
        r = (v_norms_kv[kv_idx] / q_norms[h]).item() if q_norms[h] > 0 else 0.0
        ratios.append(r)
    arr = np.array(ratios)
    mean, std = float(arr.mean()), float(arr.std())
    classification = []
    for r in ratios:
        if r < mean - 0.5 * std:
            classification.append("anchor")
        elif r > mean + 0.5 * std:
            classification.append("worker")
        else:
            classification.append("neutral")
    return classification, ratios


def compute_layer_kf_aux_loss(layer, n_heads, d_head, proj_dim=PROJ_DIM):
    """Compute Killing-form auxiliary loss for one layer's attention heads.

    Pushes heads toward controlled heterogeneity by minimizing variance of
    pairwise commutator norms within the layer (encourages balanced
    head differentiation).

    Returns a scalar tensor with gradient.
    """
    q_w = layer.self_attn.q_proj.weight  # [n_heads * d_head, d_model]
    d_model = q_w.shape[1]
    q_heads = q_w.reshape(n_heads, d_head, d_model)

    device = q_w.device
    # Use a fixed projection per layer (seed determined to be stable across steps)
    g = torch.Generator(device="cpu").manual_seed(SEED + n_heads * 1000)
    p_out = (torch.randn(proj_dim, d_head, generator=g) / math.sqrt(d_head)).to(device)
    p_in = (torch.randn(d_model, proj_dim, generator=g) / math.sqrt(d_model)).to(device)

    proj = [p_out @ q_heads[h] @ p_in for h in range(n_heads)]

    # Pairwise commutator Frobenius norms
    norms_sq = []
    for h in range(n_heads):
        for hp in range(h + 1, n_heads):
            c = proj[h] @ proj[hp] - proj[hp] @ proj[h]
            norms_sq.append((c ** 2).sum())
    if not norms_sq:
        return torch.tensor(0.0, device=device, requires_grad=True)
    norms_sq = torch.stack(norms_sq)
    # Variance is the heterogeneity measure; lower variance = more uniform
    aux = norms_sq.var()
    return aux


def apply_per_head_gradient_modulation(layer, n_heads, d_head, classification):
    """Multiplicatively modulate gradients per-head based on classification.

    Modifies layer.self_attn.q_proj.weight.grad in place.
    """
    q_grad = layer.self_attn.q_proj.weight.grad
    if q_grad is None:
        return
    q_grad_heads = q_grad.reshape(n_heads, d_head, -1)
    for h in range(n_heads):
        if classification[h] == "anchor":
            q_grad_heads[h] *= 0.8
        elif classification[h] == "neutral":
            q_grad_heads[h] *= 0.9
        # worker: unchanged (1.0)


def get_tiny_training_data(tokenizer, n_samples=500, seq_len=256):
    """Generate tiny training corpus from WikiText-2 (or fall back to bundled samples)."""
    print(f"  Loading training data (n_samples={n_samples}, seq_len={seq_len})...", flush=True)
    try:
        from datasets import load_dataset
        ds = load_dataset("wikitext", "wikitext-2-raw-v1", split="train")
        # Concatenate texts and tokenize, then chunk
        texts = [t for t in ds["text"][:5000] if t.strip()]
        big_text = "\n\n".join(texts)
        tokens = tokenizer(big_text, return_tensors="pt", truncation=False)["input_ids"][0]
        n_chunks = min(n_samples, (len(tokens) - 1) // seq_len)
        chunks = []
        for i in range(n_chunks):
            chunk = tokens[i * seq_len: (i + 1) * seq_len]
            chunks.append(chunk)
        print(f"  Loaded {n_chunks} chunks of {seq_len} tokens each from WikiText-2")
        return torch.stack(chunks)
    except Exception as e:
        print(f"  load_dataset failed ({e}); falling back to synthetic data")
        # Synthetic fallback
        vocab_size = tokenizer.vocab_size
        return torch.randint(0, vocab_size, (n_samples, seq_len))


def train(args):
    set_seed(SEED)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    if device.type == "cuda":
        print(f"  CUDA: {torch.cuda.get_device_name(0)}, free={torch.cuda.mem_get_info()[0]/1e9:.1f}GB")

    # Load model + tokenizer
    print(f"\nLoading {MODEL_ID}...", flush=True)
    t0 = time.time()
    from transformers import AutoModelForCausalLM, AutoTokenizer, AutoConfig
    config = AutoConfig.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, dtype=torch.float32).to(device)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    n_heads = config.num_attention_heads
    n_kv_heads = getattr(config, "num_key_value_heads", n_heads)
    n_layers = config.num_hidden_layers
    d_head = getattr(config, "head_dim", config.hidden_size // n_heads)
    print(f"  loaded in {time.time()-t0:.1f}s; n_layers={n_layers}, n_heads={n_heads}, d_head={d_head}")

    # Locate layers
    layers = model.model.layers
    assert len(layers) == n_layers

    # Training data
    inputs = get_tiny_training_data(tokenizer, n_samples=args.n_samples, seq_len=args.seq_len)
    print(f"  Training corpus: {inputs.shape}")

    # Optimizer
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)
    model.train()

    # Save directory + log file
    save_dir = Path(args.save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)
    log_path = save_dir / "train_log.csv"
    log_f = open(log_path, "w")
    log_f.write("step,wall_seconds,ce_loss,kf_aux_loss,total_loss,mean_layer_cv,frac_anchor,frac_worker\n")
    log_f.flush()

    # Initial uniform classification (per Path C' finding: KF training PRODUCES decomposition)
    layer_classifications = [["neutral"] * n_heads for _ in range(n_layers)]

    print(f"\nTraining: {args.n_steps} steps, batch_size={args.batch_size}, "
          f"lr={args.lr}, kf_lambda={args.kf_lambda}, classify_every={args.classify_every}")
    t_train = time.time()
    batch_idx = 0

    for step in range(1, args.n_steps + 1):
        # Sample batch (random sample with replacement from corpus chunks)
        batch_indices = torch.randint(0, inputs.shape[0], (args.batch_size,))
        batch = inputs[batch_indices].to(device)

        # Forward pass — standard CE loss (labels = inputs shifted)
        outputs = model(input_ids=batch, labels=batch)
        ce_loss = outputs.loss

        # KF auxiliary loss across layers
        kf_aux = torch.tensor(0.0, device=device)
        if args.kf_lambda > 0:
            for layer in layers:
                kf_aux = kf_aux + compute_layer_kf_aux_loss(layer, n_heads, d_head)
            kf_aux = kf_aux / n_layers

        total = ce_loss + args.kf_lambda * kf_aux

        # Backward
        optimizer.zero_grad()
        total.backward()

        # Per-head gradient modulation based on current classification
        for L, layer in enumerate(layers):
            apply_per_head_gradient_modulation(layer, n_heads, d_head, layer_classifications[L])

        # Gradient clipping
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()

        # Periodic reclassification
        if step % args.classify_every == 0:
            with torch.no_grad():
                anchor_count = 0
                worker_count = 0
                total_count = 0
                cvs = []
                for L, layer in enumerate(layers):
                    cls, ratios = classify_heads_for_layer(layer, n_heads, d_head)
                    layer_classifications[L] = cls
                    anchor_count += cls.count("anchor")
                    worker_count += cls.count("worker")
                    total_count += n_heads
                    arr = np.array(ratios)
                    cvs.append(float(np.var(arr)))
                frac_anchor = anchor_count / total_count
                frac_worker = worker_count / total_count
                mean_cv = float(np.mean(cvs))
        else:
            frac_anchor = sum(cls.count("anchor") for cls in layer_classifications) / (n_layers * n_heads)
            frac_worker = sum(cls.count("worker") for cls in layer_classifications) / (n_layers * n_heads)
            mean_cv = float("nan")

        # Log
        log_f.write(f"{step},{time.time()-t_train:.2f},{ce_loss.item():.4f},"
                    f"{kf_aux.item() if isinstance(kf_aux, torch.Tensor) else 0:.6f},"
                    f"{total.item():.4f},{mean_cv:.6f},{frac_anchor:.3f},{frac_worker:.3f}\n")
        log_f.flush()

        if step % args.print_every == 0 or step == 1:
            print(f"  step {step:5d}  ce={ce_loss.item():.3f}  kf_aux={kf_aux.item() if isinstance(kf_aux, torch.Tensor) else 0:.4f}  "
                  f"total={total.item():.3f}  anchor%={100*frac_anchor:.1f}  worker%={100*frac_worker:.1f}  "
                  f"({time.time()-t_train:.1f}s)")

        # Checkpoint saves at log-spaced steps
        if step in CHECKPOINT_STEPS:
            ckpt_path = save_dir / f"step_{step}.pt"
            torch.save({
                "model_state_dict": model.state_dict(),
                "step": step,
                "ce_loss": ce_loss.item(),
                "kf_lambda": args.kf_lambda,
                "layer_classifications": layer_classifications,
            }, ckpt_path)
            print(f"    saved checkpoint: {ckpt_path}")

    # Final save
    final_path = save_dir / f"step_{args.n_steps}_final.pt"
    torch.save({
        "model_state_dict": model.state_dict(),
        "step": args.n_steps,
        "ce_loss": ce_loss.item(),
        "kf_lambda": args.kf_lambda,
        "layer_classifications": layer_classifications,
    }, final_path)
    print(f"\nFinal checkpoint: {final_path}")
    log_f.close()
    print(f"Train log: {log_path}")
    print(f"Wall time: {time.time()-t_train:.1f}s")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--kf_lambda", type=float, default=0.0,
                        help="Weight on KF auxiliary loss (0=baseline)")
    parser.add_argument("--n_steps", type=int, default=1600)
    parser.add_argument("--batch_size", type=int, default=4)
    parser.add_argument("--seq_len", type=int, default=256)
    parser.add_argument("--lr", type=float, default=2e-5)
    parser.add_argument("--n_samples", type=int, default=500)
    parser.add_argument("--classify_every", type=int, default=50)
    parser.add_argument("--print_every", type=int, default=25)
    parser.add_argument("--save_dir", type=str, required=True)
    args = parser.parse_args()
    train(args)
