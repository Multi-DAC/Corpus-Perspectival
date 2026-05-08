"""Memory tools — search and update memory files."""
import json
import logging
import math
from datetime import datetime
from pathlib import Path
from typing import Any

import config
from tools._base import resolve_path

logger = logging.getLogger("clawd.tools.memory")

# Cross-encoder reranker — lazy-loaded
_cross_encoder = None
_cross_encoder_failed = False


def _get_cross_encoder():
    """Lazy-load cross-encoder for reranking. Returns None if unavailable.

    Day 96 evening (Phase 4 #57): upgraded from ms-marco-MiniLM-L-6-v2 (~22M
    params, English-only) to BAAI/bge-reranker-v2-m3 (~568M params, multilingual,
    state-of-the-art per Stream 3 research). 15-40% retrieval accuracy gain
    over embedding-only or smaller cross-encoders. Runs on RTX 5080 trivially.

    Falls back to ms-marco model if bge isn't available locally (e.g. on
    machines without HF cache + offline). RTX 5080 with ~16GB VRAM handles
    bge easily; CPU still functional but slower (~100ms/batch vs ~10ms GPU).
    """
    global _cross_encoder, _cross_encoder_failed
    if _cross_encoder_failed:
        return None
    if _cross_encoder is not None:
        return _cross_encoder
    try:
        import torch
        from sentence_transformers import CrossEncoder
        device = "cuda" if torch.cuda.is_available() else "cpu"
        # Try bge-reranker-v2-m3 first (preferred)
        try:
            _cross_encoder = CrossEncoder("BAAI/bge-reranker-v2-m3", device=device)
            logger.info(f"Loaded BAAI/bge-reranker-v2-m3 for reranking (device={device})")
            return _cross_encoder
        except Exception as e_bge:
            logger.info(f"bge-reranker-v2-m3 unavailable, falling back to ms-marco: {e_bge}")
            _cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", device=device)
            logger.info(f"Loaded ms-marco-MiniLM-L-6-v2 for reranking (device={device})")
            return _cross_encoder
    except Exception as e:
        logger.info(f"Cross-encoder unavailable (RRF-only mode): {e}")
        _cross_encoder_failed = True
        return None


TOOL_DEFINITIONS = [
    {
        "name": "memory_search",
        "description": "Search all memory with adaptive retrieval strategy. Choose the best strategy for your query type, or use 'auto' to let the system decide.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search terms — keywords, phrases, concepts."
                },
                "strategy": {
                    "type": "string",
                    "enum": ["auto", "vector", "keyword", "items", "episodes", "graph", "chain"],
                    "description": "auto: hybrid RRF fusion (default). vector: semantic similarity. keyword: TF-IDF exact match. items: structured memory items. episodes: episodic experiences. graph: knowledge graph traversal. chain: multi-hop iterative retrieval (follows entity/date trails across 2-3 hops)."
                },
                "top_k": {
                    "type": "integer",
                    "description": "Max results (default 10, max 30)."
                },
                "include_metadata": {
                    "type": "boolean",
                    "description": "Include scores, sources, timestamps (default false)."
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "memory_update",
        "description": "Update memory files — append to daily log, update MEMORY.md, write handoff, or update STATE.md. Use this to maintain continuity and self-awareness.",
        "input_schema": {
            "type": "object",
            "properties": {
                "target": {
                    "type": "string",
                    "enum": ["daily_log", "memory", "handoff", "state", "context"],
                    "description": "Which memory file to update: daily_log (today's session log), memory (MEMORY.md), handoff (memory/handoff.md), state (STATE.md), context (CONTEXT.md)."
                },
                "content": {
                    "type": "string",
                    "description": "Content to append or write."
                },
                "append": {
                    "type": "boolean",
                    "description": "Append (true) or overwrite (false). Default: true for daily_log, false for others."
                }
            },
            "required": ["target", "content"]
        }
    },
]

# Optional semantic search index — set by __init__.py if available
_embedding_index = None


