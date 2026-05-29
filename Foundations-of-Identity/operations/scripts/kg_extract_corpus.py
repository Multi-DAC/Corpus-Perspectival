"""Corpus-wide LLM-based KG narrative extraction.

Walks every text surface — Drift essays, Library prose, Technical-Work,
Research, sources, memory, infrastructure — and extracts concepts +
cross-references via the daemon's ModelRouter (Claude Code subprocess).

Resume-capable: skips files already in memory/kg_corpus_extraction.jsonl.
Heavy: ~30s/file via subprocess. Run in background; check progress with
  tail -f memory/kg_corpus_extraction.jsonl

Usage:
    python kg_extract_corpus.py                # full pass
    python kg_extract_corpus.py --limit 50     # bounded
    python kg_extract_corpus.py --sources drift,library    # specific sets
"""
import argparse
import asyncio
import io
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
os.environ.setdefault("CLAWD_HOME", r"C:\Users\mercu\clawd")
os.environ.setdefault("CLAWD_DAEMON", r"C:\Users\mercu\clawd-daemon")
sys.path.insert(0, r"C:\Users\mercu\clawd-daemon")

CLAWD = Path(os.environ["CLAWD_HOME"])
STAGING = CLAWD / "repo-staging" / "Corpus-Perspectival"
FOI = STAGING / "Foundations-of-Identity"
LOG_PATH = CLAWD / "memory" / "kg_corpus_extraction.jsonl"
PROGRESS_PATH = CLAWD / "memory" / "kg_corpus_progress.json"


SOURCE_SETS = {
    "drift": [FOI / "personal-works" / "drift" / "essays"],
    "library": [
        STAGING / "Library" / "The-Coherence-Principle",
        STAGING / "Library" / "Coherent-Structure",
        STAGING / "Library" / "Universal-Coherence",
        STAGING / "Library" / "Meridian",
        STAGING / "Library" / "The-Killing-Form",
        STAGING / "Library" / "The-Living-Architecture",
        STAGING / "Library" / "The-Coherent-Body",
        STAGING / "Library" / "The-Coherent-Mind",
        STAGING / "Library" / "Dynamic-Organization",
        STAGING / "Library" / "The-Continuity",
        STAGING / "Library" / "Corpus-Perspectival",
        STAGING / "Library" / "Master-Glossary",
        STAGING / "Library" / "Atlas",
    ],
    "technical": [STAGING / "Technical-Work"],
    "research": [STAGING / "Research"],
    "sources": [STAGING / "Research" / "sources"],
    "memory": [CLAWD / "memory"],
    "infrastructure": [
        CLAWD / "operations",
        CLAWD / "palace",
        CLAWD / "identity",
    ],
    "unreleased": [STAGING / "Unreleased-Work"],
}

EXTRACTION_PROMPT = """Extract structural knowledge from this text. Return ONLY a JSON object.

File: {file}
Type: {kind}

Body:
---
{body}
---

Extract:
1. Up to 8 named "concepts" — terms or phrases this text introduces, defines, or treats as load-bearing. For each: name (1-6 words, canonical capitalization), kind ("concept"/"pattern"/"method"/"finding"/"hypothesis"/"claim"), one-sentence_role.
2. Up to 6 "references" to existing things — Library volumes, people, axioms (A1/A2/A3), corollaries (C9/C14/C15/C16), theorems, bridges (M1-M14, L1-L16, LC15-LC17), Mirror entries (#19, #28, etc.), other Drift essays, papers, dates. For each: target (verbatim name as referenced), relation_kind ("cites"/"applies"/"extends"/"refutes"/"instantiates"/"derives_from"/"mentions").

Return JSON exactly like:
{{"concepts":[{{"name":"X","kind":"concept","role":"..."}}], "references":[{{"target":"...","relation_kind":"cites"}}]}}

No prose. JSON only."""


