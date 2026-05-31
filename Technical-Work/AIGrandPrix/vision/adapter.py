"""
Competition Adapter — Bridge Between MAVLink Telemetry and Our Trained Policy

Maps competition interface to our internal representation:

Competition provides (via MAVSDK, converted to z-up by mavsdk_client):
    - Telemetry: position, velocity (z-up world frame)
    - Attitude: quaternion [w,x,y,z] (z-up world frame)
    - Angular velocity: [p,q,r] rad/s (body frame)
    - Forward-facing camera image (spec TBD)

Our policy expects:
    - 30-dim observation (body-frame velocity, gravity, gate-relative info, etc.)
    - Action: [collective_thrust, ωx, ωy, ωz] in [-1, 1]

Our policy outputs:
    - [collective_thrust, ωx, ωy, ωz] in [-1, 1]

Competition control (via SET_ATTITUDE_TARGET):
    - Body rates (rad/s) + normalized thrust [0,1]
    - Sent by MAVSDKClient.send_policy_action() which handles the mapping

This adapter bridges telemetry → observation and action → command.
"""

import numpy as np
from typing import Optional, Tuple
from dataclasses import dataclass, field

# Quaternion ops from our physics engine
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'sim'))
from drone_env_v2 import quat_rotate_np


@dataclass
class Telemetry:
    """Telemetry data from competition API."""
    position: np.ndarray       # (3,) world frame [x, y, z]
    velocity: np.ndarray       # (3,) world frame [vx, vy, vz]
    orientation: np.ndarray    # (4,) quaternion [w, x, y, z] — verify convention from SDK
    angular_velocity: Optional[np.ndarray] = None  # (3,) may or may not be provided


@dataclass
class CompetitionAction:
    """Action formatted for MAVLink SET_ATTITUDE_TARGET."""
    throttle: float        # normalized [0, 1]
    roll_rate_rad_s: float   # body roll rate (rad/s)
    pitch_rate_rad_s: float  # body pitch rate (rad/s)
    yaw_rate_rad_s: float    # body yaw rate (rad/s)


