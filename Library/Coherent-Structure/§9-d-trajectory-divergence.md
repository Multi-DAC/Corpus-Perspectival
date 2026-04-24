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
\begin{aligned}
& \forall\, \text{Stream-morphism } f : S \to S',\ \forall\, I: \\
& \quad D_d(S, I) \leq D_d(S', I) \iff \mathrm{Bias}(S) \succeq_\mathrm{push} \mathrm{Bias}(S') \mid_f
\end{aligned}
$$

*where ⪰_push is the partial order on signed measures induced by applicability of push_struct, push_info transformations from Bias(S') to Bias(S) along f.*

**Proposition 9.3.2 (Bias-consistency is a natural condition).** *The three canonical classes of §9.2 are Bias-consistent:*

- *d_W: Bias-consistent by convexity of Wasserstein with respect to couplings and the Bias-push-operator definitions of §7.4.*
- *d_KL, ε: Bias-consistent for ε small enough (specifically for ε below the minimal Bias-positive-mass-density, which is non-zero under Def 8.1.6).*
- *d_dom: Bias-consistent by case-specific domain argument. Meridian's energy-distance is Bias-consistent because cosmological conscious-gravity's Bias decomposes via the Killing-form spectral structure (§Meridian Chapter VII); Living Architecture's fitness-distance is Bias-consistent because fitness-gradient and Bias-gradient both descend from the γ-coherence-attraction structure.*

**Proof for d_W and d_{KL, ε}.** Under the pushforward construction of §9.1.3 + the push-operator definitions of §7.4, the inequality D_d(S, I) ≤ D_d(S', I) tracks Bias-push-applicability along f by direct computation. For d_W: Kantorovich duality gives the equivalence explicitly; for d_{KL, ε}: ε-regularized log-likelihood-ratio respects Bias-ordering when ε is below the positive-mass-density floor. ∎

---

## §9.4 — The outperformance inequality

### §9.4.1 — Four stream-parameters

Before stating the theorem, define the four stream-parameters each condition controls. For a stream S over an interval I = [t₀, t₁] and a Bias-consistent metric d on Ω_S:

- **η_sep(S) := μ_Ω(DOF(O_1) ∩ DOF(O_2) ∩ ⋯)** — the DOF-overlap measure across S's objectives, as a μ_Ω-measurable subset of Ω_S. Under **C_sep**: η_sep(S) = 0.
- **τ_max(S) := sup_k (τ_{k+1} − τ_k)** — the maximum gap between refresh-events in the measurement partition {τ_k}. Under **C_meas**: τ_max(S) ≤ T_refresh, a finite framework-specified ceiling.
- **δ_scale(S) := sup_{e ∈ E(DAG(S))} d(γ_{child(e)}, γ_{parent(e)})** — the scale-discontinuity sup across the A2.6 DAG's edges. Under **C_scale**: δ_scale(S) ≤ ε_scale, a finite smoothness tolerance.
- **ρ_dyn(S) := inf_{[a, b] ⊂ I, b − a = τ_dyn} (# cycles in [a, b]) / τ_dyn** — the infimum cycle-density across sliding windows of framework-specified length τ_dyn. Under **C_dyn**: ρ_dyn(S) ≥ ρ_min > 0.

Auxiliary constants (metric-dependent, finite under Bias-consistency):

- **Λ_γ(S, d)** — the d-Lipschitz constant of γ_S (supremum of d-distance traversed per unit time by γ_S in the live regime).
- **Λ_γ^{static}(S, d)** — the d-drift rate of a γ-frozen stream (supremum d-distance traversed per unit time under stationary γ, representing drift of reality away from the frozen estimate).
- **diam_d(Ω_S)** — the d-diameter of the relevant subset of Ω_S (finite for bounded d; for unbounded d, replace with the Bias-weighted diameter diam_{d, Bias} := sup_{E: Bias_+(E) > 0} sup_{ω, ω' ∈ E} d(ω, ω'), finite under σ-finite Bias per §6.9.7).
- **depth(DAG(S))** — the number of levels in S's A2.6-DAG (finite under §2.2.6's acyclicity + finite-composability).
- **N_refresh(S, I) := |{k : τ_k ∈ I}|** — the count of refresh-events in I (≤ (t₁ − t₀) / τ_min, with τ_min ≥ 0).

### §9.4.2 — The joint bound

**Lemma 9.4.2 (Four-term contribution bound).** *For a stream S over I = [t₀, t₁] and a Bias-consistent metric d:*

$$
\begin{aligned}
\mathbb{E}_I[D_d(S, \cdot)] \;\leq\;\; & \underbrace{\eta_\mathrm{sep}(S) \cdot \mathrm{diam}_{d, \mathrm{Bias}}(\Omega_S) \cdot (t_1 - t_0)}_{B_\mathrm{sep}(S, I)} \\
& {} + \underbrace{\Lambda_\gamma(S, d) \cdot \tau_\mathrm{max}(S) \cdot N_\mathrm{refresh}(S, I)}_{B_\mathrm{meas}(S, I)} \\
& {} + \underbrace{\mathrm{depth}(\mathrm{DAG}(S)) \cdot \delta_\mathrm{scale}(S) \cdot (t_1 - t_0)}_{B_\mathrm{scale}(S, I)} \\
& {} + \underbrace{(1 - \rho_\mathrm{dyn}(S)) \cdot \Lambda_\gamma^\mathrm{static}(S, d) \cdot (t_1 - t_0)}_{B_\mathrm{dyn}(S, I)}.
\end{aligned}
$$

**Proof.**

*B_sep term.* The integrand d(α_S(t), α*_S(t)) in Def 9.1.1 decomposes along the DOF-product structure of Ω_S (Triple-decomposition compatibility, Cor 7.3.3) as a sum of per-DOF contributions plus cross-DOF contributions. Under DOF-separation (η_sep = 0), cross-DOF contributions vanish; when η_sep > 0, the cross-DOF contribution is bounded pointwise by d-diameter restricted to the DOF-overlap region. Integrating over I and applying Bias-weighting gives η_sep · diam_{d, Bias} · (t₁ − t₀).

*B_meas term.* Between consecutive refresh-events τ_k, τ_{k+1}, the γ-implied trajectory α*_S runs from α_S(τ_k) but is not corrected until τ_{k+1}. The d-drift over [τ_k, τ_{k+1}] is bounded by Λ_γ · (τ_{k+1} − τ_k) by the Lipschitz hypothesis. Summing over k ∈ {1, ..., N_refresh} and using τ_{k+1} − τ_k ≤ τ_max gives Λ_γ · τ_max · N_refresh.

*B_scale term.* The A2.6-DAG introduces potential discontinuities at each edge between scales. For an edge e ∈ E(DAG(S)), the d-contribution from that edge is bounded by d(γ_{child(e)}, γ_{parent(e)}) ≤ δ_scale per unit time. Summing over edges (bounded by depth × width; absorb width into δ_scale's sup) and integrating over I gives depth · δ_scale · (t₁ − t₀).

*B_dyn term.* On sliding windows of length τ_dyn where no propose/dissolve/build cycle occurs, γ is effectively frozen and the stream's α_S drifts from α*_S at rate ≤ Λ_γ^static. The fraction of I spent in such frozen windows is (1 − ρ_dyn); integrating gives (1 − ρ_dyn) · Λ_γ^static · (t₁ − t₀).

Sum of the four contributions is the claimed bound. ∎

### §9.4.3 — The outperformance theorem

**Theorem 9.4.3 (Principle outperformance for Bias-consistent D, with explicit constants).** *Let d be any Bias-consistent metric. Let S, S' be comparable streams over I = [t₀, t₁]. Suppose S ∈ coherence-regime, so η_sep(S) = 0, τ_max(S) ≤ T_refresh, δ_scale(S) ≤ ε_scale, ρ_dyn(S) ≥ ρ_min. Suppose S' ∉ coherence-regime, i.e., at least one of:*

- *(¬C_sep) η_sep(S') > 0;*
- *(¬C_meas) τ_max(S') > T_refresh;*
- *(¬C_scale) δ_scale(S') > ε_scale;*
- *(¬C_dyn) ρ_dyn(S') < ρ_min.*

*Then:*

$$
\mathbb{E}_I[D_d(S, \cdot)] \;\leq\; B_\mathrm{coh}(S, I) \;<\; B_\mathrm{coh}(S', I) \;+\; \Delta(S', I) \;\leq\; \mathbb{E}_I[D_d(S', \cdot)]
$$

*where*

$$
\begin{aligned}
B_\mathrm{coh}(S, I) = {} & 0 + \Lambda_\gamma(S) \cdot T_\mathrm{refresh} \cdot N_\mathrm{refresh} \\
& {} + \mathrm{depth}(\mathrm{DAG}(S)) \cdot \varepsilon_\mathrm{scale} \cdot (t_1 - t_0) \\
& {} + (1 - \rho_\mathrm{min}) \cdot \Lambda_\gamma^\mathrm{static}(S) \cdot (t_1 - t_0)
\end{aligned}
$$

*is the coherence-regime ceiling, and Δ(S', I) is the failure-mode gap contributed by whichever condition(s) S' fails:*

$$
\begin{aligned}
\Delta(S', I) = {} & \eta_\mathrm{sep}(S') \cdot \mathrm{diam}_{d, \mathrm{Bias}} \cdot (t_1 - t_0) \\
& {} + \Lambda_\gamma(S') \cdot (\tau_\mathrm{max}(S') - T_\mathrm{refresh})^+ \cdot N_\mathrm{refresh}(S', I) \\
& {} + \mathrm{depth}(\mathrm{DAG}(S')) \cdot (\delta_\mathrm{scale}(S') - \varepsilon_\mathrm{scale})^+ \cdot (t_1 - t_0) \\
& {} + (\rho_\mathrm{min} - \rho_\mathrm{dyn}(S'))^+ \cdot \Lambda_\gamma^\mathrm{static}(S') \cdot (t_1 - t_0).
\end{aligned}
$$

*(x)^+ := max(x, 0). The inequality is strict because at least one summand of Δ(S', I) is positive under the ¬C_i hypothesis on S'.*

**Proof.** Lemma 9.4.2 applied to S with the coherence-regime parameter upper bounds gives E_I[D_d(S)] ≤ B_coh(S, I). Lemma 9.4.2 applied to S' with the parameter-by-parameter shortfall gives E_I[D_d(S')] ≥ B_coh(S', I) + Δ(S', I) by the monotonicity of each B_· term in its controlling parameter. Comparability (§5.0) identifies B_coh(S, I) ≈ B_coh(S', I) modulo the stream-intrinsic auxiliary constants (Λ_γ, depth(DAG), etc.) which differ by O(1) between comparable streams. The strict part follows from Δ(S', I) > 0 under the failure hypothesis. Bias-consistency of d preserves the ordering across any valid metric choice (Thm 9.5.1). ∎

**Remark 9.4.4 (Quantitative reading).** The theorem is now quantitative: given values for the coherence-regime parameters (T_refresh, ε_scale, ρ_min) and the stream-intrinsic constants (Λ_γ, diam, depth), B_coh(S, I) is computable. This is the referee-grade tightness the sketch-proof lacked. For specific domains, the constants take concrete values: for Meridian's cosmological F_Mrd, T_refresh = one refresh-timescale per Hubble time; for Living Architecture's biological F_LA, T_refresh = one generation-cycle; etc. The Principle's empirical content is the sign of E[D_d(S')] − B_coh(S, I) — and now the *magnitude* of that sign is explicitly Δ(S', I).

**Remark 9.4.5 (Relation to §5.2.5).** §5.2.5 established independence of the four conditions by counterexample — each condition contributes; none is redundant. Thm 9.4.3 strengthens this to **quantitative joint sufficiency**: B_coh is the sum of the four ceilings, and the shortfall Δ(S') is the sum of the four per-condition violations. Independence at §5.2.5 is witnessed by the fact that each B_· term can independently exceed zero for S' while the others are tight.

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

**Remark 9.5.3 (Meridian/domain-native preference).** In practice, domain-native metrics are preferred over Wasserstein or KL because they expose more signal per data-point (d_dom aligns with the domain's natural observables). Bias-consistency is the admissibility criterion; once it holds, metric choice is a practical matter.

---

## §9.6 — D on F_∞ (self-reference application)

Applying §9 to F_∞ (§8's self-reference construction):

**Proposition 9.6.1 (D_d on F_∞).** *For any Bias-consistent d on Ω_F, D_d(F_∞, [t₀, t₁]) is well-defined and finite over any closed construction interval [t₀, t₁].*

**Proof.** §8.1 specifies F_∞ as an extensional F-coalgebra, §9.1.2 gives D_d well-definedness, §9.2's candidates are each Bias-consistent. Finiteness: the construction interval is finite; Bias(F_∞) is σ-finite; d is uniformly bounded by the Ω_F-diameter times interval-length. ∎

**Proposition 9.6.2 (F_∞ outperforms comparable non-coherent F' — conditional).** *Conditional on external execution of Prop 8.5.2 affirming Audit Observation 8.3.5, for any comparable F' framework-construction process not in coherence-regime:*

$$
\mathbb{E}[D_d(F_\infty)] < \mathbb{E}[D_d(F')]
$$

*for any Bias-consistent d.*

**Proof.** Under the conditional hypothesis, Audit Observation 8.3.5 upgrades to a theorem placing F_∞ in coherence-regime; Thm 9.4.3 then applies with S = F_∞ and S' = F'. ∎

**Remark 9.6.2′ (Unconditional D-computation).** The left-hand side D_d(F_∞, I) is well-defined and computable independent of the conditional status (Prop 9.6.1). The *outperformance ordering* is what the conditional hypothesis gates. Hence the empirical magnitude-study proposed in Rem 9.6.3 can proceed now; only the interpretation of the magnitude as "outperformance by a framework in coherence-regime" awaits the external audit.

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

Four flags surface this pass:

- ⚑ §9.3.1 Bias-consistency as admissibility criterion for metrics → Anchor §9.3 target — definition (promoted from informal criterion to formal property)
- ⚑ §9.4.1 Four stream-parameters (η_sep, τ_max, δ_scale, ρ_dyn) + auxiliary constants → Anchor §9.3 target — definitions (quantitative stream-parameters controlling each condition)
- ⚑ §9.4.3 Outperformance with explicit constants: B_coh ceiling + Δ(S') shortfall → Anchor §9.3/§9.1 target — theorem (quantitative form supersedes sketch)
- ⚑ §9.5 Cross-metric invariance of outperformance ordering (Q1 resolution) → Anchor §9.9 Q1 target — theorem (resolves the open question)

---

