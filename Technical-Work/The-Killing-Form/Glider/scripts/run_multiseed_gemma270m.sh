#!/bin/bash
# Multi-seed robustness — Gemma-3-270m, v0.7.1 vs baseline.
# 4 NEW seeds; combined with existing Day-111 seed-71 run = 5 seeds for analysis.
# Config matches Day-111: 1600 steps, batch 4, lr 2e-5, classify_every 25.
# No `set -e`: a single transient failure should not kill the whole ~48 min batch.
cd /mnt/c/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Technical-Work/The-Killing-Form/Glider/scripts
RESULTS=/home/clawd/path_c_results
MODEL=google/gemma-3-270m
STEPS=1600

for S in 137 271 314 419; do
  echo "=== SEED $S BASELINE (lambda=0) ==="; date
  python3 train_kf_v07_1_gemma.py --model_id $MODEL --kf_lambda 0.0 --n_steps $STEPS --seed $S \
    --save_dir $RESULTS/gemma270m_baseline_s$S > $RESULTS/gemma270m_baseline_s$S.log 2>&1
  echo "   baseline s$S exit=$?"

  echo "=== SEED $S v0.7.1 (lambda=5) ==="; date
  python3 train_kf_v07_1_gemma.py --model_id $MODEL --kf_lambda 5.0 --n_steps $STEPS --seed $S \
    --save_dir $RESULTS/gemma270m_v07_1_s$S > $RESULTS/gemma270m_v07_1_s$S.log 2>&1
  echo "   v0.7.1 s$S exit=$?"
done
echo "=== MULTI-SEED TRAINING DONE ==="; date
