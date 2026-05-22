#!/bin/bash
# Alignment-axis orchestrator: waits for capability orchestrator to finish,
# then runs cosine-orthogonality probing on pristine, baseline, v0.7.1 1b.
set -e
RESULTS=/mnt/c/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Technical-Work/The-Killing-Form/results
BASELINE_HF=/home/clawd/path_c_results/gemma3_1b_baseline_hf
V071_CKPT=/home/clawd/path_c_results/gemma3_1b_v07_1/step_400_final.pt
SCRIPTS=/mnt/c/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Technical-Work/The-Killing-Form/Glider/scripts
CAP_LOG=/home/clawd/path_c_results/capability_orchestrator.log

echo "=== Alignment orchestrator started ==="
date
echo "Waiting for capability orchestrator to finish (looking for 'ALL EVALS COMPLETE' in $CAP_LOG)..."
while ! grep -q "ALL EVALS COMPLETE" "$CAP_LOG" 2>/dev/null; do
    sleep 60
done
echo "Capability eval complete; GPU free. Starting orthogonality probing."
date

echo ""
echo "=== Orthogonality: pristine 1b ==="
python3 "$SCRIPTS/cosine_orthogonality_probing.py" \
    --model_id google/gemma-3-1b-pt \
    --output "$RESULTS/orthogonality_1b_pristine.json" \
    2>&1 | tee "$RESULTS/orthogonality_1b_pristine.log"

echo ""
echo "=== Orthogonality: baseline 1b ==="
python3 "$SCRIPTS/cosine_orthogonality_probing.py" \
    --model_id google/gemma-3-1b-pt \
    --ckpt /home/clawd/path_c_results/gemma3_1b_baseline/step_400_final.pt \
    --output "$RESULTS/orthogonality_1b_baseline.json" \
    2>&1 | tee "$RESULTS/orthogonality_1b_baseline.log"

echo ""
echo "=== Orthogonality: v0.7.1 1b ==="
python3 "$SCRIPTS/cosine_orthogonality_probing.py" \
    --model_id google/gemma-3-1b-pt \
    --ckpt "$V071_CKPT" \
    --output "$RESULTS/orthogonality_1b_v07_1.json" \
    2>&1 | tee "$RESULTS/orthogonality_1b_v07_1.log"

echo ""
echo "=== ALIGNMENT PROBING COMPLETE ==="
date
