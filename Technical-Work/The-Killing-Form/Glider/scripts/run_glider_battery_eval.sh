#!/bin/bash
# Self-syncing Geometry Battery eval for the glider experiment.
# Waits for the v0.7d checkpoint (last to finish), then measures v0.7a, v0.7d (+ pristine ref).
cd /mnt/c/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Technical-Work/The-Killing-Form/Glider/scripts
RES=/home/clawd/path_c_results
OUT=/mnt/c/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Technical-Work/The-Killing-Form/results
echo "waiting for v07d final checkpoint..."; date
while [ ! -f $RES/glider_v07d_s71/step_1600_final.pt ]; do sleep 15; done
sleep 8
echo "=== battery: v0.7a FULL GLIDER ==="; date
python3 geometry_battery.py --model_id google/gemma-3-270m --ckpt $RES/glider_v07a_s71/step_1600_final.pt --output $OUT/geometry_glider_v07a.json
echo "=== battery: v0.7d CE-ONLY CONTROL ==="; date
python3 geometry_battery.py --model_id google/gemma-3-270m --ckpt $RES/glider_v07d_s71/step_1600_final.pt --output $OUT/geometry_glider_v07d.json
echo "=== GLIDER BATTERY EVAL DONE (compare vs geometry_report_gemma270m_pristine.json) ==="; date
