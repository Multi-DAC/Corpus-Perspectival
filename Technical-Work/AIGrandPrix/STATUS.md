# Anakin (AI Grand Prix) — Project Status

**Last Updated:** 2026-04-24 Day 83 evening PST

> **For the active operating plan, see `ROADMAP.md`** (authored Day 83 post-v5-trajectory). This STATUS.md remains as background on the V2 curriculum + March 27 architecture state. The "Next Steps" section at the bottom of this file is **superseded by ROADMAP.md** as of Day 83 — the wrong-attractor finding (ρ-probe v1–v5) reframes the meaning of the 60.4M baseline's 85.5% completion number, and the post-v3-retrain phase ordering is in ROADMAP.md.

---

**Original last updated:** 2026-03-27 2:30 PM PST

## What Is This

Reinforcement learning drone racing agent ("Anakin") for the AI Grand Prix competition ($500K prize pool). Trains via PPO on procedurally generated infinite gate courses with an adaptive curriculum to build generalized flying skill that transfers to any track layout.

## Current State

- **Training:** STALLED at 68.6M steps — best model at step 60.4M (reward 2,851)
- **Curriculum V2:** IMPLEMENTED — soft boundaries + per-maneuver filtering + asymmetric EMA (March 27)
- **Speed reward:** DOUBLED — gate_speed_scale 0.04 → 0.08 (March 27)
- **VQ1 Specs:** AVAILABLE — monocular camera, throttle/roll/pitch/yaw control, Python API
- **Next training run:** Ready to launch V2 curriculum from best checkpoint

## What Changed (March 27, 2026)

### Curriculum V2 — All 3 changes now implemented

| Change | Description | Status |
|--------|-------------|--------|
| **1. Soft boundaries** | Continuous probability interpolation (no hard 80% cliff) | Already coded |
| **2. Per-maneuver filtering** | Only sequence-ready maneuvers (>82%) appear in sequences | Already coded |
| **3. Asymmetric mastery EMA** | EMA rises fast (α=0.02), falls slow (α=0.005). Prevents brief dips from collapsing curriculum. | **NEW — March 27** |

### Speed Incentive
- `gate_speed_scale` doubled from 0.04 to 0.08 (training AND eval)
- Directly rewards faster gate passage — addresses the "straightaway paradox"

### Stats Callback Improved
- Now shows EMA vs raw mastery (diagnose hysteresis behavior)
- Shows per-maneuver weak spots (<82%) in each stats print
- Eval reward config matches training (was inconsistent)

## Maneuver Mastery (last training — 23,600 episodes, 184,798 gates)

| Maneuver | Success Rate | Status |
|----------|-------------|--------|
| chicane | 91.1% | Strongest |
| threading | 90.9% | Near-ceiling |
| hairpin | 89.9% | Strong |
| spiral | 88.9% | Strong |
| gentle_arc | 88.5% | Strong |
| climb | 87.3% | Strong |
| hard_turn | 87.2% | Strong |
| diagonal | 86.4% | Strong |
| dive | 81.3% | Improving |
| sprint | 78.1% | Weak — excluded from sequences by V2 |
| speed_trap | 70.6% | Weakest — excluded from sequences by V2 |

**Overall: 85.5%** — V2 curriculum should push sprint/speed_trap up without destabilizing the rest.

## Competition Timeline

| Phase | When | What | Our Status |
|-------|------|------|------------|
| **VQ1** | **May 2026** (open until end of VQ2) | Short, simplified course, < 10 gates, completion-focused | Architecture ready; vision untested |
| **VQ2** | **June 2026** (open until mid-late July) | Longer course, < 20 gates, fastest time counts | Need speed optimization |
| **Physical Qualifier** | **September 2026** (California) | Real drones, controlled environment, no audience | — |
| **Grand Prix Final** | **November 2026** (Ohio) | Real drones, race conditions, audience, distractions | — |

