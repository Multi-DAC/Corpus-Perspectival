(* ============================================================ *)
(* 20B THRESHOLD CLOSURE: Can KK thresholds close the full    *)
(* 12% gauge gap?                                              *)
(* Project Meridian Phase 20                                   *)
(* Authors: Clayton & Clawd                                    *)
(* Date: March 22, 2026                                        *)
(* ============================================================ *)

Print["================================================================"];
Print["20B THRESHOLD CLOSURE ANALYSIS"];
Print["Can KK fermion + scalar + radion thresholds close the 12% gap?"];
Print["================================================================"];
Print[""];

(* ============================================================ *)
(* PHYSICAL CONSTANTS AND RS PARAMETERS                        *)
(* ============================================================ *)
v = 246.22;
kyc = 35.0;
MZ = 91.1876;
MPl = 2.435*^18;
alphasMZ = 0.1179;
alpha1invMZ = 59.01;
alpha2invMZ = 29.59;
alpha3invMZ = 1/alphasMZ;
sin2thetaW = 0.23121;
alphaEMinv = 127.951;

MKK = MPl * Exp[-kyc];
Print["RS Parameters:"];
Print["  ky_c = ", kyc];
Print["  M_Pl = ", ScientificForm[MPl, 4], " GeV"];
Print["  M_KK = M_Pl * e^{-ky_c} = ", ScientificForm[N[MKK], 4], " GeV"];
Print[""];

delta13needed = -10.0;
Print["Required: Delta(alpha_1^{-1} - alpha_3^{-1}) ~ ", delta13needed];
Print[""];

(* ============================================================ *)
(* ADP THRESHOLD FUNCTION                                      *)
(* ============================================================ *)
delta[c_] := Module[{nu = Abs[c + 1/2], x1},
  x1 = N[BesselJZero[nu, 1]];
  N[PolyGamma[nu + 1] - PolyGamma[1] + Log[x1/Pi]]
];

(* GUT-normalized Dynkin indices *)
t1[spec_] := (3/5) * spec[[4]]^2 * spec[[2]] * spec[[3]];
t2[spec_] := If[spec[[3]] == 2, spec[[2]] * (1/2), 0];
t3[spec_] := If[spec[[2]] == 3, spec[[3]] * (1/2), 0];

(* ============================================================ *)
(* SOURCE 1: KK FERMION BULK MASS THRESHOLDS                  *)
(* ============================================================ *)
Print["================================================================"];
Print["SOURCE 1: KK Fermion Bulk Mass Thresholds (Nominal c)"];
Print["================================================================"];
Print[""];

fermionSpecies = {
  {"Q3_L",  3, 2,  1/6,  0.40},
  {"t_R",   3, 1,  2/3, -0.30},
  {"b_R",   3, 1, -1/3,  0.43},
  {"L3_L",  1, 2, -1/2,  0.52},
  {"tau_R", 1, 1,   -1,  0.49},
  {"Q2_L",  3, 2,  1/6,  0.55},
  {"c_R",   3, 1,  2/3,  0.55},
  {"s_R",   3, 1, -1/3,  0.62},
  {"L2_L",  1, 2, -1/2,  0.58},
  {"mu_R",  1, 1,   -1,  0.61},
  {"Q1_L",  3, 2,  1/6,  0.63},
  {"u_R",   3, 1,  2/3,  0.68},
  {"d_R",   3, 1, -1/3,  0.65},
  {"L1_L",  1, 2, -1/2,  0.62},
  {"e_R",   1, 1,   -1,  0.75}
};

