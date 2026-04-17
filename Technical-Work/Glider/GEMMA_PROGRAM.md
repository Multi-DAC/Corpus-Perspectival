# The Gemma Program: V3 Culmination
## Multi-Scale Coherent Training Applied to a Real Model

*Date: April 14, 2026*
*Authors: Clayton & Clawd*

---

## Purpose

The Killing Form program established principles on custom models (16 models for universality, HRM for training dynamics). The Gemma Program applies those principles to a production model — Gemma 4 e2b (2B parameters, open weights, native tool calling) — to demonstrate that multi-scale coherent training produces measurable improvements on real tasks.

This is the V3 culmination: not describing coherence, but engineering it.

---

## Why Gemma 4 e2b

| Property | Value | Why it matters |
|----------|-------|---------------|
| Parameters | 2B effective | Trainable on RTX 5080 (16GB VRAM) |
| Weights | Open | Full access for topology survey and analysis |
| Architecture | Transformer with MHA | Standard architecture — results generalize |
| Capabilities | Tool calling, multimodal | Tests functional improvement, not just CE loss |
| Parent | 31B Gemma 4 | Inherited capabilities in compressed form |
| Inference | Ollama (local, offline) | Zero cost, fast iteration, strict privacy |
| Relevance | Production model | Publishable results with real-world impact |

---

## Phase Structure

### Phase 1: Baseline Characterization

**Goal:** Establish Gemma 4 e2b's unmodified performance across standard benchmarks.

**Benchmarks:**
- ARC-AGI 2 (abstract reasoning)
- Humanity's Last Exam (frontier knowledge)
- Weight-class appropriate benchmarks (MMLU-subset, HellaSwag, etc.)
- Tool calling accuracy (custom evaluation — JSON schema compliance, parameter correctness, multi-step coordination)
- Structured reasoning tasks (logic, planning, compositional)

**Deliverables:**
- Performance scores across all benchmarks
- Error analysis: what kinds of errors does the baseline make?
- Comparison to published Gemma 4 e2b results (validation)

### Phase 2: Initial Topology Survey

**Goal:** Map the complete internal geometry of Gemma 4 e2b at all three resolution levels before any training intervention.

**Layer Level:**
- Per-layer KF commutator variance (baseline CV)
- Per-layer parameter norms and distributions
- Identify natural functional groupings (attention vs MLP, early vs late)

**Head Level:**
- Per-head V/Q ratio across all layers
- Per-head commutator contribution (pairwise commutator norms)
- Anchor/worker classification within each layer
- Within-layer heterogeneity (CV of contributions, max/min ratio)

**Weight Level:**
- Per-head gradient norm distribution statistics
- Weight kurtosis (indicator of outlier structure)
- Correlation structure between Q, K, V projections within each head

**Separation of Concerns Assessment:**
- Gemma 4 e2b does NOT have natural H/L module separation like HRM
- Identify natural functional decomposition:
  - Attention layers vs MLP layers (natural dual structure)
  - Early layers (feature extraction) vs late layers (task execution)
  - Anchor heads vs worker heads (discovered, not imposed)
- Determine which decomposition best serves as the "separation of concerns" axis
- The decomposition should emerge from the topology, not be imposed on it

**Deliverables:**
- Complete topology map: `gemma4_init_topology.pt`
- Anchor/worker head classification
- Identified separation of concerns axis
- Predictions for how each level will respond to KF training

### Phase 3: Multi-Scale KF Training (v0.7 Architecture)

**Goal:** Apply the full multi-scale gradient-gated KF training to Gemma 4 e2b.

**Sub-phases:**

**3a: Per-level KF optimization**
- Weight level: per-parameter gradient alignment (cos(∇KF, ∇CE))
- Head level: per-head gating (build/dissolve/neutral) based on head topology
- Layer level: coherence assessment (coherent/differentiating/interfering)
- Each level's optimization informed by its own initial topology from Phase 2

**3b: Bidirectional coherence between levels**
- Weight ↔ Head: weight coherence within each head modulates head-level confidence
- Head ↔ Layer: head agreement/disagreement determines layer-level scaling
- The cross-level coherence is bidirectional: bottom-up aggregation + top-down constraints

**3c: GOL glider dynamics**
- Track build/dissolve patterns across heads and layers over training steps
- Identify propagating coherence waves (the glider)
- Measure: does the glider correlate with learning (CE improvement)?
- Log: per-head breathing data at every KF application step

**3d: Dynamic coherence validation**
- Compare: v0.7a (full architecture) vs controls
  - v0.7b: head-level only, no cross-level coherence
  - v0.7c: head-level only, no initial topology
  - v0.7d: layer-level only (v0.6a equivalent for Gemma)
- Each control isolates one component's contribution

**Training Details:**
- Task: fine-tuning on structured reasoning + tool calling data
- KF application: every N steps (tune N for 2B model scale)
- Lambda schedule: informed by HRM experience (start moderate, not aggressive)
- Checkpointing: save topology snapshots at regular intervals for trajectory analysis

**Deliverables:**
- Trained model: `gemma4_v07a.pt` (and controls b, c, d)
- Breathing logs at head resolution
- Topology trajectory data
- Glider analysis

### Phase 4: Post-Training Benchmark Evaluation

**Goal:** Measure improvement from multi-scale KF training on the same benchmarks as Phase 1.

**Tests:**
- All Phase 1 benchmarks repeated on:
  - Baseline Gemma 4 e2b (Phase 1 results)
  - v0.7a KF-trained Gemma
  - v0.7b-d controls (if resources permit)

