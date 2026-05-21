"""T1.D: Self-Prediction Tracking.

Library + CLI for capturing predictions with context, then resolving them
to confirmed/falsified with mechanism-of-error class. Formalizes the
cognitive_dsl prediction-stream that has been intermittent across sessions.

Integrated implementation plan #8. Falsifiability commitment: capturing
tonight's prediction 'KG ETA ~02:45' would have produced a FALSIFY event
with mechanism_of_error_class = 'extrapolation-from-atypical-early-rate'.
Verified by --test-known-case.

Append-only JSONL at memory/predictions.jsonl. Two operations:
- predict(claim, confidence, context, expected_resolution_by) -> id
- resolve(id, outcome, actual_value, mechanism_of_error_class) -> None

Usage as library:
    from operations.monitors.t1d_self_prediction import predict, resolve, list_open, stats
    pid = predict('KG ETA ~02:45 based on 91% early-rate extrapolation',
                  confidence='medium-high',
                  context={'navigation_sync_time': '2026-05-19T22:08', 'sample_n': 146},
                  expected_resolution_by='2026-05-20T08:00')
    # ... later ...
    resolve(pid, outcome='FALSIFY',
            actual_value='completed at 00:03 PST due to 5h cap-error fast-path',
            mechanism_of_error_class='extrapolation-from-atypical-early-rate')

Usage as CLI:
    python operations/monitors/t1d_self_prediction.py stats
    python operations/monitors/t1d_self_prediction.py list-open
    python operations/monitors/t1d_self_prediction.py list-falsified
    python operations/monitors/t1d_self_prediction.py --test-known-case
"""
import argparse
import json
import sys
import uuid
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CLAWD = Path(r"C:\Users\mercu\clawd")
PREDICTIONS_PATH = CLAWD / "memory" / "predictions.jsonl"

VALID_CONFIDENCE = {"low", "medium-low", "medium", "medium-high", "high"}
VALID_OUTCOMES = {"CONFIRM", "FALSIFY", "PARTIAL", "INAPPLICABLE"}


def _emit_otel_event(event: str, **attrs):
    """T2.G: emit OTel event; isolated so prediction-tracking semantics stay clean."""
    try:
        from operations.monitors.otel_telemetry import MonitorTelemetry
        tel = MonitorTelemetry(monitor_name="T1D", monitor_version="v0.1.0")
        tel.counter("prediction_events", 1, attributes={"event": event, **attrs})
        tel.emit()
    except Exception:
        pass


