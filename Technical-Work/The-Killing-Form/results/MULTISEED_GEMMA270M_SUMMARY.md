# Multi-seed robustness — Gemma-3-270m, v0.7.1 vs baseline (sprint item #2)

**Date:** 2026-05-26 (Day 116). Training (4 new seeds) + eval (5 seeds) this evening; seed 71 = existing Day-111 run (reproducibility anchor).
**Config:** 1600 steps, batch 4, lr 2e-5, classify_every 25, seq_len 256, n_samples 500. Baseline λ=0; v0.7.1 λ=5. `--seed` arg added to `train_kf_v07_1_gemma.py` (default 71 preserves prior reproducibility).

## Result — the v0.7.1 effect is near-deterministic; "lucky seed?" closed

Mean head-separation ratio (trained mean_separation ÷ pristine mean_separation):

| seed | baseline | v0.7.1 | v0.7.1 cv-ratio |
|---|---|---|---|
| 71 (Day-111 anchor) | 0.999 | 2.924 | 6.09 |
| 137 | 0.998 | 2.880 | 5.96 |
| 271 | 0.999 | 2.890 | 5.96 |
| 314 | 0.999 | 2.903 | 6.02 |
| 419 | 0.998 | 2.870 | 5.92 |

| metric | baseline | v0.7.1 |
|---|---|---|
| **sep-ratio mean ± std (n=5)** | **0.999 ± 0.000** | **2.893 ± 0.019** |
| sep-ratio range | [0.998, 0.999] | [2.870, 2.924] |
| cv-ratio mean ± std | — | 5.988 ± 0.061 |

- **No distributional overlap:** baseline max (0.999) << v0.7.1 min (2.870). Architecture-attributable gap = 1.895.
- **v0.7.1 coefficient of variation ≈ 0.66%** — the effect is near-deterministic, not a seed lottery.
- **Baseline produces zero decomposition across all seeds** (~1.00x) — confirms the Day-111 HRM finding (decomposition is v0.7.1-specific) is seed-invariant.
- **Seed-71 reproduces the Day-111 result** (2.924 ≈ recorded 2.93x) — reproducibility anchor holds.

## Evidence grade

- **Moat-grade on the robustness axis (Gemma-270m):** the "lucky seed?" objection is closed; the effect is a near-deterministic property of v0.7.1.
- Combined with same-day **cross-architecture** confirmation (Gemma → Qwen2, `qwen2_5_0_5b_CROSS_ARCH_SUMMARY.md`), the v0.7.1 mechanism now has both robustness (multi-seed) and breadth (cross-family) evidence.
- Remaining for fuller moat-grade: multi-seed at 1b scale; multi-seed on the cross-architecture family (Qwen); orthogonality-axis multi-seed (this batch covered the topology axis).

**Files:** `ms_gemma270m_{baseline,v07_1}_s{71,137,271,314,419}.json` (10 topology evals). Scripts: `run_multiseed_gemma270m.sh` (training), `run_multiseed_eval.sh` (self-synchronizing eval), `agg_multiseed.py` (aggregation). Checkpoints at `/home/clawd/path_c_results/gemma270m_{baseline,v07_1}_s{SEED}/step_1600_final.pt`.

🦞🧍💜🔥♾️
