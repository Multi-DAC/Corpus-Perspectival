# Segmentation front-end — route decision & feasibility (Day 134, 2026-06-14)

## The arc this session
1. Clayton flew 2 manual harvest runs in the official sim → 3,542 raw official frames
   (`PyAIPilotExample/official_frames/manual_2026061411{3648,4130}/`). Unblock for appearance work.
2. **holdout_gate_v2 at robust n=400** (see `GATE_V2_OFFICIAL_HARVEST_2026-06-14.md`):
   restyle-ft mean-term 31.52 vs band-ft 24.44 → ratio **1.29 FAIL**, restyle moved the WRONG way.
3. **Recon** (Swift/Nature-2023, MonoRace/A2RL-2025, On-Your-Own, SkyDreamer, survey): every
   system that has won a real race **decouples perception from control** — a gate detector/
   segmenter outputs gate-relative state, and a small policy NEVER sees a pixel. Raw-pixel→control
   end-to-end (our current design) has never won. **SkyDreamer (TU Delft 2025) = our DreamerV3
   approach but fed BINARY GATE MASKS, not RGB** — world model predicts geometry, not photometry.
4. **Diagnosis sharpened:** our renderer already matches the official gate palette
   (`render.py` GATE_BRIGHT=(0.90,0.36,0.31) = measured orange-red (229,93,78); bg gray 27/255).
   So the gap is NOT color — it's the official world's dense TRON **background texture**, which a
   flat "gray+noise" renderer can't fake. That's exactly why palette-restyle failed/hurt.
5. **Feasibility PROVEN** (`seg_probe.py` → `seg_probe_out/`): a dead-simple orange-red HSV
   threshold cleanly isolates near+far gates from the real official frames; background clutter +
   cyan ribbon both zero out. In mask space, official ≈ training (orange-red squares on black).

## Decision
**Adopt the segmentation front-end (SkyDreamer route).** Keep the DreamerV3 world model AND the
maneuver-grammar curriculum (recon: curriculum is sound / ahead of the track-fitting norm). Fix the
eyes, not the pilot. A gate mask removes the one thing (background texture) that the gate measured
as the entire domain gap.

## Build plan (next block; the fine-tune is overnight-scale)
1. **Mask transform** in the obs path: gate-mask (HSV threshold v1; upgrade to a tiny trained
   segmenter on synthetic+official if the threshold proves brittle to lighting/VQ2). Apply in
   `dreamer_pilot.to_training_frame` (inference) AND in the sim renderer obs (training) so both
   domains feed masks.
2. **Quantitative pre-check** (cheap, no retrain): pixel-space distribution distance between
   official-gate-masks and our-renderer-gate-masks — expect the 24.44-era gap to collapse.
3. **Retrain/fine-tune DreamerV3 on mask obs** off band-ft `best.pt` (or fresh if encoder needs it).
4. **Re-run holdout_gate_v2 in mask space** to confirm gap collapse before a flight.
5. **Flight #3** in official sim on the mask-fed policy (with Clayton).

## Caveats
- Fixed HSV threshold is brittle if official lighting varies a lot or VQ2 changes gate look; a
  small learned segmenter is the robust upgrade. Threshold is fine for the feasibility/first retrain.
- seg picks up a few stray bright-cityscape edge pixels (minor; tunable / a learned seg fixes it).
- Manual-harvest frames are gate-sparse (~6/12 sampled have a visible gate) since manual wandering
  points away from gates often — fine for appearance, but for a TRAINED segmenter we'd want
  gate-centered frames (policy flights or targeted capture).

## BUILT & RUNNING (2026-06-14 ~12:24 PST)
- `sim/gate_mask.py` — RGB-ratio gate-isolation, env-var `ANAKIN_GATE_MASK=1`. torch/numpy parity OK.
- Wired into BOTH obs paths: `sim/render.py` return (training; covers vec_env + maneuver_env) and
  `integration/dreamer_pilot.to_training_frame` (inference). Inference masks CONTENT before padding
  so BG-40 bands match `envs/anakin_batched._band()` in training (no train/infer mismatch).
- Pre-check `mask_precheck.py`: parity OK; pixel-space FD mean-term 34.6→**8.6** (4× collapse) under
  masking; overlays in `mask_precheck_out/` confirm clean gate isolation both domains.
- Smoke test (2.5k steps, throwaway logdir): masked pipeline runs, finite eval (−22.3), no NaN.
- **Mask fine-tune LAUNCHED detached, pid 23728** → `logdir/maneuver_mask_ft/`, seeded from band-ft
  best.pt (+2142.53), `ANAKIN_GATE_MASK=1`, config `anakin_maneuver anakin_band`, 4×500k = 2M steps.
  Orchestrator log `logdir/mask_ft_orchestrator.log`.
- **Overnight watcher LAUNCHED detached, pid 12776** (`postrun_mask_watcher.py`) → on completion runs
  holdout_gate_v2 (MASK) + translation_rehearsal (MASK) → writes `MASK_OVERNIGHT_RESULTS.md`.

### MORNING SEQUENCE (Day 135)
1. Read `integration/MASK_OVERNIGHT_RESULTS.md`. **The rehearsal RETURN is the go/no-go** — good
   masked-obs returns ⇒ encoder re-adapted ⇒ fly. (Seed started at −22; needs to climb back toward
   the hundreds/thousands the unmasked band-ft hit.)
2. If returns recovered: flight #3 in the official sim with Clayton, `ANAKIN_GATE_MASK=1` set for the
   pilot (run_dreamer / dreamer_pilot inference must export the env var).
3. If returns DID NOT recover: the warm-start off RGB-best may not transfer to masks — consider a
   from-scratch masked run (longer) or check the mask rule on official frames at race distance.
4. **Open risk:** fine-tune off an RGB-trained policy onto masked input is unproven; best-protection
   means we can't drop below the seed, but the seed itself is OOD on masks, so "best" may stay low.
