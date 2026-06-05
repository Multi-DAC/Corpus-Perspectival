"""Probe: does simulate()'s O(N)-per-tick Python bookkeeping erode the batched vec-env throughput?

Decides Phase-3 inner-loop architecture (A: simulate shim vs B: custom loop) on data.
RAW   = batched env stepped with GPU obs, no per-env bookkeeping (the vec_env.py benchmark path).
A-SIM = same batched step, but wrapped in simulate-shaped work: GPU->CPU obs, slice into N obs
        dicts, np.stack back for the (stub) agent, per-env add_to_cache-style dict copy+append.
The A/RAW ratio is the throughput tax approach A pays. If it stays >~0.4 (within ~2.5x), A wins
(correctness gated by a cheap parity test). If it collapses (<~0.15), that's the empirical case for B.
"""
import os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "sim"))
import numpy as np
import torch
from vec_env import BatchedManeuverEnv
from render import IMG


def bench_raw(N, steps=200):
    env = BatchedManeuverEnv(n_envs=N, max_steps=400, device="cuda", seed=0)
    obs = env.reset()
    acts = np.tile(np.array([2*0.253-1, 0.0, 0.02, 0.0], np.float32), (N, 1))
    torch.cuda.synchronize(); t0 = time.time()
    for _ in range(steps):
        obs, r, done, infos = env.step(acts + np.random.randn(N, 4).astype(np.float32)*0.1)
    torch.cuda.synchronize()
    return steps * N / (time.time() - t0)


def bench_a_sim(N, steps=200):
    """Batched step + the per-env Python that simulate() imposes on a shim."""
    env = BatchedManeuverEnv(n_envs=N, max_steps=400, device="cuda", seed=0)
    obs_t = env.reset()
    cache = [[] for _ in range(N)]          # stand-in for the per-env episode cache
    acts = np.tile(np.array([2*0.253-1, 0.0, 0.02, 0.0], np.float32), (N, 1))
    torch.cuda.synchronize(); t0 = time.time()
    for _ in range(steps):
        # --- simulate-shaped collection around the one batched step ---
        imgs = obs_t.detach().cpu().numpy()                       # GPU->CPU transfer (A pays this)
        obs_list = [{"image": imgs[i], "is_first": False, "is_terminal": False}
                    for i in range(N)]                            # N dict builds
        batched = {k: np.stack([o[k] for o in obs_list]) for k in obs_list[0]}  # agent input stack
        action = batched["image"][:, 0, 0, 0]                     # stub "agent": trivial fn of obs
        a = acts + np.random.randn(N, 4).astype(np.float32)*0.1   # per-env action array
        obs_t, r, done, infos = env.step(a)                       # the real batched step
        for i in range(N):                                        # per-env add_to_cache analogue
            t = obs_list[i].copy(); t["action"] = a[i]; t["reward"] = float(r[i])
            t["discount"] = np.array(1 - float(done[i]))
            cache[i].append(t)
            if done[i]:
                cache[i] = []
    torch.cuda.synchronize()
    return steps * N / (time.time() - t0)


if __name__ == "__main__":
    print(f"simulate-overhead probe  device=cuda  {torch.cuda.get_device_name(0)}\n")
    print(f"{'N':>6} {'RAW k/s':>10} {'A-SIM k/s':>11} {'A/RAW':>7}  verdict")
    for N in (256, 1024):
        raw = bench_raw(N)
        asim = bench_a_sim(N)
        ratio = asim / raw
        verdict = "A clearly fine" if ratio > 0.4 else ("borderline" if ratio > 0.15 else "favors B")
        print(f"{N:>6} {raw/1e3:>10.1f} {asim/1e3:>11.1f} {ratio:>7.2f}  {verdict}")
