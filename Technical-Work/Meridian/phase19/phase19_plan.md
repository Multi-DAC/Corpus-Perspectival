# Phase 19: Prediction Extraction

**Created:** March 21, 2026
**Restructured:** March 22, 2026
**Authors:** Clayton & Clawd
**Status:** ACTIVE
**Organizing Principle:** Testability x Distinctiveness
**Context:** 19B.5 COMPLETE. Perturbation coupling invisible (ΔAIC(C vs D) = -1.91). Entire DESI signal is a w(z) template effect. The cosmological MCMC era is over — the framework can't be distinguished from ΛCDM with current cosmological data. Phase 19 pivots to cross-sector prediction extraction.

---

## The Pivot

Phases 13-18 established that Meridian lives in the near-ΛCDM regime. The v5 DR2 result (ΔAIC = +1.10) and the 19B.5 perturbation isolation (μ₀ = 0.12 ± 0.52, consistent with zero at 0.2σ) together say the same thing: **current cosmological probes cannot distinguish Meridian from standard ΛCDM.**

This is not failure. This is the Standard Model pattern. QFT didn't prove itself through one experiment — it proved itself by making *specific, falsifiable predictions across every sector of physics* until the weight of evidence became overwhelming. Meridian must do the same.

The new question: **Where does the 5D warped geometry + NCG spectral action + cuscuton self-tuning framework make predictions that differ from the Standard Model + GR, and when can those predictions be tested?**

We rank every track by two axes:
- **Testability:** When can an experiment check this? (Now / 5-10 years / 20+ years / unknown)
- **Distinctiveness:** Does Meridian predict something different from SM+GR? (Yes-sharp / Yes-soft / Maybe / No)

Only tracks scoring high on BOTH axes get priority. Framework-completion tracks (necessary but not directly testable) get scheduled between prediction tracks to keep the physics pipeline flowing.

---

## Completed Tracks

| Track | Result | Implication |
|-------|--------|-------------|
| **19B.1** | χ²/dof = 0.907, w₀ = -1.010 ± 0.023 | Constant-w consistent with ΛCDM |
| **19B.2** | χ²/dof = 0.902, w₀ = -0.813, wₐ = -0.902 | CPL preferred over constant-w (BAO-driven) |
| **19B.5** | ΔAIC(C vs D) = -1.91, μ₀ = 0.12 ± 0.52 | Perturbation coupling invisible. Template effect confirmed. |
| **19F.1** | Higgs coupling deviations at ξ = 1/6 | Below planned collider sensitivity |

---

## Priority 1: Sharp Predictions, Near-Term Tests (5-10 years)

These tracks produce numbers that specific planned or active experiments can check, where Meridian predicts something *distinct* from SM+GR. This is where the framework lives or dies.

### 19H.1 — Gravitational Wave Spectrum (LISA)
**Testability:** 2035-2040 (LISA operational)
**Distinctiveness:** HIGH — RS phase transition produces a specific GW spectral shape (peak frequency, amplitude, spectral tilt) that differs from both SM electroweak and generic first-order transitions.

| Step | Description |
|------|-------------|
| H.1a | Compute RS stabilization phase transition temperature from brane parameters |
| H.1b | Calculate bubble nucleation rate and wall velocity |
| H.1c | Derive GW power spectrum (peak frequency f*, amplitude Ωgw, spectral index) |
| H.1d | Compare against LISA sensitivity curve — is the signal detectable? |
| H.1e | Identify spectral features unique to RS (vs generic FOPT) |

**Match/Pivot/Kill:**
- **Match:** Signal within LISA band with distinctive RS features → strong confirmation, write detection prediction paper
- **Pivot:** Signal exists but below LISA sensitivity → identify what experiment COULD detect it (DECIGO, BBO); refine brane parameters to sharpen prediction
- **Kill:** No first-order phase transition in RS stabilization → RS stabilization mechanism needs revision; document constraint on brane parameter space

---

### 19E.1 — Neutrino Oscillation Parameters (DUNE)
**Testability:** 2028-2032 (DUNE collecting data)
**Distinctiveness:** HIGH — NCG spectral action constrains neutrino mass matrix via seesaw structure. Three-flavor parameters (θ₂₃ octant, δCP, mass ordering) are predicted, not fitted.

| Step | Description |
|------|-------------|
| E.1a | Extract full Dirac and Majorana mass matrices from NCG spectral action on RS background |
| E.1b | Run seesaw (Type I) to get light neutrino masses and PMNS matrix |
| E.1c | Compute θ₁₂, θ₁₃, θ₂₃, δCP, Δm²₂₁, Δm²₃₁ |
| E.1d | Compare against current global fits (NuFIT 5.3) and DUNE projected sensitivity |
| E.1e | Identify the sharpest discriminator (likely θ₂₃ octant + δCP correlation) |

