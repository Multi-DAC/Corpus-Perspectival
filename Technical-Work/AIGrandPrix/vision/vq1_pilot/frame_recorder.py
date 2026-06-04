#
# Standalone visual recorder for the AI-GP VQ1 sim. Binds UDP 5600 ONLY (no MAVLink), so it
# coexists with state_pilot.py (which owns MAVLink 14550). Reassembles the sim's chunked-JPEG
# camera stream and saves each frame to frames/f{id}.jpg + a frames_index.jsonl line
# {frame_id, sim_time_ns, recv_walltime}. Align the visual stream with state_pilot's internal
# obs/action log by wall-clock offline.
#
#   python frame_recorder.py [secs]
#
import os, sys, time, struct, socket, json
from collections import deque

VPORT = 5600
HFMT = "<IHHIIQ"; HSZ = struct.calcsize(HFMT)   # fid, cid, tot, jsize, psize, t_ns


def main():
    secs = float(sys.argv[1]) if len(sys.argv) > 1 else 90.0
    HERE = os.path.dirname(os.path.abspath(__file__))
    outdir = os.path.join(HERE, "record_" + time.strftime("%Y%m%d_%H%M%S"))
    os.makedirs(os.path.join(outdir, "frames"), exist_ok=True)
    idx = open(os.path.join(outdir, "frames_index.jsonl"), "w")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); sock.settimeout(1.0)
    try:
        sock.bind(("0.0.0.0", VPORT))
    except OSError as e:
        print(f"[frame_recorder] UDP {VPORT} bind FAILED ({e}) — abort.", flush=True); return
    print(f"[frame_recorder] UDP {VPORT} bound -> {outdir} | {secs:.0f}s", flush=True)
    frames = {}; saved = 0; done = set(); done_q = deque()
    t0 = time.time()
    while time.time() - t0 < secs:
        try:
            pkt, _ = sock.recvfrom(65536)
        except socket.timeout:
            continue
        if len(pkt) < HSZ:
            continue
        fid, cid, tot, jsize, psize, t_ns = struct.unpack(HFMT, pkt[:HSZ])
        if fid in done:
            continue
        f = frames.setdefault(fid, {}); f[cid] = pkt[HSZ:]
        if len(f) == tot and all(i in f for i in range(tot)):
            jpeg = b"".join(f[i] for i in range(tot))
            open(os.path.join(outdir, "frames", f"f{fid:06d}.jpg"), "wb").write(jpeg)
            idx.write(json.dumps({"frame_id": int(fid), "sim_time_ns": int(t_ns),
                                  "recv_walltime": time.time()}) + "\n"); idx.flush()
            saved += 1
            if saved % 60 == 0:
                print(f"[frame_recorder] {saved} frames", flush=True)
            del frames[fid]; done.add(fid); done_q.append(fid)
            if len(done_q) > 4096:
                done.discard(done_q.popleft())
    idx.close(); sock.close()
    print(f"[frame_recorder] done, {saved} frames -> {outdir}", flush=True)


if __name__ == "__main__":
    main()
