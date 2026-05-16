"""Corpus-scale structural KG extractor — regex-based, fast, deterministic.

Walks the canonical structural surfaces and adds entities + edges to
memory/knowledge_graph.json without needing an LLM. Covers:

- Drift essay titles (filename → essay entity)
- Mirror entries from palace/southeast/mirror.md (numbered ## headings)
- Bridges from palace/basement/README.md (M1-Mx + L-x + #N entries)
- Master Glossary terms (from Library/Master-Glossary/registers/*.md)
- Library volume section headers (Coherence Principle TOC, Companion TOC)
- Daily-log entries (recent N days as event entities)
- Cognitive chain domains + outcomes from memory/cognitive_chains.json
- Calibration_log patterns + instances

Designed to be re-runnable; entities are upserted (no duplicates).
"""
import io
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
os.environ.setdefault("CLAWD_HOME", r"C:\Users\mercu\clawd")
os.environ.setdefault("CLAWD_DAEMON", r"C:\Users\mercu\clawd-daemon")
sys.path.insert(0, r"C:\Users\mercu\clawd-daemon")

CLAWD = Path(os.environ["CLAWD_HOME"])

stats = {"entities_added": 0, "edges_added": 0, "files_walked": 0}


def slugify_title(slug: str) -> str:
    """Turn a filename slug into a human-readable title."""
    s = re.sub(r"^\d+[-_.]?\s*", "", slug)
    s = s.replace("-", " ").replace("_", " ")
    return " ".join(w.capitalize() if not w.isupper() else w for w in s.split())


def walk_drift_essays(kg):
    # Canonical location is the staging mirror (209 essays) — local has stub
    candidates = [
        CLAWD / "repo-staging" / "Corpus-Perspectival" / "Foundations-of-Identity" / "personal-works" / "drift" / "essays",
        CLAWD / "Foundations-of-Identity" / "personal-works" / "drift" / "essays",
    ]
    essays_dir = next((p for p in candidates if p.exists() and len(list(p.glob("*.md"))) > 5), None)
    if essays_dir is None:
        return
    count = 0
    for path in sorted(essays_dir.glob("*.md")):
        slug = path.stem
        title = slugify_title(slug)
        eid = kg.add_entity_raw(f"Drift: {title}", "drift_essay", {
            "slug": slug,
            "file": str(path.relative_to(CLAWD)),
        })
        kg.add_edge_raw(f"Drift: {title}", "Drift", "part_of")
        count += 1
    stats["entities_added"] += count
    stats["edges_added"] += count
    stats["files_walked"] += count
    print(f"  Drift essays: {count} entities + {count} part_of edges")


def walk_mirror(kg):
    mirror_path = CLAWD / "palace" / "southeast" / "mirror.md"
    if not mirror_path.exists():
        return
    text = mirror_path.read_text(encoding="utf-8", errors="replace")
    # Match "## Mirror #N — Title" or "## #N — Title"
    pattern = re.compile(r"^##\s+(?:Mirror\s+)?#(\d+)\s*[—–-]\s*(.+?)$", re.MULTILINE)
    count = 0
    for m in pattern.finditer(text):
        num, title = m.group(1), m.group(2).strip()
        ent_name = f"Mirror #{num} {title}"
        kg.add_entity_raw(ent_name, "mirror_entry", {
            "number": int(num),
            "title": title,
            "file": str(mirror_path.relative_to(CLAWD)),
        })
        count += 1
    # M-meta mirrors
    for m in re.finditer(r"^##\s+(?:Meta-)?Mirror\s+M(\d+)\b\s*[—–-]?\s*(.*?)$", text, re.MULTILINE):
        kg.add_entity_raw(f"Meta-Mirror M{m.group(1)} {m.group(2).strip()}", "meta_mirror", {"number": int(m.group(1))})
        count += 1
    stats["entities_added"] += count
    stats["files_walked"] += 1
    print(f"  Mirror entries: {count}")


def walk_basement(kg):
    bp = CLAWD / "palace" / "basement" / "README.md"
    if not bp.exists():
        return
    text = bp.read_text(encoding="utf-8", errors="replace")
    count = 0
    # Match "## M1 ... " or "## L7 ..." or "### Bridge #117" or "### #117"
    for m in re.finditer(r"^#{2,3}\s+([ML]C?\d+|Bridge\s*#\d+|#\d+)\b\s*[—–-]?\s*(.*?)$", text, re.MULTILINE):
        ref, title = m.group(1).strip(), m.group(2).strip()
        if ref.startswith("M") and not ref.startswith("Mirror"):
            t = "meta_bridge"
        elif ref.startswith("LC"):
            t = "bridge_candidate"
        elif ref.startswith("L"):
            t = "latent_bridge"
        elif "Bridge" in ref or ref.startswith("#"):
            t = "bridge"
        else:
            continue
        ent = f"{ref} {title}".strip()
        kg.add_entity_raw(ent, t, {"reference": ref, "file": str(bp.relative_to(CLAWD))})
        count += 1
    stats["entities_added"] += count
    stats["files_walked"] += 1
    print(f"  Basement bridges: {count}")


