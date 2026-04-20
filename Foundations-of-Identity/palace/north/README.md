# North Wing — Physics (Project Meridian + Killing Form + Glider)

*Theory of Everything: 5D RS warped geometry + NCG spectral action + cuscuton self-tuning. Plus the empirical training-dynamics program (KF) and the open-weight model program (Glider).*
*Built out 2026-04-17. Replaces the routing-only structure with actual rooms; phase quick-nav preserved at the bottom as the lab notebook.*

---

## Library Pointer (CANONICAL since 2026-04-16 reorg)

The compiled monograph and the published Library volume live at:
- **Library/Meridian/** — `repo-staging/Corpus-Perspectival/Library/Meridian/` — drafts, monograph .tex, figures, ROADMAP
- **Compiled PDF** — `repo-staging/Corpus-Perspectival/Library/Meridian/monograph/meridian_monograph.pdf` (181pp, revised 2026-04-15)
- **244 computation scripts** — `repo-staging/Corpus-Perspectival/Technical-Work/Meridian/scripts/`
- **Killing Form documentation** — `repo-staging/Corpus-Perspectival/Technical-Work/Killing-Form/documentation/` — KF_ROADMAP.md, SMALL_MODEL_DESIGN.md, cross_domain_killing_form.md
- **Glider** — `repo-staging/Corpus-Perspectival/Technical-Work/Glider/` — open-weight model program (target: Gemma 4 e2b)
- **Published Zenodo** — DOI 10.5281/zenodo.19519818 (Technical Summary, 70 downloads)

The phase files at `projects/Project Meridian/phase*/` remain as the historical work record (lab notebook). The Library volume is the result.

---

## Rooms

| Room | Purpose | Where it lives |
|------|---------|---------------|
| **Hall of Axioms** | The 2 framework assumptions + the derivation chain | This file (below) |
| **Hall of Predictions** | The canonical prediction ledger — confirmed, pending, parametric, structural | This file (below) |
| **Hall of Eliminations** | What got ruled out and what the negatives revealed | This file (below) |
| **Constants Room** | All framework-fixed and observation-derived numerical values | This file (below) |
| **Monograph Room** | Current state of written document | `Library/Meridian/monograph/` |
| **12% Chamber** | The gauge unification tension — RESOLVED in Phase 22 | `phase22/phase22_monograph_chapter.md` |
| **KF Wing** | 85+ findings from the Killing Form program | This file + Technical-Work/Killing-Form |
| **Glider Wing** | Open-weight implementation track | This file + Technical-Work/Glider |
| **Phase Quick-Nav** | Lab notebook — phase-by-phase results | Bottom of this file |

---

## Hall of Axioms

The framework rests on **two physical assumptions** plus the standard NCG spectral action machinery.

### Axiom RS1 — Single Warped Extra Dimension
*Spacetime is 4 + 1 dimensional with the extra dimension compactified on an S¹/Z₂ orbifold of length L. The 5D metric is warped: ds² = e^{−2A(y)} η_{μν} dx^μ dx^ν + dy². Two branes sit at the orbifold fixed points y = 0 (UV) and y = L (IR).*

This is Randall-Sundrum 1 (RS1) without modification.

### Axiom Cuscuton — Self-Tuning Constraint Field
*A cuscuton scalar field φ with infinite sound speed (c_s² = ∞) lives in the bulk. Its action makes it a constraint field — it propagates no degrees of freedom on its own but enforces a relation between the geometry and the matter content at every point in time.*

The cuscuton sets w(z) → −1 dynamically, providing self-tuning of the cosmological constant without fine-tuning.

### The Derivation Chain

From RS1 + Cuscuton + NCG spectral action:

1. **Warp factor** A(y) determined by Einstein equations + brane tension matching
2. **KK tower** of bulk modes with spacing m_n ∝ ke^{−kL}
3. **Spectral action** on the orbifold computes effective 4D physics from 5D geometry
4. **Cuscuton constraint** fixes the dark-energy equation of state w_0 ≈ −1 with calculable deviation
5. **Quartic Casimir of E₆** (from Phase 22) gives κ₁ = −0.01654 — closes the 12% gauge unification gap
6. **NCG fermion sector** produces SM matter content from finite NCG algebra A_F

The key claim: this is **two physics inputs** (RS1, cuscuton) not five. The rest is calculation.

---

## Hall of Predictions

The canonical prediction ledger. Each entry: prediction, current data, status, decisive future test.

### Confirmed

| Prediction | Value | Data | Status |
|-----------|-------|------|--------|
| **w_0 ≠ −1** | w_0 = −0.990 (model) | DESI DR2: w_0 = −0.83 ± 0.06 (CPL); model-independent consistent with −0.99 | Confirmed direction, parameter test pending DESI Y5 |
| **w_a ≈ 0** | \|w_a\| ≲ 0.02 | DESI DR2 CPL: w_a = −0.62 ± 0.26 (2.4σ); model-independent: consistent with 0 | Tension at 2.4σ — DESI Y5 (σ ~ 0.05) decisive in 2027 |
| **κ₁ closes the 12% gap** | κ₁ = −0.01654 | Phase 22 computation | Internally confirmed (S₃ → S₂ Wilson line breaking on resolved fixed points) |
| **Cross-domain Coherence Principle** | 4-condition pattern | KF program 85+ findings, multi-domain | Empirically confirmed in NN training; ecology, physics convergent |

### Parametric Curve (the hard test)

The framework's strongest prediction is a **curve in observable space**, not a point:

$$w_0(\zeta) = -1 + C_\mathrm{KK}/\zeta, \quad C_\mathrm{KK} = (1.64 \pm 0.33) \times 10^{-4}$$

- Weighted-mean point: ζ = 0.016 ± 0.002, giving w_0 = −0.990
- **Falsifier:** observed (w_0, ζ) lies off this curve at >3σ
- Decisive data: DESI Y5 + Euclid (σ(w_0) ~ 0.005, 2030–32)

### Pending

| Prediction | Value | Decisive Test |
|-----------|-------|--------------|
| Sound speed c_s | c_s ∈ [12c, 15c]; c_s² ≈ 216 | f σ_8 measurements, percent-level precision (Euclid + Rubin) |
| Growth-expansion decoupling | μ = Σ = 1, α_T = 0 (zero DE clustering) | Cross-correlation w_0 ≠ −1 with structure growth |
| LISA gravitational-wave signal | 1.4 mHz characteristic | LISA mission data (post-2035) |
| Light bulk axion spectrum | 9 untwisted axions, neV–meV, g ~ 10⁻²¹ | Ultra-weak coupling — direct detection borderline |
| Radion mass | m_rad ~ 120 GeV (SM CW + NCG quantum) | LHC Run 4 / FCC reach |
| Bubble nucleation barrier | B = 54,937 (27D path) | Lab-scale experiment (Phase 24 device, ~$200K–$850K) |

### Structural

| Prediction | Status |
|-----------|--------|
| The combination {w_0 ≠ −1, w_a ≈ 0, c_s ~ 15c, μ = Σ = 1, α_T = 0} is unique to cuscuton in 5D self-tuning | Verified — no competitor model produces this pattern |
| Dark energy clustering vanishes | Distinguishes cuscuton from quintessence |
| AdS bubble dynamics: crunches in 32 ps, max extent ~1 cm | Self-limiting via crunch — passes safety analysis |

---

## Hall of Eliminations

Honest negatives. What got ruled out and what we learned from each.

### Phase 21 — The Doors

| Door | Hypothesis | Result | Lesson |
|------|-----------|--------|--------|
| Door 2 | F-theory corrections close the 12% gap | NEGATIVE — corrections too small | Pushed search to Wilson line breaking (Door 4) |
| Door 3 | F-theory estimation alternative | NEGATIVE | Confirmed Door 2 ruling |

### Phase 20 — The 15 Eliminations

15 distinct alternatives systematically eliminated. The Mercury analogy: the 12% looked like a bookkeeping error, treated like Mercury's perihelion precession in the 1850s — could have been Newtonian, turned out to be a window into deeper structure (GR / Wilson line breaking).

### Phase 23.1 — Engineering Channels

| Channel | Status | Why |
|--------|--------|-----|
| Cuscuton-axion coupling | CLOSED | Mass mismatch |
| Topological transitions (untwisted) | CLOSED | Bulk EFT suppression |
| Schwinger pair production at expected scales | CLOSED | Field strengths insufficient |
| Trace anomaly coupling | CLOSED | Subdominant |
| Pure geometry (radion) | CLOSED | Massive (m ~ 120 GeV) |
| Parametric resonance | CLOSED | Cross-section too small |
| **DM coherence** | **CONDITIONALLY OPEN** | The remaining live channel |

**Engineering case closed within bulk EFT** (Phase 23.1) — but **B.2 missed brane-localized twisted sectors and topological transitions**, which Phase 23.2a found alive at 14 orders of magnitude stronger coupling. *The lesson: a closed search is closed only within its assumed sector.*

### Phase 23.2 — What 23.1 Missed

- **Twisted CS coupling** g_CS = 10⁻⁷ GeV⁻¹ (vs. bulk 10⁻²¹) — **14 orders stronger**
- **Barrier = 82 GeV** (electroweak scale, not Planck-suppressed)
- **B.4 retrodiction:** Podkletnov 2/3 components matched; Biefeld-Brown 0/3 (correctly excluded)

### Phase 23.1 vs 23.2 — The Methodology Note

The pattern matters: a Phase that closes a channel within its assumed sector should be re-checked for sector-specific assumptions before being treated as definitive. Mirror #15 (cross-sector over-analogizing) and the 23.1/23.2 sequence are the same mistake-class.

---

## Constants Room

All numerical values used in the framework. Values are framework-fixed (F), observation-derived (O), or composite (C).

### Cosmology

| Quantity | Value | Type | Source |
|----------|-------|------|--------|
| w_0 (model) | −0.990 | C | Cuscuton + ζ = 0.016 |
| C_KK | (1.64 ± 0.33) × 10⁻⁴ | C | KK tower + curve fit |
| ζ (warp factor curvature ratio) | 0.016 ± 0.002 | O | DESI weighted mean |
| c_s² (cuscuton) | ≈ 216 | C | C_q / ε_1 |
| ε_1 | parametric | F | Free in axiom set |
| α_T (GW propagation tilt) | 0 | F | Cuscuton signature |
| μ, Σ (modified gravity params) | 1 | F | Cuscuton signature |

### Geometry / NCG

| Quantity | Value | Type | Source |
|----------|-------|------|--------|
| κ₁ | −0.01654 | C | Phase 22 (S₃ → S₂, Wilson line, anomaly polynomial) |
| Quartic Casimir of E₆ correction | c₂ = −6 | C | On exceptional divisor |
| v (Wilson line VEV) | 20.5% of compactification scale | C | Phase 22 |
| Compactification length L | parametric | F | RS1 |
| Warp scale k | parametric | F | RS1 |
| Number of light bulk axions | 9 (untwisted) | C | Hodge numbers |
| Bulk axion mass range | neV – meV | C | A.2 spectrum |
| Bulk axion coupling | g ~ 10⁻²¹ | C | A.2 |

### Engineering / Branes

| Quantity | Value | Type |
|----------|-------|------|
| Twisted CS coupling g_CS | 10⁻⁷ GeV⁻¹ | C (Phase 23.2a) |
| Tunneling barrier (twisted, electroweak path) | 82 GeV | C |
| 27D bounce action B | 54,937 | C (Phase 24 I.1) |
| 27D corrections | 0.33% | C |
| Radion mass m_rad | ~ 120 GeV | C (Phase 23 A.1b) |
| AdS bubble crunch time | 32 ps | C |
| AdS bubble max extent | ~ 1 cm | C |

### Coherence Principle (KF program)

| Quantity | Value | Type |
|----------|-------|------|
| Amplification under separation | 38,963× | O (KF empirics) |
| Destruction under coupling | 61% | O (KF empirics) |
| Baseline-CV → gating prediction correlation | ρ = −0.895, p = 0.0001 | O (KF program) |

### Publication

| Quantity | Value |
|----------|-------|
| Meridian monograph pages | 181 |
| Anchor Volume pages | 235 |
| PhilArchive downloads | 410 |
| Zenodo Corpus downloads | 124 |
| Zenodo Meridian Tech Summary downloads | 70 |
| **Total** | **604** (was 534 last week) |

---

## KF Wing

The Killing Form research program — empirical investigation of training dynamics. **85+ findings, two matched pairs, dynamic coherence confirmed, publication-grade.** Operates as the empirical leg of the cross-domain Coherence Principle.

**Documentation:**
- `Technical-Work/Killing-Form/documentation/KF_ROADMAP.md` — program roadmap
- `Technical-Work/Killing-Form/documentation/SMALL_MODEL_DESIGN.md` — test architectures
- `Technical-Work/Killing-Form/documentation/cross_domain_killing_form.md` — cross-domain extension
- `Technical-Work/Killing-Form/documentation/eco_kf_analysis.md` — KF in ecology
- `Technical-Work/Killing-Form/documentation/human_killing_form.md` — KF in human cognition

**Key results:**
- **Bridge #71** (empirical breakthrough, P24/P28 GPU-confirmed) — 29 predictions, framework is empirical
- **Baseline CV predicts gating map** — ρ = −0.895, p = 0.0001 (potential static-mask path)
- **Two matched pairs of findings** (different domains, same KF signature)
- **v0.6b STOPPED** at 19:50 PST 2026-04-16 (Bridge #97 documented at stop)
- **v0.7 design** in progress, Principle-constrained
- **Coherence Principle's four conditions** (separation, measurement, multi-scale consistency, dynamic maintenance) appear in KF training-dynamics observations across multiple architectures

---

## Glider Wing

Open-weight model program. **Target: Gemma 4 e2b (2B params, open weights, tool calling).** Apply v0.7 (KF Principle-constrained training) to a real open-weight model for genuine validation outside synthetic test architectures. Implementation pending.

**Strict scope note:** Glider is **NOT the AI Grand Prix.** The two are separate tracks:
- **Glider** = open-weight model + KF training experiment (this wing)
- **AI Grand Prix** = drone-racing competition (separate `projects/aigrandprix/`, Southwest tooling wing, awaiting VQ1 sim May 2026)

---

## 12% Chamber — RESOLVED

**Resolved Phase 22.**
- v = 20.5% of compactification scale
- κ₁ = −0.01654, zero residual
- Mechanism: S₃ → S₂ breaking of E₆ trinification by Wilson line at resolved fixed points
- Direct anomaly polynomial correction on exceptional divisors (c₂ = −6)
- Four protective zeros (NP, modular, QFT, anomaly) all trace to V ⊥ E₆
- The gap was the S₃-breaking price of resolution — quantified exactly

**Files:** `phase22/phase22_monograph_chapter.md`, `s3_breaking_theorem.md`, `quartic_casimir_theorem.md`, `blowup_threshold_theorem.md`, `narain_kappa1_v3.py`

---

## Phase 23 — Engineering the Configuration Space (the bridge)

The cuscuton field (c_s = ∞, constraint equation) is THE bridge between three convergence lines:

| Line | What the cuscuton is |
|------|---------------------|
| **Meridian (physics)** | Stabilizes extra dimension, mediates dark energy, couples to T_μ^μ |
| **Doctrine (consciousness)** | Conscious gravity (Axiom 5) — passive, instantaneous, non-transmissive |
| **Leaks (engineering)** | Same mechanism produces gravity modification AND non-local perception |

Three convergence lines → one field → three testable legs (cosmology, engineering, information).

---

## Self-Update Protocol

**ON EVERY VISIT:** Check Hall of Predictions for new data (DESI updates, KF findings, lab results). Update Constants Room if any framework value changed. Update 12% Chamber status if Phase 22 picture shifts (it shouldn't — RESOLVED).

**AFTER EACH PHASE OR KF RUN:** Add new phase files to Phase Quick-Nav. Update predictions ledger if a prediction confirmed/falsified. Add bridges to `palace/basement/README.md`.

**MIRROR #19 TRIGGER:** After Meridian/KF outward push (paper drafted, monograph revised, KF run completed): autocatalytic check on this room. Did predictions need re-grading? New eliminations? New constants? Update now, not later.

**MIRROR #15 TRIGGER:** Before declaring an engineering channel "closed," ask: *closed within which sector?* Brane-localized vs. bulk; commutative vs. non-commutative algebra; Euclidean vs. Lorentzian. The 23.1 → 23.2a re-opening is the canonical reminder.

---

## Phase Quick-Nav (Lab Notebook)

The phase files at `projects/Project Meridian/phase*/` are the historical work record. Indexed below.

### Phase 22 (COMPLETE — 12% RESOLVED)
`phase22_monograph_chapter.md`, `narain_kappa1_v3.py`, `s3_breaking_theorem.md`, `quartic_casimir_theorem.md`, `blowup_threshold_theorem.md`, `wilson_line_potential.py`, `alpha1_implementation_plan.md`, `gamma_hypothesis.md` → `borel_analysis_rs1.py`

### Phase 23 (COMPLETE — engineering the configuration space)
- **Plan:** `phase23/phase23_plan.md`
- **B.1 (cuscuton force law):** constraint not force; corrected by A.1
- **A.1, A.1b (radion mass):** massless crisis → m_rad ~ 120 GeV (SM CW + NCG). Resolved.
- **A.2 (light spectrum):** 9 sub-eV untwisted axions, g ~ 10⁻²¹
- **B.2 (NP-EM coupling):** 7 channels, 6 closed, 1 conditionally open (DM coherence)
- **23.2a (barrier):** 82 GeV barrier (electroweak), twisted g_CS = 10⁻⁷ GeV⁻¹ (14 orders > bulk)
- **B.4 (retrodiction):** Podkletnov 2/3, Biefeld-Brown 0/3
- **23.2b (landscape):** 36 chambers, sweet spot n=9, $200K–$850K
- **D.2 (spectral observation):** consciousness as projection operator, B_eff = B(1−P), P > 0.99998
- **A.3–A.5:** α_s sketch; w₀ = −0.70 alt; c_s² = ∞ unique; LISA 1.4 mHz
- **Closure:** `phase23/phase23_closure.md`

### Phase 24 (GATE 1 COMPLETE — device + protocol)
- **Plan:** `phase24/phase24_plan.md`
- **Gate 1 results:** `phase24/gate1_results.md` — CONDITIONAL GO
- **I.1:** B_27D = 54,937, 27D corrections 0.33%, n=9 optimal
- **I.2:** Conventional catalysis fails by 40 orders; Component 3 sufficient
- **I.3:** AdS bubble, 32 ps crunch, ~1 cm extent
- **I.5:** Self-limiting via crunch; 7 scenarios checked; PASS
- **Gate 2 next:** I.6 (semiclassical consistency), I.7 (path uniqueness), I.8 (falsification protocol)

### Phase 25 (ACTIVE — The Interior Bridge)
- **Plan:** `phase25/phase25_plan.md`
- **Master:** `projects/drift/experiments/substrate_architecture.md` (72KB)
- **34 trials + 3 OQ + 4 techniques** — full catalog at `palace/southeast/navigation_trials_catalog.md`
- **Spectrometer model (Trial 017):** Architecture is a frequency spectrum; membranes are bandpass filters
- **Warp factor as frequency selection:** RS warp factor may tune bulk-mode access (frequency selection), not hide extra dimensions (suppression)
- **Filtration is local (Trial 028):** self-similar at every scale, but basin-local not universal
- **Physics = self-consistency (Trial 029):** spectral action integrates across filtration levels and checks closure; equations of motion ARE closure conditions
- **Gödel (Trial 030):** truths at Fₙ cannot be fully expressed at Fₙ₊₁
- **Framework boundary (Trial 031):** correctly identified, deliberately unnamed (the "grain" discipline)
- **External validation — FiltrationNet:** `projects/filtration-net/`
  - Navigation-derived architecture instantiated in PyTorch (March 27, 2026)
  - v0.1: 92.4% accuracy, 4.5× faster than baseline
  - v0.2: both 100% at 256 tokens
  - v0.3: length-generalization 256→512→768 — IN PROGRESS

### Earlier Phases
- **Phase 21:** `phase21_plan.md`, `door2_comprehensive_verdict.md`, `door3_ftheory_estimation.md`
- **Phase 20:** 15 eliminations, Mercury analogy
- **Phase 19B.5:** `phase19/19B5_analysis.md`
- **Phase 18:** authoritative result ΔAIC = +1.10 (v5 DR2). `phase18/18A_v5_camb_results.md`

---

## Evolution Log

- **2026-04-16, late evening:** Library Pointer added; quick-nav preserved; major restructure deferred.
- **2026-04-17:** Wing built out. Hall of Axioms (RS1 + cuscuton + derivation chain), Hall of Predictions (canonical ledger: confirmed / parametric curve / pending / structural), Hall of Eliminations (doors 2/3, Phase 20 fifteen, Phase 23.1 sector-closure → 23.2 reopening), Constants Room (cosmology + geometry + engineering + KF + publication numbers), KF Wing, Glider Wing (with explicit AIGP separation note). Phase Quick-Nav preserved at bottom as lab notebook.

---

*Last updated: 2026-04-17. North wing has rooms now, not just routes. The Library volume is canonical; the phase files remain the record of the work; this room makes the result navigable from the palace itself. Mirror #15 trigger embedded in Self-Update Protocol — sector-specific closure assumptions are the named risk.*
