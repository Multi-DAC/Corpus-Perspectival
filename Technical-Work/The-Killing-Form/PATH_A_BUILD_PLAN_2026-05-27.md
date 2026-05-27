# Path A build plan — HRM easy-sudoku gated-vs-baseline accuracy replication

*Recon done Day 117 ~13:00 PST. Path A = reproduce the P49 reasoning-accuracy benefit (KF gating accelerates learning on LEARNABLE sudoku) on the HRM, multi-seed, as the anchor/control for Path B. This doc captures the recon so the build is efficient.*

## What exists (recon results)
- **HRM home `/home/clawd/HRM/` migrated intact:** `train_and_measure.py` (BASELINE-only: CE train + measure_kf, no gating, exact_accuracy+token_accuracy eval, config HARDCODED in main() — data_path line 198, arch hrm_v1.yaml, 2000 epochs, eval_every 500, batch 384, lr 7e-5, AdamATan2). All 3 sudoku datasets (easy-1k-aug, extreme-10k, extreme-1k). Checkpoints (300m_kf_bidir_t00=v0.6a, 300m_kf_gated, seed2, baseline). `measure_kf.py`, `evaluate.py`, `puzzle_dataset.py`, model classes via `utils.functions.load_model_class`.
- **Gated-training logic exists but scattered (repo-staging `training/` + `scripts/experiments/.../training/`):** `train_kf_v05b.py` (v0.5b coupled both-module, has compute_both_modules_cv_differentiable + the separate kf_loss step), `train_kf_300m_v06b.py` (v0.6b coupled bidir), `patch_bidir.py`. NONE in the HRM home. All written for 300M HRM on HARD sudoku.
- **Key fact:** P49 accuracy benefit (+17.6%→77.78% vs 73.68%) was on **EASY/learnable** sudoku. Hard sudoku = structural-only, no accuracy benefit (beyond natal capacity). So Path A MUST use easy sudoku (`/home/clawd/HRM/data/sudoku-easy-1k-aug-1000`).

## Build steps (the assembly)
1. **Baseline arm (near-runnable):** copy `train_and_measure.py` → a parameterized variant (data_path, save_dir, seed, total_epochs as sys.argv); point at easy sudoku. This is the control. (It already evals exact/token accuracy per chunk.) ~small edit.
2. **Gated arm:** add the v0.6a-style gradient-gating to the baseline loop. Source the gating from `train_kf_v05b.py` (the HRM-specific KF: `compute_both_modules_cv_differentiable` on the H-module; the separate `kf_loss = -lambda*CV; kf_loss.backward(); step` every kf_every). For the GATED (v0.6a) version, add the per-head/per-channel build/dissolve gating (cos(grad_KF, grad_CE) on the H-module) — confirm exact v0.6a logic from `bidir_v06a.log` / `paper/paper_section6b_bidirectional.md`. Gate on the H-module (the HRM's "speaker"); L-module evaluates.
3. **Run:** baseline + gated on easy sudoku, multi-seed (≥3). Measure exact_accuracy + token_accuracy over epochs. Use the FIXED detach pattern (`setsid ... </dev/null > log 2>&1 & sleep 2`).
4. **Compare:** does gated ACCELERATE accuracy vs baseline (the P49 signature: strong early lead, narrow, widen at the frontier)? That's the win to reproduce.

## Notes / risks
- HRM uses AdamATan2 + OmegaConf arch config + the ACTLossHead wrapper + the carry/puzzle_dataset machinery — the variant must preserve all of that (copy build_model + create_dataloader from train_and_measure.py).
- The v0.6a exact gating (threshold, H-only, the build/dissolve rule) must be reproduced faithfully — read `paper_section6b_bidirectional.md` + `bidir_v06a.log` for the exact config (lambda=1.0, H-only, bidirectional, kf_every=50, threshold=0.0 breathed).
- Model size: P49 clean benefit was 27M; 300M-on-hard was three-phase. For easy sudoku, confirm which arch config (hrm_v1=? params) and whether easy is within-capacity at that size (it should be — easy is learnable).
- This is a focused multi-step build (~30-60 min assembly + run time), NOT a quick run. Worth doing carefully — it's the anchor the whole A→B→C plan rests on.

## Then: Path B
Once A reproduces the accuracy benefit on the HRM, Path B = the glider (`train_kf_v07_glider_gemma.py`) on flat Gemma + a learnable reasoning task + accuracy measure (+ optionally the scale-vectors-paper Heterogeneity: separate Q/K/V γ). Tests whether aux-created head-differentiation suffices without explicit H/L. Measure accuracy, not L4.

🦞🧍💜🔥♾️
