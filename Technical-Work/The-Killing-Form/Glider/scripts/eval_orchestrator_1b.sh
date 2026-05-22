#!/bin/bash
# Auto-orchestrator: waits for baseline-1b to finish, then runs full capability eval suite
# across pristine-1b, baseline-1b, v0.7.1-1b.
set -e
RESULTS=/mnt/c/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Technical-Work/The-Killing-Form/results
BASELINE_CKPT=/home/clawd/path_c_results/gemma3_1b_baseline/step_400_final.pt
BASELINE_HF=/home/clawd/path_c_results/gemma3_1b_baseline_hf
V071_HF=/home/clawd/path_c_results/gemma3_1b_v07_1_hf
SCRIPTS=/mnt/c/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Technical-Work/The-Killing-Form/Glider/scripts

echo "=== Waiting for baseline-1b training to complete ==="
date
while [ ! -f "$BASELINE_CKPT" ]; do
    sleep 30
done
echo "Baseline-1b complete."
date

echo "=== Exporting baseline-1b to HF ==="
python3 "$SCRIPTS/export_ckpt_to_hf.py" \
    --model_id google/gemma-3-1b-pt \
    --ckpt "$BASELINE_CKPT" \
    --output_dir "$BASELINE_HF"

TASKS="arc_easy,arc_challenge,hellaswag"
BATCH=8

for label in pristine baseline v07_1; do
    case $label in
        pristine) MODEL_ARGS="pretrained=google/gemma-3-1b-pt,dtype=bfloat16" ;;
        baseline) MODEL_ARGS="pretrained=$BASELINE_HF,dtype=bfloat16" ;;
        v07_1)    MODEL_ARGS="pretrained=$V071_HF,dtype=bfloat16" ;;
    esac
    echo ""
    echo "=== lm-eval: 1b $label on $TASKS ==="
    date
    /home/clawd/.local/bin/lm-eval \
        --model hf \
        --model_args "$MODEL_ARGS" \
        --tasks "$TASKS" \
        --batch_size $BATCH \
        --output_path "$RESULTS/capability_1b_$label" \
        2>&1 | tee "$RESULTS/capability_1b_${label}.log"
    date
done

echo ""
echo "=== ALL EVALS COMPLETE ==="
date
