"""
Respira / train.py — Minimal SMOKE training loop.

This is NOT the full Phase-1 training procedure (no 3-phase Mirror curriculum, no
inside-analysis logging, no eval, no multi-arm orchestration). Its job is one thing:

    PROVE BOTH ARCHITECTURES CAN LEARN SUDOKU.

i.e., loss decreases over a few hundred steps, no NaN/explosion, gradients healthy,
the data pipeline works end-to-end. Once that's green, we build out the real training.

Usage:
    python3 train.py respira      [steps]   # train Respira
    python3 train.py transformer  [steps]   # train MatchedTransformer

CLAWD-LOCAL / PRIVATE.
"""
from __future__ import annotations

import sys
import time
import math
import torch
import torch.nn.functional as F
from torch.optim import AdamW

from respira import RespiraCell
from baselines.matched_transformer import MatchedTransformer, phase1_matched_config
from data import make_loader, cycle_loader, IGNORE_LABEL_ID


def build_model(name: str) -> torch.nn.Module:
    if name == "respira":
        return RespiraCell(
            planner_channels=32, executor_channels=64,
            seq_len=81, vocab_size=11, max_cycles=4,
            planner_omega=(0.05, 0.2), executor_omega=(0.5, 2.0),
            dt=0.1, mu_scale=1.0, halt_threshold=0.7,
        )
    elif name == "transformer":
        return MatchedTransformer(**phase1_matched_config())
    else:
        raise ValueError(f"unknown model: {name!r}. choose 'respira' or 'transformer'.")


def forward_unified(
    model: torch.nn.Module, x: torch.Tensor, name: str,
    mirror_authority: float = 1.0,
) -> tuple[torch.Tensor, dict | None]:
    """Unified forward: returns (logits, aux).  aux is None for transformer; dict for Respira.

    For Respira, mirror_authority < 1.0 enables the curriculum (Mirror outputs blended
    with defaults; halt disabled at low authority).
    """
    if name == "respira":
        logits, _, aux = model(x, mirror_authority=mirror_authority)
        return logits, aux
    return model(x), None


def supervisor_calibration_loss(
    aux: dict, logits: torch.Tensor, labels: torch.Tensor,
) -> torch.Tensor:
    """C2 supervisor: BCE between Mirror's confidence@halt and the per-batch correctness.

    Target: fraction of non-ignored positions where argmax(logits) matches labels, per batch.
    Loss: BCE(confidence_at_halt, target_correctness).

    Pins confidence to actual outcomes. If the Mirror is "very confident" (0.99) but the
    model is only 40% right, BCE pushes confidence down. Breaks the halt-collapse failure
    mode (A130). Gradient flows through aux['confidence_at_halt'] back into the Mirror's
    output head.
    """
    with torch.no_grad():
        preds = logits.argmax(dim=-1)  # [B, S]
        mask = (labels != IGNORE_LABEL_ID)
        correct = (preds == labels) & mask
        target = correct.sum(-1).float() / mask.sum(-1).clamp(min=1).float()  # [B] in [0,1]
        # BCE wants targets in [0,1], not exactly 0 or 1, to avoid log(0) singularity:
        target = target.clamp(min=1e-4, max=1 - 1e-4)
    return F.binary_cross_entropy(aux["confidence_at_halt"], target)


def compute_authority(step: int, n_a: int, n_b: int) -> float:
    """Mirror-authority schedule: 0 during Phase A, linear ramp through B, 1 in C."""
    if step < n_a:
        return 0.0
    if step >= n_b:
        return 1.0
    return (step - n_a) / max(n_b - n_a, 1)


