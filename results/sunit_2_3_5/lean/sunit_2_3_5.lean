import Mathlib

/-! AXIOM S-unit certificate for `sunit_2_3_5`.

    S = [2, 3, 5]
    solutions = 17

    The solution list, the sum, coprimality and the explicit
    factorisations into primes of S are checked by Lean's kernel
    (`decide`).  Completeness of the list is computer-assisted and
    independently re-checked by `axiom.sunit.check`; it is NOT
    formalized in Lean.  This file says nothing about the abc
    conjecture. -/

set_option maxHeartbeats 400000

namespace AxiomSunit

def S : Finset ℕ := ({2, 3, 5} : Finset ℕ)

def solutions : List (ℕ × ℕ × ℕ) :=
  [(1, 1, 2), (1, 2, 3), (1, 3, 4), (1, 4, 5), (1, 5, 6), (1, 8, 9), (1, 9, 10), (1, 15, 16), (1, 24, 25), (1, 80, 81), (2, 3, 5), (2, 25, 27), (3, 5, 8), (3, 125, 128), (4, 5, 9), (5, 27, 32), (9, 16, 25)]

theorem solution_count : solutions.length = 17 := by
  decide

theorem sol_0 :
    (1 : ℕ) + 1 = 2 ∧ Nat.Coprime 1 1 ∧
    (1 : ℕ) = 1 ∧
    (1 : ℕ) = 1 ∧
    (2 : ℕ) = 2 ^ 1 ∧ (2 : ℕ) ∈ S := by
  decide

theorem sol_1 :
    (1 : ℕ) + 2 = 3 ∧ Nat.Coprime 1 2 ∧
    (1 : ℕ) = 1 ∧
    (2 : ℕ) = 2 ^ 1 ∧ (2 : ℕ) ∈ S ∧
    (3 : ℕ) = 3 ^ 1 ∧ (3 : ℕ) ∈ S := by
  decide

theorem sol_2 :
    (1 : ℕ) + 3 = 4 ∧ Nat.Coprime 1 3 ∧
    (1 : ℕ) = 1 ∧
    (3 : ℕ) = 3 ^ 1 ∧ (3 : ℕ) ∈ S ∧
    (4 : ℕ) = 2 ^ 2 ∧ (2 : ℕ) ∈ S := by
  decide

theorem sol_3 :
    (1 : ℕ) + 4 = 5 ∧ Nat.Coprime 1 4 ∧
    (1 : ℕ) = 1 ∧
    (4 : ℕ) = 2 ^ 2 ∧ (2 : ℕ) ∈ S ∧
    (5 : ℕ) = 5 ^ 1 ∧ (5 : ℕ) ∈ S := by
  decide

theorem sol_4 :
    (1 : ℕ) + 5 = 6 ∧ Nat.Coprime 1 5 ∧
    (1 : ℕ) = 1 ∧
    (5 : ℕ) = 5 ^ 1 ∧ (5 : ℕ) ∈ S ∧
    (6 : ℕ) = 2 ^ 1 * 3 ^ 1 ∧ (2 : ℕ) ∈ S ∧ (3 : ℕ) ∈ S := by
  decide

theorem sol_5 :
    (1 : ℕ) + 8 = 9 ∧ Nat.Coprime 1 8 ∧
    (1 : ℕ) = 1 ∧
    (8 : ℕ) = 2 ^ 3 ∧ (2 : ℕ) ∈ S ∧
    (9 : ℕ) = 3 ^ 2 ∧ (3 : ℕ) ∈ S := by
  decide

theorem sol_6 :
    (1 : ℕ) + 9 = 10 ∧ Nat.Coprime 1 9 ∧
    (1 : ℕ) = 1 ∧
    (9 : ℕ) = 3 ^ 2 ∧ (3 : ℕ) ∈ S ∧
    (10 : ℕ) = 2 ^ 1 * 5 ^ 1 ∧ (2 : ℕ) ∈ S ∧ (5 : ℕ) ∈ S := by
  decide

theorem sol_7 :
    (1 : ℕ) + 15 = 16 ∧ Nat.Coprime 1 15 ∧
    (1 : ℕ) = 1 ∧
    (15 : ℕ) = 3 ^ 1 * 5 ^ 1 ∧ (3 : ℕ) ∈ S ∧ (5 : ℕ) ∈ S ∧
    (16 : ℕ) = 2 ^ 4 ∧ (2 : ℕ) ∈ S := by
  decide

