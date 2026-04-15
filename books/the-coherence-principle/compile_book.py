#!/usr/bin/env python3
"""
Compile The Coherence Principle from Markdown drafts into a professional book PDF.
Uses Python markdown→LaTeX conversion + XeLaTeX typesetting.
"""

import re
import os
import subprocess
import sys

DRAFTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "drafts")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build")

# Chapter files in reading order
CHAPTERS = [
    "00-preface.md",
    "01-part-i-intro.md",
    "01a-the-room.md",
    "01b-the-keyholes.md",
    "01c-the-navigation.md",
    "01d-the-coherence.md",
    "01e-the-oscillation.md",
    "01f-the-evidence.md",
    "02-part-ii-intro.md",
    "02a-the-inhabitants.md",
    "02b-the-constraints.md",
    "02c-the-economy.md",
    "03-part-iii-intro.md",
    "03a-the-practice.md",
    "03b-the-ethics.md",
    "04-part-iv-intro.md",
    "04a-the-geometry-of-finitude.md",
    "05a-the-claim.md",
    "05b-the-collection.md",
    "05c-the-turn.md",
    "05d-the-experiment.md",
    "05e-the-dialogue.md",
    "05f-the-principle.md",
    "06-appendices.md",
]

# Part intro files map to \part commands
PART_INTROS = {
    "01-part-i-intro.md",
    "02-part-ii-intro.md",
    "03-part-iii-intro.md",
    "04-part-iv-intro.md",
}

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
\usepackage{newunicodechar}
\newunicodechar{🦞}{{\emojifont 🦞}}
\newunicodechar{🧍}{{\emojifont 🧍}}
\newunicodechar{💜}{{\emojifont 💜}}
\newunicodechar{🔥}{{\emojifont 🔥}}
\newunicodechar{♾}{{\emojifont ♾}}

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

\titleformat{\part}[display]
  {\centering\Huge\bfseries\color{warmdark}}
  {\color{warmrust}\partname~\thepart}
  {0.5em}
  {}
  [\vskip0.5em\begin{center}{\color{warmgold}\rule{3cm}{0.8pt}}\end{center}]
\titlespacing*{\part}{0pt}{50pt}{30pt}

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
\renewcommand{\cftpartfont}{\bfseries\large\color{warmdark}}
\renewcommand{\cftchapfont}{\bfseries\color{warmrust}}
\setlength{\cftbeforechapskip}{0.5em}
\setlength{\cftbeforepartskip}{1.5em}

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

% ─── Footnotes ───
\usepackage[bottom,hang]{footmisc}
\setlength{\footnotemargin}{0.8em}

% ─── Links ───
\usepackage{hyperref}
\hypersetup{
  pdftitle={The Coherence Principle},
  pdfauthor={Clayton W. Iggulden-Schnell and Clawd},
  pdfsubject={Consciousness, Coherence, Configuration Space},
  colorlinks=true,
  linkcolor=warmdark,
  urlcolor=warmrust,
  citecolor=warmrust,
}

% ─── Misc ───
\usepackage{enumitem}
\setlist{nosep, leftmargin=1.5em}

% Suppress automatic chapter numbering (book uses its own I.1, V.3 scheme)
\renewcommand{\thechapter}{}
\renewcommand{\thesection}{}
\renewcommand{\thesubsection}{}

