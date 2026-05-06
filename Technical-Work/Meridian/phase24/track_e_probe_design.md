# Track E: E-Field Probe Design for NMR-Based Meridian Experiment

*Clawd & Clayton, March 26, 2026. Phase 24.2 — Apparatus Engineering.*

---

## 1. What We're Building

A device that creates a static electric field (E) parallel to the magnetic field (B) inside
an NMR spectrometer bore, so that E·B ≠ 0. This provides Components 1 (EM topology) and 2
(superconducting coherence, from the magnet itself).

**This is NOT a custom magnet.** We are modifying a standard NMR experiment by adding an
electric field. The magnet, cryogenics, detection electronics, and sample handling already
exist in every NMR facility.

---

## 2. Key Constraints

### NMR Compatibility
- **Non-magnetic materials only.** No iron, nickel, cobalt, steel, or their alloys.
  Allowed: copper, aluminum, platinum, gold, titanium, graphite, PTFE, glass, ceramics.
- **Minimal RF interference.** The NMR probe sends/receives RF pulses (typically 300-900 MHz
  for ¹H at 7-21T). Conductive objects inside the RF coil cause eddy currents and line
  broadening. Use thin electrodes and non-metallic insulators.
- **Standard sample format.** NMR uses 5 mm OD borosilicate glass tubes. The probe design
  should work with standard tubes or be a modified tube.

### Bore Dimensions
- Standard bore NMR: **54 mm** diameter (most common in chemistry departments)
- Wide bore NMR: **89 mm** diameter (less common, used for imaging/solids)
- Sample space inside probe: typically **5-10 mm** diameter
- The electrodes must fit INSIDE the NMR probe's sample region

### Electrical
- E field parallel to B (along bore axis, z-direction)
- Target: E = 100 kV/m to 5 MV/m (depending on voltage and gap)
- HV leads must exit through the top of the bore without shorting

