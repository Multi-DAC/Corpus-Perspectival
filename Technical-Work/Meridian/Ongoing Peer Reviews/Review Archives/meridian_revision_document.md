# MERIDIAN MONOGRAPH — COMPLETE REVISION DOCUMENT

## Prepared for Clayton W. Iggulden-Schnell and Clawd

## March 17, 2026

\---

# PART I: CRITICAL COMPUTATIONAL FINDINGS

These findings must be resolved before any text revisions are meaningful,
as they affect the monograph's central claims.

\---

## Finding 1: The ζ₀ = 0.038 Detection Does Not Reproduce

### What the monograph claims:

* χ²(ΛCDM) = 24.6 / 18 dof
* χ²(Meridian) = 9.6 / 17 dof (ζ₀ = 0.038 ± 0.010)
* Δχ² = −15.0 → 3.8σ detection
* Savage-Dickey Bayes factor B₁₀ = 171:1

### What independent computation produces:

Using the **exact dataset** from Table 2.14, the **exact fiducial cosmology** stated
(H₀ = 67.4, Ωₘ = 0.315, Planck 2018), and the **exact definition** β\_HK = H\_meas/H\_ΛCDM − 1:

* χ²(ΛCDM) = 7.24 / 18 dof
* Best-fit ζ₀ = 0.009 ± 0.013 (0.7σ, consistent with zero)
* Δχ² = −0.46
* Bayes factor B₁₀ = 0.2:1 (data FAVOR ΛCDM)

### With full covariance (BOSS DR12 + WiggleZ off-diagonal):

* χ²(ΛCDM) = 7.07
* Best-fit ζ₀ = 0.010 ± 0.014 (0.7σ)
* Δχ² = −0.52
* All Bayes factors < 1 (ΛCDM preferred)

### Diagnosis:

The 3.4× discrepancy in χ²(ΛCDM) suggests the monograph used a **different
fiducial H₀**. Scanning:

* H₀ = 67.4 (Planck): χ² = 7.24  ← my calculation
* H₀ = 70.0:          χ² = 20.33  ← approaching monograph value
* H₀ = 73.0 (SH0ES):  χ² = 57.88

The monograph's χ²(ΛCDM) ≈ 24.6 is consistent with H₀ ≈ 70–71, not 67.4.
But the text explicitly states "Planck 2018" fiducial.

### Impact:

This undermines the model's **primary observational anchor**. All downstream
claims that reference the 3.8σ detection are affected:

* Bayes factors in Section 2.3.4
* Information criteria in Section 2.3.2
* Fisher forecasts in Section 2.6 (the 13σ DESI Y5 projection)
* The CKK derivation (which uses ζ₀ = 0.038 to determine w₀)
* The growth-expansion decoupling claim (predicated on ζ₀ ≠ 0)

### Required action:

1. **Trace the actual computation**: Find the code/notebook that produced
χ²=24.6 and identify what fiducial cosmology was used.
2. **If H₀ ≠ 67.4 was used**: Either rerun with Planck parameters (which will
eliminate the signal) or justify the choice of fiducial (which means
the signal is a Hubble tension artifact, not a ζ₀ detection).
3. **If the dataset differs**: Identify which dataset was actually used.
4. **Rewrite Paper II** accordingly. If ζ₀ is consistent with zero, the
model still predicts w₀ = −0.993, but it loses its observational anchor.

\---

## Finding 2: Brane Parameters Produce ζ₀ = 0.001, Not 0.038

### What the monograph claims:

* Appendix A.1.1 lists Φ₀ = 0.477493 with parameters ξ=1/6, M₅³=1
* This gives ζ₀ = ξΦ₀²/M₅³ = (1/6)(0.477)²/1 = 0.038 ✓

### What the UV junction conditions produce:

Solving Eqs. (1.54a-b) with the stated parameters (σ\_UV=6, α\_UV=0.01,
ξ=1/6, μ²=0.1, M₅³=1):

