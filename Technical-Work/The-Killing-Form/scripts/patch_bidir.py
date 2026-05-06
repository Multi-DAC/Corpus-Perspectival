"""Patch train_kf_300m.py to add bidirectional KF objective."""
import sys

SCRIPT_PATH = "/home/clawd/train_kf_300m.py"

with open(SCRIPT_PATH, "r") as f:
    content = f.read()

# 1. Add 'bidirectional' to kf_objective choices
old_choices = 'choices=["linear", "log", "adaptive", "gated"]'
new_choices = 'choices=["linear", "log", "adaptive", "gated", "bidirectional"]'
if old_choices not in content:
    if "bidirectional" in content:
        print("Already patched — bidirectional already in choices")
        sys.exit(0)
    print("ERROR: Could not find choices line")
    sys.exit(1)
content = content.replace(old_choices, new_choices)

# 2. Update help text
content = content.replace(
    'help="KF objective: linear=-lam*H_CV, log=-lam*log(H_CV), adaptive=-CE/H_CV*H_CV, gated=per-layer gradient alignment"',
    'help="KF objective: linear/log/adaptive/gated/bidirectional"'
)

# 3. Add --kf_threshold argument after kf_every
old_kf_every = '    parser.add_argument("--kf_every", type=int, default=50)'
new_kf_every = (
    '    parser.add_argument("--kf_every", type=int, default=50)\n'
    '    parser.add_argument("--kf_threshold", type=float, default=0.1,\n'
    '                        help="Cosine threshold for bidirectional gating")'
)
content = content.replace(old_kf_every, new_kf_every)

# 4. Insert bidirectional block before the standard KF objectives block
bidir_block = r'''
                elif args.kf_objective == "bidirectional":
                    # --- BIDIRECTIONAL GRADIENT-GATED KF (three-mode) ---
                    ce_grads = {}
                    for layer_idx, layer in enumerate(raw_model.inner.H_level.layers):
                        p = layer.self_attn.qkv_proj.weight
                        if p.grad is not None:
                            ce_grads[layer_idx] = p.grad.detach().clone()

                    layer_data = compute_h_module_cv_per_layer(raw_model, device)
                    h_cv_val = torch.stack([ld[1] for ld in layer_data]).mean()

                    optimizer.zero_grad()
                    build_layers = []
                    neutral_layers = []
                    dissolve_layers = []
                    threshold = args.kf_threshold
                    for layer_idx, layer_cv, param_ref in layer_data:
                        layer_loss = -current_lambda * layer_cv
                        layer_loss.backward(retain_graph=True)

                        if layer_idx in ce_grads and param_ref.grad is not None:
                            kf_grad = param_ref.grad.detach().flatten()
                            ce_grad = ce_grads[layer_idx].flatten()
                            cos_sim = torch.dot(kf_grad, ce_grad) / (
                                torch.norm(kf_grad) * torch.norm(ce_grad) + 1e-20)
                            cos_val = cos_sim.item()
                            if cos_val > threshold:
                                # CRYSTALLIZE — build structure
                                build_layers.append((layer_idx, cos_val))
                            elif cos_val < -threshold:
                                # DISSOLVE — reverse gradient, dismantle structure
                                param_ref.grad.mul_(-1.0)
                                dissolve_layers.append((layer_idx, cos_val))
                            else:
                                # NEUTRAL — weak signal, leave alone
                                param_ref.grad.zero_()
                                neutral_layers.append(layer_idx)

                    for p in raw_model.inner.L_level.parameters():
                        if p.grad is not None:
                            p.grad.zero_()

                    optimizer.step()
                    kf_reg_applications += 1

                    if kf_reg_applications % 10 == 0:
                        n_total = len(layer_data)
                        n_build = len(build_layers)
                        n_dissolve = len(dissolve_layers)
                        n_neutral = len(neutral_layers)
                        avg_b = sum(c for _, c in build_layers) / max(n_build, 1)
                        avg_d = sum(c for _, c in dissolve_layers) / max(n_dissolve, 1)
                        print("  [Step %d] KF-bidir #%d: H_CV=%.6e  build=%d  neutral=%d  dissolve=%d  /%d  avg_cos_b=%.4f  avg_cos_d=%.4f" % (
                            global_step, kf_reg_applications, h_cv_val.item(),
                            n_build, n_neutral, n_dissolve, n_total,
                            avg_b, avg_d), flush=True)

'''

old_marker = '                else:\n                    # --- STANDARD KF OBJECTIVES (linear/log/adaptive) ---'
new_marker = bidir_block + '                else:\n                    # --- STANDARD KF OBJECTIVES (linear/log/adaptive) ---'
content = content.replace(old_marker, new_marker)

with open(SCRIPT_PATH, "w") as f:
    f.write(content)

print("Bidirectional KF patch applied successfully")
print("New choices: linear, log, adaptive, gated, bidirectional")
print("New arg: --kf_threshold (default 0.1)")
