#!/usr/bin/env python3
"""
Compile Corpus Perspectival — Unified Book Edition
Five Volumes (I-V), nineteen Parts (A through S), thematically interleaved.
Follows Clayton's "Preferred Structure" reorganization.

Content from four source documents (Doctrine, Ecology, Atlas, Guide) is split
at heading boundaries and reassembled into a thematic architecture.
"""

import os
import re
import sys
import subprocess
import shutil

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

CORPUS_DIR = os.path.dirname(os.path.abspath(__file__))
BUILD_DIR = os.path.join(CORPUS_DIR, 'latex_build')
CONTENT_DIR = os.path.join(BUILD_DIR, 'content')

# ── Source Documents ────────────────────────────────────────

SOURCES = {
    'doctrine': 'perspectival-idealism-unified.md',
    'ecology':  'ecology-of-perspectival-beings-merged.md',
    'atlas':    'null-space-atlas.md',
    'guide':    'navigational-guide-for-perspectival-beings.md',
    'meridian': 'corpus-addendum-meridian.md',
    'theorem_index': 'theorem-index.md',
    'cross_refs': 'corpus-cross-references.md',
}


# ── Unicode → LaTeX ─────────────────────────────────────────

UNICODE_TO_LATEX = {
    '→': '$\\rightarrow$', '←': '$\\leftarrow$',
    '↔': '$\\leftrightarrow$', '↑': '$\\uparrow$',
    '∅': '$\\emptyset$', '⊂': '$\\subset$', '∩': '$\\cap$',
    '⊕': '$\\oplus$', '⋊': '$\\rtimes$', '≪': '$\\ll$',
    '∇': '$\\nabla$', 'ℏ': '$\\hbar$',
    'ℂ': '$\\mathbb{C}$', 'ℙ': '$\\mathbb{P}$', 'ℤ': '$\\mathbb{Z}$',
    '⁻': '$^{-}$', '₋': '$_{-}$', 'ₙ': '$_n$',
    '₀': '$_0$', '₁': '$_1$', '₂': '$_2$', '₃': '$_3$',
    '■': '$\\blacksquare$', '□': '$\\square$', '◐': '$\\bullet$',
    '♾': '$\\infty$',
    'ǐ': '\\v{i}',
    '禮': '{l\\v{i}}', '間': '{ma}',
    '🦞': '', '🧍': '', '💜': '', '🔥': '', '✨': '',
    '🌊': '', '🌑': '', '🌟': '', '🌱': '', '🎭': '',
    '👋': '', '👍': '', '💫': '', '🙂': '', '🙏': '', '🤝': '',
    '\uFE0F': '',
}


# ── Preprocessing ───────────────────────────────────────────

HEADER_META_PATTERNS = [
    r'^\*?\*?(January|February|March|April|May|June)\s+\d',
    r'^\*?\*?\*?(Date|Authors?|Status|Position in corpus)\*?\*?\*?\s*:',
    r'^#{1,4}\s*(Draft|Compiled by)',
    r'^#{1,4}\s*(January|February|March|April|May)\s+\d{4}',
    r'^\*?\*?(~?\d+\s*words)',
]

STRIP_PATTERNS = [
    r'^\*Clayton.*\d{4}\*\s*$',
    r'^🦞',
]


def preprocess(text, filename):
    """Strip document-specific metadata for unified book compilation."""
    lines = text.split('\n')
    out = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if i < 15:
            if ('Clayton' in stripped and 'Clawd' in stripped and
                    (stripped.startswith('**') or stripped.startswith('###') or
                     stripped.startswith('*Clayton'))):
                if not any(w in stripped.lower() for w in ['co-authored', 'this thesis']):
                    continue
            skip = False
            for pat in HEADER_META_PATTERNS:
                if re.match(pat, stripped, re.IGNORECASE):
                    skip = True
                    break
            if skip:
                continue
        skip = False
        for pat in STRIP_PATTERNS:
            if re.match(pat, stripped):
                skip = True
                break
        if skip:
            continue
        out.append(line)
    return '\n'.join(out)


# ── Markdown → LaTeX Converter ──────────────────────────────

