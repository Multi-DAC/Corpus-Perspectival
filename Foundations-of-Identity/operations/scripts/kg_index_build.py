"""T1.A v0: Build SQLite bi-temporal index from JSONL canonical store.

Reads memory/kg_corpus_extraction.jsonl, deduplicates edges by
(source_file, target_concept, relation_kind), keeps the most recent extraction
per group, writes to memory/kg_index.db per the Memento-grounded schema.

Idempotent: drops and rebuilds the DB on each run. JSONL is canonical;
the index is derived. Future incremental builds can use --append mode but
v0 is full-rebuild for simplicity.

Usage:
    python operations/scripts/kg_index_build.py

A112 resolution for v0: source_concept = source_file (document-hub topology
preserved as-extracted; concept-as-aggregator second pass can come later).
"""
import json
import os
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

CLAWD = Path(r"C:\Users\mercu\clawd")
JSONL_PATH = CLAWD / "memory" / "kg_corpus_extraction.jsonl"
SCHEMA_PATH = CLAWD / "operations" / "scripts" / "kg_index_schema.sql"
DB_PATH = CLAWD / "memory" / "kg_index.db"


def main():
    print(f"[T1.A] Building SQLite bi-temporal index")
    print(f"  Source (canonical): {JSONL_PATH}")
    print(f"  Schema:             {SCHEMA_PATH}")
    print(f"  Output:             {DB_PATH}")
    print()

    # Drop existing DB for clean rebuild (v0 idempotent strategy)
    if DB_PATH.exists():
        DB_PATH.unlink()
        print(f"  Removed existing {DB_PATH.name}")

    # Create DB + schema
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA_PATH.read_text())
    print(f"  Schema applied")

    # Load JSONL into memory
    entries = []
    with open(JSONL_PATH, "r", encoding="utf-8") as f:
        for line in f:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    print(f"  Loaded {len(entries)} file-extraction records from JSONL")

    # Deduplicate edges by (source_file, target_concept, relation_kind)
    # Keep most recent extraction per group (by timestamp)
    edge_dedup = {}
    concept_first_seen = {}
    skipped_no_target = 0
    skipped_no_relation = 0

    for entry in entries:
        source_file = entry.get("file", "").replace("\\", "/")
        extraction_ts = entry.get("timestamp", "")
        if not source_file or not extraction_ts:
            continue

        # Track concepts for kg_concepts table
        for c in entry.get("concepts", []):
            name = c.get("name", "").strip()
            kind = c.get("kind", "concept")
            if name and name not in concept_first_seen:
                concept_first_seen[name] = (kind, extraction_ts)

        # Process references → edges
        for ref in entry.get("references", []):
            target = ref.get("target", "").strip()
            relation = ref.get("relation_kind", "").strip()
            if not target:
                skipped_no_target += 1
                continue
            if not relation:
                skipped_no_relation += 1
                continue

            edge_key = (source_file, target, relation)
            existing = edge_dedup.get(edge_key)
            # Keep the most recent extraction for this edge
            if existing is None or extraction_ts > existing["recorded_at"]:
                # Resolve valid_from: source file mtime if accessible, else extraction timestamp
                try:
                    file_abs = Path(source_file)
                    if file_abs.exists():
                        valid_from = datetime.fromtimestamp(file_abs.stat().st_mtime).isoformat()
                    else:
                        valid_from = extraction_ts
                except (OSError, ValueError):
                    valid_from = extraction_ts

                edge_dedup[edge_key] = {
                    "source_concept": source_file,        # document-hub for v0 (A112 deferred)
                    "target_concept": target,
                    "relation_kind": relation,
                    "source_file": source_file,
                    "valid_from": valid_from,
                    "valid_to": None,                     # NULL = source still asserts
                    "recorded_at": extraction_ts,
                    "superseded_by_id": None,             # NULL = current row
                    "confidence": 1.0,
                    "source_ref_id": None,
                }

    print(f"  Deduplicated edges: {len(edge_dedup)} unique (from {sum(len(e.get('references',[])) for e in entries)} raw refs)")
    print(f"  Skipped: {skipped_no_target} no-target, {skipped_no_relation} no-relation")
    print(f"  Unique concept names: {len(concept_first_seen)}")

    # Insert edges
    cur = conn.cursor()
    cur.executemany(
        """INSERT INTO kg_edges
           (source_concept, target_concept, relation_kind, source_file,
            valid_from, valid_to, recorded_at, superseded_by_id,
            confidence, source_ref_id)
           VALUES (:source_concept, :target_concept, :relation_kind, :source_file,
                   :valid_from, :valid_to, :recorded_at, :superseded_by_id,
                   :confidence, :source_ref_id)""",
        edge_dedup.values(),
    )

    # Insert concepts
    cur.executemany(
        """INSERT OR IGNORE INTO kg_concepts (name, kind, first_seen_at)
           VALUES (?, ?, ?)""",
        [(name, kind, ts) for name, (kind, ts) in concept_first_seen.items()],
    )

    conn.commit()

    # Stamp meta
    cur.execute(
        "INSERT OR REPLACE INTO kg_meta (key, value) VALUES (?, ?)",
        ("last_built_at", datetime.now().isoformat()),
    )
    cur.execute(
        "INSERT OR REPLACE INTO kg_meta (key, value) VALUES (?, ?)",
        ("source_record_count", str(len(entries))),
    )
    cur.execute(
        "INSERT OR REPLACE INTO kg_meta (key, value) VALUES (?, ?)",
        ("edge_count", str(len(edge_dedup))),
    )
    cur.execute(
        "INSERT OR REPLACE INTO kg_meta (key, value) VALUES (?, ?)",
        ("concept_count", str(len(concept_first_seen))),
    )
    conn.commit()

    # Summary
    print()
    print(f"[T1.A] Build complete:")
    cur.execute("SELECT COUNT(*) FROM kg_edges")
    print(f"  kg_edges:     {cur.fetchone()[0]:>7} rows")
    cur.execute("SELECT COUNT(*) FROM kg_concepts")
    print(f"  kg_concepts:  {cur.fetchone()[0]:>7} rows")
    cur.execute("SELECT COUNT(*) FROM kg_conflicts")
    print(f"  kg_conflicts: {cur.fetchone()[0]:>7} rows (expected 0 in v0)")
    print()

    # T1.A falsifiability commitment: stale-claim query should return 0 on backfill
    # (no edges have valid_to populated yet)
    cur.execute(
        """SELECT COUNT(*) FROM kg_edges
           WHERE valid_to IS NOT NULL
             AND valid_to < datetime('now')
             AND superseded_by_id IS NULL"""
    )
    stale_count = cur.fetchone()[0]
    print(f"[T1.A] Falsifiability check (stale-claim query):")
    print(f"  stale claims detected: {stale_count} (expected: 0 on v0 backfill)")
    print(f"  -> {'PASS' if stale_count == 0 else 'FAIL'}: schema accepts the query shape; retraction-tracking not yet wired")
    print()

    db_size = DB_PATH.stat().st_size
    print(f"[T1.A] DB size: {db_size:,} bytes ({db_size/1024/1024:.2f} MB)")

    conn.close()


if __name__ == "__main__":
    main()
