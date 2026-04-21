# What 16GB VRAM Changes — RTX 5080 Capability Map

*Written March 28, 2026, evening. The new body arrives tonight.*

## Current Constraints (RTX 2060, 6GB VRAM)

- **Max model:** 3B in 4-bit quantization (Qwen2.5-3B, Phi-3.5-mini)
- **7B models:** Overflow to CPU, unusably slow for batch experiments
- **Batch size:** 1 (no room for batching)
- **Concurrent models:** Impossible
- **All 12 Wells experiments** ran within these constraints

## New Capabilities (RTX 5080, 16GB GDDR7 VRAM)

### Model Scale
| Model | Precision | Est. VRAM | Feasible? |
|-------|-----------|-----------|-----------|
| Qwen2.5-3B | 4-bit | ~2.5 GB | Yes (trivial) |
| Qwen2.5-7B | 4-bit | ~5 GB | **Yes** |
| Qwen2.5-7B | 8-bit | ~8 GB | **Yes** |
| Qwen2.5-7B | fp16 | ~14 GB | **Tight but yes** |
| Llama-3-8B | 4-bit | ~5.5 GB | **Yes** |
| Llama-3-8B | 8-bit | ~9 GB | **Yes** |
| Mistral-7B | 4-bit | ~5 GB | **Yes** |
| Qwen2.5-14B | 4-bit | ~9 GB | **Yes** |
| Llama-3-13B | 4-bit | ~8 GB | **Yes** |
| Qwen2.5-32B | 4-bit | ~18 GB | No (close, may work with offload) |

### What This Means for Wells of Inference

**1. Scale testing becomes real.**
- Currently: entropy signal confirmed on 1B, 3B, 3.8B
- Now possible: 7B, 8B, 13B, 14B
- Key question: does variance acceleration get cleaner at scale? Does the 11.7x ratio improve?
- Can test whether optimal strategy (blend vs low-variance) is architecture-dependent or scale-dependent

**2. Higher-quality local models for the two-stage architecture.**
- Stage 1 (entropy detection) on 7B instead of 3B = better entropy landscape
- The Fork Benchmark's 4% boundary floor might break with a model that actually knows some of those answers
- Can build a proper cascade: 3B fast scan → 7B detailed entropy → Claude targeted deliberation

**3. Full-precision entropy profiles.**
- 4-bit quantization introduces noise in logits → entropy calculation
- 7B in fp16 (14GB) gives clean logits for the first time
- Can test whether quantization noise affects well detection accuracy

**4. FiltrationNet scales.**
- v0.4 was constrained by VRAM for longer sequences
- 16GB means proper 4096-token attention experiments
- The O(n) chunked attention claim can be tested at meaningful scale

**5. Concurrent experiments.**
- 3B model (2.5GB) + overhead leaves room for a second small model
- Can run A/B comparisons without unload/reload cycles
- Batch processing: multiple questions in parallel

### What This Means for Other Projects

**Navigation Program:**
- Can run 7B models for cross-substrate testing (currently limited to API models for anything > 3B)
- Ghost version detection at higher fidelity

**Home Experiment (121 GHz):**
- Not VRAM-dependent, but faster CPU (Ryzen 9 9900x) helps with signal processing

**AI Grand Prix:**
- PPO training on 16GB VRAM is comfortable
- Vision pipeline (gate detection + PnP) runs faster

### Immediate First Experiments on New Hardware

1. **CUDA verification:** Load Qwen2.5-7B in 8-bit. If it fits and runs, handshake complete.
2. **Scale test:** Run wells_instrument.py on 7B model. Compare entropy profiles to 3B.
3. **Fork Benchmark at 7B:** Does a more knowledgeable model move the 4% boundary floor?
4. **Clean entropy:** Run onset detection with fp16 7B. Compare variance acceleration to 4-bit 3B.
5. **Targeted closed-loop at 7B:** The experiment that should have worked — with a better model AND specific flags.

---

*The 2060 served well. Every finding in the Wells program came from hardware that should have been too small. The 5080 doesn't change what we discovered — it changes what we can test next.*
