"""
Smoke compare: train BOTH architectures 200 steps + eval BOTH, side-by-side.

One-shot script for prerequisite-clearing. Removes the "train then eval" two-step
that tomorrow's plan listed as Step 1, so tomorrow can start with the supervisor work.

Run from respira/:  python3 smoke_compare.py
"""
from __future__ import annotations

import sys
import time
import torch
import torch.nn.functional as F
from torch.optim import AdamW

from data import make_loader, cycle_loader, IGNORE_LABEL_ID
from respira import RespiraCell
from baselines.matched_transformer import MatchedTransformer, phase1_matched_config
from eval import evaluate, format_eval_report
from train import supervisor_calibration_loss


def build(name: str):
    if name == "respira":
        return RespiraCell(
            planner_channels=32, executor_channels=64, seq_len=81, vocab_size=11,
            max_cycles=4, planner_omega=(0.05, 0.2), executor_omega=(0.5, 2.0),
            dt=0.1, mu_scale=1.0, halt_threshold=0.7,
        )
    if name == "transformer":
        return MatchedTransformer(**phase1_matched_config())
    raise ValueError(name)


def train_then_eval(name: str, steps: int = 200, batch_size: int = 64,
                    lr: float = 3e-4, seed: int = 0, eval_batches: int = 20,
                    supervisor: bool = False, lambda_cal: float = 1.0) -> dict:
    """Train + eval. `supervisor` enables C2 BCE-against-correctness calibration loss
    on Respira's Mirror confidence head (A130 fix). Has no effect on transformer."""
    torch.manual_seed(seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = build(name).to(device)
    opt = AdamW(model.parameters(), lr=lr, weight_decay=0.01, betas=(0.9, 0.95))

    train_loader = make_loader(split="train", batch_size=batch_size, shuffle=True)
    it = cycle_loader(train_loader)

    sup_str = " + C2 supervisor" if (supervisor and name == "respira") else ""
    print(f"\n=== TRAIN {name}{sup_str} ({sum(p.numel() for p in model.parameters()):,} params) ===")
    model.train()
    t0 = time.time()
    losses = []
    for step in range(1, steps + 1):
        x, y = next(it)
        x, y = x.to(device, non_blocking=True), y.to(device, non_blocking=True)
        aux = None
        if name == "respira":
            logits, _, aux = model(x)
        else:
            logits = model(x)
        task_loss = F.cross_entropy(logits.reshape(-1, logits.shape[-1]),
                               y.reshape(-1), ignore_index=IGNORE_LABEL_ID)
        if supervisor and name == "respira" and aux is not None:
            cal_loss = supervisor_calibration_loss(aux, logits, y)
            loss = task_loss + lambda_cal * cal_loss
        else:
            loss = task_loss
        opt.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        losses.append(task_loss.item())  # log task_loss for fair comparison across arms
        if step == 1 or step % 50 == 0 or step == steps:
            print(f"  step {step:4d}  task_loss={task_loss.item():.4f}  elapsed={time.time()-t0:.0f}s")

    print(f"\n=== EVAL {name}{sup_str} ===")
    test_loader = make_loader(split="test", batch_size=batch_size, shuffle=False)
    result = evaluate(model, name, test_loader, device=device, max_batches=eval_batches,
                      record_trajectory=(name == "respira"))
    print(format_eval_report(result))

    return {
        "name": name + (" +super" if supervisor and name == "respira" else ""),
        "train_steps": steps,
        "first_loss": losses[0],
        "last_loss": losses[-1],
        "loss_delta": losses[0] - losses[-1],
        "token_accuracy": result["token_accuracy"],
        "exact_accuracy": result["exact_accuracy"],
        "mean_loss_per_token": result["mean_loss_per_token"],
        "inside_analysis": result.get("inside_analysis"),
    }


def main():
    print("=" * 64)
    print("  SMOKE COMPARE — train + eval both architectures")
    print("  predictions (logged in daily log before running):")
    print("    transformer:  token_acc 0.40–0.60  exact_acc 0.00–0.05  (confidence: medium)")
    print("    respira:      token_acc ~0.10      exact_acc 0.00       (confidence: high)")
    print("=" * 64)

    tr = train_then_eval("transformer", steps=200, seed=0)
    rs = train_then_eval("respira", steps=200, seed=0, supervisor=False)
    rs_sup = train_then_eval("respira", steps=200, seed=0, supervisor=True)

    print("\n" + "=" * 80)
    print("  THREE-WAY COMPARISON")
    print("=" * 80)
    print(f"  {'metric':<20} {'transformer':>13} {'respira':>13} {'respira+super':>15}")
    print(f"  {'-' * 20} {'-' * 13} {'-' * 13} {'-' * 15}")
    for k in ("first_loss", "last_loss", "loss_delta", "token_accuracy",
              "exact_accuracy", "mean_loss_per_token"):
        print(f"  {k:<20} {tr[k]:>13.4f} {rs[k]:>13.4f} {rs_sup[k]:>15.4f}")
    print("=" * 80)
    # Inside-analysis comparison (Respira variants)
    print(f"\n  inside-analysis (Respira variants):")
    for label, r in [("no-super", rs), ("+super", rs_sup)]:
        ia = r.get("inside_analysis")
        if ia:
            print(f"    {label:>10}: mean_halt_cycle={ia['mean_halt_cycle']:.2f}  "
                  f"conf@halt={ia['mean_confidence_at_halt']:.4f}  "
                  f"frac_halted_by_2={ia['frac_halted_by_cycle_2']:.3f}")


if __name__ == "__main__":
    main()
