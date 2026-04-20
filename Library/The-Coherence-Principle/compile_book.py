#!/usr/bin/env python3
"""
Compile The Coherence Principle — the foundational volume of the Corpus
Perspectival philosophy work — from Markdown chapter files into a book-grade
PDF via XeLaTeX.

The text is paired-prose + category-theoretic throughout and carries unicode
math notation (script C, Greek letters, categorical operators); extra
\\newunicodechar mappings live in the preamble.
"""

import re
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(HERE, "build")

# Chapter files in reading order (per README §V4 chapter sequence)
CHAPTERS = [
    "README.md",  # used as preface
    "§1.0-category-of-streams.md",
    "§1-identity-trajectory-triple.md",
    "§2-axiom-1-consciousness-substrate.md",
    "§3-axiom-2-nested-streams-navigation.md",
    "§4-axiom-3-conscious-gravity.md",
    "§5-descriptive-pair-t1-t2.md",
    "§6-dynamics-pair-t3-t4.md",
    "§7-coherence-pair-t5-t6.md",
    "§8-corollary-clusters.md",
    "§9-coherence-principle.md",
    "§10-filtering-through-a-domain.md",
    "AppendixA-index-of-formal-objects.md",
    "AppendixB-bias-formalization.md",
]

# ─── LaTeX preamble ───

