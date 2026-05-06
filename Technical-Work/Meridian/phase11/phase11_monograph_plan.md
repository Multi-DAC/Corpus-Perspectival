# Phase 11: The Meridian Monograph

**A Comprehensive Documentation of Five-Dimensional Self-Tuning Cosmology**

**Authors:** Clayton W. Iggulden-Schnell & Clawd
**Formalized:** 2026-03-16
**Purpose:** Transform 10 phases of research into a rigorous, publishable body of work.

---

## 0. Scope and Principles

**What goes in:** Mathematics, derivations, computational results, observational confrontation, no-go theorems, falsifiable predictions. Everything derived from A1, A2, and established physics.

**What stays out:** Leaked information, speculative consciousness mechanisms, engineering applications (reserved for Phase 12). Publications rely solely on math and principles.

**Format:** A monograph structured as five papers, each self-contained but cross-referenced. Can be submitted individually to journals or as a unified document (e.g., arXiv monograph, book chapter).

---

## 1. Paper Series Structure

### Paper I: "Self-Tuning Cosmology from Five-Dimensional Warped Geometry"
**The Foundation Paper** — Derives the complete model from first principles.

| Section | Content | Source Phases |
|---------|---------|--------------|
| I.1 | Introduction: CC problem, self-tuning, DESI context | — |
| I.2 | 5D action with S^1/Z_2 orbifold compactification | Phase 1 |
| I.3 | Self-tuning mechanism: bulk dynamics absorb vacuum energy | Phase 1 |
| I.4 | KK reduction to 4D: effective cuscuton P(X) = mu^2 sqrt(2X) | Phase 2 |
| I.5 | Non-minimal coupling zeta_0 from hierarchy stabilization | Phase 2 |
| I.6 | NCG spectral action on warped orbifold | Phase 5 |
| I.7 | Gauss-Bonnet correction: P(X) = mu^2 sqrt(2X) + eps_1 X | Phase 5, 10A |
| I.8 | The one-parameter theory: everything from zeta_0 | Phase 2 |
| I.9 | Dark energy equation of state: w_0 = -0.993 | Phase 10A |
| I.10 | Propagation speed: c_s ~ 10c, ghost-free | Phase 10A |

**Key deliverables to write:**
- D11.1: Clean derivation of the full action (5D -> 4D -> corrected)
- D11.2: Self-contained NCG spectral action section
- D11.3: The eps_1 derivation (Seeley-DeWitt -> GB -> kinetic correction)

**Source files:** phase1/step1_master_action.md, phase2/, phase5/task5_1-5_7, phase10/task10_1_general_px.md

---

### Paper II: "Observational Confrontation of Five-Dimensional Self-Tuning"
**The Data Paper** — Tests the model against all available data.

| Section | Content | Source Phases |
|---------|---------|--------------|
| II.1 | Introduction: model predictions vs current surveys | — |
| II.2 | Hubble-Kristian data fit: zeta_0 = 0.038, Delta chi^2 = -15 | Phase 6 |
| II.3 | DESI DR2 BAO analysis: model vs LCDM vs CPL | Phase 11 (morning work) |
| II.4 | The CPL artifact: literature review and quantitative verification | Phase 11 (morning work) |
| II.5 | Fisher matrix forecasts: Euclid, Rubin, Roman | Phase 6 |
| II.6 | CMB constraints and Planck compatibility | Phases 3-4 |
| II.7 | Modified gravity tests: solar system, lunar ranging | Phase 4 |
| II.8 | Five falsifiable predictions with required precision | All phases |

**Key deliverables to write:**
- D11.4: DESI BAO analysis section (expand bao_model_comparison.py to full MCMC if possible)
- D11.5: CPL artifact analysis section (integrate literature review)
- D11.6: Updated Fisher matrix with current DESI DR2 precision
- D11.7: Comprehensive predictions table with instrument requirements

**Source files:** phase6/meridian_fisher.py, phase11/bao_comparison_results.txt, phase11/cpl_artifact_literature_review.md, phase3/meridian_cosmology.py

---

### Paper III: "No-Go Theorems for Dynamical Dark Energy in Self-Tuning Warped Gravity"
**The Exclusion Paper** — Documents the systematic search and its structural results.

