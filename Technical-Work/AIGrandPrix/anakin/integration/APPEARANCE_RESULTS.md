# Appearance-DR fine-tune — gate verdict — 2026-06-20 Day 140 (~15:00, w/ Clayton)

**Run:** `maneuver_appearance_ft` (launch_appearance_ft.py, DR+RATE+PRIV) — completed 4 batches ~13:31 today.
**Training looked flat:** eval returns batch0..3 = −17.25 → +9.79 → **+23.27 (best)** → +20.26 (regressed, kept). Day-139 watcher flagged "returns-flat."

## ★ GATE PASS (holdout_gate_v2, canonical render ANAKIN_APPEARANCE_DR=0, sealed HELDOUT official testset)
| checkpoint | mean_term (official↔rendered gap) |
|---|---|
| band-ft (baseline) | 60.37 |
| **appearance-ft (adapted)** | **24.96** |

**MEAN-TERM ratio = 0.413 < 0.5 → PASS.** The appearance-DR run **closed the official-domain appearance gap ~59%** despite flat training reward.

## Interpretation (LC47 vindicated)
PREDICT was FAIL (flat +23 training return → assumed weak). **FALSIFIED.** The flat reward was a red herring: exposure-DR on a poorly-observable parameter trades *training reward* for *transfer* — precisely LC47. The training number is not the verdict; the gate is. (Measure-before-framing / Mirror #33.)

**Caveats:** cov-term unreliable (n=20 ≤ D=4096) — verdict rests on mean-term (trustworthy any n). LC46 resolution-confound partly cancels in the adapted/baseline RATIO (same official set + rendered reference both sides).

## Next: translation_rehearsal (fly-test) — does it still FLY through the adapter path? (running)