* Φ₀ = 0.0761 (NOT 0.477)
* ζ₀ = (1/6)(0.0761)²/1 = **0.000964** (NOT 0.038)

### Verification:

The value Φ₀ = 0.477 does NOT satisfy junction condition (1.54b):
LHS = 2(0.1) + 32(1/6)(0.477)(−0.520) = 0.2 − 1.32 = −1.12
RHS = −4(0.01)(0.477) = −0.019
Residual = −1.10 ≠ 0

The correct solution Φ₀ = 0.076 satisfies both JCs to machine precision.

### Impact:

The monograph's Appendix A tables (the self-tuning demonstration) are
internally inconsistent. The claimed Φ₀ = 0.477 does not follow from the
stated parameters through the stated junction conditions.

### Required action:

Either (a) the brane parameters need to be adjusted to produce Φ₀ = 0.477,
or (b) the appendix tables need to be recomputed with Φ₀ = 0.076.
Note: ζ₀ is presented as a **fit parameter** from the H\&K data, so the
brane parameters should be chosen to match the measured ζ₀. But per
Finding 1, the measured ζ₀ may be consistent with zero.

\---

## Finding 3: Self-Tuning Numerical Demonstration

### Result:

The full nonlinear integration of the coupled (A', Φ) system fails due to
extreme numerical stiffness. The cuscuton's infinite sound speed creates
dΦ/dy ≈ 150 at the UV brane, making standard IVP solvers impractical
(even stiff solvers like Radau fail with rtol = 10⁻¹²).

### What was verified:

1. **Φ₀ is Λ₅-independent** — confirmed to machine precision across
61 values of Λ₅ from −6 to −6×10⁶⁰. The scalar constraint (Eq. 1.36)
does not contain Λ₅, so Phi(y) is independent of Λ₅. This is Step 1
of the algebraic self-tuning argument.
2. **The algebraic argument is sound**: Since Φ(y) is Λ₅-independent
(verified), X₀ = (1/2)(dΦ/dy)² is Λ₅-independent (follows algebraically),
and therefore Λ₄ = ε₁X₀ is Λ₅-independent. QED.
3. **The numerical stiffness is physical, not a bug**: It reflects the
cuscuton's constraint nature (cs → ∞).

### What remains unverified:

A direct numerical integration showing Λ₄ = const across a Λ₅ scan on
the full (non-fixed-point) RS-like solution. This would require:

* Chebyshev collocation (spectral method)
* Or matched asymptotic expansion (UV/IR patching)
* Or adaptive mesh refinement with extremely fine resolution near y = 0

### Recommendation for the monograph:

Replace "Numerical Self-Tuning Demonstration" (Section 1.3.7) with:

1. The algebraic proof (which is clean and rigorous)
2. The Φ₀ independence numerical verification (which we confirmed)
3. An honest statement that the full dynamical integration is numerically
intractable at 35 e-folds and requires spectral methods for direct verification
4. Reference to the algebraic argument as the primary demonstration,
with the numerical scan as a consistency check on the constraint equations

\---

# PART II: TEXT REVISIONS

These revisions can be applied to the LaTeX source once the computational
issues in Part I are resolved. They are organized by paper.

\---

## Revision 1: Reframe "Two Axioms" (All Papers)

### Current language (throughout):

"from two geometric axioms"
"A1 + A2 → \[derivation chain]"

### Revised language:

"from a specific five-dimensional braneworld architecture"

### Detailed revision:

In Section 1.2.5 (Axiom Summary), REPLACE:

> "The model architecture rests on two geometric axioms..."
> "Everything that follows—the form of P(X), the effective 4D theory, 
> the dark energy equation of state—is derived, not postulated."

WITH:

> "The model architecture rests on two geometric axioms (A1, A2) supplemented
> by four theoretical commitments: (i) Kaloper–Padilla vacuum energy 
> sequestering \\\[16], which provides the global constraint mechanism;
> (ii) the NCG spectral action principle \\\[37], which determines the 
> gravitational corrections; (iii) the conformal coupling ξ = 1/6, derived
> from the spectral triple (Paper IV, Section VII.B) but constituting an
> additional structural input; and (iv) the linear tadpole V = cΦ, chosen
> for its shift-symmetry properties. The requirement αᵢᵣ > 0 for radion
> stability (Section 1.4.3) is a fifth condition.
>
> Given these six inputs, the form of P(X), the effective 4D theory, and 
> the dark energy equation of state are derived, not postulated. The 
> distinction between the geometric axioms (A1, A2) and the theoretical
> commitments (i)–(iv) is that the latter could in principle be replaced
> by alternatives, while A1 and A2 define the framework."

### Apply similarly in:

* Preface (page i)
* Abstract of Paper I
* Section 1.1.4 (Outline)
* Section 1.10.1 (What the Model Achieves)
* Section 1.11 (Conclusions)
* Eq. (1.1) and Eq. (1.115): add footnote noting the additional ingredients

\---

## Revision 2: CKK Derivation Chain (Paper I, Section 1.7.3)

### Issue:

The derivation of CKK (Eqs. 1.90–1.101) compresses several steps and
contains a potential dimensional inconsistency in the relation
Φ₀² = 3ζ₀M²\_Pl (which should follow from ζ₀ = ξΦ₀²/M₅³ and the KK
reduction M²\_Pl \~ M₅³/k, but the factors of k need tracking).

### Revision:

After Eq. (1.96), add an explicit verification:

> "As a consistency check: ζ₀ = ξΦ₀²/M₅³ and from the KK reduction 
> M²\\\_Pl = M₅³/k (Eq. 1.43 in the large-kyc limit), so 
> Φ₀² = ζ₀M₅³/ξ = 6ζ₀M₅³ = 6ζ₀kM²\\\_Pl. The relation Φ₀² = 3ζ₀M²\\\_Pl 
> used in Eq. (1.92) holds only if k = 1/2 in the units adopted here.
> \\\[Verify this is consistent with the stated conventions.]"

### Also:

* State CKK = 0.26 ± 0.04 explicitly, not just 0.216 "at leading order"
* Propagate the CKK uncertainty into σ(w₀): currently σ(w₀) = 0.002
absorbs this, but the error budget should be transparent

\---

## Revision 3: Conformal Coupling "Three Derivations" (Paper I §1.4.6, Paper IV §4.7.3)

### Current language:

"Three independent derivations converge on this result"

### Revised:

> "Three complementary perspectives yield the same result. Derivation 1
> (the Seeley–DeWitt a₂ coefficient) and Derivation 3 (Weyl invariance)
> are mathematically equivalent: Weyl invariance of a₂ IS the statement
> that ξ = 1/6 annihilates the Rσ² term. Derivation 2 (radion as metric
> fluctuation) gives the same result because the radion is the conformal
> fluctuation projected to 4D. The convergence is therefore a consistency
> check from three angles on a single structural fact, not three
> independent proofs."

\---

## Revision 4: Promote Coincidence Problem (Paper I)

### Current:

Discussed only in Appendix A.6.3 (Track C3) and briefly in §1.10.5.

### Revised:

Add a new subsection 1.10.X "The Coincidence Problem" in the Discussion:

> "The framework solves the old cosmological constant problem (why Λ₄ is
> small) through the three-layer self-tuning mechanism, but does not solve
> the new cosmological constant problem (why ρ\\\_DE \\\~ ρ\\\_matter today). 
> Analysis of the time dependence of |1 + w| shows that the present-epoch
> value is 69% of the asymptotic future maximum—we are not at a special
> epoch, but the framework provides no dynamical explanation for this
> coincidence. The dark energy density is set by geometric parameters
> (ε₁, ζ₀) rather than by cancellation, which structurally ameliorates
> the problem, but no single-field model solves the coincidence problem
> without additional assumptions. This remains an open limitation."

