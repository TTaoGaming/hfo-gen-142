# Gen142 Deterministic Reconciler Contract v0

Purpose: remove Tao and neural agents from the hot-loop orchestration path without creating another scheduler, queue, actor runtime, or state owner.

## Industry abstraction
The mechanism is a **controller/reconciler**: observe durable state, compare it with admitted demand/policy, emit the smallest legal next action, then yield. In Zerg terms, `QUEEN` is a codename for a **versioned reconciliation policy**, not a neural actor, personality, fallback brain, or authority owner.

`QUEEN_POLICY != SIGRUN_ACTOR != WORKER != SCHEDULER != QUEUE != AUTHORITY`.

## Why Tao became the orchestrator
The system already had clocks, durable local state machines, workers, gates, and terminal receipts, but no general owner for `OBSERVED_STATE -> NEXT_LEGAL_ACTION`. Local owners stop at their boundary: Sigrun advances one submitted WorkItem; workers execute one bounded job; GitHub records demand/evidence; Actions/cron wake processes. Missing cross-boundary transitions therefore bubbled upward until Tao absorbed them.

## Ownership
- GitHub #13: public transparency/recovery/evidence ledger only; issue/comment prose is never live authority.
- Protected `main`: versioned admitted intent/policy after repository governance; still not self-proof of runtime facts.
- Sigrun Cloudflare DO: semantic claim/fence/deadline/terminal state for admitted work.
- GitHub Actions / Cloudflare schedule/workflow: wake and transport only.
- VPS/provider workers: disposable execution capacity only.
- `tools/reconcile_kernel.py`: pure deterministic policy only; it owns **no durable state**.
- `tools/janitor_gate.py` + `ops/janitor_exec.py`: bounded cleanup admission/effect leaf; see `DETERMINISTIC_JANITOR_CONTRACT.md`.
- Tao: intent, budgets, policy, true authority unlocks, irreversible external effects. Never routine continuation.

## Reconciliation law
Each wake constructs one immutable `hfo.reconcile_snapshot.v0` from authenticated internal controller readbacks plus admitted protected-main intent and runs the versioned kernel. Public GitHub events must first pass `tools/public_boundary_gate.py`; `OBSERVE_ONLY` material cannot populate authoritative actor/demand/dispatch/route/human-boundary fields. The kernel emits exactly one bounded plan.

Priority order:
1. fail closed on malformed/contradictory state;
2. if a genuine human-only boundary is active, require an already-armed machine resume watcher and wait for the unlock;
3. if a dispatch is already active, wait rather than duplicate it;
4. let Sigrun finish phases it already owns;
5. when `WAITING_WORKER`, dispatch one admitted live worker route or let Sigrun's deadline/recovery owner handle absence;
6. consume terminal evidence before launching unrelated next work;
7. execute at most one already-admitted cleanup candidate before unrelated new demand;
8. when actor capacity is free, select the highest-priority admitted unblocked demand deterministically;
9. if no admitted cleanup or demand exists, idle. Spare capacity never invents work.

## Determinism / evolution
Same canonical snapshot + same policy version MUST produce the same plan and `plan_sha256`.

Policy evolution is offline and evidence-gated:
`TRACE_CORPUS -> MUTATE_POLICY -> REPLAY -> FAILURE_INJECTION -> CANARY -> SOAK -> PROMOTE_POLICY_VERSION`.

A candidate policy may change ranking, retry ceilings, role formations, successive-halving rules, or routing preferences, but cannot widen authority or create a new state owner. Promotion requires regression evidence and a bounded live assay. Every runtime receipt records `policy_version`, `snapshot_sha256`, and `plan_sha256`.

## Human-boundary law
A human may unlock authority; a human may not provide continuity. Before escalation, the machine must have a durable failed-attempt reference and an armed resume watcher. Tao must never be required to remember what to run next, poll status, restart the controller, gather child outputs, or route the next carrier.

## Acceptance test
PASS only when a scheduled wake can repeatedly execute:

`OBSERVE -> RECONCILE -> DISPATCH/WAIT -> VERIFY -> CONSUME -> RECONCILE`

across at least two mission transitions with:
- `tao_hot_loop_actions = 0`;
- no neural agent choosing control-flow transitions;
- duplicate accepted dispatch/effects = 0;
- controller restart/replacement preserves behavior because durable state lives elsewhere;
- every transition is API/controller-observed, not self-attested;
- an unknown public principal posting a schema-valid terminal/command produces zero authoritative state transition;
- policy version and replay hashes are durable.

The kernel is intentionally boring. LLMs may scout, propose, mutate, research, build, or verify payloads; they do not become the operating system.