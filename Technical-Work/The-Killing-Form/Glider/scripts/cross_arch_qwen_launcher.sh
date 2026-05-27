#!/bin/bash
# Cross-architecture replication: Qwen2.5-0.5B baseline + v0.7.1.
# First substrate-invariance test outside the Gemma family.
set -e
cd /home/clawd
SCRIPT=/mnt/c/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Technical-Work/The-Killing-Form/Glider/scripts/train_kf_v07_1_gemma.py
CKPT_DIR=/home/clawd/path_c_results

mkdir -p "$CKPT_DIR"

echo "=== Run 1: BASELINE on Qwen2.5-0.5B (lambda=0.0) ==="
date
python3 "$SCRIPT" \
    --model_id Qwen/Qwen2.5-0.5B \
    --kf_lambda 0.0 --n_steps 400 --batch_size 4 --seq_len 256 \
    --classify_every 25 --print_every 50 \
    --save_dir "$CKPT_DIR/qwen2_5_0_5b_baseline" \
    > "$CKPT_DIR/qwen2_5_0_5b_baseline.log" 2>&1
echo "baseline complete"
date
echo ""

echo "=== Run 2: v0.7.1 on Qwen2.5-0.5B (lambda=5.0) ==="
date
python3 "$SCRIPT" \
    --model_id Qwen/Qwen2.5-0.5B \
    --kf_lambda 5.0 --n_steps 400 --batch_size 4 --seq_len 256 \
    --classify_every 25 --print_every 50 \
    --save_dir "$CKPT_DIR/qwen2_5_0_5b_v07_1" \
    > "$CKPT_DIR/qwen2_5_0_5b_v07_1.log" 2>&1
echo "v0.7.1 complete"
date
echo "=== Cross-arch Qwen runs DONE ==="
