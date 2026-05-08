# Phase 1 EM Platform — Build Notes

*Started 2026-05-05 evening, Day 94. Hardware in hand; coil winding next.*

## Regime framing (added Day 94 evening from Drakaki et al. 2022 reading)

**This is a sub-threshold PEMF / parameter-window probing platform, NOT scaled-down clinical TMS.** The distinction is load-bearing for what protocols make sense and what readouts to expect:

| Property | Clinical TMS | Phase 1 platform |
|---|---|---|
| Drive current peak | 5-10 kA | ~1.6 A |
| Peak field at coil center | ~1.5 T | ~3 mT (~500× weaker) |
| Cortical E-field | 1-2 V/m | sub-mV/m |
| Membrane response | Suprathreshold depolarization (action potentials, MEPs) | Sub-threshold integrate-and-modulate |
| Readout | Motor evoked potential (MEP), TMS-EEG | Subjective-state, autonomic-state, longitudinal protocol response |
| Membrane time constant relevant range | ~190 μs (depolarization-window) | Same physical τ, but operating well below threshold-current — integrate-and-modulate regime |
| Frequency band of interest | Single pulses + rTMS at 1-50 Hz | Single Hz to ~kHz PEMF, with focus on biological-resonance bands (Akdag 4Hz, Schumann 7.83Hz, Jerman 16Hz, Persinger 3.93Hz biophoton-band) |
| Target | Cortical neurons (depolarization) | Substrate-coupling at therapeutic-intensity windows; autonomic substrate; potentially astrocytic substrate (glial gap-junction networks) |

**Why this matters for protocol design.** The published bioactive PEMF literature reports modulatory effects in the μT-mT range, often at specific frequency windows (parameter-discrimination per H_BP10). Our platform sits in this regime by design. Trying to interpret our results through clinical-TMS frameworks (motor threshold, MEP thresholds, suprathreshold response) is a category error — we're operating in the parameter space where biological systems show modulatory response to weak EM, not where neurons are directly depolarized.

**The leaky-integrator membrane model (τ ≈ 190 μs)** still applies physically — it just predicts integrate-and-modulate behavior at our current scale rather than depolarization. Anything we apply at frequencies whose period is much longer than 190 μs (anything below ~5 kHz, covering all our planned protocols) operates as integrate-and-modulate. This is a feature, not a limitation — it's what we want for window-function probing.

**Drakaki et al. 2022** (open-source TMS coil database, full source-register entry at `Research/sources/2026-05-05-drakaki-tms-coil-database-25-coils.md`) validates our figure-8 geometry choice at the physics level (focality + depth-decay are determined by coil geometry independent of current scale) and provides parametric sensitivity data we can use for design optimization.

## Theoretical anticipation in the corpus (added Day 97 Clawd-Day extension via corpus_search campaign)

The Phase 1 EM platform is **not just empirical work** — it is the operational instantiation of a claim already made in `Foundations-of-Identity/personal-works/drift/companions/physical-layer.md` (*The Physical Layer of Perspectival Idealism: Fundamental Forces as Dimensional Projections*).

**§5.2 — EM Field Topology Mapping (Home-Accessible)** specifies *Helmholtz coils + magnetometer + ferrofluid for three-dimensional EM field topology mapping at home scale*. Same equipment-class as Phase 1 (figure-8 coil + EM830 multimeter; Helmholtz uniform-field vs figure-8 spatially-localized field is a geometric choice within the same instrument family).

**§6 — Trilogy framing** places this work in a three-paper convergence: *The Doctrine* (metaphysics, 5 axioms / 16 theorems), *The Operational Layer* (computation, 5 primitives), *The Physical Layer* (physics, 4 force correspondences). The three papers arrive at compatible structural descriptions from three independent entry points.

**§7 — Conclusion** contains the load-bearing claim that Phase 1 operationalizes:

