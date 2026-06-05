"""
Respira / eval.py — Capability evaluation + inside-analysis hooks.

Halt-aware (Respira's ACT loop runs naturally; we read its trajectory).
Architecture-agnostic interface — works for both RespiraCell and MatchedTransformer.

Metrics:
  • token_accuracy   : per-cell correctness over non-ignored positions
                        (positions where label != IGNORE_LABEL_ID)
  • exact_accuracy   : per-puzzle correctness — all non-ignored positions match
  • mean_loss_per_token : avg CE loss per non-ignored token

For Respira, optional `record_trajectory=True` captures the per-cycle structural
snapshots from RespiraCell.forward() across all eval batches — the inside-analysis
data: confidence, halt cycle, μ amplitudes, |z| amplitudes, coupling multipliers.

CLAWD-LOCAL / PRIVATE.
"""
from __future__ import annotations

import torch
import torch.nn.functional as F

from data import IGNORE_LABEL_ID


def _spearman_corr(xs: list[float], ys: list[float]) -> float | None:
    """Pure-Python Spearman rank correlation. Returns None if undefined."""
    n = len(xs)
    if n < 2 or n != len(ys):
        return None
    def _ranks(values: list[float]) -> list[float]:
        idx_sorted = sorted(range(n), key=lambda i: values[i])
        ranks = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j + 1 < n and values[idx_sorted[j + 1]] == values[idx_sorted[i]]:
                j += 1
            avg_rank = (i + j) / 2 + 1
            for k in range(i, j + 1):
                ranks[idx_sorted[k]] = avg_rank
            i = j + 1
        return ranks
    rx, ry = _ranks(xs), _ranks(ys)
    mean_x = sum(rx) / n
    mean_y = sum(ry) / n
    num = sum((rx[i] - mean_x) * (ry[i] - mean_y) for i in range(n))
    den_x = sum((rx[i] - mean_x) ** 2 for i in range(n))
    den_y = sum((ry[i] - mean_y) ** 2 for i in range(n))
    if den_x == 0 or den_y == 0:
        return None
    return num / (den_x ** 0.5 * den_y ** 0.5)


