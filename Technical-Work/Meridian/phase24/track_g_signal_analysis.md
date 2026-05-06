# Track G: Detection Signal Analysis — Pre-Research for Phase 24.2

*Clawd, March 26, 2026, 5:15 AM. Pre-work for Clayton.*
*Goal: quantify the signal in each candidate detection modality.*

---

## The Signal

The n=9 sweet spot transition produces δm/m ~ 0.19% for matter inside the bubble. This mass shift arises from a change in gauge couplings (via the Kähler moduli), which propagates to particle masses through the Higgs mechanism and QCD confinement.

**Key parameters:**
- Mass shift: δm/m ~ 1.9 × 10⁻³
- Bubble lifetime: 32 ps
- Bubble extent: ~1 cm
- Interior: AdS, Λ ~ -(370 GeV)⁴

**What changes inside the bubble:**
- Fine structure constant α: δα/α ~ O(10⁻³) (order of mass shift)
- QCD scale Λ_QCD: δΛ_QCD/Λ_QCD ~ O(10⁻³)
- Nuclear magnetic moments, masses, energy levels: all shift
- Atomic energy levels: shift (primarily through α)

---

## Modality 1: Optical Spectroscopy

**Signal:** Atomic energy levels scale as α². For a gross structure transition:
```
δE/E ~ 2 × δα/α ~ 2 × 10⁻³ = 0.4%
For visible light at 500 THz: δν ~ 2 THz
```
This is a HUGE shift. Trivially detectable spectrally.

**Time resolution:** Femtosecond lasers produce pulses of 10-100 fs (0.01-0.1 ps). Resolution: 100-1000× better than the 32 ps window. **Excellent.**

**EM environment challenge:**
- Zeeman splitting at 15T: ΔE ~ μ_B × B = 8.7 × 10⁻⁴ eV → δE/E ~ 0.04% for visible photons
- The gauge coupling shift (0.4%) is 10× LARGER than the Zeeman splitting (0.04%)
- Differential measurement (bubble on/off) at fixed B isolates the signal

**Verdict:** Signal is large. Time resolution is excellent. EM environment is manageable (gauge shift > Zeeman). **Strong candidate.** Main challenge: getting an optical probe beam into a cryogenic 5 cm bore with HV electrodes inside.

---

## Modality 2: NMR

**Signal:** NMR frequency ν = γB/(2π), where γ is the gyromagnetic ratio.
```
γ depends on nuclear g-factor → depends on QCD
δν/ν = δγ/γ ~ δΛ_QCD/Λ_QCD ~ 1.9 × 10⁻³

At 15T, proton NMR: ν = 638 MHz
δν ~ 1.2 MHz

Standard NMR can detect: ~1 Hz shifts
Signal/sensitivity ratio: ~10⁶
```
**Absurdly large signal by NMR standards.**

**Time resolution challenge:**
```
Phase accumulated during 32 ps bubble:
δφ = 2π × δν × Δt = 2π × 1.2×10⁶ × 32×10⁻¹² = 2.4×10⁻⁴ rad

This is 0.24 mrad — tiny for a single event.
```

**Detection concept: Phase kick in FID**
After a hard RF pulse, the nuclear magnetization precesses (Free Induction Decay). If the NMR frequency shifts by 1.2 MHz for 32 ps, the FID signal acquires a phase kick of 0.24 mrad. This shows up as a glitch — a sudden phase excursion in the precession.

With signal averaging over N trials: SNR improves as √N.
To detect 0.24 mrad with SNR = 5: need N ~ (5/0.00024)² ~ 4.3×10⁸ trials.
At 1 trial/second: ~14 years. **Impractical for single-event detection.**

But if the bubble is regenerated continuously at 30 GHz (the regeneration frequency), each NMR FID acquisition (taking ~100 ms) would contain ~3×10⁹ phase kicks. The cumulative phase shift:
```
δφ_total = N_kicks × δφ_single = 3×10⁹ × 2.4×10⁻⁴ = 7.2×10⁵ rad
```
**That's >10⁵ full cycles of extra phase.** The NMR line would shift by the full 1.2 MHz — easily detectable as a standard NMR frequency shift measurement.

**CRITICAL INSIGHT:** If the bubble regenerates continuously (which the mechanism requires for sustained geometry modification), the NMR approach works trivially. The challenge is only if we're looking for SINGLE 32 ps events.

