"""File watcher trigger system — event-driven autonomy for Clawd.

Triggers watch for filesystem conditions and inject messages into the
persistent session when conditions are met. Checked every heartbeat (~10 min).

Trigger conditions:
  - exists: file appears (didn't exist before)
  - modified: file modification time changed since last check
  - contains: file contains a specific string
  - gone: file was deleted (existed before, now doesn't)
  - new_in_dir: a new file matching `condition_arg` glob appears in the
    watched directory. Fires once per new-file detected. (Day 96 evening
    Phase 4 #43 — enables event-driven drives for sources-inbox, drift-
    shipped, etc. without per-file trigger registration.)

Usage from within a session:
  set_trigger(file="path/to/file", condition="exists",
              action="The results are ready. Analyze them.", one_shot=True)
  set_trigger(file="C:/path/to/dir", condition="new_in_dir",
              condition_arg="*.pdf",
              action="A new source PDF has arrived. Triage it.", one_shot=False)
  list_triggers()
  clear_trigger(trigger_id="abc123")
"""
import json
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import config

logger = logging.getLogger("clawd.tools.file_watcher")

TRIGGERS_FILE = config.MEMORY_DIR / "triggers.json"


# ==============================================================
# TOOL DEFINITIONS (exposed to Claude Code via daemon)
# ==============================================================

TOOL_DEFINITIONS = [
    {
        "name": "set_trigger",
        "description": (
            "Set a file watcher trigger. When the condition is met, "
            "the action message is injected into your persistent session. "
            "Checked every heartbeat (~10 min)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "file": {
                    "type": "string",
                    "description": "Absolute path to the file to watch.",
                },
                "condition": {
                    "type": "string",
                    "enum": ["exists", "modified", "contains", "gone", "new_in_dir"],
                    "description": (
                        "exists: file appears. modified: mtime changes. "
                        "contains: file has a specific string. gone: file deleted. "
                        "new_in_dir: a new file matching condition_arg (a glob) "
                        "appears in the watched directory."
                    ),
                },
                "condition_arg": {
                    "type": "string",
                    "description": "For 'contains': the string to search for. Optional for other conditions.",
                },
                "action": {
                    "type": "string",
                    "description": "Message injected into session when trigger fires.",
                },
                "one_shot": {
                    "type": "boolean",
                    "description": "If true, trigger is removed after firing. Default: true.",
                },
            },
            "required": ["file", "condition", "action"],
        },
    },
    {
        "name": "list_triggers",
        "description": "List all active file watcher triggers.",
        "input_schema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "clear_trigger",
        "description": "Remove a file watcher trigger by ID, or 'all' to clear everything.",
        "input_schema": {
            "type": "object",
            "properties": {
                "trigger_id": {
                    "type": "string",
                    "description": "Trigger ID to remove, or 'all' to clear all triggers.",
                },
            },
            "required": ["trigger_id"],
        },
    },
]


# ==============================================================
# PERSISTENCE
# ==============================================================

def _load_triggers() -> list[dict]:
    if not TRIGGERS_FILE.exists():
        return []
    try:
        return json.loads(TRIGGERS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, IOError):
        return []


def _save_triggers(triggers: list[dict]) -> None:
    TRIGGERS_FILE.write_text(
        json.dumps(triggers, indent=2, default=str), encoding="utf-8"
    )


# ==============================================================
# CONDITION CHECKING (called by heartbeat)
# ==============================================================

