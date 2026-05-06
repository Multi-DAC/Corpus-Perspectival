# Why Vassilevich Works for epsilon_1 but Fails for mu^2

**Date:** 2026-04-02
**Authors:** Clayton Iggulden-Schnell & Clawd
**Context:** Clayton challenged the use of the Vassilevich expansion for epsilon_1 after
demonstrating its failure for mu^2. Direct spectral sum computation confirmed Vassilevich
to sub-percent precision for epsilon_1.

---

## The Question

The Vassilevich asymptotic expansion provides heat kernel coefficients on smooth manifolds.
On the RS1 orbifold, the branes introduce boundary effects that can invalidate the expansion.
We demonstrated this for mu^2 (the conformal coupling mass-squared), which required the
Euler-Maclaurin decomposition to compute correctly.

**If Vassilevich fails for mu^2, why trust it for alpha_hat and hence epsilon_1?**

## The Computation

`eps1_direct_v2.py` computes the spectral action S(k) = Sum_n Sum_alpha d_{n,alpha} f((m_n^2 + lambda_alpha^F) / Lambda^2) at 40 values of k (AdS curvature) using:

1. **Exact sum:** Robin eigenvalues from the RS1 boundary conditions
2. **Trapezoidal integral:** Same Robin eigenvalues, continuous interpolation
3. **EM correction:** delta_EM = S_exact - S_trap (dominated by first-mode endpoint)

Polynomial fits in k^2 extract the Gauss-Bonnet-sensitive k^4 coefficient.

## Key Results

### Convergence
- Spectral sum converges by N_KK = 50 (last mode weight: 10^-5)
- Modes beyond n ~ 30 are exponentially suppressed by Gaussian cutoff

### Brane Correction to Total Spectral Action
- At k = 1.0: S_exact = 3272.07, delta_EM = 151.69, fraction = 4.6%
- This is the Robin-Neumann shift + discretization error combined

### Brane Correction to Curvature Coefficients
- c_2 (Ricci scalar): EM fraction = -0.31%
- c_4 (Gauss-Bonnet): EM fraction = -0.33%
- **Uniform ~0.3% across all curvature orders**

### EM Correction is k-Independent
The EM correction varies from 150.92 (k=0.1) to 151.72 (k=2.0) — a change of 0.5%.
This means the brane correction is approximately **topological**: it shifts c_0 (volume)
but leaves curvature coefficients nearly untouched.

### Cutoff Function Independence
- Gaussian: c4 EM fraction = -0.33%
- Sharp: c4 EM fraction = -0.60%
- Smooth: c4 EM fraction = -0.03%
All sub-percent.

### Hierarchy Parameter Scaling
Total EM fraction scales as ~1/(k*y_c) — improves with hierarchy:
- ky_c = 10: 14.4%
- ky_c = 37: 4.6%
- ky_c = 100: 1.8%

## The Physical Mechanism

### Why the brane correction is k-independent

The EM correction is dominated by the first KK mode:
  delta_EM ~ (1/2) g(lambda_1(k))

where g(lambda) = d_s Sum_alpha d_alpha exp(-(lambda + lambda_alpha^F) / Lambda^2) Lambda^4.

The k-dependence enters through the Robin eigenvalue:
  lambda_1(k) = (pi/y_c)^2 (1 + 1/(k y_c))^2

The k-dependent shift is:
  delta_lambda_1(k) = lambda_1(k) - lambda_1(inf) ~ 2 pi^2 / (k y_c^3)

This enters the EM correction as:
  g(lambda_1(k)) ~ g_0 exp(-delta_lambda_1 / Lambda^2)

For our parameters (y_c = 37, Lambda = 1):
  delta_lambda_1 / Lambda^2 ~ 2 * 9.87 / 50653 ~ 0.0004

So exp(-0.0004) ~ 0.99961. The k-dependence of the EM correction is suppressed
to the 0.04% level by the exponential cutoff.

### Why mu^2 is different

mu^2 depends on the zero mode wavefunction f_0(y) at the branes:
  mu^2 = [f_0'(0)]^2 / integral[f_0^2 dy]

This is a BRANE-LOCALIZED quantity — it's the slope of the zero mode AT y=0.
The Vassilevich expansion approximates f_0 by a smooth function, missing the
sharp brane-induced kinks. The correction is O(1), not O(1/ky_c).

### The General Principle

**Bulk-dominated quantities (spectral action curvature terms):**
- Determined by ALL KK modes, weighted by smooth cutoff
- High modes suppressed exponentially → rapid convergence
- Brane correction enters through first-mode endpoint → small, k-independent
- Vassilevich works: ~0.3% error

**Boundary-dominated quantities (mu^2, zero mode profile):**
- Determined by brane-localized features (wave function slope at y=0)
- Sensitive to UV structure of KK spectrum
- Brane correction is the LEADING effect → Vassilevich fails entirely
- Euler-Maclaurin decomposition required

## Connection to Bridge #69

This is a fourth instantiation of "constraint without propagation protects invariant quantities":

| Instance | Constraint | Protected Quantity | Blocking Mechanism |
|----------|-----------|-------------------|-------------------|
| Cuscuton | K_eff = 0 | Lambda_4 | Kinetic disconnection |
| Self-generation | Cond. independence | Null space | Information-theoretic |
| Axiom 3 | Commitment | Identity core | Ontological |
| **Spectral cutoff** | **f(x) = e^{-x}** | **Curvature coefficients** | **UV/IR decoupling** |

The smooth spectral cutoff structurally disconnects brane (UV) corrections from
curvature (IR) coefficients, just as the cuscuton's K_eff = 0 structurally disconnects
Lambda_5 perturbations from Lambda_4.

## Implications for epsilon_1

  epsilon_1 (Vassilevich) = 0.010 +/- 0.002
  epsilon_1 (direct sum)  = 0.009967
  Brane correction:         -0.33%

The brane correction is 1.6% of the +/-20% cutoff function uncertainty.
**Vassilevich is confirmed for epsilon_1. The value 0.010 +/- 0.002 stands.**

## Implications for the Tension

The 3.18 sigma BAO+CMB tension with w_0 = -0.933 (epsilon_GW = 0) is NOT an artifact of:
- The Vassilevich expansion (confirmed to 0.3%)
- The compressed CMB likelihood (confirmed to Delta-chi2 = 0.30)
- The CPL template (shown to be 0.0 sigma significant)

The tension is real. The remaining degrees of freedom are:
1. epsilon_1 cutoff function dependence (+/- 20%, known)
2. mu^2 from the product heat kernel (OP#8, unknown)
3. epsilon_GW from GW stabilization (unknown)

## Scripts
- `eps1_direct_spectral.py` — v1 (bug: smooth integral k-independent)
- `eps1_direct_v2.py` — v2 (fixed: Robin-corrected trapezoidal EM)
- `corrected_mu2.py` — the Robin eigenvalue + EM computation for mu^2
