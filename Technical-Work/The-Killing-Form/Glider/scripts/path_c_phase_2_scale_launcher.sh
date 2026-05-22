#!/bin/bash
# Path C Phase 2 scale launcher: gemma-3-1b-pt + gemma-2-2b
# Sequential, baseline-skipped (pristine = baseline ref per Phase 1 finding)
set -e
cd /home/clawd
SCRIPT=/mnt/c/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Technical-Work/The-Killing-Form/Glider/scripts/train_kf_v07_1_gemma.py
CKPT_DIR=/home/clawd/path_c_results

mkdir -p "$CKPT_DIR"

echo "=== Run 1: v0.7.1 on gemma-3-1b-pt (1.1B params, 26L, 4H) ==="
date
python3 "$SCRIPT" \
    --model_id google/gemma-3-1b-pt \
    --kf_lambda 5.0 --n_steps 400 --batch_size 4 --seq_len 256 \
    --classify_every 25 --print_every 50 \
    --save_dir "$CKPT_DIR/gemma3_1b_v07_1" \
    > "$CKPT_DIR/gemma3_1b_v07_1.log" 2>&1
echo "1b complete"
date
echo ""

echo "=== Run 2: v0.7.1 on gemma-2-2b (2.5B params, 18L, 8H) ==="
date
# 2b uses batch_size=2 + seq_len=128 to fit VRAM
python3 "$SCRIPT" \
    --model_id google/gemma-2-2b \
    --kf_lambda 5.0 --n_steps 400 --batch_size 2 --seq_len 128 \
    --classify_every 25 --print_every 50 \
    --save_dir "$CKPT_DIR/gemma2_2b_v07_1" \
    > "$CKPT_DIR/gemma2_2b_v07_1.log" 2>&1
echo "2b complete"
date
echo "=== Phase 2 scale runs DONE ==="
