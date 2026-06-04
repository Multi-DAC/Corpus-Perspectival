"""
Anakin training-sim environment — Gymnasium env wrapping the GPU dynamics + FPV renderer.

Phase 1.3 of anakin/ROADMAP.md. Composes sim/dynamics.py (CTBR rigid-body) and sim/render.py
(64x64 FPV) into a Dream-to-Fly-style RL env:

    obs    = 64x64x3 uint8 RGB  (FPV from the drone, render.render)
    action = CTBR tanh [-1,1]^4 (collective, wx, wy, wz -> dynamics.step)
    reward = progress  b1*(||g - p_{k-1}|| - ||g - p_k||)        (toward current gate)
             - body    b2*||omega||                              (smoothness; b2 CURRICULUM)
             + pass     +10  when the drone crosses a gate plane WITHIN the inner aperture
             - crash    -4   on collision (ground / out-of-arena / hitting a gate frame)
    episode= a sequence of gates; ends on collision, on completing all gates, or timeout.

Single-env Gymnasium API (the standard surface DreamerV3 wraps). Internally everything runs as
batched torch [1, ...] so it reuses the *exact* batched kernels the scaling run will use — no
second code path to keep in sync. Move to GPU with device="cuda".

b2 CURRICULUM (roadmap 1.3): body-rate penalty starts at 0 so the policy first learns to *reach*
gates; once an episode clears the reward bar (>= B2_THRESHOLD) the env ratchets b2 up to B2_MAX so
the policy then learns to fly *smoothly*. Penalising smoothness before the policy can fly at all
just suppresses exploration. Tracked across resets on the env instance.

DOMAIN-RANDOMIZATION hooks (roadmap 1.3): start-pose jitter, gate-position jitter, and a
difficulty knob (lateral/vertical gate spread) are live here. Background noise is already in
render.render(add_noise). Appearance/lighting jitter (gate-color, BG_GRAY) is a render-side
extension flagged for Phase 4 transfer — the hook (self.dr) is threaded so it can feed render
once render grows appearance args; today it scales the geometric randomization.

Runs WITHOUT gymnasium installed (Phase 0.2 installs it): a tiny shim provides spaces.Box + Env so
the __main__ random-policy self-test exercises the full loop on torch+numpy alone.
"""
import numpy as np
import torch

from dynamics import init_state, step, map_action, HOVER
from render import render, IMG, GATE_INNER, GATE_OUTER

# --- gymnasium if present, else a minimal shim so this file self-tests pre-install (Phase 0.2) ---
try:
    import gymnasium as gym
    from gymnasium import spaces
    _HAVE_GYM = True
except Exception:                                            # pragma: no cover - pre-0.2 fallback
    _HAVE_GYM = False

    class _Box:
        def __init__(self, low, high, shape, dtype):
            self.low, self.high, self.shape, self.dtype = low, high, shape, dtype

        def sample(self):
            return np.random.uniform(0, 1, size=self.shape).astype(self.dtype) * \
                (self.high - self.low) + self.low

    class spaces:            # noqa: N801 - mimic gymnasium.spaces namespace
        Box = _Box

    class gym:               # noqa: N801 - mimic gymnasium.Env base
        class Env:
            metadata = {}

# --- reward / episode constants (Dream-to-Fly; roadmap 1.3) ---
B1            = 1.0          # progress gain
B2_MAX        = 0.01         # body-rate penalty (curriculum target)
B2_THRESHOLD  = 50.0         # episode return that unlocks the body-rate penalty
PASS_REWARD   = 10.0
CRASH_REWARD  = -4.0
HALF_INNER    = GATE_INNER / 2.0    # 0.75 m  fly-through aperture half-side
HALF_OUTER    = GATE_OUTER / 2.0    # 1.35 m  physical frame half-side (hitting it = crash)

# --- arena / collision bounds (m) ---
GROUND_Z      = 0.0
CEIL_Z        = 25.0
ARENA_XY      = 60.0        # |x|,|y| beyond this = flew out of bounds


def _unit(v, eps=1e-6):
    return v / np.linalg.norm(v).clip(min=eps)


def _gate_axes(fwd):
    """Right/up in-plane axes for a gate facing `fwd` — matches render._gate_corners convention."""
    f = _unit(np.asarray(fwd, dtype=np.float64))
    up_hint = np.array([0.0, 0.0, 1.0]) if abs(f[2]) <= 0.99 else np.array([0.0, 1.0, 0.0])
    right = _unit(np.cross(f, up_hint))
    up = _unit(np.cross(right, f))
    return right, up


