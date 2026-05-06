# VADR-TS-001 Issue 00.01 — Key Facts Extract

Source: official AI Grand Prix Virtual Qualifier Technical Specification, Issue 00.01, dated 2026-03-09. Provided by Clayton 2026-04-25 Day 84 late afternoon (PDF in same directory).

## Facts that REWRITE prior assumptions

### F1 — MAVLink v2 over UDP via MAVSDK is the actual interface
Northlake's leaked `DCLAgent.compute_action(telemetry)` spec does NOT match this Issue 00.01. The actual interface is **MAVLink v2 over UDP via MAVSDK-compatible interfaces** (§4.1, §4.2). The simulator runs SITL-style; client connects via UDP bridge.

Implication: Our existing `vision/mavsdk_client.py` is on the right line. Northlake's leaked spec was either an earlier draft or an internal Anduril-side wrapper, not the team-facing interface.

### F2 — Local NED position IS available (only GPS is withheld)
§3.3 says "No geographic coordinates are provided. GPS simulation is not available and absolute global position is not exposed." But §4.3 lists `SET_POSITION_TARGET_LOCAL_NED` (Client → Simulator) and `ODOMETRY` in the message table, plus §4.5 telemetry includes "simulator navigation reference data." 

Reading: **local Cartesian NED position IS supplied** via ODOMETRY; only GPS coordinates are withheld. The FAQ's "fly without coordinate/position data" was sloppy phrasing or referred to absolute geographic frame.

Implication: **Workstream B3 (position-less observation variant) drops from "highest-risk concentration" to "low priority / verify needed."** Our existing state-based observation stack with position should transfer with frame conversion (NED ↔ our internal frame).

### F3 — Round One is COMPLETION, not time-trial
§8.1: "Round One verifies that contestant software can successfully navigate the racecourse." 

The FAQ's "fastest valid times advances" applies across qualifying rounds in aggregate; **Round One specifically is pass/fail navigation**. Completion *is* the criterion, not speed. v2's "time-trial in BOTH VQs" patch was wrong for Round One — speed is a Round Two concern.

Re-elevates v1's framing partially: completion-first for Round One; speed-after-completion for Round Two.

### F4 — Environment is fully DETERMINISTIC
§3.5: "course geometry is identical for all participants, physics parameters are identical, environmental conditions are deterministic." Plus §3.1: "Gates will be visually distinctive to the environment, but consistent throughout the Virtual Qualifier 1 track."

Implication: For Round One, **overfitting to the specific course is a viable strategy**. Domain randomization for *gate appearance* loses urgency for VQ1 (gates are consistent). Course-specific waypoint generation is competitive. Workstream A2 scope shrinks further.

### F5 — Run window is 8 minutes, not 120 seconds
§8.3: Maximum run duration 8 minutes. Northlake's leaked 120s/heat was wrong (or applied to different round).

Implication: training episode lengths can match real run window. No need to compress strategy into 2-minute heats.

## Other concrete facts

| Item | Value |
|---|---|
| Physics rate | 120 Hz |
| Recommended command rate | 50–120 Hz |
| Min heartbeat rate | 2 Hz |
| Python version | 3.14.2 known to operate (others allowed) |
| Transport | UDP |
| Control messages | `SET_POSITION_TARGET_LOCAL_NED`, `SET_ATTITUDE_TARGET` (Client → Sim) |
| Sim → Client messages | `HEARTBEAT`, `ATTITUDE`, `HIGHRES_IMU`, `ODOMETRY`, `TIMESYNC` |
| Vision stream spec | "Provided in a separate specification" — TBD, blocked |
| Course elements | Start gate, sequential race gates, finish gate, vertical/horizontal obstacles, boundary elements, terrain |
| Scope of Issue 00.01 | Round One only; Round Two not detailed |

## What's still unknown

- Vision stream parameters (resolution, encoding, framerate, FOV) — separate spec
- Round Two course design and scoring rules
- Submission packaging spec (zip format, size limit, libraries) — Northlake's leaked details may or may not apply
- Whether `SET_POSITION_TARGET_LOCAL_NED` is preferred or whether `SET_ATTITUDE_TARGET` is expected for racing (both supported but choice has implications)
- ODOMETRY direction / contents detail (assumed Sim → Client; assumed includes pos+vel+attitude)
- Specific drone model (Neros — which Archer variant?)
- Onboard compute exposure in sim vs physical (sim presumably uncapped; physical ~100 TOPS)

## Author

Document author: "KH" (initials only). First release.
