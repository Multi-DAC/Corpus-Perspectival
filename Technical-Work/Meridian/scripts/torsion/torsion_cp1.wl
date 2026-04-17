(*
  Threshold splitting from exceptional divisors on dP5
  =====================================================

  KEY RESULT: box_1 spectra on CP^2 are IDENTICAL for O(0) and O(2)
  due to (a,b) <-> (b,a) symmetry of SU(3) Casimirs.
  Therefore the ENTIRE threshold splitting comes from exceptional divisors.

  On each E_i = CP^1:
  - O|_{E_i} = O(0)
  - L_Y|_{E_1} = O(1), L_Y|_{E_2} = O(1), L_Y|_{E_3} = O(1)
  - L_Y|_{E_4} = O(2), L_Y|_{E_5} = O(0)

  E_4 contribution: zeta1'(O) - zeta1'(O(2)) on CP^1
    By Serre: zeta1'(O) = zeta0'(O(-2)), zeta1'(O(2)) = zeta0'(O(0))
    O(-2) and O(0) have same non-zero spectrum (j even >= 2) => ZERO

  E_5 contribution: trivially zero (same bundle)

  TOTAL: Delta_3 - Delta_2 = 3 * [zeta1'(O) - zeta1'(O(1))] on CP^1
       = 3 * [zeta0'(O(-2)) - zeta0'(O(-1))] on CP^1

  Spectra on CP^1 = SU(2)/U(1):
  O(-2): j = 2, 4, 6, ..., eigenvalue = j(j+2)/4, mult = j+1
         With n = j/2: lambda = n(n+1), mult = 2n+1, n >= 1
  O(-1): j = 1, 3, 5, ..., eigenvalue = j(j+2)/4, mult = j+1
         With j = 2n+1: lambda = (2n+1)(2n+3)/4, mult = 2n+2, n >= 0
*)

Print["THRESHOLD SPLITTING FROM EXCEPTIONAL DIVISORS"];
Print["==============================================="];
Print[""];

(* ============================================================ *)
(* Spectral zeta for O(-2) on CP^1 *)
(* lambda_n = n(n+1), d_n = 2n+1, n = 1, 2, 3, ... *)
(* This is the STANDARD S^2 spectrum minus the zero mode *)
(* ============================================================ *)

(* Known result for S^2: *)
(* zeta'(0; S^2) = 4*zeta_R'(-1) - 1/2 + 2*log(2*Pi) *)
(* But let me compute directly *)

Print["=== Spectral zeta for O(-2) on CP^1 ==="];
Print["lambda_n = n(n+1), d_n = 2n+1, n >= 1"];
Print[""];

(* Partial fraction: n(n+1) = n^2 + n *)
(* zeta(s) = Sum_{n=1}^inf (2n+1) / [n(n+1)]^s *)
(* = Sum_{n=1}^inf (2n+1) / [n^s * (n+1)^s] *)

(* At s = 0: zeta(0) = Sum_{n=1}^inf (2n+1) = divergent *)
(* Need analytic continuation *)

(* Use the Euler-Maclaurin or Hurwitz expansion *)
(* n(n+1) = (n+1/2)^2 - 1/4 *)
(* So (2n+1) / [n(n+1)]^s = (2n+1) / [(n+1/2)^2 - 1/4]^s *)

(* Let u = n + 1/2, so n = u - 1/2, 2n+1 = 2u *)
(* zeta(s) = Sum_{u=3/2, 5/2, 7/2, ...} 2u / [u^2 - 1/4]^s *)

(* Expand [u^2 - 1/4]^{-s} = u^{-2s} [1 - 1/(4u^2)]^{-s} *)
(* = u^{-2s} Sum_k Pochhammer(s,k)/k! * (4u^2)^{-k} *)
(* = Sum_k Pochhammer(s,k) / (k! * 4^k) * u^{-2s-2k} *)

(* So zeta(s) = 2 * Sum_k Pochhammer(s,k)/(k!*4^k) * *)
(*   Sum_{u=3/2,5/2,...} u^{1-2s-2k} *)

(* Sum_{u=3/2,5/2,...} u^{-alpha} = Sum_{m=1}^inf (m+1/2)^{-alpha} *)
(* = Sum_{m=0}^inf (m+3/2)^{-alpha} = HurwitzZeta(alpha, 3/2) *)

