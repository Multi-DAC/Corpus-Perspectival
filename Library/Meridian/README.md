# Meridian (Physics Monograph)

Theory-of-everything program: 5D warped geometry × noncommutative geometry × self-tuning cosmology, with empirical bridges to dark energy, gravitational waves, and Standard Model structure.

## Versions

- **v1** — 181pp, published 2026-04-17, Zenodo DOI [10.5281/zenodo.19634864](https://doi.org/10.5281/zenodo.19634864).
- **v2** — synchronization pass 2026-04-21, superseding v1. Load-bearing derivations unchanged; propagation failures fixed, publication-grade displays added, Coherence-Principle integration completed.

## v2 Changelog (2026-04-21)

**Tier A — load-bearing propagation (S1):**
- $\xi = 1/6$ canonicalized to *three complementary perspectives on a single geometric fact* (App A §app:xi authority) across Ch 0, App D, and cross-volume references — the "seven convergences" drift retired.
- $N_g = 3$ canonicalized to *algebraic maximum* (App B S6 authority) across Ch 4 and App D — the "four algebraic proofs" overclaim retired.
- Prediction registry set to **15 = 7 structural + 8 parametric** (App B authority) monograph-wide.
- $C_{KK} = (1.64 \pm 0.33) \times 10^{-4}$ set canonical at App D Tier 2; Ch 2 §2-conclusions 0.51 corrected.
- Benchmark proliferation labelled by tier with weighted-mean $\zeta_0 = 0.016 \pm 0.002$, $w_0 = -0.990$ as the single canonical summary number.

**Tier B — presentation and notation (S2, S4):**
- Ch 0 notation section with master table ($\xi / C_{GB} / \varepsilon_1 / \varepsilon_2 / \varepsilon / \hat\alpha / \zeta_0 / w_0 / C_{KK}$).
- Conditional-caveat fboxes for P4 (radion), P5 (0νββ), P6 (sterile ν), P8 (LISA) in App B — mirroring Ch 5 Channel 5 template.
- Ch 5: $\varepsilon_2$ suppression tightened to explicit ≤5%; Evasion 3 heading fix; $c_s$ matter-dominated floor rounding 4.8c → 4.6c.

**Tier C — publication-grade additions (S3):**
- App D: reproducibility manifest (repo URL, Zenodo DOI, deps, tolerance discipline).
- App D: LISA SNR Monte Carlo figure (`fig10_lisa_snr_mc.{py,pdf,png}`, 1000 samples, Caprini scaling, two regimes).
- App D: Radion potential scan figure (`fig11_radion_potential_scan.{py,pdf,png}`).
- App D: SymPy verification subsection for $C_{GB} = 2/3$.
- App D: AS-exclusion promoted to `\section` with falsifiability hook.
- App B: seven-model DE fingerprint comparison table.
- Ch 5: speculative scalar-response note relegated and fbox'd off-pipeline.

**Coherence-Principle integration (S5):**
- App E factor-of-3 gap reframed as *candidate inspection-depth ceiling* with dual reading and deliberate hedge.
- App D structured apophaticism split into theory-scope vs access remainder classes.
- App D stream scope audit labelling every derived quantity (generic / this-stream / saturation).
- App D structural observation on the radion barrier-thinness with three explicit scope-limits.
- Ch 0 philosophical frame section forward-referencing Anchor DOI [10.5281/zenodo.19634474](https://doi.org/10.5281/zenodo.19634474).
- Ch 5 Conclusions: recursive decomposability paragraph on the spectral chain.

## Layout

- `monograph/` — LaTeX sources (`chapter0`–`chapter5`, appendices, bibliography). Build with `python compile_book.py` or `xelatex meridian_monograph.tex`.
- `drafts/` — In-progress drafts and working chapters.
- `figures/` — Figures used in the monograph.

PDF is not in this repo (per `.gitignore`). Build locally or download from Zenodo.

Computational substrate (244 scripts across 10 physics domains) lives in `Technical-Work/Meridian/scripts/`.

## Citation

v1 (superseded): Iggulden-Schnell & Clawd, *Project Meridian: A Self-Tuning Cosmology from 5D Warped Geometry and Noncommutative Spectral Action*, Zenodo 10.5281/zenodo.19634864 (2026).

v2: forthcoming — citing v1 as supersedes.
