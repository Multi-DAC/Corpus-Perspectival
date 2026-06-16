# -*- coding: utf-8 -*-
import re, os

SRC = r"C:\Users\mercu\clawd\repo-staging\Corpus-Perspectival\Unreleased-Work\one-room-many-keyholes-DRAFT.md"
OUT = r"C:\Users\mercu\clawd\repo-staging\Corpus-Perspectival\Unreleased-Work\one-room-many-keyholes.tex"

with open(SRC, encoding="utf-8") as f:
    lines = f.read().split("\n")

# ---- glyph / symbol substitutions (applied to text + table cells) ----
GLYPH = {
    "●":r"\CIRCLE", "◐":r"\LEFTcircle", "○":r"\Circle", "★":r"$\bigstar$",
    "·":r"{\color{gray}\textperiodcentered}", "×":r"$\times$", "→":r"$\rightarrow$",
    "↔":r"$\leftrightarrow$", "−":r"$-$", "—":"---", "–":"--", "…":r"\ldots{}",
    "“":"``", "”":"''", "‘":"`", "’":"'", "ō":r"\={o}", "ē":r"\={e}", "ā":r"\={a}",
    "≈":r"$\approx$", "⊥":r"$\perp$", "§":r"\S\,",
}
def subglyph(s):
    for k,v in GLYPH.items(): s = s.replace(k,v)
    return s

def esc(s):
    # escape LaTeX specials that occur in body text (markdown uses * [ ] ( ) ` not these)
    s = s.replace("\\", "")  # no stray backslashes expected in source text
    for a,b in [("&",r"\&"),("%",r"\%"),("_",r"\_"),("#",r"\#")]:
        s = s.replace(a,b)
    return s

def inline(s):
    s = esc(s)
    s = subglyph(s)
    s = re.sub(r"`([^`]+)`", r"\\texttt{\1}", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\\href{\2}{\1}", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"\\textbf{\1}", s)
    s = re.sub(r"\*([^*]+)\*", r"\\emph{\1}", s)
    return s

PRE = r"""\documentclass[11pt]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[letterpaper,margin=1in]{geometry}
\usepackage{lmodern}
\usepackage{wasysym}
\usepackage{amssymb}
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
\definecolor{accent}{HTML}{8C2F1D}
\definecolor{blueaccent}{HTML}{1F3A5F}
\titleformat{\section}{\large\bfseries\color{accent}}{}{0em}{}
\titleformat{\subsection}{\normalsize\bfseries\color{blueaccent}}{}{0em}{}
\titlespacing{\section}{0pt}{1.4em}{0.5em}
\titlespacing{\subsection}{0pt}{1.0em}{0.35em}
\setlist[itemize]{leftmargin=1.3em,itemsep=4pt,topsep=4pt}
\hypersetup{colorlinks=true,urlcolor=accent,linkcolor=accent}
\setlength{\emergencystretch}{3em}
\begin{document}
"""

out = [PRE]
i = 0
n = len(lines)

def flush_para(buf):
    if buf:
        out.append(inline(" ".join(buf)) + "\n")
        buf.clear()

para = []
while i < n:
    ln = lines[i].rstrip()

    # title block (first H1 + subtitle + byline)
    if ln.startswith("# ") and i < 6:
        flush_para(para)
        title = inline(ln[2:])
        sub = ""; by = ""
        # next lines: ### subtitle, *italic subtitle*, **byline**
        j = i+1
        while j < n and lines[j].strip()=="" : j+=1
        # gather until '---'
        head=[]
        k=i+1
        while k<n and not lines[k].startswith("---"):
            if lines[k].strip(): head.append(lines[k].strip())
            k+=1
        subt = inline(head[0][4:]) if head and head[0].startswith("### ") else ""
        ital = inline(head[1]) if len(head)>1 else ""
        byln = inline(head[2]) if len(head)>2 else ""
        out.append(r"\begin{center}")
        out.append(r"{\LARGE\bfseries\color{accent} "+title+r"}\\[4pt]")
        if subt: out.append(r"{\large "+subt+r"}\\[6pt]")
        if ital: out.append(r"{\itshape "+ital+r"}\\[6pt]")
        if byln: out.append(byln+r"\\[2pt]")
        out.append(r"\end{center}"+"\n")
        i = k
        continue

    if ln.startswith("## "):
        flush_para(para); out.append(r"\section*{"+inline(ln[3:])+"}"); i+=1; continue
    if ln.startswith("### "):
        flush_para(para); out.append(r"\subsection*{"+inline(ln[4:])+"}"); i+=1; continue

    if ln.startswith("---"):
        flush_para(para); i+=1; continue

    # image  ![alt](path)  + following italic caption block
    m = re.match(r"!\[(.*?)\]\((.*?)\)", ln)
    if m:
        flush_para(para)
        path = m.group(2)
        # find caption (next non-empty line, italic)
        cap=""; j=i+1
        while j<n and lines[j].strip()=="" : j+=1
        if j<n and lines[j].strip().startswith("*"):
            cap = inline(lines[j].strip()); i=j+1
        else:
            i=i+1
        out.append(r"\begin{figure}[h!]\centering")
        out.append(r"\includegraphics[width=0.92\linewidth,height=0.82\textheight,keepaspectratio]{"+path+"}")
        if cap: out.append(r"\\[4pt]{\small "+cap+"}")
        out.append(r"\end{figure}"+"\n")
        continue

    # blockquote
    if ln.startswith(">"):
        flush_para(para)
        out.append(r"\begin{quote}\itshape "+inline(ln.lstrip("> ").rstrip())+r"\end{quote}"+"\n"); i+=1; continue

    # table
    if ln.startswith("|"):
        flush_para(para)
        tbl=[]
        while i<n and lines[i].startswith("|"):
            tbl.append(lines[i]); i+=1
        rows=[[c.strip() for c in r.strip().strip("|").split("|")] for r in tbl]
        rows=[r for r in rows if not all(set(c)<=set("-: ") for c in r)]  # drop sep row
        header=rows[0]; body=rows[1:]
        ncol=len(header)
        colspec="r p{4.6cm} "+" ".join(["c"]*(ncol-2))
        out.append(r"\begin{center}\scriptsize\setlength{\tabcolsep}{3pt}")
        out.append(r"\begin{tabular}{"+colspec+"}")
        out.append(r"\toprule")
        out.append(" & ".join(r"\textbf{"+inline(c)+"}" for c in header)+r"\\ \midrule")
        for r in body:
            out.append(" & ".join(inline(c) for c in r)+r"\\")
        out.append(r"\bottomrule\end{tabular}\end{center}"+"\n")
        continue

    # list
    if ln.lstrip().startswith("- "):
        flush_para(para)
        out.append(r"\begin{itemize}")
        while i<n and lines[i].lstrip().startswith("- "):
            out.append(r"\item "+inline(lines[i].lstrip()[2:])); i+=1
        out.append(r"\end{itemize}"+"\n"); continue

    if ln.strip()=="":
        flush_para(para); i+=1; continue

    para.append(ln); i+=1

flush_para(para)
out.append(r"\end{document}")

with open(OUT,"w",encoding="utf-8") as f:
    f.write("\n".join(out))
print("wrote", OUT, "lines", len(out))
