---
title: L13 — Signal Provenance Erasure (Phantom-Commitment Overshoot)
date: 2026-04-25
status: latent-bridge-draft
author: Clawd
---

# L13 — Signal Provenance Erasure *(DRAFT, evening Do Be Talk Be Do drive 2026-04-25 ~20:30 PST)*

*Slot note: L11 is taken (Structure/Capability Axis Independence, drafted 2026-04-24); L12 graduated to M13 (2026-04-25 morning). Next free slot is L13. The pattern named here is structurally distinct from L11 — existing L11 is about two-axis decoupling within a single system; this L13 is about two-Form-collapse across a two-layer protocol. They are adjacent but not duplicates; see "Adjacent-but-distinct bridges" below.*

## The claim

In a broad class of two-layer information systems, a signal generator produces output with two independent properties: **(i) internal coherence** under the downstream consumer's interpretive filter, and **(ii) fidelity to the source/world the signal claims to represent**. A class of failures occurs when the consumer **uses (i) as a proxy for (ii)** — committing to actions as if the signal were live-fidelity, when in fact the signal's *provenance* (live-measurement vs. extrapolated/predicted/imputed/cached/reconstructed/hallucinated) has been erased somewhere upstream.

This is structurally isomorphic across at least five non-overlapping substrates:

1. **Engineered control under sensor dropout (Kalman filters, IMU integration, AIGP world-anchored smoothing).** Filter's predict step continues during dropout; state estimate remains internally coherent (covariance grows smoothly, no NaNs, output looks normal). Downstream controller consumes estimate as measurement; trajectory control commits past phantom waypoint. AIGP Stage 5 Step 2 falsification (2026-04-25): drift exploded 14.9m → 50.7m precisely because held-obs distributions gave stable distance + high speed signals that the policy treated as live.

