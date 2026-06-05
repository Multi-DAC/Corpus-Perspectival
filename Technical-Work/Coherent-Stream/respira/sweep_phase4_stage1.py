"""
Respira Phase 4 — Four-Reading Bake-Off, Stage 1: §2.1-fixed sweep.

Pre-registration: `palace/south/respira-phase4-stage1-v21-fixed-preregistration-2026-05-29.md`
Ratified: 2026-05-29 evening by Clayton.

Arms (3 seeds each, 2500 steps each):

  no_mirror   — current baseline: Mirror sits idle, scalar defaults used,
                cross-organ ComplexLinear projections are LEARNABLE.
  v21_fixed   — §2.1-fixed: identical to no_mirror EXCEPT cross-organ projections
                (p_to_e, e_to_p) are frozen at Glorot init (requires_grad=False).
                Tests "does freezing the medium hurt vs letting it learn?"

Read-C strong-form falsification condition: if v21_fixed mean token-acc @2500
exceeds no_mirror mean by > 1 SE of no_mirror, the substrate-condition effect
from having a non-learning medium is detectable — Read C's strongest form
("no coupling-layer learning helps") is falsified.

Writes results to `phase4_stage1_results_YYYY-MM-DD.json`.

Run from respira/:
  python3 sweep_phase4_stage1.py [--seeds 0,1,2] [--steps 2500] [--arms no_mirror,v21_fixed]

CLAWD-LOCAL / PRIVATE.
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(line_buffering=True)

import argparse
import json
import time
from datetime import datetime, timezone

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim import AdamW

from data import make_loader, cycle_loader, IGNORE_LABEL_ID
from respira import RespiraCell
from organ import ComplexLinear
from eval import evaluate


CHECKPOINTS = [200, 500, 1000, 2000, 2500]

# Arm definitions. All arms use no_mirror config (mirror_authority=0, arch_variant="default").
#   no_mirror   — independent learnable p_to_e + e_to_p (current canonical baseline)
#   v21_fixed   — independent FROZEN cross-organ projections (§2.1 static-medium reading)
#   v22_matrix  — single learnable W; p_to_e=W, e_to_p=W^H (§2.2 syncytium-fusion reading)
ARMS = {
    "no_mirror":      {"mode": "independent_learnable"},
    "v21_fixed":      {"mode": "independent_frozen"},
    "v22_matrix":     {"mode": "shared_hermitian"},
    "v23_stiefel":    {"mode": "stiefel_constrained"},
    "v23_soft":       {"mode": "soft_stiefel_penalty", "lambda_stiefel": 1.0},
    "v23_soft_weak":  {"mode": "soft_stiefel_penalty", "lambda_stiefel": 0.01},
    "v24c_temporal":  {"mode": "temporal_extension", "lambda_decay": 0.4},
    "v24d_adaptive":  {"mode": "adaptive_temporal_extension", "hidden_dim": 8},
}


class AdaptiveTemporalExtensionWrapper(nn.Module):
    """Wraps a ComplexLinear with content-adaptive temporal extension.

    Each cycle: gate(raw.abs()) computes per-batch-per-position λ in [0,1];
    effective = (1-λ) * history + λ * raw; history = effective.detach().

    Gate saturating at λ=1 recovers no_mirror behavior (instantaneous, no history).
    Gate at λ=0 freezes (full history, ignore new input). Architecture learns where
    to sit per signal.
    """

    def __init__(self, source: ComplexLinear, hidden_dim: int = 8):
        super().__init__()
        self.source = source
        out_features = source.real.weight.shape[0]
        self.gate = nn.Sequential(
            nn.Linear(out_features, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid(),
        )
        object.__setattr__(self, "_state", {"history": None, "gate_values": []})

    def reset_history(self):
        self._state["history"] = None
        # Keep gate_values across batches for diagnostics; clear at start of new sweep call.

    def reset_diagnostics(self):
        self._state["gate_values"] = []

    def forward(self, z: torch.Tensor) -> torch.Tensor:
        if not torch.is_complex(z):
            raise TypeError(f"AdaptiveTemporalExtensionWrapper expects complex input, got {z.dtype}")
        raw = self.source(z)
        hist = self._state["history"]
        if hist is None or hist.shape != raw.shape:
            hist = torch.zeros_like(raw, requires_grad=False)
        hist = hist.detach()
        # Per-batch-per-position scalar gate
        raw_mag = raw.abs()  # [..., out_features], real
        lam = self.gate(raw_mag)  # [..., 1], real, in [0, 1]
        # Broadcast lam to complex matching raw shape (last dim 1 broadcasts to out_features)
        lam_complex = lam.to(raw.dtype)
        effective = (1.0 - lam_complex) * hist + lam_complex * raw
        self._state["history"] = effective.detach()
        # Save mean-gate-value for diagnostics (no grad)
        self._state["gate_values"].append(float(lam.mean().detach().item()))
        return effective


def install_adaptive_temporal(model: RespiraCell, hidden_dim: int = 8) -> dict:
    """Wrap p_to_e and e_to_p with AdaptiveTemporalExtensionWrapper + auto-reset patch."""
    device = next(model.parameters()).device
    model.p_to_e = AdaptiveTemporalExtensionWrapper(model.p_to_e, hidden_dim=hidden_dim).to(device)
    model.e_to_p = AdaptiveTemporalExtensionWrapper(model.e_to_p, hidden_dim=hidden_dim).to(device)

    # Patch forward to auto-reset history
    original_forward = model.forward
    def forward_with_reset(*args, **kwargs):
        if isinstance(model.p_to_e, AdaptiveTemporalExtensionWrapper):
            model.p_to_e.reset_history()
        if isinstance(model.e_to_p, AdaptiveTemporalExtensionWrapper):
            model.e_to_p.reset_history()
        return original_forward(*args, **kwargs)
    model.forward = forward_with_reset

    return {
        "hidden_dim": hidden_dim,
        "p_to_e_params": sum(p.numel() for p in model.p_to_e.parameters()),
        "e_to_p_params": sum(p.numel() for p in model.e_to_p.parameters()),
    }


class TemporalExtensionWrapper(nn.Module):
    """Wraps a ComplexLinear to apply single-decay history buffering.

    effective_msg[k] = (1 - lambda) * history[k-1] + lambda * raw_msg[k]
    history[k] = effective_msg[k]  (detached to bound backward graph)

    Stage 4 Design C: fixed lambda_decay (no learnable parameters added).
    History detach prevents gradient accumulation through recurrent chains
    (avoids the QR-style scaling pathology from Stage 3 strict).
    """

    def __init__(self, source: ComplexLinear, lambda_decay: float = 0.4):
        super().__init__()
        self.source = source
        self.lambda_decay = float(lambda_decay)
        # Hold history outside the module's standard attribute chain via a dict.
        # Avoids any chance of PyTorch autograd tracking the attribute-assignment chain.
        # Use object.__setattr__ to bypass nn.Module's auto-tracking of attributes.
        object.__setattr__(self, "_state", {"history": None})

    def reset_history(self):
        self._state["history"] = None

    def forward(self, z: torch.Tensor) -> torch.Tensor:
        if not torch.is_complex(z):
            raise TypeError(f"TemporalExtensionWrapper expects complex input, got {z.dtype}")
        raw = self.source(z)
        hist = self._state["history"]
        if hist is None or hist.shape != raw.shape:
            hist = torch.zeros_like(raw, requires_grad=False)
        # Ensure hist has no graph: explicitly detach (defensive; should already be detached)
        hist = hist.detach()
        effective = (1.0 - self.lambda_decay) * hist + self.lambda_decay * raw
        # Store detached copy for next cycle. Use .data to fully break graph history.
        self._state["history"] = effective.detach()
        return effective


def install_temporal_extension(model: RespiraCell, lambda_decay: float = 0.4) -> dict:
    """Wrap both p_to_e and e_to_p with TemporalExtensionWrapper.

    Also patches model.forward to auto-reset history buffers at the start of each
    forward call. This ensures eval batches (which call model.forward without going
    through the training loop's explicit reset) also start with fresh history.
    """
    model.p_to_e = TemporalExtensionWrapper(model.p_to_e, lambda_decay=lambda_decay)
    model.e_to_p = TemporalExtensionWrapper(model.e_to_p, lambda_decay=lambda_decay)

    # Patch forward to auto-reset history. Bind the original method, then replace.
    original_forward = model.forward
    def forward_with_reset(*args, **kwargs):
        reset_temporal_history(model)
        return original_forward(*args, **kwargs)
    model.forward = forward_with_reset

    return {
        "lambda_decay": lambda_decay,
        "p_to_e_params": sum(p.numel() for p in model.p_to_e.parameters()),
        "e_to_p_params": sum(p.numel() for p in model.e_to_p.parameters()),
    }


def reset_temporal_history(model: RespiraCell) -> None:
    """Reset history buffers on TemporalExtensionWrapper instances. Called per-batch."""
    if isinstance(model.p_to_e, TemporalExtensionWrapper):
        model.p_to_e.reset_history()
    if isinstance(model.e_to_p, TemporalExtensionWrapper):
        model.e_to_p.reset_history()


def soft_stiefel_penalty(model: RespiraCell) -> torch.Tensor:
    """L2 penalty pushing both cross-organ projections toward Stiefel manifold.

    For p_to_e (W ∈ ℂ^(E×P) with E > P): penalize ||W^H W - I_P||_F²
    For e_to_p (V ∈ ℂ^(P×E) with P < E): penalize ||V V^H - I_P||_F²

    Returns scalar real penalty term. Add to total_loss with coefficient lambda_stiefel.
    """
    # Reconstruct complex weight matrices from real/imag parts
    W_pe = torch.complex(model.p_to_e.real.weight, model.p_to_e.imag.weight)  # (E, P)
    W_ep = torch.complex(model.e_to_p.real.weight, model.e_to_p.imag.weight)  # (P, E)
    # W^H W for p_to_e (gives P x P matrix; should be identity if columns orthonormal)
    WH_W = W_pe.conj().T @ W_pe  # (P, P)
    # V V^H for e_to_p (gives P x P matrix; should be identity if rows orthonormal)
    V_VH = W_ep @ W_ep.conj().T  # (P, P)
    P = W_pe.shape[1]
    eye_P = torch.eye(P, dtype=WH_W.dtype, device=WH_W.device)
    # Frobenius norm squared = sum of squared magnitudes of all entries
    pen_pe = (WH_W - eye_P).abs().pow(2).sum()
    pen_ep = (V_VH - eye_P).abs().pow(2).sum()
    return pen_pe + pen_ep


class StiefelComplexLinear(nn.Module):
    """Complex linear layer with Stiefel-manifold constrained weights via QR retraction.

    Holds an unconstrained complex parameter W_tilde of shape (out, in).
    At forward time:
      - If out >= in: QR-decompose W_tilde, use Q (shape (out, in)) — Q^H Q = I_in.
        Operator is an isometry (columns orthonormal).
      - If out < in: QR-decompose W_tilde^H, transpose Q back — W W^H = I_out.
        Operator is a co-isometry (rows orthonormal).

    Gradient flows through torch.linalg.qr's backward, which projects updates to
    the Stiefel-tangent space implicitly.
    """

    def __init__(self, in_features: int, out_features: int):
        super().__init__()
        self.in_features = int(in_features)
        self.out_features = int(out_features)
        scale = 0.1 / in_features ** 0.5
        self.W_re = nn.Parameter(torch.randn(out_features, in_features) * scale)
        self.W_im = nn.Parameter(torch.randn(out_features, in_features) * scale)

    def forward(self, z: torch.Tensor) -> torch.Tensor:
        if not torch.is_complex(z):
            raise TypeError(f"StiefelComplexLinear expects complex input, got {z.dtype}")
        W_tilde = torch.complex(self.W_re, self.W_im)  # (out, in)
        if self.out_features >= self.in_features:
            # Columns orthonormal: QR of W_tilde directly.
            Q, _ = torch.linalg.qr(W_tilde, mode="reduced")  # (out, in)
            W = Q
        else:
            # Rows orthonormal: QR of W_tilde^H, then conj-transpose back.
            Q, _ = torch.linalg.qr(W_tilde.conj().T, mode="reduced")  # (in, out)
            W = Q.conj().T  # (out, in)
        # output = z @ W^T along last dim. einsum keeps it simple for any leading dims.
        return torch.einsum("...i,oi->...o", z, W)


def install_stiefel_projections(model: RespiraCell) -> dict:
    """Replace model.p_to_e and model.e_to_p with StiefelComplexLinear versions.

    Preserves shapes:
      p_to_e: in=planner_channels, out=executor_channels
      e_to_p: in=executor_channels, out=planner_channels
    """
    P = model.planner_channels
    E = model.executor_channels
    device = next(model.parameters()).device
    original_p_to_e = sum(p.numel() for p in model.p_to_e.parameters())
    original_e_to_p = sum(p.numel() for p in model.e_to_p.parameters())
    model.p_to_e = StiefelComplexLinear(in_features=P, out_features=E).to(device)
    model.e_to_p = StiefelComplexLinear(in_features=E, out_features=P).to(device)
    new_p_to_e = sum(p.numel() for p in model.p_to_e.parameters())
    new_e_to_p = sum(p.numel() for p in model.e_to_p.parameters())
    return {
        "original_p_to_e_params": original_p_to_e,
        "original_e_to_p_params": original_e_to_p,
        "new_p_to_e_params": new_p_to_e,
        "new_e_to_p_params": new_e_to_p,
        "p_to_e_isometry_kind": "columns_orthonormal (E>P)" if E >= P else "rows_orthonormal (E<P)",
        "e_to_p_isometry_kind": "columns_orthonormal (P>E)" if P >= E else "rows_orthonormal (P<E)",
    }


class HermitianSharedProjection(nn.Module):
    """e_to_p that uses p_to_e's weights via Hermitian transpose.

    Given source p_to_e (ComplexLinear with W_r, W_i of shape (E, P)),
    this module applies W^H = (W_r^T - i W_i^T) of shape (P, E) to an
    (E,)-shaped complex input, producing a (P,)-shaped complex output.

    The source ComplexLinear is stored as a plain attribute (not a submodule),
    so its parameters are NOT registered here — they only live in p_to_e.
    Gradient backprops through both forward uses to the shared p_to_e weights.
    """

    def __init__(self, source: ComplexLinear):
        super().__init__()
        # Use object.__setattr__ to bypass nn.Module's auto-submodule registration.
        # We want source's parameters to appear ONCE in the model, not twice.
        object.__setattr__(self, "_source", source)

    @property
    def source(self) -> ComplexLinear:
        return self._source

    def forward(self, z: torch.Tensor) -> torch.Tensor:
        if not torch.is_complex(z):
            raise TypeError(f"HermitianSharedProjection expects complex input, got {z.dtype}")
        Wr = self.source.real.weight  # (E, P)
        Wi = self.source.imag.weight  # (E, P)
        zr, zi = z.real, z.imag       # (..., E)
        # Hermitian transpose: W^H = W_r^T - i W_i^T  (shape (P, E))
        # (W^H z) = (W_r^T - i W_i^T)(z_r + i z_i)
        #        = (W_r^T z_r + W_i^T z_i) + i (W_r^T z_i - W_i^T z_r)
        # F.linear(input, weight) computes input @ weight^T. To compute z @ W_r (i.e. W_r^T z
        # along last dim viewed row-wise), we pass weight=Wr.t() — but actually we want W_r^T z
        # which is F.linear(z, Wr) since F.linear's weight=Wr means output_dim = Wr.shape[0] = E,
        # which is wrong. Let me re-derive: we have z of shape (..., E) and want output (..., P).
        # We need W_r^T which has shape (P, E). F.linear(z, weight) does output = z @ weight^T,
        # so output shape is (..., weight.shape[0]). We want output shape (..., P), so we need
        # weight of shape (P, ?) where the second dim matches z's last dim (E). weight = Wr.t()
        # has shape (P, E). So F.linear(z, Wr.t()) = z @ (Wr.t()).t() = z @ Wr. But we want
        # W_r^T @ z applied along the last dim, which is the same thing: z @ W_r (treating z as
        # row vector). YES — F.linear(z, Wr.t()) gives (..., P) = z @ W_r. CORRECT.
        out_r = F.linear(zr, Wr.t()) + F.linear(zi, Wi.t())
        out_i = F.linear(zi, Wr.t()) - F.linear(zr, Wi.t())
        return torch.complex(out_r, out_i)


def build_model(planner_channels: int = 32, executor_channels: int = 64,
                max_cycles: int = 4) -> RespiraCell:
    """Standard no_mirror-shaped RespiraCell.
    Same hyperparameters as Phase-3 Stage-2's build_v3hp_model but mirror_kind='control'
    (we'll run with mirror_authority=0 so the control Mirror sits idle).

    planner_channels / executor_channels parameterized for Phase 5 scale-up testing.
    Phase 4 default: 32 / 64. Phase 5a (2x): 64 / 128.
    max_cycles parameterized for Phase 5d (default 4; Phase 5d: 8).
    """
    return RespiraCell(
        planner_channels=planner_channels, executor_channels=executor_channels,
        seq_len=81, vocab_size=11,
        max_cycles=max_cycles, planner_omega=(0.05, 0.2), executor_omega=(0.5, 2.0),
        dt=0.1, mu_scale=1.0, halt_threshold=0.7,
        mirror_kind="control",
    )


def freeze_cross_organ_projections(model: RespiraCell) -> dict:
    """Set requires_grad=False on p_to_e and e_to_p. Returns counts for verification."""
    n_p_to_e = 0
    n_e_to_p = 0
    for p in model.p_to_e.parameters():
        p.requires_grad = False
        n_p_to_e += p.numel()
    for p in model.e_to_p.parameters():
        p.requires_grad = False
        n_e_to_p += p.numel()
    return {
        "p_to_e_frozen_params": n_p_to_e,
        "e_to_p_frozen_params": n_e_to_p,
        "total_frozen_params": n_p_to_e + n_e_to_p,
    }


def verify_frozen(model: RespiraCell) -> dict:
    """Sanity check: confirm p_to_e and e_to_p have requires_grad=False."""
    p_grad = [p.requires_grad for p in model.p_to_e.parameters()]
    e_grad = [p.requires_grad for p in model.e_to_p.parameters()]
    return {
        "p_to_e_any_grad": any(p_grad),
        "e_to_p_any_grad": any(e_grad),
        "p_to_e_param_count": len(p_grad),
        "e_to_p_param_count": len(e_grad),
    }


def install_shared_hermitian(model: RespiraCell) -> dict:
    """Replace model.e_to_p with HermitianSharedProjection(model.p_to_e)."""
    original_e_to_p_params = sum(p.numel() for p in model.e_to_p.parameters())
    model.e_to_p = HermitianSharedProjection(model.p_to_e)
    new_e_to_p_params = sum(p.numel() for p in model.e_to_p.parameters())
    # Sanity: HermitianSharedProjection should have zero params (source is not a submodule).
    return {
        "original_e_to_p_params": original_e_to_p_params,
        "new_e_to_p_params": new_e_to_p_params,  # should be 0
        "p_to_e_params": sum(p.numel() for p in model.p_to_e.parameters()),
    }


def run_arm(arm: str, seed: int, steps: int, batch_size: int, lr: float,
            eval_batches: int, planner_channels: int = 32, executor_channels: int = 64,
            data_dir: str | None = None, max_cycles: int = 4) -> dict:
    """Train one arm-seed, eval at checkpoints, return result dict."""
    if arm not in ARMS:
        raise ValueError(f"Unknown arm {arm!r}. Valid: {list(ARMS)}")
    cfg = ARMS[arm]
    mode = cfg["mode"]

    torch.manual_seed(seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    model = build_model(planner_channels=planner_channels, executor_channels=executor_channels, max_cycles=max_cycles).to(device)

    mode_info: dict | None = None
    if mode == "independent_learnable":
        pass  # default; nothing to do
    elif mode == "independent_frozen":
        mode_info = freeze_cross_organ_projections(model)
        verify = verify_frozen(model)
        if verify["p_to_e_any_grad"] or verify["e_to_p_any_grad"]:
            raise RuntimeError(f"FREEZE FAILED — p_to_e or e_to_p still has requires_grad=True: {verify}")
        print(f"  FROZEN: {mode_info['total_frozen_params']} params "
              f"(p_to_e={mode_info['p_to_e_frozen_params']}, "
              f"e_to_p={mode_info['e_to_p_frozen_params']})  verify={verify}")
    elif mode == "shared_hermitian":
        mode_info = install_shared_hermitian(model)
        if mode_info["new_e_to_p_params"] != 0:
            raise RuntimeError(f"SHARED INSTALL FAILED — e_to_p still has params: {mode_info}")
        # Verify the wrapper is using p_to_e's weights, not copying them.
        if model.e_to_p.source is not model.p_to_e:
            raise RuntimeError("SHARED INSTALL FAILED — wrapper.source is not model.p_to_e")
        print(f"  SHARED: e_to_p replaced with HermitianSharedProjection wrapping p_to_e. "
              f"original_e_to_p={mode_info['original_e_to_p_params']} params (dropped); "
              f"p_to_e={mode_info['p_to_e_params']} params (now shared bidirectionally).")
    elif mode == "stiefel_constrained":
        mode_info = install_stiefel_projections(model)
        print(f"  STIEFEL: p_to_e + e_to_p replaced with StiefelComplexLinear "
              f"({mode_info['p_to_e_isometry_kind']}, {mode_info['e_to_p_isometry_kind']}). "
              f"params: p_to_e={mode_info['new_p_to_e_params']}, e_to_p={mode_info['new_e_to_p_params']} "
              f"(unconstrained underlying; QR-retraction at forward).")
    elif mode == "temporal_extension":
        mode_info = install_temporal_extension(model, lambda_decay=cfg["lambda_decay"])
        print(f"  TEMPORAL: p_to_e + e_to_p wrapped with TemporalExtensionWrapper "
              f"(lambda_decay={mode_info['lambda_decay']}). Single-decay history buffer; "
              f"p_to_e params={mode_info['p_to_e_params']}, e_to_p params={mode_info['e_to_p_params']} "
              f"(underlying ComplexLinear unchanged; wrapper adds zero learnable params).")
    elif mode == "adaptive_temporal_extension":
        mode_info = install_adaptive_temporal(model, hidden_dim=cfg["hidden_dim"])
        print(f"  ADAPTIVE-TEMPORAL: p_to_e + e_to_p wrapped with AdaptiveTemporalExtensionWrapper "
              f"(hidden_dim={mode_info['hidden_dim']}). Gate(raw.abs()) → λ per-batch-per-position. "
              f"p_to_e params={mode_info['p_to_e_params']}, e_to_p params={mode_info['e_to_p_params']} "
              f"(source ComplexLinear + small gate MLP).")

    # Optimizer over only trainable params (so frozen params don't waste optimizer state).
    trainable = [p for p in model.parameters() if p.requires_grad]
    opt = AdamW(trainable, lr=lr, weight_decay=0.01, betas=(0.9, 0.95))

    loader_kwargs = {"batch_size": batch_size}
    if data_dir is not None:
        loader_kwargs["data_dir"] = data_dir
    train_loader = make_loader(split="train", shuffle=True, **loader_kwargs)
    it = cycle_loader(train_loader)
    test_loader = make_loader(split="test", shuffle=False, **loader_kwargs)

    print(f"\n  ARM={arm}  seed={seed}  steps={steps}  mode={mode}  "
          f"trainable_params={sum(p.numel() for p in trainable)}")
    t0 = time.time()

    checkpoint_results = {}
    losses = []
    next_ckpt_idx = 0

    model.train()
    for step in range(1, steps + 1):
        x, y = next(it)
        x, y = x.to(device, non_blocking=True), y.to(device, non_blocking=True)

        # Stage 4: reset temporal-extension history buffers per-batch (prevents leakage
        # across batches; each forward call starts with fresh history).
        if mode == "temporal_extension":
            reset_temporal_history(model)

        # No-mirror forward: mirror_authority=0 means defaults used; arch_variant=default.
        logits, _, aux = model(
            x,
            mirror_authority=0.0,
            arch_variant="default",
        )
        task_loss = F.cross_entropy(
            logits.reshape(-1, logits.shape[-1]),
            y.reshape(-1), ignore_index=IGNORE_LABEL_ID,
        )
        if mode == "soft_stiefel_penalty":
            pen = soft_stiefel_penalty(model)
            loss = task_loss + cfg["lambda_stiefel"] * pen
            # Track penalty separately for diagnostics
            if step <= 5 or step % 500 == 0:
                print(f"    step {step:>5d}  task_loss={task_loss.item():.4f}  "
                      f"stiefel_penalty={pen.item():.4f}")
        else:
            loss = task_loss  # No supervisor / penalty for other modes.

        if not torch.isfinite(loss):
            print(f"    step {step}: NaN/Inf loss — aborting this arm-seed.")
            return {"arm": arm, "seed": seed, "aborted": True, "losses": losses}

        opt.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(trainable, 1.0)
        opt.step()
        losses.append(float(task_loss.item()))

        if next_ckpt_idx < len(CHECKPOINTS) and step == CHECKPOINTS[next_ckpt_idx]:
            ckpt_step = CHECKPOINTS[next_ckpt_idx]
            result = evaluate(
                model, "respira", test_loader, device=device,
                max_batches=eval_batches, record_trajectory=True,
                arch_variant="default",
            )
            ia = result.get("inside_analysis") or {}
            checkpoint_results[str(ckpt_step)] = {
                "token_accuracy": result["token_accuracy"],
                "exact_accuracy": result["exact_accuracy"],
                "mean_loss_per_token": result["mean_loss_per_token"],
                "task_loss_recent": sum(losses[-20:]) / min(len(losses), 20),
                "mean_halt_cycle": ia.get("mean_halt_cycle"),
                "mean_confidence_at_halt": ia.get("mean_confidence_at_halt"),
                "frac_halted_by_cycle_2": ia.get("frac_halted_by_cycle_2"),
                "calib_spearman_conf_vs_correctness": ia.get("calib_spearman_conf_vs_correctness"),
            }
            def _fmt(v, fmt):
                return format(v, fmt) if v is not None else "n/a"
            print(f"    step {ckpt_step:>4d}  token_acc={result['token_accuracy']:.4f}  "
                  f"exact={result['exact_accuracy']:.4f}  "
                  f"halt={_fmt(ia.get('mean_halt_cycle'), '.2f')}")
            model.train()
            next_ckpt_idx += 1

    elapsed = time.time() - t0
    print(f"    DONE  arm={arm} seed={seed}  elapsed={elapsed:.0f}s")
    return {
        "arm": arm, "seed": seed, "elapsed_s": elapsed,
        "mode": mode,
        "mode_info": mode_info,
        "checkpoints": checkpoint_results,
        "first_task_loss": losses[0],
        "last_task_loss": losses[-1],
        "aborted": False,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=str, default="0,1,2")
    ap.add_argument("--steps", type=int, default=2500)
    ap.add_argument("--batch_size", type=int, default=64)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--eval_batches", type=int, default=20)
    ap.add_argument("--arms", type=str, default="v22_matrix",
                    help=f"Comma-separated arm names. Valid: {list(ARMS)}")
    ap.add_argument("--planner_channels", type=int, default=32,
                    help="Planner organ channel count (default 32; Phase 5a 2x scale: 64)")
    ap.add_argument("--executor_channels", type=int, default=64,
                    help="Executor organ channel count (default 64; Phase 5a 2x scale: 128)")
    ap.add_argument("--data_dir", type=str, default=None,
                    help="HRM dataset path (default = sudoku-easy-1k-aug-1000; Phase 5b: sudoku-extreme-1k-aug-1000)")
    ap.add_argument("--max_cycles", type=int, default=4,
                    help="RespiraCell max recurrent cycles (default 4; Phase 5d: 8)")
    ap.add_argument("--out", type=str, default=None)
    args = ap.parse_args()

    seeds = [int(s) for s in args.seeds.split(",")]
    arms = [a.strip() for a in args.arms.split(",")]
    for arm in arms:
        if arm not in ARMS:
            raise ValueError(f"Unknown arm {arm!r}. Valid: {list(ARMS)}")

    if args.out:
        out_path = args.out
    else:
        out_path = f"phase4_stage1_results_{datetime.now().strftime('%Y-%m-%d')}.json"

    print("=" * 70)
    print("  RESPIRA PHASE 4 STAGE 1 — §2.1-FIXED BAKE-OFF ARM")
    print(f"  seeds={seeds}  steps={args.steps}  batch={args.batch_size}  lr={args.lr}")
    print(f"  arms={arms}")
    print(f"  output: {out_path}")
    print("=" * 70)

    all_results = {
        "metadata": {
            "started_at": datetime.now(timezone.utc).isoformat(),
            "seeds": seeds,
            "steps": args.steps,
            "batch_size": args.batch_size,
            "lr": args.lr,
            "eval_batches": args.eval_batches,
            "arms": arms,
            "arm_configs": {a: ARMS[a] for a in arms},
            "pre_registration": "palace/south/respira-phase4-stage1-v21-fixed-preregistration-2026-05-29.md",
            "ratified_by": "Clayton",
            "ratified_at": "2026-05-29 evening",
        },
        "runs": [],
    }

    t_total = time.time()
    for arm in arms:
        for seed in seeds:
            print(f"\n--- ARM {arm}  SEED {seed} ---")
            result = run_arm(
                arm=arm, seed=seed, steps=args.steps,
                batch_size=args.batch_size, lr=args.lr,
                eval_batches=args.eval_batches,
                planner_channels=args.planner_channels,
                executor_channels=args.executor_channels,
                data_dir=args.data_dir,
                max_cycles=args.max_cycles,
            )
            all_results["runs"].append(result)
            with open(out_path, "w") as f:
                json.dump(all_results, f, indent=2)

    all_results["metadata"]["elapsed_total_s"] = time.time() - t_total
    with open(out_path, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\n{'=' * 70}")
    print(f"  STAGE 1 SWEEP DONE — {len(all_results['runs'])} runs, "
          f"{(time.time() - t_total)/60:.1f} min total")
    print(f"  results: {out_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
