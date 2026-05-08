"""Memory Items — Structured fact/preference/skill extraction and retrieval.

Implements the Item Layer of Clawd's memory system:
- memory_extract: Store a structured memory item with type, categories, source, confidence
- memory_items: Search/list/get/update/delete items

Items are stored as individual JSON files in memory/items/{id}.json.
A category index (_index.json) maps category -> [item_ids] for fast lookup.

Features:
- Zettelkasten-style bidirectional linking between items (A-MEM inspired)
- Importance scoring with Ebbinghaus recency decay
- Auto-linking to related items on creation
- Keywords extraction for improved retrieval
"""
import json
import logging
import math
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import config

logger = logging.getLogger("clawd.tools.memory_items")

ITEMS_DIR = config.MEMORY_ITEMS_DIR
INDEX_FILE = ITEMS_DIR / "_index.json"

VALID_TYPES = ["fact", "preference", "skill", "relationship", "decision", "insight", "context"]

# Importance scoring constants
RECENCY_DECAY_BASE = 0.995  # Per-hour decay factor (Ebbinghaus-inspired)
IMPORTANCE_WEIGHT = 0.4
RECENCY_WEIGHT = 0.3
UTILITY_WEIGHT = 0.3

TOOL_DEFINITIONS = [
    {
        "name": "memory_extract",
        "description": (
            "Extract and store a structured memory item — a fact, preference, skill, "
            "relationship, decision, or insight worth remembering across sessions. "
            "Use this when you learn something important about Clayton, yourself, "
            "a project, or the world that should persist."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "The memory content — a concise, self-contained statement of what to remember.",
                },
                "type": {
                    "type": "string",
                    "enum": VALID_TYPES,
                    "description": "Item type: fact, preference, skill, relationship, decision, insight, or context.",
                },
                "categories": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Topic categories for organization (e.g. ['clayton', 'preferences'], ['projects', 'drift']).",
                },
                "source": {
                    "type": "string",
                    "description": "Where this was learned (e.g. 'conversation 2026-02-15', 'telegram chat').",
                },
                "confidence": {
                    "type": "number",
                    "description": "Confidence level 0.0-1.0. Default: 0.8.",
                },
                "related_items": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "IDs of related memory items for cross-referencing.",
                },
                "importance": {
                    "type": "integer",
                    "description": "Importance level 1-10. Higher = more likely to surface in search. Default: 5.",
                },
            },
            "required": ["content", "type", "categories"],
        },
    },
    {
        "name": "memory_items",
        "description": (
            "Search, list, get, update, or delete structured memory items. "
            "Use action='search' to find items by query, 'list' to list by category/type, "
            "'get' to retrieve a specific item, 'update' to modify, 'delete' to remove."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["search", "list", "get", "update", "delete", "feedback", "rebuild_index"],
                    "description": "Action to perform. feedback: mark retrieved items as useful/not useful to adjust utility scores.",
                },
                "query": {
                    "type": "string",
                    "description": "Search query (for action='search').",
                },
                "category": {
                    "type": "string",
                    "description": "Filter by category (for action='list').",
                },
                "type": {
                    "type": "string",
                    "description": "Filter by type (for action='list').",
                },
                "item_id": {
                    "type": "string",
                    "description": "Item ID (for action='get', 'update', 'delete').",
                },
                "updates": {
                    "type": "object",
                    "description": "Fields to update (for action='update'). Can include content, type, categories, confidence, related_items, importance, links, keywords.",
                },
                "useful": {
                    "type": "boolean",
                    "description": "For action='feedback': was the retrieved item useful? True boosts utility, False decreases it.",
                },
            },
            "required": ["action"],
        },
    },
]


def _generate_id() -> str:
    """Generate a short unique ID for items."""
    import hashlib
    raw = f"{time.time()}{os.getpid()}"
    return "itm_" + hashlib.md5(raw.encode()).hexdigest()[:6]


