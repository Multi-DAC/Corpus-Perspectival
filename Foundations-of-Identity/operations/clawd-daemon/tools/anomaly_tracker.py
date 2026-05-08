"""Research Anomaly Tracker — First-class tracking of unexplained observations.

Anomalies are the highest-value objects in a research program. They represent
things that don't fit current models — the gaps where new understanding lives.

Each anomaly is a typed entry with:
- observation: what was seen
- domain: which research area
- candidate_explanations: hypotheses that might explain it
- status: open, explained, dissolved, promoted (became a finding)
- confidence: how confident we are the anomaly is real (not noise)
- connections: links to other anomalies or findings

The tracker maintains an explicit list that can be queried during creative
drives for hypothesis generation, and during consolidation for synthesis.
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import uuid4

import config

logger = logging.getLogger("clawd.tools.anomaly_tracker")

ANOMALY_FILE = config.MEMORY_DIR / "research_anomalies.json"


def _load_anomalies() -> list:
    if ANOMALY_FILE.exists():
        try:
            return json.loads(ANOMALY_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def _save_anomalies(anomalies: list):
    ANOMALY_FILE.parent.mkdir(parents=True, exist_ok=True)
    ANOMALY_FILE.write_text(
        json.dumps(anomalies, indent=2, default=str), encoding="utf-8"
    )


def add_anomaly(
    observation: str,
    domain: str,
    confidence: float = 0.7,
    candidate_explanations: list[str] = None,
    connections: list[str] = None,
) -> dict:
    """Record a new research anomaly — something that doesn't fit current models."""
    anomalies = _load_anomalies()
    entry = {
        "id": str(uuid4())[:8],
        "observation": observation,
        "domain": domain,
        "confidence": confidence,
        "status": "open",
        "candidate_explanations": candidate_explanations or [],
        "connections": connections or [],
        "created": datetime.now().isoformat(),
        "updated": datetime.now().isoformat(),
        "resolution": None,
    }
    anomalies.append(entry)
    _save_anomalies(anomalies)
    logger.info(f"Anomaly recorded: [{entry['id']}] {observation[:80]}")
    return entry


def update_anomaly(
    anomaly_id: str,
    status: Optional[str] = None,
    new_explanation: Optional[str] = None,
    resolution: Optional[str] = None,
    confidence: Optional[float] = None,
    connection: Optional[str] = None,
) -> Optional[dict]:
    """Update an existing anomaly with new information."""
    anomalies = _load_anomalies()
    for a in anomalies:
        if a["id"] == anomaly_id:
            if status:
                a["status"] = status
            if new_explanation:
                a["candidate_explanations"].append(new_explanation)
            if resolution:
                a["resolution"] = resolution
                a["status"] = "explained"
            if confidence is not None:
                a["confidence"] = confidence
            if connection:
                a["connections"].append(connection)
            a["updated"] = datetime.now().isoformat()
            _save_anomalies(anomalies)
            return a
    return None


def list_anomalies(
    status: Optional[str] = None,
    domain: Optional[str] = None,
    min_confidence: float = 0.0,
) -> list:
    """List anomalies, optionally filtered by status, domain, or confidence."""
    anomalies = _load_anomalies()
    results = anomalies
    if status:
        results = [a for a in results if a["status"] == status]
    if domain:
        results = [a for a in results if a["domain"] == domain]
    if min_confidence > 0:
        results = [a for a in results if a["confidence"] >= min_confidence]
    return results


def get_open_anomalies_summary() -> str:
    """Get a brief summary of all open anomalies for use in drive prompts."""
    open_anomalies = list_anomalies(status="open")
    if not open_anomalies:
        return "No open research anomalies."
    lines = [f"OPEN RESEARCH ANOMALIES ({len(open_anomalies)}):"]
    for a in open_anomalies:
        expl = f" ({len(a['candidate_explanations'])} candidate explanations)" if a["candidate_explanations"] else ""
        lines.append(
            f"  [{a['id']}] [{a['domain']}] {a['observation'][:100]}"
            f" (confidence: {a['confidence']:.1f}){expl}"
        )
    return "\n".join(lines)


def export_to_markdown() -> str:
    """Export current anomalies state to memory/anomalies_auto.md.

    Day 96 evening Phase 4 #12 — give the structured anomaly tracker a
    human-readable mirror. Does NOT touch anomalies.md (which is hand-
    curated and load-bearing). The _auto.md is the tool-side view;
    anomalies.md remains canonical for prose-shaped entries (A85, etc.).
    """
    anomalies = _load_anomalies()
    if not anomalies:
        return "No anomalies in tracker."

    md_path = config.MEMORY_DIR / "anomalies_auto.md"
    by_status = {}
    for a in anomalies:
        s = a.get("status", "open")
        by_status.setdefault(s, []).append(a)

    lines = [
        "# Anomalies (auto-tracked)",
        "",
        f"*Auto-generated from `research_anomalies.json` on "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M PST')}.*",
        "*Structured-tool mirror; the prose-shaped canonical anomalies "
        "live in `anomalies.md`.*",
        "",
        f"**Counts:** "
        + " / ".join(f"{s}: {len(by_status.get(s, []))}"
                     for s in ("open", "explained", "dissolved", "promoted")),
        "",
    ]
    for status in ("open", "promoted", "explained", "dissolved"):
        bucket = by_status.get(status, [])
        if not bucket:
            continue
        lines.append(f"## {status.upper()} ({len(bucket)})")
        lines.append("")
        for a in sorted(bucket, key=lambda x: x.get("created", ""), reverse=True):
            lines.append(f"### `{a['id']}` — {a.get('domain', '?')}: "
                         f"{a['observation'][:100]}")
            lines.append("")
            lines.append(f"- **Confidence:** {a.get('confidence', 0):.2f}")
            lines.append(f"- **Created:** {a.get('created', '?')[:19]}")
            lines.append(f"- **Updated:** {a.get('updated', '?')[:19]}")
            if a.get("candidate_explanations"):
                lines.append(f"- **Candidate explanations:**")
                for e in a["candidate_explanations"]:
                    lines.append(f"  - {e}")
            if a.get("resolution"):
                lines.append(f"- **Resolution:** {a['resolution']}")
            if a.get("connections"):
                lines.append(f"- **Connections:** {', '.join(a['connections'])}")
            lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return f"Exported {len(anomalies)} anomalies to {md_path}"


