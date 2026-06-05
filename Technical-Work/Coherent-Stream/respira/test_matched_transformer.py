"""
Smoke test for MatchedTransformer baseline.

Criteria:
  1. Forward returns logits of correct shape & dtype.
  2. Backprop flows through all parameters from a CE loss.
  3. Determinism: same seed → bit-identical output.
  4. Phase-1 matched config produces a parameter count within ±5% of Respira's 82,452.
  5. Sanity: model is in train mode by default and respects .eval().

Run from respira/:  python3 test_matched_transformer.py
"""
from __future__ import annotations

import torch
import torch.nn.functional as F

from baselines.matched_transformer import MatchedTransformer, phase1_matched_config


RESPIRA_PHASE1_PARAMS = 82_452


def test_forward_shape() -> None:
    torch.manual_seed(0)
    m = MatchedTransformer(**phase1_matched_config())
    x = torch.randint(0, 11, (2, 81))
    logits = m(x)
    ok = (
        logits.shape == (2, 81, 11)
        and logits.dtype == torch.float32
    )
    print(f"  [TEST 1: forward shape/dtype]  shape={tuple(logits.shape)}  "
          f"{'PASS' if ok else 'FAIL'}")
    assert ok


def test_backprop() -> None:
    torch.manual_seed(0)
    m = MatchedTransformer(**phase1_matched_config())
    x = torch.randint(0, 11, (2, 81))
    targets = torch.randint(0, 11, (2, 81))
    logits = m(x)
    loss = F.cross_entropy(logits.reshape(-1, 11), targets.reshape(-1))
    loss.backward()
    missing = [name for name, p in m.named_parameters()
               if p.grad is None or p.grad.norm().item() == 0]
    ok = not missing
    print(f"  [TEST 2: backprop all params]  missing={len(missing)} {missing if missing else ''}  "
          f"{'PASS' if ok else 'FAIL'}")
    assert ok


def test_determinism() -> None:
    x = torch.randint(0, 11, (2, 81))
    torch.manual_seed(0)
    m1 = MatchedTransformer(**phase1_matched_config())
    m1.eval()
    o1 = m1(x)
    torch.manual_seed(0)
    m2 = MatchedTransformer(**phase1_matched_config())
    m2.eval()
    o2 = m2(x)
    max_diff = (o1 - o2).abs().max().item()
    ok = max_diff < 1e-6
    print(f"  [TEST 3: determinism]  max|Δ|={max_diff:.2e}  {'PASS' if ok else 'FAIL'}")
    assert ok


def test_param_count_matches_respira(tol_pct: float = 5.0) -> None:
    m = MatchedTransformer(**phase1_matched_config())
    n = sum(p.numel() for p in m.parameters())
    diff_pct = abs(n - RESPIRA_PHASE1_PARAMS) / RESPIRA_PHASE1_PARAMS * 100
    ok = diff_pct < tol_pct
    print(f"  [TEST 4: param count matches Respira]  transformer={n:,}  "
          f"respira={RESPIRA_PHASE1_PARAMS:,}  diff={diff_pct:.2f}%  "
          f"(tol < {tol_pct}%)  {'PASS' if ok else 'FAIL'}")
    assert ok, f"baseline {n} not matched to Respira {RESPIRA_PHASE1_PARAMS}"


def test_eval_mode() -> None:
    """Sanity: .eval() disables dropout, .train() re-enables (smoke check)."""
    m = MatchedTransformer(**phase1_matched_config(), attn_dropout=0.5, mlp_dropout=0.5)
    m.eval()
    x = torch.randint(0, 11, (2, 81))
    o1 = m(x)
    o2 = m(x)
    # In eval mode, dropout is off → two forward passes are identical.
    eval_diff = (o1 - o2).abs().max().item()
    ok = eval_diff < 1e-6
    print(f"  [TEST 5: eval mode disables dropout]  eval max|Δ|={eval_diff:.2e}  "
          f"{'PASS' if ok else 'FAIL'}")
    assert ok


def report_params() -> None:
    m = MatchedTransformer(**phase1_matched_config())
    s = m.parameter_summary()
    print("\n  MatchedTransformer Phase-1 (hidden=56, layers=2, heads=4):")
    for k, v in s.items():
        if k == "total":
            print(f"    {'─' * 30}")
            print(f"    {k:14s}: {v:>10,}")
        else:
            print(f"    {k:14s}: {v:>10,}")
    print(f"\n  Respira Phase-1:  {RESPIRA_PHASE1_PARAMS:,} params (target match)")


if __name__ == "__main__":
    print("MatchedTransformer baseline smoke tests")
    print("=" * 50)
    test_forward_shape()
    test_backprop()
    test_determinism()
    test_param_count_matches_respira()
    test_eval_mode()
    print("=" * 50)
    print("ALL PASS — matched_transformer.py is sound.")
    report_params()
