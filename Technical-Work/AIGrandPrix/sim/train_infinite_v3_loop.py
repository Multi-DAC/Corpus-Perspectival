"""
Resilient v3 training loop (W5) — auto-restarts from the latest checkpoint on crash.
The vision-policy training crashes recurringly near ~7.7M steps (known recurring issue,
pre-dates today). Past-us beat it the same way for the original curriculum: train in short
chunks and restart from the best/latest checkpoint, so a fresh PROCESS each chunk sheds
whatever per-process state (memory / curriculum-depth) triggers the crash. Progress
accumulates in the policy WEIGHTS (resumed via PPO.load) + the per-checkpoint vecnorm
(saved by CheckpointWithVecNormalize — the fix added 2026-06-01 that makes resume correct).

Counts steps even on crash (checkpoint is saved). Runs detached; check vq1_w5loop.log.
"""
import subprocess, sys, glob, os, time
from pathlib import Path

HERE = Path(__file__).parent
TARGET_STEPS = 30_000_000
CHUNK = 2_000_000          # < the ~7.7M crash point; fresh process each chunk sheds the trigger
N_ENVS = 8
GROUND_START = '0.5'


def latest_ckpt():
    """Most-recent ppo_v3 checkpoint (across all w5* runs) that has a paired vecnorm.pkl."""
    cands = []
    for z in glob.glob(str(HERE / 'runs' / 'infinite_v3_vq1_vision_w5*' / 'checkpoints' / 'ppo_v3_*_steps.zip')):
        if os.path.exists(z[:-4] + '_vecnorm.pkl'):
            cands.append(z)
    return max(cands, key=os.path.getmtime) if cands else None


def run_chunk(steps, resume):
    cmd = [sys.executable, '-u', 'train_infinite_v3.py',
           '--total-steps', str(steps), '--n-envs', str(N_ENVS),
           '--perception-obs', '--ground-start-prob', GROUND_START, '--tag', 'vq1_vision_w5loop']
    if resume:
        cmd += ['--resume', resume]
    print(f"\n{'='*64}\n[loop] chunk: {steps:,} steps | resume={resume}\n{'='*64}", flush=True)
    try:
        # Per-chunk timeout: a 2M chunk runs ~13 min; 30 min catches a HANG (which would
        # otherwise block the loop forever — subprocess.run kills the process on timeout).
        return subprocess.run(cmd, cwd=str(HERE), timeout=1800).returncode
    except subprocess.TimeoutExpired:
        print("[loop] chunk TIMED OUT (>1800s) — killed; resuming from latest checkpoint", flush=True)
        return 124


def main():
    done = 0; run = 0
    while done < TARGET_STEPS:
        run += 1
        chunk = min(CHUNK, TARGET_STEPS - done)
        resume = latest_ckpt()
        print(f"\n*** [loop] run {run} | {done:,}/{TARGET_STEPS:,} done | this chunk {chunk:,} | resume={'yes' if resume else 'FRESH'} ***", flush=True)
        t = time.time()
        code = run_chunk(chunk, resume)
        dt = time.time() - t
        done += chunk  # count even if it crashed — checkpoints (+vecnorm) are saved
        if code != 0:
            print(f"[loop] run {run} crashed (code {code}) after {dt:.0f}s — resuming from latest checkpoint", flush=True)
            time.sleep(5)
        else:
            print(f"[loop] run {run} done in {dt:.0f}s", flush=True)
    print(f"\n{'='*64}\n[loop] TARGET {TARGET_STEPS:,} reached across {run} runs\n{'='*64}", flush=True)


if __name__ == '__main__':
    main()
