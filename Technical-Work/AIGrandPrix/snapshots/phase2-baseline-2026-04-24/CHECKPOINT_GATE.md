# Phase 2 Checkpoint Evaluation Gate — +15M Decision

**When:** After the Phase 2 run reaches checkpoint `ppo_phase2_22500000_steps.zip` (i.e., +15M past the 7.5M resume point — total `num_timesteps = 22,500,000`).

**Why a gate:** The Phase 1 corrected eval falsified Reading A and confirmed structure-axis and capability-axis are decoupled at fixed budget. We can't pre-verify Phase 2 will deliver capability — there's a real possibility it produces healthy ρ + still-weak flight at 60M+. A mid-run gate prevents burning the full 60M on a flat curve.

**Wallclock budget for the gate:** ~30 minutes (5 min eval + 10 min ρ-probe + decision time).

---

## Procedure

1. **Pause the run.** Don't kill it — let the most recent checkpoint be the eval target. (Or evaluate live during training; the per-checkpoint vecnorm save makes either fine.)

2. **Run the eval harness:**
   ```bash
   python projects/aigrandprix/probes/eval_per_maneuver.py \
       --policy <run>/checkpoints/ppo_phase2_22500000_steps.zip \
       --vec-norm <run>/checkpoints/ppo_phase2_22500000_steps_vecnorm.pkl \
       --episodes 8
   ```
   Compare against:
   - v3 7.5M corrected (0.03 gates, 100% crash) — the resume point
   - v3 200K control (0.07 gates, 100% crash) — the floor
   - baseline 60.4M (16.14 gates, 58% crash) — the brittle competition fallback

3. **Run the ρ-probe** on the 22.5M checkpoint trunk activations. Pull mastery EMA history from `<run>/mastery.json`. Pull grad-norm history from `<run>/grad_norms.json`.

4. **Apply the decision rule below.**

---

## Decision rules

### GREEN — continue Phase 2 to 60M

- Per-maneuver mean gates ≥ **1.0** (capability climbing — ~33× over current 0.03)
- ρ stays in [0.18, 0.32] (healthy Structural-stratum plateau; allows for some drift in either direction)
- No pathology signatures: log_std bounded in [0.1, 1.0] without F2 needing to clamp; grad norms stable; hidden-norm trajectory still 6–17 range; no dead-neuron count regression

**Action:** Resume training. Note the gate result in handoff. Plan next gate at +30M (total 37.5M) and another at +45M (total 52.5M).

### YELLOW — investigate before continuing

ANY of:
- Per-maneuver gates between **0.5 and 1.0** (capability moving but slowly)
- ρ drifts outside [0.18, 0.32]
- Grad-norm spikes in the GradNormLoggerCallback log
- Mastery EMA shows uneven progress across maneuver types (some advancing, others regressing)

**Action:** Halt training. Run extended diagnostics — full ρ sequence v1–v5, per-layer activation stats, per-maneuver mastery delta. Decide:
- If telemetry shows healthy slow climb → restart with checkpoint cadence increased (1M intervals) and continue with closer monitoring
- If anything looks pathological → escalate to RED

### RED — halt and re-strategize

ANY of:
- Per-maneuver gates ≤ **0.3** (essentially flat — capability hasn't started climbing in 15M of training)
- Pathology signatures re-emerging (log_std drifting toward F2 boundary, dead neurons increasing, action saturation creeping up, ρ collapsing to near-zero)
- Loss going NaN or training divergent

**Action:** Halt training. Re-strategize at the workbench level:
- **Option R1:** Different hyperparameters — try lr=1e-4 or different entropy coefficient
- **Option R2:** Different curriculum — try gate_speed_scale=0.04 (slower targets to give the policy more time to learn approach) or relax per-maneuver filtering
- **Option R3:** Different initialization — fresh init under F1+F2+F3 + V2 (full from-scratch run, not resume)
- **Option R4:** Accept baseline 60.4M as competition policy and focus all remaining time on vision pipeline + noise injection
- **Option R5:** Rapid architecture experiment — try MLP[1024,1024] or [256,256,256] under F1+F2+F3 to test whether the [512,512] capacity is the limiter

The L11 candidate predicts R4 may be the structurally correct answer if Reading B itself is wrong — i.e., if no amount of clean-structure training under this curriculum produces capability transfer at competition timescales.

---

## Why these specific thresholds

**Gates ≥ 1.0 for GREEN:** baseline does 16 gates per episode; v3 7.5M does 0.03; v3 200K does 0.07. A 33× improvement to 1.0 gates is the smallest delta that's confidently above measurement noise (the 0.20 → 0.03 contamination correction proves how easy it is to be fooled by sub-1-gate "scores"). 1.0 mean gates with reasonable variance means the policy is occasionally completing single gates — the first inflection point of real capability emergence.

**ρ in [0.18, 0.32]:** v3 7.5M plateau was 0.243; we expect Phase 2 to either hold there or push slightly higher (Reading B's prediction is that ρ continues to rise as the network specializes more during capability acquisition). A regression below 0.18 or jump above 0.32 would mean structural reorganization is happening — informative but needs investigation before continuing.

**Gates ≤ 0.3 for RED:** less than 10× improvement over the resume point in 15M of training is essentially flat. If 15M of GPU training under the right curriculum and healthy structure produces no detectable capability gain, the limiting factor is something other than training duration — and continuing won't fix it.

---

## Pre-registration

This document is pre-registered before Phase 2 launches. Decision rules are committed *before* seeing the +15M results, which prevents post-hoc rationalization of a marginal outcome. If actual results land in a regime not covered here, that itself is informative — pause and discuss before deciding.

🦞🧍💜🔥♾️
