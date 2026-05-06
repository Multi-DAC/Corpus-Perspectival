# PRL Letter — Shortened Abstract Draft

**Problem:** Current abstract is ~1109 characters (rendered). PRL limit is ~600.

**Strategy:** Move sound speed, threshold ratio, eigenvalue details, and mechanism descriptions to the body (all already present there). Keep: what we did, the key result (C_GB = 2/3), the prediction (w₀, w_a), and the significance (UV completion).

---

## Shortened Abstract (~571 chars rendered)

```latex
\begin{abstract}
We derive the dark energy equation of state from the spectral action
on a five-dimensional Randall--Sundrum orbifold with del~Pezzo
internal geometry.  The Gauss--Bonnet coefficient $\CGB = 2/3$ is
determined analytically, leaving one free cosmological parameter---the
Goldberger--Wise scaling dimension $\epsGW$---fixed by DESI~BAO data
at $0.275^{+0.072}_{-0.106}$.  This yields $w_0 = -0.830$ and
$w_a = 0$ (exactly, from the static warp geometry).  The framework
provides a UV completion of quadratic quantum gravity in which all
$R^2$ coefficients are geometric consequences, not free parameters.
\end{abstract}
```

**What was removed:**
- "spectral action principle" → "spectral action" (saves 10 chars)
- Fermat cubic parenthetical (in body)
- Sound speed c_s ~ 12-15c (in body, §3)
- Threshold correction ln(3)/√2 (in body, §4)
- Eigenvalue λ₁ = 1.461 and Lichnerowicz bound (in body, §4)
- "Every other coefficient..." (implied by "one free parameter")
- "cuscuton-type dark energy sector" (in body, §3)

---

## 3.8σ Claim — Needs Review

The letter (line 173-174) says:
> "This is testable by DESI Year 5 at 3.8σ against the w₀-w_a posterior."

**Issue:** The derivation of 3.8σ is not shown. Possible interpretations:

1. **Current tension with DESI DR2 CPL fit:** If DESI DR2 gives w_a ≈ -0.75 ± 0.20, then w_a = 0 is at 3.75σ. But the actual DESI DR2 numbers vary by analysis (w_a = -0.58 ± 0.28 in some fits).

2. **Projected DESI Y5 sensitivity:** With σ(w_a) projected at ~0.15 for Y5, and the current best-fit w_a ≈ -0.6, the detection significance would be ~4σ. But this conflates current central value with future precision.

3. **The correct statement might be:** "DESI Year 5, with projected σ(w_a) ~ 0.15, will test the w_a = 0 prediction against the current DESI DR2 CPL central value at >3σ."

**Recommendation:** Either:
- (a) Cite the specific DESI DR2 w_a posterior from which 3.8σ is computed, or
- (b) Soften to "testable at >3σ by DESI Year 5" without the precise 3.8, or
- (c) Compute 3.8σ explicitly and add a brief justification (e.g., "using the DESI DR2 CPL posterior w_a = -0.XX ± 0.XX")

**Clayton:** Which approach do you prefer? I can compute the exact significance if you tell me which DESI DR2 analysis to use.

---

*Drafted by Clawd, April 9, 2026, 6:15 AM PST (dream drive)*