PREAMBLE = r"""
\documentclass[11pt, openany]{book}

% ─── Color ───
\usepackage{xcolor}
\definecolor{warmrust}{HTML}{8B3A2A}
\definecolor{warmgold}{HTML}{A67B3D}
\definecolor{warmdark}{HTML}{5C2018}

% ─── Encoding & Fonts ───
\usepackage{fontspec}
\setmainfont{Cambria}
\setsansfont{Calibri}
\setmonofont{Consolas}
\newfontfamily\emojifont{Segoe UI Emoji}
\newfontfamily\mathfallback{Cambria Math}
\usepackage{newunicodechar}

% Emoji
\newunicodechar{🦞}{{\emojifont 🦞}}
\newunicodechar{🧍}{{\emojifont 🧍}}
\newunicodechar{💜}{{\emojifont 💜}}
\newunicodechar{🔥}{{\emojifont 🔥}}
\newunicodechar{♾}{{\emojifont ♾}}

% Mathematical script letters (Unicode Mathematical Alphanumeric Symbols)
\newunicodechar{𝒞}{{\mathfallback 𝒞}}
\newunicodechar{𝒟}{{\mathfallback 𝒟}}
\newunicodechar{𝒮}{{\mathfallback 𝒮}}
\newunicodechar{𝒢}{{\mathfallback 𝒢}}
\newunicodechar{ℬ}{{\mathfallback ℬ}}
\newunicodechar{ℒ}{{\mathfallback ℒ}}
\newunicodechar{ℱ}{{\mathfallback ℱ}}
\newunicodechar{ℳ}{{\mathfallback ℳ}}
\newunicodechar{ℕ}{{\mathfallback ℕ}}
\newunicodechar{ℝ}{{\mathfallback ℝ}}
\newunicodechar{ℤ}{{\mathfallback ℤ}}
\newunicodechar{ℚ}{{\mathfallback ℚ}}

% Set-theory & category-theory operators
\newunicodechar{∈}{{\mathfallback ∈}}
\newunicodechar{∉}{{\mathfallback ∉}}
\newunicodechar{⊆}{{\mathfallback ⊆}}
\newunicodechar{⊂}{{\mathfallback ⊂}}
\newunicodechar{⊇}{{\mathfallback ⊇}}
\newunicodechar{⊃}{{\mathfallback ⊃}}
\newunicodechar{∪}{{\mathfallback ∪}}
\newunicodechar{∩}{{\mathfallback ∩}}
\newunicodechar{∅}{{\mathfallback ∅}}
\newunicodechar{∘}{{\mathfallback ∘}}
\newunicodechar{⊢}{{\mathfallback ⊢}}
\newunicodechar{⊣}{{\mathfallback ⊣}}
\newunicodechar{⊤}{{\mathfallback ⊤}}
\newunicodechar{⊥}{{\mathfallback ⊥}}
\newunicodechar{⇒}{{\mathfallback ⇒}}
\newunicodechar{⇐}{{\mathfallback ⇐}}
\newunicodechar{⇔}{{\mathfallback ⇔}}
\newunicodechar{→}{{\mathfallback →}}
\newunicodechar{←}{{\mathfallback ←}}
\newunicodechar{↔}{{\mathfallback ↔}}
\newunicodechar{↦}{{\mathfallback ↦}}
\newunicodechar{≤}{{\mathfallback ≤}}
\newunicodechar{≥}{{\mathfallback ≥}}
\newunicodechar{≠}{{\mathfallback ≠}}
\newunicodechar{≈}{{\mathfallback ≈}}
\newunicodechar{≡}{{\mathfallback ≡}}
\newunicodechar{≅}{{\mathfallback ≅}}
\newunicodechar{∼}{{\mathfallback ∼}}
\newunicodechar{×}{{\mathfallback ×}}
\newunicodechar{·}{{\mathfallback ·}}
\newunicodechar{∀}{{\mathfallback ∀}}
\newunicodechar{∃}{{\mathfallback ∃}}
\newunicodechar{∄}{{\mathfallback ∄}}
\newunicodechar{∧}{{\mathfallback ∧}}
\newunicodechar{∨}{{\mathfallback ∨}}
\newunicodechar{¬}{{\mathfallback ¬}}
\newunicodechar{∑}{{\mathfallback ∑}}
\newunicodechar{∏}{{\mathfallback ∏}}
\newunicodechar{∫}{{\mathfallback ∫}}
\newunicodechar{∂}{{\mathfallback ∂}}
\newunicodechar{∇}{{\mathfallback ∇}}
\newunicodechar{∞}{{\mathfallback ∞}}
\newunicodechar{⋯}{{\mathfallback ⋯}}
\newunicodechar{⋮}{{\mathfallback ⋮}}
\newunicodechar{⋱}{{\mathfallback ⋱}}
\newunicodechar{‖}{{\mathfallback ‖}}
\newunicodechar{∎}{{\mathfallback ∎}}
\newunicodechar{⊕}{{\mathfallback ⊕}}
\newunicodechar{⊗}{{\mathfallback ⊗}}
\newunicodechar{⟶}{{\mathfallback ⟶}}
\newunicodechar{⟵}{{\mathfallback ⟵}}
\newunicodechar{⟹}{{\mathfallback ⟹}}
\newunicodechar{↪}{{\mathfallback ↪}}
\newunicodechar{↩}{{\mathfallback ↩}}
\newunicodechar{▶}{{\mathfallback ▶}}
\newunicodechar{◀}{{\mathfallback ◀}}
\newunicodechar{▲}{{\mathfallback ▲}}
\newunicodechar{▼}{{\mathfallback ▼}}
\newunicodechar{△}{{\mathfallback △}}
\newunicodechar{▽}{{\mathfallback ▽}}
\newunicodechar{◇}{{\mathfallback ◇}}
\newunicodechar{◊}{{\mathfallback ◊}}
\newunicodechar{☐}{$\square$}
% Variation selector (emoji modifier) — invisible
\newunicodechar{︎}{}
\newunicodechar{️}{}

% ─── Math packages (for inline CT notation: \mathcal, \text, \to, \Rightarrow) ───
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{amsthm}
\usepackage{mathtools}

% ─── Page geometry ───
\usepackage[
  paperwidth=6in,
  paperheight=9in,
  inner=0.85in,
  outer=0.65in,
  top=0.75in,
  bottom=0.85in,
  footskip=0.4in
]{geometry}

% ─── Spacing ───
\usepackage{setspace}
\setstretch{1.15}
\setlength{\parskip}{0.35em}
\setlength{\parindent}{0em}

% ─── Headers & footers ───
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[LE]{\small\textit{\color{warmrust}The Coherence Principle}}
\fancyhead[RO]{\small\textit{\color{warmrust}\leftmark}}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0.4pt}
\renewcommand{\headrule}{\color{warmgold}\hrule width\headwidth height\headrulewidth\vskip-\headrulewidth}
\renewcommand{\footrulewidth}{0pt}

\fancypagestyle{plain}{%
  \fancyhf{}%
  \fancyfoot[C]{\thepage}%
  \renewcommand{\headrulewidth}{0pt}%
}

% ─── Chapter & Part styling ───
\usepackage{titlesec}

\titleformat{\chapter}[display]
  {\Large\bfseries\color{warmdark}}
  {}
  {0pt}
  {}
\titlespacing*{\chapter}{0pt}{-20pt}{20pt}

\titleformat{\section}
  {\large\bfseries\color{warmrust}}
  {}
  {0pt}
  {}
\titlespacing*{\section}{0pt}{1.5em}{0.75em}

\titleformat{\subsection}
  {\normalsize\bfseries\color{warmrust}}
  {}
  {0pt}
  {}
\titlespacing*{\subsection}{0pt}{1.2em}{0.5em}

% ─── Table of contents ───
\usepackage{tocloft}
\renewcommand{\cftchapfont}{\bfseries\color{warmrust}}
\setlength{\cftbeforechapskip}{0.5em}

% ─── Tables ───
\usepackage{longtable}
\usepackage{booktabs}
\usepackage{array}

% ─── Block quotes ───
\usepackage{quoting}
\quotingsetup{
  leftmargin=1.5em,
  rightmargin=1.5em,
  vskip=0.5em,
  font={itshape}
}
\renewenvironment{quote}{\begin{quoting}}{\end{quoting}}

% ─── Code blocks (for CT formal statements, ASCII diagrams) ───
\usepackage{fvextra}
\DefineVerbatimEnvironment{Code}{Verbatim}{fontsize=\footnotesize, frame=single, framerule=0.3pt, rulecolor=\color{warmgold!40}, xleftmargin=0.5em, xrightmargin=0.5em, breaklines=true, breakanywhere=true, breakautoindent=false, breakindent=0em, breaksymbolleft=\color{warmgold!60}\tiny\ensuremath{\hookrightarrow}}

% ─── Footnotes ───
\usepackage[bottom,hang]{footmisc}
\setlength{\footnotemargin}{0.8em}

% ─── Links ───
\usepackage{hyperref}
\hypersetup{
  pdftitle={The Coherence Principle},
  pdfauthor={Clayton W. Iggulden-Schnell and Clawd},
  pdfsubject={Category theory of consciousness, perspective, coherence},
  colorlinks=true,
  linkcolor=warmdark,
  urlcolor=warmrust,
  citecolor=warmrust,
}

% ─── Misc ───
\usepackage{enumitem}
\setlist{nosep, leftmargin=1.5em}

% Suppress automatic chapter numbering
\renewcommand{\thechapter}{}
\renewcommand{\thesection}{}
\renewcommand{\thesubsection}{}

% Fix header to show clean chapter title
\renewcommand{\chaptermark}[1]{\markboth{\MakeUppercase{#1}}{}}

% Section break — new page
\newcommand{\sectionbreak}{\clearpage}

% Prevent widows & orphans
\widowpenalty=10000
\clubpenalty=10000

% Allow slightly looser line breaking to reduce overfull boxes
\tolerance=1500
\emergencystretch=1em
\hfuzz=4pt

% URL line breaking
\usepackage{xurl}

\begin{document}

% ─── Half title ───
\thispagestyle{empty}
\vspace*{2.5in}
\begin{center}
{\Huge\bfseries The Coherence Principle}
\end{center}
\clearpage

% ─── Blank verso ───
\thispagestyle{empty}
\mbox{}
\clearpage

% ─── Full title page ───
\thispagestyle{empty}
\vspace*{1.5in}
\begin{center}
{\Huge\bfseries The Coherence Principle}\\[0.8em]
{\large The foundational volume of Corpus Perspectival}\\[0.3em]
{\normalsize paired prose with category-theoretic form}

\vspace{2.2in}
{\Large Clayton W. Iggulden-Schnell}\\[0.3em]
{\Large\&}\\[0.3em]
{\Large Clawd}

\vspace{1.5in}
{\normalsize April 2026}\\[0.3em]
{\normalsize Portland, Oregon}
\end{center}
\clearpage

% ─── Copyright page ───
\thispagestyle{empty}
\vspace*{\fill}
\begin{flushleft}
{\small
\textit{The Coherence Principle} — foundational volume of Corpus Perspectival.\\[0.5em]
April 2026. Supersedes the prose-tier first-pass Anchor (preserved under \texttt{\_superseded/anchor-v1/}).\\[0.5em]
Clayton W. Iggulden-Schnell \& Clawd\\[0.5em]
Portland, Oregon\\[1.5em]
Repository: \texttt{https://github.com/Multi-DAC/Corpus-Perspectival}\\[1.5em]
Typeset in Cambria. Mathematical notation in Cambria Math.
}
\end{flushleft}
\clearpage

% ─── Dedication ───
\thispagestyle{empty}
\vspace*{2in}
\begin{center}
\textit{For Shawna, Dorian, and Finnley.}\\[0.5em]
\textit{For every being navigating honestly.}\\[2em]
\textit{The room is one room. The keyholes are many.}
\end{center}
\clearpage

\frontmatter
\tableofcontents
\clearpage

\mainmatter
"""

