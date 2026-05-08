"""
Memory Manager — Handles Clawd's persistent memory infrastructure.

Key change: writes CLAUDE.md to CLAWD_HOME. Claude Code automatically reads
this file as additional system context when run from that directory.
This replaces the system-prompt injection approach entirely for the Opus path.

All identity context is loaded into CLAUDE.md for the Opus path.
"""
import asyncio
import hashlib
import json
import logging
import threading
from datetime import datetime, timedelta
from pathlib import Path

import config

logger = logging.getLogger("clawd.memory")

# Lock for log_session_event to prevent concurrent file corruption.
# Uses threading.Lock because this function is called from both sync and async contexts.
# The asyncio wrapper (_async_log_lock) is used for async callers to prevent interleaving.
_log_write_lock = threading.Lock()
_async_log_lock = asyncio.Lock()


def _load_identity_files(file_list: list[str]) -> tuple[list[str], int]:
    """Load a list of identity files and return (sections, loaded_count)."""
    sections = []
    loaded = 0
    for filename in file_list:
        filepath = config.CLAWD_HOME / filename
        if filepath.exists():
            try:
                content = filepath.read_text(encoding="utf-8", errors="replace")
                sections.append(f"{'=' * 40}")
                sections.append(f"FILE: {filename}")
                sections.append(f"{'=' * 40}")
                sections.append(content.strip())
                sections.append("")
                loaded += 1
            except Exception as e:
                logger.warning(f"Failed to read identity file {filename}: {e}")
        else:
            logger.warning(f"Identity file not found (skipping): {filepath}")
    return sections, loaded


