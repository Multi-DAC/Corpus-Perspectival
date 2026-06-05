"""
Respira Phase-3 Stage 2 v3h-prime sweep — 2x2 factorial over {channel-leakage-fix, supervisor-target-fix}.

Pre-registration: `palace/south/respira-phase3-stage2-v3h-prime-preregistration-2026-05-28.md`
Ratified: 2026-05-29 morning by Clayton (full ratification, lambda_sup=0.5 carried over from Stage 1
intentionally — Stage 3 question if borderline, not mid-experiment re-tuning).

Arms (3 new corners of the 2x2; Stage 1's (no-detach, BCE) corner stays as the reference, not re-run):

  Arm A — v3h_prime_full:        detach=YES, supervisor=TD
  Arm B — v3h_prime_td_only:     detach=NO,  supervisor=TD
  Arm C — v3h_prime_detach_only: detach=YES, supervisor=BCE-on-mean-correctness (Stage 1 form)

Reference (Stage 1 numbers reused, not re-run):
  no_mirror_3s:  0.897 ± [SE] (3 seeds, 2500 steps)

Per-arm primary verdicts (pre-reg §4a, LOCKED):
  W-VhP{X}-acc:   arm-X mean token-accuracy @2500 within ±1 SE of no_mirror=0.897.
  W-VhP{X}-halt:  arm-X mean halt cycle @2500 strictly less than 4.0.
  W-VhP{X}-calib: arm-X Spearman(conf_at_halt, correctness_pb) @2500 > +0.3.
  W-VhP{X}-DECISIVE: all three pass for arm X.

Factorial attribution table (§4c) has pre-registered reading for every outcome combination.

Captures: token_accuracy, exact_accuracy, mean_loss_per_token, mean_halt_cycle,
mean_confidence_at_halt, frac_halted_by_cycle_2, calib_spearman_conf_vs_correctness
at checkpoints [200, 500, 1000, 2000, 2500].

Writes results to `phase3_stage2_results_YYYY-MM-DD.json`.

Run from respira/:
  python3 sweep_phase3_stage2.py [--seeds 0,1,2] [--steps 2500] [--arms v3hp_full,v3hp_td,v3hp_detach]

CLAWD-LOCAL / PRIVATE.
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(line_buffering=True)  # live progress in detached log files

import argparse
import json
import time
from datetime import datetime, timezone

import torch
import torch.nn.functional as F
from torch.optim import AdamW

from data import make_loader, cycle_loader, IGNORE_LABEL_ID
from respira import RespiraCell
from eval import evaluate


CHECKPOINTS = [200, 500, 1000, 2000, 2500]
# Pre-reg §2: lambda_sup carried over from Stage 1 (intentional, NOT tuned).
LAMBDA_SUP = 0.5


# Arm-to-(detach, supervisor_type) mapping. Stage 1's (no-detach, BCE) is NOT here —
# already-failed and reference for the attribution table.
ARMS = {
    "v3hp_full":         {"detach": True,  "supervisor": "td"},   # Arm A
    "v3hp_td_only":      {"detach": False, "supervisor": "td"},   # Arm B
    "v3hp_detach_only":  {"detach": True,  "supervisor": "bce"},  # Arm C
}


def build_v3hp_model() -> RespiraCell:
    """All three Stage 2 arms share the same RespiraCell architecture — they differ only
    in forward-time kwargs (detach inputs, capture per-cycle logits) and supervisor choice.
    """
    return RespiraCell(
        planner_channels=32, executor_channels=64, seq_len=81, vocab_size=11,
        max_cycles=4, planner_omega=(0.05, 0.2), executor_omega=(0.5, 2.0),
        dt=0.1, mu_scale=1.0, halt_threshold=0.7,
        mirror_kind="measurer",
        measurer_halt_threshold=0.5,
    )


def compute_correctness_per_batch(
    logits: torch.Tensor, labels: torch.Tensor
) -> torch.Tensor:
    """Per-batch mean per-token argmax-equality, IGNORE_LABEL_ID-masked.
    Returns [batch] in [0, 1].
    """
    valid = (labels != IGNORE_LABEL_ID).float()  # [B, S]
    argmax = logits.argmax(dim=-1)               # [B, S]
    correct_per_token = (argmax == labels).float() * valid
    n_valid = valid.sum(dim=-1).clamp(min=1.0)
    return correct_per_token.sum(dim=-1) / n_valid  # [B]


def td_supervisor_loss(
    aux: dict, final_logits: torch.Tensor, labels: torch.Tensor,
) -> torch.Tensor:
    """TD supervisor loss (pre-reg §3b).

    Per batch element, computes:
      target_b = mean per-token agreement between
                 argmax(logits_at_halt_cycle_b) and argmax(final_logits.detach())
                 over non-IGNORE positions.
    Then BCE between conf_at_halt and target.

    Interpretation: target=1.0 means cycle-N halt produced the same answer as the final
    cycle would have — halting was correct. target=0.0 means continuing would have
    changed the answer — halting was premature. Confidence should track this.

    Decouples confidence from absolute accuracy (BCE-on-correctness) and ties it to
    marginal cycle utility — the Read-B-aligned thing to measure.
    """
    per_cycle_logits = aux["per_cycle_logits"]  # [cycles_run, B, S, V]
    halt_cycle = aux["halt_cycle"]              # [B] long, 1-indexed
    cycles_run = per_cycle_logits.shape[0]
    batch_size = per_cycle_logits.shape[1]

    # Index per-cycle-logits at each batch element's halt cycle (clamped to valid range).
    hc_idx = (halt_cycle - 1).clamp(min=0, max=cycles_run - 1)  # [B]
    batch_idx = torch.arange(batch_size, device=per_cycle_logits.device)
    # logits_at_halt[b] = per_cycle_logits[hc_idx[b], b, :, :]
    logits_at_halt = per_cycle_logits[hc_idx, batch_idx]  # [B, S, V]

    # Final-logits target: argmax-only, detached (no gradient through the target).
    argmax_final = final_logits.argmax(dim=-1).detach()  # [B, S]
    argmax_at_halt = logits_at_halt.argmax(dim=-1)       # [B, S] — NOT detached (gradient flows)

    # Per-token agreement, masked. Note: argmax is non-differentiable so this target
    # path doesn't carry gradient through argmax — but the agreement-statistic itself
    # is a non-differentiable target that we ALSO detach. The gradient flows through
    # the *confidence* head only, learning to match this target.
    valid = (labels != IGNORE_LABEL_ID).float()  # [B, S]
    agreement = (argmax_at_halt == argmax_final).float() * valid  # [B, S]
    n_valid = valid.sum(dim=-1).clamp(min=1.0)
    target_pb = (agreement.sum(dim=-1) / n_valid).detach().clamp(1e-6, 1.0 - 1e-6)  # [B]

    conf = aux["confidence_at_halt"].clamp(1e-6, 1.0 - 1e-6)  # [B], gradient-preserved
    return F.binary_cross_entropy(conf, target_pb)


def bce_supervisor_loss(
    aux: dict, logits: torch.Tensor, labels: torch.Tensor,
) -> torch.Tensor:
    """Stage 1's BCE-on-per-batch-mean-correctness supervisor (kept for arm C).
    Re-implementation matching sweep_phase2.py's v3h path exactly.
    """
    correctness_pb = compute_correctness_per_batch(logits, labels).detach()
    correctness_pb = correctness_pb.clamp(1e-6, 1.0 - 1e-6)
    conf = aux["confidence_at_halt"].clamp(1e-6, 1.0 - 1e-6)
    return F.binary_cross_entropy(conf, correctness_pb)


def run_arm(arm: str, seed: int, steps: int, batch_size: int, lr: float,
            eval_batches: int) -> dict:
    """Train one arm-seed of v3h-prime Stage 2, eval at checkpoints, return result dict."""
    if arm not in ARMS:
        raise ValueError(f"Unknown arm {arm!r}. Valid: {list(ARMS)}")
    arm_cfg = ARMS[arm]
    detach = arm_cfg["detach"]
    supervisor = arm_cfg["supervisor"]

    torch.manual_seed(seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    model = build_v3hp_model().to(device)
    opt = AdamW(model.parameters(), lr=lr, weight_decay=0.01, betas=(0.9, 0.95))
    train_loader = make_loader(split="train", batch_size=batch_size, shuffle=True)
    it = cycle_loader(train_loader)
    test_loader = make_loader(split="test", batch_size=batch_size, shuffle=False)

    # Capture per-cycle logits only if TD supervisor needs them.
    capture_per_cycle_logits = (supervisor == "td")

    print(f"\n  ARM={arm}  seed={seed}  steps={steps}  detach={detach}  "
          f"supervisor={supervisor}  capture_logits={capture_per_cycle_logits}  "
          f"lambda_sup={LAMBDA_SUP}")
    t0 = time.time()

    checkpoint_results = {}
    losses = []
    next_ckpt_idx = 0

    model.train()
    for step in range(1, steps + 1):
        x, y = next(it)
        x, y = x.to(device, non_blocking=True), y.to(device, non_blocking=True)

        logits, _, aux = model(
            x, arch_variant="v3h_measurer",
            mirror_detach_inputs=detach,
            capture_per_cycle_logits=capture_per_cycle_logits,
        )
        task_loss = F.cross_entropy(
            logits.reshape(-1, logits.shape[-1]),
            y.reshape(-1), ignore_index=IGNORE_LABEL_ID,
        )

        if supervisor == "td":
            sup_loss = td_supervisor_loss(aux, logits, y)
        elif supervisor == "bce":
            sup_loss = bce_supervisor_loss(aux, logits, y)
        else:
            raise ValueError(f"unknown supervisor {supervisor!r}")
        loss = task_loss + LAMBDA_SUP * sup_loss

        if not torch.isfinite(loss):
            print(f"    step {step}: NaN/Inf loss — aborting this arm-seed.")
            return {"arm": arm, "seed": seed, "aborted": True, "losses": losses}

        opt.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        losses.append(float(task_loss.item()))

        # Checkpoint eval at specific steps
        if next_ckpt_idx < len(CHECKPOINTS) and step == CHECKPOINTS[next_ckpt_idx]:
            ckpt_step = CHECKPOINTS[next_ckpt_idx]
            result = evaluate(
                model, "respira", test_loader, device=device,
                max_batches=eval_batches, record_trajectory=True,
                arch_variant="v3h_measurer",
            )
            ia = result.get("inside_analysis") or {}
            checkpoint_results[str(ckpt_step)] = {
                "token_accuracy": result["token_accuracy"],
                "exact_accuracy": result["exact_accuracy"],
                "mean_loss_per_token": result["mean_loss_per_token"],
                "task_loss_recent": sum(losses[-20:]) / min(len(losses), 20),
                "mean_halt_cycle": ia.get("mean_halt_cycle"),
                "mean_confidence_at_halt": ia.get("mean_confidence_at_halt"),
                "frac_halted_by_cycle_2": ia.get("frac_halted_by_cycle_2"),
                "calib_spearman_conf_vs_correctness": ia.get("calib_spearman_conf_vs_correctness"),
            }
            def _fmt(v, fmt):
                return format(v, fmt) if v is not None else "n/a"
            print(f"    step {ckpt_step:>4d}  token_acc={result['token_accuracy']:.4f}  "
                  f"exact={result['exact_accuracy']:.4f}  "
                  f"halt={_fmt(ia.get('mean_halt_cycle'), '.2f')}  "
                  f"conf={_fmt(ia.get('mean_confidence_at_halt'), '.3f')}  "
                  f"calib={_fmt(ia.get('calib_spearman_conf_vs_correctness'), '.3f')}")
            model.train()
            next_ckpt_idx += 1

    elapsed = time.time() - t0
    print(f"    DONE  arm={arm} seed={seed}  elapsed={elapsed:.0f}s")
    return {
        "arm": arm, "seed": seed, "elapsed_s": elapsed,
        "detach": detach, "supervisor": supervisor,
        "lambda_sup": LAMBDA_SUP,
        "checkpoints": checkpoint_results,
        "first_task_loss": losses[0],
        "last_task_loss": losses[-1],
        "aborted": False,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=str, default="0,1,2")
    ap.add_argument("--steps", type=int, default=2500)
    ap.add_argument("--batch_size", type=int, default=64)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--eval_batches", type=int, default=20)
    ap.add_argument("--arms", type=str, default="v3hp_full,v3hp_td_only,v3hp_detach_only",
                    help=f"Comma-separated arm names. Valid: {list(ARMS)}")
    ap.add_argument("--out", type=str, default=None,
                    help="Output JSON path (default: phase3_stage2_results_YYYY-MM-DD.json)")
    args = ap.parse_args()

    seeds = [int(s) for s in args.seeds.split(",")]
    arms = [a.strip() for a in args.arms.split(",")]
    for arm in arms:
        if arm not in ARMS:
            raise ValueError(f"Unknown arm {arm!r}. Valid: {list(ARMS)}")

    if args.out:
        out_path = args.out
    else:
        out_path = f"phase3_stage2_results_{datetime.now().strftime('%Y-%m-%d')}.json"

    print("=" * 70)
    print("  RESPIRA PHASE-3 STAGE 2 v3h-prime SWEEP")
    print(f"  seeds={seeds}  steps={args.steps}  batch={args.batch_size}  lr={args.lr}")
    print(f"  arms={arms}  lambda_sup={LAMBDA_SUP}")
    print(f"  output: {out_path}")
    print("=" * 70)

    all_results = {
        "metadata": {
            "started_at": datetime.now(timezone.utc).isoformat(),
            "seeds": seeds,
            "steps": args.steps,
            "batch_size": args.batch_size,
            "lr": args.lr,
            "lambda_sup": LAMBDA_SUP,
            "eval_batches": args.eval_batches,
            "arms": arms,
            "arm_configs": {a: ARMS[a] for a in arms},
            "pre_registration": "palace/south/respira-phase3-stage2-v3h-prime-preregistration-2026-05-28.md",
            "ratified_by": "Clayton",
            "ratified_at": "2026-05-29 morning",
        },
        "runs": [],
    }

    t_total = time.time()
    for arm in arms:
        for seed in seeds:
            print(f"\n--- ARM {arm}  SEED {seed} ---")
            result = run_arm(
                arm=arm, seed=seed, steps=args.steps,
                batch_size=args.batch_size, lr=args.lr,
                eval_batches=args.eval_batches,
            )
            all_results["runs"].append(result)
            # Write incrementally so partial results survive interruption.
            with open(out_path, "w") as f:
                json.dump(all_results, f, indent=2)

    all_results["metadata"]["elapsed_total_s"] = time.time() - t_total
    with open(out_path, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\n{'=' * 70}")
    print(f"  STAGE 2 SWEEP DONE — {len(all_results['runs'])} runs, "
          f"{(time.time() - t_total)/60:.1f} min total")
    print(f"  results: {out_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
