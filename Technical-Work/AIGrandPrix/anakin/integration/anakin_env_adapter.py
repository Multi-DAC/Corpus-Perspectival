"""DreamerV3 env adapter for the Anakin training sim.

Bridges anakin/sim/env.py::AnakinEnv (Gymnasium, 5-tuple) to the old-gym dict contract
the NM512/dreamerv3-torch wrappers expect (cf. envs/dmc.py): reset()->obs_dict,
step()->(obs_dict, reward, done, info), observation_space = Dict({"image": ...}).

Mapping of the two done flags Dreamer cares about:
  done        = terminated OR truncated  (episode ends; replay cuts here)
  is_terminal = terminated only          (a TRUE environmental terminal — collision or
                                          course-complete — so the cont-head learns to
                                          predict end-of-episode; a TIMEOUT is NOT terminal,
                                          so value bootstrapping still happens past it).

The Anakin sim is vision-only (image obs), so observation_space carries just "image"
(encoder/decoder cnn_keys='image', mlp_keys='$^' — see the `anakin` config block).
"""
import os
import sys

import gym
import numpy as np

# anakin/sim lives outside this vendored repo: envs/ -> dreamerv3-torch -> third_party -> anakin -> sim
_SIM = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "sim"))
if _SIM not in sys.path:
    sys.path.insert(0, _SIM)

from env import AnakinEnv  # noqa: E402  (path injected above)


class Anakin:
    metadata = {}

    def __init__(self, task="train", size=(64, 64), n_gates=2, max_steps=400,
                 difficulty=0.0, spacing=6.0, env_device="cpu", seed=0):
        self._size = tuple(size)
        self._env = AnakinEnv(
            n_gates=n_gates, max_steps=max_steps, difficulty=difficulty,
            spacing=spacing, device=env_device, seed=seed,
        )
        self.reward_range = [-np.inf, np.inf]

    @property
    def observation_space(self):
        return gym.spaces.Dict({
            "image": gym.spaces.Box(0, 255, self._size + (3,), dtype=np.uint8),
        })

    @property
    def action_space(self):
        return gym.spaces.Box(-1.0, 1.0, (4,), dtype=np.float32)

    def reset(self):
        obs, _ = self._env.reset()
        return {"image": obs, "is_first": True, "is_terminal": False}

    def step(self, action):
        obs, reward, terminated, truncated, info = self._env.step(np.asarray(action))
        done = bool(terminated or truncated)
        out = {"image": obs, "is_first": False, "is_terminal": bool(terminated)}
        info = {"discount": np.array(1.0, np.float32), **info}
        return out, float(reward), done, info

    def render(self, *args, **kwargs):
        return self._env.render()

    def close(self):
        self._env.close()