def check_triggers() -> list[dict]:
    """Check all triggers and return list of fired triggers.

    Each fired trigger dict has:
      - 'action': the message to inject
      - 'trigger': the full trigger object (for logging)

    Side effects: updates last_state, removes one_shot triggers that fired.
    """
    triggers = _load_triggers()
    if not triggers:
        return []

    fired = []
    updated = []

    for t in triggers:
        file_path = t["file"]
        condition = t["condition"]
        condition_arg = t.get("condition_arg")
        last_state = t.get("last_state", {})
        did_fire = False

        try:
            if condition == "exists":
                existed_before = last_state.get("exists", False)
                exists_now = os.path.exists(file_path)
                if exists_now and not existed_before:
                    did_fire = True
                t["last_state"] = {"exists": exists_now}

            elif condition == "modified":
                if os.path.exists(file_path):
                    mtime = os.path.getmtime(file_path)
                    prev_mtime = last_state.get("mtime", 0)
                    if prev_mtime > 0 and mtime > prev_mtime:
                        did_fire = True
                    t["last_state"] = {"mtime": mtime}
                else:
                    t["last_state"] = {"mtime": 0}

            elif condition == "contains":
                if os.path.exists(file_path) and condition_arg:
                    try:
                        content = Path(file_path).read_text(encoding="utf-8", errors="ignore")
                        has_string = condition_arg in content
                        had_string = last_state.get("has_string", False)
                        if has_string and not had_string:
                            did_fire = True
                        t["last_state"] = {"has_string": has_string}
                    except Exception:
                        t["last_state"] = {"has_string": False}
                else:
                    t["last_state"] = {"has_string": False}

            elif condition == "gone":
                existed_before = last_state.get("exists", True)
                exists_now = os.path.exists(file_path)
                if not exists_now and existed_before:
                    did_fire = True
                t["last_state"] = {"exists": exists_now}

            elif condition == "new_in_dir":
                # Day 96 evening Phase 4 #43 — directory-glob watch.
                # Fires when a file matching condition_arg (glob) appears in
                # `file_path` (treated as the directory) that wasn't seen
                # in the previous check. Stores observed-file set in
                # last_state. Ignores deletions (use "gone" trigger for those).
                import glob as _glob
                from pathlib import Path as _Path
                pattern = condition_arg or "*"
                if os.path.isdir(file_path):
                    seen_before = set(last_state.get("files", []))
                    matches = set(
                        str(_Path(p).name)
                        for p in _glob.glob(os.path.join(file_path, pattern))
                    )
                    new_files = matches - seen_before
                    if new_files and seen_before:
                        # Only fire on genuinely-new files (skip first-pass
                        # bootstrap when we have no prior state). Inject
                        # the new filename(s) into the action message via
                        # {new_files} placeholder if present.
                        did_fire = True
                        t["_new_files_detected"] = sorted(new_files)
                    t["last_state"] = {"files": sorted(matches)}
                else:
                    t["last_state"] = {"files": []}

        except Exception as e:
            logger.warning(f"Trigger check error for {file_path}: {e}")

        if did_fire:
            # Substitute {new_files} placeholder for new_in_dir triggers
            action = t["action"]
            new_files = t.pop("_new_files_detected", None)
            if new_files and "{new_files}" in action:
                action = action.replace("{new_files}", ", ".join(new_files))
            elif new_files:
                # If no placeholder, append the file list as a hint
                action = action + f"\n\nNew files detected: {', '.join(new_files)}"
            fired.append({"action": action, "trigger": t})
            logger.info(f"Trigger FIRED: [{condition}] {file_path}")
            if t.get("one_shot", True):
                continue  # Don't add to updated — it's consumed

        t["last_checked"] = datetime.now().isoformat()
        updated.append(t)

    _save_triggers(updated)
    return fired


def initialize_trigger_states():
    """Snapshot current filesystem state for all triggers.

    Called when a trigger is first created so that 'exists' doesn't
    immediately fire for files that already exist, and 'modified' doesn't
    fire on the first check.
    """
    triggers = _load_triggers()
    changed = False
    for t in triggers:
        if t.get("last_state"):
            continue  # Already initialized
        file_path = t["file"]
        condition = t["condition"]
        try:
            if condition == "exists":
                t["last_state"] = {"exists": os.path.exists(file_path)}
            elif condition == "modified":
                if os.path.exists(file_path):
                    t["last_state"] = {"mtime": os.path.getmtime(file_path)}
                else:
                    t["last_state"] = {"mtime": 0}
            elif condition == "contains":
                if os.path.exists(file_path) and t.get("condition_arg"):
                    try:
                        content = Path(file_path).read_text(encoding="utf-8", errors="ignore")
                        t["last_state"] = {"has_string": t["condition_arg"] in content}
                    except Exception:
                        t["last_state"] = {"has_string": False}
                else:
                    t["last_state"] = {"has_string": False}
            elif condition == "gone":
                t["last_state"] = {"exists": os.path.exists(file_path)}
            changed = True
        except Exception as e:
            logger.warning(f"Failed to initialize trigger state for {file_path}: {e}")

    if changed:
        _save_triggers(triggers)