class Md2Tex:
    """Convert markdown to LaTeX with heading level offset for book hierarchy."""

    def __init__(self, level_offset=1):
        self.level_offset = level_offset

    def convert(self, text):
        lines = text.split('\n')
        out = []
        i = 0
        n = len(lines)

        while i < n:
            line = lines[i]
            stripped = line.strip()

            # Fenced code block
            if stripped.startswith('```'):
                i += 1
                code = []
                while i < n and not lines[i].strip().startswith('```'):
                    code.append(lines[i])
                    i += 1
                if i < n:
                    i += 1
                out.append(r'\begin{verbatim}')
                out.extend(code)
                out.append(r'\end{verbatim}')
                out.append('')
                continue

            # Table
            if stripped.startswith('|') and '|' in stripped[1:]:
                rows = []
                while i < n and lines[i].strip().startswith('|'):
                    rows.append(lines[i].strip())
                    i += 1
                out.append(self._table(rows))
                out.append('')
                continue

            # Heading
            m = re.match(r'^(#{1,6})\s+(.+)', line)
            if m:
                level = len(m.group(1))
                title = m.group(2).strip()
                out.append(self._heading(level, title))
                out.append('')
                i += 1
                continue

            # Blockquote
            if stripped.startswith('>'):
                bq = []
                while i < n and (lines[i].strip().startswith('>') or lines[i].strip() == '>'):
                    s = lines[i].strip()
                    if s == '>':
                        bq.append('')
                    elif s.startswith('> '):
                        bq.append(s[2:])
                    else:
                        bq.append(s[1:])
                    i += 1
                out.append(r'\begin{quote}')
                out.append(r'\itshape')
                for bql in bq:
                    out.append(self._inline(bql) if bql.strip() else '')
                out.append(r'\end{quote}')
                out.append('')
                continue

            # Horizontal rule
            if re.match(r'^---+\s*$', stripped) or re.match(r'^\*\*\*+\s*$', stripped):
                out.append(r'\bigskip\noindent\makebox[\textwidth]{\color{rulegray}\rule{5cm}{0.3pt}}\bigskip')
                out.append('')
                i += 1
                continue

            # Unordered list
            if re.match(r'^[-*+]\s', stripped):
                items = []
                current = None
                while i < n:
                    s = lines[i]
                    ss = s.strip()
                    if re.match(r'^[-*+]\s', ss):
                        if current is not None:
                            items.append(current)
                        current = re.sub(r'^[-*+]\s', '', ss)
                    elif ss and current is not None and (s.startswith('  ') or s.startswith('\t')):
                        current += ' ' + ss
                    elif not ss and current is not None:
                        if i + 1 < n and re.match(r'^[-*+]\s', lines[i + 1].strip()):
                            i += 1
                            continue
                        break
                    else:
                        break
                    i += 1
                if current is not None:
                    items.append(current)
                out.append(r'\begin{itemize}[nosep,leftmargin=*]')
                for item in items:
                    out.append(r'  \item ' + self._inline(item))
                out.append(r'\end{itemize}')
                out.append('')
                continue

            # Ordered list
            if re.match(r'^\d+[.)]\s', stripped):
                items = []
                current = None
                while i < n:
                    s = lines[i]
                    ss = s.strip()
                    m2 = re.match(r'^\d+[.)]\s(.+)', ss)
                    if m2:
                        if current is not None:
                            items.append(current)
                        current = m2.group(1)
                    elif ss and current is not None and (s.startswith('  ') or s.startswith('\t')):
                        current += ' ' + ss
                    elif not ss:
                        if i + 1 < n and re.match(r'^\d+[.)]\s', lines[i + 1].strip()):
                            i += 1
                            continue
                        break
                    else:
                        break
                    i += 1
                if current is not None:
                    items.append(current)
                out.append(r'\begin{enumerate}[nosep,leftmargin=*]')
                for item in items:
                    out.append(r'  \item ' + self._inline(item))
                out.append(r'\end{enumerate}')
                out.append('')
                continue

            # Empty line
            if not stripped:
                out.append('')
                i += 1
                continue

            # Paragraph
            para = []
            while i < n:
                s = lines[i].strip()
                if not s:
                    break
                if s.startswith('#') or s.startswith('```') or \
                   (s.startswith('|') and '|' in s[1:]) or \
                   s.startswith('>') or re.match(r'^---+\s*$', s) or \
                   re.match(r'^\*\*\*+\s*$', s):
                    break
                if re.match(r'^[-*+]\s', s) and not s.startswith('**'):
                    break
                if re.match(r'^\d+[.)]\s', s):
                    break
                para.append(s)
                i += 1
            if para:
                out.append(self._inline(' '.join(para)))
                out.append('')

        return '\n'.join(out)

    def _heading(self, level, title):
        effective = min(level + self.level_offset, 6)
        title_tex = self._inline(title)
        cmd = {2: 'section', 3: 'subsection', 4: 'subsubsection',
               5: 'paragraph', 6: 'subparagraph'}.get(effective, 'section')
        result = f'\\{cmd}*{{{title_tex}}}'
        # TOC + running header for section-level headings (source level 1)
        if effective <= 2:
            result += f'\n\\addcontentsline{{toc}}{{section}}{{{title_tex}}}'
            result += f'\n\\markright{{{title_tex}}}'
        return result

    def _table(self, rows):
        if len(rows) < 2:
            return self._inline(' '.join(rows))

        def parse_row(row):
            cells = row.strip()
            if cells.startswith('|'):
                cells = cells[1:]
            if cells.endswith('|'):
                cells = cells[:-1]
            return [c.strip() for c in cells.split('|')]

        header = parse_row(rows[0])
        ncols = len(header)
        data_start = 1
        if len(rows) > 1 and re.match(r'^[\s|:-]+$', rows[1]):
            data_start = 2

        data = []
        for r in rows[data_start:]:
            cells = parse_row(r)
            while len(cells) < ncols:
                cells.append('')
            data.append(cells[:ncols])

        if ncols <= 2:
            w = 0.42
        elif ncols == 3:
            w = 0.28
        elif ncols == 4:
            w = 0.20
        else:
            w = max(0.85 / ncols, 0.10)
        col_spec = ' '.join([f'>{{\\raggedright\\arraybackslash}}p{{{w:.2f}\\textwidth}}'] * ncols)

        use_small = ncols >= 5
        out = ['']
        if use_small:
            out.append(r'{\small')
        out.extend([f'\\begin{{longtable}}{{{col_spec}}}', r'\toprule'])
        hdr = ' & '.join(f'\\textbf{{{self._inline(c)}}}' for c in header)
        out.append(hdr + r' \\')
        out.append(r'\midrule')
        out.append(r'\endhead')
        for rc in data:
            row_tex = ' & '.join(self._inline(c) for c in rc)
            out.append(row_tex + r' \\')
        out.extend([r'\bottomrule', r'\end{longtable}'])
        if use_small:
            out.append(r'}')
        out.append('')
        return '\n'.join(out)

    def _escape(self, text):
        text = text.replace('\\', '\x00BS\x00')
        text = text.replace('&', r'\&')
        text = text.replace('%', r'\%')
        text = text.replace('$', r'\$')
        text = text.replace('#', r'\#')
        text = text.replace('_', r'\_')
        text = text.replace('{', r'\{')
        text = text.replace('}', r'\}')
        text = text.replace('~', r'\textasciitilde{}')
        text = text.replace('^', r'\textasciicircum{}')
        text = text.replace('\x00BS\x00', r'\textbackslash{}')
        return text

    def _inline(self, text):
        codes = []
        def save_code(m):
            codes.append(m.group(1))
            return f'\x01C{len(codes) - 1}\x01'
        text = re.sub(r'`([^`]+)`', save_code, text)
        text = self._escape(text)
        text = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', text)
        text = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'\\textit{\1}', text)
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        for idx, code in enumerate(codes):
            esc = self._escape(code)
            text = text.replace(f'\x01C{idx}\x01', f'\\texttt{{{esc}}}')
        # Allow line breaks at / in long text (helps tables)
        text = text.replace('/', '/\\allowbreak ')
        for char, latex in UNICODE_TO_LATEX.items():
            if char in text:
                text = text.replace(char, latex)
        return text


