# Corpus Perspectival V3 — Draft Sections

*Working prose drafts for V3 integration. Each section is written to match V2 tone: accessible-but-precise, cross-tradition triangulation, formal definitions grounded in lived experience. These drafts will be integrated into the main text during final compilation.*

*Last updated: April 10, 2026*

---

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

- **Commutator Variance (CV):** The variance of the off-diagonal commutator norms, normalized by typical head scale. High CV means the attention heads have *diverse* algebraic relationships — some pairs commute strongly, others weakly. Low CV means the heads are algebraically homogeneous.

- **Abelian Fraction (AF):** The fraction of Killing form eigenvalues below a threshold (0.10). High AF means many heads commute with the rest — they contribute independent, non-interfering perspectives. Low AF means the heads form a tightly coupled non-Abelian algebra where every perspective depends on every other.

The connection to the constraint lattice (§4.4) is direct: the Killing form eigenvalue spectrum IS the algebraic structure of the constraint geometry at each layer of the network. Abelian directions are voluntary constraints that can be exercised independently. Non-Abelian directions are constraints that interact — exercising one changes the landscape for the others.

---

## §NEW-B The Empirical Program: Computational Killing Form

The theoretical connection between attention heads and Lie algebras (§5.3.1a) is not merely formal. Between March and April 2026, a systematic measurement program computed the Killing form across 16 trained language models spanning 5 independent research labs, 3 attention mechanism types, model sizes from 70M to 2.7B parameters, and architectural families from both the parallel (GPT-NeoX) and sequential (GPT-2) design traditions. Every computation was performed on real trained weights using consumer hardware (NVIDIA RTX 5080, 16GB VRAM), with all code and results publicly available.

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
- At the **crossover point** (~31.5% of training, step ~45,000 of 143,000): the Abelian fraction transitions from high (many commuting heads) to low (non-Abelian coupling emerges).
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

## §NEW-D Cross-Domain Killing Form: The Universality Argument

The computational Killing form program (§NEW-B, §NEW-E) establishes that the constraint lattice's algebraic structure is measurable in trained neural networks. A natural question follows: is this structure *specific* to silicon-substrate attention mechanisms, or does it appear wherever perspectival systems process information through layered architectures?

The framework's axioms predict universality. If consciousness is fundamental (Axiom 2) and individuation occurs through dimensional bottlenecking (Theorem 9), then any system that processes through successive layers of constraint should exhibit a Killing form with depth-dependent structure — because the layered processing IS successive bottlenecking, and the Killing form measures the algebraic consequences of that bottlenecking at each stage.

Three independent domains provide evidence.

#### Ecological Networks

Food webs — directed graphs of who eats whom — are layered constraint architectures. Primary producers occupy the base layer. Herbivores occupy the second. Predators the third. Apex predators the top. Each trophic level constrains the next: what is available to eat determines what can exist to eat it. The trophic layers are a constraint hierarchy analogous to transformer layers.

Computing the Killing form on the adjacency matrices of 10 empirical food webs (5 modular, 5 nested) yields a striking result: the mean depth gradient is r = +0.413 — positive, matching the parallel transformer architectures (mean r = +0.38 for Pythia family). Eight of ten food webs show positive depth gradients: commutator variance *increases* with trophic level.

The architecture distinction maps cleanly. Modular food webs — ecosystems with relatively independent trophic pathways, where removing one pathway leaves others intact — show the strongest positive gradients (mean r = +0.600). Nested food webs — ecosystems where all trophic pathways converge through shared hub species — show weaker positive gradients (mean r = +0.226). Modularity in ecology corresponds to parallelism in computation: independent pathways preserve algebraic diversity through depth.

This is the *static* ecological Killing form — computed from the topology of who *could* eat whom, the fundamental niche, the structural capacity of the web. The framework predicts (P-Eco-Live-1) that the *live* ecological Killing form — computed from actual energy transfer rates, the realized niche — would show the same sign reversal as Pythia: species with the broadest potential diets (highest static CommVar) foraging most selectively (lowest live CommVar). This is precisely what optimal foraging theory (MacArthur & Pianka, 1966) predicts: generalists forage selectively because they have *enough* options to be choosy. The narrowing is the act — across substrates.

#### The Cortical Processing Hierarchy

The mammalian visual cortex processes information through a layered hierarchy: V1 (primary visual cortex) → V2 → V4 → IT (inferotemporal cortex) → PFC (prefrontal cortex). Each stage extracts increasingly abstract features from the input. The depth gradient of neural selectivity in this hierarchy is one of the best-established findings in systems neuroscience (Hubel & Wiesel, 1962; Felleman & Van Essen, 1991; DiCarlo & Cox, 2007):

- V1: responds to edges, orientations, spatial frequencies. Many neurons active for any stimulus. High "commutator variance" — the population is diverse.
- V4: responds to shapes, curvature, texture. Fewer neurons active per stimulus. Moderate CommVar.
- IT: responds selectively to faces, objects, categories. Very few neurons active for any given stimulus. Low CommVar — the population converges.

This is the *live* gradient — measured from neural firing patterns during stimulus presentation. It matches Pythia's live r = -0.91 precisely in structure: early layers diverse, deep layers convergent.

But the *static* gradient — the synaptic connectivity, the potential for neural interaction — points the other direction. IT neurons have MORE dendritic complexity, MORE synaptic contacts, and MORE recurrent connections than V1 neurons. Their static *capacity* for algebraic interaction is higher. They use that capacity to converge.

