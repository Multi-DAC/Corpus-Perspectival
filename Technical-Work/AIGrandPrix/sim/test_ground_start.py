#
# Smoke test for the TAKEOFF curriculum (ground_start) in InfiniteGateEnv.
#
# Gates the retrain: confirms the ground-start initial condition is WELL-POSED before
# any GPU time. Checks (1) ground_start resets to rest at z~0.2, (2) a hover-plus
# collective climbs (does not instant-crash on the z<0 floor), (3) default prob=0 is
# unchanged (starts airborne). Offline, seconds.
#
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)                              # sim/
sys.path.insert(0, os.path.join(HERE, "..", "rl"))    # train_ppo wrappers
from infinite_gate_env import InfiniteGateEnv

G, MASS, TWR = 9.81, 0.85, 3.85
# CTBR collective: action[0] in [-1,1] -> fraction (a0+1)/2 of 4*T_max (=TWR*m*g).
# hover fraction = 1/TWR = 0.26 -> a0_hover = 2*0.26-1 = -0.48. Use a0=-0.2 (~0.40) to climb.
A_CLIMB = np.array([-0.2, 0.0, 0.0, 0.0], dtype=np.float32)


def _drone_z(env):
    return float(env._base_env.state[2])

def _drone_vel(env):
    return env._base_env.state[3:6].copy()


def test_ground_start_resets_to_rest():
    env = InfiniteGateEnv(ground_start_prob=1.0, seed=0)
    env.reset()
    z, v = _drone_z(env), _drone_vel(env)
    assert 0.1 < z < 0.4, f"ground start z should be ~0.2, got {z:.2f}"
    assert np.linalg.norm(v) < 0.5, f"should start near rest, got |v|={np.linalg.norm(v):.2f}"

def test_default_is_airborne():
    env = InfiniteGateEnv(ground_start_prob=0.0, seed=0)
    env.reset()
    assert _drone_z(env) >= 0.5, f"default must stay airborne (>=0.5), got {_drone_z(env):.2f}"

def test_hover_plus_climbs_not_crashes():
    env = InfiniteGateEnv(ground_start_prob=1.0, seed=1)
    env.reset()
    z0 = _drone_z(env)
    crashed = False
    for _ in range(300):  # 0.6s at 500Hz
        _, _, term, trunc, info = env.step(A_CLIMB)
        if info.get("crash") == "ground":
            crashed = True; break
        if term or trunc:
            break
    z1 = _drone_z(env)
    assert not crashed, "hover-plus collective should NOT ground-crash from z=0.2"
    assert z1 > z0 + 0.3, f"should climb from ground, z {z0:.2f} -> {z1:.2f}"


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
    print("Ground-start takeoff curriculum is WELL-POSED.")
