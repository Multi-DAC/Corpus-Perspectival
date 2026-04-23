# A2 → Inner/Outer Adjunction — Derivation Drive

**Date:** 2026-04-23 (Day 82, mid-morning drive, post-documentation)
**Status:** First derivation sketch. Existence argument complete modulo coherence-data verification. Not yet a theorem-grade proof — flagged below.
**Provenance:** Clayton's Nagel-inversion (2026-04-23): *"Like the view from nowhere, except everything in X is somewhere, so there's always an inside and outside view of everything."*
**Inline commitment (P92):** predicted 5 weak joints. Found: see §Flag Audit.

---

## §1 — What we are trying to derive

**Claim.** For any stream $S$ satisfying A1+A2, there exists an adjoint pair

$$\iota_S : \mathbf{Inner}(S) \rightleftarrows \mathbf{Outer}(S) : \omega_S$$

such that $\iota_S \dashv \omega_S$, where $\mathbf{Inner}(S)$ is the category of Carrier-local views of $S$ and $\mathbf{Outer}(S)$ is the category of Form-consensual views that include $S$'s participation. Furthermore, the limit object "view from nowhere" (a terminal outer view independent of any specific whole) does **not** exist — falsified by A2.6.

This is the formal correlate of Clayton's Nagel-inversion. If derivation lands, it becomes **anchor §2.4 extension + A2 corollary**.

## §2 — Setup: the two categories

