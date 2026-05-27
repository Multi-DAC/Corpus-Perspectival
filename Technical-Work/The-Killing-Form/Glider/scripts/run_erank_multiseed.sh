#!/bin/bash
# Multi-seed effective-rank probe (mechanism #3) — Gemma-270m, 5 seeds x {baseline,v0.7.1} + pristine.
# Tests whether the readout-layer effective-rank gap (v0.7.1 > baseline) survives across seeds.
cd /mnt/c/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Technical-Work/The-Killing-Form/Glider/scripts
RES=/home/clawd/path_c_results
OUT=/mnt/c/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Technical-Work/The-Killing-Form/results
MODEL=google/gemma-3-270m

python3 effective_rank_probe.py --model_id $MODEL --output $OUT/erank_gemma270m_pristine.json
python3 effective_rank_probe.py --model_id $MODEL --ckpt $RES/gemma270m_baseline/step_1600_final.pt --output $OUT/erank_gemma270m_baseline_s71.json
python3 effective_rank_probe.py --model_id $MODEL --ckpt $RES/gemma270m_v07_1/step_1600_final.pt   --output $OUT/erank_gemma270m_v07_1_s71.json
for S in 137 271 314 419; do
  python3 effective_rank_probe.py --model_id $MODEL --ckpt $RES/gemma270m_baseline_s$S/step_1600_final.pt --output $OUT/erank_gemma270m_baseline_s$S.json
  python3 effective_rank_probe.py --model_id $MODEL --ckpt $RES/gemma270m_v07_1_s$S/step_1600_final.pt   --output $OUT/erank_gemma270m_v07_1_s$S.json
done
echo "=== ERANK MULTI-SEED DONE ==="; date