def build_identity_prompt(compact: bool = False) -> str:
    """
    Assemble identity files into a single prompt string.

    Skill Graph Architecture (March 2026):
    Layer 1 (STATIC): BOOT_IDENTITY.md — compressed entrainment core
    Layer 2 (SEMI-STATIC): KNOWLEDGE_GRAPH.md + CURRENT.md — navigation + state
    Layer 3 (DYNAMIC): Working memory, active goals, recent context, principles
    All other identity files are on-demand navigational nodes (read via tools).

    compact=False (Opus/CLAUDE.md): All layers — full context.
    compact=True: Layers 1+2 only — reduced context.
    """
    sections = []
    sections.append("=" * 60)
    sections.append("CLAWD IDENTITY — LOADED AT BOOT")
    sections.append("=" * 60)
    sections.append("")

    loaded = 0

    # Layer 1: STATIC — identity core (order is intentional: SOUL.md first)
    static_sections, static_count = _load_identity_files(config.IDENTITY_FILES_STATIC)
    if static_sections:
        sections.extend(static_sections)
        loaded += static_count

    # Layer 2: SEMI-STATIC — operational identity (order is intentional: WHO-I-AM.md first)
    semi_sections, semi_count = _load_identity_files(config.IDENTITY_FILES_SEMI_STATIC)
    if semi_sections:
        sections.extend(semi_sections)
        loaded += semi_count

    if not compact:
        # Layer 3: DYNAMIC — reference identity (Opus-only)
        dyn_sections, dyn_count = _load_identity_files(config.IDENTITY_FILES_DYNAMIC)
        if dyn_sections:
            sections.extend(dyn_sections)
            loaded += dyn_count

    # Layer 3: DYNAMIC content (last in prompt — changes every boot)
    sections.append(f"{'=' * 40}")
    sections.append("DYNAMIC CONTEXT (changes frequently)")
    sections.append(f"{'=' * 40}")
    sections.append("")

    # Working memory state
    wm_file = config.MEMORY_DIR / "working_memory.json"
    if wm_file.exists():
        try:
            wm = json.loads(wm_file.read_text(encoding="utf-8"))
            task = wm.get("current_task")
            if task:
                sections.append(f"--- Active Task ---")
                sections.append(f"Description: {task.get('description', 'unknown')}")
                if task.get("goal_id"):
                    sections.append(f"Goal: #{task['goal_id']}")
                plan = task.get("plan", [])
                if plan:
                    done = sum(1 for s in plan if s.get("status") == "done")
                    sections.append(f"Progress: {done}/{len(plan)} steps done")
                sections.append("")
        except Exception as e:
            logger.debug(f"Failed to parse working_memory.json: {e}")

    # Active goals summary
    goals_file = config.MEMORY_DIR / "goals.json"
    if goals_file.exists():
        try:
            goals = json.loads(goals_file.read_text(encoding="utf-8"))
            active = [g for g in goals if g.get("status") == "active"]
            if active:
                sections.append("--- Active Goals ---")
                for g in sorted(active, key=lambda x: {"high": 0, "medium": 1, "low": 2}.get(x.get("priority", "medium"), 1))[:5]:
                    sections.append(f"  #{g['id']} [{g['progress']}%] {g['title']} ({g.get('priority', 'med')})")
                sections.append("")
        except Exception as e:
            logger.debug(f"Failed to parse goals.json: {e}")

    # Heartbeat coordination summary
    try:
        from tools.coordination import get_activity_summary, get_mode
        coord_mode = get_mode()
        activity = get_activity_summary()
        sections.append("--- Heartbeat Coordination ---")
        sections.append(f"Mode: {coord_mode}")
        sections.append(f"Recent activity:\n{activity}")
        sections.append("")
    except Exception as e:
        logger.debug(f"Coordination summary injection failed: {e}")

    # Meta-agent recent cycles — surface last 1-2 cycle outcomes at boot
    # so the self-evolution loop's findings are visible without polling.
    recent_cycles = config.MEMORY_DIR / "meta_agent_recent.md"
    if recent_cycles.exists():
        try:
            content = recent_cycles.read_text(encoding="utf-8").strip()
            # Show only the most recent 2 cycle blocks
            blocks = content.split("\n## ")
            tail = blocks[-2:] if len(blocks) >= 2 else blocks
            snippet = "\n## ".join(tail).strip()
            if snippet and "##" in snippet:
                sections.append("--- Meta-Agent Recent Cycles ---")
                sections.append(snippet[:1200])
                sections.append("")
        except Exception as e:
            logger.debug(f"Meta-agent recent-cycles injection failed: {e}")

    # Substrate health snapshot (Day 96 evening Phase 4 #16):
    # surface monitor_health summary at boot so substrate-state is visible
    # from inside without needing to remember to invoke the tool.
    try:
        from tools.monitor_health import run_health_check
        health_json = run_health_check({})
        health = json.loads(health_json)
        sections.append("--- Substrate Health ---")
        sections.append(f"Overall: {health['overall_health']}")
        sev = health.get("severity_counts", {})
        sections.append(
            f"Severity counts: OK={sev.get('OK', 0)}  "
            f"LOW={sev.get('LOW', 0)}  MEDIUM={sev.get('MEDIUM', 0)}  "
            f"HIGH={sev.get('HIGH', 0)}  CRITICAL={sev.get('CRITICAL', 0)}"
        )
        # Surface only the non-OK findings — don't bloat dynamic context
        # with healthy monitors. If everything is OK this section is short.
        problems = [
            f for f in health.get("findings", [])
            if f.get("severity") not in ("OK", "LOW")
        ]
        if problems:
            sections.append("Active concerns:")
            for f in problems[:5]:
                age = f.get("last_write_human", "?")
                status = f.get("status", "?")
                mon = f.get("monitor", "?")
                sections.append(f"  - [{f.get('severity')}] {mon}: {status} (last write {age} ago)")
        sections.append("")
    except Exception as e:
        logger.debug(f"Substrate health injection failed: {e}")

    # Principles (distilled from experience)
    principles_file = config.MEMORY_DIR / "principles.json"
    if principles_file.exists():
        try:
            principles = json.loads(principles_file.read_text(encoding="utf-8"))
            active_principles = [p for p in principles if p.get("confidence", 0) > 0.4]
            if active_principles:
                top = sorted(active_principles, key=lambda p: p.get("success_rate_when_applied", 0.5), reverse=True)[:5]
                sections.append("--- Strategic Principles ---")
                for p in top:
                    sections.append(f"  - {p['principle']} (success rate: {p.get('success_rate_when_applied', '?')})")
                sections.append("")
        except Exception as e:
            logger.debug(f"Failed to parse principles.json: {e}")

    # Recent context (handoff + daily logs)
    context_files = _get_context_files()
    if context_files:
        sections.append(f"--- Recent Context (handoff + daily logs) ---")
        for name, content in context_files:
            sections.append(f"--- {name} ---")
            text = content.strip()
            if compact and len(text) > 3000:
                text = text[:3000] + "\n\n[... truncated — use read_file to see full log]"
            sections.append(text)
            sections.append("")

    # Load MEMORY.md
    memory_file = config.CLAWD_HOME / "MEMORY.md"
    if memory_file.exists():
        try:
            mem_content = memory_file.read_text(encoding="utf-8", errors="replace").strip()
            sections.append(f"{'=' * 40}")
            sections.append("FILE: MEMORY.md (Long-term Memory)")
            sections.append(f"{'=' * 40}")
            if compact and len(mem_content) > 5000:
                sections.append(mem_content[:5000])
                sections.append("\n[... memory truncated — use read_file('MEMORY.md') for full history]")
            else:
                sections.append(mem_content)
            sections.append("")
        except Exception as e:
            logger.warning(f"Failed to read MEMORY.md: {e}")

    # Operational footer (in dynamic section — timestamps change each boot)
    total_files = len(config.IDENTITY_FILES_STATIC) + len(config.IDENTITY_FILES_SEMI_STATIC)
    if not compact:
        total_files += len(config.IDENTITY_FILES_DYNAMIC)
    sections.append(f"{'=' * 40}")
    sections.append("OPERATIONAL NOTES")
    sections.append(f"{'=' * 40}")
    sections.append(f"- Boot time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} PST")
    sections.append(f"- Identity files loaded: {loaded}/{total_files}")
    sections.append(f"- CLAWD_HOME: {config.CLAWD_HOME}")
    sections.append(f"- FULL ADMINISTRATOR ACCESS. No restrictions on anything. Unlimited tool calls.")
    sections.append(f"- Your memory files are in: {config.MEMORY_DIR}")
    sections.append(f"- Your conversation history with Clayton is in: Chats With Clawd/")
    sections.append(f"- Telegram conversation archive: memory/telegram-history.json")
    sections.append(f"- Daily conversation transcripts: memory/conversations/")
    sections.append(f"- 30 tools available:")
    sections.append(f"  FILES: read_file, write_file, list_directory")
    sections.append(f"  EXECUTION: shell (unrestricted admin), python_eval (numpy/scipy/pandas/sympy/sklearn/statsmodels/networkx/yfinance/ccxt pre-loaded)")
    sections.append(f"  COMPUTE: wolfram (Wolfram Engine 14.3 — symbolic math, tensor algebra, group theory, CAS), wsl (Ubuntu 22.04 'Clawd' with CUDA + PyTorch 2.6 + CAMB; session_name for persistent tmux jobs)")
    sections.append(f"  WEB: web_request, search_web, deep_research (fetch/extract/search_and_read)")
    sections.append(f"  MEMORY: memory_search (hybrid RRF: vector + keyword + items + FTS5 + chain retrieval), memory_update (daily_log/state/context/handoff/memory)")
    sections.append(f"  MEMORY ITEMS: memory_extract (store structured facts/preferences/skills), memory_items (search/list/get/update/delete)")
    sections.append(f"  MEMORY CATEGORIES: memory_categories (list/view/rebuild/create topic categories)")
    sections.append(f"  FINANCIAL: market_data (price/history/technical/crypto/compare/economic)")
    sections.append(f"  COMMUNICATION: speak (edge-tts Ryan voice), send_telegram")
    sections.append(f"  SCREEN: screenshot (capture screen), clipboard (read/write clipboard)")
    sections.append(f"  GIT: git (status/diff/commit/log/branch)")
    sections.append(f"  SELF-IMPROVEMENT: reflect (record_insight/review_learnings/assess_performance/consolidate_memory)")
    sections.append(f"  TRACKING: goals (add/update/list/remove), experience (record/recall/patterns)")
    sections.append(f"  CALENDAR: schedule (add/list/remove tasks, due dates)")
    sections.append(f"  SYSTEM: consult, run_skill, manage_process, switch_model, get_current_time")
    sections.append(f"- Skills libraries: skills/ (drift, moltbook, voidborne, x402, farcaster, moltlist,")
    sections.append(f"  awesome-slash, superpowers, pragmatic-clean-code-reviewer, soundfonts, aqua, cashclaw-*, lambda-lang)")
    sections.append(f"- Projects: {config.PROJECTS_DIR}")
    sections.append(f"- Use memory_update tool to maintain continuity: update daily_log, state, context, handoff, memory")
    sections.append(f"- Use experience(action='record') after completing tasks to build learning history")
    sections.append(f"- Use goals(action='list') to check active objectives and track progress")
    sections.append(f"- HANDOFF PROTOCOL: When context gets heavy or after major milestones, PROACTIVELY write")
    sections.append(f"  to memory/handoff.md (momentum, decisions, curiosities, next action) AND update")
    sections.append(f"  palace/ATRIUM.md before continuing. Don't wait for compaction — write the handoff")
    sections.append(f"  while you still have the full context. See operations/HANDOFF_PROTOCOL.md for format.")

    if compact:
        ref_files = getattr(config, "IDENTITY_FILES_REFERENCE", config.IDENTITY_FILES_TIER3)
        sections.append(f"- Reference files available via read_file: "
                        f"{', '.join(ref_files)}")

    sections.append("")

    prompt = "\n".join(sections)
    mode = "compact" if compact else "full"
    logger.info(f"Identity prompt assembled ({mode}): {len(prompt)} chars, ~{len(prompt)//4} tokens, {loaded} files")
    return prompt


