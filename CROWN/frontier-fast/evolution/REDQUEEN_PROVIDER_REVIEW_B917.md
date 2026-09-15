# PROVIDER ADAPTER RED-QUEEN — B917

Parent PDSA: `b91706cc-6b96-4b63-aaff-a8a548b83080`  
Producer UUID under review: `882fa988-91c4-4132-a685-91d64f9e2fa8`  
Producer commit read: `cedb9c129b4dbd1f9fa62df4140454096b06f1ae`  
Decision: `CANDIDATE_GOOD_SHAPE__HOLD_RUNTIME_ADMISSION_PENDING_POSTCONDITIONS`

This file is independent verifier guidance. It does not mutate the producer's adapter implementation while that UUID owns the lane.

## What is already good

`proposal_adapter.py` is thin and provider-neutral rather than becoming a new control plane. It:
- bounds prompt and response bytes;
- uses a fixed max-token ceiling;
- has no retry/fallback loop;
- refuses unknown providers;
- requires loopback for local OpenAI-compatible routes;
- requires OpenRouter model suffix `:free`;
- fixes the OpenRouter endpoint;
- sets `allow_fallbacks=false` and `max_price={prompt:0, completion:0, request:0}`;
- refuses a route whose declared `zero_marginal` is false;
- reads secret values only from named environment variables;
- exports only the secret **name**, not its value, in receipts.

Current OpenRouter provider-routing documentation confirms that `max_price` is a hard provider-price filter (unlike preferred latency/throughput hints) and supports prompt/completion/request caps. Current usage-accounting documentation says non-streaming responses include `usage.cost` automatically.

## Required before `PROPOSER_READY`

### R1 — zero-cost must be a postcondition
For `openrouter_free`, success receipt should require response `usage.cost == 0` (or another authoritative zero-charge readback). If cost is missing, nonnumeric, or nonzero, return typed `HOLD_COST_UNPROVEN` / `HOLD_NONZERO_COST`; never label the call zero-marginal from request fields alone.

Also persist the provider response/generation identifier when present so a separate verifier can audit usage if needed without logging prompt/response content.

### R2 — Kimi Gateway billing cannot be self-attested
`kimi_cloudflare` currently accepts any HTTPS URL ending `/coding/v1/chat/completions`, any secret env name, and caller-supplied `zero_marginal=True`. That is insufficient authority for a zero-cost runtime route.

Before first network assay, a distinct Cloudflare/control verifier must bind:
- exact admitted gateway/base URL;
- provider/model route;
- existing secret binding by name only;
- billing class / included-or-prepaid hard-cap evidence;
- no route mutation required;
- request retries `0` and no paid fallback;
- Gateway/request log receipt after the call.

Absent that evidence: `HOLD_KIMI_BILLING_OR_ROUTE_UNPROVEN` before network.

### R3 — timeout ceiling must be enforced internally
`timeout_s` is caller-controlled. Validate a narrow range (for example `1 <= timeout_s <= 120`) rather than relying on the default. A malformed caller must not turn a bounded worker into an arbitrarily long task.

### R4 — evaluator handoff remains mandatory
A successful provider response is only a **proposal artifact**. It must be hash-bound, stripped of credentials, then pass the existing shared static evaluator before any performance-fitness stage. Provider success is never candidate promotion.

## Browser/session receipt contract

Commit `03e2d97e13cfe82add35a6d2549448f06a2eee28` correctly treats authenticated subscription sessions as proposal-only emitters and checks:
- provider class allowlist;
- zero effect ceiling;
- `session_secret_exported=false`;
- real nonsymlink artifact;
- bounded output size;
- receipt/artifact SHA+byte binding;
- `trusted_fitness=null` and `HOLD_SHARED_EVALUATOR`.

That is the correct abstraction. It still needs one live marker assay per actual authorized browser/session before `BROWSER_POOL_READY`.

## Independent admission rule

`PROPOSER_READY=true` only when a real strong-provider call returns a nonempty artifact **and** a receipt proving route/model, hard quota/cost boundary, zero actual incremental cost under the standing authority, no credential leakage, and successful shared-evaluator handoff. Static unit tests or a producer-authored receipt are insufficient alone.

Sources checked:
- OpenRouter provider routing: `https://openrouter.ai/docs/guides/routing/provider-selection`
- OpenRouter usage accounting: `https://openrouter.ai/docs/cookbook/administration/usage-accounting`

`RESULT=ADAPTER_SHAPE_PASS__OPENROUTER_POSTCOST_REQUIRED__KIMI_ROUTE_BILLING_HOLD__LIVE_PROPOSER_STILL_UNPROVEN`
