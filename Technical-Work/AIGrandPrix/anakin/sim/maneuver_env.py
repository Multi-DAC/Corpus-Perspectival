"""Anakin maneuver env — the Phase-3 racer: infinite curriculum gates, takeoff, speed reward.

Layer 2 of PHASE3_DESIGN.md. Composes the Phase-2-proven kernels (dynamics + 64x64 FPV renderer)
with the ported grammar (maneuvers + curriculum) into an infinite, maneuver-based, minimum-TIME
racing env. The simple Phase-2 env (`env.py`) is left untouched as the baseline + lesion subject;
this is its racing successor.

Differences from env.py (the two Day-124 mandates + the grammar):
  - **Infinite curriculum gates.** Gates spawn one at a time from `Curriculum` (maneuver grammar
    with WORD->SENTENCE->PARAGRAPH->ESSAY escalation). On passing gate N, gate N+lookahead spawns.
    No fixed track; memorization impossible.
  - **Takeoff / ground-start.** With prob `ground_start_prob` the drone starts at ground rest and
    gate 0 is a `takeoff` (lift off + accelerate into the first gate). Otherwise an air-start with
    an in-flight gate 0. Takeoff competence is recorded to the curriculum like any maneuver.
  - **Speed reward (minimum-time).** Ported from the old racing reward: progress + a raw-speed
    bonus + a per-step time penalty + a velocity-scaled gate bonus (faster crossings pay more)
    + crash penalty. Optimizes the racing line, not just gate-count. (Magnitudes are the racing
    constants; Dreamer's symlog/return-normalization rescales — the SHAPE is the locked mandate.)
  - **Per-maneuver competence.** Each pass/fail (+ crossing speed) is recorded to the curriculum,
    so `env.curriculum.report()` shows per-maneuver pass% AND speed as training proceeds.

Obs/action identical to env.py so the same DreamerV3 integration consumes it:
    obs    = 64x64x3 uint8 RGB (FPV of the current target gate)
    action = CTBR tanh [-1,1]^4
"""
import numpy as np
import torch

from dynamics import init_state, step, map_action
from render import render, IMG, GATE_INNER, GATE_OUTER
from maneuvers import ManeuverLibrary
from curriculum import Curriculum

try:
    import gymnasium as gym
    from gymnasium import spaces
    _HAVE_GYM = True
except Exception:                                            # pragma: no cover
    _HAVE_GYM = False

    class _Box:
        def __init__(self, low, high, shape, dtype):
            self.low, self.high, self.shape, self.dtype = low, high, shape, dtype

        def sample(self):
            return (np.random.uniform(0, 1, size=self.shape).astype(self.dtype)
                    * (self.high - self.low) + self.low)

    class spaces:            # noqa: N801
        Box = _Box

    class gym:               # noqa: N801
        class Env:
            metadata = {}

# --- racing reward constants (ported from sim/infinite_gate_env.py::rc; Day-124 speed mandate) ---
GATE_BONUS        = 100.0
PROGRESS_SCALE    = 1.5
TIME_PENALTY      = 5.0      # * dt per step  — punishes dawdling
SPEED_BONUS_SCALE = 0.15     # * dt per step  — rewards forward speed
GATE_SPEED_SCALE  = 0.08     # gate_bonus * (1 + crossing_speed * this)
CRASH_PENALTY     = 15.0

HALF_INNER = GATE_INNER / 2.0
HALF_OUTER = GATE_OUTER / 2.0
GROUND_Z, CEIL_Z, ARENA_XY = 0.0, 25.0, 80.0
LOOKAHEAD = 3               # gates kept generated ahead of the current target


def _unit(v, eps=1e-6):
    return v / np.linalg.norm(v).clip(min=eps)


def _gate_axes(fwd):
    """Right/up in-plane axes for a gate facing `fwd` (matches render._gate_corners)."""
    f = _unit(np.asarray(fwd, dtype=np.float64))
    up_hint = np.array([0.0, 0.0, 1.0]) if abs(f[2]) <= 0.99 else np.array([0.0, 1.0, 0.0])
    right = _unit(np.cross(f, up_hint))
    up = _unit(np.cross(right, f))
    return right, up


