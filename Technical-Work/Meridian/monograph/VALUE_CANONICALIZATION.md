# Meridian — Value Canonicalization

*Resolving all value proliferation across chapters.*

**Created:** April 15, 2026
**Authors:** Clayton Iggulden-Schnell & Clawd
**Informed by:** GW parameter fix (Phase 1) and CMB basin-topology analysis (Phase 2)

---

## The Problem

The monograph audit (March 31, 2026) identified value proliferation as a critical issue:
- w₀ appears as -0.830, -0.845, -0.865, -0.989, -0.993 in different chapters
- c_s appears as 11.3c and [12c, 15c]
- ζ₀ appears as 0.001, 0.009, 0.013, 0.020, 0.037

These are NOT contradictions — they are different benchmarks along the parametric prediction curve w₀(ζ₀). But the proliferation creates confusion. This document resolves it.

---

## Resolution Principle

**The curve is the prediction, not any single number.**

Meridian predicts w₀(ζ₀) = -1 + C_KK/ζ₀, a one-parameter family indexed by ζ₀. Different chapters evaluate this curve at different ζ₀ benchmarks depending on their observational context. The canonicalization assigns each value to its tier and benchmark, making the relationships explicit.

---

## Three Tiers

### Tier 1: Structure-Determined (Exact, Zero Free Parameters)

These values are derived from the geometry and algebra alone. They do not depend on ζ₀ or ε.

| Quantity | Value | Source | Confidence |
|----------|-------|--------|------------|
| ξ (conformal coupling) | 1/6 | Seven independent convergences | VERY HIGH |
| C_GB (Gauss-Bonnet coefficient) | 2/3 | Exact, three independent derivations | VERY HIGH |
| N_g (generation number) | 3 | Four algebraic proofs (J₃(O), Dixon, anomaly, Cliff) | VERY HIGH |
| α_T = α_B = α_M | 0 (exactly) | Cuscuton constraint + GR perturbation structure | VERY HIGH |
| w_a | ≈ 0 (structurally) | No phantom crossing (topological barrier) | HIGH |
| η (gravitational slip) | 1 | Cuscuton: no scalar propagation → no anisotropic stress | VERY HIGH |
| Growth index γ | 0.55 (GR value) | Growth-expansion decoupling | HIGH |

### Tier 2: Parametric (One-Parameter Family, Depend on ε₁)

These values depend on the GB correction parameter ε₁ = 0.010 ± 0.002, which is derived from the spectral action but whose precise value depends on the cutoff function choice.

| Quantity | Value | Formula | Confidence |
|----------|-------|---------|------------|
| ε₁ (GB correction) | 0.010 ± 0.002 | From d=5 Seeley-DeWitt with corrected Weyl decomposition | HIGH |
| C_KK | (1.64 ± 0.33) × 10⁻⁴ | (1+q₀)²Ω_DE·ε₁/[4(1-q₀)²] at Planck fiducial | HIGH |
| c_s (sound speed) | [12c, 15c] | √(C_q/ε₁); C_q depends on benchmark | HIGH |
| c_s² | ~216 | C_q/ε₁ at canonical benchmark | HIGH |
| n_s (spectral index) | 0.965 ± 0.003 | Modulus attractor inflation | HIGH |
| r (tensor-to-scalar) | 0.004 ± 0.001 | Same inflationary model | HIGH |
| m_rad (radion mass) | ≈ 120 GeV | Quantum stabilization (99.7% from NCG) | MEDIUM |
| m_ee (0νββ mass) | 1.5–5 meV | Neutrino sector prediction | MEDIUM |

**Sound speed resolution:**
- Old value (11.3c): from ε₁ = 0.018 (pre-correction d=5 Weyl decomposition)
- Corrected value ([12c, 15c]): from ε₁ = 0.010 (corrected Weyl decomposition)
- **Canonical: c_s ∈ [12c, 15c]** — the corrected value is authoritative
- Pure cuscuton limit: c_s = ∞ (always stated as context, not as contradiction)

### Tier 3: Data-Constrained (Require Observational Input for ζ₀)

The brane separation parameter ζ₀ is the single free parameter. Different observational probes constrain it differently. These values depend on WHICH ζ₀ benchmark is used.

