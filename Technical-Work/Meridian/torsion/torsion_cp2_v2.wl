(*
  Analytic Torsion on CP^2 — Proper Zeta Regularization
  =====================================================

  Spectrum of box_0 on O(0): lambda_a = a(a+2), mult = (a+1)^3, a >= 1
  Spectrum of box_0 on O(2): lambda_b = b(b+4), mult = (b+1)(b+2)(b+3), b >= 1

  We need zeta'(0) for both, computed via analytic continuation
  using the heat kernel method.
*)

Print["ANALYTIC TORSION ON CP^2 VIA HEAT KERNEL"];
Print["=========================================="];
Print[""];

(* ============================================================ *)
(* 1. Heat kernel computation *)
(* ============================================================ *)

(* Heat trace for O(0): K0(t) = Sum_{a=1}^inf (a+1)^3 * Exp[-a(a+2)*t] *)
(* Heat trace for O(2): K2(t) = Sum_{b=1}^inf (b+1)(b+2)(b+3) * Exp[-b(b+4)*t] *)

(* We compute these as explicit functions of t, then use the *)
(* Mellin transform for the zeta regularization. *)

(* For the DIFFERENCE of zeta functions, many divergences cancel: *)
(* Delta_zeta(s) = zeta(s; O(0)) - zeta(s; O(2)) *)
(* = (1/Gamma(s)) * Integral_0^inf t^{s-1} * [K0(t) - K2(t)] dt *)

(* The heat kernel difference K0(t) - K2(t) has better convergence *)
(* properties than either kernel individually. *)

(* Compute heat trace difference numerically for various t *)
Print["Heat trace difference K0(t) - K2(t):"];
Print[""];

heatDiff[t_?NumericQ] := Module[{k0, k2, maxA = 200},
  k0 = Sum[(a + 1)^3*Exp[-a*(a + 2)*t], {a, 1, maxA}];
  k2 = Sum[(b + 1)*(b + 2)*(b + 3)*Exp[-b*(b + 4)*t], {b, 1, maxA}];
  k0 - k2
];

(* Also compute individual traces *)
heatK0[t_?NumericQ] := Sum[(a + 1)^3*Exp[-a*(a + 2)*t], {a, 1, 200}];
heatK2[t_?NumericQ] := Sum[(b + 1)*(b + 2)*(b + 3)*Exp[-b*(b + 4)*t], {b, 1, 200}];

Do[
  t = 10.0^(-k);
  Print["  t = ", t, ":  K0 = ", N[heatK0[t], 10],
        "  K2 = ", N[heatK2[t], 10], "  diff = ", N[heatDiff[t], 10]];
, {k, -2, 3}];

Print[""];

(* ============================================================ *)
(* 2. Seeley-deWitt coefficients from small-t expansion *)
(* ============================================================ *)

(* For t -> 0+, the heat trace has asymptotic expansion: *)
(* K(t) ~ a_0/t^2 + a_1/t + a_2 + a_3*t + ... *)

(* For the DIFFERENCE: *)
(* K0(t) - K2(t) ~ (a_0^{(0)}-a_0^{(2)})/t^2 + (a_1^{(0)}-a_1^{(2)})/t + ... *)

(* We can extract these from the small-t behavior: *)
Print["Seeley-deWitt coefficients from asymptotic expansion:"];
Print[""];

(* At very small t, the asymptotic expansion dominates *)
(* K(t) = a_0/t^2 + a_1/t + a_2 + O(t) *)
(* So: t^2*K(t) -> a_0 as t -> 0+ *)
(*     t*(K(t) - a_0/t^2) -> a_1 as t -> 0+ *)
(*     K(t) - a_0/t^2 - a_1/t -> a_2 as t -> 0+ *)

(* For O(0) on CP^2: *)
(* Using the known heat kernel coefficients for the scalar Laplacian *)
(* on a Kahler-Einstein surface with Ric = lambda*omega: *)
(* a_0 = (Vol/4pi^2) * rk = Vol/(4*pi^2) *)
(* For CP^2 with Fubini-Study: Vol = pi^2/2 (total volume of CP^2) *)
(* So a_0 = (pi^2/2)/(4*pi^2) = 1/8 *)

