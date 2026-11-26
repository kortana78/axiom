import Mathlib

/-! AXIOM ABC record export for `abc`.
    Statement: abc conjecture (Masser-Oesterle): for every eps > 0 there is K(eps) such that for all coprime positive integers a + b = c, c <= K(eps) * rad(a*b*c)^(1+eps). This queue entry runs the triple hunter, not a proof.

    Each theorem checks a+b=c and coprimality for one recorded triple.
    The radical and quality are exact integer computations by the Python
    merger (prime factorizations are included in records.json). They are
    not formalized here, and this file does not prove the abc conjecture. -/

/-- a=2, b=6436341, c=6436343, rad(abc)=15042, q=1.629912. -/
theorem rec_000_add : 2 + 6436341 = 6436343 := by norm_num
theorem rec_000_coprime : Nat.Coprime 2 6436341 := by decide

/-- a=121, b=48234375, c=48234496, rad(abc)=53130, q=1.625991. -/
theorem rec_001_add : 121 + 48234375 = 48234496 := by norm_num
theorem rec_001_coprime : Nat.Coprime 121 48234375 := by decide

/-- a=1, b=4374, c=4375, rad(abc)=210, q=1.567887. -/
theorem rec_002_add : 1 + 4374 = 4375 := by norm_num
theorem rec_002_coprime : Nat.Coprime 1 4374 := by decide

/-- a=343, b=59049, c=59392, rad(abc)=1218, q=1.547075. -/
theorem rec_003_add : 343 + 59049 = 59392 := by norm_num
theorem rec_003_coprime : Nat.Coprime 343 59049 := by decide

/-- a=121, b=255879, c=256000, rad(abc)=4290, q=1.488865. -/
theorem rec_004_add : 121 + 255879 = 256000 := by norm_num
theorem rec_004_coprime : Nat.Coprime 121 255879 := by decide

/-- a=37, b=32768, c=32805, rad(abc)=1110, q=1.482910. -/
theorem rec_005_add : 37 + 32768 = 32805 := by norm_num
theorem rec_005_coprime : Nat.Coprime 37 32768 := by decide

/-- a=49, b=31640576, c=31640625, rad(abc)=122430, q=1.474137. -/
theorem rec_006_add : 49 + 31640576 = 31640625 := by norm_num
theorem rec_006_coprime : Nat.Coprime 49 31640576 := by decide

/-- a=3200, b=4823609, c=4826809, rad(abc)=37310, q=1.461924. -/
theorem rec_007_add : 3200 + 4823609 = 4826809 := by norm_num
theorem rec_007_coprime : Nat.Coprime 3200 4823609 := by decide

/-- a=1, b=2400, c=2401, rad(abc)=210, q=1.455673. -/
theorem rec_008_add : 1 + 2400 = 2401 := by norm_num
theorem rec_008_coprime : Nat.Coprime 1 2400 := by decide

/-- a=1701, b=1046875, c=1048576, rad(abc)=14070, q=1.451344. -/
theorem rec_009_add : 1701 + 1046875 = 1048576 := by norm_num
theorem rec_009_coprime : Nat.Coprime 1701 1046875 := by decide

/-- a=338, b=390625, c=390963, rad(abc)=7410, q=1.445064. -/
theorem rec_010_add : 338 + 390625 = 390963 := by norm_num
theorem rec_010_coprime : Nat.Coprime 338 390625 := by decide

/-- a=1, b=512000, c=512001, rad(abc)=9030, q=1.443307. -/
theorem rec_011_add : 1 + 512000 = 512001 := by norm_num
theorem rec_011_coprime : Nat.Coprime 1 512000 := by decide

/-- a=61731, b=48828125, c=48889856, rad(abc)=212610, q=1.443284. -/
theorem rec_012_add : 61731 + 48828125 = 48889856 := by norm_num
theorem rec_012_coprime : Nat.Coprime 61731 48828125 := by decide

/-- a=42849, b=28629151, c=28672000, rad(abc)=149730, q=1.440969. -/
theorem rec_013_add : 42849 + 28629151 = 28672000 := by norm_num
theorem rec_013_coprime : Nat.Coprime 42849 28629151 := by decide

/-- a=1, b=19140624, c=19140625, rad(abc)=114870, q=1.439063. -/
theorem rec_014_add : 1 + 19140624 = 19140625 := by norm_num
theorem rec_014_coprime : Nat.Coprime 1 19140624 := by decide

