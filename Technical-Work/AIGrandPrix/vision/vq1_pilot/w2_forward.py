#
# W2 forward-approach capture: fly a CONTROLLED approach toward the active gate so the
# camera gets close, gate-growing frames (better detector data than the drift run).
# Also a live validation of the W1 calibration: uses the measured transform send = w/G
# (G_rp=-2.56, G_yaw=-2.40) inside a minimal attitude+altitude+heading feedback loop.
# Conservative: speed-capped, altitude-held, can't fly away. Throwaway (VQ1 unlimited).
#
import os, sys, time, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from w1w2_live import St, rx_loop, frame_loop, send, HZ, IP, PORT
from pymavlink import mavutil
import threading

# W1-calibrated command transform: measured_rate = G * sent  ->  send = rate_des / G
G_RP, G_YAW = -2.56, -2.40
HOVER = 0.26
KP_ATT, KP_YAW = 3.0, 2.0          # attitude / heading P gains (rate response is ~unit after /G)
KALT, KVZ = 0.020, 0.020           # altitude hold (thrust frac per m, per m/s)
TILT = 0.16                        # forward tilt magnitude (rad, ~9 deg) -> gentle approach
SPEED_CAP = 7.0                    # m/s horizontal; above this, level off
DIST_STOP = 3.0                    # m to active gate -> consider it reached


def angles_from_q(q):
    w, x, y, z = q
    roll = math.atan2(2*(w*x + y*z), 1 - 2*(x*x + y*y))
    pitch = math.asin(max(-1, min(1, 2*(w*y - z*x))))
    yaw = math.atan2(2*(w*z + x*y), 1 - 2*(y*y + z*z))
    return roll, pitch, yaw


def wrap(a):
    return (a + math.pi) % (2*math.pi) - math.pi


def cmd_to(conn, boot, thr, roll_rate, pitch_rate, yaw_rate):
    RATES_MASK = mavutil.mavlink.ATTITUDE_TARGET_TYPEMASK_ATTITUDE_IGNORE
    conn.mav.set_attitude_target_send(int(time.time()*1000)-boot, conn.target_system,
        conn.target_component, RATES_MASK, [1.0,0,0,0],
        float(roll_rate), float(pitch_rate), float(yaw_rate), float(thr))


def control_step(st, tilt_sign, h_target):
    """Return (thr, roll_send, pitch_send, yaw_send, dist) for one step."""
    with st.lock:
        pos = st.pos.copy(); vel = st.vel.copy(); q = st.q.copy()
        gates = dict(st.gates); active = st.active_gate
    g = gates.get(active) or gates.get(0)
    if g is None:
        return HOVER, 0.0, 0.0, 0.0, None
    g = np.array(g, dtype=float)
    d = g[:2] - pos[:2]; dist = float(np.linalg.norm(g - pos)); hdist = float(np.linalg.norm(d))
    roll, pitch, yaw = angles_from_q(q)
    # heading toward gate
    psi_des = math.atan2(d[1], d[0])
    yaw_rate_des = max(-1.5, min(1.5, KP_YAW * wrap(psi_des - yaw)))
    # forward tilt toward gate, easing off when close or too fast
    hspeed = float(np.linalg.norm(vel[:2]))
    ease = 0.0 if (hdist < 4.0 or hspeed > SPEED_CAP) else 1.0
    pitch_des = tilt_sign * TILT * ease
    pitch_rate_des = max(-1.5, min(1.5, KP_ATT * (pitch_des - pitch)))
    roll_rate_des = max(-1.5, min(1.5, KP_ATT * (0.0 - roll)))
    # altitude hold (h = -z up)
    h = -pos[2]; vz_up = -vel[2]
    thr = HOVER + KALT*(h_target - h) - KVZ*vz_up
    thr = max(0.18, min(0.45, thr))
    # calibrated transform: send = rate_des / G
    return thr, roll_rate_des/G_RP, pitch_rate_des/G_RP, yaw_rate_des/G_YAW, dist


