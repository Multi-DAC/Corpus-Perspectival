# Drone CTBR Dynamics — UE5 (validated 2026-06-01)

Kinematic CTBR integrator matching our numpy `drone_env_v2` (keeps teacher↔student transfer valid).
Reference implementation: `scripts/drone_test.py` / `forward_flight_test.py` (`step(state, action, dt)`).
Ports directly to a C++ `ADronePawn::Step`.

## Constants (UE units: cm, s)
- `G = 981` cm/s²
- `TWR = 3.85` (our calibration) → `TMAX = TWR*G = 3777` cm/s² max thrust accel
- hover collective = `1/TWR = 0.26`
- `CD = 0.3` (linear drag, 1/s)

## State / Action
- state = pos(3), vel(3), quat(4, wxyz)
- action = `collective`[0..1], `wx,wy,wz` (body rates, rad/s) — ACRO/rate-controlled
- integrate: orientation by body rates (quat); thrust = `collective*TMAX` along body +Z, rotated to
  world; `accel = thrust_world + (0,0,-G) - CD*vel`; semi-implicit Euler.

## VALIDATED control convention (UE: left-handed, Z-up, X-forward, Y-right)
Each axis tested in isolation (file-output method — camera-framing-independent):

| input          | result                | clean? |
|----------------|-----------------------|--------|
| collective ↑   | **+Z (up)**           | climb accel = collective·TMAX − G ✓ |
| pitch `wy > 0` | **+X (forward)**      | dX=+753, dY=0 ✓ |
| roll  `wx > 0` | **−Y (left)**         | dY=−753, dX=0 ✓ |
| yaw   `wz > 0` | **+heading (CCW)**    | +115° for wz=2 rad/s·1s ✓ |

**This is THE control spec.** The policy's action vector must map to these signs, or flight inverts
(the exact class of bug that wrecked the first competition flight — see vq1_pilot/CALIB_FIT). Wire the
C++ pawn AND any deploy adapter to this table.

## Open / next
- Cross-check these signs against the *competition sim's* `set_attitude_target` convention before
  deploy (our UE convention is internally consistent; the comp sim had its own inversion — keep the
  two mappings explicit and separate).
- Port `step()` → C++ `ADronePawn` (fixed-timestep, for the socket bridge).
- Add a real rate-controller (P-loop) if we want imperfect-tracking realism; current model is
  perfect-rate-tracking (good enough for v1, matches ACRO assumption).