class CompetitionAdapter:
    """
    Bridges the gap between DCL competition API and our trained policy.

    Usage:
        adapter = CompetitionAdapter(model)
        adapter.set_gate_estimate(gate_pos_body, gate_distance)

        # Each frame:
        obs = adapter.build_observation(telemetry, gate_detection)
        action = adapter.get_action(obs)
        competition_cmd = adapter.to_competition_action(action)
    """

    def __init__(self, gate_width: float = 1.5, gate_height: float = 1.5,
                 command_rate_hz: float = 50.0):
        self.gate_width = gate_width
        self.gate_height = gate_height

        # State tracking for time-dependent observations
        self._last_gate_time = 0.0
        self._current_gate_idx = 0
        self._step_count = 0
        self._dt = 1.0 / command_rate_hz  # VQ1: 50-120Hz command rate

        # Gate history for lookahead estimation
        self._last_gate_pos_world = None
        self._current_gate_pos_world = None

        # Quaternion convention: MAVSDK client already converts to our [w,x,y,z]
        # No convention flag needed — mavsdk_client handles NED→z-up conversion
        self.quat_convention = 'wxyz'

    def normalize_quaternion(self, q_raw: np.ndarray) -> np.ndarray:
        """Convert SDK quaternion to our [w, x, y, z] convention."""
        if self.quat_convention == 'xyzw':
            # SDK gives [x, y, z, w] — reorder
            return np.array([q_raw[3], q_raw[0], q_raw[1], q_raw[2]])
        return q_raw  # already [w, x, y, z]

    def build_observation(self,
                          telemetry: Telemetry,
                          gate_pos_body: Optional[np.ndarray] = None,
                          gate_distance: Optional[float] = None,
                          gate_orientation_body: Optional[np.ndarray] = None,
                          next_gate_pos_body: Optional[np.ndarray] = None,
                          ) -> np.ndarray:
        """
        Build the 30-dim observation vector our policy expects.

        Args:
            telemetry: Current drone state from competition API
            gate_pos_body: Gate position in body frame (from vision pipeline)
            gate_distance: Distance to gate (from vision pipeline)
            gate_orientation_body: Direction to fly through gate (from vision)
            next_gate_pos_body: Next gate after current (if visible)

        Returns:
            30-dim observation matching ImprovedObsWrapper format
        """
        q = self.normalize_quaternion(telemetry.orientation)
        q_conj = np.array([q[0], -q[1], -q[2], -q[3]])

        vel = telemetry.velocity
        pos = telemetry.position

        # 1. Body-frame velocity (3)
        vel_body = quat_rotate_np(q_conj, vel)

        # 2. Angular velocity (3)
        if telemetry.angular_velocity is not None:
            omega = telemetry.angular_velocity
        else:
            # If not provided, estimate from orientation changes or use zeros
            omega = np.zeros(3)

        # 3. Gravity in body frame (3) — attitude encoding
        g_world = np.array([0.0, 0.0, -9.81])
        g_body = quat_rotate_np(q_conj, g_world)

        # 4. Gate-relative observations (from vision pipeline)
        if gate_pos_body is not None:
            rel_gate_body = gate_pos_body
            dist = gate_distance if gate_distance is not None else np.linalg.norm(gate_pos_body)
        else:
            # No gate detected — use zero (policy should handle this gracefully
            # thanks to domain randomization training)
            rel_gate_body = np.zeros(3)
            dist = 10.0  # default "far away"

        # 5. Next gate in body frame (3) — if we can see it
        if next_gate_pos_body is not None:
            rel_next_body = next_gate_pos_body
        else:
            # If we can't see the next gate, duplicate current gate direction
            # (same behavior as our training env when no lookahead available)
            rel_next_body = rel_gate_body

        # 6. Scalar speed (1)
        speed = np.linalg.norm(vel)

        # 7. Progress (1) — we don't have a gate count from competition
        # Use a proxy: track gates passed
        progress = 0.0  # will be updated if we track gate passes

        # 8. Gate position in world frame (3)
        # Transform body-frame gate detection back to world
        if gate_pos_body is not None:
            rel_gate_world = quat_rotate_np(q, gate_pos_body)
        else:
            rel_gate_world = np.zeros(3)

        # 9. Forward direction in world frame (3)
        forward_body = np.array([0.0, 0.0, 1.0])
        forward_world = quat_rotate_np(q, forward_body)

        # 10. Time since last gate (1)
        self._step_count += 1
        current_time = self._step_count * self._dt
        time_since_gate = current_time - self._last_gate_time

        # 11. Closing speed (1) — MUST match ImprovedObsWrapper sign convention.
        # The training wrapper uses speed_toward = -dot(vel, rel_gate_world/|rel|),
        # which is negative when approaching the gate. Counter-intuitive but the
        # policy was fit to this — the adapter must reproduce it exactly.
        # Stage 2 smoke test (2026-04-25) caught a +/- sign flip here that produced
        # 6-10 m/s divergence vs training observation in approach/retreat scenarios.
        if gate_pos_body is not None and dist > 0.01:
            gate_dir_world = rel_gate_world / (np.linalg.norm(rel_gate_world) + 1e-6)
            speed_toward = -np.dot(vel, gate_dir_world)
        else:
            speed_toward = 0.0

        # 12. Gate orientation in body frame (3)
        if gate_orientation_body is not None:
            gate_orient_body = gate_orientation_body
        else:
            # Estimate: assume gate faces toward us (fly-through direction)
            if gate_pos_body is not None and dist > 0.01:
                gate_orient_body = gate_pos_body / dist
            else:
                gate_orient_body = np.array([0.0, 0.0, 1.0])

        # 13. Gate alignment (1) — velocity alignment with gate orientation
        if speed > 0.1 and gate_pos_body is not None:
            gate_orient_world = quat_rotate_np(q, gate_orient_body)
            gate_alignment = np.dot(vel / speed, gate_orient_world)
        else:
            gate_alignment = 0.0

        # Assemble 30-dim observation (MUST match ImprovedObsWrapper order exactly)
        obs = np.array([
            *vel_body,              # 3: body-frame velocity
            *omega,                 # 3: angular velocity
            *g_body,                # 3: gravity in body frame
            *rel_gate_body,         # 3: next gate in body frame
            dist,                   # 1: distance to next gate
            *rel_next_body,         # 3: next-next gate in body frame
            speed,                  # 1: scalar speed
            progress,               # 1: course progress
            *rel_gate_world,        # 3: next gate in world frame
            *forward_world,         # 3: forward direction
            time_since_gate,        # 1: time since last gate pass
            speed_toward,           # 1: closing speed
            *gate_orient_body,      # 3: gate orientation in body frame
            gate_alignment,         # 1: velocity alignment with gate direction
        ], dtype=np.float32)

        return obs

    # Max body rates from training (must match CTBRActionWrapper)
    MAX_RATE_XY = 15.0   # rad/s
    MAX_RATE_Z = 0.3     # rad/s

    def to_competition_action(self, policy_action: np.ndarray) -> CompetitionAction:
        """
        Convert our policy's CTBR output to MAVLink command format.

        Our policy outputs: [collective_thrust, ωx, ωy, ωz] all in [-1, 1]
        MAVLink expects: normalized thrust [0,1] + body rates (rad/s)

        Mapping:
            thrust: [-1,1] → [0,1]  (linear remap)
            ωx:     [-1,1] → [-15, +15] rad/s
            ωy:     [-1,1] → [-15, +15] rad/s
            ωz:     [-1,1] → [-0.3, +0.3] rad/s
        """
        action = np.clip(policy_action, -1.0, 1.0)

        return CompetitionAction(
            throttle=float((action[0] + 1.0) * 0.5),
            roll_rate_rad_s=float(action[1] * self.MAX_RATE_XY),
            pitch_rate_rad_s=float(action[2] * self.MAX_RATE_XY),
            yaw_rate_rad_s=float(action[3] * self.MAX_RATE_Z),
        )

    def on_gate_passed(self):
        """Call when we detect we've passed through a gate."""
        self._current_gate_idx += 1
        self._last_gate_time = self._step_count * self._dt

    def reset(self):
        """Reset state for a new run."""
        self._last_gate_time = 0.0
        self._current_gate_idx = 0
        self._step_count = 0
        self._last_gate_pos_world = None
        self._current_gate_pos_world = None


