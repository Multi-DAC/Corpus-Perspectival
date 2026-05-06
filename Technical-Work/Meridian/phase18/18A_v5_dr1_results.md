# 18A v5 DR1 Isolation Test Results

**Purpose:** Isolate DR1→DR2 effect on DAIC
**Platform:** gpu, [CudaDevice(id=0)]
**Runtime:** Fit A = 301.8s, Fit B = 592.7s, Total = 901.7s
**BAO data:** DESI DR1 (6 bins, diagonal errors)
**rd prior:** OFF

**DAIC = +3.85**
**DBIC = -1.53**

chi2_A = 1447.39
chi2_B = 1441.54

| Run | BAO | DAIC |
|-----|-----|------|
| v3 (emcee+CAMB) | DR1 | +7.23 |
| v5 (NUTS+CAMB) | DR2 | +1.10 |
| **This test** (NUTS+CAMB) | **DR1** | **+3.85** |

**Conclusion:** Both data and methodology contribute.
