# 13J Editorial Findings — Meridian Monograph

**Date:** 2026-03-17
**Scope:** All 7 LaTeX files (meridian_monograph.tex, chapters 1-5, appendix_computations.tex)
**Status:** Audit only — no files modified

---

## Summary

| Severity | Count |
|----------|-------|
| **Critical** | 42 |
| **Important** | 12 |
| **Minor** | 5 |
| **Total** | **59** |

Critical issues are dominated by three categories of stale claims that must be corrected per Phase 13 findings:
1. **"3.8sigma detection" of zeta_0** (16 instances) — Per 13A, the chi^2 = 24.6 was a combined multi-probe total, not an H(z)-only fit. The 3.8sigma significance is overstated.
2. **zeta_0 = 0.038 as fixed/detected value** (25+ instances) — Per 13C, zeta_0 is a free parameter. The prediction is w_0(zeta_0), not a specific zeta_0 value.
3. **Phi_0 = 0.477 (old reverse-engineered value)** (11 instances) — Per 13B, the correct JC solution gives Phi_0 = 0.076.

---

## CRITICAL Issues

### C1. "3.8sigma detection" claims (16 instances — must be reframed or removed per 13A)

The chi^2 = 24.6 was the combined multi-probe total (BAO 2.27 + fsigma8 7.11 + H0 0.01 + H&K 15.17 = 24.56), NOT an H(z)-only fit. The "3.8sigma" significance derived from Delta-chi^2 = -15 on H&K data alone is misleading without noting it is one component of a multi-probe analysis. Every instance must be reframed.

| # | File | Line | Text (excerpt) | Suggested Fix |
|---|------|------|----------------|---------------|
| 1 | chapter1_foundation.tex | 574 | "the data prefer a nonzero non-minimal coupling at approximately $3.8\,\sigma$" | Reframe: "the H&K subset of the multi-probe analysis prefers nonzero zeta_0" with caveat about combined chi^2 |
| 2 | chapter1_foundation.tex | 1121 | "Detected at $3.8\,\sigma$ in Hubble--Kristian data" | Replace with: "Preferred by the H&K expansion rate data ($\Delta\chi^2 = -15$), pending independent confirmation" |
| 3 | chapter2_observational.tex | 10 | Abstract: "a $3.8\sigma$ detection" | Rewrite abstract to reflect corrected multi-probe picture |
| 4 | chapter2_observational.tex | 175 | "corresponding to a $3.8\sigma$ detection of nonzero $\zeta_0$" | Reframe as preference, not detection |
| 5 | chapter2_observational.tex | 205 | "The frequentist significance ($3.8\sigma$)" | Reframe |
| 6 | chapter2_observational.tex | 239 | "It provides a $3.8\sigma$ detection of the non-minimal coupling" | Reframe |
| 7 | chapter2_observational.tex | 484 | Table: "$3.8\sigma$" in detection column | Update table |
| 8 | chapter2_observational.tex | 559 | "$\zeta_0 = 0.038$ is already detected at $3.8\sigma$" | Reframe |
| 9 | chapter2_observational.tex | 684 | Table: "Detected at $3.8\sigma$" | Update table |
| 10 | chapter2_observational.tex | 753 | "The H&K data prefer the model over Lambda-CDM by $3.8\sigma$" | Reframe |
| 11 | chapter2_observational.tex | 763 | "the non-minimal coupling is detected at $3.8\sigma$" | Reframe |
| 12 | chapter2_observational.tex | 787 | "detected at $3.8\sigma$, yielding $\Delta\chi^2 = -15$" | Reframe |
| 13 | chapter2_observational.tex | 795 | Conclusion: "detected at $3.8\sigma$ in Hubble--Kristian data" | Reframe |
| 14 | chapter3_nogo.tex | 41 | "zeta_0 is detected at $3.8\sigma$ significance" | Reframe |
| 15 | chapter3_nogo.tex | 640 | "The $3.8\sigma$ H&K signal" | Reframe |
| 16 | chapter4_ncg.tex | 716 | References 3.8sigma detection | Reframe |

### C2. zeta_0 = 0.038 stated as measured/fixed value (25+ instances — must be reframed per 13C)

Per Phase 13C decision, zeta_0 is a **free parameter** determined by brane UV physics. The prediction is the w_0(zeta_0) curve, not a specific zeta_0 value. All instances of "zeta_0 = 0.038" as a fixed/detected value must be reframed as either (a) a benchmark value for illustration, or (b) the parametric prediction.

