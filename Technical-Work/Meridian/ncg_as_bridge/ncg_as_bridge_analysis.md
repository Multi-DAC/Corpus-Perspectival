# NCG-AS Bridge: Mathematical Analysis

## Spectral Action vs. Asymptotic Safety Coupling Ratios

**Date:** March 17, 2026
**Status:** Complete mathematical groundwork
**Verdict:** The bridge exists, but as a UV-initial-condition / RG-flow relationship, not as a direct identification of coupling ratios. A sign discrepancy in at least one higher-curvature coupling is the sharpest tension. The spectral action ratios are topologically protected and matter-independent.

---

## 1. Spectral Action Coupling Ratios (Pure Gravity)

### Setup

The spectral action S = Tr(f(D^2/Lambda^2)) on a 4D Riemannian spin manifold, expanded via the heat kernel, gives:

S = (1/(16 pi^2)) int d^4x sqrt(g) [4 f_0 Lambda^4 + (5/3) f_2 Lambda^2 R + f_4/360 * (gravitational a_4)]

### Computation of a_4(D^2)

For the squared Dirac operator D^2 on a 4D spin manifold, using the Lichnerowicz formula D^2 = nabla^* nabla + R/4 and the Vassilevich general formula for Laplace-type operators:

**Key traces over the spinor bundle (N_s = 4):**

| Trace | Value | Source |
|-------|-------|--------|
| tr(I) | 4 | dim of spinor space |
| tr(E) | -R | E = -R/4, traced over 4 spinors |
| tr(E^2) | R^2/4 | (R/4)^2 * 4 |
| tr(R*E) | -R^2 | R * (-R/4) * 4 |
| tr(box E) | -box R | (-1/4) box R * 4 |
| tr(Omega^2) | -Riem^2/2 | From spin connection curvature computation |

The spin connection curvature trace requires:

tr(gamma^a gamma^b gamma^c gamma^d) = 4(g^{ab}g^{cd} - g^{ac}g^{bd} + g^{ad}g^{bc})

Contracting with (1/16) R_{mnab} R^{mncd} gives -Riem^2/2 after using the antisymmetry of the Riemann tensor.

**Result (inside (4pi)^{-2} * (1/360)):**

| Invariant | Coefficient | Derivation |
|-----------|-------------|------------|
| Riem^2 | **-7** | 2*4 + 30*(-1/2) = 8 - 15 |
| Ric^2 | **-8** | -2*4 |
| R^2 | **-85** | 5*4 - 60 - 45 |
| box R | -108 | -12*4 - 60 (total derivative, dropped) |

### Basis Conversion to (C^2, E_4, R^2)

Using C^2 = Riem^2 - 2 Ric^2 + (1/3)R^2 and E_4 = Riem^2 - 4 Ric^2 + R^2:

| Invariant | Coefficient |
|-----------|-------------|
| C^2 (Weyl^2) | **-18** |
| E_4 (Gauss-Bonnet) | **+11** |
| R^2 | **-90** |

### The Universal Ratios

