# Packomania csqv N=124 — Gen142 Evo R3 candidate record

Status: **`SUBMISSION_READY_INTERNAL`**. This is a locally and independently verified candidate record, **not yet a public crown**. `CROWN_WON=false` until the Packomania keeper accepts/publishes it.

## Result

- Battlefield: Packomania `csqv`, variable-radius circles in a unit square; maximize sum of radii.
- N: **124**.
- Fresh official HTML table (last update **14-Sep-2026**) lists N=124 at **`5.874500201027`**.
- Canonical packet `csqv124.pck`, re-summed from its exact written decimals: **`5.8746761735946872`**.
- Candidate lead: **`+0.0001759725676872`**.
- Exact 80-digit Decimal feasibility on the canonical bytes: min wall slack **`1.000101E-10`**; min pair slack **`2.00020101686429177507200407972676314175804479360448617547559228963944665E-10`**.
- Canonical `.pck` SHA256: **`16458abe5c837e3be874ce00efd549070499baa78859e038521c7277c3bb6d4f`**.

Official keeper page: <https://www.packomania.com/csqv/csqv.html>

## Lineage

Carrier UUID: `5f8f7e1b-9e2c-4f8c-b2aa-7d34a9e6c11d`

Batch: `packomania-evo-r3-5f8f7e1b`

Execution: GitHub Actions run `34921650663` (success). Verified artifact id `10378492138`, digest `sha256:f56c11d61f9c13ad21e51faf46832bb33e28fd80f2d88588debeea25ec3a9300`.

Frozen public donor: `ucsandman/discovery-loop@ce97256043f7813e0beaeeb7ca5cafacbf77fbdb`, `best/solver.py`, SHA256 `c018bec37d2dbfdbbb26d88f2a1c1611ede62594c1233596efe27f93f7d8e486`. Discovery Loop is the published island-model/basin-hopping Packomania solver lineage; this batch did not rebuild its solver.

Winning mutation: `N=124`, stage `s2`, seed `415124`, 30-second survivor budget. Source candidate SHA256 `f1a3d57a61f791f6311414099f589380019c5e93ca142a19e480376739fade74`.

The producer and verifier were separated. The downstream verifier imported no producer/donor solver code and checked geometry independently after a deterministic `1.000001e-10` safety shrink per radius. Verifier replay SHA256: `0849d89db1ccf2f70f1f8c8d7c508fce9725a61860450050c12d6875f9218e83`.

## Successive halving / negative evidence

Stage 1 attacked held-out N=`116,117,118,119,121,123,124,125`, deliberately excluding the already-packaged N=120/N=122 candidates in PR #33. N=`125,124,121` survived to stage 2.

Only **N=124** cleared the keeper threshold after safety shrink. Verified non-wins were preserved rather than hidden: N116 `-0.011974282850377628`, N117 `-0.008644893630206987`, N118 `-0.006827758340320224`, N119 `-0.003335249604111643`, N121 `-0.000742571873807544`, N123 `-0.009223167220642918`, N125 `-0.000044290964241803` versus the producer's freshly fetched keeper table.

## Keeper-freshness scar

The linked Packomania plain-text table has shown tiny/stale drift at some N compared with the rendered HTML. That does **not** change N=124 here: the post-run official HTML read still reports exactly `5.874500201027`, matching the N=124 incumbent used in verification. Nevertheless, the final send gate is **fresh HTML readback immediately before submission**.

## Attribution / packet format

The canonical `.pck` uses the keeper-style author field `Tommy Tai`. HFO/Gen142 and solver provenance live in this evidence packet rather than overloading the keeper author line. The first line equals the largest radius and the remaining `x y r` rows are sorted by radius.

## Claim ceiling

Before keeper acceptance, the strongest truthful statement is:

> **Candidate Packomania csqv N=124 record, independently verified locally and pending third-party keeper acceptance.**

After keeper acceptance/public listing, the public claim can be upgraded to the exact keeper-supported wording. Do not generalize one N=124 result into a universal circle-packing or optimization claim.
