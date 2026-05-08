"""Structured Audit Trail — Logs all tool invocations to SQLite.

Records tool name, inputs (sanitized), output hash, timestamp, beat number,
and execution context. Queryable for safety review, debugging, and
behavioral analysis.

SOTA gap: B9 (structured audit trail of all tool invocations).
"""
import hashlib
import json
import logging
import time
from collections import deque
from datetime import datetime
from typing import Any

logger = logging.getLogger("clawd.tools.audit")

# In-memory buffer — flushed to SQLite periodically
_buffer: deque = deque(maxlen=500)
_last_flush: float = 0
_FLUSH_INTERVAL = 30  # seconds
_FLUSH_BATCH_SIZE = 50  # flush when buffer reaches this size

# Fields to redact from input logging
_SENSITIVE_FIELDS = {"password", "token", "secret", "api_key", "key", "auth"}


def _sanitize_input(input_data: dict) -> str:
    """Sanitize tool input for audit logging — redact sensitive fields."""
    sanitized = {}
    for k, v in input_data.items():
        if any(s in k.lower() for s in _SENSITIVE_FIELDS):
            sanitized[k] = "[REDACTED]"
        elif isinstance(v, str) and len(v) > 500:
            sanitized[k] = v[:500] + "...[truncated]"
        else:
            sanitized[k] = v
    try:
        return json.dumps(sanitized, default=str)[:2000]
    except Exception:
        return "{}"


def _hash_output(result: str) -> str:
    """Hash the output for compact storage — full output is in logs if needed."""
    if not result:
        return ""
    return hashlib.sha256(result.encode("utf-8", errors="replace")).hexdigest()[:16]


def record_tool_call(
    tool_name: str,
    input_data: dict,
    result: str,
    beat_number: int = 0,
):
    """Record a tool invocation to the audit buffer."""
    entry = {
        "tool_name": tool_name,
        "input_summary": _sanitize_input(input_data),
        "output_hash": _hash_output(result),
        "output_length": len(result) if result else 0,
        "is_error": result.startswith("Error") if result else False,
        "beat_number": beat_number,
        "timestamp": datetime.now().isoformat(),
        "epoch": time.time(),
    }
    _buffer.append(entry)

    # Auto-flush when buffer is large enough or enough time has passed
    global _last_flush
    now = time.time()
    if len(_buffer) >= _FLUSH_BATCH_SIZE or (now - _last_flush) > _FLUSH_INTERVAL:
        # Schedule async flush (non-blocking)
        try:
            import asyncio
            loop = asyncio.get_running_loop()
            loop.create_task(_flush_to_sqlite())
        except RuntimeError:
            pass  # No event loop — skip flush


async def _flush_to_sqlite():
    """Flush buffered audit entries to SQLite."""
    global _last_flush
    if not _buffer:
        return

    try:
        from tools.sqlite_store import get_db
        db = await get_db()
        if db is None:
            return

        # Ensure table exists
        await db.execute("""
            CREATE TABLE IF NOT EXISTS audit_trail (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tool_name TEXT NOT NULL,
                input_summary TEXT,
                output_hash TEXT,
                output_length INTEGER,
                is_error BOOLEAN DEFAULT 0,
                beat_number INTEGER DEFAULT 0,
                timestamp TEXT NOT NULL,
                epoch REAL
            )
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_tool ON audit_trail(tool_name)
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_time ON audit_trail(epoch)
        """)

        # Batch insert
        entries = []
        while _buffer:
            entries.append(_buffer.popleft())

        await db.executemany(
            """INSERT INTO audit_trail
               (tool_name, input_summary, output_hash, output_length, is_error, beat_number, timestamp, epoch)
               VALUES (:tool_name, :input_summary, :output_hash, :output_length, :is_error, :beat_number, :timestamp, :epoch)""",
            entries,
        )
        await db.commit()
        _last_flush = time.time()
        logger.debug(f"Audit trail: flushed {len(entries)} entries to SQLite")

    except Exception as e:
        logger.debug(f"Audit trail flush failed: {e}")


async def query_audit(
    tool_name: str = None,
    since_epoch: float = None,
    limit: int = 50,
) -> list[dict]:
    """Query the audit trail."""
    try:
        from tools.sqlite_store import get_db
        db = await get_db()
        if db is None:
            return []

        query = "SELECT * FROM audit_trail WHERE 1=1"
        params = {}
        if tool_name:
            query += " AND tool_name = :tool_name"
            params["tool_name"] = tool_name
        if since_epoch:
            query += " AND epoch >= :since_epoch"
            params["since_epoch"] = since_epoch
        query += " ORDER BY epoch DESC LIMIT :limit"
        params["limit"] = limit

        cursor = await db.execute(query, params)
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.debug(f"Audit query failed: {e}")
        return []


async def get_tool_call_stats(minutes: int = 60) -> dict:
    """Get tool call statistics for the last N minutes."""
    try:
        from tools.sqlite_store import get_db
        db = await get_db()
        if db is None:
            return {}

        since = time.time() - (minutes * 60)
        cursor = await db.execute(
            """SELECT tool_name, COUNT(*) as count, SUM(is_error) as errors,
                      AVG(output_length) as avg_output_len
               FROM audit_trail WHERE epoch >= ?
               GROUP BY tool_name ORDER BY count DESC""",
            (since,),
        )
        rows = await cursor.fetchall()
        return {row["tool_name"]: dict(row) for row in rows}
    except Exception as e:
        logger.debug(f"Audit stats query failed: {e}")
        return {}


# No tool definitions — this is an internal module
TOOL_DEFINITIONS = []
TOOL_HANDLERS = {}
