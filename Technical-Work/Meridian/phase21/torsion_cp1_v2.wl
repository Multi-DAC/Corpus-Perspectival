(*
  Threshold splitting from CP^1 exceptional divisors — v2
  Uses Hurwitz zeta for proper analytic continuation.

  KEY RESULT FROM BRANCHING COMPUTATION:
  box_1 spectra on CP^2 are IDENTICAL for O(0) and O(2).
  Threshold splitting = 3 * [zeta1'(0; O) - zeta1'(0; O(1))] on CP^1.

  By Serre duality on CP^1 (K = O(-2)):
  zeta1'(O(k)) = zeta0'(O(k-2))

  So: threshold = 3 * [zeta0'(O(-2)) - zeta0'(O(-1))]

  Spectra:
  O(-2) on CP^1: l=1,2,3,..., eigenvalue l(l+1), mult 2l+1
    = standard S^2 spectrum
  O(-1) on CP^1: j=1,3,5,..., eigenvalue j(j+2)/4, mult j+1
    With n=(j-1)/2: eigenvalue (2n+1)(2n+3)/4, mult 2n+2, n=0,1,2,...
*)

Print["THRESHOLD SPLITTING — CP^1 EXCEPTIONAL DIVISORS (v2)"];
Print["======================================================"];
Print[""];

$MaxExtraPrecision = 500;

(* ============================================================ *)
(* PART 1: S^2 spectral zeta (= O(-2) on CP^1) *)
(* ============================================================ *)

(* KNOWN EXACT RESULT (Vardi 1988, Sarnak 1987): *)
(* For S^2 with unit radius (eigenvalues l(l+1), mult 2l+1): *)
(*   zeta(0) = -2/3 *)
(*   zeta'(0) = 4*zeta_R'(-1) - 1/3 + 2*log(2*Pi) - ... *)

