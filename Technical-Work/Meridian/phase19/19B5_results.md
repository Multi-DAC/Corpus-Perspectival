# 19B.5 Perturbation Isolation Test — Results

**Date:** 2026-03-22 03:42
**Platform:** gpu, [CudaDevice(id=0)]
**Runtime:** A=3617.8s, C=6849.5s, D=5295.7s, Total=15768.5s

## Model Comparison

| Comparison | DAIC | Interpretation |
|------------|------|----------------|
| A vs C (w(z) template) | +3.38 | CPL preferred |
| **C vs D (perturbation)** | **-1.91** | **Coupling undetectable** |
| A vs D (total) | +1.47 | Combined |

## mu0 Posterior

mu0 = 0.1235 +/- 0.5224

Meridian predicts mu0 = 0 (cuscuton has infinite sound speed, no gravitational slip).

## Chi-squared

| Fit | chi2 | params |
|-----|------|--------|
| A (constant w, mu=1) | 1422.67 | 4 |
| C (CPL, mu=1 — Meridian) | 1417.29 | 5 |
| D (CPL, mu0 free) | 1417.19 | 6 |

---

*Growth ODE solved via RK4 on GPU (500 steps). mu(a) = 1 + mu0*Omega_DE(a) parameterization.*

🦞🧍💜🔥♾️
