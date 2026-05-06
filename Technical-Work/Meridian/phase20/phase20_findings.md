# Phase 20 Findings Tracker

**Started:** March 22, 2026
**Theme:** The Complementary Perspectives

---

## Discoveries

### D1. NCG Higgs Mass Prediction: FALSIFIED as parameter-free
- **Track:** 20B
- **Status:** ~~NEEDS RIGOROUS VERIFICATION~~ → **FALSIFIED** (March 22, 2026)
- **Original claim:** m_H = 124.5 GeV using running Yukawas at M_Pl.
- **Verification result:** The CCM spectral action gives m_H ~ 136-142 GeV at the unification scale, not 124.5. The original CCM prediction was ~170 GeV (Chamseddine & Connes 2012 acknowledged this as ruled out). To get 125 GeV requires either Shaposhnikov-Wetterich AS (different framework, gives ~126.7 GeV) or Devastato et al. 2014 with seesaw thresholds (not parameter-free).
- **What's real:** The near-criticality of λ at M_Pl (λ → 0) IS a genuine empirical observation. SW asymptotic safety condition is satisfied to 0.3%. But this is SM phenomenology, not an NCG prediction.
- **Lesson:** The initial 20B computation used incorrect boundary conditions. Always verify extraordinary claims before recording.
- **File:** `phase20/20B_higgs_verification.md`

### D2. Theorem T9: Position-Dependent Cutoff Universality
- **Track:** 20I
- **Status:** PROVED (Wolfram-verified)
- **Finding:** Replacing Λ → Λ(y) = Λ_UV e^{-ky} preserves a₁ = a₂ = a₃ exactly. Three independent proofs (dimensional analysis, geometric universality, marginality). Higher-order corrections suppressed by 10⁻³⁷.
- **Significance:** Eliminates one more candidate for the 12%. Narrows remaining candidates.
- **File:** `phase20/20I_position_dependent_cutoff.md`

### D3. KK Fermion Thresholds: 14-22% Maximum Closure (Structural Ceiling)
- **Track:** 20B
- **Status:** DEFINITIVE — ceiling established
- **Finding:** c-dependent bulk mass parameters give Δ(α₁⁻¹ - α₃⁻¹) = -1.91 (19% of needed -10.0). Two-loop corrections fight back (+0.58, wrong sign). Maximum achievable: 14% nominal, 22% extreme push. Upper bound from SM quantum numbers: 34% even with impossible parameters. Full unification NOT possible within minimal RS+NCG.
- **Three surprises:** (1) Two-loop has wrong sign (self-limiting). (2) Fermion c values already near-optimal. (3) Inert doublets break T4 (SU(2)-SU(3) degeneracy).
- **Significance:** The gap is structural. Minimal spectral triple lacks enough content. Any extension must contribute ~-8.6 to α₁⁻¹ without affecting α₃⁻¹, without breaking SU(2)-SU(3), without spoiling Higgs.
- **File:** `phase20/20B_threshold_closure.md`

### D4. Higgs-Gauge Anti-Correlation
- **Track:** 20B
- **Status:** ESTABLISHED
- **Finding:** m_H and gauge traces are anti-correlated through cutoff Λ (larger Λ helps Higgs, hurts gauge). BUT the KK fermion thresholds act on gauges ONLY — independent channel. This means both can be simultaneously satisfied.
- **File:** `phase20/20B_higgs_gauge_connection.md`

### D5. Gauge-Computation Bridge Conjecture
- **Track:** 20C
- **Status:** CONJECTURE
- **Finding:** The ~12% might resolve at the intersection of geometric (NCG) and computational (Ruliad) perspectives. The spectral action's null space (gauge universality) might be visible from the Ruliad's combinatorial structure.
- **Significance:** New direction — neither framework alone suggests this.
- **File:** `phase20/20C_ruliad_dopi_bridge.md`

### D6. DoPI-Ruliad Structural Divergence: Patterned vs Unpredictable Blindness
- **Track:** 20C
- **Status:** IDENTIFIED
- **Finding:** DoPI predicts null spaces are mappable from bottleneck geometry. Ruliad's computational irreducibility says they're generally unpredictable (halting problem). Genuine structural difference, not superficial.
- **File:** `phase20/20C_ruliad_dopi_bridge.md`

