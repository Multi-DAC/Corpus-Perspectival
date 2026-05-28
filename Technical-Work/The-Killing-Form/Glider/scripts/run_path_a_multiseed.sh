#!/bin/bash
# Path A multi-seed sweep — HRM easy-sudoku baseline vs bidirectional-gated (STEP-BASED).
# Runs {baseline, gated} x SEEDS sequentially on the single GPU.
# Launch DETACHED:  setsid bash run_path_a_multiseed.sh </dev/null > LAUNCHER.log 2>&1 & sleep 2
set -u

PY=/home/clawd/miniconda3/bin/python3
SCRIPT=/mnt/c/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Technical-Work/The-Killing-Form/Glider/scripts/train_kf_gated_hrm_easy.py
DATA=/home/clawd/HRM/data/sudoku-easy-1k-aug-1000
OUT=/home/clawd/path_a_results
mkdir -p "$OUT"

# Proven config (train_kf_300m defaults): batch 64, lr 3e-5, single AdamATan2.
MAX_STEPS=${MAX_STEPS:-15000}
EVAL_STEPS=${EVAL_STEPS:-1000}
EVAL_BATCHES=${EVAL_BATCHES:-10}
LOG_EVERY=${LOG_EVERY:-200}
BATCH=${BATCH:-64}
LR=${LR:-3e-5}
SEEDS=${SEEDS:-"0 1 2"}

cd /home/clawd/HRM
echo "Path A sweep START $(date)  max_steps=$MAX_STEPS eval_steps=$EVAL_STEPS seeds=$SEEDS"

for SEED in $SEEDS; do
  echo "=== baseline seed $SEED  START $(date) ==="
  "$PY" "$SCRIPT" --data_path "$DATA" --save_dir "$OUT/easy_baseline_s$SEED" \
      --seed "$SEED" --batch_size "$BATCH" --lr "$LR" \
      --max_steps "$MAX_STEPS" --eval_steps "$EVAL_STEPS" \
      --eval_batches "$EVAL_BATCHES" --log_every "$LOG_EVERY" \
      --gating none > "$OUT/easy_baseline_s$SEED.log" 2>&1
  echo "=== baseline seed $SEED  DONE $(date) ==="

  echo "=== gated seed $SEED  START $(date) ==="
  "$PY" "$SCRIPT" --data_path "$DATA" --save_dir "$OUT/easy_gated_s$SEED" \
      --seed "$SEED" --batch_size "$BATCH" --lr "$LR" \
      --max_steps "$MAX_STEPS" --eval_steps "$EVAL_STEPS" \
      --eval_batches "$EVAL_BATCHES" --log_every "$LOG_EVERY" \
      --gating bidirectional --kf_lambda 1.0 --kf_every 50 --kf_threshold 0.0 \
      > "$OUT/easy_gated_s$SEED.log" 2>&1
  echo "=== gated seed $SEED  DONE $(date) ==="
done

echo "Path A sweep DONE $(date)"
