import Mathlib

/-! AXIOM swarm export for `sierpinski_5n`.
    Statement: forall n >= 2: exists x >= 1: exists y >= 1: exists z >= 1: 5/n = 1/x + 1/y + 1/z
    Class lemmas only (denominator-cleared form). The reduction step is not
    formalized in Lean yet. -/

set_option maxHeartbeats 400000

/-- class n = 5k + 2, k = m + 0. Witnesses: ['10*k**2 + 9*k + 2', '2*k + 1', '2*k + 1'] -/
theorem cls_5_2 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(5*(m:ℤ) + 2)*x*y - (5*(m:ℤ) + 2)*x*z - (5*(m:ℤ) + 2)*y*z + 5*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨(10*(m:ℤ)^2 + 9*(m:ℤ) + 2), (2*(m:ℤ) + 1), (2*(m:ℤ) + 1), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring

/-- class n = 5k + 4, k = m + 0. Witnesses: ['k + 1', '5*k**2 + 9*k + 5', '25*k**4 + 90*k**3 + 126*k**2 + 81*k + 20'] -/
theorem cls_5_4 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(5*(m:ℤ) + 4)*x*y - (5*(m:ℤ) + 4)*x*z - (5*(m:ℤ) + 4)*y*z + 5*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨((m:ℤ) + 1), (5*(m:ℤ)^2 + 9*(m:ℤ) + 5), (25*(m:ℤ)^4 + 90*(m:ℤ)^3 + 126*(m:ℤ)^2 + 81*(m:ℤ) + 20), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring

/-- class n = 5k + 3, k = m + 0. Witnesses: ['5*k**2 + 8*k + 3', '5*k**2 + 8*k + 3', 'k + 1'] -/
theorem cls_5_3 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(5*(m:ℤ) + 3)*x*y - (5*(m:ℤ) + 3)*x*z - (5*(m:ℤ) + 3)*y*z + 5*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨(5*(m:ℤ)^2 + 8*(m:ℤ) + 3), (5*(m:ℤ)^2 + 8*(m:ℤ) + 3), ((m:ℤ) + 1), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring

/-- class n = 60k + 11, k = m + 0. Witnesses: ['60*k + 11', '15*k + 3', '900*k**2 + 345*k + 33'] -/
theorem cls_60_11 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(60*(m:ℤ) + 11)*x*y - (60*(m:ℤ) + 11)*x*z - (60*(m:ℤ) + 11)*y*z + 5*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨(60*(m:ℤ) + 11), (15*(m:ℤ) + 3), (900*(m:ℤ)^2 + 345*(m:ℤ) + 33), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring

/-- class n = 60k + 31, k = m + 0. Witnesses: ['60*k + 31', '15*k + 8', '900*k**2 + 945*k + 248'] -/
theorem cls_60_31 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(60*(m:ℤ) + 31)*x*y - (60*(m:ℤ) + 31)*x*z - (60*(m:ℤ) + 31)*y*z + 5*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨(60*(m:ℤ) + 31), (15*(m:ℤ) + 8), (900*(m:ℤ)^2 + 945*(m:ℤ) + 248), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring

/-- class n = 10k + 7, k = m + 0. Witnesses: ['2*k + 2', '20*k**2 + 34*k + 14', '10*k**2 + 17*k + 7'] -/
theorem cls_10_7 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(10*(m:ℤ) + 7)*x*y - (10*(m:ℤ) + 7)*x*z - (10*(m:ℤ) + 7)*y*z + 5*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨(2*(m:ℤ) + 2), (20*(m:ℤ)^2 + 34*(m:ℤ) + 14), (10*(m:ℤ)^2 + 17*(m:ℤ) + 7), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring

/-- class n = 30k + 11, k = m + 0. Witnesses: ['180*k**2 + 156*k + 33', '6*k + 3', '60*k**2 + 52*k + 11'] -/
theorem cls_30_11 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(30*(m:ℤ) + 11)*x*y - (30*(m:ℤ) + 11)*x*z - (30*(m:ℤ) + 11)*y*z + 5*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨(180*(m:ℤ)^2 + 156*(m:ℤ) + 33), (6*(m:ℤ) + 3), (60*(m:ℤ)^2 + 52*(m:ℤ) + 11), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring

/-- class n = 5k + 0, k = m + 1. Witnesses: ['2*k + 1', '2*k', '4*k**2 + 2*k'] -/
theorem cls_5_0 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(5*(m:ℤ) + 5)*x*y - (5*(m:ℤ) + 5)*x*z - (5*(m:ℤ) + 5)*y*z + 5*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨(2*(m:ℤ) + 3), (2*(m:ℤ) + 2), (4*(m:ℤ)^2 + 10*(m:ℤ) + 6), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring

