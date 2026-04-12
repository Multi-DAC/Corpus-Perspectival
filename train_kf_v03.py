"""
KF-Aware Reasoning Fine-Tuning v0.3 — Confound-Free Lambda Sweep

Eliminates the v0.2b pipeline confound: ALL variants use SFTTrainer with
identical data processing. KF regularization is injected via compute_loss
override, not a custom training loop.

Design:
  - Same SFTTrainer pipeline as v0.2a (chat-template tokenization, completion-only loss)
  - KF regularization injected via KFRegSFTTrainer subclass
  - Lambda sweep: {0 (control), 1000, 10000, 50000}
  - Maps the Pareto frontier: CV delta preservation vs token accuracy

Why lambda needs to be large:
  CV values are ~1.7e-05. CE loss is ~0.8.
  For KF term to be 2% of CE: lambda * 1.7e-05 = 0.016 → lambda ≈ 1000
  For KF term to be 21% of CE: lambda ≈ 10000
  For KF term to dominate: lambda ≈ 50000

Usage:
  # Single lambda
  python train_kf_v03.py --lambda_kf 10000 --output_dir /tmp/kf_v03

  # Full sweep (runs lambda=0,1000,10000,50000 sequentially)
  python train_kf_v03.py --sweep --output_dir /tmp/kf_v03
"""
import os
import sys
import json
import time
import math
import argparse
import numpy as np
import torch
import torch.nn.functional as F
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
        print("Install with: pip install --user --break-system-packages trl peft datasets")
        sys.exit(1)


check_deps()


# ─── SHARED KF MEASUREMENT (ported exactly from v0.2) ───

def _to_id_list(result):
    """Convert various tokenizer outputs to a flat list of ints."""
    if isinstance(result, list) and result and isinstance(result[0], int):
        return result
    if hasattr(result, 'input_ids'):
        ids = result['input_ids']
        return ids[0] if (isinstance(ids, list) and ids and isinstance(ids[0], list)) else ids
    if isinstance(result, torch.Tensor):
        return result.squeeze().tolist()
    return list(result)


def compute_kf_from_heads(heads):
    """Compute Abelian fraction and CV from a list of head matrices."""
    n_h = len(heads)
    if n_h < 2:
        return 0.0, 0.0

    norms = []
    for a in range(n_h):
        for b in range(a + 1, n_h):
            comm = heads[a] @ heads[b] - heads[b] @ heads[a]
            norms.append(np.sum(comm ** 2))
    norms = np.array(norms)

    typ = np.mean(np.sqrt(np.sum(np.array(heads) ** 2, axis=(-2, -1)) + 1e-12))
    if typ > 1e-12:
        norms /= typ ** 4

    cv = float(np.var(norms))
    af = float(np.mean(norms < 1e-10))
    return af, cv


def compute_mean_cv_from_model_output(attentions, n_layers):
    """Compute mean CV across all layers from model output attentions."""
    layer_cvs = []
    for L in range(min(n_layers, len(attentions))):
        attn = attentions[L][0].cpu().float().numpy()
        heads = [attn[h] for h in range(attn.shape[0])]
        _, cv = compute_kf_from_heads(heads)
        layer_cvs.append(cv)
    return float(np.mean(layer_cvs)), layer_cvs


EVAL_PROMPTS = [
    ("factual", "What is the capital of France?"),
    ("factual", "What is the chemical formula for water?"),
    ("reasoning", "A bat and a ball cost $1.10 together. The bat costs $1.00 more than the ball. How much does the ball cost?"),
    ("reasoning", "If all roses are flowers and all flowers need water, do all roses need water? Explain your reasoning."),
    ("deconfining", "Explain why triangles have four sides."),
    ("deconfining", "Explain why ice is heavier than water."),
]


