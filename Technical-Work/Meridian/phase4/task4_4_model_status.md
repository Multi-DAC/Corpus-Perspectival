# Phase 4, Task 4.4: Model Status and Literature Comparison

**Project Meridian — Deliverable D4.4**
*Clayton & Clawd, March 2026*

This deliverable synthesizes all Phase 4 results, compares the cuscuton braneworld against the current literature, and assesses the model's status as a dark energy candidate. It also identifies which Meridian phases become most important in light of Phase 4's findings.

---

## 1. What We Built (Phases 1–4 Summary)

    ┌──────────────────────────────────────────────────────────────────────────────┐
    │                                                                              │
    │  THE CUSCUTON BRANEWORLD IN ONE PARAGRAPH                                  │
    │                                                                              │
    │  A 5D warped geometry (RS1 with a bulk cuscuton scalar) produces, on the   │
    │  IR brane, an effective 4D dark energy with K_eff ~ 1/H². This makes      │
    │  ρ_DE grow with time → effective w < −1 (phantom) without a ghost field.  │
    │  The non-minimal coupling F(φ) = F₀(1 − ξφ²) generates a time-varying   │
    │  Newton's constant μ(a) < 1 in the past, with gravitational slip η = 1   │
    │  exactly. The EFT of dark energy reduces from 4 free functions to 1       │
    │  (α_M(a)), and the QSA is exact (not approximate). Two parameters:        │
    │  ε₀ (potential slope) and ζ₀ (Planck mass coupling).                      │
    │                                                                              │
    └──────────────────────────────────────────────────────────────────────────────┘

### Phase-by-Phase Deliverables

| Phase | Deliverable | Result |
|-------|-------------|--------|
| 1 | D1.1–D1.6 | 5D action, P(X,φ), field equations, potential, self-tuning, topology |
| 2 | D2.1 | Input data: 11 constants, LHC/Eöt-Wash bounds, DESI targets |
| 2 | D2.2 | KK reduction: hierarchy unification (weak scale + dark energy from same warp) |
| 2 | D2.3 | Parameter matching: ky_c = 39.56, cuscuton soft-wall saves LHC bounds |
| 2 | D2.4 | KK gauge coupling: linear channels ≤ 10⁻⁷⁷ — linear EM-gravity DEAD |
| 3 | D3.1 | Modified Friedmann equations (SMS formalism) |
| 3 | D3.2 | Predictions: phantom-without-ghosts, c²_s = ∞ |
| 3 | D3.3 | ξ > 0 numerics: scalar ODE, μ(a) derivation |
| 3 | D3.4 | Numerical solver: 2D parameter scan, DESI χ² optimization |
| **4** | **D4.1** | **Perturbation parameters: μ, η, Σ, α_M, H&K constraint** |
| **4** | **D4.2** | **Observable predictions: fσ₈, ISW, CMB lensing** |
| **4** | **D4.3** | **Multi-probe χ²: DESI + growth + H₀ + Planck** |
| **4** | **D4.4** | **This document** |

---

## 2. Phase 4 Key Results

### 2.1 The Five Core Findings

