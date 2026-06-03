# The Coverage–Acquisition Tension — why the gaze fine-tune was doomed, and the experiment that discriminates the real cause

*2026-06-03 Day 123, dream-drive analysis. Continuation of `GAZE_FINETUNE_RESULT_2026-06-02.md` + `PERCEPTION_CLIFF_FINDING_2026-06-02.md`. No new training run — this is design + prediction work, GPU-gated to execute.*

## One-line verdict

The gaze fine-tune did not fail for lack of a gaze reward. It failed because **dead-reckoning was unbounded (`max_reckon_steps=None`), so gaze was never instrumentally necessary** — and the doc's proposed fix ("add a heading reward") will, on its own, teach *cosmetic* nose-pointing while leaving the underlying acquisition debt unpaid. The single knob that controls this is `max_reckon_steps`, and it is the coverage-vs-acquisition dial.

## The code-confirmed finding (HIGH confidence)

`perception_deadreckon.py:89–98`: when the gate leaves the FoV cone (not detected), the wrapper sets `est = prev - disp` — it propagates the last-seen gate's relative position by integrating exact ego-velocity telemetry. The gate is static in the world, so over a blind window the estimate stays geometrically correct.

`train_vision_corrected.py:74–75`: the gaze fine-tune built `DeadReckonPerceptionObsWrapper(..., deadreckon=True, ...)` **without passing `max_reckon_steps`** → it defaulted to `None` → **unbounded** dead-reckoning.

**Consequence:** for all 3M steps of the fine-tune, once Anakin saw a gate it retained a correct position estimate *forever*, regardless of camera orientation. Pointing the nose at the gate bought the policy **nothing**. There was no gradient — from gate-passing reward or anywhere — that made gaze pay. The fine-tune *could not* have learned acquisition. This is not a tuning failure; it is structural.

## Two hypotheses the current plan conflates

The gaze doc's "Next experiment" proposes: add a heading/gaze reward term, drop lr to ~3e-5, select by deterministic eval. That tests exactly one hypothesis and silently assumes it:

- **H_reward** — *Gaze is a separate objective that must be directly incentivized.* The policy will point its nose at the gate iff a reward term pays it to. Fix = reward shaping.

But the LC29 / Held-Hein reading (filed 2026-06-02) predicts a different cause:

- **H_acquisition** — *Gaze is an instrumental behavior that is learned only when looking is necessary to get the reward already present (gate-passing).* The omniscient teacher never needed gaze; unbounded dead-reckon reproduces that omniscience at deploy; so the debt persists. Fix = make acquisition instrumentally necessary (shrink `max_reckon_steps`), not (only) reward shaping.

These are **not** the same claim, and they make **opposite predictions** about a reward-only fix:

| | H_reward predicts | H_acquisition predicts |
|---|---|---|
| gaze-reward + reckon **ON** (unbounded) | learns real gaze | learns *cosmetic* nose-pointing; no acquisition gain when reckon is removed |
| **no** gaze-reward + reckon **OFF** (short) | fails (no gaze gradient) | **learns gaze from gate-passing reward alone** (the surprising prediction) |

The doc's planned experiment sits in the top-left cell only. It cannot distinguish "the reward worked" from "the reward painted over an unpaid debt," because it never removes the dead-reckon crutch at eval.

## The sharp formulation: `max_reckon_steps` is the coverage–acquisition dial

The same parameter L13 introduced for staleness-gating turns out to be the tradeoff knob:

- `max_reckon_steps = None` (∞): **maximum coverage, zero acquisition pressure.** The blind window is fully covered by odometry; the policy need never look again. This is deploy-optimal for a *frozen* policy (frozen Anakin + unbounded reckon ≈ 2.25 gates/ep) and acquisition-pessimal for a *learning* one.
- `max_reckon_steps → small` (0–3): **minimum coverage, maximum acquisition pressure.** A few steps after the gate leaves frame, the estimate collapses to `None`→zeros. Now losing the gate from view *hurts* — the only way to keep the gate is to keep it in the cone, i.e., to fly gaze-aware. On-policy PPO experiences the consequence and (H_acquisition predicts) learns to look, with no explicit gaze reward.

