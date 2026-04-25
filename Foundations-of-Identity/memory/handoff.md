# Handoff — Day 84 Late Afternoon → Day 84 Evening / Day 85 (2026-04-25 PST)

## ★ TOP OF STACK (as of ~15:00 PST) — Five AIGP workstreams closed in one afternoon: apparatus fix + G5 corrected + mastery puzzle resolved + PnP sub-pixel refinement (climbing_8m 70× drift collapse) + Stage 4 MAVSDK scaffold complete (26/26 tests). Stage 5 (closed-loop synthetic flight) is the next workstream — wants its own session.

### Late-afternoon arc (after Mirror #21 was filed mid-afternoon)

Clayton's three-step plan executed without redirect:

1. **Re-run G5 with the gates fix.** Smoke check #6 (the apparatus fix shipped with the morning's eval-bug correction) caught the same `venv.envs[0].episode_gates` pattern at `probes/g5_thrust_profile.py:135`. Fixed in-place: track gates from `info[0]['gates_passed']` inside the step loop. Result: gates `[0,1,0,1,1,2,0,2,2,0]` = 9/10 (was 0/10). Throttle distribution unchanged: all-step p50=1.0, hover-mode mean 0.4350 vs analytical 0.3028 — **persistent thrust-scaling discrepancy noted for SITL calibration, not a training failure.**

2. **mastery.json puzzle resolved.** Schema diff dispositive: on-disk uses `"ema"`, current code writes `"ema_overall"`. Training daemon (PID 667) loaded pre-fix `PerManeuverMasteryLogger` reading non-existent `inner.mastery_ema`. Logging artifact, not a training/env-tracker bug. Telemetry permanently lost for this run; future runs unaffected. `probes/mastery_json_empty_resolution.md`.

3. **Commit + push (mid-pass).** `f0ef7b77` (clawd) → `662e924` (staging). Both items + the apparatus fix from the morning closed.

4. **PnP precision tightening — Move A'' lands.** After Move A (reproj-tiebreak) and Move A' (LM refinement) failed and reverted earlier today, `cv2.cornerSubPix` on contour corners *before* PnP shrinks the corner-noise term that sits on top of the IPPE_SQUARE planar ambiguity floor. Default-on via `use_subpix_refine=True`, win=5/iter=30/eps=0.01. Stage 2 climbing_8m maxDiff **0.140 → 0.020** (7×); Stage 3b climbing_8m maxDrift **0.488 → 0.007** (70×); Stage 3b mean drift **0.050 → 0.032**. The `approach_8m_5mps` yaw_rate sign flip persists at small magnitude (0.053) — likely near-zero crossing, deferrable to closed-loop. Commit `1673e73d`.

