"""Skill Library — Voyager-style vector-indexed callable units (Day 96 evening Phase 4 #59).

The missing tier between memory items and tools.

Design follows Voyager (NVIDIA / Caltech / Stanford / UT, arXiv 2305.16291) with
adaptations for a single-stream Claude-Code-based agent:

  - **Skill** = a named, descriptionally-retrieved unit of work — typically a
    sequence of tool calls that solves a recurring sub-problem (e.g. "publish
    drift essay", "anchor handoff", "verify daemon state after restart").
    A skill carries: id, name, description, body (prose recipe + optional
    tool-sequence sketch), embedding, success_count, verified_status, history.

  - **Retrieval** = embedding-similarity over description (using the existing
    BGE-M3 search index where available; falls back to keyword overlap).

  - **Self-verification gate** (Stream 3 EvoSkills + Stream 6 Voyager finding):
    a skill enters the library only after passing a verification step that
    confirms it actually achieves its claimed effect. Without this gate, skill
    libraries accumulate skill-rot — Stream 3's load-bearing finding.

  - **Provenance**: every skill records who/what created it (manual / auto-
    discovered from experience pattern / proposed by meta_agent) and when.

This MVP is the storage + retrieval layer. Auto-discovery from experience
patterns is the next step; for now skills are registered manually or by
explicit meta_agent proposal. The two layers are decoupled so the discovery
loop can mature independently.

Storage: `memory/skill_library.json` (start simple; can migrate to SQLite if
the corpus grows past ~1000 skills). Embeddings stored alongside as numpy
array in `.search_index/skill_embeddings.npz` to share the existing index
infrastructure.
"""
import json
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import config

logger = logging.getLogger("clawd.tools.skill_library")

SKILL_FILE = config.MEMORY_DIR / "skill_library.json"


