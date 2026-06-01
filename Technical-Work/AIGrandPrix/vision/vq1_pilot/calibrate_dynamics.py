#
# Phase-0 system-ID probe for AI-GP VQ1.
#
# Drives the sim with a fixed schedule of KNOWN set_attitude_target inputs and
# logs the ODOMETRY response, so we can fit drone_env_v2's params (mass / T_max,
# body-rate response, drag) to match the competition sim. Commands are in the
# sim's NATIVE frame (raw NED body rates + thrust) — we characterize the sim as
# it is, then map to our sim offline.
#
# Output: calib_log.csv  (t, cmd_thr, cmd_r, cmd_p, cmd_y, px,py,pz, vx,vy,vz,
#                          qw,qx,qy,qz, wr,wp,wy)
#
# Usage:  python calibrate_dynamics.py
#   Arms, waits for you to press RACE, then runs the schedule (~20s) and logs.
#   Throwaway attempt (VQ1 unlimited). The drone WILL move — that's the point.
#
import time, struct, threading, csv
from pymavlink import mavutil

IP, PORT = "127.0.0.1", 14550
HZ = 100.0
RATES_MASK = mavutil.mavlink.ATTITUDE_TARGET_TYPEMASK_ATTITUDE_IGNORE

# Schedule: (label, duration_s, thrust[0-1], roll_rad_s, pitch_rad_s, yaw_rad_s)
# Refine after first run. Hover thrust unknown until thrust-ramp identifies it.
SCHEDULE = [
    ("settle",      2.0, 0.00, 0.0, 0.0, 0.0),   # baseline on pad
    ("thr_0p5",     2.0, 0.50, 0.0, 0.0, 0.0),   # below/near hover
    ("thr_0p7",     2.0, 0.70, 0.0, 0.0, 0.0),   # above hover -> vertical accel => mass/T_max
    ("thr_0p9",     1.5, 0.90, 0.0, 0.0, 0.0),   # strong climb
    ("roll_step",   1.5, 0.60, 4.0, 0.0, 0.0),   # body-rate tracking (roll)
    ("pitch_step",  1.5, 0.60, 0.0, 4.0, 0.0),   # pitch
    ("yaw_step",    1.5, 0.60, 0.0, 0.0, 1.0),   # yaw
    ("coast",       3.0, 0.55, 0.0, 0.0, 0.0),   # near-hover coast => drag/decay
]

state = {"pos": [0,0,0], "vel": [0,0,0], "q": [1,0,0,0], "w": [0,0,0], "have": False}
lock = threading.Lock()
stop = threading.Event()

def rx(conn):
    while not stop.is_set():
        m = conn.recv_match(blocking=False)
        if m is None:
            time.sleep(0.0005); continue
        if m.get_type() == "ODOMETRY":
            with lock:
                state["pos"] = [m.x, m.y, m.z]
                state["vel"] = [m.vx, m.vy, m.vz]
                state["q"]   = [m.q[0], m.q[1], m.q[2], m.q[3]]
                state["w"]   = [m.rollspeed, m.pitchspeed, m.yawspeed]
                state["have"] = True

def main():
    print(f"Connecting udpin:{IP}:{PORT} ...", flush=True)
    conn = mavutil.mavlink_connection(f"udpin:{IP}:{PORT}")
    if conn.wait_heartbeat(timeout=10) is None:
        print("NO HEARTBEAT — abort."); return
    print(f"HEARTBEAT OK sys={conn.target_system}", flush=True)
    conn.mav.command_long_send(conn.target_system, conn.target_component, 31000, 0, 0,0,0,0,0,0,0)
    time.sleep(0.5)
    threading.Thread(target=rx, args=(conn,), daemon=True).start()
    def ts():
        while not stop.is_set():
            try: conn.mav.timesync_send(int(time.time_ns()), 0)
            except Exception: pass
            time.sleep(0.1)
    threading.Thread(target=ts, daemon=True).start()
    conn.mav.command_long_send(conn.target_system, conn.target_component,
                               mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1,0,0,0,0,0,0)
    print("Armed. >>> PRESS RACE NOW <<< (schedule starts in 5s regardless)", flush=True)
    time.sleep(5.0)

    boot = int(time.time()*1000)
    dt = 1.0/HZ
    rows = []
    t0 = time.time()
    for label, dur, thr, r, p, y in SCHEDULE:
        print(f"  segment: {label} thr={thr} rpy=({r},{p},{y}) for {dur}s", flush=True)
        seg_end = time.time() + dur
        while time.time() < seg_end:
            lt = time.time()
            conn.mav.set_attitude_target_send(
                int(time.time()*1000)-boot, conn.target_system, conn.target_component,
                RATES_MASK, [1.0,0.0,0.0,0.0], float(r), float(p), float(y), float(thr))
            with lock:
                s = (state["pos"][:], state["vel"][:], state["q"][:], state["w"][:])
            rows.append([round(time.time()-t0,4), thr, r, p, y, *s[0], *s[1], *s[2], *s[3]])
            time.sleep(max(0.0, dt-(time.time()-lt)))
    stop.set()
    out = "calib_log.csv"
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t","cmd_thr","cmd_r","cmd_p","cmd_y","px","py","pz","vx","vy","vz","qw","qx","qy","qz","wr","wp","wy"])
        w.writerows(rows)
    print(f"\nDone. {len(rows)} samples -> {out}", flush=True)

if __name__ == "__main__":
    main()