(* Hmm, actually: u = n + 1/2 with n = 1, 2, 3, ... *)
(* So u = 3/2, 5/2, 7/2, ... *)
(* Sum_u u^{-alpha} = Sum_{m=0}^inf (m + 3/2)^{-alpha} = HurwitzZeta(alpha, 3/2) *)

(* Therefore: *)
(* zeta(s) = 2 * Sum_k Pochhammer(s,k)/(k!*4^k) * HZ(2s+2k-1, 3/2) *)

(* Compute directly for now *)

(* DIRECT NUMERICAL COMPUTATION *)
(* Use large partial sums with Richardson extrapolation *)

$MaxExtraPrecision = 200;

(* Method: compute zeta(s) numerically for s near 0, extract zeta'(0) *)
(* Better: use the known closed-form for S^2 zeta *)

(* KNOWN RESULT (Osgood, Phillips, Sarnak; Vardi 1988): *)
(* For S^2 (radius 1), the spectral zeta of the scalar Laplacian is: *)
(* zeta_{S^2}(s) = Sum_{l=1}^inf (2l+1) * [l(l+1)]^{-s} *)
(* = 2 * [HurwitzZeta(2s-1, 1) - HurwitzZeta(2s, 1)] *)
(* Wait, that's not right. Let me derive it. *)

(* zeta(s) = Sum_{l=1}^inf (2l+1) / [l(l+1)]^s *)
(* Use partial fractions: 2l+1 = (l+1) + l *)
(* = Sum_{l=1}^inf l / [l(l+1)]^s + Sum_{l=1}^inf (l+1) / [l(l+1)]^s *)
(* = Sum_{l=1}^inf l^{1-s} (l+1)^{-s} + Sum_{l=1}^inf l^{-s} (l+1)^{1-s} *)

(* Second sum with m = l+1: *)
(* = Sum_{m=2}^inf (m-1)^{-s} m^{1-s} *)
(* = Sum_{l=2}^inf (l-1)^{-s} l^{1-s} *)
(* = Sum_{l=1}^inf (l-1)^{-s} l^{1-s} - 0 (l=1: 0^{-s} diverges...) *)

(* Actually 0^{-s} is problematic. Let me keep the original form. *)

(* SIMPLEST APPROACH: just compute numerically *)
(* zeta(s) and zeta'(s) using direct summation with analytic regularization *)

(* Actually, use the Hurwitz representation: *)
(* l(l+1) = (l + 1/2)^2 - 1/4 *)
(* With m = l + 1/2: *)
(* zeta(s) = Sum_{m=3/2, 5/2, ...} 2m / (m^2 - 1/4)^s *)

(* For the DIFFERENCE zeta_O(-2) - zeta_O(-1), I need: *)

(* O(-2): Sum_{n=1}^inf (2n+1) / [n(n+1)]^s *)
(*      = Sum_{m=3/2,5/2,...} 2m / (m^2-1/4)^s *)

(* O(-1): Sum_{j=1,3,5,...} (j+1) / [j(j+2)/4]^s *)
(*      = 4^s Sum_{n=0}^inf (2n+2) / [(2n+1)(2n+3)]^s *)
(*      = 4^s * 2 Sum_{n=0}^inf (n+1) / [(2n+1)(2n+3)]^s *)

(* For O(-1): j = 2n+1, eigenvalue = (2n+1)(2n+3)/4, mult = 2n+2 *)
(* With u = n + 1: lambda = (2u-1)(2u+1)/4 = (4u^2-1)/4 = u^2 - 1/4 *)
(* mult = 2u, u >= 1 *)

(* So zeta_{O(-1)}(s) = Sum_{u=1}^inf 2u / [(u^2-1/4)/1]^s ... *)
(* Wait: eigenvalue = (2n+1)(2n+3)/4 with n >= 0 *)
(* u = n+1: eigenvalue = (2u-1)(2u+1)/4 = u^2 - 1/4 *)
(* mult = 2u *)
(* So: zeta_{O(-1)}(s) = Sum_{u=1}^inf 2u / (u^2 - 1/4)^s *)

(* And zeta_{O(-2)}(s) = Sum_{m=3/2,5/2,...} 2m / (m^2 - 1/4)^s *)
(* = Sum_{p=1}^inf 2(p + 1/2) / ((p+1/2)^2 - 1/4)^s *)
(* = Sum_{p=1}^inf (2p+1) / (p^2 + p)^s *)
(* = Sum_{p=1}^inf (2p+1) / [p(p+1)]^s *)
(* This is the same as before. OK. *)

(* So: *)
(* zeta_{O(-2)}(s) = Sum_{p=1}^inf 2(p+1/2) / [(p+1/2)^2 - 1/4]^s *)
(* zeta_{O(-1)}(s) = Sum_{u=1}^inf 2u / [u^2 - 1/4]^s *)

(* DIFFERENCE: *)
(* D(s) = zeta_{O(-2)}(s) - zeta_{O(-1)}(s) *)
(* = Sum_{m half-integer >= 3/2} 2m/(m^2-1/4)^s - Sum_{m integer >= 1} 2m/(m^2-1/4)^s *)

(* The first sum is over m = 3/2, 5/2, 7/2, ... *)
(* The second sum is over m = 1, 2, 3, ... *)

(* If I define F(s) = Sum_{m=1/2, 1, 3/2, 2, 5/2, ...} 2m/(m^2-1/4)^s *)
(* = Sum over all half-integers m >= 1/2 *)
(* Then: *)
(* F(s) = [m=1/2 term] + [half-integer terms >= 3/2] + [integer terms >= 1] *)
(* = 2*(1/2)/(1/4-1/4)^s + zeta_{O(-2)}(s) + zeta_{O(-1)}(s) *)
(* But m=1/2: 2*(1/2)/((1/2)^2-1/4)^s = 1/0^s which is divergent. *)
(* So m = 1/2 is a special point where m^2 - 1/4 = 0. *)

(* Hmm, this means the eigenvalue (u^2-1/4) at u=1/2 is 0, *)
(* which is a ZERO MODE. For O(-1) on CP^1: *)
(* u=1 gives eigenvalue 1^2 - 1/4 = 3/4. No zero mode. Good. *)

(* For O(-2) on CP^1: smallest eigenvalue at p=1: *)
(* (1+1/2)^2 - 1/4 = 9/4 - 1/4 = 2 = 1*2. Correct. *)

(* OK let me just compute everything numerically in Wolfram *)

(* Direct computation of zeta(s) and zeta'(s) *)

zetaOm2[s_] := Sum[(2 n + 1)/(n (n + 1))^s, {n, 1, Infinity}];
zetaOm1[s_] := Sum[(2 n + 2)/((2 n + 1) (2 n + 3)/4)^s, {n, 0, Infinity}];

(* These might not have closed forms. Use NSum with analytic continuation. *)

(* Actually, let me decompose differently. *)
(* (2n+1)/[n(n+1)]^s = [1/n + 1/(n+1)] * [n(n+1)]^{1-s} ... no *)

(* DIRECT: use the identity *)
(* Sum_{n=1}^inf (2n+1)/[n(n+1)]^s *)
(* = Sum_{n=1}^inf [(n+1) + n] / [n^s (n+1)^s] *)
(* = Sum_{n=1}^inf (n+1)^{1-s} n^{-s} + Sum_{n=1}^inf n^{1-s} (n+1)^{-s} *)
(* = Sum_{n=1}^inf n^{-s}(n+1)^{1-s} + Sum_{n=1}^inf n^{1-s}(n+1)^{-s} *)
(* With m = n+1 in first sum: *)
(* = Sum_{m=2}^inf (m-1)^{-s} m^{1-s} + Sum_{n=1}^inf n^{1-s}(n+1)^{-s} *)

(* These are "Hurwitz-lerch" type sums. Let me use a different approach. *)

(* APPROACH: Compute numerically with high precision *)
(* Use partial sums + Euler-Maclaurin *)

Print["Computing zeta'(0) numerically..."];
Print[""];

(* For O(-2): eigenvalues n(n+1), mult 2n+1, n >= 1 *)
(* zeta(s) = Sum_{n=1}^N (2n+1)/[n(n+1)]^s + tail *)

(* At s = 0: zeta(0) = Sum (2n+1) formally -> need regularization *)
(* zeta(0) is the "number of eigenvalues" regularized *)

(* Use the Hurwitz zeta approach: *)
(* (2n+1)/[n(n+1)]^s = (2n+1) * Sum_k (-1)^k Binomial(-s,k) * n^{-2s-k} ... *)
(* This is getting circular. *)

(* NUMERICAL APPROACH WITH WOLFRAM *)

(* Method: compute zeta(epsilon) for small epsilon using NSum *)
(* then estimate zeta(0) and zeta'(0) *)

Print["=== Method: symbolic partial fraction + Hurwitz ==="];

(* Key identity: *)
(* 1/[n(n+1)]^s = 1/[n^{2s}] * [1 + 1/n]^{-s} *)
(* Expand [1+1/n]^{-s} in powers of 1/n: *)
(* = Sum_k Binomial(-s, k) n^{-k} *)
(* = Sum_k (-1)^k Binomial(s+k-1, k) n^{-k} *)

(* So (2n+1)/[n(n+1)]^s = (2n+1) Sum_k (-1)^k C(s+k-1,k) n^{-2s-k} *)
(* = Sum_k (-1)^k C(s+k-1,k) [2 n^{1-2s-k} + n^{-2s-k}] *)

(* Sum over n>=1: *)
(* = Sum_k (-1)^k C(s+k-1,k) [2 HZ(2s+k-1,1) + HZ(2s+k,1)] *)
(* where HZ(alpha,1) = RiemannZeta(alpha) for alpha != 1 *)

(* At s = 0: *)
(* k=0: C(-1,0)=1: 2*RZ(-1) + RZ(0) = 2*(-1/12) + (-1/2) = -1/6 - 1/2 = -2/3 *)

zetaS2at0 = 2*(-1/12) + (-1/2);
Print["zeta_{O(-2)}(0) = ", zetaS2at0, " = -2/3"];

(* zeta'(0): differentiate w.r.t. s *)
(* d/ds [(-1)^k C(s+k-1,k) (2 HZ(2s+k-1,1) + HZ(2s+k,1))] at s=0 *)

(* k=0: d/ds [2 RZ(2s-1) + RZ(2s)] at s=0 *)
(* = 2*2*RZ'(-1) + 2*RZ'(0) = 4*RZ'(-1) + 2*RZ'(0) *)

(* k=1: d/ds [-s * (2 RZ(2s) + RZ(2s+1))] at s=0 *)
(* C(s,1) = s, d/ds[...] = product rule *)
(* = -(2 RZ(0) + RZ(1)) + ... but RZ(1) diverges! *)

(* RZ(2s+1) has a pole at s=0: RZ(2s+1) = 1/(2s) + gamma_E/2 + ... *)
(* -s * RZ(2s+1) = -s * [1/(2s) + gamma/2 + ...] = -1/2 - s*gamma/2 + ... *)
(* d/ds[-s * RZ(2s+1)]|_{s=0} = -gamma/2 *)

(* Also: -s * 2 * RZ(2s) = -2s * (-1/2 + RZ'(0)*2s + ...) [since RZ(0) = -1/2] *)
(* Actually RZ(2s) near s=0: RZ(0) = -1/2, RZ'(0)*2 comes from chain rule *)
(* d/ds[-s * 2 RZ(2s)]|_{s=0} = -2 * RZ(0) + 0 = -2*(-1/2) = 1 *)

(* k=1 total: 1 - EulerGamma/2 ... let me be more careful *)

(* k=1: term is (-1)^1 * C(s,1) * [2 HZ(2s,1) + HZ(2s+1,1)] *)
(* = -s * [2 RZ(2s) + RZ(2s+1)] *)
(* d/ds at s=0: *)
(* = -[2 RZ(0) + RZ(1)] - s*[4 RZ'(0) + 2 RZ'(1)]|_{s=0} *)
(* But this is formal; RZ(1) = infinity. Need to handle the pole. *)

(* RZ(2s+1) = 1/(2s) - gamma_E + O(s) [Laurent expansion around s=0] *)
(* Wait: RZ(s) near s=1: RZ(s) = 1/(s-1) + gamma + O(s-1) *)
(* So RZ(2s+1) near s=0: 2s+1 = 1+2s, RZ(1+2s) = 1/(2s) + gamma + O(s) *)

(* k=1 term: -s * [2 RZ(2s) + 1/(2s) + gamma + O(s)] *)
(* = -s * 2 RZ(2s) - 1/2 - s*gamma + O(s^2) *)

(* At s=0: the k=1 contribution to zeta(0) includes -1/2 - 0 = -1/2 from the pole *)
(* But we already computed zeta(0) = -2/3 using only k=0. *)
(* So the k=1 contribution to zeta(0) must be incorporated. *)

(* I think the issue is that the binomial expansion is only valid for large n, *)
(* and we need the FULL contribution. Let me not try to compute this analytically *)
(* and instead use Wolfram's capabilities. *)

(* DIRECT WOLFRAM COMPUTATION *)

Print[""];
Print["=== Direct Wolfram computation ==="];
Print[""];

(* S^2 spectral zeta: known exact result *)
(* zeta_S2'(0) = 4 zeta_R'(-1) + 2 log(2 Pi) - 3/2 *)
(* Source: Sarnak, Vardi, etc. *)
(* But let me verify *)

Print["Riemann zeta values:"];
Print["RZ'(-1)  = ", N[Derivative[1][Zeta][-1], 30]];
Print["RZ'(0)   = ", N[Derivative[1][Zeta][0], 30]];
Print["RZ(0)    = ", N[Zeta[0], 30]];
Print["RZ(-1)   = ", N[Zeta[-1], 30]];
Print[""];

(* The Vardi result for det(Laplacian on S^2) = *)
(* exp(1/3 - 4 zeta'(-1)) *)
(* i.e., zeta_{S^2}'(0) = -1/3 + 4 zeta_R'(-1) *)
(* Wait, this doesn't look right either. *)

(* Standard result: *)
(* zeta_{S^2}(s) = Sum_{l=1}^inf (2l+1) [l(l+1)]^{-s} *)
(* This can be written as: *)
(* = Sum_{l=1}^inf [(l+1)^{2-2s} - l^{2-2s}] / [using the identity *)
(* (2l+1) = (l+1)^2 - l^2 = [(l+1)-l][(l+1)+l] *)
(* and [l(l+1)]^{-s} is related to [(l+1)^2 - l^2] ... no] *)

(* Let me just compute numerically via partial sums + Euler-Maclaurin *)

nmax = 10000;

zetaS2val[s_?NumericQ] := NSum[(2 n + 1)/(n (n + 1))^s, {n, 1, Infinity},
  WorkingPrecision -> 40, Method -> "AlternatingSigns"];

(* Test at s = 1 *)
Print["zeta_{O(-2)}(1) = ", N[zetaS2val[1], 20], " (should be 2: harmonic series related)"];

(* Compute zeta(0) *)
Print["zeta_{O(-2)}(0) = ", N[zetaS2val[0], 20], " (should be -2/3 if sum = Sum (2l+1) reg.)"];

(* For zeta'(0), use finite difference *)
h = 10^(-8);
zprime0Om2 = N[(zetaS2val[h] - zetaS2val[-h])/(2 h), 20];
Print["zeta'_{O(-2)}(0) approx = ", zprime0Om2];

Print[""];

(* O(-1) spectral zeta *)
(* eigenvalues (2n+1)(2n+3)/4, mult 2n+2, n >= 0 *)
zetaOm1val[s_?NumericQ] := NSum[(2 n + 2)/((2 n + 1) (2 n + 3)/4)^s, {n, 0, Infinity},
  WorkingPrecision -> 40, Method -> "AlternatingSigns"];

Print["zeta_{O(-1)}(0) = ", N[zetaOm1val[0], 20]];

zprime0Om1 = N[(zetaOm1val[h] - zetaOm1val[-h])/(2 h), 20];
Print["zeta'_{O(-1)}(0) approx = ", zprime0Om1];

Print[""];

(* DIFFERENCE *)
diff = zprime0Om2 - zprime0Om1;
Print["=== THRESHOLD SPLITTING ==="];
Print[""];
Print["zeta'(0; O(-2)) - zeta'(0; O(-1)) on CP^1 = ", diff];
Print[""];
Print["Total splitting (3 exceptional divisors):"];
total = 3 * diff;
Print["Delta_3 - Delta_2 = 3 * diff = ", total];
Print[""];
target = Log[3]/Sqrt[2];
Print["Target ln(3)/sqrt(2) = ", N[target, 20]];
Print["Ratio = ", N[total/target, 20]];
Print["Difference = ", N[total - target, 20]];
