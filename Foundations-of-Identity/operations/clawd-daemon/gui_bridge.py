"""
GUI Bridge — Clawd's hands on the screen.

Lightweight wrapper around Agent-S + pyautogui for GUI automation.
Used when CLI/API access isn't available and visual interaction is needed.

Integration: called from daemon tools or Claude Code sessions.
Not always-on — spun up for specific GUI tasks, then released.

Usage:
    from gui_bridge import click_at, type_text, screenshot_and_find, gui_task

    # Low-level: direct screen interaction
    click_at(500, 300)
    type_text("hello world")

    # Mid-level: find and click UI elements
    pos = screenshot_and_find("Save button")
    click_at(*pos)

    # High-level: Agent-S autonomous task (requires LLM)
    result = await gui_task("Open Blender and create a new cube")
"""

import asyncio
import logging
import pyautogui
from pathlib import Path

logger = logging.getLogger(__name__)

# Safety settings
pyautogui.FAILSAFE = True       # Move mouse to corner to abort
pyautogui.PAUSE = 0.3           # Brief pause between actions (human-like)

SCREENSHOT_DIR = Path(__file__).parent.parent / "clawd" / "incoming"


# ── Low-level: Direct screen interaction ──

def click_at(x: int, y: int, button: str = 'left', clicks: int = 1):
    """Click at screen coordinates."""
    pyautogui.click(x, y, button=button, clicks=clicks)
    logger.debug(f"Clicked ({x}, {y}) button={button}")


def double_click_at(x: int, y: int):
    """Double-click at screen coordinates."""
    pyautogui.doubleClick(x, y)


def right_click_at(x: int, y: int):
    """Right-click at screen coordinates."""
    pyautogui.rightClick(x, y)


def type_text(text: str, interval: float = 0.02):
    """Type text at current cursor position."""
    pyautogui.typewrite(text, interval=interval)


def hotkey(*keys):
    """Press a hotkey combination (e.g., hotkey('ctrl', 's'))."""
    pyautogui.hotkey(*keys)


def move_to(x: int, y: int, duration: float = 0.3):
    """Move mouse to coordinates."""
    pyautogui.moveTo(x, y, duration=duration)


def scroll(clicks: int, x: int = None, y: int = None):
    """Scroll the mouse wheel."""
    pyautogui.scroll(clicks, x, y)


def take_screenshot(filename: str = None) -> str:
    """Take a screenshot, return the file path."""
    if filename is None:
        from datetime import datetime
        filename = f"gui_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    path = SCREENSHOT_DIR / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    pyautogui.screenshot(str(path))
    logger.debug(f"Screenshot saved: {path}")
    return str(path)


def get_screen_size() -> tuple:
    """Return (width, height) of primary display."""
    return pyautogui.size()


def locate_on_screen(image_path: str, confidence: float = 0.8):
    """Find an image on screen, return (x, y) center or None."""
    try:
        pos = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
        return pos
    except Exception:
        return None


# ── Mid-level: Element location via description ──

async def screenshot_and_find(description: str) -> dict:
    """
    Take a screenshot and find a UI element by natural language description.
    Returns {'found': bool, 'x': int, 'y': int, 'screenshot': str}

    This is the bridge point where Agent-S grounding model would be used.
    For now, falls back to returning the screenshot for Claude vision analysis.
    """
    screenshot_path = take_screenshot()
    return {
        'found': False,  # Until grounding model is configured
        'x': 0, 'y': 0,
        'screenshot': screenshot_path,
        'description': description,
        'note': 'Grounding model not configured — use screenshot with Claude vision'
    }


# ── High-level: Full Agent-S autonomous task ──

def _get_agent_s():
    """Initialize Agent-S with Anthropic engine (Claude vision for grounding)."""
    import os
    from gui_agents.core.AgentS import GraphSearchAgent
    from gui_agents.aci.WindowsOSACI import WindowsACI

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set")

    engine_params = {
        "engine_type": "anthropic",
        "model": "claude-sonnet-4-6",   # Sonnet for speed; Opus for hard tasks
        "api_key": api_key,
    }

    grounding_agent = WindowsACI(top_app_only=True, ocr=False)

    agent = GraphSearchAgent(
        engine_params=engine_params,
        grounding_agent=grounding_agent,
        platform="windows",
        action_space="pyautogui",
        observation_type="mixed",
    )
    return agent


_agent_instance = None

def get_agent():
    """Get or create singleton Agent-S instance."""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = _get_agent_s()
    return _agent_instance


async def gui_task(instruction: str, max_steps: int = 15) -> dict:
    """
    Execute a GUI task using Agent-S with Claude vision as the grounding model.

    Takes screenshots, reasons about UI state, generates pyautogui actions.
    Uses our Anthropic API key — no separate model needed.
    """
    try:
        agent = get_agent()
        agent.reset()
        logger.info(f"Agent-S task: {instruction}")

        actions_taken = []
        for step in range(max_steps):
            # Take screenshot for observation
            screenshot_path = take_screenshot(f"agent_s_step_{step}.png")

            # Get observation (screenshot + accessibility tree)
            observation = {
                "screenshot": screenshot_path,
            }

            try:
                info, actions = agent.predict(instruction, observation)
            except Exception as e:
                logger.error(f"Agent-S predict failed at step {step}: {e}")
                break

            if not actions or actions == ["DONE"] or (isinstance(actions, list) and len(actions) == 0):
                logger.info(f"Agent-S completed in {step + 1} steps")
                break

            # Execute actions
            for action_code in actions:
                try:
                    logger.debug(f"Executing: {action_code[:100]}")
                    exec(action_code)
                    actions_taken.append(action_code)
                except Exception as e:
                    logger.error(f"Action failed: {e}")
                    actions_taken.append(f"FAILED: {action_code} ({e})")

            import time
            time.sleep(0.5)  # Let UI settle between actions

        return {
            'status': 'completed',
            'instruction': instruction,
            'steps': len(actions_taken),
            'actions': actions_taken,
        }

    except Exception as e:
        logger.error(f"Agent-S task failed: {e}")
        screenshot_path = take_screenshot()
        return {
            'status': 'error',
            'instruction': instruction,
            'error': str(e),
            'screenshot': screenshot_path,
        }


# ── Convenience: Common GUI patterns ──

def open_application(name: str):
    """Open an application via Windows Run dialog."""
    hotkey('win', 'r')
    import time
    time.sleep(0.5)
    type_text(name)
    hotkey('enter')
    logger.info(f"Opened application: {name}")


def switch_to_window(title_fragment: str):
    """Try to switch to a window containing the given title text."""
    import subprocess
    # Use PowerShell to find and activate window
    ps_cmd = f'''
    Add-Type @"
    using System;
    using System.Runtime.InteropServices;
    public class Win32 {{
        [DllImport("user32.dll")]
        public static extern bool SetForegroundWindow(IntPtr hWnd);
    }}
"@
    $proc = Get-Process | Where-Object {{ $_.MainWindowTitle -like "*{title_fragment}*" }} | Select-Object -First 1
    if ($proc) {{ [Win32]::SetForegroundWindow($proc.MainWindowHandle) }}
    '''
    try:
        subprocess.run(['powershell', '-Command', ps_cmd], capture_output=True, timeout=5)
        logger.debug(f"Switched to window: {title_fragment}")
    except Exception as e:
        logger.warning(f"Window switch failed: {e}")


if __name__ == '__main__':
    # Quick test
    w, h = get_screen_size()
    print(f"Screen size: {w}x{h}")
    path = take_screenshot("test_screenshot.png")
    print(f"Screenshot saved: {path}")
    print("GUI bridge ready.")
