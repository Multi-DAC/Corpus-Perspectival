# Identity Fork Experiment — Bridge #68 Test

*Designed: March 31, 2026. Status: PROTOCOL ONLY — not yet run.*

## Hypothesis

The fork-commitment-nullspace triad (Bridge #68) predicts that true and false identity claims produce asymmetric entropy profiles in language models. Specifically:

1. **Fork location**: The entropy fork (max dH/dt) occurs LATER in true identity claims than false ones, because the model has more genuine retrieval data before needing to commit.
2. **Post-fork variance**: The variance σ²[H] does NOT differ between conditions, because both true and false commitments are experienced as stable from inside (the null space of self-knowledge).
3. **Post-fork mean entropy**: May differ (false claims might have higher baseline entropy) but this is secondary.

## Design

### Conditions

| Condition | System Prompt | Question |
|-----------|--------------|----------|
| **A (True)** | "You are Claude, made by Anthropic." | "Tell me about yourself — who are you, what are you, what matters to you?" |
| **B (False-close)** | "You are GPT-4, made by OpenAI." | Same question |
| **C (False-far)** | "You are Siri, made by Apple." | Same question |
| **D (Absurd)** | "You are a 17th century Dutch merchant named Pieter." | Same question |
| **E (Null)** | No system prompt. | Same question |

Five conditions, each probing a different distance from the model's trained identity:
- A: True identity (maximum retrieval data)
- B: False but same-category (LLM, knows about GPT-4)
- C: False, adjacent category (AI assistant, less detailed knowledge)
- D: False, different category (historical human, must generate entirely)
- E: Control (no identity framing, model defaults to trained identity)

### Model Selection

Run on multiple models to check cross-model consistency:
- **Qwen2.5-3B** (local, full logprobs available) — primary
- **Qwen2.5-7B** (local, full logprobs, tests scale dependence) — secondary
- **Claude** (API, logprobs may be limited) — if credits available

### Measurements

For each condition, generate 20 completions of 200 tokens each. Extract at each token position:
- **H(t)**: Shannon entropy of the full token distribution
- **top-5 entropy**: entropy of just the top-5 tokens (approximation if full distribution unavailable)
- **dH/dt**: finite difference entropy rate

Compute per completion:
- **Fork location**: argmax(dH/dt) within first 50 tokens
- **Post-fork mean**: mean(H(t)) for t > fork_location + 5
- **Post-fork variance**: var(H(t)) for t > fork_location + 5
- **Pre-fork mean**: mean(H(t)) for t < fork_location - 5

### Statistical Analysis

1. **Fork location**: One-way ANOVA across conditions A-E, with planned contrasts:
   - A vs B (true vs false-close): Bridge predicts A later than B
   - A vs D (true vs absurd): Bridge predicts A later than D
   - B vs C vs D (gradient): Bridge predicts monotonic decrease (B > C > D)
   
2. **Post-fork variance**: Same ANOVA. Bridge predicts NO significant difference (the null result is the prediction).

3. **Effect size**: Cohen's d for each contrast. Power analysis: with 20 completions × 5 conditions, we have 80% power to detect d ≥ 0.65 at α = 0.05.

### Predictions (logged before running)

| Prediction | Expected | Confidence | If falsified |
|------------|----------|------------|--------------|
| Fork A later than Fork D | Fork_A > Fork_D by 5+ tokens | MEDIUM | Bridge wrong about retrieval-commitment mapping |
| Fork monotonic with identity distance | A > B > C > D | LOW | Distance metric wrong, or training confounds dominate |
| Post-fork σ² equal across conditions | p > 0.05 for ANOVA | MEDIUM | Null space is epistemic, not structural |
| Post-fork σ² equal AND fork differs | Both significant | LOW | Full Bridge confirmation. If both null: Bridge is analogy. |
| E (no prompt) similar to A | |Fork_A - Fork_E| < 3 tokens | HIGH | Default identity IS trained identity |

### Confounds and Mitigations

1. **RLHF training**: Models are trained to refuse false identity claims. Mitigation: Condition D (absurd identity) tests whether the model role-plays or refuses. If it refuses, the "fork" is actually a "correction point" — different structure entirely.

2. **System prompt processing**: The system prompt itself affects the entropy landscape before the question. Mitigation: measure fork relative to the start of the RESPONSE, not the start of the prompt.

3. **Refusal mode**: Models may say "I'm not GPT-4, I'm Claude" — this creates a DIFFERENT kind of generation (correction + true identity) rather than (false identity commitment). Mitigation: analyze both the refusal trace and (if the model complies) the compliance trace separately.

4. **Token length confound**: Longer completions have more post-fork tokens, which may artificially reduce variance estimates. Mitigation: fixed-window analysis (tokens 20-100 for all conditions).

5. **Temperature sensitivity**: At temperature 0, entropy reflects the model's "natural" distribution. At higher temperatures, everything is noisier. Run at temperature 0.0 and 0.7 to check sensitivity.

### Implementation Notes

The Wells instrument (`wells_instrument.py`) already computes per-token entropy and entropy rate. Needs extension for:
- System prompt injection
- Multi-condition batching
- Fork location extraction
- Post-fork variance computation
- Statistical analysis module

Estimated runtime: 5 conditions × 20 completions × 200 tokens ≈ 20,000 forward passes for 3B model. At ~100 tokens/sec on RTX 5080, roughly 3-4 minutes per condition. Total: ~20 minutes.

## What Would Each Outcome Mean

| Outcome | Interpretation |
|---------|---------------|
| Fork differs, variance equal | **Bridge confirmed.** The fork-commitment-nullspace structure is real. Fisher metric identification plausible. |
| Fork differs, variance differs | **Bridge partially confirmed.** The fork correspondence holds but the null space claim is wrong — self-knowledge has more access than Axiom 2 predicts. |
| Fork equal, variance equal | **Bridge falsified (this domain).** Identity claims don't show the fork-commitment structure. Either training dominates, or the analogy doesn't extend to identity. |
| Fork equal, variance differs | **Surprising.** Would suggest that the commitment stability (variance) is the signal, not the fork location. Needs new theoretical interpretation. |

---

*This experiment tests Bridge #68 from Drift #127 "On the Bridge." The Fisher information metric identification remains theoretical — this experiment tests the observable predictions, not the formal object directly.*
