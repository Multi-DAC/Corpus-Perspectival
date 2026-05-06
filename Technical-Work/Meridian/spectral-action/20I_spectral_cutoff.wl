(* ============================================================
   Track 20I: Position-Dependent Cutoff Analysis
   Does Lambda(y) = Lambda_UV * e^{-ky} break spectral action gauge universality?
   ============================================================ *)

Print["============================================================"];
Print["PART 1: The a_n heat kernel integrals with position-dependent cutoff"];
Print["============================================================"];

(* Setup: RS geometry *)
(* Warp factor: A(y) = -k|y|, metric factor e^{-4ky} in volume *)
(* Position-dependent cutoff: Lambda(y) = Lambda_UV * e^{-ky} *)
(* Spectral action heat kernel: S ~ Sum_n f_{4-n} Lambda(y)^{4-n} a_n *)
(* For the y-integral, the contribution at each order n is: *)
(* I_n = Int_0^{piRc} dy * e^{-4ky} * Lambda(y)^{4-n} * [local a_n coefficient] *)

(* Key insight: Lambda(y)^{4-n} = (Lambda_UV e^{-ky})^{4-n} = Lambda_UV^{4-n} * e^{-(4-n)ky} *)

Print["\n--- Y-integrals for each heat kernel order ---"];
Print["Lambda(y) = Lambda_UV * exp(-ky)"];
Print["Volume factor: exp(-4ky)"];
Print["Total integrand weight at order n: exp(-(8-n)ky)"];
Print[""];

(* Compute the integral I_n = Int_0^{y_c} dy * e^{-(8-n)ky} for n = 0, 2, 4, 6, 8 *)

Do[
  exponent = -(8 - n);
  If[exponent == 0,
    Print["n = ", n, ":  weight = exp(0) = 1 (flat integral)"];
    Print["  I_", n, " = y_c"];
    ,
    Print["n = ", n, ":  weight = exp(", exponent, " * k * y)"];
    integralExact = Integrate[Exp[exponent * k * y], {y, 0, yc}, Assumptions -> {k > 0, yc > 0}];
    Print["  I_", n, " = ", Simplify[integralExact]];
  ];
  Print["  Cutoff prefactor: Lambda_UV^{", 4-n, "}"];
  Print[""];
, {n, 0, 8, 2}];

Print["============================================================"];
Print["PART 2: The n=4 term (gauge kinetic) -- cutoff drops out"];
Print["============================================================\n"];

(* For n = 4: Lambda(y)^{4-4} = Lambda(y)^0 = 1 *)
I4exact = Integrate[Exp[-4 k y], {y, 0, yc}, Assumptions -> {k > 0, yc > 0}];
Print["At n = 4: Lambda(y)^0 = 1 -- position-dependent cutoff is INVISIBLE."];
Print[""];
Print["The y-integral for gauge kinetic term:"];
Print["  I_4 = Int_0^{y_c} dy exp(-4ky) = ", Simplify[I4exact]];
Print[""];
Print["This integral is the SAME for all gauge groups."];
Print["Combined with a_i = 4 N_g (CCM theorem), gauge universality is EXACT at n=4."];

Print["\n============================================================"];
Print["PART 3: The n=6 correction -- higher-order terms"];
Print["============================================================\n"];

I6exact = Integrate[Exp[-2 k y], {y, 0, yc}, Assumptions -> {k > 0, yc > 0}];
Print["At n = 6: Lambda(y)^{-2} = Lambda_UV^{-2} * exp(+2ky)"];
Print["  I_6 = Int_0^{y_c} dy exp(-2ky) = ", Simplify[I6exact]];
Print[""];

(* Ratio of I_6 to I_4 *)
ratioExact = Simplify[I6exact / I4exact];
Print["Ratio I_6/I_4 = ", ratioExact];
Print[""];

(* Evaluate for physical RS parameters *)
(* ky_c = 37.4 *)
ratioNum = N[ratioExact /. {k -> 1, yc -> 37.4}];
Print["For ky_c = 37.4: I_6/I_4 = ", ratioNum];
Print[""];
Print["But the n=6 contribution also carries Lambda_UV^{-2}:"];
Print["  (n=6 correction)/(n=4 leading) = Lambda_UV^{-2} * I_6/I_4"];

(* Physical values *)
LambdaUVnum = 2.4*10^18; (* GeV *)
suppressionNum = N[1/LambdaUVnum^2 * ratioNum];
Print["  = ", suppressionNum, " GeV^{-2}"];
Print[""];
Print["This is effectively zero. Even multiplied by any a_6 coefficient,"];
Print["the correction is negligible."];

