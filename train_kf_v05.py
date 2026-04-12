"""
KF-Decoupled Training on HRM v0.5 — Separate Objectives on Separate Parameters

The v0.4 experiment (Finding #67) showed that stacking KF regularization and
architectural constraint on the SAME parameters causes destructive interference
(38.9% — worse than either alone). The fix: give each objective its own parameters.

v0.5 tests this directly on the Hierarchical Reasoning Model:
  - CE loss: flows through BOTH H-module and L-module (standard task training)
  - KF regularization: targets ONLY H-module parameters (algebraic preservation)
  - L-module: free to crystallize/sediment without KF interference

This is the dual-module design that v0.4's failure predicted should work.

Prediction (P67): KF-decoupled training will:
  1. Increase H-module CV relative to standard training baseline
  2. Allow L-module CV to decrease (sedimentation) unconstrained
  3. Maintain or improve exact solve rate on sudoku-extreme

Setup:
  - HRM v1 (27.3M params): 4 H-layers + 4 L-layers, 8 heads, 512 hidden
  - Data: sudoku-extreme-1k-aug-1000
  - 2000 epochs, checkpoint every 500
  - KF reg: lambda=1.0 (HRM scale), every 50 steps, H-module only
  - Baseline: standard HRM training (kf_trajectory.json, 5 checkpoints)

Usage:
  python train_kf_v05.py [--kf_lambda 1.0] [--kf_every 50] [--epochs 2000]
"""
import sys
import os
import json
import time
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


# ─── MODEL BUILDING (from complete_training.py) ───

def build_model(arch_cfg, num_puzzle_ids, device, vocab_size=11, seq_len=81, batch_size=384):
    arch_resolved = OmegaConf.to_container(arch_cfg, resolve=True)
    hidden_size = arch_resolved.get("hidden_size", 512)
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


# ─── KF MEASUREMENT (detached, for logging) ───

def extract_attention_weights(model):
    """Extract Q@K^T weight matrices from all attention heads. Detached (for logging)."""
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


def compute_cv(heads_list):
    """Commutator variance — detached, for measurement."""
    n = len(heads_list)
    if n < 2:
        return 0.0
    norms = []
    for i in range(n):
        for j in range(i + 1, n):
            comm = heads_list[i]["W"] @ heads_list[j]["W"] - heads_list[j]["W"] @ heads_list[i]["W"]
            norms.append(torch.norm(comm, p="fro").item())
    return float(np.var(norms))


def compute_mean_norm(heads_list):
    n = len(heads_list)
    if n < 2:
        return 0.0
    norms = []
    for i in range(n):
        for j in range(i + 1, n):
            comm = heads_list[i]["W"] @ heads_list[j]["W"] - heads_list[j]["W"] @ heads_list[i]["W"]
            norms.append(torch.norm(comm, p="fro").item())
    return float(np.mean(norms))


def compute_af(heads_list, threshold=1e-6):
    n = len(heads_list)
    if n < 2:
        return 0.0
    norms = []
    for i in range(n):
        for j in range(i + 1, n):
            comm = heads_list[i]["W"] @ heads_list[j]["W"] - heads_list[j]["W"] @ heads_list[i]["W"]
            norms.append(torch.norm(comm, p="fro").item())
    norms = np.array(norms)
    max_norm = np.max(norms) if len(norms) > 0 else 1.0
    return float(np.sum(norms < threshold * max_norm) / len(norms))


def measure_kf(model, step_label):
    """Full KF measurement (detached). Returns dict with H, L, cross, per-layer."""
    heads = extract_attention_weights(model)
    results = {}
    for module_name in ["H", "L"]:
        h_list = heads[module_name]
        cv = compute_cv(h_list)
        mean = compute_mean_norm(h_list)
        af = compute_af(h_list)
        layers = sorted(set(h["layer"] for h in h_list))
        per_layer = {}
        for layer in layers:
            lh = [h for h in h_list if h["layer"] == layer]
            per_layer[int(layer)] = {"cv": compute_cv(lh), "mean_norm": compute_mean_norm(lh)}
        results[module_name] = {"cv": cv, "mean_norm": mean, "af": af, "per_layer": per_layer}
    # Cross-module coupling
    cross_norms = []
    for h_head in heads["H"]:
        for l_head in heads["L"]:
            comm = h_head["W"] @ l_head["W"] - l_head["W"] @ h_head["W"]
            cross_norms.append(torch.norm(comm, p="fro").item())
    h_cv = results["H"]["cv"]
    l_cv = results["L"]["cv"]
    results["cross"] = {
        "cross_mean_norm": float(np.mean(cross_norms)),
        "cross_var": float(np.var(cross_norms)),
        "h_l_cv_ratio": h_cv / (l_cv + 1e-20),
    }
    results["step"] = step_label
    print(f"  [KF @ {step_label}]  H_CV={h_cv:.6e}  L_CV={l_cv:.6e}  "
          f"ratio={h_cv/(l_cv+1e-20):.4f}  H_AF={results['H']['af']:.4f}  "
          f"L_AF={results['L']['af']:.4f}", flush=True)
    return results


