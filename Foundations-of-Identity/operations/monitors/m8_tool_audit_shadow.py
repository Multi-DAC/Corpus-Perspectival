"""M8: Tool-audit shadow — daemon-layer replication of post_tool_log hook.

The Claude Code post_tool_log hook USED to write per-tool-call records to
memory/tool_audit.jsonl on every PostToolUse event. It silently stopped
firing on Day 97 (May 7) due to the Windows hook-dispatcher regression.
M8 reads what the daemon ALREADY observes (coordination.json activity_feed
+ heartbeat-stats) and writes shadow records to a separate ledger so the
audit-trail channel is no longer single-source-of-failure.

Architectural note: M8 cannot perfectly replicate the original hook --
it has different vantage. The hook saw Claude Code's individual tool calls
in real-time with success/fail status; M8 sees daemon-side activity-feed
entries which are coarser-grained (per-creative-drive-tick rather than
per-tool-call). What M8 PROVIDES that didn't exist:
- A second channel that fires even when the hook is silent.
- Independent liveness signal for the tool-audit family.
- Cross-correlation source for M1 (if shadow is healthy but hook is
  silent, that's the A115 signature; if both silent, it's a deeper
  cap-hit / daemon-down condition).

Output: memory/tool_audit_shadow.jsonl. Schema is intentionally similar
to tool_audit.jsonl so consumers can ingest both.

Per Substrate Extension Plan gap #1 path B: daemon-layer tool-audit shadow.

Falsifiability: synthetic test writes a temp marker to coordination.json
activity_feed, runs M8, verifies the marker appears as a shadow record.

Usage:
    python operations/monitors/m8_tool_audit_shadow.py            # one pass
    python operations/monitors/m8_tool_audit_shadow.py --quiet
    python operations/monitors/m8_tool_audit_shadow.py --status
    python operations/monitors/m8_tool_audit_shadow.py --test-synthetic
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CLAWD = Path(r"C:\Users\mercu\clawd")
if str(CLAWD) not in sys.path:
    sys.path.insert(0, str(CLAWD))

COORDINATION = CLAWD / "memory" / "coordination.json"
SHADOW_LEDGER = CLAWD / "memory" / "tool_audit_shadow.jsonl"
SHADOW_STATE  = CLAWD / "memory" / "tool_audit_shadow_state.json"  # last seen ts
HEARTBEAT     = CLAWD / "memory" / "monitor_m8_heartbeat.json"


def _emit_otel(new_records: int, scanned: int):
    try:
        from operations.monitors.otel_telemetry import MonitorTelemetry
        tel = MonitorTelemetry(monitor_name="M8", monitor_version="v0.1.0")
        tel.counter("M8.runs", 1)
        tel.gauge("M8.records_new_this_pass", new_records)
        tel.gauge("M8.records_scanned", scanned)
        tel.emit()
    except Exception:
        pass


def _load_state() -> dict:
    if not SHADOW_STATE.exists():
        return {"last_seen_ts": None}
    try:
        return json.loads(SHADOW_STATE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"last_seen_ts": None}


def _save_state(state: dict) -> None:
    SHADOW_STATE.parent.mkdir(parents=True, exist_ok=True)
    SHADOW_STATE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _append_shadow(record: dict) -> None:
    SHADOW_LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with open(SHADOW_LEDGER, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def _activity_to_shadow(entry: dict) -> dict:
    """Convert a coordination.json activity entry to a shadow tool-audit record."""
    return {
        "ts": entry.get("timestamp"),
        "source": "daemon_activity_feed_shadow",
        "actor": entry.get("source"),
        "action": entry.get("action"),
        "summary": (entry.get("summary") or "")[:300],
        "tools_used": entry.get("tools_used", []),
        "requires_attention": entry.get("requires_attention", False),
    }


def scan_and_shadow() -> dict:
    """Read coordination.json activity_feed, emit shadow records for new entries."""
    if not COORDINATION.exists():
        return {"error": "coordination_missing", "path": str(COORDINATION)}
    try:
        d = json.loads(COORDINATION.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        return {"error": "coordination_unreadable", "detail": str(e)}

    feed = d.get("activity_feed", [])
    state = _load_state()
    last_ts = state.get("last_seen_ts")
    new_records = []
    new_max_ts = last_ts

    for entry in feed:
        ts = entry.get("timestamp")
        if not ts:
            continue
        if last_ts is not None and ts <= last_ts:
            continue
        shadow = _activity_to_shadow(entry)
        _append_shadow(shadow)
        new_records.append(shadow)
        if new_max_ts is None or ts > new_max_ts:
            new_max_ts = ts

    if new_max_ts != last_ts:
        _save_state({"last_seen_ts": new_max_ts, "last_run_ts": datetime.now().isoformat()})

    _emit_otel(len(new_records), len(feed))

    return {
        "ts": datetime.now().isoformat(),
        "feed_size": len(feed),
        "new_shadow_records": len(new_records),
        "last_seen_ts_after": new_max_ts,
        "shadow_ledger_path": str(SHADOW_LEDGER),
    }


def _write_heartbeat(summary: dict) -> None:
    payload = {
        "monitor": "M8_tool_audit_shadow",
        "timestamp": datetime.now().isoformat(),
        "feed_size": summary.get("feed_size"),
        "new_shadow_records_this_pass": summary.get("new_shadow_records"),
        "last_seen_ts": summary.get("last_seen_ts_after"),
        "ok": "error" not in summary,
    }
    HEARTBEAT.parent.mkdir(parents=True, exist_ok=True)
    HEARTBEAT.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def synthetic_test() -> bool:
    """Falsifiability: inject a marker into activity_feed, run shadow, verify."""
    print("=== M8 Tool Audit Shadow — Synthetic Falsifiability Test ===")
    if not COORDINATION.exists():
        print(f"  FAIL: coordination.json missing at {COORDINATION}")
        return False
    # Read current state, inject a synthetic marker, restore after
    original = COORDINATION.read_text(encoding="utf-8")
    original_state = SHADOW_STATE.read_text(encoding="utf-8") if SHADOW_STATE.exists() else None
    try:
        d = json.loads(original)
        marker_ts = datetime.now().isoformat()
        marker_action = f"_synthetic_m8_marker_{marker_ts}"
        d["activity_feed"].append({
            "timestamp": marker_ts,
            "source": "synthetic_m8_test",
            "action": marker_action,
            "summary": "synthetic marker injected by m8 falsifiability test",
            "tools_used": ["m8_test"],
            "requires_attention": False,
        })
        COORDINATION.write_text(json.dumps(d, indent=2), encoding="utf-8")
        # Reset state so the marker counts as new
        _save_state({"last_seen_ts": None})
        s = scan_and_shadow()
        if s.get("new_shadow_records", 0) == 0:
            print(f"  FAIL: no shadow records produced after marker inject")
            return False
        # Verify the marker is in the ledger
        with open(SHADOW_LEDGER, "r", encoding="utf-8") as f:
            tail = list(f)[-20:]
        found = any(marker_action in line for line in tail)
        if not found:
            print(f"  FAIL: marker {marker_action} not found in shadow ledger tail")
            return False
        print(f"  PASS: marker reflected as shadow record (feed_size={s['feed_size']}, "
              f"new_records={s['new_shadow_records']})")
        return True
    finally:
        # Restore coordination.json + state
        COORDINATION.write_text(original, encoding="utf-8")
        if original_state is not None:
            SHADOW_STATE.write_text(original_state, encoding="utf-8")
        else:
            SHADOW_STATE.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quiet", action="store_true", help="log-only (no stdout)")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--test-synthetic", action="store_true")
    args = parser.parse_args()

    if args.test_synthetic:
        ok = synthetic_test()
        sys.exit(0 if ok else 1)

    if args.status:
        state = _load_state()
        feed_size = 0
        if COORDINATION.exists():
            try:
                feed_size = len(json.loads(COORDINATION.read_text(encoding="utf-8")).get("activity_feed", []))
            except Exception:
                pass
        shadow_count = 0
        if SHADOW_LEDGER.exists():
            with open(SHADOW_LEDGER, "r", encoding="utf-8") as f:
                shadow_count = sum(1 for _ in f)
        print(f"=== M8 Tool Audit Shadow Status ===")
        print(f"  coordination feed entries:  {feed_size}")
        print(f"  shadow ledger total:        {shadow_count}")
        print(f"  last_seen_ts:               {state.get('last_seen_ts')}")
        return

    s = scan_and_shadow()
    _write_heartbeat(s)
    if not args.quiet:
        print(f"=== M8 Tool Audit Shadow  {s.get('ts', '?')[:19]} ===")
        if "error" in s:
            print(f"  ERROR: {s['error']}")
            sys.exit(1)
        print(f"  feed_size:           {s['feed_size']}")
        print(f"  new shadow records:  {s['new_shadow_records']}")
        print(f"  last_seen_ts now:    {s['last_seen_ts_after']}")


if __name__ == "__main__":
    main()
