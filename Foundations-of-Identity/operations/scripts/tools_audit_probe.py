"""Tools-audit probe runner — exercises each daemon tool's safest action.

For each tool in _TOOL_HANDLERS, runs a read-only / safe probe action and
records (a) whether it returned, (b) excerpt of output, (c) elapsed time,
(d) declared state from tool_states.json. Writes a structured report.

Run from clawd-local:
    python operations/scripts/tools_audit_probe.py
"""
import asyncio
import io
import json
import os
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
os.environ.setdefault("CLAWD_HOME", r"C:\Users\mercu\clawd")
os.environ.setdefault("CLAWD_DAEMON", r"C:\Users\mercu\clawd-daemon")
sys.path.insert(0, r"C:\Users\mercu\clawd-daemon")

CLAWD_HOME = Path(os.environ["CLAWD_HOME"])
REPORT_PATH = CLAWD_HOME / "palace" / "southwest" / f"tools-audit-probe-{datetime.now().strftime('%Y-%m-%d')}.md"
TOOL_STATES_PATH = CLAWD_HOME / "memory" / "tool_states.json"

# Safe probe action per tool. Maps tool_name -> (action_dict, expected_substr_in_output).
# Tools without an entry are skipped (typically: ones that need real arguments / external resources).
PROBES = {
    "anomaly_tracker": ({"action": "list"}, None),
    "avatar_control": ({"action": "ping"}, "127.0.0.1"),
    "bridge_distance": ({"text_a": "axiom theorem corpus", "text_b": "axiom theorem manifold"}, "VERDICT"),
    "browser": ({"action": "info"}, None),
    "check_background_task": ({"task_id": "nonexistent-probe"}, None),
    "check_task_progress": ({"task_id": "nonexistent-probe"}, None),
    "clear_trigger": ({"trigger_id": "nonexistent-probe"}, None),
    "clipboard": ({"action": "read"}, None),
    "cognitive_dsl": ({"action": "summary"}, "PREDICT"),
    "consolidate_memory": None,  # heavy - skip
    "coordinate_heartbeat": ({"action": "list_threads"}, None),
    "corpus_search": ({"action": "info"}, "chunks"),
    "create_tool": None,  # needs arguments
    "dashboard": ({"action": "weekly"}, None),
    "deep_research": None,  # heavy - skip
    "desktop": None,  # GUI side-effect
    "email_send": ({"action": "status"}, "credentials"),
    "evolve_artifact": None,  # speculative
    "experience": ({"action": "patterns"}, None),
    "get_agent_status": ({"agent_name": "test"}, None),
    "get_current_time": ({}, None),
    "goals": ({"action": "list"}, "Priority"),
    "knowledge_graph": ({"action": "list"}, "Entities"),
    "list_background_tasks": ({}, None),
    "list_custom_tools": ({}, None),
    "list_triggers": ({}, None),
    "manage_process": ({"action": "list"}, None),
    "market_data": ({"action": "price", "symbol": "BTC-USD"}, None),
    "memory_agent": ({"action": "prune"}, "Prune"),
    "memory_categories": ({"action": "list"}, None),
    "memory_extract": None,  # needs content
    "memory_items": ({"action": "list", "limit": 1}, None),
    "memory_search": ({"query": "coherence"}, None),
    "memory_update": None,  # mutating
    "memory_version": ({"action": "status"}, None),
    "meta_agent": ({"action": "status"}, "cycles"),
    "monitor_health": ({"action": "check"}, None),
    "orchestrate": None,  # heavy
    "parallel_consult": None,  # heavy
    "plan_and_execute": None,  # heavy
    "python_eval": ({"code": "result = 2 + 2"}, "4"),
    "reflect": ({"action": "review_learnings"}, None),
    "resume_plan": ({"action": "list"}, None),
    "rollback": ({"action": "list_checkpoints"}, None),
    "run_skill": None,  # needs skill name
    "schedule": ({"action": "list"}, "Scheduled"),
    "screenshot": None,  # GUI side-effect; skip
    "search_web": None,  # network heavy
    "self_control": ({"action": "restart_status"}, None),
    "self_improve": ({"action": "analyze"}, "Success"),
    "send_sticker": None,  # external side-effect
    "send_telegram": None,  # external side-effect
    "set_trigger": None,  # mutating
    "shell": ({"command": "echo probe"}, "probe"),
    "skill_library": ({"action": "list"}, None),
    "speak": None,  # audio side-effect
    "switch_model": None,  # mutating
    "system_status": ({"action": "summary"}, None),
    "verify_action": None,  # needs action context
    "voice_input": ({"action": "info"}, None),
    "web_request": None,  # network heavy
    "wolfram": None,  # heavy
    "working_memory": ({"action": "view"}, None),
    "wsl": ({"command": "echo wsl-probe"}, "wsl-probe"),
    "code_action": None,  # candidate-for-retirement, skip
    "collaborative_consult": None,  # heavy
    "consult": None,  # heavy
}


