# GEN142 HQ — operator CPR ledger

Updated: 2026-09-15T15:23:10Z

Purpose: make Tao's remaining runtime touches explicit and delete them one by one. This is a public projection/recovery artifact, not semantic runtime authority. Sigrun Durable Object remains semantic owner; public GitHub is Byzantine unless evidence is admitted by policy.

## Target

`TAO_HOT_LOOP_ACTIONS = 0`

HQ/voice should declare intent. The machine loop should perform `OBSERVE → RECONCILE → HATCH/DISPATCH → BOUNDED WORK → VERIFY → CONSUMER_ACK → RETIRE/REMORPH → REPEAT`, surfacing only typed exceptions and real human-authority boundaries.

## Current ownership

| Operator touch | Class | Current owner | Status |
|---|---|---|---|
| periodic wake / heartbeat | mechanical | GitHub Actions + Oracle runner | MACHINE_OWNED on `cdev-control#5` branch; merge governance still applies |
| Sigrun observation | mechanical | authenticated Sigrun `/status` + `/work` | MACHINE_OWNED |
| GitHub #13 fan-in/cursor | mechanical | deterministic reconciler | MACHINE_OWNED |
| next-action selection | mechanical | `tools/reconcile_kernel.py` | MACHINE_OWNED |
| terminal consume | mechanical | deterministic reconciler | MACHINE_OWNED |
| cleanup/janitor | mechanical | gated janitor executor | MACHINE_OWNED |
| hatchery fan-in/backpressure | mechanical | native scout hatchery/reducer | MACHINE_OWNED |
| Sigrun `KIMI_TEXT` worker dispatch | mechanical + neural | bounded no-tool Kimi actuator | CODED / FAIL-CLOSED; runtime route awaits admitted Kimi config for the runner principal |
| next mission/demand submission | authority/admission | unbound | HOLD: no trusted HQ demand source may be inferred from arbitrary public GitHub prose |
| provider login / secret / OAuth / 2FA | human authority | Tao | HUMAN_BOUNDARY only; never convert into recurring CPR |
| payment / permission / protected merge / irreversible external submit | human authority | Tao | HUMAN_BOUNDARY only |

## 2026-09-15 forcing result

Existing scheduled reconciler previously hard-coded empty `demand`, `dispatches`, and `worker_routes`, while the pure kernel already knew how to produce `SUBMIT_NEXT` and `DISPATCH_WORKER`. That mismatch was a hidden Tao-CPR seam.

`TTaoGaming/cdev-control#5` now contains a bounded no-tool Kimi worker adapter and CPR-aware autocell wrapper. It validates the exact Sigrun worker schema/profile, refuses tools/repository writes/paid effects, requires a real executable before advertising the route, hash-binds output, and posts only to Sigrun `/work/complete`.

Current branch head: `2169c92164412630b4d34352ebe7a49f509b7664`.

Oracle Actions run `34988065260`, job `104445210791`: **SUCCESS**. All 20 GEN142 adapter tests passed. Scheduled deterministic reconcile completed with `TAO_HOT_LOOP_ACTIONS=0`, `NO_ADMITTED_DEMAND`, `NO_EFFECT`, and `worker_routes=0`. Receipt SHA256: `58a177dfc4dc415591b31a0b8ed91c2a88c2502d4a11155fc022e338b21162be`. Artifact SHA256: `3f53b22ec5e7a147422980be7d31bbd328eee8d001267d75e1178735670c4bd2`.

The runtime route intentionally remains absent until the **GitHub runner OS principal** has an independently admitted Kimi model/config. Kimi being installed or logged in under another VPS principal is not sufficient authority and must not be credential-smuggled.

The next-demand actuator intentionally remains fail-closed as `UNBOUND_AUTHORITY_SOURCE` until HQ intent has an admitted, authenticated, version-bound demand record. Public issue comments alone must never become executable demand.

One cheap local Red-Queen ling assay on Oracle (`qwen3.5:2b`, no tools/effects) produced no output before a 90-second cap and exited `124`; no evidence was accepted from it and the same weak path was not duplicated.

## Delete-Tao rule

If a Tao touch is repeatable and does not cross a genuine human-authority boundary, classify it as a defect in lifecycle/reconciliation and assign it a machine owner. Never solve missing machine ownership by asking Tao to poll, re-launch, gather, or ferry context.