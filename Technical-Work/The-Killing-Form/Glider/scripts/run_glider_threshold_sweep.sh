#!/bin/bash
# Glider threshold sweep: give v0.7a the neutral buffer it lacked at threshold=0.
# v07_design: the neutral zone is the buffer the glider oscillates in; threshold=0 (N always 0)
# may have killed it. Sweep 0.05, 0.1. Gemma-270m, 1600 steps, seed 71 (matches the thr=0 run).
cd /mnt/c/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Technical-Work/The-Killing-Form/Glider/scripts
RES=/home/clawd/path_c_results
for TH in 0.05 0.1; do
  echo "=== v0.7a threshold=$TH ==="; date
  python3 train_kf_v07_glider_gemma.py --variant a --kf_lambda 5.0 --kf_every 10 --gate_threshold $TH \
    --n_steps 1600 --seed 71 --save_dir $RES/glider_v07a_thr${TH}_s71 > $RES/glider_v07a_thr${TH}_s71.log 2>&1
  echo "   thr=$TH exit=$?"; date
done
echo "=== THRESHOLD SWEEP DONE ==="; date