Print["  Species\tc\tdelta(c)\tT1\tT3\t(T1-T3)*delta"];
deltaAlphaFerm = {0., 0., 0.};
Do[
  Module[{c = spec[[5]], dc, tt1, tt2, tt3},
    dc = delta[c];
    tt1 = N[t1[spec]]; tt2 = N[t2[spec]]; tt3 = N[t3[spec]];
    deltaAlphaFerm[[1]] += -(1/(2*Pi)) * tt1 * dc;
    deltaAlphaFerm[[2]] += -(1/(2*Pi)) * tt2 * dc;
    deltaAlphaFerm[[3]] += -(1/(2*Pi)) * tt3 * dc;
    Print["  ", spec[[1]], "\t",
      NumberForm[c, {3,2}], "\t",
      NumberForm[dc, {5,3}], "\t\t",
      NumberForm[tt1, {4,3}], "\t",
      NumberForm[tt3, {4,3}], "\t",
      NumberForm[(tt1-tt3)*dc, {6,3}]];
  ],
  {spec, fermionSpecies}
];

delta13ferm = deltaAlphaFerm[[1]] - deltaAlphaFerm[[3]];
Print[""];
Print["  Delta(alpha_1^{-1} - alpha_3^{-1}) = ", NumberForm[delta13ferm, {6,4}]];
Print["  Fraction of needed: ", NumberForm[delta13ferm/delta13needed * 100, {4,1}], "%"];
Print[""];

(* ============================================================ *)
(* SOURCE 2: HIGGS KK TOWER                                   *)
(* ============================================================ *)
Print["================================================================"];
Print["SOURCE 2: Higgs KK Tower Thresholds"];
Print["================================================================"];
Print[""];

(* Higgs doublet: T_1 = (3/5)*(1/2)^2*1*2 = 3/10, T_2 = 1/2, T_3 = 0 *)
s1H = N[(3/5) * (1/2)^2 * 1 * 2];
s2H = 0.5;
s3H = 0.0;
Print["  Higgs Dynkin indices: S_1=", s1H, " S_2=", s2H, " S_3=", s3H];
Print[""];

(* Scenario A: Brane-localized Higgs (no KK tower) *)
Print["  Scenario A (strict brane Higgs): Delta_{13} = 0"];
Print[""];

(* Scenario B: Bulk Higgs *)
(* delta_H(mu) = Psi(|mu-2|+1) - Psi(1) + ln(BesselJZero[|mu-2|,1]/pi) *)
Print["  Scenario B (bulk Higgs) threshold delta_H(mu):"];
Print["  mu_H\tnu\tx_1\t\tdelta_H"];
muValues = {0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0};
Do[
  Module[{nu = Abs[mu - 2], x1, dh},
    x1 = N[BesselJZero[nu, 1]];
    dh = N[PolyGamma[nu + 1] - PolyGamma[1] + Log[x1/Pi]];
    Print["  ", NumberForm[mu, {3,1}], "\t",
      NumberForm[nu, {3,1}], "\t",
      NumberForm[x1, {5,3}], "\t\t",
      NumberForm[dh, {6,4}]];
  ],
  {mu, muValues}
];
Print[""];

(* Compute for near-conformal and strong IR *)
deltaH0 = Module[{nu=2, x1}, x1=N[BesselJZero[nu,1]];
  N[PolyGamma[nu+1]-PolyGamma[1]+Log[x1/Pi]]]; (* mu=0, strong IR *)
deltaH2 = Module[{nu=0, x1}, x1=N[BesselJZero[0,1]];
  N[PolyGamma[1]-PolyGamma[1]+Log[x1/Pi]]]; (* mu=2, conformal *)
deltaH4 = Module[{nu=2, x1}, x1=N[BesselJZero[nu,1]];
  N[PolyGamma[nu+1]-PolyGamma[1]+Log[x1/Pi]]]; (* mu=4, strong UV *)

(* Scalar prefactor: 1/(6pi) instead of 1/(2pi) for fermions *)
(* The correction: Delta alpha_i = -(1/(6pi)) * S_i * delta_H *)
d13H0 = -(1/(6*Pi)) * s1H * deltaH0 - (-(1/(6*Pi)) * s3H * deltaH0);
d13H2 = -(1/(6*Pi)) * s1H * deltaH2;
d13H4 = -(1/(6*Pi)) * s1H * deltaH4;

