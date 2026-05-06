(* ============================================================
   Track 20-AS-SF: AS-Modified Spectral Function
   Part 1: Parametrize f_AS and compute modified moments
   ============================================================ *)

Print["============================================================"];
Print["PART 1: AS-Modified Spectral Function -- Moment Computation"];
Print["============================================================\n"];

(* The standard spectral action uses: S = Tr[f(D^2/Lambda^2)]
   The spectral function f(x) is typically taken as a step function
   Theta(1-x), a smooth approximation thereof, or a Gaussian.

   The moments of f determine physical predictions:
   f_0 = Int_0^infty f(u) du          (gauge couplings)
   f_2 = Int_0^infty f(u) u du        (Higgs mass parameter)
   f_4 = Int_0^infty f(u) u^2 du      (cosmological constant)

   For the step function f(u) = Theta(1-u):
   f_0 = 1, f_2 = 1/2, f_4 = 1/3

   The AS modification suppresses UV modes near the Planck scale:
   f_AS(x) = f(x) * g_AS(x)
   g_AS(x) = 1 / (1 + (x/x_AS)^n)

   where x_AS is the transition scale in units of Lambda^2 and
   n is the steepness of the suppression.
*)

(* --- Step function spectral function --- *)
Print["Standard step function f(u) = Theta(1 - u):"];

f0std = 1;
f2std = 1/2;
f4std = 1/3;

Print["  f_0 = ", f0std];
Print["  f_2 = ", f2std, " = ", N[f2std]];
Print["  f_4 = ", f4std, " = ", N[f4std]];
Print["  f_2/f_0 = ", N[f2std/f0std]];
Print[""];

(* --- AS-modified moments with step function --- *)
Print["============================================================"];
Print["AS-modified moments: step function * AS suppression"];
Print["f_AS(u) = Theta(1-u) / (1 + (u/xAS)^n)"];
Print["============================================================\n"];

(* Grid of parameters *)
xASvals = {0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9, 1.0};
nvals = {2, 4, 6, 8, 10, 20};

(* === MOMENT RATIO f2/f0 === *)
Print["--- Moment ratio f_2_AS / f_0_AS for various (xAS, n) ---"];
Print["Standard (no AS): f_2/f_0 = ", N[f2std/f0std]];
Print[""];

header = "xAS";
Do[header = header <> "\tn=" <> ToString[nn], {nn, nvals}];
Print[header];

ratioTable = {};

Do[
  line = ToString[NumberForm[xAS, {4, 2}]];
  rowRatios = {};
  Do[
    f0as = NIntegrate[1/(1 + (u/xAS)^nn), {u, 0, 1}, WorkingPrecision -> 20, MaxRecursion -> 30];
    f2as = NIntegrate[u/(1 + (u/xAS)^nn), {u, 0, 1}, WorkingPrecision -> 20, MaxRecursion -> 30];
    ratio = f2as / f0as;
    AppendTo[rowRatios, ratio];
    line = line <> "\t" <> ToString[NumberForm[ratio, {6, 4}]];
  , {nn, nvals}];
  AppendTo[ratioTable, {xAS, rowRatios}];
  Print[line];
, {xAS, xASvals}];

Print["\n--- Reduction factor R = (f2_AS/f0_AS) / (f2/f0) ---"];
Print["R < 1 means AS LOWERS the Higgs mass"];
Print[""];

Print[header];
Do[
  xAS = ratioTable[[i, 1]];
  ratios = ratioTable[[i, 2]];
  line = ToString[NumberForm[xAS, {4, 2}]];
  Do[
    R = ratios[[j]] / (f2std / f0std);
    line = line <> "\t" <> ToString[NumberForm[R, {6, 4}]];
  , {j, Length[nvals]}];
  Print[line];
, {i, Length[ratioTable]}];

(* === INDIVIDUAL MOMENT SUPPRESSIONS === *)
Print["\n============================================================"];
Print["Individual moment suppressions"];
Print["============================================================\n"];

Print["f_0_AS / f_0:"];
Print[header];
Do[
  line = ToString[NumberForm[xAS, {4, 2}]];
  Do[
    f0as = NIntegrate[1/(1 + (u/xAS)^nn), {u, 0, 1}, WorkingPrecision -> 20, MaxRecursion -> 30];
    line = line <> "\t" <> ToString[NumberForm[f0as/f0std, {6, 4}]];
  , {nn, nvals}];
  Print[line];
, {xAS, xASvals}];

Print[""];
Print["f_2_AS / f_2:"];
Print[header];
Do[
  line = ToString[NumberForm[xAS, {4, 2}]];
  Do[
    f2as = NIntegrate[u/(1 + (u/xAS)^nn), {u, 0, 1}, WorkingPrecision -> 20, MaxRecursion -> 30];
    line = line <> "\t" <> ToString[NumberForm[f2as/f2std, {6, 4}]];
  , {nn, nvals}];
  Print[line];
, {xAS, xASvals}];

(* === DIFFERENTIAL SUPPRESSION === *)
Print["\n============================================================"];
Print["Differential suppression: (f2_AS/f2) / (f0_AS/f0)"];
Print["delta < 1 means f_2 suppressed MORE than f_0"];
Print["============================================================\n"];

Print[header];
Do[
  line = ToString[NumberForm[xAS, {4, 2}]];
  Do[
    f0as = NIntegrate[1/(1 + (u/xAS)^nn), {u, 0, 1}, WorkingPrecision -> 20, MaxRecursion -> 30];
    f2as = NIntegrate[u/(1 + (u/xAS)^nn), {u, 0, 1}, WorkingPrecision -> 20, MaxRecursion -> 30];
    delta = (f2as/f2std) / (f0as/f0std);
    line = line <> "\t" <> ToString[NumberForm[delta, {6, 4}]];
  , {nn, nvals}];
  Print[line];
, {xAS, xASvals}];

Print["\nRESULT: delta < 1 whenever xAS < 1 (AS transition below cutoff)."];
Print["AS suppression reduces f_2 MORE than f_0, so Higgs mass DECREASES."];
