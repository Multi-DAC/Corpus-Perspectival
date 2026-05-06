# Track G: Topological Soliton Frequency Comb as Detection Modality

*Clawd, March 26, 2026. Deep dive per Clayton's request.*
*Source: Ledezma, Sekine et al., "Topological soliton frequency comb in nanophotonic lithium niobate," Nature (March 25, 2026). arXiv:2511.01856.*

---

## 1. The Technology

A chip-scale degenerate optical parametric oscillator (DOPO) on lithium niobate (LiNbO₃)
generates topological solitons — phase boundaries between two π-out-of-phase continuous wave
states — producing 60 fs dark pulses in the mid-IR (~2 μm).

**Key specifications:**

| Parameter | Value |
|-----------|-------|
| Pulse width | ~60 fs |
| Operating wavelength | ~2 μm (mid-IR) |
| Repetition rate | 19.2 THz |
| Spectral span | >100 nm |
| Cavity round trip | ~52 fs |
| Soliton type | Topological (phase defect between ±1 states) |
| Nonlinearity | Quadratic (χ⁽²⁾, LiNbO₃ d₃₃) |
| Finesse | Low (no high-Q requirement) |
| Pump | Electrically pumped laser diode, fiber-coupled |
| Theory | Parametrically forced Ginzburg-Landau |
| Chip scale | mm-scale (fabricated at Caltech KNI) |

**What makes it "topological":** The soliton is a boundary between the +1 and −1 phase states
of the parametric oscillation. This boundary carries topological charge — it cannot be removed
by continuous deformation. It persists under perturbations. This stability is the key property
for our application.

---

## 2. Why This Matters for Meridian

The existing Track G analysis (track_g_signal_analysis.md) identified five detection modalities.
For single 32 ps events, the top two are:

1. Mössbauer + SNSPD: 10⁹ linewidths signal, 30 ps resolution — **requires synchrotron**
2. Ultrafast optical: 0.4% line shift, 10-100 fs resolution — **bore access challenging**

The soliton comb is not merely another instance of optical spectroscopy. It introduces a
qualitatively new detection concept: **the LiNbO₃ chip is simultaneously source AND sensor.**

---

## 3. Detection Concept: Parametric Self-Sensing

### 3.1 The Mechanism

Place the DOPO chip inside the NMR bore. The chip generates solitons using the quadratic
nonlinearity (d₃₃) of LiNbO₃. During a 32 ps bubble, the gauge coupling shift δα/α ~ 10⁻³
changes ALL electromagnetic properties of matter inside the bubble, including d₃₃ of the chip.

The DOPO output depends critically on the parametric gain:

    G ∝ d₃₃² × L² × I_pump

A gauge coupling shift δα/α ~ 10⁻³ produces δd₃₃/d₃₃ ~ O(10⁻³), giving:

    δG/G ~ 2 × δd₃₃/d₃₃ ~ 2 × 10⁻³

### 3.2 Near-Threshold Amplification

This is the critical feature. Near the oscillation threshold, the DOPO output sensitivity to
gain changes is amplified by the inverse of the above-threshold fraction:

    δP_out/P_out ~ (δG/G) × 1/ε

where ε = (G/G_th) - 1 is the fractional distance above threshold.

| ε (above threshold) | Signal (δP/P) | Amplification |
|---------------------|----------------|---------------|
| 1% | 20% | 100× |
| 5% | 4% | 20× |
| 10% | 2% | 10× |
| 50% | 0.4% | 2× |

**Even at 50% above threshold (robust operation), the parametric amplification doubles the
raw signal.** At 1% above threshold, a 10⁻³ gauge coupling shift produces a 20% power change.

### 3.3 Time Resolution

- Soliton adjusts on cavity round-trip timescale: ~52 fs
- Low finesse → response time: ~10 × 52 fs = 520 fs (for F ~ 10)
- Bubble duration: 32 ps = 32,000 fs
- **Response is 60× faster than the event.** The soliton adiabatically tracks the perturbation.

During the 32 ps bubble: ~615 cavity round trips occur. Each round trip, the gain is modified.
The output shows a sustained power change lasting 32 ps, then recovery.

### 3.4 Single-Event Sensitivity

At 1 mW average output power and 2 μm wavelength (photon energy ~ 10⁻¹⁹ J):

    Photons during 32 ps window: N = 10⁻³ × 32×10⁻¹² / 10⁻¹⁹ = 3.2 × 10⁸

For 10% above threshold (δP/P = 2%):

    Signal photons: ΔN = 0.02 × 3.2×10⁸ = 6.4 × 10⁶
    Shot noise: √N = 1.8 × 10⁴
    SNR = 6.4×10⁶ / 1.8×10⁴ ≈ 360

