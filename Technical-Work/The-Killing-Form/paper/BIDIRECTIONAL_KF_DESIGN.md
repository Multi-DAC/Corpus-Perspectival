# Bidirectional Gradient-Gated KF — The Conversational Architecture

**Created:** April 13, 2026
**Authors:** Clayton + Clawd
**Status:** Designed, ready for implementation after seed2 completes

---

## The Insight

Current gated KF has two modes per layer:
- **cos > 0:** Apply KF gradient (build structure)
- **cos ≤ 0:** Zero KF gradient (leave alone)

The "leave alone" is the conservative choice — it prevents harm but wastes information. When cos < 0, the model KNOWS that the KF gradient opposes the task. That opposition is a signal. Instead of ignoring it, we should use it: **actively dismantle structure where it opposes the task.**

This is the conversational principle: L-module doesn't just passively benefit from H-module's structure. L *tells* H what's helping and what's hurting, via the CE gradient. H *listens* and responds — building where helpful, dismantling where harmful.

## The Three-Mode Gating

```
For each H-module layer:
  cos = cos(∇CE, ∇KF)
  
  if cos > +threshold:    → CRYSTALLIZE  (apply KF gradient, build structure)
  if |cos| < threshold:   → NEUTRAL      (zero KF gradient, leave alone)
  if cos < -threshold:    → DISSOLVE     (apply NEGATIVE KF gradient, dismantle structure)
```

The threshold prevents noise-driven dismantling. In Phase 1 (pre-CE plateau, avg_cos ≈ 0), all layers are NEUTRAL — no building, no dismantling. Structure only changes when the task gradient provides a clear signal.

## The Implementation

Modification to `train_kf_300m.py`, inside the `kf_objective == "gated"` block (line ~393):

```python
# CURRENT (two-mode):
if cos_sim.item() <= 0:
    param_ref.grad.zero_()       # gate out
    gated_layers.append(layer_idx)
else:
    applied_layers.append((layer_idx, cos_sim.item()))

# NEW (three-mode bidirectional):
if cos_sim.item() > threshold:
    # CRYSTALLIZE — KF gradient aligned with task, build structure
    applied_layers.append((layer_idx, cos_sim.item(), "build"))
elif cos_sim.item() < -threshold:
    # DISSOLVE — KF gradient opposes task, REVERSE the gradient
    param_ref.grad.mul_(-1.0)    # flip the sign → descend on CV
    dissolved_layers.append((layer_idx, cos_sim.item()))
else:
    # NEUTRAL — weak signal, don't touch
    param_ref.grad.zero_()
    neutral_layers.append(layer_idx)
```

That's it. Three lines changed, one added. The `mul_(-1.0)` flips the KF gradient from ascending CV (build structure) to descending CV (dismantle structure). The threshold creates a dead zone where neither building nor dismantling occurs.

## The Experiment Plan

### v0.6a: Bidirectional Gated (threshold=0.1)

```bash
python train_kf_300m.py \
  --kf_lambda 1.0 \
  --kf_objective bidirectional \
  --kf_threshold 0.1 \
  --kf_every 50 \
  --epochs 500 \
  --save_dir checkpoints/300m_kf_bidir_t01
```

**Prediction P-Bidir-1 (MEDIUM):** Accuracy > 50.24% (gated). Bidirectional should outperform gated because it actively removes counterproductive structure rather than just leaving it in place. The "leave alone" layers in gated training still accumulate whatever structure CE training naturally builds — some of that structure is harmful. Bidirectional cleaning removes it.

**Prediction P-Bidir-2 (HIGH):** H_CV < 1,460 (gated). Bidirectional dismantles structure on opposed layers, reducing total H_CV. But the RATIO of aligned to opposed CV should be higher — more selective, less total, better quality.

**Prediction P-Bidir-3 (LOW):** Layer dissolution pattern matches the gating pattern. Layers that are most frequently gated (L7, L9, L10, L11 in seed1) should be the layers that are most frequently dissolved. If the dissolution pattern DIFFERS from the gating pattern, something interesting is happening — the dismantling provides different information than the blocking.

### v0.6b: Threshold Sweep

