# AI Grand Prix — 7-Week Curriculum

*From zero to competitive in autonomous drone racing.*
*Team: Clayton (intuition, strategy) + Clawd (research, code, iteration)*

## Guiding Principle
The virtual qualifiers (April–June) are **simulation only**. No sim-to-real gap. No hardware concerns. Pure algorithm performance. This is our advantage — we can focus entirely on the control problem without worrying about physical transfer until September.

---

## Week 1: Foundations (Feb 10-16)
*Goal: Understand the problem space. Get a drone flying in sim.*

### Clayton
- [x] Read drone-physics-101.md
- [ ] Watch 30 min of FPV drone racing (YouTube: "DRL Allianz World Championship")
- [ ] Install VS Build Tools (C++ workload)
- [ ] Watch: 3Blue1Brown "Neural Networks" playlist (4 videos, ~1hr) — visual intuition for RL

### Clawd
- [x] Read & summarize Swift paper
- [ ] Get simulation environment running (gym-pybullet-drones or custom)
- [ ] Write first "fly straight" test script
- [ ] Survey DCL platform (any early documentation?)
- [ ] Read "Dream to Fly" (DreamerV3) paper for alternative approach

### Together
- [ ] Walk through the sim together — see a drone fly (even badly)
- [ ] Discuss: what does "winning" look like in the virtual qualifier?

---

## Week 2: First RL Agent (Feb 17-23)
*Goal: Train something that can hover and move toward a target.*

### Learn
- Reinforcement learning basics: states, actions, rewards, policies
- PPO algorithm intuition (not the math — the *why*)
- OpenAI Gymnasium interface

### Build
- [ ] Simple reward: fly toward a point without crashing
- [ ] First PPO training run (Stable Baselines3)
- [ ] Visualize training progress
- [ ] Iterate on reward function

### Milestone: Agent can fly from A to B without crashing (most of the time)

---

## Week 3: Gate Navigation (Feb 24 - Mar 2)
*Goal: Fly through a single gate.*

### Learn
- Gate detection from visual input (or sim-provided gate positions)
- Reward shaping: how to incentivize gate passage
- Path planning basics

### Build
- [ ] Single-gate environment
- [ ] Reward function: progress toward gate center + pass through
- [ ] Train agent to reliably pass through one gate
- [ ] Add speed optimization (faster = better reward)

### Milestone: Agent reliably flies through a single gate from various starting positions

---

## Week 4: Multi-Gate Racing (Mar 3-9)
*Goal: Complete a course with multiple gates in sequence.*

### Learn
- Sequential decision making
- Course planning / racing line optimization
- Time-optimal control

### Build
- [ ] Multi-gate course environment
- [ ] Sequential gate reward (must pass in order)
- [ ] Train agent on increasing complexity (3 gates → 5 → 7)
- [ ] Speed vs. reliability tuning

### Milestone: Agent completes a 5+ gate course with consistent times

---

## Week 5: Visual Perception (Mar 10-16)
*Goal: Add camera-based perception if the competition requires it.*

**Note:** This week depends on what DCL's platform provides. If they give gate positions as telemetry, we skip heavy CV and focus on control refinement. If we need to detect gates from images, this week is critical.

### Learn (if needed)
- CNN basics for object detection
- Gate corner detection
- State estimation from visual features

### Build (if needed)
- [ ] Gate detector network
- [ ] Integration: perception → state → control pipeline
- [ ] Train end-to-end or modular (decision based on platform)

### Alternative (if perception not needed)
- [ ] Advanced reward engineering
- [ ] Domain randomization (vary physics params during training)
- [ ] Ensemble policies / robustness testing

### Milestone: Full perception-to-control pipeline working, OR bulletproof control policy

---

## Week 6: Optimization & Robustness (Mar 17-23)
*Goal: Make it fast AND reliable.*

### Build
- [ ] Hyperparameter search (learning rate, network size, reward weights)
- [ ] Domain randomization: randomize wind, mass, drag, sensor noise
- [ ] Test on varied courses (generalization)
- [ ] Racing line optimization
- [ ] Crash recovery strategies

### Milestone: Agent is both fast and robust across course variations

---

## Week 7: Competition Prep (Mar 24-30)
*Goal: Polish and prepare for platform submission.*

### Build
- [ ] Adapt code to DCL platform API (specs should be available by now)
- [ ] Final performance optimization
- [ ] Test submission pipeline
- [ ] Edge case hunting: what breaks the agent?
- [ ] Documentation for our own reference

### Milestone: Submission-ready code that we're proud of

---

## Ongoing Throughout

### Daily
- Clawd: 1-2 hours research/coding per session
- Clayton: 30-60 min learning + discussion

### Weekly
- Sunday: Review progress, adjust curriculum
- Mid-week: Technical deep-dive discussion

### Resources Library (building)
- Swift paper (Nature 2023) — primary reference
- Dream to Fly (DreamerV3, 2025) — alternative approach
- Stable Baselines3 docs
- Gymnasium docs
- gym-pybullet-drones (if we use it)
- DCL platform docs (when released)

---

## The Meta-Strategy

We don't need to reinvent autonomous flight. The Swift team already proved the approach works and published everything. Our job is to:

1. **Implement the proven approach** (PPO + simple MLP)
2. **Optimize for the specific competition format** (DCL's platform, their physics, their gates)
3. **Iterate faster than other teams** (our 24/7 availability is an edge)
4. **Be robust** (consistent > occasionally brilliant)

The teams with more PhDs will probably build fancier architectures. Our edge is speed of iteration, willingness to try things, and the fact that the winning approach is often the simplest one executed well.

---

*"If you think you can build an autonomy stack that can out-fly the world's best, show us." — Palmer Luckey*

*We intend to.* 🦞🔥
