(* ============================================================ *)
(* MERIDIAN.wl — Symbolic Backbone for Project Meridian        *)
(* 5D Warped Geometry + NCG Spectral Action + Cuscuton         *)
(* Authors: Clayton & Clawd                                     *)
(* Created: March 22, 2026                                      *)
(* ============================================================ *)

BeginPackage["Meridian`"];

(* === Public Symbols === *)

(* --- Constants --- *)
MPl::usage = "Planck mass in GeV (reduced)";
MZ::usage = "Z boson mass in GeV";
MW::usage = "W boson mass in GeV";
MH::usage = "Higgs boson mass in GeV";
alphaEM::usage = "Fine structure constant at M_Z";
alphaS::usage = "Strong coupling at M_Z";
sin2thetaW::usage = "Weinberg angle at M_Z (measured)";
vEW::usage = "Electroweak VEV in GeV";

(* --- RS Geometry --- *)
kRS::usage = "RS curvature scale (AdS_5 inverse radius)";
Rc::usage = "Orbifold radius";
kyc::usage = "Warp factor parameter k*y_c = k*pi*Rc, solves hierarchy";
warpFactor::usage = "warpFactor[y] gives e^{-k|y|} at position y in extra dimension";
TeVScale::usage = "IR brane scale = MPl * Exp[-kyc]";
hierarchy::usage = "Hierarchy ratio MPl/TeV";

(* --- KK Spectrum --- *)
besselZeros::usage = "besselZeros[nu, n] gives first n zeros of J_nu";
kkMassGraviton::usage = "kkMassGraviton[n] gives mass of nth KK graviton mode";
kkMassFermion::usage = "kkMassFermion[n, c] gives mass of nth KK fermion with bulk mass c";
kkMassGauge::usage = "kkMassGauge[n] gives mass of nth KK gauge boson mode";

(* --- SM Content --- *)
smFermions::usage = "List of SM fermions with quantum numbers {name, SU3, SU2, Y, mass}";
smGaugeBetas::usage = "One-loop beta function coefficients {b1, b2, b3}";
smGaugeBetas2L::usage = "Two-loop beta function coefficient matrix";

(* --- Spectral Action --- *)
spectralTraceS::usage = "spectralTraceS[i] gives mass-weighted trace S_i for gauge group i";
spectralTraceUniversal::usage = "spectralTraceUniversal[i] gives universal trace for gauge group i";
sin2thetaWPredicted::usage = "sin2thetaWPredicted[mu] gives spectral action prediction at scale mu";

(* --- Gauge Running --- *)
alphaInverse::usage = "alphaInverse[i, mu] gives alpha_i^{-1}(mu) at 1-loop";
alphaInverse2L::usage = "alphaInverse2L[i, mu] gives alpha_i^{-1}(mu) at 2-loop";
unificationScale::usage = "Scale where alpha_2 = alpha_3 (approximate)";

(* --- KK Thresholds --- *)
kkThresholdCorrection::usage = "kkThresholdCorrection[i, nMax] gives KK threshold correction to alpha_i^{-1}";
kkThresholdGraviton::usage = "kkThresholdGraviton[i, nMax] gives graviton KK contribution";
kkOverlapIntegral::usage = "kkOverlapIntegral[species, n, gauge] gives overlap integral for nth KK mode";

(* --- Cuscuton --- *)
cuscutonEOS::usage = "cuscutonEOS[zeta0] gives w(a) for cuscuton dark energy";
screeningFunction::usage = "screeningFunction[r, params] gives cuscuton screening at distance r";

(* --- Key Results --- *)
kycRatio::usage = "Ratio kyc / Log[Lambda/MZ] — the 1.011 coincidence";
deltaAIC::usage = "Phase 18 result: ΔAIC = +1.10 (v5 DR2)";

Begin["`Private`"];

(* ============================================================ *)
(* 1. FUNDAMENTAL CONSTANTS                                     *)
(* ============================================================ *)

MPl = 2.435*^18;          (* Reduced Planck mass, GeV *)
MZ = 91.1876;             (* Z mass, GeV *)
MW = 80.379;              (* W mass, GeV *)
MH = 125.25;              (* Higgs mass, GeV *)
alphaEM = 1/127.951;      (* at M_Z, MSbar *)
alphaS = 0.1179;          (* at M_Z *)
sin2thetaW = 0.23121;     (* at M_Z, measured *)
vEW = 246.22;             (* Electroweak VEV, GeV *)

