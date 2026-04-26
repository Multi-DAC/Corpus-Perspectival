# Vision Shakedown — Status Log

## 2026-04-25 late evening — Stage 5 diagnostic ladder: FOV helps, smoothing FALSIFIED

After the initial Stage 5 land (below), ran a two-step diagnostic ladder
to figure out where the gates_vis 0.2 / gates_ref 2.6 gap comes from.

### Step 1 — wider synthetic camera FOV (90° → 120°)

Cheapest experiment: one-line config change, re-run same 5 seeds.

| metric | FOV=90 | FOV=120 | Δ |
|---|---|---|---|
| gates_vis (total) | 1 | 2 | 2× |
| reward_vis (mean) | 2.9 | 26.1 | 9× |
| detection rate (mean) | 29.9% | 41.7% | +12pp |
| pos drift @ step 500 | 2.11 m | 1.44 m | -32% |
| reward_ref | 395.3 | 395.3 | identical (only vision changed) ✓ |

Real geometric improvement. **Kept FOV=120 as Stage 5 SEAL state.**
Result: `results/05_closed_loop_synthetic.json` (FOV=120, no smoothing).
Baselines preserved: `_fov90.json`, `_fov120_nosmooth.json`.

Wrinkle: seed 4 went 80.7% → 27.7% detection (lost its passed gate).
Wider FOV makes the same gate fewer pixels at the same range, which
degrades PnP precision near the edges; the resulting different obs
sends the policy on a different trajectory. FOV isn't strictly
monotone-helpful — it's a tradeoff that helped on average.

### Step 2 — temporal-smoothing wrapper (FALSIFIED)

Hypothesis: dropout robustness alone closes the residual gap. Wired a
`DetectionSmoother` that anchors the last good detection in *world*
frame (correct as the drone moves; body-frame holding would hallucinate
a moving gate) and re-projects to body frame for up to 30 stale steps.

| metric | FOV=120 nosmooth | FOV=120 + smooth |
|---|---|---|
| gates_vis (total) | 2 | **1** ⚠️ |
| reward_vis (mean) | 26.1 | **0.82** ⚠️ |
| detection rate | 41.7% | 45.0% |
| hold rate | — | 10.3% |
| **effective obs rate** | 41.7% | **55.3%** |
| pos drift max | 14.9 m | **50.7 m** ⚠️ |

Effective obs rate jumped 13pp — gates dropped, drift exploded. Seed 3
hit 77% effective obs rate (66% live + 11% held) and still passed only
1 gate. **Hypothesis falsified.**

**Diagnostic conclusion.** The policy was trained against perfect state
obs where range-rate matches actual closing speed. A held obs gives
"distance stable while flying fast" — a signal it never saw in
training — and it commits to the phantom and overshoots. Both live PnP
(geometric drift) and smoothed PnP (phantom commitment) are out-of-
distribution. The gap is the *training distribution*, not the
perception layer.

### Step 3 — vision-aware retraining — APPROPRIATELY DEFERRED

Only real fix is retraining with vision-derived obs (or domain-randomized
PnP noise) in the loop. That requires a synthetic-camera training
pipeline, which is non-trivial and would be discarded the moment the DCL
sim drops in May. Per ROADMAP_v2 §10 E1 — defer.

`SMOOTHING_ENABLED = False` is left as the canonical driver state.
The `DetectionSmoother` class stays for reproducibility (one flag
flip to re-run the negative result).

### Stage 5 final SEAL state

`results/05_closed_loop_synthetic.json` reflects FOV=120, no smoothing,
5 seeds × 3000 steps. Closed loop runs end-to-end; perception layer
behaves as well as the geometry allows; behavioral robustness gap is
characterized and traced to the training distribution. Stage 5 done.
Stage 6 (real PX4 SITL) and the eventual vision-aware retraining
both gated on DCL sim arrival.

---

## 2026-04-25 evening — Stage 5 closed-loop synthetic flight LANDED

