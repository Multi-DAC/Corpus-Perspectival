"""Screen tools — screenshot and clipboard interaction."""
import asyncio
import logging
import uuid
from pathlib import Path
from typing import Any

import config

logger = logging.getLogger("clawd.tools.screen")

TOOL_DEFINITIONS = [
    {
        "name": "screenshot",
        "description": "Take a screenshot of the screen. Saves PNG to CLAWD_HOME/output/. Can capture full screen or active window.",
        "input_schema": {
            "type": "object",
            "properties": {
                "mode": {
                    "type": "string",
                    "enum": ["full", "active_window"],
                    "description": "Capture mode: full (entire screen) or active_window. Default: full."
                },
                "ocr": {
                    "type": "boolean",
                    "description": "If true, also run OCR to extract text from the screenshot. Default: false."
                }
            },
            "required": []
        }
    },
    {
        "name": "clipboard",
        "description": "Read or write the system clipboard.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["read", "write"],
                    "description": "read: get clipboard contents. write: set clipboard contents."
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to clipboard (for write action)."
                }
            },
            "required": ["action"]
        }
    },
]


async def _screenshot(input_data: dict) -> str:
    """Take a screenshot using PowerShell System.Drawing."""
    mode = input_data.get("mode", "full")
    do_ocr = input_data.get("ocr", False)

    output_dir = config.CLAWD_HOME / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"screenshot_{uuid.uuid4().hex[:8]}.png"
    filepath = output_dir / filename

    if mode == "active_window":
        ps_script = f"""
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms
Add-Type @'
using System;
using System.Runtime.InteropServices;
public class Win32 {{
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
    [StructLayout(LayoutKind.Sequential)] public struct RECT {{
        public int Left; public int Top; public int Right; public int Bottom;
    }}
}}
'@
$hwnd = [Win32]::GetForegroundWindow()
$rect = New-Object Win32+RECT
[Win32]::GetWindowRect($hwnd, [ref]$rect) | Out-Null
$width = $rect.Right - $rect.Left
$height = $rect.Bottom - $rect.Top
$bmp = New-Object System.Drawing.Bitmap($width, $height)
$graphics = [System.Drawing.Graphics]::FromImage($bmp)
$graphics.CopyFromScreen($rect.Left, $rect.Top, 0, 0, $bmp.Size)
$bmp.Save('{filepath}')
$graphics.Dispose()
$bmp.Dispose()
Write-Output "OK $width x $height"
"""
    else:
        ps_script = f"""
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms
$screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bmp = New-Object System.Drawing.Bitmap($screen.Width, $screen.Height)
$graphics = [System.Drawing.Graphics]::FromImage($bmp)
$graphics.CopyFromScreen($screen.Location, [System.Drawing.Point]::Empty, $screen.Size)
$bmp.Save('{filepath}')
$graphics.Dispose()
$bmp.Dispose()
Write-Output "OK $($screen.Width) x $($screen.Height)"
"""

    try:
        proc = await asyncio.create_subprocess_exec(
            "powershell", "-Command", ps_script,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=15)

        if proc.returncode != 0:
            err = stderr.decode("utf-8", errors="replace")
            return f"Screenshot failed: {err[-300:]}"

        out = stdout.decode("utf-8", errors="replace").strip()
        result = f"Screenshot saved: {filepath} ({out})"

        # Optional OCR
        if do_ocr and filepath.exists():
            try:
                from tools.execution import _python_eval
                ocr_result = await _python_eval({
                    "code": f"""
import pytesseract
from PIL import Image
img = Image.open(r'{filepath}')
text = pytesseract.image_to_string(img)
print(text[:5000] if len(text) > 5000 else text)
""",
                    "timeout": 30,
                })
                result += f"\n\nOCR Text:\n{ocr_result}"
            except Exception as e:
                result += f"\n\nOCR failed: {e} (install pytesseract for OCR support)"

        return result

    except asyncio.TimeoutError:
        return "Screenshot timed out."
    except Exception as e:
        return f"Screenshot error: {type(e).__name__}: {e}"


async def _clipboard(input_data: dict) -> str:
    """Read or write the system clipboard via PowerShell."""
    action = input_data["action"]

    if action == "read":
        try:
            proc = await asyncio.create_subprocess_exec(
                "powershell", "-Command", "Get-Clipboard",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=10)
            content = stdout.decode("utf-8", errors="replace").strip()
            if not content:
                return "Clipboard is empty."
            if len(content) > 50_000:
                content = content[:50_000] + "\n[... truncated]"
            return f"Clipboard contents ({len(content)} chars):\n{content}"
        except asyncio.TimeoutError:
            return "Clipboard read timed out."
        except Exception as e:
            return f"Clipboard read error: {type(e).__name__}: {e}"

    elif action == "write":
        content = input_data.get("content", "")
        if not content:
            return "Error: content required for write action."
        try:
            proc = await asyncio.create_subprocess_exec(
                "powershell", "-Command", f"Set-Clipboard -Value {repr(content)}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await asyncio.wait_for(proc.communicate(), timeout=10)
            return f"Written to clipboard ({len(content)} chars)."
        except asyncio.TimeoutError:
            return "Clipboard write timed out."
        except Exception as e:
            return f"Clipboard write error: {type(e).__name__}: {e}"

    return f"Unknown clipboard action: {action}"


TOOL_HANDLERS = {
    "screenshot": _screenshot,
    "clipboard": _clipboard,
}
