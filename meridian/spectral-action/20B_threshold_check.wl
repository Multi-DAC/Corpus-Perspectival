(* Quick check: reproduce the -1.91 from 20B *)

(* ADP threshold *)
delta[c_] := Module[{nu = Abs[c + 1/2], x1},
  x1 = N[BesselJZero[nu, 1]];
  N[PolyGamma[nu + 1] - PolyGamma[1] + Log[x1/Pi]]
];

(* The original 20B used (5/3) normalization *)
dynkin53[spec_, 1] := (5/3) * spec[[4]]^2 * spec[[2]] * spec[[3]];
dynkin53[spec_, 2] := If[spec[[3]] == 2, spec[[2]] * (1/2), 0];
dynkin53[spec_, 3] := If[spec[[2]] == 3, spec[[3]] * (1/2), 0];

(* My code used (3/5) normalization *)
dynkin35[spec_, 1] := (3/5) * spec[[4]]^2 * spec[[2]] * spec[[3]];
dynkin35[spec_, 2] := If[spec[[3]] == 2, spec[[2]] * (1/2), 0];
dynkin35[spec_, 3] := If[spec[[2]] == 3, spec[[3]] * (1/2), 0];

fermionSpecies = {
  {"Q3",   3, 2, 1/6, 0.40},
  {"t3R",  3, 1, 2/3, -0.30},
  {"b3R",  3, 1, -1/3, 0.43},
  {"L3",   1, 2, -1/2, 0.52},
  {"tau3R",1, 1, -1, 0.49},
  {"Q2",   3, 2, 1/6, 0.55},
  {"c2R",  3, 1, 2/3, 0.55},
  {"s2R",  3, 1, -1/3, 0.62},
  {"L2",   1, 2, -1/2, 0.58},
  {"mu2R", 1, 1, -1, 0.61},
  {"Q1",   3, 2, 1/6, 0.63},
  {"u1R",  3, 1, 2/3, 0.68},
  {"d1R",  3, 1, -1/3, 0.65},
  {"L1",   1, 2, -1/2, 0.62},
  {"e1R",  1, 1, -1, 0.75}
};

Print["=== With (5/3) normalization (original 20B) ==="];
da53 = {0., 0., 0.};
Do[
  Module[{c = spec[[5]], dc, t1, t2, t3},
    dc = delta[c];
    t1 = N[dynkin53[spec, 1]];
    t2 = N[dynkin53[spec, 2]];
    t3 = N[dynkin53[spec, 3]];
    da53[[1]] += -(1/(2*Pi)) * t1 * dc;
    da53[[2]] += -(1/(2*Pi)) * t2 * dc;
    da53[[3]] += -(1/(2*Pi)) * t3 * dc;
    Print[spec[[1]], "\tT1=", NumberForm[t1, {4,3}],
      "\tT3=", NumberForm[t3, {4,3}],
      "\t(T1-T3)*delta=", NumberForm[(t1-t3)*dc, {6,3}]];
  ],
  {spec, fermionSpecies}
];
Print[""];
Print["Delta alpha_1^{-1} = ", da53[[1]]];
Print["Delta alpha_2^{-1} = ", da53[[2]]];
Print["Delta alpha_3^{-1} = ", da53[[3]]];
Print["Delta(alpha_1^{-1} - alpha_3^{-1}) = ", da53[[1]] - da53[[3]]];
Print[""];

Print["=== With (3/5) normalization ==="];
da35 = {0., 0., 0.};
Do[
  Module[{c = spec[[5]], dc, t1, t2, t3},
    dc = delta[c];
    t1 = N[dynkin35[spec, 1]];
    t2 = N[dynkin35[spec, 2]];
    t3 = N[dynkin35[spec, 3]];
    da35[[1]] += -(1/(2*Pi)) * t1 * dc;
    da35[[2]] += -(1/(2*Pi)) * t2 * dc;
    da35[[3]] += -(1/(2*Pi)) * t3 * dc;
  ],
  {spec, fermionSpecies}
];
Print["Delta(alpha_1^{-1} - alpha_3^{-1}) = ", da35[[1]] - da35[[3]]];
Print[""];

(* Check: what T_1 values does each give for Q_L? *)
Print["Q_L (3,2,1/6):"];
Print["  T1 with (5/3): ", N[(5/3) * (1/6)^2 * 3 * 2]];
Print["  T1 with (3/5): ", N[(3/5) * (1/6)^2 * 3 * 2]];
Print[""];
Print["e_R (1,1,-1):"];
Print["  T1 with (5/3): ", N[(5/3) * (-1)^2 * 1 * 1]];
Print["  T1 with (3/5): ", N[(3/5) * (-1)^2 * 1 * 1]];
Print[""];

