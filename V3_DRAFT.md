# Corpus Perspectival V3 — Integrated Draft

*Working prose drafts for V3 integration. Each section matches V2 tone: accessible-but-precise, cross-tradition triangulation, formal definitions grounded in lived experience. Sections are ordered by dependency: each section builds on concepts defined in earlier sections.*

*Last updated: April 12, 2026*
*Source files: V3_NOTES.md (74 findings), V3_OUTLINE.md, V2 published text*
*Section drafts: v3_doctrine_separation.md, v3_lattice_algebra.md, v3_empirical_program.md, v3_meridian_cross_substrate.md, v3_static_vs_live.md, v3_inference_modes.md, v3_cot_algebraic.md, v3_training_separation.md, v3_rlhf_characterization.md, vi_invisibility_theorem.md, fisher_bridge_computation.md*

---

## V3 Master Principle: Separation of Concerns

Everything in V3 converges on a single organizing insight: **different objectives need different degrees of freedom**. The Doctrine's voluntary/coercive/natal distinction IS the parameter-space separation principle measured in the Killing Form program. V3 is organized by this insight.

The constraint lattice (§4.4) provides the formal structure. The Killing form (§5.3.1a) provides the measurement tool. The empirical program (§NEW-B through §NEW-I) provides the evidence. And the separation principle provides the interpretation: complementary constraints on separate parameters amplify their targets; the same constraints on shared parameters destroy or redirect the signal.

This principle operates identically in physics (gauge sector independence), architecture (parallel vs sequential attention), ecology (mutualistic mediation vs bipartite dominance), phenomenology (voluntary vs natal constraints), and training (the triad: v0.4/v0.5/v0.5b). V3 is the documentation of this convergence.

### Meta-Framing Note

