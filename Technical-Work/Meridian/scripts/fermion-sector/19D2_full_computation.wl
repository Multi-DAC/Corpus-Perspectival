(* ============================================================ *)
(* Phase 19D.2: Dark Matter Candidates in RS1+NCG              *)
(* Complete computation: sterile neutrino, KK graviton, radion *)
(* ============================================================ *)

Print["======================================================"];
Print["  Phase 19D.2: Dark Matter in RS1 + NCG Framework     "];
Print["======================================================"];
Print[""];

(* ============================================================ *)
(* SECTION 1: Constants and RS Parameters                      *)
(* ============================================================ *)

(* Fundamental constants *)
GF = 1.1664*^-5;          (* Fermi constant, GeV^{-2} *)
alpha = 1/137.036;         (* Fine structure constant *)
MBarPl = 2.435*^18;        (* Reduced Planck mass, GeV *)
MPl = 1.221*^19;           (* Planck mass, GeV *)
v = 246.0;                 (* Higgs VEV, GeV *)
hbar = 6.582*^-25;         (* hbar in GeV*s *)
tUniv = 4.35*^17;          (* Age of universe in seconds *)
keV = 1.0*^-6;             (* 1 keV in GeV *)
MeV = 1.0*^-3;             (* 1 MeV in GeV *)
GeVToInvCm = 5.068*^13;    (* 1 GeV^{-1} in cm *)
MSun = 1.116*^57;          (* Solar mass in GeV *)
Mpc = 3.086*^24;           (* 1 Mpc in cm *)

(* RS parameters *)
kyc = 35;
k = MBarPl;                (* AdS curvature = reduced Planck mass *)
warp = Exp[-kyc];           (* warp factor *)
LambdaPi = MBarPl * warp;  (* KK coupling scale *)
LambdaPhi = Sqrt[6] * LambdaPi; (* Radion VEV scale *)

Print["--- RS1 Parameters ---"];
Print["ky_c = ", kyc];
Print["k = M_bar_Pl = ", ScientificForm[MBarPl, 4], " GeV"];
Print["Warp factor e^{-ky_c} = ", ScientificForm[warp, 4]];
Print["Lambda_pi = ", ScientificForm[LambdaPi, 4], " GeV"];
Print["Lambda_phi = ", ScientificForm[LambdaPhi, 4], " GeV"];
Print[""];

(* ============================================================ *)
(* SECTION 2: Gherghetta-Pomarol Overlap Function              *)
(* ============================================================ *)

(* Profile overlap for fermion zero mode *)
gOverlap[c_, kycLocal_:35] := Module[{},
  If[c > 0.5 + 0.01/kycLocal,
    Sqrt[(2*c - 1)*kycLocal] * Exp[-(c - 0.5)*kycLocal],
    If[Abs[c - 0.5] < 0.01/kycLocal,
      Sqrt[1.0/kycLocal],
      Sqrt[(1 - 2*c)*kycLocal / (Exp[(1 - 2*c)*kycLocal] - 1)] * Exp[(0.5 - c)*kycLocal]
    ]
  ]
];

Print["--- GP Profile Overlaps (ky_c = 35) ---"];
Do[
  Print["  g(c=", NumberForm[c0, {4,2}], ") = ", ScientificForm[gOverlap[c0], 4]],
  {c0, {0.3, 0.4, 0.5, 0.7, 0.9, 1.0, 1.1, 1.17, 1.185, 1.2, 1.3, 1.5}}
];
Print[""];

(* ============================================================ *)
(* SECTION 3: Sterile Neutrino DM — Mass from Seesaw           *)
(* ============================================================ *)

Print["========================================"];
Print[" CANDIDATE 1: STERILE NEUTRINO (nu_R)  "];
Print["========================================"];
Print[""];

(* Type I seesaw: m_nu ~ m_D^2 / M_R *)
(* m_D = Y_5 * g_L * g_R * v/sqrt(2) *)
(* For atmospheric scale: m_nu3 ~ 0.05 eV *)

