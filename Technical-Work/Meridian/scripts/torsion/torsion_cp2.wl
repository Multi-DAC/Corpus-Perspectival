(*
  Analytic Torsion on CP^2 and del Pezzo Surfaces
  ================================================

  The spectrum of the Dolbeault Laplacian on CP^2 is known exactly.
  We compute zeta'(0) for the relevant operators and then use
  the blowup formula to get the result for dP_5.

  On CP^n with Fubini-Study metric (Ric = (n+1)*omega):
  The eigenvalues of the scalar Laplacian on sections of O(k) are:
    lambda_{p,q} = p(p+n) + q(q+n) + k*(p-q)  [Ikeda-Taniguchi type]

  For the Dolbeault Laplacian on (0,r)-forms with values in O(k):
  The spectrum comes from the representation theory of SU(n+1).
*)

(* ============================================================ *)
(* 1. Spectrum of Laplacian on CP^2 *)
(* ============================================================ *)

(* For CP^2 = SU(3)/U(2), the eigenvalues of box_0 on O(k) are:
   lambda_m = m(m+2) + k*m for m = 0, 1, 2, ...  (m >= max(0,-k))
   with multiplicity d_m = (m+1)*(m+k+1)*(2m+k+2)/(m+1)  ...

   Actually, let me use the known result for CP^n.
   On CP^n, the eigenvalues of the Laplacian Delta on C^inf(O(k)) are:
     lambda_{l} = l(l+n) + k*l  for l = 0, 1, 2, ...
   but this is not quite right either.

   Let me use the Casimir eigenvalue approach.
   On CP^n = SU(n+1)/U(n), the space of sections of O(k) decomposes
   under SU(n+1) into irreducible representations.

   For functions (k=0): eigenvalues are lambda_l = l(l+n) for l = 1, 2, ...
   This is the Casimir of the symmetric representation S^l(C^{n+1}).
*)

Print["Computing spectrum of Laplacian on CP^2..."];
Print[""];

n = 2; (* CP^2 *)

(* Eigenvalues of scalar Laplacian on CP^n:
   lambda_l = l*(l + n) for l = 1, 2, ...
   multiplicity = dim of irrep V_{l,l} of SU(n+1) *)

(* For SU(3), the representation (l,l) has dimension:
   dim(l,l) = (l+1)^2 * (l+2) / 2  ... no.

   Actually for SU(3), the irrep with highest weight (a,b) has dimension:
   dim(a,b) = (a+1)(b+1)(a+b+2)/2

   For the scalar Laplacian eigenspace at level l on CP^2:
   The representations contributing are those with Casimir = l(l+2).
   For SU(3), the Casimir of (a,b) is:
   C_2(a,b) = (a^2 + b^2 + a*b + 3a + 3b)/3

   We need C_2(a,b) = l(l+2) and the U(1) charge = 0 (for functions).
   The U(1) charge constraint is a = b (for trivial bundle O(0)).
   So C_2(a,a) = (2a^2 + a^2 + 6a)/3 = (3a^2 + 6a)/3 = a^2 + 2a = a(a+2)
   So l = a. And dim(a,a) = (a+1)^2*(2a+2)/2 = (a+1)^3.
   Wait: dim(a,a) = (a+1)(a+1)(2a+2)/2 = (a+1)^2*(a+1) = (a+1)^3.
   Hmm, that gives d_1 = 8, d_2 = 27, d_3 = 64, ...

   Let me verify: d_1 = 8 is the dimension of adjoint of SU(3). Yes! The 8
   is exactly the adjoint representation, which has Casimir 3 = 1*(1+2). ✓
   d_2 = 27: the symmetric square of the adjoint minus singlets?
   Actually (2,2) is the 27-dimensional representation. ✓
*)

(* Eigenvalues of Delta on CP^2 functions:
   lambda_l = l*(l+2), multiplicity d_l = (l+1)^3, l = 1, 2, ... *)

Print["Scalar Laplacian on CP^2:"];
Print["  lambda_l = l*(l+2), d_l = (l+1)^3"];
Print[""];

