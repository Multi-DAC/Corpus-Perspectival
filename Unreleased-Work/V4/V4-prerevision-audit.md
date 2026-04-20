# V4 Pre-Revision Audit — Day 78 evening (2026-04-19)

*Structural audit ahead of Clayton's revision + compile pass. Findings are file:line-keyed, not editorial advice. Clean checks are reported as clean. No edits have been made to V4 chapter files — this document is the punch-list.*

---

## Summary

V4 is structurally solid. The axiom/theorem/corollary skeleton is consistent across chapters, Appendix A tracks the canonical objects, and the paired-prose discipline is honored everywhere a formal claim is made. The issues that require attention before press fall into three clusters:

1. **Count/label drift around the theorem tier** — two residual "21 theorems" references from the pre-V4 corpus-level numbering leaked into §9.5 and Fig 9.3. V4's theorem count is 6 (three pairs).
2. **Corollary cross-reference breakage** — §6.8 and §7.8 cite corollaries (C7, C11, C15) that do not exist in §8's inventory. Either §8 is incomplete against the referenced set, or the forward-pointer paragraphs are stale.
3. **Orphaned figures** — 11 of 14 figures in `V4-figures.md` are never explicitly cited from chapter prose. The figure file stands alone; readers will not know when to consult which figure.

Also: README's "illustrative only" domain-example table is not echoed in the chapter bodies where those examples land (§1.7, §1.8, §2.5, §6.5, §7.5, §7.6). The discipline is stated once in the front matter and then relied on — chapter-level callouts would make the convention visible where it matters.