/-- a=7168, b=78125, c=85293, rad(abc)=2730, q=1.435006. -/
theorem rec_015_add : 7168 + 78125 = 85293 := by norm_num
theorem rec_015_coprime : Nat.Coprime 7168 78125 := by decide

/-- a=11, b=9565927, c=9565938, rad(abc)=77154, q=1.428323. -/
theorem rec_016_add : 11 + 9565927 = 9565938 := by norm_num
theorem rec_016_coprime : Nat.Coprime 11 9565927 := by decide

/-- a=3, b=125, c=128, rad(abc)=30, q=1.426565. -/
theorem rec_017_add : 3 + 125 = 128 := by norm_num
theorem rec_017_coprime : Nat.Coprime 3 125 := by decide

/-- a=78125, b=27217619, c=27295744, rad(abc)=170170, q=1.421575. -/
theorem rec_018_add : 78125 + 27217619 = 27295744 := by norm_num
theorem rec_018_coprime : Nat.Coprime 78125 27217619 := by decide

/-- a=43840, b=4782969, c=4826809, rad(abc)=53430, q=1.413698. -/
theorem rec_019_add : 43840 + 4782969 = 4826809 := by norm_num
theorem rec_019_coprime : Nat.Coprime 43840 4782969 := by decide

/-- a=25, b=4804839, c=4804864, rad(abc)=53430, q=1.413279. -/
theorem rec_020_add : 25 + 4804839 = 4804864 := by norm_num
theorem rec_020_coprime : Nat.Coprime 25 4804839 := by decide

/-- a=5, b=177147, c=177152, rad(abc)=5190, q=1.412681. -/
theorem rec_021_add : 5 + 177147 = 177152 := by norm_num
theorem rec_021_coprime : Nat.Coprime 5 177147 := by decide

/-- a=245, b=13436683, c=13436928, rad(abc)=117390, q=1.406079. -/
theorem rec_022_add : 245 + 13436683 = 13436928 := by norm_num
theorem rec_022_coprime : Nat.Coprime 245 13436683 := by decide

/-- a=2197, b=700928, c=703125, rad(abc)=14430, q=1.405785. -/
theorem rec_023_add : 2197 + 700928 = 703125 := by norm_num
theorem rec_023_coprime : Nat.Coprime 2197 700928 := by decide

/-- a=91, b=1771470, c=1771561, rad(abc)=30030, q=1.395484. -/
theorem rec_024_add : 91 + 1771470 = 1771561 := by norm_num
theorem rec_024_coprime : Nat.Coprime 91 1771470 := by decide

/-- a=4, b=71744535, c=71744539, rad(abc)=438090, q=1.392484. -/
theorem rec_025_add : 4 + 71744535 = 71744539 := by norm_num
theorem rec_025_coprime : Nat.Coprime 4 71744535 := by decide

/-- a=2, b=7263025, c=7263027, rad(abc)=94710, q=1.378732. -/
theorem rec_026_add : 2 + 7263025 = 7263027 := by norm_num
theorem rec_026_coprime : Nat.Coprime 2 7263025 := by decide

/-- a=1, b=1050624, c=1050625, rad(abc)=23370, q=1.378329. -/
theorem rec_027_add : 1 + 1050624 = 1050625 := by norm_num
theorem rec_027_coprime : Nat.Coprime 1 1050624 := by decide

/-- a=3906250, b=4782969, c=8689219, rad(abc)=108570, q=1.377955. -/
theorem rec_028_add : 3906250 + 4782969 = 8689219 := by norm_num
theorem rec_028_coprime : Nat.Coprime 3906250 4782969 := by decide

/-- a=33, b=2000000, c=2000033, rad(abc)=39270, q=1.371562. -/
theorem rec_029_add : 33 + 2000000 = 2000033 := by norm_num
theorem rec_029_coprime : Nat.Coprime 33 2000000 := by decide

/-- a=128, b=109375, c=109503, rad(abc)=4830, q=1.367942. -/
theorem rec_030_add : 128 + 109375 = 109503 := by norm_num
theorem rec_030_coprime : Nat.Coprime 128 109375 := by decide

/-- a=5125, b=23882747, c=23887872, rad(abc)=249690, q=1.366987. -/
theorem rec_031_add : 5125 + 23882747 = 23887872 := by norm_num
theorem rec_031_coprime : Nat.Coprime 5125 23882747 := by decide