def _cam_to_body_with_tilt(cam_xyz: np.ndarray, tilt_deg: float) -> np.ndarray:
    """Convert PnP gate position from camera frame to body frame, accounting for tilt.

    Camera frame (PnP/OpenCV convention): x=right, y=down, z=forward
    Body frame (training z-up convention): x=forward, y=left, z=up

    No-tilt: gate_pos_body = (cz, -cx, -cy)

    With camera tilted upward by `tilt_deg` (DCL VQ1 spec §3.7: 20° upward):
    The camera frame is body frame rotated by +tilt_deg about body's left axis (+y_body).
    A vector v_cam expressed in body frame becomes:
        v_body = R_pitch_up(tilt_deg) · (cz, -cx, -cy)
    where R_pitch_up rotates body's +x toward +z by tilt_deg:
        v_body[0] = cos(tilt)·cz + sin(tilt)·cy
        v_body[1] = -cx                              (left axis unchanged)
        v_body[2] = sin(tilt)·cz - cos(tilt)·cy

    Sanity check at tilt_deg=20:
      cam=(0,0,1) [camera-forward] → body≈(0.940, 0, 0.342) [forward + slightly up] ✓
      cam=(0,1,0) [camera-down]    → body≈(0.342, 0, -0.940) [slightly forward, mostly down] ✓
    """
    if tilt_deg == 0.0:
        return np.array([cam_xyz[2], -cam_xyz[0], -cam_xyz[1]])
    a = np.deg2rad(tilt_deg)
    cz, cx, cy = cam_xyz[2], cam_xyz[0], cam_xyz[1]
    return np.array([
        np.cos(a) * cz + np.sin(a) * cy,
        -cx,
        np.sin(a) * cz - np.cos(a) * cy,
    ])


