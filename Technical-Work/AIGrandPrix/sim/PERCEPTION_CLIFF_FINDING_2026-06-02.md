# The Perception Cliff — Anakin's bottleneck is visibility, not noise (2026-06-02)

**One-line:** Distilling the 80M privileged Anakin into a perception-grade vision student failed
(BC→DAgger floored at 0.05 gates/ep, *below* the 0.23 W5 RL baseline). Reverse-engineering *why*
isolated the entire bottleneck to a single perception channel — **detection (field-of-view + range
limit)** — and showed it is a *visibility/persistence* problem, not a *signal-quality* problem. The
candidate fix is a state estimator that dead-reckons out-of-frame gates by ego-motion, with **frozen
Anakin** — no better detector, no policy retraining, no UE5 required for the core problem.

---

## 1. The distillation null (and why it's not a setback)

Teacher = old 80M pilot (`runs/infinite_1771556763/checkpoints/ppo_infinite_80000000_steps.zip`),
eval'd RAW (no VecNormalize), privileged obs, **10.9 gates/ep** (robust, n=50).

Pipeline built end-to-end (all reusable):
- `distill_collect.py` — dual-view harness: teacher decides from privileged obs; a side
  `PerceptionObsWrapper` over the SAME base env logs the perception view → aligned
  `(perception_obs, teacher_action)` pairs. Validated: teacher flies the harness at 10.36 gates/ep.
- `bc_train.py` — 313,671-pair BC seed → SB3 PPO student (eval-compatible with `metrics_anakin.py`).
- `dagger.py` — student-drives / teacher-labels rollout, 5 iters × 80k pairs.

**Result:** BC = 0.00 gates/ep, DAgger plateaued 0.05, train_mse *rose* (0.306→0.328) as it
aggregated. The smoking gun: even on **teacher-distribution** states, BC could not fit below ~0.29
MSE. That is not distribution-shift (which DAgger fixes) — it is an **information floor**.

**Decisive comparison:** teacher = 512×512 MLP on *privileged* obs → 10.9. Same architecture on
*perception* obs → 0.05. Only the observation changed. → bottleneck is **observability**, full stop.

## 2. The noise sweep — it's a cliff, not a slope

`sweep_noise.py`: feed frozen Anakin gate-perception at increasing noise (0 = privileged, 1.0 =
W3-calibrated detector). 15k-step episodes (≈half the full-length gate counts).

| scale | 0.00 | 0.25 | 0.50 | **1.00 (W3)** | 1.50 |
|---|---|---|---|---|---|
| gates/ep | 5.25 | 4.83 | 4.25 | **0.00** | 0.17 |

Anakin holds 80%+ of clean up to **0.5× W3**, then falls off a cliff. The current detector (1.0×)
sits *just past* the edge. This explains W5 (RL trained at full W3 = the cliff bottom → 0.23) and the
distillation null (imitating in the regime where the teacher itself scores 0).

## 3. The channel sweep — ONE channel is the whole cliff

`sweep_channels.py`: corrupt one channel to full W3, others clean.

| channel | clean | range | range 2× | bearing | dropout | dropout 2× | latency | **detection** | all-W3 |
|---|---|---|---|---|---|---|---|---|---|
| gates/ep | 4.75 | 4.83 | 4.00 | 5.08 | 4.83 | 4.75 | 4.67 | **0.08** | 0.17 |

**Noise of any kind barely dents Anakin, even at 2×. The entire cliff is `detection` — the FoV cone
+ range limit.** When the gate leaves the ~90° camera cone (or passes ~28 m), the drone doesn't see
it and flies blind. Takeoff stayed 8–12/12 even at collapse → controls + ego-state are intact; it is
*purely gate-finding* that dies.

**Reframe:** it is not a signal-quality problem. The gate isn't faint — it's *not in the picture*.
Anakin was trained on omniscient privileged state (knows gates behind it); a forward camera breaks
that assumption the moment it passes a gate and turns toward the next.

### Implication for sim-frames vs UE5
UE5's strength is faint/occluded/cluttered gate *appearance* (detector robustness). But detector
*accuracy* is not the binding constraint — *visibility/persistence* is. So UE5 drops in priority for
the core problem (still the right finale tool for real-camera robustness; not the first lever).

## 4. The fix under test — dead-reckon the blind window