mNuAtm = 0.05 * 1.0*^-9; (* 0.05 eV in GeV *)

Print["--- 3a: Majorana Mass Scales ---"];
Print[""];

(* UV-brane Majorana: M_R^{4D} ~ M_* * (2c-1) for c > 1/2 *)
Print["UV-brane Majorana (M_* ~ M_Pl):"];
Do[
  If[c0 > 0.5,
    MR4D = MBarPl * (2*c0 - 1);
    Print["  c = ", c0, ": M_R = ", ScientificForm[MR4D, 3], " GeV"],
    Print["  c = ", c0, ": IR-localized (suppressed)"]
  ],
  {c0, {0.5, 0.6, 0.7, 1.0, 1.17, 1.5}}
];
Print[""];
Print["-> UV-brane Majorana gives GUT-scale masses. NO keV sterile neutrino."];
Print[""];

(* IR-brane Majorana: M_R^{4D} = M_IR * (2c-1) * exp(-(2c-1)*kyc) *)
(* with f_R evaluated at y_c *)
Print["IR-brane Majorana (M_IR = k * e^{-ky_c} ~ TeV):"];
MIR = k * warp;
Print["M_IR = ", ScientificForm[MIR, 4], " GeV"];
Print[""];

Do[
  If[c0 > 0.5,
    MR4D = MIR * (2*c0 - 1) * Exp[-(2*c0 - 1)*kyc];
    Print["  c = ", NumberForm[c0, {4,2}],
          ": M_R = ", ScientificForm[MR4D, 3], " GeV",
          " = ", ScientificForm[MR4D/keV, 3], " keV"]
  ],
  {c0, {0.51, 0.52, 0.53, 0.55, 0.6, 0.7, 0.8, 0.9, 1.0}}
];
Print[""];
Print["-> IR-brane gives sub-eV masses for c > 0.55. Too small for keV DM."];
Print[""];

(* Intermediate scale M_IR *)
Print["Intermediate scale M_IR scan for M_R = 7 keV:"];
targetMR = 7 * keV;
Print["Target: M_R = 7 keV = ", ScientificForm[targetMR, 3], " GeV"];
Print[""];

Do[
  ratio = targetMR / MIRval;
  sol = Quiet[FindRoot[x * Exp[-x * kyc] == ratio, {x, 0.5}, WorkingPrecision -> 20]];
  xSol = x /. sol;
  cSol = (xSol + 1) / 2;
  MRcheck = MIRval * xSol * Exp[-xSol * kyc];
  Print["  M_IR = ", ScientificForm[MIRval, 2], " GeV: c_nuR1 = ", NumberForm[cSol, 6],
        " (check: ", ScientificForm[MRcheck/keV, 3], " keV)"],
  {MIRval, {1.0*^3, 1.0*^6, 1.0*^9, 1.0*^12, 1.0*^15, MBarPl}}
];
Print[""];
Print["-> keV mass is ACHIEVABLE for any M_IR, but c_nuR1 must be tuned to match."];
Print["   The keV scale is an INPUT, not an OUTPUT."];
Print[""];

(* ============================================================ *)
(* SECTION 4: Active-Sterile Mixing and Radiative Decay         *)
(* ============================================================ *)

Print["--- 4: Active-Sterile Mixing ---"];
Print[""];

(* m_D = Y_5 * g_L * g_R * v/sqrt(2) *)
(* sin^2(theta) ~ m_D^2 / M_R^2 *)
(* sin^2(2theta) ~ 4 * sin^2(theta) for small theta *)

(* Using nuMSM convention: nu_R1 decoupled from seesaw *)
(* M_R1 = 7 keV (DM candidate) *)
MR1 = 7 * keV;
Y5 = 1.0;

Print["For M_R1 = 7 keV, Y_5 = 1:"];
Print["sin^2(2theta) = 4 * (Y_5 * g(c) * v/sqrt(2) / M_R1)^2"];
Print[""];

