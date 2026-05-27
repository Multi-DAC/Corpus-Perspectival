"""
kf_regularizer_gemma.py — Step 0 de-risk for the v0.7 Glider full-architecture build.

Ports the Killing-form commutator-variance (CV) regularizer from the numpy
kf_monitor.compute_layer_kf into a DIFFERENTIABLE torch function on Gemma's
attention matrices, and verifies it (a) computes and (b) backprops to weights.

This is the REAL KF regularizer (Claims 1-10), distinct from the weight-space
V/Q Fisher aux ("v0.7.1", Claims 24-26) tested on Day 116.

Metric (torch translation of compute_layer_kf, CV only — abelian-fraction not needed
for the -lambda*CV regularizer): per layer, per-head attention matrices A [n_h, seq, seq];
commutators comm[a,k] = A_a@A_k - A_k@A_a; per-pair Frobenius norms normalized by
mean attention Frobenius^2; CV = variance of off-diagonal commutator norms.
"""
import argparse
import torch


def layer_commutator_cv_torch(A):
    """Differentiable commutator-variance for one layer.
    A: [n_h, seq, seq] attention matrices (single sample). Returns scalar CV (torch, grad-tracking)."""
    n_h = A.shape[0]
    # comm[a,k] = A_a @ A_k - A_k @ A_a  -> [n_h, n_h, seq, seq]
    AA = torch.einsum('aij,bjk->abik', A, A)        # A_a @ A_b
    comm = AA - AA.transpose(0, 1)                   # [A_a,A_b] = A_a@A_b - A_b@A_a
    fro = torch.sqrt(torch.einsum('abij,abij->ab', comm, comm) + 1e-20)  # [n_h,n_h]
    typ = torch.sqrt(torch.einsum('hij,hij->h', A, A) + 1e-20).mean()    # typical attn Frobenius
    fro = fro / (typ ** 2 + 1e-20)
    mask = ~torch.eye(n_h, dtype=torch.bool, device=A.device)
    off = fro[mask]
    return off.var()


def kf_regularizer(attentions, batch_index=0):
    """Sum of per-layer commutator-CV across all layers (differentiable).
    attentions: tuple of [batch, n_h, seq, seq] per layer."""
    cvs = []
    for A_layer in attentions:
        A = A_layer[batch_index]            # [n_h, seq, seq]
        cvs.append(layer_commutator_cv_torch(A))
    return torch.stack(cvs)                 # [n_layers]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model_id", default="google/gemma-3-270m")
    ap.add_argument("--seq_len", type=int, default=64)
    args = ap.parse_args()

    from transformers import AutoModelForCausalLM, AutoTokenizer
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Loading {args.model_id} with attn_implementation='eager'...", flush=True)
    tok = AutoTokenizer.from_pretrained(args.model_id)
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id, dtype=torch.float32, attn_implementation="eager"
    ).to(dev)
    model.train()

    text = "The Killing form measures the algebraic coherence of attention heads during inference."
    ids = tok(text, return_tensors="pt", truncation=True, max_length=args.seq_len).to(dev)

    out = model(**ids, output_attentions=True)
    attn = out.attentions
    print(f"attentions returned: {type(attn)}; n_layers={len(attn) if attn else 'NONE'}")
    if not attn:
        print("FALSIFY: no attentions returned even with eager. Need a different access path.")
        return
    print(f"per-layer attention shape: {tuple(attn[0].shape)}")

    cvs = kf_regularizer(attn)
    reg = cvs.sum()
    print(f"per-layer CV (first 6): {[round(c.item(),8) for c in cvs[:6]]}")
    print(f"mean CV={cvs.mean().item():.8e}  sum(reg)={reg.item():.8e}  requires_grad={reg.requires_grad}")

    # Backprop test: does -lambda*CV produce gradients on q_proj weights?
    model.zero_grad()
    (-5.0 * reg).backward()
    q0 = model.model.layers[0].self_attn.q_proj.weight
    g = q0.grad
    if g is None:
        print("FALSIFY: no gradient on layer-0 q_proj after backward.")
    else:
        nz = (g.abs() > 0).float().mean().item()
        print(f"CONFIRM: layer-0 q_proj grad present. norm={g.norm().item():.6e}  frac_nonzero={nz:.4f}")
        # also check a late layer
        gl = model.model.layers[-1].self_attn.q_proj.weight.grad
        print(f"         last-layer q_proj grad norm={gl.norm().item():.6e}" if gl is not None else "         last-layer grad MISSING")


if __name__ == "__main__":
    main()