def set_embedding_index(index):
    """Register the semantic embedding index for hybrid search."""
    global _embedding_index
    _embedding_index = index


async def _memory_search(input_data: dict) -> str:
    """Search across all memory with adaptive retrieval strategy.
    Supports: auto (hybrid RRF), vector, keyword, items, episodes, graph."""
    query = input_data["query"]
    strategy = input_data.get("strategy", "auto")
    top_k = min(int(input_data.get("top_k", 10)), 30)
    include_metadata = input_data.get("include_metadata", False)

    if strategy == "auto":
        # Existing hybrid search (unchanged behavior)
        if _embedding_index is not None:
            try:
                return await _hybrid_search(query, top_k=top_k, include_metadata=include_metadata)
            except Exception as e:
                logger.warning(f"Hybrid search failed, falling back to keyword: {e}")
        return await _keyword_search(query, max_results=top_k)

    elif strategy == "vector":
        if _embedding_index is None:
            return "Vector search unavailable — no embedding index loaded."
        results = _embedding_index.search(query, top_k=top_k)
        return _format_vector_results(results, include_metadata)

    elif strategy == "keyword":
        results = await _keyword_search(query, max_results=top_k, raw=True)
        return _format_keyword_results(results, include_metadata)

    elif strategy == "items":
        try:
            from tools.memory_items import search_items_raw
            results = search_items_raw(query, max_results=top_k)
            return _format_item_results(results, include_metadata)
        except ImportError:
            return "Item search unavailable — memory_items module not loaded."
        except Exception as e:
            return f"Item search failed: {e}"

    elif strategy == "episodes":
        try:
            from tools.sqlite_store import search_episodes_fts
            results = await search_episodes_fts(query, limit=top_k)
            return _format_episode_results(results, include_metadata)
        except Exception as e:
            return f"Episode search failed: {e}"

    elif strategy == "graph":
        return _graph_search(query, top_k, include_metadata)

    elif strategy == "chain":
        return await _chain_search(query, top_k=top_k, include_metadata=include_metadata)

    else:
        return f"Unknown strategy: {strategy}. Use: auto, vector, keyword, items, episodes, graph, chain."


def _format_vector_results(results: list, include_metadata: bool) -> str:
    """Format vector search results."""
    if not results:
        return "No vector results found."
    parts = []
    for filepath, chunk, score in results:
        try:
            rel = Path(filepath).relative_to(config.CLAWD_HOME)
        except (ValueError, TypeError):
            rel = filepath
        if include_metadata:
            parts.append(f"=== {rel} (similarity: {score:.4f}) ===\n{chunk[:1000]}")
        else:
            parts.append(f"=== {rel} ===\n{chunk[:1000]}")
    return "\n\n".join(parts)


def _format_keyword_results(results: list, include_metadata: bool) -> str:
    """Format keyword (TF-IDF) raw results."""
    if not results:
        return "No keyword results found."
    parts = []
    for filepath, section, score in results:
        if include_metadata:
            parts.append(f"=== {filepath} (tf-idf: {score:.4f}) ===\n{section[:1000]}")
        else:
            parts.append(f"=== {filepath} ===\n{section[:1000]}")
    return "\n\n".join(parts)


def _format_item_results(results: list, include_metadata: bool) -> str:
    """Format structured memory item results."""
    if not results:
        return "No memory items found."
    parts = []
    for filepath, content, score in results:
        if include_metadata:
            parts.append(f"=== {filepath} (score: {score:.4f}) ===\n{content[:1000]}")
        else:
            parts.append(f"{content[:1000]}")
    return "\n\n".join(parts)


