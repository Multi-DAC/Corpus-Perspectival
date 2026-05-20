"""One-shot scheduled trigger: sleep until target time, then launch KG --retry-errors.

Detached parent-survivor. Used 2026-05-19 Day 109 night to autonomously fire the
03:30 AM PST retry-pass after the 5-hour Opus cap (hit ~22:15 PST) rolls over.

Usage:
    python operations/scripts/schedule_kg_retry.py --at "2026-05-20 03:30"

Writes timing log to memory/kg_scheduled_retry.log.
"""
import argparse
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

CLAWD = Path(r"C:\Users\mercu\clawd")
LAUNCHER = CLAWD / "operations" / "scripts" / "launch_kg_extraction.py"
LOG = CLAWD / "memory" / "kg_scheduled_retry.log"

DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200
CREATE_BREAKAWAY_FROM_JOB = 0x01000000


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--at", required=True, help='Target time in "YYYY-MM-DD HH:MM" local')
    args = parser.parse_args()

    target = datetime.strptime(args.at, "%Y-%m-%d %H:%M")
    now = datetime.now()
    wait_seconds = (target - now).total_seconds()

    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a") as f:
        f.write(f"\n=== schedule trigger {now.isoformat()} ===\n")
        f.write(f"target: {target.isoformat()}\n")
        f.write(f"wait: {wait_seconds:.0f}s ({wait_seconds/3600:.2f}h)\n")
        f.flush()

        if wait_seconds <= 0:
            f.write("ERROR: target is in the past; aborting\n")
            sys.exit(1)

        # Sleep until target
        time.sleep(wait_seconds)

        fire_time = datetime.now()
        f.write(f"firing at {fire_time.isoformat()}\n")
        f.flush()

        # Launch the existing detached launcher
        cmd = [sys.executable, str(LAUNCHER), "--retry-errors"]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            f.write(f"launcher stdout: {result.stdout}\n")
            f.write(f"launcher stderr: {result.stderr}\n")
            f.write(f"launcher returncode: {result.returncode}\n")
        except Exception as e:
            f.write(f"launcher ERROR: {e}\n")


if __name__ == "__main__":
    main()