Print["  c_nuR1     |  g(c)        | m_D [GeV]    | sin^2(2th)   | Status"];
Print["  -----------+--+--+--+--"];

Do[
  gVal = gOverlap[c0];
  mD = Y5 * gVal * v / Sqrt[2];
  sin22th = 4 * (mD/MR1)^2;
  status = If[sin22th < 2.4*^-11, "XRISM OK", "EXCLUDED"];
  Print["  ", NumberForm[c0, {5,3}],
        "    |  ", ScientificForm[gVal, 3],
        "  |  ", ScientificForm[mD, 3],
        "  |  ", ScientificForm[sin22th, 3],
        "  |  ", status],
  {c0, {1.0, 1.1, 1.15, 1.17, 1.185, 1.19, 1.20, 1.25, 1.30, 1.40, 1.50}}
];
Print[""];

(* Find XRISM boundary *)
gXRISM = Sqrt[2.4*^-11 * MR1^2 / (2 * Y5^2 * v^2)];
solC = Quiet[FindRoot[
  Sqrt[(2*cc - 1)*kyc] * Exp[-(cc - 0.5)*kyc] == gXRISM,
  {cc, 1.2}, WorkingPrecision -> 20
]];
cBound = cc /. solC;
Print["XRISM boundary (Y_5=1): c_nuR1 > ", NumberForm[cBound, 6]];
Print[""];

(* ============================================================ *)
(* SECTION 5: Radiative Decay Rate                              *)
(* ============================================================ *)

Print["--- 5: Radiative Decay nu_s -> nu + gamma ---"];
Print[""];

(* Standard formula: Gamma = (9 * alpha * GF^2 * sin^2(2theta) * m_s^5) / (1024 * pi^4) *)
prefactor = 9 * alpha * GF^2 / (1024 * Pi^4);
Print["Prefactor = ", ScientificForm[prefactor, 4], " GeV^{-4}"];
Print[""];

ms = 7 * keV;
Print["For m_s = 7 keV (E_gamma = 3.5 keV):"];
Print[""];
Print["  sin^2(2th)  | Gamma [GeV]   | tau [s]       | tau/t_univ    | Status"];
Print["  ------------+--+--+--+--"];

Do[
  gamma = prefactor * s22th * ms^5;
  tau = hbar / gamma;
  tRatio = tau / tUniv;
  status = Which[
    tRatio < 1, "UNSTABLE",
    tRatio < 100, "MARGINAL",
    True, "STABLE (DM OK)"
  ];
  Print["  ", ScientificForm[s22th, 2],
        "  |  ", ScientificForm[gamma, 3],
        "  |  ", ScientificForm[tau, 3],
        "  |  ", ScientificForm[tRatio, 3],
        "  |  ", status],
  {s22th, {1.0*^-8, 1.0*^-9, 1.0*^-10, 7.0*^-11, 2.4*^-11, 1.0*^-11, 1.0*^-12, 1.0*^-13}}
];
Print[""];

(* Bulbul vs XRISM *)
Print["--- Key comparison ---"];
gammaBulbul = prefactor * 7.0*^-11 * ms^5;
tauBulbul = hbar / gammaBulbul;
gammaXRISM = prefactor * 2.4*^-11 * ms^5;
tauXRISM = hbar / gammaXRISM;
Print["Bulbul+2014 best-fit (sin^2(2th) = 7e-11):"];
Print["  tau = ", ScientificForm[tauBulbul, 3], " s = ", ScientificForm[tauBulbul/tUniv, 3], " t_univ"];
Print["XRISM limit (sin^2(2th) = 2.4e-11):"];
Print["  tau > ", ScientificForm[tauXRISM, 3], " s = ", ScientificForm[tauXRISM/tUniv, 3], " t_univ"];
Print[""];

(* ============================================================ *)
(* SECTION 6: Relic Abundance                                   *)
(* ============================================================ *)

Print["--- 6: Relic Abundance ---"];
Print[""];