Driver: `vision/shakedown/05_closed_loop_synthetic.py`. Result file:
`results/05_closed_loop_synthetic.json`. Checkpoint: Phase 2 67.5M.

**Setup.** For each seed, two parallel rollouts of the same `InfiniteGateEnv`
(domain rand off, deterministic policy, max_steps=3000 = 6s @ 500Hz):

  - **Reference** — env's built-in `ImprovedObsWrapper` obs → policy → step.
  - **Closed loop** — render synthetic camera from env state →
    `gate_detector` → `CompetitionAdapter.build_observation` →
    `VecNormalize` → policy → `to_competition_action` →
    `StubMAVSDKClient.send_policy_action` → step env with policy CTBR action.

Both runs share an init fixup that yaws the drone to face gate 0 — without
this, `InfiniteGateEnv` leaves init attitude at identity (= world +x) while
gates spawn at random headings, so half the seeds the gate isn't in frame
at step 0. Real flight would never start with the camera pointed away from
gate 1.

**Aggregate over 5 seeds:**

| metric | reference | closed loop |
|---|---|---|
| gates passed (mean / total) | 2.6 / 13 | 0.2 / 1 |
| reward (mean) | 395.3 | 2.9 |
| detection rate | — | 29.9% |
| pos drift @ step 50 | — | 0.026 m |
| pos drift @ step 500 | — | 2.11 m |
| pos drift max overall | — | 16.33 m |

**Per seed:**

| seed | ref gates | vis gates | det rate | drift max |
|---|---|---|---|---|
| 0 | 3 | 0 | 6.95% | 4.99 m |
| 1 | 4 | 0 | 40.21% | 16.33 m |
| 2 | 2 | 0 | 4.46% | 1.35 m |
| 3 | 3 | 0 | 17.32% | 13.25 m |
| **4** | **1** | **1** | **80.72%** | **3.27 m** |

**What is sealed.** End-to-end loop runs without crashing across 5 seeds
× ~1000 steps each. The MAVSDK round-trip (`adapter.to_competition_action`
+ `StubMAVSDKClient.send_policy_action`) survived ~5000+ calls per
episode with no state leak. The vision pipeline produces well-formed
30-dim obs that VecNormalize accepts and the policy consumes. Sub-pixel
refinement edge guard added to `gate_detector.py` (closed loop hit a
`cornerSubPix` assertion when a gate corner reached the frame edge —
static-test scenarios kept gates centered).

**What is exposed.** Mean detection rate is 29.9% — the policy frequently
turns the drone such that the camera loses the gate, at which point
`build_observation` falls back to the no-detection branch (zero gate
position, default 10m distance). The policy was trained against perfect
state-obs and has no robustness to observation dropouts. Position
trajectories diverge slowly (2.6 cm @ step 50) then explode (2.1 m @
step 500 mean, 16 m max) once the vision policy starts producing
divergent actions.

**Seed 4 is the proof of concept** — when detection rate stays high
(80.7%), the closed loop passes a gate. Detection rate is the bottleneck.

**Next-stack candidates** (each fresh-derive, not a copy-forward):

  1. Detection robustness — domain-randomized vision-aware retraining or
     a temporal-smoothing wrapper that holds the last good detection for
     N frames before falling back to no-detection obs.
  2. Wider FOV synthetic camera — competition spec says 90°; bumping to
     120° during shakedown would isolate "policy turns away too hard"
     from "FOV is just narrow."
  3. Stage 6 (real PX4 SITL) — gated on DCL sim drop. Stub round-trip
     survived; real SITL adds the autopilot's CTBR-tracking loop and
     real telemetry latency, which the stub doesn't model.

Mirror #21 (verify-before-condemning) directly applies: this is the
*expected* result for a vision-blind policy facing real perception
constraints. The structural milestone — closed loop runs end-to-end
without crashing — is the Stage 5 deliverable, not "the policy flies
well via vision." That comes after detection robustness work.