**Match/Pivot/Kill:**
- **Match:** Parameters within current experimental bounds, with sharp θ₂₃/δCP prediction in DUNE range → headline prediction, publish immediately
- **Pivot:** Parameters within bounds but predictions too soft (large uncertainty from brane parameters) → identify which brane parameter dominates; feed into 19J.1
- **Kill:** Any oscillation parameter outside 3σ of measured value → NCG spectral action or seesaw structure needs modification; document which parameter fails and what it constrains

---

### 19F.2 / 19F.3 — Radion + KK Graviton (HL-LHC)
**Testability:** 2029-2035 (HL-LHC full luminosity)
**Distinctiveness:** HIGH — Radion mass and coupling, first KK graviton resonance mass are specific to RS geometry. Not predicted by any non-extra-dimensional framework.

| Step | Description |
|------|-------------|
| F.2a | Compute radion mass from stabilization potential (Goldberger-Wise or cuscuton) |
| F.2b | Calculate radion production cross-section (gg → φ) at 14 TeV |
| F.2c | Compute radion decay branching ratios (WW, ZZ, hh, γγ, tt) |
| F.3a | Compute first KK graviton mass from RS geometry |
| F.3b | Calculate KK graviton production cross-section and decay width |
| F.3c | Compare against HL-LHC projected exclusion limits |

**Match/Pivot/Kill:**
- **Match:** Radion/KK masses in HL-LHC discovery range (1-5 TeV) with identifiable signatures → write prediction paper with specific search channels
- **Pivot:** Masses above HL-LHC reach → predict for FCC-hh (100 TeV); document mass bounds
- **Kill:** Radion mass calculation inconsistent (tachyonic, or stabilization fails) → RS stabilization mechanism needs fundamental revision

---

### 19D.2 — Dark Matter X-ray Line
**Testability:** NOW (XMM-Newton, Chandra archival; XRISM operational)
**Distinctiveness:** MEDIUM-HIGH — Sterile neutrino from seesaw with keV mass predicts specific X-ray line energy. The 3.5 keV anomaly is contested but the prediction is checkable.

| Step | Description |
|------|-------------|
| D.2a | Extract sterile neutrino mass from seesaw spectrum (19E.1 prerequisite) |
| D.2b | Compute radiative decay rate (ν_s → ν + γ) |
| D.2c | Predict X-ray line energy and flux for galaxy clusters |
| D.2d | Compare against 3.5 keV anomaly data and XRISM sensitivity |

**Match/Pivot/Kill:**
- **Match:** Predicted line energy consistent with 3.5 keV (or other observed anomaly) → strong indirect confirmation
- **Pivot:** Predicted energy differs from 3.5 keV → make specific prediction for XRISM to test; the 3.5 keV may be systematic
- **Kill:** Sterile neutrino too heavy (MeV+) or too light (eV) for X-ray detection → DM candidate is not astrophysically observable via this channel; pivot to 19D.4

---

### 19X.1 — Instanton Action (Chern-Simons Coupling)
**Testability:** 5-15 years (laboratory EM experiments, potentially magnetic field correlations)
**Distinctiveness:** HIGH — Non-perturbative cuscuton coupling to electromagnetism via Chern-Simons term. No SM analog. Clayton's priority.

| Step | Description |
|------|-------------|
| X.1a | Write the full cuscuton + U(1) Chern-Simons Lagrangian on RS background |
| X.1b | Find instanton solution (Euclidean action, topological charge) |
| X.1c | Compute instanton action S_inst — is it finite, large, or small? |
| X.1d | If finite: compute tunneling rate and identify observable consequences |
| X.1e | If small (S < 10): identify laboratory signatures (EM anomalies in strong B fields) |

**Match/Pivot/Kill:**
- **Match:** Finite instanton action with observable consequences in accessible field strengths → novel detection channel, potentially the most distinctive Meridian prediction
- **Pivot:** Action exists but requires extreme field strengths (magnetar-scale) → astrophysical prediction only; look for signatures in magnetar data
- **Kill:** Action divergent or identically zero → CS coupling is perturbative only; non-perturbative sector doesn't exist in this formulation

---

## Priority 2: Near-Term Tests, Moderate Distinctiveness

These tracks test consistency with existing data or make predictions that are less uniquely Meridian but still constraining.

### 19I.3 — BBN Consistency
**Testability:** NOW (primordial abundances are measured)
**Distinctiveness:** MEDIUM — Extra-dimensional modifications to expansion rate during BBN epoch. Meridian must reproduce observed ⁴He, D/H, ⁷Li abundances or it's ruled out.

| Step | Description |
|------|-------------|
| I.3a | Compute H(T) during BBN epoch with RS modifications (radion, brane tension) |
| I.3b | Run BBN code (PArthENoPE or AlterBBN) with modified expansion rate |
| I.3c | Compare predicted abundances against observed primordial values |
| I.3d | Identify allowed brane parameter region from BBN constraints |