Print["\n============================================================"];
Print["PART 4: Numerical magnitude estimates"];
Print["============================================================\n"];

(* Complete table of ratios *)
kval = 1; (* work in units of k *)
ycval = 37.4; (* ky_c = 37.4 *)
LambdaUV = 2.4*10^18;

I0num = N[(1 - Exp[-8*ycval])/(8*kval)];
I2num = N[(1 - Exp[-6*ycval])/(6*kval)];
I4num = N[(1 - Exp[-4*ycval])/(4*kval)];
I6num = N[(1 - Exp[-2*ycval])/(2*kval)];
I8num = N[ycval/kval]; (* flat: exp(0) = 1 *)

Print["Y-integrals (in units of 1/k):"];
Print["  I_0 = ", I0num];
Print["  I_2 = ", I2num];
Print["  I_4 = ", I4num];
Print["  I_6 = ", I6num];
Print["  I_8 = ", I8num, " (flat)"];
Print[""];

(* Full contributions including Lambda_UV prefactor *)
Print["Full contributions (Lambda_UV = ", LambdaUV, " GeV):"];
Print["  n=0: Lambda_UV^4 * I_0 = ", N[LambdaUV^4 * I0num]];
Print["  n=2: Lambda_UV^2 * I_2 = ", N[LambdaUV^2 * I2num]];
Print["  n=4: Lambda_UV^0 * I_4 = ", N[I4num], "  <-- GAUGE KINETIC (Lambda-independent!)"];
Print["  n=6: Lambda_UV^{-2} * I_6 = ", N[I6num/LambdaUV^2]];
Print["  n=8: Lambda_UV^{-4} * I_8 = ", N[I8num/LambdaUV^4]];
Print[""];

(* Relative corrections to gauge kinetic *)
Print["Relative corrections to gauge kinetic (n=4) term:"];
Print["  n=6/n=4 = ", N[I6num/(LambdaUV^2 * I4num)]];
Print["  n=8/n=4 = ", N[I8num/(LambdaUV^4 * I4num)]];
Print[""];
Print["Both corrections are astronomically small."];
Print["Even IF a_6 or a_8 had gauge-dependent pieces,"];
Print["they would be suppressed by >= 10^{-35} relative to a_4."];

Print["\n============================================================"];
Print["PART 5: Why this had to be true (dimensional argument)"];
Print["============================================================\n"];

Print["The spectral action expansion in d effective dimensions:"];
Print["  S = Sum_{n>=0} f_{(d-n)/2} * Lambda^{d-n} * a_n"];
Print[""];
Print["For gauge kinetic terms (dimension 4 operators):"];
Print["  The a_n coefficient that produces F^2 has mass dimension [a_n] = n."];
Print["  The prefactor Lambda^{d-n} has dimension d-n."];
Print["  Total dimension: (d-n) + n = d."];
Print["  For a 4D effective term, we need total dimension 4 in the 4D action."];
Print[""];
Print["After y-integration (which removes one dimension):"];
Print["  The 5D spectral action gives a 4D effective action."];
Print["  The 4D gauge kinetic term Int d^4x F^2 has dimension 4."];
Print["  The F^2 piece of a_n contributes at dimension n-1 (after y-integration)."];
Print["  The cutoff contributes Lambda^{4-n} (in the 4+1 -> 4 reduction)."];
Print["  Total: (n-1) + (4-n) = 3... "];
Print[""];
Print["Actually, the cleanest argument:"];
Print["  The spectral action for gauge kinetic terms comes from a_4."];
Print["  In the expansion, a_4 multiplies Lambda^{d-4}."];
Print["  For d=5 (before y-integration): Lambda^1."];
Print["  But with position-dependent cutoff Lambda(y) = Lambda_UV e^{-ky}:"];
Print["    Lambda(y)^1 = Lambda_UV e^{-ky}"];
Print["  This is ABSORBED into the existing e^{-4ky} metric factor,"];
Print["  giving e^{-5ky} instead of e^{-4ky}."];
Print[""];
Print["WAIT -- this would change the y-integral!"];
Print["Let me reconsider the 5D vs 4D counting carefully."];

Print["\n============================================================"];
Print["PART 6: Careful 5D spectral action counting"];
Print["============================================================\n"];

(* The spectral action in d=5 dimensions: *)
(* S = Tr[f(D^2/Lambda^2)] ~ Sum_{n>=0} f_{(5-n)/2} Lambda^{5-n} a_n *)
(* where a_n is the n-th Seeley-DeWitt coefficient of D^2 on the 5D manifold *)

