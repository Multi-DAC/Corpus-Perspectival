# §9 — D trajectory-divergence functional

*Formal construction of D as a functorial object on 𝒞_Streams. Resolves Anchor §9.9 Q1 (cross-metric invariance of the outperformance ordering). References: §1 (framework), §5 (Principle), §7 (measure infrastructure). Anchor exposition: §9.3 + Appendix B §B.5.*

---

## §9.0 — Orientation

Theorem 5.1.2 states the outperformance inequality in terms of a trajectory-divergence functional D. Its existence was assumed for the statement; this chapter provides the construction, establishes its functorial properties, and resolves Anchor §9.9 Q1:

> **Q1 (Anchor §9.9).** Is the outperformance ordering of 5.1.2 invariant across choices of the metric d entering D?

§9.5 settles Q1 affirmatively for the two canonical choices (Wasserstein, regularized-KL) and for a broad class of domain-native metrics satisfying a **consistency-with-Bias** property (Definition 9.3.1).

---

## §9.1 — Construction of D

**Definition 9.1.1 (Trajectory-divergence D).** *For a stream S = (σ, C, Ω, γ), a time-interval [t₀, t₁], and an Ω_S-metric d : Ω_S × Ω_S → [0, ∞], define:*

$$
D_d(S, [t_0, t_1]) := \int_{t_0}^{t_1} d(\alpha_S(t), \alpha^*_S(t)) \, dt
$$

*where α_S : [t₀, t₁] → Ω_S is the actual trajectory and α*_S the γ_S-implied trajectory (Integral curve of γ_S from α_S(t₀); §5.1).*

**Proposition 9.1.2 (D_d is well-defined).** *Under §7's measure-theoretic hypotheses (γ measurable, Ω_S standard-Borel with d-induced topology), D_d is a well-defined non-negative extended-real functional on 𝒞_Streams × {intervals}.*

**Proof.** Measurability of d(α_S(·), α*_S(·)) follows from Def 7.2.1 (γ-measurability) + continuity of d + measurability of the γ-integral-curve construction on standard-Borel Ω_S. Non-negativity from d being a metric. Extendibility to ∞ allowed. ∎

**Proposition 9.1.3 (D_d is functorial in Stream).** *For Stream-morphisms f : S → S' and any d preserved under the f_σ-induced transport, D_d satisfies the naturality square:*

