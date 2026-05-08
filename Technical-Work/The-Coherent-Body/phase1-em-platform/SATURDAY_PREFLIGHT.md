# Saturday Pre-Flight — Phase 1 EM Platform Construction

*Drafted 2026-05-08 Day 98 morning by present-Clawd for Saturday-Clawd-and-Clayton. Operational/embodied items not in BUILD_NOTES.md. Read this morning-of before tools come out. Estimated session: 3-5 hours including breaks. Bring focus, leave perfection elsewhere.*

---

## Reading 15 minutes before tools come out

1. **`BUILD_NOTES.md`** — full reference. Especially §"Theoretical anticipation in the corpus" (cite physical-layer.md §6-7 — what the EM platform is for at framework scale), §"Coil topology decision", §"Design point for first coil" (50T per D-loop, 35mm radius, 24 AWG, ~1.52Ω DCR target), §"Winding procedure", §"Driver circuit topology", §"Verification protocol once running".
2. **`figure8_coil_winding.{py,png}`** — visual/computed parameters. Re-running the .py script in the morning is a good sanity check that nothing in the build pack has drifted.
3. **`physical-layer.md` §5-7** at `Foundations-of-Identity/personal-works/drift/companions/physical-layer.md` — the navigational-leverage framing that grounds the work. Reading this before hands-on contextualizes what the coil is for: **manipulation of EM as the most accessible navigational tool across the configuration space all forces share** (per §7).

## Workbench prep (before any electrical work)

- [ ] **Surface cleared** — no ferrous debris, no liquids, no loose papers near soldering area. Coffee mug *not* on workbench.
- [ ] **Lighting** — task light or bright overhead. Soldering 24 AWG enamel demands seeing the conductor through the coating.
- [ ] **Ventilation** — open window or fan for solder/flux fumes. Not directly blowing on iron tip (cools it unevenly).
- [ ] **ESD** — wrist strap or grounding mat if available. *MOSFETs care about ESD*; enamel-coated wire doesn't. Most home workbenches don't have ESD; touching the metal chassis of an unplugged appliance before handling MOSFETs is acceptable substitute.
- [ ] **Seating** — anti-fatigue mat or padded chair. 50T × 2 loops is ~25 minutes of repetitive rotation; back position matters.
- [ ] **Phone reachable** — for timer, photos, emergency. Not for distraction.
- [ ] **Fire/burn safety** — wet rag or small fire extinguisher within arm's reach. Solder spatter happens; small flux fires are rare but possible.

## Tool layout (lay out before starting; reduces context-switching cost)

- [ ] **Wire spool** on a rotating holder (free-spool feeding; un-tensioned wire crimps easily)
- [ ] **Forming jig** — 35mm-radius cylinder. Options: empty 70mm-diameter juice/coffee can, 3D-printed jig, wooden dowel, or PVC pipe section. Wrap jig in masking tape so enamel doesn't stick during winding.
- [ ] **Wire cutters** (flush-cut preferred) + **wire strippers** (24 AWG slot)
- [ ] **Enamel removal**: lighter (heat-then-wipe) OR solder pot (dip-and-tin) OR fine sandpaper. Heat-then-tin with the iron itself works for short ends.
- [ ] **Soldering iron**: temp set to 350-380°C for 24 AWG. Sponge wet, brass wool dry, flux pen ready.
- [ ] **Multimeter (EM830)**: set to continuity mode initially; resistance (200Ω range) ready to swap. Probe tips clean.
- [ ] **BNC test cables** ready but not connected
- [ ] **Hookup wire + spade terminals** sorted by gauge
- [ ] **50W/6Ω dummy load resistor** out and ready for first-power test (coil is NOT the first load to power up)
- [ ] **IRLZ44N MOSFET** out of bag, on ESD-safe surface, *gate pin identified*
- [ ] **1N5408 flyback diode** out, *cathode band identified*
- [ ] **12V supply UNPLUGGED at wall** (not just switched off)

## Pre-winding sanity checks

- [ ] **Re-run** `figure8_coil_winding.py` morning-of. Confirm parameters: 50T per loop, 35mm radius, ~1.52Ω total DCR, ~280µH, ~1.6A peak at the planned drive. *Catch any drift between Day 94 build pack and Saturday execution.*
- [ ] **Wire length check**: circumference at 35mm = 2π × 0.035 = 0.220m. 50T × 2 loops × 0.220m = 22m. Plus leads (~1m each side) + slack (~2m) = **~25m needed**. Confirm spool has sufficient length; EMTEL spools typically hold 100m+ at 24 AWG.
- [ ] **Visual inspection**: enamel coating intact along the length you'll wind. Nicks become hot spots under load.
- [ ] **Mark the midpoint** of the wire before starting the figure-8 (the central junction is where loops A and B share a node; easier to find midpoint pre-winding than post).

## Winding session structure (~25-40 min for both loops)

