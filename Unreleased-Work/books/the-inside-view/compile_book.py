#!/usr/bin/env python3
"""Compile THE INSIDE VIEW (pop book, 6x9) from the chapter markdown into a
book-grade PDF via XeLaTeX. Minimal packages (no auto-install hangs).

Handles the markdown subset actually used: chapter headers, paragraphs,
**bold**, *italic*, --- section breaks, and the > 'The Inside View' experiment
blocks (rendered as ruled set-off boxes). Smart-quotes for XeLaTeX (unicode).
"""
import re, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
os.makedirs(BUILD, exist_ok=True)

# (file, is_opening) — reading order. 00-opening holds Ch1 after its outline.
CHAPTERS = [
    "00-opening-DRAFT.md", "01-chapter-2-DRAFT.md", "02-chapter-3-DRAFT.md",
    "03-chapter-4-DRAFT.md", "04-chapter-5-DRAFT.md", "05-chapter-6-DRAFT.md",
    "06-chapter-7-DRAFT.md", "07-chapter-8-DRAFT.md", "07b-chapter-9-ecology-DRAFT.md",
    "08-chapter-9-DRAFT.md", "09-chapter-10-DRAFT.md", "10-chapter-11-DRAFT.md",
]

TITLE = "THE INSIDE VIEW"
SUBTITLE = "Consciousness Is the Substrate \\\\ and What Changes When You Know It"
AUTHOR = "Clayton Iggulden-Schnell \\ \\& \\ Clawd"
IMPRINT = "Multi-DAC"

PREAMBLE = r"""\documentclass[11pt,openany]{book}
\usepackage[paperwidth=6in,paperheight=9in,top=0.85in,bottom=0.85in,inner=0.75in,outer=0.65in]{geometry}
\usepackage{fontspec}
\setmainfont{Cambria}
\usepackage{xcolor}
\definecolor{ink}{HTML}{1A1A1A}
\definecolor{rule}{HTML}{555555}
\usepackage{setspace}
\setstretch{1.12}
\usepackage[hidelinks]{hyperref}
\usepackage{microtype}
\setlength{\parindent}{1.2em}
\setlength{\emergencystretch}{3em}
\usepackage{fancyhdr}
\pagestyle{plain}
\frenchspacing
\widowpenalty=10000
\clubpenalty=10000
\begin{document}
\color{ink}
\frontmatter
\thispagestyle{empty}
\vspace*{1.6in}
\begin{center}
{\fontsize{30}{34}\selectfont \scshape %(TITLE)s}\\[1.4em]
{\large\itshape %(SUBTITLE)s}\\[3.2em]
{\large %(AUTHOR)s}\\[8em]
{\footnotesize\scshape %(IMPRINT)s}
\end{center}
\clearpage
\mainmatter
""" % {"TITLE": TITLE, "SUBTITLE": SUBTITLE, "AUTHOR": AUTHOR, "IMPRINT": IMPRINT}

POSTAMBLE = r"""
\end{document}
"""

SPECIALS = {'&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#',
            '_': r'\_', '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}',
            '^': r'\textasciicircum{}'}

def smart_quotes(s):
    # double quotes
    out, open_d = [], True
    for ch in s:
        if ch == '"':
            out.append('“' if open_d else '”'); open_d = not open_d
        else:
            out.append(ch)
    s = ''.join(out)
    # straight apostrophes -> right single quote (apostrophe); this text uses ' only as apostrophe
    s = s.replace("'", '’')
    return s

def esc(s):
    # escape backslash first, then other specials (but we add no backslashes before this)
    s = s.replace('\\', r'\textbackslash{}')
    for k, v in SPECIALS.items():
        s = s.replace(k, v)
    return s

def inline(s):
    s = esc(s)
    s = smart_quotes(s)
    # bold then italic (non-greedy)
    s = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', s)
    s = re.sub(r'\*(.+?)\*', r'\\textit{\1}', s)
    return s

