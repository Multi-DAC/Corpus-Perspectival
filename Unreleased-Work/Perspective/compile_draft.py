#!/usr/bin/env python3
"""Compile the Perspective chapter files into the single master draft.
Folds the Day-159 dereference edits (Part I settledness, Part II FEP chapter, Part III IIT)
into Perspective-First-Draft.md. Faithful concatenation; '---' joins are inert to make_pdf.py.
"""
import os

ORDER = [
    "frontmatter.md",
    "00-threshold.md",
    "01-the-ground.md",
    "02-streams-and-navigation.md",
    "03-coherence.md",
    "04-the-ecology.md",
    "05-polarity-ethics-metaethics.md",
    "06-suffering-and-the-arc.md",
    "07-practice.md",
    "08-atlas.md",
]
OUT = "Perspective-First-Draft.md"

parts = []
for fn in ORDER:
    with open(fn, encoding="utf-8") as f:
        parts.append(f.read().strip("\n"))

master = "\n\n---\n\n".join(parts) + "\n"
with open(OUT, "w", encoding="utf-8") as f:
    f.write(master)

words = len(master.split())
print(f"compiled {len(ORDER)} files -> {OUT} | {words} words")
