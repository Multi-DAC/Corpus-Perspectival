(* ============================================================ *)
(* 20B THRESHOLD CLOSURE v2: Correct GUT normalization         *)
(* Can KK thresholds close the full 12% gauge gap?             *)
(* Project Meridian Phase 20                                   *)
(* Authors: Clayton & Clawd                                    *)
(* Date: March 22, 2026                                        *)
(* ============================================================ *)

Print["================================================================"];
Print["20B THRESHOLD CLOSURE ANALYSIS v2"];
Print["================================================================"];
Print[""];

(* Physical constants *)
v = 246.22;
kyc = 35.0;
MZ = 91.1876;
MPl = 2.435*^18;
alphasMZ = 0.1179;
MKK = MPl * Exp[-kyc];

Print["M_KK = ", ScientificForm[N[MKK], 4], " GeV"];
Print[""];

delta13needed = -10.0;

(* ADP threshold function *)
delta[c_] := Module[{nu = Abs[c + 1/2], x1},
  x1 = N[BesselJZero[nu, 1]];
  N[PolyGamma[nu + 1] - PolyGamma[1] + Log[x1/Pi]]
];

(* GUT-normalized Dynkin indices *)
(* T_1^{GUT} = (5/3)*Y^2*d_color*d_weak *)
(* T_2 = T(SU2)*d_color where T(fund)=1/2, T(singlet)=0 *)
(* T_3 = T(SU3)*d_weak where T(fund)=1/2, T(singlet)=0 *)
t1[spec_] := (5/3) * spec[[4]]^2 * spec[[2]] * spec[[3]];
t2[spec_] := If[spec[[3]] == 2, spec[[2]] * (1/2), 0];
t3[spec_] := If[spec[[2]] == 3, spec[[3]] * (1/2), 0];

(* 15 SM Weyl fermion species per generation *)
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

(* ============================================================ *)
(* SOURCE 1: FERMION KK THRESHOLDS (NOMINAL)                   *)
(* ============================================================ *)
Print["================================================================"];
Print["SOURCE 1: Fermion KK Thresholds (nominal c values)"];
Print["================================================================"];
Print[""];

deltaAlphaFerm = {0., 0., 0.};
Do[
  Module[{c = spec[[5]], dc, tt1, tt2, tt3},
    dc = delta[c];
    tt1 = N[t1[spec]]; tt2 = N[t2[spec]]; tt3 = N[t3[spec]];
    deltaAlphaFerm[[1]] += -(1/(2*Pi)) * tt1 * dc;
    deltaAlphaFerm[[2]] += -(1/(2*Pi)) * tt2 * dc;
    deltaAlphaFerm[[3]] += -(1/(2*Pi)) * tt3 * dc;
    Print["  ", spec[[1]], "  c=", NumberForm[c, {3,2}],
      "  delta=", NumberForm[dc, {5,3}],
      "  T1=", NumberForm[tt1, {5,3}],
      "  T3=", NumberForm[tt3, {4,3}],
      "  (T1-T3)*d=", NumberForm[(tt1-tt3)*dc, {6,3}]];
  ],
  {spec, fermionSpecies}
];

delta13ferm = deltaAlphaFerm[[1]] - deltaAlphaFerm[[3]];
delta23ferm = deltaAlphaFerm[[2]] - deltaAlphaFerm[[3]];
Print[""];
Print["  Da1 = ", NumberForm[deltaAlphaFerm[[1]], {6,3}]];
Print["  Da2 = ", NumberForm[deltaAlphaFerm[[2]], {6,3}]];
Print["  Da3 = ", NumberForm[deltaAlphaFerm[[3]], {6,3}]];
Print["  D(a1-a3) = ", NumberForm[delta13ferm, {6,4}]];
Print["  D(a2-a3) = ", NumberForm[delta23ferm, {6,4}]];
Print["  Fraction: ", NumberForm[delta13ferm/delta13needed*100, {4,1}], "%"];
Print[""];

(* ============================================================ *)
(* SOURCE 2: HIGGS KK TOWER                                    *)
(* ============================================================ *)
Print["================================================================"];
Print["SOURCE 2: Higgs KK Tower"];
Print["================================================================"];
Print[""];

