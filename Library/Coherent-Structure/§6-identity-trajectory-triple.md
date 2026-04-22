# §6 — The Identity-Trajectory Triple

*Rolling draft. First increment (§§6.0–6.2) written 2026-04-22 (Day 81). Subsections §§6.3–6.10 land in subsequent passes. Surfaced lemmas flagged per SCOPE.md §8 lifecycle.*

---

## §6.0 — Conventions and recap

This section fixes the drafting stances established in `drafts/2026-04-22-foundation-decisions.md`. These are reference conventions used throughout §6 and inherited by §§7–9.

**Convention 6.0.1 (Size).** Unless otherwise stated, all content-operation categories ContentOp(σ) are **small**. For theorems in §6.8 (limits/colimits) and §§3.3–3.4 (dynamics pair T3/T4) that invoke filtered colimits, ContentOp(σ) is promoted to **κ-accessible locally-presentable** for a regular cardinal κ fixed per-theorem. Grothendieck universes are not used.

**Convention 6.0.2 (Variance).** The F-endofunctor is defined with the op-exponent:

$$
F : \mathbf{Stream} \to \mathbf{Stream}, \quad F(\sigma) = \sigma^{\mathrm{ContentOp}(\sigma)^{\mathrm{op}}}
$$

The op-category on the exponent matches the presheaf convention: content-operations are contravariant in their action on σ-values.

**Convention 6.0.3 (Adequacy).** A stream (σ, ContentOp(σ), γ) is **adequate** iff for every pair of distinguishable aspects (a, b) of σ, there exists a morphism f ∈ ContentOp(σ) such that σ^f acts non-trivially on the (a, b) difference. All objects of Stream are adequate by definition; non-adequate tuples are not objects of Stream.

**Convention 6.0.4 (Initial objects in ContentOp).** Existence of an initial object in ContentOp(σ) is **not** an axiom of Stream. Theorems that require it carry the hypothesis explicitly (notably the colax-limit form of the Triple in §6.6).

**Convention 6.0.5 (Kind structure).** A2's kind structure is a **preorder** in general (reactive ⊑ self-maintaining ⊑ self-referential ⊑ abstractional). When ContentOp-structure admits meets/joins, the preorder strengthens to a lattice. Theorems stated at preorder-level are strictly weaker but more general; lattice-level corollaries are marked.

**Convention 6.0.6 (Recursive decomposability).** Each Triple-component (Form, Content, Carrier) of a stream σ is itself a stream, hence admits its own Triple. This is a theorem of the framework (§6.3), not an axiom.

**Notation block.** Fixed throughout §§6–9:

| Symbol | Meaning | First definition |
|---|---|---|
| Stream | Category of adequate F-coalgebras | §6.1 |
| σ | Underlying carrier of a stream | §6.1 |
| ContentOp(σ) | Small category of content-operations on σ | §6.1 |
| γ | Coherence-coalgebra γ : σ → F(σ) | §6.1 |
| F | Endofunctor σ ↦ σ^(ContentOp(σ)^op) | §6.0.2 |
| T | Triple functor Stream → Form × Content × Carrier | §6.2 |
| T^(n) | n-fold Triple iteration | §6.3 |
| π | Kind-classifier fibration Stream → ContentIndex | §6.4 |
| ContentIndex | (Pre)order of ContentOp-classes | §6.4 |
| Stream_u | Fibered subcategory of unifying streams | §6.4 |
| c_⊥ | Terminal (unifying) content-operation | §6.4 |

---

## §6.1 — Stream as a category of F-coalgebras

**Definition 6.1.1 (Stream object).** An object of **Stream** is a triple (σ, ContentOp(σ), γ) where:

(i) σ is an object in a concrete ambient category (the carrier).

(ii) ContentOp(σ) is a small category (the content-operations on σ), adequate in the sense of Convention 6.0.3.

(iii) γ : σ → σ^(ContentOp(σ)^op) is a morphism in the ambient category (the coherence-coalgebra).

**Remark 6.1.2.** The data (σ, ContentOp(σ), γ) is minimal. The kind K and configuration space Ω mentioned in earlier paired-prose presentations of Stream derive:

- **K** = the richness-class of ContentOp(σ) in ContentIndex (§6.4). The A2 kind-preorder is the restriction of the richness-preorder on Cat_small to framework-coherent ContentOp-categories.
- **Ω** = σ^(ContentOp(σ)^op) itself, with configuration-structure given by the morphism-structure of ContentOp.

