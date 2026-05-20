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

# (monitor_name, cadence_seconds, script_filename)
SCHEDULE = [
    ("M6_watchdog",        300,   "m6_watchdog.py"),
    ("M1_cross_channel",   600,   "m1_cross_channel.py"),
    ("M3_state_coherence", 3600,  "m3_state_coherence.py"),
    ("M2_external_integ",  3600,  "m2_external_integration.py"),
    ("M4_storage_integ",   14400, "m4_storage_integrity.py"),
]

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


def _run_monitor(script_name: str) -> dict:
    """Invoke a monitor script with --quiet (heartbeat-only mode)."""
    script = MONITORS_DIR / script_name
    if not script.exists():
        return {"script": script_name, "status": "missing"}
    start = time.time()
    try:
        r = subprocess.run(
            [sys.executable, str(script), "--quiet"],
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


def run_due_monitors(last_run: dict) -> dict:
    """Run any monitors whose cadence has elapsed. Returns updated last_run dict."""
    now = time.time()
    for name, cadence, script in SCHEDULE:
        last = last_run.get(name, 0)
        if now - last >= cadence:
            result = _run_monitor(script)
            _audit({"event": "monitor_run", "monitor": name, "result": result})
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


def main():
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
