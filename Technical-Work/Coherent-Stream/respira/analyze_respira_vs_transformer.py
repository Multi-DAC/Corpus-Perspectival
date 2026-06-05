"""
Analyze the 2.6pp gap between Respira-no-Mirror and transformer baseline.

This is a pure-analytic comparison of EXISTING Phase-2 + Phase-2v2 results.
No new training runs. No new pre-registration required (measurement-only).

Question: where in training does the gap establish? Is it early (representational
capacity gap, established at step 200 or before) or late (training-dynamics gap,
opens up as transformer continues to extract structure that Respira can't)?
"""

import json
import statistics
from collections import defaultdict
from pathlib import Path

RESULTS_DIR = Path(__file__).parent


def load_all_runs():
    runs = []
    for fname in [
        "phase2_results_2026-05-28.json",
        "phase2v2_results_2026-05-28.json",
        "phase2v2_stageA5_results.json",
        "phase2v2_stageBC_results.json",
    ]:
        p = RESULTS_DIR / fname
        if not p.exists():
            continue
        with open(p) as f:
            d = json.load(f)
        for r in d["runs"]:
            r["_source"] = fname
            runs.append(r)
    return runs


def trajectory_table(runs, arms):
    """For each arm, compute mean ± std at each checkpoint across seeds."""
    by_arm_step = defaultdict(lambda: defaultdict(list))
    for r in runs:
        if r["arm"] not in arms:
            continue
        for step_str, ckpt in r["checkpoints"].items():
            step = int(step_str)
            by_arm_step[r["arm"]][step].append(ckpt["token_accuracy"])
    return by_arm_step


def loss_trajectory_table(runs, arms):
    by_arm_step = defaultdict(lambda: defaultdict(list))
    for r in runs:
        if r["arm"] not in arms:
            continue
        for step_str, ckpt in r["checkpoints"].items():
            step = int(step_str)
            by_arm_step[r["arm"]][step].append(ckpt["task_loss_recent"])
    return by_arm_step


