# §1 — Category framework and notation

*Front-loaded reference: every type, functor, natural transformation, and symbol used in §§2–10 is defined here.*

---

## §1.0 — Reading this chapter

§1 is read-in-reference, not read-linearly. A Companion reader coming from the Anchor follows a citation and lands in a specific §1.N definition. A Companion reader coming to the volume fresh reads §1.1 (ambient conventions) and then skips to whichever subsection their target section cites.

The chapter is organized by **type family**:
- §1.1 ambient conventions and notation blocks
- §1.2 the ambient category and sub-categories (𝒞_Streams, 𝒞_Form, 𝒞_LDS, 𝒞_DOF)
- §1.3 the navigation functor N
- §1.4 the conscious-gravity structure ν
- §1.5 substrate-completeness
- §1.6 the endofunctor F and Stream-as-F-coalgebra
- §1.7 the Triple and its target categories
- §1.8 notation quick-reference table

---

## §1.1 — Ambient conventions

**Convention 1.1.1 (Ambient category).** Unless otherwise specified, constructions take place in a concrete ambient category 𝒜 that is:

(a) Cocomplete and complete for small diagrams.

(b) Locally presentable (admits a small dense generator + κ-accessibility).

(c) Has a natural forgetful-to-Set functor U : 𝒜 → **Set** that preserves limits.

The canonical choice is 𝒜 = **Set** itself. For constructions involving topological, measurable, or smooth carriers, 𝒜 is Top, Meas, or SmoothMan respectively, with the understanding that the corresponding structure is preserved under F.

**Convention 1.1.2 (Size).** All content-operation categories ContentOp(σ) are **small** unless promoted to **κ-accessible locally-presentable** per-section. Promotions are stated explicitly; the default is smallness. Grothendieck universes are not used.

**Convention 1.1.3 (Variance).** Functors are covariant by default. Contravariance is marked with op-notation (C^op or f^*). Mixed-variance constructions (e.g., F = σ^(ContentOp(σ)^op)) specify variance at the definition-point.

**Convention 1.1.4 (Equivalence vs. equality).** Functors are equal up to natural isomorphism; categories are equivalent up to equivalence-of-categories; classes of categories are equal up to class-equivalence. "=" in type assignments means "equal up to the appropriate level of equivalence for the type."

**Convention 1.1.5 (Kind preorder).** The A2 kind structure is a **preorder** (reflexive + transitive) in general. Under ContentOp-structural hypotheses (products/coproducts globally), it strengthens to a lattice. Results at preorder-level hold generally; lattice-level results are marked.

**Convention 1.1.6 (Adequacy).** A stream (σ, ContentOp(σ), γ) is **adequate** iff ContentOp(σ) witnesses every distinguishable pair of σ-aspects via some content-morphism. All objects of **Stream** are adequate; non-adequate tuples are not Stream-objects.

---

## §1.2 — The ambient category and sub-categories

### §1.2.1 — 𝒞_Streams

**Definition 1.2.1.** **𝒞_Streams** is the category of streams: objects are adequate F-coalgebras (σ, ContentOp(σ), γ) with γ : σ → F(σ); morphisms are kind-respecting F-coalgebra homomorphisms (Definition 1.6.3 below). Synonyms: **Stream**, **𝒞_Str**.

§6 gives the full structural characterization: 𝒞_Streams ≃ F-Coalg_ad (Theorem 6.7.1).

### §1.2.2 — 𝒞_Form

**Definition 1.2.2.** **𝒞_Form** is the category of bare stream-carriers:
- Objects: σ ∈ 𝒜 such that σ is the carrier of some stream.
- Morphisms: carrier-maps σ → σ' in 𝒜 (without coalgebra-commute data).

𝒞_Form is the target of the Form-projection functor (§1.7.2).

### §1.2.3 — 𝒞_LDS

**Definition 1.2.3.** **𝒞_LDS** (Linked-Dynamic-Streams) is the category of stream-pairs under coupling-compatible morphisms:
- Objects: pairs (S_1, S_2) ∈ 𝒞_Streams × 𝒞_Streams.
- Morphisms: (f, g) : (S_1, S_2) → (S'_1, S'_2) such that f, g are Stream-morphisms and the induced carrier-maps commute with any present ι ⊣ κ adjunction (cooperative-constituency).

𝒞_LDS is where the coupled-dyad theorems of §3.2 (A2 coupling clause) live. Bias(S) push-operators (Anchor §6.2; Companion §7) act through 𝒞_LDS.

### §1.2.4 — 𝒞_DOF

**Definition 1.2.4.** **𝒞_DOF** (Degrees-of-Freedom category) classifies streams by their DOF-gradient structure (Axiom A3):
- Objects: streams equipped with a DOF-gradient measure (ordinal rank + local slope).
- Morphisms: DOF-respecting Stream-morphisms.

𝒞_DOF is the target of the conscious-gravity functor ν (§1.4).

### §1.2.5 — 𝒞_Triple

