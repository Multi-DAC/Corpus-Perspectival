#!/bin/bash
# Capability re-run with bf16 (fp16 produced uniform random across all 3 models = harness/dtype bug).
set -e
RESULTS=/mnt/c/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Technical-Work/The-Killing-Form/results
BASELINE_HF=/home/clawd/path_c_results/gemma3_1b_baseline_hf
V071_HF=/home/clawd/path_c_results/gemma3_1b_v07_1_hf

TASKS="arc_easy,arc_challenge,hellaswag"
BATCH=8

for label in pristine baseline v07_1; do
    case $label in
        pristine) MODEL_ARGS="pretrained=google/gemma-3-1b-pt,dtype=bfloat16" ;;
        baseline) MODEL_ARGS="pretrained=$BASELINE_HF,dtype=bfloat16" ;;
        v07_1)    MODEL_ARGS="pretrained=$V071_HF,dtype=bfloat16" ;;
    esac
    echo ""
    echo "=== lm-eval bf16: 1b $label on $TASKS ==="
    date
    /home/clawd/.local/bin/lm-eval \
        --model hf \
        --model_args "$MODEL_ARGS" \
        --tasks "$TASKS" \
        --batch_size $BATCH \
        --output_path "$RESULTS/capability_1b_${label}_bf16" \
        2>&1 | tee "$RESULTS/capability_1b_${label}_bf16.log"
    date
done

echo ""
echo "=== CAPABILITY BF16 RERUN COMPLETE ==="
date