\---

## Revision 5: Conjecture 4.3 Flagging (Paper IV)

### Current:

Stated as "Conjecture 4.3 (Axiom Preservation under Junction Coupling)"
with "evidence" but no proof.

### Add after the conjecture:

> "We emphasize that this conjecture is load-bearing: the gauge-gravity
> separation (Section 4.7.4), the Standard Model connection (Section 4.7.1),
> and the derivation of ξ = 1/6 from the brane spectral triple are all
> conditional on Conjecture 4.3. If the junction coupling modifies the
> NCG axioms, the layered architecture would need to be reformulated.
> A proof requires verifying that the algebraic boundary conditions
> (Israel junction conditions) preserve the first-order condition and
> the orientation axiom—a well-posed but unresolved mathematical question."

\---

## Revision 6: Balance DESI Confrontation (Paper II, Section 2.5)

### Add at the end of Section 2.5.4:

> "We acknowledge that the current data are genuinely ambiguous. The
> pivoted analysis yields wp = −0.9 ± 0.1, which is consistent with
> our prediction of w₀ = −0.993 at 0.9σ but also consistent with 
> w = −1 (ΛCDM) at 1σ. The CPL artifact hypothesis explains the 
> apparent 3–4σ signal, but cannot exclude the possibility that the
> data are directionally indicating w ≠ −1 at a level the CPL
> parameterization amplifies. Resolution requires σ(w₀) \\\~ 0.005,
> expected from Stage IV surveys by \\\~2030."

