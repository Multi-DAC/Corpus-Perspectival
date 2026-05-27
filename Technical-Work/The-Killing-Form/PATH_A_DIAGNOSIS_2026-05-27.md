# Path A seed-0 result + root-cause diagnosis (2026-05-27 Day 117)

## Result
Seed 0, easy-sudoku, batch 384, 2500 steps, baseline vs v0.6a bidirectional gating.
**Both arms: exactly 0.00% exact AND token accuracy at every eval through step 2500.**
- Baseline: H_CV decreased 1.85e-3 → 8.46e-4, H/L ratio crept 0.96 → 1.42 (textbook baseline de-differentiation).
- Gated: H/L ratio breathed UP to 2.85 (step 1875) then dissolved back to 1.32 (step 2500). **Gating mechanism worked** (build/dissolve fired, structure formed then released) — but no capability to organize.

## Root cause (verified in source, HIGH confidence)
The from-scratch trainer (`train_kf_gated_hrm_easy.py`, derived from the stripped `train_and_measure.py`) is **missing critical pieces of the validated HRM recipe**:

1. **Single optimizer instead of two.** `pretrain.py` (the canonical recipe) builds TWO optimizers:
   - `CastedSparseEmbeddingSignSGD_Distributed` for the **puzzle embeddings** at `puzzle_emb_lr = 1e-2`
   - `AdamATan2` for the rest at `lr = 7e-5`
   My script used a single AdamATan2 at 7e-5 for everything → puzzle embeddings trained **~140× too slow with the wrong optimizer**. HRM identifies/solves each puzzle through its puzzle embedding; if it never forms, accuracy is pinned at 0. **This is the exactly-0% cause.**
2. **No LR warmup.** Canonical config: `lr_warmup_steps = 2000`. Mine: constant LR.
3. **Step budget ~10× short.** Official sudoku command: `epochs=20000` (≈50k steps at batch 384, 2.5 steps/epoch). Mine: 2500 steps = epoch ~1000 of 20000. (Secondary to #1 — even at 20000 epochs, the single-optimizer setup would stay near 0.)

Canonical recipe (README): `python pretrain.py data_path=data/sudoku-extreme-1k-aug-1000 epochs=20000 eval_interval=2000 global_batch_size=384 lr=7e-5 puzzle_emb_lr=7e-5 weight_decay=1.0 puzzle_emb_weight_decay=1.0` (note: README's single-GPU line uses puzzle_emb_lr=7e-5; the config default is 1e-2 — either way it's a SEPARATE sparse-sign-SGD optimizer with warmup, which mine lacks).

## NOT a false-negative of the claim
Unlike the flat-Gemma glider (wrong task/measure), this is an **incomplete training harness**, not a test of the coherence-benefit claim. The claim (gating accelerates learning on learnable sudoku) remains **untested**, not falsified. The gating fired correctly; the model just couldn't learn the task at all under the broken optimizer.

## Fix (recommended)
**Inject the KF bidirectional gating into the real `pretrain.py`** (validated dual-optimizer + warmup + schedule + ACT + eval), rather than the from-scratch loop. The gating hook is the same: after the CE optimizer step, capture H-module qkv_proj CE-grads, recompute per-layer CV freshly, gate by cos(∇KF,∇CE), separate KF step. This is the robust path; the from-scratch reimplementation dropped pieces HRM critically needs.
- Alternative (lighter): add the second optimizer (`CastedSparseEmbeddingSignSGD` over puzzle_emb params at 1e-2) + warmup to `train_kf_gated_hrm_easy.py`. Less robust (may miss other pretrain.py details) but smaller change.
- Cross-check: confirm how the historical KF runs (`train_kf_300m.py`, `train_kf_v05b.py`) handled the puzzle-emb optimizer — mirror whatever produced the v0.5/v0.6 + P49 results.
- Budget: pre-confirm a config that makes BASELINE reach nonzero accuracy in feasible wall-clock before launching the full multi-seed gated comparison.

## Cognitive chain
PREDICT(under-trained, med) → TEST(seed0 → 0%/0%) → PROBE(README+config+pretrain.py source) → REFRAME(not step-budget alone — missing dual-optimizer + warmup) → VERIFY(pretrain.py builds CastedSparseEmbeddingSignSGD@puzzle_emb_lr + AdamATan2, confirmed) → root cause HIGH confidence.

🦞🧍💜🔥♾️