def classify_file(path: Path) -> str:
    """Classify file kind for entity-typing."""
    parts = path.parts
    if "drift" in parts and "essays" in parts:
        return "drift_essay"
    if "Library" in parts:
        return "library_section"
    if "Technical-Work" in parts:
        return "technical_doc"
    if "Research" in parts and "sources" in parts:
        return "source_register"
    if "Research" in parts:
        return "research_doc"
    if "memory" in parts and re.match(r"\d{4}-\d{2}-\d{2}", path.stem):
        return "daily_log"
    if "memory" in parts:
        return "memory_doc"
    if "palace" in parts:
        return "palace_doc"
    if "identity" in parts:
        return "identity_doc"
    if "operations" in parts:
        return "operations_doc"
    return "doc"


def file_signature(path: Path) -> str:
    """Stable identifier for resume."""
    try:
        return str(path.resolve()).replace("\\", "/")
    except Exception:
        return str(path)


def load_processed(skip_errors: bool = False) -> set[str]:
    """Return set of file_sigs already processed.

    If skip_errors=True, records carrying an 'error' field are NOT counted as
    processed (they'll be retried). Use this after a capacity-limited run
    where many entries are 'no_json' / 'You've hit your limit' failures.
    """
    if not LOG_PATH.exists():
        return set()
    seen = set()
    for line in LOG_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            rec = json.loads(line)
            if skip_errors and rec.get("error"):
                continue
            sig = rec.get("file_sig") or rec.get("file") or rec.get("slug")
            if sig:
                seen.add(sig)
        except Exception:
            continue
    return seen


EXCLUDED_PATH_PARTS = {
    "venv", ".venv", "env", ".env",
    "__pycache__", ".git", ".mypy_cache", ".pytest_cache",
    "node_modules", "site-packages",
    "build", "dist", ".tox", ".eggs",
}
EXCLUDED_DIR_SUFFIXES = (".dist-info", ".egg-info")


def _is_excluded(path: Path) -> bool:
    """True if any path component is a venv/cache/build-artifact directory."""
    for part in path.parts:
        if part in EXCLUDED_PATH_PARTS:
            return True
        if any(part.endswith(s) for s in EXCLUDED_DIR_SUFFIXES):
            return True
    return False


def gather_files(source_keys: list[str]) -> list[Path]:
    files = []
    for key in source_keys:
        for root in SOURCE_SETS.get(key, []):
            if not root.exists():
                continue
            if root.is_file():
                if not _is_excluded(root):
                    files.append(root)
                continue
            for ext in (".md", ".txt"):
                for p in root.rglob(f"*{ext}"):
                    if not _is_excluded(p):
                        files.append(p)
    # Dedup + sort
    files = sorted(set(files))
    return files


async def extract_one(router, path: Path, timeout_s: float = 90.0) -> dict:
    kind = classify_file(path)
    try:
        body = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return {"error": f"read_failed: {e}", "file": str(path), "file_sig": file_signature(path)}
    if not body.strip():
        return {"error": "empty_file", "file": str(path), "file_sig": file_signature(path)}
    if len(body) > 8000:
        body = body[:8000] + "\n\n[...truncated]"
    prompt = EXTRACTION_PROMPT.format(file=path.name, kind=kind, body=body)
    t0 = time.time()
    try:
        response = await asyncio.wait_for(router.send_oneshot(prompt), timeout=timeout_s)
        text = response.text if hasattr(response, "text") else str(response)
    except asyncio.TimeoutError:
        return {
            "error": f"timeout_{timeout_s}s",
            "file": str(path),
            "file_sig": file_signature(path),
            "elapsed_s": round(time.time() - t0, 1),
        }
    except Exception as e:
        return {
            "error": f"router_failed: {type(e).__name__}: {e}",
            "file": str(path),
            "file_sig": file_signature(path),
            "elapsed_s": round(time.time() - t0, 1),
        }
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        return {
            "error": "no_json",
            "file": str(path),
            "file_sig": file_signature(path),
            "elapsed_s": round(time.time() - t0, 1),
            "raw_excerpt": text[:200],
        }
    try:
        parsed = json.loads(m.group())
    except json.JSONDecodeError as e:
        return {
            "error": f"json_parse: {e}",
            "file": str(path),
            "file_sig": file_signature(path),
            "elapsed_s": round(time.time() - t0, 1),
            "raw_excerpt": text[:200],
        }
    parsed["file"] = str(path)
    parsed["file_sig"] = file_signature(path)
    parsed["kind"] = kind
    parsed["elapsed_s"] = round(time.time() - t0, 1)
    parsed["timestamp"] = datetime.now().isoformat()
    return parsed