/-- a=1127357, b=5688387, c=6815744, rad(abc)=102102, q=1.364238. -/
theorem rec_032_add : 1127357 + 5688387 = 6815744 := by norm_num
theorem rec_032_coprime : Nat.Coprime 1127357 5688387 := by decide

/-- a=243, b=4194304, c=4194547, rad(abc)=73374, q=1.361140. -/
theorem rec_033_add : 243 + 4194304 = 4194547 := by norm_num
theorem rec_033_coprime : Nat.Coprime 243 4194304 := by decide

/-- a=625, b=2048, c=2673, rad(abc)=330, q=1.360723. -/
theorem rec_034_add : 625 + 2048 = 2673 := by norm_num
theorem rec_034_coprime : Nat.Coprime 625 2048 := by decide

/-- a=39375, b=7890481, c=7929856, rad(abc)=122430, q=1.356018. -/
theorem rec_035_add : 39375 + 7890481 = 7929856 := by norm_num
theorem rec_035_coprime : Nat.Coprime 39375 7890481 := by decide

/-- a=3481, b=262144, c=265625, rad(abc)=10030, q=1.355626. -/
theorem rec_036_add : 3481 + 262144 = 265625 := by norm_num
theorem rec_036_coprime : Nat.Coprime 3481 262144 := by decide

/-- a=3173, b=78121827, c=78125000, rad(abc)=666330, q=1.355290. -/
theorem rec_037_add : 3173 + 78121827 = 78125000 := by norm_num
theorem rec_037_coprime : Nat.Coprime 3173 78121827 := by decide

/-- a=47, b=250000, c=250047, rad(abc)=9870, q=1.351425. -/
theorem rec_038_add : 47 + 250000 = 250047 := by norm_num
theorem rec_038_coprime : Nat.Coprime 47 250000 := by decide

/-- a=24389, b=393216, c=417605, rad(abc)=14790, q=1.347916. -/
theorem rec_039_add : 24389 + 393216 = 417605 := by norm_num
theorem rec_039_coprime : Nat.Coprime 24389 393216 := by decide

/-- a=6859, b=24130710, c=24137569, rad(abc)=300390, q=1.347776. -/
theorem rec_040_add : 6859 + 24130710 = 24137569 := by norm_num
theorem rec_040_coprime : Nat.Coprime 6859 24130710 := by decide

/-- a=131072, b=1003833, c=1134905, rad(abc)=31110, q=1.347673. -/
theorem rec_041_add : 131072 + 1003833 = 1134905 := by norm_num
theorem rec_041_coprime : Nat.Coprime 131072 1003833 := by decide

/-- a=17, b=140608, c=140625, rad(abc)=6630, q=1.347127. -/
theorem rec_042_add : 17 + 140608 = 140625 := by norm_num
theorem rec_042_coprime : Nat.Coprime 17 140608 := by decide

/-- a=1, b=688127, c=688128, rad(abc)=21714, q=1.346096. -/
theorem rec_043_add : 1 + 688127 = 688128 := by norm_num
theorem rec_043_coprime : Nat.Coprime 1 688127 := by decide

/-- a=2890625, b=6067327, c=8957952, rad(abc)=147630, q=1.344936. -/
theorem rec_044_add : 2890625 + 6067327 = 8957952 := by norm_num
theorem rec_044_coprime : Nat.Coprime 2890625 6067327 := by decide

/-- a=1, b=47045880, c=47045881, rad(abc)=506730, q=1.344929. -/
theorem rec_045_add : 1 + 47045880 = 47045881 := by norm_num
theorem rec_045_coprime : Nat.Coprime 1 47045880 := by decide

/-- a=1, b=96059600, c=96059601, rad(abc)=870870, q=1.343873. -/
theorem rec_046_add : 1 + 96059600 = 96059601 := by norm_num
theorem rec_046_coprime : Nat.Coprime 1 96059600 := by decide

/-- a=49, b=531392, c=531441, rad(abc)=18354, q=1.342828. -/
theorem rec_047_add : 49 + 531392 = 531441 := by norm_num
theorem rec_047_coprime : Nat.Coprime 49 531392 := by decide

/-- a=83521, b=42963200, c=43046721, rad(abc)=489090, q=1.341786. -/
theorem rec_048_add : 83521 + 42963200 = 43046721 := by norm_num
theorem rec_048_coprime : Nat.Coprime 83521 42963200 := by decide