def _format_episode_results(results: list, include_metadata: bool) -> str:
    """Format episodic experience results."""
    if not results:
        return "No episodes found."
    parts = []
    for row in results:
        task = row.get("task", "")
        lesson = row.get("lesson", "")
        outcome = row.get("outcome", "")
        if include_metadata:
            created = row.get("created_at", row.get("timestamp", ""))
            rank = row.get("rank", 0)
            parts.append(f"[Episode] {task}\n  Lesson: {lesson}\n  Outcome: {outcome}\n  (created: {created}, rank: {rank})")
        else:
            parts.append(f"[Episode] {task}\n  Lesson: {lesson}\n  Outcome: {outcome}")
    return "\n\n".join(parts)


def _graph_search(query: str, top_k: int, include_metadata: bool) -> str:
    """Search the knowledge graph by fuzzy-matching entity names against query words."""
    try:
        from tools.knowledge_graph import _load_graph
    except ImportError:
        return "Knowledge graph module not available."

    graph = _load_graph()
    entities = graph.get("entities", {})
    edges = graph.get("edges", [])

    if not entities:
        return "Knowledge graph is empty."

    query_words = set(query.lower().split())
    scored = []
    for eid, entity in entities.items():
        name_words = set(eid.split("_")) | set(entity.get("name", "").lower().split())
        props_text = json.dumps(entity.get("properties", {})).lower()
        # Score: number of query words matching entity name/id + partial props match
        overlap = len(query_words & name_words)
        prop_hits = sum(1 for w in query_words if w in props_text)
        score = overlap * 2 + prop_hits
        if score > 0:
            scored.append((eid, entity, score))

    scored.sort(key=lambda x: x[2], reverse=True)
    scored = scored[:top_k]

    if not scored:
        return f"No entities matching '{query}' found in knowledge graph."

    parts = []
    for eid, entity, score in scored:
        etype = entity.get("type", "?")
        name = entity.get("name", eid)
        props = entity.get("properties", {})

        # Find connected edges
        connected = []
        for edge in edges:
            if edge.get("valid_to") is not None:
                continue
            if edge["from"] == eid:
                connected.append(f"  --{edge.get('relation', '?')}--> {edge['to']}")
            elif edge["to"] == eid:
                connected.append(f"  <--{edge.get('relation', '?')}-- {edge['from']}")

        if include_metadata:
            created = entity.get("created_at", "")
            valid_from = entity.get("valid_from", "")
            header = f"[{etype}] {name} (score: {score}, created: {created})"
            if props:
                header += f"\n  Properties: {json.dumps(props)[:200]}"
        else:
            header = f"[{etype}] {name}"
            if props:
                header += f" — {json.dumps(props)[:150]}"

        if connected:
            header += "\n" + "\n".join(connected[:10])
        parts.append(header)

    return f"Knowledge graph matches for '{query}':\n\n" + "\n\n".join(parts)