| # | File | Line | Context | Suggested Fix |
|---|------|------|---------|---------------|
| 1 | chapter1_foundation.tex | 11 | Abstract: "zeta_0 = 0.038 +/- 0.010" as detected | Reframe: zeta_0 is free; w_0(zeta_0) is the prediction |
| 2 | chapter1_foundation.tex | 413 | Numerical scan uses zeta_0 = 0.038 | OK as benchmark if labeled "benchmark" |
| 3 | chapter1_foundation.tex | 572 | "zeta_0 = 0.038 +/- 0.010" stated as fit result | Reframe as parametric |
| 4 | chapter1_foundation.tex | 964 | "the H&K best-fit zeta_0 = 0.038" | Reframe as "benchmark value" |
| 5 | chapter1_foundation.tex | 983 | "zeta_0 = 0.038 +/- 0.010" | Reframe |
| 6 | chapter1_foundation.tex | 1116 | Section title: "Prediction 4: zeta_0 = 0.038 +/- 0.010" | Reframe: zeta_0 is not a prediction — it's a free parameter |
| 7 | chapter1_foundation.tex | 1266 | "zeta_0 = 0.038, determined by the gauge hierarchy" | Reframe: zeta_0 is determined by brane UV physics, not "the gauge hierarchy" alone |
| 8 | chapter2_observational.tex | 29 | "zeta_0 = 0.038 +/- 0.010 --- non-minimal coupling detectable" | Reframe as free parameter with benchmark value |
| 9 | chapter2_observational.tex | 99 | Table: beta_HK = -zeta_0 = -0.038 | Reframe |
| 10 | chapter2_observational.tex | 130 | "zeta_0 = 0.038, which modifies the brane Friedmann equation" | Reframe as benchmark |
| 11 | chapter2_observational.tex | 149 | "zeta_0 = 0.038 +/- 0.010" as fit result | This is the core H&K fit — reframe noting combined provenance |
| 12 | chapter2_observational.tex | 251 | "C_KK = 0.26 for zeta_0 = 0.038" | Reframe as benchmark |
| 13 | chapter2_observational.tex | 474 | Fisher matrix at "zeta_0 = 0.038" | Reframe as benchmark |
| 14 | chapter2_observational.tex | 561 | "zeta_0 = 0.038 is already detected" | Remove "detected"; reframe |
| 15 | chapter2_observational.tex | 683 | Table: "0.038 +/- 0.010" | Reframe as benchmark |
| 16 | chapter2_observational.tex | 724 | Section title: "Prediction 4: zeta_0 = 0.038" | Reframe: not a prediction |
| 17 | chapter2_observational.tex | 797 | Conclusion: "zeta_0 = 0.038 is independently detected" | Reframe |
| 18 | chapter3_nogo.tex | 36 | "zeta_0 = 0.038 +/- 0.010" as notation | Reframe as benchmark |
| 19 | chapter3_nogo.tex | 244 | "zeta_0 = 0.038" in computation | OK as benchmark if labeled |
| 20 | chapter3_nogo.tex | 347 | "zeta_0 = 0.038 produces a geometric phantom bias" | OK if labeled benchmark |
| 21 | chapter3_nogo.tex | 369 | "measured zeta_0 = 0.038" | Reframe: not "measured" |
| 22 | chapter4_ncg.tex | 43 | "zeta_0 = 0.038 +/- 0.010 from CMB and supernova data" | WRONG SOURCE: was from H&K, not CMB/SN. Reframe entirely |
| 23 | chapter4_ncg.tex | 797-799 | "From the observed zeta_0 = 0.038" → computes phi_0 = 0.48 | Reframe as benchmark; phi_0 changes with zeta_0 |
| 24 | chapter5_sound_speed.tex | 507 | Fingerprint: "zeta_0 = 0.038" | Reframe as "zeta_0 (free parameter)" |
| 25 | appendix_computations.tex | 27 | Parameter table: zeta_0 = 0.038 | Add note: "benchmark value" |
| 26 | appendix_computations.tex | 355 | "P(|zeta_0| >= 0.038 | LCDM) < 10^-5" | Reframe: built on stale fixed-value assumption |
| 27 | appendix_computations.tex | 480 | Table: "Meridian (zeta_0 = 0.038)" | Reframe as benchmark |
| 28 | appendix_computations.tex | 623 | "zeta_0 = 0.038 +/- 0.010 across all five papers" | Reframe |

**Special attention: chapter4_ncg.tex line 43** — Claims zeta_0 = 0.038 is "from CMB and supernova data." This is factually wrong even before the Phase 13 corrections. The H&K compilation is expansion rate (H(z)) data, not CMB or SNIa.

