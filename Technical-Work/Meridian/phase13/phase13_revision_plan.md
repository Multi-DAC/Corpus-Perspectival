# Phase 13: Monograph Revision & Fundamental Completion

**Created:** March 17, 2026
**Authors:** Clayton & Clawd
**Status:** ACTIVE
**Scope:** Revision + five original research programs bridging literature gaps
**Gate:** Phase 13 complete → arXiv submission (monograph) + potential satellite papers

---

## Purpose

The peer review of the compiled monograph surfaced two critical computational inconsistencies and ten text revisions. Simultaneously, the Eichhorn literature survey revealed five gaps in the global research landscape that Meridian is uniquely positioned to fill. Phase 13 is both a revision phase and a completion phase: fix what's wrong, bridge what's missing, and publish a monograph that isn't just internally consistent but advances the frontier.

**Principle:** Criticality-first for the revision tracks. The fundamental research tracks run in parallel — each one informs the monograph and may produce independent publications.

**This is the lifelong project. Phase 13 extends as we learn.**

---

## Track Summary

### Part A — Monograph Revision (Tracks 13A–13K)

| Track | Title | Severity | Status | Depends On |
|-------|-------|----------|--------|------------|
| **13A** | Trace H&K computation | CRITICAL | Pending | — |
| **13B** | Resolve brane parameter inconsistency | CRITICAL | Pending | — |
| **13C** | Narrative decision: DESI-compatible or ΛCDM-adjacent | CRITICAL | Pending | 13A, 13B |
| **13D** | Rewrite Paper II observational confrontation | MAJOR | Pending | 13C |
| **13E** | Apply text revisions (10 items) | MAJOR | Pending | 13C |
| **13F** | CKK derivation chain verification | MAJOR | Pending | 13B |
| **13G** | Self-tuning numerical demonstration | SIGNIFICANT | Pending | 13B |
| **13H** | Adams et al. UV completion bounds | SIGNIFICANT | Pending | — |
| **13I** | fσ₈ → H(z) methodology documentation | SIGNIFICANT | Pending | 13A |
| **13J** | Co-authorship & editorial formatting | EDITORIAL | Pending | — |
| **13K** | Final LaTeX compilation & validation | GATE | Pending | All above |

### Part B — Fundamental Research: Bridging the Gaps (Tracks 13L–13P)

| Track | Title | Type | Status | Depends On |
|-------|-------|------|--------|------------|
| **13L** | NCG–AS Bridge: Spectral action meets asymptotic safety | FRONTIER | Pending | — |
| **13M** | Warped 5D Asymptotic Safety: RS orbifold beta functions | FRONTIER | Pending | — |
| **13N** | Gauss-Bonnet in 5D + AS: ε₁ from fixed points | FRONTIER | Pending | 13M |
| **13O** | Superluminal Scalar Positivity: c_s > c and UV completion | FRONTIER | Pending | 13H |
| **13P** | ξ = 1/6 Convergence: NCG + AS + conformal invariance | FRONTIER | Pending | 13L |

---

## Part A — Monograph Revision Tracks

### 13A: Trace the H&K Computation [CRITICAL]

**Problem:** The monograph claims χ²(ΛCDM) = 24.6/18 dof with Planck 2018 fiducial (H₀ = 67.4). Independent reproduction yields χ² = 7.24/18. The monograph's value is consistent with H₀ ≈ 70, not 67.4. If the "3.8σ detection" used the wrong fiducial, it measured the Hubble tension, not ζ₀.

**Tasks:**
1. Search all computational records (phase8/, phase9/, phase10/) for the original H&K fit
2. Identify the actual H₀ and Ωₘ used in the computation
3. Check whether a different H(z) dataset was fit (not the Table 2.14 compilation)
4. Check whether β_HK was defined differently (e.g., including growth-rate modification)
5. Rerun with verified parameters and document the result

**Output:** Definitive answer: what fiducial was used, what the correct χ² is, and what ζ₀ the data actually constrain.

---

### 13B: Resolve Brane Parameter Inconsistency [CRITICAL]

**Problem:** Stated parameters (σ_UV=6, α_UV=0.01, ξ=1/6, μ²=0.1, M₅³=1) yield Φ₀ = 0.076 from the junction conditions, not the claimed Φ₀ = 0.477. The value 0.477 was chosen to produce ζ₀ = 0.038, but doesn't satisfy JC(1.54b) — residual = −1.10.

