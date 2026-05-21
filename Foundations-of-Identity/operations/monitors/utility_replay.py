"""T2.H v0: Utility-tagged replay — memory hygiene via utility scoring.

Library + CLI for tagging stored entries (predictions, memory items, monitor
findings, basement entries) with utility scores, then querying high-utility
entries for replay or low-utility entries for archival candidates.

Per Substrate Extension Plan T2.H: 'CraniMem-style utility-tagged replay —
high-value memories get reinforced; low-value memories get pruned.'

Conservative v0:
- selective_forget() proposes archival candidates; does NOT auto-archive
- Utility scoring is event-based (caller tags); auto-scoring via heuristics
  is future iteration
- Integration with T1.D predictions: when resolve() fires, the prediction
  gets auto-tagged with utility based on outcome (CONFIRM=positive learning;
  FALSIFY=high learning per Mirror discipline)

Storage: memory/utility_ledger.jsonl (append-only). Each line is one
utility event. Aggregation is computed at query time.

Usage as library:
    from operations.monitors.utility_replay import tag, get_utility, top_utility, archival_candidates
    tag(entry_id='drift-essay-216', utility_delta=+5.0, source='Clayton-affirmation',
        category='drift_essay')
    score = get_utility('drift-essay-216')  # cumulative
    top_5_drift = top_utility(category='drift_essay', limit=5)
    candidates = archival_candidates(category='daily_log', threshold=0.0, min_age_days=30)

Usage as CLI:
    python operations/monitors/utility_replay.py tag <entry_id> <delta> <source> [--category=...]
    python operations/monitors/utility_replay.py top [--category=...] [--limit=20]
    python operations/monitors/utility_replay.py archival-candidates [--category=...] [--threshold=0.0] [--min-age-days=30]
    python operations/monitors/utility_replay.py stats
"""
import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CLAWD = Path(r"C:\Users\mercu\clawd")
if str(CLAWD) not in sys.path:
    sys.path.insert(0, str(CLAWD))
LEDGER_PATH = CLAWD / "memory" / "utility_ledger.jsonl"

# Default utility deltas per common event type
DEFAULT_UTILITY = {
    "prediction_confirm": +2.0,    # confirmed prediction validates the prediction-method
    "prediction_falsify": +3.0,    # falsified prediction is highest-value learning per Mirror discipline
    "prediction_partial": +1.0,
    "prediction_inapplicable": 0.0,
    "external_citation": +5.0,     # someone outside the program cited this entry
    "internal_cross_reference": +0.5,  # entry referenced by another entry in corpus
    "clayton_affirmation": +5.0,
    "clayton_correction": +3.0,    # corrections are high-value (Mirror discipline)
    "framework_load_bearing": +10.0,  # entry becomes load-bearing for canonical framework
    "deprecated": -10.0,           # entry has been explicitly deprecated
    "stale_unreferenced": -1.0,    # accumulates per audit pass when entry isn't referenced
}


def tag(entry_id: str, utility_delta: float, source: str,
        category: str = "general", notes: str = None) -> None:
    """Record a utility event for entry_id."""
    record = {
        "ts": datetime.now().isoformat(),
        "entry_id": entry_id,
        "utility_delta": float(utility_delta),
        "source": source,
        "category": category,
        "notes": notes,
    }
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LEDGER_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def tag_by_event(entry_id: str, event_type: str, source: str,
                 category: str = "general", notes: str = None) -> None:
    """Convenience: tag with default utility for known event_type."""
    if event_type not in DEFAULT_UTILITY:
        raise ValueError(f"unknown event_type {event_type!r}; valid: {list(DEFAULT_UTILITY)}")
    tag(entry_id, DEFAULT_UTILITY[event_type], source, category, notes=notes or event_type)