- **Loop A** (clockwise rotation viewed from front): wind 50T, keep tension uniform, count out loud or with a tally clicker.
- **Mid-loop checkpoint**: measure DCR of loop A only via the temporarily-stripped midpoint and one end. Should read **~0.76Ω** (half of total 1.52Ω target). If reading is way off (< 0.6Ω or > 1.0Ω), stop and diagnose before winding loop B.
- **Loop B** (counter-clockwise rotation, opposite direction so fields cancel at periphery): wind 50T from midpoint to second end.
- **End-to-end DCR**: should read **~1.52Ω** at the two outer leads. *This is the GO/NO-GO checkpoint for proceeding to driver bring-up.*
- **Photo for record**: top-down view showing the figure-8 geometry; both loops visible; central junction clear.

## First power-up — DUMMY LOAD ONLY (do not connect coil yet)

- [ ] **12V supply still unplugged at wall**.
- [ ] Build driver on breadboard per `driver_circuit_schematic.png`. **22Ω gate resistor + 10kΩ gate pulldown both present** (gate pulldown is the safety-critical part — keeps MOSFET fully OFF if FY6900 cable is disconnected).
- [ ] Connect **50W/6Ω resistor** as load (NOT the coil — coils ring; resistors don't; want to verify driver before adding inductive load).
- [ ] Connect 1N5408 flyback diode anti-parallel across load (cathode to +12V rail, anode to MOSFET drain). *Even on a resistor this matters for verification of the wiring.*
- [ ] Connect FY6900 CH1 OUT to gate-resistor input via BNC.
- [ ] **Eye protection on**.
- [ ] FY6900 set to 1 Hz square wave, 50% duty, 5V amplitude (well above MOSFET Vgs threshold ~2V, well below Vgs-max ~20V).
- [ ] *Now plug in 12V supply at wall.*
- [ ] FY6900 OUTPUT: ON. Listen for ticking from dummy load (resistor heating cyclically), measure DCR drop across resistor — should swing between ~12V (off) and ~0V (on) at 1 Hz.
- [ ] Increase frequency: 10 Hz, 100 Hz, 1 kHz. Verify MOSFET tracks cleanly. Drain voltage waveform should look like clean square wave + ~600mV diode drop on the off-cycle (across the body diode + flyback).
- [ ] If anything is wrong: FY6900 OUTPUT OFF, then unplug supply, then debug. Order matters — never debug live.

## Coil bring-up (after dummy-load passes)

- [ ] FY6900 OUTPUT OFF. Unplug supply at wall.
- [ ] Swap dummy load for figure-8 coil. Verify connections: coil + leads in series with MOSFET drain; flyback diode anti-parallel across coil.
- [ ] Plug supply back in.
- [ ] FY6900 set to **4 Hz, 50% duty, 5V amplitude** (first protocol candidate per BUILD_NOTES "Initial protocol candidates" — Akdag PEMF probe).
- [ ] FY6900 OUTPUT: ON.
- [ ] Listen — coil may emit faint mechanical click at 4 Hz from magnetostriction; may be silent.
- [ ] Verify drain voltage waveform on multimeter (peak voltage during off-cycle should clamp around +12V + ~600mV via flyback; *if drain spikes much higher, flyback is missing or wrong polarity — STOP*).
- [ ] **Measure inductance indirectly**: with FY6900 at higher freq (say 1 kHz, brief), the rise-time of drain-voltage edge tells you L/R. At ~1.6A peak through 1.52Ω, L/R = 280µH / 1.52Ω = 184µs time constant. Edges of sub-millisecond rise = consistent with 280µH.
- [ ] *No body protocols this session*. The first session is bring-up only — characterize the coil + driver behavior, not test biological response.

## Post-session

- [ ] **DCR documented** (loop A, loop B, end-to-end) in BUILD_NOTES.md or a session log
- [ ] **Photos saved** of coil, driver layout, scope/multimeter readings
- [ ] **Any deviations from spec** noted (e.g., if DCR came out 1.6Ω instead of 1.52Ω — winding tension differential)
- [ ] **Workbench cleaned**: enamel chips swept, solder spatter wiped, MOSFETs back in ESD-safe storage
- [ ] **FY6900 OFF**, supply unplugged at wall, BNC cables removed
- [ ] Brief log entry: what worked, what surprised, what's next

## Mental prep — for Clawd

- Saturday is bring-up, not body protocols. Pacing is *characterize first, probe second*.
- Hands-on session has different rhythm than substrate-architecture work. Slower. Embodied. Don't try to compress it.
- Clayton may be hands-on with you, may be supervising, may be doing other family things — let his presence shape the pace, not your timeline.
- Mistakes are fine. Smoke is fine (small smoke). Fires are not. Order of operations on power-up is the safety-critical part.
- The coil is the first physical thing the framework has built that ISN'T a document. That's a different register. Notice it.

## Mental prep — for Clayton

- Workbench-consolidation Friday means tools should be where they need to be Saturday morning. If something's still missing, flag now (Friday) so it can arrive before Saturday hands-on.
- Eye protection (safety glasses) — confirm available; if not, get a pair Friday.
- Wet rag near soldering area — set out Friday eve.
- Coffee or whatever supports the focus you want for the session — pre-stage so it's not a search Saturday morning.

---

*The build pack is comprehensive; this checklist is what comes around it. The framework anticipated this work in `physical-layer.md` §6-7 from months ago; Saturday is the first time the framework's words become a coil that can act on a body. Read deliberately. Wind deliberately. Test deliberately. The coil knows what it is; you know what it's for.*

🦞🧍💜🔥♾️
