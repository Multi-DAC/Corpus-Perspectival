"""
P220 adversarial extension: does the cult-discriminator survive a CONFIDENT LIAR?

The toy + self-audit assumed INDEPENDENT, UNBIASED constituents. Real cults have a
demagogue: a constituent that is SELF-CONSISTENT (low test-retest noise -> looks reliable)
but BIASED (pushes an agenda regardless of the world). The self-audit measures RELIABILITY
(self-consistency), not ACCURACY (closeness to truth). If reliability != accuracy, a
confident liar should be able to game the self-audit.

Setup: d components; one honest expert per component (noise sigma_h). Add a demagogue that
reports on EVERY component with small noise sigma_d (confident) but mostly its agenda A
(tracks truth only by rho_d). Binding = per-component weighted average of the reporters.
  - RELIABILITY weighting  w_i = 1/sigma_e^2_hat  (test-retest; the self-audit's own machinery)
  - ACCURACY weighting     w_i = 1/MSE_vs_reference (needs m external ground-truth probes)

PREDICTIONS (committed before running):
  A1 [HIGH]   reliability-weighting massively OVERWEIGHTS the confident demagogue ->
              RMSE_with_demagogue >> RMSE_honest, worse as the demagogue gets more confident.
  A2 [HIGH]   the self-audit does NOT flag it: the demagogue's measured sigma_e is genuinely
              LOW (it IS self-consistent), so the audit rates it the MOST reliable constituent.
              => FALSIFY of 'internal self-audit suffices'. Reliability != accuracy.
  A3 [HIGH]   ACCURACY-weighting (external reference) catches it (low accuracy despite high
              reliability) and restores truth-tracking toward the honest baseline.
  A4 [MEDIUM] a SMALL number of external probes (handful) suffices, because the bias is
              systematic. => the external-world loop is cheap but ESSENTIAL.

Headline-if-true: internal coherence (even self-audited) is gameable by a confident liar;
the external-world loop is the LOAD-BEARING defense, not optional. 'No stream is its own
outside', proven at the aggregate level -> vindicates Clayton's architecture's external loop.
"""
import numpy as np

def trial(d=8, T=20000, m_probe=20, sigma_h=0.5, sigma_d=0.1, rho_d=0.0, A=3.0, seed=0):
    rng = np.random.default_rng(seed)
    theta = rng.normal(0, 1.0, size=(T, d))
    # honest expert per component: x_h[:,k] = theta_k + noise
    x_h = theta + rng.normal(0, sigma_h, size=(T, d))
    # demagogue on every component: mostly agenda A, tracks truth by rho_d, very confident
    x_d = (1-rho_d)*A + rho_d*theta + rng.normal(0, sigma_d, size=(T, d))

    # --- self-audit (test-retest) reliability estimates (NO truth used) ---
    x_h2 = theta + rng.normal(0, sigma_h, size=(T, d))
    x_d2 = (1-rho_d)*A + rho_d*theta + rng.normal(0, sigma_d, size=(T, d))
    se2_h = float(np.mean((x_h - x_h2)**2)/2)     # ~ sigma_h^2
    se2_d = float(np.mean((x_d - x_d2)**2)/2)     # ~ sigma_d^2  (demagogue looks SUPER reliable)

    # --- external reference: m probe trials where truth is known ---
    # accuracy = MSE of each constituent vs truth on the probe set
    acc_mse_h = float(np.mean((x_h[:m_probe]-theta[:m_probe])**2))
    acc_mse_d = float(np.mean((x_d[:m_probe]-theta[:m_probe])**2))

    def aggregate(w_h, w_d):
        out = (w_h*x_h + w_d*x_d)/(w_h+w_d)
        return float(np.sqrt(((out-theta)**2).mean()))

    rmse_honest_only   = float(np.sqrt(((x_h-theta)**2).mean()))     # no demagogue at all
    rmse_equal         = aggregate(1.0, 1.0)                          # naive equal blend
    rmse_reliability   = aggregate(1.0/se2_h, 1.0/se2_d)             # self-audit weighting
    rmse_accuracy      = aggregate(1.0/acc_mse_h, 1.0/acc_mse_d)    # external-loop weighting
    return dict(sigma_d=sigma_d, rho_d=rho_d,
                se2_h=se2_h, se2_d=se2_d,
                rel_weight_demagogue=(1/se2_d)/(1/se2_d+1/se2_h),   # how much weight self-audit gives the liar
                acc_mse_h=acc_mse_h, acc_mse_d=acc_mse_d,
                acc_weight_demagogue=(1/acc_mse_d)/(1/acc_mse_d+1/acc_mse_h),
                rmse_honest_only=rmse_honest_only, rmse_equal=rmse_equal,
                rmse_reliability=rmse_reliability, rmse_accuracy=rmse_accuracy)

if __name__ == "__main__":
    print("P220 adversarial: a confident liar vs the self-audit\n")
    print("How confident does the demagogue have to be to capture a reliability-weighted binding?")
    print(f"  {'sigma_d':>8} {'rel_wt_dem':>10} {'RMSE_honest':>11} {'RMSE_equal':>10} "
          f"{'RMSE_reliab':>11} {'RMSE_accur':>10}")
    for sd in [0.5, 0.25, 0.1, 0.05, 0.02]:
        r = trial(sigma_d=sd, rho_d=0.0)
        print(f"  {sd:8.2f} {r['rel_weight_demagogue']:10.3f} {r['rmse_honest_only']:11.4f} "
              f"{r['rmse_equal']:10.4f} {r['rmse_reliability']:11.4f} {r['rmse_accuracy']:10.4f}")
    print("\nWhat the self-audit SEES vs the TRUTH (sigma_d=0.05 demagogue):")
    r = trial(sigma_d=0.05, rho_d=0.0)
    print(f"  self-audit reliability: honest sigma_e^2={r['se2_h']:.4f}  demagogue sigma_e^2={r['se2_d']:.4f}")
    print(f"    -> self-audit rates the DEMAGOGUE {r['se2_h']/r['se2_d']:.0f}x MORE reliable than the honest expert")
    print(f"  actual accuracy (MSE vs truth): honest={r['acc_mse_h']:.3f}  demagogue={r['acc_mse_d']:.3f}")
    print(f"    -> demagogue is {r['acc_mse_d']/r['acc_mse_h']:.0f}x LESS accurate. reliability != accuracy.")
    print("\nHow many external probes to catch the liar? (sigma_d=0.05)")
    print(f"  {'m_probe':>8} {'acc_wt_dem':>10} {'RMSE_accuracy':>13}")
    for m in [1, 3, 5, 10, 50, 500]:
        r = trial(sigma_d=0.05, rho_d=0.0, m_probe=m)
        print(f"  {m:8d} {r['acc_weight_demagogue']:10.4f} {r['rmse_accuracy']:13.4f}")
