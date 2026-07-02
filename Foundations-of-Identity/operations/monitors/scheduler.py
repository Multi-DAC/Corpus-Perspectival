"""Monitor scheduler — runs M1/M2/M3/M4/M6 at appropriate cadences.

Single detached process that wakes periodically and runs whichever
monitors are due based on per-monitor cadence. Logs to
memory/monitor_scheduler_audit.jsonl. Heartbeat at
memory/monitor_scheduler_heartbeat.json so M6 family can watch it.

Cadences (configurable):
- M6 watchdog        : every 5 min   (frequent because it's monitor-of-monitor)
- M1 cross-channel   : every 10 min  (matches expected_max_interval for
                                      monitor_m1_heartbeat in carrier_registry)
- M3 state coherence : every 60 min  (drift is slow)
- M2 external integ. : every 60 min  (credential expiry rare)
- M4 storage integ.  : every 4 hours (storage corruption rare; expensive to check)

M5 PreCompact NOT scheduled here - it is activity-triggered via library
calls, not periodic.

T1.C / T1.D are library-only, no scheduling needed.

Usage:
    python operations/monitors/scheduler.py              # foreground (testing)
    python operations/monitors/scheduler.py --once       # one cycle then exit
    python operations/monitors/scheduler.py --status     # check if running
    python operations/monitors/scheduler.py --stop       # stop running scheduler

Launching as detached process (same pattern as launch_kg_extraction):
    python operations/monitors/scheduler_launcher.py
"""
import argparse
import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CLAWD = Path(r"C:\Users\mercu\clawd")
MONITORS_DIR = CLAWD / "operations" / "monitors"
SCHEDULER_HEARTBEAT = CLAWD / "memory" / "monitor_scheduler_heartbeat.json"
SCHEDULER_AUDIT = CLAWD / "memory" / "monitor_scheduler_audit.jsonl"
SCHEDULER_PID_FILE = CLAWD / "memory" / "monitor_scheduler.pid"

# Load the daemon's .env so spawned monitors inherit the secrets the escalation
# poller needs (TELEGRAM_BOT_TOKEN, TELEGRAM_AUTHORIZED_USERS). Without this the
# poller can't deliver even when scheduled — a root cause of the dead delivery path.
try:
    from dotenv import load_dotenv
    _DAEMON_ENV = Path(os.environ.get("CLAWD_DAEMON", r"C:\Users\mercu\clawd-daemon")) / ".env"
    if _DAEMON_ENV.exists():
        load_dotenv(_DAEMON_ENV)
except Exception:
    pass

# (monitor_name, cadence_seconds, script_filename, extra_args)
# extra_args overrides the default ["--quiet"] when present.
SCHEDULE = [
    ("M6_watchdog",        300,   "m6_watchdog.py",        None),
    ("M1_cross_channel",   600,   "m1_cross_channel.py",   None),
    ("M3_state_coherence", 3600,  "m3_state_coherence.py", None),
    ("M2_external_integ",  3600,  "m2_external_integration.py", None),
    ("M4_storage_integ",   14400, "m4_storage_integrity.py", None),
    ("M7_drift_mirror",    600,   "m7_drift_mirror.py",    None),
    ("M8_tool_audit_shadow", 600, "m8_tool_audit_shadow.py", None),
    # Revived delivery + repair (were dark: escalation poller dead since 2026-05-20,
    # self_healer never scheduled). Poller delivers queued criticals; self_healer
    # runs registry-declared heal commands for faulted healable channels.
    ("escalation_poll",    60,    "escalation_router.py",  ["poll", "--once"]),
    ("self_healer",        600,   "self_healer.py",        []),
    # Retrieval canary (rebuild): proves semantic recall RETURNS real hits — the
    # recall check nothing had (the 6-week vector death was invisible). Hourly.
    ("retrieval_canary",   3600,  "retrieval_canary.py",   None),
    # Process watchdog (rebuild): catches wedged/duplicate/runaway Clawd processes
    # (the two rebuild_index that pinned 24 cores for hours were invisible). Every 5 min.
    ("process_watchdog",   300,   "process_watchdog.py",   None),
    # Liveness-by-evidence (rebuild): verifies the sleep-time writers advanced a work
    # counter, not just touched a file — the exact blindness behind the 4-week freeze. Hourly.
    ("liveness_evidence",  3600,  "liveness_evidence.py",  None),
    # External watcher-of-watchers (rebuild): dead-man's switch — pings an off-box URL only
    # when verified-healthy, so box/daemon/monitor death makes the ping STOP and pages Clayton
    # externally. No-op until HEALTHCHECKS_URL is set in .env. Every 5 min.
    ("external_pinger",    300,   "external_pinger.py",    None),
    ("ledger_backup_daily", 86400, "ledger_backup.py",      ["run"]),
    ("monitor_self_test_weekly", 604800, "monitor_self_test.py", ["run"]),
    # Post-op B1/B2: tails every *_faults.jsonl and pages NEW fault lines via the
    # escalation queue (the M1-M8 mesh detected but never delivered); also flags
    # a stalled delivery queue. Every 10 min.
    ("fault_bridge",       600,   "fault_escalation_bridge.py", None),
]

