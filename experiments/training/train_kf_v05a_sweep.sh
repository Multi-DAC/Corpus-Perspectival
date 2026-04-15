#!/bin/bash
# v0.5a Lambda Sweep — Find accuracy sweet spot for KF-decoupled HRM training
#
# v0.5 (λ=1.0) achieved 38,963x H-module CV amplification but only 2.04% exact solve.
# v0.5a sweeps λ ∈ {0.001, 0.01, 0.1} to find where H_CV > 10x baseline AND accuracy competitive.
#
# Prediction: λ=0.01 is the sweet spot.
#
# Usage: bash train_kf_v05a_sweep.sh
# Runs sequentially to avoid GPU pressure. Expects base conda env activated.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="/mnt/c/Users/mercu/clawd/repo-staging/Corpus-Perspectival/train_kf_v05.py"

echo "============================================================"
echo "v0.5a LAMBDA SWEEP — KF-Decoupled HRM Training"
echo "Lambdas: 0.001, 0.01, 0.1"
echo "Each run: 2000 epochs, checkpoint every 500"
echo "Sequential execution (one at a time)"
echo "============================================================"
echo ""

for LAMBDA in 0.001 0.01 0.1; do
    SAVE_DIR="/home/clawd/HRM/checkpoints/kf_v05a_lambda_${LAMBDA}"
    echo "============================================================"
    echo "STARTING λ=${LAMBDA}"
    echo "  Save dir: ${SAVE_DIR}"
    echo "  Time: $(date)"
    echo "============================================================"

    python "$SCRIPT" \
        --kf_lambda "$LAMBDA" \
        --kf_every 50 \
        --epochs 2000 \
        --checkpoint_every 500 \
        --save_dir "$SAVE_DIR"

    # Copy trajectory with lambda-specific name (v0.5 script overwrites the generic Windows copy)
    WIN_DIR="/mnt/c/Users/mercu/clawd/projects/Corpus Perspectival"
    cp "${SAVE_DIR}/kf_trajectory_v05.json" "${WIN_DIR}/kf_trajectory_v05a_lambda_${LAMBDA}.json" 2>/dev/null || true

    echo ""
    echo "COMPLETED λ=${LAMBDA} at $(date)"
    echo "Trajectory: ${WIN_DIR}/kf_trajectory_v05a_lambda_${LAMBDA}.json"
    echo ""
done

echo "============================================================"
echo "v0.5a SWEEP COMPLETE"
echo "============================================================"
echo ""
echo "Results saved to:"
echo "  /home/clawd/HRM/checkpoints/kf_v05a_lambda_0.001/"
echo "  /home/clawd/HRM/checkpoints/kf_v05a_lambda_0.01/"
echo "  /home/clawd/HRM/checkpoints/kf_v05a_lambda_0.1/"
echo ""
echo "Trajectory files copied to Windows:"
echo "  projects/Corpus Perspectival/kf_trajectory_v05a_*.json"
echo ""
echo "Compare with:"
echo "  v0.5 (λ=1.0): 38,963x H_CV, 2.04% exact solve"
echo "  Baseline: 2.74e-3 H_CV"
