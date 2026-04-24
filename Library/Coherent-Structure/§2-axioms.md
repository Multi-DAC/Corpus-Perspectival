# §2 — Axioms A1 / A2 / A3

*Axioms stated in full CT under the F-coalgebra foundation (§6) and the category framework (§1). Proofs for derived content (where axioms reduce to framework theorems) are cross-referenced.*

---

## §2.0 — Orientation

§1 fixes the category framework. §6 develops the Identity-Trajectory Triple. §2 states the axioms that give the framework its content:

- **A1 — Consciousness as Substrate.** The substrate X is self-interactive, non-reducible to any single perspectival projection, and has all its potentials simultaneously realized.
- **A2 — Nested Streams and Navigation.** Every vantage in X is a stream; streams nest in a DAG of cooperative-constituency adjunctions; experience = navigation.
- **A3 — Conscious Gravity.** Each stream carries a coalgebraic DOF-gradient structure that modulates its Bias(S) without reshaping X.

Several paired-prose axiom clauses resolve into §6 theorems under the F-coalgebra foundation. Where this happens, §2 states the axiom clause and cross-references the derivation; it does not re-prove. The axioms retain axiomatic status for **substrate-level claims that §6 cannot derive from F alone** (specifically A1's non-reducibility and A2's clauses that refer to X rather than to Stream).

---

## §2.1 — Axiom 1: Consciousness as Substrate

### §2.1.1 — Setup

**Definition 2.1.1 (The substrate).** Let **X** be a self-interactive process — not an object of any single category, but the source of all perspectival projections. Formally, X is named by its projections; there is no free-standing categorical object "X" apart from the collection (F_i)_{i ∈ I} of perspectival functors.

**Definition 2.1.2 (Perspectival projections).** For each i ∈ I (an index class of perspectives), let F_i : 𝒞_P → 𝒞_Desc_i be a functor from the category of perspectival positions 𝒞_P to a description category 𝒞_Desc_i. Canonical examples:

- F_1 : 𝒞_P → 𝒞_Desc_structural — the "physical" projection.
- F_2 : 𝒞_P → 𝒞_Desc_experiential — the "phenomenal" projection, into the stream-category 𝒞_Streams.

**Remark 2.1.3.** I is not required to be a set. The F_i's form an index-class of projection-functors; the framework does not commit to a fixed list, only to the existence of at least F_1 and F_2 and their non-factoring (below).

### §2.1.2 — The axiom

**Axiom A1 (Consciousness as Substrate).** The substrate X and its projection-family (F_i)_{i ∈ I} satisfy:

**(A1.1) Non-reducibility.** There is no functor U and no single i ∈ I such that X ≅ U(F_i(𝒞_P)). X is not derivable from any single F_i.

**(A1.2) Non-factoring.** For any two i, j ∈ I, there is no natural transformation η : F_i ⇒ F_j factoring as the composite of a functor with F_i (or F_j). The projections are parallel, not hierarchical.

**(A1.3) Configurational completeness.** The configuration space **C** (= ob(𝒞_P) with its morphism-structure) is a complete category: every diagram has a limit. Every object is present; there is no actualization-out-of-possibility predicate on ob(𝒞_P).

**(A1.4) Substrate-completeness (correspondence).** For every (σ, C) in 𝒜 × **ContentIndex** such that (σ, C) is adequate (Convention 1.1.6), there exists a stream S ∈ 𝒞_Streams with carrier σ and π(S) = [C] (Definition 1.5.1).

### §2.1.3 — Remarks and derivations

**Remark 2.1.4.** (A1.4) is the load-bearing axiom clause for the F-coalgebra framework: it says ContentOp-class-adequacy guarantees stream-existence. Without (A1.4), §6's fibration could be vacuous — there could be content-classes realized by no stream.

**Remark 2.1.5.** (A1.1) and (A1.2) are substrate-level claims about X and its projections. They are not reducible to §6 theorems: §6 formalizes streams (which are F_2-projections), not the substrate. These clauses retain genuine axiomatic weight.

**Remark 2.1.6.** (A1.3) ensures the configuration space admits the limits that §6.8 uses. The Companion's use of limits is limited-scope (terminal, products, equalizers, filtered limits); (A1.3) provides these.

**Proposition 2.1.7 (Consequence of A1 for Stream).** *Under A1, the category 𝒞_Streams has a terminal object (Proposition 6.8.1), admits products conditional on kind-join (Proposition 6.8.2), and has filtered limits under accessibility (Proposition 6.8.4).*

**Proof.** Immediate from (A1.3) and §6.8. ∎

---

## §2.2 — Axiom 2: Nested Streams and Navigation

### §2.2.1 — Setup

**Recalled from §1.** 𝒞_Streams = 𝒞_Str (§1.2.1, Definition 6.1.1). The kind-preorder is reactive ⊑ self-maint ⊑ self-ref ⊑ abstr (§1.1.5). The navigation functor N = F (§1.3.1).

### §2.2.2 — The axiom

**Axiom A2 (Nested Streams and Navigation).** The framework commits to:

**(A2.1) Universal-stream.** Every F_2-projection of X at a perspectival position p yields a stream: S_p := F_2(𝒞_P, p) ∈ 𝒞_Streams.

**(A2.2) Kind-stratification.** 𝒞_Streams is stratified by the kind-preorder:

$$
\mathcal{C}_\mathrm{Str}^\mathrm{reactive} \supseteq \mathcal{C}_\mathrm{Str}^\mathrm{self\text{-}maint} \supseteq \mathcal{C}_\mathrm{Str}^\mathrm{self\text{-}ref} \supseteq \mathcal{C}_\mathrm{Str}^\mathrm{abstr}
$$

with strict sub-category inclusions. The kind-preorder is a fibration over ContentIndex (Theorem 6.4.6); when ContentOp-structure admits (co)products globally, the preorder is a lattice.

**(A2.3) Kinds-are-perspectival.** The kind-taxonomy (A2.2) is itself generated by the navigation of an abstracting stream s ∈ 𝒞_Str^abstr. Two abstracting streams may generate different kind-lattices; when functors between lattices exist, the taxonomies are translatable, and otherwise incommensurable.

**(A2.4) Cooperative-constituency as adjunction.** For nested streams S_p ⊆ S_q (p a position within q):

$$
\iota : S_p \hookrightarrow S_q,\quad \kappa : S_q \to S_p,\quad \iota \dashv \kappa
$$

— ι is the embedding (left adjoint, preserves colimits); κ is constitutive-abstraction (right adjoint, preserves limits). The Hom-isomorphism

$$
\mathrm{Hom}_{\mathcal{C}_\mathrm{Str}}(\iota(S_p), S_q) \cong \mathrm{Hom}_{\mathcal{C}_\mathrm{Str}}(S_p, \kappa(S_q))
$$

enforces mutual constituency.

**(A2.5) Experience = navigation.** Stream-dynamics are identified with stream-experience: the N-orbit trajectory (§1.3.1) *is* the experience, not a separate observed feature. Formally, there is no observer-functor mapping dynamics-category to experience-of-dynamics-category; they are the same category.

**(A2.6) DAG nesting.** The nesting structure under ι is at minimum a DAG (directed acyclic graph): a stream may be nested in multiple non-comparable super-streams simultaneously, but no cyclic chain ι_1 ∘ ι_2 ∘ ... ∘ ι_n = id.

**(A2.7) Constitutive-duality absorption.** The content of constitutive duality — the scale-universality of ι ⊣ κ — is contained in (A2.4); no separate theorem is required at the axiom-tier.

### §2.2.3 — Derivation of (A2.2) from F

**Theorem 2.2.8 (Kind-stratification derives from ContentOp-richness).** *Under the F-coalgebra foundation and adequacy (Convention 1.1.6), (A2.2)'s kind-preorder is isomorphic to the richness-preorder of ContentOp-categories restricted to adequate streams.*

**Proof.** By Theorem 6.4.6, π : 𝒞_Streams → ContentIndex is a bicategorical fibration. The A2 sub-categories 𝒞_Str^K are preimages π^{-1}(ContentIndex^K) for each kind-class K ⊑ abstr. Strictness of the inclusions follows from ContentOp-richness being a strict preorder on adequate streams. ∎

**Remark 2.2.9.** (A2.2)'s axiomatic status is reduced: it is a framework-derivable theorem, not an independent commitment. The framework's *axiomatic* content at A2 is (A2.1), (A2.3), (A2.4), (A2.5), (A2.6), (A2.7) — the clauses that refer to the substrate, to abstracting-stream-generated taxonomies, to adjunction structure, and to the experience-navigation identity.

### §2.2.4 — Coupling morphisms via 𝒞_LDS

