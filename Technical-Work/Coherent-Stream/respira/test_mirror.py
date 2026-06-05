"""
Smoke test for Mirror.

Criteria:
  1. Forward returns dict with all expected keys + correct shapes/dtypes.
  2. Confidence is in (0, 1); halt is bool.
  3. Confidence MODULATES gating: |μ| ≤ mu_scale · confidence (the design property —
     the patent's three modes fall out of calibrated uncertainty, NOT a hard threshold).
  4. Coupling multipliers are in (0, confidence) — nonneg + confidence-bounded.
  5. Backprop flows through ALL params.
  6. Parameter budget reported (cuscuton-parsimony at scale).
  7. Works with and without the comm pool.

Run from respira/:  python3 test_mirror.py
"""
from __future__ import annotations

import torch

from mirror import Mirror


def _make_inputs(batch=2, seq=16, P=8, E=16, dtype=torch.complex64):
    torch.manual_seed(0)
    pz = (torch.randn(batch, seq, P) + 1j * torch.randn(batch, seq, P)).to(dtype) * 0.3
    ez = (torch.randn(batch, seq, E) + 1j * torch.randn(batch, seq, E)).to(dtype) * 0.3
    return pz, ez


def test_forward_shapes() -> None:
    torch.manual_seed(0)
    mirror = Mirror(planner_channels=8, executor_channels=16)
    pz, ez = _make_inputs(batch=2, seq=16, P=8, E=16)
    out = mirror(pz, ez)

    checks = {
        "mu_planner shape": out["mu_planner"].shape == (2, 8),
        "mu_executor shape": out["mu_executor"].shape == (2, 16),
        "confidence shape": out["confidence"].shape == (2,),
        "halt shape": out["halt"].shape == (2,) and out["halt"].dtype == torch.bool,
        "coupling keys": set(out["coupling"].keys()) == {
            "intra_planner", "intra_executor", "planner_to_executor", "executor_to_planner"
        },
        "coupling shapes": all(v.shape == (2,) for v in out["coupling"].values()),
        "mu_planner is real": not torch.is_complex(out["mu_planner"]),
        "mu_executor is real": not torch.is_complex(out["mu_executor"]),
    }
    ok = all(checks.values())
    print(f"  [TEST 1: forward shapes/dtypes]  {'PASS' if ok else 'FAIL'}")
    for k, v in checks.items():
        if not v:
            print(f"      ✗ {k}")
    assert ok


def test_confidence_in_unit_interval() -> None:
    torch.manual_seed(0)
    mirror = Mirror(planner_channels=8, executor_channels=16)
    pz, ez = _make_inputs()
    out = mirror(pz, ez)
    c = out["confidence"]
    ok = bool(((c > 0) & (c < 1)).all().item())
    print(f"  [TEST 2: confidence ∈ (0,1)]  min={c.min().item():.4f} max={c.max().item():.4f}  "
          f"{'PASS' if ok else 'FAIL'}")
    assert ok


def test_confidence_modulates_mu(tol: float = 1e-5) -> None:
    """The design contract: |μ| ≤ mu_scale · confidence, exactly.

    This is what makes build/dissolve/neutral emerge from calibrated uncertainty
    rather than from a hyperparameter. If a Mirror is uncertain (conf small),
    its μ amplitude is small (channels stay near rest = NEUTRAL).
    """
    torch.manual_seed(0)
    mu_scale = 1.0
    mirror = Mirror(planner_channels=8, executor_channels=16, mu_scale=mu_scale)
    pz, ez = _make_inputs()
    out = mirror(pz, ez)

    # |μ| ≤ mu_scale · conf, per-row.
    bound_p = mu_scale * out["confidence"].unsqueeze(-1)  # [batch, 1]
    bound_e = mu_scale * out["confidence"].unsqueeze(-1)
    violations_p = (out["mu_planner"].abs() > bound_p + tol).any().item()
    violations_e = (out["mu_executor"].abs() > bound_e + tol).any().item()

    # And a numerical headline: max |μ| / (mu_scale · conf) ≤ 1
    headroom_p = (out["mu_planner"].abs() / (bound_p + 1e-12)).max().item()
    headroom_e = (out["mu_executor"].abs() / (bound_e + 1e-12)).max().item()
    ok = (not violations_p) and (not violations_e)
    print(f"  [TEST 3: |μ| ≤ mu_scale·confidence]  "
          f"max(|μ_p|/(s·c))={headroom_p:.4f}  max(|μ_e|/(s·c))={headroom_e:.4f}  "
          f"{'PASS' if ok else 'FAIL'}")
    assert ok


