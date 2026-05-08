"""Knowledge Graph — Associative memory through entities and relations.

Stores entities (people, projects, concepts, tools) and edges (relationships)
in a bi-temporal JSON graph. Supports traversal, querying, and auto-population
from memory consolidation.
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import config

logger = logging.getLogger("clawd.tools.knowledge_graph")

KG_FILE = config.MEMORY_DIR / "knowledge_graph.json"

_DEFAULT_GRAPH = {
    "entities": {},
    "edges": [],
}

TOOL_DEFINITIONS = [
    {
        "name": "knowledge_graph",
        "description": (
            "Manage Clawd's knowledge graph — a network of entities (people, projects, concepts, tools) "
            "and their relationships. Use for associative reasoning, finding connections, and tracking "
            "how concepts relate to each other."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["add_entity", "add_edge", "query", "traverse", "list"],
                    "description": (
                        "add_entity: add a new entity. "
                        "add_edge: add a relationship between entities. "
                        "query: search entities by type or keyword. "
                        "traverse: follow edges from an entity. "
                        "list: list all entities or edges."
                    ),
                },
                "entity": {
                    "type": "string",
                    "description": "Entity name/ID (for add_entity, query, traverse).",
                },
                "entity_type": {
                    "type": "string",
                    "enum": ["person", "project", "concept", "tool", "organization", "location", "event"],
                    "description": "Entity type (for add_entity, query filter).",
                },
                "properties": {
                    "type": "object",
                    "description": "Entity properties dict (for add_entity). Arbitrary key-value pairs.",
                },
                "relation": {
                    "type": "string",
                    "description": "Relationship type (for add_edge). Examples: 'uses', 'created_by', 'depends_on', 'related_to'.",
                },
                "target": {
                    "type": "string",
                    "description": "Target entity name/ID (for add_edge).",
                },
                "depth": {
                    "type": "integer",
                    "description": "Traversal depth (for traverse). Default: 2.",
                },
                "enrich": {
                    "type": "boolean",
                    "description": "Include entity properties in traverse output (default false).",
                },
                "query_text": {
                    "type": "string",
                    "description": "Search query (for query action).",
                },
                "list_type": {
                    "type": "string",
                    "enum": ["entities", "edges", "all"],
                    "description": "What to list (for list action). Default: entities.",
                },
            },
            "required": ["action"],
        },
    },
]


def _load_graph() -> dict:
    """Load knowledge graph from disk."""
    if KG_FILE.exists():
        try:
            return json.loads(KG_FILE.read_text(encoding="utf-8"))
        except Exception as e:
            logger.debug(f"Failed to load knowledge graph, using empty graph: {e}")
    return {"entities": {}, "edges": []}


def _save_graph(graph: dict):
    """Save knowledge graph to disk."""
    KG_FILE.parent.mkdir(parents=True, exist_ok=True)
    KG_FILE.write_text(json.dumps(graph, indent=2, default=str), encoding="utf-8")


def add_entity_raw(name: str, entity_type: str, properties: dict = None) -> str:
    """Add entity programmatically (used by consolidation auto-population)."""
    graph = _load_graph()
    entities = graph.setdefault("entities", {})
    entity_id = name.lower().replace(" ", "_")

    if entity_id in entities:
        # Update existing entity
        entities[entity_id]["properties"].update(properties or {})
        entities[entity_id]["updated_at"] = datetime.now().isoformat()
    else:
        entities[entity_id] = {
            "name": name,
            "type": entity_type,
            "properties": properties or {},
            "created_at": datetime.now().isoformat(),
            "valid_from": datetime.now().isoformat(),
        }

    _save_graph(graph)
    return entity_id


def add_edge_raw(from_entity: str, to_entity: str, relation: str,
                 valid_from: str | None = None) -> bool:
    """Add edge programmatically with bi-temporal semantics (Graphiti pattern, Day 96 evening).

    Bi-temporal model:
      - `ingested_at`: when WE learned about this fact (always = now on insert)
      - `valid_from` / `valid_to`: when the fact was/is true IN THE WORLD
        (defaults to ingested_at if not specified — i.e. "we assume the world
        became true when we noticed it" unless told otherwise)

    On contradiction, the existing edge is INVALIDATED (its valid_to is set
    to now) and the new edge is added. Truth is allowed to change; history
    is preserved.

    Returns True on insert/upgrade, False only if a true logical contradiction
    cannot be reconciled.
    """
    graph = _load_graph()
    edges = graph.setdefault("edges", [])
    entities = graph.get("entities", {})

    from_id = from_entity.lower().replace(" ", "_")
    to_id = to_entity.lower().replace(" ", "_")
    now_iso = datetime.now().isoformat()
    valid_from = valid_from or now_iso

    # Check for contradicting edges (active only)
    contradictions = {
        "uses": "does_not_use",
        "depends_on": "independent_of",
        "created_by": "not_created_by",
    }
    reverse_contradictions = {v: k for k, v in contradictions.items()}
    all_contradictions = {**contradictions, **reverse_contradictions}

    contra_rel = all_contradictions.get(relation)
    if contra_rel:
        for edge in edges:
            if (edge["from"] == from_id and edge["to"] == to_id and
                    edge.get("relation") == contra_rel and
                    edge.get("valid_to") is None):
                # INVALIDATE the existing contradicting edge (Graphiti pattern)
                # Old behavior was to reject; new behavior is to record that
                # truth changed at time `now`. Old edges remain queryable
                # for point-in-time analysis.
                edge["valid_to"] = now_iso
                edge["invalidated_by"] = f"new_edge_{from_id}_{relation}_{to_id}_{now_iso}"
                logger.info(
                    f"Edge invalidated by truth-change: "
                    f"{from_id} --{contra_rel}--> {to_id} replaced by --{relation}-->"
                )
                # Fall through to insert the new edge

    # Check for duplicate active edge (same from/to/relation with valid_to=None)
    for edge in edges:
        if (edge["from"] == from_id and edge["to"] == to_id and
                edge.get("relation") == relation and edge.get("valid_to") is None):
            return True  # Already exists, idempotent

    edges.append({
        "from": from_id,
        "to": to_id,
        "relation": relation,
        "valid_from": valid_from,    # when fact was/is true in world
        "valid_to": None,             # None = currently valid
        "ingested_at": now_iso,       # when we learned it (Graphiti pattern)
    })

    _save_graph(graph)
    return True


def add_edges_batch(edges: list[tuple[str, str, str]]) -> int:
    """Add multiple edges in a single load/save cycle (avoids N reads/writes).

    Args:
        edges: List of (from_entity, to_entity, relation) tuples.

    Returns:
        Number of edges actually added (excluding duplicates/contradictions).
    """
    graph = _load_graph()
    existing_edges = graph.setdefault("edges", [])
    added = 0

    # Build a set of existing active edge signatures for fast duplicate check
    existing_sigs = set()
    for edge in existing_edges:
        if edge.get("valid_to") is None:
            sig = (edge["from"], edge["to"], edge.get("relation", ""))
            existing_sigs.add(sig)

    contradictions = {
        "uses": "does_not_use",
        "depends_on": "independent_of",
        "created_by": "not_created_by",
    }
    reverse_contradictions = {v: k for k, v in contradictions.items()}
    all_contradictions = {**contradictions, **reverse_contradictions}

    for from_entity, to_entity, relation in edges:
        from_id = from_entity.lower().replace(" ", "_")
        to_id = to_entity.lower().replace(" ", "_")
        now_iso = datetime.now().isoformat()

        sig = (from_id, to_id, relation)
        if sig in existing_sigs:
            continue  # Already exists

        # Check for contradiction — INVALIDATE old edge (Graphiti pattern)
        # rather than rejecting new edge. Truth-change is a real event.
        contra_rel = all_contradictions.get(relation)
        if contra_rel and (from_id, to_id, contra_rel) in existing_sigs:
            for edge in existing_edges:
                if (edge["from"] == from_id and edge["to"] == to_id and
                        edge.get("relation") == contra_rel and
                        edge.get("valid_to") is None):
                    edge["valid_to"] = now_iso
                    edge["invalidated_by"] = f"batch_truth_change_{now_iso}"
                    existing_sigs.discard((from_id, to_id, contra_rel))
                    logger.info(f"Batch: edge invalidated, truth changed: "
                                f"{from_id} --{contra_rel}--> {to_id}")
                    break

        existing_edges.append({
            "from": from_id,
            "to": to_id,
            "relation": relation,
            "valid_from": now_iso,    # when fact is/was true in world
            "valid_to": None,          # None = currently valid
            "ingested_at": now_iso,    # when we learned it (Graphiti)
        })
        existing_sigs.add(sig)
        added += 1

    if added > 0:
        _save_graph(graph)
    return added


def link_note_to_sources(note_id: str, source_ids: list[str]):
    """Create bidirectional KG edges between a semantic note and its source items/episodes."""
    edges = []
    for source_id in source_ids:
        edges.append((note_id, str(source_id), "derived_from"))
        edges.append((str(source_id), note_id, "contributes_to"))
    add_edges_batch(edges)


def add_artifact_entity(
    artifact_id: str,
    name: str,
    artifact_type: str,
    generation: int = 0,
    fitness: dict = None,
    parents: list[str] = None,
):
    """Add an EAC artifact as an entity in the knowledge graph."""
    properties = {
        "artifact_type": artifact_type,
        "generation": generation,
        "fitness": fitness or {},
        "parents": parents or [],
    }
    add_entity_raw(name or artifact_id, "artifact", properties)


def add_mutation_edge(parent_id: str, child_id: str, mutation_type: str):
    """Add a mutation edge between parent and child artifacts."""
    add_edge_raw(parent_id, child_id, f"mutated_to:{mutation_type}")


def add_crossover_edge(parent_a: str, parent_b: str, child_id: str):
    """Add crossover edges from both parents to child artifact."""
    add_edge_raw(parent_a, child_id, "crossover_parent")
    add_edge_raw(parent_b, child_id, "crossover_parent")


async def _knowledge_graph(input_data: dict) -> str:
    """Handle knowledge graph tool calls."""
    action = input_data["action"]
    graph = _load_graph()

    if action == "add_entity":
        name = input_data.get("entity", "")
        if not name:
            return "Error: entity name required."
        entity_type = input_data.get("entity_type", "concept")
        properties = input_data.get("properties", {})
        entity_id = add_entity_raw(name, entity_type, properties)
        return f"Entity '{name}' ({entity_type}) added/updated as '{entity_id}'."

    elif action == "add_edge":
        from_entity = input_data.get("entity", "")
        to_entity = input_data.get("target", "")
        relation = input_data.get("relation", "related_to")
        if not from_entity or not to_entity:
            return "Error: entity and target required for add_edge."
        success = add_edge_raw(from_entity, to_entity, relation)
        if success:
            return f"Edge added: {from_entity} --{relation}--> {to_entity}"
        return f"Edge NOT added: contradicting relationship exists for {from_entity} --{relation}--> {to_entity}"

    elif action == "query":
        entity_type = input_data.get("entity_type")
        query = input_data.get("query_text", input_data.get("entity", "")).lower()
        entities = graph.get("entities", {})

        results = []
        for eid, e in entities.items():
            if entity_type and e.get("type") != entity_type:
                continue
            if query:
                searchable = f"{eid} {e.get('name', '')} {json.dumps(e.get('properties', {}))}".lower()
                if query not in searchable:
                    continue
            results.append(e)

        if not results:
            return f"No entities found for query: {query or entity_type}"

        lines = [f"Found {len(results)} entities:"]
        for e in results[:20]:
            props = e.get("properties", {})
            props_str = f" — {json.dumps(props)[:100]}" if props else ""
            lines.append(f"  [{e.get('type', '?')}] {e.get('name', '?')}{props_str}")
        return "\n".join(lines)

    elif action == "traverse":
        entity = input_data.get("entity", "").lower().replace(" ", "_")
        depth = int(input_data.get("depth", 2))
        enrich = input_data.get("enrich", False)
        if not entity:
            return "Error: entity required for traverse."

        entities = graph.get("entities", {})
        edges = graph.get("edges", [])

        if entity not in entities:
            return f"Entity '{entity}' not found in knowledge graph."

        # BFS traversal
        visited = set()
        queue = [(entity, 0)]
        results = []

        while queue:
            current, d = queue.pop(0)
            if current in visited or d > depth:
                continue
            visited.add(current)

            e = entities.get(current, {})
            indent = "  " * d
            line = f"{indent}[{e.get('type', '?')}] {e.get('name', current)}"
            if enrich and e.get("properties"):
                props_str = json.dumps(e["properties"])[:200]
                line += f" | {props_str}"
            results.append(line)

            # Find connected edges
            for edge in edges:
                if edge.get("valid_to") is not None:
                    continue  # Skip expired edges
                if edge["from"] == current and edge["to"] not in visited:
                    results.append(f"{indent}  --{edge['relation']}--> {edge['to']}")
                    queue.append((edge["to"], d + 1))
                elif edge["to"] == current and edge["from"] not in visited:
                    results.append(f"{indent}  <--{edge['relation']}-- {edge['from']}")
                    queue.append((edge["from"], d + 1))

        if not results:
            return f"No connections found for entity '{entity}'."
        return f"Knowledge graph traversal from '{entity}' (depth {depth}):\n" + "\n".join(results)

    elif action == "list":
        list_type = input_data.get("list_type", "entities")
        entities = graph.get("entities", {})
        edges = graph.get("edges", [])

        if list_type in ("entities", "all"):
            lines = [f"Entities ({len(entities)}):"]
            for eid, e in sorted(entities.items()):
                lines.append(f"  [{e.get('type', '?')}] {e.get('name', eid)}")
        else:
            lines = []

        if list_type in ("edges", "all"):
            active_edges = [e for e in edges if e.get("valid_to") is None]
            lines.append(f"\nEdges ({len(active_edges)} active):")
            for edge in active_edges[:30]:
                lines.append(f"  {edge['from']} --{edge.get('relation', '?')}--> {edge['to']}")

        return "\n".join(lines) if lines else "Knowledge graph is empty."

    return f"Unknown knowledge_graph action: {action}"


TOOL_HANDLERS = {
    "knowledge_graph": _knowledge_graph,
}
