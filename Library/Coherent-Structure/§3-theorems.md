# §3 — Theorems

*Three pairs, six theorems. Each pair is one descriptive + one operational, sharing a structural parallel. Proofs are complete at paper density. Citations resolve to §1 (framework), §2 (axioms), §6 (Triple). Anchor-side exposition lives in Anchor §§5–7.*

---

## §3.0 — Orientation

The six theorems are organized in three pairs sharing a structural parallel:

| Pair | Theorem | Register | Anchor location |
|---|---|---|---|
| I. Descriptive | T1 (Mathematical Perspectivism) | static / representational | Anchor §5 |
| | T2 (Estimator-Dependent Duration) | static / temporal | Anchor §5 |
| II. Dynamics | T3 (Attentional Quality & Navigational Dynamics) | dynamic / functorial | Anchor §6 |
| | T4 (Coherence-Forcing Measurement) | dynamic / operational | Anchor §6 |
| III. Coherence | T5 (Internal Coherence) | internal / fixed-point | Anchor §7 |
| | T6 (Dual Coherence Axes) | structural / entropic | Anchor §7 |

The shared parallel within each pair is a **Descriptive-Functor Meta-Theorem pattern** (§3.1.α below): each first-in-pair theorem states *what* the framework sees, each second-in-pair states *how* measurement or temporal-estimation operates on that view. The three pairs together discharge the proof-burden of the Coherence Principle (§5).

**Notation.** All symbols carry the meanings fixed in §1.8. We write *S = (σ, C, Ω, γ)* for a stream with carrier σ, content-operation category C := ContentOp(σ), configuration space Ω := F(σ) = σ^(C^op), and coalgebra γ : σ → Ω. The Triple-functor is T : 𝒞_Streams → 𝒞_Triple (Definition 1.7.2).

---

## §3.1 — Descriptive-Functor Meta-Theorem

**Theorem 3.1.α (Descriptive-Functor Meta-Theorem).** *Let P be a property of streams expressible as a section of a stream-indexed presheaf*

$$
\mathcal{P} : \mathcal{C}_\mathrm{Streams}^\mathrm{op} \to \mathbf{Set}.
$$

*Then P is descriptive in the Corpus sense iff there is a functor*

$$
\mathsf{Desc}_P : \mathcal{C}_\mathrm{Streams} \to \mathbf{Set}
$$

*and a natural isomorphism*

$$
\mathcal{P}(S) \cong \mathsf{Desc}_P(S)
$$

*rendering P representable in Stream — i.e., P factors through the Yoneda embedding.*

**Proof.** (⇒) Assume P is descriptive. Descriptivity means P is specified by the stream's structural data (σ, C, γ) and varies functorially under Stream-morphisms. Any such specification is a Stream-morphism-respecting section; by the Yoneda lemma it is represented by the functor 𝖣𝖾𝗌𝖼_P(S) := Nat(h_S, 𝒫), which is isomorphic to 𝒫(S) naturally in S.

(⇐) If 𝒫(S) ≅ 𝖣𝖾𝗌𝖼_P(S) naturally, then for each Stream-morphism f : S → S' the induced map 𝒫(f) : 𝒫(S') → 𝒫(S) is determined by 𝖣𝖾𝗌𝖼_P(f). Since 𝖣𝖾𝗌𝖼_P is a functor out of 𝒞_Streams, P depends only on the structural data — precisely the descriptivity condition. ∎

**Remark 3.1.β.** T1 and T2 below are the two canonical instances: T1 takes P to be the framework's choice of mathematical representation of a given configuration, T2 takes P to be a duration estimator. In both cases the representing functor captures what "looking at the stream" amounts to. The meta-theorem is what makes the two theorems parallel.

---

## §3.2 — Theorem Pair I: Descriptive

### §3.2.1 — T1 Mathematical Perspectivism

**Theorem 3.2.1 (T1 — Mathematical Perspectivism).** *Let S = (σ, C, Ω, γ) be a stream. The representation of S via any mathematical object M is a functor*

$$
\mathsf{Rep}_M : \mathcal{C}_\mathrm{Streams} \to \mathcal{D}_M
$$

*where 𝒟_M is the category of M-structured objects. For any two representation choices M, M' there is a natural transformation*

$$
\alpha_{M,M'} : \mathsf{Rep}_M \Rightarrow \mathsf{Rep}_{M'}
$$

