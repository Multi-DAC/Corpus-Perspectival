#
# Anakin state-based pilot for AI-GP VQ1.
#
# Splices our trained 67.5M policy into the sim's pymavlink interface, flying
# off STATE (drone pose + gate NED positions + active-gate index streamed by the
# sim) instead of vision. State is the bootstrap; vision curriculum comes later.
#
# Pipeline each step:
#   sim NED telemetry/gates  -> z-up conversion (proven, from mavsdk_client.py)
#   -> adapter.build_observation (30-dim, matches training)
#   -> VecNormalize -> policy.predict -> to_competition_action
#   -> z-up rates back to NED -> set_attitude_target_send (rad/s)
#
# Usage:
#   python state_pilot.py --dry-run [secs]   # Stage 1: log obs+action, command NOTHING
#   python state_pilot.py [secs]             # Stage 2: actually fly
#
# Press RACE in the sim after it arms (gates + race only stream once racing).
#

import os
import sys
import time
import struct
import threading
import argparse

import numpy as np
from pymavlink import mavutil

# --- our trained-policy stack ---
AIGP = r"C:\Users\mercu\clawd\repo-staging\Corpus-Perspectival\Technical-Work\AIGrandPrix"
sys.path.insert(0, os.path.join(AIGP, "vision"))
sys.path.insert(0, os.path.join(AIGP, "sim"))
from adapter import CompetitionAdapter, Telemetry          # noqa: E402
from drone_env_v2 import quat_rotate_np                    # noqa: E402
from stable_baselines3 import PPO                          # noqa: E402
import pickle                                              # noqa: E402

# Default = the original mid-air-only 67.5M (no takeoff). Override with --ckpt to fly the
# takeoff-retrain checkpoint, e.g.:
#   --ckpt runs/infinite_v3_takeoff_twr385_1780305737/checkpoints/ppo_phase2_<step>_steps.zip
CKPT_DIR = os.path.join(AIGP, "sim", "runs", "infinite_v3_phase2_60M_1777095742", "checkpoints")
ZIP = os.path.join(CKPT_DIR, "ppo_phase2_67500016_steps.zip")
PKL = os.path.join(CKPT_DIR, "ppo_phase2_67500016_steps_vecnorm.pkl")

IP, PORT = "127.0.0.1", 14550
CONTROL_HZ = 60.0
ENC_RACE, ENC_TRACK = 1, 2
RATES_MASK = mavutil.mavlink.ATTITUDE_TARGET_TYPEMASK_ATTITUDE_IGNORE

# ---- proven NED<->z-up conversions (verbatim from mavsdk_client.py) ----
def ned_to_zup_vec(v):      # position / velocity:  x=N, y=-E, z=-D
    return np.array([v[0], -v[1], -v[2]])
def ned_to_zup_quat(q):     # q=[w,x,y,z]: negate y,z
    return np.array([q[0], q[1], -q[2], -q[3]])
def ned_to_zup_omega(o):    # body rates FRD->FLU: flip pitch,yaw (geometrically consistent)
    return np.array([o[0], -o[1], -o[2]])
def zup_to_ned_rates(r):    # body rates FLU->set_attitude_target send convention
    # FIXED 2026-06-01: tonight's [r,-p,-y] gave a sign-INVERTED closed loop (positive
    # feedback -> tumble). The competition sim measures ODOMETRY = -(sent rate) per axis
    # (calib_log_2026-05-31, CALIB_FIT_2026-06-01.md). Holding the validated obs path
    # (ned_to_zup_omega) fixed, honest negative-feedback control requires the negation:
    # [-r, +p, +y]. Locked by test_command_frame.py (4/4).
    return np.array([-r[0], r[1], r[2]])


class SharedState:
    def __init__(self):
        self.lock = threading.Lock()
        self.pos_ned = np.zeros(3)
        self.vel_ned = np.zeros(3)
        self.q_ned = np.array([1.0, 0.0, 0.0, 0.0])  # [w,x,y,z]
        self.omega_body = np.zeros(3)
        self.have_pose = False
        self.gates = {}        # gate_id -> np.array(pos_ned xyz)
        self.gate_orient = {}  # gate_id -> orient quat [w,x,y,z] NED (captured for Phase-1 exact gate-normal; convention needs unit-test)
        self.num_gates = 0
        self.active_gate = 0
        self.race_started = False
        self._chunks = {}
        self._expected = {}


