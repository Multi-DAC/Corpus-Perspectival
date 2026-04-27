# *Coherent Structure* — Scope Contract

*Rolling document. Updated as the formalization proceeds. Companion versions stamp when the flag-list goes to zero.*

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
- **§4 Corollary clusters** — 15 corollaries in four clusters (Cluster IV added 2026-04-27 with C14 Two-Mode Symmetry-Breaking + C15 Intervention-at-Symmetry-Layer), full proofs
- **§5 The Coherence Principle** — formal statement
- **§6 Identity-Trajectory Triple** — TC1/TC2/TC3 intensional construction; colax-limit theorem
- **§7 Filtering construction** — σ-algebra on Ω_S; extensional (σ_F, K_F, Ω_F, γ_F); Bias(S) well-definedness
- **§8 F-as-stream** — self-reference closure, full construction
- **§9 D trajectory-divergence** — functional construction per anchor §9.9 Q1
- **§10 Reference figures** — TikZ standard set; imported by the anchor
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

The Companion is a **rolling document** during the current phase. Anchor revisions can land Companion-citing content without waiting on a Companion version bump. The Companion stamps a version when §8's flag-list goes to zero via any combination of the four dispositions in §8.2.

**v0.1 stamped 2026-04-24** (Day 83). 40 flags dispositioned: 12 ALREADY-LANDED, 26 REFERENCE-NATIVE, 2 SCOPE-EXCLUDED (→ Universal Coherence), 0 BACK-PORT. Anchor stays at 267pp — no revision triggered by v0.1. Audit log: `drafts/2026-04-24-v0.1-flag-audit.md`.

## 8. Surfaced-lemma lifecycle

When full CT formalization surfaces a lemma or corollary that is latent in the anchor but not stated there, it lands in the Companion with a flag:

```
⚑ [SURFACED 2026-MM-DD | Companion §X.Y | → Anchor §Z target | type: lemma/corollary]
```

**Four fields:**
- **SURFACED 2026-MM-DD** — date the item surfaced during formalization
- **Companion §X.Y** — where the item lives in the Companion
- **→ Anchor §Z target** — the anchor section it should back-port into (or disposition marker per §8.2 below)
- **type** — lemma / corollary / theorem / proposition / definition-and-conjecture

### 8.1 Original three-phase lifecycle (default path)

1. **Surface:** CT formalization surfaces the item → flagged in the Companion as above
2. **Back-port:** Next anchor revision incorporates the flagged items; anchor rev_N+1 ships
3. **Clear:** Companion cleanup pass removes flags whose items now live in the anchor; when flag-list reads zero, Companion version_N stamps

The flag-count is the Companion's version-ready signal: **zero flags = version-stampable**.

### 8.2 Four-disposition extension *(added 2026-04-24 Day 83)*

Experience through the Day-78 → Day-83 formalization pass (anchor stamp 2026-04-20; §1.10 + §3.8 landings 2026-04-23; §6.10 F-coalgebra integration 2026-04-24) revealed that not every surfaced item is structurally awaiting back-port. Some items have already landed in a prior anchor revision; some are Companion-native formal content whose anchor counterpart is at a coarser-than-item granularity (or is structurally unnecessary); some belong to other Library volumes. The three-phase lifecycle in §8.1 remains the default; the extension supplies four terminal dispositions through which any given flag can clear.

**The four dispositions:**

| Disposition | Meaning | Clearance action |
|---|---|---|
| **BACK-PORT** | Item needs anchor prose counterpart that does not yet exist. | Anchor revision rev_N+1 absorbs the item. Flag clears on next Companion cleanup pass after rev_N+1 ships. (The §8.1 default path.) |
| **ALREADY-LANDED** | Item's corresponding anchor material already exists in the current stamped anchor. | Audit to confirm anchor location; add or update AppendixB row; remove flag in-place. No anchor revision needed. |
| **REFERENCE-NATIVE** | Item is Companion-original formal content whose anchor-prose counterpart is at coarser granularity (a section-level claim the item makes precise) or is structurally not required (the item is pure CT machinery internal to the Companion). | Reclassify: keep item in place as Companion text; add AppendixB row citing the coarse-grain anchor location (or explicitly marking "Companion-native — no finer anchor target"); remove flag. |
| **SCOPE-EXCLUDED** | Item belongs to a different Library volume (Universal Coherence, a domain volume, The Killing Form, etc.). | Move item's content to the target volume's drafts / research folder with a crosswalk pointer; remove from Companion; remove flag. |

**Disposition-assignment protocol:**

Each flag's disposition is assigned during an **audit pass** that can be performed on demand (not only at cleanup). For each flag, the audit records: disposition, clearance-action taken, date, and — for REFERENCE-NATIVE flags — the rationale (why the anchor's coarser-grain coverage is sufficient, or why the item is structurally pure Companion-machinery).

**Clearance-count semantics:**

The stamp-ready condition is unchanged: **zero flags = version-stampable**. The extension widens the paths to zero. A Companion version-stamp after an audit-and-clearance pass reports the disposition breakdown in its changelog (e.g., *v0.1 stamp cleared N flags: A BACK-PORT via anchor rev_N+1, B ALREADY-LANDED, C REFERENCE-NATIVE, D SCOPE-EXCLUDED*).

**Why this extension preserves the contract.** The §2 done-enough criterion is unchanged: every CT sketch in the anchor has a corresponding full CT development in the Companion, and a mathematician reading the Companion alone can verify the formal structure. The extension records, for each piece of Companion content, *how* that content relates to the anchor — whether as a back-port target, as an already-anchored claim, as a Companion-native refinement, or as out-of-scope-here-but-anchored-in-sibling-volume. Coherence between the two volumes is maintained by documented disposition for every flag.

**Structural backing (added 2026-04-24 afternoon, post-v0.1).** The four-disposition taxonomy is not ad-hoc. The first three dispositions instantiate **M12 (Form-Register Stratification by Adjunction-Residue)** at the volume-pairing register: ALREADY-LANDED ↔ Strong stratum (η identity-ish; round-trip lossless), BACK-PORT ↔ Convergent stratum (residue decays under anchor-revision dynamics), REFERENCE-NATIVE ↔ Structural stratum (permanent non-trivial cokernel — Anchor's coarse-grain prose carries the section-level claim, not the Companion's lemma-level CT machinery; no decay-dynamics available). SCOPE-EXCLUDED is register-orthogonal — item is in a different volume's adjunction. The §8.2 lifecycle is the **default template** for any paired-volume relationship in the Library; domain volumes paired with Foundation should exhibit the same lifecycle by M12-implication. See `palace/basement/README.md` M12 entry and `Research/basement-drafts/2026-04-24-M12-at-volume-pairing-register.md`.

## 9. Figure back-port policy

The Companion is the **figure authority**. New standardized TikZ figures are produced in §10 of the Companion; the anchor imports them from the Companion source. One source of truth.

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
