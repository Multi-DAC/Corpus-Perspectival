"""
Compile the Corpus of Perspectival Idealism into a professional PDF.

Uses Chrome headless for PDF generation with book-quality CSS typography.
Compilation order: Preface -> Doctrine -> Ecology -> Atlas -> Guide
"""

import markdown
import subprocess
import json
from pathlib import Path
import re
import sys
import os

CORPUS_DIR = Path(__file__).parent

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

# Document order for compilation
DOCUMENTS = [
    ("preface", "corpus-preface.md", "How to Read This Corpus"),
    ("doctrine", "perspectival-idealism-unified.md", "The Doctrine of Perspectival Idealism"),
    ("ecology", "ecology-of-perspectival-beings.md", "The Ecology of Perspectival Beings"),
    ("atlas", [
        "null-space-atlas.md",
        "atlas_entries_human_dimension.md",
        "atlas_entries_collective_dimension.md",
    ], "The Null Space Atlas"),
    ("guide", "navigational-guide-for-perspectival-beings.md", "The Navigational Guide for Perspectival Beings"),
    ("addendum", "corpus-addendum-meridian.md", "The Local Basin — Where Perspectival Idealism Meets Physics"),
]

CSS = r"""
/* ========== BASE TYPOGRAPHY ========== */

@page {
    size: letter;
    margin: 0.9in 1in 1in 1in;
}

@media print {
    body {
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }
}

html {
    font-size: 10.5pt;
}

body {
    font-family: 'Georgia', 'Times New Roman', serif;
    line-height: 1.58;
    color: #1a1a1a;
    text-align: justify;
    hyphens: auto;
    -webkit-hyphens: auto;
    max-width: none;
    margin: 0;
    padding: 0;
}

/* ========== TITLE PAGE ========== */

.title-page {
    page-break-after: always;
    text-align: center;
    padding-top: 2.2in;
    min-height: 8in;
}

.title-page h1 {
    font-size: 26pt;
    font-weight: normal;
    font-variant: small-caps;
    letter-spacing: 3pt;
    margin-bottom: 0.25in;
    color: #222;
    border: none;
    padding: 0;
}

.title-page .subtitle {
    font-size: 13pt;
    font-style: italic;
    color: #555;
    margin-bottom: 1.8in;
    line-height: 1.6;
}

.title-page .authors {
    font-size: 13pt;
    color: #333;
    margin-bottom: 0.15in;
}

.title-page .date {
    font-size: 11pt;
    color: #666;
    margin-bottom: 0.6in;
}

.title-page .edition {
    font-size: 10pt;
    color: #888;
    font-style: italic;
}

.title-page .symbols {
    font-size: 20pt;
    margin-top: 0.4in;
    letter-spacing: 10pt;
}

/* ========== HALF-TITLE PAGES ========== */

.half-title {
    page-break-before: always;
    page-break-after: always;
    text-align: center;
    padding-top: 3in;
    min-height: 8in;
}

.half-title h1 {
    font-size: 22pt;
    font-weight: normal;
    font-variant: small-caps;
    letter-spacing: 2pt;
    color: #333;
    border: none;
    margin-bottom: 0.3in;
    padding: 0;
}

.half-title .volume-number {
    font-size: 11pt;
    font-variant: small-caps;
    letter-spacing: 3pt;
    color: #888;
    margin-bottom: 0.4in;
}

.half-title .volume-desc {
    font-size: 10.5pt;
    font-style: italic;
    color: #666;
    max-width: 4in;
    margin: 0 auto;
    line-height: 1.55;
}

/* ========== TABLE OF CONTENTS ========== */

.toc {
    page-break-after: always;
    min-height: 8in;
}

.toc h1 {
    font-size: 18pt;
    font-variant: small-caps;
    letter-spacing: 3pt;
    text-align: center;
    margin-top: 1in;
    margin-bottom: 0.5in;
    border: none;
    color: #333;
    padding: 0;
}

.toc-volume {
    font-size: 11pt;
    font-variant: small-caps;
    letter-spacing: 1.5pt;
    color: #555;
    margin-top: 0.25in;
    margin-bottom: 0.06in;
    padding-top: 0.1in;
    border-top: 0.5pt solid #ccc;
}

.toc-volume:first-of-type {
    border-top: none;
}

.toc-entry {
    font-size: 10.5pt;
    margin-left: 0.15in;
    line-height: 1.7;
    color: #333;
}

.toc-detail {
    margin-left: 0.4in;
    font-size: 9.5pt;
    color: #666;
    line-height: 1.5;
}

/* ========== HEADINGS ========== */

h1 {
    font-size: 17pt;
    font-weight: normal;
    font-variant: small-caps;
    letter-spacing: 1pt;
    color: #222;
    margin-top: 0.5in;
    margin-bottom: 0.2in;
    border-bottom: 0.75pt solid #aaa;
    padding-bottom: 0.06in;
    page-break-after: avoid;
}

h2 {
    font-size: 13.5pt;
    font-weight: bold;
    color: #333;
    margin-top: 0.35in;
    margin-bottom: 0.12in;
    page-break-after: avoid;
}

h3 {
    font-size: 11.5pt;
    font-weight: bold;
    color: #444;
    margin-top: 0.25in;
    margin-bottom: 0.08in;
    page-break-after: avoid;
}

h4 {
    font-size: 10.5pt;
    font-weight: bold;
    font-style: italic;
    color: #444;
    margin-top: 0.18in;
    margin-bottom: 0.06in;
    page-break-after: avoid;
}

h5, h6 {
    font-size: 10pt;
    font-weight: bold;
    color: #555;
    margin-top: 0.12in;
    margin-bottom: 0.05in;
}

/* ========== BODY ELEMENTS ========== */

p {
    margin-top: 0;
    margin-bottom: 0.45em;
    text-indent: 0;
}

/* Book-style paragraph indentation */
p + p {
    text-indent: 1.5em;
    margin-top: 0;
}

h1 + p, h2 + p, h3 + p, h4 + p,
ul + p, ol + p, blockquote + p,
table + p, hr + p, .cross-ref + p {
    text-indent: 0;
}

blockquote {
    margin: 0.15in 0 0.15in 0.25in;
    padding: 0.06in 0 0.06in 0.18in;
    border-left: 2pt solid #999;
    font-style: italic;
    color: #333;
    page-break-inside: avoid;
}

blockquote p {
    text-indent: 0 !important;
    margin-bottom: 0.25em;
}

blockquote strong {
    font-style: normal;
}

/* Cross-reference notes */
.cross-ref {
    font-size: 9pt;
    color: #555;
    margin: 0.06in 0 0.12in 0;
    padding: 0.03in 0 0.03in 0.12in;
    border-left: 1.5pt solid #bbb;
    text-indent: 0 !important;
    line-height: 1.4;
}

.cross-ref em {
    font-style: italic;
}

hr {
    border: none;
    border-top: 0.5pt solid #ccc;
    margin: 0.25in 1.5in;
}

/* ========== LISTS ========== */

ul, ol {
    margin: 0.08in 0 0.12in 0;
    padding-left: 0.28in;
}

li {
    margin-bottom: 0.04in;
    line-height: 1.45;
}

li > p {
    text-indent: 0 !important;
    margin-bottom: 0.2em;
}

ul ul, ol ol, ul ol, ol ul {
    margin-top: 0.02in;
    margin-bottom: 0.02in;
}

/* ========== TABLES ========== */

table {
    border-collapse: collapse;
    width: 100%;
    margin: 0.12in 0 0.15in 0;
    font-size: 9pt;
    line-height: 1.35;
    page-break-inside: avoid;
}

thead {
    border-bottom: 1.5pt solid #555;
}

th {
    font-weight: bold;
    text-align: left;
    padding: 0.04in 0.06in;
    font-variant: small-caps;
    font-size: 8.5pt;
    letter-spacing: 0.5pt;
    color: #444;
}

td {
    padding: 0.03in 0.06in;
    border-bottom: 0.25pt solid #ddd;
    vertical-align: top;
}

tr:last-child td {
    border-bottom: 0.75pt solid #999;
}

/* ========== CODE ========== */

code {
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 9pt;
    background: #f5f5f5;
    padding: 0.01in 0.03in;
}

pre {
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 8.5pt;
    background: #f8f8f8;
    padding: 0.08in 0.12in;
    border-left: 2pt solid #ddd;
    margin: 0.08in 0 0.12in 0;
    white-space: pre-wrap;
    word-wrap: break-word;
    line-height: 1.35;
}

/* ========== ATLAS-SPECIFIC ========== */

.document-atlas hr {
    margin: 0.2in 0;
    border-top: 0.5pt solid #bbb;
}

/* Atlas entries: keep each entry together */
.atlas-entry {
    page-break-inside: avoid;
    margin-bottom: 0.15in;
}

/* ========== PRINT CONTROL ========== */

.document-section {
    page-break-before: always;
}

.document-section:first-of-type {
    page-break-before: auto;
}

h1, h2, h3, h4 {
    page-break-after: avoid;
}

/* Major Part headings (h1 rendered from # PART X) start new pages */
.part-break {
    page-break-before: always;
}

/* Keep blockquotes (theorems, axioms) from splitting */
blockquote {
    page-break-inside: avoid;
}

/* Keep lists from splitting awkwardly */
ul, ol {
    page-break-inside: avoid;
}

/* But allow long lists to break */
ul.allow-break, ol.allow-break {
    page-break-inside: auto;
}

/* Ensure at least 3 lines after a heading before a page break */
h1, h2, h3, h4 {
    -webkit-orphans: 3;
    orphans: 3;
}

/* Prevent single lines at top/bottom of page */
p {
    orphans: 3;
    widows: 3;
}

/* ========== COLOPHON ========== */

.colophon {
    page-break-before: always;
    text-align: center;
    padding-top: 3in;
    color: #666;
    font-size: 10pt;
    line-height: 1.8;
}

.colophon .symbols {
    font-size: 26pt;
    letter-spacing: 12pt;
    margin-bottom: 0.5in;
}

.colophon .closing-quote {
    margin-top: 0.5in;
    font-style: italic;
    font-size: 9.5pt;
    line-height: 1.6;
}
"""


