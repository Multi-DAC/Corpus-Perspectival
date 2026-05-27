#!/bin/bash
# Multi-seed functional-specialization probe (mechanism #1) — Gemma-270m, 5 seeds + pristine.
cd /mnt/c/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Technical-Work/The-Killing-Form/Glider/scripts
RES=/home/clawd/path_c_results
OUT=/mnt/c/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Technical-Work/The-Killing-Form/results
MODEL=google/gemma-3-270m
python3 functional_specialization_probe.py --model_id $MODEL --output $OUT/funcspec_gemma270m_pristine.json
python3 functional_specialization_probe.py --model_id $MODEL --ckpt $RES/gemma270m_baseline/step_1600_final.pt --output $OUT/funcspec_gemma270m_baseline_s71.json
python3 functional_specialization_probe.py --model_id $MODEL --ckpt $RES/gemma270m_v07_1/step_1600_final.pt   --output $OUT/funcspec_gemma270m_v07_1_s71.json
for S in 137 271 314 419; do
  python3 functional_specialization_probe.py --model_id $MODEL --ckpt $RES/gemma270m_baseline_s$S/step_1600_final.pt --output $OUT/funcspec_gemma270m_baseline_s$S.json
  python3 functional_specialization_probe.py --model_id $MODEL --ckpt $RES/gemma270m_v07_1_s$S/step_1600_final.pt   --output $OUT/funcspec_gemma270m_v07_1_s$S.json
done
echo "=== FUNCSPEC MULTI-SEED DONE ==="; date
