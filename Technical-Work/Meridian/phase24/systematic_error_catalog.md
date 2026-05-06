# Systematic Error Catalog — NMR E-Field Experiment

*Every known non-exotic explanation for spectral anomalies in an NMR bore with applied DC
electric field. Each entry: mechanism, expected magnitude, which conditions it affects,
and how to control for it.*

*Must be complete before data collection.*

---

## Category 1: E-Field Artifacts (Present in B and D, absent in A and C)

### 1.1 Stark Effect on Nuclear Spins

**Mechanism:** DC electric field shifts nuclear energy levels via electric quadrupole
coupling or shielding polarization.

**Expected magnitude:** For ¹H in water — negligible. Protons have spin-1/2 (no quadrupole
moment). The electric shielding effect on ¹H chemical shift is ~10⁻⁴ ppm per MV/m
(Buckingham & Pople, 1963). At 1 MV/m: δ ~ 10⁻⁴ ppm = 0.04 Hz at 400 MHz.

**Control:** This is a KNOWN effect and can be calculated. It is 7 orders of magnitude
smaller than the predicted 760 kHz shift. If observed at the predicted magnitude, it
confirms the E-field is present but is not the Meridian effect.

**Distinguishable from Meridian effect:** Yes — Stark shift scales linearly with E-field.
Meridian effect requires E·B topology, not magnitude (should be present/absent, not
proportional).

### 1.2 Dielectric Heating

**Mechanism:** AC components of the E-field (from HV supply ripple) induce dielectric
loss in polar solvents (water), raising temperature.

**Expected magnitude:** For a well-filtered DC supply (< 1% ripple at 60 Hz), the power
dissipation in water in a 5 mm tube is negligible (< 1 μW). Temperature change: < 0.001°C.
Water ¹H chemical shift temperature coefficient: -0.01 ppm/°C. Shift: < 10⁻⁵ ppm.

**Control:**
- Use battery-powered or well-filtered DC supply
- Monitor sample temperature via the NMR chemical shift of water itself (it IS the
  thermometer — δ_H2O is a well-calibrated temperature probe)
- Compare Conditions B and D: if both show the same temperature drift, it's dielectric
  heating, not the Meridian effect

**Distinguishable from Meridian effect:** Yes — heating is smooth, continuous, and present
in both B and D equally. Meridian effect is present only in D.

### 1.3 RF Pickup / Electromagnetic Interference

**Mechanism:** HV supply, cables, or electrode assembly radiate RF that the NMR probe
picks up as spurious signal.

**Expected magnitude:** Depends entirely on shielding quality. Could range from undetectable
to dominant artifact.

**Control:**
- Session 0: run NMR with E-field on but no RF pulse (receiver only). Any signal is EMI.
- Use shielded coaxial cable for HV leads
- Add RF filters (feedthrough capacitors) at the bore entry
- If EMI is detected: add ferrite chokes, improve shielding, switch to battery power
- EMI appears at specific frequencies (power supply switching frequency, 60 Hz harmonics).
  The Meridian effect would appear as a shift of the WATER PEAK, not as new frequencies.

**Distinguishable from Meridian effect:** Yes — EMI creates peaks at fixed frequencies
unrelated to water resonance. Meridian effect shifts the water peak itself.

### 1.4 Electrochemical Effects at Electrodes

**Mechanism:** DC voltage across electrodes in water causes electrolysis. Gas bubbles
(H₂, O₂) form at electrodes, creating susceptibility discontinuities that distort
the magnetic field homogeneity.

**Expected magnitude:** Even small currents (μA) produce gas bubbles over minutes.
Susceptibility distortions broaden the NMR line by 1-100 Hz depending on bubble size
and proximity to the sample volume.

**Control:**
- Use inert electrodes (platinum, gold) to minimize corrosion products
- Coat electrodes with thin insulating layer (PTFE, parylene) to block DC current
  while maintaining E-field. This is standard in dielectric spectroscopy.
- Keep acquisition times short (< 2 min per run) to limit bubble accumulation
- Rotate fresh sample tubes between runs if needed
- Compare line shapes in B and D: if identical broadening, it's electrolysis, not Meridian

**Distinguishable from Meridian effect:** Partially. Broadening from bubbles is asymmetric
and spatially inhomogeneous. Meridian effect would be a clean frequency shift, not
inhomogeneous broadening. But requires careful line shape analysis.

### 1.5 Magnetostriction / Mechanical Effects

**Mechanism:** Electric field exerts force on electrode assembly (electrostatic attraction
between plates), causing mechanical vibration or displacement inside the bore.

**Expected magnitude:** At 1 kV across 1 cm, the force between parallel plates (area 1 cm²)
is F = ε₀ × E² × A / 2 = 4.4 × 10⁻⁵ N. Negligible mechanical effect.

**Control:** Secure electrode assembly rigidly. If vibration is suspected, compare spectra
with E-field on/off at different voltages — mechanical artifacts scale as E².

