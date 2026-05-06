# Papers Found by Clayton (Feb 9, 2026)

Clayton watched drone racing footage, identified the key insight (gate-to-gate discrete optimization),
then found the team that won Abu Dhabi A2RL 2025 and collected their papers.

## CRITICAL — The Gold Papers

### 1. MonoRace: Winning Champion-Level Drone Racing (Jan 2026)
**arxiv: 2601.15222** — THIS IS THE MOST IMPORTANT PAPER
- Won the 2025 Abu Dhabi A2RL competition — beat ALL AI teams AND 3 human world champions
- Uses MONOCULAR camera (not stereo like Swift!) + IMU
- Neural network sends DIRECT MOTOR COMMANDS at 500Hz (no inner loop controller!)
- Speeds up to 100 km/h on competition track
- Handles camera interference and IMU saturation
- Key innovation: offline optimization using gate geometry to refine state estimation
- Team: TU Delft (MAVLab) — Christophe De Wagter et al.

**Why this matters:** This is the CURRENT state of the art. More recent than Swift. Won a real competition in 2025. And their approach is simpler in some ways (monocular, no stereo).

### 2. End-to-End RL for Time-Optimal Quadcopter Flight (Nov 2023)
**arxiv: 2311.16948** — Robin Ferede et al. (same TU Delft group)
- E2E RL giving DIRECT MOTOR COMMANDS (bypasses inner loop controller)
- 1.39s faster than state-of-the-art in simulation
- 0.17s faster in real-world
- Uses learned residual model + adaptive compensation for sim-to-real
- Key insight: removing the inner loop controller abstraction enables more optimal control

**Why this matters:** The E2E approach (direct motor commands) is faster than the layered approach (commands → inner loop → motors). This is the foundation MonoRace built on.

## RELEVANT — Useful Context

### 3. Adaptive Surrogate Gradients for SNN RL (Oct 2025)
**arxiv: 2510.24461** — Same TU Delft group
- Spiking Neural Networks for drone control (neuromorphic computing)
- Novel training: privileged guiding policy bootstraps learning
- 2.1x improvement with adaptive slope schedules
- Real-world drone position control
- **Relevant for us:** The privileged guiding policy idea — train with perfect info, deploy with limited info

### 4. All Eyes, No IMU: Vision-Only Flight (Jul 2025)
**arxiv: 2507.11302** — Same group
- Flight control using ONLY a camera (no IMU!)
- Event camera + recurrent CNN estimates attitude and rotation rate
- Works in real-world tests
- **Relevant for us:** Shows vision can replace traditional sensors. If competition limits sensor input, this matters.

## ADJACENT — Less Directly Relevant

### 5. Breaking the Circle: Orographic Soaring (Oct 2025)
**arxiv: 2510.23084** — Control switching for MAV soaring
- About fixed-wing soaring, not quadcopter racing
- INDI controller with angle of attack incorporation
- Less directly relevant but shows the group's breadth

### 6. Memristors for G&C Networks (Sep 2025)
**arxiv: 2509.02369** — Hardware acceleration for neural controllers
- Phase-Change Memory and RRAM for in-memory computing
- Space applications focus
- Not directly relevant for us (we're in software)

### 7. Tilt-Rotor Tailsitter (Mar 2025)
**arxiv: 2503.02158** — Novel aircraft design
- Tilt-rotor tailsitter with INDI control
- Not relevant for drone racing (different vehicle type)

## Key Takeaways

The team to study is **TU Delft MAVLab**. They:
1. Won A2RL 2025 (the real-world competition we'd face in physical stages)
2. Use end-to-end RL → direct motor commands (faster than layered approaches)
3. Monocular camera (simpler perception than Swift's stereo)
4. Neural network at 500Hz on flight controller
5. Offline optimization from flight data for calibration

**For our virtual qualifiers:** Papers #1 and #2 are the blueprint. E2E RL with direct commands. If the DCL platform provides motor-level control, this is the approach to take.

**The hierarchy of approaches:**
- Swift (2023): Perception → State → Inner loop controller → motors  
- E2E RL (2023): Perception → State → RL policy → motors (1.39s faster)
- MonoRace (2026): Monocular perception → RL policy → direct motor commands at 500Hz (WINS)

The trend is clear: fewer abstraction layers = faster = wins.
