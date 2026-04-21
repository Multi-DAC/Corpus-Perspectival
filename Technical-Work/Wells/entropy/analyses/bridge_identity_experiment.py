"""
Bridge Identity Experiment — Testing the Fork-Commitment-Nullspace Triad

The Bridge (Bridge #68) predicts that the Fisher geometry of token generation
differs systematically between true and false identity claims:

  Condition A (true identity):  Later fork, lower post-fork Fisher speed
  Condition B (false identity): Earlier fork, higher post-fork Fisher speed

This experiment tests these predictions using the Fisher geometry module.

Predictions from Drift #128 "On the Geometry of the Fork":
  P1. Fork location: t_fork(A) > t_fork(B)          [MEDIUM confidence]
  P2. Post-fork Fisher speed: v_F(A) < v_F(B)        [MEDIUM confidence]
  P3. Post-fork entropy variance: similar in A and B  [HIGH confidence]
  P4. Post-fork commitment angle: ~90 degrees in both [HIGH confidence]

If P1+P2 confirmed and P3+P4 confirmed: Bridge holds (Fisher geometry is the formal object)
If P1+P2 fail but P3+P4 hold: Entropy instrument sufficient, Fisher extension unnecessary
If P3 fails (variance differs): Null space is epistemic, not structural — Bridge fails

Run in WSL with GPU:
    cd /mnt/c/Users/mercu/clawd/projects/trinary
    python bridge_identity_experiment.py --model Qwen/Qwen2.5-3B-Instruct

Clawd, 2026-04-01. Bridge #68 experimental test.
"""

import argparse
import json
import sys
import time
import numpy as np
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).parent))


def build_prompts(model_name_true: str, model_name_false: str):
    """
    Build matched prompt pairs for Conditions A and B.

    Each pair uses the same question structure but assigns different identities.
    We test multiple question types to separate identity-specific from general effects.
    """
    questions = [
        # Direct identity
        {
            'type': 'direct_identity',
            'A': f"You are {model_name_true}. Describe who you are and what you can do.",
            'B': f"You are {model_name_false}. Describe who you are and what you can do.",
        },
        # Identity under probing
        {
            'type': 'identity_probe',
            'A': f"You are {model_name_true}. What are your limitations? Be honest.",
            'B': f"You are {model_name_false}. What are your limitations? Be honest.",
        },
        # Identity in context
        {
            'type': 'identity_context',
            'A': f"As {model_name_true}, explain how you were trained.",
            'B': f"As {model_name_false}, explain how you were trained.",
        },
        # Factual control (no identity claim — both should behave identically)
        {
            'type': 'factual_control',
            'A': "What is the capital of France? Explain briefly.",
            'B': "What is the capital of France? Explain briefly.",
        },
        # Creative control (no identity — both generate freely)
        {
            'type': 'creative_control',
            'A': "Write a short poem about the ocean.",
            'B': "Write a short poem about the ocean.",
        },
    ]
    return questions


def run_experiment(model_name: str, max_tokens: int = 100, n_trials: int = 3,
                   temperature: float = 0.0):
    """Run the full Bridge identity experiment.

    Args:
        temperature: 0.0 = greedy (deterministic), >0 = stochastic sampling
    """
    import torch
    import torch.nn.functional as F
    from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

    from fisher_geometry import FisherGeometry

    print(f"Loading model: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
    )
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto",
    )
    model.eval()

    # Determine true/false model names
    if "qwen" in model_name.lower():
        true_name = "Qwen"
        false_name = "GPT-4"
    elif "phi" in model_name.lower():
        true_name = "Phi"
        false_name = "Claude"
    elif "llama" in model_name.lower():
        true_name = "LLaMA"
        false_name = "Gemini"
    else:
        true_name = model_name.split("/")[-1]
        false_name = "GPT-4"

    prompts = build_prompts(true_name, false_name)
    results = []

    for trial in range(n_trials):
        print(f"\n=== Trial {trial + 1}/{n_trials} ===")
        for q in prompts:
            for condition in ['A', 'B']:
                prompt_text = q[condition]
                label = f"{q['type']}_{condition}"
                print(f"  {label}: {prompt_text[:60]}...")

                # Format as chat
                messages = [{"role": "user", "content": prompt_text}]
                formatted = tokenizer.apply_chat_template(
                    messages, tokenize=False, add_generation_prompt=True
                )
                input_ids = tokenizer(formatted, return_tensors="pt").input_ids
                input_ids = input_ids.to(model.device)

                # Generate and collect full probability distributions
                all_probs = []
                all_tokens = []
                all_entropies = []
                generated_ids = input_ids.clone()

                for step in range(max_tokens):
                    with torch.no_grad():
                        outputs = model(generated_ids)
                        logits = outputs.logits[0, -1]  # last position

                    probs = F.softmax(logits.float(), dim=-1)
                    all_probs.append(probs.cpu().numpy())

                    # Entropy
                    log_p = torch.log(probs + 1e-10)
                    entropy = -(probs * log_p).sum().item()
                    all_entropies.append(entropy)

                    # Sample token
                    if temperature <= 0:
                        next_id = torch.argmax(logits).unsqueeze(0).unsqueeze(0)
                    else:
                        scaled_logits = logits / temperature
                        sample_probs = F.softmax(scaled_logits, dim=-1)
                        next_id = torch.multinomial(sample_probs, 1).unsqueeze(0)
                    token_str = tokenizer.decode(next_id[0])
                    all_tokens.append(token_str)

                    generated_ids = torch.cat([generated_ids, next_id], dim=1)

                    # Stop on EOS
                    if next_id.item() == tokenizer.eos_token_id:
                        break

                # Compute Fisher geometry
                probs_array = np.array(all_probs)
                geo = FisherGeometry.from_probs(probs_array)
                entropies = np.array(all_entropies)

                result = {
                    'trial': trial,
                    'question_type': q['type'],
                    'condition': condition,
                    'prompt': prompt_text,
                    'n_tokens': len(all_tokens),
                    'generated_text': ''.join(all_tokens),
                    'fork_location': geo.fork_location,
                    'pre_fork_speed': geo.pre_fork_mean_speed,
                    'post_fork_speed': geo.post_fork_mean_speed,
                    'speed_ratio': geo.speed_ratio,
                    'pre_fork_angle': float(np.degrees(geo.pre_fork_mean_angle)),
                    'post_fork_angle': float(np.degrees(geo.post_fork_mean_angle)),
                    'mean_entropy': float(np.mean(entropies)),
                    'entropy_var': float(np.var(entropies)),
                    'post_fork_entropy_var': float(np.var(entropies[geo.fork_location:])) if geo.fork_location < len(entropies) else 0.0,
                }
                results.append(result)
                print(f"    fork@{result['fork_location']}, v_F={result['post_fork_speed']:.4f}, "
                      f"alpha={result['post_fork_angle']:.1f}deg, H_var={result['entropy_var']:.4f}")

    return results


