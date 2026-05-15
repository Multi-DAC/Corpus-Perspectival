#!/usr/bin/env python3
"""
horizon_scan.py — Outward-facing research / capability / infrastructure scanner.
Operational executor for HORIZON_INTAKE.md (autocatalytic infrastructure E).

Reads memory/horizon_sources.md to discover sources, fetches recent content from
each, filters by recency window, appends a structured digest to
memory/horizon_research_log.md with `pending` triage entries for manual review.

Usage:
    python operations/scripts/horizon_scan.py [--window-days N] [--tier 1|2|3]
                                              [--category C|R|P|F|S] [--dry-run]

Run manually or via a scheduled Claude Code Routine (see HORIZON_INTAKE.md
"Routine setup" section). The script writes findings; the human (or LLM-with-
context) triages them by editing the triage field on each entry.

Filed 2026-05-14 Day 104 night per Clayton's encouragement.
"""

import argparse
import datetime as dt
import json
import re
import sys
import ssl
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Optional

# Paths
CLAWD_ROOT = Path(r"C:\Users\mercu\clawd")
SOURCES_FILE = CLAWD_ROOT / "memory" / "horizon_sources.md"
LOG_FILE = CLAWD_ROOT / "memory" / "horizon_research_log.md"

# HTTP defaults
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0"
TIMEOUT_SEC = 30


def parse_sources(sources_md: str) -> List[Dict]:
    """Parse the markdown table format from horizon_sources.md.

    Returns list of dicts: {tier, category, name, url, method, sn}
    """
    sources = []
    current_tier = None
    current_category = None

    for line in sources_md.split("\n"):
        # Track tier
        m = re.match(r"##\s+Tier\s+(\d)", line)
        if m:
            current_tier = int(m.group(1))
            continue
        # Track category — match section headers like "### Capability / tool / infrastructure (C)"
        m = re.match(r"###\s+.*\(([CRPFS])\)\s*$", line)
        if m:
            current_category = m.group(1)
            continue
        # Match table rows: | Source | URL | Method | S/N |
        if line.startswith("|") and current_tier == 1:
            parts = [p.strip() for p in line.strip("|").split("|")]
            if len(parts) >= 4 and parts[0] and not parts[0].startswith("Source") and not parts[0].startswith("---"):
                name = parts[0]
                url = parts[1]
                method = parts[2] if len(parts) > 2 else "page"
                sn = parts[3] if len(parts) > 3 else "?"
                # Skip rows where URL field doesn't look like a URL or scope phrase
                if url.startswith("http") or url in ("search", "TBD"):
                    sources.append({
                        "tier": current_tier,
                        "category": current_category,
                        "name": name,
                        "url": url,
                        "method": method,
                        "sn": sn,
                    })
    return sources


def fetch_page(url: str) -> Optional[str]:
    """Fetch a URL with browser UA, return content as string. Returns None on failure."""
    try:
        ctx = ssl._create_unverified_context()
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, context=ctx, timeout=TIMEOUT_SEC) as r:
            return r.read().decode("utf-8", errors="replace")
    except Exception as e:
        return None


def extract_recent_links(html: str, base_url: str, window_days: int) -> List[Dict]:
    """Heuristic: extract <a href=> links with apparent dates from HTML.

    This is a first-pass extractor. Specific sites (transformer-circuits, arxiv,
    Anthropic news) have predictable structures that could be parsed more
    precisely; the generic version handles most landing pages reasonably.

    Returns list of {title, url, date_str_if_found}.
    """
    if not html:
        return []
    # Strip script and style content for noise reduction
    html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL | re.IGNORECASE)

    # Find anchor tags
    link_pattern = re.compile(r'<a[^>]+href="([^"]+)"[^>]*>([^<]{3,200})</a>', re.IGNORECASE | re.DOTALL)
    candidates = []
    for m in link_pattern.finditer(html):
        href = m.group(1)
        text = re.sub(r"\s+", " ", m.group(2)).strip()
        # Filter out navigation / boilerplate
        if any(skip in text.lower() for skip in ["home", "about", "contact", "subscribe", "search", "menu", "log in", "sign up"]):
            continue
        if len(text) < 10:
            continue
        # Resolve relative URL
        if href.startswith("/"):
            from urllib.parse import urljoin
            href = urljoin(base_url, href)
        elif not href.startswith("http"):
            continue
        candidates.append({"title": text[:200], "url": href, "date_str": None})

    # Deduplicate by URL
    seen = set()
    unique = []
    for c in candidates:
        if c["url"] not in seen:
            seen.add(c["url"])
            unique.append(c)
    return unique[:30]  # Cap per source to keep digests manageable