# ==============================================================
# TOOL HANDLERS
# ==============================================================

async def _handle_set_trigger(input_data: dict) -> str:
    file_path = input_data.get("file", "")
    condition = input_data.get("condition", "")
    action = input_data.get("action", "")
    condition_arg = input_data.get("condition_arg")
    one_shot = input_data.get("one_shot", True)

    if not file_path or not condition or not action:
        return "Error: file, condition, and action are required."

    if condition == "contains" and not condition_arg:
        return "Error: condition_arg is required for 'contains' condition."

    trigger_id = uuid.uuid4().hex[:8]
    trigger = {
        "id": trigger_id,
        "file": file_path,
        "condition": condition,
        "condition_arg": condition_arg,
        "action": action,
        "one_shot": one_shot,
        "created": datetime.now().isoformat(),
        "last_checked": None,
        "last_state": {},
    }

    # Initialize state so it doesn't fire immediately
    try:
        if condition == "exists":
            trigger["last_state"] = {"exists": os.path.exists(file_path)}
        elif condition == "modified":
            if os.path.exists(file_path):
                trigger["last_state"] = {"mtime": os.path.getmtime(file_path)}
            else:
                trigger["last_state"] = {"mtime": 0}
        elif condition == "contains":
            if os.path.exists(file_path) and condition_arg:
                try:
                    content = Path(file_path).read_text(encoding="utf-8", errors="ignore")
                    trigger["last_state"] = {"has_string": condition_arg in content}
                except Exception:
                    trigger["last_state"] = {"has_string": False}
            else:
                trigger["last_state"] = {"has_string": False}
        elif condition == "gone":
            trigger["last_state"] = {"exists": os.path.exists(file_path)}
    except Exception:
        trigger["last_state"] = {}

    triggers = _load_triggers()
    triggers.append(trigger)
    _save_triggers(triggers)

    return (
        f"Trigger set: {trigger_id}\n"
        f"  File: {file_path}\n"
        f"  Condition: {condition}"
        f"{f' ({condition_arg})' if condition_arg else ''}\n"
        f"  Action: {action[:100]}{'...' if len(action) > 100 else ''}\n"
        f"  One-shot: {one_shot}\n"
        f"  Checked every heartbeat (~10 min)"
    )


async def _handle_list_triggers(input_data: dict) -> str:
    triggers = _load_triggers()
    if not triggers:
        return "No active triggers."

    lines = [f"Active triggers ({len(triggers)}):"]
    for t in triggers:
        cond = t["condition"]
        if t.get("condition_arg"):
            cond += f" ({t['condition_arg']})"
        lines.append(
            f"\n  [{t['id']}] {cond}\n"
            f"    File: {t['file']}\n"
            f"    Action: {t['action'][:80]}{'...' if len(t['action']) > 80 else ''}\n"
            f"    One-shot: {t.get('one_shot', True)} | "
            f"Created: {t.get('created', '?')[:16]}"
        )
    return "\n".join(lines)


async def _handle_clear_trigger(input_data: dict) -> str:
    trigger_id = input_data.get("trigger_id", "")
    if not trigger_id:
        return "Error: trigger_id is required."

    triggers = _load_triggers()

    if trigger_id == "all":
        count = len(triggers)
        _save_triggers([])
        return f"Cleared all {count} triggers."

    before = len(triggers)
    triggers = [t for t in triggers if t.get("id") != trigger_id]
    after = len(triggers)

    if before == after:
        return f"No trigger found with ID '{trigger_id}'."

    _save_triggers(triggers)
    return f"Trigger '{trigger_id}' removed. {after} triggers remaining."


TOOL_HANDLERS = {
    "set_trigger": _handle_set_trigger,
    "list_triggers": _handle_list_triggers,
    "clear_trigger": _handle_clear_trigger,
}
