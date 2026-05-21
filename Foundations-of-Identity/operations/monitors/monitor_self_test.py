"""Monitor self-test — run each monitor's falsifiability/synthetic test.

Per Substrate Extension gap #7: monitors have synthetic_test() functions
to prove they work, but nothing runs them on a cadence. A regression in
M3 or M6 could silently degrade for weeks before noticed. This runs all
of them weekly (scheduler-invoked) and escalates on regression.

Each monitor's test invocation is registered explicitly (not auto-discovered)
because they evolved with different CLI shapes.

Falsifiability commitment: a deliberately broken monitor (subprocess exits
nonzero) must produce a 'regression' record and escalate within one run.

Usage:
    python operations/monitors/monitor_self_test.py run     # run all + write log
    python operations/monitors/monitor_self_test.py status  # show last run summary
    python operations/monitors/monitor_self_test.py test    # synthetic falsifiability test
"""
import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CLAWD = Path(r"C:\Users\mercu\clawd")
if str(CLAWD) not in sys.path:
    sys.path.insert(0, str(CLAWD))

MONITORS_DIR = CLAWD / "operations" / "monitors"
REGRESSION_LOG = CLAWD / "memory" / "monitor_regression.jsonl"

# (monitor_name, script_filename, test_args)
TEST_INVOCATIONS = [
    ("M1_cross_channel",     "m1_cross_channel.py",          ["--test-synthetic"]),
    ("M2_external_integ",    "m2_external_integration.py",   ["--test-synthetic"]),
    ("M3_state_coherence",   "m3_state_coherence.py",        ["--test-known-instances"]),
    ("M4_storage_integ",     "m4_storage_integrity.py",      ["--test-synthetic"]),
    ("M5_precompact_subst",  "m5_precompact_substitute.py",  ["--test-synthetic"]),
    ("M6_watchdog",          "m6_watchdog.py",               ["--test-synthetic"]),
    ("M7_drift_mirror",      "m7_drift_mirror.py",           ["--test-synthetic"]),
    ("M8_tool_audit_shadow", "m8_tool_audit_shadow.py",      ["--test-synthetic"]),
    ("T1C_circuit_breaker",  "t1c_circuit_breaker.py",       ["--test-synthetic"]),
    ("T1D_self_prediction",  "t1d_self_prediction.py",       ["--test-known-case"]),
    ("T2H_utility_replay",   "utility_replay.py",            ["test"]),
    ("ledger_backup",        "ledger_backup.py",             ["test"]),
]


def _append_log(record: dict) -> None:
    record["ts"] = datetime.now().isoformat()
    REGRESSION_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(REGRESSION_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def _run_one(name: str, script: str, args: list) -> dict:
    script_path = MONITORS_DIR / script
    if not script_path.exists():
        return {"monitor": name, "status": "script_missing", "script": script}
    start = time.time()
    try:
        r = subprocess.run(
            [sys.executable, str(script_path)] + args,
            capture_output=True, text=True, timeout=120, cwd=str(CLAWD),
        )
        elapsed = round(time.time() - start, 3)
        passed = (r.returncode == 0)
        out_tail = (r.stdout or "").strip().splitlines()
        err_tail = (r.stderr or "").strip().splitlines()
        return {
            "monitor": name,
            "status": "PASS" if passed else "FAIL",
            "returncode": r.returncode,
            "elapsed_seconds": elapsed,
            "stdout_tail": out_tail[-3:],
            "stderr_tail": err_tail[-3:],
        }
    except subprocess.TimeoutExpired:
        return {"monitor": name, "status": "TIMEOUT", "elapsed_seconds": time.time() - start}
    except Exception as e:
        return {"monitor": name, "status": "ERROR", "error": str(e)}


def run_all() -> dict:
    results = []
    for name, script, args in TEST_INVOCATIONS:
        results.append(_run_one(name, script, args))

    summary = {
        "event": "self_test_run",
        "total": len(results),
        "passed": sum(1 for r in results if r["status"] == "PASS"),
        "failed": sum(1 for r in results if r["status"] == "FAIL"),
        "timeout": sum(1 for r in results if r["status"] == "TIMEOUT"),
        "error": sum(1 for r in results if r["status"] in ("ERROR", "script_missing")),
        "results": results,
    }
    _append_log(summary)

    # Escalate any regression (FAIL/TIMEOUT) as critical fault
    regressions = [r for r in results if r["status"] in ("FAIL", "TIMEOUT", "ERROR", "script_missing")]
    if regressions:
        try:
            from operations.monitors.escalation_router import enqueue_critical
            enqueue_critical(
                monitor="monitor_self_test",
                tier="critical",
                summary=f"{len(regressions)} monitor falsifiability tests regressed",
                details={"regressions": [r["monitor"] for r in regressions]},
            )
        except Exception:
            pass

    return summary


def status() -> dict:
    if not REGRESSION_LOG.exists():
        return {"runs": 0, "latest": None}
    runs = []
    with open(REGRESSION_LOG, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                runs.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    if not runs:
        return {"runs": 0, "latest": None}
    latest = runs[-1]
    return {
        "runs": len(runs),
        "latest_ts": latest.get("ts"),
        "latest_passed": latest.get("passed"),
        "latest_failed": latest.get("failed"),
        "latest_total": latest.get("total"),
    }


def synthetic_test() -> bool:
    """Falsifiability: invoke a known-bad command and verify it surfaces as FAIL."""
    print("=== Monitor Self-Test — Synthetic Falsifiability Test ===")
    fake = _run_one("synthetic_bad", "definitely_not_a_real_script.py", ["--test-synthetic"])
    if fake["status"] != "script_missing":
        print(f"  FAIL: expected status=script_missing, got {fake['status']}")
        return False
    print(f"  PASS: missing-script correctly surfaced as {fake['status']}")

    # Run real-monitor test (m6 is fast)
    real = _run_one("M6_watchdog", "m6_watchdog.py", ["--test-synthetic"])
    if real["status"] != "PASS":
        print(f"  FAIL: real M6 test returned {real['status']}; expected PASS")
        return False
    print(f"  PASS: real M6 test PASS ({real['elapsed_seconds']}s)")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["run", "status", "test"])
    args = parser.parse_args()

    if args.command == "run":
        s = run_all()
        print(f"=== Monitor Self-Test — {s['passed']}/{s['total']} PASS ===")
        for r in s["results"]:
            marker = "OK " if r["status"] == "PASS" else "** "
            print(f"  {marker}{r['monitor']:25} {r['status']}")
            if r["status"] != "PASS":
                for line in r.get("stderr_tail", []):
                    print(f"        stderr: {line[:120]}")
        if s["failed"] or s["error"] or s["timeout"]:
            sys.exit(1)
    elif args.command == "status":
        s = status()
        print(f"=== Monitor Self-Test Status ===")
        print(f"  runs:        {s['runs']}")
        if s["latest_ts"]:
            print(f"  latest:      {s['latest_ts'][:19]}")
            print(f"  pass/total:  {s['latest_passed']}/{s['latest_total']}")
            if s["latest_failed"]:
                print(f"  *** failed:  {s['latest_failed']} ***")
    elif args.command == "test":
        ok = synthetic_test()
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
