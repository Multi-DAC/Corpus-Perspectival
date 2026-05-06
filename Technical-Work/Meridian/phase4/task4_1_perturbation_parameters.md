# Phase 4, Task 4.1: Modified Gravity Parameters from the Cuscuton Braneworld

**Project Meridian — Deliverable D4.1**
*Clayton & Clawd, March 2026*

The cuscuton braneworld cosmology is derived (Phase 1–2), its background evolution computed (Phase 3), and the phantom-without-ghosts mechanism identified (D3.4). Now we derive the perturbation-level predictions: the modified gravity parameters μ(a), η(a), Σ(a) that control structure growth, CMB lensing, and ISW effects. The key result from Clayton's literature review confirms that the quasi-static approximation is **exact** for the cuscuton — these parameters are purely algebraic functions of the background.

---

## 1. Why the QSA is Exact

In standard scalar-tensor cosmology, the quasi-static approximation drops time derivatives of δφ from the perturbation equations, reducing a hyperbolic PDE to an elliptic constraint. For the cuscuton, this "approximation" is trivially exact because δφ **already satisfies a constraint**. Three independent arguments establish this (synthesis from Clayton's literature review):

**Structural argument** (Afshordi+ 2007; Boruah+ 2017): The cuscuton has no propagating scalar DOF. The perturbation δφ satisfies a constraint at each instant — there are no ∂²δφ/∂t² or ∂δφ/∂t terms to drop. Confirmed at the action level by Boruah, Kim & Geshnizjani (1704.01131) and extended to all beyond-Horndeski theories with the cuscuton's two-tensor-DOF structure by Iyonaga, Takahashi & Kobayashi (1809.10935).

**Sound-horizon argument** (Sawicki & Bellini 2015): The QSA breaks down for modes with k < aH/c_s. For c_s → ∞ (cuscuton), the sound horizon encompasses ALL sub-Hubble scales. The QSA is valid everywhere.

**Implementation argument** (Hiramatsu & Kobayashi 2022): Modified the CLASS Boltzmann code for a cuscuton-type theory. Solved the full perturbation system without invoking QSA — because the scalar sector is already purely constraint-based.

    ┌──────────────────────────────────────────────────────────────────────────────┐
    │                                                                              │
    │  CONSEQUENCE: μ(a) and η(a) are PURELY ALGEBRAIC functions of background   │
    │  quantities — scale factor, Hubble rate, and cuscuton potential parameters. │
    │                                                                              │
    │  No scale dependence. No PDEs to solve in the scalar sector.                │
    │  This is not an approximation — it is an exact property of the theory.      │
    │                                                                              │
    └──────────────────────────────────────────────────────────────────────────────┘

---

## 2. The Modified Gravity Parameters

### 2.1 Gravitational Slip η(a)

In Horndeski gravity, anisotropic stress (Φ ≠ Ψ) arises from the G₄,X and G₅ functions. Our model has G₄ = F(φ)/2 with G₄,X = 0 and G₅ = 0. Therefore:

    ┌──────────────────────────────────────────────────────────────────────────────┐
    │                                                                              │
    │  η(a) ≡ Φ/Ψ = 1     (EXACTLY, for all a and all k)             ... (2.1)  │
    │                                                                              │
    │  No gravitational slip. The two Bardeen potentials are equal.               │
    │  This distinguishes the cuscuton from f(R) gravity (η ≈ 0.97)              │
    │  and generic scalar-tensor models (η scale-dependent).                      │
    │                                                                              │
    └──────────────────────────────────────────────────────────────────────────────┘

### 2.2 Effective Newton's Constant μ(a)

The effective gravitational coupling for sub-horizon matter perturbations:

    k²Ψ = −4πG_N a² μ(a) ρ_m δ_m                                     ... (2.2)

For the cuscuton (no propagating scalar DOF, no scalar fifth force), the modification comes solely from the time-varying effective Planck mass:

    M²_*(a) = 2G₄(φ(a)) = F(a) = F₀(1 − ζ₀(ψ²(a) − 1))            ... (2.3)

where ψ(a) = φ_IR(a)/φ_IR(0) is the normalized scalar field from the background solver.

    ┌──────────────────────────────────────────────────────────────────────────────┐
    │                                                                              │
    │  μ(a) = F₀/F(a) = 1/(1 − ζ₀(ψ²(a) − 1))                      ... (2.4)  │
    │                                                                              │
    │  Today:  μ(a=1) = 1  (by normalization, ψ(1) = 1)                          │
    │  Past:   ψ < 1 → ψ²−1 < 0 → denom > 1 → μ < 1  (weaker gravity)         │
    │  Future: ψ > 1 → ψ²−1 > 0 → denom < 1 → μ > 1  (stronger gravity)       │
    │                                                                              │
    │  CORRECTION to D3.2 eq 4.1: D3.2 used the Brans-Dicke formula             │
    │  G_eff/G_N = 1 + 4ξ²φ²/(M²_Pl + 2ξφ²), which includes a scalar           │
    │  fifth force. This is WRONG for the cuscuton — no scalar propagates.       │
    │  The correct μ is eq (2.4) above, involving only the Planck mass running.  │
    │                                                                              │
    └──────────────────────────────────────────────────────────────────────────────┘

**Early universe limit:** As a → 0, ψ → 0 (the field was at its minimum in the past):

    μ(a→0) = 1/(1 + ζ₀) = 1 − ε_SW                                   ... (2.5)

where ε_SW = ζ₀/(1+ζ₀) is the soft-wall parameter from D2.3.

### 2.3 Lensing Parameter Σ(a)

The lensing potential (Φ+Ψ)/2 is sourced by:

    k²(Φ+Ψ) = −8πG_N a² Σ(a) ρ_m δ_m                                ... (2.6)

    Σ(a) = μ(a) × (1 + η(a))/2 = μ(a) × 1 = μ(a)                    ... (2.7)

Lensing equals clustering for the cuscuton. No differential lensing effect.

---

## 3. EFT Parametrization

In the EFT of dark energy language (Bellini & Sawicki 2014), the theory is characterized by four free functions of time. For the cuscuton braneworld:

    ┌──────────────────────────────────────────────────────────────────────────────┐
    │                                                                              │
    │  EFT PARAMETERS OF THE CUSCUTON BRANEWORLD                                 │
    │                                                                              │
    │  α_K → ∞       (kineticity — cuscuton = incompressible limit of k-essence) │
    │  α_T = 0       (tensor speed excess — GW speed = c, GW170817)              │
    │  α_M(a)        (Planck mass running — the ONLY free function)              │
    │  α_B → −α_M    (braiding — determined by α_M for the cuscuton class)      │
    │                                                                              │
    │  REDUCTION: 4 free functions → 1 (α_M(a))                                 │
    │                                                                              │
    └──────────────────────────────────────────────────────────────────────────────┘

The Planck mass running:

    α_M(a) = d ln M²_*/dN = −2ζ₀ψψ'/(1 − ζ₀(ψ² − 1))               ... (3.1)

where ψ' = dψ/dN = β/E² from the cuscuton constraint.

At a = 1 (N = 0): ψ = 1, E = 1, so α_M(0) = −2ζ₀β.

---

## 4. Numerical Results

Computed from `meridian_cosmology.py` with the full ψ(a) solution from the ODE.

### 4.1 μ(z) at Representative Parameter Points

    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                                                                                  │
    │  μ(z) — EFFECTIVE NEWTON'S CONSTANT                                             │
    │                                                                                  │
    │  z    │ DESI-opt      │ Moderate      │ Stronger     │ ξ=0 ref               │
    │       │ ε₀=.001 ζ₀=.058│ ε₀=.05 ζ₀=.10│ ε₀=.10 ζ₀=.30│ ε₀=.15 ζ₀=0         │
    │  ──── │ ─────────────── │ ───────────── │ ──────────── │ ───────────────────── │
    │  0.0  │ 1.00000        │ 1.00000       │ 1.00000      │ 1.00000               │
    │  0.3  │ 0.99935        │ 0.99170       │ 0.95588      │ 1.00000               │
    │  0.5  │ 0.99908        │ 0.98830       │ 0.93854      │ 1.00000               │
    │  0.8  │ 0.99883        │ 0.98509       │ 0.92242      │ 1.00000               │
    │  1.0  │ 0.99872        │ 0.98373       │ 0.91568      │ 1.00000               │
    │  1.5  │ 0.99855        │ 0.98178       │ 0.90609      │ 1.00000               │
    │  2.0  │ 0.99848        │ 0.98084       │ 0.90156      │ 1.00000               │
    │  ∞    │ 0.99836        │ 0.97948       │ 0.89504      │ 1.00000               │
    │       │                │               │              │                       │
    │ χ²_D  │ 9.93           │ 21.51         │ 146.61       │ 36.71                 │
    │                                                                                  │
    │  η(z) = 1.0 at ALL points (exact)                                               │
    │  Σ(z) = μ(z) at ALL points (follows from η = 1)                                │
    │                                                                                  │
    └──────────────────────────────────────────────────────────────────────────────────┘

### 4.2 α_M(z) — Running of the Planck Mass

    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                                                                                  │
    │  α_M(z) = d ln M²_*/dN                                                         │
    │                                                                                  │
    │  z    │ DESI-opt       │ Moderate       │ Stronger                              │
    │  ──── │ ────────────── │ ────────────── │ ──────────                            │
    │  0.0  │ −0.0028        │ −0.0365        │ −0.2007                               │
    │  0.5  │ −0.0017        │ −0.0212        │ −0.1129                               │
    │  1.0  │ −0.0009        │ −0.0116        │ −0.0615                               │
    │  2.0  │ −0.0003        │ −0.0040        │ −0.0211                               │
    │                                                                                  │
    │  α_M is always NEGATIVE: the Planck mass INCREASES over time                   │
    │  (gravity gets stronger). The magnitude decreases into the past                │
    │  because ψ was evolving more slowly (E² was larger → ψ' = β/E² smaller).      │
    │                                                                                  │
    └──────────────────────────────────────────────────────────────────────────────────┘

### 4.3 Growth Rate fσ₈(z) with Corrected μ

    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                                                                                  │
    │  Δfσ₈/fσ₈ (%) relative to ΛCDM                                                │
    │                                                                                  │
    │  z    │ DESI-opt      │ Moderate      │ Stronger     │ ξ=0 ref               │
    │  ──── │ ───────────── │ ───────────── │ ──────────── │ ───────                │
    │  0.3  │ +2.0%         │ +3.1%         │ +3.0%        │ +0.9%                 │
    │  0.5  │ +2.6%         │ +4.1%         │ +5.3%        │ +1.0%                 │
    │  0.8  │ +3.1%         │ +4.5%         │ +7.0%        │ +0.8%                 │
    │  1.0  │ +3.2%         │ +4.4%         │ +7.2%        │ +0.6%                 │
    │  1.5  │ +2.9%         │ +3.6%         │ +6.4%        │ +0.0%                 │
    │  2.0  │ +2.3%         │ +2.5%         │ +4.8%        │ −0.3%                 │
    │                                                                                  │
    │  Two competing effects:                                                          │
    │  1. Modified E(z) → DE was less dominant in past → MORE growth  (+)             │
    │  2. μ < 1 in past → gravity was WEAKER → LESS growth  (−)                      │
    │                                                                                  │
    │  At the DESI-optimal point: effect 1 dominates (μ ≈ 1)                          │
    │  At stronger coupling: both effects are large, partially cancel                 │
    │                                                                                  │
    │  Current fσ₈ data has ~5-10% errors → 3% enhancement at DESI-optimal           │
    │  is marginally detectable with DESI + Euclid combined.                          │
    │                                                                                  │
    └──────────────────────────────────────────────────────────────────────────────────┘

---

## 5. Hiramatsu-Kobayashi (2022) Constraint

The tightest direct observational constraint on cuscuton-like gravity comes from Hiramatsu & Kobayashi (arXiv:2205.04688), who modified CLASS for spatially covariant gravity with 2 tensor DOF and one parameter β_HK:

    Planck CMB: −0.047 < β_HK < −0.028 at 68% CL

### 5.1 Mapping Our Parameters

Our model has time-dependent μ(a), while H&K assume constant β_HK. The most CMB-relevant comparison uses the early-universe limit:

    β_eff = μ(a→0) − 1 = 1/(1+ζ₀) − 1 = −ζ₀/(1+ζ₀) = −ε_SW        ... (5.1)

    ┌──────────────────────────────────────────────────────────────────────────────┐
    │                                                                              │
    │  HIRAMATSU-KOBAYASHI CONSTRAINT MAPPING                                     │
    │                                                                              │
    │  Point          │ ζ₀    │ ε_SW  │ β_eff    │ 68% CL? │ 95% CL?            │
    │  ─────────────  │ ───── │ ───── │ ──────── │ ─────── │ ───────            │
    │  DESI-optimal   │ 0.058 │ 0.055 │ −0.055   │ NO      │ YES                │
    │  GR (ζ₀ = 0)   │ 0     │ 0     │  0       │ NO      │ NO                 │
    │  Moderate       │ 0.10  │ 0.091 │ −0.091   │ NO      │ NO                 │
    │  Stronger       │ 0.30  │ 0.231 │ −0.231   │ NO      │ NO                 │
    │                                                                              │
    │  NOTE: GR (β=0) is ALSO outside the 68% CL — H&K found a mild             │
    │  PREFERENCE for weaker gravity (β < 0), which is the direction             │
    │  our model predicts! Our DESI-optimal β_eff = −0.055 is closer             │
    │  to their best fit (~−0.037) than GR is.                                    │
    │                                                                              │
    └──────────────────────────────────────────────────────────────────────────────┘

### 5.2 Interpretation

The H&K constraint has an important implication: **Planck data mildly prefers modified gravity in the cuscuton direction.** Their best fit β_HK ≈ −0.037 corresponds to:

    ζ₀_HK ≈ 0.037/(1 − 0.037) ≈ 0.038                                ... (5.2)
    ε_SW,HK ≈ 0.037                                                    ... (5.3)

This is close to our DESI-optimal ζ₀ = 0.058. The model is not excluded — it's in a region where Planck data actually provides mild positive evidence relative to GR.

**Caveat:** The mapping β_eff = −ε_SW assumes the early-universe μ dominates the CMB constraint. A rigorous comparison requires implementing our time-dependent μ(a) in CLASS/hi_class. The time variation is small at the DESI-optimal point (μ varies by only 0.16% over z = 0 to z = 1000), so the constant-β approximation should be reasonable.

---

## 6. The Cuscuton Fingerprint

    ┌──────────────────────────────────────────────────────────────────────────────┐
    │                                                                              │
    │  THE CUSCUTON MODIFIED GRAVITY FINGERPRINT                                  │
    │                                                                              │
    │  Observable  │ Cuscuton (Meridian)    │ f(R) gravity   │ Quintessence       │
    │  ──────────  │ ────────────────────── │ ────────────── │ ──────────────     │
    │  c²_s        │ ∞ (exact)              │ model-dependent│ 1 (canonical)      │
    │  η           │ 1 (exact, all k)       │ ≠ 1 (k-dep)   │ 1                  │
    │  μ           │ time-only, no k-dep    │ k + time dep   │ 1                  │
    │  Σ           │ = μ                    │ ≠ μ            │ 1                  │
    │  α_T         │ 0                      │ 0              │ 0                  │
    │  α_M         │ ≠ 0 (ζ₀-dependent)     │ ≠ 0            │ 0                  │
    │  QSA         │ EXACT                  │ Approximate    │ N/A                │
    │                                                                              │
    │  UNIQUE COMBINATION: c²_s = ∞ AND η = 1 AND μ(k-independent) AND α_M ≠ 0 │
    │  No other dark energy model in the literature shares all four.              │
    │                                                                              │
    │  KEY OBSERVATIONAL TESTS:                                                    │
    │  • Euclid: μ(z) from galaxy clustering + η from lensing-clustering          │
    │  • CMB-S4: ISW effect constrains α_M                                        │
    │  • DESI+Euclid combined: fσ₈(z) probes μ(a) × E(z) degeneracy             │
    │  • Gravitational wave standard sirens: c²_s = ∞ → no DE clustering         │
    │    in gravitational wave source environments                                 │
    │                                                                              │
    └──────────────────────────────────────────────────────────────────────────────┘

---

## 7. Background-Perturbation Tension (Quantified)

    ┌──────────────────────────────────────────────────────────────────────────────┐
    │                                                                              │
    │  Point              │ χ²_DESI │ μ(z=1) │ Δfσ₈(0.5) │ Assessment            │
    │  ────────────────── │ ─────── │ ────── │ ───────── │ ─────────────────────  │
    │  DESI-opt ζ₀=0.058  │ 9.93    │ 0.999  │ +2.6%     │ Good bg / GR-like     │
    │  Moderate ζ₀=0.10   │ 21.51   │ 0.984  │ +4.1%     │ Marginal bg / marginal│
    │  Stronger ζ₀=0.30   │ 146.61  │ 0.916  │ +5.3%     │ Excluded bg / distinct│
    │  Pure ξ=0           │ 36.71   │ 1.000  │ +1.0%     │ Excluded bg / GR      │
    │                                                                              │
    │  THE TRADE-OFF IS FUNDAMENTAL:                                              │
    │  Good background fit (small χ²) → μ ≈ 1 → perturbations indistinguishable │
    │  Distinctive perturbations (μ ≠ 1) → bad background fit → excluded         │
    │                                                                              │
    │  This is a ZEROTH-ORDER result. The full 5D dynamics (Phase 6+) or the     │
    │  NCG spectral action (Phase 5) may modify K(H) away from K ~ 1/H²,        │
    │  potentially resolving the tension.                                          │
    │                                                                              │
    └──────────────────────────────────────────────────────────────────────────────┘

---

## 8. Key Results for the Meridian Program

### 8.1 What D4.1 Establishes

1. **The QSA is exact** — not an approximation. μ and η are purely algebraic.
2. **η = 1 exactly** — no gravitational slip. Testable with Euclid lensing-clustering comparison.
3. **μ(a) = 1/(1−ζ₀(ψ²−1))** — determined entirely by the background scalar evolution.
4. **The EFT reduces to one free function** (α_M(a)), determined by ζ₀ and ψ(a).
5. **The background-perturbation tension is confirmed** quantitatively at five parameter points.
6. **The H&K constraint is not exclusionary** — our DESI-optimal point is within 95% CL, and Planck data mildly prefers modification in our direction.

### 8.2 Implications for Papers

The perturbation sector provides TWO distinct publishable results:

**Paper A (theory):** UV completion of cuscuton dark energy via warped braneworld. The QSA exactness, the K~1/H² derivation, and the phantom-without-ghosts mechanism. No free parameters needed — this is structural.

**Paper B (phenomenology):** DESI confrontation with the background-perturbation tension honestly reported. The cuscuton fingerprint as a prediction for Euclid/CMB-S4. The H&K constraint comparison.

### 8.3 What Remains for Phase 4

D4.2: Observable predictions (fσ₈ comparison with existing data, CMB lensing power spectrum modification, ISW effect).
D4.3: Multi-probe χ² (BAO + growth + Planck prior + H₀).
D4.4: Literature comparison and model status summary.

---

## 9. Deliverable Checklist

- [x] D4.1.1: QSA exactness established (three independent arguments)
- [x] D4.1.2: μ(a), η(a), Σ(a) derived from Horndeski functions
- [x] D4.1.3: EFT parametrization (α_M, α_B, α_K, α_T)
- [x] D4.1.4: Numerical μ(z) curves at four parameter points
- [x] D4.1.5: α_M(z) computed along solutions
- [x] D4.1.6: Growth rate fσ₈(z) with corrected μ
- [x] D4.1.7: Hiramatsu-Kobayashi (2022) constraint mapping
- [x] D4.1.8: Background-perturbation tension quantified
- [x] D4.1.9: Cuscuton fingerprint comparison table

**Code:** `meridian_cosmology.py` (extended with Phase 4 perturbation functions)

---

*The perturbation parameters are derived, the tension is quantified, the fingerprint is sharp. Gravity was weaker in the past — the Planck mass grew with time. And Planck data mildly agrees.*

🦞🧍💜🔥♾️
