# holdout_gate_v2 — first robust official-domain measurement (Day 134, 2026-06-14)

**Unblock:** Clayton flew two manual frame-harvest runs in the official sim this morning
(`PyAIPilotExample/official_frames/manual_20260614_113648/` = 1,759 frames,
`manual_20260614_114130/` = 1,783 frames; raw 640×360 RGB JPEGs, ~182 MB, real TRON-style
official world — monochrome block cityscape, blue ribbon distractor, orange-red gates).
This is the appearance signal flight #1's spin-out (anomaly I, appearance-OOD) needed.

**Run:**
```
.venv/Scripts/python.exe integration/holdout_gate_v2.py \
  --official-dir ".../manual_20260614_114130" --official-raw
```
400 official frames (cap) vs 200 fresh restyled renders, embedded through each world model.

**Result (mean-term = trustworthy at any n; D=4096 so cov-term flagged unreliable, n<=D):**

| checkpoint | mean_term | cov_term (noisy) | total |
|---|---|---|---|
| band-ft (`maneuver_band_ft/best.pt`, +2142.53) | **24.44** | 47.03 | 71.47 |
| restyle-ft (`maneuver_restyle_ft/best.pt`)      | **31.52** | 62.61 | 94.13 |

**MEAN-TERM ratio (restyle/band) = 1.290 → VERDICT: FAIL.**

## What it means
- The overnight n=20 reading (ratio 1.063) is now confirmed at robust n=400 — and sharper.
- **ratio > 1**: the restyle-toward-MEASURED-palette checkpoint is *farther* from the official
  domain than the plain band-ft base. The restyle adaptation moved the embedding the **wrong
  direction**. Our hand-measured palette ≠ the official appearance distribution.
- **band-ft `best.pt` is the better base for official transfer.** Abandon the measured-palette
  restyle branch as a transfer strategy.

## Next (P228 — "domain-randomize first", now data-grounded)
We finally have official frames to adapt *toward* instead of guessing a palette. Disciplined path
(measure before spending the training run):
1. Build a domain-randomization augmentation over the *training* renderer (randomize gate hue,
   lighting, ribbon, block textures/contrast — wide, not matched to one target).
2. **Pre-validate with this same gate before any retrain:** embed official-harvest vs
   DR-augmented frames; require DR mean-term gap < band-ft's 24.44 (DR should *cover* official,
   unlike the palette restyle which missed it).
3. Only if the augmentation passes the gate, fine-tune the policy under DR off band-ft `best.pt`.

Interpretation caveat: the gate measures official↔restyled-renderer gap as a proxy for
official↔training-distribution. Headline (restyle worse than base) is robust regardless; treat the
absolute mean-term values as a relative instrument, not a calibrated distance.
