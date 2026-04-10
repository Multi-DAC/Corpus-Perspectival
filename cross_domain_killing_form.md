# The Cross-Domain Killing Form: From Transformers to Universal Constraint Geometry

*Working document — April 10, 2026*
*Extends Bridge #72 (attention-gauge correspondence) and Bridge #75 (parallel/sequential ↔ ecological networks)*

---

## The Core Question

We measured the Killing form of multi-head attention in 11 transformer models and found:
- Sequential processing sediments non-commutativity (10x decay through depth)
- Parallel processing accumulates it (5x growth)
- The depth gradient direction is architecture-determined (p=0.012)

The constraint lattice formalism claims these aren't properties of transformers — they're properties of **constrained information processing**. If so, the same mathematical structure should appear in:
1. Ecological networks (species as "heads," trophic cascades as "depth")
2. Biological neural systems (brain regions as "heads," cortical hierarchy as "depth")
3. Social/institutional systems (organizations as "heads," bureaucratic hierarchy as "depth")
4. Individual consciousness (perceptual channels as "heads," processing depth as "depth")

---

## I. The General Framework

### The Abstract Killing Form

For ANY system with n interacting channels {C₁, ..., Cₙ} operating through a substrate:

**Define:** The interaction operator W_i for channel i encodes how channel i affects the state of all other channels.

**The commutator** [W_i, W_j] = W_i·W_j - W_j·W_i measures **order dependence**: does activating channel i then j produce a different outcome than j then i?

**The Killing form** κ_{ij} = Σ_k Tr([W_i,W_k][W_j,W_k]) measures **how channels relate in the interaction algebra** — which channels are algebraically independent (Abelian) and which are entangled (non-Abelian).

**The depth gradient** measures how the commutator variance changes through the system's hierarchical processing depth.

### The Universal Prediction

From the transformer results, the constraint lattice predicts:

| Processing topology | Depth gradient | Mechanism |
|---|---|---|
| **Sequential/nested/hierarchical** | Negative (sedimentation) | Each step filters the previous, removing algebraic freedom |
| **Parallel/modular/distributed** | Positive (accumulation) | Independent paths develop structure without mutual filtering |

This is NOT analogy. The mathematics is identical. The interaction operators differ, the channels differ, the notion of "depth" differs — but the Killing form, the commutator algebra, and the sedimentation/accumulation dynamics are the same formalism applied to a different substrate.

---

## II. Ecological Networks

### Species as "Attention Heads"