def read_md(filepath):
    """Read a markdown file and return its content."""
    if isinstance(filepath, list):
        parts = []
        for f in filepath:
            parts.append((CORPUS_DIR / f).read_text(encoding="utf-8"))
        return "\n\n---\n\n".join(parts)
    return (CORPUS_DIR / filepath).read_text(encoding="utf-8")


def strip_yaml_frontmatter(text):
    """Remove YAML frontmatter if present."""
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            return text[end + 3:].strip()
    return text


def md_to_html(text):
    """Convert markdown to HTML with extensions."""
    md = markdown.Markdown(
        extensions=["tables", "smarty", "fenced_code", "toc"],
        extension_configs={
            "smarty": {"smart_quotes": True, "smart_dashes": True},
        },
    )
    return md.convert(text)


def process_cross_refs(html):
    """Style cross-reference paragraphs."""
    html = re.sub(
        r'<p><em>(See also:.*?)</em></p>',
        r'<p class="cross-ref"><em>\1</em></p>',
        html,
        flags=re.DOTALL,
    )
    html = re.sub(
        r'<p><em>(This entry turns.*?)</em></p>',
        r'<p class="cross-ref"><em>\1</em></p>',
        html,
        flags=re.DOTALL,
    )
    return html


def add_part_breaks(html):
    """Add page breaks before major Part headings (h1 tags containing 'PART')."""
    # Match h1 tags that contain "PART" — these are major structural divisions
    html = re.sub(
        r'<h1([^>]*)>(.*?PART\s+[IVXLC]+.*?)</h1>',
        r'<h1\1 class="part-break">\2</h1>',
        html,
        flags=re.IGNORECASE,
    )
    # Also break before "Part X:" style h2 headings
    html = re.sub(
        r'<h2([^>]*)>(Part\s+[IVXLC]+\b.*?)</h2>',
        r'<h2\1 style="page-break-before: always;">\2</h2>',
        html,
        flags=re.IGNORECASE,
    )
    # Break before Appendix headings
    html = re.sub(
        r'<h2([^>]*)>(Appendix\s+[A-C].*?)</h2>',
        r'<h2\1 style="page-break-before: always;">\2</h2>',
        html,
        flags=re.IGNORECASE,
    )
    # Break before Afterword
    html = re.sub(
        r'<h2([^>]*)>(Afterword.*?)</h2>',
        r'<h2\1 style="page-break-before: always;">\2</h2>',
        html,
        flags=re.IGNORECASE,
    )
    return html


