# Track 14D: The Coincidence Problem --- Full Computation

**Date:** March 18, 2026
**Status:** COMPLETE
**Computation:** `14D_coincidence.py`

---

## 0. Setup

The Meridian framework gives dark energy an equation of state:

    w(z) = -1 + 2 kappa_0 / [Omega_DE * E^2(z)]

where:
- `kappa_0 = C_KK * Omega_DE / (2 * zeta_0)` is the KK kinetic correction
- `C_KK = (1+q_0)^2 * Omega_DE * eps_1 / [4*(1-q_0)^2]`
- `E^2(z) = Omega_m * (1+z)^3 + Omega_DE` (standard Friedmann)

Input parameters:

| Parameter | Value | Source |
|-----------|-------|--------|
| Omega_DE | 0.685 | Planck 2018 |
| Omega_m | 0.315 | Planck 2018 |
| q_0 | -0.55 | Deceleration parameter |
| eps_1 | 0.017 | GB coupling (C_GB = 2/3, spectral action) |
| zeta_0 (JC) | 0.001 | Junction conditions benchmark (13B) |
| zeta_0 (CMB) | 0.037 | Hiramatsu-Kobayashi CMB constraint (13F) |

---

## 1. kappa_0

    C_KK = (0.45)^2 * 0.685 * 0.017 / [4 * (1.55)^2]
         = 0.002358 / 9.610
         = 2.4538 x 10^-4

| Benchmark | zeta_0 | kappa_0 |
|-----------|--------|---------|
| JC | 0.001 | **8.404 x 10^-2** |
| CMB | 0.037 | **2.271 x 10^-3** |

The JC benchmark has kappa_0 roughly 37x larger than CMB, because kappa_0 ~ 1/zeta_0.

---

## 2. w(z) Evolution

| z | E^2(z) | w(z) [JC] | |1+w| [JC] | w(z) [CMB] | |1+w| [CMB] |
|---|--------|-----------|------------|------------|-------------|
| 0.0 | 1.0000 | **-0.7546** | 2.454 x 10^-1 | -0.9934 | 6.63 x 10^-3 |
| 0.1 | 1.1043 | -0.7778 | 2.222 x 10^-1 | -0.9940 | 6.01 x 10^-3 |
| 0.2 | 1.2293 | -0.8004 | 1.996 x 10^-1 | -0.9946 | 5.39 x 10^-3 |
| 0.3 | 1.3771 | -0.8218 | 1.782 x 10^-1 | -0.9952 | 4.82 x 10^-3 |
| 0.5 | 1.7481 | -0.8596 | 1.404 x 10^-1 | -0.9962 | 3.79 x 10^-3 |
| 0.7 | 2.2326 | -0.8901 | 1.099 x 10^-1 | -0.9970 | 2.97 x 10^-3 |
| 1.0 | 3.2050 | -0.9234 | 7.66 x 10^-2 | -0.9979 | 2.07 x 10^-3 |
| 1.5 | 5.6069 | -0.9562 | 4.38 x 10^-2 | -0.9988 | 1.18 x 10^-3 |
| 2.0 | 9.1900 | -0.9733 | 2.67 x 10^-2 | -0.9993 | 7.22 x 10^-4 |
| 3.0 | 20.845 | -0.9882 | 1.18 x 10^-2 | -0.9997 | 3.18 x 10^-4 |
| 5.0 | 68.725 | -0.9964 | 3.57 x 10^-3 | -0.9999 | 9.65 x 10^-5 |

**Key features:**
- At high z, w(z) -> -1 for both benchmarks (the correction is suppressed by E^2 ~ Omega_m * (1+z)^3).
- The deviation grows monotonically toward z = 0 (present epoch).
- At z = 0: |1+w| = 0.245 (JC) vs. 0.0066 (CMB).

**Observational sensitivity (sigma ~ 0.05):**
- **JC benchmark:** |1+w| drops below 0.05 at z > 1.38. Observable from z = 0 to z = 1.38.
- **CMB benchmark:** |1+w| NEVER reaches 0.05. Deviation undetectable with current sensitivity.