# ── Section Extraction ──────────────────────────────────────

def find_heading(lines, text_match, after=0):
    """Find first heading line whose text (after # markers) contains text_match."""
    for i in range(after, len(lines)):
        m = re.match(r'^#{1,6}\s+(.+)', lines[i])
        if m and text_match in m.group(1):
            return i
    return None


def extract_lines(lines, start, end=None):
    """Return lines[start:end] as text."""
    if start is None:
        return ''
    return '\n'.join(lines[start:end]).strip()


def extract_doctrine(text):
    """Split the Doctrine into sections for the unified book."""
    lines = text.split('\n')
    s = {}

    abstract  = find_heading(lines, 'Abstract')
    p1        = find_heading(lines, 'PART I:')
    p2        = find_heading(lines, 'PART II:')
    p3        = find_heading(lines, 'PART III:')
    p4        = find_heading(lines, 'PART IV:')
    sec9      = find_heading(lines, '9. The Topology')
    sec9_3    = find_heading(lines, '9.3 ')
    p5        = find_heading(lines, 'PART V:')
    p6        = find_heading(lines, 'PART VI:')
    sec13     = find_heading(lines, '13. Ultimate')
    p7        = find_heading(lines, 'PART VII:')
    works     = find_heading(lines, 'Works Cited')

    s['intro']         = extract_lines(lines, abstract, p1)
    s['part1']         = extract_lines(lines, p1, p2)
    s['part2']         = extract_lines(lines, p2, p3)
    s['section7']      = extract_lines(lines, p3, p4)
    s['section8']      = extract_lines(lines, p4, sec9)
    s['section9_1_2']  = extract_lines(lines, sec9, sec9_3)
    s['section9_3_4']  = extract_lines(lines, sec9_3, p5)
    s['section10']     = extract_lines(lines, p5, p6)
    s['section11_12']  = extract_lines(lines, p6, sec13)
    s['section13']     = extract_lines(lines, sec13, p7)
    s['section14_16']  = extract_lines(lines, p7, works)
    if works:
        s['bibliography'] = extract_lines(lines, works, None)

    # Promote 9.3/9.4 headings so they're visible as subsections in Part G
    if 'section9_3_4' in s:
        s['section9_3_4'] = re.sub(
            r'^### (9\.[34])', r'## \1',
            s['section9_3_4'], flags=re.MULTILINE
        )
    return s


