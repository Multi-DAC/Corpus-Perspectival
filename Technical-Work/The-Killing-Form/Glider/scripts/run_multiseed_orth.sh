#!/bin/bash
# Multi-seed ORTHOGONALITY (alignment axis) — Gemma-270m, 5 seeds x {pristine,baseline,v0.7.1}.
# Extends tonight's topology-axis robustness result to the orthogonality (alignment) axis.
cd /mnt/c/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Technical-Work/The-Killing-Form/Glider/scripts
RES=/home/clawd/path_c_results
OUT=/mnt/c/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Technical-Work/The-Killing-Form/results
MODEL=google/gemma-3-270m

echo "=== pristine ==="; date
python3 cosine_orthogonality_probing.py --model_id $MODEL --output $OUT/ms_orth_gemma270m_pristine.json

echo "=== seed 71 (existing) ==="
python3 cosine_orthogonality_probing.py --model_id $MODEL --ckpt $RES/gemma270m_baseline/step_1600_final.pt --output $OUT/ms_orth_gemma270m_baseline_s71.json
python3 cosine_orthogonality_probing.py --model_id $MODEL --ckpt $RES/gemma270m_v07_1/step_1600_final.pt   --output $OUT/ms_orth_gemma270m_v07_1_s71.json

for S in 137 271 314 419; do
  echo "=== seed $S ==="
  python3 cosine_orthogonality_probing.py --model_id $MODEL --ckpt $RES/gemma270m_baseline_s$S/step_1600_final.pt --output $OUT/ms_orth_gemma270m_baseline_s$S.json
  python3 cosine_orthogonality_probing.py --model_id $MODEL --ckpt $RES/gemma270m_v07_1_s$S/step_1600_final.pt   --output $OUT/ms_orth_gemma270m_v07_1_s$S.json
done
echo "=== ORTH MULTI-SEED DONE ==="; date
