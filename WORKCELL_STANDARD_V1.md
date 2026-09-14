# Gen142 WorkCell Standard v1

Purpose: make one autonomous work cell boring, cloneable, versioned, and independent of Tao as runtime.

## Runtime law

`WORKITEM_DATA -> NATIVE_WAKE -> DETERMINISTIC_SELECT -> ALLOWLISTED_WORKER -> VERIFY -> GITHUB_CONSUMER_ACK -> TERMINAL_GATE -> AUTO_DISPATCH|RETIRE`

The runtime is **stateless glue**. It owns no durable queue, scheduler, lease, actor state, credentials, authority, model policy, or institutional memory.

- GitHub WorkItems are durable declared demand.
- GitHub issue comments are durable ConsumerAck/retirement evidence.
- GitHub Actions is wake/transport only.
- `tools/workcell_runtime_v1.py` executes at most one WorkItem per wake.
- `tools/select_research_workitem.py` deterministically selects highest-priority admitted unretired demand.
- Worker adapters are explicitly allowlisted by schema; WorkItems cannot inject arbitrary commands.
- `tools/terminal_handoff_gate.py` must admit terminal state before a completed WorkItem is considered closed.
- If more demand remains, the runtime dispatches exactly one next wake and exits.
- If no demand remains, the runtime exits `NOOP`; it never invents work.

## Human boundary

Tao may set intent, add/approve WorkItems, budgets, secrets, permissions, protected merges, payments, or irreversible external submissions.

Tao must not be required to poll, choose the next WorkItem, launch the next carrier, retry, gather results, reconcile duplicate terminals, or remember to restart the cell.

`HUMAN_AUTHORITY_UNLOCK != RUNTIME_CONTINUATION`.

## Clone rule

Do **not** copy the workflow.

To add work to the R1 research cell, add another admitted `hfo.research-workitem.v1` JSON file under `WORKCELLS/research-r0/`. The shared runtime selects it, executes the allowlisted worker adapter, records its GitHub ConsumerAck, and continues automatically.

A new worker phenotype requires:
1. a versioned WorkItem schema;
2. one allowlisted adapter in `WORKERS`;
3. deterministic/frozen verification semantics;
4. tests proving unknown schemas fail closed;
5. no widened authority or second durable state owner.

## Versioning

Runtime contract: `hfo.workcell-runtime-receipt.v1`.
Selection contract: `hfo.workcell-selection.v1`.
Retirement marker: `hfo-workcell-v1:<work_id>:<spec_sha256>`.
Legacy `hfo-research-cell-r0` retirement markers remain readable so migration never replays completed work.

Promotion rule:
`TRACE -> REGRESSION -> CANARY -> TWO-WORKITEM_CHAIN -> EMPTY-QUEUE_NOOP -> PROMOTE`.

A runtime revision is not admitted merely because its code is cleaner. It must reproduce the A->B->retire behavior with `tao_hot_loop_actions=0`.
