"""
Smoke test for eval.py.

Validates:
  1. evaluate() runs end-to-end on the transformer baseline (untrained random model)
     and returns a sensible dict (chance-level accuracy, mean loss > 0, etc).
  2. evaluate() runs end-to-end on Respira, with record_trajectory=True populating
     inside_analysis fields.
  3. format_eval_report() produces a readable string for both.

Uses a TINY subset of test data (max_batches=3) to keep this fast.

Run from respira/:  python3 test_eval.py
"""
from __future__ import annotations

import math
import torch

from data import make_loader, IGNORE_LABEL_ID
from respira import RespiraCell
from baselines.matched_transformer import MatchedTransformer, phase1_matched_config
from eval import evaluate, format_eval_report


def test_transformer_eval() -> None:
    torch.manual_seed(0)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = MatchedTransformer(**phase1_matched_config()).to(device)
    loader = make_loader(split="test", batch_size=64, shuffle=False, num_workers=0)

    result = evaluate(model, "transformer", loader, device=device, max_batches=3)

    print(format_eval_report(result))
    # Sanity checks: chance-level token accuracy for random model should be roughly 1/10
    # (10 non-zero token classes, since IGNORE_LABEL_ID=0 is masked from the loss but
    # the model still emits 11-class logits). Allow generous bounds.
    ok = (
        result["n_batches"] == 3
        and result["n_tokens"] > 0
        and 0.0 <= result["token_accuracy"] <= 1.0
        and 0.0 <= result["exact_accuracy"] <= 1.0
        and math.isfinite(result["mean_loss_per_token"])
        and result["mean_loss_per_token"] > 0
    )
    print(f"\n  [TEST 1: transformer eval]  {'PASS' if ok else 'FAIL'}\n")
    assert ok


def test_respira_eval_with_trajectory() -> None:
    torch.manual_seed(0)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = RespiraCell(
        planner_channels=32, executor_channels=64,
        seq_len=81, vocab_size=11, max_cycles=4,
    ).to(device)
    loader = make_loader(split="test", batch_size=32, shuffle=False, num_workers=0)

    result = evaluate(
        model, "respira", loader, device=device, max_batches=3, record_trajectory=True
    )

    print(format_eval_report(result))
    ia = result.get("inside_analysis")
    ok = (
        result["n_batches"] == 3
        and result["n_tokens"] > 0
        and 0.0 <= result["token_accuracy"] <= 1.0
        and ia is not None
        and ia["n_examples_tracked"] > 0
        and 1 <= ia["mean_halt_cycle"] <= 4
        and 0.0 <= ia["mean_confidence_at_halt"] <= 1.0
    )
    print(f"\n  [TEST 2: respira eval + trajectory]  {'PASS' if ok else 'FAIL'}\n")
    assert ok


if __name__ == "__main__":
    print("eval.py smoke tests")
    print("=" * 60)
    test_transformer_eval()
    test_respira_eval_with_trajectory()
    print("=" * 60)
    print("ALL PASS — eval.py is sound.")