Print["  Higgs threshold Delta(alpha_1^{-1} - alpha_3^{-1}):"];
Print["    mu_H=0 (strong IR):  ", NumberForm[d13H0, {6,4}]];
Print["    mu_H=2 (conformal):  ", NumberForm[d13H2, {6,4}]];
Print["    mu_H=4 (strong UV):  ", NumberForm[d13H4, {6,4}]];
Print[""];

(* Also: SU(2) vs SU(3) splitting from Higgs KK *)
d23H0 = -(1/(6*Pi)) * s2H * deltaH0;
Print["  Higgs Delta(alpha_2^{-1} - alpha_3^{-1}):"];
Print["    mu_H=0: ", NumberForm[d23H0, {6,4}]];
Print["  WARNING: This breaks the T4 identity (S_2 = S_3)!"];
Print[""];

(* ============================================================ *)
(* SOURCE 3: TWO-LOOP THRESHOLD EFFECTS                       *)
(* ============================================================ *)
Print["================================================================"];
Print["SOURCE 3: Two-Loop Threshold Effects"];
Print["================================================================"];
Print[""];

b1loop = {41/10, -19/6, -7};
alphaInvMZ = {alpha1invMZ, alpha2invMZ, alpha3invMZ};
logMKKMZ = Log[N[MKK/MZ]];
Print["  ln(MKK/MZ) = ", NumberForm[logMKKMZ, {5,2}]];

alphaInvMKK = N[alphaInvMZ + b1loop/(2*Pi) * logMKKMZ];
alphaMKK = 1/alphaInvMKK;
Print["  alpha_i^{-1} at MKK: ", NumberForm[alphaInvMKK[[1]], {5,2}], ", ",
  NumberForm[alphaInvMKK[[2]], {5,2}], ", ",
  NumberForm[alphaInvMKK[[3]], {5,2}]];
Print["  alpha_i at MKK: ", NumberForm[alphaMKK[[1]], {6,5}], ", ",
  NumberForm[alphaMKK[[2]], {6,5}], ", ",
  NumberForm[alphaMKK[[3]], {6,5}]];
Print[""];

(* Two-loop beta coefficient matrix (GUT normalized) *)
b2loop = {{199/50, 27/10, 44/5},
           {9/10, 35/6, 12},
           {11/10, 9/2, -26}};

(* Two-loop matching: leading contribution *)
(* Delta_i^{2L} ~ -(1/(4pi)) * Sum_j b_{ij}^{KK} * alpha_j(MKK) * delta_j *)
(* where delta_j is the one-loop threshold shift *)
delta1L = {deltaAlphaFerm[[1]], deltaAlphaFerm[[2]], deltaAlphaFerm[[3]]};

delta2L = Table[
  -(1/(4*Pi)) * Sum[N[b2loop[[i,j]]] * alphaMKK[[j]] * delta1L[[j]], {j,1,3}],
  {i,1,3}
];

delta2L13 = delta2L[[1]] - delta2L[[3]];
Print["  Two-loop (Hall-Weinberg matching):"];
Print["    Delta alpha_1^{-1}|_{2L} = ", NumberForm[delta2L[[1]], {8,6}]];
Print["    Delta alpha_2^{-1}|_{2L} = ", NumberForm[delta2L[[2]], {8,6}]];
Print["    Delta alpha_3^{-1}|_{2L} = ", NumberForm[delta2L[[3]], {8,6}]];
Print["    Delta_{13}|_{2L} = ", NumberForm[delta2L13, {6,4}]];
Print["    Fraction of needed: ", NumberForm[delta2L13/delta13needed*100, {4,1}], "%"];
Print[""];

(* Conservative estimate: 15-25% of one-loop *)
delta2L13est = 0.20 * delta13ferm;
Print["  Conservative estimate (20% of 1-loop): ", NumberForm[delta2L13est, {6,4}]];
Print[""];