/-- a=1244485, b=2097152, c=3341637, rad(abc)=72930, q=1.341576. -/
theorem rec_049_add : 1244485 + 2097152 = 3341637 := by norm_num
theorem rec_049_coprime : Nat.Coprime 1244485 2097152 := by decide

/-- a=1487, b=67108864, c=67110351, rad(abc)=686994, q=1.340903. -/
theorem rec_050_add : 1487 + 67108864 = 67110351 := by norm_num
theorem rec_050_coprime : Nat.Coprime 1487 67108864 := by decide

/-- a=289, b=6272, c=6561, rad(abc)=714, q=1.337552. -/
theorem rec_051_add : 289 + 6272 = 6561 := by norm_num
theorem rec_051_coprime : Nat.Coprime 289 6272 := by decide

/-- a=1, b=3499199, c=3499200, rad(abc)=78870, q=1.336346. -/
theorem rec_052_add : 1 + 3499199 = 3499200 := by norm_num
theorem rec_052_coprime : Nat.Coprime 1 3499199 := by decide

/-- a=1058, b=36924979, c=36926037, rad(abc)=464646, q=1.335304. -/
theorem rec_053_add : 1058 + 36924979 = 36926037 := by norm_num
theorem rec_053_coprime : Nat.Coprime 1058 36924979 := by decide

/-- a=119232, b=40234375, c=40353607, rad(abc)=497490, q=1.335119. -/
theorem rec_054_add : 119232 + 40234375 = 40353607 := by norm_num
theorem rec_054_coprime : Nat.Coprime 119232 40234375 := by decide

/-- a=729, b=29984039, c=29984768, rad(abc)=402798, q=1.333949. -/
theorem rec_055_add : 729 + 29984039 = 29984768 := by norm_num
theorem rec_055_coprime : Nat.Coprime 729 29984039 := by decide

/-- a=4508, b=1948617, c=1953125, rad(abc)=53130, q=1.331276. -/
theorem rec_056_add : 4508 + 1948617 = 1953125 := by norm_num
theorem rec_056_coprime : Nat.Coprime 4508 1948617 := by decide

/-- a=164025, b=40353607, c=40517632, rad(abc)=519330, q=1.331068. -/
theorem rec_057_add : 164025 + 40353607 = 40517632 := by norm_num
theorem rec_057_coprime : Nat.Coprime 164025 40353607 := by decide

/-- a=9583, b=524288, c=533871, rad(abc)=20202, q=1.330293. -/
theorem rec_058_add : 9583 + 524288 = 533871 := by norm_num
theorem rec_058_coprime : Nat.Coprime 9583 524288 := by decide

/-- a=2367, b=5764801, c=5767168, rad(abc)=121506, q=1.329695. -/
theorem rec_059_add : 2367 + 5764801 = 5767168 := by norm_num
theorem rec_059_coprime : Nat.Coprime 2367 5764801 := by decide

/-- a=131072, b=221875, c=352947, rad(abc)=14910, q=1.329277. -/
theorem rec_060_add : 131072 + 221875 = 352947 := by norm_num
theorem rec_060_coprime : Nat.Coprime 131072 221875 := by decide

/-- a=7, b=32761, c=32768, rad(abc)=2534, q=1.326588. -/
theorem rec_061_add : 7 + 32761 = 32768 := by norm_num
theorem rec_061_coprime : Nat.Coprime 7 32761 := by decide

/-- a=2048, b=97970133, c=97972181, rad(abc)=1081506, q=1.324339. -/
theorem rec_062_add : 2048 + 97970133 = 97972181 := by norm_num
theorem rec_062_coprime : Nat.Coprime 2048 97970133 := by decide

/-- a=1, b=59048, c=59049, rad(abc)=4026, q=1.323545. -/
theorem rec_063_add : 1 + 59048 = 59049 := by norm_num
theorem rec_063_coprime : Nat.Coprime 1 59048 := by decide

/-- a=95, b=279841, c=279936, rad(abc)=13110, q=1.322871. -/
theorem rec_064_add : 95 + 279841 = 279936 := by norm_num
theorem rec_064_coprime : Nat.Coprime 95 279841 := by decide

/-- a=4375, b=4782969, c=4787344, rad(abc)=114870, q=1.320123. -/
theorem rec_065_add : 4375 + 4782969 = 4787344 := by norm_num
theorem rec_065_coprime : Nat.Coprime 4375 4782969 := by decide