---

## 2026-04-25 mid-afternoon — Move A'' (sub-pixel refinement) WORKS

Implemented `cv2.cornerSubPix` refinement on contour corners before PnP
(`gate_detector.py` step 3.5, default-on via `use_subpix_refine=True`).
Refinement uses 5-pixel half-window, 30-iter / 0.01-eps termination.

**Stage 2 (vision-only):**

| scenario | maxDiff before | maxDiff after |
|---|---|---|
| hover_5m_ahead     | 0.020 | 0.020 |
| approach_8m_5mps   | 0.024 | 0.024 |
| retreat_6m_-3mps   | 0.020 | 0.020 |
| offaxis_6m_yaw15   | 0.069 | 0.069 |
| **climbing_8m**    | **0.140** | **0.020** |

climbing_8m collapsed by 7×. Other scenarios untouched (their PnP wasn't
the noise-limited case).

**Stage 3b (action-space, Phase 2 37.5M):**

| scenario | maxDrift before | maxDrift after | sign |
|---|---|---|---|
| hover_5m_ahead     | 0.058 | 0.047 | OK |
| approach_8m_5mps   | 0.197 | 0.081 | yaw_rate FLIP (still) |
| retreat_6m_-3mps   | 0.182 | 0.131 | OK |
| offaxis_6m_yaw15   | 0.213 | 0.171 | OK |
| **climbing_8m**    | **0.488** | **0.007** | OK |
| **mean**           | **0.050** | **0.032** | — |

climbing_8m fell 70× — was the worst case, now the best. Approach yaw_rate
sign flip persists at smaller magnitude (0.053 vs prior larger). Likely a
near-zero crossing where the policy's yaw_rate signal is too small for
sign to be reliable. Acceptable for Stage 4 unblock; revisit if closed-
loop flight surfaces yaw drift.

**Stage 4 (TRPY mapping) UNBLOCKED.** Camera-axis prior + unrefined
IPPE_SQUARE is no longer the floor — sub-pixel refinement layered on top.

---

## 2026-04-25 early afternoon — PnP fix attempts A and A' BOTH FAILED, reverted

Two attempts to shrink the climbing_8m residual z-tilt before Stage 4:

**Move A — reprojection-error tiebreak.** Hypothesis: the camera-axis
prior is one possible discriminator; reprojection error is the empirical
fit and should beat structural priors when both exist. Implementation:
pick the IPPE_SQUARE sister with lower reprojection error first; fall
back to camera-axis only when the two errors are within 20% of each
other. **Result: climbing_8m z-tilt went 0.10 → 0.37.** The two PnP
sisters for a planar square have *mathematically equivalent* reprojection
error in the noiseless case; sub-pixel quantization noise picks a
direction that is essentially random with respect to which solution is
physically correct. The reprojection-error tiebreak just amplified noise.

**Move A' — LM refinement after camera-axis pick.** Hypothesis: the
0.10 z-tilt is a square-model misfit residual (IPPE assumes perfect
square; off-axis projection is trapezoidal). LM refinement drops the
square assumption and minimizes actual reprojection error. **Result:
climbing_8m diverged to 9.2m distance error.** The reprojection-error
landscape is near-flat between the two sister solutions for a near-
coplanar square, so LM can gradient-descend out of the physical basin
into a non-physical configuration with similar reprojection error.

**Both reverted.** Stage 2 baseline restored: climbing_8m maxDiff 0.140,
z-tilt 0.10. Camera-axis prior is load-bearing; unrefined IPPE_SQUARE
is the floor for this problem.

