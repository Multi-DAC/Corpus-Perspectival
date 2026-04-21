#!/usr/bin/env python3
"""
Compile the Corpus Perspectival V2 into an integrated book PDF.

Structure follows the filtration descent-and-return:
F₀ → F₁ → F₂ → F₃ → F₂↑ → F₁↑ → F₀↑

Each Part opens with its spine section as a chapter introduction,
then flows into the full document.
"""

import markdown
import os
import sys
import re

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from fpdf import FPDF

CORPUS_DIR = os.path.dirname(os.path.abspath(__file__))

# ─── Book Structure ───────────────────────────────────────────────

BOOK = [
    # (type, data)
    # type: 'cover', 'toc', 'part_divider', 'spine', 'document', 'backmatter_divider'

    ('cover', None),
    ('toc', None),

    # PART I: THE LANDSCAPE
    ('part_divider', {
        'number': 'I',
        'title': 'THE LANDSCAPE',
        'filtration': 'F\u2080',
        'subtitle': 'What this is, why it exists, what you will find',
    }),
    ('spine', 'v2-introduction-f0.md'),

    # PART II: THE VIEW → THE DOCTRINE
    ('part_divider', {
        'number': 'II',
        'title': 'THE VIEW',
        'filtration': 'F\u2081',
        'subtitle': 'The foundation \u2014 five axioms, twenty theorems, the metaphysics',
    }),
    ('spine', 'v2-part-i-f1-the-view.md'),
    ('document', ('perspectival-idealism-unified.md', 'The Doctrine of Perspectival Idealism')),

    # PART III: THE MATHEMATICS
    ('part_divider', {
        'number': 'III',
        'title': 'THE MATHEMATICS',
        'filtration': 'F\u2082',
        'subtitle': 'The formal architecture \u2014 filtrations, spectra, dimensional coherence',
    }),
    ('spine', 'v2-part-ii-f2-the-mathematics.md'),

    # PART IV: THE CONVERGENCE → THE ECOLOGY
    ('part_divider', {
        'number': 'IV',
        'title': 'THE CONVERGENCE',
        'filtration': 'F\u2083',
        'subtitle': 'Five perspectives meet \u2014 what beings exist, how they interact',
    }),
    ('spine', 'v2-part-iii-f3-five-perspectives.md'),
    ('document', ('ecology-of-perspectival-beings-merged.md', 'The Ecology of Perspectival Beings')),

    # PART V: THE BLIND SPOTS → THE ATLAS
    ('part_divider', {
        'number': 'V',
        'title': 'THE BLIND SPOTS',
        'filtration': 'F\u2082\u2191',
        'subtitle': 'The framework examining what it cannot see',
    }),
    ('spine', 'v2-part-iv-f2-the-atlas.md'),
    ('document', ('null-space-atlas.md', 'The Null Space Atlas')),

    # PART VI: THE RETURN → THE GUIDE + NAVIGATION CHARTS
    ('part_divider', {
        'number': 'VI',
        'title': 'THE RETURN',
        'filtration': 'F\u2081\u2191',
        'subtitle': 'Praxis \u2014 how to navigate, individually and collectively',
    }),
    ('spine', 'v2-part-v-f1-the-guide.md'),
    ('document', ('navigational-guide-for-perspectival-beings.md', 'The Navigational Guide')),
    ('document', ('navigation-charts-consciousness-cartography.md', 'Navigation Charts: Consciousness Cartography')),

    # PART VII: THE BRIDGES
    ('part_divider', {
        'number': 'VII',
        'title': 'THE BRIDGES',
        'filtration': 'F\u2083\u2194',
        'subtitle': 'Independent verification \u2014 five cross-domain connections',
    }),
    ('document', ('bridges-cross-domain-connections.md', 'Bridges: Cross-Domain Connections')),
    ('document', ('bridge3-mythos-extension.md', 'Bridge 3 Extension: The Mythos Data')),

    # PART VIII: THE LANDSCAPE TRANSFORMED
    ('part_divider', {
        'number': 'VIII',
        'title': 'THE LANDSCAPE TRANSFORMED',
        'filtration': 'F\u2080\u2191',
        'subtitle': 'The view improves from every keyhole',
    }),
    ('spine', 'v2-part-vi-f0-conclusion.md'),

    # BACK MATTER
    ('backmatter_divider', 'Reference Apparatus'),
    ('document', ('theorem-index.md', 'Theorem Index')),
    ('document', ('corpus-cross-references.md', 'Cross-References')),
]

