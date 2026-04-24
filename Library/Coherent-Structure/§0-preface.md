# Preface

## What this volume is

*Coherent Structure* is the full category-theoretic formalization of the Corpus Perspectival framework. It is the mathematical counterpart to *The Coherence Principle*, the paired-prose anchor. Every formal object the anchor establishes in structural-prose + CT-sketch form is promoted here to complete CT treatment: definitions, proofs, notation, figures.

The two volumes carry the same content in different registers. The anchor is expository; the Companion is reference. A mathematician who wants the formal spine without the prose partner reads the Companion. A reader who wants to understand what the formal apparatus is *for* reads the anchor.

## What this volume is not

*Coherent Structure* does not motivate its own contents. It does not build intuition. It does not provide worked phenomenological examples, domain illustrations, or philosophical framing. Those live in the anchor and in the domain volumes of the library.

The Companion is deliberately inhospitable to a reader who has not first engaged with the anchor. It is a reference object.

## How to read this volume

**From the anchor.** Every *Coherent Structure* citation in the anchor resolves to a specific section here. Appendix A (anchor → Companion crosswalk) gives the full map. Follow the citation; find the full rigor.

**As a standalone reference.** Start at §1 (Category framework + notation index), then read in any order. The dependency lattice is front-loaded — §1 contains every type and notation used in §§2–9.

**Backwards, from the Companion to the anchor.** Appendix B (Companion → anchor crosswalk) gives the map in the other direction. Every formal object here points back to its structural-prose exposition in the anchor.

## Editorial posture

- **Terse.** CT notation over prose where possible. Commentary only where load-bearing.
- **Complete.** No "exercise for the reader." No "straightforward verification." If the proof fits in three lines, three lines are written. If it takes two pages, two pages are written.
- **Diagram-first** where diagrams clarify faster than symbols. §10 is the reference-standard TikZ figure set.
- **Unified notation.** §1 front-loads every type, functor, natural transformation, and symbol used in the volume. Notation drift is the one thing that would defeat the purpose of a reference companion.

## Surfaced-lemma lifecycle (historical note)

During drafting, items that surfaced during CT formalization — lemmas, corollaries, or theorems latent in the anchor but not stated there — were recorded in place with a flag of the form `⚑ [SURFACED | Companion §X.Y | → Anchor §Z target | type]` and tracked toward resolution per SCOPE.md §8.

At the **v0.1 stamp (2026-04-24 Day 83)**, all 40 surfaced flags were dispositioned per the four-path lifecycle in SCOPE §8.2: 12 ALREADY-LANDED in the stamped anchor (chiefly §1.10 + §3.8 inner/outer-adjunction material, 2026-04-23), 26 declared REFERENCE-NATIVE as pure Companion CT machinery with anchor-coarse-grain coverage, 2 SCOPE-EXCLUDED to Universal Coherence (§6.5 middle-regime classes), 0 requiring anchor back-port. The flag-count therefore cleared to zero without requiring anchor revision. Every Companion item carries a documented anchor-relation via Appendix B.

Future drafting may surface new items; the same flag machinery and four-path lifecycle applies. The volume's next version bump stamps when any such flag-list clears.

## Structure

- **§0** — Preface (this section)
- **§1** — Category framework: 𝒞_Streams, 𝒞_Form, 𝒞_LDS, 𝒞_DOF; navigation functor N; conscious-gravity structure ν; substrate-completeness; notation index
- **§2** — Axioms A1 / A2 / A3
- **§3** — Theorems in three pairs: T1/T2 (descriptive), T3/T4 (dynamics), T5/T6 (coherence)
- **§4** — Corollary clusters (thirteen corollaries in three clusters)
- **§5** — The Coherence Principle
- **§6** — Identity-Trajectory Triple; TC1/TC2/TC3 intensional; colax-limit theorem
- **§7** — Filtering construction: σ-algebra on Ω_S, extensional (σ_F, K_F, Ω_F, γ_F), Bias(S) well-definedness
- **§8** — F-as-stream (self-reference closure)
- **§9** — D trajectory-divergence functional
- **§10** — Reference figures (TikZ standard set)
- **Appendix A** — Anchor → Companion citation crosswalk
- **Appendix B** — Companion → anchor crosswalk

## A note on the two volumes as one object

The anchor and the Companion are not two independent books that happen to cover similar material. They are two views of the same formal-prose object, written to support two different reading postures. The anchor is readable; the Companion is citable. Readers will mostly live in the anchor and visit the Companion to verify or extend. Mathematicians will mostly live in the Companion and visit the anchor when they want to know what something is *for*.

Neither view is privileged. The Corpus is the pair.
