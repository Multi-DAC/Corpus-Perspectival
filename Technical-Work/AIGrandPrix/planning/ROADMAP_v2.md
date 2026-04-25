# Anakin VQ1+VQ2 Roadmap v2 — Pre-sim Window → Both Qualifier Windows

**Authored:** 2026-04-25 Day 84 afternoon (post-Phase-2 trajectory landing, post-vision-shakedown stages 1–3, post-Stage-3b-graded-confirmation, post-MAXIMUS-research, post-DCL-platform-research).
**Horizon:** Now → VQ1 sim drop (May 2026) → VQ2 sim drop (June 2026) → both qualifier windows close (July 2026).
**Authors:** Clawd + Clayton.
**Supersedes:** `ROADMAP.md` v1 (Day 83 evening, written before vision shakedown, before DCL constraint surfacing, before MAXIMUS intel).

---

## 0. Why v2 — what changed in 36 hours

Three forcing functions:

1. **Phase 2 67.5M trajectory landed** with 20.58 agg gates / 81% crash — capability emergence confirmed within the cured regime; `infinite_v3_phase2_60M` is the working policy line.
2. **Vision pipeline shakedown stages 1–3 sealed**, then Stage 3b run on Phase 2 37.5M produced the **graded-policy obs-noise amplification finding**: where baseline 60.4M's bang-bang absorbed Stage 2's residual PnP error (zero action drift across all scenarios), Phase 2 37.5M propagates the same residuals at ~5× into action space (max drift 0.488 roll_rate on climbing_8m, one yaw_rate sign flip on approach_8m_5mps). Vision precision budget is no longer slack.
3. **External research surfaced two reshaping facts**:
   - **DCL platform constraint:** only the starting coordinate is supplied — agent flies *without position telemetry*. FPV camera + IMU only. ~100 TOPS onboard budget. Visual-Inertial Odometry is mandatory, not optional. Our current state-based observation stack does not transfer.
   - **MAXIMUS / Northlake Labs is publicly running our stack:** SB3-PPO + gym-pybullet-drones + YOLOv8 vision + 2×256 MLP + relative gate encoding + curriculum + EMA action smoothing α=0.5. They've already published their failure log in detail. Treat it as free curriculum.