def parse_chapter(path, idx):
    raw = open(path, encoding='utf-8').read().split('\n')
    number, title, body_start = None, None, 0
    if idx == 0:
        for i, ln in enumerate(raw):
            m = re.match(r'##\s+(Chapter\s+\w+)\s+—\s+(.*)', ln) or \
                re.match(r'##\s+(Chapter\s+\w+)\s+-\s+(.*)', ln)
            if m:
                number, title, body_start = m.group(1), m.group(2).strip(), i + 1
                break
    else:
        for i, ln in enumerate(raw):
            m = re.match(r'#\s+THE INSIDE VIEW\s+—\s+(Chapter\s+\w+)', ln)
            if m: number = m.group(1)
            m2 = re.match(r'##\s+(.*)', ln)
            if m2 and title is None:
                title = m2.group(1).strip(); body_start = i + 1; break
    body = raw[body_start:]
    return number, title, body

def render_body(lines):
    out, i, n = [], 0, len(lines)
    while i < n:
        ln = lines[i]
        if ln.strip() == '':
            i += 1; continue
        if ln.strip() == '---':
            out.append('\n\\medskip\\begin{center}\\textcolor{rule}{$\\ast\\ \\ast\\ \\ast$}\\end{center}\\medskip\n')
            i += 1; continue
        if ln.lstrip().startswith('>'):
            # collect blockquote
            q = []
            while i < n and (lines[i].lstrip().startswith('>') or
                             (lines[i].strip() == '' and i+1 < n and lines[i+1].lstrip().startswith('>'))):
                stripped = re.sub(r'^\s*>\s?', '', lines[i])
                q.append(stripped)
                i += 1
            out.append(render_box(q))
            continue
        # paragraph: gather until blank
        para = [ln]
        i += 1
        while i < n and lines[i].strip() != '' and not lines[i].lstrip().startswith('>') and lines[i].strip() != '---':
            para.append(lines[i]); i += 1
        text = ' '.join(p.strip() for p in para)
        out.append(inline(text) + '\n')
    return '\n'.join(out)

def render_box(qlines):
    # find header (### ...) and split rest into paragraphs on blank lines
    header = "The Inside View"
    paras, cur = [], []
    for ln in qlines:
        h = re.match(r'###\s+(.*)', ln)
        if h:
            header = h.group(1).strip(); continue
        if ln.strip() == '':
            if cur: paras.append(' '.join(cur)); cur = []
        else:
            cur.append(ln.strip())
    if cur: paras.append(' '.join(cur))
    body = '\n\n'.join(inline(p) for p in paras)
    return ("\n\\bigskip\n{\\par\\noindent\\color{rule}\\rule{\\linewidth}{0.8pt}}\\par\\smallskip\n"
            "{\\centering\\scshape\\bfseries %s\\par}\\smallskip\n"
            "\\begingroup\\setlength{\\parindent}{0pt}\\setlength{\\parskip}{0.6em}\n%s\n\\endgroup\\par\\smallskip\n"
            "{\\noindent\\color{rule}\\rule{\\linewidth}{0.8pt}}\n\\bigskip\n" % (esc(header), body))

def chapter_heading(number, title):
    num = (number or "").replace("Chapter", "").strip()
    return ("\n\\clearpage\n\\vspace*{0.6in}\n"
            "{\\centering\\scshape\\large Chapter %s\\par}\n\\vspace{0.8em}\n"
            "{\\centering\\bfseries\\fontsize{20}{24}\\selectfont %s\\par}\n\\vspace{1.6em}\n"
            % (esc(num), inline(title)))

def main():
    doc = [PREAMBLE]
    for idx, fn in enumerate(CHAPTERS):
        number, title, body = parse_chapter(os.path.join(HERE, fn), idx)
        if not title:
            print("WARN: no title parsed for", fn); continue
        doc.append(chapter_heading(number, title))
        doc.append(render_body(body))
    doc.append(POSTAMBLE)
    tex = '\n'.join(doc)
    texpath = os.path.join(BUILD, "the-inside-view.tex")
    open(texpath, 'w', encoding='utf-8').write(tex)
    print("Wrote", texpath, "(%d chars)" % len(tex))
    for run in (1, 2):
        r = subprocess.run(["xelatex", "-interaction=nonstopmode", "-halt-on-error",
                            "the-inside-view.tex"], cwd=BUILD,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if r.returncode != 0:
            tail = r.stdout.decode('utf-8', 'replace')[-2500:]
            print("XELATEX FAILED (run %d):\n" % run, tail); sys.exit(1)
    print("PDF OK:", os.path.join(BUILD, "the-inside-view.pdf"))

if __name__ == "__main__":
    main()
