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


# Heartbeat coverage assertions — the second half of "does it actually work". A
# falsifiability test can PASS (it detects a synthetic fault) while the monitor
# verifies nothing in production (the green-but-blind class M3 fell into: format
# drift → 0 claims extracted → clean OK). These read each monitor's REAL heartbeat
# and assert it shows evidence of work + isn't stale. (file, predicate(hb)->bool, why)
STALE_THRESHOLD_SECONDS = 26 * 3600  # these monitors run <=hourly; >26h = stopped running
COVERAGE_ASSERTIONS = [
    ("monitor_m3_heartbeat.json",
     lambda hb: bool(hb.get("coverage_ok")) and hb.get("evidence_checks", 0) > 0,
     "M3 must verify >=1 real claim (coverage_ok); a blind pass now self-FAULTs"),
    ("monitor_m1_heartbeat.json",
     lambda hb: hb.get("channels_checked", hb.get("channels", 0)) > 0,
     "M1 must compare >=1 channel"),
    ("monitor_retrieval_canary_heartbeat.json",
     lambda hb: hb.get("dim") == 1024 and hb.get("hits", 0) > 0,
     "retrieval canary must load the 1024-dim index and return hits"),
]


def _hb_age_seconds(hb: dict, path: Path) -> float:
    ts = hb.get("timestamp")
    if ts:
        try:
            return (datetime.now() - datetime.fromisoformat(ts)).total_seconds()
        except ValueError:
            pass
    return time.time() - path.stat().st_mtime


def coverage_audit() -> list:
    """Flag monitors that are heartbeating but no longer doing real work, or stale."""
    out = []
    mem = CLAWD / "memory"
    for fname, predicate, desc in COVERAGE_ASSERTIONS:
        path = mem / fname
        if not path.exists():
            out.append({"heartbeat": fname, "status": "MISSING",
                        "detail": f"no heartbeat — monitor not running ({desc})"})
            continue
        try:
            hb = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            out.append({"heartbeat": fname, "status": "UNREADABLE", "detail": str(e)})
            continue
        age = _hb_age_seconds(hb, path)
        if age > STALE_THRESHOLD_SECONDS:
            out.append({"heartbeat": fname, "status": "STALE",
                        "detail": f"last beat {age/3600:.1f}h ago (>{STALE_THRESHOLD_SECONDS/3600:.0f}h) — stopped running"})
            continue
        try:
            covered = bool(predicate(hb))
        except Exception as e:
            covered = False
            desc = f"{desc} (predicate error: {e})"
        out.append({"heartbeat": fname, "status": "COVERED" if covered else "BLIND",
                    "detail": None if covered else f"heartbeating but not verifying: {desc}"})
    return out


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

    coverage = coverage_audit()
    coverage_bad = [c for c in coverage if c["status"] != "COVERED"]

    summary = {
        "event": "self_test_run",
        "total": len(results),
        "passed": sum(1 for r in results if r["status"] == "PASS"),
        "failed": sum(1 for r in results if r["status"] == "FAIL"),
        "timeout": sum(1 for r in results if r["status"] == "TIMEOUT"),
        "error": sum(1 for r in results if r["status"] in ("ERROR", "script_missing")),
        "results": results,
        "coverage": coverage,
        "coverage_blind": len(coverage_bad),
    }
    _append_log(summary)

    # Escalate any regression: a failed falsifiability test (monitor is broken) OR a
    # coverage failure (monitor is alive but no longer verifying anything / stale).
    regressions = [r for r in results if r["status"] in ("FAIL", "TIMEOUT", "ERROR", "script_missing")]
    if regressions or coverage_bad:
        try:
            from operations.monitors.escalation_router import enqueue_critical
            parts = []
            if regressions:
                parts.append(f"{len(regressions)} falsifiability regressions")
            if coverage_bad:
                parts.append(f"{len(coverage_bad)} coverage failures (heartbeating but blind/stale)")
            enqueue_critical(
                monitor="monitor_self_test",
                tier="critical",
                summary="; ".join(parts),
                details={
                    "regressions": [r["monitor"] for r in regressions],
                    "coverage_failures": [{"hb": c["heartbeat"], "status": c["status"], "detail": c["detail"]} for c in coverage_bad],
                },
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
        print(f"=== Monitor Self-Test — {s['passed']}/{s['total']} falsifiability PASS ===")
        for r in s["results"]:
            marker = "OK " if r["status"] == "PASS" else "** "
            print(f"  {marker}{r['monitor']:25} {r['status']}")
            if r["status"] != "PASS":
                for line in r.get("stderr_tail", []):
                    print(f"        stderr: {line[:120]}")
        print(f"--- Coverage audit (heartbeating AND verifying?) ---")
        for c in s.get("coverage", []):
            marker = "OK " if c["status"] == "COVERED" else "** "
            print(f"  {marker}{c['heartbeat']:42} {c['status']}")
            if c["detail"]:
                print(f"        {c['detail'][:120]}")
        if s["failed"] or s["error"] or s["timeout"] or s.get("coverage_blind"):
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