| Benchmark | ζ₀ | w₀ | Context | Where Used |
|-----------|-----|------|---------|------------|
| Junction condition (JC) | 9.6 × 10⁻⁴ | -0.830 | Brane spectral action chain (ε = 0.275 fitted) | Ch1 (spectral chain), Ch4 §4.24 |
| CAMB best-fit | 0.013 | -0.987 | Planck CMB + DESI Y1 BAO combined Boltzmann fit | Ch2 (observational) |
| **Weighted mean** | **0.016 ± 0.002** | **-0.990** | **4-probe inverse-variance weighted (HK + H(z) + CAMB + multi-probe)** | **Canonical single number** |
| Multi-probe | 0.020 | -0.993 | DESI DR2 BAO + f·σ₈ + Planck H₀ + HK | Ch2 (multi-probe fit) |
| HK-CMB | 0.037 | -0.996 | Hiramatsu-Kobayashi β_HK from Planck | Ch2 (CMB constraint) |

**The key insight:** w₀ = -0.830 (spectral chain) and w₀ = -0.990 (weighted mean) are NOT contradictory. They are the SAME parametric prediction w₀(ζ₀) = -1 + C_KK/ζ₀ evaluated at different ζ₀ values. The spectral chain gives a SPECIFIC ζ₀ if ε = 0.275 is assumed; the data-driven fits give a DIFFERENT ζ₀ from observations.

---

## The Goldberger-Wise Result (Phase 1)

The GW parameter fix (April 15, 2026) showed that ε is **genuinely external** — it cannot be derived from the spectral action. Three independent findings:

1. S(y_c) is monotonically increasing — no minimum exists
2. d²S/d(ky_c)² = -0.31 (destabilizing)
3. Conformal coupling ξ = 1/6 on AdS₅ gives naive ε = √(2/3) ≈ 0.816, overshooting DESI-fitted 0.275 by 3×

**Consequence:** The spectral chain value (ε = 0.275 → ζ₀ = 8.8 × 10⁻⁴ → w₀ = -0.830) depends on a FITTED parameter. The data-driven values (ζ₀ = 0.016, w₀ = -0.990) do not. For canonical use, **prefer the data-driven weighted mean** unless specifically discussing the spectral chain.

---

## Canonical Values for Volume

When a single number is needed, use:

| Quantity | Canonical Value | Notes |
|----------|----------------|-------|
| w₀ | **-0.990** (weighted mean at ζ₀ = 0.016) | Or present the curve w₀(ζ₀) |
| ζ₀ | **0.016 ± 0.002** | 4-probe weighted mean |
| c_s | **[12c, 15c]** | Post-correction ε₁ = 0.010 |
| ε₁ | **0.010 ± 0.002** | Corrected d=5 Weyl |
| C_KK | **(1.64 ± 0.33) × 10⁻⁴** | Planck 2018 fiducial |

When the spectral chain is discussed (Ch4), use:
- ε = 0.275 (DESI-fitted, NOT derived)
- ζ₀ = 8.8 × 10⁻⁴ (from spectral chain with fitted ε)
- w₀ = -0.830 (spectral chain value)
- Clearly label these as "spectral chain benchmark" to distinguish from data-driven values

---

## Chapter-by-Chapter Revision Guide

### Chapter 1 (Foundation)
- Present w₀(ζ₀) as the parametric prediction (the curve, not a number)
- Use weighted mean ζ₀ = 0.016 ± 0.002 as the canonical single benchmark
- Update c_s references to [12c, 15c] (corrected Weyl)
- Note the spectral chain value as a specific point on the curve, clearly labeled

### Chapter 2 (Observational)
- Lead with the curve confrontation against data
- Tabulate all ζ₀ constraints with their probes and epochs
- Include the weighted mean and its consistency χ² = 6.34 (p = 0.042)
- Add the functional-form mismatch analysis (38.8% at z ≈ 1.14)

### Chapter 3 (No-Go)
- No ζ₀-dependent values to canonicalize
- Ensure ε₁ = 0.010 is consistent

### Chapter 4 (NCG/Spectral)
- Spectral chain discussion uses ε = 0.275, ζ₀ = 8.8 × 10⁻⁴, w₀ = -0.830
- Clearly labeled as "spectral chain at fitted ε" not "the prediction"
- Add GW result (ε external) in §4.24
- Note factor-of-3 gap (ε_naive = 0.816 vs ε_fitted = 0.275) as open physics

### Chapter 5 (Sound Speed)
- Canonical c_s = [12c, 15c]
- Remove all references to 11.3c (pre-correction value)
- Explain the correction: ε₁ = 0.018 → 0.010 from corrected d=5 Weyl decomposition

### Appendix D (Value Table)
- Complete table with all three tiers
- Cross-references to chapter and equation numbers
- Benchmark labels for all Tier 3 values