**Match/Pivot/Kill:**
- **Match:** All abundances within observational bounds → framework passes critical consistency test; BBN constrains brane parameters (feed to 19J.1)
- **Pivot:** ⁷Li tension persists (like in standard BBN) → not distinctive but not problematic; focus on ⁴He and D/H
- **Kill:** ⁴He or D/H outside observed bounds for ALL brane parameter choices → fatal; framework is inconsistent with nuclear physics

---

### 19A.3 — Black Hole Solutions
**Testability:** NOW-5 years (EHT, LIGO/Virgo/KAGRA ringdown)
**Distinctiveness:** MEDIUM — Cuscuton-modified black holes may have altered quasinormal mode spectrum.

| Step | Description |
|------|-------------|
| A.3a | Find static spherically symmetric BH solution with cuscuton field |
| A.3b | Compute quasinormal mode frequencies |
| A.3c | Compare against LIGO ringdown measurements |
| A.3d | Identify deviation from Kerr that EHT could constrain |

**Match/Pivot/Kill:**
- **Match:** QNM shifts within current measurement precision → testable with next-gen GW detectors
- **Pivot:** Shifts below current precision → predict for LISA or ET; document magnitude
- **Kill:** No well-defined BH solution exists → cuscuton sector needs boundary condition revision

---

### 19G.1 — Inflationary Power Spectrum
**Testability:** 5-10 years (CMB-S4, LiteBIRD)
**Distinctiveness:** MEDIUM — RS warping modifies inflationary predictions (n_s, r, running). Must be consistent with Planck; may predict r in LiteBIRD range.

| Step | Description |
|------|-------------|
| G.1a | Identify inflationary mechanism in RS+cuscuton framework |
| G.1b | Compute slow-roll parameters on warped background |
| G.1c | Derive n_s, r, dn_s/dlnk |
| G.1d | Compare against Planck 2018 and predict for CMB-S4/LiteBIRD |

**Match/Pivot/Kill:**
- **Match:** n_s within Planck bounds, r in LiteBIRD range (r > 0.001) → prediction paper
- **Pivot:** r below LiteBIRD sensitivity → not testable soon; document for future missions
- **Kill:** n_s outside Planck 2σ → inflationary sector of framework is wrong; may require modified potential

---

### 19C.3 — Proton Decay
**Testability:** NOW-10 years (Super-K, Hyper-K)
**Distinctiveness:** MEDIUM-HIGH — RS geometry modifies GUT-scale gauge coupling unification point, shifting proton lifetime prediction.

| Step | Description |
|------|-------------|
| C.3a | Determine unification scale from 19C.1 results (prerequisite) |
| C.3b | Compute proton partial lifetimes (p → e⁺π⁰, p → K⁺ν̄) with RS threshold corrections |
| C.3c | Compare against Super-K bounds and Hyper-K projected sensitivity |

**Match/Pivot/Kill:**
- **Match:** Lifetime prediction within Hyper-K reach (τ < 10³⁵ years) → distinctive prediction
- **Pivot:** Lifetime above Hyper-K reach → document bound; wait for next-generation detector
- **Kill:** Proton stable (no unification) → gauge unification doesn't occur in RS framework; fundamental problem

---

## Priority 3: Framework Completion

These tracks don't produce directly testable predictions but are prerequisites for Priority 1-2 tracks or resolve internal consistency questions. Schedule between prediction tracks.

### 19J.1 — Complete Brane Parameter Space Scan
**Purpose:** Every prediction in P1-P2 depends on brane parameters (k, Λ₅, brane tensions). This scan maps the full allowed region using all available constraints (w₀, ζ₀, BBN, unitarity, stability).

| Step | Description |
|------|-------------|
| J.1a | Define parameter space boundaries from theoretical constraints |
| J.1b | Scan over (k, Λ₅, T_vis, T_hid) with cuscuton self-tuning |
| J.1c | Apply all observational constraints as exclusion regions |
| J.1d | Identify the surviving parameter volume — is it narrow or wide? |
| J.1e | For each P1 prediction, map how it varies across allowed parameters |

**Gate function:** If surviving volume is zero → framework is ruled out (this would be the most important result of Phase 19). If volume is a point → all predictions are sharp. If volume is a region → predictions have ranges, and we identify which experiment narrows it most.

---

### 19A.1 — Cross-Term Cancellation Proof
**Purpose:** The 5D action has gravitational-scalar cross terms. Proving they cancel (or quantifying their residual) determines whether the cuscuton decoupling is exact or approximate.

---

### 19C.1 — AS Beta Functions on Warped RS Background
**Purpose:** Prerequisite for gauge unification (19C.3), proton decay, and collider predictions. The warped background modifies running — need to compute this before making particle physics predictions.

