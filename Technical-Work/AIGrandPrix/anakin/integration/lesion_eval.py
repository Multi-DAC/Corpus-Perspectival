"""Camera-lesion eval for a trained Anakin DreamerV3 checkpoint.

Tests LC31 vs LC29 on the 1-gate smoke checkpoint: does the policy use the camera
*instrumentally*, or has it learned to dead-reckon through the RSSM recurrent state `h`?

Method: load latest.pt (copied to scratch so we never race the live trainer's writes),
run N paired eval episodes under three camera conditions on IDENTICAL tracks
(same env seed -> same gate geometry; the lesion only rewrites obs['image']):

  none   : real FPV frames                      (sanity: should reproduce live eval ~+6.4)
  freeze : obs['image'] held at the reset frame (camera stuck)
  blank  : obs['image'] = zeros                 (camera blinded)

Read: if freeze/blank return HOLDS near `none` -> odometry (LC29 wearing LC31's clothes).
      if it COLLAPSES toward the random baseline (~-5.3) -> vision is load-bearing (LC31).
"""
import functools
import pathlib
import shutil
import sys

import numpy as np
import ruamel.yaml as yaml
import torch

import tools
from dreamer import Dreamer, make_env

DREAMER_DIR = pathlib.Path(__file__).parent
LIVE_LOGDIR = DREAMER_DIR / "logdir" / "smoke"
SCRATCH = DREAMER_DIR / "logdir" / "lesion_scratch"


def build_config():
    configs = yaml.YAML(typ="safe", pure=True).load((DREAMER_DIR / "configs.yaml").read_text())

    def recursive_update(base, update):
        for k, v in update.items():
            if isinstance(v, dict) and k in base:
                recursive_update(base[k], v)
            else:
                base[k] = v

    defaults = {}
    for name in ["defaults", "anakin"]:
        recursive_update(defaults, configs[name])

    import argparse
    parser = argparse.ArgumentParser()
    for key, value in sorted(defaults.items(), key=lambda x: x[0]):
        arg_type = tools.args_type(value)
        parser.add_argument(f"--{key}", type=arg_type, default=arg_type(value))
    config = parser.parse_args([])

    # point everything at scratch so we never touch the live trainer's dirs
    config.logdir = str(SCRATCH)
    config.traindir = str(SCRATCH / "train_eps")
    config.evaldir = str(SCRATCH / "eval_eps")
    return config


class Lesion:
    """Wraps a make_env env; rewrites obs['image'] per mode. Forwards everything else."""

    def __init__(self, env, mode):
        self._env = env
        self._mode = mode          # 'none' | 'freeze' | 'blank'
        self._frozen = None

    def __getattr__(self, name):
        return getattr(self._env, name)

    def reset(self):
        obs = self._env.reset()
        self._frozen = np.array(obs["image"]).copy()
        return self._apply(obs)

    def step(self, action):
        obs, r, d, info = self._env.step(action)
        return self._apply(obs), r, d, info

    def _apply(self, obs):
        if self._mode == "none":
            return obs
        obs = dict(obs)
        if self._mode == "freeze":
            obs["image"] = self._frozen
        elif self._mode == "blank":
            obs["image"] = np.zeros_like(np.array(obs["image"]))
        return obs


def run_mode(config, mode, n_eps, seed):
    config.seed = seed
    env = Lesion(make_env(config, "eval", 0), mode)
    eval_policy = functools.partial(agent, training=False)

    returns, outcomes = [], {}
    for ep in range(n_eps):
        obs = env.reset()
        state = None
        done = np.array([True])               # is_first for the RSSM
        ep_ret = 0.0
        last_outcome = "none"
        while True:
            batch = {k: np.stack([obs[k]]) for k in ("image", "is_first", "is_terminal")}
            action, state = eval_policy(batch, done, state)
            a = {k: np.array(action[k][0].detach().cpu()) for k in action}
            obs, r, d, info = env.step(a)
            ep_ret += float(r)
            last_outcome = info.get("outcome", last_outcome)
            done = np.array([bool(d)])
            if d:
                break
        returns.append(ep_ret)
        outcomes[last_outcome] = outcomes.get(last_outcome, 0) + 1
    env.close()
    return np.array(returns), outcomes


if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    SEED = 100
    config = build_config()
    if SCRATCH.exists():
        shutil.rmtree(SCRATCH, ignore_errors=True)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    (SCRATCH / "train_eps").mkdir(exist_ok=True)
    (SCRATCH / "eval_eps").mkdir(exist_ok=True)

    # copy the checkpoint so we read a stable snapshot, not a file the trainer may overwrite
    src = LIVE_LOGDIR / "latest.pt"
    ckpt_path = SCRATCH / "latest.pt"
    shutil.copy2(src, ckpt_path)
    print(f"copied checkpoint: {src}  ({src.stat().st_size/1e6:.0f} MB)")

    # build agent (dataset=None: eval with training=False never touches it)
    probe_env = make_env(config, "eval", 0)
    config.num_actions = probe_env.action_space.shape[0]
    obs_space, act_space = probe_env.observation_space, probe_env.action_space
    probe_env.close()

    logger = tools.Logger(pathlib.Path(SCRATCH), 0)
    agent = Dreamer(obs_space, act_space, config, logger, None).to(config.device)
    agent.requires_grad_(False)
    ckpt = torch.load(ckpt_path, map_location=config.device)
    agent.load_state_dict(ckpt["agent_state_dict"])
    agent.eval()
    train_step = ckpt.get("logger", {}).get("step", "?") if isinstance(ckpt.get("logger"), dict) else "?"
    print(f"loaded agent  device={config.device}  n_actions={config.num_actions}")

    print(f"\n=== camera-lesion eval  (N={N} paired episodes/mode, seed={SEED}) ===")
    print(f"{'mode':8s} {'mean':>8s} {'std':>7s} {'min':>7s} {'max':>7s}   outcomes")
    results = {}
    for mode in ("none", "freeze", "blank"):
        rets, outs = run_mode(config, mode, N, SEED)
        results[mode] = rets
        print(f"{mode:8s} {rets.mean():>+8.2f} {rets.std():>7.2f} "
              f"{rets.min():>+7.2f} {rets.max():>+7.2f}   {outs}")

    base = results["none"].mean()
    print("\n--- read ---")
    for mode in ("freeze", "blank"):
        drop = base - results[mode].mean()
        frac = drop / abs(base) if base != 0 else float("nan")
        print(f"{mode:8s} drop vs sighted: {drop:+.2f}  ({frac*100:+.0f}% of sighted)")
    print("\nLC31 (vision load-bearing) => large drop toward the ~-5.3 random baseline.")
    print("LC29 (odometry via h)      => return holds near sighted; the gate-passing was dead-reckoning.")