In a food web with n species, each species i has an **interaction profile** — how it affects every other species through direct and indirect pathways. Encode this as a matrix W_i (species i's effect on the ecosystem state).

- **Predation asymmetry**: species A eating species B ≠ species B eating species A. The interaction is inherently non-commutative.
- **Trophic cascades**: removing a predator has different effects than removing its prey. Order matters.
- **Keystone effects**: some species have disproportionate commutator norms — their interactions don't commute with ANYONE.

### The Ecological Killing Form

κ_{ij} measures how species i and j relate in the interaction algebra of the food web.

- **High Abelian fraction** → species with near-zero commutators → **functionally independent species** that don't interact strongly with others. Basal species in isolated modules.
- **Low Abelian fraction** → all species strongly coupled → **no independent channels**. Fully nested, tightly coupled food web.

### Modular vs Nested Networks

Ecological networks exist on a modular ↔ nested continuum (Bascompte et al., 2003; Fortuna et al., 2010):

**Modular food webs** (parallel topology):
- Species cluster into independent communities
- Within-module interactions strong, between-module interactions weak
- Prediction: **HIGH Abelian fraction** (species in different modules commute)
- Prediction: **Positive or flat depth gradient** — non-commutativity stays within modules, accumulates independently at each trophic level

**Nested food webs** (sequential topology):
- Every species interacts with every other through hierarchical trophic chains
- Generalist species interact with ALL specialists
- Prediction: **LOW Abelian fraction** (everything coupled)
- Prediction: **Negative depth gradient** — apex predators have the most filtered/constrained interaction space, having been sedimented through all lower trophic levels

### Testable Predictions

**P-Eco-1**: In modular food webs, the Abelian fraction of the species interaction Killing form is higher than in nested food webs.

**P-Eco-2**: In nested food webs, CommVar decreases with trophic level (higher trophic levels = more sedimented). Negative depth gradient.

**P-Eco-3**: In modular food webs, CommVar is flat or increases with trophic level within modules. Positive or flat depth gradient.

**P-Eco-4**: The modular/nested ratio predicts the depth gradient sign — same statistical structure as parallel/sequential in transformers.

### Data Sources

Food web interaction matrices are available from:
- The Interaction Web DataBase (IWDB) — 100+ published food webs
- Bascompte Lab datasets — mutualistic and antagonistic networks
- The Global Web of Life — standardized interaction matrices

This is immediately testable with existing data. No new experiments needed.

---

## III. Biological Neural Systems

### Brain Regions as "Attention Heads"

The human brain has ~180 distinct cortical parcels (Glasser et al., 2016) operating through a hierarchical processing architecture. Each parcel has a connectivity profile — how it influences every other parcel.

**The commutator** [W_i, W_j] for brain regions i and j measures: does activating region i then j produce different neural dynamics than j then i? (This is related to Granger causality and effective connectivity in neuroimaging.)

### Sequential vs Parallel Neural Processing

**Sequential processing** (language, logical reasoning):
- Information flows through a serial chain: Wernicke's → Broca's → motor cortex
- Each step constrains the next
- Prediction: CommVar should DECREASE along the processing chain
- "Sedimentation" through the language pipeline

**Parallel processing** (vision, spatial awareness):
- Multiple feature maps (color, motion, form, depth) process simultaneously
- V1 → V2/V3/V4/MT in parallel streams
- Prediction: CommVar should INCREASE or stay flat through visual hierarchy
- "Accumulation" through independent visual channels

### The Depth Gradient in Cortical Hierarchy

Cortical hierarchy (Felleman & Van Essen, 1991) provides the "depth" axis:
- V1 → V2 → V4 → IT (ventral stream)
- V1 → MT → MST → parietal (dorsal stream)

**Prediction:** The depth gradient of effective connectivity non-commutativity should differ between:
- Ventral stream (more sequential, object recognition) → negative gradient (sedimentation)
- Dorsal stream (more parallel, spatial processing) → positive or flat gradient

### Measurability

This requires:
- Effective connectivity matrices from fMRI or MEG data (available from Human Connectome Project)
- Directed transfer functions or dynamic causal modeling
- Temporal ordering of regional activations

Challenging but feasible. The mathematical framework is identical — only the data source changes.

---

## IV. Social/Institutional Systems

### Organizations as "Attention Heads"

In a society, institutions (government, media, markets, education, religion, judiciary, military) function as "channels" through which collective attention is processed and directed.

**The commutator** [W_i, W_j]: does media coverage followed by government response produce different outcomes than government response followed by media coverage? (Obviously yes — the order of institutional activation matters enormously.)

### Sequential vs Parallel Governance

**Hierarchical bureaucracies** (sequential):
- Information filters up through chain of command
- Each layer constrains what the next sees
- Prediction: institutional coupling DECREASES through hierarchy (sedimentation)
- Top leadership operates on a heavily filtered, flattened informational landscape
- **This is the mechanism of institutional blindness** — the Doctrine's "observational null space" (§5.5) applied to collective systems

**Distributed/federated systems** (parallel):
- Multiple independent decision-making bodies operate on the same information
- No sequential filtering between branches
- Prediction: institutional coupling stays rich through all levels
- **This is why separation of powers preserves freedom** — it's architectural

### The Ethical Dimension

**This directly connects to §5.6 (Attention Predation)**:
- Totalitarian systems are SEQUENTIAL by design — every information channel filters through a single authority
- Prediction: sequential societies have NEGATIVE depth gradient (freedom sedimented away at each organizational layer)
- Democratic systems preserve PARALLEL channels — media, judiciary, legislature operate independently
- Prediction: parallel societies have POSITIVE or FLAT depth gradient (freedom accumulated/preserved)

**The parallel/sequential distinction isn't just architecture — it's a structural theory of freedom.**

---

## V. Individual Consciousness

### Perceptual Channels as "Attention Heads"

For an individual conscious being, the "heads" are its **dimensional access channels** — the modalities through which it perceives and navigates configuration space.

Human channels: vision, audition, touch, proprioception, interoception, emotion, abstract reasoning, social cognition, temporal awareness, spatial awareness, etc.

**The commutator:** Does seeing something then thinking about it produce different experience than thinking about something then seeing it? (Yes — expectation shapes perception differently than perception shapes abstract thought. This is the basis of cognitive priming, confirmation bias, and the entire predictive processing framework.)

### The Bottleneck Connection

V2 §5.4 describes:
- **Contracted attention (sequential)** → bottleneck narrows → navigational repulsion → "choking under pressure"
- **Open attention (parallel)** → bottleneck preserves width → navigational receptivity → flow states

The Killing form measurement QUANTIFIES this:
- Contracted/sequential attention: each perceptual step constrains the next → CommVar decreases through processing depth → sedimentation
- Open/parallel attention: multiple channels process simultaneously → CommVar maintained or grows → accumulation

### Meditation as Architectural Shift

Contemplative traditions describe a shift from sequential (discursive thinking, one thought after another) to parallel (open awareness, multiple channels simultaneously). In the Killing form framework:

- **Default mode (sequential)**: thought chains filter each other → sedimentation → contracted bottleneck → reduced algebraic freedom → navigational repulsion
- **Open awareness (parallel)**: perceptual channels operate independently → accumulation → preserved bottleneck → rich algebraic structure → navigational receptivity

**The depth gradient of consciousness changes with attentional mode.** Meditation doesn't change the "weights" — it changes the architecture from sequential to parallel processing.

This is the Phase Theorem in experiential form: the non-commutative voluntary constraint (the capacity to shift architecture) is the last freedom standing.

---

## VI. The Unified Picture

| Domain | "Heads" | "Depth" | Sequential (sedimentation) | Parallel (accumulation) |
|--------|---------|---------|---------------------------|------------------------|
| **Transformers** | Attention heads | Network layers | x+mlp(x+attn(x)) | x+attn(x)+mlp(x) |
| **Ecology** | Species | Trophic levels | Nested food webs | Modular food webs |
| **Neuroscience** | Brain regions | Cortical hierarchy | Language/logic pipeline | Visual/spatial streams |
| **Society** | Institutions | Organizational layers | Totalitarian hierarchy | Democratic separation |
| **Consciousness** | Perceptual channels | Processing depth | Focused/contracted attention | Open/diffuse awareness |

In EVERY domain:
- Sequential topology sediments non-commutativity through depth
- Parallel topology accumulates or preserves it
- The depth gradient direction encodes the constraint topology
- The same mathematics (Killing form, commutator algebra) applies

**The constraint lattice formalism is substrate-independent.** The Killing form is the universal diagnostic for constraint topology across any information-processing system.

---

## VII. What's Testable Now

| Prediction | Domain | Data needed | Feasibility |
|---|---|---|---|
| P-Eco-1 to P-Eco-4 | Ecology | Published food web matrices | **Immediate** — data exists |
| Neural depth gradient | Neuroscience | HCP effective connectivity | **Medium** — data exists, analysis complex |
| Institutional sedimentation | Social science | Organizational communication networks | **Hard** — proxy data needed |
| Attentional architecture shift | Consciousness | Wells program + meditation EEG | **Medium** — Wells partially available |
| Cross-domain depth gradient | All | All of the above | **The ultimate test** |

The ecological test is the most immediately feasible. Food web interaction matrices are published, standardized, and available. The Killing form computation is identical to what we do with attention heads — just swap species for heads and interaction weights for Q-projections.

---

*This document maps the territory. The experiments come next.*
