"""T1.C: Circuit Breaker — rate-limit guard for runaway-loop prevention.

Library-style importable guard. Heavyweight operations call check_rate()
before proceeding; if recent call-rate exceeds threshold, raises
CircuitBreakerTripped. State persists across process restarts via
memory/circuit_breaker_state.json. All guard invocations append to
memory/circuit_breaker_audit.jsonl for forensic review.

Integrated implementation plan #5. Foundation: M6 + M1 (this trips a
named circuit; M1 surfaces it as a fault; M6 ensures the monitoring
process publishing alerts is itself alive).

Falsifiability commitment: synthetic 1000-rapid-call test must trigger
within 30s of crossing threshold. Verified by --test-synthetic flag.

Usage as library:
    from operations.monitors.t1c_circuit_breaker import check_rate, CircuitBreakerTripped
    try:
        check_rate("kg_extraction_spawn", max_per_minute=10)
        # ... do the heavy thing
    except CircuitBreakerTripped as e:
        # halt; surface to M1; do NOT bypass
        ...

Usage as CLI:
    python operations/monitors/t1c_circuit_breaker.py status
    python operations/monitors/t1c_circuit_breaker.py reset <breaker_name>
    python operations/monitors/t1c_circuit_breaker.py --test-synthetic
"""
import argparse
import json
import os
import sys
import time
from collections import deque
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CLAWD = Path(r"C:\Users\mercu\clawd")
STATE_PATH = CLAWD / "memory" / "circuit_breaker_state.json"
AUDIT_PATH = CLAWD / "memory" / "circuit_breaker_audit.jsonl"


class CircuitBreakerTripped(Exception):
    """Raised when a named circuit's call-rate exceeds its threshold."""
    def __init__(self, breaker_name: str, recent_count: int, max_count: int, window_seconds: int):
        self.breaker_name = breaker_name
        self.recent_count = recent_count
        self.max_count = max_count
        self.window_seconds = window_seconds
        super().__init__(
            f"Circuit breaker '{breaker_name}' tripped: {recent_count} calls in "
            f"{window_seconds}s exceeds max {max_count}. Operation BLOCKED. "
            f"Reset via: python operations/monitors/t1c_circuit_breaker.py reset {breaker_name}"
        )


def _load_state() -> dict:
    if not STATE_PATH.exists():
        return {"breakers": {}, "tripped": {}}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"breakers": {}, "tripped": {}}


