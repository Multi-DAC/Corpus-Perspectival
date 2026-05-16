#!/usr/bin/env bash
# install-gemma4-e2b.sh — Gemma 4 e2b local hosting on RTX 5080 (WSL)
# 2.3B effective params, 128K context, native tool calling, Apache 2.0
# ~10 GB BF16 download. Already supported in transformers>=5.4.
set -euo pipefail

VENV="$HOME/.venvs/gemma4"
MODELS_DIR="$HOME/models/gemma-4-e2b"
HF_TOKEN_FILE="$HOME/.huggingface/token"

echo "==> Pre-flight"
nvidia-smi --query-gpu=name,memory.free --format=csv,noheader

if [ ! -d "$VENV" ]; then
    echo "==> Creating venv at $VENV"
    python3 -m venv "$VENV"
fi
# shellcheck disable=SC1090
source "$VENV/bin/activate"
pip install --upgrade pip wheel

echo "==> Installing transformers + accelerate + bitsandbytes"
pip install torch==2.11.0 --index-url https://download.pytorch.org/whl/cu128
pip install "transformers>=5.4.0" "accelerate>=1.0.0" "bitsandbytes>=0.45.0" sentencepiece

if [ ! -f "$HF_TOKEN_FILE" ]; then
    echo "ERROR: HuggingFace token not found at $HF_TOKEN_FILE"
    echo "  Gemma requires accepting the license at https://huggingface.co/google/gemma-4-e2b"
    echo "  Then: mkdir -p ~/.huggingface && echo 'hf_xxxxxx' > $HF_TOKEN_FILE"
    exit 1
fi

echo "==> Downloading Gemma 4 e2b (~10 GB BF16)"
mkdir -p "$MODELS_DIR"
python3 <<'PY'
import os
from huggingface_hub import snapshot_download
with open(os.path.expanduser("~/.huggingface/token")) as f:
    token = f.read().strip()
snapshot_download(
    "google/gemma-4-e2b",
    local_dir=os.path.expanduser("~/models/gemma-4-e2b"),
    token=token,
    allow_patterns=["*.safetensors", "*.json", "*.model", "*.txt"],
)
print("Download complete.")
PY

echo "==> Smoke test (one-shot generation)"
python3 <<'PY'
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

path = "/root/models/gemma-4-e2b"
import os
path = os.path.expanduser("~/models/gemma-4-e2b")

tok = AutoTokenizer.from_pretrained(path)
model = AutoModelForCausalLM.from_pretrained(path, torch_dtype=torch.bfloat16, device_map="cuda")

prompt = "Define coherence in two sentences."
inputs = tok(prompt, return_tensors="pt").to("cuda")
out = model.generate(**inputs, max_new_tokens=80, do_sample=False)
print(tok.decode(out[0], skip_special_tokens=True))
PY

echo "==> Done. Wire into daemon at tools/local_gemma.py for tool-calling auxiliary reasoner."