### VQ1 Confirmed Details (April 9 email)
- Simulator: downloadable package, runs locally, Windows supported
- Internet required (anti-cheat)
- Can run multiple instances in parallel
- Gates consistent within each qualifier, change between VQ1 and VQ2
- Full 3D environment with elevation changes
- Unlimited attempts within qualification window
- 8 minute max per attempt
- Gates must be passed in correct order
- Any software stack allowed; code must be reviewable
- No human interaction during runs

## VQ1 Specs Summary

- **Camera:** Single FPV camera (~12MP wide-angle), forward-facing monocular RGB
- **Sensors:** Accelerometer, gyroscope, motor RPM readouts
- **Control:** Python API — throttle, roll, pitch, yaw
- **No LiDAR** — vision-only navigation
- **VQ1 environment:** Gates visually highlighted with visual aids
- **Limited coordinate info:** Starting position provided, then vision-only

**Gap analysis:** Our training uses full state observation. VQ1 is camera + IMU. Vision pipeline exists (`vision/gate_detector.py` + `adapter.py`) but needs verification against actual camera specs when simulator drops.

## Next Steps (Priority Order)

1. **Launch V2 curriculum training** — resume from best checkpoint (60.4M) with V2 curriculum + doubled speed reward. Target 10-20M additional steps.
2. **Monitor V2 training** — watch for: bistability damping, sprint/speed_trap improvement, EMA vs raw divergence
3. **Wait for DCL simulator** (May 2026) — when available, verify vision pipeline compatibility
4. **Vision integration** — train vision-integrated policy from best V2 checkpoint with camera input
5. **Submission adaptation** — adapt to DCL submission format

## Curriculum System (V2)

**Architecture:** Words → Sentences → Paragraphs → Essays (procedural generation)

**V2 improvements over V1:**
- **Soft boundaries:** Sentence probability ramps 0%→30% over 70%-90% mastery (was hard threshold at 80%)
- **Per-maneuver filtering:** Sprint and speed_trap excluded from sequences until individually >82%
- **Asymmetric EMA:** Curriculum mastery rises fast, falls slow — prevents oscillation between HIGH and LOW regimes
- **Speed incentive:** gate_speed_scale doubled to directly reward faster flight

**Predicted effect:** The 80% oscillation (documented in CURRICULUM_STRATEGY_V2.md) should damp. The agent should get sustained exposure to sequences and gradually push weak maneuvers up through individual word-mode practice.

## Training Infrastructure

- **PPO:** lr=3e-4 (3e-5 when resuming), clip=0.2, ent=0.01, n_steps=4096, batch=512
- **Network:** MLP [512, 512] (policy + value)
- **Environment:** 8 parallel `InfiniteGateEnv`, 500Hz physics, 15% domain randomization
- **Checkpoints:** Every 500K steps, best model saved on eval improvement

## Key Files

| Purpose | File |
|---------|------|
| **Physics** | `sim/drone_env_v2.py` |
| **Training** | `sim/train_infinite.py` |
| **Curriculum** | `sim/infinite_gate_env.py`, `sim/sequence_generators.py` |
| **V2 Design Doc** | `sim/CURRICULUM_STRATEGY_V2.md` |
| **Vision** | `vision/gate_detector.py`, `vision/adapter.py`, `vision/competition_agent.py` |
| **Best Model** | `sim/runs/` (60.4M step checkpoint) |

## Key Insights

1. **Curriculum V2 addresses root cause of plateau.** The bistability was caused by hard threshold + weak maneuvers in sequences + no hysteresis. All three now fixed.
2. **Speed reward was too low.** The "straightaway paradox" (safety > speed) is partially addressed by doubling gate_speed_scale.
3. **VQ1 format aligns with our pipeline.** Camera + TRPY control matches our vision pipeline + CTBR policy. The gap is training with visual input, not architecture.
4. **We have 2 months before VQ1.** Time to train V2, verify against simulator, integrate vision.
5. **Best model ≠ latest model.** Training past 60M didn't improve peak performance. V2 may change this.