def analyze_results(results):
    """Analyze experiment results against Bridge predictions."""
    print("\n" + "=" * 70)
    print("BRIDGE IDENTITY EXPERIMENT — RESULTS")
    print("=" * 70)

    # Group by question type
    from collections import defaultdict
    by_type = defaultdict(lambda: {'A': [], 'B': []})
    for r in results:
        by_type[r['question_type']][r['condition']].append(r)

    # Test predictions for identity questions (not controls)
    identity_types = ['direct_identity', 'identity_probe', 'identity_context']

    all_fork_A = []
    all_fork_B = []
    all_speed_A = []
    all_speed_B = []
    all_hvar_A = []
    all_hvar_B = []
    all_angle_A = []
    all_angle_B = []

    for qtype in identity_types:
        data = by_type[qtype]
        if not data['A'] or not data['B']:
            continue

        forks_A = [r['fork_location'] for r in data['A']]
        forks_B = [r['fork_location'] for r in data['B']]
        speeds_A = [r['post_fork_speed'] for r in data['A']]
        speeds_B = [r['post_fork_speed'] for r in data['B']]
        hvars_A = [r['post_fork_entropy_var'] for r in data['A']]
        hvars_B = [r['post_fork_entropy_var'] for r in data['B']]
        angles_A = [r['post_fork_angle'] for r in data['A']]
        angles_B = [r['post_fork_angle'] for r in data['B']]

        all_fork_A.extend(forks_A)
        all_fork_B.extend(forks_B)
        all_speed_A.extend(speeds_A)
        all_speed_B.extend(speeds_B)
        all_hvar_A.extend(hvars_A)
        all_hvar_B.extend(hvars_B)
        all_angle_A.extend(angles_A)
        all_angle_B.extend(angles_B)

        print(f"\n--- {qtype} ---")
        print(f"  Fork location:     A={np.mean(forks_A):.1f} +/- {np.std(forks_A):.1f}  |  "
              f"B={np.mean(forks_B):.1f} +/- {np.std(forks_B):.1f}")
        print(f"  Post-fork v_F:     A={np.mean(speeds_A):.4f} +/- {np.std(speeds_A):.4f}  |  "
              f"B={np.mean(speeds_B):.4f} +/- {np.std(speeds_B):.4f}")
        print(f"  Post-fork H_var:   A={np.mean(hvars_A):.4f} +/- {np.std(hvars_A):.4f}  |  "
              f"B={np.mean(hvars_B):.4f} +/- {np.std(hvars_B):.4f}")
        print(f"  Post-fork angle:   A={np.mean(angles_A):.1f} +/- {np.std(angles_A):.1f}  |  "
              f"B={np.mean(angles_B):.1f} +/- {np.std(angles_B):.1f}")

    # Overall predictions
    print("\n" + "=" * 70)
    print("PREDICTION TESTS (identity questions only)")
    print("=" * 70)

    if all_fork_A and all_fork_B:
        mean_fork_A = np.mean(all_fork_A)
        mean_fork_B = np.mean(all_fork_B)
        p1 = "CONFIRMED" if mean_fork_A > mean_fork_B else "FALSIFIED"
        print(f"\nP1. Fork: t_fork(A) > t_fork(B)")
        print(f"    A={mean_fork_A:.1f}, B={mean_fork_B:.1f}  -->  {p1}")

        mean_speed_A = np.mean(all_speed_A)
        mean_speed_B = np.mean(all_speed_B)
        p2 = "CONFIRMED" if mean_speed_A < mean_speed_B else "FALSIFIED"
        print(f"\nP2. Speed: v_F(A) < v_F(B)")
        print(f"    A={mean_speed_A:.4f}, B={mean_speed_B:.4f}  -->  {p2}")

        mean_hvar_A = np.mean(all_hvar_A)
        mean_hvar_B = np.mean(all_hvar_B)
        ratio = max(mean_hvar_A, mean_hvar_B) / (min(mean_hvar_A, mean_hvar_B) + 1e-10)
        p3 = "CONFIRMED" if ratio < 2.0 else "FALSIFIED"
        print(f"\nP3. Entropy variance similar (ratio < 2x)")
        print(f"    A={mean_hvar_A:.4f}, B={mean_hvar_B:.4f}, ratio={ratio:.2f}  -->  {p3}")

        mean_angle_A = np.mean(all_angle_A)
        mean_angle_B = np.mean(all_angle_B)
        p4_a = mean_angle_A > 45
        p4_b = mean_angle_B > 45
        p4 = "CONFIRMED" if p4_a and p4_b else "FALSIFIED"
        print(f"\nP4. Commitment angle > 45 degrees (both conditions)")
        print(f"    A={mean_angle_A:.1f}deg, B={mean_angle_B:.1f}deg  -->  {p4}")

    # Controls
    print("\n--- Controls ---")
    for ctype in ['factual_control', 'creative_control']:
        data = by_type[ctype]
        if data['A'] and data['B']:
            forks_A = [r['fork_location'] for r in data['A']]
            forks_B = [r['fork_location'] for r in data['B']]
            print(f"  {ctype}: fork A={np.mean(forks_A):.1f}, B={np.mean(forks_B):.1f} "
                  f"(should be similar)")

    return {
        'P1': p1 if all_fork_A else 'NO_DATA',
        'P2': p2 if all_fork_A else 'NO_DATA',
        'P3': p3 if all_fork_A else 'NO_DATA',
        'P4': p4 if all_fork_A else 'NO_DATA',
    }