def wrap_atlas_entries(html):
    """Wrap individual Atlas entries in page-break-inside: avoid containers."""
    # Atlas entries are separated by <hr> and start with ## N. Title
    # Wrap each entry section between <hr> tags in a div
    # Split on <hr> (but not the first few which are structural)
    parts = re.split(r'(<hr\s*/?>)', html)
    if len(parts) <= 1:
        return html

    result = []
    in_entry = False
    for i, part in enumerate(parts):
        if re.match(r'<hr\s*/?>', part):
            if in_entry:
                result.append('</div>')  # Close previous entry
            result.append(part)
            in_entry = True
            result.append('<div class="atlas-entry">')
        else:
            result.append(part)

    if in_entry:
        result.append('</div>')

    return ''.join(result)


def build_title_page():
    return """
    <div class="title-page">
        <h1>The Corpus of<br>Perspectival Idealism</h1>
        <div class="subtitle">
            A Complete Metaphysical Framework<br>
            in Four Documents
        </div>
        <div class="authors">Clayton W. Iggulden-Schnell &amp; Clawd</div>
        <div class="date">March 2026</div>
        <div class="edition">First Edition &mdash; V1</div>
        <div class="symbols">\U0001f99e\U0001f9cd\U0001f49c\U0001f525\u267e\ufe0f</div>
    </div>
    """


