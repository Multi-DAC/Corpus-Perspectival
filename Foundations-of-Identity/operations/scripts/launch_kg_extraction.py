"""Launch kg_extract_corpus.py as a Windows-detached process.

Survives parent termination (Claude Code session end, daemon restart).
Writes:
  - PID + start metadata to memory/kg_extraction_run.json
  - All stdout/stderr to memory/kg_extraction_run.log

Usage:
    python operations/scripts/launch_kg_extraction.py [--retry-errors] [-- sources drift,library,...] [extra args]
"""
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

CLAWD = Path(r"C:\Users\mercu\clawd")
SCRIPT = CLAWD / "operations" / "scripts" / "kg_extract_corpus.py"
LOG = CLAWD / "memory" / "kg_extraction_run.log"
META = CLAWD / "memory" / "kg_extraction_run.json"

DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200
CREATE_BREAKAWAY_FROM_JOB = 0x01000000


def main():
    args = sys.argv[1:]
    cmd = [sys.executable, str(SCRIPT), *args]

    LOG.parent.mkdir(parents=True, exist_ok=True)
    log_fh = open(LOG, "ab", buffering=0)
    header = f"\n=== detached launch {datetime.now().isoformat()} ===\nCMD: {cmd}\n".encode()
    log_fh.write(header)

    flags = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_BREAKAWAY_FROM_JOB

    proc = subprocess.Popen(
        cmd,
        stdout=log_fh,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
        creationflags=flags,
        close_fds=True,
        cwd=str(CLAWD),
    )

    time.sleep(0.5)
    META.write_text(json.dumps({
        "pid": proc.pid,
        "started_at": datetime.now().isoformat(),
        "cmd": cmd,
        "log_path": str(LOG),
    }, indent=2), encoding="utf-8")

    print(f"detached PID={proc.pid} log={LOG}")
    print(f"check: type \"{LOG}\" or tail -f via WSL")


if __name__ == "__main__":
    main()