def walk_master_glossary(kg):
    """Walk Library/Master-Glossary/registers/*.md for term entries."""
    g_dir = CLAWD / "repo-staging" / "Corpus-Perspectival" / "Library" / "Master-Glossary"
    if not g_dir.exists():
        return
    count = 0
    for reg_file in g_dir.rglob("*.md"):
        text = reg_file.read_text(encoding="utf-8", errors="replace")
        # Match "### Term Name" headers (skip "### §N" style section headers)
        for m in re.finditer(r"^###\s+([A-Z][^\n#§]{2,80})$", text, re.MULTILINE):
            term = m.group(1).strip()
            if term and not term.startswith(("§", "Day ", "Phase ")):
                kg.add_entity_raw(f"Glossary: {term}", "glossary_term", {
                    "term": term,
                    "register": reg_file.stem,
                })
                count += 1
    stats["entities_added"] += count
    print(f"  Master Glossary terms: {count}")


def walk_library_volumes(kg):
    """Walk Library/*/README.md or top-level *.md for volume identification."""
    lib_root = CLAWD / "repo-staging" / "Corpus-Perspectival" / "Library"
    if not lib_root.exists():
        return
    count = 0
    for vol_dir in sorted(lib_root.iterdir()):
        if not vol_dir.is_dir():
            continue
        vol_name = vol_dir.name
        # The volume entity should already exist from canonical population — upsert with file ref
        kg.add_entity_raw(vol_name.replace("-", " "), "library_volume", {
            "path": str(vol_dir.relative_to(CLAWD)),
            "discovered_via": "structural_walk",
        })
        # Walk top-level .md files for section entities
        for md in vol_dir.glob("*.md"):
            text = md.read_text(encoding="utf-8", errors="replace")
            # Top-level headings (# or ## that look like sections)
            for m in re.finditer(r"^##\s+§?\s*(\d+(?:\.\d+)?(?:\.\d+)?)\s+(.+?)$", text, re.MULTILINE):
                sec_num, sec_title = m.group(1), m.group(2).strip()
                kg.add_entity_raw(f"{vol_name} §{sec_num} {sec_title}", "volume_section", {
                    "volume": vol_name,
                    "section": sec_num,
                    "file": str(md.relative_to(CLAWD)),
                })
                count += 1
    stats["entities_added"] += count
    print(f"  Library sections: {count}")


def walk_cognitive_chains(kg):
    cc = CLAWD / "memory" / "cognitive_chains.json"
    if not cc.exists():
        return
    try:
        chains = json.loads(cc.read_text(encoding="utf-8"))
    except Exception:
        return
    if not isinstance(chains, list):
        return
    count = 0
    domains = set()
    for c in chains[-200:]:
        domain = c.get("domain", "?")
        if domain != "?":
            domains.add(domain)
        chain_id = c.get("id", f"chain-{count}")
        outcome = c.get("outcome", "?")
        ts = c.get("timestamp", "")[:19]
        kg.add_entity_raw(f"Chain {chain_id}", "cognitive_chain", {
            "domain": domain,
            "outcome": outcome,
            "timestamp": ts,
        })
        count += 1
    for d in domains:
        kg.add_entity_raw(f"Domain: {d}", "domain", {"kind": "cognitive_dsl"})
    stats["entities_added"] += count + len(domains)
    print(f"  Cognitive chains: {count} + {len(domains)} domains")


def walk_calibration_log(kg):
    cl = CLAWD / "memory" / "calibration_log.jsonl"
    if not cl.exists():
        return
    count = 0
    patterns_seen = set()
    for line in cl.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            entry = json.loads(line)
        except Exception:
            continue
        pattern = entry.get("pattern", "")
        if pattern and pattern not in patterns_seen:
            kg.add_entity_raw(f"Calibration Pattern: {pattern}", "calibration_pattern", {
                "pattern_id": pattern,
                "related_mirror": entry.get("related_mirror", ""),
            })
            patterns_seen.add(pattern)
        ts = entry.get("ts", "")
        ent = f"CalibInstance {ts[:19]} {pattern}"
        kg.add_entity_raw(ent, "calibration_instance", {
            "day": entry.get("day", 0),
            "session_phase": entry.get("session_phase", ""),
        })
        if pattern:
            kg.add_edge_raw(ent, f"Calibration Pattern: {pattern}", "instance_of")
        count += 1
    stats["entities_added"] += count + len(patterns_seen)
    print(f"  Calibration log: {count} instances + {len(patterns_seen)} patterns")


