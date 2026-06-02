"""
PerceptionObsWrapper — train-obs == deploy-obs (ROADMAP_v3 §3, W4).

The deployed pilot (VADR-TS-002 §3.3/§4.3) gets NO position and NO gate poses — only
attitude / velocity / IMU telemetry. Gate-relative position must come from a vision
detector + PnP (known gate size, §3.7). So the *gate-derived* observation terms are
ESTIMATES with detector error; the *telemetry-derived* terms are exact at deploy.

This wrapper makes training match that reality: it leaves the telemetry terms exact and
corrupts ONLY the gate-derived terms with a calibratable detector error model —
  • bearing noise   (angular error on the gate direction)
  • range  noise    (fractional error on distance, the PnP weak axis)
  • field-of-view    (gate outside the camera cone -> not detected)
  • dropout          (random missed detections; hold last-known, Swift-style)
  • latency          (perception runs behind the control loop)
Per-episode domain randomization samples these from ranges so the policy is robust to
the *range* of plausible detector error rather than betting on one calibration
(Clayton's "handle outside influence"). Recalibrate the defaults from the measured
detector error on the auto-labeled real-frame dataset (W3) via set_error_model().

Drop-in replacement for ImprovedObsWrapper: same 30-dim observation_space, same term
order. Ego terms (vel_body, omega, g_body, speed, forward_world, time_since_gate) are
reproduced exactly by deferring to the parent computation path.
"""

import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "rl"))

from obs_encoding import unit_dir, bound_scalar
from drone_env_v2 import quat_rotate_np
from train_ppo import ImprovedObsWrapper


# Provisional detector error model (ranges = per-episode domain-randomization spans).
# REPLACE with W3-measured values from the auto-labeled real-frame dataset.
DEFAULT_ERROR_MODEL = {
    "bearing_sigma_rad": (0.005, 0.035),   # ~0.3°–2° angular error on gate direction
    "range_sigma_frac":  (0.03, 0.15),     # 3%–15% fractional range error (PnP weak axis)
    "fov_halfangle_rad": (0.70, 0.90),     # detection cone half-angle (VFoV 90° => ~0.785 rad)
    "max_range_m":       (25.0, 45.0),     # beyond this the gate is too small to detect
    "dropout_prob":      (0.0, 0.10),      # per-frame random missed detection
    "latency_steps":     (0, 2),           # perception lag in control steps
    "next_gate_extra_dropout": 0.5,        # the look-ahead gate is usually not in view
}


