import Mathlib

/-! AXIOM swarm export for `erdos_straus`.
    Statement: forall n >= 2: exists x >= 1: exists y >= 1: exists z >= 1: 4/n = 1/x + 1/y + 1/z
    Class lemmas only (denominator-cleared form). The reduction step is not
    formalized in Lean yet. -/

set_option maxHeartbeats 400000

/-- class n = 12k + 5, k = m + 0. Witnesses: ['12*k + 5', '4*k + 2', '48*k**2 + 44*k + 10'] -/
theorem cls_12_5 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(12*(m:ℤ) + 5)*x*y - (12*(m:ℤ) + 5)*x*z - (12*(m:ℤ) + 5)*y*z + 4*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨(12*(m:ℤ) + 5), (4*(m:ℤ) + 2), (48*(m:ℤ)^2 + 44*(m:ℤ) + 10), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring

/-- class n = 840k + 709, k = m + 0. Witnesses: ['88200*k**2 + 149205*k + 63101', '210*k + 178', '176400*k**2 + 298410*k + 126202'] -/
theorem cls_840_709 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(840*(m:ℤ) + 709)*x*y - (840*(m:ℤ) + 709)*x*z - (840*(m:ℤ) + 709)*y*z + 4*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨(88200*(m:ℤ)^2 + 149205*(m:ℤ) + 63101), (210*(m:ℤ) + 178), (176400*(m:ℤ)^2 + 298410*(m:ℤ) + 126202), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring

/-- class n = 60k + 13, k = m + 0. Witnesses: ['2700*k**2 + 1185*k + 130', '90*k + 20', '18*k + 4'] -/
theorem cls_60_13 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(60*(m:ℤ) + 13)*x*y - (60*(m:ℤ) + 13)*x*z - (60*(m:ℤ) + 13)*y*z + 4*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨(2700*(m:ℤ)^2 + 1185*(m:ℤ) + 130), (90*(m:ℤ) + 20), (18*(m:ℤ) + 4), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring

/-- class n = 4k + 3, k = m + 0. Witnesses: ['2*k + 2', '2*k + 2', '4*k**2 + 7*k + 3'] -/
theorem cls_4_3 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(4*(m:ℤ) + 3)*x*y - (4*(m:ℤ) + 3)*x*z - (4*(m:ℤ) + 3)*y*z + 4*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨(2*(m:ℤ) + 2), (2*(m:ℤ) + 2), (4*(m:ℤ)^2 + 7*(m:ℤ) + 3), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring

/-- class n = 840k + 613, k = m + 0. Witnesses: ['210*k + 154', '176400*k**2 + 258090*k + 94402', '88200*k**2 + 129045*k + 47201'] -/
theorem cls_840_613 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(840*(m:ℤ) + 613)*x*y - (840*(m:ℤ) + 613)*x*z - (840*(m:ℤ) + 613)*y*z + 4*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨(210*(m:ℤ) + 154), (176400*(m:ℤ)^2 + 258090*(m:ℤ) + 94402), (88200*(m:ℤ)^2 + 129045*(m:ℤ) + 47201), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring

/-- class n = 420k + 253, k = m + 0. Witnesses: ['105*k + 65', '6300*k**2 + 7695*k + 2350', '55566000*k**4 + 135739800*k**3 + 124345935*k**2 + 50625405*k + 7729150'] -/
theorem cls_420_253 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(420*(m:ℤ) + 253)*x*y - (420*(m:ℤ) + 253)*x*z - (420*(m:ℤ) + 253)*y*z + 4*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨(105*(m:ℤ) + 65), (6300*(m:ℤ)^2 + 7695*(m:ℤ) + 2350), (55566000*(m:ℤ)^4 + 135739800*(m:ℤ)^3 + 124345935*(m:ℤ)^2 + 50625405*(m:ℤ) + 7729150), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring

