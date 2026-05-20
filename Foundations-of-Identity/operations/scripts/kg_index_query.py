"""T1.A v0: Query utilities for the bi-temporal KG index.

Both as-of query shapes implemented from day one per Memento's design-debt
lesson (Memento stored as_of but never wrote the world-time as-of query;
we commit to both).

Usage as module:
    from operations.scripts.kg_index_query import (
        connect, find_current, find_stale_claims,
        system_as_of, world_as_of, hub_degree, find_by_relation,
    )
    conn = connect()
    for row in find_stale_claims(conn): ...

Usage as CLI:
    python operations/scripts/kg_index_query.py stats
    python operations/scripts/kg_index_query.py stale
    python operations/scripts/kg_index_query.py hubs --limit 20
    python operations/scripts/kg_index_query.py system-as-of 2026-05-15T00:00:00
    python operations/scripts/kg_index_query.py world-as-of  2026-05-15T00:00:00
    python operations/scripts/kg_index_query.py relation cites --limit 10
"""
import argparse
import sqlite3
import sys
from pathlib import Path

# Windows console defaults to CP1252; force UTF-8 for stdout/stderr so
# concept names with non-ASCII characters (Λ, ∞, ⊕, etc.) print cleanly.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

CLAWD = Path(r"C:\Users\mercu\clawd")
DB_PATH = CLAWD / "memory" / "kg_index.db"


def connect():
    """Open a read-only connection to the index."""
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================================
# Core temporal queries
# ============================================================================

def find_current(conn):
    """Edges the system currently believes (not superseded)."""
    cur = conn.cursor()
    return cur.execute(
        "SELECT * FROM kg_edges WHERE superseded_by_id IS NULL"
    ).fetchall()


def find_stale_claims(conn):
    """T1.A falsifiability commitment query.

    Source says edge is retracted (valid_to in the past), but our system
    never marked it superseded. Mirror #28 stale-claim detection target.
    Returns [] on a fresh backfill because retraction-tracking is not wired
    in v0 - all valid_to values are NULL.
    """
    cur = conn.cursor()
    return cur.execute(
        """SELECT * FROM kg_edges
           WHERE valid_to IS NOT NULL
             AND valid_to < datetime('now')
             AND superseded_by_id IS NULL"""
    ).fetchall()


def system_as_of(conn, timestamp_iso):
    """System-time-as-of: what did Clawd believe at timestamp T?

    Returns edges that were recorded by T, and were either still current at T
    (no supersession yet) or whose supersession happened after T.
    """
    cur = conn.cursor()
    return cur.execute(
        """SELECT e.* FROM kg_edges e
           WHERE e.recorded_at <= ?
             AND (
               e.superseded_by_id IS NULL
               OR EXISTS (
                 SELECT 1 FROM kg_edges e2
                 WHERE e2.id = e.superseded_by_id
                   AND e2.recorded_at > ?
               )
             )""",
        (timestamp_iso, timestamp_iso),
    ).fetchall()


def world_as_of(conn, timestamp_iso):
    """World-time-as-of: what was the SOURCE asserting at timestamp T?

    Returns edges whose world-time interval (valid_from, valid_to) covers T.
    Open-ended NULL valid_to is treated as 'still valid'.
    """
    cur = conn.cursor()
    return cur.execute(
        """SELECT * FROM kg_edges
           WHERE valid_from <= ?
             AND (valid_to IS NULL OR valid_to > ?)""",
        (timestamp_iso, timestamp_iso),
    ).fetchall()


# ============================================================================
# Aggregate / exploratory queries
# ============================================================================

def hub_degree(conn, limit=25):
    """In-degree per target concept across CURRENT edges."""
    cur = conn.cursor()
    return cur.execute(
        """SELECT target_concept, COUNT(*) as in_degree
           FROM kg_edges
           WHERE superseded_by_id IS NULL
           GROUP BY target_concept
           ORDER BY in_degree DESC
           LIMIT ?""",
        (limit,),
    ).fetchall()


def find_by_relation(conn, relation_kind, limit=25):
    """All current edges of a given relation kind."""
    cur = conn.cursor()
    return cur.execute(
        """SELECT * FROM kg_edges
           WHERE relation_kind = ? AND superseded_by_id IS NULL
           LIMIT ?""",
        (relation_kind, limit),
    ).fetchall()


