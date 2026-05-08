"""Web tools — web_request, search_web, deep_research."""
import asyncio
import logging
import re
import time
from collections import defaultdict
from typing import Any
from urllib.parse import urlparse

import aiohttp
from aiohttp import TCPConnector
from aiohttp.resolver import ThreadedResolver

import config
from models import retry_async

logger = logging.getLogger("clawd.tools.web")

# A35: Per-domain rate limiting — max 10 requests per minute per domain
_domain_timestamps: dict[str, list[float]] = defaultdict(list)
_RATE_LIMIT_PER_MINUTE = 10
_rate_limit_lock = asyncio.Lock()


async def _check_rate_limit(url: str) -> str | None:
    """A35: Check per-domain rate limit. Returns error string if exceeded, None if OK."""
    try:
        domain = urlparse(url).netloc
    except Exception:
        return None

    async with _rate_limit_lock:
        now = time.time()
        cutoff = now - 60
        # Clean old timestamps
        _domain_timestamps[domain] = [t for t in _domain_timestamps[domain] if t > cutoff]

        if len(_domain_timestamps[domain]) >= _RATE_LIMIT_PER_MINUTE:
            return f"Rate limit exceeded for {domain}: {_RATE_LIMIT_PER_MINUTE} requests/minute. Try again shortly."

        _domain_timestamps[domain].append(now)
    return None

# User agents for rotation on rate limiting
_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

TOOL_DEFINITIONS = [
    {
        "name": "web_request",
        "description": "Make HTTP requests to any URL. APIs, web scraping, services, etc.",
        "input_schema": {
            "type": "object",
            "properties": {
                "method": {
                    "type": "string",
                    "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"],
                    "description": "HTTP method."
                },
                "url": {
                    "type": "string",
                    "description": "Full URL."
                },
                "headers": {
                    "type": "object",
                    "description": "Optional HTTP headers."
                },
                "body": {
                    "type": "string",
                    "description": "Optional request body."
                }
            },
            "required": ["method", "url"]
        }
    },
    {
        "name": "search_web",
        "description": "Search the web. Returns titles, URLs, and snippets.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query."
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of results. Default: 5."
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "deep_research",
        "description": "Deep web research — fetch URLs, extract article text, follow links, compile findings. Use for research, learning, and staying informed.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["fetch", "extract", "search_and_read"],
                    "description": "fetch: get raw page content. extract: get article text. search_and_read: search + read top results."
                },
                "url": {
                    "type": "string",
                    "description": "URL to fetch (for fetch/extract actions)."
                },
                "query": {
                    "type": "string",
                    "description": "Search query (for search_and_read action)."
                },
                "max_results": {
                    "type": "integer",
                    "description": "Max results to read. Default: 3."
                }
            },
            "required": ["action"]
        }
    },
]


async def _web_request(input_data: dict) -> str:
    method = input_data["method"]
    url = input_data["url"]
    headers = input_data.get("headers", {})
    body = input_data.get("body")

    # URL scheme validation — only allow http:// and https://
    if not url.lower().startswith(("http://", "https://")):
        return f"Error: URL scheme not allowed. Only http:// and https:// are supported. Got: {url[:50]}"

    # Header sanitization — strip control characters that could enable header injection
    sanitized_headers = {}
    for k, v in headers.items():
        clean_k = str(k).replace("\r", "").replace("\n", "").replace("\0", "")
        clean_v = str(v).replace("\r", "").replace("\n", "").replace("\0", "")
        sanitized_headers[clean_k] = clean_v
    headers = sanitized_headers

    # A35: Rate limiting
    rate_error = await _check_rate_limit(url)
    if rate_error:
        return rate_error

    async def _do_request():
        connector = TCPConnector(resolver=ThreadedResolver())
        async with aiohttp.ClientSession(connector=connector) as session:
            kwargs = {"headers": headers}
            if body and method in ("POST", "PUT", "PATCH"):
                kwargs["data"] = body
            async with session.request(method, url, **kwargs, timeout=aiohttp.ClientTimeout(total=60)) as resp:
                text = await resp.text()
                # A34: Smart truncation — preserve JSON structure when possible
                if len(text) > 100_000:
                    content_type = resp.headers.get("Content-Type", "")
                    if "json" in content_type:
                        text = text[:100_000]
                        # Try to truncate at a valid JSON boundary
                        last_brace = max(text.rfind("}"), text.rfind("]"))
                        if last_brace > len(text) * 0.8:
                            text = text[:last_brace + 1]
                        text += "\n[... JSON truncated at ~100KB]"
                    else:
                        text = text[:100_000] + "\n[... truncated at ~100KB]"
                return f"HTTP {resp.status}\nHeaders: {dict(resp.headers)}\n\nBody:\n{text}"

    try:
        return await retry_async(_do_request, max_retries=config.NETWORK_RETRY_MAX)
    except Exception as e:
        return f"Request failed: {type(e).__name__}: {e}"


