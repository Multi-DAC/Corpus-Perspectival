"""
End-to-end stub integration test.

Loads the Phase 2 67.5M policy + its paired VecNormalize, builds a
synthetic Telemetry + gate detection, runs the full pipeline:

    Telemetry -> CompetitionAdapter.build_observation
              -> VecNormalize.normalize_obs
              -> policy.predict
              -> CompetitionAdapter.to_competition_action
              -> StubMAVSDKClient.send_policy_action

and asserts that:
  - The 30-dim observation is finite + correctly shaped.
  - The policy emits a finite action in [-1, 1]^4.
  - The adapter's CompetitionAction throttle is in [0, 1] and rates are
    in expected physical ranges.
  - The stub client accepts send_policy_action and the latest setpoint
    on the *real* MAVSDKClient class would be updated correctly.
  - 100 sequential steps don't produce NaN propagation or runaway action
    saturation.

This is the SITL-free derisk: catches any silent break between the policy
zip and the client introduced by the G1+G2 restructuring or by future
client edits, without needing PX4 to be running.
"""

import os
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).parent
VISION = HERE.parent
AIGP = VISION.parent
SIM = AIGP / "sim"
RL = AIGP / "rl"

sys.path.insert(0, str(VISION))
sys.path.insert(0, str(SIM))
sys.path.insert(0, str(RL))

POLICY_ZIP = (
    AIGP / "sim" / "runs" / "infinite_v3_phase2_60M_1777095742"
    / "checkpoints" / "ppo_phase2_67500016_steps.zip"
)
VECNORM_PKL = (
    AIGP / "sim" / "runs" / "infinite_v3_phase2_60M_1777095742"
    / "checkpoints" / "ppo_phase2_67500016_steps_vecnorm.pkl"
)


pytestmark = pytest.mark.skipif(
    not POLICY_ZIP.exists() or not VECNORM_PKL.exists(),
    reason=f"Phase 2 67.5M artifacts not found at {POLICY_ZIP}",
)


# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------


@pytest.fixture(scope="module")
def policy():
    """Load the Phase 2 67.5M PPO policy."""
    from stable_baselines3 import PPO
    return PPO.load(str(POLICY_ZIP), device="cpu")


@pytest.fixture(scope="module")
def vecnorm():
    """Load the paired VecNormalize statistics."""
    from stable_baselines3.common.vec_env import VecNormalize
    return VecNormalize.load(str(VECNORM_PKL), venv=_DummyVenv())


class _DummyVenv:
    """Minimal venv shim VecNormalize.load expects when we only want stats."""
    def __init__(self):
        from gymnasium import spaces
        self.num_envs = 1
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(30,), dtype=np.float32
        )
        self.action_space = spaces.Box(
            low=-1.0, high=1.0, shape=(4,), dtype=np.float32
        )
        self.render_mode = None

    def reset(self):
        return np.zeros((1, 30), dtype=np.float32), {}

    def step_wait(self):
        raise RuntimeError("Stub venv: step not supported")

    def get_attr(self, name, indices=None):
        return [None]

    def render(self):
        return None

    def close(self):
        pass


def _synth_telemetry(pos=None, vel=None, q=None, omega=None):
    """Build a Telemetry in our z-up sim frame."""
    from adapter import Telemetry
    return Telemetry(
        position=np.array(pos if pos is not None else [0.0, 0.0, 2.0]),
        velocity=np.array(vel if vel is not None else [3.0, 0.0, 0.0]),
        orientation=np.array(q if q is not None else [1.0, 0.0, 0.0, 0.0]),
        angular_velocity=np.array(omega if omega is not None else [0.0, 0.0, 0.0]),
    )


# ----------------------------------------------------------------------
# Single-step pipeline
# ----------------------------------------------------------------------


def test_observation_is_finite_and_shaped():
    from adapter import CompetitionAdapter
    adapter = CompetitionAdapter()
    telem = _synth_telemetry()
    gate_body = np.array([5.0, 0.0, 0.0])  # 5m forward
    obs = adapter.build_observation(
        telemetry=telem,
        gate_pos_body=gate_body,
        gate_distance=5.0,
    )
    assert obs.shape == (30,)
    assert obs.dtype == np.float32
    assert np.all(np.isfinite(obs))


def test_policy_predict_yields_valid_action(policy, vecnorm):
    from adapter import CompetitionAdapter
    adapter = CompetitionAdapter()
    telem = _synth_telemetry()
    obs = adapter.build_observation(
        telemetry=telem,
        gate_pos_body=np.array([5.0, 0.0, 0.0]),
        gate_distance=5.0,
    )
    obs_norm = vecnorm.normalize_obs(obs.reshape(1, -1))
    action, _ = policy.predict(obs_norm, deterministic=True)
    action = np.asarray(action).reshape(-1)
    assert action.shape == (4,)
    assert np.all(np.isfinite(action))
    assert np.all(action >= -1.0 - 1e-6) and np.all(action <= 1.0 + 1e-6)


def test_adapter_to_competition_action_ranges():
    from adapter import CompetitionAdapter
    adapter = CompetitionAdapter()
    # Worst-case saturated policy output
    action = np.array([1.0, 1.0, -1.0, 1.0], dtype=np.float32)
    cmd = adapter.to_competition_action(action)
    assert 0.0 <= cmd.throttle <= 1.0
    assert abs(cmd.roll_rate_rad_s) <= adapter.MAX_RATE_XY + 1e-6
    assert abs(cmd.pitch_rate_rad_s) <= adapter.MAX_RATE_XY + 1e-6
    assert abs(cmd.yaw_rate_rad_s) <= adapter.MAX_RATE_Z + 1e-6


