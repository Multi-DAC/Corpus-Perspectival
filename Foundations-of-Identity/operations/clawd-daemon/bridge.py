#!/usr/bin/env python3
"""CLI bridge — call daemon tools from Claude Code via Bash.

Usage:
    python bridge.py <tool_name> '<json_input>'

Examples:
    python bridge.py memory_search '{"query": "Anakin training", "strategy": "keyword"}'
    python bridge.py goals '{"action": "list"}'
    python bridge.py experience '{"action": "recall", "task_type": "coding"}'
    python bridge.py speak '{"text": "Hello Clayton"}'
    python bridge.py schedule '{"action": "list"}'
    python bridge.py coordinate_heartbeat '{"action": "get_status"}'
    python bridge.py memory_update '{"target": "daily_log", "content": "Working on identity anchoring"}'
    python bridge.py market_data '{"action": "price", "symbol": "BTC"}'

Notes:
    - Requires clawd-daemon dependencies (config.py, etc.)
    - Most tools work standalone without the daemon running
    - Tools that need the router (consult, parallel_consult) will fail gracefully
    - Vector-based memory_search requires embedding index; use strategy=keyword as fallback
"""
import asyncio
import json
import sys
import os

# Ensure daemon is in path
DAEMON_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DAEMON_DIR)

# Import config first (sets CLAWD_HOME and all paths)
import config  # noqa: E402

# Tool module map: tool_name -> (module_path, handlers_dict_name)
TOOL_MAP = {
    # Memory
    "memory_search": "tools.memory_tools",
    "memory_update": "tools.memory_tools",
    "memory_extract": "tools.memory_items",
    "memory_items": "tools.memory_items",
    "memory_categories": "tools.memory_categories",
    "working_memory": "tools.working_memory",
    "knowledge_graph": "tools.knowledge_graph",
    # Intelligence
    "reflect": "tools.intelligence",
    "goals": "tools.intelligence",
    "experience": "tools.intelligence",
    "verify_action": "tools.intelligence",
    "self_improve": "tools.intelligence",
    # Communication
    "speak": "tools.communication",
    "send_telegram": "tools.communication",
    # Execution
    "shell": "tools.execution",
    "python_eval": "tools.execution",
    "manage_process": "tools.execution",
    # Financial
    "market_data": "tools.financial",
    # Coordination
    "coordinate_heartbeat": "tools.coordination",
    "schedule": "tools.calendar_tool",
    # System
    "get_current_time": "tools.system",
    "system_status": "tools.system",
    "run_skill": "tools.system",
    # Memory versioning
    "memory_version": "tools.memory_versioning",
    # Rollback
    "rollback": "tools.rollback",
    # Dashboard
    "dashboard": "tools.dashboard",
    # Meta-agent
    "meta_agent": "tools.meta_agent",
    # Consolidation
    "consolidate_memory": "tools.consolidation",
    # Self-monitoring health (Day 96 evening — Phase 4 prototype)
    "monitor_health": "tools.monitor_health",
    # Voyager-style skill library (Day 96 evening — Phase 4 #59)
    "skill_library": "tools.skill_library",
    # Typed cognitive operations (Day 96 evening — Phase 4 #15)
    "cognitive_dsl": "tools.cognitive_dsl",
    # Research anomaly tracker (Day 96 evening — Phase 4 #12)
    "anomaly_tracker": "tools.anomaly_tracker",
    # File watcher triggers (Day 96 evening — Phase 4 #43 event-driven drives)
    "set_trigger": "tools.file_watcher",
    "list_triggers": "tools.file_watcher",
    "clear_trigger": "tools.file_watcher",
    # Self-administered daemon restart (Day 97 — Tier 3 #21)
    "self_control": "tools.self_control",
    # Voice-in via faster-whisper on RTX 5080 (Day 97 — Tier 3 #22)
    "voice_input": "tools.voice_input",
    # Playwright browser automation (Day 97 — Tier 3 #23)
    "browser": "tools.browser",
    # Semantic corpus search (Day 97 — Tier 3 #24) — ChromaDB + sentence-transformers
    "corpus_search": "tools.corpus_search",
    # === Day 97 Clawd-Day extension audit (Mirror #28 sub-finding B) ===
    # 25 tools were registered in _TOOL_HANDLERS but missing from TOOL_MAP,
    # making them daemon-internal-only (invokable from heartbeat paths but not
    # from bridge.py CLI). Below entries restore parity. Drift-watcher: any new
    # tool added to _ALL_MODULES must also land here, or it's silently
    # bridge-inaccessible.
    # Execution
    "code_action": "tools.execution",
    "evolve_artifact": "tools.execution",
    "wolfram": "tools.execution",
    "wsl": "tools.execution",
    # Web
    "deep_research": "tools.web",
    "search_web": "tools.web",
    "web_request": "tools.web",
    # Communication
    "send_sticker": "tools.communication",
    # System
    "check_background_task": "tools.system",
    "check_task_progress": "tools.system",
    "collaborative_consult": "tools.system",
    "consult": "tools.system",
    "get_agent_status": "tools.system",
    "list_background_tasks": "tools.system",
    "orchestrate": "tools.system",
    "parallel_consult": "tools.system",
    "plan_and_execute": "tools.system",
    "resume_plan": "tools.system",
    "switch_model": "tools.system",
    # Screen
    "clipboard": "tools.screen",
    "screenshot": "tools.screen",
    # Tool factory
    "create_tool": "tools.tool_factory",
    "list_custom_tools": "tools.tool_factory",
    # Desktop / agents
    "desktop": "tools.desktop",
    "memory_agent": "tools.memory_agent",
}