def train_smoke(
    model_name: str = "respira",
    steps: int = 200,
    batch_size: int = 64,
    lr: float = 3e-4,
    log_every: int = 25,
    seed: int = 0,
    grad_clip: float = 1.0,
    curriculum: bool = True,
    n_a_frac: float = 0.25,     # Phase A: 0..25% of steps  (Mirror idle)
    n_b_frac: float = 0.75,     # Phase B: 25..75% (ramp)  ; Phase C: 75..100%
    supervisor: bool = True,     # NEW: C2 anti-collapse calibration on Mirror confidence
    lambda_cal: float = 1.0,     # Calibration-loss weight
) -> dict:
    torch.manual_seed(seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    use_curriculum = curriculum and model_name == "respira"
    n_a = int(steps * n_a_frac) if use_curriculum else 0
    n_b = int(steps * n_b_frac) if use_curriculum else 0

    print(f"  device         : {device}")
    print(f"  model          : {model_name}")
    print(f"  steps          : {steps}")
    print(f"  batch_size     : {batch_size}")
    print(f"  lr             : {lr}")
    print(f"  ignore_label   : {IGNORE_LABEL_ID}")
    if use_curriculum:
        print(f"  curriculum     : ON  (Phase A 0..{n_a}, Phase B {n_a}..{n_b}, Phase C {n_b}..)")
    else:
        print(f"  curriculum     : OFF (Mirror autonomous from step 0)")
    use_supervisor = supervisor and model_name == "respira"
    if use_supervisor:
        print(f"  supervisor     : ON  (C2 BCE-against-correctness, lambda_cal={lambda_cal})")
    else:
        print(f"  supervisor     : OFF")

    model = build_model(model_name).to(device)
    n_params = sum(p.numel() for p in model.parameters())
    print(f"  parameters     : {n_params:,}")

    opt = AdamW(model.parameters(), lr=lr, weight_decay=0.01, betas=(0.9, 0.95))
    loader = make_loader(batch_size=batch_size, shuffle=True, num_workers=0)
    it = cycle_loader(loader)

    losses, grad_norms = [], []
    t0 = time.time()
    model.train()
    for step in range(1, steps + 1):
        x, y = next(it)
        x, y = x.to(device, non_blocking=True), y.to(device, non_blocking=True)

        authority = compute_authority(step, n_a, n_b) if use_curriculum else 1.0
        logits, aux = forward_unified(model, x, model_name, mirror_authority=authority)
        task_loss = F.cross_entropy(
            logits.reshape(-1, logits.shape[-1]),
            y.reshape(-1),
            ignore_index=IGNORE_LABEL_ID,
        )

        # C2 supervisor (A130 fix): calibration loss on Mirror confidence head.
        if use_supervisor and aux is not None:
            cal_loss = supervisor_calibration_loss(aux, logits, y)
            loss = task_loss + lambda_cal * cal_loss
        else:
            cal_loss = None
            loss = task_loss

        if not torch.isfinite(loss):
            print(f"  step {step:4d}  LOSS NaN/Inf — aborting smoke run.")
            return {"losses": losses, "aborted": True}

        opt.zero_grad(set_to_none=True)
        loss.backward()
        grad_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip)
        opt.step()

        losses.append(float(loss.item()))
        grad_norms.append(float(grad_norm.item()) if torch.isfinite(grad_norm) else float("inf"))

        if step == 1 or step % log_every == 0 or step == steps:
            window = losses[-log_every:]
            avg = sum(window) / len(window)
            elapsed = time.time() - t0
            sps = step / max(elapsed, 1e-6)
            auth_str = f" α={authority:.2f}" if use_curriculum else ""
            sup_str = ""
            if use_supervisor and aux is not None:
                conf_mean = aux["confidence_at_halt"].detach().mean().item()
                halt_mean = aux["halt_cycle"].float().mean().item()
                cal_v = cal_loss.item() if cal_loss is not None else float("nan")
                sup_str = f"  cal={cal_v:.3f}  conf@halt={conf_mean:.3f}  hc={halt_mean:.2f}"
            print(f"  step {step:4d}/{steps}  task={task_loss.item():.4f}  "
                  f"avg{len(window)}={avg:.4f}  grad‖={grad_norm.item():.3f}  "
                  f"{sps:.1f} steps/s  elapsed={elapsed:.0f}s{auth_str}{sup_str}")

    # Report headline trend
    n_window = min(20, len(losses) // 4 or 1)
    first = sum(losses[:n_window]) / n_window
    last = sum(losses[-n_window:]) / n_window
    delta = first - last
    trend = "LEARNING" if delta > 0.05 else "FLAT/REGRESSING"
    print(f"\n  smoke result for {model_name}:")
    print(f"    first {n_window} avg loss: {first:.4f}")
    print(f"    last  {n_window} avg loss: {last:.4f}")
    print(f"    Δ (first - last):        {delta:+.4f}   ⇒ {trend}")
    print(f"    elapsed: {time.time() - t0:.0f}s")

    return {
        "model_name": model_name,
        "losses": losses,
        "grad_norms": grad_norms,
        "n_params": n_params,
        "first_loss_avg": first,
        "last_loss_avg": last,
        "delta": delta,
        "trend": trend,
    }


if __name__ == "__main__":
    model_name = sys.argv[1] if len(sys.argv) > 1 else "respira"
    steps = int(sys.argv[2]) if len(sys.argv) > 2 else 200
    # Third arg: "nocurr" disables curriculum (Respira-only flag); "curr" forces on.
    curriculum = True
    if len(sys.argv) > 3 and sys.argv[3].lower() in {"nocurr", "off", "false"}:
        curriculum = False
    print("=" * 60)
    print(f"  Respira SMOKE training run — {model_name}  curriculum={curriculum}")
    print("=" * 60)
    result = train_smoke(model_name=model_name, steps=steps, curriculum=curriculum)
    print("=" * 60)