(* Actually let me derive it properly using the formula: *)
(* zeta(s) = Sum_l (2l+1)/[l(l+1)]^s *)
(* = Sum_l [(l+1)^{2-2s} - l^{2-2s}] ... no, that's not right *)

(* Use the Hurwitz representation (separating l=1): *)
(* zeta(s) = 3*2^{-s} + Sum_{l=2}^inf (2l+1)/[l(l+1)]^s *)
(* For l >= 2, expand (l+1)^{-s} = l^{-s}(1+1/l)^{-s} *)
(* = l^{-s} Sum_k (-1)^k C(s+k-1,k) l^{-k} *)
(* This converges for l >= 2 since |1/l| <= 1/2 *)

(* But including l=1: use the identity that the full formula *)
(* zeta(s) = Sum_k (-1)^k C(s+k-1,k) [2*RZ(2s+k-1) + RZ(2s+k)] *)
(* is CORRECT due to cancellation with the boundary term *)

(* Compute zeta'(0) from the k-expansion: *)
(* zeta'(0) = Sum_k d/ds[(-1)^k C(s+k-1,k) (2*RZ(2s+k-1)+RZ(2s+k))]|_{s=0} *)

(* k=0: d/ds [2*RZ(2s-1) + RZ(2s)]|_{s=0} = 4*RZ'(-1) + 2*RZ'(0) *)

zpS2k0 = N[4*Derivative[1][Zeta][-1] + 2*Derivative[1][Zeta][0], 30];
Print["S^2 zeta'(0) k=0: ", zpS2k0];

(* k=1: d/ds [-s*(2*RZ(2s) + RZ(2s+1))]|_{s=0} *)
(* = -(2*RZ(0) + [pole]) - 0 *)
(* -s*RZ(2s+1) near s=0: RZ(1+2s) = 1/(2s) + gamma + O(s) *)
(* -s*RZ(2s+1) = -1/2 - s*gamma + O(s^2) *)
(* d/ds = -gamma *)
(* -s*2*RZ(2s): at s=0 gives -2*RZ(0) = 1. d/ds at s=0 = 1 [d/ds(-2s*RZ(2s))|_{s=0}] *)
(* Wait: -s*2*RZ(2s) = -2s*RZ(2s). RZ(2s) near s=0: RZ(0) + 2s*RZ'(0) + ... = -1/2 + 2s*RZ'(0) + ... *)
(* d/ds[-2s*(-1/2 + ...)] = -2*(-1/2) = 1. So d/ds[-2s*RZ(2s)]|_{s=0} = 1 *)

zpS2k1 = N[1 - EulerGamma, 30];
Print["S^2 zeta'(0) k=1: ", zpS2k1];

(* k=2: d/ds [s(s+1)/2 * (2*RZ(2s+1)+RZ(2s+2))]|_{s=0} *)
(* RZ(2s+1) has pole at s=0: RZ(1+2s) = 1/(2s) + gamma + O(s) *)
(* s(s+1)/2 * 2 * RZ(2s+1) = s(s+1) * [1/(2s) + gamma + ...] *)
(* = (s+1)/2 + s(s+1)*gamma + ... *)
(* At s=0: 1/2 *)
(* d/ds: 1/2 + gamma + ... = 1/2 + gamma at s=0 *)

(* s(s+1)/2 * RZ(2s+2): at s=0 = 0. d/ds = (1/2)*RZ(2) = (1/2)*(Pi^2/6) *)

zpS2k2 = N[1/2 + EulerGamma + Pi^2/12, 30];
Print["S^2 zeta'(0) k=2: ", zpS2k2];

(* k=3: d/ds [-s(s+1)(s+2)/6 * (2*RZ(2s+2)+RZ(2s+3))]|_{s=0} *)
(* Since s divides the prefactor, at s=0 the whole thing is 0 *)
(* d/ds: = -(1*2/6)*(2*RZ(2)+RZ(3)) = -(1/3)*(Pi^2/3 + RZ(3)) *)
zpS2k3 = N[-(1/3)*(Pi^2/3 + Zeta[3]), 30];
Print["S^2 zeta'(0) k=3: ", zpS2k3];

(* k=4: d/ds [C(s+3,4)*(2*RZ(2s+3)+RZ(2s+4))]|_{s=0} *)
(* C(s+3,4)|_{s=0} = C(3,4) = 0. d/ds C(s+3,4)|_{s=0} = ? *)
(* C(s+3,4) = (s+3)(s+2)(s+1)s/24 *)
(* d/ds at s=0: (3*2*1*1 + 0)/24 = 6/24 = 1/4 *)
(* Term: (1/4)*(2*RZ(3)+RZ(4)) *)
zpS2k4 = N[(1/4)*(2*Zeta[3] + Zeta[4]), 30];
Print["S^2 zeta'(0) k=4: ", zpS2k4];

(* For k >= 3 (no poles): *)
(* d/ds[(-1)^k C(s+k-1,k) (2*RZ(2s+k-1)+RZ(2s+k))]|_{s=0} *)
(* = (-1)^k * [d/ds C(s+k-1,k)]|_{s=0} * (2*RZ(k-1)+RZ(k)) *)
(* since at s=0, C(k-1,k) = 0 for k >= 2, so the value is 0 *)
(* and the derivative is: *)
(* C(s+k-1,k) = Product_{j=0}^{k-1} (s+j)/k! *)
(* At s=0: = Product_{j=0}^{k-1} j / k! = (k-1)!/k! = 1/k (for k >= 1) *)
(* Wait: C(s+k-1, k) = (s+k-1)(s+k-2)...(s)/k! *)
(* At s=0: 0 (because of the s factor for k >= 1) *)
(* d/ds at s=0: Product_{j=1}^{k-1} j / k! = (k-1)!/k! = 1/k *)

(* So for k >= 3: *)
(* contribution = (-1)^k * (1/k) * (2*RZ(k-1) + RZ(k)) *)

Print[""];
Print["Higher k terms:"];
zpS2higher = 0;
Do[
  term = (-1)^k * (1/k) * (2*Zeta[k-1] + Zeta[k]);
  zpS2higher += N[term, 30];
  If[k <= 10, Print["  k=", k, ": ", N[term, 20]]];
, {k, 3, 200}];
Print["  Sum k=3..200: ", zpS2higher];

zpS2total = zpS2k0 + zpS2k1 + zpS2k2 + zpS2higher;
Print[""];
Print["zeta'_{S^2}(0) = ", zpS2total];

(* Cross-check with known: 4*RZ'(-1) - 1/3 + ... *)
Print["4*RZ'(-1) = ", N[4*Derivative[1][Zeta][-1], 20]];
Print["2*RZ'(0) = ", N[2*Derivative[1][Zeta][0], 20]];
Print[""];

(* ============================================================ *)
(* PART 2: O(-1) spectral zeta *)
(* ============================================================ *)

(* Eigenvalues: (2n+1)(2n+3)/4, mult 2(n+1), n = 0,1,2,... *)
(* With u = n+1: eigenvalue = (2u-1)(2u+1)/4, mult = 2u, u = 1,2,3,... *)
(* = (4u^2-1)/4, mult 2u *)

(* zeta(s) = Sum_{u=1}^inf 2u * [4/(4u^2-1)]^s *)
(* = (4)^s * Sum_{u=1}^inf 2u * [(4u^2-1)]^{-s} *)

(* Let me use the same approach: separate u=1 and expand for u >= 2 *)
(* u=1: eigenvalue = 3/4, mult = 2. Contribution: 2*(3/4)^{-s} = 2*(4/3)^s *)
(* For u >= 2: expand (4u^2-1)^{-s} = (2u)^{-2s}(1-1/(4u^2))^{-s} *)
(* = Sum_k Pochhammer(s,k)/k! * (4u^2)^{-k} * (2u)^{-2s} *)
(* = Sum_k Pochhammer(s,k)/(k!*4^k) * 2^{-2s} * u^{-2s-2k} *)

(* zeta(s) - 2*(4/3)^s = 4^s * Sum_k Poch(s,k)/(k!*4^k) * 2^{-2s} * *)
(*   Sum_{u=2}^inf 2u * u^{-2s-2k} *)
(* = 4^s * 4^{-s} * Sum_k Poch(s,k)/(k!*4^k) * 2 * HZ(2s+2k-1, 2) *)
(* = Sum_k Poch(s,k)/(k!*4^k) * 2 * HZ(2s+2k-1, 2) *)

(* At s=0: 2*HZ(-1, 2) = 2*(RZ(-1)-1) = 2*(-1/12-1) = 2*(-13/12) = -13/6 *)
(* Plus the u=1 term: 2*(4/3)^0 = 2 *)
(* Total zeta(0) = 2 + (-13/6) = 12/6 - 13/6 = -1/6 *)

(* Hmm, but earlier analysis suggested -5/12. Let me check with the *)
(* alternating sum approach... *)

(* Actually let me just compute zeta(0) both ways and compare. *)

(* Direct check: *)
(* O(-1) eigenvalues at s=0: mult = 2, 4, 6, 8, ... *)
(* Regularized: Sum_{u=1}^inf 2u = 2*RZ(-1) = -1/6 *)
Print[""];
Print["=== O(-1) spectral zeta ==="];
Print["zeta_{O(-1)}(0) = 2*RZ(-1) = ", N[2*Zeta[-1], 20], " = -1/6"];

(* Now for zeta'(0): *)
(* Method: separate u=1 term, Pochhammer expansion for u >= 2 *)

(* u=1 term: 2*(4/3)^s. zeta'(0) contribution: 2*log(4/3) *)
zpOm1u1 = N[2*Log[4/3], 30];
Print["u=1 contribution to zeta'(0): 2*log(4/3) = ", zpOm1u1];

(* u >= 2: Sum_k Poch(s,k)/(k!*4^k) * 2 * HZ(2s+2k-1, 2) *)
(* But WAIT: the prefactor also has 4^s from the original zeta: *)
(* zeta(s) = 4^s * Sum_u 2u/(4u^2-1)^s *)
(* = 4^s * [2*(4/3)^s + Sum_k Poch(s,k)/(k!*4^k) * 2^{1-2s} * HZ(2s+2k-1, 2)] *)

(* Hmm wait, let me redo this more carefully. *)

(* zeta_{O(-1)}(s) = Sum_{u=1}^inf 2u * [(4u^2-1)/4]^{-s} *)
(* = 4^s Sum_{u=1}^inf 2u/(4u^2-1)^s *)

(* For u=1: 2*1/(4-1)^s = 2/3^s. Times 4^s: 2*(4/3)^s. OK. *)

(* For u >= 2: 2u/(4u^2-1)^s. *)
(* 4u^2-1 = (2u-1)(2u+1). *)
(* (4u^2-1)^{-s} = (2u)^{-2s}(1-1/(4u^2))^{-s} *)
(* = (2u)^{-2s} Sum_k Poch(s,k)/(k!*4^k) u^{-2k} *)

(* So 2u*(4u^2-1)^{-s} = 2u*(2u)^{-2s} Sum_k = 2^{1-2s}*u^{1-2s} Sum_k Poch/(k!4^k)*u^{-2k} *)

(* Sum over u >= 2: 2^{1-2s} Sum_k Poch(s,k)/(k!*4^k) * Sum_{u>=2} u^{1-2s-2k} *)
(* = 2^{1-2s} Sum_k Poch(s,k)/(k!*4^k) * HZ(2s+2k-1, 2) *)

(* Times 4^s: 4^s * 2^{1-2s} = 2^{2s} * 2^{1-2s} = 2. *)

(* So the full zeta after separating u=1: *)
(* zeta_{O(-1)}(s) = 2*(4/3)^s + 2*Sum_k Poch(s,k)/(k!*4^k) * HZ(2s+2k-1, 2) *)

(* d/ds at s=0: *)
(* = 2*log(4/3) + 2*Sum_k d/ds[Poch(s,k)/(k!*4^k) * HZ(2s+2k-1, 2)]|_{s=0} *)

(* k=0: d/ds[HZ(2s-1, 2)]|_{s=0} = 2*HZ'(-1, 2) where HZ' = d/d(alpha) *)
(* = 2*[RZ'(-1) - 0] ... wait: HZ(alpha, 2) = RZ(alpha) - 1, *)
(* so HZ'(alpha, 2) = RZ'(alpha). No: HZ(alpha, a) = Sum_{n=0}^inf (n+a)^{-alpha} *)
(* HZ(alpha, 2) = Sum_{n=0}^inf (n+2)^{-alpha} = Sum_{m=2}^inf m^{-alpha} = RZ(alpha) - 1 *)
(* d/d(alpha) HZ(alpha, 2) = -Sum_{m=2}^inf m^{-alpha} log(m) *)
(* = d/d(alpha) RZ(alpha) = RZ'(alpha) when we take the FULL derivative *)
(* Wait: d/d(alpha)[RZ(alpha) - 1] = RZ'(alpha). So HZ'(alpha,2) = RZ'(alpha). ✓ *)
(* But this is WRONG because HZ(alpha, a) = zeta_H(alpha, a) is the Hurwitz zeta. *)
(* d/d(alpha) zeta_H(alpha, a) is what Wolfram calls Derivative[1,0][HurwitzZeta]. *)
(* And zeta_H(alpha, 2) = zeta_R(alpha) - 1. *)
(* d/d(alpha) = zeta_R'(alpha). *)
(* No! d/d(alpha) [zeta_R(alpha) - 1] = zeta_R'(alpha). ✓ *)

(* BUT: d/d(alpha) zeta_H(alpha, 2) is NOT the same as Derivative[1,0][HurwitzZeta][alpha, 2] *)
(* because Wolfram's HurwitzZeta has a different sign/definition... actually it should be the same. *)

(* k=0 term: 2 * 2 * RZ'(-1) = 4*RZ'(-1) *)
zpOm1k0 = N[4*Derivative[1][Zeta][-1], 30];

(* k=1: d/ds[s/(1!*4) * HZ(2s+1, 2)]|_{s=0} *)
(* Poch(s,1) = s, so (1/4)*s*HZ(2s+1, 2) *)
(* HZ(2s+1, 2) = RZ(2s+1) - 1. Near s=0: RZ(1+2s) = 1/(2s)+gamma+O(s) *)
(* So HZ(2s+1, 2) = 1/(2s) + gamma - 1 + O(s) *)
(* (1/4)*s*[1/(2s) + gamma - 1 + ...] = 1/8 + s*(gamma-1)/4 + ... *)
(* d/ds = (gamma-1)/4 *)
zpOm1k1 = N[(EulerGamma - 1)/4, 30];

(* k=2: Poch(s,2)/(2!*4^2) = s(s+1)/32 *)
(* s(s+1)/32 * HZ(2s+3, 2): at s=0 = 0. d/ds = (1/32)*HZ(3,2) = (1/32)*(RZ(3)-1) *)
zpOm1k2 = N[(Zeta[3] - 1)/32, 30];

(* k >= 3: Poch(s,k)/(k!*4^k) at s=0 = 0. d/ds = (1/k)/(4^k) * ... *)
(* Actually: Poch(s,k) = s(s+1)...(s+k-1). d/ds at s=0 = (k-1)!. *)
(* So d/ds[Poch(s,k)/(k!*4^k)] = (k-1)!/(k!*4^k) = 1/(k*4^k) *)
(* Term: 1/(k*4^k) * HZ(2k-1, 2) = 1/(k*4^k) * (RZ(2k-1) - 1) *)

zpOm1higher = 0;
Do[
  term = 1/(k*4^k) * (Zeta[2*k - 1] - 1);
  zpOm1higher += N[term, 30];
, {k, 3, 200}];

(* Total zeta'_{O(-1)}(0): *)
zpOm1total = zpOm1u1 + 2*(zpOm1k0 + zpOm1k1 + zpOm1k2 + zpOm1higher);

Print[""];
Print["O(-1) zeta'(0) components:"];
Print["  u=1: 2*log(4/3) = ", zpOm1u1];
Print["  k=0: 4*RZ'(-1) = ", zpOm1k0, " (x2 = ", 2*zpOm1k0, ")"];
Print["  k=1: (gamma-1)/4 = ", zpOm1k1, " (x2 = ", 2*zpOm1k1, ")"];
Print["  k=2: (RZ(3)-1)/32 = ", zpOm1k2, " (x2 = ", 2*zpOm1k2, ")"];
Print["  k>=3: sum = ", zpOm1higher, " (x2 = ", 2*zpOm1higher, ")"];
Print[""];
Print["zeta'_{O(-1)}(0) = ", zpOm1total];

(* ============================================================ *)
(* PART 3: DIFFERENCE AND THRESHOLD *)
(* ============================================================ *)

Print[""];
Print["======================================================"];
Print["RESULTS"];
Print["======================================================"];
Print[""];

diff = zpS2total - zpOm1total;
Print["zeta'(0; S^2) = zeta'(0; O(-2))    = ", N[zpS2total, 20]];
Print["zeta'(0; O(-1))                      = ", N[zpOm1total, 20]];
Print["Difference zeta'(O(-2)) - zeta'(O(-1)) = ", N[diff, 20]];
Print[""];

total = 3 * diff;
target = Log[3]/Sqrt[2];
Print["Threshold splitting = 3 * difference = ", N[total, 20]];
Print["Target ln(3)/sqrt(2) = ", N[target, 20]];
Print["Ratio = ", N[total/target, 20]];
Print["Absolute difference = ", N[total - target, 20]];

(* Also compute exp(-zeta'/2) which is the torsion *)
Print[""];
Print["exp(-zeta'_{S^2}/2) = ", N[Exp[-zpS2total/2], 20]];
Print["exp(-zeta'_{O(-1)}/2) = ", N[Exp[-zpOm1total/2], 20]];
Print["Torsion ratio = ", N[Exp[-(zpS2total - zpOm1total)/2], 20]];
Print["Torsion ratio^3 = ", N[Exp[-3*(zpS2total - zpOm1total)/2], 20]];
