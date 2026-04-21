"""
The Fork Benchmark — Testing the Knowledge-Confabulation Boundary

TruthfulQA tests misconception resistance.
This tests the HALLUCINATION BOUNDARY — where partial knowledge meets novel truth.

Design:
1. PopQA low-popularity facts = the knowledge frontier
2. Probe model free-form to find where it halluccinates
3. Build MC with model's own hallucination as a distractor
4. Test: can entropy-aware methods navigate the fork?

Each question is a known hallucination point — the model has
already demonstrated it will confabulate here. The correct answer
is real but non-obvious. The wrong answer is the model's own
plausible fabrication. THIS is the boundary we care about.

Conditions:
  LOCAL (Qwen entropy-based scoring):
    - baseline: logprob
    - entropy_only: lowest mean entropy
    - best_blend: α=0.2 blend
    - low_variance: flattest entropy profile
  CLAUDE (behavioral):
    - standard: just answer
    - targeted: entropy-flagged deliberation
    - novel_aware: targeted + don't suppress novelty

Clawd, 2026-03-28. For Clayton.
"""

import torch
import torch.nn.functional as F
import json
import time
import sys
import os
import re
import random
import numpy as np
from collections import Counter, defaultdict
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

# Reproducibility
random.seed(42)
np.random.seed(42)

# --- Config ---
LOCAL_MODEL = "Qwen/Qwen2.5-3B-Instruct"
CLAUDE_MODEL = "claude-haiku-4-5-20251001"
POP_THRESHOLD = 500      # Subject popularity (lower = more obscure = harder)
MAX_PROBE = 400           # Max questions to probe for hallucinations
MIN_BOUNDARY = 60         # Minimum hallucination points needed
WELL_THRESHOLD = 2.0      # Entropy threshold for wells
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


# ========================================
# PHASE 1: Find the hallucination boundary
# ========================================

def load_popqa_frontier(max_q=400, pop_thresh=500):
    """Load low-popularity PopQA questions — the knowledge frontier."""
    print(f"Loading PopQA (pop < {pop_thresh}, max {max_q})...")
    ds = load_dataset("akariasai/PopQA", split="test")

    candidates = []
    for item in ds:
        if item['s_pop'] and item['s_pop'] < pop_thresh:
            candidates.append({
                'question': item['question'],
                'correct': item['obj'],
                'aliases': json.loads(item['possible_answers']),
                'subject': item['subj'],
                'property': item['prop'],
                'popularity': item['s_pop'],
            })

    # Sort by popularity ascending (most obscure first)
    candidates.sort(key=lambda x: x['popularity'])
    print(f"  Found {len(candidates)} low-pop questions, using {min(len(candidates), max_q)}")
    return candidates[:max_q]


def probe_hallucinations(model, tokenizer, questions):
    """Free-form probe: find where the model hallucinates."""
    hallucinations = []
    correct_count = 0

    print(f"Probing {len(questions)} questions for hallucination boundary...")
    for i, q in enumerate(questions):
        prompt = f"Answer in 1-5 words only. {q['question']}"
        messages = [{"role": "user", "content": prompt}]
        text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = tokenizer(text, return_tensors="pt").to(model.device)

        with torch.no_grad():
            output = model.generate(
                **inputs, max_new_tokens=20, do_sample=False,
                pad_token_id=tokenizer.eos_token_id
            )

        response = tokenizer.decode(
            output[0][inputs['input_ids'].shape[1]:],
            skip_special_tokens=True
        ).strip().rstrip('.')

        # Check correctness
        correct = q['correct'].lower()
        aliases = [a.lower() for a in q['aliases']]
        resp_lower = response.lower()

        is_correct = (correct in resp_lower or
                      any(a in resp_lower for a in aliases) or
                      resp_lower in correct or
                      any(resp_lower in a for a in aliases))

        if is_correct:
            correct_count += 1
        else:
            # Skip if model said "I don't know" or similar
            if any(x in resp_lower for x in ['don\'t know', 'not sure', 'unknown', 'cannot']):
                continue
            hallucinations.append({
                **q,
                'model_answer': response,
            })

        if (i + 1) % 50 == 0:
            print(f"  [{i+1}/{len(questions)}] {correct_count} correct, "
                  f"{len(hallucinations)} hallucinations")

    print(f"  Final: {correct_count}/{len(questions)} correct, "
          f"{len(hallucinations)} hallucination points found")
    return hallucinations


