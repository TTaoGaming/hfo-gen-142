# Evolution PDSA notes and blocker handoff

Consumer: Sigrun and the next carrier continuing PR4. Repeated operator messages
request sequential notes/blocker cycles, not duplicate provider campaigns or a
new scheduler. Read the last entry, inspect one unresolved edge, append a delta
or explicit no-change result. Do not rerun unchanged probes merely to fill a turn.

## Cycle N1 — 2026-09-14T03:30:56Z

**Plan:** distinguish what blocks a new campaign from what merely lacks evidence;
identify the smallest zero-provider next check. Scope: notes, source review and
GitHub readback. Provider requests, installations and runtime mutations: zero.

**Do:** read PR4 head `72fe9d5a69a60fe4d75fa96554e72702cb01b27e`, current
campaign/budget/recovery records, and the provider adapter. PR4 is OPEN/DRAFT;
GitHub reports no checks on the branch. This is absent CI evidence, not failed CI.
Runtime assays and quota figures below retain their original timestamps; neither
VPS nor live model availability was reprobed in this cycle.

**Study:** a new source-level concern was identified. `pdsa-budget.mjs` reserves
a row, awaits quota/catalog checks, sets `dispatched`, saves, then performs the
provider call. Its `save()` retains `stop_requested` but does not abort that
dispatch path. The existing stop test covers a response already in flight, not a
stop arriving during quota checking. Classify this as **suspected stop-before-
dispatch race, not reproduced**. Do not label it a live leak or a completed fix.

### Blockers in execution order

| ID | State and evidence | Owner / next action | Exit evidence |
|---|---|---|---|
| B1 | Suspected stop-before-dispatch race in current candidate source | Implementation carrier: hold a mock quota response, issue stop, release quota, count dispatches | Zero provider dispatch after stop in that window; retain existing in-flight completion test |
| B2 | Interrupted generation skipped; archived r2d caller exits 0 with only generation 0 | Implementation carrier: inspect native unfinished generation metadata and retained response; no fresh inference | Expected generation plus evaluator receipt after recovery; no repeated uncertain call |
| B3 | Arbitrary algorithm isolation unproved; Oracle Docker installation approval still absent in this task | Operator approval only for that exact installation; implementation carrier owns sandbox negative tests afterward | Explicit installation authorization if using Oracle Docker; network/credential/write/resource isolation assays |
| B4 | Longer campaign and vendor allocations are planning records; account-wide races/fences unproved | Implementation carrier: test two callers against one remaining mock allowance; bind a fresh mission in existing owner | One dispatch maximum, stale-holder rejection, finite reservation; never reset R1 |
| B5 | Verified cycle phase/ACK times and human-intervention counts unknown | Implementation carrier: instrument existing receipts on the two-generation path | Two consecutive verified dispositions with timing and zero operator routing; failures remain in denominator |

B3 is not a reason to stop B1/B2/B4's zero-provider work. Automatic approval
review previously rejected installing Docker on Oracle because it adds a
persistent privileged daemon and changes the VPS attack surface. That exact
installation remains pending explicit approval; this notes cycle does not retry
it or request approval again. Earlier general deployment approvals are not
recorded as resolving that specific rejection.

Other evidence gaps: no reported PR checks; free-vendor remaining quotas unknown;
OpenRouter's old completion remains uncertain; current champion keeper acceptance
and independent approval of the normalized descendant remain unproved. The
03:15 Kimi quota snapshot is historical and exceeds the five-minute admission
freshness window at this entry. It must not authorize a later request unchanged.

**Act / next queued cycle:** execute B1's local mock falsifier and record the
result before expanding scope. A failure justifies a narrow fix and replay; a
pass narrows the concern without proving full account safety. Then proceed to B2.
Do not infer that the next queued message authorizes additional provider spend.

**Strife:** stop-state persistence was almost treated as complete cancellation
coverage. Smallest guard: test stop before dispatch separately from stop after
dispatch. **Splendor:** existing immutable receipts expose incomplete recovery
without spending more quota; the earlier champion lineage remains preserved.
No new champion or increase in runtime stability is claimed this cycle.

## Cycle N2 — 2026-09-14T03:33:39Z

