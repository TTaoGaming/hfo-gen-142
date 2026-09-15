# Gen142 comma.ai lossless-rate crown candidate

Status: **`SUBMISSION_READY_INTERNAL`**. External submission was **not** performed.

## Frozen battlefield

- Battlefield: comma.ai video compression challenge.
- Public incumbent lineage: `semantic-pose-HPAC_CPR1_polished`, PR #135.
- Incumbent archive: `186,724` bytes, SHA-256 `12cf5d71a94065184f097c3e40dfe9f1db8402a1a76a80efc76a6956fe1e4004`.
- Exact incumbent score reported by PR #135: `0.16226842169958583`.
- Frozen metric: `100*SegNet + sqrt(10*PoseNet) + 25*archive_bytes/37545489`; lower is better.
- This attack is representation-only. It must reconstruct the incumbent F24S model bytes exactly and retain the residual + RC64 tail byte-for-byte.

## Evo lineage

Carrier UUID: `a962ab56-2fb0-492e-a63c-462c9a1cfae3`  
Batch: `comma-evo-20260915T070000Z-a962ab56`  
Producer: OVH x86_64  
Independent verifier: Oracle ARM64

Parent -> mutations -> candidate:

1. Public F26 archive from PR #135.
2. Kill: segmented Rice `1/2/4/8` did not repay its metadata; best non-parent was +3 raw carrier bytes.
3. Exact metadata MOME, 15 combinations:
   - Q8 predictor factor `int16 -> validated uint8`;
   - signed bias `int8 -> signed 6-bit`;
   - basis length `uint16 -> unsigned 12-bit`;
   - Rice `k` byte -> 4-bit.
4. Best metadata phenotype uses all four axes. It removes 28 raw model bytes, but under the local incumbent compressor it still produced `186,728` bytes and therefore failed the published threshold.
5. Successive-halving then evaluated 1,080 legal raw-LZMA2 configurations on that exact phenotype. Winner: normal mode, BT2, 1 MiB dictionary, `lc=0`, `lp=1`, `pb=0`, `nice_len=32`, `depth=8`.
6. Final candidate: **`186,709` bytes**, SHA-256 **`8e5d806cb3da2e2e4bee2087844cbde1382d2e34ccd13e7c181dbc570c231e0f`**.

The candidate is **15 bytes smaller** than the published incumbent while reconstructing the exact incumbent F24S model bytes SHA-256 `4e8d63a98dc7e42ccf17ee7d3fe15a44c8020a3c511838994c6039a673557bde` and retaining residual + RC64 tail SHA-256 `fd3e5617a130d194f65ce1540ed778bedc963ceebc0d5ca1ae64830b425bddb2`.

Because the decoded state is byte-identical, the metric delta is rate-only:

- score delta: `-0.0000099878842968325702190215181376383192132615452151922`
- derived exact score: `0.16225843381528899742978097848186236168078673845478`

This beats the published incumbent's exact score **locally under the frozen representation/evaluator contract**. It is not a public crown until the challenge accepts and publicly attributes a submission.

## Independent replay

The producer did not self-verify the material improvement. An independent Oracle ARM64 process downloaded the public incumbent, independently rebuilt the phenotype from the specification, and obtained the same candidate:

- candidate bytes: `186,709`
- candidate SHA-256: `8e5d806cb3da2e2e4bee2087844cbde1382d2e34ccd13e7c181dbc570c231e0f`
- reconstructed F24S SHA-256: `4e8d63a98dc7e42ccf17ee7d3fe15a44c8020a3c511838994c6039a673557bde`
- unchanged residual + RC64 SHA-256: `fd3e5617a130d194f65ce1540ed778bedc963ceebc0d5ca1ae64830b425bddb2`
- verifier receipt SHA-256: `323645b1df96a34c7212f2c853f5da9212d2521420e7c901ac1bab406a46c766`

`reproduce.py` uses only Python's standard library and the public F26 release. A clean run must produce the exact candidate hash above.

## Strongest falsifier

The OVH liblzma rail cannot byte-reproduce the published incumbent compressor stream: rebuilding the unchanged incumbent on that rail is `186,745` bytes. Therefore local *delta-to-local-rebuild* alone is not admissible evidence of a crown.

The promoted claim does **not** depend on that delta. The candidate's own charged archive is `186,709` bytes, below the published `186,724`, and the independent ARM64 replay produced the same candidate SHA while reconstructing the exact public F24S semantic/model bytes. The remaining real boundary is challenge-side acceptance of the new decoder representation.

## Files

- `producer.json` — lineage, populations, kills, metric and candidate receipt.
- `verifier.json` — independent ARM64 replay receipt.
- `reproduce.py` — clean public reproducer that writes `candidate.zip` and fails closed on any hash mismatch.

## Next machine action

Prepare and verify the minimal decoder integration for `F2M1` against the frozen challenge submission tree, then run a clean-checkout reproduction. Do **not** open the external challenge PR or submit the artifact without Tao authority.
