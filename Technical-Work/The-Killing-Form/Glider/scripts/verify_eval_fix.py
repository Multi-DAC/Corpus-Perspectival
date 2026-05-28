"""Load a trained HRM checkpoint and run the HALT-AWARE eval to verify the fix.
Tests whether the corrected eval (fresh carry per batch + ACT halt-loop) reveals
nonzero accuracy on the already-trained smoke checkpoint."""
import sys, os
sys.path.insert(0, '/home/clawd/HRM')
sys.path.insert(0, os.path.dirname(__file__))
import torch
from omegaconf import OmegaConf
from train_kf_gated_hrm_easy import build_model, create_dataloader

DATA = '/home/clawd/HRM/data/sudoku-easy-1k-aug-1000'
CKPT = sys.argv[1] if len(sys.argv) > 1 else '/home/clawd/path_a_results/smoke_b64/final.pt'
BS = 64
EVAL_BATCHES = 20

device = 'cuda'
arch_cfg = OmegaConf.load('/home/clawd/HRM/config/arch/hrm_v1.yaml')
_, meta = create_dataloader(DATA, "train", batch_size=BS, seed=0)
model, raw_model = build_model(arch_cfg, meta.num_puzzle_identifiers, device,
                               vocab_size=meta.vocab_size, seq_len=meta.seq_len, batch_size=BS)
sd = torch.load(CKPT, map_location=device)
raw_model.load_state_dict(sd['model_state_dict'])
print(f"loaded {CKPT}  (step {sd.get('global_step','?')})")

model.eval()
eval_sum = {}
nb = 0
loader, _ = create_dataloader(DATA, "test", batch_size=BS, seed=0)
with torch.inference_mode():
    for _s, batch, bs in loader:
        bg = {k: v.cuda() for k, v in batch.items()}
        with torch.device(device):
            carry = model.initial_carry(bg)
        guard = 0
        while True:
            carry, _, metrics, _, all_finish = model(carry=carry, batch=bg, return_keys=[])
            guard += 1
            if all_finish or guard >= 32:
                break
        if nb == 0:
            print(f"  batch0: halt_iters={guard}  metric keys={list(metrics.keys())}  count={metrics.get('count')}")
        for k, v in metrics.items():
            if isinstance(v, torch.Tensor):
                eval_sum[k] = eval_sum.get(k, 0) + v.item()
        nb += 1
        if nb >= EVAL_BATCHES:
            break
c = eval_sum.get('count', 0)
print(f"\n  HALT-AWARE EVAL over {nb} batches:  count={c}")
if c > 0:
    print(f"  exact_accuracy = {eval_sum.get('exact_accuracy',0)/c:.4f}")
    print(f"  token_accuracy = {eval_sum.get('accuracy',0)/c:.4f}")
    print(f"  q_halt_accuracy= {eval_sum.get('q_halt_accuracy',0)/c:.4f}")
else:
    print("  count still 0 — deeper issue.")
