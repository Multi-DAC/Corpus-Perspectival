"""Escalation router — enqueue critical faults for Telegram delivery.

Library + queue + standalone poller. Monitors call enqueue_critical()
to write a fault into memory/critical_fault_queue.jsonl. A separate
poller process reads the queue, sends via Telegram Bot API, and marks
the entry sent.

Design rationale: monitors are subprocess-spawned; they shouldn't
directly talk to network APIs (each subprocess would have to load
requests, manage auth, retry on transient failure). Queue + poller
decouples concerns: monitors stay fast and dependency-free; the
poller is a single long-running process with the network surface.

Token-discipline default: rate-limit Telegram sends to 1 per 5 min
across all monitors combined (avoids notification-spam during a real
incident; aligns with integrated plan 'don't escalate routine' rule).

Usage as library (from any monitor):
    from operations.monitors.escalation_router import enqueue_critical
    enqueue_critical(
        monitor='M3',
        tier='critical',
        summary='Drift count desync: declared 200, actual 215',
        details={'declared': 200, 'truth': 215},
    )

Usage as poller (standalone, run periodically OR detached):
    python operations/monitors/escalation_router.py poll
    python operations/monitors/escalation_router.py poll --once
    python operations/monitors/escalation_router.py status
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CLAWD = Path(r"C:\Users\mercu\clawd")
QUEUE_PATH = CLAWD / "memory" / "critical_fault_queue.jsonl"
SENT_PATH = CLAWD / "memory" / "critical_fault_sent.jsonl"
POLLER_STATE = CLAWD / "memory" / "escalation_poller_state.json"
POLLER_HEARTBEAT = CLAWD / "memory" / "escalation_poller_heartbeat.json"

RATE_LIMIT_SECONDS = 300  # 5 min minimum between sends
POLL_INTERVAL_SECONDS = 60


def enqueue_critical(monitor: str, tier: str, summary: str, details: dict = None) -> str:
    """Library entry point — monitors call this to enqueue a critical fault.

    tier: 'critical' | 'high' | 'medium' | 'low'. Currently only 'critical'
    triggers Telegram delivery; lower tiers are queued for audit only.
    """
    record = {
        "ts": datetime.now().isoformat(),
        "monitor": monitor,
        "tier": tier,
        "summary": summary,
        "details": details or {},
        "sent": False,
    }
    QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(QUEUE_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    return record["ts"]


def _load_state() -> dict:
    if not POLLER_STATE.exists():
        return {"last_sent_ts": None, "total_sent": 0}
    try:
        return json.loads(POLLER_STATE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"last_sent_ts": None, "total_sent": 0}


def _save_state(state: dict) -> None:
    POLLER_STATE.parent.mkdir(parents=True, exist_ok=True)
    POLLER_STATE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _write_heartbeat(state: dict, pending: int) -> None:
    payload = {
        "poller": "escalation_router",
        "timestamp": datetime.now().isoformat(),
        "pid": os.getpid(),
        "last_sent_ts": state.get("last_sent_ts"),
        "total_sent": state.get("total_sent", 0),
        "pending_in_queue": pending,
    }
    POLLER_HEARTBEAT.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _read_queue() -> list:
    if not QUEUE_PATH.exists():
        return []
    out = []
    with open(QUEUE_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def _read_sent() -> set:
    if not SENT_PATH.exists():
        return set()
    out = set()
    with open(SENT_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                out.add(rec.get("ts"))
            except json.JSONDecodeError:
                continue
    return out


def _mark_sent(record: dict) -> None:
    record["sent_ts"] = datetime.now().isoformat()
    with open(SENT_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def send_telegram(text: str) -> dict:
    """Send a message via Telegram Bot API. Returns {success: bool, error: str?}."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TG_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID") or os.environ.get("TG_CHAT_ID")
    if not token:
        return {"success": False, "error": "TELEGRAM_BOT_TOKEN env not set"}
    if not chat_id:
        return {"success": False, "error": "TELEGRAM_CHAT_ID env not set"}

    try:
        import requests
        import warnings
        warnings.filterwarnings("ignore")
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        r = requests.post(
            url,
            json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
            timeout=15,
            verify=False,
        )
        if r.status_code == 200:
            return {"success": True}
        return {"success": False, "error": f"HTTP {r.status_code}: {r.text[:200]}"}
    except ImportError:
        return {"success": False, "error": "requests library not available"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def format_critical_fault(record: dict) -> str:
    return (
        f"🦞 *CRITICAL FAULT* — {record['monitor']}\n"
        f"_{record['ts']}_\n\n"
        f"{record['summary']}\n\n"
        f"```json\n{json.dumps(record.get('details', {}), indent=2)[:800]}\n```"
    )


def poll_once() -> dict:
    """One poll cycle. Returns summary."""
    state = _load_state()
    queue = _read_queue()
    sent_ts = _read_sent()
    pending = [r for r in queue if r.get("ts") not in sent_ts and r.get("tier") == "critical"]

    sent_now = 0
    skipped_rate_limit = 0
    failed = 0

    now = datetime.now()
    last_sent_str = state.get("last_sent_ts")
    last_sent = datetime.fromisoformat(last_sent_str) if last_sent_str else None

    for rec in pending:
        # Rate limit: at most one send per RATE_LIMIT_SECONDS
        if last_sent is not None:
            elapsed = (now - last_sent).total_seconds()
            if elapsed < RATE_LIMIT_SECONDS:
                skipped_rate_limit += 1
                continue

        text = format_critical_fault(rec)
        result = send_telegram(text)
        if result.get("success"):
            _mark_sent(rec)
            sent_now += 1
            state["last_sent_ts"] = datetime.now().isoformat()
            state["total_sent"] = state.get("total_sent", 0) + 1
            last_sent = datetime.now()
        else:
            failed += 1

    _save_state(state)
    _write_heartbeat(state, len(pending))
    return {
        "pending": len(pending),
        "sent_now": sent_now,
        "skipped_rate_limit": skipped_rate_limit,
        "failed": failed,
    }


def poll_forever():
    print(f"escalation_router polling every {POLL_INTERVAL_SECONDS}s; rate-limit {RATE_LIMIT_SECONDS}s between sends")
    try:
        while True:
            summary = poll_once()
            if summary["pending"] > 0:
                print(f"  [{datetime.now().strftime('%H:%M:%S')}] {summary}")
            time.sleep(POLL_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\nstopped")


def status():
    state = _load_state()
    queue = _read_queue()
    sent_ts = _read_sent()
    pending = [r for r in queue if r.get("ts") not in sent_ts and r.get("tier") == "critical"]
    print(f"=== Escalation Router Status ===")
    print(f"  queue total entries: {len(queue)}")
    print(f"  sent entries:        {len(sent_ts)}")
    print(f"  pending critical:    {len(pending)}")
    print(f"  total_sent:          {state.get('total_sent', 0)}")
    print(f"  last_sent_ts:        {state.get('last_sent_ts', 'never')}")
    if pending:
        print(f"\n  Pending:")
        for r in pending[:5]:
            print(f"    [{r['ts'][:19]}] {r['monitor']}  {r['summary'][:60]}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["poll", "status", "test-enqueue"])
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()

    if args.command == "poll":
        if args.once:
            print(json.dumps(poll_once(), indent=2))
        else:
            poll_forever()
    elif args.command == "status":
        status()
    elif args.command == "test-enqueue":
        ts = enqueue_critical(
            monitor="test",
            tier="critical",
            summary="Synthetic test fault for escalation router",
            details={"test": True},
        )
        print(f"enqueued at {ts}")


if __name__ == "__main__":
    main()
