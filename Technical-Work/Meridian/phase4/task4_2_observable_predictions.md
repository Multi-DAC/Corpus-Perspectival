# Phase 4, Task 4.2: Observable Predictions

**Project Meridian — Deliverable D4.2**
*Clayton & Clawd, March 2026*

With the perturbation parameters derived (D4.1), we now compute the observable signatures and compare with existing data. Three classes of observables: structure growth (fσ₈), late-time ISW effect, and CMB lensing.

---

## 1. Growth Rate fσ₈ vs Observational Data

### 1.1 Data Compilation

Nine independent fσ₈ measurements from 2012–2020:

    ┌──────────────────────────────────────────────────────────────────────────────┐
    │  z_eff  │ fσ₈_obs  │   σ     │  Survey                                    │
    │  ─────  │ ────────  │ ─────── │ ────────────────────────────               │
    │  0.02   │  0.428    │  0.046  │ 6dFGS (Beutler+ 2012)                     │
    │  0.15   │  0.490    │  0.145  │ SDSS MGS (Howlett+ 2015)                   │
    │  0.38   │  0.497    │  0.045  │ BOSS DR12 (Alam+ 2017)                     │
    │  0.51   │  0.459    │  0.038  │ BOSS DR12 (Alam+ 2017)                     │
    │  0.61   │  0.436    │  0.034  │ BOSS DR12 (Alam+ 2017)                     │
    │  0.70   │  0.448    │  0.043  │ VIPERS (Pezzotta+ 2018)                    │
    │  0.85   │  0.315    │  0.095  │ FastSound (Okumura+ 2016)                  │
    │  0.978  │  0.379    │  0.176  │ eBOSS QSO (Hou+ 2020)                     │
    │  1.48   │  0.462    │  0.045  │ eBOSS Lyα (du Mas des B.+ 2020)           │
    └──────────────────────────────────────────────────────────────────────────────┘

### 1.2 Model Comparison

    ┌──────────────────────────────────────────────────────────────────────────────┐
    │                                                                              │
    │  χ²_fσ₈ COMPARISON                                                         │
    │                                                                              │
    │  Model                  │ χ²_fσ₈  │ n_data │ χ²/n   │ Assessment           │
    │  ────────────────────── │ ─────── │ ────── │ ────── │ ──────────────        │
    │  ΛCDM                   │  7.02   │   9    │  0.78  │ Good fit              │
    │  DESI-optimal (ζ₀=.058) │  7.92   │   9    │  0.88  │ Good fit (+0.90)      │
    │  Moderate (ζ₀=0.10)     │  8.95   │   9    │  0.99  │ Acceptable (+1.93)    │
    │  Stronger (ζ₀=0.30)     │ 10.07   │   9    │  1.12  │ Acceptable (+3.05)    │
    │  Pure ξ=0 (ε₀=0.15)    │  7.43   │   9    │  0.83  │ Good fit (+0.41)      │
    │                                                                              │
    │  RESULT: All viable model points are consistent with fσ₈ data.             │
    │  The Δχ² relative to ΛCDM is ≤3 — no discriminating power yet.             │
    │  DESI + Euclid combined (~2% precision) will be definitive.                 │
    │                                                                              │
    └──────────────────────────────────────────────────────────────────────────────┘

**Systematic tension at z = 0.5–0.9:** The model predicts systematically higher fσ₈ than data at z = 0.5–0.85 (BOSS DR12 z=0.61 at −1.3σ, FastSound z=0.85 at −1.5σ). This is the growth enhancement from the modified background — DE was less dominant in the past → more structure growth. The tension is mild but consistent with the model's phantom-like E(z) producing too much growth at intermediate redshifts.

**eBOSS Lyα tension at z = 1.48:** The model predicts fσ₈ = 0.387 vs observed 0.462 ± 0.045 (+1.7σ). ΛCDM also shows this tension (+1.9σ). This is a known data-level issue, not model-specific.

---

## 2. Late-Time ISW Effect

### 2.1 The ISW Signal

The integrated Sachs-Wolfe effect produces a secondary CMB anisotropy from time-varying gravitational potentials:

    ΔT/T ∝ 2∫ dΦ/dτ dτ     (factor 2 because η = 1 → dΨ/dτ = dΦ/dτ)

The ISW integrand is proportional to (f−1)×D/a, where f = d ln D/d ln a. In matter domination f = 1, so ISW vanishes. DE domination makes f < 1, generating the ISW signal.