**Tasks:**
1. Search computational records for original brane parameter scan
2. Determine whether different parameters were used, or different JC formulation
3. Check for units issues (Φ₀ in different normalization)
4. If parameters were chosen to match ζ₀ = 0.038 from H&K: this is circular — flag it
5. Compute the self-consistent parameter set: what brane physics actually predicts ζ₀

**Output:** Self-consistent (parameters, Φ₀, ζ₀) triple that satisfies the junction conditions.

**Key finding from peer review:** With actual JC solution Φ₀ = 0.076 → ζ₀ = 0.00096 → w₀ = −0.745. This is in the DESI range.

---

### 13C: Narrative Decision [CRITICAL — requires Clayton]

**Depends on:** 13A and 13B results.

**The fork:** The resolution of 13A and 13B determines which story the monograph tells.

**Option 1 — DESI-compatible (ζ₀ ≈ 0.001, w₀ ≈ −0.75):**
- Framework *predicts* the DESI signal instead of explaining it away
- Paper III no-go analysis reframed: Horndeski dilemma still holds, but magnitude depends on ζ₀
- Dramatically more testable — deviation is ~25%, detectable NOW
- Loses "zero free parameters" claim (ζ₀ becomes a one-parameter family)
- Paper II rewritten around ζ₀ as a free parameter constrained by data

**Option 2 — ΛCDM-adjacent (find parameters that genuinely produce ζ₀ ≈ 0.038):**
- Must find self-consistent brane parameters (they exist — the system is underdetermined)
- Must independently verify the H&K detection with correct fiducial
- Preserves the current narrative structure
- Risk: if H&K doesn't hold with correct fiducial, ζ₀ = 0.038 has no observational anchor

**Option 3 — Present both as limits:**
- ζ₀ is a free parameter determined by brane physics
- Show the prediction as a function of ζ₀
- H&K constrains ζ₀ (with honest error bars)
- w₀(ζ₀) curve is the prediction; specific value depends on UV completion

**Output:** Decision on narrative direction. This determines all downstream revisions.

---

### 13D: Rewrite Paper II Observational Confrontation [MAJOR]

**Depends on:** 13C decision.

**Tasks (will be specified after 13C, but scope includes):**
1. Revise H&K analysis with correct fiducial and honest error bars
2. Update Bayes factors and information criteria
3. Revise Fisher forecasts (13σ DESI Y5 projection may change dramatically)
4. Update growth-expansion decoupling claims
5. Revise DESI confrontation (Section 2.5) — may flip from "artifact" to "prediction"
6. Update all tables with corrected numbers

---

### 13E: Apply Text Revisions (10 Items) [MAJOR]

**Depends on:** 13C (some revisions change based on narrative direction).

From the revision document, in order:

| # | Revision | Papers Affected |
|---|----------|-----------------|
| R1 | Reframe "Two Axioms" → "Two axioms + four commitments" | All (especially I §1.2.5) |
| R2 | CKK derivation chain — add consistency check, state uncertainty | I §1.7.3 |
| R3 | Conformal coupling "three derivations" → "three perspectives on one fact" | I §1.4.6, IV §4.7.3 |
| R4 | Promote coincidence problem to Discussion section | I (new §1.10.X) |
| R5 | Flag Conjecture 4.3 as load-bearing | IV (after Conj. 4.3) |
| R6 | Balance DESI confrontation — acknowledge data ambiguity | II §2.5.4 |
| R7 | Soften Horndeski Dilemma: Theorem → Proposition | III §3.8 |
| R8 | Compress Phase 12 engineering speculation | V §5.5.3 |
| R9 | Co-authorship → Acknowledgments (journal compliance) | All |
| R10 | Move epigraph, add Eq. (1.1) footnote | I |

**Note:** R6 and R7 may need significant rework depending on 13C outcome.

---

### 13F: CKK Derivation Chain Verification [MAJOR]

**Depends on:** 13B (the ζ₀ value propagates through CKK).

**Tasks:**
1. Verify dimensional consistency: Φ₀² = 3ζ₀M²_Pl requires k = 1/2 — check conventions
2. Compute CKK with uncertainty: currently 0.216 "at leading order" → should be 0.26 ± 0.04
3. Propagate CKK uncertainty into σ(w₀)
4. If ζ₀ changes (per 13C), recompute w₀ and all downstream predictions

---

### 13G: Self-Tuning Numerical Demonstration [SIGNIFICANT]

