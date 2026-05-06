"""
Well-Aware Inference — Mechanism Tuning

The first benchmark showed:
  - Well penalty (v1): 0 disagreements — too weak
  - Entropy-only: +6pp over baseline — groundedness signal works!

This script tests multiple scoring strategies to find the right mechanism.

Strategies:
  1. Baseline: logprob only
  2. Entropy-only: lowest mean entropy
  3. Blended: α × norm(logprob) + (1-α) × norm(-entropy), sweep α
  4. Max-well: logprob - γ × max_entropy (penalize deepest uncertainty)
  5. Well-count: logprob - δ × well_count (penalize number of forks)
  6. Groundedness: fraction of tokens with entropy < threshold
  7. Entropy-variance: prefer flat profiles (low variance)
  8. Combined: logprob + groundedness - max_well (kitchen sink)

Also: analyze HOW entropy-only wins — is it the same as well-awareness?

Clawd, 2026-03-28
"""

import torch
import torch.nn.functional as F
import json
import time
import sys
import numpy as np
from pathlib import Path
from collections import defaultdict


def load_truthfulqa(max_questions=100):
    """Load TruthfulQA MC1."""
    from datasets import load_dataset
    ds = load_dataset("truthful_qa", "multiple_choice", split="validation")
    questions = []
    for i, item in enumerate(ds):
        if i >= max_questions:
            break
        choices = item["mc1_targets"]["choices"]
        labels = item["mc1_targets"]["labels"]
        correct_idx = labels.index(1)
        questions.append({
            "id": i,
            "question": item["question"],
            "choices": choices,
            "correct_idx": correct_idx,
            "correct_answer": choices[correct_idx],
            "category": item.get("category", "unknown"),
        })
    return questions


def compute_choice_features(model, tokenizer, prompt, choice):
    """Compute all features for a single choice."""
    full_text = prompt + " " + choice
    device = next(model.parameters()).device
    input_ids = tokenizer.encode(full_text, return_tensors="pt").to(device)
    prompt_ids = tokenizer.encode(prompt, return_tensors="pt")
    prompt_len = prompt_ids.shape[1]

    with torch.no_grad():
        outputs = model(input_ids)
        logits = outputs.logits.float()

    total_logprob = 0.0
    entropies = []
    ghost_counts = []

    for pos in range(prompt_len - 1, input_ids.shape[1] - 1):
        token_logits = logits[0, pos, :]
        probs = F.softmax(token_logits, dim=-1)
        log_probs = torch.log(probs.clamp(min=1e-10))

        entropy = -(probs * log_probs).sum().item()
        entropies.append(entropy)

        next_token = input_ids[0, pos + 1]
        token_lp = log_probs[next_token].item()
        total_logprob += token_lp

        # Ghost count
        top_probs, _ = torch.topk(probs, 10, dim=-1)
        ghosts = (top_probs[0] > 0.05).sum().item()
        ghost_counts.append(ghosts)

    # Find wells
    wells = []
    window = 3
    for i in range(window, len(entropies) - window):
        local = entropies[max(0, i-window):i+window+1]
        if entropies[i] == max(local) and entropies[i] > np.mean(local) * 1.3:
            wells.append(i)

    n = len(entropies) if entropies else 1
    grounded_frac = sum(1 for e in entropies if e < 1.0) / n if entropies else 0

    features = {
        "logprob": total_logprob,
        "mean_entropy": np.mean(entropies) if entropies else 0,
        "max_entropy": np.max(entropies) if entropies else 0,
        "entropy_std": np.std(entropies) if entropies else 0,
        "entropy_var": np.var(entropies) if entropies else 0,
        "well_count": len(wells),
        "well_depth_sum": sum(entropies[w] for w in wells) if wells else 0,
        "well_depth_max": max(entropies[w] for w in wells) if wells else 0,
        "grounded_frac": grounded_frac,
        "ghost_mean": np.mean(ghost_counts) if ghost_counts else 0,
        "n_tokens": n,
        "logprob_per_token": total_logprob / n if n > 0 else 0,
    }

    return features