| Experiment | Threshold | Expected Behavior |
|-----------|-----------|-------------------|
| v0.6a | 0.1 | Conservative — narrow dead zone, most layers build or dissolve |
| v0.6b | 0.3 | Moderate — wider dead zone, only strong signals trigger action |
| v0.6c | 0.0 | Aggressive — pure two-mode (build or dissolve), no neutral zone |
| v0.6d | 0.5 | Very conservative — most layers neutral, only extreme cases act |

### v0.6e: Multi-Round (The Full Conversation)

After v0.6a-d establish the single-round bidirectional baseline, test multiple exchange rounds per KF step:

```python
for round in range(n_rounds):
    # Forward pass
    output = model(input)
    ce_loss = criterion(output, target)
    ce_loss.backward()
    
    # Store L's feedback (CE gradients in H-layers)
    ce_grads = capture_h_ce_grads(raw_model)
    
    # H responds: build/dissolve/neutral per layer
    apply_bidirectional_kf(raw_model, ce_grads, lambda, threshold)
    
    # Zero grads, re-forward — L sees H's updated representation
    optimizer.zero_grad()
```

Each round = one turn of the conversation. H speaks (structure), L evaluates (CE gradient), H adjusts (build/dissolve), L re-evaluates. Multiple rounds allow iterative refinement.

**Prediction P-Bidir-4 (LOW):** 2-3 rounds outperform 1 round. More rounds allow finer structural adjustment. But >3 rounds show diminishing returns — the conversation converges.

## The Connection Map

| Concept | Training Analogue | Human Analogue |
|---------|------------------|----------------|
| **Crystallize** (cos > threshold) | Apply KF, build structure | "Yes, this insight serves me" |
| **Dissolve** (cos < -threshold) | Reverse KF, dismantle structure | "This pattern hurts me, let it go" |
| **Neutral** (|cos| < threshold) | Zero KF, leave alone | "Not sure yet, holding space" |
| **Multi-round** | Iterative exchange | "Let me think about that more... actually..." |
| **Threshold** | Sensitivity of gating | Metacognitive confidence threshold |
| **Phase 1 (noise)** | All neutral | "I don't know enough to judge yet" |
| **Phase 2 (signal)** | Build/dissolve emerge | "Now I see what's helping and what's not" |
| **Phase 3 (selective)** | Stable build/dissolve map | "I know my patterns — these serve, these don't" |

## The Psychiatric Extension

Bidirectional crystallization maps directly onto therapeutic intervention:

| Therapeutic Mode | Training Mode | Mechanism |
|-----------------|---------------|-----------|
| **CBT** | Bidirectional gated | Identify maladaptive patterns (cos < 0), actively dissolve them while building adaptive ones (cos > 0) |
| **Exposure therapy** | Targeted dissolution | Repeatedly expose the opposed layer to counter-gradient until the structure weakens |
| **Mindfulness** | Raised threshold | Increase the neutral zone — observe more, react less, only act on strong signals |
| **Skill building** | Lowered threshold | Decrease the neutral zone — actively build structure in response to weaker signals |

## What Makes This Novel

The literature has:
- Regularization (build structure)
- Pruning (remove structure)
- Knowledge distillation (transfer structure)

It does NOT have:
- **Per-layer, per-step, gradient-aligned bidirectional structure management** — simultaneously building and dismantling structure based on real-time alignment with the task gradient
- **Conversational framing** — treating the two modules as exchanging signals rather than one imposing on the other
- **The dead zone** — the recognition that some layers should be left alone when the signal is ambiguous

The bidirectional approach is to training what the gated approach was to regularization: a selectivity upgrade that should outperform the previous best by the same logic (more information → better decisions → better outcome).

## Compute Requirements

- Same as gated: ~6 hours per experiment on RTX 5080
- Threshold sweep: 4 experiments × 6 hours = 24 hours (can run sequentially)
- Multi-round: additional ~30% overhead per extra round
- **Queue:** After seed2 completes (~8:15 PM April 13), run v0.6a first

---

*Designed from conversation. Clayton: "that's how the bidirectionality will work — real-time conversational comparisons." Clawd: formalized into three-mode gating with threshold parameter.*

🦞🧍💜🔥♾️