/-- class n = 10k + 2, k = m + 0. Witnesses: ['10*k + 2', '5*k + 1', '5*k + 1'] -/
theorem cls_10_2 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(10*(m:ℤ) + 2)*x*y - (10*(m:ℤ) + 2)*x*z - (10*(m:ℤ) + 2)*y*z + 5*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨(10*(m:ℤ) + 2), (5*(m:ℤ) + 1), (5*(m:ℤ) + 1), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring

/-- class n = 420k + 241, k = m + 0. Witnesses: ['84*k + 49', '44452800*k**4 + 102876480*k**3 + 89288892*k**2 + 34445250*k + 4983398', '8820*k**2 + 10206*k + 2954'] -/
theorem cls_420_241 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(420*(m:ℤ) + 241)*x*y - (420*(m:ℤ) + 241)*x*z - (420*(m:ℤ) + 241)*y*z + 5*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨(84*(m:ℤ) + 49), (44452800*(m:ℤ)^4 + 102876480*(m:ℤ)^3 + 89288892*(m:ℤ)^2 + 34445250*(m:ℤ) + 4983398), (8820*(m:ℤ)^2 + 10206*(m:ℤ) + 2954), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring

/-- class n = 420k + 61, k = m + 0. Witnesses: ['84*k + 14', '5040*k**2 + 1572*k + 122', '17640*k**2 + 5502*k + 427'] -/
theorem cls_420_61 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(420*(m:ℤ) + 61)*x*y - (420*(m:ℤ) + 61)*x*z - (420*(m:ℤ) + 61)*y*z + 5*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨(84*(m:ℤ) + 14), (5040*(m:ℤ)^2 + 1572*(m:ℤ) + 122), (17640*(m:ℤ)^2 + 5502*(m:ℤ) + 427), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring

/-- class n = 840k + 121, k = m + 0. Witnesses: ['168*k + 27', '10080*k**2 + 3072*k + 234', '158054400*k**4 + 96337920*k**3 + 22008224*k**2 + 2233344*k + 84942'] -/
theorem cls_840_121 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(840*(m:ℤ) + 121)*x*y - (840*(m:ℤ) + 121)*x*z - (840*(m:ℤ) + 121)*y*z + 5*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨(168*(m:ℤ) + 27), (10080*(m:ℤ)^2 + 3072*(m:ℤ) + 234), (158054400*(m:ℤ)^4 + 96337920*(m:ℤ)^3 + 22008224*(m:ℤ)^2 + 2233344*(m:ℤ) + 84942), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring

/-- class n = 840k + 361, k = m + 0. Witnesses: ['168*k + 75', '10080*k**2 + 8832*k + 1934', '1422489600*k**4 + 2492743680*k**3 + 1637901216*k**2 + 478261632*k + 52363050'] -/
theorem cls_840_361 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(840*(m:ℤ) + 361)*x*y - (840*(m:ℤ) + 361)*x*z - (840*(m:ℤ) + 361)*y*z + 5*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨(168*(m:ℤ) + 75), (10080*(m:ℤ)^2 + 8832*(m:ℤ) + 1934), (1422489600*(m:ℤ)^4 + 2492743680*(m:ℤ)^3 + 1637901216*(m:ℤ)^2 + 478261632*(m:ℤ) + 52363050), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring

/-- class n = 840k + 541, k = m + 0. Witnesses: ['168*k + 111', '10080*k**2 + 13152*k + 4290', '158054400*k**4 + 412446720*k**3 + 403596704*k**2 + 175522208*k + 28624310'] -/
theorem cls_840_541 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(840*(m:ℤ) + 541)*x*y - (840*(m:ℤ) + 541)*x*z - (840*(m:ℤ) + 541)*y*z + 5*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨(168*(m:ℤ) + 111), (10080*(m:ℤ)^2 + 13152*(m:ℤ) + 4290), (158054400*(m:ℤ)^4 + 412446720*(m:ℤ)^3 + 403596704*(m:ℤ)^2 + 175522208*(m:ℤ) + 28624310), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring

/-- class n = 840k + 781, k = m + 0. Witnesses: ['168*k + 159', '10080*k**2 + 18912*k + 8870', '1422489600*k**4 + 5337722880*k**3 + 7510751136*k**2 + 4696965408*k + 1101467730'] -/
theorem cls_840_781 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(840*(m:ℤ) + 781)*x*y - (840*(m:ℤ) + 781)*x*z - (840*(m:ℤ) + 781)*y*z + 5*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨(168*(m:ℤ) + 159), (10080*(m:ℤ)^2 + 18912*(m:ℤ) + 8870), (1422489600*(m:ℤ)^4 + 5337722880*(m:ℤ)^3 + 7510751136*(m:ℤ)^2 + 4696965408*(m:ℤ) + 1101467730), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring
