"""M6: Watchdog of M1 (monitor-of-monitor).

The bidirectional heartbeat foundation per integrated implementation plan #1.
Without M6, M1 itself is a single point of failure — if M1 dies, no one
notices its absence. M6 watches M1's heartbeat file and raises alarm
if M1 has stopped publishing.

M6 is intentionally tiny and dependency-free: it does ONE thing, so its
own failure surface is minimal. It is the trust-anchor of the monitor
chain; it must not need its own M7-watchdog.

Falsifiability commitment: M6 must detect monitor-death within 2x
heartbeat-interval. Verified by --test-synthetic flag (kills M1's heartbeat
file mtime and confirms detection).

Usage:
    python operations/monitors/m6_watchdog.py             # one check pass
    python operations/monitors/m6_watchdog.py --json
    python operations/monitors/m6_watchdog.py --test-synthetic
    python operations/monitors/m6_watchdog.py --quiet
"""
import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CLAWD = Path(r"C:\Users\mercu\clawd")
M1_HEARTBEAT_PATH = CLAWD / "memory" / "monitor_m1_heartbeat.json"
M6_HEARTBEAT_PATH = CLAWD / "memory" / "monitor_m6_heartbeat.json"
M6_FAULT_LOG_PATH = CLAWD / "memory" / "monitor_m6_faults.jsonl"

# M1's expected interval is 600s (10 min) per carrier_registry; M6 declares
# M1 dead if heartbeat is older than 2x that = 20 min. Aligned with M6
# falsifiability commitment.
M1_EXPECTED_INTERVAL_SECONDS = 600
M6_DETECTION_RATIO = 2.0  # falsifiability target: detect within 2x


def check_m1() -> dict:
    """Read M1's heartbeat; classify it as ok / silent / missing / corrupt."""
    now = datetime.now()
    if not M1_HEARTBEAT_PATH.exists():
        return {
            "status": "missing",
            "path": str(M1_HEARTBEAT_PATH),
            "interpretation": "M1 has never run, or its heartbeat file was deleted.",
            "escalation_tier": "critical",
        }

    try:
        payload = json.loads(M1_HEARTBEAT_PATH.read_text())
    except (json.JSONDecodeError, OSError) as e:
        return {
            "status": "corrupt",
            "path": str(M1_HEARTBEAT_PATH),
            "error": str(e),
            "escalation_tier": "critical",
        }

    file_mtime = M1_HEARTBEAT_PATH.stat().st_mtime
    age_s = now.timestamp() - file_mtime
    threshold = M1_EXPECTED_INTERVAL_SECONDS * M6_DETECTION_RATIO

    result = {
        "m1_pid": payload.get("pid"),
        "m1_last_timestamp": payload.get("timestamp"),
        "m1_channels_checked": payload.get("channels_checked"),
        "m1_channels_silent": payload.get("channels_silent"),
        "m1_signatures": payload.get("cross_correlation_signatures", []),
        "age_seconds": int(age_s),
        "threshold_seconds": int(threshold),
        "ratio": round(age_s / M1_EXPECTED_INTERVAL_SECONDS, 2),
    }

    if age_s <= M1_EXPECTED_INTERVAL_SECONDS:
        result["status"] = "ok"
    elif age_s <= threshold:
        result["status"] = "delayed"
        result["escalation_tier"] = "high"
        result["interpretation"] = "M1's last heartbeat is stale but within tolerance (less than 2x expected interval)."
    else:
        result["status"] = "silent"
        result["escalation_tier"] = "critical"
        result["interpretation"] = "M1 has stopped publishing heartbeats; M1 process may be dead."

    return result


def write_heartbeat(m1_status: dict) -> None:
    """M6's own heartbeat — kept minimal."""
    payload = {
        "monitor": "M6",
        "timestamp": datetime.now().isoformat(),
        "pid": os.getpid(),
        "m1_status": m1_status["status"],
        "m1_age_seconds": m1_status.get("age_seconds"),
    }
    M6_HEARTBEAT_PATH.write_text(json.dumps(payload, indent=2))


