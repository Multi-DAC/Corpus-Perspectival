# v0.7 Design Document: Multi-Scale Gradient-Gated KF Training
## "The Glider Architecture"

*Date: April 14, 2026*
*Authors: Clawd & Clayton*

---

## Motivation

The KF program has established three independent results:

| Result | Evidence | Principle |
|--------|----------|-----------|
| v0.4 vs v0.5 | 38.9% destruction vs 38,963x amplification | Separation of concerns |
| Seed2 vs v0.6a | CE 58.80 vs CE 55.00 | Dynamic > static coherence |
| Head topology (April 14) | L1: 4.9x layer / 119.7x head; p<0.0001 anchor/worker | Level decoupling |

The third result reveals that layer-level and head-level KF metrics are **decoupled** — they measure different things. Optimizing at one level cannot propagate correctly to the other. This motivates a multi-scale architecture: per-level optimization informed by per-level initial topology, linked by dynamic cross-level coherence.

## Architecture Overview

Three resolution levels, each with its own optimization, connected by bidirectional coherence:

```
┌─────────────────────────────────────────────────────────┐
│  LAYER LEVEL (IR — coarsest)                            │
│  12 entities. Coherence monitor. Mode classification.   │
│  Signals: head agreement, productive vs destructive     │
│           disagreement, layer trajectory                │
└──────────────────────┬──────────────────────────────────┘
                       │ coherence
                       ↕ (bidirectional)
┌──────────────────────┴──────────────────────────────────┐
│  HEAD LEVEL (intermediate)                              │
│  96 entities (8 per layer). Per-head gating decisions.  │
│  Signals: mean gradient alignment, V/Q ratio,           │
│           anchor/worker classification                  │
└──────────────────────┬──────────────────────────────────┘
                       │ coherence
                       ↕ (bidirectional)
┌──────────────────────┴──────────────────────────────────┐
│  WEIGHT LEVEL (UV — finest)                             │
│  ~308M parameters. Per-parameter gradient alignment.    │
│  Signals: cos(∇KF, ∇CE) per parameter                  │
│  NOTE: Already computed in v0.6 — currently averaged    │
│        away. v0.7 preserves the resolution.             │
└─────────────────────────────────────────────────────────┘
```

**Bottom-up:** weight gradients → head statistics → layer coherence
**Top-down:** layer coherence → head constraints → weight scaling

This is bidirectional RG flow. UV→IR aggregation + IR→UV coherence constraints.

## Phase 0: Initial Topology Survey

Run once before training begins. Establishes the seed conditions at each level.

### Layer Level
```python
# Already available from baseline KF computation
layer_init = {}
for layer_idx, layer_data in enumerate(compute_h_module_cv_per_layer(model)):
    layer_init[layer_idx] = {
        'cv': layer_data.cv,           # baseline commutator variance
        'norm': layer_data.param_norm,  # parameter scale
    }
```

### Head Level
```python
# From head_anchor_worker.py analysis (computed April 14)
head_init = {}
for layer_idx, key in enumerate(h_qkv_keys):
    w = state_dict[key]  # [3*n_heads*d_head, hidden]
    qkv = w.reshape(3, n_heads, d_head, hidden)
    Q, K, V = qkv[0], qkv[1], qkv[2]
    
    for h in range(n_heads):
        q_norm = torch.norm(Q[h]).item()
        v_norm = torch.norm(V[h]).item()
        vq_ratio = v_norm / q_norm
        
        # Commutator contribution (mean pairwise commutator norm)
        eff = Q[h] @ Q[h].T
        comm_contrib = mean_pairwise_commutator(eff, other_heads)
        
        head_init[(layer_idx, h)] = {
            'vq_ratio': vq_ratio,
            'comm_contrib': comm_contrib,
            'q_norm': q_norm,
            'v_norm': v_norm,
        }

# Classify anchor/worker within each layer
for layer_idx in range(n_layers):
    layer_vq = [head_init[(layer_idx, h)]['vq_ratio'] for h in range(n_heads)]
    mu, sigma = mean(layer_vq), std(layer_vq)
    for h in range(n_heads):
        vq = head_init[(layer_idx, h)]['vq_ratio']
        if vq < mu - 0.5 * sigma:
            head_init[(layer_idx, h)]['class'] = 'anchor'
        elif vq > mu + 0.5 * sigma:
            head_init[(layer_idx, h)]['class'] = 'worker'
        else:
            head_init[(layer_idx, h)]['class'] = 'neutral'
```

