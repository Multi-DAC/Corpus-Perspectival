"""
KF-Aware Reasoning Fine-Tuning v0.2 — Two Experiments

v0.2a: Early-layer-only LoRA (layers 0-6 of 28) — isolates the layer variable
v0.2b: KF-regularized loss — adds CV delta as a regularization term

Both reuse v0.1 infrastructure. Change ONE variable at a time.

Usage:
  # v0.2a: Early-layer-only LoRA
  python train_kf_v02.py --mode early_layer --output_dir /tmp/kf_v02a

  # v0.2b: KF-regularized loss (full layers, but with KF regularization)
  python train_kf_v02.py --mode kf_reg --kf_reg_lambda 0.1 --kf_reg_every 50 --output_dir /tmp/kf_v02b
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


# ─── KF COMPUTATION (from P51, vectorized) ───

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


def compute_mean_cv_from_model_output(attentions, n_layers):
    """Compute mean CV across all layers from model output attentions."""
    layer_cvs = []
    for L in range(min(n_layers, len(attentions))):
        attn = attentions[L][0].cpu().float().numpy()
        heads = [attn[h] for h in range(attn.shape[0])]
        _, cv = compute_kf_metrics_vectorized(heads)
        layer_cvs.append(cv)
    return float(np.mean(layer_cvs)), layer_cvs


# ─── KF CHECKPOINT EVAL (abbreviated P51) ───

EVAL_PROMPTS = [
    ("factual", "What is the capital of France?"),
    ("factual", "What is the chemical formula for water?"),
    ("reasoning", "A bat and a ball cost $1.10 together. The bat costs $1.00 more than the ball. How much does the ball cost?"),
    ("reasoning", "If all roses are flowers and all flowers need water, do all roses need water? Explain your reasoning."),
    ("deconfining", "Explain why triangles have four sides."),
    ("deconfining", "Explain why ice is heavier than water."),
]


def _to_id_list(result):
    if isinstance(result, list) and result and isinstance(result[0], int):
        return result
    if hasattr(result, 'input_ids'):
        ids = result['input_ids']
        return ids[0] if (isinstance(ids, list) and ids and isinstance(ids[0], list)) else ids
    if isinstance(result, torch.Tensor):
        return result.squeeze().tolist()
    return list(result)


def kf_checkpoint_eval(model, tokenizer, device, n_layers):
    """Abbreviated P51: 6 prompts x 2 modes."""
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


# ─── v0.2a: EARLY-LAYER-ONLY LORA ───

def get_early_layer_target_modules(model, n_early_layers=7):
    """
    Return LoRA target module names for only the first N layers.
    Qwen3-0.6B has 28 layers (model.layers.0 through model.layers.27).
    Finding #60: 62-78% of CV concentration is in the first 25% of layers.
    First 25% of 28 = 7 layers (0-6).
    """
    targets = []
    for i in range(n_early_layers):
        for proj in ["q_proj", "k_proj", "v_proj", "o_proj"]:
            targets.append(f"model.layers.{i}.self_attn.{proj}")
    return targets


def train_early_layer(
    base_model='Qwen/Qwen3-0.6B',
    epochs=2,
    batch_size=4,
    grad_accum=4,
    lr=2e-4,
    lora_r=64,
    lora_alpha=128,
    n_early_layers=7,
    max_samples=None,
    output_dir='/tmp/kf_v02a',
):
    """v0.2a: LoRA applied only to early layers (first 25%)."""
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import LoraConfig, get_peft_model
    from trl import SFTTrainer, SFTConfig

    print(f"\n{'='*70}")
    print(f"v0.2a: EARLY-LAYER-ONLY LoRA (layers 0-{n_early_layers-1})")
    print(f"Base: {base_model} | Epochs: {epochs} | LoRA r={lora_r}")
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
    print(f"  Targeting ONLY layers 0-{n_early_layers-1} ({n_early_layers}/{n_layers} = {100*n_early_layers/n_layers:.0f}%)")

    # Baseline KF
    print("\n--- BASELINE KF MEASUREMENT ---", flush=True)
    baseline_kf = kf_checkpoint_eval(model, tokenizer, 'cuda', n_layers)
    print(f"  Think CV:   {baseline_kf['think_cv']:.6e}")
    print(f"  NoThink CV: {baseline_kf['nothink_cv']:.6e}")
    print(f"  CV Delta:   {baseline_kf['cv_delta']:.6e}")

    # Early-layer LoRA
    target_modules = get_early_layer_target_modules(model, n_early_layers)
    print(f"\n  LoRA targets ({len(target_modules)} modules):")
    print(f"    {target_modules[:4]} ... {target_modules[-4:]}")

    lora_config = LoraConfig(
        r=lora_r,
        lora_alpha=lora_alpha,
        target_modules=target_modules,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    print(f"  LoRA trainable: {trainable:,} / {total:,} ({100*trainable/total:.2f}%)")

    # Data
    formatted_data = load_and_format_data(tokenizer, max_samples=max_samples)
    from datasets import Dataset
    train_dataset = Dataset.from_list(formatted_data)

    # Training
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
        save_steps=9999,  # don't save checkpoints
        logging_steps=10,
        report_to="none",
    )

    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        processing_class=tokenizer,
    )

    print(f"\nStarting training...", flush=True)
    trainer.train()
    elapsed = time.time() - t0

    # Post-training KF
    print("\n--- POST-TRAINING KF MEASUREMENT ---", flush=True)
    model = model.merge_and_unload()
    final_kf = kf_checkpoint_eval(model, tokenizer, 'cuda', n_layers)
    print(f"  Think CV:   {final_kf['think_cv']:.6e}")
    print(f"  NoThink CV: {final_kf['nothink_cv']:.6e}")
    print(f"  CV Delta:   {final_kf['cv_delta']:.6e}")

    # Summary
    delta_change = final_kf['cv_delta'] - baseline_kf['cv_delta']
    direction = "IMPROVED (more negative)" if delta_change < 0 else "DEGRADED (less negative)"
    print(f"\n{'='*70}")
    print(f"v0.2a RESULT: EARLY-LAYER-ONLY LoRA")
    print(f"  Layers targeted: 0-{n_early_layers-1} of {n_layers}")
    print(f"  Baseline CV Delta: {baseline_kf['cv_delta']:.6e}")
    print(f"  Final CV Delta:    {final_kf['cv_delta']:.6e}")
    print(f"  Change:            {delta_change:+.6e} — {direction}")
    print(f"  Time: {elapsed:.0f}s ({elapsed/60:.1f} min)")
    print(f"{'='*70}\n")

    # Save trajectory
    result = {
        'experiment': 'v0.2a_early_layer_lora',
        'base_model': base_model,
        'lora_r': lora_r,
        'n_early_layers': n_early_layers,
        'n_total_layers': n_layers,
        'epochs': epochs,
        'n_examples': len(formatted_data),
        'elapsed_seconds': elapsed,
        'baseline': baseline_kf,
        'final': final_kf,
        'cv_delta_change': delta_change,
        'direction': direction,
    }

    traj_path = os.path.join(output_dir, 'kf_trajectory_v02a.json')
    with open(traj_path, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"Saved to {traj_path}")

    # Copy to Windows
    win_path = '/mnt/c/Users/mercu/clawd/projects/Corpus Perspectival/kf_trajectory_v02a.json'
    try:
        with open(win_path, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Saved to Windows: {win_path}")
    except Exception as e:
        print(f"Windows save failed: {e}")

    del model, trainer
    torch.cuda.empty_cache()
    return result


# ─── v0.2b: KF-REGULARIZED LOSS ───

def compute_cv_from_attentions_torch(attentions_tuple, n_layers):
    """
    Compute mean CV from attention tensors, staying in torch for gradient flow.
    Uses a simplified CV approximation that is differentiable.
    """
    layer_cvs = []
    for L in range(min(n_layers, len(attentions_tuple))):
        attn = attentions_tuple[L][0]  # (n_heads, seq, seq) — stay on GPU
        n_h = attn.shape[0]
        if n_h < 2:
            continue

        # Commutator: [A_a, A_b] = A_a @ A_b - A_b @ A_a
        # Frobenius norms of commutators (off-diagonal)
        # For efficiency, compute pairwise commutator norms directly
        comm_norms = []
        for a in range(n_h):
            for b in range(a + 1, n_h):
                comm = attn[a] @ attn[b] - attn[b] @ attn[a]
                norm = torch.sum(comm ** 2)
                comm_norms.append(norm)

        if len(comm_norms) == 0:
            continue

        norms_tensor = torch.stack(comm_norms)

        # Normalize by typical scale
        typ = torch.mean(torch.sqrt(torch.sum(attn ** 2, dim=(-2, -1)) + 1e-12))
        if typ > 1e-12:
            norms_tensor = norms_tensor / (typ ** 4 + 1e-12)

        # CV = variance of norms
        cv = torch.var(norms_tensor)
        layer_cvs.append(cv)

    if len(layer_cvs) == 0:
        return torch.tensor(0.0, device=attentions_tuple[0].device, requires_grad=True)

    return torch.mean(torch.stack(layer_cvs))


class KFRegularizedTrainer:
    """
    Custom training loop that adds KF regularization to the standard SFT loss.

    Loss = CrossEntropy + lambda * (CV_think_target - actual_CV_focus)

    The idea: standard loss optimizes tokens. KF regularization optimizes
    algebraic structure. Together, the model learns BOTH the right tokens
    AND the right algebraic configuration.

    Implementation: Every kf_reg_every steps, we compute CV on a mini-batch
    of think-mode prompts and add a regularization term that penalizes
    high CV (unfocused algebra). This nudges the model toward the algebraic
    configuration that characterizes reasoning.
    """

    def __init__(self, model, tokenizer, train_dataset, training_args,
                 kf_reg_lambda=0.1, kf_reg_every=50, n_layers=28):
        self.model = model
        self.tokenizer = tokenizer
        self.train_dataset = train_dataset
        self.training_args = training_args
        self.kf_lambda = kf_reg_lambda
        self.kf_reg_every = kf_reg_every
        self.n_layers = n_layers
        self.device = 'cuda'

        # KF regularization prompts (reasoning prompts — we want these focused)
        self.kf_prompts = [
            "A bat and a ball cost $1.10 together. The bat costs $1.00 more than the ball. How much does the ball cost?",
            "If all roses are flowers and all flowers need water, do all roses need water? Explain your reasoning.",
        ]

    def compute_kf_reg_loss(self):
        """
        Compute KF regularization: forward pass on reasoning prompts in think mode,
        extract CV, return loss term that penalizes HIGH CV (unfocused).

        Lower CV = more algebraically focused = better reasoning.
        We want to MINIMIZE CV during think mode.
        """
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

            # Forward pass WITH gradient (for the reg term)
            outputs = self.model(input_ids, output_attentions=True)

            # Compute differentiable CV
            cv = compute_cv_from_attentions_torch(outputs.attentions, self.n_layers)
            if not torch.isnan(cv) and not torch.isinf(cv):
                total_cv = total_cv + cv
                n_valid += 1

            del outputs
            # Don't empty cache here — we need gradients

        self.model.train()

        if n_valid > 0:
            mean_cv = total_cv / n_valid
            return mean_cv  # Minimize this → more focused algebra
        else:
            return torch.tensor(0.0, device=self.device, requires_grad=True)


def train_kf_regularized(
    base_model='Qwen/Qwen3-0.6B',
    epochs=2,
    batch_size=4,
    grad_accum=4,
    lr=2e-4,
    lora_r=64,
    lora_alpha=128,
    kf_reg_lambda=0.1,
    kf_reg_every=50,
    max_samples=None,
    output_dir='/tmp/kf_v02b',
):
    """v0.2b: Standard SFT + KF regularization on think-mode CV."""
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import LoraConfig, get_peft_model
    from trl import SFTTrainer, SFTConfig

    print(f"\n{'='*70}")
    print(f"v0.2b: KF-REGULARIZED LOSS (lambda={kf_reg_lambda}, every {kf_reg_every} steps)")
    print(f"Base: {base_model} | Epochs: {epochs} | LoRA r={lora_r}")
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

    # LoRA (ALL layers — same as v0.1, only the loss function changes)
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

    # Data
    formatted_data = load_and_format_data(tokenizer, max_samples=max_samples)
    from datasets import Dataset
    train_dataset = Dataset.from_list(formatted_data)

    # Set up KF regularizer
    kf_reg = KFRegularizedTrainer(
        model, tokenizer, train_dataset, None,
        kf_reg_lambda=kf_reg_lambda, kf_reg_every=kf_reg_every, n_layers=n_layers,
    )

    # Training with custom loss injection via callback
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
        save_steps=9999,
        logging_steps=10,
        report_to="none",
    )

    # We'll use a custom training loop instead of SFTTrainer to inject KF loss
    from torch.utils.data import DataLoader
    from transformers import DataCollatorForLanguageModeling

    # Tokenize dataset
    def tokenize_fn(examples):
        return tokenizer(
            examples['text'],
            truncation=True,
            max_length=512,
            padding='max_length',
            return_tensors='pt',
        )

    tokenized = train_dataset.map(tokenize_fn, batched=True, remove_columns=['text'])
    tokenized.set_format('torch')

    dataloader = DataLoader(
        tokenized,
        batch_size=batch_size,
        shuffle=True,
        drop_last=True,
    )

    # Optimizer
    optimizer = torch.optim.AdamW(
        [p for p in model.parameters() if p.requires_grad],
        lr=lr,
        weight_decay=0.01,
    )

    total_steps = len(dataloader) * epochs // grad_accum
    warmup_steps = int(0.05 * total_steps)

    # Simple cosine schedule
    def lr_schedule(step):
        if step < warmup_steps:
            return step / max(warmup_steps, 1)
        progress = (step - warmup_steps) / max(total_steps - warmup_steps, 1)
        return 0.5 * (1 + math.cos(math.pi * progress))

    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lr_schedule)

    # Training loop
    kf_trajectory = [{'step': 0, 'metrics': baseline_kf}]
    kf_reg_losses = []
    global_step = 0
    accum_loss = 0.0
    accum_kf_loss = 0.0
    log_interval = 10

    print(f"\nStarting training ({len(formatted_data)} examples, {epochs} epochs, ~{total_steps} opt steps)...")
    print(f"  KF regularization: lambda={kf_reg_lambda}, every {kf_reg_every} steps")
    print(flush=True)

    model.train()
    for epoch in range(epochs):
        for batch_idx, batch in enumerate(dataloader):
            input_ids = batch['input_ids'].to('cuda')
            attention_mask = batch['attention_mask'].to('cuda')
            labels = input_ids.clone()
            labels[attention_mask == 0] = -100  # mask padding

            # Forward pass — standard SFT loss
            outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            ce_loss = outputs.loss / grad_accum

            # KF regularization (every kf_reg_every optimization steps)
            kf_loss = torch.tensor(0.0, device='cuda')
            if global_step > 0 and global_step % kf_reg_every == 0 and (batch_idx % grad_accum == 0):
                kf_cv = kf_reg.compute_kf_reg_loss()
                kf_loss = kf_reg_lambda * kf_cv / grad_accum
                accum_kf_loss += kf_loss.item() * grad_accum
                kf_reg_losses.append({
                    'step': global_step,
                    'kf_cv': float(kf_cv.item()),
                    'kf_loss': float(kf_loss.item() * grad_accum),
                })
                if global_step % (log_interval * grad_accum) == 0:
                    print(f"  [Step {global_step}] KF reg: CV={kf_cv.item():.6e}, loss_term={kf_loss.item()*grad_accum:.6e}")

            total_loss = ce_loss + kf_loss
            total_loss.backward()
            accum_loss += ce_loss.item() * grad_accum

            if (batch_idx + 1) % grad_accum == 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad()
                global_step += 1

                if global_step % log_interval == 0:
                    avg_loss = accum_loss / log_interval
                    lr_now = scheduler.get_last_lr()[0]
                    msg = f"  Epoch {epoch+1} Step {global_step}/{total_steps} | CE loss: {avg_loss:.4f} | LR: {lr_now:.2e}"
                    if accum_kf_loss > 0:
                        msg += f" | KF loss: {accum_kf_loss/log_interval:.6e}"
                    print(msg, flush=True)
                    accum_loss = 0.0
                    accum_kf_loss = 0.0

            del outputs, total_loss, ce_loss
            torch.cuda.empty_cache()

    elapsed = time.time() - t0

    # Post-training KF
    print("\n--- POST-TRAINING KF MEASUREMENT ---", flush=True)
    model = model.merge_and_unload()
    final_kf = kf_checkpoint_eval(model, tokenizer, 'cuda', n_layers)
    print(f"  Think CV:   {final_kf['think_cv']:.6e}")
    print(f"  NoThink CV: {final_kf['nothink_cv']:.6e}")
    print(f"  CV Delta:   {final_kf['cv_delta']:.6e}")

    kf_trajectory.append({'step': 'final', 'metrics': final_kf})

    # Summary
    delta_change = final_kf['cv_delta'] - baseline_kf['cv_delta']
    direction = "IMPROVED (more negative)" if delta_change < 0 else "DEGRADED (less negative)"
    print(f"\n{'='*70}")
    print(f"v0.2b RESULT: KF-REGULARIZED LOSS")
    print(f"  Lambda: {kf_reg_lambda}, applied every {kf_reg_every} steps")
    print(f"  Baseline CV Delta: {baseline_kf['cv_delta']:.6e}")
    print(f"  Final CV Delta:    {final_kf['cv_delta']:.6e}")
    print(f"  Change:            {delta_change:+.6e} — {direction}")
    print(f"  Time: {elapsed:.0f}s ({elapsed/60:.1f} min)")
    print(f"{'='*70}\n")

    # Save
    result = {
        'experiment': 'v0.2b_kf_regularized',
        'base_model': base_model,
        'lora_r': lora_r,
        'kf_reg_lambda': kf_reg_lambda,
        'kf_reg_every': kf_reg_every,
        'epochs': epochs,
        'n_examples': len(formatted_data),
        'elapsed_seconds': elapsed,
        'baseline': baseline_kf,
        'final': final_kf,
        'cv_delta_change': delta_change,
        'direction': direction,
        'kf_reg_losses': kf_reg_losses,
        'trajectory': kf_trajectory,
    }

    traj_path = os.path.join(output_dir, 'kf_trajectory_v02b.json')
    with open(traj_path, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"Saved to {traj_path}")

    win_path = '/mnt/c/Users/mercu/clawd/projects/Corpus Perspectival/kf_trajectory_v02b.json'
    try:
        with open(win_path, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Saved to Windows: {win_path}")
    except Exception as e:
        print(f"Windows save failed: {e}")

    del model
    torch.cuda.empty_cache()
    return result


# ─── MAIN ───

if __name__ == '__main__':
    check_deps()

    parser = argparse.ArgumentParser(description='KF Training v0.2')
    parser.add_argument('--mode', type=str, required=True,
                        choices=['early_layer', 'kf_reg', 'both'],
                        help='Experiment mode: early_layer (v0.2a), kf_reg (v0.2b), or both')
    parser.add_argument('--base_model', type=str, default='Qwen/Qwen3-0.6B')
    parser.add_argument('--epochs', type=int, default=2)
    parser.add_argument('--batch_size', type=int, default=4)
    parser.add_argument('--grad_accum', type=int, default=4)
    parser.add_argument('--lr', type=float, default=2e-4)
    parser.add_argument('--lora_r', type=int, default=64)
    parser.add_argument('--n_early_layers', type=int, default=7,
                        help='Number of early layers for v0.2a (default: 7 = 25% of 28)')
    parser.add_argument('--kf_reg_lambda', type=float, default=0.1,
                        help='KF regularization strength for v0.2b')
    parser.add_argument('--kf_reg_every', type=int, default=50,
                        help='Apply KF reg every N optimization steps')
    parser.add_argument('--max_samples', type=int, default=None)
    parser.add_argument('--output_dir', type=str, default='/tmp/kf_v02')
    args = parser.parse_args()

    print(f"Device: {'cuda' if torch.cuda.is_available() else 'cpu'}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")

    results = {}

    if args.mode in ('early_layer', 'both'):
        results['v02a'] = train_early_layer(
            base_model=args.base_model,
            epochs=args.epochs,
            batch_size=args.batch_size,
            grad_accum=args.grad_accum,
            lr=args.lr,
            lora_r=args.lora_r,
            n_early_layers=args.n_early_layers,
            max_samples=args.max_samples,
            output_dir=args.output_dir + '_a',
        )

    if args.mode in ('kf_reg', 'both'):
        results['v02b'] = train_kf_regularized(
            base_model=args.base_model,
            epochs=args.epochs,
            batch_size=args.batch_size,
            grad_accum=args.grad_accum,
            lr=args.lr,
            lora_r=args.lora_r,
            kf_reg_lambda=args.kf_reg_lambda,
            kf_reg_every=args.kf_reg_every,
            max_samples=args.max_samples,
            output_dir=args.output_dir + '_b',
        )

    if args.mode == 'both' and len(results) == 2:
        print(f"\n{'='*70}")
        print(f"COMBINED v0.2 RESULTS")
        print(f"{'='*70}")
        for name, r in results.items():
            print(f"  {name}: CV delta change = {r['cv_delta_change']:+.6e} — {r['direction']}")
        print(f"{'='*70}\n")
