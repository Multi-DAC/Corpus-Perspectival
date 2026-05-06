"""Test anti-correlation between initial per-layer CV and final per-layer CV."""
from scipy import stats

# Seed1: init and final per-layer H_CV
s1_init = [6.4956e-4, 6.5374e-4, 6.8710e-4, 6.5995e-4, 6.0601e-4, 7.2845e-4,
           5.2450e-4, 7.9209e-4, 8.7462e-4, 7.7655e-4, 6.5576e-4, 8.5874e-4]
s1_final = [2136.2, 2700.1, 929.7, 608.3, 1061.5, 2526.1,
            2729.9, 1473.9, 695.7, 423.9, 864.3, 860.6]

# Seed2: init and final
s2_init = [6.8483e-4, 6.7551e-4, 6.2243e-4, 8.2713e-4, 9.3228e-4, 5.8018e-4,
           7.9402e-4, 6.9942e-4, 6.7593e-4, 4.7963e-4, 8.4551e-4, 6.5464e-4]
s2_final = [1901.6, 2315.5, 3685.5, 1745.5, 344.7, 1859.2,
            2470.7, 1017.1, 3503.2, 2402.7, 176.0, 792.0]

# v0.6a init
v6_init = [5.7093e-4, 6.4085e-4, 7.7323e-4, 6.9549e-4, 8.7096e-4, 5.1199e-4,
           6.1614e-4, 7.5140e-4, 5.9779e-4, 7.3746e-4, 6.4798e-4, 8.0230e-4]

print("=" * 60)
print("INIT CV vs FINAL CV -- RANK CORRELATION")
print("=" * 60)

for name, init, final in [("Seed1", s1_init, s1_final), ("Seed2", s2_init, s2_final)]:
    rho, p = stats.spearmanr(init, final)
    print("\n%s: Spearman rho = %.4f, p = %.4f" % (name, rho, p))

    init_ranks = stats.rankdata(init)
    final_ranks = stats.rankdata(final)
    print("  %6s %12s %10s %12s %11s %8s" % ("Layer", "Init CV", "InitRank", "Final CV", "FinalRank", "RankDelta"))
    for i in range(12):
        delta = int(final_ranks[i] - init_ranks[i])
        print("  L%-4d %12.4e %10.0f %12.1f %11.0f %+8d" % (
            i, init[i], init_ranks[i], final[i], final_ranks[i], delta))

print("\n" + "=" * 60)
print("CROSS-SEED INIT CORRELATION")
print("=" * 60)
rho12, p12 = stats.spearmanr(s1_init, s2_init)
rho1v, p1v = stats.spearmanr(s1_init, v6_init)
rho2v, p2v = stats.spearmanr(s2_init, v6_init)
print("Seed1 vs Seed2 init: rho=%.4f, p=%.4f" % (rho12, p12))
print("Seed1 vs v0.6a init: rho=%.4f, p=%.4f" % (rho1v, p1v))
print("Seed2 vs v0.6a init: rho=%.4f, p=%.4f" % (rho2v, p2v))

print("\n" + "=" * 60)
print("CROSS-SEED FINAL CV CORRELATION")
print("=" * 60)
rho_final, p_final = stats.spearmanr(s1_final, s2_final)
print("Seed1 vs Seed2 final: rho=%.4f, p=%.4f" % (rho_final, p_final))

print("\n" + "=" * 60)
print("CROSS-SEED INIT vs OTHER FINAL")
print("=" * 60)
rho_cross, p_cross = stats.spearmanr(s2_init, s1_final)
print("Seed2 init vs Seed1 final: rho=%.4f, p=%.4f" % (rho_cross, p_cross))
rho_cross2, p_cross2 = stats.spearmanr(s1_init, s2_final)
print("Seed1 init vs Seed2 final: rho=%.4f, p=%.4f" % (rho_cross2, p_cross2))

print("\n" + "=" * 60)
print("VERDICT")
print("=" * 60)