def _save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _append_audit(record: dict) -> None:
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    record["ts"] = datetime.now().isoformat()
    with open(AUDIT_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def check_rate(breaker_name: str, max_per_window: int = 10, window_seconds: int = 60) -> None:
    """Check whether this call would exceed the rate threshold for the named breaker.

    Raises CircuitBreakerTripped if (a) the breaker is currently tripped, or
    (b) this call would push the rolling window count over the threshold.

    Otherwise records the call and returns normally.

    State persists across process restarts via STATE_PATH.
    """
    state = _load_state()
    now = time.time()

    # Hard-tripped check
    if breaker_name in state.get("tripped", {}):
        trip_info = state["tripped"][breaker_name]
        _append_audit({
            "event": "blocked_hard_trip",
            "breaker": breaker_name,
            "trip_info": trip_info,
        })
        raise CircuitBreakerTripped(
            breaker_name,
            trip_info.get("recent_count", -1),
            max_per_window,
            window_seconds,
        )

    # Rolling-window check
    breaker = state.setdefault("breakers", {}).setdefault(breaker_name, {"calls": [], "max_per_window": max_per_window, "window_seconds": window_seconds})
    window_start = now - window_seconds
    # Filter to recent calls only
    breaker["calls"] = [t for t in breaker["calls"] if t > window_start]
    breaker["max_per_window"] = max_per_window  # may have been changed by caller
    breaker["window_seconds"] = window_seconds

    if len(breaker["calls"]) >= max_per_window:
        # Trip the breaker
        state.setdefault("tripped", {})[breaker_name] = {
            "tripped_at": datetime.now().isoformat(),
            "recent_count": len(breaker["calls"]),
            "max_per_window": max_per_window,
            "window_seconds": window_seconds,
        }
        _save_state(state)
        _append_audit({
            "event": "trip",
            "breaker": breaker_name,
            "recent_count": len(breaker["calls"]),
            "max_per_window": max_per_window,
            "window_seconds": window_seconds,
        })
        raise CircuitBreakerTripped(
            breaker_name,
            len(breaker["calls"]),
            max_per_window,
            window_seconds,
        )

    # Permit this call; record it
    breaker["calls"].append(now)
    _save_state(state)
    _append_audit({
        "event": "permit",
        "breaker": breaker_name,
        "current_count": len(breaker["calls"]),
        "max_per_window": max_per_window,
        "window_seconds": window_seconds,
    })


def reset(breaker_name: str) -> bool:
    """Manually reset a tripped breaker (or do nothing if not tripped). Returns True if a reset happened."""
    state = _load_state()
    changed = False
    if breaker_name in state.get("tripped", {}):
        del state["tripped"][breaker_name]
        changed = True
    if breaker_name in state.get("breakers", {}):
        state["breakers"][breaker_name]["calls"] = []
        changed = True
    if changed:
        _save_state(state)
        _append_audit({"event": "reset", "breaker": breaker_name})
    return changed


def status() -> dict:
    state = _load_state()
    out = {"timestamp": datetime.now().isoformat(), "breakers": {}, "tripped": list(state.get("tripped", {}).keys())}
    now = time.time()
    for name, b in state.get("breakers", {}).items():
        window_start = now - b["window_seconds"]
        recent = [t for t in b["calls"] if t > window_start]
        out["breakers"][name] = {
            "current_count": len(recent),
            "max_per_window": b["max_per_window"],
            "window_seconds": b["window_seconds"],
            "is_tripped": name in state.get("tripped", {}),
        }
    return out


def synthetic_test() -> bool:
    """Falsifiability: 1000 rapid calls must trip within 30s."""
    print("=== T1.C Circuit Breaker Falsifiability Test ===")
    test_breaker = "_falsifiability_test"

    # Clean state first
    reset(test_breaker)

    start = time.time()
    tripped_at_call = None
    for i in range(1000):
        try:
            check_rate(test_breaker, max_per_window=50, window_seconds=10)
        except CircuitBreakerTripped as e:
            tripped_at_call = i
            elapsed = time.time() - start
            print(f"  Tripped at call {i} after {elapsed:.3f}s")
            print(f"  Trip message: {e}")
            break

    elapsed = time.time() - start
    reset(test_breaker)  # cleanup

    if tripped_at_call is None:
        print(f"  FAIL: 1000 calls completed without trip in {elapsed:.3f}s")
        return False

    if elapsed > 30:
        print(f"  FAIL: trip took {elapsed:.3f}s, exceeds 30s commitment")
        return False

    print(f"  PASS: trip detected at call {tripped_at_call} in {elapsed:.3f}s (commitment: within 30s)")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?", default="status", choices=["status", "reset", "--test-synthetic"])
    parser.add_argument("args", nargs="*")
    parser.add_argument("--test-synthetic", action="store_true")
    ns = parser.parse_args()

    if ns.test_synthetic or ns.command == "--test-synthetic":
        ok = synthetic_test()
        sys.exit(0 if ok else 1)

    if ns.command == "status":
        s = status()
        print(f"=== T1.C Circuit Breaker Status {s['timestamp']} ===")
        if not s["breakers"]:
            print("  No breakers registered.")
        for name, info in s["breakers"].items():
            badge = " [TRIPPED]" if info["is_tripped"] else ""
            print(f"  {name}{badge}: {info['current_count']}/{info['max_per_window']} in {info['window_seconds']}s window")
        if s["tripped"]:
            print(f"\n  Tripped breakers: {s['tripped']}")

    elif ns.command == "reset":
        if not ns.args:
            print("usage: reset <breaker_name>")
            return
        changed = reset(ns.args[0])
        print(f"reset {ns.args[0]}: {'changed' if changed else 'no-op (not tripped)'}")


if __name__ == "__main__":
    main()