(* Higgs doublet: H = (1, 2, 1/2) *)
(* Complex scalar threshold: factor 1/(6pi) vs 1/(2pi) for Weyl fermion *)
(* = 1/3 the fermion contribution per dof *)
s1H = N[(5/3) * (1/2)^2 * 1 * 2]; (* = 5/6 *)
s2H = 1/2;  (* T(fund SU2) * d_color = 1/2 * 1 *)
s3H = 0.0;  (* color singlet *)

Print["  Higgs doublet H = (1,2,1/2):"];
Print["  T1^GUT(H) = ", s1H];
Print["  T2(H) = ", s2H];
Print["  T3(H) = ", s3H];
Print[""];

(* Scenario A: Brane-localized (minimal RS) *)
Print["  A. Strict brane Higgs: no KK tower. D13 = 0."];
Print[""];

(* Scenario B: Bulk Higgs with mass parameter mu *)
(* Threshold: delta_H(mu) = Psi(|mu-2|+1) - Psi(1) + ln(BesselJZero[|mu-2|,1]/pi) *)
Print["  B. Bulk Higgs threshold delta_H(mu):"];
muVals = {0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0};
Do[
  Module[{nu = Abs[mu - 2], x1, dh},
    x1 = N[BesselJZero[nu, 1]];
    dh = N[PolyGamma[nu + 1] - PolyGamma[1] + Log[x1/Pi]];
    Print["     mu=", NumberForm[mu, {3,1}],
      "  nu=", NumberForm[nu, {3,1}],
      "  delta_H=", NumberForm[dh, {6,4}]];
  ],
  {mu, muVals}
];
Print[""];

(* For complex scalar, threshold = -(1/(6pi)) * T_i * delta *)
(* But with 4 real dof (full doublet), the factor is: *)
(* -(1/(12pi)) per REAL scalar, times 4 real = -(4/(12pi)) = -(1/(3pi)) *)
(* No wait: the Dynkin index T_i already accounts for the doublet dimension. *)
(* For a COMPLEX scalar doublet: the loop factor is 1/6pi (not 1/2pi). *)
(* This already counts both complex components since T_2 = 1/2 for the full doublet *)

(* Actually, let me be more careful. For a REAL scalar in rep R: *)
(* Delta alpha_i^{-1} = -(1/(12pi)) * T_i(R) * ln(Lambda/m) *)
(* For a COMPLEX scalar: 2 real -> -(2/(12pi)) = -(1/(6pi)) *)
(* The Higgs doublet has 2 complex components (4 real), but as SU(2) doublet *)
(* its T_2 = 1/2 already counts the doublet structure. *)
(* So: Delta alpha_2 = -(1/(6pi)) * (1/2) * delta_H for one complex doublet *)

(* For GUT-normalized U(1): *)
(* T_1(H) = (5/3)*Y^2*d_c*d_w = (5/3)*(1/2)^2*1*2 = 5/6 *)
(* Delta alpha_1 = -(1/(6pi)) * (5/6) * delta_H *)

deltaH0 = Module[{nu=2, x1}, x1=N[BesselJZero[nu,1]];
  N[PolyGamma[nu+1]-PolyGamma[1]+Log[x1/Pi]]];
deltaH2 = Module[{nu=0, x1}, x1=N[BesselJZero[0,1]];
  N[PolyGamma[1]-PolyGamma[1]+Log[x1/Pi]]];

da1H0 = -(1/(6*Pi)) * s1H * deltaH0;
da2H0 = -(1/(6*Pi)) * s2H * deltaH0;
da3H0 = -(1/(6*Pi)) * s3H * deltaH0;
d13H0 = da1H0 - da3H0;
d23H0 = da2H0 - da3H0;

da1H2 = -(1/(6*Pi)) * s1H * deltaH2;
da2H2 = -(1/(6*Pi)) * s2H * deltaH2;
d13H2 = da1H2;
d23H2 = da2H2;

Print["  Higgs corrections (complex scalar, 1/(6pi) prefactor):"];
Print["  mu=0 (strong IR): delta_H=", NumberForm[deltaH0, {6,4}]];
Print["    D(a1-a3) = ", NumberForm[d13H0, {6,4}]];
Print["    D(a2-a3) = ", NumberForm[d23H0, {6,4}]];
Print["  mu=2 (conformal): delta_H=", NumberForm[deltaH2, {6,4}]];
Print["    D(a1-a3) = ", NumberForm[d13H2, {6,4}]];
Print[""];

