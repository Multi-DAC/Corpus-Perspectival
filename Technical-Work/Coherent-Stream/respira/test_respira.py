"""
Smoke test for the full RespiraCell.

Criteria:
  1. Forward returns logits of shape [batch, seq, vocab] + correct dtype.
  2. trajectory log captures per-cycle structural snapshots when requested.
  3. ACT halt: with halt_threshold low (forces immediate halt) the loop runs ≤ 2 cycles;
     with halt_threshold > 1 (impossible to satisfy) it runs the full max_cycles.
  4. Backprop flows: gradients reach all named parameters from a CE-style loss.
  5. Parameter summary reported for context.
  6. Forward is deterministic given same seed (sanity).

Run from respira/:  python3 test_respira.py
"""
from __future__ import annotations

import torch
import torch.nn.functional as F

from respira import RespiraCell


def _make_cell(**overrides):
    torch.manual_seed(0)
    kw = dict(
        planner_channels=8, executor_channels=16, seq_len=9, vocab_size=11,
        max_cycles=4, planner_omega=(0.05, 0.2), executor_omega=(0.5, 2.0),
        dt=0.1, mu_scale=1.0, halt_threshold=0.7,
        mirror_n_queries=4, mirror_query_dim=16, mirror_hidden_dim=32,
    )
    kw.update(overrides)
    return RespiraCell(**kw)


def _make_batch(batch=2, seq=9, vocab=11):
    torch.manual_seed(0)
    return torch.randint(0, vocab, (batch, seq))


def test_forward_shape() -> None:
    cell = _make_cell()
    x = _make_batch(batch=2, seq=9, vocab=11)
    logits, traj, _ = cell(x)
    ok = (
        logits.shape == (2, 9, 11)
        and logits.dtype == torch.float32
        and traj is None
    )
    print(f"  [TEST 1: forward shape/dtype]  logits.shape={tuple(logits.shape)}  "
          f"{'PASS' if ok else 'FAIL'}")
    assert ok


def test_trajectory_log() -> None:
    cell = _make_cell(halt_threshold=2.0)  # never halts → full max_cycles
    x = _make_batch()
    logits, traj, _ = cell(x, record_trajectory=True)
    ok = (
        traj is not None
        and len(traj) == cell.max_cycles
        and all(set(t.keys()) >= {"cycle", "confidence", "halt", "mu_planner_mean_abs",
                                    "mu_executor_mean_abs", "z_p_amplitude_mean",
                                    "z_e_amplitude_mean", "coupling"} for t in traj)
    )
    print(f"  [TEST 2: trajectory log]  len={len(traj) if traj else 'None'}  "
          f"keys ok={ok}  {'PASS' if ok else 'FAIL'}")
    assert ok


def test_act_halt_low_threshold() -> None:
    """halt_threshold low (close to 0.5) → confidence(~0.5 at init) likely halts within 1-2 cycles.

    With halt_threshold = 0.4, the init confidence ~0.5 will trigger halt on cycle 0 →
    loop runs exactly 1 iteration.
    """
    cell = _make_cell(halt_threshold=0.4)
    x = _make_batch()
    _, traj, _ = cell(x, record_trajectory=True)
    cycles_run = len(traj)
    ok = cycles_run <= 2
    print(f"  [TEST 3a: halt_threshold<conf → early halt]  cycles_run={cycles_run}  "
          f"{'PASS' if ok else 'FAIL'}")
    assert ok

def test_act_halt_high_threshold() -> None:
    """halt_threshold > 1 → impossible to halt → loop runs all max_cycles."""
    cell = _make_cell(halt_threshold=2.0)
    x = _make_batch()
    _, traj, _ = cell(x, record_trajectory=True)
    ok = len(traj) == cell.max_cycles
    print(f"  [TEST 3b: halt_threshold>1 → full run]  cycles_run={len(traj)} "
          f"(expected {cell.max_cycles})  {'PASS' if ok else 'FAIL'}")
    assert ok


def test_backprop_all_params() -> None:
    cell = _make_cell(halt_threshold=2.0)  # force full unroll → gradients hit every cycle
    x = _make_batch(batch=2, seq=9, vocab=11)
    targets = _make_batch(batch=2, seq=9, vocab=11)  # random target tokens
    logits, _, _ = cell(x)
    loss = F.cross_entropy(logits.reshape(-1, cell.vocab_size), targets.reshape(-1))
    loss.backward()
    missing = []
    for name, p in cell.named_parameters():
        if p.grad is None or p.grad.norm().item() == 0:
            missing.append(name)
    ok = not missing
    print(f"  [TEST 4: backprop all params from CE loss]  missing={len(missing)} {missing if missing else ''}  "
          f"{'PASS' if ok else 'FAIL'}")
    assert ok, f"gradients missing for {missing}"


def test_determinism() -> None:
    """Same seed → same output (sanity check for reproducibility)."""
    x = _make_batch()
    torch.manual_seed(0)
    cell1 = _make_cell()
    out1, _, _ = cell1(x)
    torch.manual_seed(0)
    cell2 = _make_cell()
    out2, _, _ = cell2(x)
    max_diff = (out1 - out2).abs().max().item()
    ok = max_diff < 1e-6
    print(f"  [TEST 5: determinism (seed 0 = seed 0)]  max|Δ|={max_diff:.2e}  "
          f"{'PASS' if ok else 'FAIL'}")
    assert ok


def report_params() -> None:
    # Phase-1 starting sizes (per spec)
    cell = RespiraCell(planner_channels=32, executor_channels=64,
                       seq_len=81, vocab_size=11, max_cycles=8)
    s = cell.parameter_summary()
    print("\n  RespiraCell Phase-1 (P=32, E=64, seq=81, vocab=11):")
    for k, v in s.items():
        if k == "total":
            print(f"    {'─' * 30}")
            print(f"    {k:14s}: {v:>10,}")
        else:
            print(f"    {k:14s}: {v:>10,}")


if __name__ == "__main__":
    print("RespiraCell smoke tests")
    print("=" * 50)
    test_forward_shape()
    test_trajectory_log()
    test_act_halt_low_threshold()
    test_act_halt_high_threshold()
    test_backprop_all_params()
    test_determinism()
    print("=" * 50)
    print("ALL PASS — respira.py is sound.")
    report_params()
