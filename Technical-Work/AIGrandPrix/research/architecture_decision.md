# Architecture Decision — AI Grand Prix RL Pipeline

*Research synthesis: Feb 10, 2026*

## Papers Reviewed

1. **Swift** (Nature 2023, UZH/Scaramuzza) — Beat human champions with VIO + gate detection + PPO MLP
2. **E2E RL** (ICRA 2024, TU Delft) — Direct motor commands via RL, 1.39s faster than inner-loop approach
3. **MonoRace** (Jan 2026, TU Delft) — Won A2RL 2025, monocular + NN at 500Hz direct motor commands
4. **Dream to Fly** (Jan 2025, UZH/Scaramuzza) — DreamerV3 pixels-to-CTBR, first pure vision RL racing

## The Evolution of Approaches

```
Swift (2023):     [VIO + Gate CNN + KF] → state → [PPO MLP] → thrust + body rates → [Inner loop] → motors
E2E RL (2023):    [State estimate] → [RL policy] → DIRECT motor commands (no inner loop) — 1.39s faster
MonoRace (2026):  [Mono camera + IMU] → [Gate segmentation + drone model] → [NN] → DIRECT motor commands at 500Hz
Dream to Fly:     [Raw pixels] → [DreamerV3 world model] → [Actor] → thrust + body rates (CTBR)
```

**Clear trend:** Fewer layers = faster = wins. But also: state-based > pixel-based for pure speed.

## Key Decision: What Do WE Need?

**Our situation is unique:**
- Virtual qualifiers = SIMULATION ONLY (no sim-to-real gap!)
- We don't know the DCL SDK interface yet (waiting on it)
- We already HAVE time-optimal trajectories (19-gate: 30.31s, gauntlet: 34.79s)
- We have correct physics sim (drone_env_v2.py)
- We have a tracking controller (11/19 gates, 0.8m tolerance)

**The question:** What RL approach gets us to 0.3m gate tolerance fastest?

## Architecture Decision: State-Based PPO with Expert Trajectory

**Why NOT DreamerV3/pixels:**
- We're in simulation — we have perfect state (no perception problem)
- DreamerV3 is slower to train (world model overhead)
- Pixel-based adds complexity we don't need yet
- Dream to Fly works but isn't fastest

**Why NOT end-to-end direct motor commands:**
- Our physics sim uses collective thrust + body rates (CTBR)
- Direct motor commands add a harder optimization problem
- CTBR is what Swift uses, proven competitive

**Why state-based PPO:**
- Simple, fast to train
- 2-layer MLP (Swift proved this works)
- We have expert trajectories for reward shaping
- Perfect state in simulation = no perception gap
- Can upgrade to pixels later for physical stage

## Observation Space (State-Based)

Following Swift and E2E RL papers:

```python
observation = {
    # Drone state (13D)
    'position': [x, y, z],           # 3D
    'velocity': [vx, vy, vz],        # 3D  
    'orientation': [qw, qx, qy, qz], # 4D (quaternion)
    'angular_velocity': [wx, wy, wz], # 3D
    
    # Relative gate info (variable, but key)
    'next_gate_relative': [dx, dy, dz],  # 3D — relative position to next gate
    'next_gate_distance': [d],            # 1D — scalar distance
    'gate_direction': [nx, ny, nz],       # 3D — gate normal (which way to fly through)
    
    # Optional: lookahead
    'next_next_gate_relative': [dx, dy, dz],  # 3D — plan ahead
}
# Total: ~20-26D
```

## Action Space

CTBR format (same as human pilots, same as Swift):
```python
action = [collective_thrust, omega_x, omega_y, omega_z]  # 4D, [-1, 1] mapped to physical limits
```

## Reward Function

Adapted from Dream to Fly (Eq. 1), which is itself adapted from Swift:

```python
def reward(state, prev_state, action):
    # Progress: move closer to next gate center
    progress = dist(gate, prev_pos) - dist(gate, curr_pos)
    
    # Gate passage bonus
    gate_bonus = 10.0 if passed_gate else 0.0
    
    # Collision penalty
    collision = -4.0 if crashed else 0.0
    
    # Body rate penalty (smooth flight)
    rate_penalty = -0.01 * norm(omega)
    
    # Optional: time penalty (encourage speed)
    time_penalty = -0.01  # per step
    
    return 1.0 * progress + gate_bonus + collision + rate_penalty + time_penalty
```

**Key insight from Swift:** NO perception reward needed (we have state). NO path-following penalty — let the agent find its own trajectory.

## Training Pipeline

### Phase 1: Behavior Cloning Warm-Start
- Use optimal trajectory as demonstration data
- Pre-train the policy network to roughly track the trajectory
- This gives PPO a non-random starting point (critical for complex tracks)

### Phase 2: PPO Fine-Tuning
- Algorithm: PPO (proven by Swift, simpler than SAC for this domain)
- Network: 2-layer MLP, [256, 256] or [128, 128] hidden dims
- Learning rate: 3e-4 (standard)
- Discount: γ = 0.99
- Episodes per update: ~64-256 parallel environments

### Phase 3: Domain Randomization (for robustness)
- Randomize: mass (±10%), motor constants (±5%), drag (±20%)
- Gate position noise (±0.1m)
- Latency injection (1-3 control steps)
- This makes the policy robust even in simulation

## Implementation Plan

1. **Gym Environment Wrapper** — Wrap drone_env_v2.py in OpenAI Gym interface
2. **BC Pre-training** — Use expert trajectory for warm-start
3. **PPO Training** — Use stable-baselines3 (fast, well-tested)
4. **Evaluation** — Gate passage rate, lap time, tolerance metrics
5. **Iterate** — Reward tuning, architecture search

## Timeline

- Day 1 (today): Gym wrapper + BC pre-training
- Day 2-3: PPO training loop, first results
- Day 4-5: Reward tuning, domain randomization
- Day 6-7: Performance optimization, gauntlet training

## References for Implementation

- stable-baselines3: https://stable-baselines3.readthedocs.io/
- Swift reward: progress + gate bonus + collision penalty (no perception reward in our case)
- Dream to Fly reward: same structure, b1=1.0, b2=0.01
- Network: 2-layer MLP, tanh activation on output (bounded actions)
