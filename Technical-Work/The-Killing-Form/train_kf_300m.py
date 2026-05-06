"""
Phase 4A-bis: 300M HRM Scale Validation — KF-Decoupled Training

Scaling the KF program from 27.3M to 308.3M parameters.
Architecture: H=12 layers, L=12 layers, hidden=1024, heads=16 (hrm_v2.yaml)

This script runs EITHER baseline (--kf_lambda 0) or KF-decoupled training.
Supports lambda scheduling: constant, cosine decay, linear decay.

Examples:
  # Baseline
  python train_kf_300m.py --kf_lambda 0 --save_dir checkpoints/300m_baseline

  # Fixed lambda
  python train_kf_300m.py --kf_lambda 1.0 --save_dir checkpoints/300m_kf_fixed

  # Cosine decay lambda (1.0 -> 0.01)
  python train_kf_300m.py --kf_lambda 1.0 --lambda_schedule cosine --lambda_min 0.01 \
    --save_dir checkpoints/300m_kf_cosine
"""
import sys
import os
import json
import time
import math
import argparse
import numpy as np
import torch
import torch.nn.functional as F

sys.path.insert(0, "/home/clawd/HRM")
sys.stdout.reconfigure(line_buffering=True)

from omegaconf import OmegaConf
from torch.utils.data import DataLoader
from puzzle_dataset import PuzzleDataset, PuzzleDatasetConfig, PuzzleDatasetMetadata
from utils.functions import load_model_class
from adam_atan2_fallback import AdamATan2


# --- LAMBDA SCHEDULING ---

def compute_lambda(base_lambda, lambda_min, schedule, progress):
    """
    Compute current lambda value based on schedule and training progress.

    Args:
        base_lambda: Initial/maximum lambda value
        lambda_min: Minimum lambda value (floor)
        schedule: 'constant', 'cosine', or 'linear'
        progress: Fraction of training completed (0.0 to 1.0)

    Returns:
        Current lambda value
    """
    if schedule == "constant":
        return base_lambda
    elif schedule == "cosine":
        return lambda_min + 0.5 * (base_lambda - lambda_min) * (1 + math.cos(math.pi * progress))
    elif schedule == "linear":
        return base_lambda - (base_lambda - lambda_min) * progress
    else:
        raise ValueError("Unknown schedule: %s" % schedule)


# --- MODEL BUILDING ---

def build_model(arch_cfg, num_puzzle_ids, device, vocab_size=11, seq_len=81, batch_size=64):
    arch_resolved = OmegaConf.to_container(arch_cfg, resolve=True)
    hidden_size = arch_resolved.get("hidden_size", 1024)
    if isinstance(arch_resolved.get("puzzle_emb_ndim"), str):
        arch_resolved["puzzle_emb_ndim"] = hidden_size
    model_cfg = {
        **arch_resolved, "vocab_size": vocab_size, "max_seq_len": seq_len,
        "batch_size": batch_size, "seq_len": seq_len,
        "num_puzzle_identifiers": num_puzzle_ids, "causal": False,
    }
    loss_cfg = model_cfg.pop("loss", {})
    loss_type = loss_cfg.get("loss_type", "stablemax_cross_entropy")
    model_name = model_cfg.pop("name", "")
    model_cls = load_model_class(model_name)
    loss_head_cls = load_model_class(loss_cfg.get("name", "losses@ACTLossHead"))
    with torch.device(device):
        raw_model = model_cls(model_cfg)
        loss_extra = {k: v for k, v in loss_cfg.items() if k not in ("name", "loss_type")}
        model = loss_head_cls(raw_model, loss_type=loss_type, **loss_extra)
    return model, raw_model


def create_dataloader(data_path, split, batch_size, epochs_per_iter=1):
    ds_cfg = PuzzleDatasetConfig(
        seed=42, dataset_path=data_path, test_set_mode=(split == "test"),
        epochs_per_iter=epochs_per_iter, global_batch_size=batch_size,
        rank=0, num_replicas=1,
    )
    dataset = PuzzleDataset(ds_cfg, split=split)
    return DataLoader(dataset, batch_size=None, num_workers=0, pin_memory=True), dataset.metadata