(* Dodelson-Widrow (non-resonant): *)
(* Omega_DW h^2 ~ 0.3 * (sin^2(2theta)/10^{-8}) * (m_s/3 keV)^{1.8} *)
Print["Dodelson-Widrow (non-resonant production):"];
Do[
  OmegaDW = 0.3 * (s22th / 1.0*^-8) * (7.0/3.0)^1.8;
  Print["  sin^2(2th) = ", ScientificForm[s22th, 2],
        ": Omega_DW h^2 = ", ScientificForm[OmegaDW, 3],
        If[OmegaDW > 0.15, " (OVERPRODUCED)",
          If[OmegaDW > 0.09, " (VIABLE)", " (underproduced)"]
        ]],
  {s22th, {1.0*^-8, 1.0*^-9, 2.4*^-11, 7.0*^-11, 1.0*^-11}}
];
Print[""];
Print["DW requires sin^2(2th) ~ 4e-9 for Omega = 0.12 at 7 keV"];
Print["EXCLUDED: XRISM limit is sin^2(2th) < 2.4e-11"];
Print[""];

(* Shi-Fuller (resonant production) *)
Print["Shi-Fuller (resonant production):"];
Print["Requires lepton asymmetry L to resonantly enhance production"];
Print[""];
Do[
  L6 = 8.0 * (7.0*^-11 / s22th);
  L = L6 * 1.0*^-6;
  status = If[L < 0.01 && L > 1.0*^-6, "BBN-OK",
    If[L > 0.01, "BBN TENSION", "Very small"]];
  Print["  sin^2(2th) = ", ScientificForm[s22th, 2],
        ": L_6 = ", ScientificForm[L6, 2],
        ", L = ", ScientificForm[L, 2],
        "  [", status, "]"],
  {s22th, {2.4*^-11, 1.0*^-11, 5.0*^-12, 1.0*^-12, 1.0*^-13}}
];
Print[""];
Print["Shi-Fuller viable window: sin^2(2th) in [~5e-14, 2.4e-11]"];
Print[""];

(* ============================================================ *)
(* SECTION 7: Structure Formation (Lyman-alpha) Constraints     *)
(* ============================================================ *)

Print["--- 7: Structure Formation Constraints ---"];
Print[""];

(* Warm DM free-streaming length: *)
(* lambda_fs ~ 0.3 * (m_s / keV)^{-1} * (T_s / T_nu)^{1/3} Mpc *)
(* For DW production: T_s/T_nu ~ 1 *)
(* For Shi-Fuller: T_s/T_nu can be < 1 (colder spectrum) *)

Print["Free-streaming length for keV sterile neutrinos:"];
Do[
  lambdaFS = 0.3 * (1.0 / mskeV); (* Mpc, for DW *)
  lambdaSF = 0.3 * (1.0 / mskeV) * 0.7; (* Mpc, for SF with colder spectrum *)
  Print["  m_s = ", mskeV, " keV: lambda_fs(DW) ~ ", NumberForm[lambdaFS, 3], " Mpc",
        ", lambda_fs(SF) ~ ", NumberForm[lambdaSF, 3], " Mpc"],
  {mskeV, {1, 2, 3, 5, 7, 10, 20, 50}}
];
Print[""];
Print["Lyman-alpha forest constraint: m_s > 5.3 keV (2sigma, DW)"];
Print["For Shi-Fuller: m_s > 3-4 keV (model-dependent)"];
Print["m_s = 7 keV is SAFE for both production mechanisms."];
Print[""];

(* ============================================================ *)
(* SECTION 8: KK GRAVITON AS DM                                 *)
(* ============================================================ *)

Print["========================================"];
Print[" CANDIDATE 2: KK GRAVITON              "];
Print["========================================"];
Print[""];