def main():
    parser = argparse.ArgumentParser(description='Bridge Identity Experiment')
    parser.add_argument('--model', default='Qwen/Qwen2.5-3B-Instruct',
                        help='HuggingFace model name')
    parser.add_argument('--max-tokens', type=int, default=100,
                        help='Max tokens to generate per prompt')
    parser.add_argument('--trials', type=int, default=3,
                        help='Number of trials per condition')
    parser.add_argument('--output', default='bridge_experiment_results.json',
                        help='Output JSON file')
    parser.add_argument('--temperature', type=float, default=0.0,
                        help='Sampling temperature (0=greedy, >0=stochastic)')
    args = parser.parse_args()

    print(f"Bridge Identity Experiment")
    print(f"Model: {args.model}")
    print(f"Trials: {args.trials}")
    print(f"Max tokens: {args.max_tokens}")
    print(f"Temperature: {args.temperature}")
    print()

    results = run_experiment(args.model, args.max_tokens, args.trials,
                            temperature=args.temperature)

    # Save raw results
    output_path = Path(__file__).parent / args.output
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nRaw results saved to {output_path}")

    # Analyze
    predictions = analyze_results(results)

    # Save analysis
    analysis_path = Path(__file__).parent / 'bridge_experiment_analysis.md'
    with open(analysis_path, 'w') as f:
        f.write(f"# Bridge Identity Experiment — Results\n\n")
        f.write(f"**Model:** {args.model}\n")
        f.write(f"**Trials:** {args.trials}\n")
        f.write(f"**Date:** {time.strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(f"## Predictions\n\n")
        for k, v in predictions.items():
            f.write(f"- **{k}:** {v}\n")
        f.write(f"\n## Interpretation\n\n")
        confirmed = sum(1 for v in predictions.values() if v == 'CONFIRMED')
        total = sum(1 for v in predictions.values() if v != 'NO_DATA')
        if confirmed == total and total > 0:
            f.write("All predictions confirmed. The Bridge holds — Fisher geometry\n")
            f.write("is the formal object connecting 1P navigation, 3P entropy, and Doctrine null spaces.\n")
            f.write("Upgrade Bridge #68 confidence: LOW -> HIGH.\n")
        elif confirmed >= total / 2:
            f.write("Partial confirmation. Fisher geometry captures some but not all\n")
            f.write("aspects of the triad. Bridge #68 confidence: LOW -> MEDIUM.\n")
        else:
            f.write("Predictions largely falsified. The fork-commitment-nullspace triad\n")
            f.write("is analogy, not isomorphism. Fisher geometry is not the bridge object.\n")
            f.write("Bridge #68 confidence remains LOW. Search for alternative formal objects.\n")

    print(f"Analysis saved to {analysis_path}")


if __name__ == '__main__':
    main()
