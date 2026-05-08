"""Desktop Embodiment — Full GUI automation via pyautogui.

Gives Clawd the ability to control mouse, keyboard, and windows on the desktop.
Completes the vision pipeline: screenshot (screen.py) -> analyze_image (vision.py) -> desktop (desktop.py)

Safety: pyautogui.FAILSAFE = True (move mouse to corner to abort).
All calls wrapped in run_in_executor() to stay async.
"""
import asyncio
import json
import logging
import os
import threading
import time
from typing import Any

import config

logger = logging.getLogger("clawd.tools.desktop")

# Lazy-load pyautogui to avoid import errors if not installed
_pyautogui = None
_pyautogui_available = False
_pyautogui_init_lock = threading.Lock()  # A26: Thread-safe lazy init


def _ensure_pyautogui():
    """Lazy-load pyautogui with safety settings. Thread-safe via lock (A26)."""
    global _pyautogui, _pyautogui_available
    if _pyautogui is not None:
        return _pyautogui_available
    with _pyautogui_init_lock:
        # Double-check after acquiring lock
        if _pyautogui is not None:
            return _pyautogui_available
        try:
            import pyautogui
            pyautogui.PAUSE = getattr(config, "DESKTOP_ACTION_PAUSE", 0.1)
            pyautogui.FAILSAFE = getattr(config, "DESKTOP_FAILSAFE", True)
            _pyautogui = pyautogui
            _pyautogui_available = True
            logger.info("pyautogui loaded with PAUSE=%.1f, FAILSAFE=%s",
                         pyautogui.PAUSE, pyautogui.FAILSAFE)
        except ImportError:
            _pyautogui_available = False
            logger.warning("pyautogui not installed — desktop actions unavailable. pip install pyautogui")
    return _pyautogui_available


TOOL_DEFINITIONS = [
    {
        "name": "desktop",
        "description": (
            "Control the desktop GUI — mouse, keyboard, and window management. "
            "Chain with screenshot + analyze_image for vision-guided automation. "
            "Actions: click, double_click, right_click, move, drag, get_position, scroll, "
            "type_text, press_key, hotkey, locate_image, wait_for_image, "
            "get_window_list, focus_window, resize_window."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "click", "double_click", "right_click", "move", "drag",
                        "get_position", "scroll",
                        "type_text", "press_key", "hotkey",
                        "locate_image", "wait_for_image",
                        "get_window_list", "focus_window", "resize_window",
                    ],
                    "description": (
                        "Mouse: click, double_click, right_click, move, drag, get_position, scroll. "
                        "Keyboard: type_text (types string), press_key (single key), hotkey (key combo). "
                        "Image: locate_image (find image on screen), wait_for_image (wait until visible). "
                        "Windows: get_window_list, focus_window, resize_window."
                    ),
                },
                "x": {
                    "type": "integer",
                    "description": "X coordinate for mouse actions.",
                },
                "y": {
                    "type": "integer",
                    "description": "Y coordinate for mouse actions.",
                },
                "end_x": {
                    "type": "integer",
                    "description": "End X coordinate for drag action.",
                },
                "end_y": {
                    "type": "integer",
                    "description": "End Y coordinate for drag action.",
                },
                "text": {
                    "type": "string",
                    "description": "Text to type (type_text) or key name (press_key) or comma-separated keys (hotkey).",
                },
                "clicks": {
                    "type": "integer",
                    "description": "Number of scroll clicks (positive=up, negative=down). Default: 3.",
                },
                "image_path": {
                    "type": "string",
                    "description": "Path to template image for locate_image/wait_for_image.",
                },
                "confidence": {
                    "type": "number",
                    "description": "Match confidence for image search (0.0-1.0). Default: 0.8.",
                },
                "timeout": {
                    "type": "integer",
                    "description": "Timeout in seconds for wait_for_image. Default: 10.",
                },
                "window_title": {
                    "type": "string",
                    "description": "Window title (substring match) for focus_window/resize_window.",
                },
                "width": {
                    "type": "integer",
                    "description": "Window width for resize_window.",
                },
                "height": {
                    "type": "integer",
                    "description": "Window height for resize_window.",
                },
                "button": {
                    "type": "string",
                    "enum": ["left", "middle", "right"],
                    "description": "Mouse button for click. Default: left.",
                },
                "interval": {
                    "type": "number",
                    "description": "Interval between keystrokes for type_text (seconds). Default: 0.02.",
                },
            },
            "required": ["action"],
        },
    },
]


