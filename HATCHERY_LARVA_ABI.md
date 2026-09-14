# Portable Hatchery and Larva ABI R0

Status: **PROPOSED CONTRACT; NO RUNTIME ADMISSION**. Consumer: #3 Hive reducer,
then the G2 execution implementer and G3 evolution evaluator in `HIVE_R0.md`.
Base: Gen142 `673bf24e08744d1a06811bb927e6da12580d493b`.

Here ABI means a versioned application-level compatibility contract, not a
binary calling convention or a new network protocol. The schema validates
configuration shape; native runtime assays establish enforcement and fitness.

## One host-independent contract

A laptop, VPS, workstation and GPU server implement the same Hatchery contract.
They differ in measured capabilities and availability, not workflow semantics,
role privileges or separate orchestration designs. A workload names required
capabilities, never a laptop/VPS brand. No mandatory laptop coordinator exists.

`Hatchery -> uncommitted Larva -> admitted Workload -> late Morph -> Result -> Release`

ConsumerAck is a separate downstream event; producer release never waits for it.
Ollama is a cognition adapter. It is neither the Hatchery nor the durable actor.
An API-only Hatchery need not install Ollama or download model weights.

| Object | Identity and responsibility |
|---|---|
| Hatchery | stable installation ID; capacity, launch, isolation, health, drain and replacement |
| Boot | new ID after supervisor/host restart; invalidates old liveness claims |
| Larva | fresh carrier episode UUID; uncommitted until existing demand is admitted |
| Workload | durable work ID, immutable inputs/evaluator, resource/effect budget and consumer |
| Attempt | unique attempt ID plus current fence; never substitutes for the work identity |
| Adapter | versioned binding to Ollama, provider-native API or CLI harness |
| Burrow | existing durable state owner; process loss does not erase responsibility |

Moving work preserves work ID, checkpoint/artifact digests and evaluator. The
replacement gets new boot/carrier/attempt IDs and a newly issued fence. Resource
reservations, settled calls and ambiguous calls remain durable across moves.

## Native ownership

Reuse the Gen142 owner map: Agent/DO for admitted hot state, AgentWorkflow for
steps/waits, native supervisor for processes, native filesystem/container limits
for compute, and MCP/provider API/CLI for tools. GitHub stores institutional
evidence, not a hot lease. Before G1, retain `GITHUB_SHADOW_ONLY`; this document
does not promote an inherited deployment to a live Gen142 owner.

Linux may bind to systemd/cgroups and Windows to a supervised process plus Job
Objects or an admitted container runtime. The implementation must demonstrate
the same limits; an unavailable enforcement primitive makes that capability
ineligible. A thin binding may translate native fields, but must not add a
second scheduler, queue, model router, credential store or lease database.

## Hatchery descriptor

`contracts/hatchery.schema.json` is the executable shape. Each observation binds
an installation ID, boot ID, UTC observation/expiry, OS/architecture, enforceable
limits, available adapters and native owner references. The descriptor carries
no credentials or private addresses. Real bindings stay in private deployment
configuration; examples in this public repository are synthetic.

Required limits: active attempts, CPU allocation, memory, workspace bytes, log
bytes, lifetime, provider requests and USD. All are finite. USD zero means no
paid spend permission, not that a provider reports zero price. A shared account
budget remains shared across every Hatchery using it; buying another VPS cannot
multiply an account allowance. A local model still consumes CPU/GPU/time/disk.
CPU allocation is in millicores (1000 = one CPU); byte fields use bytes and
lifetime uses seconds. Schema numeric ranges are representation limits, never
spending authorization. Native admission applies the existing smaller caps.

Advertised capacity is not an allocation. Admission must recheck free capacity,
health freshness, runtime enforcement, model identity, quota and authority at
reservation time. Unknown is ineligible; registration must not grant work.
Optional hardware differences include GPU/VRAM and intermittent availability.
They cannot weaken the same result or recovery requirements.

## Larva invocation and result ABI

The research/proposal/verifier loadout and telemetry interpretation are documented
in [EVO_OPERATING_LOOP.md](EVO_OPERATING_LOOP.md). They populate the existing
pinned manifest and receipts; they do not introduce another Larva ABI.

Use these semantics as fields in the incumbent Workload/native invocation;
do not create another envelope bus. Each required reference must resolve to
immutable bytes or a current native authority record before execution.

| Required invocation data | Meaning |
|---|---|
| ABI major, work ID, attempt ID, carrier UUID | negotiate compatibility and stable versus disposable identities |
| native lease/fence reference | current sole-owner exclusion, checked before effects and result acceptance |
| manifest, input, evaluator and dependency digests | identical work semantics on any compatible host |
| checkpoint reference/digest | durable resume position; absent only for first attempt |
| capability requirements and adapter binding | select from measured supply; pin local model digest where available |
| authority reference and expiry | current tool, filesystem, egress and external-effect ceiling |
| reservation reference and deadline | finite shared-account and local-resource reservation |
| output byte ceiling and consumer reference | bounded artifact delivery and named downstream use |