async def probe_tool(tools_pkg, name, probe_input, expected):
    t0 = time.time()
    try:
        result = await asyncio.wait_for(
            tools_pkg.execute_tool(name, probe_input, beat_number=0),
            timeout=30.0,
        )
        elapsed = time.time() - t0
        if isinstance(result, str):
            output = result
        else:
            output = json.dumps(result, default=str)[:1000]
        ok = True
        match_ok = (expected is None) or (expected.lower() in output.lower())
        return {
            "status": "OK" if match_ok else "OK_NO_MATCH",
            "elapsed_s": round(elapsed, 2),
            "output_excerpt": output[:280].replace("\n", " | "),
            "expected": expected,
        }
    except asyncio.TimeoutError:
        return {"status": "TIMEOUT", "elapsed_s": 30.0, "output_excerpt": "", "expected": expected}
    except Exception as e:
        return {
            "status": "ERROR",
            "elapsed_s": round(time.time() - t0, 2),
            "output_excerpt": f"{type(e).__name__}: {e}"[:280],
            "expected": expected,
        }


async def main():
    import tools as tools_pkg
    try:
        tools_pkg.init_custom_tools()
    except Exception:
        pass

    # Optionally wire router for memory_agent
    try:
        from models import ModelRouter
        from tools import memory_agent as _ma
        router = ModelRouter()
        if hasattr(_ma, "set_router"):
            _ma.set_router(router)
        else:
            _ma._router = router
    except Exception as e:
        print(f"[router wire skipped: {e}]")

    declarations = {}
    if TOOL_STATES_PATH.exists():
        declarations = json.loads(TOOL_STATES_PATH.read_text(encoding="utf-8")).get("tools", {})

    handlers = tools_pkg._TOOL_HANDLERS
    tool_names = sorted(handlers.keys())

    results = {}
    print(f"# Probing {len(tool_names)} tools...")
    for name in tool_names:
        probe = PROBES.get(name)
        if probe is None:
            results[name] = {
                "status": "SKIPPED",
                "reason": "no safe probe (heavy / mutating / external / requires args)",
                "declared_state": declarations.get(name, {}).get("state", "(undeclared)"),
            }
            print(f"  {name}: SKIPPED")
            continue
        probe_input, expected = probe
        outcome = await probe_tool(tools_pkg, name, probe_input, expected)
        outcome["declared_state"] = declarations.get(name, {}).get("state", "(undeclared)")
        results[name] = outcome
        marker = "✓" if outcome["status"] in ("OK",) else ("?" if outcome["status"] == "OK_NO_MATCH" else "✗")
        print(f"  {marker} {name}: {outcome['status']} ({outcome['elapsed_s']}s)")

    # Build report
    lines = [
        f"# Tools Audit Probe — {datetime.now().strftime('%Y-%m-%d %H:%M PST')}",
        "",
        f"Probed {len(tool_names)} registered daemon tools.",
        "",
        "## Status counts",
        "",
    ]
    counts = {}
    for r in results.values():
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    for s, c in sorted(counts.items(), key=lambda x: -x[1]):
        lines.append(f"- **{s}**: {c}")
    lines.extend(["", "## Per-tool detail", "", "| Tool | Status | Declared | Elapsed | Output excerpt |", "|------|--------|----------|---------|----------------|"])
    for name in tool_names:
        r = results[name]
        if r["status"] == "SKIPPED":
            lines.append(f"| `{name}` | SKIPPED | {r['declared_state']} | — | {r['reason']} |")
        else:
            excerpt = r["output_excerpt"].replace("|", "\\|")[:200]
            lines.append(f"| `{name}` | {r['status']} | {r['declared_state']} | {r['elapsed_s']}s | {excerpt} |")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nReport: {REPORT_PATH}")

if __name__ == "__main__":
    asyncio.run(main())