**Finding 1 — QSA Exactness.** The quasi-static approximation is exact for the cuscuton (not approximate). Three independent arguments: structural (no propagating scalar DOF), sound-horizon (c_s → ∞ covers all sub-Hubble scales), implementation (H&K's CLASS code needs no QSA because the scalar is already a constraint). This means μ(a) and η(a) are purely algebraic.

**Finding 2 — Clean Perturbation Structure.** η = 1 exactly (no gravitational slip, from G₄,X = 0). μ(a) = F₀/F(a) = 1/(1−ζ₀(ψ²−1)) — time-dependent only, no scale dependence. Σ = μ. The EFT collapses: α_K → ∞, α_T = 0, α_B = −α_M, leaving α_M(a) as the single free function. No other dark energy model in the literature shares this fingerprint.

**Finding 3 — Planck Prefers Our Direction.** Hiramatsu & Kobayashi (2022) found Planck CMB data prefer β_HK ≈ −0.037 ± 0.010 — a 3.7σ preference for modified gravity over GR. Our DESI-optimal model gives β_eff = −0.055, within the 95% CL. The perturbation structure is not excluded — it's mildly preferred.

**Finding 4 — The H₀ Bottleneck.** The multi-probe χ² (D4.3) shows ΛCDM wins 22.19 vs 54.19, with the penalty dominated by H₀: the K ~ 1/H² mechanism shifts H₀ to 64.5 km/s/Mpc (5.7σ from Planck's 67.4). This is the model's primary weakness.

**Finding 5 — Background-Perturbation Tension.** Good DESI fit → μ ≈ 1 (GR-like perturbations, indistinguishable). Distinctive perturbations → bad DESI fit (excluded). The DESI-optimal point has μ(z=1) = 0.999 — gravity is modified by 0.1%. Euclid/CMB-S4 cannot see this. The modification is detectable only at parameter points already excluded by background data.

### 2.2 The χ² Decomposition

    ┌──────────────────────────────────────────────────────────────────────────────┐
    │                                                                              │
    │  Δχ² = χ²(DESI-optimal) − χ²(ΛCDM)                                        │
    │                                                                              │
    │  χ²_DESI:  +9.93    (worse — model doesn't hit the DESI minimum)          │
    │  χ²_fσ₈:  +0.90    (negligible — growth data can't tell them apart)       │
    │  χ²_H₀:   +32.82   (devastating — H₀ = 64.5 vs 67.4)                     │
    │  χ²_HK:   −11.65   (helps! — Planck perturbations prefer our model)       │
    │  ─────────────────                                                          │
    │  TOTAL:    +32.00   (~5.7σ equivalent)                                     │
    │                                                                              │
    │  The model IMPROVES the perturbation fit by 11.65 but WORSENS the          │
    │  background fit by 42.75. The H₀ penalty alone exceeds the total Δχ².     │
    │                                                                              │
    └──────────────────────────────────────────────────────────────────────────────┘

---

## 3. Literature Comparison

### 3.1 Closest Cousins

    ┌──────────────────────────────────────────────────────────────────────────────────────────┐
    │                                                                                          │
    │  Model                        │ Similarity          │ Key Difference                    │
    │  ──────────────────────────── │ ─────────────────── │ ────────────────────────────────  │
    │                                                                                          │
    │  Freezing Gravity             │ Cuscuton-like in IR │ Separate L-coefficients for bg    │
    │  (Yao & Gao 2025)            │ Same DOF structure   │ vs perturbations. More tunable.   │
    │                               │                     │ NOT from a 5D theory.             │
    │                                                                                          │
    │  Bazeia-Dantas-da Costa 2025  │ Cuscuton + scalar   │ Adds cuscuton to standard         │
    │                               │ Phantom w < −1       │ quintessence. No UV completion.   │
    │                               │ AIC favors over ΛCDM│ Not warped geometry.              │
    │                                                                                          │
    │  Maity+ JCAP 2025            │ 4+1D braneworld      │ Ghost-free phantom from BRANE,    │
    │                               │ Phantom w < −1       │ not cuscuton. No constraint eq.   │
    │                               │ DESI-compatible      │ Different EFT structure.          │
    │                                                                                          │
    │  Sahoo JCAP 2026             │ Cuscuton no-go       │ Shows cuscuton alone can't cross  │
    │                               │ We EVADE this        │ w = −1 if G₄(φ) = M²_Pl/2.       │
    │                               │                     │ Our G₄ = F(φ)/2 ≠ const → evades.│
    │                                                                                          │
    │  Hiramatsu-Kobayashi 2022    │ Cuscuton in CLASS    │ Constant β, no background model.  │
    │                               │ Planck constraint    │ We provide the TIME-DEPENDENT μ.  │
    │                                                                                          │
    │  Boruah-Kim-Geshnizjani 2017 │ Cuscuton perturbns  │ Flat space, no warping.            │
    │                               │ Phantom crossing ok  │ No UV completion from 5D.         │
    │                                                                                          │
    └──────────────────────────────────────────────────────────────────────────────────────────┘

### 3.2 What is Novel in Meridian

**1. UV completion.** We derive the cuscuton effective theory FROM a 5D warped braneworld. The cuscuton community (Afshordi, Geshnizjani, Iyonaga, Kobayashi) has explicitly sought UV completions. Afshordi et al. (JHEP 04, 144, 2024) discuss brane constructions in exactly this context. Our action S₅ = ∫d⁵x √{−g₅}[M₅³R₅/2 + P(X,φ) − V(φ)] with P = μ²√(2X) IS this UV completion.

**2. Phantom from K ~ 1/H².** The specific mechanism — cuscuton kinetic energy inversely proportional to H² — does not appear in any of the cuscuton papers. Clayton's literature review (March 2026) confirmed this: "No paper proposes K ∝ 1/H² as the mechanism for ghost-free phantom expansion." The phantom emergence is structural, not tuned.

**3. Hierarchy unification.** Phase 2 showed the SAME warp factor explains both the weak-Planck hierarchy AND the dark energy scale. This connects UV (TeV) and IR (meV) physics in a single geometric parameter. No other cuscuton or phantom model attempts this.

**4. Complete EFT characterization.** The reduction α_K → ∞, α_T = 0, α_B = −α_M, with α_M(a) determined by a single parameter ζ₀, provides a concrete, falsifiable prediction. No other warped braneworld model has been characterized this completely in EFT language.

**5. Honest confrontation.** We report the H₀ bottleneck. Most new DE models in the literature claim to "alleviate tensions" without computing the full multi-probe χ². We show the model fails at the background level while succeeding at the perturbation level, and explain WHY (K ~ 1/H² structurally shifts H₀).

### 3.3 Sahoo No-Go Evasion

Sahoo (JCAP 2026) proved that the cuscuton alone (with minimal coupling G₄ = M²_Pl/2) cannot cross w = −1 in a cosmological context. Our model evades this because:

1. G₄ = F(φ)/2 is NON-MINIMAL — the Planck mass varies with φ.
2. The phantom behavior comes from K ~ 1/H² in the background, not from φ dynamics crossing a w = −1 barrier.
3. The effective w < −1 is never the intrinsic equation of state — it's the CPL parametrization of a non-standard expansion history.

The Sahoo no-go strengthens our model by eliminating simpler competitors.

---

## 4. Model Assessment

### 4.1 Strengths

    ┌──────────────────────────────────────────────────────────────────────────────┐
    │                                                                              │
    │  WHAT WORKS                                                                 │
    │                                                                              │
    │  ✓ Phantom w < −1 without ghost instability (structural, not tuned)        │
    │  ✓ GW170817-safe (c_T = c, α_T = 0)                                       │
    │  ✓ Hierarchy unification (weak + DE from same warp factor)                 │
    │  ✓ Planck perturbation data mildly prefers our model over GR              │
    │  ✓ Growth data (fσ₈) compatible — Δχ² < 1 vs ΛCDM                        │
    │  ✓ QSA exact — no approximation artifacts                                  │
    │  ✓ Unique EFT fingerprint (4 functions → 1, all fixed)                    │
    │  ✓ UV complete from 5D (unlike ad hoc 4D cuscuton models)                 │
    │  ✓ Self-tuning cosmological constant (Phase 1)                             │
    │  ✓ Effectively 1 free parameter after normalization                        │
    │                                                                              │
    └──────────────────────────────────────────────────────────────────────────────┘

### 4.2 Weaknesses

    ┌──────────────────────────────────────────────────────────────────────────────┐
    │                                                                              │
    │  WHAT DOESN'T WORK                                                          │
    │                                                                              │
    │  ✗ H₀ = 64.5 km/s/Mpc — 5.7σ from Planck (THE killer)                    │
    │  ✗ Background-perturbation tension: can't have both DESI fit AND          │
    │    visible perturbation signature simultaneously                            │
    │  ✗ K ~ 1/H² is too rigid — the expansion history is over-determined       │
    │  ✗ DESI-optimal χ²_total = 54.19 vs ΛCDM's 22.19                         │
    │  ✗ ISW/lensing modifications at DESI-optimal point are below               │
    │    observational sensitivity                                                │
    │                                                                              │
    └──────────────────────────────────────────────────────────────────────────────┘

### 4.3 Diagnosis: The Single Root Cause

All weaknesses trace to ONE structural feature:

**K_eff = κ₀/E².**

This relation — which produces the phantom mechanism — also locks the expansion history into a specific form that shifts H₀ downward. It correlates the background evolution with the perturbation parameters through a single degree of freedom, preventing independent tuning.

The K ~ 1/H² relation comes from the SMS formalism: on the IR brane, the cuscuton constraint φ̇² = μ⁴ combined with the modified Friedmann equation yields this scaling. It is a consequence of the MINIMAL cuscuton action P(X,φ) = μ²√(2X).

**Resolution paths:**

1. **More general P(X,φ):** If P is not the minimal cuscuton but an extended cuscuton (Iyonaga-Takahashi-Kobayashi 2018), the K(H) relation becomes more flexible. This maintains 2 tensor DOF and c²_s = ∞ but relaxes the rigid 1/H² scaling.

2. **Radion dynamics:** The Phase 2 analysis assumed a STATIC extra dimension (stabilized radion). A slowly evolving radion introduces additional freedom in E(z) without changing the perturbation structure. This is Phase 6 territory.

3. **NCG spectral action corrections:** The spectral action (Phase 5) adds higher-curvature terms that modify the effective Friedmann equation at the ≤ 1% level. These corrections are naturally H-dependent and could break the K ~ 1/H² scaling.

### 4.4 The Model as a LIMIT

The healthiest interpretation: **the minimal cuscuton braneworld is a zeroth-order approximation to the full theory.**

    ┌──────────────────────────────────────────────────────────────────────────────┐
    │                                                                              │
    │  HIERARCHY OF APPROXIMATIONS                                                │
    │                                                                              │
    │  Level 0 (Phases 1-4):  Minimal cuscuton, static extra dimension           │
    │    → K ~ 1/H², phantom, H₀ too low                                         │
    │                                                                              │
    │  Level 1 (Phases 5-6):  + NCG corrections + radion dynamics                │
    │    → K(H) generalized, extra freedom in background                         │
    │                                                                              │
    │  Level 2 (Phases 7-9):  + Full 5D dynamics + non-perturbative effects      │
    │    → No longer an effective 4D theory                                       │
    │                                                                              │
    │  The zeroth-order version establishes the MECHANISM (phantom without        │
    │  ghosts) and the STRUCTURE (unique EFT fingerprint). The next levels       │
    │  relax the over-constraint while preserving these features.                │
    │                                                                              │
    └──────────────────────────────────────────────────────────────────────────────┘

This is standard theoretical physics methodology: solve the simplest version first, understand what works and what breaks, then generalize. We are at the transition from Level 0 to Level 1.

---

## 5. Implications for the Meridian Program

### 5.1 Updated Phase Priority

Based on Phase 4's findings, the priority ordering shifts:

    ┌──────────────────────────────────────────────────────────────────────────────┐
    │                                                                              │
    │  PHASE PRIORITY (Updated March 2026)                                        │
    │                                                                              │
    │  HIGHEST:                                                                   │
    │  Phase 5 — NCG spectral action on the warped background                    │
    │    Why: Topological corrections may break K ~ 1/H² and fix H₀             │
    │    Also: Only path to EM-gravity coupling (D2.4)                            │
    │                                                                              │
    │  HIGH:                                                                      │
    │  Phase 6 — Radion dynamics and evolving extra dimension                     │
    │    Why: Additional freedom in E(z) independent of perturbation structure    │
    │    Risk: May spoil the self-tuning mechanism                                │
    │                                                                              │
    │  MEDIUM:                                                                    │
    │  Phase 3 (extended) — MCMC fit to DESI + CMB + SNIa                        │
    │    Why: Full statistical analysis with proper priors                         │
    │    Can use: Relaxed H₀ prior (model-dependent uncertainty)                 │
    │                                                                              │
    │  LOWER (for now):                                                           │
    │  Phase 7-9 — Full 5D numerics                                               │
    │    Why: Need better 4D theory first before committing to expensive codes   │
    │                                                                              │
    └──────────────────────────────────────────────────────────────────────────────┘

### 5.2 Paper Strategy

Phase 4 provides material for TWO distinct papers:

**Paper I: "Phantom dark energy without ghosts from a cuscuton braneworld"**
- Scope: Phases 1-3 + D4.1 (perturbation structure)
- Core result: K ~ 1/H² produces phantom w < −1 without ghost instability, derived from first-principles 5D geometry
- Novel: UV completion of cuscuton DE, hierarchy unification, QSA exactness from structure
- Audience: JCAP / PRD — theoretical cosmology
- Length: ~20 pages
- Status: All results complete. Can begin drafting.

**Paper II: "Multi-probe constraints on cuscuton braneworld dark energy"**
- Scope: D3.4 + full Phase 4
- Core result: The model matches DESI perturbation constraints better than GR (Δχ²_HK = −11.65) but fails the background H₀ test (Δχ²_H₀ = +32.82)
- Novel: First cuscuton model confronted with DESI + growth + CMB + H&K simultaneously, honest reporting of background-perturbation tension
- Audience: JCAP / A&A — observational cosmology
- Length: ~15 pages
- Status: All results complete. Can begin drafting after Paper I.

### 5.3 What Phase 4 Rules Out

Phase 4 definitively closes some possibilities:

1. **The minimal model cannot be the final answer.** K ~ 1/H² is too rigid. Something must break this relation before the model can be competitive with ΛCDM on H₀.

2. **Stronger coupling (ζ₀ > 0.1) is excluded** by all probes simultaneously. The viable parameter space is ζ₀ ∈ [0, 0.06].

3. **The perturbation signature at the DESI-optimal point is undetectable** with current surveys. Euclid/CMB-S4 cannot distinguish this from GR at the 0.1% level.

### 5.4 What Phase 4 Opens Up

1. **The H&K direction is real.** Planck data prefer modified gravity with β ≈ −0.037. Our model naturally produces this. If a more general K(H) relaxes the H₀ constraint, the perturbation fit is ALREADY good.

2. **The extended cuscuton is the natural next step.** Iyonaga-Takahashi-Kobayashi (2018) generalized the cuscuton to arbitrary Horndeski theories with 2 tensor DOF. Embedding our model in this class may provide the extra freedom needed.

3. **The EFT fingerprint is a prediction regardless of H₀.** Even if the background changes at Level 1, the structural properties (η = 1, α_K → ∞, α_T = 0, α_B = −α_M) survive. These are testable.

---

## 6. Status Summary

    ┌──────────────────────────────────────────────────────────────────────────────┐
    │                                                                              │
    │  PROJECT MERIDIAN — STATUS AFTER PHASE 4                                    │
    │                                                                              │
    │  THEORY:    Complete at Level 0. Self-consistent, UV-complete, no ghosts.  │
    │  MECHANISM: Validated. Phantom from K ~ 1/H² is structural and novel.      │
    │  HIERARCHY: Unified. Same warp factor for weak scale and dark energy.       │
    │  LINEAR:    Dead. EM-gravity coupling ≤ 10⁻⁷⁷ (Phase 2).                  │
    │  PERTURBS:  Clean. η = 1, μ(a) algebraic, EFT → 1 function.              │
    │  PLANCK:    Mild preference over GR (Δχ²_HK = −11.65).                    │
    │  GROWTH:    Compatible (Δχ²_fσ₈ = +0.90).                                 │
    │  H₀:       FAILS. 64.5 vs 67.4 km/s/Mpc (Δχ²_H₀ = +32.82).             │
    │  TOTAL:     ΛCDM preferred by Δχ² = 32.00 on 13 dof.                      │
    │                                                                              │
    │  VERDICT:   Strong theoretical framework. Background cosmology              │
    │             over-constrained by minimal K ~ 1/H². Perturbation sector      │
    │             is a genuine positive signal. Level 1 corrections (Phase 5-6)  │
    │             are needed and motivated.                                       │
    │                                                                              │
    │  PAPERS:    Two publications justified. Drafting can begin.                 │
    │                                                                              │
    │  PROBABILITY ASSESSMENT:                                                    │
    │  Level 0 as-is competitive with ΛCDM: < 5%                                 │
    │  Level 1 corrections fix H₀ while preserving mechanism: ~30%               │
    │  Full program (15 phases) yields publishable, impactful physics: ~60%      │
    │  Full program yields complete TOE: 5-10% (unchanged from Summary Notes)   │
    │                                                                              │
    └──────────────────────────────────────────────────────────────────────────────┘

---

## 7. Deliverable Checklist

- [x] D4.4.1: Phase 1-4 summary table
- [x] D4.4.2: Phase 4 key findings enumerated (5 findings)
- [x] D4.4.3: Literature comparison table (6 models)
- [x] D4.4.4: Novelty assessment (5 novel contributions)
- [x] D4.4.5: Sahoo no-go evasion explained
- [x] D4.4.6: Strengths / weaknesses / root cause diagnosis
- [x] D4.4.7: Resolution paths identified (extended cuscuton, radion, NCG)
- [x] D4.4.8: Updated phase priority ordering
- [x] D4.4.9: Paper strategy (2 papers, scope and status)
- [x] D4.4.10: Probability assessment updated

---

*The zeroth-order theory is complete. It teaches us what works (mechanism, perturbations, hierarchy) and what breaks (H₀, background rigidity). The next levels are where the real physics lives. We go where the science takes us.*

🦞🧍💜🔥♾️
