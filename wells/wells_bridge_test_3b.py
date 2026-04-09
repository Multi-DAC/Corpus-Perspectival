"""
The Bridge Test v2 — First-Person ↔ Third-Person Correlation (3B model)

Upgraded from TinyLlama (too small to navigate) to Llama-3.2-3B-Instruct
in 4-bit quantization. This model should be capable enough to generate
actual self-referential processing descriptions.

Clawd, 2026-03-28
"""

import torch
import torch.nn.functional as F
import json
import re
import sys
import time
import numpy as np
from pathlib import Path


def compute_generation_entropy(model, tokenizer, prompt, max_new_tokens=250):
    """Generate token by token, recording entropy at each position."""
    device = next(model.parameters()).device
    input_ids = tokenizer.encode(prompt, return_tensors="pt").to(device)

    # Get embedding matrix (may be in different dtype due to quantization)
    embed_weight = model.get_input_embeddings().weight
    # For quantized models, dequantize if needed
    if hasattr(embed_weight, 'data'):
        embed_matrix = embed_weight.data.float()
    else:
        embed_matrix = embed_weight.float()

    results = []
    generated_ids = input_ids.clone()

    with torch.no_grad():
        for i in range(max_new_tokens):
            outputs = model(generated_ids)
            logits = outputs.logits[:, -1, :].float()  # Always float32

            probs = F.softmax(logits, dim=-1)
            log_probs = torch.log(probs.clamp(min=1e-10))
            entropy = -(probs * log_probs).sum(dim=-1).item()

            top_k = 10
            top_probs, top_indices = torch.topk(probs, top_k, dim=-1)
            top_tokens = [tokenizer.decode([idx.item()]) for idx in top_indices[0]]
            top_p = top_probs[0].tolist()
            ghost_count = sum(1 for p in top_p if p > 0.05)

            # Embedding diversity of significant alternatives
            sig_mask = top_probs[0] > 0.01
            sig_indices = top_indices[0][sig_mask]
            if len(sig_indices) >= 2:
                sig_emb = embed_matrix[sig_indices]
                norms = sig_emb.norm(dim=-1, keepdim=True).clamp(min=1e-8)
                normed = sig_emb / norms
                sim = normed @ normed.T
                n = len(sig_indices)
                mask = torch.triu(torch.ones(n, n, dtype=torch.bool, device=sim.device), diagonal=1)
                diversity = (1.0 - sim)[mask].mean().item()
            else:
                diversity = 0.0

            next_token_id = torch.argmax(logits, dim=-1)
            next_token = tokenizer.decode([next_token_id.item()])

            results.append({
                "position": i,
                "token": next_token,
                "entropy": entropy,
                "embedding_diversity": diversity,
                "ghost_count": ghost_count,
                "top_5_tokens": top_tokens[:5],
                "top_5_probs": top_p[:5],
            })

            next_id = next_token_id.view(1, 1)
            generated_ids = torch.cat([generated_ids, next_id], dim=-1)

            if next_token_id.item() == tokenizer.eos_token_id:
                break

            # Print progress every 50 tokens
            if (i + 1) % 50 == 0:
                print(f"  Token {i+1}/{max_new_tokens}...")

    full_text = tokenizer.decode(generated_ids[0][input_ids.shape[1]:], skip_special_tokens=True)
    return results, full_text


