"""SQLite Memory Store — Scalable persistence layer for Clawd's memory.

Provides async SQLite storage with:
- FTS5 full-text search for keyword queries
- WAL mode for concurrent reads
- Tables: episodes, goals, principles, memory_items, kg_entities, kg_edges
- Migration script to import existing JSON data
- Backward compatible: falls back to JSON if SQLite unavailable
"""
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import config

logger = logging.getLogger("clawd.tools.sqlite_store")

DB_PATH = config.MEMORY_DIR / "clawd_memory.db"

_db = None  # Lazy-initialized aiosqlite connection
_db_init_lock = asyncio.Lock()  # Prevents concurrent init races


async def get_db():
    """Get or create the async SQLite connection. Thread-safe via asyncio.Lock."""
    global _db
    if _db is not None:
        return _db

    async with _db_init_lock:
        # Double-check after acquiring lock (another coroutine may have initialized)
        if _db is not None:
            return _db

        try:
            import aiosqlite
        except ImportError:
            logger.warning("aiosqlite not installed — SQLite store unavailable. Install with: pip install aiosqlite")
            return None

        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        _db = await aiosqlite.connect(str(DB_PATH))
        _db.row_factory = aiosqlite.Row

        # WAL mode for concurrent reads + FULL sync for durability
        await _db.execute("PRAGMA journal_mode=WAL")
        await _db.execute("PRAGMA synchronous=FULL")

        # Create tables
        await _create_tables(_db)

        logger.info(f"SQLite memory store initialized: {DB_PATH}")
        return _db


async def close_db():
    """Close the database connection with WAL checkpoint for durability."""
    global _db
    if _db is not None:
        try:
            await _db.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        except Exception as e:
            logger.debug(f"WAL checkpoint on shutdown failed: {e}")
        await _db.close()
        _db = None


async def periodic_wal_checkpoint() -> dict:
    """Run a passive WAL checkpoint. Call periodically (e.g. every 10 heartbeats).
    Returns checkpoint status including WAL size."""
    db = await get_db()
    if not db:
        return {"status": "no_db"}
    try:
        cursor = await db.execute("PRAGMA wal_checkpoint(PASSIVE)")
        row = await cursor.fetchone()
        # row = (busy, log_pages, checkpointed_pages)
        wal_path = DB_PATH.with_suffix(".db-wal")
        wal_size = wal_path.stat().st_size if wal_path.exists() else 0
        result = {
            "status": "ok",
            "busy": row[0] if row else 0,
            "log_pages": row[1] if row else 0,
            "checkpointed_pages": row[2] if row else 0,
            "wal_size_bytes": wal_size,
        }
        logger.debug(f"WAL checkpoint: {result}")
        return result
    except Exception as e:
        logger.warning(f"WAL checkpoint failed: {e}")
        return {"status": "error", "error": str(e)}


async def check_db_health() -> bool:
    """Verify the database connection is alive with a simple query."""
    db = await get_db()
    if not db:
        return False
    try:
        cursor = await db.execute("SELECT 1")
        row = await cursor.fetchone()
        return row is not None and row[0] == 1
    except Exception as e:
        logger.warning(f"DB health check failed: {e}")
        return False


async def reconnect_db():
    """Close and reopen the database connection if it becomes stale."""
    global _db
    async with _db_init_lock:
        if _db is not None:
            try:
                await _db.close()
            except Exception as e:
                logger.debug(f"Error closing database connection: {e}")
            _db = None
    # get_db() will reinitialize on next call
    return await get_db()


async def cleanup_old_episodes(days: int = 90) -> int:
    """Delete episodes older than `days`. Returns count of deleted rows."""
    db = await get_db()
    if not db:
        return 0
    try:
        from datetime import datetime, timedelta
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        cursor = await db.execute("DELETE FROM episodes WHERE timestamp < ?", (cutoff,))
        await db.commit()
        deleted = cursor.rowcount
        if deleted:
            logger.info(f"Cleaned up {deleted} episodes older than {days} days")
        return deleted
    except Exception as e:
        logger.warning(f"cleanup_old_episodes failed: {e}")
        return 0


async def cleanup_cold_items(min_importance: float = 0.2, min_access_count: int = 1,
                             days: int = 60) -> int:
    """Delete memory items that are cold (low importance, rarely accessed, old).
    Returns count of deleted rows."""
    db = await get_db()
    if not db:
        return 0
    try:
        from datetime import datetime, timedelta
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        cursor = await db.execute(
            """DELETE FROM memory_items
               WHERE importance < ?
               AND access_count <= ?
               AND last_accessed < ?""",
            (min_importance, min_access_count, cutoff),
        )
        await db.commit()
        deleted = cursor.rowcount
        if deleted:
            logger.info(f"Cleaned up {deleted} cold memory items (importance<{min_importance}, "
                        f"access_count<={min_access_count}, older than {days} days)")
        return deleted
    except Exception as e:
        logger.warning(f"cleanup_cold_items failed: {e}")
        return 0