# ─── DIFFERENTIABLE H-MODULE CV (for regularization) ───

def compute_h_module_cv_differentiable(raw_model, device):
    """
    Compute commutator variance of H-module attention heads.
    DIFFERENTIABLE — stays in autograd graph for backward through H-module params.

    We compute W_h = Q_h^T @ K_h for each head, then CV = Var(||[W_i, W_j]||_F).
    The Frobenius norm is differentiable. Variance is differentiable.
    """
    h_module = raw_model.H_level
    head_matrices = []

    for layer in h_module.layers:
        W = layer.self_attn.qkv_proj.weight  # NO detach — keep in graph
        num_heads = layer.self_attn.num_heads
        head_dim = layer.self_attn.head_dim

        W_Q = W[:num_heads * head_dim, :]
        W_K = W[num_heads * head_dim: 2 * num_heads * head_dim, :]

        for h in range(num_heads):
            q_h = W_Q[h * head_dim:(h + 1) * head_dim, :]
            k_h = W_K[h * head_dim:(h + 1) * head_dim, :]
            W_h = q_h.T @ k_h  # (hidden, hidden) attention weight matrix
            head_matrices.append(W_h)

    # Compute all pairwise commutator norms
    n = len(head_matrices)
    norms = []
    for i in range(n):
        for j in range(i + 1, n):
            comm = head_matrices[i] @ head_matrices[j] - head_matrices[j] @ head_matrices[i]
            norm = torch.sqrt(torch.sum(comm ** 2) + 1e-12)  # Smooth Frobenius norm
            norms.append(norm)

    if len(norms) == 0:
        return torch.tensor(0.0, device=device, requires_grad=True)

    norms_tensor = torch.stack(norms)
    # CV = Var(norms) = E[norms^2] - E[norms]^2
    cv = torch.var(norms_tensor)
    return cv


# ─── MAIN TRAINING LOOP ───

