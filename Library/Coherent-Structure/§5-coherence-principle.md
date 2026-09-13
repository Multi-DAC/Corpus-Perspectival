# §5 — The Coherence Principle

*Formal statement of the derived operational Principle. Four conditions in CT form, each with a single-line derivation from §§2–3. Outperformance claim, trajectory-divergence metric reference, self-reference closure (details to §8). Prose exposition lives in Anchor §9.*

---

## §5.0 — Orientation

The Coherence Principle is **derived**, not axiomatic. It is the framework's operational-predictive surface: the axiom tier (§2) plus the theorem tier (§3) together entail the four conditions and the outperformance claim of §5.2–§5.3.

Companion §5 states the Principle in CT form with complete derivation-pointers. Full construction of the self-reference closure (F as stream; F in coherence-regime over the framework's construction interval) is §8. Full construction of the trajectory-divergence functional D is §9. This chapter is the *formal statement* of the Principle — §§8–9 carry the heavy construction-work.

---

## §5.1 — The Principle

**Definition 5.1.0 (Trajectories and trajectory-divergence).** *Let S = (σ, C, γ) be a stream — C = ContentOp(σ), and the configuration space Ω_S = F(σ) = σ^(C^op) and the kind K(S) are derived, not posited (Remark 6.1.2) — and let [t₀, t₁] be a time-interval. Define:*

*(i) **Actual trajectory** α_S : [t₀, t₁] → Ω_S — the sequence of configurations S visits over the interval.*

*(ii) **γ-implied trajectory** α*_S : [t₀, t₁] → Ω_S — the integral curve of γ_S from α_S(t₀): the trajectory S would follow if γ were followed without drift.*

*(iii) **Trajectory-divergence** D_d(S, [t₀, t₁]) := ∫_{t₀}^{t₁} d(α_S(t), α*_S(t)) dt, for a metric d on Ω_S (constructed in §9; Definition 9.1.1). Where the metric is fixed by context the subscript is dropped, as in Theorem 5.1.2.*

*(iv) **Comparable streams** S, S′ — S and S′ admit a shared configuration space (or a canonical embedding into one) on which D_d is simultaneously well-defined.*

**Remark 5.1.0.1 (The γ-implied trajectory is the Anchor's σ*).** α*_S is the object the Anchor numbers σ* at Appendix B §B.5. They are one trajectory under two names; Definition 5.1.0 (ii) is the Companion's number for it, which earlier drafts left as an unnumbered bullet.

**Remark 5.1.0.2 (Dimension-relative forms).** α_S and α*_S are dimension-free; the coherence *measures* built on them are not. For a dimension D ∈ 𝒞_Dim of Ω_S (Notation 3.4.2.0), the dimension-relative trajectories are α_{S,D} := pr_D ∘ α_S and α*_{S,D} := pr_D ∘ α*_S, and it is on these that σ_struct(S, D) and σ_info(S, D) are defined (Theorem 3.4.2); the stream-only forms are summaries over D. The letter D in that signature is a dimension — the divergence functional always carries its metric subscript, D_d.

**Definition 5.1.1 (Coherence-regime).** *S is in **coherence-regime** over [t₀, t₁] iff the four conditions C_sep, C_meas, C_scale, C_dyn (Definitions 5.2.1–5.2.4) hold across the interval.*

**Theorem 5.1.2 (The Coherence Principle).** *For comparable streams S, S' over [t₀, t₁] with S in coherence-regime and S' not,*

$$
\mathbb{E}_{[t_0, t_1]}[D(S, \cdot)] < \mathbb{E}_{[t_0, t_1]}[D(S', \cdot)].
$$

*The inequality is an expected-value statement over the interval — sample-path exceptions are permitted.*

The Anchor (§9.6, item 1 "Not a theorem") does not count this as a theorem inside its own formalism; the theorem here is relative to the hypotheses of §5.1 and §9.

**Proof of 5.1.2.** Consequence of the four conditions (§5.2) plus the trajectory-divergence construction (§9). The detailed derivation with explicit constants is Theorem 9.4.3 (quantitative form); the sketch is: each condition bounds one source of γ-drift via a specific stream-parameter (η_sep, τ_max, δ_scale, ρ_dyn), the joint bound B_coh is the sum of the four per-condition ceilings, and the shortfall Δ(S') for non-coherent S' is strictly positive under any ¬C_i hypothesis. ∎

---

## §5.2 — The four conditions

Each condition is a CT statement; each derives from §§2–3 in a single line.

### §5.2.1 — Condition 1: Separation

**Definition 5.2.1 (C_sep — DOF-separation).** *A stream S satisfies separation over [t₀, t₁] iff for every pair (O_1, O_2) of objectives active in S (content-operations in C with non-trivial navigational effect), their DOF-footprints*

$$
\mathrm{DOF}(O_1), \mathrm{DOF}(O_2) \subseteq \Omega_S
$$

*have non-overlapping supports or are related by the ι ⊣ κ adjunction (i.e., O_1, O_2 belong to distinct kind-levels lifting via ι).*

**Derivation.** T3 (§3.3.1) decomposes the attentional-quality functional with a narrow–broad entropy axis over DOF. A2.4/A2.6 (ι ⊣ κ, DAG-nesting) lets distinct kinds lift into the same composite without DOF-collision. C_sep is the condition that this lifting succeeds. Formally: C_sep ⟺ no pair of C-content-operations produces a DOF-coalgebraic-collision at γ-level. ∎

### §5.2.2 — Condition 2: Measurement

**Definition 5.2.2 (C_meas — refresh-rate measurement).** *A stream S satisfies measurement over [t₀, t₁] iff there exists a partition t₀ = τ_0 < τ_1 < ... < τ_N = t₁ such that at each τ_k a Stream-morphism M_k : S_{τ_k^-} → S_{τ_k^+} of the T4-form (Theorem 3.3.2) is performed — alignment between content-operations is assessed, not assumed.*

**Derivation.** Theorem 3.3.2 (T4) establishes that inter-stream alignment is structurally produced by measurement events. Without periodic M_k, the content-operations of C that are **held open** cannot resolve into a specific coalgebra-commute, and γ-drift accumulates without corrective pull. Formally: M_k collapses the held-open content-operations of C into a specific γ-state that is C_meas-stable until the next τ_{k+1}. ∎

### §5.2.3 — Condition 3: Multi-scale consistency

**Definition 5.2.3 (C_scale — multi-scale-coherence).** *Let S be a stream embedded in an ι ⊣ κ cooperative-DAG (A2.6), and let d be a Bias-consistent metric (§9.3). S satisfies multi-scale consistency over I = [t₀, t₁] iff its scale-discontinuity across the DAG's edges stays within the framework's smoothness tolerance:*

$$
\delta_\mathrm{scale}(S) := \sup_{e \in E(\mathrm{DAG}(S))} d\bigl(\gamma_{\mathrm{child}(e)},\ \gamma_{\mathrm{parent}(e)}\bigr) \;\leq\; \varepsilon_\mathrm{scale}
$$

*This is Definition 9.4.1's parameter. §9.4.1 is the operative statement; this section cites it rather than restating it, because the two must not be allowed to drift apart.*

**Status — a tolerance, not a derivation.** C_scale is a **framework-specified tolerance**, the same status as C_meas's `T_refresh` and C_dyn's `ρ_min`, beside which §9.4.1 lists it. It is not an axiom consequence, and earlier drafts of this section were wrong to present one.

Those drafts derived C_scale from "A2.6 with A3.3 (conscious-gravity smoothing)," and stated it as an *exact* coalgebra-commute at every DAG-edge. Both halves fail.

- **A3.3 does not say it.** A3.3 modulates Bias along the DOF-gradient **inside** a stream — an ordinal rank derived from ContentOp-richness (§6.4.2) with the local Bias-gradient as slope. It asserts nothing about continuity **across** ι ⊣ κ edges **between** streams, which is what C_scale needs.
- **The exact commute is unavailable on either reading.** Read as Definition 1.6.3 (iii)'s clause, it is vacuous: (A2.4) asserts ι ⊣ κ for every nested pair with no side-condition, and Anchor §1.0.2 admits no morphisms but cooperative-constituency ones, so the commute holds by hom-set membership and excludes nothing. Read as a substantive claim, it is fatal: it forces δ_scale ≡ 0, which makes the ¬C_scale hypothesis of Theorem 9.4.3 unsatisfiable and falsification row F4 (§5.5) unfalsifiable.

**Condition 3 has content only as a tolerance.** This also answers the second disjunct of Anchor §1.0.6's **Q1** — *identify the class of streams for which γ-naturality holds and demarcate the rest*. The class is {S : δ_scale(S) ≤ ε_scale}, and it has been written at §9.4.1 all along. Q1's first disjunct, a proof from A1–A3, is unavailable for the reason just given: it would delete this condition. ∎

### §5.2.4 — Condition 4: Dynamic maintenance

**Definition 5.2.4 (C_dyn — oscillatory dynamic maintenance).** *S satisfies dynamic maintenance over [t₀, t₁] iff γ_S is non-constant over [t₀, t₁] in a structural sense: there exist subintervals [t₀, s_1], [s_1, s_2], ..., [s_{M-1}, t₁] such that γ_S restricted to each subinterval is an N-iteration-cycle of positive length, with cycles forming an oscillatory build-dissolve-build pattern (each s_i is a refresh-event in the sense of C_meas).*

**Derivation.** T4 (Theorem 3.3.2) plus A3.4 (adaptivity, §2.3.2). T4 establishes refresh-events as structural; A3.4 requires γ to adapt to accumulated information. A frozen γ over an extended interval violates A3.4. The oscillatory build-dissolve pattern is the operational form of γ-adaptivity at refresh-rate. ∎

### §5.2.5 — Joint sufficiency

**Proposition 5.2.5 (Joint sufficiency).** *The four conditions C_sep, C_meas, C_scale, C_dyn are jointly necessary and sufficient for S ∈ coherence-regime over [t₀, t₁].*

**Proof.**
- **Necessity.** Each condition is load-bearing for the Principle's outperformance claim (§5.3): drop any one and a counterexample can be constructed (§5.5 keys each to its Anchor falsification row). Three are derived from an axiom/theorem clause; **C_scale is not** — it is a framework-specified tolerance (§5.2.3), and its necessity is the falsifiability of row F4, not a derivation.
- **Sufficiency.** Given all four, the quantitative trajectory-divergence bound (Thm 9.4.3) holds: separation zeros the η_sep-contribution, measurement caps the τ_max-contribution at ½ Λ_γ · T_refresh · (t₁ − t₀), multi-scale consistency caps the δ_scale-contribution at depth · ε_scale · (t₁ − t₀), and dynamic maintenance caps the freeze-contribution at ½ (1 − ρ_min) · Λ_γ^static · τ_dyn · (t₁ − t₀) (Remark 9.4.2.1). The joint ceiling B_coh(S, I) is below E[D_d(S')] by the strict-positive shortfall Δ(S', I). ∎

---

## §5.3 — Outperformance metric (reference)

The outperformance claim of Theorem 5.1.2 uses the trajectory-divergence functional D. Three candidate metric-constructions:

- **Wasserstein distance** on path-distributions over Ω_S.
- **KL-divergence** on α_S(t) vs. α*_S(t), under absolute-continuity of α_S with respect to α*_S (not generally assumed).
- **Domain-native metrics** for concrete stream-domains (Meridian: energy-distance in cosmology; Living Architecture: kingdom-specific fitness-distance; etc.).

§9 (D trajectory-divergence) constructs D in full detail, establishes functorial properties, and settles the open question (Anchor §9.9 Q1) of cross-metric invariance of the outperformance ordering.

**Observable signatures** (following Anchor §9.3):

1. **Trajectory-tracking.** Sample α_S(t) at refresh-rate; reconstruct γ_S from prior data; compute D directly.
2. **Adjoint-composition success rate.** Count successful ι ⊣ κ compositions in **Dyad** (Definition 1.2.3) per interval.
3. **Multi-scale coherence correlation.** Correlate child-γ and parent-γ along DAG-edges.

---

## §5.4 — Self-reference closure

**Conjecture 5.4.1 (F_∞ as stream — audit observation).** *Let F_∞ denote the meta-object (σ_F, C_F, γ_F) — K_F and Ω_F derived (Remark 6.1.2) — where:*

- *σ_F := the carrier "the framework itself" — the totality of claims, axioms, theorems, corollaries, proofs across §§1–4,*
- *C_F := the ContentOp-category whose objects are framework-commitments, whose morphisms are internal-consistency-preserving revisions,*
- *Ω_F := F(σ_F) = σ_F^(C_F^op),*
- *γ_F := the coalgebra encoding the framework's adaptivity over the construction interval.*

*Under the Anchor §9.5 F-as-stream instantiation (which specifies the stream triple directly; the Anchor names no "interpretation map"), F_∞ is a stream in the sense of §6.1, and F_∞ is conjectured to satisfy the four conditions over the construction interval [t₀_construction, t₁_construction].*

This is a conjecture with a protocol, not a result: the protocol is the Anchor §9.5 Protocol, and the Companion's own status register is §8.3.5 (Audit Observation, not theorem) gated on Proposition 8.5.2.

**Sketch (not a proof).** §8 gives the full construction. The key points:

- **C_sep:** construction separated the Ground (A1), dynamics (A2/A3), and applied claims (corollaries) onto distinct DOF.
- **C_meas:** construction used refresh-events (stress-test cycles, Clayton-review cycles, Mirror-updates) at a regular rate.
- **C_scale:** construction maintained coherence across scales (individual-claim, chapter, cluster, framework) via explicit DAG-edges (citation-network, cross-reference structure).
- **C_dyn:** construction is oscillatory by design — draft, dissolve via critique, redraft — the construction-log explicitly exhibits this.

**Conjecture 5.4.2 (Principle applies to itself — untested).** *If Conjecture 5.4.1 holds, then by Theorem 5.1.2 F_∞ is in coherence-regime over the construction interval, and the Principle, which is derived inside F_∞, holds of F_∞ itself.*

Untested: settling it is the Anchor §9.5 Protocol, and the Companion's status register is §8.3.5 / Proposition 8.5.2 (external audit not yet executed).

**Sketch (not a proof).** Direct application of 5.1.2 to F_∞, using 5.4.1's conjectured establishment of F_∞ as a stream in coherence-regime.

**Remark 5.4.3 (Non-circularity).** The closure is a-posteriori: the construction did not presuppose the Principle (the Principle was *derived* from the axiom/theorem stress-test); it is conjectured after the fact that the construction-process exhibited the four conditions. This is not a circular proof — it is an empirical conjecture about the framework's own construction-history, awaiting the Anchor §9.5 Protocol. §8 audits the conjecture internally (§8.3.5) and gates it on Proposition 8.5.2.

---

## §5.5 — Necessity of each condition (falsification-table reference)

Each condition is independently necessary — dropping any one produces a counterexample stream that is not in coherence-regime yet satisfies the other three.

| Condition dropped | Counterexample structure | Anchor falsification source |
|---|---|---|
| C_sep | Streams with overlapping-DOF objectives; destructive interference observable | F2 |
| C_meas | Pre-measurement-indefinite streams; γ-drift without corrective pull | F3 |
| C_scale | DAG-inconsistent streams; child-γ and parent-γ decoupled | F4 |
| C_dyn | Frozen-γ streams; γ stationary over extended interval | F5 |
| All four | Random-γ streams; joint-exceeds-bound in E[D] | F1 |

*The numbering is Anchor §9.7's and nothing else: F1 is the joint test, F2–F5 drop one condition each in the order the conditions are stated, and F6 is the meta-falsification of the construction record, which is not a condition-drop and so has no row here.*

§9's trajectory-divergence construction gives the quantitative form of each row.

---

## §5.6 — Open questions for §5 (per Anchor §9.9)

- **Q1 (cross-metric invariance).** Whether the outperformance ordering is invariant across choices of d in D. §9 resolves this.
- **Q2 (regime-boundary topology).** Whether coherence-regime is an open condition in an appropriate topology on 𝒞_Streams. Open; depends on §9's D-continuity.
- **Q3 (self-reference closure generalization).** Whether every framework passing its own tests exhibits Principle-structure. Open; meta-question, not formally closable in this volume.

---

## §5.7 — Forward-pointers

- **§6** (Triple): already drafted; C_scale multi-scale consistency uses the Triple's recursive decomposability (Lemma 6.3.2) for DAG-child-γ construction.
- **§7** (Filtering): C_meas refresh-events are formally σ-algebra events on Ω_S; Bias(S) measurability under C_meas is §7's content.
- **§8** (F-as-stream): full construction + audit of the §5.4 self-reference closure.
- **§9** (D trajectory-divergence): D's functorial construction + cross-metric invariance result.
- **§10** (TikZ reference figures): Figures 9.1 (D trajectory), 9.2 (four-conditions schematic), 9.3 (self-reference closure) per Anchor §9 reference-figure list.

---

## §5.8 — Surfaced-lemma register

Two flags surface this pass:

- ⚑ §5.2.5 Joint-sufficiency proposition with independence-by-counterexample → Anchor §9.2 target — proposition (explicit joint-sufficiency proof)
- ⚑ §5.4.1 F-as-stream formal structure (σ_F, C_F, γ_F), with K_F and Ω_F derived (Remark 6.1.2) → Anchor §9.5 target — conjecture (detailed construction + audit deferred to §8)

Both flag-targets feed future Anchor revisions per the SCOPE §8 rhythm.

---

