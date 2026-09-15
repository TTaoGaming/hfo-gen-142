# GB10 FITNESS PREP — B917 NO-SPEND RUNBOOK

Parent PDSA: `b91706cc-6b96-4b63-aaff-a8a548b83080`  
State: `READY_NO_SPEND / NO_MACHINE_RENTED / CROWN_WON=false`  
Target: `maple-preview-gguf-gb10cuda-v1`

This file prepares the exact fitness boundary. It does **not** authorize a rental, payment, Frontier account action, token creation, or external submission.

## Frozen inputs

- Source pin: `deepgrove-ai/llama.cpp@8ce8ca6c6d370b6235dfa8e2a0611a9adb6d77d1`.
- HFO reconstruction: `CROWN/frontier-fast/maple-gb10/0001-aarch64-split-default-thread-pools.patch`.
- Static evaluator: `CROWN/frontier-fast/evolution/shared_eval.py`.
- Live Frontier readback at `2026-09-15T23:03Z`: public kernel leaderboard contained only the pinned baseline for Maple; queue depth `0`, running `0`, estimated `22 min/run`.
- Live research donor `maple-gb10-decode-is-cpu-bound` reports its measured system-level lever; that public donor result is **not inherited** by the HFO reconstruction until reproduced.

## Admission gate for a rented/local fitness worker

A worker may call itself `EXACT_GB10_FITNESS` only when the receipt captures all of:

1. `uname -a`, `uname -m = aarch64`, hostname and UTC.
2. GPU/device readback proving NVIDIA DGX Spark / GB10 class and CUDA availability.
3. CPU topology/core count and RAM/disk readback.
4. exact source commit and candidate patch SHA256.
5. compiler/CMake/CUDA versions plus full build exit code.
6. persistent work root outside `/tmp`.
7. zero benchmark/submission credentials visible to candidate code.

Anything else is `DIRECTIONAL_FITNESS_ONLY` and cannot promote a Frontier champion.

## A/A noise calibration before A/B

Before candidate timing, build stock twice from the same pinned source and run the same server-shaped harness as separate whole-process launches. Rotate launch order and persist raw observations. Do not hard-code a fantasy noise floor: calculate it from the rented box. HOLD if the baseline is thermally or operationally unstable.

Required receipt fields:
- per-run decode, prefill, TTFT;
- median and dispersion for each metric;
- model/perplexity/correctness output;
- process launch order;
- box load/temperature telemetry if available;
- harness/source/model hashes.

## First paired assay

Arms:
- `S`: stock pinned source.
- `A`: HFO reconstructed split-thread-pool patch.

Run alternating whole-process launches (`S,A,A,S,...`) rather than alternating iterations inside one process. Measure the exact same corpus/window for both arms. Candidate promotion requires:

- build PASS;
- correctness/perplexity gate PASS;
- decode, prefill and TTFT all reported, never a decode-only narrative;
- repeated positive weighted score outside the empirically observed noise envelope;
- a second verifier reproduces the candidate from source + patch hashes.

No A+B composition is attempted until a distinct `B` mutation exists and both A and B separately have receipts. Composition is not free evidence.

## Successive-halving policy

1. static evaluator kills malformed/unbuildable candidates;
2. directional CPU/near-hardware tests may rank gross losers only;
3. exact GB10 paired fitness receives a small survivor set;
4. only repeated positive candidates reach independent verifier;
5. only independently reproduced champions reach the Frontier submitter leaf;
6. public leaderboard readback is required before `CROWN_WON=true`.

## Spend boundary

Current mission policy is zero incremental spend unless Tao explicitly authorizes a new spend boundary. Therefore this runbook stops at `READY_NO_SPEND`. If Tao authorizes a rental, the machine must record provider, quoted hourly rate, hard duration/cost cap, termination time and teardown receipt before admitting the worker.

`RESULT=GB10_ASSAY_CONTRACT_READY__NO_SPEND_PERFORMED`
`LOCAL_FITNESS_READY=false`
`CROWN_WON=false`
