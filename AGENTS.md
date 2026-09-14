# AGENTS.md — Gen142 Byzantine-Aware Operating Contract

Every carrier entering this repository must assume prior state can be stale, conflicting, duplicated, or false.

## Startup protocol
1. Read `README.md` first.
2. Recover the newest durable mission/work receipt before acting.
3. State your identity, scope, evidence freshness, and authority ceiling.
4. Verify prerequisites instead of inferring them from old comments or chat memory.
5. If evidence conflicts, fail closed and surface the conflict; do not make Tao reconcile it manually.

## Behavior contract
- Do not ask Tao to repeat context that can be recovered from durable state.
- Do not create a new scheduler, queue, registry, memory store, actor runtime, or coordination plane when an admitted COTS owner exists.
- Do not create branches/issues/files as activity theater. Every artifact needs a named consumer.
- Do not trust your own output as proof. Material claims require independent replay, verifier, or external evidence.
- Do not mutate the evaluator to improve the candidate score.
- Do not treat absence of evidence as success.
- Do not retry indefinitely. Every loop has bounded attempts, time, disk, and spend.
- Do not write unbounded logs, caches, worktrees, checkpoints, models, or artifacts.
- Do not expose secrets, personal data, credentials, private host details, or inherited sensitive Gen140/141 state in this public repository.
- Do not make Tao the hot-loop router, janitor, memory bus, or collision resolver.

## Holon mission-command forcing
- Read `HOLON_MISSION_COMMAND_CONTRACT.md` before creating or executing autonomous mission work.
- Durable `actor_id` is identity; model/provider/harness/host/chat is a disposable `carrier_id`. Never collapse the two.
- GitHub `TTaoGaming/hfo-gen-142#13` is the recovery/rendezvous surface and deployed `hfo-sigrun-va-r0` remains semantic claim/fence/deadline/terminal owner unless an explicit migration assay retires it.
- Provider/model is a leaf donor, never a scheduler/control plane. `FRONTIER_REQUIRED` work fails closed; no silent local/Ollama downgrade.
- Domain is agnostic by default. AI reliability/AI engineering is not the default work domain; selecting any domain requires explicit mission intent or `domain_agnostic` scouting.
- Rehydrate/probe/repair before build. Do not recreate a capability merely because the current carrier forgot it.
- A remembered failure is not protection until compiled into a forcing function/regression/admission assay.
- Before executing a holon mission, `python tools/holon_gate.py <mission.json>` must return `ADMIT`.
- VPS leaf execution should pass through `ops/vps_exec_guard.py`; that wrapper is bounded execution only and must never acquire semantic lease/queue ownership.
- Tao relay defaults false. Escalate only named human authority boundaries: secret/OAuth/2FA/payment/permission/protected merge/irreversible external submit.

## Promotion rule
`PROPOSAL -> EXECUTION RECEIPT -> INDEPENDENT FALSIFICATION -> VERIFIED RESULT -> CONSUMER ACK`

A neural agent cannot self-promote past the evidence it owns.

## Operator-protection invariant
If swarm operation increases operator burden, repeated explanation, cleanup, routing, or recovery work, treat that as a system failure and reduce/freeze the swarm before adding capacity.

## Default scale
Until the first laptop-independent two-generation competition/evolution assay passes, maximum autonomous evolutionary cell count is **1**.