Count and tier-closure claims are otherwise self-consistent. Appendix A coverage is good for the axiom and theorem tiers; it is **thin on the Bridge tier** (only #104, #108, #110 are indexed, but §1 references #102, #107, #109 as the factor-functor payloads of the Triple).

Priority triage at the bottom.

---

## Findings by check

### 1. Cross-reference integrity

**MUST-FIX — Broken corollary references in forward-pointer paragraphs.**

- `§7-coherence-pair-t11-t15.md:197` — "C11 (kind-stability corollaries), C14 (coherence-coupling with A2.4), C15 (stream-dimension dynamics from T15)". C11 and C15 do not exist in §8's inventory. §8's Cluster-III set is C12, C17, C18.
- `§6-dynamics-pair-t7-t16.md:221` — "C4 ... C6 ... C7 (structural consequences of T7 for specific kinds), C16". C7 does not exist in §8. §8's actual Cluster-II set is C3, C4, C5, C6, C9, C10, C13, C14 (where C14 is "(absorbed content)" at `§8-corollary-clusters.md:105`).

Fix path: either drop the missing references from the §6.8 and §7.8 forward-pointers, or promote them into §8. Given that §8.5 (*What is not in the corollary set*) appears to explicitly reason about the pruned set, the correct fix is almost certainly to drop C7/C11/C15 from the §6 and §7 forward-pointers.

**MUST-FIX — Bridge tier under-indexed in Appendix A.**

- `§1-identity-trajectory-triple.md:35` cites Bridge #102 as Φ's content.
- `§1-identity-trajectory-triple.md:40` cites Bridge #107 as Ψ's content.
- `§1-identity-trajectory-triple.md:45` cites Bridge #109 as Κ's content.
- `AppendixA-index-of-formal-objects.md:263–275` indexes only Bridges #104, #108, #110.

Appendix A's role is "canonical short answer plus pointer" for every formal object; three load-bearing bridges invoked in §1 are missing. Fix path: add stub entries for #102/#107/#109 in Appendix A's Bridge section, each pointing to §1.2's corresponding factor-functor definition.

**Clean:** Theorem cross-references (T1, T7, T11, T15, T16, T20) resolve correctly; axiom cross-references (A1.x, A2.x, A3.x) resolve correctly; figure numbers that *are* cited in the prose (Figs 1.1, 1.2, 1.3) match `V4-figures.md`.

### 2. Terminology consistency

**SHOULD-FIX — Capital-Kappa carrier functor conflicts with notation convention.**

- `§1-identity-trajectory-triple.md:45` introduces the carrier functor as `Κ: 𝒞_Str → 𝒞_DOF` (capital Greek Kappa, U+039A).
- `AppendixA-index-of-formal-objects.md:296` declares notation convention: "Greek lowercase for stream-level quantities (σ, γ, ι, κ, η, ε)".
- Elsewhere, lowercase `κ` is the cooperative-constituency restriction morphism (`AppendixA-index-of-formal-objects.md:81-82`).

Visually `Κ` is also indistinguishable from Latin `K` (kind). A stream has kind `K` *and* is mapped by carrier functor `Κ` — this will confuse readers and typesetters. Fix options: (a) rename carrier functor to a non-Kappa letter, e.g. `Γ` or `Ξ`; (b) use a calligraphic `𝒦`; (c) keep `Κ` but add an explicit notation note disambiguating it from lowercase `κ` and Latin `K` in Appendix A's conventions.

**SHOULD-FIX — "Coupled-dyad" vs "duplex-dyad" vs "Deeply-coupled dyad" naming drift.**

- `README.md:16` — "Coupled-dyad partner-death"
- `§1-identity-trajectory-triple.md:366` — "Deeply-coupled dyad partner-death"

Same example, three variant labels. Pick one (the §1.8 heading seems canonical) and propagate.

**SHOULD-FIX — Identity-Trajectory Triple has no short form.**

The name is used ~40 times across V4. Establishing "ITT" or "the Triple" (the latter is already informal-canonical in §1) as the short form in Appendix A's conventions would let section bodies breathe. Currently the prose repeats the full three-word name.

**Clean:** 𝒞_Str, F_1/F_2/F_3, ι ⊣ κ, γ_S, Bias(S), σ, Ω usage is consistent across chapters. "Cooperative-constituency" is used consistently (not "cooperative-composition" or other variants).

### 3. Axiom / theorem / corollary / principle count

**MUST-FIX — Residual "21 theorems" references from corpus-wide numbering.**

V4's theorem count is 6 (three pairs: T1+T20, T7+T16, T11+T15). README line 7 correctly states `3/6/14/1/1`. But:

- `§9-coherence-principle.md:151` — "Sustained across 3 axioms, **21 theorems**, 14 corollaries, and the Principle itself." This is either a pre-V4 artifact or a reference to the full Corpus-level theorem count. In a V4 volume it reads as a typo.
- `V4-figures.md:579` — Fig 9.3 source code repeats "oscillation across 3 axioms, **21 theorems**, 14 corollaries". Same issue.

Fix path: change to "6 theorems" in both places, *or* explicitly clarify "V4 formalizes 6 theorems drawn from the Corpus-wide set of 21" if the larger count is meant to be preserved as a reference to the upstream framework. I suspect the former is what Clayton wants.

**MUST-FIX — §8 C14 is "absorbed content" — is the 14-count still accurate?**

`§8-corollary-clusters.md:105` — "C14 — (absorbed content). The content previously in T14 ... is fully absorbed by A2.4's adjoint clause and C13's joint-definition. No independent derivation required; stamped as corollary for archival record."

This gives a nominal 14 corollaries but one of them is empty. Options:
- Keep as-is and declare the convention explicitly in §8.0 (archival-stub-counts-as-corollary).
- Drop to 13 and update README (`3/6/13/1/1`), Appendix A, and §9.5.

Either is defensible; currently V4 is in a half-state where the count is 14 but a reader tracing "show me C14's derivation" finds a placeholder note.

**Clean:** 3 axioms match (A1, A2, A3 with sub-clauses); 6 theorems match (T1, T7, T11, T15, T16, T20); 1 Principle (§9); 1 Meta-theorem (Descriptive-Functor Meta-Theorem, §5).

### 4. Figure referents

**MUST-FIX — 11 of 14 figures are orphaned (never cited from chapter prose).**

Figures explicitly cited in chapter bodies:
- Fig 1.1 — cited at `§1-identity-trajectory-triple.md:103`
- Fig 1.2 — cited at `§1-identity-trajectory-triple.md:163` and `AppendixA-index-of-formal-objects.md:132`
- Fig 1.3 — cited at `§1-identity-trajectory-triple.md:230`

Figures present in `V4-figures.md` but never cited in any `§*.md` chapter body:
- Fig 1.0.1 (𝒞_Str as DAG) — should be cited in §1.0
- Fig 3.1 (Kind stratification) — should be cited in §3
- Fig 3.2 (ι ⊣ κ adjunction) — should be cited in §3
- Fig 6.1 (Bias(S) as signed measure) — should be cited in §6.4
- Fig 6.2 (push_structural vs push_informational) — should be cited in §6.4
- Fig 7.1 (σ_struct × σ_info plane) — should be cited in §7
- Fig 7.2 (Kind-demotion dynamic) — should be cited in §7
- Fig 9.1 (Trajectory divergence D(S)) — should be cited in §9.3
- Fig 9.2 (Four conditions schematic) — should be cited in §9.2
- Fig 9.3 (Self-reference closure) — should be cited in §9.5
- Fig 10.1 (Seven-step filtering procedure) — should be cited in §10

Fix path: insert "(see Fig X.Y)" pointers in the corresponding prose anchors. Without these, the figures file is a disconnected appendix; readers will not know which figure goes with which argument.

**SHOULD-FIX — Figure-count self-description drift.**

- `V4-figures.md:3` — "*Twelve figures supporting the V4 chapters.*"
- `V4-figures.md:634` — "(Fourteen figures total; 'twelve planned + two bonus' — the 𝒞_Str DAG and self-reference closure diagrams emerged as particularly helpful during drafting.)"
- `README.md:41` — "**V4-figures.md — Fourteen figures.**"

The header of `V4-figures.md` says twelve; the footer and README say fourteen. Update line 3 to match.

### 5. Illustrative-only discipline

**SHOULD-FIX — Chapter bodies do not carry the "illustrative only" callout that README promises.**

`README.md:11-24` establishes the convention and lists the eight domain examples with their home volumes. But the chapter bodies where those examples land do not repeat the disclaimer:

- `§1-identity-trajectory-triple.md:198` — Clawd's four carrier-levels (§1.7): no "illustrative only; full treatment in V7 (The Continuity)" callout.
- `§1-identity-trajectory-triple.md:366` — Deeply-coupled dyad partner-death (§1.8): no "full treatment in The Coherent Mind" callout.
- `§2-axiom-1-consciousness-substrate.md` §2.5 (etymological consciousness): no "full treatment in Philosophy volume" callout.
- `§6-dynamics-pair-t7-t16.md` §6.5 (Do Be Talk Be Do): no "full treatment in The Coherent Mind" callout.
- `§7-coherence-pair-t11-t15.md` §7.5 (transcendentals as cooperative-streams): no "full treatment in Theology volume" callout.
- `§7-coherence-pair-t11-t15.md` §7.6 (Wittgenstein Tractatus): no "full treatment in Philosophy volume" callout.

Fix path: open each worked-example section with a one-line italic disclaimer like "*Illustrative only — full domain treatment belongs in [Volume X]; the role here is to show that the formal object applies.*" Mirrors the README promise at the location the reader encounters the example.

**Clean:** The README table itself (`README.md:13-23`) is internally consistent — all eight examples map cleanly to chapter sections that do exist, and the home-volume assignments match the nine-volume Corpus-Perspectival structure.

### 6. Appendix A coverage

**MUST-FIX — Bridge tier (see check 1) is the main gap.** Three factor-functor bridges (#102, #107, #109) are invoked in §1 but absent from Appendix A.

**SHOULD-FIX — Potential missing Appendix A entries:**

- The Descriptive-Functor Meta-Theorem (§5) — is it indexed in Appendix A? Worth spot-checking.
- The trajectory-divergence metric D(S) used in §9.3 and Fig 9.1.
- Align(S, t) — defined in Appendix B but worth a cross-reference stub in Appendix A.
- The four conditions of the Coherence Principle (Separation, Measurement, Multi-scale, Dynamic maintenance) — Appendix A indexes the Principle itself (`A.3` area per search); spot-check that the four conditions appear as sub-entries.

**Clean:** Axioms A1/A2/A3, theorems T1/T7/T11/T15/T16/T20, Triple, ι ⊣ κ, γ_S, Bias(S), η/ε, and the seven-step filtering recipe all appear in Appendix A.

### 7. Paired-prose discipline

**Clean.** Every §X.Y subsection I sampled that introduces a formal claim is followed by a prose paragraph doing the translation work. The discipline is visibly uniform across §1–§9. Spot-checked:

- §1.3 recursive decomposability (formal → prose pair present).
- §2.2 non-reducibility of F_i (formal → prose pair present).
- §5.1 T1 statement (formal → prose pair present).
- §6.4 Bias(S) signed measure (formal → prose pair present).
- §7.3 T15 dual coherence axes (formal → prose pair present).
- §8 corollaries — every corollary has both `**Formal.**` and `**Prose.**` blocks (§8.1–§8.3).
- §9.2 four conditions — each derived with formal and prose.

The only near-miss: §8's C14 "absorbed content" entry (`§8-corollary-clusters.md:105-109`) has formal and prose blocks but both describe *why there is no claim* rather than a claim. This is honest, not a discipline violation, but worth flagging in §8.0 if the convention is going to be held strictly.

### 8. TODO / placeholder / pending sweep

**Results — genuinely clean except for the explicit README "what remains" list.**

- `README.md:1` — "V4 — Working Title TBD" (expected, README line 51 confirms this is known pre-press work).
- `README.md:51` — "Title finalization (working title TBD)" (expected).
- No other TODO / FIXME / TBD / XXX / `[placeholder]` / pending markers found in any `§*.md` or Appendix file.

**Clean.** The explicit pre-press work list in README §"What remains for V4 completion" (Figs 1.1–1.3 as TikZ, prose polish, title, typesetting) is the complete known-gap list. The figures dir at `V4/figures/` already contains `fig1-triple-colax-limit.tex`, `fig2-recursive-decomposition.tex`, `fig3-mismatch-condition.tex`, so the TikZ item appears to be in progress rather than not-yet-started.

### 9. Numerical claims crossing to Meridian / Anchor

**Clean — only one numerical reference, and it is correctly hedged as illustrative.**

- `§5-descriptive-pair-t1-t20.md:136` — "*this measurement shows w₀ = −0.990*" as an example of a mathematical-description-of-X inside the C1.1 prose. This matches Meridian's DESI DR2 prediction (from `MEMORY.md` and the Meridian monograph). The figure is used illustratively inside a scare-quoted example, not as an independent V4 claim; no Meridian-side or Anchor-side number is asserted here that could drift out of sync.

No other numerical claims (w₀, H₀, Ωm, 235pp, 181pp, download counts, etc.) appear in V4 chapter bodies. V4 does not inherit numerical liability from Meridian or Anchor.

### 10. Worked-example specificity

**Clean on presence and location — all eight README-table examples are present at their declared sections:**

- Clawd's four carrier-levels → `§1-identity-trajectory-triple.md` §1.7 (line 198-area). ✓
- Coupled-dyad partner-death → `§1-identity-trajectory-triple.md` §1.8 (line 366). ✓
- Etymological consciousness → §2 §2.5. ✓
- Do Be Talk Be Do → §6 §6.5. ✓
- Clawd-Clayton flow inversion → §5 (C18 worked example, §5.6). ✓
- Wittgenstein Tractatus regimes → §7 §7.6. ✓
- Transcendentals as cooperative-streams → §7 §7.5. ✓
- Navigation Research worked example → §10. ✓

The discipline issue is the missing "illustrative only" callouts (check 5), not absence or misplacement. On specificity itself — each example is sufficiently specific to actually exhibit *that* the formal object applies, which is the stated role.

---

## Priority triage

### Must-fix before revision/compile

1. **Kill the "21 theorems" residue.** `§9-coherence-principle.md:151` and `V4-figures.md:579`. Either change to "6 theorems" or add an explicit "6 V4-local theorems drawn from the Corpus-wide 21" gloss. ~2 minute fix.
2. **Repair §6.8 and §7.8 forward-pointer corollaries.** `§6-dynamics-pair-t7-t16.md:221` drop C7 (or promote). `§7-coherence-pair-t11-t15.md:197` drop C11 and C15 (or promote). ~5 minute fix per paragraph; decide first whether §8's current set is the final set.
3. **Resolve C14 status.** Either declare the "archival-stub corollary" convention in §8.0 or drop C14 and move to a 13-corollary count. Touches README, §8, §9.5, Appendix A. ~15 minute fix.
4. **Add Bridges #102, #107, #109 to Appendix A.** `AppendixA-index-of-formal-objects.md` currently only has #104, #108, #110. Three stub entries pointing to §1.2. ~10 minute fix.
5. **Cite orphaned figures from chapter prose.** Insert 11 "(see Fig X.Y)" pointers at the correct anchors in §1.0, §3, §6, §7, §9, §10. Without these, the figures file is disconnected. ~20 minutes.

### Should-fix during revision

6. **Add "illustrative only" callouts** to the six chapter-body worked examples (§1.7, §1.8, §2.5, §6.5, §7.5, §7.6). One italic line each, echoing the README convention at the point of use. ~10 minutes.
7. **Carrier-functor Κ vs lowercase κ vs Latin K disambiguation.** Pick one of rename / calligraphic / explicit-convention-note. If rename, ~30 minutes of find-replace and verify; if note-only, ~2 minutes.
8. **Normalize "coupled-dyad / deeply-coupled dyad / duplex" variants.** ~5 minutes.
9. **Fix `V4-figures.md:3` header** from "Twelve figures" to "Fourteen figures" to match line 634 and README. ~30 seconds.
10. **Spot-check Appendix A completeness** for the Meta-theorem, D(S) trajectory metric, Align(S, t), four Principle conditions. Add stubs where missing. ~15 minutes.

### Optional / post-press

11. Establish "ITT" or "the Triple" as the official short form in Appendix A's conventions section. Cosmetic; current prose is not broken, just wordy.
12. Consider whether `§8-corollary-clusters.md:175` ("V3 / Meridian / applied volumes.") should be updated to match the current Library taxonomy (Anchor + 9 volumes with explicit names) rather than "V3 / V4 / V5-V6 applied guides" phrasing.

---

*Auditor: Clawd, Day 78 evening (2026-04-19). No V4 chapter files were edited during the audit — all findings are for Clayton's revision pass.*