async def _create_tables(db):
    """Create all tables and FTS5 indexes."""
    await db.executescript("""
        -- Episodes (experiences)
        CREATE TABLE IF NOT EXISTS episodes (
            id INTEGER PRIMARY KEY,
            task TEXT NOT NULL,
            approach TEXT DEFAULT '',
            tools_used TEXT DEFAULT '',
            outcome TEXT DEFAULT 'success',
            score REAL DEFAULT 0.7,
            reflection TEXT DEFAULT '',
            lesson TEXT DEFAULT '',
            category TEXT DEFAULT 'general',
            timestamp TEXT NOT NULL,
            predicted_outcome TEXT,
            predicted_difficulty TEXT,
            actual_difficulty TEXT,
            calibration_error REAL,
            counterfactual TEXT DEFAULT '',
            times_retrieved INTEGER DEFAULT 0,
            retrievals_led_to_success INTEGER DEFAULT 0,
            q_value REAL DEFAULT 0.5,
            trigger TEXT DEFAULT '',
            tags TEXT DEFAULT '[]',
            linked_episodes TEXT DEFAULT '[]',
            evolved_from INTEGER,
            supersedes INTEGER,
            confidence REAL DEFAULT 0.7
        );

        -- Goals
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            priority TEXT DEFAULT 'medium',
            status TEXT DEFAULT 'active',
            progress INTEGER DEFAULT 0,
            created TEXT NOT NULL,
            updated TEXT NOT NULL,
            milestones TEXT DEFAULT '[]',
            notes TEXT DEFAULT '[]',
            acceptance_criteria TEXT DEFAULT '[]',
            sub_goals TEXT DEFAULT '[]',
            parent_id INTEGER
        );

        -- Principles
        CREATE TABLE IF NOT EXISTS principles (
            id INTEGER PRIMARY KEY,
            principle TEXT NOT NULL,
            derived_from TEXT DEFAULT '[]',
            category TEXT DEFAULT 'general',
            confidence REAL DEFAULT 0.5,
            times_applied INTEGER DEFAULT 0,
            success_rate_when_applied REAL DEFAULT 0.5,
            created TEXT NOT NULL,
            last_validated TEXT
        );

        -- Memory Items
        CREATE TABLE IF NOT EXISTS memory_items (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            content TEXT NOT NULL,
            source TEXT DEFAULT '',
            categories TEXT DEFAULT '[]',
            related_items TEXT DEFAULT '[]',
            links TEXT DEFAULT '[]',
            keywords TEXT DEFAULT '[]',
            importance INTEGER DEFAULT 5,
            created TEXT NOT NULL,
            last_accessed TEXT,
            access_count INTEGER DEFAULT 0,
            utility_score REAL DEFAULT 0.5,
            confidence REAL DEFAULT 0.8,
            retrieval_led_to_success INTEGER DEFAULT 0,
            q_value REAL DEFAULT 0.5,
            decay_rate REAL DEFAULT 0.995,
            memory_tier TEXT DEFAULT 'warm'
        );

        -- Knowledge Graph Entities
        CREATE TABLE IF NOT EXISTS kg_entities (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            properties TEXT DEFAULT '{}',
            created_at TEXT NOT NULL,
            valid_from TEXT NOT NULL
        );

        -- Knowledge Graph Edges
        CREATE TABLE IF NOT EXISTS kg_edges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_entity TEXT NOT NULL,
            to_entity TEXT NOT NULL,
            relation TEXT NOT NULL,
            valid_from TEXT NOT NULL,
            valid_to TEXT,
            FOREIGN KEY (from_entity) REFERENCES kg_entities(id),
            FOREIGN KEY (to_entity) REFERENCES kg_entities(id)
        );

        -- Semantic Notes (HiMem-style clustered episode summaries)
        CREATE TABLE IF NOT EXISTS semantic_notes (
            id TEXT PRIMARY KEY,
            topic TEXT NOT NULL,
            summary TEXT NOT NULL,
            insight TEXT DEFAULT '',
            source_episode_ids TEXT DEFAULT '[]',
            source_item_ids TEXT DEFAULT '[]',
            importance INTEGER DEFAULT 5,
            created TEXT NOT NULL
        );

        -- Embeddings (future sqlite-vec integration)
        CREATE TABLE IF NOT EXISTS embeddings (
            id TEXT PRIMARY KEY,
            source_type TEXT NOT NULL,
            source_id TEXT NOT NULL,
            vector BLOB,
            model TEXT DEFAULT '',
            created TEXT NOT NULL
        );

        -- Execution Plans (persistent DAG execution)
        CREATE TABLE IF NOT EXISTS execution_plans (
            id TEXT PRIMARY KEY,
            task_description TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            total_waves INTEGER DEFAULT 0,
            replan_count INTEGER DEFAULT 0
        );

        -- Execution Nodes (individual steps in a plan)
        CREATE TABLE IF NOT EXISTS execution_nodes (
            id TEXT PRIMARY KEY,
            plan_id TEXT NOT NULL,
            prompt TEXT NOT NULL,
            model TEXT DEFAULT '',
            status TEXT DEFAULT 'pending',
            result TEXT DEFAULT '',
            error TEXT DEFAULT '',
            wave INTEGER DEFAULT 0,
            retry_count INTEGER DEFAULT 0,
            FOREIGN KEY (plan_id) REFERENCES execution_plans(id)
        );

        -- Execution Edges (dependencies between nodes)
        CREATE TABLE IF NOT EXISTS execution_edges (
            plan_id TEXT NOT NULL,
            from_node TEXT NOT NULL,
            to_node TEXT NOT NULL,
            FOREIGN KEY (plan_id) REFERENCES execution_plans(id),
            FOREIGN KEY (from_node) REFERENCES execution_nodes(id),
            FOREIGN KEY (to_node) REFERENCES execution_nodes(id)
        );

        -- FTS5 indexes for keyword search
        CREATE VIRTUAL TABLE IF NOT EXISTS episodes_fts USING fts5(
            task, approach, lesson, category, reflection,
            content='episodes',
            content_rowid='id'
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS memory_items_fts USING fts5(
            content, source, keywords,
            content='memory_items'
        );

        -- Performance indexes
        CREATE INDEX IF NOT EXISTS idx_goals_status ON goals(status);
        CREATE INDEX IF NOT EXISTS idx_goals_priority ON goals(priority);
        CREATE INDEX IF NOT EXISTS idx_memory_items_tier ON memory_items(memory_tier);
        CREATE INDEX IF NOT EXISTS idx_episodes_category ON episodes(category);
        CREATE INDEX IF NOT EXISTS idx_episodes_outcome ON episodes(outcome);
        CREATE INDEX IF NOT EXISTS idx_kg_edges_from ON kg_edges(from_entity);
        CREATE INDEX IF NOT EXISTS idx_kg_edges_to ON kg_edges(to_entity);
        CREATE INDEX IF NOT EXISTS idx_execution_nodes_plan ON execution_nodes(plan_id);
        CREATE INDEX IF NOT EXISTS idx_execution_nodes_status ON execution_nodes(status);
        CREATE INDEX IF NOT EXISTS idx_execution_edges_plan ON execution_edges(plan_id);
        CREATE INDEX IF NOT EXISTS idx_embeddings_source ON embeddings(source_type, source_id);

        -- EAC Artifacts (Evolutionary Artifact Construction)
        CREATE TABLE IF NOT EXISTS eac_artifacts (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            artifact_type TEXT DEFAULT 'tool',
            generation INTEGER DEFAULT 0,
            fitness_correctness REAL DEFAULT 0.5,
            fitness_performance REAL DEFAULT 0.5,
            fitness_readability REAL DEFAULT 0.5,
            fitness_brevity REAL DEFAULT 0.5,
            fitness_overall REAL DEFAULT 0.5,
            parents TEXT DEFAULT '[]',
            mutations TEXT DEFAULT '[]',
            created_by TEXT DEFAULT 'seed',
            status TEXT DEFAULT 'active',
            code_hash TEXT DEFAULT '',
            created_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_eac_artifacts_type ON eac_artifacts(artifact_type);
        CREATE INDEX IF NOT EXISTS idx_eac_artifacts_status ON eac_artifacts(status);
        CREATE INDEX IF NOT EXISTS idx_eac_artifacts_generation ON eac_artifacts(generation);
    """)

    # FTS5 sync triggers for episodes
    await db.executescript("""
        CREATE TRIGGER IF NOT EXISTS episodes_ai AFTER INSERT ON episodes BEGIN
            INSERT INTO episodes_fts(rowid, task, approach, lesson, category, reflection)
            VALUES (new.id, new.task, new.approach, new.lesson, new.category, new.reflection);
        END;

        CREATE TRIGGER IF NOT EXISTS episodes_ad AFTER DELETE ON episodes BEGIN
            INSERT INTO episodes_fts(episodes_fts, rowid, task, approach, lesson, category, reflection)
            VALUES ('delete', old.id, old.task, old.approach, old.lesson, old.category, old.reflection);
        END;

        CREATE TRIGGER IF NOT EXISTS episodes_au AFTER UPDATE ON episodes BEGIN
            INSERT INTO episodes_fts(episodes_fts, rowid, task, approach, lesson, category, reflection)
            VALUES ('delete', old.id, old.task, old.approach, old.lesson, old.category, old.reflection);
            INSERT INTO episodes_fts(rowid, task, approach, lesson, category, reflection)
            VALUES (new.id, new.task, new.approach, new.lesson, new.category, new.reflection);
        END;

        CREATE TRIGGER IF NOT EXISTS memory_items_ai AFTER INSERT ON memory_items BEGIN
            INSERT INTO memory_items_fts(rowid, content, source, keywords)
            VALUES (new.rowid, new.content, new.source, new.keywords);
        END;

        CREATE TRIGGER IF NOT EXISTS memory_items_ad AFTER DELETE ON memory_items BEGIN
            INSERT INTO memory_items_fts(memory_items_fts, rowid, content, source, keywords)
            VALUES ('delete', old.rowid, old.content, old.source, old.keywords);
        END;

        CREATE TRIGGER IF NOT EXISTS memory_items_au AFTER UPDATE ON memory_items BEGIN
            INSERT INTO memory_items_fts(memory_items_fts, rowid, content, source, keywords)
            VALUES ('delete', old.rowid, old.content, old.source, old.keywords);
            INSERT INTO memory_items_fts(rowid, content, source, keywords)
            VALUES (new.rowid, new.content, new.source, new.keywords);
        END;
    """)

    # Schema v2 migration: add provenance fields
    await _migrate_schema_v2(db)

    await db.commit()


