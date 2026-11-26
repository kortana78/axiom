# ABC proof track: routes, partial results, status

**abc conjecture: OPEN. No result here proves it.**

Every claim on this track refers to the exact Lean statement in
`lean/Abc/Statement.lean` (`Abc.Statement`, with `Abc.rad`, `Abc.quality`, and
the equivalent `Abc.FinitelyMany`).  A candidate argument is accepted only as
a Lean proof of that statement, with no `sorry` and no new axioms, plus human
review.  Nothing in this file is a proof.

## The statement

For every `ε > 0` there is `K = K(ε) > 0` such that every coprime positive
integer triple `a + b = c` satisfies

```
c <= K * rad(a*b*c)^(1+ε).
```

Equivalent form: for each `ε > 0`, only finitely many coprime triples satisfy
`c > rad(a*b*c)^(1+ε)`.  The equivalence is standard; the Lean file records
both forms but does not formalize the equivalence.

Sources: D. W. Masser, "Open problems", *Proceedings of the Symposium on
Analytic Number Theory* (1985); J. Oesterlé, "Nouvelles approches du
'théorème' de Fermat", *Séminaire Bourbaki* 1987/88, Astérisque 161–162
(1988), 165–186.

## Routes and partial results

| Route | What it gives | Status | Citations / notes |
|---|---|---|---|
| Szpiro's conjecture | The discriminant-conductor inequality for elliptic curves; implies abc (and is equivalent up to constants) | open; no proof here | L. Szpiro, "Seminaire sur les pinceaux de courbes de genre au moins deux", Astérisque 86 (1981); Masser–Oesterlé; Bombieri–Gubler, *Heights in Diophantine Geometry* |
| Mason–Stothers | The polynomial analogue: for coprime polynomials `a+b+c=0`, `max deg + 1 <= deg rad(abc)` (with the derivative-zero exception) | proved; polynomial only | R. C. Mason, "Diophantine equations over function fields" (1984); W. W. Stothers, "Polynomial identities and Hauptmoduln", *Quart. J. Math.* 32 (1981); Mathlib: `Polynomial.abc` in `Mathlib.NumberTheory.FLT.MasonStothers` |
| Stewart–Tijdeman | Effective exponential upper bounds `c < K exp(rad^15)` type | proved partial bound; far weaker than abc | C. L. Stewart and R. Tijdeman, "On the Oesterlé–Masser conjecture", *Monatsh. Math.* 102 (1986), 251–257, doi:10.1007/BF01294603 |
| Stewart–Yu I/II | Effective bounds from linear forms in logarithms; the strongest general effective bounds of this type | proved partial bound; not abc | C. L. Stewart and K. Yu, "On the abc conjecture", *Math. Ann.* 291 (1991), 225–230, doi:10.1007/BF01445201; "On the abc conjecture, II", *Duke Math. J.* 108 (2001), 169–181, doi:10.1215/S0012-7094-01-10815-6 |
| Győry–Yu and explicit S-unit bounds | Explicit upper bounds for S-unit equations and related Thue equations | proved partial bounds; used as an alternative to the height bound here | K. Győry and K. Yu, "Bounds for the solutions of S-unit equations and Thue equations", in *Number Theory* (2006); Matschke–von Känel, arXiv:1605.06079, §10.1.2 |
| Linear forms in logarithms (Baker–Wüstholz, Matveev) | Effective lower bounds for linear forms; the engine behind the partial bounds | proved general tool; not abc | A. Baker and G. Wüstholz, *Logarithmic Forms and Diophantine Geometry* (2007); E. M. Matveev, "An explicit lower bound for a homogeneous rational linear form in logarithms of algebraic numbers", *Izv. Math.* 64 (2000) |
| Explicit abc (Baker) | A numerical inequality `c < κ rad(abc) (log rad(abc))^ω / ...` with an explicit κ | conjecture / numerical proposal; not proved | A. Baker, "Experiments on the abc-conjecture", *J. Number Theory* 1998; see also the ABC@home pages |
| IUT (Mochizuki) | Proposed inter-universal Teichmüller proof | disputed; not accepted as a proof by the wider community; no formalization | S. Mochizuki, "Inter-universal Teichmüller theory I–IV" (2012–2021), *Publ. Res. Inst. Math. Sci.*; critical analyses by P. Scholze and J. Stix (2018, 2020); the dispute is unresolved. This repository takes no side and uses no IUT claim. |
| Computational search (ABC@home, de Weger, this repo's hunter) | Records and finite verification | search only; cannot prove abc | ABC@home; B. M. M. de Weger, *Algorithms for Diophantine Equations* (1987); `results/abc/` and `axiom/abc/` |

## What would count as progress

1. A Lean proof of `Abc.Statement` with only standard axioms, no `sorry`,
   no `axiom` declarations, and a human review of the formalization.
2. A proved implication from a published theorem to `Abc.Statement`, again
   formalized in Lean against this file.
3. A complete, independently checked S-unit certificate for a fixed `S`
   (finite result; not abc).

## Unverified ideas

No candidate proof has been accepted.  LLM-generated ideas are recorded in
`swarm/llm_ideas.json` and `swarm/sunit_ideas.json` and are only proposals.
They must go through workers, merge, the kernel, and Lean like any other
untrusted input.  They never mark a problem proved and never edit `results/`,
the kernel, or the checker.

## Formalization status

`lean/Abc/Statement.lean` compiles against Mathlib.  `#print axioms` on its
trivial `rad_one` lemma reports the standard axioms `propext`,
`Classical.choice`, and `Quot.sound`; there are no custom axioms.  The file
contains no proof of `Statement`.
