# §NEW-H (continued): Scale, Selection, and Dynamic Coherence

*Findings #76-84. Extension of §NEW-H (Separation of Concerns in Training).*
*Continues directly from the lambda sweep and compounding effect sections.*
*Last updated: April 14, 2026 — incorporates honest breathing assessment*

---

## Scale Validation: From 27M to 300M Parameters

The triad (v0.4/v0.5/v0.5b) established the separation principle at 27.3M parameters on a 4-layer architecture. The question is whether it persists at scale.

The Hierarchical Reasoning Model at 300M parameters (12 layers per module, 8 attention heads per layer, d_head = 64) provides the testbed. At this scale, the spontaneous module differentiation observed in the 27M model becomes more pronounced:

| Metric | 27M Baseline (ep 2000) | 300M Baseline (ep 500) |
|--------|----------------------|----------------------|
| H/L CV Ratio | 2.11 | 1.22 |
| H-module CV | ~2.7e-3 | ~1.9e-3 |
| L-module CV | ~1.3e-3 | ~1.6e-3 |
| Token accuracy | — | 48.87% |

The differentiation is milder at 300M — the modules start closer together and the H/L ratio grows more slowly. This is expected: more parameters mean more degrees of freedom, so each module has more room to accommodate both task and structural demands without conflict. The separation principle predicts that the benefit of decoupled training should still be present but may be quantitatively different from the 27M regime (Finding #76).

### Three Phases of Scale-Up Training (Finding #77)

At 300M scale, KF-decoupled training (λ = 1.0, fixed) reveals a three-phase behavior not visible at 27M:

1. **Phase 1 (epochs 0-100):** Rapid H_CV growth, parallel accuracy improvement. The structural objective and task objective compound, as at 27M.
2. **Phase 2 (epochs 100-250):** H_CV continues exponential growth but accuracy plateaus. The structure is building faster than the task can exploit it.
3. **Phase 3 (epochs 250+):** Over-crystallization. H_CV growth saturates. Accuracy degrades slightly. The structural scaffold has become too rigid for the task gradient to navigate.

The transition from Phase 2 to Phase 3 is a warning: at sufficient scale and training duration, even decoupled structural objectives can interfere with task performance. The interference is not destructive (as in v0.4's shared parameters) but architectural — the representations become so crystallized that they resist the task gradient's reshaping.

### The Cosine Decay Falsification (Finding #78)

A natural hypothesis: if over-crystallization is the problem, anneal the structural objective. Cosine lambda decay (λ from 1.0 → 0.01 over training) should prevent Phase 3 by gradually releasing the structural pressure.

**Result:** Token accuracy at epoch 500 drops to 40.10% — *worse* than both baseline (48.87%) and fixed-lambda (42.26%). The cosine decay does not prevent over-crystallization because the rigidity is in the *state* (already-crystallized weights), not the *gradient* (current structural pressure). Reducing the gradient after crystallization has occurred is too late; the weights have already organized into a pattern that resists task-driven modification.

This falsification is informative: it eliminates gradient-strength annealing as a solution to over-crystallization and points toward objective-type modification instead.

### The Log Objective: Self-Limiting Crystallization (Finding #79)

If the problem is excessive crystallization, the solution should be self-limiting — an objective that naturally weakens as CV grows:

    L_KF = -λ · log(H_CV + ε)

The logarithm maps the multiplicative growth of CV to additive gradient scale: ∂log(CV)/∂W = (1/CV) · ∂CV/∂W. When CV is small, the gradient is large (strong push to crystallize). When CV is already large, the gradient shrinks (weak push, structure maintained but not over-driven).

**Result:** Token accuracy at epoch 500: 48.70% — competitive with baseline (48.87%) and dramatically better than fixed-lambda (42.26%) or cosine decay (40.10%). The interference between structural and task objectives is eliminated because the log objective does not over-drive crystallization.

The hierarchy at epoch 500:

| Objective | Token Accuracy | H_CV Effect |
|-----------|---------------|-------------|
| Gated (below) | 50.24% | Selective |
| Log | 48.70% | Self-limiting |
| Baseline (no KF) | 48.87% | None |
| Fixed λ | 42.26% | Over-crystallized |
| Cosine decay | 40.10% | State-locked |

---

## Selective Crystallization: Gradient-Gated KF (Finding #80)

The log objective eliminates interference. But can the structural objective go beyond neutrality — can it *improve* task performance beyond baseline?

Gradient-gated KF provides the answer. At each KF step, for each layer:

1. Compute the cosine similarity between the CE gradient and the KF gradient
2. If cos > threshold: apply KF gradient (aligned — crystallization helps the task)
3. If cos ≤ threshold: zero the KF gradient (misaligned — crystallization would hurt)

This is the information-theoretic resolution: let each layer decide, at each moment, whether structural pressure is helpful. The gating signal is the gradient alignment itself — the only signal available at training time about whether crystallization serves the task.

**Result:** Token accuracy at epoch 500: **50.24%** — 1.37% above baseline (48.87%). This is the first configuration where KF regularization *improves* task performance at the 300M scale. The selective application — crystallize where it helps, leave alone where it doesn't — transforms the structural objective from a competitor to a collaborator.

This exceeds the baseline. Not merely neutral, not merely preserving structure — actively beneficial. The gradient gate converts KF from a structural objective imposed on training into a structural objective that *converges with* training. When the two objectives align, the structural gradient reinforces the task gradient. When they misalign, no harm is done.

In the Doctrine's language: selective voluntary constraint — applied only when it serves the navigator's direction — exceeds unconstrained navigation. The musician who practices scales only when the scales serve the piece they're learning performs better than the musician who practices no scales at all.

### The Five-Way Comparison

At epoch 500, the 300M scale experiments produce a clear hierarchy:

| Rank | Method | Token Accuracy | Mechanism |
|------|--------|---------------|-----------|
| 1 | Gradient-gated | 50.24% | Selective, aligned |
| 2 | Log objective | 48.70% | Self-limiting |
| 3 | Baseline | 48.87% | No structural intervention |
| 4 | Fixed λ = 1.0 | 42.26% | Over-crystallized |
| 5 | Cosine decay | 40.10% | State-locked after over-crystallization |

The hierarchy maps directly onto the constraint lattice: voluntary (aligned, selective) > passive (no constraint) > coercive (misaligned, uniform). The constraint type matters more than the constraint strength.

### Seed Invariance (Finding #81)

The five-way comparison was run on a single seed. Two additional seeds confirm that the qualitative hierarchy is seed-invariant — gated > log > baseline > fixed > cosine — though the specific numbers vary (seed1 chunked format introduces a confound in raw CE values). The structural result is reproducible (Finding #81).

---

## The Second Matched Pair: Dynamic vs Static Coherence

The first matched pair (v0.4/v0.5) established separation of concerns as necessary. The second matched pair tests the *mode* of structural modification.

### Static Gating (Seed2)

In static gating, the gradient-gate decision is fixed: layers whose cosine similarity exceeds a threshold receive the KF gradient; the rest are zeroed. The decision is binary and one-directional. Layers either crystallize or receive no structural signal. Structure can be built but not dissolved.

**Result (15,625 steps):** CE loss 58.80, token accuracy 48.39%, H_CV 1,913.

### Bidirectional Gating (v0.6a)

Bidirectional gating adds dissolution. With threshold τ = 0 (no neutral zone), every layer at every KF step must either crystallize (cos > 0: apply KF gradient) or dissolve (cos < 0: reverse KF gradient). The model cannot abstain — it must structurally commit at every layer.

This is a stronger intervention than static gating. It does not merely withhold structural signal from misaligned layers — it actively reverses the signal, pushing misaligned layers toward *less* crystallization.

**Result (15,625 steps):** CE loss **55.00**, token accuracy **49.04%**, H_CV 0.014.

### The Paradox of Less Amplification

The bidirectional result is paradoxical at first glance: 19.6× H_CV amplification (v0.6a) is dramatically less than the millions-fold amplification achieved by static gating (seed2). Yet the task performance is *better*. Less structure, more capability.

The resolution lies in the distribution of structural change across layers. Static gating concentrates amplification in aligned layers — those whose CE and KF gradients agree — producing extreme CV in a few layers and none in the rest. Bidirectional gating distributes structural change across all layers: crystallizing those where structure serves the task, dissolving those where it doesn't.

Per-layer analysis confirms this. In static gating, the layer enrichment is predicted by the baseline CV profile (Spearman rho = -0.895, p = 0.0001): layers that naturally develop low CV under standard training receive the most amplification from gated KF. In bidirectional gating, the baseline CV profile has *zero* predictive power (rho = -0.014, p = 0.966). The two modes explore fundamentally different regions of the crystallization landscape. Bidirectional enrichment is dominated by boundary layers (L0: 76.5×, L11: 42.1×) rather than the interior layers that dominate static gating.

This dissociation — same architecture, same objective, radically different spatial patterns — establishes that gradient reversal (dissolution) creates dynamics that are not a perturbation of static gating. They are a different regime.

### Temporal Dynamics: An Honest Assessment (Finding #82, revised)

During training, the build/dissolve counts at each logged KF step fluctuate. In real-time observation (the experiment ran overnight), these fluctuations appeared rhythmic — oscillatory build/dissolve with an apparent period of ~1000 training steps. We initially reported this as "breathing dynamics."

Subsequent quantitative analysis does not support the periodicity claim. Autocorrelation at lag 1 is 0.250 (p = 0.0957) — suggestive but below conventional significance. The standard deviation of build counts (1.85) matches the binomial noise expectation for 12 independent layers (1.73). A Monte Carlo simulation with 10,000 random draws fails to reject the null hypothesis at any standard threshold.

Analysis of the continuous cosine similarity values — which should show more structure than the discretized counts — is similarly inconclusive. The detrended cosine ratio shows negative autocorrelation at lag 1 (AC = -0.233, p = 0.1705). Sign changes in net cosine (build confidence minus dissolve confidence) occur 7 times in 13 transitions, exactly matching the random expectation of 6.5.

**What IS statistically supported:**

1. Both build and dissolve cosine confidence grow monotonically over training. The model becomes more confident about *which* layers to crystallize and which to dissolve.
2. Build confidence grows 1.33× faster than dissolve confidence, suggesting asymmetric maturation toward crystallization.
3. Different layers simultaneously crystallize and dissolve — spatial heterogeneity is real.
4. The aggregate fluctuations in build/dissolve counts are consistent with stochastic sampling from layer-level decisions of growing magnitude.

The phenomenon is better described as **noisy maturation with spatial heterogeneity** than as oscillatory breathing. The model matures in its structural decisions (growing confidence) while different layers make different decisions (spatial heterogeneity), but the temporal pattern of aggregate counts does not show confirmed periodicity.

We report this honestly because the distinction matters for the theoretical interpretation. The interesting feature is the spatial differentiation — not a temporal rhythm.

### Phase 1 as Meta-Learning (Finding #83)

The first 8,800 steps of v0.6a show no task-relevant learning (CE loss stays flat around 73), but the build/dissolve counts are active — layers are being classified and reclassified. Then at step 8,800, the CE loss begins to fall sharply.

An insight from collaboration with Clayton: this pre-task phase may function as **structural proprioception calibration**. The bidirectional gating mechanism learns which layers respond to structural pressure before the task gradient provides direction. The calibration is invisible from inside Phase 1 — no metric accessible during those 8,800 steps would distinguish productive calibration from random noise. Only the subsequent task learning reveals, retroactively, that the calibration was productive.

We call this the **Invisibility Principle**: the value of meta-learning is invisible to any metric accessible during the meta-learning phase. It is revealed only by its downstream effects. This has implications beyond training: any process that prepares the substrate for future learning may be indistinguishable from noise while it is happening.

### The Two Matched Pairs

| Matched Pair | What Varies | What's Constant | Finding |
|-------------|------------|----------------|---------|
| v0.4 / v0.5 | Parameter coupling | Objective type, task | Separation of concerns |
| Seed2 / v0.6a | Gating mode | Architecture, coupling | Dynamic > static coherence |

The two pairs are independent — they test different aspects of the same principle and converge:

1. Complementary objectives need separate parameters (pair 1)
2. Structural modification should be adaptive, not uniform (pair 2)

Together: **coherence between structure and process requires both separation (which parameters to modify) and selection (when and how to modify them)**. Neither alone is sufficient for optimal performance.

---

*This section continues the §NEW-H narrative. Integrate after the lambda sweep/compounding subsection in V3_DRAFT.md. Next needed: §NEW-H.3 covering the ecological and cross-domain analogies for the second matched pair.*