/-- class n = 60k + 37, k = m + 0. Witnesses: ['15*k + 10', '300*k**2 + 385*k + 125', '54000*k**4 + 138600*k**3 + 133635*k**2 + 57365*k + 9250'] -/
theorem cls_60_37 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(60*(m:ℤ) + 37)*x*y - (60*(m:ℤ) + 37)*x*z - (60*(m:ℤ) + 37)*y*z + 4*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨(15*(m:ℤ) + 10), (300*(m:ℤ)^2 + 385*(m:ℤ) + 125), (54000*(m:ℤ)^4 + 138600*(m:ℤ)^3 + 133635*(m:ℤ)^2 + 57365*(m:ℤ) + 9250), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring

/-- class n = 420k + 13, k = m + 0. Witnesses: ['105*k + 5', '6300*k**2 + 495*k + 10', '55566000*k**4 + 8731800*k**3 + 513135*k**2 + 13365*k + 130'] -/
theorem cls_420_13 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(420*(m:ℤ) + 13)*x*y - (420*(m:ℤ) + 13)*x*z - (420*(m:ℤ) + 13)*y*z + 4*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨(105*(m:ℤ) + 5), (6300*(m:ℤ)^2 + 495*(m:ℤ) + 10), (55566000*(m:ℤ)^4 + 8731800*(m:ℤ)^3 + 513135*(m:ℤ)^2 + 13365*(m:ℤ) + 130), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring

/-- class n = 840k + 541, k = m + 0. Witnesses: ['210*k + 136', '176400*k**2 + 227850*k + 73576', '88200*k**2 + 113925*k + 36788'] -/
theorem cls_840_541 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(840*(m:ℤ) + 541)*x*y - (840*(m:ℤ) + 541)*x*z - (840*(m:ℤ) + 541)*y*z + 4*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨(210*(m:ℤ) + 136), (176400*(m:ℤ)^2 + 227850*(m:ℤ) + 73576), (88200*(m:ℤ)^2 + 113925*(m:ℤ) + 36788), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring

/-- class n = 840k + 229, k = m + 0. Witnesses: ['210*k + 58', '176400*k**2 + 96810*k + 13282', '88200*k**2 + 48405*k + 6641'] -/
theorem cls_840_229 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(840*(m:ℤ) + 229)*x*y - (840*(m:ℤ) + 229)*x*z - (840*(m:ℤ) + 229)*y*z + 4*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨(210*(m:ℤ) + 58), (176400*(m:ℤ)^2 + 96810*(m:ℤ) + 13282), (88200*(m:ℤ)^2 + 48405*(m:ℤ) + 6641), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring

/-- class n = 4k + 2, k = m + 0. Witnesses: ['4*k + 2', '4*k + 2', '2*k + 1'] -/
theorem cls_4_2 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(4*(m:ℤ) + 2)*x*y - (4*(m:ℤ) + 2)*x*z - (4*(m:ℤ) + 2)*y*z + 4*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨(4*(m:ℤ) + 2), (4*(m:ℤ) + 2), (2*(m:ℤ) + 1), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring

/-- class n = 840k + 13, k = m + 0. Witnesses: ['210*k + 4', '176400*k**2 + 6090*k + 52', '88200*k**2 + 3045*k + 26'] -/
theorem cls_840_13 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(840*(m:ℤ) + 13)*x*y - (840*(m:ℤ) + 13)*x*z - (840*(m:ℤ) + 13)*y*z + 4*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨(210*(m:ℤ) + 4), (176400*(m:ℤ)^2 + 6090*(m:ℤ) + 52), (88200*(m:ℤ)^2 + 3045*(m:ℤ) + 26), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring

/-- class n = 840k + 37, k = m + 0. Witnesses: ['210*k + 10', '176400*k**2 + 16170*k + 370', '88200*k**2 + 8085*k + 185'] -/
theorem cls_840_37 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(840*(m:ℤ) + 37)*x*y - (840*(m:ℤ) + 37)*x*z - (840*(m:ℤ) + 37)*y*z + 4*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨(210*(m:ℤ) + 10), (176400*(m:ℤ)^2 + 16170*(m:ℤ) + 370), (88200*(m:ℤ)^2 + 8085*(m:ℤ) + 185), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring

/-- class n = 840k + 61, k = m + 0. Witnesses: ['210*k + 16', '176400*k**2 + 26250*k + 976', '88200*k**2 + 13125*k + 488'] -/
theorem cls_840_61 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(840*(m:ℤ) + 61)*x*y - (840*(m:ℤ) + 61)*x*z - (840*(m:ℤ) + 61)*y*z + 4*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨(210*(m:ℤ) + 16), (176400*(m:ℤ)^2 + 26250*(m:ℤ) + 976), (88200*(m:ℤ)^2 + 13125*(m:ℤ) + 488), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring

/-- class n = 840k + 109, k = m + 0. Witnesses: ['210*k + 28', '176400*k**2 + 46410*k + 3052', '88200*k**2 + 23205*k + 1526'] -/
theorem cls_840_109 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(840*(m:ℤ) + 109)*x*y - (840*(m:ℤ) + 109)*x*z - (840*(m:ℤ) + 109)*y*z + 4*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨(210*(m:ℤ) + 28), (176400*(m:ℤ)^2 + 46410*(m:ℤ) + 3052), (88200*(m:ℤ)^2 + 23205*(m:ℤ) + 1526), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring

/-- class n = 840k + 157, k = m + 0. Witnesses: ['210*k + 40', '176400*k**2 + 66570*k + 6280', '88200*k**2 + 33285*k + 3140'] -/
theorem cls_840_157 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(840*(m:ℤ) + 157)*x*y - (840*(m:ℤ) + 157)*x*z - (840*(m:ℤ) + 157)*y*z + 4*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨(210*(m:ℤ) + 40), (176400*(m:ℤ)^2 + 66570*(m:ℤ) + 6280), (88200*(m:ℤ)^2 + 33285*(m:ℤ) + 3140), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring

/-- class n = 840k + 181, k = m + 0. Witnesses: ['210*k + 46', '176400*k**2 + 76650*k + 8326', '88200*k**2 + 38325*k + 4163'] -/
theorem cls_840_181 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(840*(m:ℤ) + 181)*x*y - (840*(m:ℤ) + 181)*x*z - (840*(m:ℤ) + 181)*y*z + 4*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨(210*(m:ℤ) + 46), (176400*(m:ℤ)^2 + 76650*(m:ℤ) + 8326), (88200*(m:ℤ)^2 + 38325*(m:ℤ) + 4163), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring

/-- class n = 840k + 253, k = m + 0. Witnesses: ['210*k + 64', '176400*k**2 + 106890*k + 16192', '88200*k**2 + 53445*k + 8096'] -/
theorem cls_840_253 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(840*(m:ℤ) + 253)*x*y - (840*(m:ℤ) + 253)*x*z - (840*(m:ℤ) + 253)*y*z + 4*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨(210*(m:ℤ) + 64), (176400*(m:ℤ)^2 + 106890*(m:ℤ) + 16192), (88200*(m:ℤ)^2 + 53445*(m:ℤ) + 8096), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring

/-- class n = 840k + 277, k = m + 0. Witnesses: ['210*k + 70', '176400*k**2 + 116970*k + 19390', '88200*k**2 + 58485*k + 9695'] -/
theorem cls_840_277 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(840*(m:ℤ) + 277)*x*y - (840*(m:ℤ) + 277)*x*z - (840*(m:ℤ) + 277)*y*z + 4*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨(210*(m:ℤ) + 70), (176400*(m:ℤ)^2 + 116970*(m:ℤ) + 19390), (88200*(m:ℤ)^2 + 58485*(m:ℤ) + 9695), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring

/-- class n = 840k + 349, k = m + 0. Witnesses: ['210*k + 88', '176400*k**2 + 147210*k + 30712', '88200*k**2 + 73605*k + 15356'] -/
theorem cls_840_349 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(840*(m:ℤ) + 349)*x*y - (840*(m:ℤ) + 349)*x*z - (840*(m:ℤ) + 349)*y*z + 4*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨(210*(m:ℤ) + 88), (176400*(m:ℤ)^2 + 147210*(m:ℤ) + 30712), (88200*(m:ℤ)^2 + 73605*(m:ℤ) + 15356), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring

