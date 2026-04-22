# Meridian Monograph — LaTeX Compilation

**Current compile:** 2026-04-21 (v2), 198pp
**v1 published:** 2026-04-17, 193pp, Zenodo [10.5281/zenodo.19634864](https://doi.org/10.5281/zenodo.19634864)
**Total:** ~13,419 lines across 11 files

## Files

| File | Lines | Content |
|------|-------|---------|
| `meridian_monograph.tex` | 355 | Main book file (preamble, custom commands, `\input` statements) |
| `chapter0_basin.tex` | 810 | Ch 0: Orientation — axioms, Principle frame, notation table (v2 §4.a) |
| `chapter1_foundation.tex` | 1,859 | Ch 1: Self-Tuning from 5D Warped Geometry |
| `chapter2_observational.tex` | 1,673 | Ch 2: Observational Confrontation |
| `chapter3_nogo.tex` | 916 | Ch 3: No-Go Theorems |
| `chapter4_ncg.tex` | 3,261 | Ch 4: NCG Spectral Geometry on Warped Orbifolds |
| `chapter5_sound_speed.tex` | 691 | Ch 5: Sound Speed of DE (recursive decomposability at close, v2 §5.e) |
| `appendix_computations.tex` | — | App A: Computations (+ v2 SymPy $C_{GB}$ verification, xi historical-simplification) |
| `appendix_gw_computation.tex` | 146 | App E: GW Computation (v2: factor-of-3 reframed as candidate inspection-depth ceiling) |
| `appendix_prediction_registry.tex` | 329 | App B: Prediction Registry (v2: conditional fboxes for P4/P5/P6/P8; DE fingerprint comparison table) |
| `appendix_value_table.tex` | 297 | App D: Value Table (v2: apophaticism, stream scope audit, radion-thinness, AS §section, LISA MC + radion figures, reproducibility manifest) |
| `bibliography.tex` | 1,779 | Shared references |

## Compilation

```bash
cd Library/Meridian/monograph/
pdflatex -interaction=nonstopmode meridian_monograph.tex
pdflatex -interaction=nonstopmode meridian_monograph.tex  # second pass for cross-refs
pdflatex -interaction=nonstopmode meridian_monograph.tex  # third pass stabilizes TOC + page numbers
```

Three passes converge to 198pp on the v2 sources. Figures fig0-fig11 live under `figures/` (fig0 resolves via `../figures/fig0_derivation_chain.pdf`).

## v2 Changelog (2026-04-21)

See `../README.md` for the full tiered changelog. Summary:

- **Tier A propagation (S1):** $\xi = 1/6$ "three perspectives" canonicalized; $N_g = 3$ "algebraic maximum" canonicalized; prediction count = 15 canonical; $C_{KK}$ canonical at App D Tier 2; benchmark taxonomy anchored to weighted-mean $\zeta_0 = 0.016 \pm 0.002$, $w_0 = -0.990$.
- **Tier B notation (S2, S4):** Ch 0 master notation table ($\xi / C_{GB} / \varepsilon_1 / \varepsilon_2 / \varepsilon / \hat\alpha / \zeta_0 / w_0 / C_{KK}$); conditional fboxes for P4 (radion), P5 (0νββ), P6 (sterile ν), P8 (LISA); Ch 5 $\varepsilon_2 \leq 5\%$ explicit; $c_s$ floor 4.6c rounding; Evasion 3 heading.
- **Tier C displays (S3):** App D reproducibility manifest; App D LISA SNR Monte Carlo (fig10, 1000 samples, Caprini scaling); App D radion potential scan (fig11); App D SymPy $C_{GB} = 2/3$ verification; App D AS-exclusion promoted to `\section`; App B DE-fingerprint comparison table; Ch 5 scalar-response note relegated and fbox'd.
- **Coherence-Principle integration (S5):** App E factor-of-3 gap as *candidate inspection-depth ceiling* with hedge; App D structured apophaticism (theory-scope vs access remainder); App D stream scope audit (generic / this-stream / saturation); App D radion barrier-thinness with three explicit scope-limits; Ch 0 philosophical frame section forward-referencing Anchor DOI [10.5281/zenodo.19634474](https://doi.org/10.5281/zenodo.19634474); Ch 5 recursive decomposability paragraph.

## Notes

- Each chapter carries its own `\begin{thebibliography}` with namespace-prefixed keys (`ch1:`, `ch2:`, etc.).
- Equation labels follow `eq:N-XX` (N = chapter number).
- Custom commands defined in the main file (`\wz`, `\zz`, `\eps`, `\ahat`, `\CGB`, `\CKK`). Note: `\eps` expands to `\epsilon_1`; writing `\eps_1` triggers a non-fatal TeX "Double subscript" warning in existing prose (unchanged from v1).
- Theorem environments: theorem, proposition, corollary, conjecture, definition, scalingrelation.
- Figure generator: `scripts/generate_all_figures.py` (outputs to `figures/`).
- PDF is force-added past the repo-wide `*.pdf` gitignore exclusion for reviewer repeatability; regenerate locally with the three-pass compile above.

## v1 → v2

v2 supersedes v1. The v1 PDF is preserved via its Zenodo deposit. v2 Zenodo deposit forthcoming; will cite v1 DOI as `supersedes`.
