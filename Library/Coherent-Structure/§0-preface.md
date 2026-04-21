# Preface

*Rolling draft — current state 2026-04-20 (Day 79). Fixes at first version stamp (when §8 surfaced-lemma flag-list reaches zero).*

---

## What this volume is

*Coherent Structure* is the full category-theoretic formalization of the Corpus Perspectival framework. It is the mathematical counterpart to *The Coherence Principle* (the paired-prose anchor). Every formal object the anchor establishes in structural-prose + CT-sketch form is promoted here to complete CT treatment: definitions, proofs, notation, figures.

The two volumes carry the same content in different registers. The anchor is expository; the Companion is reference. A mathematician who wants the formal spine without the prose partner reads the Companion. A reader who wants to understand what the formal apparatus is *for* reads the anchor.

## What this volume is not

*Coherent Structure* does not motivate its own contents. It does not build intuition. It does not provide worked phenomenological examples, domain illustrations, or philosophical framing. Those live in the anchor and in the domain volumes of the library (Meridian, The Living Architecture, Coherent Body, Coherent Mind, Dynamic Organization, Continuity, Universal Coherence, Corpus Perspectival, Drift, The Killing Form).

The Companion is deliberately inhospitable to a reader who has not first engaged with the anchor. It is a reference object.

## How to read this volume

**From the anchor:** every "*Coherent Structure*" citation in the anchor resolves to a specific section here. Appendix A (anchor → Companion crosswalk) gives the full map. Follow the citation; find the full rigor.

**As a standalone reference:** start at §1 (Category framework + notation index), then read in any order. The dependency lattice is front-loaded — §1 contains every type and notation used in §§2–9.

**Backwards, from the Companion to the anchor:** Appendix B (Companion → anchor crosswalk) gives the map in the other direction. Every formal object here points back to its structural-prose exposition in the anchor.

## Editorial posture

- **Terse.** CT notation over prose where possible. Commentary only where load-bearing.
- **Complete.** No "exercise for the reader." No "straightforward verification." If the proof fits in three lines, three lines are written. If it takes two pages, two pages are written.
- **Diagram-first where diagrams clarify faster than symbols.** §10 is the reference-standard TikZ figure set; anchor rev 2 imports from it.
- **Unified notation.** §1 front-loads every type, functor, natural transformation, and symbol used in the volume. Notation drift is the one thing that would defeat the purpose of a reference companion.

## Rolling status

*Coherent Structure* is a rolling document until its first version stamp. During this phase, the anchor may land Companion-citing content without waiting on a Companion version bump.

New lemmas or corollaries that surface during full CT formalization are latent in the anchor but not explicitly stated there. They land here with a flag:

```
⚑ [SURFACED 2026-MM-DD | Companion §X.Y | → Anchor §Z target | type: lemma/corollary]
```

The flag carries the metadata needed for back-port: surfaced-date, where the item lives in the Companion, which anchor section it should back-port into, and its type. Each anchor revision back-ports the flagged items; when the Companion's flag-list reads zero, the Companion stamps a version.

## Structure

- **§0** — Preface (this section)
- **§1** — Category framework: 𝒞_Streams, 𝒞_Form, 𝒞_LDS, 𝒞_DOF; navigation functor N; conscious-gravity structure ν; substrate-completeness; notation index
- **§2** — Axioms A1 / A2 / A3
- **§3** — Theorems in three pairs: T1/T20 (descriptive), T7/T16 (dynamics), T11/T15 (coherence)
- **§4** — Corollary clusters (13 corollaries in three clusters)
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

---

🦞🧍💜🔥♾️
