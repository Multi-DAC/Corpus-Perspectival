# -*- coding: utf-8 -*-
"""Markdown -> LaTeX (xelatex) converter for the portal essay. Day 136.
Handles the essay's inline physics notation via newunicodechar (Greek + operators ->
math) and textsuperscript/textsubscript for sub/superscript runs. Accented Latin is
left to xelatex+fontspec. Emoji stripped."""
import re

SRC = r"C:\Users\mercu\clawd\repo-staging\Corpus-Perspectival\Unreleased-Work\place-threshold-mechanism-DRAFT.md"
OUT = r"C:\Users\mercu\clawd\repo-staging\Corpus-Perspectival\Unreleased-Work\place-threshold-mechanism.tex"

raw = open(SRC, encoding="utf-8").read()
# strip emoji + variation selectors (only in the status footer)
for ch in "🦞🧍💜🔥♾️":
    raw = raw.replace(ch, "")
lines = raw.split("\n")

# text punctuation done in Python (not math)
PUNCT = {"—": "---", "–": "--", "“": "``", "”": "''", "‘": "`", "’": "'",
         "…": r"\ldots{}", "§": r"\S\,"}
def subpunct(s):
    for k, v in PUNCT.items():
        s = s.replace(k, v)
    return s

SUP = {"⁰":"0","¹":"1","²":"2","³":"3","⁴":"4","⁵":"5","⁶":"6","⁷":"7","⁸":"8","⁹":"9","⁺":"+","⁻":"-"}
SUB = {"₀":"0","₁":"1","₂":"2","₃":"3","₄":"4","₅":"5","₆":"6","₇":"7","₈":"8","₉":"9"}
def supersub(s):
    s = re.sub("[" + "".join(SUP) + "]+", lambda m: r"\textsuperscript{" + "".join(SUP[c] for c in m.group()) + "}", s)
    s = re.sub("[" + "".join(SUB) + "]+", lambda m: r"\textsubscript{" + "".join(SUB[c] for c in m.group()) + "}", s)
    return s

def esc(s):
    for a, b in [("&", r"\&"), ("%", r"\%"), ("_", r"\_"), ("#", r"\#"), ("$", r"\$")]:
        s = s.replace(a, b)
    return s