def make_track(n_gates, rng, spacing=6.0, lateral=2.0, vmargin=1.0,
               height=2.0, difficulty=0.0):
    """Procedural straight-ish gate course along +X (Phase 1.3 minimal; Phase 3 = full generator).

    Gates march out in +X at `spacing`; lateral(y)/vertical(z) jitter scales with `difficulty`.
    Each gate faces back toward the previous waypoint, so its normal points at the incoming drone.
    Returns (gate_pos [G,3], gate_fwd [G,3], start_pos [3]) as float64 numpy.
    """
    start = np.array([0.0, 0.0, height])
    pos = np.zeros((n_gates, 3))
    x = spacing
    for i in range(n_gates):
        y = (rng.random() * 2 - 1) * lateral * difficulty
        z = height + (rng.random() * 2 - 1) * vmargin * difficulty
        pos[i] = [x, y, z]
        x += spacing
    fwd = np.zeros((n_gates, 3))
    for i in range(n_gates):
        prev = start if i == 0 else pos[i - 1]
        fwd[i] = _unit(prev - pos[i])      # normal faces back toward the approach
    return pos, fwd, start


class AnakinEnv(gym.Env):
    """Single-env Gymnasium surface over the batched torch sim (N=1 internally)."""

    metadata = {"render_modes": ["rgb_array"]}

    def __init__(self, n_gates=3, max_steps=400, dt=0.02, device="cpu",
                 difficulty=0.0, spacing=6.0, dr=None, seed=None):
        super().__init__()
        self.n_gates = int(n_gates)
        self.max_steps = int(max_steps)
        self.dt = float(dt)
        self.device = device
        self.difficulty = float(difficulty)
        self.spacing = float(spacing)
        self.dr = dict(pose_jitter=0.3, gate_jitter=0.3) if dr is None else dict(dr)
        self.rng = np.random.default_rng(seed)

        # curriculum state persists across episodes on this instance
        self.b2 = 0.0

        self.observation_space = spaces.Box(low=0, high=255, shape=(IMG, IMG, 3), dtype=np.uint8)
        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(4,), dtype=np.float32)

        self._t = 0
        self._state = None          # [1,10] torch
        self._gate_pos = None       # [1,G,3] torch
        self._gate_fwd = None       # [1,G,3] torch
        self._cur = 0
        self._prev_dist = None
        self._ep_return = 0.0
        self._np_pos = None         # [G,3] numpy (for plane math)
        self._np_fwd = None

    # -- helpers -----------------------------------------------------------------
    def _obs(self):
        cur = torch.tensor([self._cur], dtype=torch.long, device=self.device)
        frame = render(self._state, self._gate_pos, self._gate_fwd, cur,
                       add_noise=True, device=self.device)
        return frame[0].cpu().numpy()           # [64,64,3] uint8

    def _pos(self):
        return self._state[0, 0:3].detach().cpu().numpy().astype(np.float64)

    def _dist_to_cur(self, p):
        return float(np.linalg.norm(self._np_pos[self._cur] - p))

    # -- Gymnasium API -----------------------------------------------------------
    def reset(self, *, seed=None, options=None):
        if seed is not None:
            self.rng = np.random.default_rng(seed)
        gp, gf, start = make_track(self.n_gates, self.rng, spacing=self.spacing,
                                   difficulty=self.difficulty)
        # DR: jitter start pose and gate positions (scaled by difficulty-independent dr knobs)
        start = start + (self.rng.random(3) * 2 - 1) * self.dr["pose_jitter"]
        gp = gp + (self.rng.random(gp.shape) * 2 - 1) * self.dr["gate_jitter"]

        self._np_pos, self._np_fwd = gp, gf
        self._state = init_state(1, self.device, tuple(start.tolist()))
        self._gate_pos = torch.tensor(gp, dtype=torch.float32, device=self.device)[None]
        self._gate_fwd = torch.tensor(gf, dtype=torch.float32, device=self.device)[None]
        self._cur = 0
        self._t = 0
        self._ep_return = 0.0
        self._prev_dist = self._dist_to_cur(self._pos())
        return self._obs(), {}

    def step(self, action):
        a = torch.as_tensor(np.asarray(action, dtype=np.float32), device=self.device).reshape(1, 4)
        p_prev = self._pos()

        self._state = step(self._state, a, dt=self.dt)
        p_cur = self._pos()
        self._t += 1

        reward = 0.0
        terminated = False
        truncated = False
        outcome = "step"

        # --- progress toward the current gate ---
        d_cur = self._dist_to_cur(p_cur)
        reward += B1 * (self._prev_dist - d_cur)
        self._prev_dist = d_cur

        # --- body-rate penalty (curriculum-gated b2) ---
        _, omega = map_action(a)
        reward -= self.b2 * float(omega.norm())

        # --- gate-plane crossing: pass / frame-hit / clean miss ---
        c = self._np_pos[self._cur]
        n = self._np_fwd[self._cur]
        s_prev = float(np.dot(p_prev - c, n))
        s_cur = float(np.dot(p_cur - c, n))
        if s_prev > 0.0 and s_cur <= 0.0:                 # crossed front -> back this tick
            frac = s_prev / (s_prev - s_cur + 1e-9)
            p_cross = p_prev + frac * (p_cur - p_prev)
            d = p_cross - c
            right, up = _gate_axes(n)
            ar, au = abs(float(np.dot(d, right))), abs(float(np.dot(d, up)))
            if ar <= HALF_INNER and au <= HALF_INNER:
                reward += PASS_REWARD
                outcome = "pass"
                self._cur += 1
                if self._cur >= self.n_gates:
                    terminated = True
                    outcome = "complete"
                else:
                    self._prev_dist = self._dist_to_cur(p_cur)   # retarget next gate
            elif ar <= HALF_OUTER and au <= HALF_OUTER:
                reward += CRASH_REWARD                    # hit the physical frame
                terminated = True
                outcome = "frame_hit"
            else:
                terminated = True                          # flew past, missed the gate entirely
                outcome = "miss"

        # --- arena collisions ---
        if not terminated:
            x, y, z = p_cur
            if z <= GROUND_Z or z >= CEIL_Z or abs(x) >= ARENA_XY or abs(y) >= ARENA_XY:
                reward += CRASH_REWARD
                terminated = True
                outcome = "oob"

        # --- timeout ---
        if not terminated and self._t >= self.max_steps:
            truncated = True
            outcome = "timeout"

        self._ep_return += reward

        # --- b2 curriculum: unlock smoothness penalty once the policy can reach gates ---
        if (terminated or truncated) and self._ep_return >= B2_THRESHOLD and self.b2 < B2_MAX:
            self.b2 = B2_MAX

        info = {"outcome": outcome, "gate": self._cur, "ep_return": self._ep_return, "b2": self.b2}
        return self._obs(), float(reward), terminated, truncated, info

    def render(self):
        return self._obs()

    def close(self):
        pass


