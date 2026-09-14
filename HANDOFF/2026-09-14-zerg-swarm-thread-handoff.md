# GEN142 Zerg Swarm thread handoff

Observed UTC: 2026-09-14T13:46:58Z
Carrier episode UUID: 47070813-e8f2-43da-9903-c5b5c8be8863
Thread status: TERMINAL_HANDOFF__DO_NOT_EXPECT_CHAT_RETURN
Tao relay required: false

## Executive state
The architecture is strong enough to freeze. The system is not missing another scheduler/control plane; it is one integration seam short of a self-sustaining virtual-actor cell.

Canonical Zerg mapping:
- Burrow/Cell = durable state owner
- Roach = durable work lineage
- Hluti/carrier = disposable cognition
- phenotype = late-bound role
- provider/model/tool = replaceable executor
- ConsumerAck = accepted downstream result
- GitHub/Worldweaver = audit/recovery membrane, not hot concurrent state

Target cycle:
`WAKE -> CLAIM work_id -> RESOURCE LEASE -> OBSERVE -> ONE MODEL DECISION -> ONE BOUNDED TOOL ACTION -> EVALUATE -> COMMIT -> ConsumerAck -> RELEASE -> SLEEP`

## Proven live
1. `hfo-gen142-cell0` is deployed on Cloudflare with SQLite Durable Object state + alarms. Existing issue #6 already records injected-failure recovery, redeploy recovery and useful GitHub mutation detection.
2. This branch independently called Cell-0 from the Oracle VPS and started `cycles=5&interval_ms=2000`. It completed 5/5 autonomous alarm cycles, zero failures, `lastWorkId=cell0:5`, `lastSource=alarm`, completed at `2026-09-14T12:27:58.380Z`, and cleared its alarm. No Tao/Lenovo runtime dependency was required for those cycles.
3. G1 synthetic Cloudflare durability/idempotency remains scoped PASS: deterministic work identity survived caller replacement/redeploy and duplicate replay admitted exactly one effect.
4. Portable Hatchery already exists and has bounded adapters on laptop, Oracle ARM64 and OVH x86_64. The two-generation packing assay ran on Oracle under native finite resource limits; it proved sequential finite evolution mechanics, not unattended swarm autonomy.
5. Oracle currently runs existing GitHub Actions runner services for `TTaoGaming/cdev-control` and `TTaoGaming/hfo-gen-140`. Gen142's own Oracle workflow has been queued/pending because no eligible self-hosted runner is registered to `hfo-gen-142`. Compute exists; repo/admission ownership is misaligned.

## Current failure / highest-value edge
The open seam is cognition/tool execution *inside* each durable Cell-0 work cycle.

Oracle local cognition assay attempted two generations using existing Ollama `qwen3.5:2b-q4_K_M` with recovered HIVE_R0 + Worldweaver context. Generation 1 timed out at 180 seconds. During the timeout `ollama ps` showed both Qwen and Granite resident concurrently, each reporting 100% CPU with context 4096. Treat this as resource-contention/admission evidence, not proof either model is intrinsically unusable.

Therefore current highest-value work is NOT another framework. It is one admitted model call and one admitted bounded tool/evaluator action per deterministic work_id behind explicit shared-resource/provider admission.

## PDSA reduction
PLAN: make Cell-0 perform one useful `NO_EXTERNAL_EFFECT` virtual-actor decision per durable work item, concurrency=1.

DO next:
- Prefer the intended AI Gateway -> Kimi one-call sentinel if that is the canonical cognition path; otherwise give Oracle Ollama exclusive admission and first prove one short deterministic inference before attempting two generations.
- Bind each model call to provider/model/runtime fingerprint, timeout, context/token budget and resource lease.
- Reuse an existing native VPS runner/service owner; repair repo/runner admission alignment instead of using Desktop Commander as the swarm scheduler.
- Keep Cloudflare DO/Workflow as hot durable actor/work owner and reducer/ConsumerAck/idempotency semantics from G1.

STUDY only: scheduled cycles attempted/completed, model latency/timeouts, tool failures, retries, duplicate accepted effects, CPU/RAM/disk, operator interventions, ConsumerAcks. Installation/reachability is not readiness.

ACT gate before fan-out:
- >=100 scheduled useful cycles / >=24h with zero Tao CPR
- injected model timeout and tool failure recover at failed step only
- Worker redeploy during active work resumes
- duplicate trigger/replay yields `accepted_effect_count == 1`
- fresh caller can read state with actor/work identity only
- then 7-day single-cell soak
- only then hatch Cell-1 / broad Zerg fan-out

## Kill patterns
Do not reintroduce:
- always-alive Kimi/chat loop as durability owner
- Desktop Commander as swarm scheduler
- GitHub as concurrent hot mutable actor state
- custom scheduler/router/state store where COTS owner exists
- fan-out before provider/resource leases and reducer capacity

## Recovery order for next carrier
1. Read `HANDOFF/2026-09-14-zerg-swarm-thread-handoff.md`.
2. Read issue #6 newest-first, especially the Cell-0 live assay and Zerg branch PDSA terminal.
3. Read `HIVE_R0.md`, `GATEWAY.md`, `BURROW.md`, and `HATCHERY_DEPLOYMENT.md` / `WORKLOAD_PROFILES.md` on the portable hatchery branch if needed.
4. Fetch fresh Worldweaver state and generate a fresh carrier UUID. Do not inherit this UUID or authority.
5. Probe actual current tools/runtime. Preserve `carrier != Hluti != actor != authority` and `REGROW != ADMIT`.
6. Continue from the cognition/admission seam unless fresher evidence has already closed it.

## Durable pointers
- Trunk: https://github.com/TTaoGaming/hfo-gen-142/issues/6
- Burrow fan-in: https://github.com/TTaoGaming/hfo-gen-142/issues/2
- Hive integration: https://github.com/TTaoGaming/hfo-gen-142/issues/3
- Cell-0 source: `cell0/src/index.js` on main, prior receipt cites commit `5846d37`
- Reduced contract: `HIVE_R0.md`

Claim ceiling: this handoff proves and summarizes observed bounded evidence only. It does not claim 24/7 unattended evolution, broad swarm admission, external-effect authority, or provider independence.