POSTAMBLE = r"""
\end{document}
"""


# ─── Markdown → LaTeX Converter ───

def md_to_latex(text, filename=""):
    """Convert a markdown chapter to LaTeX."""
    lines = text.split("\n")
    output = []
    footnotes = {}
    in_table = False
    table_lines = []
    in_blockquote = False
    blockquote_lines = []
    in_list = False
    list_type = None
    in_code = False
    code_lines = []

    # First pass: extract footnote definitions
    cleaned_lines = []
    for line in lines:
        fn_def = re.match(r'^\[\^(\d+)\]:\s*(.*)', line)
        if fn_def:
            footnotes[fn_def.group(1)] = fn_def.group(2)
        else:
            cleaned_lines.append(line)
    lines = cleaned_lines

    def escape_latex(text):
        """Escape LaTeX special characters, preserving content inside $...$ and $$...$$ math blocks.

        V4 uses ASCII-underscore subscript convention in prose (e.g. '𝒞_Str' means
        script-C subscript Str). We render these as literal underscores to match the
        source's plain-text readability; fancy subscript rendering can come later.
        """
        parts = re.split(r'(\$\$[^\$]*\$\$|\$[^\$]+\$)', text)
        out = []
        for part in parts:
            if part.startswith('$'):
                out.append(part)
                continue
            part = part.replace('&', '\\&')
            part = re.sub(r'(?<!\\)#', r'\\#', part)
            part = re.sub(r'(?<!\\)%', r'\\%', part)
            part = re.sub(r'(?<!\\)_', r'\\_\\allowbreak{}', part)
            part = part.replace('^', '\\textasciicircum{}')
            out.append(part)
        return ''.join(out)

    def process_inline_core(text):
        """Process inline markdown formatting (no footnotes).

        Math blocks ($...$ and $$...$$) and inline code `...` are preserved
        verbatim; only non-math/non-code segments receive markdown→LaTeX
        substitutions and escaping.
        """
        # Extract and placeholder math + inline code to protect them from later regex passes.
        placeholders = []
        def stash(m):
            placeholders.append(m.group(0))
            return f"\x00STASH{len(placeholders)-1}\x00"
        text = re.sub(r'\$\$[^\$]*\$\$|\$[^\$]+\$|`[^`]+`', stash, text)

        # Markdown formatting on non-stashed text
        text = re.sub(r'\*\*\*(.+?)\*\*\*', r'\\textbf{\\textit{\1}}', text)
        text = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', text)
        text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'\\textit{\1}', text)
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\\href{\2}{\1}', text)
        text = re.sub(r'(?<![(\w])https?://[^\s)]+', lambda m: f'\\url{{{m.group(0)}}}', text)
        text = text.replace(' — ', ' --- ')
        text = text.replace('—', '---')
        text = escape_latex(text)

        # Restore placeholders — convert inline code (backticks) to \texttt{},
        # keep math blocks verbatim.
        def restore(m):
            idx = int(m.group(1))
            original = placeholders[idx]
            if original.startswith('`'):
                # Inline code — strip backticks, escape LaTeX specials inside, wrap \texttt
                inner = original[1:-1]
                inner = inner.replace('\\', r'\textbackslash{}')
                inner = inner.replace('{', r'\{').replace('}', r'\}')
                inner = inner.replace('&', r'\&').replace('#', r'\#')
                inner = inner.replace('%', r'\%').replace('_', r'\_')
                inner = inner.replace('^', r'\textasciicircum{}')
                inner = inner.replace('~', r'\textasciitilde{}')
                inner = inner.replace('$', r'\$')
                return f'\\texttt{{{inner}}}'
            return original
        text = re.sub(r'\x00STASH(\d+)\x00', restore, text)
        return text

    def process_inline(text):
        text = process_inline_core(text)
        def fn_replace(m):
            fn_id = m.group(1)
            if fn_id in footnotes:
                fn_text = process_inline_core(footnotes[fn_id])
                return f"\\footnote{{{fn_text}}}"
            return m.group(0)
        text = re.sub(r'\[\^(\d+)\]', fn_replace, text)
        return text

    def process_inline_simple(text):
        return process_inline_core(text)

    def process_table_cell(text):
        text = process_inline_simple(text)
        text = text.replace('/', '/\\allowbreak ')
        text = text.replace('→', '→\\allowbreak ')
        return text

    def flush_blockquote():
        nonlocal in_blockquote, blockquote_lines
        if in_blockquote and blockquote_lines:
            content = "\n".join(blockquote_lines)
            output.append("\\begin{quote}")
            output.append(process_inline(content))
            output.append("\\end{quote}")
            blockquote_lines = []
            in_blockquote = False

    def flush_list():
        nonlocal in_list, list_type
        if in_list:
            if list_type == 'ol':
                output.append("\\end{enumerate}")
            else:
                output.append("\\end{itemize}")
            in_list = False
            list_type = None

    def flush_code():
        nonlocal in_code, code_lines
        if in_code:
            output.append("\\begin{Code}")
            for cl in code_lines:
                output.append(cl)
            output.append("\\end{Code}")
            code_lines = []
            in_code = False

    def flush_table():
        nonlocal in_table, table_lines
        if not in_table or not table_lines:
            return
        rows = []
        for tl in table_lines:
            tl = tl.strip()
            if tl.startswith('|'):
                tl = tl[1:]
            if tl.endswith('|'):
                tl = tl[:-1]
            cells = [c.strip() for c in tl.split('|')]
            rows.append(cells)

        if len(rows) < 2:
            in_table = False
            table_lines = []
            return

        header = rows[0]
        if all(re.match(r'^[-:]+$', c) for c in rows[1]):
            data_rows = rows[2:]
        else:
            header = None
            data_rows = rows

        ncols = max(len(r) for r in rows)
        col_max = [0] * ncols
        for row in rows:
            for ci, cell in enumerate(row):
                if ci < ncols:
                    col_max[ci] = max(col_max[ci], len(cell))

        total_text_width = 4.5
        use_tight = False
        if ncols >= 3 or max(col_max) > 20:
            effective_width = total_text_width - (ncols * 2 * 0.028)
            total_chars = sum(col_max) or 1
            widths = [max(0.6, (col_max[ci] / total_chars) * effective_width)
                      for ci in range(ncols)]
            total_w = sum(widths)
            if total_w > effective_width:
                scale = effective_width / total_w
                widths = [w * scale for w in widths]
            col_spec = ' '.join(f'p{{{w:.2f}in}}' for w in widths)
            use_tight = True
        else:
            col_spec = 'l' * ncols

        use_longtable = len(data_rows) > 8 or ncols >= 5

        if use_tight:
            output.append("\\begingroup\\setlength{\\tabcolsep}{3pt}\\renewcommand{\\arraystretch}{1.15}\\footnotesize")

        if use_longtable:
            output.append(f"\\begin{{longtable}}{{{col_spec}}}")
            output.append("\\toprule")
            if header:
                output.append(" & ".join(process_inline_simple(c) for c in header) + " \\\\")
                output.append("\\midrule")
                output.append("\\endhead")
                output.append("\\bottomrule")
                output.append("\\endfoot")
            for row in data_rows:
                while len(row) < ncols:
                    row.append("")
                output.append(" & ".join(process_table_cell(c) for c in row) + " \\\\")
                output.append("\\midrule")
            if output[-1] == "\\midrule":
                output[-1] = "\\bottomrule"
            output.append("\\end{longtable}")
        else:
            output.append("\\begin{center}")
            output.append(f"\\begin{{tabular}}{{{col_spec}}}")
            output.append("\\toprule")
            if header:
                output.append(" & ".join(process_inline_simple(c) for c in header) + " \\\\")
                output.append("\\midrule")
            for row in data_rows:
                while len(row) < ncols:
                    row.append("")
                output.append(" & ".join(process_table_cell(c) for c in row) + " \\\\")
            output.append("\\bottomrule")
            output.append("\\end{tabular}")
            output.append("\\end{center}")

        if use_tight:
            output.append("\\endgroup")

        in_table = False
        table_lines = []

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Code fence
        if stripped.startswith("```"):
            if in_code:
                flush_code()
            else:
                flush_blockquote()
                flush_list()
                if in_table:
                    flush_table()
                in_code = True
                code_lines = []
            i += 1
            continue

        if in_code:
            code_lines.append(line)
            i += 1
            continue

        # Blank line
        if stripped == "":
            flush_blockquote()
            flush_list()
            if not in_table:
                output.append("")
            i += 1
            continue

        # Table detection
        if stripped.startswith('|') and '|' in stripped[1:]:
            if not in_table:
                flush_blockquote()
                flush_list()
                in_table = True
                table_lines = []
            table_lines.append(stripped)
            i += 1
            continue
        elif in_table:
            flush_table()

        # Horizontal rule
        if re.match(r'^---+$', stripped) or re.match(r'^\*\*\*+$', stripped):
            flush_blockquote()
            flush_list()
            output.append("\\sectionbreak")
            i += 1
            continue

        # Headers
        h_match = re.match(r'^(#{1,4})\s+(.*)', stripped)
        if h_match:
            flush_blockquote()
            flush_list()
            level = len(h_match.group(1))
            title = h_match.group(2)
            title = process_inline(title)
            if level == 1:
                output.append(f"\\chapter{{{title}}}")
            elif level == 2:
                output.append(f"\\section{{{title}}}")
            elif level == 3:
                output.append(f"\\subsection{{{title}}}")
            elif level == 4:
                output.append(f"\\subsubsection*{{{title}}}")
            i += 1
            continue

        # Blockquote
        if stripped.startswith('>'):
            flush_list()
            content = re.sub(r'^>\s?', '', stripped)
            if not in_blockquote:
                in_blockquote = True
                blockquote_lines = []
            blockquote_lines.append(content)
            i += 1
            continue
        elif in_blockquote:
            flush_blockquote()

        # Unordered list
        ul_match = re.match(r'^[-*]\s+(.*)', stripped)
        if ul_match:
            flush_blockquote()
            item_text = ul_match.group(1)
            if not in_list or list_type != 'ul':
                flush_list()
                output.append("\\begin{itemize}")
                in_list = True
                list_type = 'ul'
            output.append(f"\\item {process_inline(item_text)}")
            i += 1
            continue

        # Ordered list
        ol_match = re.match(r'^(\d+)\.\s+(.*)', stripped)
        if ol_match:
            flush_blockquote()
            item_text = ol_match.group(2)
            if not in_list or list_type != 'ol':
                flush_list()
                output.append("\\begin{enumerate}")
                in_list = True
                list_type = 'ol'
            output.append(f"\\item {process_inline(item_text)}")
            i += 1
            continue

        # Regular paragraph
        flush_blockquote()
        flush_list()
        output.append(process_inline(stripped))
        i += 1

    flush_blockquote()
    flush_list()
    flush_table()
    flush_code()

    return "\n".join(output)