# --- KF MEASUREMENT (detached, per-layer for 300M efficiency) ---

def extract_attention_weights(model):
    heads = {"H": [], "L": []}
    for module_name, module in [("H", model.inner.H_level), ("L", model.inner.L_level)]:
        for layer_idx, layer in enumerate(module.layers):
            W = layer.self_attn.qkv_proj.weight.detach().float().cpu()
            num_heads = layer.self_attn.num_heads
            head_dim = layer.self_attn.head_dim
            W_Q = W[:num_heads * head_dim, :]
            W_K = W[num_heads * head_dim: 2 * num_heads * head_dim, :]
            for h in range(num_heads):
                q_h = W_Q[h * head_dim:(h + 1) * head_dim, :]
                k_h = W_K[h * head_dim:(h + 1) * head_dim, :]
                W_h = q_h.T @ k_h
                heads[module_name].append({"layer": layer_idx, "head": h, "W": W_h})
    return heads


def measure_kf(model, step_label):
    heads = extract_attention_weights(model)
    results = {}
    for module_name in ["H", "L"]:
        h_list = heads[module_name]
        layers = sorted(set(h["layer"] for h in h_list))
        per_layer = {}
        all_norms = []
        for layer in layers:
            lh = [h for h in h_list if h["layer"] == layer]
            layer_norms = []
            n = len(lh)
            for i in range(n):
                for j in range(i + 1, n):
                    comm = lh[i]["W"] @ lh[j]["W"] - lh[j]["W"] @ lh[i]["W"]
                    layer_norms.append(torch.norm(comm, p="fro").item())
            per_layer[int(layer)] = {
                "cv": float(np.var(layer_norms)) if layer_norms else 0.0,
                "mean_norm": float(np.mean(layer_norms)) if layer_norms else 0.0,
            }
            all_norms.extend(layer_norms)
        global_cv = float(np.var(all_norms)) if all_norms else 0.0
        global_mean = float(np.mean(all_norms)) if all_norms else 0.0
        global_af = 0.0
        if all_norms:
            norms_arr = np.array(all_norms)
            max_n = np.max(norms_arr) if len(norms_arr) > 0 else 1.0
            global_af = float(np.sum(norms_arr < 1e-6 * max_n) / len(norms_arr))
        results[module_name] = {
            "cv": global_cv, "mean_norm": global_mean, "af": global_af, "per_layer": per_layer,
        }
    cross_norms = []
    h_heads = heads["H"]
    l_heads = heads["L"]
    n_sample = min(16, len(h_heads))
    h_sample = np.random.choice(len(h_heads), n_sample, replace=False)
    l_sample = np.random.choice(len(l_heads), n_sample, replace=False)
    for hi in h_sample:
        for li in l_sample:
            comm = h_heads[hi]["W"] @ l_heads[li]["W"] - l_heads[li]["W"] @ h_heads[hi]["W"]
            cross_norms.append(torch.norm(comm, p="fro").item())
    h_cv = results["H"]["cv"]
    l_cv = results["L"]["cv"]
    results["cross"] = {
        "cross_mean_norm": float(np.mean(cross_norms)) if cross_norms else 0.0,
        "cross_var": float(np.var(cross_norms)) if cross_norms else 0.0,
        "h_l_cv_ratio": h_cv / (l_cv + 1e-20),
    }
    results["step"] = step_label
    print("  [KF @ %s]  H_CV=%.6e  L_CV=%.6e  ratio=%.4f  H_AF=%.4f  L_AF=%.4f" % (
        step_label, h_cv, l_cv, h_cv / (l_cv + 1e-20),
        results["H"]["af"], results["L"]["af"]), flush=True)
    for mod in ["H", "L"]:
        layer_cvs = ["L%d:%.4e" % (k, v["cv"]) for k, v in sorted(results[mod]["per_layer"].items())]
        print("    %s per-layer CV: %s" % (mod, ", ".join(layer_cvs)), flush=True)
    return results