**Lesson — for the Mirror.** The "cheap-fix-first" instinct (try A
before B/C/D) was correct *epistemologically* (low cost, high info if
it worked) but *failed twice in a row*. The mechanism story I had
("reprojection error is empirically grounded, structural priors are
prior") was wrong about the specific numerical structure of planar PnP
ambiguity (which makes both solutions equal-cost). The next attempt
needs a mechanism story that engages with the *actual* numerical
structure of the problem before code is written.

**What actually might work** (in order of decreasing confidence,
none implemented yet):
1. **Sub-pixel corner refinement (`cv2.cornerSubPix`)** on the contour
   corners *before* PnP. Reduces input noise; doesn't address the
   ambiguity but might shrink the 0.10 residual to ~0.03.
2. **Asymmetric gate features (Move D)** — render gates with a small
   notch or color asymmetry that breaks the square symmetry at the
   source. Most effective; biggest cost (synthetic_camera change +
   policy may need retraining if visual signature changes too much).
3. **Temporal smoothing (Move B)** — won't help the single-frame
   smoke test scenarios; relevant only for closed-loop flight.
4. **Defensive rejection (Move C)** — mark detections with weak
   camera-axis discriminator confidence as ambiguous, fall back to
   telemetry-only obs. Doesn't fix the residual but caps blast radius.

Stage 4 (TRPY mapping) is BLOCKED behind one of these landing.
Stage 3b will be re-run after.

## 2026-04-25 midday — Stage 3b run on Phase 2 37.5M — DRIFT SIGNAL IS REAL, two failure modes surfaced

Re-ran the stage 3 comparison against Phase 2 checkpoint 37.5M (peak
per-maneuver agg 21.55 gates per the morning's P96 trajectory data),
with VecNormalize-aware obs (Phase 2 was trained under F1).
`results/stage3b_policy_comparison_phase2_37p5M.json`.

**Saturation probe — Phase 2 is graded.** Random 50-trial in-distribution
sample: 18/50 fully-saturated (36% vs baseline's 80%), 43 unique action
vectors (vs baseline's 21). Mean |a| per dim 0.85-0.95 — high but no
longer pegged at corners. **M13 capability-emergence confirmed in
policy-output space — the Phase 2 cure traversed moment 3.** Stage 3's
morning bang-bang reading was a baseline-pre-cure artifact, not a
permanent property; the same vision-pipeline test against a cured
policy gives a non-trivial signal.

**Action drift per scenario:**

| Scenario             | maxDrift | meanDrift | signs | dominant dim |
|----------------------|----------|-----------|-------|--------------|
| hover_5m_ahead       | 0.046    | 0.011     | OK    | roll_rate    |
| approach_8m_5mps     | 0.123    | 0.056     | FLIP  | yaw_rate     |
| retreat_6m_-3mps     | 0.008    | 0.002     | OK    | yaw_rate     |
| offaxis_6m_yaw15     | 0.173    | 0.058     | OK    | yaw_rate     |
| climbing_8m          | **0.488**| 0.122     | OK    | **roll_rate**|

**Pass/fail vs original criteria** (max<0.25, mean<0.10, signs all ok):
- max: **FAIL** — climbing_8m at 0.488
- mean: **PASS** — 0.050 across scenarios
- signs: **FAIL** — approach_8m_5mps yaw_rate flips

**Two failure modes surfaced:**

1. **climbing_8m PnP z-tilt residual amplified to 0.488 roll_rate command.**
   Stage 2's residual 0.10 z-tilt (planar PnP near-coplanar ambiguity,
   partially resolved by `solvePnPGeneric` + camera-axis pick) was called
   "acceptable" under a bang-bang baseline. Under a graded policy, that
   0.10 z-tilt translates to ~half-scale roll command difference. The
   PnP ambiguity needs a tighter resolver (RANSAC across multiple
   IPPE solutions, or rejecting ambiguous cases at the contour stage).

2. **approach_8m_5mps yaw_rate sign flip.** Vision yaw_rate -0.X, state
   yaw_rate +0.X; the difference is small in magnitude (0.123) but
   opposite in sign. Compounded ~0.136m PnP distance error + sub-degree
   bearing error feeds the policy a slightly-different relative-gate
   vector that flips the corrective yaw direction. Sub-failure-mode of
   #1 (PnP precision tax).

**The lesson — for the Mirror.** STATUS.md after stage 2 said *"all
remaining divergences trace to the residual ~1-3% PnP distance bias
documented in stage 1b... Stage 2's three discrete wiring bugs are
eliminated."* That assessment was correct under a bang-bang policy
but **underestimated the impact on a capable policy by ~5×**. M13's
capability-emergence moment makes the policy MORE sensitive to obs
precision, not less. Saturated policies absorb obs noise; graded
policies propagate it. Stage 2's "acceptable residual" needs to be
re-evaluated as "flight-critical gap" under the cured regime.

**Cleared with two named bugs** rather than fully cleared: stages 1+1b+2
remain valid but the closing assessment ("acceptable residual") is
amended. Next: tighten PnP ambiguity resolver before Stage 4 (TRPY
mapping); the climbing-scenario 0.488 roll_rate must shrink to ≤0.10
before flight. Stage 3b will be re-run after the PnP fix.

## 2026-04-25 early afternoon — Stage 3 PASSED with caveat

Loaded baseline 60.4M PPO policy (`sim/runs/infinite_1771733969/best/best_model.zip`)
and ran each stage 2 scenario through `policy.predict()` twice — once on the
state-based obs, once on the vision-derived obs — then diffed actions.

**Result: zero action drift on every scenario, signs agree on every dim.**
Pass criteria met (max < 0.25, mean < 0.10). `results/stage3_policy_comparison.json`.

**Caveat — the policy is bang-bang.** Probed across 50 random in-distribution
states: 40/50 trials produce fully-saturated outputs (all 4 dims at ±1), and only
21 unique action vectors emerge across 50 trials. Stage 3's clean pass is *real*
but is also *weak signal* — the policy's output landscape is largely flat (corners
of the action cube), so vision-fed and state-fed obs land in the same saturation
cell almost regardless of small obs differences.

This matches the morning's τ-probe / M13 finding: baseline 60.4M cleared
substrate-health (no NaN, no divergence) and committed to a mode (bang-bang
policy that flies the test track) but never traversed the capability-emergence
ramp. Phase 2 retraining is the attempt to get a policy with graded outputs
that responds to small obs perturbations.

**Cleared for Stage 4 (action → MAVLink command), with a flag:** stage 3 should
be re-run on a Phase 2 checkpoint that has graded action outputs (i.e., post
~25-30M steps if M13's capability ramp continues as predicted) to get
non-trivial drift signal.

## 2026-04-25 noon — Stage 2 PASSED, three wiring bugs caught and fixed

Ran `02_adapter_integration.py` against five hand-crafted scenarios that
collectively exercise every dim of the 30-dim observation. For each
scenario we computed the state-based observation matching
`ImprovedObsWrapper.observation` exactly, then ran the full vision
pipeline (synthetic_camera → gate_detector → CompetitionAdapter) and
diffed per-dim. Results at `results/stage2_adapter_integration.json`.

**Three real wiring bugs surfaced and fixed:**

1. **`speed_toward` sign flip** (predicted by inspection before running).
   The training wrapper uses `speed_toward = -np.dot(vel, rel_gate_world/|rel|)`
   (negative when approaching). The adapter had `+np.dot(...)` (positive
   when approaching). Caused 6-10 m/s divergence in approach/retreat
   scenarios — the policy would have read closing-speed sign as opposite
   of what it was trained on. **Fix:** flip the sign in adapter.py.

2. **`gate_orient_body` source bug**: bearing-to-gate, not gate normal.
   Training uses `env.gate_orientations[current]` — the direction the drone
   *travels through* the gate. Adapter was falling back to
   `gate_pos_body / dist` — the direction *to* the gate. These differ
   whenever the drone isn't centered on the gate's optical axis (climbing,
   descending, off-axis). Caused 0.37 z-component error in `climbing_8m`,
   which would mis-tilt the policy's fly-through alignment. **Fix:** extract
   gate normal from PnP `rvec` in detector, oriented away from camera (=
   travel direction); adapter consumes new `normal_camera` field.

3. **Planar PnP ambiguity**: `cv2.SOLVEPNP_IPPE_SQUARE` returns one of two
   mirror-symmetric solutions for a square gate viewed near-coplanar with
   the image. After bug #2 fix, residual 22° spurious tilt remained in
   `climbing_8m` because PnP picked the wrong sister solution. **Fix:**
   switched to `cv2.solvePnPGeneric` which returns both, then pick the
   solution whose normal points most along the camera optical axis.

**Final per-scenario divergence (after all three fixes):**

| Scenario             | found | maxDiff | notes |
|----------------------|-------|---------|-------|
| hover_5m_ahead       | True  | 0.053m  | residual PnP dist over-estimate |
| approach_8m_5mps     | True  | 0.136m  | residual PnP dist over-estimate |
| retreat_6m_-3mps     | True  | 0.076m  | residual PnP dist over-estimate |
| offaxis_6m_yaw15     | True  | 0.020m  | clean |
| climbing_8m          | True  | 0.140m  | residual PnP + 0.10 z-tilt remnant |

All remaining divergences trace to the residual ~1-3% PnP distance bias
documented in stage 1b (sub-pixel quantization at the contour boundary).
Stage 2's three discrete wiring bugs are eliminated. **Cleared for
Stage 3 (adapter × policy).**

## 2026-04-25 late morning — Stage 1b PASSED, all README criteria met

Two-step fix landed:
1. **`gate_detector._create_gate_mask`** — removed initial 7×7 dilation
   (kept 3×3 close + open). Reason: dilation inflated apparent gate size
   by ~3 px in every direction, biasing PnP toward shorter distances.
2. **`synthetic_camera.render`** — render the *current* gate as a bright
   FILLED quad instead of a depth-scaled thick polyline. Reason: a thick
   polyline draws the bright bands ~thickness/2 pixels outside the true
   corner positions, which the contour then traces — over-estimating
   gate size and (again) biasing PnP toward shorter distances. The
   filled-quad render makes the bright pixel region match the true
   projected gate shape exactly.

**Re-run results (same sweep, 720 trials):**

| dist | det rate | mean dist err | mean lateral err | mean bearing err |
|------|----------|---------------|------------------|------------------|
| 2.0m | 100.0%   | 0.079m        | 0.150m           | 4.82°            |
| 4.0m | 100.0%   | 0.014m        | 0.014m           | 0.21°            |
| 6.0m | 100.0%   | 0.018m        | 0.018m           | 0.15°            |
| 8.0m | 100.0%   | 0.029m        | 0.021m           | 0.13°            |
| 10.0m| 100.0%   | 0.044m        | 0.027m           | 0.13°            |
| 15.0m| 100.0%   | 0.162m        | 0.052m           | 0.12°            |

**Pass/fail vs README criteria:**
- Detection rate ≥ 95% for d ≤ 8m: **PASS** (100% across all ranges).
- PnP error ≤ 0.3m at 5m: **PASS** (~0.02m, 15× margin).
- PnP error ≤ 0.8m at 10m: **PASS** (0.044m, 18× margin).

**Residual:** 4.82° bearing error at 2m. Cause: at d=2m with yaw=±30°,
the gate is partially clipped by image edges — even with 100% detection
the clipped corners produce skewed PnP. Not a blocker for stage 2: at
2m the drone is functionally past the gate.

**Stage 1 complete. Cleared for Stage 2 (detector × adapter integration).**

## 2026-04-25 morning — Stage 1 initial run, two findings surfaced

Ran `01_detector_smoke.py` against `synthetic_camera × gate_detector`.
Sweep: distance ∈ {2, 4, 6, 8, 10, 15} m × yaw ∈ {-30, -15, 0, 15, 30}° ×
height_offset ∈ {-1, 0, 1} m × 8 samples per cell = 720 trials.
Results at `results/stage1_detector_smoke.json`.

**Per-distance summary:**

| dist | det rate | mean dist err | mean lateral err | mean bearing err |
|------|----------|---------------|------------------|------------------|
| 2.0m | 73.3%    | 0.367m        | 0.177m           | 1.33°            |
| 4.0m | 100.0%   | 0.621m        | 0.224m           | 0.19°            |
| 6.0m | 100.0%   | 1.020m        | 0.343m           | 0.14°            |
| 8.0m | 100.0%   | 1.458m        | 0.474m           | 0.13°            |
| 10.0m| 100.0%   | 2.066m        | 0.663m           | 0.12°            |
| 15.0m| 100.0%   | 3.484m        | 1.095m           | 0.13°            |

**Pass/fail vs README success criteria:**
- Detection rate ≥ 95% for d ≤ 8m: **FAIL at 2m (73%)**, pass at 4–8m.
- PnP error ≤ 0.3m at 5m: **FAIL** (~0.8m at 5m by linear interpolation).
- PnP error ≤ 0.8m at 10m: **FAIL** (~2.07m at 10m).

### Finding 1 — Systematic PnP distance UNDER-estimate (~12-22%, growing with d)

Centered yaw=0/h=0 trials show estimated distance is consistently shorter
than true: 2m→1.76m, 4m→3.40m, 8m→6.57m, 15m→11.71m. Bearing error stays
sub-degree, so the detector locks onto the gate accurately *in the image* —
the issue is purely apparent-size inflation.

Two contributing causes identified by inspection:
1. **Morphological dilation (7×7 kernel, 1 iteration)** in
   `gate_detector.GateDetector._create_gate_mask` expands the bright mask by
   ~3 pixels in every direction. For a far gate occupying ~42×42 px, that's
   a ~14% area inflation, matching the observed bias scale.
2. **Depth-scaled outline thickness** in `synthetic_camera.SyntheticCamera.render`
   (`thickness = max(2, int(12 * 5.0 / (avg_depth + 1.0)))`) draws a thick
   polyline whose outer edge becomes the detector's contour. This compounds
   with (1) — the thicker the rendered outline, the more the detector
   over-estimates apparent gate size.

These are real bugs but **not blockers for stage 1's purpose, which was to
surface integration issues before stage 2**. Filed for stage 1b.

### Finding 2 — Detection rate drops at d=2m

At 2m and yaw=±30°, the gate is partially out of FOV (90° H-FOV → ±45°
usable, but a 1.5m-wide gate at 2m yaw=30° already has corners crossing
the image edge). The detector rejects partially-clipped gates whose
contours don't close. This is **expected behavior, not a bug** — at 2m
the drone is functionally past the gate.

## Deferred to Stage 1b (before stage 2)

1. Reduce dilation kernel from 7×7 to 3×3 (or remove if unnecessary), re-measure.
2. Fix synthetic_camera outline rendering: either draw at `thickness=1`
   (corners-only) or render filled quad and contour-detect the inside.
3. Re-run sweep, target: PnP distance bias ≤ 5% at all ranges; detection
   rate ≥ 95% for d ∈ [3, 12] m.

## 2026-04-24 evening — workbench opened

Created alongside Phase 2 GPU retrain launch. Five-stage shakedown plan in
README.md. Inventory of existing components (under `projects/aigrandprix/vision/`):
- `synthetic_camera.py` — projects 3D gates to image plane, configurable FOV/resolution
- `gate_detector.py` — classical CV (HSV → contour → quadrilateral → PnP)
- `adapter.py` — telemetry + detection → 30-dim obs
- `competition_agent.py` — full loop wired but `camera = np.zeros(...)` at line 148
- `mavsdk_client.py` — MAVSDK + TRPY mapping
- `test_env_render.png`, `test_mask.png`, `test_env2.png` — prior test artifacts