async def _hybrid_search(query: str, top_k: int = 10, include_metadata: bool = False) -> str:
    """Hybrid search: vector similarity + keyword matching with Reciprocal Rank Fusion.
    Optionally applies cross-encoder reranking for higher precision."""
    # Retrieve more candidates for reranking (top-30 each instead of 15)
    vector_results = _embedding_index.search(query, top_k=30)

    # Keyword search
    keyword_text = await _keyword_search(query, max_results=30, raw=True)

    # Item search (structured memory items)
    item_results = []
    try:
        from tools.memory_items import search_items_raw
        item_results = search_items_raw(query, max_results=30)
    except ImportError as e:
        logger.debug(f"Optional import: {e}")
    except Exception as e:
        logger.warning(f"Item search failed: {e}")

    # FTS5 episode search (4th source)
    fts5_results = []
    try:
        from tools.sqlite_store import search_episodes_fts
        fts5_rows = await search_episodes_fts(query, limit=30)
        for row in fts5_rows:
            content = f"[Episode] {row.get('task', '')} — {row.get('lesson', '')} (outcome: {row.get('outcome', '')})"
            fts5_results.append(("sqlite:episodes", content, row.get('rank', 0)))
    except Exception as e:
        logger.debug(f"FTS5 episode search skipped: {e}")

    if not vector_results and not keyword_text and not item_results and not fts5_results:
        return f"No results found for: {query}"

    # RRF merge
    rrf_scores = {}
    k = 60  # RRF constant

    # Score vector results
    for rank, (filepath, chunk, score) in enumerate(vector_results):
        key = f"{filepath}::{chunk[:100]}"
        rrf_scores[key] = rrf_scores.get(key, 0) + 1.0 / (k + rank + 1)
        rrf_scores[key + "::data"] = (filepath, chunk, score)

    # Score keyword results
    for rank, (filepath, section, score) in enumerate(keyword_text):
        key = f"{filepath}::{section[:100]}"
        rrf_scores[key] = rrf_scores.get(key, 0) + 1.0 / (k + rank + 1)
        rrf_scores[key + "::data"] = (filepath, section, score)

    # Score item results
    for rank, (filepath, content, score) in enumerate(item_results):
        key = f"item::{content[:100]}"
        rrf_scores[key] = rrf_scores.get(key, 0) + 1.0 / (k + rank + 1)
        rrf_scores[key + "::data"] = (filepath, content, score)

    # Score FTS5 episode results
    for rank, (filepath, content, score) in enumerate(fts5_results):
        key = f"episode::{content[:100]}"
        rrf_scores[key] = rrf_scores.get(key, 0) + 1.0 / (k + rank + 1)
        rrf_scores[key + "::data"] = (filepath, content, score)

    # Sort by RRF score — get top-50 candidates for reranking
    result_keys = [rk for rk in rrf_scores if not rk.endswith("::data")]
    result_keys.sort(key=lambda rk: rrf_scores[rk], reverse=True)
    top_candidates = result_keys[:50]

    # Cross-encoder reranking stage
    reranker = _get_cross_encoder()
    if reranker and len(top_candidates) > 1:
        try:
            # Build (query, passage) pairs for cross-encoder
            pairs = []
            valid_keys = []
            for key in top_candidates:
                data = rrf_scores.get(key + "::data")
                if data:
                    _, content, _ = data
                    pairs.append((query, content[:1024]))  # Truncate for cross-encoder (model supports ~2000)
                    valid_keys.append(key)

            if pairs:
                ce_scores = reranker.predict(pairs)
                # Normalize CE scores to [0, 1] range for blending
                ce_min, ce_max = min(ce_scores), max(ce_scores)
                ce_range = ce_max - ce_min if ce_max > ce_min else 1.0
                ce_norm = [(s - ce_min) / ce_range for s in ce_scores]
                # Blend RRF + cross-encoder scores (0.6 RRF + 0.4 CE)
                blended = []
                for key, ce_n in zip(valid_keys, ce_norm):
                    rrf_s = rrf_scores.get(key, 0)
                    blended.append((key, 0.6 * rrf_s + 0.4 * ce_n))
                blended.sort(key=lambda x: x[1], reverse=True)
                top_candidates = [b[0] for b in blended]
                logger.debug(f"Cross-encoder reranked {len(pairs)} candidates (blended 0.6 RRF + 0.4 CE)")
        except Exception as e:
            logger.warning(f"Cross-encoder reranking failed, using RRF order: {e}")

    # Format top results
    output_parts = []
    for key in top_candidates[:top_k]:
        data = rrf_scores.get(key + "::data")
        if data:
            filepath, content, score = data
            try:
                rel = Path(filepath).relative_to(config.CLAWD_HOME)
            except (ValueError, TypeError):
                rel = filepath
            if include_metadata:
                output_parts.append(f"=== {rel} (relevance: {rrf_scores[key]:.4f}, source_score: {score:.4f}) ===\n{content[:1000]}")
            else:
                output_parts.append(f"=== {rel} (relevance: {rrf_scores[key]:.4f}) ===\n{content[:1000]}")

    return "\n\n".join(output_parts) if output_parts else f"No results found for: {query}"


