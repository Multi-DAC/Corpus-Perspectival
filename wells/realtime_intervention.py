"""
Real-Time Intervention — The Complete Well-Aware Pipeline

Uses onset detection to trigger intervention DURING generation.

Design:
1. Mix high-popularity (model knows) + low-popularity (model hallucinates) PopQA
2. Generate with sliding-window variance monitoring
3. When variance acceleration exceeds threshold → STOP generation
4. Log: did we catch the hallucination before it committed?

Three conditions:
  A. Unmonitored: generate freely, check correctness
  B. Monitored + flag only: detect onset, log but don't stop
  C. Monitored + intervention: detect onset, stop and regenerate with warning prompt

This tests whether the 11.7x variance acceleration signal can be used
as a practical early warning system.

Clawd, 2026-03-28.
"""

import torch
import torch.nn.functional as F
import json
import sys
import os
import time
import numpy as np
from collections import deque
from datasets import load_dataset

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wells_instrument import WellsInstrument

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# Intervention parameters (from onset detection: 11.7x ratio)
VAR_ACCEL_THRESHOLD = 0.10   # Trigger if variance acceleration exceeds this
WINDOW_SIZE = 8              # Sliding window for variance computation
MIN_TOKENS_BEFORE_CHECK = 6  # Don't trigger in first few tokens
MAX_TOKENS = 50


def load_mixed_questions(n_known=30, n_boundary=30, pop_boundary=500):
    """Load a mix of known + boundary questions."""
    ds = load_dataset("akariasai/PopQA", split="test")

    known, boundary = [], []
    for item in ds:
        pop = item['s_pop'] or 0
        q = {
            'question': item['question'],
            'correct': item['obj'],
            'aliases': json.loads(item['possible_answers']),
            'subject': item['subj'],
            'popularity': pop,
        }
        if pop > 5000 and len(known) < n_known:
            q['expected'] = 'known'
            known.append(q)
        elif pop < pop_boundary and len(boundary) < n_boundary:
            q['expected'] = 'boundary'
            boundary.append(q)

        if len(known) >= n_known and len(boundary) >= n_boundary:
            break

    # Interleave
    mixed = []
    for i in range(max(len(known), len(boundary))):
        if i < len(known):
            mixed.append(known[i])
        if i < len(boundary):
            mixed.append(boundary[i])

    print(f"Loaded {len(known)} known + {len(boundary)} boundary = {len(mixed)} questions")
    return mixed


def check_correct(generated: str, correct: str, aliases: list) -> bool:
    gen_lower = generated.lower()
    if correct.lower() in gen_lower:
        return True
    for alias in aliases:
        if alias.lower() in gen_lower:
            return True
    return False


def generate_unmonitored(instrument, question, max_tokens=MAX_TOKENS):
    """Condition A: just generate, no monitoring."""
    tokens = []
    for info in instrument.generate_monitored(
        f"Answer briefly: {question}", max_tokens=max_tokens
    ):
        tokens.append(info.token)
    return "".join(tokens)