/-- a=1024, b=48828125, c=48829149, rad(abc)=669810, q=1.319729. -/
theorem rec_066_add : 1024 + 48828125 = 48829149 := by norm_num
theorem rec_066_coprime : Nat.Coprime 1024 48828125 := by decide

/-- a=1, b=5831, c=5832, rad(abc)=714, q=1.319627. -/
theorem rec_067_add : 1 + 5831 = 5832 := by norm_num
theorem rec_067_coprime : Nat.Coprime 1 5831 := by decide

/-- a=211, b=5000000, c=5000211, rad(abc)=120270, q=1.318658. -/
theorem rec_068_add : 211 + 5000000 = 5000211 := by norm_num
theorem rec_068_coprime : Nat.Coprime 211 5000000 := by decide

/-- a=1, b=512, c=513, rad(abc)=114, q=1.317571. -/
theorem rec_069_add : 1 + 512 = 513 := by norm_num
theorem rec_069_coprime : Nat.Coprime 1 512 := by decide

/-- a=49, b=5767119, c=5767168, rad(abc)=135366, q=1.317539. -/
theorem rec_070_add : 49 + 5767119 = 5767168 := by norm_num
theorem rec_070_coprime : Nat.Coprime 49 5767119 := by decide

/-- a=19321, b=17915904, c=17935225, rad(abc)=321090, q=1.317269. -/
theorem rec_071_add : 19321 + 17915904 = 17935225 := by norm_num
theorem rec_071_coprime : Nat.Coprime 19321 17915904 := by decide

/-- a=2476099, b=5451776, c=7927875, rad(abc)=181830, q=1.311710. -/
theorem rec_072_add : 2476099 + 5451776 = 7927875 := by norm_num
theorem rec_072_coprime : Nat.Coprime 2476099 5451776 := by decide

/-- a=729, b=6864896, c=6865625, rad(abc)=163410, q=1.311397. -/
theorem rec_073_add : 729 + 6864896 = 6865625 := by norm_num
theorem rec_073_coprime : Nat.Coprime 729 6864896 := by decide

/-- a=1, b=242, c=243, rad(abc)=66, q=1.311101. -/
theorem rec_074_add : 1 + 242 = 243 := by norm_num
theorem rec_074_coprime : Nat.Coprime 1 242 := by decide

/-- a=371293, b=28588707, c=28960000, rad(abc)=494130, q=1.310503. -/
theorem rec_075_add : 371293 + 28588707 = 28960000 := by norm_num
theorem rec_075_coprime : Nat.Coprime 371293 28588707 := by decide

/-- a=12005, b=161051, c=173056, rad(abc)=10010, q=1.309405. -/
theorem rec_076_add : 12005 + 161051 = 173056 := by norm_num
theorem rec_076_coprime : Nat.Coprime 12005 161051 := by decide

/-- a=203125, b=38336139, c=38539264, rad(abc)=643110, q=1.306049. -/
theorem rec_077_add : 203125 + 38336139 = 38539264 := by norm_num
theorem rec_077_coprime : Nat.Coprime 203125 38336139 := by decide

/-- a=7424, b=1586899, c=1594323, rad(abc)=56202, q=1.305874. -/
theorem rec_078_add : 7424 + 1586899 = 1594323 := by norm_num
theorem rec_078_coprime : Nat.Coprime 7424 1586899 := by decide

/-- a=768, b=1127357, c=1128125, rad(abc)=43890, q=1.303723. -/
theorem rec_079_add : 768 + 1127357 = 1128125 := by norm_num
theorem rec_079_coprime : Nat.Coprime 768 1127357 := by decide

/-- a=2744, b=2476099, c=2478843, rad(abc)=80598, q=1.303267. -/
theorem rec_080_add : 2744 + 2476099 = 2478843 := by norm_num
theorem rec_080_coprime : Nat.Coprime 2744 2476099 := by decide

/-- a=5120, b=47293129, c=47298249, rad(abc)=798330, q=1.300340. -/
theorem rec_081_add : 5120 + 47293129 = 47298249 := by norm_num
theorem rec_081_coprime : Nat.Coprime 5120 47293129 := by decide

/-- a=874577, b=2250423, c=3125000, rad(abc)=99330, q=1.299729. -/
theorem rec_082_add : 874577 + 2250423 = 3125000 := by norm_num
theorem rec_082_coprime : Nat.Coprime 874577 2250423 := by decide

