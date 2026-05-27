#!/bin/bash
# Self-sync battery eval for the threshold sweep (waits for thr=0.1 checkpoint).
cd /mnt/c/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Technical-Work/The-Killing-Form/Glider/scripts
RES=/home/clawd/path_c_results
OUT=/mnt/c/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Technical-Work/The-Killing-Form/results
echo "waiting for thr=0.1 checkpoint..."; date
while [ ! -f $RES/glider_v07a_thr0.1_s71/step_1600_final.pt ]; do sleep 15; done
sleep 8
echo "=== battery: thr=0.05 ==="; date
python3 geometry_battery.py --model_id google/gemma-3-270m --ckpt $RES/glider_v07a_thr0.05_s71/step_1600_final.pt --output $OUT/geometry_glider_thr0.05.json
echo "=== battery: thr=0.1 ==="; date
python3 geometry_battery.py --model_id google/gemma-3-270m --ckpt $RES/glider_v07a_thr0.1_s71/step_1600_final.pt --output $OUT/geometry_glider_thr0.1.json
echo "=== THRESHOLD-SWEEP BATTERY EVAL DONE ==="; date
