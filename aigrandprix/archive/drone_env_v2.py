"""
Drone Racing Environment v2 — Real Quadrotor Dynamics

Physics ported directly from rpg_time_optimal optimizer:
- Quaternion attitude representation (no gimbal lock)
- Individual motor thrust control (4 motors)
- Full 3D rigid body dynamics with inertia tensor
- Aerodynamic drag
- RK4 integration

State: [pos(3), vel(3), quat(4), bodyrate(3)] = 13 dims
Action: [T1, T2, T3, T4] normalized to [-1, 1] → mapped to [T_min, T_max]

This matches the optimizer's dynamics exactly, so expert trajectories
map directly as training data.
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Optional, List


# ============================================================
# Numpy quaternion operations (from rpg_time_optimal)
# ============================================================

def quat_mult_np(q1, q2):
    """Hamilton product q1 * q2. Convention: [w, x, y, z]."""
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2
    return np.array([
        w1*w2 - x1*x2 - y1*y2 - z1*z2,
        w1*x2 + x1*w2 + y1*z2 - z1*y2,
        w1*y2 - x1*z2 + y1*w2 + z1*x2,
        w1*z2 + x1*y2 - y1*x2 + z1*w2,
    ])


def quat_rotate_np(q, v):
    """Rotate vector v by quaternion q. v is 3D, q is [w,x,y,z]."""
    qv = np.array([0.0, v[0], v[1], v[2]])
    q_conj = np.array([q[0], -q[1], -q[2], -q[3]])
    rotated = quat_mult_np(quat_mult_np(q, qv), q_conj)
    return rotated[1:4]


def quat_normalize(q):
    """Normalize quaternion to unit length."""
    n = np.linalg.norm(q)
    if n < 1e-10:
        return np.array([1.0, 0.0, 0.0, 0.0])
    return q / n


# ============================================================
# Quadrotor parameters (from quad.yaml)
# ============================================================

class QuadParams:
    """Physical parameters matching the optimizer's quad.yaml."""
    def __init__(self):
        self.mass = 0.85            # kg
        self.arm_length = 0.15      # m (center to motor, diagonal)
        self.inertia = np.array([   # Inertia tensor
            [0.001, 0.0, 0.0],
            [0.0, 0.001, 0.0],
            [0.0, 0.0, 0.0017],
        ])
        self.inertia_inv = np.linalg.inv(self.inertia)
        self.g = 9.801              # gravity
        self.T_min = 0.0            # min thrust per motor [N]
        self.T_max = 0.85 * 9.81 * 3.3 / 4  # TWR_max=3.3 → per motor
        self.omega_max_xy = 15.0    # max body rate xy [rad/s]
        self.omega_max_z = 0.3      # max body rate z [rad/s] — yaw limited
        self.ctau = 0.05            # thrust-to-torque coefficient
        self.cd = 0.3               # linear drag coefficient (realistic for racing quad)
    
    def randomize(self, rng: np.random.Generator, scale: float = 0.1):
        """Domain randomization. Returns a copy with perturbed params."""
        p = QuadParams()
        p.mass = self.mass * rng.uniform(1 - scale, 1 + scale)
        p.arm_length = self.arm_length * rng.uniform(1 - scale, 1 + scale)
        # Perturb diagonal inertia
        i_scale = rng.uniform(1 - scale, 1 + scale, size=3)
        p.inertia = self.inertia.copy()
        p.inertia[0, 0] *= i_scale[0]
        p.inertia[1, 1] *= i_scale[1]
        p.inertia[2, 2] *= i_scale[2]
        p.inertia_inv = np.linalg.inv(p.inertia)
        p.T_max = self.T_max * rng.uniform(1 - scale * 0.5, 1 + scale * 0.5)
        p.cd = self.cd + rng.uniform(0, 0.02)  # Add small random drag
        return p


# ============================================================
# Dynamics — matches optimizer exactly
# ============================================================

