"""Batched-GPU maneuver vector-env — Phase 3 L3a, the throughput unlock.

Steps N drones at once through the maneuver curriculum: ONE batched dynamics call + ONE batched
render call per tick, instead of N separate envs (which would be N x kernel-launch overhead — the
reason single-env CUDA was *slower* than CPU). The heavy path (dynamics.step, render) stays fully
batched on the GPU; only the light per-env bookkeeping (gate-crossing classification, window
shift, gate generation on pass/reset) touches Python, and only for the usually-small subset of
envs that crossed/terminated on a given tick.

Curriculum decomposition (the correct shape for N parallel learners):
  - ONE shared `MasteryTracker`  -> competence aggregates across all N envs (= "batch-dim mastery")
  - N per-env `SequencePlanner`s -> each env flies its own WORD/SENTENCE/PARAGRAPH/ESSAY stream,
    but all consult the shared mastery to decide complexity + sequence-readiness.

Gate representation: a fixed rolling window of W gates per env (`gate_pos[N,W,3]`), slot 0 = current
target, cur_idx all-zero. On pass: shift the window left, generate one new gate at the end. This
keeps a fixed-shape tensor the batched renderer consumes directly.

Auto-resets internally (a done env is immediately re-seeded) so the batch stays full for continuous
stepping; `done[N]` is still returned so a downstream replay/collection loop cuts episodes correctly.
Reward shape = the maneuver_env racing reward (progress + speed bonus - time + velocity-scaled gate
bonus - crash); Day-124 minimum-time mandate.
"""
import os

import numpy as np
import torch

from dynamics import init_state, step
from render import render, IMG, GATE_INNER, GATE_OUTER
from maneuvers import ManeuverLibrary
from curriculum import MasteryTracker
from sequences import SequencePlanner

# racing reward constants (shared with maneuver_env.py)
GATE_BONUS, PROGRESS_SCALE, TIME_PENALTY = 100.0, 1.5, 5.0
SPEED_BONUS_SCALE, GATE_SPEED_SCALE, CRASH_PENALTY = 0.15, 0.08, 15.0
# VQ1 (chain-reliably-FIRST) reward override — opt-in via ANAKIN_VQ1=1 (Day 141, w/ Clayton).
# VQ1 scores GATE-COUNT; speed is VQ2. The default (Day-124 minimum-TIME mandate) trains a VQ2 policy:
# the speed-SCALED gate bonus + speed bonus reward flying fast, and CRASH_PENALTY(15) << GATE_BONUS(100)
# makes crashing-after-a-gate cheap → fly-fast-and-crash, gate-count stuck ~1.3 (rehearsal Day 141).
# VQ1 reward = flat gate bonus (pass it, don't race it) + crash costs one whole gate (cross-then-crash ≈ 0,
# so the policy must CHAIN to profit) + no speed incentive + minimal time penalty. Reversible; does NOT
# affect an already-running train (env code is loaded at launch).
if os.environ.get("ANAKIN_VQ1") == "1":
    GATE_SPEED_SCALE = 0.0       # flat +100/gate (was speed-scaled)
    SPEED_BONUS_SCALE = 0.0      # no fly-fast incentive (was 0.15)
    CRASH_PENALTY = 100.0        # = GATE_BONUS → chaining required to net positive (was 15)
    TIME_PENALTY = 1.0           # deliberate, anti-hover only (was 5.0)
elif os.environ.get("ANAKIN_VQ1") == "2":
    # VQ1 reward-v2 — the timidity-trap fix (Day 141, basement LC56 + VQ1_BATCH1_VERDICT).
    # v1 set CRASH=GATE=100, which made cross-then-crash net ZERO ⇒ "one gate is enough" became
    # the absorbing fixed point (rehearsal gates 1.3→1.2, no chaining gain). LC56: a productive
    # cycle stays compact iff its competing fixed point is ESCAPABLE = leaving it has positive value.
    # Fix = CRASH < GATE so cross-then-crash nets +(GATE−CRASH)>0 ⇒ the 2nd gate is ALWAYS worth
    # attempting. Chaining-vs-stop threshold drops from p*=c/(g+c)=0.50 (v1) to 40/140=0.29 (v2),
    # covering the early-training success band. SINGLE-VARIABLE vs v1: ONLY crash penalty changes
    # (no superlinear consecutive-gate bonus yet — that's a v3 if v2 still stalls, to keep the test clean).
    GATE_SPEED_SCALE = 0.0       # flat +100/gate (VQ1 = no speed)
    SPEED_BONUS_SCALE = 0.0      # no fly-fast incentive
    CRASH_PENALTY = 40.0         # < GATE_BONUS(100): cross-then-crash nets +60 → trap de-absorbed
    TIME_PENALTY = 1.0           # anti-hover only
