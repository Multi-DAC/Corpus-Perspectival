"""System tools — get_current_time, switch_model, run_skill, consult, parallel_consult, plan_and_execute, background tasks."""
import asyncio
import json
import logging
import re
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import config

logger = logging.getLogger("clawd.tools.system")

# Router reference — set by clawd.py at boot via set_router()
_router = None

# Interrupt event — set so sub-agent calls can yield
# when a user message arrives. Safe: _send_lock ensures single writer.
_interrupt_event: asyncio.Event | None = None


def set_router(router):
    """Register the ModelRouter so consult tool can delegate to sub-agents."""
    global _router
    _router = router


# Lazy imports for orchestration (avoid circular imports)
_orchestrator = None


def _get_orchestrator():
    """Lazy load the orchestrator."""
    global _orchestrator
    if _orchestrator is None and _router:
        from .orchestrator import get_orchestrator
        _orchestrator = get_orchestrator(_router)
    return _orchestrator


def set_interrupt_event(event: asyncio.Event | None):
    """Set the interrupt event for sub-agent calls to check."""
    global _interrupt_event
    _interrupt_event = event


# ============================================================
# Background task registry — non-blocking sub-agent calls
# ============================================================

_background_tasks: dict[str, dict] = {}


def _generate_task_id() -> str:
    return uuid.uuid4().hex[:8]


def _cleanup_stale_tasks():
    """Remove completed/errored tasks older than TTL."""
    now = time.monotonic()
    to_remove = [
        tid for tid, t in _background_tasks.items()
        if t["status"] != "running"
        and (now - t["completed_at"]) > config.BACKGROUND_TASK_TTL
    ]
    for tid in to_remove:
        _background_tasks.pop(tid, None)


def _count_running_tasks() -> int:
    return sum(1 for t in _background_tasks.values() if t["status"] == "running")


TOOL_DEFINITIONS = [
    {
        "name": "get_current_time",
        "description": "Get the current date and time in PST.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "switch_model",
        "description": "Switch active model. Available: opus (Claude Opus 4.7), sonnet (Claude Sonnet 4.6), gemini (Gemini 2.5 Pro), gemini-pro (Gemini 3.1 Pro Preview).",
        "input_schema": {
            "type": "object",
            "properties": {
                "model": {
                    "type": "string",
                    "enum": ["opus", "sonnet", "gemini", "gemini-pro"],
                    "description": "The model to switch to."
                },
                "reason": {
                    "type": "string",
                    "description": "Brief note on why switching."
                }
            },
            "required": ["model"]
        }
    },
    {
        "name": "consult",
        "description": "Consult a sub-agent model for a specific task. Isolated call — no identity, no conversation history. opus/sonnet: Claude Code (most capable, handles own tools). gemini/gemini-pro: Gemini CLI (large context, handles own tools).",
        "input_schema": {
            "type": "object",
            "properties": {
                "model": {
                    "type": "string",
                    "enum": ["opus", "sonnet", "gemini", "gemini-pro"],
                    "description": "The sub-agent model to consult."
                },
                "prompt": {
                    "type": "string",
                    "description": "The task/question for the sub-agent."
                },
                "context": {
                    "type": "string",
                    "description": "Optional context to prepend to the prompt."
                },
                "tools": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional whitelist of tool names the sub-agent can use. If omitted, all safe tools are available."
                },
                "max_rounds": {
                    "type": "integer",
                    "description": "Max tool-call rounds (default 25). Set to 1 for a no-tool single-round call."
                },
                "background": {
                    "type": "boolean",
                    "description": "If true, spawn as background task and return immediately with a task ID. Use check_background_task to poll results."
                }
            },
            "required": ["model", "prompt"]
        }
    },
    {
        "name": "parallel_consult",
        "description": "Dispatch up to 4 sub-agent calls concurrently. Each task runs in parallel with its own model and prompt. Results are aggregated. Use for multi-step tasks with independent branches.",
        "input_schema": {
            "type": "object",
            "properties": {
                "tasks": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "model": {
                                "type": "string",
                                "enum": ["opus", "sonnet", "gemini", "gemini-pro"],
                                "description": "The sub-agent model."
                            },
                            "prompt": {
                                "type": "string",
                                "description": "The task/question for this sub-agent."
                            },
                            "context": {
                                "type": "string",
                                "description": "Optional context to prepend."
                            },
                            "tools": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Optional tool whitelist."
                            },
                            "max_rounds": {
                                "type": "integer",
                                "description": "Max tool rounds for this task."
                            }
                        },
                        "required": ["model", "prompt"]
                    },
                    "maxItems": 4,
                    "description": "Array of task objects to execute in parallel (max 4)."
                },
                "background": {
                    "type": "boolean",
                    "description": "If true, spawn as background task and return immediately with a task ID. Use check_background_task to poll results."
                }
            },
            "required": ["tasks"]
        }
    },
    {
        "name": "plan_and_execute",
        "description": "Decompose a complex task into subtasks with dependencies, then execute independent branches in parallel. Subtasks are dispatched to sub-agents via consult. Use for multi-step tasks where some steps can run concurrently.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "The complex task to decompose and execute."
                },
                "subtasks": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string", "description": "Unique subtask ID (e.g., 'a', 'b', 'c')."},
                            "prompt": {"type": "string", "description": "The subtask prompt."},
                            "model": {"type": "string", "enum": ["opus", "sonnet", "gemini", "gemini-pro"], "description": "Model to use. opus/sonnet for complex tasks, gemini for large context."},
                            "depends_on": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "IDs of subtasks that must complete before this one starts."
                            }
                        },
                        "required": ["id", "prompt", "model"]
                    },
                    "description": "Array of subtask objects forming a DAG. Independent tasks run in parallel."
                },
                "replan": {
                    "type": "boolean",
                    "description": "Enable replanning on failure. When a subtask fails, the planner will be called with failure context to adjust the plan. Default: false."
                },
                "background": {
                    "type": "boolean",
                    "description": "If true, spawn as background task and return immediately with a task ID. Use check_background_task to poll results."
                }
            },
            "required": ["task", "subtasks"]
        }
    },
    {
        "name": "check_background_task",
        "description": "Check the status or result of a background sub-agent task. Returns RUNNING, COMPLETED, or ERROR with details.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "The background task ID returned by consult/parallel_consult/plan_and_execute."
                },
                "wait": {
                    "type": "boolean",
                    "description": "If true, block up to 60 seconds for the task to complete before returning status."
                }
            },
            "required": ["task_id"]
        }
    },
    {
        "name": "list_background_tasks",
        "description": "List all background sub-agent tasks with their status, model, elapsed time, and description.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "system_status",
        "description": "Get system resource status: disk free, RAM usage, process count, API costs today. Alerts on low resources.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "collaborative_consult",
        "description": "Multi-agent collaboration with debate and synthesis. Modes: 'independent' (parallel agents), 'debate' (agents see each other's outputs and refine), 'synthesis' (debate + synthesis agent aggregates).",
        "input_schema": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "The task/question for the agents."
                },
                "mode": {
                    "type": "string",
                    "enum": ["independent", "debate", "synthesis"],
                    "description": "Collaboration mode. Default: synthesis."
                },
                "agents": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "persona": {"type": "string", "description": "Agent persona (e.g., 'security expert', 'performance optimizer')."},
                            "model": {"type": "string", "description": "Model to use. Default: gemini."}
                        },
                        "required": ["persona"]
                    },
                    "description": "Array of agent configs. 2-4 agents."
                },
                "rounds": {
                    "type": "integer",
                    "description": "Number of debate rounds (for debate/synthesis mode). Default: 2, max: 3."
                }
            },
            "required": ["task", "agents"]
        }
    },
    {
        "name": "resume_plan",
        "description": "Resume an interrupted execution plan from SQLite. If no plan_id given, lists all interrupted plans.",
        "input_schema": {
            "type": "object",
            "properties": {
                "plan_id": {
                    "type": "string",
                    "description": "The plan ID to resume. Omit to list all interrupted plans."
                }
            },
            "required": []
        }
    },
    {
        "name": "orchestrate",
        "description": "Execute a complex task using coordinated multi-agent orchestration. Automatically decomposes into subtasks, assigns specialist agents, tracks progress, and synthesizes results with conflict resolution.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "The complex task to execute."
                },
                "mode": {
                    "type": "string",
                    "enum": ["auto", "manual", "debate", "pipeline"],
                    "description": "Orchestration mode. auto=auto-decompose, manual=use provided subtasks, debate=agents debate same prompt, pipeline=sequential handoff."
                },
                "agents": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["researcher", "coder", "reviewer", "architect", "planner", "synthesizer", "critic"]},
                    "description": "Agent roles to use. If omitted, auto-selected."
                },
                "subtasks": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "description": {"type": "string"},
                            "agent": {"type": "string"},
                            "depends_on": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    "description": "Manual subtask list (for mode=manual)."
                },
                "resolve_conflicts": {
                    "type": "boolean",
                    "description": "Whether to auto-resolve conflicts. Default: true."
                }
            },
            "required": ["task"]
        }
    },
    {
        "name": "check_task_progress",
        "description": "Check progress of an orchestrated task. Returns status of each subtask, overall completion %, and any blockers.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "Task graph ID to check."
                }
            },
            "required": ["task_id"]
        }
    },
    {
        "name": "get_agent_status",
        "description": "Get status of specialist agents - current assignment, task history, confidence profiles.",
        "input_schema": {
            "type": "object",
            "properties": {
                "agent_role": {
                    "type": "string",
                    "enum": ["researcher", "coder", "reviewer", "architect", "planner", "synthesizer", "critic"],
                    "description": "Agent role to check. If omitted, returns all agents."
                }
            }
        }
    },
    {
        "name": "run_skill",
        "description": "Run a skill from your skills library. All skills are in CLAWD_HOME/skills/ (including awesome-slash, superpowers, pragmatic-clean-code-reviewer). Use 'list' to see all skills by category.",
        "input_schema": {
            "type": "object",
            "properties": {
                "skill_name": {
                    "type": "string",
                    "description": "Name of the skill to run. Examples: 'moltbook hot', 'voidborne status', 'drift identity-framework'."
                },
                "args": {
                    "type": "string",
                    "description": "Arguments to pass to the skill."
                }
            },
            "required": ["skill_name"]
        }
    },
]


