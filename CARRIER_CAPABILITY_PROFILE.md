# Gen142 Carrier Capability Profile

Cloud-thread reliability needs three separate contracts:

1. **A2A Agent Card** — stable discovery facts for an actually served durable endpoint.
2. **Agent Skill** — reusable procedure loaded when a workload calls for it.
3. **Carrier Capability Envelope** — fresh per-episode facts about what this disposable carrier can reach, load, target and perform now.

`AGENT_CARD != SKILL != CARRIER_ENVELOPE != EFFECT_AUTHORITY`

## Admission sequence

`RECOVER -> OBSERVE_CARRIER -> VALIDATE_SKILLS -> MATCH_WORKLOAD -> CHECK_TARGET -> CHECK_CAPABILITY_ADMISSION -> CHECK_EFFECT_AUTHORITY -> ADMIT|HOLD|DENY -> EXECUTE`

Prompt equality does not imply execution equality. Cloud threads can differ in harness/model, connected tools, Skill activation, account/session state, network reachability, runtime target binding, provider limits, timeout, recovered state and effect ceiling.

Every material execution episode should emit a document conforming to `schemas/carrier-capability-envelope-v1.schema.json`.

`REACHABLE != ADMITTED != AUTHORIZED`

## Failure classes

Use the first failing boundary instead of `AGENT_FAILED`:

- `RECOVERY_STALE`
- `SKILL_NOT_DISCOVERED`
- `SKILL_INVALID`
- `SKILL_NOT_ACTIVATED`
- `CAPABILITY_UNREACHABLE`
- `TARGET_BINDING_AMBIGUOUS`
- `AUTH_CONTEXT_MISSING`
- `CAPABILITY_NOT_ADMITTED`
- `EFFECT_NOT_AUTHORIZED`
- `PROVIDER_HOLD`
- `TIMEOUT_OR_CARRIER_DEATH`
- `DURABLE_HANDOFF_MISSING`

## R0 Skill activation

- `twinling-pdsa` — disputed/uncertain evidence edge needing gather + falsify.
- `roach-fanin` — durable continuation/recovery/reduction of existing work.
- `hive-integration` — cross-contract Hive integration/reduction only.

A disposable cloud thread does not get an A2A Agent Card merely because it behaves agentically. Cards are only for served durable endpoints with live interface facts.

A fresh carrier passes portability only when it can recover current work, emit a valid envelope, select the right Skill, decide `ADMIT|HOLD|DENY` before execution, target deterministically, checkpoint a durable Result, and be replaced without Tao context ferry.
