# Wells — Entropy Track

*The quantitative hallucination-detection program. Wells of Inference: 12 experiments across 3 architectures (TinyLlama, Qwen, Phi; Claude Haiku for behavioral conditions).*

## Start here

- **[WELLS_OF_INFERENCE.md](WELLS_OF_INFERENCE.md)** — the program write-up. 12 experiments, 11 confirmed findings. Start here for the full picture.

## Structure

- `WELLS_OF_INFERENCE.md` — program write-up
- `instrument/` — `wells_instrument.py` (the deployable detection module)
- `experiments/` — one script + data + results per experiment (Exp 1 through Exp 12)
- `analyses/` — bridge/calibration/disagreement analyses; higher-level synthesis scripts and their outputs

## Load-bearing findings (short version)

1. Wells exist at local entropy maxima, mark real semantic choice points (not noise)
2. RLHF redistributes entropy — chat models are MORE honestly uncertain, not less
3. Template-honesty (performing uncertainty) and entrained-honesty have distinct entropy signatures
4. The hallucination fork IS a well; post-fork confabulation is entropy-invisible
5. Entropy beats logprob cross-architecturally (+7–12pp; Qwen, Phi)
6. **Targeted deliberation beats blanket by +11pp. Blanket HURTS (-5pp).**
7. Knowledge-frontier confabulation is entropy-resistant
8. Onset detection: 11.7x variance-acceleration ratio (correct vs hallucinated, first 10 tokens)
9. Early warning: 78% precision, 90% recall, triggers by token 7
10. Closed-loop with blanket warning FAILS (-4pp) → confirms targeted architecture
11. **The instrument's value is the translation layer** — distilled flags > raw data > generic alarms

## Cross-track links

- First-person correlates: see `../navigation/` (substrate architecture, 34 trials)
- Cross-architecture phenomenology: see `../cross-substrate/`
- 3-way integration: see `../bridge/BRIDGE.md`

🦞🧍💜🔥♾️