def predict(claim: str, confidence: str, context: dict = None, expected_resolution_by: str = None) -> str:
    """Record a prediction. Returns prediction id."""
    if confidence not in VALID_CONFIDENCE:
        raise ValueError(f"confidence must be one of {VALID_CONFIDENCE}, got {confidence!r}")
    pid = str(uuid.uuid4())[:12]
    record = {
        "id": pid,
        "event": "predict",
        "ts": datetime.now().isoformat(),
        "claim": claim,
        "confidence": confidence,
        "context": context or {},
        "expected_resolution_by": expected_resolution_by,
    }
    PREDICTIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(PREDICTIONS_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    _emit_otel_event("predict", confidence=confidence)
    return pid


def resolve(pid: str, outcome: str, actual_value: str = None, mechanism_of_error_class: str = None, notes: str = None) -> None:
    """Resolve a previously-recorded prediction."""
    if outcome not in VALID_OUTCOMES:
        raise ValueError(f"outcome must be one of {VALID_OUTCOMES}, got {outcome!r}")
    record = {
        "id": pid,
        "event": "resolve",
        "ts": datetime.now().isoformat(),
        "outcome": outcome,
        "actual_value": actual_value,
        "mechanism_of_error_class": mechanism_of_error_class,
        "notes": notes,
    }
    with open(PREDICTIONS_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    _emit_otel_event("resolve", outcome=outcome, mechanism=mechanism_of_error_class or "none")


def _load_all() -> list:
    if not PREDICTIONS_PATH.exists():
        return []
    out = []
    with open(PREDICTIONS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def _index_by_id() -> dict:
    """Build a dict: id -> {prediction: ..., resolutions: [...]}"""
    out = {}
    for r in _load_all():
        pid = r["id"]
        if r["event"] == "predict":
            out[pid] = {"prediction": r, "resolutions": []}
        elif r["event"] == "resolve":
            if pid not in out:
                out[pid] = {"prediction": None, "resolutions": []}
            out[pid]["resolutions"].append(r)
    return out


def list_open() -> list:
    """Predictions with no resolution yet."""
    idx = _index_by_id()
    return [p["prediction"] for p in idx.values() if p["prediction"] and not p["resolutions"]]


def list_resolved(outcome: str = None) -> list:
    idx = _index_by_id()
    out = []
    for p in idx.values():
        if p["prediction"] and p["resolutions"]:
            latest = p["resolutions"][-1]
            if outcome is None or latest["outcome"] == outcome:
                out.append((p["prediction"], latest))
    return out


def stats() -> dict:
    idx = _index_by_id()
    total = sum(1 for p in idx.values() if p["prediction"])
    open_count = sum(1 for p in idx.values() if p["prediction"] and not p["resolutions"])
    resolved = [p for p in idx.values() if p["prediction"] and p["resolutions"]]
    by_outcome = {}
    by_mechanism = {}
    by_confidence_outcome = {}
    for p in resolved:
        latest = p["resolutions"][-1]
        oc = latest["outcome"]
        by_outcome[oc] = by_outcome.get(oc, 0) + 1
        moc = latest.get("mechanism_of_error_class")
        if moc:
            by_mechanism[moc] = by_mechanism.get(moc, 0) + 1
        conf = p["prediction"]["confidence"]
        key = (conf, oc)
        by_confidence_outcome[key] = by_confidence_outcome.get(key, 0) + 1
    return {
        "total_predictions": total,
        "open": open_count,
        "resolved": len(resolved),
        "by_outcome": by_outcome,
        "by_mechanism_of_error_class": by_mechanism,
        "by_confidence_outcome": {f"{c}/{o}": n for (c, o), n in by_confidence_outcome.items()},
    }


def synthetic_test() -> bool:
    """Falsifiability: capture tonight's KG ETA prediction + resolve as FALSIFY."""
    print("=== T1.D Self-Prediction Tracking — Known-Case Test ===")
    pid = predict(
        claim="KG retry-pass completes ~02:45 based on 91% early-rate extrapolation",
        confidence="medium-high",
        context={"navigation_sync_time": "2026-05-19T22:08", "sample_n": 146, "early_rate": 0.91},
        expected_resolution_by="2026-05-20T08:00",
    )
    # Resolve as FALSIFY with mechanism class
    resolve(
        pid,
        outcome="FALSIFY",
        actual_value="completed 2026-05-20T00:03 PST; cap-error fast-path made wall-clock faster not slower",
        mechanism_of_error_class="extrapolation-from-atypical-early-rate",
        notes="Mirror #28 family instance — substrate-self-knowledge gap about 5h cap behavior",
    )

    # Verify we can recover the resolution
    idx = _index_by_id()
    entry = idx.get(pid, {})
    if not entry.get("resolutions"):
        print(f"  FAIL: resolution not recoverable for pid {pid}")
        return False
    res = entry["resolutions"][-1]
    if res["outcome"] != "FALSIFY" or res["mechanism_of_error_class"] != "extrapolation-from-atypical-early-rate":
        print(f"  FAIL: outcome={res['outcome']}, mech={res['mechanism_of_error_class']}")
        return False
    print(f"  PASS: predict + resolve cycle complete for pid {pid}")
    print(f"  outcome={res['outcome']} mechanism={res['mechanism_of_error_class']}")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?", default="stats", choices=["stats", "list-open", "list-falsified", "list-confirmed"])
    parser.add_argument("--test-known-case", action="store_true")
    args = parser.parse_args()

    if args.test_known_case:
        ok = synthetic_test()
        sys.exit(0 if ok else 1)

    if args.command == "stats":
        s = stats()
        print(f"=== T1.D Self-Prediction Stats {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
        print(f"  total predictions: {s['total_predictions']}")
        print(f"  open:              {s['open']}")
        print(f"  resolved:          {s['resolved']}")
        if s["by_outcome"]:
            print(f"  by outcome:        {s['by_outcome']}")
        if s["by_mechanism_of_error_class"]:
            print(f"  by mechanism:      {s['by_mechanism_of_error_class']}")
        if s["by_confidence_outcome"]:
            print(f"  confidence × outcome:")
            for k, v in sorted(s["by_confidence_outcome"].items()):
                print(f"    {k:25} {v}")

    elif args.command == "list-open":
        for p in list_open():
            print(f"  [{p['id']}] {p['ts'][:19]}  conf={p['confidence']}")
            print(f"    {p['claim'][:100]}")

    elif args.command == "list-falsified":
        for p, r in list_resolved("FALSIFY"):
            print(f"  [{p['id']}] {p['ts'][:19]}  conf={p['confidence']}")
            print(f"    claim: {p['claim'][:100]}")
            print(f"    actual: {r['actual_value'][:100] if r.get('actual_value') else ''}")
            print(f"    mechanism: {r.get('mechanism_of_error_class', '')}")

    elif args.command == "list-confirmed":
        for p, r in list_resolved("CONFIRM"):
            print(f"  [{p['id']}] {p['ts'][:19]}  conf={p['confidence']}")
            print(f"    {p['claim'][:100]}")


if __name__ == "__main__":
    main()