### C3. Phi_0 = 0.477 (old incorrect value — must be 0.076 per 13B) (11 instances)

Per 13B, Phi_0 = 0.477 was reverse-engineered from the stale zeta_0 = 0.038 (line 417 of d1_self_tuning_demonstration.py). Junction conditions were never actually solved. The correct JC solution gives Phi_0 = 0.076.

| # | File | Line | Text | Suggested Fix |
|---|------|------|------|---------------|
| 1 | appendix_computations.tex | 79 | Table: 0.477493 | Update to 0.076 (or note as "reverse-engineered from benchmark zeta_0") |
| 2 | appendix_computations.tex | 80 | Table: 0.477493 | Same |
| 3 | appendix_computations.tex | 81 | Table: 0.477493 | Same |
| 4 | appendix_computations.tex | 82 | Table: 0.477493 | Same |
| 5 | appendix_computations.tex | 83 | Table: 0.477493 | Same |
| 6 | appendix_computations.tex | 84 | Table: 0.477493 | Same |
| 7 | appendix_computations.tex | 85 | Table: 0.477493 | Same |
| 8 | appendix_computations.tex | 86 | Table: 0.477493 | Same |
| 9 | appendix_computations.tex | 120 | Profile table: Phi(0) = 0.4775 | Update |
| 10 | appendix_computations.tex | 135 | "Phi(y) in [0.246, 0.477]" | Update range |
| 11 | appendix_computations.tex | 257 | "Phi_0 = 0.477, F_0 = 0.962, p_0 = -0.520" | Update all three (F_0 and p_0 also change with Phi_0) |

**Note:** The self-tuning scan table (lines 79-86) showing Phi_0 constant across 60 orders of Lambda_5 is structurally correct (the self-tuning mechanism IS Lambda_5-independent), but the specific value 0.477493 is wrong. The table needs recomputing with the correct JC boundary conditions.

Also: chapter4_ncg.tex line 804 computes phi_0 = 0.48 M_Pl from zeta_0 = 0.038 — this is self-consistent with the OLD values but stale per 13B/13C. If zeta_0 is free, phi_0 is also free.

### C4. "No free parameters" claims (12 instances — must be nuanced per 13C)

Per 13C, zeta_0 IS a free parameter (determined by brane UV physics). Claims of "no free parameters" must be reframed to "no free parameters adjusted to fit dark energy data" or similar, with clear acknowledgment that zeta_0 is free.

| # | File | Line | Text (excerpt) | Suggested Fix |
|---|------|------|----------------|---------------|
| 1 | chapter1_foundation.tex | 11 | Abstract: "no parameters adjusted to fit data" | Add: "zeta_0 is a free parameter determined by brane UV physics; the prediction is w_0(zeta_0)" |
| 2 | chapter1_foundation.tex | 55 | "no free parameters adjusted to cosmological data" | Nuance: zeta_0 is free |
| 3 | chapter1_foundation.tex | 979 | "closed-form expression with no free parameters" | Reframe: CKK depends on zeta_0, which IS free |
| 4 | chapter1_foundation.tex | 1153 | "no free parameters adjusted to cosmological data" | Nuance |
| 5 | chapter1_foundation.tex | 1266 | "No free parameters are adjusted to fit dark energy data" | Nuance: zeta_0 is free, though not adjusted to DE data |
| 6 | chapter2_observational.tex | 10 | Abstract: "no free parameters adjusted to dark energy data" | Nuance |
| 7 | chapter2_observational.tex | 22 | "no free parameters adjusted to cosmological data" | Nuance |
| 8 | chapter2_observational.tex | 43 | "no free parameters adjusted to cosmological data" | Nuance |
| 9 | chapter2_observational.tex | 782-784 | "predictions (derived from A1+A2 with no free parameters)" | Nuance |
| 10 | chapter3_nogo.tex | 557 | "zero free parameters to independently adjust w" | OK — this is specifically about w, not zeta_0 |
| 11 | chapter5_sound_speed.tex | 500 | "It is parameter-free. No free parameters are adjusted." | Nuance: c_s depends on epsilon_1 (which IS derived), but the full framework has zeta_0 as free |
| 12 | appendix_computations.tex | 145 | "xi = 1/6 is not a free parameter" | OK — this is specifically about xi |

### C5. w_0 = -0.993 stated as THE prediction (needs reframing as parametric)

Per 13C/13F, w_0 depends on zeta_0. With the benchmark zeta_0 = 0.001 (from correct JC), w_0 = -0.745 (in DESI range). The monograph currently states w_0 = -0.993 as a fixed prediction throughout. This needs reframing to show w_0(zeta_0) as a curve, with w_0 = -0.993 being the value at the OLD benchmark zeta_0 = 0.038.