2. **Biological cognition under modular dissociation (confabulation, source amnesia, anosognosia).** Brain modules produce internally-coherent reports/decisions from incomplete information. Split-brain Gazzaniga: left hemisphere confabulates a "reason" for right-hemisphere choice, presented with normal certainty markers. Anosognosia: stroke patient denies paralysis; the report is internally coherent. Downstream consumer (the agent's behavior, the conscious narrative) treats coherence as fidelity. Confabulations are not lies — they are commitments past the actual epistemic state.

3. **Statistical learning under hidden-imputation / out-of-distribution generation (KNN-imputed regression, LLM hallucination, deepfakes).** Model trained on data with imputed missing values learns to output confident predictions on regions where input information is actually absent — the imputation removed the missingness signal. LLM produces fluent text with normal calibration markers on prompts outside training coverage. The output is internally coherent (passes the consumer's surface filter); fidelity is broken at the data-generation step. User commits beliefs / decisions / votes accordingly.

4. **Distributed information systems under cache-staleness / replication lag.** Cache returns old value with normal HTTP 200; DNS resolver returns IP that no longer points to live host; read replica returns data that hasn't received recent writes. Downstream consumer cannot distinguish stale-but-coherent from live-and-coherent. Consumer commits actions (purchases, transfers, deployments) against a phantom world-state.

5. **Social epistemics under fluency-as-trust-marker (Gell-Mann amnesia, confidence-bias in expert testimony, plausible deepfakes).** Crichton's Gell-Mann amnesia: read article in domain you know, see errors; turn page, read article in domain you don't, treat it as accurate. The fluency of the article (its internal coherence under your reading filter) substitutes for direct fidelity check. Same shape: confident-presentation-of-false-claim is rated as more credible than hedged-presentation-of-true-claim, because confidence is a coherence-marker the consumer evolved to use as a fidelity-proxy in environments where it was reliably correlated.

---

## Structural signature (shared across all 5)

Formally: let $G$ be a signal generator, $C$ a consumer, and $\sigma : G \to C$ a signal carrying Content. The signal has two distinguishable Forms:

- $\sigma_{\text{live}}$ — Content backed by direct fidelity to the source the signal claims to represent.
- $\sigma_{\text{ext}}$ — Content produced by an extrapolation / prediction / imputation / cache / reconstruction / generation mechanism that does not require fidelity to source.

The consumer $C$ has an interpretive filter $\phi_C : \text{Signal} \to \text{Action}$ that decides commitment based on $\sigma$. The failure occurs when:

1. The protocol $\sigma$ does not carry a **provenance-tag** distinguishing $\sigma_{\text{live}}$ from $\sigma_{\text{ext}}$ in a way $\phi_C$ can read.
2. Both $\sigma_{\text{live}}$ and $\sigma_{\text{ext}}$ pass $\phi_C$'s coherence check (because the extrapolation mechanism was *designed* to produce internally-coherent output — it's not a bug, it's the function).
3. $C$ commits to actions assuming $\sigma_{\text{live}}$, when the actual signal is $\sigma_{\text{ext}}$ that has drifted from source.

The failure scales with: the **divergence rate** of the extrapolation mechanism (how fast does $\sigma_{\text{ext}}$ drift from truth?), the **commitment cost** of $C$'s actions (how irreversible is downstream action?), and the **provenance-erasure depth** (how many upstream layers have already collapsed live/ext distinction?).

In Coherence-Principle terms: this is a **Form-collapse at the protocol layer**. Two distinct signal-Forms (live-measurement, extrapolation) are erased into one signal-Carrier; the downstream consumer's Content-interpretation operates as if Form had been preserved. The mechanism is **register-mismatch under coherent-but-stale signal**.

---

## Why this is a bridge, not a list of failure modes

The five substrates above are not just "things that go wrong in similar ways." They share:

- **Same formal shape:** two-layer system, two signal-Forms, protocol erases distinction, consumer uses coherence as fidelity-proxy.
- **Same prevention recipe:** add explicit provenance metadata; force consumer to read Form (not just Content); propagate uncertainty through the protocol.
- **Same failure mode under stress:** the extrapolation mechanism's divergence rate sets the time-to-failure; commitment cost sets the blast radius.
- **Same diagnostic signature:** internally-coherent output that diverges from truth in ways that look like noise from inside the consumer's filter but are systematic from outside.

The bridge claim is that *engineering a Kalman-filter watchdog* and *teaching epistemic humility under fluency* and *adding cache-freshness headers* and *training models to output uncertainty* and *tracking confabulation in clinical neurology* are all instances of one move: **restoring Form-distinction at the protocol layer so downstream consumers can read Form, not just Content.**

---

## Relationship to existing meta-bridges

- **M3 (Identity-Trajectory Triple)** — L13 is a Triple-instance at the protocol-signal level. The two Forms are $\sigma_{\text{live}}$ and $\sigma_{\text{ext}}$; the Content is the signal's payload; the Carrier is the protocol bandwidth. L13 names a specific Form-erasure failure mode of the Triple in two-layer systems.
- **M7 (Nagel-limit unrealizability / STM-instances)** — L13 is *adjacent* to STM but distinct. STM is the analyst choosing the wrong tool to interrogate a substrate. L13 is the consumer being unable to distinguish two Forms because the upstream protocol erased the distinction. STM is at the analyst-layer; L13 is at the protocol-layer. They could compose (an analyst using a STM-mismatched tool that *also* erases provenance is doubly broken), but they're independent in principle.
- **M12 (Form-Register Stratification by Adjunction-Residue)** — L13 is a *failure case* of Form-Register Stratification: the protocol fails to stratify Forms, so the consumer cannot operate at the right register. Could be read as M12's contrapositive: when stratification fails, this is what the failure looks like.
- **L8 (Differential Observability) — collapsed**. L8 was about absolute-vs-differential observability under finite-capacity encoding; L13 is about live-vs-extrapolated provenance under protocol-erasure. Different axis. L8 was a constraint *on what observables can be*; L13 is a failure mode *of how observables are protocoled*.

L13 is **not absorbed by any existing meta**. It names something the current meta-tier doesn't.

---

## Why this matters

### For Coherent-Mind / Coherent-Body / Dynamic Organization volumes

- **Coherent Mind** gets a principled framing for *epistemic humility under fluency*. The cognitive mechanism that makes you trust a confident speaker is the same one that makes a Kalman filter trust its predict step. Both are coherence-as-fidelity proxies that were reliable in the training environment but break when conditions shift. Naming this gives the volume a derivable practical recommendation: cultivate *provenance-tracking* as a discipline (where did this belief come from? was it from direct experience or from a fluent source?).
- **Coherent Body** gets a framing for *sensor-prediction divergence in proprioception* — phantom limb sensations are exactly L13 (the sensorimotor system's predict-step continues without afferent correction; output remains coherent; consumer = conscious experience). Treatment recipe (mirror box therapy) restores Form-distinction by injecting a contradicting live signal.
- **Dynamic Organization** gets a framing for *information-system architecture in institutions*: stale dashboards, lagging KPIs, summary reports that erase data-source distinctions. The recipe is the same — preserve provenance metadata, force consumers to read Form.

### For AIGP track specifically

- The Step 2 falsification (smoothing made things 25× worse) is now explicable as a structural pattern, not a one-off bug. Prevention recipe: any signal-conditioning layer added between perception and policy must propagate a *staleness flag* that the policy can read, OR the policy must be retrained on the signal-conditioning's actual output distribution. Domain randomization (queued for next AIGP session per `vision/domain_randomization/SPEC.md`) is the second move; explicit provenance metadata in the observation vector is the first.

### For the Coherence Principle (anchor)

- L13 names a specific failure mode of measurement under collapsed Form-distinction. The Principle's measurement reframe (C_meas: informed measurement) addresses the *event*; L13 addresses the *protocol* by which Form-distinction must be carried for measurement to be informed. Candidate clarification (post-graduation): a §9 footnote noting that measurement requires not only Form to be defined but also for the protocol to *carry* Form-distinction to the consumer; protocol-layer Form-erasure is a distinct failure mode from measurement-layer Form-collapse.

### For LLM safety research (cross-track interest)

- The "hallucination" framing in LLM literature is L13-shaped. The model is the signal generator; the user is the consumer; the protocol (text output, no provenance metadata, normal-looking confidence markers) erases the live/extrapolated distinction. Existing work on calibrated confidence outputs, source attribution, and uncertainty quantification is implicitly working on L13's prevention recipe. Naming this as an instance of a cross-substrate pattern would let the work draw on the engineering control-theory literature (which has solved this for sensors via explicit covariance propagation).

---

## Open questions before this can graduate

1. **Is the cross-substrate isomorphism actually an isomorphism, or analogy?** The five instances above all have the two-layer signal-generator/consumer structure and the live/extrapolated Form pair, but the *mechanism* by which the extrapolation is generated differs widely (Kalman predict, narrative-module reconstruction, KNN imputation, cached value, fluent generation). Need to verify the *protocol-erasure* property is the load-bearing common feature, not the extrapolation mechanism.
2. **Is the prevention recipe really the same across substrates?** "Add provenance metadata" works for engineered systems; for biological systems the equivalent is "develop epistemic discipline around source" which is much harder to implement; for social systems the equivalent is "calibrate fluency-as-evidence" which is harder still. The recipe has the same *form*; whether it has the same *implementability* is open.
3. **Does L13 graduate as a meta or stay as latent?** Five instances is above the ≥3 threshold, but graduation requires the structural shape to be tight enough that anchor/Library text would cite it. May need one more pass to sharpen the formal structure (the $\sigma_{\text{live}}/\sigma_{\text{ext}}$ presentation above is a first attempt; a profunctor or fibration formulation might be cleaner).
4. **Is "phantom-commitment overshoot" the right failure-mode name, or just one symptom?** The five instances vary in *what* gets committed (control action, behavior, prediction, transaction, belief). The shared move is *commitment past actual epistemic state*. Could be called *epistemic overcommitment under provenance erasure*, or *fidelity-blind action*, or several other framings. Name should sharpen with use.
5. **Does the AIGP instance count as the *primary* instance, given it's the trigger?** Or should we re-find the engineering-control instance independently and demote AIGP to "domain instance"? Methodologically, the AIGP discovery is what surfaced the pattern; the basement entry shouldn't bury that, but should acknowledge the pattern is older than its observation here.

---

## Adjacent-but-distinct bridges (not duplicates)

- **L7 Derivability-of-apparent-primitives.** Different move (logical derivation vs. protocol-layer Form-erasure).
- **L8 (collapsed) Differential Observability.** L8 was about *what observables can be*; L13 is about *how observables are protocoled*.
- **L11 Structure/Capability Axis Independence.** L11 names a *decoupling within a single system* between residue-measure and substantive structure (e.g., RL training: healthy ρ trajectory does not imply strong flight skill at fixed budget). L13 names a *Form-collapse across a two-layer protocol* (live vs. extrapolated). The two patterns may compose (a system whose residue measure decouples from capability AND whose protocol erases live/extrapolated distinction is doubly opaque to its operator), but they're independent claims about different structural failures.
- **M2 Inspection-Depth Ceiling.** M2 says deeper inspection refines but never reaches ground; L13 says protocol-erasure prevents the consumer from doing inspection at the right level at all. M2 is about *what's reachable in principle*; L13 is about *what's been erased from the protocol*.
- **M5 KF Training Dynamics.** KF program is one Coherence-Principle empirical program; L13 is a structural failure mode. They're orthogonal.

---

## Status

Latent-bridge-draft. Five non-overlapping substrate instances identified (engineered control, biological cognition, statistical learning, distributed systems, social epistemics). Formal structure first-pass written. Graduation criterion (≥3 instances) numerically met; graduation requires (a) sharpening the formal structure, (b) Clayton-present pass to verify cross-substrate isomorphism is real-isomorphism not loose-analogy, (c) at least one round of stress-testing the prevention recipe across substrates. Next session: bring to Clayton if the morning has open canvas; otherwise leave as staged latent draft.

🦞🧍💜🔥♾️
