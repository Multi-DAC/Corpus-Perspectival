# Path A seed-0 result + root-cause diagnosis (2026-05-27 Day 117)

## Result
Seed 0, easy-sudoku, batch 384, 2500 steps, baseline vs v0.6a bidirectional gating.
**Both arms: exactly 0.00% exact AND token accuracy at every eval through step 2500.**
- Baseline: H_CV decreased 1.85e-3 → 8.46e-4, H/L ratio crept 0.96 → 1.42 (textbook baseline de-differentiation).
- Gated: H/L ratio breathed UP to 2.85 (step 1875) then dissolved back to 1.32 (step 2500). **Gating mechanism worked** (build/dissolve fired, structure formed then released) — but no capability to organize.

## Root cause — CORRECTED after deeper recon (dual-optimizer was a RED HERRING)

**Initial hypothesis (WRONG):** missing dual-optimizer / warmup. Overturned by reading the *proven* KF harness.

**`train_kf_300m.py` — the historical KF-gating script that DID learn (logs show 0.48 token acc) — uses a SINGLE `AdamATan2` (no separate puzzle_emb optimizer, no warmup).** Its defaults: **`batch_size=64`, `lr=3e-5`, `epochs=3000`, `checkpoint_every=500`, `weight_decay=1.0`, betas (0.9,0.95).** So the single-optimizer setup is fine — it's not the cause.

**Actual dominant cause: UPDATE-STARVATION from large batch + too-few steps.**
- Proven harness: batch **64** → ~15.6 steps/epoch → 3000 epochs ≈ **~47,000 gradient updates**.
- My failed run: batch **384** → 2.5 steps/epoch → 2500 steps = **only 2,500 updates** (~6–18× too few).
- The model needs ~tens-of-thousands of *updates* to learn sudoku; data-seen is not the bottleneck, update-count is. At only 2500 updates, 0% is expected even with a perfect harness.
- (Aside: my "2500 steps = P49 epoch 1000" assumption was wrong — P49's epochs were small-batch epochs, ~15k–31k steps. I mis-read the epoch-accounting three times today; stop deriving step budgets, measure instead.)

**The pretrain.py dual-optimizer (CastedSparseEmbeddingSignSGD @ puzzle_emb_lr, + warmup) is the OFFICIAL recipe and likely gives the *best* final quality — but it is NOT required to learn; the single-optimizer KF harness demonstrably learns.** Keep it as a possible later optimization, not a prerequisite.

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