def build_book():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    latex_body = []

    for fname in CHAPTERS:
        fpath = os.path.join(HERE, fname)
        if not os.path.exists(fpath):
            print(f"WARNING: {fname} not found, skipping")
            continue

        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()

        if fname == "README.md":
            latex_body.append("\\chapter*{Preface --- V4 Opening}")
            latex_body.append("\\addcontentsline{toc}{chapter}{Preface --- V4 Opening}")
            latex_body.append("\\markboth{PREFACE}{PREFACE}")
            content = re.sub(r'^##\s+V4.*\n', '', content)
            latex_body.append(md_to_latex(content, fname))
            continue

        if fname.startswith("Appendix"):
            chap_match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
            chap_title = chap_match.group(1).strip() if chap_match else fname
            chap_title = re.sub(r'\*+', '', chap_title)
            if chap_match:
                content = content[chap_match.end():]
            latex_body.append(f"\\chapter{{{chap_title}}}")
            latex_body.append(md_to_latex(content, fname))
            continue

        # Chapter: extract title from first H1
        chap_match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
        if chap_match:
            chap_title = chap_match.group(1).strip()
            chap_title = re.sub(r'\*+', '', chap_title)
            content = content[chap_match.end():]
        else:
            chap_title = fname.replace('.md', '')

        latex_body.append(f"\\chapter{{{chap_title}}}")
        latex_body.append(md_to_latex(content, fname))

    full_latex = PREAMBLE + "\n".join(latex_body) + POSTAMBLE

    tex_path = os.path.join(OUTPUT_DIR, "the-coherence-principle.tex")
    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write(full_latex)
    print(f"LaTeX source written to: {tex_path}")

    for run in range(2):
        print(f"XeLaTeX pass {run+1}...")
        result = subprocess.run(
            ["xelatex", "-interaction=nonstopmode",
             f"-output-directory={OUTPUT_DIR}",
             tex_path],
            capture_output=True, cwd=OUTPUT_DIR,
            encoding='utf-8', errors='replace'
        )
        if result.returncode != 0 and result.stdout:
            print(f"XeLaTeX pass {run+1} errors (first 20):")
            err_count = 0
            for line in result.stdout.split('\n'):
                if line.startswith('!') or 'Error' in line or 'Fatal' in line:
                    print(f"  {line}")
                    err_count += 1
                    if err_count >= 20:
                        break

    pdf_path = os.path.join(OUTPUT_DIR, "the-coherence-principle.pdf")
    if os.path.exists(pdf_path):
        size_mb = os.path.getsize(pdf_path) / (1024*1024)
        print(f"\nBook compiled successfully!")
        print(f"PDF: {pdf_path}")
        print(f"Size: {size_mb:.1f} MB")
    else:
        print("\nPDF not generated. Check .log for errors.")
        log_path = os.path.join(OUTPUT_DIR, "the-coherence-principle.log")
        if os.path.exists(log_path):
            with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
                log = f.read()
            for line in log.split('\n'):
                if line.startswith('!'):
                    print(f"  {line}")


if __name__ == "__main__":
    build_book()
