# Home Experiment: 121 GHz Plasma Boundary Resonance Test

*Designed March 28, 2026. Budget: $400-1700. Location: Portland home lab.*

---

## What We're Testing

**Primary prediction:** Self-organized plasma boundaries exhibit anomalous threshold behavior — a sharp onset of unexpected properties above some critical parameter.

**Secondary prediction:** The anomaly peaks at or near 121 GHz (the first KK mode frequency for cascaded RS geometry with krc*pi = 72).

**Tertiary prediction:** The plasma self-organizes toward the threshold (Per Bak SOC).

## What Tier 0 Data Mining Found

### The field is wide open.

| Question | Answer |
|----------|--------|
| Has anyone run ECRIS at 121 GHz? | **No.** Highest ever: 75 GHz (pulsed). 45 GHz just got first plasma May 2024. |
| Has anyone measured L-H threshold vs ECRH frequency? | **No.** ITPA database doesn't even track heating frequency. |
| Has anyone tried ball lightning creation above 2.45 GHz? | **No.** Every experiment uses microwave oven magnetrons. |
| Has anyone measured microwave emission from ball lightning? | **No.** Only optical spectra exist. |
| Is lightning RF measured above 10 GHz? | **No.** Technological gap — mm-wave analyzers barely exist above 67 GHz. |
| Has anyone noted the O2 line at 118.75 GHz being 1.86% from 121 GHz? | **No.** |

### What IS known (relevant anomalies):

1. **TCV tokamak X3 at 118 GHz** produces a unique quasi-stationary ELM-free H-mode not seen at X2 (82.7 GHz). Attributed to deposition characteristics, never tested for frequency specificity. 118 GHz is 3 GHz from our prediction.

2. **ECRIS kinetic instability at Bmin/BECR ~ 0.7-0.85** is a genuine sharp bifurcation. Below: smooth scaling. Above: electron cyclotron instability, ms-scale oscillations, microwave emission bursts. Two-frequency heating suppresses it. This IS a plasma bifurcation in ECR, well-documented at JYFL (Finland).

3. **L-H transition** in tokamaks: sharp threshold, reproduced on every major machine worldwide since 1982. Trigger mechanism STILL debated after 43 years. Nobody has checked whether it's frequency-dependent.

4. **ECRIS frequency scaling "fails to follow f^2 prediction" above 20 GHz** (IMP/SECRAL, 2024). Attributed to coupling efficiency, but it's a measured deviation from smooth scaling.

5. **SOC in plasma** confirmed at TEXTOR, KSTAR, DIII-D, simple glow discharges. Plasmas DO self-organize toward critical points.

### The O2 coincidence

The molecular oxygen atmospheric absorption line sits at 118.750 GHz. Our predicted KK mode is at ~121 GHz. Separation: 2.25 GHz (1.86%). The atmosphere partially screens this frequency region. At lab scale (cm path lengths), the absorption is negligible. At atmospheric scale, it would attenuate any signal.

Nobody has noted this coincidence. It may mean nothing. But if the KK mode IS at 121 GHz, the O2 line would partially mask it in atmospheric observations while leaving it detectable in vacuum or short-path experiments.

---

## The Experiment: Four Phases

### Phase 1: Afterglow Threshold ($250-400)

*Tests: threshold prediction. No D-band equipment needed.*

**Components:**
- Borosilicate glass tube, 30 cm x 5 cm OD, with electrodes sealed in ($30-50)
- Refrigeration vacuum pump, used ($50-80)
- Vacuum gauge (Pirani or thermocouple type) ($30-60)
- Argon gas, small cylinder from welding supply ($30)
- Adjustable HV DC supply, 0-2 kV, current-limited ($80-120)
  - Options: adjustable neon sign transformer, variac + NST, or purpose-built lab supply
