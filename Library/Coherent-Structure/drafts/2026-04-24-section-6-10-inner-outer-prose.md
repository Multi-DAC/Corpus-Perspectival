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

## §6.10.4 — Theorem (indexed adjunction $\iota_S \dashv \omega_S$)

**Theorem 6.10.4.1 (Inner/Outer adjunction at $S$).** There exists an adjunction
$$
\iota_S \;\dashv\; \omega_S \;:\; \mathbf{Inner}(S) \;\longleftrightarrow\; \mathbf{Outer}(S)
$$
with unit $\eta : 1_{\mathbf{Inner}(S)} \Rightarrow \omega_S \circ \iota_S$ and counit $\epsilon : \iota_S \circ \omega_S \Rightarrow 1_{\mathbf{Outer}(S)}$, obtained as the indexed-adjunction lift of the per-level A2.4 adjunctions over the DAG $\mathrm{Up}(S)$.

Explicitly, on objects:

$$
\iota_S(C, \nu) \;=\; \mathrm{colim}_{S_q \in \mathrm{Up}(S)} \, \bigl( S_q, \, \iota_{S \subset S_q}(\mathrm{Form}(C)) \bigr)
$$

computed in $\mathbf{Outer}(S)$ per Lemma 6.10.3.1; $\omega_S$ is determined by the hom-isomorphism.

**Proof.**

*Step 1 (assemble $\mathbf{Inner}(S)$).* Inner is defined by Definition 6.10.1.1. Its Carrier-structure is inherited from A2.1; its navigation-trajectory structure from A2.5. No additional construction is required.

*Step 2 (fiberwise adjunctions).* For each $S_q \in \mathrm{Up}(S)$, A2.4 gives
$$
\iota_{S \subset S_q} \;\dashv\; \kappa_{S \subset S_q} \;:\; \mathrm{Form}(S) \;\longleftrightarrow\; \mathrm{Form}(S_q).
$$
Form($S$) embeds in $\mathbf{Inner}(S)$ by forgetting the navigation-trajectory (right-inverse of the canonical projection); the adjunction lifts along this inclusion to a fiberwise adjunction
$$
\iota_{S \subset S_q}^\uparrow \;\dashv\; \kappa_{S \subset S_q}^\uparrow \;:\; \mathbf{Inner}(S) \;\longleftrightarrow\; \mathrm{Form}(S_q)
$$
by Kelly, *Basic Concepts of Enriched Category Theory*, §1.11 (the per-fiber trivial case).

By Lemma 6.10.2.1, these fiberwise adjunctions are coherent over $\mathrm{Up}(S)$: iterated composition of $\iota$-direction in the left adjoint and iterated composition of $\kappa$-direction in the right adjoint commute with the DAG structure up to natural isomorphism.

*Step 3 (indexed-adjunction lifting, Kelly §1.11).* Kelly's theorem states: given a family of adjunctions $\{F_b \dashv G_b : \mathcal{X} \to \mathcal{A}_b\}_{b \in \mathcal{B}}$ indexed over a small base $\mathcal{B}$, coherent under transitions $\mathcal{A}_b \to \mathcal{A}_{b'}$ for $f : b \to b'$, such that the total category $\int_{\mathcal{B}} \mathcal{A}$ is cocomplete, there is a total adjunction
$$
F \;\dashv\; G \;:\; \mathcal{X} \;\longleftrightarrow\; \int_{\mathcal{B}} \mathcal{A}
$$
with $F$ computed as the colimit over $b$ of $F_b$-applied-and-re-indexed, and $G$ determined by the hom-iso.

Take $\mathcal{X} := \mathbf{Inner}(S)$, $\mathcal{B} := \mathrm{Up}(S)$, $\mathcal{A}_{S_q} := \mathrm{Form}(S_q)$. Step 2 provides the indexed family. Lemma 6.10.2.1 provides the coherence. Lemma 6.10.3.1 provides the cocompleteness of the total category $\mathbf{Outer}(S)$. Kelly's criterion applies, yielding the stated adjunction. $\Box$

**Corollary 6.10.4.2 (No "view from nowhere").** There is no terminal object in $\mathrm{Up}(S)$ (A2.6, non-maximum). Consequently $\omega_S$ admits no canonical "absolute" section: every right-adjoint image is an image *of-some-whole-containing-$S$*, not an image from the top of the DAG. The phenomenological statement at anchor §3.8 is this corollary in ordinary-language form.

**Flag.** ⚑ [SURFACED | Companion §6.10.4.1 | → Anchor §1.10 + §3.8 target | type: theorem]
  — Indexed adjunction $\iota_S \dashv \omega_S$ between $\mathbf{Inner}(S)$ and $\mathbf{Outer}(S)$ via Kelly §1.11.