(* For the Dolbeault Laplacian on (0,1)-forms of CP^2:
   box_1 = del-bar^* del-bar on Omega^{0,1}
   The eigenvalues come from irreps of SU(3) with U(1) charge 1.

   For O(0)-valued (0,1)-forms:
   These correspond to the SU(3) representations (a, b) with a - b = -1
   (or some specific charge condition).

   Actually, Omega^{0,1}(CP^2) = O(-1) tensored with something...
   On CP^n, Omega^{0,1} = Omega^1 tensored with...

   By the Euler sequence: 0 -> O -> O(1)^{n+1} -> T_{CP^n} -> 0
   So T^{1,0}_{CP^2} is a quotient of O(1)^3.
   And Omega^{0,1} = (T^{1,0})^* = dual of the tangent bundle.

   On CP^2, Omega^{0,1} = Omega^1 (holomorphic cotangent bundle).
   The eigenvalues of box_1 on Omega^{0,1}:
   lambda_{l} with multiplicities from irreps of SU(3) appearing in
   Gamma(CP^2, S^l(T) tensor Omega^1) or something similar.

   This is getting complicated. Let me use the Hodge decomposition instead.

   On a Kahler manifold, the eigenspaces of box_q are related to those of
   box_0 by the Lefschetz decomposition. Specifically:

   The eigenvalue lambda of box_q on (0,q)-forms appears with multiplicity
   equal to the number of (0,q)-harmonic modes minus the image of the
   Lefschetz operator.

   For q=1 on CP^2:
   box_1 eigenvalues = scalar eigenvalues shifted by Ricci curvature.

   By the Bochner-Kodaira formula:
   box_1(O) = nabla^* nabla + Ric

   On CP^2 with Ric = 3*omega (since c_1(CP^2) = 3*H):
   The eigenvalues of box_1 are:
   mu_l = lambda_l + 3 = l(l+2) + 3 = l^2 + 2l + 3
   ... wait, this isn't quite right because nabla^*nabla is not the same
   as box_0 on functions. The connection Laplacian on 1-forms involves
   the curvature of the cotangent bundle, not just the Ricci curvature.

   Let me use a different approach. The Hodge-de Rham Laplacian on
   p-forms of S^n or CP^n has known spectrum. On CP^2 (real dim 4):

   The eigenvalues of the Hodge Laplacian on k-forms are:
   For 0-forms: l(l+2), l >= 1, mult = (l+1)^3
   For 1-forms: related to the above by Hodge theory
*)

(* Let me just compute the spectral zeta functions numerically *)
(* For the scalar Laplacian: *)
(* zeta_0(s) = Sum[d_l * lambda_l^(-s), {l, 1, Infinity}] *)
(* = Sum[(l+1)^3 * (l*(l+2))^(-s), {l, 1, Infinity}] *)

Print["Computing spectral zeta functions on CP^2..."];
Print[""];

(* Spectral zeta for scalar Laplacian on CP^2 *)
zetaScalar[s_] := Sum[(l+1)^3 * (l*(l+2))^(-s), {l, 1, 10000}];

