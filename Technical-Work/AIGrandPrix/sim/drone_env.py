"""
Simple 3D Drone Racing Environment — No external physics engine needed.
Uses basic quadrotor dynamics for learning RL fundamentals.

This is our training wheels environment. Once DCL releases their platform,
we'll adapt to their API. But the RL concepts transfer directly.

Based on simplified quadrotor dynamics from the Swift paper approach.
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Optional


class DroneRacingEnv(gym.Env):
    """
    A simplified 3D drone racing environment.
    
    State: [x, y, z, vx, vy, vz, roll, pitch, yaw, roll_rate, pitch_rate, yaw_rate]
    Action: [throttle, roll_cmd, pitch_cmd, yaw_cmd] each in [-1, 1]
    
    The drone must fly through gates in sequence as fast as possible.
    """
    
    metadata = {"render_modes": ["human", "none"], "render_fps": 50}
    
    def __init__(
        self,
        gates: Optional[list] = None,
        max_steps: int = 1000,
        dt: float = 0.02,  # 50 Hz control
        render_mode: str = "none",
    ):
        super().__init__()
        
        # Physics parameters (simplified quadrotor)
        self.mass = 0.5          # kg
        self.gravity = 9.81      # m/s^2
        self.max_thrust = 15.0   # N (about 3x weight — allows aggressive maneuvers)
        self.max_torque = 5.0    # Nm
        self.drag_coeff = 0.1    # Linear drag
        self.dt = dt
        self.max_steps = max_steps
        self.render_mode = render_mode
        
        # Gate positions: list of (x, y, z) centers
        # Default: simple straight-line course
        if gates is None:
            self.gates = [
                np.array([5.0, 0.0, 2.0]),
                np.array([10.0, 3.0, 2.5]),
                np.array([15.0, 0.0, 3.0]),
                np.array([20.0, -3.0, 2.0]),
                np.array([25.0, 0.0, 2.5]),
            ]
        else:
            self.gates = [np.array(g) for g in gates]
        
        self.gate_radius = 1.5  # meters — must pass within this distance of gate center
        
        # Observation space: drone state (12) + relative position to next gate (3) + gate index (1)
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(16,), dtype=np.float32
        )
        
        # Action space: [throttle, roll, pitch, yaw] normalized to [-1, 1]
        self.action_space = spaces.Box(
            low=-1.0, high=1.0, shape=(4,), dtype=np.float32
        )
        
        self.reset()
    
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        # State: [x, y, z, vx, vy, vz, roll, pitch, yaw, p, q, r]
        self.state = np.zeros(12, dtype=np.float32)
        self.state[2] = 2.0  # Start at 2m altitude
        
        self.current_gate = 0
        self.steps = 0
        self.total_reward = 0.0
        self.prev_dist_to_gate = np.linalg.norm(
            self.gates[0] - self.state[:3]
        )
        
        return self._get_obs(), {}
    
    def _get_obs(self):
        """Observation: drone state + relative gate position + gate index."""
        if self.current_gate < len(self.gates):
            rel_gate = self.gates[self.current_gate] - self.state[:3]
        else:
            rel_gate = np.zeros(3)
        
        gate_idx = np.array([self.current_gate / len(self.gates)], dtype=np.float32)
        
        return np.concatenate([
            self.state,       # 12: full drone state
            rel_gate,         # 3: relative position to next gate
            gate_idx,         # 1: normalized gate index
        ]).astype(np.float32)
    
    def step(self, action):
        action = np.clip(action, -1.0, 1.0)
        
        # Unpack state
        x, y, z = self.state[0:3]
        vx, vy, vz = self.state[3:6]
        roll, pitch, yaw = self.state[6:9]
        p, q, r = self.state[9:12]
        
        # Convert actions to forces/torques
        # Throttle: 0 to max_thrust (shifted from [-1,1] to [0,1] range)
        thrust = self.max_thrust * (action[0] + 1.0) / 2.0
        
        # Torques for roll, pitch, yaw
        roll_torque = self.max_torque * action[1]
        pitch_torque = self.max_torque * action[2]
        yaw_torque = self.max_torque * action[3]
        
        # Simplified rotation: thrust direction based on roll/pitch
        # In reality this involves full rotation matrices, but for learning
        # the RL concepts this simplified model works
        ax = thrust / self.mass * np.sin(pitch) * np.cos(roll)
        ay = thrust / self.mass * (-np.sin(roll))
        az = thrust / self.mass * np.cos(pitch) * np.cos(roll) - self.gravity
        
        # Add drag
        ax -= self.drag_coeff * vx
        ay -= self.drag_coeff * vy
        az -= self.drag_coeff * vz
        
        # Angular dynamics (simplified — no coupling terms)
        pdot = roll_torque
        qdot = pitch_torque
        rdot = yaw_torque
        
        # Integrate (Euler method)
        vx_new = vx + ax * self.dt
        vy_new = vy + ay * self.dt
        vz_new = vz + az * self.dt
        
        x_new = x + vx_new * self.dt
        y_new = y + vy_new * self.dt
        z_new = z + vz_new * self.dt
        
        p_new = p + pdot * self.dt
        q_new = q + qdot * self.dt
        r_new = r + rdot * self.dt
        
        roll_new = roll + p_new * self.dt
        pitch_new = pitch + q_new * self.dt
        yaw_new = yaw + r_new * self.dt
        
        # Clamp angles to prevent numerical issues
        roll_new = np.clip(roll_new, -np.pi/2, np.pi/2)
        pitch_new = np.clip(pitch_new, -np.pi/2, np.pi/2)
        
        # Update state
        self.state = np.array([
            x_new, y_new, z_new,
            vx_new, vy_new, vz_new,
            roll_new, pitch_new, yaw_new,
            p_new, q_new, r_new,
        ], dtype=np.float32)
        
        self.steps += 1
        
        # === REWARD COMPUTATION ===
        reward = 0.0
        terminated = False
        truncated = False
        info = {}
        
        # Check gate passage
        if self.current_gate < len(self.gates):
            gate_pos = self.gates[self.current_gate]
            dist_to_gate = np.linalg.norm(self.state[:3] - gate_pos)
            
            # Progress reward: getting closer to the next gate
            progress = self.prev_dist_to_gate - dist_to_gate
            reward += progress * 1.0  # Scale factor
            self.prev_dist_to_gate = dist_to_gate
            
            # Gate passage: within radius counts as passed
            if dist_to_gate < self.gate_radius:
                reward += 10.0  # Big bonus for passing gate
                self.current_gate += 1
                info["gate_passed"] = self.current_gate
                
                if self.current_gate < len(self.gates):
                    self.prev_dist_to_gate = np.linalg.norm(
                        self.gates[self.current_gate] - self.state[:3]
                    )
                else:
                    # All gates passed — course complete!
                    reward += 50.0
                    terminated = True
                    info["course_complete"] = True
                    info["completion_steps"] = self.steps
        
        # Penalties
        # Crash: ground collision
        if z_new < 0.0:
            reward -= 20.0
            terminated = True
            info["crash"] = "ground"
        
        # Crash: too high
        if z_new > 20.0:
            reward -= 10.0
            terminated = True
            info["crash"] = "ceiling"
        
        # Out of bounds
        if abs(x_new) > 50 or abs(y_new) > 50:
            reward -= 10.0
            terminated = True
            info["crash"] = "out_of_bounds"
        
        # Small penalty for extreme angles (encourages stable flight)
        angle_penalty = 0.01 * (abs(roll_new) + abs(pitch_new))
        reward -= angle_penalty
        
        # Time penalty (encourages speed)
        reward -= 0.01
        
        # Max steps
        if self.steps >= self.max_steps:
            truncated = True
        
        self.total_reward += reward
        
        return self._get_obs(), reward, terminated, truncated, info
    
    def get_stats(self):
        """Get current episode stats."""
        return {
            "gates_passed": self.current_gate,
            "total_gates": len(self.gates),
            "steps": self.steps,
            "total_reward": self.total_reward,
            "position": self.state[:3].tolist(),
            "velocity": np.linalg.norm(self.state[3:6]),
        }


# === Quick test ===
if __name__ == "__main__":
    env = DroneRacingEnv()
    obs, info = env.reset()
    
    print("=" * 60)
    print("Drone Racing Environment — Quick Test")
    print("=" * 60)
    print(f"Observation space: {env.observation_space.shape}")
    print(f"Action space: {env.action_space.shape}")
    print(f"Gates: {len(env.gates)}")
    print(f"Starting position: {env.state[:3]}")
    print(f"First gate: {env.gates[0]}")
    print()
    
    # Random flight for 200 steps
    total_reward = 0
    for i in range(200):
        action = env.action_space.sample()  # Random actions
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        
        if terminated or truncated:
            print(f"Episode ended at step {i+1}")
            print(f"  Reason: {'terminated' if terminated else 'truncated'}")
            print(f"  Info: {info}")
            break
    
    stats = env.get_stats()
    print(f"\nFinal stats:")
    print(f"  Gates passed: {stats['gates_passed']}/{stats['total_gates']}")
    print(f"  Steps: {stats['steps']}")
    print(f"  Total reward: {stats['total_reward']:.2f}")
    print(f"  Final position: [{stats['position'][0]:.1f}, {stats['position'][1]:.1f}, {stats['position'][2]:.1f}]")
    print(f"  Final speed: {stats['velocity']:.1f} m/s")
    print()
    print("Environment works! Ready for RL training.")