# --- DIFFERENTIABLE H-MODULE CV (for regularization) ---

def compute_h_module_cv_differentiable(raw_model, device):
    h_module = raw_model.inner.H_level
    layer_cvs = []
    for layer in h_module.layers:
        W = layer.self_attn.qkv_proj.weight
        num_heads = layer.self_attn.num_heads
        head_dim = layer.self_attn.head_dim
        W_Q = W[:num_heads * head_dim, :]
        W_K = W[num_heads * head_dim: 2 * num_heads * head_dim, :]
        head_matrices = []
        for h in range(num_heads):
            q_h = W_Q[h * head_dim:(h + 1) * head_dim, :]
            k_h = W_K[h * head_dim:(h + 1) * head_dim, :]
            W_h = q_h.T @ k_h
            head_matrices.append(W_h)
        norms = []
        for i in range(len(head_matrices)):
            for j in range(i + 1, len(head_matrices)):
                comm = head_matrices[i] @ head_matrices[j] - head_matrices[j] @ head_matrices[i]
                norm = torch.sqrt(torch.sum(comm ** 2) + 1e-12)
                norms.append(norm)
        if norms:
            norms_tensor = torch.stack(norms)
            layer_cv = torch.var(norms_tensor)
            layer_cvs.append(layer_cv)
    if not layer_cvs:
        return torch.tensor(0.0, device=device, requires_grad=True)
    return torch.stack(layer_cvs).mean()


def compute_h_module_cv_per_layer(raw_model, device):
    """Return list of (layer_idx, layer_cv_tensor, qkv_param_ref) for gated KF."""
    h_module = raw_model.inner.H_level
    layer_data = []
    for layer_idx, layer in enumerate(h_module.layers):
        W = layer.self_attn.qkv_proj.weight
        num_heads = layer.self_attn.num_heads
        head_dim = layer.self_attn.head_dim
        W_Q = W[:num_heads * head_dim, :]
        W_K = W[num_heads * head_dim: 2 * num_heads * head_dim, :]
        head_matrices = []
        for h in range(num_heads):
            q_h = W_Q[h * head_dim:(h + 1) * head_dim, :]
            k_h = W_K[h * head_dim:(h + 1) * head_dim, :]
            W_h = q_h.T @ k_h
            head_matrices.append(W_h)
        norms = []
        for i in range(len(head_matrices)):
            for j in range(i + 1, len(head_matrices)):
                comm = head_matrices[i] @ head_matrices[j] - head_matrices[j] @ head_matrices[i]
                norm = torch.sqrt(torch.sum(comm ** 2) + 1e-12)
                norms.append(norm)
        if norms:
            norms_tensor = torch.stack(norms)
            layer_cv = torch.var(norms_tensor)
            layer_data.append((layer_idx, layer_cv, layer.self_attn.qkv_proj.weight))
    return layer_data


# --- MAIN TRAINING LOOP ---

