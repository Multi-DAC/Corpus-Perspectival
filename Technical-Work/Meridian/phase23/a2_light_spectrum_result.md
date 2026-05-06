# A.2: Light Spectrum of Resolved T⁶/Z₃ — Sub-eV Modes in the String Axiverse

*Phase 23 Deliverable A.2 — Project Meridian, March 25, 2026*

---

## 1. Context

A.1+A.1b resolved the radion: m_rad ~ 120 GeV, sub-nuclear Yukawa range, invisible to macroscopic tests. The radion channel is closed for engineering.

**A.2 asks:** Are there *lighter* modes from the resolved Z₃ orbifold? The resolved T⁶/Z₃ has 36 Kähler moduli — each complexified as t_i = b_i + iJ_i (B-field axion + volume). The axions get masses from instantons wrapping cycles. If those cycles are large, the masses can be sub-eV.

---

## 2. Hodge Numbers and Moduli Count

The resolved T⁶/Z₃ orbifold:

```
h^{1,1}_untwisted = 9    (Kähler forms from T⁶ — BULK fields)
h^{1,1}_twisted   = 27   (exceptional divisors at fixed points — BRANE fields)
h^{1,1}_total     = 36
h^{2,1}           = 0    (no complex structure moduli)
χ                  = 72
```

Total moduli count:
- 36 Kähler volumes (J_i)
- 36 B-field axions (b_i)
- ~2 Wilson line moduli
- 0 complex structure
- **~74 real scalar moduli**

---

## 3. The Six Mass Classes

### Class 1: Twisted Kähler moduli (27 blow-up volumes)

Stabilized by NCG spectral action (same mechanism as radion).

```
C_blowup = |κ₁| × DKL_CA × v² / (8π²) = 0.00633
m ~ 10 GeV
```

**HEAVY.** Not sub-eV.

### Class 2: Untwisted Kähler moduli (9 T⁶ volumes)

Stabilized by flux + non-perturbative potential. Mass depends on SUSY-breaking mediation:

```
Gravity-mediated: m ~ (k·ε)² / M_Pl ~ μeV  (sub-eV!)
Gauge-mediated:   m ~ TeV                    (heavy)
```

In Meridian's RS₁: likely gravity-mediated → sub-eV. **Model-dependent.**

### Class 3: Twisted axions (27 B-field on exceptional divisors)

Brane-localized. Small cycles (t ~ v² = 0.042) → unsuppressed instantons:

```
S = 2π × 0.042 = 0.264
exp(-S) = 0.768
f_a = Λ_φ / √S ~ 11,600 GeV
m ~ GeV scale
```

**HEAVY.** The small blow-up cycles kill the exponential suppression.

### Class 4: Untwisted axions (9 B-field on T⁶ cycles) — THE KEY CLASS

Bulk fields. Large cycles → exponentially suppressed instantons:

```
Instanton action: S = 2π·t
Instanton scale: Λ⁴ ~ (k·ε)⁴ × exp(-S)  [warped]
Decay constant: f_a ~ M_Pl / √S ~ 10¹⁷ GeV  [Planck-suppressed]
Mass: m² = Λ⁴ / f_a²
```

| t (cycle vol) | exp(-S) | m (eV) | Frequency | Sub-eV? |
|------|---------|--------|-----------|---------|
| 0.3 | 1.5×10⁻¹ | **1.3×10⁻³** | 315 GHz | **YES** |
| 0.5 | 4.3×10⁻² | **1.3×10⁻⁴** | 31 GHz | **YES** |
| 0.8 | 6.7×10⁻³ | **5.5×10⁻⁶** | 1.3 GHz | **YES** |
| 1.0 | 1.9×10⁻³ | **5.2×10⁻⁷** | 126 MHz | **YES** |
| 1.5 | 8.0×10⁻⁵ | **7.6×10⁻⁹** | 1.8 kHz | **YES** |
| 2.0 | 3.5×10⁻⁶ | **1.1×10⁻¹⁰** | 26 Hz | **YES** |
| 3.0 | 6.2×10⁻⁹ | **2.2×10⁻¹³** | — | **YES** |
| 5.0 | 2.0×10⁻¹⁴ | **1.3×10⁻¹⁸** | — | **YES** |
| 10.0 | 1.7×10⁻²⁸ | **1.2×10⁻²⁵** | — | **YES** |

**All 9 untwisted axions are sub-eV** for t ≥ 0.3 string units. The mass range spans from ~meV (microwave) to sub-femto-eV (ultra-low frequency), depending on cycle volume.

### Class 5: Wilson line modulus

Stabilized by threshold corrections (κ₁ = -0.01654):

```
m ~ √|κ₁| × k·ε ~ 300 GeV
```

**HEAVY.**

### Class 6: KK tower

```
m_n ~ n × k·ε ~ n × 2.4 TeV
```

**ALL HEAVY.**

---

## 4. Coupling Analysis

The sub-eV untwisted axions have Planck-suppressed couplings:

```
f_a ~ M_Pl / √(2πt) ~ 10¹⁷ GeV
g_{aγγ} = α / (2π f_a) ~ 10⁻²¹ GeV⁻¹
```