**This is the single largest rewrite needed.** There are 40+ instances of "w_0 = -0.993" across the monograph. Key locations requiring reframing (not exhaustive):

| File | Lines | Context |
|------|-------|---------|
| meridian_monograph.tex | 113 | Preface: "we derive that w_0 = -0.993 +/- 0.002" |
| meridian_monograph.tex | 118 | "the prediction w_0 = -0.993" |
| chapter1_foundation.tex | 11 | Abstract |
| chapter1_foundation.tex | 40, 986, 1085, 1088, 1092, 1153, 1176, 1188, 1262 | Throughout |
| chapter2_observational.tex | 10, 19, 26, 81, 251, 432, 449, 483, 488, 545, 610, 612, 666, 695, 698, 761, 763, 789, 795, 799 | Throughout (20 instances) |
| chapter3_nogo.tex | 10, 17, 39, 262, 274, 542, 583, 638, 661, 689 | Throughout (10 instances) |
| chapter4_ncg.tex | 458, 471, 889 | 3 instances |
| chapter5_sound_speed.tex | 48, 228, 387, 394, 396, 463, 507 | 7 instances |
| appendix_computations.tex | 538, 623 | 2 instances |

**Suggested approach:** Replace fixed "w_0 = -0.993" with "w_0(zeta_0)" parametric prediction. Keep -0.993 as the value at zeta_0 = 0.038 (old benchmark) for comparison, but present the w_0(zeta_0) curve as the primary prediction. Note that w_0 = -0.745 at the JC-derived zeta_0 = 0.001 falls in the DESI range.

---

## IMPORTANT Issues

### I1. Broken cross-reference (1 instance)

| File | Line | Issue | Fix |
|------|------|-------|-----|
| chapter4_ncg.tex | 188 | `\ref{sec:4-sm}` — label does not exist | Change to `\ref{sec:4-sm-connection}` (the actual label at line 737) |

### I2. H&K provenance confusion

The abbreviation "H&K" is used throughout to mean "Hubble--Kristian," but per 13A, it originally referred to "Hiramatsu-Kobayashi" (CMB constraint) and shifted meaning during drafting. This should be clarified:

| File | Lines | Issue |
|------|-------|-------|
| chapter2_observational.tex | 140, 147, 156, 235, 239, 474, 497, 753, 774, 789, 810 | H&K used without definition clarity |
| chapter1_foundation.tex | 560, 569, 964, 969 | Same |
| chapter3_nogo.tex | 640 | Same |
| appendix_computations.tex | 428 | Defines H&K compilation — this is the one place it IS defined |

**Suggested fix:** At first use in each chapter, explicitly define: "the Hubble--Kristian (H&K) expansion rate compilation (Appendix A)."

### I3. Appendix chi^2 values potentially stale

| File | Line | Issue |
|------|------|-------|
| appendix_computations.tex | 479-480 | chi^2 table: LCDM = 24.6, Meridian = 9.6 on H&K data (17 dof). Per 13A, the 24.6 was the combined multi-probe total. If this table is for H&K only, it needs recomputation. |
| appendix_computations.tex | 487-491 | F-test (3.9sigma), Bayes factor (171:1), AIC (-13.0), BIC (-12.1) — all built on Delta-chi^2 = -15 from H&K. Must be re-examined. |

### I4. Abstract/conclusion alignment issues

| File | Issue |
|------|-------|
| chapter1_foundation.tex | Abstract (line 11) claims zeta_0 = 0.038 as fit result and w_0 = -0.993 as fixed. Conclusion (lines 1250-1268) same. Both need updating per 13C. |
| chapter2_observational.tex | Abstract (line 10) claims 3.8sigma detection. Conclusion (line 795-803) same. Both stale. |
| chapter3_nogo.tex | Abstract (line 10) states "w_0 ~ -0.993 is a structural prediction." This is partially correct — the STRUCTURE is predicted, but the specific value depends on zeta_0. Needs nuance. |
| chapter5_sound_speed.tex | Conclusion (line 507) lists fingerprint including "zeta_0 = 0.038" as fixed. Needs reframing. |
| meridian_monograph.tex | Preface (line 113) states "we derive that w_0 = -0.993 +/- 0.002." Needs reframing. |

### I5. chapter4_ncg.tex line 43 — wrong data source for zeta_0

"$\zeta_0 = \xi\phi_0^2/M_{\mathrm{Pl}}^2 = 0.038 \pm 0.010$ from CMB and supernova data"