def main():
    parser = argparse.ArgumentParser(description="v0.5 KF-decoupled HRM training")
    parser.add_argument("--kf_lambda", type=float, default=1.0,
                        help="KF regularization strength (default: 1.0)")
    parser.add_argument("--kf_every", type=int, default=50,
                        help="Apply KF reg every N optimizer steps (default: 50)")
    parser.add_argument("--epochs", type=int, default=2000,
                        help="Total training epochs (default: 2000)")
    parser.add_argument("--save_dir", type=str, default="/home/clawd/HRM/checkpoints/kf_v05",
                        help="Checkpoint save directory")
    parser.add_argument("--data_path", type=str,
                        default="/home/clawd/HRM/data/sudoku-extreme-1k-aug-1000")
    parser.add_argument("--batch_size", type=int, default=384)
    parser.add_argument("--lr", type=float, default=7e-5)
    parser.add_argument("--checkpoint_every", type=int, default=500,
                        help="Save checkpoint every N epochs")
    args = parser.parse_args()

    device = "cuda"
    os.makedirs(args.save_dir, exist_ok=True)

    print("=" * 70)
    print("v0.5: KF-DECOUPLED HRM TRAINING")
    print(f"  KF lambda: {args.kf_lambda} (H-module ONLY)")
    print(f"  KF every: {args.kf_every} steps")
    print(f"  Epochs: {args.epochs}")
    print(f"  Save dir: {args.save_dir}")
    print("  Hypothesis: Separate objectives on separate parameters")
    print("  (v0.4 showed stacking on same params = destructive interference)")
    print("=" * 70)

    # ─── BUILD MODEL ───
    arch_cfg = OmegaConf.load("/home/clawd/HRM/config/arch/hrm_v1.yaml")
    temp_loader, train_meta = create_dataloader(
        args.data_path, "train", batch_size=args.batch_size, epochs_per_iter=1)
    del temp_loader

    model, raw_model = build_model(
        arch_cfg, train_meta.num_puzzle_identifiers, device,
        vocab_size=train_meta.vocab_size, seq_len=train_meta.seq_len,
        batch_size=args.batch_size)

    # Count H vs L parameters
    h_params = sum(p.numel() for p in raw_model.H_level.parameters())
    l_params = sum(p.numel() for p in raw_model.L_level.parameters())
    total_params = sum(p.numel() for p in raw_model.parameters())
    print(f"  H-module params: {h_params:,} ({100*h_params/total_params:.1f}%)")
    print(f"  L-module params: {l_params:,} ({100*l_params/total_params:.1f}%)")
    print(f"  Total params: {total_params:,}")

    optimizer = AdamATan2(
        [p for p in model.parameters() if p.requires_grad],
        lr=args.lr, betas=(0.9, 0.95), weight_decay=1.0)

    # ─── BASELINE KF MEASUREMENT ───
    print("\n--- BASELINE KF (random init) ---")
    kf_init = measure_kf(raw_model, "init")
    kf_trajectory = [kf_init]

    # ─── TRAINING ───
    # Train in chunks of checkpoint_every epochs
    num_chunks = args.epochs // args.checkpoint_every
    global_step = 0
    kf_reg_applications = 0

    for chunk_idx in range(num_chunks):
        epoch_start = chunk_idx * args.checkpoint_every
        epoch_end = epoch_start + args.checkpoint_every
        print(f"\n{'='*50}")
        print(f"CHUNK {chunk_idx+1}/{num_chunks}: epochs {epoch_start}-{epoch_end}")
        print(f"{'='*50}")

        chunk_loader, _ = create_dataloader(
            args.data_path, "train", batch_size=args.batch_size,
            epochs_per_iter=args.checkpoint_every)

        model.train()
        carry = None
        chunk_loss = 0.0
        chunk_kf_loss = 0.0
        chunk_steps = 0
        t_start = time.time()

        for set_name, batch, batch_size in chunk_loader:
            batch_gpu = {k: v.cuda() for k, v in batch.items()}

            # ─── STANDARD CE FORWARD/BACKWARD ───
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

            # ─── KF REGULARIZATION ON H-MODULE ONLY ───
            if global_step % args.kf_every == 0 and args.kf_lambda > 0:
                # Compute differentiable H-module CV
                h_cv = compute_h_module_cv_differentiable(raw_model, device)
                # We MAXIMIZE CV → minimize -CV
                kf_loss = -args.kf_lambda * h_cv

                # Backward through H-module params ONLY
                # (CE already updated all params via optimizer.step() above;
                #  this is an additional nudge specifically for H-module algebraic structure)
                optimizer.zero_grad()
                kf_loss.backward()

                # Zero out L-module gradients — KF reg should not touch L-module
                for p in raw_model.L_level.parameters():
                    if p.grad is not None:
                        p.grad.zero_()

                # Apply the H-module-only KF gradient
                optimizer.step()

                kf_reg_applications += 1
                chunk_kf_loss += h_cv.item()

                if kf_reg_applications % 10 == 0:
                    print(f"  [Step {global_step}] KF reg #{kf_reg_applications}: "
                          f"H_CV={h_cv.item():.6e}  kf_loss={kf_loss.item():.6e}", flush=True)

            # Progress logging
            if chunk_steps % 200 == 0:
                avg = chunk_loss / chunk_steps
                elapsed = time.time() - t_start
                kf_avg = chunk_kf_loss / max(kf_reg_applications - (chunk_idx * (args.checkpoint_every // args.kf_every)), 1)
                print(f"  step {chunk_steps}  ce_loss={avg:.4f}  "
                      f"kf_regs={kf_reg_applications}  time={elapsed:.0f}s", flush=True)

        avg_loss = chunk_loss / max(chunk_steps, 1)
        elapsed = time.time() - t_start
        print(f"Chunk {chunk_idx+1} done: ce_loss={avg_loss:.4f}  steps={chunk_steps}  "
              f"kf_regs={kf_reg_applications}  time={elapsed:.0f}s", flush=True)

        # ─── CHECKPOINT + KF MEASUREMENT ───
        print(f"\n--- KF MEASUREMENT @ epoch {epoch_end} ---")
        model.eval()
        kf_result = measure_kf(raw_model, f"epoch_{epoch_end}")
        kf_result["loss"] = avg_loss
        kf_result["global_step"] = global_step
        kf_result["kf_reg_applications"] = kf_reg_applications

        # Eval accuracy
        eval_metrics_sum = {}
        carry_eval = None
        eval_loader, _ = create_dataloader(args.data_path, "test", batch_size=args.batch_size, epochs_per_iter=1)
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
        print(f"  Exact acc: {exact_acc:.4f}  Token acc: {token_acc:.4f}", flush=True)

        kf_trajectory.append(kf_result)

        # Save checkpoint
        ckpt_path = os.path.join(args.save_dir, f"epoch_{epoch_end}.pt")
        torch.save({
            "model_state_dict": raw_model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "epoch": epoch_end,
            "global_step": global_step,
            "loss": avg_loss,
            "kf_lambda": args.kf_lambda,
        }, ckpt_path)
        print(f"  Saved checkpoint: {ckpt_path}", flush=True)

    # ─── FINAL SUMMARY ───
    print(f"\n{'='*70}")
    print(f"v0.5 COMPLETE — KF-DECOUPLED HRM TRAINING")
    print(f"{'='*70}")
    print(f"Total KF reg applications: {kf_reg_applications}")
    print(f"\nFULL KF TRAJECTORY:")
    print(f"{'Step':>15s}  {'H_CV':>12s}  {'L_CV':>12s}  {'Ratio':>8s}  {'ExactAcc':>10s}  {'Loss':>8s}")
    print("-" * 75)
    for kf in kf_trajectory:
        step = kf["step"]
        h_cv = kf["H"]["cv"]
        l_cv = kf["L"]["cv"]
        ratio = h_cv / (l_cv + 1e-20)
        acc_str = f"{kf.get('exact_accuracy', 0):.4f}" if "exact_accuracy" in kf else "N/A"
        loss_str = f"{kf.get('loss', 0):.4f}" if "loss" in kf else "N/A"
        print(f"{step:>15s}  {h_cv:>12.6e}  {l_cv:>12.6e}  {ratio:>8.4f}  {acc_str:>10s}  {loss_str:>8s}")

    # Load baseline for comparison
    baseline_path = "/home/clawd/HRM/checkpoints/kf_run/kf_trajectory.json"
    if os.path.exists(baseline_path):
        with open(baseline_path) as f:
            baseline = json.load(f)
        print(f"\nBASELINE COMPARISON (standard HRM training):")
        print(f"{'Step':>15s}  {'H_CV':>12s}  {'L_CV':>12s}  {'Ratio':>8s}")
        print("-" * 55)
        for kf in baseline:
            step = kf["step"]
            h_cv = kf["H"]["cv"]
            l_cv = kf["L"]["cv"]
            ratio = h_cv / (l_cv + 1e-20)
            print(f"{step:>15s}  {h_cv:>12.6e}  {l_cv:>12.6e}  {ratio:>8.4f}")

        # Key comparison: final H_CV
        v05_final_h = kf_trajectory[-1]["H"]["cv"]
        v05_final_l = kf_trajectory[-1]["L"]["cv"]
        baseline_final_h = baseline[-1]["H"]["cv"]
        baseline_final_l = baseline[-1]["L"]["cv"]
        print(f"\nKEY COMPARISON (epoch 2000):")
        print(f"  Baseline H_CV: {baseline_final_h:.6e}  →  v0.5 H_CV: {v05_final_h:.6e}  "
              f"({100*(v05_final_h - baseline_final_h)/baseline_final_h:+.1f}%)")
        print(f"  Baseline L_CV: {baseline_final_l:.6e}  →  v0.5 L_CV: {v05_final_l:.6e}  "
              f"({100*(v05_final_l - baseline_final_l)/baseline_final_l:+.1f}%)")

    # Save trajectory
    traj_path = os.path.join(args.save_dir, "kf_trajectory_v05.json")
    with open(traj_path, "w") as f:
        json.dump(kf_trajectory, f, indent=2, default=float)
    print(f"\nTrajectory saved: {traj_path}")

    # Copy to Windows
    win_path = "/mnt/c/Users/mercu/clawd/projects/Corpus Perspectival/kf_trajectory_v05.json"
    try:
        import shutil
        shutil.copy(traj_path, win_path)
        print(f"Copied to: {win_path}")
    except Exception as e:
        print(f"Could not copy to Windows: {e}")

    print(f"\n{'='*70}")
    print(f"P67 ASSESSMENT:")
    if kf_trajectory[-1]["H"]["cv"] > baseline[-1]["H"]["cv"] if os.path.exists(baseline_path) else False:
        print(f"  H-module CV INCREASED relative to baseline — P67 criterion 1 MET")
    else:
        print(f"  H-module CV did NOT increase — P67 criterion 1 FAILED")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