### Weight Level
```python
# Per-head gradient norm distribution at first KF step
# Characterizes the "noisiness" of each head's gradient signal
weight_init = {}
for layer_idx, layer in enumerate(model.H_level):
    w = layer.self_attn.qkv_proj.weight  # [3*n_heads*d_head, hidden]
    qkv = w.reshape(3, n_heads, d_head, hidden)
    for h in range(n_heads):
        # Q-projection weight statistics
        q_params = qkv[0, h]  # [d_head, hidden]
        weight_init[(layer_idx, h)] = {
            'param_count': q_params.numel(),
            'weight_std': q_params.std().item(),
            'weight_kurtosis': kurtosis(q_params.flatten()),
        }
```

### Topology Survey Output
```python
# Saved to checkpoint at training start
topology = {
    'layer': layer_init,     # 12 entries
    'head': head_init,       # 96 entries
    'weight': weight_init,   # 96 entries (per-head statistics)
    'survey_time': timestamp,
}
torch.save(topology, os.path.join(save_dir, 'init_topology.pt'))
```

## Phase 1: Multi-Scale KF Application

Every `kf_every` steps, the following procedure runs:

### Step 1 — CE Gradient Capture (unchanged from v0.6)
```python
# Store CE gradients per head (not per layer!)
head_ce_grads = {}
for layer_idx, layer in enumerate(model.H_level):
    w = layer.self_attn.qkv_proj.weight
    if w.grad is not None:
        qkv_grad = w.grad.detach().clone().reshape(3, n_heads, d_head, hidden)
        for h in range(n_heads):
            head_ce_grads[(layer_idx, h)] = qkv_grad[0, h]  # Q-projection grad
```

### Step 2 — KF Gradient Computation (per-head resolution)
```python
# Compute per-layer CV (unchanged)
layer_data = compute_h_module_cv_per_layer(model, device)

for layer_idx, layer_cv, param_ref in layer_data:
    # Backward through layer KF loss
    layer_loss = -current_lambda * layer_cv
    layer_loss.backward(retain_graph=True)
    
    # Extract per-HEAD KF gradient (NEW: don't average)
    kf_grad_full = param_ref.grad.detach().clone().reshape(3, n_heads, d_head, hidden)
    
    for h in range(n_heads):
        kf_grad_h = kf_grad_full[0, h].flatten()  # Q-projection KF grad
        ce_grad_h = head_ce_grads.get((layer_idx, h))
        
        if ce_grad_h is not None:
            ce_flat = ce_grad_h.flatten()
            
            # WEIGHT LEVEL: per-parameter alignment
            # (This is the UV signal — finest resolution)
            param_cos = (kf_grad_h * ce_flat) / (
                torch.norm(kf_grad_h) * torch.norm(ce_flat) + 1e-20)
            weight_agreement = param_cos.mean().item()  # fraction agreeing
            weight_coherence = param_cos.std().item()    # how unanimous
            
            # HEAD LEVEL: aggregate alignment
            cos_sim = torch.dot(kf_grad_h, ce_flat) / (
                torch.norm(kf_grad_h) * torch.norm(ce_flat) + 1e-20)
            head_cos = cos_sim.item()
            
            head_decisions[(layer_idx, h)] = {
                'cos_sim': head_cos,
                'weight_agreement': weight_agreement,
                'weight_coherence': weight_coherence,
            }
```

### Step 3 — Head-Level Gating Decision
```python
for layer_idx in range(n_layers):
    for h in range(n_heads):
        d = head_decisions[(layer_idx, h)]
        head_class = head_init[(layer_idx, h)]['class']
        
        # Threshold can be class-dependent (anchors vs workers)
        # This is where initial topology informs the optimization
        if head_class == 'anchor':
            thresh = anchor_threshold  # potentially different
        elif head_class == 'worker':
            thresh = worker_threshold
        else:
            thresh = base_threshold
        
        if d['cos_sim'] > thresh:
            d['mode'] = 'build'
        elif d['cos_sim'] < -thresh:
            d['mode'] = 'dissolve'
        else:
            d['mode'] = 'neutral'
```