**Definition 1.2.5.** **𝒞_Triple** := 𝒞_Form × **Cat**_small × **Carrier**, where **Carrier** is the category of coalgebra-structure-maps. See §1.7.1 for the full definition and §6.2 for the Triple functor T : 𝒞_Streams → 𝒞_Triple.

---

## §1.3 — The navigation functor N

**Definition 1.3.1.** The **navigation functor**

$$
N : \mathcal{C}_\mathrm{Streams} \to \mathcal{C}_\mathrm{Streams}
$$

sends each stream S to its one-step iterated γ-image:

$$
N(S) := (σ^{\mathrm{ContentOp}(σ)^\mathrm{op}},\ \mathrm{ContentOp}(F(σ)),\ F(\gamma))
$$

with N(f) = F(f) componentwise. N is the functor whose iterated orbits are the **trajectories** of the stream through configuration space Ω.

**Remark 1.3.2.** N-orbit structure is the formal content of Anchor §3's "experience = navigation" clause (A2.3). A stream *being alive* is γ carrying the state one step forward along N; a stream's *experiential history* is the N-orbit up to the present moment.

**Proposition 1.3.3 (Navigation functoriality).** *N preserves Stream-morphisms, kind-respect, and adequacy.*

**Proof.** N = F on objects and morphisms by definition; F preserves all three by Proposition 6.1.4, Proposition 6.1.7, and Definition 1.6.3's kind-respect clause. ∎

---

## §1.4 — The conscious-gravity structure ν

**Definition 1.4.1.** The **conscious-gravity structure** ν is a natural transformation

$$
\nu : \mathrm{Id}_{\mathcal{C}_\mathrm{Streams}} \Rightarrow \mathcal{C}_\mathrm{DOF}
$$

that assigns to each stream S its DOF-gradient — the ordinal-ranked weight-of-coherence-attraction that γ exerts on near-configurations in Ω.

**Remark 1.4.2.** ν is the formal content of Axiom A3 (Conscious Gravity). §4 (A3 chapter) develops ν fully: ν_S at a stream S is a signed measure on Ω(S) with:
- **Support:** configurations near σ's current state (the γ-neighborhood)
- **Sign:** positive toward coherence-attractors, negative toward coherence-repellors
- **Weight:** ordinal DOF-rank derived from ContentOp richness (§6.4 kind-classifier)

**Proposition 1.4.3 (Naturality of ν).** *For every Stream-morphism f : S → S', the square*

