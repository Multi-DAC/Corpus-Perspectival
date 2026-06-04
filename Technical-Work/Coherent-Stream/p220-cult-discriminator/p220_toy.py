"""
P220 — The Cult-Discriminator Toy.
Operationalizes "coherent != truth-seeking": measures I(output;truth) vs I(output;consensus)
as a function of binding agreement-pressure alpha (= the binding's DOF / agenda).
See FINDINGS.md for the model + committed predictions.
"""
import numpy as np

def gaussian_mi(x, y):
    """MI for jointly-Gaussian via correlation: -0.5 ln(1-rho^2). Returns (mi, rho2)."""
    x = np.asarray(x, float).ravel(); y = np.asarray(y, float).ravel()
    if x.std() < 1e-12 or y.std() < 1e-12:
        return 0.0, 0.0
    rho = np.corrcoef(x, y)[0, 1]
    rho2 = min(rho * rho, 1 - 1e-12)
    return -0.5 * np.log(1 - rho2), rho2

def run(d=8, T=20000, sigma_e=0.5, sigma_theta=1.0, alphas=None, seed=0):
    rng = np.random.default_rng(seed)
    if alphas is None:
        alphas = np.linspace(0, 1, 41)
    theta = rng.normal(0, sigma_theta, size=(T, d))          # world truth
    x = theta + rng.normal(0, sigma_e, size=(T, d))          # expert i measures comp i
    c = x.mean(axis=1, keepdims=True)                        # consensus (grand mean of reports)
    rows = []
    for a in alphas:
        r = (1 - a) * x + a * c                              # laundered reports = synthesis
        out = r
        mi_t = r2_t = mi_c = r2_c = 0.0
        for k in range(d):
            m, rr = gaussian_mi(out[:, k], theta[:, k]); mi_t += m; r2_t += rr
            m, rr = gaussian_mi(out[:, k], c[:, 0]);     mi_c += m; r2_c += rr
        mi_t/=d; r2_t/=d; mi_c/=d; r2_c/=d
        rmse = float(np.sqrt(((out - theta) ** 2).mean()))
        disp = float(r.std(axis=1).mean())                  # within-trial spread (low = high agreement)
        rows.append(dict(alpha=float(a), mi_truth=mi_t, r2_truth=r2_t,
                         mi_cons=mi_c, r2_cons=r2_c, rmse=rmse, dispersion=disp))
    # single-expert baseline: knows own comp (noise sigma_e), guesses prior 0 for the other d-1
    single_rmse = float(np.sqrt((sigma_e**2)/d + (sigma_theta**2)*(d-1)/d))
    # analytic alpha* (bias-variance optimum for shrink-to-grand-mean):
    # MSE(a) = a^2 * sigma_theta^2*(1-1/d) + (1-a)^2 * sigma_e^2 + a^2 * sigma_e^2/d
    # d/da = 0 -> a* = sigma_e^2 / (sigma_e^2 + sigma_theta^2*(1-1/d) + sigma_e^2/d)
    astar = (sigma_e**2) / (sigma_e**2 + sigma_theta**2*(1-1/d) + sigma_e**2/d)
    return alphas, rows, single_rmse, astar

def summarize(tag, alphas, rows, single_rmse, astar):
    rmse = np.array([r["rmse"] for r in rows])
    r2t  = np.array([r["r2_truth"] for r in rows])
    r2c  = np.array([r["r2_cons"] for r in rows])
    a    = np.array([r["alpha"] for r in rows])
    i_best = int(np.argmin(rmse))                  # empirical alpha* (min RMSE)
    # crossover: first alpha where r2_cons >= r2_truth
    cross = next((a[i] for i in range(len(a)) if r2c[i] >= r2t[i]), None)
    print(f"\n=== {tag} ===")
    print(f"  single-expert RMSE      = {single_rmse:.4f}")
    print(f"  alpha=0 aggregate RMSE  = {rmse[0]:.4f}   (confluence gain: {single_rmse/rmse[0]:.2f}x)")
    print(f"  alpha=1 aggregate RMSE  = {rmse[-1]:.4f}  (vs single {single_rmse:.4f})")
    print(f"  alpha* analytic         = {astar:.3f}")
    print(f"  alpha* empirical(minRMSE)= {a[i_best]:.3f}  -> RMSE {rmse[i_best]:.4f}")
    print(f"  truth-tracking gain at a*: RMSE {rmse[0]:.4f} -> {rmse[i_best]:.4f} "
          f"({100*(rmse[0]-rmse[i_best])/rmse[0]:.1f}% better than alpha=0)")
    print(f"  crossover alpha (r2_cons>=r2_truth) = {cross}")
    print(f"  {'alpha':>6} {'RMSE':>7} {'r2_truth':>9} {'r2_cons':>8} {'I_truth':>8} {'I_cons':>8} {'disp':>6}")
    for r in rows[::4]:
        print(f"  {r['alpha']:6.3f} {r['rmse']:7.4f} {r['r2_truth']:9.4f} {r['r2_cons']:8.4f} "
              f"{r['mi_truth']:8.4f} {r['mi_cons']:8.4f} {r['dispersion']:6.3f}")
    return dict(tag=tag, astar_analytic=astar, astar_emp=float(a[i_best]),
                rmse0=float(rmse[0]), rmse_astar=float(rmse[i_best]), rmse1=float(rmse[-1]),
                single=single_rmse, crossover=(float(cross) if cross is not None else None))

if __name__ == "__main__":
    print("P220 cult-discriminator toy — sweeping alpha x SNR")
    summary = []
    # SNR sweep: low sigma_e = high SNR (reliable experts); high sigma_e = low SNR (noisy)
    for sig in [0.25, 0.5, 1.0, 2.0]:
        alphas, rows, single, astar = run(d=8, T=20000, sigma_e=sig, sigma_theta=1.0, seed=0)
        summary.append(summarize(f"sigma_e={sig} (SNR={1.0/sig:.2f})", alphas, rows, single, astar))
        # save full curve for the canonical sigma_e=0.5 case
        if sig == 0.5:
            import csv
            with open("p220_curve_sigma0.5.csv", "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print("\n=== alpha* vs SNR (the headline) ===")
    print(f"  {'sigma_e':>8} {'a*_analytic':>11} {'a*_emp':>7} {'RMSE@0':>7} {'RMSE@a*':>8} {'RMSE@1':>7} {'single':>7} {'cross':>6}")
    for s in summary:
        print(f"  {s['tag'].split('=')[1].split(' ')[0]:>8} {s['astar_analytic']:11.3f} {s['astar_emp']:7.3f} "
              f"{s['rmse0']:7.4f} {s['rmse_astar']:8.4f} {s['rmse1']:7.4f} {s['single']:7.4f} "
              f"{str(s['crossover']):>6}")
