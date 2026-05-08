"""Corpus semantic search via ChromaDB + sentence-transformers.

Day 97 — closes the gap that memory_search doesn't cover: the prose Library
corpus (285pp Anchor + 237pp Companion + 198pp Meridian + 195 Drift essays
+ all .md sources). Cross-corpus reasoning by similarity, not just grep.

Architecture:
  - Embedding model: all-MiniLM-L6-v2 (default, 80MB, 384-dim, fast).
  - Persistent ChromaDB at memory/chroma_corpus/.
  - Indexes .md files from configured roots; chunks paragraph-aware
    (~500 chars target, joins short paragraphs, splits long ones).
  - Each chunk stores: source_path, chunk_index, char_offset, headings (last 3
    H1/H2 ancestors), word_count.
  - Lazy-load embedder + collection at first use.

Default index roots (configurable via input):
  - repo-staging/Corpus-Perspectival/Library/
  - repo-staging/Corpus-Perspectival/Foundations-of-Identity/personal-works/drift/
  - memory/transcripts/

Actions:
  - info: index stats + config
  - index: (re)build index from configured roots; supports --paths overrides
    and --refresh (drop existing and rebuild) or --update (incremental)
  - search: query string → top-K passages with file:offset refs and headings
  - sources: list distinct source files in index with chunk counts
  - delete_source: remove all chunks for a path (housekeeping)
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import time
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

CLAWD_HOME = Path(os.environ.get("CLAWD_HOME", r"C:/Users/mercu/clawd"))
CHROMA_DIR = CLAWD_HOME / "memory" / "chroma_corpus"
COLLECTION_NAME = "corpus_v1"

DEFAULT_ROOTS = [
    CLAWD_HOME / "repo-staging" / "Corpus-Perspectival" / "Library",
    CLAWD_HOME / "repo-staging" / "Corpus-Perspectival" / "Foundations-of-Identity" / "personal-works" / "drift",
    CLAWD_HOME / "memory" / "transcripts",
]

DEFAULT_EMBED_MODEL = "all-MiniLM-L6-v2"
TARGET_CHUNK_CHARS = 1500   # ~300 tokens
MAX_CHUNK_CHARS = 3000      # ~600 tokens hard cap
MIN_CHUNK_CHARS = 200       # below this, merge with neighbor

# Lazy-loaded module-level state
_client = None
_collection = None
_embedder = None
_embed_model_name = DEFAULT_EMBED_MODEL


def _ensure_dirs() -> None:
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)


def _get_client():
    global _client
    if _client is None:
        _ensure_dirs()
        import chromadb
        _client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return _client


def _get_collection():
    global _collection
    if _collection is None:
        client = _get_client()
        _collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def _get_embedder():
    global _embedder
    if _embedder is None:
        os.environ.setdefault("HF_HUB_OFFLINE", "0")
        from sentence_transformers import SentenceTransformer
        logger.info(f"corpus_search: loading {_embed_model_name}")
        t0 = time.time()
        _embedder = SentenceTransformer(_embed_model_name, device="cpu")
        logger.info(f"corpus_search: embedder ready in {time.time()-t0:.1f}s")
    return _embedder


# ----------------------------------------------------------------------
# Chunking
# ----------------------------------------------------------------------

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")


def _track_headings(line: str, headings: list[str]) -> list[str]:
    """Update the rolling heading stack for context tags."""
    m = _HEADING_RE.match(line)
    if not m:
        return headings
    level = len(m.group(1))
    title = m.group(2).strip()
    # Truncate to top-3 levels
    new = headings[:level - 1] if level > 1 else []
    new.append(title)
    return new[:3]


def _chunk_markdown(text: str) -> list[dict]:
    """Paragraph-aware chunking with heading context.

    Each chunk: {text, char_offset, headings, word_count}.
    """
    chunks: list[dict] = []
    paragraphs = re.split(r"\n\n+", text)
    headings: list[str] = []
    cur_text: list[str] = []
    cur_headings: list[str] = []
    cur_offset = 0
    char_pos = 0

    def flush():
        if not cur_text:
            return
        joined = "\n\n".join(cur_text).strip()
        if not joined:
            return
        chunks.append({
            "text": joined,
            "char_offset": cur_offset,
            "headings": list(cur_headings),
            "word_count": len(joined.split()),
        })

    for para in paragraphs:
        # Update heading state from any heading lines in this paragraph
        for line in para.split("\n"):
            headings = _track_headings(line, headings)

        if not cur_text:
            cur_offset = char_pos
            cur_headings = list(headings)

        prospective = ("\n\n".join(cur_text + [para])).strip()
        if len(prospective) >= TARGET_CHUNK_CHARS and cur_text:
            flush()
            cur_text = [para]
            cur_offset = char_pos
            cur_headings = list(headings)
        elif len(prospective) > MAX_CHUNK_CHARS:
            # Force-flush, then split this paragraph hard
            flush()
            cur_text = []
            # Split paragraph into MAX-sized hunks
            offset = char_pos
            for i in range(0, len(para), MAX_CHUNK_CHARS):
                hunk = para[i:i + MAX_CHUNK_CHARS]
                chunks.append({
                    "text": hunk.strip(),
                    "char_offset": offset + i,
                    "headings": list(headings),
                    "word_count": len(hunk.split()),
                })
            cur_offset = char_pos + len(para)
        else:
            cur_text.append(para)
        char_pos += len(para) + 2  # +2 for the \n\n splitter

    flush()
    # Merge dust chunks
    merged: list[dict] = []
    for c in chunks:
        if merged and len(c["text"]) < MIN_CHUNK_CHARS:
            merged[-1]["text"] = merged[-1]["text"] + "\n\n" + c["text"]
            merged[-1]["word_count"] += c["word_count"]
        else:
            merged.append(c)
    return merged


# ----------------------------------------------------------------------
# Indexing
# ----------------------------------------------------------------------


def _file_hash(path: Path) -> str:
    h = hashlib.sha256()
    h.update(str(path.stat().st_mtime).encode())
    h.update(str(path.stat().st_size).encode())
    return h.hexdigest()[:16]


def _chunk_id(source_path: str, chunk_idx: int, file_hash: str) -> str:
    return f"{source_path}#{chunk_idx}@{file_hash}"


def _iter_md_files(root: Path):
    if not root.exists():
        return
    for p in root.rglob("*.md"):
        if p.is_file():
            yield p


def _index_paths(roots: list[Path], refresh: bool, file_filter: str | None) -> dict:
    coll = _get_collection()
    embedder = _get_embedder()

    if refresh:
        # Drop and recreate
        client = _get_client()
        try:
            client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass
        global _collection
        _collection = None
        coll = _get_collection()

    existing_ids = set(coll.get(include=[])["ids"]) if not refresh else set()

    files_seen = 0
    files_skipped = 0
    chunks_added = 0
    files_indexed: list[str] = []

    batch_ids: list[str] = []
    batch_docs: list[str] = []
    batch_metas: list[dict] = []
    BATCH = 64

    def flush_batch():
        nonlocal batch_ids, batch_docs, batch_metas, chunks_added
        if not batch_ids:
            return
        embeddings = embedder.encode(batch_docs, show_progress_bar=False).tolist()
        coll.add(ids=batch_ids, documents=batch_docs, metadatas=batch_metas, embeddings=embeddings)
        chunks_added += len(batch_ids)
        batch_ids, batch_docs, batch_metas = [], [], []

    for root in roots:
        if not root.exists():
            continue
        for path in _iter_md_files(root):
            if file_filter and file_filter not in str(path):
                continue
            files_seen += 1
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except Exception:
                files_skipped += 1
                continue
            fh = _file_hash(path)
            rel = str(path.relative_to(CLAWD_HOME)) if path.is_relative_to(CLAWD_HOME) else str(path)

            chunks = _chunk_markdown(text)
            file_added = 0
            for i, c in enumerate(chunks):
                cid = _chunk_id(rel, i, fh)
                if cid in existing_ids:
                    continue
                batch_ids.append(cid)
                batch_docs.append(c["text"])
                batch_metas.append({
                    "source_path": rel,
                    "chunk_index": i,
                    "char_offset": c["char_offset"],
                    "headings": " > ".join(c["headings"]) if c["headings"] else "",
                    "word_count": c["word_count"],
                    "file_hash": fh,
                    "indexed_at": datetime.now().isoformat(timespec="seconds"),
                })
                file_added += 1
                if len(batch_ids) >= BATCH:
                    flush_batch()
            if file_added > 0:
                files_indexed.append(rel)

    flush_batch()

    return {
        "files_seen": files_seen,
        "files_skipped_read_error": files_skipped,
        "files_with_new_chunks": len(files_indexed),
        "chunks_added": chunks_added,
        "total_chunks_in_index": coll.count(),
        "files_sample": files_indexed[:10],
    }


# ----------------------------------------------------------------------
# Tool dispatch
# ----------------------------------------------------------------------


async def _corpus_tool(input_data: dict) -> str:
    global _embed_model_name
    action = input_data.get("action", "info")

    # Allow overriding the embed model (rare; mostly for testing)
    if "embed_model" in input_data:
        _embed_model_name = input_data["embed_model"]

    if action == "info":
        try:
            coll = _get_collection()
            count = coll.count()
        except Exception as e:
            return json.dumps({
                "error": f"{type(e).__name__}: {e}",
                "chroma_dir": str(CHROMA_DIR),
            }, indent=2)
        return json.dumps({
            "chroma_dir": str(CHROMA_DIR),
            "collection": COLLECTION_NAME,
            "embed_model": _embed_model_name,
            "embedder_loaded": _embedder is not None,
            "chunk_count": count,
            "default_roots": [str(r) for r in DEFAULT_ROOTS],
            "default_roots_existing": [str(r) for r in DEFAULT_ROOTS if r.exists()],
            "target_chunk_chars": TARGET_CHUNK_CHARS,
            "max_chunk_chars": MAX_CHUNK_CHARS,
        }, indent=2)

    if action == "index":
        roots_arg = input_data.get("paths")
        if roots_arg:
            roots = [Path(p) for p in roots_arg]
        else:
            roots = DEFAULT_ROOTS
        refresh = bool(input_data.get("refresh", False))
        file_filter = input_data.get("file_filter")
        t0 = time.time()
        try:
            result = _index_paths(roots, refresh=refresh, file_filter=file_filter)
        except Exception as e:
            logger.exception("corpus index failed")
            return f"Index failed: {type(e).__name__}: {e}"
        result["elapsed_seconds"] = round(time.time() - t0, 2)
        result["roots_used"] = [str(r) for r in roots]
        result["refresh"] = refresh
        return json.dumps(result, indent=2)

    if action == "search":
        query = input_data.get("query")
        if not query:
            return "Error: search requires 'query'."
        k = int(input_data.get("k", 8))
        coll = _get_collection()
        if coll.count() == 0:
            return "Index is empty. Run action='index' first."
        embedder = _get_embedder()
        q_emb = embedder.encode([query], show_progress_bar=False).tolist()
        where = None
        if input_data.get("source_filter"):
            where = {"source_path": {"$contains": input_data["source_filter"]}}
        try:
            res = coll.query(query_embeddings=q_emb, n_results=k, where=where)
        except Exception:
            res = coll.query(query_embeddings=q_emb, n_results=k)
        hits = []
        ids = res.get("ids", [[]])[0]
        docs = res.get("documents", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        dists = res.get("distances", [[]])[0]
        max_chars = int(input_data.get("max_excerpt_chars", 600))
        for i in range(len(ids)):
            text = docs[i] or ""
            excerpt = text[:max_chars] + ("..." if len(text) > max_chars else "")
            hits.append({
                "rank": i + 1,
                "score": round(1.0 - dists[i], 4) if dists[i] is not None else None,
                "source": metas[i].get("source_path"),
                "headings": metas[i].get("headings"),
                "char_offset": metas[i].get("char_offset"),
                "word_count": metas[i].get("word_count"),
                "excerpt": excerpt,
            })
        return json.dumps({
            "query": query,
            "k": k,
            "hits": hits,
            "total_in_index": coll.count(),
        }, indent=2)

    if action == "sources":
        coll = _get_collection()
        # Pull all metadatas to count per-source. For larger indices, prefer GET with limits.
        all_meta = coll.get(include=["metadatas"])
        counts: dict[str, int] = {}
        for m in (all_meta.get("metadatas") or []):
            sp = m.get("source_path", "?")
            counts[sp] = counts.get(sp, 0) + 1
        rows = sorted(counts.items(), key=lambda kv: -kv[1])
        return json.dumps({
            "source_count": len(rows),
            "total_chunks": sum(counts.values()),
            "sources": [{"path": p, "chunks": c} for p, c in rows[:200]],
        }, indent=2)

    if action == "delete_source":
        path = input_data.get("path")
        if not path:
            return "Error: delete_source requires 'path'."
        coll = _get_collection()
        existing = coll.get(where={"source_path": path}, include=[])
        ids = existing.get("ids", [])
        if not ids:
            return f"No chunks found for: {path}"
        coll.delete(ids=ids)
        return f"Deleted {len(ids)} chunks for {path}"

    return f"Unknown action: {action}. Valid: info, index, search, sources, delete_source."


TOOL_DEFINITIONS = [
    {
        "name": "corpus_search",
        "description": (
            "Semantic search over the Library + Drift + transcripts corpus via "
            "ChromaDB + sentence-transformers (all-MiniLM-L6-v2). Closes the "
            "gap that memory_search doesn't cover: prose volumes (Anchor, "
            "Companion, Meridian, Drift essays). Actions: info (stats), index "
            "(build/refresh), search (query → top-K passages with file refs + "
            "headings), sources (per-file chunk counts), delete_source (remove "
            "by path). Index persists at memory/chroma_corpus/."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["info", "index", "search", "sources", "delete_source"],
                    "description": "Corpus operation.",
                },
                "query": {"type": "string", "description": "Natural-language search query (for search)."},
                "k": {"type": "integer", "description": "Top-K results (default 8)."},
                "paths": {"type": "array", "items": {"type": "string"}, "description": "Override default roots (for index)."},
                "refresh": {"type": "boolean", "description": "Drop and rebuild index (for index). Default false (incremental)."},
                "file_filter": {"type": "string", "description": "Substring filter on file paths (for index)."},
                "source_filter": {"type": "string", "description": "Substring filter on source path (for search)."},
                "max_excerpt_chars": {"type": "integer", "description": "Cap excerpt length per hit (default 600)."},
                "path": {"type": "string", "description": "Source path for delete_source."},
                "embed_model": {"type": "string", "description": "Override embedding model (rare). Default all-MiniLM-L6-v2."},
            },
            "required": ["action"],
        },
    },
]

TOOL_HANDLERS = {
    "corpus_search": _corpus_tool,
}