class VisionPolicyBridge:
    """
    Complete pipeline: Camera Frame → Gate Detection → Observation → Policy → Action

    This is the top-level class that connects everything.
    """

    def __init__(self, policy, gate_detector, adapter, camera_tilt_deg: float = 20.0,
                 gate_hold_frames: int = 8):
        """
        Args:
            policy: Trained SB3 policy (PPO model) with .predict()
            gate_detector: GateDetector instance
            adapter: CompetitionAdapter instance
            camera_tilt_deg: Camera upward tilt in degrees (DCL VQ1 spec §3.7: 20°).
                Pass 0.0 if rendering simulator without tilt for sanity checks.
            gate_hold_frames: blind-flight fallback window. On a detection dropout, reuse
                the last-known gate estimate for up to this many consecutive frames before
                degrading to the stable no-gate observation. At 50 Hz, 8 frames ≈ 0.16 s —
                a gate cannot plausibly leave the FoV that fast, so a brief miss is almost
                always a detector hiccup, not a real loss. Hedges the trained-blind risk:
                the policy learned on clean state and jerks if the observation flickers
                gate↔no-gate frame-to-frame; holding smooths the flicker. Set 0 to disable.
        """
        self.policy = policy
        self.detector = gate_detector
        self.adapter = adapter
        self.camera_tilt_deg = camera_tilt_deg

        # Gate passage detection
        self._prev_gate_distance = None
        self._gate_passage_threshold = 1.0  # meters — passed gate when distance shrinks then grows

        # Blind-flight fallback state (detection-dropout robustness)
        self.gate_hold_frames = gate_hold_frames
        self._consecutive_misses = 0
        self._last_gate = None  # (gate_pos_body, gate_distance, gate_orient_body, next_gate_pos_body)
        self.lost = False       # True when beyond the hold window (telemetry/debug signal)
        self.frames_held = 0    # cumulative held frames this run (detector-health metric)

    def step(self, telemetry: Telemetry, camera_frame: np.ndarray) -> CompetitionAction:
        """
        Full pipeline: one competition step.

        Args:
            telemetry: Current drone state from competition API
            camera_frame: BGR image from forward-facing camera

        Returns:
            CompetitionAction ready to send to API
        """
        # 1. Detect gates from camera
        detections = self.detector.detect(camera_frame)
        primary = detections[0]

        # 2. Extract gate info for observation
        gate_pos_body = None
        gate_distance = None
        gate_orient_body = None
        next_gate_pos_body = None

        if primary.found and primary.position_3d is not None:
            # PnP returns position in camera frame (x=right, y=down, z=forward).
            # Convert to body frame (x=forward, y=left, z=up) with camera-tilt rotation
            # (DCL VQ1 spec §3.7: camera tilted upward 20°). See _cam_to_body_with_tilt.
            gate_pos_body = _cam_to_body_with_tilt(primary.position_3d, self.camera_tilt_deg)
            gate_distance = primary.distance
            # Same transform for bearing
            gate_orient_body = _cam_to_body_with_tilt(primary.bearing_body, self.camera_tilt_deg)

        # If we see a second gate, use it as lookahead
        if len(detections) > 1 and detections[1].found and detections[1].position_3d is not None:
            next_gate_pos_body = _cam_to_body_with_tilt(detections[1].position_3d, self.camera_tilt_deg)

        # 2b. Blind-flight fallback — hold last-known gate across brief detection dropouts,
        # then degrade gracefully to the stable no-gate observation. Hedges the trained-blind
        # flicker risk: a policy fit on clean state jerks if the observation snaps gate↔no-gate
        # frame-to-frame; holding for ~0.16 s smooths detector hiccups. See __init__.
        if gate_pos_body is not None:
            self._consecutive_misses = 0
            self.lost = False
            self._last_gate = (gate_pos_body, gate_distance, gate_orient_body, next_gate_pos_body)
        elif self._last_gate is not None and self._consecutive_misses < self.gate_hold_frames:
            # HOLD: reuse last-known estimate (a real gate cannot leave the FoV this fast)
            self._consecutive_misses += 1
            self.frames_held += 1
            self.lost = False
            gate_pos_body, gate_distance, gate_orient_body, next_gate_pos_body = self._last_gate
        else:
            # LOST: beyond the hold window → fall through to the graceful no-gate default
            self._consecutive_misses += 1
            self.lost = True
            self._last_gate = None

        # 3. Detect gate passage (distance decreasing then suddenly increasing)
        if gate_distance is not None:
            if (self._prev_gate_distance is not None and
                gate_distance > self._prev_gate_distance * 1.5 and
                self._prev_gate_distance < self._gate_passage_threshold):
                self.adapter.on_gate_passed()
            self._prev_gate_distance = gate_distance
        elif primary.found and primary.area > 0:
            # No 3D pose but gate is detected — use area as distance proxy
            # Large area + sudden area drop = gate passage
            pass

        # 4. Build observation
        obs = self.adapter.build_observation(
            telemetry=telemetry,
            gate_pos_body=gate_pos_body,
            gate_distance=gate_distance,
            gate_orientation_body=gate_orient_body,
            next_gate_pos_body=next_gate_pos_body,
        )

        # 5. Run policy
        action, _ = self.policy.predict(obs, deterministic=True)

        # 6. Convert to competition format
        return self.adapter.to_competition_action(action)

    def reset(self):
        """Reset for new run."""
        self.adapter.reset()
        self._prev_gate_distance = None
        self._consecutive_misses = 0
        self._last_gate = None
        self.lost = False
        self.frames_held = 0
