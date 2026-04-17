"""
Randomized Drone Racing Environment.
Each reset picks a random course layout — forces the agent to generalize.
Also randomizes physics params slightly for domain randomization.
"""
import gymnasium as gym
from gymnasium import spaces
import numpy as np
from drone_env import DroneRacingEnv


# Course library
COURSES = [
    # Easy straight
    [[5,0,2], [10,3,2.5], [15,0,3], [20,-3,2], [25,0,2.5]],
    # Zigzag
    [[5,4,2], [10,-4,3], [15,4,2], [20,-4,3], [25,0,2.5]],
    # Climb and dive
    [[5,0,3], [10,2,5], [15,0,7], [20,-2,5], [25,0,3]],
    # Tight turns
    [[4,2,2], [8,-2,3], [12,3,2], [16,-3,4], [20,0,2.5]],
    # S-curve
    [[5,3,2], [10,0,3], [15,-3,2], [20,0,3], [25,3,2.5]],
    # Descending
    [[5,0,6], [10,2,5], [15,0,4], [20,-2,3], [25,0,2]],
    # Wide loop
    [[6,5,2], [12,0,3], [18,-5,2], [24,0,3], [30,5,2.5]],
    # Short sprint
    [[3,1,2], [6,-1,2.5], [9,1,3], [12,-1,2.5], [15,0,2]],
]


class RandomCourseEnv(DroneRacingEnv):
    """Drone env that randomizes course and physics each reset."""
    
    def __init__(self, max_steps=500, domain_randomize=True):
        self.course_library = COURSES
        self.domain_randomize = domain_randomize
        # Init with first course, will be overwritten on reset
        super().__init__(gates=COURSES[0], max_steps=max_steps)
    
    def reset(self, seed=None, options=None):
        # Pick random course
        idx = np.random.randint(len(self.course_library))
        self.gates = [np.array(g, dtype=np.float32) for g in self.course_library[idx]]
        
        # Domain randomization: slightly vary physics
        if self.domain_randomize:
            self.mass = 0.5 * np.random.uniform(0.9, 1.1)
            self.drag_coeff = 0.1 * np.random.uniform(0.8, 1.2)
            self.max_thrust = 15.0 * np.random.uniform(0.95, 1.05)
        
        return super().reset(seed=seed, options=options)


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    
    env = RandomCourseEnv()
    print(f"Course library: {len(COURSES)} courses")
    
    # Show a few resets
    for i in range(5):
        obs, _ = env.reset()
        gates_str = " -> ".join(f"[{g[0]:.0f},{g[1]:.0f},{g[2]:.0f}]" for g in env.gates)
        print(f"Reset {i+1}: mass={env.mass:.3f}, drag={env.drag_coeff:.3f}, gates: {gates_str}")
    
    print("\nRandomized env ready!")
