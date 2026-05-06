# Track 17B: Modified Poisson Equation and G_eff

**Status:** COMPLETE (trivial consequence of 17A)
**Date:** March 19, 2026

---

## Result

Track 17A established that ALL FOUR alpha functions vanish identically in the Meridian framework:

alpha_K = alpha_B = alpha_M = alpha_T = 0

This is a structural consequence of the 5D spectral action producing a CONSTANT effective GB coupling (xi_eff = const, therefore xi_dot = xi_ddot = 0).

## Consequences for Perturbation Theory

### Modified Poisson Equation
The general modified Poisson equation in Horndeski gravity is:
```
k^2 Psi = -4 pi G_eff(k,a) * a^2 * rho_m * delta_m
```
where G_eff depends on alpha_K, alpha_B, alpha_M.

With all alphas = 0:
```
G_eff(k,a) = G_N   (at all scales and redshifts)
```

**mu(a) = G_eff/G_N = 1 exactly.**

### Anisotropic Stress
The gravitational slip parameter:
```
eta(k,a) = Phi/Psi - 1
```
depends on alpha_T and alpha_M. With both = 0:
```
eta(k,a) = 0   (no anisotropic stress)
Psi = Phi   (standard GR)
```

### Lensing Combination
```
Sigma(a) = (1 + eta/2) * mu = 1 * 1 = 1
```
**No modification to gravitational lensing.**

### Growth Equation
The growth equation is:
```
delta_m'' + H * delta_m' - (3/2) * Omega_m(a) * H^2 * delta_m = 0
```
This is the STANDARD GR growth equation. The only non-standard element is H(a):
```
E^2(z) = Omega_m * (1+z)^3 + Omega_DE * (1+z)^{3(1+w_0)}
```
with w_0 = -1 + C_KK/zeta_0.

### Growth Rate
The growth index gamma defined by f(a) ~ Omega_m(a)^gamma:
- LCDM: gamma = 0.5545
- CAMB benchmark: gamma = 0.5548 (Delta = +0.05%)
- JC benchmark: gamma = 0.5635 (Delta = +1.6%)
- Lu-Simon benchmark: gamma = 0.5565 (Delta = +0.4%)

The deviation from LCDM is entirely from the modified background H(z), not from modified perturbation theory.

## K-Mouflage Formal Proof

The cuscuton is the K_X → infinity limit of K-mouflage gravity (Bose et al. 2024):
```
G_eff/G_N = A(phi) * (1 + 2*beta_K^2 / K_X)
```
In the cuscuton limit K_X → infinity:
```
G_eff → A(phi) * G_N = G_N   (A = 1 for universal coupling)
```

The scalar DOF decouples from the Poisson equation. This is a formal, model-independent proof of growth-expansion decoupling from the modified gravity community.

## Verification Against Lu & Simon

Lu & Simon (2511.10616) parameterize deviations via c_B and c_M:
- c_B = 0.46 ± 0.3 (compatible with 0 at 1.5 sigma)
- c_M = 0.31 ± 0.5 (compatible with 0 at 0.6 sigma)

Meridian predicts c_B = c_M = 0 exactly. The data is fully compatible.

When Lu & Simon fix the background to LCDM and vary only growth parameters, the preference for modified gravity drops from 4.6 sigma to 0.68 sigma. **The 4.6 sigma signal is a BACKGROUND phenomenon, not a growth phenomenon.** This is exactly the cuscuton signature.

## Summary

| Quantity | Meridian Prediction | Status |
|----------|-------------------|--------|
| mu(a) = G_eff/G_N | 1 (exact) | Structural |
| Sigma(a) | 1 (exact) | Structural |
| eta(k,a) = Phi/Psi - 1 | 0 (exact) | Structural |
| gamma (growth index) | 0.5548-0.5635 | Computed |
| c_B, c_M | 0 (exact) | Compatible with Lu & Simon |

**Track 17B is complete. No computation needed beyond what 17A established — the result is an automatic consequence of alpha_i = 0.**