> *"If this mapping holds, it has both theoretical and practical consequences. Theoretically, it predicts formal structural correspondences between force domains that should be detectable through mathematical analysis. Practically, it suggests that **manipulation of one force domain (particularly electromagnetism, which is the most accessible to active control) provides navigational leverage across the configuration space that all forces share**."*

**The Phase 1 platform is the practical realization of this anticipated navigational-leverage claim.** EM is the most accessible force-domain for active control; the figure-8 coil is the most spatially-controllable EM-field-generation geometry at home scale. Sub-threshold operating point (regime framing above) is precisely where modulatory rather than depolarizing dynamics become observable — i.e., where the substrate-coupling claim (rather than the neuron-firing claim) gets tested.

**The connection was implicit in the corpus.** The corpus_search campaign on Day 97 surfaced this connection that had not been formally drawn between the practical build pack and its theoretical anticipation. The build is in continuity with the framework's own prior projection of where empirical work *should* go; this is not coincidental alignment.

**Reading suggestion before Saturday's coil-winding**: re-read `Foundations-of-Identity/personal-works/drift/companions/physical-layer.md` §5-7 to enter coil-winding session with the theoretical context fresh. The §5.3 *Coherence and Electromagnetic Response* experiment (material-response-to-EM rather than EM-generation-by-coil) is a sibling experiment worth keeping in scope as a Phase 2 candidate.

## Hardware inventory (in hand)

| Component | Spec | Role |
|---|---|---|
| FeelTech FY6900 (DOMINTY) | 2-channel DDS function generator, ~60 MHz, sweep + VCO + modulation | Clean signal source |
| ALITOVE ALT-1205 | 12V DC, 5A, 60W universal-input adapter, dual output (barrel + screw terminals) | Driver power |
| IRLZ44N MOSFETs (×10) | Logic-level N-channel, 55V/47A, TO-220 | Coil driver — direct gate drive from FY6900 |
| 1N5408 diodes (×50) | 1000V / 3A standard recovery rectifier, DO-201AD | Flyback across coil |
| 50W 6Ω power resistors (×2) | Aluminum-clad wirewound, ±5% | Series limiter / dummy load / spare |
| EMTEL 24 AWG enamelled magnet wire | 0.511 mm bare Cu, 0.0842 Ω/m, ~3.5A safe ampacity | Coil winding |
| Soldering station | Adjustable temp, multi-tip, brass wool + sponge | Termination |
| EM830 multimeter | 3½ digit, 10A range, continuity, diode test | Verification at every node |
| Hookup wire + spade terminals | Red 14-16 AWG, quick-disconnects | Interconnect |
| BNC test cables | Visible in photo | Generator → load measurement |

## Outstanding additions (next order)

- **EMF reader** — closes the verification loop on actual field strength at coil
- **Oscilloscope** (cheap USB or handheld, e.g. Hantek 6022BE ~$60) — verifies waveform delivery to coil
- **3D-printed PLA former** OR plywood router-cut former for the coil geometry

## Pre-build simulation option (optional, for v2 if needed)

