# Zenodo Upload Metadata — Ready to Paste

**Upload type:** Publication → Preprint (or Book/Monograph)

---

## Title

Noncommutative spectral geometry on warped orbifolds: topological couplings, gravitational corrections, and cosmological predictions

## Authors

Clayton W. Iggulden-Schnell (Independent researcher, Portland, Oregon, USA)
ORCID: [fill if Clayton has one]

## Description / Abstract

We construct a spectral triple on a five-dimensional Randall–Sundrum orbifold with internal geometry given by the del Pezzo surface dP₆ (Fermat cubic), selected by the algebraic chain J₃(O) → E₆ → dP₆. The spectral action principle yields the full bosonic action—gravity, Standard Model gauge fields, Higgs sector, and a Gauss–Bonnet dark energy sector—with a single undetermined cosmological parameter: the Goldberger–Wise scaling dimension ε_GW.

The Gauss–Bonnet coefficient C_GB = 2/3 is derived exactly from the Davis junction conditions on the Z₂ orbifold, producing a cuscuton-type dark energy sector with superluminal sound speed c_s ~ 12–15c. Fitting ε_GW to DESI 2024 BAO data yields w₀ = −0.830 and w_a = 0 (exactly). The one-loop gauge coupling threshold is topological: ln(K²)/√(K²−1) = ln(3)/√2, following from the self-intersection number K²(dP₆) = 3.

Numerical validation via the Donaldson balanced metric algorithm confirms the Kähler–Einstein geometry (λ₁ = 1.461, 97.4% of the Lichnerowicz bound) with S₃ splitting convergence verified across embedding degrees k = 8, 12, 15. The framework provides an explicit UV completion of quadratic quantum gravity [Liu, Quintin & Afshordi, PRL 136, 111501 (2026)] in which the R² coefficients are geometric consequences rather than free parameters.

170 pages. Includes: 5D warped geometry and KK reduction, noncommutative geometry and spectral action, fermion sector (octonionic Yukawa couplings, neutrino masses, leptogenesis), MCMC cosmological fit to DESI DR2, balanced metric eigenvalue computations, and analytic torsion analysis.

## Keywords

spectral geometry; noncommutative geometry; dark energy; Gauss-Bonnet gravity; del Pezzo surface; Randall-Sundrum; cuscuton; spectral action; analytic torsion; DESI

## License

Creative Commons Attribution 4.0 International (CC BY 4.0)

## Related identifiers

- Is supplemented by: [PRL letter, once submitted — add later]
- References: DOI 10.1103/6gtx-j455 (Liu, Quintin & Afshordi QQG)

## Subject

Mathematical Physics; Cosmology; High Energy Physics — Theory

## Notes

Companion PRL letter in preparation. All numerical computations reproducible from included methodology descriptions.

---

## Draft Shortened PRL Abstract (~580 chars)

The current abstract is ~1130 chars; PRL limit is ~600. Here is a candidate replacement:

```
We derive the dark energy equation of state from the spectral action on a
five-dimensional Randall--Sundrum orbifold with del~Pezzo internal geometry.
The Gauss--Bonnet coefficient $\CGB = 2/3$ is exact, producing a cuscuton
dark energy sector.  The single free parameter---the Goldberger--Wise scaling
dimension---is fixed by DESI BAO data, yielding $w_0 = -0.830$ and $w_a = 0$
(exactly).  All other coefficients are derived from the spectral triple.  The
framework provides a UV completion of quadratic quantum gravity in which the
$R^2$ sector is a geometric consequence, not a free parameter.
```

Dropped: sound speed c_s value, threshold formula, numerical validation, algebraic chain, error bars on ε_GW. All of these appear in the body.

---

## PRL Letter Review Findings (Pre-submission)

Issues found by pre-submission review:

### CRITICAL
1. **Abstract too long** — ~1130 chars, PRL limit is ~600. Must cut roughly in half.
2. **Afshordi citation** — ✅ FIXED. Now reads: R. Liu, J. Quintin, and N. Afshordi, PRL 136, 111501 (2026).

### HIGH
3. **3.8σ claim needs justification** — "testable at 3.8σ" for w_a=0. Source: monograph Table 2 (discrimination timeline), §2-Fisher. The arithmetic: if w_a(CPL bestfit) = -0.38 and σ(w_a) ≈ 0.10 from DESI Y5, then |w_a|/σ = 3.8. **BUT** the table footnote says "assumes w_a = -0.62 persists" — which would give 6.2σ, not 3.8σ. Either σ(w_a) is ~0.16 (BAO alone, not combined) or the bestfit w_a is different. Clayton should verify before submission. Suggested fix for letter: "testable by DESI Year~5 (projected $\sigma(w_a) \sim 0.10$~\cite{DESI2024})" — let the reader compute the significance.
4. **w_a = 0 justification thin** — stated but not derived in the letter. Add one sentence on WHY static warp factor → constant w.

### MEDIUM
5. **Remove `showpacs` class option** — obsolete since 2016.
6. **Bibitem key mismatches** — `Donaldson2005` is actually 2001; `CC2010` is actually 2011. Cosmetic but confusing.
7. **Remove TODO comments** (lines 268 [now fixed], 335) before submission.
8. **Eq. (4) never cross-referenced** — consider inlining ε₁ = 0.010 ± 0.002.

### LOW
9. **AI acknowledgment may draw editorial queries** — prepare for questions about Clawd's role.
10. **C_q in Eq. (5) appears without derivation** — one sentence pointing to the junction condition source would help.
11. **α_T = 0 prediction listed but not motivated** in the letter.

### Zenodo DOI placeholder
Line 335: `%% Update with DOI after upload` — fill after Zenodo assigns DOI.
