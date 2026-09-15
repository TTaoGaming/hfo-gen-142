# Frontier Fast evolution — resource / adapter requirements

Snapshot UTC: `2026-09-15T22:37Z`

Purpose: remove Tao from the hot loop for Frontier Fast crown search while preserving human-only account/TOS/spend/final-submit boundaries.

## New operator-supplied capacity
User reports these proposer sources are available or can be made available:
- Cloudflare API / Workers AI capacity.
- Kimi.ai API with frontier Kimi 3-class model access.
- OpenRouter free frontier-model capacity.
- ChatGPT account A and account B subscription sessions.
- Codex and other subscription-backed coding agents.
- User is willing to rent an exact/near benchmark box tonight.

These are **capacity claims pending machine readback**; never publish keys/tokens. API capacity existing means the strong-proposer blocker is now primarily **adapter + secret admission**, not model availability.

## Required proposer plane
Use one provider-neutral proposal contract:
`mission + parent artifact + evaluator feedback + mutation budget -> candidate artifact + provenance + provider/model + cost/quota receipt`.

Preferred order:
1. API workers first: Cloudflare, Kimi.ai, OpenRouter. They are deterministic to automate and should be the primary unattended proposal path.
2. Subscription/browser workers second: ChatGPT A/B, Codex, other logged-in agents. Treat them as replaceable emitters, never as execution authority.
3. Local Ollama remains free scout/fallback only; the 2-core Granite 3B path was empirically too slow/unreliable for real Shinka/OpenEvolve mutation prompts.

Every provider adapter must enforce: explicit provider/model allowlist, timeout, max tokens, hard spend/quota ceiling, no silent paid fallback, structured provenance, and credential stripping before candidate evaluation.

## Browser-adapter requirement
Need one thin browser adapter for existing authenticated subscription sessions rather than embedding browser logic in the control plane.

Minimum contract per account/session (`chatgpt-A`, `chatgpt-B`, `codex`, others):
- input: bounded proposal task + parent/evaluator receipts;
- effect ceiling: proposal text/code only; no external submit/payment/account/settings action;
- preserve authenticated browser profile on the authorized host; do not export password/2FA/session cookies into GitHub/Cloudflare;
- output: response artifact, account/session label, model/mode if observable, UTC start/end, timeout/error, content SHA256;
- one active task per browser session unless proven safe;
- deterministic timeout/retry ceiling; browser failure returns typed HOLD/FAIL and never blocks the reducer;
- browser outputs go through the same shared Frontier evaluator before promotion.

The browser adapter is **supplemental capacity**, not the semantic owner, scheduler, evaluator, or Frontier submitter.

## GPU fitness box — what to rent tonight
For `maple-preview-gguf-gb10cuda-v1`, preferred = **exact NVIDIA DGX Spark / GB10** because the leading Maple donor lever depends on the GB10 ARM64 CPU/thread-pool + CUDA system shape. A generic H100/4090/5090 may be useful for compile/filtering but is not equivalent fitness for this target.

Required characteristics:
- NVIDIA GB10 / DGX Spark class, CUDA `sm_121` compatible;
- ARM64 host CPU matching the track as closely as possible;
- ~128 GB unified memory preferred (exact Spark class); Maple itself is small, but exact-system fidelity matters more than minimum VRAM;
- Linux, SSH access, git, Python 3.11/3.12, `uv`, CMake/Ninja, CUDA toolkit/compiler, build-essential;
- >=100 GB free persistent disk for pinned source, model/cache, multiple isolated worktrees and receipts;
- outbound HTTPS to GitHub / model-download sources / Frontier Fast; no broad inbound exposure beyond SSH/Tailscale as needed.

If exact GB10 is unavailable, label a near-GPU run `DIRECTIONAL_FITNESS_ONLY`; never promote it as Frontier-equivalent performance proof.

## Existing machine roles
- Cloudflare/Sigrun DO: mission state, timeout/retry semantics, reducer state — **not GPU fitness**.
- Oracle ARM64 VPS: primary evolution controller, shared static evaluator, persistent population/checkpoint state.
- OVH x86_64 VPS: secondary compile/falsifier/controller capacity.
- Lenovo/laptop: currently useful as authenticated browser/session host, but the intended autonomous crown loop must not depend on it for semantic state.
- Rented GB10: dense local fitness worker.
- Frontier Fast trusted runner: external promotion/verifier lane; use for survivors, not inner-loop population fitness.

## Secret / authority placement
- API keys: private controller/worker secret store only; never public GitHub, candidate worktree, model prompt, or evaluator artifact.
- Frontier `GAINZ_TOKEN`: submitter leaf only.
- Browser account sessions: remain on authorized browser host; never serialize cookies/session secrets into the swarm.
- Candidate code receives zero provider/controller/submit credentials.
- Human retains: account/TOS/2FA/payment/new spend and first irreversible Frontier submission approval.

## Shortest execution order
1. Wire one API proposer first (prefer already-available Kimi.ai or OpenRouter/Cloudflare) into GEPA/shared evaluator and prove one real mutation -> static selection cycle.
2. Add browser adapters for ChatGPT A/B + Codex as extra proposal emitters; do not wait on them to start API evolution.
3. Rent exact GB10 and install the thin fitness worker; run stock + Maple A + Maple B + A+B paired local assays.
4. Feed measured diagnostics back into GEPA/Shinka/OpenEvolve; successive-halve populations.
5. Send only independently reproduced champions to Frontier trusted runner.
6. Separately promote `cdev-control#5` and bind the evolution capsule so wake/reconcile/propose/evaluate/continue completes two natural cycles with `TAO_INTERVENTION_COUNT=0`.

## Acceptance
`PROPOSER_READY` = at least one strong API provider completes proposal -> shared evaluator -> reducer with a quota/cost receipt.

`BROWSER_POOL_READY` = A/B/Codex each can receive one bounded task and return a hash-bound artifact without Tao context ferrying.

`LOCAL_FITNESS_READY` = exact GB10 reproduces stock baseline within an admitted noise band and can evaluate A/B/A+B without manual environment surgery.

`CROWN_READY` = repeated local champion + independent verifier + Frontier trusted-runner positive result; still no crown claim until public board readback.

`CROWN_WON=false` until third-party public evidence exists.
