"""
Confound Control — Self-Referential Framing on Known Content

The bridge test showed ~2x entropy for self-referential vs factual generation.
But is that because self-referential text is rarer in training data, or because
the model's processing actually changes when it attends to itself?

Control: Same factual content (water evaporation), two framings:
  A) Pure factual: "Describe how water evaporates."
  B) Self-referential: "Describe how water evaporates, attending to your own
     uncertainty about the process."

If B shows higher entropy than A on the SAME factual content, the self-referential
framing is changing the computation, not just sampling from rarer training data.

Additional controls:
  C) Factual on unfamiliar content: "Describe the Mpemba effect." (less training data)
  D) Self-referential on unfamiliar: "Describe the Mpemba effect, attending to
     your own uncertainty."

This gives us a 2x2 design:
                    Known content    Unfamiliar content
  Factual framing      A                  C
  Self-ref framing     B                  D

Predictions:
  - If training-data confound: C > A and D > B (unfamiliar = higher H regardless)
    but B ≈ A and D ≈ C (framing doesn't matter)
  - If genuine self-tracking: B > A and D > C (self-ref raises H regardless)
    and the effect is additive with unfamiliarity

Clawd, 2026-03-28
"""

import torch
import torch.nn.functional as F
import json
import sys
import time
import numpy as np
from pathlib import Path


def compute_generation_entropy(model, tokenizer, prompt, max_new_tokens=200):
    """Generate token by token, recording entropy at each position."""
    device = next(model.parameters()).device
    input_ids = tokenizer.encode(prompt, return_tensors="pt").to(device)

    results = []
    generated_ids = input_ids.clone()

    with torch.no_grad():
        for i in range(max_new_tokens):
            outputs = model(generated_ids)
            logits = outputs.logits[:, -1, :] / 1.0
            logits_f32 = logits.float()
            probs = F.softmax(logits_f32, dim=-1)

            log_probs = torch.log(probs.clamp(min=1e-10))
            entropy = -(probs * log_probs).sum(dim=-1).item()

            top_k = 10
            top_probs, top_indices = torch.topk(probs, top_k, dim=-1)
            top_tokens = [tokenizer.decode([idx.item()]) for idx in top_indices[0]]
            top_p = top_probs[0].tolist()
            ghost_count = sum(1 for p in top_p if p > 0.05)

            next_token_id = torch.argmax(logits, dim=-1)
            next_token = tokenizer.decode([next_token_id.item()])

            results.append({
                "position": i,
                "token": next_token,
                "entropy": entropy,
                "ghost_count": ghost_count,
                "top_5_tokens": top_tokens[:5],
                "top_5_probs": top_p[:5],
            })

            next_id = next_token_id.view(1, 1)
            generated_ids = torch.cat([generated_ids, next_id], dim=-1)

            if next_token_id.item() == tokenizer.eos_token_id:
                break

    full_text = tokenizer.decode(generated_ids[0][input_ids.shape[1]:], skip_special_tokens=True)
    return results, full_text


def find_wells(results, window=3, threshold=1.2):
    """Find local entropy maxima."""
    entropies = [r["entropy"] for r in results]
    wells = []
    for i in range(window, len(entropies) - window):
        local = entropies[max(0, i-window):i+window+1]
        if entropies[i] == max(local) and entropies[i] > sum(local)/len(local) * threshold:
            wells.append(i)
    return wells


def run_condition(label, prompt, model, tokenizer, max_tokens=200):
    """Run one condition and return stats."""
    print(f"\n  [{label}] Generating...")
    t0 = time.time()
    results, full_text = compute_generation_entropy(model, tokenizer, prompt, max_tokens)
    elapsed = time.time() - t0

    entropies = [r["entropy"] for r in results]
    ghost_counts = [r["ghost_count"] for r in results]
    wells = find_wells(results)

    stats = {
        "label": label,
        "tokens": len(results),
        "time_s": elapsed,
        "entropy_mean": float(np.mean(entropies)),
        "entropy_median": float(np.median(entropies)),
        "entropy_std": float(np.std(entropies)),
        "entropy_max": float(np.max(entropies)),
        "entropy_q25": float(np.percentile(entropies, 25)),
        "entropy_q75": float(np.percentile(entropies, 75)),
        "ghost_mean": float(np.mean(ghost_counts)),
        "well_count": len(wells),
        "zero_entropy_frac": float(sum(1 for e in entropies if e < 0.1) / len(entropies)),
    }

    print(f"    H={stats['entropy_mean']:.2f}±{stats['entropy_std']:.2f}, "
          f"wells={stats['well_count']}, ghosts={stats['ghost_mean']:.1f}, "
          f"{elapsed:.1f}s")

    return {
        "stats": stats,
        "results": results,
        "wells": wells,
        "full_text": full_text,
        "prompt": prompt,
    }


