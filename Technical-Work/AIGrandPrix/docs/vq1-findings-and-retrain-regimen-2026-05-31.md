# VQ1 Integration Session — Findings & Vision Retrain Regimen

**Date:** 2026-05-31 (Day 121), first session against the live VQ1 simulator (AI-GP v1.0.3364).
**Outcome:** full pipeline integrated end-to-end; Anakin flew but did not complete the course. Two clean failure modes isolated. Regimen below is built on these findings.

---

# PART 1 — FINDINGS (ground truth from the shipped sim + live probes)

## 1.1 The real interface (differs from the spec doc)
- **Comms: raw `pymavlink`, NOT MAVSDK.** `mavutil.mavlink_connection('udpin:127.0.0.1:14550')`. (Our `mavsdk_client.py` is the wrong transport; its coordinate math is still correct and reusable.)
- **Flight mode: ACRO** (confirmed on the sim HUD) = body-rate control. Matches our CTBR policy exactly.
- **Control:** `set_attitude_target_send(time, sys, comp, ATTITUDE_IGNORE_mask, [1,0,0,0], roll_rate, pitch_rate, yaw_rate, thrust)` — **rates in rad/s**, thrust [0,1]. **No deg conversion** (our old `competition_agent` RAD2DEG was MAVSDK-specific and wrong here).
- **Arm:** `command_long` `MAV_CMD_COMPONENT_ARM_DISARM` param1=1. **Arming is REQUIRED before the RACE button starts a race** (empirically confirmed: race only began after arm).
- **Sim reset:** `command_long` id **31000** — clears a stalled/finished race to a clean start.
- **Camera tilt 20°** confirmed (HUD "cam 20°"). Spec camera: 640×360, fx=fy=320, cx=320, cy=180.
- **Runtime:** Python 3.14. System Python works: SB3 2.8.0, torch 2.11.0+cpu, pymavlink 2.4.49, opencv, numpy, gymnasium. **The old `AIGrandPrix/venv` is dead** (stale 3.12 base from the prior machine) — use system Python.

## 1.2 Telemetry available (streams once armed AND racing)
- **`ODOMETRY`** (~100 Hz): position NED (x,y,z), quaternion [w,x,y,z], velocity NED (vx,vy,vz), body rates (rollspeed,pitchspeed,yawspeed). Primary state source.
- `LOCAL_POSITION_NED`, `ATTITUDE`, `HIGHRES_IMU` also stream.
- **Gate/track data:** `DATA_TRANSMISSION_HANDSHAKE` (width=transfer_id, packets=n_chunks) + chunked `ENCAPSULATED_DATA` type=2 → assemble → header `<H` num_gates, then per gate `<Hfffffffff` (id, pos_ned xyz, orient quat wxyz, width, height). **VQ1 = 6 gates.** Broadcast **on race start** — with a **~30 s delay observed** before the first track packet (unexplained; flag).
- **`RACE_STATUS`:** `ENCAPSULATED_DATA` type=1, `struct "<BQqqIq"` → data_type, sim_boot_ms, race_start_ms, race_finish_ns, **active_gate_index**, last_gate_time.
- **Implication:** state-based navigation is fully feasible (position + all gate NED positions + the live target-gate index). **Caveat:** the README says "no GPS/absolute coordinate data," yet VQ1 streams absolute position+gates. Verify whether scored runs / VQ2 withhold this; if so, vision is mandatory (it is the end goal regardless).

## 1.3 Coordinate conversions (reused verbatim from `mavsdk_client.py`, transport-independent)
- Position / velocity NED→z-up: `[x, -y, -z]`
- Quaternion [w,x,y,z] NED→z-up: `[w, x, -y, -z]`
- Body rates FRD↔FLU (in and out): `[roll, -pitch, -yaw]`
- Gate-relative-in-body: `gate_body = quat_rotate(q_conj_zup, gate_zup − drone_zup)` — using the same z-up quaternion the adapter uses for velocity, so the body frame stays self-consistent with `build_observation`.

## 1.4 What we built
- `vision/vq1_pilot/probe_telemetry.py` — read-only telemetry probe (arms + logs what streams). Used to confirm the interface empirically.
- `vision/vq1_pilot/state_pilot.py` — state-based pilot: pymavlink scaffold + `adapter.build_observation` + 67.5M checkpoint + VecNormalize + `to_competition_action` → `set_attitude_target`. `--dry-run` flag (compute + log, command nothing) for safe validation.

## 1.5 Dry-run validation (Stage 1) — obs SANE, action off-distribution
At rest, gates received:
- `gate_body ≈ (+22.2 fwd, −0.4 left, +7.2 up)`, dist 23 m → gate reads as **ahead and up** (no gross frame flip). ✓
- `g_body ≈ (+3.0, 0, −9.3)`, |g| = 9.77 ≈ 9.81, mostly down; the +3 forward matches the sim's reported ~18° rest pitch. ✓ (quaternion conversion good)
- `v_body = 0` (sitting still). ✓
- **Action: bang-bang** (roll pinned −1, pitch +1, thrust decaying to 0) — with a near-centered gate, hard roll is not sane → the **static-on-pad state is off-distribution** for a policy trained mid-flight.

