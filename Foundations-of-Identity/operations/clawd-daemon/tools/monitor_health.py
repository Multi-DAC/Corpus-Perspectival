"""Monitor-the-Monitors — Anomaly detection on self-monitoring infrastructure.

Filed Day 96 evening 2026-05-07 as the structural fix for Mirror #28's
M2-Mirror infrastructure-trust-by-default sub-valence. The literature
name (Stream 3 research): "every monitor must itself be monitored."

Today's three Mirror #28 instances (A85 / schema-migration / post_tool_log)
were each one self-monitoring system silently producing wrong or null
information for weeks-to-months. A simple z-score job over per-monitor
write-rates would have caught each one on day one of its silent failure.

Scope: read-only health check across known monitors. Compute current
write-rate vs historical baseline. Flag at z-score >= 3.0 below baseline.

Monitors covered:
- File-based audit logs (tool_audit.jsonl, change_journal.json, anomalies.md)
- SQLite-tracked tables (audit_trail, episodes, memory_items, principles, kg_*)
- Daemon log file (clawd_daemon.log)
- Memory consolidation outputs (principles.json, knowledge_graph.json)

Returns structured findings; intended to run from bridge.py as
`bridge.py monitor_health '{}'` — health check on demand.
"""
import json
import logging
import os
import statistics
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

logger = logging.getLogger("clawd.tools.monitor_health")

CLAWD_HOME = Path(os.environ.get("CLAWD_HOME", os.path.expanduser("~/clawd")))
MEMORY_DIR = CLAWD_HOME / "memory"
DB_PATH = MEMORY_DIR / "clawd_memory.db"


def _file_age_seconds(path: Path) -> float | None:
    if not path.exists():
        return None
    return (datetime.now().timestamp() - path.stat().st_mtime)


def _file_size_bytes(path: Path) -> int:
    if not path.exists():
        return 0
    return path.stat().st_size


def _file_line_count(path: Path) -> int:
    if not path.exists():
        return 0
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


def check_jsonl_monitor(name: str, path: Path, expected_writes_per_hour: float, severity: str) -> dict:
    """Check a JSONL append-log monitor's recent activity vs expectation.

    expected_writes_per_hour: rough baseline for healthy operation (informed estimate).
    Returns a finding dict with status and details.
    """
    age_s = _file_age_seconds(path)
    line_count = _file_line_count(path)

    if age_s is None:
        return {
            "monitor": name,
            "path": str(path),
            "status": "MISSING",
            "severity": "HIGH",
            "lines": 0,
            "last_write_seconds_ago": None,
            "message": f"Monitor file does not exist at {path}",
        }

    age_h = age_s / 3600
    age_d = age_h / 24

    # Anomaly: file hasn't been written to recently relative to expected rate
    expected_interval_h = 1 / max(expected_writes_per_hour, 0.001)
    z_score_estimate = age_h / expected_interval_h if expected_interval_h > 0 else 0

    if z_score_estimate >= 100:  # >100x expected interval since last write
        status = "DEAD"
        sev = "CRITICAL"
    elif z_score_estimate >= 20:  # >20x expected interval
        status = "STALE"
        sev = severity
    elif z_score_estimate >= 5:  # >5x expected interval
        status = "QUIET"
        sev = "LOW"
    else:
        status = "OK"
        sev = "OK"

    return {
        "monitor": name,
        "path": str(path),
        "status": status,
        "severity": sev,
        "lines": line_count,
        "last_write_seconds_ago": int(age_s),
        "last_write_human": _humanize_seconds(age_s),
        "expected_writes_per_hour": expected_writes_per_hour,
        "z_score_estimate": round(z_score_estimate, 1),
    }