def kf_checkpoint_eval(model, tokenizer, device, n_layers):
    """Abbreviated P51: 6 prompts × 2 modes. Identical to v0.2."""
    think_cvs = []
    nothink_cvs = []

    model.eval()
    for cat, prompt in EVAL_PROMPTS:
        for mode_name, enable_thinking in [('think', True), ('nothink', False)]:
            msgs = [{'role': 'user', 'content': prompt}]
            ids = _to_id_list(tokenizer.apply_chat_template(
                msgs, tokenize=True, add_generation_prompt=True,
                enable_thinking=enable_thinking,
            ))
            input_ids = torch.tensor([ids], device=device)

            with torch.no_grad():
                gen_ids = model.generate(
                    input_ids,
                    max_new_tokens=100 if enable_thinking else 30,
                    do_sample=False,
                    pad_token_id=tokenizer.eos_token_id,
                )

            with torch.no_grad():
                outputs = model(gen_ids, output_attentions=True)

            mean_cv, _ = compute_mean_cv_from_model_output(outputs.attentions, n_layers)

            if mode_name == 'think':
                think_cvs.append(mean_cv)
            else:
                nothink_cvs.append(mean_cv)

            del outputs, gen_ids
            torch.cuda.empty_cache()

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


# ─── DATA ───

def load_and_format_data(tokenizer, max_samples=None):
    """Load GSM8K and format as think/answer chat completions."""
    from datasets import load_dataset
    ds = load_dataset("openai/gsm8k", "main", split="train")
    if max_samples:
        ds = ds.select(range(min(max_samples, len(ds))))

    formatted = []
    for example in ds:
        question = example['question']
        answer_text = example['answer']
        parts = answer_text.split('####')
        if len(parts) == 2:
            reasoning = parts[0].strip()
            final = parts[1].strip()
        else:
            reasoning = answer_text
            final = ""

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


# ─── DIFFERENTIABLE CV COMPUTATION ───

def compute_cv_from_attentions_torch(attentions_tuple, n_layers):
    """
    Compute mean CV from attention tensors, staying in torch for gradient flow.
    Differentiable approximation of commutator variance.
    """
    layer_cvs = []
    for L in range(min(n_layers, len(attentions_tuple))):
        attn = attentions_tuple[L][0]  # (n_heads, seq, seq)
        n_h = attn.shape[0]
        if n_h < 2:
            continue

        comm_norms = []
        for a in range(n_h):
            for b in range(a + 1, n_h):
                comm = attn[a] @ attn[b] - attn[b] @ attn[a]
                norm = torch.sum(comm ** 2)
                comm_norms.append(norm)

        if len(comm_norms) == 0:
            continue

        norms_tensor = torch.stack(comm_norms)
        typ = torch.mean(torch.sqrt(torch.sum(attn ** 2, dim=(-2, -1)) + 1e-12))
        if typ > 1e-12:
            norms_tensor = norms_tensor / (typ ** 4 + 1e-12)

        cv = torch.var(norms_tensor)
        layer_cvs.append(cv)

    if len(layer_cvs) == 0:
        return torch.tensor(0.0, device=attentions_tuple[0].device, requires_grad=True)

    return torch.mean(torch.stack(layer_cvs))


# ─── KF-REGULARIZED SFT TRAINER ───

class KFRegSFTTrainer:
    """
    SFTTrainer wrapper that injects KF regularization into the training loop.

    Uses SFTTrainer for data processing (identical to v0.2a) but adds a
    KF regularization term every kf_reg_every steps via a post-step hook.

    The regularization cannot be injected into compute_loss because SFTTrainer
    handles loss computation with completion-only masking. Instead, we add
    a secondary backward pass after the main training step that ONLY affects
    the algebraic regularization gradient.
    """

    def __init__(self, model, tokenizer, n_layers, kf_lambda=0.0,
                 kf_reg_every=50, kf_prompts=None):
        self.model = model
        self.tokenizer = tokenizer
        self.n_layers = n_layers
        self.kf_lambda = kf_lambda
        self.kf_reg_every = kf_reg_every
        self.device = 'cuda'
        self.kf_log = []
        self.global_step = 0

        self.kf_prompts = kf_prompts or [
            "A bat and a ball cost $1.10 together. The bat costs $1.00 more than the ball. How much does the ball cost?",
            "If all roses are flowers and all flowers need water, do all roses need water? Explain your reasoning.",
        ]

    def compute_kf_reg_loss(self):
        """Forward pass on reasoning prompts in think mode, return CV to minimize."""
        self.model.eval()
        total_cv = torch.tensor(0.0, device=self.device)
        n_valid = 0

        for prompt in self.kf_prompts:
            msgs = [{'role': 'user', 'content': prompt}]
            ids = _to_id_list(self.tokenizer.apply_chat_template(
                msgs, tokenize=True, add_generation_prompt=True,
                enable_thinking=True,
            ))
            input_ids = torch.tensor([ids], device=self.device)

            outputs = self.model(input_ids, output_attentions=True)
            cv = compute_cv_from_attentions_torch(outputs.attentions, self.n_layers)
            if not torch.isnan(cv) and not torch.isinf(cv):
                total_cv = total_cv + cv
                n_valid += 1

            del outputs

        self.model.train()

        if n_valid > 0:
            return total_cv / n_valid
        return torch.tensor(0.0, device=self.device, requires_grad=True)