- Neodymium magnets, N52, various ring and block shapes ($40)
- Photodiode (BPW34 or similar) + transimpedance amplifier ($10)
- Arduino or oscilloscope for data capture ($30 if Arduino, $0 if you have a scope)
- Vacuum fittings, hose, wire, safety gear ($50)

**Total Phase 1: ~$350-440**

**Procedure:**
1. Evacuate tube to ~1-10 Torr argon
2. Strike DC glow discharge
3. Arrange magnets in mirror geometry (two rings of N52 magnets around tube, separated by ~10 cm) to create magnetic mirror that encourages double-layer formation
4. Pulse discharge: 100 ms on, 200 ms off (or adjustable)
5. Photodiode monitors luminosity decay after power cutoff
6. Record afterglow decay time constant vs:
   - Discharge current (primary variable — proportional to E*B coherence)
   - Gas pressure
   - Magnetic geometry (spacing, strength)
   - Tube geometry

**What you're looking for:**
- Plot afterglow decay time vs discharge current
- Standard physics: smooth, monotonic increase with current
- Anomaly: sharp step — short afterglow below threshold, anomalously long above
- The threshold current (if it exists) should depend on magnetic geometry (it sets B, which determines what ECR frequency the plasma supports)

**Controls:**
- Run with no magnets (removes any ECR-related physics)
- Run with magnets at different spacings (changes the effective B and thus the ECR frequency the plasma boundary supports)
- Run with different gases (helium, neon) — different masses change plasma dynamics predictably
- If afterglow shows threshold with magnets but NOT without: that's a magnetic-field-dependent threshold

**Key physics insight:** Even without an external 121 GHz source, a magnetized plasma naturally contains electrons gyrating at the local cyclotron frequency. If the magnetic field at the double layer happens to put the cyclotron frequency near 121 GHz (B ~ 4.32 T — achievable only with very strong magnets, NOT with N52 permanent magnets which top out at ~1.4 T surface field), the electrons themselves are the source. With N52 magnets, the cyclotron frequency at the plasma boundary will be ~28-39 GHz (B ~ 1-1.4 T). This is NOT at the predicted resonance.

**However:** The threshold behavior, if it exists for ANY physical reason, would show up regardless. Phase 1 tests whether plasma boundaries bifurcate at all. The specific frequency is Phase 2's job.

### Phase 2: Two-Frequency Probe ($350-1300 added)

*Tests: frequency specificity at 122 GHz vs control frequency.*

**Components (add to Phase 1):**
- 122 GHz transceiver: VK3CV board (~$300 if available) or SiRad Simple (~$1400)
  - The VK3CV board: TRX_120_001 chip + ADF4159 PLL, outputs at 122 GHz, receives via 144 MHz IF. Connect to any 2m ham receiver or SDR.
  - The SiRad Simple: complete USB radar kit, software included, raw IQ data output.
- 60 GHz control transceiver: Infineon DEMO-BGT60TR13C ($139)
- Horn antennas: 2x PME 1.5 stainless steel cake icing nozzles (~$5 total)
  - ~21 dBi gain at 122 GHz. Yes, really. UK amateur radio operators use these.
- For VK3CV: RTL-SDR dongle ($25) or 2m receiver to capture IF

**Total Phase 2 addition: ~$350 (VK3CV path) or ~$1540 (SiRad path)**

**Setup:**
- Position transmit horn on one side of plasma tube at boundary region
- Position receive horn on opposite side
- Align so beam passes THROUGH the plasma double layer
- Same geometry for both 122 GHz and 60 GHz systems (sequential, not simultaneous)

**Procedure:**
1. Establish stable discharge with magnetic geometry
2. Transmit 122 GHz CW through plasma boundary
3. Measure: received power, phase shift (via IQ data)
4. Turn off 122 GHz, transmit 60 GHz through same boundary
5. Measure same observables at 60 GHz
6. Standard plasma dispersion predicts the RATIO of these measurements precisely:
   - Phase shift ratio: (omega_p^2 / omega_60^2) / (omega_p^2 / omega_122^2) = (122/60)^2 = 4.13
   - Any deviation from this ratio is anomalous
