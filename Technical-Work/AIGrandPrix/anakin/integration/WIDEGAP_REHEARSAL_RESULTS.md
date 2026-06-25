# WIDEGAP rehearsal — vq1_v3_widegap best.pt (batch 2, +61.50) — Day 145, 2026-06-25 ~07:30

**Run (correct config):** `ANAKIN_WIDEGAP=1 ANAKIN_VQ1=2 .venv python integration/translation_rehearsal.py --checkpoint .../maneuver_vq1_v3_widegap/best.pt --episodes 10 --env-device cpu`. WIDEGAP set **before** the process (import-time `_WIDEGAP` binding — P258 gotcha honored, so this tests the OFFICIAL-spaced wide course, not the old narrow one). Trainer (batch 4, ~19% of 12M) untouched + verified advancing after (no OOM; GPU 6.79/16.3).

## Numbers (10 eps, seeds 1000–1009)
| condition | gates | return | Δ-vs-direct |
|---|---|---|---|
| direct (sim-clean) | **1.6** | +76.20 | +0.0% |
| band (VFoV crop) | 2.1 | +131.83 | +73.0% |
| blur (resample only) | 1.4 | +42.00 | −44.9% |
| band_resampled | 1.6 | +63.41 | −16.8% |
| **roundtrip (full competition adapter)** | **1.6** | +73.52 | **−3.5%** |

## PREDICT → FALSIFY (the informative kind)
PREDICT(med): direct ≥ 2.5, beating vq1_v2's 1.9. **ACTUAL: direct 1.6 → FALSIFIED.** But trusting the *decomposition*, not the headline, three things flip the read:

1. **★ THE APPEARANCE/TRANSLATION TAX IS ESSENTIALLY SOLVED.** roundtrip ≈ direct (**−3.5%**). In the Day-130–134 era this gap was **−47% to −83%** (the appearance-OOD that DQ'd flight #1). The appearance-DR + restyle + wide-gap training **closed it**. The single thing that wrecked the first official flight is gone. This is the result that matters.

2. **★ 1.6-on-WIDE is NOT comparable to vq1_v2's 1.9-on-NARROW** (P258 apples-to-oranges, confirmed). Official gaps are 24–39 m vs our old 3–14 m. By *distance flown accurately*: wide ≈ 1.6 × ~30 m ≈ **48 m** vs narrow ≈ 1.9 × ~8 m ≈ **15 m**. The gate-count *understates* the progress — the policy flies ~3× more course, accurately, than the number suggests.

3. **★ The ceiling is good; the mean is dragged by early crashes.** Best episodes hit **3 gates** (roundtrip seed 1001 = +259). The drag is ~30% of episodes crashing in <65 steps (seeds 1003/1004/1009 = 50–63 steps = down in the first ~3 s). That's **early-flight instability** — the bobbing / control-precision failure from flight #1 — NOT appearance, NOT geometry-OOD.

## EXTRACT → the bottleneck moved
- **Appearance:** SOLVED (roundtrip ≈ direct). Don't spend more on restyle/DR.
- **Geometry-OOD:** FIXED by the recalibration (it flies the wide course; best eps = 3 gates).
- **Remaining bottleneck = early-flight control stability** (≈30% sub-3s crashes cap the mean). Levers: (a) more BUDGET — only batch 4/24, the floor should rise as it trains; (b) **dt-conditioning / rate-robustness** for control precision (the supply-side fix flagged Day 137–138); blur −45% is a minor secondary (resample sensitivity).
- **A real flight test off best.pt is now worth MORE** — it won't DQ on appearance anymore, so a flight would isolate exactly the control-stability question on the real sim.

## Status / next
- Let the budget run keep training (batch 4 → ~10–12), **re-rehearse ~batch 10–12** (same WIDEGAP config) to see the early-crash floor rise. VQ2 drops 6/29 (4 days); VQ1 ~26 days.
- Flight #4 off `maneuver_vq1_v3_widegap/best.pt` w/ Clayton — `ANAKIN_WIDEGAP=1` exported for the pilot — now that appearance is solved, the flight measures control-stability cleanly.
