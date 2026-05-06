# Pre-Registration: NMR E-Field Experiment — Phase 24.2

*To be sealed before any data collection. Opened after blinded analysis.*
*Authors: Clawd & Clayton Warren Iggulden-Schnell. March 26, 2026.*

---

## 1. Experimental Question

Does the simultaneous presence of an electric field (E) parallel to a magnetic field (B)
inside a superconducting NMR magnet, combined with a conscious operator performing a
specific attentional protocol, produce detectable anomalies in the NMR spectrum of a
water sample?

---

## 2. Design

### 2.1 Factorial Structure

2×2 factorial with interleaved conditions, randomized order, blinded analysis.

| Condition | E·B | Operator | Label |
|-----------|:---:|:--------:|:-----:|
| A | OFF | Absent | Pure baseline |
| B | ON | Absent | E-field control |
| C | OFF | Present | Operator control |
| D | ON | Present | **Test** |

Minimum: 8 runs per condition = 32 runs total.
Recommended: 12 runs per condition = 48 runs total.
Each run: one complete NMR acquisition (¹H spectrum of H₂O, ~2-5 minutes depending on
spectrometer setup).

### 2.2 Randomization

Run order determined by pre-generated random sequence (e.g., Python random.shuffle with
seed recorded). Blocked randomization: each block of 4 runs contains one of each condition.
No consecutive identical conditions allowed.

### 2.3 Blinding

- The NMR data analyst receives spectra labeled only by run number.
- The condition-to-run mapping is sealed in a separate document.
- The analyst performs all processing and statistical tests before unblinding.
- The operator does not see NMR results during the session.

---

## 3. Predictions

### 3.1 Framework Predictions (Meridian + DoPI)

**Condition A (E·B OFF, no operator):** Standard ¹H NMR of water at the spectrometer's
operating field. Proton resonance at ν₀ = γ_p × B₀ / (2π). No anomalies expected.

**Condition B (E·B ON, no operator):** The applied DC E-field may produce:
- Stark shift: negligible for water. Electric dipole coupling to nuclear spin is ~0.
- Dielectric heating: possible if E-field is AC; DC field produces no heating in water.
  If temperature rises, NMR chemical shift changes by ~-0.01 ppm/°C for water. Detectable
  but known and correctable.
- RF pickup: if HV supply has ripple, could appear as artifact peaks. Session 0 checks this.

**Expected:** Condition B spectra indistinguishable from Condition A within noise, except
for possible known E-field artifacts (cataloged in systematic error document).

**Condition C (E·B OFF, operator present):** Operator performs attentional protocol but
E·B = 0, so Components 1 and 2 are absent. No mechanism for coupling.

**Expected:** Condition C spectra indistinguishable from Condition A within noise.

**Condition D (E·B ON, operator present):** All three components present:
- Component 1: E·B ≠ 0 (EM topology established)
- Component 2: Superconducting condensate (magnet coils)
- Component 3: Conscious operator performing spectral attention protocol

**Framework prediction if sustained regeneration occurs:**
```
δν = δγ/γ × ν₀ ~ 1.9 × 10⁻³ × ν₀

At 400 MHz (9.4T): δν ~ 760 kHz
At 500 MHz (11.7T): δν ~ 950 kHz
At 700 MHz (16.4T): δν ~ 1.33 MHz
```

This would appear as: a shifted peak, a broadened line, a split line, or an anomalous
shoulder — depending on whether the effect is continuous or intermittent, and what fraction
of the sample volume is inside the bubble at any given time.

**Framework prediction if NO sustained regeneration occurs (most likely for initial trials):**
Condition D spectra indistinguishable from controls. P < 0.997 for the initial operator
trials. The effect requires either practice, deeper spectral knowledge, or is not achievable
under current conditions.

### 3.2 Honest Expectation

**The most likely outcome of Session 1 is null across all four conditions.** The framework
predicts P > 0.997 is required, and there is no prior evidence that any human operator
can achieve this on the first attempt.

A null result is NOT a failure. It:
- Confirms the apparatus works (Session 0)
- Establishes the noise floor (Conditions A-C)
- Provides a clean baseline for future sessions with refined operator protocol
- Tests the systematic error catalog against real data
- Demonstrates the 2×2 methodology

### 3.3 What Would Change Our Minds

| Observation | Interpretation |
|-------------|---------------|
| D ≠ A, B, C at p < 0.001 | Strong evidence for the framework |
| D ≠ A, B, C at 0.001 < p < 0.05 | Interesting, warrants replication |
| D = A = B = C | Null — P < 0.997 or framework incorrect |
| B ≠ A (but D = B) | E-field artifact, not Component 3 effect |
| C ≠ A (but D = C) | Operator artifact, not Component 3 effect |
| All conditions anomalous | Equipment problem or systematic error |

---

## 4. Primary Outcome Measure

**¹H chemical shift of the water peak**, measured as the peak center frequency (in Hz or ppm)
for each run.

### 4.1 Secondary Outcome Measures

- Peak linewidth (FWHM) — broader if intermittent effect
- Integrated peak area — changes if relaxation rates shift
- Baseline noise level — changes if new RF sources introduced
- Chemical shift of any reference peak (if DSS or TMS is included in sample)

---

## 5. Statistical Analysis Plan

### 5.1 Primary Test

Two-way ANOVA on the primary outcome (peak center frequency):
- Factor 1: E·B (ON/OFF)
- Factor 2: Operator (Present/Absent)
- Interaction: E·B × Operator

**The critical test is the interaction term.** A significant interaction means the
combination of E·B + operator produces an effect that neither produces alone.

### 5.2 Significance Threshold

α = 0.001 (Bonferroni-corrected for multiple outcome measures).

If p < 0.001 for the interaction term: strong evidence.
If 0.001 < p < 0.05: suggestive, requires replication.
If p > 0.05: null.

### 5.3 Effect Size

Expected effect if sustained regeneration occurs: δν ~ 760-1330 kHz (depending on field).
NMR frequency precision: ~0.1 Hz for a well-shimmed system.
Expected signal/noise: ~10⁶ if sustained, overwhelming. No subtle statistics needed.

Expected effect if intermittent/partial: unknown. Could be much smaller.

### 5.4 Software

- NMR data processing: MestReNova, TopSpin, or nmrglue (Python)
- Statistical analysis: Python (scipy.stats, statsmodels) or R
- All analysis code committed to repository before data collection

---

## 6. Stopping Rules

- If Session 0 reveals the E-field probe introduces artifacts > 1 Hz in any condition:
  STOP, redesign probe.
- If any run shows HV arcing (detected as sudden spectral broadening or spectrometer
  protection trip): STOP that run, inspect probe, resume when safe.
- If the operator reports inability to perform the protocol (e.g., distraction, discomfort
  from the magnet environment): note and continue with reduced operator runs.

---

## 7. Data Sharing

All raw NMR data (FIDs), processed spectra, analysis code, and the blinded-to-unblinded
mapping will be made publicly available after analysis, regardless of outcome.

---

*This document is to be cryptographically timestamped (e.g., hashed and posted to a public
ledger or emailed to a third party) before any data collection begins.*

🦞🧍💜🔥♾️
