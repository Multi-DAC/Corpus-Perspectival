"""
Resilient training loop — auto-restarts from best checkpoint on crash.
Runs until total target steps are reached.
"""
import subprocess
import sys
import time
from pathlib import Path

TARGET_STEPS = 20_000_000
STEPS_PER_RUN = 2_000_000  # Shorter runs to survive crashes
RESUME_DIR = Path(__file__).parent / 'runs'

def find_latest_best():
    """Find the most recent best_model.zip."""
    candidates = []
    for d in RESUME_DIR.glob('infinite_*/best/best_model.zip'):
        candidates.append(d)
    if not candidates:
        return None
    return str(max(candidates, key=lambda p: p.stat().st_mtime))

def run_training(steps, resume_path=None):
    """Run a single training batch."""
    cmd = [sys.executable, '-u', 'train_infinite.py', '--total-steps', str(steps), '--n-envs', '4']
    if resume_path:
        cmd.extend(['--resume', resume_path])
    
    print(f"\n{'='*60}")
    print(f"Starting training: {steps:,} steps")
    if resume_path:
        print(f"Resuming from: {resume_path}")
    print(f"{'='*60}\n")
    
    result = subprocess.run(cmd, cwd=str(Path(__file__).parent))
    return result.returncode

def main():
    total_done = 0
    run_count = 0
    
    while total_done < TARGET_STEPS:
        run_count += 1
        remaining = TARGET_STEPS - total_done
        steps_this_run = min(STEPS_PER_RUN, remaining)
        
        resume = find_latest_best()
        print(f"\n*** Run {run_count} | {total_done:,}/{TARGET_STEPS:,} steps done | "
              f"This run: {steps_this_run:,} ***")
        
        start = time.time()
        code = run_training(steps_this_run, resume)
        elapsed = time.time() - start
        
        total_done += steps_this_run  # Count even if crashed — checkpoint saved
        
        if code != 0:
            print(f"\n!!! Run {run_count} crashed (code {code}) after {elapsed:.0f}s")
            print(f"    Will resume from latest best checkpoint...")
            time.sleep(5)  # Brief cooldown
        else:
            print(f"\n*** Run {run_count} completed in {elapsed:.0f}s ***")
    
    print(f"\n{'='*60}")
    print(f"All {TARGET_STEPS:,} steps complete across {run_count} runs!")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
