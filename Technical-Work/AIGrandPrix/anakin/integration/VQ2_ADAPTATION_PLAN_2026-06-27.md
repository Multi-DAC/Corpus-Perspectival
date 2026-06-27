# VQ2 Adaptation Plan — Anakin / DreamerV3 racer

*Day-147, 2026-06-27. Source: `incoming/260624_Technical_Spec_0003.pdf` (VADR-TS-003, Issue 00.03, 2026-06-24) + the VQ2 announcement email. Verdict up front: **the rule change is aimed at the field's crutch, and we don't use it. We are ~90% VQ2-compliant by construction; the one real upgrade is folding HIGHRES_IMU into the observation.***

---

## 1. VQ2 interface, as it actually is (Phase-2 restricted)

**Inputs the policy is allowed at competitive race time (Sim → Client):**
| Stream | Detail | Status in our stack |
|---|---|---|
| **Vision** | Forward FPV, **640×360 JPEG @ 30 Hz**, UDP **:5600**, chunked, 24-byte LE header `<IHHIIQ` | ✅ **Already parsed byte-for-byte** (`capture_official_frames.py:41`) |
| **HIGHRES_IMU** | gyro + accel (+ mag/baro), body frame, **body↔IMU = identity** | ⚠ **Not yet in obs — the upgrade** |
| HEARTBEAT / TIMESYNC | connection + `sim_time_ns` timing | glue |

**Outputs (Client → Sim):** `SET_ATTITUDE_TARGET` (our CTBR/attitude interface ✅) or `SET_POSITION_TARGET_LOCAL_NED` (awkward without position feedback — ignore).

**BLOCKED in Phase 2 (§9.3):** `ATTITUDE`, `LOCAL_POSITION_NED`, `ODOMETRY`, **and `GATE_INFO`** ← *the email omitted GATE_INFO.* Also deprecated (§4.5): attitude, orientation, linear velocities, system-status flags. **Net: in VQ2 the only things the sim tells us are pixels, IMU, and time.** That is the entire raw-sensor regime.

