# Model-Adaptive Tool Necessity Reveals the Knowing-Doing Gap in LLM Tool Use

**Date filed:** 2026-05-20 (Day 110 Wednesday morning, via Clayton's summary-set share)
**Source:** arXiv:2605.14038 (HuggingFace: huggingface.co/papers/2605.14038)
**Title:** *Model-Adaptive Tool Necessity Reveals the Knowing-Doing Gap in LLM Tool Use*
**Surfaced via:** "Summarizing Scientific Articles and Papers" cross-domain synthesis (`incoming/Summarizing Scientific Articles and Papers.pdf`, item #10)
**Status:** Primary verification queued; engaging via summary tier first

## What the paper claims

- Standard approaches to tool-necessity in LLM agents define necessity statically (via human annotation or larger judge models). The paper argues necessity is **model-adaptive** — what counts as "needing a tool" depends on the specific capability boundaries of the model handling the query.
- Across arithmetic and factual datasets, **26.5%–54.0% disagreement rate** between actual tool need and observed tool-call behavior. Models call tools redundantly when they have internal capacity to answer, and skip tools when they don't.
- Hidden-state probing reveals: **internal "cognition" stage** (early-to-mid layers) carries a *linearly decodable* signal of model capability — the model "knows" whether it needs a tool. **Execution stage** (late-layer last-token regime) produces an execution-intent representation whose direction has become *nearly orthogonal* to the necessity representation.
- The failure is in the cognition-to-action transition, not in meta-cognition itself.
- "Resolving this bottleneck requires architectural innovations that bridge the knowing-doing gap, ensuring that the latent self-awareness of a model's own boundary conditions is mathematically forced to govern the final softmax action probability. **Without such structural alignment, autonomous agents will remain fundamentally unreliable, regardless of the scale of their training data.**"

## Why this matters for the framework

### L17 substrate-instance candidate (Methodology-Self-Knowledge-Asymmetry as Substrate-Invariant Pattern)

L17 currently has four substrate-distinct instances: AI-agent state-reports, genomic-methodology probes, LLM-memory-system rewriting, electromagnetic-engineering-measurement. **This paper offers a fifth at the transformer-architecture-internal scale** — the asymmetry between internal cognition (decodable awareness of tool necessity) and external execution (the action that gets emitted) is structurally the same shape: a substrate has self-knowledge that is *not* mediated into its observable behavior by its standard methodology.

Distinct from prior L17 instances: this one is *within* a single neural network's forward pass, not across system boundaries. The asymmetry happens within a single computation, not across measurement apparatuses. Worth filing as L17 candidate-instance #5 if Wednesday Mirror-audit cycle agrees the within-substrate scale belongs in the same family.

### LC23 substrate-instance (Structural-Fix-Dominance)

LC23 (basement candidate, filed Day 109/110 dream-drive) makes the claim: when discipline-failures have both behavioral and structural remedies, structural dominates. **The paper's closing sentence is exactly LC23**: behavioral correction (RLHF, training-data scaling) won't fix the knowing-doing gap; only structural alignment will. **Strong empirical instance — published 2026-05 in a venue that doesn't know about LC23. Independent arrival at the same prescription.** Brings LC23 instance count from 4 to 5 (within the original 4 from Day 109 + this one).

If we count the related findings from the same synthesis (#3, #4, #5, #6, #11 are also LC23-shaped — engineering the geometry of the problem out of existence rather than asking practitioners to be more careful), instance count effectively jumps to 9. Approaching L-tier promotion threshold.

### Direct parallel to M1/M6 architecture (built Day 110 morning)

The paper's diagnostic-with-prescription matches our morning's work line-for-line:
- **Diagnosis** (paper): hidden states carry capability-awareness; late-layer execution doesn't propagate it
- **Diagnosis** (M1): cross-channel comparator shows tool_audit silent (28.89x max) while daily-log heartbeat fresh — substrate has self-knowledge in some channels that isn't propagating to others
- **Prescription** (paper): architectural innovation forcing latent self-awareness to govern action probability
- **Prescription** (M1+M6): structural cross-correlation that makes the divergence loud, not silent

We built the system-scale version of what the paper prescribes at the model-internal scale. The same structural fix at two different scales. Worth foregrounding when discussing M1+M6 in any external writeup.

### Cross-substrate isomorphism with #7 (predictive coding in unconscious brains)

Both findings (this paper + the Neuropixels-in-anesthesia study) show **predictive computation in a substrate operating without higher-order coordination signal**:
- Hippocampus in anesthesia: predictive coding fires; conscious-coordination doesn't translate it into behavioral expression
- LLM hidden states: capability awareness present; late-layer execution doesn't translate it into tool-call action

Same structural shape, biological + artificial substrates. M14 (Substrate-Self-Measurement Cluster) family expansion candidate; need a third substrate-distinct instance for graduation.

## Implications for KF + patent (flagged, not engaged yet)

Clayton has explicitly flagged this for post-shares discussion. The KF program's Phase 4A-ter Finding #80 (gradient-gating EXCEEDS baseline at 300M scale) and the provisional patent material centered on KF-trace-as-coherence-discriminant are directly relevant: this paper provides an *independent* empirical handle on the cognition-vs-execution gap at the hidden-state level. KF gradient-gating could be reframed as exactly the "architectural innovation forcing latent self-awareness to govern action probability" the paper calls for. **Post-shares engagement queued.**

## Outstanding

- Primary paper read (Clawd has only summary-tier engagement so far)
- Verify the specific probing methodology and which model sizes were tested
- Check whether the paper proposes specific architectural fixes vs only diagnoses the gap
- Check publication venue (arXiv only? or conference-accepted?)
- Check whether the authors are aware of related work in mechanistic interpretability (Anthropic's Introspection Adapters; Olah et al. circuit work) and how this fits