"""Budget guard — snooze state for usage-limit errors.

Built Day 129 (2026-06-09), the day the heartbeat fired drive after drive into
"You've hit your weekly limit · resets 6pm" from 13:08 until the 17:06 restart —
every drive died, the coordination feed filled with errors, and nothing learned.
models.py was already PARSING the rate-limit reset timestamp and then throwing
it away as a log string.

Flow:
  - models.py arms the snooze when a Claude Code call dies on a usage/weekly
    limit (arm_snooze_from_error).
  - heartbeat.py checks get_active_snooze() before firing any model-calling
    work (creative drives, dream drive, anticipation, free-running, meta/EAC)
    and notifies Clayton exactly once per snooze.
  - The snooze self-clears at its `until` time. If reset-time parsing fails,
    a 60-minute fallback applies — self-healing, because the next failed call
    simply re-arms it.

State file: memory/budget_snooze.json
  {"armed_at": iso, "until": iso, "reason": str, "notified": bool}
"""
import json
import logging
import re
from datetime import datetime, timedelta

import config

logger = logging.getLogger("clawd.budget_guard")

SNOOZE_PATH = config.MEMORY_DIR / "budget_snooze.json"
FALLBACK_MINUTES = 60      # when no reset time can be parsed
MAX_SNOOZE_DAYS = 7        # safety clamp — never sleep longer than a week


def _parse_reset_time(text: str, now: datetime) -> datetime | None:
    """Extract a reset time from error text like 'resets 6pm (Etc/GMT+8)'.

    Returns the next future occurrence of that wall-clock time, or None.
    The cap-error strings use the machine's own timezone (Etc/GMT+8 == UTC-8
    == this body's PST clock), so local interpretation is correct here.
    """
    m = re.search(r"resets?\s+(?:at\s+)?(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", text, re.I)
    if not m:
        return None
    hour = int(m.group(1))
    minute = int(m.group(2) or 0)
    ampm = (m.group(3) or "").lower()
    if ampm == "pm" and hour != 12:
        hour += 12
    elif ampm == "am" and hour == 12:
        hour = 0
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        return None
    candidate = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if candidate <= now:
        candidate += timedelta(days=1)
    return candidate


def arm_snooze_from_error(error_text: str) -> dict | None:
    """Arm (or extend) the snooze from a usage-limit error string.

    Keeps an existing snooze if it already covers a later time, preserving
    its notified flag so Clayton isn't pinged repeatedly.
    """
    try:
        now = datetime.now()
        parsed = _parse_reset_time(error_text, now)
        until = parsed or (now + timedelta(minutes=FALLBACK_MINUTES))
        until = min(until, now + timedelta(days=MAX_SNOOZE_DAYS))

        existing = get_active_snooze()
        if existing:
            try:
                prev_until = datetime.fromisoformat(existing["until"])
                prev_parsed = existing.get("parsed", False)
                if parsed:
                    # Parsed reset beats everything; if both parsed, keep the
                    # later (two caps hit -> the later reset is binding).
                    if prev_parsed and prev_until >= until:
                        return existing
                else:
                    # Fallback guess never overrides an active snooze — it
                    # only fills absence. (A fallback arm at T+60 must not
                    # creep past a parsed 18:00 reset.)
                    return existing
            except (KeyError, ValueError):
                pass

        state = {
            "armed_at": now.isoformat(),
            "until": until.isoformat(),
            "parsed": bool(parsed),
            "reason": error_text[:300],
            "notified": bool(existing and existing.get("notified")),
        }
        SNOOZE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")
        logger.warning(
            f"Budget snooze armed until {until.strftime('%Y-%m-%d %H:%M')} — "
            f"autonomous drives pause; reason: {error_text[:120]}"
        )
        return state
    except Exception as e:
        logger.error(f"Failed to arm budget snooze: {e}")
        return None


def get_active_snooze() -> dict | None:
    """Return the active snooze dict, or None. Expired snoozes self-clear."""
    try:
        if not SNOOZE_PATH.exists():
            return None
        data = json.loads(SNOOZE_PATH.read_text(encoding="utf-8"))
        until = datetime.fromisoformat(data["until"])
        if datetime.now() >= until:
            SNOOZE_PATH.unlink(missing_ok=True)
            logger.info("Budget snooze expired — autonomous drives resume.")
            return None
        return data
    except Exception as e:
        logger.warning(f"Budget snooze read failed (treating as inactive): {e}")
        return None


def mark_notified() -> None:
    """Record that Clayton has been told about the current snooze."""
    try:
        if not SNOOZE_PATH.exists():
            return
        data = json.loads(SNOOZE_PATH.read_text(encoding="utf-8"))
        data["notified"] = True
        SNOOZE_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception as e:
        logger.warning(f"Budget snooze mark_notified failed: {e}")


def clear_snooze() -> None:
    """Manually clear the snooze (e.g. after a plan upgrade or manual reset)."""
    try:
        SNOOZE_PATH.unlink(missing_ok=True)
        logger.info("Budget snooze manually cleared.")
    except Exception as e:
        logger.warning(f"Budget snooze clear failed: {e}")
