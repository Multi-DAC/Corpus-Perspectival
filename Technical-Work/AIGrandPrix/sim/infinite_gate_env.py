"""
Infinite Gate Environment — Procedural Maneuver Training

Instead of pre-defined tracks, gates spawn one at a time based on
a library of maneuver formulas. Each gate transition tests a specific
flying skill. The agent trains on an infinite stream of randomized
maneuvers, making memorization impossible.

Maneuver Library:
    sprint      — far gate, same heading (top speed)
    gentle_arc  — medium distance, small turn (smooth racing)
    hard_turn   — medium distance, 60-120 deg (banking)
    hairpin     — close gate, 140-180 deg reversal (deceleration)
    climb       — next gate higher (thrust management)
    dive        — next gate lower (controlled descent)
    chicane     — S-curve pair (rapid direction changes)
    speed_trap  — long straight then tight turn (braking)
    spiral      — consistent turn + altitude gain (coordination)
    threading   — very close gates (precision)
    diagonal    — horizontal turn + altitude change (3D skill)

Architecture by Clayton Walsh, Feb 11, 2026.
"""

from collections import deque
import numpy as np
import gymnasium as gym
from gymnasium import spaces

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from drone_env_v2 import DroneRacingEnvV2, QuadParams
from sequence_generators import SequencePlanner


# ============================================================
# Maneuver Library — Each returns (next_gate_pos, maneuver_name)
# ============================================================

