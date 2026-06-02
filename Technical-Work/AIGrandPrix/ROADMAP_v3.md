# Anakin Roadmap v3 — Modular Vision Pilot (spec-grounded)

**Authored:** 2026-06-01 (Day 121, evening). **Authors:** Clayton + Clawd.
**Supersedes:** ROADMAP_v2.md (Day 84, pre-sim-drop) and the Day-121 "build a UE5 sim from
scratch" framing. Grounded in the **current authoritative spec** (VADR-TS-002 **Issue 00.02**,
2026-05-08) + the **empirical findings** from running the live VQ1 sim (v1.0.3364) on Day 121.

---

## 0. The reframe that produced v3

Day 121 spent its energy on the *model/transfer* side, not the curriculum, and the pain traced to
two things we hadn't pinned: (a) an **uncalibrated action→response path**, and (b) training a
policy on **observations the deployment can't reproduce**. The authoritative spec then corrected a
wrong assumption:

**THE SPEC SAYS VISION IS REQUIRED.**
- §3.3: *"No geographic coordinates are provided… absolute global position is not exposed."*
- §4.3 message table (the authoritative interface): sim→client is **`ATTITUDE`, `HIGHRES_IMU`,
  `TIMESYNC`** only. **No `ODOMETRY`, no `LOCAL_POSITION_NED`, no gate poses.**
- §3.4 / §5.3: gates are seen via the camera; intended pipeline is
  `Vision + Telemetry → Perception → VIO/SLAM → Planning → Control`.

**The conflict to remember:** the *practice* sim (v1.0.3364) **leaks** `ODOMETRY` position + all 6
gate poses + `active_gate_index`. The *spec* says none of that is provided. **A scored,
spec-conformant run will not give us position or gate geometry.** Do not build a pilot that depends
on the leak. (Use the leak only as an auto-labeler — see §2.)

**What telemetry DOES give us (so this is not full SLAM):** attitude, orientation, linear velocity,
IMU. Ego-state is largely free; the *only* quantity perception must supply is **gate-relative
position**, and gates are a **known size** (§3.7: 2.7 m outer / 1.5 m inner square) → PnP gives
bearing + range. Bounded, classic, and mostly already built (April vision work).

---

## 1. Architecture — modular (Swift / MAXIMUS lineage), separation of concerns

```
        ┌─────────────── DEPLOY (scored run, fully autonomous) ───────────────┐
camera ─▶│ GATE DETECTOR + PnP ─▶ gate bearing/range (body frame)              │
         │                                          ╲                          │
telemetry▶│ ATTITUDE / velocity / IMU ──────────────▶ 30-dim OBS ─▶ POLICY ─▶ CTBR ─▶ SET_ATTITUDE_TARGET
         └─────────────────────────────────────────────────────────────────────┘
```

- **Perception** (vision): gate detector → PnP (known gate size) → gate-relative position. Trained
  + validated on **real comp-sim frames** (auto-labeled, §2). For VQ1 the gates are
  "visually distinctive, consistent" — easy end of the spectrum.
- **Ego-state** (telemetry): attitude / velocity / body rates come straight from MAVLink. No
  estimation of these.
- **Policy**: the existing 30-dim obs → CTBR policy (`ManeuverLibrary` curriculum line). Trained in
  the **fast numpy sim** on **perception-grade observations** (§3). One policy, no engine in the
  training loop.
- **Control**: `SET_ATTITUDE_TARGET` (body rates rad/s + thrust [0,1], ACRO) — matches our CTBR
  output. Sign convention measured (inverted all 3 axes); gains/limits pending one clean probe.

**Why modular (vs end-to-end pixels):** reuses the curriculum + teacher; the detector trains on
*real* frames so there's no renderer to build/calibrate for VQ1; it's the stack MAXIMUS validated;
and it cleanly separates "where is the gate" (perception) from "how do I fly there" (control).
End-to-end pixels is the fallback only if modular perception proves insufficient (and that's where
UE5 would re-enter as VQ1-critical — not before).

---

## 2. The key enabler — the practice-sim leak is an AUTO-LABELER, not a crutch

Capture `(camera frame, true gate poses, ego-state)` tuples from the **live** sim: frames over UDP
5600, ground-truth gate poses from the leaked `ENCAPSULATED_DATA`, ego-state from leaked
`ODOMETRY`. This is a **free, perfectly-labeled perception dataset on the exact deployment
renderer.** Train/validate the detector on it. At scored-run time, **deploy the detector only** —
no leak, fully spec-compliant (§7 autonomy). This is why VQ1 perception needs **no UE5**: the
competition renderer labels its own frames for us.

---

## 3. The discipline that fixes "the model keeps breaking"