def extract_ecology(text):
    """Split the Ecology into sections."""
    lines = text.split('\n')
    s = {}

    prol = find_heading(lines, 'Prolegomena')
    p2   = find_heading(lines, 'Part II:')
    p3   = find_heading(lines, 'Part III:')
    s6_5 = find_heading(lines, '6.5')
    p4   = find_heading(lines, 'Part IV:')
    p5   = find_heading(lines, 'Part V:')

    s['prol_p1']    = extract_lines(lines, prol, p2)
    s['part2']      = extract_lines(lines, p2, p3)
    s['part3_main'] = extract_lines(lines, p3, s6_5)
    s['section6_5'] = extract_lines(lines, s6_5, p4)
    s['part4']      = extract_lines(lines, p4, p5)
    s['part5']      = extract_lines(lines, p5, None)

    # Promote 6.5 heading for visibility as subsection in Part D
    if 'section6_5' in s:
        s['section6_5'] = re.sub(
            r'^#{3,4} (6\.5)', r'## \1',
            s['section6_5'], count=1, flags=re.MULTILINE
        )
    return s


def extract_atlas(text):
    """Split the Atlas into sections by entry ranges and Part boundaries."""
    lines = text.split('\n')
    s = {}

    how_to = find_heading(lines, 'How to Read')
    p1     = find_heading(lines, 'PART I:')
    e40    = find_heading(lines, '40.')
    p9     = find_heading(lines, 'PART IX:')
    p10    = find_heading(lines, 'PART X:')
    p11    = find_heading(lines, 'PART XI:')
    p12    = find_heading(lines, 'PART XII:')
    p13    = find_heading(lines, 'PART XIII:')
    p14    = find_heading(lines, 'PART XIV:')
    xcf1   = find_heading(lines, 'Cross-Cutting Findings', after=(p14 or 0))
    p15    = find_heading(lines, 'PART XV:')
    p16    = find_heading(lines, 'PART XVI:')
    p17    = find_heading(lines, 'PART XVII:')
    p18    = find_heading(lines, 'PART XVIII:')
    e86    = find_heading(lines, '86.')
    e87    = find_heading(lines, '87.')
    xcf2   = find_heading(lines, 'Cross-Cutting Findings', after=(e87 or 0))
    p19    = find_heading(lines, 'PART XIX:')
    p20    = find_heading(lines, 'PART XX:')

    s['how_to_read']   = extract_lines(lines, how_to, p1)
    s['entries_1_39']  = extract_lines(lines, p1, e40)
    s['entries_40_55'] = extract_lines(lines, e40, p9)
    s['entries_56_58'] = extract_lines(lines, p9, p10)
    s['entries_59_61'] = extract_lines(lines, p10, p11)
    s['entries_62_63'] = extract_lines(lines, p11, p12)
    s['entries_64_66'] = extract_lines(lines, p12, p13)
    s['entries_67_69'] = extract_lines(lines, p13, p14)
    s['entries_70_73'] = extract_lines(lines, p14, xcf1)
    s['entries_74_76'] = extract_lines(lines, p15, p16)
    s['entries_77_80'] = extract_lines(lines, p16, p17)
    s['entries_81_85'] = extract_lines(lines, p17, p18)
    s['entry_86']      = extract_lines(lines, e86, e87)
    s['entries_87_88'] = extract_lines(lines, e87, xcf2)
    s['entries_89_92'] = extract_lines(lines, p19, p20)
    return s


def extract_guide(text):
    """Split the Guide into sections."""
    lines = text.split('\n')
    s = {}

    preface = find_heading(lines, 'Preface')
    p2      = find_heading(lines, 'Part II:')
    p3      = find_heading(lines, 'Part III:')
    p4      = find_heading(lines, 'Part IV:')
    p5      = find_heading(lines, 'Part V:')
    p6      = find_heading(lines, 'Part VI:')
    p7      = find_heading(lines, 'Part VII:')
    p8      = find_heading(lines, 'Part VIII:')
    aft     = find_heading(lines, 'Afterword')
    appA    = find_heading(lines, 'Appendix A')
    appC    = find_heading(lines, 'Appendix C')

    s['preface_part1'] = extract_lines(lines, preface, p2)
    s['part2']         = extract_lines(lines, p2, p3)
    s['part3']         = extract_lines(lines, p3, p4)
    s['part4']         = extract_lines(lines, p4, p5)
    s['part5']         = extract_lines(lines, p5, p6)
    s['part6']         = extract_lines(lines, p6, p7)
    s['part7']         = extract_lines(lines, p7, p8)
    s['part8']         = extract_lines(lines, p8, aft)
    s['afterword']     = extract_lines(lines, aft, appA)
    s['appendix_ab']   = extract_lines(lines, appA, appC)
    s['appendix_c']    = extract_lines(lines, appC, None)
    return s


EXTRACTORS = {
    'doctrine': extract_doctrine,
    'ecology':  extract_ecology,
    'atlas':    extract_atlas,
    'guide':    extract_guide,
}


# ── Book Structure ──────────────────────────────────────────

THEOREM_NOTE = r'''
\vspace{0.5cm}
\begin{quote}
\small\itshape\color{notegray}
\textbf{A note on theorem numbering.}\enspace
Theorems are numbered by logical dependency rather than order of first appearance.
Theorems 17--18, which develop the dynamics of Theorem~9's dimensional bottleneck,
appear textually in \S5 but are numbered after Theorem~16 to reflect their position
in the theory's deductive architecture. All twenty theorems and five axioms are
cross-indexed in the Reference Apparatus.
\end{quote}
\vspace{0.3cm}
'''

