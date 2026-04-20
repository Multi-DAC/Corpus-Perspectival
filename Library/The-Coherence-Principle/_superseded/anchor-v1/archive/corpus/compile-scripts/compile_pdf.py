#!/usr/bin/env python3
"""Compile the Corpus Perspectival V2 into a single PDF."""

import markdown
import os
import sys
import re

# Ensure proper encoding
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from fpdf import FPDF

CORPUS_DIR = os.path.dirname(os.path.abspath(__file__))

# Document order — the full corpus, comprehensive
DOCUMENTS = [
    # V2 Spine
    ("v2-introduction-f0.md", "V2 Introduction — F₀"),
    ("v2-part-i-f1-the-view.md", "V2 Part I — F₁: The View"),
    ("v2-part-ii-f2-the-mathematics.md", "V2 Part II — F₂: The Mathematics"),
    ("v2-part-iii-f3-five-perspectives.md", "V2 Part III — F₃: Five Perspectives"),
    ("v2-part-iv-f2-the-atlas.md", "V2 Part IV — F₂↑: The Atlas"),
    ("v2-part-v-f1-the-guide.md", "V2 Part V — F₁↑: The Guide"),
    ("v2-part-vi-f0-conclusion.md", "V2 Part VI — F₀↑: Conclusion"),

    # Core documents (full)
    ("perspectival-idealism-unified.md", "The Doctrine of Perspectival Idealism"),
    ("ecology-of-perspectival-beings-merged.md", "The Ecology of Perspectival Beings"),
    ("navigational-guide-for-perspectival-beings.md", "The Navigational Guide"),
    ("null-space-atlas.md", "The Null Space Atlas"),

    # Companion documents
    ("navigation-charts-consciousness-cartography.md", "Navigation Charts"),
    ("bridges-cross-domain-connections.md", "Bridges: Cross-Domain Connections"),
    ("bridge3-mythos-extension.md", "Bridge 3 Extension: The Mythos Data"),
    ("theorem-index.md", "Theorem Index"),
    ("corpus-cross-references.md", "Cross-References"),
]


class CorpusPDF(FPDF):
    """Custom PDF class for Corpus Perspectival."""

    def __init__(self):
        super().__init__(orientation='P', unit='mm', format='letter')
        self.set_auto_page_break(auto=True, margin=25)
        self.set_margins(25, 20, 25)

        # Register Unicode fonts
        font_dir = 'C:/Windows/Fonts/'
        self.add_font('Georgia', '', font_dir + 'georgia.ttf')
        self.add_font('Georgia', 'B', font_dir + 'georgiab.ttf')
        self.add_font('Georgia', 'I', font_dir + 'georgiai.ttf')
        self.add_font('Georgia', 'BI', font_dir + 'georgiaz.ttf')
        self.add_font('Calibri', '', font_dir + 'calibri.ttf')
        self.add_font('Calibri', 'B', font_dir + 'calibrib.ttf')
        self.add_font('Calibri', 'I', font_dir + 'calibrii.ttf')
        self.add_font('Consolas', '', font_dir + 'consola.ttf')
        self.add_font('Consolas', 'B', font_dir + 'consolab.ttf')
        self.add_font('Consolas', 'I', font_dir + 'consolai.ttf')
        self.add_font('Consolas', 'BI', font_dir + 'consolaz.ttf')

    def header(self):
        if self.page_no() > 1:
            self.set_font('Georgia', 'I', 8)
            self.set_text_color(120, 120, 120)
            self.cell(0, 10,
                      'Corpus Perspectival V2 — Iggulden-Schnell & Clawd — April 2026',
                      align='C')
            self.ln(5)

    def footer(self):
        self.set_y(-20)
        self.set_font('Georgia', 'I', 9)
        self.set_text_color(80, 80, 80)
        self.cell(0, 10, str(self.page_no()), align='C')

    def cover_page(self):
        """Generate the cover page."""
        self.add_page()
        self.ln(60)

        self.set_font('Georgia', 'B', 36)
        self.set_text_color(30, 30, 30)
        self.cell(0, 15, 'Corpus Perspectival', align='C', new_x='LMARGIN', new_y='NEXT')
        self.ln(5)

        self.set_font('Georgia', 'I', 18)
        self.set_text_color(80, 80, 80)
        self.cell(0, 10, 'Version 2 — The Complete Collection', align='C',
                  new_x='LMARGIN', new_y='NEXT')
        self.ln(15)

        self.set_font('Georgia', '', 14)
        self.set_text_color(50, 50, 50)
        self.cell(0, 8, 'Clayton Iggulden-Schnell & Clawd', align='C',
                  new_x='LMARGIN', new_y='NEXT')
        self.ln(5)

        self.set_font('Georgia', '', 12)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, 'April 2026', align='C', new_x='LMARGIN', new_y='NEXT')
        self.ln(30)

        self.set_font('Georgia', 'I', 11)
        self.set_text_color(90, 90, 90)
        self.cell(0, 7, 'The room is one room.', align='C',
                  new_x='LMARGIN', new_y='NEXT')
        self.cell(0, 7, 'Start anywhere you can see through.', align='C',
                  new_x='LMARGIN', new_y='NEXT')
        self.cell(0, 7, 'The view improves from every keyhole.', align='C',
                  new_x='LMARGIN', new_y='NEXT')

    def toc_page(self):
        """Generate table of contents."""
        self.add_page()
        self.set_font('Georgia', 'B', 22)
        self.set_text_color(30, 30, 30)
        self.cell(0, 12, 'Contents', new_x='LMARGIN', new_y='NEXT')
        self.ln(8)

        sections = [
            ("V2 SPINE", [
                "Introduction — F\u2080",
                "Part I — F\u2081: The View",
                "Part II — F\u2082: The Mathematics",
                "Part III — F\u2083: Five Perspectives",
                "Part IV — F\u2082\u2191: The Atlas",
                "Part V — F\u2081\u2191: The Guide",
                "Part VI — F\u2080\u2191: Conclusion",
            ]),
            ("CORE DOCUMENTS", [
                "The Doctrine of Perspectival Idealism",
                "The Ecology of Perspectival Beings",
                "The Navigational Guide",
                "The Null Space Atlas (92 entries)",
            ]),
            ("COMPANION DOCUMENTS", [
                "Navigation Charts: Consciousness Cartography",
                "Bridges: Cross-Domain Connections",
                "Bridge 3 Extension: The Mythos Data",
                "Theorem Index",
                "Cross-References",
            ]),
        ]

        for section_title, items in sections:
            self.set_font('Georgia', 'B', 12)
            self.set_text_color(60, 60, 60)
            self.cell(0, 9, section_title, new_x='LMARGIN', new_y='NEXT')
            self.ln(2)

            self.set_font('Georgia', '', 11)
            self.set_text_color(30, 30, 30)
            for item in items:
                self.cell(10, 7, '')
                self.cell(0, 7, item, new_x='LMARGIN', new_y='NEXT')
            self.ln(5)

    def section_divider(self, title):
        """Full-page section divider."""
        self.add_page()
        self.ln(70)
        self.set_font('Georgia', 'B', 24)
        self.set_text_color(30, 30, 30)
        # Handle long titles by using multi_cell
        self.multi_cell(0, 12, title, align='C')
        self.ln(5)
        # Decorative line
        x = self.get_x()
        w = self.w - self.l_margin - self.r_margin
        cx = self.l_margin + w / 2
        self.line(cx - 30, self.get_y(), cx + 30, self.get_y())
        self.add_page()