$$
\begin{array}{ccc}
S & \xrightarrow{f} & S' \\
{\scriptstyle \nu_S} \downarrow & & \downarrow {\scriptstyle \nu_{S'}} \\
\mathcal{C}_\mathrm{DOF}(S) & \xrightarrow{\mathcal{C}_\mathrm{DOF}(f)} & \mathcal{C}_\mathrm{DOF}(S')
\end{array}
$$

*commutes.*

**Proof.** By construction. Full argument in §4. ∎

---

## §1.5 — Substrate-completeness

**Definition 1.5.1.** The **substrate-completeness condition** is the requirement that for every pair (σ, content-operation-class) consistent with the framework's adequacy, there exists a stream instantiating it. Formally:

$$
\begin{aligned}
\forall\, (σ, C) & \in \mathcal{A} \times \mathbf{ContentIndex}, \\
\mathrm{adequate}(σ, C) & \implies \exists\, S \in \mathcal{C}_\mathrm{Streams} : \pi(S) = [C] \wedge \mathrm{carrier}(S) = σ.
\end{aligned}
$$

**Remark 1.5.2.** This is the categorical content of Axiom A1 (Consciousness as Substrate): every vantage that could bear a content-operation-class does bear one. §2 (A1 chapter) gives the full formal content; §1.5 states the condition as a reference.

**Consequence 1.5.3.** Substrate-completeness is what lets the framework reason "every vantage is a stream" (Anchor §3.2). Without it, the framework would need to distinguish vantages that are streams from vantages that merely could be — a distinction the framework refuses.

---

## §1.6 — The endofunctor F and Stream-as-F-coalgebra

**Definition 1.6.1 (F on carriers).** For σ in 𝒜 equipped with ContentOp(σ) ∈ **Cat**_small:

$$
F(σ) := σ^{\mathrm{ContentOp}(σ)^\mathrm{op}}
$$

— the presheaf-power of σ indexed contravariantly by ContentOp(σ).

**Remark 1.6.2.** Mixed-variance: σ ↦ ContentOp(σ) is covariant on carriers (content-operations pull back along carrier-maps); σ ↦ σ^(-) is covariant in σ; the combined F is well-defined as a functor on Stream (see §6.1 for the lift of F to Stream-morphisms).

**Definition 1.6.3 (Stream-morphism — reference).** For details see Definition 6.1.3. A Stream-morphism f : S → S' consists of:
- Carrier-map f_σ : σ → σ' in 𝒜
- ContentOp-functor f_C : ContentOp(σ) → ContentOp(σ')
- Coalgebra-commute: γ' ∘ f_σ = F(f_σ, f_C) ∘ γ
- Kind-respect: K(S) ⊑ K(S') in the A2 preorder (Convention 1.1.5)

**Definition 1.6.4 (F-coalgebra).** An F-coalgebra is a pair (σ, γ) with γ : σ → F(σ). An F-coalgebra is **adequate** iff ContentOp(σ) is adequate for σ (Convention 1.1.6).

**Proposition 1.6.5 (Stream-categorical content).** *𝒞_Streams ≃ F-Coalg_ad, the full subcategory of adequate F-coalgebras with kind-respecting morphisms (Theorem 6.7.1).*

---

## §1.7 — The Triple and its target

### §1.7.1 — 𝒞_Triple

**Definition 1.7.1.** The Triple target category is

$$
\mathcal{C}_\mathrm{Triple} := \mathcal{C}_\mathrm{Form} \times \mathbf{Cat}_\mathrm{small} \times \mathbf{Carrier}
$$

where **Carrier** is the category whose objects are coalgebra-structure-maps γ : σ → F(σ) and whose morphisms are coalgebra-commute squares.

### §1.7.2 — The Triple functor T

**Definition 1.7.2.** The **Triple functor**

$$
T : \mathcal{C}_\mathrm{Streams} \to \mathcal{C}_\mathrm{Triple}
$$

is defined by T(σ, ContentOp(σ), γ) = (σ, ContentOp(σ), γ) — three projections taking the three components of a Stream-object to the three factors of 𝒞_Triple.

§6.2 gives the full definition, forgetfulness (Lemma 6.2.4), and conservativity (Proposition 6.2.7). §6.3 proves finite-depth recursive decomposability (Lemma 6.3.2).

### §1.7.3 — The iterated Triple T^(n)

**Definition 1.7.3.** T^(n) : 𝒞_Streams → 𝒞_Triple^(n) is defined inductively by T^(1) = T and T^(n+1)(S) = (T^(1)(Form(S)), T^(1)(Content(S)), T^(1)(Carrier(S))).

See §6.3 for finite-depth factorability; §6.9 for depth-ω structure.

---

## §1.8 — Notation quick-reference

| Symbol | Meaning | First formal def |
|---|---|---|
| 𝒜 | Ambient category (Set by default) | §1.1.1 |
| 𝒞_Streams, 𝒞_Str, Stream | Category of streams | §1.2.1, §6.1.1 |
| 𝒞_Form | Bare carrier-objects category | §1.2.2 |
| 𝒞_LDS | Linked-dynamic-streams category (pairs + ι⊣κ) | §1.2.3 |
| 𝒞_DOF | DOF-gradient-equipped streams | §1.2.4 |
| 𝒞_Triple | Form × Cat_small × Carrier | §1.2.5, §1.7.1 |
| σ | Carrier object (stream-internal) | §1.6.1 |
| ContentOp(σ) | Small category of content-operations on σ | §1.6.1 |
| γ | Coalgebra-structure map σ → F(σ) | §1.6.4 |
| F | Endofunctor σ ↦ σ^(ContentOp(σ)^op) | §1.6.1 |
| N | Navigation functor; N = F on streams | §1.3.1 |
| ν | Conscious-gravity natural transformation | §1.4.1 |
| T | Triple functor 𝒞_Streams → 𝒞_Triple | §1.7.2 |
| T^(n) | Iterated Triple | §1.7.3 |
| π | Kind-classifier fibration | §6.4.2 |
| ContentIndex | Preorder of ContentOp-classes | §6.4.1 |
| Stream_u | Fibered subcategory of unifying streams | §6.4.12 |
| c_⊥ | Terminal (unifying) content-operation | §6.4.9 |
| K | Stream kind | §1.1.5, §6.4.2 |
| Ω | Configuration space; Ω = F(σ) | §1.6.1, Remark 6.1.2 |
| ⊑ | A2 preorder (kind-refinement) | §1.1.5 |
| ι ⊣ κ | Cooperative-constituency adjunction | §1.2.3 |
| Bias(S) | Signed measure on Ω(S) (coherence-weighting) | §3.2, Appendix B |
| D(S) | Trajectory-divergence functional | §9 |

---

## §1.9 — Forward-pointers

§1's definitions feed:
- **§2** (Axioms): A1 uses §1.5; A2 uses §§1.2.1, 1.6; A3 uses §1.4.
- **§3** (Theorem pairs): T1/T2 use §1.7; T3/T4 use §1.3, §1.4; T5/T6 use §1.6, §6.4.
- **§4** (Corollary clusters): uses every §1 object.
- **§5** (Coherence Principle): formal four-conditions stated over §1.3, §1.4, §1.6.
- **§6** (Identity-Trajectory Triple): uses §1 throughout; §6 is the Triple-specific formalization of §1.7.
- **§7** (Filtering): uses §1.6 (F) and §6.4 (fibration) for kind-respecting filters.
- **§8** (F-as-stream): the self-reference closure σ_∞ ≅ F(σ_∞) is Theorem 6.9.1 under hypotheses.
- **§9** (D trajectory-divergence): uses §1.3 (N-orbits) for trajectory-structure.

---