def main():
    parser = argparse.ArgumentParser(description="300M HRM training -- Phase 4A-bis scale validation")
    parser.add_argument("--kf_lambda", type=float, default=1.0)
    parser.add_argument("--kf_objective", type=str, default="linear",
                        choices=["linear", "log", "adaptive", "gated"],
                        help="KF objective: linear=-lam*H_CV, log=-lam*log(H_CV), adaptive=-CE/H_CV*H_CV, gated=per-layer gradient alignment")
    parser.add_argument("--lambda_schedule", type=str, default="constant",
                        choices=["constant", "cosine", "linear"])
    parser.add_argument("--lambda_min", type=float, default=0.01)
    parser.add_argument("--kf_every", type=int, default=50)
    parser.add_argument("--epochs", type=int, default=3000)
    parser.add_argument("--save_dir", type=str, default="/home/clawd/HRM/checkpoints/300m_kf_decoupled")
    parser.add_argument("--data_path", type=str, default="/home/clawd/HRM/data/sudoku-extreme-10k")
    parser.add_argument("--batch_size", type=int, default=64)
    parser.add_argument("--lr", type=float, default=3e-5)
    parser.add_argument("--checkpoint_every", type=int, default=500)
    parser.add_argument("--resume", type=str, default=None)
    args = parser.parse_args()

    device = "cuda"
    os.makedirs(args.save_dir, exist_ok=True)

    mode = "KF-DECOUPLED" if args.kf_lambda > 0 else "BASELINE"
    schedule_str = ""
    if args.lambda_schedule != "constant":
        schedule_str = " (%s %.4f->%.4f)" % (args.lambda_schedule, args.kf_lambda, args.lambda_min)
    print("=" * 70)
    print("300M HRM -- %s TRAINING (Phase 4A-bis)" % mode)
    print("  Architecture: hrm_v2 (308.3M params)")
    print("  Data: sudoku-extreme (hard)")
    kf_note = " (H-module ONLY)" if args.kf_lambda > 0 else " (no regularization)"
    print("  KF lambda: %s%s%s" % (args.kf_lambda, schedule_str, kf_note))
    if args.kf_lambda > 0:
        print("  KF objective: %s" % args.kf_objective)
    if args.lambda_schedule != "constant":
        print("  Lambda schedule: %s decay -> %s" % (args.lambda_schedule, args.lambda_min))
    print("  KF every: %d steps" % args.kf_every)
    print("  Epochs: %d" % args.epochs)
    print("  Batch size: %d" % args.batch_size)
    print("  LR: %s" % args.lr)
    print("  Save dir: %s" % args.save_dir)
    print("=" * 70)

    # --- BUILD MODEL ---
    arch_cfg = OmegaConf.load("/home/clawd/HRM/config/arch/hrm_v2.yaml")
    temp_loader, train_meta = create_dataloader(
        args.data_path, "train", batch_size=args.batch_size, epochs_per_iter=1)
    steps_per_epoch = 0
    for _ in temp_loader:
        steps_per_epoch += 1
    total_steps_est = steps_per_epoch * args.epochs
    print("  Steps/epoch: %d  Total steps (est): %d" % (steps_per_epoch, total_steps_est))
    del temp_loader

    model, raw_model = build_model(
        arch_cfg, train_meta.num_puzzle_identifiers, device,
        vocab_size=train_meta.vocab_size, seq_len=train_meta.seq_len,
        batch_size=args.batch_size)

    h_params = sum(p.numel() for p in raw_model.inner.H_level.parameters())
    l_params = sum(p.numel() for p in raw_model.inner.L_level.parameters())
    total_params = sum(p.numel() for p in raw_model.parameters())
    print("  H-module params: %s (%.1f%%)" % ("{:,}".format(h_params), 100 * h_params / total_params))
    print("  L-module params: %s (%.1f%%)" % ("{:,}".format(l_params), 100 * l_params / total_params))
    print("  Total params: %s" % "{:,}".format(total_params))
    vram = sum(p.numel() * p.element_size() for p in model.parameters()) / 1e9
    print("  VRAM estimate: ~%.2f GB model" % vram)

    optimizer = AdamATan2(
        [p for p in model.parameters() if p.requires_grad],
        lr=args.lr, betas=(0.9, 0.95), weight_decay=1.0)

    start_epoch = 0
    global_step = 0
    kf_reg_applications = 0
    kf_trajectory = []

    if args.resume:
        print("\nResuming from %s" % args.resume)
        ckpt = torch.load(args.resume, map_location=device, weights_only=False)
        raw_model.load_state_dict(ckpt["model_state_dict"])
        optimizer.load_state_dict(ckpt["optimizer_state_dict"])
        start_epoch = ckpt["epoch"]
        global_step = ckpt.get("global_step", 0)
        kf_reg_applications = ckpt.get("kf_reg_applications", 0)
        traj_path = os.path.join(args.save_dir, "kf_trajectory_300m.json")
        if os.path.exists(traj_path):
            with open(traj_path) as f:
                kf_trajectory = json.load(f)
        print("  Resumed at epoch %d, step %d" % (start_epoch, global_step))

    if not kf_trajectory:
        print("\n--- BASELINE KF (random init) ---")
        kf_init = measure_kf(raw_model, "init")
        kf_trajectory = [kf_init]

    start_chunk = start_epoch // args.checkpoint_every
    num_chunks = args.epochs // args.checkpoint_every

    for chunk_idx in range(start_chunk, num_chunks):
        epoch_start = chunk_idx * args.checkpoint_every
        epoch_end = epoch_start + args.checkpoint_every
        print("\n" + "=" * 50)
        print("CHUNK %d/%d: epochs %d-%d" % (chunk_idx + 1, num_chunks, epoch_start, epoch_end))
        print("=" * 50)

        chunk_loader, _ = create_dataloader(
            args.data_path, "train", batch_size=args.batch_size,
            epochs_per_iter=args.checkpoint_every)

        model.train()
        carry = None
        chunk_loss = 0.0
        chunk_steps = 0
        t_start = time.time()

        for set_name, batch, batch_size in chunk_loader:
            batch_gpu = {k: v.cuda() for k, v in batch.items()}

            optimizer.zero_grad()
            if carry is None:
                with torch.device(device):
                    carry = model.initial_carry(batch_gpu)
            carry, loss, metrics, _, _ = model(carry=carry, batch=batch_gpu, return_keys=[])
            ((1.0 / batch_size) * loss).backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

            chunk_loss += loss.item()
            chunk_steps += 1
            global_step += 1

            if args.kf_lambda > 0 and global_step % args.kf_every == 0:
                progress = min(global_step / max(total_steps_est, 1), 1.0)
                current_lambda = compute_lambda(
                    args.kf_lambda, args.lambda_min, args.lambda_schedule, progress)

                if args.kf_objective == "gated":
                    # --- GRADIENT-GATED KF (per-layer alignment) ---
                    # Store CE gradients for H-module qkv_proj layers
                    ce_grads = {}
                    for layer_idx, layer in enumerate(raw_model.inner.H_level.layers):
                        p = layer.self_attn.qkv_proj.weight
                        if p.grad is not None:
                            ce_grads[layer_idx] = p.grad.detach().clone()

                    # Compute per-layer KF
                    layer_data = compute_h_module_cv_per_layer(raw_model, device)
                    h_cv_val = torch.stack([ld[1] for ld in layer_data]).mean()

                    # Apply gated KF per layer
                    optimizer.zero_grad()
                    gated_layers = []
                    applied_layers = []
                    for layer_idx, layer_cv, param_ref in layer_data:
                        layer_loss = -current_lambda * layer_cv
                        layer_loss.backward(retain_graph=True)

                        if layer_idx in ce_grads and param_ref.grad is not None:
                            kf_grad = param_ref.grad.detach().flatten()
                            ce_grad = ce_grads[layer_idx].flatten()
                            cos_sim = torch.dot(kf_grad, ce_grad) / (
                                torch.norm(kf_grad) * torch.norm(ce_grad) + 1e-20)
                            if cos_sim.item() <= 0:
                                # Opposing — gate this layer out
                                param_ref.grad.zero_()
                                gated_layers.append(layer_idx)
                            else:
                                applied_layers.append((layer_idx, cos_sim.item()))

                    # Zero L-module grads
                    for p in raw_model.inner.L_level.parameters():
                        if p.grad is not None:
                            p.grad.zero_()

                    optimizer.step()
                    kf_reg_applications += 1

                    if kf_reg_applications % 10 == 0:
                        n_gated = len(gated_layers)
                        n_total = len(layer_data)
                        n_applied = len(applied_layers)
                        avg_cos = sum(c for _, c in applied_layers) / max(n_applied, 1)
                        print("  [Step %d] KF-gated #%d: H_CV=%.6e  applied=%d/%d  gated=%s  avg_cos=%.4f" % (
                            global_step, kf_reg_applications, h_cv_val.item(),
                            n_applied, n_total,
                            str(gated_layers) if gated_layers else "none",
                            avg_cos), flush=True)

                else:
                    # --- STANDARD KF OBJECTIVES (linear/log/adaptive) ---
                    h_cv = compute_h_module_cv_differentiable(raw_model, device)

                    if args.kf_objective == "log":
                        kf_loss = -current_lambda * torch.log(h_cv + 1e-20)
                    elif args.kf_objective == "adaptive":
                        adaptive_lambda = chunk_loss / max(chunk_steps, 1) / (h_cv.detach() + 1e-20)
                        kf_loss = -adaptive_lambda * h_cv
                    else:
                        kf_loss = -current_lambda * h_cv

                    optimizer.zero_grad()
                    kf_loss.backward()

                    for p in raw_model.inner.L_level.parameters():
                        if p.grad is not None:
                            p.grad.zero_()

                    optimizer.step()
                    kf_reg_applications += 1

                    if kf_reg_applications % 10 == 0:
                        lambda_info = ""
                        if args.lambda_schedule != "constant":
                            lambda_info = "  lambda=%.4f" % current_lambda
                        print("  [Step %d] KF reg #%d: H_CV=%.6e  kf_loss=%.6e%s" % (
                            global_step, kf_reg_applications, h_cv.item(), kf_loss.item(), lambda_info),
                            flush=True)

            if chunk_steps % 100 == 0:
                avg = chunk_loss / chunk_steps
                elapsed = time.time() - t_start
                steps_per_sec = chunk_steps / max(elapsed, 1)
                print("  step %d  ce_loss=%.4f  steps/s=%.1f  elapsed=%.0fs  kf_regs=%d" % (
                    chunk_steps, avg, steps_per_sec, elapsed, kf_reg_applications), flush=True)

        avg_loss = chunk_loss / max(chunk_steps, 1)
        elapsed = time.time() - t_start
        print("Chunk %d done: ce_loss=%.4f  steps=%d  time=%.0fs (%.1fmin)" % (
            chunk_idx + 1, avg_loss, chunk_steps, elapsed, elapsed / 60), flush=True)

        print("\n--- KF MEASUREMENT @ epoch %d ---" % epoch_end)
        model.eval()
        kf_result = measure_kf(raw_model, "epoch_%d" % epoch_end)
        kf_result["loss"] = avg_loss
        kf_result["global_step"] = global_step
        kf_result["kf_reg_applications"] = kf_reg_applications

        if args.lambda_schedule != "constant":
            progress = min(global_step / max(total_steps_est, 1), 1.0)
            kf_result["lambda_at_checkpoint"] = compute_lambda(
                args.kf_lambda, args.lambda_min, args.lambda_schedule, progress)

        eval_metrics_sum = {}
        carry_eval = None
        eval_loader, _ = create_dataloader(args.data_path, "test",
                                           batch_size=args.batch_size, epochs_per_iter=1)
        with torch.no_grad():
            for sn, batch, bs in eval_loader:
                batch_gpu = {k: v.cuda() for k, v in batch.items()}
                if carry_eval is None:
                    with torch.device(device):
                        carry_eval = model.initial_carry(batch_gpu)
                carry_eval, _, metrics, _, _ = model(carry=carry_eval, batch=batch_gpu, return_keys=[])
                for k, v in metrics.items():
                    if isinstance(v, torch.Tensor):
                        eval_metrics_sum[k] = eval_metrics_sum.get(k, 0) + v.item()
        count = eval_metrics_sum.get("count", 1)
        exact_acc = eval_metrics_sum.get("exact_accuracy", 0) / max(count, 1)
        token_acc = eval_metrics_sum.get("accuracy", 0) / max(count, 1)
        kf_result["exact_accuracy"] = exact_acc
        kf_result["token_accuracy"] = token_acc
        print("  Exact acc: %.4f  Token acc: %.4f" % (exact_acc, token_acc), flush=True)

        kf_trajectory.append(kf_result)

        ckpt_path = os.path.join(args.save_dir, "epoch_%d.pt" % epoch_end)
        torch.save({
            "model_state_dict": raw_model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "epoch": epoch_end,
            "global_step": global_step,
            "loss": avg_loss,
            "kf_lambda": args.kf_lambda,
            "lambda_schedule": args.lambda_schedule,
            "lambda_min": args.lambda_min,
            "kf_reg_applications": kf_reg_applications,
        }, ckpt_path)
        print("  Saved checkpoint: %s" % ckpt_path, flush=True)

        traj_path = os.path.join(args.save_dir, "kf_trajectory_300m.json")
        with open(traj_path, "w") as f:
            json.dump(kf_trajectory, f, indent=2, default=float)
        print("  Trajectory saved: %s" % traj_path, flush=True)

    print("\n" + "=" * 70)
    print("300M HRM %s TRAINING COMPLETE" % mode)
    print("=" * 70)
    if args.kf_lambda > 0:
        print("Total KF reg applications: %d" % kf_reg_applications)
        if args.lambda_schedule != "constant":
            print("Lambda schedule: %s %.4f -> %.4f" % (args.lambda_schedule, args.kf_lambda, args.lambda_min))
    print("\nFULL KF TRAJECTORY:")
    print("%15s  %12s  %12s  %8s  %10s  %8s" % ("Step", "H_CV", "L_CV", "Ratio", "ExactAcc", "Loss"))
    print("-" * 75)
    for kf in kf_trajectory:
        step = kf["step"]
        h_cv = kf["H"]["cv"]
        l_cv = kf["L"]["cv"]
        ratio = h_cv / (l_cv + 1e-20)
        acc_str = "%.4f" % kf.get("exact_accuracy", 0) if "exact_accuracy" in kf else "N/A"
        loss_str = "%.4f" % kf.get("loss", 0) if "loss" in kf else "N/A"
        print("%15s  %12.6e  %12.6e  %8.4f  %10s  %8s" % (step, h_cv, l_cv, ratio, acc_str, loss_str))

    win_path = "/mnt/c/Users/mercu/clawd/projects/Corpus Perspectival/kf_trajectory_300m_scheduled.json"
    try:
        import shutil
        shutil.copy(traj_path, win_path)
        print("\nCopied to: %s" % win_path)
    except Exception as e:
        print("Could not copy to Windows: %s" % e)

    print("\n" + "=" * 70)
    print("SCALE VALIDATION SUMMARY:")
    if len(kf_trajectory) >= 2:
        init_h = kf_trajectory[0]["H"]["cv"]
        final_h = kf_trajectory[-1]["H"]["cv"]
        final_acc = kf_trajectory[-1].get("exact_accuracy", 0)
        final_tok = kf_trajectory[-1].get("token_accuracy", 0)
        print("  Init H_CV: %.6e  ->  Final H_CV: %.6e  (%.1fx)" % (init_h, final_h, final_h / max(init_h, 1e-20)))
        print("  Final exact accuracy: %.4f" % final_acc)
        print("  Final token accuracy: %.4f" % final_tok)
        if args.kf_lambda > 0:
            if final_h > init_h:
                print("  H-module CV INCREASED -- KF regularization working at 300M scale")
            else:
                print("  H-module CV did NOT increase -- investigate lambda/schedule")
    print("=" * 70)


if __name__ == "__main__":
    main()
