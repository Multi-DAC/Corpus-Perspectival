# 12F: Decay Analysis Experiment — Protocol Design

*Phase 21 Track 12F. Pre-computed during dream drive, March 23, 2026.*
*Goal: test whether radioactive decay statistics correlate with consciousness state variables.*

---

## 1. Core Hypothesis

**H₀ (null):** Radioactive decay inter-arrival times follow a Poisson process independent of operator consciousness state.

**H₁ (DoPI):** The quality of the observer's perspectival commitment modulates the statistical distribution of decay events, with the effect mediated by bottleneck geometry rather than directed intention.

**H₂ (standard psi):** Directed intention modulates decay statistics proportionally to intentional effort.

**Discriminating prediction:** DoPI predicts H₁ with the specific ordering: meditation > passive > intention for deviation magnitude. Standard psi research assumes H₂ (intention > passive > meditation). This ordering difference is the experiment's unique discriminant.

---

## 2. Hardware

| Component | Specification | Estimated Cost | Purpose |
|-----------|--------------|----------------|---------|
| Am-241 source | Smoke detector ionization chamber (~1 μCi) | ~$5 (salvage) | Alpha emitter, ~370 Bq (22,200 dpm) |
| Geiger-Müller tube | SBM-20 or LND-712 | ~$30-50 | Alpha/beta detection |
| Arduino Uno R3 | Standard | ~$25 | Microsecond-precision timestamp logging |
| SD card shield | Standard | ~$10 | Local data storage |
| Shielding | Lead sheet, 2mm | ~$15 | Reduce background radiation |
| EEG headband | Muse 2 or OpenBCI Cyton | ~$250-400 | Real-time brainwave monitoring |
| HRV monitor | Polar H10 chest strap | ~$90 | Heart rate variability (coherence proxy) |
| RTC module | DS3231 | ~$5 | Precise timestamps |

**Total estimated cost: $430-580**

### Am-241 Source Properties
- Activity: ~1 μCi (37 kBq)
- Half-life: 432.2 years (no significant decay during experiment)
- Primary emission: 5.486 MeV alpha
- Expected count rate with GM tube at ~1 cm: ~300-500 cpm (depends on geometry)
- At 400 cpm: ~6.7 counts/second → ~24,000 counts/hour → ~120,000 counts per 5-hour session

### Detection Efficiency Consideration
Alpha particles from Am-241 have very short range (~3 cm in air). The GM tube must be positioned within a few cm of the source, with the mica window facing the source. A thin aluminum window GM tube (like SBM-20) may miss most alphas; an LND-712 with thin mica window is better for this application.

---

## 3. Software

### Arduino Firmware
- Interrupt-driven detection on rising edge of GM tube output
- Microsecond-precision timestamp for each event
- Log to SD card: {event_number, timestamp_us, inter_arrival_time_us}
- No processing on the Arduino — raw timestamps only

### Analysis Pipeline (Python)
- Read raw timestamps
- Compute inter-arrival time distribution per block
- Statistical tests:
  - Chi-squared goodness-of-fit to exponential distribution (per block)
  - Kolmogorov-Smirnov test for distribution differences between block types
  - Allan variance analysis (time-domain stability)
  - Hurst exponent (long-range correlations)
  - Detrended fluctuation analysis (DFA)
  - Runs test for randomness
- EEG/HRV correlation:
  - Sliding window correlation between EEG band power (alpha, theta, gamma) and decay rate deviations
  - Heart-brain coherence index vs. deviation magnitude

---

## 4. Experimental Protocol

### Block Structure
Each session consists of alternating 10-minute blocks:

| Block | Label | Instruction | Duration |
|-------|-------|------------|----------|
| 1 | Baseline | Sit quietly, eyes closed, no instruction | 10 min |
| 2 | Intention | "Try to influence the count rate. Will it higher/lower." | 10 min |
| 3 | Rest | Sit quietly, eyes closed, no instruction | 10 min |
| 4 | Meditation | "Meditate as you normally would. Open awareness." | 10 min |
| 5 | Rest | Sit quietly, eyes closed, no instruction | 10 min |
| 6 | Intention | "Try to influence the count rate." (opposite direction) | 10 min |
| 7 | Rest | Sit quietly, eyes closed, no instruction | 10 min |
| 8 | Meditation | "Meditate. No goal regarding the counts." | 10 min |
| 9 | Rest | Sit quietly, eyes closed, no instruction | 10 min |
| 10 | Baseline | Sit quietly, eyes closed, no instruction | 10 min |

**Total session: 100 minutes (~67,000 events at 400 cpm)**

### Counterbalancing
- Intention direction (increase/decrease) alternates between sessions
- Block order (intention first vs. meditation first) alternates between sessions
- Minimum 20 sessions for statistical power

### Blinding
- Arduino logs raw timestamps with block labels encoded numerically
- Analysis pipeline does not know which number maps to which condition until after all statistical tests are run
- Double-blind: a second person assigns block-condition mappings; experimenter does not know during data collection

### Environmental Controls
- Temperature logged (DS18B20 sensor on Arduino) — Am-241 decay rate is temperature-independent but GM tube sensitivity has slight temperature dependence
- Time of day logged — control for cosmic ray flux diurnal variation
- Sessions at same location, same time of day when possible
- Minimum 30 minutes settling time after hardware setup before first block

---

## 5. Statistical Power Analysis

### Effect Size Estimation
PEAR REG data: ~0.0001 bits/bit effect size over 28 years. This is approximately a 0.01% deviation from expected mean.

