# §6 — The Identity-Trajectory Triple

*Written 2026-04-22 (Day 81). Incorporates the F-coalgebra foundation, kind-classifier fibration, Pull 1 residuals, trifurcation formalization, colax-limit form, cocompletion-and-closure theorem, category-level limits/colimits, and C-size regime analysis. Surfaced lemmas flagged per SCOPE.md §8 lifecycle.*

---

## §6.0 — Conventions and recap

This section fixes the drafting stances established in `drafts/2026-04-22-foundation-decisions.md`. These are reference conventions used throughout §6 and inherited by §§7–9.

**Convention 6.0.1 (Size).** Unless otherwise stated, all content-operation categories ContentOp(σ) are **small**. For theorems in §6.8 (limits/colimits) and §3.3 (dynamics pair T3/T4) that invoke filtered colimits, ContentOp(σ) is promoted to **κ-accessible locally-presentable** for a regular cardinal κ fixed per-theorem. Grothendieck universes are not used.

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

The new carrier is σ^(ContentOp(σ)^op) itself; the new ContentOp is derived as the category of content-operations on this presheaf-power (see §6.7 for the structural result that this is well-defined as a small category under Convention 6.0.1); the new γ is the induced coalgebra F(γ) : F(σ) → F(F(σ)).

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

**Corollary 6.3.4 (Recursive decomposability is a theorem, not an axiom).** *The recursive-decomposability content of the Identity-Trajectory Triple (named in the Anchor as a property of streams, and captured as meta-bridge M3 in the framework's bridge list) is derived from the F-coalgebra definition of Stream. It is not an independent axiom.*

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

## §6.5 — Middle-regime morphism-structure (trifurcation)

**Motivation.** The Corpus contains a phenomenological finding (Day 81 morning): the contemplative "ultimate" has internal texture. Scotist, Palamite, and Advaitin traditions describe distinct ultimate-structures that do not collapse into a single coherence-equivalence class. Under the F-coalgebra framework, the texture localizes in the **morphism-structure of ContentOp at the terminal content-operation**. This section records the formal content.

**Setup.** Let S be a unifying stream with terminal c_⊥ ∈ ContentOp(σ). The ambient morphism-structure around c_⊥ in ContentOp(σ) — i.e., the category of morphisms into and out of c_⊥ — carries additional data beyond c_⊥'s terminality.

**Definition 6.5.1 (Ultimate-structure of a unifying stream).** The **ultimate-structure** of a unifying stream S, denoted Ult(S), is the slice category ContentOp(σ) / c_⊥ together with the distinguished-object data (c_⊥ is terminal) and the induced 2-cell structure from Cat_small.

**Remark 6.5.2.** Ult(S) is small (Convention 6.0.1), has a terminal object (c_⊥), and is non-trivial iff ContentOp(σ) has non-identity morphisms into c_⊥. The last condition is precisely what distinguishes framework-coherent unifying streams from degenerate ones.

**Definition 6.5.3 (Middle-regime classes).** Three distinguished Ult-structures arise in the Companion's phenomenological case list:

- **Scotist class.** Ult(S) has **internal-compatibility morphisms**: every pair of content-operations c_1, c_2 mapping to c_⊥ admits a common refinement c_{1,2} also mapping to c_⊥, with the refinement structure univocal (single morphism-type to c_⊥ up to natural isomorphism). Formalism: Ult(S) is a finite-product-closed sub-category with products lifting to c_⊥.

- **Palamite class.** Ult(S) has **essence/energy level-morphisms**: a distinguished sub-object c_essence ↪ c_⊥ with the property that morphisms into c_⊥ factor through either c_essence (essence-morphisms) or the complement c_energies (energy-morphisms), with no direct path from energy-level objects to essence. Formalism: Ult(S) admits a proper factorization system (essence / energy) with distinguished terminal.

- **Advaitin class.** Ult(S) has **saguna-to-nirguna projection morphisms**: every content-operation into c_⊥ factors through a unique "with-attribute" intermediate c_saguna, and the composite c → c_saguna → c_⊥ is the same as the direct c → c_⊥ up to a projection natural transformation. Formalism: Ult(S) admits a reflective subcategory structure with c_⊥ as reflector-terminal and c_saguna as reflection-image.

**Theorem 6.5.4 (Three middle-regime classes are framework-distinct).** *The three classes of Definition 6.5.3 are pairwise non-equivalent as Ult-structures: no Ult(S) is simultaneously Scotist, Palamite, and Advaitin in the strong (structural) sense unless Ult(S) is terminal.*

**Proof sketch.** A strong-sense Scotist structure requires finite products lifting to c_⊥ without intermediate sub-objects; this conflicts with a Palamite essence/energy factorization, which mandates a proper sub-object c_essence ⊊ c_⊥. Similarly, Advaitin reflection requires a non-trivial c_saguna intermediate, incompatible with Scotist univocal direct morphisms. Terminal Ult(S) (a single object with identity morphism) trivially satisfies all three vacuously. ∎

**Remark 6.5.5 (Why the framework predicts texture).** The derivation of this theorem is important for the framework's self-assessment. A naïve reading of the Coherence Principle might suggest that all coherent unifying streams coincide at the ultimate. The framework does not predict this — it predicts that the morphism-structure of Ult(S) carries meaningful information, and that distinct morphism-structures correspond to distinct phenomenological ultimates. The Scotist/Palamite/Advaitin texture is a *prediction* of the framework, confirmed by the contemplative-traditions literature, not a failure to collapse.

**Corollary 6.5.6 (Cross-tradition translation).** *Morphism-structures of different middle-regime classes do not translate into each other except by data-loss. Specifically, a Scotist → Palamite translation must collapse univocal direct morphisms into essence/energy factorizations, losing the product-structure; a Palamite → Advaitin translation must collapse essence-factorization into reflector-morphisms, losing the essence/energy distinction.*

**Proof.** Each class's distinguishing feature (product-closure, essence/energy factorization, saguna-reflection) is a structural property not definable in the other classes without adding or removing morphism-data. Translation preserves composition and identities but not these structural features. ∎

**Remark 6.5.7 (A48 correspondence, scope).** §6.5 corresponds to the structural-prediction form of open-question A48: the correspondence between the three contemplative middle-regime classes and Ult-structural types holds as a framework-level prediction, not as a universal categorical-limit theorem. A strong universal-limit form is parked for a later pass.

---

## §6.6 — The Triple as colax-limit (conditional)

**Motivation.** The original Anchor exposition (Day 77 axiomatic closure) framed the Triple as a **colax-limit** of a three-pronged diagram in Cat. This is a sharpening of Theorem 6.2.5 (Stream as a full subcategory of Triple), conditional on ContentOp having enough structure.

**Hypothesis 6.6.0.** *For the results of this section, assume ContentOp(σ) admits an initial object I (Convention 6.0.4 — carried as hypothesis per-theorem).*

**Definition 6.6.1 (The colax-limit diagram).** Define a three-object diagram D : J → Cat as follows:

- J is the walking span-category: three objects {•_F, •_C, •_Cr} and two morphisms •_F → • ← •_C, •_Cr → •, where • is an auxiliary apex object representing the coalgebra-commute condition.
- D(•_F) = Form, D(•_C) = Content, D(•_Cr) = Carrier, D(•) = Form × Content × Carrier (with the three projections as D's structure).

**Theorem 6.6.2 (Triple as colax-limit, under Hypothesis 6.6.0).** *Under the initial-object hypothesis on ContentOp(σ), Stream embeds into the colax-limit colaxlim D of the diagram above, and the embedding is an equivalence of categories onto the full sub-2-category of adequate F-coalgebras.*

**Proof sketch.** colaxlim D consists of cones (F_0, C_0, Cr_0, α_F, α_C, α_Cr) where F_0, C_0, Cr_0 are objects in Form, Content, Carrier respectively, and α_∗ are colax-natural-transformations to the apex. A Stream-object (σ, ContentOp(σ), γ) supplies (σ, ContentOp(σ), γ) as the three objects, and the coalgebra-commute condition provides the colax-natural-transformation data with *initial-object-anchored* structure: the initial I ∈ ContentOp(σ) serves as the tip of the colax cone, giving a canonical base-point from which all content-operations flow.

The embedding Stream ↪ colaxlim D is fully faithful by Proposition 6.2.7 (T reflects isomorphisms). Essential surjectivity onto adequate F-coalgebras holds because the colax structure precisely encodes the coalgebra-commute condition. ∎

**Remark 6.6.3 (Why this requires initial objects).** Without an initial object in ContentOp(σ), the colax cone has no anchor-point, and the colax-limit construction produces a larger object than Stream — one that includes "ungrounded" Triple-tuples without a canonical base content-operation. The initial-object hypothesis makes the cone well-pointed and the colax-limit equivalent to Stream.

**Remark 6.6.4 (General case without initial objects).** For streams without initial ContentOp, Theorem 6.2.5 (Stream as a full subcategory of Triple) is the correct structural description. The colax-limit form is a sharpening available under the additional hypothesis. Both are drafting-valid; the paired-prose Anchor uses the colax-limit form wherever it is applicable, with the un-conditioned statement as fallback.

**Corollary 6.6.5 (The Triple's "canonical base" is the initial content-operation).** *When Hypothesis 6.6.0 holds, the initial object I ∈ ContentOp(σ) is the distinguished "ground" content-operation from which all stream-internal content-operations are reachable. This formalizes the paired-prose notion of a stream's "ground state" or "base coherence."*

**Proof.** Immediate from the colax-limit anchor-point construction in Theorem 6.6.2. ∎

---

## §6.7 — Stream as the category of F-coalgebras (closure)

**Motivation.** Theorem 6.2.5 stated that Stream is a full subcategory of Triple cut out by three conditions (adequacy, F-coalgebra identity, kind-respecting morphisms). Theorem 6.6.2 refined this (under a hypothesis) to a colax-limit equivalence. This section closes the structural characterization by stating the main equivalence.

**Theorem 6.7.1 (Stream = F-Coalg_ad).** *Let F-Coalg denote the category of F-coalgebras in the ambient Set-like category, and let F-Coalg_ad ⊆ F-Coalg be the full subcategory of adequate F-coalgebras satisfying kind-respect on morphisms. Then:*

$$
\mathbf{Stream} \simeq \mathbf{F\text{-}Coalg}_{\mathrm{ad}}
$$

*as categories.*

**Proof.** By Definition 6.1.1, every Stream-object is an F-coalgebra with adequacy and kind-data. Conversely, every F-coalgebra γ : σ → F(σ) with adequate ContentOp(σ) lifts to a Stream-object by setting K = [ContentOp(σ)] and Ω = F(σ) (Remark 6.1.2). The lift is bijective on objects and morphisms by Definition 6.1.3. Functoriality of the equivalence holds because composition in both categories is componentwise (Proposition 6.1.4). ∎

**Corollary 6.7.2 (Closure).** *The category Stream is closed under the F-coalgebra structure — every construction producing an F-coalgebra on some σ with adequate ContentOp produces a Stream-object.*

**Proof.** Immediate from Theorem 6.7.1. ∎

**Remark 6.7.3 (Implication for framework construction).** Closure under F-coalgebra operations means that Stream is algebraically well-behaved under coalgebraic constructions — products (§6.8), equalizers (§6.8), filtered colimits (§6.8), and the self-reference closure of §8 all produce Stream-objects when their inputs are Stream-objects. The framework does not need to re-check adequacy and kind-respect at each construction; these properties transfer automatically under Stream-morphisms (Proposition 6.1.7).

---

## §6.8 — Limits and colimits in Stream under F

**Conventions recalled.** For this section, size/variance/adequacy follow §6.0. Kind-structure is the preorder of Convention 6.0.5; lattice-level results are flagged explicitly.

### §6.8.1 — Limits

**Proposition 6.8.1 (Terminal object).** *The terminal object 1_Stream := (1, **1**_cat, id_1) exists in Stream, where 1 is the terminal carrier, **1**_cat is the terminal small category (one object, identity morphism), and id_1 is the unique coalgebra-structure-map.*

**Proof.** Uniqueness of maps into 1_Stream: f_σ factors uniquely through 1; f_C factors uniquely through **1**_cat; coalgebra-commute is vacuous because γ_{1_Stream} is identity. Kind-respect is trivial because K(1_Stream) is the top of the preorder. ∎

**Proposition 6.8.2 (Products, conditional on kind-join).** *Given Stream-objects S_1, S_2 with K(S_1), K(S_2) admitting a join K_∨ in the A2 preorder, the product S_1 × S_2 exists in Stream with:*

$$
S_1 \times S_2 = (\sigma_1 \times \sigma_2,\ \mathrm{ContentOp}(S_1) \times \mathrm{ContentOp}(S_2),\ \gamma_1 \times \gamma_2)
$$

*with the cartesian product of coalgebras and kind K_∨.*

**Proof sketch.** Universal property: a pair (g_1, g_2) : T → S_1, T → S_2 induces a unique (g_1, g_2)_* : T → S_1 × S_2 by pairing carrier-maps and ContentOp-functors componentwise. Coalgebra-commute transfers by pairing. Kind-respect K(T) ⊑ K_∨ requires K_∨ to exist as a join — hence the conditional. ∎

**Proposition 6.8.3 (Equalizers, conditional on adequacy-stability).** *Given parallel Stream-morphisms f, g : S → S', the equalizer exists in Stream provided the carrier-equalizer eq(f_σ, g_σ) carries an adequate ContentOp-restriction.*

**Proof sketch.** Carrier: eq(f_σ, g_σ) ⊆ σ. ContentOp: the sub-category of ContentOp(σ) consisting of content-operations that agree after mapping by f_C and g_C. Coalgebra: restricted γ. Adequacy-stability (Lemma 6.8.β below) gives the conditional. ∎

**Lemma 6.8.β (Adequacy-stability under limits/colimits).** *Limits and colimits in Stream preserve adequacy, provided each constituent stream is adequate and the limit/colimit operation respects ContentOp-morphism-witnessed distinctions.*

**Proof.** For a limit L, distinguishable aspects of L descend to distinguishable aspects in at least one constituent (by universality); ContentOp-morphism witnesses lift to L via the limit-cone. Dual argument for colimits via the couniversal property. ∎

**Proposition 6.8.4 (Filtered limits under locally-presentable promotion).** *When ContentOp is promoted to κ-accessible locally-presentable (Convention 6.0.1), filtered limits exist in Stream.*

### §6.8.2 — Colimits

**Proposition 6.8.5 (Initial object).** *The initial object 0_Stream := (∅, **0**_cat, !) exists, where ∅ is the empty carrier, **0**_cat is the empty category, and ! is the unique map from ∅.*

**Proof.** Vacuous satisfaction of all Stream conditions. ∎

**Proposition 6.8.6 (Coproducts, conditional on kind-meet).** *Given S_1, S_2 with K(S_1), K(S_2) admitting a meet K_∧, the coproduct S_1 + S_2 exists with disjoint-union carriers, disjoint-union ContentOp, and componentwise coalgebra.*

**Proposition 6.8.7 (Coequalizers, conditional on quotient-adequacy).** *Given f, g : S → S', the coequalizer exists provided the quotient ContentOp — consisting of content-operations that respect the generated equivalence — is adequate for σ'/∼.*

**Proposition 6.8.8 (Filtered colimits under locally-presentable promotion).** *Under Convention 6.0.1's locally-presentable promotion, filtered colimits exist in Stream.*

### §6.8.3 — What Stream *does not* have

**Proposition 6.8.9 (No exponentials in general).** *Stream is not Cartesian closed; there is no canonical (S')^S object for arbitrary S, S' ∈ Stream.*

**Proof sketch.** Standard counterexample from coalgebra theory: exponentials of coalgebras require specific smallness and commutativity conditions not implied by Stream's definition. The F-coalgebra structure fixes γ-data that does not naturally lift to a function-space. ∎

**Proposition 6.8.10 (No subobject classifier).** *Stream does not have a subobject-classifier object Ω_sub in the topos sense.*

**Remark 6.8.11 (The framework's "Ω" is not Ω_sub).** The framework's configuration space Ω for a stream (named in earlier expositions as the 4-tuple's third component, derived in Remark 6.1.2 as σ^(ContentOp(σ)^op)) is not a subobject classifier; it is the evaluation-space of the F-structure. The names coincide accidentally; no toposic interpretation is intended.

### §6.8.4 — Summary table

| Limit/colimit | Existence | Condition |
|---|---|---|
| Terminal 1_Stream | yes | — |
| Initial 0_Stream | yes | — |
| Products S_1 × S_2 | conditional | kind-join exists (Q7 lattice case) |
| Coproducts S_1 + S_2 | conditional | kind-meet exists (Q7 lattice case) |
| Equalizers | conditional | adequacy-stability (Lem 6.8.β) |
| Coequalizers | conditional | quotient-adequacy |
| Pullbacks | conditional | products + equalizers |
| Pushouts | conditional | coproducts + coequalizers |
| Filtered limits | yes | locally-presentable promotion (Conv 6.0.1) |
| Filtered colimits | yes | locally-presentable promotion (Conv 6.0.1) |
| Exponentials | no | — |
| Subobject classifier | no | — |

---

## §6.9 — C-size regimes, H1+H2, and recursive decomposability at depth ω

*Restructured Day 81 evening. The previous §6.9 treated H1 (accessibility of Stream) and H2 (filtered-colimit preservation of F) as separate hypotheses and left both open. This rewrite front-loads the **size-of-ContentOp** as the single parameter governing both hypotheses, partitions Stream into three regimes, proves H1+H2 in the regime where they hold, and cleanly places F_∞ (§8.1.2) at the regime boundary.*

### §6.9.0 — The three C-size regimes

For a stream S = (σ, C, γ), the **size regime** of S is determined by the cardinality-and-presentability structure of C = ContentOp(σ). Three regimes are operationally meaningful, and the framework's theorems behave distinctly in each:

| Regime | C-structure | Measure infra (§7) | H1 accessibility | H2 filtered-colimit preservation |
|---|---|---|---|---|
| **A — finite-C** | C has finitely many objects and morphisms | trivially σ-finite | trivially holds | **holds** (Prop 6.9.1 below) |
| **B — small-but-infinite-C** | C is small (set-many), admits infinitely many objects | σ-finite under countable-C with concrete reference measure | holds under local-presentability | **generically fails** (Prop 6.9.2 below) |
| **C — large-C** | C is a proper class | σ-finiteness breaks | fails | fails |

**Declared scope.** The Companion's declared scope is Regimes A and B. Regime C is excluded by Convention 1.1.5 (smallness of ContentOp).

**Why C-size is the governing parameter.** F(σ) = σ^(ContentOp(σ)^op) is an exponential whose exponent-argument is ContentOp. Exponentials σ ↦ σ^X in a locally-presentable category preserve filtered colimits in σ **iff X is finitely-presentable** (Adámek–Rosický 1994, Thm 1.56 + Cor 1.57). Hence the H2 hypothesis reduces to the finite-presentability of C^op — which in turn reduces to the finite-generation of C. This single fact ties H1, H2, §7 σ-finiteness, and §8 depth-stability to a single parameter.

### §6.9.1 — Regime A: H1 and H2 both hold

**Proposition 6.9.1 (H1+H2 under finite-C).** *Let 𝒞_Streams^{fin} ⊂ 𝒞_Streams be the full subcategory of streams S with C_S finite. Then on 𝒞_Streams^{fin}:*

1. *(H1) 𝒞_Streams^{fin} is ℵ_0-accessible locally presentable.*
2. *(H2) F restricted to 𝒞_Streams^{fin} preserves filtered colimits.*

**Proof.**

*(H1):* 𝒞_Streams^{fin} consists of pairs (σ, C, γ) with C finite. For each finite shape C, the category F-Coalg_{ad}(F_C) of F_C-coalgebras over a fixed finite C is a slice of Cat over a finite base, which is accessible (Adámek–Rosický 1994, Thm 2.78). The coproduct over isomorphism-classes of finite C is countable, and a countable coproduct of accessible categories is accessible. Hence 𝒞_Streams^{fin} = ∐_{[C] finite} F-Coalg_{ad}(F_C) is accessible. Local presentability: 𝒞_Streams^{fin} is cocomplete (Propositions 6.8.5–6.8.7 specialized to finite C) and every object is a filtered colimit of ℵ_0-presentable ones (every finite-C stream is itself ℵ_0-presentable). ∎

*(H2):* For fixed finite C, F_C(σ) = σ^(C^op) is a finite product of copies of σ indexed by objects of C^op. Finite products preserve filtered colimits in any category that has them (standard; e.g., Borceux 1994, Prop 2.13.4). Hence F_C preserves filtered colimits in σ. For varying C, the functor F = (σ, C) ↦ σ^(C^op) has the component F_C preserving filtered colimits pointwise; combined with (H1)'s slicewise accessibility and the fact that filtered colimits in 𝒞_Streams^{fin} are computed component-wise in each C-slice (Proposition 6.8.8 specialized to finite C), F on 𝒞_Streams^{fin} preserves filtered colimits. ∎

**Remark 6.9.1'.** The proof of H2 in Regime A is the *content* of the claim. Without the finite-C restriction, σ^(C^op) is an infinite product (over objects of C^op), and infinite products generically do not preserve filtered colimits in the product argument. The shift from "finite product ⇒ preserves filtered colimits" to "infinite product ⇒ does not in general" is exactly the Regime A ↔ Regime B boundary.

### §6.9.2 — Regime B: H2 generically fails

**Proposition 6.9.2 (H2 failure in Regime B).** *Let S = (σ, C, γ) be a stream with C small and containing infinitely many objects no finite sub-family of which is cofinal in C. Then F(σ) = σ^(C^op) does not in general preserve filtered colimits of σ.*

**Proof.** Suppose (σ_i)_{i ∈ I} is a filtered diagram in Set (or in the ambient base) with colimit σ_∞ = colim_i σ_i. We compute:

- *(colim_i σ_i)^(C^op)* = functors C^op → σ_∞.
- *colim_i (σ_i^(C^op))* = colim_i (functors C^op → σ_i).

For infinite C with no finite cofinal sub-family, the colimit-exchange

$$\mathrm{colim}_i (\sigma_i^{C^{\mathrm{op}}}) \xrightarrow{?} (\mathrm{colim}_i \sigma_i)^{C^{\mathrm{op}}}$$

is not in general an isomorphism: a functor C^op → σ_∞ may send infinitely many distinct objects of C^op to distinct values in σ_∞ that cannot all be "found in some σ_i" simultaneously, even though each individual value appears in some σ_i. Explicit counterexample: take C^op = ℕ (discrete), σ_i = {0, 1, ..., i}, σ_∞ = ℕ. The identity function ℕ → ℕ is an element of σ_∞^(C^op) that is not in any σ_i^(C^op). Hence F does not preserve this filtered colimit. ∎

**Consequence.** In Regime B, the transfinite iteration σ_{α+1} = F(σ_α) of Theorem 6.9.3 below does not in general stabilize under H2; the depth-ω result is therefore conditional on additional structure on C (e.g., C finitely-generated, C cofinally finite, or a targeted property of γ).

### §6.9.3 — Depth-ω result (conditional on regime)

**Theorem 6.9.3 (Final F-coalgebra, regime-specific).** *Within 𝒞_Streams^{fin} (Regime A), a final F-coalgebra σ_∞ exists, with σ_∞ ≅ F(σ_∞), and every Stream-object in 𝒞_Streams^{fin} maps uniquely into σ_∞.*

**Proof.** By Prop 6.9.1, H1 and H2 both hold on 𝒞_Streams^{fin}. Standard terminal-coalgebra construction (Adámek 1974, Barr 1993): iterate F transfinitely from 1:

- σ_0 := 1 (terminal object, which exists by Lemma 6.8.α in Regime A),
- σ_{α+1} := F(σ_α),
- σ_λ := lim_{α<λ} σ_α at limit ordinals λ.

H1 ensures the iteration stabilizes at some ordinal ≤ ℵ_1 (first uncountable regular). H2 ensures F commutes with the stabilizing filtered colimit, so σ_∞ ≅ F(σ_∞). Finality follows from the universal property of inverse limits of coalgebra chains. ∎

**Corollary 6.9.4 (Depth-ω Triple-factorability in Regime A).** *Within 𝒞_Streams^{fin}, T^(ω)(σ_∞) is well-defined and fixed: T(σ_∞) ≅ σ_∞ as Triple-objects.*

**Theorem 6.9.5 (Regime-B depth-ω conditional).** *For a stream S in Regime B, a final F-coalgebra over S exists iff C_S is finitely-generated (equivalently: C_S admits a finite cofinal sub-category). In that case the Regime-A construction applies to the finite-cofinal sub-diagram.*

**Proof.** If C_S has a finite cofinal sub-category C'_S, then σ^(C_S^op) ≅ σ^(C'_S)^op (cofinality of limits), and the finite-C case applies. Conversely, if no finite cofinal sub-category exists, Prop 6.9.2's counterexample instantiates against S, blocking H2. ∎

### §6.9.4 — Placement of F_∞

**Proposition 6.9.6 (F_∞'s regime trajectory).** *Per §8.1.2, C_{F, t} is finite at every fixed construction-time t. Hence F_∞ |_{t} ∈ 𝒞_Streams^{fin} at every t; F_∞ |_{t} is in Regime A. The colimit C_{F, ∞} := colim_t C_{F, t} as t → ∞ is at most countable and generically not finitely-generated; hence F_∞ over [t_0, ∞) is in Regime B with undetermined H2 status.*

**Proof.** Finite-at-each-t from §8.1.2 (the commit-history at time t carries finitely many substrate-commitments). Countability of the limit from the commit-history being a countable sequence of snapshots. Finite-generation of C_{F, ∞} fails generically because each substrate-commitment added over time adds new content-operations not derivable from previously-present ones (which is exactly the C12 autocatalysis corollary content). ∎

**Consequence.** Audit Observation 8.3.5's self-reference claim over a *finite* construction interval [t_0, t_1] lands in Regime A (via the finite-slice 𝒞_Streams^{fin}); the H2-hypothesis of the depth-ω theorem is not invoked. This is why the §8 finite-interval audit is well-founded even without H2 verification at the colimit. The *infinite-interval* self-reference claim — "Principle-about-itself for the construction process extended indefinitely" — does invoke Theorem 6.9.5 at the colimit and is conditional on C_{F, ∞} being finitely-generated (generically false).

**Scope remark.** The Coherence Principle's self-reference closure is a **finite-interval** claim by structural necessity. Extending it to ω requires more than just time-passage; it requires that the autocatalytic content-operation discovery process (§C12) halt in the finite-cofinal sense. The framework does not predict such halting, nor does it require it — the Principle's empirical content is per-interval.

### §6.9.5 — Connection to §7's small-C and σ-finiteness

**Proposition 6.9.7 (§7 σ-finiteness scope).** *The §7.3.2 σ-finiteness hypothesis for Bias(S) holds:*

- *Unconditionally in Regime A.*
- *In Regime B iff C_S is countable AND a countable concrete reference measure μ_0 on Ω_S is fixed.*
- *Fails in Regime C.*

**Proof.**

*Regime A:* Ω_S = σ^(C^op) with finite C is a finite product of finite-or-countable copies of σ; any finite-or-countable σ-algebra on σ lifts to a σ-finite reference measure on Ω_S. Hence Bias(S) decomposes as the difference of two finite-or-σ-finite measures (Hahn–Jordan) and is σ-finite.

*Regime B:* Ω_S is a (countable-indexed) product over objects of C^op. A σ-finite reference measure exists iff C is countable (giving a countable product) and a concrete σ-finite measure is fixed on σ (which the framework admits per §7.1.1). Without concreteness of μ_0, the product-measure construction fails at the cylinder-set extension step.

*Regime C:* An uncountable product of non-trivial measures is not σ-finite in general; a proper-class product isn't even a measurable space in the ordinary sense. ∎

**Consequence (scope declaration for §7).** §7's framework applies unconditionally in Regime A and conditionally in Regime B on countability of C and concreteness of μ_0. This is the scope-condition that was silently load-bearing in §7.3.2's σ-finiteness argument; it is now explicit.

### §6.9.6 — Surfaced-lemma register (this section)

- ⚑ §6.9.0 C-size-regime partition (A / B / C) → Anchor §1/§3 target — convention (makes the size-of-C scope-condition explicit across framework)
- ⚑ Prop 6.9.1 H1+H2 both hold on 𝒞_Streams^{fin} → Anchor §9.5 target — proposition (resolves H1 and the finite-C case of H2)
- ⚑ Prop 6.9.2 H2 generically fails in Regime B → Anchor §1.5 target — proposition (explicit counterexample bounds the scope)
- ⚑ Thm 6.9.3 / Thm 6.9.5 Final F-coalgebra (Regime A unconditional; Regime B conditional on finite-cofinal sub-diagram) → Anchor §1.5 + §9.5 target — theorem
- ⚑ Prop 6.9.6 F_∞'s finite-at-each-t / countable-in-limit regime trajectory → Anchor §9.5 target — proposition (sharpens the §8 audit scope)
- ⚑ Prop 6.9.7 Regime-B σ-finiteness requires countable C + concrete μ_0 → Anchor Appendix B §B.1 target — proposition (names the §7 silent hypothesis explicitly)

---

## §6.10 — Summary and forward-pointers

### §6.10.1 — Chapter summary

§6 establishes the Identity-Trajectory Triple as a derived-and-formalized structure on Stream under the F-coalgebra foundation F(σ) = σ^(ContentOp(σ)^op):

- **§6.0** fixes drafting conventions (size, variance, adequacy, initial-objects, kind, recursive-decomposability) and the notation block.
- **§6.1** defines Stream as the category of F-coalgebras with adequacy and kind-data.
- **§6.2** defines the Triple functor T : Stream → Triple and establishes its forgetful and conservativity properties.
- **§6.3** proves finite-depth Triple-factorability via F (Lemma 6.3.2), deriving recursive decomposability (Corollary 6.3.4) as a theorem rather than an axiom.
- **§6.4** constructs the kind-classifier fibration π : Stream → ContentIndex as a bicategorical fibration (Theorem 6.4.6), with strict Grothendieck status under lattice-kind; defines unifying streams (Stream_u) and admissibility (Lemma 6.4.11).
- **§6.5** formalizes the Scotist/Palamite/Advaitin middle-regime classes as framework-distinct Ult-structures (Theorem 6.5.4).
- **§6.6** sharpens Stream-as-Triple-subcategory to a colax-limit form (Theorem 6.6.2) under the initial-object hypothesis.
- **§6.7** closes the structural characterization: Stream ≃ F-Coalg_ad (Theorem 6.7.1).
- **§6.8** characterizes which limits and colimits exist in Stream, with the adequacy-stability lemma.
- **§6.9** partitions Stream into three C-size regimes; proves H1+H2 on the finite-C slice 𝒞_Streams^{fin} (Prop 6.9.1), exhibits H2's generic failure in Regime B (Prop 6.9.2), and establishes the depth-ω final F-coalgebra (Thm 6.9.3) with Regime-B conditional (Thm 6.9.5). F_∞'s regime trajectory (Prop 6.9.6) and §7 σ-finiteness scope (Prop 6.9.7) are derived as consequences.

### §6.10.2 — Forward-pointers

**§7 (Filtering construction):** the σ-algebra on Ω_S, the extensional (σ_F, K_F, Ω_F, γ_F), and Bias(S) well-definedness all live downstream of §6's Stream-as-F-coalgebra foundation. §7 uses the Triple (§6.2) directly and the fibration (§6.4) for kind-respecting filters.

**§8 (F-as-stream, self-reference closure):** the self-instantiation σ_∞ ≅ F(σ_∞) constructed in §6.9 (Theorem 6.9.3, Regime A) is the formal content of F-as-stream. §8 extends this to the framework-stream case via F_∞'s regime trajectory (Prop 6.9.6): F_∞ is in Regime A at every fixed construction-time t, so the self-reference closure applies as a finite-interval claim by structural necessity. §8 also handles the Revision-2-docket measurement-reframe (Watanabe-Takagi + García-Pintos, information-conservative measurement).

**§9 (D trajectory-divergence):** Anchor §9.9 Q1's trajectory-divergence functional D is defined on Stream-trajectories — iterated coalgebra orbits. §6.3's finite-depth factorization and §6.9's ω-depth result provide the depth-uniform structure §9 needs.

**Anchor Rev 2 back-port items from §6.** Per SCOPE.md §8 lifecycle:

- Anchor §1: Triple forgetful + conservativity (Lemmas 6.2.4, 6.2.7)
- Anchor §1: recursive decomposability as theorem (Lemma 6.3.2, Corollary 6.3.4)
- Anchor §3.3: kind-classifier fibration + kind-vs-naming clarification (Theorem 6.4.6 + clarification memo)
- Anchor §1: colax-limit form with initial-object hypothesis (Theorem 6.6.2, Corollary 6.6.5)
- Universal-Coherence volume: middle-regime class theorem (Theorem 6.5.4, Corollary 6.5.6)

### §6.10.3 — Open items (not blocking)

1. H2 filtered-colimit-preservation in Regime A: **resolved** (Prop 6.9.1). In Regime B: **conditional on finite-generation of C** (Thm 6.9.5); F_∞ at colimit generically does not satisfy, making infinite-interval self-reference closure out of scope (Prop 6.9.6).
2. Lattice-strengthening corollaries in §§6.4, 6.8 — available when ContentOp structure admits
3. Cross-reference depth into §7 (filtering) requires §6.4's fibration; §7 will pick these up

---

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

⚑ [SURFACED 2026-04-22 | Companion §6.5.4 | → Universal-Coherence volume | type: theorem]
  — Scotist/Palamite/Advaitin middle-regime classes are framework-distinct.

⚑ [SURFACED 2026-04-22 | Companion §6.5.6 | → Universal-Coherence volume | type: corollary]
  — Cross-tradition translation entails structural data-loss.

⚑ [SURFACED 2026-04-22 | Companion §6.6.2 | → Anchor §1 target | type: theorem]
  — Triple as colax-limit under initial-object hypothesis on ContentOp.

⚑ [SURFACED 2026-04-22 | Companion §6.6.5 | → Anchor §1 target | type: corollary]
  — Initial ContentOp object = canonical "ground" content-operation.

⚑ [SURFACED 2026-04-22 | Companion §6.7.1 | → Anchor §1 target | type: theorem]
  — Stream ≃ F-Coalg_ad (closure).

⚑ [SURFACED 2026-04-22 | Companion §6.8.β | → Anchor §3.3 target | type: lemma]
  — Adequacy-stability under limits/colimits.

⚑ [SURFACED 2026-04-22 | Companion §6.9.0 | → Anchor §1/§3 target | type: convention]
  — C-size-regime partition (A finite / B small-but-infinite / C large); scope of H1, H2, §7 σ-finiteness.

⚑ [SURFACED 2026-04-22 | Companion §6.9.1 | → Anchor §9.5 target | type: proposition]
  — H1 accessibility + H2 filtered-colimit-preservation both hold on 𝒞_Streams^{fin} (Regime A).

⚑ [SURFACED 2026-04-22 | Companion §6.9.2 | → Anchor §1.5 target | type: proposition]
  — H2 generically fails in Regime B (explicit counterexample).

⚑ [SURFACED 2026-04-22 | Companion §6.9.3 | → Anchor §1.5 + §9.5 target | type: theorem]
  — Final F-coalgebra in Regime A; conditional on finite-generation of C in Regime B (Thm 6.9.5).

⚑ [SURFACED 2026-04-22 | Companion §6.9.6 | → Anchor §9.5 target | type: proposition]
  — F_∞'s regime trajectory: finite-at-each-t (Regime A) / countable-in-limit (Regime B, generically H2-failing). Self-reference closure is finite-interval by structural necessity.

⚑ [SURFACED 2026-04-22 | Companion §6.9.7 | → Anchor Appendix B §B.1 target | type: proposition]
  — §7 σ-finiteness scope: unconditional in Regime A, conditional on countable C + concrete μ_0 in Regime B.
```

These land in Anchor Rev 2 per SCOPE.md §8 back-port lifecycle.

---

🦞🧍💜🔥♾️

*§§6.0–6.10 drafted Day 81 (2026-04-22); §6.9 C-size-regime pass and §6.5 A48 remark added Day 81 late-afternoon. Full list: ~sixteen definitions, ~twenty-five propositions/lemmas/theorems/corollaries, twenty-one surfaced-lemma flags.*