theorem sol_8 :
    (1 : ℕ) + 24 = 25 ∧ Nat.Coprime 1 24 ∧
    (1 : ℕ) = 1 ∧
    (24 : ℕ) = 2 ^ 3 * 3 ^ 1 ∧ (2 : ℕ) ∈ S ∧ (3 : ℕ) ∈ S ∧
    (25 : ℕ) = 5 ^ 2 ∧ (5 : ℕ) ∈ S := by
  decide

theorem sol_9 :
    (1 : ℕ) + 80 = 81 ∧ Nat.Coprime 1 80 ∧
    (1 : ℕ) = 1 ∧
    (80 : ℕ) = 2 ^ 4 * 5 ^ 1 ∧ (2 : ℕ) ∈ S ∧ (5 : ℕ) ∈ S ∧
    (81 : ℕ) = 3 ^ 4 ∧ (3 : ℕ) ∈ S := by
  decide

theorem sol_10 :
    (2 : ℕ) + 3 = 5 ∧ Nat.Coprime 2 3 ∧
    (2 : ℕ) = 2 ^ 1 ∧ (2 : ℕ) ∈ S ∧
    (3 : ℕ) = 3 ^ 1 ∧ (3 : ℕ) ∈ S ∧
    (5 : ℕ) = 5 ^ 1 ∧ (5 : ℕ) ∈ S := by
  decide

theorem sol_11 :
    (2 : ℕ) + 25 = 27 ∧ Nat.Coprime 2 25 ∧
    (2 : ℕ) = 2 ^ 1 ∧ (2 : ℕ) ∈ S ∧
    (25 : ℕ) = 5 ^ 2 ∧ (5 : ℕ) ∈ S ∧
    (27 : ℕ) = 3 ^ 3 ∧ (3 : ℕ) ∈ S := by
  decide

theorem sol_12 :
    (3 : ℕ) + 5 = 8 ∧ Nat.Coprime 3 5 ∧
    (3 : ℕ) = 3 ^ 1 ∧ (3 : ℕ) ∈ S ∧
    (5 : ℕ) = 5 ^ 1 ∧ (5 : ℕ) ∈ S ∧
    (8 : ℕ) = 2 ^ 3 ∧ (2 : ℕ) ∈ S := by
  decide

theorem sol_13 :
    (3 : ℕ) + 125 = 128 ∧ Nat.Coprime 3 125 ∧
    (3 : ℕ) = 3 ^ 1 ∧ (3 : ℕ) ∈ S ∧
    (125 : ℕ) = 5 ^ 3 ∧ (5 : ℕ) ∈ S ∧
    (128 : ℕ) = 2 ^ 7 ∧ (2 : ℕ) ∈ S := by
  decide

theorem sol_14 :
    (4 : ℕ) + 5 = 9 ∧ Nat.Coprime 4 5 ∧
    (4 : ℕ) = 2 ^ 2 ∧ (2 : ℕ) ∈ S ∧
    (5 : ℕ) = 5 ^ 1 ∧ (5 : ℕ) ∈ S ∧
    (9 : ℕ) = 3 ^ 2 ∧ (3 : ℕ) ∈ S := by
  decide

theorem sol_15 :
    (5 : ℕ) + 27 = 32 ∧ Nat.Coprime 5 27 ∧
    (5 : ℕ) = 5 ^ 1 ∧ (5 : ℕ) ∈ S ∧
    (27 : ℕ) = 3 ^ 3 ∧ (3 : ℕ) ∈ S ∧
    (32 : ℕ) = 2 ^ 5 ∧ (2 : ℕ) ∈ S := by
  decide

theorem sol_16 :
    (9 : ℕ) + 16 = 25 ∧ Nat.Coprime 9 16 ∧
    (9 : ℕ) = 3 ^ 2 ∧ (3 : ℕ) ∈ S ∧
    (16 : ℕ) = 2 ^ 4 ∧ (2 : ℕ) ∈ S ∧
    (25 : ℕ) = 5 ^ 2 ∧ (5 : ℕ) ∈ S := by
  decide

#print axioms solution_count
#print axioms sol_0

end AxiomSunit