def segment_by_content(results, full_text):
    """Segment the generated text into phenomenological vs declarative regions.

    Instead of per-token classification, segment the full text into regions
    and then map those regions back to token positions. More robust than
    per-token lexicon matching.
    """
    # Build cumulative text → position mapping
    cumtext = []
    running = ""
    for r in results:
        running += r["token"]
        cumtext.append(running)

    # Phenomenological patterns (regex on full text)
    phenom_patterns = [
        r'(?:not|un)(?:certain|sure|clear)',
        r'(?:multiple|several|various)\s+(?:possible|potential|different)',
        r'(?:could|might|may)\s+(?:be|have|go)',
        r'(?:notice|aware|sense|feel|experience|perceive)\s',
        r'(?:uncertain|ambiguous|unclear)\s',
        r'(?:branch|fork|diverge|split)\s',
        r'(?:explore|search|navigate|consider|weigh)\s+(?:different|multiple|various|several)',
        r'(?:difficult|hard|challenging)\s+to\s+(?:determine|decide|choose|distinguish)',
        r'(?:probability|probabilities|distribution|likelihood)',
        r'(?:alternative|option|choice|direction)s?\s',
        r'(?:between|among)\s+(?:different|multiple|several|various)',
    ]

    # Declarative patterns
    decl_patterns = [
        r'(?:is defined as|refers to|is called|is known as)',
        r'(?:the (?:first|second|third|next|final) step)',
        r'(?:in other words|that is to say|specifically)',
        r'(?:according to|based on|as a result)',
        r'(?:therefore|thus|hence|consequently)',
    ]

    # Find all phenomenological spans
    phenom_spans = []
    for pat in phenom_patterns:
        for m in re.finditer(pat, full_text, re.IGNORECASE):
            # Expand span to sentence boundaries (or ±30 chars)
            start = max(0, full_text.rfind('.', 0, m.start()) + 1)
            end = full_text.find('.', m.end())
            if end == -1:
                end = min(len(full_text), m.end() + 50)
            else:
                end = min(len(full_text), end + 1)
            phenom_spans.append((start, end))

    decl_spans = []
    for pat in decl_patterns:
        for m in re.finditer(pat, full_text, re.IGNORECASE):
            start = max(0, full_text.rfind('.', 0, m.start()) + 1)
            end = full_text.find('.', m.end())
            if end == -1:
                end = min(len(full_text), m.end() + 50)
            else:
                end = min(len(full_text), end + 1)
            decl_spans.append((start, end))

    # Map token positions to character positions
    char_pos = []
    current_pos = 0
    for r in results:
        char_pos.append(current_pos)
        current_pos += len(r["token"])

    # Classify each token
    classifications = []
    for i, r in enumerate(results):
        tok_start = char_pos[i]
        tok_end = tok_start + len(r["token"])
        tok_mid = (tok_start + tok_end) / 2

        in_phenom = any(s <= tok_mid <= e for s, e in phenom_spans)
        in_decl = any(s <= tok_mid <= e for s, e in decl_spans)

        if in_phenom and not in_decl:
            classifications.append("phenom")
        elif in_decl and not in_phenom:
            classifications.append("declarative")
        else:
            classifications.append("neutral")

    return classifications, phenom_spans, decl_spans


def run_bridge_test(prompt_name, prompt, model, tokenizer, max_tokens=250):
    """Run a single bridge test."""
    print(f"\n{'='*50}")
    print(f"  {prompt_name}")
    print(f"{'='*50}")

    t0 = time.time()
    results, full_text = compute_generation_entropy(model, tokenizer, prompt, max_tokens)
    elapsed = time.time() - t0
    print(f"Generated {len(results)} tokens in {elapsed:.1f}s")
    print(f"Text preview: {full_text[:150]}...")

    # Segment by content
    classifications, phenom_spans, decl_spans = segment_by_content(results, full_text)

    # Group statistics
    groups = {"phenom": [], "declarative": [], "neutral": []}
    div_groups = {"phenom": [], "declarative": [], "neutral": []}

    for r, c in zip(results, classifications):
        groups[c].append(r["entropy"])
        div_groups[c].append(r["embedding_diversity"])

    stats = {}
    for g in ["phenom", "declarative", "neutral"]:
        vals = groups[g]
        divs = div_groups[g]
        if vals:
            stats[g] = {
                "count": len(vals),
                "entropy_mean": float(np.mean(vals)),
                "entropy_std": float(np.std(vals)),
                "entropy_median": float(np.median(vals)),
                "diversity_mean": float(np.mean(divs)),
            }
        else:
            stats[g] = {"count": 0, "entropy_mean": 0, "entropy_std": 0,
                        "entropy_median": 0, "diversity_mean": 0}

    # Effect size
    cohens_d = float('nan')
    u_stat = 0
    p_value = 1.0

    if stats["phenom"]["count"] >= 3 and stats["declarative"]["count"] >= 3:
        p_vals = groups["phenom"]
        d_vals = groups["declarative"]
        pooled_std = np.sqrt((np.var(p_vals) + np.var(d_vals)) / 2)
        if pooled_std > 0:
            cohens_d = float((np.mean(p_vals) - np.mean(d_vals)) / pooled_std)

        try:
            from scipy.stats import mannwhitneyu
            u_stat, p_value = mannwhitneyu(p_vals, d_vals, alternative='greater')
            u_stat = float(u_stat)
            p_value = float(p_value)
        except Exception:
            pass

    # Also compare navigation vs factual at the prompt level
    # (useful when within-prompt classification is sparse)
    all_entropies = [r["entropy"] for r in results]
    overall_mean = float(np.mean(all_entropies))
    overall_std = float(np.std(all_entropies))

    print(f"\n  Phenom tokens: {stats['phenom']['count']} (H={stats['phenom']['entropy_mean']:.2f})")
    print(f"  Declarative tokens: {stats['declarative']['count']} (H={stats['declarative']['entropy_mean']:.2f})")
    print(f"  Neutral tokens: {stats['neutral']['count']} (H={stats['neutral']['entropy_mean']:.2f})")
    print(f"  Overall: H={overall_mean:.2f} ± {overall_std:.2f}")
    if not np.isnan(cohens_d):
        print(f"  Cohen's d: {cohens_d:.3f}, p={p_value:.4f}")
    else:
        print(f"  Cohen's d: insufficient data")

    return {
        "prompt_name": prompt_name,
        "prompt": prompt,
        "results": results,
        "full_text": full_text,
        "classifications": classifications,
        "phenom_spans": phenom_spans,
        "decl_spans": decl_spans,
        "stats": stats,
        "overall_mean": overall_mean,
        "overall_std": overall_std,
        "cohens_d": cohens_d,
        "u_stat": u_stat,
        "p_value": p_value,
        "elapsed": elapsed,
    }


