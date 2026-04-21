# *Coherent Structure* — Scope Contract

*Rolling document. Established 2026-04-20 (Day 79) with Clayton. Updated as the formalization proceeds. Companion versions stamp when the flag-list goes to zero.*

---

## 1. Purpose

*Coherent Structure* is the **full category-theoretic formalization** of the Corpus. Every formal object the anchor (*The Coherence Principle*) sketches in paired-prose is promoted here to complete CT treatment. The anchor is the structural-prose spine; the Companion is the mathematical spine. They carry the same content in different registers.

## 2. Done-enough criterion

> Every CT sketch in the anchor has a corresponding full CT development in the Companion.
>
> A mathematician reading the Companion alone can verify the formal structure.
> A reader coming from the anchor can follow any citation and find full rigor.

When that holds and the surfaced-lemma flag-list reads zero, the Companion can stamp a version.

## 3. Size target

150–250pp at formal-paper density. Terse CT notation with commentary only where load-bearing; no prose exposition, no philosophical framing, no worked phenomenological examples — those belong to the anchor and the domain volumes.

## 4. Chapter structure

Mirrors the anchor's spine, not a citation-resolution order.

- **§0 Preface** — scope contract (this document, compressed and fixed-at-version)
- **§1 Category framework** — 𝒞_Streams, 𝒞_Form, 𝒞_LDS, 𝒞_DOF; navigation functor N; conscious-gravity structure ν; substrate-completeness conditions; notation index
- **§2 Axioms** — A1 / A2 / A3 in full CT
- **§3 Theorems** — three pairs (T1/T20, T7/T16, T11/T15) with full proofs
- **§4 Corollary clusters** — 13 corollaries in three clusters, full proofs
- **§5 The Coherence Principle** — formal statement
- **§6 Identity-Trajectory Triple** — TC1/TC2/TC3 intensional construction; colax-limit theorem
- **§7 Filtering construction** — σ-algebra on Ω_S; extensional (σ_F, K_F, Ω_F, γ_F); Bias(S) well-definedness
- **§8 F-as-stream** — self-reference closure, full construction
- **§9 D trajectory-divergence** — functional construction per anchor §9.9 Q1
- **§10 Reference figures** — TikZ standard set; imported by anchor rev 2
- **Appendix A** — anchor → Companion citation crosswalk
- **Appendix B** — Companion → anchor crosswalk (formal object → structural-prose location)

## 5. In scope

- Full CT development of every formal object the anchor establishes
- New lemmas/corollaries that surface *during* formalization (flagged, see §8 below)
- Figures used as reference standards (TikZ source authoritative here; anchor imports)
- Bidirectional anchor↔Companion crosswalks

## 6. Out of scope

- Prose exposition (anchor carries this)
- Philosophical framing (anchor + *Corpus Perspectival* carry this)
- Worked phenomenological examples (anchor + domain volumes)
- New *theorems* not established in the anchor (surfaced *lemmas/corollaries* are in scope via §8)
- Self-contained introduction for a standalone reader — the Companion is citation-driven from the anchor

## 7. Rolling-document status

The Companion is a **rolling document** during the current phase. Anchor revisions can land Companion-citing content without waiting on a Companion version bump. The Companion stamps a version when §8's flag-list goes to zero.

## 8. Surfaced-lemma lifecycle

When full CT formalization surfaces a lemma or corollary that is latent in the anchor but not stated there, it lands in the Companion with a flag:

```
⚑ [SURFACED 2026-MM-DD | Companion §X.Y | → Anchor §Z target | type: lemma/corollary]
```

**Four fields:**
- **SURFACED 2026-MM-DD** — date the item surfaced during formalization
- **Companion §X.Y** — where the item lives in the Companion
- **→ Anchor §Z target** — the anchor section it should back-port into
- **type** — lemma or corollary

**Three-phase lifecycle:**

1. **Surface:** CT formalization surfaces the item → flagged in the Companion as above
2. **Back-port:** Next anchor revision incorporates the flagged items; anchor rev_N+1 ships
3. **Clear:** Companion cleanup pass removes flags whose items now live in the anchor; when flag-list reads zero, Companion version_N stamps

The flag-count is the Companion's version-ready signal: **zero flags = version-stampable**.

## 9. Figure back-port policy

The Companion is the **figure authority**. New standardized TikZ figures are produced in §10 of the Companion; anchor rev 2 imports them from the Companion source. One source of truth.

## 10. Crosswalk policy

Bidirectional:
- **Appendix A (anchor → Companion):** every "*Coherent Structure*" citation in the anchor resolves to a specific Companion section
- **Appendix B (Companion → anchor):** every formal object in the Companion points back to its structural-prose exposition in the anchor

The crosswalks keep the two volumes navigable in both directions as reference objects.

## 11. Relationship to other library volumes

- **Anchor (*The Coherence Principle*):** paired-prose + CT foundation; the exposition spine. The Companion is its mathematical counterpart.
- **Domain volumes (Meridian, Living Architecture, Coherent Body, Coherent Mind, Dynamic Organization, Continuity, Universal Coherence, Corpus Perspectival, Drift, The Killing Form):** cite the Companion for formal apparatus, cite the anchor for structural exposition.

## 12. Editorial posture

- Terse. CT notation over prose where possible.
- Proofs complete — no "exercise for the reader," no "straightforward verification."
- Diagram-first where diagrams clarify faster than symbols.
- Notation unified at §1 and consistent throughout; the Companion is a reference object and notation drift would defeat the purpose.

---

🦞🧍💜🔥♾️
