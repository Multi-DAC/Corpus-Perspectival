"""Semantic Segmentation — HiMem-style automatic episode clustering.

Uses LLM-assisted extraction to identify notable facts/decisions/insights
from daily logs (replaces regex-only extraction when router is available).
Clusters recent episodes into semantic "notes" linked bidirectionally in KG.
"""
import json
import logging
import re
import uuid
from datetime import datetime
from typing import Optional

import config

logger = logging.getLogger("clawd.tools.semantic_segmentation")


async def segment_daily_log(date_str: str, content: str, router) -> list[dict]:
    """Use LLM sub-agent to extract ALL notable facts/decisions/insights from a daily log.

    Falls back to regex extraction if router is unavailable.

    Args:
        date_str: The date of the log (YYYY-MM-DD)
        content: Raw text content of the daily log
        router: ModelRouter instance for LLM-assisted extraction

    Returns:
        List of dicts with keys: type, content, categories, importance
    """
    if not content or len(content) < 100:
        return []

    if router is None:
        return _regex_fallback(content, date_str)

    try:
        from tools.system import consult_model
    except ImportError:
        return _regex_fallback(content, date_str)

    prompt = f"""Analyze this daily log from {date_str} and extract ALL notable items.

For each item, classify as one of: fact, decision, insight, skill, relationship
Rate importance 1-10 (10 = life-changing, 1 = trivial).

Return ONLY a JSON array. Each element:
{{"type": "fact|decision|insight|skill|relationship", "content": "the extracted fact", "importance": 5, "categories": ["topic1", "topic2"]}}

Extract 3-15 items. Focus on:
- Concrete facts learned or confirmed
- Decisions made and their reasoning
- Insights or realizations
- New skills or techniques demonstrated
- Relationship dynamics or preferences

Daily log:
---
{content[:3000]}
---

Return ONLY the JSON array, no other text."""

    try:
        result = await consult_model(
            prompt=prompt,
            model="gemini",
            tools=[],
            max_tool_rounds=0,
        )

        # Parse JSON from response
        text = result.get("response", "") if isinstance(result, dict) else str(result)

        # Extract JSON array from response
        json_match = re.search(r'\[.*\]', text, re.DOTALL)
        if json_match:
            items = json.loads(json_match.group())
            # Validate and normalize
            valid_items = []
            for item in items:
                if isinstance(item, dict) and "content" in item:
                    valid_items.append({
                        "type": item.get("type", "fact"),
                        "content": str(item["content"])[:200],
                        "categories": item.get("categories", ["auto-extracted"]),
                        "importance": min(10, max(1, int(item.get("importance", 5)))),
                    })
            logger.info(f"LLM segmentation extracted {len(valid_items)} items from {date_str}")
            return valid_items[:15]
    except Exception as e:
        logger.warning(f"LLM segmentation failed for {date_str}: {e}")

    return _regex_fallback(content, date_str)


def _regex_fallback(content: str, date_str: str) -> list[dict]:
    """Fallback regex extraction (same as original _extract_facts_from_text)."""
    from tools.consolidation import _extract_facts_from_text
    return _extract_facts_from_text(content, date_str)


async def cluster_episodes_into_notes(episodes: list[dict], router) -> list[dict]:
    """Topic-cluster recent episodes into 2-5 semantic "notes" that summarize patterns.

    Each note captures a theme across multiple episodes and is linked
    bidirectionally in the knowledge graph.

    Args:
        episodes: List of episode dicts (from experiences)
        router: ModelRouter for LLM-assisted clustering

    Returns:
        List of semantic note dicts ready for sqlite_store.upsert_semantic_note()
    """
    if not episodes or len(episodes) < 3:
        return []

    if router is None:
        return _rule_based_clustering(episodes)

    try:
        from tools.system import consult_model
    except ImportError:
        return _rule_based_clustering(episodes)

    # Format episodes for the prompt
    episode_summaries = []
    for i, ep in enumerate(episodes[:30]):
        episode_summaries.append(
            f"{i+1}. [{ep.get('category', '?')}] {ep.get('task', '?')} → "
            f"{ep.get('outcome', '?')} (lesson: {ep.get('lesson', 'none')[:80]})"
        )

    prompt = f"""Analyze these {len(episode_summaries)} recent experiences and identify 2-5 thematic patterns.

For each theme, create a semantic note that captures:
1. The topic/theme name
2. A summary of the pattern across episodes
3. An actionable insight derived from the pattern

Return ONLY a JSON array:
[{{"topic": "theme name", "summary": "pattern description", "insight": "actionable insight", "episode_indices": [1, 3, 7]}}]

Experiences:
{chr(10).join(episode_summaries)}

Return ONLY the JSON array."""

    try:
        result = await consult_model(
            prompt=prompt,
            model="gemini",
            tools=[],
            max_tool_rounds=0,
        )

        text = result.get("response", "") if isinstance(result, dict) else str(result)
        json_match = re.search(r'\[.*\]', text, re.DOTALL)

        if json_match:
            clusters = json.loads(json_match.group())
            notes = []
            now = datetime.now().isoformat()

            for cluster in clusters[:5]:
                if not isinstance(cluster, dict):
                    continue
                indices = cluster.get("episode_indices", [])
                source_ids = []
                for idx in indices:
                    if isinstance(idx, int) and 0 < idx <= len(episodes):
                        ep_id = episodes[idx - 1].get("id")
                        if ep_id:
                            source_ids.append(ep_id)

                note = {
                    "id": f"note-{uuid.uuid4().hex[:8]}",
                    "topic": str(cluster.get("topic", ""))[:100],
                    "summary": str(cluster.get("summary", ""))[:500],
                    "insight": str(cluster.get("insight", ""))[:300],
                    "source_episode_ids": source_ids,
                    "source_item_ids": [],
                    "importance": 6,
                    "created": now,
                }
                notes.append(note)

            logger.info(f"LLM clustering produced {len(notes)} semantic notes")
            return notes
    except Exception as e:
        logger.warning(f"LLM clustering failed: {e}")

    return _rule_based_clustering(episodes)


def _rule_based_clustering(episodes: list[dict]) -> list[dict]:
    """Fallback: cluster by category."""
    category_groups = {}
    for ep in episodes:
        cat = ep.get("category", "general")
        category_groups.setdefault(cat, []).append(ep)

    notes = []
    now = datetime.now().isoformat()

    for cat, eps in sorted(category_groups.items(), key=lambda x: len(x[1]), reverse=True):
        if len(eps) < 2:
            continue

        successes = sum(1 for e in eps if e.get("outcome") == "success")
        lessons = [e.get("lesson", "") for e in eps if e.get("lesson")]

        note = {
            "id": f"note-{uuid.uuid4().hex[:8]}",
            "topic": f"{cat} pattern",
            "summary": f"{len(eps)} episodes in '{cat}' category. Success rate: {successes}/{len(eps)}.",
            "insight": lessons[0][:200] if lessons else "No dominant lesson identified.",
            "source_episode_ids": [e.get("id") for e in eps[:10] if e.get("id")],
            "source_item_ids": [],
            "importance": 5,
            "created": now,
        }
        notes.append(note)

        if len(notes) >= 5:
            break

    return notes