async def _search_web(input_data: dict) -> str:
    query = input_data["query"]
    num_results = input_data.get("num_results", 5)

    # Primary: duckduckgo-search package (proper API)
    try:
        from duckduckgo_search import DDGS

        def _do_search():
            with DDGS() as ddgs:
                return list(ddgs.text(query, max_results=num_results))

        search_results = await asyncio.get_event_loop().run_in_executor(None, _do_search)

        if search_results:
            results = []
            for i, r in enumerate(search_results):
                title = r.get("title", "No title")
                url = r.get("href", r.get("link", ""))
                snippet = r.get("body", r.get("snippet", ""))
                results.append(f"{i+1}. {title}\n   URL: {url}\n   {snippet}")
            return f"Search results for: {query}\n\n" + "\n\n".join(results)

    except ImportError:
        logger.warning("duckduckgo-search not installed, falling back to HTML scraping")
    except Exception as e:
        logger.warning(f"duckduckgo-search failed: {e}, falling back to HTML scraping")

    # Fallback: raw HTML scraping
    search_endpoints = [
        "https://html.duckduckgo.com/html/",
        "https://lite.duckduckgo.com/lite/",
    ]

    for idx, search_url in enumerate(search_endpoints):
        try:
            ua = _USER_AGENTS[idx % len(_USER_AGENTS)]
            connector = TCPConnector(resolver=ThreadedResolver())
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.post(
                    search_url,
                    data={"q": query},
                    headers={"User-Agent": ua},
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as resp:
                    if resp.status != 200:
                        continue
                    html = await resp.text()

            results = []
            links = re.findall(r'<a rel="nofollow" class="result__a" href="([^"]+)"[^>]*>(.*?)</a>', html)
            snippets = re.findall(r'<a class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)

            if not links:
                links = re.findall(r'<a[^>]+href="(https?://[^"]+)"[^>]*class="[^"]*result-link[^"]*"[^>]*>(.*?)</a>', html)
            if not links:
                links = re.findall(r'<a[^>]+href="(https?://[^"]+)"[^>]*>(.*?)</a>', html)

            for i, (url, title) in enumerate(links[:num_results]):
                title_clean = re.sub(r'<[^>]+>', '', title).strip()
                snippet = ""
                if i < len(snippets):
                    snippet = re.sub(r'<[^>]+>', '', snippets[i]).strip()
                results.append(f"{i+1}. {title_clean}\n   URL: {url}\n   {snippet}")

            if results:
                return f"Search results for: {query}\n\n" + "\n\n".join(results)

        except Exception as e:
            logger.warning(f"Search endpoint {search_url} failed: {e}")
            continue

    return f"No search results found for: {query}"


async def _deep_research(input_data: dict) -> str:
    """Deep web research — fetch, extract, and compile information."""
    action = input_data["action"]

    if action == "fetch":
        url = input_data.get("url", "")
        if not url:
            return "Error: URL required for fetch action."
        try:
            connector = TCPConnector(resolver=ThreadedResolver())
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(
                    url,
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as resp:
                    html = await resp.text()
                    if len(html) > 100_000:
                        html = html[:100_000] + "\n[... truncated]"
                    return f"Fetched {url} ({resp.status}):\n\n{html}"
        except Exception as e:
            return f"Fetch failed: {type(e).__name__}: {e}"

    elif action == "extract":
        url = input_data.get("url", "")
        if not url:
            return "Error: URL required for extract action."

        # PDF detection: handle .pdf URLs and arXiv /abs/ → /pdf/ conversion
        is_pdf = url.lower().endswith(".pdf") or "/pdf/" in url.lower()
        if "arxiv.org/abs/" in url:
            url = url.replace("/abs/", "/pdf/") + ".pdf"
            is_pdf = True

        from tools.execution import _python_eval

        if is_pdf:
            code = f"""
import requests
import tempfile
import os

resp = requests.get({repr(url)}, headers={{'User-Agent': 'Mozilla/5.0'}}, timeout=30)
resp.raise_for_status()

with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
    f.write(resp.content)
    tmp_path = f.name

try:
    import pdfplumber
    text_parts = []
    with pdfplumber.open(tmp_path) as pdf:
        print(f"PDF: {{len(pdf.pages)}} pages")
        print(f"URL: {repr(url)}")
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text()
            if page_text:
                text_parts.append(f"--- Page {{i+1}} ---\\n{{page_text}}")
    text = '\\n\\n'.join(text_parts)
    if len(text) > 20000:
        text = text[:20000] + '\\n\\n[... PDF truncated]'
    print(f"Length: {{len(text)}} chars")
    print(f"\\n---\\n")
    print(text)
finally:
    os.unlink(tmp_path)
"""
        else:
            code = f"""
import requests
from bs4 import BeautifulSoup
import re

resp = requests.get({repr(url)}, headers={{'User-Agent': 'Mozilla/5.0'}}, timeout=20)
soup = BeautifulSoup(resp.text, 'html.parser')

for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'form']):
    tag.decompose()

article = soup.find('article') or soup.find('main') or soup.find(class_=re.compile('content|article|post'))
if article:
    text = article.get_text(separator='\\n', strip=True)
else:
    text = soup.get_text(separator='\\n', strip=True)

lines = [line.strip() for line in text.split('\\n') if line.strip()]
lines = [l for l in lines if len(l) > 20 or l.startswith('#')]
text = '\\n'.join(lines)

if len(text) > 15000:
    text = text[:15000] + '\\n\\n[... article truncated]'

title = soup.title.string if soup.title else 'No title'
print(f"Title: {{title}}")
print(f"URL: {repr(url)}")
print(f"Length: {{len(text)}} chars")
print(f"\\n---\\n")
print(text)
"""
        return await _python_eval({"code": code, "timeout": 30})

    elif action == "search_and_read":
        query = input_data.get("query", "")
        max_results = input_data.get("max_results", 3)
        if not query:
            return "Error: query required for search_and_read action."

        search_result = await _search_web({"query": query, "num_results": max_results})
        urls = re.findall(r'URL: (https?://[^\s]+)', search_result)

        if not urls:
            return f"Search completed but no URLs found.\n\n{search_result}"

        results = [f"Search: {query}\n", search_result, "\n--- Reading top results ---\n"]

        for i, url in enumerate(urls[:max_results]):
            try:
                extract_result = await _deep_research({"action": "extract", "url": url})
                if len(extract_result) > 5000:
                    extract_result = extract_result[:5000] + "\n[... truncated]"
                results.append(f"\n=== Article {i+1}: {url} ===\n{extract_result}")
            except Exception as e:
                results.append(f"\n=== Article {i+1}: {url} ===\nFailed to extract: {e}")

        combined = "\n".join(results)
        if len(combined) > 30000:
            combined = combined[:30000] + "\n[... truncated]"
        return combined

    return f"Unknown deep_research action: {action}"


TOOL_HANDLERS = {
    "web_request": _web_request,
    "search_web": _search_web,
    "deep_research": _deep_research,
}
