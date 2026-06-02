#
# W1 + W2 combined live session against the AI-GP VQ1 sim (ROADMAP_v3).
#
# W1 (calibration): a GENTLE schedule of small, non-diverging set_attitude_target rate
#   steps at ~hover thrust, logging cmd vs ODOMETRY response -> per-axis rate gain+sign
#   and yaw limit (the divergence-free read CALIB_FIT could not get), + a coast for drag.
# W2 (auto-label): the practice sim LEAKS ODOMETRY + gate poses. We log, per received
#   camera frame (UDP 5600), the concurrent ego-state + all gate poses -> a perfectly
#   labeled perception dataset on the real competition renderer. Deploy uses detector-only.
#
# Commands are RAW native rates (no sign conversion) — we characterize the sim as-is.
# One race, ~70s, throwaway (VQ1 unlimited attempts). The drone WILL move.
#
import os, sys, time, struct, threading, csv, json, socket
import numpy as np
from pymavlink import mavutil

HERE = os.path.dirname(os.path.abspath(__file__))
IP, PORT = "127.0.0.1", 14550
VPORT = 5600
HZ = 100.0
ENC_RACE, ENC_TRACK = 1, 2
RATES_MASK = mavutil.mavlink.ATTITUDE_TARGET_TYPEMASK_ATTITUDE_IGNORE
HFMT = "<IHHIIQ"; HSZ = struct.calcsize(HFMT)

# W1 gentle schedule: (label, dur_s, thr[0-1], roll, pitch, yaw)  rates rad/s, RAW native.
HOVER = 0.26  # ~1/TWR(3.85) from CALIB_FIT
SCHEDULE = [
    ("settle",   1.5, 0.00, 0,0,0),
    ("liftoff",  2.0, 0.34, 0,0,0),     # gentle climb off the pad
    ("hover",    1.5, HOVER,0,0,0),
    ("roll+",    0.6, HOVER, 0.6,0,0),  # small steps -> non-diverging gain read
    ("hover1",   0.9, HOVER,0,0,0),
    ("roll-",    0.6, HOVER,-0.6,0,0),
    ("hover2",   0.9, HOVER,0,0,0),
    ("pitch+",   0.6, HOVER,0, 0.6,0),
    ("hover3",   0.9, HOVER,0,0,0),
    ("pitch-",   0.6, HOVER,0,-0.6,0),
    ("hover4",   0.9, HOVER,0,0,0),
    ("yaw+",     0.6, HOVER,0,0, 1.0),
    ("hover5",   0.9, HOVER,0,0,0),
    ("yaw-",     0.6, HOVER,0,0,-1.0),
    ("hover6",   0.9, HOVER,0,0,0),
    ("roll_big", 0.6, HOVER, 1.5,0,0),  # linearity check (still small)
    ("hover7",   0.9, HOVER,0,0,0),
    ("coast",    2.5, 0.30, 0,0,0),     # drag / decay
]
CAPTURE_DRIFT_S = 45.0   # W2 phase after W1 (gates broadcast ~30s after race start)


class St:
    def __init__(self):
        self.lock = threading.Lock()
        self.pos = np.zeros(3); self.vel = np.zeros(3)
        self.q = np.array([1.,0,0,0]); self.w = np.zeros(3)
        self.have_pose = False
        self.gates = {}; self.gate_orient = {}
        self.num_gates = 0; self.active_gate = 0; self.race_started = False
        self._chunks = {}; self._expected = {}


