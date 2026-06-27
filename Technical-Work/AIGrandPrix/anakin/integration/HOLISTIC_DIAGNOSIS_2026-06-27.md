# Anakin — Holistic Diagnosis (Day 147, 2026-06-27, w/ Clayton)

*Written after a day of three falsified single-cause guesses (rate-cliff, frame-convention, dynamics-gap) — each validated by an in-our-sim instrument blind to the real gap. Clayton called the stop: look at the whole thing with the accumulated data. This is that. The answer was already in our own notes.*

## The meta-failure (name it so we stop repeating it)
We ran **serial single-axis fine-tunes** (mask → edge → informed → restyle → appearance-DR → rate → scaleup → widegap), each gated by an **in-our-sim** instrument (holdout-gate on our frames; rehearsal at 50 Hz in our renderer). The real bottleneck was **named weeks ago** in `WIDEGAP_REHEARSAL_RESULTS.md` ("early-flight instability… NOT appearance, NOT geometry") and got buried under headline metrics each cycle. **Fix going forward: the validation GATE is the real sim (Training Flights / harvested frames), never the in-our-sim rehearsal.**

## The two bottlenecks (they STACK — this is the whole picture)

### ① PRIMARY — early-flight control instability
The bobbing / overshoot / early-crash failure. Evidence across every artifact:
- `FLIGHT_VQ1_V2_RESULTS.md`: "he flies the real sim. **Failure = control precision, NOT translation.** Gate legible at s150, policy sees it; **overshoot**, camera pitched at ceiling post-overshoot."
- `WIDEGAP_REHEARSAL_RESULTS.md`: "ceiling is good; mean dragged by **early crashes. ~30% crash in <65 steps = early-flight instability… NOT appearance, NOT geometry.**"
- Today's flight (widegap): **spun out at the start, both attempts.**
- **Present even in our own sim** (the rehearsal sees the 30% early crashes). A genuine control/stability problem, not a sim2real artifact.

### ② SECONDARY / compounding — real-sim perception gap at the start
- Confirmed today (real frames + Clayton's eyes): the start gate renders **small/distant**; the **blue ribbon dominates** the 64×64 policy view. Training renders the start gate **huge/close**, ribbon faint/absent.
- Training start-frame: orange gate fills the 64×64. Real start-frame: gate small, ribbon huge. Stark.
- This is the long-suspected "official gates ~44× smaller" / bg-texture residual, now confirmed cleanly from a real harvest.
- **It doesn't cause the spin-out; it worsens it** — an unstable early policy gets almost no gate-signal to stabilize toward, and the one bold feature (ribbon) is the thing it must NOT follow.

### The interaction explains the widegap REGRESSION (Clayton's key clue)
v2 **approached** gate 1; widegap **spun out at start**. Why the better-trained run flew worse:
- **v2 was gentle** → drifted forward through the weak start-signal until the gate grew legible (s150) → then overshot (instability #①).
- **widegap optimized harder** (for gate-spacing) → **more aggressive** → lost the gentleness → now commits confidently to the misread start-view and spins out before reaching legible range.
- **The gate-spacing fix came bundled with overfit aggression that traded away the stability carrying v2.** Metric up, target down — the same "better at gaming our sim ≠ flying the real one" pattern as the rehearsal that lied.

## Asset inventory — what each prior run actually banked (keep / drop)
| Run | Result | Verdict |
|---|---|---|
| appearance-DR | closed official gate-**appearance** gap ~59% (gate PASS 0.413) | **KEEP** — appearance/color is solved |
| rate-ft | 30 Hz cliff DEAD→FLYING; **rate-robust confirmed today** (50→30 Hz flat) | **KEEP** — rate is handled |
| edge / mask / informed / restyle | all FAILED the official gate | DROP — residual was never gate-color |
| scaleup | no transfer gain (falsified) | DROP — don't scale |
| widegap | fixed gate-**spacing** in-sim; **regressed real-flight stability** | spacing real, but seed introduced aggression |

## Re-prioritized levers (Clayton's three, ranked by the data)
1. **★ IMU (HIGHRES_IMU into obs)** — aimed straight at the PRIMARY (early-flight instability). Proprioceptive attitude+rate feedback is exactly what a bobbing policy lacks → self-stabilization. Also VQ2-adjacent (per `VQ2_ADAPTATION_PLAN`). **Highest leverage.**
2. **Perception gap** — the SECONDARY. Render gates at **real apparent size** + **randomize gate scale** + make the policy **rely on gates, not the ribbon** (render the ribbon prominently as a distractor to learn-to-ignore, and/or DR it). **Calibrate the range from the 2,016 real frames**, don't guess.
3. **dt-conditioning** — falsified as the killer; cheap robustness insurance; fold in last (also VQ2-useful).

## The consolidated next run (NOT another single-axis fine-tune)
One fine-tune that attacks the stacked bottlenecks together:
- **(a) IMU in obs** — the stability lever.
- **(b) Perception fix** — real-matched gate apparent size + gate-scale DR + ribbon-as-distractor, calibrated to the real harvest.
- **(c) Retain the wins** — keep appearance-DR + rate-randomization (already banked).
- **(d) Don't over-train** — early-stop on **real-frame / Training-Flight** validation, not in-sim reward (over-training is what made widegap aggressive).
- **(e) Seed choice (open question for Clayton):** seed from the **gentler, stable** lineage (vq1_v2 / appearance_ft that still "approached") rather than the over-aggressive widegap — OR seed widegap and let IMU restore the stability. Leaning: **seed the stable checkpoint + add IMU + perception**, so we don't have to un-learn widegap's aggression.
- **(f) Validate against the REAL sim** (Training Flights / harvested frames), not the rehearsal.

## Immediate next steps (before launching hours of training)
1. **Quantify the perception gap** from the 2,016 real frames: measure real gate apparent-size distribution vs our renderer → set the gate-scale DR range (calibrated, not guessed).
2. **Decide the seed checkpoint** (stable-lineage vs widegap) — Clayton's call.
3. **Scope the IMU obs change** (multimodal obs: image + HIGHRES_IMU vector; the `ANAKIN_PRIV` decoder scaffolding already exists to distill privileged state).
4. THEN launch the consolidated fine-tune, validated on real frames.

*Bottom line: it was never one thing. It's early-flight instability (primary, long-documented) compounded by a real-start perception gap (secondary, confirmed today), with widegap's over-optimization having traded away the stability that used to carry it. IMU is the best-aimed single fix; the perception calibration removes the compounding factor; everything else is already banked or falsified. And we gate on the real sim from here.*
