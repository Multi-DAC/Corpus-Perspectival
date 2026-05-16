"""Proactive Memory Agent — LLM-powered memory dreaming and recombination.

Extends consolidation with creative phases:
- cross_pollinate: Find unexpected connections between memory categories
- synthesize: Distill experiences into higher-level principles
- dream: Generate creative suggestions from goal+experience pairs
- prune: Remove low-confidence, unused items and check contradictions
- strengthen: Boost items aligned with active goals
- full_cycle: Run all phases sequentially
"""
import json
import logging
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import config

logger = logging.getLogger("clawd.tools.memory_agent")


async def _send_to_router(router, prompt: str, max_tokens: int = 500) -> str:
    """Send a prompt to the router and get a text response.
    A33: Log failures at WARNING level and return structured error."""
    try:
        response = await router.send_oneshot(prompt)
        return response.text.strip()
    except Exception as e:
        logger.warning(f"Memory agent router call failed: {type(e).__name__}: {e}")
        return f"[ROUTER_ERROR: {type(e).__name__}]"


def _load_json_file(path: Path) -> list | dict:
    """Load a JSON file, return empty list/dict on failure."""
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data
    except Exception:
        return []


def _save_json_file(path: Path, data):
    """Save data to JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def _load_memory_items() -> list[dict]:
    """Load all memory items from disk."""
    items = []
    if config.MEMORY_ITEMS_DIR.is_dir():
        for fpath in config.MEMORY_ITEMS_DIR.glob("*.json"):
            if fpath.name == "_index.json":
                continue
            try:
                items.append(json.loads(fpath.read_text(encoding="utf-8")))
            except Exception:
                continue
    return items


# ============================================================
# Phase: Cross-Pollinate
# ============================================================

async def _cross_pollinate(router=None) -> str:
    """Find unexpected connections between items from different categories."""
    items = _load_memory_items()
    if len(items) < 6:
        return "Not enough memory items for cross-pollination (need 6+)."

    # Group by category
    by_cat = {}
    for item in items:
        for cat in item.get("categories", ["general"]):
            by_cat.setdefault(cat, []).append(item)

    cats = [c for c in by_cat if len(by_cat[c]) >= 2 and c not in ("auto-extracted", "general")]
    if len(cats) < 2:
        return "Not enough distinct categories for cross-pollination."

    # Pick 2 random different categories
    cat_pair = random.sample(cats, min(2, len(cats)))
    items_a = random.sample(by_cat[cat_pair[0]], min(3, len(by_cat[cat_pair[0]])))
    items_b = random.sample(by_cat[cat_pair[1]], min(3, len(by_cat[cat_pair[1]])))

    connections_found = 0

    if router:
        # LLM-assisted connection finding
        prompt = (
            f"I have memory items from two different categories.\n\n"
            f"Category '{cat_pair[0]}':\n"
            + "\n".join(f"- {i['content'][:150]}" for i in items_a)
            + f"\n\nCategory '{cat_pair[1]}':\n"
            + "\n".join(f"- {i['content'][:150]}" for i in items_b)
            + "\n\nFind 1-3 unexpected connections or relationships between items across these categories. "
            "For each connection, output one line: CONNECTION: [item_a_summary] <-> [item_b_summary]: [relationship]"
        )
        response = await _send_to_router(router, prompt)
        if response:
            # Add connections to knowledge graph
            try:
                from tools.knowledge_graph import add_edge_raw
                for line in response.split("\n"):
                    if "CONNECTION:" in line.upper() or "<->" in line:
                        add_edge_raw(
                            cat_pair[0], cat_pair[1], "cross_pollinated",
                            {"detail": line.strip()[:200], "timestamp": datetime.now().isoformat()}
                        )
                        connections_found += 1
            except Exception as e:
                logger.debug(f"KG edge creation failed: {e}")
    else:
        # Rule-based: check keyword overlap
        for a in items_a:
            for b in items_b:
                kw_a = set(a.get("keywords", []))
                kw_b = set(b.get("keywords", []))
                overlap = kw_a & kw_b
                if len(overlap) >= 2:
                    try:
                        from tools.knowledge_graph import add_edge_raw
                        add_edge_raw(
                            a.get("id", ""), b.get("id", ""), "keyword_overlap",
                            {"shared_keywords": list(overlap)}
                        )
                        connections_found += 1
                    except Exception as e:
                        logger.debug(f"Failed to add knowledge graph edge during cross-pollination: {e}")

    return f"Cross-pollination between '{cat_pair[0]}' and '{cat_pair[1]}': {connections_found} new connections found."


# ============================================================
# Phase: Synthesize
# ============================================================

async def _synthesize(router=None) -> str:
    """Group experiences by category, synthesize higher-level principles."""
    experiences = _load_json_file(config.MEMORY_DIR / "experiences.json")
    if len(experiences) < 5:
        return "Not enough experiences for synthesis (need 5+)."

    # Group by category
    by_cat = {}
    for e in experiences:
        cat = e.get("category", "general")
        by_cat.setdefault(cat, []).append(e)

    # Find categories with 5+ experiences
    rich_cats = [(c, exps) for c, exps in by_cat.items() if len(exps) >= 5]
    if not rich_cats:
        return "No categories have enough experiences (5+) for synthesis."

    principles_file = config.MEMORY_DIR / "principles.json"
    principles = _load_json_file(principles_file)
    if not isinstance(principles, list):
        principles = []
    existing_texts = {p.get("principle", "").lower() for p in principles}

    new_count = 0
    for cat, exps in rich_cats[:3]:
        top_exps = sorted(exps, key=lambda e: e.get("score", 0.5), reverse=True)[:10]

        if router:
            prompt = (
                f"These are {len(top_exps)} experiences from the '{cat}' category:\n\n"
                + "\n".join(
                    f"- Task: {e.get('task', '?')[:80]} | Outcome: {e.get('outcome', '?')} | "
                    f"Lesson: {e.get('lesson', 'none')[:100]}"
                    for e in top_exps
                )
                + "\n\nSynthesize ONE higher-level principle or skill that emerges from these experiences. "
                "Be specific and actionable. Output format: PRINCIPLE: [text]"
            )
            response = await _send_to_router(router, prompt)
            if response:
                for line in response.split("\n"):
                    if "PRINCIPLE:" in line.upper():
                        text = line.split(":", 1)[-1].strip()
                        if text.lower() not in existing_texts and len(text) > 15:
                            principles.append({
                                "id": len(principles) + 1,
                                "principle": text,
                                "derived_from": [e.get("id") for e in top_exps[:5]],
                                "category": cat,
                                "confidence": 0.6,
                                "times_applied": 0,
                                "success_rate_when_applied": 0,
                                "created": datetime.now().isoformat(),
                                "last_validated": datetime.now().isoformat(),
                                "source": "memory_agent_synthesis",
                            })
                            existing_texts.add(text.lower())
                            new_count += 1
                            break

    if new_count > 0:
        _save_json_file(principles_file, principles)

    return f"Synthesis complete: {new_count} new principles created from {len(rich_cats)} categories."


# ============================================================
# Phase: Dream
# ============================================================

async def _dream(router=None) -> str:
    """Generate creative suggestions from random goal+experience pairs."""
    if not router:
        return "Dream phase requires a router for LLM-powered creativity."

    goals = _load_json_file(config.MEMORY_DIR / "goals.json")
    experiences = _load_json_file(config.MEMORY_DIR / "experiences.json")

    active_goals = [g for g in goals if g.get("status") == "active"]
    if not active_goals or not experiences:
        return "Need active goals and experiences for dreaming."

    # Pick random pairs
    num_pairs = min(3, len(active_goals))
    pairs = []
    for _ in range(num_pairs):
        goal = random.choice(active_goals)
        exp = random.choice(experiences)
        pairs.append((goal, exp))

    suggestions = []
    for goal, exp in pairs:
        prompt = (
            f"Active goal: {goal.get('title', '?')} — {goal.get('description', '')[:100]}\n"
            f"Past experience: Task '{exp.get('task', '?')[:80]}' resulted in {exp.get('outcome', '?')}. "
            f"Lesson: {exp.get('lesson', 'none')[:100]}\n\n"
            f"What new approach or creative idea does this past experience suggest for advancing the goal? "
            f"Be specific and actionable. One sentence."
        )
        response = await _send_to_router(router, prompt)
        if response:
            suggestions.append({
                "goal_id": goal.get("id"),
                "goal_title": goal.get("title", ""),
                "experience_id": exp.get("id"),
                "suggestion": response[:300],
                "timestamp": datetime.now().isoformat(),
            })

    # Store suggestions in working memory scratch
    if suggestions:
        wm_file = config.MEMORY_DIR / "working_memory.json"
        try:
            wm = json.loads(wm_file.read_text(encoding="utf-8")) if wm_file.exists() else {}
            scratch = wm.get("scratch", {})
            existing_dreams = scratch.get("dream_suggestions", [])
            if isinstance(existing_dreams, str):
                existing_dreams = []
            existing_dreams.extend(suggestions)
            scratch["dream_suggestions"] = existing_dreams[-10:]  # Keep last 10
            wm["scratch"] = scratch
            wm["last_updated"] = datetime.now().isoformat()
            wm_file.write_text(json.dumps(wm, indent=2, default=str), encoding="utf-8")
        except Exception as e:
            logger.debug(f"Failed to store dream suggestions: {e}")

    return f"Dream phase complete: {len(suggestions)} creative suggestions generated."


# ============================================================
# Phase: Prune
# ============================================================

async def _prune(router=None) -> str:
    """Delete low-confidence, unused items and check contradictions."""
    items = _load_memory_items()
    now = datetime.now()
    pruned = 0
    contradictions_found = 0

    for item in items:
        confidence = item.get("confidence", 0.7)
        access_count = item.get("access_count", 0)
        created = item.get("created", "")

        # Age check
        try:
            created_dt = datetime.fromisoformat(created)
            age_days = (now - created_dt).days
        except (ValueError, TypeError):
            age_days = 0

        # Prune: confidence < 0.3 AND 0 accesses AND older than 90 days
        if confidence < 0.3 and access_count == 0 and age_days > 90:
            fpath = config.MEMORY_ITEMS_DIR / f"{item['id']}.json"
            if fpath.exists():
                fpath.unlink()
                pruned += 1
                logger.info(f"Pruned item {item['id']}: conf={confidence}, accesses={access_count}, age={age_days}d")

    # Simple contradiction check: items with overlapping keywords but conflicting content
    remaining_items = _load_memory_items()
    for i, item_a in enumerate(remaining_items):
        for item_b in remaining_items[i + 1:]:
            kw_a = set(item_a.get("keywords", []))
            kw_b = set(item_b.get("keywords", []))
            if len(kw_a & kw_b) >= 3:
                # High keyword overlap — potential contradiction
                cont_a = item_a.get("contradictions", [])
                if item_b["id"] not in cont_a:
                    # Flag for manual review (don't auto-delete)
                    cont_a.append(item_b["id"])
                    item_a["contradictions"] = cont_a
                    fpath = config.MEMORY_ITEMS_DIR / f"{item_a['id']}.json"
                    if fpath.exists():
                        fpath.write_text(json.dumps(item_a, indent=2), encoding="utf-8")
                    contradictions_found += 1

        if contradictions_found >= 10:
            break

    return f"Prune complete: {pruned} items deleted, {contradictions_found} potential contradictions flagged."


# ============================================================
# Phase: Strengthen
# ============================================================

async def _strengthen(router=None) -> str:
    """Boost items whose keywords align with active goals."""
    goals = _load_json_file(config.MEMORY_DIR / "goals.json")
    active_goals = [g for g in goals if g.get("status") == "active"]
    if not active_goals:
        return "No active goals to strengthen memories against."

    # Collect goal keywords
    goal_words = set()
    for g in active_goals:
        title_words = g.get("title", "").lower().split()
        desc_words = g.get("description", "").lower().split()
        goal_words.update(w for w in title_words + desc_words if len(w) > 3)

    items = _load_memory_items()
    strengthened = 0

    for item in items:
        item_keywords = set(k.lower() for k in item.get("keywords", []))
        overlap = item_keywords & goal_words
        if len(overlap) >= 2:
            # Boost importance and confidence
            old_importance = item.get("importance", 5)
            old_confidence = item.get("confidence", 0.7)
            item["importance"] = min(10, old_importance + 1)
            item["confidence"] = min(1.0, round(old_confidence + 0.05, 3))

            fpath = config.MEMORY_ITEMS_DIR / f"{item['id']}.json"
            if fpath.exists():
                fpath.write_text(json.dumps(item, indent=2), encoding="utf-8")
                strengthened += 1

    return f"Strengthen complete: {strengthened} items boosted (aligned with {len(active_goals)} active goals)."


# ============================================================
# Phase: Full Cycle
# ============================================================

async def _full_cycle(router=None) -> str:
    """Run all memory agent phases sequentially."""
    results = []

    # Avatar event-binding (Day 105): memory dreaming = contemplative
    try:
        import avatar as _avatar
        await _avatar.set_state("contemplative")
    except Exception:
        pass

    result = await _cross_pollinate(router)
    results.append(f"Cross-pollinate: {result}")

    result = await _synthesize(router)
    results.append(f"Synthesize: {result}")

    result = await _dream(router)
    results.append(f"Dream: {result}")

    result = await _prune(router)
    results.append(f"Prune: {result}")

    result = await _strengthen(router)
    results.append(f"Strengthen: {result}")

    # Avatar event-binding (Day 105): cycle complete → idle
    try:
        import avatar as _avatar
        await _avatar.set_state("idle")
    except Exception:
        pass

    return "Memory agent full cycle complete:\n" + "\n".join(f"  - {r}" for r in results)


# ============================================================
# Public API for consolidation integration
# ============================================================

async def run_memory_agent_cycle(router=None) -> str:
    """Run a full memory agent cycle. Called by consolidation during quiet hours."""
    return await _full_cycle(router)


# ============================================================
# Tool definition
# ============================================================

TOOL_DEFINITIONS = [
    {
        "name": "memory_agent",
        "description": (
            "Proactive memory management with LLM-powered 'dreaming' phases. "
            "Actions: cross_pollinate (find unexpected connections), synthesize (distill principles), "
            "dream (creative goal+experience suggestions), prune (delete stale items), "
            "strengthen (boost goal-aligned items), full_cycle (run all phases)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["cross_pollinate", "synthesize", "dream", "prune", "strengthen", "full_cycle"],
                    "description": (
                        "cross_pollinate: find connections between different memory categories. "
                        "synthesize: distill experiences into principles. "
                        "dream: generate creative suggestions from goal+experience pairs. "
                        "prune: delete low-confidence unused items. "
                        "strengthen: boost items aligned with active goals. "
                        "full_cycle: run all phases sequentially."
                    ),
                },
            },
            "required": ["action"],
        },
    },
]

# Router reference (set by consolidation or heartbeat)
_router = None


def set_router(router):
    """Set the router for LLM-assisted phases."""
    global _router
    _router = router


async def _memory_agent_tool(input_data: dict) -> str:
    """Handle memory_agent tool calls."""
    action = input_data.get("action", "")
    action_map = {
        "cross_pollinate": _cross_pollinate,
        "synthesize": _synthesize,
        "dream": _dream,
        "prune": _prune,
        "strengthen": _strengthen,
        "full_cycle": _full_cycle,
    }

    handler = action_map.get(action)
    if not handler:
        return f"Unknown memory_agent action: {action}. Valid: {', '.join(action_map.keys())}"

    return await handler(_router)


TOOL_HANDLERS = {
    "memory_agent": _memory_agent_tool,
}