def quadrotor_dynamics(state, action, params: QuadParams):
    """
    Compute state derivative. Matches rpg_time_optimal/src/quad.py dynamics().
    
    State: [px, py, pz, vx, vy, vz, qw, qx, qy, qz, wx, wy, wz]
    Action: [T1, T2, T3, T4] — individual motor thrusts in Newtons
    """
    p = state[0:3]
    v = state[3:6]
    q = state[6:10]
    w = state[10:13]
    T = action  # 4 motor thrusts
    
    total_thrust = T[0] + T[1] + T[2] + T[3]
    
    # Gravity
    g_vec = np.array([0.0, 0.0, -params.g])
    
    # Position derivative = velocity
    p_dot = v
    
    # Velocity derivative = rotated thrust/mass + gravity - drag
    thrust_body = np.array([0.0, 0.0, total_thrust / params.mass])
    v_dot = quat_rotate_np(q, thrust_body) + g_vec - v * params.cd
    
    # Quaternion derivative = 0.5 * q ⊗ [0, w]
    omega_quat = np.array([0.0, w[0], w[1], w[2]])
    q_dot = 0.5 * quat_mult_np(q, omega_quat)
    
    # Body rate derivative from torque equation
    # Torque from motor layout (X-configuration):
    #   τ_x = l * (T0 - T1 - T2 + T3)
    #   τ_y = l * (-T0 - T1 + T2 + T3)  
    #   τ_z = ctau * (T0 - T1 + T2 - T3)
    l = params.arm_length
    tau = np.array([
        l * (T[0] - T[1] - T[2] + T[3]),
        l * (-T[0] - T[1] + T[2] + T[3]),
        params.ctau * (T[0] - T[1] + T[2] - T[3]),
    ])
    
    # Euler's rotation equation: I * w_dot = tau - w × (I * w)
    Iw = params.inertia @ w
    w_dot = params.inertia_inv @ (tau - np.cross(w, Iw))
    
    return np.concatenate([p_dot, v_dot, q_dot, w_dot])


def rk4_step(state, action, dt, params: QuadParams):
    """Runge-Kutta 4th order integration step."""
    k1 = quadrotor_dynamics(state, action, params)
    k2 = quadrotor_dynamics(state + dt/2 * k1, action, params)
    k3 = quadrotor_dynamics(state + dt/2 * k2, action, params)
    k4 = quadrotor_dynamics(state + dt * k3, action, params)
    
    new_state = state + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)
    
    # Re-normalize quaternion
    new_state[6:10] = quat_normalize(new_state[6:10])
    
    return new_state


# ============================================================
# Environment
# ============================================================