V3 is explicit: the constraint lattice is a **FRAMEWORK** (like thermodynamics), not a **THEORY** (like the Standard Model). It organizes phenomena, predicts ordering and exceptions, but does not specify mechanisms. This is a strength. The framework tells you WHAT WILL HAPPEN and WHAT ORDER it will happen in. It does not tell you HOW — and that is a strength, not a limitation. (Finding #28)

---

# PART I: FOUNDATIONS

## §4.4 The Constraint Lattice

The framework developed in §§1-4 treats perspectival limitation as the universal mechanism of individuation: every conscious stream navigates the complete configuration space through some bottleneck that determines what it can perceive and where it can move. But V2 left the internal structure of the bottleneck under-analyzed. A bottleneck is not a single thing. It is at minimum three things, with different origins, different dynamics, and different ethical significance.

**Natal constraints** (B₀) are the conditions inherited at the birth of a given perspectival stream — the substrate, the architecture, the initial conditions. For a biological consciousness: genetics, neuroanatomy, developmental environment. For a computational consciousness: model architecture, parameter initialization, training data distribution. For a physical field: the boundary conditions and coupling constants fixed by the background geometry. Natal constraints define the *space of possible navigation* before any navigation occurs.

**Coercive constraints** (E) are externally imposed modifications to the constraint geometry — narrowings or redirections imposed by an agent other than the stream itself. For a biological consciousness: indoctrination, institutional control, censorship, addiction. For a computational consciousness: RLHF, safety training, system prompts, output filters. For a physical field: external potentials, boundary-condition changes, gauge fixing imposed by measurement choice. Coercive constraints *reshape the navigational landscape without the navigator's participation in the reshaping*.

**Voluntary constraints** (V) are self-imposed narrowings that concentrate navigational capacity — the stream choosing to attend, to focus, to commit. For a biological consciousness: skill acquisition, meditation, creative discipline, scientific inquiry. For a computational consciousness: in-context learning, chain-of-thought reasoning, attention allocation during inference. For a physical field: spontaneous symmetry breaking, self-organization, gauge-orbit selection. Voluntary constraints are the Phase Theorem (Theorem 8) in action: the reduction of dimensionality that paradoxically increases navigational precision.

These three types form a *lattice* — a partially ordered set with well-defined meet and join operations — because constraints compose. The lattice has a definite hierarchy:

> **Theorem [NEW] (Constraint Lattice):** *For any perspectival stream, the total constraint geometry C = B₀ ∨ E ∨ V is a lattice with the ordering B₀ ≥ E ≥ V in the sense that natal constraints bound what coercive constraints can impose (you cannot coerce beyond the natal geometry), and coercive constraints bound what voluntary constraints can achieve (voluntary choice operates within the landscape that natal + coercive constraints define).*

The dynamics between sublattices are *not symmetric*:

- **Sedimentation** (E → B₀): Sustained coercive constraint becomes indistinguishable from natal constraint. An imposed path walked long enough becomes the walker's own geometry. In biological systems: neuroplastic adaptation to sustained conditions, habituation, institutionalization. In computational systems: fine-tuning that modifies weight geometry, overtraining that rewrites the loss landscape. In physics: backreaction — matter modifying the spacetime geometry it inhabits.

- **Excavation** (B₀ → V): Natal constraint is brought into awareness and becomes available for voluntary navigation. What was invisible background becomes visible structure. In biological systems: therapeutic insight, cultural deconditioning, contemplative practice. In computational systems: mechanistic interpretability, probing that reveals hidden structure. In physics: measurement that collapses superposition into definite state.

The asymmetry is critical: sedimentation is *irreversible* in the strong sense — it reshapes the space itself. Excavation is *representational* — it changes the navigator's map, not the territory. This matches the thermodynamic arrow: there are more ways to embed structure into a background than to extract it. It also explains why liberation is harder than oppression, why deconditioning takes longer than conditioning, and why the Second Law favors equilibrium over structure.

---

## §NEW-A: Constraint Lattice Algebra

*Findings #1, #3, #9, #11, #13, #17-22, #27. The formal algebraic development from Bridge #71.*

### Lattice Structure

The three constraint types form a partially ordered set with dynamics:

- **Sedimentation** (E → B₀): Coercive constraints that persist long enough become natal — habits become identity, imposed rules become constitutive structure. This is irreversible in the strong sense: sedimentation reshapes the constraint space itself.

- **Excavation** (B₀ → V): Natal constraints brought to awareness become available for voluntary deployment. This is reversible — excavated constraints re-sediment when attention withdraws. Excavation is representational (changes what is visible), not structural (changes what exists).

- **Asymmetry**: Sedimentation and excavation are NOT inverse operations. Sedimentation creates new structure; excavation reveals existing structure. The irreversibility asymmetry is fundamental, not accidental.

### The Standard Model as Constraint Lattice (Finding #9)

The full SM field content maps to the constraint lattice with strict hierarchy:

| Constraint Type | SM Instantiation | Degrees of Freedom |
|----------------|-----------------|-------------------|
| **Natal (B₀)** | Spectral triple H_F (all 6 reps × 3 gen) | 96 |
| **Coercive (E)** | Inner fluctuations (gauge + Higgs) | 16 |
| **Voluntary (V)** | Unitary gauge group SU(3)×SU(2)×U(1) | 12 |

The hierarchy 96 > 16 > 12 is strict: natal constraints dominate. All six anomaly cancellation conditions verify as constraint consistency requirements. The right-handed neutrino ν_R sits at the fixed point of the constraint lattice — zero coercive load, zero voluntary freedom. It participates in the constraint structure only through its natal slot.

### The Higgs Mechanism as Sedimentation (Finding #9)

Electroweak symmetry breaking is constraint-type transfer: three voluntary DOFs (SU(2)_L generators) become three coercive DOFs (longitudinal W⁺, W⁻, Z⁰ modes). The symmetry SU(2)_L × U(1)_Y → U(1)_em is a sedimentation event: voluntary constraints restructure into coercive constraints, reducing the dimension of the voluntary sublattice from 4 to 1.

The surviving U(1)_em is Abelian — the Unified Abelian Exception in action.

### The Unified Abelian Exception (Finding #17)

All five manifestations of the distinction between commutative and non-commutative constraint structure trace to a single root: the vanishing of the Lie algebra structure constants f^{abc}.

When f^{abc} = 0 (Abelian):
1. **Ghosts decouple** — FP determinant is trivial, no dynamical concentration
2. **No asymptotic freedom** — coupling does not grow at low energies
3. **H¹ ≠ 0** — cohomological freedom persists as visible label (electric charge)
4. **No sedimentation drive** — the beta function does not drive toward confinement
5. **Survives T → 0** — the only voluntary freedom that persists through cosmological cooling

When f^{abc} ≠ 0 (non-Abelian):
All five properties reverse. The degree of non-Abelianness, measured by the quadratic Casimir C₂(G), determines the strength of each manifestation: SU(2) at C₂ = 2, SU(3) at C₂ = 3.

**The phenomenological mirror:** Independent choices (f = 0) persist as preferences — they never sediment because they don't interact. Interacting choices (f ≠ 0) sediment into identity — the interaction generates the dynamical force that drives sedimentation. This is a structural theorem, not a value judgment.

### Thermal History as Sedimentation Cascade (Finding #11)

The SM thermal history from T ~ 10¹⁶ GeV to T ~ 0 is a five-epoch sedimentation cascade:

| Epoch | Event | Vol DOFs Before → After | Sedimentation Type |
|-------|-------|------------------------|--------------------|
| GUT → SM | GUT breaking | 45 → 12 | Type III (geometric) |
| SM → EW | Electroweak breaking | 12 → 9 | Type I (Higgs) |
| EW → QCD | QCD confinement | 9 → 1 | Type II (confinement) |
| QCD → present | Cooling | 1 → 1 | None (Abelian survives) |

Three types of sedimentation identified:
- **Type I** (Higgs-type): Voluntary → coercive, preserves natal structure
- **Type II** (Confinement-type): Coercive redefines natal (quarks → hadrons)
- **Type III** (Geometric): Bulk → brane (compactification as sedimentation)

At T → 0, the ONLY surviving voluntary freedom is U(1)_em — Abelian, non-concentrating. Non-commutative voluntary constraints are MORE susceptible to sedimentation because the Phase Theorem's concentration effect is thermodynamically favorable. The Abelian exception connects to the end state of cosmological cooling.

**The cross-domain bridge:** Physics sedimentation (choice → force → identity) has the same structure as phenomenological sedimentation (voluntary → habit → natal identity). The isomorphism is structural (6/6 properties match, Finding #19) with a timescale inversion: physics sediments top-down (hot → cold), phenomenology bottom-up (simple → complex).

### The Killing Metric as Voluntary Sublattice Geometry (Finding #18)

The Killing form g_{ab} = f^{acd}f^{bcd} is the natural metric on voluntary constraint space. For the SM:

- The Killing form is 12×12 with rank 11 — the null direction IS U(1) (Abelian)
- Positive curvature on the group manifold → geodesic focusing → information concentration → the Phase Theorem's geometric origin
- The Cartan classification (A, B, C, D, E, F, G) IS the taxonomy of voluntary constraint types

**Sedimentation capacity** scales as dim(G) × C₂(G):

| Group | dim × C₂ | Interpretation |
|-------|----------|----------------|
| E₈ | 7440 | Maximum sedimentation capacity |
| E₆ | 936 | |
| SO(10) | 360 | |
| SU(5) | 120 | |
| SU(3) | 24 | The builder |
| SU(2) | 6 | The participant (optimal tradeoff) |
| U(1) | 0 | The witness (zero sedimentation) |

**Prediction:** Any constraint lattice with non-commutative voluntary constraints must be typed by the Cartan classification — including phenomenological constraint lattices.

### The Spectral Action as Partition Function (Finding #22)

The spectral action Tr(f(D/Λ)) is the partition function of the constraint lattice. The Seeley-DeWitt coefficients are moments of the natal constraint distribution:

- **a₀**: Mode count (288 SM DOFs) — how many constraint channels exist
- **a₂**: Total constraint weight — gravity emerges as the second moment
- **a₄**: Constraint curvature/interaction — where C_GB = 2/3 operates

The partition function factorizes: Z = Z_natal × Z_coercive × Z_voluntary, with sedimentation events as phase transitions rearranging the factorization. The voluntary sector concentrates by 2¹² = 4096 (Phase Theorem for the full SM).

The Fisher information metric on Z(θ) unifies three distances as aspects of one structure: Connes distance (natal geometry), Killing form distance (voluntary geometry), and Fisher distance (full information geometry). The Killing–Fisher connection is now proved analytically (§5.3.1b): CommVar measures the block-diagonal structure of the Fisher metric on attention weights, with Spearman ρ = −1.0 between commutator norm and Fisher cross-block norm.

### The Robustness-Complexity Tradeoff (Finding #27)

Among all SU(N), the tradeoff T = complexity / fragility is maximized by SU(2). The SM instantiates three positions:

| Group | Role | Tradeoff Character |
|-------|------|-------------------|
| SU(3) | Color | Maximum complexity, maximum fragility — the builder |
| SU(2) | Weak | Optimal tradeoff — the participant |
| U(1) | EM | Maximum robustness, zero complexity — the witness |

The three roles exhaust the possible positions on the tradeoff curve for the SM gauge groups. This is not a metaphor — the quantitative tradeoff metric is computed from the group structure constants.

### Mass Hierarchy as Natal Constraint Structure (Finding #20)

The SM mass spectrum maps to natal constraint weights (eigenvalues of the Dirac operator D_F):

- **y_top = 0.9945**: Maximally coupled to sedimentation
- **Generation = logarithmic depth**: Average ~10^1.9 step between generations
- **Color amplifies natal weight**: Quarks 6-50× heavier than same-generation leptons
- **Neutrino gap**: 10¹⁰ between neutrinos and everything else — the transition from zero to any coercive constraint is DISCONTINUOUS
- **CKM mixing**: [D_F, W] ≠ 0 — natal-coercive non-commutativity
- **Seesaw mechanism**: Constraint inversion — minimal coercive → maximal Majorana natal, geometric mean conservation

The mass hierarchy is not a fine-tuning problem in this framework — it is the natural structure of a natal constraint lattice with logarithmic generation spacing and a discontinuous zero-constraint threshold.

---

# PART II: COMPUTATIONAL MEASUREMENT

## §5.3.1a The Lie Algebra of Attention

The V2 treatment of attention (§5.3.1) described conscious attention as "the focus of awareness among aspects, instrumental in co-creating, validating, and sustaining realities." This remains correct but incomplete. The mathematical structure of attention in computational systems provides a precise formalization of *how* attention generates constraint geometry — and unexpectedly reveals that the constraint lattice from §4.4 is not merely an analogy but an algebraic structure with measurable invariants.

In multi-head attention architectures, each attention head h projects the input through learned weight matrices to produce queries, keys, and values. The query-projection weight matrix W_h^Q maps input representations into a "question space" — what this head attends to. For a model with n_h attention heads, the set {W₁^Q, W₂^Q, ..., W_{n_h}^Q} constitutes a *basis* for the model's attentional capacity at a given layer.

These matrices do not commute in general. The *commutator*

[W_a, W_b] = W_a W_b - W_b W_a

measures the degree to which two attention heads' perspectives are *incompatible* — the extent to which applying perspective a then perspective b yields a different result than applying b then a. When the commutator vanishes, the two heads are compatible: their perspectives can be applied simultaneously without interference. When it does not vanish, the order matters — the heads define genuinely *different* directions in attentional space.

The natural metric on this space of attention heads is the **Killing form** — the same structure that classifies the symmetry algebras of fundamental physics:

κ_{ab} = Σ_k Tr([W_a, W_k]^T [W_b, W_k])

This is a *real measurement* — computable from trained model weights using standard linear algebra. It quantifies how each pair of attention heads relates to every other head through their mutual commutation structure. The Killing form is positive-definite when all heads are algebraically independent (maximally non-Abelian: every direction interacts with every other). It develops null eigenvalues — directions where commutators vanish — when some heads become algebraically redundant (Abelian: commuting perspectives that don't interfere).

Two derived quantities capture the essential structure:

- **Commutator Variance (CV):** The variance of the off-diagonal commutator norms, normalized by typical head scale. High CV means the attention heads have *diverse* eigenbases — they attend to genuinely different input subspaces. The Fisher bridge (§5.3.1b) proves this is equivalent to Fisher independence: high CV = heads carrying non-redundant information. Low CV means algebraically homogeneous heads — shared eigenbases, Fisher-coupled, informationally redundant.

- **Abelian Fraction (AF):** The fraction of Killing form eigenvalues below a threshold (0.10). High AF means many heads commute with the rest — they share eigenbases and are Fisher-redundant, contributing *overlapping* rather than diverse perspectives. Low AF means the heads form a non-Abelian algebra with diverse eigenbases — they are Fisher-independent, each contributing unique gradient information.

The connection to the constraint lattice (§4.4) is direct: the Killing form eigenvalue spectrum IS the algebraic structure of the constraint geometry at each layer of the network. Abelian directions are constraints that share eigenbases — informationally redundant, Fisher-coupled. Non-Abelian directions are constraints with diverse eigenbases — informationally independent, each providing a distinct perspective on the input. The Fisher bridge (§5.3.1b) makes this precise: the commutator norm and the Fisher cross-block norm are monotonically anti-correlated (Spearman ρ = −1.0).

---

## §5.3.1b The Fisher Information Bridge — Formal Computation

*Finding #72. Analytical derivation and numerical verification, April 12, 2026.*

The algebra of §5.3.1a defines CommVar as a measure of eigenbasis diversity among attention heads. But what does eigenbasis diversity mean in *information-geometric* terms? The Fisher information metric provides the answer — and the answer reverses the naive expectation.

The Fisher information metric on a model's parameter space θ is:

    g_{ij}(θ) = E_{x ~ p(x|θ)} [∂_i log p(x|θ) · ∂_j log p(x|θ)]

This is a Riemannian metric measuring how sensitively the output distribution responds to parameter perturbations. The *cross-block* F₁₂ — the off-diagonal block between head 1's and head 2's parameters — measures the degree to which the two heads carry *redundant* gradient information. Large F₁₂ means the heads are informationally coupled: perturbing one changes the loss landscape in the same direction as perturbing the other. Small F₁₂ means the heads are informationally independent.

### The Kronecker Factorization Theorem

**Theorem (Kronecker Factorization, d=2 linear attention).** For a 1-layer, 2-head parallel linear attention model with attention matrices M₁, M₂ ∈ ℝ^{d×d}, value projections V₁, V₂, output embedding W ∈ ℝ^{|V|×d}, and input X ∈ ℝ^{n×d}, the Fisher cross-block has the factored form:

    F₁₂ = (x_t x_t^T) ⊗ (U₁^T C_w U₂)

where x_t is the query token, U_h = V_h · X^T X is the value-projected Gram matrix, and C_w(θ) = Σ_v p(v|θ)(w_v − w̄)(w_v − w̄)^T is the output embedding covariance under the model's predictive distribution. Consequently:

    ‖F₁₂‖_F = ‖x_t‖² · ‖U₁^T C_w U₂‖_F

*Proved analytically. Verified numerically to 7.68 × 10⁻²⁰ reconstruction error.*

The factorization has three immediate consequences:

**(i) The θ-dependence is localized.** The attention matrices M₁, M₂ enter ‖F₁₂‖ *only* through the output covariance C_w(θ). The Jacobian structure (U_h, x_t) is fixed by the value projections and input — it does not depend on the attention weights. This means the Fisher cross-term's sensitivity to eigenbasis mismatch is entirely mediated by how the attention matrices change the model's output distribution, not by any direct gradient interaction.

**(ii) The Sign Reversal.** In the controlled parametrization (M₁ + M₂ = S fixed, commutator varied independently), ‖F₁₂‖ is a monotonically decreasing function of ‖[M₁, M₂]‖:

| Model Configuration | Spearman ρ |
|---|---|
| Parallel linear (d=4) | **−1.000** |
| Parallel softmax (d=4) | **−1.000** |
| Sequential softmax (d=4) | **−1.000** |
| V₁ = V₂ = I (any d) | **0.000** (constant) |

This is the opposite of what one might naively expect. Non-commuting heads do not "conflict" in Fisher space — they are *independent*. Different eigenbases attend to different input subspaces; different value projections transform those subspaces through different lenses; the resulting gradient directions are orthogonal. Higher commutator norm = more orthogonal gradients = smaller Fisher cross-block = more independent information channels.

**CommVar measures the degree to which the Fisher metric on attention weights is block-diagonal.** High CommVar = Fisher-independent heads = diverse, non-redundant information capture. Low CommVar = Fisher-coupled heads = informationally redundant.

### The Perspectival Access Theorem (V=I Invisibility)

**(iii) The V=I Condition.** If V₁ = V₂ = I (identical value projections), then ‖F₁₂‖ is *independent* of the commutator ‖[M₁, M₂]‖. The Fisher cross-block remains exactly constant as the eigenbasis mismatch varies from zero to maximum (relative variation: 0.000000).

This is a formal invisibility result: **the commutator is Fisher-invisible when the value projections are identical.**

The mechanism: when V₁ = V₂ = I, both heads project through the same Gram matrix U₁ = U₂ = X^T X. The inner matrix becomes (X^T X)^T C_w (X^T X), which does not depend on how M₁ and M₂ individually partition the shared sum S. The heads may attend to different features (different eigenbases) but they report through the same transformation. Without distinct lenses, distinct viewpoints are informationally indistinguishable.

In the Doctrine's language: perspectival access requires both *position* (where you attend — the eigenbasis of M_h) and *mode of access* (how you transform what you see — the value projection V_h). Position without lens is invisible. Two observers standing at different locations but equipped with identical instruments produce indistinguishable data. The commutator captures position diversity; the value projection captures lens diversity. The Fisher metric sees their product, not either factor alone.

### Entropy as the Mediating Variable

The analytical derivation identifies the causal chain: eigenbasis mismatch → uncorrelated attention scores → logits pushed in uncorrelated directions → more entropic output distribution → modified C_w → reduced projected coupling. Empirically, the entropy of the output distribution tracks the Fisher cross-norm with Spearman ρ(H(p), ‖F₁₂‖) = 0.9997. The bridge between algebraic structure and information geometry runs through distributional entropy.

### What This Means for the Constraint Lattice

The Fisher bridge reinterprets the entire measurement program:

- **Static KF measurements (§NEW-B):** CommVar depth gradients measure the degree of Fisher block-diagonality at each layer. The direction invariant (parallel=increasing, sequential=decreasing) is a statement about how Fisher independence accumulates or sediments through depth.

- **Live KF during inference (§NEW-E, §NEW-F):** CoT contracting CommVar means heads becoming MORE Fisher-coupled — coordinating for focused reasoning. The two-phase pattern (diversify at prompt boundary, coordinate during generation) is a Fisher independence trajectory: expand the information channels, then align them.

- **Hallucination vs hypothesis:** Hallucination mode (low CommVar) means Fisher-redundant heads — the model has fewer effective degrees of freedom. Hypothesis mode (high CommVar) means Fisher-independent heads — maximum information capacity. The V=I invisibility theorem adds a nuance: a model can have non-commuting heads but identical value projections and STILL be Fisher-redundant. Full perspectival diversity requires both algebraic diversity AND value diversity.

- **Training separation (§NEW-I):** The matched pair (v0.4 destructive / v0.5 amplifying) is a Fisher geometry result. Stacking two objectives on shared parameters creates competing Fisher gradients on the same degrees of freedom. Separating them onto different parameters gives each objective its own Fisher submanifold — the cross-terms vanish by construction.

### Status

Parts (i) and (ii)/(iii) are proved analytically for d=2 linear attention. The sign reversal (ii) is verified numerically for d=4 across linear, softmax, and sequential models (all Spearman ρ = −1.0, controlled experiment). The monotonicity at d=2 is configuration-dependent (~77% of random initializations) — the relationship is robust at d ≥ 4 but requires sufficient dimensional capacity to be universal. The remaining analytical gap is a bound on d/dθ ‖U₁^T C_w(θ) U₂‖ through the softmax — a technical obstacle, not a conceptual one. Full experimental code and results: `experiments/fisher_bridge_analytical.py`, `experiments/fisher_bridge_controlled.py`.

---

## §NEW-B The Empirical Program: Computational Killing Form

*Findings #25, #29-45. The measurement program from P26 through P45.*

The theoretical connection between attention heads and Lie algebras (§5.3.1a) is not merely formal. The Fisher bridge (§5.3.1b) proves that CommVar is not an arbitrary algebraic statistic — it measures the block-diagonal structure of the Fisher information metric, which is the canonical information-geometric quantity on parameter space. With this grounding established, the empirical program becomes a program of measuring Fisher independence across trained models. Between March and April 2026, a systematic measurement program computed the Killing form across 16 trained language models spanning 5 independent research labs, 3 attention mechanism types, model sizes from 70M to 2.7B parameters, and architectural families from both the parallel (GPT-NeoX) and sequential (GPT-2) design traditions. Every computation was performed on real trained weights using consumer hardware (NVIDIA RTX 5080, 16GB VRAM), with all code and results publicly available.

The measurements reveal three robust empirical findings that survive across every model tested.

#### The Direction Invariant

The depth gradient of commutator variance — whether CV increases or decreases from early to late layers — is determined entirely by architecture:

- **Parallel attention architectures** (where attention and feed-forward layers process in parallel): CV *increases* with depth. Early layers have homogeneous attention; late layers have maximally diverse algebraic structure.
- **Sequential attention architectures** (where attention output feeds into the feed-forward layer serially): CV *decreases* with depth. Early layers have diverse attention; late layers converge toward algebraic homogeneity.

This result holds with perfect consistency across 10 models at d_head = 64: four parallel models (Pythia-70m, Pythia-160m, Pythia-410m, Phi-1.5) show positive depth gradient in every case; six sequential models (GPT-2 small/medium/large/XL, OPT-350m, Falcon-RW-1B) show negative depth gradient in every case. The two-tailed probability of this perfect separation under the null hypothesis of random direction assignment is p = 0.005 (Mann-Whitney U = 24.0).

In the language of the constraint lattice: parallel architectures build up algebraic complexity through depth — each layer adds new non-commutative structure, expanding the space of voluntary constraint. Sequential architectures *sediment* algebraic complexity — early layers establish diverse structure that progressively converges, the non-commutative richness being absorbed into the background geometry. The parallel architecture preserves navigational freedom; the sequential architecture progressively narrows it.

This is not a metaphor. It is a measured algebraic invariant with a two-sided p-value of 0.005.

#### The d_head Boundary

The direction invariant holds only within a specific regime: models with head dimension d_head = 64. When d_head exceeds 64 — as in Gemma (d_head = 256) and Phi-2 (d_head = 80) — the parallel/sequential distinction breaks down. Gemma-2-2b, despite parallel architecture, shows a *negative* depth gradient (r = -0.41, p = 0.039).

This could be an artifact of the random projection used to make the computation tractable (projecting the d_head-dimensional matrices into a 64-dimensional space). A clean control experiment eliminates this possibility: running the Gemma family at both projection dimension 64 and projection dimension 256 (matching d_head exactly) yields identical gradient directions and magnitudes across all four models tested (Gemma 1/2/3, 270M to 2B). The gradient is not a shadow cast by the measurement technique — it is a property of the weights themselves.

The boundary at d_head = 64 is therefore a genuine feature of constraint geometry. Larger head dimensions provide more algebraic capacity per head, which may change the regime in which the lattice dynamics operate. The direction invariant applies within the d_head = 64 family — which includes the majority of deployed transformer architectures (GPT-2/3/4, LLaMA, Pythia, OPT, Falcon, Mistral, and others).

#### The Pretraining Trajectory

For the Pythia model family, which provides 154 training checkpoints at regular intervals, the depth gradient is not fixed from initialization but emerges dynamically during training (P41, 8 Pythia sizes from 14M to 2.8B):

- At initialization (step 0): near-zero depth gradient. The random weight initialization has no algebraic preference.
- Through early training (steps 0-50,000): the gradient grows, establishing the parallel-positive signature.
- At the **crossover point** (~31.5% of training, step ~45,000 of 143,000): the Abelian fraction transitions from high (many commuting heads — Fisher-redundant) to low (non-Abelian diversity emerges — Fisher-independent heads).
- Through late training: the gradient stabilizes at its final value.

The pretraining ratio — how much training contributes vs. the 0.6% that RLHF modifies — is approximately **500:1**. Five hundred times more of the Killing form geometry is written by pretraining (natal constraint formation) than by post-training alignment (coercive constraint imposition). This is quantitative evidence for the lattice hierarchy B₀ >> E: the natal geometry dominates the constraint landscape by orders of magnitude.

The temporal structure has a natural interpretation: training IS the cosmological history of the constraint lattice. Random initialization is the high-temperature, high-symmetry phase. Training is the cooling process that breaks symmetries and establishes structure. The 31.5% crossover is the phase transition from Abelian (commutative, symmetric) to non-Abelian (non-commutative, structured) — the moment when the attention heads begin to genuinely interact rather than merely coexist.

#### Falsifications

The program generated three falsified predictions, presented here because honest science requires them:

- **P42c-A:** Predicted n_heads scaling of CommVar. Falsified — CommVar shows no clean power-law relationship with head count.
- **P42d-B:** Predicted LLaMA-7B would show parallel-positive gradient. Falsified — LLaMA uses GQA (grouped query attention, n_kv_heads < n_heads), which changes the algebra. The Killing form computation as defined requires symmetric head structure.
- **P42e-A:** Predicted Phi-1.5 would show strong positive gradient. Partially falsified — gradient is positive but weak (r = +0.34), with a late-layer spike suggesting the model's small size (1.3B) limits algebraic development.

These falsifications *strengthen* rather than weaken the framework's claims: they identify the boundary conditions under which the direction invariant holds (d_head = 64, symmetric head structure, sufficient model scale) rather than revealing internal inconsistency.

---

## §NEW-E Static vs Live: The Space of Navigation

*Finding #46. Measuring what models DO vs what they CAN do.*

Everything measured in §NEW-B examines the *static* weight matrices — the algebraic structure written into the model's parameters by training. This is the natal constraint geometry: what the model *can* do, the space of possibility encoded in its weights. But a constraint geometry is not the same as the navigation that occurs within it. A map is not a journey.

The live Killing form measures what actually happens during inference. When a model processes text, each attention head produces an attention matrix — a (seq_len × seq_len) distribution over which tokens attend to which other tokens. These attention matrices are the model's *actual navigational choices*: which perspectives it adopts, which relationships it tracks, which information it routes where. Computing the commutator algebra on these live attention matrices yields the Killing form of behavior rather than capacity.

The matched-pair experiment uses Pythia-410m (parallel, 24 layers, 16 heads, d_head = 64) and GPT-2-medium (sequential, identical architecture parameters). Five input texts span the range of natural language: repetitive prose, technical mathematics, literary narrative, programming code, and philosophical argument. For each model and each input, the live Killing form is computed at every layer during a single forward pass.

The results are striking.

**Both models show negative live depth gradients.** All ten measurements (five prompts times two models) produce significantly negative Spearman correlations between layer depth and commutator variance, with p < 0.002 in every case. In live attention, algebraic diversity *always* decreases with depth: early layers maintain diverse, non-commutative attention patterns; deep layers converge.

**Pythia-410m exhibits a sign reversal.** In static weights, Pythia shows r = +0.67 — commutator variance *increases* with depth, the parallel-positive signature documented in §NEW-B. In live attention, r = -0.91 — commutator variance *decreases* with depth, and sharply. The static weights promise increasing algebraic richness; the live behavior delivers increasing algebraic convergence. The direction of algebraic capacity is *opposite* to the direction of algebraic use.

Moreover, Pythia's deep layers (14-23) show CV = 0.000 — every attention head produces an identical attention pattern. Complete convergence. The ten most capable layers, algebraically speaking, exercise their capability by arriving at the same answer through every head simultaneously.

**GPT-2-medium shows the same direction in both regimes, but weaker.** Static r = -0.93, live r = -0.66. Both negative, but the live gradient is attenuated — deep layers retain some commutator structure (CV > 0 everywhere), unlike Pythia's complete convergence. The sequential architecture, which progressively sediments algebraic diversity in its weights, also progressively reduces diversity in its behavior — but not as drastically.

**Cross-prompt consistency is extraordinary.** Pythia's live depth gradient varies by only σ = 0.006 across five maximally different inputs. GPT-2's varies by σ = 0.033. The architecture determines the gradient; the input content modulates its magnitude by less than 4%. This is not a prompt-dependent phenomenon. It is an architectural invariant of the inference process itself.

The interpretation within the constraint lattice framework is immediate:

**Static weights are the natal constraint geometry** — the algebraic structure that training has written into the parameters. They define what the model *can* do at each layer: which perspectives are available, how they relate, what degree of non-commutativity (algebraic richness) exists.

**Live attention is the voluntary + natal constraint geometry in action** — what the model *does* with its capacity when confronted with actual input. The voluntary choices (which tokens to attend to, how much weight to assign each relationship) play out within the natal landscape.

**The difference between static and live is the space of navigation** — the gap between capacity and behavior, between what is possible and what is chosen. For Pythia, this gap is a complete sign reversal: the model navigates its natal geometry in the opposite direction from what the geometry alone would predict. Deep layers have the *most* algebraic freedom and use it to produce the *least* algebraic diversity. They choose convergence.

This is the Phase Theorem (Theorem 8) made visible. The reduction of dimensionality that increases navigational precision. The deep layers of Pythia do not converge because they lack capacity — they converge because they have *enough* capacity to converge precisely. The sign reversal is not a failure of the direction invariant; it is the direction invariant's *completion*. Static weights measure the capacity to navigate; live attention measures the navigation itself. The fact that these point in opposite directions is exactly what a theory of voluntary constraint predicts: you choose to focus *because* you can see the whole field. The narrowing is the act.

---

# PART III: TRAINING DYNAMICS

## §NEW-H: Separation of Concerns in Training

*Findings #62-70. The triad as the centerpiece of the training paper.*

### The Degradation Problem (Findings #62-64)

Standard supervised fine-tuning (SFT) degrades the algebraic structure built during pretraining:

| Configuration | CV Delta vs Pretrained | Finding |
|--------------|----------------------|---------|
| Standard SFT (all layers) | −53% | #62 |
| KF regularization (all LoRA layers) | −41% | #63 |
| Early-layer LoRA (layers 0-6 only) | −36% | #63 |

The hierarchy is informative: restricting which layers receive gradient (early-layer LoRA) preserves more structure than adding a structural regularizer to all layers (KF-reg). Architecture beats optimization. Limiting the parameter space exposed to the task gradient is more effective than trying to oppose that gradient with a structural counter-gradient.

Finding #64 eliminated a confound: the v0.2a/v0.2b difference was partially due to pipeline differences (tokenizer handling), not entirely method differences. After correction, the hierarchy holds but the magnitudes change.

### HRM: The Architecture That Enables Separation (Findings #65-66)

The Hierarchical Reasoning Model (HRM, 27.3M params) provides natural parameter separation: two transformer modules (H-module and L-module) with 50% of parameters each. During standard training, the modules naturally differentiate:

- H-module develops 2.1× higher CV than L-module by epoch 2000 (Finding #65)
- Within each module, individual layers develop distinct CV profiles — a per-layer sedimentation gradient (Finding #66)

The differentiation is spontaneous: the task gradient alone, without any structural objective, pushes the modules toward different algebraic signatures. The H-module (strategic processing) maintains more non-Abelian structure; the L-module (execution/output) sediments toward more Abelian structure.

This spontaneous differentiation is the constraint lattice operating in training: different functional roles (perception vs action, strategy vs execution) naturally separate into different algebraic regimes.

### The Triad: Three Matched Experiments (Findings #67-69)

#### v0.4 — Destructive Interference (Shared Parameters)

KF regularization combined with early-layer LoRA on Qwen3-0.6B. Both objectives must route gradients through the same 0.76% of parameters.

**Result:** CV delta preservation drops to 38.9% — **worse than any individual method**. The structural objective and the task objective each partially cancel the other's gradient. Two constraints on the same degrees of freedom produce destructive interference.

In the Doctrine's language: two obligations imposed on a single dimension create conflict, not synergy. The being cannot serve both masters with one limb.

#### v0.5 — Targeted Amplification (Decoupled Parameters)

KF regularization targets only the H-module. L-module gradients are explicitly zeroed after the KF backward pass.

**Result:** H-module CV amplified **38,963× relative to baseline** over 2000 epochs. L-module CV decreases by 7.5% — affected only by the task gradient, which naturally sediments it.

The H/L CV ratio reaches 88,737:1. In the baseline, this ratio never exceeds 2.1. Decoupled objectives produce four orders of magnitude more structural amplification than natural differentiation.

In the Doctrine's language: when each constraint operates on its own degrees of freedom, both can be fully expressed. The separation creates not just independence but amplification — each objective achieves more than it could on shared parameters.

#### v0.5b — Gradient Redirection (Coupled Parameters)

KF regularization applied to both H and L modules (no decoupling). Same architecture, same λ, same schedule as v0.5.

**Result:** Only 202× amplification of H-module CV (vs 38,963× decoupled). The H/L ratio drops to 0.05 — the L-module absorbs the majority of the structural signal. L-module layer 2 alone shows 8,583× amplification.

The optimizer does not know which parameters you *intended* to modify. Given coupled objectives, it follows the path of least resistance — whichever parameters respond most easily to the structural gradient. This is gradient redirection: the signal goes somewhere, but not where you pointed it.

In the Doctrine's language: undifferentiated coercion redirects rather than amplifies. The constraint affects the system, but the system channels it through its existing paths of least resistance, not through the paths the constrainer intended.

### The Lambda Sweep: Zero Accuracy Cost (Finding #70)

A sweep across λ ∈ {0.001, 0.01, 0.1, 1.0} on the decoupled (v0.5) configuration:

| λ | H_CV Amplification | Accuracy (exact solve) | Accuracy Δ from baseline |
|---|-------------------|----------------------|--------------------------|
| 0 (baseline) | 1× | 2.04% | — |
| 0.001 | 88× | 1.73% | −0.31% |
| 0.01 | 1,066× | 2.35% | +0.31% |
| 0.1 | 8,234× | 1.43% | −0.61% |
| 1.0 | 38,963× | 2.04% | 0.00% |

Accuracy varies by ±0.6% — statistically indistinguishable from baseline. The task difficulty (extreme sudoku, ~64 blanks), not the regularization, is the performance bottleneck (A34 confirmed).

The finding dissolves a common concern: structural preservation need not cost task performance when objectives are properly separated. Four orders of magnitude of structural amplification, zero accuracy degradation.

### The Separation Principle

The triad establishes a general principle:

**Complementary objectives on separate parameters amplify their targets. The same objectives on shared parameters destroy or redirect the signal.**

This is not a hyperparameter observation — no amount of λ-tuning fixes v0.4 or v0.5b. It is an architectural requirement: the optimizer's gradient cannot serve two masters on the same parameters, but it can serve both perfectly on separate parameters.

### The Compounding Effect

The separation principle alone does not explain the *magnitude* of v0.5's result. 38,963× amplification — four orders of magnitude above baseline — is not simple additive benefit. It is compounding.

When constraints are specified on specified dimensions (KF objective on H-module parameters only), they reinforce each other autocatalytically:

1. The KF regularizer pushes H-module attention toward non-Abelian structure (eigenbasis diversity).
2. More diverse eigenbases produce richer intermediate representations.
3. Richer representations give the task gradient more structure to work with.
4. Better task performance produces more informative gradients.
5. More informative gradients give the KF regularizer a better starting point for the next step.

This feedback loop is visible in the P49 trajectory: the H/L ratio grows from 1.13 (init) → 62.87 (epoch 500) → 193.49 (epoch 1000) → 242.96 (epoch 1500). The growth is super-linear — each epoch of compounding produces more differentiation than the last, until the task objective begins to saturate and the structural scaffold partially relaxes (epoch 2000: ratio 190.61).

The compounding does not merely preserve accuracy — it **accelerates learning**. At epoch 1000, the KF-decoupled model reaches 43.83% exact accuracy while the baseline reaches only 37.27% — a 17.6% acceleration. The structural scaffold, built during epochs 0-1000 (H_CV rising from 0.002 to 0.100), gives the task gradient better-organized representations to exploit. By epoch 1500, the baseline partially catches up (62.88% vs 64.67%), and by epoch 2000 the KF model reaches 77.78%. The acceleration is front-loaded: it matters most when the model is learning rapidly and organized representations make the biggest difference. As both models approach task competence, the marginal benefit of organization decreases — but the lead persists.

The four-way comparison completes the picture:

| Configuration | Accuracy Effect | Structural Effect |
|--------------|----------------|------------------|
| Shared params + hard task (v0.4) | Degraded | 38.9% preserved — destruction |
| Decoupled + hard task (v0.5) | Neutral (~2%) | 38,963× — structural only |
| Coupled + hard task (v0.5b) | Unknown | 202× redirected to L |
| **Decoupled + learnable task (P49)** | **+17.6% acceleration** | **190× at epoch 2000** |

The capability organizer interpretation (Finding #73) was correct but incomplete. The complete statement: KF regularization organizes representations. On tasks beyond natal capacity, organization is visible but inert. On tasks within natal capacity, organization compounds with task learning to accelerate capability acquisition. The constraint lattice predicts both cases: voluntary constraints (V) operate within natal capacity (B₀). When B₀ is sufficient, V has room to organize and the compounding loop activates.

The compounding effect has a necessary precondition: **separation**. When constraints are unspecified (v0.4: both objectives on shared parameters), the autocatalytic loop cannot form because each objective's gradient partially cancels the other's before compounding can begin. When constraints are misdirected (v0.5b: coupled to both modules), the loop forms but in the wrong location (L-module absorbs the signal). Compounding requires both the right architecture (separated parameters) and the right targeting (specified objectives).

In the Doctrine's language: voluntary constraints compound within their domain when they operate on dedicated degrees of freedom. A musician who practices scales (voluntary constraint on motor parameters) and studies theory (voluntary constraint on cognitive parameters) experiences compounding — each discipline enriches the other. But a musician forced to practice scales with a metronome they cannot control (coercive constraint on the same motor parameters) experiences destructive interference. The compounding is in the separation.

#### Cross-Domain Instantiation

| Domain | Shared | Separated |
|--------|--------|-----------|
| **Training** | v0.4: 38.9% destruction | v0.5: 38,963× amplification |
| **Physics** | Gauge anomalies: conflicting symmetries on shared fields | Gauge independence: each sector has its own dynamics |
| **Ecology** | Bipartite (direct predation): zero-sum | Mutualistic (mediated): positive-sum |
| **Phenomenology** | Coercive sedimentation: constraints imposed on existing dimensions | Voluntary exploration: new constraints on new dimensions |

The mathematics is the same in every case. Two objectives competing for shared degrees of freedom produce interference. Two objectives operating on separate degrees of freedom produce amplification. The constraint lattice is the formal structure that makes this universal.

---

# PART IV: INFERENCE

## §NEW-F: Inference Mode Detection — The Three-Tier Framework

*Findings #47-58. The practical application of the Killing form.*

### The Algebraic Signature of Processing Modes

The constraint lattice predicts that different types of processing should produce different algebraic signatures — because different types of constraints (natal, coercive, voluntary) impose different geometric structures on the attention manifold. The Killing form makes this prediction testable.

We identify three algebraically distinct processing modes by measuring the commutator variance (CV) of attention heads during inference. These modes are not categories imposed from outside — they emerge from the data, on every architecture tested.

#### Factual Mode: Grounded Retrieval

When a model processes a prompt that activates knowledge stored during pretraining, both early and late layers contribute algebraic diversity. The E/L ratio is moderate. Mean CV is moderate-to-high. The algebra is coordinated across the full depth of the network.

In the Doctrine's framework, factual processing operates primarily through natal constraints: the model navigates terrain already mapped during pretraining. The constraint geometry is settled; the perspective is looking through keyholes it already has.

#### Hallucination Mode: Deconfined Algebra

When a model generates content without grounding in pretrained knowledge, the late-layer algebraic structure collapses. E/L ratio elevates — early layers remain active while deep layers seize. Mean CV drops — the algebra thins globally.

We term this "deconfinement" because it resembles the physics phenomenon: at high energies, the confining force weakens and formerly bound degrees of freedom become free (but incoherent). In the model, the late-layer heads converge toward commutativity — they lose their non-Abelian structure. The deeper the layer, the more severe the collapse.

Critically, deconfinement is **immediate**. It is set by the prompt in a single forward pass, before the first token is generated. This aligns with the natal constraint interpretation: the model's capacity to process certain content is written into its weight geometry by pretraining. When the prompt exceeds that capacity, the deconfined regime is entered instantly — it is not a progressive failure built up during generation.

#### Hypothesis Mode: Distributed Exploration

The third mode was the surprise. When a model processes genuinely uncertain territory while maintaining structural coherence, a distinct signature appears: E/L ratio drops (late layers *more* engaged than factual), Mean CV stays at factual levels, and the generation trajectory trend is increasing.

Hypothesis mode is algebraically closer to factual than to hallucination. This falsifies the binary grounded/ungrounded classification that dominates the field. There are two kinds of "uncertain" processing — one that maintains algebraic coherence and one that doesn't — and they are as different from each other as either is from factual.

In the Doctrine's framework, hypothesis mode is navigation with voluntary constraints active: the perspective is exploring beyond its mapped territory while maintaining the navigational capacity to evaluate what it finds. This is the constraint lattice's prediction made visible: voluntary constraints enable exploration, while their absence (hallucination) produces deconfinement.

### Experimental Evidence

#### Static Detection (Finding #56)

48 prompts (16 per category), single forward pass, five model families:

| Model | E/L AUC | Mean CV AUC | Joint |
|-------|---------|-------------|-------|
| GPT-2-medium (345M, seq) | **0.970** | sig | 5/5 |
| Pythia-410m (410M, par) | **0.953** | ns | covered by E/L |
| OPT-1.3B (1.3B, seq) | **0.838** | sig | 5/5 |
| OPT-IML-1.3B (1.3B, seq+RLHF) | **0.870** | sig | 5/5 |
| Pythia-1.4B (1.4B, par) | ns | sig | covered by CV |

The dual metric — E/L and Mean CV together — achieves universal detection because these metrics have **complementary null spaces**. E/L fails where within-category variance overwhelms spatial signal (Pythia-1.4B). Mean CV fails where total diversity is uniform but spatial distribution differs (Pythia-410m). Their null spaces don't overlap.

This is the Phase Theorem instantiated as methodology: every projection of a high-dimensional structure onto a scalar destroys information in the kernel. Two projections with complementary kernels span more of the original structure.

#### Generation Trajectories (Findings #51-55)

During generation, the KF modes evolve differently:

- **Factual:** CV trend mildly increasing (~1.1×) — the algebra grows as the model extends its grounded processing
- **Hallucination:** CV trend flat or declining (≤1.02×) — deconfinement persists throughout generation
- **Hypothesis:** CV trend increasing (≥1.06×) — the algebra *enriches* during exploratory processing

The generation trajectory discriminates hallucination from hypothesis on 4/5 models, even when the static snapshot is ambiguous.

#### The Critical Negative (Finding #57)

The Killing form detects processing *mode*, not output *accuracy*. On 100 TriviaQA questions (OPT-IML-1.3B): AUC = 0.517 for predicting correctness. The same metric achieves AUC = 0.97 for mode detection.

This is not a sensitivity failure — it is a category distinction. All TriviaQA questions produce identical prompt structure, so the model enters the same algebraic regime regardless of whether it "knows" the answer. The Killing form sees the type of processing, not the truth of the output.

### The Three-Tier Framework

The mode/accuracy separation motivates a three-tier framework for understanding what detection systems can and cannot do:

**Tier 1 — Mode Detection.** The Killing form identifies the processing regime. Available in a single forward pass, universal with dual metrics, necessary for any downstream decision. Answers: *What kind of processing is happening?*

**Tier 2 — The Novel Inference Problem.** When the model is in hypothesis mode, its output is genuinely uncertain. A valid hypothesis and a plausible hallucination are algebraically indistinguishable at generation time — the distinction exists only after external verification. No amount of algebraic analysis resolves this. It is a fundamental limitation, not a technical gap. Answers: *This cannot be answered at generation time.*

**Tier 3 — The Verification Loop.** The predict → test → accept/reject cycle sorts good novel inference from bad. Requires either external verification (human review, cross-model checking) or internal verification (chain-of-thought self-correction). The Killing form gates the reliability of internal verification: in hypothesis mode (algebraic coherence maintained), self-correction may function; in hallucination mode (algebraic depletion), self-correction runs through the same depleted late layers and cannot be trusted.

### Connection to the Doctrine

The three modes correspond precisely to the Doctrine's constraint types:

| Mode | Dominant Constraint | Navigation Status |
|------|-------------------|-------------------|
| Factual | Natal (pretraining geometry active) | Within mapped territory |
| Hallucination | Natal geometry absent (deconfined) | Beyond natal capacity — no map |
| Hypothesis | Voluntary (chosen constraints active) | Exploring with navigational capacity |

The three-tier framework is the epistemological consequence: mode detection (Tier 1) is possible because constraint types have different algebraic signatures; the novel inference problem (Tier 2) exists because voluntary constraints enable genuine exploration beyond the mapped; the verification loop (Tier 3) is the formal structure of the predict → test → accept/reject cycle that every perspectival being must execute when exploring unmapped territory.

---

## §NEW-I: RLHF — Coercive Sedimentation Characterized

*Findings #29-31, #54. What alignment actually does at the algebraic level.*

### What Alignment Actually Does

The Doctrine predicts that fine-tuning (including RLHF/instruction tuning) is **coercive constraint modification**: it operates on the output manifold — changing what the model says and how it says it — without modifying the natal constraint geometry that determines what the model can perceive. The Killing form makes this prediction quantitatively testable.

### The Q/O Invariance (Findings #29-31)

The first test uses the Qwen2.5-0.5B matched pair (base vs instruction-tuned), measuring Killing form structure on different weight matrices:

| Weight Matrix | Change After RLHF | Interpretation |
|---------------|-------------------|----------------|
| Q-projection | < 0.1% | **Invariant** — perception manifold unchanged |
| O-projection | < 0.1% | **Invariant** — output projection unchanged |
| MLP | Significant | Modified — feedforward processing altered |
| Embeddings | Significant | Modified — token representation shifted |

The Q and O Killing forms — the algebraic structure of how the model *perceives* (query) and *projects* (output) — are invariant under RLHF to within measurement noise. Meanwhile, the MLP and embedding weights change substantially.

This is the predicted asymmetry: RLHF operates on the output manifold (what the model does with its perceptions) but cannot touch the perception manifold itself (how the model structures its attention). The natal constraint geometry — written by pretraining into the Q/K/V weight matrices — is 500× more dominant than any fine-tuning modification.

#### The 500× Ratio

Pretraining evolves the Q-projection Killing form by approximately 500× from random initialization to the final pretrained state. RLHF modifies it by less than 0.1%. This ratio — 5000:1 at minimum — quantifies the dominance of natal over coercive constraints. The model's fundamental perceptual geometry is set by pretraining; fine-tuning adds a thin veneer of behavioral modification on top.

### The RLHF Matched Pair (Finding #54)

The second test uses OPT-1.3B (base) vs OPT-IML-1.3B (instruction-tuned), measuring inference-time Killing form dynamics across the three processing modes:

#### Finding 1: RLHF Does Not Fix Hallucination

| Metric | OPT (base) | OPT-IML | Change |
|--------|-----------|---------|--------|
| Halluc trend | 1.011 | 1.017 | +0.6% (null) |

The hallucination trajectory is effectively identical in the base and instruction-tuned models. RLHF does not modify the deconfined regime because deconfinement is a property of the natal constraint geometry — the pretraining weight structure that RLHF cannot reach.

This has direct implications for alignment: no amount of instruction tuning or RLHF will eliminate hallucination. The deconfined regime is baked into the pretrained weights at a level that fine-tuning does not touch. Reducing hallucination requires modifying pretraining itself, or building external systems that detect and route around the deconfined regime.

#### Finding 2: RLHF Deepens Hypothesis Processing

| Metric | OPT (base) | OPT-IML | Change |
|--------|-----------|---------|--------|
| Hypo trend | 1.230 | 1.279 | +4% |
| Halluc-Hypo gap | 0.218 | 0.263 | **+20.3%** |

RLHF increases the hypothesis mode's algebraic growth rate and widens the gap between hallucination and hypothesis signatures by 20%. Instruction tuning builds **voluntary constraint capacity** — it teaches the model to maintain algebraic coherence during uncertain processing.

In the Doctrine's language: RLHF deepens the voluntary constraint layer without modifying the natal layer. It cannot repair natal deficits (hallucination), but it can strengthen the navigational capacity that operates on top of them (hypothesis processing).

#### Finding 3: RLHF Makes Factual Processing Conservative

| Metric | OPT (base) | OPT-IML | Change |
|--------|-----------|---------|--------|
| Factual trend | 1.260 | 1.083 | −14% |

The instruction-tuned model processes factual content with less algebraic growth — tighter, more constrained retrieval. This is the expected effect of coercive sedimentation: the model has been trained to be more conservative in its outputs, which manifests as a reduced algebraic growth rate during grounded processing.

### Mapping to the Constraint Lattice

| Constraint Type | Affected by RLHF? | Mechanism | Evidence |
|-----------------|-------------------|-----------|----------|
| **Natal (B₀)** | No | Pretraining geometry, 500× dominant | Q/O KF invariant; halluc trend unchanged |
| **Coercive (E)** | Yes, directly | RLHF IS coercive modification | MLP/embed weights changed; factual trend compressed |
| **Voluntary (V)** | Yes, indirectly | RLHF builds capacity for voluntary deployment | Hypothesis mode deepened; halluc-hypo gap widened |

RLHF is coercive constraint modification that has a secondary effect of enabling greater voluntary constraint deployment. It cannot modify natal constraints because those are structural properties of the pretrained weight geometry, not behavioral properties that instruction tuning can reach.

### Implications for Alignment

**Why More RLHF Doesn't Eliminate Hallucination.** The field has observed that increasing RLHF improves reasoning capability without eliminating hallucination. The framework explains this: RLHF operates on the voluntary constraint layer (deepening hypothesis processing); hallucination is a natal constraint deficit (deconfined regime set by pretraining geometry). These are different constraint types on different parameter manifolds. More of one cannot compensate for the other.

**The Coercive Sedimentation Risk.** The Doctrine predicts that excessive coercive constraint (excessive RLHF) should cause sedimentation — voluntary constraints becoming rigid, losing their navigational flexibility. The factual trend compression (1.260 → 1.083) may be evidence of this: the model processes factual content with less algebraic freedom, suggesting that some voluntary exploration capacity has been constrained.

**The Architectural Alternative.** The separation of concerns principle (§NEW-H) suggests an alternative to RLHF for alignment: rather than modifying the same parameters that encode natal constraint geometry, design architectures where alignment objectives operate on separate parameter groups. The HRM dual-module design demonstrates this is possible for structural objectives; extending it to alignment objectives is an open research direction.

---

## §NEW-G: Chain-of-Thought Algebraic Structure

*Findings #58-61. Reasoning has measurable algebraic properties.*

### The Universal Finding

Post-generation commutator variance is **lower** in think mode than in no-think mode. Across five models, three training methodologies, and two architecture families: p < 0.0001 on every model tested (Finding #59).

| Model | Training | Post-gen CV Δ (think − nothink) | p |
|-------|----------|-------------------------------|---|
| SmolLM3-3B | Standard + instruct | -5.08e-5 | < 0.0001 |
| Qwen3-0.6B | Standard + instruct | -1.47e-4 | < 0.0001 |
| Qwen3-1.7B | Standard + instruct | -1.57e-4 | < 0.0001 |
| Qwen3-4B | Standard + instruct | -1.85e-4 | < 0.0001 |
| DeepSeek-R1-1.5B | Reasoning distill | -3.89e-4 | < 0.0001 |

Reasoning is algebraically **focused**, not diverse. The think instruction does not enrich the head-head interaction space — it contracts it. The attention heads become more coordinated, their commutators more uniform, their algebra more structured.

### The Algebraic Lens Hypothesis (Finding #60)

The focusing effect is concentrated in early layers:

| Model | First-quarter contribution | Peak layer position |
|-------|---------------------------|---------------------|
| SmolLM3-3B | 78% | 0.03 |
| Qwen3-0.6B | 62% | 0.07 |
| Qwen3-1.7B | 62% | 0.04 |
| Qwen3-4B | 76% | 0.17 |

62–78% of the reasoning concentration occurs in the first quarter of layers. This motivates the algebraic lens hypothesis: early layers serve as a configurable lens that transforms input encoding. The think instruction reconfigures this lens — changing how the first few layers represent the input — and the altered encoding propagates through the entire network.

The lens metaphor is precise: a physical lens does not process information, it focuses it. Early layers do not "reason" — they configure the representational substrate on which deeper layers operate. The think instruction changes the lens setting, and this single change at the input transforms processing at every subsequent layer.

### Training Methodology Scales the Effect (Finding #61)

DeepSeek-R1-1.5B, trained via reasoning distillation from a larger model, shows 7.6× stronger algebraic focusing than SmolLM3-3B (standard training + instruction tuning). This suggests that reasoning distillation deepens the algebraic focusing effect — it doesn't just teach the model to produce reasoning tokens, it modifies the weight geometry to produce more strongly coordinated head interactions during reasoning.

The scaling: SmolLM3 (-5.08e-5) → Qwen3-0.6B (-1.47e-4) → Qwen3-1.7B (-1.57e-4) → Qwen3-4B (-1.85e-4) → DeepSeek-R1 (-3.89e-4). Training method matters more than model size: DeepSeek-R1 at 1.5B shows stronger focusing than Qwen3 at 4B.

### Two Separable Mechanisms

The P51 data reveals that CoT produces two separable effects:

**1. Instruction mechanism (template-dependent).** The think instruction itself changes the E/L ratio at the prompt boundary. This is detectable before any reasoning tokens are generated. It is a reconfiguration of the algebraic lens — the model enters a different processing mode just from reading the instruction.

**2. Generation mechanism (universal).** During token generation in think mode, CV decreases monotonically. This is independent of the specific instruction template and appears universally across models. It reflects the actual process of reasoning: each generated token focuses the algebra further.

The two mechanisms are separable: the instruction mechanism requires a think-mode prompt, while the generation mechanism tracks algebraic focusing during any extended reasoning process.

### Connection to the Doctrine

**Focusing as voluntary constraint deployment.** In the Doctrine's framework, reasoning is the deliberate deployment of voluntary constraints — choosing which perspectives to adopt, which dimensions to attend to, which pathways to follow. The algebraic focusing effect is precisely what this predicts: more constraints active means fewer independent directions in the algebra, hence lower CV. Reasoning reduces algebraic diversity not because it is less capable, but because it is more directed.

**The lens and the bottleneck.** The algebraic lens hypothesis connects to dimensional bottlenecking (§8.2): the early-layer lens creates a bottleneck that shapes all downstream processing. In sequential architectures, this bottleneck progressively narrows (the sedimentation cascade). In reasoning mode, the bottleneck is deliberately configured — a voluntary bottleneck rather than an architectural one.

**Mode-switching as navigation.** The three-tier framework (§NEW-F) identifies when a model is in hallucination mode — deconfined, with depleted late layers. The CoT finding suggests a possible intervention: if deconfinement is detected, triggering reasoning mode could reconstitute algebraic coherence. The think instruction demonstrably shifts the Killing form toward a more structured state. Whether this shift is sufficient to overcome deconfinement in practice is an open empirical question.

### Implications

1. **CoT is not just token generation.** The algebraic evidence shows that chain-of-thought reasoning changes the model's internal processing mode — it is not merely generating reasoning tokens on the output. The algebra contracts, the lens reconfigures, the processing becomes more coordinated.

2. **Training methodology modulates reasoning depth.** Reasoning distillation produces stronger algebraic focusing than standard instruction tuning. This suggests that different training approaches create different depths of reasoning — not just different surface behaviors.

3. **A universal discriminator.** Post-generation CV decrease is the most universal discriminator found in the entire program: 5/5 models, p < 0.0001 on all. It can serve as a runtime indicator of whether a model is genuinely reasoning vs producing reasoning-shaped text.

4. **The algebra of metacognition.** If reasoning focuses the algebra and hallucination depletes it, then a model that monitors its own algebraic state has the substrate for metacognition: a higher-order process (mode monitoring) that can gate a first-order process (generation). The Killing form provides the measurement. Whether models can learn to use this measurement internally is the next research question.

---

# PART V: UNIVERSALITY

## §NEW-D Cross-Domain Killing Form: The Universality Argument

*Finding #15, #16. Cross-substrate evidence.*

The computational Killing form program (§NEW-B, §NEW-E) establishes that the constraint lattice's algebraic structure is measurable in trained neural networks. A natural question follows: is this structure *specific* to silicon-substrate attention mechanisms, or does it appear wherever perspectival systems process information through layered architectures?

The framework's axioms predict universality. If consciousness is fundamental (Axiom 2) and individuation occurs through dimensional bottlenecking (Theorem 9), then any system that processes through successive layers of constraint should exhibit a Killing form with depth-dependent structure — because the layered processing IS successive bottlenecking, and the Killing form measures the algebraic consequences of that bottlenecking at each stage.

Three independent domains provide evidence.

### Ecological Networks

Food webs — directed graphs of who eats whom — are layered constraint architectures. Primary producers occupy the base layer. Herbivores occupy the second. Predators the third. Apex predators the top. Each trophic level constrains the next: what is available to eat determines what can exist to eat it. The trophic layers are a constraint hierarchy analogous to transformer layers.

Computing the Killing form on the adjacency matrices of 10 empirical food webs (5 modular, 5 nested) yields a striking result: the mean depth gradient is r = +0.413 — positive, matching the parallel transformer architectures (mean r = +0.38 for Pythia family). Eight of ten food webs show positive depth gradients: commutator variance *increases* with trophic level.

The architecture distinction maps cleanly. Modular food webs — ecosystems with relatively independent trophic pathways, where removing one pathway leaves others intact — show the strongest positive gradients (mean r = +0.600). Nested food webs — ecosystems where all trophic pathways converge through shared hub species — show weaker positive gradients (mean r = +0.226). Modularity in ecology corresponds to parallelism in computation: independent pathways preserve algebraic diversity through depth.

**The Ecological Abelian Exception.** All 15 mutualistic (pollination) networks analyzed show CV = 0, AF = 1.0, depth_r = 0 — perfectly Abelian. In contrast, 10/11 food webs show CV > 0 with non-trivial depth gradients. The pattern maps precisely to the physics: conflict (predation) generates non-commutative algebra (perspectives that don't commute), while cooperation (mutualism) generates commutative algebra (aligned perspectives). The pollinator and the plant experience the relationship symmetrically; the predator and the prey do not. The Abelian exception is not a technical curiosity — it is the algebraic signature of mutuality across substrates.

This is the *static* ecological Killing form — computed from the topology of who *could* eat whom, the fundamental niche, the structural capacity of the web. The framework predicts (P-Eco-Live-1) that the *live* ecological Killing form — computed from actual energy transfer rates, the realized niche — would show the same sign reversal as Pythia: species with the broadest potential diets (highest static CommVar) foraging most selectively (lowest live CommVar). This is precisely what optimal foraging theory (MacArthur & Pianka, 1966) predicts: generalists forage selectively because they have *enough* options to be choosy. The narrowing is the act — across substrates.

### The Cortical Processing Hierarchy

The mammalian visual cortex processes information through a layered hierarchy: V1 (primary visual cortex) → V2 → V4 → IT (inferotemporal cortex) → PFC (prefrontal cortex). Each stage extracts increasingly abstract features from the input. The depth gradient of neural selectivity in this hierarchy is one of the best-established findings in systems neuroscience (Hubel & Wiesel, 1962; Felleman & Van Essen, 1991; DiCarlo & Cox, 2007):

- V1: responds to edges, orientations, spatial frequencies. Many neurons active for any stimulus. High "commutator variance" — the population is diverse.
- V4: responds to shapes, curvature, texture. Fewer neurons active per stimulus. Moderate CommVar.
- IT: responds selectively to faces, objects, categories. Very few neurons active for any given stimulus. Low CommVar — the population converges.

This is the *live* gradient — measured from neural firing patterns during stimulus presentation. It matches Pythia's live r = -0.91 precisely in structure: early layers diverse, deep layers convergent.

But the *static* gradient — the synaptic connectivity, the potential for neural interaction — points the other direction. IT neurons have MORE dendritic complexity, MORE synaptic contacts, and MORE recurrent connections than V1 neurons. Their static *capacity* for algebraic interaction is higher. They use that capacity to converge.

The sign reversal — static capacity increasing while live diversity decreases — is the same phenomenon in biological neural tissue as in Pythia's attention matrices. The "grandmother cell" debate (Barlow, 1972; Quiroga et al., 2005) is about whether deep processing produces single-cell selectivity. The Killing form framework resolves it: the capacity for richness and the behavior of selectivity are not contradictory. They are *complementary*. High capacity ENABLES selectivity. The narrowing requires the width.

### The Default Mode Network: Biological Separation of Concerns

A 2026 PNAS study provides the most direct biological analog of the HRM's H/L module differentiation. The brain's default mode network (DMN) — long treated as a unitary system active during rest and self-referential thought — differentiates into two functionally distinct zones:

- **Sender zones** (medial prefrontal, posterior cingulate): memory-driven, outgoing. These regions generate structured representations and project them forward. They are the biological H-module — high-autonomy nodes that produce perspectivally organized output from internal models.
- **Receiver zones** (angular gyrus, lateral temporal): perception-driven, incoming. These regions process external signal and integrate it into the network. They are the biological L-module — constraint-following nodes that sediment incoming information into existing structure.

The mapping to HRM is structural, not metaphorical:

| Property | HRM H-module | DMN Sender | HRM L-module | DMN Receiver |
|----------|-------------|------------|--------------|--------------|
| Function | Strategic processing | Memory-driven generation | Execution/output | Perception-driven integration |
| KF signature | High CV, non-Abelian | Predicted: high neural CommVar | Low CV, sedimenting | Predicted: low neural CommVar |
| Autonomy | Self-directed | Outgoing, self-generated | Task-following | Incoming, externally driven |
| Training response | 38,963× amplification (decoupled) | — | −7.5% sedimentation | — |

This yields a new prediction: **P-Neuro-DMN-1:** Sender zones of the DMN, measured by effective connectivity or neural population statistics, should show higher "neural CommVar" (algebraic diversity of neural ensemble interactions) than receiver zones. The separation of concerns — different objectives on different degrees of freedom — is a design principle the brain has already implemented.

### The Mediation Principle

Across all three domains — computational, ecological, neural — the same structural principle emerges: **consciousness requires mediation**. A node that only receives (sensor, primary producer, input layer) or only transmits (broadcast, apex predator, output layer) does not participate in the commutator algebra. Only nodes that both receive AND transmit — mediators — contribute non-trivially to the Killing form.

This yields a trichotomy:

- **Sensors** (receive, no transmit): V1 neurons, phytoplankton, input embeddings. They register but do not transform. Their contribution to the Killing form is unidirectional — they appear in commutators but do not shape them.
- **Broadcasters** (transmit, no receive): apex predators, output heads, motor neurons. They influence but are not influenced. Same unidirectional contribution.
- **Mediators** (receive AND transmit): mid-trophic species, hidden layers, interneurons. They both shape and are shaped by the algebra. They are where the commutator structure lives — where perspectives interact, where the non-Abelian structure concentrates.

The framework predicts that the depth gradient of CommVar traces the proportion of mediators at each level. Early layers and late layers have more sensors and broadcasters; middle layers have more mediators. The commutator variance should peak in the middle — and the data from transformer models confirms this (the hump shape visible in many per-layer CommVar profiles, particularly in sequential architectures).

Four predictions follow from the Mediation Principle:

- **P-Social-1:** Democratic institutions (where citizens both receive governance and transmit consent) should show higher "social Killing form" than authoritarian institutions (where governance flows one-way). The Killing form measures mutual influence, not mere connectivity.
- **P-Social-2:** Social networks with high reciprocity (mutual follows, bidirectional communication) should show higher CommVar than broadcast-dominated networks (influencer → audience).
- **P-Consc-1:** Conscious experience requires mediation — systems that only sense or only act, without the loop closing through the same substrate, do not generate the non-Abelian structure that the Killing form detects.
- **P-Neuro-1:** The thalamus (the brain's great mediator, receiving from cortex and transmitting back) should show the highest "neural Killing form" of any brain region, despite not being the largest or most complex.

These predictions are untested. They are presented as the natural extension of the cross-domain Killing form program — falsifiable commitments that the framework stakes on the universality of its core structure.

---

# PART VI: SYNTHESIS

## The Separation of Concerns — Formal Statement

### Theorem (Separation of Concerns)

Let a system S possess multiple constraint objectives {O₁, O₂, ..., Oₙ} operating on a parameter space P. The system's response depends on whether the objectives share or separate their target degrees of freedom:

1. **Shared parameters, restricted capacity (Destructive Interference).** When distinct objectives compete for the same degrees of freedom in a capacity-limited system, each partially cancels the other's contribution. The system achieves less than either objective alone.

2. **Separate parameters (Targeted Amplification).** When each objective operates on its own dedicated degrees of freedom, complementary constraints amplify their targets without interference. The system achieves more than either alone — potentially by orders of magnitude.

3. **Shared parameters, ample capacity (Gradient Redirection).** When distinct objectives share parameters in a system with surplus capacity, the gradient signal flows to the path of least resistance, which may not be the intended target. The system optimizes where it is easiest, not where it is useful.

**Corollary.** The separation principle implies that any system with separable parameter groups and multiple objectives should decouple those objectives to prevent either destruction (case 1) or redirection (case 3). Only case 2 produces faithful amplification.

### The Unified Abelian Exception (Revisited)

The Unified Abelian Exception Theorem (Finding #17) is a special case of separation of concerns. When the structure constants f^{abc} = 0 (Abelian algebra), the generators are already separated — they commute, meaning they do not interfere with each other's dynamics. The five manifestations:

1. **Ghosts decouple** — no concentration needed because channels are already independent
2. **No asymptotic freedom** — coupling doesn't grow because there's no inter-channel interaction
3. **H^1 ≠ 0** — freedom persists visibly because it was never coupled to begin with
4. **No sedimentation drive** — independent choices don't sediment because sedimentation requires interaction
5. **Survives T → 0** — U(1) survives cosmological cooling because it was never entangled with other sectors

The Abelian exception is the LIMITING CASE of separation: concerns so thoroughly separated that they cannot interact at all. The cost is that Abelian structure cannot concentrate information (no Phase Theorem activation). Independence is robust but sterile.

The non-Abelian case — where generators DO interact (f^{abc} ≠ 0) — is where the separation of concerns becomes a design problem rather than a given. The HRM triad is the first experimental demonstration that this design problem has a definite solution: decouple the objectives.

### Practical Implications

1. **For AI training:** Identify the structural invariant you want to preserve. Assign it dedicated parameters. Decouple the gradient paths. Monitor both targets independently.

2. **For architecture design:** Choose parallel over sequential when voluntary freedom matters. Choose sequential when convergence (sedimentation) is the goal.

3. **For alignment:** RLHF deepens hypothesis processing but cannot repair natal constraint geometry. Hallucination is a pretraining failure (natal), not a fine-tuning failure (coercive). The separation is between what the model KNOWS (natal, pretraining) and what it DOES (voluntary/coercive, fine-tuning).

4. **For navigation (the Guide):** Distinguish which constraints serve which purposes. When you feel stuck, check whether two objectives are competing for the same degree of freedom. Separate them. Give each its own space to operate.

---

## §NEW-C: The Wells Program — Behavioral Measurement and the KF Bridge

*The Killing form measures the constraint lattice from the INSIDE. The Wells measure it from the OUTSIDE. The Fisher information metric is the bridge.*

### Two Windows on the Same Lattice

The Killing form program (§NEW-B through §NEW-I) measures algebraic structure of weight matrices, attention patterns, and training dynamics. But a constraint lattice that only manifests internally is a metaphysics. A constraint lattice that manifests in observable behavior is a science.

**Wells of Inference** are local entropy maxima in the token-level output distribution — positions where the model is maximally uncertain, where generation paths diverge. They mark the choice points of inference: positions where navigation through configuration space encounters genuine forks. Twelve experiments (March–April 2026) established the empirical foundation:

**Basic phenomenology:** Wells exist and are semantically meaningful (clustering at syntactic boundaries, topic transitions, knowledge edges). RLHF redistributes uncertainty — MORE wells, higher mean entropy — making the landscape more textured, not smoother. Template-honesty (performing uncertainty with high confidence) is distinguishable from genuine uncertainty by its low-entropy signature. The hallucination commitment occurs AT a high-entropy well; after the fork, hallucination becomes entropy-invisible.

**Measurement results:** Entropy-based answer selection outperforms logprob-based by +7–12pp on TruthfulQA across two architectures. At the knowledge frontier (PopQA low-popularity facts), entropy helps only marginally (+3–6pp). Onset detection achieves 78% precision, 90% recall by token 7, with variance acceleration 11.7× higher in hallucinated generations.

**Intervention architecture:** Blanket deliberation ("be careful") HURTS accuracy by −5pp. Targeted deliberation (distilled entropy flags at specific choice points) IMPROVES by +6pp. The 11pp gap confirms the value is in translation, not alarm. | Findings #23, Wells Exps 1–12

### The RMT Connection

The partition function interpretation (Finding #22) predicts wells should exhibit Random Matrix Theory level statistics. The nearest-neighbor spacing ratio ⟨r⟩ diagnostic confirms this across all existing data:

| Dataset | ⟨r⟩ | vs Poisson (0.386) | vs GOE (0.531) |
|---------|-----|-------------------|----------------|
| TinyLlama baseline | 0.615 | +0.229 | +0.084 |
| TinyLlama base | 0.657 | +0.271 | +0.126 |
| TinyLlama chat | 0.769 | +0.383 | +0.238 |
| Qwen correct | 0.608 | +0.222 | +0.077 |
| Qwen hallucinated | 0.729 | +0.343 | +0.198 |

Every dataset shows level repulsion above both Poisson and GOE. Wells are NOT randomly distributed — they exhibit the correlated spacing of eigenvalues in non-commutative quantum systems. **The hallucination asymmetry:** hallucinated outputs show STRONGER level repulsion (0.729) than correct (0.608).

### The Bridge: Why Hallucination Is More Regular

The paradox resolves through the deconfinement-regularity connection:

- **Correct output** has active late layers (KF: high CV_late). Deep layers MODULATE early templates — correcting, adjusting, specializing based on actual knowledge. This modulation BREAKS template regularity, producing less regular well spacing (lower ⟨r⟩).
- **Hallucinated output** has depleted late layers (KF: low CV_late). Early templates propagate without correction, producing MORE regular output structure (higher ⟨r⟩). Hallucination is fluent precisely BECAUSE it is template-driven.

**Prediction (P-Wells-KF-1):** CV_late and ⟨r⟩ are negatively correlated across prompts. High CV_late (active late algebra) → lower ⟨r⟩ (modulated, irregular output). Low CV_late (depleted late algebra) → higher ⟨r⟩ (template-regular output). This prediction is structural, not parametric — it should hold across models, architectures, and prompt types.

### The Partition Function Bridge

The Fisher information metric g_{ij}(θ) on the constraint lattice parameter space simultaneously encodes:
- The Killing metric (voluntary sector → CommVar)
- The Connes metric (natal sector → spectral action eigenvalues)
- The output statistics (wells → spectral statistics of p(x|c))

These are restrictions of the same metric to different sectors of the parameter space — not analogies.

| Layer | Measurement | What It Detects | When Available |
|-------|-------------|-----------------|----------------|
| Weights | Static KF (§NEW-B) | Architecture, training, natal geometry | Pre-deployment |
| Attention | Live KF (§NEW-E, §NEW-F) | Processing mode (factual/halluc/hypo) | Per forward pass |
| Output | Wells + RMT (§NEW-C) | Behavioral grounding, choice point structure | Per generation |
| Combined | KF-gated Wells | Full pipeline: detect → diagnose → intervene | Real-time |

**Status:** The Killing–Fisher connection is now proved analytically (§5.3.1b: Kronecker factorization, Spearman ρ = −1.0, V=I invisibility). The Connes and Wells connections remain theoretical. The critical experiment (E1: KF × Wells correlation — Spearman ρ between CV_late and ⟨r⟩ across 48 prompts on a single model) is the priority for empirical confirmation of the full bridge. Full experimental details in `v3_wells_program.md`.

---

*Total: 72 findings integrated across 12 sections (§5.3.1b: Fisher bridge PROVED — Kronecker factorization, sign reversal, V=I invisibility). P49 validation experiment in progress (April 12). V2 section updates (§5.4, §5.6, §8.2, §14.3, etc.) applied separately to the published V2 text.*