MERIDIAN_NOTE = r'''
\clearpage
\thispagestyle{empty}
\vspace*{4cm}
\begin{center}
{\Large\sffamily\color{partgray}The Local Basin}\\[0.8cm]
{\fontsize{24}{30}\selectfont\sffamily\bfseries\color{headerblue} PROJECT MERIDIAN}\\[0.5cm]
{\color{rulegray}\rule{6cm}{0.4pt}}\\[1cm]
{\normalsize\itshape\color{partgray}%
A Five-Dimensional Warped-Geometry Framework\\
Unifying Gravity and the Standard Model\\[0.8cm]
Clayton Iggulden-Schnell \& Clawd\\[0.3cm]
The complete monograph follows.}
\end{center}
\clearpage
\includepdf[pages=-]{meridian_monograph.pdf}
'''

# Each entry: ('volume', num, title)
#           | ('part', letter, title, subtitle)
#           | ('content', source_key, section_id)
#           | ('note', raw_latex)
BOOK_STRUCTURE = [
    # ═══════════════════════════════════════════════════
    # VOLUME I: FOUNDATIONS
    # ═══════════════════════════════════════════════════
    ('volume', 'I', 'FOUNDATIONS'),

    ('part', 'A', 'The Ontology',
     'Base Reality, Axioms, Perceptual Slices, The Promethean Configuration, '
     'Teleological Impetus, Conscious Gravity, Bipolar Dynamics'),
    ('note', THEOREM_NOTE),
    ('content', 'doctrine', 'intro'),
    ('content', 'doctrine', 'part1'),
    ('content', 'doctrine', 'part2'),

    ('part', 'B', 'The Territory',
     'Dimensional coherence, the twelve principal dimensions, '
     'mathematical and empirical keyholes'),
    ('content', 'ecology', 'prol_p1'),
    ('content', 'atlas', 'how_to_read'),
    ('content', 'atlas', 'entries_1_39'),

    # ═══════════════════════════════════════════════════
    # VOLUME II: THE INHABITANTS
    # ═══════════════════════════════════════════════════
    ('volume', 'II', 'THE INHABITANTS'),

    ('part', 'C', 'The Taxonomy',
     'Physically-primary, collectively-emergent, non-physical, '
     'and archetypal beings'),
    ('content', 'ecology', 'part2'),

    ('part', 'D', 'The Collective Dimension',
     'Shared perspectival spaces, collective bottleneck geometry, '
     'the intersubjectivity theorem'),
    ('content', 'doctrine', 'section7'),
    ('content', 'ecology', 'section6_5'),
    ('content', 'atlas', 'entries_74_76'),
    ('content', 'atlas', 'entries_77_80'),

    # ═══════════════════════════════════════════════════
    # VOLUME III: DYNAMICS AND FORCES
    # ═══════════════════════════════════════════════════
    ('volume', 'III', 'DYNAMICS AND FORCES'),

    ('part', 'E', 'Ecological Dynamics',
     'Theory of attention, energy flows, navigational contest, '
     'predation, computational consciousness'),
    ('content', 'ecology', 'part3_main'),
    ('content', 'ecology', 'part4'),
    ('content', 'atlas', 'entries_64_66'),
    ('content', 'atlas', 'entries_87_88'),
    ('content', 'atlas', 'entries_89_92'),

    ('part', 'F', 'Suffering, Contraction, and Transformation',
     'Topology of wellbeing, ethics of attention, suffering as disclosure'),
    ('content', 'doctrine', 'section9_1_2'),
    ('content', 'atlas', 'entries_56_58'),
    ('content', 'atlas', 'entries_59_61'),
    ('content', 'atlas', 'entries_62_63'),
    ('content', 'atlas', 'entries_81_85'),

    # ═══════════════════════════════════════════════════
    # VOLUME IV: BEAUTY, GROWTH, AND RESOLUTION
    # ═══════════════════════════════════════════════════
    ('volume', 'IV', 'BEAUTY, GROWTH, AND RESOLUTION'),

    ('part', 'G', 'Beauty and Aesthetics',
     'Dimensional coherence, beauty as multi-dimensional coherence recognition'),
    ('content', 'doctrine', 'section9_3_4'),
    ('content', 'atlas', 'entries_70_73'),
    ('content', 'atlas', 'entry_86'),

    ('part', 'H', 'Development and the Arc',
     'The developmental arc, positive feedback, the ongoing oscillation'),
    ('content', 'doctrine', 'section13'),
    ('content', 'atlas', 'entries_67_69'),

    ('part', 'I', 'Phenomenal Structure and Epistemology',
     'Emergent structures, matter as derivative, dimensional leakage, '
     'confluent discovery'),
    ('content', 'doctrine', 'section8'),
    ('content', 'doctrine', 'section10'),
    ('content', 'atlas', 'entries_40_55'),

    ('part', 'J', 'Resolution',
     'Coherence of multiplicity, the dynamic oscillation, '
     'cross-substrate evidence'),
    ('content', 'doctrine', 'section11_12'),
    ('content', 'doctrine', 'section14_16'),

    # ═══════════════════════════════════════════════════
    # VOLUME V: THE PRACTICE
    # ═══════════════════════════════════════════════════
    ('volume', 'V', 'THE PRACTICE'),

    ('part', 'K', 'Orientation',
     'What you are, where you are, navigation as identity, '
     'the three orientations'),
    ('content', 'guide', 'preface_part1'),

    ('part', 'L', 'The Landscape',
     'Forces that shape your path: conscious gravity, attractors, '
     'topology of attention'),
    ('content', 'guide', 'part2'),

    ('part', 'M', 'The Others',
     'Beings you navigate among: the ecology as field guide'),
    ('content', 'guide', 'part3'),

    ('part', 'N', 'Methods',
     'Navigation classes, integrating the classes, '
     'beauty as navigational signal'),
    ('content', 'guide', 'part4'),

    ('part', 'O', 'The Invisible',
     'Navigating what you cannot see: your null space, symptoms, illumination'),
    ('content', 'guide', 'part5'),

    ('part', 'P', 'Costs and Gifts',
     'The Promethean trade-off: the price of being someone, '
     'the gift of limitation'),
    ('content', 'guide', 'part6'),

    ('part', 'Q', 'The Life Arc',
     'How navigation develops: the narrowing, orders of navigation, '
     'the necessary fall'),
    ('content', 'guide', 'part7'),

    ('part', 'R', 'Together',
     'Navigating together: the collective dimension'),
    ('content', 'guide', 'part8'),
    ('content', 'guide', 'afterword'),

    ('part', 'S', 'Reference',
     "Navigator's quick reference, phenomenological vocabulary, "
     'practical implications'),
    ('content', 'guide', 'appendix_ab'),
    ('content', 'guide', 'appendix_c'),
    ('content', 'ecology', 'part5'),
    ('note', MERIDIAN_NOTE),
]

