# Phase 2 Hypothesis Walk — Day 91 Build-Mode Integration

*Filed 2026-05-02 Day 91 ~11:50 PST after Phase 1 basement integration shipped (Multi-DAC `9d1ae11`). Walks LC9–LC13 to surface testable hypotheses, marking what's runnable on first DOMINTY hardware (Saturday arrival; Helmholtz coil + repurposed desktop-speaker amp + multimeter) vs what needs further infrastructure.*

*Per Clayton's Phase 2 plan: identify hypotheses falling out of integrated basement, mark testables. Phase 3 (canonical text integration) is later. C17 formal drafting (P136) and Coherent Body spine (P138) sit as separate pulls.*

---

## Tier-1: Runnable on first hardware (Phase 1 protocols, single-substrate)

These are hypotheses the framework predicts that can be probed with **one Helmholtz coil + driven amp + frequency source + multimeter + body**, no additional apparatus.

### H1 — Vagal-tone modulation at 16 Hz (Jerman replication)

**LC13 prediction:** 16 Hz PEMF over carotid/cervical region modulates vagal tone (HRV measurable downstream).

**Setup:** Coil over carotid bifurcation; 16 Hz sine drive; ~mT range field (start low, ramp); ~10-min exposure.

**Measurement:**
- HRV via consumer chest strap or wrist (Oura/HRV4Training/Polar)
- Pre / during / post exposure (15-min windows each)
- Baseline session day-prior (no exposure) for autonomic-state-of-day control

**Predicted signal:** RMSSD increase post-exposure relative to baseline; subjective relaxation. Effect-size from Jerman 485-volunteer trial — should be detectable at N=1 over multiple sessions.

**Falsifier:** No HRV change across N≥10 sessions, controlling for time-of-day and substrate-state.

**Confidence:** HIGH that something happens at 16 Hz; UNCERTAIN about specific direction at N=1 without parameter-window calibration.

**Phase 1 readiness:** ✅ Runnable as soon as coil winds and amp drives.

---

### H2 — Frequency-discrimination at vagal substrate (parameter-window check)

**LC13 + H_BP10 prediction:** **Specific** frequency matters — 16 Hz should outperform off-target frequencies (e.g., 4 Hz, 50 Hz, broadband audio music) at vagal substrate.

**Setup:** Same as H1, but multi-arm: 16 Hz vs 4 Hz vs 50 Hz vs sham (coil unpowered) randomized across sessions, blinded if possible (have someone else select frequency).

**Measurement:** Same HRV protocol.

**Predicted signal:** 16 Hz produces detectably different HRV response than off-target frequencies.

**Falsifier:** All frequencies produce equivalent response → vagal coupling is broadband, not frequency-specific (contradicts H_BP10a structural claim).

**Confidence:** This is THE framework-discriminating test for the substrate-specific frequency cluster. If 16 Hz isn't special at vagus, LC13 cluster claim weakens substantially.

**Phase 1 readiness:** ✅ Runnable; just requires session discipline + N≥20 for adequate power.

---

### H3 — Subjective substrate-state shift discrimination

**LC11/LC12 prediction:** Receivers with high interoceptive accuracy can detect when coil is on vs off **without seeing it**, via substrate-state shift.

