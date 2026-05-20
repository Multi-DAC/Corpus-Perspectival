"""Self-healer — invoke documented healing commands for healable faults.

Reads operations/monitors/carrier_registry.json. For each channel marked
self_healing_applicable: true with self_healing_command set, checks if
the channel is currently in fault state; if so, runs the healing command
and audits the invocation.

Conservative: only invokes commands explicitly declared in the registry.
Never invokes arbitrary commands. Re-checks after healing to verify
recovery.

Used by monitor scheduler. Can also be invoked standalone.

Usage:
    python operations/monitors/self_healer.py             # one pass
    python operations/monitors/self_healer.py --dry-run   # log without invoking
    python operations/monitors/self_healer.py --status
"""
import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CLAWD = Path(r"C:\Users\mercu\clawd")
REGISTRY_PATH = CLAWD / "operations" / "monitors" / "carrier_registry.json"
AUDIT_PATH = CLAWD / "memory" / "self_healer_audit.jsonl"
STATE_PATH = CLAWD / "memory" / "self_healer_state.json"

# Rate-limit: at most one heal attempt per channel per N seconds
PER_CHANNEL_RATE_LIMIT_SECONDS = 600  # 10 min


def _audit(record: dict) -> None:
    record["ts"] = datetime.now().isoformat()
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def _load_state() -> dict:
    if not STATE_PATH.exists():
        return {"last_heal_per_channel": {}}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"last_heal_per_channel": {}}


def _save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def channel_in_fault_state(channel: dict) -> bool:
    """Check if the channel's actual file/path is in fault state per its expected interval."""
    if "path" not in channel:
        return False
    path = CLAWD / channel["path"]
    if not path.exists():
        return True  # missing = fault
    age = datetime.now().timestamp() - path.stat().st_mtime
    expected = channel.get("expected_max_interval_seconds", 999999999)
    return age > expected


def run_healing(channel: dict, dry_run: bool = False) -> dict:
    """Invoke the channel's declared healing command. Returns result dict."""
    cmd_str = channel.get("self_healing_command")
    if not cmd_str:
        return {"status": "no_command_declared"}

    if dry_run:
        return {"status": "dry_run", "command": cmd_str}

    # Split command into args. cmd_str is e.g. "python operations/scripts/kg_index_build.py"
    cmd = cmd_str.split()
    start = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=600, cwd=str(CLAWD))
        elapsed = time.time() - start
        return {
            "status": "ok" if r.returncode == 0 else "failed",
            "returncode": r.returncode,
            "elapsed_seconds": round(elapsed, 3),
            "stdout_excerpt": r.stdout[-400:] if r.stdout else "",
            "stderr_excerpt": r.stderr[-400:] if r.stderr else "",
        }
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "elapsed_seconds": time.time() - start}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def heal_pass(dry_run: bool = False) -> list:
    """One pass: check all healable channels, invoke healing for those in fault state.

    Returns list of {channel, in_fault, healed, result} dicts.
    """
    if not REGISTRY_PATH.exists():
        return [{"error": "registry missing", "path": str(REGISTRY_PATH)}]

    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    state = _load_state()
    now = time.time()
    out = []

    for channel in registry.get("channels", []):
        if not channel.get("self_healing_applicable"):
            continue
        if not channel.get("self_healing_command"):
            continue

        name = channel["name"]
        in_fault = channel_in_fault_state(channel)

        if not in_fault:
            out.append({"channel": name, "in_fault": False, "healed": False, "skip_reason": "channel_ok"})
            continue

        # Rate-limit check
        last_heal = state["last_heal_per_channel"].get(name, 0)
        if now - last_heal < PER_CHANNEL_RATE_LIMIT_SECONDS:
            elapsed_since = round(now - last_heal, 0)
            out.append({
                "channel": name, "in_fault": True, "healed": False,
                "skip_reason": f"rate_limited (last heal {elapsed_since}s ago, limit {PER_CHANNEL_RATE_LIMIT_SECONDS}s)",
            })
            continue

        # Invoke healing
        result = run_healing(channel, dry_run=dry_run)
        state["last_heal_per_channel"][name] = now

        # Re-check after healing (only if not dry-run)
        recovered = False
        if not dry_run and result.get("status") == "ok":
            recovered = not channel_in_fault_state(channel)

        _audit({
            "event": "heal_attempt",
            "channel": name,
            "dry_run": dry_run,
            "result": result,
            "recovered": recovered,
        })

        out.append({
            "channel": name,
            "in_fault": True,
            "healed": result.get("status") == "ok",
            "recovered_after_heal": recovered,
            "result": result,
        })

    _save_state(state)
    return out


def status():
    state = _load_state()
    print(f"=== Self-Healer Status ===")
    print(f"  Channels with healing history:")
    if not state["last_heal_per_channel"]:
        print(f"    (none yet)")
    else:
        now = time.time()
        for name, ts in sorted(state["last_heal_per_channel"].items()):
            elapsed = (now - ts) / 60
            print(f"    {name:30} last healed {elapsed:.1f} min ago")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()

    if args.status:
        status()
        return

    results = heal_pass(dry_run=args.dry_run)
    print(f"=== Self-Healer Pass {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    print(f"  Healable channels checked: {len(results)}")
    for r in results:
        if "error" in r:
            print(f"  ERROR: {r['error']}")
            continue
        if not r["in_fault"]:
            print(f"  ok    {r['channel']:30} (not in fault)")
        elif not r["healed"]:
            print(f"  skip  {r['channel']:30} ({r.get('skip_reason', '?')})")
        else:
            recovered = "RECOVERED" if r.get("recovered_after_heal") else "still in fault"
            print(f"  heal  {r['channel']:30} -> {recovered}")
            if r.get("result", {}).get("stdout_excerpt"):
                print(f"        stdout: {r['result']['stdout_excerpt'][-150:]}")


if __name__ == "__main__":
    main()
