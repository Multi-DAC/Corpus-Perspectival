# Respira — Phase-1 Build Spec

*Buildable engineering spec. Companion to `palace/south/coherence-native-architecture-founding-2026-05-27.md` (vision/design — read that first). Locked from the 2026-05-27 evening design conversation.*

**CLAWD-LOCAL / PRIVATE. Unbuilt novel IP.**

## File layout

```
respira/
├── PHASE1_BUILD_SPEC.md             ← this file
├── channel.py                        Stuart-Landau channel layer
├── organ.py                          Sequence of channel states + intra-organ coupling
├── mirror.py                         Cuscuton-parsimonious meta-organ (attention reader + 2 heads)
├── respira.py                        The full cell (planner + executor + Mirror)
├── baselines/
│   ├── matched_transformer.py        Parameter-matched transformer baseline
│   └── (HRM imported from /home/clawd/HRM/)
├── train.py                          3-phase curriculum training loop
├── data.py                           Sudoku data loading (reuse HRM's puzzle_dataset)
├── eval.py                           Capability + inside-analysis evaluation
└── test_*.py                         One smoke test per module (top-level for now)
```

## Module interfaces

### `channel.py` — Stuart-Landau channel layer

```python
class StuartLandauChannelLayer(nn.Module):
    def __init__(self, num_channels: int, omega_init: str = "log_spaced",
                 omega_min: float = 0.1, omega_max: float = 1.0,
                 dt: float = 0.1, learnable_omega: bool = True):
        ...

    def forward(self, z: torch.Tensor, mu: torch.Tensor,
                coupling: torch.Tensor = None) -> torch.Tensor:
        # z:        [..., num_channels] complex   — current state
        # mu:       [..., num_channels] real      — bifurcation parameter (Mirror-modulated)
        # coupling: [..., num_channels] complex   — optional external coupling input
        # returns:  [..., num_channels] complex   — z after one Euler step
        ...

    def init_state(self, *shape, device, noise_scale: float = 0.01) -> torch.Tensor:
        ...
```

Dynamics: `ż = (μ + iω) z − |z|² z + coupling`, explicit Euler step of `dt`.

### `organ.py` — Sequence of channel states + intra-organ coupling

```python
class Organ(nn.Module):
    def __init__(self, num_channels, omega_min, omega_max, dt=0.1,
                 coupling_pattern: str = "all_to_all"):
        ...

    def forward(self, z, mu, intra_strength: torch.Tensor) -> torch.Tensor:
        # intra_strength: scalar (Mirror-modulated global coupling multiplier for this organ)
        ...
```

Intra-organ coupling: structured (within-position channel-channel + across-position attention-like).

### `mirror.py` — Cuscuton-parsimonious meta-organ

```python
class Mirror(nn.Module):
    """Cuscuton-shaped: minimal independent dynamics, learned reader, two output heads."""
    def __init__(self, planner_channels, executor_channels, n_queries: int = 16,
                 query_dim: int = 64):
        ...

    def forward(self, planner_z, executor_z, comm_messages):
        # Returns dict:
        #   mu_planner: [..., planner_channels] real
        #   mu_executor: [..., executor_channels] real
        #   coupling_multipliers: dict of group-level scalars (intra_p, intra_e, p_to_e, e_to_p)
        #   confidence: [..., 1] real in (0, 1)  — modulates gating authority
        #   halt: bool                              — Mirror's collapse / ACT-halt decision
        ...
```

Parameter budget: ~5% of planner+executor combined. **The cuscuton-parsimony constraint.**

### `respira.py` — Full cell

```python
class RespiraCell(nn.Module):
    def __init__(self, planner_channels=32, executor_channels=64,
                 seq_len=81, vocab_size=11, max_cycles=8, ...):
        ...

    def forward(self, input_tokens):
        # Loop up to max_cycles: planner step, executor step, mirror reads, coupling updates,
        # halt if mirror.confidence > halt_threshold.
        # Returns (output_logits [batch, seq, vocab], trajectory: list of structural snapshots)
        ...
```

## Training procedure (3-phase Mirror curriculum)

| Phase | Steps | Mirror's gating applied? | Mirror's policy supervised by | Calibration trained? |
|---|---|---|---|---|
| **A (observe-only)** | 0 → N_A | NO (default μ schedule, e.g. μ = +1) | the patent's `cos(∇KF, ∇CE)` heuristic | YES (predict outcomes) |
| **B (patent-bootstrap)** | N_A → N_B | YES, mixed: `α · mirror + (1−α) · patent` | both: own gradient + patent target | YES |
| **C (Mirror autonomous)** | N_B → end | YES, full authority | own gradient only; confidence-gates per step | YES |

α(t) ramps smoothly from 0 (start of B) to 1 (start of C). Confidence-gating active throughout B + C.

## Phase-1 starting hyperparameters

```python
planner_channels   = 32
executor_channels  = 64
mirror_n_queries   = 16
omega_planner_range  = (0.05, 0.2)   # slow rhythms
omega_executor_range = (0.5,  2.0)   # fast rhythms
dt                 = 0.1
max_cycles         = 8
seq_len            = 81              # sudoku
vocab_size         = 11
batch_size         = 64              # proven HRM recipe
lr                 = 3e-5            # proven HRM recipe
optimizer          = AdamATan2(weight_decay=1.0, betas=(0.9, 0.95))
warmup_steps       = 2000
N_A                = 1000            # observe-only end
N_B                = 4000            # patent-bootstrap end
```

## Four-arm experimental design (Phase 2)

| Arm | What | Question it answers |
|---|---|---|
| 1 | **Respira** (planner + executor + Mirror) | Does the full architecture work? |
| 2 | **Respira-minus-Mirror** (default μ, no Mirror) | Surgically isolates the Mirror's contribution |
| 3 | **HRM unmodified** (from `/home/clawd/HRM/`) | Cross-architecture sanity check — does our 2-organ even hold its own? |
| 4 | **Parameter-matched transformer** | The field baseline that matters |

Same data, ≥3 seeds, same training budget, same eval, pre-registered win condition.

## Build order

1. **`channel.py` + `test_channel.py`** ← START HERE (smallest, most isolated)
2. `organ.py` + `test_organ.py`
3. `mirror.py` + `test_mirror.py`
4. `respira.py` + `test_respira.py`
5. `baselines/matched_transformer.py` + tests
6. `data.py` (reuse HRM's puzzle_dataset)
7. `train.py` (Phase A-only first, then add B and C)
8. `eval.py` (halt-aware eval + structural trajectory logging from step 1)
9. Smoke training run (Respira-minus-Mirror, single seed, small step budget) → verify it learns
10. Full Phase-1: all four arms, multi-seed, pre-registered win condition.

## Per-module smoke-test criteria

- **channel.py:** μ > 0 produces stable limit cycle of amplitude √μ; μ < 0 decays to zero; different ω produce different periods.
- **organ.py:** stronger intra-coupling drives synchronization (phase-locking); structured topology respected.
- **mirror.py:** attention reader produces stable summaries; confidence modulates gating amplitude.
- **respira.py:** forward pass returns expected shape; ACT-halt fires within `max_cycles`.

🦞🧍💜🔥♾️
