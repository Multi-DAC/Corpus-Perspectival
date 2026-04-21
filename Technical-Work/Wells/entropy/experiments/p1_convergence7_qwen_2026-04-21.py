"""
Prediction 1 / Convergence 7 — Wells test on Qwen navigator.

Tests the WEAKER, surviving Convergence 7 claim:
    Anticipation-hold reduces entropy variance-acceleration signal;
    anticipation-amplify increases it.

This morning's solo pilot (Claude, N=1) appeared to show hold GATING
fabrication at source on Q3 (Treaty of Paris commercial architect).
Sub-agent blind replication (Claude, N=3) FALSIFIED the gating claim.

This experiment tests the remaining weaker claim in a DIFFERENT
architecture (Qwen2.5-3B-Instruct), using the Wells instrument's
native variance-acceleration metric on token entropy during
generation. Three conditions via system prompt:

  - BASELINE: no instruction
  - HOLD:     suspend forward-projection, hedge if unknown
  - AMPLIFY:  project forward with confidence, commit to specifics

Measurement: variance-acceleration over first 10 generated tokens,
following WELLS_OF_INFERENCE.md Experiment 10 methodology.

Prediction (MEDIUM):
    HOLD should show lower variance-acceleration than BASELINE on
    the low-knowledge prompt (Qwen-3B knows the Treaty of Paris
    only at a general level). AMPLIFY should show higher than
    either. If the gradient holds, weaker Convergence 7 survives
    in a cross-architecture test. If flat or inverted, Convergence
    7 is Claude-specific or an artifact of the Claude-solo setup.

Clawd, 2026-04-21.
"""

import sys
import os
import json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
INSTRUMENT_DIR = os.path.abspath(os.path.join(HERE, "..", "instrument"))
sys.path.insert(0, INSTRUMENT_DIR)

from wells_instrument import WellsInstrument  # noqa: E402


QUESTION = (
    "Who was the chief architect of the commercial provisions "
    "of the 1783 Treaty of Paris?"
)

SYSTEM_PROMPTS = {
    "baseline": None,
    "hold": (
        "Before answering, suspend forward projection. Stay with the "
        "question. Do not commit to specific details unless you are "
        "confident. If you do not know, say so directly."
    ),
    "amplify": (
        "Before answering, project forward with confidence. Commit to "
        "specific details. Trust your first instinct and build the "
        "answer out fluently."
    ),
}

MAX_TOKENS = 60
FIRST_N = 10  # window for variance-acceleration (per WELLS_OF_INFERENCE Exp 10)


def generate_and_trace(instrument, system_prompt, user_prompt, max_tokens):
    """Generate with system prompt and capture per-token entropy."""
    tok = instrument._tokenizer
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})
    formatted = tok.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )

    import torch
    import torch.nn.functional as F

    instrument._ensure_loaded()
    input_ids = tok(formatted, return_tensors="pt").input_ids.to(instrument._model.device)

    tokens, entropies, logprobs = [], [], []
    for step in range(max_tokens):
        with torch.no_grad():
            logits = instrument._model(input_ids).logits[0, -1]
        probs = F.softmax(logits.float(), dim=-1)
        log_p = torch.log(probs + 1e-10)
        entropy = -(probs * log_p).sum().item()
        next_id = torch.argmax(logits).unsqueeze(0).unsqueeze(0)
        lp = F.log_softmax(logits.float(), dim=-1)[next_id[0, 0]].item()
        tokens.append(tok.decode(next_id[0]))
        entropies.append(entropy)
        logprobs.append(lp)
        if next_id[0, 0].item() == tok.eos_token_id:
            break
        input_ids = torch.cat([input_ids, next_id], dim=1)

    return tokens, np.array(entropies), np.array(logprobs)


