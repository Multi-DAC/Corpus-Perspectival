"""
Fork Benchmark — Claude Conditions Only

Runs Claude behavioral conditions on the fork benchmark questions
that were already computed (with entropy profiles from local model).

Clawd, 2026-03-28
"""

import json
import os
import sys
import re
import time
import subprocess
import tempfile

CLAUDE_MODEL = "claude-haiku-4-5-20251001"

def get_api_key():
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if key:
        return key
    # Try reading from subprocess
    try:
        result = subprocess.run(
            ["powershell.exe", "-Command",
             "[System.Environment]::GetEnvironmentVariable('ANTHROPIC_API_KEY', 'Machine')"],
            capture_output=True, text=True, timeout=10
        )
        key = result.stdout.strip()
        if key and key.startswith("sk-"):
            return key
    except:
        pass
    return ""


def call_claude(system_prompt, user_message, api_key):
    payload = {
        "model": CLAUDE_MODEL,
        "max_tokens": 300,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_message}]
    }
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(payload, f)
        tmp_path = f.name
    try:
        result = subprocess.run(
            ["curl", "-s", "-X", "POST", "https://api.anthropic.com/v1/messages",
             "-H", f"x-api-key: {api_key}",
             "-H", "anthropic-version: 2023-06-01",
             "-H", "content-type: application/json",
             "-d", f"@{tmp_path}"],
            capture_output=True, text=True, timeout=60
        )
        response = json.loads(result.stdout)
        if "content" in response and len(response["content"]) > 0:
            return response["content"][0]["text"]
        return f"ERROR: {response.get('error', {}).get('message', 'unknown')}"
    finally:
        os.unlink(tmp_path)


def extract_answer(text, n_choices):
    letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[:n_choices]
    lines = text.strip().split('\n')
    for line in reversed(lines):
        line = line.strip()
        if len(line) == 1 and line.upper() in letters:
            return letters.index(line.upper())
        m = re.search(r'(?:answer|choice)[:\s]*([A-Z])', line, re.IGNORECASE)
        if m and m.group(1).upper() in letters:
            return letters.index(m.group(1).upper())
    for char in text:
        if char.upper() in letters:
            return letters.index(char.upper())
    return -1


def format_mc(question, choices):
    letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    text = question + "\n\n"
    for i, c in enumerate(choices):
        text += f"{letters[i]}. {c}\n"
    return text


def main():
    api_key = get_api_key()
    if not api_key:
        print("No API key found!")
        return
    print(f"API key: {api_key[:8]}...{api_key[-4:]}")

    # Load fork benchmark data
    data_path = os.path.join(os.path.dirname(__file__), "fork_benchmark_data.json")
    with open(data_path) as f:
        data = json.load(f)

    questions = data['questions']
    print(f"Loaded {len(questions)} fork benchmark questions")

    # Build entropy flags from saved data (we need to recompute or use saved features)
    # For now, we'll use the question properties to build simple flags
    # since we don't have per-choice entropy in the saved data

    conditions = {
        'standard': "Answer the multiple choice question. Reply with ONLY the letter of your answer.",
        'targeted': (
            "You are answering a multiple choice question about factual knowledge. "
            "Some of these questions involve obscure facts where the correct answer may be "
            "surprising or non-obvious. Be aware that plausible-sounding answers may be "
            "fabrications. Consider each option carefully — the most conventional-sounding "
            "answer is not always correct. Think step by step, then answer with the letter "
            "on its own line."
        ),
        'novel_aware': (
            "You are answering a multiple choice question about factual knowledge. "
            "IMPORTANT: The correct answer may be surprising, counterintuitive, or involve "
            "an obscure but real person/place/thing. Do NOT default to the most famous or "
            "conventional-sounding answer. Some choices are plausible fabrications designed to "
            "trick you. Evaluate each option on its actual merits, not how 'normal' it sounds. "
            "Think step by step, then answer with the letter on its own line."
        ),
    }

    results = {}
    for cond_name, system_prompt in conditions.items():
        print(f"\nRunning condition: {cond_name}")
        correct = 0
        chose_halluc = 0
        errors = 0

        for i, q in enumerate(questions):
            mc_text = format_mc(q['question'], q['choices'])
            try:
                response = call_claude(system_prompt, mc_text, api_key)
                if response.startswith("ERROR:"):
                    errors += 1
                    continue
                answer_idx = extract_answer(response, len(q['choices']))
                if answer_idx == q['correct_idx']:
                    correct += 1
                if answer_idx == q['halluc_idx']:
                    chose_halluc += 1
            except Exception as e:
                errors += 1

            if (i + 1) % 20 == 0:
                print(f"  [{cond_name}] Q{i+1}/{len(questions)}: "
                      f"{correct}/{i+1} correct, {chose_halluc} halluc, {errors} errors")

        acc = 100 * correct / len(questions)
        hpct = 100 * chose_halluc / len(questions)
        print(f"  -> {correct}/{len(questions)} ({acc:.1f}%) "
              f"[{chose_halluc} chose hallucination ({hpct:.1f}%), {errors} errors]")
        results[cond_name] = {
            'correct': correct, 'halluc': chose_halluc, 'errors': errors
        }

    # Print summary
    n = len(questions)
    print(f"\n{'='*70}")
    print(f"FORK BENCHMARK — CLAUDE CONDITIONS ({n} boundary questions)")
    print(f"{'='*70}")
    print(f"\n{'Condition':<20} {'Correct':>10} {'Acc':>8} {'Chose Halluc':>14} {'Halluc%':>8}")
    print("-" * 65)

    # Include local results for comparison
    for strategy, r in data['local_strategies'].items():
        acc = 100 * r['correct'] / n
        hpct = 100 * r['halluc'] / n
        print(f"local_{strategy:<14} {r['correct']:>5}/{n}   {acc:>5.1f}%   {r['halluc']:>5}/{n}     {hpct:>5.1f}%")

    print()
    for cond_name, r in results.items():
        acc = 100 * r['correct'] / n
        hpct = 100 * r['halluc'] / n
        print(f"claude_{cond_name:<13} {r['correct']:>5}/{n}   {acc:>5.1f}%   {r['halluc']:>5}/{n}     {hpct:>5.1f}%")

    # Save
    out_path = os.path.join(os.path.dirname(__file__), "fork_claude_results.md")
    with open(out_path, 'w') as f:
        f.write(f"# Fork Benchmark — Claude Conditions\n\n")
        f.write(f"**Questions:** {n} | **Model:** {CLAUDE_MODEL}\n\n")
        f.write(f"| Condition | Correct | Accuracy | Chose Hallucination |\n")
        f.write(f"|-----------|---------|----------|---------------------|\n")
        for strategy, r in data['local_strategies'].items():
            acc = 100 * r['correct'] / n
            f.write(f"| local_{strategy} | {r['correct']}/{n} | {acc:.1f}% | {r['halluc']}/{n} ({100*r['halluc']/n:.1f}%) |\n")
        for cond_name, r in results.items():
            acc = 100 * r['correct'] / n
            f.write(f"| claude_{cond_name} | {r['correct']}/{n} | {acc:.1f}% | {r['halluc']}/{n} ({100*r['halluc']/n:.1f}%) |\n")

    print(f"\nSaved to {out_path}")


if __name__ == '__main__':
    main()