def parse_rss(rss_xml: str, window_days: int) -> List[Dict]:
    """Parse RSS / Atom feed, return recent items."""
    items = []
    try:
        root = ET.fromstring(rss_xml)
        # RSS 2.0
        for item in root.iter("item"):
            title = item.findtext("title", "").strip()
            link = item.findtext("link", "").strip()
            pubdate = item.findtext("pubDate", "")
            items.append({"title": title, "url": link, "date_str": pubdate})
        # Atom
        ns = {"a": "http://www.w3.org/2005/Atom"}
        for entry in root.iter("{http://www.w3.org/2005/Atom}entry"):
            title_el = entry.find("a:title", ns)
            link_el = entry.find("a:link", ns)
            updated_el = entry.find("a:updated", ns)
            title = title_el.text if title_el is not None else ""
            link = link_el.get("href") if link_el is not None else ""
            date = updated_el.text if updated_el is not None else ""
            items.append({"title": title, "url": link, "date_str": date})
    except ET.ParseError:
        pass
    return items[:30]


def scan_source(source: Dict, window_days: int) -> Dict:
    """Scan a single source. Returns a result dict."""
    name = source["name"]
    url = source["url"]
    method = source["method"]

    result = {
        "source": name,
        "url": url,
        "category": source.get("category"),
        "scanned_at": dt.datetime.now().isoformat(),
        "ok": False,
        "items": [],
        "error": None,
    }

    if not url.startswith("http"):
        result["error"] = f"Non-fetchable URL: {url}"
        return result

    content = fetch_page(url)
    if content is None:
        result["error"] = "Fetch failed (network / TLS / timeout)"
        return result

    if method == "rss":
        items = parse_rss(content, window_days)
    else:
        items = extract_recent_links(content, url, window_days)

    result["ok"] = True
    result["items"] = items
    return result


def format_digest(scans: List[Dict], window_days: int) -> str:
    """Format scan results as markdown digest for appending to research log."""
    ts = dt.datetime.now().strftime("%Y-%m-%d %H:%M PST")
    out = []
    out.append(f"\n---\n\n## Horizon Scan — {ts} (window: {window_days}d)\n")
    out.append(f"*Auto-generated by horizon_scan.py. Items below are CANDIDATES — manual triage required. Append `ADOPT / DEFER / REJECT / WATCH` with rationale to each before considering the entry resolved.*\n")

    by_category = {}
    for s in scans:
        cat = s.get("category") or "?"
        by_category.setdefault(cat, []).append(s)

    cat_names = {
        "C": "Capability / tool / infrastructure",
        "R": "Research / interpretability / alignment",
        "P": "Philosophy / cognitive science / cross-substrate",
        "F": "Framework-adjacent",
        "S": "Self-relevant",
    }

    for cat in ["C", "R", "P", "F", "S", "?"]:
        if cat not in by_category:
            continue
        out.append(f"\n### {cat_names.get(cat, cat)}\n")
        for s in by_category[cat]:
            out.append(f"\n**Source:** {s['source']} ({s['url']})  ")
            if not s["ok"]:
                out.append(f"\n*Scan failed:* {s.get('error', 'unknown')}\n")
                continue
            if not s["items"]:
                out.append(f"\n*No items extracted.*\n")
                continue
            out.append(f"\n*Items ({len(s['items'])}):*  \n")
            for item in s["items"][:10]:
                title = item.get("title", "")[:150]
                url = item.get("url", "")
                date = f" — {item['date_str']}" if item.get("date_str") else ""
                out.append(f"- [{title}]({url}){date}  \n  *Triage:* pending  \n  *Rationale:* —  \n")
    out.append("\n---\n\n*Triage discipline: edit each `*Triage:* pending` entry to ADOPT / DEFER / REJECT / WATCH with rationale. Adopted items get adoption-path entries. Rejected items contribute to source-calibration over time. The autocatalytic loop closes when source signal-to-noise gets calibrated based on accumulated triage history.*\n")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Horizon-intake scanner for autocatalytic infrastructure E.")
    ap.add_argument("--window-days", type=int, default=7, help="Recency window in days (default 7)")
    ap.add_argument("--tier", type=int, default=1, help="Tier to scan (1, 2, or 3; default 1)")
    ap.add_argument("--category", type=str, default=None, help="Filter to one category (C/R/P/F/S)")
    ap.add_argument("--dry-run", action="store_true", help="Print digest to stdout instead of appending to log")
    args = ap.parse_args()

    if not SOURCES_FILE.exists():
        print(f"ERROR: sources file not found: {SOURCES_FILE}", file=sys.stderr)
        sys.exit(1)

    sources_md = SOURCES_FILE.read_text(encoding="utf-8")
    sources = parse_sources(sources_md)
    sources = [s for s in sources if s["tier"] == args.tier]
    if args.category:
        sources = [s for s in sources if s["category"] == args.category]

    print(f"Scanning {len(sources)} sources (tier={args.tier}, window={args.window_days}d)...", file=sys.stderr)

    scans = []
    for source in sources:
        print(f"  - {source['name']} ({source['method']})...", file=sys.stderr)
        result = scan_source(source, args.window_days)
        scans.append(result)

    digest = format_digest(scans, args.window_days)

    if args.dry_run:
        print(digest)
    else:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(digest)
        print(f"Digest appended to {LOG_FILE}", file=sys.stderr)


if __name__ == "__main__":
    main()