---

## 3. Matter-DE Equality Redshift

LCDM:

    z_eq = (Omega_DE / Omega_m)^(1/3) - 1 = (0.685/0.315)^(1/3) - 1 = 0.2956

Meridian: the effective DE density is rho_DE_eff = Omega_DE + kappa_0/E^2(z). Equality when Omega_m*(1+z)^3 = rho_DE_eff.

| Benchmark | z_eq | Delta_z from LCDM | Relative shift |
|-----------|------|-------------------|----------------|
| LCDM | 0.2956 | --- | --- |
| JC | **0.3316** | +0.0361 | **+12.2%** |
| CMB | 0.2966 | +0.0010 | +0.35% |

**The JC benchmark shifts matter-DE equality to 12% higher redshift.** The KK correction adds to the effective DE density, so equality happens earlier (higher z). The CMB benchmark shift is negligible.

---

## 4. Dynamical Onset

### 4a. Rate of change

The KK correction to DE density is delta_rho = kappa_0 / E^2(z). Its derivative:

    d/dz [kappa_0/E^2] = kappa_0 * [-3 Omega_m (1+z)^2] / E^4(z)

This is always negative (the correction grows as z decreases toward 0).

| z | d/dz [kappa_0/E^2] (JC) | d/dz [kappa_0/E^2] (CMB) |
|---|--------------------------|--------------------------|
| 0.0 | -7.94 x 10^-2 | -2.15 x 10^-3 |
| 0.1 | -7.88 x 10^-2 | -2.13 x 10^-3 |
| 0.5 | -5.85 x 10^-2 | -1.58 x 10^-3 |
| 1.0 | -3.09 x 10^-2 | -8.36 x 10^-4 |
| 2.0 | -8.46 x 10^-3 | -2.29 x 10^-4 |
| 5.0 | -6.05 x 10^-4 | -1.64 x 10^-5 |

The rate is largest (most negative) near z = 0 and decreases at high z:  the dynamics are most active *now*.

### 4b. Inflection point

Setting d^2/dz^2 [1/E^2(z)] = 0:

    d^2/dz^2 [1/E^2] = -6 Omega_m (1+z) [Omega_DE - 2 Omega_m (1+z)^3] / E^6(z)

This vanishes when:

    (1+z_infl)^3 = Omega_DE / (2 Omega_m) = 0.685 / 0.630 = 1.0873

    z_inflection = 0.0283

**This is extremely low** --- the inflection is at z ~ 0.03, essentially the present epoch. The KK correction's rate of change is *maximized* near z = 0 and has been accelerating throughout the matter-dominated era. The dynamics do not "turn on" at some special redshift --- they have been building monotonically since radiation-matter equality, with the fastest growth happening right now.

### 4c. Fractional correction to DE density

The ratio kappa_0 / [E^2(z) * Omega_DE] measures what fraction of the DE density is contributed by the KK kinetic term:

| z | Fraction (JC) | Fraction (CMB) |
|---|---------------|----------------|
| 0.0 | **12.27%** | 0.33% |
| 0.5 | 7.02% | 0.19% |
| 1.0 | 3.83% | 0.10% |
| 2.0 | 1.34% | 0.04% |
| 5.0 | 0.18% | 0.005% |

**JC benchmark:** The KK correction exceeds 1% of DE density all the way out to z = 2.33.
**CMB benchmark:** The correction never reaches 1% of DE density.

---

## 5. eps_1 Sensitivity --- The Coincidence Question

### How special is the value eps_1 = 0.017?

C_KK scales linearly with eps_1, so kappa_0 and |1+w| do too. Define:

    eps_1^crit = value of eps_1 that gives |1+w(0)| = 1

| Benchmark | eps_1^crit | eps_1 / eps_1^crit |
|-----------|-----------|-------------------|
| JC (zeta_0 = 0.001) | **0.0693** | 0.245 |
| CMB (zeta_0 = 0.037) | 2.563 | 0.0066 |

