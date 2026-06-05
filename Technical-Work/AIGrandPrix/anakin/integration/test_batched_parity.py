"""Phase-3 approach-A correctness gate: prove the BatchedSimAdapter is behaviorally faithful BEFORE
spending any training compute.  Nothing trains until this is green.

  [A] index integrity  — each of N envs is stepped by ITS OWN action (no batch scramble/transpose).
                          Reference: pure dynamics.step on each env's own pre-state+action.
  [B] reset isolation   — reset_one(j) re-seeds ONLY slot j; all other slots stay byte-identical
                          (validates the auto_reset=False reset-ownership handed to simulate).
  [D] simulate smoke    — the real upstream tools.simulate() drives the adapter handles end-to-end,
                          collecting episodes without error (the actual integration contract).
"""
import collections
import os
import sys
import tempfile
from pathlib import Path

import numpy as np
import torch

_HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(_HERE, "..", "sim")))
from dynamics import step as dyn_step  # noqa: E402

from batched_sim_adapter import BatchedSimAdapter  # noqa: E402

DEV = "cuda" if torch.cuda.is_available() else "cpu"


# -- simulate's access pattern, reproduced for unit testing -----------------------------------------
def _drive_reset(ad, indices):
    thunks = [ad.handles[i].reset() for i in indices]   # mark all first ...
    return [t() for t in thunks]                         # ... then resolve (collect-then-resolve)


def _drive_step(ad, actions):
    thunks = [ad.handles[i].step(actions[i]) for i in range(ad.N)]
    return [t() for t in thunks]


def test_index_integrity():
    N = 8
    ad = BatchedSimAdapter(n_envs=N, device=DEV, seed=0, ground_start_prob=0.0)
    _drive_reset(ad, range(N))                           # initial reset of all slots
    S0 = ad.env.state.clone()                            # [N,10] pre-step state

    base = np.array([2 * 0.253 - 1, 0.0, 0.0, 0.0], dtype=np.float32)
    actions = np.stack([base + np.array([0.0, 0.03 * i, 0.02 * i, 0.0], np.float32)
                        for i in range(N)])              # each env a DISTINCT action

    _drive_step(ad, actions)

    for i in range(N):                                   # env i's post-state == dynamics(its own a, its own s0)
        a_i = torch.as_tensor(actions[i:i + 1], device=DEV)
        expected = dyn_step(S0[i:i + 1], a_i, dt=ad.env.dt)
        got = ad.env.state[i:i + 1]
        assert torch.allclose(expected, got, atol=1e-5), \
            f"env {i}: batched step did not apply env {i}'s own action to env {i}'s own state"
    print(f"  [A] index integrity  — N={N} envs each stepped by their OWN action  OK")


def test_reset_isolation():
    N = 6
    ad = BatchedSimAdapter(n_envs=N, device=DEV, seed=1, ground_start_prob=0.0)
    _drive_reset(ad, range(N))
    S0 = ad.env.state.clone()
    g0 = ad.env.gpos.copy()

    ad.env.reset_one(2)                                  # simulate would call this on a done slot

    for i in range(N):
        if i == 2:
            continue
        assert torch.equal(ad.env.state[i], S0[i]), f"reset_one(2) perturbed env {i} state"
        assert np.array_equal(ad.env.gpos[i], g0[i]), f"reset_one(2) perturbed env {i} gates"
    assert not torch.equal(ad.env.state[2], S0[2]), "env 2 should have been re-seeded"
    print(f"  [B] reset isolation  — reset_one(2) touched ONLY slot 2  OK")


def test_simulate_smoke():
    # import the vendored DreamerV3 collection loop
    sys.path.insert(0, os.path.abspath(os.path.join(_HERE, "..", "third_party", "dreamerv3-torch")))
    import tools as dreamer_tools

    class _FakeLogger:
        def __init__(self):
            self.step = 0

        def scalar(self, *a, **k):
            pass

        def video(self, *a, **k):
            pass

        def write(self, *a, **k):
            pass

    N, MAXS = 8, 200
    ad = BatchedSimAdapter(n_envs=N, device=DEV, seed=0, ground_start_prob=0.3, max_steps=MAXS)
    cache = collections.OrderedDict()
    tmp = Path(tempfile.mkdtemp(prefix="anakin_sim_smoke_"))

    # faithful agent: returns a DICT of torch tensors, exactly like DreamerV3's actor / random_actor
    # (exercises wrappers.SelectAction unwrap + .detach().cpu() in simulate's dict path).
    def agent(obs, done, state):
        assert obs["image"].shape == (N, 64, 64, 3), f"agent got obs {obs['image'].shape}"
        n = len(done)
        return {"action": torch.rand(n, 4) * 2 - 1, "logprob": torch.zeros(n)}, None

    dreamer_tools.simulate(agent, ad.handles, cache, tmp, _FakeLogger(),
                           is_eval=False, limit=200_000, steps=4800)   # ~600 ticks -> real turnover

    assert len(cache) >= 1, "tools.simulate collected no episode caches"
    good = [k for k, ep in cache.items()
            if "image" in ep and "action" in ep and len(ep["reward"]) > 1]
    assert good, "collected caches are malformed (missing image/action/reward)"
    # turnover happened (more episodes than slots) ...
    assert len(cache) > N, f"expected episode turnover (>{N} ids), got {len(cache)}"
    # ... and the per-episode UUID prevented cross-episode concatenation: NO cache entry can be
    # longer than one episode (a fixed-id bug would glue many episodes into one >> max_steps).
    longest = max(len(ep["reward"]) for ep in cache.values())
    assert longest <= MAXS + 2, f"cache concatenated episodes (len {longest} > max_steps {MAXS}) — UUID broken"
    print(f"  [D] simulate smoke   — dict-action agent, {len(cache)} distinct episodes, "
          f"longest {longest}<= {MAXS} (no concat)  OK")


if __name__ == "__main__":
    print(f"Phase-3 approach-A parity gate  device={DEV}")
    test_index_integrity()
    test_reset_isolation()
    test_simulate_smoke()
    print("\nALL PARITY CHECKS GREEN — approach A is behaviorally faithful; cleared for wiring + training.")
