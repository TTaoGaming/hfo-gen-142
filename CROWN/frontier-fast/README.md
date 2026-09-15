# Frontier Fast Crown Lane — live selection 2026-09-15

Status: `TARGET_SELECTED / SUBMISSION_HOLD_CONTRACT_CONFLICT / CROWN_WON=false`

This lane exists to prevent benchmark whiplash. Selection is based on live third-party readback, not an LLM recommendation frozen in prose.

## Decision

Primary buyer-legible target: `deepseek-v4-flash-gguf-gb10cuda-v1` — DeepSeek V4 Flash 0731 on NVIDIA DGX Spark GB10, llama.cpp CUDA.

Why it displaced the earlier Qwen3.6 recommendation:

- Qwen3.6 GB10 already has a confirmed trusted-runner kernel frontier of about `+9.247%`; it is not an easy empty-board crown.
- DeepSeek V4 Flash GB10 is `active` and, at the 2026-09-15 assay, has `0` eligible trusted-runner kernel records and `0` eligible trusted-runner speculative records.
- Frontier Fast's live track contract itself reports a pinned author-provenance DSpark draft and states that depth 3 measured about `25.51 tok/s` decode versus `17.51` stock on the same GB10 — roughly `1.46x` decode. This is a donor/attack hypothesis, not our measurement and not yet our record.
- Live queue readback at assay time: depth `0`, running `0`, estimated about `22 min/run`.
- The task is highly buyer-legible: inference/kernel optimization for a 284B-total / 13B-active DeepSeek model on NVIDIA hardware, with a third-party trusted runner.

Fast-crown backup: `maple-preview-gguf-gb10cuda-v1`. It is also active with an empty trusted-runner board and has a strong public local finding, but the DeepSeek/NVIDIA result is more legible to a general AI-infrastructure buyer.

## Red-Queen finding: submission is currently HOLD

The live DeepSeek contract is internally inconsistent:

- `speculative.draftModel.specType` says `draft-dspark`.
- `speculative.draftModel.note` also describes `--spec-type draft-dspark --spec-draft-n-max 3`.
- the generated `speculative.howToRun` block currently says `draft-dflash`.

The upstream current `benchmark.json` / `AGENTS.md` list both `draft-dspark` and `draft-dflash` as distinct accepted llama.cpp speculative types and state that the track contract chooses the pinned draft. Therefore we do **not** guess which published field is stale and do **not** submit until this contradiction is resolved by an authoritative intake/dry-run or corrected live contract.

Run `python3 CROWN/frontier-fast/contract_assay.py`; current expected result is exit `2` / `HOLD_PUBLISHED_CONTRACT_CONFLICT`. If it turns green later, re-run the live target assay before spending or submitting.

## Deterministic gates

1. `python3 CROWN/frontier-fast/live_assay.py` must return `PASS_CANDIDATE` immediately before work begins.
2. `python3 CROWN/frontier-fast/contract_assay.py` must return `PASS` before an external submission is allowed.
3. A local/rented-GB10 mutation is only a champion candidate after the official track correctness gates and reproducible paired A/B measurement pass.
4. A Frontier Fast trusted-runner row is the external fitness receipt. A local number, API description, or HFO claim is not a crown.
5. `CROWN_WON=true` only after a public trusted-runner leaderboard readback shows Tommy Tai / the admitted submitting identity at rank #1 for the exact track/board, with the associated patch/artifact addressable.

## Suggested first search population after the contract HOLD clears

Do not start with broad kernel surgery. The live contract already exposes a pinned speculative donor. Use a bounded successive-halving experiment:

- control: stock/no speculation;
- DSpark depth candidates centered on the documented depth `3` (for example 1, 2, 3, 4, 5) only if supported by the intake contract;
- optional separate `ngram-cache` candidate because it requires no second model;
- never combine speculative and kernel changes in one candidate; Frontier Fast explicitly ranks them on separate boards;
- cheap local/rented-GB10 falsification first, then submit only the best reproducible candidate(s), respecting platform concurrency/queue limits.

## Human / authority boundaries

The swarm may research, clone public code, create local configs/patches, run zero-effect assays, and package a champion. Tao/manual authority remains required for any new paid GPU rental/account purchase unless already pre-authorized, credential entry, and the final external submission until an explicit standing authority is established.

No new scheduler, queue, or swarm control plane belongs in this lane. It is just `WorkItem -> bounded worker -> verifier -> external evaluator receipt`.

## Primary evidence surfaces

- `https://frontier.fast/api/tracks`
- `https://frontier.fast/api/leaderboard?contract=<track>&technique=<kernel|speculative|all>`
- `https://frontier.fast/api/findings?track=<track>`
- `https://frontier.fast/api/recipe?track=<track>`
- `https://frontier.fast/api/queue`
- upstream public repository: `metaspartan/frontier-fast`

Re-read them live. This file is a checkpoint, not authority over a moving external leaderboard.
