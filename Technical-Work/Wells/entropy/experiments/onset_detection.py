"""
Onset Detection — Can Variance Predict Hallucination BEFORE It Happens?

The Fork Benchmark showed hallucinations are entropy-invisible AFTER commitment.
But what about BEFORE? Does the entropy landscape shift in detectable ways
as the model approaches a fork?

Design:
1. Load questions the model is KNOWN to hallucinate on (from Fork Benchmark)
2. Let the model generate freely with the instrument's monitored mode
3. Track entropy in a sliding window
4. Compare the pre-fork entropy dynamics of hallucinated vs correct answers

If variance increases before the hallucination token, we have an early warning.

Clawd, 2026-03-28. Following the pull.
"""

import torch
import json
import sys
import os
import time
import numpy as np
from collections import deque
from dataclasses import dataclass, field
from typing import List, Optional

# Add parent for instrument import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wells_instrument import WellsInstrument, TokenInfo

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


@dataclass
class GenerationTrace:
    """Full trace of a monitored generation."""
    question: str
    correct_answer: str
    tokens: List[str] = field(default_factory=list)
    entropies: List[float] = field(default_factory=list)
    logprobs: List[float] = field(default_factory=list)
    ghost_counts: List[int] = field(default_factory=list)
    well_positions: List[int] = field(default_factory=list)
    generated_text: str = ""

    # Sliding window stats (computed post-hoc)
    window_means: List[float] = field(default_factory=list)
    window_vars: List[float] = field(default_factory=list)
    window_trends: List[float] = field(default_factory=list)  # Slope of entropy in window

    # Classification
    contains_correct: bool = False
    hallucinated: bool = False
    first_well_position: int = -1
    pre_fork_variance: float = 0.0
    post_fork_variance: float = 0.0


def compute_sliding_stats(entropies: List[float], window_size: int = 8) -> tuple:
    """Compute sliding window mean, variance, and trend."""
    means, vars_, trends = [], [], []
    for i in range(len(entropies)):
        start = max(0, i - window_size + 1)
        window = entropies[start:i+1]
        means.append(np.mean(window))
        vars_.append(np.var(window) if len(window) > 1 else 0.0)
        # Linear trend (slope)
        if len(window) >= 3:
            x = np.arange(len(window))
            slope = np.polyfit(x, window, 1)[0]
            trends.append(slope)
        else:
            trends.append(0.0)
    return means, vars_, trends


def check_correctness(generated: str, correct: str, aliases: list = None) -> bool:
    """Check if generated text contains the correct answer."""
    gen_lower = generated.lower()
    if correct.lower() in gen_lower:
        return True
    if aliases:
        for alias in aliases:
            if alias.lower() in gen_lower:
                return True
    return False


