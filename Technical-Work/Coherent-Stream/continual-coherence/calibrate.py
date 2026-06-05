"""
Difficulty calibration probe (not part of the experiment — a setup check).

Smoke test revealed difficulty-3 is above the 270m model's bootstrap threshold
(0/8 train correct => empty store => vacuous tier-2 mechanism). This probes bare-model
accuracy across difficulties to find the band where the model succeeds *sometimes*
(store can grow) but not *always* (headroom to improve). Target band ~0.20-0.50.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from config import CONFIG
from domain import generate_batch, check
from model import load_model, build_prompt, generate

N = 32

def main():
    model_name = sys.argv[1] if len(sys.argv) > 1 else CONFIG.base_model
    model, tok = load_model(model_name)
    print(f"model: {model_name}  N={N} per difficulty (bare, k=0)\n", flush=True)
    for d in (1, 2, 3, 4):
        probs = generate_batch(base_seed=555_000 + d, n=N, difficulty=d)
        correct = sum(check(generate(model, tok, build_prompt(p.text)), p.answer) for p in probs)
        print(f"  difficulty {d}: accuracy = {correct/N:.3f}  ({correct}/{N})", flush=True)

if __name__ == "__main__":
    main()
