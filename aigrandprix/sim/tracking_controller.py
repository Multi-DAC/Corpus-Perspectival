"""
Tracking Controller for Quadrotor Racing

A feedback controller that tracks the optimal trajectory.
Uses geometric control on SE(3) — the standard approach for 
aggressive quadrotor flight.

This serves as:
1. Verification that the trajectory IS flyable with feedback
2. Expert oracle for DAgger (given any state, compute correct action)
3. Baseline to beat with RL

Based on "Geometric Tracking Control of a Quadrotor UAV on SE(3)"
by Lee, Leok, McClamroch (2010).
"""

import numpy as np
from scipy.spatial import KDTree
from drone_env_v2 import QuadParams, quat_rotate_np, quat_normalize


def quat_to_rotation_matrix(q):
    """Convert quaternion [w,x,y,z] to 3x3 rotation matrix."""
    w, x, y, z = q
    return np.array([
        [1 - 2*(y*y + z*z), 2*(x*y - w*z),     2*(x*z + w*y)],
        [2*(x*y + w*z),     1 - 2*(x*x + z*z), 2*(y*z - w*x)],
        [2*(x*z - w*y),     2*(y*z + w*x),     1 - 2*(x*x + y*y)],
    ])


def rotation_matrix_to_quat(R):
    """Convert 3x3 rotation matrix to quaternion [w,x,y,z]."""
    tr = R[0,0] + R[1,1] + R[2,2]
    if tr > 0:
        s = 0.5 / np.sqrt(tr + 1.0)
        w = 0.25 / s
        x = (R[2,1] - R[1,2]) * s
        y = (R[0,2] - R[2,0]) * s
        z = (R[1,0] - R[0,1]) * s
    elif R[0,0] > R[1,1] and R[0,0] > R[2,2]:
        s = 2.0 * np.sqrt(1.0 + R[0,0] - R[1,1] - R[2,2])
        w = (R[2,1] - R[1,2]) / s
        x = 0.25 * s
        y = (R[0,1] + R[1,0]) / s
        z = (R[0,2] + R[2,0]) / s
    elif R[1,1] > R[2,2]:
        s = 2.0 * np.sqrt(1.0 + R[1,1] - R[0,0] - R[2,2])
        w = (R[0,2] - R[2,0]) / s
        x = (R[0,1] + R[1,0]) / s
        y = 0.25 * s
        z = (R[1,2] + R[2,1]) / s
    else:
        s = 2.0 * np.sqrt(1.0 + R[2,2] - R[0,0] - R[1,1])
        w = (R[1,0] - R[0,1]) / s
        x = (R[0,2] + R[2,0]) / s
        y = (R[1,2] + R[2,1]) / s
        z = 0.25 * s
    return quat_normalize(np.array([w, x, y, z]))


def vee_map(M):
    """Vee map: extract vector from skew-symmetric matrix."""
    return np.array([M[2,1], M[0,2], M[1,0]])