---

### 19J.2 / 19J.3 — ζ₀ Determination
**Purpose:** The cuscuton parameter ζ₀ controls the magnitude of all dark energy deviations. Pinning it from first principles (asymptotic safety or self-adjoint extension uniqueness) would sharpen every cosmological prediction.

---

## Priority 4: Deep Frontiers

Long-shot tracks. Success probability 10-20% but potentially transformative. Run when P1-P3 generate breathing room.

| Track | Title | Question |
|-------|-------|----------|
| **14A** | NCG-AS Basin of Attraction | Does the NCG spectral action emerge as a fixed point of asymptotic safety? |
| **14B** | Three Generations (N_g = 3) | Can the framework derive WHY there are exactly three fermion generations? |
| **14C** | Brane Parameter First-Principles | Can brane parameters be derived rather than fitted? |
| **14D** | The Coincidence Problem | Why is dark energy density ~ matter density NOW? |

---

## Execution Order

Based on prerequisites, computational cost, and information value:

### Sprint 1: Weeks 1-2
**Primary:** 19E.1 (neutrinos) — highest information density. Requires only NCG spectral action algebra, no MCMC. Produces 6+ testable numbers.
**Parallel:** 19X.1 (instanton) — independent calculation, Clayton's priority. Pure theory, no data dependencies.
**Background:** 19I.3 (BBN) — consistency check. If this fails, everything else is moot. Run early.

### Sprint 2: Weeks 3-5
**Primary:** 19H.1 (GW spectrum) — requires Phase transition temperature, which 19I.3 constrains.
**Parallel:** 19F.2/F.3 (collider) — independent of GW. Radion mass from stabilization potential.
**Background:** 19J.1 (parameter scan) — accumulates constraints from Sprint 1 results.

### Sprint 3: Weeks 6-8
**Primary:** 19D.2 (X-ray line) — requires 19E.1 seesaw spectrum as input.
**Parallel:** 19A.3 (black holes) — independent calculation.
**Support:** 19C.1 (AS beta functions) — prerequisite for Sprint 4 proton decay.

### Sprint 4: Weeks 9-12
**Primary:** 19C.3 (proton decay) — requires 19C.1.
**Parallel:** 19G.1 (inflation) — independent.
**Support:** 19A.1 (cross-term cancellation) — mathematical proof, schedule when computational tracks need cooling.

### Sprint 5: Weeks 13+
- 19J.2/J.3 — ζ₀ determination
- PRL letter — now informed by all P1 results, not just cosmological decomposition
- Tier 4 frontiers as energy permits

### Cross-Sprint Protocol

After EACH track completion:

1. **Match:** Result consistent with framework + experimentally distinguishable → record prediction, identify sharpest test, flag for publication
2. **Pivot:** Result consistent but not distinguishable (or depends on unknown parameters) → identify what additional information would sharpen it; feed back into 19J.1
3. **Kill:** Result inconsistent with observation or internally contradictory → document the failure honestly; identify what it constrains; assess whether the failure is local (one sector) or global (framework-threatening)

**Information flows forward.** Every Sprint's results constrain the next Sprint's inputs. The parameter scan (19J.1) accumulates constraints continuously and gets tighter with each completed track.

---

## Success Criteria (Revised)

The old success criteria centered on PRL submission. The new criteria center on prediction density:

1. **5+ sharp, falsifiable predictions** across different physics sectors (neutrinos, GW, collider, DM, BBN)
2. **Each prediction includes:** central value, uncertainty range, experimental timeline, match/pivot/kill protocol
3. **Parameter space mapped** — surviving brane parameter volume quantified, with each prediction's sensitivity to parameters documented
4. **At least one "kill" documented** — an honest constraint or tension. If every track matches, we're probably not being rigorous enough.
5. **No framework-fatal inconsistencies** — BBN, unitarity, and stability tests all pass

## What Changed from v1

| Old (v1) | New (v2) |
|----------|----------|
| Organized by publication urgency | Organized by testability x distinctiveness |
| PRL letter as top priority | PRL letter moved to Sprint 5 (informed by all results) |
| 19B.5 as "most important test" | 19B.5 COMPLETE — answer is definitive (template effect) |
| Cosmological MCMC as primary tool | Cross-sector prediction extraction as primary method |
| "First to publish decomposition" | "First to extract the full prediction suite" |
| Success = PRL accepted | Success = 5+ falsifiable predictions across sectors |

The framework has survived its cosmological test. Now it needs to predict particle physics, gravitational waves, neutrinos, and nucleosynthesis — or fail honestly trying. This is how theories earn their place.

---

*"Seek the balance, work the science, synthesize." — Puscifer's Theorem*

🦞🧍💜🔥♾️
