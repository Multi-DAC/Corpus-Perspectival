"""Ledger backup — daily snapshots of append-only JSONL ledgers.

Copies all *.jsonl in memory/ to memory/backups/YYYY-MM-DD/ with size +
checksum recorded in memory/ledger_backup_manifest.jsonl.

Retention v0: keep last 30 daily snapshots; older snapshots compacted to
manifest-only (filename + size + checksum, no body). Conservative — does
NOT delete uncompacted snapshots automatically; flags them for manual review.

Per Substrate Extension gap #6: code is in git; state isn't. Closes the
single-disk-no-backup gap for predictions/utility/faults/audit/otel ledgers.

Falsifiability commitment: synthetic test creates a temp ledger, runs
backup, verifies the snapshot exists with matching size + checksum.

Usage:
    python operations/monitors/ledger_backup.py run        # snapshot today
    python operations/monitors/ledger_backup.py status     # most-recent + retention
    python operations/monitors/ledger_backup.py verify     # checksum-verify last snapshot
    python operations/monitors/ledger_backup.py test       # synthetic falsifiability test
"""
import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CLAWD = Path(r"C:\Users\mercu\clawd")
if str(CLAWD) not in sys.path:
    sys.path.insert(0, str(CLAWD))

MEMORY = CLAWD / "memory"
BACKUPS = MEMORY / "backups"
MANIFEST = MEMORY / "ledger_backup_manifest.jsonl"
RETENTION_DAYS = 30


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _all_ledgers() -> list:
    """All .jsonl files in memory/ (top-level only, not in subdirs)."""
    return sorted([p for p in MEMORY.glob("*.jsonl") if p.is_file()])


def run_snapshot() -> dict:
    today = datetime.now().strftime("%Y-%m-%d")
    snap_dir = BACKUPS / today
    snap_dir.mkdir(parents=True, exist_ok=True)

    ledgers = _all_ledgers()
    files_backed = []
    total_bytes = 0
    for src in ledgers:
        dst = snap_dir / src.name
        shutil.copy2(src, dst)
        sz = dst.stat().st_size
        csum = _sha256(dst)
        files_backed.append({"name": src.name, "bytes": sz, "sha256": csum})
        total_bytes += sz

    record = {
        "ts": datetime.now().isoformat(),
        "snapshot_date": today,
        "snapshot_dir": str(snap_dir),
        "files_count": len(files_backed),
        "total_bytes": total_bytes,
        "files": files_backed,
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    return record


def _load_manifest() -> list:
    if not MANIFEST.exists():
        return []
    out = []
    with open(MANIFEST, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def status() -> dict:
    records = _load_manifest()
    if not records:
        return {"snapshots": 0, "latest": None}
    latest = records[-1]
    # Identify snapshots older than RETENTION_DAYS that haven't been compacted
    cutoff = datetime.now() - timedelta(days=RETENTION_DAYS)
    overdue = []
    for r in records:
        try:
            d = datetime.strptime(r["snapshot_date"], "%Y-%m-%d")
        except (ValueError, KeyError):
            continue
        if d < cutoff:
            snap_dir = Path(r["snapshot_dir"])
            if snap_dir.exists():
                overdue.append({"date": r["snapshot_date"], "dir": str(snap_dir)})
    return {
        "snapshots": len(records),
        "latest": {
            "date": latest["snapshot_date"],
            "files_count": latest["files_count"],
            "total_bytes": latest["total_bytes"],
            "dir": latest["snapshot_dir"],
        },
        "retention_overdue_count": len(overdue),
        "retention_overdue": overdue[:10],
    }


def verify_last() -> dict:
    """Recompute checksums of last snapshot; compare to manifest."""
    records = _load_manifest()
    if not records:
        return {"status": "no_snapshots"}
    latest = records[-1]
    snap_dir = Path(latest["snapshot_dir"])
    if not snap_dir.exists():
        return {"status": "snapshot_dir_missing", "dir": str(snap_dir)}
    mismatches = []
    verified = 0
    for f in latest["files"]:
        p = snap_dir / f["name"]
        if not p.exists():
            mismatches.append({"file": f["name"], "issue": "missing"})
            continue
        actual = _sha256(p)
        if actual != f["sha256"]:
            mismatches.append({"file": f["name"], "issue": "checksum_drift",
                               "expected": f["sha256"][:16], "actual": actual[:16]})
        else:
            verified += 1
    return {
        "status": "ok" if not mismatches else "drift_detected",
        "snapshot_date": latest["snapshot_date"],
        "verified": verified,
        "mismatches": mismatches,
    }


def synthetic_test() -> bool:
    """Falsifiability: create temp ledger -> snapshot -> verify."""
    print("=== Ledger Backup — Synthetic Falsifiability Test ===")
    test_marker = f"_synthetic_backup_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    temp_ledger = MEMORY / f"{test_marker}.jsonl"
    temp_ledger.write_text('{"event": "synthetic_test", "marker": "' + test_marker + '"}\n',
                           encoding="utf-8")
    try:
        rec = run_snapshot()
        snap_dir = Path(rec["snapshot_dir"])
        copied = snap_dir / temp_ledger.name
        if not copied.exists():
            print(f"  FAIL: temp ledger not in snapshot dir {snap_dir}")
            return False
        if _sha256(temp_ledger) != _sha256(copied):
            print(f"  FAIL: checksum mismatch between source and snapshot")
            return False
        print(f"  PASS: temp ledger backed up; sha256 matches; snapshot dir: {snap_dir.name}")
        # Verify the manifest also wrote our test file
        v = verify_last()
        if v["status"] != "ok":
            print(f"  FAIL: verify_last returned {v['status']}; mismatches={v['mismatches']}")
            return False
        print(f"  PASS: verify_last status=ok; verified {v['verified']} files")
        return True
    finally:
        # Cleanup the source temp ledger (not the snapshot — leave evidence)
        if temp_ledger.exists():
            temp_ledger.unlink()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["run", "status", "verify", "test"])
    args = parser.parse_args()

    if args.command == "run":
        rec = run_snapshot()
        print(f"=== Ledger Backup — Snapshot {rec['snapshot_date']} ===")
        print(f"  files: {rec['files_count']}")
        print(f"  total: {rec['total_bytes'] / 1024:.1f} KB")
        print(f"  dir:   {rec['snapshot_dir']}")
    elif args.command == "status":
        s = status()
        print(f"=== Ledger Backup Status ===")
        print(f"  snapshots taken: {s['snapshots']}")
        if s["latest"]:
            print(f"  latest:          {s['latest']['date']} ({s['latest']['files_count']} files, "
                  f"{s['latest']['total_bytes'] / 1024:.1f} KB)")
        if s.get("retention_overdue_count"):
            print(f"  *** {s['retention_overdue_count']} snapshots older than {RETENTION_DAYS}d "
                  "(manual compaction recommended) ***")
    elif args.command == "verify":
        v = verify_last()
        print(f"=== Ledger Backup Verify (last snapshot) ===")
        print(f"  status:  {v['status']}")
        if v.get("snapshot_date"):
            print(f"  date:    {v['snapshot_date']}")
            print(f"  verified: {v['verified']}")
        if v.get("mismatches"):
            print(f"  *** {len(v['mismatches'])} MISMATCHES ***")
            for m in v["mismatches"][:5]:
                print(f"    {m}")
    elif args.command == "test":
        ok = synthetic_test()
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
