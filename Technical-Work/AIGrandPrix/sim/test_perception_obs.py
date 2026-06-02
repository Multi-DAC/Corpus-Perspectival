"""Test: PerceptionObsWrapper keeps telemetry terms exact, corrupts only gate terms.

Run: python test_perception_obs.py  (or pytest). Validates the train-obs==deploy-obs
discipline (ROADMAP_v3 §3 / W4).
"""
import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "rl"))
from drone_env_v2 import DroneRacingEnvV2
from train_ppo import CTBRActionWrapper, ImprovedObsWrapper
from perception_obs import PerceptionObsWrapper

# obs index groups (30-dim layout, see ImprovedObsWrapper / PerceptionObsWrapper)
TELE = list(range(0, 9)) + [16, 17, 21, 22, 23, 24]   # vel_body,omega,g_body,speed,progress,forward,t
PERC = [9, 10, 11, 12, 13, 14, 18, 19, 20, 25, 26, 27, 28, 29]


def _make(gates):
    base = DroneRacingEnvV2(gates=gates, gate_radius=0.75, max_steps=1000, dt=0.002)
    return CTBRActionWrapper(base)


def test_zero_noise_matches_parent():
    ctbr = _make([np.array([8., 0, 2.0]), np.array([16., 2., 3.0])])
    ref = ImprovedObsWrapper(ctbr); ref.reset(seed=0)
    zero = dict(bearing_sigma_rad=0.0, range_sigma_frac=0.0, fov_halfangle_rad=3.2,
                max_range_m=1e6, dropout_prob=0.0, latency_steps=0, next_gate_extra_dropout=0.0)
    per = PerceptionObsWrapper(ctbr, error_model=zero, randomize=False)
    per.last_gate_idx, per.last_gate_time = ref.last_gate_idx, ref.last_gate_time
    assert np.max(np.abs(ref.observation(None) - per.observation(None))) < 1e-9


def test_telemetry_exact_perception_noisy():
    ctbr = _make([np.array([8., 0, 2.0]), np.array([16., 2., 3.0])])
    ref = ImprovedObsWrapper(ctbr); ref.reset(seed=0)
    per = PerceptionObsWrapper(ctbr, randomize=True, seed=3)
    per.last_gate_idx, per.last_gate_time = ref.last_gate_idx, ref.last_gate_time
    o_ref, o_per = ref.observation(None), per.observation(None)
    assert np.max(np.abs(o_ref[TELE] - o_per[TELE])) < 1e-9           # telemetry untouched
    assert np.max(np.abs(o_ref[PERC] - o_per[PERC])) > 1e-3           # perception corrupted
    assert np.all(np.isfinite(o_per))


def test_out_of_range_drops_to_zero():
    per = PerceptionObsWrapper(_make([np.array([100., 0, 2.0])]),
                               error_model={"max_range_m": (5., 5.)}, randomize=False)
    per.reset(seed=1)
    o = per.observation(None)
    assert np.allclose(o[9:12], 0) and np.all(np.isfinite(o))         # never seen -> zeros, no crash


if __name__ == "__main__":
    test_zero_noise_matches_parent()
    test_telemetry_exact_perception_noisy()
    test_out_of_range_drops_to_zero()
    print("perception_obs: 3/3 OK")
