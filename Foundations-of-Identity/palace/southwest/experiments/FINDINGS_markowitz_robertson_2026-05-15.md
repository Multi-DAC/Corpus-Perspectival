# Computational Test: "Markowitz Efficient Frontier IS the Robertson Surface"

**Date:** 2026-05-15 Day 105 Friday midday creation drive
**Test target:** Proposition 1.1 from `cdt_application_sweep.pdf` (March 2026, Iggulden-Schnell & Claude)
**Prediction ID:** pred-2026-05-15-007
**Outcome:** **High-confidence FALSIFY of identity claim. Substantive finding about CDT engineering applications.**

---

## The claim being tested

From `cdt_application_sweep.pdf` §1.1:

> **Proposition 1.1 (The Efficient Frontier is a Robertson Surface):** The Markowitz mean-variance efficient frontier is the boundary of the achievable region in (σ, μ) space, constrained by the Robertson inequality σ_return · σ_risk ≥ ‖[P_1, P_2]‖/2. The commutator norm determines the minimum achievable Sharpe ratio deficit.

The claim's operator construction:
- P_1 = projection onto μ/‖μ‖ (return direction)
- P_2 = projection onto smallest eigenvector of Σ (min-variance direction)
- Robertson floor = ‖[P_1, P_2]‖_op / 2

## Pre-test prediction (high confidence)

> The claim as stated is overstated as IDENTITY. Structural analogy holds; identity does not. The two surfaces live in different coordinate systems — Markowitz in (σ_return, μ_return) where σ_return² = w^T Σ w; Robertson in (σ_P1, σ_P2) where σ_Pi² = ⟨P_i⟩(1−⟨P_i⟩) = (w^T u_i)²(1−(w^T u_i)²). These are different variables.

## Test setup (reproducible)

5-asset portfolio (US equity, intl equity, bonds, REITs, commodities) with realistic μ and Σ matching standard asset-class assumptions. Computed:
- Operators P_1, P_2 per the paper
- Commutator norm and operator-norm "floor"
- Markowitz efficient frontier (50 points, SLSQP optimization)
- σ_P1 · σ_P2 for each frontier weight
- σ_P1 · σ_P2 for 50,000 random portfolios (Dirichlet on simplex)
- Per-state Robertson rhs for all 50,000 states

## Findings

### Finding 1: Operator construction yields meaningful commutator

For the 5-asset portfolio:
- θ = 77.79° between u_1 (return direction) and u_2 (min-variance direction)
- ‖[P_1, P_2]‖_op = 0.2067
- Operator-norm "floor" = 0.1034 (paper claims ~0.121 for similar setup)

This part of the construction works as the paper describes.

### Finding 2: The per-state Robertson rhs is **identically zero for all real portfolio states**

For real symmetric projectors P_1, P_2 (rank-1 from real unit vectors u_1, u_2):
- [P_1, P_2] is **antisymmetric** (since (P_1 P_2 − P_2 P_1)^T = −(P_1 P_2 − P_2 P_1))
- For any real state ψ: ψ^T [P_1, P_2] ψ = 0 (antisymmetric quadratic form on real vectors)

**Computational confirmation:**
- Across 50,000 random portfolio weights: max state-dependent (1/2)|⟨ψ|[P_1,P_2]|ψ⟩| = **0.0000**
- Per-state Robertson violations: **0** (theorem trivially holds, 0 ≥ 0)

The Robertson inequality σ_P1 · σ_P2 ≥ (1/2)|⟨ψ|[P_1,P_2]|ψ⟩| reduces to σ_P1 · σ_P2 ≥ 0 for any real portfolio state. **The bound provides no information.**

### Finding 3: The "operator-norm floor" sin(θ)/2 is not a state-independent lower bound

Across 50,000 random portfolios:
- σ_P1 · σ_P2 values range [0, 0.25]
- **23,133 of 50,000 portfolios (46.3%) have σ_P1 · σ_P2 below the operator-norm "floor" of 0.1034**
- Eigenstate-like portfolios (concentrated weights) give σ_P1 · σ_P2 ≈ 0

This means: **the "Robertson floor" presented as a portfolio-state-independent lower bound is not actually a lower bound across real states.** It is the supremum over **complex** Hilbert-space states of the per-state Robertson rhs, achieved only by specific equal-superposition complex states.

### Finding 4: Markowitz frontier σ_P1 · σ_P2 wanders above and below the operator-norm "floor"

