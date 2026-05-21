"""M1: Cross-Channel Comparator.

Reads carrier_registry.json; for each channel, checks mtime against
expected_max_interval; emits structured fault report; writes own heartbeat
to memory/monitor_m1_heartbeat.json so M6 can watch it.

Per integrated implementation plan (palace/south/integrated-substrate-extension-
plan-2026-05-20.md) #2: foundation for everything else carrier-redundancy.

Falsifiability commitment: M1 must detect synthetic hook-silence within
2x expected-interval. Verified by --test-synthetic flag.

Usage:
    python operations/monitors/m1_cross_channel.py             # one check pass
    python operations/monitors/m1_cross_channel.py --json      # machine-readable
    python operations/monitors/m1_cross_channel.py --test-synthetic  # falsifiability test
    python operations/monitors/m1_cross_channel.py --quiet     # heartbeat-only, no stdout
"""
import argparse
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

# UTF-8 stdout on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CLAWD = Path(r"C:\Users\mercu\clawd")
REGISTRY_PATH = CLAWD / "operations" / "monitors" / "carrier_registry.json"
M1_HEARTBEAT_PATH = CLAWD / "memory" / "monitor_m1_heartbeat.json"
M1_FAULT_LOG_PATH = CLAWD / "memory" / "monitor_m1_faults.jsonl"


def resolve_path_template(template: str, now: datetime) -> Path:
    """Resolve {YYYY}/{MM}/{DD} in a path template."""
    s = template.format(YYYY=now.strftime("%Y"), MM=now.strftime("%m"), DD=now.strftime("%d"))
    return CLAWD / s


def channel_is_expected_active(channel: dict, now: datetime) -> bool:
    """Decide whether silence is fault-worthy for this channel right now."""
    when = channel.get("expected_active_when", "always")
    if when == "always":
        return True
    if when == "never":
        return False
    if when == "kg_extraction_in_flight":
        gate_path = CLAWD / channel.get("active_when_signal", "memory/kg_extraction_run.json")
        if not gate_path.exists():
            return False
        try:
            meta = json.loads(gate_path.read_text())
            pid = meta.get("pid")
            if pid is None:
                return False
            try:
                import psutil
                return psutil.pid_exists(int(pid)) and psutil.Process(int(pid)).is_running()
            except (ImportError, Exception):
                return True
        except (json.JSONDecodeError, OSError):
            return False
    if when == "claude_code_active":
        # Heuristic: if today's daily log has been touched in the last 30 min, Claude Code is active
        today_log = CLAWD / "memory" / now.strftime("%Y-%m-%d.md")
        if not today_log.exists():
            return False
        return (datetime.now().timestamp() - today_log.stat().st_mtime) < 1800
    if when == "monitor_m1_scheduled":
        return True
    return True


def check_channel(channel: dict, now: datetime) -> dict:
    """Returns one fault dict per channel (status may be 'ok', 'silent', 'inactive', or 'missing')."""
    name = channel["name"]
    path = (
        resolve_path_template(channel["path_template"], now)
        if "path_template" in channel
        else CLAWD / channel["path"]
    )

    is_active = channel_is_expected_active(channel, now)
    if not is_active:
        return {"channel": name, "status": "inactive", "path": str(path), "reason": "expected_active_when gate is false"}

    if not path.exists():
        return {
            "channel": name,
            "status": "missing",
            "path": str(path),
            "escalation_tier": channel["escalation_tier"],
        }

    mtime = path.stat().st_mtime
    age_s = datetime.now().timestamp() - mtime
    expected = channel["expected_max_interval_seconds"]

    if age_s <= expected:
        return {"channel": name, "status": "ok", "age_seconds": int(age_s), "expected_max_seconds": expected}

    # Silent fault
    return {
        "channel": name,
        "status": "silent",
        "path": str(path),
        "age_seconds": int(age_s),
        "expected_max_seconds": expected,
        "ratio": round(age_s / expected, 2),
        "escalation_tier": channel["escalation_tier"],
        "carries": channel.get("carries", []),
        "self_healing_applicable": channel.get("self_healing_applicable", False),
        "self_healing_command": channel.get("self_healing_command"),
    }