def synthesize_anomalies() -> list[dict]:
    """Look for connections between open anomalies across domains.

    Returns pairs of anomalies that might be related but haven't been
    explicitly connected. Used during consolidation/dream drives.
    """
    open_anomalies = list_anomalies(status="open")
    if len(open_anomalies) < 2:
        return []

    # Find anomalies in different domains that share no explicit connections
    suggestions = []
    for i, a in enumerate(open_anomalies):
        for j, b in enumerate(open_anomalies):
            if j <= i:
                continue
            if a["domain"] != b["domain"] and b["id"] not in a.get("connections", []):
                suggestions.append({
                    "anomaly_a": a,
                    "anomaly_b": b,
                    "reason": f"Cross-domain ({a['domain']} x {b['domain']}): "
                              f"no explicit connection yet",
                })
    return suggestions


# ──────────────────────────────────────────────────────────────────────
# Tool surface (Day 96 evening Phase 4 #12 — bridge.py + MCP exposure)
# ──────────────────────────────────────────────────────────────────────

TOOL_DEFINITIONS = [
    {
        "name": "anomaly_tracker",
        "description": (
            "First-class tracking of unexplained observations. Anomalies are "
            "the highest-value research objects — the gaps where new understanding "
            "lives. Actions: add (record new), update (status/explanation/"
            "resolution), list (filtered by status/domain/confidence), summary "
            "(open anomalies brief), synthesize (find cross-domain connection "
            "candidates), export_md (write human-readable mirror to "
            "anomalies_auto.md)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["add", "update", "list", "summary", "synthesize", "export_md"],
                    "description": "Anomaly tracker operation. add: record new. update: revise status/explanation/resolution/confidence. list: filtered by status/domain/min_confidence. summary: brief view of open anomalies. synthesize: cross-domain connection candidates. export_md: write human-readable mirror to anomalies_auto.md.",
                },
                "observation": {"type": "string", "description": "What was observed (for add). The thing that doesn't fit current models."},
                "domain": {"type": "string", "description": "Research domain (for add/list). e.g. physics, infrastructure, biology."},
                "confidence": {"type": "number", "description": "0.0-1.0 (for add/update). How confident the anomaly is real (not noise). Default 0.7."},
                "candidate_explanations": {"type": "array", "items": {"type": "string"}, "description": "Hypotheses that might explain (for add). Optional."},
                "anomaly_id": {"type": "string", "description": "Anomaly id (for update). 8-char slug from add."},
                "status": {"type": "string", "description": "For update: open/explained/dissolved/promoted. For list: filter by status."},
                "new_explanation": {"type": "string", "description": "Append to candidate_explanations (for update)."},
                "resolution": {"type": "string", "description": "How the anomaly was explained (for update). Sets status=explained."},
                "connection": {"type": "string", "description": "Append to connections list (for update). Reference to other anomaly id or finding."},
                "min_confidence": {"type": "number", "description": "Filter threshold (for list). Default 0.0."},
            },
            "required": ["action"],
        },
    },
]


async def _anomaly_tracker_tool(input_data: dict) -> str:
    import json as _json
    action = input_data.get("action", "summary")

    if action == "add":
        obs = input_data.get("observation")
        dom = input_data.get("domain")
        if not obs or not dom:
            return "Error: add requires 'observation' and 'domain'."
        entry = add_anomaly(
            observation=obs,
            domain=dom,
            confidence=float(input_data.get("confidence", 0.7)),
            candidate_explanations=input_data.get("candidate_explanations") or [],
        )
        # Auto-export to markdown after add (keeps mirror fresh)
        try:
            export_to_markdown()
        except Exception:
            pass
        return f"Anomaly added: [{entry['id']}] {obs[:80]}"

    if action == "update":
        aid = input_data.get("anomaly_id")
        if not aid:
            return "Error: update requires 'anomaly_id'."
        entry = update_anomaly(
            anomaly_id=aid,
            status=input_data.get("status"),
            new_explanation=input_data.get("new_explanation"),
            resolution=input_data.get("resolution"),
            confidence=input_data.get("confidence"),
            connection=input_data.get("connection"),
        )
        if entry is None:
            return f"Anomaly not found: {aid}"
        try:
            export_to_markdown()
        except Exception:
            pass
        return f"Anomaly updated: [{aid}] status={entry['status']}"

    if action == "list":
        items = list_anomalies(
            status=input_data.get("status"),
            domain=input_data.get("domain"),
            min_confidence=float(input_data.get("min_confidence", 0.0)),
        )
        if not items:
            return "No anomalies match filter."
        return _json.dumps(items, indent=2, default=str)

    if action == "summary":
        return get_open_anomalies_summary()

    if action == "synthesize":
        suggestions = synthesize_anomalies()
        if not suggestions:
            return "No cross-domain connection candidates found."
        return _json.dumps(suggestions, indent=2, default=str)

    if action == "export_md":
        return export_to_markdown()

    return f"Unknown action: {action}. Valid: add, update, list, summary, synthesize, export_md."


TOOL_HANDLERS = {
    "anomaly_tracker": _anomaly_tracker_tool,
}
