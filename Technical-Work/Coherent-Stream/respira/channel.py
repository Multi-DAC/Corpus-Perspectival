"""
Respira / channel.py — Stuart-Landau channel layer.

Each channel is a complex-valued unit z with Hopf-bifurcation dynamics:

    ż = (μ + iω) z − |z|² z + coupling

  • μ (real)     — bifurcation parameter. μ > 0: stable limit cycle, amplitude √μ
                    (channel BUILT / oscillating). μ < 0: rest at zero (DISSOLVED).
                    Mirror-modulated per cycle.
  • ω (real)     — natural frequency. Varied across channels for multi-scale rhythms.
                    Learned by default; planner gets slow ω, executor fast ω.
  • |z|² z       — cubic self-limiting term. Gives stable amplitude under perturbation.
  • coupling     — external input (from intra-organ + cross-organ coupling ops).

Discretization: explicit Euler step with small dt (default 0.1).

This is the smallest, most isolated primitive of Respira. See PHASE1_BUILD_SPEC.md.

CLAWD-LOCAL / PRIVATE.
"""
from __future__ import annotations

import math
import torch
import torch.nn as nn


class StuartLandauChannelLayer(nn.Module):
    """A bank of `num_channels` Stuart-Landau oscillators evolving in parallel.

    State convention: any leading-dim tensor of shape [..., num_channels] (complex dtype).
    A typical usage shape is [batch, seq_len, num_channels].
    """

    def __init__(
        self,
        num_channels: int,
        omega_init: str = "log_spaced",
        omega_min: float = 0.1,
        omega_max: float = 1.0,
        dt: float = 0.1,
        learnable_omega: bool = True,
    ):
        super().__init__()
        self.num_channels = int(num_channels)
        self.dt = float(dt)

        if omega_init == "log_spaced":
            log_min, log_max = math.log10(omega_min), math.log10(omega_max)
            omegas = torch.logspace(log_min, log_max, self.num_channels)
        elif omega_init == "uniform":
            omegas = torch.linspace(omega_min, omega_max, self.num_channels)
        else:
            raise ValueError(f"unknown omega_init: {omega_init!r}")

        if learnable_omega:
            self.omega = nn.Parameter(omegas.clone())
        else:
            self.register_buffer("omega", omegas.clone())

    def forward(
        self,
        z: torch.Tensor,
        mu: torch.Tensor,
        coupling: torch.Tensor | None = None,
    ) -> torch.Tensor:
        """One explicit-Euler step.

        z:        [..., num_channels] complex
        mu:       [..., num_channels] real  (broadcast-compatible with z's leading dims)
        coupling: [..., num_channels] complex, optional
        """
        if not torch.is_complex(z):
            raise TypeError(f"z must be complex, got {z.dtype}")
        if mu.is_complex():
            raise TypeError("mu must be real, not complex")

        # |z|² as a real tensor (same shape as z's real/imag).
        abs_z_sq = z.real * z.real + z.imag * z.imag

        # Broadcast omega to mu's shape (matches z's leading dims through mu).
        omega = self.omega.to(mu.dtype).expand_as(mu)

        # (μ + iω) z = (μ z.real − ω z.imag) + i (μ z.imag + ω z.real)
        lin_real = mu * z.real - omega * z.imag
        lin_imag = mu * z.imag + omega * z.real

        # Cubic self-limiting: |z|² · z
        cubic_real = abs_z_sq * z.real
        cubic_imag = abs_z_sq * z.imag

        dz_real = lin_real - cubic_real
        dz_imag = lin_imag - cubic_imag

        if coupling is not None:
            if not torch.is_complex(coupling):
                raise TypeError(f"coupling must be complex, got {coupling.dtype}")
            dz_real = dz_real + coupling.real
            dz_imag = dz_imag + coupling.imag

        z_next = torch.complex(z.real + self.dt * dz_real, z.imag + self.dt * dz_imag)
        return z_next

    def init_state(
        self,
        *shape: int,
        device: torch.device | str | None = None,
        dtype: torch.dtype = torch.complex64,
        noise_scale: float = 0.01,
        generator: torch.Generator | None = None,
    ) -> torch.Tensor:
        """Initialize channel state as small random complex perturbations.

        Why nonzero: μ < 0 has stable equilibrium at z=0 (exact);
        small noise lets dynamics amplify if μ flips positive (limit cycle catches on).
        Pass a `generator` for reproducible runs.
        """
        if not shape:
            raise ValueError("must specify at least one leading dim (e.g. batch)")
        full_shape = (*shape, self.num_channels)
        re = torch.randn(*full_shape, device=device, generator=generator)
        im = torch.randn(*full_shape, device=device, generator=generator)
        z = torch.complex(re, im).to(dtype) * noise_scale
        return z

    def extra_repr(self) -> str:
        return (
            f"num_channels={self.num_channels}, dt={self.dt}, "
            f"omega_range=({self.omega.min().item():.3g}, {self.omega.max().item():.3g})"
        )