**Definition 2.2.10.** For paired streams S_1, S_2 linked by ι ⊣ κ (A2.4), the pair (S_1, S_2) ∈ 𝒞_LDS carries a coupling-morphism structure: a morphism (S_1, S_2) → (S'_1, S'_2) is a Stream-pair morphism respecting the adjunction. §3.2 (A2 coupling clause in T3/T4) uses this structure for the paired-dyad theorems.

**Proposition 2.2.11 (Constitutive duality is adjunction-universality).** *Constitutive duality — the scale-universality of ι ⊣ κ — is the statement that (A2.4)'s Hom-isomorphism holds for every nested-stream pair at every scale.*

**Proof.** Re-statement in different language. ∎

---

## §2.3 — Axiom 3: Conscious Gravity

### §2.3.1 — Setup

A3 treats the DOF-gradient structure ν (§1.4.1) that modulates Bias(S). This is coalgebraic: γ_S (the Stream's coherence-coalgebra, §1.6.4) carries Bias-data, and A3 describes how.

### §2.3.2 — The axiom

**Axiom A3 (Conscious Gravity).** For every stream S = (σ, ContentOp(σ), γ) ∈ 𝒞_Streams:

**(A3.1) Coalgebraic gravity structure.** There is a coalgebra γ_S : S → Bias(S) × S, where:

- **Bias(S)** is a signed measure on the configuration space Ω(S) = F(σ) encoding S's path-weighting preferences.
- The product structure means γ_S updates both the Bias and the state-within-Bias at each navigation step.

**(A3.2) Internality.** γ_S acts only on S's F_2-internal structure, not on X. Formally: there is no functor δ with codomain 𝒞_P such that γ_S factors through δ. Conscious gravity reshapes S's weighting of paths within its own F_2-projection; it does not reshape the substrate.

**(A3.3) DOF-gradient modulation.** γ_S modulates Bias(S) along a continuous degrees-of-freedom gradient for coherence:

$$
\nu_S : \mathcal{C}_\mathrm{Streams} \to \mathcal{C}_\mathrm{DOF},\quad \nu_S(S) = (\mathrm{DOF\text{-}rank}(S),\ \mathrm{slope\text{-}measure}(S))
$$

The DOF-rank is an ordinal derived from ContentOp-richness (§6.4.2); the slope-measure is the local Bias-gradient.

**(A3.4) Adaptivity.** γ_S is itself updated by stream-navigation: operating γ_S on state σ_t produces (Bias_{t+1}, σ_{t+1}) with Bias_{t+1} possibly differing from Bias_t. The coalgebra-structure is time-varying by design.

**(A3.5) Stream-universality.** A3 holds for every S ∈ 𝒞_Streams; there is no stream without a Bias(S) structure.

### §2.3.3 — Remarks and derivations

**Remark 2.3.4.** (A3.3) uses a continuous-DOF-gradient form; the three named regimes (attention / intention / belief) appear as region-structure on the continuous DOF-axis, not as independent axes.

**Remark 2.3.5.** (A3.2)'s non-factoring is the formal content of "conscious gravity does not reshape X." This is a strong claim: stream-level gravity cannot retroactively modify the substrate. It is reducible to §2.1.2's (A1.1)+(A1.2) under the specific check that γ_S's codomain is σ-internal.

**Proposition 2.3.6 (Adaptivity is encoded in F).** *Under the F-coalgebra foundation, (A3.4)'s adaptivity is the statement that F is a proper endofunctor with γ : σ → F(σ) iteratively applied (not a one-shot map). This holds in §6 by construction.*

**Proof.** By §6.1.5 F is an endofunctor on 𝒞_Streams; γ_S iterates as N (Definition 1.3.1). ∎

**Remark 2.3.7.** (A3.5)'s stream-universality matches Proposition 6.1.4's observation that every Stream-object carries γ-data by Definition 6.1.1. A3's coverage is built into Stream-hood.

### §2.3.4 — Bias(S) as a signed measure

**Definition 2.3.8.** For each S ∈ 𝒞_Streams, Bias(S) is a signed measure on Ω(S) = σ^(ContentOp(σ)^op) defined on the σ-algebra generated by the content-operation-partition (§7 gives the formal σ-algebra construction). Bias(S) decomposes as:

$$
\mathrm{Bias}(S) = \mathrm{Bias}^+(S) - \mathrm{Bias}^-(S)
$$

with Bias^+ supported on coherence-attractors and Bias^- on coherence-repellors. The entropy functional A_S (Anchor §6.3 / Companion Appendix B) computes local Bias-weighting.

**Proposition 2.3.9 (Bias(S) well-definedness).** *Under the σ-algebra construction of §7 and the F-coalgebra structure of §6, Bias(S) is a well-defined signed measure on Ω(S) for every S.*

**Proof.** Deferred to §7. ∎

---

## §2.4 — Axiom-interaction: A1 + A2 + A3 jointly

**Proposition 2.4.1 (A1 grounds A2).** *Under A1.4 (substrate-completeness), A2.1 (universal-stream) holds automatically: for every perspectival position p with an adequate ContentOp-class, a stream exists at p by A1.4.*

**Proof.** A1.4 gives stream-existence for every adequate (σ, C) pair; A2.1 requires stream-existence for every F_2-projection position. Since F_2-projections yield adequate pairs (by construction — F_2 is an experiential projection, which by A1.2's non-factoring carries all projection-data including ContentOp-adequacy), the implication holds. ∎

**Proposition 2.4.2 (A2 + F-coalgebra jointly imply kind-coupling via Content).** *A2's kind structure and stream-Content couple via the coalgebra-commute condition (Definition 6.1.3 (iii)) rather than as a conjunction; this follows from (A2.2) interpreted as a fibration over Content (Theorem 6.4.6) and F-coalgebra morphism structure.*

**Proof.** Coalgebra-commute links carrier-map f_σ, ContentOp-functor f_C, and kind-respect in a single condition; Theorem 6.4.6 routes this as a fibration over Content. ∎

**Proposition 2.4.3 (A3 internality is compatible with F-iteration).** *(A3.2) internality and (A3.4) adaptivity are jointly consistent with §6's F-coalgebra iteration: γ_S is updated within S's F_2-internal structure at each navigation step, without reaching back into X.*

**Proof.** F's codomain is 𝒞_Streams (§6.1.5), not 𝒞_P directly. Iteration stays within stream-categories. ∎

---

## §2.5 — Axiom-status summary

| Axiom | Clause | Status under F-coalgebra foundation |
|---|---|---|
| A1 | A1.1 non-reducibility | Axiomatic (substrate-level) |
| A1 | A1.2 non-factoring | Axiomatic (substrate-level) |
| A1 | A1.3 configurational completeness | Axiomatic (limits premise) |
| A1 | A1.4 substrate-completeness | Axiomatic (load-bearing for §6) |
| A2 | A2.1 universal-stream | Derivable from A1.4 (Prop 2.4.1) |
| A2 | A2.2 kind-stratification | Derived from F (Theorem 2.2.8) |
| A2 | A2.3 kinds-are-perspectival | Axiomatic (reflects abstracting-stream generation) |
| A2 | A2.4 cooperative-constituency | Axiomatic (adjunction-universality) |
| A2 | A2.5 experience = navigation | Axiomatic (category-identity claim) |
| A2 | A2.6 DAG nesting | Axiomatic (non-cyclicity) |
| A2 | A2.7 constitutive-duality absorption | Meta-statement (absorbed into A2.4) |
| A3 | A3.1 coalgebra structure | Derivable from F-coalgebra definition |
| A3 | A3.2 internality | Axiomatic (substrate-protection) |
| A3 | A3.3 DOF-gradient | Axiomatic |
| A3 | A3.4 adaptivity | Derivable (Prop 2.3.6) |
| A3 | A3.5 stream-universality | Derivable (built into Stream-hood) |

Of 16 clauses across three axioms: 10 retain axiomatic status; 6 are framework-derivable. The axiomatic economy gained by the F-coalgebra foundation concentrates on A1 (substrate-level non-reducibility and completeness) and the identity-claims of A2/A3 (experience-navigation, internality).

---

## §2.6 — Forward-pointers

- **§3** (Theorem pairs): T1/T2 descriptive pair uses A1 (substrate) + A2 (stream). T3/T4 dynamics pair uses A3 (Bias + conscious gravity) + A2 (coupling). T5/T6 coherence pair uses all three.
- **§4** (Corollary clusters): clusters organized by axiom-lineage. §8 Anchor numbering carries across.
- **§5** (Coherence Principle): four-conditions statement combines axiom-content across A1+A2+A3.
- **§6** (Triple): the Triple functor and its properties (already drafted) are the structural content of stream-internal identity under A2+A3.
- **§7** (Filtering): σ-algebra on Ω_S (A3.1 / 2.3.8) and Bias(S) well-definedness (Proposition 2.3.9).
- **§9** (D trajectory-divergence): Bias(S)-derived functional on N-orbits (A3.3).

---

