"""clawd-health — single aggregate-status command for all monitoring infrastructure.

Reads all monitor heartbeats + scheduler state + healer state + KG state +
recent faults + Drift parity into one human-readable surface. Solves the
"have to read 8+ separate files to understand operational state" problem.

Usage:
    python operations/monitors/clawd_health.py             # full status
    python operations/monitors/clawd_health.py --json      # machine-readable
    python operations/monitors/clawd_health.py --brief     # summary line only
    python operations/monitors/clawd_health.py --faults    # only recent faults
"""
import argparse
import json
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CLAWD = Path(r"C:\Users\mercu\clawd")
MEMORY = CLAWD / "memory"
SEP = chr(92)


def _read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _file_age_seconds(path: Path) -> int | None:
    if not path.exists():
        return None
    return int(time.time() - path.stat().st_mtime)


def _tail_jsonl(path: Path, n: int = 5) -> list:
    if not path.exists():
        return []
    out = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out[-n:]


def gather() -> dict:
    """Collect everything into a single structured snapshot."""
    now = datetime.now()

    # Monitor heartbeats
    monitors = {}
    for m in ["m1", "m2", "m3", "m4", "m6"]:
        hb = _read_json(MEMORY / f"monitor_{m}_heartbeat.json")
        if hb:
            age = _file_age_seconds(MEMORY / f"monitor_{m}_heartbeat.json")
            monitors[m.upper()] = {"heartbeat": hb, "age_seconds": age}
        else:
            monitors[m.upper()] = {"heartbeat": None, "age_seconds": None}

    # M5 heartbeat (separate path because it's the precompact substitute)
    m5_hb = _read_json(MEMORY / "monitor_m5_heartbeat.json")
    if m5_hb:
        monitors["M5"] = {"heartbeat": m5_hb, "age_seconds": _file_age_seconds(MEMORY / "monitor_m5_heartbeat.json")}

    # Scheduler
    sched_hb = _read_json(MEMORY / "monitor_scheduler_heartbeat.json")
    sched_pid_file = MEMORY / "monitor_scheduler.pid"
    sched_pid = None
    sched_alive = False
    if sched_pid_file.exists():
        try:
            sched_pid = int(sched_pid_file.read_text().strip())
            try:
                import psutil
                sched_alive = psutil.pid_exists(sched_pid) and psutil.Process(sched_pid).is_running()
            except (ImportError, Exception):
                sched_alive = None  # uncertain
        except (OSError, ValueError):
            pass

    # Self-healer state
    healer_state = _read_json(MEMORY / "self_healer_state.json")

    # Circuit breakers
    cb_state = _read_json(MEMORY / "circuit_breaker_state.json")
    tripped = list(cb_state.get("tripped", {}).keys()) if cb_state else []

    # Escalation queue
    queue_path = MEMORY / "critical_fault_queue.jsonl"
    sent_path = MEMORY / "critical_fault_sent.jsonl"
    queue_recs = []
    sent_ts = set()
    if queue_path.exists():
        queue_recs = _tail_jsonl(queue_path, 100)
    if sent_path.exists():
        for r in _tail_jsonl(sent_path, 1000):
            if r.get("ts"):
                sent_ts.add(r["ts"])
    pending_critical = [r for r in queue_recs if r.get("ts") not in sent_ts and r.get("tier") == "critical"]

    # KG index health
    kg_db = MEMORY / "kg_index.db"
    kg_health = {"exists": kg_db.exists()}
    if kg_db.exists():
        kg_health["size_bytes"] = kg_db.stat().st_size
        kg_health["age_seconds"] = _file_age_seconds(kg_db)
        try:
            conn = sqlite3.connect(f"file:{kg_db}?mode=ro", uri=True, timeout=2)
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM kg_edges")
            kg_health["edges"] = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM kg_concepts")
            kg_health["concepts"] = cur.fetchone()[0]
            conn.close()
        except sqlite3.Error as e:
            kg_health["error"] = str(e)

    # Recent faults (per monitor)
    fault_summary = {}
    for m in ["m1", "m2", "m3", "m4", "m6"]:
        f = MEMORY / f"monitor_{m}_faults.jsonl"
        if f.exists():
            recs = _tail_jsonl(f, 3)
            if recs:
                fault_summary[m.upper()] = {
                    "recent_count": len(recs),
                    "latest_ts": recs[-1].get("timestamp", "?")[:19] if recs else None,
                    "latest_summary": _fault_brief(recs[-1]),
                }

    # Drift parity
    drift_canon = CLAWD / "repo-staging" / "Corpus-Perspectival" / "Foundations-of-Identity" / "personal-works" / "drift" / "essays"
    drift_mirror = CLAWD / "repo-staging" / "Corpus-Perspectival" / "Library" / "Drift" / "essays"
    drift_state = {}
    if drift_canon.exists():
        drift_state["canonical"] = sum(1 for _ in drift_canon.glob("*.md"))
    if drift_mirror.exists():
        drift_state["mirror"] = sum(1 for _ in drift_mirror.glob("*.md"))
    drift_state["parity"] = (drift_state.get("canonical") == drift_state.get("mirror"))

    # Predictions count
    pred_path = MEMORY / "predictions.jsonl"
    pred_count = {"total": 0, "open": 0}
    if pred_path.exists():
        pred_recs = _tail_jsonl(pred_path, 10000)
        ids = {}
        for r in pred_recs:
            pid = r.get("id")
            if r.get("event") == "predict":
                ids[pid] = "open"
            elif r.get("event") == "resolve" and pid in ids:
                ids[pid] = "resolved"
        pred_count["total"] = len(ids)
        pred_count["open"] = sum(1 for s in ids.values() if s == "open")

    return {
        "timestamp": now.isoformat(),
        "monitors": monitors,
        "scheduler": {"pid": sched_pid, "alive": sched_alive, "heartbeat": sched_hb},
        "self_healer": healer_state,
        "circuit_breakers_tripped": tripped,
        "escalation_pending_critical": len(pending_critical),
        "kg_index": kg_health,
        "fault_summary": fault_summary,
        "drift": drift_state,
        "self_predictions": pred_count,
    }