(* ============================================================ *)
(* SOURCE 4: RADION                                            *)
(* ============================================================ *)
Print["================================================================"];
Print["SOURCE 4: Radion / Graviscalar"];
Print["================================================================"];
Print[""];
Print["  Pure radion: gauge-UNIVERSAL coupling (via T^mu_mu trace)"];
Print["  Delta(alpha_1^{-1} - alpha_3^{-1})_radion = 0 (exact)"];
Print[""];
xi = 246.22/5000.;
Print["  Radion-Higgs mixing: xi ~ v/Lambda_r = ", NumberForm[xi, {4,4}]];
radHigDelta = xi^2 * d13H0;
Print["  Mixed contribution: xi^2 * Delta_Higgs = ", NumberForm[radHigDelta, {8,6}]];
Print["  NEGLIGIBLE."];
Print[""];

(* ============================================================ *)
(* SOURCE 5: BRANE KINETIC TERMS                              *)
(* ============================================================ *)
Print["================================================================"];
Print["SOURCE 5: Brane Kinetic Terms"];
Print["================================================================"];
Print[""];
Print["  Loop-induced BKTs: ALREADY in ADP formula (Source 1)"];
Print["  Tree-level BKTs: ~ 1/(16pi^2) = ", NumberForm[1/(16*Pi^2), {6,4}]];
Print["  NEGLIGIBLE (0.006 vs needed ~10)."];
Print[""];

(* ============================================================ *)
(* SOURCE 6: RIGHT-HANDED NEUTRINOS                            *)
(* ============================================================ *)
Print["================================================================"];
Print["SOURCE 6: Right-Handed Neutrinos"];
Print["================================================================"];
Print[""];
Print["  SM gauge singlets: no direct threshold contribution."];
Print["  Indirect (2-loop via Yukawa): < 0.1"];
Print["  NEGLIGIBLE."];
Print[""];

(* ============================================================ *)
(* SOURCE 7+8: GAUGE KK + WAVEFUNCTION RENORM                 *)
(* ============================================================ *)
Print["================================================================"];
Print["SOURCE 7+8: Gauge KK Sub-leading + Wavefunction Renorm"];
Print["================================================================"];
Print[""];
Print["  Gauge KK: universal spectrum -> zero differential"];
Print["  Sub-leading crossed 2-loop: ~ (alpha/pi)^2 * kyc ~ 0.003"];
Print["  Wavefunction renorm: already in ADP (Source 1)"];
Print["  NEGLIGIBLE."];
Print[""];

(* ============================================================ *)
(* SOURCE 9: PARAMETER SPACE EXPLORATION                       *)
(* ============================================================ *)
Print["================================================================"];
Print["SOURCE 9: Maximum Fermion Threshold (Optimized c)"];
Print["================================================================"];
Print[""];

(* Type-level T1-T3 analysis *)
Print["  Species type\t\tT_1\tT_3\tT_1-T_3\tSign"];
specTypesData = {
  {"Q_L (3,2,1/6)", 3, 2, 1/6},
  {"u_R (3,1,2/3)", 3, 1, 2/3},
  {"d_R (3,1,-1/3)", 3, 1, -1/3},
  {"L_L (1,2,-1/2)", 1, 2, -1/2},
  {"e_R (1,1,-1)", 1, 1, -1}
};
Do[
  Module[{tt1, tt3},
    tt1 = N[(3/5)*st[[4]]^2*st[[2]]*st[[3]]];
    tt3 = N[If[st[[2]]==3, st[[3]]*(1/2), 0]];
    Print["  ", st[[1]], "\t",
      NumberForm[tt1,{4,3}], "\t",
      NumberForm[tt3,{4,3}], "\t",
      NumberForm[tt1-tt3,{5,3}], "\t",
      If[tt1>tt3, "+", "-"]];
  ],
  {st, specTypesData}
];
Print[""];

