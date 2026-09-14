# H3 — Packomania public-proof effect packet

**Actor UUID:** `099db845-7255-443d-8b72-ec22d743e826`  
**Lane:** H3 — packing public-proof submission  
**PDSA window:** 2026-09-14 ~14:00–14:10 UTC  
**Status:** `PACKED_TO_EXTERNAL_EFFECT_BOUNDARY__HOLD_SEND_AUTHORITY`  
**Fitness:** externally verifiable progress per operator-minute  
**TAO_RELAY_REQUIRED:** `false`  
**tao_context_ferry_bytes:** `0`

## PLAN

Recover the existing GEN140 packing evidence instead of restarting search. Falsify stale candidates against the live public Packomania surfaces, select the highest-readiness candidate that can plausibly produce a fast third-party receipt, bind it to exact existing artifacts, and reduce the remaining work to the keeper's native submission format. Reuse only existing GitHub evidence, Python stdlib/gzip replay, and Packomania's documented `.pck` format. No scheduler, queue, daemon, alternate ledger, or new control plane.

## DO

### 1. Kill stale former leaders before packaging

The live CSQV table observed 2026-09-14 now shows:

- N117: `5.699606654188`
- N118: `5.723940934671`

Therefore the older GEN140 N117 candidate `5.6742622579724105` and N118 candidate `5.6870220652628776` are no longer served-table wins. They are **not** H3 submission candidates.

Public source: <https://packomania.com/csqv/csqv.html>

### 2. Select CRC800 N389 as the fastest defensible public-proof edge

The live served CRC800 table observed 2026-09-14 shows:

- N389 served radius: `0.023840209433828469161245150244`
- N390 served radius: `0.023848376539816648640120148446`

Deleting one circle from a valid N390 equal-circle packing preserves containment and all remaining pairwise non-overlap, so the N390 geometry gives an N389 witness at the same radius. The existing GEN140 evidence already materializes that deterministic deletion and binds it to exact bytes.

Public source: <https://packomania.com/crc_800/crc.html>

Existing ResultRecord: `G140-RR-CRC800-N389-R1`  
Canonical reducer patch: <https://github.com/TTaoGaming/hfo-gen-140/issues/331#issuecomment-5646930497>  
Independent verifier: <https://github.com/TTaoGaming/hfo-gen-140/issues/315#issuecomment-5635270495>  
Fresh source-binding receipt: <https://github.com/TTaoGaming/hfo-gen-140/issues/315#issuecomment-5646928722>

Current evidence ceiling from #331:

- `incumbent_value_current_served = 0.023840209433828469161245150244`
- `candidate_value_printed = 0.023848376539816648640120148446`
- `relative_delta_pct ≈ +0.034257694%`
- `replay_state = SOURCE_BYTES_BOUND_TO_EXISTING_INDEPENDENT_REPLAY_1`
- `currentness_state = CURRENT_SERVED_PACKOMANIA_ROW_WIN__GLOBAL_CURRENTNESS_UNKNOWN`
- `keeper_verification_state = NOT_REQUESTED`
- `public_attribution_state = NONE`

This is a **current-served-table win**, not a claim of global optimality or a world record.

### 3. Bind the exact keeper-facing source material

Pinned producer bundle: draft PR <https://github.com/TTaoGaming/hfo-gen-140/pull/345>, commit `28c3ba94bf88106cbf0cf1dd73a9aa1b88c506bc`, directory `evidence/packing/crc800_n389_89e310e4/`.

Exact artifacts already present there:

- `artifacts/n389_coordinates.txt.gz`
  - Git blob `40af21745ce4897808d0fee99e93e3311166012d`
  - stored gzip SHA256 `ea8a1e5cb5ff47267cf6ed2c5b8cd4e9d2871fd1bcb63364359234bc28e36967`
  - decoded coordinate SHA256 `d388ebc334df5e5c7fb2b03cd120623e15c06362876993c87362813837d588ca`
  - decoded shape: `27,507` bytes, `389` index/x/y rows
- `artifacts/conservative_radius.txt`
  - radius `0.023848376538816648640120148446`
  - SHA256 `d69decb89b5b33f04fde9dac3839e95b102466b9264857025aec15b01b430b05`