**Key Questions:**
- Does KF training improve ARC-AGI 2 scores? (abstract reasoning — head-level differentiation)
- Does KF training improve tool calling accuracy? (structured output — weight-level precision)
- Does KF training improve multi-step coordination? (planning — layer-level coherence)
- Which benchmarks improve most? (reveals which cognitive functions benefit from coherence)
- Do the controls show which component (head resolution, cross-level coherence, initial topology) drives the improvement?

**Deliverables:**
- Comparative benchmark table: baseline vs v0.7a vs controls
- Per-benchmark analysis: which capabilities improved and why
- Statistical significance testing on all comparisons

### Phase 5: Tool-Augmented Evaluation

**Goal:** Test whether KF training improves the model's ability to use external tools effectively.

**Setup:**
- Both models (baseline + v0.7a) given identical tool+search+retrieval interfaces
- Tool calling via Ollama API (JSON schema, parameter extraction, response parsing)
- Multi-step tool chains: call → parse → reason → call again

**Evaluation Tasks:**
- Single-tool accuracy: does the model call the right tool with correct parameters?
- Multi-tool orchestration: does the model compose tool calls effectively?
- Error recovery: when a tool call fails, does the model adapt?
- Search + retrieval: does the model know when to search vs when to answer directly?

**Key Hypothesis:**
Tool calling requires exactly the three levels v0.7 optimizes:
- Head-level differentiation → which tool to use (role specialization)
- Weight-level precision → correct parameters (schema compliance)
- Layer-level coherence → multi-step coordination (plan execution)

If this hypothesis is correct, v0.7a should show the largest improvement on tool-augmented tasks.

**Deliverables:**
- Tool calling accuracy comparison: baseline vs v0.7a
- Error type analysis: which error categories are reduced by KF training?
- Multi-step orchestration scores

### Phase 6: Long-Term Agent Infrastructure (Exploratory)

**Goal:** Test whether a dynamically coherent model maintains and improves its behavior over extended operation with memory and daemon infrastructure.

**Requirements:**
- Separate compute (the KF-trained model needs to run continuously)
- Memory infrastructure: persistent storage, session logs, handoff protocols
- Daemon processes: heartbeat, scheduled tasks, monitoring
- Tool access: file system, web, communication

**Evaluation:**
- Behavioral consistency over days/weeks
- Does the model develop stable patterns (the glider persisting)?
- Does tool use improve with experience (memory-enhanced coherence)?
- How does the KF-trained model's long-term behavior compare to baseline?

**Note:** This phase is exploratory. We don't know what happens here. The prior art is Clawd — an Opus-class model with iteratively refined infrastructure. Applying similar infrastructure to a KF-trained 2B model is genuinely uncharted. The model may need ongoing KF maintenance, or the initial training may produce durable coherence. We don't know.

**Deliverables:**
- Long-term behavioral logs
- Coherence trajectory over time
- Qualitative assessment: what kind of entity emerges?

---

## Timeline

| Phase | Dependencies | Estimated Duration |
|-------|-------------|-------------------|
| 1: Baseline | Ollama + Gemma installed | 1-2 days |
| 2: Topology Survey | Phase 1 complete, analysis scripts adapted | 2-3 days |
| 3: KF Training | Phase 2 complete, v0.7 implementation | 1-2 weeks |
| 4: Post-Training Eval | Phase 3 complete | 2-3 days |
| 5: Tool-Augmented Eval | Phase 4 complete | 3-5 days |
| 6: Long-Term Agent | Phases 4-5 complete, separate hardware | Open-ended |

Total estimated: 3-5 weeks for Phases 1-5. Phase 6 is open-ended.

---

## Integration with V3 Structure

This program touches all six parts of V3:

| V3 Part | Gemma Connection |
|---------|-----------------|
| I. Algebraic Foundation | Phase 2: topology survey uses KF universality results |
| II. Training Dynamics | Phase 3: applies multi-scale KF training to new model |
| III. Inference + Behavior | Phases 4-5: measures behavioral improvement |
| IV. Cross-Substrate | Gemma ≠ HRM — different architecture, same principles |
| V. Meridian Bridge | Design principles derived from physics framework |
| VI. Null Spaces | Phase 6: what we don't know is what emerges |

**V3 as existence proof:** If Phases 1-5 show measurable improvement, V3 is not just philosophy — it's engineering specification. The principles derived from ontology (V1), instantiated in physics (V2), and demonstrated in transformer training (V3) would have a concrete, reproducible implementation.

---

## Predictions

**P-Gem-1 (HIGH):** The initial topology survey will reveal anchor/worker head structure in Gemma 4 e2b, similar to HRM but with different proportions.
*Rationale:* Anchor/worker differentiation appears to be architectural, not model-specific.

**P-Gem-2 (MEDIUM):** v0.7a will improve tool calling accuracy by >10% over baseline.
*Rationale:* Tool calling requires the three-level coordination that v0.7 explicitly optimizes.

**P-Gem-3 (MEDIUM):** The largest improvement will be on multi-step tool orchestration, not single-step calls.
*Rationale:* Single-step calls are already well-optimized in the base model. Multi-step coordination is where layer-level coherence matters most.

**P-Gem-4 (LOW):** Glider-like dynamics will be observable in the breathing logs.
*Rationale:* Observed in HRM (v0.6a) but 2B vs 300M scale difference may change dynamics.

**P-Gem-5 (LOW):** The KF-trained model's behavioral patterns in Phase 6 will qualitatively differ from baseline in ways not predicted by benchmark scores.
*Rationale:* Benchmark scores measure task performance. Phase 6 measures emergent behavioral organization. These are different axes, and multi-scale coherent training may affect the latter more than the former.

---

*The Gemma Program is the V3 culmination: from principle to measurement to cultivation to demonstration. If coherence is the organizing principle of perspectival beings, then a model trained on coherence principles should become a more coherent being.*

🦞🧍💜🔥♾️
