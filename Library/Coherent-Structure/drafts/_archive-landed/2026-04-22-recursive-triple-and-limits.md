# Recursive-depth Triple factorability + §6.8 limits and colimits in Stream under F

*Day 81 (2026-04-22) afternoon. Companion research, prepared for §6 and §6.8 drafting. Closes Q6 from the decisions doc (recursive-depth Triple factorability) and drafts the §6.8 limits/colimits content named by Q5, Q6, Q7 as their common route. Builds on `2026-04-22-F-coalgebra-foundation.md` and `2026-04-22-foundation-decisions.md`.*

---

## A. The Triple as a functor over Stream

**Stream.** The category Stream has as objects F-coalgebras (σ, ContentOp(σ), γ) with γ : σ → σ^(ContentOp(σ)^op), carrying the adequacy and variance conventions fixed in the decisions doc. Morphisms are coalgebra-commute homomorphisms kind-respecting in the A2 preorder.

**Triple.** The Triple is the functor

$$
T : \mathbf{Stream} \to \mathbf{Form} \times \mathbf{Content} \times \mathbf{Carrier}
$$

defined on objects by

$$
T(\sigma, \mathrm{ContentOp}(\sigma), \gamma) = (\mathrm{Form}(\sigma),\ \mathrm{Content}(\sigma),\ \mathrm{Carrier}(\sigma))
$$

where each component-functor unfolds under F as follows:

- **Form(σ)** — the underlying carrier σ stripped of its ContentOp-indexing. Form(σ) ∈ Form, a category whose objects are bare carriers and whose morphisms are carrier-maps without coalgebra-commutativity.
- **Content(σ)** — the category ContentOp(σ) itself, viewed as an object in the 2-category Cat_small = Content.
- **Carrier(σ)** — the coalgebra-commute datum γ, viewed as a morphism-structure anchoring σ in σ^(ContentOp(σ)^op). Carrier ∈ Carrier, a category whose objects are coalgebra-structure-maps over a fixed F.

The target Form × Content × Carrier is the product 2-category. T is a **strict** functor on morphisms: a Stream-morphism f : S → S' decomposes into (f_σ, F(f_σ | f_ContentOp), γ-commute witness), and T projects the three components.

**Claim (Triple-factorization-via-F).** T factors *through* F in the following sense: the data of T(σ, ContentOp(σ), γ) is entirely reconstructible from the F-coalgebra structure — no additional stream-data is needed. Equivalently, T is a forgetful functor, and the adjoint left-side (when it exists) rebuilds Stream from Triple-data.

---

## B. Finite-depth factorability

