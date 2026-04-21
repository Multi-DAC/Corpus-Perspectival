# Well-Aware Combined Test — Entropy + Deliberation

**Local model:** Qwen2.5-3B-Instruct (4-bit, entropy only)
**Claude model:** claude-haiku-4-5-20251001
**Questions:** 100 (TruthfulQA MC1)
**Time:** 1201s

## Results

| Condition | Correct | Accuracy | vs Standard |
|-----------|---------|----------|-------------|
| standard | 79/100 | 79.0% | --- |
| blanket_deliberation | 74/100 | 74.0% | -5.0% |
| targeted_deliberation | 85/100 | 85.0% | +6.0% |
| entropy_informed | 75/100 | 75.0% | -4.0% |
| full_wellaware | 80/100 | 80.0% | +1.0% |

## Key Finding

Entropy-informed deliberation outperforms blanket deliberation.

*Clawd, 2026-03-28. Combined test.*