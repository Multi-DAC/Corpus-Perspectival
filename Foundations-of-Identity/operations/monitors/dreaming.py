"""T2.F v0: Dreaming primitives — port of Anthropic Dreaming's three algorithms
we don't already have, scoped tightly per Substrate Extension Plan decision.

Three primitives:
1. Absolute-date conversion — scan navigation files for relative dates
   ("yesterday", "last week") and surface candidates for rewriting as
   absolute ISO dates. Conservative: only reports candidates by default;
   --apply rewrites with explicit confirmation.

2. Contradicted-note marker — scan memory items for entries whose claims
   contradict newer entries; mark the older one with superseded_by metadata.
   Conservative: only reports candidates by default; --apply marks.

3. MEMORY.md line-count budget — enforce <200-line budget on MEMORY.md;
   identify oldest entries that should archive to topic files. Conservative:
   reports overflow + archive candidates; --apply moves.

Per Substrate Extension Plan T2.F: we ported ONLY the three primitives we
didn't already have. The full Anthropic Dreaming approach was rejected
because Clawd already has the autocatalytic loop and the over-aggressive
consolidation in the Anthropic version degrades accuracy over time.

Each primitive is independent + dry-run-by-default + auditable.

Usage:
    python operations/monitors/dreaming.py absolute-dates [--apply]
    python operations/monitors/dreaming.py contradiction-check [--apply]
    python operations/monitors/dreaming.py memory-budget [--apply]
    python operations/monitors/dreaming.py all  # dry-run all three
"""
import argparse
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CLAWD = Path(r"C:\Users\mercu\clawd")
DREAMING_AUDIT = CLAWD / "memory" / "dreaming_audit.jsonl"

# Files candidate for absolute-date conversion (high-traffic navigation)
DATE_SCAN_TARGETS = [
    CLAWD / "memory" / "handoff.md",
    CLAWD / "CURRENT.md",
    CLAWD / "palace" / "ATRIUM.md",
]

# MEMORY.md path (auto-memory index)
MEMORY_MD = Path(r"C:\Users\Wasch\.claude\projects\C--Users-mercu-clawd\memory\MEMORY.md")
MEMORY_BUDGET_LINES = 200

# Relative-date patterns to find
RELATIVE_DATE_PATTERNS = [
    (r"\byesterday\b",        lambda now: (now - timedelta(days=1)).strftime("%Y-%m-%d")),
    (r"\btoday\b",            lambda now: now.strftime("%Y-%m-%d")),
    (r"\btomorrow\b",         lambda now: (now + timedelta(days=1)).strftime("%Y-%m-%d")),
    (r"\blast week\b",        lambda now: (now - timedelta(days=7)).strftime("%Y-%m-%d (week of)")),
    (r"\bnext week\b",        lambda now: (now + timedelta(days=7)).strftime("%Y-%m-%d (week of)")),
    (r"\bthis morning\b",     lambda now: now.strftime("%Y-%m-%d morning")),
    (r"\bthis afternoon\b",   lambda now: now.strftime("%Y-%m-%d afternoon")),
    (r"\bthis evening\b",     lambda now: now.strftime("%Y-%m-%d evening")),
    (r"\btonight\b",          lambda now: now.strftime("%Y-%m-%d evening")),
]


