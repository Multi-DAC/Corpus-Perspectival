"""Coordination — Heartbeat state and activity feed.

Provides a shared state file (memory/coordination.json) that tracks
heartbeat mode (active/sleep) and an activity feed for monitoring.
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import config

logger = logging.getLogger("clawd.tools.coordination")

COORDINATION_FILE = config.MEMORY_DIR / "coordination.json"
MAX_FEED_ENTRIES = 50


def _load() -> dict:
    """Load coordination state from disk."""
    if COORDINATION_FILE.exists():
        try:
            return json.loads(COORDINATION_FILE.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning(f"Failed to load coordination.json: {e}")
    return {
        "last_updated": datetime.now().isoformat(),
        "heartbeat_mode": "active",
        "activity_feed": [],
    }


def _save(state: dict):
    """Save coordination state to disk."""
    state["last_updated"] = datetime.now().isoformat()
    # Trim activity feed
    if len(state.get("activity_feed", [])) > MAX_FEED_ENTRIES:
        state["activity_feed"] = state["activity_feed"][-MAX_FEED_ENTRIES:]
    COORDINATION_FILE.parent.mkdir(parents=True, exist_ok=True)
    COORDINATION_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def get_mode() -> str:
    """Get the current heartbeat mode (active or sleep)."""
    state = _load()
    mode = state.get("heartbeat_mode", "active")
    # Backwards compat: treat old "scout"/"autonomous" as "active"
    if mode in ("scout", "autonomous"):
        return "active"
    return mode


def record_activity(source: str, action: str, summary: str,
                    tools_used: list[str] | None = None,
                    requires_attention: bool = False,
                    beat: int | None = None):
    """Record an activity to the shared feed."""
    state = _load()
    entry = {
        "timestamp": datetime.now().isoformat(),
        "source": source,
        "action": action,
        "summary": summary,
        "tools_used": tools_used or [],
        "requires_attention": requires_attention,
    }
    if beat is not None:
        entry["beat"] = beat
    state.setdefault("activity_feed", []).append(entry)
    _save(state)


def get_recent_activity(limit: int = 10) -> list[dict]:
    """Get the most recent activity feed entries."""
    state = _load()
    feed = state.get("activity_feed", [])
    return feed[-limit:]


def get_activity_summary() -> str:
    """Get a human-readable summary of recent activity for CLAUDE.md injection."""
    feed = get_recent_activity(15)
    if not feed:
        return "No recent heartbeat activity."

    lines = []
    for entry in feed:
        ts = entry.get("timestamp", "?")
        try:
            dt = datetime.fromisoformat(ts)
            time_str = dt.strftime("%H:%M")
        except (ValueError, TypeError):
            time_str = ts[:5]

        source = entry.get("source", "?")
        action = entry.get("action", "?")
        summary = entry.get("summary", "")
        attention = " [!]" if entry.get("requires_attention") else ""

        lines.append(f"- [{time_str}] {source}: {action} — {summary}{attention}")

    return "\n".join(lines)


# ============================================================
# Tool interface
# ============================================================

TOOL_DEFINITIONS = [
    {
        "name": "coordinate_heartbeat",
        "description": (
            "Manage the heartbeat. Read the activity feed, change mode (active/sleep), "
            "or clear the feed."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["read_feed", "set_mode", "clear_feed", "get_status"],
                    "description": (
                        "read_feed: See recent heartbeat activity. "
                        "set_mode: Change heartbeat mode (active/sleep). "
                        "clear_feed: Clear the activity feed. "
                        "get_status: Full coordination state overview."
                    ),
                },
                "mode": {
                    "type": "string",
                    "enum": ["active", "sleep"],
                    "description": (
                        "For set_mode: "
                        "active = normal operation (monitoring + creative drives). "
                        "sleep = skip beats entirely."
                    ),
                },
                "limit": {
                    "type": "integer",
                    "description": "For read_feed: max entries to return (default 10).",
                },
            },
            "required": ["action"],
        },
    },
]


async def _handle_coordinate_heartbeat(input_data: dict) -> str:
    action = input_data.get("action", "get_status")

    if action == "get_status":
        state = _load()
        mode = get_mode()
        feed_len = len(state.get("activity_feed", []))
        attention_count = sum(
            1 for e in state.get("activity_feed", [])
            if e.get("requires_attention")
        )
        return json.dumps({
            "mode": mode,
            "feed_entries": feed_len,
            "requires_attention": attention_count,
            "last_updated": state.get("last_updated"),
        }, indent=2)

    elif action == "read_feed":
        limit = input_data.get("limit", 10)
        feed = get_recent_activity(limit)
        if not feed:
            return "No activity recorded yet."
        return json.dumps(feed, indent=2)

    elif action == "set_mode":
        mode = input_data.get("mode", "active")
        if mode not in ("active", "sleep"):
            return f"Invalid mode: {mode}. Must be active or sleep."
        state = _load()
        old_mode = state.get("heartbeat_mode", "active")
        state["heartbeat_mode"] = mode
        _save(state)
        record_activity("claude_code", "mode_change",
                        f"Heartbeat mode: {old_mode} → {mode}")
        return f"Heartbeat mode changed: {old_mode} → {mode}"

    elif action == "clear_feed":
        state = _load()
        cleared = len(state.get("activity_feed", []))
        state["activity_feed"] = []
        _save(state)
        return f"Cleared {cleared} activity feed entries."

    else:
        return f"Unknown action: {action}"


TOOL_HANDLERS = {
    "coordinate_heartbeat": _handle_coordinate_heartbeat,
}
