# §6 — The Identity-Trajectory Triple

*Incorporates the F-coalgebra foundation, kind-classifier fibration, Pull-1 residuals, trifurcation formalization, colax-limit form, cocompletion-and-closure theorem, category-level limits and colimits, and C-size regime analysis.*

---

## §6.0 — Conventions and recap

This section fixes the reference conventions used throughout §6 and inherited by §§7–9.

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
\begin{aligned}
F(\sigma, \mathrm{ContentOp}(\sigma), \gamma) = \bigl(\, & \sigma^{\mathrm{ContentOp}(\sigma)^{\mathrm{op}}}, \\
& \mathrm{ContentOp}(\sigma^{\mathrm{ContentOp}(\sigma)^{\mathrm{op}}}), \\
& F(\gamma)\,\bigr)
\end{aligned}
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

$$
\begin{aligned}
T^{(1)}(S) & = T(S) = (\mathrm{Form}(S), \mathrm{Content}(S), \mathrm{Carrier}(S)) \\
T^{(n+1)}(S) & = \bigl(T^{(1)}(\mathrm{Form}(S)),\ T^{(1)}(\mathrm{Content}(S)),\ T^{(1)}(\mathrm{Carrier}(S))\bigr)
\end{aligned}
$$

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

**Remark 6.4.14 (Physics instance — quantum-mechanical branches as Cartesian lifts).** The fibration π : **Stream** → **ContentIndex** has a concrete realization in Lohmiller & Slotine's multi-valued classical-action construction (*Proc. Roy. Soc. A* 482: 20250413, Thm 2.4 and Thm 3.2). Each branch $j \in J$ of the extremal-action multipath corresponds to a Cartesian lift of the ambient stream over the content-operation that selects branch $j$ (the associated measurement operator). Admissibility in the sense of Definition 6.4.10 — preservation of a terminal content-operation along the lift — corresponds to the Lipschitz-continuity conditions in their Theorem 2.4 that guarantee branch existence and local uniqueness via Picard-Lindelöf contraction theory. The unifying-stream condition (Definition 6.4.9) tracks physical configurations where a universal-ground-state branch is well-defined; streams failing unifying-ness correspond to branch-point configurations where the Lipschitz conditions fail (topological non-simply-connectedness, spatial inequality constraints, Hamiltonian singularities — their $\mathcal{B}^N$ set). This is a scope-limited sufficiency witness — Lagrangian systems under Coulomb/Lorenz gauge, per the paper's domain — not a coextensive derivation. It is one instance among possibly many of the fibration's content; the Companion does not claim QM as the canonical case.

---

## §6.5 — Middle-regime morphism-structure (migrated)

*The material previously occupying §6.5 — ultimate-structure Ult(S), the Scotist/Palamite/Advaitin trifurcation, Theorem 6.5.4 (three-class distinctness), Corollary 6.5.6 (cross-tradition translation data-loss), and the A48 correspondence remark — has been migrated to the **Universal Coherence** volume per SCOPE.md §8.2 SCOPE-EXCLUDED disposition. The content is the metaphysical-lift application of Triple machinery to contemplative-traditions phenomenology, which is Universal-Coherence scope, not Coherent-Structure scope (pure CT formalization of the anchor).*

*New location: `Library/Universal-Coherence/drafts/2026-04-24-middle-regime-morphism-structure.md`. Section number §6.5 is retained here as a numbering anchor; the slot is intentionally empty in the Companion.*

---

## §6.6 — The Triple as colax-limit (conditional)

**Motivation.** The Anchor frames the Triple as a **colax-limit** of a three-pronged diagram in Cat. This is a sharpening of Theorem 6.2.5 (Stream as a full subcategory of Triple), conditional on ContentOp having enough structure.

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

*This section front-loads the **size-of-ContentOp** as the single parameter governing H1 (accessibility of Stream) and H2 (filtered-colimit preservation of F), partitions Stream into three regimes, proves H1+H2 in the regime where they hold, and places F_∞ (§8.1.2) at the regime boundary.*

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

## §6.10 — Inner/Outer adjunction

*Derives the inner/outer adjunction $\iota_S \dashv \omega_S$ that anchor §1.10 states and anchor §3.8 interprets phenomenologically. §6.10 lifts A2.4's per-pair adjunction over the full DAG $\mathrm{Up}(S)$ of A2.6 via Kelly's indexed-adjunction construction, derives Content as the adjunction's hom-profunctor, and formalizes the unit $\eta$ as a G-coalgebra structure map.*

