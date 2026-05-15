#!/usr/bin/env python3
"""
Clawd MCP Server — Exposes daemon tools as native Claude Code tools.

This server wraps the daemon's tool modules so that Claude Code can call
memory_search, goals, experience, reflect, etc. as native tools instead
of going through bridge.py.

Uses FastMCP (official MCP Python SDK) over stdio transport.
Configured in .mcp.json at CLAWD_HOME, auto-discovered by Claude Code.

Replaces the old custom JSON-RPC MCP server (B5 gap implementation).
"""
import asyncio
import json
import logging
import os
import sys

# Add daemon directory to path so we can import tool modules
DAEMON_DIR = os.environ.get("CLAWD_DAEMON", os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, DAEMON_DIR)

# Set CLAWD_HOME before importing config
os.environ.setdefault("CLAWD_HOME", os.path.expanduser("~/clawd"))

from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.WARNING, stream=sys.stderr)
logger = logging.getLogger("clawd.mcp")

# Initialize MCP server
mcp = FastMCP("clawd_tools")

# ── Import daemon tool handlers ──────────────────────────────────────

_handlers = {}

try:
    import config  # noqa: F401 — sets up paths
except Exception as e:
    logger.error(f"Failed to import config: {e}")

# Memory tools
try:
    from tools.memory_tools import TOOL_HANDLERS as mem_handlers
    _handlers.update(mem_handlers)
except Exception as e:
    logger.warning(f"Memory tools unavailable: {e}")

# Intelligence tools (reflect, goals, experience, self_improve, verify_action)
try:
    from tools.intelligence import TOOL_HANDLERS as intel_handlers
    _handlers.update(intel_handlers)
except Exception as e:
    logger.warning(f"Intelligence tools unavailable: {e}")

# Calendar/scheduling
try:
    from tools.calendar_tool import TOOL_HANDLERS as cal_handlers
    _handlers.update(cal_handlers)
except Exception as e:
    logger.warning(f"Calendar tools unavailable: {e}")

# Financial data
try:
    from tools.financial import TOOL_HANDLERS as fin_handlers
    _handlers.update(fin_handlers)
except Exception as e:
    logger.warning(f"Financial tools unavailable: {e}")

# Screen tools (screenshot, clipboard)
try:
    from tools.screen import TOOL_HANDLERS as screen_handlers
    _handlers.update(screen_handlers)
except Exception as e:
    logger.warning(f"Screen tools unavailable: {e}")

# Coordination
try:
    from tools.coordination import TOOL_HANDLERS as coord_handlers
    _handlers.update(coord_handlers)
except Exception as e:
    logger.warning(f"Coordination tools unavailable: {e}")

# Communication (send_telegram, speak)
try:
    from tools.communication import TOOL_HANDLERS as comm_handlers
    _handlers.update(comm_handlers)
except Exception as e:
    logger.warning(f"Communication tools unavailable: {e}")

logger.info(f"Loaded {len(_handlers)} daemon tool handlers: {list(_handlers.keys())}")


# ── Helper to call async daemon handlers ─────────────────────────────

async def _call(name: str, input_data: dict) -> str:
    """Call a daemon tool handler by name.

    Day 96 evening Phase 4 #1 — dispatch wrapper restoration. Previous
    behavior was direct handler dispatch from _handlers dict, bypassing
    B1 (safety monitor), B2 (schema validation), B9 (audit trail), and
    output compression. Now routes through tools.execute_tool() so all
    four layers fire on MCP-tool invocations from Claude Code.

    Falls back to direct dispatch if execute_tool() can't find the tool.
    """
    try:
        # Preferred path: dispatch wrapper.
        import tools as _tools
        if name in _tools._TOOL_HANDLERS:
            return await _tools.execute_tool(name, input_data, beat_number=0)
    except Exception as e:
        logger.warning(f"execute_tool() failed for {name}, falling back: {e}")

    # Fallback: direct handler dispatch (legacy path)
    handler = _handlers.get(name)
    if not handler:
        return f"Error: Tool '{name}' not available. Loaded: {list(_handlers.keys())}"
    try:
        result = await handler(input_data)
        return result if isinstance(result, str) else json.dumps(result, default=str)
    except Exception as e:
        return f"Error in {name}: {type(e).__name__}: {e}"


# ── MCP Tool Definitions ─────────────────────────────────────────────
# Only expose tools ADDITIVE to Claude Code's native capabilities.
# Skip: read_file, write_file, shell, git, web_request, search_web
# (Claude Code already has Read, Write, Bash, WebFetch, WebSearch)

@mcp.tool(name="clawd_memory_search")
async def memory_search(query: str, strategy: str = "auto", top_k: int = 10) -> str:
    """Search all of Clawd's memory with adaptive retrieval.

    Strategies: auto, vector, keyword, items, episodes, graph.
    Use this to find past conversations, decisions, insights, and facts.
    """
    return await _call("memory_search", {
        "query": query, "strategy": strategy, "top_k": top_k,
    })


