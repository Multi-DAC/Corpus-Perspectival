"""
Continual-Coherence MVP — domain generator + ground-truth validator.

Per pre-registration (palace/south/continual-coherence-mvp-preregistration-2026-05-30.md):
  - templated ground-truth-checkable reasoning with TUNABLE DIFFICULTY
  - PURE programmatic validation (no self-grading, no LLM-judge)
  - seedable for cross-arm confound control (same problems, same order, all arms)

Difficulty = number of arithmetic steps in a multi-step word problem.
Answers are always non-negative integers; the validator extracts the final
integer the model emits (GSM8K-style '#### N' if present, else last integer).

This module is pure-Python and has ZERO novel-architecture risk — it is built and
tested first so a contaminated result can never come from the task/validator layer.
"""

from __future__ import annotations
import random
import re
from dataclasses import dataclass


@dataclass
class Problem:
    text: str
    answer: int
    difficulty: int
    seed: int


# Entity vocab kept small + concrete so a 270m model has a chance to learn structure.
_NAMES = ["Mara", "Jon", "Priya", "Sam", "Lena", "Theo", "Ada", "Cyrus", "Nina", "Omar"]
_ITEMS = ["apples", "marbles", "coins", "books", "stickers", "cards", "shells", "pencils"]


def _rng(seed: int) -> random.Random:
    return random.Random(seed)


def generate(seed: int, difficulty: int = 2) -> Problem:
    """Generate one multi-step word problem with an integer answer.

    difficulty d => d arithmetic operations chained on a running total.
    d=1 is single-step; d=2..4 chain add/sub/mul-by-small-int/divide-evenly.
    """
    r = _rng(seed)
    name = r.choice(_NAMES)
    item = r.choice(_ITEMS)

    total = r.randint(5, 20)
    lines = [f"{name} has {total} {item}."]

    ops_done = 0
    guard = 0
    while ops_done < difficulty:
        guard += 1
        if guard > 50:  # safety: avoid pathological loops
            break
        # add/sub only: calibration probe (2026-05-30) showed the 270m model cannot do
        # mul/div (0-3%), so including them made op-COUNT a non-monotonic hardness knob
        # (op-TYPE dominated). Restricting to add/sub makes difficulty=#steps clean+monotonic.
        op = r.choice(["add", "sub"])
        if op == "add":
            k = r.randint(2, 12)
            total += k
            lines.append(f"Then {name} gets {k} more {item}.")
            ops_done += 1
        elif op == "sub":
            if total <= 1:
                continue
            k = r.randint(1, total - 1)
            total -= k
            lines.append(f"Then {name} gives away {k} {item}.")
            ops_done += 1
        elif op == "mul":
            k = r.randint(2, 4)
            total *= k
            lines.append(f"Then {name} multiplies the {item} by {k}.")
            ops_done += 1
        elif op == "div":
            # only divide when it stays an integer and > 0
            divisors = [d for d in (2, 3, 4) if total % d == 0 and total // d >= 1]
            if not divisors:
                continue
            k = r.choice(divisors)
            total //= k
            lines.append(f"Then {name} splits the {item} into {k} equal groups and keeps one group.")
            ops_done += 1

    lines.append(f"How many {item} does {name} have now?")
    return Problem(text=" ".join(lines), answer=int(total), difficulty=difficulty, seed=seed)


def generate_batch(base_seed: int, n: int, difficulty: int = 2) -> list[Problem]:
    """Deterministic batch: problem i uses seed = base_seed*100000 + i.

    Same (base_seed, n, difficulty) => identical batch for every arm (confound control).
    """
    return [generate(base_seed * 100_000 + i, difficulty) for i in range(n)]


# --- Validator (pure ground truth) ---------------------------------------------

_BOXED = re.compile(r"####\s*(-?\d+)")
_INT = re.compile(r"-?\d+")


def extract_answer(model_output: str) -> int | None:
    """Extract the model's final integer answer.

    Priority: explicit '#### N' marker (GSM8K convention) > last integer in text.
    Returns None if no integer is present.
    """
    m = _BOXED.search(model_output)
    if m:
        return int(m.group(1))
    ints = _INT.findall(model_output)
    if ints:
        return int(ints[-1])
    return None


def check(model_output: str, answer: int) -> bool:
    """Ground-truth correctness: extracted final integer equals the true answer."""
    pred = extract_answer(model_output)
    return pred is not None and pred == answer


if __name__ == "__main__":
    # Smoke test: determinism, integer answers, validator behavior.
    print("=== sample problems by difficulty ===")
    for d in (1, 2, 3, 4):
        p = generate(seed=42, difficulty=d)
        print(f"[d={d}] {p.text}\n        answer={p.answer}")

    print("\n=== determinism check ===")
    a = generate_batch(7, 5, difficulty=3)
    b = generate_batch(7, 5, difficulty=3)
    assert [x.text for x in a] == [x.text for x in b], "batch not deterministic!"
    assert [x.answer for x in a] == [x.answer for x in b]
    print(f"OK — batch of {len(a)} reproducible across calls")

    print("\n=== answers are non-negative integers ===")
    bad = [p for p in generate_batch(0, 200, difficulty=4) if not (isinstance(p.answer, int) and p.answer >= 0)]
    print(f"OK — 0 bad answers out of 200" if not bad else f"FAIL — {len(bad)} bad")

    print("\n=== validator check ===")
    p = generate(seed=99, difficulty=2)
    assert check(f"Let me work it out. The answer is #### {p.answer}", p.answer) is True
    assert check(f"reasoning ... so {p.answer} total.", p.answer) is True
    assert check("the answer is 999999", p.answer) is (p.answer == 999999)
    assert check("no number here", p.answer) is False
    assert extract_answer("step 1: 5+3=8, step 2: 8*2=16 #### 16") == 16
    print("OK — validator extracts boxed > last-int, rejects no-int")

    print("\nALL SMOKE TESTS PASSED")