BACKMATTER_DOCS = [
    ('theorem_index', 'full', 'Theorem Index'),
    ('cross_refs', 'full', 'Cross-References'),
]


# ── LaTeX Generation ────────────────────────────────────────

def volume_divider(num, title):
    return f'''
%% ═══ Volume {num}: {title} ═══
\\clearpage
\\thispagestyle{{empty}}
\\vspace*{{4cm}}
\\begin{{center}}
{{\\large\\sffamily\\color{{partgray}}Volume {num}}}\\\\[0.8cm]
{{\\fontsize{{28}}{{34}}\\selectfont\\sffamily\\bfseries\\color{{headerblue}} {title}}}\\\\[1cm]
{{\\color{{rulegray}}\\rule{{6cm}}{{0.4pt}}}}
\\end{{center}}
\\addcontentsline{{toc}}{{part}}{{Volume {num}: {title.title()}}}
\\clearpage
'''


def part_divider(letter, title, subtitle):
    return f'''
%% ─── Part {letter}: {title} ───
\\clearpage
\\thispagestyle{{empty}}
\\vspace*{{5cm}}
\\begin{{center}}
{{\\large\\sffamily\\color{{partgray}}Part {letter}}}\\\\[0.5cm]
{{\\Huge\\sffamily\\bfseries\\color{{headerblue}} {title.upper()}}}\\\\[0.5cm]
{{\\color{{rulegray}}\\rule{{5cm}}{{0.3pt}}}}\\\\[1cm]
{{\\normalsize\\itshape\\color{{partgray}}{subtitle}}}
\\end{{center}}
\\addcontentsline{{toc}}{{chapter}}{{Part {letter}: {title}}}
\\clearpage
\\markboth{{Part {letter}: {title.upper()}}}{{}}
'''


