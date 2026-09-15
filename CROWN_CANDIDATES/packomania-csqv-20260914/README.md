# Packomania csqv crown candidates — 2026-09-14

**Status:** `CANDIDATE_RECORD`, not yet a third-party accepted/public crown.

This packet contains two strictly-feasible candidate improvements for Packomania `csqv`: variable-radius circles in a unit square, maximizing sum of radii.

## Candidate results

| N | candidate Σr | keeper record fetched 2026-09-14 | delta |
|---:|---:|---:|---:|
| 120 | 5.7742848313038259 | 5.773179664810 | +0.001105166494 |
| 122 | 5.8242710218195016 | 5.822533741917 | +0.001737279903 |

The submitted `.pck` files include a uniform ~1e-10 radius safety shrink. The unshrunk raw solver results are preserved beside them.

## Provenance

- HFO carrier/roach UUID: `1a3d1b55-bb63-403d-a76a-1f16a94e5b17`
- Donor: `ucsandman/discovery-loop@ce97256043f7813e0beaeeb7ca5cafacbf77fbdb`
- Solver: donor `best/solver.py` (Discovery Loop; Wes Sander)
- Run: unmodified donor solver, `--time 20`
- N=120 seed: `142120`; N=122 seed: `142122`
- Live keeper source: `https://www.packomania.com/csqv/txt/sumradii.txt`

## Verification stack

1. Discovery Loop's own independent `problems/circle_packing/verify.py` accepted both raw candidates as feasible.
2. Independent verifier donor: `jasonzliang/circle-packing-sota@28e129593b1c696627db67911b0392c439c64610`, pure stdlib and no shared solver code.
3. That verifier re-fetched the keeper table and accepted both final `.pck` files with `--tol 0`.
4. Separate 80-digit `Decimal` geometry readback of the exact written decimals found strictly positive wall and pair slacks.
5. Discovery Loop breaker: N=120 survived 400 perturbation attempts; N=122 survived 395. Breaker survival is bounded evidence, not proof of optimality.

Final exact-coordinate slacks:

- N=120: min wall `1.000001e-10`; min pair `2.0000004114e-10`.
- N=122: min wall `1.000001e-10`; min pair `2.0000000386e-10`.

Final file SHA-256:

- `csqv120.pck`: `a5222477917e40b4fd6f908ced5576687169e15ddc3332d6ffcaf3a25124470d`
- `csqv122.pck`: `b82b2943c8861dcf30c44772fed9de77d11b2357f6e2e286f5b8a9d9bb15ab1b`

## Claim ceiling

These coordinates beat the Packomania record snapshot retrieved on 2026-09-14 and independently pass the local mathematical checks above. They are **not** called world records until an independent public keeper/verifier accepts or lists them. Re-fetch the keeper table immediately before external submission; if either incumbent has moved above the candidate, HOLD or re-evolve rather than sending a stale crown claim.
