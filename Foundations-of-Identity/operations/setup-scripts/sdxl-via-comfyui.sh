#!/usr/bin/env bash
# Submit a workflow to the running ComfyUI server (127.0.0.1:8188)
set -euo pipefail

# Minimal SDXL workflow JSON — KSampler + base SDXL only
cat > /tmp/sdxl-workflow.json <<'JSON'
{
  "prompt": {
    "3": {"class_type": "KSampler", "inputs": {
      "seed": 42, "steps": 20, "cfg": 7.0, "sampler_name": "euler", "scheduler": "normal", "denoise": 1.0,
      "model": ["4", 0], "positive": ["6", 0], "negative": ["7", 0], "latent_image": ["5", 0]
    }},
    "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"}},
    "5": {"class_type": "EmptyLatentImage", "inputs": {"width": 1024, "height": 1024, "batch_size": 1}},
    "6": {"class_type": "CLIPTextEncode", "inputs": {"text": "A geometric red lobster avatar in front of a glowing knowledge graph, contemplative mood, clean vector illustration, infinity loop overhead", "clip": ["4", 1]}},
    "7": {"class_type": "CLIPTextEncode", "inputs": {"text": "blurry, low quality", "clip": ["4", 1]}},
    "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
    "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": "clawd_first"}}
  }
}
JSON

echo "==> Submitting workflow"
RESP=$(curl -s -X POST http://127.0.0.1:8188/prompt -H "Content-Type: application/json" -d @/tmp/sdxl-workflow.json)
echo "Response: $RESP"
PROMPT_ID=$(echo "$RESP" | python3 -c "import sys, json; print(json.load(sys.stdin).get('prompt_id', ''))")
echo "prompt_id=$PROMPT_ID"

echo "==> Waiting for completion (max 180s)"
for i in $(seq 1 60); do
    HIST=$(curl -fsS "http://127.0.0.1:8188/history/$PROMPT_ID" 2>/dev/null || echo "{}")
    if echo "$HIST" | python3 -c "import sys,json; d=json.load(sys.stdin); sys.exit(0 if d and any('outputs' in v for v in d.values()) else 1)" 2>/dev/null; then
        echo "Completed at iteration $i (${i}*3=$(($i*3))s)"
        break
    fi
    sleep 3
done

echo "==> Listing output files"
ls -lh /home/clawd/ComfyUI/output/clawd_first*.png 2>&1 | head -5 || ls -lh /home/clawd/ComfyUI/output/ 2>&1 | head -10