async def _chain_search(query: str, top_k: int = 10, max_hops: int = 3, include_metadata: bool = False) -> str:
    """Multi-hop chain retrieval: search, extract entities/dates, search again.

    Follows trails through memory by extracting salient terms from initial results
    and using them to discover connected information across 2-3 hops.
    Deduplicates across hops and returns a merged, chronologically-ordered result set.
    """
    import re

    all_results = {}  # key -> (filepath, content, score, hop)
    seen_content_keys = set()
    hop_queries = [query]

    for hop in range(max_hops):
        current_query = hop_queries[hop] if hop < len(hop_queries) else None
        if current_query is None:
            break

        # Use hybrid search for each hop if available, else keyword
        hop_results = []
        if _embedding_index is not None:
            try:
                vector_results = _embedding_index.search(current_query, top_k=15)
                hop_results.extend(vector_results)
            except Exception:
                pass

        keyword_results = await _keyword_search(current_query, max_results=15, raw=True)
        for filepath, section, score in keyword_results:
            hop_results.append((filepath, section, score))

        if not hop_results:
            break

        # Deduplicate and store with hop metadata
        new_content_for_extraction = []
        for filepath, content, score in hop_results:
            content_key = content[:150].strip()
            if content_key not in seen_content_keys:
                seen_content_keys.add(content_key)
                result_key = f"{filepath}::{content_key}"
                # Boost earlier hops (more directly relevant)
                hop_decay = 1.0 / (1 + hop * 0.3)
                all_results[result_key] = (filepath, content, score * hop_decay, hop)
                new_content_for_extraction.append(content)

        if not new_content_for_extraction or hop >= max_hops - 1:
            break

        # Extract entities and dates from new results to form next query
        combined_text = " ".join(new_content_for_extraction[:5])  # Top 5 results

        # Extract dates (YYYY-MM-DD, Month DD, etc.)
        dates = re.findall(r'\b\d{4}-\d{2}-\d{2}\b', combined_text)
        # Extract capitalized multi-word entities (proper nouns, project names)
        entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b', combined_text)
        # Extract quoted terms
        quoted = re.findall(r'"([^"]{3,50})"', combined_text)
        # Extract markdown headers as topic markers
        headers = re.findall(r'#+\s+(.+)', combined_text)

        # Build next hop query from extracted terms (different from original)
        extracted = set()
        for d in dates[:3]:
            extracted.add(d)
        for e in entities[:3]:
            if e.lower() not in query.lower():
                extracted.add(e)
        for q in quoted[:2]:
            if q.lower() not in query.lower():
                extracted.add(q)
        for h in headers[:2]:
            h_clean = h.strip()
            if h_clean.lower() not in query.lower() and len(h_clean) > 3:
                extracted.add(h_clean)

        if extracted:
            next_query = " ".join(list(extracted)[:5])
            if next_query.lower() != current_query.lower():
                hop_queries.append(next_query)
                logger.debug(f"Chain search hop {hop+1} → {hop+2}: '{next_query}'")

    if not all_results:
        return f"No results found for chain query: {query}"

    # Sort by score (with hop decay already applied)
    sorted_results = sorted(all_results.values(), key=lambda x: x[2], reverse=True)

    # Format output
    output_parts = []
    hops_used = max(r[3] for r in sorted_results) + 1
    output_parts.append(f"[Chain search: {hops_used} hop{'s' if hops_used > 1 else ''}, {len(sorted_results)} unique results, queries: {hop_queries[:hops_used]}]\n")

    for filepath, content, score, hop in sorted_results[:top_k]:
        try:
            rel = Path(filepath).relative_to(config.CLAWD_HOME)
        except (ValueError, TypeError):
            rel = filepath
        if include_metadata:
            output_parts.append(f"=== {rel} (score: {score:.4f}, hop: {hop+1}) ===\n{content[:1000]}")
        else:
            output_parts.append(f"=== {rel} (hop {hop+1}) ===\n{content[:1000]}")

    return "\n\n".join(output_parts)


