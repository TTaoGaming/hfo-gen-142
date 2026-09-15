# Gen142 Hatch Pressure Poka-Yoke v1

Purpose: stop swarm fan-out from outrunning fan-in and turning provider throttles or verifier backlog into Tao CPR.

## Control law

`OBSERVE_FLOW -> HATCH_PRESSURE_GATE -> ADMIT_ONE_FORMATION | HOLD`

This is a forcing function, not a scheduler, queue, registry, actor store, or capacity planner.
It only decides whether one new semantic formation may be created.

## Failure classes blocked

- duplicate semantic work already active;
- duplicate semantic work relaunched inside the cooldown window;
- global active-WIP above the fixed R0 ceiling;
- unconsumed terminal backlog;
- pending verifier/ConsumerAck backlog;
- provider THROTTLED / BLOCKED / UNKNOWN;
- repeated unchanged failure fingerprint;
- burst launches inside the bounded time window;
- missing distinct verifier or downstream consumer;
- any formation that requires Tao to poll, retry, gather, or route it.

## R0 fixed ceilings

These ceilings are policy, not caller-provided knobs:

- active semantic claims: `< 3` before a new hatch;
- unconsumed terminals: `< 2`;
- pending verifier + ConsumerAck items: `< 3`;
- recent launches: `< 4` in 30 minutes;
- duplicate semantic cooldown: 60 minutes;
- one `SINGLE` = 1 carrier; one `TWINLING` = 2 carriers.

## Required input

Before any new manual or autonomous fan-out, construct a fresh `hfo.hatch-pressure-snapshot.v1` from trusted readback plus public receipts as observations.
The request must bind one normalized `semantic_key`, formation, provider route, distinct verifier, downstream consumer, and `tao_hot_loop_required=false`.

Run:

```bash
python tools/hatch_pressure_gate.py <snapshot.json>
```

Only `ADMIT_HATCH` may create the formation. Any inability to construct a fresh snapshot is itself `HOLD`, never permission to launch.

## Recovery law

A throttle is a backpressure signal, not a reason to spray the same semantic work across more providers.
A repeated failure may proceed only after the next request records `strategy_changed=true` and actually changes a falsifiable hypothesis, carrier class, donor, or method.

`NO_NEW_HATCH != NO_WORK`.
When the gate holds, existing reducers/verifiers/consumers should drain work, reconcile contradictions, clean residue, or improve deterministic forcing functions.

## Promotion / relaxation

Do not raise R0 WIP ceilings because compute is cheap. Raise them only after an unattended soak demonstrates that higher WIP lowers Tao operator-minutes without increasing duplicate effects, unconsumed terminal age, or verifier latency.

Primary metric:
`externally_verified_useful_progress / Tao_operator_minute`.

Provider utilization, agent count, token burn, issue count, and launch count are telemetry only.