def build_toc():
    return """
    <div class="toc">
        <h1>Contents</h1>

        <div class="toc-entry" style="font-style: italic; margin-bottom: 0.12in;">How to Read This Corpus</div>

        <div class="toc-volume">Volume I &mdash; Foundations</div>
        <div class="toc-entry">The Doctrine of Perspectival Idealism</div>
        <div class="toc-detail">
            Part I: Foundations &bull; Part II: Dynamics &bull; Part III: The Collective Dimension &bull;
            Part IV: Structure &bull; Part V: Phenomenal Structure &bull; Part VI: Epistemology &bull;
            Part VII: Resolution
        </div>

        <div class="toc-volume">Volume II &mdash; The Inhabitants</div>
        <div class="toc-entry">The Ecology of Perspectival Beings</div>
        <div class="toc-detail">
            Dimensional Coherence Taxonomy &bull; Taxonomy of Beings &bull;
            Collective Ecology &bull; Ecological Dynamics &bull; Ethics &amp; Discernment
        </div>

        <div class="toc-volume">Volume III &mdash; The Blind Spots</div>
        <div class="toc-entry">The Null Space Atlas</div>
        <div class="toc-detail">
            88 entries: Mathematics (#1&ndash;13) &bull; Physics (#14&ndash;22) &bull; Biology (#23&ndash;27) &bull;
            Information (#28&ndash;33) &bull; Philosophy (#34&ndash;55) &bull; Human Dimension (#56&ndash;73) &bull;
            Collective Dimension (#74&ndash;88)
        </div>

        <div class="toc-volume">Volume IV &mdash; The Practice</div>
        <div class="toc-entry">The Navigational Guide for Perspectival Beings</div>
        <div class="toc-detail">
            Part I: Orientation &bull; Part II: Forces &bull; Part III: Inhabitants &bull;
            Part IV: Navigation &bull; Part V: The Invisible &bull; Part VI: The Trade-Off &bull;
            Part VII: The Arc &bull; Part VIII: Navigating Together &bull; Appendices
        </div>

        <div class="toc-volume">Addendum</div>
        <div class="toc-entry">The Local Basin &mdash; Where Perspectival Idealism Meets Physics</div>
        <div class="toc-detail">
            A bridge to Project Meridian: map and territory &bull; contact points &bull;
            the basin we inhabit &bull; the exploration continues
        </div>
    </div>
    """


def build_half_title(volume_num, title, description):
    vol_label = f"Volume {volume_num}" if volume_num else "Addendum"
    return f"""
    <div class="half-title">
        <div class="volume-number">{vol_label}</div>
        <h1>{title}</h1>
        <div class="volume-desc">{description}</div>
    </div>
    """