HALF_INNER, HALF_OUTER = GATE_INNER / 2.0, GATE_OUTER / 2.0
GROUND_Z, CEIL_Z, ARENA_XY = 0.0, 25.0, 80.0
W = 3                       # rolling gate-window size (current + 2 lookahead)


def _unit(v, eps=1e-6):
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.clip(n, eps, None)


def _gate_axes(fwd):
    f = _unit(np.asarray(fwd, dtype=np.float64))
    up_hint = np.array([0.0, 0.0, 1.0]) if abs(f[2]) <= 0.99 else np.array([0.0, 1.0, 0.0])
    right = _unit(np.cross(f, up_hint))
    up = _unit(np.cross(right, f))
    return right, up


class BatchedManeuverEnv:
    """N-drone batched maneuver curriculum env (custom vector API: reset()->obs[N], step(a[N])->...)."""

    def __init__(self, n_envs=256, max_steps=1200, dt=0.02, device="cuda",
                 ground_start_prob=0.5, seed=0, auto_reset=True):
        self.N = int(n_envs)
        self.max_steps = int(max_steps)
        self.dt = float(dt)
        self.device = device
        # CONTROL-RATE randomization (Day 137, the control-rate-cliff fix): per-env decision dt,
        # resampled each episode, so the policy becomes invariant to the deploy clock (train 50 Hz /
        # deploy 30 Hz killed transfer — CONTROL_RATE_FINDING_2026-06-17.md). Env-var gated so OFF ==
        # byte-identical (scalar self.dt). Default range covers the 30 Hz deploy clock with margin:
        # 0.020..0.040 s = 50..25 Hz. The world model infers the effective rate from observed motion.
        self._rate_rand = os.environ.get("ANAKIN_RATE_RANDOM") == "1"
        self._dt_min = float(os.environ.get("ANAKIN_DT_MIN", "0.020"))
        self._dt_max = float(os.environ.get("ANAKIN_DT_MAX", "0.040"))
        self.dt_vec = np.full(self.N, self.dt, dtype=np.float64)                 # per-env dt (reward)
        self._dt_t = torch.full((self.N, 1), self.dt, dtype=torch.float32, device=device)  # dynamics
        self.ground_start_prob = float(ground_start_prob)
        # auto_reset=True keeps the batch full (custom-loop / benchmark use). auto_reset=False hands
        # reset-ownership to the caller (DreamerV3 tools.simulate, approach A): a done env holds its
        # terminal state until reset_one(i) is called. See PHASE3_DESIGN.md §70 + integration/.
        self.auto_reset = bool(auto_reset)
        self.rng = np.random.default_rng(seed)
        self.lib = ManeuverLibrary()

        # shared mastery (batch-dim) + per-env planners
        self.tracker = MasteryTracker()
        self.planners = [SequencePlanner(self.rng, adaptive=True) for _ in range(self.N)]

        # per-env rolling gate window + cursor bookkeeping (numpy; light)
        self.gpos = np.zeros((self.N, W, 3))
        self.gfwd = np.zeros((self.N, W, 3))
        self.gman = [["sprint"] * W for _ in range(self.N)]   # maneuver name per window slot
        self.heading = np.zeros(self.N)
        self.alt = np.full(self.N, 2.0)
        self.prev_dist = np.zeros(self.N)
        self.t = np.zeros(self.N, dtype=np.int64)
        self.ep_return = np.zeros(self.N)

        self.state = init_state(self.N, device)               # [N,10] on GPU

    # -- per-env helpers ------------------------------------------------------
    def _in_flight_masteries(self):
        m = self.tracker.maneuver_masteries
        return {k: m[k] for k in ManeuverLibrary.IN_FLIGHT}

    def _next_in_flight(self, i, im):
        return self.planners[i].next_maneuver(self.tracker.avg_mastery, im) \
            or self.rng.choice(ManeuverLibrary.IN_FLIGHT)

    def _make_gate(self, last_pos, i, maneuver):
        new_pos, new_head, new_alt = getattr(self.lib, maneuver)(last_pos, self.heading[i],
                                                                 self.alt[i], self.rng)
        fwd = _unit(last_pos - new_pos)
        self.heading[i], self.alt[i] = new_head, new_alt
        return new_pos, fwd

    def _sample_dt(self, i):
        """Per-episode control dt for env i (control-rate randomization). No-op when disabled."""
        if self._rate_rand:
            d = float(self.rng.uniform(self._dt_min, self._dt_max))
            self.dt_vec[i] = d
            self._dt_t[i, 0] = d

    def _reset_env(self, i, im):
        """Re-seed env i: ground (takeoff) or air start, fill the W-gate window."""
        self._sample_dt(i)
        self.heading[i] = float(self.rng.uniform(-np.pi, np.pi))
        ground = self.rng.random() < self.ground_start_prob
        if ground:
            start = np.array([0.0, 0.0, 0.05]); self.alt[i] = 0.05
            first = "takeoff"
        else:
            self.alt[i] = float(self.rng.uniform(1.5, 4.0))
            start = np.array([0.0, 0.0, self.alt[i]])
            first = self._next_in_flight(i, im)
        last = start.copy()
        names = []
        for slot in range(W):
            man = first if slot == 0 else self._next_in_flight(i, im)
            pos, fwd = self._make_gate(last, i, man)
            self.gpos[i, slot] = pos; self.gfwd[i, slot] = fwd
            names.append(man); last = pos
        self.gman[i] = names
        # write state row i (rest at start)
        row = init_state(1, self.device, tuple(start.tolist()))[0]
        self.state[i] = row
        self.t[i] = 0; self.ep_return[i] = 0.0
        self.prev_dist[i] = float(np.linalg.norm(self.gpos[i, 0] - start))

    def _advance_window(self, i, im):
        """Env i passed slot 0: shift window left, append one fresh gate at the end."""
        self.gpos[i, :-1] = self.gpos[i, 1:]; self.gfwd[i, :-1] = self.gfwd[i, 1:]
        self.gman[i] = self.gman[i][1:]
        man = self._next_in_flight(i, im)
        last = self.gpos[i, -2]
        pos, fwd = self._make_gate(last, i, man)
        self.gpos[i, -1] = pos; self.gfwd[i, -1] = fwd
        self.gman[i].append(man)

    # -- obs ------------------------------------------------------------------
    def _obs(self):
        gp = torch.as_tensor(self.gpos, dtype=torch.float32, device=self.device)
        gf = torch.as_tensor(self.gfwd, dtype=torch.float32, device=self.device)
        cur = torch.zeros(self.N, dtype=torch.long, device=self.device)
        return render(self.state, gp, gf, cur, add_noise=True, device=self.device)  # [N,64,64,3] uint8

    # -- API ------------------------------------------------------------------
    def reset(self):
        im = self._in_flight_masteries()
        for i in range(self.N):
            self._reset_env(i, im)
        return self._obs()

    def step(self, actions):
        """actions: [N,4] (np or torch). Returns obs[N,...], reward[N] np, done[N] np, infos(list)."""
        a = torch.as_tensor(np.asarray(actions, dtype=np.float32), device=self.device).reshape(self.N, 4)
        p_prev = self.state[:, 0:3].detach().cpu().numpy().astype(np.float64)
        # per-env dt when rate-randomizing (byte-identical scalar path when off)
        dt_arg = self._dt_t if self._rate_rand else self.dt
        dt_np = self.dt_vec if self._rate_rand else self.dt
        self.state = step(self.state, a, dt=dt_arg)
        p_cur = self.state[:, 0:3].detach().cpu().numpy().astype(np.float64)
        speed = self.state[:, 3:6].norm(dim=-1).detach().cpu().numpy()
        self.t += 1

        c = self.gpos[:, 0, :]; n = self.gfwd[:, 0, :]
        d_cur = np.linalg.norm(c - p_cur, axis=-1)
        reward = PROGRESS_SCALE * (self.prev_dist - d_cur)
        reward += SPEED_BONUS_SCALE * dt_np * speed
        reward -= TIME_PENALTY * dt_np
        self.prev_dist = d_cur

        s_prev = np.einsum("ij,ij->i", p_prev - c, n)
        s_cur = np.einsum("ij,ij->i", p_cur - c, n)
        crossed = (s_prev > 0.0) & (s_cur <= 0.0)

        terminated = np.zeros(self.N, dtype=bool)
        outcomes = ["step"] * self.N
        im = self._in_flight_masteries()

        # classify crossings (only the few that crossed)
        for i in np.nonzero(crossed)[0]:
            frac = s_prev[i] / (s_prev[i] - s_cur[i] + 1e-9)
            p_cross = p_prev[i] + frac * (p_cur[i] - p_prev[i])
            right, up = _gate_axes(n[i])
            d = p_cross - c[i]
            ar, au = abs(d @ right), abs(d @ up)
            if ar <= HALF_INNER and au <= HALF_INNER:
                reward[i] += GATE_BONUS * (1.0 + GATE_SPEED_SCALE * speed[i])
                self.tracker.record(self.gman[i][0], True, speed[i])
                self._advance_window(i, im)
                self.prev_dist[i] = float(np.linalg.norm(self.gpos[i, 0] - p_cur[i]))
                outcomes[i] = "pass"
            elif ar <= HALF_OUTER and au <= HALF_OUTER:
                reward[i] -= CRASH_PENALTY; self.tracker.record(self.gman[i][0], False)
                terminated[i] = True; outcomes[i] = "frame_hit"
            else:
                self.tracker.record(self.gman[i][0], False)
                terminated[i] = True; outcomes[i] = "miss"

        # arena bounds (vectorized) -> oob for those not already terminated
        x, y, z = p_cur[:, 0], p_cur[:, 1], p_cur[:, 2]
        oob = (~terminated) & ((z <= GROUND_Z) | (z >= CEIL_Z) | (np.abs(x) >= ARENA_XY) | (np.abs(y) >= ARENA_XY))
        for i in np.nonzero(oob)[0]:
            reward[i] -= CRASH_PENALTY; self.tracker.record(self.gman[i][0], False)
            terminated[i] = True; outcomes[i] = "oob"

        truncated = (~terminated) & (self.t >= self.max_steps)
        done = terminated | truncated
        self.ep_return += reward

        # episode close + reset. auto_reset=True re-seeds done envs to keep the batch full; with
        # auto_reset=False the done envs hold their terminal state for the caller to reset.
        for i in np.nonzero(done)[0]:
            if truncated[i]:
                outcomes[i] = "timeout"
            if self.auto_reset:
                self.planners[i].on_episode_end()
                self._reset_env(i, im)

        infos = [{"outcome": outcomes[i], "speed": float(speed[i]),
                  "terminated": bool(terminated[i])} for i in range(self.N)]
        return self._obs(), reward.astype(np.float32), done, infos

    def reset_one(self, i):
        """Re-seed env i (approach-A reset-ownership: tools.simulate resets a done slot itself)."""
        self.planners[i].on_episode_end()
        self._reset_env(i, self._in_flight_masteries())

    def obs_numpy(self):
        """Current batched observation as a CPU numpy array [N, IMG, IMG, 3] uint8."""
        return self._obs().detach().cpu().numpy()

    def report(self):
        stats = self.tracker.get_stats()
        lines = [f"avg_mastery {stats['avg_mastery']:.2f}",
                 f"{'maneuver':12s} {'pass':>6s} {'n':>7s} {'speed':>7s}"]
        for m in self.tracker.maneuvers:
            d = stats["per_maneuver"][m]
            lines.append(f"{m:12s} {d['rate']*100:>5.0f}% {d['attempts']:>7d} {d['mean_speed']:>6.1f}m/s")
        return "\n".join(lines)


if __name__ == "__main__":
    import time
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"BatchedManeuverEnv benchmark  device={dev}")
    for N in (64, 256, 1024):
        env = BatchedManeuverEnv(n_envs=N, max_steps=400, device=dev, seed=0)
        obs = env.reset()
        assert obs.shape == (N, IMG, IMG, 3) and obs.dtype == torch.uint8
        hover = np.array([2 * 0.253 - 1, 0.0, 0.02, 0.0], dtype=np.float32)
        acts = np.tile(hover, (N, 1))
        if dev == "cuda": torch.cuda.synchronize()
        t0 = time.time()
        STEPS = 200
        for _ in range(STEPS):
            obs, r, done, infos = env.step(acts + np.random.randn(N, 4).astype(np.float32) * 0.1)
        if dev == "cuda": torch.cuda.synchronize()
        dt = time.time() - t0
        fps = STEPS * N / dt
        print(f"N={N:5d}: {STEPS} steps in {dt:5.2f}s = {fps/1e3:8.1f}k env-steps/s "
              f"({STEPS/dt:6.0f} batched-ticks/s)")
    print("\n--- curriculum after benchmark (N=1024) ---")
    print(env.report())
    print("\nvec_env.py benchmark OK")
