# Tuesday Plan — Anakin: from fine-tune-patching to a vision flight school

**Date set:** 2026-06-01 (Day 121). Execute: Tuesday evening (token-budget refresh).
**The pivot (Clayton's call, agreed):** stop fine-tuning a policy across mismatched assumptions.
Build a **flight school on the competition's own engine** and train Anakin **from scratch**,
**through vision**, on an **infinite/random grammar-school curriculum** in the real distribution.

---

## Why we pivoted (the weekend in one paragraph)
One opaque VQ1 failure → three root causes: (1) body-rate SEND signs inverted [FIXED, deploy,
test-locked]; (2) no-takeoff, trained mid-air only [FIXED: ground_start + TWR 3.85]; (3) fly-away
= obs encoded RAW UNBOUNDED gate distance → VQ1's 23m start landed ~6σ off-distribution → stick
saturation. We bounded the encoding [obs_encoding.py, deploy==training verified] and it WORKS at
the obs level (live `max|obs-norm|` 10→3.41, calm flight) — **but it didn't produce navigation**,
because we kept *fine-tuning across three simultaneous shifts* (representation raw→bounded,
distribution 3m→23m, dynamics TWR 3.3→3.85). A policy can't cleanly re-adapt baked-in steering.
**From scratch on a matched sim learns the real distribution natively — no adaptation friction.**

## Engine finding (the throughput scout, done 2026-06-01)
The competition sim is **Unreal Engine** (`AIGP_3364/FlightSim.exe`, `Engine/`,
`Manifest_*_Win64.txt`). Implications:
- **Vision-native + watchable: YES** — Unreal renders real frames; this is the AirSim lineage
  (AirSim was built on Unreal for exactly drone vision-RL). "Watch him train through vision" is home turf.
- **Throughput is the constraint** — Unreal headless (`-nullrhi`/`-RenderOffScreen`), accelerated,
  and parallel are all *possible* but heavy (GPU+RAM per instance), nowhere near a numpy sim's
  millions-of-cheap-steps. Pure vision-RL-from-scratch on Unreal at RL step counts would crawl.
- **⟹ STAGED pipeline, not pure-on-their-engine.**

## WINDFALL SCOUT UPDATE (2026-06-01, token reset) — engine ACCESS resolved; pivot reshaped
**FALSIFY (high conf) of "build our flight school ON their engine":** the competition sim is a
**closed, auth-gated, real-time, single-instance Unreal SERVER** — you log in with account
credentials, and the ONLY interface (PyAIPilotExample/main.py) is a real-time UDP CLIENT:
telemetry+vision in (ports 14550/5600), commands out. **No reset / no step / no timestep
acceleration / no headless / no SDK / no parallel.** It is NOT an engine we can build on; it's a
finished product behind a login. So it cannot be a bulk-RL training surface.

**Reshaped architecture (cleaner than it sounds):**
- **Their sim's role = real-time VALIDATION + the actual scored qualifier runs** (drive via UDP as
  we do now). Plus: a source of real vision frames (port 5600) to *collect* for offline training.
- **ALL bulk training is in OUR OWN sims:**
  - State: our numpy fast-sim (have it).
  - **Vision: WE build a lightweight vision sim.** KEY ENABLER: VQ1 is per the README "Simple,
    high-contrast, desaturated gate environment" — that's CHEAP to render ourselves (high-contrast
    gate shapes on a desaturated background); no Unreal needed for VQ1 vision-RL. (VQ2 = "high-
    fidelity 3D-scanned" is the hard one — defer; collect-frames-from-their-sim + domain-rand is the
    likely VQ2 path.)
- Net: we do NOT reverse-engineer their Unreal (impossible anyway). We build our own VQ1-visual
  flight school + use their sim to validate. Everything we built stays the spec.

## The two-stage pipeline
**Stage 0 (pre-req, do FIRST):** fold the **A150 lateral-decoupling** into `obs_encoding.py`.
Current `bound_vec = unit_dir × tanh(|v|/10)` couples direction+magnitude → lateral components
get tiny-variance → over-normalized → policy reads *how far* but not cleanly *which way* (steering
is a lateral task — likely why the bounded run flew calm but didn't navigate). Fix: encode gate
vectors as **raw unit direction (natural per-component variance) + a separate bounded magnitude**
(for rel_gate_body the magnitude already lives in the bounded dist scalar; for rel_next_body /
rel_gate_world add a bounded-mag dim or accept unit-dir-only). Re-run `test_obs_encoding.py`.
**Get the encoding right BEFORE anything trains on it.**

**Stage 1 — fast state-based pretrain (our numpy sim, cheap, millions of steps):**
- FROM SCRATCH (fresh policy, NOT resume — use the from-zero trainer, not train_phase2's resume).
- `InfiniteGateEnv` with ALL fixes: bounded+decoupled encoding, ground_start far 15–28m, TWR 3.85.
- **Grammar-school curriculum ORDER** (design this): takeoff → hover/stabilize → single far gate
  (from rest) → two-gate sequences → partial courses → full random courses. Verify gate spacing
  matches VQ1 (~23m; we have the live track layout from `flight_obs_dump`/RACE_STATUS).
- Deliverable: a state-based pilot as good in our matched sim as the old one was "blind."

**Stage 2 — vision + final polish (their Unreal engine, fewer steps, real frames):**
- Render-matched camera (640×360, fx=fy=320, cx=320, cy=180, 20° tilt — already in spec).
- Two candidate transfer paths: (a) learned **gate-detector front-end** feeding the Stage-1 state
  policy (cheaper, modular); (b) **end-to-end pixels→CTBR** fine-tune from Stage-1 (richer, slower).
  Start with (a).
- This is where we *watch* — both his flight and his vision.

## First feasibility items for Tuesday (resolve before committing the big run)
1. **How to drive `FlightSim.exe` programmatically for TRAINING** — does it expose anything beyond
   the live MAVLink/UDP race interface (port 14550, arm→RACE→telemetry+track stream)? Can it be
   stepped/reset headlessly + faster-than-real-time, or is it locked to real-time single-loop?
   (If locked: Stage 2 is slow-but-doable polish, not bulk training — which the staged plan assumes.)
2. **Parallel instances** feasibility (RAM/GPU budget on the Ryzen 9 / RTX 5080 box).
3. Confirm the Stage-1→Stage-2 transfer interface (state obs ≅ gate-detector output schema).

## What's already done (the spec, not wasted)
- `sim/obs_encoding.py` (bounded encoding; needs the A150 decoupling refinement)
- `sim/infinite_gate_env.py` (curriculum + ground_start far + bounded obs; `--ground-start-prob`)
- `sim/drone_env_v2.py` (TWR 3.85)
- `vision/vq1_pilot/state_pilot.py` (command-sign deploy fix + `--ckpt` + obs dump)
- `vision/vq1_pilot/{CALIB_FIT,FARSTART_FALSIFY,TAKEOFF_EVAL_RESULTS}.md` (the record)
- Tests: `test_command_frame` 4/4, `test_ground_start` 3/3, `test_obs_encoding` 3/3

🦞🧍💜🔥♾️