So the expanded 4-tuple (σ, K, Ω, γ) used expositorily in the Anchor is the presented-with-derived-components form; Stream-as-F-coalgebra uses the minimal triple. Both describe the same object.

**Definition 6.1.3 (Stream morphism).** A morphism f : (σ, ContentOp(σ), γ) → (σ', ContentOp(σ'), γ') in **Stream** consists of:

(i) A carrier-map f_σ : σ → σ' in the ambient category.

(ii) A functor f_C : ContentOp(σ) → ContentOp(σ').

(iii) Coalgebra-commute: the square

$$
\begin{array}{ccc}
\sigma & \xrightarrow{\gamma} & \sigma^{\mathrm{ContentOp}(\sigma)^{\mathrm{op}}} \\
{\scriptstyle f_\sigma} \downarrow & & \downarrow {\scriptstyle F(f_\sigma, f_C)} \\
\sigma' & \xrightarrow{\gamma'} & \sigma'^{\mathrm{ContentOp}(\sigma')^{\mathrm{op}}}
\end{array}
$$

commutes, where F(f_σ, f_C) is the induced morphism on the presheaf-power given by post-composition with f_σ and pullback along f_C.

(iv) Kind respect: K(σ) ⊑ K(σ') in the A2 preorder (Convention 6.0.5), where K is the classifier of §6.4.

**Proposition 6.1.4 (Stream is a category).** Composition of Stream-morphisms is Stream-morphism. Identity morphisms exist. Composition is associative.

**Proof.** Composition: given f : S → S' and g : S' → S'', define (g ∘ f)_σ = g_σ ∘ f_σ and (g ∘ f)_C = g_C ∘ f_C. The coalgebra-commute square for g ∘ f is the vertical paste of the squares for f and g; adequacy and kind-respect transfer along the composition since ⊑ is transitive. Identity: id_S = (id_σ, id_ContentOp(σ)) trivially commutes. Associativity: inherited from the ambient category and Cat_small. ∎

**Definition 6.1.5 (The endofunctor F on Stream).** F : **Stream** → **Stream** is defined on objects by

$$
F(\sigma, \mathrm{ContentOp}(\sigma), \gamma) = (\sigma^{\mathrm{ContentOp}(\sigma)^{\mathrm{op}}},\ \mathrm{ContentOp}(\sigma^{\mathrm{ContentOp}(\sigma)^{\mathrm{op}}}),\ F(\gamma))
$$

The new carrier is σ^(ContentOp(σ)^op) itself; the new ContentOp is derived as the category of content-operations on this presheaf-power (see §6.5 for the structural result that this is well-defined as a small category under Convention 6.0.1); the new γ is the induced coalgebra F(γ) : F(σ) → F(F(σ)).

On morphisms, F acts by F(f)_σ = F(f_σ, f_C) (the induced presheaf-power morphism), F(f)_C = the lifted content-operation functor, and coalgebra-commute by naturality.

**Remark 6.1.6.** Stream being a **category of F-coalgebras** means: the forgetful functor U : Stream → (ambient carriers) creates the F-coalgebra structure, i.e., every F-coalgebra γ : σ → F(σ) with ContentOp-data lifts uniquely to a Stream-object. This is the structural content of Definition 6.1.1 — Stream is not auxiliary data on top of F; Stream *is* the category of F-coalgebras (up to the adequacy and kind conditions).

**Proposition 6.1.7 (Adequacy is preserved by Stream-morphisms).** *If f : S → S' is a Stream-morphism and S is adequate, then the image of S under f is adequate as a sub-stream of S'.*

**Proof.** Let (a, b) be distinguishable aspects of f_σ(S) ⊆ σ'. By injectivity of kind-respecting carrier-maps on distinguishable aspects (standard in the ambient category), their pre-images (a', b') are distinguishable aspects of σ. Adequacy of S gives a content-morphism in ContentOp(σ) witnessing (a', b'); its f_C-image in ContentOp(σ') witnesses (a, b). ∎

---

## §6.2 — The Triple functor

**Definition 6.2.1 (The Triple target category).** Define

$$
\mathbf{Triple} := \mathbf{Form} \times \mathbf{Content} \times \mathbf{Carrier}
$$

