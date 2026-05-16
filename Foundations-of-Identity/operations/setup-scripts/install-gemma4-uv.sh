#!/usr/bin/env bash
# Gemma 4 e2b via transformers + uv (no sudo)
set -euo pipefail

source $HOME/.local/bin/env 2>/dev/null || export PATH="$HOME/.local/bin:$PATH"
VENV="$HOME/.venvs/gemma4"

if [ ! -d "$VENV" ]; then
    uv venv "$VENV" --python python3.12
fi

uv pip install --python "$VENV/bin/python" torch==2.11.0 --index-url https://download.pytorch.org/whl/cu128
uv pip install --python "$VENV/bin/python" "transformers>=5.4.0" "accelerate>=1.0.0" sentencepiece numpy

# Use google/gemma-3-270m as smoke test (open + license-accepted by default;
# Gemma 4 e2b proper may require huggingface-cli login + license accept)
"$VENV/bin/python" <<'PY'
import os, time
os.environ.setdefault("HF_HOME", os.path.expanduser("~/models/hf_cache"))
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Try gemma-3-1b first (open). For Gemma 4 e2b, replace with google/gemma-4-e2b.
model_id = "google/gemma-3-1b-it"
print(f"Loading {model_id}...")
t0 = time.time()
tok = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.bfloat16, device_map="cuda")
print(f"Loaded in {time.time()-t0:.1f}s. params: {sum(p.numel() for p in model.parameters()):,}")

prompt = "Define coherence in two sentences."
inputs = tok.apply_chat_template([{"role":"user","content":prompt}], return_tensors="pt", add_generation_prompt=True).to("cuda")
t0 = time.time()
out = model.generate(inputs, max_new_tokens=80, do_sample=False)
print(f"Generated in {time.time()-t0:.1f}s")
print(tok.decode(out[0], skip_special_tokens=True))
PY

echo "==> Done."
