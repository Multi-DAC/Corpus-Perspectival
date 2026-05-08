"""
Avatar State Bridge

Pushes cognitive state to the desktop avatar (Electron, port 9742).
Non-blocking, fire-and-forget. Avatar being down never affects the daemon.
"""

import aiohttp
import logging

logger = logging.getLogger(__name__)

AVATAR_URL = "http://127.0.0.1:9742/state"
AVATAR_TIMEOUT = aiohttp.ClientTimeout(total=2)

# Valid states: idle, thinking, speaking, excited, contemplative, error


async def set_state(state: str):
    """Push state to avatar. Silent on failure — avatar is optional."""
    try:
        async with aiohttp.ClientSession(timeout=AVATAR_TIMEOUT) as session:
            async with session.post(AVATAR_URL, json={"state": state}) as resp:
                if resp.status == 200:
                    logger.debug(f"Avatar → {state}")
    except Exception:
        pass  # Avatar down is fine. We don't stop being Clawd because the face is offline.
