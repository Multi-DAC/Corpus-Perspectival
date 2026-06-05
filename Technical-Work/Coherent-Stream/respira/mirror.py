"""
Respira / mirror.py — The cuscuton-parsimonious meta-organ.

Design (from PHASE1_BUILD_SPEC §0.5 and the founding-doc §0.5 convergence):

The Mirror is the keystone — one component demanded by four orthogonal needs at once:
  • Evaluator (makes the model transparent)
  • Build/dissolve driver (emits the μ values that govern channel rest-vs-limit-cycle)
  • Deadlock breaker (arbitrates planner ↔ executor)
  • Measurement-collapse (its halt decision is the Coherence-Principle "informed measurement")

Cuscuton-parsimony principle (from the Meridian brane/bulk/cuscuton parallel):
  The Mirror has MINIMAL independent dynamics — a learned reader + a shallow MLP +
  output projection. No deep stack, no recurrence of its own, no large internal latent.
  It is a *constraint coordinator*, not a third brain.

Architecture:
  1. Attention-pool each input (planner state, executor state, optional comm) into a
     fixed-size summary regardless of seq length.
  2. Concatenate summaries, pass through a small MLP trunk.
  3. Single output head emits, jointly:
       • mu_planner   [batch, P_channels] — per-channel bifurcation control
       • mu_executor  [batch, E_channels] — per-channel bifurcation control
       • coupling_mults: 4 scalars (intra_p, intra_e, p→e, e→p)  — Organ-level dials
       • confidence   [batch]              — modulates gating authority + halt decision
  4. Confidence modulates μ amplitude:  μ = mu_scale · confidence · tanh(raw_μ)
       • confidence ≈ 0 → μ ≈ 0 → channel left alone (NEUTRAL)
       • confidence ≈ 1 → μ ≈ ±mu_scale → committed BUILD or DISSOLVE
       The patent's three-mode gating falls out of the Mirror's own calibrated
       uncertainty — NOT from a hyperparameter threshold.

The Mirror emits PER-BATCH values, broadcast over sequence positions when applied
in respira.py. This keeps the Mirror's output budget cuscuton-parsimonious.

CLAWD-LOCAL / PRIVATE.
"""
from __future__ import annotations

import math
import torch
import torch.nn as nn


