"""BatchedSimAdapter — present ONE BatchedManeuverEnv as N thunked env-handles for DreamerV3's
`tools.simulate()`.  Phase-3 approach A (PHASE3_DESIGN.md §70): keep upstream's tested collection /
world-model / imagination loop untouched; the *only* batching trick lives here.

How it works (the thunk seam):
  `tools.simulate` treats `envs` as a list of N single-env handles. Each tick it (1) calls
  `envs[i].reset()` on the done subset, (2) calls `envs[i].step(a_i)` on all N — collecting the
  returned *thunks* first, then resolving them (`[r() for r in results]`, cf. parallel.Damy).
  We exploit that collect-then-resolve order: every handle's reset()/step() just records intent and
  returns a thunk; the FIRST thunk resolved runs ONE batched env op for the whole phase, and the
  rest return their per-env slice.  So N handle calls -> 1 batched dynamics+render.

Reset-ownership is upstream's: the env runs `auto_reset=False`, so a done slot holds its terminal
state until simulate calls `reset()` on that handle (-> `BatchedManeuverEnv.reset_one`).

Obs/info contract mirrors `anakin_env_adapter.Anakin` exactly (the proven Phase-2 single-env
integration): obs = Dict({"image"}), done = terminated|truncated, is_terminal = terminated
(timeout is NOT terminal), discount = 1.0 (Dreamer's cont-head consumes is_terminal).
"""
import datetime
import os
import sys
import uuid

import gym
import numpy as np

# anakin/sim holds the batched env + kernels. This file is tracked in integration/ (../sim) but
# COPIED into the vendored repo at third_party/dreamerv3-torch/envs/ (../../../sim) — resolve both.
def _find_sim():
    here = os.path.dirname(os.path.abspath(__file__))
    for rel in (("..", "sim"), ("..", "..", "..", "sim")):
        cand = os.path.abspath(os.path.join(here, *rel))
        if os.path.exists(os.path.join(cand, "vec_env.py")):
            return cand
    raise ImportError(f"anakin sim/ (vec_env.py) not found relative to {here}")


_SIM = _find_sim()
if _SIM not in sys.path:
    sys.path.insert(0, _SIM)

from vec_env import BatchedManeuverEnv  # noqa: E402
from render import IMG                  # noqa: E402


class _Handle:
    """One env-slot facing simulate. reset()/step() return thunks the adapter resolves in batch."""

    metadata = {}

    def __init__(self, adapter, i):
        self._ad = adapter
        self._i = i
        self._new_id()

    def _new_id(self):
        # fresh per-episode id (replicates wrappers.UUID): keeps tools.simulate from concatenating
        # successive episodes of the same slot into one cache entry.
        ts = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
        self.id = f"anakin{self._i}-{ts}-{uuid.uuid4().hex}"

    @property
    def observation_space(self):
        return self._ad.observation_space

    @property
    def action_space(self):
        return self._ad.action_space

    def reset(self):
        self._new_id()
        self._ad._mark_reset(self._i)
        return lambda: self._ad._resolve_reset(self._i)

    def step(self, action):
        self._ad._mark_step(self._i, action)
        return lambda: self._ad._resolve_step(self._i)

    def close(self):
        pass


class BatchedSimAdapter:
    """Wraps one BatchedManeuverEnv; exposes `.handles` (list of N) for tools.simulate(envs=...)."""

    def __init__(self, n_envs=256, device="cuda", max_steps=1200, dt=0.02,
                 ground_start_prob=0.5, seed=0):
        self.N = int(n_envs)
        self.env = BatchedManeuverEnv(
            n_envs=self.N, max_steps=max_steps, dt=dt, device=device,
            ground_start_prob=ground_start_prob, seed=seed, auto_reset=False,
        )
        self.observation_space = gym.spaces.Dict({
            "image": gym.spaces.Box(0, 255, (IMG, IMG, 3), dtype=np.uint8),
        })
        self.action_space = gym.spaces.Box(-1.0, 1.0, (4,), dtype=np.float32)
        self.handles = [_Handle(self, i) for i in range(self.N)]

        # reset-phase batch state
        self._pending_reset = set()
        self._reset_obs = None
        # step-phase batch state
        self._action = np.zeros((self.N, 4), dtype=np.float32)
        self._step_out = None

    def __len__(self):
        return self.N

    # -- reset phase: simulate calls reset() on the done subset, then resolves all thunks ----------
    def _mark_reset(self, i):
        self._pending_reset.add(i)
        self._reset_obs = None            # invalidate; the batch is recomputed on first resolve

    def _resolve_reset(self, i):
        if self._reset_obs is None:       # first thunk of this phase -> run the batched reset once
            for j in self._pending_reset:
                self.env.reset_one(j)
            self._pending_reset = set()
            self._reset_obs = self.env.obs_numpy()
        return {"image": self._reset_obs[i], "is_first": True, "is_terminal": False}

    # -- step phase: simulate calls step(a_i) on all N, then resolves all thunks -------------------
    def _mark_step(self, i, action):
        if isinstance(action, dict):      # replicate wrappers.SelectAction(key="action")
            action = action["action"]
        self._action[i] = np.asarray(action, dtype=np.float32).reshape(4)
        self._step_out = None             # invalidate; the batch is recomputed on first resolve

    def _resolve_step(self, i):
        if self._step_out is None:        # first thunk of this phase -> ONE batched step for all N
            obs_t, reward, done, infos = self.env.step(self._action)
            self._step_out = (obs_t.detach().cpu().numpy(), reward, done, infos)
        obs_np, reward, done, infos = self._step_out
        terminated = bool(infos[i].get("terminated", False))
        obs = {"image": obs_np[i], "is_first": False, "is_terminal": terminated}
        info = {"discount": np.array(1.0, np.float32), **infos[i]}
        return obs, float(reward[i]), bool(done[i]), info

    def close(self):
        for h in self.handles:
            h.close()


def make_batched(config, seed_offset=0):
    """Build a BatchedSimAdapter from a DreamerV3 config — approach A's replacement for the
    `[make_env(...) for i in range(envs)]` + Damy list. Returns the adapter; pass `.handles` to
    tools.simulate(envs=...). `seed_offset` separates train from eval streams."""
    size = tuple(config.size)
    assert size == (IMG, IMG), f"anakin batched env renders {IMG}x{IMG}; config.size={size}"
    return BatchedSimAdapter(
        n_envs=config.envs,
        device=getattr(config, "anakin_env_device", "cuda"),
        max_steps=config.time_limit,
        ground_start_prob=getattr(config, "anakin_ground_start_prob", 0.5),
        seed=config.seed + seed_offset,
    )
