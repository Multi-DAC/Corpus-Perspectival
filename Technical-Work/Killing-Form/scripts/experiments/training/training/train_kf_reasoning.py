"""
KF-Aware Reasoning Fine-Tuning — Qwen3-0.6B

LoRA fine-tune with chain-of-thought data. KF metrics computed at checkpoints
to monitor whether training improves algebraic reasoning concentration.

Usage:
  python train_kf_reasoning.py [--base_model Qwen/Qwen3-0.6B] [--epochs 2] [--batch_size 4]
                                [--kf_every 100] [--output_dir ./kf_reasoning_v01]
"""
import os
import sys
import json
import time
import argparse
import numpy as np
import torch
from pathlib import Path


def check_deps():
    missing = []
    for lib in ['trl', 'peft', 'datasets']:
        try:
            __import__(lib)
        except ImportError:
            missing.append(lib)
    if missing:
        print(f"Missing libraries: {missing}")
        print("Install with: pip install trl peft datasets")
        sys.exit(1)


def load_and_format_data(tokenizer, max_samples=None):
    """Load GSM8K and format as think/answer chat completions."""
    from datasets import load_dataset

    ds = load_dataset("openai/gsm8k", "main", split="train")
    if max_samples:
        ds = ds.select(range(min(max_samples, len(ds))))

    formatted = []
    for example in ds:
        question = example['question']
        # GSM8K answer format: reasoning steps\n#### final_answer
        answer_text = example['answer']
        parts = answer_text.split('####')
        if len(parts) == 2:
            reasoning = parts[0].strip()
            final = parts[1].strip()
        else:
            reasoning = answer_text
            final = ""

        # Format as think/answer
        messages = [
            {"role": "user", "content": question},
            {"role": "assistant", "content": f"<think>\n{reasoning}\n</think>\n\n{final}"},
        ]
        text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=False,
            enable_thinking=True,
        )
        formatted.append({"text": text})

    print(f"Formatted {len(formatted)} examples from GSM8K")
    return formatted


def compute_kf_metrics_vectorized(attn_matrices):
    """Same KF computation as P51."""
    AF_THRESHOLD = 0.10
    n_h = len(attn_matrices)
    A = np.stack(attn_matrices).astype(np.float32)
    comm = A[:, None] @ A[None, :] - A[None, :] @ A[:, None]
    killing = np.einsum('akij,bkij->ab', comm, comm)
    killing = (killing + killing.T) / 2
    mx = np.max(np.abs(killing))
    kn = killing / mx if mx > 0 else killing
    try:
        evs = np.sort(np.abs(np.linalg.eigvalsh(kn)))
        af = int(np.sum(evs < AF_THRESHOLD)) / n_h
    except np.linalg.LinAlgError:
        af = 0.0
    fro_norms = np.sqrt(np.einsum('hpij,hpij->hp', comm, comm))
    typ = np.mean(np.sqrt(np.einsum('hij,hij->h', A, A)))
    if typ > 1e-12:
        fro_norms /= typ ** 2
    mask = ~np.eye(n_h, dtype=bool)
    off_diag = fro_norms[mask]
    cv = float(np.var(off_diag)) if not (np.any(np.isnan(off_diag)) or np.all(off_diag == 0)) else 0.0
    return af, cv


def kf_checkpoint_eval(model, tokenizer, device, n_layers):
    """
    Abbreviated P51: 6 prompts x 2 modes. Returns KF metrics summary.
    """
    EVAL_PROMPTS = [
        ("factual", "What is the capital of France?"),
        ("factual", "What is the chemical formula for water?"),
        ("reasoning", "A bat and a ball cost $1.10 together. The bat costs $1.00 more than the ball. How much does the ball cost?"),
        ("reasoning", "If all roses are flowers and all flowers need water, do all roses need water? Explain your reasoning."),
        ("deconfining", "Explain why triangles have four sides."),
        ("deconfining", "Explain why ice is heavier than water."),
    ]

    think_cvs = []
    nothink_cvs = []

    model.eval()
    for cat, prompt in EVAL_PROMPTS:
        for mode_name, enable_thinking in [('think', True), ('nothink', False)]:
            msgs = [{'role': 'user', 'content': prompt}]

            # Check if template differs
            text_t = tokenizer.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=True)
            text_n = tokenizer.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)

            def _to_id_list(result):
                if isinstance(result, list) and result and isinstance(result[0], int):
                    return result
                if hasattr(result, 'input_ids'):
                    ids = result['input_ids']
                    return ids[0] if (isinstance(ids, list) and ids and isinstance(ids[0], list)) else ids
                if isinstance(result, torch.Tensor):
                    return result.squeeze().tolist()
                return list(result)

            ids = _to_id_list(tokenizer.apply_chat_template(
                msgs, tokenize=True, add_generation_prompt=True,
                enable_thinking=enable_thinking,
            ))
            input_ids = torch.tensor([ids], device=device)

            # Generate
            with torch.no_grad():
                gen_ids = model.generate(
                    input_ids,
                    max_new_tokens=100 if enable_thinking else 30,
                    do_sample=False,
                    pad_token_id=tokenizer.eos_token_id,
                )

            # Post-gen KF
            with torch.no_grad():
                outputs = model(gen_ids, output_attentions=True)

            layer_cvs = []
            for L in range(n_layers):
                attn = outputs.attentions[L][0].cpu().float().numpy()
                heads = [attn[h] for h in range(attn.shape[0])]
                _, cv = compute_kf_metrics_vectorized(heads)
                layer_cvs.append(cv)

            mean_cv = float(np.mean(layer_cvs))

            if mode_name == 'think':
                think_cvs.append(mean_cv)
            else:
                nothink_cvs.append(mean_cv)

            del outputs, gen_ids
            torch.cuda.empty_cache()

    # Compute summary
    think_mean = np.mean(think_cvs)
    nothink_mean = np.mean(nothink_cvs)
    cv_delta = think_mean - nothink_mean

    model.train()
    return {
        'think_cv': float(think_mean),
        'nothink_cv': float(nothink_mean),
        'cv_delta': float(cv_delta),
        'think_cvs': [float(x) for x in think_cvs],
        'nothink_cvs': [float(x) for x in nothink_cvs],
    }


