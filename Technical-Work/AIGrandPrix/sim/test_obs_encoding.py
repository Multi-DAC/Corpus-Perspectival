#
# Unit test: the bounded-distance encoding is applied IDENTICALLY in the deploy path
# (vision/adapter.build_observation) and the training path (rl/ImprovedObsWrapper), and it
# actually bounds the far-gate distance that blew up live (VQ1 23m start -> obs was ~23 raw,
# ~6 sigma after VecNormalize). This is the L17-trap guard: if deploy != training, the live
# obs silently diverges from what the policy trained on.
#
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "rl"))
sys.path.insert(0, os.path.join(HERE, "..", "vision"))
from infinite_gate_env import InfiniteGateEnv
from adapter import CompetitionAdapter, Telemetry
from drone_env_v2 import quat_rotate_np

# Distance dims (0-indexed) that we bounded — must match in both paths and be bounded.
DIST_DIMS = list(range(9, 12)) + [12] + list(range(13, 16)) + list(range(18, 21))


def _matched_state():
    # Drone level at 2m, at rest, identity attitude (body==world -> simplest matched frame).
    # FAR gate 0 at 23m ahead (the VQ1 geometry that blew up), gate 1 at 40m.
    pos = np.array([0.0, 0.0, 2.0]); vel = np.zeros(3)
    q = np.array([1.0, 0.0, 0.0, 0.0]); omega = np.zeros(3)
    g0 = np.array([23.0, 0.0, 2.0]); g1 = np.array([40.0, 0.0, 2.0])
    return pos, vel, q, omega, g0, g1


def _training_obs():
    env = InfiniteGateEnv(ground_start_prob=0.0, seed=0); env.reset()
    pos, vel, q, omega, g0, g1 = _matched_state()
    b = env._base_env
    b.state = np.concatenate([pos, vel, q, omega]).astype(np.float64)
    b.gates = [g0, g1]; b.n_gates = 2; b.current_gate = 0
    b.gate_orientations = [np.array([1.0, 0.0, 0.0]), np.array([1.0, 0.0, 0.0])]
    b.steps = 0
    return np.asarray(env._obs_wrapper.observation(None), dtype=float)


def _deploy_obs():
    pos, vel, q, omega, g0, g1 = _matched_state()
    q_conj = np.array([q[0], -q[1], -q[2], -q[3]])
    gate_body = quat_rotate_np(q_conj, g0 - pos)
    next_body = quat_rotate_np(q_conj, g1 - pos)
    dist = float(np.linalg.norm(g0 - pos))
    adapter = CompetitionAdapter(command_rate_hz=60.0)
    telem = Telemetry(position=pos, velocity=vel, orientation=q, angular_velocity=omega)
    return np.asarray(adapter.build_observation(telem, gate_body, dist, None, next_body), dtype=float)


def test_deploy_equals_training_on_distance_dims():
    ot, od = _training_obs(), _deploy_obs()
    for d in DIST_DIMS:
        assert abs(ot[d] - od[d]) < 1e-4, f"dim {d}: train {ot[d]:.4f} != deploy {od[d]:.4f} (L17-trap!)"

def test_distance_dims_are_bounded():
    ot, od = _training_obs(), _deploy_obs()
    for name, o in (("train", ot), ("deploy", od)):
        for d in DIST_DIMS:
            assert abs(o[d]) <= 1.01, f"{name} dim {d}={o[d]:.3f} not bounded (raw would be ~23!)"

def test_far_gate_no_longer_blows_up():
    # The whole point: at 23m the gate-distance dims used to be ~23 (->6 sigma). Now <=1.
    ot = _training_obs()
    assert max(abs(ot[d]) for d in DIST_DIMS) <= 1.01, "far-gate distance dims must be bounded"
    # And direction is preserved: gate is +x ahead, so dim 9 (rel_gate_body x) should be ~+0.98.
    assert ot[9] > 0.9, f"direction lost: rel_gate_body x = {ot[9]:.3f} (gate is dead ahead)"


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    for t in tests:
        try:
            t(); passed += 1; print(f"  PASS  {t.__name__}")
        except AssertionError as e:
            print(f"  FAIL  {t.__name__}: {e}")
        except Exception as e:
            print(f"  ERROR {t.__name__}: {type(e).__name__}: {e}")
    print(f"\n{passed}/{len(tests)} passed")
    if passed != len(tests):
        raise SystemExit(1)
    print("Bounded encoding: deploy==training, far gate bounded, direction preserved.")