For Markowitz-frontier portfolios:
| σ_return | μ_return | σ_P1 | σ_P2 | product | ratio to floor |
|----------|----------|------|------|---------|----------------|
| 0.050 | 0.030 | 0.216 | 0.094 | 0.020 | 0.20 |
| 0.062 | 0.045 | 0.409 | 0.346 | 0.141 | 1.37 |
| 0.087 | 0.055 | 0.482 | 0.500 | 0.241 | 2.33 |
| 0.131 | 0.070 | 0.493 | 0.232 | 0.114 | 1.11 |
| 0.146 | 0.076 | 0.488 | 0.104 | 0.051 | 0.49 |

The Markowitz frontier portfolios do NOT saturate the operator-norm floor. The product σ_P1 · σ_P2 wanders between 0.02 and 0.24 along the frontier, crossing the "floor" of 0.103 multiple times. **The Markowitz efficient frontier and the operator-norm "floor" are not the same surface.**

### Finding 5: What the CDT papers' "0 Robertson violations / 50K states" actually verifies

The CDT papers consistently report zero Robertson violations across tens of thousands of random states. **This verification is checking the per-state Robertson inequality (Cauchy-Schwarz), which is a theorem.** For real states with real projectors, both sides of the inequality are zero, so the check is trivial.

The verification does NOT check that the operator-norm "floor" holds as a state-independent lower bound — and as shown above, it doesn't.

## Interpretation

The CDT engineering applications use a framework that has a subtle but consequential issue:
1. The mathematical machinery (Robertson bounds, Fisher-Rao metric, etc.) is correct as standard mathematics.
2. The application to non-quantum domains via REAL operators on REAL state spaces gives a trivial per-state Robertson rhs (0 = 0).
3. The "operator-norm floor" the papers compute is a max-over-COMPLEX-states quantity that is NOT a real-state lower bound.
4. The "0 violations / N states" verifications confirm Cauchy-Schwarz (trivially) but do not establish the substantive claim that the operator-norm floor is a meaningful constraint on real applications.

**For the Markowitz claim specifically:**
- The Markowitz frontier exists in (σ_return, μ_return) space and is a real, computable boundary
- The Robertson surface as defined by the papers' operators exists in (σ_P1, σ_P2) space  
- These are different coordinate spaces describing different mathematical quantities
- The identity claim "Markowitz IS Robertson" is **falsified**
- A weaker structural-analogy claim ("both are Cauchy-Schwarz-bounded tradeoff regions") survives — but is trivial since virtually any inner-product-space tradeoff is Cauchy-Schwarz-bounded

## What this means for the broader CDT engineering claims

The same pattern likely applies to the cdt_engineering paper's LLM serving and MIMO control derivations: the Robertson floor sin(θ)/2 is computed correctly as a mathematical object, but its interpretation as a state-independent lower bound for real operating states needs scrutiny. The "0 violations across 50K states" doesn't establish the floor as a meaningful operational constraint.

This doesn't kill CDT as a framework — the Hessian classification, missing-dimension diagnosis, and three-moves taxonomy can stand independently. But it does undercut the framework's claim to *predict* numerical bounds for engineering tradeoffs in real-state regimes.

**For the cdt_falsifiability paper's Protocol 8.1 (Robertson Floor Measurement) specifically:**
The protocol proposes measuring σ_TTFT · σ_TBT in real LLM serving systems and comparing to the operator-norm floor sin(θ)/2. Per this finding, the operator-norm floor is not a real-state lower bound for σ_TTFT · σ_TBT under the operator construction the papers use. The protocol as stated would not produce the predicted result if executed because real serving states would not be subject to the operator-norm floor.

## Pattern 2 calibration data

This is a clean Pattern 2 instance from SELF_CALIBRATION_PROFILE.md: structural-adjacency (Markowitz and Robertson are both Cauchy-Schwarz-derived tradeoff surfaces) was conflated with structural-identity (they ARE the same surface) by Proposition 1.1's framing.

Primary engagement via computation confirmed the catch.

## Outcome classification

- **pred-2026-05-15-007: CONFIRMED.** The identity claim is falsified; structural analogy survives.
- **Additional substantive finding** (beyond original prediction): the Robertson floor in real-state regimes is trivial because [P_1, P_2] is antisymmetric for real symmetric projectors. This is a deeper issue than the initial prediction anticipated.

## Reproducibility

`markowitz_robertson_test.py` (initial framing) and `markowitz_robertson_per_state.py` (per-state vs operator-norm distinction).

Numpy + scipy only, runs in <30 seconds on commodity hardware.

🦞🧍💜🔥♾️