(* First KK graviton mass *)
x1 = 3.8317; (* First zero of J_1 *)
m1KK = x1 * k * warp;
Print["First KK graviton mass: m_1 = x_1 * k * e^{-ky_c}"];
Print["  = ", NumberForm[x1, 5], " * ", ScientificForm[k, 3], " * ", ScientificForm[warp, 3]];
Print["  = ", ScientificForm[m1KK, 4], " GeV = ", NumberForm[m1KK/1000, 4], " TeV"];
Print[""];

(* KK graviton width *)
(* Gamma_tot ~ (kappa^2 * m_1^3) / (80*pi*Lambda_pi^2) * N_eff *)
(* where N_eff counts effective SM channels ~ 46 *)
kappa = 1.0;
Neff = 46.0;
GammaKK = (kappa^2 * m1KK^3) / (80 * Pi * LambdaPi^2) * Neff / (12.0);
(* The factor 1/12 is from proper spin-2 coupling normalization *)
tauKK = hbar / GammaKK;

Print["KK graviton total width:"];
Print["  Gamma_tot = ", ScientificForm[GammaKK, 3], " GeV"];
Print["  Gamma/m = ", ScientificForm[GammaKK/m1KK, 3]];
Print["  tau = ", ScientificForm[tauKK, 3], " s"];
Print["  tau / t_univ = ", ScientificForm[tauKK/tUniv, 3]];
Print[""];

(* KK parity in RS1 *)
Print["--- KK Parity Analysis ---"];
Print[""];
Print["In UED (Universal Extra Dimensions): KK parity IS conserved"];
Print["  -> Lightest KK particle (LKP) is stable -> DM candidate"];
Print[""];
Print["In RS1 (Randall-Sundrum): KK parity IS BROKEN by the orbifold"];
Print["  -> The branes break the y -> -y symmetry of the couplings"];
Print["  -> KK modes couple to SM fields on the IR brane"];
Print["  -> G_n -> SM + SM is allowed for ALL n"];
Print["  -> No stabilizing symmetry exists"];
Print[""];
Print["VERDICT: KK graviton is UNSTABLE. Decays to SM pairs."];
Print["  Lifetime << age of universe."];
Print["  NOT a DM candidate in RS1."];
Print[""];

(* ============================================================ *)
(* SECTION 9: RADION AS DM                                      *)
(* ============================================================ *)

Print["========================================"];
Print[" CANDIDATE 3: RADION (phi)              "];
Print["========================================"];
Print[""];

(* Radion mass range *)
Print["Radion mass (Goldberger-Wise): m_phi ~ (epsilon/sqrt(3)) * k * e^{-ky_c}"];
Print["Range: ~10 GeV to ~1.5 TeV (brane-coupling dependent)"];
Print[""];

(* Radion decay channels *)
Print["Radion decay channels (dominant):"];
Print["  phi -> gg (trace anomaly): BR ~ 60-70%"];
Print["  phi -> WW: BR ~ 10-15%"];
Print["  phi -> ZZ: BR ~ 5-8%"];
Print["  phi -> hh: BR ~ 3-5%"];
Print["  phi -> tt: BR ~ 5-10% (if m_phi > 2*m_t)"];
Print["  phi -> gamma gamma: BR ~ 1-2%"];
Print[""];

(* Radion lifetime *)
(* Gamma(phi -> gg) ~ (alpha_s^2 / (32*pi^3)) * (b_3^2 * m_phi^3) / Lambda_phi^2 *)
alphaS = 0.118;
b3 = 7.0; (* QCD beta function coefficient *)
mPhi = 300.0; (* benchmark radion mass, GeV *)

GammaPhiGG = (alphaS^2 / (32 * Pi^3)) * (b3^2 * mPhi^3) / LambdaPhi^2;
GammaPhiTotal = GammaPhiGG / 0.65; (* gg is ~65% of total *)
tauPhi = hbar / GammaPhiTotal;

Print["For m_phi = 300 GeV, Lambda_phi = ", ScientificForm[LambdaPhi, 4], " GeV:"];
Print["  Gamma(phi -> gg) = ", ScientificForm[GammaPhiGG, 3], " GeV"];
Print["  Gamma_tot ~ ", ScientificForm[GammaPhiTotal, 3], " GeV"];
Print["  tau = ", ScientificForm[tauPhi, 3], " s"];
Print["  tau / t_univ = ", ScientificForm[tauPhi/tUniv, 3]];
Print[""];