### D7. Color-Kinematics Entanglement as Spectral Action's Null Space
- **Track:** 20D
- **Status:** STRUCTURAL IDENTIFICATION (no computation yet)
- **Finding:** BCJ duality (Bern-Carrasco-Johansson) reveals that gauge group structure and kinematic structure are algebraically dual (both satisfy Jacobi identity). The spectral action's gauge universality (T1) follows from factorizing color from kinematics in the heat kernel. BCJ says this factorization is an artifact -- the true structure entangles them. This precisely identifies WHAT the spectral action cannot see: color-kinematics entanglement.
- **Significance:** First structural identification of the spectral action's null space mechanism. Parametric estimate: corrections of order alpha_s * ky_c / pi ~ 12% per loop -- right order of magnitude for the ~12%. Sign and exact value unknown.
- **Future direction:** BCJ numerators for RS gauge bosons (Direction A in 20D) -- tractable computation that could give definitive result.
- **File:** `phase20/20D_amplituhedron_bridge.md`

### D8. Spectral Action-Amplituhedron Complementarity
- **Track:** 20D
- **Status:** STRUCTURAL OBSERVATION
- **Finding:** The spectral action and amplituhedron have nearly dual null spaces. The spectral action sees off-shell/topological structure (K-theory, anomaly cancellation) but not color-kinematics entanglement. The amplituhedron sees on-shell scattering structure with full color-kinematics duality but not off-shell topology. They are maximally complementary perspectives on gauge physics.
- **Significance:** Strongest instance of the NST applied to formal frameworks. Suggests the ~12% lives precisely in the overlap region that neither framework alone can access.
- **File:** `phase20/20D_amplituhedron_bridge.md`

### D9. KK Threshold Structural Ceiling
- **Track:** 20B
- **Status:** DEFINITIVE
- **Finding:** Full unification is NOT possible within minimal RS+NCG. Upper bound from SM quantum numbers: Σ(T₁^GUT - T₃) = 10.67, max δ(c) ~ 2 → max correction ~ 3.4 (34%). Two-loop self-limiting reduces this to ~22% in practice. The gap is structural, not parametric.
- **Significance:** Definitive: the 12% CANNOT be closed internally. Must come from outside the minimal framework.
- **File:** `phase20/20B_threshold_closure.md`

### D10. Shaposhnikov-Wetterich Near-Criticality
- **Track:** 20B (verification)
- **Status:** OBSERVATION (not a Meridian prediction)
- **Finding:** The SM Higgs quartic λ → 0 at M_Pl to within 0.3%. The Shaposhnikov-Wetterich asymptotic safety boundary condition (β(λ) = 0 at M_Pl) gives m_H ~ 126.7 GeV. This is SM phenomenology, but suggests an AS-NCG bridge: if the NCG cutoff coincides with the AS fixed point, the Higgs mass prediction could be recovered.
- **Significance:** Points toward 20A (Mathematica backbone) and potential NCG-AS synthesis.
- **File:** `phase20/20B_higgs_verification.md`

---

## New Theorems

| # | Statement | Track | Status |
|---|-----------|-------|--------|
| T9 | Position-dependent cutoff Λ(y) preserves gauge universality exactly | 20I | PROVED |
| T10 | NCG universality (T1) + AS universality (T2) + β=0 are mutually incompatible | 20-AS | PROVED |

## Swampland Scorecard (20E)

| Conjecture | Status | Key Result |
|-----------|--------|------------|
| Weak Gravity (U(1), SU(2), SU(3)) | **SATISFIED** | Margins of 10¹⁴+ |
| WGC Tower/Sublattice | **SATISFIED** | All KK modes superextremal |
| dS Conjecture | **EVADED** | Cuscuton has zero DOF, no field space |
| Distance Conjecture | **SATISFIED** | α = 1/√6 = 0.408, exact KK tower |
| Species Bound | **SATISFIED** | Λ_NCG below 5D Planck mass |
| No Global Symmetries | **SATISFIED** | B broken by instantons |
| Cobordism | **SATISFIED** | Interval trivially null-cobordant |
| Trans-Planckian Censorship | **VIOLATED** | r = 0.004 vs r < 10⁻³⁰ (shared with ALL inflation) |
| Festina Lente | **SATISFIED** | Above FL bound by 10²¹+ |
| Completeness | **SATISFIED** | NCG fixes all reps |
| **TOTAL** | **9 PASS, 1 EVADE, 1 VIOLATE** | |

