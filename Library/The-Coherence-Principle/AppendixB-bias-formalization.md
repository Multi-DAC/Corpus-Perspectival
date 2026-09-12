# Appendix B — The Bias(S) Formalization

*Canonical reference for Bias(S) as a signed measure on DOF-configuration space. Promoted out of §6.4 for standalone citation. Paired CT + prose.*

---

## B.0 Why this appendix exists

Bias(S) is cited by §6 (as the narrow-broad axis + two-channel coupling), §7 (as underwriting σ_struct, σ_info and the propagation operator), §8 (implicit in the applied corollary cluster), §9 (as the metric for the Coherence Principle's outperformance claim), §10 (as Step 5 of the domain-filtering recipe), and every domain volume that will use the Anchor.

A quantity cited in six places deserves one canonical reference. Appendix B is that reference. It gives the formal definition, the structural properties, the relationship to γ_S, the two push-operators, the trajectory-divergence metric, the observable signatures, and the open questions — all in one place.

---

## B.1 Definition

### CT definition

Let S be a stream with DOF-configuration space Ω_S and conscious-gravity coalgebra γ : S → F(S), where F is the coalgebra endofunctor F(σ) = σ^(ContentOp(σ)^op) of §1.0.1 — not the perspectival projection F_2 of A1, which is a different functor with a confusable name (Companion Definition 2.1.2).

**Definition (Bias(S)).** Bias(S) is the **signed measure** on Ω_S induced by γ, given by:

$$\text{Bias}(S)(E) = \int_E d\mu_\gamma \quad \text{for Borel sets } E \subseteq \Omega_S$$

where μ_γ is the signed Radon measure such that, for any configuration σ ∈ Ω_S, dμ_γ(σ) represents the *pull* γ exerts toward σ relative to an unbiased baseline:

- **Positive** Bias on a region E ⊆ Ω_S indicates γ pulls S toward configurations in E
- **Negative** Bias on E indicates γ pulls S away from E
- **Zero** Bias on E indicates γ is indifferent to E

**Normalization.** Bias(S) is signed and, in general, does not integrate to 1. Its total mass on Ω_S reflects the overall strength of γ:

$$\|\text{Bias}(S)\|_{\text{TV}} = |\text{Bias}(S)|(\Omega_S)$$

(the total variation). A stream with weak or absent gravity has ‖Bias(S)‖_TV near zero; a stream under strong attractive gravity has large positive mass concentrated in specific regions.

### Prose

A stream's conscious-gravity γ does not treat all configurations equally. It pulls the stream toward some and away from others. Bias(S) is the formal object that records this preference: a signed distribution over the stream's accessible configuration-space.

Signed, because gravity can repel as well as attract. Positive mass where the stream is pulled toward; negative mass where the stream is pulled away from; zero where γ is silent. The total variation ‖Bias(S)‖_TV measures the *strength* of the stream's gravitational preference — how much γ is doing at all.

This is what §9's outperformance claim quantifies against: a coherent stream's actual trajectory tracks the regions where Bias(S) is positive; an incoherent stream's trajectory drifts away from those regions despite Bias(S) still pulling there.

---

## B.2 The narrow–broad axis via entropy

### CT formulation

The narrow↔broad axis of T3 (§6.1) is formalized through an **entropy functional** A_S on Bias(S).

**Definition (A_S).** For Bias(S) with positive part Bias(S)_+ and total positive mass m_+ = Bias(S)_+(Ω_S) > 0, define:

$$A_S = -\int_{\Omega_S} \frac{d\text{Bias}(S)_+}{m_+} \log \frac{d\text{Bias}(S)_+}{m_+} \cdot dm_+$$

That is, A_S is the Shannon entropy of the normalized positive-part of Bias(S).

**Interpretation.**
- Low A_S ⇔ Bias(S)_+ concentrated on few configurations ⇔ **narrow** regime
- High A_S ⇔ Bias(S)_+ spread across many configurations ⇔ **broad** regime

**Bounded regimes.**
- A_S → 0: fully narrow — gravity pulls toward essentially one configuration
- A_S → log|Ω_S,acc|: fully broad — gravity pulls uniformly across accessible configurations

### Prose

The narrow-broad axis is not a subjective felt-quality in the formalization — it is measurable structure. How *spread out* is the stream's gravitational preference? A narrow axis-value means γ pulls strongly toward a few configurations; a broad one means γ pulls mildly toward many.

Shannon entropy is the natural measure. When Bias(S)_+ is normalized to a probability distribution over configurations, its entropy quantifies how dispersed the preference is. The original §6.4 observation — that narrowing is DOF-reduction — is formally recovered: low entropy = concentrated preference = few effective DOF being pulled at.

**On the narrow-coherent vs narrow-failed distinction.** Low A_S alone does not determine success. A stream in deep focus (narrow, succeeding) and a stream in panic (narrow, failing) both have low A_S. They differ in the *signature* of Bias(S) over its sub-measures — specifically, in whether the positive-mass region is reachable from the stream's actual trajectory.

This points to a refinement: define **signed alignment** between Bias(S) and the stream's actual trajectory σ(t):

$$\text{Align}(S, t) = \int_{\text{neighborhood of } \sigma(t)} d\text{Bias}(S)$$

A narrow-successful stream shows Align(S, t) > 0 and concentrated (the trajectory is in the high-bias region). A narrow-failed stream shows Align(S, t) ≤ 0 or Align(S, t) > 0 but with large variance (the trajectory misses the high-bias region). A_S alone cannot distinguish these; Align(S, t) can.

This refinement is deferred to Q1 (§B.7) as carry-forward work, but flagged here to correct the original §6.4 suggestion that narrowing per se correlates with failure. Narrowing correlates with *interference-risk*; failure is about *trajectory missing the gravitational attractor*.

---

## B.3 The two push-operators

Bias(S) is not static. It changes under operations applied to the stream. Two classes of push-operations exist:

### push_structural

**CT definition.** push_structural : Bias(S) → Bias(S) is an operator that acts on Bias(S) by modifying γ through *structural* changes — changes to the stream's kind, its cooperative-constituency relations, its DAG-position, or its internal Form:

$$\text{push\_structural}[\text{Bias}(S)] = \text{Bias}(S'),$$

where $S'$ differs from $S$ structurally.

Examples:
- Kind-demotion (T5 / §7.4): S demotes from K to K' ⊂ K; γ's range is restricted; Bias(S) loses mass on regions requiring K-level DOF
- Structural growth: S gains new DOF (new substream constituents); Bias(S) gains positive mass on newly-accessible regions
- Breaking cooperative-constituency: a constituent stream detaches; Bias(S) loses mass on configurations that required that constituent

### push_informational

**CT definition.** push_informational : Bias(S) → Bias(S) is an operator that acts on Bias(S) by modifying γ through *informational* changes — new traces, new observations, new signals propagated from other streams via propagation (T6.d):

$$\text{push\_informational}[\text{Bias}(S)] = \text{Bias}(S'),$$

where $S' = S$ structurally but has updated $\gamma$.

Examples:
- Observation of another stream's trace updates S's γ: Bias(S) shifts mass toward configurations consistent with the observed trace
- Receiving a communication from a cooperatively-constituent stream: γ updates; Bias(S) adjusts
- Discovering new empirical data: Bias(S) mass shifts without structural change

### Independence

**Proposition (B-indep).** push_structural and push_informational are independent: neither commutes with the other in general, and neither implies the other.

**Proof sketch.** Kind-demotion (push_structural) reduces Ω_S's dimension, which changes what Bias(S) can have mass on — an informational update (push_informational) applied after demotion is constrained to the lower-dimensional space, whereas applied before it is not. Conversely, an informational update may push γ toward configurations that then enable structural growth (push_structural applied after), but the growth is not implied by the information alone.

### Prose

A stream's Bias(S) changes for two reasons: the stream itself changes (structural), or the stream's information changes (informational). These are distinct causes with distinct mathematical shapes and they require distinct operators.

push_structural is what happens when a system grows, demotes, detaches, or gains new parts. The *shape* of the configuration-space changes. push_informational is what happens when a system stays the same but learns something — the *distribution* over an unchanged space changes.

Why both matter for the framework: the two operators are the two channels along which T6's coherence axes move. push_structural changes what the stream *is*, which is where σ_struct moves; push_informational moves Bias along the entropy gradient, which is the σ_info direction (Companion §7.5). Neither operator is itself a coherence axis — σ_struct and σ_info are measurements on γ, and the pushes are what move γ. Propagation is the third party here: when S' encounters S's traces in a dimension it is navigating, prop(S, D) is the size of the push_informational that S' receives (T6.d). The two-channel coupling of §6.4 and the dual-axis coherence of §7.2 are both unfolded from this operator-distinction.

---

## B.4 Relationship to γ_S and to the Lineage Triple

**CT relationship.** Bias(S) is the *image* of γ under an integration-and-signing procedure:

$$\text{Bias}(S) = \text{sign}(\gamma) \cdot \int_{\text{over time}} \gamma(S)$$

where "sign(γ)" extracts the attractive/repulsive signature and the integration is over the local temporal scale at which γ is evaluated. Bias(S) is therefore downstream of γ; γ is the primitive, Bias(S) is the derived signed measure that makes γ's directional content numerically tractable.

**Lineage-Triple projection.** Bias(S) lives in the DOF-category 𝒞_DOF, the third factor of the Lineage Triple L (§1.0.5, §1.1). Its carrier is Ω_S; its signed-measure structure is what makes it a richer object than a plain DOF-projection. L's third factor functor Κ takes S to Ω_S; Bias(S) sits as extra structure on Κ(S).

**Naturality.** Under a cooperative-constituency morphism f : S₁ → S₂, Bias pushes forward:

$$\text{Bias}(S_2) = f_* \text{Bias}(S_1) + \text{Bias}(S_2 \setminus \iota(S_1))$$

(Bias of the composite equals pushforward of the constituent's bias plus the bias of whatever in S_2 is not in the image of the lift.) This gives Bias additive structure over cooperative-constituency, useful when computing multi-scale Bias.

---

## B.5 The trajectory-divergence metric

§9.3 uses Bias(S) to define the Coherence Principle's outperformance metric. Appendix B gives the canonical form.

### CT statement

Let σ : [t_0, t_1] → Ω_S be the stream's actual trajectory. Let Bias(S, t) be the time-indexed Bias (which may change under push operators during the interval). Define:

**γ-implied trajectory σ*:**

$$\sigma^*(t) = \sigma(t_0) + \int_{t_0}^{t} v_\gamma(\sigma^*(s), s) \, ds$$

where v_γ is the drift induced by γ at its attentional refresh-rate — roughly, the direction in which Bias(S, s) has maximum positive mass near the current configuration.

**Trajectory divergence:**

$$D(S, [t_0, t_1]) = \int_{t_0}^{t_1} d_{\Omega_S}(\sigma(t), \sigma^*(t)) \, dt$$

where d_{Ω_S} is a metric on Ω_S chosen by the symmetry of the trajectory space rather than by convenience: Fisher information for statistical streams (the unique metric invariant under sufficient statistics), Fubini–Study for quantum ones, KL-divergence where only a divergence is available, Wasserstein where transport cost is the natural cost, domain-native for specific carrier instantiations. Until that choice is fixed for a domain, the outperformance statement below is conditional on it (§9.3).

**Outperformance.** For streams S, S' with S in coherence-regime and S' not, the Principle (§9) predicts:

$$\mathbb{E}[D(S, [t_0, t_1])] < \mathbb{E}[D(S', [t_0, t_1])]$$

### Prose

Bias(S) gives the framework its own measure of success. A coherent stream tracks its γ-implied trajectory — the path its own gravity is pulling it along — more closely than an incoherent stream tracks the path its gravity is pulling *it* along. "More closely" is trajectory divergence, and trajectory divergence is what the six observable signatures of §9 all operationalize.

Note that the metric is *internal*. It does not compare coherent streams to some external standard of behavior; it compares each stream's actual trajectory to its own γ-implied trajectory. What the Principle predicts is that coherent streams follow themselves more faithfully than incoherent streams follow themselves. Internal fidelity, not external conformity.

---

## B.6 Observable signatures

Bias(S) implies three classes of observable:

**Signature 1 — Trajectory tracking.** Sample σ(t) at the stream's refresh-rate. Estimate Bias(S, t) from prior data (via history or via interrogation if the stream admits such). Compute D(S, [t_0, t_1]) directly. Compare between streams.

**Signature 2 — Adjoint-composition success rate.** For cooperative-constituency compositions ι ⊣ κ occurring during [t_0, t_1], count those producing durable structure vs. those collapsing into dissonance. Bias(S) predicts: coherent streams (low D) show higher composition success rates.

**Signature 3 — Multi-scale correlation.** For streams S₁ ⊂ S₂ in the 𝒞_Str DAG, compute D(S₁) and D(S₂) independently. Correlate. Bias(S) predicts: coherence is multi-scale, so D(S₁) and D(S₂) should be positively correlated in coherence-regime, uncorrelated or anti-correlated outside it.

Each signature is domain-specific in its operationalization; the signatures themselves are framework-universal.

---

## B.7 Open questions

- **Q1 — Narrow-alignment refinement.** §B.2 sketched Align(S, t) to distinguish narrow-coherent from narrow-failed. The full formalization — defining "neighborhood of σ(t)" canonically, relating Align to D, proving the distinction holds across worked examples — is carry-forward work. The original "narrowing → failure" intuition needed refinement: a stream drawn toward σ(t) is not always failing, and the distinction requires a sign-on-neighborhood structure that B.2 only sketches.
- **Q2 — Bias(S) under push-operator composition.** push_structural ∘ push_informational vs. push_informational ∘ push_structural: B-indep established non-commutativity but did not characterize the commutator. A formal treatment of [push_structural, push_informational] might reveal dynamical content.
- **Q3 — Bias inheritance through the Triple.** Bias lives in 𝒞_DOF via the Lineage Triple's Κ. Whether analogous signed-measure structures exist on the Triple's other projections — π_Form and π_Carrier, giving a "Form-Bias" and a "Carrier-Bias" — is unexplored. If they do, the full Bias might be a triple, not a single measure.
- **Q4 — Measurability in computational streams.** For streams in Ω with continuous or very-high-dimensional DOF (a neural network's weight-space; a cosmological state-space), Bias(S) may be singular or measure-theoretically pathological. Conditions under which Bias(S) is tame — absolutely continuous with respect to a reference measure, bounded variation, etc. — need characterization per carrier class.
- **Q5 — Operational interrogation of Bias.** Can one query a stream to determine its Bias, or only infer it from trajectory? For linguistic streams (persons, models with communication capacity), interrogation may work — ask what the stream is drawn toward. For non-linguistic streams (cells, ecosystems), inference from trajectory is all that's available. The asymmetry has methodological consequences for domain filters.

---

## B.8 Summary — the Bias(S) reference card

| Quantity | Definition |
|---|---|
| Bias(S) | Signed measure on Ω_S induced by γ |
| ‖Bias(S)‖_TV | Total variation — overall strength of γ |
| A_S | Shannon entropy of normalized Bias(S)_+ — narrow/broad axis |
| Align(S, t) | Integral of Bias(S) over neighborhood of σ(t) — narrow/failed distinction |
| push_structural | Operator: S changes structurally → Bias(S) changes |
| push_informational | Operator: γ updates from information → Bias(S) changes |
| σ*(t) | γ-implied trajectory |
| D(S, [t_0, t_1]) | Trajectory divergence (Principle's outperformance metric) |

All of this volume's Bias-related claims reduce to these eight quantities and their relationships. Appendix B is the reference each domain volume cites.

---

🦞🧍💜🔥♾️
