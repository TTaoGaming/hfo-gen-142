# Gen142 Hive A2A Agent Card Requirements

Status: design/admission requirements only. No Gen142 Agent Card is `LIVE` until an actual durable endpoint is served and independently assayed.

## Purpose

Use the current official A2A Agent Card format for truthful discovery of an actually served durable Hive/Sigrun actor. Do not invent an HFO identity schema and do not publish stale heritage as current runtime capability.

## Materialization rule

Before writing or serving a candidate card, the producing Roach must fresh-read the current official A2A specification and SDK/TCK surface. Pin the spec/release used in the evidence receipt.

Materialize card fields from two evidence classes:

1. **stable profile evidence** — public name/description and admitted Skill references that survive ablation;
2. **live runtime facts** — endpoint/interface, protocol/runtime version, security, supported modes/capabilities and actually served skills.

Historical or aspirational capability remains omitted/HOLD.

## Hard boundary

`AGENT_CARD_CLAIM != CAPABILITY_ADMISSION != EFFECT_AUTHORITY != EVALUATOR_TRUTH`

A card is discovery/self-description. It never grants protected-effect permission.

## Hive design

Prefer **one card per actual durable served endpoint**, not one card per Zerg archetype.

Most internal morphology is represented through workload/Skill selection:
- Larva: pre-morph capacity, no card.
- Twinling: formation/Skill, no card.
- Roach: Skill + Burrow continuity; card only if it is independently served as a durable agent.
- Reducer/Verifier/Queen: card only if realized as independently served durable actors/services.

A single durable Sigrun/Hive actor may advertise a small coherent set of current Agent Skills and late-morph internally by Workload.

## Required evidence matrix

For each nontrivial proposed card field preserve:

```yaml
field:
value_or_hold:
source_ref:
observed_utc:
currentness:
claim_ceiling:
strongest_falsifier:
runtime_readback_ref:
```

Fields that depend on runtime facts must remain `HOLD` until live readback exists.

## Candidate acceptance

A candidate card is promotion-ready only when:
1. it validates against the current pinned A2A contract/tooling where available;
2. required runtime facts come from the served endpoint/build, not heritage prose;
3. every advertised Skill maps to a real current Skill package/procedure;
4. current tool reachability/admission is separately tested;
5. no private endpoints, credentials, or sensitive control-plane information leak;
6. a fresh distinct client can discover the card and successfully invoke at least one advertised no-effect capability;
7. unsupported capability is rejected/HOLD rather than silently fabricated;
8. protected-effect authority remains separate.

## Expected artifact

The Hive integration wave should eventually produce:
- `a2a/agent-card.candidate.json` — only after current-spec recovery and field evidence;
- an evidence matrix for every nontrivial field;
- a conformance/hostile-fixture receipt;
- a `LIVE | HOLD` disposition.

Do not create a fake URL or security configuration merely to make candidate JSON structurally complete.