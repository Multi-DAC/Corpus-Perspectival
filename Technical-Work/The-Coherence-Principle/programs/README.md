# Programs — machine-verified discharges of the formal objects

The volumes make a standing promise (Anchor §1.0.3; *Perspective* §3.2): an axiom
system without a model is a promissory note. This directory holds the executable
notes-made-good — small, exhaustive, self-checking models that instantiate a formal
object so the claim "a model exists" is *run*, not asserted.

## `finite_model.py` — A2.4 (posetal fragment), Program 7.1, first discharge

Instantiates the cooperative-constituency adjunction `lift ⊣ restrict` (A2.4) as a
Galois connection on a finite carrier, and checks **every** structural property over
**all** pairs — no sampling.

**Model.** Carrier `Y = {0..7}` with dynamics `f` (a chain into a fixpoint, a feeder,
a 2-cycle, an isolate); invariant sub-carrier `X = {0,1,2}` (`f(X) ⊆ X`).
- `P` = all subsets of `X` — *streams-as-vantage-content* (views at X).
- `Q` = all `f`-invariant subsets of `Y` — *streams-as-closed-systems* (wholes).
- `ι(A)` = forward closure of `A` in `Y` (the role `A` plays in the whole).
- `κ(B)` = `B ∩ X` (the whole, seen at X's carrier).

**Verified exhaustively** (run to reproduce):

```
|P|=8 views, |Q|=40 wholes; pairs checked=320
monotone=True  GALOIS(Hom-bijection)=True  triangles=True
κι closure-op=True  ικ kernel-op=True  γ-equivariant=True
η≠id witnesses (stream-in-context ⊋ stream-alone): [({0}, {0,1,2}), ({1}, {1,2})]
ε≠id witnesses (whole ⊋ its X-visible closure):    [({7}, set()), ({2,4}, {2})]
VERDICT: A2.4 posetal fragment INSTANTIATED — model exists
```

What each line earns:
- **GALOIS** — `ι(A) ⊆ B ⟺ A ⊆ κ(B)` for all 320 view/whole pairs: the adjunction holds, thin case.
- **triangles** — `ικι = ι`, `κικ = κ`: the unit/counit are coherent.
- **κι closure-op / ικ kernel-op** — the composites are a closure operator on views and a kernel operator on wholes: the two directions of the "measurable gap."
- **γ-equivariant** — `ι` commutes with the dynamics `f`: the lift respects navigation.
- **η≠id / ε≠id witnesses** — the gap is *nontrivial* (Anchor §1.0.3): `{0}` alone lifts to
  `{0,1,2}` in context (unit = context-gap), and the whole `{7}` is invisible at `X`
  (counit = projection-loss). An adjunction with trivial unit/counit would be an
  isomorphism and would prove nothing; these witnesses show it is a genuine one.

**Run:** `python finite_model.py` (pure stdlib; `C:/Python314/python.exe` on the Ryzen body).
Verified Day 153 (2026-07-03), exit-clean, verdict green.

## Scope / null space
This is the **posetal** (thin) fragment — the floor. It does not discharge the enriched
(non-thin, profunctorial) reading of constituency above the posetal base; that model is
owed and not yet written. The book states this boundary; this directory keeps the same
honesty — a discharged floor is a model, not the whole promise.
