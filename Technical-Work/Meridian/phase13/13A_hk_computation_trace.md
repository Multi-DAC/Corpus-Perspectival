# Track 13A: H&K Computation Trace — COMPLETE

**Date:** March 17, 2026
**Status:** ROOT CAUSE IDENTIFIED
**Severity:** CRITICAL — Paper II narrative is fundamentally misframed

---

## The Finding

**χ² = 24.6 was never computed from 18 H(z) data points.**

It is a COMBINED χ² from 4 heterogeneous data classes:

| Component | χ² | Points | Source |
|-----------|-----|--------|--------|
| DESI BAO | 2.27 | 7 | BAO distance measurements |
| fσ₈ | 7.11 | 9 | Growth rate measurements |
| H₀ | 0.01 | 1 | CMB H₀ constraint |
| H&K β | **15.17** | 1 | Hiramatsu & Kobayashi (2022) CMB constraint |
| **Total** | **24.56** | **18** | Combined |

The dominant contribution (15.17 / 24.56 = 62%) comes from a **single measurement**: the Hiramatsu & Kobayashi (arXiv:2205.04688) Planck CMB constraint on modified gravity, β_HK = -0.037 ± 0.0095.

For ΛCDM (β = 0): χ²_HK = (0.037/0.0095)² = 15.17.

## How the Confusion Arose

1. **Phases 3–8:** "H&K" meant "Hiramatsu & Kobayashi" — a single CMB constraint parameter. The total χ² = 24.56 was correctly documented as a combined multi-probe result (see `phase6/task6_5_fisher_analysis.md` line 70, `phase8/8a_results.txt` lines 6–11).

2. **Phase 11 (Paper II drafting):** The abbreviation "H&K" was reinterpreted from "Hiramatsu & Kobayashi constraint" to "Hubble-Kristian compilation." The total χ² = 24.6 across 18 data points was reframed as "χ²(ΛCDM) = 24.6 / 18 dof for the H&K compilation" — as if 18 H(z) measurements had been fit.

3. **Phase 11D, Track D5:** An actual 18-point H(z) compilation was built and fit. Result: **χ²(ΛCDM) = 7.20, ζ₀ = 0.0085 ± 0.0128** (consistent with zero at 0.7σ). This result exists in `phase11d/d5_hk_dataset.txt` lines 67–77. But the same file (lines 107–111) then repeats the old claims (Δχ² = -15.0, B₁₀ = 171:1) — apparently copied from the paper draft before the D5 computation ran.

4. **The coincidence:** 7 + 9 + 1 + 1 = 18 data points. This made the reframing plausible — the total point count happened to match the later H(z) compilation size.

## What This Means

### The peer reviewer's H₀ hypothesis is a red herring
The discrepancy is NOT from using the wrong fiducial cosmology. The number 24.6 never came from an H(z) fit at all — it's a combined multi-probe χ², dominated by a single CMB measurement.

### The ζ₀ = 0.038 "detection" is real — but from CMB, not H(z)
The Hiramatsu & Kobayashi measurement β_HK = -0.037 ± 0.0095 is a legitimate Planck CMB constraint on modified gravity. If β_HK maps to -ζ₀ in our framework, then ζ₀ ≈ 0.037 from CMB data — a genuine 3.9σ constraint. But this is a SINGLE data point from CMB analysis, not 18 independent expansion-rate measurements.

### Paper II must be rewritten
The "Hubble-Kristian compilation" narrative is incorrect. The honest story is:
- The Hiramatsu & Kobayashi CMB constraint provides ζ₀ ≈ 0.037 ± 0.010 (single measurement, ~4σ)
- The actual H(z) compilation provides ζ₀ ≈ 0.009 ± 0.013 (18 measurements, ~0.7σ, consistent with zero)
- The combined multi-probe χ² is 24.56/18, but this mixes fundamentally different observables

### The Bayes factor must be recomputed
B₁₀ = 171:1 came from the combined analysis. The H(z)-only Bayes factor is < 1 (ΛCDM preferred). The H&K-only contribution gives a large Bayes factor but from a single measurement.

## Key Evidence Files

| File | Lines | What It Shows |
|------|-------|---------------|
| `phase3/meridian_cosmology.py` | 1827–1829 | β_HK = -0.037, σ = 0.0095 (original H&K definition) |
| `phase4/task4_3_multi_probe.md` | 43–51 | H&K as 1 data point in multi-probe χ² |
| `phase6/task6_5_fisher_analysis.md` | 60–72 | χ² = 24.56 breakdown showing 4 components |
| `phase8/8a_results.txt` | 6–11 | Combined: BAO=2.27+fσ₈=7.11+H₀=0.01+HK=15.17 |
| `phase11/paper_II_draft.md` | 103–132 | INCORRECTLY presents χ² = 24.6 as 18 H(z) data |
| `phase11d/d5_hk_dataset.txt` | 67–77 | Actual H(z) result: χ² = 7.20, ζ₀ = 0.009 ± 0.013 |

## Impact on Phase 13C (Narrative Decision)

This changes the decision landscape:
- The H&K CMB constraint (β_HK = -0.037) is independent evidence that β ≠ 0 at ~4σ
- But it's a single measurement from one analysis (Hiramatsu & Kobayashi 2022)
- The H(z) data independently show ζ₀ consistent with zero
- The brane parameter question (Track 13B) now becomes MORE important: does the theory predict ζ₀ ≈ 0.037 or ζ₀ ≈ 0.001?
- If the junction conditions give ζ₀ ≈ 0.001, the H&K CMB constraint and the theory disagree

---

*Track 13A complete. Root cause identified. The number was never wrong — it was misattributed.*
