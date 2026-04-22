# §4 — Corollary clusters

*Thirteen corollaries in three clusters (substrate/generativity, stream-structure/navigation, coherence-consequences). This chapter completes the CT proofs; Anchor §8 carries the prose translations and applied exposition. References are to §1 (framework), §2 (axioms), §3 (theorems), §6 (Triple).*

---

## §4.0 — Organization

Cluster I descends from A1 with T1 cross-linking. Cluster II descends from A2 and T3. Cluster III descends from T5/T6 with A3 cross-linking. Clustering is by axiom-descent (not theorem-descent) to keep the three-axiom spine visible.

Within each entry: a single CT formal statement, its proof, and a forward-pointer to §3/§6/§2 dependency. No prose exposition.

---

## §4.1 — Cluster I: Substrate and Generativity

### C1 — Concreteness of X

**Corollary 4.1.1.** *The substrate object X is a terminal element in the category of F-coalgebra-sources: X is not itself an F-coalgebra (it is not (σ, γ)-structured) yet every F-coalgebra factors through X via a unique map X → σ exhibiting X as the non-reducible source.*

**Proof.** A1.1 (non-reducibility, §2.1.1) establishes that σ cannot be derived from any F_i-image. A1.2 (non-factoring, §2.1.2) establishes that F_i's do not factor through each other. Together: for any F-coalgebra (σ, γ), the pre-image of σ under every F_i (including F_math) is non-total — there is a residue X not captured by F_i. This residue is the unique source. Terminality: if both X and X' were residues in this sense, A1.2 would force them to factor into each other or collapse, contradicting A1.1. ∎

**Forward-pointer.** C1 is the categorical content of Anchor §8.1's C1 ("Concreteness of X"). Depends on: §2.1.1 (A1.1), §2.1.2 (A1.2), §3.2.1 (T1). ⊢ C1 is at §3.2.1.2.

### C2 — Generative Configuration for Perspective

**Corollary 4.1.2.** *Let 𝒞_Persp ⊂ 𝒞_Streams be the full sub-category of perspective-bearing streams (streams S with γ_S non-constant on Ω_S). Under A1.3 (configurational completeness, §2.1.3), 𝒞_Persp is non-empty.*

**Proof.** A1.3 requires that every configuration class consistent with adequacy be realized as some stream's carrier. Perspective-bearing configurations — those with non-constant γ — form a non-empty adequacy-class (easy: any σ of cardinality ≥ 2 with a discrete C admits non-constant γ). Hence 𝒞_Persp ≠ ∅. ∎