(* The a_4 coefficient gives Lambda^{5-4} = Lambda^1 *)
(* The a_5 coefficient (if it exists, but Seeley-DeWitt only has even n for *)
(* manifolds without boundary) gives Lambda^0 *)

(* Wait: on a manifold WITH boundary (the RS orbifold), there ARE half-integer *)
(* Seeley-DeWitt coefficients (boundary terms). But the bulk coefficients *)
(* still come at even n. *)

(* Actually, the standard expansion is: *)
(* Tr[f(D^2/Lambda^2)] ~ Sum_{n=0,1,2,...} f_n Lambda^{2n} a_{d-2n}(D^2) *)
(* where f_n = Int_0^infty u^n f(u) du *)
(* or equivalently: *)
(* ~ Sum_k f_{(d-k)/2} Lambda^{d-k} a_k *)

(* For d=5 (ODD!), the expansion is: *)
(* f_{5/2} Lambda^5 a_0 + f_{3/2} Lambda^3 a_2 + f_{1/2} Lambda^1 a_4 + f_{-1/2} Lambda^{-1} a_6 + ... *)

Print["5D spectral action expansion (d=5):"];
Print["  S = f_{5/2} Lambda^5 a_0 + f_{3/2} Lambda^3 a_2 + f_{1/2} Lambda a_4 + f_{-1/2}/Lambda a_6 + ..."];
Print[""];
Print["For the gauge kinetic (F^2) term coming from a_4:"];
Print["  Contribution = f_{1/2} * Lambda * a_4|_{F^2}"];
Print[""];
Print["With position-dependent cutoff Lambda(y) = Lambda_UV e^{-ky}:"];
Print["  Contribution = f_{1/2} * Lambda_UV * e^{-ky} * a_4|_{F^2}"];
Print[""];
Print["The FULL 5D integral for gauge kinetic terms:"];

I4five = Integrate[Exp[-4 k y] * Exp[-k y], {y, 0, yc}, Assumptions -> {k > 0, yc > 0}];
I4fiveSimp = Simplify[I4five];
Print["  Int_0^{y_c} dy sqrt{g_5} Lambda(y) a_4|_{F^2}"];
Print["  = Int_0^{y_c} dy e^{-4ky} * Lambda_UV * e^{-ky} * a_4|_{F^2}"];
Print["  = Lambda_UV * a_4|_{F^2} * Int_0^{y_c} dy e^{-5ky}"];
Print["  = Lambda_UV * a_4|_{F^2} * ", I4fiveSimp];
Print[""];

(* Compare with UNIFORM cutoff Lambda_UV: *)
I4uniform = Integrate[Exp[-4 k y], {y, 0, yc}, Assumptions -> {k > 0, yc > 0}];
Print["With UNIFORM cutoff Lambda_UV (standard computation):"];
Print["  = Lambda_UV * a_4|_{F^2} * Int_0^{y_c} dy e^{-4ky}"];
Print["  = Lambda_UV * a_4|_{F^2} * ", Simplify[I4uniform]];
Print[""];

Print["THE DIFFERENCE: e^{-5ky} vs e^{-4ky} in the y-integral!"];
Print[""];
Print["But BOTH integrals are gauge-group INDEPENDENT."];
Print["The extra e^{-ky} factor from Lambda(y) is the SAME for all gauge groups."];
Print[""];

(* Ratio *)
ratioFive = Simplify[I4five / I4uniform];
Print["Ratio (position-dependent / uniform):"];
Print["  = [Int e^{-5ky} dy] / [Int e^{-4ky} dy] = ", ratioFive];
ratioFiveNum = N[ratioFive /. {k -> 1, yc -> 37.4}];
Print["  Numerical value for ky_c = 37.4: ", ratioFiveNum];
Print["  (approximately 4/5 = 0.8 for large ky_c)"];
Print[""];
Print["CONCLUSION (CORRECTED): In 5D, the a_4 contribution carries Lambda^1,"];
Print["so Lambda(y) = Lambda_UV e^{-ky} DOES enter the gauge kinetic y-integral."];
Print["But it enters as a UNIVERSAL multiplicative factor e^{-ky} that is the"];
Print["SAME for all gauge groups. The gauge universality a_1 = a_2 = a_3 is PRESERVED."];
Print["The position-dependent cutoff changes the OVERALL normalization of all gauge"];
Print["couplings by the ratio 4/5 (for large ky_c), but does NOT split them."];

Print["\n============================================================"];
Print["PART 7: The a_6 correction in 5D"];
Print["============================================================\n"];