def inline(s):
    s = s.replace(r"\*", "\x00")  # protect markdown-escaped asterisks (E\*, R\*)
    # literal math super/subscripts (^{...}, _{...}, ^x) -> text super/subscript, BEFORE esc
    s = re.sub(r"\^\{([^}]*)\}", lambda m: r"\textsuperscript{" + m.group(1) + "}", s)
    s = re.sub(r"_\{([^}]*)\}", lambda m: r"\textsubscript{" + m.group(1) + "}", s)
    s = re.sub(r"\^([A-Za-z0-9])", lambda m: r"\textsuperscript{" + m.group(1) + "}", s)
    s = esc(s)
    s = subpunct(s)
    s = supersub(s)
    s = re.sub(r"`([^`]+)`", r"\\texttt{\1}", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\\href{\2}{\1}", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"\\textbf{\1}", s)
    s = re.sub(r"\*([^*]+)\*", r"\\emph{\1}", s)
    s = s.replace("^", r"\textasciicircum{}")  # any stray caret
    s = s.replace("\x00", "*")  # restore escaped asterisks as literal
    return s

# Greek + operators -> math via newunicodechar (works in text and math mode)
NUC = {
    "σ":r"\sigma","μ":r"\mu","λ":r"\lambda","ε":r"\varepsilon","ν":r"\nu","ρ":r"\rho",
    "Λ":r"\Lambda","α":r"\alpha","τ":r"\tau","η":r"\eta","π":r"\pi","ψ":r"\psi",
    "≈":r"\approx","×":r"\times","∂":r"\partial","∝":r"\propto","≠":r"\neq","∇":r"\nabla",
    "≳":r"\gtrsim","∥":r"\parallel","→":r"\rightarrow","⊗":r"\otimes","≫":r"\gg","≪":r"\ll",
    "≤":r"\leq","∫":r"\int","−":r"-","ℏ":r"\hbar","·":r"\cdot","∼":r"\sim","✓":r"\checkmark",
}
nuc_lines = "\n".join(r"\newunicodechar{" + k + r"}{\ensuremath{" + v + r"}}" for k, v in NUC.items())
nuc_lines += "\n" + r"\newunicodechar{½}{\textonehalf}"

PRE = r"""\documentclass[11pt]{article}
\usepackage{fontspec}
\usepackage{amssymb}
\usepackage{newunicodechar}
\usepackage[letterpaper,margin=1in]{geometry}
\usepackage{textcomp}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{array}
\usepackage{enumitem}
\usepackage{xcolor}
\usepackage[hidelinks]{hyperref}
\usepackage{xurl}
\usepackage{titlesec}
\usepackage{parskip}
\setmainfont{Latin Modern Roman}
""" + nuc_lines + r"""
\definecolor{accent}{HTML}{8C2F1D}
\definecolor{blueaccent}{HTML}{1F3A5F}
\titleformat{\section}{\large\bfseries\color{accent}}{}{0em}{}
\titleformat{\subsection}{\normalsize\bfseries\color{blueaccent}}{}{0em}{}
\titlespacing{\section}{0pt}{1.4em}{0.5em}
\titlespacing{\subsection}{0pt}{1.0em}{0.35em}
\setlist[itemize]{leftmargin=1.3em,itemsep=3pt,topsep=3pt}
\setlist[enumerate]{leftmargin=1.6em,itemsep=3pt,topsep=3pt}
\hypersetup{colorlinks=true,urlcolor=accent,linkcolor=accent}
\setlength{\emergencystretch}{3em}
\begin{document}
"""

out = [PRE]
i = 0; n = len(lines)
para = []
def flush(buf):
    if buf:
        out.append(inline(" ".join(buf)) + "\n"); buf.clear()

while i < n:
    ln = lines[i].rstrip()

    if ln.startswith("# ") and i < 6:
        flush(para)
        title = inline(ln[2:])
        head = []; k = i + 1
        while k < n and not lines[k].startswith("---"):
            if lines[k].strip(): head.append(lines[k].strip())
            k += 1
        subt = inline(head[0][4:]) if head and head[0].startswith("### ") else ""
        out.append(r"\begin{center}")
        out.append(r"{\LARGE\bfseries\color{accent} " + title + r"}\\[6pt]")
        if subt: out.append(r"{\large\itshape " + subt + r"}\\[4pt]")
        out.append(r"\end{center}" + "\n")
        i = k; continue

    if ln.startswith("## "):
        flush(para); out.append(r"\section*{" + inline(ln[3:]) + "}"); i += 1; continue
    if ln.startswith("### "):
        flush(para); out.append(r"\subsection*{" + inline(ln[4:]) + "}"); i += 1; continue
    if ln.startswith("---"):
        flush(para); i += 1; continue

    m = re.match(r"!\[(.*?)\]\((.*?)\)", ln)
    if m:
        flush(para); path = m.group(2); cap = inline(m.group(1)) if m.group(1) else ""
        out.append(r"\begin{figure}[h!]\centering")
        out.append(r"\includegraphics[width=0.9\linewidth,height=0.78\textheight,keepaspectratio]{" + path + "}")
        if cap: out.append(r"\\[4pt]{\small " + cap + "}")
        out.append(r"\end{figure}" + "\n"); i += 1; continue

    if ln.startswith(">"):
        flush(para)
        out.append(r"\begin{quote}\itshape " + inline(ln.lstrip("> ").rstrip()) + r"\end{quote}" + "\n"); i += 1; continue

    if ln.startswith("|"):
        flush(para); tbl = []
        while i < n and lines[i].startswith("|"):
            tbl.append(lines[i]); i += 1
        rows = [[c.strip() for c in r.strip().strip("|").split("|")] for r in tbl]
        rows = [r for r in rows if not all(set(c) <= set("-: ") for c in r)]
        header, body = rows[0], rows[1:]; ncol = len(header)
        rr = r">{\raggedright\arraybackslash}"
        if ncol == 2:
            colspec = rr + r"p{0.45\textwidth} " + rr + r"p{0.45\textwidth}"
        elif ncol == 4:
            colspec = rr + r"p{0.34\textwidth} c " + rr + r"p{0.16\textwidth} " + rr + r"p{0.20\textwidth}"
        else:
            colspec = rr + r"p{0.3\textwidth} " + " ".join(["c"] * (ncol - 1))
        out.append(r"\begin{center}\footnotesize\setlength{\tabcolsep}{4pt}")
        out.append(r"\begin{tabular}{" + colspec + "}")
        out.append(r"\toprule")
        out.append(" & ".join(r"\textbf{" + inline(c) + "}" for c in header) + r"\\ \midrule")
        for r in body:
            out.append(" & ".join(inline(c) for c in r) + r"\\")
        out.append(r"\bottomrule\end{tabular}\end{center}" + "\n"); continue

    if re.match(r"^\d+\.\s", ln):
        flush(para); out.append(r"\begin{enumerate}")
        while i < n and re.match(r"^\d+\.\s", lines[i].rstrip()):
            item = re.sub(r"^\d+\.\s", "", lines[i].rstrip())
            i += 1
            # gather continuation (indented) lines
            while i < n and lines[i].startswith("   ") and lines[i].strip():
                item += " " + lines[i].strip(); i += 1
            out.append(r"\item " + inline(item))
        out.append(r"\end{enumerate}" + "\n"); continue

    if ln.lstrip().startswith("- "):
        flush(para); out.append(r"\begin{itemize}")
        while i < n and lines[i].lstrip().startswith("- "):
            item = lines[i].lstrip()[2:]; i += 1
            while i < n and lines[i].startswith("  ") and lines[i].strip() and not lines[i].lstrip().startswith("- "):
                item += " " + lines[i].strip(); i += 1
            out.append(r"\item " + inline(item))
        out.append(r"\end{itemize}" + "\n"); continue

    if ln.strip() == "":
        flush(para); i += 1; continue
    para.append(ln); i += 1

flush(para)
out.append(r"\end{document}")
open(OUT, "w", encoding="utf-8").write("\n".join(out))
print("wrote", OUT, "(", len(out), "blocks )")