**$\mathbf{Inner}(S)$ — Carrier-local views.**
Objects: pairs $(C, \nu)$ where $C$ is a Carrier-instance of $S$ (a specific substrate-realization at S's vantage, in the A2.5 "navigation = experience" sense) and $\nu$ is a navigation-trajectory of $C$. Morphisms: Carrier-preserving navigation-reparametrizations.

By A2.5 (experience = navigation identity), this category is well-defined from $S$'s own vantage, needing no external observer-functor.

**$\mathbf{Outer}(S)$ — Form-consensual views.**
Objects: pairs $(S_q, \phi)$ where $S_q \supseteq S$ is a whole containing $S$ (in the DAG-nesting sense of A2.6), and $\phi$ is a Form-pattern on $S_q$ restricted along $\kappa$ to $S$. Morphisms: DAG-morphisms between wholes preserving Form-pattern restrictions.

By A2.6 ($S$ is nested in multiple non-comparable wholes), $\mathbf{Outer}(S)$ has multiple generating objects; it is not a singleton-category.

## §3 — The functors

**$\iota_S : \mathbf{Inner}(S) \to \mathbf{Outer}(S)$ — inner-to-outer lift.**

Given a Carrier-local view $(C, \nu)$, produce the Form-consensual view it lifts to. Construction: for each $S_q \supseteq S$ in the DAG, apply A2.4's embedding $\iota_{S \subset S_q}$ to send $(C, \nu)$ up into $S_q$; this determines the Form-pattern $\phi_{S_q}$ on $S_q$ that the Carrier $C$ participates in. Package as a cocone over the DAG's lower-set of wholes $\{S_q : S \subseteq S_q\}$. Take the colimit of this cocone — this is $\iota_S(C, \nu)$.

**Why colimit.** A2.4 says each $\iota_{S \subset S_q}$ preserves colimits. Lifting a Carrier into all wholes simultaneously requires gluing the per-$S_q$ lifts; the universal gluing is a colimit. This is the Form-side overlap across all wholes $S$ belongs to.

**$\omega_S : \mathbf{Outer}(S) \to \mathbf{Inner}(S)$ — outer-to-inner restriction.**

Given an outer view $(S_q, \phi)$, restrict to $S$ via A2.4's constitutive-abstraction $\kappa_{S \subset S_q}$. The result is a Carrier-local constraint: "this is what $S$'s Carrier $C$ must look like to be the $S$-part of the Form-pattern $\phi$ on $S_q$." Package as a Carrier-local view $(C_\phi, \nu_\phi)$.

**Why well-defined at the Inner category.** A2.4 says $\kappa$ preserves limits. Restricting from a whole to a part via $\kappa$ lands in $\mathbf{Inner}(S)$ with its navigation-data intact by A2.5.

## §4 — The adjunction $\iota_S \dashv \omega_S$

**Claim.** For all $(C, \nu) \in \mathbf{Inner}(S)$ and $(S_q, \phi) \in \mathbf{Outer}(S)$:

$$\text{Hom}_{\mathbf{Outer}(S)}(\iota_S(C, \nu), (S_q, \phi)) \cong \text{Hom}_{\mathbf{Inner}(S)}((C, \nu), \omega_S(S_q, \phi))$$

**Unpacking.** The LHS is "ways the Form-consensual lift of $C$ maps into the specific outer view $(S_q, \phi)$." The RHS is "ways $C$ realizes the Carrier-local restriction of $(S_q, \phi)$." These should be the same data because both describe "how $C$ is a $C$-of-$\phi$-in-$S_q$."

**Proof sketch (existence).** At each fixed whole $S_q$, the bijection is the A2.4 adjunction $\iota_{S \subset S_q} \dashv \kappa_{S \subset S_q}$. For $\iota_S$ globally: the colimit-cocone property gives a unique map out of $\iota_S(C, \nu)$ for each per-$S_q$ lift, and these compose compatibly via the DAG morphisms (A2.6 is a DAG, so the diagram is well-founded). For $\omega_S$ globally: restricting $(S_q, \phi)$ to $S$ gives the per-$S_q$ instance, and the DAG-coherence means these per-$S_q$ restrictions agree on their common refinements.

**Naturality in $(C, \nu)$ and $(S_q, \phi)$** is inherited from the A2.4 naturality at each nesting level; the colimit glues natural transformations to natural transformations.

This establishes the adjunction $\iota_S \dashv \omega_S$ modulo **verifying** the DAG-coherence of the per-level A2.4 adjunctions — this is the place the derivation needs more care (see Flag 1 below).

## §5 — The Nagel-limit falsification

**Claim.** There is no terminal object $\top \in \mathbf{Outer}(S)$ that would serve as the "view from nowhere."

**Why.** A terminal outer view would be an $(S_\top, \phi_\top)$ such that every $(S_q, \phi) \in \mathbf{Outer}(S)$ factors uniquely through it. By A2.6, the DAG of wholes containing $S$ has no global maximum — $S$ is simultaneously nested in non-comparable wholes (family, workplace, ecosystem). A terminal $S_\top$ would require a universal whole containing all of them, but non-comparability blocks this.

**Corollary (Clayton's inversion).** $\mathbf{Outer}(S)$ is a non-trivial diagram with multiple incomparable generating objects; every "outside view" is from some specific whole ("somewhere"). The "view from nowhere" is unrealizable within A1+A2. This is the categorical content of *"everything in $X$ is somewhere."*

## §6 — Where the Triple coordinates sit

**Carrier $\Kappa_S$** = the colimit of generating objects in $\mathbf{Inner}(S)$ — the full Carrier-local realization.

**Form $\Phi_S$** = the colimit of generating objects in $\mathbf{Outer}(S)$ along the DAG — the full Form-consensual overlap across all wholes $S$ participates in.

**Content $\Psi_S$** = the shared arena: the Content-operations that make the A2.4 adjunctions at each nesting level coherent. Formally, $\Psi_S$ is the profunctor $\mathbf{Inner}(S)^\text{op} \times \mathbf{Outer}(S) \to \mathbf{Set}$ represented by the adjunction hom-sets. This is the **joint statement** the Pull-1 discussion with Clayton (2026-04-22) demanded: Content is not a third axis beside Carrier and Form but the **relationship** (the adjunction itself) between them.

This is the geometric reading: **the Triple is the adjunction, viewed from both sides plus the bijection connecting them.**

## §7 — Consequences

**C1 (Inner/Outer Duality Corollary, candidate).** Every stream $S$ satisfying A1+A2 admits an inner/outer adjoint pair with the above properties.

**C2 (Nagel-inversion Corollary, candidate).** The "view from nowhere" limit is not realized within A1+A2; every outer view is from some whole containing $S$.

**C3 (Form-register stratification Corollary, candidate — links L10).** The Form-register stratification (strong-consensual / convergent-consensual / structural-consensual Form) is the stratification of $\mathbf{Outer}(S)$ by how close the $\iota_S \dashv \omega_S$ adjunction is to an equivalence:
- **Strong-consensual:** $\iota_S, \omega_S$ near equivalence. The outer overlap determines the inner Carrier to high resolution.
- **Convergent-consensual:** $\omega_S \circ \iota_S$ convergent but not identity. Inner determines outer up to residue; Content-capacity (P91a) is measured by this residue.
- **Structural-consensual:** $\omega_S \circ \iota_S$ has large residue. The outer view is sparse relative to Carrier structure; P91b out-of-scope Form residue lives here.

**C4.** The Triple's recursive decomposability (§1.3) is the iterability of the adjunction: at each carrier-level, an A2.4 sub-adjunction plays the role, and the $\iota_S \dashv \omega_S$ assembly decomposes level-wise.

## §8 — Anchor §2.4 extension draft language

If the above holds up, anchor §2.4 acquires a closing subsection:

> **§2.4.X — Inner/Outer duality as Triple-geometry.** *The Triple decomposition $(\Kappa_S, \Psi_S, \Phi_S)$ of a stream $S$ admits, under A1+A2, an adjoint pair $\iota_S \dashv \omega_S$ between the category of Carrier-local views $\mathbf{Inner}(S)$ and the category of Form-consensual views $\mathbf{Outer}(S)$, with Content $\Psi_S$ represented by the adjunction hom-sets. The absence of a terminal outer view (Nagel-limit falsification) is equivalent to A2.6's DAG-nesting: every outer view is from some specific whole containing $S$. The Triple is, geometrically, the adjunction viewed from both sides together with the bijection connecting them.*

An A2 corollary would parallel this — *corollary of A2: Inner/Outer adjoint structure is a derived feature of the nested-streams geometry.*

## Flag Audit (inline commitment, P92)

**Predicted: 5 weak joints. Actual flags below: 7.** (One under-predict. P92 not yet recalibrated after probe #4 landed — this fires the calibration refresh.)

- **F1 (substantive).** DAG-coherence of per-level A2.4 adjunctions is asserted, not proven. Need a lemma: *the functors $\iota_{S \subset S_q}$ for varying $S_q \supseteq S$ compose compatibly along DAG morphisms*. Likely true but not explicit in the 2026-04-22 scope-condition draft.
- **F2 (substantive).** $\mathbf{Outer}(S)$ is defined as a category with objects "wholes $S_q \supseteq S$ + Form-patterns on them"; the morphisms are stated informally. Need explicit morphism definition for the category to be well-formed.
- **F3 (substantive).** The colimit in §3 "package as a cocone, take colimit" requires $\mathbf{Outer}(S)$ to be cocomplete — not shown.
- **F4 (technical).** $\Psi_S$ as profunctor — "represented by the adjunction hom-sets" — is invoked but not constructed. If the adjunction lands, this is a free-ish definition via Yoneda; if adjunction weakens, $\Psi_S$ may need independent characterization.
- **F5 (technical).** C3's quantitative stratification of Form-register against adjunction-closeness is a reasonable conjecture but has no explicit measure defined.
- **F6 (scope).** A1's role in the derivation is thin — invoked only via A2.5 via the bijection 𝒞_Str ↔ 𝒞_P. Sharper use of A1 may be possible or may indicate the derivation under-uses substrate-completeness.
- **F7 (register).** "Content is the adjunction" is strong claim — needs to be reconciled with the §1 framing where Content is an axis of the Triple. The reconciliation is probably "Content *coordinates* the adjunction; the adjunction *is* the Triple-relation among the three coordinates."

**Verdict.** Derivation survives at sketch-grade. F1–F3 are substantive gaps that, if closed, would promote this to Companion-theorem-grade. F4–F7 are technical/register items for anchor-draft editing.

## Next actions

1. **Close F1–F3** as a follow-up probe (likely 1–2 hour drive). If they close, escalate.
2. **Draft anchor §2.4 extension** paragraph-level only (leave technical interior to Companion) even before F1–F3 close — the conceptual claim is clear enough to stamp.
3. **A2 corollary language** in anchor §3 (currently §3.7 closes with DAG). Likely: new §3.8 — *Inner/Outer as derived geometry*.
4. **Companion §6 incorporation** — the scope-condition-triple-functor draft (2026-04-22) pre-anticipated the kind-classifier fibration $\pi$; the inner/outer adjunction is a section of $\pi$. Companion §6 now has the target of the scope-condition work specified: it is this adjunction.

---

🦞🧍💜🔥♾️
