(*
  Analytic Torsion via Analytic Continuation — v2
  ================================================
  Fixed: no underscores in variable names (Mathematica pattern clash)

  O(0) on CP^2: zeta(s) = Sum_{m=2}^inf m^3 / (m^2 - 1)^s
  O(2) on CP^2: zeta(s) = Sum_{m=3}^inf (m^3-m) / (m^2 - 4)^s

  Pochhammer expansion gives analytic continuation via Hurwitz zeta.
*)

Print["ANALYTIC TORSION VIA ANALYTIC CONTINUATION (v2)"];
Print["================================================="];
Print[""];

(* ============================================================ *)
(* O(0) on CP^2                                                  *)
(* ============================================================ *)

(* k=0: 2 * HZ'(-3, 2) *)
c0 = 2*N[Derivative[1, 0][HurwitzZeta][-3, 2], 30];

(* k=1: HZ(-1, 2) *)
c1 = N[HurwitzZeta[-1, 2], 30];

(* k=2: pole subtraction gives -1/4 + gamma/2 *)
c2 = N[-1/4 + EulerGamma/2, 30];

(* k>=3: convergent sum of HZ(2k-3, 2)/k *)
$MaxExtraPrecision = 200;
c3 = Sum[N[HurwitzZeta[2*k - 3, 2]/k, 30], {k, 3, 200}];

Print["=== O(0) on CP^2 ==="];
Print["k=0: 2*HZ'(-3,2)  = ", c0];
Print["k=1: HZ(-1,2)     = ", c1];
Print["k=2: -1/4+gamma/2 = ", c2];
Print["k>=3: sum          = ", c3];
Print[""];

zpO0 = c0 + c1 + c2 + c3;
Print["zeta'(0; box0, O(0)) on CP^2 = ", zpO0];
Print[""];

(* ============================================================ *)
(* O(2) on CP^2                                                  *)
(* ============================================================ *)

(* k=0: 2*(HZ'(-3,3) - HZ'(-1,3)) *)
e0 = 2*N[Derivative[1, 0][HurwitzZeta][-3, 3] - Derivative[1, 0][HurwitzZeta][-1, 3], 30];

(* k=1: 4*HZ(-1,3) + 4*(3/2 - gamma) *)
e1a = 4*N[HurwitzZeta[-1, 3], 30];
e1b = 4*N[3/2 - EulerGamma, 30];
e1 = e1a + e1b;

(* k=2: (-8 + 8*gamma) + (-8*HZ(3,3)) *)
e2pole = N[-8 + 8*EulerGamma, 30];
e2reg = -8*N[HurwitzZeta[3, 3], 30];
e2 = e2pole + e2reg;

(* k>=3: convergent sum of 4^k/k * (HZ(2k-3,3) - HZ(2k-1,3)) *)
e3 = Sum[N[4^k/k*(HurwitzZeta[2*k - 3, 3] - HurwitzZeta[2*k - 1, 3]), 30], {k, 3, 100}];

Print["=== O(2) on CP^2 ==="];
Print["k=0: 2*(HZ'(-3,3)-HZ'(-1,3)) = ", e0];
Print["k=1a: 4*HZ(-1,3)              = ", e1a];
Print["k=1b: 4*(3/2-gamma)            = ", e1b];
Print["k=1 total:                      = ", e1];
Print["k=2 pole: -8+8*gamma           = ", e2pole];
Print["k=2 reg: -8*HZ(3,3)            = ", e2reg];
Print["k=2 total:                      = ", e2];
Print["k>=3: sum                       = ", e3];
Print[""];

zpO2 = e0 + e1 + e2 + e3;
Print["zeta'(0; box0, O(2)) on CP^2 = ", zpO2];
Print[""];

(* ============================================================ *)
(* DIFFERENCE AND TORSION RATIO                                   *)
(* ============================================================ *)

diff = zpO0 - zpO2;
Print["==================================================="];
Print["RESULTS"];
Print["==================================================="];
Print[""];
Print["zeta'(0; O(0)) = ", N[zpO0, 20]];
Print["zeta'(0; O(2)) = ", N[zpO2, 20]];
Print["Difference      = ", N[diff, 20]];
Print[""];

(* Blowup formula for dP5: *)
(* base contribution = -(zeta'(O(0)) - zeta'(O(2))) *)
(* exceptional contribution = log(2) (from E4 only) *)
baseDiff = -diff;
excDiff = Log[2];
total = baseDiff + excDiff;
target = Log[3]/Sqrt[2];

Print["=== Torsion ratio on dP5 (box0 approximation) ==="];
Print[""];
Print["Base (CP^2):          ", N[baseDiff, 20]];
Print["Exceptional (log 2):  ", N[excDiff, 20]];
Print["Total:                ", N[total, 20]];
Print[""];
Print["Target ln(3)/sqrt(2): ", N[target, 20]];
Print["Ratio total/target:   ", N[total/target, 20]];
Print["Difference:           ", N[total - target, 20]];
Print[""];

(* ============================================================ *)
(* CROSS-CHECK: Known values                                      *)
(* ============================================================ *)

(* On CP^2 with trivial bundle O, the analytic torsion is known: *)
(* log T(CP^2, O) = zeta'(0)/something — check against literature *)
(* HurwitzZeta[-3, 2] = -B4(2)/4 where B4 is 4th Bernoulli poly *)
Print["=== Cross-checks ==="];
Print["HurwitzZeta[-3, 2] = ", N[HurwitzZeta[-3, 2], 20]];
Print["HurwitzZeta[-1, 2] = ", N[HurwitzZeta[-1, 2], 20]];
Print["HurwitzZeta[-3, 3] = ", N[HurwitzZeta[-3, 3], 20]];
Print["HurwitzZeta[-1, 3] = ", N[HurwitzZeta[-1, 3], 20]];
Print["HurwitzZeta[3, 2]  = ", N[HurwitzZeta[3, 2], 20]];
Print["HurwitzZeta[3, 3]  = ", N[HurwitzZeta[3, 3], 20]];
Print[""];

(* Bernoulli polynomial values *)
Print["B4(2) = ", BernoulliB[4, 2]];
Print["-B4(2)/4 should = HZ(-3,2): ", N[-BernoulliB[4, 2]/4, 20]];
Print["B2(2) = ", BernoulliB[2, 2]];
Print["-B2(2)/2 should = HZ(-1,2): ", N[-BernoulliB[2, 2]/2, 20]];
