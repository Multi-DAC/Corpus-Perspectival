#!/usr/bin/env bash
# A57 threshold probe — eval 5 intermediate checkpoints to pin τ.
# Predictions committed in TAU_PREDICTION.md before this script runs.
set -e
source ~/miniconda3/etc/profile.d/conda.sh
conda activate base
cd /mnt/c/Users/mercu/clawd
for STEP in 10000016 12500016 15000016 17500016 20000016; do
  echo "######## Step: $STEP ########"
  python projects/aigrandprix/probes/eval_phase2_checkpoint.py --step "$STEP"
done
echo "DONE all 5 threshold-probe checkpoints"