**Fixed facts that match us exactly:**
- Camera intrinsics: `cx,cy=[320,180]`, `fx,fy=[320,320]`, **20° up-tilt**, ~90° HFoV → **identical to our render model** (Mirror #32 vindicated; never re-derive).
- Gate inner square **1500×1500mm**, outer 2700, depth 260 (verify our sim's gate geometry matches).
- Physics 120 Hz; **command rate < 100 Hz**; vision 30 Hz; min heartbeat 2 Hz.
- Deploy box: **Windows 11, 8 GB VRAM, Python 3.14.2**, no Linux. (Training stays on WSL/CUDA; deploy is Windows-native — already our split.)
- Determinism: course geometry + physics + conditions identical for all; **gate appearance consistent across the track** (a *single* fixed look to match, not an open-ended distribution).
- VQ2 qualifies for the **Physical Qualifier, September**. Unlimited attempts; pure lap-time; team-best counts.

---

## 2. Why this is a tailwind, not a threat

- The blocked streams (`ATTITUDE/LOCAL_POSITION_NED/ODOMETRY`) are **ground-truth state** — the input that classical state-machine + ground-truth-PID stacks (the MAXIMUS/Northlake archetype) fly on. **We never fed any of it to the policy** (`sim/env.py:133`, `maneuver_env.py:118`: obs = `Box(IMG,IMG,3)`, image-only). The ground-truth `pos/vel/quat` in `dynamics.py` feeds only physics, reward, and the renderer — all training-side, in our own sim.
- **GATE_INFO blocked** forces every team to **detect gates from vision** instead of waypoint-following ground-truth gate coordinates. Our policy learned pixel→action toward gates inherently. This deletes another whole class of competitor.
- **Our world-model latent `h` already does implicit odometry** — lesion-verified (`integration/lesion_eval.py`, LC29: "the gate-passing was dead-reckoning"). The "state estimation / localization / VO" the spec orders teams to *go build*, Dreamer's RSSM does natively.
- They deleted the crutch; they kept the camera. Our entire Phase-3 investment (appearance robustness, segmentation, informed-Dreamer, control-rate) **is** the VQ2 skill set.

---

## 3. Gap analysis → ranked changes

**① ★ Add HIGHRES_IMU to the observation (the headline change).**
We are vision-*only*; the latent infers motion from frame-to-frame change alone. VQ2 hands us IMU explicitly. Fold gyro+accel (body frame; identity extrinsic, so no transform) into a multimodal obs so the RSSM does proper visual-**inertial** odometry — far more robust for attitude/scale/velocity, the exact quantities the blocked telemetry used to hand out.
  - Obs becomes `{image: Box(IMG,IMG,3), imu: Box(6..N)}`; DreamerV3 already supports dict obs (concat IMU vector into the deterministic/encoder path).
  - Train the world model to **predict the (training-only) privileged `ATTITUDE`/velocity from image+IMU history** via the existing `ANAKIN_PRIV` decoder head → the latent is forced to carry a real state estimate; at deploy we never read the API's ground truth.
  - Risk: low/additive. Cost: an obs-space change + a retrain. **Highest expected value.**

**② Control-rate decision (the cliff, now with real numbers).**
Vision = 30 Hz; command rate < 100 Hz; we trained at 50 Hz and a 30 Hz deploy fell off a cliff (LC47). VQ2 pins perception at 30 Hz. Options: (a) run the policy at 30 Hz (one action per frame) and **dt-condition** the policy so 30 Hz isn't OOD (the clean fix flagged Day-137 — needs a dt input the obs currently lacks); (b) hold the last latent and re-emit `SET_ATTITUDE_TARGET` at a higher inner rate (≤100 Hz) for a smoother stabilized command between frames. Likely **both**: 30 Hz perception + faster command re-emit, with dt-conditioning to kill the OOD.

**③ Harvest the official camera + IMU via Training Flights (a gift in §9.2).**
Free, non-scoring flights = a **legitimate** channel to record the official sim's real 5600 vision stream *and* HIGHRES_IMU, then retrain the appearance front-end and the IMU fusion on the true distribution. This is the clean dissolution of the appearance-OOD / holdout-confound mess we fought all Phase 3 — the official frames were biased/hard to get; now they're a button.

**④ Compliance hygiene (for the §9.2 code-audit clause).**
- Confirm no deploy *glue* reads `LOCAL_POSITION_NED`/`GATE_INFO` for race-start, gate-progress, or countdown. (Policy is clean; check the runner.) → swap any for vision/latent/`sim_time_ns` signals.
- **Competitive runs must be fully autonomous** (§7: human interaction mid-run = instant DQ). Our manual "PRESS RACE" + countdown-hold is *setup*; ensure the timed loop is hands-off after start.
- Document the **privileged-training / vision-deployment split** plainly (it's the published standard — Kaufmann & Scaramuzza, *Nature* 2023): train with ground-truth reward + the `ANAKIN_PRIV` head; deploy reads only pixels+IMU. We're clean by construction — make it legible so an audit passes on sight.

**⑤ 8 GB VRAM deploy ceiling.**
Inference must fit Windows + 8 GB. Reinforces that the Day-141 scale-up pause was right; size the model to the deploy box, not the training box.

---

## 4. Open questions to confirm
- Exact **HIGHRES_IMU** field set + rate (gyro/accel only, or mag+baro too? update rate?).
- VQ2 **deadline/date** (doc says only "qualifies for September physical"; memory cached "R2 cutoff ~end July" — confirm).
- Does our sim's **gate inner-square geometry = 1.5 m**? (track-validation "strict" in VQ2.)
- Track-validation rules (what counts as a valid gate pass / DQ).

---

## 5. Bottom line
We are not scrambling to meet VQ2; we are **already most of the way inside it**. The vision wire-format is implemented, the camera model matches to the pixel, the policy never touched the blocked telemetry, and the latent already estimates state. The single highest-value move is **IMU-into-obs + privileged-state distillation**, validated on **official data harvested through Training Flights**. They changed the rules toward the thing we built.