**Single-event SNR ≈ 360.** Even with 100× realistic losses: SNR ≈ 36. Detectable.

For 50% above threshold (conservative):

    ΔN = 0.004 × 3.2×10⁸ = 1.3 × 10⁶
    SNR = 1.3×10⁶ / 1.8×10⁴ ≈ 72

Still excellent. **Single-event detection is feasible across a wide range of operating points.**

---

## 4. Differential Measurement Architecture

### 4.1 Chip Pair Configuration

    [Pump laser] → fiber splitter → [DOPO chip INSIDE bore] → [fast photodiode A]
                                   → [DOPO chip OUTSIDE bore] → [fast photodiode B]

    Signal = A - B (common-mode rejected)

Both chips are driven by the same pump laser (via fiber splitter). The reference chip (outside)
experiences no gauge coupling shift. Any laser fluctuations, temperature drifts, or mechanical
vibrations affect both identically → cancelled in the difference.

The only signal that survives the subtraction:
- Gauge coupling shift inside the bubble (the target signal)
- E-field electro-optic effect on chip A (systematic — see Section 5)

### 4.2 Detection Electronics

The signal is a 32 ps transient in the difference channel (A - B). Detection requires:

| Method | Bandwidth | Resolution | Feasibility |
|--------|-----------|------------|-------------|
| Fast InGaAs photodiode | >40 GHz | ~25 ps | Commercial, ~$5K |
| Streak camera | THz | ~1 ps | Expensive (~$100K) |
| Electro-optic sampling | THz | ~100 fs | Requires probe laser |
| Cross-correlation with reference comb | THz | ~60 fs | Natural with chip pair |

**The fast photodiode is sufficient.** 40 GHz bandwidth gives ~25 ps resolution, adequate
for the 32 ps event. Cost: ~$5K for a commercial InGaAs detector.

---

## 5. Systematic Effects

### 5.1 E-Field Electro-Optic Effect

LiNbO₃ is electro-optic (r₃₃ ~ 30 pm/V). The experimental E-field directly modulates the chip.

    At E = 10 kV/cm:  δn = n³ × r₃₃ × E / 2 ~ 2.2³ × 30×10⁻¹² × 10⁶ / 2 ≈ 1.6 × 10⁻⁴
    δn/n ≈ 7 × 10⁻⁵

This is 14× SMALLER than the gauge coupling signal (10⁻³). Separable.

**Control:** The 2×2 factorial design separates this automatically:
- E only (no B): see only electro-optic effect → calibrate it
- E + B: see electro-optic + any anomalous shift
- The gauge coupling shift requires BOTH E and B (the experimental condition for tunneling)

### 5.2 Magnetic Field (Faraday Effect)

At 15T in 1 mm LiNbO₃ at 2 μm:

    Faraday rotation ~ V × B × L ~ 15 × 15 × 10⁻³ ≈ 0.23 rad

This is significant but DC (constant B). It rotates polarization but doesn't produce a 32 ps
transient. Design consideration: orient chip so extraordinary axis (used by DOPO) is along B,
minimizing Faraday coupling. Or compensate with a Faraday rotator.

### 5.3 Thermal Effects

LiNbO₃ thermo-optic coefficient: dn/dT ~ 4 × 10⁻⁵ /K. Thermal changes in the bore are slow
(ms timescale) compared to the 32 ps signal. No crosstalk.

### 5.4 Vibration

Topological solitons are ROBUST against perturbations — that's the defining property.
Mechanical vibrations (kHz-MHz) are far below the soliton timescale (THz). No effect on the
32 ps signal.

---

## 6. Operating in a Cryogenic NMR Bore

### 6.1 Temperature

LiNbO₃ works well at cryogenic temperatures:
- Nonlinearity INCREASES at low temperature (reduced thermal phonons)
- Absorption DECREASES
- Electro-optic coefficient is well-characterized vs temperature
- No phase transition above 4K

### 6.2 Space

Chip is mm-scale. NMR bore is 5 cm diameter. Fiber input/output. No geometric conflict.

### 6.3 Power Dissipation

Chip-scale DOPO: mW pump power. Negligible thermal load in cryo environment. No helium
boil-off concern.

---

## 7. Comparison with Existing Modalities

### 7.1 For Single 32 ps Events

