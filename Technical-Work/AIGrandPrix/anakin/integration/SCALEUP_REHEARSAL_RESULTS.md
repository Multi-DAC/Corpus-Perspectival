# Scale-up best.pt — translation rehearsal — Day 141 (~09:00, w/ Clayton)

**Checkpoint:** `maneuver_scaleup_ft/best.pt` (+65.04 in-sim eval, batch 1; scale-up still training on batch 3). 10 episodes, seeds 1000–1009, CPU (alongside live training).

## Result — PREDICTION FALSIFIED (scaling did NOT lift transfer); honest verdict = PARITY
| condition | return | gates | vs direct |
|---|---|---|---|
| direct (training-eval interface = the +65 eval) | **+61.76 ± 111** | **1.3** | — |
| band (VFoV crop only) | +63.34 | 1.3 | +2.6% |
| blur (resample only) | +107.60 | 1.5 | +74% |
| band_resampled (crop+resample) | +44.85 | 1.2 | −27% |
| **roundtrip (full competition adapter)** | **+37.78 ± 100** | **1.2** | **−39%** |

- vs appearance-ft baseline (yesterday): roundtrip +70.94 / gates 1.3. **+37.78 vs +70.94 is within ~1 SE (σ≈100, SE≈32) → statistically INDISTINGUISHABLE.** No detectable transfer gain from scaling.

## ★ The robust finding (variance-independent): scaling improved RETURN, not GATE-COUNT
- **Gate-count is ~1.2–1.3 in EVERY condition, including `direct`.** The +65 return and the +23 seed both chain ~1.3 gates. So the +20→+65 in-sim gain was *flight quality through 1–2 gates*, NOT *chaining more gates*.
- Episodes are **bimodal**: most crash after gate 1 (negative return); a few chain 2–3 gates (+257, +453). The +65 average is carried by the few good ones.
- ⇒ **The VQ1 bottleneck is chaining RELIABILITY (surviving past gate 1–2 repeatedly), NOT training amount.** Scaling the current recipe optimized the axis that was already fine (flight quality) and left the blocking axis (chaining) untouched.
- **A153 re-vindicated at the transfer level:** the in-sim return is a valid *in-sim* signal but a poor predictor of *gate-count/transfer* — the metric optimized ≠ the metric needed.

## Adapter-path tax (secondary)
- roundtrip −39% vs direct, concentrated in the **band+resample interaction** (band alone +2.6% ≈ free; resample alone +74%; combined −27% to −39%). A real translation cost, separate from the chaining bottleneck.

## Caveats / next
- 10 eps, huge variance — a paired re-run of appearance-ft through THIS harness would tighten the cross-run comparison (but the robust gates≈1.3 finding doesn't need it).
- Scale-up still training (batch 3); best.pt may improve, but if it keeps improving *return* without *gate-count*, the bottleneck conclusion holds.
- **Strategy implication (Clayton):** to lift gate-count, the lever is chaining-reliability — candidates: a curriculum that rewards CHAINING specifically / longer-horizon credit; gate-density or recovery-from-near-miss training; NOT more of the same scaling. Discuss.