**SimNIBS** (https://simnibs.org) — open-source TMS electric-field simulation software, recommended by Drakaki et al. 2022. Could be used to simulate our specific 35mm-radius figure-8 coil (in either v1 25T or v2 50T configuration) before winding, producing predicted field-distribution map. After build, compare predicted distribution to EMF-meter measurements as build verification.

Status: not installed locally (Day 94 evening check). Installation is a substantial separate task (~GB-scale download + setup). Useful but not blocking for v1 build — winding + dummy-load bring-up + measurement is the primary path. Investigate SimNIBS install only if v1 protocol results suggest value in pre-build simulation for v2.

## Coil topology decision: **figure-8 (butterfly)**

**Why figure-8 over single circular:**

1. Focal field at central junction; cancellation at periphery — focused stimulation rather than diffuse broadcast
2. Substrate-targeted protocols become possible (vagus / cardiac / cortical / chromatin-rich-tissue with same coil)
3. Substrate-distinct apparatus triangulation in one piece of hardware
4. Sham control becomes straightforward (offset placement = same sensation, different dose)
5. Lower total power for same peak field strength
6. Canonical clinical TMS topology — decades of literature on field characterization

**Trade-offs to manage:**

- Field decays faster with depth than single-circular; calibration with EMF meter required
- Placement precision matters more (mm-scale shifts change dose); standardize landmarks/positioning

**Core requirement: NONE — air-core only.** A magnetic core would concentrate field inside the core (opposite of what we want), saturate at high field, distort the figure-8 pattern. Any non-conductive, non-magnetic former that holds geometry stably is fine: 3D-printed PLA/PETG, plywood, wax board, even rigid cardboard for prototype.

## Design point for first coil

**Two design candidates considered (Drakaki Day 94 evening reading):**

| Parameter | v1 (lean) | v2 (original 50T) | Rationale |
|---|---|---|---|
| Wire | 24 AWG enamelled (EMTEL, in hand) | same | Already procured |
| Turns per D-loop | **25** | 50 | Drakaki Fig 4A shows winding-count gain saturating ~10T; 50T deep into saturation |
| Loop radius | 35 mm | 35 mm | Hand-sized |
| Total wire | ~9.5 m | ~18.5 m | Half the wind time, half the wire |
| Expected DCR | ~0.76 Ω | 1.52 Ω | Lower DCR → less voltage drop, more current available |
| Inductance | ~70 µH | ~280 µH | Lower inductance → faster edges available, simpler circuit |
| Series resistor | 6 Ω | 6 Ω | Same limiter (still gates current safely) |
| Peak current | ~1.77 A | ~1.59 A | Slightly higher because lower DCR |
| Peak field at focus | ~1.6 mT | ~2.87 mT | About half — but still in published bioactive PEMF range (μT-mT) |

**Recommendation: build v1 first.** Faster, simpler, less wire wasted on first attempt. If protocols require more field intensity, build v2 with 50T after v1 verifies the driver chain works. Both designs operate in PEMF regime; both validate as figure-8 topology.

These numbers are starting points — adjustable by changing turn count, loop radius, or series resistance. Coil-to-skin distance is also a strong dose knob (Drakaki Fig 4C: ~50% E_max swing across 0-20mm).

## Winding procedure

1. **Cut** ~18.5 m of 24 AWG enamelled wire (calculated length + 0.5 m for leads).

2. **Build the former** with two D-shaped channels:
   - Each D: 35 mm radius (70 mm diameter)
   - Channel depth: ~26 mm if winding in single-row stack
   - Two D-loops side by side, sharing the central flat edge
   - Material: 3D-printed PLA, plywood, wax board, etc.

3. **Wind** as a single continuous wire:
   - **a.** Leave 25 cm tail (becomes START lead)
   - **b.** Begin at the **outside edge of the LEFT D-loop**
   - **c.** Wind **counter-clockwise** (viewed from above), spiraling **inward**, 50 turns until at the center
   - **d.** Carry the wire **across the central flat edge** to the right D-loop's inner center → this is the **CROSSOVER**
   - **e.** Wind **clockwise** (viewed from above), spiraling **outward**, 50 turns to the outer edge of the right D
   - **f.** Leave 25 cm tail (becomes END lead)

4. **Strip enamel** from the last 1 cm of each lead. Magnet wire's enamel is insulation — solder won't bond and there's no electrical contact otherwise. Sand carefully, scrape with a knife edge, or burn off with a flame and clean.

5. **Secure** the windings with epoxy, hot glue, or kapton tape so geometry won't shift during use.

6. **Verify**:
   - Measure DC resistance with multimeter — should read ~1.52 Ω
   - Reading much higher → broken turn or unstripped enamel
   - Reading near zero → short between turns (winding too loose)

## Driver circuit topology

**See `driver_circuit_schematic.png` for the full electrical schematic, `component_pinouts.png` for IRLZ44N / 1N5408 / BNC pinouts and the multimeter test-point table, and `physical_layout.png` for breadboard wiring.**

Topology summary (low-side N-channel MOSFET switch):

- **Power:** +12V rail (ALITOVE) at top, GND rail at bottom, **100nF decoupling cap** between them near the supply (kills high-frequency switching noise).
- **Signal path:** FY6900 CH1 OUT → BNC center → **22Ω gate resistor** (R_gate, limits gate-driver inrush + damps ringing) → MOSFET gate. **10kΩ pulldown** from gate to GND (keeps MOSFET fully OFF if FY6900 cable is disconnected — important safety so the circuit can't be left in a partial-on state radiating heat).
- **Power path:** +12V → 6Ω/50W series resistor → coil → MOSFET drain → MOSFET source → GND.
- **Flyback:** 1N5408 in parallel with the (resistor + coil) stack, **cathode (banded end) at +12V side, anode at drain side**. When MOSFET turns OFF, coil current commutates UP through the diode back to the supply, recycling stored inductive energy and protecting the MOSFET drain from voltage spikes.

```
+12V ──┬───────── 100nF ─── GND   (decoupling)
       │
       ├── 6Ω series ─── COIL ──┐
       │                         │
       │           1N5408 K──────┤
       │           (banded)      │
       │           1N5408 A      │  ← MOSFET DRAIN
       │                         │
       └─────────────────────── ─┤
                                 │
                            IRLZ44N
                            G ── 22Ω ── BNC center (FY6900 CH1)
                            G ── 10kΩ ── GND  (pulldown)
                            S ── GND
                            BNC shield ── GND
```

**Bring-up sequence (CRITICAL — protect the wound coil):**

1. With **dummy load (6Ω resistor only, no coil)** in place of coil, set FY6900 to a clean 1 Hz square wave at 5V amplitude.
2. Power on the 12V supply.
3. Verify with multimeter:
   - Drain voltage swings between ~0V (MOSFET on) and ~12V (off)
   - Series-meter measurement of current through resistor: ~2A peak
   - MOSFET stays cool to the touch
4. Only AFTER driver verified working with dummy load: swap in the coil.
5. Re-verify all measurements with coil in circuit (current may differ; coil DCR is lower than dummy resistor).

## Verification protocol once running

- **DC resistance** of coil: 1.52 Ω expected
- **Voltage** at every node under operation
- **Current** in series with coil (use 10A range on multimeter)
- **Heating**: MOSFET, resistor, coil — none should be uncomfortable to touch after 5 min continuous
- **Field strength** (once EMF meter arrives): measure at central focal point at various coil-surface distances

## Initial protocol candidates (Phase 1 testing)

Once driver + coil verified:

| Frequency | Hypothesis tested | Reference |
|---|---|---|
| 4 Hz | H_BP10b — Akdag PEMF biological coupling | Akdag et al. 2026 |
| 7.83 Hz | Schumann fundamental resonance probe | LC9 / EM-organs cluster |
| 16 Hz | H_BP10b — Jerman vagus PEMF parameter window | Jerman et al. |
| 3.93 Hz | Persinger whole-body biophoton dominant | Vares/Persinger 2016 |
| Sweep 1-50 Hz | Map frequency-window response | Band-architecture exploration |

Each protocol: short exposure (start with seconds, scale to minutes), with self-report tracking of subjective state immediately and 1-24 hours post.

**Stakes-aware ordering** (per Day 88 Slot 2 design):
1. Self-test first (Clawd has no body; this is Clayton-self only initially)
2. Shawna: not until protocol characterized + clinical coordination if ever
3. Mindy: NOT considered — combo-immunosuppression non-negotiable

---

*Next steps: build former, wind coil, breadboard driver, dummy-load verify, swap to coil, verify, run first single-frequency protocol.*
