# Gen142 Hive A2A Agent Card Requirements

Status: design/admission requirements only. No Gen142 Agent Card is `LIVE` until an actual durable endpoint is served and independently assayed.

Baseline normative release: **A2A 1.0.0** as observed 2026-09-14. Re-read the current released specification/TCK before promotion to LIVE.

## Purpose

Use the official A2A Agent Card format for truthful discovery of an actually served durable Hive/Sigrun actor. Do not invent an HFO identity schema and do not publish stale heritage as current runtime capability.

A disposable cloud thread/carrier is not represented by an Agent Card. Per-episode execution capability belongs in `schemas/carrier-capability-envelope-v1.schema.json`.

## Materialization rule

Before writing or serving a card, the producing Roach must fresh-read the current official A2A specification and SDK/TCK surface. Pin the release used in the evidence receipt.

Start from `a2a/agent-card-evidence.template.yaml`. Materialize JSON only when required fields have current evidence.

Materialize card fields from two evidence classes:

1. **stable profile evidence** — public name/description and admitted Skill references that survive ablation;
2. **live runtime facts** — endpoint/interface, protocol/runtime version, security, supported modes/capabilities and actually served skills.

Historical or aspirational capability remains omitted/HOLD.

## Hard boundary

`AGENT_CARD_CLAIM != CARRIER_CAPABILITY != CAPABILITY_ADMISSION != EFFECT_AUTHORITY != EVALUATOR_TRUTH`

A card is discovery/self-description. It never grants protected-effect permission.

## A2A 1.0 field contract

Required core card facts for Gen142 promotion:
- `name`
- `description`
- `supportedInterfaces`
- `version`
- `capabilities`
- `defaultInputModes`
- `defaultOutputModes`
- `skills`

Each served interface must truthfully provide `url`, `protocolBinding`, and `protocolVersion`. `version` is the agent/service version; `protocolVersion` is the A2A protocol version for that interface.

When authentication is actually required, current fields are `securitySchemes` plus `securityRequirements`. Do not copy pre-1.0 field shapes into a Gen142 card.

Every advertised A2A skill must have current evidence for at least `id`, `name`, `description`, and `tags`. An A2A advertised skill is discovery metadata; an Agent Skills `SKILL.md` package is procedural cognition. They may align semantically but are not the same artifact.

## Hive design

Prefer **one card per actual durable served endpoint**, not one card per Zerg archetype.

Most internal morphology is represented through workload/Skill selection:
- Larva: pre-morph capacity, no card.
- Twinling: formation/Skill, no card.
- Roach: Skill + Burrow continuity; card only if it is independently served as a durable agent.
- Reducer/Verifier/Queen: card only if realized as independently served durable actors/services.

A single durable Sigrun/Hive actor may advertise a small coherent set of current capabilities and late-morph internally by Workload.

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

Fields that depend on runtime facts remain `HOLD` until live readback exists.

## Promotion ladder

A card may become `LIVE` only when:
1. an actual served endpoint is independently read back;
2. the well-known card is served at `/.well-known/agent-card.json`;
3. required runtime facts come from the served endpoint/build, not heritage prose;
4. upstream A2A validation/TCK checks relevant to declared interfaces/capabilities pass;
5. every advertised skill maps to a real current served capability/procedure;
6. a fresh distinct client successfully invokes at least one advertised no-effect skill;
7. hostile unsupported-capability requests fail closed;
8. a distinct ConsumerAck exists;
9. protected-effect authority remains separately enforced.

Do not create fake URL, security, protocol or capability values merely to make JSON structurally complete.