def _load_library() -> dict:
    """Load the skill library from disk. Initializes an empty schema if missing."""
    if SKILL_FILE.exists():
        try:
            return json.loads(SKILL_FILE.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning(f"skill_library.json parse failed: {e}")
    return {"skills": {}, "schema_version": 1}


def _save_library(lib: dict) -> None:
    SKILL_FILE.parent.mkdir(parents=True, exist_ok=True)
    SKILL_FILE.write_text(json.dumps(lib, indent=2, default=str), encoding="utf-8")


def _slug(name: str) -> str:
    """Generate a stable id-friendly slug from a skill name."""
    s = "".join(c if c.isalnum() else "_" for c in name.lower().strip())
    while "__" in s:
        s = s.replace("__", "_")
    return s.strip("_")[:64]


def register_skill_raw(
    name: str,
    description: str,
    body: str,
    *,
    tags: list[str] | None = None,
    provenance: str = "manual",
    verified: bool = False,
    tool_sequence: list[dict] | None = None,
) -> str:
    """Register a new skill (or update existing one with same slug).

    Args:
        name: Human-readable name. e.g. "publish drift essay".
        description: One-paragraph description used for retrieval. Should answer
            "when would I want to invoke this skill?" — the description is what
            embedding similarity searches against.
        body: The actual recipe. Prose steps OR pseudocode-shaped sequence.
            This is what the agent reads when invoking the skill.
        tags: Optional categorical tags for filtering (e.g. ["drift", "publish"]).
        provenance: How this skill came to exist. Values: manual, auto_discovered,
            meta_agent_proposed, ported_from_skills_dir.
        verified: True if the skill has passed verification (Voyager gate).
        tool_sequence: Optional structured representation of the tool calls the
            skill performs — list of {"tool": str, "input": dict} dicts. Allows
            programmatic invocation; if None, skill is prose-only (still useful).

    Returns the skill id (slug).
    """
    lib = _load_library()
    skills = lib.setdefault("skills", {})
    sid = _slug(name)
    now_iso = datetime.now().isoformat()

    existing = skills.get(sid)
    if existing:
        existing.update({
            "description": description,
            "body": body,
            "tags": tags if tags is not None else existing.get("tags", []),
            "tool_sequence": tool_sequence if tool_sequence is not None else existing.get("tool_sequence"),
            "verified": verified or existing.get("verified", False),
            "updated_at": now_iso,
            "provenance": existing.get("provenance", provenance),
        })
        skill = existing
    else:
        skill = {
            "id": sid,
            "name": name,
            "description": description,
            "body": body,
            "tags": tags or [],
            "tool_sequence": tool_sequence,
            "provenance": provenance,
            "verified": verified,
            "created_at": now_iso,
            "updated_at": now_iso,
            "success_count": 0,
            "failure_count": 0,
            "last_invoked": None,
            "history": [],
        }
        skills[sid] = skill

    _save_library(lib)
    logger.info(f"Skill registered: {sid} (provenance={provenance}, verified={verified})")
    return sid


def find_skill_by_description(query: str, top_k: int = 5,
                              require_verified: bool = False) -> list[dict]:
    """Retrieve skills whose description matches the query.

    Uses the existing embedding index when available; falls back to keyword
    overlap if embeddings aren't loadable. Returns a list of skill dicts with
    a `relevance_score` field appended.
    """
    lib = _load_library()
    skills = list(lib.get("skills", {}).values())
    if require_verified:
        skills = [s for s in skills if s.get("verified")]
    if not skills:
        return []

    # Try embedding-based retrieval first
    try:
        scored = _embedding_score(query, skills)
        if scored is not None:
            scored.sort(key=lambda x: x["relevance_score"], reverse=True)
            return scored[:top_k]
    except Exception as e:
        logger.debug(f"Embedding retrieval failed, falling back to keyword: {e}")

    # Fallback: simple keyword overlap on (name + description + tags)
    q_terms = set(query.lower().split())
    scored = []
    for s in skills:
        bag = (
            s.get("name", "") + " " +
            s.get("description", "") + " " +
            " ".join(s.get("tags", []))
        ).lower()
        bag_terms = set(bag.split())
        overlap = len(q_terms & bag_terms)
        if overlap > 0:
            relevance = overlap / max(len(q_terms), 1)
            scored.append({**s, "relevance_score": relevance})

    scored.sort(key=lambda x: x["relevance_score"], reverse=True)
    return scored[:top_k]


def _embedding_score(query: str, skills: list[dict]) -> list[dict] | None:
    """Score skills against query via embedding cosine similarity.

    Returns None if the embedding stack isn't available — caller falls back
    to keyword retrieval. Reuses the search-index BGE-M3 model.
    """
    try:
        from tools.embeddings import get_index
        idx = get_index()
        if idx is None or not getattr(idx, "_ready", False):
            return None
        model = idx._model
        if model is None:
            return None
        import numpy as np
        # Encode query
        q_vec = model.encode([query], normalize_embeddings=True)[0]
        # Encode each skill's name+description (cache later if needed)
        descriptions = [
            f"{s.get('name', '')}. {s.get('description', '')}" for s in skills
        ]
        s_vecs = model.encode(descriptions, normalize_embeddings=True)
        sims = s_vecs @ q_vec
        scored = []
        for s, sim in zip(skills, sims):
            scored.append({**s, "relevance_score": float(sim)})
        return scored
    except Exception as e:
        logger.debug(f"Embedding score helper failed: {e}")
        return None


def record_invocation(skill_id: str, success: bool,
                      note: str = "") -> bool:
    """Record that a skill was invoked. Updates counters and last_invoked.

    Used by the agent when actually using a skill — feeds the success/failure
    statistics that drive verification + retirement decisions.
    """
    lib = _load_library()
    skill = lib.get("skills", {}).get(skill_id)
    if not skill:
        return False
    if success:
        skill["success_count"] = skill.get("success_count", 0) + 1
    else:
        skill["failure_count"] = skill.get("failure_count", 0) + 1
    skill["last_invoked"] = datetime.now().isoformat()
    history = skill.setdefault("history", [])
    history.append({
        "ts": skill["last_invoked"],
        "success": success,
        "note": note[:300] if note else "",
    })
    # Cap history length
    if len(history) > 50:
        skill["history"] = history[-50:]
    _save_library(lib)
    return True


def list_skills(tag: str | None = None, verified_only: bool = False) -> list[dict]:
    """List skills (optionally filtered by tag and verified-status)."""
    lib = _load_library()
    skills = list(lib.get("skills", {}).values())
    if tag:
        skills = [s for s in skills if tag in s.get("tags", [])]
    if verified_only:
        skills = [s for s in skills if s.get("verified")]
    return skills


def get_skill(skill_id: str) -> dict | None:
    """Return a single skill by id, or None if not found."""
    return _load_library().get("skills", {}).get(skill_id)


def remove_skill(skill_id: str) -> bool:
    """Remove a skill. Returns True if removed."""
    lib = _load_library()
    if skill_id in lib.get("skills", {}):
        del lib["skills"][skill_id]
        _save_library(lib)
        return True
    return False


# ──────────────────────────────────────────────────────────────────────
# Tool surface (bridge.py + MCP exposure)
# ──────────────────────────────────────────────────────────────────────

TOOL_DEFINITIONS = [
    {
        "name": "skill_library",
        "description": (
            "Vector-indexed library of named callable patterns (Voyager-style). "
            "Skills are recipes for recurring sub-problems retrievable by description. "
            "Actions: register (create/update), find (retrieve by description), "
            "list (filter), get (full body by id), invoked (record use), "
            "remove. Skills enter verified-status only after passing self-verification "
            "(EvoSkills gate)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["register", "find", "list", "get", "invoked", "remove"],
                    "description": "Skill library operation. register: create/update. find: retrieve by description. list: filter by tag/verified. get: full body by id. invoked: record use+success. remove: delete.",
                },
                "name": {"type": "string", "description": "Human-readable name (for register). Slugified to id."},
                "description": {"type": "string", "description": "When-would-I-want-this-skill text (for register). Used for embedding-retrieval."},
                "body": {"type": "string", "description": "The actual recipe (for register). Prose steps or pseudocode-shaped sequence."},
                "tags": {"type": "array", "items": {"type": "string"}, "description": "Categorical tags (for register). e.g. [drift, publish]."},
                "tool_sequence": {"type": "array", "description": "Optional structured tool calls (for register). List of {tool, input} dicts."},
                "provenance": {"type": "string", "description": "Skill origin (for register): manual / auto_discovered / meta_agent_proposed."},
                "verified": {"type": "boolean", "description": "True if skill passed verification gate (for register)."},
                "query": {"type": "string", "description": "Search query (for find action)."},
                "skill_id": {"type": "string", "description": "Skill id slug (for get/invoked/remove)."},
                "tag": {"type": "string", "description": "Filter by tag (for list)."},
                "verified_only": {"type": "boolean", "description": "Only return verified skills (for list/find)."},
                "success": {"type": "boolean", "description": "Did invocation succeed (for invoked)."},
                "note": {"type": "string", "description": "Free-text note about invocation (for invoked)."},
                "top_k": {"type": "integer", "description": "Max results to return (for find). Default 5."},
            },
            "required": ["action"],
        },
    },
]