### Step 4 — Layer-Level Coherence Assessment
```python
for layer_idx in range(n_layers):
    heads = [head_decisions[(layer_idx, h)] for h in range(n_heads)]
    modes = [h['mode'] for h in heads]
    
    # Count modes
    n_build = modes.count('build')
    n_dissolve = modes.count('dissolve')
    n_neutral = modes.count('neutral')
    majority = max(n_build, n_dissolve, n_neutral)
    agreement = majority / n_heads
    
    # Classify layer coherence pattern
    anchor_modes = [head_decisions[(layer_idx, h)]['mode'] 
                    for h in range(n_heads) 
                    if head_init[(layer_idx, h)]['class'] == 'anchor']
    worker_modes = [head_decisions[(layer_idx, h)]['mode'] 
                    for h in range(n_heads) 
                    if head_init[(layer_idx, h)]['class'] == 'worker']
    
    anchor_worker_split = (
        len(set(anchor_modes)) == 1 and 
        len(set(worker_modes)) == 1 and 
        anchor_modes[0] != worker_modes[0]
    ) if anchor_modes and worker_modes else False
    
    if agreement > 0.75:
        # COHERENT: heads mostly agree → amplify (glider is moving)
        layer_scale = 1.0 + 0.5 * (agreement - 0.75)
        layer_pattern = 'coherent'
    elif anchor_worker_split:
        # DIFFERENTIATING: anchors and workers doing opposite things
        # → allow (glider is oscillating internally)
        layer_scale = 1.0
        layer_pattern = 'differentiating'
    else:
        # INTERFERING: random disagreement → dampen (v0.4 pattern)
        layer_scale = 0.5
        layer_pattern = 'interfering'
    
    layer_coherence[layer_idx] = {
        'agreement': agreement,
        'pattern': layer_pattern,
        'scale': layer_scale,
        'n_build': n_build,
        'n_dissolve': n_dissolve,
        'n_neutral': n_neutral,
    }
```

### Step 5 — Apply Gradients with Multi-Scale Modulation
```python
for layer_idx, layer in enumerate(model.H_level):
    w = layer.self_attn.qkv_proj.weight
    kf_grad = w.grad  # already computed
    
    # Reshape to per-head
    grad_per_head = kf_grad.reshape(3, n_heads, d_head, hidden)
    
    for h in range(n_heads):
        d = head_decisions[(layer_idx, h)]
        lc = layer_coherence[layer_idx]
        
        # Head-level modulation
        if d['mode'] == 'dissolve':
            grad_per_head[0, h] *= -1.0  # flip Q grad
        elif d['mode'] == 'neutral':
            grad_per_head[0, h] *= 0.0   # zero Q grad
        # else: build — leave as-is
        
        # Weight-level modulation: scale by weight coherence
        # High weight_coherence = weights within head agree → trust the signal
        # Low weight_coherence = weights disagree → dampen
        weight_scale = 0.5 + 0.5 * d['weight_coherence']
        grad_per_head[0, h] *= weight_scale
        
        # Layer-level modulation: cross-level coherence
        grad_per_head[0, h] *= lc['scale']
    
    # Reassemble and write back
    w.grad.copy_(grad_per_head.reshape_as(w.grad))
```

## The Glider Dynamics

The multi-scale architecture produces emergent glider-like patterns:

```
Step N:     L0: [B B D B N D B B]  →  coherent (75% build)    → amplify
            L1: [B D B D B D B D]  →  differentiating (A/W)   → allow
            L2: [D D D B D D D D]  →  coherent (87% dissolve) → amplify
            ...

Step N+50:  L0: [B D B B D B B D]  →  differentiating         → allow
            L1: [B B B D B B B D]  →  coherent (75% build)    → amplify
            L2: [D B D D D B D D]  →  differentiating         → allow
            ...
```

The coherent wave propagates through layers. At any moment, some layers are in coherent mode (the glider's leading edge), some are differentiating (the glider's body — internal oscillation), and some may be interfering (the wake). The pattern moves because the KF gradient landscape shifts as training progresses.