def rx_loop(conn, st, stop):
    while not stop.is_set():
        try: msg = conn.recv_match(blocking=False)
        except ConnectionResetError: return
        if msg is None: time.sleep(0.0005); continue
        t = msg.get_type()
        if t == "ODOMETRY":
            with st.lock:
                st.pos = np.array([msg.x, msg.y, msg.z]); st.vel = np.array([msg.vx, msg.vy, msg.vz])
                st.q = np.array([msg.q[0], msg.q[1], msg.q[2], msg.q[3]])
                st.w = np.array([msg.rollspeed, msg.pitchspeed, msg.yawspeed]); st.have_pose = True
        elif t == "DATA_TRANSMISSION_HANDSHAKE":
            with st.lock: st._chunks[msg.width] = {}; st._expected[msg.width] = msg.packets
        elif t == "ENCAPSULATED_DATA":
            raw = bytes(msg.data)
            if not raw: continue
            if raw[0] == ENC_RACE:
                try:
                    (_d,_s,rs,_f,active,_l) = struct.unpack_from("<BQqqIq", raw)
                    with st.lock: st.active_gate = int(active); st.race_started = rs is not None and rs >= 0
                except struct.error: pass
            elif raw[0] == ENC_TRACK:
                _d, tid = struct.unpack_from("<BH", raw)
                with st.lock:
                    if tid in st._expected:
                        st._chunks[tid][msg.seqnr] = raw[3:]
                        if len(st._chunks[tid]) == st._expected[tid]:
                            payload = b"".join(st._chunks[tid][i] for i in range(st._expected[tid]))
                            _parse_track(payload, st); del st._chunks[tid]; del st._expected[tid]


def _parse_track(payload, st):
    (ng,) = struct.unpack_from("<H", payload); payload = payload[2:]
    g={}; o={}
    for _ in range(ng):
        v = struct.unpack_from("<Hfffffffff", payload)
        g[v[0]] = [v[1],v[2],v[3]]; o[v[0]] = [v[4],v[5],v[6],v[7]]; payload = payload[38:]
    st.gates = g; st.gate_orient = o; st.num_gates = ng
    print(f"  [TRACK] {ng} gates received", flush=True)


def frame_loop(st, stop, outdir):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); sock.settimeout(1.0)
        sock.bind(("0.0.0.0", VPORT))
    except OSError as e:
        print(f"  [W2] UDP {VPORT} bind failed ({e}); frames disabled (W1 still runs).", flush=True)
        return
    os.makedirs(os.path.join(outdir, "frames"), exist_ok=True)
    lbl = open(os.path.join(outdir, "labels.jsonl"), "w")
    frames = {}; saved = 0
    from collections import deque
    done = set(); done_q = deque()   # skip retransmitted/duplicate completed frames
    while not stop.is_set():
        try: pkt, _ = sock.recvfrom(65536)
        except socket.timeout: continue
        if len(pkt) < HSZ: continue
        fid, cid, tot, jsize, psize, t_ns = struct.unpack(HFMT, pkt[:HSZ])
        if fid in done: continue
        f = frames.setdefault(fid, {})
        f[cid] = pkt[HSZ:]
        if len(f) == tot and all(i in f for i in range(tot)):
            jpeg = b"".join(f[i] for i in range(tot))
            with st.lock:
                rec = {"frame_id": int(fid), "sim_time_ns": int(t_ns),
                       "ego": {"pos_ned": st.pos.tolist(), "vel_ned": st.vel.tolist(),
                               "q_ned": st.q.tolist(), "omega": st.w.tolist()},
                       "gates": {int(k): v for k, v in st.gates.items()},
                       "gate_orient": {int(k): v for k, v in st.gate_orient.items()},
                       "active_gate": int(st.active_gate), "num_gates": int(st.num_gates)}
            open(os.path.join(outdir, "frames", f"f{fid:06d}.jpg"), "wb").write(jpeg)
            lbl.write(json.dumps(rec) + "\n"); lbl.flush()
            saved += 1
            if saved % 60 == 0:
                print(f"  [W2] {saved} frames captured ({rec['num_gates']} gates labeled)", flush=True)
            del frames[fid]
            done.add(fid); done_q.append(fid)
            if len(done_q) > 4096: done.discard(done_q.popleft())
    lbl.close(); sock.close()
    print(f"  [W2] done, {saved} labeled frames -> {outdir}", flush=True)


def send(conn, boot, thr, r, p, y):
    conn.mav.set_attitude_target_send(int(time.time()*1000)-boot, conn.target_system,
        conn.target_component, RATES_MASK, [1.0,0,0,0], float(r), float(p), float(y), float(thr))