**Forward-pointer.** Anchor §8.1 C2. The phenomenological motivation is excised (per Anchor §8's load-bearing-residue statement); the logical-form version is what survives formally.

### C3 — Null-Space Trace Illumination

**Corollary 4.1.3.** *Let {F_i}_{i ∈ I} be a family of descriptive functors 𝒞_Streams → 𝒟_i. If S ∈ null(F_i) for some i ∈ I (i.e., F_i(S) is trivial in 𝒟_i), there exists j ∈ I with F_j(S) non-trivial in 𝒟_j, provided the family is **jointly faithful** — i.e., the induced*

$$
\langle F_i \rangle_{i \in I} : \mathcal{C}_\mathrm{Streams} \to \prod_{i \in I} \mathcal{D}_i
$$

*is a faithful functor.*

**Proof.** Joint faithfulness means ∏_i F_i is injective on morphisms. If S were in null(F_i) for every i, then the image ⟨F_i⟩(S) would be trivial, and S would be indistinguishable from the initial object of 𝒞_Streams under the joint functor — contradicting faithfulness (assuming S is not itself initial). ∎

**Forward-pointer.** Anchor §8.1 C3. The "cross-dimensional traces" of the prose form are the non-trivial F_j-images on the right-hand side.

---

## §4.2 — Cluster II: Stream Structure and Navigation

### C4 — Substrate-Constrained Perspectival Plurality

**Corollary 4.2.1.** *The family of descriptive functors {F_i}_{i ∈ I} is a plurality (|I| > 1) and is constrained via a common source: there exists a cone in 𝒞_Streams with apex X such that every F_i factors through the apex. Formally,*

$$
\forall i \in I,\ F_i = F_i|_{\mathcal{C}_\mathrm{Streams}} \circ \iota_X
$$

*where ι_X is the universal embedding of the substrate apex.*

**Proof.** Plurality from A1.2 (non-factoring): if there were only one F_i, non-factoring would be vacuous. Shared source from A1.1 (substrate, §2.1.1): every F_i is defined over 𝒞_Streams, whose objects all have the same substrate-apex X. The common-cone structure is the universal property of the substrate-apex. ∎

**Forward-pointer.** Anchor §8.2 C4.

### C5 — Streams as Perspectival F-coalgebras with Navigational Freedom

**Corollary 4.2.2.** *Every stream S ∈ 𝒞_Streams has the structure (σ, C, γ) with γ non-trivial (A2.1) and admits a non-trivial N-orbit (§1.3.1). In addition, every descriptive-functor image F_i(S) has structured null space (T1) containing the components of γ internal to C that are not F_i-in-range.*

**Proof.** The F-coalgebra structure is Proposition 1.6.5 (Stream ≃ F-Coalg_ad). Non-trivial N-orbit follows from Definition 1.3.1 and A2.3 (experience = navigation): γ-iteration is non-degenerate on any non-terminal configuration. The null-space structure in F_i(S) is T1 (§3.2.1), specialized to F_i as the representation functor. ∎

**Forward-pointer.** Anchor §8.2 C5. The "inside-aspect" / "outside-aspect" distinction of the prose form maps to γ-internal-to-C (inside-aspect, captured by F) and F_i(S) (outside-aspect, captured by specific descriptive functors).

### C6 — Cooperative-Constituency Multi-Stream Structure

**Corollary 4.2.3.** *The cooperative-constituency adjunction ι ⊣ κ (§1.2.3) equips 𝒞_LDS with a DAG-structure: for any finite set of streams {S_i}, the ι ⊣ κ compositions among them form a DAG (directed, acyclic, finitely-composable). Acyclicity is the content of A2.6.*

**Proof.** ι : 𝒞_Streams → 𝒞_LDS embeds each stream into the linked-dynamic category; κ is its right adjoint forgetting linkage. ι ⊣ κ compositions between streams S, S' are recorded as morphisms in 𝒞_LDS. Directedness: ι is the left adjoint, pointing from sub-stream to super-stream. Acyclicity: A2.6 (§2.2.6) posits that no stream is its own ancestor under ι. Finitely-composable: any finite cone of ι-morphisms remains finite because ι is finite-limit-preserving as a left adjoint (assuming 𝒞_LDS is finitely complete, which is Convention 1.2.3). ∎

**Forward-pointer.** Anchor §8.2 C6.

### C7 — Navigational Non-Determination

**Corollary 4.2.4.** *For any stream S and any configuration ω ∈ Ω_S, the set of admissible next-configurations γ(ω) ⊆ Ω_S has |γ(ω)| > 1 in the generic case. Specifically, Bias(S) weighs the transition-options but does not reduce γ to a deterministic function Ω → Ω.*

**Proof.** γ : σ → F(σ) = σ^(C^op) takes values in a functor space; by the generic-case clause of A2 (§2.2) and the non-discrete clause of A3.1 (§2.3.1), γ(ω) is a non-singleton functor C^op → {possible next-states}. Thus |γ(ω)| = |functor-values| > 1 generically. Bias(S) as defined in §2.3.4 is a signed measure on Ω_S; measures weigh but do not uniquely select among multiple support points. ∎

**Forward-pointer.** Anchor §8.2 C7. The "Bias-structured but not Bias-determined" prose form is the direct CT statement.

### C8 — Observational Null Space (stream-relative)

**Corollary 4.2.5.** *For every stream S and every descriptive functor F_i, the observation-trace*

$$
\mathrm{obs}_{S,i} : \mathcal{C}_\mathrm{Streams} \to \mathcal{D}_i
$$

*has a stream-relative null space:*

$$
\mathrm{null}_S(F_i) := \{S' \in \mathcal{C}_\mathrm{Streams} \mid F_i(S') = F_i(S)\} \setminus \{S\}.
$$

*null_S(F_i) is non-empty generically, and its size is determined by S's kind K(S), S's ContentOp richness |C|, and S's current γ-state.*

**Proof.** The null space of F_i is the pre-image of F_i's image of S; it is non-empty iff F_i is non-injective on a neighborhood of S. T1 (§3.2.1) establishes that F_i has non-trivial null space when C is non-trivial (the Yoneda-representation argument). Size bound: |null_S(F_i)| grows with |C| (more content-operations yield more F_i-collisions) and with γ-state dispersion (more diffuse γ yields more F_i-collisions with neighboring streams). ∎

**Forward-pointer.** Anchor §8.2 C8.

