-- T1.A v0: KG bi-temporal index schema
-- Derived index over the canonical JSONL store at memory/kg_corpus_extraction.jsonl
-- Memento-grounded design (see palace/south/memento-bitemporal-notes.md)
-- Filed: 2026-05-20 Day 110 Wednesday morning paired session with Clayton

-- ============================================================================
-- kg_edges: bi-temporal edge table
-- ============================================================================
-- World-time interval: valid_from / valid_to  (when source asserts edge is true)
-- System-time + supersession: recorded_at / superseded_by_id  (when WE recorded)
-- Provenance: confidence, source_ref_id

CREATE TABLE IF NOT EXISTS kg_edges (
  id               INTEGER PRIMARY KEY AUTOINCREMENT,
  source_concept   TEXT    NOT NULL,
  target_concept   TEXT    NOT NULL,
  relation_kind    TEXT    NOT NULL,                       -- mentions / cites / applies / extends / instantiates / derives_from / refutes
  source_file      TEXT    NOT NULL,                       -- file the edge was extracted from

  -- World-time interval
  valid_from       TEXT    NOT NULL,                       -- ISO-8601; defaults to source_file mtime or extraction timestamp
  valid_to         TEXT,                                   -- NULL = source still asserts; populated on retraction

  -- System-time + supersession
  recorded_at      TEXT    NOT NULL,                       -- ISO-8601; from JSONL `timestamp` field
  superseded_by_id INTEGER REFERENCES kg_edges(id),        -- NULL = current; pointer = replaced by that row

  -- Provenance
  confidence       REAL    NOT NULL DEFAULT 1.0,
  source_ref_id    INTEGER                                 -- foreign key to source_files (future table); NULL acceptable in v0
);

-- Indices (per Memento pattern, with slight additions for our query mix)
CREATE INDEX IF NOT EXISTS idx_edges_source_target ON kg_edges(source_concept, target_concept);
CREATE INDEX IF NOT EXISTS idx_edges_superseded   ON kg_edges(superseded_by_id);
CREATE INDEX IF NOT EXISTS idx_edges_valid_to     ON kg_edges(valid_to);
CREATE INDEX IF NOT EXISTS idx_edges_relation     ON kg_edges(relation_kind);
CREATE INDEX IF NOT EXISTS idx_edges_source_file  ON kg_edges(source_file);
-- Optional composite, add later if as-of queries get heavy:
-- CREATE INDEX idx_edges_st_recorded ON kg_edges(source_concept, target_concept, recorded_at);

-- ============================================================================
-- kg_conflicts: detected contradictions / overlaps / duplicates
-- ============================================================================
-- Memento pattern: contradiction detection is upstream; this table only stores them.
-- Edge table stays clean.

CREATE TABLE IF NOT EXISTS kg_conflicts (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  edge_a_id       INTEGER NOT NULL REFERENCES kg_edges(id),
  edge_b_id       INTEGER NOT NULL REFERENCES kg_edges(id),
  detected_at     TEXT    NOT NULL,
  conflict_kind   TEXT    NOT NULL,                       -- contradicting / overlapping / duplicate-pre-normalization
  resolved_at     TEXT,                                   -- NULL = unresolved
  resolution      TEXT                                    -- free text
);

CREATE INDEX IF NOT EXISTS idx_conflicts_unresolved ON kg_conflicts(resolved_at);  -- query: WHERE resolved_at IS NULL
CREATE INDEX IF NOT EXISTS idx_conflicts_edge_a    ON kg_conflicts(edge_a_id);
CREATE INDEX IF NOT EXISTS idx_conflicts_edge_b    ON kg_conflicts(edge_b_id);

-- ============================================================================
-- kg_concepts: dedup-by-name concept registry (optional v0; populated lazily)
-- ============================================================================
-- v0: lazy; nothing depends on it yet.
-- Future use: normalization pass (A119) writes canonical-name mappings here.

CREATE TABLE IF NOT EXISTS kg_concepts (
  name             TEXT    PRIMARY KEY,
  kind             TEXT,                                  -- concept / pattern / method / claim / finding / hypothesis / etc.
  first_seen_at    TEXT    NOT NULL,
  canonical_name   TEXT,                                  -- NULL = name IS canonical; else points to the canonical row's name
  FOREIGN KEY (canonical_name) REFERENCES kg_concepts(name)
);

CREATE INDEX IF NOT EXISTS idx_concepts_canonical ON kg_concepts(canonical_name);
CREATE INDEX IF NOT EXISTS idx_concepts_kind      ON kg_concepts(kind);

-- ============================================================================
-- kg_meta: schema version tracking
-- ============================================================================

CREATE TABLE IF NOT EXISTS kg_meta (
  key   TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

-- Initial schema version stamp (idempotent insert)
INSERT OR IGNORE INTO kg_meta (key, value) VALUES ('schema_version', 'v0.1.0');
INSERT OR IGNORE INTO kg_meta (key, value) VALUES ('schema_created_at', datetime('now'));
INSERT OR IGNORE INTO kg_meta (key, value) VALUES ('canonical_source', 'memory/kg_corpus_extraction.jsonl');