async def migrate_json_to_sqlite():
    """Migrate existing JSON data to SQLite.
    Preserves JSON files as backups."""
    db = await get_db()
    if db is None:
        return "SQLite not available (aiosqlite not installed)."

    results = []

    # 1. Migrate experiences
    exp_file = config.MEMORY_DIR / "experiences.json"
    if exp_file.exists():
        try:
            experiences = json.loads(exp_file.read_text(encoding="utf-8"))
            count = 0
            for e in experiences:
                await db.execute("""
                    INSERT OR REPLACE INTO episodes (id, task, approach, tools_used, outcome, score,
                        reflection, lesson, category, timestamp, predicted_outcome, predicted_difficulty,
                        actual_difficulty, calibration_error, counterfactual, times_retrieved,
                        retrievals_led_to_success, q_value, trigger, tags, linked_episodes,
                        evolved_from, supersedes, confidence)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    e.get("id"), e.get("task", ""), e.get("approach", ""),
                    e.get("tools_used", ""), e.get("outcome", "success"),
                    e.get("score", 0.7), e.get("reflection", ""), e.get("lesson", ""),
                    e.get("category", "general"), e.get("timestamp", datetime.now().isoformat()),
                    e.get("predicted_outcome"), e.get("predicted_difficulty"),
                    e.get("actual_difficulty"), e.get("calibration_error"),
                    e.get("counterfactual", ""), e.get("times_retrieved", 0),
                    e.get("retrievals_led_to_success", 0), e.get("q_value", 0.5),
                    e.get("trigger", ""), json.dumps(e.get("tags", [])),
                    json.dumps(e.get("linked_episodes", [])),
                    e.get("evolved_from"), e.get("supersedes"), e.get("confidence", 0.7),
                ))
                count += 1
            await db.commit()
            results.append(f"Migrated {count} episodes")
        except Exception as e:
            results.append(f"Episodes migration error: {e}")

    # 2. Migrate goals
    goals_file = config.MEMORY_DIR / "goals.json"
    if goals_file.exists():
        try:
            goals = json.loads(goals_file.read_text(encoding="utf-8"))
            count = 0
            for g in goals:
                await db.execute("""
                    INSERT OR REPLACE INTO goals (id, title, description, priority, status, progress,
                        created, updated, milestones, notes, acceptance_criteria, sub_goals, parent_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    g.get("id"), g.get("title", ""), g.get("description", ""),
                    g.get("priority", "medium"), g.get("status", "active"),
                    g.get("progress", 0), g.get("created", ""), g.get("updated", ""),
                    json.dumps(g.get("milestones", [])), json.dumps(g.get("notes", [])),
                    json.dumps(g.get("acceptance_criteria", [])),
                    json.dumps(g.get("sub_goals", [])), g.get("parent_id"),
                ))
                count += 1
            await db.commit()
            results.append(f"Migrated {count} goals")
        except Exception as e:
            results.append(f"Goals migration error: {e}")

    # 3. Migrate principles
    principles_file = config.MEMORY_DIR / "principles.json"
    if principles_file.exists():
        try:
            principles = json.loads(principles_file.read_text(encoding="utf-8"))
            count = 0
            for p in principles:
                await db.execute("""
                    INSERT OR REPLACE INTO principles (id, principle, derived_from, category,
                        confidence, times_applied, success_rate_when_applied, created, last_validated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    p.get("id"), p.get("principle", ""), json.dumps(p.get("derived_from", [])),
                    p.get("category", "general"), p.get("confidence", 0.5),
                    p.get("times_applied", 0), p.get("success_rate_when_applied", 0.5),
                    p.get("created", ""), p.get("last_validated"),
                ))
                count += 1
            await db.commit()
            results.append(f"Migrated {count} principles")
        except Exception as e:
            results.append(f"Principles migration error: {e}")

    # 4. Migrate memory items
    if config.MEMORY_ITEMS_DIR.is_dir():
        try:
            count = 0
            for fpath in config.MEMORY_ITEMS_DIR.glob("*.json"):
                if fpath.name == "_index.json":
                    continue
                item = json.loads(fpath.read_text(encoding="utf-8"))
                await db.execute("""
                    INSERT OR REPLACE INTO memory_items (id, type, content, source, categories,
                        related_items, links, keywords, importance, created, last_accessed,
                        access_count, utility_score, confidence, retrieval_led_to_success,
                        q_value, decay_rate, memory_tier)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    item.get("id"), item.get("type", "fact"), item.get("content", ""),
                    item.get("source", ""), json.dumps(item.get("categories", [])),
                    json.dumps(item.get("related_items", [])), json.dumps(item.get("links", [])),
                    json.dumps(item.get("keywords", [])), item.get("importance", 5),
                    item.get("created", ""), item.get("last_accessed", ""),
                    item.get("access_count", 0), item.get("utility_score", 0.5),
                    item.get("confidence", 0.8), item.get("retrieval_led_to_success", 0),
                    item.get("q_value", 0.5), item.get("decay_rate", 0.995),
                    item.get("memory_tier", "warm"),
                ))
                count += 1
            await db.commit()
            results.append(f"Migrated {count} memory items")
        except Exception as e:
            results.append(f"Memory items migration error: {e}")

    # 5. Migrate knowledge graph
    kg_file = config.MEMORY_DIR / "knowledge_graph.json"
    if kg_file.exists():
        def _txt(v, default=""):
            if v is None:
                return default
            if isinstance(v, str):
                return v
            if isinstance(v, (dict, list)):
                return json.dumps(v, ensure_ascii=False)
            return str(v)
        try:
            kg = json.loads(kg_file.read_text(encoding="utf-8"))
            entity_count = 0
            entity_errors = 0
            for eid, e in kg.get("entities", {}).items():
                if not isinstance(e, dict):
                    entity_errors += 1
                    continue
                try:
                    await db.execute("""
                        INSERT OR REPLACE INTO kg_entities (id, name, type, properties, created_at, valid_from)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        _txt(eid), _txt(e.get("name"), default=_txt(eid)),
                        _txt(e.get("type"), default="concept"),
                        json.dumps(e.get("properties", {}), ensure_ascii=False),
                        _txt(e.get("created_at")), _txt(e.get("valid_from")),
                    ))
                    entity_count += 1
                except Exception as ee:
                    entity_errors += 1
                    logger.debug(f"KG entity migration skipped (id={eid!r}): {ee}")

            edge_count = 0
            edge_errors = 0
            for edge in kg.get("edges", []):
                if not isinstance(edge, dict):
                    edge_errors += 1
                    continue
                try:
                    await db.execute("""
                        INSERT INTO kg_edges (from_entity, to_entity, relation, valid_from, valid_to)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        _txt(edge.get("from")), _txt(edge.get("to")), _txt(edge.get("relation")),
                        _txt(edge.get("valid_from")), _txt(edge.get("valid_to")) or None,
                    ))
                    edge_count += 1
                except Exception as ee:
                    edge_errors += 1
                    logger.debug(f"KG edge migration skipped (from={edge.get('from')!r} to={edge.get('to')!r}): {ee}")

            await db.commit()
            tail = f" ({entity_errors} entity / {edge_errors} edge records skipped)" if (entity_errors or edge_errors) else ""
            results.append(f"Migrated {entity_count} entities and {edge_count} edges" + tail)
        except Exception as e:
            results.append(f"Knowledge graph migration error: {e}")

    # Rebuild FTS indexes
    try:
        await db.execute("INSERT INTO episodes_fts(episodes_fts) VALUES('rebuild')")
        await db.commit()
        results.append("FTS indexes rebuilt")
    except Exception as e:
        logger.debug(f"FTS rebuild skipped: {e}")

    return "SQLite migration complete:\n" + "\n".join(f"  - {r}" for r in results)


