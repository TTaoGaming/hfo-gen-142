# Maple Preview GB10 — deterministic fallback crown mutant

Status: `FALLBACK_ONLY / DONOR_DERIVED_MUTANT / OFFICIAL_VERIFICATION_REQUIRED / CROWN_WON=false`

This is **not** a battlefield switch by intuition. The primary buyer-legible lane remains DeepSeek V4 Flash GB10 while its public contract contradiction is being resolved. Maple becomes eligible only under an explicit fallback gate: DeepSeek remains `HOLD_PUBLISHED_CONTRACT_CONFLICT` when we are ready to buy an external runner cycle.

## Why this fallback exists

The live Frontier Fast track `maple-preview-gguf-gb10cuda-v1` is active and has only the pinned baseline on its public kernel board. Its live findings ledger contains a `WON` donor named `maple-gb10-decode-is-cpu-bound` reporting:

- stock decode around 53.4 tok/s;
- candidate decode around 104.4 tok/s;
- median decode ratio `1.9556`;
- prefill ratio `0.9975`;
- TTFT ratio `1.0045`;
- projected score about `1.546`;
- perplexity bit-identical `22.4217 -> 22.4217`.

The public finding attributes the gain to splitting the default CPU thread pools on the GB10's aarch64 hybrid CPU: keep batch/prefill at the full math-core count, but cap default generation to seven threads because the TQ2_0 fallback matvecs are CPU-bound and barrier-heavy.

## What HFO actually built

`0001-aarch64-split-default-thread-pools.patch` is an independent reconstruction of that published lever against the track's pinned engine source:

`deepgrove-ai/llama.cpp@8ce8ca6c6d370b6235dfa8e2a0611a9adb6d77d1`

It is **not** claimed to be the original unpublished winning patch. The reconstruction preserves explicit `-t` / `-tb` behavior and changes only the both-default case on Linux aarch64:

1. resolve the batch pool independently to the full math-core count;
2. resolve the generation pool;
3. cap the default generation pool at seven threads.

The mutation does not alter model weights, evaluator code, or arithmetic kernels.

## Verification ladder

- `git apply --check` against the exact pinned source: required.
- ARM64 compile of `llama-server` with CUDA disabled: syntax/build portability check only; **not performance evidence**.
- exact GB10 local A/B with the platform's current measurement discipline: required before calling it a local champion.
- Frontier Fast trusted runner: required for any crown claim.

The live platform finding is donor evidence. HFO's reconstructed patch does not inherit the donor's measured score until reproduced.

## External submission boundary

To submit, the patch must live in a reachable commit of a Frontier Fast fork under `Sources/patches/maple-preview-gguf-gb10cuda-v1/`, with a Frontier Fast submit token and final manual approval while that authority remains human. Do not submit this HFO repository directly; it is a staging/evidence surface, not a Frontier Fast candidate repository.