class DroneRacingEnvV2(gym.Env):
    """
    Quadrotor racing with real physics.
    
    Observation (20-dim):
        [pos(3), vel(3), quat(4), bodyrate(3)] = 13 (drone state)
        + [rel_gate_pos(3)] = 3 (relative position to next gate)
        + [rel_gate_pos_after(3)] = 3 (relative position to gate after next — lookahead)
        + [gate_progress(1)] = 1 (normalized gate index)
        Total: 20
    
    Action (4-dim):
        [T1, T2, T3, T4] normalized to [-1, 1]
        Mapped to [T_min, T_max] per motor
    """
    
    metadata = {"render_modes": ["human", "none"], "render_fps": 50}
    
    def __init__(
        self,
        gates: Optional[List[list]] = None,
        gate_radius: float = 0.3,
        max_steps: int = 2000,
        dt: float = 0.02,  # 50 Hz control (can substep internally)
        substeps: int = 4,  # 4 substeps = 200 Hz physics
        render_mode: str = "none",
        domain_randomization: bool = False,
        domain_rand_scale: float = 0.1,
        reward_config: Optional[dict] = None,
    ):
        super().__init__()
        
        self.base_params = QuadParams()
        self.params = QuadParams()
        self.dt = dt
        self.substeps = substeps
        self.physics_dt = dt / substeps
        self.max_steps = max_steps
        self.render_mode = render_mode
        self.domain_randomization = domain_randomization
        self.domain_rand_scale = domain_rand_scale
        self.gate_radius = gate_radius
        
        # Default gates from track.yaml
        if gates is None:
            self.gates = [
                np.array([-1.1, -1.6, 3.6]),
                np.array([9.2, 6.6, 1.0]),
                np.array([9.2, -4.0, 1.2]),
                np.array([-4.5, -6.0, 3.5]),
                np.array([-4.5, -6.0, 0.8]),
                np.array([4.75, -0.9, 1.2]),
                np.array([-2.8, 6.8, 1.2]),
            ] * 3  # 3 laps = 21 gates (track repeats 7-gate circuit ~2.7 times)
            self.gates = self.gates[:19]  # Match optimizer's 19 gates
        else:
            self.gates = [np.array(g, dtype=np.float64) for g in gates]
        
        self.n_gates = len(self.gates)
        
        # Compute gate orientations (unit vector pointing through each gate)
        # Direction is from previous gate to current gate (or init_pos to gate 0)
        self.gate_orientations = []
        for i in range(self.n_gates):
            if i == 0:
                if hasattr(self, 'initial_position'):
                    direction = self.gates[0] - self.initial_position
                elif i + 1 < self.n_gates:
                    direction = self.gates[1] - self.gates[0]
                else:
                    direction = np.array([1.0, 0.0, 0.0])
            else:
                direction = self.gates[i] - self.gates[i - 1]
            norm = np.linalg.norm(direction)
            if norm > 1e-6:
                direction = direction / norm
            else:
                direction = np.array([1.0, 0.0, 0.0])
            self.gate_orientations.append(direction)
        
        # Reward config
        self.rc = {
            'gate_bonus': 20.0,
            'course_complete_bonus': 100.0,
            'progress_scale': 2.0,
            'time_penalty': 0.05,
            'crash_penalty': 50.0,
            'attitude_penalty_scale': 0.0,  # Off by default (aggressive flight is OK)
            'bodyrate_penalty_scale': 0.0,
            'speed_bonus_scale': 0.1,       # Small reward for going fast
        }
        if reward_config:
            self.rc.update(reward_config)
        
        # Observation: 13 (state) + 3 (rel gate) + 3 (lookahead gate) + 1 (progress) = 20
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(20,), dtype=np.float32
        )
        
        # Action: 4 motor thrusts, normalized [-1, 1]
        self.action_space = spaces.Box(
            low=-1.0, high=1.0, shape=(4,), dtype=np.float32
        )
        
        # Track initial state from track.yaml
        self.initial_position = np.array([-5.0, 4.5, 1.2])
        self.initial_attitude = np.array([1.0, 0.0, 0.0, 0.0])  # Identity quaternion
        
        self.reset()
    
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        # Domain randomization
        if self.domain_randomization:
            self.params = self.base_params.randomize(
                self.np_random, self.domain_rand_scale
            )
        else:
            self.params = QuadParams()
        
        # Initial state: [pos(3), vel(3), quat(4), bodyrate(3)]
        self.state = np.zeros(13, dtype=np.float64)
        self.state[0:3] = self.initial_position.copy()
        self.state[6:10] = self.initial_attitude.copy()
        
        # Small random perturbation on reset (helps exploration)
        if self.domain_randomization:
            self.state[0:3] += self.np_random.normal(0, 0.1, size=3)
            self.state[3:6] += self.np_random.normal(0, 0.1, size=3)
        
        self.current_gate = 0
        self.steps = 0
        self.total_reward = 0.0
        self.prev_dist_to_gate = self._dist_to_gate(self.current_gate)
        self.gates_passed_times = []
        
        return self._get_obs(), {}
    
    def _dist_to_gate(self, gate_idx):
        if gate_idx >= self.n_gates:
            return 0.0
        return np.linalg.norm(self.state[0:3] - self.gates[gate_idx])
    
    def _get_obs(self):
        # Current gate relative position
        if self.current_gate < self.n_gates:
            rel_gate = self.gates[self.current_gate] - self.state[0:3]
        else:
            rel_gate = np.zeros(3)
        
        # Lookahead gate (next after current)
        if self.current_gate + 1 < self.n_gates:
            rel_gate_next = self.gates[self.current_gate + 1] - self.state[0:3]
        elif self.current_gate < self.n_gates:
            rel_gate_next = rel_gate  # Same as current if no next
        else:
            rel_gate_next = np.zeros(3)
        
        # Normalized progress
        progress = np.array([self.current_gate / max(self.n_gates, 1)])
        
        obs = np.concatenate([
            self.state,        # 13: full physics state
            rel_gate,          # 3: vector to next gate
            rel_gate_next,     # 3: vector to gate after next
            progress,          # 1: course progress
        ]).astype(np.float32)
        
        return obs
    
    def _map_action(self, action):
        """Map normalized [-1, 1] action to thrust [T_min, T_max]."""
        action = np.clip(action, -1.0, 1.0)
        # Linear map: -1 → T_min, +1 → T_max
        T_min = self.params.T_min
        T_max = self.params.T_max
        return T_min + (action + 1.0) * 0.5 * (T_max - T_min)
    
    def step(self, action):
        thrust = self._map_action(action)
        
        # Substep physics integration
        for _ in range(self.substeps):
            self.state = rk4_step(self.state, thrust, self.physics_dt, self.params)
        
        # Clamp body rates to physical limits
        w = self.state[10:13]
        w[0] = np.clip(w[0], -self.params.omega_max_xy, self.params.omega_max_xy)
        w[1] = np.clip(w[1], -self.params.omega_max_xy, self.params.omega_max_xy)
        w[2] = np.clip(w[2], -self.params.omega_max_z, self.params.omega_max_z)
        self.state[10:13] = w
        
        self.steps += 1
        t = self.steps * self.dt
        
        # === REWARD ===
        reward = 0.0
        terminated = False
        truncated = False
        info = {}
        
        pos = self.state[0:3]
        vel = self.state[3:6]
        speed = np.linalg.norm(vel)
        
        # Gate check
        if self.current_gate < self.n_gates:
            dist = self._dist_to_gate(self.current_gate)
            
            # Progress reward
            progress = self.prev_dist_to_gate - dist
            reward += progress * self.rc['progress_scale']
            self.prev_dist_to_gate = dist
            
            # Gate passage
            if dist < self.gate_radius:
                reward += self.rc['gate_bonus']
                self.gates_passed_times.append(t)
                self.current_gate += 1
                info['gate_passed'] = self.current_gate
                
                if self.current_gate < self.n_gates:
                    self.prev_dist_to_gate = self._dist_to_gate(self.current_gate)
                else:
                    # Course complete!
                    reward += self.rc['course_complete_bonus']
                    terminated = True
                    info['course_complete'] = True
                    info['completion_time'] = t
        
        # Speed bonus (encourage aggressive flight)
        reward += speed * self.rc['speed_bonus_scale'] * self.dt
        
        # Time penalty (scaled by dt so it's consistent across control frequencies)
        reward -= self.rc['time_penalty'] * self.dt
        
        # Crash conditions
        if pos[2] < 0.0:
            reward -= self.rc['crash_penalty']
            terminated = True
            info['crash'] = 'ground'
        
        if pos[2] > 30.0:  # Gauntlet goes to ~20m, give headroom
            reward -= self.rc['crash_penalty'] * 0.5
            terminated = True
            info['crash'] = 'ceiling'
        
        if np.any(np.abs(pos[:2]) > 80.0):  # Wide enough for gauntlet (x goes to 70)
            reward -= self.rc['crash_penalty'] * 0.5
            terminated = True
            info['crash'] = 'out_of_bounds'
        
        # NaN check (physics diverged)
        if np.any(np.isnan(self.state)):
            reward -= self.rc['crash_penalty']
            terminated = True
            info['crash'] = 'nan_divergence'
            self.state = np.zeros(13)
            self.state[6] = 1.0  # Valid quaternion
        
        if self.steps >= self.max_steps:
            truncated = True
        
        self.total_reward += reward
        
        return self._get_obs(), float(reward), terminated, truncated, info
    
    def get_stats(self):
        speed = np.linalg.norm(self.state[3:6])
        return {
            'gates_passed': self.current_gate,
            'total_gates': self.n_gates,
            'steps': self.steps,
            'time': self.steps * self.dt,
            'total_reward': self.total_reward,
            'position': self.state[0:3].tolist(),
            'velocity': speed,
            'gate_times': self.gates_passed_times,
        }
    
    def set_state(self, state):
        """Set drone state directly (useful for imitation learning reset)."""
        self.state = state.copy()


