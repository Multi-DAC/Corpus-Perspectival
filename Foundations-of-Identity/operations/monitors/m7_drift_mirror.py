"""M7: Drift mirror daemon-layer replication (A115 fix path A).

Replicates what the Claude Code drift_mirror hook USED to do, before the
Windows hook-dispatcher regression silently broke it on Day 97 (May 7).
Hook is still configured in .claude/settings.json; this is the daemon-layer
backstop that runs regardless of whether the hook fires.

What the hook does (when working):
- On every PostToolUse Edit/Write of a Drift essay in
  Foundations-of-Identity/personal-works/drift/essays/, shutil.copy2()
  the file to Library/Drift/essays/.

What this monitor does (always):
- Polls both directories; copies any canonical essay whose mtime is newer
  than its mirror counterpart, OR which exists only in canonical.
- Writes audit record per copy to memory/m7_drift_mirror_audit.jsonl.
- Emits heartbeat at memory/monitor_m7_heartbeat.json.
- If parity is OK, no-op.

Conservative: NEVER deletes from mirror. If the mirror has files canonical
doesn't, those persist (handled by separate manual reorg, e.g. A116 in May).

Per Substrate Extension Plan gap #1: A115 daemon-layer replication.
Decision rationale documented in 2026-05-20 research deliverable.

Falsifiability: synthetic test writes a new essay to canonical, runs the
monitor, verifies the file appears in mirror with matching content.

Usage:
    python operations/monitors/m7_drift_mirror.py            # one pass
    python operations/monitors/m7_drift_mirror.py --quiet    # one pass, log-only
    python operations/monitors/m7_drift_mirror.py --status   # show parity state
    python operations/monitors/m7_drift_mirror.py --test-synthetic
"""
import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CLAWD = Path(r"C:\Users\mercu\clawd")
if str(CLAWD) not in sys.path:
    sys.path.insert(0, str(CLAWD))

CANONICAL = CLAWD / "repo-staging" / "Corpus-Perspectival" / "Foundations-of-Identity" / "personal-works" / "drift" / "essays"
MIRROR    = CLAWD / "repo-staging" / "Corpus-Perspectival" / "Library" / "Drift" / "essays"
HEARTBEAT = CLAWD / "memory" / "monitor_m7_heartbeat.json"
AUDIT     = CLAWD / "memory" / "m7_drift_mirror_audit.jsonl"


def _emit_otel(action: str, copied: int, missing: int, drift: int):
    try:
        from operations.monitors.otel_telemetry import MonitorTelemetry
        tel = MonitorTelemetry(monitor_name="M7", monitor_version="v0.1.0")
        tel.counter("M7.runs", 1)
        tel.gauge("M7.files_copied", copied)
        tel.gauge("M7.files_missing_from_mirror", missing)
        tel.gauge("M7.files_mtime_drift", drift)
        tel.emit()
    except Exception:
        pass


def _file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _audit_event(record: dict) -> None:
    record["ts"] = datetime.now().isoformat()
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def scan_parity() -> dict:
    """Return parity state: which essays need copying canonical->mirror."""
    if not CANONICAL.exists():
        return {"error": "canonical_dir_missing", "path": str(CANONICAL)}
    if not MIRROR.exists():
        MIRROR.mkdir(parents=True, exist_ok=True)
    needs_copy = []  # missing from mirror
    needs_refresh = []  # canonical newer than mirror
    mirror_orphans = []  # in mirror but not canonical (informational only)
    canonical_files = {p.name: p for p in CANONICAL.glob("*.md")}
    mirror_files = {p.name: p for p in MIRROR.glob("*.md")}
    for name, cpath in canonical_files.items():
        if name not in mirror_files:
            needs_copy.append(name)
            continue
        mpath = mirror_files[name]
        if cpath.stat().st_mtime > mpath.stat().st_mtime + 1:  # 1s tolerance for fs precision
            needs_refresh.append(name)
    for name in mirror_files:
        if name not in canonical_files:
            mirror_orphans.append(name)
    return {
        "canonical_count": len(canonical_files),
        "mirror_count": len(mirror_files),
        "needs_copy": needs_copy,
        "needs_refresh": needs_refresh,
        "mirror_orphans": mirror_orphans,
        "parity_ok": (len(needs_copy) == 0 and len(needs_refresh) == 0),
    }