- `artifacts/backup_radius.txt`
  - radius `0.023848370000000000000000000000`
  - SHA256 `7e098427279804408f8a88ce595b2c2ffb5aee52b97939c2616f44cf9a768616`

The PR's stdlib-only replay reports exact validation of all `75,466` pairs and `1,556` wall constraints; the later #331 reducer binds fresh source bytes and one independent replay. Preserve that distinction: PR #345 itself was producer-side; the later ledger patch is the stronger combined state.

### 4. Reduce external submission to Packomania's native format

Packomania's current formatting instructions say:

1. one `.pck` file per packing;
2. first line = radius for equal circles/spheres;
3. second line = author name(s), comma-separated for multiple authors;
4. coordinates begin on the third line;
5. whitespace-separated columns; preserve as many decimals as possible;
6. multiple files may be zipped.

Public format source: <https://www.packomania.com/hints.html>

**Do not invent the second line.** The N389 witness is a deterministic derivative of David W. Cantrell's credited N390 geometry. The current evidence explicitly preserves Cantrell donor credit and does not establish accepted attribution semantics for a derivative submission. A syntactically valid `.pck` with an unadjudicated author line would be a semantic failure.

The effect packet is therefore intentionally frozen one field before submission:

```text
line 1: 0.023848376538816648640120148446
line 2: <HOLD — keeper/author-credit semantics must be explicitly authorized>
line 3+: x y coordinates derived losslessly from the exact 389-row hash-bound artifact
```

Before any authorized send, replay the pinned coordinate+radius bytes first; only then transform index/x/y rows into the keeper's x/y coordinate section. Regeneration is not a substitute for byte replay.

### 5. Runtime continuity check without credential ferrying

Both VPS Desktop Commander endpoints were recoverable in this episode. Oracle VPS UTC was `2026-09-14T14:06:40Z`. A disposable direct clone of the private GEN140 repository failed closed at GitHub authentication (`could not read Username for 'https://github.com'`). No credential request, secret ferry, laptop dependency, alternate login route, or new control plane was introduced. The authorized GitHub connector supplied the pinned evidence instead.

## STUDY

### What survived falsification

- **CSQV N117/N118:** killed as current submission candidates by today's served table.
- **CRC800 N389:** survives as a source-byte-bound, independently replayed improvement over the **currently served Packomania N389 row**.
- **External proof route:** unusually short because Packomania already publishes the target table and native file format, and a keeper response/public row would be third-party evidence.

### What remains UNKNOWN / cannot be promoted

- Global current-best status beyond Packomania's served table is unknown.
- The CRC800 family page says last update `25-Jun-2013`; age is a material stale-table risk.
- The geometry is derivative of a credited N390 donor, not an original optimized discovery by this swarm.
- Keeper-compatible attribution/credit for that derivative is unresolved.
- Keeper acceptance and public attribution are absent.

Therefore the claim ceiling is:

`SOURCE_BYTES_BOUND__INDEPENDENT_REPLAY_1__CURRENT_SERVED_PACKOMANIA_ROW_WIN__DERIVATIVE_CREDIT_HOLD__NO_GLOBAL_RECORD__NO_KEEPER_ACCEPTANCE__NO_PUBLIC_ATTRIBUTION`

## ACT

**H3 is internally terminal for this bounded PDSA.** More numerical search is lower-value than crossing the existing external verification boundary correctly.

The exact next edge, under separate explicit authority for the outside effect, is:

1. replay pinned PR #345 bytes + conservative radius;
2. freeze a same-session fresh N389/N390 Packomania table read;
3. adjudicate the derivative author/credit line without erasing David W. Cantrell's donor credit;
4. emit exactly one keeper-native `.pck` (ZIP only if useful);
5. make exactly one keeper contact;
6. preserve the keeper response and public Packomania row/credit as the external receipt.

No external email, submission, spend, merge, deploy, scheduler mutation, provider/account mutation, or public-record claim was made in this episode.

### Auxiliary Harbor receipt

A separate future-Harbor-leaderboard packaging gate was also recovered and committed at `experiments/harbor/H3_PUBLIC_PROOF_SUBMISSION.md` (`15014ccd2f834d5502700162c6120047dca01d25`). It is useful for the Harbor finalist later, but it is **not** substituted for this packing H3 lane.
