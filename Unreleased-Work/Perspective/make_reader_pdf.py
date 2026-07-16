# Build a shareable reader's PDF: identical to the draft build but with the
# "*Draft. Day 160.*" front-matter memo removed. Reuses make_pdf's exact
# rendering (fonts/styles), only swapping SRC/OUT. Does NOT touch the canonical
# Perspective-First-Draft.{md,pdf}.
import make_pdf

DRAFT_LINE = "*Draft. Day 165.*"
src = open("Perspective-First-Draft.md", encoding="utf-8").read()
lines = src.split("\n")
kept = [l for l in lines if l.strip() != DRAFT_LINE]
removed = len(lines) - len(kept)
open("Perspective-Reader.md", "w", encoding="utf-8", newline="\n").write("\n".join(kept))
print(f"removed {removed} line(s) matching the draft memo")

make_pdf.SRC = "Perspective-Reader.md"
make_pdf.OUT = "Perspective.pdf"
make_pdf.main()