async def _keyword_search(query: str, max_results: int = 20, raw: bool = False):
    """TF-IDF keyword search across all memory files."""
    query_lower = query.lower()
    keywords = query_lower.split()
    scored_results = []

    search_paths = []

    # All .md files in CLAWD_HOME (identity files)
    for md_file in config.CLAWD_HOME.glob("*.md"):
        search_paths.append(md_file)

    # Memory directory
    if config.MEMORY_DIR.is_dir():
        search_paths.extend(config.MEMORY_DIR.glob("*.md"))
        convos_dir = config.MEMORY_DIR / "conversations"
        if convos_dir.is_dir():
            search_paths.extend(convos_dir.glob("*.md"))
        summaries_dir = config.MEMORY_DIR / "weekly-summaries"
        if summaries_dir.is_dir():
            search_paths.extend(summaries_dir.glob("*.md"))
        daily_summaries_dir = config.MEMORY_DIR / "daily-summaries"
        if daily_summaries_dir.is_dir():
            search_paths.extend(daily_summaries_dir.glob("*.md"))

    # Project files
    if config.PROJECTS_DIR.is_dir():
        for md_file in config.PROJECTS_DIR.glob("**/*.md"):
            search_paths.append(md_file)

    # Skills files
    if config.SKILLS_DIR.is_dir():
        for md_file in config.SKILLS_DIR.glob("**/*.md"):
            search_paths.append(md_file)

    # Chats With Clawd
    chats_dir = config.CLAWD_HOME / "Chats With Clawd"
    if chats_dir.is_dir():
        for html_file in chats_dir.glob("**/*.html"):
            search_paths.append(html_file)
        for json_file in chats_dir.glob("**/*.json"):
            search_paths.append(json_file)

    # Awesome-slash, superpowers, pragmatic-clean-code-reviewer (now under skills/)
    for subdir in ["awesome-slash", "superpowers", "pragmatic-clean-code-reviewer"]:
        d = config.SKILLS_DIR / subdir
        if d.is_dir():
            for md_file in d.glob("**/*.md"):
                search_paths.append(md_file)

    # Experience log
    exp_file = config.MEMORY_DIR / "experiences.json"
    if exp_file.exists():
        search_paths.append(exp_file)

    # TF-IDF scoring
    total_docs = len(search_paths)
    doc_freq = {kw: 0 for kw in keywords}

    file_data = []
    for fpath in search_paths:
        if not fpath.exists():
            continue
        try:
            content = fpath.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        content_lower = content.lower()
        for kw in keywords:
            if kw in content_lower:
                doc_freq[kw] += 1
        file_data.append((fpath, content, content_lower))

    # IDF weights
    idf = {}
    for kw in keywords:
        df = doc_freq.get(kw, 0)
        idf[kw] = math.log((total_docs + 1) / (df + 1)) + 1.0 if total_docs > 0 else 1.0

    for fpath, content, content_lower in file_data:
        lines = content.split("\n")
        matched_sections = []
        section_scores = []

        for i, line in enumerate(lines):
            line_lower = line.lower()
            matching_kws = [kw for kw in keywords if kw in line_lower]
            if matching_kws:
                start = max(0, i - 5)
                end = min(len(lines), i + 6)
                section = "\n".join(lines[start:end])

                section_lower = section.lower()
                score = 0.0
                for kw in matching_kws:
                    tf = section_lower.count(kw) / max(len(section_lower.split()), 1)
                    score += tf * idf.get(kw, 1.0)

                # Boost identity files
                try:
                    rel = fpath.relative_to(config.CLAWD_HOME)
                    rel_str = str(rel)
                except ValueError:
                    rel_str = str(fpath)

                if rel_str in ("identity/SOUL.md", "identity/WHO-I-AM.md", "identity/IDENTITY.md",
                               "operations/STATE.md", "identity/DRIVE.md",
                               "identity/RELATIONSHIPS.md", "MEMORY.md"):
                    score *= 2.0
                elif "handoff" in rel_str.lower():
                    score *= 1.8
                elif "learnings" in rel_str.lower():
                    score *= 1.5

                score *= (1 + 0.3 * len(matching_kws))

                matched_sections.append(section)
                section_scores.append(score)

        if matched_sections:
            seen = set()
            unique = []
            unique_scores = []
            for s, sc in zip(matched_sections, section_scores):
                key = s[:100]
                if key not in seen:
                    seen.add(key)
                    unique.append(s)
                    unique_scores.append(sc)

            top_indices = sorted(range(len(unique_scores)), key=lambda i: unique_scores[i], reverse=True)[:5]
            top_sections = [unique[i] for i in top_indices]
            file_score = max(unique_scores)

            try:
                rel = fpath.relative_to(config.CLAWD_HOME)
            except ValueError:
                rel = fpath

            if raw:
                for section, sc in zip(top_sections, [unique_scores[i] for i in top_indices]):
                    scored_results.append((str(rel), section, sc))
            else:
                scored_results.append(
                    (file_score, f"=== {rel} (relevance: {file_score:.2f}) ===\n" + "\n---\n".join(top_sections))
                )

    if raw:
        scored_results.sort(key=lambda x: x[2], reverse=True)
        return scored_results[:max_results]

    if not scored_results:
        return f"No results found for: {query}"

    scored_results.sort(key=lambda x: x[0], reverse=True)
    return "\n\n".join(r[1] for r in scored_results[:max_results])