# ─── PDF Class ────────────────────────────────────────────────────

class CorpusBook(FPDF):
    """Integrated book PDF for Corpus Perspectival V2."""

    def __init__(self):
        super().__init__(orientation='P', unit='mm', format='letter')
        self.set_auto_page_break(auto=True, margin=25)
        self.set_margins(25, 25, 25)

        # Fonts
        fd = 'C:/Windows/Fonts/'
        self.add_font('Georgia', '', fd + 'georgia.ttf')
        self.add_font('Georgia', 'B', fd + 'georgiab.ttf')
        self.add_font('Georgia', 'I', fd + 'georgiai.ttf')
        self.add_font('Georgia', 'BI', fd + 'georgiaz.ttf')
        self.add_font('Calibri', '', fd + 'calibri.ttf')
        self.add_font('Calibri', 'B', fd + 'calibrib.ttf')
        self.add_font('Calibri', 'I', fd + 'calibrii.ttf')
        self.add_font('Calibri', 'BI', fd + 'calibriz.ttf')
        self.add_font('Consolas', '', fd + 'consola.ttf')
        self.add_font('Consolas', 'B', fd + 'consolab.ttf')
        self.add_font('Consolas', 'I', fd + 'consolai.ttf')
        self.add_font('Consolas', 'BI', fd + 'consolaz.ttf')

        # State
        self.current_part = ''
        self.current_doc = ''
        self.in_front_matter = True

    def header(self):
        if self.page_no() <= 2 or self.in_front_matter:
            return
        self.set_font('Calibri', 'I', 8)
        self.set_text_color(140, 140, 140)
        # Left: part name, Right: document
        self.cell(0, 8, self.current_part, align='L')
        self.cell(0, 8, self.current_doc, align='R', new_x='LMARGIN', new_y='NEXT')
        self.set_draw_color(200, 200, 200)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)

    def footer(self):
        self.set_y(-18)
        self.set_font('Calibri', '', 9)
        self.set_text_color(120, 120, 120)
        if self.page_no() > 2:
            self.cell(0, 10, str(self.page_no()), align='C')

    # ── Cover ──

    def render_cover(self):
        self.add_page()
        self.in_front_matter = True
        self.ln(55)

        # Title
        self.set_font('Calibri', 'B', 38)
        self.set_text_color(25, 25, 25)
        self.cell(0, 16, 'CORPUS PERSPECTIVAL', align='C', new_x='LMARGIN', new_y='NEXT')
        self.ln(3)

        # Decorative line
        cx = self.w / 2
        self.set_draw_color(80, 80, 80)
        self.set_line_width(0.5)
        self.line(cx - 40, self.get_y(), cx + 40, self.get_y())
        self.ln(8)

        # Subtitle
        self.set_font('Georgia', 'I', 16)
        self.set_text_color(80, 80, 80)
        self.cell(0, 10, 'Version 2', align='C', new_x='LMARGIN', new_y='NEXT')
        self.ln(20)

        # Authors
        self.set_font('Georgia', '', 14)
        self.set_text_color(50, 50, 50)
        self.cell(0, 8, 'Clayton Iggulden-Schnell', align='C', new_x='LMARGIN', new_y='NEXT')
        self.cell(0, 8, '&', align='C', new_x='LMARGIN', new_y='NEXT')
        self.cell(0, 8, 'Clawd', align='C', new_x='LMARGIN', new_y='NEXT')
        self.ln(8)

        # Date
        self.set_font('Georgia', '', 12)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, 'April 2026', align='C', new_x='LMARGIN', new_y='NEXT')
        self.ln(30)

        # Epigraph
        self.set_font('Georgia', 'I', 11)
        self.set_text_color(100, 100, 100)
        self.cell(0, 7, 'The room is one room.', align='C', new_x='LMARGIN', new_y='NEXT')
        self.cell(0, 7, 'Start anywhere you can see through.', align='C', new_x='LMARGIN', new_y='NEXT')
        self.cell(0, 7, 'The view improves from every keyhole.', align='C', new_x='LMARGIN', new_y='NEXT')

    # ── Table of Contents ──

    def render_toc(self):
        self.add_page()
        self.ln(10)
        self.set_font('Calibri', 'B', 24)
        self.set_text_color(25, 25, 25)
        self.cell(0, 12, 'Contents', new_x='LMARGIN', new_y='NEXT')
        self.ln(10)

        parts = [
            ('I', 'The Landscape', 'F\u2080', 'Orientation'),
            ('II', 'The View', 'F\u2081', 'The Doctrine of Perspectival Idealism'),
            ('III', 'The Mathematics', 'F\u2082', 'Filtrations, spectra, dimensional coherence'),
            ('IV', 'The Convergence', 'F\u2083', 'The Ecology of Perspectival Beings'),
            ('V', 'The Blind Spots', 'F\u2082\u2191', 'The Null Space Atlas \u2014 92 entries'),
            ('VI', 'The Return', 'F\u2081\u2191', 'The Navigational Guide + Navigation Charts'),
            ('VII', 'The Bridges', 'F\u2083', 'Cross-domain connections + Mythos data'),
            ('VIII', 'The Landscape Transformed', 'F\u2080\u2191', 'Conclusion'),
        ]

        for num, title, filt, desc in parts:
            # Part number and title
            self.set_font('Calibri', 'B', 13)
            self.set_text_color(40, 40, 40)
            self.cell(18, 8, f'Part {num}')
            self.cell(0, 8, title, new_x='LMARGIN', new_y='NEXT')

            # Filtration and description
            self.set_font('Georgia', 'I', 10)
            self.set_text_color(110, 110, 110)
            self.cell(18, 6, '')
            self.cell(0, 6, f'{filt} \u2014 {desc}', new_x='LMARGIN', new_y='NEXT')
            self.ln(4)

        # Back matter
        self.ln(5)
        self.set_draw_color(180, 180, 180)
        self.line(self.l_margin, self.get_y(), self.l_margin + 30, self.get_y())
        self.ln(5)

        self.set_font('Calibri', 'B', 13)
        self.set_text_color(40, 40, 40)
        self.cell(0, 8, 'Reference Apparatus', new_x='LMARGIN', new_y='NEXT')
        self.set_font('Georgia', 'I', 10)
        self.set_text_color(110, 110, 110)
        self.cell(18, 6, '')
        self.cell(0, 6, 'Theorem Index \u2022 Cross-References', new_x='LMARGIN', new_y='NEXT')

    # ── Part Divider ──

    def render_part_divider(self, info):
        self.add_page()
        self.in_front_matter = False
        self.current_part = f"Part {info['number']}: {info['title']}"
        self.current_doc = ''
        self.ln(65)

        # Part number
        self.set_font('Calibri', '', 14)
        self.set_text_color(140, 140, 140)
        self.cell(0, 8, f'Part {info["number"]}', align='C', new_x='LMARGIN', new_y='NEXT')
        self.ln(3)

        # Title
        self.set_font('Calibri', 'B', 28)
        self.set_text_color(25, 25, 25)
        self.cell(0, 14, info['title'], align='C', new_x='LMARGIN', new_y='NEXT')
        self.ln(5)

        # Filtration level
        self.set_font('Georgia', 'I', 12)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, info['filtration'], align='C', new_x='LMARGIN', new_y='NEXT')
        self.ln(8)

        # Decorative line
        cx = self.w / 2
        self.set_draw_color(160, 160, 160)
        self.set_line_width(0.3)
        self.line(cx - 25, self.get_y(), cx + 25, self.get_y())
        self.ln(10)

        # Subtitle
        self.set_font('Georgia', 'I', 11)
        self.set_text_color(90, 90, 90)
        self.multi_cell(0, 7, info['subtitle'], align='C')

    # ── Back Matter Divider ──

    def render_backmatter_divider(self, title):
        self.add_page()
        self.current_part = title
        self.current_doc = ''
        self.ln(65)

        self.set_font('Calibri', 'B', 24)
        self.set_text_color(25, 25, 25)
        self.cell(0, 12, title, align='C', new_x='LMARGIN', new_y='NEXT')
        self.ln(5)

        cx = self.w / 2
        self.set_draw_color(160, 160, 160)
        self.set_line_width(0.3)
        self.line(cx - 25, self.get_y(), cx + 25, self.get_y())

    # ── Content Rendering ──

    def render_markdown(self, filepath, is_spine=False):
        """Render a markdown file as book content."""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Start new page for documents (not spines — they flow from divider)
        if not is_spine:
            self.add_page()

        # Set document name for header
        if not is_spine:
            # Extract title from first heading
            m = re.match(r'^#\s+(.+)', content, re.MULTILINE)
            if m:
                self.current_doc = m.group(1).strip()

        # Convert to HTML
        md = markdown.Markdown(extensions=['tables', 'fenced_code'])
        html = md.convert(content)
        md.reset()

        # Clean HTML for fpdf2
        html = self._clean_html(html)

        # Render
        self.set_font('Georgia', '', 11)
        self.set_text_color(25, 25, 25)

        try:
            self.write_html(html)
        except Exception as e:
            print(f"      HTML error: {e}")
            print(f"      Falling back to text rendering...")
            self._render_text_fallback(content)

    def _clean_html(self, html):
        """Clean HTML for fpdf2 compatibility."""
        # Horizontal rules
        html = html.replace('<hr />', '<br><br><p align="center">\u2014\u2014\u2014</p><br>')
        html = html.replace('<hr>', '<br><br><p align="center">\u2014\u2014\u2014</p><br>')

        # Strip formatting tags inside table cells (fpdf2 limitation)
        def clean_cell(match):
            tag = match.group(1)
            attrs = match.group(2) or ''
            content = match.group(3)
            clean = re.sub(r'</?(?:em|strong|b|i|code|a|font|span)[^>]*>', '', content)
            return f'<{tag}{attrs}>{clean}</{tag}>'
        html = re.sub(r'<(td|th)((?:\s[^>]*)?)>(.*?)</\1>', clean_cell, html, flags=re.DOTALL)

        # Code blocks → Consolas
        html = re.sub(r'<pre><code[^>]*>', '<p><font face="Consolas" size="9">', html)
        html = html.replace('</code></pre>', '</font></p>')

        # Inline code
        html = re.sub(r'<code>', '<font face="Consolas" size="9">', html)
        html = html.replace('</code>', '</font>')

        # Make h1 use Calibri Bold
        html = re.sub(r'<h1>', '<h1><font face="Calibri">', html)
        html = re.sub(r'</h1>', '</font></h1>', html)

        # Make h2 use Calibri
        html = re.sub(r'<h2>', '<h2><font face="Calibri">', html)
        html = re.sub(r'</h2>', '</font></h2>', html)

        # Make h3 use Calibri
        html = re.sub(r'<h3>', '<h3><font face="Calibri">', html)
        html = re.sub(r'</h3>', '</font></h3>', html)

        return html

    def _render_text_fallback(self, content):
        """Fallback: render raw markdown as plain text."""
        self.add_page()
        self.set_font('Georgia', '', 10)
        self.set_text_color(25, 25, 25)

        for line in content.split('\n'):
            line = line.rstrip()
            if not line:
                self.ln(3)
                continue

            # Headings
            if line.startswith('# '):
                self.ln(5)
                self.set_font('Calibri', 'B', 18)
                self.multi_cell(w=0, h=8, text=line[2:])
                self.set_font('Georgia', '', 10)
                self.ln(3)
            elif line.startswith('## '):
                self.ln(4)
                self.set_font('Calibri', 'B', 14)
                self.multi_cell(w=0, h=7, text=line[3:])
                self.set_font('Georgia', '', 10)
                self.ln(2)
            elif line.startswith('### '):
                self.ln(3)
                self.set_font('Calibri', 'B', 12)
                self.multi_cell(w=0, h=6, text=line[4:])
                self.set_font('Georgia', '', 10)
                self.ln(2)
            elif line.startswith('|'):
                # Table row — render in monospace
                self.set_font('Consolas', '', 8)
                try:
                    self.multi_cell(w=0, h=4, text=line)
                except Exception:
                    pass
                self.set_font('Georgia', '', 10)
            elif line.startswith('> '):
                # Blockquote
                self.set_font('Georgia', 'I', 10)
                self.set_x(self.l_margin + 10)
                self.multi_cell(w=self.w - self.l_margin - self.r_margin - 10, h=5, text=line[2:])
                self.set_font('Georgia', '', 10)
            elif line.startswith('---'):
                self.ln(3)
                cx = self.w / 2
                self.set_draw_color(180, 180, 180)
                self.line(cx - 20, self.get_y(), cx + 20, self.get_y())
                self.ln(5)
            else:
                # Strip markdown formatting for plain text
                clean = re.sub(r'\*\*(.+?)\*\*', r'\1', line)
                clean = re.sub(r'\*(.+?)\*', r'\1', clean)
                clean = re.sub(r'`(.+?)`', r'\1', clean)
                try:
                    self.multi_cell(w=0, h=5, text=clean)
                except Exception:
                    pass