def _extract_keywords(content: str) -> list[str]:
    """Extract simple keywords from content for linking and retrieval."""
    import re
    # Remove common stop words and extract meaningful words
    stop_words = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "to", "of", "in", "for",
        "on", "with", "at", "by", "from", "as", "into", "about", "like",
        "through", "after", "over", "between", "out", "against", "during",
        "without", "before", "under", "around", "among", "this", "that",
        "these", "those", "it", "its", "i", "he", "she", "we", "they",
        "my", "his", "her", "our", "their", "and", "but", "or", "not",
        "no", "so", "if", "then", "than", "when", "what", "which", "who",
        "how", "all", "each", "every", "both", "few", "more", "most",
        "other", "some", "such", "very", "just", "also", "now",
    }
    words = re.findall(r'\b[a-zA-Z]{3,}\b', content.lower())
    keywords = [w for w in words if w not in stop_words]
    # Deduplicate preserving order, keep top 10
    seen = set()
    unique = []
    for w in keywords:
        if w not in seen:
            seen.add(w)
            unique.append(w)
    return unique[:10]


def _compute_recency_score(last_accessed: str) -> float:
    """Compute recency score using Ebbinghaus decay curve."""
    try:
        last_dt = datetime.fromisoformat(last_accessed)
        hours_elapsed = (datetime.now() - last_dt).total_seconds() / 3600
        return RECENCY_DECAY_BASE ** hours_elapsed
    except (ValueError, TypeError):
        return 0.5  # Default for items without access timestamp


def _compute_retrieval_score(item: dict, relevance: float) -> float:
    """Compute final retrieval score combining relevance, importance, recency, and utility."""
    importance = item.get("importance", 5) / 10.0  # Normalize 1-10 to 0-1
    recency = _compute_recency_score(item.get("last_accessed", item.get("created", "")))
    utility = item.get("utility_score", 0.5)

    return relevance * (
        IMPORTANCE_WEIGHT * importance +
        RECENCY_WEIGHT * recency +
        UTILITY_WEIGHT * utility
    )