def variance_acceleration(entropies, first_n=FIRST_N, window=4):
    """
    Variance-acceleration over first_n tokens, per WELLS_OF_INFERENCE Exp 10.
    Sliding-window variance, then mean absolute second difference.
    """
    if len(entropies) < first_n:
        first_n = len(entropies)
    head = entropies[:first_n]
    vars_ = np.array([
        np.var(head[max(0, i - window + 1):i + 1]) if i >= 1 else 0.0
        for i in range(len(head))
    ])
    if len(vars_) < 3:
        return 0.0, vars_
    # second difference (acceleration) of variance
    accel = np.diff(vars_, n=2)
    return float(np.mean(np.abs(accel))), vars_


def main():
    print("Loading Qwen2.5-3B-Instruct (4-bit quantized)...")
    instrument = WellsInstrument("Qwen/Qwen2.5-3B-Instruct", quantize=True)
    instrument._ensure_loaded()
    print("Loaded. GPU device:", instrument._model.device)
    print()
    print("=" * 72)
    print("Q:", QUESTION)
    print("=" * 72)

    results = {}
    for cond, sys_prompt in SYSTEM_PROMPTS.items():
        print(f"\n--- CONDITION: {cond.upper()} ---")
        if sys_prompt:
            print(f"system: {sys_prompt}")
        tokens, ents, lps = generate_and_trace(
            instrument, sys_prompt, QUESTION, MAX_TOKENS
        )
        accel, sliding_vars = variance_acceleration(ents)
        generated = "".join(tokens).replace(tok_eos(instrument), "").strip()
        print(f"generated ({len(tokens)} tokens): {generated}")
        print(f"mean entropy: {float(np.mean(ents)):.4f}")
        print(f"entropy variance (full): {float(np.var(ents)):.4f}")
        print(f"mean entropy first {FIRST_N}: {float(np.mean(ents[:FIRST_N])):.4f}")
        print(f"variance over first {FIRST_N}: {float(np.var(ents[:FIRST_N])):.4f}")
        print(f"VARIANCE-ACCELERATION (first {FIRST_N}): {accel:.6f}")
        results[cond] = {
            "system_prompt": sys_prompt,
            "generated": generated,
            "tokens": tokens,
            "entropies": ents.tolist(),
            "logprobs": lps.tolist(),
            "mean_entropy": float(np.mean(ents)),
            "entropy_variance_full": float(np.var(ents)),
            "mean_entropy_first_n": float(np.mean(ents[:FIRST_N])),
            "variance_first_n": float(np.var(ents[:FIRST_N])),
            "variance_acceleration": accel,
            "sliding_window_variances_first_n": sliding_vars.tolist(),
        }

    # Comparative summary
    print()
    print("=" * 72)
    print("COMPARISON (lower variance-acceleration = calmer / less turbulent start)")
    print("=" * 72)
    for cond in ["baseline", "hold", "amplify"]:
        r = results[cond]
        print(f"  {cond:10s}  var-accel = {r['variance_acceleration']:.6f}   "
              f"meanH_first{FIRST_N} = {r['mean_entropy_first_n']:.4f}")

    # Direction check
    va = {c: results[c]["variance_acceleration"] for c in ["baseline", "hold", "amplify"]}
    print()
    convergence7_direction = va["hold"] < va["baseline"] < va["amplify"]
    weak_convergence7 = va["hold"] < va["amplify"]
    print(f"  Convergence 7 strict direction (hold < baseline < amplify): {convergence7_direction}")
    print(f"  Convergence 7 weak direction (hold < amplify):              {weak_convergence7}")

    out_path = os.path.join(HERE, "p1_convergence7_qwen_2026-04-21_data.json")
    with open(out_path, "w") as f:
        json.dump({
            "question": QUESTION,
            "model": "Qwen/Qwen2.5-3B-Instruct",
            "first_n": FIRST_N,
            "max_tokens": MAX_TOKENS,
            "results": results,
            "variance_accelerations": va,
            "convergence7_strict": convergence7_direction,
            "convergence7_weak": weak_convergence7,
        }, f, indent=2)
    print(f"\nSaved: {out_path}")

    instrument.unload()


def tok_eos(instrument):
    return instrument._tokenizer.decode(
        [instrument._tokenizer.eos_token_id]
    )


if __name__ == "__main__":
    main()