def test_stub_client_accepts_full_pipeline_action(policy, vecnorm):
    """
    End-to-end: synth telemetry → adapter → policy → stub client.send_policy_action.
    Verifies the boundary contract works without needing SITL.
    """
    from adapter import CompetitionAdapter
    from mavsdk_client import StubMAVSDKClient

    client = StubMAVSDKClient()
    client.init_flight(connect_timeout=1, health_timeout=1)
    adapter = CompetitionAdapter()

    telem = _synth_telemetry()
    obs = adapter.build_observation(
        telemetry=telem,
        gate_pos_body=np.array([5.0, 0.0, 0.0]),
        gate_distance=5.0,
    )
    obs_norm = vecnorm.normalize_obs(obs.reshape(1, -1))
    action, _ = policy.predict(obs_norm, deterministic=True)
    action = np.asarray(action).reshape(-1).astype(np.float32)

    # Stub silently accepts; we only need the call to not raise
    client.send_policy_action(action)


def test_real_client_setpoint_update_after_policy(policy, vecnorm):
    """
    Run policy through the *real* MAVSDKClient (without connecting to anything)
    and verify send_body_rates updates the _last_setpoint slot the pre-stream
    coroutine reads from.
    """
    from adapter import CompetitionAdapter
    from mavsdk_client import (
        MAVSDKClient, send_policy_action_constants, zup_to_ned_rates,
    )

    client = MAVSDKClient.__new__(MAVSDKClient)
    MAVSDKClient.__init__(client)
    client._connected = True  # bypass the noop guard

    adapter = CompetitionAdapter()
    telem = _synth_telemetry()
    obs = adapter.build_observation(
        telemetry=telem,
        gate_pos_body=np.array([5.0, 0.0, 0.0]),
        gate_distance=5.0,
    )
    obs_norm = vecnorm.normalize_obs(obs.reshape(1, -1))
    action, _ = policy.predict(obs_norm, deterministic=True)
    action = np.asarray(action).reshape(-1).astype(np.float32)

    client.send_policy_action(action)

    thrust, r, p, y = client._last_setpoint
    # Thrust mapping consistency with adapter
    assert abs(thrust - float((action[0] + 1.0) * 0.5)) < 1e-6
    # Rates: zup → NED (pitch and yaw flipped)
    rad2deg = send_policy_action_constants["RAD2DEG"]
    max_xy = send_policy_action_constants["MAX_RATE_XY"]
    max_z = send_policy_action_constants["MAX_RATE_Z"]
    expected_zup = np.array([
        action[1] * max_xy * rad2deg,
        action[2] * max_xy * rad2deg,
        action[3] * max_z * rad2deg,
    ])
    expected_ned = zup_to_ned_rates(expected_zup)
    assert abs(r - expected_ned[0]) < 1e-6
    assert abs(p - expected_ned[1]) < 1e-6
    assert abs(y - expected_ned[2]) < 1e-6


# ----------------------------------------------------------------------
# Multi-step rollout
# ----------------------------------------------------------------------


def test_no_nan_propagation_over_100_steps(policy, vecnorm):
    """
    Roll the policy for 100 steps with a slowly-moving synthetic target.
    Catch any state that produces NaN/Inf actions or observations.
    """
    from adapter import CompetitionAdapter
    from mavsdk_client import StubMAVSDKClient

    client = StubMAVSDKClient()
    client.init_flight(connect_timeout=1, health_timeout=1)
    adapter = CompetitionAdapter()

    pos = np.array([0.0, 0.0, 2.0])
    vel = np.array([3.0, 0.0, 0.0])
    q = np.array([1.0, 0.0, 0.0, 0.0])
    omega = np.zeros(3)
    dt = 1.0 / 50.0  # 50 Hz command rate

    saturation_count = 0
    actions = []

    for step in range(100):
        # Move target slowly relative to the drone
        gate_body = np.array([5.0 - 0.01 * step, 0.0, 0.0])
        gate_dist = float(np.linalg.norm(gate_body))

        telem = adapter.__class__  # placeholder to avoid unused warnings
        from adapter import Telemetry
        telem = Telemetry(
            position=pos.copy(),
            velocity=vel.copy(),
            orientation=q.copy(),
            angular_velocity=omega.copy(),
        )

        obs = adapter.build_observation(
            telemetry=telem,
            gate_pos_body=gate_body,
            gate_distance=gate_dist,
        )
        assert np.all(np.isfinite(obs)), f"obs went non-finite at step {step}"

        obs_norm = vecnorm.normalize_obs(obs.reshape(1, -1))
        action, _ = policy.predict(obs_norm, deterministic=True)
        action = np.asarray(action).reshape(-1).astype(np.float32)

        assert np.all(np.isfinite(action)), f"action went non-finite at step {step}"
        actions.append(action.copy())

        # Track all-saturation as a soft signal (not failure)
        if np.all(np.abs(action) > 0.99):
            saturation_count += 1

        # Naive integration of the drone state — just to keep telemetry
        # changing, not to be physically accurate.
        pos = pos + vel * dt
        client.send_policy_action(action)

    actions = np.array(actions)
    # No constant action — policy must respond to the changing observation
    assert actions.std(axis=0).sum() > 0, "Policy produced constant action over 100 steps"
    # Sanity: not every single step is at the saturation boundary
    assert saturation_count < 100, "Policy saturated all four channels every step"
