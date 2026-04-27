# Appendix A — Index of Formal Objects

*Canonical reference for every formal object introduced in this volume. Each entry: definition, location, forward-pointers to domain volumes. Organized structurally (substrate → streams → functors → dynamics → coherence).*

---

## A.0 Purpose and use

This appendix is for citation. When a domain volume or a reader needs to look up a formal object — what is γ_S? where is Bias(S) defined? what does ι ⊣ κ denote? — Appendix A gives the canonical short answer plus a pointer to the chapter that develops it.

Entries are tight. For full treatment, follow the reference.

---

## A.1 Substrate

### X
**Definition.** The substrate — the unique neutral-monist ground of which all streams are localized perspectives. Not itself a stream.
**Located in.** §2 (A1 — Consciousness as Substrate).
**Cited by.** Philosophy, Theology, Physics (as the medium in which any domain's phenomena are localized).

### X_local
**Definition.** A neighborhood of σ ∈ X — the substrate-region accessible to a stream at σ.
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

### Stream S = (σ, K, Ω, γ)
**Definition.** A tuple of localization σ ∈ X, kind K, DOF-configuration space Ω, and conscious-gravity coalgebra γ : S → F_2(S).
**Located in.** §1.0.1.
**Cited by.** All domain volumes — streams are the unit of domain-filter analysis (Step 1 of §10).

### σ (localization)
**Definition.** The substrate-point at which a stream is localized.
**Located in.** §1.0.1, §2.1.
**Cited by.** Any domain filter specifying where its streams "are."

### K (kind)
**Definition.** The stream's kind-stratum; K ∈ {reactive, self-maintaining, self-referential, abstractive}, linearly ordered by strict inclusion.
**Located in.** §1.0.1, §3.2 (A2.3).
**Cited by.** Biology (cell/organism/ecosystem kind-stratification), Psychology (kind of person), Philosophy (kind of mental phenomenon).

### Ω_S (DOF-configuration space)
**Definition.** The set of configurations accessible to S given its kind and localization. Ω_S ⊆ X_local.
**Located in.** §1.0.1.
**Cited by.** Any domain Bias-operationalization (Step 5 of §10).

### γ_S (conscious-gravity coalgebra)
**Definition.** The structure-map γ : S → F_2(S) that gives S's internal dynamics — what pulls the stream toward which configurations. Adaptive by A3.
**Located in.** §4 (A3).
**Cited by.** All domain volumes instantiating the Principle (§9).

### F_2
**Definition.** The functor describing integration of DOF over time; the target of γ_S.
**Located in.** §4.1.
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

### 𝒞_Kind
**Definition.** The four-element totally-ordered category of kinds.
**Located in.** §1.0.4.
**Cited by.** Domain volumes that stratify their streams by kind.

### K : 𝒞_Str → 𝒞_Kind
**Definition.** The kind functor — S ↦ K(S). Preserves order under cooperative-constituency.
**Located in.** §1.0.4 Property 3.
**Cited by.** Domain filters working out their kind-structure.

---

## A.3 The Triple and its projections

### T : 𝒞_Str → 𝒞_Form × 𝒞_LDS × 𝒞_DOF
**Definition.** The Identity-Trajectory Triple — principal functor out of 𝒞_Str. Projects a stream to its (Form, Content/Carrier-substrate, DOF-trajectory) decomposition.
**Located in.** §1, with formal grounding in §1.0.5.
**Cited by.** All domain volumes (Step 4 of §10).

### 𝒞_Form
**Definition.** Category of forms/kinds — objects are kinds with structural constraints; morphisms are kind-subsumptions.
**Located in.** §1.0.5.
**Cited by.** Any domain analyzing form.

### 𝒞_LDS
**Definition.** Category of localized dynamical substrates — objects are (σ, local dynamics); morphisms are substrate-inclusions.
**Located in.** §1.0.5.
**Cited by.** Physics especially; also Biology, Computation (substrate-carrier analyses).

### 𝒞_DOF
**Definition.** Category of DOF-configuration spaces — objects are Ω_S; morphisms are measurable DOF-projections.
**Located in.** §1.0.5.
**Cited by.** Bias(S)-operationalizing domains.

### F_1, F_2, F_3 (perspectival sub-functors)
**Definition.** F_i = π_i ∘ T for i ∈ {Form, LDS, DOF}. Each is a functor from 𝒞_Str to the i-th projection category.
**Located in.** §5.1 (F_math as sub-functor instance).
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
**Statement.** The contracted↔open axis is a DOF-structure governing navigational dynamics; quality-functional form in CT.
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

*Fifteen corollaries in four clusters: three axiom-descent clusters (I/II/III) plus one mechanism-descent cluster (IV) added 2026-04-27.*

### Cluster I — Substrate and Generativity (descends from A1)

**C1 — Concreteness of X.** X is in null(F_math) yet is the source of F_math-describable structure; X is concrete-without-materiality. *Located §8.1. Cited by philosophy, theology.*

**C2 — Generative Configuration for Perspective.** Perspectival positions are an A1.3 + A2.1 consequence; no separate metaphysical principle required. *Located §8.1. Cited by philosophy.*

**C3 — Null-Space Trace Illumination.** Streams in null(F_i) remain detectable via traces in dimensions where they are F_{D'}-in-range. *Located §8.1. Cited by philosophy of science, discovery-dynamics analyses.*

### Cluster II — Stream Structure and Navigation (descends from A2 + T3)

**C4 — Substrate-Constrained Perspectival Plurality.** Multiple F_i; all anchored to shared X; plurality constrained, not free. *Located §8.2. Cited by philosophy, sociology.*

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

### Cluster IV — Mechanism Consequences (descends from T4 + Promethean Configuration apparatus)

**C14 — Two-Mode Symmetry-Breaking.** T4's measurement-event has two modes: **resolution** (substrate has pre-existing multi-valued content; carrier selects a branch) and **generation** (substrate has pure symmetry; carrier produces content from the symmetry-break itself). Both are cases of *carriers break substrate symmetries*. The Promethean Configuration's foundational claim is that generation is primary; resolution is downstream of generation, requiring pre-existing branches that themselves arose from earlier generation. *Located §8.4. Cited by Physics (cosmology measurement), Computation (training dynamics), Coherent Body (immune response modes), Coherent Mind (decision vs. discovery).*

**C15 — Intervention-at-Symmetry-Layer.** From C14 + C2: substrate-content cannot be constrained without changing the substrate's symmetries; all intervention operates at the symmetry layer, not the content layer. Direct intervention on content is structurally impossible; intervention reshapes which symmetries are accessible to the substrate's carriers, and content emerges as the carrier breaks whatever symmetries are breakable. The framework's stance on intervention: the question is never "what content do you want" but "which symmetries do you remove and which do you preserve?" *Located §8.4. Cited by Coherent Body (medical), Coherent Mind (therapy/contemplative), Dynamic Organization (institutional design), Killing Form (regularization), Meridian (boundary conditions).*

---

## A.5 Coherence and Bias

### σ_struct
**Definition.** Coherence-axis tracking kind-closure engagement.
**Located in.** §7.2.
**Cited by.** All domain volumes.

### σ_info
**Definition.** Coherence-axis tracking trace-propagation. Operator via push_informational.
**Located in.** §7.2.
**Cited by.** All domain volumes with communication structure.

### Bias(S)
**Definition.** Signed measure on Ω_S induced by γ. See Appendix B for full treatment.
**Located in.** §6.4, Appendix B.
**Cited by.** All domain volumes (Step 5 of §10).

### A_S (entropy functional)
**Definition.** Shannon entropy of normalized Bias(S)_+ — the contracted-open axis formalized.
**Located in.** Appendix B.2.
**Cited by.** Psychology (attentional state), Computation (attention-distribution).

### Align(S, t)
**Definition.** Integral of Bias(S) over a neighborhood of σ(t); distinguishes contracted-coherent from contracted-failed.
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
**Statement.** Coherent multi-scale systems that maintain structural superposition until informed measurement collapses them outperform systems that collapse prematurely or incoherently.
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
**Definition.** Integral of the distance between σ(t) and σ*(t) over [t_0, t_1]. The Principle's outperformance metric.
**Located in.** §9.3, Appendix B.5.
**Cited by.** All domain volumes testing the Principle empirically.

### Self-reference closure
**Definition.** The observation that this volume's construction process itself instantiates the four Conditions — the framework describes its own making as a coherent process.
**Located in.** §9.5.
**Cited by.** Philosophy, Theology (framework self-grounding questions).

---

## A.7 Axioms and Bridges (short-form)

### A1 — Consciousness as Substrate
Substrate X is neutral-monist; non-reducible, non-factoring, all-potentials-realized; etymologically consciousness.
**§2.**

### A2 — Nested Streams and Navigation
Streams are localized perspectives in X; kind-stratified; cooperative-constituency ι ⊣ κ; experience = navigation; DAG-nested.
**§3.**

### A3 — Conscious Gravity
γ_S is the adaptive coalgebra representing internal DOF-gradient integration; continuous; stream-universal.
**§4.**

### Bridge #102 — Form factor-functor payload
**Form.** The content carried by Φ : 𝒞_Str → 𝒞_Form — Form as an independent axis of identity under the Triple.
**Located in.** §1.2 (Φ definition).
**Cited by.** Philosophy, Biology, Computation.

### Bridge #104 — Bootstrap Asymmetry
**Qualified form.** Organized dynamical loops within an existing framework require priming external to themselves.
**HIGH confidence for qualified form; MEDIUM for strict-universal.**
**Cited by.** Theology (on ultimacy/origin), Physics (initial-conditions problem), Philosophy (self-grounding questions).

### Bridge #107 — Content factor-functor payload
**Form.** The content carried by Ψ : 𝒞_Str → 𝒞_LDS — Content/substrate-phase as an independent axis of identity under the Triple.
**Located in.** §1.2 (Ψ definition).
**Cited by.** Physics, Biology, Computation (substrate-analysis volumes).

### Bridge #108 — Triple-derived bridge
**Form.** Form/Content/Carrier orthogonality with consistency constraints derivable from §1.
**Cited by.** Philosophy, Biology, Computation.

### Bridge #109 — Carrier factor-functor payload
**Form.** The content carried by Κ : 𝒞_Str → 𝒞_DOF — Carrier/scale-relational position as an independent axis of identity under the Triple.
**Located in.** §1.2 (Κ definition).
**Cited by.** Continuity volume especially; all domain volumes analyzing scale-relational position.

### Bridge #110 — Identity-Trajectory Triple
**Form.** T : 𝒞_Str → 𝒞_Form × 𝒞_LDS × 𝒞_DOF as principal identity-carrying functor.
**Cited by.** Continuity volume especially; all domain volumes via §1.

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
- **Capital Roman** for kinds (K) and functors (T, F_i)
- **Subscript S** indicates stream-specific quantities (Ω_S, γ_S, Bias(S))
- **Asterisk** on trajectory indicates γ-implied (σ*(t))

**The ITT factor-functors Φ, Ψ, Κ.** The three projection factor-functors of the Identity-Trajectory Triple (Form, Content, Carrier) are denoted by capital Greek letters as a structural set: Φ : 𝒞_Str → 𝒞_Form, Ψ : 𝒞_Str → 𝒞_LDS, Κ : 𝒞_Str → 𝒞_DOF. The capital Κ (Kappa, U+039A) is a distinct object from the stream-level lowercase κ (the cooperative-constituency right adjoint of A2.4) and from the Latin K used for stream-kind. Typesetters should preserve the capital Greek glyph; the three letters are chosen to travel together as a labelled Triple.

Domain volumes should preserve these conventions when citing into the Anchor; deviations should be flagged explicitly.
