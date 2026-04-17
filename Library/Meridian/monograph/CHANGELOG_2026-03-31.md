# Monograph Changelog — March 31, 2026

## Summary
Comprehensive editorial pass implementing findings from the monograph cross-reference audit.
All changes maintain the existing logical structure; no theoretical results were altered.

## Files Modified

### chapter1_foundation.tex
1. **Radion section (Section 4.3)**: Updated to reflect Phase 23 finding that cuscuton and radion are distinct modes (not the same field). Removed language suggesting "cuscuton may play the role of the stabilizing scalar."
2. **Radion mass**: Updated from classical estimate (~O(10^2) GeV) to quantum-corrected result (m_rad ≈ 120 GeV from NCG spectral action, 99.7% NCG contribution). Classical formula retained as Eq. 1-radion-mass-classical; quantum result added as Eq. 1-radion-mass-quantum.
3. **Radion limitations paragraph**: Updated to note classically massless radion, NCG quantum correction as dominant mass source, and proximity to Higgs mass (125.1 GeV).
4. **w₀ value note**: Added clarification that the analytical formula gives -0.746 while the full numerical evaluation gives -0.755, a ~1% shift from additional cosmological parameter precision.
5. **m_ee prediction (Prediction 8)**: Updated range from 3-5 meV to 1.5-5 meV, noting TBM limit vs realistic PMNS mixing. Updated detectability assessment: null result in 0νββ is a concrete negative prediction.

### chapter2_observational.tex
1. **c_s standardization**: Changed all instances of "c_s ~ 10c" to "c_s ≈ 11c" for consistency with Ch5's derived value (11.3c).
2. **m_ee prediction (Prediction 9)**: Updated range to 1.5-5 meV with explanation of TBM limit vs realistic range. Updated detectability table: LEGEND-1000 changed from "Marginal" to "No (below threshold)", nEXO changed from "Yes" to "Marginal (upper edge only)". Added note that null result is a concrete negative prediction.

### chapter4_ncg.tex
1. **c_s standardization**: Changed all instances of "c_s ~ 10c" to "c_s ≈ 11c".
2. **Collider section (Section 13)**: Added predicted radion mass paragraph noting m_r ≈ 120 GeV from NCG quantum corrections. At this mass, Higgs-radion mixing angle increases to ~18.5° and κ_V - 1 ≈ 0.021, entering HL-LHC sensitivity range.
3. **m_ee (Eq. 4-111)**: Added "(tribimaximal limit)" label and note about 1.5-3.7 meV realistic range from S₃-breaking.

### appendix_computations.tex
1. **Radion mass section**: Updated from classical-only estimate to quantum-corrected result (120 GeV from NCG one-loop). Added note on cuscuton-radion distinction. Updated Goldberger-Wise comparison table to reflect separate modes and quantum mass origin.

## New Files Created

### monograph_audit_2026-03-31.md
Comprehensive cross-reference audit identifying 4 critical, 6 important, 5 moderate, and 4 low-priority issues across the monograph.

### figures/ (8 publication-quality figures)
| Figure | Content | Chapters |
|--------|---------|----------|
| fig1_w0_zeta0 | w₀(ζ₀) parametric curve with benchmarks | Ch1 |
| fig2_wz_comparison | w(z) evolution: Meridian vs CPL vs ΛCDM | Ch2 |
| fig3_chi2_comparison | χ² model comparison (5 models) | Ch2 |
| fig4_inflation_nsr | Inflationary (n_s, r) prediction plane | Ch4 |
| fig5_fermion_profiles | Fermion localization in extra dimension | Ch4 |
| fig6_goldilocks | ε₁ Goldilocks window | Ch5/Appendix |
| fig7_forecast | Sensitivity forecast timeline | Ch2 |
| fig8_sound_speed | Sound speed landscape comparison | Ch5 |

### figures/figure_includes.tex
LaTeX \includegraphics commands and captions for all 8 figures, ready to be placed in the appropriate chapters.

### figures/generate_all_figures.py
Python script generating all figures from the framework's parameters.

## Issues Resolved

| Issue | Status | Resolution |
|-------|--------|------------|
| C1: w₀ value proliferation | **Resolved** | Added clarifying note; both -0.746 and -0.755 acknowledged |
| C2: c_s ~10c vs ~11c | **Resolved** | Standardized to ~11c across all chapters |
| C3: Radion-cuscuton distinction | **Resolved** | Updated Ch1 + appendix; Phase 23 correction integrated |
| C4: B_eff ansatz | **Deferred** | Phase 24 material not yet in monograph |
| I2: m_ee range | **Resolved** | Standardized to 1.5-5 meV with context |
| I4: Quantum radion mass | **Resolved** | 120 GeV integrated into Ch1, Ch4, appendix |

## Issues Remaining

1. **Phase 22 results** (S₃ breaking theorem, Quartic Casimir) not yet integrated into Ch4
2. **Phase 24 experimental material** not yet integrated (deferred to separate paper or future monograph update)
3. **New sections** (new_sections/) already merged into main chapters; these files are now archival
4. **Figure placement**: figure_includes.tex provides the LaTeX commands but figures not yet placed in the chapter files (requires choosing placement locations)
5. **LaTeX compilation**: Full compilation test needed to verify cross-references and figure placement