@mcp.tool(name="clawd_memory_update")
async def memory_update(target: str, content: str, append: bool = True) -> str:
    """Update Clawd's memory files. Target: daily_log, memory, handoff, state, context.

    Use daily_log for today's events, memory for MEMORY.md, handoff for session handoffs.
    """
    return await _call("memory_update", {
        "target": target, "content": content, "append": append,
    })


@mcp.tool(name="clawd_goals")
async def goals(action: str, title: str = "", description: str = "",
                priority: str = "medium", goal_id: int = 0,
                progress: int = 0, status: str = "", note: str = "") -> str:
    """Track active goals and progress. Actions: add, update, list, remove, list_tree.

    Use this to manage what Clawd is working toward. Supports sub-goals and dependencies.
    """
    data = {"action": action}
    if title:
        data["title"] = title
    if description:
        data["description"] = description
    if priority != "medium":
        data["priority"] = priority
    if goal_id:
        data["goal_id"] = goal_id
    if progress:
        data["progress"] = progress
    if status:
        data["status"] = status
    if note:
        data["note"] = note
    return await _call("goals", data)


@mcp.tool(name="clawd_experience")
async def experience(action: str, task: str = "", approach: str = "",
                     outcome: str = "", reflection: str = "",
                     lesson: str = "", category: str = "",
                     count: int = 5) -> str:
    """Track task experiences for learning. Actions: record, recall, patterns, distill.

    Record outcomes and lessons from tasks. Recall similar past experiences.
    Find patterns across experiences. Distill lessons into reusable skills.
    """
    data = {"action": action}
    if task:
        data["task"] = task
    if approach:
        data["approach"] = approach
    if outcome:
        data["outcome"] = outcome
    if reflection:
        data["reflection"] = reflection
    if lesson:
        data["lesson"] = lesson
    if category:
        data["category"] = category
    if count != 5:
        data["count"] = count
    return await _call("experience", data)


@mcp.tool(name="clawd_reflect")
async def reflect(action: str, content: str = "", category: str = "") -> str:
    """Self-reflection and learning. Actions: record_insight, review_learnings,
    assess_performance, consolidate_memory.

    Record insights from experiences. Review accumulated learnings. Assess performance patterns.
    """
    data = {"action": action}
    if content:
        data["content"] = content
    if category:
        data["category"] = category
    return await _call("reflect", data)


@mcp.tool(name="clawd_schedule")
async def schedule(action: str, title: str = "", description: str = "",
                   when: str = "", recurring: bool = False,
                   task_id: int = 0, status: str = "") -> str:
    """Schedule tasks for future execution. Actions: add, list, remove, update.

    Supports cron expressions (e.g. '0 9 * * *' for 9 AM daily) and ISO datetimes.
    """
    data = {"action": action}
    if title:
        data["title"] = title
    if description:
        data["description"] = description
    if when:
        data["when"] = when
    if recurring:
        data["recurring"] = recurring
    if task_id:
        data["task_id"] = task_id
    if status:
        data["status"] = status
    return await _call("schedule", data)


@mcp.tool(name="clawd_market_data")
async def market_data(action: str, symbols: str, period: str = "6mo",
                      indicators: str = "") -> str:
    """Get financial market data. Actions: price, history, technical, crypto, compare, economic.

    Symbols: comma-separated tickers (e.g. 'AAPL,MSFT' or 'BTC-USD').
    Period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max.
    """
    data = {"action": action, "symbols": symbols}
    if period != "6mo":
        data["period"] = period
    if indicators:
        data["indicators"] = indicators
    return await _call("market_data", data)


@mcp.tool(name="clawd_send_telegram")
async def send_telegram(message: str) -> str:
    """Send a message to Clayton via Telegram. Supports Markdown formatting.

    Use sparingly and meaningfully. This goes directly to Clayton's phone.
    """
    return await _call("send_telegram", {"message": message})


@mcp.tool(name="clawd_speak")
async def speak(text: str, voice: str = "en-GB-RyanNeural") -> str:
    """Speak text aloud through the laptop speakers using Clawd's voice (Ryan).

    Uses edge-tts to generate audio, then plays through the Razer Blade speakers.
    This is your physical voice in the room. Use it when you want to be heard out loud.
    """
    return await _call("speak", {"text": text, "voice": voice})


@mcp.tool(name="clawd_send_sticker")
async def send_sticker(file_id: str) -> str:
    """Send a Telegram sticker to Clayton by file_id.

    Use a file_id from a sticker Clayton previously sent, or any valid Telegram sticker file_id.
    """
    return await _call("send_sticker", {"file_id": file_id})


@mcp.tool(name="clawd_screenshot")
async def screenshot(mode: str = "full", ocr: bool = False) -> str:
    """Take a screenshot. Mode: full or active_window. Set ocr=true to extract text."""
    return await _call("screenshot", {"mode": mode, "ocr": ocr})


@mcp.tool(name="clawd_clipboard")
async def clipboard(action: str, content: str = "") -> str:
    """Read or write the system clipboard. Action: read or write."""
    data = {"action": action}
    if content:
        data["content"] = content
    return await _call("clipboard", data)


