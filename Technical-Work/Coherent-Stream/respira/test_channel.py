"""
Smoke test for Stuart-Landau channel layer.

Three criteria (PHASE1_BUILD_SPEC.md):
  1. μ > 0  →  stable limit cycle of amplitude √μ
  2. μ < 0  →  decay to zero
  3. Different ω  →  different rotation periods

Run from respira/:  python3 test_channel.py
"""
from __future__ import annotations

import math
import torch

from channel import StuartLandauChannelLayer


def _amplitude(z: torch.Tensor) -> torch.Tensor:
    return (z.real * z.real + z.imag * z.imag).sqrt()


def test_limit_cycle_amplitude(tol: float = 0.05) -> None:
    """μ > 0 should drive |z| → √μ."""
    torch.manual_seed(0)
    layer = StuartLandauChannelLayer(num_channels=16, omega_min=0.5, omega_max=2.0, dt=0.05)
    mu_val = 0.5
    expected_amp = math.sqrt(mu_val)

    z = layer.init_state(1, noise_scale=0.01)
    mu = torch.full_like(z.real, mu_val)
    for _ in range(2000):  # plenty of time to reach the limit cycle
        z = layer(z, mu)
    final_amp = _amplitude(z).mean().item()

    err = abs(final_amp - expected_amp) / expected_amp
    status = "PASS" if err < tol else "FAIL"
    print(f"  [TEST 1: μ > 0 → |z| ≈ √μ]  final={final_amp:.4f}  expected={expected_amp:.4f}  "
          f"rel_err={err:.4f}  {status}")
    assert err < tol, f"limit-cycle amplitude off: {final_amp} vs expected {expected_amp}"


def test_decay_to_zero(tol: float = 1e-3) -> None:
    """μ < 0 should drive |z| → 0."""
    torch.manual_seed(0)
    layer = StuartLandauChannelLayer(num_channels=16, omega_min=0.5, omega_max=2.0, dt=0.05)
    z = layer.init_state(1, noise_scale=0.5)  # start large; should still decay
    mu = torch.full_like(z.real, -0.5)
    for _ in range(2000):
        z = layer(z, mu)
    final_amp = _amplitude(z).mean().item()

    status = "PASS" if final_amp < tol else "FAIL"
    print(f"  [TEST 2: μ < 0 → |z| ≈ 0]   final={final_amp:.2e}  "
          f"(tol < {tol:.0e})  {status}")
    assert final_amp < tol, f"did not decay: |z|={final_amp}"


def test_omega_controls_period(tol_rel: float = 0.15) -> None:
    """Different ω should produce different phase velocities ≈ ω."""
    torch.manual_seed(0)
    N = 8
    layer = StuartLandauChannelLayer(
        num_channels=N, omega_init="log_spaced", omega_min=0.5, omega_max=4.0, dt=0.05,
        learnable_omega=False,  # fix ω so we can compare against the init values
    )
    z = layer.init_state(1, noise_scale=0.01)
    mu = torch.full_like(z.real, 0.5)
    # Settle into limit cycle first
    for _ in range(2000):
        z = layer(z, mu)
    # Measure phase velocity over a window of steps
    n_steps = 200
    phase_start = torch.atan2(z.imag, z.real)
    for _ in range(n_steps):
        z = layer(z, mu)
    phase_end = torch.atan2(z.imag, z.real)
    # Unwrap phase difference (avoid wrap-around mismatch in single step)
    raw_delta = (phase_end - phase_start)
    # The actual phase accumulated over n_steps with ω is ω · n_steps · dt
    # Account for wraps: expected_unwrapped = ω · n_steps · dt
    expected_unwrapped = layer.omega * n_steps * layer.dt
    # Bring raw_delta into the same range as expected by adding the right number of 2π's
    k = torch.round((expected_unwrapped - raw_delta.squeeze(0)) / (2 * math.pi))
    observed = raw_delta.squeeze(0) + 2 * math.pi * k
    observed_velocity = observed / (n_steps * layer.dt)
    expected_velocity = layer.omega.detach()

    rel_err = ((observed_velocity - expected_velocity).abs() / expected_velocity.abs()).max().item()
    status = "PASS" if rel_err < tol_rel else "FAIL"
    print(f"  [TEST 3: phase velocity ≈ ω]  max_rel_err={rel_err:.4f}  (tol < {tol_rel})  {status}")
    print(f"      ω values:      {expected_velocity.tolist()}")
    print(f"      observed vel:  {observed_velocity.tolist()}")
    assert rel_err < tol_rel, f"phase velocity off: {observed_velocity} vs {expected_velocity}"


def test_backprop_through_channel() -> None:
    """Sanity: gradients flow through the channel update (training viability)."""
    torch.manual_seed(0)
    layer = StuartLandauChannelLayer(num_channels=8, dt=0.05)
    z = layer.init_state(2, noise_scale=0.01)  # batch=2
    mu = torch.full_like(z.real, 0.5, requires_grad=True)
    for _ in range(10):
        z = layer(z, mu)
    loss = _amplitude(z).mean()
    loss.backward()
    grad_mu_norm = mu.grad.norm().item()
    omega_grad = layer.omega.grad
    omega_grad_norm = omega_grad.norm().item() if omega_grad is not None else 0.0
    status = "PASS" if (grad_mu_norm > 0 and omega_grad_norm > 0) else "FAIL"
    print(f"  [TEST 4: backprop]  grad‖μ‖={grad_mu_norm:.4e}  grad‖ω‖={omega_grad_norm:.4e}  {status}")
    assert grad_mu_norm > 0, "no gradient flowing to μ"
    assert omega_grad_norm > 0, "no gradient flowing to ω"


if __name__ == "__main__":
    print("Stuart-Landau channel smoke tests")
    print("=" * 50)
    test_limit_cycle_amplitude()
    test_decay_to_zero()
    test_omega_controls_period()
    test_backprop_through_channel()
    print("=" * 50)
    print("ALL PASS — channel.py is sound.")