class AnakinManeuverEnv(gym.Env):
    """Single-env Gymnasium surface; infinite maneuver curriculum + speed reward."""

    metadata = {"render_modes": ["rgb_array"]}

    def __init__(self, max_steps=1200, dt=0.02, device="cpu",
                 ground_start_prob=0.5, curriculum=None, seed=None):
        super().__init__()
        self.max_steps = int(max_steps)
        self.dt = float(dt)
        self.device = device
        self.ground_start_prob = float(ground_start_prob)
        self.rng = np.random.default_rng(seed)
        self.lib = ManeuverLibrary()
        # curriculum persists across episodes so mastery accumulates (share one across envs later)
        self.curriculum = curriculum if curriculum is not None else Curriculum(self.rng)

        self.observation_space = spaces.Box(low=0, high=255, shape=(IMG, IMG, 3), dtype=np.uint8)
        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(4,), dtype=np.float32)

        self._state = None
        self._gpos = []          # list of np[3] gate centers (full history this episode)
        self._gfwd = []          # list of np[3] gate normals (face the incoming drone)
        self._gman = []          # list of maneuver-name per gate
        self._cur = 0
        self._t = 0
        self._heading = 0.0
        self._alt = 2.0
        self._prev_dist = None
        self._ep_return = 0.0

    # -- gate generation ------------------------------------------------------
    def _append_gate(self, maneuver):
        """Generate one gate via the given maneuver from the running (pos, heading, alt) cursor."""
        last = self._gpos[-1] if self._gpos else np.array([0.0, 0.0, self._alt])
        new_pos, new_head, new_alt = getattr(self.lib, maneuver)(last, self._heading, self._alt, self.rng)
        prev = last
        fwd = _unit(prev - new_pos)         # normal faces back toward the approach
        self._gpos.append(new_pos)
        self._gfwd.append(fwd)
        self._gman.append(maneuver)
        self._heading, self._alt = new_head, new_alt

    def _ensure_lookahead(self):
        while len(self._gpos) < self._cur + 1 + LOOKAHEAD:
            m = self.curriculum.next_maneuver() or self.rng.choice(ManeuverLibrary.IN_FLIGHT)
            self._append_gate(m)

    # -- obs ------------------------------------------------------------------
    def _pos(self):
        return self._state[0, 0:3].detach().cpu().numpy().astype(np.float64)

    def _speed(self):
        return float(self._state[0, 3:6].norm())

    def _dist_to_cur(self, p):
        return float(np.linalg.norm(self._gpos[self._cur] - p))

    def _obs(self):
        # render a small window [cur : cur+LOOKAHEAD] with the current target at window-index 0
        hi = min(len(self._gpos), self._cur + LOOKAHEAD)
        win_pos = np.stack(self._gpos[self._cur:hi])
        win_fwd = np.stack(self._gfwd[self._cur:hi])
        gp = torch.tensor(win_pos, dtype=torch.float32, device=self.device)[None]
        gf = torch.tensor(win_fwd, dtype=torch.float32, device=self.device)[None]
        cur = torch.tensor([0], dtype=torch.long, device=self.device)
        frame = render(self._state, gp, gf, cur, add_noise=True, device=self.device)
        return frame[0].cpu().numpy()

    # -- Gymnasium API --------------------------------------------------------
    def reset(self, *, seed=None, options=None):
        if seed is not None:
            self.rng = np.random.default_rng(seed)
        self._gpos, self._gfwd, self._gman = [], [], []
        self._cur, self._t, self._ep_return = 0, 0, 0.0
        self._heading = float(self.rng.uniform(-np.pi, np.pi))

        ground = self.rng.random() < self.ground_start_prob
        if ground:
            start = np.array([0.0, 0.0, 0.05])      # ground rest
            self._alt = 0.05
            self._gpos.append(np.array([0.0, 0.0, 0.05]))  # phantom "prev" at the start
            self._gfwd.append(np.array([1.0, 0.0, 0.0]))
            self._gman.append("_start")
            self._cur = 1                            # gate 1 is the real first target (takeoff)
            self._append_gate("takeoff")
        else:
            self._alt = float(self.rng.uniform(1.5, 4.0))
            start = np.array([0.0, 0.0, self._alt])
            self._gpos.append(start.copy()); self._gfwd.append(np.array([1.0, 0.0, 0.0]))
            self._gman.append("_start")
            self._cur = 1
            self._append_gate(self.curriculum.next_maneuver() or self.rng.choice(ManeuverLibrary.IN_FLIGHT))

        self._state = init_state(1, self.device, tuple(start.tolist()))
        self._ensure_lookahead()
        self._prev_dist = self._dist_to_cur(self._pos())
        return self._obs(), {}

    def step(self, action):
        a = torch.as_tensor(np.asarray(action, dtype=np.float32), device=self.device).reshape(1, 4)
        p_prev = self._pos()
        self._state = step(self._state, a, dt=self.dt)
        p_cur = self._pos()
        self._t += 1
        speed = self._speed()

        reward, terminated, truncated, outcome = 0.0, False, False, "step"

        # progress toward the current gate + raw-speed bonus + per-step time penalty
        d_cur = self._dist_to_cur(p_cur)
        reward += PROGRESS_SCALE * (self._prev_dist - d_cur)
        reward += SPEED_BONUS_SCALE * self.dt * speed
        reward -= TIME_PENALTY * self.dt
        self._prev_dist = d_cur

        # gate-plane crossing
        c = self._gpos[self._cur]
        n = self._gfwd[self._cur]
        s_prev = float(np.dot(p_prev - c, n))
        s_cur = float(np.dot(p_cur - c, n))
        if s_prev > 0.0 and s_cur <= 0.0:
            frac = s_prev / (s_prev - s_cur + 1e-9)
            p_cross = p_prev + frac * (p_cur - p_prev)
            d = p_cross - c
            right, up = _gate_axes(n)
            ar, au = abs(float(np.dot(d, right))), abs(float(np.dot(d, up)))
            if ar <= HALF_INNER and au <= HALF_INNER:
                reward += GATE_BONUS * (1.0 + GATE_SPEED_SCALE * speed)   # speed-scaled pass bonus
                self.curriculum.record_gate(self._gman[self._cur], success=True, speed=speed)
                outcome = "pass"
                self._cur += 1
                self._ensure_lookahead()
                self._prev_dist = self._dist_to_cur(p_cur)
            elif ar <= HALF_OUTER and au <= HALF_OUTER:
                reward -= CRASH_PENALTY
                self.curriculum.record_gate(self._gman[self._cur], success=False)
                terminated, outcome = True, "frame_hit"
            else:
                self.curriculum.record_gate(self._gman[self._cur], success=False)
                terminated, outcome = True, "miss"

        # arena collisions (count as failing the current maneuver)
        if not terminated:
            x, y, z = p_cur
            if z <= GROUND_Z or z >= CEIL_Z or abs(x) >= ARENA_XY or abs(y) >= ARENA_XY:
                reward -= CRASH_PENALTY
                self.curriculum.record_gate(self._gman[self._cur], success=False)
                terminated, outcome = True, "oob"

        if not terminated and self._t >= self.max_steps:
            truncated, outcome = True, "timeout"

        self._ep_return += reward
        if terminated or truncated:
            self.curriculum.on_episode_end(completed_all_gates=False)

        info = {"outcome": outcome, "gate": self._cur - 1, "maneuver": self._gman[self._cur],
                "speed": speed, "ep_return": self._ep_return}
        return self._obs(), float(reward), terminated, truncated, info

    def render(self):
        return self._obs()

    def close(self):
        pass