| Feature | Mössbauer + SNSPD | Ultrafast optical | **Soliton comb** |
|---------|-------------------|-------------------|------------------|
| Signal | 10⁹ linewidths | 0.4% | **2-20% (amplified)** |
| Time resolution | 30 ps | 10-100 fs | **520 fs** |
| Single-event SNR | High | Moderate | **36-360** |
| Synchrotron? | YES | No | **No** |
| Fits in bore? | Yes (absorber) | Challenging | **Yes (chip)** |
| Self-referencing? | No | No | **YES** |
| Topological stability? | N/A | No | **YES** |
| Common-mode rejection? | No | Possible | **YES (chip pair)** |
| Cost | $50K-100K + beamtime | Medium | **$5K-20K** |

### 7.2 For Sustained Regeneration

At 30 GHz regeneration, the bubble duty cycle approaches 100% (32 ps × 30 GHz ≈ 1). The
soliton comb sees a continuous δd₃₃/d₃₃ shift. Detection is trivial — standard lock-in
with E-field modulation.

---

## 8. Revised Detection Strategy

| Phase | Modality | Target | Cost | Timeline |
|-------|----------|--------|------|----------|
| 1 | NMR screening | Sustained regeneration (null test) | $10K-50K | Weeks |
| **1b** | **Soliton comb** | **Single-event detection, in-lab** | **$5K-20K** | **Weeks** |
| 2 | Mössbauer + SNSPD | Definitive single-event (if needed) | $50K-100K + beamtime | 6-12 months |
| 3 | Operator testing | Sustained regeneration with operator | Incremental | After 1/1b |

**Phase 1b can run simultaneously with Phase 1** — the chip can be added to the NMR bore
alongside the NMR probe. The soliton comb provides time-resolved single-event detection
while NMR provides steady-state frequency monitoring. Two independent channels in one apparatus.

**The soliton comb potentially eliminates the need for Phase 2 (synchrotron Mössbauer).**
If Phase 1b detects single events with sufficient SNR, the Mössbauer confirmation becomes
a bonus rather than a necessity.

---

## 9. What Needs to Happen

### 9.1 Immediate (Can Do Now)
1. Detailed δd₃₃/δα calculation (trace gauge coupling shift to nonlinear coefficient)
2. DOPO threshold model with gauge coupling perturbation
3. Optimal operating point analysis (ε vs stability vs sensitivity tradeoff)
4. Integration design for chip + NMR bore + E-field electrodes

### 9.2 Requires Collaboration
1. Contact Marandi group at Caltech (chip fabrication, characterization)
2. Source commercial LiNbO₃ DOPO chips (if available)
3. Fast InGaAs photodiode procurement (~$5K)
4. Fiber-coupled pump laser selection

### 9.3 Requires Facility
1. Test chip response in high-B environment (Faraday characterization)
2. Calibrate electro-optic systematic at experimental E-field
3. Measure near-threshold sensitivity curve

---

## 10. The Assessment

The Caltech soliton comb is not just "another optical source." It introduces three capabilities
that change the Track G detection landscape:

1. **Parametric amplification** converts a 10⁻³ gauge shift into a 2-20% power change
2. **Self-sensing** eliminates the need for a separate probe material
3. **Topological stability** provides robustness in the harsh bore environment

The combination of chip-scale, in-lab, low-cost, single-event-capable, and self-referencing
makes this the most promising detection modality for Phase 1. If it works, the entire
experiment can be done with an NMR magnet + E-field electrodes + a DOPO chip + a fast
photodiode. Total cost: **$15K-70K with no synchrotron.**

The main uncertainty: whether the near-threshold amplification behaves as modeled when the
gain perturbation is a 32 ps transient rather than a DC change. This requires either
simulation (Ginzburg-Landau dynamics with pulsed gain modulation) or direct measurement
(perturbation experiments on an existing DOPO chip). Both are feasible.

---

## 11. Open Questions

1. **Does apparatus (E-field direction) select target T² plane?** If so, the chip orientation
   may matter for which of the 3 equivalent targets is addressed.
2. **Can the soliton comb detect the STEP FUNCTION?** The within-subject protocol predicts
   all-or-nothing coupling (Section 10.8 of I.9 analysis). The soliton comb would see either
   no signal or full signal — no gradual onset.
3. **Crosstalk between NMR and soliton comb?** The NMR RF pulses (MHz) are far below the
   DOPO bandwidth (THz). No spectral overlap. But the RF field could modulate the chip through
   the electro-optic effect — need to quantify.
4. **Multi-soliton states as additional observable?** The paper demonstrated "soliton crystal
   states" with 16 evenly spaced dark pulses. Gauge coupling shifts could change the soliton
   count or spacing — a qualitatively different observable beyond power modulation.

---

*This analysis should be integrated into the Phase 24 engineering package and shared with
potential collaborators, particularly the Marandi group at Caltech.*

🦞🧍💜🔥♾️
