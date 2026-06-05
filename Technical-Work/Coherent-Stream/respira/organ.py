"""
Respira / organ.py — A sequence of channel states + intra-organ coupling.

An Organ wraps:
  • a Stuart-Landau channel layer (per-channel, per-position dynamics)
  • an intra-organ coupling op:
      − within-position channel mixing      (learnable complex C×C)
      − across-position position mixing      (learnable complex L×L)
  • the Mirror's intra_strength scalar multiplies the combined coupling output
    (cuscuton-parsimonious: ONE Mirror-output scalar per organ group, NOT per-edge)

Forward = one cycle:
    coupling = intra_strength · (channel_mix(z) + position_mix(z)) [+ external_coupling]
    z_next   = channel_step(z, μ, coupling)

State shape: [batch, seq_len, num_channels] complex.

Phase-1 uses a fixed L×L position-mixing matrix (sudoku has fixed seq_len=81).
Variable-length / LLM-scale will swap position_mix for attention-style mixing; the
rest of the architecture is unchanged. This is a deliberate Phase-1 simplification.

CLAWD-LOCAL / PRIVATE.
"""
from __future__ import annotations

import torch
import torch.nn as nn

from channel import StuartLandauChannelLayer


class ComplexLinear(nn.Module):
    """A complex-valued linear layer: y = W z, with W = W_r + i W_i.

    Uses two real nn.Linear layers under the hood (W_r, W_i), which keeps it
    portable across PyTorch versions and trivially backprop-friendly.

        W z = (W_r + i W_i)(z_r + i z_i)
            = (W_r z_r − W_i z_i) + i (W_r z_i + W_i z_r)
    """

    def __init__(self, in_features: int, out_features: int, bias: bool = False):
        super().__init__()
        self.real = nn.Linear(in_features, out_features, bias=bias)
        self.imag = nn.Linear(in_features, out_features, bias=bias)
        # Small init: avoid the coupling op blowing up dynamics before training shapes it.
        nn.init.normal_(self.real.weight, mean=0.0, std=0.1 / in_features ** 0.5)
        nn.init.normal_(self.imag.weight, mean=0.0, std=0.1 / in_features ** 0.5)

    def forward(self, z: torch.Tensor) -> torch.Tensor:
        if not torch.is_complex(z):
            raise TypeError(f"ComplexLinear expects complex input, got {z.dtype}")
        zr, zi = z.real, z.imag
        out_r = self.real(zr) - self.imag(zi)
        out_i = self.real(zi) + self.imag(zr)
        return torch.complex(out_r, out_i)


class Organ(nn.Module):
    """A sequence of Stuart-Landau channel states + intra-organ coupling op."""

    def __init__(
        self,
        num_channels: int,
        seq_len: int,
        omega_init: str = "log_spaced",
        omega_min: float = 0.1,
        omega_max: float = 1.0,
        dt: float = 0.1,
        learnable_omega: bool = True,
    ):
        super().__init__()
        self.num_channels = int(num_channels)
        self.seq_len = int(seq_len)

        self.channel = StuartLandauChannelLayer(
            num_channels=num_channels,
            omega_init=omega_init,
            omega_min=omega_min,
            omega_max=omega_max,
            dt=dt,
            learnable_omega=learnable_omega,
        )

        # Within-position channel mixing: C → C
        self.channel_mix = ComplexLinear(num_channels, num_channels, bias=False)
        # Across-position position mixing: L → L  (Phase-1 fixed seq_len)
        self.position_mix = ComplexLinear(seq_len, seq_len, bias=False)

    def forward(
        self,
        z: torch.Tensor,
        mu: torch.Tensor,
        intra_strength: torch.Tensor,
        external_coupling: torch.Tensor | None = None,
    ) -> torch.Tensor:
        """One cycle: compute intra-organ coupling, scale, then channel step.

        z:                 [batch, seq_len, num_channels] complex
        mu:                [batch, seq_len, num_channels] real (Mirror-modulated)
        intra_strength:    scalar tensor — Mirror's group-level coupling multiplier
        external_coupling: [batch, seq_len, num_channels] complex, optional
                           (e.g., cross-organ contribution coming from respira.py)
        """
        if z.shape[-2] != self.seq_len:
            raise ValueError(
                f"Organ was built with seq_len={self.seq_len}, got z.seq_len={z.shape[-2]}"
            )

        # Channel mixing (within each position): applies on the channel dim
        coupling_c = self.channel_mix(z)  # [batch, seq, channels]

        # Position mixing (across positions for each channel): apply on the seq dim
        z_t = z.transpose(-1, -2)  # [batch, channels, seq]
        coupling_p_t = self.position_mix(z_t)  # [batch, channels, seq]
        coupling_p = coupling_p_t.transpose(-1, -2)  # [batch, seq, channels]

        coupling = intra_strength * (coupling_c + coupling_p)

        if external_coupling is not None:
            if not torch.is_complex(external_coupling):
                raise TypeError("external_coupling must be complex")
            coupling = coupling + external_coupling

        return self.channel(z, mu, coupling)

    def init_state(
        self,
        batch: int,
        device: torch.device | str | None = None,
        dtype: torch.dtype = torch.complex64,
        noise_scale: float = 0.01,
        generator: torch.Generator | None = None,
    ) -> torch.Tensor:
        return self.channel.init_state(
            batch,
            self.seq_len,
            device=device,
            dtype=dtype,
            noise_scale=noise_scale,
            generator=generator,
        )

    def extra_repr(self) -> str:
        return f"num_channels={self.num_channels}, seq_len={self.seq_len}"
