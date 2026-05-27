#!/bin/bash
# v0.7 Glider first real experiment: full gradient-gating (v0.7a) vs pure-CE control (v0.7d).
# Gemma-270m, 1600 steps, seed 71. Battery-eval both + pristine after.
cd /mnt/c/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Technical-Work/The-Killing-Form/Glider/scripts
RES=/home/clawd/path_c_results

echo "=== v0.7a FULL GLIDER (gradient-gating + layer-coherence) ==="; date
python3 train_kf_v07_glider_gemma.py --variant a --kf_lambda 5.0 --kf_every 10 --n_steps 1600 --seed 71 \
  --save_dir $RES/glider_v07a_s71 > $RES/glider_v07a_s71.log 2>&1
echo "   v07a exit=$?"; date

echo "=== v0.7d CE-ONLY CONTROL ==="; date
python3 train_kf_v07_glider_gemma.py --variant ce_only --kf_lambda 0 --n_steps 1600 --seed 71 \
  --save_dir $RES/glider_v07d_s71 > $RES/glider_v07d_s71.log 2>&1
echo "   v07d exit=$?"; date

echo "=== GLIDER EXPERIMENT TRAINING DONE ==="; date
