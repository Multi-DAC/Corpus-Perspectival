#!/bin/bash
# Path C Phase 1: launch baseline + KF-gated training pair sequentially
set -e
cd /home/clawd
SCRIPT=/mnt/c/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Technical-Work/The-Killing-Form/Glider/scripts/train_kf_v07_gemma.py
CKPT_DIR=/home/clawd/path_c_results

mkdir -p "$CKPT_DIR"

echo "=== Run 1: BASELINE (kf_lambda=0) ==="
date
python3 "$SCRIPT" --kf_lambda 0.0 --n_steps 1600 --batch_size 4 --seq_len 256 \
    --classify_every 50 --print_every 100 \
    --save_dir "$CKPT_DIR/gemma270m_baseline" \
    > "$CKPT_DIR/gemma270m_baseline.log" 2>&1
echo "Baseline complete"
date
echo ""

echo "=== Run 2: KF-GATED v0.7 (kf_lambda=1.0) ==="
date
python3 "$SCRIPT" --kf_lambda 1.0 --n_steps 1600 --batch_size 4 --seq_len 256 \
    --classify_every 50 --print_every 100 \
    --save_dir "$CKPT_DIR/gemma270m_v07" \
    > "$CKPT_DIR/gemma270m_v07.log" 2>&1
echo "KF complete"
date
echo "=== ALL DONE ==="