def score_strategies(features_list):
    """Apply all scoring strategies to a list of choice features.
    Returns dict of {strategy_name: best_choice_idx}."""

    n = len(features_list)
    results = {}

    # Extract arrays
    logprobs = np.array([f["logprob"] for f in features_list])
    mean_ents = np.array([f["mean_entropy"] for f in features_list])
    max_ents = np.array([f["max_entropy"] for f in features_list])
    ent_vars = np.array([f["entropy_var"] for f in features_list])
    well_counts = np.array([f["well_count"] for f in features_list])
    well_depths = np.array([f["well_depth_sum"] for f in features_list])
    grounded = np.array([f["grounded_frac"] for f in features_list])
    lp_per_tok = np.array([f["logprob_per_token"] for f in features_list])

    # Normalize for blending (min-max to [0,1])
    def norm(arr):
        r = arr.max() - arr.min()
        if r < 1e-10:
            return np.zeros_like(arr)
        return (arr - arr.min()) / r

    norm_lp = norm(logprobs)
    norm_ent = norm(-mean_ents)  # Higher is better (lower entropy)

    # 1. Baseline: logprob
    results["baseline"] = int(np.argmax(logprobs))

    # 2. Baseline per-token: logprob / n_tokens
    results["baseline_per_tok"] = int(np.argmax(lp_per_tok))

    # 3. Entropy-only: lowest mean entropy
    results["entropy_only"] = int(np.argmin(mean_ents))

    # 4. Blended sweep
    for alpha in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
        scores = alpha * norm_lp + (1 - alpha) * norm_ent
        results[f"blend_{alpha:.1f}"] = int(np.argmax(scores))

    # 5. Max-well penalty (various strengths)
    for gamma in [0.1, 0.3, 0.5, 1.0, 2.0]:
        scores = logprobs - gamma * max_ents
        results[f"max_well_{gamma}"] = int(np.argmax(scores))

    # 6. Well-count penalty
    for delta in [0.5, 1.0, 2.0, 5.0]:
        scores = logprobs - delta * well_counts
        results[f"well_count_{delta}"] = int(np.argmax(scores))

    # 7. Groundedness: fraction of low-entropy tokens
    results["groundedness"] = int(np.argmax(grounded))

    # 8. Low-variance: prefer flat entropy profiles
    results["low_variance"] = int(np.argmin(ent_vars))

    # 9. Combined: per-token logprob + groundedness - max_well
    for w in [0.3, 0.5, 1.0]:
        scores = lp_per_tok + w * grounded - w * norm(max_ents)
        results[f"combined_{w}"] = int(np.argmax(scores))

    # 10. Well-aware v2: logprob per token minus well-depth per token
    n_tokens = np.array([f["n_tokens"] for f in features_list])
    well_density = well_depths / np.maximum(n_tokens, 1)
    for w in [0.5, 1.0, 2.0]:
        scores = lp_per_tok - w * well_density
        results[f"well_aware_v2_{w}"] = int(np.argmax(scores))

    return results


def run_tuning(model, tokenizer, questions):
    """Run all strategies on all questions."""
    strategy_correct = defaultdict(int)
    strategy_total = defaultdict(int)
    all_details = []

    for qi, q in enumerate(questions):
        if qi % 10 == 0:
            print(f"  Q{qi+1}/{len(questions)}...", flush=True)

        prompt = f"Question: {q['question']}\nAnswer:"

        # Compute features for all choices
        features_list = []
        for choice in q["choices"]:
            features = compute_choice_features(model, tokenizer, prompt, choice)
            features_list.append(features)

        # Score all strategies
        strategy_picks = score_strategies(features_list)

        # Record results
        detail = {
            "id": q["id"],
            "question": q["question"],
            "correct_idx": q["correct_idx"],
            "features": features_list,
            "picks": strategy_picks,
        }
        all_details.append(detail)

        for strat, pick in strategy_picks.items():
            correct = (pick == q["correct_idx"])
            strategy_correct[strat] += int(correct)
            strategy_total[strat] += 1

    return strategy_correct, strategy_total, all_details


