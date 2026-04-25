# MAVSDK Client — Gap Analysis (Day 84, 2026-04-25)

Source: read of `vision/mavsdk_client.py` (474 lines) against the actual VQ1 spec
(VADR-TS-001 Issue 00.01, 2026-03-09) and the training stack
(`sim/infinite_gate_env.py`, `sim/drone_env_v2.py`, `rl/train_ppo.py`).

The client was authored before the official spec landed and against the
leaked Northlake `DCLAgent.compute_action(telemetry)` API. Issue 00.01
reveals the actual interface is MAVLink v2 over UDP via MAVSDK, so the
broad shape of `mavsdk_client.py` is on the right line. These are the
specific gaps to close before plugging it into a SITL loop.

## Severity scale

- **CRITICAL** — silently wrong; will produce incorrect commands or telemetry.
- **HIGH** — will fail to fly (won't arm, won't enter offboard, won't reach health).
- **MEDIUM** — works but fragile (timing, reconnect, race conditions).
- **LOW** — cosmetic / readability / future-friendliness.

## The 9 gaps

| # | Gap | Severity | Note |
|---|-----|----------|------|
| **G1** | Offboard pre-stream insufficient. `_async_start_offboard` sends a single zero-rate setpoint then calls `offboard.start()`. PX4 typically requires a *stream* of setpoints (≥2 Hz, recommended ≥10 Hz) to be already flowing before it accepts the offboard mode change. A single message is fragile and timing-dependent. | HIGH | Spawn a background pre-stream task that pushes 50 Hz setpoints for ~500 ms before `offboard.start()` returns. |
| **G2** | No `init_flight()` orchestration. `connect → wait_for_health → arm → start_offboard` is left to the caller. Each step has its own timeout and failure mode; getting them right is exactly the integration risk we want to eliminate. | HIGH | Add `init_flight(timeout=30)` that wraps the four-step sequence with proper error reporting. |
| **G3** | Frame conventions assumed but never asserted. `ned_to_zup_position`, `ned_to_zup_quaternion`, `zup_to_ned_rates` encode FLU↔FRD with shared body-x axis. The sim is verified z-up (`g_world = [0,0,-9.81]` in `train_ppo.py:165`); MAVSDK is verified NED. The mapping is mathematically consistent, but there is no test guarding against accidental edits. | CRITICAL (latent) | Write asserting tests in `vision/tests/test_frame_conversion.py`. **Done in G3+G4 sub-sprint below.** |
| **G4** | Action rate scaling assumed. `MAX_RATE_XY=15.0`, `MAX_RATE_Z=0.3` are pasted constants. Verified against `QuadParams` (`sim/drone_env_v2.py:74-75`): `omega_max_xy=15.0`, `omega_max_z=0.3`. Match. | CRITICAL (latent) | Test that imports `QuadParams` and asserts equality, so a future training-side change can't silently desync. |
| **G5** | Thrust mapping is conceptually different. Training maps `action[0]∈[-1,1] → collective thrust ∈ [0, 4·T_max] N` (sum of all motors). Client maps `action[0]∈[-1,1] → thrust ∈ [0,1]` (PX4 normalized fraction). PX4's "1.0" is the autopilot's max collective; whether that equals the sim's `4·T_max` depends on PX4 vehicle config. If PX4 max collective ≠ sim max collective, the policy's thrust commands will saturate or undershoot. | HIGH | Tunable scale factor `THRUST_SCALE` (default 1.0); calibrate at SITL bring-up by hovering. |
| **G6** | `start_offboard()` doesn't verify mode actually engaged. PX4 may reject the mode change silently if the pre-stream lapses; the only signal is the `OffboardError`. Useful to read back the flight mode and assert. | MEDIUM | Add post-start mode check via `telemetry.flight_mode()`. |
| **G7** | No reconnect / restart path. If the UDP link drops mid-run, the loop has no way to recover. Spec §4.4 requires ≥2 Hz heartbeat; transient packet loss is realistic. | MEDIUM | Add heartbeat watchdog + auto-restart of offboard on reconnect. |
| **G8** | Cosmetic: line 197 (`get_telemetry`) uses `ned_to_zup_position` for **velocity** as well as position. The math is identical (component-wise sign flip) but the function name is misleading. | LOW | Rename to `ned_to_zup_vec3` or add a thin `ned_to_zup_velocity` alias. |
| **G9** | Hard-coded `system_address="udp://:14540"`. Spec §4.1/§4.2 doesn't fix the port; competition harness may hand us a different one. | LOW | Accept env var override (`AIGP_MAVLINK_URL`); keep 14540 as default. |

## Sub-sprint ordering

Tackle as one Week-1 sub-sprint:

1. **G3 + G4 first** (verification work, ~1 hour) — read the training side, write asserting tests. Pure read-the-other-side-of-the-loop work; surfaces any sign error or constant drift before we invest in orchestration. **(In progress, this session.)**
2. **G1 + G2** (orchestration, ~2 hours) — once conventions are confirmed, build `init_flight()` with proper setpoint pre-streaming.
3. **G5** (thrust calibration) — needs SITL running; can't be unit-tested.
4. **G6 + G7** (robustness) — defer until first end-to-end SITL hover works.
5. **G8 + G9** (cosmetic) — bundle into a polish pass.

## G3 + G4 verification — findings (this sub-sprint)

### G3 — Frame conventions

- Training world frame: **z-up** (verified at `train_ppo.py:165`, `drone_env_v2.py:116`: `g_world = [0, 0, -9.81]`).
- Training body frame: **FLU** (Forward-Left-Up). Body z is the thrust axis (`drone_env_v2.py:122`: `thrust_body = [0, 0, total_thrust/m]`).
- MAVLink world frame: **NED** (North-East-Down). MAVLink body frame: **FRD** (Forward-Right-Down).
- Mapping `[N, -E, -D]` is consistent for FLU↔FRD with **body-x shared as forward**.
- Quaternion `[w, x, -y, -z]` is consistent (negate the y,z components — the two axes that flip between FLU and FRD).
- Body rate mapping `[wx, -wy, -wz]` is consistent (rates about y and z axes flip sign with the axis direction).

**Verdict: G3 PASS for static analysis.** Behavioral verification (PX4 SITL + policy) still required — that's the integration sprint, not this verification.

### G4 — Action rate scaling

- `omega_max_xy = 15.0 rad/s` (`drone_env_v2.py:74`) **matches** `MAX_RATE_XY = 15.0` in `mavsdk_client.py:302`.
- `omega_max_z = 0.3 rad/s` (`drone_env_v2.py:75`) **matches** `MAX_RATE_Z = 0.3` in `mavsdk_client.py:303`.
- Conversion to deg/s for MAVSDK (`AttitudeRate` expects deg/s): correct (`* RAD2DEG`).

**Verdict: G4 PASS.** Test now codified.

## What this sub-sprint does NOT cover

- **G5 thrust scale** — needs SITL to calibrate (can't unit-test the autopilot's max collective).
- Behavioral verification of the policy under PX4 dynamics — that's the next sprint.
- Vision stream — blocked on the separate spec promised in §4.6.
