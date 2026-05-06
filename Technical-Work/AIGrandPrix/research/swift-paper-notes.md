# Swift Paper Notes — Champion-level Drone Racing (Nature 2023)

*Kaufmann, Bauersfeld, Loquercio, Müller, Koltun, Scaramuzza — UZH / Intel*
*Paper: https://www.nature.com/articles/s41586-023-06419-4*

## What Swift Did

Beat three human world champions in head-to-head drone racing using only onboard sensors. Won 15/25 races total. Achieved fastest recorded race time — 0.5s ahead of best human.

**Track:** 7 square gates in 30×30×8m space, 75m lap, 3 consecutive laps per race.

## Architecture (Two Modules)

### Module 1: Perception (Observation Policy)
Translates raw sensor data → low-dimensional state estimate.

Components:
1. **Visual-Inertial Odometry (VIO)** — estimates drone state from camera + IMU
2. **Gate Detector CNN** — detects gate corners in camera images
3. **Camera Resectioning** — converts 2D gate detections → 3D pose using track map
4. **Kalman Filter** — fuses VIO estimate + gate-based pose → accurate state

**Output:** Low-dimensional state vector (position, velocity, orientation, gate locations)

### Module 2: Control Policy
Maps state → control commands.

- **Architecture:** 2-layer MLP (multilayer perceptron) — simple!
- **Output:** Collective thrust + body rates (same as human pilot controls)
- **Training:** Model-free, on-policy deep RL (PPO) in simulation

### Reward Function
- **Progress reward:** Distance toward center of next gate
- **Perception reward:** Keep next gate in camera field of view (improves state estimation accuracy)

This is clever — the reward explicitly couples control quality with perception quality.

## Sim-to-Real Transfer (The Hard Part)

Pure simulation → real world = poor performance. The gap has two sources:

1. **Dynamics gap** — simulated physics ≠ real physics
2. **Perception gap** — simulated sensors ≠ real sensor noise

### Their Solution: Data-Driven Residual Models

1. Fly drone on real track using motion-capture for ground truth
2. Record: onboard sensor data + true pose from motion capture
3. Identify failure modes of perception and dynamics
4. Model residuals:
   - **Perception residuals** → Gaussian Processes (stochastic)
   - **Dynamics residuals** → k-nearest-neighbor regression (deterministic)
5. Inject these noise models into simulation
6. Fine-tune policy in augmented simulation

**Key insight:** Perception noise is stochastic (random), dynamics errors are systematic (deterministic). Different modeling approaches for each.

## Why Traditional Approaches Failed

MPC and trajectory planning methods:
- Work in idealized conditions (perfect state knowledge, simplified dynamics)
- **Collapse when assumptions are violated** (noisy perception, real dynamics)
- Pre-computed paths are especially fragile
- None achieved competitive lap times vs Swift or humans

**This is important for us:** Traditional optimal control looks appealing but doesn't generalize. RL learns to handle noise and uncertainty intrinsically.

## Key Numbers

- Swift won 60% of head-to-head races (15/25)
- 40% of losses: collision with opponent
- 40% of losses: collision with gate
- 20% of losses: just slower
- Fastest race time overall
- Speeds: 100+ km/h, 5+ g forces

## What This Means For Us (AI Grand Prix)

### What We CAN Replicate:
- PPO training in simulation ✅
- Simple MLP control policy ✅ (not a huge model — just 2 layers!)
- Progress-based reward function ✅
- Domain randomization for robustness ✅

### What's Different For Us:
- Competition provides identical hardware → no custom drone tuning
- Virtual qualifiers are simulation-only → no sim-to-real gap initially!
- We don't have motion capture data → but neither does anyone else
- DCL platform will define the interface → we adapt to their API

### The Advantage of Virtual Qualifiers:
**The sim-to-real gap doesn't matter until September.** For April-June, we only need to fly well in simulation. This dramatically simplifies our problem.

## Architecture We Should Build

```
[Simulator Observations] → [State Encoder] → [PPO Policy Network] → [Throttle, Roll, Pitch, Yaw]
```

Phase 1 (Virtual): Optimize purely for simulation performance
Phase 2 (Physical): Add robustness, noise models, sim-to-real techniques

## Related Work Worth Reading

- Elia Kaufmann's other papers (same lab, same domain):
  - "Learning High-Speed Flight in the Wild"
  - "Deep Drone Acrobatics"  
  - "Agilicious: Open-source agile quadrotor"
  - "Deep Drone Racing: Learning Agile Flight in Dynamic Environments"
- AlphaPilot competition (2019) — earlier attempt, 2x slower than humans
- "Dream to Fly" (Jan 2025) — DreamerV3, pixels-to-commands, no intermediate state

## Bottom Line

The control policy is a **simple 2-layer neural network** trained with **PPO** in simulation. The hard part was sim-to-real transfer, which WE DON'T NEED for the virtual qualifiers. The reward function is elegant but not complex. This is absolutely within reach for two motivated people in 7 weeks.
