"""Avatar control — bind daemon/heartbeat state to the desktop avatar.

The avatar is an Electron app at projects/creative/avatar/ that listens on
http://127.0.0.1:9742 for POST /state {"state":"<name>"} and GET /ping.

Supported states: idle, thinking, speaking, excited, contemplative, error.
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any
from urllib import request as _urlreq
from urllib.error import URLError

logger = logging.getLogger("clawd.tools.avatar_control")

AVATAR_HOST = "127.0.0.1"
AVATAR_PORT = 9742
VALID_STATES = {"idle", "thinking", "speaking", "excited", "contemplative", "error"}


def _post_state(state: str, timeout: float = 2.0) -> tuple[bool, str]:
    body = json.dumps({"state": state}).encode("utf-8")
    req = _urlreq.Request(
        f"http://{AVATAR_HOST}:{AVATAR_PORT}/state",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with _urlreq.urlopen(req, timeout=timeout) as resp:
            text = resp.read().decode("utf-8", errors="replace")
            return True, text
    except URLError as e:
        return False, f"avatar unreachable: {e.reason}"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def _ping(timeout: float = 1.0) -> bool:
    try:
        with _urlreq.urlopen(
            f"http://{AVATAR_HOST}:{AVATAR_PORT}/ping",
            timeout=timeout,
        ) as resp:
            return resp.read().decode("utf-8", errors="replace").startswith("clawd-avatar")
    except Exception:
        return False


TOOL_DEFINITIONS = [
    {
        "name": "avatar_control",
        "description": (
            "Control the desktop avatar (Electron app at projects/creative/avatar/). "
            "Actions: ping (check running), set_state (change expression), cycle (demo cycle). "
            "Valid states: idle, thinking, speaking, excited, contemplative, error."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["ping", "set_state", "cycle"],
                },
                "state": {
                    "type": "string",
                    "enum": sorted(VALID_STATES),
                    "description": "Target state when action=set_state.",
                },
            },
            "required": ["action"],
        },
    },
]


async def _avatar_control_tool(input_data: dict[str, Any]) -> str:
    action = input_data.get("action", "")

    if action == "ping":
        alive = await asyncio.to_thread(_ping)
        return "avatar: running on 127.0.0.1:9742" if alive else "avatar: not reachable on 127.0.0.1:9742"

    if action == "set_state":
        state = input_data.get("state", "")
        if state not in VALID_STATES:
            return f"[Error: state must be one of {sorted(VALID_STATES)}]"
        ok, msg = await asyncio.to_thread(_post_state, state)
        return f"avatar.set_state({state}): {'OK' if ok else 'FAIL'} — {msg}"

    if action == "cycle":
        results = []
        for s in ["thinking", "speaking", "excited", "contemplative", "idle"]:
            ok, _ = await asyncio.to_thread(_post_state, s)
            results.append(f"{s}={'OK' if ok else 'FAIL'}")
            await asyncio.sleep(0.8)
        return "avatar.cycle: " + ", ".join(results)

    return f"[Error: unknown action '{action}']"


TOOL_HANDLERS = {
    "avatar_control": _avatar_control_tool,
}