def rx_loop(conn, st, stop):
    while not stop.is_set():
        try:
            msg = conn.recv_match(blocking=False)
        except ConnectionResetError:
            return
        if msg is None:
            time.sleep(0.0005)
            continue
        t = msg.get_type()
        if t == "ODOMETRY":
            with st.lock:
                st.pos_ned = np.array([msg.x, msg.y, msg.z])
                st.vel_ned = np.array([msg.vx, msg.vy, msg.vz])
                st.q_ned = np.array([msg.q[0], msg.q[1], msg.q[2], msg.q[3]])
                st.omega_body = np.array([msg.rollspeed, msg.pitchspeed, msg.yawspeed])
                st.have_pose = True
        elif t == "DATA_TRANSMISSION_HANDSHAKE":
            with st.lock:
                st._chunks[msg.width] = {}
                st._expected[msg.width] = msg.packets
        elif t == "ENCAPSULATED_DATA":
            raw = bytes(msg.data)
            if not raw:
                continue
            dt = raw[0]
            if dt == ENC_RACE:
                try:
                    (_dt, _sim, race_start_ms, _fin, active, _last) = struct.unpack_from("<BQqqIq", raw)
                    with st.lock:
                        st.active_gate = int(active)
                        st.race_started = race_start_ms is not None and race_start_ms >= 0
                except struct.error:
                    pass
            elif dt == ENC_TRACK:
                _dt, transfer_id = struct.unpack_from("<BH", raw)
                with st.lock:
                    if transfer_id in st._expected:
                        st._chunks[transfer_id][msg.seqnr] = raw[3:]
                        if len(st._chunks[transfer_id]) == st._expected[transfer_id]:
                            payload = b"".join(st._chunks[transfer_id][i]
                                               for i in range(st._expected[transfer_id]))
                            _parse_track(payload, st)
                            del st._chunks[transfer_id]
                            del st._expected[transfer_id]


def _parse_track(payload, st):
    (num_gates,) = struct.unpack_from("<H", payload)
    payload = payload[2:]
    gates = {}; orients = {}
    for _ in range(num_gates):
        vals = struct.unpack_from("<Hfffffffff", payload)
        gate_id = vals[0]
        gates[gate_id] = np.array([vals[1], vals[2], vals[3]])             # pos_ned xyz
        orients[gate_id] = np.array([vals[4], vals[5], vals[6], vals[7]])  # orient quat [w,x,y,z] NED
        payload = payload[38:]
    st.gates = gates
    st.gate_orient = orients
    st.num_gates = num_gates
    print(f"  [TRACK] received {num_gates} gates", flush=True)


def load_vecnorm(path):
    with open(path, "rb") as f:
        vn = pickle.load(f)
    return vn.obs_rms, float(vn.clip_obs), float(vn.epsilon)


