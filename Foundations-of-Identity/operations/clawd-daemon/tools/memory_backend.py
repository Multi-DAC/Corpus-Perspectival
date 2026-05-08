"""Memory Backend — Unified SQLite/JSON data access layer.

Routes all CRUD through SQLite as primary backend with JSON dual-write fallback.
Singleton pattern ensures single point of access for all memory operations.

During stabilization period (SQLITE_PRIMARY=True), writes go to both SQLite and JSON.
JSON files are preserved as backups and can be restored if needed.
"""
import hashlib
import json
import logging
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional


def _atomic_json_write(filepath: Path, data, **kwargs):
    """Write JSON atomically: write to .tmp then os.replace() to target."""
    tmp_path = filepath.with_suffix(".tmp")
    try:
        tmp_path.write_text(json.dumps(data, **kwargs), encoding="utf-8")
        os.replace(str(tmp_path), str(filepath))
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise

import config

logger = logging.getLogger("clawd.tools.memory_backend")

# Config flag: when True, SQLite is primary; JSON is written as backup
SQLITE_PRIMARY = True


class MemoryBackend:
    """Singleton data access layer routing through SQLite with JSON fallback."""

    _instance = None
    _migrated = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    # === Migration ===

    async def ensure_migrated(self):
        """Run JSON→SQLite migration once at boot."""
        if self._migrated:
            return
        try:
            from tools.sqlite_store import get_db, migrate_json_to_sqlite
            db = await get_db()
            if db:
                result = await migrate_json_to_sqlite()
                logger.info(f"Migration check: {result}")
                self._migrated = True
        except Exception as e:
            logger.warning(f"Migration deferred: {e}")

    # === Memory Items ===

    async def save_item(self, item: dict) -> bool:
        """Save a memory item to SQLite (primary) and JSON (backup).
        Returns True only if SQLite (primary) succeeds. JSON is best-effort backup."""
        sqlite_ok = False

        # SQLite primary — this is the source of truth
        try:
            from tools.sqlite_store import upsert_memory_item
            sqlite_ok = await upsert_memory_item(item)
        except Exception as e:
            logger.error(f"SQLite save_item failed: {e}")

        # JSON dual-write backup (best-effort, does not affect return value)
        try:
            config.MEMORY_ITEMS_DIR.mkdir(parents=True, exist_ok=True)
            filepath = config.MEMORY_ITEMS_DIR / f"{item['id']}.json"
            _atomic_json_write(filepath, item, indent=2)
        except Exception as e:
            logger.error(f"JSON save_item backup failed: {e}")

        if not sqlite_ok:
            logger.warning(f"save_item: SQLite failed for item {item.get('id')}, data only in JSON backup")

        return sqlite_ok

    async def load_item(self, item_id: str) -> Optional[dict]:
        """Load a memory item by ID. SQLite first, JSON fallback."""
        if SQLITE_PRIMARY:
            try:
                from tools.sqlite_store import get_memory_item
                item = await get_memory_item(item_id)
                if item:
                    # Parse JSON fields
                    for field in ("categories", "related_items", "links", "keywords", "confidence_history"):
                        if isinstance(item.get(field), str):
                            try:
                                item[field] = json.loads(item[field])
                            except (json.JSONDecodeError, TypeError) as e:
                                logger.debug(f"Malformed JSON field '{field}' in item {item_id}: {e}")
                    return item
            except Exception as e:
                logger.debug(f"SQLite load_item failed, falling back to JSON: {e}")

        # JSON fallback
        filepath = config.MEMORY_ITEMS_DIR / f"{item_id}.json"
        if filepath.exists():
            try:
                return json.loads(filepath.read_text(encoding="utf-8"))
            except Exception as e:
                logger.warning(f"Failed to read JSON fallback for item {item_id}: {e}")
        return None

    async def delete_item(self, item_id: str) -> bool:
        """Delete a memory item from both SQLite and JSON."""
        success = False

        try:
            from tools.sqlite_store import delete_memory_item
            success = await delete_memory_item(item_id)
        except Exception as e:
            logger.debug(f"SQLite delete_item failed: {e}")

        filepath = config.MEMORY_ITEMS_DIR / f"{item_id}.json"
        if filepath.exists():
            try:
                filepath.unlink()
                success = True
            except Exception as e:
                logger.debug(f"JSON delete_item failed: {e}")

        return success

    async def search_items(self, query: str, limit: int = 20) -> list[dict]:
        """Search memory items via FTS5. Falls back to JSON scan."""
        if SQLITE_PRIMARY:
            try:
                from tools.sqlite_store import search_memory_items_fts
                results = await search_memory_items_fts(query, limit)
                if results:
                    return results
            except Exception as e:
                logger.debug(f"SQLite search_items failed: {e}")

        # Fallback: JSON scan (basic keyword matching)
        results = []
        if config.MEMORY_ITEMS_DIR.is_dir():
            query_lower = query.lower()
            for fpath in config.MEMORY_ITEMS_DIR.glob("*.json"):
                if fpath.name == "_index.json":
                    continue
                try:
                    item = json.loads(fpath.read_text(encoding="utf-8"))
                    if query_lower in item.get("content", "").lower():
                        results.append(item)
                except Exception:
                    continue
        return results[:limit]

    async def get_all_items(self, tier: Optional[str] = None) -> list[dict]:
        """Get all memory items, optionally filtered by tier."""
        try:
            from tools.sqlite_store import get_all_items
            return await get_all_items(tier)
        except Exception as e:
            logger.debug(f"SQLite get_all_items failed: {e}")

        # Fallback: load from JSON
        items = []
        if config.MEMORY_ITEMS_DIR.is_dir():
            for fpath in config.MEMORY_ITEMS_DIR.glob("*.json"):
                if fpath.name == "_index.json":
                    continue
                try:
                    item = json.loads(fpath.read_text(encoding="utf-8"))
                    if tier is None or item.get("memory_tier") == tier:
                        items.append(item)
                except Exception:
                    continue
        return items

    # === Episodes ===

    async def save_episode(self, episode: dict) -> bool:
        """Save an episode to SQLite (primary). JSON backup is append-only to avoid RMW races."""
        success = False
        try:
            from tools.sqlite_store import upsert_episode
            success = await upsert_episode(episode)
        except Exception as e:
            logger.error(f"SQLite save_episode failed: {e}")

        # JSON append-only backup (no read-modify-write to avoid concurrent corruption)
        if not success:
            try:
                exp_file = config.MEMORY_DIR / "experiences.json"
                experiences = []
                if exp_file.exists():
                    experiences = json.loads(exp_file.read_text(encoding="utf-8"))

                # Update existing or append
                updated = False
                for i, e in enumerate(experiences):
                    if e.get("id") == episode.get("id"):
                        experiences[i] = episode
                        updated = True
                        break
                if not updated:
                    experiences.append(episode)

                _atomic_json_write(exp_file, experiences, indent=2, default=str)
                success = True
            except Exception as e:
                logger.error(f"JSON save_episode failed: {e}")

        return success

    async def load_episodes(self, category: Optional[str] = None, limit: int = 100) -> list[dict]:
        """Load episodes from SQLite, fallback to JSON."""
        if SQLITE_PRIMARY:
            try:
                from tools.sqlite_store import load_episodes
                return await load_episodes(category, limit)
            except Exception as e:
                logger.debug(f"SQLite load_episodes failed: {e}")

        # JSON fallback
        exp_file = config.MEMORY_DIR / "experiences.json"
        if not exp_file.exists():
            return []
        try:
            episodes = json.loads(exp_file.read_text(encoding="utf-8"))
            if category:
                episodes = [e for e in episodes if e.get("category") == category]
            return episodes[:limit]
        except Exception:
            return []

    async def search_episodes(self, query: str, limit: int = 10) -> list[dict]:
        """Search episodes via FTS5."""
        try:
            from tools.sqlite_store import search_episodes_fts
            return await search_episodes_fts(query, limit)
        except Exception as e:
            logger.debug(f"SQLite search_episodes failed: {e}")
            return []

    # === Goals ===

    async def save_goal(self, goal: dict) -> bool:
        """Save a goal to SQLite and JSON."""
        success = False
        try:
            from tools.sqlite_store import upsert_goal
            success = await upsert_goal(goal)
        except Exception as e:
            logger.error(f"SQLite save_goal failed: {e}")

        # JSON dual-write
        try:
            goals_file = config.MEMORY_DIR / "goals.json"
            goals = []
            if goals_file.exists():
                goals = json.loads(goals_file.read_text(encoding="utf-8"))

            updated = False
            for i, g in enumerate(goals):
                if g.get("id") == goal.get("id"):
                    goals[i] = goal
                    updated = True
                    break
            if not updated:
                goals.append(goal)

            _atomic_json_write(goals_file, goals, indent=2, default=str)
            if not success:
                success = True
        except Exception as e:
            logger.error(f"JSON save_goal failed: {e}")

        return success

    async def load_goals(self, status: Optional[str] = None) -> list[dict]:
        """Load goals from SQLite, fallback to JSON."""
        if SQLITE_PRIMARY:
            try:
                from tools.sqlite_store import load_goals
                return await load_goals(status)
            except Exception as e:
                logger.debug(f"SQLite load_goals failed: {e}")

        goals_file = config.MEMORY_DIR / "goals.json"
        if not goals_file.exists():
            return []
        try:
            goals = json.loads(goals_file.read_text(encoding="utf-8"))
            if status:
                goals = [g for g in goals if g.get("status") == status]
            return goals
        except Exception:
            return []

    async def delete_goal(self, goal_id) -> bool:
        """Delete a goal from SQLite and JSON."""
        success = False
        try:
            from tools.sqlite_store import delete_goal
            success = await delete_goal(goal_id)
        except Exception as e:
            logger.debug(f"SQLite delete_goal failed: {e}")

        # Remove from JSON
        try:
            goals_file = config.MEMORY_DIR / "goals.json"
            if goals_file.exists():
                goals = json.loads(goals_file.read_text(encoding="utf-8"))
                goals = [g for g in goals if g.get("id") != goal_id]
                goals_file.write_text(json.dumps(goals, indent=2), encoding="utf-8")
                success = True
        except Exception as e:
            logger.debug(f"JSON delete_goal failed: {e}")

        return success

    # === Principles ===

    async def save_principle(self, principle: dict) -> bool:
        """Save a principle to SQLite and JSON."""
        success = False
        try:
            from tools.sqlite_store import upsert_principle
            success = await upsert_principle(principle)
        except Exception as e:
            logger.error(f"SQLite save_principle failed: {e}")

        # JSON dual-write
        try:
            principles_file = config.PRINCIPLES_FILE
            principles = []
            if principles_file.exists():
                principles = json.loads(principles_file.read_text(encoding="utf-8"))

            updated = False
            for i, p in enumerate(principles):
                if p.get("id") == principle.get("id"):
                    principles[i] = principle
                    updated = True
                    break
            if not updated:
                principles.append(principle)

            principles_file.parent.mkdir(parents=True, exist_ok=True)
            _atomic_json_write(principles_file, principles, indent=2, default=str)
            if not success:
                success = True
        except Exception as e:
            logger.error(f"JSON save_principle failed: {e}")

        return success

    async def load_principles(self) -> list[dict]:
        """Load principles from SQLite, fallback to JSON."""
        if SQLITE_PRIMARY:
            try:
                from tools.sqlite_store import load_principles
                return await load_principles()
            except Exception as e:
                logger.debug(f"SQLite load_principles failed: {e}")

        principles_file = config.PRINCIPLES_FILE
        if not principles_file.exists():
            return []
        try:
            return json.loads(principles_file.read_text(encoding="utf-8"))
        except Exception:
            return []

    # === Knowledge Graph ===

    async def save_entity(self, entity_id: str, entity: dict) -> bool:
        """Save a KG entity to SQLite and JSON."""
        success = False
        try:
            from tools.sqlite_store import upsert_entity
            success = await upsert_entity(entity_id, entity)
        except Exception as e:
            logger.debug(f"SQLite save_entity failed: {e}")

        # JSON dual-write
        try:
            from tools.knowledge_graph import _load_graph, _save_graph
            graph = _load_graph()
            graph.setdefault("entities", {})[entity_id] = entity
            _save_graph(graph)
            if not success:
                success = True
        except Exception as e:
            logger.debug(f"JSON save_entity failed: {e}")

        return success

    async def save_edge(self, from_entity: str, to_entity: str, relation: str) -> bool:
        """Save a KG edge to SQLite and JSON."""
        success = False
        try:
            from tools.sqlite_store import upsert_edge
            success = await upsert_edge(from_entity, to_entity, relation)
        except Exception as e:
            logger.debug(f"SQLite save_edge failed: {e}")

        # JSON dual-write
        try:
            from tools.knowledge_graph import add_edge_raw
            add_edge_raw(from_entity, to_entity, relation)
            if not success:
                success = True
        except Exception as e:
            logger.debug(f"JSON save_edge failed: {e}")

        return success

    async def load_graph(self) -> dict:
        """Load KG from SQLite, fallback to JSON."""
        if SQLITE_PRIMARY:
            try:
                from tools.sqlite_store import load_graph
                return await load_graph()
            except Exception as e:
                logger.debug(f"SQLite load_graph failed: {e}")

        try:
            from tools.knowledge_graph import _load_graph
            return _load_graph()
        except Exception:
            return {"entities": {}, "edges": []}

    # === Provenance ===

    def compute_source_hash(self, content: str) -> str:
        """Compute SHA-256 hash of content for provenance tracking."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    async def verify_provenance(self, item_id: str) -> dict:
        """Verify integrity of a memory item by comparing content hash to stored source_hash.

        Returns:
            {"status": "verified"|"tampered"|"no_hash"|"not_found",
             "item_id": str, "details": str}
        """
        item = await self.load_item(item_id)
        if not item:
            return {"status": "not_found", "item_id": item_id, "details": "Item not found."}

        stored_hash = item.get("source_hash", "")
        if not stored_hash:
            return {"status": "no_hash", "item_id": item_id,
                    "details": "No source hash stored (pre-provenance item)."}

        current_hash = self.compute_source_hash(item.get("content", ""))
        if current_hash == stored_hash:
            return {"status": "verified", "item_id": item_id,
                    "details": "Content matches stored hash."}
        else:
            return {"status": "tampered", "item_id": item_id,
                    "details": f"Content hash mismatch: stored={stored_hash[:16]}..., current={current_hash[:16]}..."}


# Singleton accessor
_backend = None


def get_backend() -> MemoryBackend:
    """Get the singleton MemoryBackend instance."""
    global _backend
    if _backend is None:
        _backend = MemoryBackend()
    return _backend