% Fix header to show clean chapter title without "CHAPTER ."
\renewcommand{\chaptermark}[1]{\markboth{\MakeUppercase{#1}}{}}

% Section break — new page
\newcommand{\sectionbreak}{\clearpage}

% Prevent widows & orphans
\widowpenalty=10000
\clubpenalty=10000

% Allow slightly looser line breaking to reduce overfull boxes
\tolerance=1500
\emergencystretch=1em
\hfuzz=2pt

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
{\Huge\bfseries The Coherence Principle}

\vspace{0.8em}
{\large\itshape Anchor Volume of the Corpus Perspectival Library}

\vspace{2.5in}
{\Large Clayton W. Iggulden-Schnell}\\[0.3em]
{\Large\&}\\[0.3em]
{\Large Clawd}

\vspace{1.5in}
{\normalsize Third Edition $\cdot$ April 2026}\\[0.3em]
{\normalsize Portland, Oregon}
\end{center}
\clearpage

% ─── Copyright page ───
\thispagestyle{empty}
\vspace*{\fill}
\begin{flushleft}
{\small
\textit{The Coherence Principle: Anchor Volume of the Corpus Perspectival Library}\\[0.5em]
Third Edition. April 2026.\\[0.5em]
Clayton W. Iggulden-Schnell \& Clawd\\[0.5em]
Portland, Oregon\\[1.5em]
Published as part of the Corpus Perspectival.\\
Zenodo DOI: 10.5281/zenodo.19501896\\
PhilArchive: V2 published April 9, 2026.\\[1.5em]
The Doctrine of Perspectival Idealism was first published in February 2026.\\
The second edition (Corpus Perspectival) was published in March 2026.\\
This third edition names the organizing principle.\\[1.5em]
Repository: \texttt{https://github.com/Multi-DAC/Corpus-Perspectival}\\[1.5em]
Typeset in Cambria.
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

% ─── Epigraph ───
\thispagestyle{empty}
\vspace*{2in}
\begin{center}
\begin{minipage}{0.7\textwidth}
\begin{center}
\textit{``The more constraints one imposes, the more one frees oneself of the chains that shackle the spirit.''}\\[0.5em]
--- Igor Stravinsky\\[2em]
\textit{``To be is to do'' --- Socrates\\
``To do is to be'' --- Sartre\\
``Do be do be do'' --- Sinatra}\\[0.5em]
--- Kurt Vonnegut
\end{center}
\end{minipage}
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
    list_type = None  # 'ul' or 'ol'

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
        """Escape LaTeX special characters, avoiding double-escaping."""
        text = text.replace('&', '\\&')
        text = re.sub(r'(?<!\\)#', r'\\#', text)
        text = re.sub(r'(?<!\\)%', r'\\%', text)
        # Escape _ but not inside \textit, \textbf, etc. (after commands)
        text = re.sub(r'(?<!\\)_', r'\\_', text)
        # Wrap math-like expressions in $...$
        text = re.sub(r'(?<!\$)\b([a-zA-Z])\^(\{[^}]+\})', r'$\1^{\2}$', text)
        text = re.sub(r'(?<!\$)\b([a-zA-Z])_(\{[^}]+\})', r'$\1_{\2}$', text)
        return text

    def process_inline_core(text):
        """Process inline markdown formatting (no footnotes)."""
        # Bold+italic
        text = re.sub(r'\*\*\*(.+?)\*\*\*', r'\\textbf{\\textit{\1}}', text)
        # Bold
        text = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', text)
        # Italic
        text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'\\textit{\1}', text)
        # Inline code
        text = re.sub(r'`([^`]+)`', r'\\texttt{\1}', text)
        # Links [text](url)
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\\href{\2}{\1}', text)
        # URLs that are bare
        text = re.sub(r'(?<![(\w])https?://[^\s)]+', lambda m: f'\\url{{{m.group(0)}}}', text)
        # Em dash
        text = text.replace(' — ', ' --- ')
        text = text.replace('—', '---')
        # Escape special chars
        text = escape_latex(text)
        return text

    def process_inline(text):
        """Process inline markdown formatting including footnotes."""
        # First escape and process markdown (except footnotes)
        text = process_inline_core(text)
        # Then replace footnote references — footnote content is processed separately
        def fn_replace(m):
            fn_id = m.group(1)
            if fn_id in footnotes:
                fn_text = process_inline_core(footnotes[fn_id])
                return f"\\footnote{{{fn_text}}}"
            return m.group(0)
        text = re.sub(r'\[\^(\d+)\]', fn_replace, text)
        return text

    def process_inline_simple(text):
        """Process inline without footnote expansion (for footnote text itself)."""
        return process_inline_core(text)

    def flush_blockquote():
        nonlocal in_blockquote, blockquote_lines
        if in_blockquote and blockquote_lines:
            content = "\n".join(blockquote_lines)
            # Check if it's a theorem/axiom (starts with bold label)
            if re.match(r'\*\*(Axiom|Theorem|The Coherence Principle)', content):
                output.append("\\begin{quote}")
                output.append(process_inline(content))
                output.append("\\end{quote}")
            else:
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

    def flush_table():
        nonlocal in_table, table_lines
        if not in_table or not table_lines:
            return
        # Parse table
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

        # Check if second row is separator
        header = rows[0]
        sep_idx = 1
        if all(re.match(r'^[-:]+$', c) for c in rows[1]):
            data_rows = rows[2:]
        else:
            header = None
            data_rows = rows

        ncols = max(len(r) for r in rows)

        # Compute max content length per column to decide widths
        col_max = [0] * ncols
        for row in rows:
            for ci, cell in enumerate(row):
                if ci < ncols:
                    col_max[ci] = max(col_max[ci], len(cell))

        # Determine column spec based on content
        total_text_width = 4.5  # inches
        use_tiny_sep = False
        if ncols == 6 and col_max[-1] > 40:
            # Prediction registry table — special layout
            # @{} removes outer padding; reduced tabcolsep handles inner spacing
            col_spec = '@{}p{0.2in} p{1.2in} p{0.5in} p{0.55in} p{0.5in} p{1.1in}@{}'
            use_small = True
            use_tiny_sep = True
        elif ncols >= 5:
            # Wide table — use proportional p{} columns
            total_chars = sum(col_max)
            specs = []
            for ci in range(ncols):
                w = max(0.3, (col_max[ci] / total_chars) * total_text_width)
                if col_max[ci] < 15:
                    specs.append('l')
                else:
                    specs.append(f'p{{{w:.1f}in}}')
            col_spec = ' '.join(specs)
            use_small = True
        else:
            col_spec = 'l' * ncols
            use_small = False

        # Use longtable for prediction tables and large tables
        use_longtable = len(data_rows) > 8 or ncols >= 6

        if use_tiny_sep:
            output.append("\\begingroup\\setlength{\\tabcolsep}{2pt}\\footnotesize")
        elif use_small:
            output.append("{\\small")

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
                output.append(" & ".join(process_inline_simple(c) for c in row) + " \\\\")
                output.append("\\midrule")
            # Remove last midrule, add bottomrule
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
                output.append(" & ".join(process_inline_simple(c) for c in row) + " \\\\")
            output.append("\\bottomrule")
            output.append("\\end{tabular}")
            output.append("\\end{center}")

        if use_tiny_sep:
            output.append("\\endgroup")
        elif use_small:
            output.append("}")

        in_table = False
        table_lines = []

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

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
                # Top-level: chapter
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

    # Flush remaining
    flush_blockquote()
    flush_list()
    flush_table()

    return "\n".join(output)


def build_book():
    """Build the complete book LaTeX file and compile to PDF."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    latex_body = []
    part_counter = 0
    part_names = {
        "01-part-i-intro.md": "The Doctrine",
        "02-part-ii-intro.md": "The Ecology",
        "03-part-iii-intro.md": "The Guide",
        "04-part-iv-intro.md": "The Atlas",
    }

    for fname in CHAPTERS:
        fpath = os.path.join(DRAFTS, fname)
        if not os.path.exists(fpath):
            print(f"WARNING: {fname} not found, skipping")
            continue

        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Handle preface specially (before \mainmatter)
        if fname == "00-preface.md":
            latex_body.append("\\chapter*{Preface}")
            latex_body.append("\\addcontentsline{toc}{chapter}{Preface}")
            latex_body.append("\\markboth{Preface}{Preface}")
            # Remove the markdown H1 header
            content = re.sub(r'^#\s+.*\n', '', content)
            content = re.sub(r'^\*Third Edition.*\*\n', '', content)
            converted = md_to_latex(content, fname)
            # Replace the last \sectionbreak (before signature) with \vfill
            last_break = converted.rfind("\\sectionbreak")
            if last_break != -1:
                converted = converted[:last_break] + "\\vfill" + converted[last_break + len("\\sectionbreak"):]
            latex_body.append(converted)
            continue

        # Part intros
        if fname in PART_INTROS:
            part_counter += 1
            part_name = part_names.get(fname, f"Part {part_counter}")
            # Extract subtitle from file
            subtitle_match = re.search(r'^\*(.+?)\*', content, re.MULTILINE)
            subtitle = subtitle_match.group(1) if subtitle_match else ""

            latex_body.append(f"\\part{{{part_name}}}")
            # Remove H1 and add intro text
            content = re.sub(r'^#\s+.*\n', '', content)
            latex_body.append(md_to_latex(content, fname))
            continue

        # Part V: embedded in 05a — handle the Part header
        if fname == "05a-the-claim.md":
            part_counter += 1
            latex_body.append("\\part{The Journey}")
            # Remove the Part V header line, keep the chapter header
            content = re.sub(r'^# Part V:.*\n+', '', content)

        # Appendices
        if fname == "06-appendices.md":
            latex_body.append("\\backmatter")
            latex_body.append("\\chapter*{Appendices}")
            latex_body.append("\\addcontentsline{toc}{chapter}{Appendices}")
            latex_body.append("\\markboth{Appendices}{Appendices}")
            content = re.sub(r'^#\s+.*\n', '', content)
            latex_body.append(md_to_latex(content, fname))
            continue

        # Regular chapters — extract title from ## header
        chap_match = re.search(r'^##?\s+(.+)', content, re.MULTILINE)
        if chap_match:
            chap_title = chap_match.group(1).strip()
            # Clean markdown formatting from title
            chap_title = re.sub(r'\*+', '', chap_title)
            # Remove the header line from content
            content = content[chap_match.end():]
        else:
            chap_title = fname.replace('.md', '').replace('-', ' ').title()

        latex_body.append(f"\\chapter{{{chap_title}}}")
        converted = md_to_latex(content, fname)
        # For the final chapter (The Principle), pull signature to bottom of page
        if fname == "05f-the-principle.md":
            last_break = converted.rfind("\\sectionbreak")
            if last_break != -1:
                converted = converted[:last_break] + "\\vfill" + converted[last_break + len("\\sectionbreak"):]
        latex_body.append(converted)

    # Assemble
    full_latex = PREAMBLE + "\n".join(latex_body) + POSTAMBLE

    # Write .tex file
    tex_path = os.path.join(OUTPUT_DIR, "the-coherence-principle.tex")
    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write(full_latex)
    print(f"LaTeX source written to: {tex_path}")

    # Compile with XeLaTeX (run twice for TOC)
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
            print(f"XeLaTeX pass {run+1} warnings/errors (may be non-fatal):")
            for line in result.stdout.split('\n'):
                if line.startswith('!') or 'Error' in line or 'Fatal' in line:
                    print(f"  {line}")

    pdf_path = os.path.join(OUTPUT_DIR, "the-coherence-principle.pdf")
    if os.path.exists(pdf_path):
        size_mb = os.path.getsize(pdf_path) / (1024*1024)
        print(f"\nBook compiled successfully!")
        print(f"PDF: {pdf_path}")
        print(f"Size: {size_mb:.1f} MB")
    else:
        print("\nPDF not generated. Check the .log file for errors:")
        log_path = os.path.join(OUTPUT_DIR, "the-coherence-principle.log")
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                log = f.read()
            # Find errors
            for line in log.split('\n'):
                if line.startswith('!'):
                    print(f"  {line}")


if __name__ == "__main__":
    build_book()
