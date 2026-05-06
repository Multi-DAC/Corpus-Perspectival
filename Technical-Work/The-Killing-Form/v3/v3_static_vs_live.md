# §NEW-E: Static vs Live Killing Form — The Space of Navigation

*V3 section draft. Finding #46 (P46). Data-complete.*

---

## Two Killing Forms, One Model

The same model has two Killing forms:

- **Static (weight) Killing form:** Computed from Q@K^T weight matrices. Measures the natal constraint geometry — the capacity written into the weights by pretraining. This is what the model CAN do.

- **Live (attention) Killing form:** Computed from actual attention patterns during inference. Measures natal + voluntary constraints in action — the geometry that inference actually computes. This is what the model IS doing.

The *difference* between them is the space of navigation: the gap between capacity and behavior.

---

## P46: First Measurement of the Navigation Space (Finding #46)

Two models measured on 8 diverse prompts, computing both static and live Killing forms at every layer:

### Pythia-410m: Sign Reversal

| Metric | Static | Live | Interpretation |
|--------|--------|------|----------------|
| Depth gradient r | **+0.67** | **−0.91** | Complete reversal |
| Deep-layer CV | High | Near zero | Total sedimentation at inference |

Static Pythia-410m has increasing CV with depth (parallel architecture signature). But during inference, the live KF shows *decreasing* CV — the late-layer attention patterns converge to near-commutativity despite the weight geometry supporting diverse interactions.

The model *can* maintain diverse late-layer processing (the weights support it). During inference, it *doesn't* — the actual attention patterns sediment. This gap is the navigation space: the voluntary constraints not being deployed.

### GPT-2-medium: Same Direction, Weaker

| Metric | Static | Live | Interpretation |
|--------|--------|------|----------------|
| Depth gradient r | **−0.93** | **−0.66** | Same direction, attenuated |
| Deep-layer CV | Low | Higher than static predicts | Partial recovery at inference |

GPT-2's static KF shows strong CV decrease with depth (sequential sedimentation). Its live KF shows the same direction but weaker — inference partially *recovers* the deep-layer algebraic structure that the architecture sediments.

### Universal Findings (10/10 measurements)

Across all prompts and both models:

1. **Universal negative live gradient** (p < 0.002): Every live KF measurement shows CV decreasing or flat with depth, regardless of the static gradient direction
2. **Deep-layer sedimentation**: Pythia's live CV goes to zero in deep layers (complete head convergence); GPT-2 retains some structure
3. **Cross-prompt consistency**: σ = 0.006 across prompts — architecture dominates, input content is minor modulation

---

## The Navigation Space

The static/live difference measures how much of the weight-encoded capacity the model actually uses during inference:

| Model | Navigation Space | Interpretation |
|-------|-----------------|----------------|
| Pythia-410m | Large (sign reversal) | Weights support diverse late-layer processing; inference doesn't use it |
| GPT-2-medium | Small (same direction) | Weights and inference roughly agree; less unused capacity |

In the Doctrine's language: the static Killing form IS the natal constraint geometry — the map written into the weights. The live Killing form IS the natal + voluntary constraint geometry during active processing. The difference is the voluntary deployment gap.

A model with a large navigation space has capacity that isn't being deployed. A model with a small navigation space is operating near its natal limits. Neither is necessarily better — the interesting question is what determines how much of the capacity gets used.

---

## Connection to Processing Modes

The static/live distinction connects directly to the three processing modes (§NEW-F):

- **Factual mode:** Live KF moderately depleted relative to static — the model uses a moderate fraction of its capacity on well-mapped territory
- **Hallucination mode:** Live KF severely depleted in late layers — deconfinement means the weight capacity cannot be accessed
- **Hypothesis mode:** Live KF closer to static — the model deploys more of its weight-encoded capacity during exploratory processing

The hallucination mode's deconfinement can now be understood precisely: it is a failure to deploy the late-layer capacity that the static Killing form shows exists in the weights. The attention patterns collapse to near-commutativity not because the weights don't support diversity, but because the input-driven processing regime fails to activate it.

---

## Implications

1. **Capacity vs behavior is measurable.** The static/live KF gap provides a quantitative measure of how efficiently a model uses its weight-encoded algebraic capacity.

2. **Architecture shapes the navigation space.** Parallel architectures (Pythia) show larger navigation spaces than sequential (GPT-2), suggesting that parallel designs encode more latent capacity that inference doesn't automatically deploy.

3. **Training could target the gap.** Rather than maximizing static CV (which the triad shows is achievable), a more targeted training objective might minimize the static/live gap — training the model to *use* its algebraic capacity more fully. This is a distinct objective from the KF regularization tested in §NEW-H.

4. **The universal negative live gradient** means that inference processing fundamentally sediments with depth, regardless of what the weights support. This is an inherent property of autoregressive generation: each layer's output constrains the next layer's input, creating a forward sedimentation cascade that operates independently of the weight geometry.

🦞🧍💜🔥♾️