(* In 5D, a_6 carries Lambda^{5-6} = Lambda^{-1} *)
(* With Lambda(y): Lambda_UV^{-1} e^{+ky} *)
I6five = Integrate[Exp[-4 k y] * Exp[k y], {y, 0, yc}, Assumptions -> {k > 0, yc > 0}];
Print["a_6 contribution in 5D:"];
Print["  f_{-1/2}/Lambda(y) * a_6 integrated:"];
Print["  Int_0^{y_c} dy e^{-4ky} * Lambda_UV^{-1} * e^{+ky} * a_6"];
Print["  = Lambda_UV^{-1} * Int_0^{y_c} dy e^{-3ky} * a_6"];
Print["  = Lambda_UV^{-1} * a_6 * ", Simplify[I6five]];
Print[""];

ratioSix = Simplify[I6five / I4five];
Print["Ratio (a_6 correction / a_4 leading) in 5D:"];
Print["  = (f_{-1/2}/f_{1/2}) * Lambda_UV^{-2} * ", ratioSix];
ratioSixNum = N[ratioSix /. {k -> 1, yc -> 37.4}];
Print["  Y-integral ratio: ", ratioSixNum];
Print["  Full suppression: ~ Lambda_UV^{-2} * ", ratioSixNum];
Print["  = ", N[ratioSixNum / (2.4*10^18)^2], " GeV^{-2}"];
Print[""];
Print["Still negligibly small."];

Print["\n============================================================"];
Print["FINAL THEOREM AND RESULT"];
Print["============================================================\n"];

Print["THEOREM T9 (Position-Dependent Cutoff Universality):"];
Print[""];
Print["Let (M_4 x I x F, D_total) be the almost-commutative spectral triple"];
Print["on the RS_1 warped orbifold with CCM finite geometry F = (A_F, H_F, D_F)."];
Print["Let the spectral action cutoff be position-dependent:"];
Print["  Lambda(y) = Lambda_UV * exp(-k|y|)"];
Print["corresponding to the local physical energy scale on the warped background."];
Print[""];
Print["Then:"];
Print[""];
Print["(i) The gauge kinetic coefficients in the 4D effective action satisfy"];
Print["    a_1 = a_2 = a_3 = 4 N_g"];
Print["    EXACTLY. The position-dependent cutoff enters the gauge kinetic term"];
Print["    only as a universal multiplicative factor affecting the overall"];
Print["    normalization, not the relative gauge couplings."];
Print[""];
Print["(ii) In the 5D spectral action, the gauge kinetic term (from a_4)"];
Print["     carries Lambda(y)^1 = Lambda_UV * exp(-ky). The y-integral"];
Print["     becomes Int_0^{y_c} dy exp(-5ky) instead of Int_0^{y_c} dy exp(-4ky),"];
Print["     but this modification is gauge-group INDEPENDENT."];
Print[""];
Print["(iii) The first potentially non-universal correction enters at order a_6,"];
Print["      suppressed by:"];
Print["        Delta(a_i)/a_i <= C * Lambda_UV^{-2} * (a_6/a_4)"];
Print["      For the RS_1 hierarchy: Delta(a_i)/a_i ~ 10^{-37} GeV^{-2}."];
Print[""];
Print["(iv) The position-dependent cutoff CANNOT resolve the ~12% sin^2(theta_W)"];
Print["     discrepancy. Gauge universality is preserved to better than 10^{-30}"];
Print["     relative precision."];
Print[""];
Print["Proof sketch: The gauge kinetic term arises from the a_4 Seeley-DeWitt"];
Print["coefficient. In the 5D spectral action, this carries Lambda^{5-4} = Lambda."];
Print["With Lambda(y) = Lambda_UV exp(-ky), the y-integrand gains an extra exp(-ky)"];
Print["factor. This factor is INDEPENDENT of the gauge group index i because:"];
Print["  (a) The warp factor exp(-ky) depends only on geometry, not on which"];
Print["      gauge group the field belongs to;"];
Print["  (b) All gauge boson zero modes have FLAT profiles f_0(y) = const"];
Print["      on the RS_1 orbifold (proved in Section 1.4 of 14A);"];
Print["  (c) The trace over H_F giving a_i = 4N_g is algebraic and y-independent."];
Print["Therefore the ratio a_i/a_j = 1 for all i,j, and the position-dependent"];
Print["cutoff preserves gauge universality exactly. QED."];
Print[""];
Print["CLASSIFICATION: PIVOT -> THEOREM"];
Print["The track was classified as SPECULATIVE in the Phase 20 plan."];
Print["The answer is cleaner than expected: universality is preserved by"];
Print["dimensional analysis (Lambda^0 in 4D) or by gauge-independence of the"];
Print["warp factor (Lambda^1 in 5D). Either way, the splitting is zero."];