class DroneRacingExpertEnv(DroneRacingEnvV2):
    """
    Extended environment for imitation learning from expert trajectory.
    
    Loads the optimal trajectory and can:
    1. Reset to random points along the trajectory (DAgger-style)
    2. Provide expert actions for any state
    3. Compute imitation reward (deviation from expert)
    """
    
    def __init__(
        self,
        expert_states_path: str,
        expert_actions_path: str,
        expert_times_path: str,
        reset_mode: str = 'start',  # 'start', 'random', 'dagger'
        dagger_noise: float = 0.5,  # Noise scale for DAgger resets
        **kwargs,
    ):
        # Load expert data before super().__init__ calls reset
        self.expert_states = np.load(expert_states_path)
        self.expert_actions = np.load(expert_actions_path)
        self.expert_times = np.load(expert_times_path)
        self.reset_mode = reset_mode
        self.dagger_noise = dagger_noise
        self.expert_idx = 0
        
        super().__init__(**kwargs)
    
    def reset(self, seed=None, options=None):
        obs, info = super().reset(seed=seed, options=options)
        
        if not hasattr(self, 'expert_states'):
            return obs, info
        
        if self.reset_mode == 'start':
            # Always start from the beginning
            self.expert_idx = 0
            self.state = self.expert_states[0].copy()
        
        elif self.reset_mode == 'random':
            # Start from a random point along the trajectory
            self.expert_idx = self.np_random.integers(0, len(self.expert_states) - 1)
            self.state = self.expert_states[self.expert_idx].copy()
        
        elif self.reset_mode == 'dagger':
            # Start from a random point with noise (DAgger-style)
            self.expert_idx = self.np_random.integers(0, len(self.expert_states) - 1)
            self.state = self.expert_states[self.expert_idx].copy()
            # Add noise to position and velocity
            self.state[0:3] += self.np_random.normal(0, self.dagger_noise, size=3)
            self.state[3:6] += self.np_random.normal(0, self.dagger_noise * 0.5, size=3)
        
        # Figure out which gate we should be targeting
        pos = self.state[0:3]
        best_gate = 0
        for g in range(self.n_gates):
            if self.expert_idx > 0:
                # Estimate gate from time progress
                t_frac = self.expert_idx / len(self.expert_states)
                best_gate = int(t_frac * self.n_gates)
                best_gate = min(best_gate, self.n_gates - 1)
        self.current_gate = best_gate
        if self.current_gate < self.n_gates:
            self.prev_dist_to_gate = self._dist_to_gate(self.current_gate)
        
        return self._get_obs(), info
    
    def get_expert_action(self):
        """Get the expert action for the current trajectory index."""
        if self.expert_idx < len(self.expert_actions):
            return self.expert_actions[self.expert_idx]
        return self.expert_actions[-1]
    
    def get_expert_action_normalized(self):
        """Get expert action normalized to [-1, 1] for the policy."""
        raw = self.get_expert_action()
        T_min = self.params.T_min
        T_max = self.params.T_max
        # Inverse of _map_action: T = T_min + (a+1)/2 * (T_max-T_min)
        # → a = 2*(T - T_min)/(T_max - T_min) - 1
        normalized = 2.0 * (raw - T_min) / (T_max - T_min + 1e-8) - 1.0
        return np.clip(normalized, -1.0, 1.0)
    
    def step(self, action):
        obs, reward, terminated, truncated, info = super().step(action)
        
        # Advance expert index
        self.expert_idx = min(self.expert_idx + 1, len(self.expert_states) - 1)
        
        # Add imitation reward: how close are we to the expert trajectory?
        if self.expert_idx < len(self.expert_states):
            expert_pos = self.expert_states[self.expert_idx][0:3]
            pos_error = np.linalg.norm(self.state[0:3] - expert_pos)
            imitation_reward = max(0, 1.0 - pos_error)  # 1 when perfect, 0 when 1m off
            reward += imitation_reward * 2.0
            info['expert_pos_error'] = pos_error
        
        return obs, reward, terminated, truncated, info


