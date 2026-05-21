"""Q-B: KG concept-name normalization pass.

Merges known duplicate concept-name variants in the bi-temporal index.
Resolves the measurement artifact where 'A1' + 'Axiom 1' + 'The Coherence
Principle' + 'Coherence Principle' etc. fragment apparent in-degree.

Uses kg_concepts.canonical_name column (already in schema) to point
non-canonical variants at canonical. Edges are not modified; the
canonical_name column is the override consulted at query time.

Conservative: only merges explicitly-declared canonical pairs. Never
infers merges automatically. Run-once; safe to re-run (idempotent).

Usage:
    python operations/scripts/kg_normalize.py --dry-run
    python operations/scripts/kg_normalize.py
"""
import argparse
import sqlite3
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CLAWD = Path(r"C:\Users\mercu\clawd")
DB_PATH = CLAWD / "memory" / "kg_index.db"

# Explicit canonical merges. Format: canonical_name -> [variants]
# Add new pairs here as they surface.
CANONICAL_MERGES = {
    "The Coherence Principle":   ["Coherence Principle"],
    "Project Meridian":          ["Meridian"],
    "Mirror #28":                ["Mirror 28"],
    "Mirror #26":                ["Mirror 26"],
    "Mirror #19":                ["Mirror 19"],
    "Doctrine of Perspectival Idealism": ["The Doctrine", "DoPI"],
    "Axiom 1":                   ["A1"],
    "Axiom 2":                   ["A2"],
    "Axiom 3":                   ["A3"],
    # Cluster IV corollaries
    "Corollary 14":              ["C14"],
    "Corollary 15":              ["C15"],
    "Corollary 16":              ["C16"],
    # Other corollaries that frequently get short-form
    "Corollary 9":               ["C9"],
    # Theorems
    "Theorem 9":                 ["T9"],
    # Bridges meta-tier
    "M14":                       ["Bridge M14", "meta-bridge M14"],
    "M15":                       ["Bridge M15", "meta-bridge M15"],
    # Latent bridges
    "L17":                       ["latent L17", "Bridge L17"],
}


def apply_merges(dry_run: bool = False) -> dict:
    """Apply normalization. Returns stats."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Ensure all canonical names exist in kg_concepts (may not if extractor
    # never saw them as introduced-concepts in their own right)
    inserted_canonical = 0
    for canonical in CANONICAL_MERGES:
        # Check existence
        r = cur.execute("SELECT name FROM kg_concepts WHERE name = ?", (canonical,)).fetchone()
        if r is None and not dry_run:
            cur.execute(
                "INSERT INTO kg_concepts (name, kind, first_seen_at, canonical_name) VALUES (?, ?, datetime('now'), NULL)",
                (canonical, "concept"),
            )
            inserted_canonical += 1

    # Apply merges: set canonical_name on variants
    total_merged = 0
    per_canonical = {}
    for canonical, variants in CANONICAL_MERGES.items():
        n_for_this = 0
        for variant in variants:
            # Check if variant exists at all
            r = cur.execute("SELECT name, canonical_name FROM kg_concepts WHERE name = ?", (variant,)).fetchone()
            if r is None:
                continue
            # r is a tuple: (name, canonical_name)
            if r[1] == canonical:
                continue  # already merged
            if not dry_run:
                cur.execute(
                    "UPDATE kg_concepts SET canonical_name = ? WHERE name = ?",
                    (canonical, variant),
                )
            n_for_this += 1
        if n_for_this > 0:
            per_canonical[canonical] = n_for_this
            total_merged += n_for_this

    if not dry_run:
        conn.commit()

    # Compute post-merge effective in-degree for the merged hubs
    post_effective = {}
    for canonical, variants in CANONICAL_MERGES.items():
        all_names = [canonical] + variants
        placeholders = ",".join("?" * len(all_names))
        r = cur.execute(
            f"SELECT COUNT(*) FROM kg_edges WHERE target_concept IN ({placeholders}) AND superseded_by_id IS NULL",
            all_names,
        ).fetchone()
        post_effective[canonical] = r[0] if r else 0

    conn.close()
    return {
        "inserted_canonical": inserted_canonical,
        "variants_merged": total_merged,
        "per_canonical_merge_count": per_canonical,
        "post_effective_in_degree": post_effective,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print(f"=== KG Concept Normalization Pass ({'DRY-RUN' if args.dry_run else 'APPLYING'}) ===")
    print(f"  Canonical pairs in registry: {len(CANONICAL_MERGES)}")
    print()

    stats = apply_merges(dry_run=args.dry_run)

    print(f"  Canonical names inserted (missing-from-kg_concepts): {stats['inserted_canonical']}")
    print(f"  Variants merged: {stats['variants_merged']}")
    print()
    if stats["per_canonical_merge_count"]:
        print(f"  Per-canonical merges:")
        for canonical, n in sorted(stats["per_canonical_merge_count"].items()):
            print(f"    {canonical:40} <- {n} variant(s)")
    print()
    print(f"=== Post-normalization effective in-degree (canonical + all variants) ===")
    for canonical, in_deg in sorted(stats["post_effective_in_degree"].items(), key=lambda x: -x[1])[:15]:
        print(f"  {in_deg:5}  {canonical}")


if __name__ == "__main__":
    main()
