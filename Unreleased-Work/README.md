# Unreleased-Work — the active writing desk

Drafts, papers in preparation, and their working materials (figures, figure-scripts, reviewer responses, build helpers). Things **graduate out** of here — to the Library, to Research, or to the public web (Substack, Zenodo, PhilArchive). Nothing should live here permanently.

The files sit flat (no subfolders yet) because each paper is a small cluster that moves together. Here's what's actually in the drawer, grouped by paper:

## Papers & their materials

- **The Curvature of Good and Evil** (the "Ouroboros" article — **published** 2026-06-19 on Substack)
  `ouroboros-*` — the draft, all figures (`*-fig-*.png` + their `.py` generators), results notes (`*-RESULTS-*.md`), the Hopf/SNIC analyses, and three rounds of reviewer responses. The richest cluster here; kept as the article's full provenance.

- **One Room, Many Keyholes** (cross-channel invariance — **published**)
  `one-room-many-keyholes.{md,html,pdf,tex}` — draft + rendered outputs.

- **Place-Threshold Mechanism** (the portal/dark-energy-scalar paper — **published** as "Where the Ordinary Rules Go Thin")
  `place-threshold-mechanism.{md,html,pdf,tex}` + `bouguer.xyz.gz` (gravity data).

- **Coupling-Textured Consciousness** (the C17 / "Different Containers" paper — **in progress**)
  `coupling-textured-consciousness-{DRAFT,SPINE}-2026-06-20.md`.

- **Q-ball existence** (supporting the portal program — **in progress**)
  `canonical-qball-existence-*.py`, `dynamical-qball-breathing-*.py`.

## Build helpers
`make_pdf.py`, `make_portal_pdf.py` — LaTeX/HTML→PDF render scripts (referenced by relative filename, so the files stay flat alongside them).

---
*Note: several of these are **published** — their materials live on here as provenance/archive rather than as pending work. When a paper is fully wrapped, its cluster can graduate to the relevant Library volume's folder or to Research. Grouping into per-paper subfolders is possible later, but the build scripts use relative paths, so that's a deliberate move, not a casual one.*
