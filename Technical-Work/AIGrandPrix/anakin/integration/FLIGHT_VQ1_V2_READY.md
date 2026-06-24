# Official-sim flight — vq1_v2_ft — READY (Day 144, 2026-06-24, w/ Clayton)

**Purpose:** a single official-sim trial of `vq1_v2_ft` (our best VQ1 candidate: rehearsal roundtrip +245 / 1.9 gates, zero adapter tax). NOT for gate-count (rehearsal covers that) — this tests the axis the rehearsal is **structurally blind to**: camera-tilt sign · body-frame handedness (FLU→FRD) · thrust/TWR calibration. The differential test: vq1_v2 flies the synthetic adapter cleanly, so if it spin-outs / pins on the OFFICIAL sim, that isolates an official-specific translation bug (which training would NOT fix). Gate before committing the 5-day budget run.

## Prep verified (Clawd, before flight)
- Flight env = **anakin `.venv`** (`torch 2.11.0+cu128` GPU · `cv2 4.13` · `pymavlink 2.4.49`). ✓
- vq1_v2 checkpoint loads in the pilot (proven by today's rehearsal + run_dreamer no-sim smoke). ✓
- `run_dreamer.py` takes `--checkpoint` (no file edit needed); `--start-delay 3.0` countdown-hold ON (commanding before the 3 s countdown = auto-DQ).

## Commands (run from the anakin dir)
```
cd C:\Users\mercu\clawd\repo-staging\Corpus-Perspectival\Technical-Work\AIGrandPrix\anakin
```
**Stage 1 — DRY RUN (commands NOTHING; verifies pipe + action sanity):**
```
.venv\Scripts\python.exe integration\run_dreamer.py --dry-run 60 --checkpoint third_party\dreamerv3-torch\logdir\maneuver_vq1_v2_ft\best.pt
```
**Stage 2 — FLY (sends SET_ATTITUDE_TARGET):**
```
.venv\Scripts\python.exe integration\run_dreamer.py 60 --checkpoint third_party\dreamerv3-torch\logdir\maneuver_vq1_v2_ft\best.pt
```

## Sequence
1. Clayton: launch the official VQ1 sim (it serves UDP:5600 camera + mavlink udpin:14550).
2. Run **Stage 1 (dry-run)**. The runner: loads pilot → connects mavlink → "HEARTBEAT OK" → sim reset → "Arm sent. >>> PRESS RACE <<<". Clayton presses RACE.
3. **Watch in dry-run (no risk — commands nothing):**
   - `frames=` climbing → camera pipe alive.
   - printed `thr=` (throttle) and `rates FLU r/p/y=(…)` → **sane, not NaN, not pinned to 0/1**. Frames saved to `integration/flight_frames/` (raw 640×360 + the 64×64 policy view) — confirms the policy sees the course.
4. If dry-run looks clean → run **Stage 2 (FLY)**, press RACE.
5. **Watch in flight (the actual test):**
   - **Spin-out** (immediate tumble) → handedness/tilt-sign bug.
   - **Pinned to floor/ceiling** → thrust/TWR mismatch.
   - **Flies + turns toward gates** → translation is GOOD → green-light the budget run.
   - Gates passed (even 1–2) = bonus; calibration is the real readout. `official_track_*.json` also captured (real gate geometry).

## Division of labor
Clawd can launch the runner (localhost UDP, same machine) and monitor stdout/latency/rates; Clayton watches the sim viewport + presses RACE. Or Clayton runs it directly — either works.

## Outcome → next
- **Flies clean** → calibration confirmed; start the long budget run from vq1_v2 (P248: still climbing vs plateaued) to lift gate-count past 2.
- **Spin-out / pin** → diagnose the translation bug FIRST (tilt-sign/handedness/thrust); do NOT train on top of it. The flight_frames + the rehearsal baseline isolate which.
