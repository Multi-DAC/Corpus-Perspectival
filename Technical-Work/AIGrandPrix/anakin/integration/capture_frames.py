#
# capture_frames.py — passive camera capture from the official AI-GP sim.
#
# Sends NOTHING. Binds UDP:5600, assembles chunked JPEGs (protocol verbatim from
# vision_rx.py), and saves frame pairs:
#     capture_frames/<tag>_f<id>_raw.jpg        (640x360 as received, BGR)
#     capture_frames/<tag>_f<id>_policyview.png (the 64x64 the policy would see)
# plus a running stats line (fps, brightness/contrast of the policy view) so we
# can compare the official sim's visual domain against our training renderer.
#
# Day-130 purpose: the first flight showed the policy is OOD on the official
# sim's APPEARANCE (geometry already verified). This collects the reference
# imagery for the renderer restyle + carry-forward fine-tune.
#
# Usage (any python with cv2+numpy; the anakin .venv works):
#   python capture_frames.py [secs] [--every N] [--cap M]
# Defaults: 120s, save every 15th frame, max 600 pairs.
# While it runs: do anything in the sim — menu, countdown, manual ACRO flight.
# A manually-flown lap through gates = the gold-standard reference set.
#

import argparse
import os
import socket
import struct
import time

import cv2
import numpy as np

import sys
ANAKIN = r"C:\Users\mercu\clawd\repo-staging\Corpus-Perspectival\Technical-Work\AIGrandPrix\anakin"
sys.path.insert(0, os.path.join(ANAKIN, "integration"))
from dreamer_pilot import to_training_frame  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "capture_frames")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("secs", nargs="?", type=float, default=120.0)
    ap.add_argument("--every", type=int, default=15, help="save every Nth frame")
    ap.add_argument("--cap", type=int, default=600, help="max saved pairs")
    args = ap.parse_args()

    os.makedirs(OUT, exist_ok=True)
    tag = time.strftime("%H%M%S")

    header_format = "<IHHIIQ"
    header_sz = struct.calcsize(header_format)
    frames = {}

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1.0)
    sock.bind(("0.0.0.0", 5600))
    print(f"Listening on UDP:5600 for {args.secs:.0f}s — go do things in the sim "
          f"(manual ACRO lap = gold). Saving every {args.every}th frame to {OUT}",
          flush=True)

    t0 = time.time()
    n_complete = 0
    saved = 0
    last_log = 0.0
    bright_acc, contrast_acc, stat_n = 0.0, 0.0, 0

    while time.time() - t0 < args.secs:
        try:
            packet, _ = sock.recvfrom(65536)
        except socket.timeout:
            if time.time() - t0 - last_log >= 2.0:
                last_log = time.time() - t0
                print(f"t={last_log:5.1f} no packets yet — is the sim running?", flush=True)
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
                img = cv2.imdecode(np.frombuffer(jpeg, dtype=np.uint8),
                                   cv2.IMREAD_COLOR)
                if img is not None:
                    n_complete += 1
                    if n_complete % args.every == 0 and saved < args.cap:
                        pv = to_training_frame(img)          # RGB 64x64
                        cv2.imwrite(os.path.join(
                            OUT, f"{tag}_f{frame_id:08d}_raw.jpg"), img)
                        cv2.imwrite(os.path.join(
                            OUT, f"{tag}_f{frame_id:08d}_policyview.png"),
                            cv2.cvtColor(pv, cv2.COLOR_RGB2BGR))
                        saved += 1
                        g = cv2.cvtColor(pv, cv2.COLOR_RGB2GRAY)
                        bright_acc += float(g.mean())
                        contrast_acc += float(g.std())
                        stat_n += 1
            del frames[frame_id]
            if len(frames) > 8:
                for k in sorted(frames)[:-4]:
                    del frames[k]

        now = time.time() - t0
        if now - last_log >= 2.0:
            last_log = now
            fps = n_complete / max(now, 1e-6)
            b = bright_acc / max(stat_n, 1)
            c = contrast_acc / max(stat_n, 1)
            print(f"t={now:5.1f} frames={n_complete} ({fps:.0f}/s) saved={saved} "
                  f"| policyview brightness={b:.1f} contrast={c:.1f} "
                  f"(training renderer bg=40)", flush=True)

    print(f"\nDone. complete frames={n_complete}, saved pairs={saved} -> {OUT}",
          flush=True)
    if stat_n:
        print(f"Mean policyview brightness={bright_acc/stat_n:.1f} "
              f"contrast={contrast_acc/stat_n:.1f} "
              f"(our renderer: gray-40 background, high-contrast gates)", flush=True)


if __name__ == "__main__":
    main()