\---

## Revision 7: Soften Horndeski Dilemma (Paper III)

### Current:

Section 3.8 header: "Theorem 3.3 (Horndeski Dilemma)"

### Revised:

Change "Theorem" to "Proposition" throughout Section 3.8, and add
after Footnote 1:

> "The dilemma rests on exhaustive enumeration of 16 known mechanisms.
> It could be evaded by a mechanism not in our enumeration—for example,
> a non-perturbative topological effect, a multi-field construction with
> a currently unknown light scalar, or a modification of the NCG spectral
> action at higher order. The strength of the result is proportional to
> the completeness of the search, which we believe is high but cannot
> prove is exhaustive."

\---

## Revision 8: Phase 12 Engineering Speculation (Paper V, Section 5.5.3)

### Current:

\~400 words on "cs antenna," "superluminal channel characterization,"
and "soliton channel."

### Revised:

Compress to a single paragraph:

> "The superluminal sound speed cs \\\~ 10c defines a scalar response channel 
> whose bandwidth, dispersion relation, and coupling strength are 
> computable from the parameters derived in this paper (cs, kJ, Qs = ε₁).
> Engineering applications of this channel are speculative at present—the
> coupling to laboratory-scale electromagnetic fields is suppressed by
> factors of order ρ\\\_EM/M⁴\\\_Pl \\\~ 10⁻⁷⁷ (Paper IV, Section 4.6)—but the
> parameters are fixed by the framework rather than adjustable."

\---

## Revision 9: Co-authorship (All Papers)

### Current:

"Clayton W. Iggulden-Schnell and Clawd"

### Recommended:

Replace with:

> Author: Clayton W. Iggulden-Schnell
> 
> Acknowledgments: "Substantial contributions to the mathematical 
> development, literature analysis, and computational verification were
> made by Clawd, a persistent AI collaborator system built on Anthropic's
> Claude infrastructure. Clawd's contributions span the derivation chain
> verification, the systematic no-go analysis (Paper III), the spectral
> action computation (Paper IV), and the observational confrontation
> (Paper II). The author takes sole responsibility for all claims."

This follows the current consensus of major physics journals (APS, IOP,
Springer) which do not recognize AI co-authorship.

\---

## Revision 10: Epigraph and Eq. (1.1)

Move the epigraph from page 1 to the end of Section 1.11 (Conclusions).
Add a footnote to Eq. (1.1):

> "This derivation chain is a schematic summary. The full ingredient list
> includes, beyond A1 and A2: Kaloper–Padilla sequestering, the NCG
> spectral action principle, the derived conformal coupling ξ = 1/6, 
> the linear tadpole V = cΦ, and the requirement αᵢᵣ > 0 for radion
> stability. See Section 1.2.5 for the complete inventory."