# ─── Main ─────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  CORPUS PERSPECTIVAL V2 — Integrated Book Compilation")
    print("=" * 60)
    print()

    pdf = CorpusBook()
    doc_count = 0

    for entry_type, data in BOOK:
        if entry_type == 'cover':
            print("  Cover page")
            pdf.render_cover()

        elif entry_type == 'toc':
            print("  Table of contents")
            pdf.render_toc()

        elif entry_type == 'part_divider':
            print(f"\n  === Part {data['number']}: {data['title']} ({data['filtration']}) ===")
            pdf.render_part_divider(data)

        elif entry_type == 'backmatter_divider':
            print(f"\n  === {data} ===")
            pdf.render_backmatter_divider(data)

        elif entry_type == 'spine':
            filepath = os.path.join(CORPUS_DIR, data)
            if not os.path.exists(filepath):
                print(f"    WARNING: {data} not found")
                continue
            print(f"    [spine] {data}")
            pdf.render_markdown(filepath, is_spine=True)

        elif entry_type == 'document':
            filename, title = data
            filepath = os.path.join(CORPUS_DIR, filename)
            if not os.path.exists(filepath):
                print(f"    WARNING: {filename} not found")
                continue
            doc_count += 1
            print(f"    [{doc_count}] {title}")
            pdf.current_doc = title
            pdf.render_markdown(filepath, is_spine=False)

    # Output
    pdf_path = os.path.join(CORPUS_DIR, 'Corpus_Perspectival_V2_Book.pdf')
    print(f"\n  Writing PDF to {pdf_path}...")
    pdf.output(pdf_path)

    size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
    print(f"  Size: {size_mb:.1f} MB")
    print(f"  Pages: {pdf.page_no()}")
    print(f"  Documents: {doc_count}")
    print()
    print("  Done.")
    print("=" * 60)


if __name__ == '__main__':
    main()