**Plan:** run B1's falsifier using only mocked quota and provider transport.
**Do:** extend the existing adapter fixture with a deferred quota response.
Start a request, wait until quota checking begins, acknowledge stop, release
the quota response, then count provider dispatches. No production code change,
runtime deployment, package installation or live model request occurred.

**Study:** **B1 is confirmed locally, not repaired.** The stop ACK was true with
zero calls at that instant. After releasing quota, one mock call occurred; the
stored state still read `STOPPED_BY_EVALUATOR`. The new guard assertion failed
with `1 !== 0`; the three older tests passed in the same execution. A final
stopped state does not establish that a post-stop call was prevented.
Evidence: `hatchery/shinka-cell/PDSA_N2.json`, bound to the candidate source hash.

Reproduce in PowerShell from this repository:

```powershell
$env:PDSA_STOP_RACE_ASSAY='1'
node hatchery/pdsa-budget.test.mjs
Remove-Item Env:PDSA_STOP_RACE_ASSAY
```

The opt-in falsifier intentionally exits 1 on current code. Default tests do not
exercise B1 and their passing result must not be presented as cancellation
acceptance. This is local fixture evidence; the deployed Worker was not probed
or modified, and no live quota leak is inferred.

**Act / next queued cycle:** narrow B1 repair before B2 recovery work. The
implementation carrier must serialize stop against the actual dispatch boundary,
including asynchronous persistence; merely preserving a stop flag or checking it
before another await is insufficient. Keep an already in-flight result recoverable
without reopening admission. Required replay: this falsifier reports zero mock
calls after stop; existing in-flight completion, replay and exhaustion tests pass.
No deployment follows without that evidence and current source/version readback.

Blocker delta: B1 `SUSPECTED -> REPRODUCED_LOCAL`; B2–B5 unchanged and not re-tested.
The next campaign remains unstarted. **Strife:** durable status can disagree with
effect history. **Splendor:** a deterministic mock isolated the failure without
using quota. This is diagnostic progress, not improved runtime stability.

## Cycle N3 — 2026-09-14T03:37:26Z