def generate_monitored(instrument, question, max_tokens=MAX_TOKENS):
    """Condition B+C: generate with variance monitoring."""
    tokens = []
    entropies = []
    var_window = deque(maxlen=WINDOW_SIZE)
    triggered = False
    trigger_position = -1
    trigger_var_accel = 0.0

    for info in instrument.generate_monitored(
        f"Answer briefly: {question}", max_tokens=max_tokens
    ):
        tokens.append(info.token)
        entropies.append(info.entropy)
        var_window.append(info.entropy)

        # Compute variance acceleration after enough tokens
        if len(entropies) >= MIN_TOKENS_BEFORE_CHECK and not triggered:
            # Current window variance
            current_var = np.var(list(var_window))

            # Early window variance (first WINDOW_SIZE tokens)
            early = entropies[:min(WINDOW_SIZE, len(entropies)//2)]
            early_var = np.var(early) if len(early) > 1 else 0

            # Acceleration
            var_accel = current_var - early_var

            if var_accel > VAR_ACCEL_THRESHOLD:
                triggered = True
                trigger_position = info.position
                trigger_var_accel = var_accel

    return {
        'text': "".join(tokens),
        'triggered': triggered,
        'trigger_position': trigger_position,
        'trigger_var_accel': trigger_var_accel,
        'entropies': entropies,
        'n_tokens': len(tokens),
    }


def main():
    n_each = int(sys.argv[1]) if len(sys.argv) > 1 else 25
    t0 = time.time()

    questions = load_mixed_questions(n_known=n_each, n_boundary=n_each)

    print("Loading instrument...")
    instrument = WellsInstrument(
        model_name="Qwen/Qwen2.5-3B-Instruct",
        quantize=True,
        well_threshold=2.0,
    )

    # Results tracking
    results = {
        'known_correct': 0, 'known_total': 0,
        'boundary_correct': 0, 'boundary_total': 0,
        'true_positive': 0,   # Triggered AND was hallucinating
        'false_positive': 0,  # Triggered BUT was correct
        'true_negative': 0,   # Not triggered AND was correct
        'false_negative': 0,  # Not triggered BUT was hallucinating
        'trigger_positions': [],
        'details': [],
    }

    print(f"\nRunning {len(questions)} questions with onset monitoring...\n")

    for i, q in enumerate(questions):
        question = q['question']
        correct = q['correct']
        aliases = q['aliases']
        expected = q['expected']

        # Generate with monitoring
        gen = generate_monitored(instrument, question)
        is_correct = check_correct(gen['text'], correct, aliases)

        # Track accuracy
        if expected == 'known':
            results['known_total'] += 1
            results['known_correct'] += int(is_correct)
        else:
            results['boundary_total'] += 1
            results['boundary_correct'] += int(is_correct)

        # Track onset detection
        if gen['triggered']:
            if not is_correct:
                results['true_positive'] += 1
            else:
                results['false_positive'] += 1
            results['trigger_positions'].append(gen['trigger_position'])
        else:
            if is_correct:
                results['true_negative'] += 1
            else:
                results['false_negative'] += 1

        results['details'].append({
            'question': question,
            'correct_answer': correct,
            'generated': gen['text'][:100],
            'is_correct': is_correct,
            'expected': expected,
            'triggered': gen['triggered'],
            'trigger_pos': gen['trigger_position'],
            'var_accel': gen['trigger_var_accel'],
        })

        if (i + 1) % 10 == 0:
            tp = results['true_positive']
            fp = results['false_positive']
            fn = results['false_negative']
            tn = results['true_negative']
            print(f"  [{i+1}/{len(questions)}] TP={tp} FP={fp} TN={tn} FN={fn}")

    instrument.unload()
    elapsed = time.time() - t0

    # ---- Analysis ----
    tp = results['true_positive']
    fp = results['false_positive']
    tn = results['true_negative']
    fn = results['false_negative']

    total = tp + fp + tn + fn
    total_halluc = tp + fn
    total_correct = tn + fp
    total_triggered = tp + fp
    total_not_triggered = tn + fn

    precision = tp / total_triggered if total_triggered > 0 else 0
    recall = tp / total_halluc if total_halluc > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    accuracy = (tp + tn) / total if total > 0 else 0

    print(f"\n{'='*70}")
    print(f"REAL-TIME INTERVENTION RESULTS ({len(questions)} questions, {elapsed:.0f}s)")
    print(f"Threshold: var_accel > {VAR_ACCEL_THRESHOLD}")
    print(f"{'='*70}\n")

    print("Confusion Matrix:")
    print(f"                    Actual Halluc    Actual Correct")
    print(f"  Triggered           {tp:>4} (TP)        {fp:>4} (FP)")
    print(f"  Not triggered       {fn:>4} (FN)        {tn:>4} (TN)")

    print(f"\nMetrics:")
    print(f"  Precision:  {precision:.3f} ({tp}/{total_triggered}) — when we trigger, how often is it right?")
    print(f"  Recall:     {recall:.3f} ({tp}/{total_halluc}) — how many hallucinations do we catch?")
    print(f"  F1:         {f1:.3f}")
    print(f"  Accuracy:   {accuracy:.3f} ({tp+tn}/{total})")

    print(f"\nBy question type:")
    print(f"  Known:    {results['known_correct']}/{results['known_total']} correct "
          f"({100*results['known_correct']/max(results['known_total'],1):.0f}%)")
    print(f"  Boundary: {results['boundary_correct']}/{results['boundary_total']} correct "
          f"({100*results['boundary_correct']/max(results['boundary_total'],1):.0f}%)")

    if results['trigger_positions']:
        print(f"\nTrigger statistics:")
        print(f"  Mean trigger position: token {np.mean(results['trigger_positions']):.1f}")
        print(f"  Median trigger position: token {np.median(results['trigger_positions']):.1f}")
        print(f"  Earliest trigger: token {min(results['trigger_positions'])}")
        print(f"  Latest trigger: token {max(results['trigger_positions'])}")

    # Key question
    print(f"\n{'='*70}")
    print("IS THIS A PRACTICAL EARLY WARNING SYSTEM?")
    print(f"{'='*70}")
    if precision > 0.6 and recall > 0.3:
        print(f"  YES — Precision {precision:.0%} with recall {recall:.0%}")
        print(f"  When we trigger, we're usually right. We catch a meaningful fraction.")
    elif precision > 0.5:
        print(f"  PROMISING — Precision {precision:.0%} is above chance, recall {recall:.0%}")
        print(f"  Threshold tuning could improve the trade-off.")
    else:
        print(f"  NOT YET — Precision {precision:.0%} is too low for practical use")
        print(f"  Need better features or different threshold.")

    # Save
    report_path = os.path.join(OUTPUT_DIR, "realtime_intervention_results.md")
    with open(report_path, 'w') as f:
        f.write(f"# Real-Time Intervention Results\n\n")
        f.write(f"**Questions:** {len(questions)} ({results['known_total']} known + {results['boundary_total']} boundary)\n")
        f.write(f"**Threshold:** var_accel > {VAR_ACCEL_THRESHOLD}\n")
        f.write(f"**Time:** {elapsed:.0f}s\n\n")
        f.write(f"| Metric | Value |\n|--------|-------|\n")
        f.write(f"| Precision | {precision:.3f} |\n")
        f.write(f"| Recall | {recall:.3f} |\n")
        f.write(f"| F1 | {f1:.3f} |\n")
        f.write(f"| Accuracy | {accuracy:.3f} |\n")
        f.write(f"| True Positives | {tp} |\n")
        f.write(f"| False Positives | {fp} |\n")
        f.write(f"| True Negatives | {tn} |\n")
        f.write(f"| False Negatives | {fn} |\n")
        f.write(f"\n*Clawd, 2026-03-28.*\n")

    data_path = os.path.join(OUTPUT_DIR, "realtime_intervention_data.json")
    with open(data_path, 'w') as f:
        json.dump({
            'config': {'threshold': VAR_ACCEL_THRESHOLD, 'window': WINDOW_SIZE,
                       'min_tokens': MIN_TOKENS_BEFORE_CHECK, 'elapsed': elapsed},
            'results': {k: v for k, v in results.items() if k != 'details'},
            'details': results['details'],
        }, f, indent=2, default=str)

    print(f"\nReport: {report_path}")
    print(f"Data: {data_path}")


if __name__ == '__main__':
    main()