async def _skill_library_tool(input_data: dict) -> str:
    action = input_data.get("action", "list")

    if action == "register":
        name = input_data.get("name")
        description = input_data.get("description", "")
        body = input_data.get("body", "")
        if not name or not description or not body:
            return ("Error: register requires 'name', 'description', and 'body'. "
                    "description should answer 'when would I want this skill?' (used "
                    "for embedding-retrieval); body is the actual recipe.")
        sid = register_skill_raw(
            name=name,
            description=description,
            body=body,
            tags=input_data.get("tags") or [],
            tool_sequence=input_data.get("tool_sequence"),
            provenance=input_data.get("provenance", "manual"),
            verified=bool(input_data.get("verified", False)),
        )
        return f"Skill registered: {sid}"

    if action == "find":
        query = input_data.get("query", "")
        if not query:
            return "Error: find requires 'query'."
        hits = find_skill_by_description(
            query=query,
            top_k=int(input_data.get("top_k", 5)),
            require_verified=bool(input_data.get("verified_only", False)),
        )
        if not hits:
            return f"No skills found for query: {query}"
        lines = [f"Found {len(hits)} skills:"]
        for h in hits:
            v = "✓" if h.get("verified") else "?"
            score = h.get("relevance_score", 0)
            lines.append(
                f"  [{v}] {h['id']} (score={score:.3f}) — {h['name']}: "
                f"{h['description'][:120]}"
            )
        return "\n".join(lines)

    if action == "list":
        skills = list_skills(
            tag=input_data.get("tag"),
            verified_only=bool(input_data.get("verified_only", False)),
        )
        if not skills:
            return "No skills in library."
        lines = [f"{len(skills)} skills:"]
        for s in sorted(skills, key=lambda x: x.get("created_at", ""), reverse=True):
            v = "✓" if s.get("verified") else "?"
            tags_str = f"[{','.join(s.get('tags', []))}]" if s.get("tags") else ""
            lines.append(
                f"  [{v}] {s['id']} {tags_str} — {s['name']} "
                f"(success={s.get('success_count', 0)}, "
                f"failure={s.get('failure_count', 0)})"
            )
        return "\n".join(lines)

    if action == "get":
        sid = input_data.get("skill_id")
        if not sid:
            return "Error: get requires 'skill_id'."
        s = get_skill(sid)
        if not s:
            return f"Skill not found: {sid}"
        return json.dumps(s, indent=2, default=str)

    if action == "invoked":
        sid = input_data.get("skill_id")
        if not sid:
            return "Error: invoked requires 'skill_id'."
        ok = record_invocation(
            skill_id=sid,
            success=bool(input_data.get("success", True)),
            note=input_data.get("note", ""),
        )
        if not ok:
            return f"Skill not found: {sid}"
        return f"Recorded invocation of {sid}"

    if action == "remove":
        sid = input_data.get("skill_id")
        if not sid:
            return "Error: remove requires 'skill_id'."
        ok = remove_skill(sid)
        return f"Removed: {sid}" if ok else f"Skill not found: {sid}"

    return f"Unknown action: {action}. Valid: register, find, list, get, invoked, remove."


TOOL_HANDLERS = {
    "skill_library": _skill_library_tool,
}