class ManeuverLibrary:
    """
    Library of gate placement formulas.
    Each maneuver: (current_pos, heading, rng) -> (next_pos, new_heading)
    """
    
    MANEUVERS = [
        'sprint', 'gentle_arc', 'hard_turn', 'hairpin',
        'climb', 'dive', 'chicane', 'speed_trap',
        'spiral', 'threading', 'diagonal',
    ]
    
    @staticmethod
    def sprint(pos, heading, alt, rng):
        """Far gate, same heading — tests top speed."""
        dist = rng.uniform(10, 22)
        angle_change = rng.uniform(-0.1, 0.1)  # Near-straight
        alt_change = rng.uniform(-0.3, 0.3)
        
        new_heading = heading + angle_change
        new_pos = pos + np.array([
            dist * np.cos(new_heading),
            dist * np.sin(new_heading),
            0.0
        ])
        new_alt = np.clip(alt + alt_change, 0.5, 12.0)
        new_pos[2] = new_alt
        return new_pos, new_heading, new_alt
    
    @staticmethod
    def gentle_arc(pos, heading, alt, rng):
        """Medium distance, 10-30 deg turn — smooth racing line."""
        dist = rng.uniform(6, 14)
        angle_change = rng.choice([-1, 1]) * rng.uniform(0.17, 0.52)  # 10-30 deg
        alt_change = rng.uniform(-0.5, 0.5)
        
        new_heading = heading + angle_change
        new_pos = pos + np.array([
            dist * np.cos(new_heading),
            dist * np.sin(new_heading),
            0.0
        ])
        new_alt = np.clip(alt + alt_change, 0.5, 12.0)
        new_pos[2] = new_alt
        return new_pos, new_heading, new_alt
    
    @staticmethod
    def hard_turn(pos, heading, alt, rng):
        """Medium distance, 60-120 deg — banking skill."""
        dist = rng.uniform(4, 10)
        angle_change = rng.choice([-1, 1]) * rng.uniform(1.05, 2.09)  # 60-120 deg
        alt_change = rng.uniform(-0.5, 0.5)
        
        new_heading = heading + angle_change
        new_pos = pos + np.array([
            dist * np.cos(new_heading),
            dist * np.sin(new_heading),
            0.0
        ])
        new_alt = np.clip(alt + alt_change, 0.5, 12.0)
        new_pos[2] = new_alt
        return new_pos, new_heading, new_alt
    
    @staticmethod
    def hairpin(pos, heading, alt, rng):
        """Close gate, 140-180 deg reversal — deceleration + flip."""
        dist = rng.uniform(3, 6)
        angle_change = rng.choice([-1, 1]) * rng.uniform(2.44, 3.14)  # 140-180 deg
        alt_change = rng.uniform(-0.3, 0.3)
        
        new_heading = heading + angle_change
        new_pos = pos + np.array([
            dist * np.cos(new_heading),
            dist * np.sin(new_heading),
            0.0
        ])
        new_alt = np.clip(alt + alt_change, 0.5, 12.0)
        new_pos[2] = new_alt
        return new_pos, new_heading, new_alt
    
    @staticmethod
    def climb(pos, heading, alt, rng):
        """Next gate significantly higher — thrust management."""
        dist = rng.uniform(5, 12)
        angle_change = rng.uniform(-0.3, 0.3)
        alt_change = rng.uniform(2.0, 5.0)
        
        new_heading = heading + angle_change
        new_pos = pos + np.array([
            dist * np.cos(new_heading),
            dist * np.sin(new_heading),
            0.0
        ])
        new_alt = np.clip(alt + alt_change, 0.5, 12.0)
        new_pos[2] = new_alt
        return new_pos, new_heading, new_alt
    
    @staticmethod
    def dive(pos, heading, alt, rng):
        """Next gate significantly lower — controlled descent."""
        dist = rng.uniform(5, 12)
        angle_change = rng.uniform(-0.3, 0.3)
        alt_change = rng.uniform(-5.0, -2.0)
        
        new_heading = heading + angle_change
        new_pos = pos + np.array([
            dist * np.cos(new_heading),
            dist * np.sin(new_heading),
            0.0
        ])
        new_alt = np.clip(alt + alt_change, 0.5, 12.0)
        new_pos[2] = new_alt
        return new_pos, new_heading, new_alt
    
    @staticmethod
    def chicane(pos, heading, alt, rng):
        """S-curve — rapid direction change."""
        dist = rng.uniform(3, 6)
        angle_change = rng.choice([-1, 1]) * rng.uniform(0.7, 1.2)  # 40-70 deg
        alt_change = rng.uniform(-0.3, 0.3)
        
        new_heading = heading + angle_change
        new_pos = pos + np.array([
            dist * np.cos(new_heading),
            dist * np.sin(new_heading),
            0.0
        ])
        new_alt = np.clip(alt + alt_change, 0.5, 12.0)
        new_pos[2] = new_alt
        return new_pos, new_heading, new_alt
    
    @staticmethod
    def speed_trap(pos, heading, alt, rng):
        """Long straight then will be followed by tight turn — tests speed buildup."""
        dist = rng.uniform(12, 24)
        angle_change = rng.uniform(-0.05, 0.05)  # Nearly straight
        alt_change = rng.uniform(-0.2, 0.2)
        
        new_heading = heading + angle_change
        new_pos = pos + np.array([
            dist * np.cos(new_heading),
            dist * np.sin(new_heading),
            0.0
        ])
        new_alt = np.clip(alt + alt_change, 0.5, 12.0)
        new_pos[2] = new_alt
        return new_pos, new_heading, new_alt
    
    @staticmethod
    def spiral(pos, heading, alt, rng):
        """Consistent turning + altitude gain — coordinated flight."""
        dist = rng.uniform(4, 8)
        angle_change = rng.choice([-1, 1]) * rng.uniform(0.5, 0.9)  # 30-50 deg
        alt_change = rng.uniform(0.5, 1.5)  # Always climbing
        
        new_heading = heading + angle_change
        new_pos = pos + np.array([
            dist * np.cos(new_heading),
            dist * np.sin(new_heading),
            0.0
        ])
        new_alt = np.clip(alt + alt_change, 0.5, 12.0)
        new_pos[2] = new_alt
        return new_pos, new_heading, new_alt
    
    @staticmethod
    def threading(pos, heading, alt, rng):
        """Very close gates — precision control."""
        dist = rng.uniform(2.0, 3.5)
        angle_change = rng.choice([-1, 1]) * rng.uniform(0.1, 0.6)  # Small-medium turn
        alt_change = rng.uniform(-0.5, 0.5)
        
        new_heading = heading + angle_change
        new_pos = pos + np.array([
            dist * np.cos(new_heading),
            dist * np.sin(new_heading),
            0.0
        ])
        new_alt = np.clip(alt + alt_change, 0.5, 12.0)
        new_pos[2] = new_alt
        return new_pos, new_heading, new_alt
    
    @staticmethod
    def diagonal(pos, heading, alt, rng):
        """Horizontal turn + altitude change — full 3D skill."""
        dist = rng.uniform(5, 12)
        angle_change = rng.choice([-1, 1]) * rng.uniform(0.5, 1.5)  # 30-85 deg
        alt_change = rng.choice([-1, 1]) * rng.uniform(1.5, 4.0)  # Significant
        
        new_heading = heading + angle_change
        new_pos = pos + np.array([
            dist * np.cos(new_heading),
            dist * np.sin(new_heading),
            0.0
        ])
        new_alt = np.clip(alt + alt_change, 0.5, 12.0)
        new_pos[2] = new_alt
        return new_pos, new_heading, new_alt
    
    def generate(self, pos, heading, alt, rng, maneuver=None):
        """Generate next gate position using a random or specified maneuver."""
        if maneuver is None:
            maneuver = rng.choice(self.MANEUVERS)
        
        func = getattr(self, maneuver)
        new_pos, new_heading, new_alt = func(pos, heading, alt, rng)
        return new_pos, new_heading, new_alt, maneuver


