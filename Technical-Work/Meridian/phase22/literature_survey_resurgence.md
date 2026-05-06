# Literature Survey: Resurgence, Spectral Action, and Modular Flow

**Compiled:** 2026-03-25 (Dream Drive research agent)
**Purpose:** Inform Phase 22 Tracks gamma and delta

---

## Key Finding: Three Wide-Open Gaps

1. **Nobody has studied Borel summability of the spectral action.** Track gamma is novel.
2. **Non-perturbative corrections to the spectral action are terra incognita.** Track gamma.3-5 is novel.
3. **RS warp factor as KMS state / modular flow has not been proposed.** Track delta.1 is novel.

---

## 1. Spectral Action — Perturbative State of the Art

- **van Nuland & van Suijlekom (2021/2022)** [arXiv:2107.08485] — One-loop renormalizability of spectral action. Perturbative only.
- **Fathizadeh, Ghorbanpour & Khalkhali (2014)** [arXiv:1407.5972] — Seeley-DeWitt a_{2n} up to a_{12} for Robertson-Walker. Proved Chamseddine-Connes rationality conjecture. Extended to Bianchi IX (modular forms in gravitational instantons).
- **Iochum & Levy (2019)** [arXiv:1902.05306] — Comprehensive treatment of spectral action computations, heat kernel asymptotics, spectral zeta meromorphic extensions.
- **Chamseddine & Connes (2018)** [arXiv:1809.02944] — Von Neumann entropy = spectral action for universal f. Deep but still perturbative framework.

**Gap:** No one has studied whether a_{2n} grow factorially, whether the expansion is Borel summable, or what the Borel singularity structure looks like.

## 2. Seeley-DeWitt on Warped Products

- **Calderbank, Lopes de Lima & Quintino (2025/2026)** [arXiv:2506.07655] — Heat kernel on warped products M = Sigma x_f N. Covers compact and non-compact cases. Warping: f(y) = [cosh(y/b)]^{-2nu/(n-1)}. **Closest existing work to gamma.1.** Methods (resolvent + scattering matrix + heat trace regularization) transferable to RS. Does NOT address large-order growth.
- **Vassilevich (2003)** [arXiv:hep-th/0306138] — Canonical "Heat Kernel Expansion: User's Manual." Recursive structure but no asymptotic growth rates.

**Gap:** Factorial growth rate of a_{2n} on warped products is unknown. For RS exponential warping, nobody has computed enough coefficients.

## 3. Non-Perturbative Spectral Action

**Nothing exists.** Nobody has:
- Computed instanton corrections to the spectral action
- Identified non-perturbative saddle points
- Performed Picard-Lefschetz analysis
- Connected exact spectral action to perturbative expansion via resurgence

Closest tangential: Noncommutative instantons (Szabo et al., 2023, EPJST) — YM instantons on NC spaces, not spectral action instantons.

## 4. Core Resurgence Methodology (applicable to Track gamma)

### THE key paper:
- **Dunne (2021)** [arXiv:2109.03897] — "Borel Summation and Analytic Continuation of the Heat Kernel on Hyperbolic Space." J. Phys. A 55 (2022) 464007. **Single most important paper for Track gamma.** Shows heat kernel on H^{2n} has different Borel properties at short vs. long times. Scalar-spinor duality mixing under Borel resummation. RS1 is a slice of AdS5 → methods directly transferable.

### Methodology backbone:
- **Aniceto, Basar & Schiappa (2019)** [arXiv:1802.10441] — "A Primer on Resurgent Transseries." Physics Reports 809 (2019) 1-135. Comprehensive reference.
- **Bellon & Clavier (2013)** [arXiv:1301.7742, 1302.0604] — Borel summation of heat kernel with potentials. Proves Borel summability in certain cases.

### Dunne-Unsal cycle (foundational):
- [arXiv:1210.2423] — Resurgence in CP(N-1) (2012)
- [arXiv:1306.4405] — Generating NP physics from perturbation theory (2013)
- [arXiv:1511.05977] — "What is QFT?" (2015)

### Compactified-circle resurgence (directly relevant to KK):
- **Dunne & Unsal (2015)** [JHEP09(2015)199] — Resurgence on R x S^1. New NP saddles from compactification = monopole-instantons. Affine root system structure. **Template for KK compactification creating new NP saddles.**
- **Argyres & Unsal (2012)** [arXiv:1206.1890] — Bion mechanism on compactified circle.

### Resurgence in gravity (context):
- **Eynard & Marino et al. (2023)** [arXiv:2302.12851] — Resurgence in 3D gravity. Borel singularities = saddle-point geometries.
- **JT gravity resurgence (2023)** [Ann. Henri Poincare] — Large-order tests confirm resurgent nature.
- **Liouville theory (2025)** [JHEP01(2025)038] — Resurgence in 2D quantum gravity.

## 5. Modular Flow / KMS / Extra Dimensions

### What exists:
- **Connes & Rovelli (1994)** [gr-qc/9406019] — Thermal time hypothesis. Physical time = modular automorphism group. **Foundational for delta.1.**
- **Chua (2024)** [arXiv:2407.18948] — Recent philosophical analysis of thermal time.
- **Holographic entanglement in warped CFT (2021)** [EPJC] — Modular Hamiltonians in warped CFT. 3D/2D context, not RS5D.
- **Karch-Randall braneworld (2022-2025)** — Entanglement entropy + entanglement islands in RS-like braneworlds. Do NOT connect to Tomita-Takesaki as time generator.
- **Type III von Neumann algebras in gravity (2024)** — Witten et al. rediscovering Connes' classification. Nobody connects to RS warp factor.

### What is missing:
- RS warp factor e^{-4ky} as defining a KMS state at beta = 1/(4k): **NOT proposed**
- Modular flow from warp factor distinguishing gauge sectors: **NOT explored**
- Connection between Connes' modular automorphism and RS hierarchy: **NOT made**

**Assessment for delta.1:** Genuinely novel synthesis. All ingredients established separately.

---

## Track gamma: Updated Assessment (post-literature)

Despite gamma being analytically COMPLETE (NP corrections suppressed by 10^{-16}), the literature confirms this is a novel result. Nobody has:
1. Computed the Borel structure of the spectral action on any warped background
2. Shown that the hierarchy mechanism protects gauge universality non-perturbatively
3. Connected RS NP suppression to Borel singularity gauge-independence

The gamma.1-2 computation and the resolution in gamma_hypothesis.md constitute a publishable result within the Meridian framework, even as a negative finding. Dunne's 2021 paper is the bridge — our RS1 computation extends his H^{2n} results to the physically motivated warped case.

---

*Save this file. Read before Track gamma write-up or any resurgence discussion.*