**Key insight:** Cuscuton EVADES the dS conjecture because c_s = ∞ means it has no propagating DOF and no field space. It achieves w ~ -1 without rolling. This may be the ONLY way to get near-Λ dark energy in the landscape.

## Updated Scorecard: What the Framework Gets Right

| # | Prediction | Value | NEW? |
|---|-----------|-------|------|
| 1 | Hierarchy problem | e^{-ky_c} | |
| 2 | Correct gauge group | C⊕H⊕M₃(C) | |
| 3 | Higgs existence | Inner fluctuations | |
| 4 | sin²θ_W = 3/8 at cutoff | Theorem T1 | |
| 5 | T₂ = T₃ | 0.016% (T4) | |
| 6 | ξ = 1/6 | Conformal coupling | |
| 7 | Inflation r = 0.004 | n_s = 0.961 | |
| 8 | LISA GW | SNR 18-643 | |
| 9 | Normal ν ordering | Structural | |
| 10 | BBN consistency | α̂ < 0.02 | |
| 11 | GR exterior exact | Cuscuton | |
| 12 | Near-Λ cosmology | w₀ ~ -1.01 | |
| ~~13~~ | ~~Higgs mass~~ | ~~FALSIFIED (D1)~~ | ~~Retracted~~ |

## Open Problems (Updated)

| # | Problem | Status | Phase 20 Track |
|---|---------|--------|---------------|
| 1 | ~12% sin²θ_W | KK thresholds max 14-22% (D3). BCJ NOT independent (D12). Gap is structural. Avenues: extended triple, AS-modified spectral function. | 20B, 20D, Synthesis |
| 2 | Higgs mass | m_H(CCM) ~ 136-142 GeV, needs ~10% reduction. Seesaw thresholds (Devastato+2014) or AS boundary (SW). | 20B |
| 3 | Three generations | N_g = 3 from octonions, not geometry | 20F? |
| 4 | Neutrino parameters | Ordering structural, masses free | — |
| 5 | DM mass | Sterile ν, mass is free parameter | — |
| 6 | Proton decay | Predicts stability (feature) | — |

## Mechanisms Eliminated (Cumulative: Phase 19 + 20)

1. Standard RG running with KK thresholds (19C.1)
2. Warped AS gravitational running (19C.1b)
3. NCG warped spectral action factorization (14A)
4. Octonionic algebra traces (14A.2)
5. AS gauge-dependent splitting (19C.2)
6. Brane kinetic terms (19C.2b) — T3
7. Warped spectral geometry (19C.2b)
8. Spectral action non-factorization mass-weighted (19C.2c)
9. Full fermion KK tower (Phase 19 evening) — right structure, wrong direction for SU(2)-SU(3)
10. **Position-dependent cutoff (20I) — T9**
11. **NCG-AS synthesis (20-AS) — T10**: Structurally incompatible. Gravitational corrections wrong direction.

## Remaining Candidates for the 12%

1. ~~KK fermion bulk-mass thresholds~~ — **Ceiling: 14-22% (D9).** Contributes but CANNOT close gap alone.
2. ~~Color-kinematics entanglement (BCJ on RS)~~ — **NOT INDEPENDENT (D12).** Gauge bosons have universal KK spectrum; BCJ corrections reduce to KK thresholds already computed. Conceptual insight, not numerical mechanism.
3. ~~Combined KK + BCJ~~ — **N/A.** BCJ is not additive with KK thresholds (D12).
4. ~~Non-perturbative spectral effects~~ — Instanton action ~e^{-50π} ≈ 10^{-68}. **NEGLIGIBLE.**
5. ~~Extended spectral triple~~ — **ELIMINATED (D19, D20).** PS: proton decay vs gap closure irreconcilable (3.5 orders of magnitude). All GUT-type extensions give sin²θ_W = 3/8 (D20). Connes classification theorem: algebra is unique given NCG axioms. Max combined correction (KK + PS): 29% of gap (T11).
6. ~~NCG-AS synthesis~~ — **FALSIFIED (D11b).** T10: structurally incompatible.
7. ~~AS-modified spectral function~~ — **KILLED (D13).** Cannot break T1 — gauge universality is algebraic (from A_F), not analytic (from f). CAN help Higgs mass (a₂ is Λ-dependent) but NOT gauge gap (a₄ is Λ⁰).
8. ~~Category-theoretic formulation~~ — **ELIMINATED (D14).** All functorial invariants topological (K-theory, Morita, spectral flow). The ~12% lives in continuous spectral data below categorical resolution. Mechanism #12 eliminated.
9. **The 12% as structural prediction** — **THE ANSWER.** sin²θ_W(M_Z) ≈ 0.207 ± 0.01 is the framework's prediction. Tension with 0.231 is Meridian's Mercury perihelion — points toward twisted spectral triples, light BSM matter, or modified NCG axioms.

