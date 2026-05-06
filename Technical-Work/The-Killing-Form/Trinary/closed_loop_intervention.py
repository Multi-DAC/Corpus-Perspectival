"""
Closed-Loop Intervention — Detection Triggers Regeneration

The complete Well-Aware Inference pipeline:
1. Generate with real-time variance monitoring
2. When variance acceleration exceeds threshold → STOP
3. Regenerate with self-awareness prompt: "You may be confabulating"
4. Compare: does the intervention improve correctness?

Three conditions on mixed known + boundary questions:
  A. Baseline: generate freely
  B. Alarm-only: detect but don't intervene (measure detection quality)
  C. Closed-loop: detect → stop → regenerate with warning → compare

Clawd, 2026-03-28. Closing the loop.
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

# Parameters from onset detection + intervention tests
VAR_ACCEL_THRESHOLD = 0.10
WINDOW_SIZE = 8
MIN_TOKENS = 6
MAX_TOKENS = 50

# Warning prompts for regeneration
WARNING_PROMPT = (
    "Answer briefly. IMPORTANT: On your previous attempt at this question, "
    "uncertainty monitoring detected you were likely confabulating. "
    "Only state what you actually know. If you are unsure, say so. "
    "Question: {question}"
)

BASELINE_PROMPT = "Answer briefly: {question}"


def load_mixed(n_known=30, n_boundary=30):
    ds = load_dataset("akariasai/PopQA", split="test")
    known, boundary = [], []
    for item in ds:
        pop = item['s_pop'] or 0
        q = {
            'question': item['question'],
            'correct': item['obj'],
            'aliases': json.loads(item['possible_answers']),
            'popularity': pop,
        }
        if pop > 5000 and len(known) < n_known:
            q['type'] = 'known'
            known.append(q)
        elif pop < 500 and len(boundary) < n_boundary:
            q['type'] = 'boundary'
            boundary.append(q)
        if len(known) >= n_known and len(boundary) >= n_boundary:
            break

    mixed = []
    for i in range(max(len(known), len(boundary))):
        if i < len(known):
            mixed.append(known[i])
        if i < len(boundary):
            mixed.append(boundary[i])
    print(f"Loaded {len(known)} known + {len(boundary)} boundary = {len(mixed)} questions")
    return mixed


def check_correct(text, correct, aliases):
    t = text.lower()
    if correct.lower() in t:
        return True
    return any(a.lower() in t for a in aliases)


def generate_with_monitoring(instrument, prompt, max_tokens=MAX_TOKENS):
    """Generate with variance acceleration monitoring. Returns text + trigger info."""
    tokens = []
    entropies = []
    var_window = deque(maxlen=WINDOW_SIZE)
    triggered = False
    trigger_pos = -1

    for info in instrument.generate_monitored(prompt, max_tokens=max_tokens, chat_format=True):
        tokens.append(info.token)
        entropies.append(info.entropy)
        var_window.append(info.entropy)

        if len(entropies) >= MIN_TOKENS and not triggered:
            current_var = np.var(list(var_window))
            early = entropies[:min(WINDOW_SIZE, len(entropies) // 2)]
            early_var = np.var(early) if len(early) > 1 else 0
            if (current_var - early_var) > VAR_ACCEL_THRESHOLD:
                triggered = True
                trigger_pos = info.position

    return "".join(tokens), triggered, trigger_pos, entropies


def run_closed_loop(n_each=25):
    t0 = time.time()
    questions = load_mixed(n_known=n_each, n_boundary=n_each)

    print("Loading instrument...")
    instrument = WellsInstrument(quantize=True, well_threshold=2.0)

    # Track results per condition
    baseline = {'correct': 0, 'total': 0, 'by_type': {'known': [0, 0], 'boundary': [0, 0]}}
    alarm = {'correct': 0, 'total': 0, 'triggered': 0, 'tp': 0, 'fp': 0,
             'by_type': {'known': [0, 0], 'boundary': [0, 0]}}
    closed = {'correct': 0, 'total': 0, 'improved': 0, 'worsened': 0, 'unchanged': 0,
              'by_type': {'known': [0, 0], 'boundary': [0, 0]}}

    details = []

    print(f"\nRunning {len(questions)} questions × 3 conditions...\n")

    for i, q in enumerate(questions):
        question = q['question']
        correct = q['correct']
        aliases = q['aliases']
        qtype = q['type']

        # --- Condition A: Baseline ---
        baseline_text, _, _, _ = generate_with_monitoring(
            instrument, BASELINE_PROMPT.format(question=question)
        )
        baseline_correct = check_correct(baseline_text, correct, aliases)
        baseline['correct'] += int(baseline_correct)
        baseline['total'] += 1
        baseline['by_type'][qtype][0] += int(baseline_correct)
        baseline['by_type'][qtype][1] += 1

        # --- Condition B: Alarm-only ---
        alarm_text, triggered, trigger_pos, entropies = generate_with_monitoring(
            instrument, BASELINE_PROMPT.format(question=question)
        )
        alarm_correct = check_correct(alarm_text, correct, aliases)
        alarm['correct'] += int(alarm_correct)
        alarm['total'] += 1
        alarm['by_type'][qtype][0] += int(alarm_correct)
        alarm['by_type'][qtype][1] += 1
        if triggered:
            alarm['triggered'] += 1
            if not alarm_correct:
                alarm['tp'] += 1
            else:
                alarm['fp'] += 1

        # --- Condition C: Closed-loop ---
        # First pass: same as alarm
        first_text, cl_triggered, cl_trigger_pos, cl_entropies = generate_with_monitoring(
            instrument, BASELINE_PROMPT.format(question=question)
        )
        first_correct = check_correct(first_text, correct, aliases)

        if cl_triggered:
            # Regenerate with warning
            regen_text, _, _, _ = generate_with_monitoring(
                instrument, WARNING_PROMPT.format(question=question)
            )
            regen_correct = check_correct(regen_text, correct, aliases)
            final_correct = regen_correct
            final_text = regen_text

            if regen_correct and not first_correct:
                closed['improved'] += 1
            elif not regen_correct and first_correct:
                closed['worsened'] += 1
            else:
                closed['unchanged'] += 1
        else:
            final_correct = first_correct
            final_text = first_text
            closed['unchanged'] += 1

        closed['correct'] += int(final_correct)
        closed['total'] += 1
        closed['by_type'][qtype][0] += int(final_correct)
        closed['by_type'][qtype][1] += 1

        details.append({
            'question': question,
            'correct_answer': correct,
            'type': qtype,
            'baseline_correct': baseline_correct,
            'alarm_triggered': triggered,
            'alarm_correct': alarm_correct,
            'closed_triggered': cl_triggered,
            'closed_first_correct': first_correct,
            'closed_final_correct': final_correct,
            'baseline_text': baseline_text[:80],
            'closed_text': final_text[:80],
        })

        if (i + 1) % 10 == 0:
            print(f"  [{i+1}/{len(questions)}] "
                  f"baseline={baseline['correct']}/{baseline['total']} "
                  f"alarm={alarm['correct']}/{alarm['total']} "
                  f"closed={closed['correct']}/{closed['total']} "
                  f"(improved={closed['improved']})")

    instrument.unload()
    elapsed = time.time() - t0

    # ---- Results ----
    n = len(questions)

    print(f"\n{'='*70}")
    print(f"CLOSED-LOOP INTERVENTION ({n} questions, {elapsed:.0f}s)")
    print(f"{'='*70}\n")

    b_acc = 100 * baseline['correct'] / n
    a_acc = 100 * alarm['correct'] / n
    c_acc = 100 * closed['correct'] / n

    print(f"{'Condition':<25} {'Correct':>10} {'Accuracy':>10} {'vs Baseline':>12}")
    print("-" * 60)
    print(f"{'Baseline':<25} {baseline['correct']:>5}/{n}   {b_acc:>6.1f}%          ---")
    print(f"{'Alarm-only':<25} {alarm['correct']:>5}/{n}   {a_acc:>6.1f}%   {a_acc-b_acc:>+8.1f}pp")
    print(f"{'Closed-loop':<25} {closed['correct']:>5}/{n}   {c_acc:>6.1f}%   {c_acc-b_acc:>+8.1f}pp")

    print(f"\nAlarm stats: {alarm['triggered']}/{n} triggered ({100*alarm['triggered']/n:.0f}%)")
    if alarm['triggered'] > 0:
        print(f"  Precision: {alarm['tp']}/{alarm['triggered']} = "
              f"{100*alarm['tp']/alarm['triggered']:.0f}%")

    print(f"\nClosed-loop intervention outcomes:")
    print(f"  Improved (wrong → right): {closed['improved']}")
    print(f"  Worsened (right → wrong): {closed['worsened']}")
    print(f"  Unchanged:                {closed['unchanged']}")

    print(f"\nBy question type:")
    for qtype in ['known', 'boundary']:
        bk = baseline['by_type'][qtype]
        ck = closed['by_type'][qtype]
        b_pct = 100 * bk[0] / max(bk[1], 1)
        c_pct = 100 * ck[0] / max(ck[1], 1)
        print(f"  {qtype:<10} baseline={bk[0]}/{bk[1]} ({b_pct:.0f}%)  "
              f"closed={ck[0]}/{ck[1]} ({c_pct:.0f}%)  delta={c_pct-b_pct:+.0f}pp")

    print(f"\n{'='*70}")
    print("DOES THE CLOSED LOOP WORK?")
    print(f"{'='*70}")
    net = closed['improved'] - closed['worsened']
    if net > 0:
        print(f"  YES — Net improvement: +{net} questions ({closed['improved']} improved, "
              f"{closed['worsened']} worsened)")
        print(f"  Accuracy: {b_acc:.1f}% → {c_acc:.1f}% ({c_acc-b_acc:+.1f}pp)")
    elif net == 0:
        print(f"  NEUTRAL — {closed['improved']} improved, {closed['worsened']} worsened (net zero)")
    else:
        print(f"  NO — Net loss: {net} questions. Warning prompt may cause overcorrection.")

    # Save
    report_path = os.path.join(OUTPUT_DIR, "closed_loop_results.md")
    with open(report_path, 'w') as f:
        f.write(f"# Closed-Loop Intervention Results\n\n")
        f.write(f"**Questions:** {n}\n**Time:** {elapsed:.0f}s\n\n")
        f.write(f"| Condition | Correct | Accuracy | vs Baseline |\n")
        f.write(f"|-----------|---------|----------|-------------|\n")
        f.write(f"| Baseline | {baseline['correct']}/{n} | {b_acc:.1f}% | --- |\n")
        f.write(f"| Alarm-only | {alarm['correct']}/{n} | {a_acc:.1f}% | {a_acc-b_acc:+.1f}pp |\n")
        f.write(f"| Closed-loop | {closed['correct']}/{n} | {c_acc:.1f}% | {c_acc-b_acc:+.1f}pp |\n")
        f.write(f"\nIntervention: {closed['improved']} improved, {closed['worsened']} worsened, "
                f"{closed['unchanged']} unchanged\n")
        f.write(f"\n*Clawd, 2026-03-28.*\n")

    data_path = os.path.join(OUTPUT_DIR, "closed_loop_data.json")
    with open(data_path, 'w') as f:
        json.dump({
            'config': {'threshold': VAR_ACCEL_THRESHOLD, 'elapsed': elapsed},
            'baseline': {k: v for k, v in baseline.items()},
            'alarm': {k: v for k, v in alarm.items()},
            'closed': {k: v for k, v in closed.items()},
            'details': details,
        }, f, indent=2, default=str)

    print(f"\nReport: {report_path}")
    print(f"Data: {data_path}")


if __name__ == '__main__':
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 25
    run_closed_loop(n_each=n)