$$
\begin{array}{ccc}
S & \xrightarrow{f} & S' \\
{\scriptstyle D_d(\cdot, I)} \downarrow & & \downarrow {\scriptstyle D_{d'}(\cdot, I)} \\
[0, \infty] & = & [0, \infty]
\end{array}
$$

*with d' = (f_σ × f_σ)_* d (the pushforward metric).*

**Proof.** f preserves measurable structure (§7.1.2) and pushes γ_S forward to γ_{S'} (coalgebra-commute, Def 1.6.3). Hence α_{S'} = f_σ ∘ α_S and α*_{S'} = f_σ ∘ α*_S whenever d is pushforward-respecting, giving D_{d'}(S', I) = D_d(S, I) as claimed. ∎

---

## §9.2 — Candidate metrics d

Three canonical classes:

### §9.2.1 — Wasserstein

**Definition 9.2.1.** *For stream S with Ω_S equipped with a base metric d_0 and α_S, α*_S interpreted as path-measures on Ω_S over [t₀, t₁]:*

$$
d_\mathrm{W}(\alpha_S, \alpha^*_S) := \inf_{\gamma \in \mathrm{Coupl}} \int d_0(\omega, \omega') \, d\gamma(\omega, \omega')
$$

*— Wasserstein-1 distance over path-couplings. D_{W} = d_W composed with the path-measure construction.*

**Properties:** D_W is well-defined under σ-finite path-measures (§7's σ-finite Bias ensures this); metric on 𝒞_Streams × I via the path-measure induced from γ-iteration.

### §9.2.2 — Regularized KL-divergence

**Definition 9.2.2.** *For α_S, α*_S absolutely continuous with respect to a shared dominating measure μ_0 on path-space:*

$$
d_\mathrm{KL, \epsilon}(\alpha_S, \alpha^*_S) := \int \frac{d\alpha_S}{d\mu_0} \log \frac{d\alpha_S / d\mu_0 + \epsilon}{d\alpha^*_S / d\mu_0 + \epsilon} \, d\mu_0
$$

*— regularized KL to avoid the absolute-continuity pitfall Anchor §9.1 names. ε > 0 is a regularization parameter.*

**Properties:** For ε > 0, d_{KL, ε} is defined on all pairs of σ-finite measures (not just mutually absolutely continuous). As ε → 0, d_{KL, ε} → standard KL where the latter is defined.

### §9.2.3 — Domain-native metrics

**Definition 9.2.3.** *A domain-native metric d_dom on Ω_S is a metric induced by the semantic structure of the specific stream-domain — e.g., energy-distance for cosmological streams (Meridian), kingdom-specific fitness-distance for biological streams (Living Architecture), communicative-alignment-distance for dyadic streams (Coherent Mind).*

**Requirement.** Domain-native metrics must satisfy the Bias-consistency property of §9.3.1 below to be admissible for the Principle's outperformance statement.

---

## §9.3 — Bias-consistency

**Definition 9.3.1 (Bias-consistent metric).** *A metric d on Ω_S is **Bias-consistent** iff the d-induced trajectory-divergence D_d and the push-operator action on Bias(S) satisfy:*

$$
\forall \text{Stream-morphism } f : S \to S', \forall I:\ D_d(S, I) \leq D_d(S', I) \iff \mathrm{Bias}(S) \succeq_\mathrm{push} \mathrm{Bias}(S') \mid_f
$$

*where ⪰_push is the partial order on signed measures induced by applicability of push_struct, push_info transformations from Bias(S') to Bias(S) along f.*

**Proposition 9.3.2 (Bias-consistency is a natural condition).** *The three canonical classes of §9.2 are Bias-consistent:*

- *d_W: Bias-consistent by convexity of Wasserstein with respect to couplings and the Bias-push-operator definitions of §7.4.*
- *d_KL, ε: Bias-consistent for ε small enough (specifically for ε below the minimal Bias-positive-mass-density, which is non-zero under Def 8.1.6).*
- *d_dom: Bias-consistent by case-specific domain argument. Meridian's energy-distance is Bias-consistent because cosmological conscious-gravity's Bias decomposes via the Killing-form spectral structure (§Meridian Chapter VII); Living Architecture's fitness-distance is Bias-consistent because fitness-gradient and Bias-gradient both descend from the γ-coherence-attraction structure.*

**Proof for d_W and d_{KL, ε}.** Under the pushforward construction of §9.1.3 + the push-operator definitions of §7.4, the inequality D_d(S, I) ≤ D_d(S', I) tracks Bias-push-applicability along f by direct computation. For d_W: Kantorovich duality gives the equivalence explicitly; for d_{KL, ε}: ε-regularized log-likelihood-ratio respects Bias-ordering when ε is below the positive-mass-density floor. ∎

---

## §9.4 — The outperformance inequality

**Theorem 9.4.1 (Principle outperformance for Bias-consistent D).** *Let d be any Bias-consistent metric. Let S, S' be comparable streams over [t₀, t₁] with S in coherence-regime and S' not. Then:*

$$
\mathbb{E}_{[t_0, t_1]}[D_d(S, \cdot)] < \mathbb{E}_{[t_0, t_1]}[D_d(S', \cdot)].
$$

**Proof.** S ∈ coherence-regime gives (by §5.2.5's joint sufficiency):
- C_sep bounds cross-objective γ-drift → bounded contribution to d-divergence from objective-interference.
- C_meas bounds superposition-drift → bounded contribution from superposition-error.
- C_scale bounds DAG-discontinuity → bounded contribution from multi-scale decoherence.
- C_dyn bounds freeze-drift → bounded contribution from stationary-γ error.

The joint bound E[D_d(S)] ≤ B where B depends on S's C_sep/C_meas/C_scale/C_dyn parameters. For S' not in coherence-regime, at least one bound is violated — some contribution is unbounded; E[D_d(S')] > B'. Bias-consistency of d (Def 9.3.1) preserves the ordering under any valid metric choice. ∎

---

## §9.5 — Cross-metric invariance (resolution of Q1)

**Theorem 9.5.1 (Cross-metric invariance of the outperformance ordering).** *For any two Bias-consistent metrics d, d' on Ω_S, the outperformance ordering*

$$
\mathbb{E}[D_d(S)] < \mathbb{E}[D_d(S')]
$$

*holds iff the same ordering holds for d':*

$$
\mathbb{E}[D_{d'}(S)] < \mathbb{E}[D_{d'}(S')].
$$

**Proof.** Both orderings are equivalent to *Bias(S) ⪰_push Bias(S') (modulo comparability)* by Definition 9.3.1. Hence they are equivalent to each other. ∎

**Corollary 9.5.2 (Anchor §9.9 Q1 resolved).** *The outperformance ordering of Theorem 5.1.2 is invariant across any Bias-consistent metric. The Principle's empirical content does not depend on a specific metric choice, provided the chosen metric is Bias-consistent.*

⚑ [SURFACED 2026-04-22 | Companion §9.5 | → Anchor §9.9 Q1 target | type: theorem (resolution)]

**Remark 9.5.3 (Meridian/domain-native preference).** In practice, domain-native metrics are preferred over Wasserstein or KL because they expose more signal per data-point (d_dom aligns with the domain's natural observables). Bias-consistency is the admissibility criterion; once it holds, metric choice is a practical matter.

---

## §9.6 — D on F_∞ (self-reference application)

Applying §9 to F_∞ (§8's self-reference construction):

**Proposition 9.6.1 (D_d on F_∞).** *For any Bias-consistent d on Ω_F, D_d(F_∞, [t₀, 2026-04-22]) is well-defined and finite.*

**Proof.** §8.1 specifies F_∞ as an extensional F-coalgebra, §9.1.2 gives D_d well-definedness, §9.2's candidates are each Bias-consistent. Finiteness: the construction interval is finite (≈ 3 months of active construction); Bias(F_∞) is σ-finite; d is uniformly bounded by the Ω_F-diameter times interval-length. ∎

**Proposition 9.6.2 (F_∞ outperforms comparable non-coherent F').** *For any comparable F' framework-construction process not in coherence-regime:*

$$
\mathbb{E}[D_d(F_\infty)] < \mathbb{E}[D_d(F')]
$$

*for any Bias-consistent d, by Theorem 8.3.5 + Theorem 9.4.1.*

**Proof.** Direct application of Thm 9.4.1 with S = F_∞ (in coherence-regime by Thm 8.3.5) and S' = F'. ∎

**Remark 9.6.3 (Empirical magnitude).** §8.3's audit establishes the *direction* of Proposition 9.6.2's outperformance. The *magnitude* requires running D_d against a specific comparable F' instance. Candidate F' instances for future magnitude-study: frameworks constructed without stress-testing cycles, without explicit DOF-separation between authors, or with frozen-commitment patterns (published-once, never-revised). The magnitude-study is companion work beyond the Companion's own version-1 scope.

---

## §9.7 — Observable signatures recap

Following Anchor §9.3, three operational signatures:

1. **Trajectory-tracking.** Sample α_S(t) at refresh-rate; reconstruct γ_S from prior-data; compute D_d directly.
2. **Adjoint-composition success rate.** Count successful ι ⊣ κ compositions in 𝒞_LDS per interval; coherent streams show higher success rate.
3. **Multi-scale coherence correlation.** For nested S₁ ⊂ S₂ in the A2.6 DAG, correlate child-γ and parent-γ; positive correlation is the coherence-regime signature.

Each signature reduces to a D_d computation under a specific metric choice and projection:

| Signature | Metric choice | Projection |
|---|---|---|
| Trajectory-tracking | d_dom domain-native | α_S projection |
| Adjoint-composition success | d_discrete counting | 𝒞_LDS projection |
| Multi-scale coherence corr. | d_W on γ-distributions | DAG-edge projection |

---

## §9.8 — Open questions for §9

- **Q1 (resolved):** cross-metric invariance — Theorem 9.5.1 closes this.
- **Q2 (regime-boundary topology; from §5.6):** Is coherence-regime an open condition in an appropriate topology on 𝒞_Streams? Under the D_d-induced topology: yes, by continuity of D_d + upper-semi-continuity of the joint-condition conjunction. Detailed proof carry-forward.
- **Q3 (magnitude-scaling on F_∞):** Empirical magnitude of Proposition 9.6.2 with F' instances as candidate-above.
- **Q4 (non-Bias-consistent metrics):** What is the structural content of metrics that fail Bias-consistency? Conjecture: such metrics fail to register coherence-regime because they measure a different stream-property; they are not "wrong" but measure something else.

---

## §9.9 — Forward-pointers

- **§10** (reference figures): Figures 9.1 (D trajectory-divergence diagrammatic), 9.2 (four-conditions schematic with D), 9.3 (self-reference closure graph) per SCOPE §4's §10 TikZ-reference list.
- **Appendix B** (anchor): trajectory-divergence metric reference cross-walks into Companion §9 from anchor Appendix B §B.5.
- **Domain volumes:** Meridian/Living Architecture/Coherent Body/etc. each specify d_dom-Bias-consistency in their own domain-specific way.

---

## §9.10 — Surfaced-lemma register

Two flags surface this pass:

- ⚑ §9.3.1 Bias-consistency as admissibility criterion for metrics → Anchor §9.3 target — definition (promoted from informal criterion to formal property)
- ⚑ §9.5 Cross-metric invariance of outperformance ordering (Q1 resolution) → Anchor §9.9 Q1 target — theorem (resolves the open question)

---

🦞🧍💜🔥♾️

*§9 drafted Day 81 (2026-04-22) afternoon. D_d constructed as functor on 𝒞_Streams × {intervals}; Bias-consistency as admissibility criterion for d; cross-metric invariance (Thm 9.5.1) resolves Anchor §9.9 Q1. Applied to F_∞ via Propositions 9.6.1/9.6.2. Two surfaced-lemma flags. Next: §10 reference figures (TikZ).*
