"""M5: PreCompact Partial-Substitute.

Heuristic-based state snapshotting before context compaction. Since we
cannot observe compaction directly (Claude Code internal), we approximate
via three triggers: time-since-last-snapshot, activity-since-last-snapshot,
and explicit-trigger. ANY trigger fires the snapshot.

Integrated implementation plan #9. Separate workstream from carrier-
redundancy monitors but uses the same heartbeat/audit patterns.

Snapshot contents: handoff.md + CURRENT.md + ATRIUM.md state + current
git HEADs across all known repos + monitor heartbeat states. Saved to
memory/precompact_snapshots/<timestamp>/ as one snapshot per fire.

Falsifiability commitment: triggers must fire within 90% of explicitly-
declared compact-imminent events in test scenarios. Substitute test:
synthetic trigger conditions known to fire, verify snapshot is created.

Usage as library:
    from operations.monitors.m5_precompact_substitute import maybe_snapshot, force_snapshot
    maybe_snapshot()  # checks triggers; snapshots if any fires

Usage as CLI:
    python operations/monitors/m5_precompact_substitute.py status
    python operations/monitors/m5_precompact_substitute.py force
    python operations/monitors/m5_precompact_substitute.py --test-synthetic
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CLAWD = Path(r"C:\Users\mercu\clawd")
SNAPSHOT_ROOT = CLAWD / "memory" / "precompact_snapshots"
STATE_PATH = CLAWD / "memory" / "monitor_m5_state.json"
M5_HEARTBEAT_PATH = CLAWD / "memory" / "monitor_m5_heartbeat.json"
M5_AUDIT_PATH = CLAWD / "memory" / "monitor_m5_audit.jsonl"

# Defaults; tunable per call
DEFAULT_TIME_THRESHOLD_MINUTES = 90
DEFAULT_ACTIVITY_THRESHOLD = 50  # tool-call-equivalents since last snapshot

FILES_TO_SNAPSHOT = [
    CLAWD / "memory" / "handoff.md",
    CLAWD / "CURRENT.md",
    CLAWD / "palace" / "ATRIUM.md",
]


def _load_state() -> dict:
    if not STATE_PATH.exists():
        return {"last_snapshot_ts": None, "activity_since_snapshot": 0, "total_snapshots": 0}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"last_snapshot_ts": None, "activity_since_snapshot": 0, "total_snapshots": 0}


def _save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _audit(record: dict) -> None:
    record["ts"] = datetime.now().isoformat()
    M5_AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(M5_AUDIT_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def _git_head(cwd: Path) -> str:
    if not (cwd / ".git").exists():
        return None
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(cwd), capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            return r.stdout.strip()
    except (subprocess.SubprocessError, OSError):
        pass
    return None


def force_snapshot(reason: str = "explicit") -> Path:
    """Create a snapshot now regardless of triggers. Returns snapshot dir path."""
    now = datetime.now()
    ts = now.strftime("%Y%m%dT%H%M%S")
    snap_dir = SNAPSHOT_ROOT / ts
    snap_dir.mkdir(parents=True, exist_ok=True)

    # Copy navigation files
    copied = []
    for src in FILES_TO_SNAPSHOT:
        if src.exists():
            dst = snap_dir / src.name
            shutil.copy2(src, dst)
            copied.append(src.name)

    # Capture git HEADs
    git_heads = {}
    git_heads["clawd_local"] = _git_head(CLAWD)
    git_heads["multi_dac_staging"] = _git_head(CLAWD / "repo-staging" / "Corpus-Perspectival")

    # Capture monitor heartbeats
    heartbeats = {}
    for hb_path in (CLAWD / "memory").glob("monitor_*_heartbeat.json"):
        try:
            heartbeats[hb_path.name] = json.loads(hb_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass

    # Manifest
    manifest = {
        "snapshot_ts": now.isoformat(),
        "reason": reason,
        "files_copied": copied,
        "git_heads": git_heads,
        "monitor_heartbeats_snapshotted": list(heartbeats.keys()),
        "heartbeat_states": heartbeats,
    }
    (snap_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    # Update state
    state = _load_state()
    state["last_snapshot_ts"] = now.isoformat()
    state["activity_since_snapshot"] = 0
    state["total_snapshots"] = state.get("total_snapshots", 0) + 1
    _save_state(state)

    _audit({"event": "snapshot_created", "snapshot_dir": str(snap_dir), "reason": reason, "files_copied": len(copied)})
    return snap_dir


def maybe_snapshot(
    time_threshold_minutes: int = DEFAULT_TIME_THRESHOLD_MINUTES,
    activity_threshold: int = DEFAULT_ACTIVITY_THRESHOLD,
    activity_delta: int = 1,
) -> Path:
    """Check triggers; snapshot if any fires. Returns snapshot dir or None."""
    state = _load_state()
    state["activity_since_snapshot"] = state.get("activity_since_snapshot", 0) + activity_delta
    _save_state(state)

    triggers_fired = []
    now = datetime.now()
    last_ts_str = state.get("last_snapshot_ts")
    if last_ts_str is None:
        triggers_fired.append("no_prior_snapshot")
    else:
        last_ts = datetime.fromisoformat(last_ts_str)
        elapsed_min = (now - last_ts).total_seconds() / 60.0
        if elapsed_min >= time_threshold_minutes:
            triggers_fired.append(f"time_elapsed_{int(elapsed_min)}min")

    if state["activity_since_snapshot"] >= activity_threshold:
        triggers_fired.append(f"activity_{state['activity_since_snapshot']}")

    if not triggers_fired:
        return None

    return force_snapshot(reason=";".join(triggers_fired))


def status() -> dict:
    state = _load_state()
    out = {
        "timestamp": datetime.now().isoformat(),
        "last_snapshot_ts": state.get("last_snapshot_ts"),
        "activity_since_snapshot": state.get("activity_since_snapshot", 0),
        "total_snapshots": state.get("total_snapshots", 0),
        "snapshot_root": str(SNAPSHOT_ROOT),
    }
    if state.get("last_snapshot_ts"):
        last = datetime.fromisoformat(state["last_snapshot_ts"])
        out["minutes_since_last_snapshot"] = round((datetime.now() - last).total_seconds() / 60.0, 1)
    # List existing snapshots
    if SNAPSHOT_ROOT.exists():
        snaps = sorted([p.name for p in SNAPSHOT_ROOT.iterdir() if p.is_dir()])
        out["snapshots_on_disk"] = len(snaps)
        out["latest_snapshot_dir"] = snaps[-1] if snaps else None
    return out


def synthetic_test() -> bool:
    """Falsifiability: synthetic trigger should fire and produce a snapshot."""
    print("=== M5 PreCompact Substitute Falsifiability Test ===")
    # Force activity-trigger by exceeding threshold in one call
    snap_dir = maybe_snapshot(time_threshold_minutes=999999, activity_threshold=1, activity_delta=10)
    if snap_dir is None:
        print("  FAIL: trigger did not fire")
        return False

    # Verify snapshot artifacts
    manifest_path = snap_dir / "manifest.json"
    if not manifest_path.exists():
        print(f"  FAIL: snapshot dir created but no manifest at {manifest_path}")
        return False
    manifest = json.loads(manifest_path.read_text())
    if not manifest.get("files_copied"):
        print(f"  FAIL: manifest has empty files_copied")
        return False

    print(f"  PASS: snapshot created at {snap_dir}")
    print(f"  reason: {manifest['reason']}")
    print(f"  files copied: {manifest['files_copied']}")
    print(f"  git heads captured: {list(manifest['git_heads'].keys())}")
    print(f"  monitor heartbeats captured: {len(manifest['monitor_heartbeats_snapshotted'])}")
    return True


def write_heartbeat() -> None:
    state = _load_state()
    payload = {
        "monitor": "M5",
        "timestamp": datetime.now().isoformat(),
        "pid": os.getpid(),
        "total_snapshots": state.get("total_snapshots", 0),
        "activity_since_snapshot": state.get("activity_since_snapshot", 0),
        "last_snapshot_ts": state.get("last_snapshot_ts"),
    }
    M5_HEARTBEAT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?", default="status", choices=["status", "force", "maybe"])
    parser.add_argument("--test-synthetic", action="store_true")
    args = parser.parse_args()

    if args.test_synthetic:
        ok = synthetic_test()
        write_heartbeat()
        sys.exit(0 if ok else 1)

    if args.command == "status":
        s = status()
        print(f"=== M5 PreCompact Substitute Status {s['timestamp']} ===")
        print(f"  total snapshots: {s['total_snapshots']}")
        print(f"  activity since last: {s['activity_since_snapshot']}")
        print(f"  minutes since last: {s.get('minutes_since_last_snapshot', 'n/a')}")
        print(f"  snapshots on disk: {s.get('snapshots_on_disk', 0)}")
        print(f"  latest: {s.get('latest_snapshot_dir', 'none')}")
        write_heartbeat()

    elif args.command == "force":
        snap = force_snapshot(reason="cli_force")
        print(f"  snapshot created: {snap}")
        write_heartbeat()

    elif args.command == "maybe":
        snap = maybe_snapshot()
        if snap:
            print(f"  trigger fired; snapshot created: {snap}")
        else:
            print(f"  no trigger fired; current state: {status()}")
        write_heartbeat()


if __name__ == "__main__":
    main()