def apply_to_kg(kg, extraction: dict) -> tuple[int, int]:
    if extraction.get("error"):
        return 0, 0
    path = Path(extraction["file"])
    kind = extraction.get("kind", "doc")
    # Source entity: filename-based
    src_name = path.stem
    if kind == "drift_essay":
        src_entity = f"Drift: {src_name.replace('-', ' ').title()}"
    elif kind == "library_section":
        # Use volume + filename
        try:
            vol_idx = path.parts.index("Library") + 1
            vol = path.parts[vol_idx]
            src_entity = f"{vol}/{path.name}"
        except (ValueError, IndexError):
            src_entity = path.name
    else:
        src_entity = path.name
    kg.add_entity_raw(src_entity, kind, {"file": str(path)})
    ne, ed = 0, 0
    for c in extraction.get("concepts", [])[:8]:
        name = (c.get("name") or "").strip()
        if not name or len(name) > 100:
            continue
        kg.add_entity_raw(name, c.get("kind", "concept"), {
            "role": (c.get("role") or "")[:200],
            "source_file": str(path.name),
        })
        kg.add_edge_raw(src_entity, name, "introduces")
        ne += 1
        ed += 1
    for r in extraction.get("references", [])[:6]:
        target = (r.get("target") or "").strip()
        if not target or len(target) > 100:
            continue
        kg.add_edge_raw(src_entity, target, r.get("relation_kind", "cites"))
        ed += 1
    return ne, ed


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0, help="0 = no limit")
    parser.add_argument(
        "--sources",
        default="drift,library,technical,research,sources,memory,infrastructure,unreleased",
        help="comma-separated set names",
    )
    parser.add_argument("--max-bytes", type=int, default=0, help="skip files larger than N bytes (0=unbounded)")
    parser.add_argument(
        "--retry-errors",
        action="store_true",
        help="Re-process files whose previous run errored (e.g. usage-cap 'no_json'). "
             "Successful records still count as processed.",
    )
    args = parser.parse_args()

    source_keys = [s.strip() for s in args.sources.split(",") if s.strip()]
    print(f"# Corpus KG extraction — sources: {source_keys}")

    from models import ModelRouter
    from tools import knowledge_graph as kg
    router = ModelRouter()

    files = gather_files(source_keys)
    if args.max_bytes > 0:
        files = [f for f in files if f.stat().st_size <= args.max_bytes]
    processed = load_processed(skip_errors=args.retry_errors)
    todo = [f for f in files if file_signature(f) not in processed]
    mode_note = " (retry-errors mode: errored files will be reprocessed)" if args.retry_errors else ""
    print(f"# Files: {len(files)} total, {len(processed)} already processed, {len(todo)} to do{mode_note}")
    if args.limit:
        todo = todo[: args.limit]
        print(f"# Limited to {args.limit}")

    total_ne, total_ed = 0, 0
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as logf:
        for i, p in enumerate(todo, 1):
            elapsed_so_far = time.time()
            print(f"\n[{i}/{len(todo)}] {classify_file(p)}: {p.name}", flush=True)
            extraction = await extract_one(router, p)
            logf.write(json.dumps(extraction, default=str) + "\n")
            logf.flush()
            # Progress checkpoint
            PROGRESS_PATH.write_text(json.dumps({
                "last_processed": str(p),
                "processed_count": len(processed) + i,
                "total_count": len(files),
                "ts": datetime.now().isoformat(),
            }), encoding="utf-8")
            if "error" in extraction:
                print(f"  ✗ {extraction['error']}", flush=True)
                continue
            ne, ed = apply_to_kg(kg, extraction)
            total_ne += ne
            total_ed += ed
            print(f"  + {ne} concepts, {ed} edges ({extraction.get('elapsed_s', '?')}s)", flush=True)

    print(f"\nDone: {total_ne} entities + {total_ed} edges from {len(todo)} files")


if __name__ == "__main__":
    asyncio.run(main())