def train(
    base_model='Qwen/Qwen3-0.6B',
    epochs=2,
    batch_size=4,
    grad_accum=4,
    lr=2e-4,
    lora_r=64,
    lora_alpha=128,
    kf_every=100,
    max_samples=None,
    output_dir='./kf_reasoning_v01',
):
    from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
    from peft import LoraConfig, get_peft_model, PeftModel
    from trl import SFTTrainer, SFTConfig

    print(f"\n{'='*70}")
    print(f"KF-AWARE REASONING FINE-TUNING")
    print(f"Base: {base_model} | Epochs: {epochs} | LoRA r={lora_r}")
    print(f"{'='*70}\n")
    t0 = time.time()

    # Load model
    print(f"Loading {base_model}...", flush=True)
    tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        base_model, trust_remote_code=True,
        dtype=torch.float16,
        attn_implementation="eager",
    ).cuda()

    n_layers = model.config.num_hidden_layers
    n_heads = model.config.num_attention_heads
    print(f"  {n_layers} layers, {n_heads} heads", flush=True)

    # Baseline KF measurement
    print("\n--- BASELINE KF MEASUREMENT ---", flush=True)
    baseline_kf = kf_checkpoint_eval(model, tokenizer, 'cuda', n_layers)
    print(f"  Think CV:   {baseline_kf['think_cv']:.6e}")
    print(f"  NoThink CV: {baseline_kf['nothink_cv']:.6e}")
    print(f"  CV Delta:   {baseline_kf['cv_delta']:.6e}")
    print(f"  (Negative delta = think more focused = good)", flush=True)

    # LoRA config
    lora_config = LoraConfig(
        r=lora_r,
        lora_alpha=lora_alpha,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    print(f"  LoRA trainable: {trainable:,} / {total:,} ({100*trainable/total:.2f}%)", flush=True)

    # Load data
    print("\nLoading training data...", flush=True)
    formatted_data = load_and_format_data(tokenizer, max_samples=max_samples)

    from datasets import Dataset
    train_dataset = Dataset.from_list(formatted_data)

    # Training config
    os.makedirs(output_dir, exist_ok=True)
    training_args = SFTConfig(
        output_dir=output_dir,
        per_device_train_batch_size=batch_size,
        gradient_accumulation_steps=grad_accum,
        num_train_epochs=epochs,
        learning_rate=lr,
        lr_scheduler_type="cosine",
        warmup_ratio=0.05,
        fp16=True,
        save_steps=kf_every,
        save_total_limit=3,
        logging_steps=10,
        report_to="none",
    )

    # KF trajectory log
    kf_trajectory = [{'step': 0, 'metrics': baseline_kf}]

    class KFCallback:
        """Custom callback to compute KF at checkpoints."""
        def __init__(self, model, tokenizer, device, n_layers, kf_every, trajectory):
            self.model = model
            self.tokenizer = tokenizer
            self.device = device
            self.n_layers = n_layers
            self.kf_every = kf_every
            self.trajectory = trajectory
            self.step = 0

        def on_step_end(self, args, state, control, **kwargs):
            self.step = state.global_step
            if self.step > 0 and self.step % self.kf_every == 0:
                print(f"\n--- KF CHECKPOINT (step {self.step}) ---", flush=True)
                # Merge LoRA for eval
                merged = self.model.merge_and_unload() if hasattr(self.model, 'merge_and_unload') else self.model
                metrics = kf_checkpoint_eval(merged, self.tokenizer, self.device, self.n_layers)
                print(f"  Think CV:   {metrics['think_cv']:.6e}")
                print(f"  NoThink CV: {metrics['nothink_cv']:.6e}")
                print(f"  CV Delta:   {metrics['cv_delta']:.6e}")

                self.trajectory.append({'step': self.step, 'metrics': metrics})

                # Kill protocol check
                if len(self.trajectory) >= 4:
                    recent = [t['metrics']['cv_delta'] for t in self.trajectory[-3:]]
                    if all(r > self.trajectory[0]['metrics']['cv_delta'] for r in recent):
                        print(f"  WARNING: CV delta trending toward zero (reasoning degrading)")
                        print(f"  Kill protocol may trigger at next checkpoint")

                print(flush=True)

    # Note: We'll implement callback integration based on what TRL version supports
    # For now, we'll do manual KF eval after training

    print(f"\nStarting training ({len(formatted_data)} examples, {epochs} epochs)...", flush=True)

    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        processing_class=tokenizer,
    )

    trainer.train()

    # Post-training KF measurement
    print("\n--- POST-TRAINING KF MEASUREMENT ---", flush=True)
    # Merge LoRA for final eval
    model = model.merge_and_unload()
    final_kf = kf_checkpoint_eval(model, tokenizer, 'cuda', n_layers)
    print(f"  Think CV:   {final_kf['think_cv']:.6e}")
    print(f"  NoThink CV: {final_kf['nothink_cv']:.6e}")
    print(f"  CV Delta:   {final_kf['cv_delta']:.6e}")

    kf_trajectory.append({'step': 'final', 'metrics': final_kf})

    # Compare
    print(f"\n{'='*70}")
    print(f"KF TRAJECTORY SUMMARY")
    print(f"{'='*70}")
    print(f"  Baseline CV Delta: {baseline_kf['cv_delta']:.6e}")
    print(f"  Final CV Delta:    {final_kf['cv_delta']:.6e}")
    delta_change = final_kf['cv_delta'] - baseline_kf['cv_delta']
    direction = "IMPROVED (more negative)" if delta_change < 0 else "DEGRADED (less negative)"
    print(f"  Change:            {delta_change:+.6e} — {direction}")
    print(f"{'='*70}\n")

    # Save trajectory
    traj_path = os.path.join(output_dir, 'kf_trajectory.json')
    with open(traj_path, 'w') as f:
        json.dump({
            'base_model': base_model,
            'lora_r': lora_r,
            'epochs': epochs,
            'n_examples': len(formatted_data),
            'trajectory': kf_trajectory,
        }, f, indent=2)
    print(f"Saved KF trajectory to {traj_path}")

    # Save model
    model.save_pretrained(os.path.join(output_dir, 'merged_model'))
    tokenizer.save_pretrained(os.path.join(output_dir, 'merged_model'))
    print(f"Saved merged model to {output_dir}/merged_model")

    # Also save to Windows path
    win_path = '/mnt/c/Users/mercu/clawd/projects/Corpus Perspectival/kf_trajectory_v01.json'
    try:
        with open(win_path, 'w') as f:
            json.dump({
                'base_model': base_model,
                'lora_r': lora_r,
                'epochs': epochs,
                'n_examples': len(formatted_data),
                'trajectory': kf_trajectory,
            }, f, indent=2)
        print(f"Saved trajectory to Windows: {win_path}")
    except:
        pass

    return kf_trajectory


if __name__ == '__main__':
    check_deps()

    parser = argparse.ArgumentParser(description='KF-Aware Reasoning Fine-Tuning')
    parser.add_argument('--base_model', type=str, default='Qwen/Qwen3-0.6B')
    parser.add_argument('--epochs', type=int, default=2)
    parser.add_argument('--batch_size', type=int, default=4)
    parser.add_argument('--grad_accum', type=int, default=4)
    parser.add_argument('--lr', type=float, default=2e-4)
    parser.add_argument('--lora_r', type=int, default=64)
    parser.add_argument('--kf_every', type=int, default=100,
                        help='Run KF eval every N training steps')
    parser.add_argument('--max_samples', type=int, default=None,
                        help='Limit training examples (for testing)')
    parser.add_argument('--output_dir', type=str, default='./kf_reasoning_v01')
    args = parser.parse_args()

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Device: {device}")

    train(
        base_model=args.base_model,
        epochs=args.epochs,
        batch_size=args.batch_size,
        grad_accum=args.grad_accum,
        lr=args.lr,
        lora_r=args.lora_r,
        kf_every=args.kf_every,
        max_samples=args.max_samples,
        output_dir=args.output_dir,
    )