def append_faults(m1_status: dict) -> None:
    """Append non-ok findings."""
    if m1_status["status"] in ("ok",):
        return
    record = {
        "timestamp": datetime.now().isoformat(),
        "m1_status": m1_status,
    }
    with open(M6_FAULT_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def synthetic_silence_test() -> bool:
    """Verify M6 detects synthetic M1-death within 2x heartbeat-interval.

    Test: push M1's heartbeat-file mtime back beyond 2x interval, run M6
    check, verify status == silent. Restore mtime immediately.
    """
    print("=== M6 Synthetic Silence Falsifiability Test ===")

    if not M1_HEARTBEAT_PATH.exists():
        print("  PRE-SETUP: M1 heartbeat does not exist; running M1 once to create it...")
        import subprocess
        result = subprocess.run(
            [sys.executable, str(CLAWD / "operations" / "monitors" / "m1_cross_channel.py"), "--quiet"],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            print(f"  FAIL: could not create M1 heartbeat: {result.stderr}")
            return False

    original_mtime = M1_HEARTBEAT_PATH.stat().st_mtime
    threshold = M1_EXPECTED_INTERVAL_SECONDS * M6_DETECTION_RATIO

    # Push mtime back 3x threshold (well past detection point)
    fake_mtime = original_mtime - 3 * threshold
    os.utime(M1_HEARTBEAT_PATH, (fake_mtime, fake_mtime))

    try:
        result = check_m1()
    finally:
        os.utime(M1_HEARTBEAT_PATH, (original_mtime, original_mtime))

    if result["status"] == "silent":
        print(f"  PASS: detected M1 silence (age {result['age_seconds']}s vs threshold {result['threshold_seconds']}s = {result['ratio']}x interval)")
        return True
    else:
        print(f"  FAIL: M6 status was {result['status']}, not silent. age={result.get('age_seconds')}s threshold={result.get('threshold_seconds')}s")
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--test-synthetic", action="store_true")
    args = parser.parse_args()

    if args.test_synthetic:
        ok = synthetic_silence_test()
        sys.exit(0 if ok else 1)

    run_start = datetime.now()
    result = check_m1()
    write_heartbeat(result)
    append_faults(result)
    run_elapsed = (datetime.now() - run_start).total_seconds()

    # T2.G: emit OTel metrics
    try:
        from operations.monitors.otel_telemetry import MonitorTelemetry
    except ImportError:
        sys.path.insert(0, str(CLAWD))
        from operations.monitors.otel_telemetry import MonitorTelemetry
    tel = MonitorTelemetry(monitor_name="M6", monitor_version="v0.1.0")
    tel.counter("runs", 1, description="number of M6 invocations")
    tel.gauge("m1_age_seconds", result.get("age_seconds", -1),
              description="age of M1 heartbeat at M6 check time",
              attributes={"m1_status": result.get("status", "unknown")})
    if "ratio" in result:
        tel.gauge("m1_age_ratio", result["ratio"],
                  description="ratio of M1 age to expected interval")
    tel.counter("m1_status_observations", 1,
                attributes={"m1_status": result.get("status", "unknown")},
                description="count of M1 status observations by status type")
    tel.histogram("run_duration_seconds", run_elapsed,
                  description="wall-clock duration of M6 check pass")
    tel.emit()

    if args.quiet:
        return

    if args.json:
        print(json.dumps(result, indent=2))
        return

    print(f"=== M6 Watchdog Check {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    status = result["status"]
    print(f"  M1 status: {status.upper()}")
    if status == "ok":
        print(f"  M1 last heartbeat: {result.get('m1_last_timestamp')} (age {result['age_seconds']}s, within {M1_EXPECTED_INTERVAL_SECONDS}s)")
        print(f"  M1 PID: {result.get('m1_pid')}")
        print(f"  M1 channels checked: {result.get('m1_channels_checked')} (silent: {result.get('m1_channels_silent')})")
        if result.get("m1_signatures"):
            print(f"  M1 cross-correlation signatures: {result['m1_signatures']}")
    elif status == "delayed":
        print(f"  [HIGH] {result['interpretation']}")
        print(f"  age={result['age_seconds']}s, ratio={result['ratio']}x interval")
    elif status == "silent":
        print(f"  [CRITICAL] {result['interpretation']}")
        print(f"  age={result['age_seconds']}s, threshold={result['threshold_seconds']}s, ratio={result['ratio']}x interval")
    elif status == "missing":
        print(f"  [CRITICAL] {result['interpretation']}")
    elif status == "corrupt":
        print(f"  [CRITICAL] Heartbeat file corrupted: {result.get('error')}")


if __name__ == "__main__":
    main()
