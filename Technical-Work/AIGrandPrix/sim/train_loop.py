"""
Anakin Training Loop — Continuous Improvement

Runs train_infinite.py in a loop, each time resuming from the
best checkpoint (best gauntlet transfer score) of the previous run.

Each run: 80M steps on infinite procedural course.
Between runs: auto-restarts from best model.

Usage:
    python train_loop.py
    python train_loop.py --steps-per-run 80000000
    python train_loop.py --resume path/to/checkpoint.zip

To stop gracefully: Ctrl+C (finishes current run's checkpoint, then exits)
"""

import os
import sys
import time
import signal
import subprocess
from pathlib import Path
from glob import glob

SIM_DIR = Path(__file__).parent
RUNS_DIR = SIM_DIR / 'runs'
TRAIN_SCRIPT = SIM_DIR / 'train_infinite.py'

# Graceful shutdown flag
_stop_after_run = False

def _signal_handler(sig, frame):
    global _stop_after_run
    if _stop_after_run:
        print("\n[train_loop] Second interrupt — killing immediately.")
        sys.exit(1)
    print("\n[train_loop] Caught interrupt — will stop after current run finishes.")
    print("[train_loop] Press Ctrl+C again to kill immediately.")
    _stop_after_run = True

signal.signal(signal.SIGINT, _signal_handler)


def find_latest_best_model() -> str | None:
    """Find the best model from the most recent completed run."""
    run_dirs = sorted(RUNS_DIR.glob('infinite_*'), key=lambda p: p.stat().st_mtime)

    for run_dir in reversed(run_dirs):
        best_model = run_dir / 'best' / 'best_model.zip'
        if best_model.exists():
            return str(best_model)

    return None


def run_training(resume_path: str, total_steps: int, n_envs: int) -> Path | None:
    """Run a single training cycle. Returns the run directory."""
    cmd = [
        sys.executable, str(TRAIN_SCRIPT),
        '--total-steps', str(total_steps),
        '--n-envs', str(n_envs),
    ]

    if resume_path:
        cmd.extend(['--resume', resume_path])

    print(f"\n{'=' * 60}")
    print(f"[train_loop] Starting training run")
    print(f"  Resume: {resume_path or 'FROM SCRATCH'}")
    print(f"  Steps:  {total_steps:,}")
    print(f"  Time:   {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 60}\n")

    result = subprocess.run(cmd, cwd=str(SIM_DIR))

    if result.returncode != 0:
        print(f"\n[train_loop] Training exited with code {result.returncode}")
        return None

    # Find the run directory that was just created (most recent)
    run_dirs = sorted(RUNS_DIR.glob('infinite_*'), key=lambda p: p.stat().st_mtime)
    return run_dirs[-1] if run_dirs else None


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Anakin continuous training loop')
    parser.add_argument('--steps-per-run', type=int, default=80_000_000,
                        help='Steps per training run (default: 80M)')
    parser.add_argument('--n-envs', type=int, default=8,
                        help='Parallel environments (default: 8)')
    parser.add_argument('--resume', type=str, default=None,
                        help='Initial checkpoint to resume from (auto-detects if not set)')
    parser.add_argument('--max-runs', type=int, default=0,
                        help='Stop after N runs (0 = infinite)')
    args = parser.parse_args()

    run_count = 0
    resume_path = args.resume

    # Auto-detect starting checkpoint if not specified
    if resume_path is None:
        resume_path = find_latest_best_model()
        if resume_path:
            print(f"[train_loop] Auto-detected checkpoint: {resume_path}")
        else:
            print("[train_loop] No checkpoint found — starting from scratch")

    print(f"[train_loop] Anakin continuous training — {args.steps_per_run:,} steps per run")
    print(f"[train_loop] Ctrl+C to stop after current run")

    while True:
        if _stop_after_run:
            print(f"\n[train_loop] Stopping as requested after {run_count} run(s).")
            break

        if args.max_runs > 0 and run_count >= args.max_runs:
            print(f"\n[train_loop] Reached max runs ({args.max_runs}). Done.")
            break

        run_count += 1
        print(f"\n[train_loop] === RUN {run_count} ===")

        run_dir = run_training(resume_path, args.steps_per_run, args.n_envs)

        if run_dir is None:
            print("[train_loop] Run failed. Waiting 30s before retry...")
            time.sleep(30)
            continue

        # Find best model from completed run for next iteration
        best_model = run_dir / 'best' / 'best_model.zip'
        final_checkpoints = sorted((run_dir / 'checkpoints').glob('*.zip'))

        if best_model.exists():
            resume_path = str(best_model)
            print(f"\n[train_loop] Run {run_count} complete. Best model: {resume_path}")
        elif final_checkpoints:
            resume_path = str(final_checkpoints[-1])
            print(f"\n[train_loop] Run {run_count} complete. No best model — using latest checkpoint: {resume_path}")
        else:
            print(f"\n[train_loop] Run {run_count} complete but no checkpoints found. Stopping.")
            break

        # Brief pause between runs
        print(f"[train_loop] Next run starting in 10s...")
        time.sleep(10)

    print(f"\n[train_loop] Anakin training loop finished. Total runs: {run_count}")


if __name__ == '__main__':
    main()
