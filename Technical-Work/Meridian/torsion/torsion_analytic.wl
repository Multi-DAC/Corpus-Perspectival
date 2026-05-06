(*
  Analytic Torsion via Analytic Continuation
  ==========================================

  The spectral zeta for box_0 on O(0) on CP^2:
    zeta(s) = Sum_{m=2}^inf m^3 / (m^2 - 1)^s

  Expand (m^2-1)^{-s} = m^{-2s}(1-1/m^2)^{-s}
  = m^{-2s} * Sum_{k=0}^inf Pochhammer(s,k)/k! * m^{-2k}

  So zeta(s) = Sum_{k=0}^inf [Pochhammer(s,k)/k!] * HurwitzZeta(2s+2k-3, 2)

  zeta'(0) = derivative at s=0 of this expansion.
  Need special care at k=2 (pole of HurwitzZeta).
*)

Print["ANALYTIC TORSION VIA ANALYTIC CONTINUATION"];
Print["============================================"];
Print[""];

(* The formula for zeta'(0; O(0)) on CP^2: *)
(* zeta'(0) = 2*HZ'(-3,2) + HZ(-1,2) + (-1/4 + EulerGamma/2) *)
(*          + Sum_{k=3}^inf HZ(2k-3, 2)/k *)

(* where HZ = HurwitzZeta, HZ' = d/ds HurwitzZeta *)

(* k=0 contribution: *)
c0 = 2*N[Derivative[1, 0][HurwitzZeta][-3, 2], 30];

(* k=1 contribution: *)
c1 = N[HurwitzZeta[-1, 2], 30];

(* k=2 contribution (pole subtraction): *)
c2 = N[-1/4 + EulerGamma/2, 30];

(* k>=3 contribution: convergent sum *)
c3inf = Sum[N[HurwitzZeta[2*k - 3, 2]/k, 30], {k, 3, 200}];

Print["k=0: 2*HZ'(-3,2)  = ", c0];
Print["k=1: HZ(-1,2)     = ", c1];
Print["k=2: -1/4+gamma/2 = ", c2];
Print["k>=3: sum          = ", c3inf];
Print[""];

zetaPrime0_O0 = c0 + c1 + c2 + c3inf;
Print["zeta'(0; box, O(0)) on CP^2 = ", zetaPrime0_O0];
Print[""];

(* ============================================================ *)
(* Same for O(2) on CP^2 *)
(* ============================================================ *)

(* Spectrum: lambda_b = b(b+4) = (b+2)^2 - 4, mult = (b+1)(b+2)(b+3) *)
(* With m = b+2 >= 3: mult = (m-1)*m*(m+1) = m(m^2-1) = m^3 - m *)
(* lambda = m^2 - 4 *)

(* zeta(s; O(2)) = Sum_{m=3}^inf (m^3-m) / (m^2-4)^s *)

(* Expand (m^2-4)^{-s} = m^{-2s}(1-4/m^2)^{-s} *)
(* = m^{-2s} Sum_{k=0}^inf Pochhammer(s,k)/k! * (4/m^2)^k *)
(* = Sum_k Pochhammer(s,k)*4^k/k! * m^{-2s-2k} *)

(* So zeta(s) = Sum_k Pochhammer(s,k)*4^k/k! * *)
(*   [HurwitzZeta(2s+2k-3, 3) - HurwitzZeta(2s+2k-1, 3)] *)

(* Because m^3-m multiplied by m^{-2s-2k} = m^{3-2s-2k} - m^{1-2s-2k} *)

(* At s=0: *)
(* k=0: HZ(-3,3) - HZ(-1,3) *)
(* k=1 and beyond: need derivatives *)

(* k=0 term: 2 * [HZ'(-3,3) - HZ'(-1,3)] * 1 *)
(* (factor of 2 from d/ds of the HurwitzZeta argument 2s+...) *)
(* Wait, let me be more careful. *)

(* zeta(s) = Sum_k P(s,k)*4^k/k! * [HZ(2s+2k-3,3) - HZ(2s+2k-1,3)] *)

(* d/ds at s=0: *)
(* k=0: P'(0,0)*4^0/0! * [HZ(-3,3)-HZ(-1,3)] = 0 *)
(*     + P(0,0)*1 * 2*[HZ'(-3,3)-HZ'(-1,3)] = 2[HZ'(-3,3)-HZ'(-1,3)] *)
(* = 2*[HZ'(-3,3) - HZ'(-1,3)] *)

d0_O2 = 2*N[Derivative[1,0][HurwitzZeta][-3, 3] - Derivative[1,0][HurwitzZeta][-1, 3], 30];

(* k=1: d/ds [s * 4 * [HZ(2s-1,3) - HZ(2s+1,3)]] at s=0 *)
(* = 4 * [HZ(-1,3) - HZ(1,3)] + 0 *)
(* But HZ(1,3) diverges! Need pole subtraction. *)

(* HZ(2s-1, 3) at s=0 = HZ(-1, 3) — no pole, fine *)
(* HZ(2s+1, 3) at s=0 = HZ(1, 3) — POLE! *)

(* Near s=0: HZ(2s+1, 3) = 1/(2s) - psi(3) + O(s) *)
(* where psi(3) = 1 + 1/2 - EulerGamma = 3/2 - gamma *)

(* d/ds [s * 4 * (HZ(2s-1,3) - HZ(2s+1,3))]|_{s=0} *)
(* = 4 * [HZ(-1,3)] + s*4*2*HZ'(-1,3)|_{s=0} *)
(*   - 4*d/ds[s * HZ(2s+1,3)]|_{s=0} *)

(* d/ds [s * HZ(2s+1,3)]|_{s=0}: *)
(* s * HZ(2s+1,3) = s * [1/(2s) + ...] = 1/2 + s*(-psi(3)) + ... *)
(* d/ds = -psi(3) = -(3/2 - gamma_E) *)

d1_O2_part1 = 4*N[HurwitzZeta[-1, 3], 30];
d1_O2_part2 = -4*N[-(3/2 - EulerGamma), 30]; (* = 4*(3/2 - gamma) *)

d1_O2 = d1_O2_part1 + d1_O2_part2;

Print["O(2) contributions:"];
Print["  k=0: 2*(HZ'(-3,3)-HZ'(-1,3))    = ", d0_O2];
Print["  k=1 part a: 4*HZ(-1,3)           = ", d1_O2_part1];
Print["  k=1 part b: 4*(3/2-gamma)         = ", d1_O2_part2];
Print["  k=1 total:                         = ", d1_O2];

(* k=2: involves HZ(2s+1, 3) and HZ(2s+3, 3) *)
(* d/ds [s(s+1)/2 * 16 * (HZ(2s+1,3) - HZ(2s+3,3))]|_{s=0} *)
(* For HZ(2s+3,3): at s=0, HZ(3,3) = no pole, fine *)
(* For HZ(2s+1,3): pole, already handled *)

(* s(s+1)/2 * 16 * HZ(2s+1,3) = 16*s(s+1)/2 * [1/(2s) - psi(3) + ...] *)
(* = 16*(s+1)/4 - 16*s(s+1)/2*psi(3) + ... *)
(* = 4(s+1) - 8*s(s+1)*psi(3) + ... *)
(* At s=0: = 4 *)
(* d/ds at s=0: = 4 - 8*psi(3) = 4 - 8*(3/2-gamma) = 4 - 12 + 8*gamma = -8 + 8*gamma *)

d2_O2_pole = N[-8 + 8*EulerGamma, 30];

(* The non-pole part: s(s+1)/2 * 16 * (-HZ(2s+3,3)) *)
(* At s=0: 0 * (-HZ(3,3)) = 0 *)
(* d/ds: (1/2)*(-16)*HZ(3,3) = -8*HZ(3,3) *)

d2_O2_reg = -8*N[HurwitzZeta[3, 3], 30];

d2_O2 = d2_O2_pole + d2_O2_reg;
Print["  k=2 pole part: -8+8*gamma        = ", d2_O2_pole];
Print["  k=2 regular part: -8*HZ(3,3)      = ", d2_O2_reg];
Print["  k=2 total:                         = ", d2_O2];

(* k>=3: convergent sum *)
(* contribution = Sum_{k=3}^inf 4^k/k * [HZ(2k-3,3) - HZ(2k-1,3)] *)
d3inf_O2 = Sum[N[4^k/k*(HurwitzZeta[2*k-3, 3] - HurwitzZeta[2*k-1, 3]), 30], {k, 3, 100}];
Print["  k>=3: sum                          = ", d3inf_O2];

zetaPrime0_O2 = d0_O2 + d1_O2 + d2_O2 + d3inf_O2;
Print[""];
Print["zeta'(0; box, O(2)) on CP^2 = ", zetaPrime0_O2];
Print[""];

(* ============================================================ *)
(* DIFFERENCE *)
(* ============================================================ *)

zetaDiff = zetaPrime0_O0 - zetaPrime0_O2;
Print["==================================================="];
Print["ZETA DIFFERENCE ON CP^2"];
Print["==================================================="];
Print[""];
Print["zeta'(0; O(0)) = ", N[zetaPrime0_O0, 20]];
Print["zeta'(0; O(2)) = ", N[zetaPrime0_O2, 20]];
Print["Difference      = ", N[zetaDiff, 20]];
Print[""];

(* Torsion difference (sign: log T = -zeta' for the convention *)
(* where T = prod lambda^{-1/2} for each eigenvalue) *)
(* Actually, the analytic torsion T(S, L) = exp(-sum (-1)^q q zeta'(0; box_q, L) / 2) *)
(* For the THRESHOLD correction, we need zeta'(0; box_1, L), not box_0 *)

(* BUT: on a Kahler-Einstein surface, box_q and box_0 are related by: *)
(* box_q(L) = box_0(L tensor Lambda^q) + (curvature shift) *)

(* For q=1: box_1(L) on (0,1)-forms with values in L *)
(* The spectrum of box_1(O) on CP^2: *)
(* By Hodge duality and the Kodaira-Nakano identity, *)
(* the eigenvalues of box_1(O) on Omega^{0,1}(CP^2) are: *)
(* Lambda^{0,1} = Omega^1, which has spectrum related to the *)
(* scalar spectrum shifted by the Ricci curvature. *)

(* On a KE surface with Ric = lambda*omega: *)
(* box_1(O) eigenvalues = box_0(O) eigenvalues + lambda *)
(* (from the Bochner-Kodaira-Nakano formula) *)
(* Wait: this gives box_1 = nabla^*nabla + Ric = nabla^*nabla + lambda *)
(* but nabla^*nabla on (0,1)-forms is NOT the same as box_0 on functions *)

(* Actually, for KE: the eigenvalues of box_1 on CP^2 are: *)
(* mu_{a,b} = a(a+2) + b(b+2) + 3 for specific ranges *)
(* This is because Omega^1(CP^2) = Omega^1 decomposes under SU(3) *)

(* Let me sidestep this and use the relation: *)
(* zeta'(0; box_1, L) = zeta'(0; box_0, L tensor K) + correction *)
(* where K is the canonical bundle *)

(* On CP^2: K = O(-3), so L tensor K = L(-3) *)
(* For L = O: L tensor K = O(-3) *)
(* For L = L_Y: L tensor K = L_Y(-3) on CP^2 *)

(* Actually, this relation is for the SERRE DUALITY: *)
(* H^q(S, L) = H^{n-q}(S, K tensor L^{-1})^* *)
(* The spectra of box_q(L) and box_{n-q}(K tensor L^{-1}) *)
(* are the SAME (up to zero modes). *)

(* So for a surface (n=2): *)
(* box_1(L) and box_1(K tensor L^{-1}) have the same non-zero spectrum. *)

(* For L = O: box_1(O) has same spectrum as box_1(K) = box_1(O(-3)) *)
(* For L = O(2): box_1(O(2)) has same spectrum as box_1(O(-5)) *)

(* But we still don't know the box_1 spectrum explicitly. *)

(* IMPORTANT SIMPLIFICATION: *)
(* The THRESHOLD correction is proportional to the *)
(* SPECTRAL ASYMMETRY = eta invariant, not the full torsion. *)
(* But for the gauge kinetic function, it's the log det. *)

(* For now, let me just output the box_0 computation *)
(* and note that the box_1 computation needs additional work. *)

Print["NOTE: The above is for box_0 (scalar Laplacian on bundle sections)."];
Print["The threshold correction involves box_1 (on (0,1)-forms)."];
Print["These are related but not identical on CP^2."];
Print[""];

(* However, the DIFFERENCE box_0(O) - box_0(O(2)) gives us *)
(* the TOPOLOGICAL part of the torsion ratio, which is what *)
(* enters the blowup formula. *)

Print["==================================================="];
Print["TORSION RATIO ON dP_5 (box_0 approximation)"];
Print["==================================================="];
Print[""];

(* On dP_5: the torsion decomposes as: *)
(* log T(dP_5, L_Y) = log T(CP^2, O(2)) [base] + sum log T(E_i, L_Y|_{E_i}) [exceptional] *)
(* log T(dP_5, O) = log T(CP^2, O) [base] + sum log T(E_i, O) [exceptional] *)

(* Exceptional contribution: *)
(* L_Y|_{E1} = O(1), L_Y|_{E2} = O(1), L_Y|_{E3} = O(1) *)
(* L_Y|_{E4} = O(2), L_Y|_{E5} = O(0) *)
(* O|_{E_i} = O(0) for all i *)

(* log T(CP^1, O(k)) = -log(|k|!) for k != 0, 0 for k = 0 *)
(* So: log T(E_i, L_Y|_{E_i}) = {0, 0, 0, -log(2), 0} *)
(* log T(E_i, O) = 0 for all i *)

excDiff = Log[2]; (* = sum [log T(E_i, O) - log T(E_i, L_Y)] = 0-(-log2) = log2 *)

(* Total: *)
baseDiff = -zetaDiff; (* log T(CP^2, O) - log T(CP^2, O(2)) = -(zeta'(O) - zeta'(O(2))) *)

total = baseDiff + excDiff;
target = Log[3]/Sqrt[2];

Print["Base (CP^2):         ", N[baseDiff, 15]];
Print["Exceptional:         ", N[excDiff, 15]];
Print["Total:               ", N[total, 15]];
Print[""];
Print["Target ln(3)/sqrt(2): ", N[target, 15]];
Print["Ratio:                ", N[total/target, 15]];
Print["Difference:           ", N[total - target, 15]];
