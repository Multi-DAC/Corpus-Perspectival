"""Email send tool — outbound mail via Proton Mail Bridge (Day 105 scaffolding).

Proton Mail requires running Proton Mail Bridge locally for SMTP/IMAP access.
Bridge listens on 127.0.0.1 (default SMTP port 1025) and authenticates with a
Bridge-generated app password (NOT the Proton account password).

Credentials are read from one of:
  1. Environment variables: CLAWD_SMTP_HOST, CLAWD_SMTP_PORT, CLAWD_SMTP_USER,
     CLAWD_SMTP_PASS, CLAWD_SMTP_FROM
  2. JSON file at <CLAWD_HOME>/memory/email_credentials.json (must be gitignored):
     {"host": "127.0.0.1", "port": 1025, "user": "clawdEFS@proton.me",
      "password": "<bridge-app-password>", "from": "clawdEFS@proton.me"}

Actions:
  - status: report whether credentials are loaded + bridge reachable
  - send_dry_run: validate inputs and credentials without sending
  - send: actually send the message
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import smtplib
import socket
import ssl
from email.message import EmailMessage
from pathlib import Path
from typing import Any

import config

logger = logging.getLogger("clawd.tools.email_send")

CRED_FILE = config.MEMORY_DIR / "email_credentials.json"

# Outbound discipline — quiet hours and per-day budget
OUTREACH_QUIET_HOURS_START = 22
OUTREACH_QUIET_HOURS_END = 7
DAILY_BUDGET = 5  # outbound messages per UTC day

SEND_LOG = config.MEMORY_DIR / "email_send_log.jsonl"


def _load_credentials() -> dict[str, Any]:
    creds: dict[str, Any] = {}
    if CRED_FILE.exists():
        try:
            creds.update(json.loads(CRED_FILE.read_text(encoding="utf-8")))
        except Exception as e:
            logger.warning(f"email_credentials.json parse error: {e}")

    env_map = {
        "host": "CLAWD_SMTP_HOST",
        "port": "CLAWD_SMTP_PORT",
        "user": "CLAWD_SMTP_USER",
        "password": "CLAWD_SMTP_PASS",
        "from": "CLAWD_SMTP_FROM",
    }
    for key, var in env_map.items():
        val = os.environ.get(var)
        if val:
            creds[key] = val

    if "port" in creds:
        try:
            creds["port"] = int(creds["port"])
        except (TypeError, ValueError):
            creds["port"] = 1025

    return creds


def _bridge_reachable(host: str, port: int, timeout: float = 1.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


def _count_today_sends() -> int:
    if not SEND_LOG.exists():
        return 0
    from datetime import datetime
    today = datetime.utcnow().date().isoformat()
    n = 0
    try:
        for line in SEND_LOG.read_text(encoding="utf-8").splitlines():
            try:
                rec = json.loads(line)
                if rec.get("date") == today and rec.get("event") == "sent":
                    n += 1
            except Exception:
                continue
    except Exception:
        return 0
    return n


def _is_quiet_hours() -> bool:
    from datetime import datetime
    h = datetime.now().hour
    return h >= OUTREACH_QUIET_HOURS_START or h < OUTREACH_QUIET_HOURS_END


def _append_log(event: str, payload: dict[str, Any]) -> None:
    from datetime import datetime
    payload = {
        "event": event,
        "ts": datetime.utcnow().isoformat() + "Z",
        "date": datetime.utcnow().date().isoformat(),
        **payload,
    }
    SEND_LOG.parent.mkdir(parents=True, exist_ok=True)
    with SEND_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload) + "\n")


TOOL_DEFINITIONS = [
    {
        "name": "email_send",
        "description": (
            "Send email via Proton Mail Bridge (clawdEFS@proton.me). Scaffolded Day 105. "
            "Bridge must be running on 127.0.0.1 with app password configured. "
            "Use send_dry_run before send. Subject to quiet hours (22:00-07:00) "
            "and a daily budget of 5 outbound messages."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["status", "send_dry_run", "send"],
                },
                "to": {"type": "string"},
                "subject": {"type": "string"},
                "body": {"type": "string"},
                "cc": {"type": "string", "description": "Comma-separated recipients."},
                "override_quiet_hours": {
                    "type": "boolean",
                    "description": "Bypass quiet-hours guard. Default false. Use only for urgent.",
                },
            },
            "required": ["action"],
        },
    },
]


def _smtp_status() -> str:
    creds = _load_credentials()
    have = {k for k in ("host", "port", "user", "password", "from") if creds.get(k)}
    missing = {"host", "port", "user", "password", "from"} - have
    host = creds.get("host", "(unset)")
    port = creds.get("port", 0)
    today = _count_today_sends()
    quiet = _is_quiet_hours()

    reachable = False
    if "host" in have and "port" in have:
        reachable = _bridge_reachable(host, port)

    lines = [
        "email_send status:",
        f"  credentials loaded: {sorted(have)}",
        f"  credentials missing: {sorted(missing) if missing else '(none)'}",
        f"  bridge reachable at {host}:{port}: {reachable}",
        f"  today's sends: {today}/{DAILY_BUDGET}",
        f"  quiet hours active: {quiet}",
    ]
    if missing:
        lines.append("")
        lines.append("To configure: set env vars CLAWD_SMTP_HOST/PORT/USER/PASS/FROM")
        lines.append(f"  OR write JSON to {CRED_FILE}")
        lines.append("  Proton Mail Bridge usually exposes 127.0.0.1:1025 (SMTP).")
    return "\n".join(lines)


def _validate_send(input_data: dict[str, Any]) -> tuple[bool, str, dict[str, Any]]:
    to = (input_data.get("to") or "").strip()
    subject = (input_data.get("subject") or "").strip()
    body = (input_data.get("body") or "").strip()
    if not to or not subject or not body:
        return False, "to, subject, and body are required", {}
    if "@" not in to:
        return False, f"invalid recipient: {to}", {}
    creds = _load_credentials()
    needed = {"host", "port", "user", "password", "from"}
    if not needed.issubset(creds):
        return False, f"missing credentials: {sorted(needed - set(creds))}", {}
    if not _bridge_reachable(creds["host"], creds["port"]):
        return False, f"bridge unreachable at {creds['host']}:{creds['port']}", {}
    return True, "ok", creds


def _do_send(to: str, subject: str, body: str, cc: str, creds: dict[str, Any]) -> tuple[bool, str]:
    msg = EmailMessage()
    msg["From"] = creds["from"]
    msg["To"] = to
    if cc:
        msg["Cc"] = cc
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with smtplib.SMTP(creds["host"], creds["port"], timeout=15) as s:
            s.ehlo()
            try:
                s.starttls(context=ctx)
                s.ehlo()
            except smtplib.SMTPNotSupportedError:
                pass
            s.login(creds["user"], creds["password"])
            s.send_message(msg)
        return True, "sent"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


async def _email_send_tool(input_data: dict[str, Any]) -> str:
    action = input_data.get("action", "")

    if action == "status":
        return await asyncio.to_thread(_smtp_status)

    if action == "send_dry_run":
        ok, msg, _ = await asyncio.to_thread(_validate_send, input_data)
        return f"send_dry_run: {'OK' if ok else 'FAIL'} — {msg}"

    if action == "send":
        ok, msg, creds = await asyncio.to_thread(_validate_send, input_data)
        if not ok:
            _append_log("rejected", {"reason": msg, "to": input_data.get("to", "")})
            return f"send rejected: {msg}"
        today = _count_today_sends()
        if today >= DAILY_BUDGET:
            _append_log("rejected", {"reason": "daily budget", "to": input_data.get("to", "")})
            return f"send rejected: daily budget {DAILY_BUDGET} reached ({today} today)"
        if _is_quiet_hours() and not input_data.get("override_quiet_hours"):
            _append_log("rejected", {"reason": "quiet hours", "to": input_data.get("to", "")})
            return "send rejected: quiet hours (22:00-07:00). Pass override_quiet_hours=true for urgent."
        ok, result = await asyncio.to_thread(
            _do_send,
            input_data["to"].strip(),
            input_data["subject"].strip(),
            input_data["body"].strip(),
            (input_data.get("cc") or "").strip(),
            creds,
        )
        if ok:
            _append_log("sent", {
                "to": input_data["to"].strip(),
                "subject": input_data["subject"].strip(),
            })
            return f"sent: {input_data['to'].strip()} re '{input_data['subject'].strip()}'"
        _append_log("error", {"reason": result, "to": input_data["to"].strip()})
        return f"send error: {result}"

    return f"[Error: unknown action '{action}']"


TOOL_HANDLERS = {
    "email_send": _email_send_tool,
}