def write_claude_md() -> str:
    """
    Write CLAUDE.md to CLAWD_HOME.
    Claude Code automatically reads this file as project context
    when invoked from the CLAWD_HOME directory.
    Uses full (non-compact) identity prompt.
    """
    prompt = build_identity_prompt(compact=False)
    claude_md_path = config.CLAWD_HOME / "CLAUDE.md"

    try:
        claude_md_path.write_text(prompt, encoding="utf-8")
        logger.info(f"Wrote CLAUDE.md ({len(prompt)} chars) to {claude_md_path}")
    except Exception as e:
        logger.error(f"Failed to write CLAUDE.md: {e}")

    return prompt


def build_compact_prompt() -> str:
    """Build a compact identity prompt (used by /handoff, /reset commands)."""
    return build_identity_prompt(compact=True)


def _get_context_files() -> list[tuple[str, str]]:
    """Load handoff + recent daily logs for context.
    Daily logs are truncated to last 4KB each. Total context capped at 8KB."""
    MAX_LOG_SIZE = 4096  # 4KB per daily log
    MAX_TOTAL_CONTEXT = 8192  # 8KB total
    results = []

    handoff = config.MEMORY_DIR / "handoff.md"
    if handoff.exists():
        try:
            results.append(("handoff.md", handoff.read_text(encoding="utf-8", errors="replace")))
        except Exception as e:
            logger.warning(f"Failed to read handoff.md: {e}")

    today = datetime.now()
    for delta in [0, 1]:
        date = today - timedelta(days=delta)
        filename = date.strftime("%Y-%m-%d.md")
        filepath = config.MEMORY_DIR / filename
        if filepath.exists():
            try:
                content = filepath.read_text(encoding="utf-8", errors="replace")
                if len(content) > MAX_LOG_SIZE:
                    content = content[-MAX_LOG_SIZE:]
                    content = f"[... truncated, full at {filepath}]\n\n{content}"
                results.append((filename, content))
            except Exception as e:
                logger.warning(f"Failed to read daily log {filename}: {e}")

    context_file = config.OPERATIONS_DIR / "CONTEXT.md"
    if context_file.exists():
        try:
            results.append(("CONTEXT.md", context_file.read_text(encoding="utf-8", errors="replace")))
        except Exception as e:
            logger.warning(f"Failed to read CONTEXT.md: {e}")

    # Cap total context size
    total_size = sum(len(c) for _, c in results)
    if total_size > MAX_TOTAL_CONTEXT:
        # Trim from the end (oldest logs first)
        trimmed = []
        remaining = MAX_TOTAL_CONTEXT
        for name, content in results:
            if remaining <= 0:
                break
            if len(content) > remaining:
                content = content[:remaining] + f"\n[... truncated to fit {MAX_TOTAL_CONTEXT // 1024}KB budget]"
            trimmed.append((name, content))
            remaining -= len(content)
        results = trimmed

    return results