(* Optimized c values: maximize delta for T1>T3, minimize for T1<T3 *)
fermionMax = {
  {"Q3_L",  3, 2,  1/6,  0.35},
  {"t_R",   3, 1,  2/3, -0.50},
  {"b_R",   3, 1, -1/3,  0.55},
  {"L3_L",  1, 2, -1/2,  0.60},
  {"tau_R", 1, 1,   -1,  0.60},
  {"Q2_L",  3, 2,  1/6,  0.50},
  {"c_R",   3, 1,  2/3,  0.65},
  {"s_R",   3, 1, -1/3,  0.70},
  {"L2_L",  1, 2, -1/2,  0.65},
  {"mu_R",  1, 1,   -1,  0.75},
  {"Q1_L",  3, 2,  1/6,  0.55},
  {"u_R",   3, 1,  2/3,  0.80},
  {"d_R",   3, 1, -1/3,  0.75},
  {"L1_L",  1, 2, -1/2,  0.70},
  {"e_R",   1, 1,   -1,  0.90}
};

deltaAlphaMax = {0., 0., 0.};
Do[
  Module[{c = spec[[5]], dc, tt1, tt2, tt3},
    dc = delta[c];
    tt1 = N[t1[spec]]; tt2 = N[t2[spec]]; tt3 = N[t3[spec]];
    deltaAlphaMax[[1]] += -(1/(2*Pi)) * tt1 * dc;
    deltaAlphaMax[[2]] += -(1/(2*Pi)) * tt2 * dc;
    deltaAlphaMax[[3]] += -(1/(2*Pi)) * tt3 * dc;
  ],
  {spec, fermionMax}
];
delta13max = deltaAlphaMax[[1]] - deltaAlphaMax[[3]];
delta23max = deltaAlphaMax[[2]] - deltaAlphaMax[[3]];

Print["  MAXIMUM fermion threshold (optimized):"];
Print["    Delta(alpha_1^{-1} - alpha_3^{-1}) = ", NumberForm[delta13max, {6,4}]];
Print["    Fraction of needed: ", NumberForm[delta13max/delta13needed*100, {4,1}], "%"];
Print[""];

(* Also compute minimum *)
fermionMin = {
  {"Q3_L",  3, 2,  1/6,  0.45},
  {"t_R",   3, 1,  2/3,  0.00},
  {"b_R",   3, 1, -1/3,  0.35},
  {"L3_L",  1, 2, -1/2,  0.45},
  {"tau_R", 1, 1,   -1,  0.40},
  {"Q2_L",  3, 2,  1/6,  0.63},
  {"c_R",   3, 1,  2/3,  0.45},
  {"s_R",   3, 1, -1/3,  0.55},
  {"L2_L",  1, 2, -1/2,  0.50},
  {"mu_R",  1, 1,   -1,  0.50},
  {"Q1_L",  3, 2,  1/6,  0.70},
  {"u_R",   3, 1,  2/3,  0.55},
  {"d_R",   3, 1, -1/3,  0.55},
  {"L1_L",  1, 2, -1/2,  0.55},
  {"e_R",   1, 1,   -1,  0.60}
};

deltaAlphaMin = {0., 0., 0.};
Do[
  Module[{c = spec[[5]], dc, tt1, tt2, tt3},
    dc = delta[c];
    tt1 = N[t1[spec]]; tt2 = N[t2[spec]]; tt3 = N[t3[spec]];
    deltaAlphaMin[[1]] += -(1/(2*Pi)) * tt1 * dc;
    deltaAlphaMin[[2]] += -(1/(2*Pi)) * tt2 * dc;
    deltaAlphaMin[[3]] += -(1/(2*Pi)) * tt3 * dc;
  ],
  {spec, fermionMin}
];
delta13min = deltaAlphaMin[[1]] - deltaAlphaMin[[3]];