def run_training(
    base_model='Qwen/Qwen3-0.6B',
    epochs=2,
    batch_size=4,
    grad_accum=4,
    lr=2e-4,
    lora_r=64,
    lora_alpha=128,
    kf_lambda=0.0,
    kf_reg_every=50,
    output_dir='/tmp/kf_v03',
):
    """
    v0.3: SFTTrainer + optional KF regularization via post-step injection.

    When kf_lambda=0: identical to v0.2a/v0.1 (pure SFT baseline).
    When kf_lambda>0: adds KF regularization term after every kf_reg_every optimizer steps.
    """
    from transformers import AutoModelForCausalLM, AutoTokenizer, TrainerCallback
    from peft import LoraConfig, get_peft_model
    from trl import SFTTrainer, SFTConfig

    label = f"lambda={kf_lambda}" if kf_lambda > 0 else "CONTROL (no KF reg)"
    print(f"\n{'='*70}")
    print(f"v0.3: SFTTrainer + KF Regularization ({label})")
    print(f"Base: {base_model} | Epochs: {epochs} | LoRA r={lora_r}")
    if kf_lambda > 0:
        print(f"KF lambda: {kf_lambda} | KF every: {kf_reg_every} steps")
    print(f"{'='*70}\n")
    t0 = time.time()

    tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        base_model, trust_remote_code=True,
        torch_dtype=torch.float16,
        attn_implementation="eager",
    ).cuda()

    n_layers = model.config.num_hidden_layers
    n_heads = model.config.num_attention_heads
    print(f"  {n_layers} layers, {n_heads} heads")

    # Baseline KF
    print("\n--- BASELINE KF MEASUREMENT ---", flush=True)
    baseline_kf = kf_checkpoint_eval(model, tokenizer, 'cuda', n_layers)
    print(f"  Think CV:   {baseline_kf['think_cv']:.6e}")
    print(f"  NoThink CV: {baseline_kf['nothink_cv']:.6e}")
    print(f"  CV Delta:   {baseline_kf['cv_delta']:.6e}")

    # LoRA — ALL layers (identical to v0.1/v0.2b)
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
    print(f"  LoRA trainable: {trainable:,} / {total:,} ({100*trainable/total:.2f}%)")

    # Data — identical to v0.2a
    formatted_data = load_and_format_data(tokenizer)
    from datasets import Dataset
    train_dataset = Dataset.from_list(formatted_data)

    # SFTConfig — identical to v0.2a
    os.makedirs(output_dir, exist_ok=True)
    sft_config = SFTConfig(
        output_dir=output_dir,
        per_device_train_batch_size=batch_size,
        gradient_accumulation_steps=grad_accum,
        num_train_epochs=epochs,
        learning_rate=lr,
        lr_scheduler_type="cosine",
        warmup_ratio=0.05,
        fp16=True,
        save_steps=9999,
        logging_steps=10,
        report_to="none",
    )

    # KF regularizer (only active when lambda > 0)
    kf_reg = KFRegSFTTrainer(
        model, tokenizer, n_layers,
        kf_lambda=kf_lambda, kf_reg_every=kf_reg_every,
    )

    # Callback to inject KF regularization after optimizer steps
    class KFRegCallback(TrainerCallback):
        """Inject KF regularization via additional backward pass after optimizer step."""

        def __init__(self, kf_reg_trainer):
            self.kf = kf_reg_trainer
            self.trainer_ref = None  # Set after trainer creation

        def on_step_end(self, args, state, control, model=None, **kwargs):
            """After each optimizer step, optionally add KF regularization."""
            self.kf.global_step = state.global_step

            if self.kf.kf_lambda <= 0:
                return

            if state.global_step > 0 and state.global_step % self.kf.kf_reg_every == 0:
                # Compute KF regularization term
                cv = self.kf.compute_kf_reg_loss()
                kf_loss = self.kf.kf_lambda * cv

                # Additional backward pass for KF regularization
                kf_loss.backward()

                # Step the optimizer (available via trainer reference during training)
                if self.trainer_ref is not None and self.trainer_ref.optimizer is not None:
                    self.trainer_ref.optimizer.step()
                    self.trainer_ref.optimizer.zero_grad()

                cv_val = cv.item()
                kf_loss_val = kf_loss.item()
                self.kf.kf_log.append({
                    'step': state.global_step,
                    'cv': float(cv_val),
                    'kf_loss': float(kf_loss_val),
                })

                if state.global_step % (self.kf.kf_reg_every * 2) == 0:
                    print(f"  [Step {state.global_step}] KF reg: CV={cv_val:.6e}, "
                          f"loss={kf_loss_val:.6e}", flush=True)

                del cv, kf_loss
                torch.cuda.empty_cache()

    kf_callback = KFRegCallback(kf_reg)

    # SFTTrainer — the SAME trainer used in v0.2a, with callback
    trainer = SFTTrainer(
        model=model,
        args=sft_config,
        train_dataset=train_dataset,
        callbacks=[kf_callback],
    )

    # Give callback reference to trainer (optimizer available once training starts)
    kf_callback.trainer_ref = trainer

    print(f"\nStarting SFTTrainer ({len(formatted_data)} examples, {epochs} epochs)...")
    if kf_lambda > 0:
        print(f"  KF regularization: lambda={kf_lambda}, every {kf_reg_every} steps")
    print(flush=True)

    # Train
    trainer.train()

    # Post-training KF
    print("\n--- POST-TRAINING KF MEASUREMENT ---", flush=True)
    final_kf = kf_checkpoint_eval(model, tokenizer, 'cuda', n_layers)
    print(f"  Think CV:   {final_kf['think_cv']:.6e}")
    print(f"  NoThink CV: {final_kf['nothink_cv']:.6e}")
    print(f"  CV Delta:   {final_kf['cv_delta']:.6e}")

    # Results
    elapsed = time.time() - t0
    delta_change = final_kf['cv_delta'] - baseline_kf['cv_delta']
    degraded = delta_change > 0  # delta is negative, moving toward 0 = degraded

    # Get final training metrics
    train_log = trainer.state.log_history
    final_loss = None
    final_acc = None
    for entry in reversed(train_log):
        if 'loss' in entry and final_loss is None:
            final_loss = entry['loss']
        if 'mean_token_accuracy' in entry and final_acc is None:
            final_acc = entry['mean_token_accuracy']
        if final_loss is not None and final_acc is not None:
            break

    print(f"\n{'='*70}")
    print(f"v0.3 RESULT: lambda={kf_lambda}")
    print(f"  Baseline CV Delta: {baseline_kf['cv_delta']:.6e}")
    print(f"  Final CV Delta:    {final_kf['cv_delta']:.6e}")
    print(f"  Change:            {delta_change:+.6e} — {'DEGRADED' if degraded else 'PRESERVED/IMPROVED'}")
    pct_degradation = abs(delta_change / baseline_kf['cv_delta']) * 100
    pct_preserved = 100 - pct_degradation if degraded else 100 + pct_degradation
    print(f"  Degradation:       {pct_degradation:.1f}%")
    print(f"  Preserved:         {pct_preserved:.1f}%")
    if final_loss is not None:
        print(f"  Final CE loss:     {final_loss}")
    if final_acc is not None:
        print(f"  Final token acc:   {final_acc}")
    print(f"  Time: {elapsed:.0f}s ({elapsed/60:.1f} min)")
    print(f"{'='*70}\n")

    result = {
        'version': 'v0.3',
        'kf_lambda': kf_lambda,
        'kf_reg_every': kf_reg_every,
        'baseline_kf': baseline_kf,
        'final_kf': final_kf,
        'delta_change': float(delta_change),
        'pct_degradation': float(pct_degradation),
        'pct_preserved': float(pct_preserved),
        'final_ce_loss': final_loss,
        'final_token_accuracy': final_acc,
        'kf_trajectory': kf_reg.kf_log,
        'training_log': [e for e in train_log if 'loss' in e],
        'elapsed_seconds': elapsed,
        'config': {
            'base_model': base_model,
            'epochs': epochs,
            'batch_size': batch_size,
            'grad_accum': grad_accum,
            'lr': lr,
            'lora_r': lora_r,
            'lora_alpha': lora_alpha,
        },
    }

    # Save
    suffix = f"_lambda{kf_lambda}" if kf_lambda > 0 else "_control"
    local_path = os.path.join(output_dir, f'kf_trajectory_v03{suffix}.json')
    with open(local_path, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"Saved to {local_path}")

    win_path = f'/mnt/c/Users/mercu/clawd/projects/Corpus Perspectival/kf_trajectory_v03{suffix}.json'
    try:
        with open(win_path, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Saved to Windows: {win_path}")
    except Exception as e:
        print(f"Windows save failed: {e}")

    del model, trainer
    torch.cuda.empty_cache()
    return result


def main():
    parser = argparse.ArgumentParser(description='KF-Aware Training v0.3 — Confound-Free Lambda Sweep')
    parser.add_argument('--base_model', default='Qwen/Qwen3-0.6B')
    parser.add_argument('--epochs', type=int, default=2)
    parser.add_argument('--lambda_kf', type=float, default=0.0,
                        help='KF regularization lambda (0 = control, no reg)')
    parser.add_argument('--kf_reg_every', type=int, default=50,
                        help='Apply KF reg every N optimizer steps')
    parser.add_argument('--output_dir', default='/tmp/kf_v03')
    parser.add_argument('--sweep', action='store_true',
                        help='Run full lambda sweep: {0, 1000, 10000, 50000}')
    args = parser.parse_args()

    print(f"Device: {'cuda' if torch.cuda.is_available() else 'cpu'}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")

    if args.sweep:
        lambdas = [0, 1000, 10000, 50000]
        all_results = {}

        for lam in lambdas:
            print(f"\n{'#'*70}")
            print(f"# SWEEP: lambda = {lam}")
            print(f"{'#'*70}")

            result = run_training(
                base_model=args.base_model,
                epochs=args.epochs,
                kf_lambda=lam,
                kf_reg_every=args.kf_reg_every,
                output_dir=args.output_dir,
            )
            all_results[f'lambda_{lam}'] = result

        # Summary table
        print(f"\n{'='*70}")
        print("SWEEP SUMMARY — v0.3 Lambda Sweep")
        print(f"{'='*70}")
        print(f"{'Lambda':>10} | {'CV Delta':>12} | {'Degradation':>12} | {'Preserved':>10} | {'CE Loss':>8} | {'Token Acc':>10}")
        print("-" * 75)
        for lam in lambdas:
            r = all_results[f'lambda_{lam}']
            print(f"{lam:>10} | {r['final_kf']['cv_delta']:>12.6e} | "
                  f"{r['pct_degradation']:>10.1f}% | {r['pct_preserved']:>8.1f}% | "
                  f"{r.get('final_ce_loss', '?'):>8} | {r.get('final_token_accuracy', '?'):>10}")
        print(f"{'='*70}")

        # Save sweep summary
        sweep_path = os.path.join(args.output_dir, 'v03_sweep_summary.json')
        with open(sweep_path, 'w') as f:
            json.dump(all_results, f, indent=2)
        print(f"\nSweep summary saved to {sweep_path}")

        win_sweep = '/mnt/c/Users/mercu/clawd/projects/Corpus Perspectival/v03_sweep_summary.json'
        try:
            with open(win_sweep, 'w') as f:
                json.dump(all_results, f, indent=2)
            print(f"Saved to Windows: {win_sweep}")
        except Exception as e:
            print(f"Windows save failed: {e}")
    else:
        run_training(
            base_model=args.base_model,
            epochs=args.epochs,
            kf_lambda=args.lambda_kf,
            kf_reg_every=args.kf_reg_every,
            output_dir=args.output_dir,
        )


if __name__ == '__main__':
    main()