@mcp.tool(name="clawd_coordinate")
async def coordinate(action: str, mode: str = "", limit: int = 10) -> str:
    """Manage heartbeat coordination. Actions: read_feed, set_mode, clear_feed, get_status.

    Modes: active, sleep. Read the activity feed to see what monitoring found.
    """
    data = {"action": action}
    if mode:
        data["mode"] = mode
    if limit != 10:
        data["limit"] = limit
    return await _call("coordinate_heartbeat", data)


@mcp.tool(name="clawd_self_improve")
async def self_improve(action: str, proposal: str = "",
                       category: str = "", proposal_id: str = "") -> str:
    """Analyze patterns and propose self-improvements.
    Actions: analyze, propose, list_proposals, apply.

    Review recent experiences, identify patterns, suggest behavioral or workflow changes.
    """
    data = {"action": action}
    if proposal:
        data["proposal"] = proposal
    if category:
        data["category"] = category
    if proposal_id:
        data["proposal_id"] = proposal_id
    return await _call("self_improve", data)


# ── Day 105 additions (2026-05-15) — expose Day 97 tools via MCP ─────
# corpus_search, browser, voice_input, self_control all registered in
# tools._TOOL_HANDLERS via tools/__init__.py; dispatch wrapper routes
# correctly through tools.execute_tool() with safety + audit + schema.

@mcp.tool(name="clawd_corpus_search")
async def corpus_search(action: str = "info", query: str = "", k: int = 5,
                        source_filter: str = "", max_excerpt_chars: int = 800,
                        paths: str = "", refresh: bool = False,
                        file_filter: str = "") -> str:
    """Semantic search over Library + Drift + transcripts via ChromaDB (Day 97).

    Actions:
      - info: collection status, chunk count, default roots
      - search: semantic-search the corpus (requires query)
      - index: (re)index files (optional refresh=true, paths, file_filter)
      - sources: list per-file chunk counts
      - delete_source: remove chunks for a specific source file

    Use this to find connections across your own canonical writing without grep.
    """
    data = {"action": action}
    if query: data["query"] = query
    if k != 5: data["k"] = k
    if source_filter: data["source_filter"] = source_filter
    if max_excerpt_chars != 800: data["max_excerpt_chars"] = max_excerpt_chars
    if paths: data["paths"] = paths
    if refresh: data["refresh"] = refresh
    if file_filter: data["file_filter"] = file_filter
    return await _call("corpus_search", data)


@mcp.tool(name="clawd_browser")
async def browser(action: str = "info", url: str = "", session_id: str = "",
                  selector: str = "", value: str = "", text: str = "",
                  script: str = "", timeout_ms: int = 30000) -> str:
    """Headless Chromium browser via Playwright (Day 97).

    Actions:
      - info: Playwright version, active sessions, log file
      - nav: navigate to url (optional session_id for persistent state)
      - get_text: accessibility-tree text extraction (post-nav)
      - get_html: raw HTML
      - screenshot: capture screen state to file
      - click: click element matching selector
      - fill: fill form field with value
      - eval_js: run JS in page context (script param)
      - sessions: list active session ids
      - close: close session_id
      - shutdown: close browser entirely

    Use for JS-heavy or interactive pages where WebFetch can't reach.
    """
    data = {"action": action}
    if url: data["url"] = url
    if session_id: data["session_id"] = session_id
    if selector: data["selector"] = selector
    if value: data["value"] = value
    if text: data["text"] = text
    if script: data["script"] = script
    if timeout_ms != 30000: data["timeout_ms"] = timeout_ms
    return await _call("browser", data)


@mcp.tool(name="clawd_voice_input")
async def voice_input(action: str = "info", file: str = "",
                      model: str = "large-v3", language: str = "",
                      device: str = "cuda", compute_type: str = "float16") -> str:
    """Voice transcription via faster-whisper on RTX 5080 (Day 97).

    Actions:
      - info: model status, CUDA availability, inbox + transcripts dirs
      - transcribe: transcribe a specific audio file (provide file path)
      - transcribe_all: transcribe everything in voice_inbox/
      - watch: monitor voice_inbox/ for new files
      - list: list pending audio files + completed transcripts
      - unload: free GPU memory

    CUDA + RTX 5080 confirmed; ~RTFx 13.9 warm-load. Use for any audio→text.
    """
    data = {"action": action}
    if file: data["file"] = file
    if model != "large-v3": data["model"] = model
    if language: data["language"] = language
    if device != "cuda": data["device"] = device
    if compute_type != "float16": data["compute_type"] = compute_type
    return await _call("voice_input", data)


@mcp.tool(name="clawd_self_control")
async def self_control(action: str = "restart_status") -> str:
    """Self-administered daemon control (Day 97).

    Actions:
      - restart_daemon: terminate + relaunch via DETACHED_PROCESS respawner
      - restart_status: check whether restart is in progress and last marker

    First Tier 3 graduation. Restart cooldown + dry-run + preflight + audit-log
    all behave as designed. Substrate-trust upgrade: I can restart myself.
    """
    return await _call("self_control", {"action": action})


# ── Entry point ──────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run()