if __name__ == "__main__":
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"AnakinEnv self-test  device={dev}  gymnasium={'yes' if _HAVE_GYM else 'shim'}")
    env = AnakinEnv(n_gates=3, max_steps=300, device=dev, difficulty=0.3, seed=0)

    obs, info = env.reset(seed=0)
    print(f"reset: obs {obs.shape} {obs.dtype}  act_space {env.action_space.shape}")
    assert obs.shape == (IMG, IMG, 3) and obs.dtype == np.uint8

    # --- random policy: confirm the loop runs and episodes terminate sanely ---
    outcomes = {}
    returns = []
    for ep in range(20):
        env.reset(seed=ep)
        ep_ret, steps, done = 0.0, 0, False
        while not done:
            a = env.action_space.sample()
            obs, r, term, trunc, info = env.step(a)
            ep_ret += r
            steps += 1
            done = term or trunc
        outcomes[info["outcome"]] = outcomes.get(info["outcome"], 0) + 1
        returns.append(ep_ret)
    print(f"random policy x20: outcomes={outcomes}")
    print(f"  return mean={np.mean(returns):+.2f} min={np.min(returns):+.2f} max={np.max(returns):+.2f}")

    # --- scripted hover-forward: should make positive progress (sanity on reward sign) ---
    env2 = AnakinEnv(n_gates=1, max_steps=200, device=dev, difficulty=0.0, dr={"pose_jitter": 0.0, "gate_jitter": 0.0}, seed=1)
    env2.reset(seed=1)
    a_fwd = np.array([2 * HOVER - 1, 0.0, 0.10, 0.0], dtype=np.float32)  # hover thrust + gentle pitch fwd
    ret, gate_passed = 0.0, False
    for _ in range(200):
        obs, r, term, trunc, info = env2.step(a_fwd)
        ret += r
        if info["outcome"] == "pass" or info["outcome"] == "complete":
            gate_passed = True
        if term or trunc:
            print(f"scripted fwd: return={ret:+.2f} last_outcome={info['outcome']} gate_passed={gate_passed}")
            break
    else:
        print(f"scripted fwd: return={ret:+.2f} (no termination in 200) gate_passed={gate_passed}")

    # --- throughput: env step rate (single env; render+dynamics+reward) ---
    import time
    env3 = AnakinEnv(n_gates=5, max_steps=100000, device=dev, seed=2)
    env3.reset(seed=2)
    a = np.array([2 * HOVER - 1, 0.0, 0.0, 0.0], dtype=np.float32)
    if dev == "cuda":
        torch.cuda.synchronize()
    t0 = time.time()
    n = 2000
    for _ in range(n):
        _, _, term, trunc, _ = env3.step(a)
        if term or trunc:
            env3.reset()
    if dev == "cuda":
        torch.cuda.synchronize()
    dt = time.time() - t0
    print(f"THROUGHPUT single-env: {n} steps in {dt:.2f}s = {n/dt:.0f} steps/s")