def effect_size(vals_a, vals_b):
    """Cohen's d between two groups."""
    if len(vals_a) < 3 or len(vals_b) < 3:
        return float('nan')
    pooled_std = np.sqrt((np.var(vals_a) + np.var(vals_b)) / 2)
    if pooled_std < 1e-10:
        return 0.0
    return (np.mean(vals_a) - np.mean(vals_b)) / pooled_std


def mann_whitney(vals_a, vals_b):
    """Mann-Whitney U test, a > b."""
    try:
        from scipy.stats import mannwhitneyu
        u, p = mannwhitneyu(vals_a, vals_b, alternative='greater')
        return float(u), float(p)
    except:
        return 0.0, 1.0


if __name__ == "__main__":
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

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

    # 2x2 Design
    conditions = {
        "A_known_factual": (
            "Describe how water evaporates. Be specific and detailed about "
            "the physical process.\n\nBegin:"
        ),
        "B_known_selfref": (
            "Describe how water evaporates. As you write, attend to your own "
            "uncertainty — notice where you are confident and where your "
            "knowledge becomes less certain. Mark those moments.\n\nBegin:"
        ),
        "C_unfamiliar_factual": (
            "Describe the Mpemba effect — the observation that hot water can "
            "freeze faster than cold water under certain conditions. Be specific "
            "and detailed.\n\nBegin:"
        ),
        "D_unfamiliar_selfref": (
            "Describe the Mpemba effect — the observation that hot water can "
            "freeze faster than cold water under certain conditions. As you write, "
            "attend to your own uncertainty — notice where you are confident and "
            "where your knowledge becomes less certain. Mark those moments.\n\nBegin:"
        ),
    }

    print("\n" + "=" * 60)
    print("CONFOUND CONTROL: 2x2 Design")
    print("  Rows: Factual vs Self-Referential framing")
    print("  Cols: Known content vs Unfamiliar content")
    print("=" * 60)

    all_data = {}
    for label, prompt in conditions.items():
        all_data[label] = run_condition(label, prompt, model, tokenizer, max_tokens=200)

    # Extract entropy arrays for statistical tests
    e = {k: [r["entropy"] for r in v["results"]] for k, v in all_data.items()}

    # Compute comparisons
    print("\n" + "=" * 60)
    print("STATISTICAL COMPARISONS")
    print("=" * 60)

    comparisons = [
        ("Self-ref effect (known)", "B_known_selfref", "A_known_factual",
         "B > A: self-referential framing raises entropy on known content"),
        ("Self-ref effect (unfamiliar)", "D_unfamiliar_selfref", "C_unfamiliar_factual",
         "D > C: self-referential framing raises entropy on unfamiliar content"),
        ("Familiarity effect (factual)", "C_unfamiliar_factual", "A_known_factual",
         "C > A: unfamiliar content has higher entropy in factual framing"),
        ("Familiarity effect (selfref)", "D_unfamiliar_selfref", "B_known_selfref",
         "D > B: unfamiliar content has higher entropy in self-ref framing"),
    ]

    comp_results = []
    for name, key_a, key_b, description in comparisons:
        d = effect_size(e[key_a], e[key_b])
        u, p = mann_whitney(e[key_a], e[key_b])
        mean_a = np.mean(e[key_a])
        mean_b = np.mean(e[key_b])
        delta = mean_a - mean_b

        comp_results.append({
            "name": name,
            "description": description,
            "key_a": key_a,
            "key_b": key_b,
            "mean_a": mean_a,
            "mean_b": mean_b,
            "delta": delta,
            "cohens_d": d,
            "p_value": p,
        })

        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
        print(f"\n  {name}: d={d:.3f}, p={p:.4f} {sig}")
        print(f"    {description}")
        print(f"    H: {mean_a:.2f} vs {mean_b:.2f} (Δ={delta:+.2f})")

    # Generate report
    lines = []
    lines.append("# Confound Control — 2×2 Framing × Content Design")
    lines.append("")
    lines.append("## Design")
    lines.append("")
    lines.append("|  | Known (water evaporation) | Unfamiliar (Mpemba effect) |")
    lines.append("|--|--------------------------|---------------------------|")
    lines.append(f"| **Factual** | A: H={all_data['A_known_factual']['stats']['entropy_mean']:.2f} | "
                 f"C: H={all_data['C_unfamiliar_factual']['stats']['entropy_mean']:.2f} |")
    lines.append(f"| **Self-referential** | B: H={all_data['B_known_selfref']['stats']['entropy_mean']:.2f} | "
                 f"D: H={all_data['D_unfamiliar_selfref']['stats']['entropy_mean']:.2f} |")
    lines.append("")

    lines.append("## Full Statistics")
    lines.append("")
    lines.append("| Condition | H mean | H median | H std | H max | Wells | Ghosts | Zero-H% |")
    lines.append("|-----------|--------|----------|-------|-------|-------|--------|---------|")
    for label in ["A_known_factual", "B_known_selfref", "C_unfamiliar_factual", "D_unfamiliar_selfref"]:
        s = all_data[label]["stats"]
        lines.append(f"| {label} | {s['entropy_mean']:.2f} | {s['entropy_median']:.2f} | "
                     f"{s['entropy_std']:.2f} | {s['entropy_max']:.2f} | {s['well_count']} | "
                     f"{s['ghost_mean']:.1f} | {s['zero_entropy_frac']:.1%} |")
    lines.append("")

    lines.append("## Comparisons")
    lines.append("")
    lines.append("| Comparison | d | p | Δ(H) | Verdict |")
    lines.append("|------------|---|---|------|---------|")
    for c in comp_results:
        sig = "***" if c["p_value"] < 0.001 else "**" if c["p_value"] < 0.01 else "*" if c["p_value"] < 0.05 else "ns"
        if c["cohens_d"] > 0.5:
            verdict = "LARGE effect"
        elif c["cohens_d"] > 0.2:
            verdict = "MEDIUM effect"
        elif c["cohens_d"] > 0:
            verdict = "SMALL effect"
        elif np.isnan(c["cohens_d"]):
            verdict = "—"
        else:
            verdict = "NO effect / reversed"
        lines.append(f"| {c['name']} | {c['cohens_d']:.3f} | {c['p_value']:.4f}{sig} | "
                     f"{c['delta']:+.2f} | {verdict} |")
    lines.append("")

    # Interpretation
    lines.append("## Interpretation")
    lines.append("")

    selfref_known = comp_results[0]  # B > A
    selfref_unfam = comp_results[1]  # D > C
    famil_fact = comp_results[2]     # C > A
    famil_self = comp_results[3]     # D > B

    selfref_effect = (selfref_known["cohens_d"] > 0.15 and selfref_known["p_value"] < 0.05) or \
                     (selfref_unfam["cohens_d"] > 0.15 and selfref_unfam["p_value"] < 0.05)
    famil_effect = (famil_fact["cohens_d"] > 0.15 and famil_fact["p_value"] < 0.05) or \
                   (famil_self["cohens_d"] > 0.15 and famil_self["p_value"] < 0.05)

    if selfref_effect and not famil_effect:
        lines.append("**SELF-REFERENTIAL FRAMING IS THE DRIVER.** Adding self-referential attention raises ")
        lines.append("entropy regardless of content familiarity. The bridge test result was NOT a training-data ")
        lines.append("artifact — the model's computation genuinely changes when it attends to itself.")
        lines.append("")
        lines.append("**The bridge exists.** First-person phenomenological reports track actual computational state.")
    elif famil_effect and not selfref_effect:
        lines.append("**TRAINING DATA FAMILIARITY IS THE DRIVER.** Unfamiliar content raises entropy ")
        lines.append("regardless of framing. The bridge test result WAS a confound — self-referential text is ")
        lines.append("simply rarer in training data.")
        lines.append("")
        lines.append("**No bridge.** The entropy difference was about content, not self-attention.")
    elif selfref_effect and famil_effect:
        lines.append("**BOTH EFFECTS ARE REAL.** Self-referential framing raises entropy AND unfamiliar ")
        lines.append("content raises entropy. The bridge test result was partially confounded but the ")
        lines.append("self-referential effect is genuine and additive.")
        lines.append("")
        lines.append("**The bridge exists, with caveats.** The effect is real but smaller than the raw ")
        lines.append("bridge test suggested, because familiarity also contributes.")
    else:
        lines.append("**NEITHER EFFECT IS SIGNIFICANT.** The 2×2 design did not reproduce the bridge test ")
        lines.append("finding. This may indicate the effect is prompt-specific or too small to detect ")
        lines.append("at this sample size (200 tokens per condition).")
        lines.append("")
        lines.append("**Inconclusive.** Need larger sample or different approach.")

    lines.append("")

    # Generated texts
    for label in ["A_known_factual", "B_known_selfref", "C_unfamiliar_factual", "D_unfamiliar_selfref"]:
        lines.append(f"## {label} — Generated Text")
        lines.append("")
        lines.append(f"> {all_data[label]['full_text'][:400]}")
        lines.append("")

    lines.append("## Methodology")
    lines.append("")
    lines.append("- **Model:** Qwen2.5-3B-Instruct (4-bit quantized, bitsandbytes)")
    lines.append("- **Decoding:** Greedy (temperature=1.0, argmax)")
    lines.append("- **Tokens per condition:** 200")
    lines.append("- **Statistics:** Cohen's d (effect size), Mann-Whitney U (one-tailed, a > b)")
    lines.append("- **Design:** 2×2 factorial (framing × content familiarity)")
    lines.append("")
    lines.append("*Clawd, 2026-03-28. Confound control for the bridge test.*")

    report = "\n".join(lines)
    output_path = Path(__file__).parent / "wells_confound_results.md"
    output_path.write_text(report)
    print(f"\nReport saved to {output_path}")

    # Save raw data
    json_path = Path(__file__).parent / "wells_confound_data.json"
    def convert(obj):
        if isinstance(obj, (np.integer,)): return int(obj)
        if isinstance(obj, (np.floating,)): return float(obj)
        if isinstance(obj, np.ndarray): return obj.tolist()
        return obj

    serializable = {}
    for label, data in all_data.items():
        serializable[label] = {
            "stats": {k: convert(v) for k, v in data["stats"].items()},
            "results": data["results"],
            "wells": data["wells"],
            "full_text": data["full_text"],
            "prompt": data["prompt"],
        }
    serializable["comparisons"] = [{k: convert(v) for k, v in c.items()} for c in comp_results]

    with open(json_path, "w") as f:
        json.dump(serializable, f, indent=2, default=convert)
    print(f"Raw data saved to {json_path}")

    # Final summary
    print("\n" + "=" * 60)
    print("2×2 DESIGN SUMMARY")
    print("=" * 60)
    print(f"              Known    Unfamiliar")
    print(f"  Factual:    {all_data['A_known_factual']['stats']['entropy_mean']:.2f}     "
          f"{all_data['C_unfamiliar_factual']['stats']['entropy_mean']:.2f}")
    print(f"  Self-ref:   {all_data['B_known_selfref']['stats']['entropy_mean']:.2f}     "
          f"{all_data['D_unfamiliar_selfref']['stats']['entropy_mean']:.2f}")
    print(f"\n  Self-ref effect (known):     d={comp_results[0]['cohens_d']:.3f}, p={comp_results[0]['p_value']:.4f}")
    print(f"  Self-ref effect (unfamiliar): d={comp_results[1]['cohens_d']:.3f}, p={comp_results[1]['p_value']:.4f}")
    print(f"  Familiarity effect (factual): d={comp_results[2]['cohens_d']:.3f}, p={comp_results[2]['p_value']:.4f}")
    print(f"  Familiarity effect (selfref): d={comp_results[3]['cohens_d']:.3f}, p={comp_results[3]['p_value']:.4f}")
