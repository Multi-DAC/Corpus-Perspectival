"""Control for wm_recon_diag: reconstruct TRAINING-distribution frames (from the sim
renderer via maneuver_env) through the same world model. If these come back SHARP while
the real sim frames came back mush, the appearance gap is proven (not a broken decoder)."""
import sys, os
import numpy as np, cv2
_HERE = os.path.dirname(os.path.abspath(__file__))
for p in [_HERE, os.path.join(_HERE, "..", "sim"),
          os.path.join(_HERE, "..", "third_party", "dreamerv3-torch")]:
    sys.path.insert(0, os.path.abspath(p))
import torch
from dreamer_pilot import DreamerPilot
CKPT = os.path.join(_HERE, "..", "third_party", "dreamerv3-torch", "logdir",
                    "maneuver_imu_stability", "best.pt")
out = sys.argv[1] if len(sys.argv) > 1 else "C:/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Technical-Work/AIGrandPrix/anakin/integration/wm_recon_control.png"

pilot = DreamerPilot(CKPT); wm = pilot._agent._wm
from maneuver_env import AnakinManeuverEnv as ManeuverEnv
from dynamics import imu_from_state
env = ManeuverEnv(max_steps=200, device=pilot._config.device, seed=1002)
obs, _ = env.reset(seed=1002); pilot.reset()
frames, imus = [], []
a = np.zeros(4, np.float32)
for t in range(8):
    frames.append(obs.copy())
    im = imu_from_state(env._state, torch.as_tensor(a, dtype=torch.float32,
         device=env._state.device).reshape(1, -1), noise_std=0.0)[0].detach().cpu().numpy()
    imus.append(np.clip(im, -50, 50))
    a = pilot.act_training_frame(obs, imu=imus[-1]); obs, r, term, trunc, info = env.step(a)
    if term or trunc: break

imgs = np.stack(frames)[None]; T = imgs.shape[1]
imu = np.stack(imus)[None].astype(np.float32)
isf = np.zeros((1, T), np.float32); isf[0, 0] = 1.0
data = {"image": imgs.astype(np.float32), "imu": imu, "action": np.zeros((1, T, 4), np.float32),
        "is_first": isf, "is_terminal": np.zeros((1, T), np.float32)}
with torch.no_grad():
    d = wm.preprocess(data); embed = wm.encoder(d)
    states, _ = wm.dynamics.observe(embed, d["action"], d["is_first"])
    recon = wm.heads["decoder"](wm.dynamics.get_feat(states))["image"].mode()
recon = (recon.clamp(0, 1) * 255).byte().cpu().numpy()[0]
U = 160; rows = []
for t in range(T):
    inp = cv2.resize(cv2.cvtColor(imgs[0, t], cv2.COLOR_RGB2BGR), (U, U), interpolation=cv2.INTER_NEAREST)
    rec = cv2.resize(cv2.cvtColor(recon[t], cv2.COLOR_RGB2BGR), (U, U), interpolation=cv2.INTER_NEAREST)
    rows.append(np.concatenate([inp, np.full((U, 4, 3), 60, np.uint8), rec], axis=1))
grid = np.concatenate(rows, axis=0)
cv2.putText(grid, "TRAIN-INPUT      RECON", (6, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
cv2.imwrite(out, grid); print(f"wrote {out} (rendered training frames vs their reconstruction)")