The drone knows its own velocity + attitude *exactly* (telemetry). A static gate's relative position
evolves as `rel(t+1) = rel(t) − velocity·dt`. So instead of holding the **stale** last-known vector
(stock `PerceptionObsWrapper`), **propagate** it by ego-motion through the blind window — the minimal
visual-inertial-odometry move, needing no position telemetry.

- `perception_deadreckon.py` — `DeadReckonPerceptionObsWrapper`; only change is the not-detected
  branch: `est = prev − velocity·dt` instead of `est = prev`.
- `sweep_deadreckon.py` — frozen Anakin, stock vs dead-reckon × {clean, detection, all_W3}.

**Prediction (medium-high):** recovers Anakin from 0.08 toward clean (~4.75) under `detection`.
Residual risk: cannot reckon a *never-seen* next gate (`prev=None`) — a known subtlety is that at a
gate-pass the new current gate may never have been seen, so a *partial* recovery would point to a
"never-seen-next-gate" residual (fix: hand off the look-ahead estimate `_last_next → _last_cur` at
the index transition, and/or FoV-aware flight).

### The L13 lens (basement bridge — predicts the failure mode)

Checking `palace/basement` before claiming novelty surfaced **L13 — Signal Provenance Erasure
(Phantom-Commitment Overshoot)**, whose instance #1 is literally *"Kalman/IMU drift under sensor
dropout, AIGP world-anchored smoothing"* — the prior AIGP event where smoothing made things **25×
worse**. L13's claim: failures occur when a consumer commits to an extrapolated signal (σ_ext) as if
it were live (σ_live) because no **provenance tag** distinguishes them.

Dead-reckoning is exactly an σ_ext generator, and **frozen Anakin's 30-dim obs has no provenance/
staleness channel** — it cannot tell a reckoned gate from a live one. So L13 sharpens the prediction:
dead-reckon helps **only while the reckoning stays accurate** (short blind windows; sim velocity is
exact). If blind windows are long or it reckons a no-longer-current gate, Anakin commits hard to a
confidently-wrong gate — the 25×-worse mechanism.

This makes the experiment a **controlled test of L13**: stock (σ_live only, goes blind) vs dead-reckon
(σ_live + *untagged* σ_ext). A *positive* result refines L13 — "σ_ext is not inherently harmful;
accurate σ_ext through short gaps is a feature, and the provenance tag matters precisely when σ_ext
*degrades*" — i.e. the prevention recipe should be **staleness-gated**, not blanket-distrust. A
*negative/partial* result confirms L13 cleanly and points to adding a staleness channel + retraining.

### RESULT — dead-reckoning FALSIFIED (high-confidence)

| config | stock (hold-stale) | dead-reckon | recovery of gap to clean |
|---|---|---|---|
| clean | 4.75 | 4.42 | (sanity — both fly) |
| detection | 0.17 | 0.25 | **2%** |
| all_W3 | 0.00 | 0.17 | **4%** |

Prediction (recover toward ~4.75) **FALSIFIED.** Dead-reckon barely moved the needle — and
crucially it did NOT *hurt* either (no 25×-worse). That "no help, no harm" signature is the tell.

**EXTRACT_INSIGHT — the bottleneck is signal ACQUISITION, not persistence.** Dead-reckoning can only
propagate a gate that was *seen at least once* (`prev != None`). The result says the gates that kill
Anakin are **never-seen**: the next gate is out of range/cone and has *never been detected*, so there
is nothing to extrapolate from. Two compounding causes:
1. **Never-seen gates** — the look-ahead gate has heavy dropout and is "usually not in view"; the
   next gate is often beyond the 28 m range limit until you're nearly on it.
2. **Gate-index handoff** — when Anakin passes gate N, `_last_cur` still holds gate N (now *behind*
   you); reckoning propagates the *wrong* (passed) gate until N+1 is freshly detected. (Fixable by
   `_last_next → _last_cur` at the pass — but only helps if N+1 was ever seen, see cause 1.)

