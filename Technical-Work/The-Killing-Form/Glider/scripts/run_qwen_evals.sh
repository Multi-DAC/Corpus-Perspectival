#!/bin/bash
# Qwen2.5-0.5B cross-architecture eval batch — remaining 4 evals
# (topology on v0.7.1 already run in foreground 2026-05-26)
# Full inline paths used deliberately (no shell vars) for robustness.
set -e
cd /mnt/c/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Technical-Work/The-Killing-Form/Glider/scripts

echo "=== [1/4] Topology eval: BASELINE-trained checkpoint ==="
date
python3 eval_v07_1_generic.py --model_id Qwen/Qwen2.5-0.5B \
  --ckpt /home/clawd/path_c_results/qwen2_5_0_5b_baseline/step_400_final.pt \
  --output /mnt/c/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Technical-Work/The-Killing-Form/results/qwen2_5_0_5b_baseline_eval.json

echo "=== [2/4] Orthogonality: PRISTINE (no ckpt) ==="
date
python3 cosine_orthogonality_probing.py --model_id Qwen/Qwen2.5-0.5B \
  --output /mnt/c/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Technical-Work/The-Killing-Form/results/orthogonality_qwen0_5b_pristine.json

echo "=== [3/4] Orthogonality: BASELINE-trained ==="
date
python3 cosine_orthogonality_probing.py --model_id Qwen/Qwen2.5-0.5B \
  --ckpt /home/clawd/path_c_results/qwen2_5_0_5b_baseline/step_400_final.pt \
  --output /mnt/c/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Technical-Work/The-Killing-Form/results/orthogonality_qwen0_5b_baseline.json

echo "=== [4/4] Orthogonality: v0.7.1-trained ==="
date
python3 cosine_orthogonality_probing.py --model_id Qwen/Qwen2.5-0.5B \
  --ckpt /home/clawd/path_c_results/qwen2_5_0_5b_v07_1/step_400_final.pt \
  --output /mnt/c/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Technical-Work/The-Killing-Form/results/orthogonality_qwen0_5b_v07_1.json

echo "=== ALL QWEN CROSS-ARCH EVALS DONE ==="
date