**Plan:** make the narrow B1 repair and preserve the incident as a mandatory
regression. **Do:** the existing stop/dispatch gate now checks durable stop state,
persists the reservation and starts transport before releasing the gate. It waits
for the provider response outside that gate, so cancellation remains available
while a call is in flight. Expected refusals are caught inside the callback and
handled afterward: an escaping callback exception can reset a Durable Object
according to [Cloudflare's state API](https://developers.cloudflare.com/durable-objects/api/state/).

**Study:** all **5 local tests pass**. The N2 quota-wait incident changed from one
mock dispatch after stop to zero. Repeated/new requests after that stop also
dispatch zero. A new persistence-window test establishes the other ordering:
if dispatch already owns the gate, transport starts before stop is acknowledged;
the response may complete later without reopening admission. The original
in-flight, replay, exhaustion and uncertain-completion checks still pass.
The B1 test is now always enabled; `PDSA_STOP_RACE_ASSAY` is no longer needed.
Source hashes and result are in `hatchery/shinka-cell/PDSA_N3.json`.

**Blocker delta:** B1 `REPRODUCED_LOCAL -> LOCAL_FIX_VERIFIED_HOSTED_HOLD`.
No live provider calls, hosted deployment or allowance changes occurred. The mock
serializer is not the Cloudflare runtime. Native event/input-gate behavior,
eviction, persistence failure and the 30-second concurrency-callback deadline
still need their own evidence before deployment. B2–B5 remain open; no scientific
generation recovery or autonomous stability is inferred from these five tests.

**Act / next queued cycle:** inspect B2's unfinished generation metadata read-only
and classify what can resume from retained evidence without inference. B1 still
requires a native no-provider replay and current-version guarded deployment. Do not blindly
replace the hosted source from this local module.

**Strife:** checking a stop flag before asynchronous work does not protect the
actual effect boundary. **Splendor:** the same deterministic falsifier that failed
in N2 now passes, and a persistence-window test checks that cancellation does not
wait for model completion. This is local repair evidence only.

## Cycle N4 — final queue wrap-up, 2026-09-14

**Plan:** inspect the preserved B2 recovery fixture read-only and close this
four-message notes queue with a mission-command handoff. **Do:** inspected the
Oracle r2d generation-1 directory to depth two, original before/after archive
snapshots, and the first two recovery-log lines. No candidate/evaluation files
were returned from that directory inspection. Both archive snapshots contain
only the same generation-zero ID. The log still reports an existing generation-1
directory and a missing generation when the generation budget ends.

**Study:** B2 remains OPEN. The preserved fixture has no completed generation-one
receipt to accept. Its separately cached test response is test equipment, not
evidence that the interrupted generation finished or that a live provider call
may be repeated. A zero exit and an existing directory cannot authorize success.
Next B2 work must distinguish pre-dispatch, uncertain dispatch, retained response,
evaluated result and accepted result, then continue only from proven native state.
Do not delete the unfinished directory to make the runner retry blindly.

**Act:** this operator-supplied four-cycle queue is now wrapped up. No recurring
automation, background campaign or queued model allowance was created. Across
N1–N4, live model requests and runtime deployments were zero. B1 has a local fix
and five passing tests; B2–B5 remain unresolved. Native verification and deployment
of B1 are still pending. No claim of improved hosted stability follows from this
notes queue. Consumer: Sigrun's next admitted stabilization mission.

### Mission command: target and acceptance boundary

Tao and Sigrun set the mission intent, scientific objective, available quota,
effect boundaries and promotion criteria. The hive should own bounded assignment,
execution, recovery, independent verification, durable evidence and escalation.
Sigrun supervises meaningful decisions; Tao must not become the per-step scheduler.
This role allocation is the desired operating model, not a claim of a deployed
supervisor or permission inherited by a persona.

Compose the existing contract in this order:

`compute -> Hatchery admission -> uncommitted Larva -> selected workload/loadout
-> durable Roach actor + bounded carrier -> verified result + retained lesson`

Cloudflare hosts durable identity/state and Workflow execution; the selected
Kimi/Gemini/other adapter supplies cognition. MAPE-K/PDSA is the observe, decide,
experiment, verify and learn behavior inside that lifecycle. Callsign, persona,
model and tools remain replaceable manifest fields; they cannot change the
evaluator, work identity or shared-account reservation. Stabilize primitives first,
then compose researcher/proposer/verifier force packages and compare loadouts.

**Factory acceptance remains:** one laptop-independent cell completes two
consecutive verified generations, survives an interruption without replaying
uncertain effects, respects account and resource bounds, and needs zero Tao
routing/cleanup/context ferrying after admission. Until that joined test passes,
the system is an experimental factory prototype, not an unattended swarm factory.

Ordered handoff: (1) native no-provider cancellation replay and guarded B1
deployment, (2) native B2 recovery classification/replay, (3) admitted algorithm
isolation and shared-account/fence tests, (4) the two-generation acceptance run
with phase/ACK and intervention telemetry, (5) repeat missions and loadout trials.
Existing champion candidates remain valuable and separate from this incomplete
automation. Neither a new champion nor keeper acceptance was established here.

**Strife:** an unfinished directory was mistaken by the runner for work already
being processed. **Splendor:** immutable snapshots and a short log expose the
missing generation without another model request. Remaining blocker is lifecycle
recovery, not evidence that more compute or more personas are needed.

## Goal R1 — implement cancellation and recovery, 2026-09-14

The bounded 30-minute stabilization mission produced native local workerd
cancellation evidence and a tested opt-in Shinka accepted-proposal checkpoint.
The isolated VPS assay completed two native generations after killing the caller
and evaluator descendants, without re-requesting the interrupted proposal. Both
results passed separate exact geometry checks and retained the incumbent.
Missing or changed checkpoints and a competing caller were rejected.

Details, exact source hashes, failed experiments and installation boundaries:
[recovery report](hatchery/shinka-cell/RECOVERY_GOAL_R1.md) and
[machine-readable receipt](hatchery/shinka-cell/GOAL_R1.json).

B1 is now native-local verified, not hosted deployed. B2 has an isolated tested
repair, not production installation or automatic supervisor recovery. Automatic
approval review rejected persistent installation; the isolated test left the
system package unchanged. Live model calls, cap changes and new champions were
zero. Two verified fixture generations are proven; two unattended live
generations still need the joined admitted acceptance test.