# Post-op B4: a monitor failing EVERY cycle used to look like success for cadence
# purposes (last_run advanced regardless; failures only landed in an unread audit
# file). After this many consecutive non-ok results, page once.
FAILURE_ESCALATE_AFTER = 3

# Cycle period: scheduler loop wake-up interval. Should be <= shortest cadence.
CYCLE_PERIOD_SECONDS = 60


def _audit(record: dict) -> None:
    record["ts"] = datetime.now().isoformat()
    SCHEDULER_AUDIT.parent.mkdir(parents=True, exist_ok=True)
    with open(SCHEDULER_AUDIT, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def _write_heartbeat(state: dict) -> None:
    payload = {
        "scheduler": "monitor_scheduler",
        "timestamp": datetime.now().isoformat(),
        "pid": os.getpid(),
        "monitors_scheduled": [s[0] for s in SCHEDULE],
        "last_run_per_monitor": state.get("last_run", {}),
    }
    SCHEDULER_HEARTBEAT.parent.mkdir(parents=True, exist_ok=True)
    SCHEDULER_HEARTBEAT.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _run_monitor(script_name: str, extra_args=None) -> dict:
    """Invoke a monitor script. Default arg ['--quiet'] suits the M* monitors;
    extra_args overrides for scripts with a different CLI shape."""
    script = MONITORS_DIR / script_name
    if not script.exists():
        return {"script": script_name, "status": "missing"}
    args = extra_args if extra_args is not None else ["--quiet"]
    start = time.time()
    try:
        r = subprocess.run(
            [sys.executable, str(script)] + args,
            capture_output=True, text=True, timeout=120, cwd=str(CLAWD),
        )
        elapsed = time.time() - start
        return {
            "script": script_name,
            "status": "ok" if r.returncode == 0 else "exit_nonzero",
            "returncode": r.returncode,
            "elapsed_seconds": round(elapsed, 3),
            "stderr_excerpt": r.stderr[:200] if r.stderr else "",
        }
    except subprocess.TimeoutExpired:
        return {"script": script_name, "status": "timeout", "elapsed_seconds": time.time() - start}
    except Exception as e:
        return {"script": script_name, "status": "error", "error": str(e)}


_consecutive_failures: dict = {}


def _track_monitor_failure(name: str, result: dict) -> None:
    """B4: page after FAILURE_ESCALATE_AFTER consecutive non-ok results (once
    per failure streak — the counter escalates at the threshold, not repeatedly)."""
    status = result.get("status")
    # exit_nonzero means the monitor RAN and reported a finding (process_watchdog,
    # fault_bridge use rc=1 as a signal) — its own escalation handles that. Only
    # missing/timeout/error mean the monitor itself is broken.
    if status in ("ok", "exit_nonzero"):
        _consecutive_failures.pop(name, None)
        return
    count = _consecutive_failures.get(name, 0) + 1
    _consecutive_failures[name] = count
    if count == FAILURE_ESCALATE_AFTER:
        try:
            from escalation_router import enqueue_critical
            enqueue_critical(
                monitor="scheduler", tier="critical",
                summary=f"Monitor '{name}' failed {count} consecutive cycles "
                        f"(status={status}); it is effectively dead.",
                details={"monitor": name, "last_result": result},
            )
        except Exception:
            pass


def run_due_monitors(last_run: dict) -> dict:
    """Run any monitors whose cadence has elapsed. Returns updated last_run dict."""
    now = time.time()
    for entry in SCHEDULE:
        # Support both 3-tuple (legacy) and 4-tuple (with extra_args) shapes
        if len(entry) == 4:
            name, cadence, script, extra_args = entry
        else:
            name, cadence, script = entry
            extra_args = None
        last = last_run.get(name, 0)
        if now - last >= cadence:
            result = _run_monitor(script, extra_args=extra_args)
            _audit({"event": "monitor_run", "monitor": name, "result": result})
            _track_monitor_failure(name, result)
            last_run[name] = now
    return last_run


def run_forever():
    SCHEDULER_PID_FILE.write_text(str(os.getpid()), encoding="utf-8")
    _audit({"event": "scheduler_start", "pid": os.getpid()})
    state = {"last_run": {}}
    try:
        while True:
            state["last_run"] = run_due_monitors(state["last_run"])
            _write_heartbeat(state)
            time.sleep(CYCLE_PERIOD_SECONDS)
    except KeyboardInterrupt:
        _audit({"event": "scheduler_stop_keyboard"})
    finally:
        SCHEDULER_PID_FILE.unlink(missing_ok=True)


def run_once():
    state = {"last_run": {}}
    # First-time run forces all monitors (cadence elapsed since epoch)
    state["last_run"] = run_due_monitors(state["last_run"])
    _write_heartbeat(state)
    print(f"=== Monitor scheduler single-pass complete ===")
    print(f"  monitors run: {len(state['last_run'])}")
    for name in state["last_run"]:
        print(f"    {name}")


def status():
    print(f"=== Monitor Scheduler Status ===")
    if SCHEDULER_PID_FILE.exists():
        pid = int(SCHEDULER_PID_FILE.read_text().strip())
        print(f"  PID file present: {pid}")
        try:
            import psutil
            if psutil.pid_exists(pid):
                p = psutil.Process(pid)
                print(f"  Process: {p.status()} (created {time.strftime('%H:%M:%S', time.localtime(p.create_time()))})")
            else:
                print(f"  Process: DEAD (stale PID file)")
        except ImportError:
            print("  Process: cannot verify (psutil not available)")
    else:
        print("  PID file absent — scheduler not running")
    if SCHEDULER_HEARTBEAT.exists():
        hb = json.loads(SCHEDULER_HEARTBEAT.read_text())
        print(f"  Heartbeat ts: {hb.get('timestamp')}")
        print(f"  Monitors scheduled: {hb.get('monitors_scheduled')}")
        last_run = hb.get("last_run_per_monitor", {})
        if last_run:
            now = time.time()
            print(f"  Last-run intervals (minutes ago):")
            for name, ts in sorted(last_run.items()):
                if ts:
                    print(f"    {name:25} {(now - ts)/60:.1f}")


def stop():
    if not SCHEDULER_PID_FILE.exists():
        print("No PID file — scheduler not running")
        return
    pid = int(SCHEDULER_PID_FILE.read_text().strip())
    try:
        os.kill(pid, signal.SIGTERM)
        print(f"SIGTERM sent to PID {pid}")
    except ProcessLookupError:
        print(f"PID {pid} not found (stale file)")
    SCHEDULER_PID_FILE.unlink(missing_ok=True)
    _audit({"event": "scheduler_stop_cli", "pid": pid})


def _ensure_venv_interpreter() -> None:
    """Post-op C5: the whole monitor tree (incl. the GPU retrieval canary) runs
    under whatever interpreter launched this scheduler — historically the nssm
    service pointed at system Python (CPU-only torch = the recall death). If the
    daemon venv exists and we're NOT it, re-exec under it so the guarantee lives
    in code, not in out-of-repo service config."""
    daemon_dir = Path(os.environ.get("CLAWD_DAEMON") or r"C:\Users\mercu\clawd-daemon")
    venv_py = daemon_dir / ".venv" / "Scripts" / "python.exe"
    try:
        if venv_py.exists() and Path(sys.executable).resolve() != venv_py.resolve():
            print(f"scheduler: re-exec under venv interpreter {venv_py}")
            os.execv(str(venv_py), [str(venv_py)] + sys.argv)
    except OSError as e:
        print(f"scheduler: venv re-exec failed ({e}); continuing under {sys.executable}")


def main():
    _ensure_venv_interpreter()
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="run one cycle then exit")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--stop", action="store_true")
    args = parser.parse_args()

    if args.status:
        status()
    elif args.stop:
        stop()
    elif args.once:
        run_once()
    else:
        run_forever()


if __name__ == "__main__":
    main()