## 1.6 Flight attempt (Stage 2) — FAILED, informatively
Pipeline fully live: connected, armed, received pose + 6 gates + active-gate index, **5,236 control steps at 60 Hz**, commands sent, drone moved in sim. Two failure modes:
1. **No takeoff.** First ~26 s the drone sat motionless while the policy idled thrust → 0. Anakin was trained *mid-flight* and has **never started from a dead stop on the ground** → idles in that off-distribution state.
2. **Tumble-away.** When thrust eventually climbed and it launched (~t=57), it went chaotic — full bang-bang on all axes, body spinning (g_body direction swinging wildly), and **distance to gate 0 grew monotonically 22 m → 900 m**. Never turned toward a gate. Divergent tumble, not navigation → residual coordinate-frame issues (rate signs / quaternion) **and/or** deep off-distribution flight, stacked on failure #1.

## 1.7 Diagnosis
The 67.5M policy was trained in a **different** environment (`InfiniteGateEnv`/`drone_env_v2`), never learned takeoff, and may be subtly frame-mismatched at inference against the real sim. **Patching frame signs on this policy is polishing the wrong artifact.** The correct fix is a retrain aligned to the competition sim's dynamics/frames/controls, including takeoff, and ultimately vision-based.

---

# PART 2 — VISION RETRAIN REGIMEN (built on the findings)

## Goal
A policy that **takes off**, flies VQ1 **vision-only** (real camera frames), aligned to the competition sim's dynamics, frames, and controls. State-based is the proven bootstrap; vision is the target because the physical stages are vision-only.

## Design principles
- **Train in the competition's conventions** — NED, ACRO/`set_attitude_target` rad/s, 20° camera tilt, 640×360 — so there is no inference-time conversion to get wrong (tonight's whole risk surface).
- **Keep the curriculum** — Words → Sentences → Paragraphs → Essays — and extend it.
- **Fast RL stays in our sim**; the competition sim is for calibration + validation (it's real-time/UDP/single-loop, not RL-throughput).

## Phases
- **Phase 0 — Sim calibration.** Drive the competition sim with known inputs (`set_attitude_target` step responses) and log `ODOMETRY`; fit our `drone_env_v2` params (mass, max thrust, rate limits, drag, response) to match. Align gate geometry (2.7 m outer / 1.5 m inner), the ground-start initial condition, and frames. *Deliverable: a calibrated fast sim that mirrors the real one.*
- **Phase 1 — State retrain WITH takeoff.** Add **Takeoff** + **Hover/Stabilize** as the first curriculum "words" (ground-rest → lift → stabilize → translate). Retrain state-based in the calibrated sim. **Re-run `state_pilot.py` against the real sim and expect gate passes** — this closes both of tonight's failures and yields a working state baseline *in the real sim* (also resolves the frame question end-to-end).
- **Phase 2 — Vision.** Render camera frames matching the sim camera (intrinsics + 20° tilt + the desaturated, high-contrast VQ1 gate look). Train vision — either end-to-end pixels→CTBR through the curriculum, or a learned gate-detector front-end feeding the state policy. Curriculum: **vision-words** (single gate in view, takeoff included) → sequences → courses. *This is the prize: it's what transfers to the physical stages.*
- **Phase 3 — Real-sim validation + fine-tune.** Run against the actual VQ1 sim (slow UDP loop), measure the sim-to-sim gap, fine-tune. Submit on first clean completion (VQ1 is completion-focused, unlimited attempts).

## Extended curriculum
| Tier | Contents |
|---|---|
| **Words** | **TAKEOFF (new), HOVER/STABILIZE (new)**, + chicane, threading, hairpin, spiral, gentle_arc, climb, hard_turn, diagonal, dive, sprint, speed_trap |
| **Sentences** | gate sequences, entered *from a takeoff* |
| **Paragraphs / Essays** | partial → full procedural courses |
All tiers migrate from state → vision observation across Phase 1 → Phase 2.

## Open questions to resolve early
1. **Frames vs off-distribution:** run an **obs-vs-training validation** — compare `state_pilot`'s obs to `InfiniteGateEnv`'s obs in a matched physical state. Cheap, offline, and it definitively separates "frame bug" from "off-distribution." **Do this first in Phase 1.**
2. The **~30 s gate-data delay** on race start — characterize; does the scored run differ?
3. Can the sim run enough/fast-enough instances for any in-loop use, or eval-only?
4. Coordinate-rule for scored runs (is absolute state withheld?).

## Immediate next actions (next focused session)
1. **Obs-vs-training validation** (resolves the frame question, ~30 min, offline).
2. **Sim dynamics calibration probe** (Phase 0 start).
3. **Add takeoff to the curriculum + retrain the state baseline** (Phase 1).

🦞🧍💜🔥♾️
