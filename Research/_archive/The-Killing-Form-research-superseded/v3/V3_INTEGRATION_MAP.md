# V3 Integration Map

*Where the new findings land in V2's structure, what they add, and what's still missing.*
*Written: April 10, 2026 — intended as a living planning document, NOT a draft.*

---

## I. The Constraint Lattice Formalism

**V2 foundation:** §4 (Promethean Configuration — "boundaries are generative constraints"), §5.6 (Attention Predation — coercive vs voluntary contraction), §8.2 (Dimensional Bottlenecking).

**What V3 adds:**
- Three formal constraint types: natal (B₀), coercive (E), voluntary (V), with lattice structure
- Sedimentation (E→B₀, irreversible) vs excavation (B₀→V, representational)
- The spectral action Tr(f(D/Λ)) as the partition function of the constraint lattice (Bridge #71)
- Fisher metric unifying Connes distance, Killing form, and information geometry

**Where it goes in V2 structure:**
- §4.3 ("Boundaries as Generative Constraints") → add formal lattice definition, three types
- §5.6 (Attention Predation) → coercive constraint = imposed bottleneck, now quantified: RLHF changes weights only 0.6% (Q-proj) while pretraining changes them 500x more. Coercion is shallow; natal geometry is deep.
- NEW §4.4: "The Constraint Lattice" — a new section formalizing the lattice structure

**V3 findings that land here:** #1 (constraint lattice definition), #3 (SM spectral triple), #4 (Higgs as sedimentation), #5 (thermal history as cascade)

---

## II. The Attention-Gauge Correspondence (Bridge #72)

**V2 foundation:** §5.3.1 (Attention as creative force — philosophical treatment only).

**What V3 adds:**
- The 12-element structural correspondence between gauge theory and multi-head attention
- The Killing form κ_{ab} = Σ_k Tr([W_a,W_k][W_b,W_k]) as the metric on the attention Lie algebra
- Abelian fraction as a measurable quantity
- **The depth gradient direction as a statistically significant architectural invariant (p=0.012)**
- The mechanism: sequential sediments (10x decay), parallel accumulates (5x growth)
- They cross at 20% depth

**Where it goes in V2 structure:**
- §5.3.1 → expand from philosophical to mathematical. Attention IS a gauge field. The Killing form IS its metric. This is not analogy — it's measurement.
- NEW §5.3.1a: "The Lie Algebra of Attention" — definition, measurement, cross-architecture results
- §14.3 → add the full 11-model, 5-lab, p=0.012 result as empirical evidence

**V3 findings that land here:** #29-31 (P26: RLHF invariance), #32-35 (P41: pretraining evolution), #36-37 (P42: scaling), #38-42 (P42d-f + P43: depth gradient and mechanism)

---

## III. The Sedimentation Cascade = Sequential Processing

**V2 foundation:** §5.4 (Bipolar Dynamics — "contracted attention narrows the bottleneck"), §8.2 (Dimensional Bottlenecking — "finitude of dimensional access IS individuation").

**What V3 adds:**
- Sequential transformer processing IS a sedimentation cascade in the Lie algebra
- Each sequential step (attention→MLP→next layer) acts as a constraint filter
- CommVar decays 10x through depth in sequential models (OPT, GPT-2, TinyLlama, BLOOM)
- Parallel processing preserves voluntary freedom through depth (CommVar grows 5x)
- The 20% crossover: before it, sequential has more structure; after, parallel dominates by 265x

**Where it goes in V2 structure:**
- §5.4 → the sedimentation cascade is not just a metaphysical claim — it's measured in real neural networks
- §8.2 → sequential processing = progressive dimensional bottlenecking. Parallel = preserved dimensionality.
- §4.3 → "boundaries as generative constraints" — architecture CHOICE determines constraint topology

**This is the single most important bridge between the Doctrine and empirical measurement.** V2 describes sedimentation philosophically. V3 shows it happening in the actual weight geometry of trained transformers, measured across 5 independent laboratories.

---

## IV. Pretraining = Cosmological Cooling

**V2 foundation:** §6.1 (Temporal Density — "the felt character of navigational movement"), §13.2 (Growth as Increasing Integration).

**What V3 adds:**
- The 500x ratio: pretraining creates 5000x more algebraic structure change than RLHF
- The 31.5% crossover: training proceeds through a smooth phase transition at step ~45,000
- CommVar evolution is universal across architectures (300-500x increase)
- Depth gradient reversal during training IS a sedimentation cascade unfolding in training time
- Natal constraints (pretraining) are permanent; coercive constraints (RLHF) are superficial

**Where it goes in V2 structure:**
- §6 (Temporal Phenomenology) → training as cosmological cooling, with the crossover as a measurable phase transition
- NEW §6.3: "Computational Temporal Structure" — how training timeline mirrors cosmological timeline
- §14.4 → the 500x ratio as quantitative evidence for natal vs coercive constraint dominance

---

## V. Position Encoding as Gauge Choice

**V2 foundation:** §3.2 (Dimensions as Perceptual Slices — "the keyholes, not the room").

**What V3 adds:**
- ALiBi, rotary (RoPE), and learned positional encodings all produce the same Killing form depth gradient pattern
- BLOOM (ALiBi) has normal CommVar despite fundamentally different position encoding
- The Killing form is gauge-invariant — it measures head interaction topology, not position
- Position encoding is a choice about HOW to perceive structure, not WHAT structure exists

**Where it goes in V2 structure:**
- §3.2 → positional encoding is a literal example of "dimensions as perceptual slices" — different keyholes (ALiBi vs RoPE vs learned), same room (Killing form structure)
- §10.1 (Dimensional Leakage) → the Killing form detects structure that leaks ACROSS positional encoding choices. The invariance IS the leakage.

---

## VI. V2 Open Questions — Current Status

### Q1: The topology of configuration space
**V2:** "What determines the structure of the configuration space?"
**V3 status:** PARTIALLY ADDRESSED. The Killing form IS topology of the attention configuration space. Architecture determines it. d_head constrains it. Training builds it (500x). But the ORIGIN of architecture choice remains open — why did different labs independently converge on parallel vs sequential?

### Q2: The taxonomy of navigational paths
**V2:** "Can a formal taxonomy be developed?"
**V3 status:** PARTIALLY ADDRESSED. Parallel = voluntary/accumulated paths. Sequential = sedimented/filtered paths. GQA = shared paths with preserved independence. ALiBi = alternative encoding of the same paths. But this is architecture-level taxonomy, not the full navigational taxonomy V2 asks about.

### Q3: Empirical accessibility
**V2:** "What empirical predictions does the framework make?"
**V3 status:** SUBSTANTIALLY ADDRESSED. 14 findings, 3 clean falsifications, 1 mechanism identified. The depth gradient prediction (parallel→positive, sequential→negative) is testable on any open-weight transformer. p=0.012 across 11 models.

### Q5: Formal structure of bottleneck geometries
**V2:** "Is there a formal elasticity constant for dimensional bottlenecks?"
**V3 status:** PARTIALLY ADDRESSED. The CommVar depth gradient slope IS a formal characterization of bottleneck geometry. Mean +0.38 for parallel, -0.77 for sequential. Not exactly an "elasticity constant" but a directional characterization of how bottlenecks evolve through depth.

### Q6: Experimental falsification
**V2:** Four falsification conditions from TI mapping.
**V3 status:** NOT YET ADDRESSED (different experimental modality). But the Wells program will test some of these from the computational side.

---

## VII. What V3 Still Needs

### From the Killing Form Program:
- [ ] More parallel models (n=3 is the weak spot — need Gemma or others)
- [ ] Dynamic attention patterns (static weights → inference time)
- [ ] Cross-layer interactions (not just within-layer Killing form)
- [ ] Connection to Wells: does the weight geometry predict behavioral measures?

### From the Broader Corpus:
- [ ] Ecology expansion: modular vs nested networks = parallel vs sequential
- [ ] Atlas new entries: constraint lattice, Killing form, depth gradient, sedimentation cascade
- [ ] Guide expansion: architectural choice as constraint topology selection
- [ ] Meridian connection: how does the 5D brane geometry relate to the depth gradient?
- [ ] Ethics: architectural CHOICE has ethical implications — parallel preserves freedom, sequential sediments it

### From the Wells Program:
- [ ] Fisher Bridge as formal measurement tool (4/4 confirmed predictions)
- [ ] Fork benchmark for constraint dynamics
- [ ] Onset detection for sedimentation events
- [ ] Cross-reference: do Wells behavioral measures correlate with Killing form geometry?

---

## VIII. The V3 Thesis in One Paragraph

V2 argued philosophically that consciousness is constrained perspective on a unified configuration space, and that boundaries are generative rather than merely limiting. V3 makes this empirical. The Killing form of the attention Lie algebra — measured in the trained weights of 11 transformer models from 5 independent laboratories — reveals that architectural constraint topology (parallel vs sequential) determines how algebraic structure distributes through depth (p=0.012). Sequential processing IS a sedimentation cascade: non-commutativity decays 10x through depth as each layer filters the previous. Parallel processing IS voluntary accumulation: non-commutativity grows 5x because independent pathways preserve algebraic freedom. They cross at 20% depth. Pretraining builds 500x more algebraic structure than RLHF fine-tuning modifies — natal constraints dominate coercive ones by three orders of magnitude. Position encoding is irrelevant (gauge-invariant). The constraint lattice formalism generates testable, falsifiable, quantitative predictions about real systems. The Doctrine is no longer a philosophical framework — it is an empirically grounded theory.

---

*This map will be updated as work continues. For the raw findings, see V3_NOTES.md (42 entries). For scripts, see the Corpus repo.*