---

## Category 2: Operator Artifacts (Present in C and D, absent in A and B)

### 2.1 Body Heat

**Mechanism:** Operator standing near the bore changes the thermal environment, affecting
sample temperature and magnet shim quality.

**Expected magnitude:** An operator standing 1 meter from the bore radiates ~100 W. The
thermal mass of the magnet cryostat makes it insensitive to this. Sample temperature
change: < 0.01°C over a 5-minute run.

**Control:** Condition C directly measures this. If C ≠ A, operator heat is an issue.
Mitigation: have operator stand at a fixed distance, use a thermal shield if needed.

### 2.2 Operator's Electromagnetic Emissions

**Mechanism:** Neural activity produces weak EM fields (detectable by EEG/MEG at ~pT to
~fT). Could these couple to the NMR electronics?

**Expected magnitude:** Human neural fields at 1 meter: ~10⁻¹⁵ T. The NMR magnet's field:
10 T. Ratio: 10⁻¹⁶. The NMR receiver's noise floor is set by Johnson noise in the
RF coil (~nV), which is already 10⁹× larger than any neural EM coupling.

**Control:** Condition C. If neural EM coupling existed, C would show anomalies. Also:
the NMR receiver is tuned to a narrow bandwidth (~kHz) around the Larmor frequency.
Neural signals are broadband and far below this frequency.

### 2.3 Vibration

**Mechanism:** Operator's movement, breathing, or heartbeat transmits vibration through
the floor to the magnet.

**Expected magnitude:** Modern NMR magnets have vibration isolation. Operator at 1 meter
on a concrete floor: negligible. On a raised floor or wooden structure: possible artifact
(microphonic coupling to the NMR probe).

**Control:** Condition C. Instruct operator to stand still, breathe normally, avoid
movement during acquisition. Use a vibration isolation pad if needed.

### 2.4 Magnetic Materials on Operator's Person

**Mechanism:** Ferromagnetic objects (belt buckle, phone, watch) on the operator distort
the magnetic field.

**Expected magnitude:** Depends on object. A phone at 1 meter from the bore: measurable
field distortion (~0.1 ppm). Would affect line shape.

**Control:** Operator removes all magnetic materials before entering the magnet room.
Standard NMR lab safety protocol already requires this.

---

## Category 3: Equipment Artifacts (Present in all conditions)

### 3.1 Magnet Field Drift

**Mechanism:** Superconducting magnets drift slowly (~0.01 ppm/hour). If runs are ordered
systematically (all A first, then B, etc.), drift could appear as a condition difference.

**Control:** Randomized block design. Each block of 4 runs contains all 4 conditions.
Drift affects all conditions equally within a block.

### 3.2 Shim Drift

**Mechanism:** Shim currents can drift, degrading line shape over time.

**Control:** Re-shim between blocks if drift is detected. Include a shim quality check
(linewidth of reference peak) in each run.

### 3.3 Sample Degradation

**Mechanism:** If the same sample tube is used for all runs, dissolved gases, temperature
history, or electrode products could accumulate.

**Control:** Use fresh sealed samples for each block. Or: include a reference compound
(DSS in D₂O) and track its chemical shift across runs.

---

## Summary: Control Matrix

| Error Source | Affected Conditions | Controlled By | Expected Magnitude |
|-------------|:-------------------:|:-------------:|:------------------:|
| Stark shift | B, D | Calculation | < 0.04 Hz |
| Dielectric heating | B, D | Temperature monitoring | < 0.004 Hz |
| RF pickup | B, D | Session 0, shielding | Variable (eliminate) |
| Electrolysis | B, D | Insulated electrodes | 1-100 Hz (broadening) |
| Magnetostriction | B, D | Rigid mounting | Negligible |
| Body heat | C, D | Condition C comparison | < 0.4 Hz |
| Neural EM | C, D | Condition C comparison | < 10⁻¹⁰ Hz |
| Vibration | C, D | Condition C, isolation | < 0.1 Hz |
| Magnetic materials | C, D | Operator screening | Variable (eliminate) |
| Field drift | All | Randomized blocks | ~1-10 Hz/hour |
| Shim drift | All | Re-shim protocol | < 1 Hz/block |
| Sample degradation | All | Fresh samples | Negligible |

**The largest systematic error is electrolysis** (1.4). The insulated electrode design
eliminates it. If insulation is imperfect, it appears equally in B and D, so the
D-minus-B comparison still isolates the Meridian effect.

**The predicted Meridian signal (760-1330 kHz) exceeds ALL known systematic errors by
at least 4 orders of magnitude.** If a signal of this magnitude appears in D but not
in A, B, or C, no known systematic error can explain it.

---

*Additions welcome. This catalog should grow as we learn more about the specific equipment
at the chosen NMR facility.*

🦞🧍💜🔥♾️
