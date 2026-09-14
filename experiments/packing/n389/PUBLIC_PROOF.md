# N389 Packomania public-proof packet

- actor_uuid: `15ab7b18-64bf-4cb8-93ca-8483a770e4a0`
- UTC assay: 2026-09-14
- status: `VERIFIED_DERIVATIVE_CANDIDATE_NOT_EXTERNALLY_SUBMITTED`
- problem: 389 equal circles in a 1 x 0.8 rectangle
- candidate radius: `0.023848376538816648640120148446`
- candidate SHA-256: `6285aba27da8b879a7464469d8d223ec987fce3ec83193f7d9aef9cee4fa800b`

## Public comparator/currentness
Packomania currently serves N389 radius `0.023840209433828469161245150244` and N390 radius `0.023848376539816648640120148446`; the table itself states last update 2013-06-25. The candidate beats the served N389 radius by ~`0.034257689769246%`.

Sources:
- https://www.packomania.com/crc_800/crc.html
- https://www.packomania.com/crc_800/txt/crc390_0.800000000000.txt
- https://www.packomania.com/hints.html

## Construction + attribution
Packomania identifies the N390 root as a David W. Cantrell improvement (2010-09-10). This packet removes source point #390 from that public 390-point coordinate set and reduces the radius by exactly `1e-12`. It is a donor-derived subset/table correction, **not** an original geometry discovery. Draft `.pck` author line credits `David W. Cantrell, Tommy Tai`; keeper attribution should preserve Cantrell's root credit.

## Independent verification
1. Python exact-rational verifier: `PASS_EXACT_RATIONAL`; 389 points; boundary clearance exactly `1e-12`; minimum pair squared-clearance positive (`~1.9078701231453318e-13`).
2. Independent Node/IEEE-754 verifier: `PASS_IEEE754_FLOAT64`; boundary clearance `9.999778782798785e-13`; minimum pair distance clearance `1.999962695453661e-12`.
Both verifiers hash the same candidate bytes: `6285aba27da8b879a7464469d8d223ec987fce3ec83193f7d9aef9cee4fa800b`.

## Submission boundary
Packomania's published hints require radius on line 1, author(s) line 2, then full-precision coordinates. The draft artifact follows that content format. No email/keeper submission was sent in this PDSA: external submission remains an operator-authorized effect, and the exact family filename convention should be confirmed at send time.