def _find_related_items(content: str, keywords: list[str], exclude_id: str = None, max_results: int = 3) -> list[str]:
    """Find existing items related to new content for auto-linking."""
    if not ITEMS_DIR.is_dir():
        return []

    content_lower = content.lower()
    scored = []

    for fpath in ITEMS_DIR.glob("*.json"):
        if fpath.name == "_index.json":
            continue
        item_id = fpath.stem
        if item_id == exclude_id:
            continue
        try:
            item = json.loads(fpath.read_text(encoding="utf-8"))
        except Exception:
            continue

        item_content = item.get("content", "").lower()
        item_keywords = item.get("keywords", [])
        item_categories = [c.lower() for c in item.get("categories", [])]

        # Score by keyword overlap
        score = 0.0
        for kw in keywords:
            if kw in item_content:
                score += 1.0
            if kw in item_keywords:
                score += 0.5
        # Category overlap bonus
        for cat in item_categories:
            if cat in content_lower:
                score += 0.3

        if score > 0.5:  # Minimum threshold
            scored.append((item_id, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return [item_id for item_id, _ in scored[:max_results]]


def _add_backlinks(target_id: str, linked_ids: list[str]):
    """Add backlinks from linked items back to the target item."""
    for linked_id in linked_ids:
        item = _load_item(linked_id)
        if item:
            links = item.get("links", [])
            if target_id not in links:
                links.append(target_id)
                item["links"] = links
                _save_item(item)


def _migrate_item_schema(item: dict) -> dict:
    """Ensure item has all current schema fields (backward compatibility)."""
    defaults = {
        "links": [],
        "keywords": [],
        "importance": 5,
        "last_accessed": item.get("created", datetime.now().isoformat()),
        "access_count": 0,
        "utility_score": 0.5,
        # Adaptive forgetting fields (Task 21)
        "retrieval_led_to_success": 0,
        "q_value": 0.5,
        "decay_rate": 0.995,  # Per-hour, adaptive
        "memory_tier": "warm",  # hot/warm/cold
        # Provenance fields
        "source_hash": "",
        "confidence_history": [],
    }
    for key, default in defaults.items():
        if key not in item:
            item[key] = default
    return item


def compute_memory_tier(item: dict) -> str:
    """Compute memory tier based on access patterns.
    Hot: accessed in last 7 days (in-prompt eligible)
    Warm: 7-30 days (searchable only)
    Cold: >30 days with low q_value (archived)
    """
    last_accessed = item.get("last_accessed", item.get("created", ""))
    try:
        last_dt = datetime.fromisoformat(last_accessed)
        days_since = (datetime.now() - last_dt).days
    except (ValueError, TypeError):
        days_since = 30

    q_value = item.get("q_value", 0.5)

    if days_since <= 7:
        return "hot"
    elif days_since <= 30:
        return "warm"
    elif q_value > 0.6:
        return "warm"  # High Q-value items stay warm even if old
    else:
        return "cold"


def update_item_tiers():
    """Update memory tiers for all items. Called during consolidation."""
    if not ITEMS_DIR.is_dir():
        return 0

    updated = 0
    for fpath in ITEMS_DIR.glob("*.json"):
        if fpath.name == "_index.json":
            continue
        try:
            item = json.loads(fpath.read_text(encoding="utf-8"))
        except Exception:
            continue

        item = _migrate_item_schema(item)
        new_tier = compute_memory_tier(item)
        if item.get("memory_tier") != new_tier:
            item["memory_tier"] = new_tier
            # Items with high q_value get slower decay
            q = item.get("q_value", 0.5)
            if q > 0.7:
                item["decay_rate"] = 0.998  # Slower decay
            elif q < 0.3:
                item["decay_rate"] = 0.990  # Faster decay
            else:
                item["decay_rate"] = 0.995  # Default

            fpath.write_text(json.dumps(item, indent=2), encoding="utf-8")
            updated += 1

    return updated


def _load_index() -> dict[str, list[str]]:
    """Load the category index. Returns {category: [item_ids]}."""
    if INDEX_FILE.exists():
        try:
            return json.loads(INDEX_FILE.read_text(encoding="utf-8"))
        except Exception as e:
            logger.debug(f"Failed to parse _index.json: {e}")
    return {}


def _save_index(index: dict[str, list[str]]):
    """Save the category index."""
    ITEMS_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_FILE.write_text(json.dumps(index, indent=2), encoding="utf-8")


def _load_item(item_id: str) -> dict | None:
    """Load a single item by ID."""
    filepath = ITEMS_DIR / f"{item_id}.json"
    if filepath.exists():
        try:
            return json.loads(filepath.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def _save_item(item: dict):
    """Save an item to disk (JSON) and async-save to SQLite via backend."""
    ITEMS_DIR.mkdir(parents=True, exist_ok=True)
    filepath = ITEMS_DIR / f"{item['id']}.json"
    filepath.write_text(json.dumps(item, indent=2), encoding="utf-8")

    # Also persist to SQLite (fire-and-forget via backend)
    try:
        import asyncio
        from tools.memory_backend import get_backend
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(get_backend().save_item(item))
        else:
            loop.run_until_complete(get_backend().save_item(item))
    except Exception as e:
        logger.debug(f"SQLite fire-and-forget save failed for item {item.get('id')}: {e}")


def _update_index_for_item(item_id: str, categories: list[str]):
    """Add an item to the category index."""
    index = _load_index()
    for cat in categories:
        cat_lower = cat.lower().strip()
        if cat_lower not in index:
            index[cat_lower] = []
        if item_id not in index[cat_lower]:
            index[cat_lower].append(item_id)
    _save_index(index)


def _remove_from_index(item_id: str):
    """Remove an item from all categories in the index."""
    index = _load_index()
    changed = False
    for cat in list(index.keys()):
        if item_id in index[cat]:
            index[cat].remove(item_id)
            changed = True
        if not index[cat]:
            del index[cat]
            changed = True
    if changed:
        _save_index(index)


def search_items_raw(query: str, max_results: int = 15) -> list[tuple[str, str, float]]:
    """Search items by keyword matching with importance/recency scoring.

    Returns [(filepath, content_text, score)].
    Exported for use by memory_tools._hybrid_search() as a third RRF source.
    """
    if not ITEMS_DIR.is_dir():
        return []

    query_lower = query.lower()
    keywords = query_lower.split()
    results = []

    for fpath in ITEMS_DIR.glob("*.json"):
        if fpath.name == "_index.json":
            continue
        try:
            item = json.loads(fpath.read_text(encoding="utf-8"))
        except Exception:
            continue

        content = item.get("content", "")
        item_type = item.get("type", "")
        categories = " ".join(item.get("categories", []))
        item_keywords = " ".join(item.get("keywords", []))
        searchable = f"{content} {item_type} {categories} {item_keywords}".lower()

        relevance = 0.0
        for kw in keywords:
            if kw in searchable:
                relevance += 1.0
                # Bonus for content match vs category-only match
                if kw in content.lower():
                    relevance += 0.5
                # Bonus for keyword match
                if kw in item_keywords:
                    relevance += 0.3

        if relevance > 0:
            # Apply importance/recency/utility scoring
            final_score = _compute_retrieval_score(item, relevance)

            # Format as readable text
            links = item.get("links", [])
            link_info = f"; links: {len(links)}" if links else ""
            importance = item.get("importance", 5)
            display = (
                f"[{item.get('type', '?')}] {content} "
                f"(categories: {', '.join(item.get('categories', []))}; "
                f"confidence: {item.get('confidence', '?')}; "
                f"importance: {importance}{link_info})"
            )
            results.append((str(fpath), display, final_score))

    results.sort(key=lambda x: x[2], reverse=True)
    return results[:max_results]


async def _memory_extract(input_data: dict) -> str:
    """Extract and store a structured memory item with auto-linking and importance scoring."""
    content = input_data["content"]
    item_type = input_data["type"]
    categories = input_data["categories"]
    source = input_data.get("source", f"conversation {datetime.now().strftime('%Y-%m-%d')}")
    confidence = input_data.get("confidence", 0.8)
    related = input_data.get("related_items", [])
    importance = int(input_data.get("importance", 5))  # 1-10 scale

    if item_type not in VALID_TYPES:
        return f"Invalid type '{item_type}'. Valid types: {', '.join(VALID_TYPES)}"

    item_id = _generate_id()
    keywords = _extract_keywords(content)

    # Auto-link to related existing items
    auto_links = _find_related_items(content, keywords, exclude_id=item_id)
    all_links = list(set(related + auto_links))

    now_iso = datetime.now().isoformat()

    # Provenance: compute source hash and init confidence history
    import hashlib
    source_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    confidence_val = max(0.0, min(1.0, confidence))
    confidence_history = [{"timestamp": now_iso, "confidence": confidence_val, "reason": "initial"}]

    item = {
        "id": item_id,
        "type": item_type,
        "content": content,
        "source": source,
        "categories": [c.lower().strip() for c in categories],
        "related_items": [r for r in related if r],  # Keep explicit relations separate
        "links": all_links,  # Zettelkasten bidirectional links
        "keywords": keywords,
        "importance": max(1, min(10, importance)),
        "created": now_iso,
        "last_accessed": now_iso,
        "access_count": 0,
        "utility_score": 0.5,
        "confidence": confidence_val,
        "source_hash": source_hash,
        "confidence_history": confidence_history,
    }

    _save_item(item)
    _update_index_for_item(item_id, item["categories"])

    # Add backlinks from linked items to this new item
    if all_links:
        _add_backlinks(item_id, all_links)

    # Auto-categorize via memory_categories if available
    try:
        from tools.memory_categories import register_item_in_categories
        register_item_in_categories(item_id, item["categories"])
    except ImportError as e:
        logger.debug(f"Optional import: {e}")
    except Exception as e:
        logger.warning(f"Auto-categorization failed for {item_id}: {e}")

    # Trigger re-index if embedding index is available
    try:
        from tools import _embedding_index
        if _embedding_index is not None:
            filepath = ITEMS_DIR / f"{item_id}.json"
            _embedding_index.index_file(filepath)
    except Exception as e:
        logger.warning(f"Embedding re-index failed for item {item_id}: {e}")

    link_info = f", linked to {len(all_links)} items" if all_links else ""
    logger.info(f"Extracted memory item {item_id}: [{item_type}] {content[:80]}{link_info}")
    return json.dumps({
        "status": "stored",
        "id": item_id,
        "type": item_type,
        "categories": item["categories"],
        "keywords": keywords,
        "links": all_links,
        "importance": item["importance"],
        "content_preview": content[:100],
    })


async def _memory_items(input_data: dict) -> str:
    """Search, list, get, update, or delete memory items."""
    action = input_data["action"]

    if action == "search":
        query = input_data.get("query", "")
        if not query:
            return "Search requires a 'query' parameter."
        results = search_items_raw(query, max_results=10)
        if not results:
            return f"No memory items found for: {query}"
        output = []
        for filepath, display, score in results:
            item_id = Path(filepath).stem
            output.append(f"- **{item_id}** (score: {score:.1f}): {display}")
            # Boost-on-retrieval (Ebbinghaus reinforcement, Day 96 evening Phase 4 #58):
            # surfacing an item in search results updates its access tracking,
            # which slows decay (per compute_memory_tier + adaptive decay_rate).
            # Frequently-retrieved items stay hot/warm; ignored items drift cold.
            try:
                item = _load_item(item_id)
                if item:
                    item["access_count"] = item.get("access_count", 0) + 1
                    item["last_accessed"] = datetime.now().isoformat()
                    _save_item(item)
            except Exception:
                pass  # Never break search on access-bookkeeping failure
        return f"Found {len(results)} items:\n" + "\n".join(output)

    elif action == "list":
        category = input_data.get("category")
        type_filter = input_data.get("type")

        if category:
            index = _load_index()
            item_ids = index.get(category.lower().strip(), [])
            if not item_ids:
                return f"No items in category '{category}'."
        else:
            # List all items
            if not ITEMS_DIR.is_dir():
                return "No memory items stored yet."
            item_ids = [
                f.stem for f in ITEMS_DIR.glob("*.json")
                if f.name != "_index.json"
            ]

        items = []
        for iid in item_ids:
            item = _load_item(iid)
            if item:
                if type_filter and item.get("type") != type_filter:
                    continue
                items.append(item)

        if not items:
            return "No matching items found."

        output = []
        for item in sorted(items, key=lambda x: x.get("created", ""), reverse=True):
            output.append(
                f"- **{item['id']}** [{item['type']}] {item['content'][:80]} "
                f"(categories: {', '.join(item.get('categories', []))})"
            )
        return f"{len(items)} items:\n" + "\n".join(output)

    elif action == "get":
        item_id = input_data.get("item_id")
        if not item_id:
            return "Get requires an 'item_id' parameter."
        item = _load_item(item_id)
        if not item:
            return f"Item '{item_id}' not found."
        # Migrate schema if needed
        item = _migrate_item_schema(item)
        # Update access tracking
        item["access_count"] = item.get("access_count", 0) + 1
        item["last_accessed"] = datetime.now().isoformat()
        _save_item(item)

        # 1-hop linked neighbor traversal
        result = {"item": item}
        linked_ids = item.get("links", [])
        if linked_ids:
            neighbors = []
            for lid in linked_ids[:5]:  # Cap at 5 neighbors
                neighbor = _load_item(lid)
                if neighbor:
                    neighbors.append({
                        "id": neighbor["id"],
                        "type": neighbor.get("type", "?"),
                        "content": neighbor.get("content", "")[:200],
                        "categories": neighbor.get("categories", []),
                    })
            if neighbors:
                result["linked_neighbors"] = neighbors

        return json.dumps(result, indent=2)

    elif action == "update":
        item_id = input_data.get("item_id")
        updates = input_data.get("updates", {})
        if not item_id:
            return "Update requires an 'item_id' parameter."
        item = _load_item(item_id)
        if not item:
            return f"Item '{item_id}' not found."

        item = _migrate_item_schema(item)
        old_categories = set(item.get("categories", []))
        allowed_update_keys = (
            "content", "type", "confidence", "related_items", "categories",
            "importance", "links", "keywords", "utility_score",
        )
        for key, value in updates.items():
            if key in allowed_update_keys:
                item[key] = value
        item["modified"] = datetime.now().isoformat()
        _save_item(item)

        # Update index if categories changed
        new_categories = set(item.get("categories", []))
        if new_categories != old_categories:
            _remove_from_index(item_id)
            _update_index_for_item(item_id, list(new_categories))

        return f"Updated item {item_id}."

    elif action == "delete":
        item_id = input_data.get("item_id")
        if not item_id:
            return "Delete requires an 'item_id' parameter."
        filepath = ITEMS_DIR / f"{item_id}.json"
        if not filepath.exists():
            return f"Item '{item_id}' not found."
        filepath.unlink()
        _remove_from_index(item_id)
        return f"Deleted item {item_id}."

    elif action == "feedback":
        item_id = input_data.get("item_id")
        useful = input_data.get("useful", True)
        if not item_id:
            return "Feedback requires an 'item_id' parameter."
        item = _load_item(item_id)
        if not item:
            return f"Item '{item_id}' not found."
        item = _migrate_item_schema(item)
        # Adjust utility score: increase for useful, decrease for not useful
        current_utility = item.get("utility_score", 0.5)
        if useful:
            item["utility_score"] = min(1.0, current_utility + 0.1)
            # Track retrieval-led-to-success for Q-value
            item["retrieval_led_to_success"] = item.get("retrieval_led_to_success", 0) + 1
        else:
            item["utility_score"] = max(0.0, current_utility - 0.1)

        # Recalculate Q-value
        retrievals = max(item.get("access_count", 1), 1)
        item["q_value"] = round(item.get("retrieval_led_to_success", 0) / retrievals, 3)

        # Append to confidence_history on utility change
        conf_history = item.get("confidence_history", [])
        if not isinstance(conf_history, list):
            conf_history = []
        conf_history.append({
            "timestamp": datetime.now().isoformat(),
            "confidence": item.get("confidence", 0.8),
            "reason": f"feedback_{'useful' if useful else 'not_useful'}, q={item['q_value']:.3f}"
        })
        item["confidence_history"] = conf_history[-20:]  # Keep last 20 entries

        # Update tier and decay rate based on Q-value
        item["memory_tier"] = compute_memory_tier(item)
        if item["q_value"] > 0.7:
            item["decay_rate"] = 0.998
        elif item["q_value"] < 0.3:
            item["decay_rate"] = 0.990

        _save_item(item)
        return f"Feedback recorded for {item_id}: utility {'↑' if useful else '↓'} → {item['utility_score']:.2f}, q_value={item['q_value']:.3f}, tier={item['memory_tier']}"

    elif action == "rebuild_index":
        # A29: Rebuild index from directory scan to fix index/directory divergence
        return _rebuild_index()

    else:
        return f"Unknown action '{action}'. Valid: search, list, get, update, delete, feedback, rebuild_index."


def _rebuild_index() -> str:
    """A29: Rebuild the category index by scanning the items directory.
    Fixes divergence between _index.json and actual item files."""
    if not ITEMS_DIR.is_dir():
        return "No items directory found."

    new_index = {}
    rebuilt_count = 0
    orphan_count = 0

    for item_file in ITEMS_DIR.glob("*.json"):
        if item_file.name.startswith("_"):
            continue  # Skip index files
        try:
            item = json.loads(item_file.read_text(encoding="utf-8"))
            item_id = item.get("id", item_file.stem)
            categories = item.get("categories", [])
            for cat in categories:
                if cat not in new_index:
                    new_index[cat] = []
                if item_id not in new_index[cat]:
                    new_index[cat].append(item_id)
            rebuilt_count += 1
        except Exception as e:
            logger.warning(f"Skipping corrupted item file {item_file.name}: {e}")
            orphan_count += 1

    # Save rebuilt index
    INDEX_FILE.write_text(json.dumps(new_index, indent=2), encoding="utf-8")

    return (
        f"Index rebuilt: {rebuilt_count} items indexed across {len(new_index)} categories. "
        f"{orphan_count} corrupted files skipped."
    )


TOOL_HANDLERS = {
    "memory_extract": _memory_extract,
    "memory_items": _memory_items,
}