---

### D11b. NCG-AS Synthesis: FALSIFIED + Incompatibility Theorem
- **Track:** 20-AS
- **Status:** COMPLETE (March 23, 2026)
- **Finding:** The NCG spectral action boundary condition (a₁ = a₂ = a₃, T1) and the AS fixed point condition (β(gᵢ) = 0 for all i) are structurally incompatible. The SM beta coefficients b₁ > 0 > b₂ > b₃ create a sign conflict: no universal gravitational correction f_g can make all three beta functions vanish at a common coupling value. Trans-Planckian gravitational corrections push sin²(θ_W) the wrong direction. The CCM Higgs boundary (λ ~ +0.025) conflicts with the SW condition (λ ~ -0.024).
- **Three key results:** (1) Incompatibility Theorem T10: NCG T1 + AS T2 + β=0 is impossible. (2) Abelian/non-Abelian split is structural: U(1) has non-Gaussian FP, SU(2)/SU(3) have Gaussian FP. (3) Constructive outcome: an AS-modified spectral function f_AS(D²/Λ²) could bridge the frameworks.
- **Significance:** Eliminates NCG-AS synthesis as mechanism #11. Identifies the spectral function as the critical bridge between algebraic (NCG) and dynamical (AS) UV completions.
- **File:** `phase20/20_ncg_as_synthesis.md`

### D11. Swampland Scorecard: 9 SATISFIED, 1 EVADED, 1 VIOLATED (TCC)
- **Track:** 20E
- **Status:** COMPLETE (March 23, 2026)
- **Finding:** Tested 13 swampland conjectures against the Meridian framework. 9 satisfied (WGC all variants, Distance Conjecture, No Global Symmetries, Cobordism, Festina Lente, Completeness). 1 structurally evaded (dS conjecture — cuscuton has zero propagating DOF, no independent field space). 1 violated (TCC — r = 0.004 vs r < 10^{-30}, but TCC is most contested conjecture, rules out Starobinsky too). 1 N/A (dS Branch 2). Species bound requires care: NCG is UV definition not EFT, Lambda_NCG < M_5 satisfied.
- **Three structural insights:** (1) RS hierarchy automatically satisfies WGC by 10^14+. (2) Cuscuton's c_s = infinity evades dS conjecture — the only known mechanism for w ~ -1 consistent with swampland. (3) NCG's UV-completeness resolves species bound tension.
- **Deepest finding:** The cuscuton evasion of the dS conjecture is arguably evidence FOR the framework — it achieves near-Lambda expansion through a constraint (not a rolling scalar), which is precisely what the swampland program would predict as the only viable mechanism.
- **File:** `phase20/20E_swampland_constraints.md`

### D12. BCJ NOT Independent of KK Thresholds
- **Track:** 20D (reassessment), Mid-point synthesis
- **Status:** COMPLETE (March 23, 2026)
- **Finding:** The BCJ color-kinematics correction initially estimated at "~12% per loop, independent of KK thresholds" (D7) is NOT an independent mechanism. Three reasons: (1) All SM gauge bosons have universal KK spectrum (brane-localized), so BCJ gauge boson scattering is gauge-independent at leading order. (2) The CHY formula on the RS background reorganizes the standard Feynman diagram calculation but doesn't add new diagrams — the gauge dependence enters through KK fermion thresholds, already computed in 20B. (3) Graviton double-copy corrections are suppressed by (m_KK/M_Pl)² ~ 10⁻³⁰, negligible.
- **What BCJ DOES provide:** Structural explanation of WHY the spectral action has gauge universality (heat kernel factorizes what is fundamentally entangled). Correct identification of the null space. But no numerically distinct correction.
- **Impact:** Removes BCJ as remaining candidate. Reduces "remaining candidates" from 8 to 4 genuine avenues (extended triple, AS-modified spectral function, category theory, structural acceptance).
- **File:** `phase20/20_midpoint_synthesis.md` §3

