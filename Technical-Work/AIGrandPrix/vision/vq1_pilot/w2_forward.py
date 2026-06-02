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
KP_ATT, KP_YAW = 3.0, 1.5          # attitude / heading P gains (3.0 flew a controlled approach in run 2)
KALT, KVZ = 0.05, 0.06             # altitude hold — stronger (thrust frac per m, per m/s)
TILT = 0.06                        # VERY gentle forward lean (~3.4 deg) -> slow creep, tiny vert loss
SPEED_CAP = 2.5                    # m/s horizontal -> slow hover-forward
ALT_BAND = 1.5                     # m: if altitude error exceeds this, level off & recover first
DIST_STOP = 4.0
H_TARGET = 8.0                     # working altitude (margin + ~level with the ~7m-high gate)


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
    h = -pos[2]; vz_up = -vel[2]; alt_err = h_target - h
    hspeed = float(np.linalg.norm(vel[:2]))
    # heading toward gate (gentle)
    psi_des = math.atan2(d[1], d[0])
    yaw_rate_des = max(-1.0, min(1.0, KP_YAW * wrap(psi_des - yaw)))
    # ALTITUDE HAS PRIORITY: only lean forward when altitude is well-held, we're slow, and not close.
    alt_ok = abs(alt_err) < ALT_BAND
    ease = 1.0 if (alt_ok and hspeed < SPEED_CAP and hdist > 5.0) else 0.0
    pitch_des = tilt_sign * TILT * ease
    pitch_rate_des = max(-1.2, min(1.2, KP_ATT * (pitch_des - pitch)))
    roll_rate_des  = max(-1.2, min(1.2, KP_ATT * (0.0 - roll)))
    # collective: feed-forward tilt compensation (HOVER/vertical-fraction) + altitude PD damping
    vfrac = max(0.6, math.cos(roll) * math.cos(pitch))   # world-up component of body thrust
    thr = HOVER / vfrac + KALT*alt_err - KVZ*vz_up
    thr = max(0.18, min(0.42, thr))
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
    # patient liftoff + climb with PURE THRUST, zero rates (proven stable — the attitude
    # controller at release tumbled & dove). Gentle thrust just above hover to reach altitude.
    print(f"liftoff + climb to ~{H_TARGET:.0f} m (pure thrust, stable)...", flush=True)
    t_end = time.time() + 16.0; h = 0.0
    while time.time() < t_end:
        cmd_to(conn, boot, 0.34, 0, 0, 0)   # net ~+3.6 m/s^2 up; no attitude commands
        with st.lock: h = -st.pos[2]
        if h > H_TARGET - 1.5: break
        time.sleep(dt)
    if h < 1.0:
        print(f"  WARNING: still on pad (h={h:.2f}) — commands not taking; abort.", flush=True)
        stop.set(); return
    print(f"  at altitude (h={h:.1f} m); engaging attitude controller for creep.", flush=True)
    h0 = H_TARGET   # hold the working altitude for probe + creep (not the instantaneous value)
    print(f"holding for gate broadcast (target h={h0:.1f} m)...", flush=True)
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
    # slow forward hover (altitude-priority): creep toward the gate while holding altitude
    print("slow forward hover (altitude-priority)...", flush=True)
    t_end = time.time() + 18.0; last_print = 0.0
    while time.time() < t_end:
        thr, rr, pr, yr, dist = control_step(st, tilt_sign, h0)
        cmd_to(conn, boot, thr, rr, pr, yr)
        with st.lock: h = -st.pos[2]; sp = float(np.linalg.norm(st.vel[:2]))
        if h < 1.0:
            print(f"  altitude lost (h={h:.1f}m) — stopping early.", flush=True); break
        if time.time() - last_print > 2.0:
            dstr = f"{dist:5.1f}" if dist is not None else "  n/a"
            print(f"  h={h:4.1f}m  dist={dstr}m  hspeed={sp:4.1f} m/s", flush=True); last_print = time.time()
        time.sleep(dt)
    stop.set(); time.sleep(0.5)
    with st.lock: ng = st.num_gates
    print(f"\nDONE. frames+labels -> {outdir} (gates={ng}). Disarm/reset when ready.", flush=True)


if __name__ == "__main__":
    main()