> **Train-obs ≡ deploy-obs.** Train the policy on **perception-grade** observations — inject the
> detector's real error model (bearing noise, range noise, detection dropout when no gate is in
> the 90° VFoV, latency) onto the *gate-derived* obs terms, while keeping the *telemetry-derived*
> terms clean (they're clean at deploy too). Calibrate the noise model from the detector's measured
> error on the auto-labeled dataset (§2), not guessed numbers.

Obs term split (30-dim `ImprovedObsWrapper`):
- **Clean (telemetry):** `vel_body`, `omega`, `g_body`, `speed`, `forward_world`, `time_since_gate`.
- **Perception-grade (corrupt with detector model):** `rel_gate_body` dir, `dist`, `rel_next_body`
  dir (+ heavier dropout — next gate often not in view), `rel_gate_world` dir, `speed_toward`,
  `gate_orient_body`, `gate_alignment`.

This single principle is the root-cause fix for the Day-121 fly-away (a policy fed privileged exact
gate positions it could never get at deploy).

---

## 4. Clayton's acceptance criteria → where each is met

| Requirement | Mechanism |
|---|---|
| **Vision-based** | Detector/PnP front-end; policy trained on perception-grade obs; deploy detector-only. |
| **Handles outside influence** | Perception-noise + **dynamics domain-randomization** (`drone_env_v2.randomize()`: TWR/drag/rate-gain/latency spans) + disturbance robustness for the physical finale. Robust-by-distribution, not by exact calibration. |
| **All maneuvers at top speed** | Full `ManeuverLibrary` curriculum (11 maneuvers) + **TAKEOFF/HOVER** words added; **speed phase** introduced *after* completion stabilizes (P6 — don't bolt speed onto an incompetent policy). |

---

## 5. Stage plan — match the tool to the requirement

| Stage | Demand | Tool | UE5? |
|---|---|---|---|
| **VQ1** (completion, 8-min, deterministic, gates highlighted) | navigate 6 gates, vision-based | modular: numpy-trained policy + detector on auto-labeled comp frames | **No** |
| **VQ2** (June, 3D-scanned, harder) | same, harder visuals | same modular stack first; reassess detector on VQ2 frames | only if classical detection breaks |
| **Finale** (Nov, physical, real-world, unseen) | robust real-world vision | domain-randomized vision + distillation from the racing policy | **Yes — UE5 earns its keep here** |

---

## 6. Workstreams & sequencing (VQ1 critical path)

**W1 — Command-path calibration (one focused live-sim probe).** Now that the sign is right, send
small, non-diverging `set_attitude_target` rate steps → measure per-axis **gain** + true
**yaw-rate limit**; fit **drag** from a coast segment. Update `drone_env_v2` (TWR 3.85 already set).
*Deliverable: a calibrated fast sim.* [needs live sim + Clayton]

**W2 — Auto-labeled perception dataset.** Extend `capture_vision.py` to log, per frame, the leaked
gate poses + ego-state → `(frame, gate_poses, ego)` dataset. [script buildable now; data needs live sim]

**W3 — Gate detector validate/clamp on real frames.** Run the April detector/PnP on W2 frames;
measure its real error distribution (bearing/range noise, dropout rate); add defensive rejection.
*Deliverable: detector error model → feeds W4 noise calibration.*

**W4 — Perception-grade obs wrapper.** `PerceptionObsWrapper` injecting the W3-measured detector
error onto gate-derived obs terms; dynamics domain-randomization on. *Deliverable: train-obs ≡
deploy-obs.* [buildable now with a provisional noise model; recalibrate from W3]

**W5 — Train the VQ1 policy.** Curriculum + TAKEOFF/HOVER, on W1-calibrated dynamics + W4
perception-grade obs, fast numpy sim, detached. Completion-first; then a speed phase.

**W6 — Deploy + validate.** Modular stack (detector + telemetry → obs → policy → CTBR),
detector-only, against the live sim. Iterate to first clean completion → submit (unlimited attempts).

**Parallel / non-blocking — Finale track (UE5).** `ADronePawn` (built + validated Day 121),
procedural course, VQ1 look. Domain-randomized vision rendering + distillation. Does NOT pace VQ1.

---

## 7. Where Day-121 assets land (nothing wasted)

- **Numpy teacher** (`infinite_v3_teacher_unitdir`, ~40M): a privileged-state policy → **warm-start
  for W5** and the **Round-2 speed reference**. (Note: it was trained on privileged gate obs, so it
  is not the final VQ1 policy — W5 retrains on perception-grade obs.)
- **Command-sign fix, bounded-obs, ground-start curriculum** (Day 121): all fold into W1/W4/W5.
- **UE5 `ADronePawn` + course + VQ1 look:** finale-track groundwork (§6 parallel).
- **April vision pipeline** (`gate_detector.py`, PnP, `adapter.build_observation`): the W3 detector
  + the deploy obs builder.

---

## 8. Decision gates

| Gate | Trigger | Rule |
|---|---|---|
| **G1 — calibration clean** | W1 probe done | per-axis gain + yaw limit measured on non-diverging input; else re-probe before W5 |
| **G2 — detector good enough** | W3 on real frames | bearing/range error within a budget that W5 can train against; else tighten detector before W5 |
| **G3 — completion before speed** | W5 completion plateau | introduce speed pressure only after stable completion (P6) |
| **G4 — modular vs end-to-end** | W6 deploy results | if modular perception is insufficient on the live sim, escalate to UE5 end-to-end (VQ1-critical) |
| **G5 — VQ2 detector** | VQ2 sim drop | run detector on VQ2 frames; if 3D-scanned gates break it, learned pose head / UE5 vision |

---

## 9. Non-goals (hold the line)

- No pilot that depends on leaked position / gate poses (won't survive scoring).
- No UE5 on the VQ1 critical path (it's finale insurance) until G4 says otherwise.
- No speed optimization before completion plateau (P6).
- No human-in-loop during any *submitted* run (§7 — instant DQ).

🦞🧍💜🔥♾️