7. Repeat at multiple discharge currents (especially across any threshold found in Phase 1)
8. Repeat with and without magnets

**What you're looking for:**
- At 60 GHz: behavior consistent with standard plasma dispersion at all currents
- At 122 GHz: ANYTHING anomalous that doesn't appear at 60 GHz
  - Unexpected absorption peak
  - Phase shift exceeding the predicted ratio
  - Threshold behavior (normal below some current, anomalous above)
- The key discriminant: the 122/60 GHz RATIO. This is precisely predicted by standard physics. Any deviation is signal.

**If using SiRad Simple (FMCW mode):**
- The chip sweeps across 122-123 GHz in FMCW radar mode
- This gives you a 1 GHz bandwidth centered near the predicted resonance
- Look for: spectral features — peaks or dips in transmission as a function of frequency within the 122-123 GHz band
- A narrow absorption or phase feature at a specific frequency within this band would be remarkable

### Phase 3: Resonance Characterization ($0 added)

*Tests: frequency profile of any anomaly found in Phase 2. Requires SiRad or VK3CV with frequency agility.*

**Procedure:**
1. If Phase 2 found anomalous behavior at 122 GHz:
2. Sweep the VCO across its full range (the TRX_120_001 has digital band switching)
3. Map the anomalous observable vs frequency in fine steps
4. Determine: center frequency, width, shape (Lorentzian? Gaussian?)
5. The width constrains the Q factor of whatever resonance you've found
6. The center frequency constrains the physical parameter (krc*pi if KK, or something else if not KK)

### Phase 4: Self-Organization ($0-100 added)

*Tests: SOC prediction. Does the plasma drift toward the threshold?*

**Procedure:**
1. Set discharge current just BELOW threshold (from Phase 1)
2. Use a large current-limiting resistor so the plasma can self-regulate
3. Monitor discharge current and afterglow over time (minutes to hours)
4. Standard physics: plasma sits at fixed operating point determined by external circuit
5. SOC prediction: plasma slowly drifts toward threshold, with intermittent excursions above it (avalanche-like behavior)
6. Record time series of afterglow duration. Power spectrum analysis: look for 1/f noise signature (hallmark of SOC)

---

## Budget Summary

| Phase | Budget | What It Tests |
|-------|--------|---------------|
| **Phase 1** | $350-440 | Threshold existence |
| **Phase 2 (cheap)** | +$350 (VK3CV path) | Frequency specificity |
| **Phase 2 (turnkey)** | +$1540 (SiRad path) | Frequency specificity + FMCW sweep |
| **Phase 3** | $0 | Resonance characterization |
| **Phase 4** | $0-100 | Self-organization |
| **TOTAL (cheap)** | **$700-800** | All four tests |
| **TOTAL (turnkey)** | **$1700-1900** | All four tests + professional software |

## Decision Tree

```
Phase 1: Afterglow threshold test
  |
  No threshold found → STOP (or: vary conditions more widely)
  |
  Threshold found → Is it magnetic-field-dependent?
    |
    No → Probably standard plasma physics (contact potential, etc.)
    |
    Yes → Phase 2: Two-frequency probe
      |
      No difference between 122 GHz and 60 GHz → Standard plasma physics
      |
      Anomaly at 122 GHz absent at 60 GHz → Phase 3: Characterize the resonance
        |
        Phase 3 gives center frequency + width → Constrains physical model
        |
        Phase 4: Self-organization test → SOC signature?
```

## Safety Notes

- HV DC supply is lethal. Current-limiting is essential. Never work on energized circuits alone.
- Vacuum implosion risk with glass tubes. Safety glasses always. Consider acrylic shield.
- Argon is an asphyxiant. Ventilate work area. Small quantities are safe but don't fill a closed room.
- RF at 122 GHz: power is milliwatts, beam is narrow. Eye hazard at close range (corneal absorption). Don't look into the horn.
- Magnets: N52 neodymium can pinch fingers severely. Handle with care, keep away from electronics.

