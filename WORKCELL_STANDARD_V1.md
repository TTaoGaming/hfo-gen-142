# Gen142 WorkCell Standard v1

Purpose: make one autonomous work cell boring, cloneable, versioned, and independent of Tao as runtime.

## Runtime law

`WORKITEM_DATA -> NATIVE_WAKE -> DETERMINISTIC_SELECT -> ALLOWLISTED_WORKER -> VERIFY -> GITHUB_CONSUMER_ACK -> TERMINAL_GATE -> RETIRE -> SCHEDULED_RECONCILE|MISSION_COMPLETE`

The runtime is **stateless glue**. It owns no durable queue, scheduler, lease, actor state, credentials, authority, model policy, or institutional memory.

- GitHub WorkItems are durable declared demand.
- GitHub issue comments are durable ConsumerAck and retirement evidence, as separate facts.
- GitHub Actions is wake/transport only.
- `.github/workflows/workcell-runtime-v1.yml` is the shared heartbeat; normal continuation uses its versioned schedule rather than recursive self-dispatch.
- `tools/workcell_runtime_v1.py` executes at most one WorkItem per wake.
- `tools/select_research_workitem.py` deterministically selects highest-priority admitted unretired demand.
- Worker adapters are explicitly allowlisted by schema; WorkItems cannot inject arbitrary commands.
- `tools/terminal_handoff_gate.py` must admit terminal state before a completed WorkItem is considered retired.
- If more demand remains, the runtime API-observes the shared workflow as active and emits an armed `RECONCILE` receipt. The scheduled heartbeat owns the next wake.
- If no demand remains, the runtime closes `MISSION_COMPLETE`; later wakes return `NOOP` and never invent work.

## Failure ordering

ConsumerAck is not retirement.

A WorkItem retirement marker MUST NOT be published until:
1. worker result exists;
2. ConsumerAck is durable;
3. continuation is either API-observed/armed or mission-complete;
4. `terminal_handoff_gate.py` returns `ADMIT_TERMINAL`.

If ConsumerAck already exists but retirement did not complete, the next wake reuses that ConsumerAck rather than duplicating it. A failed watch, terminal gate, or retirement write must leave the WorkItem eligible for retry.


### Worker failure / poison-pill law

Worker failure is a first-class durable outcome, never an implicit busy-loop and never a success retirement.

- Each failed attempt emits `hfo.workcell-failure-receipt.v1` with a deterministic failure fingerprint and attempt count.
- Retry budget is versioned in the WorkItem as optional `max_attempts` (default `3`, hard range `1..20`).
- Below the ceiling, the scheduled heartbeat owns retry; Tao does not relaunch it.
- At the ceiling, the exact `work_id + spec_sha256` is marked `hfo-workcell-quarantine-v1` and remains **unretired**.
- The deterministic selector skips quarantined exact specs so lower-priority admitted demand can continue.
- Editing a WorkItem changes `spec_sha256`; old quarantine evidence therefore cannot silently suppress a repaired spec.
- Quarantine is not success, not ConsumerAck, and not deletion. It is STRIFE/poka-yoke evidence requiring a later repaired spec or explicit policy decision.

`REPEATED_FAILURE != RETIREMENT` and `ONE_POISON_WORKITEM != GLOBAL_STARVATION`.

## Human boundary

Tao may set intent, add/approve WorkItems, budgets, secrets, permissions, protected merges, payments, or irreversible external submissions.

Tao must not be required to poll, choose the next WorkItem, launch the next carrier, retry, gather results, reconcile duplicate terminals, or remember to restart the cell.

`HUMAN_AUTHORITY_UNLOCK != RUNTIME_CONTINUATION`.

## Clone rule

Do **not** copy the workflow.

To add work to the R1 research cell, add another admitted `hfo.research-workitem.v1` JSON file under `WORKCELLS/research-r0/`. The shared runtime selects it, executes the allowlisted worker adapter, records its GitHub ConsumerAck, gates terminal state, retires it, and the shared heartbeat continues automatically.

A new worker phenotype requires:
1. a versioned WorkItem schema;
2. one allowlisted adapter in `WORKERS`;
3. deterministic/frozen verification semantics;
4. tests proving unknown schemas fail closed;
5. no widened authority or second durable state owner.

## Versioning

Runtime contract: `hfo.workcell-runtime-receipt.v1`.
Selection contract: `hfo.workcell-selection.v1`.
ConsumerAck marker: `hfo-workcell-ack-v1:<work_id>:<spec_sha256>`.
Retirement marker: `hfo-workcell-v1:<work_id>:<spec_sha256>`.
Legacy `hfo-research-cell-r0` retirement markers remain readable so migration never replays completed work.

Promotion rule:
`TRACE -> HELD_OUT_BEHAVIOR -> REGRESSION -> CANARY -> MULTI-WAKE_CHAIN -> EMPTY-QUEUE_NOOP -> PROMOTE`.

A runtime revision is not admitted merely because its code is cleaner. It must pass held-out failure behavior and preserve `tao_hot_loop_actions=0`.
