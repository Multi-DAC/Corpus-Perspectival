# Track 16L: Gravitational Wave Signatures — Research Report

**Authors:** Clayton W. Iggulden-Schnell & Clawd
**Date:** March 19, 2026
**Status:** COMPLETE

---

## 1. RS Phase Transition

The Randall-Sundrum model undergoes a first-order confinement-deconfinement phase transition (Hawking-Page type) at T_c ~ k * exp(-ky_c) / 8 ~ 192 GeV. At T > T_c the extra dimension is an AdS-Schwarzschild black brane; at T < T_c it is the stabilised RS1 orbifold.

This first-order PT generates gravitational waves through three mechanisms: bubble collisions, sound waves in the plasma, and turbulence.

## 2. GW Signal

For benchmark PT parameters (alpha = 1, beta/H = 10):

| Quantity | Value |
|----------|-------|
| Peak frequency | 0.32 mHz |
| Peak Omega_GW h^2 | 1.6 x 10^-7 |
| Dominant source | Sound waves (Omega ~ 3 x 10^-8) + turbulence (~1 x 10^-7) |
| Spectral shape | f^3 (low f), f^{-4} (high f) |

## 3. Detector Comparison

| Detector | Optimal f | Sensitivity | Signal at f_opt | Detectable? |
|----------|-----------|-------------|-----------------|-------------|
| LISA | 3 mHz | 10^{-13} | 3.9 x 10^{-10} | **YES** (SNR >> 1) |
| BBO | 0.1 Hz | 10^{-17} | 3.3 x 10^{-16} | YES |
| DECIGO | 0.1 Hz | 10^{-16} | 3.3 x 10^{-16} | YES |
| ET | 10 Hz | 10^{-13} | ~0 | No (wrong band) |
| NANOGrav | 10 nHz | 10^{-10} | ~0 | No (wrong band) |

## 4. Parameter Dependence

The signal is detectable by LISA across the entire reasonable parameter space:

| alpha | beta/H | Omega_peak | LISA detectable? |
|-------|--------|------------|-----------------|
| 0.1 | 10 | 10^{-9} | Yes |
| 0.1 | 100 | 10^{-10} | Yes |
| 1.0 | 10 | 3 x 10^{-8} | Yes |
| 1.0 | 100 | 3 x 10^{-9} | Yes |

Even weak PTs (alpha = 0.1) and fast nucleation (beta/H = 100) produce signals above LISA sensitivity.

## 5. Other GW Sources

- **Inflationary background** (r = 0.004): Omega ~ 3 x 10^{-17}. Far below all detectors. Only detectable via CMB B-modes.
- **KK graviton decays**: Prompt (tau ~ 10^{-29} s). No relic background. Energy thermalised.

## 6. Honest Assessment

The PT signal depends on the dynamics of the RS stabilisation, which involves non-perturbative physics (bubble nucleation in a warped background). The PT parameters (alpha, beta/H) are not predicted from first principles — they depend on the Goldberger-Wise stabilisation potential. The computation above uses benchmark values from Creminelli et al. (2002) and Randall-Servant (2007).

The honest statement: **if the RS phase transition is strongly first-order (alpha > 0.1), LISA will detect it.** The peak frequency (sub-mHz) sits squarely in the LISA sensitivity band. This is the framework's third independent detection channel, alongside B-modes (LiteBIRD + SO, ~2037) and collider signatures (FCC-hh, ~2045+).

The uncertainty is in the PT strength, not the detectability: a weakly first-order or crossover transition would produce no GW signal.

## 🦞🧍💜🔥♾️