## Hardware Sources

| Component | Source | Notes |
|-----------|--------|-------|
| VK3CV 122 GHz board | Groups.io: The122GProject | Check availability; ~500 shipped to date |
| SiRad Simple 120 GHz | AliExpress (~$1420) or indie Semiconductor | Turnkey with software |
| SiRad Easy r4 StarterKit | DigiKey | More capable, modular |
| Infineon 60 GHz eval | DigiKey ($139) | DEMO-BGT60TR13C |
| Cake icing nozzle horns | Any kitchen supply store | PME 1.5 stainless steel, ~21 dBi at 122 GHz |
| Borosilicate glass tube | eBay, Amazon, lab supply | Custom sealed tubes from glassblower if needed |
| Vacuum pump | eBay (used refrigeration pump) | Or borrow from maker space |
| Argon | Welding supply store | Small cylinder |
| N52 magnets | K&J Magnetics, Amazon | Various ring and block shapes |
| HV supply | eBay, Amazon, or build from NST + variac | Current-limit to ~50 mA max |

## What Each Outcome Means

### Phase 1 negative (no threshold)
Plasma boundaries don't bifurcate under these conditions. Either the prediction is wrong, or the conditions don't access the right regime (field too low, wrong geometry, wrong gas). Try more configurations before concluding.

### Phase 1 positive + Phase 2 negative (threshold exists but not frequency-specific)
The threshold is standard plasma physics (double-layer formation transition, contact potential bifurcation). Not evidence for KK coupling. Still publishable as a study of DC discharge bifurcations.

### Phase 1 positive + Phase 2 positive (frequency-specific anomaly at 122 GHz)
Something at 122 GHz interacts with the plasma boundary differently than 60 GHz, in a way standard plasma dispersion doesn't predict. This requires careful systematic investigation. Rule out: parametric instabilities, harmonic effects, instrumental artifacts, coupling geometry differences. If it survives: you've found a sub-meV resonance in a plasma boundary.

### Phases 1-3 positive + frequency measured
The resonance center frequency constrains the physical model. If it's at 121 +/- 1 GHz: consistent with krc*pi = 72. The width constrains the Q factor. The ratio of 122 GHz vs 60 GHz anomaly constrains the coupling channel (gravitational vs CS vs something else).

### Phases 1-4 all positive
Threshold exists, frequency-specific at ~121 GHz, characterized resonance, and the plasma self-organizes toward it. This is the full prediction set. File a patent application before publishing anything.

---

## Tier 0 Summary: Key Literature Findings

### Near-coincidences worth noting:
1. **TCV X3 operates at 118 GHz** → unique ELM-free H-mode → 3 GHz from prediction
2. **O2 absorption at 118.75 GHz** → 1.86% from prediction → atmosphere partially screens this region
3. **122 GHz ISM amateur band** → 1 GHz from prediction → hardware exists cheaply
4. **Kapitsa resonance for 0.68 mm ball** → exactly 121 GHz → sub-mm kernel inside larger structure?
5. **ECRIS kinetic instability** → IS a sharp plasma bifurcation → exists at Bmin/BECR ~ 0.7-0.85

### What nobody has done:
1. Measured L-H threshold vs ECRH frequency (field treats it as irrelevant)
2. Operated ECRIS above 75 GHz (45 GHz just got first plasma May 2024)
3. Tried ball lightning creation above 2.45 GHz (all use microwave oven magnetrons)
4. Measured microwave emission from ball lightning (only optical spectra exist)
5. Measured lightning RF above 10 GHz (technological gap)
6. Noted the O2 118.75 GHz / KK 121 GHz near-coincidence

---

*This experiment does not require believing in extra dimensions. It requires a plasma, two microwave transceivers, and the hypothesis that 122 GHz is special. The physics either shows up or it doesn't.*
