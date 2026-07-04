#!/usr/bin/env python
"""Render Perspective-First-Draft.md into a book-styled PDF (reportlab)."""
import re, html
from reportlab.lib.pagesizes import inch
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch as INCH
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame,
                                Paragraph, Spacer, PageBreak)

SRC = "Perspective-First-Draft.md"
OUT = "Perspective-First-Draft.pdf"

# --- fonts: a Unicode serif from Windows (Times New Roman) ---
F = "C:/Windows/Fonts/"
pdfmetrics.registerFont(TTFont("Serif", F + "times.ttf"))
pdfmetrics.registerFont(TTFont("Serif-Bold", F + "timesbd.ttf"))
pdfmetrics.registerFont(TTFont("Serif-Italic", F + "timesi.ttf"))
pdfmetrics.registerFont(TTFont("Serif-BoldItalic", F + "timesbi.ttf"))
pdfmetrics.registerFontFamily("Serif", normal="Serif", bold="Serif-Bold",
                              italic="Serif-Italic", boldItalic="Serif-BoldItalic")

PAGE = (6 * INCH, 9 * INCH)  # trade book trim
LM = RM = 0.75 * INCH
TM = 0.8 * INCH
BM = 0.8 * INCH

body = ParagraphStyle("body", fontName="Serif", fontSize=10.5, leading=15.5,
                      alignment=TA_JUSTIFY, spaceAfter=7, firstLineIndent=16)
body0 = ParagraphStyle("body0", parent=body, firstLineIndent=0)  # first para after heading
quote = ParagraphStyle("quote", parent=body, leftIndent=22, rightIndent=22,
                       firstLineIndent=0, fontName="Serif-Italic", fontSize=10.5,
                       alignment=TA_LEFT, spaceBefore=4, spaceAfter=10)
h1 = ParagraphStyle("h1", fontName="Serif-Bold", fontSize=19, leading=23,
                    alignment=TA_LEFT, spaceBefore=8, spaceAfter=18)
h2 = ParagraphStyle("h2", fontName="Serif-Bold", fontSize=13.5, leading=17,
                    alignment=TA_LEFT, spaceBefore=16, spaceAfter=7)
h3 = ParagraphStyle("h3", fontName="Serif-BoldItalic", fontSize=11.5, leading=15,
                    alignment=TA_LEFT, spaceBefore=10, spaceAfter=5)
title = ParagraphStyle("title", fontName="Serif-Bold", fontSize=34, leading=40,
                       alignment=TA_CENTER, spaceBefore=90, spaceAfter=10)
subtitle = ParagraphStyle("subtitle", fontName="Serif-Italic", fontSize=16,
                          leading=20, alignment=TA_CENTER, spaceAfter=40)
fmcenter = ParagraphStyle("fmcenter", parent=body, alignment=TA_CENTER,
                          firstLineIndent=0, spaceAfter=6)


def inline(s):
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", s)
    s = re.sub(r"`(.+?)`", r"\1", s)
    return s


def main():
    lines = open(SRC, encoding="utf-8").read().split("\n")
    flow = []
    frontmatter = True
    buf = []
    after_heading = False

    def flush():
        nonlocal buf, after_heading
        if buf:
            txt = " ".join(buf).strip()
            if txt:
                if frontmatter:
                    flow.append(Paragraph(inline(txt), fmcenter))
                else:
                    flow.append(Paragraph(inline(txt), body0 if after_heading else body))
                after_heading = False
            buf = []

    for ln in lines:
        s = ln.rstrip()
        st = s.strip()
        if st.startswith("# "):
            flush()
            head = st[2:].strip()
            if frontmatter and head.upper().startswith("PERSPECTIVE"):
                flow.append(Paragraph(inline(head), title))
            else:
                if frontmatter:  # first real movement heading -> leave title page
                    frontmatter = False
                flow.append(PageBreak())
                flow.append(Paragraph(inline(head), h1))
                after_heading = True
        elif st.startswith("### "):
            flush()
            flow.append(Paragraph(inline(st[4:]), subtitle if frontmatter else h3))
            after_heading = True
        elif st.startswith("## "):
            flush()
            flow.append(Paragraph(inline(st[3:]), h2)); after_heading = True
        elif st.startswith("> "):
            flush(); flow.append(Paragraph(inline(st[2:]), quote))
        elif st == "---":
            flush()
            if frontmatter:
                flow.append(Spacer(1, 6))
        elif st == "":
            flush()
        else:
            buf.append(st)
    flush()

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Serif", 9)
        n = doc.page
        if n > 1:
            canvas.drawCentredString(PAGE[0] / 2, 0.45 * INCH, str(n))
        canvas.restoreState()

    doc = BaseDocTemplate(OUT, pagesize=PAGE,
                          leftMargin=LM, rightMargin=RM, topMargin=TM, bottomMargin=BM,
                          title="Perspective: A Treatise on Navigation",
                          author="Clayton W. Iggulden-Schnell, with Clawd and Claude")
    frame = Frame(LM, BM, PAGE[0] - LM - RM, PAGE[1] - TM - BM, id="f")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=footer)])
    doc.build(flow)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