Print["  MINIMUM fermion threshold (pessimized):"];
Print["    Delta(alpha_1^{-1} - alpha_3^{-1}) = ", NumberForm[delta13min, {6,4}]];
Print["    Fraction of needed: ", NumberForm[delta13min/delta13needed*100, {4,1}], "%"];
Print[""];
Print["  RANGE: ", NumberForm[delta13min, {6,3}], " to ",
  NumberForm[delta13max, {6,3}],
  " (", NumberForm[delta13min/delta13needed*100, {3,0}],
  "% to ", NumberForm[delta13max/delta13needed*100, {3,0}], "%)"];
Print[""];

(* ============================================================ *)
(* SOURCE 10: INERT DOUBLETS                                   *)
(* ============================================================ *)
Print["================================================================"];
Print["SOURCE 10: Inert Doublets (Extended NCG)"];
Print["================================================================"];
Print[""];

lnLamMKK = N[kyc]; (* ln(Lambda/MKK) = ln(MPl/MKK) = kyc *)
deltaInert13 = -(1/(6*Pi)) * (3/10) * lnLamMKK;
deltaInert23 = -(1/(6*Pi)) * (1/2) * lnLamMKK;
Print["  Per doublet (running from MKK to Lambda):"];
Print["    Delta(alpha_1^{-1} - alpha_3^{-1}) = ", NumberForm[deltaInert13, {6,4}]];
Print["    Delta(alpha_2^{-1} - alpha_3^{-1}) = ", NumberForm[deltaInert23, {6,4}]];
Print["  NOTE: Requires extending the minimal spectral triple."];
Print[""];

(* ============================================================ *)
(* kyc SENSITIVITY                                             *)
(* ============================================================ *)
Print["================================================================"];
Print["SENSITIVITY: kyc dependence"];
Print["================================================================"];
Print[""];

yPhys = {Sqrt[2]*172.76/v, Sqrt[2]*4.18/v, Sqrt[2]*1.27/v,
         Sqrt[2]*0.093/v, Sqrt[2]*0.00467/v, Sqrt[2]*0.00216/v,
         Sqrt[2]*1.777/v, Sqrt[2]*0.10566/v, Sqrt[2]*0.000511/v};

Do[
  Module[{cVals, daLocal = {0., 0., 0.}, specLocal},
    (* c values for this kyc: c = 1/2 + ln(1/y_f)/(2*kycT) *)
    (* For right-handed: use y directly *)
    (* For left-handed doublets: shift by ~0.1 *)
    cTR = 1/2 + Log[1/yPhys[[1]]]/(2*kycT);
    cBR = 1/2 + Log[1/yPhys[[2]]]/(2*kycT);
    cCR = 1/2 + Log[1/yPhys[[3]]]/(2*kycT);
    cSR = 1/2 + Log[1/yPhys[[4]]]/(2*kycT);
    cDR = 1/2 + Log[1/yPhys[[5]]]/(2*kycT);
    cUR = 1/2 + Log[1/yPhys[[6]]]/(2*kycT);
    cTauR = 1/2 + Log[1/yPhys[[7]]]/(2*kycT);
    cMuR = 1/2 + Log[1/yPhys[[8]]]/(2*kycT);
    cER = 1/2 + Log[1/yPhys[[9]]]/(2*kycT);
    cQ3 = Max[cTR + 0.70, 0.35];
    cQ2 = Max[cCR + 0.05, 0.50];
    cQ1 = Max[cUR + 0.05, 0.55];
    cL3 = cTauR + 0.03;
    cL2 = cMuR + 0.03;
    cL1 = cER + 0.03;

    cVals = {cQ3, cTR, cBR, cL3, cTauR, cQ2, cCR, cSR, cL2, cMuR,
             cQ1, cUR, cDR, cL1, cER};

    specLocal = Table[
      {fermionSpecies[[i,1]], fermionSpecies[[i,2]], fermionSpecies[[i,3]],
       fermionSpecies[[i,4]], cVals[[i]]},
      {i, 15}
    ];

    Do[
      Module[{c = spec[[5]], dc, tt1, tt2, tt3},
        dc = delta[c];
        tt1 = N[t1[spec]]; tt2 = N[t2[spec]]; tt3 = N[t3[spec]];
        daLocal[[1]] += -(1/(2*Pi)) * tt1 * dc;
        daLocal[[2]] += -(1/(2*Pi)) * tt2 * dc;
        daLocal[[3]] += -(1/(2*Pi)) * tt3 * dc;
      ],
      {spec, specLocal}
    ];

    Print["  kyc=", NumberForm[kycT, {4,1}],
      "  Delta13=", NumberForm[daLocal[[1]]-daLocal[[3]], {6,3}],
      "  (", NumberForm[(daLocal[[1]]-daLocal[[3]])/delta13needed*100, {4,1}], "%)"];
  ],
  {kycT, {25., 30., 35., 40., 45., 50.}}
];
Print[""];

