#
# Anakin VISION pilot for AI-GP VQ1 — DreamerV3 band-ft best.pt (+421.91 exam-cond).
#
# First flight of the from-pixels policy in the OFFICIAL sim (Day 130, 2026-06-10).
# Splices integration/dreamer_pilot.py (the sim-to-sim translation adapter, rehearsal
# gate PASSED: roundtrip +36.1% vs direct) into the official UDP interfaces:
#
#   UDP:5600 JPEG camera (640x360@30Hz) -> latest-frame buffer
#     -> DreamerPilot.act(frame_bgr)            (geometry-preserving 64x64, stateful RSSM)
#     -> to_competition_action                  (SIM constants: OMEGA_XY/OMEGA_Z, crux #3)
#     -> FLU->FRD rate flip (proven, state_pilot.py verbatim)
#     -> SET_ATTITUDE_TARGET (body rates rad/s + throttle), frame-driven (~30 Hz)
#
# Usage:
#   .venv python run_dreamer.py --dry-run [secs]   # Stage 1: frames+actions logged, command NOTHING
#   .venv python run_dreamer.py [secs]             # Stage 2: FLY
#   (anakin .venv python — has torch + cv2 + pymavlink:
#    C:\Users\mercu\clawd\repo-staging\Corpus-Perspectival\Technical-Work\AIGrandPrix\anakin\.venv\Scripts\python.exe)
#
# Press RACE in the sim after "Arm sent". LIVE-TEST CHECKLIST (dreamer_pilot docstring):
#   tilt: RESOLVED Day 129 (render.py now 20deg UP per spec; HUD shows cam 20)
#   handedness: FLU->FRD flip applied below (state_pilot-proven)
#   thrust: WATCH on first flight — pinned-to-floor/ceiling = TWR mismatch
#   frame-rate: act() is frame-driven at the feed's 30 Hz; RSSM holds state between frames
#

import os
import socket
import struct
import sys
import threading
import time
import argparse

import numpy as np
from pymavlink import mavutil

ANAKIN = r"C:\Users\mercu\clawd\repo-staging\Corpus-Perspectival\Technical-Work\AIGrandPrix\anakin"
sys.path.insert(0, os.path.join(ANAKIN, "integration"))
from dreamer_pilot import DreamerPilot, to_competition_action, to_training_frame  # noqa: E402

# Default = the RESTYLE fine-tune best.pt (flight #2, Day 131+). Override with
# --checkpoint for A/B flights (e.g. the pre-restyle band-ft best.pt).
CKPT = os.path.join(ANAKIN, "third_party", "dreamerv3-torch", "logdir",
                    "maneuver_restyle_ft", "best.pt")

IP, PORT = "127.0.0.1", 14550
VISION_IP, VISION_PORT = "0.0.0.0", 5600
RATES_MASK = mavutil.mavlink.ATTITUDE_TARGET_TYPEMASK_ATTITUDE_IGNORE
ENC_RACE, ENC_TRACK = 1, 2  # ENCAPSULATED_DATA payload types (state_pilot.py)
FRAME_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "flight_frames")
SAVE_EVERY = 5      # save every Nth consumed frame (raw + 64x64 policy view)
SAVE_CAP = 400      # max saved pairs per run

def zup_to_ned_rates(r):    # body rates FLU->FRD for sending (state_pilot.py verbatim)
    return np.array([r[0], -r[1], -r[2]])