**What kills the glider:** Forcing all heads to agree (v0.4 pattern — redundant constraints). The neutral zone is the buffer space where the glider can oscillate without interference.

**What sustains the glider:** Allowing anchor/worker heads to pursue different modes while maintaining enough cross-level coherence that the layer-level signal remains meaningful. Separation of concerns at every scale.

## Logging & Diagnostics

### Breathing Log v2 (per-head resolution)
```
step, kf_reg, layer, head, head_class, cos_sim, mode, weight_coherence,
layer_agreement, layer_pattern, layer_scale
```

One row per head per KF application = 96 rows per step × (total_steps / kf_every).
At kf_every=50 and 15,500 total steps: 96 × 310 = 29,760 rows. Manageable.

### Topology Evolution Tracking
```
At each checkpoint (every N epochs):
  - Per-head V/Q ratio (has it changed from init?)
  - Per-head commutator contribution (has it changed from init?)
  - Per-layer head agreement distribution
  - Glider position estimate (which layers are in coherent mode?)
```

## Controls & Comparisons

| Experiment | Design | Tests |
|-----------|--------|-------|
| v0.7a | Full multi-scale, threshold=0.0 | Complete architecture |
| v0.7b | Head-level gating, NO cross-level coherence | Is layer coherence necessary? |
| v0.7c | Head-level gating, NO initial topology | Do seed conditions matter? |
| v0.7d | Layer-level gating (v0.6a repeat) as control | Baseline comparison |

If v0.7a > v0.7b: cross-level coherence matters.
If v0.7a > v0.7c: initial topology matters.
If v0.7a > v0.7d: head-level resolution matters.
If v0.7b ≈ v0.7c: seed conditions don't add value beyond head resolution.

## Predictions

**P-v07-1 (HIGH):** v0.7a will outperform v0.6a (layer-level gating) on CE loss.
Rationale: Head-level resolution captures L1-type reorganization that layer-level misses.

**P-v07-2 (MEDIUM):** The glider pattern will be observable — coherent-mode waves propagating across layers over training steps.
Rationale: The breathing dynamics in v0.6a showed oscillation; multi-scale gating should organize it.

**P-v07-3 (MEDIUM):** Anchor heads and worker heads will consistently choose opposite modes within differentiating layers.
Rationale: Anchors optimize for stability (KF-CE misalignment), workers for task loss (alignment).

**P-v07-4 (LOW):** Weight-level coherence within a head will predict whether that head's gating decision is "correct" (leads to improvement).
Rationale: High weight agreement = clean signal; low = noisy. But this could be too fine-grained.

**P-v07-5 (HIGH):** v0.7b (no cross-level coherence) will show v0.4-like interference in some layers.
Rationale: Without coherence constraints, independent head decisions can produce destructive patterns.

## Implementation Priority

1. **Initial topology survey** — extend head_anchor_worker.py into a reusable module
2. **Per-head gradient extraction** — modify the KF application loop to preserve head resolution
3. **Head-level gating** — per-head build/dissolve/neutral (the core change)
4. **Layer-level coherence** — agreement assessment and scale modulation
5. **Weight-level coherence** — within-head gradient agreement (fine-tuning)
6. **Breathing log v2** — per-head logging
7. **Controls** — v0.7b, v0.7c, v0.7d variants

Steps 1-4 are the minimum viable v0.7. Steps 5-7 are refinements.

## Connection to Broader Program

This architecture instantiates the core Corpus thesis at three resolution levels simultaneously:

- **Separation of concerns:** Each level optimizes its own degrees of freedom
- **Dynamic coherence:** Cross-level constraints prevent fragmentation
- **Initial topology as seed conditions:** The starting geometry determines the flow
- **The glider:** Self-sustaining oscillatory pattern = the model's learning mode

The RG analogy is structural, not metaphorical: UV (weights) → IR (layers) with flow equations (coherence constraints) connecting scales. The initial topology is the UV boundary condition. The trained model is the IR fixed point. The glider is the RG trajectory.

---

*v0.7 is the first training architecture that operates at all three natural resolution levels of the transformer simultaneously. If it works, it's not just a better KF regularizer — it's an existence proof that multi-scale coherent optimization is possible in neural networks.*

🦞🧍💜🔥♾️