class PerceptionObsWrapper(ImprovedObsWrapper):
    def __init__(self, env, error_model=None, randomize=True, seed=None):
        super().__init__(env)
        self.error_model = dict(DEFAULT_ERROR_MODEL)
        if error_model:
            self.error_model.update(error_model)
        self.randomize = randomize
        self.rng = np.random.default_rng(seed)
        self._reset_perception_state()
        self._sample_episode_params()

    # --- configuration ---------------------------------------------------------------
    def set_error_model(self, **kwargs):
        """Plug W3-measured detector error (point values or (lo,hi) ranges)."""
        self.error_model.update(kwargs)

    def _sample_episode_params(self):
        em = self.error_model
        def draw(key):
            v = em[key]
            if isinstance(v, (tuple, list)):
                lo, hi = v
                if isinstance(lo, int) and isinstance(hi, int):
                    return int(self.rng.integers(lo, hi + 1))
                return float(self.rng.uniform(lo, hi))
            return v
        if self.randomize:
            self._p = {k: draw(k) for k in
                       ("bearing_sigma_rad", "range_sigma_frac", "fov_halfangle_rad",
                        "max_range_m", "dropout_prob", "latency_steps")}
        else:
            # midpoint of each range (deterministic eval)
            def mid(key):
                v = em[key]
                if isinstance(v, (tuple, list)):
                    return type(v[0])((v[0] + v[1]) / 2)
                return v
            self._p = {k: mid(k) for k in
                       ("bearing_sigma_rad", "range_sigma_frac", "fov_halfangle_rad",
                        "max_range_m", "dropout_prob", "latency_steps")}
        self._p["next_gate_extra_dropout"] = em["next_gate_extra_dropout"]

    def _reset_perception_state(self):
        # last-known perceived gate vectors (world frame) + latency buffers
        self._last_cur = None
        self._last_next = None
        self._buf_cur = []
        self._buf_next = []

    # --- perception model ------------------------------------------------------------
    def _perceive(self, rel_world, forward_world, is_next, buf, last_key):
        """Given the TRUE world-frame gate offset, return a detector-style estimate
        (world frame), or None if not detected (hold last-known downstream)."""
        p = self._p
        dist = float(np.linalg.norm(rel_world))
        detected = dist > 1e-6 and dist <= p["max_range_m"]
        if detected:
            # field-of-view: angle between camera/heading axis and the gate direction
            fdir = forward_world / (np.linalg.norm(forward_world) + 1e-9)
            cos_ang = float(np.dot(fdir, rel_world / dist))
            if cos_ang < np.cos(p["fov_halfangle_rad"]):
                detected = False
        if detected:
            dp = p["dropout_prob"]
            if is_next:
                dp = 1.0 - (1.0 - dp) * (1.0 - p["next_gate_extra_dropout"])
            if self.rng.random() < dp:
                detected = False

        if detected:
            d = rel_world / dist
            d = d + self.rng.normal(0.0, p["bearing_sigma_rad"], size=3)  # bearing noise
            d = d / (np.linalg.norm(d) + 1e-9)
            r = dist * (1.0 + self.rng.normal(0.0, p["range_sigma_frac"]))  # range noise
            est = d * max(r, 0.0)
            setattr(self, last_key, est)
        else:
            est = getattr(self, last_key)  # hold last-known (may be None = never seen)

        # latency: emit the estimate from `latency_steps` ago
        buf.append(est)
        k = p["latency_steps"]
        return buf[-1 - k] if len(buf) > k else buf[0]

    # --- observation -----------------------------------------------------------------
    def observation(self, obs):
        env = self.env
        while hasattr(env, "env"):
            env = env.env

        state = env.state
        pos, vel, q, omega = state[0:3], state[3:6], state[6:10], state[10:13]
        q_conj = np.array([q[0], -q[1], -q[2], -q[3]])

        # ----- telemetry-derived terms: EXACT (available at deploy) -----
        vel_body = quat_rotate_np(q_conj, vel)
        g_body = quat_rotate_np(q_conj, np.array([0.0, 0.0, -9.81]))
        forward_world = quat_rotate_np(q, np.array([0.0, 0.0, 1.0]))
        speed = float(np.linalg.norm(vel))

        n_gates, current = env.n_gates, env.current_gate

        # ----- gate-derived terms: detector ESTIMATES (perception-grade) -----
        if current < n_gates:
            true_rel_world = env.gates[current] - pos
            est_world = self._perceive(true_rel_world, forward_world, False,
                                       self._buf_cur, "_last_cur")
        else:
            est_world = None

        if est_world is not None:
            rel_gate_body = quat_rotate_np(q_conj, est_world)
            dist_to_gate = float(np.linalg.norm(est_world))
            rel_gate_world = est_world
            sd = dist_to_gate + 1e-6
            speed_toward = -float(np.dot(vel, est_world / sd))
            # gate orientation estimate (perceived via PnP) — bearing-noised true normal
            go_world = np.array(env.gate_orientations[current], dtype=float)
            go_world = go_world + self.rng.normal(0.0, self._p["bearing_sigma_rad"], size=3)
            go_world = go_world / (np.linalg.norm(go_world) + 1e-9)
            gate_orient_body = quat_rotate_np(q_conj, go_world)
            gate_alignment = float(np.dot(vel / (speed + 1e-9), go_world)) if speed > 0.1 else 0.0
        else:
            rel_gate_body = np.zeros(3); dist_to_gate = 0.0; rel_gate_world = np.zeros(3)
            speed_toward = 0.0; gate_orient_body = np.zeros(3); gate_alignment = 0.0

        # look-ahead gate
        if current + 1 < n_gates:
            true_next_world = env.gates[current + 1] - pos
            est_next = self._perceive(true_next_world, forward_world, True,
                                      self._buf_next, "_last_next")
            rel_next_body = quat_rotate_np(q_conj, est_next) if est_next is not None else np.zeros(3)
        elif est_world is not None:
            rel_next_body = rel_gate_body
        else:
            rel_next_body = np.zeros(3)

        # timing / progress (deploy: derive from passed-gate count + a step clock)
        if current > self.last_gate_idx:
            self.last_gate_time = env.steps * env.dt
            self.last_gate_idx = current
        time_since_gate = env.steps * env.dt - self.last_gate_time
        progress = current / max(n_gates, 1)

        return np.array([
            *vel_body,                    # 3  telemetry (exact)
            *omega,                       # 3  telemetry (exact)
            *g_body,                      # 3  telemetry (exact)
            *unit_dir(rel_gate_body),     # 3  PERCEPTION
            bound_scalar(dist_to_gate),   # 1  PERCEPTION
            *unit_dir(rel_next_body),     # 3  PERCEPTION
            speed,                        # 1  telemetry (exact)
            progress,                     # 1  derived
            *unit_dir(rel_gate_world),    # 3  PERCEPTION
            *forward_world,               # 3  telemetry (exact)
            time_since_gate,              # 1  derived
            speed_toward,                 # 1  PERCEPTION (vel exact, dir noisy)
            *gate_orient_body,            # 3  PERCEPTION
            gate_alignment,               # 1  PERCEPTION
        ], dtype=np.float32)

    def reset(self, **kwargs):
        self._reset_perception_state()
        self._sample_episode_params()
        return super().reset(**kwargs)
