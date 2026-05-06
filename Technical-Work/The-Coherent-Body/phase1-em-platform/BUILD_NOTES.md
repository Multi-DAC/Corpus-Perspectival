# Phase 1 EM Platform — Build Notes

*Started 2026-05-05 evening, Day 94. Hardware in hand; coil winding next.*

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

| Parameter | Value | Rationale |
|---|---|---|
| Wire | 24 AWG enamelled (EMTEL, in hand) | Already procured; good gauge for our currents |
| Turns per D-loop | 50 | Field strength × wire-length tradeoff |
| Loop radius | 35 mm | ~70 mm diameter per loop, hand-sized |
| Total wire | ~18 m | Cut 18.5 m to allow ~0.5 m for leads |
| Expected DCR | 1.52 Ω | Verify with multimeter after winding |
| Inductance | ~280 µH | Reactance negligible below 1 kHz |
| Series resistor | 6 Ω (50W power resistor) | Limits current to 1.6A |
| Peak current | 1.59 A | At 12V supply, total R = 7.52 Ω |
| Peak field at focus | ~2.87 mT | ~57× Earth's field; in published bioactive PEMF range |

These numbers are starting points — adjustable by changing turn count, loop radius, or series resistance.

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