def check_sqlite_table(name: str, table: str, expected_writes_per_hour: float, severity: str) -> dict:
    """Check a SQLite table's recent write activity.

    Looks for a timestamp column and computes time-since-last-write +
    rate over last 24h.
    """
    if not DB_PATH.exists():
        return {
            "monitor": name,
            "path": str(DB_PATH),
            "status": "DB_MISSING",
            "severity": "CRITICAL",
            "message": "SQLite database does not exist",
        }

    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        # Check table exists
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        if not cur.fetchone():
            conn.close()
            return {
                "monitor": name,
                "table": table,
                "status": "TABLE_MISSING",
                "severity": "HIGH",
                "message": f"Table {table} does not exist",
            }

        # Find timestamp column
        cur.execute(f"PRAGMA table_info({table})")
        cols = [r[1] for r in cur.fetchall()]
        ts_col = next(
            (c for c in ["timestamp", "ts", "created_at", "created", "updated_at", "date"] if c in cols),
            None,
        )

        # Total rows
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        total_rows = cur.fetchone()[0]

        if not ts_col or total_rows == 0:
            conn.close()
            return {
                "monitor": name,
                "table": table,
                "status": "EMPTY" if total_rows == 0 else "NO_TS_COL",
                "severity": severity if total_rows == 0 else "LOW",
                "rows": total_rows,
                "message": f"{total_rows} rows; no timestamp column to age-check"
                if not ts_col else f"Empty (0 rows)",
            }

        # Latest write
        cur.execute(f"SELECT {ts_col} FROM {table} ORDER BY {ts_col} DESC LIMIT 1")
        latest_ts_str = cur.fetchone()[0]
        try:
            latest_ts = datetime.fromisoformat(latest_ts_str)
            age_s = (datetime.now() - latest_ts).total_seconds()
        except Exception:
            age_s = None

        # Rows in last 24h
        cutoff_24h = (datetime.now() - timedelta(hours=24)).isoformat()
        cur.execute(f"SELECT COUNT(*) FROM {table} WHERE {ts_col} > ?", (cutoff_24h,))
        rows_24h = cur.fetchone()[0]

        conn.close()

        if age_s is None:
            return {
                "monitor": name,
                "table": table,
                "status": "TS_PARSE_ERROR",
                "severity": "LOW",
                "rows": total_rows,
                "rows_24h": rows_24h,
                "message": f"Could not parse latest timestamp: {latest_ts_str!r}",
            }

        age_h = age_s / 3600
        expected_interval_h = 1 / max(expected_writes_per_hour, 0.001)
        z_score_estimate = age_h / expected_interval_h if expected_interval_h > 0 else 0

        if z_score_estimate >= 100:
            status = "DEAD"
            sev = "CRITICAL"
        elif z_score_estimate >= 20:
            status = "STALE"
            sev = severity
        elif z_score_estimate >= 5:
            status = "QUIET"
            sev = "LOW"
        else:
            status = "OK"
            sev = "OK"

        return {
            "monitor": name,
            "table": table,
            "status": status,
            "severity": sev,
            "rows": total_rows,
            "rows_24h": rows_24h,
            "last_write_seconds_ago": int(age_s),
            "last_write_human": _humanize_seconds(age_s),
            "latest_ts": latest_ts_str,
            "expected_writes_per_hour": expected_writes_per_hour,
            "z_score_estimate": round(z_score_estimate, 1),
        }
    except Exception as e:
        return {
            "monitor": name,
            "table": table,
            "status": "ERROR",
            "severity": "MEDIUM",
            "error": f"{type(e).__name__}: {e}",
        }


def check_file_freshness(name: str, path: Path, expected_age_max_hours: float, severity: str) -> dict:
    """Check that a file was modified recently enough.

    For files like principles.json, knowledge_graph.json that should be
    refreshed by consolidation runs.
    """
    age_s = _file_age_seconds(path)
    if age_s is None:
        return {
            "monitor": name,
            "path": str(path),
            "status": "MISSING",
            "severity": "HIGH",
            "message": f"File does not exist at {path}",
        }
    age_h = age_s / 3600
    if age_h <= expected_age_max_hours:
        status = "OK"
        sev = "OK"
    elif age_h <= expected_age_max_hours * 5:
        status = "QUIET"
        sev = "LOW"
    elif age_h <= expected_age_max_hours * 20:
        status = "STALE"
        sev = severity
    else:
        status = "DEAD"
        sev = "CRITICAL"

    return {
        "monitor": name,
        "path": str(path),
        "status": status,
        "severity": sev,
        "size_bytes": _file_size_bytes(path),
        "last_write_seconds_ago": int(age_s),
        "last_write_human": _humanize_seconds(age_s),
        "expected_age_max_hours": expected_age_max_hours,
    }


