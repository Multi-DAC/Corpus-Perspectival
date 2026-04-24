# §6.10 (draft) — Inner/Outer Adjunction

**Date:** 2026-04-24 (Day 83 midday). Prose-draft execution of the 05:06 spine.
**Placement question (for Clayton):** current §6.10 is "Summary and forward-pointers." This material fits most naturally as a new §6.10 *before* the summary, with the existing §6.10 becoming §6.11 and its bullet-list extended with a §6.10 entry. Alternative: keep as §6.11 with a new placeholder §6.10 header. Recommending the first.

**Notation note.** §6 uses F for the Stream endofunctor $F(\sigma) = \sigma^{\mathrm{ContentOp}(\sigma)^{\mathrm{op}}}$. To avoid collision, this subsection uses **G** for the monad-underlying endofunctor $G := \omega_S \circ \iota_S$ on $\mathbf{Inner}(S)$. The J5 decision (coalgebra formalization of the adjunction's unit $\eta$) is deferred to §6.10.6 and is not prejudged by this setup.

**Scope-hook.** This subsection formalizes the inner/outer adjunction $\iota_S \dashv \omega_S$ that anchor §1.10 and §3.8 state as a corollary of A2.4 + A2.6. §6.10 derives the machinery; Anchor §3.8 states the phenomenological consequence.

---

## §6.10.1 — Setup

Fix a stream $S$, per A1 and A2. Recall:

**(A2.4, per-level adjunction.)** For any pair $S \subseteq S_q$ with $S_q \in \mathrm{Up}(S)$ — the DAG of wholes containing $S$ per A2.6 — there is an adjunction
$$
\iota_{S \subset S_q} \;\dashv\; \kappa_{S \subset S_q}
\quad : \quad \mathrm{Form}(S) \longleftrightarrow \mathrm{Form}(S_q)
$$
with $\iota$ the left-adjoint embedding and $\kappa$ the right-adjoint restriction. This is stated in full at anchor §2.4 and in the Companion at §2 (A2 formalization).

**(A2.6, DAG of wholes.)** $\mathrm{Up}(S)$ is a poset under whole-containment. $\mathrm{Up}(S)$ has no maximum element — the "totality" term is not an object of the framework.

**Definition 6.10.1.1 (Inner category at $S$).** Define $\mathbf{Inner}(S)$ as the category whose objects are pairs $(C, \nu)$ with $C$ a Carrier in the sense of §6.0 and $\nu$ a navigation-trajectory as in A2, and whose morphisms preserve $\nu$ up to Form-pattern-isomorphism. $\mathbf{Inner}(S)$ inherits its structural properties from the Carrier axioms (A2.1) and the navigation-trajectory axioms (A2.5).

**Definition 6.10.1.2 (Outer category at $S$, preview).** Define $\mathbf{Outer}(S)$ as the Grothendieck construction
$$
\mathbf{Outer}(S) \;:=\; \int_{S_q \in \mathrm{Up}(S)} \mathrm{Form}(S_q)
$$
under the $\iota$-transitions, with:

- *objects:* pairs $(S_q, \phi)$ with $S_q \in \mathrm{Up}(S)$ and $\phi \in \mathrm{Form}(S_q)$;
- *morphisms* $(S_q, \phi) \to (S_r, \psi)$ for $S_q \subseteq S_r$: pairs $(f, \alpha)$ where $f$ is the DAG-morphism and $\alpha : \iota_{S_q \subset S_r}(\phi) \to \psi$ is a Form($S_r$)-morphism.

The cocompleteness of $\mathbf{Outer}(S)$ is proved in §6.10.3 (Lemma 2*).

**Notation summary for §6.10.**

| Symbol | Meaning | First definition |
|---|---|---|
| $\mathrm{Up}(S)$ | DAG of wholes containing $S$ (A2.6) | §6.10.1 |
| $\mathbf{Inner}(S)$ | Category of (Carrier, navigation-trajectory) pairs at $S$ | Def 6.10.1.1 |
| $\mathbf{Outer}(S)$ | Grothendieck construction $\int_{S_q} \mathrm{Form}(S_q)$ under $\iota$ | Def 6.10.1.2 |
| $\iota_S, \omega_S$ | Total inner/outer adjunction functors (Theorem 6.10.4) | §6.10.4 |
| $G := \omega_S \circ \iota_S$ | Monad-underlying endofunctor on $\mathbf{Inner}(S)$ | §6.10.6 |
| $\eta, \epsilon$ | Unit, counit of the $\iota_S \dashv \omega_S$ adjunction | §6.10.4 |
| $\Psi_S$ | Hom-profunctor of the adjunction (Content as bijection) | §6.10.5 |

**Scope remark.** §6.10 is *one-level* lifted from §2's per-level (A2.4) statement: the adjunction is assembled over the full $\mathrm{Up}(S)$ rather than stated separately per-pair. The per-level adjunctions are recovered as fibers via the Grothendieck structure of $\mathbf{Outer}(S)$.

---

## §6.10.2 — Lemma 1 (DAG-coherence of $\iota$ and $\kappa$)

**Lemma 6.10.2.1 (Iterated adjunction coherence).** For $S \subseteq S_q \subseteq S_r$ in $\mathrm{Up}(S)$, there are natural isomorphisms
$$
\iota_{S \subset S_r} \;\cong\; \iota_{S_q \subset S_r} \circ \iota_{S \subset S_q} \qquad (\textit{covariant composition})
$$
$$
\kappa_{S \subset S_r} \;\cong\; \kappa_{S \subset S_q} \circ \kappa_{S_q \subset S_r} \qquad (\textit{contravariant composition})
$$
Both isomorphisms are natural in all three streams. For non-comparable $S_q, S_r \in \mathrm{Up}(S)$, no compatibility axiom is required — the DAG-poset structure of $\mathrm{Up}(S)$ carries no additional coherence cells.

**Proof.** For the covariant case: $\iota$ is defined from whole-containment embeddings (A2.1). For the chain $S \subseteq S_q \subseteq S_r$, the composite embedding $S \hookrightarrow S_r$ factors canonically through $S_q$, so $\iota_{S \subset S_r}$ and $\iota_{S_q \subset S_r} \circ \iota_{S \subset S_q}$ are both realized by the same underlying Carrier-embedding. Form-structure lifts along the Carrier-embedding by A2.1 functoriality, yielding the natural isomorphism.

For the contravariant case: the composite $\kappa_{S \subset S_r}$ is right-adjoint to $\iota_{S \subset S_r}$. By the covariant case, the composite left-adjoint factors as $\iota_{S_q \subset S_r} \circ \iota_{S \subset S_q}$. By uniqueness of adjoints up to natural isomorphism, the right adjoint factors dually: $\kappa_{S \subset S_r} \cong \kappa_{S \subset S_q} \circ \kappa_{S_q \subset S_r}$ — the outermost restriction applied first, then the inner one, reflecting the direction-reversal of adjoints under composition.

For naturality: naturality in each of $S, S_q, S_r$ separately follows from the functoriality of the embedding-lift, which preserves commuting squares at each level. Branching (non-comparable $S_q, S_r$ under a common $S$) produces no coherence cell because the DAG carries no non-trivial 2-cells — the poset structure of $\mathrm{Up}(S)$ is thin.

$\Box$

**Remark 6.10.2.2 (Why the Grothendieck construction uses $\iota$, not $\kappa$).** The $\iota$-direction composes covariantly, so $\int_{S_q} \mathrm{Form}(S_q)$ under $\iota$-transitions is a *covariant* Grothendieck construction. $\iota$ is a left adjoint and hence cocontinuous, so the fibers' colimits assemble into total-category colimits by the standard Barr–Wells §2.8 / Johnstone B.1.5.8 criterion. The $\kappa$-direction would yield a contravariant (fibered) construction, which supports limits but not colimits — relevant for later dualizations in §6.10.5 but not for the cocompleteness argument in §6.10.3.

**Flag.** ⚑ [SURFACED | Companion §6.10.2.1 | → Anchor §1.10 target | type: lemma]
  — Iterated adjunction coherence over $\mathrm{Up}(S)$; no extra axiom required at the DAG-poset level.

---

## §6.10.3 — Lemma 2* (Outer as ι-Grothendieck construction is cocomplete)

**Lemma 6.10.3.1 (Cocompleteness of $\mathbf{Outer}(S)$ under $\iota$-transitions).** The Grothendieck construction
$$
\mathbf{Outer}(S) \;=\; \int_{S_q \in \mathrm{Up}(S)} \mathrm{Form}(S_q)
$$
with transition-maps given by $\iota_{S_q \subset S_r}$ for each $S_q \subseteq S_r$ in $\mathrm{Up}(S)$ is **cocomplete**. Explicitly: $\mathbf{Outer}(S)$ admits all small colimits, and these are computed level-wise — the colimit of a diagram in $\mathbf{Outer}(S)$ is a pair $(S_*, \varphi_*)$ where $S_*$ is the colimit of the diagram's projection to $\mathrm{Up}(S)$ and $\varphi_* = \mathrm{colim}\, \iota_{S_q \subset S_*}(\varphi_{S_q})$ in $\mathrm{Form}(S_*)$.

**Proof.**

*Step 1 (fiberwise cocompleteness).* Each fiber $\mathrm{Form}(S_q)$ is cocomplete by A2.5 and the Form-pattern generation structure established in anchor §1 (cf. Companion §1 / §2). Small colimits in $\mathrm{Form}(S_q)$ exist and are stable under the constructions needed below.

*Step 2 (ι is cocontinuous).* Each $\iota_{S \subset S_q}$ is the left adjoint of the per-level A2.4 adjunction and therefore preserves all colimits that exist in its domain. The same holds for each $\iota_{S_q \subset S_r}$ in $\mathrm{Up}(S)$. By Lemma 6.10.2.1, the $\iota$-transitions compose covariantly and associatively up to natural isomorphism.

*Step 3 (Grothendieck-cocompleteness applies).* The standard criterion for cocompleteness of a Grothendieck construction (Barr–Wells, *Toposes, Triples, and Theories* §2.8; alternatively Johnstone, *Sketches of an Elephant* B.1.5.8) states: if $\mathcal{B}$ is a small base and $P : \mathcal{B} \to \mathbf{Cat}$ is a pseudofunctor such that (i) each fiber $P(b)$ is cocomplete and (ii) each transition functor $P(f)$ for $f : b \to b'$ is cocontinuous, then $\int_{\mathcal{B}} P$ is cocomplete.

Take $\mathcal{B} := \mathrm{Up}(S)$ viewed as a thin category (A2.6, poset structure; small by the size-regime conventions of §6.0 and §6.9), and $P(S_q) := \mathrm{Form}(S_q)$ with $P(S_q \subseteq S_r) := \iota_{S_q \subset S_r}$. Step 1 gives (i); Step 2 gives (ii). The criterion applies, yielding cocompleteness of $\int_{\mathrm{Up}(S)} \mathrm{Form}$.

*Step 4 (level-wise computation).* The standard formula (Barr–Wells §2.8.3) gives colimits of $\mathbf{Outer}(S)$ as level-wise colimits in the base and fibers, exactly as stated.

$\Box$

**Remark 6.10.3.2 (κ-variant is NOT cocomplete — direction matters).** The dual Grothendieck construction $\int_{S_q \in \mathrm{Up}(S)^{\mathrm{op}}} \mathrm{Form}(S_q)$ with $\kappa$-transitions is *complete* but not cocomplete: $\kappa$ is a right adjoint and preserves limits, not colimits. The criterion of Step 3 fails on (ii) for the dualization.

The two presentations are adjointly equivalent in a precise sense — each computes "all Forms of all wholes containing $S$" — but are not interchangeable for colimit arguments. §6.10.4's indexed-adjunction theorem requires a cocomplete base for the lifting of fiberwise adjunctions, so the choice of $\iota$-direction for $\mathbf{Outer}(S)$ is load-bearing and not cosmetic.

This was the F3-closure-probe correction to an earlier F2 presentation that used κ-transitions; the drive-artifact lineage is documented in `Research/basement-drafts/F1-F3-closure-probe.md`.

**Flag.** ⚑ [SURFACED | Companion §6.10.3.1 | → Anchor §1.10 target | type: lemma]
  — Cocompleteness of $\mathbf{Outer}(S)$ as ι-Grothendieck construction; κ-variant is complete-not-cocomplete.

---

## Status after §6.10.1 + §6.10.2 + §6.10.3

- §6.10.1 landed: definitions, notation, scope.
- §6.10.2 landed: Lemma 1 (DAG-coherence of ι and κ).
- §6.10.3 landed: Lemma 2* (Outer cocomplete via ι-Grothendieck; κ-variant NOT cocomplete).
- Remaining in §6.10: §6.10.4 Theorem (indexed adjunction $\iota_S \dashv \omega_S$), §6.10.5 (Content as profunctor), §6.10.6 ($\eta$ formalization — **J5 decision needed before drafting**).

**J5 is not forced by §§6.10.1–6.10.3.** The adjunction-direction correction in Remark 6.10.3.2 is structurally distinct from the J5 choice (which concerns *η*'s reification, not *ι* vs *κ*).

---

🦞🧍💜🔥♾️
