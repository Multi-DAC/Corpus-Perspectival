"""Memory Categories — Auto-organized topic directories for memory items.

Implements the Category Layer of Clawd's memory system:
- memory_categories: list/view/rebuild/create topic categories

Category structure:
  memory/categories/{name}/
    summary.md      — Aggregated summary of all items in this category
    _items.json     — List of item IDs belonging to this category

Auto-categorization happens when items are extracted via memory_extract.
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import config

logger = logging.getLogger("clawd.tools.memory_categories")

CATEGORIES_DIR = config.MEMORY_CATEGORIES_DIR

TOOL_DEFINITIONS = [
    {
        "name": "memory_categories",
        "description": (
            "Manage memory categories — auto-organized topics that group related memory items. "
            "Actions: 'list' all categories, 'view' a specific category's summary and items, "
            "'rebuild' category summaries, 'create' a new empty category."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "view", "rebuild", "create"],
                    "description": "Action to perform.",
                },
                "category": {
                    "type": "string",
                    "description": "Category name (for action='view', 'rebuild', 'create').",
                },
            },
            "required": ["action"],
        },
    },
]


def _category_dir(name: str) -> Path:
    """Get the directory path for a category."""
    return CATEGORIES_DIR / name.lower().strip()


def _load_category_items(name: str) -> list[str]:
    """Load the item IDs for a category."""
    items_file = _category_dir(name) / "_items.json"
    if items_file.exists():
        try:
            return json.loads(items_file.read_text(encoding="utf-8"))
        except Exception as e:
            logger.debug(f"Failed to parse _items.json for category '{name}': {e}")
    return []


def _save_category_items(name: str, item_ids: list[str]):
    """Save the item IDs for a category."""
    cat_dir = _category_dir(name)
    cat_dir.mkdir(parents=True, exist_ok=True)
    items_file = cat_dir / "_items.json"
    items_file.write_text(json.dumps(item_ids, indent=2), encoding="utf-8")


def _rebuild_summary(name: str) -> str:
    """Rebuild the summary.md for a category from its items."""
    from tools.memory_items import _load_item

    item_ids = _load_category_items(name)
    items = []
    for iid in item_ids:
        item = _load_item(iid)
        if item:
            items.append(item)

    if not items:
        summary = f"# {name}\n\nNo items in this category yet.\n"
    else:
        lines = [f"# {name}", f"", f"*{len(items)} items — last updated {datetime.now().strftime('%Y-%m-%d %H:%M')}*", ""]
        # Group by type
        by_type: dict[str, list[dict]] = {}
        for item in items:
            t = item.get("type", "unknown")
            by_type.setdefault(t, []).append(item)

        for item_type, type_items in sorted(by_type.items()):
            lines.append(f"## {item_type.title()}s")
            for item in sorted(type_items, key=lambda x: x.get("confidence", 0), reverse=True):
                conf = item.get("confidence", "?")
                lines.append(f"- {item['content']} *(conf: {conf}, id: {item['id']})*")
            lines.append("")

        summary = "\n".join(lines)

    cat_dir = _category_dir(name)
    cat_dir.mkdir(parents=True, exist_ok=True)
    summary_file = cat_dir / "summary.md"
    summary_file.write_text(summary, encoding="utf-8")
    return summary


def register_item_in_categories(item_id: str, categories: list[str]):
    """Register an item in its category directories.

    Called automatically by memory_extract after storing an item.
    Creates category directories if needed and updates _items.json + summary.md.
    """
    for cat in categories:
        cat_name = cat.lower().strip()
        if not cat_name:
            continue

        item_ids = _load_category_items(cat_name)
        if item_id not in item_ids:
            item_ids.append(item_id)
            _save_category_items(cat_name, item_ids)

        # Rebuild summary
        try:
            _rebuild_summary(cat_name)
        except Exception as e:
            logger.warning(f"Failed to rebuild summary for category '{cat_name}': {e}")


async def _memory_categories(input_data: dict) -> str:
    """Manage memory categories."""
    action = input_data["action"]

    if action == "list":
        if not CATEGORIES_DIR.is_dir():
            return "No categories exist yet. Extract memory items to auto-create categories."

        categories = []
        for cat_dir in sorted(CATEGORIES_DIR.iterdir()):
            if cat_dir.is_dir():
                item_ids = _load_category_items(cat_dir.name)
                categories.append(f"- **{cat_dir.name}** ({len(item_ids)} items)")

        if not categories:
            return "No categories exist yet."
        return f"{len(categories)} categories:\n" + "\n".join(categories)

    elif action == "view":
        category = input_data.get("category")
        if not category:
            return "View requires a 'category' parameter."

        cat_dir = _category_dir(category)
        if not cat_dir.is_dir():
            return f"Category '{category}' does not exist."

        summary_file = cat_dir / "summary.md"
        if summary_file.exists():
            return summary_file.read_text(encoding="utf-8")
        else:
            # Generate on the fly
            return _rebuild_summary(category)

    elif action == "rebuild":
        category = input_data.get("category")
        if category:
            # Rebuild one category
            cat_dir = _category_dir(category)
            if not cat_dir.is_dir():
                return f"Category '{category}' does not exist."
            summary = _rebuild_summary(category)
            return f"Rebuilt summary for '{category}'.\n\n{summary}"
        else:
            # Rebuild all categories
            if not CATEGORIES_DIR.is_dir():
                return "No categories to rebuild."
            count = 0
            for cat_dir in CATEGORIES_DIR.iterdir():
                if cat_dir.is_dir():
                    _rebuild_summary(cat_dir.name)
                    count += 1
            return f"Rebuilt summaries for {count} categories."

    elif action == "create":
        category = input_data.get("category")
        if not category:
            return "Create requires a 'category' parameter."

        cat_name = category.lower().strip()
        cat_dir = _category_dir(cat_name)
        if cat_dir.is_dir():
            return f"Category '{cat_name}' already exists."

        cat_dir.mkdir(parents=True, exist_ok=True)
        _save_category_items(cat_name, [])
        summary = f"# {cat_name}\n\nNo items in this category yet.\n"
        (cat_dir / "summary.md").write_text(summary, encoding="utf-8")
        return f"Created category '{cat_name}'."

    else:
        return f"Unknown action '{action}'. Valid: list, view, rebuild, create."


TOOL_HANDLERS = {
    "memory_categories": _memory_categories,
}
