"""
Respira / respira.py — The full coherence-native cell.

Wires together:
  • planner Organ   — slow ω, holds context (bulk-like)
  • executor Organ  — fast ω, where the work happens (brane-like)
  • Mirror          — cuscuton-shaped meta-organ, observes both + the comm
  • cross-organ projections (ComplexLinear) — planner↔executor messages, Mirror-gated
  • input embedding (vocab → complex planner state) and output projection
    (executor state → vocab logits)

Forward = recurrent loop of up to `max_cycles`:
  1. Compute cross-organ messages: p_to_e_msg = W_pe(z_p); e_to_p_msg = W_ep(z_e).
  2. Mirror reads the current organ states, emits (μ_p, μ_e, coupling_mults, confidence, halt).
  3. Each organ steps one cycle with its mu, its intra coupling, and the cross-organ
     message scaled by the Mirror's cross-coupling multiplier.
  4. Per-batch ACT halt: a batch element stops being updated once its halt fires;
     loop ends when all batch elements have halted or `max_cycles` reached.

After the loop, the executor state is projected to vocab logits.

Optional `trajectory` log captures per-cycle structural summaries (confidence, μ
amplitudes, |z| amplitudes, coupling multipliers) for the inside-analysis protocol.

CLAWD-LOCAL / PRIVATE.
"""
from __future__ import annotations

import torch
import torch.nn as nn

from organ import Organ, ComplexLinear
from mirror import Mirror