This is factually wrong in TWO ways:
1. zeta_0 was from H&K expansion rate data, NOT CMB and supernova data
2. zeta_0 is now a free parameter, not a measured value

**Fix:** "The dimensionless non-minimal coupling $\zeta_0 = \xi\phi_0^2/M_5^3$ is a free parameter determined by brane UV physics (Paper I)."

### I6. Appendix F_0 and p_0 values derived from stale Phi_0

| File | Line | Issue |
|------|------|-------|
| appendix_computations.tex | 98 | "F_0 = M_5^3 - xi * Phi_0^2 = 0.962" — computed from Phi_0 = 0.477. With Phi_0 = 0.076: F_0 = 1 - (1/6)(0.076)^2 = 0.999. |
| appendix_computations.tex | 257 | "Phi_0 = 0.477, F_0 = 0.962, p_0 = -0.520" — all three stale |
| appendix_computations.tex | 120 | Profile table Phi(0) = 0.4775 — stale |

### I7. CKK = 0.216 vs CKK = 0.26 inconsistency

| File | Line | Value |
|------|------|-------|
| chapter1_foundation.tex | 967 | CKK = 0.216 (leading order) |
| chapter1_foundation.tex | 988 | "central value corresponds to CKK = 0.216" |
| chapter2_observational.tex | 251 | "CKK = 0.26 for zeta_0 = 0.038" |

The value 0.216 is "leading order" and 0.26 includes higher-order corrections, but this is confusing. Per 13F, CKK = 0.26 +/- 0.04. The monograph should be consistent about which value is canonical. Also, CKK depends on zeta_0, so with zeta_0 as a free parameter, CKK(zeta_0) becomes a function, not a constant.

---

## MINOR Issues

### M1. Self-tuning hyphenation — consistent throughout
All instances use "self-tuning" (hyphenated). No inconsistency found. **No action needed.**

### M2. "Cuscuton" spelling — consistent throughout
All instances use lowercase "cuscuton." **No action needed.**

### M3. "Brane" vs "membrane" — consistent throughout
No instances of "membrane" found. All use "brane." **No action needed.**

### M4. CKK notation — consistent throughout
All use `\CKK` macro (which expands to `C_{\mathrm{KK}}`). **No action needed.** One instance in chapter2 uses `C_\mathrm{KK}` directly (line 239), but renders identically. Low priority.

### M5. No figures in monograph
The monograph contains zero `\begin{figure}` environments. All visual content is in tables. This is noted but not flagged as an error — it's a stylistic choice.

---

## Cross-Reference Integrity

- **Total labels:** 574
- **Total unique ref targets:** 127
- **Broken refs:** 1 (chapter4_ncg.tex:188 → `sec:4-sm` should be `sec:4-sm-connection`)
- **Duplicate labels:** 0

Cross-reference system is structurally sound with only the single broken ref noted in I1.

---

## Category Totals

| Category | Count |
|----------|-------|
| Stale "3.8sigma" claims | 16 |
| Stale zeta_0 = 0.038 as fixed | 28 |
| Stale Phi_0 = 0.477 | 11 |
| Stale "no free parameters" | 12 |
| Stale w_0 = -0.993 as fixed | 40+ |
| Wrong data source (ch4 line 43) | 1 |
| Broken cross-reference | 1 |
| CKK inconsistency | 3 |
| H&K provenance confusion | ~15 |
| Stale appendix statistics | 5 |
| Abstract/conclusion misalignment | 5 |

**Note:** Many issues overlap (e.g., a single sentence may contain both "3.8sigma" and "zeta_0 = 0.038"). The 59-issue count in the summary counts each distinct finding once.

---

## Recommended Revision Order

1. **First:** Reframe the zeta_0 narrative globally (C2 + C4 + C5). This is the largest conceptual change and cascades into everything else. Establish zeta_0 as free parameter, w_0(zeta_0) as the prediction curve.
2. **Second:** Remove/reframe all "3.8sigma detection" claims (C1). Replace with appropriate language about H&K data preference and combined multi-probe context.
3. **Third:** Fix Phi_0 = 0.477 → 0.076 in appendix (C3). Recompute derived quantities (F_0, p_0, profile table).
4. **Fourth:** Fix broken cross-reference (I1) and wrong data source (I5).
5. **Fifth:** Update abstract/conclusion alignment across all chapters (I4).
6. **Last:** Verify appendix chi^2 statistics are still valid after reframing (I3).

---

*Generated by 13J editorial audit. No LaTeX files were modified.*