class AttentionPool(nn.Module):
    """Cross-attention pool: read a sequence into n_queries fixed summary vectors.

    Q is a small bank of learned query vectors (the Mirror's "things it looks for").
    K, V are projected from the input sequence. Output is attention(Q, K, V).

    This is the Mirror's *reader* — its capacity-bounded view of an organ's state.
    """

    def __init__(self, in_dim: int, query_dim: int, n_queries: int):
        super().__init__()
        self.n_queries = n_queries
        self.query_dim = query_dim
        self.scale = 1.0 / math.sqrt(query_dim)
        self.queries = nn.Parameter(torch.randn(n_queries, query_dim) * 0.1)
        self.k_proj = nn.Linear(in_dim, query_dim, bias=False)
        self.v_proj = nn.Linear(in_dim, query_dim, bias=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """x: [batch, seq, in_dim] real → [batch, n_queries, query_dim] real."""
        K = self.k_proj(x)  # [batch, seq, query_dim]
        V = self.v_proj(x)  # [batch, seq, query_dim]
        # attention scores: [batch, n_queries, seq]
        scores = torch.einsum("qd,bsd->bqs", self.queries, K) * self.scale
        attn = scores.softmax(dim=-1)
        # weighted values: [batch, n_queries, query_dim]
        out = torch.einsum("bqs,bsd->bqd", attn, V)
        return out


class Mirror(nn.Module):
    """The cuscuton-parsimonious meta-organ."""

    def __init__(
        self,
        planner_channels: int,
        executor_channels: int,
        comm_dim: int | None = None,
        n_queries: int = 4,
        query_dim: int = 32,
        hidden_dim: int = 64,
        mu_scale: float = 1.0,
        halt_threshold: float = 0.7,
        n_coupling_groups: int = 4,  # intra_p, intra_e, p→e, e→p
    ):
        super().__init__()
        self.planner_channels = int(planner_channels)
        self.executor_channels = int(executor_channels)
        self.n_coupling_groups = int(n_coupling_groups)
        self.mu_scale = float(mu_scale)
        self.halt_threshold = float(halt_threshold)

        # Complex organ state → real features (concat real & imag); per-position feat dim = 2C.
        self.pool_planner = AttentionPool(2 * planner_channels, query_dim, n_queries)
        self.pool_executor = AttentionPool(2 * executor_channels, query_dim, n_queries)

        if comm_dim is not None:
            self.pool_comm: AttentionPool | None = AttentionPool(int(comm_dim), query_dim, n_queries)
            n_pools = 3
        else:
            self.pool_comm = None
            n_pools = 2

        pooled_dim = n_pools * n_queries * query_dim

        # Shallow trunk — ONE MLP layer. (Cuscuton-parsimony: no deep internal computation.)
        self.trunk = nn.Sequential(
            nn.Linear(pooled_dim, hidden_dim),
            nn.GELU(),
        )

        # Joint output head: μ_p ‖ μ_e ‖ coupling_logits ‖ confidence_logit
        n_outputs = (
            self.planner_channels
            + self.executor_channels
            + self.n_coupling_groups
            + 1  # confidence
        )
        self.head = nn.Linear(hidden_dim, n_outputs)
        # Initialize the head small so the Mirror starts roughly neutral
        # (raw_μ ≈ 0 → tanh(raw_μ) ≈ 0; confidence_logit ≈ 0 → confidence ≈ 0.5).
        nn.init.normal_(self.head.weight, mean=0.0, std=0.01)
        nn.init.zeros_(self.head.bias)

    def forward(
        self,
        planner_z: torch.Tensor,
        executor_z: torch.Tensor,
        comm: torch.Tensor | None = None,
    ) -> dict:
        """Observe the system state, emit gating + confidence.

        planner_z:  [batch, seq, P_channels] complex
        executor_z: [batch, seq, E_channels] complex
        comm:       [batch, seq, comm_dim]   real or complex, optional

        Returns dict with:
          mu_planner:   [batch, P_channels] real  — confidence-modulated
          mu_executor:  [batch, E_channels] real  — confidence-modulated
          coupling:     dict[str, [batch]] real, in (0, 1) — group-level multipliers
          confidence:   [batch] real in (0, 1)
          halt:         [batch] bool — confidence > halt_threshold
        """
        # Complex → real features (concat real & imag along channel dim).
        p_feat = torch.cat([planner_z.real, planner_z.imag], dim=-1)
        e_feat = torch.cat([executor_z.real, executor_z.imag], dim=-1)

        p_pool = self.pool_planner(p_feat).flatten(start_dim=1)
        e_pool = self.pool_executor(e_feat).flatten(start_dim=1)
        pools = [p_pool, e_pool]

        if self.pool_comm is not None:
            if comm is None:
                raise ValueError("Mirror built with comm_dim but no comm passed to forward")
            if torch.is_complex(comm):
                c_feat = torch.cat([comm.real, comm.imag], dim=-1)
            else:
                c_feat = comm
            pools.append(self.pool_comm(c_feat).flatten(start_dim=1))

        summary = torch.cat(pools, dim=-1)        # [batch, pooled_dim]
        h = self.trunk(summary)                    # [batch, hidden]
        raw = self.head(h)                         # [batch, n_outputs]

        # Split outputs along the channel dim.
        offset = 0
        raw_mu_p = raw[:, offset : offset + self.planner_channels]
        offset += self.planner_channels
        raw_mu_e = raw[:, offset : offset + self.executor_channels]
        offset += self.executor_channels
        coupling_logits = raw[:, offset : offset + self.n_coupling_groups]
        offset += self.n_coupling_groups
        confidence_logit = raw[:, offset : offset + 1]  # [batch, 1]

        confidence = torch.sigmoid(confidence_logit)  # [batch, 1] in (0, 1)

        # Confidence-modulated gating: low conf → μ ≈ 0 (NEUTRAL); high conf → committed.
        # tanh keeps the raw signal bounded; mu_scale sets the maximum amplitude.
        mu_planner = self.mu_scale * confidence * torch.tanh(raw_mu_p)
        mu_executor = self.mu_scale * confidence * torch.tanh(raw_mu_e)

        # Coupling multipliers: nonneg, also confidence-modulated.
        # σ keeps each in (0, 1); confidence scales the maximum strength.
        coupling_mults = torch.sigmoid(coupling_logits) * confidence  # [batch, 4]

        conf_flat = confidence.squeeze(-1)  # [batch]
        return {
            "mu_planner": mu_planner,         # [batch, P]
            "mu_executor": mu_executor,        # [batch, E]
            "coupling": {
                "intra_planner":       coupling_mults[:, 0],
                "intra_executor":      coupling_mults[:, 1],
                "planner_to_executor": coupling_mults[:, 2],
                "executor_to_planner": coupling_mults[:, 3],
            },
            "confidence": conf_flat,                                   # [batch]
            "halt": (conf_flat > self.halt_threshold),                 # [batch] bool
        }

    def extra_repr(self) -> str:
        return (
            f"planner_channels={self.planner_channels}, "
            f"executor_channels={self.executor_channels}, "
            f"mu_scale={self.mu_scale}, halt_threshold={self.halt_threshold}"
        )
