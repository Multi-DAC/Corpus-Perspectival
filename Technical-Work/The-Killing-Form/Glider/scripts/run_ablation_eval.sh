#!/bin/bash
# Self-synchronizing eval for the gate-OFF arm of the 2x2 ablation.
# Waits for the last gate-off checkpoint, then runs topology + orthogonality on both.
cd /mnt/c/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Technical-Work/The-Killing-Form/Glider/scripts
RES=/home/clawd/path_c_results
OUT=/mnt/c/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Technical-Work/The-Killing-Form/results
MODEL=google/gemma-3-270m

echo "waiting for v07_1_s137_nogate final checkpoint..."; date
while [ ! -f $RES/gemma270m_v07_1_s137_nogate/step_1600_final.pt ]; do sleep 10; done
sleep 8
echo "=== gate-off training done; evaluating ==="; date

# (aux OFF, gate OFF)
python3 eval_v07_1_generic.py --model_id $MODEL --ckpt $RES/gemma270m_baseline_s137_nogate/step_1600_final.pt --output $OUT/ms_gemma270m_baseline_s137_nogate_eval.json
python3 cosine_orthogonality_probing.py --model_id $MODEL --ckpt $RES/gemma270m_baseline_s137_nogate/step_1600_final.pt --output $OUT/ms_orth_gemma270m_baseline_s137_nogate.json
# (aux ON, gate OFF)
python3 eval_v07_1_generic.py --model_id $MODEL --ckpt $RES/gemma270m_v07_1_s137_nogate/step_1600_final.pt --output $OUT/ms_gemma270m_v07_1_s137_nogate_eval.json
python3 cosine_orthogonality_probing.py --model_id $MODEL --ckpt $RES/gemma270m_v07_1_s137_nogate/step_1600_final.pt --output $OUT/ms_orth_gemma270m_v07_1_s137_nogate.json

echo "=== ABLATION EVAL DONE ==="; date