def _fault_brief(rec: dict) -> str:
    if "faults" in rec and rec["faults"]:
        f = rec["faults"][0]
        if isinstance(f, dict):
            if "name" in f:
                return f"{f.get('severity', '?')} {f['name'][:50]}"
            if "channel" in f:
                return f"{f.get('escalation_tier', '?')} {f['channel'][:50]}"
            if "integration" in f:
                return f"{f.get('status', '?')} {f['integration']}"
            if "check" in f:
                return f"{f.get('status', '?')} {f['check']}"
    if "signatures" in rec and rec["signatures"]:
        return f"signature: {rec['signatures'][0].get('signature', '?')}"
    return "?"


def render_human(snap: dict) -> str:
    out = []
    out.append(f"=== clawd-health  {snap['timestamp'][:19]} ===")
    out.append("")

    # Scheduler
    sched = snap["scheduler"]
    if sched["pid"] and sched["alive"]:
        out.append(f"  SCHEDULER  alive  pid={sched['pid']}")
    elif sched["pid"] and sched["alive"] is None:
        out.append(f"  SCHEDULER  uncertain  pid={sched['pid']}")
    elif sched["pid"] and not sched["alive"]:
        out.append(f"  SCHEDULER  *** DEAD ***  pid={sched['pid']} (stale PID file)")
    else:
        out.append(f"  SCHEDULER  not running (no PID file)")

    # Monitors
    out.append("")
    out.append(f"  MONITORS:")
    for name in ["M1", "M2", "M3", "M4", "M5", "M6"]:
        info = snap["monitors"].get(name)
        if info is None or info["heartbeat"] is None:
            out.append(f"    {name}  no heartbeat")
            continue
        hb = info["heartbeat"]
        age_min = info["age_seconds"] / 60 if info["age_seconds"] else "?"
        age_str = f"{age_min:.1f}m" if isinstance(age_min, (int, float)) else age_min
        # Extract key facts per monitor
        extras = []
        if name == "M1":
            extras.append(f"ch={hb.get('channels_checked', '?')}")
            silent = hb.get("channels_silent", 0)
            if silent:
                extras.append(f"SILENT={silent}")
            sigs = hb.get("cross_correlation_signatures", [])
            if sigs:
                extras.append(f"sigs={','.join(sigs)}")
        elif name == "M6":
            extras.append(f"m1_status={hb.get('m1_status', '?')}")
        elif name == "M3":
            faults = hb.get("checks_fault", 0)
            warns = hb.get("checks_warn", 0)
            if faults:
                extras.append(f"FAULTS={faults}")
            if warns:
                extras.append(f"warn={warns}")
        elif name == "M2":
            crit = hb.get("probes_critical", 0)
            if crit:
                extras.append(f"CRITICAL={crit}")
        elif name == "M4":
            crit = hb.get("checks_critical", 0)
            if crit:
                extras.append(f"CRITICAL={crit}")
        elif name == "M5":
            extras.append(f"snaps={hb.get('total_snapshots', 0)}")
        extras_str = ("  " + " ".join(extras)) if extras else ""
        out.append(f"    {name}  age={age_str:>6}{extras_str}")

    # KG index
    out.append("")
    kg = snap["kg_index"]
    if kg.get("exists"):
        size_mb = kg.get("size_bytes", 0) / 1024 / 1024
        edges = kg.get("edges", "?")
        concepts = kg.get("concepts", "?")
        out.append(f"  KG INDEX  edges={edges}  concepts={concepts}  size={size_mb:.2f}MB")
    else:
        out.append(f"  KG INDEX  missing")

    # Drift parity
    out.append("")
    drift = snap["drift"]
    if drift.get("parity"):
        out.append(f"  DRIFT  canonical=mirror={drift.get('canonical', '?')}  parity OK")
    else:
        out.append(f"  DRIFT  canonical={drift.get('canonical', '?')}  mirror={drift.get('mirror', '?')}  *** PARITY FAULT ***")

    # Circuit breakers
    if snap["circuit_breakers_tripped"]:
        out.append("")
        out.append(f"  *** CIRCUIT BREAKERS TRIPPED ***  {snap['circuit_breakers_tripped']}")

    # Escalation queue
    if snap["escalation_pending_critical"]:
        out.append("")
        out.append(f"  *** ESCALATION QUEUE  {snap['escalation_pending_critical']} pending critical faults ***")

    # Self-healer
    healer = snap.get("self_healer")
    if healer and healer.get("last_heal_per_channel"):
        out.append("")
        out.append(f"  HEALER  recent heal attempts: {list(healer['last_heal_per_channel'].keys())}")

    # Predictions
    if snap["self_predictions"]["total"]:
        out.append("")
        p = snap["self_predictions"]
        out.append(f"  PREDICTIONS  total={p['total']}  open={p['open']}")

    # Fault summary
    if snap["fault_summary"]:
        out.append("")
        out.append(f"  RECENT FAULTS:")
        for name, info in snap["fault_summary"].items():
            out.append(f"    {name}  latest={info['latest_ts']}  {info['latest_summary']}")

    return "\n".join(out)