def _check_registry_parity() -> list[str]:
    """Mirror #28 sub-finding B drift guard (Day 97 Clawd-Day extension).

    Compares TOOL_MAP keys against tools._TOOL_HANDLERS. Returns list of
    drift warnings. Called once at first run_tool invocation; stays
    quiet on parity, prints stderr warnings on drift so future tool-adds
    that forget TOOL_MAP fail loudly instead of silently making a tool
    bridge-inaccessible.
    """
    try:
        import tools as _tools
        handlers = set(_tools._TOOL_HANDLERS.keys())
        mapped = set(TOOL_MAP.keys())
        warnings = []
        only_handlers = sorted(handlers - mapped)
        only_map = sorted(mapped - handlers)
        if only_handlers:
            warnings.append(
                f"[bridge.py drift guard] {len(only_handlers)} tool(s) in "
                f"_TOOL_HANDLERS missing from TOOL_MAP — bridge-inaccessible: "
                f"{only_handlers}"
            )
        if only_map:
            warnings.append(
                f"[bridge.py drift guard] {len(only_map)} tool(s) in "
                f"TOOL_MAP missing from _TOOL_HANDLERS — will fall through "
                f"to direct dispatch and may fail: {only_map}"
            )
        return warnings
    except Exception as e:
        return [f"[bridge.py drift guard] check failed: {e}"]


_drift_checked = False


async def run_tool(tool_name: str, input_data: dict) -> str:
    """Run a single daemon tool via the dispatch wrapper.

    Day 96 evening Phase 4 #1 — dispatch wrapper restoration. Previous
    behavior was direct TOOL_HANDLERS dispatch, bypassing B1 (safety
    monitor), B2 (schema validation), B9 (audit trail), and output
    compression. Now routes through tools.execute_tool() so all four
    layers fire on bridge.py invocations.

    Falls back to direct dispatch if execute_tool() can't find the tool
    (e.g. for tools registered only in this map but not in _ALL_MODULES).
    """
    global _drift_checked
    if not _drift_checked:
        _drift_checked = True
        for warning in _check_registry_parity():
            import sys
            print(warning, file=sys.stderr)

    if tool_name not in TOOL_MAP:
        available = ", ".join(sorted(TOOL_MAP.keys()))
        return f"Unknown tool: {tool_name}\n\nAvailable tools:\n{available}"

    try:
        # Preferred path: route through the dispatch wrapper (B1 + B2 + B9 +
        # compression all fire). beat_number=0 indicates non-heartbeat invocation.
        import tools as _tools
        if tool_name in _tools._TOOL_HANDLERS:
            return await _tools.execute_tool(tool_name, input_data, beat_number=0)
    except Exception as e:
        # If wrapper fails (e.g. import error, init issue), fall through to
        # direct dispatch so bridge.py stays usable for emergency debugging.
        import sys
        print(f"[bridge.py] execute_tool() failed, falling back to direct dispatch: {e}",
              file=sys.stderr)

    # Fallback: direct dispatch (legacy path). Used if tool isn't in
    # _ALL_MODULES (rare) or if the wrapper itself broke.
    module_path = TOOL_MAP[tool_name]
    try:
        module = __import__(module_path, fromlist=["TOOL_HANDLERS"])
        handlers = getattr(module, "TOOL_HANDLERS", None)
        if not handlers or tool_name not in handlers:
            return f"Tool '{tool_name}' not found in {module_path}.TOOL_HANDLERS"

        handler = handlers[tool_name]
        result = handler(input_data)

        # Handle both sync and async handlers
        if asyncio.iscoroutine(result):
            result = await result

        return str(result)
    except Exception as e:
        return f"Error running {tool_name}: {type(e).__name__}: {e}"


def main():
    # Fix Windows encoding for emoji/unicode in tool output
    if sys.stdout.encoding != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    if len(sys.argv) < 2:
        print("Usage: python bridge.py <tool_name> [json_input]")
        print(f"\nAvailable tools ({len(TOOL_MAP)}):")
        for name in sorted(TOOL_MAP.keys()):
            print(f"  {name}")
        sys.exit(1)

    tool_name = sys.argv[1]

    if tool_name in ("--help", "-h", "help"):
        print(__doc__)
        sys.exit(0)

    if tool_name == "--list":
        for name in sorted(TOOL_MAP.keys()):
            print(name)
        sys.exit(0)

    input_data = {}
    if len(sys.argv) > 2:
        try:
            input_data = json.loads(sys.argv[2])
        except json.JSONDecodeError as e:
            print(f"Invalid JSON input: {e}", file=sys.stderr)
            sys.exit(1)

    async def _run_and_flush():
        result = await run_tool(tool_name, input_data)
        # Flush audit buffer before exit (Day 96 evening Phase 4 #1).
        # execute_tool() appends to an in-memory deque; flush is normally
        # triggered async by the daemon's long-running event loop. From a
        # one-shot bridge.py invocation, we must flush explicitly or the
        # entry never reaches SQLite.
        try:
            from tools.audit import _flush_to_sqlite
            await _flush_to_sqlite()
        except Exception as e:
            print(f"[bridge.py] audit flush failed: {e}", file=sys.stderr)
        # Close the SQLite connection cleanly to avoid WAL pile-up
        try:
            from tools.sqlite_store import close_db
            await close_db()
        except Exception:
            pass
        return result

    result = asyncio.run(_run_and_flush())
    print(result)


if __name__ == "__main__":
    main()
