"""seg_probe.py — feasibility probe for the segmentation front-end (SkyDreamer route).

Hypothesis (Day 134): the official<->training appearance gap is the official sim's
dense TRON background texture, NOT gate color (our renderer already matches the measured
orange-red gate palette). An orange-red gate segmenter should therefore (a) isolate gates
cleanly in BOTH domains with ONE threshold, and (b) make official and training frames look
near-identical in mask space. This probes (a) on the real official harvest + measures gate
coverage stats. Output: mask overlays to seg_probe_out/ for visual inspection.
"""
import glob
import os
import sys

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OFFICIAL = r"C:\Users\Wasch\OneDrive\Desktop\AI-GP Simulator v1.0.3364\PyAIPilotExample\official_frames\manual_20260614_114130"
OUT = os.path.join(HERE, "seg_probe_out")
os.makedirs(OUT, exist_ok=True)


def gate_mask(bgr):
    """Orange-red gate mask. Gate core RGB~(229,93,78) -> OpenCV HSV hue ~4-9deg, high S,V.
    Red wraps, so take low-hue AND high-hue bands. Excludes cyan ribbon + gray bg."""
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    lo1 = cv2.inRange(hsv, (0, 70, 70), (16, 255, 255))     # orange-red core + glow
    lo2 = cv2.inRange(hsv, (168, 70, 70), (179, 255, 255))  # red wrap-around
    m = cv2.bitwise_or(lo1, lo2)
    # clean speckle, close gate-frame gaps
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    return m


def main():
    paths = sorted(glob.glob(os.path.join(OFFICIAL, "*.jpg")))
    if not paths:
        print(f"no frames in {OFFICIAL}", file=sys.stderr)
        return 1
    # sample evenly across the run (varied viewpoints)
    idx = np.linspace(0, len(paths) - 1, 12).astype(int)
    covs = []
    saved = 0
    for k, i in enumerate(idx):
        bgr = cv2.imread(paths[i], cv2.IMREAD_COLOR)
        if bgr is None:
            continue
        m = gate_mask(bgr)
        cov = float((m > 0).mean())
        covs.append(cov)
        # side-by-side: raw | mask-overlay (gate pixels kept, rest dimmed)
        overlay = bgr.copy()
        overlay[m == 0] = (overlay[m == 0] * 0.15).astype(np.uint8)
        strip = np.hstack([bgr, np.full((bgr.shape[0], 8, 3), 255, np.uint8), overlay])
        cv2.imwrite(os.path.join(OUT, f"seg_{k:02d}_cov{cov*100:04.1f}.png"), strip)
        saved += 1
    covs = np.array(covs)
    print(f"official frames probed: {saved}/{len(idx)}  (pool {len(paths)})")
    print(f"gate-pixel coverage: mean={covs.mean()*100:.2f}%  "
          f"min={covs.min()*100:.2f}%  max={covs.max()*100:.2f}%  "
          f"frames-with-gate(>0.05%)={int((covs > 5e-4).sum())}/{len(covs)}")
    print(f"overlays -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