**At the JC benchmark, the actual eps_1 is only 4.1x smaller than the value that would give |1+w| = 1.** This is not fine-tuned. The deviation is O(0.25), which means eps_1 naturally produces a "moderate" departure from Lambda. This is the key number.

### What changes with different eps_1?

| eps_1 | |1+w(0)| [JC] | |1+w(0)| [CMB] | Observable? |
|-------|---------------|----------------|-------------|
| 0.0017 (10x smaller) | 0.0245 | 6.6 x 10^-4 | JC: marginal; CMB: no |
| **0.017** (actual) | **0.245** | **0.0066** | **JC: yes; CMB: no** |
| 0.17 (10x larger) | 2.454 (phantom!) | 0.066 | Both: yes, but JC has perturbative breakdown |

**At 10x smaller eps_1:** The JC deviation drops to 2.5% --- below the DESI sensitivity threshold of ~5%. The framework becomes observationally indistinguishable from LCDM even at JC benchmark.

**At 10x larger eps_1:** The JC benchmark gives w(0) = +1.45 --- the dark energy becomes phantom (w > -1) and then positive, which is ruled out. The linearized formula has broken down catastrophically. The CMB benchmark reaches |1+w| = 0.066, barely detectable.

**The NCG spectral action's value of eps_1 = 0.017 places the framework in a narrow observational window:** large enough to be detectable by DESI at the JC benchmark, small enough to remain perturbatively valid.

---

## 6. Structural Analysis

### Key redshifts

| Redshift | Value | Defined by |
|----------|-------|------------|
| z_eq (LCDM) | 0.296 | (Omega_DE/Omega_m)^(1/3) - 1 |
| z_eq (Meridian, JC) | 0.332 | Omega_m (1+z)^3 = Omega_DE + kappa_0/E^2 |
| z_inflection | 0.028 | (Omega_DE/(2 Omega_m))^(1/3) - 1 |
| z_accel (LCDM) | 0.632 | (2 Omega_DE/Omega_m)^(1/3) - 1 |

### Universal structural relations

All three characteristic redshifts are determined by the same ratio Omega_DE/Omega_m:

    (1+z_infl)^3  = Omega_DE / (2 Omega_m)     = 1.087
    (1+z_eq)^3    = Omega_DE / Omega_m           = 2.175
    (1+z_accel)^3 = 2 Omega_DE / Omega_m         = 4.349

These are related by exact factors:

    (1+z_infl) / (1+z_eq)   = 2^(-1/3) = 0.7937
    (1+z_accel) / (1+z_infl) = 4^(1/3)  = 1.5874
    (1+z_accel) / (1+z_eq)   = 2^(1/3)  = 1.2599

**The KK correction's inflection is locked to the matter-DE equality by a factor of 2^(-1/3).** This is not a coincidence and not a prediction --- it is a structural consequence of the fact that both the correction and the background cosmology are governed by the same Friedmann equation. The KK correction does not introduce an independent timescale.

### Energy budget at z = 0

| Quantity | JC | CMB |
|----------|-----|------|
| KK correction / Omega_DE | 12.3% | 0.33% |
| KK correction / total energy | 8.4% | 0.23% |

### Cosmic time fraction

At the JC benchmark, |1+w| > 1% from z = 0 all the way back to z = 3.23, spanning **88.8% of cosmic time since z = 10.** The dynamical DE epoch is not a brief window --- it is the dominant regime of late cosmology.

---

## 7. The Verdict

### What the framework does to the coincidence problem

The "old" coincidence problem asks: why is rho_DE ~ rho_m *today*? In LCDM, there is no answer --- Lambda is a constant and the matter density has been falling through it for no structural reason.

Meridian adds a dynamical correction kappa_0/E^2(z) that grows monotonically as the universe expands. This has three consequences:

**1. The coincidence is AMELIORATED, not solved.**

The KK correction shifts matter-DE equality from z_eq = 0.296 (LCDM) to z_eq = 0.332 (JC benchmark), a 12% change. The effective DE density is no longer a constant --- it grows at late times. But the *timing* of equality is still set by Omega_DE/Omega_m, which is an input parameter, not a derived quantity. The coincidence is softened (DE is dynamical, not static) but not explained (why *this* epoch?).