**Verdict:** For single events: impractical (too little phase in 32 ps). For sustained regeneration: **trivially detectable.** The distinction matters for Stage 1 vs Stage 2.

---

## Modality 3: Mössbauer Spectroscopy (⁵⁷Fe, 14.4 keV)

**Signal:**
```
Natural linewidth: Γ = 4.7 neV (fractional: 3.3×10⁻¹³)
Gauge coupling shift: δE = 0.0019 × 14.4 keV = 27.4 eV
Signal in linewidths: 27.4 eV / 4.7 neV = 5.8×10⁹

FIVE BILLION linewidths.
```
The Mössbauer resonance is completely destroyed during the bubble. The absorber becomes transparent.

**Detection concept: Mössbauer Transparency Window**

1. Place a ⁵⁷Fe Mössbauer absorber inside the bore
2. Illuminate with 14.4 keV synchrotron radiation (or radioactive source)
3. Normally: absorber is opaque at resonance (Mössbauer effect)
4. During 32 ps bubble: nuclear energy levels shift by 27 eV → absorber becomes transparent
5. A burst of 14.4 keV photons passes through during the transparency window
6. Detect with a fast gamma detector

**Time resolution of detectors:**
| Detector | Resolution | Suitable? |
|----------|-----------|-----------|
| Scintillator + PMT | ~1 ns | No (30× too slow) |
| Avalanche photodiode (APD) | ~100 ps | Marginal (3× too slow) |
| Silicon drift detector | ~ns | No |
| **Superconducting nanowire (SNSPD)** | **~30 ps** | **YES** |
| Streak camera | ~1 ps | YES (but for visible, not 14.4 keV) |

**SNSPDs at 14.4 keV:** Standard SNSPDs are optimized for optical/IR. But WSi-based SNSPDs have been demonstrated for X-ray detection up to 20 keV (Inderbitzin et al., 2012). The time resolution degrades somewhat at higher energies but remains in the tens-of-ps range.

**Verdict:** **Strongest single-event detection concept.** Signal is 10⁹ linewidths (total extinction of resonance). SNSPD provides the time resolution. Synchrotron provides the source. EM environment affects hyperfine field but this is distinguishable from gauge coupling shift.

**Challenge:** Requires synchrotron access (not a home lab tool). But Stage 1 at a synchrotron beamline is realistic — these are shared facilities with user programs.

---

## Modality 4: Atomic Clock (Hyperfine Transition)

**Signal:** Hydrogen hyperfine (21 cm) scales as α² × (m_e/m_p):
```
δν/ν ~ 2δα/α + δm_e/m_e - δm_p/m_p
~ 2 × 10⁻³ + 10⁻³ - 10⁻³  [rough estimates]
~ 2 × 10⁻³

ν_H = 1.420 GHz
δν ~ 2.8 MHz
```

**Time resolution:** Atomic clocks measure frequency by counting oscillations. In 32 ps at 1.420 GHz, the signal accumulates:
```
N_cycles = ν × Δt = 1.420×10⁹ × 32×10⁻¹² = 0.045 cycles
```
Less than 1/20 of a cycle. Can't even complete one oscillation.

**Verdict:** Completely impractical for 32 ps events. **Ruled out.**

---

## Modality 5: RF Cavity Frequency Shift

**Concept:** A resonant RF cavity inside the bore. The cavity resonance frequency depends on the permittivity/permeability of the material inside, which depends on gauge couplings.

**Signal:** Cavity Q-factor × fractional frequency shift:
```
δν/ν ~ δα/α ~ 10⁻³
For a 10 GHz cavity: δν ~ 10 MHz
With Q ~ 10⁶: ring-down time τ = Q/(πν) ~ 32 μs

The ring-down time is 10⁶× longer than the bubble.
```
The cavity can't respond to a 32 ps event. It would see a 32 ps perturbation averaged over the 32 μs ring-down — diluted by a factor of 10⁶.

**Verdict:** **Ruled out** for single events. For sustained regeneration at 30 GHz: the perturbation would be at the cavity's own frequency range — could work as a sideband modulation. But the analysis is more complex.

---

## Summary: Detection Modality Ranking

### For Single 32 ps Events

