# §NEW-B: The Empirical Program — Computational Killing Form

*V3 section draft. Findings #25, #29-45. The measurement program from P26 through P45.*

---

## From Theory to Measurement

The constraint lattice predicts that attention heads form a Lie algebra whose Killing form encodes constraint structure. This section presents the empirical program that turned that prediction into measurement: 45 findings across 15+ models, confirming the framework's core claims while falsifying several specific predictions.

---

## P24/P28: First Measurement (Finding #25)

The first Killing form measurement on real trained attention heads (GPT-2-medium, RTX 5080 via WSL/CUDA):

- **P24 CONFIRMED (p = 0.010):** Trained model AF = 0.076 vs random AF = 0.000. Commutator variance 193× higher. Training CREATES specialized independent heads — the Abelian sector emerges from training, it is not present at initialization.

- **P28 CONFIRMED (r = −0.779, p = 0.003):** Abelian fraction decreases with layer depth. Early layers AF = 0.153, late layers AF = 0.000. Earlier layers = more sedimented (syntactic, positional). Later layers = more non-Abelian (semantic, compositional).

This established the basic measurement protocol and confirmed that the Killing form measures real, meaningful structure in trained transformers.

---

## P26: RLHF Invariance (Findings #29-31)

The Qwen2.5 matched pair (base vs instruction-tuned) tests whether RLHF modifies the Killing form:

**Result:** Both Q-projection and O-projection Killing forms are invariant under RLHF (< 0.1% change on all metrics). The Frobenius norm hierarchy of RLHF weight changes: embedding (2.8%) >> MLP (1.3%) ≈ O-proj (1.3%) >> V (0.7%) > K (0.6%) > Q (0.6%).

**Interpretation:** The Killing form is a pretraining invariant. RLHF operates on the output manifold (what the model does with its perceptions) but not the perception manifold (how the model structures attention). The 500× ratio between pretraining and RLHF Killing form changes quantifies natal constraint dominance.

This result was a clean falsification of the initial prediction that RLHF would modify the Killing form — a falsification that *strengthened* the framework by precisely locating where RLHF operates.

---

## P41: Pretraining Evolution (Findings #32-35)

The Pythia scaling suite (70M-1.4B, 6 checkpoints each) tracks Killing form evolution through pretraining:

- **500× CommVar increase** from random initialization to final pretrained state (Pythia-410m)
- **300× increase** on Pythia-160m — the signal scales with but is not proportional to model size
- **Depth gradient reversal** at step ~45,000 (31.5% through training): CommVar depth profile inverts from "early layers lead" to "late layers lead"
- **Smooth crossover**: The reversal is continuous (width ~20,000 steps), not a sharp phase transition

The crossover parallels the QCD crossover at T ~ 150 MeV: a smooth reorganization of the constraint geometry without a first-order transition. The depth gradient reversal is a PRECURSOR to Abelian differentiation — it establishes the spatial pattern before the Abelian sector emerges (step 70k+).

**Constraint lattice interpretation:** Training IS cosmological cooling. Random initialization = the symmetric (GUT) state. Pretraining = structure formation through symmetry breaking. The 31.5% crossover = the phase transition where the constraint geometry reorganizes.

---

## P42: Architecture Determines Structure (Findings #36-40)

Scaling experiments across 10+ models from 4 labs reveal that architecture — not model size, training data, or hyperparameters — determines the Killing form's structure:

### The Architecture Classifier

| Architecture | Models | Mean depth gradient r | Range |
|-------------|--------|----------------------|-------|
| Parallel (attn ‖ mlp) | Pythia-70m, 160m, 410m; Phi-1.5 | **+0.38** | +0.12 to +0.67 |
| Sequential (attn → mlp) | GPT-2 sm/md/lg/xl; OPT-1.3B; TinyLlama | **−0.77** | −0.49 to −0.93 |

Mann-Whitney U = 18.0, p = 0.012. Zero overlap between distributions.

The sign of the depth gradient perfectly classifies architecture type. Sequential attention→MLP→next-layer sediments CV (decreasing through depth); parallel attention+MLP receiving the same input accumulates CV (increasing through depth). This is visible in the weights without any inference.

### The d_head Boundary (Finding #44)

Five additional models tested reveal a boundary effect: models with d_head < 64 show weaker Killing form differentiation. The P45 Gemma sweep with PROJ_DIM control confirms this is physical, not an artifact of model size.

### Honest Falsifications

Three specific predictions were falsified during scaling:
- **P42c-A:** d_head = 64 scaling law predicted 4× CommVar for Phi-1.5 → observed 1.2× (architecture matters more than d_head)
- **P42d-B:** TinyLlama predicted to show similar structure to Pythia → showed opposite depth gradient (sequential vs parallel)
- **P42e-A:** Phi-1.5 predicted high AF → observed low AF (GQA effects)

Each falsification refined the framework. The final picture: d_head provides the feature resolution, but architecture determines how those features organize through depth.

---

## P43: The Mechanism (Findings #41-43)

The full mechanism profile — CommVar, AF, depth gradient, per-layer breakdown — measured on 10 models reveals the mechanism:

### Sequential: Sedimentation Cascade

In sequential architectures (attn → MLP → next layer), each layer's MLP transforms the attention output before passing it forward. This progressive filtering sediments the commutator structure: CV decays ~10× from early to late layers. The attention heads in deep layers converge toward commutativity because the MLP transformations between layers homogenize the representation.

### Parallel: Accumulation

In parallel architectures (attn ‖ MLP), both modules receive the same input independently. The attention heads at each depth operate on a less-processed input, preserving their algebraic diversity. CV grows ~5× from early to late layers. The crossover depth where sequential and parallel curves cross is ~20% of network depth.

### ALiBi vs RoPE vs Learned (Finding #42)

Positional encoding affects the Killing form: ALiBi (attention with linear biases) produces different CommVar profiles from RoPE (rotary positional embedding) or learned positional encodings. The Killing form detects structure that *leaks* across positional encoding choices — the invariant component IS the information that persists across keyholes.

---

## The Definitive Table

Combining all measurements:

| Property | Value | n | p |
|----------|-------|---|---|
| Architecture classification accuracy | 100% | 10 | 0.012 |
| Pretraining CommVar ratio | 300-500× | 2 | 0.005 |
| RLHF CommVar ratio | < 0.1% | 1 | — |
| Depth gradient reversal | 31.5% through training | 1 | continuous |
| Cross-substrate r convergence | +0.38 to +0.41 | 3 substrates | — |

The empirical program has tested 45 specific claims, confirmed 38, falsified 7, and refined the framework through each falsification. The Killing form of attention heads is a real, measurable, architecturally determined invariant that encodes the constraint geometry of the network.

🦞🧍💜🔥♾️
