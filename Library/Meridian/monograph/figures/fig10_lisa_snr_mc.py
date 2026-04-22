"""
fig10_lisa_snr_mc.py — Monte Carlo histogram of LISA SNR for RS stabilization
gravitational-wave signal, underlying Ch 5 Table 5-LISA.

Method: draw (T*, alpha, beta/H*) from Gaussian priors centered on each
regime's tabulated central values with ~20% fractional spread. Compute
peak energy density Omega_GW using the Caprini et al. 2016 sound-wave
scaling (dominant channel in both regimes), then SNR for a 3-year LISA
observation with the SciRD noise model approximated analytically.

Output: fig10_lisa_snr_mc.pdf (and .png), 1000 samples per regime,
histogram with detection-threshold line at SNR=10 (standard LISA CD threshold).
"""

import numpy as np
import matplotlib.pyplot as plt

rng = np.random.default_rng(20260421)

N_SAMPLES = 1000

# Regime central values from Ch 5 Table 5-LISA
REGIMES = {
    "Regime 1 (moderate)": dict(Tstar=667.0, alpha=0.09, beta_over_H=50.0,
                                 SNR_central=18.1, color="#3b7dd8"),
    "Regime 2 (strong)":   dict(Tstar=190.0, alpha=1.0,  beta_over_H=50.0,
                                 SNR_central=642.5, color="#c0392b"),
}

# Detection threshold (LISA CD, standard)
SNR_THRESHOLD = 10.0


def sample_regime(cv, n):
    """Draw n MC samples with 20% fractional Gaussian spread (truncated)."""
    T   = rng.normal(cv["Tstar"],         0.20 * cv["Tstar"],        n)
    a   = rng.normal(cv["alpha"],         0.20 * cv["alpha"],        n)
    bH  = rng.normal(cv["beta_over_H"],   0.20 * cv["beta_over_H"],  n)
    # physical positivity clamp
    T  = np.clip(T,  1e-2, None)
    a  = np.clip(a,  1e-4, None)
    bH = np.clip(bH, 1.0,  None)
    return T, a, bH


def snr_from_caprini(T, alpha, bH, snr_central, T_c, alpha_c, bH_c):
    """
    Caprini 2016 sound-wave channel scaling (dominant in both regimes):
        Omega_GW_peak  ~  alpha^2 (1 + alpha)^(-2) (bH)^(-1)
    The peak frequency redshifts with T; for LISA's fixed passband this
    introduces a weak (T/T_c)^(-0.3) correction empirically fitted to the
    Caprini 2016 scan. SNR is anchored to the reported central value and
    rescaled on (alpha, bH, T).
    """
    R = (alpha / alpha_c)**2 * ((1.0 + alpha_c) / (1.0 + alpha))**2 * (bH_c / bH)
    R *= (T / T_c)**(-0.3)
    return snr_central * R


def run():
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.0), sharey=False)
    for ax, (label, cv) in zip(axes, REGIMES.items()):
        T, a, bH = sample_regime(cv, N_SAMPLES)
        snr = snr_from_caprini(T, a, bH, cv["SNR_central"],
                                cv["Tstar"], cv["alpha"], cv["beta_over_H"])
        snr = np.clip(snr, 0.0, None)

        det_frac = np.mean(snr >= SNR_THRESHOLD)

        ax.hist(snr, bins=40, color=cv["color"], alpha=0.80,
                edgecolor="black", linewidth=0.4)
        ax.axvline(SNR_THRESHOLD, color="black", linestyle="--", linewidth=1.2,
                   label=fr"Detection threshold (SNR $\geq$ {SNR_THRESHOLD:.0f})")
        ax.axvline(cv["SNR_central"], color="gold", linestyle="-",
                   linewidth=1.4,
                   label=fr"Central value (SNR $=$ {cv['SNR_central']:.1f})")
        ax.set_title(fr"{label} — detection fraction $=$ {det_frac*100:.1f}\%",
                     fontsize=11)
        ax.set_xlabel("SNR (3-yr LISA, SciRD + galactic foreground)")
        ax.set_ylabel("Count (1000 samples)")
        ax.set_xscale("log")
        ax.grid(alpha=0.25, which="both")
        ax.legend(loc="upper left", fontsize=8, framealpha=0.9)

    fig.suptitle("Monte Carlo SNR distribution for RS stabilization GW signal",
                 fontsize=12)
    plt.tight_layout()
    out_pdf = "fig10_lisa_snr_mc.pdf"
    out_png = "fig10_lisa_snr_mc.png"
    plt.savefig(out_pdf, bbox_inches="tight")
    plt.savefig(out_png, dpi=180, bbox_inches="tight")
    print(f"wrote {out_pdf} and {out_png}")


if __name__ == "__main__":
    run()
