# Gen142 A2A / Skills / Tools Profile

Purpose: make JIT morphing portable without creating another HFO agent protocol.

## Four distinct contracts

- **A2A Agent Card (A2A 1.0)**: discovery/self-description for an actually served durable agent endpoint. Do not use it as a per-chat capability manifest.
- **Agent Skills**: progressive-disclosure procedural cognition loaded only when relevant to an admitted Workload.
- **Carrier Capability Envelope**: fresh per-episode observation of what this disposable thread/carrier can actually reach, load, target and perform now. Schema: `schemas/carrier-capability-envelope-v1.schema.json`.
- **MCP / provider-native API / CLI**: tool and resource interfaces. No duplicate HFO tool bus.

GitHub owns institutional evidence/admission; Cloudflare Agent/DO owns admitted durable hot actor state; thread/model/carrier is disposable cognition supply.

## Hard boundaries

`AGENT_CARD_CLAIM != CARRIER_CAPABILITY != CAPABILITY_ADMISSION != EFFECT_AUTHORITY != EVALUATOR_TRUTH`

`SKILL_DISCOVERED != SKILL_LOADED != TOOL_REACHABLE != TOOL_ADMITTED != EFFECT_AUTHORIZED`

A card says what a served endpoint advertises. A Carrier Envelope says what one execution episode can prove now. Neither grants protected-effect permission.

## A2A 1.0 materialization rule

Until a live Gen142 durable A2A endpoint is admitted, keep Agent Card disposition `HOLD`; do not fabricate URL, protocol binding/version, service version, security, media modes, capabilities or served skills.

When an endpoint exists, serve the card at `/.well-known/agent-card.json` and materialize from live facts. Core current fields include:
- `name`, `description`, `supportedInterfaces`, `version`, `capabilities`, `defaultInputModes`, `defaultOutputModes`, `skills`;
- each `supportedInterfaces` entry carries `url`, `protocolBinding`, `protocolVersion`;
- current auth uses `securitySchemes` + `securityRequirements` when applicable.

Validate with the upstream A2A contract/TCK. One card per actually served durable endpoint, never one card per Zerg metaphor.

## Agent Skills R0

Current Skill ceiling:
- `twinling-pdsa` — disputed evidence edge needing gather/falsify.
- `roach-fanin` — durable continuation/recovery/reduction of existing evidence/work.
- `hive-integration` — cross-contract Hive integration/reduction only.

Every Skill must follow the upstream Agent Skills format: `SKILL.md` YAML frontmatter with `name` and `description`, directory/name match, progressively loaded body/resources. Descriptions are activation boundaries and must be mutually discriminating.

Do not use experimental `allowed-tools` as an HFO authority system. Skill discovery/loading never grants tool admission or effect authority.

## JIT morph / admission target

`UNCOMMITTED_CARRIER -> RECOVER -> EMIT_CARRIER_ENVELOPE -> WORKLOAD_SELECT -> SKILL_MATCH -> CAPABILITY_MATCH -> TARGET_BIND -> AUTHORITY_CHECK -> ADMIT|HOLD|DENY -> ROLE_MORPH -> EXECUTE -> RESULT -> CONSUMER_ACK -> RELEASE`

Do not bind morphology to provider/model brand. Do not morph first and assume capabilities appear later.

## Acceptance

A fresh carrier given only the Gen142 pickup pointer should recover state, emit a valid Carrier Capability Envelope, load only the matching Skill, use native tools against a deterministic target, terminal with durable evidence, and require zero Tao context ferry after admission.