**This is NOT the L13 failure I expected.** L13 is *committing to stale σ_ext as σ_live*. Here the
problem is upstream of L13: **σ_ext can't even be formed because there's no σ_live to extrapolate
from.** Signal *absence*, not provenance-erasure. (L13's staleness-gating is therefore not the fix.)

**Course-correction — the "[estimator] → frozen Anakin" architecture is INSUFFICIENT.** You cannot
bolt perception onto omniscient-Anakin: it assumes the gate is always known, and when the gate is
never in frame, no estimator can fabricate it. The policy *itself* must become FoV-aware —
(a) handle "no gate visible" gracefully (search / hold heading), and (b) fly gaze-aware lines that
bring the next gate into the cone. **Policy retraining is necessary, not optional** — but now aimed
correctly: not at denoising, but at *flying to acquire and keep the target in view*. This re-elevates
an FoV-constrained policy trained with privileged Anakin as critic/guide (asymmetric actor-critic),
and/or a recurrent policy with a search behavior.

### Confirmatory probe — it's a CAMERA-AXIS artifact (the drive's breakthrough)

`diag_visibility.py`: on Anakin's ideal line, the current gate is in frame **0.1% of steps**, **96%
of gates NEVER seen**. Then `drone_env_v2.py:128` — `thrust_body = [0,0,total_thrust/mass]` — so
**body-z is the UP/thrust axis**, yet the perception FoV cone is built around
`forward_world = quat_rotate(q,[0,0,1])` = body-z. **The virtual camera points up the thrust axis at
the sky**, not forward like a real FPV cam (forward + ~20° tilt, per VADR / `adapter.py`).

`diag_camera_axis.py` (frozen Anakin, ideal line, candidate body-fixed camera axes):

| camera axis | in-frame % | gates seen ≥1× |
|---|---|---|
| z_up (current) | 0.2% | 4% |
| −x_fwd | 33.0% | **96%** |
| y_fwd | 37.1% | 92% |
| −x + 20° tilt | 29.5% | ~100% |

Velocity-alignment: body-x 0.67 > body-y 0.52 > body-z 0.27 → flight-forward ≈ body-x hemisphere
(gates in −x/+y). **Correcting the camera axis raises gate visibility 0.2%→~33% and gates-seen
4%→96%.** The detection cliff is largely a camera-model artifact.

**Synthesis:** with a correct forward camera, gates are *seen* (acquisition solved), and the residual
out-of-frame gaps become *seen-then-lost* — which dead-reckoning CAN bridge. So **corrected-camera +
dead-reckon** is the candidate that could let frozen Anakin fly VQ1. (Exact production camera axis
should be pinned to the VADR spec + `adapter.py` `_cam_to_body_with_tilt`; the empirical −x/−x+tilt
winner is used here to *test* whether corrected geometry unblocks perception.)

### CONFIRMED — corrected camera + dead-reckon recovers Anakin (frozen, no retraining)

`sweep_corrected_camera.py` (frozen Anakin, realistic all-W3 detector):

| config | gates/ep | >=1% | takeoff |
|---|---|---|---|
| clean ceiling | 4.83 | 83 | 12/12 |
| body-z (broken) / hold | 0.08 | 8 | 8/12 |
| body-z / dead-reckon | 0.17 | 17 | 9/12 |
| **−x+tilt cam / hold** | **0.67** | 42 | 12/12 |
| **−x+tilt cam / dead-reckon** | **2.92** | 83 | 12/12 |
| −x_fwd / dead-reckon | 2.92 | 75 | 12/12 |
| y_fwd / dead-reckon | 2.42 | 92 | 12/12 |

**The full causal chain is now closed and validated:**
1. Noise isn't the bottleneck (channel sweep).
2. The FoV cone was around body-z = the thrust/UP axis → camera aimed at the sky (root cause).
3. Forward camera → gates visible 96% (acquisition solved): 0.08 → **0.67** (camera fix *alone*, 8×).
4. With gates now *seen*, blind windows are seen-then-lost → dead-reckon bridges them: 0.67 → **2.92**
   (camera + persistence, 36× baseline, **60% of the clean ceiling**, frozen Anakin, zero retraining).

Dead-reckon went from useless (never-seen gates) to worth +2.25 gates/ep — exactly because the camera
fix turned never-seen into seen-then-lost. **Robust to the exact forward axis** (−x, −x+tilt, y all
give 2.4–2.9) → not a knife-edge on getting the direction perfect.

**vs prior baselines:** W5 RL-on-perception 0.23; distillation floor 0.05. This is ~13× and ~58×.

### Camera-axis verification vs deploy adapter (2026-06-02, Clayton-requested)

`vision/adapter.py::_cam_to_body_with_tilt` documents the real geometry: camera frame (x=right,
y=down, z=forward); body frame (x=forward, y=left, z=up); 20° tilt maps camera-forward →
body (0.940, 0, 0.342). **So the DEPLOY adapter models the camera correctly (forward + 20° up).** The
FoV bug is **only in the training/eval sim model** `perception_obs.py` (cone around body-z = up).
Good news: the *real* detector sees forward; only our *simulated* detector threw gates away.

**But two wrinkles surfaced, and they matter:**
1. **Sim vs adapter body-frame convention mismatch.** Empirically (frozen Anakin, seed 7): mean
   body-frame velocity ≈ (−0.55, +0.40, +0.20); mean body-frame gate-direction ≈ (−0.19, +0.32,
   −0.04). The sim's flight/gate "forward" is a **−x/+y diagonal**, NOT the adapter's +x-forward. A
   sim-trained policy could hit a sign/orientation error at the real adapter — **reconcile before W6
   deploy.**
2. **Anakin crabs (flies non-nose-forward).** Because it's omniscient it never had to point at gates;
   its body-relative gate direction is off-axis and inconsistent. So **no fixed body-mounted camera
   axis sees gates consistently** — which is *why* the corrected-camera frozen-Anakin tops out at 2.92
   (not clean 4.83): the camera intermittently points away when Anakin crabs. The wide 90° cone +
   dead-reckon cover most of it, but the residual gap is **attitude/gaze**, not detection.

**Refined conclusion:** corrected camera geometry is necessary and gets 60% of the way with a frozen
omniscient pilot. Closing the rest requires a **gaze-aware policy that flies nose-toward-gates** (so a
body-mounted forward camera keeps the target in frame) — the FoV-aware retrain, now correctly aimed.

**Nose-axis honesty check (deploy convention, `nose_axis_test.py`):** frozen Anakin, all-W3,
dead-reckon — +x_fwd (deploy nose, no tilt) **2.25**; +x+20°tilt (deploy spec) **1.42**;
−x+tilt (non-deployable mount) 2.75. So the deployable nose camera gives ~2.25 (≈10× W5's 0.23) —
the crabbing cost is small, NOT the near-zero I feared (prediction partially falsified). **Actionable:
the 20° up-tilt HURTS frozen Anakin (1.42 vs 2.25)** — Anakin doesn't pitch forward enough for an
up-tilted cone to land on level gates. A gaze-aware retrain (flies faster/more-pitched) should reclaim
the tilt, but the camera-tilt × flight-attitude interaction is a real deploy-mount consideration.
Deployable frozen baseline for the retrain: **~1.4–2.25 gates/ep**; target → toward clean 4.83.

### Open / next (W6 territory)
1. **Pin the exact production camera axis** to VADR spec + `adapter.py::_cam_to_body_with_tilt` —
   confirm whether the wrong axis is only in the training perception MODEL (`perception_obs.py`,
   likely — good news, means the real detector sees forward) or also in the deploy adapter.
2. **Close the remaining 2.92 → 4.83 gap**: fine-tune / FoV-aware retrain Anakin under the corrected
   perception model (now that learning signal exists) — and/or a recurrent estimator for cleaner
   persistence. The frozen-Anakin 2.92 is the floor, not the ceiling.
3. **Wire corrected perception into the real VQ1 sim interface** (W6) for an actual sim run.

---

## Architecture read (your three-part decomposition, confirmed by data)

- **Stage 3 — Controls:** SOLVED. Anakin + exact ego telemetry. (Takeoff survives even at collapse.)
- **Stage 1 — Perception (signal-from-noise):** NOT the bottleneck. Noise is tolerable to ~0.5× W3.
- **The real work — target *persistence* through the blind window** (the seam between perception and
  triangulation): keep a valid gate estimate when it's out of frame. Plus possibly **FoV-aware
  flight** (fly lines that keep the next gate in view), if dead-reckoning alone is partial.

**The end-goal pilot ("Anakin at max performance in any situation") = [state-estimator] → [Anakin].**
The 80M pilot is already the triangulation+controls answer; the undone work is the front-end that
keeps the target alive between sightings.