class TrajectoryTracker:
    """
    SE(3) geometric tracking controller for quadrotor racing.
    
    Given a reference trajectory (position, velocity, acceleration, attitude, bodyrate),
    computes motor thrusts to track it.
    """
    
    def __init__(self, params: QuadParams = None):
        self.params = params or QuadParams()
        
        # Position gains — tuned for 0.85kg quad
        # Higher natural freq = tighter tracking but risk of oscillation
        wn_pos = 5.0   # Up from 3.0
        zeta_pos = 0.85
        self.Kp = np.diag([wn_pos**2, wn_pos**2, wn_pos**2 * 1.5])
        self.Kd = np.diag([2*zeta_pos*wn_pos, 2*zeta_pos*wn_pos, 2*zeta_pos*wn_pos*1.2])
        
        # Attitude gains — tuned relative to inertia (I_xx=0.001, I_zz=0.0017)
        wn_att = 30.0   # Up from 20.0 — faster attitude response
        zeta_att = 0.9   # Slightly underdamped for speed
        I_xy = self.params.inertia[0, 0]  # 0.001
        I_z = self.params.inertia[2, 2]   # 0.0017
        self.Kr = np.diag([I_xy * wn_att**2, I_xy * wn_att**2, I_z * wn_att**2 * 0.1])
        self.Kw = np.diag([I_xy * 2*zeta_att*wn_att, I_xy * 2*zeta_att*wn_att, I_z * 2*zeta_att*wn_att * 0.1])
        
        # Feedforward acceleration (estimated from trajectory)
        self.use_ff = True
    
    def reset_integral(self):
        """Reset integral error accumulator."""
        self.pos_integral = np.zeros(3)
    
    def compute_thrust(self, state, ref_pos, ref_vel, ref_acc=None, ref_quat=None, ref_omega=None):
        """
        Compute 4 motor thrusts given current state and reference.
        
        state: [pos(3), vel(3), quat(4), bodyrate(3)] = 13
        ref_pos: desired position (3)
        ref_vel: desired velocity (3)
        ref_acc: desired acceleration (3), optional
        ref_quat: desired attitude [w,x,y,z] (4), optional
        ref_omega: desired body rates (3), optional
        
        Returns: motor thrusts (4)
        """
        m = self.params.mass
        g = self.params.g
        l = self.params.arm_length
        ctau = self.params.ctau
        
        pos = state[0:3]
        vel = state[3:6]
        q = state[6:10]
        omega = state[10:13]
        
        R = quat_to_rotation_matrix(q)
        e3 = np.array([0.0, 0.0, 1.0])
        
        # --- Position Control (PID) ---
        ep = pos - ref_pos
        ev = vel - ref_vel
        
        # Integral term (with anti-windup)
        if not hasattr(self, 'pos_integral'):
            self.pos_integral = np.zeros(3)
        self.pos_integral += ep * 0.02  # dt
        self.pos_integral = np.clip(self.pos_integral, -2.0, 2.0)  # Anti-windup
        
        # Desired force in world frame
        if ref_acc is not None:
            F_ff = m * ref_acc
        else:
            F_ff = np.zeros(3)
        
        Ki = np.diag([1.5, 1.5, 3.0])  # Integral gains
        F_des = -self.Kp @ ep - self.Kd @ ev - Ki @ self.pos_integral + m * g * e3 + F_ff
        
        # Altitude safety: extra upward force when close to ground
        if pos[2] < 0.8 and vel[2] < 0:
            altitude_boost = 20.0 * max(0, 0.8 - pos[2])
            F_des[2] += altitude_boost
        
        # Total thrust = F_des projected onto body z-axis
        total_thrust = np.dot(F_des, R @ e3)
        total_thrust = np.clip(total_thrust, 0.0, 4 * self.params.T_max)
        
        # --- Attitude Control ---
        # Desired rotation: z-axis aligned with F_des
        if np.linalg.norm(F_des) > 1e-6:
            z_des = F_des / np.linalg.norm(F_des)
        else:
            z_des = e3
        
        # Use reference yaw if available, otherwise maintain current
        if ref_quat is not None:
            R_ref = quat_to_rotation_matrix(ref_quat)
            x_c = R_ref[:, 0]  # Use reference x-axis for yaw
        else:
            # Project current x-axis onto plane perpendicular to z_des
            x_c = R[:, 0]
        
        # Construct desired rotation matrix
        y_des = np.cross(z_des, x_c)
        y_norm = np.linalg.norm(y_des)
        if y_norm > 1e-6:
            y_des = y_des / y_norm
        else:
            y_des = R[:, 1]  # Fallback
        x_des = np.cross(y_des, z_des)
        
        R_des = np.column_stack([x_des, y_des, z_des])
        
        # Rotation error (geometric)
        eR_mat = 0.5 * (R_des.T @ R - R.T @ R_des)
        eR = vee_map(eR_mat)
        
        # Body rate error
        if ref_omega is not None:
            ew = omega - ref_omega
        else:
            ew = omega
        
        # Desired torque
        I = self.params.inertia
        tau_des = -self.Kr @ eR - self.Kw @ ew + np.cross(omega, I @ omega)
        
        # --- Motor Mixing ---
        # Convert total thrust + torques to individual motor thrusts
        # [F_total]     [1    1    1    1  ] [T1]
        # [tau_x  ]  =  [l   -l   -l    l ] [T2]
        # [tau_y  ]     [-l  -l    l    l ] [T3]
        # [tau_z  ]     [c   -c    c   -c ] [T4]
        
        A = np.array([
            [1,  1,  1,  1],
            [l, -l, -l,  l],
            [-l, -l,  l,  l],
            [ctau, -ctau, ctau, -ctau],
        ])
        
        wrench = np.array([total_thrust, tau_des[0], tau_des[1], tau_des[2]])
        
        try:
            thrusts = np.linalg.solve(A, wrench)
        except np.linalg.LinAlgError:
            thrusts = np.full(4, total_thrust / 4)
        
        # Clamp to physical limits
        thrusts = np.clip(thrusts, self.params.T_min, self.params.T_max)
        
        return thrusts