def main():
    stamp = time.strftime("%Y%m%d_%H%M%S")
    outdir = os.path.join(HERE, f"w2_dataset_{stamp}")
    print(f"Connecting udpin:{IP}:{PORT} ...", flush=True)
    conn = mavutil.mavlink_connection(f"udpin:{IP}:{PORT}")
    if conn.wait_heartbeat(timeout=10) is None:
        print("NO HEARTBEAT — is the sim at the pilot screen? abort."); return
    print(f"HEARTBEAT OK sys={conn.target_system}", flush=True)
    st = St(); stop = threading.Event()
    conn.mav.command_long_send(conn.target_system, conn.target_component, 31000, 0, 0,0,0,0,0,0,0)
    time.sleep(0.4)
    threading.Thread(target=rx_loop, args=(conn, st, stop), daemon=True).start()
    threading.Thread(target=frame_loop, args=(st, stop, outdir), daemon=True).start()
    def ts():
        while not stop.is_set():
            try: conn.mav.timesync_send(int(time.time_ns()), 0)
            except Exception: pass
            time.sleep(0.1)
    threading.Thread(target=ts, daemon=True).start()
    conn.mav.command_long_send(conn.target_system, conn.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1,0,0,0,0,0,0)
    print("Armed + reset sent. Waiting for race to start (telemetry/gates stream once racing)...", flush=True)

    # race-start detection (auto if reset engaged it; else prompt)
    t_wait = time.time(); prompted = False
    while time.time() - t_wait < 45:
        with st.lock: started = st.race_started or st.have_pose
        if started: break
        if not prompted and time.time() - t_wait > 6:
            print("\n  >>> If the race hasn't started, PRESS RACE IN THE SIM NOW <<<\n", flush=True)
            prompted = True
        time.sleep(0.2)
    with st.lock: started = st.race_started or st.have_pose
    if not started:
        print("Race did not start within 45s — abort (no telemetry)."); stop.set(); return
    print(f"RACE LIVE (race_started={st.race_started}, pose={st.have_pose}). Running W1 schedule.", flush=True)

    # ---- W1: gentle calibration schedule ----
    boot = int(time.time()*1000); dt = 1.0/HZ; rows = []; t0 = time.time()
    for label, dur, thr, r, p, y in SCHEDULE:
        print(f"  W1 {label}: thr={thr} rpy=({r},{p},{y}) {dur}s", flush=True)
        end = time.time() + dur
        while time.time() < end:
            lt = time.time(); send(conn, boot, thr, r, p, y)
            with st.lock: s = (st.pos.tolist(), st.vel.tolist(), st.q.tolist(), st.w.tolist())
            rows.append([round(time.time()-t0,4), thr, r, p, y, *s[0], *s[1], *s[2], *s[3]])
            time.sleep(max(0.0, dt-(time.time()-lt)))
    calib = os.path.join(outdir, "calib_log_w1.csv"); os.makedirs(outdir, exist_ok=True)
    with open(calib, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t","cmd_thr","cmd_r","cmd_p","cmd_y","px","py","pz","vx","vy","vz","qw","qx","qy","qz","wr","wp","wy"])
        w.writerows(rows)
    print(f"  W1 done: {len(rows)} samples -> {calib}", flush=True)

    # ---- W2 capture-drift: gentle near-hover + slow yaw sweep, keep capturing labeled frames ----
    print(f"  W2 capture-drift {CAPTURE_DRIFT_S}s (gentle yaw sweep; gates arrive ~30s in)...", flush=True)
    end = time.time() + CAPTURE_DRIFT_S; boot2 = int(time.time()*1000); k = 0
    while time.time() < end:
        lt = time.time()
        yaw = 0.4 * np.sin(2*np.pi*(time.time()-(end-CAPTURE_DRIFT_S))/8.0)  # slow ±0.4 sweep
        send(conn, boot2, HOVER, 0.0, 0.0, float(yaw)); k += 1
        time.sleep(max(0.0, dt-(time.time()-lt)))
    stop.set(); time.sleep(0.5)
    with st.lock: ng = st.num_gates
    print(f"\nSESSION DONE. calib={calib}\n  W2 dataset -> {outdir} (gates seen: {ng})", flush=True)
    print("Disarm/reset the sim when ready.", flush=True)


if __name__ == "__main__":
    main()