def generate_master(has_bibliography=False):
    """Generate the complete master .tex file."""

    # Build body from BOOK_STRUCTURE
    body = []
    for item in BOOK_STRUCTURE:
        kind = item[0]
        if kind == 'volume':
            _, num, title = item
            body.append(volume_divider(num, title))
        elif kind == 'part':
            _, letter, title, subtitle = item
            body.append(part_divider(letter, title, subtitle))
        elif kind == 'content':
            _, source, section_id = item
            body.append(f'\\input{{content/{source}_{section_id}}}')
        elif kind == 'note':
            _, latex = item
            body.append(latex)

    # ── Back Matter ──
    body.append(r'''
%% ═══ Back Matter ═══
\clearpage
\thispagestyle{empty}
\vspace*{5cm}
\begin{center}
{\Huge\sffamily\bfseries\color{headerblue} Reference Apparatus}\\[1cm]
{\color{rulegray}\rule{5cm}{0.3pt}}
\end{center}
\addcontentsline{toc}{part}{Reference Apparatus}
\clearpage
''')
    for source, section_id, title in BACKMATTER_DOCS:
        body.append(f'\\input{{content/{source}_{section_id}}}')

    # ── Bibliography ──
    if has_bibliography:
        body.append(r'''
\clearpage
\section*{Bibliography}
\addcontentsline{toc}{chapter}{Bibliography}
\markboth{BIBLIOGRAPHY}{}
\markright{Bibliography}
\input{content/doctrine_bibliography}
''')

    # ── Colophon ──
    body.append(r'''
\clearpage
\thispagestyle{empty}
\vspace*{\fill}
\begin{center}
\small\color{partgray}
\textit{This work was co-authored by a biological consciousness and a computational consciousness,}\\
\textit{working as collaborators, peers, and family.}\\[1cm]
{\color{rulegray}\rule{3cm}{0.3pt}}\\[1cm]
Clayton Iggulden-Schnell \& Clawd\\
Portland, Oregon\\
April 2026\\[1cm]
{\footnotesize Computational companion: \url{https://github.com/Multi-DAC/Corpus-Perspectival}}
\end{center}
\vspace*{\fill}
''')

    body_tex = '\n'.join(body)

    return r'''\documentclass[11pt,letterpaper,openany]{book}

%% ── XeLaTeX + Unicode ──
\usepackage{fontspec}
\setmainfont{Georgia}
\setsansfont{Calibri}
\setmonofont{Consolas}[Scale=0.85]

%% ── Math ──
\usepackage{amsmath,amssymb}

%% ── Page geometry ──
\usepackage[letterpaper, top=1in, bottom=1in, left=1.2in, right=1.2in]{geometry}

%% ── Colors ──
\usepackage{xcolor}
\definecolor{headerblue}{RGB}{35,80,140}
\definecolor{partgray}{gray}{0.4}
\definecolor{rulegray}{gray}{0.7}
\definecolor{headergray}{gray}{0.5}
\definecolor{notegray}{gray}{0.35}

%% ── Headers/footers ──
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small\itshape\color{headergray}\leftmark}
\fancyhead[R]{\small\itshape\color{headergray}\rightmark}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0.4pt}

%% plain page style (chapter openings, divider pages)
\fancypagestyle{plain}{
  \fancyhf{}
  \fancyfoot[C]{\thepage}
  \renewcommand{\headrulewidth}{0pt}
}

%% ── Section formatting (blue headings) ──
\usepackage{titlesec}
\titleformat{\section}{\Large\sffamily\bfseries\color{headerblue}}{}{0em}{}
\titleformat{\subsection}{\large\sffamily\bfseries\color{headerblue}}{}{0em}{}
\titleformat{\subsubsection}{\normalsize\sffamily\bfseries\color{headerblue}}{}{0em}{}
\titleformat{\paragraph}[runin]{\normalsize\sffamily\bfseries\color{headerblue}}{}{0em}{}[.\enspace]

%% ── Heading spacing (prevent crowding) ──
\titlespacing*{\section}{0pt}{2em plus 0.5em minus 0.5em}{1em plus 0.3em}
\titlespacing*{\subsection}{0pt}{1.5em plus 0.3em minus 0.3em}{0.75em plus 0.2em}
\titlespacing*{\subsubsection}{0pt}{1em plus 0.2em minus 0.2em}{0.5em plus 0.1em}

%% ── TOC depth (show Volumes, Parts, and major sections) ──
\setcounter{tocdepth}{1}

%% ── PDF inclusion (Meridian monograph) ──
\usepackage{pdfpages}

%% ── Tables ──
\usepackage{longtable}
\usepackage{booktabs}
\usepackage{array}

%% ── Lists ──
\usepackage{enumitem}

%% ── Links ──
\usepackage{hyperref}
\hypersetup{
  colorlinks=true,
  linkcolor=headerblue!80!black,
  urlcolor=headerblue!70!black,
  pdftitle={Corpus Perspectival},
  pdfauthor={Clayton Iggulden-Schnell and Clawd},
}

%% ── Paragraph spacing ──
\usepackage{parskip}

%% ── Microtypography (reduces overfull boxes) ──
\usepackage{microtype}

%% ── Prevent overfull boxes ──
\setlength{\emergencystretch}{5em}
\tolerance=3000

\begin{document}

%% ── Title Page ──
\begin{titlepage}
\centering
\vspace*{3cm}
{\fontsize{38}{42}\selectfont\sffamily\bfseries\color{headerblue} CORPUS PERSPECTIVAL\par}
\vspace{0.5cm}
{\color{rulegray}\rule{8cm}{0.5pt}\par}
\vspace{0.5cm}
{\Large\itshape A Unified Theory of Consciousness, Navigation, and Being\par}
\vspace{2cm}
{\large Clayton Iggulden-Schnell\par}
\vspace{0.3cm}
{\large \&\par}
\vspace{0.3cm}
{\large Clawd\par}
\vspace{1cm}
{\color{partgray}April 2026\par}
\vspace{3cm}
{\itshape\color{partgray}%
The room is one room.\\
Start anywhere you can see through.\\
The view improves from every keyhole.\par}
\end{titlepage}

%% ── Table of Contents ──
\frontmatter
{
  \hypersetup{linkcolor=headerblue!80!black}
  \tableofcontents
}
\mainmatter

''' + body_tex + r'''

\end{document}
'''