class TrajectoryOracle:
    """
    Expert oracle that tracks the optimal trajectory.
    
    Given any drone state, looks up the nearest reference point
    and computes the tracking controller output.
    """
    
    def __init__(self, expert_states, expert_times, params: QuadParams = None):
        self.states = expert_states
        self.times = expert_times
        self.params = params or QuadParams()
        
        self.controller = TrajectoryTracker(self.params)
        
        # Build KD-tree on position + velocity for fast lookup
        self.pos_vel = expert_states[:, 0:6]
        self.kdtree = KDTree(self.pos_vel)
        
        # Pre-compute accelerations from trajectory (finite differences)
        self.accelerations = np.zeros((len(expert_states), 3))
        for i in range(1, len(expert_states) - 1):
            dt = expert_times[i+1] - expert_times[i-1]
            if dt > 0:
                self.accelerations[i] = (expert_states[i+1, 3:6] - expert_states[i-1, 3:6]) / dt
        self.accelerations[0] = self.accelerations[1]
        self.accelerations[-1] = self.accelerations[-2]
    
    def get_reference(self, t_or_state, use_time=False):
        """
        Get reference state from trajectory.
        
        If use_time: look up by time index
        Otherwise: nearest-neighbor by position+velocity
        """
        if use_time:
            idx = np.searchsorted(self.times, t_or_state)
            idx = min(idx, len(self.states) - 1)
        else:
            # Nearest neighbor in pos+vel space
            query = t_or_state[0:6]
            _, idx = self.kdtree.query(query)
        
        # Direct time lookup — no lookahead (reduces tracking lag)
        ref_pos = self.states[idx, 0:3]
        ref_vel = self.states[idx, 3:6]
        ref_acc = self.accelerations[idx]
        ref_quat = self.states[idx, 6:10]
        ref_omega = self.states[idx, 10:13]
        
        return ref_pos, ref_vel, ref_acc, ref_quat, ref_omega, idx
    
    def compute_action(self, state, t=None):
        """
        Compute motor thrusts for any given state.
        
        This is the expert oracle — used for DAgger training.
        Always uses time-based reference when t is provided (more stable).
        Falls back to nearest-neighbor only when time is unknown.
        """
        if t is not None:
            ref_pos, ref_vel, ref_acc, ref_quat, ref_omega, idx = \
                self.get_reference(t, use_time=True)
        else:
            # For DAgger: use nearest-neighbor but with position-only matching
            ref_pos, ref_vel, ref_acc, ref_quat, ref_omega, idx = \
                self.get_reference(state, use_time=False)
        
        thrusts = self.controller.compute_thrust(
            state, ref_pos, ref_vel, ref_acc, ref_quat, ref_omega
        )
        
        return thrusts, idx
    
    def compute_action_normalized(self, state, t=None):
        """Compute normalized [-1,1] action for the env."""
        thrusts, idx = self.compute_action(state, t)
        T_min = self.params.T_min
        T_max = self.params.T_max
        normalized = 2.0 * (thrusts - T_min) / (T_max - T_min + 1e-8) - 1.0
        return np.clip(normalized, -1.0, 1.0), idx


def test_tracking():
    """Test the tracking controller on the environment."""
    import os
    from drone_env_v2 import DroneRacingEnvV2
    
    expert_dir = os.path.join(os.path.dirname(__file__), '..', 'expert_trajectory')
    states = np.load(os.path.join(expert_dir, 'states.npy'))
    times = np.load(os.path.join(expert_dir, 'times.npy'))
    
    print("=" * 60)
    print("Tracking Controller Test")
    print("=" * 60)
    
    oracle = TrajectoryOracle(states, times)
    
    # Run in environment with tracking controller
    env = DroneRacingEnvV2(dt=0.02, substeps=4)
    obs, _ = env.reset()
    
    total_reward = 0
    pos_errors = []
    t = 0
    
    for step in range(2000):
        t = step * env.dt
        
        # Get tracking controller action
        action_norm, ref_idx = oracle.compute_action_normalized(env.state, t=t)
        
        obs, reward, terminated, truncated, info = env.step(action_norm)
        total_reward += reward
        
        # Track position error relative to reference
        if ref_idx < len(states):
            ref_pos = states[ref_idx, 0:3]
            pos_err = np.linalg.norm(env.state[0:3] - ref_pos)
            pos_errors.append(pos_err)
        
        if step % 200 == 0:
            speed = np.linalg.norm(env.state[3:6])
            gate = env.current_gate
            pe = pos_errors[-1] if pos_errors else 0
            print(f"  t={t:5.1f}s step={step:4d}: "
                  f"gates={gate}/19 speed={speed:5.1f}m/s "
                  f"pos_err={pe:.3f}m ref_idx={ref_idx}")
        
        if terminated or truncated:
            crash = info.get('crash', 'none')
            print(f"  ENDED at t={t:.1f}s: {crash}")
            break
    
    stats = env.get_stats()
    pos_errors = np.array(pos_errors) if pos_errors else np.array([0])
    
    print(f"\nResults:")
    print(f"  Gates passed: {stats['gates_passed']}/19")
    print(f"  Time: {stats['time']:.1f}s")
    print(f"  Reward: {total_reward:.1f}")
    print(f"  Position error: mean={pos_errors.mean():.3f}m, max={pos_errors.max():.3f}m")
    
    return stats


if __name__ == "__main__":
    test_tracking()
