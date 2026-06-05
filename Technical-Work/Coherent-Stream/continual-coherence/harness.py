"""
Continual-Coherence MVP — experience store + retrieval + evaluation.

No novel-architecture risk here: an append-only validated-experience store (firewall
rule 1: augmentative, never rewrites), seeded random-k retrieval, and a ground-truth
evaluation loop. Shared by all arms so the comparison is clean.
"""

from __future__ import annotations
import random
from dataclasses import dataclass, field

from domain import Problem, check, generate_batch
from model import build_prompt, generate as model_generate


@dataclass
class ExperienceStore:
    """Append-only store of validated experience (firewall rule 1)."""
    validated_correct: list[tuple[str, int, str]] = field(default_factory=list)  # (problem, answer, solution)
    validated_incorrect: list[tuple[str, int]] = field(default_factory=list)  # negative corpus

    def add_correct(self, problem_text: str, answer: int, solution: str) -> None:
        self.validated_correct.append((problem_text, answer, solution))

    def add_incorrect(self, problem_text: str, answer: int) -> None:
        self.validated_incorrect.append((problem_text, answer))

    def retrieve(self, k: int, rng: random.Random) -> list[tuple[str, str]]:
        """Seeded random-k validated exemplars as (problem, solution) pairs (memory into context)."""
        if k <= 0 or not self.validated_correct:
            return []
        items = self.validated_correct if len(self.validated_correct) <= k else rng.sample(self.validated_correct, k)
        return [(q, sol) for (q, a, sol) in items]

    def __len__(self) -> int:
        return len(self.validated_correct)


def evaluate(model, tok, problems: list[Problem], store: ExperienceStore | None,
             k_exemplars: int, rng: random.Random, max_new_tokens: int = 96) -> float:
    """Accuracy over a fixed problem set. store=None or k=0 => zero-shot (Arm 0)."""
    correct = 0
    for p in problems:
        exemplars = store.retrieve(k_exemplars, rng) if (store is not None and k_exemplars > 0) else None
        prompt = build_prompt(p.text, exemplars)
        out = model_generate(model, tok, prompt, max_new_tokens=max_new_tokens)
        if check(out, p.answer):
            correct += 1
    return correct / len(problems) if problems else 0.0


def collect_validated(model, tok, problems: list[Problem], store: ExperienceStore,
                      k_exemplars: int, rng: random.Random, max_new_tokens: int = 96) -> tuple[int, int]:
    """Model attempts a batch; ground-truth validator labels; results enter the store.
    Returns (n_correct, n_total). Firewall rule 2: only validated items become eligible.
    """
    n_correct = 0
    for p in problems:
        exemplars = store.retrieve(k_exemplars, rng) if k_exemplars > 0 else None
        prompt = build_prompt(p.text, exemplars)
        out = model_generate(model, tok, prompt, max_new_tokens=max_new_tokens)
        if check(out, p.answer):
            store.add_correct(p.text, p.answer, out)   # store the model's OWN correct solution
            n_correct += 1
        else:
            store.add_incorrect(p.text, p.answer)
    return n_correct, len(problems)


def make_eval_sets(cfg, seed: int):
    """Held-in (same difficulty as training) and held-out general (difficulty 1, disjoint seeds).
    Disjoint seed spaces guarantee no overlap with training problems.
    """
    held_in = generate_batch(base_seed=900_000 + seed, n=cfg.held_in_test_size, difficulty=cfg.difficulty)
    held_out = generate_batch(base_seed=800_000 + seed, n=cfg.held_out_general_size, difficulty=1)
    return held_in, held_out
