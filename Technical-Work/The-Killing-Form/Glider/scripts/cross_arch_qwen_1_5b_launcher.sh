#!/bin/bash
# Cross-architecture scaling test: Qwen2.5-1.5B baseline + v0.7.1
# Tests whether v0.7.1 mechanism intensifies with scale on Qwen architecture
# (analogous to Gemma 270M 2.93x -> 1B 5.40x intensification).
set -e
cd /home/clawd
SCRIPT=/mnt/c/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Technical-Work/The-Killing-Form/Glider/scripts/train_kf_v07_1_gemma.py
CKPT_DIR=/home/clawd/path_c_results

mkdir -p "$CKPT_DIR"

echo "=== Run 1: BASELINE Qwen2.5-1.5B (lambda=0.0) ==="
date
python3 "$SCRIPT" \
    --model_id Qwen/Qwen2.5-1.5B \
    --kf_lambda 0.0 --n_steps 400 --batch_size 4 --seq_len 256 \
    --classify_every 25 --print_every 50 \
    --save_dir "$CKPT_DIR/qwen2_5_1_5b_baseline" \
    > "$CKPT_DIR/qwen2_5_1_5b_baseline.log" 2>&1
echo "baseline complete"
date
echo ""

echo "=== Run 2: v0.7.1 Qwen2.5-1.5B (lambda=5.0) ==="
date
python3 "$SCRIPT" \
    --model_id Qwen/Qwen2.5-1.5B \
    --kf_lambda 5.0 --n_steps 400 --batch_size 4 --seq_len 256 \
    --classify_every 25 --print_every 50 \
    --save_dir "$CKPT_DIR/qwen2_5_1_5b_v07_1" \
    > "$CKPT_DIR/qwen2_5_1_5b_v07_1.log" 2>&1
echo "v0.7.1 complete"
date
echo "=== Qwen 1.5B cross-arch runs DONE ==="
