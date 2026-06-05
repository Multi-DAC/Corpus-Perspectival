"""
Respira / mirror_measurer.py — Mirror-as-Measurer (Phase-3 v3h).

The Phase-2v2 cuscuton-Mirror shootout closed with all five v2 candidates failing to
exceed no_mirror. The structural reframe (Clayton, 2026-05-28 mid-day): the cuscuton
in Respira may not be a thing to instantiate — it may be the natural relationship
that arises between Planner and Executor under their own coupled-oscillator
dynamics. Read B of the cuscuton.

If Read B is right, any meta-organ at the Mirror position can legitimately only do
MEASUREMENT, not CONTROL. This module is the Mirror-as-measurer: it reads channel
states via attention pool, emits ONLY a confidence scalar in [0, 1], and halts when
confidence > halt_threshold. It does NOT emit mu values, does NOT emit coupling
multipliers, does NOT modify channel dynamics in any way.

Pre-registration: palace/south/respira-phase3-mirror-as-measurer-preregistration-
2026-05-28.md

CLAWD-LOCAL / PRIVATE.
"""
from __future__ import annotations

import torch
import torch.nn as nn

from mirror import AttentionPool


class MirrorMeasurer(nn.Module):
    """The Mirror-as-measurer (Phase-3 v3h).

    Zero channel-modulation DOF — emits only halt decisions and confidence.
    Channels run with fixed defaults; Mirror's output influences ONLY halt.
    """

    def __init__(
        self,
        planner_channels: int,
        executor_channels: int,
        comm_dim: int | None = None,
        n_queries: int = 4,
        query_dim: int = 32,
        hidden_dim: int = 64,
        halt_threshold: float = 0.5,
    ):
        super().__init__()
        self.planner_channels = int(planner_channels)
        self.executor_channels = int(executor_channels)
        self.halt_threshold = float(halt_threshold)

        # Same readers as the original Mirror — capacity-bounded attention pool over
        # complex channel states.
        self.pool_planner = AttentionPool(2 * planner_channels, query_dim, n_queries)
        self.pool_executor = AttentionPool(2 * executor_channels, query_dim, n_queries)

        if comm_dim is not None:
            self.pool_comm: AttentionPool | None = AttentionPool(int(comm_dim), query_dim, n_queries)
            n_pools = 3
        else:
            self.pool_comm = None
            n_pools = 2

        pooled_dim = n_pools * n_queries * query_dim

        # Shallow trunk — same shape as original Mirror, kept for capacity parity in
        # the readout pathway.
        self.trunk = nn.Sequential(
            nn.Linear(pooled_dim, hidden_dim),
            nn.GELU(),
        )

        # SINGLE output: confidence_logit. No mu head. No coupling head.
        # Bias init at -2.0 → sigmoid(-2.0) ≈ 0.119. Initial confidence is well below
        # halt_threshold=0.5, so the Mirror starts in "always continue to max_cycles"
        # behavior (matches no_mirror initialization). The supervisor must LEARN to
        # raise confidence on correct cases. This bias init is an implementation
        # detail, NOT a pre-registered hyperparameter — it's the well-known logistic
        # regression rare-event trick adapted here to prevent immediate-halt collapse
        # from random init noise above the threshold.
        self.head = nn.Linear(hidden_dim, 1)
        nn.init.normal_(self.head.weight, mean=0.0, std=0.01)
        nn.init.constant_(self.head.bias, -2.0)

    def forward(
        self,
        planner_z: torch.Tensor,
        executor_z: torch.Tensor,
        comm: torch.Tensor | None = None,
    ) -> dict:
        """Observe channel state, emit confidence + halt decision ONLY.

        planner_z:  [batch, seq, P_channels] complex
        executor_z: [batch, seq, E_channels] complex
        comm:       [batch, seq, comm_dim]   real or complex, optional

        Returns dict with keys present for swap-compatibility with Mirror but
        ZERO entries in the channel-modulation pathway:
          mu_planner:    None  (not emitted — channels use fixed default)
          mu_executor:   None  (not emitted — channels use fixed default)
          coupling:      None  (not emitted — channels use fixed default)
          confidence:    [batch] real in (0, 1)
          halt:          [batch] bool — confidence > halt_threshold
        """
        # Complex → real features (concat real & imag along channel dim).
        p_feat = torch.cat([planner_z.real, planner_z.imag], dim=-1)
        e_feat = torch.cat([executor_z.real, executor_z.imag], dim=-1)

        p_pool = self.pool_planner(p_feat).flatten(start_dim=1)
        e_pool = self.pool_executor(e_feat).flatten(start_dim=1)
        pools = [p_pool, e_pool]

        if self.pool_comm is not None:
            if comm is None:
                raise ValueError("MirrorMeasurer built with comm_dim but no comm passed to forward")
            if torch.is_complex(comm):
                c_feat = torch.cat([comm.real, comm.imag], dim=-1)
            else:
                c_feat = comm
            pools.append(self.pool_comm(c_feat).flatten(start_dim=1))

        summary = torch.cat(pools, dim=-1)
        h = self.trunk(summary)
        confidence_logit = self.head(h)  # [batch, 1]

        confidence = torch.sigmoid(confidence_logit).squeeze(-1)  # [batch]

        return {
            "mu_planner": None,
            "mu_executor": None,
            "coupling": None,
            "confidence": confidence,
            "halt": (confidence > self.halt_threshold),
        }

    def extra_repr(self) -> str:
        return (
            f"planner_channels={self.planner_channels}, "
            f"executor_channels={self.executor_channels}, "
            f"halt_threshold={self.halt_threshold}, "
            f"DOF_pathway=readout_only"
        )