class RespiraCell(nn.Module):
    """The full Respira cell: planner + executor + Mirror, recurrent with ACT halt."""

    def __init__(
        self,
        planner_channels: int = 32,
        executor_channels: int = 64,
        seq_len: int = 81,
        vocab_size: int = 11,
        max_cycles: int = 8,
        planner_omega: tuple[float, float] = (0.05, 0.2),
        executor_omega: tuple[float, float] = (0.5, 2.0),
        dt: float = 0.1,
        mu_scale: float = 1.0,
        halt_threshold: float = 0.7,
        mirror_n_queries: int = 4,
        mirror_query_dim: int = 32,
        mirror_hidden_dim: int = 64,
        # Phase-2v2 cuscuton-Mirror v2-c family — granular learnable-defaults flags.
        # v2-c   : learn_mu=True,  learn_coupling=True   (2 DOF — NCG-extended cuscuton shape)
        # v2-c1μ : learn_mu=True,  learn_coupling=False  (1 DOF — μ alone, bare-cuscuton shape)
        # v2-c1c : learn_mu=False, learn_coupling=True   (1 DOF — coupling alone)
        # no-mirror: both False                          (0 DOF — pure constants)
        # learnable_defaults kept as a back-compat shortcut for both-True.
        learnable_defaults: bool = False,
        learn_mu: bool | None = None,
        learn_coupling: bool | None = None,
        default_mu_init: float = 1.0,
        default_coupling_init: float = 0.5,
        # Phase-3 v3h Mirror-as-measurer flag.
        # "control"  : standard Mirror (emits mu + coupling + confidence + halt).
        # "measurer" : MirrorMeasurer (emits ONLY confidence + halt; channels use
        #              fixed defaults; Mirror has zero channel-modulation DOF).
        # Pre-registered at palace/south/respira-phase3-mirror-as-measurer-preregistration-2026-05-28.md
        mirror_kind: str = "control",
        measurer_halt_threshold: float = 0.5,
    ):
        super().__init__()
        self.planner_channels = int(planner_channels)
        self.executor_channels = int(executor_channels)
        self.seq_len = int(seq_len)
        self.vocab_size = int(vocab_size)
        self.max_cycles = int(max_cycles)

        # Organs
        self.planner = Organ(
            num_channels=planner_channels, seq_len=seq_len,
            omega_min=planner_omega[0], omega_max=planner_omega[1], dt=dt,
        )
        self.executor = Organ(
            num_channels=executor_channels, seq_len=seq_len,
            omega_min=executor_omega[0], omega_max=executor_omega[1], dt=dt,
        )

        # Mirror — observes both organs (no comm channel for Phase 1)
        self.mirror_kind = str(mirror_kind)
        if self.mirror_kind == "measurer":
            from mirror_measurer import MirrorMeasurer
            self.mirror = MirrorMeasurer(
                planner_channels=planner_channels,
                executor_channels=executor_channels,
                n_queries=mirror_n_queries,
                query_dim=mirror_query_dim,
                hidden_dim=mirror_hidden_dim,
                halt_threshold=measurer_halt_threshold,
            )
        elif self.mirror_kind == "control":
            self.mirror = Mirror(
                planner_channels=planner_channels,
                executor_channels=executor_channels,
                n_queries=mirror_n_queries,
                query_dim=mirror_query_dim,
                hidden_dim=mirror_hidden_dim,
                mu_scale=mu_scale,
                halt_threshold=halt_threshold,
            )
        else:
            raise ValueError(f"mirror_kind must be 'control' or 'measurer', got {self.mirror_kind!r}")

        # Cross-organ projections (per-position channel mapping; Mirror-gated downstream)
        self.p_to_e = ComplexLinear(planner_channels, executor_channels, bias=False)
        self.e_to_p = ComplexLinear(executor_channels, planner_channels, bias=False)

        # Input embedding: vocab → complex initial planner state
        # Two real embeddings (real, imag) keeps it dtype-portable.
        self.embed_real = nn.Embedding(vocab_size, planner_channels)
        self.embed_imag = nn.Embedding(vocab_size, planner_channels)
        # Small init so initial planner state has bounded amplitude
        nn.init.normal_(self.embed_real.weight, mean=0.0, std=0.1)
        nn.init.normal_(self.embed_imag.weight, mean=0.0, std=0.1)

        # Output projection: executor state (real+imag stacked) → vocab logits
        self.output_proj = nn.Linear(2 * executor_channels, vocab_size)

        # Phase-2v2 v2-c family — learnable scalar replacements for the constants in the
        # mirror_authority=0 path. Resolves the granular flags; `learnable_defaults`
        # kept as back-compat shortcut for both-True.
        if learn_mu is None and learn_coupling is None:
            learn_mu_resolved = bool(learnable_defaults)
            learn_coupling_resolved = bool(learnable_defaults)
        else:
            learn_mu_resolved = bool(learn_mu) if learn_mu is not None else False
            learn_coupling_resolved = bool(learn_coupling) if learn_coupling is not None else False
        self.learn_mu = learn_mu_resolved
        self.learn_coupling = learn_coupling_resolved
        # Keep back-compat attribute for any external callers.
        self.learnable_defaults = self.learn_mu and self.learn_coupling
        if self.learn_mu:
            self.default_mu_param = nn.Parameter(torch.tensor(float(default_mu_init)))
        if self.learn_coupling:
            self.default_coupling_param = nn.Parameter(torch.tensor(float(default_coupling_init)))

    def _where_complex(self, mask: torch.Tensor, a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
        """Complex-safe torch.where (some torch versions error on complex tensors)."""
        return torch.complex(
            torch.where(mask, a.real, b.real),
            torch.where(mask, a.imag, b.imag),
        )

    def forward(
        self,
        input_tokens: torch.Tensor,
        record_trajectory: bool = False,
        mirror_authority: float = 1.0,
        default_mu: float = 1.0,
        default_coupling: float = 0.5,
        halt_authority_threshold: float = 0.5,
        arch_variant: str = "default",  # Phase-2v2: "default" | "v2a_phase_locking" | Phase-3: "v3h_measurer"
        mirror_detach_inputs: bool = False,    # Phase-3 Stage 2: detach z_p/z_e at Mirror input (arms A, C)
        capture_per_cycle_logits: bool = False, # Phase-3 Stage 2: needed for TD supervisor (arms A, B)
    ) -> tuple[torch.Tensor, list | None, dict]:
        """Run the cell on a batch of token sequences.

        input_tokens: [batch, seq_len] long
        Returns:
            logits:     [batch, seq_len, vocab_size]
            trajectory: list of per-cycle dicts (if record_trajectory) else None
        """
        if input_tokens.dim() != 2 or input_tokens.shape[1] != self.seq_len:
            raise ValueError(
                f"input_tokens shape must be [batch, {self.seq_len}], got {tuple(input_tokens.shape)}"
            )
        batch = input_tokens.shape[0]
        device = input_tokens.device

        # Initial planner state from input embeddings; executor starts at small noise.
        z_p = torch.complex(self.embed_real(input_tokens), self.embed_imag(input_tokens))
        z_e = self.executor.init_state(batch, device=device, noise_scale=0.01)

        trajectory: list = [] if record_trajectory else None
        # `halted` flags batch elements that have already collapsed via Mirror halt.
        halted = torch.zeros(batch, dtype=torch.bool, device=device)
        # Track the cycle at which each batch halted (for inside-analysis); default = max.
        halt_cycle = torch.full((batch,), self.max_cycles, dtype=torch.long, device=device)
        # Track Mirror confidence per cycle (always — needed for the C2 calibration loss).
        # We snapshot the confidence the Mirror emits at each cycle BEFORE halt-masking,
        # so each batch element's halt-cycle confidence is its "committal" signal.
        per_cycle_confidence: list[torch.Tensor] = []
        # Phase-3 Stage 2: per-cycle logits (state AFTER each cycle update → output_proj).
        # Captured when capture_per_cycle_logits=True. Used by TD supervisor to compute
        # "would running another cycle have changed the answer?" target.
        per_cycle_logits: list[torch.Tensor] = [] if capture_per_cycle_logits else None

        for cycle in range(self.max_cycles):
            # 1) Cross-organ messages from current states (Mirror-gated below)
            p_to_e_msg = self.p_to_e(z_p)  # [batch, seq, E]
            e_to_p_msg = self.e_to_p(z_e)  # [batch, seq, P]

            # 2) Mirror reads + emits gating.
            # Phase-3 Stage 2: if mirror_detach_inputs, sever the gradient back-flow into
            # upstream channel parameters from the Mirror's supervisor loss. This isolates
            # the bug in Stage 1's v3h where attention-pool backward gradient flowed through
            # MultiheadAttention into channels (the "channel-leakage" fix).
            if mirror_detach_inputs:
                m = self.mirror(z_p.detach(), z_e.detach())
            else:
                m = self.mirror(z_p, z_e)

            # Phase-2v2 v2-a: phase-locking rule (zero DOF — pure deterministic constraint).
            # Computes mu values per-channel-per-position from inter-organ phase coherence;
            # skips Mirror outputs entirely (the Mirror is still computed for trajectory
            # logging consistency, but its outputs are not used in the dynamics).
            # Pre-registered spec §3a: BASE_MU=1.0, all-pairs mean of cos(phase_p − phase_e).
            BASE_MU_V2A = 1.0
            if arch_variant == "v2a_phase_locking":
                phase_p = z_p.angle()  # [B, S, P]
                phase_e = z_e.angle()  # [B, S, E]
                delta_pe = phase_p.unsqueeze(-1) - phase_e.unsqueeze(-2)  # [B, S, P, E]
                phase_coh_p = torch.cos(delta_pe).mean(-1)  # [B, S, P]
                phase_coh_e = torch.cos(-delta_pe).mean(-2)  # [B, S, E]
                mu_p = BASE_MU_V2A * phase_coh_p  # [B, S, P] — already has seq dim
                mu_e = BASE_MU_V2A * phase_coh_e  # [B, S, E]
                # Coupling: fixed default (no Mirror, no learnable scalar).
                intra_p = torch.tensor(default_coupling, device=device).view(1, 1, 1)
                intra_e = torch.tensor(default_coupling, device=device).view(1, 1, 1)
                p_to_e_str = torch.tensor(default_coupling, device=device).view(1, 1, 1)
                e_to_p_str = torch.tensor(default_coupling, device=device).view(1, 1, 1)
                effective_halt = torch.zeros_like(m["halt"])  # Halt disabled for v2-a.
                # Cast to complex for the cross-organ message multiplication.
                p_to_e_strC = p_to_e_str.to(p_to_e_msg.dtype)
                e_to_p_strC = e_to_p_str.to(e_to_p_msg.dtype)
                # Skip the mu/coupling-broadcasting block below — we've set them already.
                _v2a_branch_taken = True
            else:
                _v2a_branch_taken = False

            # Phase-3 v3h: Mirror-as-measurer. Channels use fixed defaults (like v2-a),
            # but the Mirror's halt decision IS honored (unlike v2-a). The Mirror has
            # zero channel-modulation outputs (no mu, no coupling) — pre-registered.
            if arch_variant == "v3h_measurer":
                P = self.planner_channels
                E = self.executor_channels
                mu_p = torch.full(
                    (batch, self.seq_len, P), float(default_mu),
                    device=device, dtype=z_p.real.dtype,
                )
                mu_e = torch.full(
                    (batch, self.seq_len, E), float(default_mu),
                    device=device, dtype=z_e.real.dtype,
                )
                intra_p = torch.tensor(default_coupling, device=device).view(1, 1, 1)
                intra_e = torch.tensor(default_coupling, device=device).view(1, 1, 1)
                p_to_e_str = torch.tensor(default_coupling, device=device).view(1, 1, 1)
                e_to_p_str = torch.tensor(default_coupling, device=device).view(1, 1, 1)
                effective_halt = m["halt"]  # HONOR the Measurer's halt decision
                p_to_e_strC = p_to_e_str.to(p_to_e_msg.dtype)
                e_to_p_strC = e_to_p_str.to(e_to_p_msg.dtype)
                _v3h_branch_taken = True
            else:
                _v3h_branch_taken = False

            # Curriculum: interpolate Mirror outputs with defaults.
            # mirror_authority=0 → Mirror sits idle (no influence, no gradient through it)
            # mirror_authority=1 → Mirror is fully in charge (current behavior)
            # In-between: linear blend.  Halt is only respected when authority is high.
            # v2-c: default constants are LEARNABLE scalars when self.learnable_defaults.
            if _v2a_branch_taken or _v3h_branch_taken:
                pass  # already set everything in v2-a or v3h branch above
            elif mirror_authority < 1.0:
                a = mirror_authority
                # v2-c family — gradient-flowing scalars replace each constant individually:
                d_mu = self.default_mu_param if self.learn_mu else default_mu
                d_co = self.default_coupling_param if self.learn_coupling else default_coupling
                mu_p_e = a * m["mu_planner"]  + (1 - a) * (torch.ones_like(m["mu_planner"]) * d_mu)
                mu_e_e = a * m["mu_executor"] + (1 - a) * (torch.ones_like(m["mu_executor"]) * d_mu)
                intra_p_v = a * m["coupling"]["intra_planner"]       + (1 - a) * d_co
                intra_e_v = a * m["coupling"]["intra_executor"]      + (1 - a) * d_co
                p_to_e_v  = a * m["coupling"]["planner_to_executor"] + (1 - a) * d_co
                e_to_p_v  = a * m["coupling"]["executor_to_planner"] + (1 - a) * d_co
                effective_halt = m["halt"] if mirror_authority > halt_authority_threshold else torch.zeros_like(m["halt"])
            else:
                mu_p_e = m["mu_planner"]
                mu_e_e = m["mu_executor"]
                intra_p_v = m["coupling"]["intra_planner"]
                intra_e_v = m["coupling"]["intra_executor"]
                p_to_e_v  = m["coupling"]["planner_to_executor"]
                e_to_p_v  = m["coupling"]["executor_to_planner"]
                effective_halt = m["halt"]

            if not (_v2a_branch_taken or _v3h_branch_taken):
                # Broadcast per-channel μ over the seq dim
                mu_p = mu_p_e.unsqueeze(1).expand(-1, self.seq_len, -1)
                mu_e = mu_e_e.unsqueeze(1).expand(-1, self.seq_len, -1)

                # Per-batch coupling multipliers reshaped for broadcasting [batch, 1, 1]
                intra_p = intra_p_v.view(-1, 1, 1)
                intra_e = intra_e_v.view(-1, 1, 1)
                p_to_e_str = p_to_e_v.view(-1, 1, 1)
                e_to_p_str = e_to_p_v.view(-1, 1, 1)
                # cast to complex for multiplication with complex messages
                p_to_e_strC = p_to_e_str.to(p_to_e_msg.dtype)
                e_to_p_strC = e_to_p_str.to(e_to_p_msg.dtype)

            # 3) Step each organ (cross-organ message arrives as external_coupling)
            z_p_next = self.planner(
                z_p, mu_p, intra_strength=intra_p,
                external_coupling=e_to_p_strC * e_to_p_msg,
            )
            z_e_next = self.executor(
                z_e, mu_e, intra_strength=intra_e,
                external_coupling=p_to_e_strC * p_to_e_msg,
            )

            # 4) Per-batch ACT halt — already-halted batch elements keep their state.
            keep_old = halted.view(-1, 1, 1)  # [batch, 1, 1] bool
            z_p = self._where_complex(keep_old, z_p, z_p_next)
            z_e = self._where_complex(keep_old, z_e, z_e_next)

            # Record cycle of first halt (use effective_halt — only fires when Mirror has authority)
            newly_halting = effective_halt & (~halted)
            halt_cycle = torch.where(newly_halting, torch.full_like(halt_cycle, cycle + 1), halt_cycle)
            halted = halted | effective_halt

            # Snapshot this cycle's Mirror confidence (BEFORE next iteration) — keeps the
            # gradient path live for the C2 calibration loss in train.py.
            per_cycle_confidence.append(m["confidence"])  # [batch]

            # Phase-3 Stage 2: snapshot per-cycle logits if requested (TD supervisor).
            # Computes from state AFTER this cycle's update — gives "logits-if-we-halt-here".
            # Gradient preserved so TD-supervisor backprop reaches Mirror confidence head.
            if per_cycle_logits is not None:
                e_feat_cycle = torch.cat([z_e.real, z_e.imag], dim=-1)
                per_cycle_logits.append(self.output_proj(e_feat_cycle))

            if trajectory is not None:
                traj_entry = {
                    "cycle": cycle,
                    "confidence": m["confidence"].detach(),
                    "halt": m["halt"].detach(),
                    "halted_so_far": halted.detach().clone(),
                    "z_p_amplitude_mean": z_p.detach().abs().mean(dim=(1, 2)),
                    "z_e_amplitude_mean": z_e.detach().abs().mean(dim=(1, 2)),
                }
                # Mirror-as-measurer emits no mu/coupling — guard those keys.
                if m.get("mu_planner") is not None:
                    traj_entry["mu_planner_mean_abs"] = m["mu_planner"].detach().abs().mean(-1)
                    traj_entry["mu_executor_mean_abs"] = m["mu_executor"].detach().abs().mean(-1)
                if m.get("coupling") is not None:
                    traj_entry["coupling"] = {k: v.detach() for k, v in m["coupling"].items()}
                trajectory.append(traj_entry)

            if halted.all():
                break

        # Output projection from final executor state
        e_feat = torch.cat([z_e.real, z_e.imag], dim=-1)  # [batch, seq, 2E]
        logits = self.output_proj(e_feat)  # [batch, seq, vocab]

        # Phase-2v2 v2-b: coherence-energy term computed from FINAL z_p, z_e (committed state).
        # Spec from pre-reg §3b:
        #   coherence_energy = -mean_{i,j}( |z_p_i| · |z_e_j| · cos(phase(z_p_i) − phase(z_e_j)) )
        #   averaged over batch, seq, all i ∈ planner channels, all j ∈ executor channels.
        # Train.py adds λ_coh · coherence_energy to total_loss when this aux key is present.
        # Computed unconditionally (cheap) — train.py decides whether to use it.
        abs_p = (z_p.real * z_p.real + z_p.imag * z_p.imag).sqrt()  # [B, S, P]
        abs_e = (z_e.real * z_e.real + z_e.imag * z_e.imag).sqrt()  # [B, S, E]
        phase_p_final = z_p.angle()  # [B, S, P]
        phase_e_final = z_e.angle()  # [B, S, E]
        delta = phase_p_final.unsqueeze(-1) - phase_e_final.unsqueeze(-2)  # [B, S, P, E]
        cos_delta = torch.cos(delta)  # [B, S, P, E]
        product = abs_p.unsqueeze(-1) * abs_e.unsqueeze(-2) * cos_delta  # [B, S, P, E]
        coherence_energy = -product.mean()  # scalar

        # Build aux dict — used by train.py for the C2 calibration loss (A130 fix).
        # confidence_at_halt: each batch element's confidence at its halt cycle, with
        # GRADIENT preserved (so calibration loss flows back to the Mirror's head).
        conf_stack = torch.stack(per_cycle_confidence, dim=0)  # [cycles_run, batch]
        cycles_run = conf_stack.shape[0]
        hc_idx = (halt_cycle - 1).clamp(min=0, max=cycles_run - 1)  # [batch]
        confidence_at_halt = conf_stack.gather(0, hc_idx.unsqueeze(0)).squeeze(0)  # [batch]
        aux = {
            "confidence_at_halt": confidence_at_halt,
            "halt_cycle": halt_cycle,
            "per_cycle_confidence": conf_stack,  # [cycles_run, batch]
            "coherence_energy": coherence_energy,  # scalar (v2-b uses this in train loss)
        }
        # Phase-3 Stage 2: if per-cycle logits captured, stack and expose for TD supervisor.
        if per_cycle_logits is not None:
            # [cycles_run, batch, seq, vocab] — gradient preserved on Mirror's halt-cycle slice.
            aux["per_cycle_logits"] = torch.stack(per_cycle_logits, dim=0)

        return logits, trajectory, aux

    def parameter_summary(self) -> dict:
        groups = {
            "planner": sum(p.numel() for p in self.planner.parameters()),
            "executor": sum(p.numel() for p in self.executor.parameters()),
            "mirror": sum(p.numel() for p in self.mirror.parameters()),
            "p_to_e": sum(p.numel() for p in self.p_to_e.parameters()),
            "e_to_p": sum(p.numel() for p in self.e_to_p.parameters()),
            "embed": sum(p.numel() for p in self.embed_real.parameters())
                   + sum(p.numel() for p in self.embed_imag.parameters()),
            "output_proj": sum(p.numel() for p in self.output_proj.parameters()),
        }
        groups["total"] = sum(groups.values())
        return groups

    def extra_repr(self) -> str:
        return (
            f"P={self.planner_channels}, E={self.executor_channels}, "
            f"seq_len={self.seq_len}, vocab={self.vocab_size}, max_cycles={self.max_cycles}"
        )
