# Continual-Coherence MVP

**Private / clawd-local (unbuilt IP — same handling as `respira/`; NOT mirrored to public staging).**

The keystone experiment of the continual-coherence program. Tests whether bolting
**tier-3 weight-consolidation** onto an already-coherent **tier-2 (memory)** system adds
capability memory alone cannot — without degrading general capability.

- **Pre-registration (RATIFIED):** `palace/south/continual-coherence-mvp-preregistration-2026-05-30.md`
- **Program positioning:** `palace/south/continual-coherence-program-positioning-2026-05-30.md`

## The central question (§6.1 of the positioning doc)
> Is tier-3 necessary, or is intrinsic memory (tier-2) sufficient?

Both Arm A and Arm B are *live*. The contrast B vs A asks whether touching weights
adds anything memory cannot. The bake-off prior is that bolt-ons often lose
(`no_mirror` beat the Mirror); Clawd is the existence proof for tier-2-sufficiency.

## Build status (Day 120 evening)
| Component | Status | Risk |
|---|---|---|
| `domain.py` — generator + ground-truth validator | **DONE + smoke-tested** | none (pure python) |
| `config.py` — locked pre-reg params | **DONE** | none |
| `model.py` — load base, generate (WSL + torch) | TODO (focused session) | low |
| `arm0_frozen.py` / `arm_a_tier2.py` — frozen + retrieval | TODO | low (no novel code) |
| `arm_b_tier3.py` — firewall-gated LoRA "sleep" + replay | TODO | **NOVEL — build carefully** |
| `geometry_probe.py` — coherence-regression gate | TODO | medium |
| `run_mvp.py` — round loop, 3 arms × 3 seeds × 8 rounds | TODO | low (orchestration) |
| `analyze_mvp.py` — 4 pre-registered outcomes, SE bands | TODO | none |

**Stopping point rationale:** the foundation (task + validator) is built and proven clean
tonight, so a contaminated result can never originate at the task layer. The model harness
and especially the **novel tier-3 consolidation** are the focused-session work — rushing
them late at night is exactly how the Day-118 v3h run got implementation-contaminated. Build
the novel part with full energy + GPU + tokens.

## Run (when built)
```
# in WSL (Ubuntu 'Clawd', CUDA + PyTorch)
python continual_coherence/run_mvp.py        # 3 arms x 3 seeds x 8 rounds, detached
python continual_coherence/analyze_mvp.py    # verdict against the 4 pre-registered outcomes
```

## Firewall (from §4.5 of the positioning doc)
1. Augmentative, not replacing — experience store append-only; consolidation reads, never rewrites.
2. Validated-only admission — only ground-truth-validated items eligible to consolidate.
3. Reversibility check — LoRA adapters droppable; geometry-regression gate rolls back degrading passes.