# ============================================================
# Quick test
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Drone Racing Environment v2 — Real Quadrotor Physics")
    print("=" * 60)
    
    params = QuadParams()
    print(f"\nQuad parameters:")
    print(f"  Mass: {params.mass} kg")
    print(f"  Arm length: {params.arm_length} m")
    print(f"  Thrust range: [{params.T_min:.2f}, {params.T_max:.2f}] N per motor")
    print(f"  Max body rate XY: {params.omega_max_xy} rad/s")
    print(f"  Max body rate Z: {params.omega_max_z} rad/s")
    print(f"  Hover thrust per motor: {params.mass * params.g / 4:.2f} N")
    
    env = DroneRacingEnvV2()
    obs, info = env.reset()
    
    print(f"\nEnvironment:")
    print(f"  Observation space: {env.observation_space.shape}")
    print(f"  Action space: {env.action_space.shape}")
    print(f"  Gates: {env.n_gates}")
    print(f"  Physics dt: {env.physics_dt*1000:.1f} ms ({1/env.physics_dt:.0f} Hz)")
    print(f"  Control dt: {env.dt*1000:.1f} ms ({1/env.dt:.0f} Hz)")
    print(f"  Initial position: {env.state[0:3]}")
    
    # Test: hover in place
    print(f"\nHover test (100 steps)...")
    hover_thrust = params.mass * params.g / 4  # Exact hover
    hover_action = 2.0 * (hover_thrust - params.T_min) / (params.T_max - params.T_min) - 1.0
    hover_action_vec = np.full(4, hover_action, dtype=np.float32)
    
    for i in range(100):
        obs, reward, terminated, truncated, info = env.step(hover_action_vec)
        if terminated:
            print(f"  Terminated at step {i}: {info}")
            break
    
    stats = env.get_stats()
    print(f"  Position after hover: [{stats['position'][0]:.3f}, {stats['position'][1]:.3f}, {stats['position'][2]:.3f}]")
    print(f"  Altitude drift: {abs(stats['position'][2] - 1.2):.4f} m (should be ~0)")
    print(f"  Speed: {stats['velocity']:.4f} m/s (should be ~0)")
    
    # Test: random flight
    print(f"\nRandom flight test (500 steps)...")
    env.reset()
    for i in range(500):
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        if terminated or truncated:
            print(f"  Ended at step {i}: {info}")
            break
    
    stats = env.get_stats()
    print(f"  Gates passed: {stats['gates_passed']}/{stats['total_gates']}")
    print(f"  Steps: {stats['steps']}")
    print(f"  Reward: {stats['total_reward']:.1f}")
    
    # Test: expert environment
    import os
    expert_dir = os.path.join(os.path.dirname(__file__), '..', 'expert_trajectory')
    if os.path.exists(os.path.join(expert_dir, 'states.npy')):
        print(f"\nExpert environment test...")
        expert_env = DroneRacingExpertEnv(
            expert_states_path=os.path.join(expert_dir, 'states.npy'),
            expert_actions_path=os.path.join(expert_dir, 'actions.npy'),
            expert_times_path=os.path.join(expert_dir, 'times.npy'),
            reset_mode='start',
        )
        obs, _ = expert_env.reset()
        print(f"  Expert trajectory: {len(expert_env.expert_states)} steps")
        print(f"  Expert action (normalized): {expert_env.get_expert_action_normalized()}")
        print(f"  Starting position: {expert_env.state[0:3]}")
        
        # Replay expert trajectory
        total_error = 0
        for i in range(min(100, len(expert_env.expert_actions))):
            action = expert_env.get_expert_action_normalized()
            obs, reward, terminated, truncated, info = expert_env.step(action)
            if 'expert_pos_error' in info:
                total_error += info['expert_pos_error']
            if terminated:
                break
        
        print(f"  Avg position error over 100 expert steps: {total_error/100:.4f} m")
        print(f"  Gates passed: {expert_env.current_gate}/{expert_env.n_gates}")
    
    print(f"\n{'='*60}")
    print("Environment v2 ready. Real physics. Real racing.")
    print(f"{'='*60}")