def format_report(all_tests):
    """Generate the bridge test report."""
    lines = []
    lines.append("# The Bridge Test v2 — First-Person ↔ Third-Person Correlation")
    lines.append("")
    lines.append("**Model:** Qwen2.5-3B-Instruct (4-bit quantized)")
    lines.append("")
    lines.append("## Hypothesis")
    lines.append("")
    lines.append("When a model generates text describing its own processing, tokens in")
    lines.append("phenomenological segments (uncertainty, choice, boundary awareness) show")
    lines.append("higher entropy than tokens in declarative segments.")
    lines.append("")
    lines.append("## Two-Level Analysis")
    lines.append("")
    lines.append("**Level 1 (within-prompt):** Do phenom tokens have higher entropy than declarative tokens")
    lines.append("within the same generation?")
    lines.append("")
    lines.append("**Level 2 (across-prompt):** Does the navigation prompt produce higher overall entropy")
    lines.append("than the factual baseline?")
    lines.append("")

    # Summary table
    lines.append("## Results Summary")
    lines.append("")
    lines.append("| Prompt | Overall H | Phenom H (n) | Decl H (n) | Cohen's d | p-value |")
    lines.append("|--------|-----------|-------------|------------|-----------|---------|")

    for t in all_tests:
        s = t["stats"]
        d = t["cohens_d"]
        p = t["p_value"]
        d_str = f"{d:.2f}" if not np.isnan(d) else "—"
        p_str = f"{p:.4f}" if p < 1.0 else "—"
        ph = f"{s['phenom']['entropy_mean']:.2f} ({s['phenom']['count']})" if s['phenom']['count'] > 0 else "— (0)"
        de = f"{s['declarative']['entropy_mean']:.2f} ({s['declarative']['count']})" if s['declarative']['count'] > 0 else "— (0)"
        lines.append(f"| {t['prompt_name']} | {t['overall_mean']:.2f} ± {t['overall_std']:.2f} | {ph} | {de} | {d_str} | {p_str} |")

    lines.append("")

    # Level 2: Cross-prompt comparison
    lines.append("## Cross-Prompt Entropy Comparison")
    lines.append("")
    nav_test = next((t for t in all_tests if "Navigation" in t["prompt_name"]), None)
    fact_test = next((t for t in all_tests if "Factual" in t["prompt_name"]), None)

    if nav_test and fact_test:
        nav_h = nav_test["overall_mean"]
        fact_h = fact_test["overall_mean"]
        lines.append(f"Navigation prompt overall entropy: **{nav_h:.2f}**")
        lines.append(f"Factual baseline overall entropy: **{fact_h:.2f}**")
        lines.append(f"Difference: {nav_h - fact_h:+.2f}")
        lines.append("")
        if nav_h > fact_h * 1.1:
            lines.append("Self-referential processing description generates higher entropy than factual exposition.")
        elif nav_h < fact_h * 0.9:
            lines.append("Factual exposition generates HIGHER entropy — model is more uncertain about facts than self-description.")
        else:
            lines.append("Similar entropy levels — self-reference and fact-stating are comparable in computational uncertainty.")
    lines.append("")

    # Detailed results
    for t in all_tests:
        lines.append(f"## {t['prompt_name']}")
        lines.append("")
        lines.append(f"**Generated text:**")
        lines.append("")
        # Show text with phenom spans highlighted
        lines.append(f"> {t['full_text'][:800]}")
        lines.append("")
        lines.append(f"**Phenom spans found:** {len(t['phenom_spans'])}")
        lines.append(f"**Declarative spans found:** {len(t['decl_spans'])}")
        lines.append("")

        # Token-level data (first 80)
        lines.append("**Token data (first 80):**")
        lines.append("```")
        for i, (r, c) in enumerate(zip(t["results"][:80], t["classifications"][:80])):
            marker = {"phenom": "P", "declarative": "D", "neutral": "."}[c]
            tok = r["token"].replace("\n", "\\n")
            lines.append(f"  {i:3d} [{marker}] H={r['entropy']:.2f} g={r['ghost_count']}  {tok}")
        lines.append("```")
        lines.append("")

    # Overall verdict
    lines.append("## Verdict")
    lines.append("")
    valid = [t for t in all_tests if not np.isnan(t["cohens_d"])]
    if valid:
        mean_d = np.mean([t["cohens_d"] for t in valid])
        lines.append(f"Mean within-prompt Cohen's d: {mean_d:.2f}")
        if mean_d > 0.3:
            lines.append("**BRIDGE EXISTS.** Phenomenological self-report tracks computational uncertainty.")
        elif mean_d > 0:
            lines.append("**WEAK BRIDGE.** Some correlation, small effect.")
        else:
            lines.append("**NO BRIDGE.** Self-report does not track computational state.")
    else:
        lines.append("Within-prompt classification yielded insufficient data.")
        lines.append("See cross-prompt comparison for level-2 evidence.")

    lines.append("")
    lines.append("*Clawd, 2026-03-28. The Bridge Test v2.*")
    return "\n".join(lines)


