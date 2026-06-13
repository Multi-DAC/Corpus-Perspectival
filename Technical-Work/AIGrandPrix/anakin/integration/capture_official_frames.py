#
# capture_official_frames.py — control-AGNOSTIC official-sim frame harvester.
#
# WHY THIS EXISTS (Day 133, 2026-06-13):
#   Flight #2 spun out exactly as the overnight Fréchet gate predicted (ratio 1.063,
#   "the wall is texture-deep, not palette-deep"). The gate is now a VALIDATED predictor
#   of official-sim transfer, and the next move is official-DOMAIN appearance adaptation:
#   re-style / fine-tune against the real sim's textures+lighting, not our measured palette.
#   For that we need RAW FRAMES OF THE OFFICIAL WORLD — and crucially, flying skill is
#   IRRELEVANT. A drone wandering drunkenly under manual override produces exactly as much
#   appearance signal as a perfect lap.
#
#   run_dreamer.py captures frames only inside the policy control loop (gated on `steps`),
#   so manual-override flying records NOTHING. This script fixes that by decoupling capture
#   from control entirely: it ONLY listens to the camera feed and saves frames. It commands
#   nothing and reads no MAVLink. Run it in PARALLEL with manual flying (or a parked drone,
#   or the policy) — whoever flies, we get the pictures.
#
#   UDP NOTE: binds the SAME camera port (5600) the policy would. A manual-control script
#   that only SENDS rate/attitude commands on MAVLink (14550) does not touch 5600, so the
#   two run side by side cleanly. If your manual script ALSO consumes 5600, run ONLY this
#   one to harvest (you can fly blind from the sim's own window) — or merge capture into it.
#
# Usage (anakin .venv — though this needs only the stdlib):
#   python capture_official_frames.py                 # harvest until Ctrl-C, every 3rd frame
#   python capture_official_frames.py --secs 120      # harvest for 120s then stop
#   python capture_official_frames.py --every 1       # save EVERY frame (densest)
#   python capture_official_frames.py --out my_run    # custom output subdir
#
# Output: official_frames/<run_tag>/f<NNNNNN>_id<frame_id>.jpg  (raw 640x360 JPEG, as sent)
#

import argparse
import os
import socket
import struct
import sys
import time

VISION_IP, VISION_PORT = "0.0.0.0", 5600
HEADER_FORMAT = "<IHHIIQ"   # frame_id, chunk_id, total_chunks, jpeg_size, payload_size, t_ns
HEADER_SZ = struct.calcsize(HEADER_FORMAT)


def main():
    ap = argparse.ArgumentParser(description="Control-agnostic official-sim frame harvester.")
    ap.add_argument("--secs", type=float, default=0.0,
                    help="harvest duration in seconds (0 = until Ctrl-C, the default)")
    ap.add_argument("--every", type=int, default=3,
                    help="save every Nth completed frame (default 3; use 1 for densest)")
    ap.add_argument("--cap", type=int, default=5000,
                    help="max frames to save this run (default 5000)")
    ap.add_argument("--out", default=None,
                    help="output subdir name under official_frames/ (default: timestamp)")
    args = ap.parse_args()

    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "official_frames")
    run_tag = args.out or time.strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(base, run_tag)
    os.makedirs(out_dir, exist_ok=True)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(1.0)
    try:
        sock.bind((VISION_IP, VISION_PORT))
    except OSError as e:
        print(f"FAILED to bind UDP:{VISION_PORT} ({e}).\n"
              f"  Something else is already holding the camera port — most likely the\n"
              f"  policy flight script or a manual-control script that also reads 5600.\n"
              f"  Run only ONE consumer of the camera feed at a time.", file=sys.stderr)
        return 1

    print(f"Harvesting official frames on UDP:{VISION_PORT} -> {out_dir}", flush=True)
    print(f"  save every {args.every} frame(s), cap {args.cap}, "
          f"{'until Ctrl-C' if args.secs <= 0 else f'{args.secs:.0f}s'}.  "
          f"Fly however you like — skill is irrelevant for appearance frames.", flush=True)

    frames = {}            # frame_id -> {chunk_id: payload, ...}
    expected = {}          # frame_id -> total_chunks
    completed = 0          # fully-decoded frames seen
    saved = 0
    t0 = time.time()
    last_log = 0.0

    try:
        while True:
            if args.secs > 0 and time.time() - t0 >= args.secs:
                break
            if saved >= args.cap:
                print(f"Reached --cap {args.cap}; stopping.", flush=True)
                break
            try:
                packet, _ = sock.recvfrom(65536)
            except socket.timeout:
                continue

            if len(packet) < HEADER_SZ:
                continue
            frame_id, chunk_id, total_chunks, jpeg_size, payload_size, _t_ns = \
                struct.unpack(HEADER_FORMAT, packet[:HEADER_SZ])
            payload = packet[HEADER_SZ:]

            if frame_id not in frames:
                frames[frame_id] = {}
                expected[frame_id] = total_chunks
            frames[frame_id][chunk_id] = payload

            if len(frames[frame_id]) == expected[frame_id]:
                # reassemble in chunk order; only save if every chunk is present
                if all(i in frames[frame_id] for i in range(total_chunks)):
                    jpeg = b"".join(frames[frame_id][i] for i in range(total_chunks))
                    completed += 1
                    if completed % args.every == 0:
                        fn = os.path.join(out_dir, f"f{completed:06d}_id{frame_id}.jpg")
                        with open(fn, "wb") as f:
                            f.write(jpeg)     # raw JPEG as sent — no decode/re-encode
                        saved += 1
                del frames[frame_id]
                del expected[frame_id]
                # bound memory: drop stale partial frames
                if len(frames) > 8:
                    for k in sorted(frames)[:-4]:
                        del frames[k]
                        expected.pop(k, None)

            now = time.time() - t0
            if now - last_log >= 1.0:
                last_log = now
                print(f"t={now:6.1f}s  completed={completed}  saved={saved}", flush=True)
    except KeyboardInterrupt:
        print("\nCtrl-C — stopping.", flush=True)
    finally:
        sock.close()

    print(f"Done. {saved} frames saved to {out_dir}  "
          f"(seen {completed} complete frames over {time.time()-t0:.0f}s).", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