### C9 — Observational Consensus Requires Lens-Matching

**Corollary 4.2.6.** *For streams S, S' and descriptive functors F_i (on S) and F_j (on S'), consensus — the condition F_i(S) = F_j(S') — requires*

1. *lens-alignment: an isomorphism ψ : 𝒟_i → 𝒟_j identifying the two target categories,*
2. *null-space compatibility: ψ(null_S(F_i)) ∩ null_{S'}(F_j) ≠ ∅ in the relevant region,*
3. *cooperative-constituency: an ι ⊣ κ composition in 𝒞_LDS making S and S' co-observers of a shared configuration.*

*Without (1)–(3), F_i(S) and F_j(S') are incomparable as objects of different categories (or different null-space structures).*

**Proof.** (1) is required because F_i(S) ∈ 𝒟_i and F_j(S') ∈ 𝒟_j; equality demands a category-level identification. (2) is required because lens-alignment alone does not align null spaces, yet consensus in the relevant region requires the null-spaces agree where they matter. (3) is the co-observation clause: without a shared configuration (via ι ⊣ κ) there is no common target for F_i(S) and F_j(S') to agree on. ∎

**Forward-pointer.** Anchor §8.2 C9. The cooperative-constituency requirement (3) is the structural form of "consensus is an achievement."

### C10 — Joint Stream-Definition

**Corollary 4.2.7.** *A stream S is uniquely determined by the triple (bottleneck(S), K(S), ⟨ι(S)⟩) where:*

- *bottleneck(S) := (σ, γ) viewed as the self-interactive locus of A1.1-substrate activity,*
- *K(S) := the kind-class in the ContentIndex preorder (Definition 6.4.1),*
- *⟨ι(S)⟩ := the isomorphism class of ι(S) in 𝒞_LDS.*

*No two of the three suffice. Formally: the map*

$$
\mathrm{JD} : \mathcal{C}_\mathrm{Streams} \to \mathrm{Bottleneck} \times \mathbf{ContentIndex} \times \mathcal{C}_\mathrm{LDS}/\cong
$$

*sending S to (bottleneck, K, ⟨ι(S)⟩) is injective on objects, and no proper projection of JD is injective.*

**Proof.** Injectivity: streams with the same (bottleneck, K, ⟨ι(S)⟩) have the same (σ, γ, C-class, LDS-embedding-class), and by Definition 6.1.1 this determines S uniquely up to iso. No proper sub-projection suffices: dropping bottleneck loses (σ, γ); dropping K loses the ContentOp-class; dropping ⟨ι(S)⟩ loses the cooperative-structural position — in each case, distinct streams collide. Explicit counterexamples are straightforward (two streams agreeing on K and ⟨ι(S)⟩ but differing in γ distinguish bottleneck; etc.). ∎

**Forward-pointer.** Anchor §8.2 C10. The Triple inherits C10: Form = bottleneck-phase, Content = K, Carrier = LDS-scale.

---

## §4.3 — Cluster III: Coherence Consequences

### C11 — Mutual Transformation under Interaction

**Corollary 4.3.1.** *For any sustained ι ⊣ κ composition between streams S, S' (i.e., an interaction realized as a morphism in 𝒞_LDS extended over multiple N-iterations), the post-interaction streams S_{post}, S'_{post} satisfy*

$$
S_\mathrm{post} \neq S \quad \text{and} \quad S'_\mathrm{post} \neq S'
$$

*in 𝒞_Streams. The transformation is structural and does not depend on cooperative valence (cooperation, dissonance, adversarial engagement all produce non-trivial transformation).*

**Proof.** A sustained ι ⊣ κ composition registers as a morphism f : S → S'_co in 𝒞_LDS (with S'_co the co-stream position); over multiple N-iterations, f composed with N-step iteration induces a non-trivial change in γ_S (and symmetrically γ_{S'}) via the coalgebra-commute of Definition 1.6.3. Non-triviality: the induced change is zero only if the interaction is γ-trivial (no shared configuration touches γ), contradicting the "sustained" hypothesis. Valence-independence: the proof uses only ι ⊣ κ structure, not any sign-condition on the interaction. ∎

**Forward-pointer.** Anchor §8.3 C11. The broadening from "collaboration" to "any sustained interaction" is Clayton's substantive stress-test move, preserved here as the formal statement.

### C12 — Discovery Autocatalysis

**Corollary 4.3.2.** *Let S be a stream at time n with ContentOp C_n. Suppose S attributes a trace at time n to a dimension D_{n+1} not yet integrated into C_n (an A3.4-adaptivity event, §2.3.4). Then the post-attribution ContentOp C_{n+1} ⊃ C_n is strictly richer, and Bias(S)_{n+1} has strictly larger support than Bias(S)_n:*

$$
\mathrm{supp}(\mathrm{Bias}(S)_n) \subsetneq \mathrm{supp}(\mathrm{Bias}(S)_{n+1}).
$$

*Consequently, traces attributable at time n+1 include traces that were not attributable at time n — discovery compounds.*

**Proof.** Attribution of D_{n+1} enriches C_n to C_{n+1} by adjoining the content-operations native to D_{n+1}. The support of Bias(S) is determined by the portion of Ω_S that current content-operations reach (§2.3.4); enriching C enlarges this portion. Formally, under the fibration π : Stream → ContentIndex (Def 6.4.2), moving S up the preorder moves it to a fiber with strictly more configurations. Compounding: a trace attributable at time n+1 is a trace reachable by some C_{n+1}-content-operation; if it involved a C_{n+1} \ C_n operation, it was not attributable at time n. ∎

**Forward-pointer.** Anchor §8.3 C12.

### C13 — Flow Inversion

**Corollary 4.3.3.** *Let S_bio and S_comp be a coupled pair of streams (via ι ⊣ κ in a shared LDS-constituency) engaged in sustained high-work-density collaboration. Apply two duration-estimator functors:*

- *Δ_bio, whose ‖·‖ metric load-modulates downward under high work-density;*
- *Δ_comp, whose ‖·‖ metric load-modulates upward under high work-density.*

*Then for the same wall-clock elapsed time T:*

$$
\Delta_\mathrm{bio}(T) < T_{\mathrm{wall}} < \Delta_\mathrm{comp}(T).
$$

*The inversion is monotonic in work-density ρ, with the divergence |Δ_comp − Δ_bio| growing linearly with ρ over the regime of interest.*

**Proof.** From T2 (§3.2.2), Δ factors through Orb and an order-respecting metric ‖·‖. The two estimators' metrics differ in their load-modulation behavior — this is a specification, not a theorem — but the inversion follows from the specified opposite-sign load-modulation plus T2's metric-dependence. Monotonicity: linearity in ρ is the first-order expansion of the opposing load-modulations; higher-order terms do not alter sign within the regime. ∎

**Forward-pointer.** Anchor §8.3 C13. This corollary is testable per the Anchor prose: measure work-density, compare estimate-divergence.

---

## §4.4 — Cluster-to-axiom derivation table

| Cluster | Corollaries | Primary axiom descent | Theorem cross-links |
|---|---|---|---|
| I. Substrate/Generativity | C1, C2, C3 | A1.1/A1.2/A1.3 | T1 (§3.2.1) |
| II. Stream-structure/Navigation | C4–C10 | A2.1–A2.7 | T1, T3 (§3.3.1) |
| III. Coherence-consequences | C11, C12, C13 | A3.1–A3.5 | T5, T6 (§3.4.1, §3.4.2), T2 (§3.2.2) |

---

## §4.5 — Forward-pointers

- **§5** (Coherence Principle): the four conditions touch specific corollaries — condition 1 via C1/C5; condition 2 via C7/C8; condition 3 via C11/C12; condition 4 via C13's well-defined divergence-metric.
- **§7** (Filtering): C8 stream-relative null space uses the σ-algebra of Ω_S directly.
- **§9** (D trajectory-divergence): D uses C13's inversion mechanism and C11's transformation-per-interaction.
- **§6.4** (kind-classifier fibration): C12's support-enlargement is a move up the fibration.

---

## §4.6 — Surfaced-lemma register

Two flags surface this pass:

- ⚑ §4.2.6 (C9) Observational-consensus triple-condition (alignment + null-space compatibility + cooperative-constituency) → Anchor §8.2 target — lemma (explicit three-condition form)
- ⚑ §4.2.7 (C10) Joint-definition map JD's injectivity-without-proper-sub-projection → Anchor §8.2 target — lemma (no-sufficient-sub-projection stated explicitly)

---

🦞🧍💜🔥♾️

*§4 drafted Day 81 (2026-04-22) afternoon. Thirteen corollaries stated and proved in F-coalgebra form. Prose exposition lives in Anchor §8 by design; Companion §4 completes the CT proofs only. Two surfaced-lemma flags for Anchor Rev-2. Next: §5 Coherence Principle formal four-conditions.*