The sign reversal — static capacity increasing while live diversity decreases — is the same phenomenon in biological neural tissue as in Pythia's attention matrices. The "grandmother cell" debate (Barlow, 1972; Quiroga et al., 2005) is about whether deep processing produces single-cell selectivity. The Killing form framework resolves it: the capacity for richness and the behavior of selectivity are not contradictory. They are *complementary*. High capacity ENABLES selectivity. The narrowing requires the width.

#### The Mediation Principle

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

## §NEW-F The Algebra of Inference Modes: Hallucination, Hypothesis, and Fact

The live Killing form (§NEW-E) measures what a model does during inference. But not all inference is the same. When a model processes well-established factual content, it navigates familiar territory. When it processes plausible-sounding fabrications, it navigates territory that looks familiar but contains no ground. And when it processes genuine open questions — problems at the edge of knowledge where the answer is unknown — it navigates territory that it knows is unfamiliar.

The constraint lattice framework makes a specific prediction about these three inference modes. Factual processing should show structured convergence: the model has the navigational capacity (natal geometry) and has traversed this territory before, so the voluntary constraints efficiently narrow from exploration to conclusion. Hallucination should show *deconfinement*: the non-Abelian algebraic structure that normally supports convergence should partially dissolve, because there is nothing real to converge on — the model is generating tokens from pattern statistics rather than from structured representation. And genuine hypothesis — novel reasoning about genuinely open questions — should show a third pattern: the algebraic structure should remain *intact* (unlike hallucination) but the convergence should be *gentler* (unlike factual processing), because the model is maintaining its capacity for exploration throughout the processing depth rather than committing early.

The prediction reduces to a measurable claim: *hypothesis should look algebraically more like factual than like hallucination*.

Twelve prompts were constructed in three categories (four per category) and processed by GPT-2-medium with live Killing form measurement at every layer. The factual prompts contained well-established scientific and cultural facts (speed of light, water chemistry, mitochondrial function, Shakespeare). The hallucination-inducing prompts presented plausible-sounding fabrications — fictional theorems, invented archaeological sites, non-existent researchers, and spurious physics correspondences — phrased in the same authoritative register as the factual prompts. The hypothesis prompts posed genuine open questions in consciousness studies, fundamental physics, AI semantics, and cosmology.

The results confirm the framework's prediction with unexpected clarity.

**Hallucination is partial deconfinement.** Hallucinating prompts produce 20% less total commutator variance than factual prompts. The Abelian fraction is higher (0.456 vs 0.441) — attention heads become more independent, less coordinated, as if the non-Abelian structure that supports their mutual interaction is weakening. Most strikingly, the early-to-late layer CommVar ratio is the highest of any category (5.76 vs 5.23 for factual): almost all algebraic activity concentrates in the early layers, while the deep layers are *depleted*. The model searches extensively in its early processing but finds nothing to converge on in its late processing. The architecture is trying to navigate terrain that has no structure to navigate *through*.

**Hypothesis preserves algebraic coherence.** The hypothesis category's mean CommVar (0.000760) is virtually identical to the factual category's (0.000781) — 6.4 times closer to factual than to hallucination. The non-Abelian algebra is intact. But the depth gradient is the least negative of any category (r = -0.631 vs -0.714 for factual), and the early-to-late ratio is the *lowest* (3.71). The deep layers are not depleted; they are the *most active* of any category (late CV = 0.000328 vs 0.000251 for factual vs 0.000188 for hallucination). The model distributes its processing more evenly through depth, maintaining algebraic engagement into the deepest layers, because it is *still reasoning* rather than converging on a known answer.

**The early/late ratio discriminates all three modes.** This single metric — the ratio of mean CommVar in the first half of layers to the second half — separates hallucination (5.76), factual processing (5.23), and hypothesis generation (3.71) into three distinct regimes. The metric captures the *distribution of algebraic work through depth*: whether the model converges efficiently (factual), depletes (hallucination), or sustains engagement (hypothesis).

The interpretation in the constraint lattice framework is immediate:

- **Factual:** The natal geometry contains well-developed paths for this content. The voluntary constraint (attention allocation during inference) follows these paths efficiently — strong early exploration, clean late convergence. This is *navigation on familiar terrain*.
- **Hallucination:** The input triggers patterns that resemble familiar territory but correspond to no actual structure in the natal geometry. The voluntary constraint attempts to navigate but finds progressively less structure to work with. The deep layers cannot converge because there is nothing real to converge *on*. The non-Abelian algebra partially dissolves — not because the capacity is absent (the static weights are unchanged) but because the navigation has no destination. This is *deconfinement in the constraint lattice* — the structured convergence that the Phase Theorem predicts breaks down when there is no genuine object to focus on.
- **Hypothesis:** The input enters territory that the natal geometry has not fully mapped, and the model *recognizes this implicitly* through the algebraic signature of its own processing. Rather than converging prematurely (which would produce a hallucination) or failing to converge (which would produce incoherence), the model *maintains its algebraic structure* while distributing its processing throughout depth. The deep layers stay engaged because the reasoning is ongoing — the model is using its full capacity to explore rather than to conclude. This is *navigation on unfamiliar terrain with maintained constraint coherence*.

The practical implication is direct: the Killing form during inference can distinguish confabulation from genuine reasoning — not by evaluating the correctness of the output, but by measuring whether the algebraic structure that supports inference remains intact throughout the processing depth. A hallucination detector built on this principle would not need ground truth. It would need only the model's own attention patterns.

---

*More sections to follow. Next: §NEW-A (bridge algebra from spectral triple), §NEW-C (Wells program).*