def main():
    stamp = time.strftime("%Y%m%d_%H%M%S")
    outdir = os.path.join(HERE, f"w2_forward_{stamp}")
    print(f"Connecting udpin:{IP}:{PORT} ...", flush=True)
    conn = mavutil.mavlink_connection(f"udpin:{IP}:{PORT}")
    if conn.wait_heartbeat(timeout=10) is None:
        print("NO HEARTBEAT — abort."); return
    print(f"HEARTBEAT sys={conn.target_system}", flush=True)
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
    print("Armed + reset. Waiting for RACE to actually start (commands only take when racing)...", flush=True)
    tw = time.time(); prompted = False
    while time.time() - tw < 60:
        with st.lock: ok = st.race_started   # the REAL race-active signal (not mere telemetry)
        if ok: break
        if not prompted and time.time()-tw > 4:
            print("\n  >>> PRESS RACE IN THE SIM NOW (reset to the pilot screen first if needed) <<<\n", flush=True)
            prompted = True
        time.sleep(0.2)
    with st.lock: ok = st.race_started
    if not ok:
        print("Race never started (race_started=False) — abort, no blind commands."); stop.set(); return
    print("RACE LIVE (race_started=True).", flush=True)

    boot = int(time.time()*1000); dt = 1.0/HZ
    # THROTTLE-DOWN GATE (Clayton's finding 2026-06-01): the sim shows "THROTTLE DOWN please"
    # and pins the drone if thrust is commanded before the countdown releases. Hold thrust=0
    # (idle on pad) for a few seconds to satisfy the gate / let the start release. This is why
    # run-1 flew (it opened with a thr=0 settle) and the thrust-first runs did not.
    print("throttle-idle settle (satisfy THROTTLE-DOWN gate)...", flush=True)
    t_end = time.time() + 3.0
    while time.time() < t_end:
        cmd_to(conn, boot, 0.0, 0, 0, 0); time.sleep(dt)
    # patient liftoff: apply thrust and WAIT for climb (countdown/hold can persist a moment).
    print("liftoff (patient — waiting past any countdown hold)...", flush=True)
    t_end = time.time() + 12.0; h_after = 0.0
    while time.time() < t_end:
        cmd_to(conn, boot, 0.42, 0,0,0)
        with st.lock: h_after = -st.pos[2]
        if h_after > 2.0: break
        time.sleep(dt)
    if h_after < 1.0:
        print(f"  WARNING: still on pad after 12s (h={h_after:.2f}) — commands not taking; abort.", flush=True)
        stop.set(); return
    print(f"  airborne (h={h_after:.1f} m after {time.time()-(t_end-12.0):.1f}s).", flush=True)
    # wait for gates (broadcast ~30s after race start); hold altitude meanwhile
    with st.lock: h0 = -st.pos[2]
    print(f"holding for gate broadcast (h0={h0:.1f} m)...", flush=True)
    t_end = time.time() + 35.0
    while time.time() < t_end:
        with st.lock: have = st.num_gates > 0
        thr,_,_,_,_ = control_step(st, +1, h0)  # hold alt, no tilt yet
        cmd_to(conn, boot, thr, 0,0,0)
        if have: print("  gates present — beginning approach.", flush=True); break
        time.sleep(dt)
    # probe forward-tilt sign (1.2s)
    with st.lock: d_start = None
    def cur_dist():
        with st.lock:
            g = st.gates.get(st.active_gate) or st.gates.get(0)
            return None if g is None else float(np.linalg.norm(np.array(g)-st.pos))
    d0 = cur_dist(); print(f"probe (+tilt), dist0={d0}", flush=True)
    t_end = time.time() + 1.2
    while time.time() < t_end:
        thr, rr, pr, yr, _ = control_step(st, +1, h0); cmd_to(conn, boot, thr, rr, pr, yr); time.sleep(dt)
    d1 = cur_dist()
    tilt_sign = +1 if (d0 and d1 and d1 < d0) else -1
    print(f"  dist1={d1} -> tilt_sign={tilt_sign}", flush=True)
    # approach cruise (up to 20 s, stop when close)
    print("approach...", flush=True)
    t_end = time.time() + 20.0
    while time.time() < t_end:
        thr, rr, pr, yr, dist = control_step(st, tilt_sign, h0)
        cmd_to(conn, boot, thr, rr, pr, yr)
        if dist is not None and dist < DIST_STOP:
            print(f"  reached active gate (dist={dist:.1f}); continuing to next.", flush=True)
        time.sleep(dt)
    stop.set(); time.sleep(0.5)
    with st.lock: ng = st.num_gates
    print(f"\nDONE. frames+labels -> {outdir} (gates={ng}). Disarm/reset when ready.", flush=True)


if __name__ == "__main__":
    main()
