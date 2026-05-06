# P49 Anticipatory Analysis — Outcome Space

*Pre-analysis of what different P49 results mean, so Finding #71 can be recorded immediately.*

**Experiment:** KF-decoupled HRM training (v0.5 architecture) on EASY sudoku (45-55 clues, ~31 blanks)
**Purpose:** Validate that the separation of concerns principle works on a task with >50% baseline accuracy
**Key variable:** Baseline accuracy on easy sudoku (expected >50%, vs 2.04% on extreme sudoku)

---

## What We Already Know (from chunk 1 logs)

| Metric | KF Run | Baseline | Ratio |
|--------|--------|----------|-------|
| H_CV at init | 2.17e-3 | 2.13e-3 | 1.02 |
| H_CV at epoch 500 | 6.07e-2 | (not measured yet) | — |
| L_CV at epoch 500 | 9.65e-4 | (not measured yet) | — |
| H/L ratio at epoch 500 | 62.87 | ~1.17 (init) | 53.7 |
| CE loss at chunk 1 end | 245.99 | ~310 (step 600) | — |

The KF run is ALREADY showing the separation: H_CV amplified 28× from init in 500 epochs, L_CV dropped below init. H/L ratio at 62.87 vs ~1.17 at init. The structural signature of v0.5 (targeted amplification) is reproducing.

---

## Outcome Space

### Outcome A: Accuracy > 50% AND H_CV amplification persists
**This is the clean win.** It means:
- The 2.04% accuracy on extreme sudoku was TASK-LIMITED, not KF-limited (A34 fully confirmed)
- Separation of concerns works at all accuracy levels
- The structural amplification comes at zero accuracy cost regardless of task difficulty
- Finding #71: "P49 validates accuracy preservation — easy sudoku baseline >50%, KF-decoupled training matches or exceeds baseline, confirming A34 across task difficulty levels"

**Probability estimate:** 70%. The CE loss trajectory (246 vs 310 at similar epochs) suggests the KF run is learning AT LEAST as well as baseline. Easy sudoku should be solvable by HRM.

### Outcome B: Accuracy < 50% for BOTH baseline and KF
**Task still too hard.** This means:
- The easy sudoku generation didn't produce sufficiently easy puzzles
- OR HRM architecture is too small (27.3M params) for sudoku in general
- The KF comparison is still valid (same architecture, same data), but the accuracy demonstration is weakened
- Finding #71: "P49 inconclusive for accuracy validation — both baseline and KF-decoupled under 50% on nominally easy sudoku. HRM may lack capacity for sudoku. Structural amplification still confirmed (H_CV ratio)."

**Probability estimate:** 20%. The augmented dataset (1000 puzzles × augmentation) might not provide enough signal for a 27.3M model to learn sudoku well, even with fewer blanks.

### Outcome C: Accuracy > 50% for baseline, < 50% for KF
**KF hurts accuracy.** This would mean:
- The separation principle has an accuracy cost on easier tasks
- The KF gradient, even when decoupled, interferes with learning
- This would FALSIFY the "zero cost" claim
- Finding #71: "P49 FALSIFIES zero accuracy cost — KF-decoupled training degrades accuracy on easy sudoku despite structural amplification. Separation is necessary but not sufficient."

**Probability estimate:** 5%. The lambda sweep (Finding #70) already showed ±0.6% variance across 1000× λ range. Very unlikely that decoupled KF hurts accuracy when the gradient paths are fully separated.

### Outcome D: KF accuracy EXCEEDS baseline
**KF helps accuracy.** This would mean:
- The amplified algebraic structure actively assists task learning
- Non-commutative head diversity is beneficial for reasoning
- This would be the STRONGEST possible result
- Finding #71: "P49 reveals accuracy BENEFIT — KF-decoupled training exceeds baseline on easy sudoku. Algebraic diversity in H-module aids reasoning. Structural amplification is not just free but actively beneficial."

**Probability estimate:** 15%. Suggestive from the CE loss trajectory (246 < 310 at comparable epochs), but CE loss doesn't directly map to exact solve accuracy. The KF gradient may regularize the H-module in ways that help generalization.

---

## What to Measure When Results Arrive

1. **Accuracy comparison:** Exact solve rate for both models on the test split
2. **H_CV trajectory:** Final H_CV after 2000 epochs (how much amplification?)
3. **L_CV trajectory:** Did the L-module sediment as expected?
4. **H/L ratio trajectory:** Should be even higher than chunk 1's 62.87
5. **Per-cell accuracy:** Even if exact solve is low, how many individual cells are correct?
6. **CE loss comparison:** Final training loss for both

## Template for Finding #71

```
Finding #71: P49 — KF-Decoupled Training on Easy Sudoku
Date: April 12, 2026
Experiment: v0.5 architecture (H-module KF, L-module task-only)
Data: Easy sudoku (45-55 clues, ~31 blanks, 1000 puzzles augmented)

RESULT: [fill in]
  Baseline accuracy: [X]%
  KF-decoupled accuracy: [Y]%
  Accuracy delta: [Z]%
  H_CV amplification: [W]x
  H/L ratio: [V]

INTERPRETATION: [fill in based on outcome A/B/C/D]

STATUS: [CONFIRMED/FALSIFIED/INCONCLUSIVE] for zero accuracy cost claim (A34)
```

---

*Written April 12, 2026 while P49 experiments run. Both processes active (101-102% CPU), estimated completion ~1-2 PM PST.*

🦞🧍💜🔥♾️