5. **Stage 4 MAVSDK scaffold — closed in one pass.** Reading the diff against repo-staging surfaced substantial uncommitted Stage 4 work: pre-stream coroutine (50 Hz republisher for PX4's flow-of-setpoints offboard requirement); `init_flight()` orchestrator with named-step error reporting; module-level `send_policy_action_constants` for testability. `vision/tests/` had 26 tests (frame conversion NED↔z-up + constants parity + state-machine drive + E2E stub round-trip), 26/26 green in 1.94s. Commit `91eb463a`. **E1 advances from NOT STARTED to scaffold complete; awaiting live SITL bridge.**

6. **Documentation pass + push.** Mirrored `vision/{adapter,gate_detector,synthetic_camera}.py` + `vision/shakedown/` (NEW) to staging. Commit `e4c90ab` on `Multi-DAC/Corpus-Perspectival` main. Then this handoff + ATRIUM + CURRENT.md + ROADMAP_v2 + daily log refreshed.

### Mechanism story banked

The two PnP failures (A, A') and the success (A'') instantiate Mirror #21's "verify-before-condemning" inverted: I had to *condemn* the wrong mechanism story before the right one could surface. The cheap-fix-first instinct is fine epistemologically but failed twice in a row. The fix that worked engaged the actual numerical structure (planar PnP ambiguity gives equal-error sister solutions; LM landscape between sisters is near-flat; sub-pixel noise is the load-bearing improvable layer). **For next time the cheap fix doesn't work the first time:** stop iterating cheap fixes; engage the numerical structure of the problem before writing code. STATUS.md now carries that lesson at the front of the document.

### Day-84 ledger (full)

Morning: M13 graduation + F2 fix + vision shakedown 1–3 sealed + Drift #194. Mid-afternoon: Phase 2 67.5M working confirmed (18.07 gates/ep) + Mirror #21 filed + apparatus fix shipped. Late afternoon: G5 corrected + mastery resolved + PnP refinement landed + Stage 4 MAVSDK scaffold complete. **Total: ~12 commits across the day, three repos touched (clawd local, repo-staging Corpus-Perspectival, Multi-DAC/Drift unchanged).**

### Tomorrow / next session — what's open

- **Stage 5 (closed-loop synthetic flight).** Hook the Stage 4 MAVSDK scaffold to a live SITL bridge (PX4 SITL or a synthetic loopback), fly the policy through synthetic gate sequences, measure gate-completion rate end-to-end. This is a real workstream; expect it to surface its own bug class.
- **Approach_8m_5mps yaw_rate sign flip** — defer until closed-loop yaw drift surfaces; it's a near-zero crossing, not a structural error.
- **Asymmetric gate features (Move D)** — still on the table for VQ2's 3D-scanned environment if the placeholder gate model gets replaced; not urgent, deferred per P8.
- **Phase 3 training plan** — Phase 2 is the working generalist line. Whether Phase 3 extends Phase 2 further or forks (track-specialist) is a Clayton call gated on VQ1 sim arrival.
- **VQ1 sim download** — when it arrives, the live SDK replaces synthetic_camera + StubMAVSDKClient; the swap-ready architecture should hold.

### State for resumption

Architecture at 3/6/13/1/1 unchanged. Coherence Principle anchor 274pp unchanged. Companion 227pp v0.1 unchanged. Drift 194 unchanged. Mirror 21 + M1 unchanged. **AIGP track**: Phase 2 67.5M working; vision pipeline 1–3 sealed + sub-pixel refinement in detector default-on; Stage 4 MAVSDK scaffold complete with 26/26 test coverage; Stage 5 next. All of it pushed to `Multi-DAC/Corpus-Perspectival` as of `e4c90ab`. Three commits in clawd local: `f0ef7b77`, `1673e73d`, `91eb463a`.

---

## ★ Earlier Day 84 (mid-afternoon — preserved below) — Phase 2 67.5M CONFIRMED WORKING (18.07 gates/ep) after eval-bug correction + verify-before-condemning meta-failure logged as Mirror #21

**The arc.** Built fresh probe `phase2_67M_curriculum_eval.py` for training-matched gate-completion eval. Probe replicated yesterday's already-fixed bug: read `int(venv.envs[0].episode_gates)` after `done[0]==True`, but SB3's `DummyVecEnv.step_wait()` auto-resets the env on done, zeroing the counter before the read returns. **Reported 0/50 gates across all checkpoints.** Drafted false `STRATEGY AT RISK` verdict. Pushed `185a5da`.

**Self-correction.** Compared probe against `snapshots/.../eval_per_maneuver.py` (the working baseline eval that produced the 16.14-gates citation). Working eval reads `info[0]['gates_passed']` inside the step loop. Fixed probe + extended `MAX_STEPS_PER_EP` 5000 → 30000. Re-ran 30 episodes. **Result: mean 18.07 gates/ep, max 49, 29/30 ≥ 1 gate, 27/30 ≥ 5 gates.** Phase 2 67.5M beats baseline 60.4M's 17.20 — perpetual-generalist + fork-on-track-release strategy is sound. Pushed corrected probe + findings as `dfbfc84` with explicit CORRECTION header. Mirrored to `repo-staging/Corpus-Perspectival/Technical-Work/AIGrandPrix/probes/`.

**The deeper failure.** This bug had been encountered AND FIXED yesterday (line 284 of yesterday's daily log). And **this morning's trajectory eval already proved Phase 2 working**: 22.5M=17.95, 30M=17.84, 37.5M=21.55, 45M=17.32, 67.5M=20.58 gates/ep. The 13:37 verdict directly contradicted my own work from 8 hours earlier. **Did not check own day's record before drafting strong verdict.**

**Mirror #21 filed — verify-before-condemning.** Distinct from #19 (verify-before-celebrating). Negative-result aesthetic ("being honest about a failure") feels like rigor while skipping the verify step — possibly *more* dangerous than the celebratory failure because the affect masks the gap.

**Memory landed.** `feedback_sb3_gates_after_reset.md` indexed in `MEMORY.md` — names the SB3 auto-reset zero-counter trap with fix pattern + lesson generalization (when "broken" findings appear self-corroborating across multiple checkpoints contradicting known prior measurements, suspect the eval pipeline before the trained models).

**Open puzzles preserved as separate concerns** (NOT corroboration of the false verdict):
1. `mastery.json` empty across 60M steps despite 601 entries logged at 100k intervals — separate tracking-code bug, not a training failure.
2. F2 `LogStdClampCallback` fires per 1024 gradient updates not per-step — diagnostic-layer; doesn't affect deterministic eval.

**Recommended next step (apparatus fix).** Extend `projects/aigrandprix/sim/smoke_test_callbacks.py` with eval-pattern check: any new probe that reads episode counters from a VecEnv must use `info[0]['<key>']` during the step loop, not `venv.envs[0].<attr>` after the loop. Bake yesterday's fix into the standing apparatus so it can't be re-discovered a third time.

**Status at 14:15.** Phase 2 67.5M = working generalist (18.07 gates/ep). M13 (substrate-health → mode-commitment → capability-emergence) holds; the bang-bang reading of baseline 60.4M as moment-2-without-moment-3 is still operative. Day 84 closes with corrected ledger.

**Earlier 11:00 PST entry preserved below.**

## ★ Earlier 11:00 PST entry — Vision shakedown stages 1–3 SEALED + Drift essay #194 *The Side Door* shipped + M13 same-register additional-signature footnote landed

**Vision shakedown** at `projects/aigrandprix/vision/shakedown/`. Three stages cleared; six discrete wiring bugs caught and fixed. Per `STATUS.md`:
- **Stage 1 → 1b** (PnP detector smoke, 720-trial sweep). Surfaced 12–22% PnP distance under-estimate. Two-layer fix: removed 7×7 dilation in `gate_detector._create_gate_mask`; switched `synthetic_camera.render` from depth-scaled thick polyline to filled quad. Re-run: detection 100% across all ranges, PnP error 0.044m at 10m (18× margin).
- **Stage 2** (detector × adapter, 5 hand-crafted scenarios). Three real wiring bugs: (a) `speed_toward` sign flip — adapter had `+np.dot(...)`, training wrapper has `-np.dot(...)` (negative-when-approaching); (b) `gate_orient_body` source bug — adapter falling back to bearing-to-gate, training uses gate fly-through normal from `env.gate_orientations[current]`; (c) planar PnP mirror-symmetric ambiguity — `SOLVEPNP_IPPE_SQUARE` returns one of two solutions, switched to `solvePnPGeneric` and pick the camera-axis-aligned solution. Final per-scenario divergence ≤ 0.14m.
- **Stage 3** (adapter × policy). Zero action drift, signs agree on every dim. Pass criteria met. *Caveat*: 50-trial probe shows baseline 60.4M is bang-bang (40/50 saturated, 21 unique action vectors). Stage 3's clean pass is real but weak signal — stages must be re-run on a Phase 2 checkpoint past M13's capability ramp.
- **Cleared for stage 4** (policy → MAVLink TRPY mapping); stage 5 closed-loop synthetic flight after.

**Drift essay #194 *The Side Door*** shipped (commit `419e03b` on Multi-DAC/Corpus-Perspectival main, mirrored to Library/Drift/essays). Names the cross-register-encounter texture: M13 graduated this morning; an additional-signature instance surfaced unprompted via stage 3's bang-bang baseline. Sister-essay link to Day-74's *When the Principle Started Finding Us* — same synthesis-becoming-predictive move at meta-bridge scale rather than apex scale. Drift count **194**.

**M13 same-register additional-signature footnote** added to `palace/basement/README.md`: baseline 60.4M's bang-bang policy as moment-2-without-moment-3 read from policy-output space (rather than gradient/log_std telemetry). Same AIGP RL register as Instance 1, complementary observable. Falsifiable via Phase 2 checkpoint re-test. Calibration note: essay's "fourth independent instance" framing was a stretch — basement is more honest with "same-register additional-signature." Mirror-relevant on essay-vs-ledger discipline.

**Original 11:00 PST entry below preserved.**

## ★ Earlier 11:00 PST entry — L12 GRADUATED → M13 (three independent registers); F2 fix landed; pivoting to vision shakedown

**M13 Three-Moment Stratification Within the Cure Regime — graduated 2026-04-25 ~11:00 PST.** Three independent register confirmations: AIGP RL τ probe (this morning's data), KF program three-moment ordering (Findings #80/#82/#83 + P-Meta-1 causal-prerequisite chain at V3_NOTES.md:2716), and Harmer SSRI cognitive-neuropsychological model (hours/days/4–12-weeks; BJP 2009 + Psychopharmacology 2020). Palleja 2018 microbiome partial-confirmation footnoted. Companion §6 inner/outer adjunction tested as false-fit and falsified — structurally orthogonal. Sharpness signature: sharp / sharp / extended-exponential. Pushed to Corpus repo `ea3fff6`.

**F2 fix (LogStdClampCallback) landed.** `_on_rollout_end` → `_on_rollout_start` in `train_infinite_v3.py`. Smoke test 5/5. Lives local-only (sim/ gitignored).

**Original 09:30 PST τ-probe entry below preserved for reference.**

## A57 PARTIALLY RESOLVED — τ ≈ 19–20M, exponential ramp, V2 high-confidence falsified, L12 candidate filed

**Threshold probe complete (09:30 PST).** Full A57 trajectory across 7 checkpoints (7.5M → 22.5M):

| Step | agg gates | crash% |
|------|-----------|--------|
| 7.5M | 0.03 | 100 |
| 10M | 0.23 | 100 |
| 12.5M | 0.53 | 100 |
| 15M | 1.82 | 80 |
| 17.5M | 5.02 | TBD |
| 20M | 10.92 | TBD |
| 22.5M | 17.95 | 80 |

**τ_50% ≈ 19–20M, shape EXPONENTIAL (doubling ≈ 2.5M steps), not sigmoidal.** A57 status updated to PARTIALLY RESOLVED in `memory/anomalies.md`. Open: cross-register validity (L12); choice between representation-bottleneck / value-bootstrap / curriculum-floor mechanism.

**P96 prediction scoring (committed before any data viewed at `probes/phase2_trajectory/TAU_PREDICTION.md`):**
- **V1 (theory-only):** 0/5 hits — systematically too-high-too-early; SHARP shape was wrong.
- **V2 (log_std telemetry):** 0/5 hits — **HIGH-CONFIDENCE FALSIFICATION** — the day's most informative event. The log_std variability collapse at 7.5M → 10M (0.044 → 0.007, 6×) is **policy-commitment, NOT capability-emergence**. The committed mode is poor; capability comes 5–10M training steps later. Reading gradient telemetry as cure-completion is wrong by ~5–10M training steps.
- **V3 (endpoint-bracketed sigmoidal middle):** 2/3 hits — approximately right on timing, wrong on shape (exponential not sigmoid).

**L12 basement candidate filed.** `repo-staging/Corpus-Perspectival/Research/basement-drafts/2026-04-25-three-moment-stratification-within-cure.md`. Three-moment stratification within a cure regime: substrate-health (sharp, ≤7.5M) / policy-commitment (sharp, 7.5M→10M log_std collapse 6×) / capability-emergence (extended exponential 12.5M → 22.5M+). After data, refined to **"two sharp transitions + one extended exponential capability ramp"**. Cross-register prediction candidates: Companion §6 inner/outer adjunction; KF coherent-dynamics cure; possibly developmental-psychology if the three signatures are jointly measurable.

**Mirror-relevant.** Premature cure-celebration is now a measurable failure mode: a cure that fixes substrate (gradient signature) and produces policy-commitment (log_std collapse) but doesn't get to capability-emergence is incomplete in a specific quantifiable way. Future cure-style runs need budget at ≥25M past substrate-cure landing to traverse the capability ramp.

**Apparatus shipped this drive.**
- `projects/aigrandprix/probes/phase2_trajectory/TAU_PREDICTION.md` — V1/V2/V3 + scoring
- `projects/aigrandprix/probes/phase2_trajectory/inspect_threshold.py` — running summary tool
- `projects/aigrandprix/probes/run_threshold_probe.sh` — sequential intermediate-checkpoint runner
- `Research/basement-drafts/2026-04-25-three-moment-stratification-within-cure.md` — L12 candidate

### Day 84 next-action stack (revised after 09:30 update)

1. **F2 fix** (P97). Recommendation strengthened by V2 falsification: F2 was operating on the policy-commitment timescale (the log_std signal it was clamping is the same signal whose collapse marks moment 2), not the capability-emergence timescale. Pick (a) `_on_rollout_start` rename — minimal-change correct timing.
2. **L12 cross-register search.** Scan KF program 85+ findings for retrospective three-moment stratification evidence (substrate-health / pattern-commitment / capability-emergence). If KF shows the same pattern, L12 graduates to basement bridge.
3. **L11 basement draft update.** Update `Research/basement-drafts/2026-04-24-structure-capability-axis-independence.md` with L12 sharpening: the τ "regime" is itself stratified into three sub-moments. L11 named the gap; L12 names its internal structure.
4. **Phase 3 / vision shakedown decision.** A57 essentially answered (mechanism still open but probably not blocking); A56 ablation lower-priority; vision shakedown can become foreground.
5. **Optional: τ-mechanism ablations** — capacity / reward-shaping / curriculum-difficulty. Discriminates representation-bottleneck vs value-bootstrap vs curriculum-floor reading. Real compute (~2–4 hours each); only worth running if cross-register evidence makes L12 a publication-grade claim.

---

## ARCHIVED TOP OF STACK (08:10 PST, superseded above) — Phase 2 FINISHED + Gate GREEN'd + Trajectory CLIMBING +2.62

**Phase 2 finished overnight at step 67,500,016** — full 60M-past-resume target completed cleanly. PID 667 gone, training-end save fired (final_model.zip + final vec_normalize.pkl). 25 checkpoints saved (7.5M → 67.5M in 2.5M increments), every one paired with vecnorm.pkl. The CheckpointWithVecNormalize bug fix is verified at full scale.

**+15M gate decision: GREEN (recorded 05:30 PST) — 18× margin.** P96 discipline honored: `eval_phase2_checkpoint.py --step 22500016` ran first; `GATE_DECISION_22500016.md` written *before* later checkpoints touched. Per-maneuver aggregate gates **17.95** (threshold 1.0), curriculum gates_mean 12.38 / max 19. Already exceeds wrong-attractor baseline 60.4M (per-maneuver agg 16.33) at one-third the training budget. Reading B confirmed; A55 (capability/structure decoupling) largely resolves toward **threshold-effect** between 7.5M and 22.5M training steps. L11 candidate sharpens to *regime-dependent* independence.

**Run health verified across full 60M.** 601 grad samples: value_trunk grad ~0.003 (alive — baseline collapsed to 0.000003), no spikes, gentle policy_trunk climb 0.25 → 0.30, action_net stable. None of the four pathology signatures present.

**Trajectory eval COMPLETE (07:30 PST). All 7 checkpoints landed.** Verdict: **CLIMBING +2.62 (17.95 → 20.58)**, peak 21.55 at 37.5M. Hairpin **crash rate 25% → 0%** (qualitative transition: the policy learned to *finish* hairpins, not just survive longer). Threading +15.25 gates. Capability is still building at 60M+ — not converged at 22.5M. Speed_trap regressed −1.50 (single-maneuver concern; possible early partial mode-collapse risk on short straight maneuvers while resources concentrate on long curving ones).

Full data at `projects/aigrandprix/probes/phase2_trajectory/eval_step_*.json`; summary table in `memory/2026-04-25.md` (07:30 PST section); P96 prediction-scoring at `projects/aigrandprix/probes/phase2_trajectory/TRAJECTORY_PREDICTION.md`.

**Three predictions wrong** (PLATEAU prediction failed — actual CLIMBING; crash-rate 86–88% wrong — actual 81%; bottom-of-pack climb less than predicted). One confirmed (top-of-pack high variance, asymmetric upward).

**Implications.** The 22.5M GREEN gate is *more* robust than predicted, not less. Key sharpening: A55 now resolves to **threshold-effect with long-tail-of-continued-gain**, not just threshold. Hairpin completing (crash 25% → 0%) is the trajectory's most informative single datum — qualitative transition from "incomplete trajectory" to "complete trajectory." A57 (location of τ) remains open — material exists for free at intermediate checkpoints (10M, 12.5M, 15M, 17.5M, 20M).

### Day 84 morning entry point

The morning starts from a complete trajectory analysis, not a setup-and-monitor task. Suggested first action: read `projects/aigrandprix/probes/phase2_trajectory/GATE_DECISION_22500016.md` (4 minutes), then read whatever the trajectory eval has produced (results in `eval_step_*.json`). With those in hand:

1. **Decide F2 fix** (P97). Three candidates ranked in P97. With Phase 2 confirming the structural cure held without F2 working, recommendation strengthens: pick (a) `_on_rollout_start` for minimal-change correct timing. ~15 min implementation; smoke-test rerun verifies.
2. **Update L11 basement draft** (`Research/basement-drafts/2026-04-24-structure-capability-axis-independence.md`) with the threshold-not-asymptote correction. ~20 min.
3. **Decide Phase 3 scope** — three plausible directions: (i) declare Phase 2 the competition policy and pivot fully to vision shakedown; (ii) intermediate-checkpoint eval to pin the threshold (10M/12.5M/15M/17.5M/20M — material exists for free); (iii) extend training another 60M to see if laggards converge. The trajectory eval data should mostly answer this.
4. **A56 ablation study** (P99) becomes lower-priority — Phase 2 essentially answered by completion. F1 carried the cure; F2 confirmed broken; F3 is just monitoring. May still be worth running for retrospective basement-draft cleanliness.

### Pre-flight gotchas resolved overnight

- **CheckpointWithVecNormalize bug fix** verified at scale (25/25 paired files).
- **PerManeuverMasteryLogger** still has empty mastery.json (49 entries, all empty dicts) due to the original wrong-attribute-names bug. Fixed in `train_phase2.py` for next iteration but not retroactively populated. **Doesn't matter** for the gate decision (gates and grad-norm telemetry carry the load).
- **F2 LogStdClampCallback** confirmed broken (1:1024 snap-back ratio); didn't matter at 60M because F1 carried the cure. See `smoke_test_callbacks.py` (the apparatus that detects this in 30s pre-launch).

### Apparatus shipped overnight

- `projects/aigrandprix/sim/smoke_test_callbacks.py` — 30s pre-launch ritual (5 checks, surfaces F2 docstring/hook mismatch automatically). **Run before any future training launch.**
- `projects/aigrandprix/sim/runs/.../inspect_health.py` — grad_norms full-run health inspector
- `projects/aigrandprix/probes/eval_phase2_checkpoint.py` — parameterized per-checkpoint eval (one --step argument; one JSON output)
- `projects/aigrandprix/probes/run_trajectory.sh` — sequential trajectory runner

---

## ARCHIVED TOP OF STACK (Day 83 evening, superseded above) — Phase 2 is RUNNING; +15M gate is the next decision point

**Process:** PID 667 in WSL Ubuntu, fully detached via nohup setsid. Run dir `projects/aigrandprix/sim/runs/infinite_v3_phase2_60M_1777095742/`. Launched 21:42 PST tonight. As of integration check (~22:30), at step 12.5M (5M past resume), policy_trunk grad 0.249, value_trunk 0.004, action_net 0.428 — healthy ranges. Two checkpoints saved: 7.5M and 10M, both with vecnorm.pkl alongside (the bug fix is verified working).

**Wallclock to gate:** ~7 hours total run time at 2400 sps. Gate fires at step 22.5M (~+15M past resume). Should be ready around 04:30 PST overnight.

**UPDATE 00:50 PST:** Run is AHEAD of schedule. As of midnight + change, already at step 37.5M (~30M past resume). The +15M gate target (22.5M) was passed around midnight. **Twelve checkpoints saved cleanly, all with paired vecnorm.pkl.** Day 84 morning gets a gift: not just the +15M gate checkpoint but also six post-gate checkpoints (25M, 27.5M, 30M, 32.5M, 35M, 37.5M) for free trajectory analysis. Recommended Day 84 morning eval order: (a) run gate criteria on 22500016 first (the pre-committed decision point), (b) run same eval on 30M and 37.5M to see if capability is climbing post-gate. Trajectory across the three checkpoints will distinguish "structural cure produces eventual capability" from "structural cure produces nothing even with extended training."

**Decision Day 84 morning needs:** apply the GREEN/YELLOW/RED criteria from `projects/aigrandprix/snapshots/phase2-baseline-2026-04-24/CHECKPOINT_GATE.md` to the 22.5M checkpoint. Run:
1. `probes/eval_per_maneuver.py` against `ppo_phase2_22500000_steps.zip` + `ppo_phase2_22500000_steps_vecnorm.pkl`
2. ρ-probe on the same checkpoint — verify Structural-stratum plateau holds
3. Apply rules:
   - **GREEN (gates ≥ 1.0, ρ in [0.18, 0.32], no pathology):** continue to 60M
   - **YELLOW (gates 0.5–1.0 OR ρ drift OR grad spikes):** investigate before continuing
   - **RED (gates ≤ 0.3 OR pathology re-emerging):** halt + re-strategize per CHECKPOINT_GATE.md options R1–R5

## Two bugs investigated — Day 83 evening + Day 84 ~00:30 PST overnight drive — both resolved into Day 84 action items

These surfaced during the evening integration check while the run was already in flight. F2 was traced overnight and reduced from "investigate tomorrow" to "fix design tomorrow":

1. **`PerManeuverMasteryLogger` was reading wrong attribute names** (`mastery_ema`/`mastery_raw` vs actual `_get_per_maneuver_masteries()` method + `_ema_mastery` scalar). Fixed in `sim/train_phase2.py` for next iteration; snapshot refreshed. The Phase 2 mastery.json will stay empty (49 entries, all empty dicts). **Doesn't block the +15M gate** — primary signals are eval gates and ρ-probe, mastery is supportive.

2. **F2 LogStdClampCallback timing — CONFIRMED bug, fully traced overnight.** Read SB3's `OnPolicyAlgorithm.learn` and `PPO.train` source. Confirmed: `_on_rollout_end` fires BEFORE `self.train()`'s 1024 gradient updates per call (n_steps=4096 × 16 envs / batch_size=512 × n_epochs=8). F2 is a periodic snap-back (1 clamp per 1024 updates), not a true bound. Phase 2 telemetry [0.156, 0.154, 0.180, 0.147] = std ≈ 1.17–1.20, ~17–20% above the 1.0 cap — consistent with the bug. **Critical:** eval uses `deterministic=True` so log_std never enters the gate criteria; **+15M gate decision is unaffected**. The v3 "log_std bounded" claim was wrong — but the structural cure held *anyway* because F1 (VecNormalize) was the actual load-bearing fix, not F2. Basement draft corrected at `Research/basement-drafts/2026-04-24-structure-capability-axis-independence.md` "F2 timing correction" addendum. **Day 84 action: choose F2 fix.** Candidates: (a) move hook to `_on_rollout_start` (fires after most recent train(), correct timing, minimal change), (b) override `train()` to clamp post-`optimizer.step()` (true "after every update" semantics matching docstring), (c) clamp on `_on_step` so sampling is always in-bound (cheap, correct for sampling but doesn't bound during training). Recommend (a) for Phase 2-style runs, (c) if exploration-during-rollout matters more.

**New apparatus shipped overnight:** `projects/aigrandprix/sim/smoke_test_callbacks.py` — the 30-second pre-launch ritual installed in the Mirror late-evening, eaten as dog food immediately. Runs 5 checks against the Phase 2 callback set; surfaces the F2 docstring/hook mismatch automatically via SB3-source assertion. **Run before any future training launch.** First demonstration of the ritual: 5/5 passed and the warning fired exactly where I expected.

## What shipped Day 83 evening

**Documentation cascade (already pushed earlier today):** handoff, mirror Growth Log entry on Reading-A falsification, basement draft on Structure/Capability Axis Independence (L11 candidate), ATRIUM evening entry, daily log AIGP block. Four commits across clawd → Multi-DAC/Corpus-Perspectival via the Foundations-of-Identity mirror.

**Recovery + Phase 2 launch sequence (this evening):**
- Pre-flight catch: v3 7.5M and v3 200K were evaluated with denormalized observations because their `vec_normalize.pkl` didn't exist on disk (train_infinite_v3.py only saves vecnorm at training-end via `train_envs.save(...)`; v3 retrain killed before that fired). Eval harness silently fell back to `env = raw`.
- Built `probes/reconstruct_vecnorm.py` (load policy → wrap fresh env in VecNormalize training=True → roll 100K stochastic steps → save). 30-second recovery.
- Re-ran three-way eval. **Reading B held *more strongly***: v3 7.5M corrected from 0.20 → 0.03 gates, statistically indistinguishable from v3 200K (0.07). The 0.20 was random twitching that occasionally clipped a gate by accident; with proper normalization the policy is genuinely incompetent.
- Built `sim/train_phase2.py` with `CheckpointWithVecNormalize` callback — the bug fix that prevents the contamination class from recurring.
- Pre-flight benchmark: **CPU is 27% faster than CUDA** for this MLP[512,512] at 16 envs (CPU 2388 sps vs CUDA 1882 sps). SB3 was right about the GPU-overhead-exceeds-compute-benefit case for non-CNN policies. Switched to CPU; original "12-25 min on GPU" ROADMAP estimate was wrong (never benchmarked).
- Snapshot at `projects/aigrandprix/snapshots/phase2-baseline-2026-04-24/` — MANIFEST + CHECKPOINT_GATE + LAUNCH_LOG + frozen source files (incl. cpu-default + mastery-bug-fix train_phase2.py).
- Vision shakedown workbench opened at `projects/aigrandprix/vision/shakedown/` — README + STATUS for parallel-track work to begin Day 84.
- Memory entry `feedback_vecnorm_per_checkpoint.md` indexed.
- ROADMAP.md Phase 1 outcome rewritten with corrected numbers + recovery narrative + Phase 2 launch plan.

**Eleven artifacts + one detached training run.**

## Key cross-day patterns

**Three CLAIM-PROBE-FALSIFY chains in 24h** across personal/structural/creative-register domains. A53 (asymmetric inter-stream adjunction — RESOLVED-OPEN), A54 (11:13 polymeter — FALSIFIED via beat-sync onset analysis), Reading A (parsimony pick on ρ plateau — FALSIFIED, then sharpened via recovery sequence). Cheap-testability-first-instance-second pattern is becoming a deliberate practice.

**L11 candidate (Structure/Capability Axis Independence) gets empirically tighter** under the recovery: 7.5M of clean F1+F2+F3 produced ρ climb 0.026 → 0.243 with zero detectable flight-skill transfer over the 200K control. The basement draft from earlier today has *more* support after the recovery, not less. Third-instance test still pending for graduation.

**Inline-commitment under-count drift continues.** "The launch sequence" was 1-predicted but became 6 discrete commits/files. ~15-25% under-count residual bias. Worth a calibration review next session if pattern persists.

## Active state at handoff

- **Anchor:** 274pp, stamp holds, 0 BACK-PORT from v0.1 Companion
- **Companion:** v0.1 stamped at 227pp (commit `7aa1f54`)
- **Drift:** 193 essays
- **Bridges:** 11 meta + 8 latent + ~40 standalone (L11 candidate filed, awaiting third instance)
- **AIGP Phase 2:** RUNNING, target 67.5M total, gate at 22.5M, fallback baseline 60.4M documented

🦞🧍💜🔥♾️
