# GEN142 Cell-0 Recovery / Handoff

State: CHECKPOINTED_FOR_FRESH_CARRIER
Observed: 2026-09-14
Owner surface: `TTaoGaming/hfo-gen-142`
Trunk: issue #6

## Recovery order
1. Read issue #6 newest-first.
2. Read this file.
3. Read `cell0/src/index.js` and `cell0/wrangler.jsonc` from `main`.
4. Probe actual tools/authority; do not inherit a prior carrier UUID or authority.
5. Treat Worldweaver as regeneration context only; `REGROW != ADMIT`.

## What exists now
A deliberately small Cloudflare Durable Object cell is deployed as worker `hfo-gen142-cell0`.
Public status surface: `https://hfo-gen142-cell0.tommytai3.workers.dev/status`.
Runtime path is intentionally minimal: Durable Object persisted state + DO Alarm + one read-only GitHub observation target (issue #6). Desktop Commander/VPS/Lenovo are deployment/debug callers, not required for autonomous wake cycles after deployment.

Source: `cell0/src/index.js`.
Wrangler config: `cell0/wrangler.jsonc`.
Initial implementation commit: `5846d37` (`Add tested Cell0 durable actor implementation`).

## Proven assays
- Autonomous DO alarm wake and checkpoint progression without per-cycle operator calls: PASS.
- Injected single-cycle failure followed by autonomous recovery: PASS in prior assay (`failures=1`, later cycle progressed, `lastError=null`).
- Worker redeploy during an active logical run: PASS; same durable object state continued and bounded run completed.
- External-state observation: PASS. After issue #6 changed from 1 to 2 comments, Cell-0 independently observed the newer `updated_at` and changed persisted digest from `3b80d9fe...` to `2f55dd48...`.
- Fresh Oracle VPS readback of deployed worker status: PASS.

## Current readback at checkpoint
Oracle VPS fetched `/status` successfully. Returned terminal state `SUCCEEDED`, `cycles=5`, `failures=0`, `targetCycles=5`, `lastWorkId=cell0:5`, `lastSource=alarm`, `alarmAt=null`.
Last observed trunk state: issue #6, comments=2, updated_at=`2026-09-14T12:27:02Z`.
Last digest: `2f55dd48bfcf29efcd43c9b3a88df2960980bf6226881f6741257e10a68aa68c`.

Important: current status also reports invariants `exactlyOnceInternal=false`, `noDeadletters=false`, `boundedAttempts=false`. Do not promote these properties; they are explicitly unproven/false in current instrumentation.

## Known blockers / nonclaims
- 24h / 100-cycle / 7-day soak: NOT PROVEN.
- Model reasoning step: NOT PROVEN.
- Protected external write effect: NOT PROVEN.
- Exactly-once external effect: NOT PROVEN.
- Dead-letter policy and bounded retry contract: NOT PROVEN.
- Workflow multi-step continuation: NOT PROVEN.
- Evolution/swarm: deliberately NOT on the Cell-0 critical path yet.
- OVH Desktop Commander path has been intermittent; do not rely on it for Cell-0 runtime claims.
- Remote Desktop Commander multi-device calls require explicit `deviceId`; G2 admitted/default VPS path remains separate from Cell-0.

## Next exact task
Do not add architecture. Run the next reliability gate on the existing Cell-0:
1. Add/verify explicit counters for attempts, successes, failures, retries, duplicate work/effects, deadletters, and manual interventions.
2. Make retry ceiling/dead-letter behavior bounded and observable.
3. Run >=100 scheduled cycles, including deliberate failure and redeploy perturbations.
4. PASS only if Cell-0 completes with `manual_interventions=0` and no duplicate accepted external effects.
5. Then run a 24h soak before adding one model call.

Only after the reliability gate passes, add exactly one new capability: one model call producing schema-validated judgment from the observed GitHub change. No swarm, evolution, A2A, custom scheduler, or second control plane until a measured Cell-0 failure justifies it.

## Pickup contract
Fresh carrier: generate a fresh carrier episode UUID; recover issue #6 + this file newest-first; probe actual tools; preserve the minimal Cell-0 architecture; run one bounded PDSA reliability cycle; checkpoint evidence back to #6 and update this file only when canonical state materially changes. `TAO_RELAY_REQUIRED=false`.