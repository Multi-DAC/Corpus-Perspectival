"""Detached daemon respawner.

Spawned by tools.self_control.restart_daemon() as a detached child of bridge.py.

Sequence:
  1. Wait `--delay` seconds (gives the originating Claude Code response time
     to flush, and creates a predictable observation window).
  2. Find the clawd.py daemon PID (via psutil scan — re-scan rather than trust
     a passed PID, in case the daemon respawned independently between spawn
     and now).
  3. Terminate the daemon (Windows TerminateProcess via psutil.terminate).
     Wait up to 10s for exit; fall back to kill() if needed.
  4. Wait 1s for OS to release file handles, telegram bot to disconnect, etc.
  5. Launch new daemon as fully detached process (DETACHED_PROCESS +
     CREATE_NEW_PROCESS_GROUP, no stdin/out/err inheritance).
  6. Verify new daemon's python.exe is alive after 5s.
  7. Write success/failure marker to memory/last_restart.json.

Run directly:
    python respawn.py --reason "..." --delay 10

Critical: this script must NEVER hang, even on errors. All operations have
timeouts. If something goes wrong, write the failure to the marker and exit.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

CLAWD_HOME = Path(os.environ.get("CLAWD_HOME", r"C:/Users/mercu/clawd"))
CLAWD_DAEMON = Path(os.environ.get("CLAWD_DAEMON", r"C:/Users/mercu/clawd-daemon"))
TRACE_LOG = CLAWD_HOME / "memory" / "respawn_trace.log"
RESTART_LOG = CLAWD_HOME / "memory" / "daemon_restart_log.jsonl"
RESTART_MARKER = CLAWD_HOME / "memory" / "last_restart.json"

DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200


def trace(msg: str) -> None:
    line = f"[{datetime.now().isoformat()}] {msg}\n"
    try:
        TRACE_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(TRACE_LOG, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass
    sys.stderr.write(line)


def log_event(entry: dict) -> None:
    entry = {"ts": datetime.now().isoformat(), "source": "respawn.py", **entry}
    try:
        RESTART_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(RESTART_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        trace(f"log_event failed: {e}")


def write_marker(payload: dict) -> None:
    try:
        merged = {}
        if RESTART_MARKER.exists():
            try:
                merged = json.loads(RESTART_MARKER.read_text(encoding="utf-8"))
            except Exception:
                merged = {}
        merged.update(payload)
        merged["last_marker_update"] = datetime.now().isoformat()
        RESTART_MARKER.write_text(json.dumps(merged, indent=2), encoding="utf-8")
    except Exception as e:
        trace(f"write_marker failed: {e}")


def find_daemon_pid() -> int | None:
    try:
        import psutil
    except ImportError:
        trace("psutil not available")
        return None
    for p in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            cl = " ".join(p.info["cmdline"] or [])
            if "clawd.py" in cl and "python" in (p.info["name"] or "").lower():
                return p.info["pid"]
        except Exception:
            pass
    return None


def terminate_daemon(pid: int, timeout: float = 10.0) -> tuple[bool, str]:
    try:
        import psutil
    except ImportError:
        return False, "psutil not available"
    try:
        proc = psutil.Process(pid)
    except psutil.NoSuchProcess:
        return True, "already gone"
    trace(f"terminating daemon pid={pid} (psutil.terminate)")
    try:
        proc.terminate()
    except Exception as e:
        return False, f"terminate() failed: {e}"
    try:
        proc.wait(timeout=timeout)
        return True, "exited cleanly within timeout"
    except psutil.TimeoutExpired:
        trace(f"daemon pid={pid} did not exit within {timeout}s; falling back to kill()")
        try:
            proc.kill()
            proc.wait(timeout=5.0)
            return True, "killed (TerminateProcess)"
        except Exception as e:
            return False, f"kill failed: {e}"
    except Exception as e:
        return False, f"wait failed: {e}"


def launch_new_daemon() -> tuple[int | None, str]:
    python_exe = sys.executable
    cmd = [python_exe, "clawd.py"]
    trace(f"launching new daemon: {cmd} cwd={CLAWD_DAEMON}")
    try:
        proc = subprocess.Popen(
            cmd,
            cwd=str(CLAWD_DAEMON),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
            close_fds=True,
        )
        return proc.pid, "spawned"
    except Exception as e:
        return None, f"spawn failed: {e}"


def verify_new_daemon_alive(pid: int, settle_seconds: float = 5.0) -> tuple[bool, str]:
    time.sleep(settle_seconds)
    try:
        import psutil
        proc = psutil.Process(pid)
        if proc.is_running() and proc.status() != psutil.STATUS_ZOMBIE:
            return True, f"alive (status={proc.status()})"
        return False, f"not running (status={proc.status() if proc.is_running() else 'gone'})"
    except Exception as e:
        return False, f"verify failed: {e}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reason", default="(no reason given)")
    parser.add_argument("--delay", type=int, default=10)
    parser.add_argument("--originating-pid", type=int, default=None,
                        help="PID of bridge.py subprocess that initiated; informational only")
    args = parser.parse_args()

    trace(f"respawn.py started — reason={args.reason!r} delay={args.delay}s")
    log_event({
        "action": "respawner_started",
        "reason": args.reason,
        "delay": args.delay,
        "originating_pid": args.originating_pid,
        "respawner_pid": os.getpid(),
    })
    write_marker({
        "respawner_pid": os.getpid(),
        "respawner_started_at": datetime.now().isoformat(),
        "reason": args.reason,
        "delay_seconds": args.delay,
        "phase": "waiting",
    })

    # Phase 1 — wait
    trace(f"sleeping {args.delay}s before terminating daemon")
    time.sleep(args.delay)

    # Phase 2 — find + terminate
    daemon_pid = find_daemon_pid()
    if daemon_pid is None:
        trace("no clawd.py daemon found — proceeding directly to launch")
        log_event({"action": "no_daemon_found_at_terminate"})
        write_marker({"phase": "no_daemon_found", "daemon_pid_pre_terminate": None})
    else:
        trace(f"found daemon at pid={daemon_pid}")
        write_marker({"phase": "terminating", "daemon_pid_pre_terminate": daemon_pid})
        ok, detail = terminate_daemon(daemon_pid, timeout=10.0)
        log_event({"action": "terminate_attempt", "pid": daemon_pid, "ok": ok, "detail": detail})
        if not ok:
            write_marker({"phase": "terminate_failed", "terminate_detail": detail})
            trace(f"FATAL: failed to terminate daemon: {detail}")
            # Continue anyway — maybe new daemon can coexist briefly
        else:
            write_marker({"phase": "terminated", "terminate_detail": detail})

    # Phase 3 — settle window
    time.sleep(1.5)

    # Phase 4 — launch new daemon
    new_pid, launch_detail = launch_new_daemon()
    log_event({"action": "launch_attempt", "new_pid": new_pid, "detail": launch_detail})
    if new_pid is None:
        write_marker({"phase": "launch_failed", "launch_detail": launch_detail})
        trace(f"FATAL: failed to launch new daemon: {launch_detail}")
        log_event({"action": "respawner_exit", "outcome": "launch_failed"})
        sys.exit(1)

    write_marker({"phase": "launched", "new_daemon_pid": new_pid, "launch_detail": launch_detail})

    # Phase 5 — verify alive
    alive, verify_detail = verify_new_daemon_alive(new_pid, settle_seconds=5.0)
    log_event({"action": "verify_alive", "new_pid": new_pid, "alive": alive, "detail": verify_detail})

    final_phase = "verified_alive" if alive else "verify_failed"
    write_marker({
        "phase": final_phase,
        "verify_detail": verify_detail,
        "respawner_finished_at": datetime.now().isoformat(),
    })

    log_event({"action": "respawner_exit", "outcome": final_phase, "new_pid": new_pid})
    trace(f"respawn complete — new_pid={new_pid} alive={alive}")
    sys.exit(0 if alive else 2)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        trace(f"FATAL exception: {e}\n{traceback.format_exc()}")
        log_event({"action": "respawner_crashed", "error": repr(e)})
        write_marker({"phase": "crashed", "error": repr(e)})
        sys.exit(1)