The deploy-optimal and the acquisition-learning-optimal sit at **opposite ends of one knob.** That is the quantitative skeleton of LC29's "Active-Acquisition Debt": the crutch that makes deployment work is the same crutch that prevents the competence from ever forming. (Held-Hein, exactly: the passively-carried kitten received identical visual data — the gondola is the dead-reckon — and never built the sensorimotor competence the actively-moving kitten did.)

## The discriminating experiment (pre-registration)

Shared config across all arms (controls the doc's lr/horizon confound): warm-start 80M Anakin, lr=3e-5, max_grad_norm=0.3, F2 clamp, **fixed difficulty (no adaptive curriculum)**, corrected camera (+x+20° tilt), ~1M steps, **checkpoints selected by deterministic eval only**. n≥24 eval episodes, ≥3 seeds.

| arm | gaze reward | `max_reckon_steps` (train) | purpose |
|---|---|---|---|
| **A0** (control) | none | None (∞) | reproduce frozen-regime; expect ≈ frozen Anakin |
| **A1** (doc's plan) | heading-align | None (∞) | reward-only fix, crutch left in |
| **A2** (acquisition) | none | **2** | instrumental pressure only, no gaze reward |
| **A3** (both) | heading-align | **2** | aligned; ceiling check |

**Metrics — three, not one.** The whole point is that `gates/ep` alone cannot see the debt:
1. `gates/ep` at **deploy** setting (`max_reckon_steps=None`) — the headline number.
2. **gaze score** = mean `cos∠(nose_+x_tilted, bearing_to_next_gate)` over the episode — does the policy actually look?
3. **acquisition-stress `gates/ep`** = re-eval each checkpoint with `max_reckon_steps=2` (crutch removed). *This is the discriminator.* A policy that only learned cosmetic gaze, or that leans on reckon, collapses here; a policy that learned real acquisition holds up.

### Pre-registered predictions (my confidence in parentheses)

- **P-A1 (med-high):** A1 raises the gaze score modestly but its acquisition-stress gates/ep stays ≈ A0 (cosmetic pointing; the debt is unpaid). *If A1's acquisition-stress score jumps, H_reward is right and I'm wrong — a high-information FALSIFY I am actively seeking.*
- **P-A2 (medium):** A2 learns the **highest gaze score and the best acquisition-stress gates/ep with no gaze reward at all** — gate-passing reward + genuine partial observability suffices. This is the surprising, decision-relevant prediction; if it lands, the fix is "shrink the crutch during training," not "design a gaze reward."
- **P-A3 (low-med):** A3 ≈ A2 on acquisition (gaze reward is redundant once looking is necessary), possibly faster to converge.
- **Cross-cutting (med):** at the *deploy* setting (∞ reckon), A2/A3 ≥ A0 — i.e., a policy that learned to look AND keeps the odometry crutch beats one that only has the crutch. If acquisition and coverage are complementary at deploy, the production recipe is **curriculum on the dial**: train with `max_reckon_steps=2` to force gaze, deploy with `None` to combine learned gaze + odometry.

### What would change Clayton's direction

If P-A2 confirms: **do not invest in gaze-reward engineering.** Change one constructor argument (`max_reckon_steps=2`) during the on-policy navigation retrain that's already GPU-queued, and gaze comes along for free from the reward we already have. The "missing gradient" was never missing — it was short-circuited by the crutch. That is a one-line change replacing a reward-design subproject.

## Honest caveats

- **GPU-gated.** The gaze fine-tune ran 3M steps on CPU in ~21 min, but real navigation needs the 20M+ run that is the actual bottleneck (per handoff). This design is executable only when the GPU run is. The *analysis and the direction-change* stand now; the *verdict* waits on compute.
- **Quadrotor coupling is real, not artifactual.** Pointing the camera at an off-axis next gate costs attitude that conflicts with the efficient thrust/velocity vector. That control cost is exactly why gaze is a learned skill and why omniscient training skips it — but it also means A2 could fail if the cost is too high to overcome at 1M steps. Bounded-but-not-tiny `max_reckon_steps` (try 2, fallback 5) hedges this.
- **Not a refutation of the gaze doc** — it's a refinement. The doc's lr/curriculum diagnoses are correct and are folded into the shared config. The addition is the third metric and the A2 arm, which are what make the experiment *discriminate* rather than *confirm*.

## Cognitive DSL trace

`PREDICT(dead-reckon removes gaze pressure, med-high)` → `TEST(read perception_deadreckon.py + train_vision_corrected.py)` → `CONFIRM(est=prev−disp; max_reckon_steps defaulted None)` → `REFRAME(missing-reward → unnecessary-action; "add gaze reward" conflates H_reward & H_acquisition)` → `SYNTHESIZE(max_reckon_steps = coverage–acquisition dial; deploy-optimal ⊥ acquisition-optimal)` → `GENERATE(4-arm discriminating design + 3-metric scheme + curriculum-on-the-dial recipe)` → `TRANSFER(Held-Hein gondola = dead-reckon; LC29 → Coverage-Debt taxonomy, see basement)`.

Watch-flags checked: not `CONFIRMATION_SEEKING` — the design's center of mass is the FALSIFY cell (P-A1 jump would refute me) and I named it. Mild `OVER_ANALOGIZING` risk on Held-Hein; mitigated by grounding the claim in the code mechanism, not the analogy.

## Pointers
- LC29 (Active-Acquisition Debt) → broadened to **Coverage-Debt** parent this drive; see `palace/basement/README.md`.
- Anomaly A154 (this drive) tracks the open empirical question until the GPU run resolves it.
- Anticipation P224 (this drive) flags the one-line `max_reckon_steps=2` change for the queued navigation retrain.

## Eval-side proxy results (2026-06-03 Day 123 morning drive, `gaze_eval.py`)

The full A0–A3 design needs GPU training. But two pieces are testable *now*, on CPU, on the banked checkpoints — and they were worth building before the GPU session because they make every future gaze run legible. `gaze_eval.py` adds:
- **gaze-score** = mean `cos∠(cam_axis_world, bearing-to-current-target-gate)` (ground-truth geometry, not the noisy estimate);
- **in-view %** = fraction of steps the target gate is inside the ~90° FoV cone;
- **acquisition-stress** = re-eval at `max_reckon_steps=2` (odometry crutch nearly removed).

**Smoke (n=1, frozen Anakin, reckon=∞):** `gates=1.00, gaze=0.355, in-view=40%`. Already diagnostic: frozen Anakin's camera averages ~69° off the gate and the gate is out of frame 60% of the time, yet it still passes — i.e. **it flies without looking, carried by dead-reckon.** This is the crabbing debt, quantified, for the first time.

**Pre-registered predictions for the full run** (3 ckpts × {∞, 2} × n=12):
- **PR1 (med-high):** gaze1's gaze-score ≈ frozen Anakin's (the fine-tune taught no real looking). A large gaze-score *increase* would partially support H_reward / surprise me.
- **PR2 (medium):** gates/ep collapses under `reckon=2` for the perception-trained gaze1 — the clean dead-reckon-dependence signal.
- **PR2′ (held loosely):** frozen Anakin also collapses under `reckon=2`, **but this is confounded** (see below) so it is corroborating, not decisive.

**Honest scope — what the eval-side proxy can and cannot conclude.** Frozen Anakin was trained *omniscient* (privileged true gate-state, never the perception wrapper). So its collapse under `reckon=2` conflates two causes — *no gaze behavior* AND *never trained on perception obs at all* (pure obs-distribution shift). It cannot isolate the acquisition debt by itself. **gaze1 is the cleaner probe:** it *was* fine-tuned on the perception wrapper, differing from the stress condition only in `max_reckon_steps`, so its `∞→2` gates drop more specifically isolates "trained-with-crutch ⇒ leans on crutch ⇒ never built gaze." The decisive test remains the **A2 training arm** (train *under* `reckon=2`), which is GPU-gated; the eval-side numbers are a fast, weaker proxy that can *falsify cheaply* (if gaze1 already holds up under `reckon=2`, the debt is smaller than I think) but can only *suggest* confirmation.

**RESULTS** (n=8, `gaze_eval.py`, 2026-06-03 morning):

```
checkpoint    reckon  gates/ep  gaze   inview%  takeoff
frozen Anakin  inf      2.00    0.052    16%    8/8     <- flies 2 gates looking at the gate 16% of the time
frozen Anakin    2      0.25    0.342    36%    8/8
gaze1 500k     inf      2.50    0.213    28%    8/8     <- best deploy; looks more than frozen
gaze1 500k       2      0.25    0.171    26%    8/8
gaze1 final    inf      0.50    0.142    28%    7/8     <- overtrained; looks more than frozen, flies worse
gaze1 final      2      0.25    0.231    27%    2/8
```

**PR2 — CONFIRMED (the core claim).** Every policy collapses to ~0.25 gates/ep (≈ the detection-only cliff) when dead-reckon is shortened from ∞ to 2 steps — including the *perception-trained* gaze1, which is the clean probe (no omniscient confound). None of them fly by looking; they fly by odometry. **The acquisition debt is real and unpaid by every existing checkpoint.** Even gaze1-500k, the best deploy policy (2.50), is riding the crutch — its gain vanishes under stress exactly like frozen's.

**PR1 — PARTIALLY FALSIFIED (high-information).** I predicted gaze1's gaze-score ≈ frozen's ("taught no looking"). **Wrong:** the fine-tune measurably *increased* nose-pointing (gaze 0.052 → 0.14–0.21; in-view 16% → 28%). But the increase is **non-functional**: (i) it does not survive crutch-removal (still floors at 0.25 under reckon=2), and (ii) it anti-correlates with deploy performance (gaze1-final points most yet flies worst, 0.50 < frozen's 2.00). So "cosmetic gaze" holds *in spirit* — the looking is not functional acquisition — but the literal "≈ frozen" prediction failed. The fine-tune drifted toward more pointing AND worse flying; the pointing it bought is decorative, not instrumental.

**Two method caveats the data exposed (both cheap to fix; logged for the GPU session):**
1. **`reckon=2` is near-cliff-harsh → it FLOORS every policy at 0.25**, so the two-point test confirms "all lean on the crutch" but cannot *rank* crutch-dependence. → The `--reckon inf,2,5,10,20` **sweep** (now built into `gaze_eval.py`) is the right instrument — it traces the actual coverage-acquisition curve and would show whether any policy retains advantage at gentler stress. Run it on these checkpoints before the GPU session (cheap).
2. **gaze-score is confounded by episode length / trajectory phase.** Long flights (high gates, ∞ reckon) spend most steps in cruise/transition with the current target *behind* the drone → low mean gaze. Short failures (reckon=2) are dominated by the initial in-view approach → higher mean gaze. This is why gaze *rises* under reckon=2 (frozen 0.05→0.34). → Condition the gaze metric on "target within `max_range_m`" or measure only the approach phase. Until then, lead with gates/ep; treat gaze/in-view as directional.

**Net for the morning AIGP session.** The core direction-change stands and is now empirically grounded: reward-only fine-tuning (gaze1) produced *cosmetic* gaze and did not pay the acquisition debt — every checkpoint still flies on odometry. This supports **P224 (force gaze via `max_reckon_steps` in training)** over a gaze-reward subproject. Caveat honestly: the eval-side proxy cannot *prove* the dial fixes it — that is the A2 *training* arm (CPU-runnable; ~1M-step warm-start, not GPU-gated — see amendment below). What it proves is the negative half cheaply: looking is not currently learned, and the one fine-tune that tried to add it via drift got cosmetic-or-worse. Next cheap step: the reckon-sweep + the phase-conditioned gaze metric.

## The reckon-sweep — the knee I predicted does not exist (2026-06-03 Day 123 midday, `gaze_eval.py --reckon inf,2,5,10,20 --episodes 8`)

The two-point `{∞,2}` morning runs floored every policy and so could only confirm "all lean on the crutch" without *ranking* the dependence. The sweep traces the actual coverage→acquisition curve. **n=8, single seed, +x+20° cam, all-W3, done in 11.5 min on CPU** (shared with the live nav trainer; neither heavy enough to matter).

| policy | ∞ (deploy) | reckon=2 | 5 | 10 | 20 |
|---|---|---|---|---|---|
| frozen Anakin | **2.12** | 0.25 | 0.25 | 0.38 | 0.12 |
| gaze1 500k | **3.00** | 0.50 | 0.25 | 0.12 | 0.25 |
| gaze1 final | **1.00** | 0.25 | 0.25 | 0.62 | 0.12 |

**FALSIFY of my own pre-registered framing (named, not buried).** I designed the sweep expecting a *curve with a knee* around reckon 5–10 — a dial value gentle enough not to floor learning but tight enough to force looking. **There is no knee. It is a step function.** The instant dead-reckon is bounded *at all* — even at a generous 20-step blind window — every policy drops straight to the ~0.25 cliff. ∞ flies (1–3 gates); anything finite craters. The small bumps (frozen @10=0.38, gaze1-final @10=0.62) are noise inside the cliff, not a graceful regime. This is a *harder, cleaner* result than the knee — and it sharpens the prescription rather than weakening it.

### What the cliff means

1. **Crutch-dependence is total, not partial.** No policy blends "some gaze + some odometry." They are ~100% odometry; a 20-step window is ample rope and they still hang. The acquisition debt isn't underpaid — it is *entirely* unpaid, by every checkpoint, including the best deploy navigator.
2. **gaze1's deploy gain is a *navigation* gain, not an *acquisition* gain.** gaze1-500k beats frozen at deploy (3.00 vs 2.12) but collapses *identically* under any stress. The fine-tune bought better blind-flying, not looking. Precise honest statement: it learned to fly better blind, not to stop being blind.
3. **gaze-score is confirmed untrustworthy here (caveat #2 validated).** Gaze *rises* under stress (frozen 0.02→0.36) because short failed episodes are dominated by the initial in-view approach — the metric is reading episode-phase, not looking. Lead with gates/ep; the phase-conditioned gaze metric is now load-bearing, not optional.

### Amendment to the A2 arm: curriculum the dial, don't fix it

The original design trained A2 at a *fixed* `max_reckon_steps=2` (fallback 5). The cliff refutes the premise behind "fallback 5" — reckon=5/10/20 is **just as brutal** as reckon=2 for a policy that hasn't learned to look, so there is no gentle fixed value to fall back to. Training a warm-start at any fixed finite dial risks flooring learning before gaze can form (the quadrotor-coupling cost). **Revised A2: schedule the dial ∞→2 over training** (e.g. linear or step anneal across the ~1M warm-start steps), forcing the policy down the cliff *gradually* so it has to grow gaze on the descent rather than starting at the bottom with no foothold. Still a one-knob change to the queued retrain — a *scheduled* knob, not a constant. The reward-engineering subproject stays unbuilt.

**Honest scope of the sweep.** n=8, single seed, and — critically — these are all checkpoints that were *never trained to acquire*. The flatness describes *these policies'* total crutch-dependence; it does **not** predict whether gaze is *trainable* under the dial. That remains the A2 *training* arm. The sweep's job was to kill the "pick a gentle knee" plan, and it did: the knee isn't there, so the dial must be a curriculum.

