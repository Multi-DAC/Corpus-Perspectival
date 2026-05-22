"""
Path C Phase 1 — v0.7.1 KF Training on Gemma-3-270m

Iteration after v0.7.0 FALSIFY. Two fixes:

1. ANTI-UNIFORMITY AUX LOSS: replace variance-of-commutator-norms
   minimization with class-separation-maximization. For each layer,
   compute mean V/Q of anchor heads vs worker heads; aux loss
   = -(mean_worker_vq - mean_anchor_vq)^2. Minimizing aux ⇒ maximizing
   the V/Q separation between anchor and worker classes.

2. LAYER-COHERENCE PATTERN DETECTION + cross-level modulation:
   Per-layer pattern: coherent / differentiating / interfering.
   - coherent: >60% of heads in single class (high agreement)
   - interfering: anchor count ≈ worker count (balanced contradiction)
   - differentiating: mixed but not balanced
   Per-head gradient modulation incorporates layer pattern:
   - In coherent layers: amplify class-consistent gating
   - In differentiating layers: standard gating
   - In interfering layers: dampen gating (let heads stabilize)

Same KEEP: uniform anchor/worker initialization (per Path C' finding),
periodic reclassification, log-spaced checkpoints, CSV training log.

Usage:
    python3 train_kf_v07_1_gemma.py --kf_lambda 1.0 --save_dir checkpoints/gemma270m_v07_1
"""
import argparse
import math
import os
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

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