def build_obs(st, adapter):
    """Return (obs30, gate_pos_body, gate_dist, active) or None if no gate yet."""
    with st.lock:
        pos_ned = st.pos_ned.copy(); vel_ned = st.vel_ned.copy()
        q_ned = st.q_ned.copy(); omega = st.omega_body.copy()
        gates = dict(st.gates); num = st.num_gates; active = st.active_gate
    if not gates or active not in gates:
        return None
    pos = ned_to_zup_vec(pos_ned)
    vel = ned_to_zup_vec(vel_ned)
    q = ned_to_zup_quat(q_ned)
    q_conj = np.array([q[0], -q[1], -q[2], -q[3]])
    omega_flu = ned_to_zup_omega(omega)

    telem = Telemetry(position=pos, velocity=vel, orientation=q, angular_velocity=omega_flu)

    gate_zup = ned_to_zup_vec(gates[active])
    rel = gate_zup - pos
    gate_pos_body = quat_rotate_np(q_conj, rel)
    gate_dist = float(np.linalg.norm(rel))

    nxt = active + 1
    next_gate_pos_body = None
    gate_orient_body = None
    if nxt in gates:
        nxt_zup = ned_to_zup_vec(gates[nxt])
        next_gate_pos_body = quat_rotate_np(q_conj, nxt_zup - pos)
        # Fix #2 (obs-vs-training): training uses the gate's fly-through orientation,
        # not direction-to-gate. The sim ships a per-gate orientation quat (st.gate_orient)
        # but its local-normal convention is unverified offline; the course flow
        # (this gate -> next gate) is a convention-free proxy for the fly-through
        # direction. Exact-quat version is a Phase-1 task gated on a synthetic unit test.
        course_dir = nxt_zup - gate_zup
        n = np.linalg.norm(course_dir)
        if n > 1e-6:
            gate_orient_body = quat_rotate_np(q_conj, course_dir / n)

    obs = adapter.build_observation(telem, gate_pos_body, gate_dist, gate_orient_body, next_gate_pos_body)
    # Fix #1 (obs-vs-training): adapter hardcodes progress=0; training uses
    # current_gate / n_gates (index 17 of the 30-dim layout).
    obs[17] = float(active) / float(max(num, 1))
    return obs, gate_pos_body, gate_dist, active


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("secs", nargs="?", type=float, default=120.0)
    ap.add_argument("--dry-run", action="store_true", help="log obs+action, command NOTHING")
    ap.add_argument("--ckpt", default=None, help="path to a .zip checkpoint (vecnorm inferred as <ckpt>_vecnorm.pkl)")
    args = ap.parse_args()

    zip_path = args.ckpt or ZIP
    pkl_path = (zip_path[:-4] + "_vecnorm.pkl") if args.ckpt else PKL
    print(f"Loading policy {os.path.basename(zip_path)} ...", flush=True)
    model = PPO.load(zip_path)
    rms, clip, eps = load_vecnorm(pkl_path)
    adapter = CompetitionAdapter(command_rate_hz=CONTROL_HZ)
    print("Policy + VecNormalize loaded.", flush=True)

    print(f"Connecting udpin:{IP}:{PORT} ...", flush=True)
    conn = mavutil.mavlink_connection(f"udpin:{IP}:{PORT}")
    if conn.wait_heartbeat(timeout=10) is None:
        print("NO HEARTBEAT — abort.", flush=True); return
    print(f"HEARTBEAT OK. sys={conn.target_system} comp={conn.target_component}", flush=True)

    # Reset the sim course to a clean pre-race state (clears any prior/stalled race
    # so a fresh RACE press takes). MAVLINK_CMD_SIM_RESET = 31000 (from controller.py).
    conn.mav.command_long_send(conn.target_system, conn.target_component,
                               31000, 0, 0, 0, 0, 0, 0, 0, 0)
    print("Sim reset sent.", flush=True)
    time.sleep(0.5)

    st = SharedState()
    stop = threading.Event()
    threading.Thread(target=rx_loop, args=(conn, st, stop), daemon=True).start()

    # timesync 10 Hz
    def ts():
        while not stop.is_set():
            try: conn.mav.timesync_send(int(time.time_ns()), 0)
            except Exception: pass
            time.sleep(0.1)
    threading.Thread(target=ts, daemon=True).start()

    # arm (required before RACE engages)
    conn.mav.command_long_send(conn.target_system, conn.target_component,
                               mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0,
                               1, 0, 0, 0, 0, 0, 0)
    print("Arm sent. >>> PRESS RACE IN THE SIM NOW <<<", flush=True)
    print(f"Mode: {'DRY-RUN (no commands)' if args.dry_run else 'FLYING'} | {args.secs:.0f}s\n", flush=True)

    boot_ms = int(time.time() * 1000)
    dt = 1.0 / CONTROL_HZ
    t0 = time.time()
    last_log = 0.0
    last_active = -1
    steps = 0
    while time.time() - t0 < args.secs:
        loop_t = time.time()
        res = build_obs(st, adapter)
        if res is not None:
            obs, gpb, gdist, active = res
            if active != last_active:
                if last_active >= 0:
                    adapter.on_gate_passed()
                last_active = active
            obs_n = np.clip((obs - rms.mean) / np.sqrt(rms.var + eps), -clip, clip).astype(np.float32)
            action, _ = model.predict(obs_n, deterministic=True)
            ca = adapter.to_competition_action(action)
            rates_ned = zup_to_ned_rates(np.array([ca.roll_rate_rad_s, ca.pitch_rate_rad_s, ca.yaw_rate_rad_s]))
            steps += 1

            if not args.dry_run:
                conn.mav.set_attitude_target_send(
                    int(time.time() * 1000) - boot_ms,
                    conn.target_system, conn.target_component,
                    RATES_MASK, [1.0, 0.0, 0.0, 0.0],
                    float(rates_ned[0]), float(rates_ned[1]), float(rates_ned[2]),
                    float(ca.throttle))

            now = time.time() - t0
            if now - last_log >= 0.5:  # 2 Hz log
                last_log = now
                with st.lock:
                    started = st.race_started; num = st.num_gates
                g_body = obs[6:9]
                vel_body = obs[0:3]
                print(f"t={now:5.1f} race={started} gate={active}/{num} dist={gdist:5.1f}m "
                      f"| gate_body(F,L,U)=({gpb[0]:+.1f},{gpb[1]:+.1f},{gpb[2]:+.1f}) "
                      f"g_body=({g_body[0]:+.1f},{g_body[1]:+.1f},{g_body[2]:+.1f}) "
                      f"v_body=({vel_body[0]:+.1f},{vel_body[1]:+.1f},{vel_body[2]:+.1f}) "
                      f"| act thr={ca.throttle:.2f} r/p/y=({action[1]:+.2f},{action[2]:+.2f},{action[3]:+.2f})",
                      flush=True)
        else:
            now = time.time() - t0
            if now - last_log >= 1.0:
                last_log = now
                with st.lock:
                    started = st.race_started; num = st.num_gates; hp = st.have_pose
                print(f"t={now:5.1f} waiting... pose={hp} gates={num} race={started} "
                      f"(arm sent; press RACE to start gate stream)", flush=True)

        time.sleep(max(0.0, dt - (time.time() - loop_t)))

    stop.set()
    print(f"\nDone. control steps={steps}", flush=True)


if __name__ == "__main__":
    main()