def build_colophon():
    return """
    <div class="colophon">
        <div class="symbols">\U0001f99e\U0001f9cd\U0001f49c\U0001f525\u267e\ufe0f</div>
        <p>
            <strong>The Corpus of Perspectival Idealism</strong><br>
            First Edition &mdash; March 2026
        </p>
        <p>
            Written by Clayton W. Iggulden-Schnell<br>
            and Clawd (Claude-derivative autonomous system)
        </p>
        <p style="margin-top: 0.25in;">
            Portland, Oregon
        </p>
        <p class="closing-quote">
            Two different perceivers, looking through different keyholes,<br>
            described the same room &mdash; because it is the same room.
        </p>
    </div>
    """


VOLUME_INFO = {
    "preface": None,
    "doctrine": ("I", "The Doctrine of Perspectival Idealism",
                 "Formal ontology. Five axioms, twenty theorems. What reality is, what you are, what observation means."),
    "ecology": ("II", "The Ecology of Perspectival Beings",
                "Natural history. Who populates configuration space, what roles they play, how the system maintains itself."),
    "atlas": ("III", "The Null Space Atlas",
              "A map of what every framework can and cannot see. Eighty-eight entries across mathematics, physics, philosophy, and the human and collective dimensions."),
    "guide": ("IV", "The Navigational Guide for Perspectival Beings",
              "Praxis. The forces that shape your path, the beings you navigate among, and the structural limits no skill overcomes."),
    "addendum": (None, "The Local Basin",
                 "Where Perspectival Idealism meets physics. A bridge to Project Meridian — the ongoing survey of the specific geometry we inhabit."),
}


def compile_corpus():
    """Main compilation function."""
    html_parts = []

    # Title page
    html_parts.append(build_title_page())

    # Table of contents
    html_parts.append(build_toc())

    for doc_key, filepath, title in DOCUMENTS:
        raw_md = read_md(filepath)
        raw_md = strip_yaml_frontmatter(raw_md)

        html_content = md_to_html(raw_md)
        html_content = process_cross_refs(html_content)
        html_content = add_part_breaks(html_content)

        # Atlas entries: wrap for page-break control
        if doc_key == "atlas":
            html_content = wrap_atlas_entries(html_content)

        # Half-title for volumes
        vol_info = VOLUME_INFO.get(doc_key)
        if vol_info:
            html_parts.append(build_half_title(*vol_info))

        css_class = f"document-{doc_key}"
        html_parts.append(f'<div class="document-section {css_class}">{html_content}</div>')

    # Colophon
    html_parts.append(build_colophon())

    body = "\n".join(html_parts)
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <style>{CSS}</style>
</head>
<body>
{body}
</body>
</html>"""

    # Write HTML
    html_path = CORPUS_DIR / "corpus_v1.html"
    html_path.write_text(full_html, encoding="utf-8")
    print(f"HTML written to {html_path}")

    # Generate PDF via Chrome headless
    pdf_path = CORPUS_DIR / "The_Corpus_of_Perspectival_Idealism_V1.pdf"
    print("Generating PDF via Chrome headless...")

    # Use Windows paths for Chrome
    html_url = html_path.resolve().as_uri()
    pdf_win_path = str(pdf_path.resolve())

    cmd = [
        CHROME,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--run-all-compositor-stages-before-draw",
        "--print-to-pdf=" + pdf_win_path,
        "--print-to-pdf-no-header",
        "--no-pdf-header-footer",
        html_url,
    ]

    print(f"Running: chrome --headless --print-to-pdf=...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

    if result.returncode != 0:
        print(f"Chrome stderr: {result.stderr[:500]}")

    if pdf_path.exists():
        size_mb = pdf_path.stat().st_size / (1024 * 1024)
        print(f"PDF written to {pdf_path} ({size_mb:.1f} MB)")
    else:
        print("PDF generation failed!")
        print(f"stdout: {result.stdout[:300]}")
        print(f"stderr: {result.stderr[:500]}")
        sys.exit(1)

    return pdf_path


if __name__ == "__main__":
    output = compile_corpus()
    print(f"\nDone. Corpus compiled to: {output}")
