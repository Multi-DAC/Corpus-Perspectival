"""
Anakin Training Launcher - Always resumes from best checkpoint

Usage:
    python run_anakin.py              # Start/resume training
    python run_anakin.py --eval       # Evaluate current model
    python run_anakin.py --resume     # Force resume from checkpoint
"""

import os
import sys
import glob
from pathlib import Path

# Paths
RUNS_DIR = Path(__file__).parent / "runs"
CHECKPOINT_PATTERN = "gauntlet_resume_*/checkpoints/ppo_drone_*_steps.zip"
BEST_MODEL_PATTERN = "gauntlet_resume_*/best/best_model.zip"

def find_best_checkpoint():
    """Find the most recent best checkpoint."""
    
    # First try best model
    best_models = sorted(RUNS_DIR.glob(BEST_MODEL_PATTERN), key=os.path.getmtime, reverse=True)
    if best_models:
        print(f"Found best model: {best_models[0]}")
        return str(best_models[0])
    
    # Then try latest checkpoint
    checkpoints = sorted(RUNS_DIR.glob(CHECKPOINT_PATTERN), key=os.path.getmtime, reverse=True)
    if checkpoints:
        print(f"Found checkpoint: {checkpoints[0]}")
        return str(checkpoints[0])
    
    return None

def get_latest_run_dir():
    """Get the most recent run directory."""
    run_dirs = [d for d in RUNS_DIR.iterdir() if d.is_dir() and d.name.startswith("gauntlet")]
    if not run_dirs:
        return None
    return max(run_dirs, key=lambda d: d.stat().st_mtime)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--eval", action="store_true", help="Evaluate only")
    parser.add_argument("--resume", action="store_true", help="Force resume from checkpoint")
    parser.add_argument("--steps", type=int, default=40_000_000, help="Total steps")
    parser.add_argument("--from-step", type=int, default=None, help="Resume from specific step")
    args = parser.parse_args()
    
    # Find checkpoint
    checkpoint = find_best_checkpoint() if args.resume or args.from_step else None
    
    if args.eval:
        if checkpoint:
            print(f"Evaluating: {checkpoint}")
            os.system(f"python train_ppo.py --eval {checkpoint} --track gauntlet")
        else:
            print("No checkpoint found!")
        return
    
    # Build command
    cmd = f"python train_ppo.py --track gauntlet --total-steps {args.steps}"
    
    if checkpoint:
        # Extract step count from checkpoint filename
        fname = Path(checkpoint).stem  # ppo_drone_1200000_steps
        if "steps" in fname:
            step_str = fname.split("_")[-2]
            from_step = int(step_str)
            cmd += f" --resume-from {from_step}"
            print(f"Resuming from step {from_step}")
        else:
            print(f"Using checkpoint but couldn't parse step: {checkpoint}")
    else:
        print("Starting FRESH training (no checkpoint found)")
    
    print(f"\nCommand: {cmd}\n")
    os.system(cmd)

if __name__ == "__main__":
    main()