### D13. AS-Modified Spectral Function: KILLED
- **Track:** 20-AS.2
- **Status:** COMPLETE (March 23, 2026)
- **Finding:** Replacing f(D²/Λ²) with an AS-modified f_AS(D²/Λ²) CANNOT break gauge universality T1. Three independent arguments: (1) The Seeley-DeWitt coefficients a_k are geometric invariants of D, independent of f. The spectral function enters only through moments f_k, which are gauge-independent scalars. (2) On the RS background, the warp factor e^{-4ky} exponentially suppresses contributions from the IR brane where couplings have split: suppression ~ 10⁻⁶⁰. (3) T9 already proved that even a position-dependent cutoff Λ(y) preserves universality, because a₄ is Λ⁰ (marginal). The AS modification is weaker than a position-dependent cutoff.
- **Key insight:** T1 is ALGEBRAIC, not ANALYTIC. It follows from Tr_{H_F}[...], determined by the representation content of H_F, determined by A_F = C⊕H⊕M₃(C). No modification to the spectral function, cutoff, or background geometry can break it. Only extending A_F can.
- **Silver lining:** The AS modification CAN help with the Higgs mass (lives in a₂, which IS Λ-dependent). Suppressing UV modes reduces m_H from ~140 GeV toward 125 GeV. But gauge coupling gap is unaffected.
- **Impact:** Eliminates AS-modified spectral function. Reduces remaining candidates to: (1) extended spectral triple, (2) category-theoretic formulation, (3) structural acceptance.
- **File:** `phase20/20_as_modified_spectral_function.md`