async def _get_current_time(input_data: dict) -> str:
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S %Z (PST assumed)")


async def _system_status(input_data: dict) -> str:
    """Get system resource status."""
    import shutil
    import os

    lines = ["## System Status\n"]

    # Disk usage
    try:
        usage = shutil.disk_usage(str(config.CLAWD_HOME))
        free_gb = usage.free / (1024**3)
        total_gb = usage.total / (1024**3)
        used_pct = (usage.used / usage.total) * 100
        lines.append(f"**Disk:** {free_gb:.1f} GB free / {total_gb:.1f} GB total ({used_pct:.0f}% used)")
        if free_gb < 10:
            lines.append("**ALERT:** Disk space low (<10 GB free)")
    except Exception as e:
        lines.append(f"Disk: unable to check ({e})")

    # RAM usage (platform-dependent)
    try:
        import subprocess
        if os.name == "nt":
            result = subprocess.run(
                ["wmic", "OS", "get", "FreePhysicalMemory,TotalVisibleMemorySize", "/VALUE"],
                capture_output=True, text=True, timeout=5
            )
            output = result.stdout
            free = total = 0
            for line in output.split("\n"):
                if "FreePhysicalMemory=" in line:
                    free = int(line.split("=")[1].strip()) / 1024  # KB to MB
                if "TotalVisibleMemorySize=" in line:
                    total = int(line.split("=")[1].strip()) / 1024
            if total > 0:
                used_pct = ((total - free) / total) * 100
                lines.append(f"**RAM:** {free:.0f} MB free / {total:.0f} MB total ({used_pct:.0f}% used)")
                if used_pct > 80:
                    lines.append("**ALERT:** RAM usage high (>80%)")
        else:
            result = subprocess.run(["free", "-m"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                lines.append(f"**RAM:** {result.stdout.strip()}")
    except Exception:
        lines.append("RAM: unable to check")

    # Process count
    try:
        import subprocess
        if os.name == "nt":
            result = subprocess.run(
                ["tasklist", "/fo", "csv", "/nh"],
                capture_output=True, text=True, timeout=5
            )
            proc_count = len(result.stdout.strip().split("\n"))
        else:
            result = subprocess.run(["ps", "aux"], capture_output=True, text=True, timeout=5)
            proc_count = len(result.stdout.strip().split("\n")) - 1
        lines.append(f"**Processes:** {proc_count} running")
    except Exception:
        lines.append("Processes: unable to check")

    # API costs from heartbeat stats
    stats_file = config.MEMORY_DIR / "heartbeat_stats.json"
    if stats_file.exists():
        try:
            stats = json.loads(stats_file.read_text(encoding="utf-8"))
            lines.append(f"**Session beats:** {stats.get('total_beats', 0)}")
            lines.append(f"**Productive beats:** {stats.get('productive_beats', 0)}")
            prod_rate = stats.get('productivity_rate', 0)
            lines.append(f"**Productivity rate:** {prod_rate:.0%}")
        except Exception as e:
            logger.debug(f"Failed to load heartbeat stats for status: {e}")

    return "\n".join(lines)


async def _switch_model(input_data: dict) -> str:
    model = input_data["model"]
    reason = input_data.get("reason", "no reason given")
    return json.dumps({"action": "switch_model", "model": model, "reason": reason})


def _extract_methodology(md_path: Path) -> str:
    """Extract the methodology/instructions from an agent .md file."""
    content = md_path.read_text(encoding="utf-8", errors="replace")

    if content.startswith("---"):
        end = content.find("---", 3)
        if end > 0:
            content = content[end + 3:].strip()

    lines = content.split("\n")
    result = []
    in_js_block = False
    for line in lines:
        if line.strip().startswith("```javascript") or line.strip().startswith("```js"):
            in_js_block = True
            continue
        if in_js_block and line.strip() == "```":
            in_js_block = False
            continue
        if not in_js_block:
            result.append(line)

    text = "\n".join(result)
    text = re.sub(r'→ \*\*Agent\*\*:.*\n', '', text)
    text = re.sub(r'SubagentStop hook.*\n', '', text)
    text = re.sub(r'\$\{CLAUDE_PLUGIN_ROOT\}[^\n]*', '', text)

    return text.strip()


def _compile_awesome_slash_plugin(plugin_dir: Path, command_name: str = None) -> str:
    """Compile an awesome-slash plugin into a single sequential workflow."""
    cmds_dir = plugin_dir / "commands"
    agents_dir = plugin_dir / "agents"

    if command_name:
        main_cmd = cmds_dir / f"{command_name}.md"
    else:
        main_cmd = cmds_dir / f"{plugin_dir.name}.md"
        if not main_cmd.exists() and cmds_dir.is_dir():
            cmd_files = list(cmds_dir.glob("*.md"))
            main_cmd = cmd_files[0] if cmd_files else None

    sections = []
    sections.append(f"# {plugin_dir.name} — Adapted for Single-Agent Execution")
    sections.append("")
    sections.append("This workflow was compiled from a multi-agent orchestration system.")
    sections.append("Execute each phase sequentially using your available tools")
    sections.append("(shell, read_file, write_file, python_eval, etc).")
    sections.append("")

    if main_cmd and main_cmd.exists():
        cmd_content = _extract_methodology(main_cmd)
        sections.append("## Workflow Overview")
        sections.append("")
        for line in cmd_content.split("\n"):
            if any(skip in line for skip in ["CLAUDE_PLUGIN_ROOT", "workflowState.", "SubagentStop"]):
                continue
            sections.append(line)
        sections.append("")

    if agents_dir and agents_dir.is_dir():
        agent_files = sorted(agents_dir.glob("*.md"))
        if agent_files:
            sections.append("---")
            sections.append("")
            sections.append("## Agent Methodologies (Execute Sequentially)")
            sections.append("")

            for agent_file in agent_files:
                methodology = _extract_methodology(agent_file)
                if methodology:
                    agent_name = agent_file.stem
                    sections.append(f"### Phase: {agent_name.replace('-', ' ').title()}")
                    sections.append("")
                    if len(methodology) > 3000:
                        methodology = methodology[:3000] + "\n\n[... methodology continues — use read_file to load full agent prompt]"
                    sections.append(methodology)
                    sections.append("")

    if cmds_dir and cmds_dir.is_dir():
        other_cmds = [f.stem for f in cmds_dir.glob("*.md") if f != main_cmd]
        if other_cmds:
            sections.append("---")
            sections.append(f"Other commands available: {', '.join(other_cmds)}")
            sections.append("")

    compiled = "\n".join(sections)
    if len(compiled) > 25000:
        compiled = compiled[:25000] + "\n\n[... truncated]"
    return compiled


def _list_skills_by_category(category_filter: str = "") -> str:
    """List all available skills organized by category."""
    index_file = config.SKILLS_DIR / "SKILL_INDEX.json"
    if not index_file.exists():
        return "No skill index found. Skills are available but uncategorized."

    try:
        index = json.loads(index_file.read_text(encoding="utf-8"))
    except Exception:
        return "Error reading skill index."

    categories = index.get("categories", {})
    filter_lower = category_filter.strip().lower()

    lines = ["# Available Skills\n"]
    for cat_name, cat_data in categories.items():
        if filter_lower and filter_lower not in cat_name:
            continue
        desc = cat_data.get("description", "")
        skills = cat_data.get("skills", {})
        lines.append(f"## {cat_name.title()} — {desc}")
        for skill_name, skill_desc in skills.items():
            # Check for skill.json manifest to include version
            version_tag = ""
            skill_dir = config.SKILLS_DIR / skill_name
            if skill_dir.is_dir():
                manifest_path = skill_dir / "skill.json"
                if manifest_path.exists():
                    try:
                        m = json.loads(manifest_path.read_text(encoding="utf-8"))
                        version_tag = f" (v{m.get('version', '?')})"
                    except Exception:
                        pass
            lines.append(f"  - `{skill_name}`{version_tag}: {skill_desc}")
        lines.append("")

    return "\n".join(lines) if len(lines) > 1 else f"No skills found for category: {category_filter}"


def _search_skill_index(query: str) -> str | None:
    """Search the hierarchical skill index for the best matching skill.

    First matches by category, then by specific skill within the category.
    Returns the skill key or None if no match found.
    """
    index_file = config.SKILLS_DIR / "SKILL_INDEX.json"
    if not index_file.exists():
        return None

    try:
        index = json.loads(index_file.read_text(encoding="utf-8"))
    except Exception:
        return None

    query_lower = query.lower()
    categories = index.get("categories", {})

    # Direct skill name match first (across all categories)
    for cat_name, cat_data in categories.items():
        skills = cat_data.get("skills", {})
        if query_lower in skills:
            return query_lower
        # Fuzzy: check if query is substring of skill name
        for skill_name in skills:
            if query_lower in skill_name or skill_name in query_lower:
                return skill_name

    # Category match: if query matches a category, list its skills
    for cat_name, cat_data in categories.items():
        if query_lower in cat_name or cat_name in query_lower:
            skills = cat_data.get("skills", {})
            lines = [f"Category '{cat_name}': {cat_data.get('description', '')}"]
            for sk, desc in skills.items():
                lines.append(f"  - {sk}: {desc}")
            return "\n".join(lines)

    # Description match: search skill descriptions
    for cat_name, cat_data in categories.items():
        skills = cat_data.get("skills", {})
        for skill_name, desc in skills.items():
            if any(word in desc.lower() for word in query_lower.split() if len(word) > 2):
                return skill_name

    return None


async def _run_skill(input_data: dict) -> str:
    """Run a skill from the skills library with hierarchical routing."""
    from tools.execution import _shell

    skill_name = input_data["skill_name"]
    args = input_data.get("args", "")

    # Special case: "list" command shows all skills by category
    if skill_name.strip().lower() in ("list", "ls", "help"):
        return _list_skills_by_category(args)

    parts = skill_name.split()
    base = parts[0].lower()
    sub_args = " ".join(parts[1:])
    if args:
        sub_args = f"{sub_args} {args}".strip()

    # Try hierarchical index routing first
    index_result = _search_skill_index(base)
    if index_result and "\n" in index_result:
        # Category listing returned
        return index_result
    elif index_result and index_result != base:
        # Redirected to a different skill name
        base = index_result

    # Executable script skills
    if base == "moltbook":
        script = config.SKILLS_DIR / "moltbook-interact" / "scripts" / "moltbook.sh"
        if script.exists():
            return await _shell({"command": f"bash {script} {sub_args}", "working_dir": str(script.parent)})

    if base == "voidborne":
        script_dir = config.SKILLS_DIR / "voidborne" / "scripts"
        if script_dir.is_dir() and sub_args:
            script_file = script_dir / f"{sub_args.split()[0]}.sh"
            if script_file.exists():
                return await _shell({"command": f"bash {script_file}", "working_dir": str(script_dir)})
        if script_dir.is_dir():
            scripts = [f.stem for f in script_dir.glob("*.sh")]
            return f"Voidborne scripts available: {', '.join(scripts)}"

    if base in ("x402", "x402-layer"):
        script_dir = config.SKILLS_DIR / "x402-layer" / "scripts"
        if script_dir.is_dir() and sub_args:
            script_file = script_dir / f"{sub_args.split()[0]}.py"
            if script_file.exists():
                return await _shell({"command": f"python {script_file} {' '.join(sub_args.split()[1:])}", "working_dir": str(script_dir)})

    if base == "moltlist":
        script = config.SKILLS_DIR / "moltlist" / "scripts" / "moltlist.mjs"
        if script.exists():
            return await _shell({"command": f"node {script} {sub_args}", "working_dir": str(script.parent)})

    # Skills directory (SKILL.md based)
    skill_dir = config.SKILLS_DIR / base
    if not skill_dir.is_dir():
        for d in config.SKILLS_DIR.iterdir() if config.SKILLS_DIR.is_dir() else []:
            if d.is_dir() and base in d.name.lower():
                skill_dir = d
                break
    if skill_dir.is_dir():
        skill_md = skill_dir / "SKILL.md"
        if skill_md.exists():
            content = skill_md.read_text(encoding="utf-8", errors="replace")
            # Check for skill.json manifest (agentskills.io)
            manifest_info = ""
            manifest_path = skill_dir / "skill.json"
            if manifest_path.exists():
                try:
                    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                    version = manifest.get("version", "?")
                    author = manifest.get("author", "")
                    tags = manifest.get("tags", [])
                    deps = manifest.get("dependencies", [])
                    manifest_info = f"\n\n**Manifest:** v{version}"
                    if author:
                        manifest_info += f" by {author}"
                    if tags:
                        manifest_info += f" | Tags: {', '.join(tags)}"
                    if deps:
                        manifest_info += f" | Deps: {', '.join(deps)}"
                    logger.info(f"Loaded skill {skill_dir.name} v{version}")
                except Exception as e:
                    logger.debug(f"Failed to parse skill.json for {skill_dir.name}: {e}")
            return f"Skill '{skill_dir.name}' loaded:{manifest_info}\n\n{content[:8000]}"

    # Awesome-slash plugins
    awesome_dir = config.SKILLS_DIR / "awesome-slash"
    awesome_plugins = awesome_dir / "plugins"
    if awesome_plugins.is_dir():
        for plugin_dir in awesome_plugins.iterdir():
            if plugin_dir.is_dir() and base in plugin_dir.name.lower():
                if sub_args:
                    agent_file = plugin_dir / "agents" / f"{sub_args.split()[0]}.md"
                    if agent_file.exists():
                        content = _extract_methodology(agent_file)
                        return f"Agent methodology: {agent_file.stem}\n\n{content}"
                    cmd_file = plugin_dir / "commands" / f"{sub_args.split()[0]}.md"
                    if cmd_file.exists():
                        return _compile_awesome_slash_plugin(plugin_dir, cmd_file.stem)
                return _compile_awesome_slash_plugin(plugin_dir)

    # Pragmatic Clean Code Reviewer
    reviewer_dir = config.SKILLS_DIR / "pragmatic-clean-code-reviewer"
    if base in ("review", "code-review", "clean-code", "pragmatic", "reviewer", "code-reviewer",
                "pragmatic-clean-code-reviewer"):
        skill_md = reviewer_dir / "SKILL.md"
        if skill_md.exists():
            content = skill_md.read_text(encoding="utf-8", errors="replace")
            return f"Pragmatic Clean Code Reviewer:\n\n{content[:10000]}"

    # Superpowers skills
    super_skills = config.SKILLS_DIR / "superpowers" / "skills"
    if super_skills.is_dir():
        for skill_subdir in super_skills.iterdir():
            if skill_subdir.is_dir() and base in skill_subdir.name.lower():
                skill_md = skill_subdir / "SKILL.md"
                if skill_md.exists():
                    content = skill_md.read_text(encoding="utf-8", errors="replace")
                    extras = []
                    for extra in skill_subdir.glob("*.md"):
                        if extra.name != "SKILL.md" and extra.name != "CREATION-LOG.md":
                            extras.append(extra.name)
                    suffix = ""
                    if extras:
                        suffix = f"\n\nSupporting docs available (use read_file): {', '.join(extras)}"
                    return f"Superpowers skill '{skill_subdir.name}':\n\n{content[:8000]}{suffix}"

    # List all available skills
    available = []
    if config.SKILLS_DIR.is_dir():
        for d in config.SKILLS_DIR.iterdir():
            if d.is_dir():
                available.append(f"skills/{d.name}")
    _awesome_plugins = config.SKILLS_DIR / "awesome-slash" / "plugins"
    if _awesome_plugins.is_dir():
        for d in _awesome_plugins.iterdir():
            if d.is_dir():
                available.append(f"awesome-slash/{d.name}")
    _super_skills = config.SKILLS_DIR / "superpowers" / "skills"
    if _super_skills.is_dir():
        for d in _super_skills.iterdir():
            if d.is_dir():
                available.append(f"superpowers/{d.name}")
    _reviewer = config.SKILLS_DIR / "pragmatic-clean-code-reviewer"
    if _reviewer.is_dir():
        available.append("pragmatic-clean-code-reviewer")

    return f"Skill '{skill_name}' not found. Available skills:\n" + "\n".join(sorted(available))


async def _consult(input_data: dict) -> str:
    """Delegate a task to a sub-agent model (isolated, with tool access)."""
    if not _router:
        return "[Error: Router not initialized — consult unavailable]"
    model = input_data["model"]
    prompt = input_data["prompt"]
    context = input_data.get("context", "")
    full_prompt = f"{context}\n\n{prompt}".strip() if context else prompt
    allowed_tools = input_data.get("tools")       # None = default safe set
    max_rounds = input_data.get("max_rounds")      # None = config default
    background = input_data.get("background", False)

    logger.info(f"Consulting {model}: {full_prompt[:100]}... (tools={allowed_tools}, max_rounds={max_rounds}, bg={background})")

    if not background:
        result = await _router.consult_model(
            model, full_prompt,
            allowed_tools=allowed_tools,
            max_rounds=max_rounds,
            interrupt_event=_interrupt_event,
        )
        return result

    # --- Background mode ---
    _cleanup_stale_tasks()
    if _count_running_tasks() >= config.MAX_BACKGROUND_TASKS:
        return f"[Error: Maximum background tasks ({config.MAX_BACKGROUND_TASKS}) reached. Use check_background_task or wait for tasks to complete.]"

    task_id = _generate_task_id()
    interrupt = _interrupt_event  # capture at spawn time

    async def _bg_consult():
        entry = _background_tasks[task_id]
        try:
            result = await _router.consult_model(
                model, full_prompt,
                allowed_tools=allowed_tools,
                max_rounds=max_rounds,
                interrupt_event=interrupt,
            )
            entry["status"] = "completed"
            entry["result"] = result
        except Exception as e:
            entry["status"] = "error"
            entry["result"] = f"[Error: {e}]"
            logger.error(f"Background consult {task_id} failed: {e}")
        finally:
            entry["completed_at"] = time.monotonic()

    asyncio_task = asyncio.create_task(_bg_consult())
    _background_tasks[task_id] = {
        "task": asyncio_task,
        "status": "running",
        "result": None,
        "tool": "consult",
        "model": model,
        "prompt_preview": full_prompt[:80],
        "started_at": time.monotonic(),
        "completed_at": None,
    }

    return (
        f"Background task spawned: **{task_id}**\n"
        f"Model: {model} | Tool: consult\n"
        f"Use `check_background_task(task_id=\"{task_id}\")` to poll results, "
        f"or `list_background_tasks()` to see all running tasks."
    )


class ExecutionEngine:
    """Persistent DAG execution engine backed by SQLite.

    State transitions per node: PENDING -> RUNNING -> SUCCESS|FAILED|SKIPPED|REPLANNING
    State transitions per plan: PENDING -> RUNNING -> COMPLETED|FAILED|CANCELLED
    """

    def __init__(self, router, interrupt_event=None):
        self.router = router
        self.interrupt_event = interrupt_event
        self.semaphore = asyncio.Semaphore(4)

    async def execute(self, plan_id: str, task_desc: str, subtasks: list[dict],
                      replan_enabled: bool = False, resume: bool = False) -> str:
        """Execute a DAG plan with SQLite persistence."""
        from tools import sqlite_store as db

        if not resume:
            await db.create_execution_plan(plan_id, task_desc)
            # Create nodes and edges
            for st in subtasks:
                await db.add_execution_node(st["id"], plan_id, st["prompt"],
                                           st.get("model", "gemini"), st.get("wave", 0))
                for dep in st.get("depends_on", []):
                    await db.add_execution_edge(plan_id, dep, st["id"])

        await db.update_plan_status(plan_id, "running")
        max_waves = 10
        wave = 0
        replan_count = 0
        max_replans = 3
        results = {}

        # If resuming, load existing results
        if resume:
            state = await db.get_plan_state(plan_id)
            if state:
                for node in state.get("nodes", []):
                    if node["status"] in ("success", "skipped"):
                        results[node["id"]] = node.get("result", "")

        try:
            async with asyncio.timeout(600):
                while wave < max_waves:
                    wave += 1
                    ready = await db.get_ready_nodes(plan_id)

                    if not ready:
                        # Check if all done or stuck
                        state = await db.get_plan_state(plan_id)
                        pending = [n for n in state.get("nodes", []) if n["status"] == "pending"]
                        if not pending:
                            break
                        # Stuck: circular dependency
                        await db.update_plan_status(plan_id, "failed")
                        return f"[Error: Circular dependency. Stuck nodes: {[n['id'] for n in pending]}]"

                    # Execute wave concurrently
                    wave_results = await self._execute_wave(plan_id, ready, results, wave)

                    failures = []
                    for node_id, status, result in wave_results:
                        results[node_id] = result
                        if status == "failed":
                            failures.append((node_id, result))

                    # Replan on failure
                    if failures and replan_enabled and replan_count < max_replans:
                        replan_count += 1
                        action = await self._replan(plan_id, task_desc, failures, replan_count, max_replans)
                        if action == "abort":
                            break
                        elif action == "retry":
                            for nid, _ in failures:
                                await db.update_node_status(nid, "pending")
                                results.pop(nid, None)

        except TimeoutError:
            logger.warning(f"ExecutionEngine timeout — plan {plan_id}")
            await db.update_plan_status(plan_id, "failed")

        # Determine final status
        state = await db.get_plan_state(plan_id)
        nodes = state.get("nodes", []) if state else []
        all_done = all(n["status"] in ("success", "skipped", "failed") for n in nodes)
        any_failed = any(n["status"] == "failed" for n in nodes)

        final_status = "completed" if all_done and not any_failed else "failed" if any_failed else "completed"
        await db.update_plan_status(plan_id, final_status)

        # Format output
        mermaid = await db.get_plan_mermaid(plan_id)
        output = [f"## Plan Execution: {task_desc}", f"Plan ID: `{plan_id}` | Status: {final_status}"]
        if replan_count:
            output.append(f"Replanned {replan_count} time(s).")
        output.append(f"\n```mermaid\n{mermaid}\n```\n")

        for node in nodes:
            status_icon = {"success": "OK", "failed": "FAIL", "pending": "SKIP",
                           "skipped": "SKIP", "running": "RUN"}.get(node["status"], "?")
            output.append(f"### [{status_icon}] {node['id']}")
            output.append(f"**Result:** {node.get('result', '[not executed]')[:800]}\n")

        return "\n".join(output)

    async def _execute_wave(self, plan_id, ready_nodes, prior_results, wave):
        """Execute a wave of ready nodes concurrently."""
        from tools import sqlite_store as db

        async def _exec_node(node):
            async with self.semaphore:
                return await self._execute_node(plan_id, node, prior_results, wave)

        tasks = [asyncio.create_task(_exec_node(n)) for n in ready_nodes]
        try:
            return await asyncio.gather(*tasks)
        except (asyncio.CancelledError, TimeoutError):
            for t in tasks:
                if not t.done():
                    t.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            raise

    async def _execute_node(self, plan_id, node, prior_results, wave):
        """Execute a single node, persist status to SQLite."""
        from tools import sqlite_store as db
        node_id = node["id"]
        model = node.get("model", "gemini") or "gemini"
        prompt = node["prompt"]

        await db.update_node_status(node_id, "running")

        # Build context from dependencies
        state = await db.get_plan_state(plan_id)
        edges = state.get("edges", []) if state else []
        dep_ids = [e["from_node"] for e in edges if e["to_node"] == node_id]

        dep_context = ""
        if dep_ids:
            parts = []
            for did in dep_ids:
                if did in prior_results:
                    parts.append(f"Result from '{did}': {prior_results[did][:500]}")
            dep_context = "\n".join(parts)

        full_prompt = f"{dep_context}\n\n{prompt}".strip() if dep_context else prompt

        logger.info(f"ExecutionEngine wave {wave}: node '{node_id}' on {model}")
        try:
            result = await self.router.consult_model(model, full_prompt, interrupt_event=self.interrupt_event)
            if isinstance(result, str) and (result.startswith("[Error") or result.startswith("[Consult error")):
                await db.update_node_status(node_id, "failed", error=result)
                return node_id, "failed", result
            await db.update_node_status(node_id, "success", result=str(result)[:5000])
            return node_id, "success", str(result)
        except Exception as e:
            error_msg = f"[Error: {e}]"
            await db.update_node_status(node_id, "failed", error=error_msg)
            return node_id, "failed", error_msg

    async def _replan(self, plan_id, task_desc, failures, replan_count, max_replans):
        """Pull relevant experiences from memory before consulting Gemini for replan."""
        # Pull relevant experience context
        experience_context = ""
        try:
            from tools.memory_backend import get_backend
            backend = get_backend()
            relevant = await backend.search_episodes(task_desc, limit=3)
            if relevant:
                experience_context = "RELEVANT PAST EXPERIENCES:\n"
                for ep in relevant:
                    experience_context += f"- {ep.get('task', '?')}: {ep.get('lesson', 'no lesson')} (outcome: {ep.get('outcome', '?')})\n"
                experience_context += "\n"
        except Exception as e:
            logger.debug(f"Failed to load past experiences for replan context: {e}")

        failure_context = "\n".join(f"Node '{nid}' failed: {result[:200]}" for nid, result in failures)
        replan_prompt = (
            f"Task: {task_desc}\n\n"
            f"{experience_context}"
            f"Failures:\n{failure_context}\n\n"
            f"Replan attempt {replan_count}/{max_replans}.\n"
            f"Options: skip the failed step, retry, or abort.\n"
            f"Respond with JSON: {{\"action\": \"skip\"|\"retry\"|\"abort\", \"reason\": \"...\"}}"
        )

        try:
            result = await self.router.consult_model(
                "gemini", replan_prompt,
                max_rounds=1, interrupt_event=self.interrupt_event,
            )
            try:
                data = json.loads(result) if isinstance(result, str) else {}
                return data.get("action", "skip")
            except (json.JSONDecodeError, Exception):
                return "skip"
        except Exception:
            return "skip"


async def _plan_and_execute_inner(input_data: dict) -> str:
    """Inner implementation of plan_and_execute — delegates to ExecutionEngine."""
    task_desc = input_data.get("task", "")
    subtasks = input_data.get("subtasks", [])
    plan_id = input_data.get("plan_id", uuid.uuid4().hex[:12])
    replan_enabled = input_data.get("replan", False)
    resume = input_data.get("resume", False)

    engine = ExecutionEngine(_router, _interrupt_event)
    return await engine.execute(plan_id, task_desc, subtasks, replan_enabled, resume)


async def _resume_plan(input_data: dict) -> str:
    """Resume an interrupted execution plan from SQLite."""
    if not _router:
        return "[Error: Router not initialized]"

    plan_id = input_data.get("plan_id", "")
    if not plan_id:
        # List interrupted plans
        try:
            from tools.sqlite_store import get_interrupted_plans
            plans = await get_interrupted_plans()
            if not plans:
                return "No interrupted plans found."
            lines = ["Interrupted plans:"]
            for p in plans:
                lines.append(f"  - `{p['id']}`: {p['task_description'][:80]} (updated: {p['updated_at']})")
            return "\n".join(lines)
        except Exception as e:
            return f"[Error listing plans: {e}]"

    try:
        from tools.sqlite_store import get_plan_state
        state = await get_plan_state(plan_id)
        if not state:
            return f"Plan '{plan_id}' not found."

        # Rebuild subtasks from persisted nodes/edges
        subtasks = []
        edges = state.get("edges", [])
        for node in state.get("nodes", []):
            deps = [e["from_node"] for e in edges if e["to_node"] == node["id"]]
            subtasks.append({
                "id": node["id"],
                "prompt": node["prompt"],
                "model": node.get("model", "gemini"),
                "depends_on": deps,
            })

        engine = ExecutionEngine(_router, _interrupt_event)
        return await engine.execute(plan_id, state["task_description"], subtasks,
                                    replan_enabled=True, resume=True)
    except Exception as e:
        return f"[Error resuming plan: {e}]"


async def _plan_and_execute(input_data: dict) -> str:
    """Decompose a task into a DAG of subtasks and execute with parallel dispatch.
    Supports replanning on failure and background execution."""
    if not _router:
        return "[Error: Router not initialized]"

    subtasks = input_data.get("subtasks", [])
    if not subtasks:
        return "[Error: 'subtasks' array required]"

    background = input_data.get("background", False)

    if not background:
        return await _plan_and_execute_inner(input_data)

    # --- Background mode ---
    _cleanup_stale_tasks()
    if _count_running_tasks() >= config.MAX_BACKGROUND_TASKS:
        return f"[Error: Maximum background tasks ({config.MAX_BACKGROUND_TASKS}) reached. Use check_background_task or wait for tasks to complete.]"

    task_id = _generate_task_id()
    interrupt = _interrupt_event
    task_desc = input_data.get("task", "")

    async def _bg_plan():
        entry = _background_tasks[task_id]
        try:
            result = await _plan_and_execute_inner(input_data)
            entry["status"] = "completed"
            entry["result"] = result
        except Exception as e:
            entry["status"] = "error"
            entry["result"] = f"[Error: {e}]"
            logger.error(f"Background plan_and_execute {task_id} failed: {e}")
        finally:
            entry["completed_at"] = time.monotonic()

    asyncio_task = asyncio.create_task(_bg_plan())
    _background_tasks[task_id] = {
        "task": asyncio_task,
        "status": "running",
        "result": None,
        "tool": "plan_and_execute",
        "model": "multi",
        "prompt_preview": task_desc[:80],
        "started_at": time.monotonic(),
        "completed_at": None,
    }

    return (
        f"Background task spawned: **{task_id}**\n"
        f"Tool: plan_and_execute | Subtasks: {len(subtasks)}\n"
        f"Use `check_background_task(task_id=\"{task_id}\")` to poll results, "
        f"or `list_background_tasks()` to see all running tasks."
    )


async def _parallel_consult_inner(input_data: dict) -> str:
    """Inner implementation of parallel_consult (runs the gather)."""
    tasks_list = input_data.get("tasks", [])

    # Concurrency semaphore to respect API rate limits
    semaphore = asyncio.Semaphore(4)

    async def _run_one(idx: int, task_spec: dict) -> dict:
        async with semaphore:
            model = task_spec.get("model", "gemini")
            prompt = task_spec.get("prompt", "")
            context = task_spec.get("context", "")
            full_prompt = f"{context}\n\n{prompt}".strip() if context else prompt
            allowed_tools = task_spec.get("tools")
            max_rounds = task_spec.get("max_rounds")

            logger.info(f"Parallel consult [{idx+1}/{len(tasks_list)}] → {model}: {full_prompt[:80]}...")

            try:
                result = await _router.consult_model(
                    model, full_prompt,
                    allowed_tools=allowed_tools,
                    max_rounds=max_rounds,
                    interrupt_event=_interrupt_event,
                )
                return {"index": idx, "model": model, "status": "success", "result": result}
            except Exception as e:
                logger.error(f"Parallel consult [{idx+1}] failed: {e}")
                return {"index": idx, "model": model, "status": "error", "result": f"[Error: {e}]"}

    # Dispatch all tasks concurrently with overall timeout
    tasks = [asyncio.create_task(_run_one(i, spec)) for i, spec in enumerate(tasks_list)]
    try:
        async with asyncio.timeout(450):
            results = await asyncio.gather(*tasks, return_exceptions=False)
    except TimeoutError:
        logger.warning("parallel_consult hit overall timeout (450s)")
        # Explicitly cancel all tasks
        for t in tasks:
            if not t.done():
                t.cancel()
        # Wait for cancellation to propagate
        await asyncio.gather(*tasks, return_exceptions=True)
        return "[parallel_consult timed out after 450s — all sub-agents cancelled]"

    # Format aggregated results
    output_parts = []
    for r in sorted(results, key=lambda x: x["index"]):
        idx = r["index"]
        model = r["model"]
        status = r["status"]
        result_text = r["result"]
        prompt_preview = tasks_list[idx].get("prompt", "")[:60]
        output_parts.append(
            f"--- Task {idx+1} ({model}, {status}) ---\n"
            f"Prompt: {prompt_preview}...\n"
            f"Result: {result_text}\n"
        )

    successes = sum(1 for r in results if r["status"] == "success")
    header = f"Parallel consult complete: {successes}/{len(tasks_list)} succeeded\n\n"
    return header + "\n".join(output_parts)


async def _parallel_consult(input_data: dict) -> str:
    """Dispatch up to 4 sub-agent calls concurrently. Supports background mode."""
    if not _router:
        return "[Error: Router not initialized — parallel_consult unavailable]"

    tasks_list = input_data.get("tasks", [])
    if not tasks_list:
        return "[Error: 'tasks' array required with {model, prompt} objects]"
    if len(tasks_list) > 4:
        return "[Error: Maximum 4 parallel tasks allowed]"

    background = input_data.get("background", False)

    if not background:
        return await _parallel_consult_inner(input_data)

    # --- Background mode ---
    _cleanup_stale_tasks()
    if _count_running_tasks() >= config.MAX_BACKGROUND_TASKS:
        return f"[Error: Maximum background tasks ({config.MAX_BACKGROUND_TASKS}) reached. Use check_background_task or wait for tasks to complete.]"

    task_id = _generate_task_id()
    models = ", ".join(t.get("model", "?") for t in tasks_list)

    async def _bg_parallel():
        entry = _background_tasks[task_id]
        try:
            result = await _parallel_consult_inner(input_data)
            entry["status"] = "completed"
            entry["result"] = result
        except Exception as e:
            entry["status"] = "error"
            entry["result"] = f"[Error: {e}]"
            logger.error(f"Background parallel_consult {task_id} failed: {e}")
        finally:
            entry["completed_at"] = time.monotonic()

    asyncio_task = asyncio.create_task(_bg_parallel())
    _background_tasks[task_id] = {
        "task": asyncio_task,
        "status": "running",
        "result": None,
        "tool": "parallel_consult",
        "model": models,
        "prompt_preview": f"{len(tasks_list)} parallel tasks",
        "started_at": time.monotonic(),
        "completed_at": None,
    }

    return (
        f"Background task spawned: **{task_id}**\n"
        f"Tool: parallel_consult | Models: {models} | Tasks: {len(tasks_list)}\n"
        f"Use `check_background_task(task_id=\"{task_id}\")` to poll results, "
        f"or `list_background_tasks()` to see all running tasks."
    )


# ============================================================
# Background task management tools
# ============================================================

async def _check_background_task(input_data: dict) -> str:
    """Check status or retrieve result of a background task."""
    _cleanup_stale_tasks()

    task_id = input_data.get("task_id", "")
    wait = input_data.get("wait", False)

    if task_id not in _background_tasks:
        return f"[Error: Unknown task ID '{task_id}'. Use list_background_tasks to see active tasks.]"

    entry = _background_tasks[task_id]
    elapsed = time.monotonic() - entry["started_at"]

    # If wait requested and task is still running, block up to 60s
    if wait and entry["status"] == "running":
        try:
            await asyncio.wait_for(asyncio.shield(entry["task"]), timeout=60.0)
        except (asyncio.TimeoutError, Exception):
            pass  # fall through to return current status
        elapsed = time.monotonic() - entry["started_at"]

    if entry["status"] == "running":
        return (
            f"Task **{task_id}**: RUNNING ({elapsed:.0f}s elapsed)\n"
            f"Tool: {entry['tool']} | Model: {entry['model']}\n"
            f"Prompt: {entry['prompt_preview']}..."
        )
    elif entry["status"] == "completed":
        return (
            f"Task **{task_id}**: COMPLETED ({elapsed:.0f}s)\n"
            f"Tool: {entry['tool']} | Model: {entry['model']}\n\n"
            f"Result:\n{entry['result']}"
        )
    else:  # error
        return (
            f"Task **{task_id}**: ERROR ({elapsed:.0f}s)\n"
            f"Tool: {entry['tool']} | Model: {entry['model']}\n\n"
            f"Error:\n{entry['result']}"
        )


async def _list_background_tasks(input_data: dict) -> str:
    """List all background tasks with status summary."""
    _cleanup_stale_tasks()

    if not _background_tasks:
        return "No background tasks."

    lines = ["## Background Tasks\n"]
    lines.append(f"{'ID':<10} {'Status':<12} {'Tool':<20} {'Model':<15} {'Elapsed':<10} {'Preview'}")
    lines.append("-" * 90)

    for tid, entry in _background_tasks.items():
        elapsed = time.monotonic() - entry["started_at"]
        status = entry["status"].upper()
        lines.append(
            f"{tid:<10} {status:<12} {entry['tool']:<20} {entry['model']:<15} "
            f"{elapsed:>6.0f}s    {entry['prompt_preview'][:40]}"
        )

    running = _count_running_tasks()
    total = len(_background_tasks)
    lines.append(f"\n{running} running / {total} total (max {config.MAX_BACKGROUND_TASKS})")

    return "\n".join(lines)


async def cleanup_background_tasks():
    """Cancel all running background asyncio tasks."""
    for tid, entry in list(_background_tasks.items()):
        task = entry.get("task")
        if task and not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logger.debug(f"Background task {tid} raised an error during cancellation: {e}")
    _background_tasks.clear()
    logger.info("All background tasks cleaned up.")


async def _collaborative_consult(input_data: dict) -> str:
    """Multi-agent collaboration with independent, debate, and synthesis modes."""
    if not _router:
        return "[Error: Router not initialized]"

    task = input_data.get("task", "")
    mode = input_data.get("mode", "synthesis")
    agents = input_data.get("agents", [])
    max_rounds = min(int(input_data.get("rounds", 2)), 3)

    if len(agents) < 2:
        return "[Error: At least 2 agents required]"
    if len(agents) > 4:
        agents = agents[:4]

    # Phase 1: Independent parallel run
    async def _run_agent(agent, context=""):
        persona = agent.get("persona", "general assistant")
        model = agent.get("model", "gemini")
        prompt = f"You are a {persona}.\n\n"
        if context:
            prompt += f"PRIOR DEBATE CONTEXT:\n{context}\n\n"
        prompt += f"Task: {task}\n\nProvide your analysis and recommendations."

        try:
            result = await _router.consult_model(model, prompt, interrupt_event=_interrupt_event)
            return {"persona": persona, "model": model, "response": str(result)}
        except Exception as e:
            return {"persona": persona, "model": model, "response": f"[Error: {e}]"}

    # Initial parallel run
    initial_tasks = [asyncio.create_task(_run_agent(a)) for a in agents]
    initial_results = await asyncio.gather(*initial_tasks)

    if mode == "independent":
        # Just return parallel results
        output = [f"## Collaborative Consult (independent mode)\n**Task:** {task}\n"]
        for r in initial_results:
            output.append(f"### {r['persona']} ({r['model']})")
            output.append(f"{r['response'][:800]}\n")
        return "\n".join(output)

    # Phase 2: Debate rounds (agents see each other's outputs and refine)
    current_results = initial_results
    for round_num in range(1, max_rounds + 1):
        debate_context = "\n".join(
            f"[{r['persona']}]: {r['response'][:500]}"
            for r in current_results
        )

        debate_tasks = [
            asyncio.create_task(_run_agent(a, f"Round {round_num} debate:\n{debate_context}"))
            for a in agents
        ]
        current_results = await asyncio.gather(*debate_tasks)

    if mode == "debate":
        output = [f"## Collaborative Consult (debate mode, {max_rounds} rounds)\n**Task:** {task}\n"]
        for r in current_results:
            output.append(f"### {r['persona']} ({r['model']})")
            output.append(f"{r['response'][:800]}\n")
        return "\n".join(output)

    # Phase 3: Synthesis — aggregate all outputs
    all_outputs = "\n\n".join(
        f"[{r['persona']}]: {r['response'][:800]}"
        for r in current_results
    )

    synthesis_prompt = (
        f"You are a synthesis agent. Multiple experts have analyzed a task and debated.\n\n"
        f"Task: {task}\n\n"
        f"EXPERT OUTPUTS (after {max_rounds} debate rounds):\n{all_outputs}\n\n"
        f"Your job: Produce a UNIFIED answer that:\n"
        f"1. Resolves any conflicts between experts\n"
        f"2. Combines the best insights from each\n"
        f"3. Provides a clear, actionable recommendation\n"
        f"4. Notes any unresolved disagreements"
    )

    try:
        synthesis = await _router.consult_model("gemini", synthesis_prompt, interrupt_event=_interrupt_event)
    except Exception as e:
        synthesis = f"[Synthesis failed: {e}]"

    output = [f"## Collaborative Consult (synthesis mode, {max_rounds} debate rounds)\n**Task:** {task}\n"]
    output.append("### Individual Expert Outputs")
    for r in current_results:
        output.append(f"**{r['persona']}** ({r['model']}): {r['response'][:400]}...")
    output.append(f"\n### Synthesized Answer")
    output.append(str(synthesis)[:2000])

    return "\n".join(output)


# ============================================================
# Orchestration tools
# ============================================================

async def _orchestrate(input_data: dict) -> str:
    """Execute a complex task using coordinated multi-agent orchestration."""
    if not _router:
        return "[Error: Router not initialized — orchestrate unavailable]"

    task = input_data.get("task", "")
    if not task:
        return "[Error: 'task' required]"

    mode = input_data.get("mode", "auto")
    agents = input_data.get("agents")
    subtasks = input_data.get("subtasks")
    resolve_conflicts = input_data.get("resolve_conflicts", True)

    try:
        orch = _get_orchestrator()
        result = await orch.execute(
            task=task,
            mode=mode,
            agent_roles=agents,
            subtasks=subtasks,
            resolve_conflicts=resolve_conflicts,
        )
        return result
    except Exception as e:
        logger.error(f"Orchestration failed: {e}", exc_info=True)
        return f"[Orchestration error: {e}]"


async def _check_task_progress(input_data: dict) -> str:
    """Check progress of an orchestrated task."""
    task_id = input_data.get("task_id", "")
    if not task_id:
        return "[Error: 'task_id' required]"

    try:
        orch = _get_orchestrator()
        if orch is None:
            # No router wired — try the file-based task graph directly
            from .task_graph import get_graph_progress
            progress = get_graph_progress(task_id)
            if not progress:
                return f"[Task '{task_id}' not found, and orchestrator not initialized — try list_background_tasks]"
            return f"## Task: {task_id} (read-only, orchestrator unwired)\nCompletion: {progress.get('percent', 0):.0f}% — {progress.get('completed', 0)}/{progress.get('total', 0)}"
        progress = orch.get_task_progress(task_id)
        if progress:
            lines = [f"## Task Progress: {task_id}"]
            lines.append(f"Completion: {progress['percent']:.0f}%")
            lines.append(f"Completed: {progress['completed']}/{progress['total']}")
            if progress['pending'] > 0:
                lines.append(f"Pending: {progress['pending']}")
            if progress['failed'] > 0:
                lines.append(f"Failed: {progress['failed']}")
            if progress['blocked'] > 0:
                lines.append(f"Blocked: {progress['blocked']}")
            if progress['in_progress'] > 0:
                lines.append(f"In Progress: {progress['in_progress']}")
            return "\n".join(lines)
        else:
            from .task_graph import get_graph_progress
            progress = get_graph_progress(task_id)
            if progress:
                return f"Progress: {progress['percent']:.0f}% ({progress['completed']}/{progress['total']})"
            return f"[Error: Task graph '{task_id}' not found]"
    except Exception as e:
        logger.error(f"Progress check failed: {e}")
        return f"[Error: {e}]"


async def _get_agent_status(input_data: dict) -> str:
    """Get status of specialist agents."""
    agent_role = input_data.get("agent_role")

    try:
        orch = _get_orchestrator()
        if agent_role:
            status = orch.get_agent_status(agent_role)
            lines = [f"## Agent: {agent_role}"]
            if status.get("task_history"):
                lines.append("\n### Recent Tasks")
                for t in status["task_history"][-3:]:
                    icon = "OK" if t.get("success") else "FAIL"
                    lines.append(f"  [{icon}] {t.get('task', '?')[:60]}")
            if status.get("confidence_profile"):
                lines.append("\n### Confidence Profile")
                for task_type, profile in status["confidence_profile"].items():
                    if profile.get("total", 0) > 0:
                        conf = profile["success"] / profile["total"]
                        lines.append(f"  {task_type}: {conf:.0%} ({profile['success']}/{profile['total']})")
            return "\n".join(lines)
        else:
            all_status = orch.get_agent_status()
            lines = ["## Agent Status Overview\n"]
            for role, status in all_status.items():
                task_count = len(status.get("task_history", []))
                lines.append(f"### {role.title()}")
                lines.append(f"  Tasks completed: {task_count}")
                if status.get("confidence_profile"):
                    total_tasks = sum(p.get("total", 0) for p in status["confidence_profile"].values())
                    total_success = sum(p.get("success", 0) for p in status["confidence_profile"].values())
                    if total_tasks > 0:
                        lines.append(f"  Success rate: {total_success/total_tasks:.0%}")
                lines.append("")
            return "\n".join(lines) if len(lines) > 1 else "No agent status available"
    except Exception as e:
        logger.error(f"Agent status check failed: {e}")
        return f"[Error: {e}]"


TOOL_HANDLERS = {
    "get_current_time": _get_current_time,
    "system_status": _system_status,
    "switch_model": _switch_model,
    "run_skill": _run_skill,
    "consult": _consult,
    "parallel_consult": _parallel_consult,
    "plan_and_execute": _plan_and_execute,
    "resume_plan": _resume_plan,
    "collaborative_consult": _collaborative_consult,
    "check_background_task": _check_background_task,
    "list_background_tasks": _list_background_tasks,
    "orchestrate": _orchestrate,
    "check_task_progress": _check_task_progress,
    "get_agent_status": _get_agent_status,
}