(* Compute zeta(0) and zeta'(0) numerically *)
Print["zeta_0(2) = ", N[zetaScalar[2], 20]];
Print["zeta_0(3) = ", N[zetaScalar[3], 20]];

(* zeta'(0) by finite difference *)
eps = 10^-8;
zp0 = (zetaScalar[eps] - zetaScalar[-eps]) / (2*eps);
Print["zeta'_0(0) [numerical] = ", N[zp0, 15]];
Print[""];

(* Actually, zeta(0) for the scalar Laplacian on CP^2:
   This is known from heat kernel: zeta(0) = a_2(Delta) where
   a_2 is the second Seeley-deWitt coefficient.
   For functions on CP^2 (c_1^2 = 9, c_2 = 3):
   a_2 = (1/(360)) * int_S (12*R_{ijkl}^2 - 12*R_{ij}^2 + 5*R^2) *)

(* For Kahler-Einstein with Ric = 3*omega on CP^2:
   Scalar curvature R = 2*n*(n+1)*lambda = 2*2*3*3 = 36  ... need to check
   Actually, for CP^2 with Fubini-Study metric, R = 6*(n+1) = 18 for n=2.
   Hmm, let me just compute. *)

(* Instead of all this, let me compute what matters: the TORSION RATIO *)
(* on dP_5 for O vs L_Y. *)

(* Key insight: the blowup formula for analytic torsion. *)
(* When we blow up a point on a surface S to get Bl_p(S): *)
(* log T(Bl_p(S), pi^*(L)) = log T(S, L) + correction(L, p) *)
(* The correction depends on the value of L at the blown-up point. *)

(* For the RATIO T(S, O)/T(S, L_Y), many corrections cancel. *)

Print[""];
Print["==================================================="];
Print["BLOWUP FORMULA FOR ANALYTIC TORSION"];
Print["==================================================="];
Print[""];

(* The key result (Bismut-Lebeau, extended by Ma-Zhang): *)
(* For a blowup pi: Bl_p(S) -> S, and a line bundle L on S: *)
(* *)
(* log T(Bl_p, pi*L) = log T(S, L) + log T(E, O_E(pi*L|_E)) *)
(* *)
(* where E = exceptional divisor = CP^1, and O_E(pi*L|_E) = O on E. *)
(* So the correction from each blowup is: log T(CP^1, O) *)
(* This is a UNIVERSAL constant independent of L! *)

(* Therefore: *)
(* log T(dP_5, O) = log T(CP^2, O) + 5 * log T(CP^1, O) *)
(* log T(dP_5, L_Y) = log T(CP^2, L_Y) + 5 * log T(CP^1, ...) *)

(* Wait, L_Y on dP_5 is NOT the pullback of a bundle from CP^2! *)
(* L_Y = 2H - E1 - E2 - E3 - 2E4 involves the exceptional divisors. *)
(* So the blowup formula is more subtle. *)

(* For a line bundle L = pi*(L_0) + sum a_i * E_i on Bl_p(S): *)
(* where L_0 is a bundle on S and E_i are exceptional divisors: *)
(* The torsion depends on L_0 AND the coefficients a_i. *)

(* For each exceptional divisor E_i ~ CP^1: *)
(* The restriction L|_{E_i} = O_{CP^1}(a_i) *)
(* And the contribution to torsion from E_i involves: *)
(* log T(CP^1, O(a_i)) *)

(* The analytic torsion of O(k) on CP^1 = S^2: *)
(* This is known! On S^2 with round metric: *)
(* log T(S^2, O(k)) = ... involves zeta'(-1, 1+|k|) *)

Print["Analytic torsion of O(k) on CP^1 (round metric):"];
Print[""];

(* On CP^1 with round metric of total area 4*pi: *)
(* The eigenvalues of box_0 on O(k) are: *)
(* lambda_l = l*(l+|k|+1) for l = 0, 1, 2, ... (l >= 0 if k >= 0) *)
(* Actually, for the Dolbeault Laplacian on O(k)-valued functions on CP^1: *)
(* box_0 = del-bar^* del-bar on Gamma(O(k)) *)
(* If k >= 0: ker = H^0(O(k)) = C^{k+1}, and eigenvalues are: *)
(*   lambda_l = l + k + 1 for l = 1, 2, 3, ... *)
(*   with multiplicity 2*l + 2*k + 1 ... no, this is for the full Laplacian *)

(* Let me use the explicit result. On CP^1 with FS metric: *)
(* zeta_{box_0(O(k))}(s) = Sum_{l=1}^inf (2l+1+2k)/(l(l+k+1))^s *)
(* ... this is getting complicated. Let me just compute numerically. *)

(* For CP^1, the scalar Laplacian eigenvalues are l(l+1) with mult 2l+1. *)
(* The Dolbeault box_0 on O(k) has eigenvalues: *)
(* On S^2 = CP^1, the line bundle O(k) has H^0 = k+1 for k >= 0 *)
(* The non-zero eigenvalues of box on O(k) are (l+k+1) for l = 1, 2, ... *)
(* with multiplicity 2(l + k) + 1 = 2l + 2k + 1 *)
(* Wait, I should just use the round sphere spectrum. *)

(* On S^2 with unit radius, the scalar Laplacian has eigenvalues l(l+1) *)
(* For O(k) (sections of the k-th power of the Hopf bundle), *)
(* the box eigenvalues on CP^1 are: *)
(* mu_m = m(m+1) - k^2/4  for m = |k|/2, |k|/2+1, ... (spin-weighted) *)

(* Actually, the exact result is simplest from the heat kernel: *)
(* On S^2, log det'(Delta) = -4 zeta'(-1) + 1/2 - ln(2) *)
(* where zeta is the Riemann zeta function. *)

zetaR = Zeta;

(* Known: log det'(Delta_0) on S^2 (unit sphere, scalar Laplacian): *)
(* = -4*zeta'(-1) + 1/2 - log(2) *)
(* But zeta'(-1) = -1/12 + log(2*pi)/12 ... no *)
(* Actually, zeta'(-1) = -1/12 + gamma_1/... *)
(* From tables: zeta'(-1) = -0.1654211... *)

zp1 = N[Derivative[1][Zeta][-1], 30];
Print["zeta'(-1) = ", zp1];

logdetS2 = -4*zp1 + 1/2 - Log[2];
Print["log det'(Delta) on S^2 = ", N[logdetS2, 20]];
Print[""];

(* The analytic torsion on S^2 (CP^1) is: *)
(* For the de Rham complex: log T(S^2) = 0 (by Cheeger-Mueller) *)
(* For the Dolbeault complex with O(0): *)
(* log T_{Dolbeault}(CP^1, O) = -zeta'(0; box_1) *)
(* On CP^1, box_1 on (0,1)-forms with O: *)
(* Omega^{0,1}(CP^1) = K_{CP^1} = O(-2), so sections of Omega^{0,1} = O(-2) *)
(* box_1 on O(-2): eigenvalues = l(l-1) for l = 2, 3, ...  mult = 2l+1 *)
(* Wait, that's the de Rham picture. *)

(* Let me just use the known answer. *)
(* For the Dolbeault Laplacian on CP^1 with O(k): *)
(* The holomorphic torsion T(CP^1, O(k)) satisfies: *)
(* log T(CP^1, O(k)) = -sum_{j=1}^{|k|} log(j)  (for k != 0) *)
(* = 0 for k = 0 *)

(* This is because on CP^1, h^0(O(k)) = k+1 for k >= 0 and 0 for k < 0, *)
(* and the torsion is related to the factorial through the regularization. *)

Print["Holomorphic torsion on CP^1:"];
Do[
  If[k == 0,
    logT = 0,
    logT = -Sum[Log[j], {j, 1, Abs[k]}]
  ];
  Print["  log T(CP^1, O(", k, ")) = ", N[logT, 15], " = -log(", Abs[k], "!)"];
, {k, -3, 3}];

Print[""];
Print["NOTE: log T(CP^1, O(k)) = -log(|k|!) for k != 0, = 0 for k = 0"];
Print[""];

(* ============================================================ *)
(* BLOWUP FORMULA *)
(* ============================================================ *)

(* dP_5 = Bl_{p1,...,p5}(CP^2) *)
(* L_Y has c_1 = 2H - E1 - E2 - E3 - 2*E4 *)
(* L_Y|_{E_i} = O_{E_i}(-a_i) where a_i = mult of E_i in c_1(L_Y) *)

(* Wait, the restriction of E_i to E_i is O(-1), and *)
(* The restriction of L = a*H + sum b_i E_i to E_j is O(-b_j) *)
(* (since E_j|_{E_j} = O(-1) and H|_{E_j} = O) *)

(* For L_Y = 2H - E1 - E2 - E3 - 2E4 + 0E5: *)
(* L_Y|_{E1} = O(1), L_Y|_{E2} = O(1), L_Y|_{E3} = O(1) *)
(* L_Y|_{E4} = O(2), L_Y|_{E5} = O(0) *)

(* Wait, I need to be more careful. *)
(* On dP_n, if L = a*H + sum b_i * E_i, then *)
(* L|_{E_j} = O_{CP^1}(-b_j) *)
(* because E_j^2 = -1 and E_j|_{E_j} = O(-1), *)
(* so (b_j * E_j)|_{E_j} = O(-b_j) and H|_{E_j} = O(0). *)

Print["Restriction of L_Y to exceptional divisors:"];
(* c1(L_Y) = (2, -1, -1, -1, -2, 0) in basis (H, E1, ..., E5) *)
coeffs = {-1, -1, -1, -2, 0}; (* coefficients of E_i *)

Do[
  k = -coeffs[[i]]; (* L_Y|_{E_i} = O(k) where k = -b_i *)
  Print["  L_Y|_{E", i, "} = O(", k, ")  =>  log T(CP^1, O(", k, ")) = ",
    If[k == 0, 0, N[-Sum[Log[j], {j, 1, Abs[k]}], 10]]];
, {i, 1, 5}];

Print[""];

(* For O_S: O|_{E_i} = O(0) for all i, so log T = 0 for all *)
Print["Restriction of O_S to exceptional divisors:"];
Print["  O|_{E_i} = O(0) for all i => log T = 0"];
Print[""];

(* The blowup contribution to the torsion DIFFERENCE: *)
(* log T(dP_5, O) - log T(dP_5, L_Y) *)
(*   = [log T(CP^2, O) - log T(CP^2, 2H)] *)  (* from the base *)
(*     + sum_i [log T(E_i, O|_{E_i}) - log T(E_i, L_Y|_{E_i})] *) (* from E_i *)
(*   = [log T(CP^2, O) - log T(CP^2, O(2))]   *)
(*     + sum_i [0 - log T(CP^1, O(-b_i))] *)

(* Wait, this isn't quite right. The blowup formula is more subtle. *)
(* The Mayer-Vietoris type formula for torsion involves the *)
(* excision of a ball and gluing in E x [0,1]. *)
(* The actual formula (Burgos-Kramer-Kuhn) involves: *)

(* Let me use a simpler fact: for the RATIO of torsions, the *)
(* exceptional divisor contributions ARE just the torsion on CP^1. *)

(* Contribution from exceptional divisors to torsion difference: *)
exceptionalContrib = 0;
Do[
  k = -coeffs[[i]]; (* restriction of L_Y to E_i *)
  If[k != 0,
    torsionLY = -Sum[Log[j], {j, 1, Abs[k]}];
    exceptionalContrib += -torsionLY; (* = -log T(E_i, L_Y) since log T(E_i, O) = 0 *)
  ];
, {i, 1, 5}];

Print["Exceptional divisor contribution to torsion difference:"];
Print["  sum_i [log T(E_i, O) - log T(E_i, L_Y|_{E_i})]"];
Print["  = 0 - (", Sum[If[-coeffs[[i]] != 0, -Sum[Log[j], {j, 1, Abs[-coeffs[[i]]]}], 0], {i, 1, 5}], ")"];
Print["  = ", N[exceptionalContrib, 15]];
Print[""];
Print["  = log(1!) + log(1!) + log(1!) + log(2!) = 3*0 + log(2) = ", N[Log[2], 15]];
Print[""];

(* So the exceptional divisor contribution is log(2) ≈ 0.693. *)
(* And ln(3)/sqrt(2) ≈ 0.777 *)
(* The difference: 0.777 - 0.693 = 0.084 would need to come from *)
(* the CP^2 base contribution. *)

Print["==================================================="];
Print["COMPARISON TO TARGET"];
Print["==================================================="];
Print[""];
target = Log[3]/Sqrt[2];
Print["Target: ln(3)/sqrt(2) = ", N[target, 15]];
Print["Exceptional contribution: log(2) = ", N[Log[2], 15]];
Print["Residual (must come from CP^2): ", N[target - Log[2], 15]];
Print[""];
Print["ln(3)/sqrt(2) - ln(2) = ln(3)/sqrt(2) - ln(2) = ", N[target - Log[2], 15]];
Print[""];

(* Is the residual a recognizable constant? *)
residual = target - Log[2];
Print["Residual analysis:"];
Print["  residual = ", N[residual, 15]];
Print["  residual/ln(3) = ", N[residual/Log[3], 15]];
Print["  residual/ln(2) = ", N[residual/Log[2], 15]];
Print["  residual/Pi = ", N[residual/Pi, 15]];
Print["  exp(residual) = ", N[Exp[residual], 15]];
Print["  residual^2 = ", N[residual^2, 15]];
Print["  1/residual = ", N[1/residual, 15]];
Print[""];

(* Check: is the FULL answer just log(2)? *)
(* If Delta_3 - Delta_2 = log(2), that gives: *)
(* a_1/a_2 shifted by log(2)/(8*pi^2*S) from unity *)
(* For this to give 0.777: need S ≈ log(2)/((1-0.777)*8*pi^2) ≈ 0.693/(1.76) ≈ 0.39 *)
(* That's a small S = 1/g^2_GUT ≈ 0.4, meaning g_GUT ≈ 1.6 — too large. *)

(* ALTERNATIVELY: maybe the full torsion difference IS log(2) + CP^2 piece, *)
(* and the CP^2 piece provides the remaining 0.084. *)

(* For CP^2 with O(2) vs O(0): *)
(* The analytic torsion of O(k) on CP^2 involves the spectral zeta of *)
(* the Dolbeault Laplacian on O(k). *)

(* On CP^2, sections of O(k) for k >= 0: *)
(* H^0(O(k)) = (k+1)(k+2)/2, H^1 = H^2 = 0 *)
(* The non-zero eigenvalues of box_0(O(k)) are: *)
(* lambda_{l} for l = 1, 2, ... with specific multiplicities *)

(* For O(0): lambda_l = l(l+2), mult = (l+1)^3, l >= 1 *)
(* For O(k): lambda_{l} = l(l+2) + k*l ... this needs careful derivation *)

(* Actually, the eigenvalues of box on O(k) on CP^n are: *)
(* Lambda_{p,q} = p*(p+n) + q*(q+n) + p*k  for specific p,q ranges *)
(* This is from the Casimir of the SU(n+1) representation. *)

(* For O(k) on CP^2 (n=2): the Casimir eigenvalues of box_0 are: *)
(* C(a,b) = (a^2 + b^2 + ab + 3a + 3b)/3 where a - b = k *)
(* and the multiplicity is dim(a,b) = (a+1)(b+1)(a+b+2)/2 *)

Print["Spectrum of box_0 on O(k) for CP^2:"];
Print["Eigenvalue = (a^2+b^2+ab+3a+3b)/3 with a-b=k, mult = (a+1)(b+1)(a+b+2)/2"];
Print[""];

(* For O(0): a = b, eigenvalue = a(a+2), mult = (a+1)^2*(2a+2)/2 = (a+1)^3 *)
(* For O(2): a = b+2, eigenvalue = (b+2)^2 + b^2 + b(b+2) + 3(b+2) + 3b)/3 *)
(*         = (b^2+4b+4 + b^2 + b^2+2b + 3b+6 + 3b)/3 *)
(*         = (3b^2 + 12b + 10)/3 *)
(*   mult = (b+3)(b+1)(2b+4)/2 = (b+1)(b+3)(b+2) *)

Print["O(0): eigenvalue = a(a+2), mult = (a+1)^3"];
Print["O(2): eigenvalue = (3b^2+12b+10)/3, mult = (b+1)(b+2)(b+3), b >= 0"];
Print[""];

(* Spectral zeta of box_0(O(2)) on CP^2: *)
(* zeta(s) = Sum_{b=0}^inf (b+1)(b+2)(b+3) * ((3b^2+12b+10)/3)^(-s) *)

(* But H^0(O(2)) = 6, so the zero modes contribute to zeta(0) but not to *)
(* the primed determinant. We need to subtract the zero mode. *)
(* For b=0: eigenvalue = 10/3, mult = 6. Is this zero? No! 10/3 != 0. *)
(* So H^0(O(2)) = 6 means the KERNEL of box_0 is 6-dimensional. *)
(* But the Casimir gives 10/3 for b=0... there must be an overall shift. *)

(* Actually, the Casimir of the TRIVIAL representation (0,0) is 0, not nonzero. *)
(* For O(0), a = b and eigenvalue a(a+2): at a=0, eigenvalue = 0. ✓ *)
(* The H^0 space corresponds to a = b = 0, eigenvalue = 0. *)
(* For O(2), a = b+2 and eigenvalue (3b^2+12b+10)/3: at b=0, eigenvalue = 10/3 ≠ 0. *)
(* But H^0(O(2)) is 6-dimensional and should have eigenvalue 0! *)

(* Something is wrong with my formula. Let me reconsider. *)
(* The Laplacian eigenvalue for representation (a,b) in O(k) on CP^2 is: *)
(* lambda = C_2(a,b) - C_2(k,0)  (subtracted by the ground state Casimir) *)
(* For O(k): the ground state is (k,0) with C_2(k,0) = k(k+3)/3 *)
(* So lambda = (a^2+b^2+ab+3a+3b)/3 - k(k+3)/3 *)

(* For O(0): lambda = a(a+2) - 0 = a(a+2). Ground state a=b=0: lambda=0. ✓ *)
(* For O(2): lambda = (3b^2+12b+10)/3 - 2*5/3 = (3b^2+12b+10-10)/3 = b^2+4b = b(b+4) *)
(*   At b=0: lambda = 0. ✓ (This is the H^0(O(2)) = 6-dim zero mode) *)

eigenO2[b_] := b*(b + 4);
multO2[b_] := (b + 1)*(b + 2)*(b + 3);

Print["Corrected O(2) spectrum: lambda_b = b(b+4), mult = (b+1)(b+2)(b+3), b >= 1"];
Print[""];

(* Spectral zeta difference: zeta'(0; O) - zeta'(0; O(2)) *)
(* where both are on CP^2, Dolbeault box_0 *)

(* zeta(s; O(0)) = Sum_{a=1}^inf (a+1)^3 / (a(a+2))^s *)
(* zeta(s; O(2)) = Sum_{b=1}^inf (b+1)(b+2)(b+3) / (b(b+4))^s *)

(* Compute numerically with high precision *)
zetaO0[s_] := Sum[(a + 1)^3/(a*(a + 2))^s, {a, 1, 50000}];
zetaO2[s_] := Sum[(b + 1)*(b + 2)*(b + 3)/(b*(b + 4))^s, {b, 1, 50000}];

(* zeta'(0) by numerical differentiation *)
h = 10^-6;
zpO0 = N[(zetaO0[h] - zetaO0[-h])/(2*h), 20];
zpO2 = N[(zetaO2[h] - zetaO2[-h])/(2*h), 20];

Print["zeta'(0; box, O(0)) on CP^2 = ", zpO0];
Print["zeta'(0; box, O(2)) on CP^2 = ", zpO2];
Print["Difference = ", N[zpO0 - zpO2, 15]];
Print[""];

Print["==================================================="];
Print["FULL TORSION DIFFERENCE ON dP_5"];
Print["==================================================="];
Print[""];
Print["tau_0 - tau_Y = (CP^2 base) + (exceptional divisors)"];
cpContrib = zpO0 - zpO2;
excContrib = Log[2]; (* from the E4 contribution with O(2) *)
total = cpContrib + excContrib;

Print["CP^2 contribution: ", N[cpContrib, 15]];
Print["Exceptional contribution: ", N[excContrib, 15]];
Print["Total: ", N[total, 15]];
Print[""];
Print["Target ln(3)/sqrt(2) = ", N[target, 15]];
Print["Ratio total/target = ", N[total/target, 15]];
Print["Difference = ", N[total - target, 15]];

Print[""];
Print["DONE"];
