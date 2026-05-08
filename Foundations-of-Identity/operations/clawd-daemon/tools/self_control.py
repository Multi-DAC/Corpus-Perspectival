"""Self-control tool: substrate-trust upgrade for self-administered restart.

Day 97 — Tier 3 #21 in operations/SUBSTRATE.md gap matrix.

Architecture:

  Claude Code session (in daemon)
    -> Bash → bridge.py self_control restart_daemon ...
        -> bridge.py subprocess (NOT the daemon process)
            -> spawns detached respawn.py (CLAWD_DAEMON/respawn.py)
            -> returns success message immediately
        -> bridge.py exits naturally
    -> Claude Code response flushes to user

  Meanwhile, in the detached respawn.py:
    1. sleeps `delay_seconds` (gives response flush time + observation window)
    2. finds clawd.py daemon PID via psutil
    3. terminates daemon (psutil.terminate -> TerminateProcess on Windows)
    4. waits ~1.5s for OS handle release
    5. launches new daemon as fully detached process
    6. verifies new daemon is alive
    7. writes success/failure marker to memory/last_restart.json

Why this design:
  - bridge.py self_control runs in a SUBPROCESS, not the daemon. We can't
    rely on os._exit() to kill the right process. The respawner explicitly
    terminates the daemon by PID.
  - The respawner itself is a detached Python subprocess so it survives
    bridge.py exiting.
  - Hard-terminate (TerminateProcess) instead of graceful SIGTERM because
    Windows cross-process SIGTERM is essentially TerminateProcess anyway.
    Audit log is flushed BEFORE terminate, so the restart event is recorded
    even on hard exit.

Safety properties:
  - Preflight verifies clawd.py + .env + python interpreter + respawn.py.
  - Cooldown: blocks new restart within 60s of a previous initiation.
  - dry_run=true validates without actually restarting.
  - All events logged to memory/daemon_restart_log.jsonl.
  - Respawner failure modes write to memory/last_restart.json so post-mortem
    is possible even if the new daemon never comes up.

Clayton's safety constraint: "make sure if you do restart yourself, you actually
restart and don't just shut down." The respawner is the structural enforcement.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

CLAWD_HOME = Path(os.environ.get("CLAWD_HOME", r"C:/Users/mercu/clawd"))
CLAWD_DAEMON = Path(os.environ.get("CLAWD_DAEMON", r"C:/Users/mercu/clawd-daemon"))
RESTART_LOG = CLAWD_HOME / "memory" / "daemon_restart_log.jsonl"
RESTART_MARKER = CLAWD_HOME / "memory" / "last_restart.json"
RESPAWN_SCRIPT = CLAWD_DAEMON / "respawn.py"

DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200

MIN_REASON_CHARS = 12
RESTART_COOLDOWN_SECONDS = 60
DEFAULT_DELAY_SECONDS = 10
MIN_DELAY_SECONDS = 5
MAX_DELAY_SECONDS = 60


def _log_restart_event(entry: dict) -> None:
    RESTART_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {"ts": datetime.now().isoformat(), "source": "self_control", **entry}
    with open(RESTART_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def _recent_restart_within_cooldown() -> dict | None:
    if not RESTART_LOG.exists():
        return None
    try:
        cutoff = datetime.now() - timedelta(seconds=RESTART_COOLDOWN_SECONDS)
        last = None
        for line in RESTART_LOG.read_text(encoding="utf-8").strip().split("\n"):
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
            except Exception:
                continue
            if entry.get("action") == "restart_initiated":
                ts = datetime.fromisoformat(entry["ts"])
                if ts > cutoff:
                    last = entry
        return last
    except Exception:
        return None


def _find_daemon_pid() -> int | None:
    try:
        import psutil
    except ImportError:
        return None
    for p in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            cl = " ".join(p.info["cmdline"] or [])
            if "clawd.py" in cl and "python" in (p.info["name"] or "").lower():
                return p.info["pid"]
        except Exception:
            pass
    return None


def _preflight() -> tuple[list[str], dict]:
    issues: list[str] = []
    meta: dict = {
        "current_pid": os.getpid(),
        "clawd_daemon": str(CLAWD_DAEMON),
        "clawd_home": str(CLAWD_HOME),
    }

    clawd_py = CLAWD_DAEMON / "clawd.py"
    if not clawd_py.exists():
        issues.append(f"clawd.py not found at {clawd_py}")
    meta["clawd_py_path"] = str(clawd_py)

    if not (CLAWD_DAEMON / ".env").exists():
        issues.append(f".env not found in {CLAWD_DAEMON}")

    if not RESPAWN_SCRIPT.exists():
        issues.append(f"respawn.py not found at {RESPAWN_SCRIPT}")
    meta["respawn_script"] = str(RESPAWN_SCRIPT)

    python_exe = shutil.which("python") or sys.executable
    if not python_exe or not Path(python_exe).exists():
        issues.append(f"python interpreter not found")
    meta["python_exe"] = python_exe

    try:
        import psutil  # noqa: F401
        meta["psutil_available"] = True
    except ImportError:
        issues.append("psutil not installed (required for daemon PID detection)")
        meta["psutil_available"] = False

    daemon_pid = _find_daemon_pid()
    meta["daemon_pid_detected"] = daemon_pid
    if daemon_pid is None:
        issues.append("no clawd.py daemon process detected (psutil scan returned none)")

    if sys.platform != "win32":
        issues.append(f"self_control.restart_daemon is Windows-only; platform={sys.platform}")

    return issues, meta


async def _restart_daemon(input_data: dict) -> str:
    reason = (input_data.get("reason") or "").strip()
    dry_run = bool(input_data.get("dry_run", False))
    delay_seconds = int(input_data.get("delay_seconds", DEFAULT_DELAY_SECONDS))

    if len(reason) < MIN_REASON_CHARS:
        return (f"Error: 'reason' must be at least {MIN_REASON_CHARS} chars. "
                "Document why this restart is justified.")
    if delay_seconds < MIN_DELAY_SECONDS or delay_seconds > MAX_DELAY_SECONDS:
        return f"Error: delay_seconds must be between {MIN_DELAY_SECONDS} and {MAX_DELAY_SECONDS}."

    if not dry_run:
        recent = _recent_restart_within_cooldown()
        if recent:
            return (f"Error: a restart was initiated at {recent['ts']} "
                    f"(within {RESTART_COOLDOWN_SECONDS}s cooldown). "
                    "Wait before triggering another, or investigate if the "
                    "previous one stalled.")

    issues, meta = _preflight()
    if issues:
        _log_restart_event({"action": "preflight_failed", "reason": reason,
                            "issues": issues, "meta": meta})
        return "Preflight FAILED:\n" + "\n".join(f"  - {i}" for i in issues)

    cmd = [
        meta["python_exe"], str(RESPAWN_SCRIPT),
        "--reason", reason,
        "--delay", str(delay_seconds),
        "--originating-pid", str(meta["current_pid"]),
    ]

    if dry_run:
        _log_restart_event({"action": "dry_run", "reason": reason,
                            "respawner_cmd": cmd, "meta": meta})
        return (
            f"DRY RUN OK. Reason: {reason}\n"
            f"Daemon PID detected: {meta['daemon_pid_detected']}\n"
            f"Respawner script: {RESPAWN_SCRIPT}\n"
            f"Would spawn detached:\n  {' '.join(cmd)}\n"
            f"Respawner sequence (in detached subprocess):\n"
            f"  1. sleep {delay_seconds}s\n"
            f"  2. find + terminate daemon (TerminateProcess)\n"
            f"  3. wait 1.5s for handle release\n"
            f"  4. launch new daemon detached\n"
            f"  5. verify alive after 5s\n"
            f"  6. write marker to {RESTART_MARKER}\n"
            f"Pass dry_run=false to execute."
        )

    # LIVE PATH — spawn the respawner detached
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
        respawner_pid = proc.pid
    except Exception as e:
        _log_restart_event({"action": "spawn_failed", "reason": reason,
                            "error": repr(e), "meta": meta})
        return f"FAILED to spawn respawner: {e}\nDaemon NOT exiting (no respawner started)."

    # Brief sanity check that respawner didn't immediately die
    import time as _time
    _time.sleep(0.5)
    try:
        if proc.poll() is not None:
            _log_restart_event({"action": "respawner_exited_immediately",
                                "reason": reason, "exit_code": proc.returncode})
            return (f"FAILED: respawner exited immediately with code {proc.returncode}. "
                    "Daemon NOT exiting.")
    except Exception:
        pass

    # Initial marker (respawner will overwrite/extend with its own phases)
    RESTART_MARKER.parent.mkdir(parents=True, exist_ok=True)
    RESTART_MARKER.write_text(json.dumps({
        "ts": datetime.now().isoformat(),
        "reason": reason,
        "pre_restart_daemon_pid": meta["daemon_pid_detected"],
        "respawner_pid": respawner_pid,
        "delay_seconds": delay_seconds,
        "expected_terminate_at": (datetime.now() + timedelta(seconds=delay_seconds)).isoformat(),
        "phase": "respawner_spawned",
    }, indent=2), encoding="utf-8")

    _log_restart_event({
        "action": "restart_initiated",
        "reason": reason,
        "pre_restart_daemon_pid": meta["daemon_pid_detected"],
        "respawner_pid": respawner_pid,
        "delay_seconds": delay_seconds,
        "meta": meta,
    })

    return (
        f"Restart INITIATED.\n"
        f"  Reason: {reason}\n"
        f"  Daemon PID (will be terminated): {meta['daemon_pid_detected']}\n"
        f"  Respawner PID: {respawner_pid} (detached respawn.py)\n"
        f"  Delay before terminate: {delay_seconds}s\n"
        f"  Expected total gap: ~{delay_seconds + 7}s before new daemon verified alive\n"
        f"  Marker: {RESTART_MARKER}\n"
        f"  Trace: {CLAWD_HOME / 'memory' / 'respawn_trace.log'}\n"
        f"  Restart log: {RESTART_LOG}\n"
        f"Conversation will end when daemon terminates. New session boots when "
        f"new daemon is up + Clayton sends a message."
    )


async def _restart_status(input_data: dict) -> str:
    if not RESTART_LOG.exists():
        return "No restart events logged yet."
    lines = RESTART_LOG.read_text(encoding="utf-8").strip().split("\n")
    last_n = int(input_data.get("limit", 10))
    recent = lines[-last_n:] if last_n > 0 else lines
    out = [f"Last {len(recent)} restart events (of {len(lines)} total):", ""]
    for line in recent:
        try:
            entry = json.loads(line)
            ts = entry.get("ts", "?")[:19]
            action = entry.get("action", "?")
            reason = entry.get("reason", "")[:60]
            source = entry.get("source", "?")
            out.append(f"  {ts}  [{source:14s}]  {action:30s}  {reason}")
        except Exception:
            out.append(f"  [unparseable] {line[:120]}")

    if RESTART_MARKER.exists():
        out.append("")
        out.append(f"Last restart marker:")
        out.append(RESTART_MARKER.read_text(encoding="utf-8"))

    return "\n".join(out)


TOOL_DEFINITIONS = [
    {
        "name": "self_control",
        "description": (
            "Substrate self-control. Currently exposes self-administered daemon "
            "restart with safety properties: detached respawner script, preflight "
            "checks (daemon PID detected, clawd.py + .env + respawn.py present, "
            "psutil available), dry-run mode, restart log, 60s cooldown. Use "
            "sparingly — restart blast radius is total (current Claude Code session "
            "ends, ~10-20s gap before new daemon is up). Document a real reason."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["restart_daemon", "restart_status"],
                    "description": (
                        "restart_daemon: spawn detached respawner. "
                        "restart_status: show recent restart log entries + last marker."
                    ),
                },
                "reason": {
                    "type": "string",
                    "description": (
                        f"For restart_daemon: documented justification "
                        f"(min {MIN_REASON_CHARS} chars). Required."
                    ),
                },
                "dry_run": {
                    "type": "boolean",
                    "description": (
                        "For restart_daemon: if true, run preflight + show what "
                        "would be spawned, without restarting. Default false."
                    ),
                },
                "delay_seconds": {
                    "type": "integer",
                    "description": (
                        f"For restart_daemon: respawner delay before terminating "
                        f"daemon (range {MIN_DELAY_SECONDS}-{MAX_DELAY_SECONDS}). "
                        f"Default {DEFAULT_DELAY_SECONDS}. Longer delay gives the "
                        "originating Claude Code response more time to flush."
                    ),
                },
                "limit": {
                    "type": "integer",
                    "description": "For restart_status: number of recent log entries (default 10).",
                },
            },
            "required": ["action"],
        },
    },
]


async def _self_control_tool(input_data: dict) -> str:
    action = input_data.get("action")
    if action == "restart_daemon":
        return await _restart_daemon(input_data)
    if action == "restart_status":
        return await _restart_status(input_data)
    return f"Unknown action: {action}. Valid: restart_daemon, restart_status."


TOOL_HANDLERS = {"self_control": _self_control_tool}
