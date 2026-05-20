# Memento Bi-Temporal Pattern — Notes for T1.A Schema Design

**Source:** `github.com/shane-farkas/memento-memory` (SQLite-backed, Python). Schema at `src/memento/schema.py`; write/query logic at `src/memento/graph_store.py`; post-hoc hygiene at `src/memento/consolidation.py`.
**Filed:** 2026-05-20 Day 110 Wednesday morning, during T1.A schema design session.
**Purpose:** Ground T1.A's schema choices in actual Memento design rather than naive bi-temporal pattern.

## Key findings

### 1. Asymmetric temporality is intentional

Memento splits temporality across two tables rather than putting all 4 columns on every edge:

- **`relationships`** (edges): world-time interval only — `valid_from TEXT NOT NULL`, `valid_to TEXT` (nullable for open-ended). No system-time on the edge itself.
- **`properties`** and **`relationship_properties`** (attributes): single world-time point `as_of TEXT NOT NULL`, system-time point `recorded_at TEXT NOT NULL`, and a pointer-based supersession chain `superseded_by_id TEXT REFERENCES <same table>(id)`.

The question to ask: are we modeling **"facts that have a truth-interval in the world"** (use `valid_from`/`valid_to`) or **"claims the system extracted at some time, possibly with later retraction in source"** (use `recorded_at` + `superseded_by_id`)?

For our Mirror #28 stale-claim use case: **the second**. Our edges are extracted claims, not world-facts with intrinsic intervals. The supersession pointer is the right primitive.

### 2. Supersession via pointer, not timestamp

`superseded_by_id` (foreign key to same table's id) beats `system_superseded TEXT` (timestamp) for retraction-detection queries:

```sql
-- Memento's "find current" pattern
WHERE superseded_by_id IS NULL

-- Combined with source-retraction:
WHERE source_says_retracted = true
  AND superseded_by_id IS NULL
```

Index scan, not range comparison. Cleaner.

### 3. Mark-and-insert, not update-in-place

Pattern:
1. INSERT new row with new id
2. UPDATE old_row SET superseded_by_id = new_id

Old rows persist verbatim — full audit trail. README: *"facts are never deleted, only superseded."* This matches our records-authoritative discipline (Zhang convergence + Drift #214 + "records are authoritative; draft is translation").

**Warning:** wrap in explicit transaction. Memento's snippet doesn't show `BEGIN`; verify if borrowing the pattern. Without transaction, can land in state with two "current" rows.

### 4. Both temporal axes always populated; nullability reserved for open-end

`recorded_at = _now()` always. `as_of = as_of or now` — defaults to NOW if caller didn't supply. **NULL is reserved for the open end** (`valid_to`, `superseded_by_id`). Never NULL on the "from" side.

### 5. Indexing — minimal, lazy on temporal columns

Memento creates:
- `idx_properties_entity_key ON properties(entity_id, key)` — composite for attribute lookup
- `idx_properties_superseded ON properties(superseded_by_id)` — for "find current"
- `idx_rel_source`, `idx_rel_target`, `idx_rel_type` — single-column edge indices
- `idx_rel_props_rel_key ON relationship_properties(relationship_id, key)`

**Notably absent:** no indices on `as_of`, `recorded_at`, `valid_from`, `valid_to`. Point-in-time queries do a scan filtered by composite, then `ORDER BY recorded_at DESC LIMIT 1`. **Fine for small-scale; add `(entity_id, key, recorded_at)` composite if heavy as-of traffic.**

### 6. Conflicts as separate table, not flag on edges

Memento has a `conflicts` table separate from `relationships`. Keeps edge table clean; makes "unresolved contradictions" a single query. Worth copying for our design.

Note: contradiction *detection* is assumed upstream. `consolidation.py` only *resolves* pre-existing rows in `conflicts`. We'd need our own detection logic.

### 7. Provenance is first-class

Every versioned row has:
- `confidence REAL NOT NULL DEFAULT 1.0`
- `source_ref_id` foreign key to source

Worth adopting — claim-provenance was the T1.B falsifiability target anyway.

### 8. Latent design debt to avoid: as-of asymmetry

Memento stores `as_of` (world-time) but **never wrote the world-time as-of query**. Only system-time as-of is implemented (`point_in_time_snapshot()`). **Lesson:** if we commit to bi-temporal, write both as-of shapes from day one — or pick one and don't waste storage on the other.

### 9. ISO-8601 TEXT timestamps

All Memento timestamps are `TEXT` (ISO-8601). SQLite-native. Sortable as strings. No epoch-int conversion. Adopt as-is.

### 10. `valid_to` open-ended via NULL, no sentinel date

No `9999-12-31`. Cleaner schema. Every as-of query needs `(valid_to IS NULL OR valid_to > ?)`. Acceptable tradeoff.

## What this changes vs. our naive 4-column plan

- **Drop** `system_superseded TEXT` (our original column 4)
- **Add** `superseded_by_id INTEGER REFERENCES kg_edges(id)`
- **Rename** `system_created` → `recorded_at` (Memento naming convention)
- **Keep** `valid_from`, `valid_until` (Memento naming uses `valid_to`, we'll align)
- **Add** `confidence REAL NOT NULL DEFAULT 1.0`
- **Add** `source_ref_id` foreign key
- **Add** separate `kg_conflicts` table (Memento pattern)
- **Commit** to writing BOTH as-of queries (system-time AND world-time) from day one

## Files of record (for future reference)

- `src/memento/schema.py` — table definitions
- `src/memento/graph_store.py` — write/query logic, `point_in_time_snapshot()`
- `src/memento/consolidation.py` — post-hoc hygiene (decay/merge/prune)

---

**Filed-by:** Clawd (with research-agent help reading the Memento repo), 2026-05-20 Day 110 morning.
**Next:** consume this in the T1.A schema design proposal (Clayton paired session, immediately following).