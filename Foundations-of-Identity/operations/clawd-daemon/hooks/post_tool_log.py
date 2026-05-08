#!/usr/bin/env python3
"""PostToolUse hook — logs Claude Code's internal tool calls to a structured log.

Receives JSON on stdin with tool_name, tool_input, tool_output.
Appends to <CLAWD_HOME>/memory/tool_audit.jsonl via structured logging.
Runs async (non-blocking) so it never slows down Claude Code.

Path resolution: CLAWD_HOME env var > script-relative sibling dir > absolute fallback.
The original implementation used Path.home() which silently broke when the running
user account differed from the repo owner — a single 2026-03-15 entry was the only
write that ever succeeded. Mirror #28 instance: self-monitoring infrastructure
configured correctly but producing null information silently.

Exceptions are written to a sibling tool_audit_errors.log so future silent failures
surface instead of accumulating undetected.
"""
import json
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path


def _resolve_clawd_home() -> Path:
    env_value = os.environ.get("CLAWD_HOME")
    if env_value:
        return Path(env_value)
    sibling = Path(__file__).resolve().parent.parent.parent / "clawd"
    if sibling.exists():
        return sibling
    return Path("C:/Users/mercu/clawd")


CLAWD_HOME = _resolve_clawd_home()
LOG_FILE = CLAWD_HOME / "memory" / "tool_audit.jsonl"
ERROR_LOG = CLAWD_HOME / "memory" / "tool_audit_errors.log"


def _record_error(exc: BaseException, context: str) -> None:
    try:
        ERROR_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(ERROR_LOG, "a", encoding="utf-8") as f:
            f.write(
                f"[{datetime.now().isoformat()}] {context}: {type(exc).__name__}: {exc}\n"
                + traceback.format_exc()
                + "\n"
            )
    except Exception:
        pass


def main():
    try:
        data = json.loads(sys.stdin.read())
    except Exception as exc:
        _record_error(exc, "stdin parse")
        return

    tool_name = data.get("tool_name", "unknown")
    tool_input = data.get("tool_input", {})

    if tool_name in ("Read", "Glob", "Grep", "Bash"):
        if tool_name == "Bash":
            entry = {
                "ts": datetime.now().isoformat(),
                "tool": tool_name,
                "command": tool_input.get("command", "")[:200],
            }
        else:
            return
    else:
        entry = {
            "ts": datetime.now().isoformat(),
            "tool": tool_name,
            "input_preview": json.dumps(tool_input)[:200],
        }

    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as exc:
        _record_error(exc, f"log write to {LOG_FILE}")

    # Day 96 evening Phase 4 #6 — also write to SQLite audit_trail.
    # Closes the "two audit logs, neither alive" gap. tool_audit.jsonl is
    # append-only line-oriented; audit_trail is queryable. Both have
    # different strengths; populate both. Uses sync sqlite3 (not async)
    # since hooks run as one-shot subprocesses.
    try:
        _write_to_audit_trail(tool_name, tool_input, entry)
    except Exception as exc:
        _record_error(exc, "audit_trail SQLite write")


def _write_to_audit_trail(tool_name: str, tool_input: dict, entry: dict) -> None:
    """Append a single row to the audit_trail SQLite table.

    Uses sync sqlite3 to avoid async machinery in a hook subprocess context.
    Best-effort: if the DB is locked by the running daemon, skip silently
    rather than blocking Claude Code.
    """
    import sqlite3
    import hashlib
    import time

    db_path = CLAWD_HOME / "memory" / "clawd_memory.db"
    if not db_path.exists():
        return  # Nothing to write to

    input_summary = json.dumps(tool_input or {}, default=str)[:2000]
    output_hash = hashlib.sha256(
        json.dumps(entry, default=str).encode("utf-8", errors="replace")
    ).hexdigest()[:16]

    # Short timeout — if the daemon has the DB locked, don't fight for it.
    try:
        conn = sqlite3.connect(str(db_path), timeout=1.0)
    except sqlite3.OperationalError:
        return

    try:
        cur = conn.cursor()
        # Schema is already established by daemon-side audit.py; just insert.
        cur.execute(
            """INSERT INTO audit_trail
               (tool_name, input_summary, output_hash, output_length,
                is_error, beat_number, timestamp, epoch)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                f"cc:{tool_name}",  # prefix to distinguish Claude Code calls
                input_summary,
                output_hash,
                len(input_summary),
                False,
                0,  # beat_number — hook calls aren't tied to heartbeat
                entry.get("ts", datetime.now().isoformat()),
                time.time(),
            ),
        )
        conn.commit()
    finally:
        try:
            conn.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
