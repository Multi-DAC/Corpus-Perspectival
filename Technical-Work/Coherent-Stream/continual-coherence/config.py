"""
Continual-Coherence MVP — locked configuration.

These values are RATIFIED (Clayton, 2026-05-30 ~20:00 PST) per
palace/south/continual-coherence-mvp-preregistration-2026-05-30.md.
Do NOT tune mid-run. Changing any of these invalidates the pre-registration.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class MVPConfig:
    # --- base model (decision point 1; AMENDED 2026-05-30 post-calibration) ---
    # Gemma-3-270m floored at 0% on all multi-step difficulties (vacuous, can't bootstrap).
    # Switched to the pre-reg's listed alternative; bare d3 accuracy ~0.50 = ideal regime.
    base_model: str = "Qwen/Qwen2.5-0.5B"
    alt_model_for_replication: str = "google/gemma-3-270m"  # cross-arch only (single-step floor)

    # --- domain (decision point 2, locked) ---
    domain: str = "templated_ground_truth_arithmetic"
    difficulty: int = 3          # multi-step; 270m has headroom, not floor
    train_problems_per_round: int = 64
    held_in_test_size: int = 128   # in-domain capability trajectory
    held_out_general_size: int = 128  # forgetting check (general benchmark subset)

    # --- rounds / seeds (decision point 3, locked) ---
    n_rounds: int = 8
    seeds: tuple[int, ...] = (0, 1, 2)   # >=3, seed-0-deflation lesson

    # --- win-condition SE bands (decision point 4, locked) ---
    se_exceeds: float = 1.0      # >1 SE = real difference
    se_ties: float = 1.0         # within 1 SE = tie
    se_degrades: float = -1.0    # <-1 SE on held-out = forgetting

    # --- tier-3 consolidation (the novel component; hyperparams pre-set) ---
    lora_rank: int = 8
    lora_alpha: int = 16
    consolidation_lr: float = 1e-4
    consolidate_every_n_rounds: int = 1
    replay_ratio: float = 0.5    # new : retained core set during sleep
    gate_validated_only: bool = True   # firewall rule 2 — only ground-truth-validated data eligible
    geometry_regression_gate: bool = True  # firewall rule 3 — roll back degrading passes

    # --- arms ---
    arms: tuple[str, ...] = ("frozen_bare", "tier2_memory", "tier2_tier3")

    # --- bookkeeping ---
    results_dir: str = "continual_coherence/results"
    private_ip: bool = True   # clawd-local only; NOT mirrored to public staging (same as respira/)


CONFIG = MVPConfig()