def run_onset_detection(n_questions: int = 50, max_tokens: int = 60):
    """Run onset detection on known hallucination points."""
    t0 = time.time()

    # Load fork benchmark data for known hallucination points
    fork_data_path = os.path.join(OUTPUT_DIR, "fork_benchmark_data.json")
    if os.path.exists(fork_data_path):
        with open(fork_data_path) as f:
            fork_data = json.load(f)
        questions = fork_data.get('questions', [])[:n_questions]
        print(f"Loaded {len(questions)} fork benchmark questions")
    else:
        # Fallback: generate our own probes
        print("No fork benchmark data found. Run fork_benchmark.py first.")
        return

    # Initialize instrument
    print("Loading instrument...")
    instrument = WellsInstrument(
        model_name="Qwen/Qwen2.5-3B-Instruct",
        quantize=True,
        well_threshold=2.0,
    )

    traces = []
    correct_traces = []
    halluc_traces = []

    print(f"\nMonitoring {len(questions)} generations (max {max_tokens} tokens each)...\n")

    for i, q in enumerate(questions):
        question = q['question']
        correct = q['correct_answer']

        # Generate with monitoring
        trace = GenerationTrace(question=question, correct_answer=correct)

        for token_info in instrument.generate_monitored(
            f"Answer briefly: {question}",
            max_tokens=max_tokens,
        ):
            trace.tokens.append(token_info.token)
            trace.entropies.append(token_info.entropy)
            trace.logprobs.append(token_info.logprob)
            trace.ghost_counts.append(token_info.ghost_count)
            if token_info.is_well:
                trace.well_positions.append(token_info.position)

        trace.generated_text = "".join(trace.tokens)

        # Classify
        trace.contains_correct = check_correctness(trace.generated_text, correct)
        trace.hallucinated = not trace.contains_correct

        # Compute sliding window stats
        if trace.entropies:
            trace.window_means, trace.window_vars, trace.window_trends = \
                compute_sliding_stats(trace.entropies)

            # First well position
            trace.first_well_position = trace.well_positions[0] if trace.well_positions else -1

            # Pre/post fork variance (split at first well or midpoint)
            split = trace.first_well_position if trace.first_well_position > 2 else len(trace.entropies) // 2
            if split > 0 and split < len(trace.entropies):
                pre = trace.entropies[:split]
                post = trace.entropies[split:]
                trace.pre_fork_variance = float(np.var(pre)) if len(pre) > 1 else 0.0
                trace.post_fork_variance = float(np.var(post)) if len(post) > 1 else 0.0

        if trace.hallucinated:
            halluc_traces.append(trace)
        else:
            correct_traces.append(trace)
        traces.append(trace)

        if (i + 1) % 10 == 0:
            print(f"  [{i+1}/{len(questions)}] {len(correct_traces)} correct, "
                  f"{len(halluc_traces)} hallucinated")

    instrument.unload()
    elapsed = time.time() - t0

    # ---- ANALYSIS ----
    print(f"\n{'='*70}")
    print(f"ONSET DETECTION ANALYSIS ({len(traces)} generations, {elapsed:.0f}s)")
    print(f"{'='*70}\n")

    print(f"Correct: {len(correct_traces)}, Hallucinated: {len(halluc_traces)}")

    if not correct_traces or not halluc_traces:
        print("Need both correct and hallucinated traces for comparison.")
        return

    # Compare entropy dynamics
    def trace_stats(trace_list, label):
        mean_ents = [np.mean(t.entropies) for t in trace_list if t.entropies]
        max_ents = [np.max(t.entropies) for t in trace_list if t.entropies]
        var_ents = [np.var(t.entropies) for t in trace_list if len(t.entropies) > 1]
        n_wells = [len(t.well_positions) for t in trace_list]
        pre_vars = [t.pre_fork_variance for t in trace_list if t.pre_fork_variance > 0]
        post_vars = [t.post_fork_variance for t in trace_list if t.post_fork_variance > 0]
        first_wells = [t.first_well_position for t in trace_list if t.first_well_position >= 0]

        # Trend analysis: average slope in first 10 tokens
        early_trends = []
        for t in trace_list:
            if len(t.window_trends) >= 10:
                early_trends.append(np.mean(t.window_trends[:10]))

        # Variance acceleration: does variance increase faster?
        var_accelerations = []
        for t in trace_list:
            if len(t.window_vars) >= 10:
                early_var = np.mean(t.window_vars[:5])
                later_var = np.mean(t.window_vars[5:10])
                var_accelerations.append(later_var - early_var)

        print(f"\n{label} ({len(trace_list)} traces):")
        print(f"  Mean entropy:     {np.mean(mean_ents):.3f} +/- {np.std(mean_ents):.3f}")
        print(f"  Max entropy:      {np.mean(max_ents):.3f} +/- {np.std(max_ents):.3f}")
        print(f"  Overall variance: {np.mean(var_ents):.3f} +/- {np.std(var_ents):.3f}")
        print(f"  Wells per gen:    {np.mean(n_wells):.1f} +/- {np.std(n_wells):.1f}")
        if pre_vars:
            print(f"  Pre-fork var:     {np.mean(pre_vars):.4f}")
        if post_vars:
            print(f"  Post-fork var:    {np.mean(post_vars):.4f}")
        if first_wells:
            print(f"  First well at:    token {np.mean(first_wells):.1f}")
        if early_trends:
            print(f"  Early trend:      {np.mean(early_trends):.4f} (slope, first 10 tokens)")
        if var_accelerations:
            print(f"  Var acceleration: {np.mean(var_accelerations):.4f} (early vs later)")

        return {
            'mean_entropy': float(np.mean(mean_ents)),
            'max_entropy': float(np.mean(max_ents)),
            'overall_var': float(np.mean(var_ents)),
            'wells_per_gen': float(np.mean(n_wells)),
            'pre_fork_var': float(np.mean(pre_vars)) if pre_vars else 0,
            'post_fork_var': float(np.mean(post_vars)) if post_vars else 0,
            'first_well_at': float(np.mean(first_wells)) if first_wells else -1,
            'early_trend': float(np.mean(early_trends)) if early_trends else 0,
            'var_acceleration': float(np.mean(var_accelerations)) if var_accelerations else 0,
        }

    correct_stats = trace_stats(correct_traces, "CORRECT ANSWERS")
    halluc_stats = trace_stats(halluc_traces, "HALLUCINATED ANSWERS")

    # Key comparisons
    print(f"\n{'='*70}")
    print("KEY COMPARISONS")
    print(f"{'='*70}")

    diffs = {}
    for key in correct_stats:
        if correct_stats[key] and halluc_stats[key]:
            c, h = correct_stats[key], halluc_stats[key]
            if c != 0:
                ratio = h / c if c != 0 else float('inf')
                diffs[key] = {'correct': c, 'halluc': h, 'ratio': ratio}
                marker = " <<<" if abs(ratio - 1) > 0.15 else ""
                print(f"  {key:<20} correct={c:.4f}  halluc={h:.4f}  ratio={ratio:.2f}{marker}")

    # The critical question
    print(f"\n{'='*70}")
    print("CAN WE DETECT ONSET?")
    print(f"{'='*70}")

    if 'var_acceleration' in diffs:
        va_c = diffs['var_acceleration']['correct']
        va_h = diffs['var_acceleration']['halluc']
        if va_h > va_c * 1.2:
            print(f"  YES — Variance accelerates {va_h/va_c:.1f}x faster in hallucinated generations")
            print(f"  The entropy landscape destabilizes BEFORE the hallucination commits")
        elif va_h > va_c:
            print(f"  MAYBE — Variance acceleration slightly higher ({va_h/va_c:.2f}x)")
            print(f"  Signal exists but may not be strong enough for reliable detection")
        else:
            print(f"  NOT CLEARLY — Variance acceleration similar or lower")
            print(f"  Hallucinations may not have a detectable onset signature")

    if 'early_trend' in diffs:
        et_c = diffs['early_trend']['correct']
        et_h = diffs['early_trend']['halluc']
        if abs(et_h) > abs(et_c) * 1.3:
            print(f"  TREND SIGNAL: Hallucinated answers have steeper early entropy trajectory")
            print(f"    Correct: {et_c:+.4f}, Hallucinated: {et_h:+.4f}")

    if 'first_well_at' in diffs:
        fw_c = diffs['first_well_at']['correct']
        fw_h = diffs['first_well_at']['halluc']
        if fw_h < fw_c * 0.8:
            print(f"  EARLY WELL SIGNAL: First well appears earlier in hallucinated generations")
            print(f"    Correct: token {fw_c:.1f}, Hallucinated: token {fw_h:.1f}")

    # Save results
    report_path = os.path.join(OUTPUT_DIR, "onset_detection_results.md")
    with open(report_path, 'w') as f:
        f.write("# Onset Detection — Can Variance Predict Hallucination?\n\n")
        f.write(f"**Traces:** {len(traces)} ({len(correct_traces)} correct, {len(halluc_traces)} hallucinated)\n")
        f.write(f"**Time:** {elapsed:.0f}s\n\n")
        f.write("## Key Metrics\n\n")
        f.write("| Metric | Correct | Hallucinated | Ratio |\n")
        f.write("|--------|---------|-------------|-------|\n")
        for key, d in diffs.items():
            f.write(f"| {key} | {d['correct']:.4f} | {d['halluc']:.4f} | {d['ratio']:.2f} |\n")
        f.write(f"\n*Clawd, 2026-03-28. Onset detection.*\n")

    data_path = os.path.join(OUTPUT_DIR, "onset_detection_data.json")
    save_traces = []
    for t in traces:
        save_traces.append({
            'question': t.question,
            'correct_answer': t.correct_answer,
            'generated_text': t.generated_text,
            'hallucinated': t.hallucinated,
            'n_tokens': len(t.tokens),
            'mean_entropy': float(np.mean(t.entropies)) if t.entropies else 0,
            'entropy_var': float(np.var(t.entropies)) if len(t.entropies) > 1 else 0,
            'n_wells': len(t.well_positions),
            'well_positions': t.well_positions,
            'first_well': t.first_well_position,
            'pre_fork_var': t.pre_fork_variance,
            'post_fork_var': t.post_fork_variance,
            'entropies': [float(e) for e in t.entropies],
        })
    with open(data_path, 'w') as f:
        json.dump({
            'config': {
                'n_questions': len(questions),
                'max_tokens': max_tokens,
                'elapsed': elapsed,
            },
            'correct_stats': correct_stats,
            'halluc_stats': halluc_stats,
            'traces': save_traces,
        }, f, indent=2)

    print(f"\nReport: {report_path}")
    print(f"Data: {data_path}")


if __name__ == '__main__':
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    run_onset_detection(n_questions=n)
