# Frontier Fast crown runbook — tonight

Status: `READY_TO_PREPARE / EXTERNAL_SUBMIT_MANUAL / NO_CROWN_CLAIM_YET`

This runbook is deliberately narrow. Do not reopen battlefield discovery during the execution window unless a live assay fails closed.

## Objective

Obtain one independently verified, public #1 Frontier Fast row on a buyer-legible NVIDIA track, with a reproducible patch and timestamped third-party result. Being later displaced does not invalidate the historical receipt.

Primary: `deepseek-v4-flash-gguf-gb10cuda-v1`.

Fallback: `maple-preview-gguf-gb10cuda-v1` **only if** the DeepSeek live contract remains contradictory at the moment we are ready to spend a runner slot.

## Zero-trust preflight

Run immediately before any candidate work or submission:

```bash
python3 CROWN/frontier-fast/survey.py
python3 CROWN/frontier-fast/live_assay.py
python3 CROWN/frontier-fast/contract_assay.py
```

Interpretation:

- `live_assay.py = PASS_CANDIDATE` means DeepSeek is still active with no verified non-baseline record. It does **not** mean HFO has a winning patch.
- `contract_assay.py = HOLD_PUBLISHED_CONTRACT_CONFLICT` means do not guess `draft-dspark` vs `draft-dflash` and do not buy a runner slot with ambiguous config.
- Any live non-baseline record appearing on the board changes the incumbent and forces a re-score before submission.

## Human boundaries before first submit

These are account/credential/irreversible boundaries, not runtime CPR:

1. Sign in to Frontier Fast with the chosen identity and mint/save the submit-only token. Do not paste it into chat or public GitHub.
2. Create/fork a reachable `metaspartan/frontier-fast` repository under the submitting GitHub identity. The trusted runner clones `repositoryUrl` and fetches `commitSha`; local-only commits are rejected.
3. Final external `frontierfast submit ...` remains a manual approval until standing submit authority is explicitly granted.

Everything else should be swarm/machine owned.

## Important cost correction

**A rented GB10 is not required for the first official canary.** Frontier Fast already supplies the trusted DGX Spark runner. Current public CLI says one submission claims a physical GPU for roughly 22 minutes. The live queue has recently been empty.

Rent exact GB10 hardware only when local iteration throughput justifies it. Renting helps evolve many mutants before consuming official slots; it is not required to get the first official verdict.

Therefore the cheapest first crown attempt can be effectively `$0` incremental GPU rental, plus whatever LLM/API capacity is already available, provided we have a plausible patch/config and a Frontier token/fork.

## Primary DeepSeek path

Current state is `HOLD_PUBLISHED_CONTRACT_CONFLICT` because the live contract simultaneously publishes:

- pinned draft `specType = draft-dspark`;
- note/examples describing `draft-dspark`;
- generated `howToRun` using `draft-dflash`.

Do not resolve this by LLM vote. Release only after one authoritative source/intake path converges. Once resolved:

1. Build a candidate in a Frontier Fast fork; keep speculative-only and kernel-only changes separate.
2. Smoke-test that the chosen lever actually fires.
3. Use the official correctness gates; do not optimize toward the threshold.
4. If local exact hardware is unavailable, one official canary is acceptable only for a high-prior donor candidate; record nulls/failures in the findings ledger.
5. If the trusted runner gives a positive reproducible delta, use successive halving before broad mutation.

## Deterministic Maple fallback

Fallback trigger: DeepSeek remains HOLD when credentials/fork are ready and the external runner queue is available.

Prepared donor-derived mutant:

`CROWN/frontier-fast/maple-gb10/0001-aarch64-split-default-thread-pools.patch`

It reconstructs the public `WON` finding `maple-gb10-decode-is-cpu-bound`. The platform's finding reports nearly 2x decode while preserving prefill/TTFT and bit-identical perplexity. HFO has **not** reproduced those performance numbers and must not inherit them.

Before submit:

- patch applies cleanly to `deepgrove-ai/llama.cpp@8ce8ca6c6d370b6235dfa8e2a0611a9adb6d77d1`;
- place the patch in the Frontier Fast candidate repository at `Sources/patches/maple-preview-gguf-gb10cuda-v1/`;
- verify the commit is pushed/reachable;
- publish useful notes identifying the lever and measurement expectations;
- final submit manually.

## Success receipt

`CROWN_WON=true` only when all are true:

1. Frontier Fast trusted runner accepts the candidate;
2. result beats the exact live incumbent on the intended board;
3. public leaderboard shows the submitting identity at rank #1;
4. candidate commit/patch is addressable and reproducible;
5. timestamp, track ID, score, and public row are captured into `#13` and a case-study artifact.

Local benchmarks, platform donor descriptions, HFO prose, or an LLM saying “world record” are insufficient.

## Evolution loop after first official signal

Use successive halving, not branch explosion:

`donor mine -> 6–12 diverse mutations -> cheap/static falsification -> local exact-hardware A/B when available -> top 2–3 official canaries -> independent reproduction -> promote/kill`

Stop conditions:

- live battlefield becomes occupied by a materially stronger incumbent;
- correctness gate repeatedly fails;
- two generations produce no reproducible positive delta;
- API/runner budget hits the declared ceiling;
- provenance or submission contract becomes ambiguous (`HOLD`).

No new scheduler, queue, registry, or state owner is part of this runbook.