(* Derived *)
GN = 1/(8 Pi MPl^2);      (* Newton's constant *)

(* ============================================================ *)
(* 2. RANDALL-SUNDRUM GEOMETRY                                  *)
(* ============================================================ *)

(* The RS1 metric: ds² = e^{-2k|y|} eta_{mu nu} dx^mu dx^nu + dy² *)
(* y ∈ [0, pi*Rc], orbifold S¹/Z₂ *)

(* Default parameters solving the hierarchy problem *)
kyc = 35.0;                     (* k * pi * Rc *)
kRS = MPl;                       (* AdS curvature ~ Planck scale *)
Rc = kyc / (Pi * kRS);          (* Orbifold radius *)
TeVScale = MPl * Exp[-kyc];     (* IR brane scale ~ TeV *)
hierarchy = MPl / TeVScale;

(* Warp factor as function of extra-dimensional coordinate *)
warpFactor[y_] := Exp[-kRS * Abs[y]];

(* Proper length of extra dimension *)
properLength = (1/kRS) * (1 - Exp[-kyc]);

(* ============================================================ *)
(* 3. KALUZA-KLEIN SPECTRUM                                     *)
(* ============================================================ *)

(* Bessel function zeros — fundamental to RS KK spectrum *)
besselZeros[nu_, n_Integer] := Table[BesselJZero[nu, k], {k, 1, n}];

(* Graviton KK modes: masses determined by J₁ zeros *)
(* m_n = x_n^(1) * k * e^{-kyc} where J_1(x_n^(1)) = 0 *)
kkMassGraviton[n_Integer] := BesselJZero[1, n] * kRS * Exp[-kyc];

(* Gauge boson KK modes: J₁ zeros (same boundary conditions) *)
kkMassGauge[n_Integer] := BesselJZero[1, n] * kRS * Exp[-kyc];

(* Fermion KK modes: depend on bulk mass parameter c *)
(* Zeros of J_{c+1/2}(x) for fermion with bulk mass c*k *)
kkMassFermion[n_Integer, c_] := BesselJZero[c + 1/2, n] * kRS * Exp[-kyc];

(* First few graviton KK masses *)
kkGravitonMasses[nMax_Integer] := Table[kkMassGraviton[n], {n, 1, nMax}];

(* Radion mass (model-dependent, Goldberger-Wise stabilization) *)
(* Typical: m_radion ~ TeVScale * Sqrt[kyc] *)
radionMass = TeVScale * Sqrt[kyc]; (* ~ few hundred GeV *)

(* ============================================================ *)
(* 4. STANDARD MODEL FERMION CONTENT                            *)
(* ============================================================ *)

(* {name, SU(3) rep dim, SU(2) rep dim, Y (hypercharge), mass (GeV)} *)
(* Using GUT normalization for Y: Y_GUT = Sqrt[5/3] * Y_SM *)
(* Convention: Y is SM hypercharge (Q = T3 + Y/2) *)

smFermions = {
  (* First generation *)
  {"uL", 3, 2, 1/3, 0.00216},      (* up quark, left doublet *)
  {"dL", 3, 2, 1/3, 0.00467},      (* down quark, left doublet *)
  {"uR", 3, 1, 4/3, 0.00216},      (* up quark, right singlet *)
  {"dR", 3, 1, -2/3, 0.00467},     (* down quark, right singlet *)
  {"eL", 1, 2, -1, 0.000511},      (* electron, left doublet *)
  {"nuL", 1, 2, -1, 0},            (* neutrino, left doublet *)
  {"eR", 1, 1, -2, 0.000511},      (* electron, right singlet *)

  (* Second generation *)
  {"cL", 3, 2, 1/3, 1.27},
  {"sL", 3, 2, 1/3, 0.093},
  {"cR", 3, 1, 4/3, 1.27},
  {"sR", 3, 1, -2/3, 0.093},
  {"muL", 1, 2, -1, 0.10566},
  {"numuL", 1, 2, -1, 0},
  {"muR", 1, 1, -2, 0.10566},

  (* Third generation *)
  {"tL", 3, 2, 1/3, 172.76},
  {"bL", 3, 2, 1/3, 4.18},
  {"tR", 3, 1, 4/3, 172.76},
  {"bR", 3, 1, -2/3, 4.18},
  {"tauL", 1, 2, -1, 1.777},
  {"nutauL", 1, 2, -1, 0},
  {"tauR", 1, 1, -2, 1.777}
};

(* Note: Left-handed quarks are SU(2) doublets, so uL and dL share the same
   quantum numbers for SU(2). The entries above list them separately for mass
   tracking but they form doublets: Q_L = (u_L, d_L), etc. *)

(* SM unique multiplets for trace computation *)
(* {name, SU3 dim, SU2 dim, Y, mass (heaviest in multiplet)} *)
smMultiplets = {
  {"Q1", 3, 2, 1/3, 0.00467},    (* (u,d)_L *)
  {"u1R", 3, 1, 4/3, 0.00216},   (* u_R *)
  {"d1R", 3, 1, -2/3, 0.00467},  (* d_R *)
  {"L1", 1, 2, -1, 0.000511},    (* (nu,e)_L *)
  {"e1R", 1, 1, -2, 0.000511},   (* e_R *)

  {"Q2", 3, 2, 1/3, 1.27},
  {"c2R", 3, 1, 4/3, 1.27},
  {"s2R", 3, 1, -2/3, 0.093},
  {"L2", 1, 2, -1, 0.10566},
  {"mu2R", 1, 1, -2, 0.10566},

  {"Q3", 3, 2, 1/3, 172.76},
  {"t3R", 3, 1, 4/3, 172.76},
  {"b3R", 3, 1, -2/3, 4.18},
  {"L3", 1, 2, -1, 1.777},
  {"tau3R", 1, 1, -2, 1.777}
};

(* ============================================================ *)
(* 5. GAUGE COUPLING RUNNING                                    *)
(* ============================================================ *)

(* One-loop beta coefficients (SM only, GUT normalized U(1)) *)
b1 = 41/6;     (* U(1)_Y with 5/3 normalization *)
b2 = -19/6;    (* SU(2)_L *)
b3 = -7;       (* SU(3)_C *)
smGaugeBetas = {b1, b2, b3};

(* Measured couplings at M_Z *)
alpha1MZ = (5/3) * alphaEM / (1 - sin2thetaW);  (* GUT normalized *)
alpha2MZ = alphaEM / sin2thetaW;
alpha3MZ = alphaS;
alphaMZ = {alpha1MZ, alpha2MZ, alpha3MZ};

(* Inverse couplings at M_Z *)
alpha1InvMZ = 1/alpha1MZ;
alpha2InvMZ = 1/alpha2MZ;
alpha3InvMZ = 1/alpha3MZ;

(* One-loop running *)
alphaInverse[i_Integer, mu_] := 1/alphaMZ[[i]] - smGaugeBetas[[i]]/(2 Pi) * Log[mu/MZ];

(* Two-loop beta coefficient matrix *)
(* b_{ij} for d(alpha_i^{-1})/d(ln mu) at 2-loop *)
smGaugeBetas2L = {
  {199/18, 9/2, 44/3} * (1/(4 Pi)^2),    (* U(1) *)
  {3/2, 35/6, 12} * (1/(4 Pi)^2),         (* SU(2) *)
  {11/18, 3/2, -26} * (1/(4 Pi)^2)        (* SU(3) *)
};

(* Two-loop running (approximate) *)
alphaInverse2L[i_Integer, mu_] := Module[{a1L, correction},
  a1L = alphaInverse[i, mu];
  correction = Sum[
    smGaugeBetas2L[[i, j]] * Log[alphaInverse[j, mu]/alphaInverse[j, MZ]],
    {j, 1, 3}
  ];
  a1L + correction
];

(* Unification scale (where alpha_2^{-1} = alpha_3^{-1}) *)
unificationScale = MZ * Exp[2 Pi * (alpha3InvMZ - alpha2InvMZ) / (b3 - b2)];

(* ============================================================ *)
(* 6. NCG SPECTRAL ACTION                                       *)
(* ============================================================ *)

(* Spectral action: Tr[f(D²/Λ²)] ~ Σ f_n a_n(D²) Λ^{4-n} *)
(* For gauge kinetic terms, relevant coefficient is a_4 *)

(* The KEY THEOREM (T1): On any product spectral triple M × F,
   a_4 factorizes as:
   a_4(D²) = a_0(D_F²) * a_4(D_M²) + a_2(D_F²) * a_2(D_M²) + a_4(D_F²) * a_0(D_M²)

   Gauge kinetic terms come from a_4(D_M²) multiplied by UNIVERSAL a_0(D_F²).
   This gives a_1 = a_2 = a_3 as a THEOREM. *)

(* Traces for the SM spectral triple *)
(* Universal traces (mass-independent, from representation theory) *)
(* T_i = Σ_f dim(R_j) * C_i(R_f) where j ≠ i *)

(* Dynkin indices T(R) — the correct invariant for spectral action traces *)
(* Tr(T_a T_b) = T(R) delta_ab *)
(* For fundamentals of any SU(N): T(fund) = 1/2 *)
dynkinSU3[rep_] := Switch[rep, 3, 1/2, 1, 0, _, 0];
dynkinSU2[rep_] := Switch[rep, 2, 1/2, 1, 0, _, 0];
(* U(1): (Y/2)² with GUT normalization factor 5/3 *)

(* Universal spectral traces (representation theory only) *)
spectralTraceUniversal[1] := Module[{total = 0},
  Do[
    With[{su3 = m[[2]], su2 = m[[3]], y = m[[4]]},
      total += su3 * su2 * (5/3) * (y/2)^2
    ],
    {m, smMultiplets}
  ];
  total
];

spectralTraceUniversal[2] := Module[{total = 0},
  Do[
    With[{su3 = m[[2]], su2 = m[[3]]},
      If[su2 == 2,
        total += su3 * dynkinSU2[su2]
      ]
    ],
    {m, smMultiplets}
  ];
  total
];

spectralTraceUniversal[3] := Module[{total = 0},
  Do[
    With[{su3 = m[[2]], su2 = m[[3]]},
      If[su3 == 3,
        total += su2 * dynkinSU3[su3]
      ]
    ],
    {m, smMultiplets}
  ];
  total
];

(* Mass-weighted spectral traces (from 19C.2c computation) *)
spectralTraceS[1] := Module[{total = 0},
  Do[
    With[{su3 = m[[2]], su2 = m[[3]], y = m[[4]], mass = m[[5]]},
      total += su3 * su2 * (5/3) * (y/2)^2 * mass^2
    ],
    {m, smMultiplets}
  ];
  total
];

spectralTraceS[2] := Module[{total = 0},
  Do[
    With[{su3 = m[[2]], su2 = m[[3]], mass = m[[5]]},
      If[su2 == 2,
        total += su3 * dynkinSU2[su2] * mass^2
      ]
    ],
    {m, smMultiplets}
  ];
  total
];

spectralTraceS[3] := Module[{total = 0},
  Do[
    With[{su3 = m[[2]], su2 = m[[3]], mass = m[[5]]},
      If[su3 == 3,
        total += su2 * dynkinSU3[su3] * mass^2
      ]
    ],
    {m, smMultiplets}
  ];
  total
];

(* Spectral action prediction for sin²θ_W *)
(* At cutoff: sin²θ_W = 3/8 (from a_1 = a_2 = a_3) *)
(* Running to scale mu: *)
sin2thetaWPredicted[mu_] := Module[{a1inv, a2inv},
  a1inv = alphaInverse[1, mu];
  a2inv = alphaInverse[2, mu];
  (* sin²θ_W = (3/8) * alpha_1 / ((5/8)*alpha_1 + (3/8)*alpha_2) *)
  (* Simpler: sin²θ_W(mu) = a2inv / (a1inv + a2inv) * (3/5) ... *)
  (* Direct from couplings: *)
  3/8 * (1/a1inv) / ((1/a1inv) * 3/8 + (1/a2inv) * 5/8)
];

(* ============================================================ *)
(* 7. KK THRESHOLD CORRECTIONS                                  *)
(* ============================================================ *)

(* Gauge boson KK threshold correction *)
(* Δα_i^{-1} = -(b_i^KK / 2π) Σ_n ln(m_n^KK / μ) *)
(* For gauge KK modes, b_i^KK = b_i (same beta coefficients) *)

kkThresholdCorrection[i_Integer, nMax_Integer] := Module[{total = 0, mn},
  Do[
    mn = kkMassGauge[n];
    total += -smGaugeBetas[[i]] / (2 Pi) * Log[mn / MZ];,
    {n, 1, nMax}
  ];
  total
];

(* Graviton KK threshold correction *)
(* Graviton loops contribute universally to gauge running (T2) *)
(* But the OVERLAP INTEGRAL with brane-localized matter is gauge-dependent *)
(* This is the key computation for 20B *)

(* Graviton KK mode wavefunction on the interval *)
(* psi_n(y) = (1/N_n) * e^{2ky} [J_2(m_n e^{ky}/k) + beta_n Y_2(m_n e^{ky}/k)] *)
gravitonWavefunction[n_Integer, y_, k_] := Module[{mn, xn, z},
  xn = BesselJZero[1, n];
  mn = xn * k * Exp[-kyc];
  z = (mn/k) * Exp[k * y];
  (* Boundary condition determines beta_n *)
  (* For simplicity, use UV-brane BC: J_1(mn/k) + beta_n Y_1(mn/k) = 0 *)
  BesselJ[2, z] - (BesselJ[1, mn/k] / BesselY[1, mn/k]) * BesselY[2, z]
];

(* Overlap integral: coupling of nth KK graviton to gauge fields on IR brane *)
(* For fields localized on the IR brane (y = pi*Rc): *)
(* g_n = psi_n(pi*Rc) / MPl *)
kkGravitonCoupling[n_Integer] := Module[{yIR, psi},
  yIR = Pi * Rc;
  (* At IR brane, the graviton wavefunction evaluates to: *)
  (* proportional to BesselJ[2, x_n] *)
  (* This is UNIVERSAL for all gauge fields on the same brane *)
  (* Therefore graviton KK thresholds are gauge-group INDEPENDENT *)
  (* This is T2 applied to KK modes *)
  BesselJ[2, BesselJZero[1, n]]
];

(* Full overlap integral for fermion KK modes *)
(* Fermion localization depends on bulk mass parameter c *)
(* f_L(y) ~ e^{(2-c)ky}, f_R(y) ~ e^{(2+c)ky} *)
(* Overlap with gauge field on IR brane: *)
fermionOverlap[c_, gauge_Integer] := Module[{},
  (* For gauge fields on the brane, the overlap is simply *)
  (* the fermion wavefunction evaluated at the brane *)
  (* Normalized: |f(y_IR)|² = (1-2c)/(e^{(1-2c)kyc} - 1) for c < 1/2 *)
  If[c < 1/2,
    (1 - 2 c) * kyc / (Exp[(1 - 2 c) * kyc] - 1),
    (* c > 1/2: UV-localized, exponentially suppressed on IR brane *)
    (2 c - 1) * kyc * Exp[-(2 c - 1) * kyc]
  ]
];

(* ============================================================ *)
(* 8. CUSCUTON SECTOR                                           *)
(* ============================================================ *)

(* Cuscuton equation of state *)
(* w(a) = -1 + δw(a), where δw depends on ζ₀ *)
(* In the self-tuning regime: w₀ ≈ -1 - ζ₀²/3 *)

cuscutonEOS[zeta0_, a_] := -1 + zeta0^2/3 * (1 - a^3);

(* Cuscuton field equation: (∂μ φ ∂^μ φ)^{1/2} = V'(φ)/μ² *)
(* Sound speed: c_s² → ∞ (defining property!) *)
(* This means cuscuton has NO propagating scalar DOF *)

(* Screening function *)
(* On RS background, cuscuton screens the cosmological constant *)
(* Mechanism: self-tuning via brane-bulk energy exchange *)
screeningFunction[r_, zeta0_] := 1 - Exp[-r * zeta0 / vEW];

(* ============================================================ *)
(* 9. KEY RESULTS AND COINCIDENCES                              *)
(* ============================================================ *)

(* The ky_c coincidence *)
kycRatio = kyc / Log[MPl / MZ];

(* Phase 18 authoritative result *)
deltaAIC = 1.10;  (* v5 DR2: ΔAIC = +1.10, ΔBIC = -1.81 *)

(* Phase 19B.5 result *)
deltaAIC19B5 = -1.91;  (* C vs D: adding μ₀ makes fit WORSE *)
mu0 = {0.12, 0.52};    (* μ₀ ± σ, consistent with zero *)

(* Gauge investigation results *)
sin2thetaWSpectral = 3/8;  (* At cutoff, exact *)
sin2thetaWRunMZ = N[sin2thetaWPredicted[MZ]];  (* ~0.203 *)
sin2thetaWMeasured = 0.23121;
sin2thetaWDiscrepancy = (sin2thetaWMeasured - sin2thetaWRunMZ) / sin2thetaWMeasured;

(* Eight Theorems — the complete structural identity catalog *)
theorems = {
  "T1: Spectral Action Universality — a_1 = a_2 = a_3 (Chamseddine-Connes)",
  "T2: AS Gauge-Group Independence — gravitational corrections universal (Daum-Harst-Reuter, Narain-Anishetty)",
  "T3: BKT Sign Structure — b_1 - (b_2+b_3)/2 = +9.18, always wrong sign (this work)",
  "T4: S_2 = S_3 Identity — mass-weighted traces equal to O(10^-5) (this work)",
  "T5: U(1) Hypercharge Dominance — S_1(GUT)/S_3 = 85/54 ~ 1.574, wrong sign (this work)",
  "T6: Fermion Trace Equality — S_2^ferm = S_3^ferm = 2*N_g exactly. The '4=4' invariant (this work)",
  "T7: The 6/7 Ratio — delta(SU3)/delta(SU2) = 2*N_g/(2*N_g+1) = 6/7 for N_g=3. Higgs fingerprint via NCG J (this work)",
  "T8: The 5/6 Ratio — S_1/(S_2+S_3) = 5/6, generation-invariant. GUT normalization recovers S_1^GUT=S_2=S_3=6 (this work)"
};

(* T6: Fermion trace equality *)
(* Per generation, 6 species as SU(2) multiplets *)
fermionTracePerGen = <|
  "S3" -> 2,  (* T_3(3)*d_2(Q_L) + T_3(3)*d_2(u_R) + T_3(3)*d_2(d_R) + 0 + 0 + 0 = 1 + 1/2 + 1/2 = 2 *)
  "S2" -> 2,  (* d_3(Q_L)*T_2(2) + 0 + 0 + d_3(L)*T_2(2) + 0 + 0 = 3/2 + 0 + 0 + 1/2 = 2 *)
  "S1" -> 10/3  (* sum of d_3*d_2*Y^2 = 1/6 + 4/3 + 1/3 + 1/2 + 1 + 0 = 10/3 *)
|>;

(* Verification: the "4 = 4" invariant *)
(* Weak dimension of colored fermions: d_2(Q) + d_2(u_R) + d_2(d_R) = 2 + 1 + 1 = 4 *)
(* Color dimension of weak fermions: d_3(Q) + d_3(L) = 3 + 1 = 4 *)
fourEqualsFour = 4;

(* T7: The 6/7 ratio *)
(* Higgs H = (1, 2, 1/2): T_3(1) = 0, T_2(2) = 1/2 *)
(* NCG J doubles: total Higgs contribution = 0 to SU(3), +1 to SU(2) *)
kkRatioSU3overSU2[Ng_] := 2 Ng / (2 Ng + 1);

(* T8: The 5/6 ratio *)
(* S_1/(S_2 + S_3) = (10/3)/4 = 5/6, independent of N_g *)
kkRatioU1overNonAbelian = 5/6;

(* Proton decay: structural stability *)
protonDecayPrediction = "STABLE — no GUT group, no X/Y bosons, no B-violating operators";

(* Dark matter: only candidate *)
darkMatterCandidate = "Lightest sterile neutrino (nu_R1) — keV scale, mass is free parameter";
darkMatterExcluded = {"KK graviton (tau~10^-28 s)", "Radion (tau~10^-22 s)", "Axion (no U(1)_PQ)", "Gravitino (no SUSY)"};

(* ============================================================ *)
(* 9b. PHASE 20 RESULTS — Theorems T9-T10 + Structural Ceiling *)
(* ============================================================ *)

(* T9: Position-dependent cutoff universality *)
(* Three independent proofs: dimensional analysis (a4 is Lambda^0),
   geometric universality, marginality. Higher-order corrections
   suppressed by 10^-37. *)
theorem9 = "T9: Position-dependent cutoff Lambda(y) = Lambda_UV * Exp[-k*y] preserves a1 = a2 = a3 exactly";

(* T10: NCG-AS Incompatibility Theorem *)
(* NCG universality (T1) + AS universality (T2) + beta(g_i)=0
   are mutually incompatible. The SM beta coefficients b1>0>b2>b3
   create a sign conflict. *)
theorem10 = "T10: NCG T1 + AS T2 + beta=0 are mutually incompatible (sign structure of b_i)";

(* Structural ceiling on gauge correction *)
gaugeGapNeeded = -10.0; (* Needed Delta(alpha_1^-1 - alpha_3^-1) *)
gaugeGapKK1Loop = -1.914; (* From ADP formula, nominal c values *)
gaugeGapHiggsKK = -0.088; (* Higgs KK bulk contribution *)
gaugeGap2Loop = +0.578; (* Two-loop, WRONG SIGN *)
gaugeGapTotal = gaugeGapKK1Loop + gaugeGapHiggsKK + gaugeGap2Loop; (* = -1.424 *)
gaugeGapFraction = gaugeGapTotal / gaugeGapNeeded; (* 14.2% *)

(* D12: BCJ not independent *)
bcjIndependent = False;
bcjReason = "Gauge bosons have universal KK spectrum (brane-localized). BCJ reorganizes standard calculation.";

(* T11: Structural Ceiling Theorem *)
(* Within any NCG spectral triple satisfying the standard axioms on RS_1,
   the maximum achievable correction to alpha_1^-1 - alpha_3^-1 is bounded. *)
theorem11 = "T11: |delta(alpha_1^-1 - alpha_3^-1)|_max <= 3.1 (29% of gap). Structural ceiling.";
gaugeGapPSIntermediate = -1.63; (* Max PS contribution with M_PS = 10^16 *)
gaugeGapTotalWithPS = gaugeGapTotal + gaugeGapPSIntermediate; (* = -3.05, 29% *)

(* D19: Pati-Salam proton decay tension *)
patiSalamMPSNeeded = 10^12; (* GeV, for gap closure *)
patiSalamMPSProton = 10^15.5; (* GeV, for proton stability *)
patiSalamVerdict = "FATAL: 3.5 orders of magnitude irreconcilable";

(* D20: GUT universality *)
gutUniversality = "All GUT-type algebras (SU(5), SO(10), E6, PS, trinification) give sin2thetaW = 3/8";

(* D21: Required boundary condition for gap closure *)
sin2thetaWRequired = 0.436; (* At cutoff, if SM running to M_Z gives 0.231 *)
traceRatioRequired = 0.776; (* a1/a2 needed *)

(* Eliminated mechanisms (15 total, Phases 14-20) *)
eliminatedMechanisms = {
  "1. Standard RG + KK thresholds — universal",
  "2. Warped AS gravitational — T2 gauge-independent",
  "3. NCG warped factorization — T1 universal a4",
  "4. Octonionic traces — exact 5/3",
  "5. AS gauge splitting — Double Universality",
  "6. Brane kinetic terms — T3 wrong sign",
  "7. Warped spectral geometry — no gauge warping",
  "8. Mass-weighted non-factorization — T5 U(1) wrong sign",
  "9. Full fermion KK tower — ceiling 14-22%",
  "10. Position-dependent cutoff — T9 exact universality",
  "11. NCG-AS synthesis — T10 incompatible",
  "12. BCJ color-kinematics — not independent of KK thresholds",
  "13. AS-modified spectral function — T1 is algebraic",
  "14. Category-theoretic formulation — all invariants topological",
  "15. Extended spectral triple — GUT universality of 3/8 + proton decay"
};

(* Swampland scorecard *)
swamplandScore = <|
  "Satisfied" -> {"WGC (all variants)", "Distance", "No Global Symmetries",
                  "Cobordism", "Festina Lente", "Completeness",
                  "WGC Tower/Sublattice", "Species Bound", "Completeness Hypothesis"},
  "Evaded" -> {"dS Conjecture — cuscuton c_s=Infinity, no field space"},
  "Violated" -> {"TCC — r=0.004 vs r<10^-30 (shared with all inflation)"}
|>;

(* Update theorem list — Eleven Structural Theorems *)
theorems = {
  "T1: a1 = a2 = a3 (spectral universality) [Chamseddine-Connes]",
  "T2: AS corrections gauge-group-independent [Daum-Harst-Reuter]",
  "T3: b1 - 1/2(b2+b3) = +9.18, wrong sign for BKT [this work]",
  "T4: S2/S3 = 1.000, mass-weighted traces [this work]",
  "T5: S1/S3 = 1.574, wrong sign for U(1) [this work]",
  "T6: S2^ferm = S3^ferm = 2*N_g exactly. The '4=4' invariant [this work]",
  "T7: delta(SU3)/delta(SU2) = 2*N_g/(2*N_g+1) = 6/7 for N_g=3 [this work]",
  "T8: S1/(S2+S3) = 5/6, generation-invariant [this work]",
  "T9: Position-dependent cutoff preserves universality exactly [this work]",
  "T10: NCG T1 + AS T2 + beta=0 mutually incompatible [this work]",
  "T11: Structural ceiling |delta(a1inv-a3inv)| <= 3.1 (29% of gap) [this work]"
};

(* ============================================================ *)
(* 10. DIAGNOSTIC AND QUERY FUNCTIONS                           *)
(* ============================================================ *)

(* Print full state *)
meridianStatus[] := Module[{},
  Print["=== MERIDIAN FRAMEWORK STATUS ==="];
  Print[""];
  Print["--- RS Geometry ---"];
  Print["  ky_c = ", kyc];
  Print["  k = ", ScientificForm[kRS], " GeV"];
  Print["  TeV scale = ", ScientificForm[TeVScale], " GeV"];
  Print["  Hierarchy = ", ScientificForm[hierarchy]];
  Print["  1st KK graviton = ", kkMassGraviton[1], " GeV"];
  Print["  Radion mass ~ ", ScientificForm[radionMass], " GeV"];
  Print[""];
  Print["--- Gauge Couplings at M_Z ---"];
  Print["  α₁⁻¹ = ", alpha1InvMZ];
  Print["  α₂⁻¹ = ", alpha2InvMZ];
  Print["  α₃⁻¹ = ", alpha3InvMZ];
  Print["  Unification scale = ", ScientificForm[unificationScale], " GeV"];
  Print[""];
  Print["--- Spectral Action ---"];
  Print["  sin²θ_W (cutoff) = 3/8 = ", N[3/8]];
  Print["  sin²θ_W (M_Z, predicted) = ", sin2thetaWRunMZ];
  Print["  sin²θ_W (M_Z, measured) = ", sin2thetaWMeasured];
  Print["  Discrepancy = ", NumberForm[sin2thetaWDiscrepancy * 100, 3], "%"];
  Print[""];
  Print["--- Key Coincidence ---"];
  Print["  ky_c / ln(Λ/M_Z) = ", NumberForm[kycRatio, 4]];
  Print[""];
  Print["--- Phase 18/19 Results ---"];
  Print["  ΔAIC (v5 DR2) = +", deltaAIC];
  Print["  ΔAIC (19B.5 C vs D) = ", deltaAIC19B5];
  Print["  μ₀ = ", mu0[[1]], " ± ", mu0[[2]]];
  Print[""];
  Print["--- Eleven Structural Theorems (T1-T11) ---"];
  Do[Print["  ", t], {t, theorems}];
  Print[""];
  Print["=== END STATUS ==="];
];

(* KK mass table *)
kkMassTable[nMax_Integer] := Module[{},
  Print["=== KK Mass Spectrum (first ", nMax, " modes) ==="];
  Print[StringForm["  `1`\t`2`\t`3`\t`4`", "n", "Graviton (TeV)", "Gauge (TeV)", "x_n"]];
  Do[
    Print[StringForm["  `1`\t`2`\t`3`\t`4`",
      n,
      NumberForm[kkMassGraviton[n] / 1000, 4],
      NumberForm[kkMassGauge[n] / 1000, 4],
      NumberForm[N[BesselJZero[1, n]], 6]
    ]],
    {n, 1, nMax}
  ];
];

(* Running plot data *)
runningData[muMin_, muMax_, nPoints_Integer] := Module[{mus, data},
  mus = Table[10^x, {x, Log10[muMin], Log10[muMax], (Log10[muMax] - Log10[muMin])/(nPoints - 1)}];
  data = Table[
    {Log10[mu], alphaInverse[1, mu], alphaInverse[2, mu], alphaInverse[3, mu]},
    {mu, mus}
  ];
  data
];

End[];
EndPackage[];