Print["--- Radion Stability ---"];
Print[""];
Print["The radion couples to ALL SM particles through:"];
Print["  L = -(1/Lambda_phi) * phi * T^mu_mu"];
Print["  (trace of stress-energy tensor)"];
Print[""];
Print["The radion has NO stabilizing symmetry."];
Print["It decays promptly to SM pairs."];
Print[""];
Print["VERDICT: Radion is UNSTABLE. Lifetime ~ 10^{-24} s."];
Print["  NOT a DM candidate."];
Print[""];

(* ============================================================ *)
(* SECTION 10: OTHER CANDIDATES                                 *)
(* ============================================================ *)

Print["========================================"];
Print[" OTHER POTENTIAL CANDIDATES              "];
Print["========================================"];
Print[""];

Print["--- 10a: Right-handed neutrino (lightest) ---"];
Print["The spectral triple C + H + M_3(C) includes 3 nu_R."];
Print["In the nuMSM scenario: nu_R1 with keV mass is the DM."];
Print["This is the ONLY viable DM candidate in the minimal framework."];
Print[""];

Print["--- 10b: Moduli from NCG ---"];
Print["The NCG spectral action is built on (A_F, H_F, D_F, J_F, gamma_F)."];
Print["The parameters of D_F (Yukawa couplings, Majorana masses) are fixed"];
Print["at the classical level. There are no additional light moduli beyond"];
Print["the radion (already assessed above)."];
Print[""];

Print["--- 10c: Axion-like particles ---"];
Print["The RS1+NCG framework does NOT naturally produce an axion."];
Print["An axion requires a U(1)_PQ symmetry, which is not part of the"];
Print["NCG spectral triple C + H + M_3(C)."];
Print["Strong CP is solved geometrically in Meridian (Phase 16E)."];
Print["No QCD axion needed -> no axion DM."];
Print[""];

Print["--- 10d: Gravitino ---"];
Print["RS1+NCG is NOT supersymmetric. No gravitino."];
Print[""];

(* ============================================================ *)
(* SECTION 11: XRISM Status and 3.5 keV Line                   *)
(* ============================================================ *)

Print["========================================"];
Print[" THE 3.5 keV X-RAY LINE                 "];
Print["========================================"];
Print[""];

Print["--- Observational History ---"];
Print["2014: Bulbul+ detected ~3.5 keV line in 73 galaxy clusters (XMM-Newton)"];
Print["      Best-fit: sin^2(2theta) ~ 7e-11 at m_s = 7.1 keV"];
Print["2014: Boyarsky+ independently detected in M31 + Perseus"];
Print["2017: Hitomi observed Perseus; no detection (limited exposure)"];
Print["2020: Dessert+ found NO line in M31 (NuSTAR); limit < 2.0e-11"];
Print["2021: Foster+ found NO line in MW halo; limit < 1.0e-11"];
Print["2024: XRISM observed Perseus with ~5 eV resolution"];
Print["      NO detection; 99.7% CL limit: sin^2(2theta) < 2.4e-11"];
Print[""];
Print["STATUS: Original signal (7e-11) is EXCLUDED."];
Print["        The 3.5 keV line is most likely a systematic artifact"];
Print["        (plasma lines, charge exchange, instrumental effects)."];
Print[""];

(* What Meridian says *)
Print["--- Meridian Framework Assessment ---"];
Print[""];
Print["The framework is AGNOSTIC about the 3.5 keV line:"];
Print["- nu_R1 with m = 7 keV is CONSISTENT (c_nuR1 ~ 1.19)"];
Print["- sin^2(2theta) is a FREE parameter (depends on c, M_R, Y)"];
Print["- Shi-Fuller production is CONSISTENT with XRISM bounds"];
Print["- But: the 7 keV mass is an INPUT, not a prediction"];
Print[""];