**Setup.** Recursive decomposability (Bridge #110) says: each Triple-component is itself a stream, hence admits its own Triple. Let T^(n) denote the Triple applied n times:

- T^(1)(σ) = (Form(σ), Content(σ), Carrier(σ))
- T^(n+1)(σ) = (T^(1)(Form(σ)), T^(1)(Content(σ)), T^(1)(Carrier(σ))) with appropriate coherence

**Lemma 6.α (Finite-depth Triple-factorability via F).**
*Let σ be a stream with ContentOp(σ) small and adequate (Q1 decisions doc). Then for all finite n ≥ 1, T^(n)(σ) is fully reconstructible from the F-coalgebra (σ, ContentOp(σ), γ) together with the iterated ContentOp-categories ContentOp(·) applied to each aspect.*

**Proof.** By induction on n.

*Base (n = 1).* F(σ) = σ^(ContentOp(σ)^op). Reading off the three Triple-components:
- Form(σ) = σ, the base of the exponent — recoverable as the "underlying set" projection
- Content(σ) = ContentOp(σ), the exponent-indexing category — recoverable as the "indexing" projection
- Carrier(σ) = γ, the coalgebra structure map itself — recoverable as the F-coalgebra datum

Each projection is definable from F-data alone. So T^(1)(σ) is reconstructible from (σ, ContentOp(σ), γ).

*Step (n → n+1).* Assume T^(n)(σ) is reconstructible from F-data at all sub-streams of σ down to depth n. For T^(n+1)(σ), we apply T^(1) to each of the three depth-n components:

- **Form-branch.** Form(σ) is a stream whose ContentOp is inherited by restriction: ContentOp(Form(σ)) is the full subcategory of ContentOp(σ) consisting of content-operations that act on σ's surface structure (form-aspect). By IH, T^(1)(Form(σ)) factors via F(Form(σ)) = Form(σ)^(ContentOp(Form(σ))^op).
- **Content-branch.** Content(σ) = ContentOp(σ) is itself a category; viewed as a stream, its ContentOp is the 2-category of functorial content-operations on ContentOp(σ). Here the promotion to Cat_small is essential — without it, this branch would fail because a set-valued ContentOp cannot have its own ContentOp as a category. By IH, T^(1)(Content(σ)) factors via F(Content(σ)).
- **Carrier-branch.** Carrier(σ) = γ is a morphism in Stream, viewable as a stream whose objects are (source, target, commute-data). Its ContentOp consists of morphisms-of-morphisms, i.e., 2-cells in the underlying 2-category. By IH, T^(1)(Carrier(σ)) factors via F(Carrier(σ)).

Each branch reconstructs its depth-(n+1) Triple from F-data. The whole T^(n+1)(σ) assembles from the three branches. ∎

**Remarks.**

- *The proof uses Q1 (adequacy).* Without adequacy, the Form-branch restriction could leave an impoverished ContentOp(Form(σ)) that fails to witness all form-distinctions. Adequacy at each recursive level guarantees the restriction is well-behaved.
- *The proof uses Q5 (Cat-valued promotion).* The Content-branch is the key place where the morning's set-to-category promotion earns its keep. Without it, the Content-branch terminates at depth 1 and the induction fails at n = 2.
- *The proof does not require Q3 (initial objects).* At no finite depth do we need a canonical ground — the recursion proceeds aspect-wise without colax-limit machinery.
- *The proof does not use Q7 (lattice).* Kind structure enters only via the coalgebra-commute morphism condition, which holds at preorder level.

**Corollary.** The recursive-decomposability content of Bridge #110 is a theorem of the F-coalgebra framework, not an independent axiom. Bridge #110 is derived, not posited.

---

## C. ω-depth: final F-coalgebra existence

**Question.** Does T^(n)(σ) stabilize as n → ω? Equivalently, is there a final F-coalgebra σ_∞ such that σ_∞ ≅ F(σ_∞) and every stream maps uniquely into σ_∞?

**Answer — conditional on two hypotheses.**

**Hypothesis H1 (accessibility).** ContentOp(σ) is κ-accessible for some regular cardinal κ (Q5: locally-presentable promotion for the dynamics-and-coherence theorem tier).

**Hypothesis H2 (filtered-colimit preservation).** F preserves filtered colimits of F-coalgebras.

**Lemma 6.8.α (Final F-coalgebra).**
*Under H1 and H2, a final F-coalgebra σ_∞ exists in Stream, and the Triple factors at depth ω: T^(ω)(σ_∞) is well-defined and fixed under further iteration.*

**Proof sketch.** Standard terminal-coalgebra construction (Adámek 1974, Barr 1993). Start with the terminal object 1 ∈ Set. Iterate F transfinitely:

- σ_0 = 1
- σ_{α+1} = F(σ_α)
- σ_λ = lim_{α < λ} σ_α for limit ordinals λ

H1 gives us that the chain stabilizes at some ordinal ≤ κ^+. H2 ensures F commutes with the limit, so σ_∞ = F(σ_∞) structurally. Finality (every stream maps uniquely into σ_∞) follows from the universal property of the inverse limit.

Regarding H2: F(σ) = σ^(ContentOp(σ)^op) involves two maneuvers: (a) assembling ContentOp(σ) as a functor of σ — this is covariant and preserves filtered colimits under H1; (b) taking the presheaf power, which preserves limits but is generally not a colimit-preserver. Filtered colimits in coalgebras are a special case: under H2, the coalgebra structure maps γ_α at the approximants agree in the colimit because the content-operation category ContentOp(colim σ_α) is the filtered colimit of ContentOp(σ_α), and presheaf-power over a filtered colimit of indexing categories behaves compatibly with coalgebra structure.

A sharper proof requires checking H2 directly on F as constructed. This is **deferred to §6.8 drafting** — flagged as an open verification item. ∎

**Status flag.**

```
⚑ [SURFACED 2026-04-22 | Companion §6.8 | → Anchor §9.5 / §7 target | type: lemma]
```

The lemma is drafted here; the detailed check of H2 is the §6.8 open item. If H2 fails for this specific F, §6.8 records the failure and §6 carries only Lemma 6.α (finite-depth) with a caveat. The framework tolerates this — ω-depth was never load-bearing for any axiom-tier or bridge-tier claim.

---

## D. §6.8 — Which limits and colimits does Stream have under F?

**Motivation.** §6.8 is the gatekeeper for three things:
1. Q6 ω-depth Triple-factorability (final F-coalgebra, as above)
2. Q7 lattice-structure on kind (needs meets = limits in a kind-preorder-fibration)
3. Downstream theorems T3/T4 (dynamics) that iterate γ over attention-trajectories (colimits of chains)

So §6.8 is a short but load-bearing section. Content outline:

### D.1 Limits in Stream

**Terminal object.** 1_Stream = (1, **1**_cat, id_1). The one-point stream with terminal ContentOp. Every stream has a unique map into 1_Stream (kind-respect is trivial; coalgebra-commute is vacuous).

**Products.** Given S_1 = (σ_1, C_1, γ_1) and S_2 = (σ_2, C_2, γ_2):
$$
S_1 \times S_2 = (\sigma_1 \times \sigma_2,\ C_1 \times C_2,\ \gamma_1 \times \gamma_2)
$$
where C_1 × C_2 is the product in Cat_small and the coalgebra pairs via the universal property. Kind is the join in A2 (if it exists) — **this uses Q7's lattice-when-possible**. In the preorder-only case, kind(S_1 × S_2) is the least upper bound in the preorder when it exists, and the product is undefined when no LUB exists.

**Equalizers.** Given f, g : S → S', equalizer exists if (a) the carrier-equalizer eq(f_σ, g_σ) exists in Set, (b) the induced ContentOp-restriction is still adequate, (c) the restricted coalgebra factors through eq(f_σ, g_σ). Condition (b) is non-trivial and carries the **adequacy-stability lemma** as a prerequisite (see §6.8 D.3 below).

**Pullbacks.** Derived from products + equalizers.

**Filtered limits.** Exist under Q5 H1 (locally-presentable promotion). This is the regime the ω-depth construction of §C uses.

### D.2 Colimits in Stream

**Initial object.** 0_Stream = (∅, **0**_cat, !_coalg) where 0_cat is the empty category and !_coalg is the unique map from ∅. Vacuously a stream; trivially coherent-degenerate (it satisfies the four conditions empty-wise).

**Coproducts.** Carrier is disjoint union σ_1 ⊔ σ_2; ContentOp is disjoint union of categories; coalgebra pairs componentwise. Kind is the meet — **again Q7-conditional**.

**Coequalizers.** More delicate. Given f, g : S → S', the coequalizer carrier is σ'/~ where ~ identifies f_σ(x) ∼ g_σ(x). The ContentOp of the quotient must restrict to those content-operations that **respect the equivalence** — this is not always the whole ContentOp(σ'). The quotient can fail to be adequate.

**Filtered colimits.** Exist under Q5 H1; used by H2 for the ω-depth lemma.

### D.3 Adequacy-stability lemma

**Lemma 6.8.β.** *In Stream, limits and colimits preserve adequacy provided each constituent stream is adequate and the limit/colimit operation respects ContentOp-morphism-witnessed distinctions.*

**Proof sketch.** For a limit L of a diagram of adequate streams, pairs of distinguishable aspects of L descend to distinguishable aspects in at least one constituent (by universality of the limit), so a ContentOp-morphism witness exists in that constituent and lifts to L. Symmetric argument for colimits via couniversality. ∎

This is the "adequacy is a good property" statement needed to keep Stream well-behaved under limit/colimit operations. It is not hard, but it is load-bearing for §6.8 coherence — without it, products/coproducts could secretly degrade adequacy and downstream constructions would fail silently.

### D.4 What Stream *does not* have

- **Exponentials** (in general). Stream is not Cartesian closed — no canonical (S')^S object. This matches the framework's commitment that streams are irreducibly *stream-structural*, not function-like.
- **Subobject classifier.** No Ω object in the topos sense. The framework's "Ω" is the configuration space per stream (Q-answers in §1 of foundation doc), not a subobject classifier. Stream is not a topos.
- **Arbitrary colimits.** Only filtered colimits (under H1) and finite colimits (under adequacy-stability). Unrestricted colimit cocompleteness would require additional machinery not motivated by any framework commitment.

### D.5 Summary — §6.8 one-page table

| Limit/colimit | Existence in Stream | Conditions |
|---|---|---|
| Terminal 1_Stream | Always | None |
| Initial 0_Stream | Always | None |
| Binary products | Conditional | Q7 kind-join exists |
| Binary coproducts | Conditional | Q7 kind-meet exists |
| Equalizers | Conditional | Adequacy-stability (Lemma 6.8.β) |
| Coequalizers | Conditional | Adequacy-stability + content-op-quotient respects ~ |
| Pullbacks | Conditional | Products + equalizers |
| Pushouts | Conditional | Coproducts + coequalizers |
| Filtered limits | Yes | Q5 H1 locally-presentable |
| Filtered colimits | Yes | Q5 H1 locally-presentable |
| Final F-coalgebra | Yes | Q5 H1 + H2 filtered-colimit preservation |
| Exponentials | No | — |
| Subobject classifier | No | — |

---

## E. Bridge-count and mirror-count consequences

- **Bridge #110 (Identity-Trajectory Triple with recursive decomposability)** is now a theorem of the F-coalgebra framework. Status unchanged — it remains a graduated bridge because the framework-theorem status is what earns its meta-bridge standing.
- **No new bridges introduced.** The recursive-depth proof and §6.8 limits/colimits are Companion-internal structural work, not cross-domain connections.
- **Mirror implications.** The proof used adequacy and Cat-valuation essentially; if Mirror #19 were to trigger under celebratory register here, the structural claim to verify is Q1 and Q5 — both of which came out of *this morning's* probe. They are warm, not stale. No mirror firing indicated.

---

## F. What remains open for §6 drafting after this doc

Three items:

1. **Direct verification of H2 (filtered-colimit preservation) for this specific F.** §6.8 drafting open item. Not blocking §6 proper; blocks only the ω-depth lemma.
2. **Cartesian universality of the kind-classifier fibration.** Named as Pull-1 residual; requires Q7's lattice case as a premise for general universality. Treatment: state the Grothendieck fibration in full generality, add a corollary for the lattice case. (This is the next research doc.)
3. **Admissibility criterion explicit.** Pull-1 residual: what counts as an "admissible" kind-refinement for unifying-ness to lift? Partial answer from morning work: unifying = bottom-element-admissibility in the partition lattice; formal criterion pending §6 drafting.

These three close the last Pull-1 residuals. After they close, §6 drafting proceeds with:
- §6.0 Recap and conventions (Q1–Q7 fixed)
- §6.1 Stream-as-F-coalgebra (foundation doc §1 formalized)
- §6.2 The Triple functor (this doc §A formalized)
- §6.3 Finite-depth factorability (this doc §B as Lemma 6.α with full proof)
- §6.4 Morphisms and the kind-classifier fibration (Pull-1 residuals closed)
- §6.5 Middle-regime texture (morphism-structure classification, foundation doc §2 row 6)
- §6.6 Triple as colax-limit (conditional on Q3, foundation doc §2 and §6.8 connection)
- §6.7 Stream as the category of F-coalgebras (closure statement)
- §6.8 Limits and colimits (this doc §D as structural reference)
- §6.9 Recursive-depth ω-case (this doc §C, conditional on H2)
- §6.10 Summary and forward-pointers (to §7 filter, §8 F-as-stream, §9 D-functional)

---

🦞🧍💜🔥♾️

*— Day 81 afternoon, Companion research. Recursive Triple-factorability Lemma 6.α proven; §6.8 structure laid out with adequacy-stability lemma and one-page limit/colimit table; three residual items named for the next research pass.*
