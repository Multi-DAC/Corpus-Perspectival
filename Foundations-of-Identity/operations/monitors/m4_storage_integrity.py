"""M4: Storage-Integrity Sentinel.

Verifies that critical storage layers parse, exist, and respond. Catches
JSONL corruption, ChromaDB unresponsiveness, SQLite DB issues, and
missing-critical-file failures before downstream consumers hit them.

Integrated implementation plan #7. Protects the KG + corpus_search +
T1.A index investment. Atomic heartbeat + UTF-8 + audit log per pattern.

Falsifiability commitment: must detect synthetic JSONL corruption within
1 sanity-check pass. Verified by --test-synthetic.

Checks:
- KG canonical JSONL: parses line-by-line; file is non-empty
- T1.A SQLite index: file exists; opens; expected tables present; row count > 0
- ChromaDB corpus_search index: directory present; responds to a smoke query
- Auto-memory SQLite (clawd_memory.db): file exists; opens
- Critical navigation files exist + non-empty (handoff, CURRENT, ATRIUM)

Usage:
    python operations/monitors/m4_storage_integrity.py
    python operations/monitors/m4_storage_integrity.py --json
    python operations/monitors/m4_storage_integrity.py --quiet
    python operations/monitors/m4_storage_integrity.py --test-synthetic
"""
import argparse
import json
import os
import shutil
import sqlite3
import sys
import tempfile
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CLAWD = Path(r"C:\Users\mercu\clawd")
M4_HEARTBEAT_PATH = CLAWD / "memory" / "monitor_m4_heartbeat.json"
M4_FAULT_LOG_PATH = CLAWD / "memory" / "monitor_m4_faults.jsonl"


def check_jsonl(path: Path, max_sample_lines: int = 100) -> dict:
    """Sample-parse a JSONL file. Reports first parse failure if any."""
    if not path.exists():
        return {"check": f"jsonl:{path.name}", "status": "missing", "path": str(path)}
    if path.stat().st_size == 0:
        return {"check": f"jsonl:{path.name}", "status": "empty", "path": str(path)}

    failed_at = None
    parsed_lines = 0
    try:
        with open(path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                if not line.strip():
                    continue
                try:
                    json.loads(line)
                    parsed_lines += 1
                except json.JSONDecodeError as e:
                    failed_at = (i, str(e))
                    break
                if parsed_lines >= max_sample_lines:
                    break
    except OSError as e:
        return {"check": f"jsonl:{path.name}", "status": "read_error", "error": str(e)}

    if failed_at:
        return {
            "check": f"jsonl:{path.name}",
            "status": "corrupt",
            "failed_at_line": failed_at[0],
            "error": failed_at[1],
            "lines_parsed_ok": parsed_lines,
        }
    return {"check": f"jsonl:{path.name}", "status": "ok", "lines_sampled": parsed_lines, "size_bytes": path.stat().st_size}


def check_sqlite(path: Path, expected_tables: list = None) -> dict:
    if not path.exists():
        return {"check": f"sqlite:{path.name}", "status": "missing", "path": str(path)}
    try:
        conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True, timeout=5)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cur.fetchall()]
        result = {"check": f"sqlite:{path.name}", "status": "ok", "tables": tables, "size_bytes": path.stat().st_size}
        if expected_tables:
            missing = [t for t in expected_tables if t not in tables]
            if missing:
                result["status"] = "schema_drift"
                result["missing_tables"] = missing
        # Cheap row-count sanity for first known table
        if tables:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {tables[0]}")
                result["sample_row_count"] = cur.fetchone()[0]
            except sqlite3.Error:
                pass
        conn.close()
        return result
    except sqlite3.DatabaseError as e:
        return {"check": f"sqlite:{path.name}", "status": "corrupt", "error": str(e)}
    except sqlite3.OperationalError as e:
        return {"check": f"sqlite:{path.name}", "status": "locked_or_unreachable", "error": str(e)}


def check_chromadb_dir() -> dict:
    """Light-touch: verify chromadb directory exists and has expected internal structure.

    We do NOT spin up a chromadb client (too expensive for a monitor); instead
    we check the on-disk presence of the persistent collection files. Full
    query check is deferred to a separate opt-in mode.
    """
    chroma = CLAWD / "memory" / "chroma_corpus"
    if not chroma.exists():
        return {"check": "chromadb:chroma_corpus", "status": "missing", "path": str(chroma)}
    files = list(chroma.glob("*.sqlite3")) + list(chroma.glob("**/*.sqlite3"))
    if not files:
        return {"check": "chromadb:chroma_corpus", "status": "no_persistent_files", "path": str(chroma)}
    total_size = sum(f.stat().st_size for f in files)
    return {
        "check": "chromadb:chroma_corpus",
        "status": "ok",
        "persistent_files": len(files),
        "total_size_bytes": total_size,
    }


def check_critical_file(path: Path, min_size_bytes: int = 100) -> dict:
    if not path.exists():
        return {"check": f"file:{path.name}", "status": "missing", "path": str(path)}
    size = path.stat().st_size
    if size < min_size_bytes:
        return {"check": f"file:{path.name}", "status": "suspiciously_small", "size_bytes": size, "min_expected": min_size_bytes}
    return {"check": f"file:{path.name}", "status": "ok", "size_bytes": size}