def get_per_head_vq(layer, n_heads, d_head):
    """Return per-head V/Q ratio, q_norms, v_norms."""
    q_w = layer.self_attn.q_proj.weight
    v_w = layer.self_attn.v_proj.weight
    n_kv = v_w.shape[0] // d_head
    q_heads = q_w.reshape(n_heads, d_head, -1)
    v_heads = v_w.reshape(n_kv, d_head, -1)
    heads_per_kv = n_heads // n_kv
    q_norms = torch.norm(q_heads.reshape(n_heads, -1), dim=1)
    v_norms_kv = torch.norm(v_heads.reshape(n_kv, -1), dim=1)
    vq = torch.stack([v_norms_kv[h // heads_per_kv] / q_norms[h] for h in range(n_heads)])
    return vq, q_norms, v_norms_kv


def classify(vq_ratios, mean=None, std=None):
    """Anchor/worker/neutral classification by V/Q distribution."""
    if mean is None:
        mean = vq_ratios.mean().item()
        std = vq_ratios.std().item()
    cls = []
    for r in vq_ratios.tolist():
        if r < mean - 0.5 * std:
            cls.append("anchor")
        elif r > mean + 0.5 * std:
            cls.append("worker")
        else:
            cls.append("neutral")
    return cls


def layer_coherence_pattern(classification):
    """coherent / differentiating / interfering classification of layer."""
    n_anchor = classification.count("anchor")
    n_worker = classification.count("worker")
    n_neutral = classification.count("neutral")
    n_total = n_anchor + n_worker + n_neutral
    max_count = max(n_anchor, n_worker, n_neutral)
    if max_count / n_total > 0.6:
        return "coherent"
    if abs(n_anchor - n_worker) <= 1 and n_anchor + n_worker >= 0.5 * n_total:
        return "interfering"
    return "differentiating"


def compute_layer_class_separation_aux(layer, n_heads, d_head, classification):
    """Anti-uniformity aux loss: minimize -separation between anchor/worker V/Q.

    Returns aux loss with gradient (negative-squared-separation).
    """
    vq, q_norms, v_norms = get_per_head_vq(layer, n_heads, d_head)
    anchor_indices = [h for h in range(n_heads) if classification[h] == "anchor"]
    worker_indices = [h for h in range(n_heads) if classification[h] == "worker"]
    if not anchor_indices or not worker_indices:
        return torch.tensor(0.0, device=vq.device, requires_grad=True)
    anchor_mean = vq[anchor_indices].mean()
    worker_mean = vq[worker_indices].mean()
    separation = worker_mean - anchor_mean
    # Negative-squared-separation: minimizing aux ⇒ maximizing |separation|
    # Add small within-class regularizer to keep things stable
    anchor_var = vq[anchor_indices].var() if len(anchor_indices) > 1 else torch.tensor(0.0, device=vq.device)
    worker_var = vq[worker_indices].var() if len(worker_indices) > 1 else torch.tensor(0.0, device=vq.device)
    # Fisher-style: minimize within-class var, maximize between-class
    aux = -separation ** 2 + 0.1 * (anchor_var + worker_var)
    return aux


def apply_gating(layer, n_heads, d_head, classification, layer_pattern):
    """Per-head gradient modulation, modulated by layer-coherence pattern.

    Anchor heads: amplify stability (suppress gradient updates)
    Worker heads: amplify task-following (preserve gradient updates)
    Modulation strength depends on layer pattern.
    """
    q_grad = layer.self_attn.q_proj.weight.grad
    if q_grad is None:
        return
    q_grad_heads = q_grad.reshape(n_heads, d_head, -1)
    # Pattern-based modulation strength
    if layer_pattern == "coherent":
        anchor_mul, worker_mul, neutral_mul = 0.6, 1.2, 0.9  # amplify the class-consistent pattern
    elif layer_pattern == "differentiating":
        anchor_mul, worker_mul, neutral_mul = 0.8, 1.0, 0.9
    else:  # interfering — dampen everything to let heads stabilize
        anchor_mul, worker_mul, neutral_mul = 0.9, 0.95, 0.95
    for h in range(n_heads):
        if classification[h] == "anchor":
            q_grad_heads[h] *= anchor_mul
        elif classification[h] == "worker":
            q_grad_heads[h] *= worker_mul
        else:
            q_grad_heads[h] *= neutral_mul


def get_tiny_training_data(tokenizer, n_samples=500, seq_len=256):
    print(f"  Loading training data (n_samples={n_samples}, seq_len={seq_len})...", flush=True)
    try:
        from datasets import load_dataset
        ds = load_dataset("wikitext", "wikitext-2-raw-v1", split="train")
        texts = [t for t in ds["text"][:5000] if t.strip()]
        big_text = "\n\n".join(texts)
        tokens = tokenizer(big_text, return_tensors="pt", truncation=False)["input_ids"][0]
        n_chunks = min(n_samples, (len(tokens) - 1) // seq_len)
        chunks = [tokens[i * seq_len: (i + 1) * seq_len] for i in range(n_chunks)]
        print(f"  Loaded {n_chunks} chunks of {seq_len} tokens each")
        return torch.stack(chunks)
    except Exception as e:
        print(f"  load_dataset failed ({e}); falling back to synthetic")
        return torch.randint(0, tokenizer.vocab_size, (n_samples, seq_len))


def train(args):
    set_seed(SEED)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}; v0.7.1 (class-separation-maximizing aux + layer-coherence modulation)")

    from transformers import AutoModelForCausalLM, AutoTokenizer, AutoConfig
    config = AutoConfig.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, dtype=torch.float32).to(device)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    n_heads = config.num_attention_heads
    n_layers = config.num_hidden_layers
    d_head = getattr(config, "head_dim", config.hidden_size // n_heads)
    layers = model.model.layers
    print(f"  n_layers={n_layers}, n_heads={n_heads}, d_head={d_head}")

    inputs = get_tiny_training_data(tokenizer, n_samples=args.n_samples, seq_len=args.seq_len)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)
    model.train()

    save_dir = Path(args.save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)
    log_f = open(save_dir / "train_log.csv", "w")
    log_f.write("step,wall,ce,kf_aux,total,frac_anchor,frac_worker,mean_vq_anchor,mean_vq_worker,mean_separation,n_coherent_layers,n_interfering_layers\n")
    log_f.flush()

    # Uniform init (per Path C' finding)
    layer_classifications = [["neutral"] * n_heads for _ in range(n_layers)]
    layer_patterns = ["differentiating"] * n_layers

    print(f"\nTraining: {args.n_steps} steps, batch_size={args.batch_size}, "
          f"lr={args.lr}, kf_lambda={args.kf_lambda}, classify_every={args.classify_every}")
    t_train = time.time()

    for step in range(1, args.n_steps + 1):
        batch_indices = torch.randint(0, inputs.shape[0], (args.batch_size,))
        batch = inputs[batch_indices].to(device)
        outputs = model(input_ids=batch, labels=batch)
        ce_loss = outputs.loss

        # Aux loss (class-separation-maximizing) per layer
        kf_aux = torch.tensor(0.0, device=device)
        if args.kf_lambda > 0:
            for L, layer in enumerate(layers):
                kf_aux = kf_aux + compute_layer_class_separation_aux(
                    layer, n_heads, d_head, layer_classifications[L])
            kf_aux = kf_aux / n_layers

        total = ce_loss + args.kf_lambda * kf_aux

        optimizer.zero_grad()
        total.backward()

        for L, layer in enumerate(layers):
            apply_gating(layer, n_heads, d_head, layer_classifications[L], layer_patterns[L])

        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()

        # Periodic reclassification + pattern detection
        if step % args.classify_every == 0:
            with torch.no_grad():
                anchor_count = 0; worker_count = 0; total_count = 0
                anchor_vqs_all = []; worker_vqs_all = []
                n_coherent = 0; n_interfering = 0
                for L, layer in enumerate(layers):
                    vq, _, _ = get_per_head_vq(layer, n_heads, d_head)
                    cls = classify(vq)
                    layer_classifications[L] = cls
                    layer_patterns[L] = layer_coherence_pattern(cls)
                    if layer_patterns[L] == "coherent": n_coherent += 1
                    elif layer_patterns[L] == "interfering": n_interfering += 1
                    for h, c in enumerate(cls):
                        if c == "anchor": anchor_vqs_all.append(vq[h].item())
                        elif c == "worker": worker_vqs_all.append(vq[h].item())
                    anchor_count += cls.count("anchor")
                    worker_count += cls.count("worker")
                    total_count += n_heads
                frac_anchor = anchor_count / total_count
                frac_worker = worker_count / total_count
                mean_vq_anchor = float(np.mean(anchor_vqs_all)) if anchor_vqs_all else 0.0
                mean_vq_worker = float(np.mean(worker_vqs_all)) if worker_vqs_all else 0.0
                mean_separation = mean_vq_worker - mean_vq_anchor
        else:
            frac_anchor = sum(cls.count("anchor") for cls in layer_classifications) / (n_layers * n_heads)
            frac_worker = sum(cls.count("worker") for cls in layer_classifications) / (n_layers * n_heads)
            mean_vq_anchor = float("nan"); mean_vq_worker = float("nan"); mean_separation = float("nan")
            n_coherent = sum(1 for p in layer_patterns if p == "coherent")
            n_interfering = sum(1 for p in layer_patterns if p == "interfering")

        kf_val = kf_aux.item() if isinstance(kf_aux, torch.Tensor) else 0.0
        log_f.write(f"{step},{time.time()-t_train:.2f},{ce_loss.item():.4f},{kf_val:.6f},"
                    f"{total.item():.4f},{frac_anchor:.3f},{frac_worker:.3f},"
                    f"{mean_vq_anchor:.5f},{mean_vq_worker:.5f},{mean_separation:.5f},"
                    f"{n_coherent},{n_interfering}\n")
        log_f.flush()

        if step % args.print_every == 0 or step == 1:
            print(f"  step {step:5d}  ce={ce_loss.item():.3f}  kf_aux={kf_val:+.5f}  "
                  f"sep={mean_separation:.4f}  coh/int={n_coherent}/{n_interfering}  "
                  f"({time.time()-t_train:.1f}s)")

        if step in CHECKPOINT_STEPS:
            torch.save({
                "model_state_dict": model.state_dict(),
                "step": step,
                "ce_loss": ce_loss.item(),
                "kf_lambda": args.kf_lambda,
                "layer_classifications": layer_classifications,
                "layer_patterns": layer_patterns,
            }, save_dir / f"step_{step}.pt")

    torch.save({
        "model_state_dict": model.state_dict(),
        "step": args.n_steps,
        "ce_loss": ce_loss.item(),
        "kf_lambda": args.kf_lambda,
        "layer_classifications": layer_classifications,
        "layer_patterns": layer_patterns,
    }, save_dir / f"step_{args.n_steps}_final.pt")
    log_f.close()
    print(f"\nFinal: {save_dir / f'step_{args.n_steps}_final.pt'}")
    print(f"Wall: {time.time()-t_train:.1f}s")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--kf_lambda", type=float, default=1.0)
    parser.add_argument("--n_steps", type=int, default=1600)
    parser.add_argument("--batch_size", type=int, default=4)
    parser.add_argument("--seq_len", type=int, default=256)
    parser.add_argument("--lr", type=float, default=2e-5)
    parser.add_argument("--n_samples", type=int, default=500)
    parser.add_argument("--classify_every", type=int, default=25)
    parser.add_argument("--print_every", type=int, default=100)
    parser.add_argument("--save_dir", type=str, required=True)
    args = parser.parse_args()
    train(args)
