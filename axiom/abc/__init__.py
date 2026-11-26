"""ABC triple hunter.

A search-only mode for the AXIOM swarm. It looks for coprime positive
integers a + b = c with a high quality

    q(a,b,c) = log(c) / log(rad(a*b*c)),

where rad(n) is the product of the distinct primes dividing n. The hunter
does not prove the abc conjecture. Every recorded triple is re-verified
exactly by the merge step, including the radical, before it is committed.
"""