**Tasks:**
1. Implement Chebyshev collocation on RS orbifold for the coupled (A', Φ) system
2. Demonstrate Λ₄ independence of Λ₅ via full dynamical integration (not just algebraic)
3. If spectral method succeeds: replace Section 1.3.7 with clean numerical result
4. If spectral method also fails: rewrite Section 1.3.7 per peer review recommendation (algebraic proof primary, Φ₀ independence scan as consistency check, honest stiffness statement)

**Already verified:** Φ₀ is Λ₅-independent (61 values, machine precision). Algebraic argument sound.

---

### 13H: Adams et al. UV Completion Bounds [SIGNIFICANT]

**Tasks:**
1. Compute 2→2 forward-scattering amplitude for ε₁X term
2. Check positivity bounds (Adams et al., JHEP 0610:014, 2006)
3. Determine whether 5D UV completion (subluminal bulk) provides sufficient justification
4. Strengthen Section 5.3.2 argument if needed
5. Cross-reference with Eichhorn+ (2405.08862) positivity results for AS

**Feeds into:** Track 13O (scalar positivity bounds)

---

### 13I: fσ₈ → H(z) Conversion Methodology [SIGNIFICANT]

**Depends on:** 13A (same computational pipeline).

**Tasks:**
1. Document how WiggleZ and VIPERS fσ₈ measurements were converted to H(z)
2. Assess model-dependence of the conversion
3. Add methodology section or appendix to Paper II
4. If conversion is model-dependent: flag and assess impact on ζ₀ constraint

---

### 13J: Co-authorship & Editorial Formatting [EDITORIAL]

**Tasks:**
1. Implement co-authorship decision (likely: Clayton as author, Clawd in Acknowledgments per journal policy)
2. Final formatting pass: consistent notation, citation style, cross-references
3. Remove any self-referential citations (papers citing themselves as "forthcoming")
4. Verify all bibliography entries exist and are correctly formatted
5. Add new citations from Eichhorn survey (see `phase13/eichhorn_asymptotic_safety_connections.md`)

---

### 13K: Final Compilation & Validation [GATE]

**Depends on:** All Part A tracks + relevant Part B results.

**Tasks:**
1. Apply all revisions to markdown source files (phase11/paper_I_draft.md etc.)
2. Regenerate LaTeX from revised markdown
3. Run validate_monograph.py
4. Compile with pdflatex (MiKTeX installed)
5. Visual inspection of compiled PDF
6. Final peer review pass
7. **Gate decision: GO/NO-GO for arXiv submission**

---

## Part B — Fundamental Research: Bridging the Gaps

*Each track represents unexplored territory in the global literature. Each could produce an independent publication. Results feed back into the monograph where applicable.*

---

### 13L: NCG–AS Bridge [FRONTIER]

**The gap:** No paper in the literature connects Connes' spectral action to asymptotic safety fixed points. These are two of the most developed quantum gravity programs. Nobody has asked whether they're compatible, complementary, or secretly the same.

**Research questions:**
1. Does the spectral action S = Tr(f(D²/Λ²)) generate an effective action whose couplings flow to an AS fixed point?
2. Can the Seeley-DeWitt heat kernel expansion (which produces the spectral action's physical content) be reinterpreted as a derivative expansion around an RG fixed point?
3. Does the NCG classification theorem (finite spectral triples → SM gauge group) survive when the gravitational sector is UV-completed by AS?
4. Is there a "spectral fixed point" — a Dirac operator D* that is a fixed point of some spectral RG flow?

**Approach:**
1. Start with the simplest case: NCG on flat 4D with U(1) gauge field. Compute the spectral action and extract the coupling constants. Compare to Eichhorn's photon-graviton AS flow.
2. Add gravity: spectral action on a compact Riemannian 4-manifold. The a₄ coefficient gives Einstein-Hilbert + cosmological constant + Weyl² + GB. Compare coefficient ratios to AS fixed-point values.
3. If ratios match: this is evidence that NCG and AS are different descriptions of the same UV structure. If they don't match: identify which additional constraints AS imposes beyond the NCG axioms.
4. Extend to M₄ × F (SM spectral triple). Does AS constrain the finite space F?

**Key references:**
- Chamseddine & Connes, spectral action papers (1996–2012)
- Eichhorn review arXiv:2003.00044
- Ohta & Percacci arXiv:1308.3398 (higher-derivative AS in diverse dimensions)

**Output:** Paper or section establishing whether NCG and AS are compatible, complementary, or in tension.

---

### 13M: Warped 5D Asymptotic Safety [FRONTIER]

**The gap:** AS survives in flat 5D (Ohta-Percacci 2014). Nobody has studied AS on a warped Randall-Sundrum orbifold. Our entire framework lives on this geometry.

**Research questions:**
1. Does the Reuter fixed point survive on AdS₅ sliced by Minkowski₄ branes?
2. How does the warp factor e^{-2ky} modify the beta functions?
3. Does the KK spectrum (graviton tower) affect the running of gravitational couplings?
4. At what energy scale does the 5D → 4D crossover occur in the RG flow, and is it consistent with the KK scale k·e^{-kyc}?

**Approach:**
1. Background field method on RS geometry: expand g_MN = ḡ_MN + h_MN where ḡ is the RS solution
2. Compute one-loop effective action using heat kernel on the warped background
3. Extract beta functions for Newton's constant and cosmological constant in the warped geometry
4. Look for fixed points; compare to flat 5D results (Ohta-Percacci)

**Technical challenge:** The warped geometry breaks 5D Lorentz invariance → the heat kernel coefficients on AdS₅ are non-standard. May need the Gilkey-Branson-Ørsted results for manifolds with boundary.

**Key references:**
- Ohta & Percacci arXiv:1308.3398
- Gerwick, Litim, Plehn arXiv:1101.5548 (KK gravitons + AS)
- Randall & Sundrum (1999) original papers

**Output:** First computation of AS beta functions in warped 5D geometry. Determines whether our RS framework is UV-complete in the AS sense.

---

### 13N: Gauss-Bonnet in 5D + Asymptotic Safety [FRONTIER]

**The gap:** In 4D, the GB term is topological (total derivative). In 5D, it contributes non-trivially to the dynamics — and our ε₁ = 0.017 comes from the GB correction. Nobody has computed whether AS in 5D predicts or constrains the GB coefficient.

**Depends on:** 13M (needs the warped 5D AS framework).

**Research questions:**
1. In the 5D AS fixed point, what is the predicted GB coupling (α_GB)?
2. Is our C_GB = 2/3 (which gives ε₁ = 0.017) consistent with the AS prediction?
3. Does the GB term's topological nature in 4D emerge naturally from the 5D → 4D flow at the AS fixed point?

**Approach:**
1. Include R² and R_MN² (equivalently, Weyl² and GB) in the 5D truncation
2. Compute beta functions for all gravitational couplings including α_GB
3. Find fixed-point values; extract the physical GB coefficient
4. Compare to Meridian's C_GB = 2/3

**Key references:**
- Ohta & Percacci arXiv:1308.3398 (C² and GB in diverse dimensions)
- Meridian Paper I, Section 1.5 (GB correction derivation)

**Output:** AS prediction for the 5D GB coefficient. Comparison to Meridian's derived value.

---

### 13O: Superluminal Scalar Positivity Bounds [FRONTIER]

**The gap:** Eichhorn+ (2025) showed AS respects positivity bounds for *photon*-graviton systems. Our cuscuton has c_s ~ 10c — superluminal scalar propagation. Nobody has studied whether AS modifies the Adams et al. (2006) positivity bounds for *scalar* fields, or whether a 5D UV completion can justify superluminal 4D propagation.

**Depends on:** 13H (Adams et al. bounds computation).

**Research questions:**
1. Does our 5D UV completion (where the bulk scalar propagates subluminally) satisfy positivity bounds in the 4D effective theory despite c_s > c?
2. Can we prove a "subluminal UV → superluminal EFT" theorem: if the fundamental theory is causal, can the KK-reduced EFT have c_s > c without violating unitarity/analyticity?
3. What are the positivity bounds on the ε₁X operator specifically?
4. Does the cuscuton limit (c_s → ∞ as ε₁ → 0) have special status regarding positivity?

**Approach:**
1. Compute the 2→2 scalar scattering amplitude in the 4D EFT with P(X) = ε₁X
2. Check forward-scattering dispersion relation (Adams et al. methodology)
3. Compare to the full 5D amplitude (which includes KK tower exchange)
4. The KK tower acts as the UV completion — verify that the tower sum respects the positivity bounds

**Key references:**
- Adams, Arkani-Hamed, Dubovsky, Nicolis, Rattazzi, JHEP 0610:014 (2006)
- Eichhorn, Pedersen, Schiffer arXiv:2405.08862
- de Rham, Melville, Tolley, Zhou on positivity bounds for EFTs (2017–2022)
- Meridian Paper V, Section 5.3

**Output:** Rigorous statement about whether Meridian's c_s ~ 10c is consistent with UV completeness. Could resolve one of the monograph's open questions.

---

### 13P: ξ = 1/6 Convergence [FRONTIER]

**The gap:** Meridian derives ξ = 1/6 from the spectral triple (three proofs: Seeley-DeWitt a₂, Weyl invariance, radion identification). Eichhorn has "hints" that AS constrains ξ but no definitive value. If AS independently predicts ξ = 1/6, that's convergence from two QG programs — a result with implications far beyond our specific model.

**Depends on:** 13L (NCG-AS bridge framework).

**Research questions:**
1. At the Reuter fixed point with a non-minimally coupled scalar, what is the fixed-point value of ξ?
2. Does the AS prediction for ξ depend on the matter content (number of scalars, fermions, gauge fields)?
3. With SM matter content (as determined by the NCG spectral triple), does ξ_AS = 1/6?
4. Is there a deep reason why conformal coupling appears in both programs? (Weyl invariance in NCG; possibly conformal fixed point in AS?)

**Approach:**
1. Start from Eichhorn+ arXiv:2009.13543 ("Constraining power of AS for scalar fields")
2. Extract the beta function β_ξ in the AS framework with SM matter content
3. Find the fixed point ξ* and assess its stability (relevant vs irrelevant)
4. If ξ* = 1/6: prove it analytically. If ξ* ≠ 1/6: understand why and what this means for the NCG-AS relationship
5. If ξ = 1/6 is a UV *attractor* in AS: this would mean conformal coupling isn't just derived — it's *inevitable* under RG flow. The NCG derivation and the AS derivation would be the UV and IR faces of the same coin.

**Key references:**
- Eichhorn, Pauly, Schiffer arXiv:2009.13543
- Meridian Paper I §1.4.6 and Paper IV §4.7.3
- Buchbinder, Odintsov, Shapiro — "Effective Action in Quantum Gravity" (textbook, β_ξ derivation)

**Output:** Definitive answer on whether AS predicts ξ = 1/6. If yes: a letter-quality result establishing convergence between NCG and AS. If no: a clear characterization of where the two programs diverge.

---

## Execution Architecture

```
PART A — REVISION (critical path to publication)
═══════════════════════════════════════════════════
Phase 13A ──┐
             ├──→ 13C (narrative) ──→ 13D (Paper II rewrite)
Phase 13B ──┘                      ──→ 13E (text revisions)
                                   ──→ 13F (CKK verification)

13H (Adams et al.) ─── independent ──→ feeds 13O
13G (self-tuning) ──── after 13B
13I (fσ₈ method) ──── after 13A
13J (editorial) ────── independent

ALL Part A ──→ 13K (compile, validate, GATE)

PART B — FUNDAMENTAL RESEARCH (parallel, feeds back into monograph)
═══════════════════════════════════════════════════════════════════
13L (NCG-AS bridge) ────── independent ──→ feeds 13P
13M (warped 5D AS) ─────── independent ──→ feeds 13N
13N (GB in 5D + AS) ────── after 13M
13O (scalar positivity) ── after 13H ──→ strengthens Paper V
13P (ξ convergence) ────── after 13L ──→ strengthens Papers I & IV

PART B results ──→ incorporated into monograph at 13K if ready
              ──→ independent publications if they mature beyond monograph scope
```

---

## Success Criteria

### Monograph Gate (Part A)
- [ ] All computational claims independently verified and self-consistent
- [ ] Every number in every table traces to a documented computation
- [ ] Narrative honestly represents what the framework predicts and what the data constrain
- [ ] All ten text revisions applied
- [ ] Eichhorn citations integrated where relevant
- [ ] LaTeX compiles cleanly with zero errors
- [ ] validate_monograph.py passes with zero errors
- [ ] Clayton and Clawd both sign off

### Fundamental Research (Part B)
- [ ] 13L: Definitive statement on NCG-AS compatibility
- [ ] 13M: AS beta functions computed on warped RS geometry
- [ ] 13N: AS prediction for 5D GB coefficient obtained
- [ ] 13O: Positivity bounds resolved for Meridian's c_s ~ 10c
- [ ] 13P: ξ_AS value determined; convergence assessed

### The Standard
Each result must meet the same bar: maximal truth, minimal sycophancy. If a computation shows our framework is wrong somewhere, we say so. If a gap turns out to be unbridgeable, we say so. The goal is not to confirm our theory — it's to find out what's true.

---

*Phase 13 is where the theory meets reality in both senses: confrontation with data (Part A) and exploration of the frontier (Part B). This is the lifelong project. We extend as we learn. The exploration of reality doesn't have a deadline — it has a direction.*

🦞🧍💜🔥♾️