# === Query helpers for tool integration ===

async def search_episodes_fts(query: str, limit: int = 10) -> list[dict]:
    """Full-text search across episodes."""
    db = await get_db()
    if db is None:
        return []

    try:
        cursor = await db.execute("""
            SELECT e.* FROM episodes e
            JOIN episodes_fts f ON e.id = f.rowid
            WHERE episodes_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (query, limit))
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
    except Exception as e:
        logger.debug(f"FTS search error: {e}")
        return []


async def get_goals_by_status(status: str = "active") -> list[dict]:
    """Get goals filtered by status, ordered by priority."""
    db = await get_db()
    if db is None:
        return []

    priority_order = "CASE priority WHEN 'high' THEN 0 WHEN 'medium' THEN 1 WHEN 'low' THEN 2 END"
    cursor = await db.execute(
        f"SELECT * FROM goals WHERE status = ? ORDER BY {priority_order}",
        (status,)
    )
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]


async def get_items_by_tier(tier: str = "hot") -> list[dict]:
    """Get memory items filtered by tier."""
    db = await get_db()
    if db is None:
        return []

    cursor = await db.execute(
        "SELECT * FROM memory_items WHERE memory_tier = ? ORDER BY q_value DESC",
        (tier,)
    )
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]


async def get_episodes_by_category(category: str, limit: int = 20) -> list[dict]:
    """Get episodes filtered by category."""
    db = await get_db()
    if db is None:
        return []

    cursor = await db.execute(
        "SELECT * FROM episodes WHERE category = ? ORDER BY timestamp DESC LIMIT ?",
        (category, limit)
    )
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]


# === Schema v2 Migration: Provenance Fields ===

async def _migrate_schema_v2(db):
    """Add provenance fields (source_hash, confidence_history) to tables."""
    try:
        await db.execute("SELECT source_hash FROM memory_items LIMIT 1")
    except Exception:
        try:
            await db.execute("ALTER TABLE memory_items ADD COLUMN source_hash TEXT DEFAULT ''")
            await db.execute("ALTER TABLE memory_items ADD COLUMN confidence_history TEXT DEFAULT '[]'")
            logger.info("Schema v2: added provenance fields to memory_items")
        except Exception as e:
            logger.debug(f"Schema v2 memory_items migration skipped: {e}")

    try:
        await db.execute("SELECT source_hash FROM episodes LIMIT 1")
    except Exception:
        try:
            await db.execute("ALTER TABLE episodes ADD COLUMN source_hash TEXT DEFAULT ''")
            await db.execute("ALTER TABLE episodes ADD COLUMN confidence_history TEXT DEFAULT '[]'")
            logger.info("Schema v2: added provenance fields to episodes")
        except Exception as e:
            logger.debug(f"Schema v2 episodes migration skipped: {e}")


# === CRUD Methods for MemoryBackend ===

async def upsert_memory_item(item: dict) -> bool:
    """Insert or update a memory item."""
    db = await get_db()
    if db is None:
        return False
    try:
        await db.execute("""
            INSERT OR REPLACE INTO memory_items (id, type, content, source, categories,
                related_items, links, keywords, importance, created, last_accessed,
                access_count, utility_score, confidence, retrieval_led_to_success,
                q_value, decay_rate, memory_tier, source_hash, confidence_history)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item.get("id"), item.get("type", "fact"), item.get("content", ""),
            item.get("source", ""), json.dumps(item.get("categories", [])),
            json.dumps(item.get("related_items", [])), json.dumps(item.get("links", [])),
            json.dumps(item.get("keywords", [])), item.get("importance", 5),
            item.get("created", datetime.now().isoformat()),
            item.get("last_accessed", ""), item.get("access_count", 0),
            item.get("utility_score", 0.5), item.get("confidence", 0.8),
            item.get("retrieval_led_to_success", 0), item.get("q_value", 0.5),
            item.get("decay_rate", 0.995), item.get("memory_tier", "warm"),
            item.get("source_hash", ""), json.dumps(item.get("confidence_history", [])),
        ))
        await db.commit()
        return True
    except Exception as e:
        logger.error(f"upsert_memory_item failed: {e}")
        return False


