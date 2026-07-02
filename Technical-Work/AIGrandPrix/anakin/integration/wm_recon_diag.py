"""
"What does Anakin see?" — world-model reconstruction diagnostic (Day 152).

Feeds REAL sim frames through best.pt's DreamerV3 world model and decodes what it
represents. If the reconstruction shows the ribbon+gate, he SEES it (problem = control).
If it's mush, he's effectively blind to real imagery (problem = appearance/coverage OOD).

Mirrors WorldModel.video_pred (proven path): preprocess -> encoder -> dynamics.observe
-> decoder["image"].mode(). Uses the SAME to_training_frame the live policy uses, so the
encoder sees exactly what it sees in flight.

Usage:
  .venv/Scripts/python.exe integration/wm_recon_diag.py <glob of raw jpgs> [out.png]
"""
import sys, os, glob
import numpy as np
import cv2

_HERE = os.path.dirname(os.path.abspath(__file__))
for p in [_HERE, os.path.join(_HERE, "..", "sim"),
          os.path.join(_HERE, "..", "third_party", "dreamerv3-torch")]:
    sys.path.insert(0, os.path.abspath(p))

import torch
from dreamer_pilot import DreamerPilot, to_training_frame

CKPT = os.path.join(_HERE, "..", "third_party", "dreamerv3-torch", "logdir",
                    "maneuver_imu_stability", "best.pt")

def main():
    pattern = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "..", "..",
              "..", "..", "..", "..", "flight_frames", "*prerace*.jpg")
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(_HERE, "wm_recon.png")

    paths = sorted(glob.glob(pattern))[:8]
    if not paths:
        print(f"no frames matched {pattern}"); return
    print(f"{len(paths)} frames:", *[os.path.basename(p) for p in paths], sep="\n  ")

    pilot = DreamerPilot(CKPT)                 # auto-detects IMU arch
    wm = pilot._agent._wm
    dev = pilot._config.device

    # build the SAME 64x64 policy view the encoder gets in flight
    imgs = []
    for p in paths:
        bgr = cv2.imread(p)
        imgs.append(to_training_frame(bgr))    # RGB 64x64 uint8
    imgs = np.stack(imgs)[None]                 # [1, T, 64,64,3]
    T = imgs.shape[1]

    # rest-IMU (drone hovering at start), clamped to the training box like live
    imu = np.tile(np.array([0, 0, 0, -3.0, 0, 9.3], np.float32), (1, T, 1))
    imu = np.clip(imu, -50.0, 50.0)
    is_first = np.zeros((1, T), np.float32); is_first[0, 0] = 1.0
    data = {
        "image": imgs.astype(np.float32),
        "imu": imu,
        "action": np.zeros((1, T, 4), np.float32),
        "is_first": is_first,
        "is_terminal": np.zeros((1, T), np.float32),
    }
    with torch.no_grad():
        d = wm.preprocess(data)
        embed = wm.encoder(d)
        states, _ = wm.dynamics.observe(embed, d["action"], d["is_first"])
        recon = wm.heads["decoder"](wm.dynamics.get_feat(states))["image"].mode()
    recon = (recon.clamp(0, 1) * 255).byte().cpu().numpy()[0]   # [T,64,64,3] RGB

    # side-by-side grid: rows=frames, cols=[input | reconstruction], upscaled
    U = 160
    rows = []
    for t in range(T):
        inp = cv2.resize(cv2.cvtColor(imgs[0, t], cv2.COLOR_RGB2BGR), (U, U), interpolation=cv2.INTER_NEAREST)
        rec = cv2.resize(cv2.cvtColor(recon[t], cv2.COLOR_RGB2BGR), (U, U), interpolation=cv2.INTER_NEAREST)
        sep = np.full((U, 4, 3), 60, np.uint8)
        rows.append(np.concatenate([inp, sep, rec], axis=1))
    grid = np.concatenate(rows, axis=0)
    cv2.putText(grid, "INPUT            RECON", (6, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    cv2.imwrite(out, grid)
    print(f"wrote {out}  ({T} frames, left=what the camera gave, right=what the world model represents)")

if __name__ == "__main__":
    main()