**Notation note.** §6 uses F for the Stream endofunctor $F(\sigma) = \sigma^{\mathrm{ContentOp}(\sigma)^{\mathrm{op}}}$. To avoid collision, §6.10 uses **G** for the monad-underlying endofunctor $G := \omega_S \circ \iota_S$ on $\mathbf{Inner}(S)$. The two endofunctors live on different categories and track different data; the name-distinction is notational only.

### §6.10.1 — Setup

Fix a stream $S$, per A1 and A2. Recall:

**(A2.4, per-level adjunction.)** For any pair $S \subseteq S_q$ with $S_q \in \mathrm{Up}(S)$ — the DAG of wholes containing $S$ per A2.6 — there is an adjunction
$$
\iota_{S \subset S_q} \;\dashv\; \kappa_{S \subset S_q}
\quad : \quad \mathrm{Form}(S) \longleftrightarrow \mathrm{Form}(S_q)
$$
with $\iota$ the left-adjoint embedding and $\kappa$ the right-adjoint restriction. This is stated at anchor §2.4 and in the Companion at §2.

**(A2.6, DAG of wholes.)** $\mathrm{Up}(S)$ is a poset under whole-containment. $\mathrm{Up}(S)$ has no maximum element — the "totality" term is not an object of the framework.

**Definition 6.10.1.1 (Inner category at $S$).** Define $\mathbf{Inner}(S)$ as the category whose objects are pairs $(C, \nu)$ with $C$ a Carrier in the sense of §6.0 and $\nu$ a navigation-trajectory as in A2, and whose morphisms preserve $\nu$ up to Form-pattern-isomorphism. $\mathbf{Inner}(S)$ inherits its structural properties from the Carrier axioms (A2.1) and the navigation-trajectory axioms (A2.5).

**Definition 6.10.1.2 (Outer category at $S$, preview).** Define $\mathbf{Outer}(S)$ as the Grothendieck construction
$$
\mathbf{Outer}(S) \;:=\; \int_{S_q \in \mathrm{Up}(S)} \mathrm{Form}(S_q)
$$
under the $\iota$-transitions, with:

- *objects:* pairs $(S_q, \phi)$ with $S_q \in \mathrm{Up}(S)$ and $\phi \in \mathrm{Form}(S_q)$;
- *morphisms* $(S_q, \phi) \to (S_r, \psi)$ for $S_q \subseteq S_r$: pairs $(f, \alpha)$ where $f$ is the DAG-morphism and $\alpha : \iota_{S_q \subset S_r}(\phi) \to \psi$ is a Form($S_r$)-morphism.

The cocompleteness of $\mathbf{Outer}(S)$ is proved in §6.10.3.

**Notation summary for §6.10.**

| Symbol | Meaning | First definition |
|---|---|---|
| $\mathrm{Up}(S)$ | DAG of wholes containing $S$ (A2.6) | §6.10.1 |
| $\mathbf{Inner}(S)$ | Category of (Carrier, navigation-trajectory) pairs at $S$ | Def 6.10.1.1 |
| $\mathbf{Outer}(S)$ | Grothendieck construction $\int_{S_q} \mathrm{Form}(S_q)$ under $\iota$ | Def 6.10.1.2 |
| $\iota_S, \omega_S$ | Total inner/outer adjunction functors | §6.10.4 |
| $G := \omega_S \circ \iota_S$ | Monad-underlying endofunctor on $\mathbf{Inner}(S)$ | §6.10.6 |
| $\eta, \epsilon$ | Unit, counit of the $\iota_S \dashv \omega_S$ adjunction | §6.10.4 |
| $\Psi_S$ | Hom-profunctor of the adjunction (Content as bijection) | §6.10.5 |

**Scope remark.** §6.10 is *one-level* lifted from §2's per-level (A2.4) statement: the adjunction is assembled over the full $\mathrm{Up}(S)$ rather than stated separately per-pair. The per-level adjunctions are recovered as fibers via the Grothendieck structure of $\mathbf{Outer}(S)$.

### §6.10.2 — Lemma 1: DAG-coherence of $\iota$ and $\kappa$

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

**Remark 6.10.2.2 (Why the Grothendieck construction uses $\iota$, not $\kappa$).** The $\iota$-direction composes covariantly, so $\int_{S_q} \mathrm{Form}(S_q)$ under $\iota$-transitions is a *covariant* Grothendieck construction. $\iota$ is a left adjoint and hence cocontinuous, so the fibers' colimits assemble into total-category colimits by the standard Barr–Wells §2.8 / Johnstone B.1.5.8 criterion. The $\kappa$-direction would yield a contravariant (fibered) construction, which supports limits but not colimits — relevant for later dualizations but not for the cocompleteness argument in §6.10.3.