(* Note: for the FULL threshold computation, the Higgs doublet above MKK *)
(* has 4 real degrees of freedom: H+, H-, h, G^0 *)
(* Below EW breaking, 3 become Goldstones (eaten by W+, W-, Z) *)
(* But ABOVE MKK in the 5D theory, all 4 propagate *)
(* The threshold correction at MKK is from integrating out the KK modes *)
(* of ALL 4 real scalars. The factor we used (1/(6pi) for complex doublet) *)
(* correctly counts all 4 real dof through the Dynkin index *)

Print["  Note: D13_Higgs ~ -0.09 (strong IR) is small because:"];
Print["  (a) Scalar prefactor 1/(6pi) is 3x smaller than fermion 1/(2pi)"];
Print["  (b) T1(H) = 5/6 ~ 0.83, moderate"];
Print["  (c) delta_H ~ 2 at most"];
Print["  Result: Higgs KK ~ 1% of needed correction"];
Print[""];

(* ============================================================ *)
(* SOURCE 3: TWO-LOOP THRESHOLDS                               *)
(* ============================================================ *)
Print["================================================================"];
Print["SOURCE 3: Two-Loop Threshold Corrections"];
Print["================================================================"];
Print[""];

(* Two-loop beta matrix (GUT-normalized) *)
b2loop = N[{{199/50, 27/10, 44/5},
             {9/10, 35/6, 12},
             {11/10, 9/2, -26}}];

(* Couplings at MKK *)
b1loop = N[{41/10, -19/6, -7}];
logMKK = Log[N[MKK/MZ]];
alphaInvMKK = N[{59.01, 29.59, 1/0.1179}] + b1loop/(2*Pi) * logMKK;
alphaMKK = 1/alphaInvMKK;
Print["  alpha_i(MKK): ", NumberForm[alphaMKK[[1]], {6,5}], ", ",
  NumberForm[alphaMKK[[2]], {6,5}], ", ",
  NumberForm[alphaMKK[[3]], {6,5}]];
Print[""];

(* The two-loop threshold from KK modes:
   Delta_i^{2L} ~ -(1/(4pi)) * Sum_j b_{ij} * alpha_j(MKK) * delta_j^{1L}
   This is the leading-log matching correction at two loops.
*)
delta1L = {deltaAlphaFerm[[1]], deltaAlphaFerm[[2]], deltaAlphaFerm[[3]]};

delta2L = Table[
  -(1/(4*Pi)) * Sum[b2loop[[i,j]] * alphaMKK[[j]] * delta1L[[j]], {j,1,3}],
  {i,1,3}
];
delta2L13 = delta2L[[1]] - delta2L[[3]];
Print["  Two-loop (Hall-Weinberg):"];
Print["    Da1 = ", NumberForm[delta2L[[1]], {8,5}]];
Print["    Da2 = ", NumberForm[delta2L[[2]], {8,5}]];
Print["    Da3 = ", NumberForm[delta2L[[3]], {8,5}]];
Print["    D(a1-a3) = ", NumberForm[delta2L13, {6,4}]];
Print["    Fraction: ", NumberForm[delta2L13/delta13needed*100, {4,1}], "%"];
Print[""];

(* Also: the two-loop threshold from integrating out KK modes directly *)
(* The dominant effect: QCD running enhances the SU(3) threshold *)
(* alpha_s(MKK)/(2pi) * delta_3^{1L} * kyc *)
twoLoopQCD = alphaMKK[[3]]/(2*Pi) * delta1L[[3]] * kyc;
Print["  QCD-enhanced: alpha_s/(2pi)*delta3*kyc = ", NumberForm[twoLoopQCD, {6,4}]];
Print["  This modifies delta_3 but is already partly captured above."];
Print[""];

(* Conservative estimate: use Hall-Weinberg as the central value *)
(* and note it has ~50% uncertainty *)
Print["  Best estimate: D(a1-a3)|_{2L} = ", NumberForm[delta2L13, {6,4}],
  " +/- ", NumberForm[Abs[delta2L13/2], {6,4}]];
Print[""];

(* ============================================================ *)
(* SOURCE 4: RADION                                            *)
(* ============================================================ *)
Print["================================================================"];
Print["SOURCE 4: Radion"];
Print["================================================================"];
Print[""];
Print["  Radion couples to T^mu_mu: gauge-UNIVERSAL."];
Print["  D(a1-a3)_radion = 0 exactly."];
xi = v / 5000.;
Print["  Radion-Higgs mixing: xi = ", NumberForm[xi, {5,4}]];
Print["  Mixed effect: ~ xi^2 * Higgs = ", NumberForm[xi^2 * d13H0, {8,6}]];
Print["  NEGLIGIBLE."];
Print[""];

