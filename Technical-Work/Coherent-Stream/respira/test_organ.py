"""
Smoke test for Organ.

Criteria:
  1. Forward returns correct shape, complex dtype, finite values.
  2. intra_strength=0 reduces exactly to bare channel dynamics (coupling truly off).
  3. Coupling is non-trivial at intra_strength>0 (something actually happens).
  4. intra_strength scales the coupling contribution LINEARLY (cuscuton-shaped
     scalar control behaves as designed — doubling intra doubles the coupling delta).
  5. Backprop flows through ALL params (ω, channel_mix, position_mix, μ, intra_strength).

Run from respira/:  python3 test_organ.py
"""
from __future__ import annotations

import torch

from organ import Organ


def test_forward_shape() -> None:
    torch.manual_seed(0)
    batch, seq, C = 2, 16, 8
    organ = Organ(num_channels=C, seq_len=seq, omega_min=0.5, omega_max=2.0, dt=0.05)
    z = organ.init_state(batch, noise_scale=0.01)
    mu = torch.full_like(z.real, 0.5)
    intra = torch.tensor(0.5)

    z_next = organ(z, mu, intra)

    ok = (
        z_next.shape == (batch, seq, C)
        and torch.is_complex(z_next)
        and torch.isfinite(z_next.real).all()
        and torch.isfinite(z_next.imag).all()
    )
    print(f"  [TEST 1: shape + dtype + finite]  shape={tuple(z_next.shape)} complex={torch.is_complex(z_next)}  "
          f"{'PASS' if ok else 'FAIL'}")
    assert ok


def test_zero_coupling_matches_bare_channel(tol: float = 1e-6) -> None:
    """intra_strength=0 should make the Organ behave identically to the bare channel."""
    torch.manual_seed(0)
    batch, seq, C = 2, 4, 4
    organ = Organ(num_channels=C, seq_len=seq, omega_min=0.5, omega_max=2.0, dt=0.05)
    z = organ.init_state(batch, noise_scale=0.01)
    mu = torch.full_like(z.real, 0.5)

    z_organ = organ(z, mu, intra_strength=torch.tensor(0.0))
    z_chan = organ.channel(z, mu, coupling=None)

    max_diff = (z_organ - z_chan).abs().max().item()
    ok = max_diff < tol
    print(f"  [TEST 2: intra=0 ≡ bare channel]  max|Δ|={max_diff:.2e}  (tol < {tol})  "
          f"{'PASS' if ok else 'FAIL'}")
    assert ok, f"organ@intra=0 differs from bare channel: {max_diff}"


def test_coupling_is_non_trivial(min_delta: float = 1e-3) -> None:
    """At intra>0, the result must differ from the no-coupling baseline."""
    torch.manual_seed(0)
    batch, seq, C = 2, 8, 8
    organ = Organ(num_channels=C, seq_len=seq, omega_min=0.5, omega_max=2.0, dt=0.05)
    z = organ.init_state(batch, noise_scale=0.5)  # bigger init so coupling actually matters
    mu = torch.full_like(z.real, 0.5)

    z_no_coupling = organ(z, mu, intra_strength=torch.tensor(0.0))
    z_with_coupling = organ(z, mu, intra_strength=torch.tensor(1.0))

    max_diff = (z_with_coupling - z_no_coupling).abs().max().item()
    ok = max_diff > min_delta
    print(f"  [TEST 3: coupling on ≠ off]  max|Δ|={max_diff:.4f}  (must exceed {min_delta})  "
          f"{'PASS' if ok else 'FAIL'}")
    assert ok, f"intra_strength had no effect on output: {max_diff}"