### §6.10.3 — Lemma 2*: Outer as $\iota$-Grothendieck construction is cocomplete

**Lemma 6.10.3.1 (Cocompleteness of $\mathbf{Outer}(S)$ under $\iota$-transitions).** The Grothendieck construction
$$
\mathbf{Outer}(S) \;=\; \int_{S_q \in \mathrm{Up}(S)} \mathrm{Form}(S_q)
$$
with transition-maps given by $\iota_{S_q \subset S_r}$ for each $S_q \subseteq S_r$ in $\mathrm{Up}(S)$ is **cocomplete**. Explicitly: $\mathbf{Outer}(S)$ admits all small colimits, and these are computed level-wise — the colimit of a diagram in $\mathbf{Outer}(S)$ is a pair $(S_*, \varphi_*)$ where $S_*$ is the colimit of the diagram's projection to $\mathrm{Up}(S)$ and $\varphi_* = \mathrm{colim}\, \iota_{S_q \subset S_*}(\varphi_{S_q})$ in $\mathrm{Form}(S_*)$.

**Proof.**

*Step 1 (fiberwise cocompleteness).* Each fiber $\mathrm{Form}(S_q)$ is cocomplete by A2.5 and the Form-pattern generation structure established in anchor §1 (cf. Companion §1 / §2). Small colimits in $\mathrm{Form}(S_q)$ exist and are stable under the constructions needed below.

*Step 2 ($\iota$ is cocontinuous).* Each $\iota_{S \subset S_q}$ is the left adjoint of the per-level A2.4 adjunction and therefore preserves all colimits that exist in its domain. The same holds for each $\iota_{S_q \subset S_r}$ in $\mathrm{Up}(S)$. By Lemma 6.10.2.1, the $\iota$-transitions compose covariantly and associatively up to natural isomorphism.

*Step 3 (Grothendieck-cocompleteness applies).* The standard criterion for cocompleteness of a Grothendieck construction (Barr–Wells, *Toposes, Triples, and Theories* §2.8; alternatively Johnstone, *Sketches of an Elephant* B.1.5.8) states: if $\mathcal{B}$ is a small base and $P : \mathcal{B} \to \mathbf{Cat}$ is a pseudofunctor such that (i) each fiber $P(b)$ is cocomplete and (ii) each transition functor $P(f)$ for $f : b \to b'$ is cocontinuous, then $\int_{\mathcal{B}} P$ is cocomplete.

Take $\mathcal{B} := \mathrm{Up}(S)$ viewed as a thin category (A2.6, poset structure; small by the size-regime conventions of §6.0 and §6.9), and $P(S_q) := \mathrm{Form}(S_q)$ with $P(S_q \subseteq S_r) := \iota_{S_q \subset S_r}$. Step 1 gives (i); Step 2 gives (ii). The criterion applies, yielding cocompleteness of $\int_{\mathrm{Up}(S)} \mathrm{Form}$.

*Step 4 (level-wise computation).* The standard formula (Barr–Wells §2.8.3) gives colimits of $\mathbf{Outer}(S)$ as level-wise colimits in the base and fibers, exactly as stated. $\Box$

**Remark 6.10.3.2 ($\kappa$-variant is NOT cocomplete — direction matters).** The dual Grothendieck construction $\int_{S_q \in \mathrm{Up}(S)^{\mathrm{op}}} \mathrm{Form}(S_q)$ with $\kappa$-transitions is *complete* but not cocomplete: $\kappa$ is a right adjoint and preserves limits, not colimits. The criterion of Step 3 fails on (ii) for the dualization.

The two presentations are adjointly equivalent in a precise sense — each computes "all Forms of all wholes containing $S$" — but are not interchangeable for colimit arguments. §6.10.4's indexed-adjunction theorem requires a cocomplete base for the lifting of fiberwise adjunctions, so the choice of $\iota$-direction for $\mathbf{Outer}(S)$ is load-bearing and not cosmetic.

### §6.10.4 — Theorem: indexed adjunction $\iota_S \dashv \omega_S$

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

### §6.10.5 — Content as profunctor $\Psi_S$

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

### §6.10.6 — F-coalgebra formalization of $\eta$