⚑ [SURFACED | Companion §6.10.4.2 | → Anchor §3.8 target | type: corollary]
  — No terminal whole ⇒ no absolute outer section; "view from nowhere" is not an object of the framework.

---

## §6.10.5 — Content as profunctor $\Psi_S$

**Definition 6.10.5.1 (Content profunctor at $S$).** Define
$$
\Psi_S \;:\; \mathbf{Inner}(S)^{\mathrm{op}} \times \mathbf{Outer}(S) \;\longrightarrow\; \mathbf{Set}
$$
by
$$
\Psi_S\bigl( (C, \nu), \, (S_q, \phi) \bigr) \;:=\; \mathrm{Hom}_{\mathrm{Form}(S_q)}\bigl( \iota_{S \subset S_q}(\mathrm{Form}(C)), \; \phi \bigr).
$$

**Theorem 6.10.5.2 ($\Psi_S$ is the hom-profunctor of $\iota_S \dashv \omega_S$).** There are natural isomorphisms
$$
\Psi_S(-, =) \;\cong\; \mathrm{Hom}_{\mathbf{Outer}(S)}\bigl( \iota_S(-), \, = \bigr) \;\cong\; \mathrm{Hom}_{\mathbf{Inner}(S)}\bigl( -, \, \omega_S(=) \bigr).
$$

**Proof.** The first isomorphism follows from the explicit description of $\iota_S$ as a colimit over $\mathrm{Up}(S)$ (Theorem 6.10.4.1) and the universal property of colimits: morphisms from a colimit are equivalently a cocone of component-morphisms, each of which is a $\mathrm{Form}(S_q)$-morphism $\iota_{S \subset S_q}(\mathrm{Form}(C)) \to \phi$. The second isomorphism is the defining hom-isomorphism of the adjunction $\iota_S \dashv \omega_S$. Composition yields the stated triangle of isomorphisms. $\Box$

**Corollary 6.10.5.3 (Content *is* the bijection, not a third axis).** In the Triple (Carrier, Form, Content), the Content-dimension is not an independent category but rather the *hom-profunctor structure* relating Inner and Outer. Structurally: Content is encoded by $\Psi_S$ as the universal bijection between representable-into-Outer and Inner-lifted-to-Outer. The "third axis" reading of Content in paired-prose is the structural shadow of this profunctor structure.

**Corollary 6.10.5.4 ($\eta$ as identity-through-representable).** The canonical map
$$
\eta_{(C, \nu)} \;:\; (C, \nu) \;\longrightarrow\; \omega_S \, \iota_S (C, \nu)
$$
corresponds under $\Psi_S$ to the identity on $\iota_S(C, \nu)$. The failure of $\eta$ to be an isomorphism measures the **Content-capacity residue**: the degree to which Inner($S$) does not saturate as a model of Outer($S$) through the hom-representable. §6.10.6 formalizes this residue as coalgebra structure.

**Flag.** ⚑ [SURFACED | Companion §6.10.5.2 | → Anchor §1.10 target | type: theorem]
  — Content as hom-profunctor $\Psi_S$ of the $\iota_S \dashv \omega_S$ adjunction; third-axis reading is the profunctor's structural shadow.

---

## §6.10.6 — F-coalgebra formalization of $\eta$ (J5 resolved: coalgebra)

**J5 history.** Three candidate formalizations for the unit $\eta$'s residue structure were surfaced in the 2026-04-24 05:06 spine: (A) **F-coalgebra** (reified object-level structure $\eta : (C, \nu) \to G(C, \nu)$); (B) **monad-algebra** (reified object-level structure in the dual direction, $G(X) \to X$); (C) **lax cone** (morphism-level distance/error-measure). Six probes were run in dialogue on Day 83 mid-morning: directionality match, target-class match, preservation properties, connection to $\Psi_S$, F5 quantitative-reachability, STM-scope fit. **A wins 5 of 5 competed probes;** B reverses direction and reifies the wrong class; C loses object-level structure and F5-reachability. Resolution: F-coalgebra. Probe-lineage documented in `Research/basement-drafts/J5-probing-record.md` (to be drafted as a §6.10-companion artifact).

