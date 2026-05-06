# VQ1 Readiness Assessment — April 9, 2026

*Assessed against the April 9 competition update email. Simulator not yet available.*

## Executive Summary

**We have the architecture. The gap is end-to-end integration with real visual input.**

Our policy can fly (85.5% gate completion in sim). Our vision pipeline exists (gate detector + PnP + adapter). Our competition interface is written (MAVSDK + submission agent). But the policy was trained on *perfect state observation*, and VQ1 provides only FPV camera + IMU telemetry. The bridge between these two has never been tested end-to-end on real imagery.

VQ1 is completion-focused (< 10 gates, clear visibility). This is our best scenario — classical CV on highlighted gates should be reliable.

## Component Readiness

| Component | Status | Confidence | Gap |
|-----------|--------|------------|-----|
| PPO policy (state-based) | ✅ TRAINED | HIGH | 85.5% gate completion, reward 2,851 |
| Curriculum training V2 | ✅ READY | HIGH | All 3 improvements implemented, not yet run from best checkpoint |
| Gate detector (classical CV) | ⚠️ PARTIAL | MEDIUM | Architecture sound, needs calibration on real VQ1 frames |
| Telemetry adapter | ✅ READY | HIGH | MAVSDK integration, coordinate transforms, TRPY mapping |
| Vision → Policy bridge | ✅ CODED | HIGH | Architecture clean, never tested with real imagery |
| Full pipeline end-to-end | ❌ UNTESTED | LOW | camera input is currently `np.zeros()` (competition_agent.py:148) |
| Robustness to visual noise | ❌ NO | LOW | Policy trained on perfect state, never seen noisy obs |
| Competition submission format | ⚠️ UNKNOWN | LOW | Awaiting simulator for format details |

## What We Have

### Training Pipeline
- `sim/train_infinite.py` — PPO training with infinite procedural gate courses
- `sim/infinite_gate_env.py` — Curriculum system (Words → Sentences → Paragraphs → Essays)
- Curriculum V2: soft boundaries, per-maneuver filtering, asymmetric EMA
- Best model: 60.4M steps, 85.5% overall completion, 91% on strongest maneuvers
- ~90 model checkpoints across multiple training runs
- 500Hz physics, 8 parallel envs, 15% domain randomization

### Vision Pipeline
- `vision/gate_detector.py` — Classical CV: brightness/HSV filtering → contour detection → quadrilateral fitting → PnP pose estimation
- `vision/adapter.py` — Bridges MAVLink telemetry + gate detection → 30-dim policy observation
- `vision/competition_agent.py` — Full competition loop: connect → arm → loop(telemetry → vision → policy → command)
- `vision/mavsdk_client.py` — MAVSDK interface with coordinate frame handling

### Control
- Policy outputs: [collective_thrust, ωx, ωy, ωz] in [-1, 1]
- Competition expects: Throttle, Roll rate, Pitch rate, Yaw rate
- Mapping handled in mavsdk_client.py

## The Critical Gap

**Line 148 of competition_agent.py:**
```python
camera = np.zeros((480, 640, 3), dtype=np.uint8)
```

This is where real camera frames need to go. Everything downstream of this line is implemented but untested with real data.

**The observation gap:** Our policy expects 30 dimensions including:
- Body-frame velocity (from telemetry ✅)
- Gravity vector in body frame (from telemetry ✅)  
- Gate-relative bearing and distance (from vision ⚠️)
- Angular velocity (from telemetry ✅)

The gate-relative information depends entirely on the vision pipeline working. If gate detection fails → policy doesn't know where to fly → crash.

## VQ1 Strategy

VQ1 is our best scenario:
- **< 10 gates** — fewer detection challenges
- **Clear visibility** — highlighted gates, minimal distractions
- **Completion, not speed** — reliability > performance
- **Unlimited attempts** — we can iterate fast

### When Simulator Drops (shortly before May):

**Day 1-2: Calibration**
1. Capture sample frames from simulator camera
2. Calibrate gate detector HSV/brightness thresholds on real gate appearance
3. Verify camera intrinsics (resolution, FOV) against our PnP model
4. Test gate detection offline on captured frames → measure detection rate

**Day 3-4: Integration**
5. Replace `np.zeros()` with actual camera stream
6. Run full pipeline end-to-end in simulator
7. Measure: detection rate, PnP accuracy, observation quality, flight stability

**Day 5-7: Adaptation**
8. If policy works with visual obs → submit, iterate on edge cases
9. If policy struggles → add observation noise to training, fine-tune 1-5M steps
10. If gate detection fails → switch to learned detector or adjust pipeline

**Week 2+: Optimization**
11. Fine-tune for specific VQ1 course layout
12. Improve robustness: missed detection fallback (hold heading, search pattern)
13. Speed optimization (only needed if VQ2 timeline allows)

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Gate detector fails on real frames | LOW (gates are highlighted) | HIGH | Pre-calibrate; have learned detector fallback |
| PnP inaccurate at distance | MEDIUM | MEDIUM | Use bearing-only at distance, PnP close-up |
| Policy brittle to noisy obs | MEDIUM | HIGH | Fine-tune with noise injection |
| Coordinate frame mismatch | LOW | HIGH | Verified in adapter; re-verify with sim |
| Simulator incompatible with MAVSDK | MEDIUM | HIGH | Check format on Day 1; may need new interface |
| VQ1 course has unexpected features | LOW (email says "minimal") | LOW | Unlimited attempts; adapt |

## What We Should Do Before Simulator Drops

1. **Resume V2 curriculum training** from best checkpoint (60.4M steps) — this costs nothing and improves the base policy. Even 5-10M additional steps could push sprint/speed_trap past 82%.

2. **Add observation noise injection** to training — make the policy robust to the kind of errors visual estimation introduces (bearing noise, distance noise, missed detections). This is cheap and high-value.

3. **Prepare a "blind flight" fallback** — if gate detection fails for N frames, hold last known heading and search. This prevents hard crashes from brief detection gaps.

4. **Test gate detector on synthetic test images** — we have `vision/synthetic_camera.py` and test images. Verify the pipeline works at least on synthetic data.

## Key Files

| Purpose | File |
|---------|------|
| **Competition entry point** | `vision/competition_agent.py` |
| **Gate detection** | `vision/gate_detector.py` |
| **Telemetry adapter** | `vision/adapter.py` |
| **MAVSDK interface** | `vision/mavsdk_client.py` |
| **Training** | `sim/train_infinite.py` |
| **Environment** | `sim/infinite_gate_env.py` |
| **Curriculum V2 design** | `sim/CURRICULUM_STRATEGY_V2.md` |
| **Best model** | `sim/runs/` (60.4M checkpoint) |
| **This assessment** | `VQ1_READINESS.md` |

---

*Bottom line: We're closer than we might think. The architecture is right, the policy can fly, the vision pipeline exists. The unknown is whether they work together. When the simulator drops, we'll know within 48 hours.*