def _load_ledger() -> list:
    if not LEDGER_PATH.exists():
        return []
    out = []
    with open(LEDGER_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def get_utility(entry_id: str) -> dict:
    """Cumulative utility for entry_id."""
    events = [r for r in _load_ledger() if r["entry_id"] == entry_id]
    if not events:
        return {"entry_id": entry_id, "cumulative_utility": 0.0, "event_count": 0}
    total = sum(r["utility_delta"] for r in events)
    return {
        "entry_id": entry_id,
        "cumulative_utility": round(total, 2),
        "event_count": len(events),
        "first_tagged": events[0]["ts"],
        "last_tagged": events[-1]["ts"],
        "category": events[-1].get("category", "general"),
    }


def top_utility(category: str = None, limit: int = 20) -> list:
    """Highest cumulative-utility entries, optionally filtered by category."""
    cumulative = defaultdict(float)
    meta = {}
    for r in _load_ledger():
        if category and r.get("category") != category:
            continue
        cumulative[r["entry_id"]] += r["utility_delta"]
        meta[r["entry_id"]] = {
            "category": r.get("category", "general"),
            "last_ts": r["ts"],
        }
    ranked = sorted(cumulative.items(), key=lambda x: -x[1])
    return [
        {"entry_id": eid, "cumulative_utility": round(score, 2),
         "category": meta[eid]["category"], "last_tagged": meta[eid]["last_ts"]}
        for eid, score in ranked[:limit]
    ]


def archival_candidates(category: str = None, threshold: float = 0.0,
                        min_age_days: int = 30) -> list:
    """Entries with cumulative_utility <= threshold AND last tagged > min_age_days ago.

    Conservative: only proposes; never archives automatically.
    """
    cumulative = defaultdict(float)
    last_seen = {}
    meta_cat = {}
    for r in _load_ledger():
        if category and r.get("category") != category:
            continue
        cumulative[r["entry_id"]] += r["utility_delta"]
        last_seen[r["entry_id"]] = r["ts"]
        meta_cat[r["entry_id"]] = r.get("category", "general")

    now = datetime.now()
    cutoff_ts = now - timedelta(days=min_age_days)
    candidates = []
    for eid, score in cumulative.items():
        if score > threshold:
            continue
        try:
            last_dt = datetime.fromisoformat(last_seen[eid])
        except ValueError:
            continue
        if last_dt > cutoff_ts:
            continue
        candidates.append({
            "entry_id": eid,
            "cumulative_utility": round(score, 2),
            "last_tagged": last_seen[eid],
            "age_days": (now - last_dt).days,
            "category": meta_cat[eid],
        })
    candidates.sort(key=lambda x: x["cumulative_utility"])
    return candidates


def stats() -> dict:
    ledger = _load_ledger()
    if not ledger:
        return {"total_events": 0, "total_entries": 0}
    by_category = defaultdict(lambda: {"events": 0, "entries": set(), "total_utility": 0.0})
    for r in ledger:
        c = r.get("category", "general")
        by_category[c]["events"] += 1
        by_category[c]["entries"].add(r["entry_id"])
        by_category[c]["total_utility"] += r["utility_delta"]
    return {
        "total_events": len(ledger),
        "total_entries": len({r["entry_id"] for r in ledger}),
        "by_category": {
            c: {
                "events": v["events"],
                "entries": len(v["entries"]),
                "total_utility": round(v["total_utility"], 2),
            }
            for c, v in by_category.items()
        },
        "first_event": ledger[0]["ts"],
        "latest_event": ledger[-1]["ts"],
    }


def synthetic_test() -> bool:
    """Falsifiability: tag → query → archival-candidates cycle.

    Uses a per-run unique category so the ranking test isn't polluted by
    prior runs' entries (caught by monitor_self_test 2026-05-20).
    """
    print("=== T2.H Utility-Tagged Replay Test ===")
    run_id = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    test_category = f"_test_{run_id}"
    tid = f"_synthetic_test_{run_id}"
    tag(tid, +3.0, "synthetic_test", category=test_category, notes="initial positive tag")
    tag(tid, +2.0, "synthetic_test", category=test_category)
    u = get_utility(tid)
    assert u["cumulative_utility"] == 5.0, f"cumulative wrong: {u}"
    print(f"  PASS: tag + get_utility round-trip (cumulative=5.0)")

    # Tag a separate negative-utility entry in same test category
    tid_old = f"_synthetic_old_{run_id}"
    tag(tid_old, -5.0, "synthetic_test_neg", category=test_category)
    tops = top_utility(category=test_category, limit=5)
    assert tops and tops[0]["entry_id"] == tid, f"top utility wrong: {tops}"
    print(f"  PASS: top_utility ranks correctly; #1={tops[0]['entry_id']} score={tops[0]['cumulative_utility']}")

    print(f"  PASS: full cycle works (tag/get/top)")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["tag", "get", "top", "archival-candidates", "stats", "test"])
    parser.add_argument("args", nargs="*")
    parser.add_argument("--category", default=None)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--threshold", type=float, default=0.0)
    parser.add_argument("--min-age-days", type=int, default=30)
    ns = parser.parse_args()

    if ns.command == "test":
        ok = synthetic_test()
        sys.exit(0 if ok else 1)

    elif ns.command == "tag":
        if len(ns.args) < 3:
            print("usage: tag <entry_id> <utility_delta> <source>")
            sys.exit(1)
        tag(ns.args[0], float(ns.args[1]), ns.args[2], category=ns.category or "general")
        print(f"  tagged {ns.args[0]} with delta {ns.args[1]}")

    elif ns.command == "get":
        if not ns.args:
            print("usage: get <entry_id>")
            sys.exit(1)
        print(json.dumps(get_utility(ns.args[0]), indent=2))

    elif ns.command == "top":
        rows = top_utility(category=ns.category, limit=ns.limit)
        print(f"=== Top {ns.limit} utility entries{' in ' + ns.category if ns.category else ''} ===")
        for r in rows:
            print(f"  {r['cumulative_utility']:>7.2f}  {r['entry_id'][:60]:60} ({r['category']})")

    elif ns.command == "archival-candidates":
        rows = archival_candidates(category=ns.category, threshold=ns.threshold,
                                    min_age_days=ns.min_age_days)
        print(f"=== Archival candidates (utility<={ns.threshold}, age>={ns.min_age_days}d) ===")
        if not rows:
            print(f"  none")
        for r in rows[:50]:
            print(f"  utility={r['cumulative_utility']:>7.2f} age={r['age_days']}d  {r['entry_id'][:55]}")
        print(f"  (NOT archived; this is a PROPOSAL list; manual review required.)")

    elif ns.command == "stats":
        s = stats()
        print(json.dumps(s, indent=2))


if __name__ == "__main__":
    main()