def test_coupling_bounded_by_confidence(tol: float = 1e-5) -> None:
    """Coupling mults are σ(·)·confidence ∈ [0, confidence], bounded above by confidence."""
    torch.manual_seed(0)
    mirror = Mirror(planner_channels=8, executor_channels=16)
    pz, ez = _make_inputs()
    out = mirror(pz, ez)
    conf = out["confidence"]
    violations = []
    for name, val in out["coupling"].items():
        if (val < -tol).any() or (val > conf + tol).any():
            violations.append(name)
    ok = not violations
    print(f"  [TEST 4: coupling ∈ [0, confidence]]  violations={violations}  "
          f"{'PASS' if ok else 'FAIL'}")
    assert ok


def test_backprop_all_params() -> None:
    torch.manual_seed(0)
    mirror = Mirror(planner_channels=8, executor_channels=16)
    pz, ez = _make_inputs()
    out = mirror(pz, ez)
    # Build a scalar loss that depends on every output channel.
    loss = (
        out["mu_planner"].pow(2).mean()
        + out["mu_executor"].pow(2).mean()
        + out["confidence"].mean()
        + sum(v.mean() for v in out["coupling"].values())
    )
    loss.backward()
    missing = []
    for name, p in mirror.named_parameters():
        if p.grad is None or p.grad.norm().item() == 0:
            missing.append(name)
    ok = not missing
    print(f"  [TEST 5: backprop all params]  missing={missing}  {'PASS' if ok else 'FAIL'}")
    assert ok


def test_with_comm() -> None:
    """Optional comm pool: build with comm_dim and pass a comm tensor."""
    torch.manual_seed(0)
    comm_dim = 8
    mirror = Mirror(planner_channels=8, executor_channels=16, comm_dim=comm_dim)
    pz, ez = _make_inputs()
    comm = torch.randn(2, 16, comm_dim)
    out = mirror(pz, ez, comm=comm)
    ok = (
        out["mu_planner"].shape == (2, 8)
        and out["mu_executor"].shape == (2, 16)
        and mirror.pool_comm is not None
    )
    print(f"  [TEST 6: with comm pool]  {'PASS' if ok else 'FAIL'}")
    assert ok


def report_params() -> None:
    # Phase-1 starting sizes
    m_small = Mirror(planner_channels=32, executor_channels=64)
    # Production-scale toy
    m_big = Mirror(planner_channels=256, executor_channels=512)
    n_small = sum(p.numel() for p in m_small.parameters())
    n_big = sum(p.numel() for p in m_big.parameters())
    # Compare to planner+executor scale (organ.py reported 37K combined for Phase-1).
    print(f"\n  Mirror Phase-1 size (32 + 64): {n_small:,} params")
    print(f"  Mirror prod-toy size (256 + 512): {n_big:,} params")
    print("  Note: cuscuton-parsimony ratio improves with channel count — at toy scale")
    print("  the Mirror is non-trivial in relative terms; at production scale it shrinks.")


if __name__ == "__main__":
    print("Mirror smoke tests")
    print("=" * 50)
    test_forward_shapes()
    test_confidence_in_unit_interval()
    test_confidence_modulates_mu()
    test_coupling_bounded_by_confidence()
    test_backprop_all_params()
    test_with_comm()
    print("=" * 50)
    print("ALL PASS — mirror.py is sound.")
    report_params()