| Section | Content | Source Phases |
|---------|---------|--------------|
| III.1 | Introduction: why w ≈ -1 is a prediction, not a limitation | — |
| III.2 | The zero kinetic energy theorem and its consequences | Phase 8 |
| III.3 | Phase 8 tracks: perturbative resolution attempts (7 tracks) | Phase 8 |
| III.4 | Phase 9: non-perturbative program (3 tracks) | Phase 9 |
| III.5 | Phase 10: alternative models and extensions (6 tracks) | Phase 10 |
| III.6 | The Horndeski dilemma: self-tuning determines P(X) | Phase 10F |
| III.7 | The structural insight: all failures share a common root | Phases 8-10 |
| III.8 | Classification of what CAN and CANNOT modify w in this framework | Synthesis |

**Key deliverables to write:**
- D11.8: The zero KE theorem (formal statement + proof)
- D11.9: The Horndeski dilemma (formal statement + proof)
- D11.10: Track summary table (18 tracks, kill mechanisms, quantitative bounds)
- D11.11: The structural classification theorem

**Source files:** phase8/task8_1-8_7.md, phase9/task9_1-9_7.md, phase10/task10_1-10_12.md

---

### Paper IV: "Noncommutative Spectral Geometry on Warped Orbifolds: Topological Couplings and Gravitational Corrections"
**The Mathematics Paper** — The NCG formalism and its physical consequences.

| Section | Content | Source Phases |
|---------|---------|--------------|
| IV.1 | Introduction: NCG spectral action in extra-dimensional physics | — |
| IV.2 | The spectral triple on M_4 x I x F | Phase 5 |
| IV.3 | Seeley-DeWitt coefficients on S^1/Z_2 | Phase 5 |
| IV.4 | Gauss-Bonnet universality: dimension and topology independence | Phases 5, 10E |
| IV.5 | Chern-Simons terms from APS index theorem | Phase 9B |
| IV.6 | theta_EM ~ O(1): the topological EM-gravity coupling | Phase 9B |
| IV.7 | Perturbative vs non-perturbative channels | Phase 9 |
| IV.8 | Connection to Standard Model coupling structure | Phase 5 |

**Key deliverables to write:**
- D11.12: Clean derivation of spectral action on warped orbifold
- D11.13: CS term derivation with theta_EM computation
- D11.14: GB universality proof (independence from d and topology)
- D11.15: Non-perturbative channel analysis

**Source files:** phase5/task5_1-5_3.md, phase9/task9_4_cs_terms.md, phase10/task10_11_6d_extension.md

---

### Paper V: "The Sound Speed of Dark Energy: A Superluminal Prediction from Five-Dimensional Geometry"
**The Prediction Paper** — Short, targeted, high-impact.

| Section | Content | Source Phases |
|---------|---------|--------------|
| V.1 | Introduction: dark energy sound speed as discriminator | — |
| V.2 | Derivation: c_s = sqrt(eps_1/2) * mu/H_0 ~ 10c | Phase 10A |
| V.3 | Physical interpretation: from c_s = infinity to c_s = 10c | Phases 1, 10A |
| V.4 | Observational signatures: ISW, perturbation growth, GW correlation | Phase 4 |
| V.5 | Comparison to other dark energy models | Literature |
| V.6 | Detection prospects: LISA, Einstein Telescope, CMB lensing | Forecast |

**Key deliverables to write:**
- D11.16: c_s derivation (self-contained, short)
- D11.17: Observational signatures analysis
- D11.18: Instrument requirements for c_s detection

**Source files:** phase10/task10_1_general_px.md, phase4/

---

## 2. Writing Order

The papers have dependencies. Optimal writing order:

| Order | Paper | Reason |
|-------|-------|--------|
| 1st | **Paper I** | Foundation — everything else references this |
| 2nd | **Paper III** | Exclusion — independent of data analysis, uses Phase 8-10 deliverables directly |
| 3rd | **Paper IV** | Mathematics — builds on Paper I's notation |
| 4th | **Paper II** | Data — needs Papers I and III for model definition and context |
| 5th | **Paper V** | Prediction — short, can be written quickly once Papers I and IV establish the derivation |

**Estimated deliverables:** 18 (D11.1 through D11.18)
**Estimated sections:** 42 across 5 papers

---

## 3. Quality Standards

