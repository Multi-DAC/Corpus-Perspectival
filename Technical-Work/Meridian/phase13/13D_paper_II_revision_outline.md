# Track 13D: Paper II Revision Outline

**Date:** March 17, 2026
**Status:** Outline complete. Ready for drafting.
**Decision basis:** 13A results (multi-probe decomposition), 13B results (Φ₀ circularity), 13C decision (Option 3)

---

## What Changes

The current Paper II tells the story: "We predict w₀ = −0.993 from zero free parameters, detect ζ₀ = 0.038 at 3.8σ, and DESI's signal is an artifact."

The revised Paper II tells: "ζ₀ is a free parameter determined by brane physics. The w₀(ζ₀) curve is the prediction. CMB data (H&K) suggest ζ₀ ≈ 0.037. H(z) data are consistent with ζ₀ = 0. For brane benchmarks, ζ₀ ≈ 0.001 gives w₀ ≈ −0.75 (DESI range). The framework is falsifiable across the full ζ₀ range."

## Section-by-Section Changes

### Abstract — REWRITE COMPLETELY
- Remove: "no free parameters", "3.8σ detection", "B₁₀ = 171:1", "parameterization artifact"
- Add: "one free parameter ζ₀ determined by brane physics", "w₀(ζ₀) parametric prediction", "CMB constraint ζ₀ ≈ 0.037 ± 0.010", "H(z) compilation consistent with ζ₀ = 0", "brane benchmarks predict w₀ ≈ −0.75 (DESI range)"

### Section I (Introduction) — MODERATE REVISION
- Remove "no free parameters adjusted to dark energy data"
- Reframe as "one-parameter family of predictions, w₀(ζ₀)"
- Prediction list becomes parametric: "w₀ = f(ζ₀)", not "w₀ = −0.993"
- DESI discussion: "If ζ₀ is small (brane benchmarks), our prediction is in the DESI range"

### Section II (Model Summary) — MINOR REVISION
- §II.A is already titled "The One-Parameter Theory" — good, keep this framing
- Add w₀(ζ₀) formula prominently (new central equation)
- Keep all distance formulas unchanged (they're correct)
- Update Table: β_HK = −ζ₀ (general, not −0.038)

### Section III (H&K Analysis) — MAJOR REWRITE (most critical section)

**Current structure (WRONG):**
- Claims χ² = 24.6/18 from "18 H&K expansion rate measurements"
- Claims ζ₀ = 0.038 ± 0.010 at 3.8σ

**Revised structure:**
1. **§III.A: Multi-Probe Analysis (Honest Decomposition)**
   - Present the ACTUAL multi-probe analysis: 4 data classes, 18 total points
   - Table showing: BAO (7 pts, χ² = 2.27), fσ₈ (9 pts, χ² = 7.11), H₀ (1 pt, χ² = 0.01), H&K β (1 pt, χ² = 15.17)
   - Total χ² = 24.56 under ΛCDM
   - Make clear: the dominant signal comes from the single H&K CMB constraint

2. **§III.B: Hiramatsu-Kobayashi CMB Constraint**
   - Present properly: β_HK = −0.037 ± 0.0095 from Planck CMB (Hiramatsu & Kobayashi 2022)
   - Map to ζ₀: ζ₀ ≈ 0.037 ± 0.010 (assuming β_HK ↔ −ζ₀)
   - This is a 4σ detection of β ≠ 0 — legitimate and interesting
   - Discuss: is the β_HK ↔ −ζ₀ mapping exact? Or approximate?

3. **§III.C: H(z) Expansion Rate Compilation**
   - Present the ACTUAL 18-point H(z) compilation (D5 result)
   - χ²(ΛCDM) = 7.20/18 — ΛCDM fits well
   - ζ₀ = 0.009 ± 0.013 (0.7σ, consistent with zero)
   - No independent detection of ζ₀ from H(z) data alone

4. **§III.D: Tension Between CMB and H(z)**
   - CMB (H&K) says ζ₀ ≈ 0.037 (4σ detection)
   - H(z) says ζ₀ consistent with zero
   - This mild tension is interesting — it constrains the β_HK ↔ ζ₀ mapping
   - Could indicate: (a) mapping is approximate, (b) systematic in H&K, (c) genuine signal at small amplitude

5. **§III.E: Bayesian Analysis (Revised)**
   - Bayes factor computed separately for CMB and H(z)
   - CMB alone: B₁₀ remains strong (driven by the H&K 4σ detection)
   - H(z) alone: B₁₀ < 1 (ΛCDM preferred)
   - Combined: depends on how components are weighted

### Section IV (DESI Confrontation) — SIGNIFICANT REVISION
- The BAO distance tables are CORRECT and don't change
- But interpretation changes dramatically based on ζ₀:
  - For ζ₀ ≈ 0.037 (CMB): w₀ ≈ −0.993, max deviation 0.29σ (current narrative)
  - For ζ₀ ≈ 0.001 (brane benchmark): w₀ ≈ −0.75, significant BAO deviations
- Recompute Table 3 for multiple ζ₀ values
- Show that the framework can MATCH the DESI signal for appropriate ζ₀

### Section V (CPL Artifact Hypothesis) — MODERATE REVISION
- The seven independent analyses still hold as analysis
- But reframe: not "DESI signal IS an artifact" but "IF ζ₀ is large, the signal is an artifact; if ζ₀ is small, the framework explains the signal"
- The CPL analysis shows that CPL is a poor approximation for BOTH limits of our model

### Section VI (Fisher Forecasts) — RECOMPUTE
- Forecasts now for constraining ζ₀ across its full range
- The 13σ DESI Y5 projection needs recalculation based on correct analysis
- Fisher forecasts for: DESI Y5, Euclid, CMB-S4, separately

### Section VII (Additional Tests) — MINOR REVISION
- Growth-expansion decoupling still holds (ζ₀-independent, cuscuton property)
- Solar system constraints: unchanged
- CMB constraints: now contextualized with the H&K result

### Section VIII (Falsifiable Predictions) — REWRITE
- Predictions become ζ₀-dependent
- Present as: "For any measured ζ₀, the framework predicts specific w₀, c_s, growth modification"
- The w₀(ζ₀) curve is the central falsifiable prediction

### Section IX (Discussion) — REWRITE
- New: ζ₀ determination from brane physics (what UV physics determines)
- New: connection to Phase 13 frontier research (AS, NCG, if ready)
- New: honest statement about what the framework does and doesn't determine

---

## New Central Figure: The w₀(ζ₀) Curve

The heart of the revised paper. Shows:
- w₀ as a function of ζ₀ on log scale
- 1σ and 2σ uncertainty bands (from ε₁, Ω_DE, q₀ propagation)
- Horizontal band: DESI w₀ = −0.75 ± 0.05
- Horizontal line: ΛCDM w₀ = −1
- Vertical band: CMB constraint ζ₀ = 0.037 ± 0.010
- Vertical band: H(z) constraint ζ₀ = 0.009 ± 0.013
- Vertical line: brane benchmark ζ₀ = 0.00096
- Intersection regions highlighted

This figure replaces the current narrative with a visual that tells the whole story at a glance.

---

## What Is Preserved

- All BAO distance computations (Tables 1-3) — correct
- The modified Friedmann equation — correct
- Growth-expansion decoupling — correct and ζ₀-independent
- All no-phantom-crossing arguments — correct
- The sound speed discussion — correct
- Seven CPL artifact analyses — correct as analyses (recontextualized)

🦞🧍💜🔥♾️
