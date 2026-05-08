"""Working Memory — Clawd's active cognitive state.

Provides a persistent JSON state file that tracks:
- current_task: What Clawd is actively working on (goal, plan, progress)
- scratch: Arbitrary key/value workspace for intermediate state
- pending_questions: Questions Clawd needs answered
- blocked_on: What's blocking current progress

Also auto-generates TODO.md from working memory state for human-readable tracking.
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import config

logger = logging.getLogger("clawd.tools.working_memory")

WORKING_MEMORY_FILE = config.MEMORY_DIR / "working_memory.json"
TODO_FILE = config.MEMORY_DIR / "TODO.md"

# Default empty state
_DEFAULT_STATE = {
    "current_task": None,
    "scratch": {},
    "pending_questions": [],
    "blocked_on": None,
    "last_updated": None,
    "curiosity_queue": [],  # list of {topic, score, source, reason, added_at}
}

# Task template
_DEFAULT_TASK = {
    "goal_id": None,
    "description": "",
    "plan": [],  # list of {step, status, notes}
    "current_step": 0,
    "started_at": None,
    "beats_spent": 0,
    "context": {},
}

TOOL_DEFINITIONS = [
    {
        "name": "working_memory",
        "description": (
            "Manage Clawd's active working memory — the cognitive scratchpad that persists across heartbeats. "
            "Track current task, plan steps, scratch notes, and blockers. "
            "Working memory auto-generates TODO.md for human-readable state tracking."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["get", "set", "clear", "get_task", "set_task", "clear_task",
                             "add_curiosity", "pop_curiosity", "list_curiosity"],
                    "description": (
                        "get: read a key from scratch or full state. "
                        "set: write a key/value to scratch. "
                        "clear: clear scratch or a specific key. "
                        "get_task: read current task state. "
                        "set_task: create or update the current task. "
                        "clear_task: mark current task as done and clear it. "
                        "add_curiosity: add a topic to the curiosity queue. "
                        "pop_curiosity: pop the highest-scored curiosity topic. "
                        "list_curiosity: list all queued curiosity topics."
                    ),
                },
                "key": {
                    "type": "string",
                    "description": "Key for get/set/clear scratch operations. Omit for full state.",
                },
                "value": {
                    "type": "string",
                    "description": "Value for set action (will be JSON-parsed if valid JSON, else stored as string).",
                },
                "description": {
                    "type": "string",
                    "description": "Task description (for set_task).",
                },
                "goal_id": {
                    "type": "integer",
                    "description": "Associated goal ID (for set_task).",
                },
                "plan": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "step": {"type": "string"},
                            "status": {
                                "type": "string",
                                "enum": ["pending", "in_progress", "done", "skipped"],
                            },
                            "notes": {"type": "string"},
                        },
                        "required": ["step"],
                    },
                    "description": "Plan steps for the task (for set_task). Each step has step text, status, optional notes.",
                },
                "current_step": {
                    "type": "integer",
                    "description": "Set current step index (for set_task update).",
                },
                "step_status": {
                    "type": "string",
                    "enum": ["pending", "in_progress", "done", "skipped"],
                    "description": "Update status of the current step (for set_task).",
                },
                "step_notes": {
                    "type": "string",
                    "description": "Add notes to the current step (for set_task).",
                },
                "context": {
                    "type": "object",
                    "description": "Task context dict to merge (for set_task).",
                },
                "question": {
                    "type": "string",
                    "description": "A pending question to add (for set action with key='question').",
                },
                "blocked_on": {
                    "type": "string",
                    "description": "What's blocking progress (for set action with key='blocked_on').",
                },
                "topic": {
                    "type": "string",
                    "description": "Curiosity topic to explore (for add_curiosity).",
                },
                "score": {
                    "type": "number",
                    "description": "Curiosity score 0-1 indicating priority (for add_curiosity). Default: 0.5.",
                },
                "source": {
                    "type": "string",
                    "description": "Source of curiosity (e.g., 'weak_category', 'knowledge_gap', 'heartbeat'). For add_curiosity.",
                },
                "reason": {
                    "type": "string",
                    "description": "Why this topic is interesting (for add_curiosity).",
                },
            },
            "required": ["action"],
        },
    },
]


def _load_state() -> dict:
    """Load working memory state from disk."""
    if WORKING_MEMORY_FILE.exists():
        try:
            return json.loads(WORKING_MEMORY_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Failed to load working memory: {e}")
    return dict(_DEFAULT_STATE)


def _save_state(state: dict):
    """Save working memory state to disk."""
    WORKING_MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    state["last_updated"] = datetime.now().isoformat()
    WORKING_MEMORY_FILE.write_text(json.dumps(state, indent=2, default=str), encoding="utf-8")


def _regenerate_todo(state: dict):
    """Regenerate TODO.md from working memory state.

    Format:
    - [x] Step 1 (done)
    - [ ] Step 2 (pending)
    - [>] Step 3 (in_progress)
    - [-] Step 4 (skipped)
    """
    lines = ["# Clawd Working Memory — TODO", ""]
    lines.append(f"*Last updated: {state.get('last_updated', 'unknown')}*")
    lines.append("")

    task = state.get("current_task")
    if task:
        lines.append("## Current Task")
        lines.append("")
        if task.get("goal_id"):
            lines.append(f"**Goal:** #{task['goal_id']}")
        lines.append(f"**Description:** {task.get('description', 'No description')}")
        lines.append(f"**Started:** {task.get('started_at', 'unknown')}")
        lines.append(f"**Beats spent:** {task.get('beats_spent', 0)}")
        lines.append("")

        plan = task.get("plan", [])
        if plan:
            lines.append("### Plan")
            lines.append("")
            current_step = task.get("current_step", 0)
            for i, step in enumerate(plan):
                status = step.get("status", "pending")
                marker = {
                    "done": "x",
                    "in_progress": ">",
                    "skipped": "-",
                    "pending": " ",
                }.get(status, " ")
                pointer = " ← current" if i == current_step and status != "done" else ""
                line = f"- [{marker}] {step['step']}{pointer}"
                if step.get("notes"):
                    line += f" — {step['notes']}"
                lines.append(line)
            lines.append("")

        ctx = task.get("context", {})
        if ctx:
            lines.append("### Context")
            lines.append("")
            for k, v in ctx.items():
                lines.append(f"- **{k}:** {v}")
            lines.append("")
    else:
        lines.append("## No Active Task")
        lines.append("")
        lines.append("*Use working_memory(action='set_task') to start a task.*")
        lines.append("")

    # Scratch notes
    scratch = state.get("scratch", {})
    if scratch:
        lines.append("## Scratch Notes")
        lines.append("")
        for k, v in scratch.items():
            lines.append(f"- **{k}:** {v}")
        lines.append("")

    # Pending questions
    questions = state.get("pending_questions", [])
    if questions:
        lines.append("## Pending Questions")
        lines.append("")
        for q in questions:
            lines.append(f"- {q}")
        lines.append("")

    # Blocked on
    blocked = state.get("blocked_on")
    if blocked:
        lines.append("## Blocked On")
        lines.append("")
        lines.append(f"**{blocked}**")
        lines.append("")

    TODO_FILE.parent.mkdir(parents=True, exist_ok=True)
    TODO_FILE.write_text("\n".join(lines), encoding="utf-8")


def increment_beats_spent():
    """Increment beats_spent counter on current task. Called by heartbeat."""
    state = _load_state()
    task = state.get("current_task")
    if task:
        task["beats_spent"] = task.get("beats_spent", 0) + 1
        _save_state(state)


def get_stall_count() -> int:
    """Return number of consecutive beats with no step progress.
    Used by heartbeat for stall detection."""
    state = _load_state()
    task = state.get("current_task")
    if not task:
        return 0
    # beats_spent minus completed steps gives a rough stall measure
    plan = task.get("plan", [])
    done_count = sum(1 for s in plan if s.get("status") == "done")
    beats = task.get("beats_spent", 0)
    # If beats > done steps + 2, we're stalling
    return max(0, beats - done_count - 2)


async def _working_memory(input_data: dict) -> str:
    """Handle working memory tool calls."""
    action = input_data["action"]
    state = _load_state()

    if action == "get":
        key = input_data.get("key")
        if key:
            value = state.get("scratch", {}).get(key)
            if value is not None:
                return json.dumps({"key": key, "value": value}, indent=2, default=str)
            return f"Key '{key}' not found in scratch."
        # Return full state
        return json.dumps(state, indent=2, default=str)

    elif action == "set":
        key = input_data.get("key")
        value_raw = input_data.get("value", "")

        # Handle special keys
        if key == "question" or input_data.get("question"):
            q = input_data.get("question") or value_raw
            if q:
                questions = state.get("pending_questions", [])
                questions.append(q)
                state["pending_questions"] = questions
                _save_state(state)
                _regenerate_todo(state)
                return f"Question added: {q}"
            return "Error: question text required."

        if key == "blocked_on" or input_data.get("blocked_on"):
            blocker = input_data.get("blocked_on") or value_raw
            state["blocked_on"] = blocker if blocker else None
            _save_state(state)
            _regenerate_todo(state)
            return f"Blocked on: {blocker}" if blocker else "Blocker cleared."

        if not key:
            return "Error: 'key' required for set action."

        # Parse value as JSON if possible
        try:
            value = json.loads(value_raw)
        except (json.JSONDecodeError, TypeError):
            value = value_raw

        scratch = state.get("scratch", {})
        scratch[key] = value
        state["scratch"] = scratch
        _save_state(state)
        _regenerate_todo(state)
        return f"Scratch['{key}'] = {json.dumps(value, default=str)}"

    elif action == "clear":
        key = input_data.get("key")
        if key:
            scratch = state.get("scratch", {})
            if key in scratch:
                del scratch[key]
                state["scratch"] = scratch
                _save_state(state)
                _regenerate_todo(state)
                return f"Cleared scratch key: {key}"
            return f"Key '{key}' not found."
        # Clear all scratch
        state["scratch"] = {}
        state["pending_questions"] = []
        state["blocked_on"] = None
        _save_state(state)
        _regenerate_todo(state)
        return "Scratch, questions, and blockers cleared."

    elif action == "get_task":
        task = state.get("current_task")
        if not task:
            return "No active task. Use set_task to start one."
        return json.dumps(task, indent=2, default=str)

    elif action == "set_task":
        task = state.get("current_task")

        if task is None:
            # Creating new task
            description = input_data.get("description", "")
            if not description:
                return "Error: 'description' required to create a task."

            plan_raw = input_data.get("plan", [])
            plan = []
            for step in plan_raw:
                plan.append({
                    "step": step.get("step", ""),
                    "status": step.get("status", "pending"),
                    "notes": step.get("notes", ""),
                })

            task = {
                "goal_id": input_data.get("goal_id"),
                "description": description,
                "plan": plan,
                "current_step": 0,
                "started_at": datetime.now().isoformat(),
                "beats_spent": 0,
                "context": input_data.get("context", {}),
            }
            state["current_task"] = task
            _save_state(state)
            _regenerate_todo(state)
            return f"Task created: {description}\nPlan: {len(plan)} steps"
        else:
            # Updating existing task
            updated = []

            if "description" in input_data:
                task["description"] = input_data["description"]
                updated.append("description")

            if "goal_id" in input_data:
                task["goal_id"] = input_data["goal_id"]
                updated.append("goal_id")

            if "plan" in input_data:
                plan_raw = input_data["plan"]
                task["plan"] = [
                    {"step": s.get("step", ""), "status": s.get("status", "pending"), "notes": s.get("notes", "")}
                    for s in plan_raw
                ]
                updated.append("plan")

            if "current_step" in input_data:
                task["current_step"] = int(input_data["current_step"])
                updated.append("current_step")

            if "step_status" in input_data:
                idx = task.get("current_step", 0)
                plan = task.get("plan", [])
                if 0 <= idx < len(plan):
                    plan[idx]["status"] = input_data["step_status"]
                    # Auto-advance: if marking done, move to next pending step
                    if input_data["step_status"] == "done":
                        for j in range(idx + 1, len(plan)):
                            if plan[j].get("status", "pending") == "pending":
                                task["current_step"] = j
                                plan[j]["status"] = "in_progress"
                                break
                    updated.append(f"step[{idx}].status={input_data['step_status']}")

            if "step_notes" in input_data:
                idx = task.get("current_step", 0)
                plan = task.get("plan", [])
                if 0 <= idx < len(plan):
                    plan[idx]["notes"] = input_data["step_notes"]
                    updated.append(f"step[{idx}].notes")

            if "context" in input_data:
                ctx = task.get("context", {})
                ctx.update(input_data["context"])
                task["context"] = ctx
                updated.append("context")

            state["current_task"] = task
            _save_state(state)
            _regenerate_todo(state)
            return f"Task updated: {', '.join(updated)}"

    elif action == "clear_task":
        task = state.get("current_task")
        if not task:
            return "No active task to clear."
        description = task.get("description", "unknown")
        beats = task.get("beats_spent", 0)
        state["current_task"] = None
        _save_state(state)
        _regenerate_todo(state)
        return f"Task cleared: '{description}' (spent {beats} beats)"

    elif action == "add_curiosity":
        topic = input_data.get("topic", "")
        if not topic:
            return "Error: 'topic' required for add_curiosity."
        queue = state.get("curiosity_queue", [])
        entry = {
            "topic": topic,
            "score": input_data.get("score", 0.5),
            "source": input_data.get("source", "manual"),
            "reason": input_data.get("reason", ""),
            "added_at": datetime.now().isoformat(),
        }
        queue.append(entry)
        # Sort by score descending
        queue.sort(key=lambda x: x.get("score", 0), reverse=True)
        # Cap at 20 items
        state["curiosity_queue"] = queue[:20]
        _save_state(state)
        return f"Curiosity added: '{topic}' (score: {entry['score']}, source: {entry['source']})"

    elif action == "pop_curiosity":
        queue = state.get("curiosity_queue", [])
        if not queue:
            return "Curiosity queue is empty."
        # Pop highest-scored item
        item = queue.pop(0)
        state["curiosity_queue"] = queue
        _save_state(state)
        return json.dumps(item, indent=2, default=str)

    elif action == "list_curiosity":
        queue = state.get("curiosity_queue", [])
        if not queue:
            return "Curiosity queue is empty."
        lines = [f"Curiosity queue ({len(queue)} items):"]
        for i, item in enumerate(queue):
            lines.append(
                f"  {i+1}. [{item.get('score', 0):.1f}] {item['topic']} "
                f"(source: {item.get('source', '?')}, reason: {item.get('reason', '')[:60]})"
            )
        return "\n".join(lines)

    return f"Unknown working_memory action: {action}"


TOOL_HANDLERS = {
    "working_memory": _working_memory,
}