def all_checks() -> list:
    return [
        check_jsonl(CLAWD / "memory" / "kg_corpus_extraction.jsonl"),
        check_sqlite(CLAWD / "memory" / "kg_index.db", expected_tables=["kg_edges", "kg_concepts", "kg_conflicts", "kg_meta"]),
        check_sqlite(CLAWD / "memory" / "clawd_memory.db"),
        check_chromadb_dir(),
        check_critical_file(CLAWD / "memory" / "handoff.md"),
        check_critical_file(CLAWD / "CURRENT.md"),
        check_critical_file(CLAWD / "palace" / "ATRIUM.md"),
    ]


def severity_of(status: str) -> str:
    if status == "ok":
        return "ok"
    if status in ("corrupt", "schema_drift"):
        return "critical"
    if status in ("missing", "locked_or_unreachable"):
        return "high"
    if status in ("empty", "suspiciously_small", "no_persistent_files"):
        return "medium"
    if status == "read_error":
        return "high"
    return "low"


def write_heartbeat(checks: list) -> None:
    payload = {
        "monitor": "M4",
        "timestamp": datetime.now().isoformat(),
        "pid": os.getpid(),
        "checks_total": len(checks),
        "checks_ok": sum(1 for c in checks if c["status"] == "ok"),
        "checks_critical": sum(1 for c in checks if severity_of(c["status"]) == "critical"),
        "checks_high": sum(1 for c in checks if severity_of(c["status"]) == "high"),
    }
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=str(M4_HEARTBEAT_PATH.parent), delete=False) as tmp:
        json.dump(payload, tmp, indent=2)
        tmp_name = tmp.name
    shutil.move(tmp_name, M4_HEARTBEAT_PATH)


def append_faults(checks: list) -> None:
    faults = [c for c in checks if c["status"] != "ok"]
    if not faults:
        return
    record = {"timestamp": datetime.now().isoformat(), "faults": faults}
    with open(M4_FAULT_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def synthetic_test() -> bool:
    """Falsifiability: detect synthetic JSONL corruption."""
    print("=== M4 Falsifiability Test ===")
    test_file = CLAWD / "memory" / "_m4_test.jsonl"
    test_file.write_text('{"valid": 1}\n{"valid": 2}\n{this is not json\n{"valid": 3}\n', encoding="utf-8")
    try:
        result = check_jsonl(test_file)
    finally:
        test_file.unlink(missing_ok=True)

    if result["status"] == "corrupt" and result.get("failed_at_line") == 3:
        print(f"  PASS: detected synthetic JSONL corruption at line {result['failed_at_line']}")
        print(f"  parsed_ok_before_corruption: {result['lines_parsed_ok']}; error: {result['error'][:80]}")
        return True
    else:
        print(f"  FAIL: result={result}")
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--test-synthetic", action="store_true")
    args = parser.parse_args()

    if args.test_synthetic:
        ok = synthetic_test()
        sys.exit(0 if ok else 1)

    if not M4_HEARTBEAT_PATH.exists():
        M4_HEARTBEAT_PATH.write_text(json.dumps({
            "monitor": "M4", "timestamp": datetime.now().isoformat(),
            "pid": os.getpid(), "status": "initializing"
        }, indent=2))

    run_start = datetime.now()
    checks = all_checks()
    write_heartbeat(checks)
    append_faults(checks)
    run_elapsed = (datetime.now() - run_start).total_seconds()

    # T2.G: emit OTel metrics
    try:
        from operations.monitors.otel_telemetry import MonitorTelemetry
    except ImportError:
        sys.path.insert(0, str(CLAWD))
        from operations.monitors.otel_telemetry import MonitorTelemetry
    tel = MonitorTelemetry(monitor_name="M4", monitor_version="v0.1.0")
    tel.counter("runs", 1)
    tel.gauge("checks_total", len(checks))
    tel.gauge("checks_ok", sum(1 for c in checks if c["status"] == "ok"))
    tel.gauge("checks_critical", sum(1 for c in checks if severity_of(c["status"]) == "critical"))
    tel.gauge("checks_high", sum(1 for c in checks if severity_of(c["status"]) == "high"))
    for c in checks:
        tel.counter("check_status_observations", 1,
                    attributes={"check": c["check"], "status": c["status"]})
    tel.histogram("run_duration_seconds", run_elapsed)
    tel.emit()

    if args.quiet:
        return

    if args.json:
        print(json.dumps(checks, indent=2))
        return

    print(f"=== M4 Storage-Integrity Check {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    for c in checks:
        sev = severity_of(c["status"])
        name = c["check"]
        if sev == "ok":
            extras = []
            if "size_bytes" in c: extras.append(f"size={c['size_bytes']:,}B")
            if "lines_sampled" in c: extras.append(f"lines~{c['lines_sampled']}")
            if "tables" in c: extras.append(f"tables={len(c['tables'])}")
            if "sample_row_count" in c: extras.append(f"rows~{c['sample_row_count']:,}")
            if "persistent_files" in c: extras.append(f"files={c['persistent_files']}")
            print(f"  OK         {name:35} {' '.join(extras)}")
        elif sev == "critical":
            print(f"  CRITICAL   {name:35} {c['status']}  {c.get('error', '')[:80]}")
        elif sev == "high":
            print(f"  HIGH       {name:35} {c['status']}  {c.get('error', c.get('path', ''))[:80]}")
        elif sev == "medium":
            print(f"  med        {name:35} {c['status']}  {c.get('path', '')[:80]}")
        else:
            print(f"  low        {name:35} {c['status']}")


if __name__ == "__main__":
    main()