**2. The framework introduces no independent timescale.**

The inflection point z_infl = 0.028, the equality z_eq = 0.296, and the deceleration-acceleration transition z_accel = 0.632 are all locked to the single ratio Omega_DE/Omega_m by exact algebraic factors (2^(-1/3), 2^(1/3)). The KK correction peaks where the background cosmology is already transitioning. It amplifies the transition but does not explain why the transition happens now.

**3. eps_1 from the spectral action places the deviation in a detectable window --- but this is not a coincidence explanation.**

The NCG-determined GB coupling eps_1 = 0.017 gives |1+w(0)| = 0.245 at the JC benchmark. This is:
- Only 4.1x below the O(1) threshold
- Large enough for DESI detection
- Small enough for perturbative validity

If eps_1 were 10x smaller, the deviation would be unobservable. If 10x larger, it would be ruled out. The spectral action places eps_1 in a "Goldilocks zone" --- but whether this is anthropically selected, structurally necessary, or a numerical accident of the spectral triple is unknown. **This is a question for Track 14C (brane parameter determination), not 14D.**

### What would solve the coincidence problem

A genuine solution would require one of:
1. **Tracker behavior:** A mechanism where rho_DE follows rho_m during matter domination and then peels off. The cuscuton's infinite sound speed likely forbids this (no slow-roll tracking), but the eps_1 correction introduces finite propagation. Checking P(X) = mu^2 * sqrt(2X) + eps_1 * X for scaling solutions remains open.
2. **Structural constraint from the hierarchy:** If the same warping k*y_c ~ 35 that sets the Planck/TeV hierarchy also determines Omega_DE/Omega_m ~ 2, the coincidence would be structural. This requires computing V_eff from the full 5D potential with the stabilized radion, which is a Phase 12 calculation.
3. **Multi-field dynamics:** If the radion (integrated out in the current treatment) has residual dynamics coupled to the cuscuton, the two-field system might exhibit tracking.

### Classification

| Aspect | Status |
|--------|--------|
| Old CC problem (why Lambda_4 is small) | **SOLVED** (self-tuning, 15 sig figs) |
| New CC problem (why rho_DE ~ rho_m today) | **AMELIORATED** (dynamical DE, shifted z_eq, Goldilocks eps_1) |
| Full coincidence solution | **OPEN** (requires tracker or structural hierarchy constraint) |

The honest statement: **The coincidence problem is ameliorated but not solved.** The framework replaces a static coincidence (constant Lambda happens to equal rho_m today) with a dynamical one (the KK correction grows to O(25%) of Lambda at z = 0). The dynamics make the coincidence less sharp --- DE is not suddenly "turning on" but has been gradually deviating from Lambda for most of cosmic history (88.8% of time since z = 10 at >1% deviation). But the fundamental question --- why the asymptotic DE density Omega_DE is the same order as the present matter density --- remains unanswered within this framework. That question likely requires input from the full 5D stabilization mechanism (Phase 12) or from the spectral triple structure (Phase 14C).

---

## 8. Files

| File | Contents |
|------|----------|
| `14D_coincidence.py` | Full Python computation (all 5 parts + structural analysis) |
| `14D_coincidence_computation.md` | This document |

---

## 9. Implications for the Monograph

The coincidence analysis should be presented honestly:

1. **State the amelioration:** The KK correction makes DE dynamical, shifts z_eq by 12% (JC), and the spectral action's eps_1 places the deviation in a detectable window.

2. **State the limitation:** The framework does not solve the coincidence problem. The timing of matter-DE equality is still set by the input ratio Omega_DE/Omega_m. No independent timescale emerges.

3. **State the structural relations:** The universal ratio (1+z_infl)/(1+z_eq) = 2^(-1/3) is an exact algebraic consequence, not a prediction. Document it as framework self-consistency.

4. **State the open direction:** Tracker behavior from the full P(X) Lagrangian, and structural hierarchy from the 5D stabilization, are the two paths toward a complete solution.
