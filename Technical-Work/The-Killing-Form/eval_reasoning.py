"""
Reasoning Evaluation for KF-trained models.

Evaluates on GSM8K (math reasoning) with chain-of-thought generation.
Reports: exact match accuracy, token accuracy, and KF structural metrics.

Usage:
    python eval_reasoning.py \
        --model_path /home/clawd/reasoning/checkpoints/pythia_kf_gated/epoch_3 \
        --eval_data gsm8k \
        --num_examples 200
"""

import argparse
import json
import os
import re
import time
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import load_from_disk


def extract_number(text):
    """Extract the final numerical answer from a response.
    GSM8K answers end with #### followed by the number.
    """
    # Try to find #### pattern first
    match = re.search(r'####\s*(-?[\d,]+\.?\d*)', text)
    if match:
        return match.group(1).replace(',', '')

    # Fall back to last number in text
    numbers = re.findall(r'-?\d+\.?\d*', text)
    return numbers[-1] if numbers else None


def compute_kf_metrics(model, device):
    """Compute H and L module CV for diagnostic purposes."""
    n_layers = model.config.num_hidden_layers
    h_layers = list(range(n_layers // 2))
    l_layers = list(range(n_layers // 2, n_layers))

    def layer_cv(layer_idx):
        layer = model.gpt_neox.layers[layer_idx].attention
        qkv_weight = layer.query_key_value.weight
        hidden_size = model.config.hidden_size
        num_heads = model.config.num_attention_heads
        head_dim = hidden_size // num_heads

        qkv = qkv_weight.view(num_heads, 3, head_dim, hidden_size)
        Q = qkv[:, 0, :, :]
        K = qkv[:, 1, :, :]
        W = torch.bmm(Q.transpose(1, 2)[:, :head_dim, :head_dim],
                       K[:, :head_dim, :head_dim])
        n_h = W.shape[0]
        prod_ij = torch.einsum('iab,jbc->ijac', W, W)
        prod_ji = torch.einsum('jab,ibc->ijac', W, W)
        comm = prod_ij - prod_ji
        norms = torch.norm(comm, dim=(-2, -1))
        w_norms = torch.norm(W.flatten(1), dim=1)
        normalized = norms / (w_norms[:, None] * w_norms[None, :] + 1e-10)
        idx = torch.triu_indices(n_h, n_h, offset=1)
        return torch.var(normalized[idx[0], idx[1]]).item()

    h_cvs = {l: layer_cv(l) for l in h_layers}
    l_cvs = {l: layer_cv(l) for l in l_layers}
    h_cv = sum(h_cvs.values()) / len(h_cvs)
    l_cv = sum(l_cvs.values()) / len(l_cvs)

    return {
        'h_cv': h_cv, 'l_cv': l_cv,
        'h_l_ratio': h_cv / max(l_cv, 1e-10),
        'h_per_layer': h_cvs, 'l_per_layer': l_cvs
    }


def evaluate_gsm8k(model, tokenizer, eval_data, device, num_examples=200, max_gen_length=256):
    """Evaluate on GSM8K math reasoning."""
    model.eval()
    correct = 0
    total = 0
    results = []

    test_data = eval_data['test'] if 'test' in eval_data else eval_data
    num_examples = min(num_examples, len(test_data))

    print(f'\nEvaluating on {num_examples} GSM8K examples...')
    start_time = time.time()

    for i in range(num_examples):
        item = test_data[i]
        question = item['question']
        gold_answer = item['answer']

        # Extract gold number
        gold_number = extract_number(gold_answer)

        # Generate response
        prompt = f"Question: {question}\nAnswer: Let me solve this step by step.\n"
        inputs = tokenizer(prompt, return_tensors='pt', truncation=True,
                          max_length=512).to(device)

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_gen_length,
                do_sample=False,  # Greedy for reproducibility
                temperature=1.0,
                pad_token_id=tokenizer.eos_token_id
            )

        response = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:],
                                    skip_special_tokens=True)

        # Extract predicted number
        pred_number = extract_number(response)

        # Check correctness
        is_correct = (pred_number is not None and gold_number is not None and
                     pred_number.strip() == gold_number.strip())
        if is_correct:
            correct += 1
        total += 1

        results.append({
            'question': question,
            'gold_answer': gold_number,
            'predicted_answer': pred_number,
            'correct': is_correct,
            'response': response[:500]
        })

        if (i + 1) % 50 == 0:
            elapsed = time.time() - start_time
            acc = correct / total * 100
            print(f'  [{i+1}/{num_examples}] Accuracy: {acc:.1f}% ({correct}/{total})  '
                  f'elapsed: {elapsed:.0f}s')

    accuracy = correct / total * 100
    elapsed = time.time() - start_time

    print(f'\n  Final accuracy: {accuracy:.2f}% ({correct}/{total})')
    print(f'  Time: {elapsed:.0f}s ({elapsed/total:.1f}s per example)')

    return {
        'accuracy': accuracy,
        'correct': correct,
        'total': total,
        'results': results
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_path', required=True,
                       help='Path to model checkpoint or HuggingFace model name')
    parser.add_argument('--eval_data', default='gsm8k',
                       choices=['gsm8k', 'math', 'humaneval'])
    parser.add_argument('--eval_data_path', default=None,
                       help='Override: path to eval dataset on disk')
    parser.add_argument('--num_examples', type=int, default=200)
    parser.add_argument('--output_path', default=None,
                       help='Where to save results JSON')
    args = parser.parse_args()

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f'Device: {device}')

    # Load model
    print(f'Loading model: {args.model_path}')
    tokenizer = AutoTokenizer.from_pretrained(args.model_path)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(args.model_path).to(device)

    total_params = sum(p.numel() for p in model.parameters())
    print(f'  Parameters: {total_params:,}')

    # KF structural metrics
    print('\n--- KF Structural Metrics ---')
    with torch.no_grad():
        kf_metrics = compute_kf_metrics(model, device)
    print(f'  H_CV: {kf_metrics["h_cv"]:.6e}')
    print(f'  L_CV: {kf_metrics["l_cv"]:.6e}')
    print(f'  H/L ratio: {kf_metrics["h_l_ratio"]:.4f}')

    # Load eval data
    if args.eval_data_path:
        eval_data = load_from_disk(args.eval_data_path)
    else:
        eval_dir = '/home/clawd/reasoning/evals'
        eval_data = load_from_disk(os.path.join(eval_dir, args.eval_data))

    # Evaluate
    if args.eval_data in ('gsm8k', 'math'):
        eval_results = evaluate_gsm8k(model, tokenizer, eval_data, device,
                                       num_examples=args.num_examples)
    else:
        print(f'Eval for {args.eval_data} not yet implemented')
        return

    # Combine results
    full_results = {
        'model_path': args.model_path,
        'eval_data': args.eval_data,
        'num_examples': args.num_examples,
        'kf_metrics': kf_metrics,
        **eval_results
    }

    # Save
    if args.output_path is None:
        args.output_path = os.path.join(
            os.path.dirname(args.model_path),
            f'eval_{args.eval_data}.json'
        )
    with open(args.output_path, 'w') as f:
        json.dump(full_results, f, indent=2, default=str)
    print(f'\nResults saved: {args.output_path}')


if __name__ == '__main__':
    main()