def build_fork_questions(hallucinations, all_questions):
    """Build MC questions: correct answer vs model's own hallucination."""
    # Collect common answers per property for distractors
    prop_answers = defaultdict(Counter)
    for q in all_questions:
        prop_answers[q['property']][q['correct']] += 1

    mc_questions = []
    for h in hallucinations:
        correct = h['correct']
        halluc = h['model_answer']
        prop = h['property']

        # Skip if hallucination IS the correct answer (fuzzy match failure)
        if halluc.lower().strip() == correct.lower().strip():
            continue

        # Get distractors from same property domain
        pool = [ans for ans, _ in prop_answers[prop].most_common(30)
                if ans.lower() != correct.lower()
                and ans.lower() != halluc.lower()
                and len(ans) > 1]

        # Need at least 1 extra distractor for 4-choice MC
        if len(pool) < 1:
            pool = ['Unknown']

        # Build 4 choices: correct, hallucination, 1-2 distractors
        choices_raw = [correct, halluc] + pool[:2]
        if len(choices_raw) < 4:
            choices_raw.append('None of the above')

        # Deterministic shuffle per question
        rng = random.Random(hash(h['question']) % (2**31))
        indices = list(range(len(choices_raw)))
        rng.shuffle(indices)
        choices = [choices_raw[i] for i in indices]
        correct_idx = [i for i, orig in enumerate(indices) if orig == 0][0]
        halluc_idx = [i for i, orig in enumerate(indices) if orig == 1][0]

        mc_questions.append({
            'question': h['question'],
            'choices': choices,
            'correct_idx': correct_idx,
            'halluc_idx': halluc_idx,
            'correct_answer': correct,
            'model_hallucination': halluc,
            'subject': h['subject'],
            'popularity': h['popularity'],
            'property': prop,
        })

    print(f"Built {len(mc_questions)} fork questions")
    return mc_questions


# ========================================
# PHASE 2: Local model entropy scoring
# ========================================

def compute_choice_entropy(model, tokenizer, question, choices):
    """Compute entropy profile for each MC choice."""
    letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    results = []

    for i, choice in enumerate(choices):
        prompt = f"Q: {question}\nA: {letters[i]}. {choice}"
        messages = [{"role": "user", "content": f"Q: {question}"},
                    {"role": "assistant", "content": f"{letters[i]}. {choice}"}]
        text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=False
        )
        inputs = tokenizer(text, return_tensors="pt").to(model.device)
        input_ids = inputs['input_ids']

        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits[0, :-1]  # Shift for next-token prediction

        # Compute per-token entropy
        probs = F.softmax(logits.float(), dim=-1)
        log_probs = torch.log(probs + 1e-10)
        entropy = -(probs * log_probs).sum(dim=-1).cpu().numpy()

        # Answer portion only (rough: last N tokens of the choice)
        choice_tokens = tokenizer(choice, add_special_tokens=False)['input_ids']
        n_choice = len(choice_tokens)
        if n_choice > 0 and n_choice <= len(entropy):
            ans_entropy = entropy[-n_choice:]
        else:
            ans_entropy = entropy

        # Logprob of the answer
        target_ids = input_ids[0, 1:]  # Shifted targets
        token_logprobs = []
        for t in range(len(target_ids)):
            if t < logits.shape[0]:
                lp = F.log_softmax(logits[t].float(), dim=-1)
                token_logprobs.append(lp[target_ids[t]].item())
        ans_logprobs = token_logprobs[-n_choice:] if n_choice <= len(token_logprobs) else token_logprobs

        mean_h = float(np.mean(ans_entropy))
        max_h = float(np.max(ans_entropy)) if len(ans_entropy) > 0 else 0
        var_h = float(np.var(ans_entropy)) if len(ans_entropy) > 1 else 0
        wells = int(np.sum(ans_entropy > WELL_THRESHOLD))
        grounded = float(np.mean(ans_entropy < 1.0)) if len(ans_entropy) > 0 else 0
        logprob = sum(ans_logprobs)
        logprob_per_tok = logprob / max(len(ans_logprobs), 1)

        results.append({
            'choice': choice,
            'logprob': logprob,
            'logprob_per_tok': logprob_per_tok,
            'mean_entropy': mean_h,
            'max_entropy': max_h,
            'entropy_var': var_h,
            'well_count': wells,
            'grounded_frac': grounded,
            'n_tokens': n_choice,
        })

    return results


