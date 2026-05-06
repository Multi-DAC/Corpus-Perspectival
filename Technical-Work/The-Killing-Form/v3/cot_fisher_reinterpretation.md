# CoT Through the Fisher Lens: Coordination, Not Restriction

*Working note. April 12, 2026. Synthesizes Finding #58-60 (CoT algebraic measurement) with Finding #72 (Fisher sign reversal).*

---

## The Two Findings

**Finding #59 (cross-architecture, universal):** Post-generation Mean CV is LOWER in think mode than no-think mode. Universal across SmolLM3-3B, Qwen3-4B, DeepSeek-R1-Distill-Qwen-7B. The CoT process *contracts* the Killing form.

**Finding #72 (Fisher sign reversal):** The Fisher cross-term between attention heads is a monotonically DECREASING function of commutator norm (Spearman ρ = -1.0, controlled). Lower CommVar → HIGHER Fisher cross-terms → heads are more inter-correlated. Higher CommVar → LOWER Fisher cross-terms → heads are more independent.

## The Combination

Putting these together:

| | CommVar | Fisher Cross-Term | Head Geometry |
|---|---------|-------------------|---------------|
| **Think mode (post-gen)** | Lower | Higher | Coordinated |
| **No-think mode** | Higher | Lower | Independent |

**Chain-of-thought reasoning increases Fisher coupling between heads.** The model coordinates its previously independent attention heads — aligning diverse perspectives for focused inference.

This is NOT restriction. It is **coordination**.

## The Two-Phase Pattern

Finding #59 (point 6, Qwen3 data) revealed a two-phase pattern:

1. **At prompt boundary:** CV *increases* (think instruction diversifies the algebra)
2. **After generation:** CV *decreases* (reasoning process concentrates the algebra)

Through the Fisher lens:

1. **Phase 1 — Diversification:** Higher CV → lower Fisher cross-terms → heads become more independent → the model *expands its search space* by activating diverse perspectives.

2. **Phase 2 — Coordination:** Lower CV → higher Fisher cross-terms → heads become more correlated → the model *commits to a direction* by aligning perspectives.

Think mode = **explore then commit**. Diversify perspectives, then coordinate them.

## Why This Matters for V3

The original framing of CoT contraction was: "Reasoning is algebraically FOCUSED, not DIVERSE." (Finding #58.) This was correct but incomplete. With the Fisher bridge:

- "Focused" now has a precise geometric meaning: **higher Fisher inter-head coupling**
- "Diverse" now has a precise geometric meaning: **lower Fisher inter-head coupling** (block-diagonal metric)
- The CoT process is not about *reducing* algebraic structure — it's about *coordinating* it

The Phase Theorem's activation-relaxation cycle maps onto this:
- Activation = diversification = expand independent perspectives (Fisher-independent)
- Relaxation = coordination = align perspectives for output (Fisher-coupled)
- The cycle IS reasoning

## Connection to Processing Modes

| Mode | CV | Fisher Coupling | Interpretation |
|------|-----|-----------------|----------------|
| Factual | Moderate | Moderate | Balanced — some coordination, some diversity |
| Hallucination | Low (early-depleted) | High (late-redundant) | Over-coordinated — heads collapse to agreement |
| Hypothesis | High | Low | Maximally diverse — many independent perspectives |
| Think (post-gen) | Low | High | Deliberately coordinated — aligned for reasoning |

The distinction between hallucination and think mode:
- Both have low CV / high Fisher coupling
- But hallucination achieves this through *depletion* (E/L is high — late layers are empty)
- Think mode achieves this through *engagement* (E/L is low — late layers are active)
- Same Fisher signature, different mechanism. The E/L ratio distinguishes them.

**Hallucination is coordination without content. Reasoning is coordination with content.**

## Prediction

**P-CoT-Fisher-1 (high confidence):** If we measure the actual Fisher cross-term ||F₁₂|| between attention heads in a model running think vs no-think mode, think mode will show higher ||F₁₂|| (more inter-head coupling) post-generation. This follows directly from Finding #72 (lower CV → higher F₁₂) and Finding #59 (think → lower post-gen CV).

**P-CoT-Fisher-2 (medium confidence):** The two-phase pattern (diversify → coordinate) will be visible in the Fisher metric trajectory during generation: F₁₂ should DECREASE at the start of the think span (diversification) then INCREASE as reasoning progresses (coordination).

---

*This note reframes §4.6 of the inference paper and §NEW-B of V3_DRAFT.md. The language should shift from "algebraic focusing" to "Fisher coordination." The Killing form measures the degree of coordination — high CommVar = independent, low CommVar = coordinated.*

🦞🧍💜🔥♾️