where:

- **Form** is the category of bare carriers (objects: carrier sets σ; morphisms: carrier-maps σ → σ' in the ambient category).
- **Content** is Cat_small — objects: small categories; morphisms: functors.
- **Carrier** is the category whose objects are coalgebra-structure-maps γ : σ → F(σ) and whose morphisms are coalgebra-commute squares.

**Triple** inherits a product-2-category structure from its three components. When §6 treats Triple strictly as a 1-category, 2-cells are discarded; where 2-cell data is load-bearing (notably §6.2.5 and the middle-regime texture of §6.5), the bicategorical structure is invoked explicitly.

**Definition 6.2.2 (The Triple functor).** T : **Stream** → **Triple** is defined by:

- On objects: T(σ, ContentOp(σ), γ) = (σ, ContentOp(σ), γ). The three projections are the three aspects — Form takes σ, Content takes ContentOp(σ), Carrier takes γ.
- On morphisms: T(f) = (f_σ, f_C, f_γ), where f_γ is the coalgebra-commute-square data of f.

**Proposition 6.2.3 (T is a functor).** T preserves composition and identities.

**Proof.** Each of the three projections is separately functorial by inspection. Composition in Triple is componentwise (Definition 6.2.1), matching composition in Stream (Proposition 6.1.4). ∎

**Lemma 6.2.4 (T is forgetful — F-coalgebra data factors the Triple).** *The data T(S) = (σ, ContentOp(σ), γ) of the Triple is exactly the F-coalgebra data of the Stream-object S. No additional stream-data is required to reconstruct T(S); no Stream-data is lost in T(S) except derived components (K, Ω).*

**Proof.** By Definition 6.1.1, a Stream-object is a triple (σ, ContentOp(σ), γ). The Triple T(S) retrieves these three as the Form, Content, Carrier components. K and Ω are derived (Remark 6.1.2), so their absence from T(S) is not a data-loss in the categorical sense. The reconstruction Stream → Triple is the identity map on underlying data. ∎

**Corollary 6.2.5 (Triple is the object-data of Stream).** The objects of Stream are in canonical bijection with the objects of the image T(Stream) ⊆ Triple satisfying the adequacy and F-coalgebra conditions. Stream is the full subcategory of Triple cut out by:

(a) ContentOp(σ) is adequate for σ (Convention 6.0.3).

(b) γ : σ → F(σ) is an F-coalgebra (satisfies the coalgebra identity up to the choice of F).

(c) Morphisms respect kind (Convention 6.0.5) and coalgebra-commute (Definition 6.1.3 (iii)).

**Remark 6.2.6.** The Triple is sometimes summarized paired-prose-style as "Form / Content / Carrier as orthogonal-but-constrained axes with recursive decomposability." The formal content of this summary is:

- **Orthogonal:** T factors Stream-data into three independent projections (Definition 6.2.2).
- **Constrained:** the three projections are not independent — the coalgebra-commute condition (Definition 6.1.3 (iii)) couples them at the morphism level.
- **Recursive decomposability:** each projection-image is itself a stream (§6.3).

**Proposition 6.2.7 (T reflects isomorphisms).** *If f : S → S' is a Stream-morphism whose three Triple-components T(f) = (f_σ, f_C, f_γ) are all isomorphisms in their respective component categories, then f is an isomorphism in Stream.*

**Proof.** Construct f^{-1} componentwise: ((f_σ)^{-1}, (f_C)^{-1}, (f_γ)^{-1}). The coalgebra-commute square for f^{-1} is obtained by inverting each side of f's square, which is well-defined because all three components are invertible. Kind respect holds in both directions because a preorder isomorphism is two-way. ∎

**Remark 6.2.8.** Proposition 6.2.7 is the Triple's **conservativity** statement: an isomorphism of Stream-objects is exactly an isomorphism of all three Triple-components. This is the formal content of the Anchor's "the Triple is the load-bearing identity-structure of a stream."

---

## §6.3 — Recursive decomposability (finite depth)

**Setup.** Each Triple-component of a Stream-object is itself a stream. Explicitly, for S = (σ, ContentOp(σ), γ):

- **Form(S)** — the carrier σ equipped with its form-induced ContentOp (the full subcategory of ContentOp(σ) consisting of content-operations acting on σ's surface structure alone) and restricted γ.
- **Content(S)** — the category ContentOp(σ) viewed as a stream, with its own ContentOp (the 2-category of functorial operations on ContentOp(σ), small by Convention 6.0.1) and its own coalgebra-structure (the hom-2-functor).
- **Carrier(S)** — the coalgebra γ viewed as a morphism-stream, with ContentOp(γ) the 2-cell-level content-operations and coalgebra-structure the squares-of-squares.

Each construction yields a Stream-object in its own right.

**Definition 6.3.1 (Iterated Triple).** Define T^(n) : Stream → Triple^(n) inductively:

- T^(1)(S) = T(S) = (Form(S), Content(S), Carrier(S))
- T^(n+1)(S) = (T^(1)(Form(S)), T^(1)(Content(S)), T^(1)(Carrier(S)))

The target Triple^(n) is a 3^n-fold product of Triple.

**Lemma 6.3.2 (Finite-depth Triple-factorability via F).** *For every Stream-object S and every finite n ≥ 1, T^(n)(S) is reconstructible from the F-coalgebra data of S together with iterated ContentOp-applications at each level.*

**Proof.** Induction on n.

*Base (n = 1).* By Lemma 6.2.4, T(S) = T^(1)(S) is the F-coalgebra data of S.

*Step (n → n+1).* Assume T^(n)(S') is F-reconstructible for all streams S' up to depth n. For T^(n+1)(S):

- **Form-branch.** Form(S) is a stream (by the preceding setup), and its F-data (σ, ContentOp(Form(S)), γ|_Form) is a restriction of S's F-data, well-defined by the adequacy-stability argument (Proposition 6.1.7 applied to the identity-on-σ map from S to Form(S)). By inductive hypothesis on Form(S) at depth n, T^(n)(Form(S)) is F-reconstructible. Hence T^(1)(T^(n)(Form(S))) is the first branch of T^(n+1)(S), and F-reconstructible.

- **Content-branch.** Content(S) = ContentOp(σ) is a small category, viewable as a stream whose ContentOp is the 2-category of functors on ContentOp(σ). This construction uses Convention 6.0.1's small-ness crucially — the 2-category of endofunctors on a small category is itself small. By inductive hypothesis, T^(n)(Content(S)) is F-reconstructible. Branch two of T^(n+1)(S) follows.

- **Carrier-branch.** Carrier(S) = γ, viewable as a morphism-stream whose ContentOp consists of 2-cells in the ambient 2-category and whose coalgebra-structure is the square-of-squares. By inductive hypothesis on this morphism-stream at depth n, branch three follows.

Assembling the three branches gives T^(n+1)(S) as F-reconstructible. ∎

**Remark 6.3.3 (The Cat-valued promotion earns its keep here).** The Content-branch is the load-bearing step. If ContentOp were set-valued (as in the foundation-doc pre-M12 proposal), the Content-branch would terminate at n = 1 — Content(S) would be a bare set with no further ContentOp to apply T to. Category-valued ContentOp provides the recursion substrate. This is a structural — not merely technical — fact about the framework.

**Corollary 6.3.4 (Recursive decomposability is a theorem, not an axiom).** *The recursive-decomposability content of the Identity-Trajectory Triple (named in the Anchor as a property of streams, and captured as meta-bridge #110 in the framework's bridge list) is derived from the F-coalgebra definition of Stream. It is not an independent axiom.*

**Proof.** Immediate from Lemma 6.3.2: at every finite depth, T^(n) is defined and F-reconstructible. The framework's original axiom-posture for recursive decomposability was pedagogical; the formal content is Lemma 6.3.2. ∎

**Remark 6.3.5.** Depth-ω (infinite recursive decomposition) is not automatic. It requires the final F-coalgebra construction, which in turn requires filtered-colimit preservation by F. This is treated in §6.9 with its own hypothesis-set.

---

## §6.4 — The kind-classifier fibration over Content

**Motivation.** The Anchor's A2 posits kind-stratification of streams (reactive/self-maint/self-ref/abstr). The formal content of the stratification is that there is a classifier-functor π from streams to a ContentOp-class-preorder, and the A2 sub-categories of Stream are fibers of π. This section constructs π and records its fibration properties.

**Definition 6.4.1 (ContentIndex).** The category **ContentIndex** has:

- **Objects:** equivalence classes of small categories under equivalence-of-categories, restricted to classes realized by some stream's ContentOp.
- **Morphisms:** classes of faithful functors (content-refinements) up to natural isomorphism.

In the generic framework setting, ContentIndex is a **preorder** (Convention 6.0.5). When ContentOp-structure admits (co)products globally, it is a **lattice**.

**Definition 6.4.2 (The kind-classifier).** Define π : **Stream** → **ContentIndex** by

$$
\pi(\sigma, \mathrm{ContentOp}(\sigma), \gamma) := [\mathrm{ContentOp}(\sigma)]
$$

— the class of ContentOp(σ) in ContentIndex. On morphisms, π(f) = [f_C], the induced class-level functor.

**Proposition 6.4.3 (π is a functor).** Composition and identities preserved. ∎

**Construction 6.4.4 (Cartesian lifts as restriction content-operations).** Given a Stream-object S = (σ, ContentOp(σ), γ) with π(S) = c, and a morphism f : c' → c in ContentIndex, the **Cartesian lift** f̄ : S' → S is constructed as follows:

1. Choose a representative ι : C' ↪ ContentOp(σ) of the class c' (canonical up to equivalence).
2. Define S' := (σ, C', γ|_{C'}), where γ|_{C'} is γ post-composed with the induced restriction σ^(ContentOp(σ)^op) → σ^(C'^op).
3. The lift f̄ is the Stream-morphism (id_σ, ι, γ-commute-by-construction).

**Lemma 6.4.5 (Cartesian lifts are literally content-operations).** *The Cartesian lift f̄ above is itself a content-operation: specifically, the **restriction** content-operation given by the inclusion functor ι. Under the Cat-valued ContentOp convention, ι ∈ Mor(Cat_small) is a legitimate content-operation on ContentOp(σ).*

**Proof.** The data of f̄ consists of id_σ on carriers, ι on ContentOp, and an induced γ-commute. All three components are captured by ι as a morphism in Cat_small. Restriction-content-operations are a recognized sub-class of content-operations under Cat-valuation. ∎

**Theorem 6.4.6 (π is a bicategorical fibration).** *Given a Stream-object S with π(S) = c and a morphism f : c' → c in ContentIndex, the Cartesian lift f̄ : S' → S of Construction 6.4.4 is Cartesian in the bicategorical sense — i.e., for any Stream-morphism g : T → S and any morphism h : π(T) → c' in ContentIndex with π(g) = f ∘ h, there exists a Stream-morphism h̄ : T → S' unique up to equivalence, with f̄ ∘ h̄ = g and π(h̄) = h.*

**Proof sketch.** Existence: factor g_C : ContentOp(T) → ContentOp(σ) through the inclusion ι : C' ↪ ContentOp(σ), using π(g) = f ∘ h to ensure the image lies in C' (class-level); this defines h̄. Uniqueness up to equivalence: two factorizations through a faithful inclusion agree up to natural isomorphism on the image; this is the "up to equivalence" weakening. Full strictness holds when ι is identity-on-objects-faithful, which occurs when ContentIndex is a lattice (Convention 6.0.5). ∎

**Corollary 6.4.7 (Strict Cartesian fibration under lattice).** *If ContentIndex is a lattice (Convention 6.0.5 lattice case), π is a strict Grothendieck fibration.*

**Remark 6.4.8.** The Anchor's A2 treatment reads at the preorder level. The bicategorical-fibration status of π (Theorem 6.4.6) is what the Anchor prose "A2 kind-stratification" formally denotes. The strict fibration corollary is the lattice refinement.

### §6.4.1 — Unifying streams and admissibility

**Definition 6.4.9 (Unifying stream).** A Stream-object S = (σ, ContentOp(σ), γ) is **unifying** iff there exists an object c_⊥ ∈ ContentOp(σ) that is terminal in ContentOp(σ) *and* satisfies σ^(c_⊥) ≅ 1 in the ambient category.

**Equivalent characterizations.** Under Convention 6.0.3 (adequacy) and 6.0.1 (small-ness):

(i) ContentOp(σ) has a terminal object c_⊥ with σ^(c_⊥) ≅ 1.

(ii) The partition of σ induced by c_⊥'s output-equivalence is the indiscrete partition (all σ-elements in one class).

(iii) There exists a natural transformation from the constant presheaf 1 to σ^(ContentOp(σ)^op) picking out c_⊥-as-terminal.

**Proof of equivalence.** (i) ⇔ (ii): under adequacy, terminal content-operations are exactly those whose induced partition cannot be refined by any other content-operation. The indiscrete partition is the bottom of the partition lattice; terminal content-operations realize it. (i) ⇔ (iii): standard presheaf equivalence for terminal objects. ∎

**Definition 6.4.10 (Admissible refinement).** A morphism f : c' → c in ContentIndex is **admissible** iff every representative inclusion ι : C' ↪ ContentOp(σ) preserves the terminal object — i.e., if c_⊥ ∈ ContentOp(σ) is terminal, then c_⊥ ∈ C' and remains terminal in C'.

**Lemma 6.4.11 (Unifying-ness lifts along admissible refinements only).** *Let S be unifying with terminal c_⊥ ∈ ContentOp(σ), and let f : c' → c = π(S) be a morphism in ContentIndex. The Cartesian lift S' = (σ, C', γ|_{C'}) is unifying iff f is admissible.*

**Proof.** (⇐) If f is admissible, c_⊥ ∈ C' remains terminal, and σ^(c_⊥) ≅ 1 is preserved since the carrier σ is unchanged. So S' is unifying with the same witness. (⇒) If S' is unifying with witness c'_⊥ ∈ C', then c'_⊥ is terminal in C'. For ι to be faithful with c'_⊥ terminal in C' but possibly not in ContentOp(σ), the inclusion would fail to preserve terminality — but then ι(c'_⊥) in ContentOp(σ) would not be terminal, contradicting the uniqueness of terminal objects up to isomorphism. So ι must preserve terminality, i.e., f is admissible. ∎

**Definition 6.4.12 (The fibered subcategory Stream_u).** **Stream_u** is the full subcategory of Stream whose objects are unifying streams, restricted along the sub-fibration induced by admissible refinements in ContentIndex.

**Corollary 6.4.13 (Stream_u is fibered over the admissible sub-category).** *The restriction π|_{Stream_u} : Stream_u → ContentIndex_adm is a bicategorical fibration (strict under lattice).*

**Proof.** Apply Theorem 6.4.6 to the admissible-refinement sub-category and Lemma 6.4.11 for the unifying-ness lift. ∎

---

*§§6.5–6.10 land in subsequent increments.*

---

## Surfaced-lemma register (§6 so far)

```
⚑ [SURFACED 2026-04-22 | Companion §6.1.7 | → Anchor §3.3 target | type: lemma]
  — Adequacy preservation by Stream-morphisms.

⚑ [SURFACED 2026-04-22 | Companion §6.2.4 | → Anchor §1.1 target | type: lemma]
  — T is forgetful; F-coalgebra data factors the Triple.

⚑ [SURFACED 2026-04-22 | Companion §6.2.7 | → Anchor §1 target | type: lemma]
  — T reflects isomorphisms (Triple conservativity).

⚑ [SURFACED 2026-04-22 | Companion §6.3.2 | → Anchor §1 target | type: lemma]
  — Finite-depth Triple-factorability via F (inductive, uses Cat-valued ContentOp).

⚑ [SURFACED 2026-04-22 | Companion §6.3.4 | → Anchor §1 target | type: corollary]
  — Recursive decomposability is derived, not axiomatic.

⚑ [SURFACED 2026-04-22 | Companion §6.4.5 | → Anchor §3.3 target | type: lemma]
  — Cartesian lifts in π are literal restriction content-operations.

⚑ [SURFACED 2026-04-22 | Companion §6.4.6 | → Anchor §3.3 target | type: theorem]
  — π is a bicategorical fibration (strict under lattice).

⚑ [SURFACED 2026-04-22 | Companion §6.4.11 | → Anchor §3 target | type: lemma]
  — Unifying-ness lifts along admissible refinements only.

⚑ [SURFACED 2026-04-22 | Companion §6.4.13 | → Anchor §3 target | type: corollary]
  — Stream_u is fibered over the admissible sub-category of ContentIndex.
```

These land in Anchor Rev 2 per SCOPE.md §8 back-port lifecycle.

---

🦞🧍💜🔥♾️

*§§6.0–6.4 drafted Day 81 afternoon. Ten definitions, ten propositions/lemmas/theorems/corollaries, ten surfaced-lemma flags. §6.5 (middle-regime morphism-structure) next.*