/-- class n = 840k + 373, k = m + 0. Witnesses: ['210*k + 94', '176400*k**2 + 157290*k + 35062', '88200*k**2 + 78645*k + 17531'] -/
theorem cls_840_373 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(840*(m:ℤ) + 373)*x*y - (840*(m:ℤ) + 373)*x*z - (840*(m:ℤ) + 373)*y*z + 4*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨(210*(m:ℤ) + 94), (176400*(m:ℤ)^2 + 157290*(m:ℤ) + 35062), (88200*(m:ℤ)^2 + 78645*(m:ℤ) + 17531), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring

/-- class n = 840k + 397, k = m + 0. Witnesses: ['210*k + 100', '176400*k**2 + 167370*k + 39700', '88200*k**2 + 83685*k + 19850'] -/
theorem cls_840_397 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(840*(m:ℤ) + 397)*x*y - (840*(m:ℤ) + 397)*x*z - (840*(m:ℤ) + 397)*y*z + 4*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨(210*(m:ℤ) + 100), (176400*(m:ℤ)^2 + 167370*(m:ℤ) + 39700), (88200*(m:ℤ)^2 + 83685*(m:ℤ) + 19850), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring

/-- class n = 840k + 421, k = m + 0. Witnesses: ['210*k + 106', '176400*k**2 + 177450*k + 44626', '88200*k**2 + 88725*k + 22313'] -/
theorem cls_840_421 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(840*(m:ℤ) + 421)*x*y - (840*(m:ℤ) + 421)*x*z - (840*(m:ℤ) + 421)*y*z + 4*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨(210*(m:ℤ) + 106), (176400*(m:ℤ)^2 + 177450*(m:ℤ) + 44626), (88200*(m:ℤ)^2 + 88725*(m:ℤ) + 22313), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring

/-- class n = 840k + 493, k = m + 0. Witnesses: ['210*k + 124', '176400*k**2 + 207690*k + 61132', '88200*k**2 + 103845*k + 30566'] -/
theorem cls_840_493 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(840*(m:ℤ) + 493)*x*y - (840*(m:ℤ) + 493)*x*z - (840*(m:ℤ) + 493)*y*z + 4*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨(210*(m:ℤ) + 124), (176400*(m:ℤ)^2 + 207690*(m:ℤ) + 61132), (88200*(m:ℤ)^2 + 103845*(m:ℤ) + 30566), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring

/-- class n = 840k + 517, k = m + 0. Witnesses: ['210*k + 130', '176400*k**2 + 217770*k + 67210', '88200*k**2 + 108885*k + 33605'] -/
theorem cls_840_517 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(840*(m:ℤ) + 517)*x*y - (840*(m:ℤ) + 517)*x*z - (840*(m:ℤ) + 517)*y*z + 4*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨(210*(m:ℤ) + 130), (176400*(m:ℤ)^2 + 217770*(m:ℤ) + 67210), (88200*(m:ℤ)^2 + 108885*(m:ℤ) + 33605), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring

/-- class n = 840k + 589, k = m + 0. Witnesses: ['210*k + 148', '176400*k**2 + 248010*k + 87172', '88200*k**2 + 124005*k + 43586'] -/
theorem cls_840_589 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(840*(m:ℤ) + 589)*x*y - (840*(m:ℤ) + 589)*x*z - (840*(m:ℤ) + 589)*y*z + 4*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨(210*(m:ℤ) + 148), (176400*(m:ℤ)^2 + 248010*(m:ℤ) + 87172), (88200*(m:ℤ)^2 + 124005*(m:ℤ) + 43586), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring

