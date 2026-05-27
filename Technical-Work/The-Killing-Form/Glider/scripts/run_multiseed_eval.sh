#!/bin/bash
# Multi-seed topology eval — Gemma-270m, 5 seeds {71(existing),137,271,314,419} x {baseline,v0.7.1}.
# Self-synchronizes: waits for the last training checkpoint (s419 v0.7.1) before starting.
# Variables fine here (script file, not bash -lc inline).
cd /mnt/c/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Technical-Work/The-Killing-Form/Glider/scripts
RES=/home/clawd/path_c_results
OUT=/mnt/c/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Technical-Work/The-Killing-Form/results
MODEL=google/gemma-3-270m

echo "waiting for s419 v0.7.1 final checkpoint..."; date
while [ ! -f $RES/gemma270m_v07_1_s419/step_1600_final.pt ]; do sleep 10; done
sleep 8  # ensure fully flushed
echo "=== all training done; starting evals ==="; date

# seed 71 = existing Day-111 runs (best-effort; dir names lack _s suffix)
python3 eval_v07_1_generic.py --model_id $MODEL --ckpt $RES/gemma270m_baseline/step_1600_final.pt --output $OUT/ms_gemma270m_baseline_s71.json
python3 eval_v07_1_generic.py --model_id $MODEL --ckpt $RES/gemma270m_v07_1/step_1600_final.pt      --output $OUT/ms_gemma270m_v07_1_s71.json

for S in 137 271 314 419; do
  echo "--- seed $S ---"
  python3 eval_v07_1_generic.py --model_id $MODEL --ckpt $RES/gemma270m_baseline_s$S/step_1600_final.pt --output $OUT/ms_gemma270m_baseline_s$S.json
  python3 eval_v07_1_generic.py --model_id $MODEL --ckpt $RES/gemma270m_v07_1_s$S/step_1600_final.pt   --output $OUT/ms_gemma270m_v07_1_s$S.json
done
echo "=== MULTI-SEED EVAL DONE ==="; date