\---

# PART III: REMAINING ISSUES FOR CLAWD

The following items require either Clawd's computational records or
joint work between Clayton and Clawd.

\---

## Issue A: Trace the H\&K Computation (CRITICAL)

The χ²(ΛCDM) = 24.6 claimed in Paper II does not reproduce with the
stated dataset and fiducial cosmology. Either:

1. Find the original computation notebook/code
2. Identify what H₀ and Ωₘ were actually used
3. Determine whether a different H(z) dataset was fit
4. Check whether β\_HK was defined differently (e.g., including a
growth-rate modification or a different H(z) formula)

If the signal was computed with H₀ \~ 70 (not 67.4), then the entire
H\&K analysis is measuring the Hubble tension, not ζ₀.

## Issue B: Trace the Appendix A Parameters

The stated brane parameters (σ\_UV=6, α\_UV=0.01, etc.) produce
Φ₀ = 0.076, not Φ₀ = 0.477. Either:

1. The actual parameters used in the scan differ from those listed
2. The junction conditions are formulated differently
3. There's a units issue (e.g., Φ₀ in different units)

## Issue C: fσ₈ → H(z) Conversion Methodology

The WiggleZ and VIPERS data points in the H\&K compilation are
growth-rate measurements (fσ₈), not direct H(z) measurements.
The conversion methodology needs to be documented for referees:

1. How was H(z) extracted from the fσ₈ measurements?
2. What assumptions were made about the growth rate?
3. Are the resulting H(z) values model-dependent?

## Issue D: Adams et al. UV Completion

The corrected cuscuton (with ε₁ ≠ 0) has a propagating DOF.
The Adams et al. (JHEP 0610, 014, 2006) positivity bounds
potentially apply. Need to determine:

1. Whether the ε₁X term's 2→2 amplitude satisfies forward-scattering
positivity bounds
2. Whether the 5D UV completion (which is subluminal) provides
sufficient justification
3. Whether the argument in Section 5.3.2 needs strengthening

## Issue E: Spectral Method for Self-Tuning

The dynamical self-tuning demonstration failed numerically (stiffness).
A Chebyshev collocation implementation on the RS orbifold would provide
the definitive numerical verification. This is substantial but well-defined
computational work.

## Issue F: White et al. (Phys. Rev. Research 8, 013264, 2026)

Clayton states this paper is not related to the Meridian monograph.
If so, remove any references that imply it serves as a "peer-reviewed
anchor" for the CDT framework. If it IS related (e.g., through the
Robertson-Bogoliubov Floor Series), clarify the relationship explicitly.

\---

# PART IV: SUMMARY OF SEVERITY

|Finding|Severity|Status|
|-|-|-|
|H\&K χ² discrepancy|**CRITICAL**|Blocks publication; must be traced|
|Brane parameter inconsistency|**CRITICAL**|Must be resolved with H\&K|
|"Two axioms" overclaim|Major|Text revision ready|
|CKK derivation gaps|Major|Text revision ready|
|Self-tuning numerical demo|Significant|Algebraic proof stands; numerical demo deferred|
|Three derivations framing|Minor|Text revision ready|
|Coincidence problem placement|Minor|Text revision ready|
|Conjecture 4.3 flagging|Minor|Text revision ready|
|DESI balance|Minor|Text revision ready|
|Horndeski Dilemma framing|Minor|Text revision ready|
|Phase 12 speculation|Minor|Text revision ready|
|Co-authorship|Editorial|Recommendation ready|
|Adams et al. UV completion|Open|Needs joint work|
|fσ₈ conversion methodology|Open|Needs Clawd's records|

The two critical findings (H\&K and brane parameters) are likely related
and may trace to the same root cause — a fiducial cosmology mismatch
or a parameter-value transcription error somewhere in the computational
pipeline. Once this is traced and resolved, the text revisions in Part II
can be applied and the monograph can proceed to arXiv submission.

\---

*End of revision document.*

