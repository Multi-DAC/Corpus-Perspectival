(*
  Scalar Laplacian spectral zeta on CP^2 with O(k) bundles
  Computes zeta'_0(0; O(k)) via Pochhammer/Hurwitz expansion

  Eigenvalues: lambda = u^2 + c, c = k^2/12 - 1
  Multiplicity: d = u(u^2 - k^2/4)
  u = p + (k+2)/2, p = 0,1,2,...

  zeta(s;k) = Sum_j (-c)^j Poch(s,j)/j! * [H(2s+2j-3,a) - k^2/4 H(2s+2j-1,a)]
  where a = (k+2)/2 for k>0, a = 2 for k=0
*)

Print["============================================================"];
Print["SCALAR LAPLACIAN zeta'_0(0; O(k)) ON CP^2"];
Print["============================================================"];

$MaxExtraPrecision = 500;

scalarZetaPrime[k_Integer] := Module[
  {c, a, result, maxJ = 200, jj, mc, sVal1, sVal2, contrib,
   kSq4, fullTerm, pochDeriv},

  c = k^2/12 - 1;
  a = If[k == 0, 2, (k + 2)/2];
  kSq4 = k^2/4;

  result = 0;

  Do[
    mc = (-c)^jj;
    sVal1 = 2 jj - 3;  (* arg of first Hurwitz at s=0 *)
    sVal2 = 2 jj - 1;  (* arg of second Hurwitz at s=0 *)

    Which[
      (* j = 0: poch_val = 1, poch_deriv = 0 *)
      (* contribution = d/ds[H(2s-3,a) - k^2/4 H(2s-1,a)]|_{s=0} *)
      jj == 0,
      contrib = mc * (
        2 * Derivative[1, 0][HurwitzZeta][-3, a] -
        If[k > 0, kSq4 * 2 * Derivative[1, 0][HurwitzZeta][-1, a], 0]
      ),

      (* j = 1: poch_val = 0, poch_deriv = 1 *)
      (* sVal1 = -1, sVal2 = 1 (POLE!) *)
      jj == 1,
      (* Handle the pole in H(2s+1, a) at s=0 *)
      (* The product s * H(2s+1, a) is finite at s=0 *)
      (* s * H(1+2s, a) = s * [1/(2s) + ... ] = 1/2 + ... *)
      (* So poch_deriv * H(sVal1, a) - k^2/4 * [limit of s*H(sVal2,a)] *)
      (* = 1 * H(-1, a) - k^2/4 * [value at s=0 of s*H(1+2s,a)] *)
      (* But we need d/ds of the FULL product at s=0 *)
      (* Use numerical differentiation *)
      fullTerm[s_] := (
        s * (HurwitzZeta[2s + 2 - 3, a] -
             If[k > 0, kSq4 * HurwitzZeta[2s + 2 - 1, a], 0])
      );
      contrib = mc * N[D[fullTerm[s], s] /. s -> 0, 40],

      (* j = 2: poch_deriv = 1/2, sVal1 = 1 (POLE!), sVal2 = 3 *)
      jj == 2,
      fullTerm[s_] := (
        s (s + 1)/2 * (HurwitzZeta[2s + 4 - 3, a] -
                        If[k > 0, kSq4 * HurwitzZeta[2s + 4 - 1, a], 0])
      );
      contrib = mc * N[D[fullTerm[s], s] /. s -> 0, 40],

      (* j >= 3: no poles (sVal1 >= 3, sVal2 >= 5), poch_deriv = 1/j *)
      True,
      pochDeriv = 1/jj;
      contrib = mc * pochDeriv * (
        N[HurwitzZeta[sVal1, a], 40] -
        If[k > 0, kSq4 * N[HurwitzZeta[sVal2, a], 40], 0]
      )
    ];

    result += N[contrib, 40];

    (* Check convergence *)
    If[jj > 10 && Abs[N[contrib]] < 10^(-35),
      Print["  O(", k, "): converged at j=", jj];
      Break[]
    ],

    {jj, 0, maxJ}
  ];

  result
];

(* Compute for each needed k *)
Print[""];
kValues = {0, 2, 3, 5, 8};
results = Association[];

Do[
  Print["Computing zeta'_0(0; O(", k, "))..."];
  val = scalarZetaPrime[k];
  results[k] = val;
  Print["  zeta'_0(0; O(", k, ")) = ", N[val, 30]];
  Print[""],
  {k, kValues}
];

(* ============================================================ *)
(* ASSEMBLY: f(O(k)) and threshold                              *)
(* ============================================================ *)

Print[""];
Print["============================================================"];
Print["PARTIAL ASSEMBLY (scalar part only)"];
Print["============================================================"];

(* f(O(k)) = zeta'_0(O(k)) - zeta'_1(O(k)) + zeta'_0(O(-3-k)) *)
(* Using O(-m) = O(m) symmetry for zeta'_0 *)
(* zeta'_0(O(-3)) = zeta'_0(O(3)), etc. *)

(* For now, report the scalar contributions *)
(* f_scalar(O(k)) = zeta'_0(O(k)) + zeta'_0(O(|3+k|)) *)
(* (missing the -zeta'_1 term) *)

fScalar0 = results[0] + results[3];
fScalar5 = results[5] + results[8];
fScalarm5 = results[5] + results[2];

Print["f_scalar(O(0))  = zeta'_0(O(0)) + zeta'_0(O(3))  = ", N[fScalar0, 25]];
Print["f_scalar(O(5))  = zeta'_0(O(5)) + zeta'_0(O(8))  = ", N[fScalar5, 25]];
Print["f_scalar(O(-5)) = zeta'_0(O(5)) + zeta'_0(O(2))  = ", N[fScalarm5, 25]];

thresholdScalar = fScalar0 + 5/12 * (fScalar5 + fScalarm5);
target = Log[3]/Sqrt[2];

Print[""];
Print["Scalar contribution to threshold = ", N[thresholdScalar, 25]];
Print["Target ln(3)/sqrt(2) = ", N[target, 25]];
Print[""];
Print["NOTE: Full threshold = scalar part - (0,1)-form part."];
Print["The (0,1)-form zeta'_1 values must be computed separately (SageMath branching)."];
Print[""];

(* Also report individual values for cross-checking *)
Print["============================================================"];
Print["INDIVIDUAL VALUES"];
Print["============================================================"];
Do[
  Print["zeta'_0(0; O(", k, ")) = ", N[results[k], 30]],
  {k, kValues}
];
Print[""];
Print["Cross-checks:"];
Print["zeta'_0(0; O(0)) should relate to known CP^2 spectral determinant"];
Print["For O(0): eigenvalues p(p+2), mult (p+1)^3, p=0,1,2,..."];
