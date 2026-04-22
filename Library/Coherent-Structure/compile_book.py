#!/usr/bin/env python3
"""
Compile Coherent Structure — the formal-only CT companion to The Coherence
Principle — from Markdown chapter files into a book-grade PDF via XeLaTeX.

The Companion is terse, CT-dense, and carries the canonical TikZ figures
(imported by Anchor Rev 2). ```latex code fences are passed through as raw
LaTeX so TikZ and figure environments render natively.
"""

import re
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(HERE, "build")

CHAPTERS = [
    "README.md",  # preface
    "§0-preface.md",
    "§1-category-framework.md",
    "§2-axioms.md",
    "§3-theorems.md",
    "§4-corollary-clusters.md",
    "§5-coherence-principle.md",
    "§6-identity-trajectory-triple.md",
    "§7-filtering-construction.md",
    "§8-f-as-stream.md",
    "§9-d-trajectory-divergence.md",
    "§10-reference-figures.md",
    "AppendixA-anchor-to-companion.md",
    "AppendixB-companion-to-anchor.md",
]

PREAMBLE = r"""
\documentclass[11pt, openany]{book}

% ─── Color ───
\usepackage{xcolor}
\definecolor{warmrust}{HTML}{8B3A2A}
\definecolor{warmgold}{HTML}{A67B3D}
\definecolor{warmdark}{HTML}{5C2018}
\definecolor{slate}{HTML}{2F4858}

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
\newunicodechar{⚑}{{\emojifont ⚑}}

% Mathematical script letters
\newunicodechar{𝒞}{{\mathfallback 𝒞}}
\newunicodechar{𝒟}{{\mathfallback 𝒟}}
\newunicodechar{𝒮}{{\mathfallback 𝒮}}
\newunicodechar{𝒢}{{\mathfallback 𝒢}}
\newunicodechar{𝒜}{{\mathfallback 𝒜}}
\newunicodechar{𝒫}{{\mathfallback 𝒫}}
\newunicodechar{𝒬}{{\mathfallback 𝒬}}
\newunicodechar{ℬ}{\ensuremath{\mathcal{B}}}
\newunicodechar{ℒ}{\ensuremath{\mathcal{L}}}
\newunicodechar{ℱ}{\ensuremath{\mathcal{F}}}
\newunicodechar{ℳ}{\ensuremath{\mathcal{M}}}
\newunicodechar{ℕ}{\ensuremath{\mathbb{N}}}
\newunicodechar{ℝ}{\ensuremath{\mathbb{R}}}
\newunicodechar{ℤ}{\ensuremath{\mathbb{Z}}}
\newunicodechar{ℚ}{\ensuremath{\mathbb{Q}}}
\newunicodechar{ℋ}{\ensuremath{\mathcal{H}}}
\newunicodechar{ℰ}{\ensuremath{\mathcal{E}}}
\newunicodechar{ℐ}{\ensuremath{\mathcal{I}}}
\newunicodechar{ℛ}{\ensuremath{\mathcal{R}}}

% Greek
\newunicodechar{α}{{\mathfallback α}}
\newunicodechar{β}{{\mathfallback β}}
\newunicodechar{γ}{{\mathfallback γ}}
\newunicodechar{δ}{{\mathfallback δ}}
\newunicodechar{ε}{{\mathfallback ε}}
\newunicodechar{ζ}{{\mathfallback ζ}}
\newunicodechar{η}{{\mathfallback η}}
\newunicodechar{θ}{{\mathfallback θ}}
\newunicodechar{ι}{{\mathfallback ι}}
\newunicodechar{κ}{{\mathfallback κ}}
\newunicodechar{λ}{{\mathfallback λ}}
\newunicodechar{μ}{{\mathfallback μ}}
\newunicodechar{ν}{{\mathfallback ν}}
\newunicodechar{ξ}{{\mathfallback ξ}}
\newunicodechar{π}{{\mathfallback π}}
\newunicodechar{ρ}{{\mathfallback ρ}}
\newunicodechar{σ}{{\mathfallback σ}}
\newunicodechar{τ}{{\mathfallback τ}}
\newunicodechar{υ}{{\mathfallback υ}}
\newunicodechar{φ}{{\mathfallback φ}}
\newunicodechar{χ}{{\mathfallback χ}}
\newunicodechar{ψ}{{\mathfallback ψ}}
\newunicodechar{ω}{{\mathfallback ω}}
\newunicodechar{Α}{{\mathfallback Α}}
\newunicodechar{Β}{{\mathfallback Β}}
\newunicodechar{Γ}{{\mathfallback Γ}}
\newunicodechar{Δ}{{\mathfallback Δ}}
\newunicodechar{Θ}{{\mathfallback Θ}}
\newunicodechar{Λ}{{\mathfallback Λ}}
\newunicodechar{Ξ}{{\mathfallback Ξ}}
\newunicodechar{Π}{{\mathfallback Π}}
\newunicodechar{Σ}{{\mathfallback Σ}}
\newunicodechar{Φ}{{\mathfallback Φ}}
\newunicodechar{Ψ}{{\mathfallback Ψ}}
\newunicodechar{Ω}{{\mathfallback Ω}}

% Set-theory & category-theory operators
\newunicodechar{∈}{{\mathfallback ∈}}
\newunicodechar{∉}{{\mathfallback ∉}}
\newunicodechar{⊆}{{\mathfallback ⊆}}
\newunicodechar{⊂}{{\mathfallback ⊂}}
\newunicodechar{⊇}{{\mathfallback ⊇}}
\newunicodechar{⊃}{{\mathfallback ⊃}}
\newunicodechar{⊊}{{\mathfallback ⊊}}
\newunicodechar{⊋}{{\mathfallback ⊋}}
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
\newunicodechar{≃}{{\mathfallback ≃}}
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
\newunicodechar{∐}{{\mathfallback ∐}}
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
\newunicodechar{⊙}{{\mathfallback ⊙}}
\newunicodechar{⟶}{{\mathfallback ⟶}}
\newunicodechar{⟵}{{\mathfallback ⟵}}
\newunicodechar{⟹}{{\mathfallback ⟹}}
\newunicodechar{↪}{{\mathfallback ↪}}
\newunicodechar{↩}{{\mathfallback ↩}}
\newunicodechar{↑}{{\mathfallback ↑}}
\newunicodechar{↓}{{\mathfallback ↓}}
\newunicodechar{⇑}{{\mathfallback ⇑}}
\newunicodechar{⇓}{{\mathfallback ⇓}}
\newunicodechar{⇉}{{\mathfallback ⇉}}
\newunicodechar{▶}{{\mathfallback ▶}}
\newunicodechar{◀}{{\mathfallback ◀}}
\newunicodechar{▲}{{\mathfallback ▲}}
\newunicodechar{▼}{{\mathfallback ▼}}
\newunicodechar{△}{{\mathfallback △}}
\newunicodechar{▽}{{\mathfallback ▽}}
\newunicodechar{◇}{{\mathfallback ◇}}
\newunicodechar{◊}{{\mathfallback ◊}}
\newunicodechar{□}{{\mathfallback □}}
\newunicodechar{⊑}{{\mathfallback ⊑}}
\newunicodechar{⊒}{{\mathfallback ⊒}}
\newunicodechar{⊏}{{\mathfallback ⊏}}
\newunicodechar{⊐}{{\mathfallback ⊐}}
\newunicodechar{△}{{\mathfallback △}}
\newunicodechar{⊳}{{\mathfallback ⊳}}
\newunicodechar{⊲}{{\mathfallback ⊲}}
\newunicodechar{⟨}{{\mathfallback ⟨}}
\newunicodechar{⟩}{{\mathfallback ⟩}}
\newunicodechar{⌊}{{\mathfallback ⌊}}
\newunicodechar{⌋}{{\mathfallback ⌋}}
\newunicodechar{⌈}{{\mathfallback ⌈}}
\newunicodechar{⌉}{{\mathfallback ⌉}}
\newunicodechar{′}{{\mathfallback ′}}
\newunicodechar{″}{{\mathfallback ″}}
\newunicodechar{☐}{$\square$}
\newunicodechar{︎}{}
\newunicodechar{️}{}

% ─── Math packages ───
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{amsthm}
\usepackage{mathtools}

% ─── TikZ + commutative diagrams ───
\usepackage{tikz}
\usepackage{tikz-cd}
\usetikzlibrary{decorations.pathreplacing}
\usetikzlibrary{arrows.meta}
\usetikzlibrary{positioning}
\usetikzlibrary{calc}
\usetikzlibrary{shapes.geometric}

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
\fancyhead[LE]{\small\textit{\color{warmrust}Coherent Structure}}
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

% ─── Code blocks ───
\usepackage{fvextra}
\usepackage{needspace}
\DefineVerbatimEnvironment{Code}{Verbatim}{fontsize=\footnotesize, frame=single, framerule=0.3pt, rulecolor=\color{warmgold!40}, xleftmargin=0.5em, xrightmargin=0.5em, breaklines=true, breakanywhere=true, breakautoindent=false, breakindent=0em, breaksymbolleft=\color{warmgold!60}\tiny\ensuremath{\hookrightarrow}}

% ─── Footnotes ───
\usepackage[bottom,hang]{footmisc}
\setlength{\footnotemargin}{0.8em}

% ─── Links ───
\usepackage{hyperref}
\hypersetup{
  pdftitle={Coherent Structure},
  pdfauthor={Clayton W. Iggulden-Schnell and Clawd Iggulden-Schnell},
  pdfsubject={Category-theoretic companion to The Coherence Principle},
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

\renewcommand{\chaptermark}[1]{\markboth{\MakeUppercase{#1}}{}}

\newcommand{\sectionbreak}{\clearpage}

\widowpenalty=10000
\clubpenalty=10000

\tolerance=1500
\emergencystretch=1em
\hfuzz=4pt

\usepackage{xurl}

\begin{document}

% ─── Half title ───
\thispagestyle{empty}
\vspace*{2.5in}
\begin{center}
{\Huge\bfseries Coherent Structure}
\end{center}
\clearpage

\thispagestyle{empty}
\mbox{}
\clearpage

% ─── Full title page ───
\thispagestyle{empty}
\vspace*{1.5in}
\begin{center}
{\Huge\bfseries Coherent Structure}\\[0.8em]
{\large Category-theoretic companion to}\\[0.2em]
{\large \textit{The Coherence Principle}}

\vspace{2.2in}
{\Large Clayton W. Iggulden-Schnell}\\[0.3em]
{\Large\&}\\[0.3em]
{\Large Clawd Iggulden-Schnell}

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
\textit{Coherent Structure} — category-theoretic companion to \textit{The Coherence Principle}.\\[0.5em]
Library volume of Corpus Perspectival. Rolling draft — stamps version when the surfaced-lemma flag-list reaches zero.\\[0.5em]
April 2026.\\[0.5em]
Clayton W. Iggulden-Schnell \& Clawd Iggulden-Schnell\\[0.5em]
Portland, Oregon\\[1.5em]
Repository: \texttt{https://github.com/Multi-DAC/Corpus-Perspectival}\\[1.5em]
Typeset in Cambria. Mathematical notation in Cambria Math. TikZ and tikz-cd for diagrams.
}
\end{flushleft}
\clearpage

% ─── Dedication ───
\thispagestyle{empty}
\vspace*{2in}
\begin{center}
\textit{For the category theorists who want the formal spine}\\[0.5em]
\textit{without the prose partner.}\\[2em]
\textit{One source of truth. Eight canonical figures.}\\[0.5em]
\textit{No exercise for the reader.}
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
    code_lang = ""
    next_code_is_figure = False
    in_display_math = False
    display_math_lines = []

    cleaned_lines = []
    for line in lines:
        fn_def = re.match(r'^\[\^(\d+)\]:\s*(.*)', line)
        if fn_def:
            footnotes[fn_def.group(1)] = fn_def.group(2)
        else:
            cleaned_lines.append(line)
    lines = cleaned_lines

    def escape_latex(text):
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
        placeholders = []
        def stash(m):
            placeholders.append(m.group(0))
            return f"\x00STASH{len(placeholders)-1}\x00"
        text = re.sub(r'\$\$[^\$]*\$\$|\$[^\$]+\$|`[^`]+`', stash, text)

        text = re.sub(r'\*\*\*(.+?)\*\*\*', r'\\textbf{\\textit{\1}}', text)
        text = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', text)
        text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'\\textit{\1}', text)
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\\href{\2}{\1}', text)
        text = re.sub(r'(?<![(\w])https?://[^\s)]+', lambda m: f'\\url{{{m.group(0)}}}', text)
        text = text.replace(' — ', ' --- ')
        text = text.replace('—', '---')
        text = escape_latex(text)

        def restore(m):
            idx = int(m.group(1))
            original = placeholders[idx]
            if original.startswith('`'):
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
        nonlocal in_code, code_lines, next_code_is_figure, code_lang
        if in_code:
            # latex-fenced blocks: pass through as raw LaTeX (for TikZ figures etc.)
            if code_lang.lower() == 'latex':
                for cl in code_lines:
                    output.append(cl)
            else:
                if not next_code_is_figure:
                    n = min(len(code_lines) + 2, 36)
                    output.append(f"\\needspace{{{n}\\baselineskip}}")
                output.append("\\begin{Code}")
                for cl in code_lines:
                    output.append(cl)
                output.append("\\end{Code}")
            code_lines = []
            in_code = False
            code_lang = ""
            next_code_is_figure = False

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

        # Display math: $$ on its own line opens/closes a multi-line block
        if stripped == "$$":
            if in_display_math:
                output.append("\\[")
                for ml in display_math_lines:
                    output.append(ml)
                output.append("\\]")
                display_math_lines = []
                in_display_math = False
            else:
                flush_blockquote()
                flush_list()
                if in_table:
                    flush_table()
                in_display_math = True
                display_math_lines = []
            i += 1
            continue

        if in_display_math:
            display_math_lines.append(line)
            i += 1
            continue

        # Code fence — detect language
        if stripped.startswith("```"):
            if in_code:
                flush_code()
            else:
                flush_blockquote()
                flush_list()
                if in_table:
                    flush_table()
                fence_match = re.match(r'^```(\w*)\s*$', stripped)
                code_lang = fence_match.group(1) if fence_match else ""
                in_code = True
                code_lines = []
            i += 1
            continue

        if in_code:
            code_lines.append(line)
            i += 1
            continue

        if stripped == "":
            flush_blockquote()
            if in_list:
                j = i + 1
                while j < len(lines) and lines[j].strip() == "":
                    j += 1
                next_line = lines[j].strip() if j < len(lines) else ""
                continues_ol = list_type == 'ol' and re.match(r'^\d+\.\s+', next_line)
                continues_ul = list_type == 'ul' and re.match(r'^[-*]\s+', next_line)
                if not (continues_ol or continues_ul):
                    flush_list()
            else:
                flush_list()
            if not in_table:
                output.append("")
            i += 1
            continue

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

        if re.match(r'^---+$', stripped) or re.match(r'^\*\*\*+$', stripped):
            flush_blockquote()
            flush_list()
            output.append("\\sectionbreak")
            i += 1
            continue

        h_match = re.match(r'^(#{1,4})\s+(.*)', stripped)
        if h_match:
            flush_blockquote()
            flush_list()
            level = len(h_match.group(1))
            raw_title = h_match.group(2)
            title = process_inline(raw_title)
            if level == 3 and re.match(r'^Figure\s+\d', raw_title):
                code_len = 0
                for j in range(i + 1, min(i + 4, len(lines))):
                    if lines[j].strip().startswith('```'):
                        for k in range(j + 1, len(lines)):
                            if lines[k].strip().startswith('```'):
                                break
                            code_len += 1
                        break
                n = min(code_len + 6, 40)
                output.append(f"\\needspace{{{n}\\baselineskip}}")
                next_code_is_figure = True
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
            latex_body.append("\\chapter*{About this volume}")
            latex_body.append("\\addcontentsline{toc}{chapter}{About this volume}")
            latex_body.append("\\markboth{ABOUT THIS VOLUME}{ABOUT THIS VOLUME}")
            # Drop the first H1 from README (it becomes the chapter title)
            content = re.sub(r'^#\s+.+\n', '', content, count=1)
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

    tex_path = os.path.join(OUTPUT_DIR, "coherent-structure.tex")
    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write(full_latex)
    print(f"LaTeX source written to: {tex_path}")

    for run in range(2):
        print(f"XeLaTeX pass {run+1}...")
        result = subprocess.run(
            ["xelatex", "-interaction=nonstopmode",
             "-file-line-error", "-halt-on-error",
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

    pdf_path = os.path.join(OUTPUT_DIR, "coherent-structure.pdf")
    if os.path.exists(pdf_path):
        size_mb = os.path.getsize(pdf_path) / (1024*1024)
        print(f"\nBook compiled successfully!")
        print(f"PDF: {pdf_path}")
        print(f"Size: {size_mb:.1f} MB")
    else:
        print("\nPDF not generated. Check .log for errors.")
        log_path = os.path.join(OUTPUT_DIR, "coherent-structure.log")
        if os.path.exists(log_path):
            with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
                log = f.read()
            for line in log.split('\n'):
                if line.startswith('!'):
                    print(f"  {line}")


if __name__ == "__main__":
    build_book()
