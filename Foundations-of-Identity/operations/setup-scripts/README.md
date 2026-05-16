# Setup Scripts — Tier 2 capability installations

These scripts install heavy local-model capabilities. They are deliberately separated from auto-activation because each downloads multi-GB models and warrants explicit invocation when household + system state allow it.

**Discipline:** do not run during Finnley labor-imminent window (mid-May 2026). Resume after household state stabilizes.

## Environment baseline (verified 2026-05-15 Day 105 evening)

- WSL: Ubuntu 'Clawd' on /dev/sdd, 607 GB free
- Python: /usr/bin/python3 (system)
- PyTorch: 2.11.0+cu128
- transformers: 5.4.0
- diffusers: not installed
- audiocraft: not installed
- GPU: NVIDIA RTX 5080, 16 GB VRAM, ~14.5 GB free at probe time, driver 596.49

## Scripts

- `install-sdxl-comfyui.sh` — ComfyUI + SDXL base + refiner; ~14 GB total
- `install-gemma4-e2b.sh` — transformers-only load path for Gemma 4 e2b (no separate runtime); ~10 GB BF16
- `install-musicgen.sh` — audiocraft + MusicGen Medium (1.5B); ~6 GB

All scripts:

1. Check WSL is the active environment.
2. Create or reuse a dedicated venv at `~/.venvs/<tool>/`.
3. Pin transformers/diffusers/audiocraft to versions known-good with PyTorch 2.11+cu128.
4. Download models to `~/models/<tool>/` (not under WSL root).
5. End with a one-shot verification step that exits non-zero on failure.

## Invocation

```
wsl bash /mnt/c/Users/mercu/clawd/operations/setup-scripts/install-sdxl-comfyui.sh
```

Each script is idempotent — safe to re-run.