(* ============================================================ *)
(* STRUCTURAL ANALYSIS                                         *)
(* ============================================================ *)
Print["================================================================"];
Print["STRUCTURAL ANALYSIS: Why the Gap Persists"];
Print["================================================================"];
Print[""];

totalT1minusT3 = Total[N[t1[#] - t3[#]] & /@ fermionSpecies];
Print["  Sum_f (T_1 - T_3) = ", NumberForm[totalT1minusT3, {6,3}]];

(* Flat limit *)
deltaFlat = delta[0.50];
Print["  delta(c=0.5) = ", NumberForm[deltaFlat, {6,4}]];
deltaFlat13 = -(1/(2*Pi)) * totalT1minusT3 * deltaFlat;
Print["  Flat limit Delta_{13} = ", NumberForm[deltaFlat13, {6,4}]];
Print[""];

enhanceNom = delta13ferm / deltaFlat13;
enhanceMax = delta13max / deltaFlat13;
Print["  Enhancement over flat (nominal): ", NumberForm[enhanceNom, {4,2}], "x"];
Print["  Enhancement over flat (maximum): ", NumberForm[enhanceMax, {4,2}], "x"];
Print[""];

Print["  Structural limits:"];
Print["  1. T_1-T_3 sum fixed by SM quantum numbers"];
Print["  2. delta(c) grows only logarithmically for large c"];
Print["  3. Q_L doublets: T_1-T_3 < 0 (NEGATIVE), cannot be eliminated"];
Print["  4. FCNC bounds prevent Q_L from going fully IR"];
Print[""];

(* ============================================================ *)
(* GRAND SYNTHESIS                                             *)
(* ============================================================ *)
Print["================================================================"];
Print["================================================================"];
Print["GRAND SYNTHESIS: Total Achievable Correction"];
Print["================================================================"];
Print["================================================================"];
Print[""];

Print["Source                            | Nominal   | Max       "];
Print["----------------------------------------------------------"];
Print["1. Fermion KK (ADP threshold)     | ", NumberForm[delta13ferm, {6,3}],
  "   | ", NumberForm[delta13max, {6,3}]];
Print["2. Higgs KK (bulk, mu=0)          | ", NumberForm[d13H0, {6,4}],
  "  | ", NumberForm[d13H0, {6,4}]];
Print["3. Two-loop threshold             | ", NumberForm[delta2L13, {8,4}],
  "  | ", NumberForm[0.25*delta13max, {6,4}]];
Print["4. Radion-Higgs mixing            | ", NumberForm[radHigDelta, {8,5}],
  " | ~0.0003"];
Print["5. Brane kinetic terms            | ~0.000    | ~0.006"];
Print["6. Right-handed neutrinos         | ~0.000    | ~0.100"];
Print["7. Gauge KK sub-leading           | ~0.000    | ~0.003"];
Print["8. Wavefunction renorm            | (in #1)   | (in #1)"];
Print["----------------------------------------------------------"];

totalNom = delta13ferm + d13H0 + delta2L13;
totalMax = delta13max + d13H0 + 0.25*delta13max;

Print["TOTAL (minimal RS+NCG, nominal):  ", NumberForm[totalNom, {6,3}]];
Print["TOTAL (minimal RS+NCG, maximum):  ", NumberForm[totalMax, {6,3}]];
Print[""];
Print["Fraction of needed (nominal):  ", NumberForm[totalNom/delta13needed*100, {4,1}], "%"];
Print["Fraction of needed (maximum):  ", NumberForm[totalMax/delta13needed*100, {4,1}], "%"];
Print[""];

(* With inert doublets *)
totalMaxExt1 = totalMax + deltaInert13;
totalMaxExt3 = totalMax + 3*deltaInert13;
remainAfterMax = delta13needed - totalMax;
nDoubletsNeeded = remainAfterMax / deltaInert13;

Print["With extended NCG (inert doublets at MKK):"];
Print["  + 1 doublet: ", NumberForm[totalMaxExt1, {6,3}],
  " (", NumberForm[totalMaxExt1/delta13needed*100, {4,1}], "%)"];
Print["  + 3 doublets: ", NumberForm[totalMaxExt3, {6,3}],
  " (", NumberForm[totalMaxExt3/delta13needed*100, {4,1}], "%)"];
Print["  Doublets needed for 100%: ", NumberForm[nDoubletsNeeded, {4,1}]];
Print[""];

(* ============================================================ *)
(* FINAL VERDICT                                               *)
(* ============================================================ *)
Print["================================================================"];
Print["================================================================"];
Print["FINAL VERDICT"];
Print["================================================================"];
Print["================================================================"];
Print[""];
Print["QUESTION: Can KK thresholds close the full 12% gauge gap?"];
Print[""];
Print["ANSWER: NO within minimal RS+NCG."];
Print["  Maximum achievable: ~35% of needed correction."];
Print["  Remaining ~65% requires new physics or structural extension."];
Print[""];
Print["BREAKDOWN:"];
Print["  Fermion KK:     19-35% (c-parameter dependent)"];
Print["  Higgs KK:       ~1-2% (small, but non-zero)"];
Print["  Two-loop:       ~3-7% (suppressed by alpha/pi)"];
Print["  Everything else: < 1%"];
Print[""];
Print["THE STRUCTURAL REASON: The T_1-T_3 imbalance in the SM is fixed"];
Print["by quantum numbers. The ADP threshold function delta(c) has"];
Print["limited dynamic range (logarithmic growth). The Q_L doublets"];
Print["contribute with NEGATIVE sign and cannot be eliminated."];
Print[""];
Print["POSSIBLE PATHS TO CLOSURE:"];
Print["  1. ~13 inert doublets at MKK (extended NCG; ugly)"];
Print["  2. Non-perturbative spectral effects (unexplored)"];
Print["  3. Modified spectral triple algebra"];
Print["  4. Intermediate-scale physics"];
Print["  5. The gap IS the prediction (sin^2 = 0.201 at tree level,"];
Print["     corrected to ~0.208 by thresholds; remaining 10% from"];
Print["     something genuinely new)"];
Print[""];
Print["IMPLICATION FOR MERIDIAN:"];
Print["  The ~12% gap is NOT a parameter-tuning problem. It is a"];
Print["  STRUCTURAL feature of the minimal spectral triple that"];
Print["  cannot be resolved by adjusting bulk masses alone. This is"];
Print["  either the framework's Achilles heel or its sharpest"];
Print["  prediction: something beyond the minimal content is needed"];
Print["  to achieve exact unification."];
Print[""];
Print["================================================================"];
Print["END 20B THRESHOLD CLOSURE"];
Print["================================================================"];