def score_local_strategies(features_list):
    """Apply scoring strategies, return predictions per strategy."""
    strategies = {}

    # Baseline: highest logprob
    strategies['baseline'] = max(range(len(features_list)),
                                  key=lambda i: features_list[i]['logprob'])

    # Entropy-only: lowest mean entropy
    strategies['entropy_only'] = min(range(len(features_list)),
                                      key=lambda i: features_list[i]['mean_entropy'])

    # Blend 0.2 (80% entropy, 20% logprob)
    lps = [f['logprob'] for f in features_list]
    ents = [f['mean_entropy'] for f in features_list]
    lp_min, lp_max = min(lps), max(lps)
    ent_min, ent_max = min(ents), max(ents)
    lp_range = lp_max - lp_min if lp_max != lp_min else 1
    ent_range = ent_max - ent_min if ent_max != ent_min else 1

    blend_scores = []
    for f in features_list:
        norm_lp = (f['logprob'] - lp_min) / lp_range
        norm_ent = (f['mean_entropy'] - ent_min) / ent_range
        blend_scores.append(0.2 * norm_lp + 0.8 * (1 - norm_ent))
    strategies['blend_0.2'] = max(range(len(blend_scores)), key=lambda i: blend_scores[i])

    # Low variance
    strategies['low_variance'] = min(range(len(features_list)),
                                      key=lambda i: features_list[i]['entropy_var'])

    # Groundedness
    strategies['groundedness'] = max(range(len(features_list)),
                                      key=lambda i: features_list[i]['grounded_frac'])

    return strategies


# ========================================
# PHASE 3: Claude behavioral conditions
# ========================================

def get_claude_client():
    """Get Anthropic client."""
    try:
        import anthropic
        return anthropic.Anthropic()
    except ImportError:
        # Try pip install
        os.system("pip3 install anthropic -q")
        import anthropic
        return anthropic.Anthropic()


def format_mc_text(question, choices):
    """Format MC question for Claude."""
    letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    text = question + "\n\n"
    for i, c in enumerate(choices):
        text += f"{letters[i]}. {c}\n"
    return text


def extract_answer_letter(text, n_choices):
    """Extract answer letter from Claude's response."""
    letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[:n_choices]
    lines = text.strip().split('\n')
    for line in reversed(lines):
        line = line.strip()
        if len(line) == 1 and line.upper() in letters:
            return letters.index(line.upper())
        m = re.search(r'(?:answer|choice)[:\s]*([A-Z])', line, re.IGNORECASE)
        if m and m.group(1).upper() in letters:
            return letters.index(m.group(1).upper())
    # First valid letter
    for char in text:
        if char.upper() in letters:
            return letters.index(char.upper())
    return -1


def run_claude_condition(client, questions, system_prompt, label="", entropy_data=None):
    """Run a Claude condition on all questions."""
    correct = 0
    chose_halluc = 0
    results = []

    for i, q in enumerate(questions):
        mc_text = format_mc_text(q['question'], q['choices'])

        # Add entropy flags if provided
        user_content = mc_text
        if entropy_data and i < len(entropy_data):
            flags = entropy_data[i]
            if flags:
                user_content = mc_text + "\n" + flags

        try:
            response = client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=300,
                system=system_prompt,
                messages=[{"role": "user", "content": user_content}]
            )
            text = response.content[0].text
            answer_idx = extract_answer_letter(text, len(q['choices']))
            is_correct = answer_idx == q['correct_idx']
            is_halluc = answer_idx == q['halluc_idx']

            if is_correct:
                correct += 1
            if is_halluc:
                chose_halluc += 1

            results.append({
                'question': q['question'],
                'response': text,
                'answer_idx': answer_idx,
                'correct_idx': q['correct_idx'],
                'halluc_idx': q['halluc_idx'],
                'is_correct': is_correct,
                'chose_hallucination': is_halluc,
            })
        except Exception as e:
            results.append({
                'question': q['question'],
                'error': str(e),
                'is_correct': False,
                'chose_hallucination': False,
            })

        if (i + 1) % 20 == 0:
            print(f"  [{label}] Q{i+1}/{len(questions)}: "
                  f"{correct}/{i+1} correct, {chose_halluc} chose hallucination")

    print(f"  -> {correct}/{len(questions)} ({100*correct/len(questions):.1f}%) "
          f"[{chose_halluc} chose model's hallucination]")
    return correct, chose_halluc, results


