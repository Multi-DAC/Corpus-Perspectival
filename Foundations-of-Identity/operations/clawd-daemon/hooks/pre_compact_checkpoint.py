#!/usr/bin/env python3
"""PreCompact hook — preserves session state before context compaction.

Claude Code's PreCompact event fires before the harness compacts the
conversation context to save tokens. This hook writes a checkpoint file
capturing what's recoverable from the hook's input (session_id,
transcript_path, current cwd) so that post-compact orientation has a
"last-known-state-before-compact" reference.

The hook does NOT block compaction. It runs synchronously (timeout-bounded)
to ensure the checkpoint is written before compaction proceeds, but it
exits cleanly with code 0 to let compaction continue normally.

Receives JSON on stdin per the Claude Code hooks protocol. Available fields
include session_id, transcript_path, cwd, hook_event_name. Per 2.1.105+
hooks can block via exit 2 or {"decision":"block"}; this hook intentionally
does not block.

Writes to: <CLAWD_HOME>/memory/checkpoints/precompact-<timestamp>.json
Also appends a brief marker line to the day's daily log so post-compact
re-orientation surfaces it as part of standard handoff/daily-log review.

R8 from infrastructure audit 2026-05-15 Day 105.
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
CHECKPOINT_DIR = CLAWD_HOME / "memory" / "checkpoints"
ERROR_LOG = CLAWD_HOME / "memory" / "precompact_errors.log"


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


def _append_daily_log_marker(timestamp: str, session_id: str | None) -> None:
    """Append a one-line marker to today's daily log noting the compaction."""
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        daily_log = CLAWD_HOME / "memory" / f"{today}.md"
        sid_short = (session_id[:12] + "...") if session_id else "(unknown)"
        marker = (
            f"\n**{datetime.now().strftime('%H:%M:%S')} — PreCompact checkpoint** "
            f"(session {sid_short}; checkpoint at memory/checkpoints/"
            f"precompact-{timestamp}.json)\n"
        )
        # Only append if daily log exists (don't create it from a hook)
        if daily_log.exists():
            with open(daily_log, "a", encoding="utf-8") as f:
                f.write(marker)
    except Exception as exc:
        _record_error(exc, "daily log marker append")


def main() -> int:
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")

    # Read whatever Claude Code sent us
    try:
        raw = sys.stdin.read()
        try:
            data = json.loads(raw) if raw.strip() else {}
        except json.JSONDecodeError:
            # Couldn't parse JSON; record raw input for diagnostic
            data = {"_raw_stdin": raw[:2000]}
    except Exception as exc:
        _record_error(exc, "stdin read")
        data = {}

    # Build checkpoint
    checkpoint = {
        "compacted_at": datetime.now().isoformat(),
        "timestamp": timestamp,
        "hook_event": data.get("hook_event_name", "PreCompact"),
        "session_id": data.get("session_id"),
        "transcript_path": data.get("transcript_path"),
        "cwd": data.get("cwd"),
        "raw_input": data,  # preserve everything the hook received for forensic review
    }

    # Write checkpoint
    try:
        CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
        checkpoint_file = CHECKPOINT_DIR / f"precompact-{timestamp}.json"
        with open(checkpoint_file, "w", encoding="utf-8") as f:
            json.dump(checkpoint, f, indent=2, default=str)
    except Exception as exc:
        _record_error(exc, f"checkpoint write to {CHECKPOINT_DIR}")

    # Append daily log marker
    _append_daily_log_marker(timestamp, data.get("session_id"))

    # Exit cleanly — do NOT block compaction
    return 0


if __name__ == "__main__":
    sys.exit(main())