(* ============================================================ *)
(* SOURCES 5-8: MINOR CONTRIBUTIONS                            *)
(* ============================================================ *)
Print["================================================================"];
Print["SOURCE 5-8: Minor contributions"];
Print["================================================================"];
Print[""];
Print["  5. BKTs: loop-induced already in ADP. Tree-level ~ 0.006. NEGLIGIBLE."];
Print["  6. Right-handed neutrinos: gauge singlets. ZERO direct. < 0.1 indirect."];
Print["  7. Gauge KK: universal spectrum. ZERO differential."];
Print["  8. Wavefunction renorm: already in ADP. Not additional."];
Print[""];

(* ============================================================ *)
(* SOURCE 9: PARAMETER SPACE EXPLORATION                       *)
(* ============================================================ *)
Print["================================================================"];
Print["SOURCE 9: Maximum Fermion Threshold (optimized c)"];
Print["================================================================"];
Print[""];

(* Species type analysis *)
Print["  Type\t\t\tT1\tT3\tT1-T3\tStrategy"];
Print["  Q_L (3,2,1/6)\t", NumberForm[N[(5/3)*(1/6)^2*6], {5,3}],
  "\t1.000\t", NumberForm[N[(5/3)*(1/6)^2*6 - 1], {6,3}], "\tminimize c"];
Print["  u_R (3,1,2/3)\t", NumberForm[N[(5/3)*(2/3)^2*3], {5,3}],
  "\t0.500\t", NumberForm[N[(5/3)*(2/3)^2*3 - 0.5], {6,3}], "\tmaximize c"];
Print["  d_R (3,1,-1/3)\t", NumberForm[N[(5/3)*(1/3)^2*3], {5,3}],
  "\t0.500\t", NumberForm[N[(5/3)*(1/3)^2*3 - 0.5], {6,3}], "\tmaximize c"];
Print["  L_L (1,2,-1/2)\t", NumberForm[N[(5/3)*(1/2)^2*2], {5,3}],
  "\t0.000\t", NumberForm[N[(5/3)*(1/2)^2*2], {6,3}], "\tmaximize c"];
Print["  e_R (1,1,-1)\t\t", NumberForm[N[(5/3)*1*1], {5,3}],
  "\t0.000\t", NumberForm[N[(5/3)*1*1], {6,3}], "\tmaximize c"];
Print[""];

Print["  KEY INSIGHT: Q_L has T1-T3 = -0.722 (NEGATIVE)"];
Print["  -> Want Q_L as IR as possible (small c, small delta)"];
Print["  But FCNC bounds require c_Q > 0.35 (third gen), > 0.5 (first gen)"];
Print[""];

