# Meridian Monograph — LaTeX Compilation

**Compiled:** March 17, 2026
**Total:** 6,076 lines across 7 files

## Files

| File | Lines | Content |
|------|-------|---------|
| `meridian_monograph.tex` | 163 | Main book file (preamble, custom commands, \input statements) |
| `chapter1_foundation.tex` | 1,550 | Paper I: Self-Tuning from 5D Warped Geometry (96 eqs, 70 refs) |
| `chapter2_observational.tex` | 1,044 | Paper II: Observational Confrontation (24 eqs, 49 refs) |
| `chapter3_nogo.tex` | 918 | Paper III: No-Go Theorems (28 eqs, 44 refs) |
| `chapter4_ncg.tex` | 1,116 | Paper IV: NCG Spectral Geometry (67 eqs, 47 refs) |
| `chapter5_sound_speed.tex` | 621 | Paper V: Sound Speed of DE (30 eqs, 30 refs) |
| `appendix_computations.tex` | 664 | Phase 11C/D Computational Results |

## Compilation

```bash
cd monograph/
pdflatex meridian_monograph.tex
pdflatex meridian_monograph.tex  # twice for TOC/refs
```

## Notes

- Each chapter has its own `\begin{thebibliography}` with namespace-prefixed keys (ch1:, ch2:, etc.)
- Equation labels follow `eq:N-XX` convention (N = chapter number)
- Custom commands defined in main file (\wz, \zz, \eps, \ahat, \CGB, \CKK, etc.)
- Theorem environments: theorem, proposition, corollary, conjecture, definition, scalingrelation
- Source papers (markdown): `../phase11/paper_*_draft.md`
- D6 revision checklist not yet applied — `../phase11d/d6_revision_summary.md`
