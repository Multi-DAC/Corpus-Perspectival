# Official-sim flight — vq1_v2_ft — Day 144 (2026-06-24, w/ Clayton)

**First official-sim flight of vq1_v2.** Runner `run_dreamer.py` (GPU `.venv`, `--checkpoint maneuver_vq1_v2_ft/best.pt`). Dry-run (75s) → real fly (50s). Clayton watched the viewport; Clawd read the wire + frames.

## Verdict: GREEN — he flies the real sim. Failure = control precision, NOT translation.
**Clayton's eyes:** took off, **approached a gate and nearly threaded it, then flew over it**, continued over the course, **then lost control downrange.** Not smooth — **bobbing** — but real, committed flight. No spin-out, no pin.

### What this confirms (the axis the rehearsal couldn't test)
- **Tilt-sign / handedness / thrust calibration are SOUND.** He takes off stably, navigates toward a gate, commits to it. The Day-130 spin-out class of bug is absent.
- **Wire:** ~30 Hz control, **19 ms act latency** (GPU, real-time), throttle + rates finite/in-range/both-signs, no NaN/freeze. RACE + 3 s countdown-hold worked.
- **Frames (`flight_frames/124056_*`):** at s00150 the **orange-red gate renders exactly as our restyle training** and is clearly legible; policy sees it. At s00350 the camera is pitched up at the ceiling grid (post-overshoot, uncontrolled). → appearance translation good; failure is downstream control.

### The failure modes, named
1. **Vertical/altitude instability ("bobbing")** = throttle slamming 0↔1 on the wire. Control-precision problem.
2. **Gate overshoot** — flew *over* the gate instead of dropping through. ← see geometry finding below.
3. **Loss of control downrange** — pitched up, lost the line. Budget/training axis (A154: many-gate chaining is budget-governed).

## ★ Geometry analysis — official course vs our curriculum (the actionable find)
Captured `official_track_*.json` (6 gates, 161 m). Computed distances/turns/climbs vs `sim/maneuvers.py`:

| axis | OFFICIAL course | our curriculum | verdict |
|---|---|---|---|
| **gate spacing** | **24–39 m (mean 27)** | mostly 3–14 m; max ~22–24 m (sprint/speed_trap) | **OUT OF DISTRIBUTION — we train tight, course is long** |
| heading turns | ≤20° (mean 12°), gentle S | gentle_arc 10–30° + hard_turn 60–120° + hairpin ≤180° | over-prepared (good for VQ2) |
| vertical | ~15° segs, ~26 m, front-loaded then flat | climb/dive 18–45° | over-prepared |

**The gate-spacing OOD is the cleanest explanation for the overshoot:** a policy tuned to expect a gate every ~8 m, dropped onto a 27 m approach, builds the wrong speed/timing and sails over. Turns + vertical are already harder in training than VQ1 needs.

## Plan (Clayton: "I trust your judgement")
**Budget run from vq1_v2, curriculum gate-spacing widened to the official band** (general + vision-only throughout; distribution-calibration, NOT geometry-as-input, NOT fixed-layout overfit). Targets bobbing + overshoot. "Generalize first" phase; course-tight fine-tune held for the final stretch before VQ1 (~27 days out). Brightness/contrast: gates rendered correct orange-red → likely already handled (Clayton's recollection); quick histogram to close it.

## Artifacts
`integration/official_track_20260624_124056.json` (real 6-gate geometry) · `integration/flight_frames/124056_*` (raw + policyview) · run_dreamer dry+fly traces.
