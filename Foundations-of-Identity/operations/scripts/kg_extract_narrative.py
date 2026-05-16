"""LLM-based narrative KG extraction.

Calls the daemon's ModelRouter with prompts that extract:
- Concepts mentioned (with first definition / role)
- Cross-references to existing KG entities
- Empirical claims / hypotheses
- New bridge candidates

Outputs structured JSON, parsed, fed to add_entity_raw / add_edge_raw.

Heavy. Each call ~30s via Claude Code subprocess. Use --limit N to bound.

Usage:
    python kg_extract_narrative.py --limit 3   # smoke test
    python kg_extract_narrative.py --limit 20  # sample pass
    python kg_extract_narrative.py             # full pass (long-running)
"""
import argparse
import asyncio
import io
import json
import os
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
os.environ.setdefault("CLAWD_HOME", r"C:\Users\mercu\clawd")
os.environ.setdefault("CLAWD_DAEMON", r"C:\Users\mercu\clawd-daemon")
sys.path.insert(0, r"C:\Users\mercu\clawd-daemon")

CLAWD = Path(os.environ["CLAWD_HOME"])
LOG_PATH = CLAWD / "memory" / "kg_narrative_extraction.jsonl"


EXTRACTION_PROMPT = """You are extracting structural knowledge from a Drift essay. Return ONLY a JSON object.

The essay (slug: {slug}):
---
{body}
---

Extract:
1. Up to 8 named "concepts" — terms or phrases the essay introduces, defines, or treats as load-bearing. For each: name (1-6 words, canonical capitalization), kind ("concept"/"pattern"/"method"/"experience"/"claim"), one-sentence_role.
2. Up to 6 "references" to existing things by name — Library volumes, people, axioms (A1/A2/A3), corollaries (C9/C14/C15/C16), bridges (M1-M14, L1-L16, LC15-17), Mirror entries (#19, #28, etc.), other Drift essays. For each: target (verbatim name as referenced), relation_kind ("cites"/"applies"/"extends"/"refutes"/"instantiates").

Return JSON exactly like:
{{"concepts":[{{"name":"X","kind":"concept","role":"..."}}], "references":[{{"target":"...","relation_kind":"cites"}}]}}

No prose. JSON only."""


async def extract_one(router, essay_path: Path) -> dict:
    slug = essay_path.stem
    body = essay_path.read_text(encoding="utf-8", errors="replace")
    # Truncate to keep prompt manageable
    if len(body) > 6000:
        body = body[:6000] + "\n\n[...truncated]"
    prompt = EXTRACTION_PROMPT.format(slug=slug, body=body)
    try:
        response = await router.send_oneshot(prompt)
        text = response.text if hasattr(response, "text") else str(response)
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}", "slug": slug}

    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        return {"error": "no JSON in response", "slug": slug, "raw": text[:200]}
    try:
        parsed = json.loads(m.group())
    except json.JSONDecodeError as e:
        return {"error": f"JSON parse: {e}", "slug": slug, "raw": text[:200]}
    parsed["slug"] = slug
    return parsed


def apply_to_kg(kg, extraction: dict) -> tuple[int, int]:
    """Add extracted concepts + references to KG. Returns (entities_added, edges_added)."""
    if extraction.get("error"):
        return 0, 0
    slug = extraction.get("slug", "?")
    essay_ent = f"Drift: {slug.replace('-', ' ').title()}"
    ne, ed = 0, 0
    for c in extraction.get("concepts", [])[:8]:
        name = c.get("name", "").strip()
        if not name or len(name) > 80:
            continue
        kg.add_entity_raw(name, c.get("kind", "concept"), {
            "role": c.get("role", "")[:200],
            "source_essay": slug,
        })
        kg.add_edge_raw(essay_ent, name, "introduces")
        ne += 1
        ed += 1
    for r in extraction.get("references", [])[:6]:
        target = r.get("target", "").strip()
        if not target:
            continue
        kg.add_edge_raw(essay_ent, target, r.get("relation_kind", "cites"))
        ed += 1
    return ne, ed


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=3, help="Number of essays to process")
    parser.add_argument("--essays-dir", default=None)
    args = parser.parse_args()

    from models import ModelRouter
    from tools import knowledge_graph as kg
    router = ModelRouter()

    essays_dir = Path(args.essays_dir) if args.essays_dir else (
        CLAWD / "repo-staging" / "Corpus-Perspectival" / "Foundations-of-Identity" / "personal-works" / "drift" / "essays"
    )
    essays = sorted(essays_dir.glob("*.md"))[-args.limit:]  # Most recent N
    print(f"# LLM KG extraction over {len(essays)} essays ({args.limit} limit)")

    total_ne, total_ed = 0, 0
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as logf:
        for i, p in enumerate(essays, 1):
            print(f"\n[{i}/{len(essays)}] {p.stem}")
            extraction = await extract_one(router, p)
            logf.write(json.dumps(extraction, default=str) + "\n")
            logf.flush()
            if "error" in extraction:
                print(f"  ✗ {extraction['error']}")
                continue
            ne, ed = apply_to_kg(kg, extraction)
            total_ne += ne
            total_ed += ed
            print(f"  + {ne} concepts, {ed} edges")

    print(f"\nDone: {total_ne} entities + {total_ed} edges from {len(essays)} essays")
    print(f"Log: {LOG_PATH}")


if __name__ == "__main__":
    asyncio.run(main())
