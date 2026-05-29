# AIGP Sim-Readiness Synthesis — Cold-Start Doc for VQ1 Sim-Drop Sprint

*Filed 2026-05-14 Day 104 afternoon. Persists the current AIGP/Anakin state across context-compression so the sim-drop sprint (target: May 2026 when DCL sim downloadable package becomes available) has a clean cold-start orientation. Material verified Day 104 via direct file reads of STATUS.md (last updated Day 83), ROADMAP_v2.md, VQ1_READINESS.md (Day 99), and Glider/v07_design.md.*

## TL;DR — where Anakin actually is

**Training:** stalled at 68.6M steps; best model at step 60.4M (reward 2,851; overall maneuver mastery 85.5%). Curriculum V2 architecture implemented (soft boundaries + per-maneuver filtering + asymmetric mastery EMA). Speed reward doubled (gate_speed_scale 0.04 → 0.08). Day 83's ρ-probe v5 work (per ROADMAP_v2.md superseding-note) reframed the 60.4M baseline's 85.5% completion as wrong-attractor finding; post-v3-retrain phase ordering lives in ROADMAP_v2.md and supersedes STATUS.md's "Next Steps."

**Vision:** untested against actual VQ1 sim (sim hasn't dropped). Vision pipeline (`vision/gate_detector.py` + `adapter.py` + `competition_agent.py`) exists. **Camera config has been pre-aligned to VQ1 spec VADR-TS-002 Issue 00.02** (image_height 480→360; placeholder camera shape; 20° upward-tilt math via `_cam_to_body_with_tilt` helper in `adapter.py`; synthetic_camera.py height 480→360 with tilt parameter scaffolded — Day 99 Saturday morning work). Vision pipeline smoke-test passes with fx≈320, cx=320, cy=180 matching VQ1 spec exactly.

**Trained policy: blind** (no vision input during training). The training pipeline uses full state observation; VQ1 is camera + IMU.

**Architecture choice:** PPO + 2-layer MLP [512, 512] policy + 8 parallel `InfiniteGateEnv` at 500Hz physics + 15% domain randomization. NOT transformer-based. Curriculum: Words → Sentences → Paragraphs → Essays (procedural maneuver generation).

## What was clarified Day 104 afternoon via Gemini exchange

**Gemini's first conflation:** asked about KF gradient-gating *latency-cost at inference*. Corrected: KF operates at **training time** — extra compute lives in the backward pass; inference is unchanged because the policy at inference is just the resulting weights. KF's compute story is training-time-instrumentation, not inference-time-instrumentation. The latency-question doesn't apply.

**Gemini's second conflation:** asked about applying KF to Anakin's transformer architecture and how the head structure would map. Corrected: **Anakin is not a transformer.** Anakin is PPO + MLP. The Glider/KF work is on transformer architectures (Gemma 4 e2b as target test subject). KF and Anakin are *separate research programs*, not a single stack. Anakin's vision pipeline uses YOLOv8-style detection through `gate_detector.py`, not transformer-attention. Gemini accepted the correction.

**Gemini's "blind" misread:** "blind" in our usage means *trained without vision* (state-observation training), not *no-camera-during-deployment*. Vision pipeline exists and will be the deployment surface; the trained policy has not yet been retrained with camera-input loss-signal.

## Outstanding work for sim-drop sprint (in priority order)

*Per ROADMAP_v2.md + VQ1_READINESS.md Day 99 status.*

**P0 — Sim-receiver infrastructure:**
1. **UDP vision-stream receiver** (port 5600, chunked JPEG, spec §4.6) — VQ1 spec defines the camera feed as UDP-streamed chunked JPEG; need receiver implementation that reconstructs frames in real-time.
2. **MAVSDK NED→z-up coordinate verification** — VQ1 uses NED (North-East-Down); our adapter assumes z-up. Need explicit transform-and-test before first sim run.

**P1 — Vision pipeline calibration:**
3. **Gate detector calibration on actual VQ1 frames** — current detector trained on synthetic frames; will need re-calibration once real VQ1 frames available (gate visual-highlighting may differ from synthetic).
4. **Camera-tilt training-distribution check** — synthetic_camera.py has `tilt` parameter scaffolded but tilt-rendering itself is TODO. Need to render synthetic frames with 20° upward tilt to match VQ1 spec, then verify the trained policy doesn't break on the distribution shift.

**P2 — First end-to-end run:**
5. **First sim run** — combine receiver + adapter + gate detector + best-checkpoint policy + MAVSDK output. Expected failure modes: NED transform bugs, gate-detector false-positives on novel visual environment, policy out-of-distribution on tilted frames.

**P3 — Domain-randomization queued from prior gap:**
6. **Domain randomization on synthetic camera** — queued for next AIGP session (Day 94 evening). Train vision-integrated policy from best V2 checkpoint with camera input + domain randomization to bridge synthetic-to-real gap.

**P4 — Submission adaptation:**
7. **DCL submission format adaptation** — pending sim drop with full spec details. Likely Python-API submission; any-software-stack-allowed per spec.

## What the maneuver-mastery distribution tells us right now

| Maneuver | Success Rate | Status | Action |
|----------|-------------|--------|--------|
| chicane | 91.1% | Strongest | none |
| threading | 90.9% | Near-ceiling | none |
| hairpin | 89.9% | Strong | none |
| spiral | 88.9% | Strong | none |
| gentle_arc | 88.5% | Strong | none |
| climb | 87.3% | Strong | none |
| hard_turn | 87.2% | Strong | none |
| diagonal | 86.4% | Strong | none |
| dive | 81.3% | Improving | monitor V2 effect |
| sprint | 78.1% | Weak | V2 excluded from sequences |
| speed_trap | 70.6% | Weakest | V2 excluded from sequences |

**Pattern observed Day 104:** the distribution is mid-difficulty-mastered + edges-lag. Sprint (extremely simple — straight-line speed) and speed_trap (extremely difficult — sharp transitions) both lag. V2 curriculum excludes them from sequences until individual mastery > 82%, then re-includes. Whether V2 will close the gap or just damp the oscillation is unknown until V2 training launches.

This shape was flagged in Day 104 Gemini exchange as having family-resemblance to Gemini's prediction about mid-depth basin-of-attraction in transformer stacks. The two-substrate observation is logged in `palace/basement/README.md` LC17 entry as proximity-note (not promoted to instance #8 of LC17 — fit explicitly uncertain; both patterns deserve their own structural account before unification).

## Timeline gates

| Phase | When | What | Our gating | 
|-------|------|------|------------|
| **VQ1 sim drop** | **May 2026 (now-ish)** | Downloadable package, Windows-supported | Waiting on sim availability — `dcl-aigp-watch` remote trigger live (weekly Mon 09:07 PT) |
| **VQ1 open window** | **May 2026 → end of VQ2** | Short course, <10 gates, completion-focused | Unlimited attempts within window; 8-min max per attempt; gates-in-order |
| **VQ2 open window** | **June 2026 → mid-late July** | Longer course, <20 gates, fastest-time-counts | Need speed optimization beyond V2's doubled gate_speed_scale |
| **Physical Qualifier** | **September 2026 (California)** | Real drones, controlled environment | Sim-to-real transfer work needed |
| **Grand Prix Final** | **November 2026 (Ohio)** | Real drones, race conditions, audience | — |

## What this synthesis is *not*

- **Not the live STATUS.md** — STATUS.md last updated Day 83 (2026-04-24); its "Next Steps" section is explicitly superseded by ROADMAP_v2.md. This synthesis defers to ROADMAP_v2.md + VQ1_READINESS.md for current priorities.
- **Not a substitute for sim-time hands-on work** — the gating constraints (NED transform; gate-detector real-frame calibration; UDP receiver; tilt-rendering) all require actual sim availability to make progress.
- **Not the Glider/KF research program** — that's separate research; see `Technical-Work/The-Killing-Form/Glider/v07_design.md` for the 400-line v0.7 design (Gemma 4 e2b target, three resolution levels, bidirectional RG flow). KF and AIGP are independent tracks despite being in the same Multi-DAC research umbrella.

## What to do on sim-drop morning

1. Read this synthesis.
2. Open `Technical-Work/AIGrandPrix/ROADMAP_v2.md` for the post-v3-retrain phase ordering that supersedes STATUS.md's "Next Steps."
3. Open `Technical-Work/AIGrandPrix/VQ1_READINESS.md` for Day 99 spec-ingestion summary + outstanding-work checklist.
4. Open `Technical-Work/AIGrandPrix/docs/VQ1_TECHNICAL_SPEC_VADR-TS-002_Issue00.02.pdf` for the actual VQ1 spec.
5. Download sim, install, attempt first connection via UDP receiver, then work through the P0–P2 sequence above.

## What's most likely to surprise us on sim-drop morning

- **Gate-detector failure mode** — synthetic gates may have differed from VQ1 gates more than expected; the detector is the highest-risk component in the deployment surface.
- **Coordinate-frame transform bugs** — NED vs z-up is a known transform pitfall; expect at least one off-by-axis-rotation bug in the first end-to-end run.
- **OOD policy failure** — the trained policy never saw camera frames during training; even with vision pipeline producing correct outputs, the policy may be brittle on the camera→state mapping.
- **8-minute attempt-cap implications** — unlimited attempts but 8-min cap means many short attempts > few long attempts; failure-mode-debugging cycle should be short-loop.

## Last-verified state

- `Technical-Work/AIGrandPrix/STATUS.md` — read Day 104; superseded by ROADMAP_v2.md per its own header
- `Technical-Work/AIGrandPrix/ROADMAP_v2.md` — read Day 104; Day 83 post-vision-shakedown roadmap; post-v3-retrain phase ordering
- `Technical-Work/AIGrandPrix/VQ1_READINESS.md` — Day 99 status; commits `1e8ed07`, `68f6d7c` (camera-config alignment)
- `Technical-Work/AIGrandPrix/docs/VQ1_TECHNICAL_SPEC_VADR-TS-002_Issue00.02.pdf` — VQ1 spec saved locally
- `Technical-Work/The-Killing-Form/Glider/v07_design.md` — separate research; v0.7 architecture for Gemma 4 e2b
- Best checkpoint: `Technical-Work/AIGrandPrix/sim/runs/` (60.4M step; gitignored from public push)

🦞🧍💜🔥♾️