class LatestFrame:
    """UDP:5600 chunked-JPEG receiver keeping only the newest decoded BGR frame.
    Protocol verbatim from the official vision_rx.py; storage added."""

    def __init__(self):
        import cv2
        self._cv2 = cv2
        self.lock = threading.Lock()
        self.frame = None
        self.frame_id = -1
        self.count = 0
        self.stop = threading.Event()
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def get(self):
        with self.lock:
            return (self.frame, self.frame_id)

    def _loop(self):
        header_format = "<IHHIIQ"
        header_sz = struct.calcsize(header_format)
        frames = {}
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1.0)
        sock.bind((VISION_IP, VISION_PORT))
        print("Listening for camera frames on UDP:5600 ...", flush=True)
        while not self.stop.is_set():
            try:
                packet, _ = sock.recvfrom(65536)
            except socket.timeout:
                continue
            header = packet[:header_sz]
            payload = packet[header_sz:]
            frame_id, chunk_id, total_chunks, jpeg_size, payload_size, t_ns = \
                struct.unpack(header_format, header)
            if frame_id not in frames:
                frames[frame_id] = {"chunks": {}, "total": total_chunks}
            frames[frame_id]["chunks"][chunk_id] = payload
            if len(frames[frame_id]["chunks"]) == total_chunks:
                jpeg = bytearray()
                ok = True
                for i in range(total_chunks):
                    if i not in frames[frame_id]["chunks"]:
                        ok = False
                        break
                    jpeg.extend(frames[frame_id]["chunks"][i])
                if ok:
                    img = self._cv2.imdecode(
                        np.frombuffer(jpeg, dtype=np.uint8), self._cv2.IMREAD_COLOR)
                    if img is not None:
                        with self.lock:
                            self.frame = img
                            self.frame_id = frame_id
                            self.count += 1
                del frames[frame_id]
                # drop stale partial frames so the dict can't grow unbounded
                if len(frames) > 8:
                    for k in sorted(frames)[:-4]:
                        del frames[k]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("secs", nargs="?", type=float, default=120.0)
    ap.add_argument("--dry-run", action="store_true",
                    help="log frames+actions, command NOTHING")
    ap.add_argument("--checkpoint", default=CKPT,
                    help="DreamerV3 checkpoint to fly (default: restyle-ft best.pt)")
    ap.add_argument("--start-delay", type=float, default=3.0,
                    help="seconds after the race signal before commanding "
                         "(the sim runs a 3s countdown; commanding early = DQ). "
                         "During the delay the RSSM watches frames but sends nothing.")
    args = ap.parse_args()

    print(f"Loading DreamerPilot from {args.checkpoint} ...", flush=True)
    pilot = DreamerPilot(args.checkpoint)
    pilot.reset()
    print("Pilot loaded.", flush=True)

    vision = LatestFrame()

    print(f"Connecting udpin:{IP}:{PORT} ...", flush=True)
    conn = mavutil.mavlink_connection(f"udpin:{IP}:{PORT}")
    if conn.wait_heartbeat(timeout=10) is None:
        print("NO HEARTBEAT — is the sim running? abort.", flush=True)
        return
    print(f"HEARTBEAT OK. sys={conn.target_system} comp={conn.target_component}",
          flush=True)

    # Clean pre-race state (MAVLINK_CMD_SIM_RESET = 31000, from controller.py)
    conn.mav.command_long_send(conn.target_system, conn.target_component,
                               31000, 0, 0, 0, 0, 0, 0, 0, 0)
    print("Sim reset sent.", flush=True)
    time.sleep(0.5)

    # timesync 10 Hz keepalive + race-state listener (ENC_RACE, state_pilot-proven)
    stop = threading.Event()
    race = {"started": False}
    race_lock = threading.Lock()

    def ts():
        while not stop.is_set():
            try:
                conn.mav.timesync_send(int(time.time_ns()), 0)
            except Exception:
                pass
            time.sleep(0.1)
    threading.Thread(target=ts, daemon=True).start()

    # track capture: official gate layout (ENC_TRACK chunked transfer) -> JSON.
    # The geometry-calibration measurement (Day 131): lets us verify the maneuver
    # grammar's distance/turn distributions against the REAL course (the geometry
    # twin of the A150 appearance lesson — anchor one end outside our wall).
    trk_chunks, trk_expected = {}, {}

    def _save_track(payload):
        import json
        (num_gates,) = struct.unpack_from("<H", payload)
        body = payload[2:]
        gates = []
        for _ in range(num_gates):
            v = struct.unpack_from("<Hfffffffff", body)
            gates.append({"id": int(v[0]),
                          "pos_ned": [float(v[1]), float(v[2]), float(v[3])],
                          "quat_wxyz_ned": [float(v[4]), float(v[5]), float(v[6]), float(v[7])]})
            body = body[38:]
        out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           f"official_track_{time.strftime('%Y%m%d_%H%M%S')}.json")
        with open(out, "w") as f:
            json.dump({"num_gates": num_gates, "gates": gates}, f, indent=1)
        print(f"  [TRACK] {num_gates} gates captured -> {out}", flush=True)

    def rx():
        while not stop.is_set():
            try:
                msg = conn.recv_match(blocking=False)
            except ConnectionResetError:
                return
            if msg is None:
                time.sleep(0.001)
                continue
            t = msg.get_type()
            if t == "DATA_TRANSMISSION_HANDSHAKE":
                trk_chunks[msg.width] = {}
                trk_expected[msg.width] = msg.packets
            elif t == "ENCAPSULATED_DATA":
                raw = bytes(msg.data)
                if not raw:
                    continue
                if raw[0] == ENC_RACE:
                    try:
                        (_dt, _sim, race_start_ms, _fin, _active, _last) = \
                            struct.unpack_from("<BQqqIq", raw)
                        with race_lock:
                            race["started"] = race_start_ms is not None and race_start_ms >= 0
                    except struct.error:
                        pass
                elif raw[0] == ENC_TRACK:
                    try:
                        _dt, transfer_id = struct.unpack_from("<BH", raw)
                        if transfer_id in trk_expected:
                            trk_chunks[transfer_id][msg.seqnr] = raw[3:]
                            if len(trk_chunks[transfer_id]) == trk_expected[transfer_id]:
                                payload = b"".join(
                                    trk_chunks[transfer_id][i]
                                    for i in range(trk_expected[transfer_id]))
                                _save_track(payload)
                                del trk_chunks[transfer_id]
                                del trk_expected[transfer_id]
                    except (struct.error, KeyError):
                        pass
    threading.Thread(target=rx, daemon=True).start()

    conn.mav.command_long_send(conn.target_system, conn.target_component,
                               mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0,
                               1, 0, 0, 0, 0, 0, 0)
    print("Arm sent.  >>> PRESS RACE IN THE SIM NOW <<<", flush=True)
    print(f"Mode: {'DRY-RUN (no commands)' if args.dry_run else 'FLYING'} "
          f"| {args.secs:.0f}s\n", flush=True)

    import cv2
    os.makedirs(FRAME_DIR, exist_ok=True)
    run_tag = time.strftime("%H%M%S")
    saved = 0

    boot_ms = int(time.time() * 1000)
    t0 = time.time()
    last_id = -1
    last_log = 0.0
    steps = 0
    lat_acc = 0.0
    was_started = False
    while time.time() - t0 < args.secs:
        with race_lock:
            started = race["started"]
        if not started and not args.dry_run:
            # HOLD before the countdown finishes — commanding early is an auto-DQ
            # (learned the hard way, first flight Day 130). Save a few pre-race
            # frames for the OOD diagnosis, command nothing.
            frame, fid = vision.get()
            if frame is not None and fid != last_id and saved < 10:
                last_id = fid
                cv2.imwrite(os.path.join(FRAME_DIR, f"{run_tag}_prerace_{fid}.jpg"), frame)
                saved += 1
            now = time.time() - t0
            if now - last_log >= 1.0:
                last_log = now
                print(f"t={now:5.1f} HOLDING (race not started; frames={vision.count}) "
                      f"— press RACE", flush=True)
            time.sleep(0.01)
            continue
        if started and not was_started:
            was_started = True
            race_t = time.time()
            pilot.reset()   # fresh RSSM at the episode boundary
            print(f"t={time.time()-t0:5.1f} RACE SIGNAL — countdown hold "
                  f"{args.start_delay:.1f}s (RSSM watching, commanding nothing).",
                  flush=True)
        in_countdown = was_started and (time.time() - race_t) < args.start_delay

        frame, fid = vision.get()
        if frame is None or fid == last_id:
            time.sleep(0.002)   # wait for a NEW frame (frame-driven ~30 Hz)
            now = time.time() - t0
            if frame is None and now - last_log >= 1.0:
                last_log = now
                print(f"t={now:5.1f} waiting for camera frames... "
                      f"(arm sent; press RACE)", flush=True)
            continue
        last_id = fid

        t_act = time.time()
        action = pilot.act(frame)               # stateful RSSM, geometry-preserving
        lat_acc += time.time() - t_act
        ca = to_competition_action(action)      # SIM constants (crux #3)
        rates_ned = zup_to_ned_rates(np.array(
            [ca.roll_rate_rad_s, ca.pitch_rate_rad_s, ca.yaw_rate_rad_s]))
        steps += 1

        # frame capture: raw 640x360 + the 64x64 the policy actually saw
        if steps % SAVE_EVERY == 0 and saved < SAVE_CAP:
            cv2.imwrite(os.path.join(FRAME_DIR, f"{run_tag}_s{steps:05d}_raw.jpg"), frame)
            pv = to_training_frame(frame)       # RGB 64x64
            cv2.imwrite(os.path.join(FRAME_DIR, f"{run_tag}_s{steps:05d}_policyview.png"),
                        cv2.cvtColor(pv, cv2.COLOR_RGB2BGR))
            saved += 1

        if not args.dry_run and not in_countdown:
            conn.mav.set_attitude_target_send(
                int(time.time() * 1000) - boot_ms,
                conn.target_system, conn.target_component,
                RATES_MASK, [1.0, 0.0, 0.0, 0.0],
                float(rates_ned[0]), float(rates_ned[1]), float(rates_ned[2]),
                float(ca.throttle))

        now = time.time() - t0
        if now - last_log >= 0.5:
            last_log = now
            print(f"t={now:5.1f} frames={vision.count} steps={steps} "
                  f"lat={1000*lat_acc/max(steps,1):4.1f}ms "
                  f"| thr={ca.throttle:.2f} "
                  f"rates FLU r/p/y=({ca.roll_rate_rad_s:+.2f},"
                  f"{ca.pitch_rate_rad_s:+.2f},{ca.yaw_rate_rad_s:+.2f}) rad/s",
                  flush=True)

    stop.set()
    vision.stop.set()
    print(f"\nDone. frames={vision.count} control steps={steps} "
          f"avg act latency={1000*lat_acc/max(steps,1):.1f}ms", flush=True)


if __name__ == "__main__":
    main()