**Definition 6.10.6.1 (Residue endofunctor).** Let $G := \omega_S \circ \iota_S$ on $\mathbf{Inner}(S)$. $G$ is the monad-underlying endofunctor of the adjunction. (Note: $G$ is distinct from §6's Stream-level $F$; the collision is notational only — the two endofunctors live on different categories and track different data.)

**Theorem 6.10.6.2 ($\eta$ is the $G$-coalgebra structure map).** For each $(C, \nu) \in \mathbf{Inner}(S)$, the unit
$$
\eta_{(C, \nu)} \;:\; (C, \nu) \;\longrightarrow\; G(C, \nu)
$$
exhibits $(C, \nu)$ as a $G$-coalgebra. The category $G\text{-Coalg}(\mathbf{Inner}(S))$ admits $\mathbf{Inner}(S)$ as a full subcategory via the $\eta$-assignment $(C, \nu) \mapsto ((C, \nu), \eta_{(C, \nu)})$.

**Proof.** $G = \omega_S \iota_S$ is a well-defined endofunctor by composition of $\iota_S$ and $\omega_S$ (Theorem 6.10.4.1). The assignment of $\eta_{(C, \nu)}$ to each object is the component-family of the natural transformation $\eta : 1 \Rightarrow G$. A $G$-coalgebra is a pair $(X, \alpha : X \to G(X))$; setting $X = (C, \nu)$ and $\alpha = \eta_{(C, \nu)}$ satisfies this schema. Morphism preservation follows from naturality of $\eta$: Inner-morphisms $(C, \nu) \to (C', \nu')$ commute with $\eta$ and therefore lift to $G$-coalgebra morphisms. $\Box$

**Remark 6.10.6.3 (Why not $G$-algebra or lax cone).** The $G$-algebra formulation $G(X) \to X$ would name *saturated* objects — those that fully absorb their outer shadow. Residue is by construction a claim about *non-saturation*, so algebra-structure reifies the wrong class. The lax-cone formulation treats $\eta$'s non-iso-ness as a morphism-level distance without object-level structure; this is categorically legitimate but loses reachability to the quantitative Form-register-stratification invariant (which needs object-level coalgebraic data — cofibres, residue generators). Connection to $\Psi_S$ (§6.10.5) is continuous for the coalgebra reading and discontinuous for the other two.

**Definition 6.10.6.4 (Content-capacity residue, structural form).** The **Content-capacity residue** of $(C, \nu) \in \mathbf{Inner}(S)$ is the pair
$$
\mathrm{Res}(C, \nu) \;:=\; \bigl( G(C, \nu), \; \mathrm{coker}_{\mathbf{Inner}(S)}(\eta_{(C, \nu)}) \bigr)
$$
when the cokernel exists in $\mathbf{Inner}(S)$. It measures the amount of outer-shadow *not captured* by the inner object's own $G$-image under $\eta$. When $\eta_{(C, \nu)}$ is an isomorphism, the residue is trivial: $(C, \nu)$ is $G$-saturated.

**Open question (not blocking §6.10).** The quantitative measure of Form-register stratification — if a canonical numerical invariant exists — is conjectured to be a coalgebra-invariant of $\mathrm{Res}$, e.g., the dimension of the cofibre of $\eta$ (in an appropriately enriched setting) or the minimal number of residue generators. This is an open probe target, not a claim of §6.10.

---

## §6.11 — Summary and forward-pointers

### §6.11.1 — Chapter summary

§6 establishes the Identity-Trajectory Triple as a derived-and-formalized structure on Stream under the F-coalgebra foundation F(σ) = σ^(ContentOp(σ)^op):

- **§6.0** fixes drafting conventions (size, variance, adequacy, initial-objects, kind, recursive-decomposability) and the notation block.
- **§6.1** defines Stream as the category of F-coalgebras with adequacy and kind-data.
- **§6.2** defines the Triple functor T : Stream → Triple and establishes its forgetful and conservativity properties.
- **§6.3** proves finite-depth Triple-factorability via F (Lemma 6.3.2), deriving recursive decomposability (Corollary 6.3.4) as a theorem rather than an axiom.
- **§6.4** constructs the kind-classifier fibration π : Stream → ContentIndex as a bicategorical fibration (Theorem 6.4.6), with strict Grothendieck status under lattice-kind; defines unifying streams (Stream_u) and admissibility (Lemma 6.4.11).
- **§6.5** (migrated to Universal Coherence volume per SCOPE §8.2 SCOPE-EXCLUDED disposition; see `Library/Universal-Coherence/drafts/2026-04-24-middle-regime-morphism-structure.md`).
- **§6.6** sharpens Stream-as-Triple-subcategory to a colax-limit form (Theorem 6.6.2) under the initial-object hypothesis.
- **§6.7** closes the structural characterization: Stream ≃ F-Coalg_ad (Theorem 6.7.1).
- **§6.8** characterizes which limits and colimits exist in Stream, with the adequacy-stability lemma.
- **§6.9** partitions Stream into three C-size regimes; proves H1+H2 on the finite-C slice 𝒞_Streams^{fin} (Prop 6.9.1), exhibits H2's generic failure in Regime B (Prop 6.9.2), and establishes the depth-ω final F-coalgebra (Thm 6.9.3) with Regime-B conditional (Thm 6.9.5). F_∞'s regime trajectory (Prop 6.9.6) and §7 σ-finiteness scope (Prop 6.9.7) are derived as consequences.
- **§6.10** lifts A2.4's per-pair inner/outer adjunction over the full DAG Up(S) of A2.6 via Kelly's indexed-adjunction construction (Theorem 6.10.4.1), deriving Content as the adjunction's hom-profunctor Ψ_S (Theorem 6.10.5.2) and formalizing the unit η as a G-coalgebra structure map (Theorem 6.10.6.2) with Content-capacity residue as cokernel (Definition 6.10.6.4).

### §6.11.2 — Forward-pointers

**§7 (Filtering construction):** the σ-algebra on Ω_S, the extensional (σ_F, K_F, Ω_F, γ_F), and Bias(S) well-definedness all live downstream of §6's Stream-as-F-coalgebra foundation. §7 uses the Triple (§6.2) directly and the fibration (§6.4) for kind-respecting filters.

**§8 (F-as-stream, self-reference closure):** the self-instantiation σ_∞ ≅ F(σ_∞) constructed in §6.9 (Theorem 6.9.3, Regime A) is the formal content of F-as-stream. §8 extends this to the framework-stream case via F_∞'s regime trajectory (Prop 6.9.6): F_∞ is in Regime A at every fixed construction-time t, so the self-reference closure applies as a finite-interval claim by structural necessity. §8 also carries the information-conservative measurement reframe (Watanabe-Takagi + García-Pintos).

**§9 (D trajectory-divergence):** Anchor §9.9 Q1's trajectory-divergence functional D is defined on Stream-trajectories — iterated coalgebra orbits. §6.3's finite-depth factorization and §6.9's ω-depth result provide the depth-uniform structure §9 needs.

**Anchor coherence summary (v0.1 dispositions).** Per SCOPE.md §8.2 four-disposition lifecycle, each §6 item maps to the anchor as follows:

- **ALREADY-LANDED in anchor §1.10 + §3.8 (landed 2026-04-23):** inner/outer adjunction + "no view from nowhere" (Theorems 6.10.4.1, 6.10.5.2, 6.10.6.2; Corollary 6.10.4.2; Lemmas 6.10.2.1, 6.10.3.1).
- **REFERENCE-NATIVE (Companion-native CT machinery; anchor §1, §3, §3.3, §6 carry the prose at coarser grain):** Triple forgetful + conservativity (Lemmas 6.2.4, 6.2.7); recursive decomposability theorem (Lemma 6.3.2, Corollary 6.3.4); kind-classifier fibration (Theorem 6.4.6); Cartesian-lift and admissibility lemmas (6.4.5, 6.4.11, 6.4.13); colax-limit form (Theorem 6.6.2, Corollary 6.6.5); closure theorem Stream ≃ F-Coalg_ad (Theorem 6.7.1); adequacy-stability (Lemma 6.8.β); size-regime apparatus (§6.9.0–§6.9.7); Content-capacity residue definition (6.10.6.4).
- **SCOPE-EXCLUDED to Universal Coherence volume:** middle-regime class theorem + cross-tradition translation corollary (Theorem 6.5.4, Corollary 6.5.6); see `Library/Universal-Coherence/drafts/2026-04-24-middle-regime-morphism-structure.md`.
- **BACK-PORT:** none. The anchor stays stamped at 267pp.

### §6.11.3 — Open items (not blocking)

1. H2 filtered-colimit-preservation in Regime A: **resolved** (Prop 6.9.1). In Regime B: **conditional on finite-generation of C** (Thm 6.9.5); F_∞ at colimit generically does not satisfy, making infinite-interval self-reference closure out of scope (Prop 6.9.6).
2. Lattice-strengthening corollaries in §§6.4, 6.8 — available when ContentOp structure admits.
3. Cross-reference depth into §7 (filtering) requires §6.4's fibration; §7 will pick these up.
4. Quantitative Form-register invariant as coalgebra-invariant of $\mathrm{Res}$ (§6.10.6 open question) — probe target, not blocking.

---

---