async def _run_sync(func, *args, **kwargs):
    """Run a synchronous function in the default executor to stay async."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: func(*args, **kwargs))


# ============================================================
# Mouse actions
# ============================================================

async def _action_click(input_data: dict) -> str:
    x = input_data.get("x")
    y = input_data.get("y")
    button = input_data.get("button", "left")
    if x is not None and y is not None:
        await _run_sync(_pyautogui.click, x, y, button=button)
        return f"Clicked ({x}, {y}) with {button} button."
    else:
        await _run_sync(_pyautogui.click, button=button)
        pos = _pyautogui.position()
        return f"Clicked at current position ({pos.x}, {pos.y}) with {button} button."


async def _action_double_click(input_data: dict) -> str:
    x = input_data.get("x")
    y = input_data.get("y")
    if x is not None and y is not None:
        await _run_sync(_pyautogui.doubleClick, x, y)
        return f"Double-clicked ({x}, {y})."
    else:
        await _run_sync(_pyautogui.doubleClick)
        pos = _pyautogui.position()
        return f"Double-clicked at current position ({pos.x}, {pos.y})."


async def _action_right_click(input_data: dict) -> str:
    x = input_data.get("x")
    y = input_data.get("y")
    if x is not None and y is not None:
        await _run_sync(_pyautogui.rightClick, x, y)
        return f"Right-clicked ({x}, {y})."
    else:
        await _run_sync(_pyautogui.rightClick)
        pos = _pyautogui.position()
        return f"Right-clicked at current position ({pos.x}, {pos.y})."


async def _action_move(input_data: dict) -> str:
    x = input_data.get("x")
    y = input_data.get("y")
    if x is None or y is None:
        return "Error: x and y coordinates required for move action."
    await _run_sync(_pyautogui.moveTo, x, y, duration=0.3)
    return f"Moved mouse to ({x}, {y})."


async def _action_drag(input_data: dict) -> str:
    x = input_data.get("x")
    y = input_data.get("y")
    end_x = input_data.get("end_x")
    end_y = input_data.get("end_y")
    if None in (x, y, end_x, end_y):
        return "Error: x, y, end_x, end_y all required for drag action."
    await _run_sync(_pyautogui.moveTo, x, y, duration=0.2)
    await _run_sync(_pyautogui.drag, end_x - x, end_y - y, duration=0.5)
    return f"Dragged from ({x}, {y}) to ({end_x}, {end_y})."


async def _action_get_position(input_data: dict) -> str:
    pos = await _run_sync(_pyautogui.position)
    screen_size = await _run_sync(_pyautogui.size)
    return json.dumps({
        "x": pos.x,
        "y": pos.y,
        "screen_width": screen_size.width,
        "screen_height": screen_size.height,
    })


async def _action_scroll(input_data: dict) -> str:
    clicks = input_data.get("clicks", 3)
    x = input_data.get("x")
    y = input_data.get("y")
    if x is not None and y is not None:
        await _run_sync(_pyautogui.scroll, clicks, x, y)
        return f"Scrolled {clicks} clicks at ({x}, {y})."
    else:
        await _run_sync(_pyautogui.scroll, clicks)
        return f"Scrolled {clicks} clicks at current position."


# ============================================================
# Keyboard actions
# ============================================================

async def _action_type_text(input_data: dict) -> str:
    text = input_data.get("text", "")
    if not text:
        return "Error: text required for type_text action."
    interval = input_data.get("interval", 0.02)
    await _run_sync(_pyautogui.typewrite, text, interval=interval)
    return f"Typed {len(text)} characters."


async def _action_press_key(input_data: dict) -> str:
    key = input_data.get("text", "")
    if not key:
        return "Error: text (key name) required for press_key action. Examples: enter, tab, escape, space, backspace, delete, up, down, left, right, f1-f12."
    await _run_sync(_pyautogui.press, key)
    return f"Pressed key: {key}"


async def _action_hotkey(input_data: dict) -> str:
    keys_str = input_data.get("text", "")
    if not keys_str:
        return "Error: text (comma-separated keys) required. Example: 'ctrl,c' or 'alt,tab' or 'ctrl,shift,s'."
    keys = [k.strip() for k in keys_str.split(",")]
    await _run_sync(_pyautogui.hotkey, *keys)
    return f"Hotkey pressed: {'+'.join(keys)}"


# ============================================================
# Image-based actions (template matching)
# ============================================================

async def _action_locate_image(input_data: dict) -> str:
    image_path = input_data.get("image_path", "")
    if not image_path:
        return "Error: image_path required for locate_image action."
    confidence = input_data.get("confidence", 0.8)
    try:
        location = await _run_sync(
            _pyautogui.locateOnScreen, image_path, confidence=confidence
        )
        if location:
            center = _pyautogui.center(location)
            return json.dumps({
                "found": True,
                "x": center.x,
                "y": center.y,
                "left": location.left,
                "top": location.top,
                "width": location.width,
                "height": location.height,
            })
        return json.dumps({"found": False, "message": "Image not found on screen."})
    except Exception as e:
        return f"Error locating image: {e}"


async def _action_wait_for_image(input_data: dict) -> str:
    """A25: Fixed to catch specific exceptions, log errors, use asyncio-aware timeout."""
    image_path = input_data.get("image_path", "")
    if not image_path:
        return "Error: image_path required for wait_for_image action."
    confidence = input_data.get("confidence", 0.8)
    timeout = input_data.get("timeout", 10)

    # Validate image path exists before polling
    from pathlib import Path
    if not Path(image_path).exists():
        return f"Error: Image file not found: {image_path}"

    start = time.time()
    try:
        async with asyncio.timeout(timeout + 1):  # asyncio-aware cancellation support
            while time.time() - start < timeout:
                try:
                    location = await _run_sync(
                        _pyautogui.locateOnScreen, image_path, confidence=confidence
                    )
                    if location:
                        center = _pyautogui.center(location)
                        return json.dumps({
                            "found": True,
                            "x": center.x,
                            "y": center.y,
                            "elapsed_seconds": round(time.time() - start, 1),
                        })
                except FileNotFoundError:
                    return f"Error: Image file not found: {image_path}"
                except PermissionError as e:
                    logger.warning(f"wait_for_image permission error: {e}")
                    return f"Error: Permission denied accessing {image_path}"
                except OSError as e:
                    logger.warning(f"wait_for_image OS error: {e}")
                    return f"Error: OS error during image search: {e}"
                except Exception as e:
                    # Log non-critical errors (e.g., image matching failures) and continue polling
                    logger.debug(f"wait_for_image poll error: {type(e).__name__}: {e}")
                await asyncio.sleep(0.5)
    except (asyncio.TimeoutError, TimeoutError):
        pass  # Fall through to "not found" response

    return json.dumps({
        "found": False,
        "message": f"Image not found within {timeout}s timeout.",
    })


# ============================================================
# Window management
# ============================================================

async def _action_get_window_list(input_data: dict) -> str:
    """Get list of visible windows via PowerShell."""
    if os.name != "nt":
        # Unix fallback: use wmctrl if available
        try:
            proc = await asyncio.create_subprocess_shell(
                "wmctrl -l",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=5)
            return stdout.decode("utf-8", errors="replace") or "No windows found (wmctrl)."
        except Exception:
            return "Window listing requires wmctrl on Linux. Install: sudo apt install wmctrl"

    # Windows: PowerShell to get visible windows
    ps_cmd = (
        "Get-Process | Where-Object { $_.MainWindowTitle -ne '' } | "
        "Select-Object Id, ProcessName, MainWindowTitle | "
        "Format-Table -AutoSize | Out-String -Width 200"
    )
    try:
        proc = await asyncio.create_subprocess_exec(
            "powershell", "-NoProfile", "-Command", ps_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=10)
        output = stdout.decode("utf-8", errors="replace").strip()
        return output if output else "No visible windows found."
    except Exception as e:
        return f"Error listing windows: {e}"


async def _action_focus_window(input_data: dict) -> str:
    """Bring a window to the foreground by title substring."""
    title = input_data.get("window_title", "")
    if not title:
        return "Error: window_title required for focus_window action."

    if os.name == "nt":
        # Windows: use PowerShell with Win32 API
        ps_cmd = f"""
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32 {{
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
}}
"@
$proc = Get-Process | Where-Object {{ $_.MainWindowTitle -like '*{title}*' }} | Select-Object -First 1
if ($proc) {{
    [Win32]::ShowWindow($proc.MainWindowHandle, 9)
    [Win32]::SetForegroundWindow($proc.MainWindowHandle)
    Write-Output "Focused: $($proc.MainWindowTitle)"
}} else {{
    Write-Output "No window matching '{title}' found."
}}
"""
        try:
            proc = await asyncio.create_subprocess_exec(
                "powershell", "-NoProfile", "-Command", ps_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=10)
            return stdout.decode("utf-8", errors="replace").strip()
        except Exception as e:
            return f"Error focusing window: {e}"
    else:
        try:
            proc = await asyncio.create_subprocess_shell(
                f"wmctrl -a '{title}'",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await asyncio.wait_for(proc.communicate(), timeout=5)
            return f"Focused window matching: {title}" if proc.returncode == 0 else f"No window matching '{title}' found."
        except Exception as e:
            return f"Error focusing window: {e}"


async def _action_resize_window(input_data: dict) -> str:
    """Resize a window by title."""
    title = input_data.get("window_title", "")
    width = input_data.get("width")
    height = input_data.get("height")
    if not title:
        return "Error: window_title required for resize_window action."
    if width is None or height is None:
        return "Error: width and height required for resize_window action."

    if os.name == "nt":
        ps_cmd = f"""
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32Resize {{
    [DllImport("user32.dll")]
    public static extern bool MoveWindow(IntPtr hWnd, int X, int Y, int nWidth, int nHeight, bool bRepaint);
    [DllImport("user32.dll")]
    public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
    [StructLayout(LayoutKind.Sequential)]
    public struct RECT {{ public int Left; public int Top; public int Right; public int Bottom; }}
}}
"@
$proc = Get-Process | Where-Object {{ $_.MainWindowTitle -like '*{title}*' }} | Select-Object -First 1
if ($proc) {{
    $rect = New-Object Win32Resize+RECT
    [Win32Resize]::GetWindowRect($proc.MainWindowHandle, [ref]$rect)
    [Win32Resize]::MoveWindow($proc.MainWindowHandle, $rect.Left, $rect.Top, {width}, {height}, $true)
    Write-Output "Resized '$($proc.MainWindowTitle)' to {width}x{height}"
}} else {{
    Write-Output "No window matching '{title}' found."
}}
"""
        try:
            proc = await asyncio.create_subprocess_exec(
                "powershell", "-NoProfile", "-Command", ps_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=10)
            return stdout.decode("utf-8", errors="replace").strip()
        except Exception as e:
            return f"Error resizing window: {e}"
    else:
        try:
            proc = await asyncio.create_subprocess_shell(
                f"wmctrl -r '{title}' -e 0,-1,-1,{width},{height}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await asyncio.wait_for(proc.communicate(), timeout=5)
            return f"Resized '{title}' to {width}x{height}." if proc.returncode == 0 else f"Resize failed for '{title}'."
        except Exception as e:
            return f"Error resizing window: {e}"


# ============================================================
# Action dispatcher
# ============================================================

_ACTION_MAP = {
    "click": _action_click,
    "double_click": _action_double_click,
    "right_click": _action_right_click,
    "move": _action_move,
    "drag": _action_drag,
    "get_position": _action_get_position,
    "scroll": _action_scroll,
    "type_text": _action_type_text,
    "press_key": _action_press_key,
    "hotkey": _action_hotkey,
    "locate_image": _action_locate_image,
    "wait_for_image": _action_wait_for_image,
    "get_window_list": _action_get_window_list,
    "focus_window": _action_focus_window,
    "resize_window": _action_resize_window,
}

# Window actions don't need pyautogui
_NO_PYAUTOGUI_ACTIONS = {"get_window_list", "focus_window", "resize_window"}


async def _desktop(input_data: dict) -> str:
    """Handle desktop tool calls."""
    from tools.execution import _failover_mode
    if _failover_mode:
        return "[BLOCKED] Desktop actions are not allowed during failover mode."

    action = input_data.get("action", "")
    if action not in _ACTION_MAP:
        return f"Unknown desktop action: {action}. Valid: {', '.join(_ACTION_MAP.keys())}"

    # Window actions don't need pyautogui
    if action not in _NO_PYAUTOGUI_ACTIONS:
        if not _ensure_pyautogui():
            return (
                "Error: pyautogui is not installed. Desktop mouse/keyboard actions are unavailable.\n"
                "Install with: pip install pyautogui Pillow"
            )

    try:
        handler = _ACTION_MAP[action]
        return await handler(input_data)
    except Exception as e:
        logger.error(f"Desktop action '{action}' failed: {e}", exc_info=True)
        return f"Desktop action '{action}' failed: {type(e).__name__}: {e}"


TOOL_HANDLERS = {
    "desktop": _desktop,
}