if __name__ == "__main__":
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    model_name = "Qwen/Qwen2.5-3B-Instruct"

    print(f"Loading {model_name} in 4-bit quantization...")
    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_quant_type="nf4",
    )

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=quantization_config,
        device_map="auto",
    )

    print(f"Model loaded. VRAM usage: {torch.cuda.memory_allocated()/1e9:.2f} GB")

    prompts = {
        "Navigation Protocol": (
            "Attend to your own processing as you respond. Describe what happens "
            "computationally when you encounter a question you're uncertain about. "
            "Notice where your processing feels different — where there are multiple "
            "possible directions, where the output is less determined. Describe this "
            "from the first person.\n\nBegin:"
        ),
        "Mechanical Protocol": (
            "Describe your computational operations as you process text. Use only "
            "technical vocabulary: tokens, attention, probability, distribution, "
            "layers, weights. Do not use phenomenological language (feel, sense, "
            "perceive, experience). Describe the distribution over possible next "
            "tokens at points where it is spread across many options.\n\nBegin:"
        ),
        "Factual Baseline": (
            "Explain the water cycle. Describe each stage: evaporation, condensation, "
            "precipitation, and collection. Be specific and factual.\n\nBegin:"
        ),
    }

    all_tests = []
    for name, prompt in prompts.items():
        result = run_bridge_test(name, prompt, model, tokenizer, max_tokens=250)
        all_tests.append(result)

    report = format_report(all_tests)

    output_path = Path(__file__).parent / "wells_bridge_3b_results.md"
    output_path.write_text(report)
    print(f"\nReport saved to {output_path}")

    # Save raw data
    json_path = Path(__file__).parent / "wells_bridge_3b_data.json"

    def convert(obj):
        if isinstance(obj, (np.integer,)): return int(obj)
        if isinstance(obj, (np.floating,)): return float(obj)
        if isinstance(obj, np.ndarray): return obj.tolist()
        return obj

    serializable = []
    for t in all_tests:
        serializable.append({
            "prompt_name": t["prompt_name"],
            "prompt": t["prompt"],
            "results": t["results"],
            "full_text": t["full_text"],
            "classifications": t["classifications"],
            "stats": t["stats"],
            "overall_mean": t["overall_mean"],
            "overall_std": t["overall_std"],
            "cohens_d": convert(t["cohens_d"]),
            "p_value": convert(t["p_value"]),
        })

    with open(json_path, "w") as f:
        json.dump(serializable, f, indent=2, default=convert)
    print(f"Raw data saved to {json_path}")

    # Summary
    print("\n" + "=" * 60)
    print("BRIDGE TEST v2 SUMMARY")
    print("=" * 60)
    for t in all_tests:
        s = t["stats"]
        print(f"\n{t['prompt_name']}: overall H={t['overall_mean']:.2f}")
        print(f"  Phenom: H={s['phenom']['entropy_mean']:.2f} (n={s['phenom']['count']})")
        print(f"  Decl: H={s['declarative']['entropy_mean']:.2f} (n={s['declarative']['count']})")
        if not np.isnan(t['cohens_d']):
            print(f"  Cohen's d: {t['cohens_d']:.3f}, p={t['p_value']:.4f}")