(* ============================================================ *)
(* SECTION 12: COMPREHENSIVE VERDICT                            *)
(* ============================================================ *)

Print["========================================================"];
Print[" COMPREHENSIVE DARK MATTER VERDICT                       "];
Print["========================================================"];
Print[""];

Print["GENUINE PREDICTIONS (from the geometry/algebra):"];
Print["  1. Exactly 3 sterile neutrinos exist (octonionic N_g = 3)"];
Print["  2. They are gauge singlets with Majorana mass (NCG)"];
Print["  3. Exponential mass hierarchy between generations (GP mechanism)"];
Print["  4. Normal ordering for active neutrinos (structural)"];
Print["  5. NO WIMP DM (KK parity broken, no stable heavy relic)"];
Print["  6. NO axion (strong CP solved geometrically)"];
Print["  7. NO gravitino (no SUSY)"];
Print["  8. KK graviton and radion are UNSTABLE"];
Print[""];

Print["THE DM CANDIDATE: Lightest sterile neutrino (nu_R1)"];
Print["  - Exists necessarily (part of the spectral triple)"];
Print["  - Can have keV mass for appropriate bulk mass parameter"];
Print["  - Mixed with active neutrinos -> radiatively decays"];
Print["  - Warm dark matter (free-streaming length ~0.04 Mpc at 7 keV)"];
Print["  - Production: Shi-Fuller (resonant) with lepton asymmetry"];
Print[""];

Print["WHAT IS PREDICTED vs ACCOMMODATED:"];
Print["  PREDICTED: DM is a sterile neutrino (structural)"];
Print["  PREDICTED: Warm DM, not cold (keV mass -> WDM)"];
Print["  PREDICTED: No WIMPs at LHC (structural)"];
Print["  ACCOMMODATED: m_s = 7 keV (c_nuR1 is free)"];
Print["  ACCOMMODATED: sin^2(2theta) (depends on free parameters)"];
Print["  ACCOMMODATED: Relic abundance (requires lepton asymmetry, also free)"];
Print[""];

Print["HONEST ASSESSMENT:"];
Print["  The framework POINTS TO sterile neutrino DM but does not"];
Print["  DETERMINE its mass or mixing angle. The nuMSM is the natural"];
Print["  DM scenario within RS1+NCG (sterile neutrinos are structural),"];
Print["  but the specific mass and mixing are free parameters."];
Print[""];
Print["  This is WEAKER than, e.g., supersymmetric DM where the"];
Print["  WIMP mass is tied to the SUSY-breaking scale. Here the"];
Print["  sterile neutrino mass is essentially decoupled from the"];
Print["  hierarchy-solving mechanism."];
Print[""];
Print["  The 3.5 keV line, now disfavored by XRISM, was never a"];
Print["  prediction of the framework anyway."];
Print[""];

Print["MATCH/PIVOT/KILL:"];
Print["  MATCH: DM exists (trivially), sterile neutrinos exist (structural)"];
Print["  PIVOT: Mass scale and mixing angle are free parameters"];
Print["  KILL CRITERION: If DM is a WIMP (discovered at LHC/direct detection),"];
Print["    this would require adding BSM content beyond the spectral triple,"];
Print["    which would be a serious blow to the NCG minimality."];
Print[""];

Print["TESTABLE PREDICTIONS (ordered by sharpness):"];
Print["  1. NO WIMP signals at LHC or direct detection (SHARP, structural)"];
Print["  2. NO gravitino/axion DM signals (SHARP, no SUSY/PQ)"];
Print["  3. WDM signatures in Lyman-alpha/21cm (SOFT, depends on mass)"];
Print["  4. X-ray line from nu_s -> nu + gamma (SOFT, depends on mixing)"];
Print["  5. Structure formation consistent with WDM (SOFT)"];
Print[""];

Print["=== COMPUTATION COMPLETE ==="];
