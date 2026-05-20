"""Detached launcher for the monitor scheduler.

Same DETACHED_PROCESS pattern as launch_kg_extraction.py and
schedule_kg_retry.py. Launches the scheduler as a parent-survivor
process; survives Claude Code session ends and daemon restarts.

Usage:
    python operations/monitors/scheduler_launcher.py
"""
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

CLAWD = Path(r"C:\Users\mercu\clawd")
SCHEDULER_SCRIPT = CLAWD / "operations" / "monitors" / "scheduler.py"
LAUNCH_LOG = CLAWD / "memory" / "monitor_scheduler_launch.log"

DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200
CREATE_BREAKAWAY_FROM_JOB = 0x01000000


def main():
    LAUNCH_LOG.parent.mkdir(parents=True, exist_ok=True)
    log_fh = open(LAUNCH_LOG, "ab", buffering=0)
    log_fh.write(f"\n=== detached launch {datetime.now().isoformat()} ===\n".encode())

    cmd = [sys.executable, str(SCHEDULER_SCRIPT)]
    flags = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_BREAKAWAY_FROM_JOB

    proc = subprocess.Popen(
        cmd,
        stdout=log_fh,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
        creationflags=flags,
        close_fds=True,
    )
    print(f"monitor scheduler detached PID={proc.pid}")
    print(f"log: {LAUNCH_LOG}")
    print(f"status: python operations/monitors/scheduler.py --status")
    print(f"stop:   python operations/monitors/scheduler.py --stop")


if __name__ == "__main__":
    main()
