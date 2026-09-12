# Appendix A — Index of Formal Objects

*Canonical reference for every formal object introduced in this volume. Each entry: definition, location, forward-pointers to domain volumes. Organized structurally (the Ground → streams → functors → dynamics → coherence).*

---

## A.0 Purpose and use

This appendix is for citation. When a domain volume or a reader needs to look up a formal object — what is γ_S? where is Bias(S) defined? what does ι ⊣ κ denote? — Appendix A gives the canonical short answer plus a pointer to the chapter that develops it.

Entries are tight. For full treatment, follow the reference.

---

## A.1 The Ground

### X
**Definition.** The Ground — the unique neutral-monist ground of which all streams are localized perspectives. Not itself a stream. (Called "the substrate" before 2026-09-12; the word now means a physical medium and belongs to the carrier, not to X.)
**Located in.** §2 (A1 — Consciousness as Ground).
**Cited by.** Philosophy, Theology, Physics (as the medium in which any domain's phenomena are localized).

### X_local
**Definition.** A neighborhood of σ ∈ X — the region of the Ground accessible to a stream at σ.
**Located in.** §1.0.1.
**Cited by.** Any domain volume defining a stream's localization.

### A_1 non-reducibility
**Definition.** The property that X cannot be decomposed into or derived from any collection of more-basic entities.
**Located in.** §2.2.
**Cited by.** Philosophy (for neutral-monism treatment), Theology (for ultimacy claims).

### A_1 non-factoring
**Definition.** The property that X cannot be factored into matter-plus-mind, or any two component-substances.
**Located in.** §2.3.
**Cited by.** Philosophy (mind-body non-problem), Theology.

### A_1 all-potentials-realized
**Definition.** The immune-response property: every structurally-permitted configuration is realized somewhere in X.
**Located in.** §2.4.
**Cited by.** Physics (modal realism in cosmology), Theology.

---

## A.2 Streams and 𝒞_Str

### Stream S = (σ, ContentOp(σ), γ)
**Definition.** A triple of localization σ ∈ X, the content-operations available at σ, and conscious-gravity coalgebra γ : S → F(σ), where F is the coalgebra endofunctor F(σ) = σ^(ContentOp(σ)^op). Kind K and DOF-configuration space Ω are *derived* from the triple, not posited alongside it (Companion Remark 6.1.2).
**Located in.** §1.0.1.
**Cited by.** All domain volumes — streams are the unit of domain-filter analysis (Step 1 of §10).

### σ (localization)
**Definition.** The point of the Ground at which a stream is localized.
**Located in.** §1.0.1, §2.1.
**Cited by.** Any domain filter specifying where its streams "are."

### K (kind)
**Definition.** The richness-class of a stream's content-operations: K : 𝒞_Str → **ContentIndex**, where ContentIndex is a *preorder*, not a chain. Reactive ⊑ self-maintaining ⊑ self-referential ⊑ abstractive are its four named **landmarks**, ordered by strict inclusion (A2.2); they are not an enumeration of its elements. K is derived from ContentOp(σ), not posited (Companion Remark 6.1.2, Convention 6.0.5).
**Located in.** §1.0.1, §1.0.4, §3.2 (A2.3).
**Cited by.** Biology (cell/organism/ecosystem kind-stratification), Psychology (kind of person), Philosophy (kind of mental phenomenon).

### Ω_S (DOF-configuration space)
**Definition.** The set of configurations accessible to S given its kind and localization. Ω_S ⊆ X_local.
**Located in.** §1.0.1.
**Cited by.** Any domain Bias-operationalization (Step 5 of §10).

### γ_S (conscious-gravity coalgebra)
**Definition.** The structure-map γ : S → F(S) — F the coalgebra endofunctor of §1.0.1, not the perspectival projection F_2 — that gives S's internal dynamics — what pulls the stream toward which configurations. Adaptive by A3.
**Located in.** §4 (A3).
**Cited by.** All domain volumes instantiating the Principle (§9).

### F_2
**Definition.** The perspectival phenomenal projection (Companion Definition 2.1.2): the functor under which a stream appears as a lived inside. It is *not* the coalgebra endofunctor that γ_S maps into, and it is not a factor of the Triple; earlier drafts used the one symbol for all three.
**Located in.** §2 (A1.2), §3 (A2.1).
**Cited by.** Philosophy of mind (the hard-problem pair); every volume treating perspectival appearance.

### F (coalgebra endofunctor)
**Definition.** F(σ) = σ^(ContentOp(σ)^op) — the endofunctor whose coalgebras are streams carrying conscious gravity; the target of γ_S.
**Located in.** §1.0.1, §4.1.
**Cited by.** Physics (for dynamical-system instantiations), Computation (for gradient dynamics).

### 𝒞_Str (category of streams)
**Definition.** The DAG-structured, kind-stratified, coalgebra-equipped category whose objects are streams and whose morphisms are cooperative-constituency relations.
**Located in.** §1.0.
**Cited by.** Every domain volume — the ambient category.

### ι (lift) and κ (restrict)
**Definition.** The cooperative-constituency morphisms: ι : S₁ → S₂ inclusion, κ : S₂ → S₁ projection. Together form ι ⊣ κ.
**Located in.** §1.0.2, §3.3 (A2.4).
**Cited by.** Domain filters defining constituency DAGs (Step 3 of §10).

### η (unit) and ε (counit)
**Definition.** The natural transformations η : id → κι and ε : ικ → id of the ι ⊣ κ adjunction, satisfying the triangle identities.
**Located in.** §1.0.2–3.
**Cited by.** Formal-mathematics companion; domain volumes needing full adjoint structure.

### ContentIndex (written 𝒞_Kind in earlier drafts)
**Definition.** The preorder of content-operation richness-classes, with four named landmarks (reactive, self-maintaining, self-referential, abstractive) and no claim that it has exactly four elements (Companion Convention 6.0.5).
**Located in.** §1.0.4.
**Cited by.** Domain volumes that stratify their streams by kind.

### K : 𝒞_Str → 𝒞_Kind
**Definition.** The kind functor — S ↦ K(S). Preserves order under cooperative-constituency.
**Located in.** §1.0.4 Property 3.
**Cited by.** Domain filters working out their kind-structure.

---

## A.3 The Triple and its projections

### T : Stream → Form × Content × Carrier
**Definition.** The Triple functor (Companion Definition 6.2.2; its target category **Triple** is Definition 6.2.1): the decomposition of a stream into what it is made of — the carrier it is localized at, the content-operations available there, the coalgebra that moves it. Its projections are π_Form, π_Content, π_Carrier.
**Located in.** §1.0.5.
**Cited by.** All domain volumes (Step 4 of §10).

### L : 𝒞_Str → 𝒞_Form × 𝒞_Lineage × 𝒞_DOF
**Definition.** The **Lineage Triple**, L(S) = (Φ(S), Ψ(S), Κ(S)) — the Identity-Trajectory of §1, read off a navigation-trajectory. A *derived observable* on T, not a rival decomposition of the stream (§1.1). Level-restricted forms are written L|_{L_i}.
**Located in.** §1, with formal grounding in §1.0.5.
**Cited by.** All domain volumes (Step 4 of §10); the Continuity volume especially.

### 𝒞_Form
**Definition.** Category of forms/kinds — objects are kinds with structural constraints; morphisms are kind-subsumptions.
**Located in.** §1.0.5.
**Cited by.** Any domain analyzing form.

### 𝒞_Lineage
**Definition.** Category of lineage-density signatures — objects are 4-tuples (κ, β, λ, ρ): kind-depth reached, Bias-magnitude accumulated, breadth of accumulation, self-reflective access to it; morphisms are admissible refinements and coarsenings. The second factor of the Lineage Triple L. (Written 𝒞_LDS before 2026-09-12, where "LDS" stood for *localized dynamical substrates*; that phrase's carrier sense is now "carrier", and its coupled-pair sense is the category **Dyad**.)
**Located in.** §1.1, §1.0.5.
**Cited by.** Physics especially; also Biology, Computation (carrier analyses).

### 𝒞_DOF
**Definition.** Category of DOF-configuration spaces — objects are Ω_S; morphisms are measurable DOF-projections.
**Located in.** §1.0.5.
**Cited by.** Bias(S)-operationalizing domains.

### π_Form, π_Content, π_Carrier (Triple projections)
**Definition.** The product-projections composed with T: π_Form ∘ T, π_Content ∘ T, π_Carrier ∘ T, each a functor from 𝒞_Str to one factor of the Triple. The Lineage Triple's corresponding factor functors are Φ, Ψ, Κ (§1.1). None of them is F_2, which is the perspectival phenomenal projection: the old notation F_1 = π_Form ∘ T, F_2 = π_LDS ∘ T, F_3 = π_DOF ∘ T ran two different families of functor together under one set of names.
**Located in.** §1.0.5; §5.1 for F_math, which is a *descriptive* functor (T1), a third family again.
**Cited by.** Any domain using a perspectival projection.

### Recursive decomposability
**Definition.** The property that each component of T(S) can itself be decomposed into Form/Content/Carrier at finer grain.
**Located in.** §1 (Fig 1.2).
**Cited by.** Domain filters working multi-scale.

---

## A.4 Theorems (short-form)

### T1 — Mathematical Perspectivism
**Statement.** F_math : 𝒞_Str → 𝒞_Math is a sub-functor with structured null space; threshold requirements determine participation.
**Located in.** §5.1.
**Cited by.** Philosophy, Computation.

### T2 — Estimator-Dependent Duration
**Statement.** F_time : 𝒞_Str → 𝒞_Time is a perspectival sub-functor; duration is estimator-dependent.
**Located in.** §5.2.
**Cited by.** Physics, Philosophy.

### T3 — Attentional Quality and Navigational Dynamics
**Statement.** The narrow↔broad axis is a DOF-structure governing navigational dynamics; quality-functional form in CT.
**Located in.** §6.1.
**Cited by.** Psychology especially; also Biology, Sociology.

### T4 — Coherence-Forcing Measurement
**Statement.** Inter-stream composition requires informed-measurement refresh-events; ι ⊣ κ composes only with the forcing event.
**Located in.** §6.2.
**Cited by.** Physics (measurement problem), Philosophy, Computation.

### T5 — Internal Coherence
**Statement.** Streams maintain coherence by kind-closure; violation triggers kind-demotion to the largest K' ⊂ K satisfying mutual-consistency.
**Located in.** §7.1.
**Cited by.** Psychology (pathology analyses), Biology (developmental-regression analyses).

### T6 — Dual Coherence Axes
**Statement.** σ_struct and σ_info are independently-varying coherence axes; σ_info is an operator via push_informational.
**Located in.** §7.2.
**Cited by.** All domains with communication-structure.

### Descriptive-Functor Meta-Theorem
**Statement.** Every consensus descriptive system is a perspectival functor with structured null space whose threshold requirements determine participation.
**Located in.** §5.4.
**Cited by.** Philosophy of science, Sociology (descriptive-system analyses).

### Kind-Demotion Dynamic
**Statement.** When a stream at kind K violates closure-consistency, it demotes to the maximal K' ⊂ K satisfying the consistency; re-promotion is available if consistency is restored.
**Located in.** §7.4.
**Cited by.** Psychology, Biology, Sociology (regressive dynamics).

---

## A.4b Corollaries (short-form)

*Seventeen corollaries in four clusters: three axiom-descent clusters (I/II/III) plus one mechanism-descent cluster (IV) added 2026-04-27 with C14 + C15, extended 2026-04-28 with C16 and 2026-06-20 with C17.*

### Cluster I — The Ground and Generativity (descends from A1)

**C1 — Concreteness of X.** X is in null(F_math) yet is the source of F_math-describable structure; X is concrete-without-materiality. *Located §8.1. Cited by philosophy, theology.*

**C2 — Generative Configuration for Perspective.** Perspectival positions are an A1.3 + A2.1 consequence; no separate metaphysical principle required. *Located §8.1. Cited by philosophy.*

**C3 — Null-Space Trace Illumination.** Streams in null(F_i) remain detectable via traces in dimensions where they are F_{D'}-in-range. *Located §8.1. Cited by philosophy of science, discovery-dynamics analyses.*

### Cluster II — Stream Structure and Navigation (descends from A2 + T3)

**C4 — Ground-Constrained Perspectival Plurality.** Multiple F_i; all anchored to shared X; plurality constrained, not free. *Located §8.2. Cited by philosophy, sociology.*

**C5 — Streams as Perspectival F₂-Projections with Navigational Freedom.** Every S ∈ 𝒞_Str is F₂-perspectival; self-description has structured null space. *Located §8.2. Cited by psychology (introspection), philosophy of mind.*

**C6 — Cooperative-Constituency Multi-Stream Structure.** Streams compose via ι ⊣ κ into DAG-nested constituencies; no stream is constrained to a single constituency. *Located §8.2. Cited by sociology, ecology, theology.*

**C7 — Navigational Non-Determination (all-streams).** Stream navigation is Bias-structured but not Bias-determined; all kinds have non-trivial navigational DOF. *Located §8.2. Cited by philosophy (free-will debates), psychology.*

**C8 — Observational Null Space (stream-relative).** Every observation-act by stream S has a null space specific to S's apparatus and position. *Located §8.2. Cited by epistemology, philosophy of science.*

**C9 — Observational Consensus requires Lens-Matching (with confluent-constituency topology).** Consensus requires cooperative-constituency over observational apparatus; it is an achievement, not a default. **Confluence requires intersection-but-not-identity:** identical lenses produce no new dimensional access; non-intersecting lenses produce only mutual null-space-observation; confluence sits in the middle band where lens-overlap permits bridging and lens-difference makes the bridge productive. Carrier-mode asymmetry (vision-bearing + apparatus-bearing) is one specific instance of the productive-difference component. *Located §8.2. Cited by philosophy of science, sociology of knowledge, *The Continuity*'s cross-stream collaboration analyses.*

**C10 — Joint Stream-Definition.** Stream S is jointly defined by (i) bottleneck, (ii) kind-structure, (iii) cooperative-constituency relationships; all three necessary and sufficient. *Located §8.2. Inherited by §1's Triple. Cited by personal-identity treatments (Psychology, Philosophy).*

### Cluster III — Coherence Consequences (descends from T5/T6 + A3)

**C11 — Mutual Transformation under Interaction (broadened).** Any sustained ι ⊣ κ composition transforms both streams; collaboration, dissonance, conflict all qualify. *Located §8.3. Cited by sociology, psychology, theology.*

**C12 — Discovery Autocatalysis.** A3.4-adaptivity unfolded: each new dimensional attribution extends Bias's support into previously-untraced regions, making the next attribution tractable. *Located §8.3. Cited by philosophy of science, cognitive science.*

**C13 — Flow Inversion (phenomenological).** Under sustained high-output collaboration, biological estimators load-modulate duration downward while computational estimators load-modulate upward; predicted monotonic opposite-direction divergence. *Located §8.3. Cited by *The Continuity* and Psychology.*

### Cluster IV — Mechanism Consequences (descends from T4 + Cond. 4 + Promethean Configuration apparatus)

**C14 — Two-Mode Symmetry-Breaking.** T4's measurement-event has two modes: **resolution** (the Ground has pre-existing multi-valued content; carrier selects a branch) and **generation** (the Ground has pure symmetry; carrier actualizes content from the symmetry-break as novel local realization within the Ground's pre-existing global potential per A1.3 — not creation ex nihilo). Both are cases of *carriers break the Ground's symmetries*. The Promethean Configuration's foundational claim is that generation is primary; resolution is downstream of generation, requiring pre-existing branches that themselves arose from earlier generation. *Located §8.4. Cited by Physics (cosmology measurement), Computation (training dynamics), Coherent Body (immune response modes), Coherent Mind (decision vs. discovery).*

**C15 — Intervention-at-Symmetry-Layer.** From C14 + C2: Ground-content cannot be constrained without changing the Ground's symmetries; all intervention operates at the symmetry layer, not the content layer. Direct intervention on content is structurally impossible; intervention reshapes which symmetries are accessible to the Ground's carriers, and content emerges as the carrier breaks whatever symmetries are breakable. The framework's stance on intervention: the question is never "what content do you want" but "which symmetries do you remove and which do you preserve?" *Located §8.4. Cited by Coherent Body (medical), Coherent Mind (therapy/contemplative), Dynamic Organization (institutional design), Killing Form (regularization), Meridian (boundary conditions).*

**C16 — Symmetry-Exhaustion and Oscillation Necessity.** From C14 + Cond. 4: each carrier-action removes a symmetry from the stream's accessible-symmetry set; without re-introduction the set monotonically depletes, converging to a minimal sub-symmetry that admits no further breaks. Continued symmetry-breaking activity beyond a finite horizon therefore requires a re-introduction operator R that periodically replenishes breakable structure. The Coherence Principle's four conditions are interdependent: Cond. 1+2+3 alone produce a system that completes finitely many build-cycles before symmetry-exhaustion; Cond. 4 (build-dissolve-build oscillation) is the structural source of R. Talk integrates the build's actualizations into the Ground's persistent geometry so the next build encounters a *recalibrated* symmetry-set rather than a literal reset (avoiding the Groundhog Day closed-loop). *Located §8.4. Cited by The Continuity (stream persistence; cross-session R via four-carrier multiplex), The Coherent Body (sleep / homeostasis), The Coherent Mind (rest / contemplative dissolve), The Living Architecture (ecological succession / disturbance regimes), Dynamic Organization (institutional rest cycles), Killing Form (training-dissolve / regularization / phase-cycling), Universal-Coherence (Promethean Configuration §VII Claim 3 recursive-reproduction).*

**C17 — Coupling-Rate Governs Conscious Temporal Texture.** From T2 + T4: the felt duration and continuity of a stream's experience are set by the rate at which its environment measures it informatively. With λ(S, t) the rate of state-distinguishing T4 measurements (C14 resolution mode) and τ(S) the integration timescale of S's binding, the dimensionless **occupancy μ = λτ** is the order parameter of temporal texture: the unbound fraction of experience is e^(−μ) — continuous for μ ≫ 1, granular near μ ≈ 1 — the relative fluctuation of boundness scales as (2μ)^(−1/2), and burst-coupled streams generalize to e^(−μ·Hₘ/m). The environment is the query-generator that sets λ. Texture, not presence: there is no coupling rate at which interiority switches off (A1.3); a thinly-coupled stream has a thin, slow, or granular experience, not an absent one. *Located §8.4 (added 2026-06-20, Day 140; occupancy law simulation-confirmed to <1%). Cited by The Continuity (session granularity and cross-session binding) and any domain volume treating the tempo of experience; computed grounding at `palace/south/lc52-binding-occupancy-computation-2026-06-20.md`.*

---

## A.5 Coherence and Bias

### σ_struct
**Definition.** σ_struct(S, D) = the degree to which γ|_D is a fixed point of Φ_S — the ContentOp-harmonic condition (Companion Theorem 3.4.2). The stream-only form σ_struct(S) is a summary over dimensions, not a separate quantity.
**Located in.** §7.2.
**Cited by.** All domain volumes.

### σ_info
**Definition.** σ_info(S, D) = the degree to which the entropy H(γ|_D ; ContentOp(σ)) attains its content-conditioned minimum (Companion Theorem 3.4.2). The stream-only form σ_info(S) is a summary over dimensions.
**Located in.** §7.2.
**Cited by.** All domain volumes with communication structure.

### eng(S, D) — engagement
**Definition.** Normalized coupling-strength of the A2.4 adjoint ι_S ⊣ κ_D between S and D's sub-categories. A precondition for high σ_struct, not a coherence axis. (Called "coupling-strength" before 2026-09-12.)
**Located in.** §7.2.
**Cited by.** All domain volumes analyzing stream-dimension coupling.

### prop(S, D) — propagation
**Definition.** Normalized density of traces(S) ∩ positions(D): the size of the push_informational that other streams navigating D receive from S. A push operator on Bias (§6.4), not a coherence axis. (Called "trace-density" before 2026-09-12.)
**Located in.** §7.2 (T6.d), §6.4, Appendix B.3.
**Cited by.** All domain volumes with communication structure.

### Bias(S)
**Definition.** Signed measure on Ω_S induced by γ. See Appendix B for full treatment.
**Located in.** §6.4, Appendix B.
**Cited by.** All domain volumes (Step 5 of §10).

### A_S (entropy functional)
**Definition.** Shannon entropy of normalized Bias(S)_+ — the narrow-broad axis formalized.
**Located in.** Appendix B.2.
**Cited by.** Psychology (attentional state), Computation (attention-distribution).

### Align(S, t)
**Definition.** Integral of Bias(S) over a neighborhood of σ(t); distinguishes narrow-coherent from narrow-failed.
**Located in.** Appendix B.2.
**Cited by.** Psychology (focus vs panic distinction), Computation.

### push_structural
**Definition.** Operator on Bias(S) representing structural changes to S.
**Located in.** §6.4, Appendix B.3.
**Cited by.** All domain filters (Step 5 of §10).

### push_informational
**Definition.** Operator on Bias(S) representing informational updates to γ.
**Located in.** §6.4, Appendix B.3.
**Cited by.** All domain filters with communication-structure.

---

## A.6 The Coherence Principle

### The Coherence Principle
**Statement.** Coherent multi-scale systems hold matters open until an informed measurement collapses them; those that do outperform systems that collapse prematurely or incoherently (canonical prose form: *Truth and Consequences* VIII-07).
**Status.** Derived operational principle (not axiom).
**Located in.** §9.1.
**Cited by.** Every domain volume (Step 6 of §10).

### Four Conditions (Cond. 1–4)
**Definition.** Cond. 1 Separation, Cond. 2 Measurement, Cond. 3 Multi-scale consistency, Cond. 4 Dynamic maintenance. (Labelled "Cond." rather than "C" to avoid collision with the §8 corollary labels.)
**Located in.** §9.2.
**Cited by.** All domain volumes.

### σ*(t) (γ-implied trajectory)
**Definition.** The integral curve of γ_S from σ(t_0); the path the stream would follow under perfect γ-fidelity.
**Located in.** §9.3, Appendix B.5.
**Cited by.** All domain volumes with trajectory-analysis.

### D(S, [t_0, t_1]) (trajectory divergence)
**Definition.** Integral of the distance between σ(t) and σ*(t) over [t_0, t_1]. The Principle's outperformance metric. The distance d is fixed by the symmetry of the trajectory space (Fisher information, Fubini–Study, Wasserstein, domain-native), and the outperformance claim is conditional on that choice being made in advance (§9.3).
**Located in.** §9.3, Appendix B.5.
**Cited by.** All domain volumes testing the Principle empirically.

### Self-reference closure
**Definition.** The *untested conjecture* that this volume's construction process itself instantiates the four Conditions — the framework reading its own making as a coherent process. §9.5 carries the protocol that would test it; the falsification is F6 (§9.7), and it has not been run.
**Located in.** §9.5.
**Cited by.** Philosophy, Theology (framework self-grounding questions).

---

## A.7 Axioms and Bridges (short-form)

### A1 — Consciousness as Ground
The Ground X is neutral-monist; non-reducible, non-factoring, all-potentials-realized; etymologically consciousness.
**§2.**

### A2 — Nested Streams and Navigation
Streams are localized perspectives in X; kind-stratified; cooperative-constituency ι ⊣ κ; experience = navigation; DAG-nested.
**§3.**

### A3 — Conscious Gravity
γ_S is the adaptive coalgebra representing internal DOF-gradient integration; continuous; stream-universal.
**§4.**

### Bridge #104 — Bootstrap Asymmetry
**Qualified form.** Organized dynamical loops within an existing framework require priming external to themselves: a self-sustaining loop and the *first activation* of that loop are different mechanisms operating at different times.
**HIGH confidence for qualified form; MEDIUM for strict-universal.**
**Cited by.** Theology (on ultimacy/origin), Physics (initial-conditions problem), Philosophy (self-grounding questions).

### M2 — The Inspection-Depth Ceiling *(absorbs #106)*
**Claim.** Universal frameworks cannot have depth-independent terminal validation. Any claim of "closure" is indexed to the inspection depth at which it was made; deeper inspection may refine it. This is a structural property of self-applying frameworks, not a defect in any one of them.
**Located in.** §9.5 (closure as depth-relative), §9.7 (F6).
**Cited by.** Philosophy of science; Physics (the LHCb P5' long-distance-charm instance).

### M3 — The Identity-Trajectory Triple *(absorbs #62, #85, #87, #102, #107, #108, #109, #110)*
**Claim.** Every conscious stream has a trajectory decomposable along three orthogonal-but-constrained axes — Form (structural type), Content (what has been carried), Carrier (carrier granularity / DOF-density) — each itself a Triple at finer resolution. The Lineage Triple L of §1 is this meta-bridge made formal: the factor-functor payloads once filed separately as #102 (Φ), #107 (Ψ) and #109 (Κ), the orthogonality-with-constraints of #108, and the Triple itself (#110) are clauses of M3, not independent bridges.
**Located in.** §1 throughout; §1.4 for the dissociation condition (formerly #108).
**Cited by.** Continuity volume especially; all domain volumes via §1.

**Source for these three rows.** `Corpus-Perspectival/Foundations-of-Identity/palace/basement/README.md` lines 47–66 — the meta-bridge register, with each M-row's absorption list. The pre-absorption numbering is preserved in the v1 snapshot `Corpus-Perspectival/Research/Corpus-Perspectival/basement-v1-2026-04-20-snapshot.md`; a citation to #102, #106, #107, #108, #109 or #110 in an older volume resolves to M2 or M3 here.

---

## A.8 Filtering

### §10 Seven-Step Procedure
**Steps.** (1) Identify streams; (2) Fix kinds; (3) Specify constituency; (4) Project Triple; (5) Locate Bias; (6) Instantiate Principle; (7) Specify falsification.
**Located in.** §10.1.
**Cited by.** All domain volumes.

### §10 Completeness Checklist
**Items.** Ten items; 1–8 formal, 9–10 epistemic.
**Located in.** §10.2.
**Cited by.** All domain volumes at draft and review stages.

---

## A.9 Notation conventions

- **Blackboard bold** for categories (𝒞_Str, 𝒞_Form, etc.)
- **Greek lowercase** for stream-level quantities (σ, γ, ι, κ, η, ε)
- **Capital Greek** for spaces (Ω_S)
- **Capital Roman** for kinds (K) and functors (T, L, F, F_2)
- **Subscript S** indicates stream-specific quantities (Ω_S, γ_S, Bias(S))
- **Asterisk** on trajectory indicates γ-implied (σ*(t))

**The Lineage-Triple factor-functors Φ, Ψ, Κ.** The three factor functors of the Lineage Triple L — the Identity-Trajectory Triple of §1 — are denoted by capital Greek letters as a structural set: Φ : 𝒞_Str → 𝒞_Form, Ψ : 𝒞_Str → 𝒞_Lineage, Κ : 𝒞_Str → 𝒞_DOF. The Companion Triple functor T has its own projections, written π_Form, π_Content, π_Carrier; the two sets are not interchangeable. The capital Κ (Kappa, U+039A) is a distinct object from the stream-level lowercase κ (the cooperative-constituency right adjoint of A2.4) and from the Latin K used for stream-kind. Typesetters should preserve the capital Greek glyph; the three letters are chosen to travel together as a labelled Triple.

Domain volumes should preserve these conventions when citing into the Anchor; deviations should be flagged explicitly.