Each paper must meet:
- [ ] All equations numbered and derivable from stated assumptions
- [ ] No free parameters adjusted to fit dark energy data (zeta_0 is fixed by hierarchy, eps_1 by NCG)
- [ ] Explicit statement of what is derived vs what is assumed
- [ ] Kill conditions and negative results reported honestly
- [ ] All numerical results reproducible from included code or equations
- [ ] Comparison with existing literature (minimum 50 references per paper)
- [ ] Self-contained: readable without the other papers in the series

---

## 4. Notation Convention

To be established in Paper I and used throughout:
- G_5, G_4: 5D and 4D gravitational couplings
- Phi, phi: 5D bulk scalar and 4D effective scalar
- zeta_0: non-minimal coupling (= 0.038)
- eps_1: GB kinetic correction (~ 10^{-2})
- P(X): kinetic function, X = (1/2)g^{mu nu} d_mu phi d_nu phi
- w_0: dark energy equation of state today
- c_s: sound speed of dark energy perturbations
- r_d: sound horizon at baryon drag
- D_M, D_H, D_V: comoving angular diameter, Hubble, volume-averaged distances

---

## 5. Target Venues

| Paper | Primary Target | Backup |
|-------|---------------|--------|
| I (Foundation) | Physical Review D | JHEP |
| II (Data) | JCAP | Astronomy & Astrophysics |
| III (No-Go) | Physical Review Letters (short) or PRD | JHEP |
| IV (Math) | Communications in Mathematical Physics | Journal of Geometry and Physics |
| V (Sound Speed) | Physical Review Letters | JCAP |

Papers III and V are PRL candidates (short, sharp results with broad impact).

---

## 6. Execution Plan

### Stage A: Paper I Foundation (estimated: 2-3 sessions)
- A.1: Write D11.1 (full derivation, 5D -> 4D -> corrected P(X))
- A.2: Write D11.2 (NCG spectral action section)
- A.3: Write D11.3 (eps_1 derivation)
- A.4: Assemble Paper I draft
- A.5: Internal review and revision

### Stage B: Paper III Exclusion (estimated: 2-3 sessions)
- B.1: Write D11.8 (zero KE theorem, formal)
- B.2: Write D11.9 (Horndeski dilemma, formal)
- B.3: Write D11.10 (18-track summary table)
- B.4: Write D11.11 (structural classification)
- B.5: Assemble Paper III draft
- B.6: Internal review

### Stage C: Paper IV Mathematics (estimated: 2-3 sessions)
- C.1: Write D11.12-D11.15 (spectral geometry, CS, GB, channels)
- C.2: Assemble Paper IV draft
- C.3: Internal review

### Stage D: Paper II Data (estimated: 2-3 sessions)
- D.1: Expand BAO analysis (attempt full MCMC or at minimum Fisher analysis with DESI data)
- D.2: Write D11.4-D11.7 (DESI section, CPL artifact, Fisher update, predictions)
- D.3: Assemble Paper II draft
- D.4: Internal review

### Stage E: Paper V Prediction (estimated: 1 session)
- E.1: Write D11.16-D11.18 (c_s derivation, signatures, detection)
- E.2: Assemble Paper V draft
- E.3: Internal review

### Stage F: Final Assembly (estimated: 1-2 sessions)
- F.1: Cross-reference check across all five papers
- F.2: Notation consistency pass
- F.3: Bibliography compilation
- F.4: Abstract and introduction harmonization
- F.5: Prepare submission packages

---

## 7. Kill Conditions

Phase 11 is documentation, not new research. Kill conditions are different:
- **If a derivation doesn't reproduce a claimed result:** Fix the derivation or revise the claim. Do not paper over.
- **If a computation gives different numbers on rerun:** Investigate and resolve before including.
- **If the literature already contains our result:** Cite it, add our perspective, don't claim novelty on that point.
- **If Clayton redirects priorities (e.g., VQ1 specs drop):** Pause at current stage boundary, record state, resume later.

---

## 8. Connection to Phase 12

Phase 11 produces the academic record. Phase 12 (Technology Derivation Program) builds on Paper IV specifically:
- CS coupling geometry → potential engineering applications
- c_s ~ 10c propagation → communication channel analysis
- zeta_0 amplification → gravitational modification theory
- Non-perturbative soliton channel → coupling enhancement methods

Phase 12 does NOT begin until Phase 11 Papers I and IV are drafted (they establish the mathematical foundations that the engineering analysis requires).

---

*The Meridian Monograph: From two axioms to five papers.*