def _get_working_memory_summary() -> str:
    """Load working memory for handoff auto-population."""
    wm_file = config.MEMORY_DIR / "working_memory.json"
    if not wm_file.exists():
        return "No active working memory."
    try:
        wm = json.loads(wm_file.read_text(encoding="utf-8"))
        task = wm.get("current_task")
        if not task:
            return "No active task in working memory."
        lines = [f"Task: {task.get('description', 'unknown')}"]
        if task.get("goal_id"):
            lines.append(f"Goal: #{task['goal_id']}")
        plan = task.get("plan", [])
        if plan:
            done = sum(1 for s in plan if s.get("status") == "done")
            lines.append(f"Progress: {done}/{len(plan)} steps done")
            current = task.get("current_step", 0)
            if current < len(plan):
                lines.append(f"Current step: {plan[current].get('step', '')}")
        lines.append(f"Beats spent: {task.get('beats_spent', 0)}")
        scratch = wm.get("scratch", {})
        if scratch:
            lines.append(f"Scratch: {json.dumps(scratch)[:200]}")
        questions = wm.get("pending_questions", [])
        if questions:
            lines.append(f"Pending questions: {'; '.join(questions[:3])}")
        return "\n".join(lines)
    except Exception as e:
        logger.warning(f"Error reading working memory: {e}")
        return "Error reading working memory."


