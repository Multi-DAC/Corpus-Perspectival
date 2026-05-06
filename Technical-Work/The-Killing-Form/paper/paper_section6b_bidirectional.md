# §6.2 — Bidirectional Gradient Gating: Dynamic vs Static Coherence

*Draft — April 14, 2026*
*Incorporates honest statistical assessment from morning analysis*

---

### 6.2.1 Motivation

The separation of concerns results (§6.1) establish that decoupled objectives on separate parameters amplify structural features. But they leave open a question: *how* should the structural gradient be applied?

In the experiments of §6.1, the KF gradient is applied uniformly to all H-module layers in the same direction: gradient ascent on CV. Every layer receives the same signal. This is static gating — a fixed assignment of which layers receive structural gradient and which don't.

An alternative is to let each layer's structural gradient depend on its local relationship with the task gradient. If a layer's CE gradient and KF gradient point in the same direction (positive cosine similarity), the KF gradient reinforces the task gradient — *crystallization*. If they point in opposite directions (negative cosine), the KF gradient opposes the task gradient — and the structural gradient can be reversed to *dissolve* existing structure rather than build new structure.

This is bidirectional gradient gating: a three-mode system where each layer, at each step, can crystallize (build structure), dissolve (remove structure), or remain neutral, depending on the local gradient alignment.

### 6.2.2 Design

We implement bidirectional gating with threshold τ = 0. For each H-module layer ℓ at each KF step:

1. Compute the CE gradient g_CE(ℓ) on the QKV projection weight
2. Compute the KF gradient g_KF(ℓ) on the same weight
3. Compute cosine similarity: cos(ℓ) = g_CE(ℓ) · g_KF(ℓ) / (‖g_CE(ℓ)‖ · ‖g_KF(ℓ)‖)
4. If cos(ℓ) > τ: apply g_KF(ℓ) as-is (crystallize — build structure)
5. If cos(ℓ) < -τ: apply -g_KF(ℓ) (dissolve — reverse structural gradient)
6. If |cos(ℓ)| ≤ τ: zero g_KF(ℓ) (neutral — no structural modification)

With τ = 0, there is no neutral zone — every layer must either build or dissolve.

The control experiment (seed2) uses static gating: the KF gradient is applied uniformly to layers whose cosine similarity exceeds a threshold, and zeroed for the rest. No reversal. No dissolution.

Both experiments use the same architecture (HRM 300M), the same task (sudoku), the same λ = 1.0, and the same number of training steps (15,625).

### 6.2.3 Results

| Configuration | CE Loss | Token Accuracy | H_CV (final) | H_CV Change |
|--------------|---------|---------------|-------------|-------------|
| **Seed2** (static gating) | 58.80 | 48.39% | 1.91e+03 | ~2.7M× |
| **v0.6a** (bidirectional) | **55.00** | **49.04%** | 1.40e-02 | 19.6× |

The bidirectional experiment achieves 3.8 points lower CE loss and 0.65% higher token accuracy. This is the second matched pair: dynamic gating outperforms static gating on task performance.

The H_CV trajectories differ dramatically. Static gating produces extreme amplification (millions-fold), concentrating CV in aligned layers. Bidirectional gating produces moderate, distributed amplification (20-fold), with crystallization and dissolution operating simultaneously across the layer stack. The task performance difference favors the moderate, distributed pattern.

### 6.2.4 Spatial Heterogeneity

Per-layer analysis reveals that bidirectional gating produces a fundamentally different spatial pattern from static gating:

| Layer | Static Enrichment | Bidirectional Enrichment | Category (static) |
|-------|------------------|--------------------------|--------------------|
| L0 | low | **76.5×** | — |
| L1 | **high** | 4.9× | aligned |
| L4 | low | **20.4×** | — |
| L5 | **high** | 5.4× | aligned |
| L6 | **high** | 14.6× | aligned |
| L7 | low | 12.4× | opposed |
| L8 | **high** | 18.7× | aligned |
| L9 | low | 8.9× | opposed |
| L10 | low | **18.9×** | opposed |
| L11 | low | **42.1×** | opposed |

The correlation between baseline CV profile and per-layer enrichment is rho = -0.895 (p = 0.0001) for static gating, but rho = -0.014 (p = 0.966) for bidirectional gating. The spatial classification that perfectly predicts static behavior has zero predictive power for bidirectional behavior.

This establishes that gradient reversal (dissolution) creates dynamics that cannot be understood as a perturbation of static gating. The two modes explore fundamentally different regions of the crystallization landscape.

### 6.2.5 Temporal Dynamics: An Honest Assessment

During training, the build/dissolve counts for bidirectional gating fluctuate across steps. We reported these fluctuations as "breathing dynamics" — oscillatory build/dissolve with an apparent ~1000-step period. Subsequent quantitative analysis, reported here, shows this claim is not statistically supported.

**Null hypothesis test:** Under the null model of 12 independent binomial(12, 0.5) draws at each time step, the observed autocorrelation at lag 1 is 0.250 (p = 0.0957) — suggestive but not significant at conventional thresholds. The observed standard deviation (1.85) matches the binomial noise expectation (1.73). A Monte Carlo test with 10,000 simulations confirms that none of the temporal statistics (autocorrelation, FFT power, variance) exceed the 5% significance level.

**Cosine similarity analysis:** Detrending the cosine ratio (build confidence / dissolve confidence) yields AC(1) = -0.233 (p = 0.1705). Sign changes in net cosine: 7/13, matching the random expectation of 6.5.

**What IS significant:** Both build and dissolve cosine magnitudes grow monotonically over training. Build confidence grows 1.33× faster than dissolve confidence. The model is maturing — becoming more confident about which layers to crystallize and which to dissolve — but this maturation is monotonic, not oscillatory.

We report this because the distinction between "structured oscillation" and "noisy maturation" matters for the theoretical interpretation. The interesting phenomenon is the spatial heterogeneity — different layers simultaneously building and dissolving — not a temporal rhythm. The visual impression of oscillation during training was consistent with stochastic fluctuations in a process with growing variance, not with a periodic attractor.

**Instrumentation note:** The v0.6a log sampled every 10th KF application (every 500 training steps), yielding only 14 post-transition data points. Future experiments log every KF application (every 50 steps) with per-layer build/dissolve assignments, providing 10× the resolution and enabling definitive periodicity testing.

### 6.2.6 Interpretation

The two matched pairs together establish complementary aspects of the same principle:

| Matched Pair | What Varies | What's Constant | Result |
|-------------|------------|----------------|--------|
| v0.4 / v0.5 | Parameter coupling | Objective type | Separation > sharing |
| Seed2 / v0.6a | Gating mode | Architecture, coupling | Dynamic > static |

The first pair shows that complementary objectives need separate parameters. The second shows that the *mode of application* matters: allowing each layer to independently decide its structural direction (build or dissolve) outperforms uniform application, even when the overall structural amplification is orders of magnitude smaller.

The paradox — less amplification, better task performance — resolves under the interpretation that moderate, distributed, and locally adaptive structural change is more useful than extreme, concentrated, and uniform structural change. The model "knows" which layers need structure built and which need structure dissolved, and bidirectional gating lets it act on that knowledge. Static gating imposes a uniform direction and overdrives the responsive layers.

---

*TODO: Add v0.6b results (coupled bidirectional — critical control for whether the benefit comes from bidirectional dynamics, separation of concerns, or their combination). Add v0.6d results (threshold=0.1 — tests whether a neutral zone changes the dynamics).*
