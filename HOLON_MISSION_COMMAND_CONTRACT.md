# Holon Mission Command Contract v1

Purpose: turn HFO from manually revived chats into durable virtual actors that compound verified skills across changing carriers. Target architecture is ~95% mechanical kernel + <=5% domain adapter.

## Ontology
- **Actor / holon**: persistent headquarters with immutable `actor_id`, mission history, promoted skills, heritage, reputation, open liabilities, and child-actor relations. The actor survives model/runtime/host replacement.
- **Carrier**: replaceable execution substrate: model, provider, harness, process, host, or chat. A carrier never owns canonical identity, heritage, reputation, leases, or promotion authority.
- **Mission**: commander's intent plus fitness, verifier, budgets, deadline, effect ceiling, authority boundary, and stop conditions. Mission command specifies WHAT/WHY/limits; the holon chooses HOW inside those limits.
- **Pyramid**: temporary delegation topology with bounded scope/TTL. It is not persistent identity or authority.
- **Herald / Raven**: machine courier that returns immutable receipts to durable state. Tao is never the context courier/message bus.
- **Skill gene**: versioned donor-derived capability with source/provenance and explicit lifecycle `REFERENCE -> CANDIDATE -> ASSAYED -> PROMOTED|REJECTED`.

## Canonical ownership
- GitHub `TTaoGaming/hfo-gen-142#13` is recovery/rendezvous SSOT.
- Existing Sigrun Cloudflare Durable Object owns semantic claim/fence/deadline/terminal state.
- GitHub Actions/VPS/Cloudflare execution surfaces are wake/transport/carriers only.
- Providers/models are leaf donors only; they are never control planes.
- Frozen external verifier/environment owns fitness truth. Neural self-report is never proof.
- Do not add a second queue, lease, scheduler, registry, actor runtime, memory authority, or verifier while an admitted owner exists.

## Mission-command invariants
Every executable mission MUST declare: `mission_id`, `actor_id`, `parent_actor_id` (nullable only for the root), `domain`, `intent`, `fitness`, `verifier`, `deadline_utc`, `max_attempts`, `max_spend_usd`, `effect_ceiling`, `receipt_sink`, `semantic_owner`, `provider_policy`, and `human_boundaries`.

Hard rules:
1. `actor_id != carrier_id`. Carrier death/replacement must not create a new actor.
2. Every loop is bounded in time, attempts, spend, disk/effects. No liveness-as-fitness and no infinite retry.
3. `semantic_owner` must remain the admitted Sigrun DO unless an explicit retirement/migration assay proves a replacement end-to-end.
4. `provider_role=leaf`. Crown/frontier work marked `FRONTIER_REQUIRED` fails closed when no admitted frontier route is live; no silent Ollama/small-model fallback.
5. Rehydrate/probe/repair before build. A new primitive requires evidence that the current admitted donor/owner cannot satisfy the frozen contract.
6. Tao relay defaults FALSE. Human intervention is admissible only for declared secret/OAuth/2FA/payment/permission/protected-merge/irreversible external-submit boundaries. The human action may only unlock that authority boundary; before escalation, the system must record the failed machine attempt and arm an automatic resume watcher. Tao must never be required to launch, retry, route, gather, monitor, check back, or restart continuation work.
7. A worker cannot promote its own output. Promotion requires an independent verifier receipt and ConsumerAck.
8. Memory/heritage is reference until promoted. `LIBRARY != RUNTIME`; `PROSE != CONTROL`.
9. Domain is **agnostic by default**. Agents are leverage, not the business domain. AI-reliability/AI-engineering work receives no default priority unless the mission explicitly selects it.
10. Buyer-facing crown missions must also pass `CROWN_FITNESS_CONTRACT.md`; low-prestige proxy trophies are rejected.
11. A carrier cannot self-attest its own transition to the next carrier. Terminal-to-next evidence must be controller/API-observed, provenance-bound, and accepted by `tools/terminal_handoff_gate.py`.

## Evolution / learning loop
`INTENT -> DONOR_RECOVERY -> FINGERPRINT -> MUTATE -> CHEAP_CANARY -> SUCCESSIVE_HALVING -> FROZEN_VERIFIER -> RESULT -> CONSUMER_ACK -> PROMOTE|REJECT -> HERITAGE -> TRANSFER_ASSAY`

Promotion is the learning event. A chat summary, remembered trick, or successful one-off run is not inherited skill until a named actor receives a promoted, versioned gene backed by evidence.

Public incumbent/champion papers, prompts, harnesses, tool policies, repos, and methods are valid donor genes when the target's rules permit them. Do not copy prohibited/private solution code. Preserve lineage and test mutations on the frozen official protocol.

## Reputation / attribution
Reputation is an evidence-backed skill graph, not a raw crown counter. Each reputation event references:
- actor and contributing child actors;
- promoted skill genes and lineage;
- external verifier/result receipt;
- prestige/buyer-legibility of the event;
- reliability, cost, operator-minutes, and transfer success.

A crown may contribute reputation only when public accepted-protocol evidence exists. Contribution credit must be explicit; team wins do not imply equal skill.

## Commercial default fitness
Primary system fitness: `externally_verified_useful_progress / Tao_operator_minute`.

For income missions also track: `P(qualified_paid_conversation <= 7d)`, `expected_cash_30d`, `expected_cash_90d`, evidence prestige, buyer legibility, and repeatability. The swarm may search any lawful domain. Do not route back to AI work merely because the machinery is AI.

## Actor-survival acceptance test
A durable holon is not admitted until this succeeds with Tao hot-loop actions = 0:
1. Actor receives mission A and durably claims it through the admitted semantic owner.
2. Kill/replace the current carrier after claim.
3. Actor reaches an honest bounded terminal or recovers, preserving identity/lineage and producing verifier + ConsumerAck evidence.
4. A controller/API-observed transition automatically dispatches mission B; a prose `next_consumer`, arbitrary string receipt, or Tao relay does not count.
5. Actor automatically receives/claims mission B.
6. B closes under a different carrier if available.
7. Promoted learning from A is readable by the same `actor_id` during B; no Tao context ferry.

The carrier may die. The actor must remain attributable, reconstructible, and governable.

## Forcing-function principle
A remembered failure remains `REFERENCE` until compiled into enforcement:
`FAILURE -> FINGERPRINT -> DEDUPE -> SMALLEST_FORCING_FUNCTION -> FAILING_REGRESSION/ADMISSION -> RECOVERY_ASSAY -> SPLENDOR_OR_REJECT`.

The executable forcing functions for this contract live in `tools/holon_gate.py`, `tools/terminal_handoff_gate.py`, and `ops/vps_exec_guard.py`. They are gates/wrappers, not a new control plane.
