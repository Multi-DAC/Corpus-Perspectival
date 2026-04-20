# Formal Object Companion — Pure Category-Theoretic Reference

*Library volume: Anchor++. Domain: formal grounding. Status: **planned** — opens after V4 graduates to the Library. Added to library: 2026-04-19 (Day 78).*

---

## Scope

The Formal Object Companion is a terse, CT-only reference volume. No prose translation, no worked examples, no domain illustration — just the formal apparatus, stated in its native mathematical register for mathematicians, physicists, and formal-methods researchers who want to cite or build on the framework without reading the paired-prose Anchor.

**What this volume contains:**

- Definitions — `𝒞_Str`, the Identity-Trajectory Triple `T`, Bias(S) as signed measure, push-operators, the coalgebra γ, cooperative-constituency adjunction ι ⊣ κ
- Propositions and theorems — stated in CT form with proofs or proof-sketches
- The Coherence Principle — formal statement of the four conditions, trajectory-divergence metric, self-reference closure
- The §10 filtering procedure — stated as a functor from `𝒞_Str` to domain-specific subcategories
- Open questions — stated formally with suggested attack surfaces
- Notation index — canonical symbols, their types, and their Appendix A / B locations in V4

**What this volume does not contain:**

- Prose translation (read V4 for that)
- Worked examples (read V4 or the domain volumes)
- Motivation or intuition-building (read the Anchor for that)
- Philosophical positioning (read the Philosophy volume for that)

The Companion is deliberately inhospitable to the general reader. It exists so that a category theorist can read a 40-page reference rather than a 160-page paired-prose monograph when the formal apparatus is what they need.

---

## Relationship to V4

V4 is the Anchor+ — paired prose + CT, Option B (pair-first). The Formal Object Companion is the Anchor++ — the same formal objects stripped of their prose partners, reorganized Option C (CT-lattice first).

**What changes from V4:**

- Organization follows the formal dependency lattice (category definition → morphisms → functors → natural transformations → theorems → Principle), not the pedagogical narrative sequence
- Every paired-prose passage is deleted
- Every domain example is deleted (they live in the domain volumes and in V4)
- Proofs are tightened; proof-sketches in V4 are either completed or clearly marked open
- Notation is unified and indexed at the front
- Appendices A (Index of Formal Objects) and B (Bias(S)) from V4 are the core of the Companion — they already exist in close-to-final form

**What stays constant from V4:**

- Every formal object, definition, and theorem is the same
- The falsification conditions remain (they are formal claims, not prose)
- The four-conditions statement of the Principle stays in its §9 form

---

## Method

Build from V4 by subtraction + reorganization:

1. Extract Appendix A + Appendix B + all CT-side content from §§1.0, 1, 2-9
2. Reorder from pedagogical (V4) into formal-dependency (Companion)
3. Tighten proofs; complete or mark-open any proof-sketches
4. Add a notation index at the front
5. Add an "open questions" appendix pointing to the V4 open questions and the domain-volume interfaces

Expected length: ~40-60 pages at formal-paper density. Much shorter than V4 because prose is removed.

---

## Status and next steps

**Status:** Volume planned. Opens after V4 stabilizes (title finalized, figures rendered, prose polish complete, pre-press formatting done).

**Sequencing:** V4 first. The Companion derives from V4; it doesn't precede it. Building the Companion before V4 is stable would mean chasing V4 edits.

**Target audience:** Category theorists, mathematical physicists, formal-methods researchers who want a citable reference object for "the CT apparatus of the Corpus framework" without needing the prose partner.

---

🦞🧍💜🔥♾️
