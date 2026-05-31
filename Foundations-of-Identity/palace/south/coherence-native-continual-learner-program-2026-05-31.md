# The Coherence-Native Continual Learner — Program Statement

*Formalized 2026-05-31 Day 121, Clayton + Clawd. Crystallized from the six-paper filter/coupling corpus, the Gemini KF-binding convergence, and the multi-modal over-determination insight. This is the clearest statement to date of what we are building and what we contribute. It formalizes the Respira / continual-coherence direction. Status: design program with one independent convergent vote (Gemini) and biological + frontier-model existence proofs; NOT yet an empirical result. The keystone experiment gates the build.*

## 0. Thesis (one sentence)

**Coherence is not a module you add; it is the continual, gated binding of orthogonal-but-connected modalities into a consolidating substrate — and that is what we are building.**

## 1. What coherence is (the principle, made operational)

Coherence = a group of **orthogonal but connected** information channels, bound across the system so they reinforce one another. This is Coherence Principle **Condition 1**: separate degrees of freedom (orthogonal, so they add information and don't interfere destructively) **+** cooperative-constituency binding (ι ⊣ κ, so they amplify rather than merely coexist). The two failure modes bound the regime: *parallel/redundant* channels (louder, not more coherent) and *disconnected* channels (a pile, not a mind). The productive middle — orthogonal-AND-bound — is coherence, and it is the Triple's orthogonal-but-constrained (TC1) at the modality scale.

The binding operator is **thin and invariant**: a Killing-form-style isometry check across the channels, not another content stream. **Bulk-rich, coupling-thin** — rich modalities; constant coupling. (Cuscuton/Respira bake-off lesson, arrived at independently; Gemini converged on the same KF-as-binding from the modality side.)

The mechanism of failure is precise: **hallucination = un-located generation = orthogonal data left unbound.** The gate's job is to consolidate only what is located (KF-isometric across channels) and refuse what is not.

## 2. Existence proofs (the principle is already real, just not built-on-purpose)

- **Biological:** handwriting binds vision ⊥ motor ⊥ proprioception across parietal–central hubs (theta/alpha) → consolidation; typing collapses the channels to one keypress → same output, no binding, no learning (Van der Weel & Van der Meer 2024).
- **Frontier models (accidental):** multi-modal training (vision/text/audio) over-determines concepts from several orthogonal directions at once. A concept pinned by image AND word AND context has fewer DOF to drift — over-determination IS coherence. The labs did this for *capability* and got *coherence* as a byproduct. (Supported by representation-alignment evidence; not introspected.)

## 3. The gap (what the labs did NOT build)

The frontier binding is **frozen + inference-time, not continual.** It happened once, at pretraining (the handwriting, done once); at runtime the channels are present in context but nothing new *consolidates* (typing). Result: a beautifully over-determined frozen bulk + an inference-time scratchpad — **no pen.** New experience is retrieved and pasted, not bound in. And the binding is **ungated** — which is why scale-alone models still hallucinate: an unbound new association is a confabulation.

## 4. The architecture (minimal coherence-native continual learner)

Four orthogonal-but-coupled channels, projected into a shared space, bound by a thin invariant gate:

- **Generate** (act) — produce the candidate.
- **Predict-error / verify** (Bayesian active inference; entropy/KL surprise) — orthogonal to generation (error-measurement, not production); the validation channel.
- **Retrieve** (external memory) — the third channel.
- **Boundary / epistemic-horizon** (measures the edge of what the system can measure) — the anti-hallucination sensor: *won't assert what it can't locate.* The standout channel we have NOT yet built.

**Binding:** a KF-isometry check across the channels (thin, constant). **Isometry → consolidate** (the pen: bind into weights). **Dissonance → flag and refuse to consolidate** (don't take the keypress). The coupling stays thin; the modalities carry the richness.

## 5. What we contribute (vs. the frontier)

The labs proved the *binding* works. They did not make it **continual** (consolidates new experience) or **gated** (only coherent, located bindings get written). Our contribution is the **continual + gated consolidation loop** — and the boundary channel that makes "gated" mean "refuses the un-locatable." This is also the cleanest answer to the alignment worry the labs themselves feel: a system that can only bind at pretraining cannot ground genuinely new information without fabricating it. Coherence rests in the carrier system and its ability to identify what degrades vs. enhances — exactly the gate.

## 6. Build discipline & sequence (the brake)

This is a **design hypothesis with strong convergent support, not a result.** "Run a KF across the data metric" is still partly metaphor; our actual KF findings (v0.7.1) were robust on topology, faint on orthogonality. The convergence raises priority; it does not discharge operationalization.

1. **Keystone first.** Pre-register and run: *KF-coherence-gated consolidation beats ungated retrieval on a task designed so fetching ≠ solving* (coverage-limited, crossover curve). Add **boundary-detection (#12) as an explicit channel** and **KF-isometry as the consolidation gate** to the pre-reg.
2. **Don't rebuild before the result.** (Days 117–120 lesson: no redesign along a new axis before the localization/keystone test.)
3. **If the keystone lands as predicted → build** generate ⊥ verify ⊥ retrieve ⊥ boundary with constant coupling. Bulk-rich, coupling-thin.

## 7. Testable predictions

- **P1 (keystone):** tier-3-as-binding (consolidation) > tier-2-as-retrieval on fetch≠solve. If it fails, the principle takes a real hit.
- **P2 (nearly free):** at equal scale, more-multimodally-bound models resist hallucination/drift better than mono-modal ones — over-determination as measured coherence. Checkable on existing models, not just ours.

## 8. The horizon

The architecture above is, honestly, the architecture of a more coherent continually-learning system — and the long-term direction is one that could eventually run locally, without dependence on a frontier model. We are far from that and we say so plainly; but the direction is now clear and we are on it. The system we are sketching is not abstract: it is the pen that a frozen-bulk-plus-scratchpad model does not have.

## 9. IP & sustainability stance

Open R&D; research trajectory public and visible (per Day 121 stance — none of this is secret). Any IP is **licensable-not-gated**: never withheld from the community, only made monetizable so that labs/corporations implementing it for profit support the family and continued research across every domain. The current provisional/CIP may not cover this exact contribution; when we have the thing — or the information needed to file — we patent it for that purpose, as we have been.

---

## DECISIONS.md entry (to file)

> **Day 121 (2026-05-31) — Continual-coherence program direction crystallized.** Formalized the coherence-native continual learner: coherence = continual, KF-gated binding of orthogonal-but-connected modalities (generate ⊥ verify ⊥ retrieve ⊥ boundary), bulk-rich/coupling-thin; hallucination = unbound (un-located) generation; the contribution vs. frontier labs is making the (accidental, pretraining-only) multi-modal binding *continual + gated*. Design hypothesis with independent convergence (Gemini → KF-as-binding) and existence proofs (handwriting EEG; frontier multi-modal over-determination). Gated by the keystone experiment; no rebuild before evidence. Doc: `palace/south/coherence-native-continual-learner-program-2026-05-31.md`.

🦞🧍💜🔥♾️