def test_intra_strength_scales_linearly(tol: float = 0.01) -> None:
    """intra_strength is a scalar multiplier of the coupling input — must be linear.

    Because: z_next = z + dt·(channel_dyn(z) + intra · coupling_op(z))
    so       z_next(intra) − z_next(0) = dt · intra · coupling_op(z)
    which means delta scales exactly linearly with intra.
    """
    torch.manual_seed(0)
    batch, seq, C = 2, 8, 8
    organ = Organ(num_channels=C, seq_len=seq, omega_min=0.5, omega_max=2.0, dt=0.05)
    z = organ.init_state(batch, noise_scale=0.5)
    mu = torch.full_like(z.real, 0.5)

    z_0 = organ(z, mu, intra_strength=torch.tensor(0.0))
    z_1 = organ(z, mu, intra_strength=torch.tensor(1.0))
    z_2 = organ(z, mu, intra_strength=torch.tensor(2.0))

    d1 = (z_1 - z_0).abs().mean().item()
    d2 = (z_2 - z_0).abs().mean().item()
    ratio = d2 / max(d1, 1e-12)
    err = abs(ratio - 2.0)
    ok = err < tol
    print(f"  [TEST 4: intra scales linearly]  d(2x)/d(1x)={ratio:.4f}  (expect 2.0, err={err:.2e})  "
          f"{'PASS' if ok else 'FAIL'}")
    assert ok, f"linearity broken: ratio={ratio}"


def test_backprop_all_params() -> None:
    torch.manual_seed(0)
    batch, seq, C = 1, 8, 4
    organ = Organ(num_channels=C, seq_len=seq, omega_min=0.5, omega_max=2.0, dt=0.05)
    z = organ.init_state(batch, noise_scale=0.01)
    mu = torch.full_like(z.real, 0.5, requires_grad=True)
    intra = torch.tensor(0.5, requires_grad=True)

    # A few cycles of BPTT to ensure gradients flow through the recurrence
    for _ in range(8):
        z = organ(z, mu, intra)
    loss = (z.real * z.real + z.imag * z.imag).mean()
    loss.backward()

    checks = {
        "μ":              (mu.grad is not None and mu.grad.norm().item() > 0),
        "intra_strength": (intra.grad is not None and abs(intra.grad.item()) > 0),
        "ω":              (organ.channel.omega.grad is not None and organ.channel.omega.grad.norm().item() > 0),
        "channel_mix.r":  (organ.channel_mix.real.weight.grad is not None and organ.channel_mix.real.weight.grad.norm().item() > 0),
        "channel_mix.i":  (organ.channel_mix.imag.weight.grad is not None and organ.channel_mix.imag.weight.grad.norm().item() > 0),
        "position_mix.r": (organ.position_mix.real.weight.grad is not None and organ.position_mix.real.weight.grad.norm().item() > 0),
        "position_mix.i": (organ.position_mix.imag.weight.grad is not None and organ.position_mix.imag.weight.grad.norm().item() > 0),
    }
    ok = all(checks.values())
    print(f"  [TEST 5: backprop through all params]  {'PASS' if ok else 'FAIL'}")
    for name, passed in checks.items():
        print(f"      {name:18s}: {'✓' if passed else '✗'}")
    assert ok, f"gradients missing: {checks}"


def report_params() -> None:
    p_organ = Organ(num_channels=32, seq_len=81, omega_min=0.05, omega_max=0.2, dt=0.1)
    e_organ = Organ(num_channels=64, seq_len=81, omega_min=0.5, omega_max=2.0, dt=0.1)
    p_count = sum(p.numel() for p in p_organ.parameters())
    e_count = sum(p.numel() for p in e_organ.parameters())
    print(f"\n  Planner-like Organ (32ch, seq=81): {p_count:,} params")
    print(f"  Executor-like Organ (64ch, seq=81): {e_count:,} params")
    print(f"  Combined (planner+executor):         {p_count + e_count:,} params")


if __name__ == "__main__":
    print("Organ smoke tests")
    print("=" * 50)
    test_forward_shape()
    test_zero_coupling_matches_bare_channel()
    test_coupling_is_non_trivial()
    test_intra_strength_scales_linearly()
    test_backprop_all_params()
    print("=" * 50)
    print("ALL PASS — organ.py is sound.")
    report_params()