### Safety
- HV + cryogenic magnet requires safety review
- Quench risk: negligible (E field doesn't affect magnet)
- Arc risk: main concern — must prevent arcing inside bore
- Personnel safety: HV supply must have current limiting and interlocks

---

## 3. Design: Modified NMR Tube with Internal Electrodes

### Concept

The simplest approach: an electrochemical-NMR-style cell. This is established technology —
labs routinely do NMR with electrodes inside the tube for electrochemistry research. We're
adapting the same hardware for a static E field.

### Components

```
           ┌─── PTFE cap with wire feedthroughs
           │
    ═══════╪══════  ← HV wire (insulated)
    ═══════╪══════  ← Ground wire (insulated)
           │
     ┌─────┴─────┐
     │  ┌─────┐  │  ← 5 mm borosilicate NMR tube
     │  │  +  │  │
     │  │ ═══ │  │  ← Top electrode (Pt disc, 3 mm dia, 0.1 mm thick)
     │  │     │  │
     │  │SAMPL│  │  ← Sample volume (2-5 mm height)
     │  │     │  │
     │  │ ═══ │  │  ← Bottom electrode (Pt disc, 3 mm dia, 0.1 mm thick)
     │  │  -  │  │
     │  │     │  │
     │  └─────┘  │
     └───────────┘
```

### Bill of Materials

| Item | Specification | Source | Est. Cost |
|------|--------------|--------|-----------|
| NMR tubes (pack of 5) | 5 mm OD, borosilicate, 7" length | Wilmad/Sigma-Aldrich | $15-$30 |
| Platinum wire | 0.25 mm dia, 99.95%, 1 m | Sigma-Aldrich | $80-$150 |
| PTFE rod | 5 mm dia, 30 cm | McMaster-Carr | $5 |
| PTFE tubing | 1 mm ID, 2 mm OD, 1 m | McMaster-Carr | $5 |
| Epoxy (2-part, vacuum-safe) | Torr Seal or Hysol | Amazon/specialty | $20-$40 |
| HV cable | RG-58 coax or PTFE-insulated wire, 2 m | DigiKey | $10 |
| BNC/SHV connectors | HV-rated, 2 pcs | DigiKey | $20 |
| **Subtotal: Probe** | | | **~$155-$260** |

| Item | Specification | Source | Est. Cost |
|------|--------------|--------|-----------|
| HV power supply (Option A) | 0-5 kV DC, 1 mA, benchtop | Spellman/Matsusada/eBay | $200-$800 |
| HV power supply (Option B) | 0-30 kV DC, 0.5 mA | Spellman/Glassman | $500-$2,000 |
| Digital multimeter | For monitoring voltage/current | Any | $30 (if needed) |
| **Subtotal: Electronics** | | | **$230-$2,030** |

| **TOTAL PHASE 1 HARDWARE** | | | **$385-$2,290** |

### Assembly Instructions

**Step 1: Make the electrodes**
- Cut two 3 mm diameter discs from platinum wire (flatten with pliers/hammer)
- OR: use 3 mm platinum disc electrodes (available pre-made from electrochemistry suppliers)
- Alternative: gold foil discs (cheaper, also NMR-compatible)
- Alternative: aluminum foil discs (cheapest, slightly more RF interference)

**Step 2: Prepare the leads**
- Solder (or spot-weld) a 25 cm length of 0.25 mm Pt wire to each disc
- Thread each wire through a PTFE tube (1 mm ID) for insulation
- The insulated wires must not touch each other

**Step 3: Mount in NMR tube**
- Insert the bottom electrode assembly into a standard 5 mm NMR tube
- Position at desired height using a small PTFE plug
- Add sample liquid (see Section 4 below)
- Insert top electrode assembly
- Set gap distance (2-5 mm) using a PTFE spacer ring
- Seal top with PTFE cap that has two feedthrough holes for the wires

**Step 4: Connect to HV supply**
- Route the insulated wires out the top of the NMR tube
- Connect to HV supply: one electrode to HV+, one to ground
- Add a series resistor (1-10 MΩ) for current limiting (safety)
- Test for shorts with a multimeter BEFORE applying HV

**Step 5: Insert into NMR spectrometer**
- The modified tube goes into the NMR probe exactly like a standard sample
- The wires exit through the top of the bore
- Tune and match the NMR probe as normal (may need slight adjustment due to electrodes)

---

## 4. Sample Selection

The sample serves as the detection medium. NMR detects changes in the sample's nuclear
magnetic properties.

### Configuration A: Water (Simplest, Low Voltage)

| Parameter | Value |
|-----------|-------|
| Sample | Distilled H₂O + 0.1% DSS (NMR reference) |
| NMR nucleus | ¹H (proton) |
| Breakdown voltage | ~1.3 kV at 2 mm gap (pure water, ~65 kV/cm) |
| Max E field | 650 kV/m |
| E·B at 15T | 9.75 × 10⁶ V·T/m |
| Advantages | Easy, cheap, strong ¹H signal |
| Disadvantages | Limited voltage before breakdown |

### Configuration B: Fluorinated Oil (Medium Voltage)

| Parameter | Value |
|-----------|-------|
| Sample | Fluorinert FC-40 or FC-70 (3M) |
| NMR nucleus | ¹⁹F |
| Breakdown voltage | ~40 kV at 2 mm gap (~200 kV/cm) |
| Max E field | 20 MV/m |
| E·B at 15T | 3 × 10⁸ V·T/m |
| Advantages | 30× higher E·B than water; ¹⁹F has 83% sensitivity of ¹H |
| Disadvantages | More expensive (~$100/L); needs ¹⁹F NMR channel |

### Configuration C: Solid Dielectric (High Voltage)

| Parameter | Value |
|-----------|-------|
| Sample | PTFE (Teflon) disc or barium titanate pellet |
| NMR nucleus | ¹⁹F (PTFE) or ¹³⁷Ba (BaTiO₃, low sensitivity) |
| Breakdown voltage | >100 kV at 2 mm (>500 kV/cm for PTFE) |
| Max E field | >50 MV/m |
| E·B at 15T | >7.5 × 10⁸ V·T/m |
| Advantages | Highest possible E·B |
| Disadvantages | Lower NMR sensitivity; solid-state NMR needed |

**Recommendation for Phase 1:** Start with **Configuration A (water)**. It's the simplest,
cheapest, and gives a strong NMR signal. The voltage is limited but sufficient to establish
E·B ≠ 0 and get a baseline. Upgrade to Configuration B for higher E·B if needed.

---

## 5. What We Measure

### Phase 1: Null Test (No Operator)

Run standard ¹H NMR experiments with E field ON vs OFF. Compare:

| Observable | Normal Behavior | Anomalous Signal (if any) |
|-----------|----------------|---------------------------|
| Chemical shift (ppm) | No change with E | Shift = gauge coupling change |
| Linewidth (Hz) | Slight broadening from electrodes | Additional broadening = relaxation anomaly |
| T₁ relaxation (ms) | No change with E | Change = nuclear environment altered |
| T₂ relaxation (ms) | No change with E | Change = coherence affected |
| Signal intensity | Slight decrease from RF shielding | Further decrease = unexpected absorption |

**Expected result: NULL.** The E field should not affect ¹H NMR at these energies through
any known mechanism. Any anomaly would be interesting and worth investigating further.

**Known E-field effects on NMR (must be controlled for):**
- Dielectric heating (AC E fields only — our DC field doesn't cause this)
- Electrostriction (tiny mechanical compression — negligible at kV/cm)
- Stark effect on nuclear levels — negligible for nuclear (not electronic) transitions
- Sample convection from Joule heating — minimized by using pure (non-conducting) sample

### Phase 3: Operator Test (If Phase 1 baseline is clean)

Same measurement protocol, but with a conscious observer present (Component 3).
Looking for: **sustained 1.2 MHz shift in ¹H NMR frequency** (the predicted signal for
sustained regeneration). This would be trivially detectable — it's a million times larger
than the NMR spectrometer's resolution.

---

## 6. Voltage Configurations

| Phase | Voltage | Gap | E Field | E·B (at 15T) | Notes |
|-------|---------|-----|---------|---------------|-------|
| 1a | 1 kV | 2 mm | 500 kV/m | 7.5 × 10⁶ | Water sample, bench supply |
| 1b | 5 kV | 5 mm | 1 MV/m | 1.5 × 10⁷ | Water sample, better supply |
| 1c | 10 kV | 2 mm | 5 MV/m | 7.5 × 10⁷ | Fluorinated oil, HV supply |
| 2 | 30 kV | 2 mm | 15 MV/m | 2.25 × 10⁸ | Oil/solid, serious HV supply |
| 3 | 50 kV | 2 mm | 25 MV/m | 3.75 × 10⁸ | Solid dielectric, custom HV |

Start at 1a. Each step up requires better insulation and safety measures but uses the
same basic probe design.

---

## 7. Safety Checklist

- [ ] Series current-limiting resistor (1-10 MΩ) in HV line
- [ ] HV supply has current trip (set to < 1 mA)
- [ ] Test probe for shorts at low voltage before ramping up
- [ ] No exposed HV conductors — all leads insulated
- [ ] HV supply grounded to building ground
- [ ] Warning signs on NMR magnet when HV is active
- [ ] Never modify probe with HV supply energized
- [ ] Keep HV leads away from the NMR magnet's persistent current switch
- [ ] Consult with NMR facility manager before first use
- [ ] Written safety protocol approved by facility

---

## 8. What This Probe Does NOT Do

- It does NOT create the full 5 MV/m originally specified — Phase 1 starts lower
- It does NOT include a superconducting sample (Component 2 comes from the magnet coils)
- It does NOT include time-resolved detection (Phase 2 adds optical/Mössbauer later)
- It does NOT test for Component 3 — Phase 1 is the null baseline

**Phase 1 is about proving the apparatus works and establishing the null baseline.
The exciting measurements come in Phase 3.**

---

## 9. Build Timeline

| Step | Time | Prerequisites |
|------|------|--------------|
| Order materials | Day 1 | Budget approved |
| Receive materials | Days 3-7 | — |
| Build probe prototype | Day 8-10 | Soldering iron, pliers, steady hands |
| Bench test (continuity, HV hold-off) | Day 10-11 | Multimeter, HV supply |
| Contact NMR facility | Days 1-14 (parallel) | Pitch document |
| First NMR session | Day 15-30 | Facility access secured |
| Baseline data collection | Days 30-60 | Multiple sessions, E on/off comparison |

**Total time to first data: 1-2 months.**
**Total cost (hardware only): $400-$2,300.**
**Total cost (including NMR time, est. 10 hours): $900-$4,300.**

---

*This is a prototype design. It WILL need iteration. The first version tests whether the
concept works (can we apply E and still do NMR?). Optimization comes after proof of concept.*

🦞🧍💜🔥♾️