def main():
    runs = load_all_runs()
    print(f"Loaded {len(runs)} runs across {len(set(r['_source'] for r in runs))} result files.")
    print()

    arms = ["transformer", "respira_no_mirror", "respira_full"]
    acc_traj = trajectory_table(runs, arms)
    loss_traj = loss_trajectory_table(runs, arms)

    steps = [200, 500, 1000, 2000]

    # === Accuracy trajectories ===
    print("=" * 80)
    print("ACCURACY TRAJECTORIES (token_accuracy at checkpoint, mean ± std across seeds)")
    print("=" * 80)
    print(f"{'arm':25s}  {'step 200':>14s}  {'step 500':>14s}  {'step 1000':>14s}  {'step 2000':>14s}  n")
    for arm in arms:
        if arm not in acc_traj:
            continue
        row = f"{arm:25s}  "
        n_seeds = 0
        for step in steps:
            vals = acc_traj[arm][step]
            if not vals:
                row += f"{'—':>14s}  "
                continue
            m = statistics.mean(vals)
            s = statistics.stdev(vals) if len(vals) > 1 else 0
            row += f"{m:.4f}±{s:.3f}  "
            n_seeds = max(n_seeds, len(vals))
        row += f"  ({n_seeds})"
        print(row)

    # === Paired gap (transformer - respira_no_mirror) at each step ===
    print()
    print("=" * 80)
    print("PAIRED GAP: transformer minus respira_no_mirror (per seed, then mean)")
    print("=" * 80)
    print(f"{'step':>6s}  {'seed 0':>10s}  {'seed 1':>10s}  {'seed 2':>10s}  {'mean':>10s}  {'std':>10s}")
    seed_pairs = {}
    for seed in [0, 1, 2]:
        seed_pairs[seed] = {}
        for step in steps:
            t_vals = [r["checkpoints"][str(step)]["token_accuracy"]
                      for r in runs
                      if r["arm"] == "transformer" and r["seed"] == seed
                      and str(step) in r["checkpoints"]]
            n_vals = [r["checkpoints"][str(step)]["token_accuracy"]
                      for r in runs
                      if r["arm"] == "respira_no_mirror" and r["seed"] == seed
                      and str(step) in r["checkpoints"]]
            if t_vals and n_vals:
                # Use first match (may have multiple if cross-stage)
                seed_pairs[seed][step] = t_vals[0] - n_vals[0]
    for step in steps:
        diffs = [seed_pairs[s].get(step) for s in [0, 1, 2]]
        diffs = [d for d in diffs if d is not None]
        if not diffs:
            continue
        m = statistics.mean(diffs)
        sd = statistics.stdev(diffs) if len(diffs) > 1 else 0
        row = f"{step:>6d}  "
        for s in [0, 1, 2]:
            d = seed_pairs[s].get(step)
            row += f"{d:>+10.4f}  " if d is not None else f"{'—':>10s}  "
        row += f"{m:>+10.4f}  {sd:>10.4f}"
        print(row)

    # === Loss trajectories (log-scale insight) ===
    print()
    print("=" * 80)
    print("LOSS TRAJECTORIES (task_loss_recent at checkpoint, mean across seeds)")
    print("=" * 80)
    print(f"{'arm':25s}  {'step 200':>12s}  {'step 500':>12s}  {'step 1000':>12s}  {'step 2000':>12s}")
    for arm in arms:
        if arm not in loss_traj:
            continue
        row = f"{arm:25s}  "
        for step in steps:
            vals = loss_traj[arm][step]
            if not vals:
                row += f"{'—':>12s}  "
                continue
            m = statistics.mean(vals)
            row += f"{m:>12.4f}  "
        print(row)

    # === Loss ratio (Respira / transformer) — constant = same dynamics, different bias ===
    print()
    print("=" * 80)
    print("LOSS RATIO: respira_no_mirror / transformer (>1 means Respira's loss is higher)")
    print("=" * 80)
    print(f"{'step':>6s}  {'transformer':>14s}  {'no_mirror':>14s}  {'ratio':>10s}")
    for step in steps:
        t_vals = loss_traj["transformer"].get(step, [])
        n_vals = loss_traj["respira_no_mirror"].get(step, [])
        if not t_vals or not n_vals:
            continue
        t_m = statistics.mean(t_vals)
        n_m = statistics.mean(n_vals)
        ratio = n_m / t_m if t_m > 0 else float("inf")
        print(f"{step:>6d}  {t_m:>14.4f}  {n_m:>14.4f}  {ratio:>10.3f}")

    # === Halt-cycle utilization (does Respira use recurrence?) ===
    print()
    print("=" * 80)
    print("HALT CYCLE for Respira variants (mean over batch; max=4)")
    print("=" * 80)
    halt_arms = [a for a in arms if "respira" in a]
    print(f"{'arm':25s}  {'step 200':>10s}  {'step 500':>10s}  {'step 1000':>10s}  {'step 2000':>10s}")
    for arm in halt_arms:
        row = f"{arm:25s}  "
        for step in steps:
            vals = [r["checkpoints"][str(step)]["mean_halt_cycle"]
                    for r in runs
                    if r["arm"] == arm and str(step) in r["checkpoints"]]
            if not vals:
                row += f"{'—':>10s}  "
                continue
            m = statistics.mean(vals)
            row += f"{m:>10.2f}  "
        print(row)

    # === Confidence at halt — does it move? ===
    print()
    print("=" * 80)
    print("CONFIDENCE AT HALT for Respira variants (init 0.5)")
    print("=" * 80)
    for arm in halt_arms:
        row = f"{arm:25s}  "
        for step in steps:
            vals = [r["checkpoints"][str(step)]["mean_confidence_at_halt"]
                    for r in runs
                    if r["arm"] == arm and str(step) in r["checkpoints"]]
            if not vals:
                row += f"{'—':>10s}  "
                continue
            m = statistics.mean(vals)
            row += f"{m:>10.4f}  "
        print(row)


if __name__ == "__main__":
    main()