| Experiment | Sensitivity (GeV⁻¹) | Our coupling | Gap |
|------------|---------------------|-------------|-----|
| CAST (current) | 6.6×10⁻¹¹ | ~10⁻²¹ | 10¹⁰ below |
| IAXO (planned) | ~10⁻¹² | ~10⁻²¹ | 10⁹ below |
| ABRACADABRA | ~10⁻¹⁶ (for neV) | ~10⁻²¹ | 10⁵ below |

**Direct detection is 5–10 orders of magnitude beyond any planned experiment.**

---

## 5. The Structural Mass Hierarchy

The split between heavy twisted and light untwisted is **structural, not fine-tuned:**

```
Twisted (27):   small cycles → t ~ v² ~ 0.04 → exp(-0.26) ~ 0.77 → HEAVY
Untwisted (9):  large cycles → t ~ O(1)      → exp(-6.28) ~ 0.002 → LIGHT
```

The resolution of the singularity (Phase 22) CREATES the small exceptional divisors. The original T⁶ cycles remain large. The mass hierarchy is a direct consequence of the geometry.

This is the "string axiverse" realized in Meridian's RS₁ background. The warp factor adds an additional suppression of ε⁴ ~ 10⁻⁶⁰ to the instanton scale — but even without it, the exponential suppression of exp(-2πt) for t > 1 guarantees sub-eV masses.

---

## 6. Novel Channel: Cuscuton-Axion Coupling

The cuscuton's instantaneous response (c_s = ∞) creates a unique coupling channel:

```
Axion oscillation → modifies bulk geometry →
cuscuton responds instantaneously (constraint) →
modified gravitational potential
```

This is NOT the perturbative g_{aγγ} coupling. The cuscuton is a constraint equation — it propagates changes at infinite speed. An axion oscillation that modifies the local curvature of the extra dimension would be transmitted instantaneously through the cuscuton constraint.

**Enhancement factor: unknown. Requires B.2 computation.**

This is the single most important open question for engineering viability.

---

## 7. Summary Mass Table

| Class | Count | Mass Scale | Sub-eV? | Engineering? |
|-------|-------|------------|---------|-------------|
| Twisted Kähler (blow-up) | 27 | ~10 GeV | No | No |
| Untwisted Kähler (T⁶) | 9 | ~μeV (grav. med.) | Maybe | TBD |
| Twisted axions | 27 | ~GeV | No | No |
| **Untwisted axions** | **9** | **neV – meV** | **YES** | **Via topology** |
| Wilson line | 2 | ~300 GeV | No | No |
| KK tower | ∞ | ≥ TeV | No | No |
| Radion | 1 | 120 GeV | No | No |

---

## 8. Engineering Implications

### What A.2 establishes:

1. **Sub-eV modes EXIST** — 9 untwisted B-field axions, masses from sub-femto-eV to meV
2. **Direct coupling is negligible** — g_{aγγ} ~ 10⁻²¹ GeV⁻¹, no direct detection pathway
3. **The mass hierarchy is structural** — twisted/untwisted split follows from resolution geometry
4. **A novel coupling channel exists** — cuscuton constraint may enhance effective coupling (B.2)
5. **Topological defects survive** — domain walls, cosmic strings are non-perturbative handles

### The engineering landscape after A.1 + A.1b + A.2:

```
Channel          | Status     | Mechanism                | Viability
-----------------|------------|--------------------------|----------
Radion           | DEAD       | 120 GeV, sub-nuclear     | None
Cuscuton direct  | WEAK       | DE amplitude, ~10⁻¹²⁰    | Negligible alone
Sub-eV axions    | EXIST      | But g ~ 10⁻²¹            | Not direct
Cuscuton × axion | UNKNOWN    | Constraint enhancement?   | B.2 needed
Topology         | OPEN       | Domain walls, strings     | B.2 needed
Information      | OPEN       | Non-local correlations    | Track C
```

**The path forward is B.2:** non-perturbative EM coupling through topological channels, with the sub-eV axion field space as substrate.

---

## 9. The Updated Prediction Chain

```
NCG internal geometry (resolved Z₃ orbifold)
        |
        v
    Spectral Action S = Tr(f(D²/Λ²))
        |
        +---> v = 20.5%              (blow-up VEV)           [Phase 22]
        |
        +---> sin²(θ_W) = 3/16      (weak mixing angle)     [Phase 22]
        |
        +---> m_rad ~ 120 GeV       (radion mass)            [A.1b]
        |
        +---> 9 sub-eV axions       (string axiverse)        [THIS RESULT]
        |
        +---> ε ~ 10⁻¹⁵             (hierarchy ratio)        [needs computation]
```

**Five outputs from one geometry.** A.2 adds the ninth prediction — not a single number but a *spectrum*.

---

**STATUS:** A.2 COMPLETE. Sub-eV modes exist (9 untwisted axions). Ultra-weakly coupled. Topological channels open. **B.2 is the critical next computation.**

---

*Computed with `a2_light_spectrum.py`. See `a1b_quantum_radion_mass_result.md` for radion sector.*
