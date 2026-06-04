#
# diag_freeze_ablation.py  (2026-06-02 late, creative drive)
#
# The A150 3M policy commands thr=+1 (takeoff) on our-sim ground-start obs but thr=-1 (freeze)
# on the real-sim start obs. Both obs are in-range (no clip). WHICH obs dims cause the flip?
# Ablate: start from the real-sim (freeze) obs, swap in the our-sim (takeoff) values one dim-
# group at a time, and see which swap flips thr positive. The causal group is the freeze driver.
#
import os, sys, json, pickle
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from infinite_gate_env import InfiniteGateEnv
from stable_baselines3 import PPO

CK = "runs/infinite_v3_a150_farstart_1780470710/checkpoints/ppo_v3_3000192_steps.zip"
VN = CK[:-4] + "_vecnorm.pkl"
model = PPO.load(CK, device="cpu")
vn = pickle.load(open(VN, "rb")); mean = vn.obs_rms.mean; var = vn.obs_rms.var
clip = float(vn.clip_obs); eps = float(vn.epsilon)
def nrm(o): return np.clip((np.asarray(o) - mean) / np.sqrt(var + eps), -clip, clip).astype(np.float32)
def thr_of(o): a, _ = model.predict(nrm(o), deterministic=True); return a

# real-sim freeze obs (last dump record)
live = np.array(json.loads(open("../vision/vq1_pilot/flight_obs_dump.jsonl").read().strip().split(chr(10))[-1])["obs_raw"])
# our-sim ground-start (takes off) — average a few resets for a representative takeoff obs
sims = []
for s in range(8):
    e = InfiniteGateEnv(ground_start_prob=1.0, perception_obs=False, adaptive_curriculum=True, seed=s)
    o, _ = e.reset(); sims.append(np.asarray(o, dtype=float)); e.close()
sim = np.mean(sims, axis=0)

GROUPS = {
    "vel(0-2)": [0, 1, 2], "omega(3-5)": [3, 4, 5], "GRAVITY(6-8)": [6, 7, 8],
    "gatedir(9-11)": [9, 10, 11], "dist(12)": [12], "nextdir(13-15)": [13, 14, 15],
    "speed(16)": [16], "prog(17)": [17], "worlddir(18-20)": [18, 19, 20],
    "fwd(21-23)": [21, 22, 23], "tsg(24)": [24], "vclose(25)": [25], "gateorient(26-28)": [26, 27, 28], "galign(29)": [29],
}

print(f"baseline real-sim (freeze): thr={thr_of(live)[0]:+.2f}")
print(f"baseline our-sim (takeoff): thr={thr_of(sim)[0]:+.2f}")
print("\nablate: real-sim obs with ONE group swapped to our-sim values ->")
flips = []
for name, idx in GROUPS.items():
    mod = live.copy(); mod[idx] = sim[idx]
    a = thr_of(mod)
    flip = "  *** FLIPS TO TAKEOFF" if a[0] > 0.3 else ""
    if a[0] > 0.3: flips.append(name)
    print(f"   swap {name:>16}: thr={a[0]:+.2f}{flip}")

# cumulative: add the flip groups together
if flips:
    mod = live.copy()
    allidx = [i for n in flips for i in GROUPS[n]]
    mod[allidx] = sim[allidx]
    print(f"\n   swap ALL flip-groups {flips}: thr={thr_of(mod)[0]:+.2f}")
print("\nINTERPRETATION: the group(s) that flip thr positive are the freeze drivers.")
print("If GRAVITY(6-8) alone flips it -> spawn-attitude is the cause -> fix = attitude-randomized")
print("ground-starts in the retrain curriculum (robust regardless of physical-vs-convention).")
