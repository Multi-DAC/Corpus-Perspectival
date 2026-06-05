"""
Respira Phase-2 multi-seed sweep — three arms × three seeds × 2000 steps.

Pre-registration: `palace/south/respira-phase2-preregistration-2026-05-28.md`.

Arms:
  1. respira_full     — Planner + Executor + Mirror + C2 supervisor (lambda_cal=1.0)
  2. respira_no_mirror — Same architecture, mirror_authority=0 throughout (Mirror outputs unused, dynamics use defaults)
  3. transformer      — Matched transformer baseline (phase1_matched_config)

Captures: token_accuracy at steps [200, 500, 1000, 2000] (sample-efficiency curve),
exact accuracy, final task loss, halt distribution + confidence statistics (Respira variants).

Writes results to `phase2_results_YYYY-MM-DD.json` for `analyze_phase2.py` to consume.

DO NOT launch without Clayton's ratification of the pre-registration.
Run from respira/:  python3 sweep_phase2.py [--seeds 0,1,2] [--steps 2000]

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
from baselines.matched_transformer import MatchedTransformer, phase1_matched_config
from eval import evaluate
from train import supervisor_calibration_loss


CHECKPOINTS = [200, 500, 1000, 2000]
# Phase-3 §2 / §5c: no_mirror_5k extended-training convergence test uses additional checkpoints
# beyond the standard 2500-step training to test the W-N5k convergence prediction.
CHECKPOINTS_5K = [200, 500, 1000, 2000, 3000, 4000, 5000]


def build(name: str):
    if name in ("respira_full", "respira_no_mirror", "respira_no_mirror_5k"):
        return RespiraCell(
            planner_channels=32, executor_channels=64, seq_len=81, vocab_size=11,
            max_cycles=4, planner_omega=(0.05, 0.2), executor_omega=(0.5, 2.0),
            dt=0.1, mu_scale=1.0, halt_threshold=0.7,
        )
    if name == "respira_v3h":  # Phase-3: Mirror-as-measurer (Read B test).
        return RespiraCell(
            planner_channels=32, executor_channels=64, seq_len=81, vocab_size=11,
            max_cycles=4, planner_omega=(0.05, 0.2), executor_omega=(0.5, 2.0),
            dt=0.1, mu_scale=1.0, halt_threshold=0.7,
            mirror_kind="measurer",     # Use MirrorMeasurer (zero channel-modulation DOF)
            measurer_halt_threshold=0.5,  # Pre-registered §4c, NOT learnable.
        )
    if name == "respira_v2c":  # Phase-2v2 cuscuton-Mirror v2-c: 2 learnable scalars (γ_μ, γ_c)
        return RespiraCell(
            planner_channels=32, executor_channels=64, seq_len=81, vocab_size=11,
            max_cycles=4, planner_omega=(0.05, 0.2), executor_omega=(0.5, 2.0),
            dt=0.1, mu_scale=1.0, halt_threshold=0.7,
            learn_mu=True, learn_coupling=True, default_mu_init=1.0, default_coupling_init=0.5,
        )
    if name == "respira_v2c1_mu":  # Phase-2v2 Stage A.5: 1-scalar variant — γ_μ only
        return RespiraCell(
            planner_channels=32, executor_channels=64, seq_len=81, vocab_size=11,
            max_cycles=4, planner_omega=(0.05, 0.2), executor_omega=(0.5, 2.0),
            dt=0.1, mu_scale=1.0, halt_threshold=0.7,
            learn_mu=True, learn_coupling=False, default_mu_init=1.0,
        )
    if name == "respira_v2c1_c":  # Phase-2v2 Stage A.5: 1-scalar variant — γ_c only
        return RespiraCell(
            planner_channels=32, executor_channels=64, seq_len=81, vocab_size=11,
            max_cycles=4, planner_omega=(0.05, 0.2), executor_omega=(0.5, 2.0),
            dt=0.1, mu_scale=1.0, halt_threshold=0.7,
            learn_mu=False, learn_coupling=True, default_coupling_init=0.5,
        )
    if name == "respira_v2a":  # Phase-2v2 Stage B: phase-locking rule, zero DOF
        return RespiraCell(
            planner_channels=32, executor_channels=64, seq_len=81, vocab_size=11,
            max_cycles=4, planner_omega=(0.05, 0.2), executor_omega=(0.5, 2.0),
            dt=0.1, mu_scale=1.0, halt_threshold=0.7,
            # No learnable defaults — v2-a is pure rule, no learnable params in Mirror position.
        )
    if name == "respira_v2b":  # Phase-2v2 Stage C: coherence-energy loss term, zero DOF
        return RespiraCell(
            planner_channels=32, executor_channels=64, seq_len=81, vocab_size=11,
            max_cycles=4, planner_omega=(0.05, 0.2), executor_omega=(0.5, 2.0),
            dt=0.1, mu_scale=1.0, halt_threshold=0.7,
            # No learnable defaults — v2-b is a fixed loss-term penalty, no Mirror params.
        )
    if name == "transformer":
        return MatchedTransformer(**phase1_matched_config())
    raise ValueError(name)


def run_arm(arm: str, seed: int, steps: int, batch_size: int, lr: float,
            lambda_cal: float, eval_batches: int) -> dict:
    """Train one arm with one seed, eval at checkpoints, return result dict."""
    torch.manual_seed(seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    model = build(arm).to(device)
    is_respira = arm.startswith("respira")
    use_supervisor = (arm == "respira_full")
    # mirror_authority=0 means "use defaults" — applies to no_mirror, v2c, and the
    # 1-scalar v2c1 variants (all have constants or learnable scalars replacing them,
    # never the full Mirror). For respira_full, authority=1 (Mirror used).
    # respira_v3h uses arch_variant="v3h_measurer" path, which sets defaults
    # directly and ignores mirror_authority — set 0.0 for clarity.
    no_mirror_arms = {"respira_no_mirror", "respira_no_mirror_5k", "respira_v2c",
                      "respira_v2c1_mu", "respira_v2c1_c", "respira_v2a", "respira_v2b",
                      "respira_v3h"}
    mirror_authority = 0.0 if arm in no_mirror_arms else 1.0
    if arm == "respira_v2a":
        arch_variant = "v2a_phase_locking"
    elif arm == "respira_v3h":
        arch_variant = "v3h_measurer"
    else:
        arch_variant = "default"
    use_v2b_coherence_loss = (arm == "respira_v2b")
    LAMBDA_COH = 0.1  # Pre-registered constant from §3b — NOT tuned.
    # Phase-3 v3h supervisor: BCE(confidence_at_halt, per_batch_correctness.detach()).
    # Pre-registered λ_sup = 0.5 at §4d. NOT tuned.
    use_v3h_supervisor = (arm == "respira_v3h")
    LAMBDA_SUP = 0.5

    # Per-arm step + checkpoint overrides (Phase-3 §2: no_mirror_5k = 5000 steps).
    arm_steps = steps
    arm_ckpts = list(CHECKPOINTS)
    if arm == "respira_no_mirror_5k":
        arm_steps = 5000
        arm_ckpts = list(CHECKPOINTS_5K)

    opt = AdamW(model.parameters(), lr=lr, weight_decay=0.01, betas=(0.9, 0.95))
    train_loader = make_loader(split="train", batch_size=batch_size, shuffle=True)
    it = cycle_loader(train_loader)
    test_loader = make_loader(split="test", batch_size=batch_size, shuffle=False)

    print(f"\n  ARM={arm}  seed={seed}  steps={arm_steps}  "
          f"mirror_authority={mirror_authority}  supervisor={use_supervisor}  "
          f"v3h_sup={use_v3h_supervisor}  arch_variant={arch_variant}")
    t0 = time.time()

    checkpoint_results = {}
    losses = []
    next_ckpt_idx = 0

    model.train()
    for step in range(1, arm_steps + 1):
        x, y = next(it)
        x, y = x.to(device, non_blocking=True), y.to(device, non_blocking=True)

        aux = None
        if is_respira:
            logits, _, aux = model(x, mirror_authority=mirror_authority, arch_variant=arch_variant)
        else:
            logits = model(x)
        task_loss = F.cross_entropy(logits.reshape(-1, logits.shape[-1]),
                                    y.reshape(-1), ignore_index=IGNORE_LABEL_ID)

        if use_supervisor and aux is not None:
            cal_loss = supervisor_calibration_loss(aux, logits, y)
            loss = task_loss + lambda_cal * cal_loss
        elif use_v2b_coherence_loss and aux is not None and "coherence_energy" in aux:
            # v2-b: add fixed coherence-energy penalty (§3b pre-registered λ_coh = 0.1).
            loss = task_loss + LAMBDA_COH * aux["coherence_energy"]
        elif use_v3h_supervisor and aux is not None and "confidence_at_halt" in aux:
            # Phase-3 v3h §4d supervisor: BCE(confidence_at_halt, per_batch_correctness).
            # Per-batch correctness = mean per-token argmax-equality, masked to ignore
            # IGNORE_LABEL_ID padding positions. Detached to keep the supervisor gradient
            # off the task substrate (the BCE pressure only flows into the Mirror's
            # readout head + attention pool).
            valid = (y != IGNORE_LABEL_ID).float()  # [B, S]
            argmax = logits.argmax(dim=-1)           # [B, S]
            correct_per_token = (argmax == y).float() * valid
            n_valid = valid.sum(dim=-1).clamp(min=1.0)
            correctness_pb = correct_per_token.sum(dim=-1) / n_valid  # [B] in [0, 1]
            conf = aux["confidence_at_halt"].clamp(1e-6, 1.0 - 1e-6)  # numerical safety
            sup_loss = F.binary_cross_entropy(conf, correctness_pb.detach())
            loss = task_loss + LAMBDA_SUP * sup_loss
        else:
            loss = task_loss

        if not torch.isfinite(loss):
            print(f"    step {step}: NaN/Inf loss — aborting this arm-seed.")
            return {"arm": arm, "seed": seed, "aborted": True, "losses": losses}

        opt.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        losses.append(float(task_loss.item()))

        # Checkpoint eval at specific steps
        if next_ckpt_idx < len(arm_ckpts) and step == arm_ckpts[next_ckpt_idx]:
            ckpt_step = arm_ckpts[next_ckpt_idx]
            result = evaluate(
                model, ("respira" if is_respira else "transformer"),
                test_loader, device=device, max_batches=eval_batches,
                record_trajectory=is_respira,
                arch_variant=arch_variant if is_respira else "default",
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
            print(f"    step {ckpt_step:>4d}  token_acc={result['token_accuracy']:.4f}  "
                  f"exact_acc={result['exact_accuracy']:.4f}  "
                  + (f"halt_cycle={ia.get('mean_halt_cycle', 'n/a'):.2f}  "
                     f"conf@halt={ia.get('mean_confidence_at_halt', 'n/a'):.3f}"
                     if is_respira else ""))
            model.train()
            next_ckpt_idx += 1

    elapsed = time.time() - t0
    # Log learned gamma values (pre-reg §5 secondary metric — fixed from Stage A oversight).
    learned_gammas = {}
    if is_respira and hasattr(model, "default_mu_param"):
        learned_gammas["gamma_mu_final"] = float(model.default_mu_param.detach().item())
    if is_respira and hasattr(model, "default_coupling_param"):
        learned_gammas["gamma_c_final"] = float(model.default_coupling_param.detach().item())
    if learned_gammas:
        print(f"    learned gammas: {learned_gammas}")
    print(f"    DONE  arm={arm} seed={seed}  elapsed={elapsed:.0f}s")
    return {
        "arm": arm, "seed": seed, "elapsed_s": elapsed,
        "checkpoints": checkpoint_results,
        "first_task_loss": losses[0],
        "last_task_loss": losses[-1],
        "learned_gammas": learned_gammas,
        "aborted": False,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=str, default="0,1,2")
    ap.add_argument("--steps", type=int, default=2500)
    ap.add_argument("--batch_size", type=int, default=64)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--lambda_cal", type=float, default=1.0)
    ap.add_argument("--eval_batches", type=int, default=20)
    ap.add_argument("--arms", type=str, default="respira_full,respira_no_mirror,transformer",
                    help="Comma-separated arm names. Valid: respira_full, respira_no_mirror, "
                         "respira_v2c, transformer.")
    ap.add_argument("--out", type=str, default=None,
                    help="Output JSON path (default: phase{2|2v2}_results_YYYY-MM-DD.json)")
    args = ap.parse_args()

    seeds = [int(s) for s in args.seeds.split(",")]
    arms = [a.strip() for a in args.arms.split(",")]

    # Auto-name based on arms involved — phase2v2 if any v2 arm is present.
    if args.out:
        out_path = args.out
    else:
        is_v2 = any("v2" in a for a in arms)
        tag = "phase2v2" if is_v2 else "phase2"
        out_path = f"{tag}_results_{datetime.now().strftime('%Y-%m-%d')}.json"

    print("=" * 70)
    print("  RESPIRA PHASE-2 SWEEP")
    print(f"  seeds={seeds}  steps={args.steps}  batch={args.batch_size}  lr={args.lr}")
    print(f"  arms={arms}")
    print(f"  output: {out_path}")
    print("=" * 70)

    all_results = {
        "metadata": {
            "started_at": datetime.now(timezone.utc).isoformat(),
            "seeds": seeds,
            "steps": args.steps,
            "batch_size": args.batch_size,
            "lr": args.lr,
            "lambda_cal": args.lambda_cal,
            "eval_batches": args.eval_batches,
            "arms": arms,
            "pre_registration": "palace/south/respira-phase2-preregistration-2026-05-28.md",
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
                lambda_cal=args.lambda_cal, eval_batches=args.eval_batches,
            )
            all_results["runs"].append(result)
            # Write incrementally so partial results survive interruption.
            with open(out_path, "w") as f:
                json.dump(all_results, f, indent=2)

    all_results["metadata"]["elapsed_total_s"] = time.time() - t_total
    with open(out_path, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\n{'=' * 70}")
    print(f"  SWEEP DONE — {len(all_results['runs'])} runs, "
          f"{(time.time() - t_total)/60:.1f} min total")
    print(f"  results: {out_path}")
    print(f"  next: python3 analyze_phase2.py {out_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