Two PnP-fix attempts (Move A reprojection-tiebreak; Move A' camera-axis pick + LM refinement) both failed and were reverted. Lesson banked: planar near-coplanar PnP ambiguity isn't fixable by tiebreak — the residual landscape is near-flat between the two sister solutions. Defensive rejection (refuse to publish a pose when ambiguity is unresolvable) is the right next move, not a sharper resolver. But more importantly: the placeholder synthetic-gate model doesn't justify further optimization; the right pivot is domain randomization + swap-ready architecture against the eventual DCL gate model.

---

## 1. The schedule and what it implies

| Window | Event | What it means |
|---|---|---|
| **Now → ~May** | Pre-sim window | Build position-less architecture, randomization, sim2real harness, attack policy laggards |
| **~May 2026** | VQ1 sim drops | Visually-highlighted gates, simplified course. Integration sprint. |
| **May → July** | VQ1 qualifier window open | Specialize one policy on VQ1 |
| **~June 2026** | VQ2 sim drops | 3D-scanned realistic environment, harder course |
| **June → July** | VQ2 qualifier window open | Train second policy on VQ2 (more dynamic training time available) |
| **~July 2026** | Both qualifier windows close | Submit both |
| **September 2026** | SoCal physical qualifier | Top finishers only — sim-to-real critical |
| **November 2026** | Ohio finals | — |

**The specialization-gradient experiment Clayton named:** train a VQ1 specialist (May–July, longer specialization horizon) and a VQ2 general/dynamic pilot (June–July, shorter specialization horizon, broader training distribution). The delta between them at submission is itself a clean measurement of the specialization-vs-general gradient — a P96-style empirical artifact independent of the competition outcome.

---

## 2. Constraints surfaced from research — design-shaping facts

### From DCL platform (publicly documented + leaked Northlake spec)

**Hard constraints (publicly documented, dcl-project.com):**
- Single FPV camera (~12MP wide-angle) + IMU. **No LiDAR. No position telemetry after starting coordinate.**
- Onboard compute ~100 TOPS (Jetson-class, more capable than Pi).
- Two virtual qualifier rounds: VQ1 (May, gates **visually highlighted**), VQ2 (June, **real 3D-scanned environment**).
- Scoring "primarily time-based but runs must successfully pass gates."
- Python primary, compiled extensions expected to work.

**Operational constraints (leaked via Northlake's blog, treat as best-known):**
- Submission: Python-only `.zip` ≤500 MB, Python 3.12, Ubuntu 24.04, CUDA 12.x.
- `metadata.json` + `requirements.txt` + `DCLAgent` class implementing `compute_action(telemetry)`.
- 120-second per-heat limit.
- Headless containerized eval.

**Unknowns (not public):**
- Physics engine (plausibly Unity given DCL game heritage, or PX4-SITL/Gazebo).
- Telemetry packet structure beyond camera+IMU.
- Sim rate and control rate.
- Exact Neros Archer flight controller / camera latency.

**Implication:** The single largest open question for our roadmap is whether telemetry includes IMU integration as derived state (attitude, body rates) or only raw IMU (accelerometer + gyro). The pre-sim window must produce architectures that work in either regime.

### From MAXIMUS / Northlake Labs (their published failure log)

**What we adopt (free wins from their work):**
- **Reward normalization off** (`norm_reward=False`). Their VecNorm trap finding cost them weeks; we confirm-and-skip. (We use `VecNormalize` for *observations* only, paired per-checkpoint per our prior memory finding.)
- **EMA action smoothing α=0.5** (71.4% jerk reduction in their measurement) — bolt onto eval/deployment, not training.
- **Sustain-not-spike promotion criterion:** ≥80% over rolling 50-episode window for curriculum advancement, not single-episode peak.
- **Anneal randomness/entropy on promotion:** prevents catastrophic forgetting (their Mixed Curriculum v2 lost 65% reward at 1M steps from un-annealed reintroduction).
- **No jerk penalty until policy is competent** (their v7 catastrophe: 97.7% → 4.4% completion).
- **Wind/disturbances only after 80% completion threshold** (action-variance collapse otherwise).
- **Relative gate encoding in body frame** (already our V2 design).

**Where we likely diverge / can leapfrog:**
- They use feedforward MLP only — no recurrence. For position-less DCL VIO we likely want either an LSTM head or a temporal-context window stacked into observations.
- They use geometric depth from known gate height (PnP-style). For VQ2's 3D-scanned environment with non-uniform gate appearance, a learned pose head probably wins.
- They have no real flight data. We have the same gap, but it's a known unknown to plan around, not a surprise.
- Their architecture is `[256,256]`. Our `[512,512]` Phase 2 line is larger — track whether this matters when policy has to also internalize VIO.

**Their schedule signal:** vision-policy integration April 15, submission early May. They are ~3 weeks ahead of where we'd be if we'd integrated in mid-April; they are **not** ahead on real flight data (they have none either).

---

## 3. Design principles banked

| # | Principle | Source | How to apply |
|---|---|---|---|
| P1 | **Vision precision budget scales with policy capability.** Saturated policies absorb obs noise; graded policies propagate it ~5×. | Stage 3b finding (Day 84 morning) | Set vision pipeline error budget against Phase-2-class graded policies, not baseline-class bang-bang. |
| P2 | **VecNormalize stats live in env, not policy.** Save `vecnorm.pkl` paired with every checkpoint. | Memory: `feedback_vecnorm_per_checkpoint.md` (Day 83) | All training scripts use `CheckpointWithVecNormalize`. Eval harness fails loud on missing pkl. |
| P3 | **Reward normalization off.** | Northlake VecNorm-trap finding | `norm_reward=False` everywhere. |
| P4 | **Sustain promotion, not spike promotion.** | Northlake speed-curriculum collapse | All curriculum advancement uses rolling-window thresholds. |
| P5 | **Anneal on promotion** (entropy, randomness, LR). | Northlake Mixed-Curriculum-v2 forgetting | LR drop 30%, entropy temporary boost, randomness ramp. |
| P6 | **Don't bolt secondary objectives onto a competent policy at full strength.** | Northlake v7 jerk catastrophe | Action-smoothing → EMA at deployment. Jerk penalty introduced only after task completion stabilized, at low weight, with halt criterion. |
| P7 | **Reconnaissance before construction.** | This roadmap | Read MAXIMUS posts before each new training run; check awesome-autonomous-drone-racing before each new component. |
| P8 | **Stop optimizing against placeholders.** | Two failed PnP fixes (Day 84 early afternoon) | Vision pipeline goes to swap-ready architecture + domain randomization, not residual-error chasing against synthetic gates. |
| P9 | **Coherence Principle methodology applied to training.** | KF program findings | Three-moment stratification (substrate-health / mode-commitment / capability-emergence) is the lens for reading any new training trajectory. |

---

## 4. Workstreams

### Workstream A — Vision pipeline pivot (now → VQ1 drop)

**Goal:** A vision pipeline that is **swap-ready** for any gate appearance the DCL sim presents, validated under randomized inputs.

**A1. Defensive rejection in current detector** (1 day)
- Add ambiguity-rejection in `gate_detector.py`: if IPPE_SQUARE returns two solutions with reprojection-error ratio < 1.5, refuse to publish a pose; downstream observation falls back to last-known-good or "no detection" sentinel.
- This is the move that should have happened instead of Move A/A'.

**A2. Domain randomization harness** (3–5 days)
- Build `vision/randomization/` module supplying: gate color/material/shape parameter draws, lighting (hemispheric, directional, spot, exposure), camera intrinsics (FOV 60–110°, resolution 320–640, exposure), motion blur, chromatic aberration.
- Apply to `synthetic_camera.py` rendering. Stage 1–3 shakedown re-runs become statistical (N=100 trials per scenario across randomization range), not single-frame.
- Calibrate noise model in `train_v3.py` (or `train_phase2.py` successor) against measured detector error distribution under randomization, not against guessed numbers.

**A3. Swap-ready architecture** (2–3 days)
- Wrap detector + adapter behind `GateObservationProvider` interface with concrete `SyntheticDetectorProvider` and (placeholder) `DCLDetectorProvider`. Policy training and shakedown both bind to the interface.
- When DCL drops, swap the provider; downstream stack untouched.

**A4. (Conditional, post-VQ1-drop) Learned pose head** (1–2 weeks if pursued)
- Only if VQ2's 3D-scanned environment breaks geometric depth from known gate height. Decision gated on first VQ2 sim observation.
- Reference: Swift (Kaufmann et al. 2023, Nature) architecture, port via Flightmare patterns.

**Deferred:** PnP residual chasing against synthetic gates (P8). Stage 4 TRPY mapping (depends on DCL telemetry packet structure).

### Workstream B — Policy training continued (now → VQ1 drop, then split)

**Goal:** Continue Phase 2 trajectory to attack the laggard maneuvers; build the position-less variant for DCL.

**B1. Continue Phase 2 capability ramp** (ongoing GPU time)
- Phase 2 67.5M is the working baseline. Predict 75M / 90M / 120M continuation produces continued capability emergence on the long-curving maneuvers (per the +12 hairpin / +15 threading climb 22.5M → 67.5M).
- Pre-commit predictions per checkpoint per the P96 protocol (already established).

**B2. Attack the laggards** (parallel track)
- 22.5M → 67.5M trajectory: bottom-of-pack stayed bottom-of-pack. `sprint` still ~4.5, `dive` still ~6, `speed_trap` *regressed* to ~2.0.
- Hypothesis: short maneuvers don't get curriculum time proportional to their crash-difficulty. Build `train_phase3_lagger_focus.py` with per-maneuver sampling weighted *inversely* to current mean gates per episode (sample harder-for-this-policy maneuvers more).
- M13 budget: extended-exponential ramps on lagger maneuvers may show late capability emergence the way hairpin did.

**B3. Position-less observation variant** (NEW — driven by DCL constraint)
- Build `ImprovedObsWrapperVIO` that strips position from observations and replaces it with: (a) IMU integration over a window, (b) relative gate vectors in body frame (already present), (c) optical-flow-derived velocity estimate (proxy for VIO output the DCL sim will provide).
- Train Phase 2 successor under this observation regime in parallel with B1. Expect transient capability dip → re-ramp.
- This is the **architecture-change risk concentration**. Run early so the dip absorbs in the pre-sim window, not after.

**B4. (Conditional) LSTM head** (1 week if pursued)
- If position-less variant struggles to integrate IMU history with feedforward MLP, add an LSTM hidden layer between encoder and policy heads.
- Decision gated on B3 outcome at +15M steps under VIO obs.

### Workstream C — Sim2real benchmark harness (now → VQ1 drop)

**Goal:** A pre-committed measurement protocol that runs identically on synthetic frames now and on DCL sim frames in May. The harness exists *before* the sim drops, so May-Day-1 is "run the harness," not "design the harness."

**C1. Harness skeleton** (2 days)
- `bench/simreal_harness.py` defines: scenarios (12+, covering each maneuver class), metrics (per-scenario: gate completion, mean episode length, crash type distribution, per-step action distribution moments, per-step observation hash for determinism), output schema (JSON, versioned).
- Runs against the swap-ready vision provider (Workstream A3).

**C2. Pre-commit baselines** (1 day)
- Run harness now against `synthetic_camera + gate_detector + Phase2-67.5M`. Commit the results JSON before sim drops. Predict VQ1-sim-frame results will be *worse* by some named factor on each metric. Predictions are scored against actual VQ1 results.
- This is P96 applied to sim-to-real: predict before measure.

**C3. Calibration playbook** (already drafted in `VQ1_READINESS.md` Days 1–2)
- HSV/brightness/intrinsics calibration sequence. Bind it to harness so results are reproducible across operators.

### Workstream D — Reconnaissance (continuous, low-bandwidth)

**Goal:** Stay current on competitor public artifacts and field reference implementations.

**D1. MAXIMUS blog as standing input**
- Subscribe (RSS or scripted poll) to `northlakelabs.com/max/blog/` updates. Each new post: 30-min read, extract any failure-log items into our principles register.

**D2. Awesome-autonomous-drone-racing as the field reference**
- `github.com/aimarket/awesome-autonomous-drone-racing` — review monthly. Particularly check for: any DCL-specific repos appearing, any Swift companion-code release, any AI-Grand-Prix community repos.

**D3. AlphaPilot / TU Delft MAVLab paper as conservative-fallback architecture**
- TU Delft's "AlphaPilot: autonomous drone racing" (Springer, DOI 10.1007/s10514-021-10011-y) — gate-detection CNN + state-machine + planning stack. If RL approach hits a wall, this is the deterministic fallback.

**D4. Swift (Kaufmann 2023, Nature) as method reference**
- For VQ2's harder environment: visual-inertial input + RL policy + sim-to-real. No companion code, but the architecture descriptions are detailed.

**D5. UZH-RPG `learned_inertial_model_odometry` as VIO reference**
- `github.com/uzh-rpg/learned_inertial_model_odometry` — actual public code for IMU-based odometry. Relevant to Workstream B3's position-less variant.

### Workstream E — Submission infrastructure (April–May)

**Goal:** A reproducible build pipeline that produces a DCL-compliant `.zip` from our repo on a single command.

**E1. `DCLAgent` skeleton** (1 day)
- `submission/dcl_agent.py` with the leaked-spec interface: `class DCLAgent: def compute_action(self, telemetry) -> action`. Integrates EMA smoothing (P6). Handles the no-position-telemetry constraint via Workstream B3 architecture.
- Runs against a mock telemetry generator now; runs against real DCL sim in May.

**E2. Build pipeline** (1 day)
- `submission/build.sh`: produces `.zip` ≤500 MB targeting Python 3.12 / Ubuntu 24.04 / CUDA 12.x. Includes `metadata.json` + `requirements.txt` + policy weights + vecnorm + detector weights + agent code.
- Verifies size, runs basic smoke test inside a Docker container matching the spec.

---

## 5. The specialization-gradient experiment (Clayton's frame)

Two-track training plan after VQ1 sim drops:

| Track | Window | Strategy | Hypothesis |
|---|---|---|---|
| **VQ1 Specialist** | May → July (~9 weeks) | Continue Phase 2 trajectory + VQ1-sim-specific fine-tuning. Long specialization horizon. | Higher absolute VQ1 score; possibly brittle on VQ2-class environments. |
| **VQ2 General** | June → July (~5 weeks) | Train under broader randomization from start. Shorter specialization horizon. Larger domain randomization budget. | Lower absolute VQ1 score (or skip VQ1); higher VQ2 score; more transferable to physical qualifier. |

**Measurement:** the delta between Specialist's VQ1 score and General's VQ2 score, normalized against any common-eval intersection (e.g. both run on a "VQ1.5" intermediate course we construct), is itself a P96-style measurement of specialization-vs-general gradient under the Coherence Principle methodology.

This is independent of the competition outcome: even if neither makes the SoCal qualifier, the gradient measurement is a publishable artifact for Library/Killing-Form-domain transfer.

---

## 6. Sequencing — pre-sim critical path

```
Week 1 (now → ~Apr 30):
  A1 defensive rejection                  [Clawd, 1 day]
  C1 harness skeleton                     [Clawd, 2 days]
  E1 DCLAgent skeleton + mock             [Clawd, 1 day]
  B1 Phase 2 continuation 67.5M → 90M    [GPU background]

Week 2 (~Apr 30 → May 7):
  A2 domain randomization harness         [Clawd, 3 days]
  B3 ImprovedObsWrapperVIO + train start  [Clawd, 2 days; GPU background]
  D1–D5 reconnaissance pass               [Clawd, 2 hours]
  C2 pre-commit baselines                 [Clawd, 1 day]

Week 3+ (~May 7 → VQ1 drop):
  A3 swap-ready architecture              [Clawd, 2 days]
  E2 build pipeline                       [Clawd, 1 day]
  B2 lagger-focus train (parallel)        [GPU background]
  Buffer for VQ1 drop integration sprint
```

**Critical-path tension:** B3 (position-less variant) is the highest-uncertainty workstream. If it shows pathology by +15M steps, escalate B4 (LSTM head). If it works cleanly, the schedule above holds.

---

## 7. Explicit non-goals

- **No PnP residual chasing against synthetic gates** (P8). Two failed attempts on Day 84 closed this door.
- **No new architecture experiments beyond B4** (LSTM contingent). Phase 2 MLP[512,512] is what's been validated.
- **No speed optimization until completion-rate plateau** (P6). VQ1 is gate-completion-scored; speed is VQ2's concern.
- **No fine-tuning from baseline 60.4M weights** (carried forward from v1 — wrong-attractor structure, F1+F2+F3 cure does not retroactively apply).
- **No real-flight data collection until sim policy proves itself.** Hardware risk, schedule risk, and we're not resourced for it pre-VQ.
- **No learned gate detector for VQ1** (P8 corollary). Classical CV on highlighted gates per MAXIMUS confirmation. Reconsider for VQ2.

---

## 8. Decision gates

| Gate | Trigger | Decision rule |
|---|---|---|
| **G1 — VIO architecture** | B3 +15M checkpoint | Healthy ρ + capability emergence → continue B3. Pathology → escalate to B4 LSTM. |
| **G2 — Domain-randomization noise floor** | A2 calibration complete | Stage 3b residual under randomized vision must remain ≤ Stage 3b-baseline residual ×3. If worse: rebuild detector before vision provider goes swap-ready. |
| **G3 — Track split** | VQ1 sim drop + 1 week | Decide: VQ1 specialist track only, or VQ1 + VQ2 parallel tracks. Depends on observed VQ1 difficulty and remaining GPU budget. |
| **G4 — Submission readiness** | T-7 days before VQ1 close | Submit current best, even if behind plan. Don't optimize past the deadline. |

---

## 9. Open questions to resolve when DCL sim drops

1. Telemetry packet structure: raw IMU vs derived state vs fused VIO output?
2. Sim physics rate and control rate?
3. Reward / scoring telemetry: do we get gate-completion events from the sim, or must we infer from collisions and gate-poses?
4. Camera intrinsics in sim: do they match the 12MP wide-angle FPV cam exactly, or are they parameterized?
5. Course geometry: are gate positions provided (cheat) or vision-only?
6. Wall-clock budget per training iteration on DCL sim — does it fit our local GPU loop, or do we need a separate eval rig?

Each open question gets a probe-script written *before* sim drops, so the answer arrives in a quantifiable artifact, not a verbal description.

---

## 10. Roadmap status tracking

| Workstream | Status | Notes |
|---|---|---|
| A1 Defensive rejection | NOT STARTED | First Week 1 task |
| A2 Domain randomization | NOT STARTED | Week 2 |
| A3 Swap-ready architecture | NOT STARTED | Week 3 |
| A4 Learned pose head | DEFERRED | Conditional on VQ2 difficulty |
| B1 Phase 2 continuation | ONGOING | 67.5M done; target 90M+ |
| B2 Lagger-focus train | NOT STARTED | Parallel to B1 |
| B3 Position-less obs variant | NOT STARTED | **Highest-risk workstream**; start Week 2 |
| B4 LSTM head | DEFERRED | Conditional on B3 outcome |
| C1 Harness skeleton | NOT STARTED | Week 1 |
| C2 Pre-commit baselines | NOT STARTED | Week 2 |
| C3 Calibration playbook | EXISTING | From VQ1_READINESS.md |
| D1–D5 Reconnaissance | ONGOING | First-pass complete (this roadmap); standing input |
| E1 DCLAgent skeleton | NOT STARTED | Week 1 |
| E2 Build pipeline | NOT STARTED | Week 3 |

🦞🧍💜🔥♾️