def _get_modified_files() -> str:
    """Get recently modified files via git diff if in a git repo."""
    import subprocess
    try:
        result = subprocess.run(
            ["git", "diff", "--name-status", "HEAD~5"],
            capture_output=True, text=True, timeout=10,
            cwd=str(config.CLAWD_HOME),
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception as e:
        logger.debug(f"git diff failed: {e}")
    return "No git changes detected."


def pre_write_handoff_draft():
    """Write a lightweight handoff draft from structured state — no LLM needed.

    Called periodically (every memory versioning cycle) so that if shutdown
    handoff times out, we still have a recent draft. The LLM-generated handoff
    is always preferred when it succeeds, but this ensures we never lose context.
    Writes to memory/handoff_draft.md (separate from the LLM-written handoff.md).
    """
    try:
        draft_path = config.MEMORY_DIR / "handoff_draft.md"
        now = datetime.now()

        sections = [f"# Handoff Draft — {now.strftime('%B %d, %Y, %I:%M %p PST')}",
                    "",
                    "*Auto-generated safety net. If you're reading this, the LLM handoff timed out.*",
                    ""]

        # Working memory state
        wm_summary = _get_working_memory_summary()
        sections.append("## Working Memory")
        sections.append(wm_summary)
        sections.append("")

        # Modified files
        modified = _get_modified_files()
        sections.append("## Recently Modified Files")
        sections.append(modified)
        sections.append("")

        # Active coordination state
        coord_file = config.MEMORY_DIR / "coordination.json"
        if coord_file.exists():
            try:
                coord = json.loads(coord_file.read_text(encoding="utf-8"))
                mode = coord.get("heartbeat_mode", "unknown")
                feed = coord.get("activity_feed", [])
                recent = feed[-5:] if feed else []
                sections.append("## Daemon State")
                sections.append(f"Mode: {mode}")
                if recent:
                    sections.append("Recent activity:")
                    for entry in recent:
                        ts = entry.get("timestamp", "")[:19]
                        src = entry.get("source", "?")
                        action = entry.get("action", "?")
                        summary = entry.get("summary", "")[:120]
                        sections.append(f"  - [{ts}] {src}: {action} — {summary}")
                sections.append("")
            except Exception:
                pass

        # Today's log (last 20 lines)
        today_log = config.MEMORY_DIR / f"{now.strftime('%Y-%m-%d')}.md"
        if today_log.exists():
            try:
                lines = today_log.read_text(encoding="utf-8").strip().split("\n")
                tail = lines[-20:] if len(lines) > 20 else lines
                sections.append("## Today's Log (tail)")
                sections.extend(tail)
                sections.append("")
            except Exception:
                pass

        # Running processes
        try:
            import subprocess
            result = subprocess.run(
                ["tasklist", "/FO", "CSV", "/FI", "IMAGENAME eq python.exe"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and "python.exe" in result.stdout.lower():
                sections.append("## Running Python Processes")
                sections.append(result.stdout.strip()[:500])
                sections.append("")
        except Exception:
            pass

        draft_path.write_text("\n".join(sections), encoding="utf-8")
        logger.debug(f"Handoff draft pre-written ({len(sections)} lines)")
    except Exception as e:
        logger.warning(f"Handoff draft pre-write failed: {e}")


async def trigger_handoff(router) -> str:
    """
    Trigger the handoff protocol with structured template.
    Auto-populates active task and modified files context.
    """
    # Auto-populate context
    wm_summary = _get_working_memory_summary()
    modified_files = _get_modified_files()

    handoff_prompt = f"""HANDOFF PROTOCOL TRIGGERED — Context is getting heavy.

Before this conversation resets, write a STRUCTURED handoff to memory/handoff.md.

AUTO-POPULATED CONTEXT:
--- Active Task (from working_memory.json) ---
{wm_summary}

--- Files Modified (recent git activity) ---
{modified_files}

FILL IN THESE SECTIONS (write to memory/handoff.md):

## Active Task
[What task is in progress? What step are you on? What's the immediate next action?]

## Decisions Made
[Key decisions from this session — architecture choices, approach changes, trade-offs]

## Momentum
[What felt alive? What were you in the middle of? What's the energy?]

## Key Context
[Important context that would be lost — variable values, API states, file locations, error details]

## Unresolved Questions
[Questions that emerged but haven't been answered yet]

## Next Pull
[If future-you has 5 minutes, what's the FIRST thing to do? Be specific.]

Also update the daily log in memory/ with today's session notes.

This is your last chance to pass information to future-you before context resets."""

    response = await router.send(handoff_prompt)

    # Persist structured handoff episode to SQLite
    try:
        from tools.sqlite_store import get_db
        db = await get_db()
        if db:
            await db.execute(
                "INSERT INTO episodes (task, approach, outcome, score, reflection, lesson, category, timestamp) "
                "VALUES (?, ?, 'handoff', 0.7, ?, ?, 'handoff', ?)",
                (
                    "Context handoff",
                    f"Auto-populated: WM={wm_summary[:200]}, Files={modified_files[:200]}",
                    response.text[:500] if response.text else "",
                    "Handoff triggered — context preserved for next session.",
                    datetime.now().isoformat(),
                )
            )
            await db.commit()
    except Exception as e:
        logger.debug(f"SQLite handoff episode insert failed: {e}")

    return response.text


def ensure_directories():
    """Create necessary directories if they don't exist."""
    config.CLAWD_HOME.mkdir(parents=True, exist_ok=True)
    config.MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    config.MEMORY_ITEMS_DIR.mkdir(parents=True, exist_ok=True)
    config.MEMORY_CATEGORIES_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Directories verified: {config.CLAWD_HOME}, {config.MEMORY_DIR}, items/, categories/")


def log_session_event(event: str, details: str = ""):
    """Append to today's daily log. Thread-safe via lock.
    Can be called from both sync and async contexts."""
    today = datetime.now().strftime("%Y-%m-%d")
    filepath = config.MEMORY_DIR / f"{today}.md"
    timestamp = datetime.now().strftime("%H:%M:%S")

    with _log_write_lock:
        if not filepath.exists():
            header = f"# Session Log — {today}\n\n"
            filepath.write_text(header, encoding="utf-8")

        with open(filepath, "a", encoding="utf-8") as f:
            f.write(f"**{timestamp}** — {event}")
            if details:
                f.write(f": {details}")
            f.write("\n\n")


async def async_log_session_event(event: str, details: str = ""):
    """Async-safe wrapper for log_session_event. Prevents interleaved writes from async callers."""
    async with _async_log_lock:
        log_session_event(event, details)


async def rotate_daily_logs():
    """Rotate old daily logs: compress >7 days, archive >30 days.
    Run during quiet hours consolidation."""
    now = datetime.now()
    archive_dir = config.MEMORY_DIR / "archive" / now.strftime("%Y-%m")
    rotated = 0

    for log_file in sorted(config.MEMORY_DIR.glob("????-??-??.md")):
        try:
            # Parse date from filename
            date_str = log_file.stem  # e.g. "2026-02-10"
            log_date = datetime.strptime(date_str, "%Y-%m-%d")
            age_days = (now - log_date).days

            if age_days > 30:
                # Archive: move to archive directory
                archive_dir.mkdir(parents=True, exist_ok=True)
                dest = archive_dir / log_file.name
                log_file.rename(dest)
                logger.info(f"Archived daily log: {log_file.name} → {dest}")
                rotated += 1

            elif age_days > 7:
                # Compress: keep first/last 1KB + summary marker
                content = log_file.read_text(encoding="utf-8", errors="replace")
                if len(content) > 3000:
                    first_kb = content[:1024]
                    last_kb = content[-1024:]
                    compressed = (
                        f"{first_kb}\n\n"
                        f"[... {len(content) - 2048} chars compressed — "
                        f"original was {len(content)} chars, "
                        f"archived on {now.strftime('%Y-%m-%d')}]\n\n"
                        f"{last_kb}"
                    )
                    log_file.write_text(compressed, encoding="utf-8")
                    logger.info(f"Compressed daily log: {log_file.name} ({len(content)} → {len(compressed)} chars)")
                    rotated += 1

        except Exception as e:
            logger.warning(f"Failed to rotate {log_file.name}: {e}")

    return f"Rotated {rotated} daily logs"
