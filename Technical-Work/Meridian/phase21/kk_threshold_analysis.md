# KK Threshold Corrections to sin^2(theta_W): Analysis

**Date:** 2026-03-23 (midday creative drive)
**Status:** Complete. Prediction CONFIRMED: KK thresholds can't close the 12% gap.
**Script:** `kk_threshold_sin2tw.py`

## Question

Does the KK tower on RS₁ produce gauge-dependent threshold corrections that shift sin²θ_W from 0.207 (NCG prediction) toward 0.2312 (measured)?

## Answer: No.

KK threshold corrections at leading (one-loop, planar) order preserve the gauge coupling ratio that determines sin²θ_W. The 12% gap requires physics beyond leading-order perturbative RS-NCG.

## Reasoning

### The hierarchy of corrections

| Level | Effect | Gauge-dependent? | Size | Included in Phase 18? |
|-------|--------|-------------------|------|----------------------|
| Tree-level spectral action | a₁ = a₂ = a₃ (T1) | NO (algebraic) | O(Λ²) | Yes |
| SM zero-mode RG | Different b_i | YES | O(ln Λ/MZ) ~ 30-60 | Yes |
| KK threshold (leading) | Same ratio b₁/b₂ | YES but same ratio | 60× SM running | N/A (see below) |
| Non-planar KK loops | Different color structure | YES, different ratio | Unknown | No |
| Instanton/resurgence | C₂(G_i)-dependent | YES | Unknown | No |
| String thresholds | Flux-dependent | YES | Unknown | No |

### Why KK thresholds don't change sin²θ_W

The Weinberg angle at MZ depends on the RATIO of inverse couplings:

  sin²θ_W = (3/5) · (1/α₂) / ((3/5)(1/α₂) + 1/α₁)

Starting from T1 (α₁ = α₂ = α₃ at Λ), the ratio at MZ is determined by the relative running:

  1/α₁(MZ) - 1/α₂(MZ) = (b₁ - b₂)/(2π) × [total logarithmic integral]

where the "total logarithmic integral" includes SM running + KK threshold steps.

The KK tower amplifies the total running by a factor ~60 (for 200 modes between 3 TeV and 10^13 GeV). But it amplifies BOTH the numerator and denominator of sin²θ_W equally, because each KK level has the SAME beta function structure as the SM (same particle content, same gauge representations).

Formally:

  sin²θ_W = 3/8 × 1/(1 + (b₁-b₂)/(b₁+5b₂/3) × [total log] / [common 1/α at Λ])

The KK modes increase [total log] but don't change the ratio (b₁-b₂)/(b₁+5b₂/3). The common value 1/α(Λ) also increases (from the spectral action's f₂Λ² factor). The NET effect on sin²θ_W cancels.

### The double-counting trap

Naively adding KK threshold corrections on top of the spectral action double-counts: the tree-level spectral action already sums over ALL eigenvalues of D (including KK modes). The KK modes enter the heat kernel expansion through terms like ∫dy e^{-4ky} Tr_F(Q_i²), which gives a₁ = a₂ = a₃ (T1). Adding them again at one loop produces absurd results (1/α₂ → -1765 in the numerical test).

The correct procedure: the spectral action gives the tree-level effective action. The one-loop correction is the PATH INTEGRAL around this vacuum, using the full KK-dressed propagators. This one-loop correction includes:
- Planar diagrams: reproduce the standard RG with KK thresholds (already in tree level)
- Non-planar diagrams: NEW gauge-dependent corrections not captured by the spectral action

### What breaks the ratio

To change sin²θ_W, we need a mechanism that changes the RATIO (b₁-b₂)/(b₁+5b₂/3). Four known candidates:

1. **Non-planar one-loop diagrams (21A.2):** The non-planar color structure in qq̄ → γ + gluon at one loop entangles the gauge group factors differently from the planar structure. On the RS background, the KK mode sum in non-planar diagrams involves different profile overlaps. This is the MOST TRACTABLE candidate — it's a standard (if tedious) Feynman diagram calculation.

2. **Warp-dependent gauge localization (21A.1 open subtlety):** If different gauge fields have different bulk mass parameters (from flux backgrounds or non-minimal couplings to the warp factor), their KK profiles differ, and the threshold corrections become gauge-dependent in a new way. This is what F-theory provides (Path 2).

3. **Non-perturbative gauge effects (21A.4):** Instanton corrections to the gauge kinetic function depend on C₂(G_i), which differs for U(1), SU(2), SU(3). On the RS background, the instanton action is warp-factor-dependent, potentially unsuppressed at the IR brane. The fluctuation determinant is gauge-dependent.

4. **String threshold corrections (21A.3, 21B.2):** In the F-theory or heterotic embedding, gauge-dependent threshold corrections arise from the compactification geometry (flux backgrounds, Wilson lines, moduli-dependent gauge kinetic functions). These are external to the spectral action framework.

## New result: complete classification of gauge coupling corrections

The 12% gap CANNOT come from:
- Tree-level spectral action (T1, algebraic)
- Heat kernel expansion to any order (T12)
- Exact vacuum spectral action (toy model result)
- Leading-order KK thresholds (this analysis)
- Twisted spectral triples (21A.1, eliminated)
- KK Schwinger tunneling (21A.7, eliminated)

The 12% gap CAN potentially come from:
- Non-planar KK loops (21A.2, untested)
- Warp-dependent gauge localization (F-theory/string flux)
- Non-perturbative gauge field path integral (resurgence/instantons)
- String threshold corrections (heterotic/F-theory)

## What this changes for Phase 21

**21A.2 is elevated.** Non-planar one-loop is now the most tractable remaining candidate. It's a specific Feynman diagram calculation that could be done numerically.

**21A.4 (resurgence) is refined AGAIN.** It's not about the vacuum spectral action (exactly universal), not about KK thresholds (same ratio), but about the gauge field PATH INTEGRAL — specifically the fluctuation determinant around non-perturbative saddles.

**21B.7 (instanton) remains central.** The RS instanton action and its gauge dependence.

**Path 2 (string embedding) is the cleanest route.** If the 12% is from flux-dependent gauge localization, it's a PREDICTION of the specific string compactification, not a free parameter.

## Files

- Computation: `kk_threshold_sin2tw.py`
- This analysis: `kk_threshold_analysis.md`
- Exact spectral action: `exact_spectral_action_results.md`
- T12 proof: `warp_factor_gauge_coupling.md`