Lifecycle: `UNCOMMITTED -> RESERVED -> RUNNING -> TERMINAL -> RELEASED`.
Reservation failure leaves Larva uncommitted. Cancellation/expiry is terminal
for that attempt, not evidence that an in-flight remote effect did not happen.
The host drains by refusing new reservations and checkpointing/terminating
existing attempts within their original limits. Reboot never renews budgets.

Terminal receipt: work/attempt/carrier/boot IDs, fence, pinned source/evaluator,
status, UTC timestamps, artifact references/digests/byte counts, resource usage,
provider request/response identity, tokens/cost with explicit UNKNOWN where
unavailable, checkpoint reference, and failure classification. Producer status
is not independent fitness or consumer acceptance. Empty/truncated output,
wrong identity and absent artifacts cannot become success.

Failure classes must distinguish `UNSUPPORTED`, `AUTH_REJECTED`,
`QUOTA_REJECTED`, `RESOURCE_EXHAUSTED`, `INVALID_OUTPUT`, `CANCELLED`,
`DEADLINE_EXCEEDED`, `EFFECT_UNKNOWN` and ordinary workload failure. Retry count
defaults to zero for provider effects. Only native evidence of non-execution or
provider-supported idempotency can justify a separately bounded retry.

## Ollama adapter

Use the [native API](https://docs.ollama.com/api), without an HFO model router.

- `GET /api/tags`: discover installed names/digests; installation is not a canary.
- `GET /api/ps`: observe loaded model/context/VRAM; loading is not fitness.
- `POST /api/generate` or `/api/chat`: use the admitted model and bounded context,
  generation tokens, deadline and response bytes. Prefer `stream:false` for the
  first conformance assay; stream completion must otherwise be explicit.
- Recheck the admitted model digest before dispatch and serialize tag mutation
  against inference through the native owner. A mutable tag without that
  protection cannot certify pinned-model execution.
- Preserve returned model, completion flag/reason, token counts and durations.
  Treat thinking-only, malformed, truncated or wrong-model output as failure.
- Disconnect/timeout is `EFFECT_UNKNOWN` if server completion is unobserved;
  do not assume HTTP cancellation stopped GPU/CPU work or replay it blindly.
- Pull/delete/create models is a separate authorized operation with a finite
  disk/network budget. Never auto-pull a missing model in a workload retry.

Provider APIs and Codex/Claude/OpenClaw CLI bindings obey the same reservation,
completion and artifact rules. Where a remote provider exposes only a model
alias, record that weaker identity honestly and require the workload to accept
it. n8n is an optional existing integration owner, not a mandatory second queue.

## Adding or replacing a machine

1. Provision an OS and install the same pinned supervisor/adapter release.
2. Enroll a unique installation identity using the existing private identity
   mechanism. Obtain narrowly scoped native credentials; no shared image secrets.
3. Measure capabilities and limits, publish a fresh private descriptor, and
   reserve no work until its required assays pass.
4. Run the same no-effect conformance workload, interruption/replacement test
   and artifact verification used for every other host.
5. Admit eligible capacity into the existing allocator. A laptop can go offline;
   another eligible host resumes from durable state without a new task or Tao.
6. Drain/revoke an old installation before replacement; stale fences fail closed.

Until G1/G2/G3 pass, extra registrations are standby capacity and the maximum
autonomous evolutionary cell count stays **one across the fleet**, not one per
machine. Capacity expansion does not change permissions or spending caps.

## Required conformance evidence

| Assay | Required falsifier/observation |
|---|---|
| Host substitution | same workload/evaluator on two compatible hosts; equivalent validity, not necessarily bit-identical stochastic outputs |
| Unsupported host/model | reject before provider/process dispatch |
| Stale observation or revoked authority | reject before new effect |
| Local resource limit | CPU/memory/disk/log/lifetime enforcement is measured, not just declared |
| Shared account | two hosts contend for one remaining request; at most one dispatch |
| Duplicate delivery | same work/terminal slot and payload returns existing receipt |
| Conflicting delivery | same work/terminal slot with different payload rejects conflict; payload hash alone is not a unique terminal slot |
| Carrier replacement | checkpoint survives caller loss; no completed step or ambiguous call is blindly repeated |
| Host failure | native lease expires, replacement fence wins, old holder cannot commit effects/results |
| Release and ACK | producer capacity releases; downstream independently accepts/rejects immutable result |
| Evolution acceptance | G3 two generations, frozen evaluator, bounded storage, zero duplicate accepted effects and zero operator routing |

JSON Schema checks only shape. Time, reference resolution, atomic reservation,
identity, enforcement and all assays above remain runtime obligations. Do not
label the contract or a schema-valid descriptor a live/verified Hatchery.

## Offline validation and review ceiling

Run `python contracts/check_contract.py` with Python and `jsonschema` installed.
Three synthetic platform descriptors pass; nine hostile shapes must reject.
This same-author fixture checks configuration shape only, not policy execution,
independent review, or host portability. In particular, a schema-valid ADMITTED
string is still an untrusted claim until its native authority resolves.

The strongest unresolved falsifiers are cross-host shared-account races,
stale-fence commits and ambiguous provider completion after host loss. G2/G3
implementers must demonstrate the corresponding native behavior before adoption.
The contract itself creates no autonomous cell. The bounded implementation and
current deployment evidence are documented in [Hatchery deployment](HATCHERY_DEPLOYMENT.md).
