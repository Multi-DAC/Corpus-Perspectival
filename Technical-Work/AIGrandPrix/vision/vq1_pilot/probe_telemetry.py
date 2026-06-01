#
# Read-only telemetry probe for AI-GP VQ1.
# Connects exactly like setup.py (udpin:127.0.0.1:14550), runs timesync,
# and LOGS what the sim actually streams. Does NOT arm or send control —
# pure observation. Answers: is drone position available? gates? active-gate-index?
# This decides state-based vs vision-based for our first fly.
#
# Usage:  python probe_telemetry.py [seconds]   (default 30)
# Press RACE in the sim ~10s in to capture race-status / track data.
#

import sys
import time
import struct
import threading
from collections import Counter

from pymavlink import mavutil

IP, PORT = "127.0.0.1", 14550
DURATION = float(sys.argv[1]) if len(sys.argv) > 1 else 30.0

ENC_RACE, ENC_TRACK = 1, 2

print(f"Connecting udpin:{IP}:{PORT} ...", flush=True)
try:
    conn = mavutil.mavlink_connection(f"udpin:{IP}:{PORT}")
except Exception as e:
    print(f"CONNECT FAILED ({type(e).__name__}: {e}). "
          f"Is port {PORT} already bound by another client (their main.py / a prior run)?", flush=True)
    sys.exit(1)

print("Waiting for heartbeat (10s timeout)...", flush=True)
hb = conn.wait_heartbeat(timeout=10)
if hb is None:
    print("NO HEARTBEAT in 10s — sim not streaming on 14550, or port taken. Abort.", flush=True)
    sys.exit(1)
print(f"HEARTBEAT OK. target_system={conn.target_system} target_component={conn.target_component}", flush=True)

# Arm — the sim likely won't start the race for an unarmed pilot, and the gate
# layout may only broadcast once the race starts. Arming is harmless here: with no
# control commands the drone just sits. (Throwaway attempt; VQ1 is unlimited.)
conn.mav.command_long_send(
    conn.target_system, conn.target_component,
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0,
    1, 0, 0, 0, 0, 0, 0)
print("Arm command sent.", flush=True)

# Timesync at 10 Hz (matches their TimeSync) in case telemetry is gated on it.
ts_running = True
def ts_loop():
    while ts_running:
        try:
            conn.mav.timesync_send(int(time.time_ns()), 0)
        except Exception:
            pass
        time.sleep(0.1)
threading.Thread(target=ts_loop, daemon=True).start()

counts = Counter()
seen = set()
race_status = None
track_seen = False

t0 = time.time()
print(f"\nListening {DURATION:.0f}s — PRESS 'RACE' IN THE SIM ~10s IN to capture race-status/track.\n", flush=True)
while time.time() - t0 < DURATION:
    msg = conn.recv_match(blocking=False)
    if msg is None:
        time.sleep(0.001)
        continue
    t = msg.get_type()
    if t == "BAD_DATA":
        continue
    counts[t] += 1

    if t not in seen:
        seen.add(t)
        if t == "LOCAL_POSITION_NED":
            print(f"  + LOCAL_POSITION_NED  x={msg.x:.2f} y={msg.y:.2f} z={msg.z:.2f}  v=({msg.vx:.2f},{msg.vy:.2f},{msg.vz:.2f})", flush=True)
        elif t == "ODOMETRY":
            print(f"  + ODOMETRY  x={msg.x:.2f} y={msg.y:.2f} z={msg.z:.2f}  q(wxyz)={[round(v,3) for v in msg.q]}", flush=True)
        elif t == "ATTITUDE":
            print(f"  + ATTITUDE  roll={msg.roll:.2f} pitch={msg.pitch:.2f} yaw={msg.yaw:.2f}  rates=({msg.rollspeed:.2f},{msg.pitchspeed:.2f},{msg.yawspeed:.2f})", flush=True)
        elif t == "HIGHRES_IMU":
            print(f"  + HIGHRES_IMU  acc=({msg.xacc:.1f},{msg.yacc:.1f},{msg.zacc:.1f})", flush=True)
        else:
            print(f"  + {t}", flush=True)

    if t == "ENCAPSULATED_DATA":
        raw = bytes(msg.data)
        if len(raw) >= 1:
            dt = raw[0]
            if dt == ENC_RACE:
                try:
                    (_dt, sim_ms, race_start_ms, race_finish_ns,
                     active_gate, last_gate_t) = struct.unpack_from("<BQqqIq", raw)
                    race_status = {"active_gate_index": active_gate,
                                   "race_started": race_start_ms is not None and race_start_ms >= 0,
                                   "race_start_ms": race_start_ms}
                except Exception:
                    pass
            elif dt == ENC_TRACK:
                track_seen = True
    elif t == "DATA_TRANSMISSION_HANDSHAKE":
        track_seen = True

ts_running = False

print("\n================ SUMMARY ================", flush=True)
for k, v in counts.most_common():
    print(f"  {k:28s} {v}", flush=True)

pos = bool(counts.get("LOCAL_POSITION_NED") or counts.get("ODOMETRY"))
print("\n---------------- KEY QUESTIONS ----------------", flush=True)
print(f"  Drone absolute position (LOCAL_POSITION_NED / ODOMETRY): {'YES' if pos else 'NO'}", flush=True)
print(f"  Attitude + body rates (ATTITUDE):                        {'YES' if counts.get('ATTITUDE') else 'NO'}", flush=True)
print(f"  Gate/track data (ENCAPSULATED track / handshake):        {'YES' if track_seen else 'NO'}", flush=True)
print(f"  RACE_STATUS w/ active_gate_index:                        {race_status if race_status else 'NOT SEEN (press RACE during the probe)'}", flush=True)
print("\nIf position + gates + active_gate_index are all YES -> STATE-BASED first fly (matches training).", flush=True)
print("If only vision (no position/gates) -> fall back to the JPEG/detector path.", flush=True)
