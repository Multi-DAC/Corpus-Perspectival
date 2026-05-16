"""kg_neighbors — focused 1-hop / 2-hop query over the knowledge graph.

After the Day 105 KG expansion (10 → 882+ entities), the existing
knowledge_graph.traverse action is too verbose for casual associative
use. This tool returns a structured neighborhood: incoming + outgoing
edges, grouped by relation type, optionally filtered by entity_type.

Use cases:
  - "What does the Coherence Principle anchor connect to?"
  - "Which Drift essays reference C15?"
  - "Show me all hypotheses derived from any corollary."
"""
import json
import logging
from typing import Any

import config

logger = logging.getLogger("clawd.tools.kg_neighbors")

KG_FILE = config.MEMORY_DIR / "knowledge_graph.json"

TOOL_DEFINITIONS = [
    {
        "name": "kg_neighbors",
        "description": (
            "Query the knowledge graph for an entity's neighborhood. Returns "
            "incoming + outgoing edges grouped by relation type. Use when you "
            "want to see what connects to X, or find all instances of relation R."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "entity": {
                    "type": "string",
                    "description": "Entity name or ID (case-insensitive substring match).",
                },
                "relation": {
                    "type": "string",
                    "description": "Optional: filter by specific relation type (e.g. 'derives', 'instance_of').",
                },
                "direction": {
                    "type": "string",
                    "enum": ["out", "in", "both"],
                    "description": "Edge direction. Default: both.",
                },
                "filter_type": {
                    "type": "string",
                    "description": "Optional: only return neighbors of this entity type.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max neighbors per direction. Default 30.",
                },
            },
            "required": ["entity"],
        },
    },
]


def _load_graph() -> dict:
    if not KG_FILE.exists():
        return {"entities": {}, "edges": []}
    try:
        return json.loads(KG_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        logger.warning(f"Failed to load KG: {e}")
        return {"entities": {}, "edges": []}


def _entity_id(name: str) -> str:
    return name.lower().replace(" ", "_")


def _resolve_entity(graph: dict, query: str) -> str | None:
    """Find an entity by exact ID, exact name, or substring match."""
    entities = graph.get("entities", {})
    qid = _entity_id(query)
    if qid in entities:
        return qid
    # Exact name match
    for eid, e in entities.items():
        if e.get("name", "").lower() == query.lower():
            return eid
    # Substring match
    matches = []
    for eid, e in entities.items():
        if query.lower() in e.get("name", "").lower() or query.lower() in eid:
            matches.append(eid)
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        # Prefer shortest (most specific) match
        matches.sort(key=lambda m: len(m))
        return matches[0]
    return None


async def _kg_neighbors_tool(input_data: dict[str, Any]) -> str:
    entity_query = input_data.get("entity", "").strip()
    if not entity_query:
        return "[Error: 'entity' required]"

    graph = _load_graph()
    entities = graph.get("entities", {})
    edges = graph.get("edges", [])

    eid = _resolve_entity(graph, entity_query)
    if not eid:
        return f"[No entity matches '{entity_query}']"
    e = entities.get(eid, {})
    ename = e.get("name", eid)

    direction = input_data.get("direction", "both")
    rel_filter = input_data.get("relation", "").strip()
    type_filter = input_data.get("filter_type", "").strip()
    limit = int(input_data.get("limit", 30))

    out_edges = []  # (relation, target_id)
    in_edges = []   # (relation, from_id)
    for edge in edges:
        from_id = edge.get("from", "")
        to_id = edge.get("to", "")
        rel = edge.get("relation", "")
        # Skip invalidated edges
        if edge.get("valid_to") and not isinstance(edge.get("valid_to"), dict):
            continue
        if rel_filter and rel != rel_filter:
            continue
        if from_id == eid:
            out_edges.append((rel, to_id))
        if to_id == eid:
            in_edges.append((rel, from_id))

    def _filter_by_type(edge_list):
        if not type_filter:
            return edge_list
        return [(r, n) for r, n in edge_list if entities.get(n, {}).get("type") == type_filter]

    out_edges = _filter_by_type(out_edges)[:limit]
    in_edges = _filter_by_type(in_edges)[:limit]

    # Group by relation
    def _group(elist):
        groups: dict[str, list[str]] = {}
        for rel, nid in elist:
            n = entities.get(nid, {})
            label = n.get("name", nid)
            etype = n.get("type", "?")
            groups.setdefault(rel, []).append(f"[{etype}] {label}")
        return groups

    out_g = _group(out_edges)
    in_g = _group(in_edges)

    lines = [f"# {ename}  [{e.get('type', '?')}]"]
    props = e.get("properties", {})
    if props:
        prop_summary = ", ".join(f"{k}={v}" for k, v in list(props.items())[:5])
        lines.append(f"  properties: {prop_summary}")

    if direction in ("out", "both"):
        if out_g:
            lines.append(f"\n## Outgoing ({sum(len(v) for v in out_g.values())} edges)")
            for rel, targets in sorted(out_g.items()):
                lines.append(f"  --{rel}-->")
                for t in targets[:limit]:
                    lines.append(f"    {t}")
        elif direction == "out":
            lines.append("\n(no outgoing edges)")

    if direction in ("in", "both"):
        if in_g:
            lines.append(f"\n## Incoming ({sum(len(v) for v in in_g.values())} edges)")
            for rel, sources in sorted(in_g.items()):
                lines.append(f"  <--{rel}--")
                for s in sources[:limit]:
                    lines.append(f"    {s}")
        elif direction == "in":
            lines.append("\n(no incoming edges)")

    if not out_g and not in_g:
        lines.append("\n(entity has no edges)")

    return "\n".join(lines)


TOOL_HANDLERS = {
    "kg_neighbors": _kg_neighbors_tool,
}