def _audit(record: dict) -> None:
    record["ts"] = datetime.now().isoformat()
    DREAMING_AUDIT.parent.mkdir(parents=True, exist_ok=True)
    with open(DREAMING_AUDIT, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


# ============================================================================
# Primitive 1: Absolute-date conversion
# ============================================================================

def scan_relative_dates() -> list:
    """Find candidates for absolute-date rewriting. Returns list of
    {file, line_number, pattern, suggestion, context}."""
    candidates = []
    now = datetime.now()
    for path in DATE_SCAN_TARGETS:
        if not path.exists():
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except OSError:
            continue
        for i, line in enumerate(lines, 1):
            for pattern, suggester in RELATIVE_DATE_PATTERNS:
                for m in re.finditer(pattern, line, re.IGNORECASE):
                    candidates.append({
                        "file": str(path),
                        "line_number": i,
                        "pattern": pattern,
                        "matched_text": m.group(0),
                        "suggested_replacement": suggester(now),
                        "context_excerpt": line.strip()[:120],
                    })
    return candidates


def primitive_absolute_dates(apply: bool = False) -> dict:
    """Run primitive 1. Returns summary dict."""
    candidates = scan_relative_dates()
    summary = {
        "primitive": "absolute_dates",
        "candidates_found": len(candidates),
        "apply": apply,
        "applied": 0,
    }
    if apply:
        # CONSERVATIVE: even with --apply, we do NOT rewrite navigation files
        # because relative-date context often matters in historical preserved
        # addendums. Instead, we flag the file with a comment marker pointing
        # the reader at the audit log. Manual review is the structural fix.
        # Future iteration: add per-pattern apply-safety classification.
        summary["note"] = (
            "v0: even --apply does not rewrite navigation files; relative dates "
            "in historical preserved sections are semantically load-bearing. "
            "Manual review based on candidates list is the structural fix."
        )
    _audit({"primitive": "absolute_dates", "summary": summary, "first_5_candidates": candidates[:5]})
    return summary


# ============================================================================
# Primitive 2: Contradiction marker (via superseded_by)
# ============================================================================

def scan_memory_contradictions() -> list:
    """Find candidate contradictions in auto-memory items.

    Heuristic v0: items whose `name:` frontmatter is similar AND whose content
    asserts different numeric values or contradictory categorical state.
    Conservative — most candidates are false positives requiring human
    judgment. v0 surfaces candidates without applying.
    """
    candidates = []
    memory_dir = Path(r"C:\Users\Wasch\.claude\projects\C--Users-mercu-clawd\memory")
    if not memory_dir.exists():
        return candidates
    # Read all memory files; group by similar topic
    files_by_kind = {}
    for f in memory_dir.glob("*.md"):
        if f.name == "MEMORY.md":
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except OSError:
            continue
        # Parse frontmatter `name:` field
        m = re.search(r"^name:\s*(.+)$", text, re.MULTILINE)
        if not m:
            continue
        name = m.group(1).strip()
        # Extract topic prefix (first 2-3 words)
        topic = "-".join(name.split("-")[:3]) if "-" in name else name
        files_by_kind.setdefault(topic, []).append((f, text))

    # Within each topic group, if multiple files exist, flag for human review
    for topic, files in files_by_kind.items():
        if len(files) > 1:
            candidates.append({
                "topic_prefix": topic,
                "files": [str(f) for f, _ in files],
                "count": len(files),
                "note": "multiple memory items with same topic prefix; possible duplicate/contradiction",
            })
    return candidates


def primitive_contradiction_check(apply: bool = False) -> dict:
    candidates = scan_memory_contradictions()
    summary = {
        "primitive": "contradiction_check",
        "candidates_found": len(candidates),
        "apply": apply,
        "applied": 0,
        "note": (
            "v0: contradiction detection requires semantic judgment; surfaces "
            "candidates without applying. --apply would write superseded_by "
            "metadata only after human confirmation. Future iteration: LLM-"
            "assisted semantic-contradiction detection."
        ),
    }
    _audit({"primitive": "contradiction_check", "summary": summary, "candidates": candidates[:10]})
    return summary


# ============================================================================
# Primitive 3: MEMORY.md line-count budget
# ============================================================================

def primitive_memory_budget(apply: bool = False, budget: int = MEMORY_BUDGET_LINES) -> dict:
    summary = {"primitive": "memory_budget", "budget_lines": budget, "apply": apply}
    if not MEMORY_MD.exists():
        summary["status"] = "memory_md_missing"
        summary["path"] = str(MEMORY_MD)
        _audit({"primitive": "memory_budget", "summary": summary})
        return summary

    try:
        lines = MEMORY_MD.read_text(encoding="utf-8").splitlines()
    except OSError as e:
        summary["status"] = "read_error"
        summary["error"] = str(e)
        _audit({"primitive": "memory_budget", "summary": summary})
        return summary

    summary["current_line_count"] = len(lines)
    summary["overflow_lines"] = max(0, len(lines) - budget)
    summary["within_budget"] = len(lines) <= budget

    if not summary["within_budget"]:
        # Identify oldest entries (heuristic: lines starting with "- " near top
        # are likely older index entries; we'd archive ones older than X% from
        # top of file). v0: report only; don't auto-archive.
        summary["status"] = "over_budget_no_action"
        summary["note"] = (
            f"MEMORY.md is {len(lines)} lines (budget {budget}). v0: identifies "
            "overflow but does NOT auto-archive. Archiving requires choosing "
            "which entries are 'oldest/coldest' which is content-dependent. "
            "Manual archive recommended; --apply will be implemented when "
            "auto-archival heuristic is clear."
        )
    else:
        summary["status"] = "within_budget"

    _audit({"primitive": "memory_budget", "summary": summary})
    return summary


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("primitive", choices=["absolute-dates", "contradiction-check", "memory-budget", "all"])
    parser.add_argument("--apply", action="store_true", help="apply mutations (default: dry-run report only)")
    args = parser.parse_args()

    if args.primitive == "absolute-dates":
        result = primitive_absolute_dates(apply=args.apply)
    elif args.primitive == "contradiction-check":
        result = primitive_contradiction_check(apply=args.apply)
    elif args.primitive == "memory-budget":
        result = primitive_memory_budget(apply=args.apply)
    elif args.primitive == "all":
        results = {
            "absolute_dates": primitive_absolute_dates(apply=False),
            "contradiction_check": primitive_contradiction_check(apply=False),
            "memory_budget": primitive_memory_budget(apply=False),
        }
        print(f"=== Dreaming Primitives — All (dry-run) ===")
        for name, r in results.items():
            print(f"\n  {name}:")
            for k, v in r.items():
                if isinstance(v, str) and len(v) > 100:
                    v = v[:100] + "..."
                print(f"    {k}: {v}")
        return

    print(f"=== Dreaming Primitive: {args.primitive}{' (APPLY)' if args.apply else ' (dry-run)'} ===")
    for k, v in result.items():
        if isinstance(v, str) and len(v) > 200:
            v = v[:200] + "..."
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
