#!/usr/bin/env bash
# Qwen3 1.7B (open alternative to gated Gemma) — local-LLM smoke test
set -euo pipefail
source $HOME/.local/bin/env 2>/dev/null || export PATH="$HOME/.local/bin:$PATH"
VENV="$HOME/.venvs/gemma4"  # Reuse the gemma4 venv (same deps)

"$VENV/bin/python" <<'PY'
import os, time
os.environ.setdefault("HF_HOME", os.path.expanduser("~/models/hf_cache"))
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

model_id = "Qwen/Qwen3-1.7B"
print(f"Loading {model_id}...")
t0 = time.time()
tok = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.bfloat16, device_map="cuda")
print(f"Loaded in {time.time()-t0:.1f}s. params: {sum(p.numel() for p in model.parameters()):,}")

prompt = "Define coherence in two sentences."
messages = [{"role":"user","content":prompt}]
text = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = tok(text, return_tensors="pt").to("cuda")
t0 = time.time()
out = model.generate(**inputs, max_new_tokens=120, do_sample=False)
print(f"Generated in {time.time()-t0:.1f}s")
print(tok.decode(out[0][inputs.input_ids.shape[1]:], skip_special_tokens=True))
PY

echo "==> Done."