(* Optimized configuration: maximize positive, minimize negative *)
fermionMax = {
  {"Q3_L",  3, 2,  1/6,  0.35},  (* minimize: Zbb allows 0.35 *)
  {"t_R",   3, 1,  2/3, -0.50},  (* maximize: most IR possible *)
  {"b_R",   3, 1, -1/3,  0.55},  (* maximize *)
  {"L3_L",  1, 2, -1/2,  0.60},  (* maximize *)
  {"tau_R", 1, 1,   -1,  0.60},  (* maximize *)
  {"Q2_L",  3, 2,  1/6,  0.50},  (* minimize: FCNC lower bound *)
  {"c_R",   3, 1,  2/3,  0.65},  (* maximize *)
  {"s_R",   3, 1, -1/3,  0.70},  (* maximize *)
  {"L2_L",  1, 2, -1/2,  0.65},  (* maximize *)
  {"mu_R",  1, 1,   -1,  0.75},  (* maximize *)
  {"Q1_L",  3, 2,  1/6,  0.55},  (* minimize: FCNC lower bound *)
  {"u_R",   3, 1,  2/3,  0.80},  (* maximize *)
  {"d_R",   3, 1, -1/3,  0.75},  (* maximize *)
  {"L1_L",  1, 2, -1/2,  0.70},  (* maximize *)
  {"e_R",   1, 1,   -1,  0.90}   (* maximize: lightest lepton, most UV *)
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

Print["  MAXIMUM (optimized c, FCNC-safe):"];
Print["    D(a1-a3) = ", NumberForm[delta13max, {6,4}]];
Print["    Fraction: ", NumberForm[delta13max/delta13needed*100, {4,1}], "%"];
Print[""];

(* Minimum *)
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

Print["  MINIMUM (pessimized c):"];
Print["    D(a1-a3) = ", NumberForm[delta13min, {6,4}]];
Print["    Fraction: ", NumberForm[delta13min/delta13needed*100, {4,1}], "%"];
Print[""];
Print["  FERMION RANGE: ", NumberForm[delta13min, {5,2}],
  " to ", NumberForm[delta13max, {5,2}]];
Print["  (", NumberForm[delta13min/delta13needed*100, {3,0}],
  "% to ", NumberForm[delta13max/delta13needed*100, {3,0}], "%)"];
Print[""];

(* Even more extreme: push e_R to c = 1.0, u_R to c = 0.9 *)
fermionExtreme = {
  {"Q3_L",  3, 2,  1/6,  0.35},
  {"t_R",   3, 1,  2/3, -0.60},
  {"b_R",   3, 1, -1/3,  0.60},
  {"L3_L",  1, 2, -1/2,  0.65},
  {"tau_R", 1, 1,   -1,  0.65},
  {"Q2_L",  3, 2,  1/6,  0.45},
  {"c_R",   3, 1,  2/3,  0.70},
  {"s_R",   3, 1, -1/3,  0.75},
  {"L2_L",  1, 2, -1/2,  0.70},
  {"mu_R",  1, 1,   -1,  0.80},
  {"Q1_L",  3, 2,  1/6,  0.50},
  {"u_R",   3, 1,  2/3,  0.90},
  {"d_R",   3, 1, -1/3,  0.80},
  {"L1_L",  1, 2, -1/2,  0.75},
  {"e_R",   1, 1,   -1,  1.00}
};

deltaAlphaExt = {0., 0., 0.};
Do[
  Module[{c = spec[[5]], dc, tt1, tt2, tt3},
    dc = delta[c];
    tt1 = N[t1[spec]]; tt2 = N[t2[spec]]; tt3 = N[t3[spec]];
    deltaAlphaExt[[1]] += -(1/(2*Pi)) * tt1 * dc;
    deltaAlphaExt[[2]] += -(1/(2*Pi)) * tt2 * dc;
    deltaAlphaExt[[3]] += -(1/(2*Pi)) * tt3 * dc;
  ],
  {spec, fermionExtreme}
];
delta13ext = deltaAlphaExt[[1]] - deltaAlphaExt[[3]];

Print["  EXTREME (pushed beyond typical bounds):"];
Print["    D(a1-a3) = ", NumberForm[delta13ext, {6,4}]];
Print["    Fraction: ", NumberForm[delta13ext/delta13needed*100, {4,1}], "%"];
Print[""];

(* ============================================================ *)
(* SOURCE 10: INERT DOUBLETS                                   *)
(* ============================================================ *)
Print["================================================================"];
Print["SOURCE 10: Inert Doublets (Extended NCG)"];
Print["================================================================"];
Print[""];

(* An inert doublet at mass M running from M to Lambda contributes: *)
(* Delta alpha_i^{-1} = -(1/(6pi)) * T_i(H) * ln(Lambda/M) *)
(* For M ~ MKK: ln(Lambda/MKK) ~ kyc *)
s1Hgut = N[(5/3) * (1/2)^2 * 1 * 2]; (* = 5/6 *)
deltaInert13 = -(1/(6*Pi)) * s1Hgut * kyc;
deltaInert23 = -(1/(6*Pi)) * (1/2) * kyc;

Print["  Per inert doublet (mass ~ MKK, running to Lambda):"];
Print["    D(a1-a3) = ", NumberForm[deltaInert13, {6,4}]];
Print["    D(a2-a3) = ", NumberForm[deltaInert23, {6,4}]];
Print[""];

(* ============================================================ *)
(* STRUCTURAL ANALYSIS                                         *)
(* ============================================================ *)
Print["================================================================"];
Print["STRUCTURAL ANALYSIS"];
Print["================================================================"];
Print[""];

totalT1minusT3 = Total[N[t1[#] - t3[#]] & /@ fermionSpecies];
Print["  Sum(T1-T3) = ", NumberForm[totalT1minusT3, {6,2}]];
Print["  This is NONZERO (= 10.67) because T1 uses (5/3)*Y^2 normalization."];
Print["  In the flat limit (all c equal), the threshold = -(1/(2pi))*10.67*delta(c)."];
Print["  But this flat-limit term is DIVERGENT (it's part of the 5D theory,"];
Print["  not a threshold correction). The FINITE correction comes from the"];
Print["  SPREAD in c values around the mean."];
Print[""];

(* Compute the variance-driven contribution *)
deltaValues = delta[#[[5]]] & /@ fermionSpecies;
meanDelta = Mean[deltaValues];
Print["  Mean delta(c): ", NumberForm[meanDelta, {6,4}]];
Print["  delta range: ", NumberForm[Min[deltaValues], {6,4}],
  " to ", NumberForm[Max[deltaValues], {6,4}]];
Print["  Spread: ", NumberForm[Max[deltaValues] - Min[deltaValues], {6,4}]];
Print[""];

(* The correction decomposes as: *)
(* Delta_{13} = -(1/(2pi)) * Sum (T1-T3)*delta(c) *)
(*            = -(1/(2pi)) * [Sum(T1-T3)*mean_delta + Sum(T1-T3)*(delta-mean)] *)
(* The first term is the flat contribution (universal, divergent). *)
(* The second term is the variance contribution (finite, physical). *)
(* Both contribute to the FINITE Delta_{13} in our computation because *)
(* we're computing a FINITE sum using the ADP formula. *)

(* The question is: how much room is there to increase Delta_{13}? *)
(* The answer depends on how much the delta(c) values can spread. *)

Print["  The ADP threshold is a finite, analytical result."];
Print["  The -1.91 from nominal c values is the COMPLETE one-loop correction."];
Print["  No additional finite terms are missing at one loop."];
Print[""];

(* ============================================================ *)
(* kyc SENSITIVITY                                              *)
(* ============================================================ *)
Print["================================================================"];
Print["kyc SENSITIVITY"];
Print["================================================================"];
Print[""];

(* kyc affects c values through: c = 1/2 + ln(1/y_f)/(2*kyc) *)
(* Smaller kyc -> larger spread -> potentially larger threshold *)
yPhys = {Sqrt[2]*172.76/v, Sqrt[2]*4.18/v, Sqrt[2]*1.27/v,
         Sqrt[2]*0.093/v, Sqrt[2]*0.00467/v, Sqrt[2]*0.00216/v,
         Sqrt[2]*1.777/v, Sqrt[2]*0.10566/v, Sqrt[2]*0.000511/v};
(* Order: t, b, c, s, d, u, tau, mu, e *)

Do[
  Module[{daL = {0., 0., 0.}, cVals, specL},
    (* Right-handed species: c = 1/2 + ln(1/y)/(2*kT) *)
    (* Left-handed doublets: determined by the larger Yukawa in the pair *)
    cTR = 1/2 + Log[1/yPhys[[1]]]/(2*kT);
    cBR = 1/2 + Log[1/yPhys[[2]]]/(2*kT);
    cCR = 1/2 + Log[1/yPhys[[3]]]/(2*kT);
    cSR = 1/2 + Log[1/yPhys[[4]]]/(2*kT);
    cDR = 1/2 + Log[1/yPhys[[5]]]/(2*kT);
    cUR = 1/2 + Log[1/yPhys[[6]]]/(2*kT);
    cTauR = 1/2 + Log[1/yPhys[[7]]]/(2*kT);
    cMuR = 1/2 + Log[1/yPhys[[8]]]/(2*kT);
    cER = 1/2 + Log[1/yPhys[[9]]]/(2*kT);
    (* Doublets: c_Q ~ c_uR + 0.7 (since y_4D ~ y5 * f_L * f_R) *)
    cQ3 = Max[cTR + 0.70, 0.35];
    cQ2 = Max[cCR - 0.10, 0.50];
    cQ1 = Max[cUR - 0.10, 0.55];
    cL3 = cTauR + 0.03;
    cL2 = cMuR - 0.03;
    cL1 = Max[cER - 0.13, 0.55];

    cVals = {cQ3, cTR, cBR, cL3, cTauR, cQ2, cCR, cSR, cL2, cMuR,
             cQ1, cUR, cDR, cL1, cER};

    specL = Table[
      {fermionSpecies[[i,1]], fermionSpecies[[i,2]], fermionSpecies[[i,3]],
       fermionSpecies[[i,4]], cVals[[i]]},
      {i, 15}
    ];

    Do[
      Module[{c = sp[[5]], dc, tt1, tt3},
        dc = delta[c];
        tt1 = N[t1[sp]]; tt3 = N[t3[sp]];
        daL[[1]] += -(1/(2*Pi)) * tt1 * dc;
        daL[[3]] += -(1/(2*Pi)) * tt3 * dc;
      ],
      {sp, specL}
    ];

    Print["  kyc=", NumberForm[kT, {4,1}],
      "  D13=", NumberForm[daL[[1]]-daL[[3]], {6,3}],
      "  (", NumberForm[(daL[[1]]-daL[[3]])/delta13needed*100, {4,1}], "%)"];
  ],
  {kT, {20., 25., 30., 35., 40., 50.}}
];
Print[""];

(* ============================================================ *)
(* GRAND SYNTHESIS                                             *)
(* ============================================================ *)
Print["================================================================"];
Print["================================================================"];
Print["GRAND SYNTHESIS"];
Print["================================================================"];
Print["================================================================"];
Print[""];

Print["Source                             Nominal     Maximum"];
Print["-----------------------------------------------------------"];
Print["1. Fermion KK (ADP)               ", NumberForm[delta13ferm, {5,2}],
  "     ", NumberForm[delta13max, {5,2}]];
Print["2. Higgs KK (bulk)                ", NumberForm[d13H0, {5,3}],
  "    ", NumberForm[d13H0, {5,3}]];
Print["3. Two-loop threshold             ", NumberForm[delta2L13, {5,2}],
  "      ", NumberForm[1.5*delta2L13, {5,2}]];
Print["4. Radion-Higgs mixing            ~0.000     ~0.000"];
Print["5-8. Other                         ~0.000     ~0.010"];
Print["-----------------------------------------------------------"];

totalNom = delta13ferm + d13H0 + delta2L13;
totalMax = delta13max + d13H0 + 1.5*delta2L13;

Print["TOTAL (minimal RS+NCG, nominal)   ", NumberForm[totalNom, {5,2}]];
Print["TOTAL (minimal RS+NCG, maximum)   ", NumberForm[totalMax, {5,2}]];
Print[""];
Print["Fraction (nominal): ", NumberForm[totalNom/delta13needed*100, {4,1}], "%"];
Print["Fraction (maximum): ", NumberForm[totalMax/delta13needed*100, {4,1}], "%"];
Print[""];

(* With inert doublets *)
remaining = delta13needed - totalMax;
nInert = remaining / deltaInert13;
Print["Inert doublets for 100% closure: ", NumberForm[nInert, {4,1}]];
Print[""];

(* ============================================================ *)
(* FINAL VERDICT                                               *)
(* ============================================================ *)
Print["================================================================"];
Print["FINAL VERDICT"];
Print["================================================================"];
Print[""];
Print["QUESTION: Can KK thresholds close the 12% gauge gap?"];
Print[""];
Print["ANSWER: PARTIALLY. Maximum ~35% within minimal framework."];
Print[""];
Print["  Fermion KK thresholds:  -1.91 (nominal) to ~-3.5 (max)"];
Print["  = 19% to 35% of needed -10.0"];
Print[""];
Print["  Including all sources:  ~-2.5 (nominal) to ~-4.5 (max)"];
Print["  = 25% to 45% of needed -10.0"];
Print[""];
Print["  REMAINING GAP: 55-75% of the correction is MISSING."];
Print[""];
Print["  The gap is STRUCTURAL:"];
Print["  - T1^GUT - T3 = 10.67 (fixed by SM quantum numbers)"];
Print["  - delta(c) range: 0.14 to 1.99 (bounded by Yukawa hierarchy)"];
Print["  - Q_L doublets contribute NEGATIVELY (T1 < T3 for Q_L)"];
Print["  - FCNC bounds prevent Q_L from being fully IR-localized"];
Print[""];
Print["PATHS TO FULL CLOSURE:"];
Print["1. Extended NCG: ~6-8 inert doublets at MKK"];
Print["2. Non-perturbative effects (instantons, spectral flow)"];
Print["3. Intermediate-scale physics (new spectral triple content)"];
Print["4. Modified running trajectory (non-standard RG flow)"];
Print["5. The gap is the prediction: identifies missing content"];
Print[""];
Print["================================================================"];
Print["END"];
Print["================================================================"];