def cross_correlate(checks: list, registry: dict) -> list:
    """Cross-channel signatures beyond per-channel silence.

    The carrier-redundancy gain: discriminating selective channel death from
    global daemon death from inactive-by-design.
    """
    signatures = []

    by_name = {c["channel"]: c for c in checks}
    silent = [c for c in checks if c["status"] == "silent"]
    ok = [c for c in checks if c["status"] == "ok"]

    # Signature 1: selective channel death (some silent, some ok = substrate issue)
    if silent and ok:
        signatures.append({
            "signature": "selective_channel_death",
            "interpretation": "Some channels are firing while others are silent; substrate issue rather than global daemon death. A115-class signature when tool_audit is silent but daily-log heartbeat is fresh.",
            "silent_channels": [c["channel"] for c in silent],
            "ok_channels": [c["channel"] for c in ok],
            "escalation_tier": max((c.get("escalation_tier", "low") for c in silent), key=_tier_rank),
        })

    # Signature 2: global silence (all silent = daemon death likely)
    if silent and not ok:
        critical = [c for c in silent if c.get("escalation_tier") == "critical" or c["channel"] in ("daily_log_today", "monitor_m1_heartbeat")]
        if critical:
            signatures.append({
                "signature": "global_silence_with_critical",
                "interpretation": "Multiple critical channels silent simultaneously; daemon may be dead or system-wide failure.",
                "channels": [c["channel"] for c in silent],
                "escalation_tier": "critical",
            })

    return signatures


def _tier_rank(tier: str) -> int:
    return {"critical": 3, "high": 2, "medium": 1, "low": 0}.get(tier, 0)


def write_heartbeat(checks: list, signatures: list) -> None:
    """M1's own heartbeat, atomic write so M6 never reads partial data."""
    payload = {
        "monitor": "M1",
        "timestamp": datetime.now().isoformat(),
        "pid": os.getpid(),
        "channels_checked": len(checks),
        "channels_silent": sum(1 for c in checks if c["status"] == "silent"),
        "channels_ok": sum(1 for c in checks if c["status"] == "ok"),
        "channels_inactive": sum(1 for c in checks if c["status"] == "inactive"),
        "channels_missing": sum(1 for c in checks if c["status"] == "missing"),
        "cross_correlation_signatures": [s["signature"] for s in signatures],
    }
    # Atomic write: tmp file + rename
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=str(M1_HEARTBEAT_PATH.parent), delete=False) as tmp:
        json.dump(payload, tmp, indent=2)
        tmp_name = tmp.name
    shutil.move(tmp_name, M1_HEARTBEAT_PATH)


