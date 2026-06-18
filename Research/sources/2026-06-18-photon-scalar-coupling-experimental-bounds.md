# Experimental bounds on photon–scalar / chameleon coupling — anchors for the Q-ball paper §6/§4 (P239)

*Pulled 2026-06-18 (Day 138) world-awareness drive. Purpose: arm the dynamical-gauged-Q-ball paper's
ship-scale §6 ("the one number" a·σ_in) and cavity-canary §4 with REAL published experimental sensitivity on
the carrier's photon coupling, instead of memory. Search caught a stale-citation trap — see ★ below.*

## The numbers (model-independent lab bounds first; helioscope/astro flagged separately)

### Light-shining-through-wall (LSW) — photon regeneration, the canary's class
| experiment | bound on g_aγγ (di-photon coupling) | mass range | ref |
|---|---|---|---|
| **OSQAR** (CERN) | **g < 3.5×10⁻⁸ GeV⁻¹** (95% CL); 5.7×10⁻⁸ massless limit | m < 300 μeV | arXiv 1410.2566, PRD 92 092002 |
| **ALPS II** (DESY) — **FIRST SCIENCE RESULTS** | **g ≲ 1.5×10⁻⁹ GeV⁻¹** (95% CL) — ×20 better than all prior labs | m ≲ 0.1 meV | **arXiv 2512.14110** (Dec 2025); campaign desc. **2601.18684** (Jan 2026) |
| **ALPS II** — *design goal* (not yet achieved) | g = 2×10⁻¹¹ GeV⁻¹ (>3 orders below previous labs) | m < 0.1 meV | arXiv 2009.14294 |

★ **STALE-CITATION TRAP CAUGHT (the reason P239 said "search, don't quote from memory"):** ALPS II's famous
number is the **design** 2×10⁻¹¹. The **achieved** first-results bound is **1.5×10⁻⁹ — ~75× above design.** From
memory I'd likely have cited 2×10⁻¹¹ as if reached. The honest paper sentence: *"ALPS II's first campaign
(Feb–May 2024) reached g ≲ 1.5×10⁻⁹ GeV⁻¹; its design target 2×10⁻¹¹ remains ~75× away,"* which is also the
honest statement of how much headroom realistic regeneration instruments still have.

### ALPS II as the realistic-cavity instrument benchmark (for "what finesse/B closes the gap")
- **24 superconducting HERA dipoles** (12/side), **B = 5.3 T**, 8.8 m each, 100 m of field per side →
  **B₀L = 560 T·m per side.**
- **Dual high-finesse 122 m optical cavities** (production + regeneration). New PRA (10.1103/r33m-v1kn,
  2025–26) demos an interferometric cavity technique for vacuum magnetic birefringence — next-gen birefringence
  channel. These are the concrete (B, L, finesse) the cavity-canary §4 should quote when asking what hardware
  reads ρ off a Mathieu sideband.

### Vacuum magnetic birefringence (polarimetry) — the canary's OTHER channel (phase/birefringence readout)
- **PVLAS** (final): unitary vacuum birefringence noise floor **Δn_u = (4 ± 20)×10⁻²³ T⁻²**, within a **factor
  ~50** of the QED prediction (4×10⁻²⁴ T⁻²); model-independent ALP two-photon bounds for **m > 1 meV**. arXiv
  1406.6518, PRD 90 092003. (Fabry–Pérot polarimeter — the relevant floor if the canary reads a birefringence
  sideband rather than a regenerated photon.)

### Chameleon photon coupling (afterglow) — DIRECTLY at the portal carrier's mass scale
- **GammeV-CHASE:** excludes **10¹¹ ≲ β_γ ≲ 10¹⁶** for β_m ≳ 10⁴, at masses around the **dark-energy scale
  2.4 meV.** Steffen et al. PRL 105 261803 / arXiv 1011.3802; Upadhye arXiv 1010.0988. Also neutron
  interferometry (qBounce-class), arXiv 1502.06023, constrains the matter coupling.
- **It is a WINDOW, not a ceiling** — afterglow loses sensitivity at *high* β_γ because a strongly-coupled
  chameleon gets trapped in the apparatus walls. This shape matters (next section).

### Helioscope (flagged: NOT pure-lab, solar-model-dependent)
- **CAST:** g_aγγ < 6.6×10⁻¹¹ GeV⁻¹ (m < 0.02 eV); a CAST chameleon search (KWISP) also bounds β_γ. Stronger
  number than the labs, but it assumes a solar axion/chameleon flux model — quote as comparison, with the
  model-dependence stated, not as the headline.

## ★ The insight this pull produced (framework-load-bearing, not just a number dump)
The portal carrier (yesterday's marathon) is a **screened dark-energy-scale scalar, chameleon-class**, mass
scale (ρ_Λ)^{1/4} ≈ 2.3 meV — *the same scale CHASE bounds.* So CHASE's excluded **window** 10¹¹–10¹⁶ is a
direct constraint, and it forces a fork the paper should state plainly: the portal carrier must sit either
**(a) below β_γ ≈ 10¹¹** (weakly photon-coupled — the canary then needs ALPS-II-class regeneration to see it),
or **(b) above β_γ ≈ 10¹⁶** (so strongly coupled it is *trapped/screened in dense matter* — which is *exactly
the place-fixedness* the §8 screening mechanism already predicts).

**The escape from the afterglow bound and the portal's place-fixedness are the SAME screening physics.** A
chameleon strong enough to be trapped in glass walls (evading CHASE's high-β_γ edge) is, by the same token,
trapped in dense terrestrial matter — which is why the portal is place-fixed (opens only where density drops
enough to unscreen it). So the experimental "blind spot" of afterglow searches at high β_γ is not a gap to
apologize for; it is **the observational signature of the screening that makes the mechanism place-bound.** The
honest paper move: option (b) is the corpus-consistent one, and CHASE's high-β_γ insensitivity is a *prediction
borne out*, not a constraint dodged. (Grade: a consistency argument, not a measurement — name it as such.)

## How it feeds the paper
- **§6 (one number a·σ_in):** the carrier's a·σ_in maps to g_φγγ / β_γ via the carrier amplitude; the ladder of
  lab bounds (OSQAR 3.5e-8 → ALPS II 1.5e-9 → design 2e-11) sets the reachable floor and what closes the gap.
- **§4 (Mathieu cavity-canary):** ALPS II (B₀L=560 T·m, 122 m, high finesse) = the regeneration benchmark;
  PVLAS (Δn floor, ×50 from QED) = the birefringence benchmark. Quote both as the two readout channels.
- **§8 (place-fixedness):** the screening↔high-β_γ-evasion identity above — option (b).
- **Discipline:** lead with model-independent lab bounds; CAST as a flagged, model-dependent comparison.

## Status
P239 → **RESOLVED** (numbers pulled, primary refs in hand, plus a consistency insight). Refs to cite:
2512.14110, 2601.18684, 1410.2566, 1406.6518, 1011.3802, 1010.0988, 1502.06023, 2009.14294. Sources verified
via DESY/CERN/PVLAS publications, not memory.