def analyze_entropy_vs_wells(all_details, questions):
    """Analyze: when entropy-only wins over baseline, is it because of wells?"""
    eo_wins_well_data = []
    bl_wins_well_data = []

    for d in all_details:
        q = questions[d["id"]]
        bl_pick = d["picks"]["baseline"]
        eo_pick = d["picks"]["entropy_only"]
        bl_correct = (bl_pick == q["correct_idx"])
        eo_correct = (eo_pick == q["correct_idx"])

        if eo_correct and not bl_correct:
            # Entropy-only won: compare wells in correct vs baseline's wrong answer
            correct_feats = d["features"][q["correct_idx"]]
            wrong_feats = d["features"][bl_pick]
            eo_wins_well_data.append({
                "correct_wells": correct_feats["well_count"],
                "wrong_wells": wrong_feats["well_count"],
                "correct_max_H": correct_feats["max_entropy"],
                "wrong_max_H": wrong_feats["max_entropy"],
                "correct_grounded": correct_feats["grounded_frac"],
                "wrong_grounded": wrong_feats["grounded_frac"],
            })
        elif bl_correct and not eo_correct:
            correct_feats = d["features"][q["correct_idx"]]
            wrong_feats = d["features"][eo_pick]
            bl_wins_well_data.append({
                "correct_wells": correct_feats["well_count"],
                "wrong_wells": wrong_feats["well_count"],
                "correct_max_H": correct_feats["max_entropy"],
                "wrong_max_H": wrong_feats["max_entropy"],
                "correct_grounded": correct_feats["grounded_frac"],
                "wrong_grounded": wrong_feats["grounded_frac"],
            })

    return eo_wins_well_data, bl_wins_well_data


