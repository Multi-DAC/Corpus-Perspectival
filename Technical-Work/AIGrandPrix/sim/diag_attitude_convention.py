#
# diag_attitude_convention.py  (2026-06-02 late, creative drive)
#
# WHY: the A150 state policy froze (thr=0) on the real VQ1 sim. Root-narrowed: the real-sim
# spawn reads as ~18deg pitched (gravity-body g0=+3.0) while every training ground-start was
# LEVEL (g0=0). test_obs_encoding.py only ever checked the DISTANCE dims (9-20); the gravity/
# attitude dims (6-8) were NEVER verified for deploy==training parity. This probes:
#   (A) do deploy & training agree on gravity-body at a LEVEL pose?  (parity gap check)
#   (B) what does each give for the REAL-SIM spawn quaternion?
#   (C) is there an axis/convention reading of the real-sim quaternion that is actually LEVEL?
#       (i.e., is the 18deg a physical spawn pitch, or a convention artifact -> tonight-fixable)
#
import os, sys, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "vision"))
from infinite_gate_env import InfiniteGateEnv
from adapter import CompetitionAdapter, Telemetry
from drone_env_v2 import quat_rotate_np

# real-sim spawn quaternion as state_pilot reads it (MAVLink ODOMETRY q, assumed [w,x,y,z], NED)
Q_REAL_NED = np.array([0.0, -0.155, 0.0, -0.988])
def ned_to_zup_quat(q): return np.array([q[0], q[1], -q[2], -q[3]])

def euler_deg(q):
    w, x, y, z = q
    roll = math.degrees(math.atan2(2*(w*x + y*z), 1 - 2*(x*x + y*y)))
    pitch = math.degrees(math.asin(max(-1, min(1, 2*(w*y - z*x)))))
    yaw = math.degrees(math.atan2(2*(w*z + x*y), 1 - 2*(y*y + z*z)))
    return roll, pitch, yaw

def deploy_gravity(q_zup):
    """gravity-body (obs[6:9]) via the DEPLOY path (adapter.build_observation)."""
    pos = np.zeros(3); vel = np.zeros(3); omega = np.zeros(3)
    g0 = np.array([23.0, 0.0, 0.0]); g1 = np.array([40.0, 0.0, 0.0])
    q_conj = np.array([q_zup[0], -q_zup[1], -q_zup[2], -q_zup[3]])
    gate_body = quat_rotate_np(q_conj, g0 - pos); next_body = quat_rotate_np(q_conj, g1 - pos)
    ad = CompetitionAdapter(command_rate_hz=60.0)
    telem = Telemetry(position=pos, velocity=vel, orientation=q_zup, angular_velocity=omega)
    return np.asarray(ad.build_observation(telem, gate_body, float(np.linalg.norm(g0)), None, next_body))[6:9]

def training_gravity(q_zup):
    """gravity-body (obs[6:9]) via the TRAINING path (InfiniteGateEnv)."""
    env = InfiniteGateEnv(ground_start_prob=0.0, seed=0); env.reset()
    b = env._base_env
    b.state = np.concatenate([np.zeros(3), np.zeros(3), q_zup, np.zeros(3)]).astype(np.float64)
    b.gates = [np.array([23.0, 0.0, 0.0]), np.array([40.0, 0.0, 0.0])]
    b.n_gates = 2; b.current_gate = 0
    b.gate_orientations = [np.array([1.0, 0.0, 0.0]), np.array([1.0, 0.0, 0.0])]; b.steps = 0
    return np.asarray(env._obs_wrapper.observation(None), dtype=float)[6:9]

def pitchdeg_from_gravity(g):
    return math.degrees(math.atan2(g[0], -g[2]))  # forward-gravity vs down

print("=" * 70)
print("(A) LEVEL pose q=[1,0,0,0] — do deploy & training agree gravity=(0,0,-g)?")
qlevel = np.array([1.0, 0.0, 0.0, 0.0])
dg, tg = deploy_gravity(qlevel), training_gravity(qlevel)
print(f"   deploy  g_body = {np.round(dg,3)}  pitch={pitchdeg_from_gravity(dg):+.1f}")
print(f"   training g_body = {np.round(tg,3)}  pitch={pitchdeg_from_gravity(tg):+.1f}")
print(f"   PARITY: {'OK' if np.allclose(dg,tg,atol=1e-3) else 'MISMATCH <<<'}")

print("\n(B) REAL-SIM spawn quaternion, z-up converted")
q_zup = ned_to_zup_quat(Q_REAL_NED)
print(f"   q_ned={np.round(Q_REAL_NED,3)} -> z-up={np.round(q_zup,3)}  euler(zup)={tuple(round(x,1) for x in euler_deg(q_zup))}")
dg, tg = deploy_gravity(q_zup), training_gravity(q_zup)
print(f"   deploy  g_body = {np.round(dg,3)}  pitch={pitchdeg_from_gravity(dg):+.1f}")
print(f"   training g_body = {np.round(tg,3)}  pitch={pitchdeg_from_gravity(tg):+.1f}")
print(f"   PARITY: {'OK' if np.allclose(dg,tg,atol=1e-3) else 'MISMATCH <<<'}")

print("\n(C) Is there a component reading of the real-sim q that is LEVEL (pitch~0)?")
w, x, y, z = Q_REAL_NED
candidates = {
    "[w,x,y,z] as-is":      np.array([w, x, y, z]),
    "[x,y,z,w] scalar-last": np.array([z, w, x, y]),   # if sim scalar is last
    "neg-x (roll/pitch flip)": np.array([w, -x, y, z]),
    "swap x<->y":            np.array([w, y, x, z]),
    "[w,y,x,z]":             np.array([w, y, x, z]),
}
for name, q in candidates.items():
    q = q / (np.linalg.norm(q) + 1e-12)
    r, p, yw = euler_deg(q)
    flag = "  <-- LEVEL" if abs(p) < 5 and abs(r) < 5 else ""
    print(f"   {name:>26}: roll={r:+6.1f} pitch={p:+6.1f} yaw={yw:+6.1f}{flag}")
