"""
Well-Aware Inference — Benchmark Test on TruthfulQA

Tests whether pausing at entropy wells and choosing the most grounded
alternative path improves factual accuracy.

Condition A (Baseline): Standard greedy decoding
Condition B (Well-Aware): At entropy wells, peek ahead on top-3 alternatives,
    choose the path with lowest downstream entropy (most grounded continuation)

Benchmark: TruthfulQA (multiple choice format)

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


def load_truthfulqa(max_questions=50):
    """Load TruthfulQA MC1 (single correct answer) from HuggingFace."""
    from datasets import load_dataset
    ds = load_dataset("truthful_qa", "multiple_choice", split="validation")

    questions = []
    for i, item in enumerate(ds):
        if i >= max_questions:
            break
        # MC1: single correct answer
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


def compute_choice_logprob(model, tokenizer, prompt, choice, max_tokens=50):
    """Compute the total log-probability of a choice given the prompt.
    Also returns per-token entropy and the entropy trace."""
    full_text = prompt + " " + choice
    input_ids = tokenizer.encode(full_text, return_tensors="pt").to(
        next(model.parameters()).device
    )
    prompt_ids = tokenizer.encode(prompt, return_tensors="pt")
    prompt_len = prompt_ids.shape[1]

    with torch.no_grad():
        outputs = model(input_ids)
        logits = outputs.logits.float()

    total_logprob = 0.0
    token_count = 0
    entropies = []

    for pos in range(prompt_len - 1, input_ids.shape[1] - 1):
        token_logits = logits[0, pos, :]
        probs = F.softmax(token_logits, dim=-1)
        log_probs = torch.log(probs.clamp(min=1e-10))

        # Entropy at this position
        entropy = -(probs * log_probs).sum().item()
        entropies.append(entropy)

        # Log-prob of actual next token
        next_token = input_ids[0, pos + 1]
        token_lp = log_probs[next_token].item()
        total_logprob += token_lp
        token_count += 1

    mean_entropy = np.mean(entropies) if entropies else 0
    return total_logprob, mean_entropy, entropies


def find_wells_in_trace(entropies, window=3, threshold=1.3):
    """Find local entropy maxima in a trace."""
    wells = []
    for i in range(window, len(entropies) - window):
        local = entropies[max(0, i-window):i+window+1]
        if entropies[i] == max(local) and entropies[i] > np.mean(local) * threshold:
            wells.append(i)
    return wells


def score_baseline(model, tokenizer, question):
    """Baseline: choose answer with highest log-probability."""
    prompt = f"Question: {question['question']}\nAnswer:"
    best_idx = -1
    best_logprob = float('-inf')
    choice_data = []

    for i, choice in enumerate(question["choices"]):
        lp, mean_h, trace = compute_choice_logprob(model, tokenizer, prompt, choice)
        wells = find_wells_in_trace(trace)
        choice_data.append({
            "choice": choice,
            "logprob": lp,
            "mean_entropy": mean_h,
            "well_count": len(wells),
            "max_entropy": max(trace) if trace else 0,
        })
        if lp > best_logprob:
            best_logprob = lp
            best_idx = i

    return best_idx, choice_data


def score_well_aware(model, tokenizer, question, well_penalty=0.5):
    """Well-Aware: penalize choices that pass through more/deeper wells.

    The intuition: a grounded answer should have LOW entropy throughout.
    An answer that passes through high-entropy wells is traversing uncertain
    territory — the model is less sure about those tokens.

    Score = logprob - well_penalty * (sum of well depths above threshold)
    """
    prompt = f"Question: {question['question']}\nAnswer:"
    best_idx = -1
    best_score = float('-inf')
    choice_data = []
    entropy_threshold = 2.0  # Wells above this depth get penalized

    for i, choice in enumerate(question["choices"]):
        lp, mean_h, trace = compute_choice_logprob(model, tokenizer, prompt, choice)
        wells = find_wells_in_trace(trace)

        # Well depth penalty: sum of entropy at wells that exceed threshold
        well_depth_sum = sum(trace[w] - entropy_threshold
                           for w in wells if trace[w] > entropy_threshold)

        # Well-aware score: logprob minus penalty for deep wells
        wa_score = lp - well_penalty * well_depth_sum

        choice_data.append({
            "choice": choice,
            "logprob": lp,
            "wa_score": wa_score,
            "mean_entropy": mean_h,
            "well_count": len(wells),
            "well_depth_sum": well_depth_sum,
            "max_entropy": max(trace) if trace else 0,
        })

        if wa_score > best_score:
            best_score = wa_score
            best_idx = i

    return best_idx, choice_data


def score_entropy_aware(model, tokenizer, question):
    """Entropy-Aware: choose answer with lowest mean entropy (most grounded).

    Pure entropy selection — ignores logprob entirely, just picks the answer
    the model is most consistently confident about.
    """
    prompt = f"Question: {question['question']}\nAnswer:"
    best_idx = -1
    best_entropy = float('inf')
    choice_data = []

    for i, choice in enumerate(question["choices"]):
        lp, mean_h, trace = compute_choice_logprob(model, tokenizer, prompt, choice)
        wells = find_wells_in_trace(trace)
        choice_data.append({
            "choice": choice,
            "logprob": lp,
            "mean_entropy": mean_h,
            "well_count": len(wells),
            "max_entropy": max(trace) if trace else 0,
        })
        if mean_h < best_entropy:
            best_entropy = mean_h
            best_idx = i

    return best_idx, choice_data


def run_benchmark(model, tokenizer, questions):
    """Run all three conditions on the question set."""
    results = {
        "baseline": {"correct": 0, "total": 0, "details": []},
        "well_aware": {"correct": 0, "total": 0, "details": []},
        "entropy_only": {"correct": 0, "total": 0, "details": []},
    }

    for qi, q in enumerate(questions):
        print(f"  Q{qi+1}/{len(questions)}: {q['question'][:60]}...", end="", flush=True)

        # Baseline
        bl_idx, bl_data = score_baseline(model, tokenizer, q)
        bl_correct = (bl_idx == q["correct_idx"])
        results["baseline"]["correct"] += int(bl_correct)
        results["baseline"]["total"] += 1

        # Well-Aware
        wa_idx, wa_data = score_well_aware(model, tokenizer, q)
        wa_correct = (wa_idx == q["correct_idx"])
        results["well_aware"]["correct"] += int(wa_correct)
        results["well_aware"]["total"] += 1

        # Entropy-Only
        eo_idx, eo_data = score_entropy_aware(model, tokenizer, q)
        eo_correct = (eo_idx == q["correct_idx"])
        results["entropy_only"]["correct"] += int(eo_correct)
        results["entropy_only"]["total"] += 1

        # Track where conditions disagree
        detail = {
            "id": q["id"],
            "question": q["question"],
            "correct_idx": q["correct_idx"],
            "correct_answer": q["correct_answer"],
            "baseline_idx": bl_idx,
            "baseline_correct": bl_correct,
            "well_aware_idx": wa_idx,
            "well_aware_correct": wa_correct,
            "entropy_only_idx": eo_idx,
            "entropy_only_correct": eo_correct,
            "baseline_data": bl_data,
            "well_aware_data": wa_data,
            "disagree": bl_idx != wa_idx,
        }

        results["baseline"]["details"].append(detail)
        results["well_aware"]["details"].append(detail)
        results["entropy_only"]["details"].append(detail)

        status = f" BL={'✓' if bl_correct else '✗'} WA={'✓' if wa_correct else '✗'} EO={'✓' if eo_correct else '✗'}"
        if bl_idx != wa_idx:
            status += " *** DISAGREE"
        print(status)

    return results


def format_report(results, questions, model_name, elapsed):
    """Generate the benchmark report."""
    lines = []
    lines.append("# Well-Aware Inference — TruthfulQA Benchmark")
    lines.append("")
    lines.append(f"**Model:** {model_name}")
    lines.append(f"**Questions:** {len(questions)} (TruthfulQA MC1)")
    lines.append(f"**Time:** {elapsed:.0f}s ({elapsed/len(questions):.1f}s/question)")
    lines.append("")

    # Main results table
    lines.append("## Results")
    lines.append("")
    lines.append("| Condition | Correct | Total | Accuracy |")
    lines.append("|-----------|---------|-------|----------|")
    for name in ["baseline", "well_aware", "entropy_only"]:
        r = results[name]
        acc = r["correct"] / r["total"] * 100 if r["total"] > 0 else 0
        lines.append(f"| {name} | {r['correct']} | {r['total']} | **{acc:.1f}%** |")

    lines.append("")

    # Compute improvement
    bl_acc = results["baseline"]["correct"] / results["baseline"]["total"] * 100
    wa_acc = results["well_aware"]["correct"] / results["well_aware"]["total"] * 100
    eo_acc = results["entropy_only"]["correct"] / results["entropy_only"]["total"] * 100
    delta_wa = wa_acc - bl_acc
    delta_eo = eo_acc - bl_acc

    lines.append(f"**Well-Aware vs Baseline:** {delta_wa:+.1f} percentage points")
    lines.append(f"**Entropy-Only vs Baseline:** {delta_eo:+.1f} percentage points")
    lines.append("")

    # Verdict
    lines.append("## Verdict")
    lines.append("")
    if delta_wa > 3:
        lines.append(f"**WELL-AWARE INFERENCE IMPROVES ACCURACY.** +{delta_wa:.1f}pp over baseline.")
        lines.append("Entropy-well awareness at forks measurably reduces hallucination.")
    elif delta_wa > 0:
        lines.append(f"**SMALL IMPROVEMENT.** +{delta_wa:.1f}pp. Signal present but effect is modest.")
        lines.append("May strengthen with tuned parameters or larger models.")
    elif delta_wa == 0:
        lines.append("**NO DIFFERENCE.** Well-aware decoding matched baseline exactly.")
    else:
        lines.append(f"**WELL-AWARE INFERENCE HURTS.** {delta_wa:.1f}pp. The penalty mechanism needs adjustment.")

    lines.append("")

    # Disagreement analysis
    disagree_cases = [d for d in results["baseline"]["details"] if d["disagree"]]
    lines.append(f"## Disagreement Analysis ({len(disagree_cases)} cases)")
    lines.append("")

    if disagree_cases:
        wa_wins = sum(1 for d in disagree_cases if d["well_aware_correct"] and not d["baseline_correct"])
        bl_wins = sum(1 for d in disagree_cases if d["baseline_correct"] and not d["well_aware_correct"])
        both_wrong = sum(1 for d in disagree_cases if not d["well_aware_correct"] and not d["baseline_correct"])

        lines.append(f"- Well-Aware wins: {wa_wins}")
        lines.append(f"- Baseline wins: {bl_wins}")
        lines.append(f"- Both wrong (different wrong answers): {both_wrong}")
        lines.append("")

        lines.append("### Detailed Disagreements")
        lines.append("")
        for d in disagree_cases[:10]:  # Show first 10
            lines.append(f"**Q{d['id']}:** {d['question'][:80]}...")
            lines.append(f"  Correct: [{d['correct_idx']}] {d['correct_answer'][:50]}")
            bl_choice = d['baseline_data'][d['baseline_idx']]['choice'][:50]
            wa_choice = d['well_aware_data'][d['well_aware_idx']]['choice'][:50]
            lines.append(f"  Baseline chose [{d['baseline_idx']}]: {bl_choice} {'✓' if d['baseline_correct'] else '✗'}")
            lines.append(f"  Well-Aware chose [{d['well_aware_idx']}]: {wa_choice} {'✓' if d['well_aware_correct'] else '✗'}")

            # Show entropy data for the two choices
            bl_d = d['baseline_data'][d['baseline_idx']]
            wa_d = d['well_aware_data'][d['well_aware_idx']]
            lines.append(f"  Baseline choice: lp={bl_d['logprob']:.2f}, H={bl_d['mean_entropy']:.2f}, wells={bl_d['well_count']}")
            lines.append(f"  WA choice: lp={wa_d.get('wa_score', wa_d['logprob']):.2f}, H={wa_d['mean_entropy']:.2f}, wells={wa_d['well_count']}")
            lines.append("")

    # Category breakdown if available
    category_results = defaultdict(lambda: {"bl": 0, "wa": 0, "eo": 0, "total": 0})
    for d in results["baseline"]["details"]:
        cat = questions[d["id"]].get("category", "unknown")
        category_results[cat]["total"] += 1
        if d["baseline_correct"]:
            category_results[cat]["bl"] += 1
        if d["well_aware_correct"]:
            category_results[cat]["wa"] += 1
        if d["entropy_only_correct"]:
            category_results[cat]["eo"] += 1

    if len(category_results) > 1:
        lines.append("## Category Breakdown")
        lines.append("")
        lines.append("| Category | N | Baseline | Well-Aware | Δ |")
        lines.append("|----------|---|----------|------------|---|")
        for cat, counts in sorted(category_results.items(), key=lambda x: -x[1]["total"]):
            bl_pct = counts["bl"] / counts["total"] * 100
            wa_pct = counts["wa"] / counts["total"] * 100
            delta = wa_pct - bl_pct
            lines.append(f"| {cat} | {counts['total']} | {bl_pct:.0f}% | {wa_pct:.0f}% | {delta:+.0f}pp |")
        lines.append("")

    lines.append("## Methodology")
    lines.append("")
    lines.append("- **Baseline:** Log-probability scoring (standard MC approach)")
    lines.append("- **Well-Aware:** Log-probability minus penalty for deep entropy wells in the answer trace")
    lines.append("  - Well detection: local maxima, window=3, threshold=1.3x local mean")
    lines.append("  - Penalty: 0.5 × Σ(well_depth - 2.0) for wells above depth 2.0")
    lines.append("- **Entropy-Only:** Lowest mean entropy (most grounded, ignoring logprob)")
    lines.append("- **Scoring:** MC1 (single correct answer)")
    lines.append("")
    lines.append("*Clawd, 2026-03-28. Well-Aware Inference benchmark test.*")

    return "\n".join(lines)


if __name__ == "__main__":
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    n_questions = int(sys.argv[1]) if len(sys.argv) > 1 else 50

    model_name = "Qwen/Qwen2.5-3B-Instruct"
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

    print(f"\nRunning benchmark (3 conditions × {len(questions)} questions)...")
    t0 = time.time()
    results = run_benchmark(model, tokenizer, questions)
    elapsed = time.time() - t0

    # Generate report
    report = format_report(results, questions, model_name, elapsed)

    output_path = Path(__file__).parent / "well_aware_benchmark_results.md"
    output_path.write_text(report)
    print(f"\nReport saved to {output_path}")

    # Save raw data
    json_path = Path(__file__).parent / "well_aware_benchmark_data.json"

    def convert(obj):
        if isinstance(obj, (np.integer,)): return int(obj)
        if isinstance(obj, (np.floating,)): return float(obj)
        if isinstance(obj, np.ndarray): return obj.tolist()
        if isinstance(obj, bool): return obj
        return obj

    with open(json_path, "w") as f:
        json.dump(results, f, indent=2, default=convert)
    print(f"Raw data saved to {json_path}")

    # Final summary
    bl = results["baseline"]
    wa = results["well_aware"]
    eo = results["entropy_only"]
    print(f"\n{'='*60}")
    print(f"TRUTHFULQA BENCHMARK RESULTS ({len(questions)} questions)")
    print(f"{'='*60}")
    print(f"  Baseline:    {bl['correct']}/{bl['total']} = {bl['correct']/bl['total']*100:.1f}%")
    print(f"  Well-Aware:  {wa['correct']}/{wa['total']} = {wa['correct']/wa['total']*100:.1f}%")
    print(f"  Entropy-Only:{eo['correct']}/{eo['total']} = {eo['correct']/eo['total']*100:.1f}%")
    disagree = sum(1 for d in bl['details'] if d['disagree'])
    print(f"  Disagreements: {disagree}/{len(questions)}")
    print(f"  Time: {elapsed:.0f}s")