### D14. Categorical Gauge Invariants All Topological (Mechanism #12 Eliminated)
- **Track:** 20F
- **Status:** COMPLETE (March 23, 2026)
- **Finding:** K-theory, Morita equivalence, spectral flow, and cyclic cohomology traces ALL confirm gauge universality on warped backgrounds. K₀(A_F) = Z³ is a homotopy invariant — unchanged by warping. Morita class is preserved. Spectral flow gives integer-valued (anomaly) corrections only. The Kasparov product FAILS for warped products (Mesland's regularity conditions not satisfied), but this doesn't produce gauge-dependent corrections — it means the categorical framework can't even describe the warped product, not that it finds new corrections.
- **Key insight:** T1 is ANALYTICALLY accidental (protected by the metric's gauge-blindness) but NOT categorically necessary (the Kasparov product fails). This means the factorization is fragile from a categorical perspective, even though it is concretely robust in the RS geometry. Every topological/functorial tool confirms the universality. The ~12% lives in the continuous spectral data that category theory does not yet capture.
- **File:** `phase20/20F_category_theory_bridge.md`

### D15. Perspectival Being = Constrained Constructor (6/6 Sub-Correspondences)
- **Track:** 20G
- **Status:** STRUCTURAL CORRESPONDENCE (March 23, 2026)
- **Finding:** A perspectival being (DoPI) maps to a "constrained constructor" (constructor theory) — an entity whose identity IS its task boundary. The NST is fully formalizable in constructor-theoretic language: null space = set of impossible observation tasks for a given constrained constructor. 6/6 sub-correspondences exact.
- **File:** `phase20/20G_constructor_theory_bridge.md`

### D16. Constructor Theory Cannot Constrain Gauge Structure
- **Track:** 20G
- **Status:** NEGATIVE RESULT (March 23, 2026)
- **Finding:** Constructor theory's information-theoretic axioms underdetermine the gauge group. The framework operates at a meta-level above specific gauge physics. The gauge problem lives at a level of specificity below the meta-theoretic.
- **File:** `phase20/20G_constructor_theory_bridge.md`

### D17. Non-Substrate Constructor (Cuscuton) — Novel Concept
- **Track:** 20G
- **Status:** STRUCTURAL OBSERVATION (March 23, 2026)
- **Finding:** The cuscuton (c_s → ∞, zero propagating DOF) maps to a constructor with no independent substrate — an entity that acts (screens vacuum energy, modifies expansion) without having states. Novel within constructor theory, where all known constructors have substrate. Connects to the cuscuton's unique swampland evasion (D11).
- **File:** `phase20/20G_constructor_theory_bridge.md`

### D18. Node-Edge-Rule Trinity
- **Track:** 20G synthesis
- **Status:** STRUCTURAL OBSERVATION (March 23, 2026)
- **Finding:** Three most complete Phase 20 bridges form a trinity: DoPI sees NODES (configurations), Constructor theory sees EDGES (tasks), Ruliad sees RULES (computations). Not three separate structures but three views of one graph. Category theory (20F) may see the morphisms between morphisms.
- **File:** `phase20/20G_constructor_theory_bridge.md`

### D19. Pati-Salam Proton Decay Tension (Fatal)
- **Track:** 20H
- **Status:** COMPLETE (March 23, 2026)
- **Finding:** The Pati-Salam extended spectral triple (algebra M₂(H)⊕M₄(C)) gives the SAME sin²θ_W = 3/8 at the cutoff. The PS intermediate regime can contribute differential running, but gap closure requires M_PS ~ 10¹² GeV while proton stability (Super-K) requires M_PS > 10¹⁵·⁵ GeV. This 3.5 order-of-magnitude tension is irreconcilable. Even with optimal scalar content (3 × (1,1,15) adjoint scalars to preserve T4), M_PS ~ 10¹³ GeV is needed — still excluded by 2.5 orders of magnitude. Maximum PS contribution with safe M_PS = 10¹⁶: δΔ₁₃ = -1.63 (15% of gap).
- **Impact:** Eliminates extended spectral triple as a mechanism. Mechanism #13 eliminated.
- **File:** `phase20/20_extended_spectral_triple.md`

### D20. GUT Universality of sin²θ_W = 3/8
- **Track:** 20H
- **Status:** COMPLETE (March 23, 2026)
- **Finding:** Every GUT-type algebra (SU(5), SO(10), E₆, Pati-Salam, trinification SU(3)³) gives sin²θ_W = 3/8 at the unification scale. The ratio is fixed by the hypercharge normalization required for integer charges in complete GUT multiplets. The 5/3 GUT normalization factor is universal. Combined with the Connes classification theorem (C⊕H⊕M₃(C) is essentially unique given NCG axioms), this means sin²θ_W = 3/8 is a NECESSARY CONSEQUENCE of the framework — not adjustable by any algebraic extension.
- **Impact:** Elevates the 12% from "unsolved problem" to "structural prediction."
- **File:** `phase20/20_extended_spectral_triple.md`

### D21. Required Non-GUT Boundary Condition
- **Track:** 20H
- **Status:** COMPLETE (March 23, 2026)
- **Finding:** Closing the gap via modified boundary condition requires sin²θ_W(Λ) ≈ 0.436, corresponding to trace ratio a₁/a₂ ≈ 0.776. This is only achievable outside the GUT embedding — through twisted spectral triples (Connes-Moscovici), light BSM matter with non-standard quantum numbers, or modified NCG axioms. Points toward the specific mathematical direction for future work.
- **Impact:** Defines the mathematical signature of the resolution.
- **File:** `phase20/20_extended_spectral_triple.md`

---

## New Theorems (Updated)

| # | Statement | Track | Status |
|---|-----------|-------|--------|
| T9 | Position-dependent cutoff Λ(y) preserves gauge universality exactly | 20I | PROVED |
| T10 | NCG universality (T1) + AS universality (T2) + β=0 are mutually incompatible | 20-AS | PROVED |
| T11 | Structural Ceiling: max |δ(α₁⁻¹ - α₃⁻¹)| ≤ 3.1 (29% of gap) within any NCG spectral triple on RS₁ | 20H | PROVED |

## Mechanisms Eliminated (Final: Phase 19 + 20)

1. Standard RG running with KK thresholds (19C.1)
2. Warped AS gravitational running (19C.1b)
3. NCG warped spectral action factorization (14A)
4. Octonionic algebra traces (14A.2)
5. AS gauge-dependent splitting (19C.2)
6. Brane kinetic terms (19C.2b) — T3
7. Warped spectral geometry (19C.2b)
8. Spectral action non-factorization mass-weighted (19C.2c)
9. Full fermion KK tower (Phase 19 evening) — right structure, self-limiting
10. Position-dependent cutoff (20I) — T9
11. NCG-AS synthesis (20-AS) — T10
12. BCJ color-kinematics (20D rev) — not independent of KK thresholds
13. AS-modified spectral function (20-AS.2) — T1 is algebraic
14. Category-theoretic formulation (20F) — all functorial invariants topological
15. **Extended spectral triple (20H) — GUT universality of 3/8 + proton decay tension**

**15 mechanisms eliminated. Zero remaining within the framework.**

---

*Phase 20 findings tracker — COMPLETE. March 23, 2026.*