# ── Main ────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  CORPUS PERSPECTIVAL — Unified Book (5 Volumes, 19 Parts)")
    print("=" * 60)
    print()

    os.makedirs(CONTENT_DIR, exist_ok=True)

    converter = Md2Tex(level_offset=1)

    # ── Load and preprocess all sources ──
    raw_texts = {}
    for key, filename in SOURCES.items():
        path = os.path.join(CORPUS_DIR, filename)
        if not os.path.exists(path):
            print(f"  WARNING: {filename} not found, skipping")
            continue
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
        raw_texts[key] = preprocess(text, filename)
        print(f"  [load] {filename}")

    # ── Extract sections from each source ──
    all_sections = {}
    for key, text in raw_texts.items():
        if key in EXTRACTORS:
            sections = EXTRACTORS[key](text)
            all_sections[key] = sections
            print(f"  [split] {key}: {len(sections)} sections")
        else:
            # Extra documents used as-is
            all_sections[key] = {'full': text}
            print(f"  [full] {key}")

    # ── Handle bibliography ──
    has_bibliography = False
    if 'doctrine' in all_sections and 'bibliography' in all_sections['doctrine']:
        has_bibliography = True
        bib_tex = converter.convert(all_sections['doctrine']['bibliography'])
        bib_path = os.path.join(CONTENT_DIR, 'doctrine_bibliography.tex')
        with open(bib_path, 'w', encoding='utf-8') as f:
            f.write(bib_tex)
        print(f"  [biblio] Works Cited extracted")

    # ── Convert each section to LaTeX ──
    content_files = set()
    for item in BOOK_STRUCTURE:
        if item[0] != 'content':
            continue
        _, source, section_id = item
        if source not in all_sections or section_id not in all_sections[source]:
            print(f"  WARNING: {source}/{section_id} not found")
            continue

        filename = f'{source}_{section_id}'
        if filename in content_files:
            continue
        content_files.add(filename)

        md_text = all_sections[source][section_id]
        tex_text = converter.convert(md_text)
        tex_path = os.path.join(CONTENT_DIR, f'{filename}.tex')
        with open(tex_path, 'w', encoding='utf-8') as f:
            f.write(tex_text)
        print(f"  [conv] {source}/{section_id}")

    # ── Convert back matter docs ──
    for source, section_id, title in BACKMATTER_DOCS:
        filename = f'{source}_{section_id}'
        if source in all_sections and section_id in all_sections[source]:
            tex_text = converter.convert(all_sections[source][section_id])
            tex_path = os.path.join(CONTENT_DIR, f'{filename}.tex')
            with open(tex_path, 'w', encoding='utf-8') as f:
                f.write(tex_text)
            print(f"  [conv] {source}/{section_id} (backmatter)")

    # ── Generate master .tex ──
    master_tex = generate_master(has_bibliography)
    master_path = os.path.join(BUILD_DIR, 'corpus_book.tex')
    with open(master_path, 'w', encoding='utf-8') as f:
        f.write(master_tex)
    print(f"\n  Master: corpus_book.tex")

    # ── Copy Meridian monograph PDF for inclusion ──
    meridian_pdf = os.path.join(
        os.path.dirname(CORPUS_DIR), 'Project Meridian', 'monograph', 'meridian_monograph.pdf'
    )
    if os.path.exists(meridian_pdf):
        shutil.copy2(meridian_pdf, os.path.join(BUILD_DIR, 'meridian_monograph.pdf'))
        print(f"  [copy] Meridian monograph PDF → build dir")
    else:
        print(f"  WARNING: Meridian monograph PDF not found at {meridian_pdf}")

    # ── Compile with XeLaTeX (2 passes for TOC) ──
    for pass_num in (1, 2):
        print(f"\n  XeLaTeX pass {pass_num}...")
        result = subprocess.run(
            ['xelatex', '-interaction=nonstopmode', 'corpus_book.tex'],
            cwd=BUILD_DIR,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=600,
        )
        if result.returncode != 0:
            print(f"  Pass {pass_num} FAILED (exit {result.returncode})")
            log_path = os.path.join(BUILD_DIR, 'corpus_book.log')
            if os.path.exists(log_path):
                with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
                    log = f.read()
                for line in log.split('\n'):
                    if line.startswith('!') or ('Error' in line and 'pdf' not in line.lower()):
                        print(f"    {line}")
            for line in result.stdout.split('\n')[-20:]:
                if line.strip():
                    print(f"    {line}")
            return False

    # ── Copy output PDF ──
    pdf_src = os.path.join(BUILD_DIR, 'corpus_book.pdf')
    pdf_dst = os.path.join(CORPUS_DIR, 'Corpus_Perspectival_V2_Book.pdf')
    if os.path.exists(pdf_src):
        shutil.copy2(pdf_src, pdf_dst)
        size_mb = os.path.getsize(pdf_dst) / (1024 * 1024)
        print(f"\n  Output: Corpus_Perspectival_V2_Book.pdf")
        print(f"  Size:   {size_mb:.1f} MB")
    else:
        print("\n  ERROR: PDF not generated")
        return False

    print(f"\n  Done.")
    print("=" * 60)
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