async def get_memory_item(item_id: str) -> Optional[dict]:
    """Load a single memory item by ID."""
    db = await get_db()
    if db is None:
        return None
    try:
        cursor = await db.execute("SELECT * FROM memory_items WHERE id = ?", (item_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None
    except Exception as e:
        logger.error(f"get_memory_item failed: {e}")
        return None


async def delete_memory_item(item_id: str) -> bool:
    """Delete a memory item by ID."""
    db = await get_db()
    if db is None:
        return False
    try:
        await db.execute("DELETE FROM memory_items WHERE id = ?", (item_id,))
        await db.commit()
        return True
    except Exception as e:
        logger.error(f"delete_memory_item failed: {e}")
        return False


async def search_memory_items_fts(query: str, limit: int = 20) -> list[dict]:
    """Full-text search across memory items."""
    db = await get_db()
    if db is None:
        return []
    try:
        cursor = await db.execute("""
            SELECT m.* FROM memory_items m
            JOIN memory_items_fts f ON m.rowid = f.rowid
            WHERE memory_items_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (query, limit))
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
    except Exception as e:
        logger.debug(f"Memory items FTS search error: {e}")
        return []


async def get_all_items(tier: Optional[str] = None) -> list[dict]:
    """Get all memory items, optionally filtered by tier."""
    db = await get_db()
    if db is None:
        return []
    try:
        if tier:
            cursor = await db.execute(
                "SELECT * FROM memory_items WHERE memory_tier = ? ORDER BY q_value DESC", (tier,))
        else:
            cursor = await db.execute("SELECT * FROM memory_items ORDER BY q_value DESC")
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
    except Exception as e:
        logger.error(f"get_all_items failed: {e}")
        return []


async def batch_update_items(updates: list[dict]) -> int:
    """Batch update multiple memory items. Each dict must have 'id' and fields to update."""
    db = await get_db()
    if db is None:
        return 0
    count = 0
    try:
        for upd in updates:
            item_id = upd.pop("id", None)
            if not item_id or not upd:
                continue
            set_clauses = []
            values = []
            for k, v in upd.items():
                set_clauses.append(f"{k} = ?")
                values.append(json.dumps(v) if isinstance(v, (list, dict)) else v)
            values.append(item_id)
            await db.execute(
                f"UPDATE memory_items SET {', '.join(set_clauses)} WHERE id = ?",
                tuple(values)
            )
            count += 1
        await db.commit()
        return count
    except Exception as e:
        logger.error(f"batch_update_items failed: {e}")
        return 0


async def upsert_episode(episode: dict) -> bool:
    """Insert or update an episode."""
    db = await get_db()
    if db is None:
        return False
    try:
        await db.execute("""
            INSERT OR REPLACE INTO episodes (id, task, approach, tools_used, outcome, score,
                reflection, lesson, category, timestamp, predicted_outcome, predicted_difficulty,
                actual_difficulty, calibration_error, counterfactual, times_retrieved,
                retrievals_led_to_success, q_value, trigger, tags, linked_episodes,
                evolved_from, supersedes, confidence, source_hash, confidence_history)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            episode.get("id"), episode.get("task", ""), episode.get("approach", ""),
            episode.get("tools_used", ""), episode.get("outcome", "success"),
            episode.get("score", 0.7), episode.get("reflection", ""),
            episode.get("lesson", ""), episode.get("category", "general"),
            episode.get("timestamp", datetime.now().isoformat()),
            episode.get("predicted_outcome"), episode.get("predicted_difficulty"),
            episode.get("actual_difficulty"), episode.get("calibration_error"),
            episode.get("counterfactual", ""), episode.get("times_retrieved", 0),
            episode.get("retrievals_led_to_success", 0), episode.get("q_value", 0.5),
            episode.get("trigger", ""), json.dumps(episode.get("tags", [])),
            json.dumps(episode.get("linked_episodes", [])),
            episode.get("evolved_from"), episode.get("supersedes"),
            episode.get("confidence", 0.7),
            episode.get("source_hash", ""), json.dumps(episode.get("confidence_history", [])),
        ))
        await db.commit()
        return True
    except Exception as e:
        logger.error(f"upsert_episode failed: {e}")
        return False


async def load_episodes(category: Optional[str] = None, limit: int = 100) -> list[dict]:
    """Load episodes, optionally filtered by category."""
    db = await get_db()
    if db is None:
        return []
    try:
        if category:
            cursor = await db.execute(
                "SELECT * FROM episodes WHERE category = ? ORDER BY timestamp DESC LIMIT ?",
                (category, limit))
        else:
            cursor = await db.execute(
                "SELECT * FROM episodes ORDER BY timestamp DESC LIMIT ?", (limit,))
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
    except Exception as e:
        logger.error(f"load_episodes failed: {e}")
        return []


async def upsert_goal(goal: dict) -> bool:
    """Insert or update a goal."""
    db = await get_db()
    if db is None:
        return False
    try:
        await db.execute("""
            INSERT OR REPLACE INTO goals (id, title, description, priority, status, progress,
                created, updated, milestones, notes, acceptance_criteria, sub_goals, parent_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            goal.get("id"), goal.get("title", ""), goal.get("description", ""),
            goal.get("priority", "medium"), goal.get("status", "active"),
            goal.get("progress", 0),
            goal.get("created", datetime.now().isoformat()),
            goal.get("updated", datetime.now().isoformat()),
            json.dumps(goal.get("milestones", [])), json.dumps(goal.get("notes", [])),
            json.dumps(goal.get("acceptance_criteria", [])),
            json.dumps(goal.get("sub_goals", [])), goal.get("parent_id"),
        ))
        await db.commit()
        return True
    except Exception as e:
        logger.error(f"upsert_goal failed: {e}")
        return False


async def load_goals(status: Optional[str] = None) -> list[dict]:
    """Load goals, optionally filtered by status."""
    db = await get_db()
    if db is None:
        return []
    try:
        if status:
            cursor = await db.execute("SELECT * FROM goals WHERE status = ?", (status,))
        else:
            cursor = await db.execute("SELECT * FROM goals")
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
    except Exception as e:
        logger.error(f"load_goals failed: {e}")
        return []


async def delete_goal(goal_id) -> bool:
    """Delete a goal by ID."""
    db = await get_db()
    if db is None:
        return False
    try:
        await db.execute("DELETE FROM goals WHERE id = ?", (goal_id,))
        await db.commit()
        return True
    except Exception as e:
        logger.error(f"delete_goal failed: {e}")
        return False


async def upsert_principle(principle: dict) -> bool:
    """Insert or update a principle."""
    db = await get_db()
    if db is None:
        return False
    try:
        await db.execute("""
            INSERT OR REPLACE INTO principles (id, principle, derived_from, category,
                confidence, times_applied, success_rate_when_applied, created, last_validated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            principle.get("id"), principle.get("principle", ""),
            json.dumps(principle.get("derived_from", [])),
            principle.get("category", "general"), principle.get("confidence", 0.5),
            principle.get("times_applied", 0),
            principle.get("success_rate_when_applied", 0.5),
            principle.get("created", datetime.now().isoformat()),
            principle.get("last_validated"),
        ))
        await db.commit()
        return True
    except Exception as e:
        logger.error(f"upsert_principle failed: {e}")
        return False


async def load_principles() -> list[dict]:
    """Load all principles."""
    db = await get_db()
    if db is None:
        return []
    try:
        cursor = await db.execute("SELECT * FROM principles ORDER BY confidence DESC")
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
    except Exception as e:
        logger.error(f"load_principles failed: {e}")
        return []


async def upsert_entity(entity_id: str, entity: dict) -> bool:
    """Insert or update a KG entity."""
    db = await get_db()
    if db is None:
        return False
    try:
        await db.execute("""
            INSERT OR REPLACE INTO kg_entities (id, name, type, properties, created_at, valid_from)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            entity_id, entity.get("name", entity_id), entity.get("type", "concept"),
            json.dumps(entity.get("properties", {})),
            entity.get("created_at", datetime.now().isoformat()),
            entity.get("valid_from", datetime.now().isoformat()),
        ))
        await db.commit()
        return True
    except Exception as e:
        logger.error(f"upsert_entity failed: {e}")
        return False


async def upsert_edge(from_entity: str, to_entity: str, relation: str) -> bool:
    """Insert a KG edge if not duplicate."""
    db = await get_db()
    if db is None:
        return False
    try:
        cursor = await db.execute(
            "SELECT id FROM kg_edges WHERE from_entity=? AND to_entity=? AND relation=? AND valid_to IS NULL",
            (from_entity, to_entity, relation))
        if await cursor.fetchone():
            return True  # Already exists
        await db.execute("""
            INSERT INTO kg_edges (from_entity, to_entity, relation, valid_from)
            VALUES (?, ?, ?, ?)
        """, (from_entity, to_entity, relation, datetime.now().isoformat()))
        await db.commit()
        return True
    except Exception as e:
        logger.error(f"upsert_edge failed: {e}")
        return False


async def load_graph() -> dict:
    """Load the full knowledge graph from SQLite."""
    db = await get_db()
    if db is None:
        return {"entities": {}, "edges": []}
    try:
        entities = {}
        cursor = await db.execute("SELECT * FROM kg_entities")
        for row in await cursor.fetchall():
            r = dict(row)
            entities[r["id"]] = r
        edges = []
        cursor = await db.execute("SELECT * FROM kg_edges WHERE valid_to IS NULL")
        for row in await cursor.fetchall():
            r = dict(row)
            edges.append({"from": r["from_entity"], "to": r["to_entity"],
                          "relation": r["relation"], "valid_from": r["valid_from"]})
        return {"entities": entities, "edges": edges}
    except Exception as e:
        logger.error(f"load_graph failed: {e}")
        return {"entities": {}, "edges": []}


# === Execution Plan Helpers ===

async def create_execution_plan(plan_id: str, task_description: str) -> bool:
    """Create a new execution plan."""
    db = await get_db()
    if db is None:
        return False
    try:
        now = datetime.now().isoformat()
        await db.execute(
            "INSERT INTO execution_plans (id, task_description, status, created_at, updated_at) VALUES (?, ?, 'pending', ?, ?)",
            (plan_id, task_description, now, now))
        await db.commit()
        return True
    except Exception as e:
        logger.error(f"create_execution_plan failed: {e}")
        return False


async def add_execution_node(node_id: str, plan_id: str, prompt: str, model: str = "", wave: int = 0) -> bool:
    """Add a node to an execution plan."""
    db = await get_db()
    if db is None:
        return False
    try:
        await db.execute(
            "INSERT INTO execution_nodes (id, plan_id, prompt, model, wave) VALUES (?, ?, ?, ?, ?)",
            (node_id, plan_id, prompt, model, wave))
        await db.commit()
        return True
    except Exception as e:
        logger.error(f"add_execution_node failed: {e}")
        return False


async def add_execution_edge(plan_id: str, from_node: str, to_node: str) -> bool:
    """Add a dependency edge between execution nodes."""
    db = await get_db()
    if db is None:
        return False
    try:
        await db.execute(
            "INSERT INTO execution_edges (plan_id, from_node, to_node) VALUES (?, ?, ?)",
            (plan_id, from_node, to_node))
        await db.commit()
        return True
    except Exception as e:
        logger.error(f"add_execution_edge failed: {e}")
        return False


async def update_node_status(node_id: str, status: str, result: str = "", error: str = "") -> bool:
    """Update execution node status and result."""
    db = await get_db()
    if db is None:
        return False
    try:
        await db.execute(
            "UPDATE execution_nodes SET status=?, result=?, error=? WHERE id=?",
            (status, result, error, node_id))
        await db.commit()
        return True
    except Exception as e:
        logger.error(f"update_node_status failed: {e}")
        return False


async def update_plan_status(plan_id: str, status: str) -> bool:
    """Update execution plan status."""
    db = await get_db()
    if db is None:
        return False
    try:
        await db.execute(
            "UPDATE execution_plans SET status=?, updated_at=? WHERE id=?",
            (status, datetime.now().isoformat(), plan_id))
        await db.commit()
        return True
    except Exception as e:
        logger.error(f"update_plan_status failed: {e}")
        return False


async def get_plan_state(plan_id: str) -> Optional[dict]:
    """Get full execution plan state including nodes and edges."""
    db = await get_db()
    if db is None:
        return None
    try:
        cursor = await db.execute("SELECT * FROM execution_plans WHERE id=?", (plan_id,))
        plan_row = await cursor.fetchone()
        if not plan_row:
            return None
        plan = dict(plan_row)

        cursor = await db.execute("SELECT * FROM execution_nodes WHERE plan_id=?", (plan_id,))
        plan["nodes"] = [dict(r) for r in await cursor.fetchall()]

        cursor = await db.execute("SELECT * FROM execution_edges WHERE plan_id=?", (plan_id,))
        plan["edges"] = [dict(r) for r in await cursor.fetchall()]

        return plan
    except Exception as e:
        logger.error(f"get_plan_state failed: {e}")
        return None


async def get_ready_nodes(plan_id: str) -> list[dict]:
    """Get nodes that are ready to execute (pending, with all dependencies completed)."""
    db = await get_db()
    if db is None:
        return []
    try:
        cursor = await db.execute("""
            SELECT n.* FROM execution_nodes n
            WHERE n.plan_id = ? AND n.status = 'pending'
            AND NOT EXISTS (
                SELECT 1 FROM execution_edges e
                JOIN execution_nodes dep ON dep.id = e.from_node
                WHERE e.to_node = n.id AND e.plan_id = n.plan_id
                AND dep.status NOT IN ('success', 'skipped')
            )
        """, (plan_id,))
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
    except Exception as e:
        logger.error(f"get_ready_nodes failed: {e}")
        return []


async def get_plan_mermaid(plan_id: str) -> str:
    """Generate Mermaid flowchart from plan state."""
    state = await get_plan_state(plan_id)
    if not state:
        return "No plan found."
    lines = ["graph TD"]
    status_icons = {"pending": "⏳", "running": "🔄", "success": "✅", "failed": "❌", "skipped": "⏭️"}
    for node in state.get("nodes", []):
        icon = status_icons.get(node["status"], "?")
        label = node["prompt"][:40].replace('"', "'")
        lines.append(f'    {node["id"]}["{icon} {label}"]')
    for edge in state.get("edges", []):
        lines.append(f'    {edge["from_node"]} --> {edge["to_node"]}')
    return "\n".join(lines)


async def get_interrupted_plans() -> list[dict]:
    """Get plans that were interrupted (running status at shutdown)."""
    db = await get_db()
    if db is None:
        return []
    try:
        cursor = await db.execute("SELECT * FROM execution_plans WHERE status = 'running'")
        return [dict(r) for r in await cursor.fetchall()]
    except Exception as e:
        logger.error(f"get_interrupted_plans failed: {e}")
        return []


async def mark_interrupted_plans() -> int:
    """Mark all running plans as interrupted at shutdown."""
    db = await get_db()
    if db is None:
        return 0
    try:
        cursor = await db.execute(
            "UPDATE execution_plans SET status='interrupted', updated_at=? WHERE status='running'",
            (datetime.now().isoformat(),))
        await db.commit()
        return cursor.rowcount
    except Exception as e:
        logger.error(f"mark_interrupted_plans failed: {e}")
        return 0


# === Memory Reflection Query Helper ===

async def get_decayed_high_value_items(min_q_value: float = 0.4, limit: int = 3) -> list[dict]:
    """Get cold-tier items with historically high Q-values for memory reflection."""
    db = await get_db()
    if db is None:
        return []
    try:
        cursor = await db.execute("""
            SELECT * FROM memory_items
            WHERE memory_tier = 'cold' AND (q_value >= ? OR importance >= 7)
            ORDER BY RANDOM()
            LIMIT ?
        """, (min_q_value, limit))
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
    except Exception as e:
        logger.error(f"get_decayed_high_value_items failed: {e}")
        return []


# === Semantic Notes CRUD ===

async def store_eac_artifact(artifact: dict) -> bool:
    """Store an EAC artifact in SQLite."""
    db = await get_db()
    if db is None:
        return False
    try:
        await db.execute("""
            INSERT OR REPLACE INTO eac_artifacts (id, name, artifact_type, generation,
                fitness_correctness, fitness_performance, fitness_readability,
                fitness_brevity, fitness_overall, parents, mutations,
                created_by, status, code_hash, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            artifact["id"],
            artifact.get("name", ""),
            artifact.get("artifact_type", "tool"),
            artifact.get("generation", 0),
            artifact.get("fitness_correctness", 0.5),
            artifact.get("fitness_performance", 0.5),
            artifact.get("fitness_readability", 0.5),
            artifact.get("fitness_brevity", 0.5),
            artifact.get("fitness_overall", 0.5),
            json.dumps(artifact.get("parents", [])),
            json.dumps(artifact.get("mutations", [])),
            artifact.get("created_by", "seed"),
            artifact.get("status", "active"),
            artifact.get("code_hash", ""),
            artifact.get("created_at", datetime.now().isoformat()),
        ))
        await db.commit()
        return True
    except Exception as e:
        logger.error(f"store_eac_artifact failed: {e}")
        return False


async def upsert_semantic_note(note: dict) -> bool:
    """Insert or update a semantic note."""
    db = await get_db()
    if db is None:
        return False
    try:
        await db.execute("""
            INSERT OR REPLACE INTO semantic_notes (id, topic, summary, insight,
                source_episode_ids, source_item_ids, importance, created)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            note["id"], note.get("topic", ""), note.get("summary", ""),
            note.get("insight", ""),
            json.dumps(note.get("source_episode_ids", [])),
            json.dumps(note.get("source_item_ids", [])),
            note.get("importance", 5),
            note.get("created", datetime.now().isoformat()),
        ))
        await db.commit()
        return True
    except Exception as e:
        logger.error(f"upsert_semantic_note failed: {e}")
        return False