/-- class n = 840k + 661, k = m + 0. Witnesses: ['210*k + 166', '176400*k**2 + 278250*k + 109726', '88200*k**2 + 139125*k + 54863'] -/
theorem cls_840_661 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(840*(m:ℤ) + 661)*x*y - (840*(m:ℤ) + 661)*x*z - (840*(m:ℤ) + 661)*y*z + 4*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨(210*(m:ℤ) + 166), (176400*(m:ℤ)^2 + 278250*(m:ℤ) + 109726), (88200*(m:ℤ)^2 + 139125*(m:ℤ) + 54863), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring

/-- class n = 840k + 697, k = m + 0. Witnesses: ['210*k + 175', '58800*k**2 + 97790*k + 40660', '2074464000*k**4 + 6900062400*k**3 + 8606641260*k**2 + 4771271890*k + 991900700'] -/
theorem cls_840_697 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(840*(m:ℤ) + 697)*x*y - (840*(m:ℤ) + 697)*x*z - (840*(m:ℤ) + 697)*y*z + 4*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨(210*(m:ℤ) + 175), (58800*(m:ℤ)^2 + 97790*(m:ℤ) + 40660), (2074464000*(m:ℤ)^4 + 6900062400*(m:ℤ)^3 + 8606641260*(m:ℤ)^2 + 4771271890*(m:ℤ) + 991900700), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring

/-- class n = 840k + 733, k = m + 0. Witnesses: ['210*k + 184', '176400*k**2 + 308490*k + 134872', '88200*k**2 + 154245*k + 67436'] -/
theorem cls_840_733 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(840*(m:ℤ) + 733)*x*y - (840*(m:ℤ) + 733)*x*z - (840*(m:ℤ) + 733)*y*z + 4*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨(210*(m:ℤ) + 184), (176400*(m:ℤ)^2 + 308490*(m:ℤ) + 134872), (88200*(m:ℤ)^2 + 154245*(m:ℤ) + 67436), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring

/-- class n = 840k + 757, k = m + 0. Witnesses: ['210*k + 190', '176400*k**2 + 318570*k + 143830', '88200*k**2 + 159285*k + 71915'] -/
theorem cls_840_757 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(840*(m:ℤ) + 757)*x*y - (840*(m:ℤ) + 757)*x*z - (840*(m:ℤ) + 757)*y*z + 4*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨(210*(m:ℤ) + 190), (176400*(m:ℤ)^2 + 318570*(m:ℤ) + 143830), (88200*(m:ℤ)^2 + 159285*(m:ℤ) + 71915), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring

/-- class n = 840k + 781, k = m + 0. Witnesses: ['210*k + 196', '176400*k**2 + 328650*k + 153076', '88200*k**2 + 164325*k + 76538'] -/
theorem cls_840_781 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(840*(m:ℤ) + 781)*x*y - (840*(m:ℤ) + 781)*x*z - (840*(m:ℤ) + 781)*y*z + 4*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨(210*(m:ℤ) + 196), (176400*(m:ℤ)^2 + 328650*(m:ℤ) + 153076), (88200*(m:ℤ)^2 + 164325*(m:ℤ) + 76538), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring

/-- class n = 840k + 829, k = m + 0. Witnesses: ['210*k + 208', '176400*k**2 + 348810*k + 172432', '88200*k**2 + 174405*k + 86216'] -/
theorem cls_840_829 (m : ℕ) : ∃ x y z : ℤ, 1 ≤ x ∧ 1 ≤ y ∧ 1 ≤ z ∧ -(840*(m:ℤ) + 829)*x*y - (840*(m:ℤ) + 829)*x*z - (840*(m:ℤ) + 829)*y*z + 4*x*y*z = 0 := by
  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity
  refine ⟨(210*(m:ℤ) + 208), (176400*(m:ℤ)^2 + 348810*(m:ℤ) + 172432), (88200*(m:ℤ)^2 + 174405*(m:ℤ) + 86216), ?_, ?_, ?_, ?_⟩
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · nlinarith [hm, pow_nonneg hm 2, pow_nonneg hm 3, pow_nonneg hm 4, pow_nonneg hm 5, pow_nonneg hm 6, pow_nonneg hm 7, pow_nonneg hm 8]
  · ring