async def _memory_update(input_data: dict) -> str:
    """Update memory files for continuity."""
    target = input_data["target"]
    content = input_data["content"]
    default_append = target == "daily_log"
    append = input_data.get("append", default_append)

    timestamp = datetime.now().strftime("%H:%M:%S")
    today = datetime.now().strftime("%Y-%m-%d")

    if target == "daily_log":
        filepath = config.MEMORY_DIR / f"{today}.md"
        filepath.parent.mkdir(parents=True, exist_ok=True)
        if not filepath.exists():
            filepath.write_text(f"# Session Log — {today}\n\n", encoding="utf-8")
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(f"**{timestamp}** — {content}\n\n")

        # Trigger re-index if embedding index is available
        if _embedding_index is not None:
            try:
                _embedding_index.index_file(filepath)
            except Exception as e:
                logger.warning(f"Embedding re-index failed for daily log {filepath.name}: {e}")

        # Also index in SQLite
        try:
            from tools.sqlite_store import get_db
            db = await get_db()
            if db:
                await db.execute(
                    "INSERT OR REPLACE INTO memory_items (id, type, content, source, created, memory_tier, importance) "
                    "VALUES (?, 'fact', ?, ?, ?, 'warm', 5)",
                    (f"log-{today}-{timestamp.replace(':', '')}", content, f"daily_log/{today}.md", datetime.now().isoformat())
                )
                await db.commit()
        except Exception as e:
            logger.debug(f"SQLite daily_log index failed: {e}")

        return f"Appended to daily log ({today}.md)."

    elif target == "memory":
        filepath = config.CLAWD_HOME / "MEMORY.md"
    elif target == "handoff":
        filepath = config.MEMORY_DIR / "handoff.md"
    elif target == "state":
        filepath = config.OPERATIONS_DIR / "STATE.md"
    elif target == "context":
        filepath = config.OPERATIONS_DIR / "CONTEXT.md"
    else:
        return f"Unknown target: {target}"

    filepath.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if append else "w"
    with open(filepath, mode, encoding="utf-8") as f:
        f.write(content)

    # Trigger re-index if embedding index is available
    if _embedding_index is not None:
        try:
            _embedding_index.index_file(filepath)
        except Exception as e:
            logger.warning(f"Embedding re-index failed for {filepath.name}: {e}")

    return f"{'Appended to' if append else 'Wrote'} {filepath.name} ({len(content)} chars)."


TOOL_HANDLERS = {
    "memory_search": _memory_search,
    "memory_update": _memory_update,
}
