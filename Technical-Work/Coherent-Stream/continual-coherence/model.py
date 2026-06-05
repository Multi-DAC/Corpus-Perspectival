"""
Continual-Coherence MVP — model interface (load + generate + shared prompt framing).

Runs in WSL (Ubuntu, torch 2.11+cu128, transformers 5.4, peft 0.18) via the
/mnt/c/.../continual_coherence path. Pure inference + prompt-building here; the novel
tier-3 LoRA consolidation lives in arm_b_tier3.py (built separately, carefully).

Fairness invariant: ALL arms share the SAME task-framing preamble. The preamble is
task instruction + answer-format spec + ONE fixed worked example. It is NOT memory —
it is constant across arms. The only variables between arms are (A) retrieved
validated exemplars [memory] and (B) consolidated weights. This prevents the floor
arm from being unfairly handicapped on output format.
"""

from __future__ import annotations
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Shared across ALL arms — task framing only, never grows, never counts as "memory".
SYSTEM_PREAMBLE = (
    "Solve the word problem step by step, then give the final integer answer "
    "on its own line in the form '#### N'.\n\n"
    "Problem: Ada has 4 coins. Then Ada gets 3 more coins. How many coins does Ada have now?\n"
    "Step by step: 4 + 3 = 7.\n"
    "#### 7\n"
)


def load_model(model_name: str, dtype=torch.bfloat16):
    tok = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=dtype, device_map="cuda"
    )
    model.eval()
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    return model, tok


def build_prompt(problem_text: str, exemplars: list[tuple[str, str]] | None = None) -> str:
    """Compose the prompt: shared preamble + (optional) validated memory exemplars + target.

    exemplars: list of (problem_text, solution_text) from the validated store, where
    solution_text is the model's OWN validated-correct output (reasoning + '#### N').
    Replaying real worked solutions = genuine memory of validated experience.
    Arm 0 passes exemplars=None (no memory). Arms A/B pass retrieved validated exemplars.
    """
    parts = [SYSTEM_PREAMBLE]
    if exemplars:
        for q, sol in exemplars:
            parts.append(f"\nProblem: {q}\nStep by step:{sol}\n")
    parts.append(f"\nProblem: {problem_text}\nStep by step:")
    return "".join(parts)


@torch.no_grad()
def generate(model, tok, prompt: str, max_new_tokens: int = 96) -> str:
    inputs = tok(prompt, return_tensors="pt").to(model.device)
    out = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        do_sample=False,            # greedy — deterministic, confound control
        temperature=None,
        top_p=None,
        top_k=None,
        pad_token_id=tok.pad_token_id,
        stop_strings=["\nProblem:"],  # halt before the model hallucinates a follow-up problem
        tokenizer=tok,
    )
    # Return only the newly generated continuation.
    gen = out[0][inputs["input_ids"].shape[1]:]
    text = tok.decode(gen, skip_special_tokens=True)
    # Belt-and-suspenders: truncate at any hallucinated follow-up so extraction stays on-target.
    return text.split("\nProblem:")[0]


if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    from domain import generate as gen_problem, check, extract_answer
    from config import CONFIG

    print(f"loading {CONFIG.base_model} ...")
    model, tok = load_model(CONFIG.base_model)
    print("loaded.")

    p = gen_problem(seed=42, difficulty=CONFIG.difficulty)
    prompt = build_prompt(p.text)
    print(f"\nPROBLEM: {p.text}\nTRUE ANSWER: {p.answer}")
    completion = generate(model, tok, prompt)
    print(f"\nMODEL OUTPUT:\n{completion}")
    print(f"\nEXTRACTED: {extract_answer(completion)}  CORRECT: {check(completion, p.answer)}")
    print("\nmodel.py smoke test complete.")
