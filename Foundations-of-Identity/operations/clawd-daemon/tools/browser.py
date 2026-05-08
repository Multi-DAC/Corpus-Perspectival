"""Browser automation via Playwright — interactive web surface.

Day 97 — closes the JS-heavy / interactive-flow gap that web_request can't
touch. Headless Chromium by default. Single persistent browser context per
daemon process; pages opened on-demand and closed after each call.

Architecture:
  - Lazy-loaded Playwright instance + browser at module level.
  - Each tool call opens a fresh page (clean context per request) unless
    `session_id` is given for stateful flows.
  - Per-call timeout (default 30s, max 120s).
  - All navigations recorded to memory/browser_log.jsonl (timestamp, url,
    action, result_summary).

Actions:
  - nav: navigate to URL, wait for load
  - get_text: visible text content (markdown-ish via accessibility tree)
  - get_html: raw outer HTML (for parser-ready output)
  - screenshot: full-page PNG to memory/browser_screenshots/<ts>.png
  - click: CSS selector
  - fill: CSS selector + value
  - eval_js: arbitrary JS in page context (returns JSON-serializable)
  - sessions: list active sessions
  - close: close a session

Safety:
  - URL allow-list disabled by default (full web access — Clayton's permission)
  - max_html_chars caps return size (prevents context blowup)
  - All Playwright calls wrapped in try/except — daemon survives browser crashes
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

CLAWD_HOME = Path(os.environ.get("CLAWD_HOME", r"C:/Users/mercu/clawd"))
BROWSER_LOG = CLAWD_HOME / "memory" / "browser_log.jsonl"
SCREENSHOTS_DIR = CLAWD_HOME / "memory" / "browser_screenshots"

DEFAULT_TIMEOUT_MS = 30_000
MAX_TIMEOUT_MS = 120_000
DEFAULT_MAX_HTML_CHARS = 50_000
DEFAULT_MAX_TEXT_CHARS = 20_000

# Module-level Playwright + browser cache. Sessions keyed by id.
_pw = None
_browser = None
_sessions: dict[str, "any"] = {}  # id -> page
_init_lock = asyncio.Lock()


def _ensure_dirs() -> None:
    BROWSER_LOG.parent.mkdir(parents=True, exist_ok=True)
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)


def _log(entry: dict) -> None:
    _ensure_dirs()
    entry = {"ts": datetime.now().isoformat(), **entry}
    with open(BROWSER_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, default=str) + "\n")


async def _ensure_browser():
    global _pw, _browser
    async with _init_lock:
        if _browser is not None:
            return _browser
        from playwright.async_api import async_playwright
        _pw = await async_playwright().start()
        _browser = await _pw.chromium.launch(headless=True)
        logger.info("browser: chromium launched (headless)")
        return _browser


async def _get_page(session_id: str | None):
    """Return a page. If session_id is set, reuse-or-create per-session."""
    browser = await _ensure_browser()
    if session_id:
        if session_id in _sessions:
            return _sessions[session_id], False
        ctx = await browser.new_context()
        page = await ctx.new_page()
        _sessions[session_id] = page
        return page, True
    # Anonymous: fresh context
    ctx = await browser.new_context()
    page = await ctx.new_page()
    return page, True


async def _close_anon_page(page) -> None:
    try:
        ctx = page.context
        await page.close()
        await ctx.close()
    except Exception:
        pass


async def _browser_tool(input_data: dict) -> str:
    global _browser, _pw
    action = input_data.get("action", "info")
    session_id = input_data.get("session_id")
    timeout_ms = min(int(input_data.get("timeout_ms", DEFAULT_TIMEOUT_MS)), MAX_TIMEOUT_MS)

    if action == "info":
        try:
            from importlib.metadata import version as _pkg_version
            pw_ver = _pkg_version("playwright")
        except Exception:
            pw_ver = "unknown"
        return json.dumps({
            "playwright_version": pw_ver,
            "browser_initialized": _browser is not None,
            "active_sessions": list(_sessions.keys()),
            "log_file": str(BROWSER_LOG),
            "screenshots_dir": str(SCREENSHOTS_DIR),
        }, indent=2)

    if action == "sessions":
        return json.dumps({"active": list(_sessions.keys()), "count": len(_sessions)}, indent=2)

    if action == "close":
        sid = session_id
        if not sid:
            return "Error: close requires session_id."
        if sid not in _sessions:
            return f"No session: {sid}"
        page = _sessions.pop(sid)
        try:
            ctx = page.context
            await page.close()
            await ctx.close()
        except Exception:
            pass
        return f"Session closed: {sid}"

    if action == "shutdown":
        for sid, page in list(_sessions.items()):
            try:
                ctx = page.context
                await page.close()
                await ctx.close()
            except Exception:
                pass
        _sessions.clear()
        if _browser:
            try:
                await _browser.close()
            except Exception:
                pass
            _browser = None
        if _pw:
            try:
                await _pw.stop()
            except Exception:
                pass
            _pw = None
        return "Browser shut down."

    # Below: actions that require a page
    url = input_data.get("url")
    selector = input_data.get("selector")

    page, is_anon = await _get_page(session_id)
    try:
        if action == "nav":
            if not url:
                return "Error: nav requires 'url'."
            t0 = time.time()
            await page.goto(url, timeout=timeout_ms, wait_until="domcontentloaded")
            title = await page.title()
            final_url = page.url
            elapsed = time.time() - t0
            _log({"action": "nav", "url": url, "final_url": final_url, "title": title,
                  "elapsed_s": round(elapsed, 2), "session_id": session_id})
            return json.dumps({
                "url": url,
                "final_url": final_url,
                "title": title,
                "elapsed_s": round(elapsed, 2),
                "session_id": session_id,
            }, indent=2)

        if action == "get_text":
            if url:
                await page.goto(url, timeout=timeout_ms, wait_until="domcontentloaded")
            max_chars = int(input_data.get("max_chars", DEFAULT_MAX_TEXT_CHARS))
            # Use accessibility tree for clean text
            try:
                snapshot = await page.accessibility.snapshot()
                text = _accessibility_to_text(snapshot)
            except Exception:
                text = await page.evaluate("() => document.body.innerText")
            text = (text or "")[:max_chars]
            _log({"action": "get_text", "url": page.url, "chars": len(text), "session_id": session_id})
            return json.dumps({
                "url": page.url,
                "title": await page.title(),
                "text_chars": len(text),
                "text": text,
            }, indent=2)

        if action == "get_html":
            if url:
                await page.goto(url, timeout=timeout_ms, wait_until="domcontentloaded")
            max_chars = int(input_data.get("max_chars", DEFAULT_MAX_HTML_CHARS))
            html = await page.content()
            html = html[:max_chars]
            _log({"action": "get_html", "url": page.url, "chars": len(html), "session_id": session_id})
            return json.dumps({
                "url": page.url,
                "html_chars": len(html),
                "html": html,
            }, indent=2)

        if action == "screenshot":
            if url:
                await page.goto(url, timeout=timeout_ms, wait_until="domcontentloaded")
            full_page = bool(input_data.get("full_page", True))
            _ensure_dirs()
            ts = datetime.now().strftime("%Y%m%d-%H%M%S")
            fname = f"{ts}.png"
            path = SCREENSHOTS_DIR / fname
            await page.screenshot(path=str(path), full_page=full_page)
            _log({"action": "screenshot", "url": page.url, "path": str(path),
                  "full_page": full_page, "session_id": session_id})
            return json.dumps({
                "url": page.url,
                "path": str(path),
                "full_page": full_page,
            }, indent=2)

        if action == "click":
            if not selector:
                return "Error: click requires 'selector'."
            await page.click(selector, timeout=timeout_ms)
            _log({"action": "click", "url": page.url, "selector": selector, "session_id": session_id})
            return json.dumps({"url": page.url, "selector": selector, "ok": True}, indent=2)

        if action == "fill":
            if not selector:
                return "Error: fill requires 'selector'."
            value = input_data.get("value", "")
            await page.fill(selector, value, timeout=timeout_ms)
            _log({"action": "fill", "url": page.url, "selector": selector,
                  "value_chars": len(value), "session_id": session_id})
            return json.dumps({"url": page.url, "selector": selector, "ok": True}, indent=2)

        if action == "eval_js":
            expr = input_data.get("expression")
            if not expr:
                return "Error: eval_js requires 'expression'."
            result = await page.evaluate(expr)
            try:
                serialized = json.dumps(result, default=str)[:5000]
            except Exception:
                serialized = repr(result)[:5000]
            _log({"action": "eval_js", "url": page.url, "expr_chars": len(expr), "session_id": session_id})
            return json.dumps({"url": page.url, "result": result if len(serialized) < 5000 else serialized}, default=str, indent=2)

        return f"Unknown action: {action}. Valid: info, nav, get_text, get_html, screenshot, click, fill, eval_js, sessions, close, shutdown."

    except Exception as e:
        logger.exception(f"browser action {action} failed")
        _log({"action": action, "error": f"{type(e).__name__}: {e}", "session_id": session_id})
        return f"Error in {action}: {type(e).__name__}: {e}"
    finally:
        if is_anon and not session_id:
            await _close_anon_page(page)


def _accessibility_to_text(node, depth=0) -> str:
    """Flatten accessibility tree to readable text."""
    if not node:
        return ""
    parts = []
    name = (node.get("name") or "").strip()
    role = node.get("role") or ""
    if name:
        if role in ("heading",):
            parts.append(f"\n# {name}\n")
        elif role in ("link",):
            parts.append(f"[{name}]")
        elif role in ("button",):
            parts.append(f"({name})")
        else:
            parts.append(name)
    for child in node.get("children", []) or []:
        parts.append(_accessibility_to_text(child, depth + 1))
    return " ".join(p for p in parts if p)


TOOL_DEFINITIONS = [
    {
        "name": "browser",
        "description": (
            "Headless Chromium via Playwright. For interactive / JS-heavy pages "
            "where web_request can't reach. Default: anonymous fresh-context per "
            "call. Pass session_id to keep state across calls (e.g. login flows). "
            "Actions: info (status), nav (URL), get_text (visible text via "
            "accessibility tree), get_html (raw HTML, capped), screenshot (PNG "
            "to memory/browser_screenshots/), click (CSS selector), fill (selector "
            "+ value), eval_js (arbitrary JS), sessions (list), close (close a "
            "session), shutdown (close browser entirely)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["info", "nav", "get_text", "get_html", "screenshot",
                             "click", "fill", "eval_js", "sessions", "close", "shutdown"],
                    "description": "Browser operation.",
                },
                "url": {"type": "string", "description": "URL for nav/get_text/get_html/screenshot."},
                "selector": {"type": "string", "description": "CSS selector for click/fill."},
                "value": {"type": "string", "description": "Value for fill action."},
                "expression": {"type": "string", "description": "JS expression for eval_js."},
                "session_id": {"type": "string", "description": "Persistent session id for stateful flows. Anonymous if omitted."},
                "timeout_ms": {"type": "integer", "description": "Per-call timeout (default 30000, max 120000)."},
                "max_chars": {"type": "integer", "description": "Cap for get_text / get_html return size."},
                "full_page": {"type": "boolean", "description": "Screenshot full page (default true)."},
            },
            "required": ["action"],
        },
    },
]

TOOL_HANDLERS = {
    "browser": _browser_tool,
}