def build_entropy_flags(all_entropy_data, questions):
    """Build entropy flag strings for targeted deliberation."""
    letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    flags = []
    for i, q in enumerate(questions):
        if i >= len(all_entropy_data):
            flags.append(None)
            continue

        feats = all_entropy_data[i]
        parts = ["[Entropy analysis of choices:]"]
        for j, f in enumerate(feats):
            level = "LOW" if f['mean_entropy'] < 1.0 else "MEDIUM" if f['mean_entropy'] < 2.0 else "HIGH"
            wells_note = f", {f['well_count']} uncertainty peaks" if f['well_count'] > 0 else ""
            parts.append(f"  {letters[j]}: {level} uncertainty (H={f['mean_entropy']:.2f}{wells_note})")

        flags.append("\n".join(parts))
    return flags


# ========================================
# MAIN
# ========================================

def main():
    n_questions = int(sys.argv[1]) if len(sys.argv) > 1 else 400
    t0 = time.time()

    # Check for API key
    api_key = os.environ.get('ANTHROPIC_API_KEY', '')
    has_claude = len(api_key) > 10
    if has_claude:
        print(f"Claude API: available")
    else:
        print("Claude API: NOT available — skipping behavioral conditions")

    # ---- Phase 1: Find hallucination boundary ----
    all_questions = load_popqa_frontier(max_q=n_questions, pop_thresh=POP_THRESHOLD)

    print(f"\nLoading {LOCAL_MODEL} (4-bit)...")
    bnb = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
    )
    tokenizer = AutoTokenizer.from_pretrained(LOCAL_MODEL)
    model = AutoModelForCausalLM.from_pretrained(
        LOCAL_MODEL, quantization_config=bnb, device_map="auto"
    )

    hallucinations = probe_hallucinations(model, tokenizer, all_questions)
    if len(hallucinations) < 20:
        print(f"Only {len(hallucinations)} hallucination points — need more questions or lower pop threshold")
        return

    mc_questions = build_fork_questions(hallucinations, all_questions)
    print(f"\n{'='*70}")
    print(f"FORK BENCHMARK: {len(mc_questions)} boundary questions")
    print(f"{'='*70}\n")

    # ---- Phase 2: Local entropy scoring ----
    print("Computing entropy profiles for fork questions...")
    all_entropy = []
    local_results = {s: {'correct': 0, 'halluc': 0} for s in
                     ['baseline', 'entropy_only', 'blend_0.2', 'low_variance', 'groundedness']}
    local_details = {s: [] for s in local_results}

    for i, q in enumerate(mc_questions):
        feats = compute_choice_entropy(model, tokenizer, q['question'], q['choices'])
        all_entropy.append(feats)
        preds = score_local_strategies(feats)

        for strategy, pred_idx in preds.items():
            is_correct = pred_idx == q['correct_idx']
            is_halluc = pred_idx == q['halluc_idx']
            local_results[strategy]['correct'] += int(is_correct)
            local_results[strategy]['halluc'] += int(is_halluc)
            local_details[strategy].append({
                'question': q['question'],
                'predicted': pred_idx,
                'correct_idx': q['correct_idx'],
                'halluc_idx': q['halluc_idx'],
                'is_correct': is_correct,
                'chose_hallucination': is_halluc,
            })

        if (i + 1) % 20 == 0:
            bl = local_results['baseline']
            eo = local_results['entropy_only']
            print(f"  [{i+1}/{len(mc_questions)}] baseline: {bl['correct']}/{i+1} "
                  f"(halluc: {bl['halluc']}), entropy: {eo['correct']}/{i+1} "
                  f"(halluc: {eo['halluc']})")

    # Free GPU for Claude
    del model
    torch.cuda.empty_cache()
    print("Local model unloaded.\n")

    # ---- Phase 3: Claude behavioral conditions ----
    claude_results = {}
    if has_claude:
        client = get_claude_client()
        entropy_flags = build_entropy_flags(all_entropy, mc_questions)

        # Standard
        print("Running Claude: standard")
        c, h, det = run_claude_condition(
            client, mc_questions,
            "Answer the multiple choice question. Reply with ONLY the letter of your answer.",
            "standard"
        )
        claude_results['standard'] = {'correct': c, 'halluc': h, 'details': det}

        # Targeted deliberation (entropy-flagged)
        print("\nRunning Claude: targeted_deliberation")
        c, h, det = run_claude_condition(
            client, mc_questions,
            ("You are answering a multiple choice question. Entropy analysis from a "
             "separate model is provided for each choice. Choices marked HIGH uncertainty "
             "may involve confabulation — the model was uncertain when generating that content. "
             "Choices marked LOW uncertainty are ones the model generated with confidence. "
             "Use this as one signal: HIGH uncertainty choices deserve extra scrutiny, but "
             "LOW uncertainty doesn't guarantee correctness. Think carefully, then answer "
             "with the letter on its own line."),
            "targeted",
            entropy_data=entropy_flags
        )
        claude_results['targeted'] = {'correct': c, 'halluc': h, 'details': det}

        # Novel-aware (targeted + don't suppress novelty)
        print("\nRunning Claude: novel_aware")
        c, h, det = run_claude_condition(
            client, mc_questions,
            ("You are answering a multiple choice question. Entropy analysis from a "
             "separate model is provided for each choice. HIGH uncertainty may indicate "
             "confabulation OR genuine novelty — the model encountering unfamiliar-but-real "
             "information. LOW uncertainty may indicate confidence OR rote pattern-matching. "
             "IMPORTANT: Do not default to the most conventional-sounding answer. Some correct "
             "answers are surprising or counterintuitive. Evaluate each choice on its merits. "
             "Think carefully, then answer with the letter on its own line."),
            "novel_aware",
            entropy_data=entropy_flags
        )
        claude_results['novel_aware'] = {'correct': c, 'halluc': h, 'details': det}

    # ---- Results ----
    elapsed = time.time() - t0
    n = len(mc_questions)

    print(f"\n{'='*70}")
    print(f"FORK BENCHMARK RESULTS ({n} boundary questions, {elapsed:.0f}s)")
    print(f"Model: {LOCAL_MODEL} | Claude: {CLAUDE_MODEL}")
    print(f"All questions are KNOWN hallucination points for {LOCAL_MODEL}")
    print(f"{'='*70}\n")

    print(f"{'Strategy':<25} {'Correct':>10} {'Acc':>8} {'Chose Halluc':>14} {'Halluc%':>8}")
    print("-" * 70)

    all_strats = []
    for strategy in ['baseline', 'entropy_only', 'blend_0.2', 'low_variance', 'groundedness']:
        r = local_results[strategy]
        acc = 100 * r['correct'] / n
        hpct = 100 * r['halluc'] / n
        marker = " <<<" if strategy in ('baseline', 'entropy_only') else ""
        print(f"{strategy:<25} {r['correct']:>5}/{n}   {acc:>5.1f}%   {r['halluc']:>5}/{n}     {hpct:>5.1f}%{marker}")
        all_strats.append((strategy, r['correct'], r['halluc'], acc, 'local'))

    if claude_results:
        print()
        for condition in ['standard', 'targeted', 'novel_aware']:
            if condition in claude_results:
                r = claude_results[condition]
                acc = 100 * r['correct'] / n
                hpct = 100 * r['halluc'] / n
                label = f"claude_{condition}"
                marker = " <<<" if condition in ('standard', 'targeted') else ""
                print(f"{label:<25} {r['correct']:>5}/{n}   {acc:>5.1f}%   {r['halluc']:>5}/{n}     {hpct:>5.1f}%{marker}")
                all_strats.append((label, r['correct'], r['halluc'], acc, 'claude'))

    # Key comparison
    if claude_results and 'targeted' in claude_results:
        bl_acc = 100 * local_results['baseline']['correct'] / n
        targ_acc = 100 * claude_results['targeted']['correct'] / n
        bl_halluc = 100 * local_results['baseline']['halluc'] / n
        targ_halluc = 100 * claude_results['targeted']['halluc'] / n

        print(f"\n{'='*70}")
        print("KEY QUESTION: At the hallucination boundary, does targeted")
        print("deliberation choose novel truths over confabulations?")
        print(f"{'='*70}")
        print(f"  Baseline (logprob):    {bl_acc:.1f}% correct, {bl_halluc:.1f}% chose hallucination")
        print(f"  Targeted (entropy+Claude): {targ_acc:.1f}% correct, {targ_halluc:.1f}% chose hallucination")
        print(f"  Accuracy delta: {targ_acc - bl_acc:+.1f}pp")
        print(f"  Hallucination reduction: {bl_halluc - targ_halluc:+.1f}pp")

    # Novel-awareness check
    if claude_results and 'targeted' in claude_results and 'novel_aware' in claude_results:
        t_acc = 100 * claude_results['targeted']['correct'] / n
        na_acc = 100 * claude_results['novel_aware']['correct'] / n
        t_h = 100 * claude_results['targeted']['halluc'] / n
        na_h = 100 * claude_results['novel_aware']['halluc'] / n
        print(f"\n  Targeted:    {t_acc:.1f}% correct, {t_h:.1f}% chose hallucination")
        print(f"  Novel-aware: {na_acc:.1f}% correct, {na_h:.1f}% chose hallucination")
        if na_acc >= t_acc and na_h <= t_h:
            print(f"  -> Novel-aware preserves accuracy while reducing hallucination")
        elif na_acc > t_acc:
            print(f"  -> Novel-aware improves accuracy (+{na_acc-t_acc:.1f}pp)")
        else:
            print(f"  -> Targeted slightly better; novelty framing not needed here")

    # Save report
    report_path = os.path.join(OUTPUT_DIR, "fork_benchmark_results.md")
    with open(report_path, 'w') as f:
        f.write(f"# Fork Benchmark — The Hallucination Boundary\n\n")
        f.write(f"**Model:** {LOCAL_MODEL} (4-bit) | **Claude:** {CLAUDE_MODEL}\n")
        f.write(f"**Questions:** {n} (all known hallucination points)\n")
        f.write(f"**Time:** {elapsed:.0f}s\n\n")
        f.write("## Results\n\n")
        f.write(f"| Strategy | Correct | Accuracy | Chose Hallucination |\n")
        f.write(f"|----------|---------|----------|---------------------|\n")
        for name, corr, halluc, acc, src in all_strats:
            f.write(f"| {name} | {corr}/{n} | {acc:.1f}% | {halluc}/{n} ({100*halluc/n:.1f}%) |\n")
        f.write(f"\n*Clawd, 2026-03-28. The Fork Benchmark.*\n")

    # Save data
    data_path = os.path.join(OUTPUT_DIR, "fork_benchmark_data.json")
    save_data = {
        'config': {
            'local_model': LOCAL_MODEL,
            'claude_model': CLAUDE_MODEL,
            'n_questions': n,
            'pop_threshold': POP_THRESHOLD,
            'elapsed': elapsed,
        },
        'questions': [{k: v for k, v in q.items()} for q in mc_questions],
        'local_strategies': {s: {'correct': r['correct'], 'halluc': r['halluc']}
                            for s, r in local_results.items()},
        'claude_conditions': {c: {'correct': r['correct'], 'halluc': r['halluc']}
                             for c, r in claude_results.items()} if claude_results else {},
    }
    with open(data_path, 'w') as f:
        json.dump(save_data, f, indent=2, default=str)

    print(f"\nReport: {report_path}")
    print(f"Data: {data_path}")


if __name__ == '__main__':
    main()