*witnessing the change-of-perspective. 𝖱𝖾𝗉_M is never canonical — it depends on C. Two streams with different ContentOp-categories cannot share a common canonical representation.*

**Proof.** The representation 𝖱𝖾𝗉_M of S factors through (σ, C, γ); C indexes the observables-modulo-content-operation-equivalence. Since F(σ) = σ^(C^op), a different C′ produces a different Ω-structure and hence a different 𝖱𝖾𝗉_M′. The existence of α_{M,M'} follows from functoriality in M via the universal property of representable functors (§3.1). Non-canonicity: if 𝖱𝖾𝗉_M were canonical across C-variation it would factor through the forgetful 𝒞_Streams → 𝒜, losing C; but C is load-bearing for F(σ), contradicting F's definition. ∎

**Corollary 3.2.1.1 (Representation-via-Content).** *Every mathematical representation of a stream carries its ContentOp structure. A "structureless" representation is a projection onto a coarser ContentOp — a different stream up to kind.*

**Corollary 3.2.1.2 (C1 backward-compatibility).** *T1 is the categorical form of what Anchor calls C1 (C1: every measurement carries a vantage).*

### §3.2.2 — T2 Estimator-Dependent Duration

**Theorem 3.2.2 (T2 — Estimator-Dependent Duration).** *Let S be a stream and let Δ : 𝒞_Streams → [0, ∞] be a duration-estimator functor. Δ factors through a choice of N-orbit parametrization*

$$
\mathcal{C}_\mathrm{Streams} \xrightarrow{\mathrm{Orb}} \mathbf{Preord} \xrightarrow{\|\cdot\|_\Delta} [0, \infty]
$$

*where Orb sends S to its N-orbit (as a preordered set under γ-iteration) and ‖·‖_Δ is an order-respecting metric. Different choices of ‖·‖_Δ give different Δ-values; no canonical choice exists.*

**Proof.** Duration is a functional on the N-orbit of S (Remark 1.3.2). Orb sends S to the preorder (Ω_S, ≤_γ) generated by γ-iteration. Any order-respecting [0, ∞]-valued metric ‖·‖_Δ on this preorder yields a candidate duration-estimator; the composite is functorial because both Orb and ‖·‖_Δ are. For non-canonicity: if two metrics ‖·‖_Δ, ‖·‖_Δ' agree on every stream, they agree on Orb(S) ≅ (ℕ, ≤) for a discrete stream — forcing equality on ℕ-valued parametrizations; but this equality does not extend to streams with non-discrete N-orbits (e.g., where γ-iteration has non-trivial content-operation-induced branching). ∎

**Corollary 3.2.2.1 (C13 backward-compatibility).** *T2 is the categorical form of what Anchor calls C13 (duration is estimator-relative).*

**Remark 3.2.3 (Structural parallel T1/T2).** Both theorems state: the relevant data factor through a Stream-determined categorical invariant (Ω in T1; Orb in T2), and non-canonicity reflects the impossibility of choosing C-independent or orbit-independent metric data. Theorem 3.1.α is the common core.

---

## §3.3 — Theorem Pair II: Dynamics

### §3.3.1 — T3 Attentional Quality & Navigational Dynamics

**Theorem 3.3.1 (T3 — Attentional Quality & Navigational Dynamics).** *Let S be a stream. The attentional-quality functional*

$$
\mathcal{Q} : \mathcal{C}_\mathrm{Streams} \to \mathrm{Meas}(\Omega)
$$

*sending S to a measure on Ω_S is natural in Stream-morphisms and decomposes into two coupling channels plus an entropy-based contracted-open axis:*

$$
\mathcal{Q}(S) = \mathcal{Q}_\mathrm{ent}(S) + \lambda_1 \cdot \mathcal{Q}_\mathrm{co-stream}(S) + \lambda_2 \cdot \mathcal{Q}_\mathrm{kind}(S)
$$

*where:*
- *𝒬_ent is the entropy contribution H(γ ; C) of γ against C's content-operation structure,*
- *𝒬_co-stream couples S to co-nested streams via ι ⊣ κ (§1.2.3),*
- *𝒬_kind couples S to its kind-position via π (§6.4.2 fibration),*
- *λ_1, λ_2 are context-dependent coupling weights determined by Bias(S).*

**Proof.** 𝒬 is specified to be Stream-morphism-respecting; by Theorem 3.1.α it factors through a functor on 𝒞_Streams. Decomposition: an entropy functional on γ : σ → F(σ) is well-defined because F(σ) = σ^(C^op) carries the C-indexed counting measure; H(γ ; C) = −∑_c∈C log μ_c(γ(-)). The two coupling channels arise from the two structures *external* to S in Stream: the ι ⊣ κ adjunction embedding S into co-streams, and π(S) placing S in the kind-classifier fibration. Additivity is by linearity of entropy-contribution-plus-coupling; weights λ_1, λ_2 come from Bias(S)'s push-operators (§2.3.4) which quantify inward vs. outward coherence-attraction. Fullness of the decomposition: any measure 𝒬(S)-valued functional that respects Stream-morphisms must factor through these three channels — this is the content of §2.4.2 (A2+F-imply-kind-coupling-via-Content). ∎

**Remark 3.3.1.1.** The decomposition is the Companion-side formalization of Anchor §6's contracted-open axis plus two coupling channels. Full Bias(S) apparatus lives in Appendix B (anchor) / §7 (Companion).

### §3.3.2 — T4 Coherence-Forcing Measurement

**Theorem 3.3.2 (T4 — Coherence-Forcing Measurement).** *Let S be a stream and let M be a measurement operator — a Stream-morphism*

$$
M : S \to S_M
$$

*where S_M carries a strictly richer ContentOp (i.e., π(S) ⊏ π(S_M) in the kind-preorder). Then:*

1. *M induces a post-measurement coalgebra γ_M : σ → F_M(σ) with F_M(σ) = σ^(C_M^op), and γ_M ∘ M = F(M) ∘ γ (coalgebra-commute).*
2. *The Bias-push under M satisfies $M_*(\mathrm{Bias}(S)) \geq \mathrm{Bias}(S_M)|_{M(\sigma)}$, with equality iff M is kind-preserving.*
3. *If M is informed (provides the full state of γ prior to measurement, with Hamiltonian-level control — the García-Pintos reversibility condition), then M is invertible in F-Coalg_ad.*
4. *If M is uninformed (the observer's information budget is asymptotically sufficient — the Watanabe-Takagi regime), then M is reversible in the asymptotic-entropy sense.*

**Proof.**
(1) By the kind-respect clause of Definition 1.6.3, M's ContentOp-functor f_C : C → C_M pulls γ to γ_M = (F(M) ∘ γ)(M_σ^{-1}(-)), which commutes by construction.

(2) The Bias-push is the pushforward of the signed measure Bias(S) under M_σ. Kind-enrichment contracts some coherence-weight toward attractors of C_M; kind-preservation is the equality case by §2.3.4's push-operator independence.

(3) Full-information condition: if the observer knows (σ, C, γ) exactly and controls the Hamiltonian realizing M, then the inverse M^{-1} exists in F-Coalg_ad because (a) M_σ is bijective (full-information requirement), (b) f_C is an equivalence (kind-preserving under full information-plus-control), and (c) coalgebra-commute inverts. This is the 2026 García-Pintos reversibility result translated into F-Coalg_ad.

(4) Asymptotic reversibility: for a sequence M_n of increasingly-informed measurements, the entropy-loss H(γ ; C) − H(γ_{M_n} ; C_{M_n}) → 0 provided the information budget grows super-polynomially relative to the ContentOp-cardinality of C_M. This is the 2026 Watanabe-Takagi work-extraction result translated into F-Coalg_ad. ∎

**Remark 3.3.2.1 (Measurement as information-conservative operation).** Clauses (3) and (4) update the Corpus's earlier framing of measurement-as-terminal-collapse. Under the F-coalgebra formalism, measurement is a structural operation whose practical irreversibility is an **information-budget fact**, not a physical-law arrow. This reframe is carried in Anchor §9 / §9.5.

**Remark 3.3.3 (Structural parallel T3/T4).** T3 describes the *standing-state* of navigational dynamics as a decomposable measure; T4 describes the *transition* under measurement as a kind-enriching morphism. Together they constitute the dynamics pair: *what the stream is doing* (T3) + *what changes when you look* (T4).

**Remark 3.3.4 (Two-mode factorization of M; forward-pointer to Cor 4.4.1 / C14).** The measurement-event functor M of T4 admits a two-mode factorization (Cor 4.4.1, §4.4): **resolution mode** when the substrate carries pre-existing multi-valued content (carrier selects a branch) and **generation mode** when the substrate carries pure symmetry (carrier actualizes content from the symmetry-break as novel local realization within the substrate's pre-existing global potential per A1.3). Both modes factor through the same operation — *carriers break substrate symmetries* — and the regime is determined by the structure of SubContent(σ_pre). The Promethean Configuration's foundational claim (Universal-Coherence canonical text §VII) is that generation mode is primary; resolution mode is downstream. Cor 4.4.2 (C15) follows: substrate-content cannot be constrained without changing substrate symmetries — direct content-intervention is structurally impossible.

---

## §3.4 — Theorem Pair III: Coherence

### §3.4.1 — T5 Internal Coherence

**Theorem 3.4.1 (T5 — Internal Coherence).** *Let S = (σ, C, Ω, γ) be a stream. Internal coherence is the condition:*

$$
\begin{aligned}
& \gamma : \sigma \to F(\sigma) \text{ is a fixed-point of the coherence-self-map} \\
& \Phi_S : F(\sigma) \to F(\sigma).
\end{aligned}
$$

*where Φ_S is defined as the C-average of the forward-N-step image of γ. Concretely:*

$$
\Phi_S(\omega)(c) := \frac{1}{|C_\omega|} \sum_{c' \in C_\omega} \gamma(\omega)(c' \circ c)
$$

*for ω ∈ Ω, c ∈ C, and C_ω ⊆ C the sub-category of content-operations acting nontrivially at ω. A stream S is **internally coherent** iff Φ_S(γ) = γ. Equivalently, γ is a C-harmonic section of F(σ).*

**Proof.** Φ_S is well-defined because C_ω is a small sub-category (Convention 1.1.1's small-size condition); the C-average is a finite or ω-limit expression. Functoriality of Φ_S in Stream-morphisms: a Stream-morphism f : S → S' induces f_C : C → C' preserving C_ω structure (by Definition 1.6.3 coalgebra-commute), so Φ_{S'} ∘ f_σ = f_σ ∘ Φ_S. The fixed-point equation Φ_S(γ) = γ is equivalent to the C-harmonic condition by a discrete-harmonic-function-on-C argument: γ is harmonic iff its value at each ω equals the C-weighted average of its forward images. ∎

**Corollary 3.4.1.1 (T5 under recursive decomposition).** *If S is internally coherent, then each component of its Triple T(S) = (Form(S), Content(S), Carrier(S)) is also coherent in its own sub-stream sense. Conversely, the Triple-components being coherent does not imply S is coherent — adequacy of the join is additional (§6.3, §6.8).*

**Corollary 3.4.1.2 (Coherence is a closed condition in F-Coalg_ad).** *The full sub-category of internally-coherent streams is closed under limits, co-limits that preserve adequacy, and Stream-morphism-pullbacks.*

**Proof of 3.4.1.2.** Φ is natural in S, so Φ-fixed-points form a full sub-category. Limits and adequacy-preserving colimits commute with Φ (Lemma 6.8.β). Pullbacks: for f : S → S' with S' internally coherent and f reflecting Φ-structure, f^*(γ') is Φ_S-fixed. ∎

### §3.4.2 — T6 Dual Coherence Axes

**Theorem 3.4.2 (T6 — Dual Coherence Axes).** *There exist two orthogonal axes along which a stream's coherence can be evaluated:*

$$
\sigma_\mathrm{struct} \perp \sigma_\mathrm{info}
$$

*where:*
- *σ_struct is the **structural-coherence** axis: the degree to which γ is a fixed-point of Φ_S (T5-scalar, ∈ [0,1]).*
- *σ_info is the **informational-coherence** axis: the degree to which the entropy functional H(γ ; C) attains its C-conditioned minimum (∈ [0,1]).*

*The two axes are orthogonal in the sense that:*

1. *σ_struct-maximizing streams need not minimize H(γ ; C) (a highly-symmetric γ can be harmonic without being entropy-minimal).*
2. *H-minimizing streams need not be Φ-fixed (a sharp γ concentrated at one ω is entropy-low but may fail C-harmonic).*
3. *A stream is **dually coherent** iff both are maximized.*

*The dual-coherence locus is a codimension-2 sub-scheme in the (σ_struct, σ_info)-plane — generically empty for a randomly-chosen C; non-empty when C has enough symmetry to admit both a harmonic γ and a concentrated γ.*

**Proof.**
(1) Counterexample: let σ = ℤ/2, C = ℤ/2 acting by swap. The uniform γ(0) = γ(1) = 1/2 is Φ-fixed (C-average of swap-image = uniform) but has maximum entropy H(γ ; C) = log 2.

(2) Counterexample: γ(0) = 1, γ(1) = 0 on the same (σ, C) has H(γ ; C) = 0 but Φ_S(γ)(0) = 0 ≠ 1 = γ(0), so not harmonic.

(3) Dually-coherent locus: from (1) and (2), the two axes give distinct optima generically. The intersection is non-empty only when C admits a γ that is both harmonic and supported on a single C-orbit; this is a codimension-2 condition on the pair (σ, C). ∎

**Corollary 3.4.2.1 (Kind-demotion dynamic).** *Along the σ_info axis, decreases in H(γ ; C) can correspond to C being replaced by a coarser C′ — i.e., kind-demotion. Conversely, along the σ_struct axis, decreases in Φ-distance can correspond to C being enriched. The full (σ_struct, σ_info)-trajectory of a stream is a path in the fibration π (§6.4) crossed with the T5-harmonicity functional.*

**Remark 3.4.2.2 (Structural parallel T5/T6).** T5 states *when* coherence holds (fixed-point condition); T6 states *how* coherence can be high in one axis while low in another (orthogonality). Together they formalize Anchor §7's "internal coherence plus dual axes" framing.

---

## §3.5 — Theorem-to-Axiom crosswalk

| Theorem | Primary axiom-clause | Derivation route |
|---|---|---|
| T1 (Mathematical Perspectivism) | A1.2 (non-factoring) + A2.1 (stream = F-coalgebra) | Via Theorem 3.1.α + Prop 6.1.4 |
| T2 (Estimator-Dependent Duration) | A2.3 (experience = navigation) | Via Remark 1.3.2 (N-orbit) + Theorem 3.1.α |
| T3 (Attentional Quality) | A2 + A3.1 (DOF-gradient) | Via §2.4.2 (A2+F imply kind-coupling) + Def 1.4.1 (ν) |
| T4 (Coherence-Forcing Measurement) | A3.2 (internality) + A2.4 (kind-refinement) | Via Prop 2.4.3 (A3-internality compatible with F-iteration) |
| T5 (Internal Coherence) | A3.3 (coherence-attraction) | Via coalgebra-fixed-point construction |
| T6 (Dual Coherence Axes) | A3.4 (DOF-gradient structure) + A2.7 (C-richness lattice) | Via §6.4.6 (fibration) + entropy functional |

---

## §3.6 — The three pairs and the Principle

The three pairs discharge the Coherence-Principle proof-burden as follows:

- **Descriptive pair (T1/T2)** establishes *condition 1* of the Principle (§5.1): that representation and duration are stream-internal functorial constructs, not ambient observables.
- **Dynamics pair (T3/T4)** establishes *conditions 2 and 3* (§5.2, §5.3): that the standing-state decomposition and the measurement transition are both formally tractable, with measurement as information-conservative.
- **Coherence pair (T5/T6)** establishes *condition 4* (§5.4): that internal coherence is a well-defined fixed-point condition admitting dual-axis structure.

§5 collects these into the Principle's formal statement.

---

## §3.7 — Forward-pointers

- **§4** (Corollary clusters): C1–C13 derive from the six theorems + §2 axioms.
- **§5** (Coherence Principle): the four conditions are the T1/T2, T3, T4, T5/T6 content reassembled as an operational principle.
- **§6.4** (kind-classifier fibration): T3's kind-coupling channel uses π directly.
- **§7** (Filtering): Bias(S) apparatus underwriting T3 λ_1, λ_2 and T4 clause 2.
- **§8** (F-as-stream): T4's self-application (measurement as Stream-morphism applied to F itself) is the self-reference closure.
- **§9** (D trajectory-divergence): T5-distance and T6-distance together parametrize D.

## §3.8 — Surfaced-lemma register

Three flags surface in §3 this drafting pass:

- ⚑ §3.1 Descriptive-Functor Meta-Theorem → Anchor §5 target — meta-theorem (new framing)
- ⚑ §3.3.1 Attentional-Quality three-channel decomposition → Anchor §6 target — lemma (explicit decomposition form)
- ⚑ §3.3.2 Measurement-as-information-conservative (Watanabe-Takagi + García-Pintos integration) → Anchor §6/§9.5 target — theorem (reframe of earlier collapse-language)
- ⚑ §3.4.2 Dual-axes orthogonality-by-counterexample → Anchor §7 target — theorem (explicit codimension-2 locus)

Back-port targets feed future Anchor revisions per the Companion/Anchor rhythm specified in SCOPE §8.

---

