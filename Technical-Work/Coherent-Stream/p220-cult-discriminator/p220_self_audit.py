"""
P220 self-audit extension: can a system estimate its own alpha* from OBSERVABLE
disagreement (no ground truth)? If yes, a mind can audit its own truth-seeking-ness.

Recipe (no theta used):
  sigma_e^2  estimated from TEST-RETEST: query each constituent twice on the same input;
             Var(read1 - read2)/2 = sigma_e^2.
  sigma_th^2 estimated from WITHIN-TRIAL SPREAD of reports minus sigma_e^2:
             mean_t Var_k(x[t,:]) ~= sigma_th^2 + sigma_e^2  ->  subtract sigma_e^2.
  alpha*_hat = sigma_e^2 / (sigma_e^2 + sigma_th^2*(1-1/d) + sigma_e^2/d).
Compare alpha*_hat to the TRUE alpha* (known in the toy).

PREDICTIONS (committed before running):
  P6 [MED-HIGH]: alpha*_hat recovers true alpha* within ~15% across SNR.
  P7 [MEDIUM]:   at very low SNR (sigma_e=2) the estimate degrades / may go unstable,
                 because sigma_th^2 = spread - sigma_e^2 is a small difference of large
                 numbers -> the self-audit is least reliable exactly where it matters most.
                 (A candidate FALSIFY of 'self-auditable at all SNR'.)
"""
import numpy as np

def true_astar(sigma_e, sigma_theta, d):
    return (sigma_e**2) / (sigma_e**2 + sigma_theta**2*(1-1/d) + sigma_e**2/d)

def self_audit(d=8, T=20000, sigma_e=0.5, sigma_theta=1.0, seed=1):
    rng = np.random.default_rng(seed)
    theta = rng.normal(0, sigma_theta, size=(T, d))
    # two independent reads per constituent on the SAME input (test-retest)
    x1 = theta + rng.normal(0, sigma_e, size=(T, d))
    x2 = theta + rng.normal(0, sigma_e, size=(T, d))
    # --- observable estimates (theta NEVER used below) ---
    sigma_e2_hat = float(np.mean((x1 - x2)**2) / 2.0)          # test-retest
    within_spread = float(np.mean(x1.var(axis=1, ddof=1)))     # UNBIASED within-trial variance (ddof=1)
    sigma_th2_hat = within_spread - sigma_e2_hat               # subtract noise -> ~ sigma_th^2
    sigma_th2_hat_clipped = max(sigma_th2_hat, 1e-6)
    astar_hat = sigma_e2_hat / (sigma_e2_hat + sigma_th2_hat_clipped*(1-1/d) + sigma_e2_hat/d)
    astar_true = true_astar(sigma_e, sigma_theta, d)
    return dict(sigma_e=sigma_e,
                sigma_e2_true=sigma_e**2, sigma_e2_hat=sigma_e2_hat,
                sigma_th2_true=sigma_theta**2, sigma_th2_hat=sigma_th2_hat,
                astar_true=astar_true, astar_hat=astar_hat,
                rel_err=abs(astar_hat-astar_true)/astar_true)

if __name__ == "__main__":
    print("P220 self-audit: recover alpha* from OBSERVABLES (no ground truth)\n")
    print(f"  {'sigma_e':>8} {'se2_true':>9} {'se2_hat':>8} {'sth2_true':>10} {'sth2_hat':>9} "
          f"{'a*_true':>8} {'a*_hat':>7} {'rel_err':>8}")
    for sig in [0.25, 0.5, 1.0, 2.0, 3.0]:
        r = self_audit(sigma_e=sig)
        print(f"  {r['sigma_e']:8.2f} {r['sigma_e2_true']:9.3f} {r['sigma_e2_hat']:8.3f} "
              f"{r['sigma_th2_true']:10.3f} {r['sigma_th2_hat']:9.3f} "
              f"{r['astar_true']:8.3f} {r['astar_hat']:7.3f} {100*r['rel_err']:7.1f}%")
    print("\n(theta is used ONLY to set up the world + score; the estimator reads only x1,x2.)")