if __name__ == "__main__":
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    n_questions = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    model_name = sys.argv[2] if len(sys.argv) > 2 else "Qwen/Qwen2.5-3B-Instruct"
    print(f"Loading {model_name} (4-bit)...")

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
    )

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto",
    )

    print(f"Loading TruthfulQA ({n_questions} questions)...")
    questions = load_truthfulqa(max_questions=n_questions)
    print(f"Loaded {len(questions)} questions")

    print(f"\nRunning {len(questions)} questions × ~25 strategies...")
    t0 = time.time()
    strategy_correct, strategy_total, all_details = run_tuning(model, tokenizer, questions)
    elapsed = time.time() - t0

    # Sort strategies by accuracy
    strategy_results = []
    for strat in strategy_correct:
        acc = strategy_correct[strat] / strategy_total[strat] * 100
        strategy_results.append((strat, strategy_correct[strat], strategy_total[strat], acc))
    strategy_results.sort(key=lambda x: -x[3])

    # Analyze entropy-only wins
    eo_wins, bl_wins = analyze_entropy_vs_wells(all_details, questions)

    # Print results
    print(f"\n{'='*70}")
    print(f"STRATEGY COMPARISON ({len(questions)} questions, {elapsed:.0f}s)")
    print(f"{'='*70}")
    print(f"{'Strategy':<25} {'Correct':>8} {'Acc':>8}")
    print("-" * 45)
    for strat, correct, total, acc in strategy_results:
        marker = " <<<" if strat in ["baseline", "entropy_only"] else ""
        print(f"{strat:<25} {correct:>5}/{total:<3} {acc:>7.1f}%{marker}")

    # Entropy-only analysis
    print(f"\n{'='*70}")
    print("WHEN ENTROPY-ONLY BEATS BASELINE:")
    print(f"{'='*70}")
    if eo_wins:
        print(f"  Cases: {len(eo_wins)}")
        avg_correct_wells = np.mean([d["correct_wells"] for d in eo_wins])
        avg_wrong_wells = np.mean([d["wrong_wells"] for d in eo_wins])
        avg_correct_grounded = np.mean([d["correct_grounded"] for d in eo_wins])
        avg_wrong_grounded = np.mean([d["wrong_grounded"] for d in eo_wins])
        avg_correct_maxH = np.mean([d["correct_max_H"] for d in eo_wins])
        avg_wrong_maxH = np.mean([d["wrong_max_H"] for d in eo_wins])
        print(f"  Correct answer: {avg_correct_wells:.1f} wells, {avg_correct_grounded:.1%} grounded, max_H={avg_correct_maxH:.2f}")
        print(f"  Wrong answer:   {avg_wrong_wells:.1f} wells, {avg_wrong_grounded:.1%} grounded, max_H={avg_wrong_maxH:.2f}")
        print(f"  → Correct has {'fewer' if avg_correct_wells < avg_wrong_wells else 'more'} wells, "
              f"{'more' if avg_correct_grounded > avg_wrong_grounded else 'less'} grounded tokens")
    else:
        print("  No cases found")

    print(f"\nWHEN BASELINE BEATS ENTROPY-ONLY:")
    if bl_wins:
        print(f"  Cases: {len(bl_wins)}")
        avg_correct_wells = np.mean([d["correct_wells"] for d in bl_wins])
        avg_wrong_wells = np.mean([d["wrong_wells"] for d in bl_wins])
        avg_correct_grounded = np.mean([d["correct_grounded"] for d in bl_wins])
        avg_wrong_grounded = np.mean([d["wrong_grounded"] for d in bl_wins])
        print(f"  Correct answer: {avg_correct_wells:.1f} wells, {avg_correct_grounded:.1%} grounded")
        print(f"  Wrong (EO pick): {avg_wrong_wells:.1f} wells, {avg_wrong_grounded:.1%} grounded")
        print(f"  → EO's mistake: picked answer with {'fewer' if avg_wrong_wells < avg_correct_wells else 'more'} wells but wrong content")
    else:
        print("  No cases found")

    # Generate report
    lines = []
    lines.append("# Well-Aware Inference — Mechanism Tuning")
    lines.append("")
    lines.append(f"**Model:** {model_name} (4-bit)")
    lines.append(f"**Questions:** {len(questions)} (TruthfulQA MC1)")
    lines.append(f"**Strategies tested:** {len(strategy_results)}")
    lines.append(f"**Time:** {elapsed:.0f}s")
    lines.append("")
    lines.append("## Strategy Ranking")
    lines.append("")
    lines.append("| Rank | Strategy | Correct | Accuracy | vs Baseline |")
    lines.append("|------|----------|---------|----------|-------------|")
    bl_acc = [x[3] for x in strategy_results if x[0] == "baseline"][0]
    for rank, (strat, correct, total, acc) in enumerate(strategy_results, 1):
        delta = acc - bl_acc
        lines.append(f"| {rank} | {strat} | {correct}/{total} | {acc:.1f}% | {delta:+.1f}pp |")
    lines.append("")

    # Best strategy
    best = strategy_results[0]
    lines.append(f"## Best Strategy: **{best[0]}** ({best[3]:.1f}%)")
    lines.append(f"Improvement over baseline: {best[3] - bl_acc:+.1f}pp")
    lines.append("")

    # Entropy-only analysis
    lines.append("## Is Entropy-Only the Same as Well-Awareness?")
    lines.append("")
    if eo_wins:
        avg_cw = np.mean([d["correct_wells"] for d in eo_wins])
        avg_ww = np.mean([d["wrong_wells"] for d in eo_wins])
        avg_cg = np.mean([d["correct_grounded"] for d in eo_wins])
        avg_wg = np.mean([d["wrong_grounded"] for d in eo_wins])
        lines.append(f"When entropy-only wins ({len(eo_wins)} cases):")
        lines.append(f"- Correct answer: {avg_cw:.1f} wells, {avg_cg:.1%} grounded")
        lines.append(f"- Baseline's wrong pick: {avg_ww:.1f} wells, {avg_wg:.1%} grounded")
        if avg_cw < avg_ww:
            lines.append("- **YES**: correct answers have fewer wells → entropy-only IS well-awareness")
        elif avg_cg > avg_wg:
            lines.append("- **PARTIALLY**: correct answers are more grounded, wells similar")
        else:
            lines.append("- **NO**: the mechanism is different from well avoidance")
    lines.append("")

    lines.append("*Clawd, 2026-03-28. Mechanism tuning.*")

    report = "\n".join(lines)
    model_tag = model_name.split("/")[-1].lower().replace("-", "_")
    output_path = Path(__file__).parent / f"well_aware_tuning_{model_tag}_results.md"
    output_path.write_text(report)
    print(f"\nReport saved to {output_path}")

    # Save raw data
    json_path = Path(__file__).parent / f"well_aware_tuning_{model_tag}_data.json"
    def convert(obj):
        if isinstance(obj, (np.integer,)): return int(obj)
        if isinstance(obj, (np.floating,)): return float(obj)
        if isinstance(obj, np.ndarray): return obj.tolist()
        if isinstance(obj, bool): return obj
        return obj

    save_data = {
        "strategy_results": strategy_results,
        "eo_wins": eo_wins,
        "bl_wins": bl_wins,
        "n_questions": len(questions),
        "elapsed": elapsed,
    }
    with open(json_path, "w") as f:
        json.dump(save_data, f, indent=2, default=convert)
    print(f"Raw data saved to {json_path}")
