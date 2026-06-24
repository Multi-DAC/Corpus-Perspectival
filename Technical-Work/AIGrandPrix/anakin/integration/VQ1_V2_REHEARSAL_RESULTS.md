# vq1_v2_ft — translation rehearsal — Day 144 (2026-06-24, w/ Clayton, re-engaging Anakin pre-VQ2)

**Checkpoint:** `maneuver_vq1_v2_ft/best.pt` (the reward-v2 timidity-trap fix: CRASH=40 < GATE=100, LC56; warm-started from appearance-ft; trained Day 142, NEVER rehearsed until now). 10 eps, seeds 1000–1009, CPU, `translation_rehearsal.py`.

## Result — TWO robust wins + one standing wall
| condition | return | gates | Δ vs direct |
|---|---|---|---|
| direct (in-sim anchor) | +218.30 ± 116 | **1.8** | — |
| band (VFoV crop only) | +245.17 ± 95 | 1.9 | +12.3% |
| blur (resample only) | +243.86 ± 199 | 1.9 | +11.7% |
| band_resampled (crop+resample) | +305.15 ± 96 | 2.1 | +39.8% |
| **roundtrip (full competition adapter)** | **+245.43 ± 88** | **1.9** | **+12.4%** |

### Win 1 — the timidity fix WORKED (chaining floor moved up). LC56 confirmed.
- Gate-count **1.8 direct / 1.9 roundtrip**, vs the prior baselines: appearance-ft 1.3, scaleup 1.2–1.3, **v1 reward 1.1–1.2**. 8/10 direct episodes now chain 2 gates (was: most stop at 1).
- The reward-v2 hypothesis (de-absorbing `CRASH==GATE` so "pass-then-crash" stops being break-even) is **borne out** — the policy is no longer satisfied stopping at one gate. Predicted ≥1.5; got 1.8–1.9.

### ★ Win 2 — the ADAPTER/TRANSLATION TAX VANISHED.
- **Every prior checkpoint paid −39% to −47% roundtrip-vs-direct** (the band+resample translation cost = a real killer; SCALEUP_REHEARSAL Day 141). **vq1_v2 pays NONE:** roundtrip +12.4% vs direct (i.e. roundtrip ≈ direct, slightly better). All four adapted conditions are ≥ direct.
- Roundtrip RETURN jumped **+70.94 (appearance) / +37.78 (scaleup) → +245.43** — a large, beyond-noise shift (σ≈90, SE≈28). The policy is now robust through the synthetic competition feed (VFoV crop + resample).
- vq1_v2 is now unambiguously the **best VQ1 candidate.**

### The standing wall — gate-count CEILING ≈ 2 (occasionally 3).
- Best episodes reach 3 gates (blur s1001 +500/3, s1006 +615/3; band_resampled s1006 +581/3) but the **mode is 2**. No episode chained 4+.
- Inter-condition gate differences (1.8/1.9/2.1) are within n=10 noise; the robust claim is "all ≈ 2, no adapter penalty." The RETURN jump and the tax-sign-flip are the beyond-noise findings.
- **Consistent with A154/P248:** many-gate chaining is BUDGET-governed (capability-emergence, ~10–20M steps), not reward/adapter-governed. v2 was a short fine-tune; it fixed the reward-stage and adapter-robustness problems and left the budget-stage problem (5+ gates) untouched.

## Honest caveats
- **Sim-to-sim, synthetic adapter.** This is our own sim through a *synthetic* inversion of the competition camera, NOT the official VQ sim. Cannot test camera-tilt sign, body-frame handedness, thrust calibration (dreamer_pilot live-checklist). "Adapter tax gone" = gone for OUR adapter; the official sim can still surprise.
- n=10, large variance; gate-count is the noisy metric. Returns and the tax-sign-flip are the trustworthy signals.

## Strategy implication (for the 5-day pre-VQ2 window)
1. **vq1_v2 is a solid, adapter-robust, 2-gate-reliable baseline** — keep it as the warm-start.
2. **The lever to lift gate-count past 2 is BUDGET, not reward.** Resume a longer training run from vq1_v2 and test P248: is DreamerV3 still *climbing* with more steps (→ train hard through the 5 days) or *plateaued* under transfer (→ a different lever / curriculum). A chaining-specific curriculum (reward consecutive gates / longer-horizon credit / gate-density) is the candidate accelerator.
3. **Gated on the VQ2 email:** is the 29th a sim/specs drop (adapt) or a submission deadline (ship)? And does VQ2 add speed on top of gates? That sizes/aims the run.