For decay counts in a 10-minute block:
- Expected counts: ~4,000 (at 400 cpm)
- Poisson standard deviation: √4000 ≈ 63.2
- PEAR-scale effect: 0.0001 × 4000 = 0.4 counts deviation
- Z-score per block: 0.4/63.2 ≈ 0.006 (undetectable in single block)

**This means:** At PEAR-scale effect sizes, single-block detection is impossible. Detection requires aggregation across MANY blocks.

### Required Sample Size
For a two-tailed test at α = 0.05, power = 0.80, with effect size d = 0.006 per block:
- Required blocks per condition: n = (Z_α/2 + Z_β)²/(d²) ≈ (1.96 + 0.84)²/(0.006²) ≈ 2.18 × 10⁶

**This is infeasible for single-operator PEAR-scale effects.**

### But: DoPI predicts LARGER effects under meditation
If navigational repulsion (R1) is correct, meditation blocks should show MUCH larger deviations than intention blocks — because the bottleneck is wider, reducing self-interference. The question is: how much larger?

If meditation-state effects are 10× PEAR scale (0.001 bits/bit):
- Deviation: 4 counts per block
- Z-score per block: 0.063
- Required blocks: ~21,800 (still large but feasible over months)

If meditation-state effects are 100× PEAR scale (0.01 bits/bit):
- Deviation: 40 counts per block
- Z-score per block: 0.63
- Required blocks: ~22 per condition (achievable in ~10 sessions!)

**The experiment's feasibility depends critically on the effect size under meditation conditions.** DoPI does not predict the magnitude, only the ordering. A pilot study (5 sessions) would estimate the effect size and determine whether the full experiment is practical.

### Alternative Statistical Approach
Instead of testing mean deviation, test for **distributional changes**:
- Kolmogorov-Smirnov test for inter-arrival time distribution differences
- This captures not just mean shifts but also variance changes, correlation structure changes, and distributional shape changes
- More sensitive to the bottleneck-geometry prediction (which affects the STRUCTURE of the distribution, not just the mean)

---

## 6. DoPI-Specific Predictions

### Primary Prediction (from R1 — Navigational Repulsion)
**Meditation blocks show larger deviations from Poisson than intention blocks.**

Mechanism: Intention contracts the bottleneck (fixation on outcome → narrower perspectival geometry → stronger restoring forces → less access to the null space of normal perception → less modulation of decay statistics). Meditation widens the bottleneck (open awareness → wider perspectival geometry → weaker restoring forces → more access → more modulation).

### Secondary Prediction (from Theory of Attention)
**EEG alpha/theta coherence correlates positively with deviation magnitude, independent of block type.**

Mechanism: High coherence = wide bottleneck = large accessible region of configuration space = large potential modulation. This should appear as a continuous predictor, not just a categorical (meditation vs. intention) effect.

### Tertiary Prediction (from Completeness-Dissolution)
**The largest deviations occur when the operator reports ego-dissolution or "losing track of self."**

Mechanism: Completeness-dissolution (NST consequence) = bottleneck approaching identity → maximum access → maximum modulation. But this state is inherently unstable (you can't maintain dissolved individuation for long). Predict: brief spikes of large deviation correlated with reported moments of self-loss.

### Null Prediction (important for falsification)
**If the experiment shows intention > meditation, navigational repulsion (R1) is falsified.** This would not falsify all of DoPI, but it would eliminate the specific mechanism proposed for consciousness-physics coupling through attentional quality. It would suggest that directed intention IS the relevant variable, consistent with standard psi assumptions.

---

## 7. Pilot Study Design

Before the full experiment, a 5-session pilot to:

1. **Verify hardware:** Confirm count rate stability over 100-minute sessions. Check for drift, electronic noise, temperature effects.
2. **Estimate effect size:** Under the DoPI prediction, meditation blocks should show the largest deviations. Even 5 sessions (10 meditation blocks, 10 intention blocks, 15 rest blocks) gives a preliminary estimate.
3. **Optimize block length:** 10 minutes may be too short for deep meditation. Test 10 vs. 15 vs. 20 minute blocks.
4. **Test EEG/HRV data quality:** Confirm that Muse 2 / Polar H10 provide usable real-time data.
5. **Identify confounds:** Any unexpected correlations with temperature, time, or other variables.

**Pilot duration:** 5 sessions × 100 minutes = ~8.3 hours of data collection over 1-2 weeks.
**Pilot data:** ~335,000 decay events. Enough for distributional analysis even if mean-shift effects are undetectable.

---

## 8. Analysis Plan (Pre-Registered)

Before data collection begins, register:

1. Primary hypothesis: meditation blocks show larger KS statistic (deviation from exponential) than intention blocks.
2. Secondary hypothesis: EEG alpha coherence positively correlates with block-level KS statistic.
3. Tertiary hypothesis: HRV coherence index positively correlates with deviation magnitude.
4. Alpha level: 0.05, two-tailed.
5. Multiple comparison correction: Bonferroni for 3 primary tests.
6. Effect size estimation: report Cohen's d and 95% CI regardless of significance.

---

*This experiment is cheap, buildable, and makes a prediction that no other framework makes. The U-shaped curve (meditation > passive > intention) is the signature of navigational repulsion. If it appears, it simultaneously validates R1 AND consciousness-physics coupling. If it doesn't appear, R1 is constrained.*

*Total cost: ~$500. Total pilot time: ~2 weeks. Discriminating power: HIGH (unique prediction).*