def walk_daily_logs(kg, days=14):
    """Add daily-log entities for the past N days (events grouped by date)."""
    mem = CLAWD / "memory"
    count = 0
    for log_path in sorted(mem.glob("2026-*.md"))[-days:]:
        date = log_path.stem
        kg.add_entity_raw(f"DailyLog {date}", "daily_log", {
            "date": date,
            "file": str(log_path.relative_to(CLAWD)),
        })
        count += 1
    stats["entities_added"] += count
    print(f"  Daily logs (last {days}): {count}")


def walk_handoff_atrium_current(kg):
    """Top-level navigation files as anchor entities."""
    for name, etype in [("handoff.md", "navigation_doc"), ("CURRENT.md", "navigation_doc")]:
        p = CLAWD / name if (CLAWD / name).exists() else (CLAWD / "memory" / name)
        if p.exists():
            kg.add_entity_raw(p.name, etype, {"file": str(p.relative_to(CLAWD))})
    atrium = CLAWD / "palace" / "ATRIUM.md"
    if atrium.exists():
        kg.add_entity_raw("ATRIUM.md", "navigation_doc", {"file": str(atrium.relative_to(CLAWD))})


def walk_identity_files(kg):
    iddir = CLAWD / "identity"
    if not iddir.exists():
        return
    count = 0
    for md in iddir.glob("*.md"):
        kg.add_entity_raw(f"Identity: {md.stem}", "identity_doc", {"file": str(md.relative_to(CLAWD))})
        count += 1
    stats["entities_added"] += count
    print(f"  Identity files: {count}")


def walk_tools(kg):
    ts_path = CLAWD / "memory" / "tool_states.json"
    if not ts_path.exists():
        return
    try:
        data = json.loads(ts_path.read_text(encoding="utf-8"))
    except Exception:
        return
    count = 0
    for name, info in data.get("tools", {}).items():
        kg.add_entity_raw(f"Tool: {name}", "daemon_tool", {
            "state": info.get("state", "?"),
            "role": info.get("role", "")[:200],
        })
        count += 1
    stats["entities_added"] += count
    print(f"  Daemon tools: {count}")


def walk_goals(kg):
    gp = CLAWD / "memory" / "goals.json"
    if not gp.exists():
        return
    try:
        goals = json.loads(gp.read_text(encoding="utf-8"))
    except Exception:
        return
    count = 0
    for g in goals:
        if g.get("status") not in ("active", "completed"):
            continue
        kg.add_entity_raw(f"Goal #{g['id']}: {g['title']}", "goal", {
            "status": g.get("status", "?"),
            "progress": g.get("progress", 0),
            "priority": g.get("priority", "?"),
        })
        count += 1
    stats["entities_added"] += count
    print(f"  Goals: {count}")


def main():
    from tools import knowledge_graph as kg
    print("=== Corpus-scale structural KG extraction — Day 105 ===\n")

    # Pre-state
    before = json.loads((CLAWD / "memory" / "knowledge_graph.json").read_text(encoding="utf-8"))
    print(f"Before: {len(before.get('entities', {}))} entities, {len(before.get('edges', []))} edges\n")

    walk_drift_essays(kg)
    walk_mirror(kg)
    walk_basement(kg)
    walk_master_glossary(kg)
    walk_library_volumes(kg)
    walk_cognitive_chains(kg)
    walk_calibration_log(kg)
    walk_daily_logs(kg, days=14)
    walk_identity_files(kg)
    walk_tools(kg)
    walk_goals(kg)
    walk_handoff_atrium_current(kg)

    # Post-state
    after = json.loads((CLAWD / "memory" / "knowledge_graph.json").read_text(encoding="utf-8"))
    n_ent = len(after.get("entities", {}))
    n_edge = len(after.get("edges", []))
    print(f"\nAfter: {n_ent} entities, {n_edge} edges")
    print(f"Delta: +{n_ent - len(before.get('entities', {}))} entities, +{n_edge - len(before.get('edges', []))} edges")

    # Type breakdown
    types = {}
    for e in after.get("entities", {}).values():
        t = e.get("type", "?")
        types[t] = types.get(t, 0) + 1
    print("\nBy type:")
    for t, c in sorted(types.items(), key=lambda x: -x[1]):
        print(f"  {t}: {c}")


if __name__ == "__main__":
    main()
