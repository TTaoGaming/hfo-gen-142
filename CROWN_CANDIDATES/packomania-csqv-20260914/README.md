# Packomania csqv crown candidates — 2026-09-14

**Status:** `CANDIDATE_RECORD / R2_EXACT_BYTES_VERIFIER_PASS / READY_FOR_HUMAN_SEND`, not yet a third-party accepted/public crown.

This packet contains two strictly-feasible candidate improvements for Packomania `csqv`: variable-radius circles in a unit square, maximizing sum of radii.

## Candidate results

| N | candidate Σr | keeper record last read | delta |
|---:|---:|---:|---:|
| 120 | 5.7742848313038259 | 5.773179664812 | +0.0011051664918259 |
| 122 | 5.8242710218195016 | 5.822533741922 | +0.0017372798975016 |

The candidate `.pck` files include a uniform ~1e-10 radius safety shrink. The unshrunk raw solver results are preserved beside them.

## Provenance

- HFO carrier/roach UUID: `1a3d1b55-bb63-403d-a76a-1f16a94e5b17`
- Donor: `ucsandman/discovery-loop@ce97256043f7813e0beaeeb7ca5cafacbf77fbdb`
- Solver: donor `best/solver.py` (Discovery Loop; Wes Sander)
- Run: unmodified donor solver, `--time 20`
- N=120 seed: `142120`; N=122 seed: `142122`
- Live keeper source: `https://www.packomania.com/csqv/txt/sumradii.txt`
- R2 packaging carrier: `6c4fa680-c4e8-45e9-bce2-223f619c1b36`
- R2 packaging change: keeper author line normalized to `Tommy Tai`; HFO/solver provenance remains here and in the cover note.

## Verification stack

1. Discovery Loop's own independent `problems/circle_packing/verify.py` accepted both raw candidates as feasible.
2. Independent verifier donor: `jasonzliang/circle-packing-sota@28e129593b1c696627db67911b0392c439c64610`, pure stdlib and no shared solver code.
3. R2 exact attachment bytes were re-read from the durable branch and passed that pinned verifier at `--tol 0` against the current keeper values recorded here; see `R2_VERIFIER_RECEIPT.md`.
4. Separate 80-digit `Decimal` geometry replay found strictly positive wall and pair slacks and reproduced the prior numeric invariants after the metadata-only R2 change.
5. Discovery Loop breaker: N=120 survived 400 perturbation attempts; N=122 survived 395. Breaker survival is bounded evidence, not proof of optimality.

Exact-coordinate slacks (unchanged numeric payload):

- N=120: min wall `1.000001e-10`; min pair `2.0000004114e-10`.
- N=122: min wall `1.000001e-10`; min pair `2.0000000386e-10`.

R2 file SHA-256:

- `csqv120.pck`: `5921e2ca32b2da8c8f908caaeaa9decc6498fd51b5e98006c96b1fe0571fa63a`
- `csqv122.pck`: `87af14334f54bb1c517e8e5d5cd36c38302f5b34bc0eca9a851641e59e73247f`

## Claim ceiling

These coordinates beat the current keeper values above and the R2 exact bytes pass the pinned independent verifier, but `CROWN_WON=false`. Re-fetch the keeper table immediately before the human external-send boundary. Do not claim a world record or Packomania acceptance until the keeper independently accepts/lists the construction. Reusable heritage admission from this cycle remains `NONE` pending verifier + downstream ConsumerAck.