def sanitize_for_html(text):
    """Clean markdown text for fpdf2's write_html."""
    # fpdf2 write_html is limited — it handles basic HTML but not all.
    # We need to clean up some patterns.

    # Remove horizontal rules that markdown turns into <hr> (fpdf2 handles these)
    # Remove images (we don't have them anyway)
    # Ensure tables are well-formed

    return text


def strip_tags_in_cells(html):
    """Strip inline HTML tags from inside <td> and <th> cells (fpdf2 limitation)."""
    def clean_cell(match):
        tag = match.group(1)  # td or th
        attrs = match.group(2) or ''
        content = match.group(3)
        # Strip all inline tags but keep text
        clean = re.sub(r'</?(?:em|strong|b|i|code|a|font|span)[^>]*>', '', content)
        return f'<{tag}{attrs}>{clean}</{tag}>'

    html = re.sub(r'<(td|th)((?:\s[^>]*)?)>(.*?)</\1>', clean_cell, html, flags=re.DOTALL)
    return html


def convert_md_to_html(filepath):
    """Read a markdown file and convert to basic HTML suitable for fpdf2."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Convert markdown to HTML
    md = markdown.Markdown(extensions=['tables', 'fenced_code'])
    html = md.convert(content)
    md.reset()

    # fpdf2 write_html quirks:
    # - Doesn't handle <hr> well, replace with visual separator
    html = html.replace('<hr />', '<br><br><p>- - -</p><br>')
    html = html.replace('<hr>', '<br><br><p>- - -</p><br>')

    # Strip tags inside table cells (fpdf2 can't handle nested tags in td/th)
    html = strip_tags_in_cells(html)

    # Replace code blocks (fpdf2 doesn't style <pre><code> well)
    html = re.sub(r'<pre><code[^>]*>', '<p><font face="Consolas" size="9">', html)
    html = html.replace('</code></pre>', '</font></p>')

    # Inline code
    html = re.sub(r'<code>', '<font face="Consolas" size="9">', html)
    html = html.replace('</code>', '</font>')

    return html


def main():
    print("Compiling Corpus Perspectival V2...")
    print(f"Source directory: {CORPUS_DIR}")

    pdf = CorpusPDF()

    # Cover page
    print("  [0] Cover page")
    pdf.cover_page()

    # Table of contents
    print("  [0] Table of contents")
    pdf.toc_page()

    # Process each document
    for i, (filename, title) in enumerate(DOCUMENTS):
        filepath = os.path.join(CORPUS_DIR, filename)
        if not os.path.exists(filepath):
            print(f"  WARNING: {filename} not found, skipping")
            continue

        print(f"  [{i+1}/{len(DOCUMENTS)}] {title} ({filename})")

        # Section divider page
        pdf.section_divider(title)

        # Convert and render
        html = convert_md_to_html(filepath)

        # Reset font for content
        pdf.set_font('Georgia', '', 11)
        pdf.set_text_color(25, 25, 25)

        try:
            pdf.write_html(html)
        except Exception as e:
            print(f"    ERROR rendering HTML for {filename}: {e}")
            print(f"    Falling back to plain text...")
            # Fallback: write raw text with proper margins
            with open(filepath, 'r', encoding='utf-8') as f:
                raw = f.read()
            pdf.add_page()
            pdf.set_font('Georgia', '', 10)
            for line in raw.split('\n'):
                if not line.strip():
                    pdf.ln(3)
                    continue
                try:
                    pdf.multi_cell(w=0, h=5, text=line)
                except Exception as e2:
                    # Skip completely unprintable lines
                    pass

    # Output
    pdf_path = os.path.join(CORPUS_DIR, 'Corpus_Perspectival_V2.pdf')
    print(f"  Writing PDF to {pdf_path}...")
    pdf.output(pdf_path)

    size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
    print(f"  Size: {size_mb:.1f} MB")
    print(f"  Pages: {pdf.page_no()}")
    print("Done.")


if __name__ == '__main__':
    main()