def reconcile() -> dict:
    """Copy missing/stale canonical files to mirror. Returns summary."""
    state = scan_parity()
    if "error" in state:
        return state
    copied = []
    refreshed = []
    errors = []
    for name in state["needs_copy"]:
        src = CANONICAL / name
        dst = MIRROR / name
        try:
            shutil.copy2(src, dst)
            copied.append(name)
            _audit_event({"event": "copy_missing", "file": name, "size": src.stat().st_size})
        except Exception as e:
            errors.append({"file": name, "error": str(e)})
            _audit_event({"event": "copy_error", "file": name, "error": str(e)})
    for name in state["needs_refresh"]:
        src = CANONICAL / name
        dst = MIRROR / name
        try:
            # Only refresh if content differs (mtime drift alone isn't enough -- avoid touch loops)
            if _file_hash(src) != _file_hash(dst):
                shutil.copy2(src, dst)
                refreshed.append(name)
                _audit_event({"event": "refresh_stale", "file": name})
        except Exception as e:
            errors.append({"file": name, "error": str(e)})
            _audit_event({"event": "refresh_error", "file": name, "error": str(e)})
    summary = {
        "ts": datetime.now().isoformat(),
        "canonical_count": state["canonical_count"],
        "mirror_count_after": state["mirror_count"] + len(copied),
        "copied_missing": copied,
        "refreshed_stale": refreshed,
        "mirror_orphans": state["mirror_orphans"],  # informational
        "errors": errors,
        "parity_now_ok": len(errors) == 0,
    }
    _emit_otel("reconcile", len(copied) + len(refreshed), len(state["needs_copy"]),
               len(state["needs_refresh"]))
    return summary


def _write_heartbeat(summary: dict) -> None:
    payload = {
        "monitor": "M7_drift_mirror",
        "timestamp": datetime.now().isoformat(),
        "canonical_count": summary.get("canonical_count"),
        "mirror_count_after": summary.get("mirror_count_after"),
        "copied_this_pass": len(summary.get("copied_missing", [])),
        "refreshed_this_pass": len(summary.get("refreshed_stale", [])),
        "orphans": len(summary.get("mirror_orphans", [])),
        "parity_ok": summary.get("parity_now_ok", False),
    }
    HEARTBEAT.parent.mkdir(parents=True, exist_ok=True)
    HEARTBEAT.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def synthetic_test() -> bool:
    """Falsifiability: write a temp essay to canonical, reconcile, verify mirror."""
    print("=== M7 Drift Mirror — Synthetic Falsifiability Test ===")
    marker = f"_synthetic_m7_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    test_canonical = CANONICAL / f"{marker}.md"
    test_mirror = MIRROR / f"{marker}.md"
    try:
        test_canonical.write_text(f"# Synthetic Test Essay\n\nMarker: {marker}\n",
                                  encoding="utf-8")
        # Pre-condition: only in canonical
        if test_mirror.exists():
            print(f"  FAIL: test marker already in mirror before reconcile")
            return False
        s = reconcile()
        if marker + ".md" not in s["copied_missing"]:
            print(f"  FAIL: test essay not in copied_missing: {s['copied_missing']}")
            return False
        if not test_mirror.exists():
            print(f"  FAIL: test essay not present in mirror after reconcile")
            return False
        if test_canonical.read_text(encoding="utf-8") != test_mirror.read_text(encoding="utf-8"):
            print(f"  FAIL: content mismatch between canonical and mirror")
            return False
        print(f"  PASS: temp essay copied canonical -> mirror; content matches")
        # Test refresh path: modify canonical, reconcile, verify mirror updated
        import time
        time.sleep(1.1)  # ensure mtime separation
        test_canonical.write_text(f"# Synthetic Test Essay (v2)\n\nMarker: {marker}\n",
                                  encoding="utf-8")
        s2 = reconcile()
        if marker + ".md" not in s2["refreshed_stale"]:
            print(f"  FAIL: test essay not in refreshed_stale: {s2['refreshed_stale']}")
            return False
        if "(v2)" not in test_mirror.read_text(encoding="utf-8"):
            print(f"  FAIL: mirror did not receive v2 content")
            return False
        print(f"  PASS: stale mirror refreshed from canonical (content diff)")
        return True
    finally:
        for p in [test_canonical, test_mirror]:
            if p.exists():
                p.unlink()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quiet", action="store_true", help="log-only (no stdout)")
    parser.add_argument("--status", action="store_true", help="show parity state without reconciling")
    parser.add_argument("--test-synthetic", action="store_true")
    args = parser.parse_args()

    if args.test_synthetic:
        ok = synthetic_test()
        sys.exit(0 if ok else 1)

    if args.status:
        s = scan_parity()
        print(f"=== M7 Drift Mirror Parity State ===")
        for k, v in s.items():
            if isinstance(v, list):
                print(f"  {k}: {len(v)}")
                for item in v[:5]:
                    print(f"    - {item}")
                if len(v) > 5:
                    print(f"    ... and {len(v) - 5} more")
            else:
                print(f"  {k}: {v}")
        return

    s = reconcile()
    _write_heartbeat(s)
    if not args.quiet:
        print(f"=== M7 Drift Mirror Reconcile  {s['ts'][:19]} ===")
        print(f"  canonical:   {s['canonical_count']}")
        print(f"  mirror after: {s['mirror_count_after']}")
        if s["copied_missing"]:
            print(f"  copied missing: {len(s['copied_missing'])}")
            for n in s["copied_missing"][:5]:
                print(f"    + {n}")
        if s["refreshed_stale"]:
            print(f"  refreshed stale: {len(s['refreshed_stale'])}")
        if s["mirror_orphans"]:
            print(f"  mirror orphans (info): {len(s['mirror_orphans'])}")
        if s["errors"]:
            print(f"  *** errors: {len(s['errors'])} ***")
            for e in s["errors"][:5]:
                print(f"    {e}")


if __name__ == "__main__":
    main()
