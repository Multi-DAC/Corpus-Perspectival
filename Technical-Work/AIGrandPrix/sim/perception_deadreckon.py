"""
perception_deadreckon.py — DeadReckonPerceptionObsWrapper.

The cliff finding (sweep_channels.py 2026-06-02): Anakin is robust to range/bearing/dropout/
latency noise but collapses (0.08 gates/ep) under the DETECTION constraint — FoV cone + range
limit. The drone goes blind when a gate leaves the ~90 deg camera cone (or passes ~28 m), and
Anakin — trained on omniscient privileged state — flies blind into nothing.

The fix tested here: when a gate is NOT detected, don't hold the STALE last-known relative
vector (what the stock PerceptionObsWrapper does) — instead DEAD-RECKON it by integrating the
drone's own ego-motion. The gate is static in the world, so its relative position evolves as
    rel(t+1) = gate_world - pos(t+1) = rel(t) - velocity*dt .
Velocity is exact telemetry (no position needed), so over a blind window the gate estimate
stays geometrically correct. This is the minimal visual-inertial-odometry move a real deploy
pilot makes. The ONLY change from the parent is the not-detected branch: `est = prev - disp`
instead of `est = prev`. Everything else (noise model, FoV/range gating, latency, term order)
is identical, so any recovery is attributable purely to persistence-through-the-blind-window.
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "rl"))

from perception_obs import PerceptionObsWrapper
from drone_env_v2 import quat_rotate_np


class DeadReckonPerceptionObsWrapper(PerceptionObsWrapper):
    """Identical to PerceptionObsWrapper but propagates lost gates by ego-motion.

    `max_reckon_steps` implements L13's staleness-gated prevention recipe: after that many
    consecutive blind steps, STOP trusting the reckoned estimate and emit "no detection" (None ->
    zeros downstream) rather than a confidently-wrong stale σ_ext. None = unbounded (pure VIO).
    """

    def __init__(self, env, max_reckon_steps=None, cam_axis_body=None, deadreckon=True, **kwargs):
        super().__init__(env, **kwargs)
        self.max_reckon_steps = max_reckon_steps
        self.deadreckon = deadreckon       # False = hold-stale (parent behavior) w/ corrected cam
        # If set, the FoV cone is built around this body-fixed camera axis (forward FPV cam)
        # instead of the obs's forward_world (= body-z = thrust/up axis). The obs term is unchanged.
        self.cam_axis_body = None if cam_axis_body is None else np.asarray(cam_axis_body, float)
        self._stale = {"_last_cur": 0, "_last_next": 0}

    def _reset_perception_state(self):
        super()._reset_perception_state()
        self._stale = {"_last_cur": 0, "_last_next": 0}

    def _ego_disp(self):
        """World-frame displacement of the drone this control step (velocity * dt)."""
        env = self.env
        while hasattr(env, "env"):
            env = env.env
        return env.state[3:6] * env.dt

    def _perceive(self, rel_world, forward_world, is_next, buf, last_key):
        p = self._p
        disp = self._ego_disp()
        dist = float(np.linalg.norm(rel_world))
        detected = dist > 1e-6 and dist <= p["max_range_m"]
        if detected:
            if self.cam_axis_body is not None:
                env = self.env
                while hasattr(env, "env"):
                    env = env.env
                cam_w = quat_rotate_np(env.state[6:10], self.cam_axis_body)
                fdir = cam_w / (np.linalg.norm(cam_w) + 1e-9)
            else:
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
            d = d + self.rng.normal(0.0, p["bearing_sigma_rad"], size=3)
            d = d / (np.linalg.norm(d) + 1e-9)
            r = dist * (1.0 + self.rng.normal(0.0, p["range_sigma_frac"]))
            est = d * max(r, 0.0)
            setattr(self, last_key, est)
            self._stale[last_key] = 0             # fresh live measurement resets staleness
        else:
            prev = getattr(self, last_key)
            self._stale[last_key] += 1
            gated_out = (self.max_reckon_steps is not None
                         and self._stale[last_key] > self.max_reckon_steps)
            if prev is not None and not gated_out:
                est = (prev - disp) if self.deadreckon else prev   # reckon, or hold-stale
                setattr(self, last_key, est)
            else:
                est = None                        # never seen, or staleness-gated -> no detection

        buf.append(est)
        k = p["latency_steps"]
        return buf[-1 - k] if len(buf) > k else buf[0]
