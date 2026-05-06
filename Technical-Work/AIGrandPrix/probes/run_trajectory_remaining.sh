#!/usr/bin/env bash
set -e
source ~/miniconda3/etc/profile.d/conda.sh
conda activate base
cd /mnt/c/Users/mercu/clawd
for STEP in 45000016 52500016 60000016 67500016; do
  echo "######## Step: $STEP ########"
  python projects/aigrandprix/probes/eval_phase2_checkpoint.py --step "$STEP"
done
echo "DONE all 4 remaining checkpoints"
