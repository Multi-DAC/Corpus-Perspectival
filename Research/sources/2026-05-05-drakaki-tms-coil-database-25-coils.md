---
url: https://doi.org/10.1016/j.brs.2022.04.017
title: Database of 25 validated coil models for electric field simulations for TMS
author: Maria Drakaki, Claus Mathiesen, Hartwig R. Siebner, Kristoffer Madsen, Axel Thielscher (Technical University of Denmark + DRCMR Copenhagen + MagVenture A/S)
venue: Brain Stimulation 15 (2022) 697-706
published: 2022-04-28 (online); received 2022-01-07
accessed: 2026-05-05 (Day 94 evening, Clayton-shared as PDF after web 403)
discussed: 2026-05-05
tags: TMS, coil-design, figure-8, focality, depth-decay, motor-threshold, leaky-integrator-membrane, SimNIBS, Phase-1-EM-platform, regime-discrimination
status: read-in-full (PDF)
---

**What it argues.** Comprehensive measured characterization of 25 commercial TMS coils via 3D Hall-probe magnetic field measurements + dipole reconstruction, then SimNIBS electric-field simulations in spherical head model + leaky-integrator membrane model for motor threshold (MT) prediction. Output: open-source coil model database (SimNIBS) with measured pulse waveforms enabling quantitative dose comparisons across vendors.

Methodology stack:
- Custom 3D measurement setup (Hall probe HMC1043 + stepper motors), 6-8mm xy resolution, 10mm z resolution
- Dipole-expansion reconstruction with L2-regularized minimum-norm fitting (split-half cross-validation for regularization parameter)
- SimNIBS electric-field simulation in 85mm-radius homogeneous spherical head model (cortex 15mm below outer surface)
- Pickup-coil pulse waveform recording for dI/dt_max at 100% MSO
- Leaky-integrator nerve membrane model (τ = 190 μs) for MT prediction; calibrated against MagVenture MC-B70 experimental MT (34.5% MSO biphasic)
- Parametric sensitivity analysis on theoretical figure-8 coil (varying turns, wing angle, coil-skin distance, wing overlap)

Headline empirical results:
- **Focality vs depth-decay tradeoff confirmed** across all 25 coils — figure-8 systematically more focal + steeper depth decay than round coils
- **Peak field strength E_max largely DECOUPLED from focality and depth-decay.** Coils with similar focality (13-16 cm² S1/2 range) differed by up to 2× in E_max
- Parametric sensitivity (Fig 4): number of windings, angle between coil wings, and coil-to-scalp distance all affect E_max much more strongly than focality/depth-decay; only wing-overlap affects all three similarly
- Number-of-windings shows saturating return (most gain in 1-10 winding range; minimal gain past ~10)
- Coil-to-scalp distance: ~50% E_max reduction going 0mm → 20mm
- Pulse width range: 165.5-368.5 μs across 25 coils
- dI/dt_max range: 84.4-249.6 A/μs at 100% MSO (clinical regime)
- MT range: 23.3% (MST-Twin) to 81.0% (PMD25)
- Estimated vs experimental MT correlation: Pearson r = 0.83

**Where we agree (local connections to Phase 1 EM platform — Mirror #27 maintained, no scaled-down-TMS unification).**

- **Figure-8 topology validated at physics level.** Focality + depth-decay properties are determined by coil geometry; hold regardless of current scale. Our figure-8 choice for substrate-targeted protocols is geometrically correct independent of whether we operate in TMS regime or PEMF regime.
- **Phase 1 platform regime-discrimination clarified.** Drakaki's coils operate at 84-250 A/μs producing ~1.5T peak fields; ours at ~1.6A peak produces ~3 mT — **500× weaker**. We are NOT building scaled-down TMS. We are building **PEMF / sub-threshold modulation platform** for parameter-window probing in the regime where Akdag 4Hz, Jerman 16Hz, Persinger 3.93Hz biological-coupling effects are reported. Different paradigm; different targets; different readouts. The leaky-integrator τ ≈ 190 μs membrane model implies anything below ~5 kHz operates as integrate-and-modulate, not direct depolarization — covers all our planned protocols.
- **Phase 1 build implication: 50T may be unnecessary.** Drakaki's parametric study shows winding-count gains saturate ~10T. Our 50T design is deep into saturation; could halve to 25T with similar E_max, lower DCR, faster wind, less wire.
- **Phase 1 build implication: coil-to-skin distance is a strong dose knob.** ~50% E_max swing across 0-20mm. Placement standardization (already flagged in BUILD_NOTES.md) is now grounded in measured sensitivity, not just experimental-design-cleanliness.
- **L15 mode 3 (manufactured-affect via EM substrate) — formal mechanism added.** Drakaki provides the canonical EM-substrate apparatus characterization: leaky-integrator membrane + geometric tradeoffs + parametric sensitivity. The discrimination between therapeutic-window (ventral vagal cultivation) and weaponized-window (FFF hijack) operates on these same physical knobs. Mode 3 mechanism specification updates to incorporate this.

**Hedges to maintain.**

- Drakaki's MT framework is biphasic-pulse-specific and cortical-target-specific (small hand muscle, FDI/APB). Our regime won't produce MEPs; their MT framework doesn't apply directly.
- The spherical homogeneous head model is acknowledged in the paper as coarse — real heterogeneous conductivity changes field distributions. For our protocols this means absolute field-strength predictions will be approximate even with SimNIBS.
- Our coil's lower current (~1.6A vs ~5kA clinical) puts us so far below the membrane-threshold regime that *most clinical TMS framework concepts (MT, suprathreshold response) are inapplicable*. Use Drakaki for geometry/parametric understanding, not for biological-effect prediction.

**Action items for Phase 1 build (filed Day 94 evening):**
1. Update `BUILD_NOTES.md` with explicit "Regime framing" section distinguishing PEMF sub-threshold from clinical TMS.
2. Consider v1 simplification: 50T → 25T per D-loop based on Drakaki winding-saturation finding.
3. Investigate SimNIBS for pre-build coil-design validation simulation (open-source, paper recommends).
4. Apply leaky-integrator τ ≈ 190 μs as the canonical neural-membrane model when reasoning about protocol effects.