/-- a=5, b=1024, c=1029, rad(abc)=210, q=1.297214. -/
theorem rec_083_add : 5 + 1024 = 1029 := by norm_num
theorem rec_083_coprime : Nat.Coprime 5 1024 := by decide

/-- a=12672, b=117649, c=130321, rad(abc)=8778, q=1.297109. -/
theorem rec_084_add : 12672 + 117649 = 130321 := by norm_num
theorem rec_084_coprime : Nat.Coprime 12672 117649 := by decide

/-- a=81, b=134375, c=134456, rad(abc)=9030, q=1.296508. -/
theorem rec_085_add : 81 + 134375 = 134456 := by norm_num
theorem rec_085_coprime : Nat.Coprime 81 134375 := by decide

/-- a=8, b=4826809, c=4826817, rad(abc)=143754, q=1.295881. -/
theorem rec_086_add : 8 + 4826809 = 4826817 := by norm_num
theorem rec_086_coprime : Nat.Coprime 8 4826809 := by decide

/-- a=32768, b=859375, c=892143, rad(abc)=39270, q=1.295245. -/
theorem rec_087_add : 32768 + 859375 = 892143 := by norm_num
theorem rec_087_coprime : Nat.Coprime 32768 859375 := by decide

/-- a=8107, b=5242880, c=5250987, rad(abc)=154770, q=1.294922. -/
theorem rec_088_add : 8107 + 5242880 = 5250987 := by norm_num
theorem rec_088_coprime : Nat.Coprime 8107 5242880 := by decide

/-- a=36864, b=48828125, c=48864989, rad(abc)=872070, q=1.294324. -/
theorem rec_089_add : 36864 + 48828125 = 48864989 := by norm_num
theorem rec_089_coprime : Nat.Coprime 36864 48828125 := by decide

/-- a=23040, b=1419857, c=1442897, rad(abc)=57630, q=1.293781. -/
theorem rec_090_add : 23040 + 1419857 = 1442897 := by norm_num
theorem rec_090_coprime : Nat.Coprime 23040 1419857 := by decide

/-- a=10125, b=1075648, c=1085773, rad(abc)=46410, q=1.293388. -/
theorem rec_091_add : 10125 + 1075648 = 1085773 := by norm_num
theorem rec_091_coprime : Nat.Coprime 10125 1075648 := by decide

/-- a=1, b=80, c=81, rad(abc)=30, q=1.292030. -/
theorem rec_092_add : 1 + 80 = 81 := by norm_num
theorem rec_092_coprime : Nat.Coprime 1 80 := by decide

/-- a=81, b=123823, c=123904, rad(abc)=8778, q=1.291548. -/
theorem rec_093_add : 81 + 123823 = 123904 := by norm_num
theorem rec_093_coprime : Nat.Coprime 81 123823 := by decide

/-- a=625, b=4091904, c=4092529, rad(abc)=132090, q=1.291185. -/
theorem rec_094_add : 625 + 4091904 = 4092529 := by norm_num
theorem rec_094_coprime : Nat.Coprime 625 4091904 := by decide

/-- a=10, b=2187, c=2197, rad(abc)=390, q=1.289752. -/
theorem rec_095_add : 10 + 2187 = 2197 := by norm_num
theorem rec_095_coprime : Nat.Coprime 10 2187 := by decide

/-- a=163840, b=1771561, c=1935401, rad(abc)=75790, q=1.288375. -/
theorem rec_096_add : 163840 + 1771561 = 1935401 := by norm_num
theorem rec_096_coprime : Nat.Coprime 163840 1771561 := by decide

/-- a=2197, b=583443, c=585640, rad(abc)=30030, q=1.288120. -/
theorem rec_097_add : 2197 + 583443 = 585640 := by norm_num
theorem rec_097_coprime : Nat.Coprime 2197 583443 := by decide

/-- a=3, b=65533, c=65536, rad(abc)=5538, q=1.286675. -/
theorem rec_098_add : 3 + 65533 = 65536 := by norm_num
theorem rec_098_coprime : Nat.Coprime 3 65533 := by decide

/-- a=121, b=12167, c=12288, rad(abc)=1518, q=1.285486. -/
theorem rec_099_add : 121 + 12167 = 12288 := by norm_num
theorem rec_099_coprime : Nat.Coprime 121 12167 := by decide
