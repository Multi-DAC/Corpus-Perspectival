# Phase C — Mathieu cavity-gain map: the carrier sideband's observability (2026-06-17)

**Result of `portal-mathieu-cavity-2026-06-17.py`.** Completes the dynamical-Q-ball program (A profile ✓,
B modes ✓ [breathing flat + ω_pin], C this, D densitometer ✓). Operationalizes the paper's qualitative
"gain ~ finesse × aσ_in" (§ cavity-birefringence) into a quantitative (coupling a, density ρ, finesse F)
observability map, with the Mathieu parametric structure the FOLLOWUP-SEED asked for — reframed for the
CARRIER (ω≈m, 556 GHz), since the breathing mode ω_b was falsified flat.

## The physics
Wall field σ(x,t)=σ_in e^{iωt} modulates the dilatonic photon coupling e^{aσ}F² → the intracavity field obeys
a Hill/Mathieu equation `a'' + 2γa' + ω_c²[1 + h cos ωt]a = 0`, γ=ω_c/(2F), per-pass modulation **h = a·σ_in**.
Two observables:
- **Sideband comb** (below threshold): finesse-enhanced phase index β=F·h; detectable when F·h/2 > φ_noise (~1e-10 rad).
- **Parametric oscillation** (Mathieu principal tongue, ω=2ω_c): threshold h≈2/F → onset at F·h > ~2.

## Results (operating point ρ₀~4.3 g/cm³, σ_in=φ_min=2.9 meV; B enters as O(1) birefringence enhancement)
| coupling a = 1/M | h = aσ_in | F_thresh COMB | F_thresh PARAMETRIC |
|---|---|---|---|
| gravitational (1/M_Pl) | 1.2e-30 | 1.7e20 | 1.7e30 |
| GUT (1/1e25 eV) | 2.9e-28 | 6.9e17 | 6.9e27 |
| intermediate (1/1e16 eV) | 2.9e-19 | **6.9e8** | 6.9e18 |
| TeV (1/1e12 eV) | 2.9e-15 | **6.9e4** | 6.9e14 |
| eV (1/1 eV) | 2.9e-3 | <1 | 6.9e2 |
| field-natural (1/meV) | 2.9 | <1 | 0.7 |

Achievable: optical F~1e6, SC microwave F~1e11.

## Three robust conclusions
1. **Observability spans ~30 orders, set ENTIRELY by the dilatonic coupling a.** Gravitational coupling →
   hopeless (F~1e20). The comb is reachable at **a ≳ 1/1e16 eV (SC microwave F~1e11)** and comfortably at
   **a ≳ 1/TeV (optical F~1e6)**. Parametric self-oscillation only near field-natural coupling.
2. **The comb is ~10 orders easier than parametric oscillation** (F·h > 2e-10 vs > 2). The comb is the lead
   observable; the Mathieu instability is the dramatic-but-distant upper end.
3. **Lower density is EASIER** — F_thresh ∝ 1/σ_in ∝ ρ^{-(n+2)/(2(n+1))}. At air density σ_in~174 meV →
   F_thresh ~1e-12 (trivial). **Probe the low-density HALO, not the dense substrate-anchored wall** — which
   stitches Phase C to tonight's substrate-anchoring result (the wall anchors in solid; the cavity reads the halo).

## The verdict (matches the paper: a bound, or a detection if the coupling is strong)
- A cavity null at optical F~1e6 **bounds** a < ~1/TeV (at the operating σ_in); at SC-microwave F~1e11, a < ~1/1e16 eV.
- The e^{aσ}F² channel is to the PHOTON, so it **bypasses the matter-screening** that limits the mechanical
  probes — the cavity's key advantage. Even a null is a coupling bound, not a failure.
- IF the dilatonic coupling is intermediate-to-strong, the **556 GHz comb is detectable** (FSR-matched 270 µm
  cavity or N≈371 on a 10 cm one); the experiment is mature-technology.

## Caveats (evidence-grade)
- ROBUST: the 30-order coupling span, the ~10-order comb/parametric gap, the inverse-density scaling, the
  bound-vs-detection verdict. ORDER-OF-MAGNITUDE: absolute F_thresh (φ_noise choice, B² geometry, O(1) factors).
- Framework-level (the carrier-modulation mechanism); the static EM signatures remain the falsifiable floor.

## Status: dynamical-Q-ball program COMPLETE
A (existence/profile) ✓ · B (breathing flat + ω_pin translational) ✓ · C (Mathieu cavity map) ✓ ·
D (carrier-blueshift densitometer, gradient-free) ✓. Forward: fold C's "probe-the-halo" + the coupling-bound
map into the paper's cavity section; a dynamical-gauged-Q-ball follow-on (densitometer + cavity map) is now a
complete spine. Related: [[portal-quantitative-densitometer-RESULTS-2026-06-17]], [[portal-fixedQ-carrier-RESULTS-2026-06-17]], LC48.