(* Actually, the heat kernel coefficients for box_0 on O(k) on CP^n are: *)
(* a_0 = dim(sections) * Vol/(4*pi)^n ... *)
(* This depends on the normalization of the metric. *)

(* Let me extract them numerically from the heat trace. *)
(* K0(t) for small t should go as a_0/t^2 + a_1/t + a_2 + ... *)

(* Use Richardson extrapolation for the coefficients *)
t0 = 0.001;
k0vals = Table[{t0*2^(-j), heatK0[t0*2^(-j)]}, {j, 0, 8}];
k2vals = Table[{t0*2^(-j), heatK2[t0*2^(-j)]}, {j, 0, 8}];

(* Extract a_0: a_0 = lim t^2 * K(t) as t -> 0 *)
a0_O0 = k0vals[[-1, 1]]^2*k0vals[[-1, 2]];
a0_O2 = k2vals[[-1, 1]]^2*k2vals[[-1, 2]];
Print["a_0(O(0)) ~ ", N[a0_O0, 10]];
Print["a_0(O(2)) ~ ", N[a0_O2, 10]];
Print["Expected: both should be Vol/(4*pi^2) * (something)"];
Print[""];

(* ============================================================ *)
(* 3. Zeta'(0) via Mellin transform with analytic continuation *)
(* ============================================================ *)

(* The spectral zeta function: *)
(* zeta(s) = (1/Gamma(s)) * Int_0^inf t^{s-1} * (K(t) - dim_ker) dt *)

(* For the REGULARIZED value at s = 0: *)
(* zeta'(0) = Int_0^1 [K(t) - dim_ker - a_0/t^2 - a_1/t] dt/t *)
(*          + Int_1^inf [K(t) - dim_ker] dt/t *)
(*          + a_0/2 + a_1 - gamma*a_2 *)
(*          (up to conventions) *)

(* Actually, the standard formula is: *)
(* zeta'(0) = FP_{s=0} int_0^inf t^{s-1} (K(t) - dim_ker) dt / Gamma(s) *)

(* Let me use a different, more stable approach. *)
(* For eigenvalues lambda_j with multiplicities d_j: *)
(* zeta(s) = Sum_j d_j * lambda_j^{-s} *)
(* zeta'(0) = -Sum_j d_j * log(lambda_j) * lambda_j^0 = -Sum_j d_j * log(lambda_j) *)
(* WAIT: zeta'(0) = d/ds Sum_j d_j lambda_j^{-s} |_{s=0} *)
(*                = -Sum_j d_j log(lambda_j) lambda_j^{-s} |_{s=0} *)
(*                = -Sum_j d_j log(lambda_j) *)
(* This DIVERGES! The regularization is needed. *)

(* The correct formula using zeta regularization: *)
(* log det'(Delta) = -zeta'(0) *)
(* and zeta'(0) is defined by analytic continuation, not direct summation. *)

(* For the DIFFERENCE: *)
(* zeta'(0; O(0)) - zeta'(0; O(2)) = -[Sum d_j^{(0)} log lambda_j^{(0)} - Sum d_j^{(2)} log lambda_j^{(2)}] *)
(* This still diverges term by term, but the DIFFERENCE might converge *)
(* if the asymptotic behaviors match. *)

(* Let's check: *)
(* O(0): d_a = (a+1)^3, lambda_a = a(a+2), for a >= 1 *)
(* O(2): d_b = (b+1)(b+2)(b+3), lambda_b = b(b+4), for b >= 1 *)

(* Asymptotically as n -> inf: *)
(* O(0): d_n ~ n^3, lambda_n ~ n^2, d_n*log(lambda_n) ~ 2*n^3*log(n) *)
(* O(2): d_n ~ n^3, lambda_n ~ n^2, d_n*log(lambda_n) ~ 2*n^3*log(n) *)
(* The leading terms MATCH, so the difference converges! *)

Print[""];
Print["==================================================="];
Print["REGULARIZED ZETA DIFFERENCE BY PARTIAL SUMS"];
Print["==================================================="];
Print[""];

(* Compute partial sums of the difference *)
(* S(N) = Sum_{n=1}^N [d_n^{(0)} log lambda_n^{(0)} - d_n^{(2)} log lambda_n^{(2)}] *)

Print["Partial sums of zeta'(0; O(0)) - zeta'(0; O(2)):"];
Print["(This is -[log det'(box; O(0)) - log det'(box; O(2))])"];
Print[""];

partialSum[nMax_] := Sum[
  (n + 1)^3*Log[n*(n + 2)] - (n + 1)*(n + 2)*(n + 3)*Log[n*(n + 4)]
, {n, 1, nMax}];

Do[
  ps = N[partialSum[nMax], 20];
  Print["  N = ", nMax, ": S(N) = ", ps];
, {nMax, {10, 50, 100, 500, 1000, 5000, 10000}}];

Print[""];

(* If the sum converges, the limit gives zeta'(0; O(0)) - zeta'(0; O(2)) *)
(* The TORSION difference is -(zeta' difference) *)

(* Let's also try acceleration using Euler-Maclaurin *)
(* Or compute more carefully by splitting log(n(n+k)) = log(n) + log(n+k) *)

Print[""];
Print["==================================================="];
Print["TERM-BY-TERM ANALYSIS"];
Print["==================================================="];
Print[""];

(* Difference of n-th terms: *)
(* Delta_n = (n+1)^3 * log(n(n+2)) - (n+1)(n+2)(n+3) * log(n(n+4)) *)
(* = (n+1)^3 * [log n + log(n+2)] - (n+1)(n+2)(n+3) * [log n + log(n+4)] *)
(* = [(n+1)^3 - (n+1)(n+2)(n+3)] * log n *)
(*   + (n+1)^3 * log(n+2) - (n+1)(n+2)(n+3) * log(n+4) *)

(* (n+1)^3 - (n+1)(n+2)(n+3) = (n+1)[(n+1)^2 - (n+2)(n+3)] *)
(* = (n+1)[n^2+2n+1 - n^2-5n-6] = (n+1)(-3n-5) *)

Print["Coefficient of log(n): (n+1)^3 - (n+1)(n+2)(n+3) = -(n+1)(3n+5)"];
Print["This grows as -3n^2, so individual pieces diverge."];
Print["But the TOTAL difference might still converge by cancellation."];
Print[""];

(* Let me use a more sophisticated regularization. *)
(* Split the sum into a convergent part and a divergent part *)
(* that can be evaluated using Hurwitz zeta. *)

(* Write: *)
(* Sum d_n * log(lambda_n) = Sum d_n * [log(lambda_n) - 2*log(n)] + 2*Sum d_n*log(n) *)
(* The first sum converges (since lambda_n ~ n^2). *)
(* The second sum needs zeta regularization: *)
(* Sum d_n * log(n) = -d/ds Sum d_n * n^{-s} |_{s=0} *)

Print["Decomposing the sum:"];
Print[""];

(* Convergent part: *)
convPartO0[nMax_] := Sum[(n+1)^3*(Log[n*(n+2)] - 2*Log[n+1]), {n, 1, nMax}];
convPartO2[nMax_] := Sum[(n+1)*(n+2)*(n+3)*(Log[n*(n+4)] - 2*Log[n+1+1]), {n, 1, nMax}];

(* Wait, lambda_n ~ (n+1)^2 for O(0), so log(lambda_n) - 2*log(n+1) -> log(1-1/(n+1)^2) -> 0 *)
(* Actually: lambda_a = a(a+2) = (a+1)^2 - 1, so log(lambda_a) = 2*log(a+1) + log(1-1/(a+1)^2) *)

(* For O(0): *)
(* Sum = Sum (a+1)^3 * [2*log(a+1) + log(1-1/(a+1)^2)] *)
(*     = 2 * Sum (a+1)^3 * log(a+1) + Sum (a+1)^3 * log(1-1/(a+1)^2) *)

(* With m = a+1 >= 2: *)
(* = 2 * Sum_{m=2}^inf m^3 * log(m) + Sum_{m=2}^inf m^3 * log(1-1/m^2) *)

(* The first sum needs zeta reg: -2 * d/ds Sum m^{-s+3} |_{s=0} = -2 * zeta'(-3) *)
(* [but shifted: Sum_{m=2} = zeta_H(-3, 2) ... this is the Hurwitz version] *)

(* For O(2): lambda_b = b(b+4) = (b+2)^2 - 4 *)
(* log(lambda_b) = 2*log(b+2) + log(1 - 4/(b+2)^2) *)

(* Sum = Sum (b+1)(b+2)(b+3) * [2*log(b+2) + log(1 - 4/(b+2)^2)] *)
(* With m = b+2 >= 3: b+1 = m-1, b+3 = m+1 *)
(* = Sum_{m=3}^inf (m-1)*m*(m+1) * [2*log(m) + log(1-4/m^2)] *)
(* = 2*Sum m(m^2-1)*log(m) + Sum m(m^2-1)*log(1-4/m^2) *)

(* The convergent parts: *)
conv0[nMax_] := Sum[m^3*Log[1 - 1/m^2], {m, 2, nMax}];
conv2[nMax_] := Sum[(m-1)*m*(m+1)*Log[1 - 4/m^2], {m, 3, nMax}];

Print["Convergent parts (N = 10000):"];
c0 = N[conv0[10000], 20];
c2 = N[conv2[10000], 20];
Print["  C_0 = Sum m^3 * log(1-1/m^2) = ", c0];
Print["  C_2 = Sum m(m^2-1) * log(1-4/m^2) = ", c2];
Print["  Difference C_0 - C_2 = ", N[c0 - c2, 15]];
Print[""];

(* The divergent parts need Hurwitz zeta: *)
(* D_0 = 2 * Sum_{m=2}^inf m^3 * log(m) = -2 * HurwitzZeta'(-3, 2) *)
(* D_2 = 2 * Sum_{m=3}^inf m(m^2-1) * log(m) *)
(*     = 2 * [Sum m^3*log(m) - Sum m*log(m)] from m=3 *)
(*     = -2 * [HurwitzZeta'(-3, 3) - HurwitzZeta'(-1, 3)] *)

(* Wolfram can compute these! *)
hz3d2 = N[Derivative[1, 0][HurwitzZeta][-3, 2], 25];
hz1d2 = N[Derivative[1, 0][HurwitzZeta][-1, 2], 25];
hz3d3 = N[Derivative[1, 0][HurwitzZeta][-3, 3], 25];
hz1d3 = N[Derivative[1, 0][HurwitzZeta][-1, 3], 25];

Print["Hurwitz zeta derivatives:"];
Print["  zeta'(-3, 2) = ", hz3d2];
Print["  zeta'(-1, 2) = ", hz1d2];
Print["  zeta'(-3, 3) = ", hz3d3];
Print["  zeta'(-1, 3) = ", hz1d3];
Print[""];

(* D_0 = -2 * zeta'(-3, 2) *)
D0 = -2*hz3d2;
Print["D_0 = -2*zeta'(-3,2) = ", N[D0, 20]];

(* D_2: Sum_{m=3}^inf m(m^2-1)*log(m) *)
(* = Sum m^3*log(m) - Sum m*log(m) from m=3 *)
(* = -zeta'(-3, 3) + zeta'(-1, 3) *)
D2 = -2*(hz3d3 - hz1d3);
Print["D_2 = -2*(zeta'(-3,3) - zeta'(-1,3)) = ", N[D2, 20]];
Print[""];

(* Also need the m=2 term for D_0 that's not in D_2: *)
(* D_0 counts m >= 2, D_2 counts m >= 3 *)
(* D_0 = D_0(m>=2), D_2 = D_2(m>=3) *)
(* But D_2 has the factor m(m^2-1) not m^3 *)

(* Let me be more careful. *)
(* zeta'(0; O(0)) = Sum_{a=1}^inf (a+1)^3 * log((a+1)^2 - 1) *)
(*                = Sum_{m=2}^inf m^3 * log(m^2 - 1) *)
(*                = Sum m^3 * [2*log(m) + log(1-1/m^2)] *)
(*                = 2 * Sum m^3 log(m) + Sum m^3 log(1-1/m^2)   [m >= 2] *)
(*                = -2 * zeta_H'(-3, 2) + C_0 *)

(* zeta'(0; O(2)) = Sum_{b=1}^inf (b+1)(b+2)(b+3) * log(b(b+4)) *)
(* With m = b+2 >= 3: *)
(* = Sum_{m=3}^inf (m-1)*m*(m+1) * log((m-2)(m+2)) *)
(* = Sum (m^3-m) * log(m^2-4) *)
(* = Sum (m^3-m) * [2*log(m) + log(1-4/m^2)] *)
(* = 2*Sum (m^3-m)*log(m) + Sum (m^3-m)*log(1-4/m^2)  [m >= 3] *)
(* = -2*[zeta_H'(-3,3) - zeta_H'(-1,3)] + C_2 *)

zprime0_O0 = -2*hz3d2 + c0;
zprime0_O2 = -2*(hz3d3 - hz1d3) + c2;

Print["==================================================="];
Print["RESULTS"];
Print["==================================================="];
Print[""];
Print["zeta'(0; box, O(0)) on CP^2 = ", N[zprime0_O0, 20]];
Print["zeta'(0; box, O(2)) on CP^2 = ", N[zprime0_O2, 20]];
Print[""];

zetaDiff = zprime0_O0 - zprime0_O2;
Print["zeta'(0; O(0)) - zeta'(0; O(2)) = ", N[zetaDiff, 20]];
Print[""];

(* Torsion difference on CP^2: *)
(* log T(CP^2, O(0)) - log T(CP^2, O(2)) = -(zeta'(O(0)) - zeta'(O(2))) *)
(* (sign depends on convention for analytic torsion) *)

torsionDiffCP2 = -zetaDiff;
Print["log T(CP^2, O(0)) - log T(CP^2, O(2)) = ", N[torsionDiffCP2, 15]];
Print[""];

(* Exceptional divisor contribution from the blowup: *)
(* Only E4 contributes (L_Y|_{E4} = O(2)) *)
excContrib = Log[2]; (* = log T(E4, O(0)) - log T(E4, O(2)) = 0 - (-log(2)) = log(2) *)

(* Total torsion difference on dP_5: *)
total = torsionDiffCP2 + excContrib;

Print["==================================================="];
Print["TORSION DIFFERENCE ON dP_5"];
Print["==================================================="];
Print[""];
Print["CP^2 base contribution: ", N[torsionDiffCP2, 15]];
Print["Exceptional (E4 only):  ", N[excContrib, 15]];
Print["Total tau_0 - tau_Y:    ", N[total, 15]];
Print[""];

target = Log[3]/Sqrt[2];
Print["Target ln(3)/sqrt(2) = ", N[target, 15]];
Print["Ratio total/target =   ", N[total/target, 15]];
Print["Difference =            ", N[total - target, 15]];
Print[""];

(* Also output some special numbers for comparison *)
Print["--- Special numbers ---"];
Print["log(2) = ", N[Log[2], 15]];
Print["log(3) = ", N[Log[3], 15]];
Print["1/sqrt(2) = ", N[1/Sqrt[2], 15]];
Print["zeta'(-1) = ", N[Derivative[1][Zeta][-1], 15]];
Print["zeta'(-3) = ", N[Derivative[1][Zeta][-3], 15]];
Print["log(2*Pi) = ", N[Log[2*Pi], 15]];
Print["EulerGamma = ", N[EulerGamma, 15]];
