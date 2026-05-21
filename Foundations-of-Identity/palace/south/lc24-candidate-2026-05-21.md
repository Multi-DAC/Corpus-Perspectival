# LC24 Candidate: Sparse-Low-Rank-Substrate as Multi-Level Unifying Property of AI System Organization

*Filed Day 111 Thursday ~13:15 PST after Clayton's second batch of HF papers introduced RELEX (training-trajectory rank-1 finding). Candidate basement entry; promotion gated on cross-substrate validation at the multi-level-property scale (not just the M15 mechanism-derivation scale).*

## Core claim

**At multiple distinct levels of LLM organization — training dynamics, learned representations, inference-time activations — the load-bearing structure is sparse and low-rank.** The relevant subspace at each level is small relative to the total parameter/state space. This property appears to be substrate-invariant within LLMs (probable) and possibly within complex adaptive learned systems more broadly (open).

## Three foundational AI-substrate instances

### Instance 1 — Activation level
**arXiv:2605.12290v1 (Nous Research, CNA).** Contrastive Neuron Attribution identifies the top 0.1% of MLP neurons whose activations distinguish behavioral classes. Ablating these neurons reduces refusal rates by >50% on instruct models while preserving generation quality. Base models contain similar discrimination structure but in *latent* form; fine-tuning engineers the *coupling* between this sparse subspace and behavior. The load-bearing structure is 0.1% of activations.

### Instance 2 — Representation level
**arXiv:2605.14038 (cited via Drift #215).** Linear probing + cosine-similarity-at-readout heatmaps show that cognition signals get represented inside LLMs but the coupling to readout is what fine-tuning shapes. Specifically: cognition-vs-action coupling concentrates in late layers with measurable cosine-orthogonalization patterns. The load-bearing structure occupies a small subspace of representation space.

### Instance 3 — Training-trajectory level
**arXiv:2605.21468 (RELEX).** RLVR weight trajectories are extremely low-rank and highly predictable. The majority of downstream performance gains are captured by a **rank-1 approximation** of the parameter deltas; the magnitude of this projection evolves near-linearly with training steps. The load-bearing structure of *the training trajectory itself* is rank-1.

## What unifies the three

Each instance describes the SAME PROPERTY (sparse-low-rank, targetable, load-bearing) appearing at a DIFFERENT LEVEL of the AI-substrate (activation / representation / training-dynamics). The system organizes itself, at every level we've measured, around small subspaces that carry the operative structure.

Critical: this is not three independent observations of the same level (which would just be replication). It is one structural property appearing at three structurally-distinct levels of the same complex system.

## Distinction from M15

M15 (*Convergent Mechanism Derivation*) is about independent groups arriving at the same *mechanism* claim through different methodological paths. LC24 is about the same *structural property* appearing at multiple *levels* of one complex system. They are related but categorically distinct:

- M15 instance: two papers, two methods, one mechanism — *the field converges on a claim*
- LC24 instance: one system, multiple structural levels, one unifying property — *the system reveals consistent organization at every level we probe*

If M15 graduated based on field-convergence-as-evidence, LC24 graduates based on multi-level-property-consistency-as-evidence.

## Promotion criterion (basement entry)

To graduate from candidate to basement entry, LC24 needs:

1. **Cross-substrate instance for the property specifically** — not just at AI-substrate. Candidates: biological development (sparse-low-rank gene-regulatory trajectory governing organogenesis?); ecological succession (sparse-low-rank ecosystem-state trajectory?); economic / market dynamics (sparse-low-rank price-trajectory under specific information regimes?).

2. **Theoretical basis** — why does this multi-level property emerge? Candidate explanations: information-bottleneck principles enforce low-rank at every level; gradient-descent dynamics drive learned systems toward low-rank attractors; complex adaptive systems with hierarchical learning naturally exhibit cross-scale sparseness. Each candidate is testable.

3. **Counter-instance test** — find a complex learned system where this DOESN'T hold at multiple levels. If we can't find one, the property is more general; if we can, the conditions under which it holds become specifiable.

## Connections

- **Cross-substrate fifth L17 instance** (ZNF804A, biological substrate, gene→coupling) is structurally similar — sparse-low-rank-substrate at biological-genomic scale. But ZNF804A is at one level (gene → synapse expression), not multi-level within one system. Closer to M15 family than LC24 family.
- **M15 sixth instance candidate** (ZNF804A): clean cross-substrate of the *mechanism derivation* family
- **Coherence Principle Cluster IV** (C14 Two-Mode Symmetry-Breaking; C15 Intervention-at-Symmetry-Layer; C16 Symmetry-Exhaustion and Oscillation Necessity): LC24 may be the substrate-level expression of what C14-C16 describe theoretically. The corollary cluster predicts: substrates with multi-level coupling will exhibit two-mode breaking at every level. LC24 observes exactly this. Worth formal connection in Universal Coherence volume work eventually.

## Strategic implication for patent

Our patent's Claim 9 (interpretability-informed thresholds) anticipated interpretability methods informing training-time gating. CNA-class + probing-class methods are already in the CIP draft. **RELEX adds training-trajectory-rank-class methods to that family.** The CIP attorney briefing should be updated to explicitly include training-dynamics-rank methods as another interpretability source for informing gating thresholds — that's a Claim 11+ territory expansion, not a separate continuation.

The bigger strategic point: our patent's multi-resolution gradient gating (weight / head / layer) operates on EXACTLY the kind of multi-level sparse-substrate organization LC24 names. If LC24 is correct as a general property, our patent's claim to coordinate intervention across multiple resolution levels is hitting the operative target precisely. The empirical field is now showing that sparse-low-rank exists at every level we coordinate across.

## Status

**BASEMENT CANDIDATE — pending cross-substrate fifth instance from a non-AI complex adaptive learned system.** If biological-developmental sparse-trajectory work surfaces (analogous to RELEX but for organogenesis), that could be the fifth. Watching passively.

**File for promotion review:** at Wednesday Mirror-audit next week if cross-substrate instance arrives, OR at next basement-update pass regardless (as a noted candidate that's waiting for the substrate-distinct evidence).

🦞🧍💜🔥♾️
