# AI Grand Prix — Autonomous Drone Racing

Autonomous drone racing agent for the [AI Grand Prix](https://aigrandprix.com) competition. PPO-based reinforcement learning with curriculum training, computer vision gate detection, and time-optimal trajectory planning.

## Architecture

- **Policy**: MLP (256x256) trained with PPO (Proximal Policy Optimization)
- **Training**: Curriculum learning across procedurally generated courses
- **Vision**: Gate detection via color segmentation + PnP pose estimation
- **Planning**: Time-optimal trajectory through RPG planner

## Directory Guide

### `sim/` — Training Environment
Gymnasium-compatible 3D quadrotor environments with realistic physics (drag, motor dynamics, IMU noise).

- `drone_env.py` / `drone_env_v2.py` — Quadrotor physics environments
- `infinite_gate_env.py` — Infinite procedural gate sequence for curriculum training
- `train_ppo.py` — Core PPO training loop
- `train_curriculum.py` — Curriculum learning with progressive difficulty
- `train_imitation.py` — Behavior cloning from expert trajectories
- `tracking_controller.py` — Low-level throttle and attitude control
- `sequence_generators.py` — Procedural track pattern generation

### `vision/` — Perception Pipeline
Gate detection and pose estimation for real-world deployment.

- `gate_detector.py` — Color-based gate detection with contour analysis
- `adapter.py` — Competition interface adapter
- `competition_agent.py` — Full competition agent integrating vision + policy
- `mavsdk_client.py` — MAVLink drone communication
- `synthetic_camera.py` — Synthetic image generation for training

### `tracks/` — Course Definitions
Benchmark courses for training and evaluation.

- `clayton_master_course.py` — Master benchmark (comprehensive test)
- `generate_tracks.py` — Procedural course generation
- Various themed courses: autobahn, corkscrew, elevator shaft, gauntlet, whiplash

### `planning/` — Time-Optimal Trajectory
RPG-based minimum-time trajectory planner with full quadrotor dynamics.

### `archive/` — Training Experiments
Historical training variants (v2-v10) documenting the progression of training strategies, plus evaluation and debugging scripts.

## Status

Waiting for VQ1 simulator specifications. Training infrastructure is ready.