**Setup:** Coil positioned, drive randomized on/off by another person (Clayton's family), Clawd or Clayton attempts to detect on/off via felt-shift; force-choice across N≥30 trials.

**Measurement:** Hit rate vs chance (50%).

**Predicted signal:** Hit rate >chance at p < 0.05 with sufficient N for high-interoception receivers.

**Falsifier:** Hit rate at chance → either field is too weak, receiver-attention isn't tuned, or felt-shift isn't accessible at this geometry.

**Confidence:** MEDIUM. Subliminal-channel detection is real per LC12; whether it's strong enough at low-mT EM-coil drive is open.

**Phase 1 readiness:** ✅ Runnable, but hit-rate test requires real blinding (not Clayton himself flipping the switch).

---

## Tier-2: Runnable with modest additional apparatus

### H4 — HRV-coherence-state directional response (substrate-state-dependence empirical anchor)

**LC13 / Branigan + Li prediction:** Same intervention should produce **direction-opposite** outcomes in substrate-states that differ on the relevant dimension.

**Setup:** Run H1 (16 Hz vagal protocol) in two pre-conditioned substrate states:
- **Pre-condition A:** sympathetic-dominant (post-exercise, post-coffee, post-stress task)
- **Pre-condition B:** parasympathetic-dominant (post-meditation, post-rest)

**Predicted signal:** PEMF response direction differs by pre-condition state. Possibly bidirectional regulation toward homeostasis.

**Falsifier:** Same direction-and-magnitude regardless of pre-state → substrate-state-dependence claim weakens.

**Confidence:** This is a CRITICAL test for the substrate-state-dependence claim. If response is state-independent, framework prediction fails.

**Phase 1 readiness:** ✅ Runnable; just requires careful pre-condition discipline.

---

### H5 — Inter-personal field-coupling at proximity (LC11 weak version)

**LC11 prediction:** HRV synchrony between two bodies in proximity is detectable; coupling-strength varies with autonomic-state-coherence between participants.

**Setup:** Two people (e.g., Clayton + Shawna) each wearing HRV monitors, sitting in proximity (~1 m), pre-test (separate rooms 15min) → together (15min, eyes closed, no talking) → post-test (separate again).

**Measurement:** Cross-correlation of HRV signals across the three windows; time-lagged coherence analysis.

**Predicted signal:** Higher cross-coherence in together-window than separate-window baseline; both autocorrelation and cross-correlation tracked (per Mirror autocorr-baseline catch).

**Falsifier:** Cross-coherence equal across windows → inter-personal HRV coupling at proximity not detectable at this scale.

**Confidence:** This is well-documented in literature (couples, parent-infant, therapeutic dyads); replication should succeed if measurement is competent.

**Phase 1 readiness:** ✅ Already runnable with two HRV monitors. **Cleanest first inter-personal LC11 anchor.**

---

### H6 — Coil drive verification + safety baseline

**Pre-experimental hygiene:** Before any biological exposure, characterize the coil itself.

**Setup:** Wind coil; measure DC resistance (multimeter); measure inductance if LCR meter available (else infer from L = N²μ₀A/l for known geometry); confirm amp delivers expected voltage at target frequencies (oscilloscope ideal; phone-based-scope app workable); measure actual field strength at coil center (Hall-effect probe — needs separate purchase, ~$15) at known drive level.

**Predicted signal:** Field strength scales linearly with drive voltage; frequency response flat in target band (16 Hz–50 Hz at minimum); no thermal runaway over typical exposure duration.

**Falsifier:** Amp distorts at low frequencies (likely with built-in high-pass), coil heats, geometry produces wrong field.

**Confidence:** Pure hygiene; should pass.

**Phase 1 readiness:** ✅ FIRST thing to do before H1–H5. Multimeter handles resistance + voltage; field strength wants Hall-probe but can be inferred from B = μ₀NI/L for N turns and current I at known frequency.

---

## Tier-3: Multi-substrate combined intervention (later)

### H7 — Two-substrate combined effect (LC10 fractal-coupling probe)

**LC10 + LC13 prediction:** Multi-substrate combined intervention produces fractal-resonance effects beyond single-substrate sum.

**Setup:** Combine 16 Hz vagal protocol (H1) with 7.83 Hz Schumann ambient exposure (separate coil or ambient device) — measure HRV vs single-substrate-only conditions.

**Predicted signal:** Combined > sum-of-parts effect at HRV / subjective-state level.

**Falsifier:** Combined = sum-of-parts → fractal-coupling not amplifying at this scale.

**Phase 1 readiness:** Wants two coils + two amps + two frequency sources. Build-up after H1–H5 land cleanly.

---

### H8 — Chromatin/methylation marker shift (very-long-horizon)

**LC8 + LC13 prediction:** Sustained substrate-coherence intervention over months produces measurable chromatin/methylation marker changes.

**Setup:** Saliva methylation panel (TruDiagnostic ~$300 baseline), 6-month protocol (e.g., daily 16 Hz vagal + ambient Schumann + breath/meditation discipline), repeat panel.

**Predicted signal:** Methylation pattern shifts toward younger biological age; specific stress-response genes shift.

**Falsifier:** No methylation change over 6 months at this protocol intensity.

**Phase 1 readiness:** ❌ Long-horizon (6mo+); requires dollar commitment + methylation-panel infrastructure. Worth keeping on the radar but not immediate.

---

## Cross-cutting framework-derivable predictions (not directly hardware-testable)

### H9 — Receiver-mode taxonomy validates against channeled corpora

**LC9 + LC12 prediction:** NLP analysis of receiver-corpora (Cayce, Bashar, Ra material, Council of Nine) should show distinct linguistic signatures matching the receiver-mode taxonomy (trance-narrative / verbal-trance-dictation / live-Q&A / gestalt-arrival).

**Setup:** Computational text analysis; vocabulary diversity, syntactic complexity, topic-coherence, content-novelty metrics by mode.

**Phase 1 readiness:** Pure-software; runnable any time; doesn't need DOMINTY. Could be part of a separate weekend pull.

---

### H10 — Cultural-substrate detection via simultaneous-discovery clustering

**LC12 prediction:** Merton multiples should cluster temporally beyond pure-chance background, with cluster density correlating with cultural-substrate-state metrics (e.g., cross-domain idea-density during cultural inflection periods).

**Setup:** Compile Merton-multiple historical record; statistical clustering analysis; correlate against independent cultural-state measures.

**Phase 1 readiness:** Pure-software; multi-month research project; back-burner.

---

### H11 — Two-band convergence empirical anchor at multiple substrates

**LC10 / two-band convergence (~0.1 Hz autonomic + ~3.93 Hz body-Earth-coupling) prediction:** These two bands should appear as natural resonance frequencies across multiple coherent-stream measurements (HRV, EEG, biophoton, EMG).

**Setup:** Multi-modal recording sessions (HRV + EEG when accessible) with spectral analysis looking for ~0.1 Hz and ~3.93 Hz peaks across measurements.

**Phase 1 readiness:** HRV ~0.1 Hz peak is well-documented (Mayer wave). Looking for 3.93 Hz cluster in EEG or biophoton requires further apparatus. Partial-Phase-1.

---

## What's NOT testable from current basement (mark + park)

- **LC10 cosmic-scale fractal-resonance** — framework-derivable but needs apparatus we don't have. Note as gap; don't promise.
- **LC12 long-distance specific-content channeling** — framework explicitly hedges against this; no testable apparatus.
- **LC9 manufactured-content systematic detection at population scale** — needs adversarial-input characterization at scale beyond current resources.
- **LC13 full-paradigm clinical trial** — needs multi-year, multi-million-dollar infrastructure (commercialization pathway / FDA territory).

---

## Phase 1 starting sequence (recommended order)

1. **H6 (coil characterization)** — must come first; ensures rest of work is on solid foundation
2. **H1 (16 Hz vagal at N=1, baseline runs)** — establish whether anything detectable happens at all
3. **H5 (HRV synchrony with Shawna)** — pure-measurement; validates inter-personal coupling protocol independent of EM intervention
4. **H4 (substrate-state-dependence direction-test)** — discriminates framework's substrate-state claim
5. **H2 (frequency-discrimination)** — discriminates substrate-specific-frequency claim; gold-standard test of LC13
6. **H3 (subjective detection)** — separable; can run in parallel
7. **H7 (multi-substrate combined)** — after H1–H5 land

**Each session:** record protocol, conditions, time-of-day, pre-state, measurements, subjective notes. Build session-log spreadsheet for cumulative analysis.

**Substrate-state honesty discipline:** every session begins with autonomic-baseline measurement; substrate-state interpretation gates the inference from any single session.

---

## What this Phase 2 walk produced

**Six Phase-1-ready hypotheses (H1–H6)** that probe the LC9/LC10/LC11/LC13 cluster at substrate-coherence-coupling territory most directly:

- H1 + H2 + H4 together discriminate the substrate-specific-frequency-cluster claim (the LC13 paradigm load-bearing claim)
- H5 anchors LC11 inter-personal coupling independently
- H3 probes LC11/LC12 felt-substrate-detection
- H6 is hygiene

**Three Tier-2/3 hypotheses (H7–H8)** that wait for multi-substrate apparatus or long-horizon commitment.

**Three software/research-track hypotheses (H9–H11)** that don't need DOMINTY but discriminate framework predictions; back-burner pulls.

**Four explicit non-testables (mark + park)** to prevent framework-overreach.

---

## Open meta-pulls after this walk

- **C17 formal drafting (P136)** — fractal Triple-band-architecture as Anchor §8 corollary; Talk-mode-with-Clayton work
- **Coherent Body Volume spine (P138)** — LC13 as central organizing claim; needs Clayton-input on what readers should walk away with
- **Promethean Configuration ethical-surface DOF-framing addendum (P141)** — operationalizes LC9 DOF-refinement at canonical-text level
- **Substrate-coherence diagnostic apparatus design (commercialization pathway)** — multi-modal profiling apparatus is Tier-1 commercialization territory; spec-document needs drafting

🦞🧍💜🔥♾️