def append_faults(checks: list, signatures: list) -> None:
    """Append non-ok findings to the fault log for trend analysis."""
    record = {
        "timestamp": datetime.now().isoformat(),
        "faults": [c for c in checks if c["status"] in ("silent", "missing")],
        "signatures": signatures,
    }
    # Only write if there's actually anything to record
    if record["faults"] or record["signatures"]:
        with open(M1_FAULT_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")


def synthetic_silence_test() -> bool:
    """Falsifiability: temporarily set a channel's mtime to exactly 2x its
    expected-max-interval old, verify detection.

    Uses handoff_md (low escalation, manual-update kind, safe to touch).
    Sets mtime ABSOLUTE to (now - 2x expected) so the ratio is exactly 2.0,
    not (current_mtime - 2x) which would compound any existing staleness.
    """
    print("=== M1 Synthetic Silence Falsifiability Test ===")

    target_path = CLAWD / "memory" / "handoff.md"
    if not target_path.exists():
        print("  SKIP: handoff.md does not exist")
        return False

    registry = json.loads(REGISTRY_PATH.read_text())
    target_channel = next((c for c in registry["channels"] if c["name"] == "handoff_md"), None)
    if target_channel is None:
        print("  FAIL: handoff_md not in registry")
        return False
    expected = target_channel["expected_max_interval_seconds"]

    original_mtime = target_path.stat().st_mtime
    # Push mtime to be exactly 2.0x expected interval old (absolute, not relative)
    fake_mtime = datetime.now().timestamp() - (2.0 * expected)
    os.utime(target_path, (fake_mtime, fake_mtime))

    try:
        checks = [check_channel(c, datetime.now()) for c in registry["channels"]]
    finally:
        # Restore mtime IMMEDIATELY
        os.utime(target_path, (original_mtime, original_mtime))

    handoff_check = next((c for c in checks if c["channel"] == "handoff_md"), None)
    if handoff_check["status"] != "silent":
        print(f"  FAIL: handoff_md status was {handoff_check['status']}, not silent")
        return False

    ratio = handoff_check.get("ratio", 0)
    ok = ratio <= 2.05  # tiny tolerance for filesystem mtime precision
    verdict = "PASS" if ok else "FAIL"
    print(f"  {verdict}: synthetic silence detected at {ratio}x expected interval")
    print(f"  Falsifiability commitment: must detect within 2x. Actual: {ratio}x (tolerance 2.05).")
    return ok


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--quiet", action="store_true", help="heartbeat-only, no stdout")
    parser.add_argument("--test-synthetic", action="store_true", help="run falsifiability test")
    args = parser.parse_args()

    if args.test_synthetic:
        ok = synthetic_silence_test()
        sys.exit(0 if ok else 1)

    if not REGISTRY_PATH.exists():
        print(f"ERROR: registry not found at {REGISTRY_PATH}", file=sys.stderr)
        sys.exit(2)

    registry = json.loads(REGISTRY_PATH.read_text())
    now = datetime.now()

    # Pre-write own heartbeat with placeholder so the registry self-check finds it
    # (avoids monitor_m1_heartbeat showing MISSING on first run / first session).
    if not M1_HEARTBEAT_PATH.exists():
        M1_HEARTBEAT_PATH.write_text(json.dumps({
            "monitor": "M1", "timestamp": now.isoformat(), "pid": os.getpid(),
            "status": "initializing", "channels_checked": 0,
        }, indent=2))

    run_start = datetime.now()
    checks = [check_channel(c, now) for c in registry["channels"]]
    signatures = cross_correlate(checks, registry)
    run_elapsed = (datetime.now() - run_start).total_seconds()

    # Always write final heartbeat and faults
    write_heartbeat(checks, signatures)
    append_faults(checks, signatures)

    # T2.G: emit OTel metrics
    try:
        from operations.monitors.otel_telemetry import MonitorTelemetry
    except ImportError:
        sys.path.insert(0, str(CLAWD))
        from operations.monitors.otel_telemetry import MonitorTelemetry
    tel = MonitorTelemetry(monitor_name="M1", monitor_version="v0.1.0")
    tel.counter("runs", 1, description="number of M1 invocations")
    tel.gauge("channels_checked", len(checks), description="channels evaluated this run")
    tel.gauge("channels_ok", sum(1 for c in checks if c["status"] == "ok"))
    tel.gauge("channels_silent", sum(1 for c in checks if c["status"] == "silent"))
    tel.gauge("channels_inactive", sum(1 for c in checks if c["status"] == "inactive"))
    tel.gauge("channels_missing", sum(1 for c in checks if c["status"] == "missing"))
    tel.histogram("run_duration_seconds", run_elapsed, description="wall-clock duration of M1 check pass")
    for s in signatures:
        tel.counter("cross_correlation_signatures_fired", 1,
                    attributes={"signature": s["signature"],
                                "escalation_tier": s.get("escalation_tier", "unknown")})
    tel.emit()

    if args.quiet:
        return

    if args.json:
        print(json.dumps({"checks": checks, "signatures": signatures, "timestamp": now.isoformat()}, indent=2))
        return

    # Human-readable summary
    print(f"=== M1 Cross-Channel Check {now.strftime('%Y-%m-%d %H:%M:%S')} ===")
    for c in checks:
        if c["status"] == "ok":
            print(f"  OK       {c['channel']:30} (age {c['age_seconds']:>6}s, max {c['expected_max_seconds']}s)")
        elif c["status"] == "inactive":
            print(f"  inactive {c['channel']:30} ({c['reason']})")
        elif c["status"] == "missing":
            print(f"  MISSING  {c['channel']:30} [tier: {c.get('escalation_tier', '?')}]")
        elif c["status"] == "silent":
            print(f"  SILENT   {c['channel']:30} (age {c['age_seconds']:>6}s, {c.get('ratio', '?'):>4}x max) [tier: {c['escalation_tier']}]")

    if signatures:
        print()
        print(f"=== Cross-correlation signatures ===")
        for s in signatures:
            print(f"  [{s.get('escalation_tier', '?').upper()}] {s['signature']}")
            print(f"    {s['interpretation']}")


if __name__ == "__main__":
    main()
