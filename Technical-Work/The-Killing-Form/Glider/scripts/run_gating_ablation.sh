#!/bin/bash
# 2x2 ablation {aux} x {gating} — gate-OFF arm (gate-ON arm already exists as baseline_s137 + v07_1_s137).
# seed 137, 1600 steps, matches multi-seed config exactly except --gating 0.
cd /mnt/c/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Technical-Work/The-Killing-Form/Glider/scripts
RES=/home/clawd/path_c_results
MODEL=google/gemma-3-270m

echo "=== (aux OFF, gate OFF) lambda=0 ==="; date
python3 train_kf_v07_1_gemma.py --model_id $MODEL --kf_lambda 0.0 --n_steps 1600 --seed 137 --gating 0 \
  --save_dir $RES/gemma270m_baseline_s137_nogate > $RES/gemma270m_baseline_s137_nogate.log 2>&1
echo "   exit=$?"

echo "=== (aux ON, gate OFF) lambda=5 ==="; date
python3 train_kf_v07_1_gemma.py --model_id $MODEL --kf_lambda 5.0 --n_steps 1600 --seed 137 --gating 0 \
  --save_dir $RES/gemma270m_v07_1_s137_nogate > $RES/gemma270m_v07_1_s137_nogate.log 2>&1
echo "   exit=$?"
echo "=== GATING ABLATION TRAINING DONE ==="; date