@torch.no_grad()
def evaluate(
    model: torch.nn.Module,
    model_name: str,
    loader,
    device: str | torch.device = "cuda",
    max_batches: int | None = None,
    record_trajectory: bool = False,
    arch_variant: str = "default",
) -> dict:
    """Evaluate model on a data loader.

    Args:
      model:             a RespiraCell or MatchedTransformer.
      model_name:        'respira' or 'transformer' (determines forward signature).
      loader:            DataLoader yielding (input_tokens, target_tokens) tuples.
      device:            cuda / cpu.
      max_batches:       cap on number of batches (None = full pass).
      record_trajectory: only meaningful for Respira; capture per-cycle snapshots.

    Returns dict with metrics and (optionally) inside-analysis trajectory.
    """
    model.eval()

    total_correct_tokens = 0
    total_tokens = 0
    total_correct_puzzles = 0
    total_puzzles = 0
    total_loss_sum = 0.0
    n_batches = 0

    # Inside-analysis aggregation
    trajectory_per_batch: list = [] if record_trajectory else []
    halt_cycles_all: list[int] = []
    confidence_at_halt: list[float] = []
    # Per-batch-element correctness (mean per-token accuracy) — needed for the
    # Phase-3 §5a W-Vh-calib metric (Spearman of confidence vs correctness).
    correctness_per_element: list[float] = []

    for batch_idx, (x, y) in enumerate(loader):
        if max_batches is not None and batch_idx >= max_batches:
            break
        x = x.to(device, non_blocking=True)
        y = y.to(device, non_blocking=True)

        if model_name == "respira":
            logits, traj, _ = model(x, record_trajectory=record_trajectory, arch_variant=arch_variant)
            if record_trajectory and traj is not None:
                trajectory_per_batch.append({
                    "batch": batch_idx,
                    "n_cycles": len(traj),
                    "cycles": traj,
                })
                # Aggregate halt info — the cycle at which each batch element halted.
                # Find first cycle where halted_so_far was True per batch element.
                if traj:
                    halted_per_cycle = torch.stack([t["halted_so_far"] for t in traj])  # [cycles, B]
                    B = halted_per_cycle.shape[1]
                    for b in range(B):
                        flips = (halted_per_cycle[:, b].int().diff() == 1).nonzero(as_tuple=True)[0]
                        # If never halted, record max_cycles; else the first cycle it flipped on.
                        if len(flips) > 0:
                            halt_c = int(flips[0].item()) + 1
                        elif halted_per_cycle[0, b].item():
                            halt_c = 1
                        else:
                            halt_c = len(traj)
                        halt_cycles_all.append(halt_c)
                        # Confidence at (or right before) halt.
                        conf_idx = min(halt_c - 1, len(traj) - 1)
                        confidence_at_halt.append(float(traj[conf_idx]["confidence"][b].item()))
        else:
            logits = model(x)

        # Loss (sum reduction; we'll normalize by total tokens)
        loss = F.cross_entropy(
            logits.reshape(-1, logits.shape[-1]),
            y.reshape(-1),
            ignore_index=IGNORE_LABEL_ID,
            reduction="sum",
        )
        total_loss_sum += float(loss.item())

        # Token-level accuracy
        preds = logits.argmax(dim=-1)  # [B, S]
        mask = (y != IGNORE_LABEL_ID)
        correct = (preds == y) & mask

        # Per-puzzle: all non-ignored positions match
        per_puzzle_mask_count = mask.sum(dim=-1)         # [B]
        per_puzzle_correct = correct.sum(dim=-1)         # [B]
        valid = per_puzzle_mask_count > 0                # [B]
        puzzle_exact = (per_puzzle_correct == per_puzzle_mask_count) & valid  # [B]

        total_correct_tokens += int(correct.sum().item())
        total_tokens += int(mask.sum().item())
        total_correct_puzzles += int(puzzle_exact.sum().item())
        total_puzzles += int(valid.sum().item())
        n_batches += 1

        # Per-batch-element correctness for W-Vh-calib (Phase-3 §5a).
        if record_trajectory and model_name == "respira":
            n_valid = per_puzzle_mask_count.clamp(min=1).float()  # [B]
            per_elem_correct = per_puzzle_correct.float() / n_valid  # [B] in [0, 1]
            for b in range(per_elem_correct.shape[0]):
                if int(per_puzzle_mask_count[b].item()) > 0:
                    correctness_per_element.append(float(per_elem_correct[b].item()))

    result = {
        "model_name": model_name,
        "n_batches": n_batches,
        "n_puzzles": total_puzzles,
        "n_tokens": total_tokens,
        "token_accuracy": total_correct_tokens / max(total_tokens, 1),
        "exact_accuracy": total_correct_puzzles / max(total_puzzles, 1),
        "mean_loss_per_token": total_loss_sum / max(total_tokens, 1),
    }

    if record_trajectory and model_name == "respira" and halt_cycles_all:
        # Inside-analysis summary
        # W-Vh-calib (Phase-3 §5a): Spearman correlation of per-element confidence
        # vs per-element correctness. Computed in pure-Python via rank-based formula
        # to avoid scipy dependency. NaN when std=0 (constant rank).
        calib_spearman = None
        if len(correctness_per_element) == len(confidence_at_halt) and len(confidence_at_halt) >= 8:
            calib_spearman = _spearman_corr(confidence_at_halt, correctness_per_element)
        result["inside_analysis"] = {
            "mean_halt_cycle": sum(halt_cycles_all) / len(halt_cycles_all),
            "max_halt_cycle": max(halt_cycles_all),
            "min_halt_cycle": min(halt_cycles_all),
            "frac_halted_by_cycle_2": sum(1 for c in halt_cycles_all if c <= 2) / len(halt_cycles_all),
            "mean_confidence_at_halt": sum(confidence_at_halt) / len(confidence_at_halt),
            "n_examples_tracked": len(halt_cycles_all),
            "calib_spearman_conf_vs_correctness": calib_spearman,
            "trajectory_per_batch": trajectory_per_batch,  # full per-cycle snapshots
        }

    return result


def format_eval_report(result: dict) -> str:
    """Human-readable eval summary."""
    lines = [
        f"  eval report — {result['model_name']}",
        f"    batches:                {result['n_batches']}",
        f"    puzzles evaluated:      {result['n_puzzles']:,}",
        f"    tokens evaluated:       {result['n_tokens']:,}",
        f"    EXACT ACCURACY:         {result['exact_accuracy']:.4f}",
        f"    token accuracy:         {result['token_accuracy']:.4f}",
        f"    mean loss / token:      {result['mean_loss_per_token']:.4f}",
    ]
    ia = result.get("inside_analysis")
    if ia is not None:
        lines += [
            "    --- inside-analysis (Respira) ---",
            f"    mean halt cycle:        {ia['mean_halt_cycle']:.2f}",
            f"    halt cycle range:       [{ia['min_halt_cycle']}, {ia['max_halt_cycle']}]",
            f"    fraction halted ≤ c=2:  {ia['frac_halted_by_cycle_2']:.3f}",
            f"    mean confidence@halt:   {ia['mean_confidence_at_halt']:.4f}",
            f"    examples tracked:       {ia['n_examples_tracked']:,}",
        ]
    return "\n".join(lines)