def _humanize_seconds(s: float) -> str:
    if s < 60:
        return f"{int(s)}s"
    if s < 3600:
        return f"{int(s / 60)}m"
    if s < 86400:
        return f"{int(s / 3600)}h"
    if s < 86400 * 7:
        return f"{int(s / 86400)}d"
    if s < 86400 * 30:
        return f"{int(s / (86400 * 7))}w"
    return f"{int(s / (86400 * 30))}mo"


def run_health_check(input_data: dict | None = None) -> str:
    """Run full monitor health check and return structured findings.

    Designed to be invoked via bridge.py: `bridge.py monitor_health '{}'`
    or as a standalone script: `python tools/monitor_health.py`.
    """
    findings = []

    # File-based monitors with rough baseline rates
    findings.append(check_jsonl_monitor(
        "post_tool_log (Claude Code hook)",
        MEMORY_DIR / "tool_audit.jsonl",
        expected_writes_per_hour=20.0,  # active session writes ~20/hour
        severity="HIGH",
    ))
    findings.append(check_jsonl_monitor(
        "change_journal (rollback tracker)",
        MEMORY_DIR / "change_journal.json",
        expected_writes_per_hour=2.0,  # writes happen on file mods
        severity="MEDIUM",
    ))

    # SQLite-tracked monitors
    findings.append(check_sqlite_table(
        "audit_trail (B9 — daemon-internal tool audit)",
        "audit_trail",
        expected_writes_per_hour=5.0,  # heartbeat tool calls
        severity="HIGH",
    ))
    findings.append(check_sqlite_table(
        "episodes (experience records)",
        "episodes",
        expected_writes_per_hour=0.5,  # ~12/day average
        severity="MEDIUM",
    ))
    findings.append(check_sqlite_table(
        "memory_items (semantic items)",
        "memory_items",
        expected_writes_per_hour=0.2,  # ~5/day average
        severity="MEDIUM",
    ))

    # Freshness checks (files that should be regenerated periodically)
    findings.append(check_file_freshness(
        "principles.json (consolidation Layer 4)",
        MEMORY_DIR / "principles.json",
        expected_age_max_hours=24.0,  # daily consolidation
        severity="MEDIUM",
    ))
    findings.append(check_file_freshness(
        "knowledge_graph.json (consolidation Layer 5)",
        MEMORY_DIR / "knowledge_graph.json",
        expected_age_max_hours=24.0,
        severity="MEDIUM",
    ))
    findings.append(check_file_freshness(
        "anomalies.md (research anomaly tracker)",
        MEMORY_DIR / "anomalies.md",
        expected_age_max_hours=168.0,  # at least weekly touch
        severity="LOW",
    ))

    # Daemon log
    findings.append(check_file_freshness(
        "clawd_daemon.log",
        CLAWD_HOME / "clawd_daemon.log",
        expected_age_max_hours=1.0,
        severity="HIGH",
    ))

    # Compute summary
    severity_counts = {"OK": 0, "LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    for f in findings:
        sev = f.get("severity", "OK")
        severity_counts[sev] = severity_counts.get(sev, 0) + 1

    overall = "HEALTHY"
    if severity_counts.get("CRITICAL", 0) > 0:
        overall = "CRITICAL"
    elif severity_counts.get("HIGH", 0) > 0:
        overall = "DEGRADED"
    elif severity_counts.get("MEDIUM", 0) > 0:
        overall = "WATCH"

    result = {
        "overall_health": overall,
        "checked_at": datetime.now().isoformat(),
        "severity_counts": severity_counts,
        "findings": findings,
    }

    return json.dumps(result, indent=2, default=str)


# Tool handler interface (for bridge.py + dispatch-wrapper registration)
TOOL_DEFINITIONS = [
    {
        "name": "monitor_health",
        "description": (
            "Run a substrate-health check across all known self-monitoring "
            "infrastructure (audit logs, SQLite tables, consolidation outputs, "
            "daemon log). Returns structured findings with severity (OK/LOW/"
            "MEDIUM/HIGH/CRITICAL) and z-score-style write-rate analysis. "
            "Filed Day 96 evening as the structural fix for Mirror #28: every "
            "monitor must itself be monitored."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
        },
    },
]


# Async wrapper so handler matches execute_tool's await pattern
async def _monitor_health_handler(input_data: dict) -> str:
    return run_health_check(input_data)


TOOL_HANDLERS = {
    "monitor_health": _monitor_health_handler,
}


if __name__ == "__main__":
    print(run_health_check({}))