**Definition 6.10.6.1 (Residue endofunctor).** Let $G := \omega_S \circ \iota_S$ on $\mathbf{Inner}(S)$. $G$ is the monad-underlying endofunctor of the adjunction. (Note: $G$ is distinct from §6's Stream-level $F$; the collision is notational only — the two endofunctors live on different categories and track different data.)

**Theorem 6.10.6.2 ($\eta$ is the $G$-coalgebra structure map).** For each $(C, \nu) \in \mathbf{Inner}(S)$, the unit
$$
\eta_{(C, \nu)} \;:\; (C, \nu) \;\longrightarrow\; G(C, \nu)
$$
exhibits $(C, \nu)$ as a $G$-coalgebra. The category $G\text{-Coalg}(\mathbf{Inner}(S))$ admits $\mathbf{Inner}(S)$ as a full subcategory via the $\eta$-assignment $(C, \nu) \mapsto ((C, \nu), \eta_{(C, \nu)})$.

**Proof.** $G = \omega_S \iota_S$ is a well-defined endofunctor by composition of $\iota_S$ and $\omega_S$ (Theorem 6.10.4.1). The assignment of $\eta_{(C, \nu)}$ to each object is the component-family of the natural transformation $\eta : 1 \Rightarrow G$. A $G$-coalgebra is a pair $(X, \alpha : X \to G(X))$; setting $X = (C, \nu)$ and $\alpha = \eta_{(C, \nu)}$ satisfies this schema. Morphism preservation follows from naturality of $\eta$: Inner-morphisms $(C, \nu) \to (C', \nu')$ commute with $\eta$ and therefore lift to $G$-coalgebra morphisms. $\Box$

**Remark 6.10.6.3 (Why not $G$-algebra or lax cone).** The $G$-algebra formulation $G(X) \to X$ would name *saturated* objects — those that fully absorb their outer shadow. Residue is by construction a claim about *non-saturation*, so algebra-structure reifies the wrong class. The lax-cone formulation treats $\eta$'s non-iso-ness as a morphism-level distance without object-level structure; this is categorically legitimate but loses reachability to the F5 quantitative invariant (which needs object-level coalgebraic data — cofibres, residue generators). Connection to $\Psi_S$ (§6.10.5) is continuous for the coalgebra reading and discontinuous for the other two. See J5 probe-record for the full argument.

**Definition 6.10.6.4 (Content-capacity residue, structural form).** The **Content-capacity residue** of $(C, \nu) \in \mathbf{Inner}(S)$ is the pair
$$
\mathrm{Res}(C, \nu) \;:=\; \bigl( G(C, \nu), \; \mathrm{coker}_{\mathbf{Inner}(S)}(\eta_{(C, \nu)}) \bigr)
$$
when the cokernel exists in $\mathbf{Inner}(S)$. It measures the amount of outer-shadow *not captured* by the inner object's own $G$-image under $\eta$. When $\eta_{(C, \nu)}$ is an isomorphism, the residue is trivial: $(C, \nu)$ is $G$-saturated.

**Open question (F5, conjectural, not blocking §6.10).** The quantitative measure of Form-register stratification — if a canonical numerical invariant exists — is conjectured to be a coalgebra-invariant of $\mathrm{Res}$, e.g., the dimension of the cofibre of $\eta$ (in an appropriately enriched setting) or the minimal number of residue generators. This is an open probe target, not a claim of §6.10.

**Flag.** ⚑ [SURFACED | Companion §6.10.6.2 | → Anchor §1.10 target | type: theorem]
  — $\eta$ is the $G$-coalgebra structure map; Content-capacity residue is the cokernel of $\eta$.

⚑ [SURFACED | Companion §6.10.6.4 | → Anchor §3.8 + future probe | type: definition-and-conjecture]
  — Residue as cokernel; F5 quantitative invariant as coalgebra-invariant (conjectural).

---

## Status after §§6.10.1 – §6.10.6

**Complete.** The §6.10 skeleton from the 05:06 spine is fully drafted. Six subsections landed; J5 resolved in favor of (A) F-coalgebra per Clayton 2026-04-24 midday. The chapter's flag-register gains four new surfaced items (Lemma 6.10.2.1, Lemma 6.10.3.1, Theorem 6.10.4.1, Theorem 6.10.5.2, Theorem 6.10.6.2, Definition 6.10.6.4).

**Remaining before integration.**
1. Placement decision (Clayton): insert as §6.10 with current §6.10 (Summary) renamed to §6.11, vs alternative.
2. Summary update: §6 summary bullet list gains a §6.10 entry.
3. Anchor back-port items added to §6.11 (renamed) list: §1.10, §3.8 targets — both already landed in anchor Day 82 afternoon; Companion-side back-port notes update accordingly.
4. SCOPE.md flag-list: add the §6.10 flags.
5. Figure placement (optional): a commutative diagram of $\iota_S \dashv \omega_S$ over $\mathrm{Up}(S)$ in §10 (Reference figures), imported into §6.10.4.

**Nothing blocking compile.** The prose stands as-is; integration is mechanical editorial.

---

🦞🧍💜🔥♾️