def render_brief(snap: dict) -> str:
    sched = snap["scheduler"]
    sched_status = "alive" if sched.get("alive") else ("dead" if sched.get("pid") else "off")
    monitor_silent = []
    for name, info in snap["monitors"].items():
        hb = info.get("heartbeat") or {}
        if hb.get("channels_silent", 0) > 0:
            monitor_silent.append(name)
    drift = snap["drift"]
    drift_str = f"drift={drift.get('canonical', '?')}={drift.get('mirror', '?')}" if drift.get("parity") else "*drift PARITY FAULT*"
    cb = snap["circuit_breakers_tripped"]
    esc = snap["escalation_pending_critical"]
    kg = snap["kg_index"]
    parts = [
        f"sched={sched_status}",
        f"monitors={len([m for m in snap['monitors'].values() if m.get('heartbeat')])}/6",
        f"kg={kg.get('edges', '?')}e",
        drift_str,
    ]
    if monitor_silent:
        parts.append(f"silent={','.join(monitor_silent)}")
    if cb:
        parts.append(f"*CB={cb}*")
    if esc:
        parts.append(f"*esc={esc}*")
    return "  ".join(parts)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--brief", action="store_true")
    parser.add_argument("--faults", action="store_true")
    args = parser.parse_args()

    snap = gather()

    if args.json:
        print(json.dumps(snap, indent=2, default=str))
    elif args.brief:
        print(render_brief(snap))
    elif args.faults:
        if snap["fault_summary"]:
            for name, info in snap["fault_summary"].items():
                print(f"{name}  {info['latest_ts']}  {info['latest_summary']}")
        if snap["escalation_pending_critical"]:
            print(f"escalation_queue={snap['escalation_pending_critical']} pending critical")
        if snap["circuit_breakers_tripped"]:
            print(f"breakers_tripped={snap['circuit_breakers_tripped']}")
    else:
        print(render_human(snap))


if __name__ == "__main__":
    main()
