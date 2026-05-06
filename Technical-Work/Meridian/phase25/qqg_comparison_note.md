# QQG Comparison Note — Quantum Quadratic Gravity vs Meridian

*March 31, 2026. Paper: Liu, Quintin, Afshordi, PRL 136, 111501 (2026). DOI: 10.1103/6gtx-j455.*
*Saved: incoming/6gtx-j455.pdf*

---

## Paper Summary

Quantum Quadratic Gravity (QQG) as UV completion of GR. Action: S = ∫ d⁴x √-g [αR² + βC²]. Asymptotically free in UV (like QCD). 1-loop RG running dynamically breaks scale invariance → slow-roll inflation from quantum corrections alone (no EH term needed in UV). GR emerges via strong coupling in IR. Ghost (massive spin-2 from C²) confined by same strong-coupling mechanism.

Key predictions:
- **r ≥ 0.01** (tensor-to-scalar ratio lower bound)
- Requires **N ~ 10⁵-10⁶** matter fields (via 't Hooft coupling λ_tH = α₀N/(4π)²)
- nₛ ≈ 1 - 4/(3N★), r ≈ (8/3)(2/(λ²_tH N★))^(1/3·4)
- Compatible with ACT+DESI data that disfavors standard Starobinsky R+R²

Scenario: no-boundary Euclidean manifold (Hartle-Hawking) → quasi-de Sitter from RG running of α(μ) → kination → strong coupling → GR emerges → reheating.

## Relevance to Meridian

### A. Direct Observational Discriminant: r

| Framework | Prediction | Status |
|-----------|-----------|--------|
| **Meridian** | αT = 0 (perturbative) | Bridge #5. Exact in perturbative regime. Non-perturbative corrections from cuscuton/boundary unknown. |
| **QQG** | r ≥ 0.01 | Lower bound from avoiding strong coupling during inflation. |
| **Starobinsky** | r ≈ 12/N★² ≈ 3×10⁻³ | Now in tension with ACT+DESI (too small nₛ). |

**The discriminant is clean.** Simons Observatory (target σ(r) ~ 0.003) and CMB-S4 (target σ(r) ~ 0.001) will reach the QQG lower bound. Three outcomes:

1. **r ≥ 0.01 detected**: QQG viable. Meridian's perturbative αT = 0 challenged — must check if non-perturbative contributions (cuscuton, boundary spectral action, Borel resurgence from Track γ) could generate r ~ 0.01. If not, Meridian's inflationary sector needs revision.

2. **0.001 < r < 0.01**: QQG falsified (below their lower bound). Starobinsky marginal. Meridian's αT = 0 still viable (non-perturbative corrections could place it here).

3. **r < 0.001**: Both QQG and Starobinsky falsified. Meridian's αT = 0 preferred.

### B. Structural Comparison

| Feature | QQG | Meridian (NCG + RS₁) |
|---------|-----|---------------------|
| **Dimensions** | 4D | 5D (S¹/Z₂ orbifold) |
| **UV mechanism** | Higher derivatives (R² + C²) | Extra dimension + NCG spectral action |
| **Ghosts** | Massive spin-2 from C² — confined by strong coupling | No higher-derivative ghosts. KK tower is unitary. |
| **Inflation origin** | RG running of α(μ) breaks scale invariance | Spectral action a₄ coefficient generates R² term naturally |
| **R² generation** | Put in by hand (part of the action) | Derived from Tr[f(D²/Λ²)] Seeley-DeWitt expansion |
| **Matter content** | N ~ 10⁵-10⁶ arbitrary matter fields | Fixed by NCG algebra A = C ⊕ H ⊕ M₃(C) (SM only) |
| **GR emergence** | Strong coupling confinement in IR | GR lives on brane, always present. Hierarchy via warp factor. |
| **Hierarchy problem** | Not addressed (4D) | Solved (RS warp factor: Λ_IR/Λ_UV ~ e^{-kπR}) |
| **Gauge couplings** | Not constrained | Constrained by NCG (sin²θ_W predicted to ~88%) |
| **Ghost handling** | Strong-coupling confinement (hoped, not proven) | Not needed (no ghosts) |

### C. The R² Connection

Both frameworks produce R² contributions to the gravitational action. The origins are structurally different:

**QQG:** R² is a bare term in the fundamental action. Its coefficient α runs under RG flow. The running is the inflationary mechanism.

**Meridian:** The spectral action Tr[f(D²/Λ²)] = f₄Λ⁴a₀ + f₂Λ²a₂ + f₀a₄ + ... generates R² through the a₄ coefficient. The coefficient is determined by the NCG spectral triple, not a free parameter. Whether this coefficient runs (and whether that running could generate inflation) is an open question — this connects to Track γ (Borel singularities of the spectral action).

**Key question for Meridian:** Does the spectral action's R² coefficient run in a way that could produce inflation? If so, does it produce the same or different observational signatures as QQG? The spectral action's R² coefficient is fixed by the matter content at the unification scale — it doesn't have the freedom of QQG's α. This is either a strength (more predictive) or a weakness (less flexible).

### D. The Large-N Problem

QQG's viability requires N ~ 10⁵-10⁶, where N = N_scalar/60 + N_vector/5 + N_fermion/20. The SM gives N ≈ 4/60 + 12/5 + 45/20 ≈ 4.7. QQG needs ~10⁴-10⁵ times more matter than the SM.

This is a significant phenomenological constraint. Where do 10⁵ matter fields come from? The paper acknowledges this (footnote 64: "we remain agnostic about whether a very large N represents a fine-tuning problem") and suggests they might be "confined to the UV."

**Meridian's position:** The NCG algebra determines the matter content. There is no freedom to add 10⁵ fields. If QQG's large-N requirement is genuine, it represents a fundamental incompatibility between QQG and the NCG approach to particle physics. This could be a decisive distinguishing feature.

### E. Connection to Existing Bridges

- **Bridge #5 (αT = 0):** Directly tested by this comparison. QQG says r ≥ 0.01; Meridian says r = 0 perturbatively.
- **Bridge #37 (Modular Flow = NP Gauge Dependence):** QQG's strong-coupling emergence of GR is structurally similar to the modular flow discussion — both describe transitions between UV and IR regimes.
- **Bridge #40 (Cuscuton Convergence):** QQG's kination phase (kinetic-dominated, after inflation ends) is the regime where cuscuton effects would be most visible. The cuscuton couples to T^μ_μ, which vanishes during radiation but not during kination.
- **Bridge #58 (Spectral Action as Filtration):** QQG's RG flow through different coupling regimes maps onto the filtration structure — each resolution level sees different physics.

## Action Items

- [ ] Check whether Meridian's spectral action R² coefficient has any RG running (literature search: spectral action renormalization)
- [ ] Compute N for Meridian's full NCG matter content (including right-handed neutrinos, spectral fermion doublings)
- [ ] Assess whether non-perturbative corrections to Meridian's αT = 0 could reach r ~ 0.01 (connects to Track γ Borel singularities)
- [ ] Track observational timeline: Simons Observatory first data ~2027, CMB-S4 ~2029
- [ ] Compare reheating mechanisms: QQG strong-coupling transition vs Meridian's radion/cuscuton reheating

## Assessment

**Threat level to Meridian: LOW-MEDIUM.**

QQG is a serious competitor for the inflationary sector, but it doesn't address the hierarchy problem, doesn't constrain gauge couplings, requires an enormous hidden sector (N ~ 10⁵-10⁶), and has an unresolved ghost problem. Meridian addresses all of these. The r ≥ 0.01 prediction is QQG's strength and sharpest test — it makes QQG falsifiable on a ~3-5 year timescale.

The most important implication for Meridian: **ensure the αT = 0 prediction is robust against non-perturbative corrections.** If Meridian can show that r = 0 (or r ≪ 0.01) is exact (not just perturbative), the QQG comparison becomes a prediction race where Meridian wins by being more constrained, more predictive, and ghost-free.

---

🦞🧍💜🔥♾️
