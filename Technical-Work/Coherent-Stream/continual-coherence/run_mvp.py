"""
Continual-Coherence MVP — orchestrator.

Runs Arm 0 (frozen-bare) and Arm A (tier-2 memory) tonight (no novel code).
Arm B (tier-2+tier-3 consolidation) is the NOVEL component — stubbed here as pending,
to be built carefully in arm_b_tier3.py and plugged into this same harness so the
comparison stays clean (pinned seeds + identical problems via config/domain).

Usage (in WSL):
  python3 continual_coherence/run_mvp.py            # full ratified config, arms 0 + A
  python3 continual_coherence/run_mvp.py --smoke     # tiny fast end-to-end check
  python3 continual_coherence/run_mvp.py --arm tier2_tier3   # -> NotImplemented (pending)
"""

from __future__ import annotations
import argparse, json, os, random, time
from dataclasses import replace

from config import CONFIG
from harness import ExperienceStore, evaluate, collect_validated, make_eval_sets
from domain import generate_batch

RETRIEVAL_K = 3  # few-shot validated exemplars for tier-2 arms (Arm 0 uses 0)


def run_arm_seed(model, tok, cfg, arm: str, seed: int) -> dict:
    rng = random.Random(seed)            # retrieval determinism
    held_in, held_out = make_eval_sets(cfg, seed)
    store = ExperienceStore()
    k = 0 if arm == "frozen_bare" else RETRIEVAL_K

    in_domain, held_out_acc, store_sizes = [], [], []

    # Arm 0: weights frozen, no memory => identical every round. Eval once, replicate.
    if arm == "frozen_bare":
        acc_in = evaluate(model, tok, held_in, None, 0, rng)
        acc_out = evaluate(model, tok, held_out, None, 0, rng)
        in_domain = [acc_in] * cfg.n_rounds
        held_out_acc = [acc_out] * cfg.n_rounds
        store_sizes = [0] * cfg.n_rounds
        return _result(arm, seed, in_domain, held_out_acc, store_sizes)

    # Arm A: memory grows each round; held-out (k=0) is constant (frozen weights) but recorded.
    for r in range(cfg.n_rounds):
        in_domain.append(evaluate(model, tok, held_in, store, k, rng))
        held_out_acc.append(evaluate(model, tok, held_out, None, 0, rng))  # forgetting check, raw capability
        store_sizes.append(len(store))
        train = generate_batch(base_seed=seed * 1000 + r, n=cfg.train_problems_per_round, difficulty=cfg.difficulty)
        n_ok, n_tot = collect_validated(model, tok, train, store, k, rng)
        print(f"    [{arm} seed{seed} round{r}] in={in_domain[-1]:.3f} out={held_out_acc[-1]:.3f} "
              f"store={store_sizes[-1]} train_ok={n_ok}/{n_tot}", flush=True)

    return _result(arm, seed, in_domain, held_out_acc, store_sizes)


def _result(arm, seed, in_domain, held_out_acc, store_sizes) -> dict:
    return {
        "arm": arm, "seed": seed,
        "in_domain_trajectory": in_domain,
        "held_out_trajectory": held_out_acc,
        "store_sizes": store_sizes,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true", help="tiny fast config")
    ap.add_argument("--arm", default=None, help="run a single arm")
    args = ap.parse_args()

    cfg = CONFIG
    if args.smoke:
        cfg = replace(cfg, n_rounds=2, seeds=(0,), train_problems_per_round=8,
                      held_in_test_size=16, held_out_general_size=16)

    arms = [args.arm] if args.arm else ["frozen_bare", "tier2_memory"]
    if "tier2_tier3" in arms:
        raise NotImplementedError(
            "Arm tier2_tier3 (tier-3 consolidation) is the NOVEL component — build it "
            "carefully in arm_b_tier3.py per the pre-reg, then add it to this orchestrator."
        )

    from model import load_model
    print(f"loading {cfg.base_model} ...", flush=True)
    model, tok = load_model(cfg.base_model)
    print("loaded.", flush=True)

    os.makedirs(cfg.results_dir, exist_ok=True)
    tag = "smoke" if args.smoke else "full"
    all_results = []
    t0 = time.time()
    for arm in arms:
        for seed in cfg.seeds:
            print(f"\n=== {arm} seed {seed} ===", flush=True)
            res = run_arm_seed(model, tok, cfg, arm, seed)
            all_results.append(res)
            with open(os.path.join(cfg.results_dir, f"{tag}_{arm}_seed{seed}.json"), "w") as f:
                json.dump(res, f, indent=2)

    summary_path = os.path.join(cfg.results_dir, f"{tag}_arms0A_results.json")
    with open(summary_path, "w") as f:
        json.dump({"config_tag": tag, "retrieval_k": RETRIEVAL_K,
                   "elapsed_sec": round(time.time() - t0, 1), "results": all_results}, f, indent=2)
    print(f"\nDONE in {time.time()-t0:.1f}s -> {summary_path}", flush=True)


if __name__ == "__main__":
    main()