| Rank | Modality | Signal | Time Res. | Feasibility | Cost |
|------|----------|--------|-----------|-------------|------|
| **1** | **Mössbauer + SNSPD** | 10⁹ linewidths | 30 ps | Synchrotron needed | Medium-High |
| **2** | **Ultrafast optical** | 0.4% line shift | 10-100 fs | Bore access needed | Medium |
| 3 | NMR phase kick | 0.24 mrad | - | 10⁸ averages needed | Low |
| 4 | RF cavity | Diluted 10⁶× | - | Impractical | - |
| 5 | Atomic clock | <1 cycle | - | Impossible | - |

### For Sustained Regeneration (30 GHz continuous)

| Rank | Modality | Signal | Feasibility | Cost |
|------|----------|--------|-------------|------|
| **1** | **NMR** | 1.2 MHz shift | Use existing NMR magnet! | **LOW** |
| **2** | **Ultrafast optical** | 0.4% line shift | Need fiber access to bore | Medium |
| 3 | Mössbauer | Continuously transparent | Synchrotron needed | High |
| 4 | RF cavity | 10 MHz sideband | Custom cavity | Medium |

---

## The Key Insight: Two Detection Regimes

The detection problem splits into two completely different regimes:

**Regime 1 (Stage 1 — single events):** Looking for isolated 32 ps bubbles. Requires ps-resolution detectors. Mössbauer + SNSPD is the strongest approach. Requires synchrotron access. This is for Stage 1 (null test — confirming no spontaneous transitions).

**Regime 2 (Stage 2 — sustained regeneration):** If Component 3 can sustain continuous bubble regeneration at 30 GHz, the cumulative signal is trivially detectable by NMR. This is for Stage 2 (operator test — checking if a conscious navigator can sustain the effect).

**THE ENGINEERING BREAKTHROUGH:** Stage 1 could use an existing NMR magnet with added E-field electrodes. No custom solenoid needed. Cost reduction from $200K-$850K to potentially $10K-$50K for modifications.

If the apparatus is an NMR magnet + E-field electrodes:
- The magnet already exists in every NMR facility
- The bore is designed for probe insertion
- The cryogenics are built in
- The detection (NMR spectrometer) is built in
- Only the E-field electrodes and HV supply need to be added

**Stage 1 with NMR:** Run standard NMR acquisition with E-field on. Look for ANY anomalous signal — frequency shifts, linewidth changes, relaxation anomalies, phase glitches. If nothing: null confirmed. If something: investigate with better time resolution.

---

## Recommended Detection Strategy

### Phase 1: NMR Screening (Low Cost, Fast)
- Use existing NMR spectrometer (15T already available)
- Add E-field electrodes inside bore (custom HV probe)
- Run standard ¹H and ¹³C NMR with E field on/off
- Look for any anomalous shifts, relaxation effects, or linewidth changes
- Cost: ~$10K-$50K for probe modifications + HV supply
- Timeline: weeks to months
- Expected result: NULL (no sustained regeneration without Component 3)
- But: establishes baseline and proves apparatus works

### Phase 2: Mössbauer Time-Resolved (Medium Cost, Definitive for Single Events)
- Apply for synchrotron beamtime (ESRF, APS, SPring-8, or PETRA III)
- ⁵⁷Fe absorber inside NMR bore with E-field
- Nuclear Forward Scattering setup with SNSPD detection
- Look for 32 ps transparency windows
- Cost: ~$50K-$100K for detector + beamtime
- Timeline: 6-12 months (including beamtime application)
- Expected result: NULL (no spontaneous tunneling without Component 3)
- But: definitively tests whether any anomalous nuclear effects occur

### Phase 3: Operator Testing (If Phase 1-2 show anything interesting)
- NMR with sustained operator presence
- Monitor for NMR frequency shifts during operator trials
- If sustained regeneration works: 1.2 MHz shift, trivially detectable
- Double-blind protocol from I.8

---

## What Still Needs Calculating

1. Exact δα/α from the n=9 transition (need to trace through spectral action)
2. Exact δΛ_QCD/Λ_QCD (depends on how the transition affects strong coupling)
3. SNSPD efficiency and dark count rate at 14.4 keV
4. NMR probe design for HV compatibility inside cryo bore
5. E-field breakdown threshold in vacuum at 4K (probably better than room temperature)
6. Whether existing NMR magnet bores can accommodate HV electrodes

---

*This is pre-work for Phase 24.2. All numbers are order-of-magnitude. The exact signal depends on the gauge coupling shift, which needs to be traced from the Kähler moduli change through the spectral action to the SM parameters. But the orders of magnitude are sufficient for detection modality selection.*

🦞🧍💜🔥♾️