# ============================================================
# Infinite Gate Environment
# ============================================================

class InfiniteGateEnv(gym.Env):
    """
    Procedurally generated infinite gate sequence.
    
    Gates spawn one at a time. On passing gate N, gate N+2 appears.
    Always maintains 2-gate lookahead (current target + next).
    Episode ends on timeout or crash. Score = gates passed.
    
    Tracks per-maneuver success rates for adaptive curriculum.
    """
    
    metadata = {"render_modes": ["none"]}
    
    def __init__(self, 
                 gate_radius=0.75,
                 max_steps=30000,       # 60s at 500Hz
                 dt=0.002,              # 500 Hz
                 substeps=1,
                 domain_rand=False,
                 domain_rand_scale=0.15,
                 adaptive_curriculum=True,
                 ground_start_prob=0.0,   # fraction of episodes that start at ground rest
                 seed=None):
        super().__init__()

        self.gate_radius = gate_radius
        self.max_steps = max_steps
        self.dt = dt
        self.substeps = substeps
        self.domain_rand = domain_rand
        self.domain_rand_scale = domain_rand_scale
        self.adaptive_curriculum = adaptive_curriculum
        self.ground_start_prob = ground_start_prob
        
        self.rng = np.random.default_rng(seed)
        self.library = ManeuverLibrary()
        
        # Reward config (dt-scaled where needed)
        self.rc = {
            'gate_bonus': 100.0,
            'progress_scale': 1.5,
            'time_penalty': 5.0,        # * dt per step
            'crash_penalty': 15.0,
            'speed_bonus_scale': 0.15,  # * dt per step
            'gate_speed_scale': 0.08,   # velocity-scaled gate bonus (gate_bonus * (1 + speed * this)) — doubled from 0.04 to incentivize speed
        }
        
        # Per-maneuver tracking (lifetime — for stats reporting)
        self.maneuver_attempts = {m: 0 for m in ManeuverLibrary.MANEUVERS}
        self.maneuver_successes = {m: 0 for m in ManeuverLibrary.MANEUVERS}

        # Rolling window for curriculum mastery (recent performance only)
        self._mastery_window = 200  # last 200 attempts per maneuver
        self._recent_outcomes = {
            m: deque(maxlen=self._mastery_window)
            for m in ManeuverLibrary.MANEUVERS
        }

        # Asymmetric EMA for curriculum mastery (Change 3 adapted)
        # Rises fast (alpha_up=0.02), falls slow (alpha_down=0.005).
        # This prevents brief mastery dips from immediately collapsing
        # the curriculum back to word mode. The curriculum "remembers"
        # recent high performance and resists de-escalation.
        self._ema_mastery = 0.5  # Start neutral
        self._ema_alpha_up = 0.02    # Fast rise: ~50 episodes to adapt
        self._ema_alpha_down = 0.005  # Slow fall: ~200 episodes to forget
        
        # Sequence planner — Words → Sentences → Paragraphs → Essays
        self.sequence_planner = SequencePlanner(self.rng, adaptive=adaptive_curriculum)
        
        # Will be set on reset
        self.gates = []
        self.gate_orientations = []
        self.current_heading = 0.0
        self.current_alt = 2.0
        self.current_maneuver = None
        
        # Build base env with dummy gates (will be swapped)
        dummy_gates = [np.array([0, 0, 2.0]), np.array([5, 0, 2.0])]
        self._base_env = DroneRacingEnvV2(
            gates=dummy_gates,
            gate_radius=gate_radius,
            max_steps=max_steps,
            dt=dt,
            substeps=substeps,
            domain_randomization=domain_rand,
            domain_rand_scale=domain_rand_scale,
            reward_config=self.rc,
        )
        
        # Import wrappers
        sys.path.insert(0, str(os.path.join(os.path.dirname(__file__), '..', 'rl')))
        from train_ppo import CTBRActionWrapper, ImprovedObsWrapper
        
        self._ctbr = CTBRActionWrapper(self._base_env)
        self._obs_wrapper = ImprovedObsWrapper(self._ctbr)
        
        self.observation_space = self._obs_wrapper.observation_space
        self.action_space = self._obs_wrapper.action_space
        
        # Stats
        self.episode_gates = 0
        self.total_episodes = 0
    
    def _get_per_maneuver_masteries(self):
        """Get per-maneuver mastery rates from rolling window."""
        rates = {}
        for m in ManeuverLibrary.MANEUVERS:
            window = self._recent_outcomes[m]
            if len(window) > 10:
                rates[m] = sum(window) / len(window)
            else:
                rates[m] = 0.5  # Not enough data — neutral
        return rates

    def _get_avg_mastery(self):
        """Compute curriculum mastery using asymmetric EMA.

        The raw rolling-window average is computed, then the EMA is updated
        asymmetrically: it tracks upward quickly but resists downward movement.
        This prevents brief performance dips from collapsing the curriculum.
        """
        rates = self._get_per_maneuver_masteries()
        raw_avg = np.mean(list(rates.values()))

        # Update EMA asymmetrically
        if raw_avg > self._ema_mastery:
            alpha = self._ema_alpha_up
        else:
            alpha = self._ema_alpha_down
        self._ema_mastery = (1 - alpha) * self._ema_mastery + alpha * raw_avg

        return self._ema_mastery

    def _choose_maneuver(self):
        """Choose next maneuver via SequencePlanner.

        V2: Passes per-maneuver masteries so the planner can filter
        unready maneuvers out of sequences.
        """
        if not self.adaptive_curriculum:
            return None

        # Warmup: need enough data for reliable mastery estimates.
        # Use mastery-based gate (not episode count) so resumed models
        # activate the planner immediately when mastery data is available.
        if self.total_episodes < 10:
            return None  # Minimum data collection
        avg_mastery = self._get_avg_mastery()
        if avg_mastery == 0.5 and self.total_episodes < 50:
            return None  # Still at neutral default — not enough data yet

        maneuver_masteries = self._get_per_maneuver_masteries()
        maneuver = self.sequence_planner.next_maneuver(
            avg_mastery=avg_mastery,
            maneuver_masteries=maneuver_masteries,
        )

        if maneuver is not None:
            return maneuver

        # Planner returned None (word mode) — use weighted random biased toward weak skills
        weights = np.array([max(0.05, 1.0 - maneuver_masteries[m])
                            for m in ManeuverLibrary.MANEUVERS])
        weights = weights / weights.sum()

        return self.rng.choice(ManeuverLibrary.MANEUVERS, p=weights)
    
    def _spawn_gate(self, prev_pos):
        """Spawn the next gate using a maneuver formula."""
        maneuver = self._choose_maneuver()
        new_pos, new_heading, new_alt, maneuver_name = self.library.generate(
            prev_pos, self.current_heading, self.current_alt, self.rng, maneuver
        )
        self.current_heading = new_heading
        self.current_alt = new_alt
        self.current_maneuver = maneuver_name
        self.maneuver_attempts[maneuver_name] += 1
        return new_pos, maneuver_name
    
    def _setup_gates(self):
        """Initialize first 2 gates."""
        self.current_heading = self.rng.uniform(0, 2 * np.pi)
        self.current_alt = self.rng.uniform(1.5, 4.0)
        
        # First gate at origin-ish
        g0 = np.array([0.0, 0.0, self.current_alt])
        g1_pos, m1 = self._spawn_gate(g0)
        
        self.gates = [g0, g1_pos]
        self.pending_maneuvers = [None, m1]  # Track which maneuver each gate tests
        
        # Compute orientations
        dir0 = g1_pos - g0
        norm0 = np.linalg.norm(dir0)
        if norm0 > 1e-6:
            dir0 = dir0 / norm0
        else:
            dir0 = np.array([1.0, 0.0, 0.0])
        
        self.gate_orientations = [dir0, dir0]  # Will update gate 1 orient when gate 2 spawns
        
        # Initial position: behind first gate
        init_pos = g0 - 3.0 * dir0
        init_pos[2] = max(init_pos[2], 0.5)

        # TAKEOFF curriculum (2026-06-01): with ground_start_prob, start at ground rest
        # (z=0.2, just clear of the z<0 crash floor) so the policy must take off and climb
        # to the elevated gate 0. The 67.5M policy never learned takeoff (trained mid-air,
        # idled thrust->0 on the VQ1 pad). g0 stays at current_alt (1.5-4.0m) so the
        # ground start forces a real climb. Base env already resets vel=0, level attitude.
        self.ground_start = self.rng.random() < self.ground_start_prob
        if self.ground_start:
            # VQ1 fix (2026-06-01, Day 121): VQ1 places gate 0 ~23 m from the pad, but the
            # default init (g0 - 3*dir0) trained gate 0 at ~3-5 m. Live diagnosis showed the
            # gate-distance obs hit ~6 sigma at the 23 m start (training max was 2.9 sigma) ->
            # the policy saturated the sticks. So ground-start spawns FAR (15-28 m) at ground
            # rest, training the distant-first-gate-from-standstill case VQ1 actually presents.
            gs_dist = self.rng.uniform(15.0, 28.0)
            init_pos = g0 - gs_dist * dir0
            init_pos[2] = 0.2

        return init_pos
    
    def reset(self, **kwargs):
        """Reset with fresh procedural gates."""
        # Record failures for unresolved gates in rolling window
        if self.total_episodes > 0:
            current_gate_idx = self._base_env.current_gate
            for idx in range(current_gate_idx, len(getattr(self, 'pending_maneuvers', []))):
                m = self.pending_maneuvers[idx]
                if m is not None:
                    self._recent_outcomes[m].append(False)

        # Notify planner that the episode ended (tracks sequence interruptions)
        if self.total_episodes > 0:
            self.sequence_planner.on_episode_end(completed_all_gates=False)
        
        self.total_episodes += 1
        self.episode_gates = 0
        
        init_pos = self._setup_gates()
        
        # Set up base env
        self._base_env.gates = [g.copy() for g in self.gates]
        self._base_env.n_gates = len(self.gates)
        self._base_env.gate_orientations = list(self.gate_orientations)
        self._base_env.initial_position = init_pos.copy()
        
        obs, info = self._obs_wrapper.reset(**kwargs)
        return obs, info
    
    def step(self, action):
        prev_gate = self._base_env.current_gate
        obs, reward, terminated, truncated, info = self._obs_wrapper.step(action)
        
        new_gate = self._base_env.current_gate
        
        # Gate was passed!
        if new_gate > prev_gate:
            self.episode_gates += 1
            
            # Record maneuver success
            passed_idx = new_gate - 1  # The gate we just passed
            if passed_idx < len(self.pending_maneuvers) and self.pending_maneuvers[passed_idx]:
                m = self.pending_maneuvers[passed_idx]
                self.maneuver_successes[m] += 1
                self._recent_outcomes[m].append(True)
            
            # Spawn next gate
            last_gate_pos = self.gates[-1]
            new_gate_pos, maneuver_name = self._spawn_gate(last_gate_pos)
            
            # Add to gate list
            self.gates.append(new_gate_pos)
            self.pending_maneuvers.append(maneuver_name)
            
            # Compute orientation
            direction = new_gate_pos - last_gate_pos
            norm = np.linalg.norm(direction)
            if norm > 1e-6:
                direction = direction / norm
            else:
                direction = np.array([1.0, 0.0, 0.0])
            self.gate_orientations.append(direction)
            
            # Update base env's gate list
            self._base_env.gates = [g.copy() for g in self.gates]
            self._base_env.n_gates = len(self.gates)
            self._base_env.gate_orientations = list(self.gate_orientations)
            
            # Override termination from "course complete" — there's always another gate
            if terminated and info.get('course_complete'):
                terminated = False
                # Update prev_dist for reward computation
                self._base_env.prev_dist_to_gate = np.linalg.norm(
                    self._base_env.state[0:3] - self.gates[new_gate]
                )
        
        info['gates_passed'] = self.episode_gates
        info['current_maneuver'] = self.current_maneuver
        
        return obs, reward, terminated, truncated, info
    
    def get_maneuver_stats(self):
        """Get per-maneuver success rates."""
        stats = {}
        for m in ManeuverLibrary.MANEUVERS:
            a = self.maneuver_attempts[m]
            s = self.maneuver_successes[m]
            stats[m] = {
                'attempts': a,
                'successes': s,
                'rate': s / max(a, 1),
            }
        return stats
    
    def get_curriculum_stats(self):
        """Get sequence planner stats (complexity distribution, completions, etc)."""
        avg_m = self._get_avg_mastery()
        rates = self._get_per_maneuver_masteries()
        raw_avg = np.mean(list(rates.values()))
        return {
            'avg_mastery': avg_m,
            'raw_avg_mastery': raw_avg,
            'ema_mastery': self._ema_mastery,
            'per_maneuver': rates,
            'planner': self.sequence_planner.get_stats(avg_mastery=avg_m),
        }
    
    def render(self):
        pass
    
    def close(self):
        if self._base_env:
            self._base_env.close()


# ============================================================
# Test
# ============================================================

if __name__ == '__main__':
    print("Testing Infinite Gate Environment...")
    
    env = InfiniteGateEnv(
        gate_radius=0.75,
        max_steps=30000,
        dt=0.002,
        substeps=1,
        domain_rand=True,
        adaptive_curriculum=True,
    )
    
    obs, info = env.reset()
    print(f"Obs shape: {obs.shape}")
    print(f"Initial gates: {len(env.gates)}")
    
    total_reward = 0
    for step in range(1000):
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        
        if terminated or truncated:
            print(f"  Episode ended at step {step}: gates={info['gates_passed']}, "
                  f"reward={total_reward:.1f}, terminated={terminated}")
            break
    
    print(f"\nManeuver stats:")
    for m, s in env.get_maneuver_stats().items():
        if s['attempts'] > 0:
            print(f"  {m:15s}: {s['successes']}/{s['attempts']} ({s['rate']:.0%})")
    
    print("\nTest passed!")
