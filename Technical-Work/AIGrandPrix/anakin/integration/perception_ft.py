"""
Perception fine-tune (Day 152) — teach Anakin's world model to SEE real sim frames,
without breaking the policy's latent space.

Mixed self-supervised fine-tune of the DreamerV3 WORLD MODEL only (actor/critic frozen —
wm._train's optimizer holds only WM params):
  - REAL frames (manual gamepad captures) -> the encoder learns to represent real imagery.
  - RENDERED frames (maneuver_env rollouts, full obs/action/reward) -> anchors the existing
    representation so the policy still works (anti-catastrophic-forgetting).
Reuses the tested `WorldModel._train` (recon + KL + heads). No reward needed for real frames
(dummy 0). Saves a NEW checkpoint (maneuver_percept_ft/) — best.pt is never touched.

Usage:
  .venv/Scripts/python.exe integration/perception_ft.py --smoke        # quick sanity (few steps)
  .venv/Scripts/python.exe integration/perception_ft.py --steps 6000   # full detached run
"""
import sys, os, glob, time, argparse
import numpy as np, cv2, torch

_HERE = os.path.dirname(os.path.abspath(__file__))
for p in [_HERE, os.path.join(_HERE, "..", "sim"),
          os.path.join(_HERE, "..", "third_party", "dreamerv3-torch")]:
    sys.path.insert(0, os.path.abspath(p))
from dreamer_pilot import DreamerPilot, to_training_frame

CKPT = os.path.join(_HERE, "..", "third_party", "dreamerv3-torch", "logdir", "maneuver_imu_stability", "best.pt")
OUTDIR = os.path.join(_HERE, "..", "third_party", "dreamerv3-torch", "logdir", "maneuver_percept_ft")
REAL_GLOB = r"C:/Users/Wasch/OneDrive/Desktop/AI-GP Simulator v1.0.3364/PyAIPilotExample/official_frames/manual_*/*.jpg"
REST_IMU = np.clip(np.array([0, 0, 0, -3.0, 0, 9.3], np.float32), -50, 50)

def load_real(max_n):
    """Preprocess real jpgs -> (N,64,64,3) uint8, grouped by session for clean sequences."""
    paths = sorted(glob.glob(REAL_GLOB))
    if max_n: paths = paths[:max_n]   # contiguous slice — preserve session sequences
    sess, cur, curkey = [], [], None
    for p in paths:
        key = os.path.basename(os.path.dirname(p))
        if key != curkey and cur:
            sess.append(np.stack(cur)); cur = []
        curkey = key
        img = cv2.imread(p)
        if img is None: continue
        cur.append(to_training_frame(img))
    if cur: sess.append(np.stack(cur))
    print(f"[real] {sum(len(s) for s in sess)} frames in {len(sess)} sessions", flush=True)
    return [s for s in sess if len(s) >= 4]

def collect_rendered(pilot, n_steps, device):
    """Roll out maneuver_env with the pilot -> per-episode dicts of arrays."""
    from maneuver_env import AnakinManeuverEnv as ManeuverEnv
    from dynamics import imu_from_state
    eps, seed = [], 5000
    got = 0
    while got < n_steps:
        env = ManeuverEnv(max_steps=400, device=device, seed=seed); seed += 1
        obs, _ = env.reset(seed=seed); pilot.reset()
        buf = {"image": [], "imu": [], "action": [], "reward": []}
        a = np.zeros(4, np.float32)
        while True:
            im = imu_from_state(env._state, torch.as_tensor(a, dtype=torch.float32,
                 device=env._state.device).reshape(1, -1), noise_std=0.0)[0].detach().cpu().numpy()
            im = np.clip(im, -50, 50)
            a = pilot.act_training_frame(obs, imu=im)
            buf["image"].append(obs.copy()); buf["imu"].append(im); buf["action"].append(a.astype(np.float32))
            obs, r, term, trunc, info = env.step(a); buf["reward"].append(np.float32(r))
            got += 1
            if term or trunc or len(buf["image"]) >= 400: break
        eps.append({k: np.stack(v) for k, v in buf.items()})
    print(f"[rendered] {got} steps in {len(eps)} episodes", flush=True)
    return eps

def sample_real(sessions, B, T):
    img = np.zeros((B, T, 64, 64, 3), np.float32)
    rng = np.random.default_rng()
    for b in range(B):
        s = sessions[rng.integers(len(sessions))]
        i = rng.integers(0, len(s) - T + 1)
        img[b] = s[i:i+T].astype(np.float32)
    z = lambda *sh: np.zeros(sh, np.float32)
    isf = z(B, T); isf[:, 0] = 1.0
    return {"image": img, "imu": np.tile(REST_IMU, (B, T, 1)), "action": z(B, T, 4),
            "reward": z(B, T), "is_first": isf, "is_terminal": z(B, T)}

def sample_rendered(eps, B, T):
    img = np.zeros((B, T, 64, 64, 3), np.float32); imu = np.zeros((B, T, 6), np.float32)
    act = np.zeros((B, T, 4), np.float32); rew = np.zeros((B, T), np.float32)
    rng = np.random.default_rng()
    for b in range(B):
        e = eps[rng.integers(len(eps))]
        n = len(e["image"])
        i = rng.integers(0, max(1, n - T + 1)); j = min(i + T, n); L = j - i
        img[b, :L] = e["image"][i:j]; imu[b, :L] = e["imu"][i:j]
        act[b, :L] = e["action"][i:j]; rew[b, :L] = e["reward"][i:j]
    isf = np.zeros((B, T), np.float32); isf[:, 0] = 1.0
    return {"image": img, "imu": imu, "action": act, "reward": rew,
            "is_first": isf, "is_terminal": np.zeros((B, T), np.float32)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=6000)
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--seqlen", type=int, default=16)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--max-real", type=int, default=0)
    args = ap.parse_args()
    if args.smoke:
        args.steps, args.max_real = 12, 600

    pilot = DreamerPilot(CKPT)
    agent, wm = pilot._agent, pilot._agent._wm
    for p in wm.parameters(): p.requires_grad_(True)     # DreamerPilot froze it for inference

    real = [s for s in load_real(args.max_real) if len(s) >= args.seqlen]
    assert real, "no real sessions >= seqlen; lower --seqlen or collect longer runs"
    rendered = collect_rendered(pilot, 2000 if args.smoke else 8000, pilot._config.device)
    os.makedirs(OUTDIR, exist_ok=True)
    Bh = max(1, args.batch // 2)

    t0 = time.time()
    for step in range(1, args.steps + 1):
        br = sample_rendered(rendered, Bh, args.seqlen)
        bx = sample_real(real, args.batch - Bh, args.seqlen)
        batch = {k: np.concatenate([br[k], bx[k]], 0) for k in br}
        _, _, metrics = wm._train(batch)
        if step % (2 if args.smoke else 100) == 0 or step == 1:
            im = metrics.get("image_loss", float("nan")); kl = metrics.get("kl", float("nan"))
            print(f"step {step:5d}/{args.steps}  image_loss={im:.3f}  kl={kl:.3f}  "
                  f"({(time.time()-t0)/step:.2f}s/it)", flush=True)
        if step % 1000 == 0 or step == args.steps:
            path = os.path.join(OUTDIR, "best.pt")
            torch.save({"agent_state_dict": agent.state_dict()}, path)
            print(f"  saved {path}", flush=True)
    print("done.", flush=True)

if __name__ == "__main__":
    main()