if __name__ == "__main__":
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"AnakinManeuverEnv self-test  device={dev}  gym={'yes' if _HAVE_GYM else 'shim'}")
    env = AnakinManeuverEnv(max_steps=300, device=dev, ground_start_prob=1.0, seed=0)
    obs, _ = env.reset(seed=0)
    assert obs.shape == (IMG, IMG, 3) and obs.dtype == np.uint8
    assert env._gman[env._cur] == "takeoff", "ground-start episode must target takeoff first"
    print(f"reset OK: obs {obs.shape}  first target = {env._gman[env._cur]}  lookahead={len(env._gpos)-env._cur}")

    outcomes = {}
    for ep in range(30):
        env.reset(seed=ep)
        done = False
        while not done:
            obs, r, term, trunc, info = env.step(env.action_space.sample())
            done = term or trunc
        outcomes[info["outcome"]] = outcomes.get(info["outcome"], 0) + 1
    print(f"random policy x30 outcomes: {outcomes}")

    # scripted takeoff+forward: full-ish thrust + gentle pitch should make progress / lift off
    env.reset(seed=1)
    from dynamics import HOVER
    a_climb = np.array([2 * 0.6 - 1, 0.0, 0.08, 0.0], dtype=np.float32)  # >hover thrust, gentle pitch
    ret = 0.0
    for _ in range(120):
        obs, r, term, trunc, info = env.step(a_climb)
        ret += r
        if term or trunc:
            break
    print(f"scripted climb+fwd: return={ret:+.1f} last={info['outcome']} reached_alt={env._pos()[2]:.2f}")
    print("\n--- curriculum after 30 random eps ---")
    print(env.curriculum.report())
    print("\nmaneuver_env.py self-test OK")
