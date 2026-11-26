import Mathlib

/-!
# The abc conjecture: exact statement

This file fixes the statement that every abc-track claim must refer to.
It contains definitions and a trivial lemma only.  It does **not** prove the
abc conjecture.

The formulation is the Masser–Oesterlé form: for every `ε > 0` there is a
constant `K > 0` such that every coprime positive triple `a + b = c` satisfies

  `c ≤ K * rad(a*b*c)^(1+ε)`.

`FinitelyMany ε` is the equivalent form saying that for each `ε > 0` only
finitely many coprime triples have `c > rad(a*b*c)^(1+ε)`.  The equivalence is
standard (see e.g. Bombieri–Gubler, *Heights in Diophantine Geometry*, and
the survey by Nitaj); it is not formalized here.

The polynomial analogue is Mason–Stothers, already in Mathlib as
`Polynomial.abc` in `Mathlib.NumberTheory.FLT.MasonStothers`.  It does not
imply the integer statement.

No `sorry`, no new axioms, and no candidate proof is included in this file.
-/

noncomputable section

open scoped BigOperators

namespace Abc

/-- Product of the distinct prime divisors of `n` (the radical). -/
def rad (n : ℕ) : ℕ := n.primeFactors.prod id

/-- The quality `log c / log rad(a*b*c)` of a positive triple. -/
def quality (a b c : ℕ) : ℝ :=
  Real.log (c : ℝ) / Real.log (rad (a * b * c) : ℝ)

/-- The abc conjecture in the Masser–Oesterlé form. -/
def Statement : Prop :=
  ∀ ε : ℝ, 0 < ε → ∃ K : ℝ, 0 < K ∧
    ∀ a b c : ℕ, 0 < a → 0 < b → 0 < c → a + b = c →
      Nat.Coprime a b →
      (c : ℝ) ≤ K * (rad (a * b * c) : ℝ) ^ (1 + ε)

/-- The finitely-many-exceptions form of abc for a fixed `ε`. -/
def FinitelyMany (ε : ℝ) : Prop :=
  {t : ℕ × ℕ × ℕ |
    0 < t.1 ∧ 0 < t.2.1 ∧ 0 < t.2.2 ∧
    t.1 + t.2.1 = t.2.2 ∧ Nat.Coprime t.1 t.2.1 ∧
    (t.2.2 : ℝ) > (rad (t.1 * t.2.1 * t.2.2) : ℝ) ^ (1 + ε)}.Finite

/-- A trivial kernel check: the radical of `1` is `1`. -/
theorem rad_one : rad 1 = 1 := by
  simp [rad]

#check Statement
#check FinitelyMany
#check quality
#print axioms rad_one

end Abc