(* Check: total T1 - T3 with each normalization *)
Print["Sum(T1-T3) with (5/3): ",
  Total[N[dynkin53[#, 1] - dynkin53[#, 3]] & /@ fermionSpecies]];
Print["Sum(T1-T3) with (3/5): ",
  Total[N[dynkin35[#, 1] - dynkin35[#, 3]] & /@ fermionSpecies]];
Print[""];

(* The correct normalization for the threshold formula:
   Delta alpha_i^{-1} = -(1/(2pi)) * sum_f T_i(f) * delta(c_f)
   where T_i(f) is the Dynkin index S_i(R) of representation R under group i.

   For SU(N): S(fund) = 1/2
   For U(1)_Y: S = Y^2 per degree of freedom

   The question is whether T_1 uses the GUT-normalized alpha_1 or the
   non-normalized alpha_Y.

   In the standard convention:
   alpha_1^{-1} = (5/3) * alpha_Y^{-1}

   The threshold correction to alpha_1^{-1} (GUT normalized) is:
   Delta alpha_1^{-1} = (5/3) * Delta alpha_Y^{-1}
   = (5/3) * [-(1/(2pi)) * sum_f Y_f^2 * d_c * d_w * delta(c_f)]
   = -(1/(2pi)) * sum_f [(5/3) * Y_f^2 * d_c * d_w] * delta(c_f)
   = -(1/(2pi)) * sum_f T_1^{GUT}(f) * delta(c_f)

   where T_1^{GUT} = (5/3)*Y^2*d_c*d_w

   So the CORRECT normalization for alpha_1^{-1} in GUT convention IS (5/3).
*)

Print["CONCLUSION: The (5/3) normalization is correct for GUT-normalized alpha_1^{-1}."];
Print["The (3/5) normalization gives alpha_Y^{-1}, not alpha_1^{-1}."];
Print[""];

(* But ALSO check: does Sum(T1-T3) vanish with (5/3)? *)
(* The one-loop beta coefficients: b_1 = sum (2/3)*T_1(f) per Weyl fermion *)
(* b_1 = (2/3) * Sum T_1^{GUT}(f) *)
(* SM: b_1 = 41/10 for one generation *)
(* Sum T_1^{GUT} = (3/2) * b_1 = (3/2) * 41/10 = 123/20 per generation *)

Print["Per-generation beta check:"];
Print["  b_1 = 41/10 = ", N[41/10]];
Print["  (2/3)*Sum(T1_GUT) = ",
  N[(2/3)*Total[dynkin53[#, 1] & /@ fermionSpecies[[1;;5]]]]];
(* Hmm, that should match b_1 per generation if these are Weyl fermions *)

(* Actually b_i = (2/3)*sum_f T_i(f) for Weyl fermions only *)
(* In our list, each entry is a Weyl fermion *)
(* b_1(one gen) = (2/3)*sum_{f in gen} T_1(f) *)
gen1T1 = Total[N[dynkin53[#, 1]] & /@ fermionSpecies[[1;;5]]];
Print["  Sum T1 (gen 3): ", gen1T1];
Print["  (2/3)*Sum: ", (2/3)*gen1T1];
Print["  Expected b_1 per gen: 41/(10*3) = ", N[41/30]];
Print[""];

(* Similarly for T3 *)
gen1T3 = Total[N[dynkin53[#, 3]] & /@ fermionSpecies[[1;;5]]];
Print["  Sum T3 (gen 3): ", gen1T3];
Print["  (2/3)*Sum: ", (2/3)*gen1T3];
Print["  Expected b_3 per gen: -7/3 = ... no, b_3 = -7 includes gauge+scalar"];
Print["  Fermion contribution to b_3: (2/3)*Sum T3 = ", (2/3)*gen1T3];
Print["  SM fermion b_3 = 4/3 per generation (3 gen gives 4)"];
Print["  But we have gauge (-11) and Higgs (scalar) contributions too"];
Print["  Just fermions: b_3^ferm = (2/3)*sum T3 per Dirac = (4/3)*sum T3 per Weyl"];
Print[""];
Print["Wait - each Weyl fermion contributes (2/3)*T(R) to the beta function."];
Print["Our Q_L is a single Weyl doublet with T3 = 3*(1/2) = 3/2? No..."];
Print["Q_L: (3,2,1/6) means SU(3) triplet, SU(2) doublet."];
Print["T3(Q_L) = T(3)*d_2 = (1/2)*2 = 1 per Q_L Weyl fermion"];
Print["t3R: (3,1,2/3) means SU(3) triplet, SU(2) singlet."];
Print["T3(t3R) = T(3)*d_2 = (1/2)*1 = 1/2 per Weyl fermion"];
Print[""];

(* Let me verify the formula against the known SM beta function *)
(* b_3(SM) = -11 + (4/3)*n_g where n_g = 3 generations *)
(* b_3(SM) = -11 + 4 = -7 *)
(* The fermion part: (4/3)*3 = 4 *)
(* Per generation, fermion contribution to b_3 = 4/3 *)
(* Using our formula: (2/3)*sum T3(f) per generation *)
(* We need: (2/3)*sum T3 = 4/3 -> sum T3 = 2 *)
Print["  Verify: sum T3 per gen should be 2"];
Print["  Q_L: T3 = ", N[dynkin53[fermionSpecies[[1]], 3]]];
Print["  t_R: T3 = ", N[dynkin53[fermionSpecies[[2]], 3]]];
Print["  b_R: T3 = ", N[dynkin53[fermionSpecies[[3]], 3]]];
Print["  L_L: T3 = ", N[dynkin53[fermionSpecies[[4]], 3]]];
Print["  tau_R: T3 = ", N[dynkin53[fermionSpecies[[5]], 3]]];
Print["  Sum: ", gen1T3];
Print[""];

(* Now verify T1 *)
(* b_1(SM) = 41/10 for 3 generations + Higgs *)
(* b_1(SM, fermions only, 3 gen) = 4/3 * sum_per_gen T1 *)
(* Per gen: Q_L(T1) + u_R(T1) + d_R(T1) + L_L(T1) + e_R(T1) *)
(* = (5/3)*(1/6)^2*6 + (5/3)*(2/3)^2*3 + (5/3)*(1/3)^2*3 + (5/3)*(1/2)^2*2 + (5/3)*1*1 *)
gen3T1 = Total[N[dynkin53[#, 1]] & /@ fermionSpecies[[1;;5]]];
Print["  T1 per gen (with 5/3): ", gen3T1];
Print["  (2/3)*T1 per gen = ", (2/3)*gen3T1];
Print["  b_1(fermion, per gen) should be 4/3 * (10/3) ... let me compute"];
Print["  From PDG: b_1(SM) = 41/10, includes Higgs (1/10)"];
Print["  Fermion: 41/10 - 1/10 = 40/10 = 4"];
Print["  Per gen: 4/3"];
Print["  (2/3)*sum T1 per gen = ", (2/3)*gen3T1];
Print[""];

(* So the total T1 for 3 generations is 3*gen3T1 *)
totalT153 = Total[N[dynkin53[#, 1]] & /@ fermionSpecies];
totalT353 = Total[N[dynkin53[#, 3]] & /@ fermionSpecies];
Print["Total T1 (3 gen, 5/3 norm): ", totalT153];
Print["Total T3 (3 gen): ", totalT353];
Print["T1 - T3: ", totalT153 - totalT353];
Print[""];

(* The REAL check: is Sum(T1-T3) supposed to be zero? *)
(* For anomaly cancellation: Tr(Y) = 0 per generation *)
(* But T1 = (5/3)*Y^2*d, T3 = (1/2)*d_SU2 for SU(3) reps *)
(* These are NOT the same quantity as the anomaly coefficient *)
(* T1 - T3 does NOT have to vanish *)
Print["NOTE: T1 - T3 is NOT required to vanish by anomaly cancellation."];
Print["Anomaly cancellation requires Tr(Y) = 0, Tr(Y^3) = 0, etc."];
Print["T1 = (5/3)*Y^2*d_c*d_w and T3 = T(SU3)*d_w are different quantities."];
Print[""];
Print["b_1 - b_3 (SM, fermion) = ", (2/3)*(totalT153 - totalT353)];
Print["This should equal b_1^ferm - b_3^ferm = 4 - 4 = 0? No..."];
Print["b_1(SM) = 41/10, b_3(SM) = -7"];
Print["b_1 - b_3 = 41/10 + 7 = 111/10 = 11.1"];
Print["Fermion part: b_1^f - b_3^f = 4 - 4 = 0"];
Print[""];
Print["Wait: b_1^ferm = (2/3)*sum T1 for all 3 gens = ", (2/3)*totalT153];
Print["b_3^ferm = (2/3)*sum T3 for all 3 gens = ", (2/3)*totalT353];
Print["b_1^ferm - b_3^ferm = ", (2/3)*(totalT153 - totalT353)];