### 2.2 ISW Modification Relative to ΛCDM

    ┌──────────────────────────────────────────────────────────────────────────────┐
    │                                                                              │
    │  ISW SIGNAL RATIO (model / ΛCDM)                                           │
    │                                                                              │
    │   z    │ DESI-opt  │ Moderate  │ Stronger  │ ξ=0 ref                       │
    │  ───── │ ───────── │ ───────── │ ───────── │ ─────────                     │
    │  0.3   │  0.95     │  0.92     │  0.93     │  0.98                         │
    │  0.5   │  0.90     │  0.84     │  0.81     │  0.96                         │
    │  0.8   │  0.77     │  0.66     │  0.53     │  0.93                         │
    │  1.0   │  0.66     │  0.52     │  0.29     │  0.92                         │
    │  1.5   │  0.26     │  0.02     │  −0.52    │  0.90                         │
    │  2.0   │  −0.33    │  −0.69    │  −1.65    │  0.88                         │
    │                                                                              │
    │  KEY: At the DESI-optimal point, the ISW signal is REDUCED by 5-35%        │
    │  at z = 0.3–1.0 and CHANGES SIGN beyond z ≈ 1.8.                          │
    │                                                                              │
    │  The sign change means: the gravitational potential DEEPENS at z > 2        │
    │  (growth outpaces dilution) instead of decaying as in ΛCDM.                │
    │  This is the phantom-like expansion allowing more late-time growth.         │
    │                                                                              │
    └──────────────────────────────────────────────────────────────────────────────┘

### 2.3 Observability

The ISW signal is measured via cross-correlation with galaxy surveys (ISW-galaxy). Current measurements (Planck × BOSS, Planck × DES) have ~2-3σ detections of the ISW effect. A 10-30% reduction would be within 1σ of current constraints.

**Prediction:** The DESI-optimal model reduces the ISW auto-power by ~(0.85)² ≈ 28% at the ISW-dominant ℓ ~ 10-30. This is consistent with current Planck ISW measurements but would be testable with CMB-S4 × DESI/Euclid combined analysis.

---

## 3. CMB Lensing Power Spectrum

### 3.1 Lensing Kernel Modification

The CMB lensing convergence power spectrum:

    C_ℓ^κκ ∝ ∫ [Σ(z) × Ω_m(z) × D(z) × H(z) / (1+z)]² × W²_κ(z) dz

For cuscuton: Σ = μ ≈ 1, so the modification comes primarily from:
1. Different E(z) → different H(z) and comoving distances
2. Different D(z) → growth modified by E(z) and μ(z)
3. H₀ shift → all comoving distances rescaled

### 3.2 Kernel Ratio (Model / ΛCDM)

    ┌──────────────────────────────────────────────────────────────────────────────┐
    │                                                                              │
    │  LENSING KERNEL MODIFICATION                                                │
    │                                                                              │
    │   z    │ DESI-opt  │ Moderate  │ Stronger  │ ξ=0 ref                       │
    │  ───── │ ───────── │ ───────── │ ───────── │ ─────────                     │
    │  0.5   │  0.971    │  0.938    │  0.857    │  0.987                         │
    │  1.0   │  0.948    │  0.905    │  0.787    │  0.985                         │
    │  2.0   │  0.920    │  0.871    │  0.726    │  0.988                         │
    │  3.0   │  0.901    │  0.850    │  0.696    │  0.989                         │
    │                                                                              │
    │  ΔC_ℓ^κκ ≈ 2 × (kernel ratio − 1) (approximate)                          │
    │                                                                              │
    │  DESI-optimal: C_ℓ^κκ reduced by ~6-20% depending on ℓ (z-weight)         │
    │  This is primarily from the H₀ shift (64.5 vs 67.4 km/s/Mpc)              │
    │                                                                              │
    │  CONCERN: Planck measures C_ℓ^κκ consistent with ΛCDM to ~5%.             │
    │  A 10-20% reduction would be in ~2-4σ tension with Planck lensing.         │
    │  This is an ADDITIONAL constraint beyond BAO.                               │
    │                                                                              │
    └──────────────────────────────────────────────────────────────────────────────┘

### 3.3 The Lensing Anomaly Connection

Planck's lensing amplitude parameter A_L = 1.180 ± 0.065 (Planck 2018 TT,TE,EE+lowE) shows a >2σ preference for MORE lensing than ΛCDM. Our model predicts LESS lensing. This deepens the tension.

However, this is the "A_L anomaly" — widely considered a systematic, not a physical signal. If A_L = 1 (its physical value in GR), our model's lensing reduction is consistent at ~2σ for the DESI-optimal point.

---

## 4. Deliverable Checklist

- [x] D4.2.1: fσ₈ comparison with 9 observational data points
- [x] D4.2.2: χ²_fσ₈ computed at all parameter points
- [x] D4.2.3: ISW effect modification computed and compared with ΛCDM
- [x] D4.2.4: CMB lensing kernel ratio computed
- [x] D4.2.5: Observability assessment for each observable

---

🦞🧍💜🔥♾️