def stats(conn):
    """Aggregate stats for sanity-check."""
    cur = conn.cursor()
    out = {}
    out["edges_total"]    = cur.execute("SELECT COUNT(*) FROM kg_edges").fetchone()[0]
    out["edges_current"]  = cur.execute("SELECT COUNT(*) FROM kg_edges WHERE superseded_by_id IS NULL").fetchone()[0]
    out["concepts_total"] = cur.execute("SELECT COUNT(*) FROM kg_concepts").fetchone()[0]
    out["conflicts_total"]= cur.execute("SELECT COUNT(*) FROM kg_conflicts").fetchone()[0]
    out["conflicts_unresolved"] = cur.execute("SELECT COUNT(*) FROM kg_conflicts WHERE resolved_at IS NULL").fetchone()[0]
    out["stale_claims"]   = cur.execute(
        """SELECT COUNT(*) FROM kg_edges
           WHERE valid_to IS NOT NULL
             AND valid_to < datetime('now')
             AND superseded_by_id IS NULL"""
    ).fetchone()[0]
    out["distinct_relations"] = [
        (r["relation_kind"], r["c"])
        for r in cur.execute(
            "SELECT relation_kind, COUNT(*) as c FROM kg_edges WHERE superseded_by_id IS NULL GROUP BY relation_kind ORDER BY c DESC"
        )
    ]
    return out


# ============================================================================
# CLI
# ============================================================================

def _row_brief(row):
    """Compact one-line edge representation."""
    src = row["source_file"].split("/")[-1] if row["source_file"] else "?"
    return f"  [{row['id']:>5}] {src} --{row['relation_kind']}--> {row['target_concept']}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["stats", "stale", "hubs", "system-as-of", "world-as-of", "relation"])
    parser.add_argument("args", nargs="*")
    parser.add_argument("--limit", type=int, default=25)
    ns = parser.parse_args()

    conn = connect()

    if ns.command == "stats":
        s = stats(conn)
        print(f"=== KG Index Stats ===")
        print(f"  edges_total:         {s['edges_total']}")
        print(f"  edges_current:       {s['edges_current']}")
        print(f"  concepts_total:      {s['concepts_total']}")
        print(f"  conflicts_total:     {s['conflicts_total']}")
        print(f"  conflicts_unresolved:{s['conflicts_unresolved']}")
        print(f"  stale_claims:        {s['stale_claims']}  (T1.A falsifiability target)")
        print(f"  distinct_relations:")
        for kind, n in s["distinct_relations"]:
            print(f"    {kind:>15}  {n}")

    elif ns.command == "stale":
        rows = find_stale_claims(conn)
        print(f"=== Stale claims (T1.A query) ===")
        print(f"  Count: {len(rows)}")
        for r in rows[:ns.limit]:
            print(_row_brief(r))

    elif ns.command == "hubs":
        rows = hub_degree(conn, ns.limit)
        print(f"=== Top {ns.limit} hubs (in-degree) ===")
        for r in rows:
            print(f"  {r['in_degree']:>5}  {r['target_concept']}")

    elif ns.command == "system-as-of":
        if not ns.args:
            print("usage: system-as-of <ISO-8601 timestamp>")
            return
        rows = system_as_of(conn, ns.args[0])
        print(f"=== System-as-of {ns.args[0]}: {len(rows)} edges ===")
        for r in rows[:ns.limit]:
            print(_row_brief(r))

    elif ns.command == "world-as-of":
        if not ns.args:
            print("usage: world-as-of <ISO-8601 timestamp>")
            return
        rows = world_as_of(conn, ns.args[0])
        print(f"=== World-as-of {ns.args[0]}: {len(rows)} edges ===")
        for r in rows[:ns.limit]:
            print(_row_brief(r))

    elif ns.command == "relation":
        if not ns.args:
            print("usage: relation <relation_kind>")
            return
        rows = find_by_relation(conn, ns.args[0], ns.limit)
        print(f"=== Relation '{ns.args[0]}': {len(rows)} edges ===")
        for r in rows:
            print(_row_brief(r))

    conn.close()


if __name__ == "__main__":
    main()