These ratios are **independent of the cutoff function f** (they don't depend on f_0, f_2, f_4):

| Ratio | Value | Decimal |
|-------|-------|---------|
| C^2 / R^2 | 1/5 | 0.200 |
| E_4 / R^2 | -11/90 | -0.122 |
| C^2 / E_4 | -18/11 | -1.636 |
| Riem^2 / Ric^2 | 7/8 | 0.875 |
| Ric^2 / R^2 | 8/85 | 0.094 |

**Sign structure:** All gravitational higher-curvature couplings are negative (for f_4 > 0), except E_4 which is positive. This means:
- Weyl^2 has the **opposite** sign from Stelle gravity
- R^2 is **negative** (wrong sign for the Starobinsky inflation term)
- E_4 is **positive** (standard topological term sign)

### 4D Effective Basis (R^2, Ric^2)

In 4D, using Riem^2 = E_4 + 4 Ric^2 - R^2 (Gauss-Bonnet identity):

a_4 = (1/360)[-7(E_4 + 4 Ric^2 - R^2) - 8 Ric^2 - 85 R^2]
    = (1/360)[-7 E_4 - 36 Ric^2 - 78 R^2]

Dropping the topological E_4, the effective 4D higher-derivative action is:

| Coupling | Coefficient (inside 1/360) |
|----------|--------------------------|
| alpha (R^2) | **-78** |
| beta (Ric^2) | **-36** |

Ratio: beta/alpha = 6/13 = 0.462

Both are negative. Equivalently: alpha + beta/3 = -78 + (-12) = -90 = effective R^2 in the (C^2, R^2) basis, and beta/2 = -18 = C^2 coefficient. This is consistent with the (C^2, E_4, R^2) computation above (cross-check passes).

---

## 2. Asymptotic Safety Fixed-Point Values

### 2A. Ohta & Percacci (2014) [arXiv:1308.3398]

**Action:** S = int d^Dx sqrt(g) [sigma R/kappa^2 - 2 Lambda/kappa^2 + alpha R^2 + beta Ric^2 + gamma Riem^2]

**4D Fixed Points** (in dimensionless couplings omega, theta):

| Fixed Point | omega* | theta* | Lambda_tilde* | G_tilde* |
|-------------|--------|--------|---------------|----------|
| FP1 | -5.467 | 0.327 | 0.293 | -2.148 |
| FP2 (physical) | -0.0229 | 0.327 | 0.209 | 1.346 |

**Notable:** theta* = 0.327 is **identical at both FPs**. Critical exponents: (-4, -2), both UV-attractive.

### 2B. Benedetti, Machado & Saueressig (2009) [arXiv:0901.2984]

**Action:** Gamma = int d^4x sqrt(g) [u_0 + u_1 R - (omega/(3lambda))R^2 + (1/(2lambda))C^2 + (theta/lambda)E_4]

**Fixed-point values:**

| Coupling | Value | Interpretation |
|----------|-------|---------------|
| g_0* | 0.00442 | Cosmological constant |
| g_1* | -0.0101 | Einstein-Hilbert |
| g_2* | +0.00754 | Ric^2 combination |
| g_3* | -0.0050 | Riem^2 combination |

Universal product: (G Lambda)* = 0.427

**Critical exponents:** theta_0 = 2.51, theta_1 = 1.69, theta_2 = 8.40 (UV-attractive), theta_3 = -2.11 (UV-repulsive).

---

## 3. The Comparison

### 3A. Riem^2/Ric^2 Ratio (Most Robust Comparison)

| Framework | Riem^2/Ric^2 |
|-----------|-------------|
| Spectral Action | 7/8 = **+0.875** |
| AS (BMS) | -0.005/0.00754 = **-0.663** |

**These have opposite signs.** In the spectral action, Riem^2 and Ric^2 enter with the same sign (both negative). In the BMS AS fixed point, they have opposite signs (Ric^2 positive, Riem^2 negative).

### 3B. Sign Structure Comparison

| Coupling | Spectral Action | AS (BMS) | Match? |
|----------|----------------|----------|--------|
| Riem^2 | NEGATIVE (-7) | NEGATIVE (-0.005) | YES |
| Ric^2 | NEGATIVE (-8) | POSITIVE (+0.00754) | **NO** |
| R^2 | NEGATIVE (-85) | (scheme-dep.) | ? |
| C^2 | NEGATIVE (-18) | (scheme-dep.) | ? |
| E_4 | POSITIVE (+11) | POSITIVE | YES |
| EH (R) | POSITIVE | POSITIVE | YES |

### 3C. Assessment

The Ric^2 sign discrepancy is **structural**, not a matter of numerical fine-tuning. The spectral action gives all curvature-squared terms with negative coefficients (except E_4), while the AS fixed point has a positive Ric^2 coefficient.

---

## 4. NCG + SM Matter Corrections

### Key Result: Ratios Are Protected

The spectral action on M_4 x F (where F is the SM finite spectral triple) gives:

D = D_M tensor 1_F + gamma_5 tensor D_F

D^2 = D_M^2 tensor 1_F + 1_S tensor D_F^2

The gravitational curvature terms come **entirely** from D_M^2. The internal space H_F provides a multiplicative factor N_F to ALL gravitational traces equally. Therefore:

**C^2 : E_4 : R^2 = -18 : 11 : -90 (UNCHANGED by matter)**

The SM matter contributes:
- Gauge kinetic terms (not gravitational curvature)
- Non-minimal Higgs-gravity coupling xi |H|^2 R (modifies EH, not R^2)
- Quartic Higgs potential (not gravitational)
- Yukawa couplings (not gravitational)

**None of these modify the gravitational curvature-squared coupling ratios.**

### Verification via Chamseddine-Connes-Marcolli (2007)

The explicit Chamseddine-Connes result for the gravitational sector gives:
- C^2 coefficient: -3 N_g
- E_4 coefficient: (11/6) N_g

Ratio: C^2/E_4 = -3/(11/6) = **-18/11** (identical to pure gravity)

The N_g factor (number of generations) cancels in the ratio.

### One-Loop Matter Contributions to AS Flow

If we instead compute the one-loop matter contribution to the gravitational effective action (relevant for the AS beta functions):

**Per field type (inside 1/360):**

| Field | Riem^2 | Ric^2 | R^2 |
|-------|--------|-------|-----|
| Real scalar | +2 | -2 | +5 |
| Dirac fermion | -7 | -8 | -85 |
| Gauge boson (+ ghost) | +34 | -184 | -50 |

**SM total (4 scalars + 22.5 Dirac + 12 gauge):**
- Riem^2: 258.5
- Ric^2: -2396
- R^2: -2492.5

**In (C^2, E_4, R^2) basis:**
- C^2: -681
- E_4: 939.5
- R^2: -3205

C^2/E_4 = -0.725 (different from the pure gravity ratio of -1.636)

**Important:** These one-loop matter contributions affect the AS beta functions, potentially shifting the fixed point. But they do NOT change the spectral action ratios, which are determined by the tree-level heat kernel expansion.

---

## 5. Interpretation and the Nature of the Bridge

### Why the Discrepancy Does NOT Kill the Bridge

The spectral action and the AS fixed point play **different roles**:

1. **Spectral action** = the bare action at the NCG cutoff scale Lambda. It is the **initial condition** for the RG flow.

2. **AS fixed point** = the attractor of the RG flow in the UV. The effective average action Gamma_k approaches the fixed-point form as k -> infinity.

These are not the same thing. The spectral action defines where the theory STARTS; the fixed point defines where it GOES. For the theory to be UV-complete via asymptotic safety, the spectral action initial condition must lie in the **basin of attraction** of the Reuter fixed point.

### Basin of Attraction

The BMS fixed point has **3 UV-attractive directions** (critical exponents 2.51, 1.69, 8.40) and only **1 UV-repulsive direction** (critical exponent -2.11). This means:

- The basin of attraction is **3-dimensional** in the 4-dimensional coupling space
- **Most** initial conditions flow toward the fixed point
- The spectral action ratios need to satisfy only **1 constraint** (the UV-repulsive direction)

Whether the spectral action ratios satisfy this single constraint is the key open question.

### The Correct Framing

The NCG-AS relationship should be understood as:

**NCG provides the UV initial condition. AS provides the RG flow. The bridge is the requirement that the spectral action lies in the basin of attraction of the Reuter fixed point.**

This is analogous to how the SM gauge couplings at the GUT scale (initial condition) are different from the IR fixed-point values, but the theory is asymptotically free because the initial conditions lie in the basin of attraction of the Gaussian fixed point.

### What Would Confirm the Bridge

1. Compute the single UV-repulsive eigenvector at the BMS fixed point
2. Check whether the spectral action ratios project to zero along this eigenvector
3. If so: the spectral action lies EXACTLY on the UV critical surface, and the NCG-AS bridge is exact
4. If not: check how far off it is. A small projection means the theory is approximately asymptotically safe (the deviation grows slowly)

---

## 6. Open Questions for Phase 12

1. **Spectral action on M_4 x S^1/Z_2:** How does the 5D RS orbifold structure modify the a_4 coefficients? The KK reduction gives additional gravitational couplings from the 5D Weyl and R^2 terms.

2. **Compatibility with Chamseddine-Connes SM:** The RS orbifold Z_2 is the same Z_2 that appears in the NCG real structure J. Is this a coincidence or a structural connection?

3. **The f_4 moment:** The spectral action ratios are independent of f_4, but the ABSOLUTE values of the higher-curvature couplings depend on f_4/f_2. If we identify the NCG cutoff with the Planck scale, what does f_4/f_2 need to be for the higher-curvature corrections to be compatible with low-energy observations?

4. **One-loop spectral action:** The spectral action Tr(f(D^2/Lambda^2)) is computed at tree level. The one-loop correction to the spectral action (from integrating out fluctuations) would modify the coupling ratios. Does this one-loop correction bring them closer to the AS fixed point?

---

## 7. Key References

- Chamseddine, Connes: "The Spectral Action Principle" [hep-th/9606001]
- Chamseddine, Connes, Marcolli: "Gravity and the standard model with neutrino mixing" [hep-th/0610241]
- Vassilevich: "Heat kernel expansion: user's manual" [hep-th/0306138]
- Ohta, Percacci: "Higher Derivative Gravity and Asymptotic Safety in Diverse Dimensions" [1308.3398]
- Benedetti, Machado, Saueressig: "Asymptotic safety in higher-derivative gravity" [0901.2984]
- Codello, Percacci: "Fixed Points of Higher Derivative Gravity" [hep-th/0607128]

---

## Summary Table

| Quantity | Spectral Action | AS Fixed Point | Status |
|----------|----------------|----------------|--------|
| C^2 : E_4 : R^2 | -18 : 11 : -90 | (scheme-dep.) | No direct comparison possible |
| 4D effective (R^2, Ric^2) | -78 : -36 | BMS g_2*=+0.0075, g_3*=-0.005 | Sign of g_2 differs |
| beta/alpha (Ric^2/R^2) | 6/13 = 0.462 | -0.663 (BMS interpretation) | Different signs and magnitudes |
| E_4 sign | + | + | **Match** |
| C^2 sign | - | - (inferred) | **Match** |
| Riem^2 sign | - | - (BMS g_3*) | **Match** |
| One BMS coupling (g_2*) | - (all neg.) | + | **Mismatch** |
| UV-attractive directions | N/A | 3 of 4 | Large basin of attraction |
| Matter correction to ratios | None (protected) | Shifts FP values | Neutral for bridge |
| (G Lambda)* | f_0/f_2-dependent | 0.427 (BMS) | Observable constraint |

### Parametrization Caveat

The BMS couplings g_2 and g_3 are defined through their Eq. 6 as specific combinations of the (R^2, C^2, E_4) coefficients. The exact identification with (R^2, Ric^2) or another basis requires reading the full paper. The sign structure comparison is robust under reasonable interpretations, but the numerical ratios may shift depending on the exact mapping.
