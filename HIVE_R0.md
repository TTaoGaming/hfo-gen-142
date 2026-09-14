# Gen142 Hive R0 — Reduced Contract

State: CONTRACT_REDUCED__RUNTIME_HOLD
Observed: 2026-09-14T00:30Z
Parent evidence: issue #3 H0..H8 terminals; issue #1 heritage/evidence lake; issue #2 future Burrow assay surface.

## Hard ontology
`WORKLOAD != CAPACITY != CARRIER != ACTOR != PHENOTYPE != SKILL != TOOL != AUTHORITY != EVIDENCE`

Zerg vocabulary is a thin projection over this ontology, not a second runtime type system.

## Ingress / morph
`GATEWAY -> recover current frontier -> select existing demand -> capability/admission check -> late morph -> load only needed Skill -> per-call authority recheck -> PDSA -> terminal/readback -> producer release`

Capacity never creates demand. Morphology never enlarges authority. Producer release does not wait for downstream ConsumerAck.

## Twinling / Red Queen
Twinling is a gatherer/falsifier formation, not proof. Independent corroboration is earned only at terminal evidence boundaries with distinct carrier episodes and assessed failure-domain independence. Red Queen is adversarial falsifier pressure, not a separate durable actor/card/runtime. Minority falsifiers and UNKNOWN survive reduction.

## Roach / Burrow
Roach = logical continuation lineage. Burrow = durable responsibility/state slot. Carrier = disposable cognition. Exactly one mutable Burrow state owner at a time. Before Cloudflare assay PASS, active state owner remains `GITHUB_SHADOW_ONLY`.

Persist stable `work_id` / idempotency identity separately from carrier UUID. GitHub remains institutional evidence/recovery, not concurrent hot state after Cloudflare promotion.

## ConsumerAck
ConsumerAck proves downstream use or explicit rejection of an immutable knowledge item; it does not prove the underlying claim true. `consumer_refs` are pointers only. `CONSUMED` and `ADOPTED` are derived projection states and require resolvable evidence, reducer admission, currentness and preserved falsifiers.

## A2A
One Agent Card per actually served durable endpoint, never per Zerg metaphor. Current live card remains HOLD until a served endpoint provides truthful A2A 1.0 interface/version/security/capability facts, survives TCK-relevant checks, one no-effect skill invocation, hostile unsupported-capability checks and distinct ConsumerAck.

## Agent Skills
R0 ceiling is three procedures: `twinling-pdsa`, `roach-fanin`, `hive-integration`. No Skill-per-metaphor taxonomy. Skills are procedural cognition only; loading/discovery never grants tool admission or effect authority. `roach-fanin` and `hive-integration` require upstream-format frontmatter repair + reference validation before conformance is claimed.

## Tools / authority
Use MCP/provider-native/API/CLI directly; no HFO tool bus. Discovery/reachability/card/Skill/role/credential presence never implies permission. Every protected operation must remain within the current workload effect ceiling and the native resource owner's authorization at call time; unknown/revoked prerequisite fails closed.

## Cloudflare R0 owner map
Minimal hot path: `Agent/DO -> AgentWorkflow -> Service Binding/RPC reducer -> ConsumerAck`.

- Agent/DO: durable actor identity + persisted recovery-critical state.
- AgentWorkflow/Workflow: durable multi-step retry/resume/wait.
- Service Binding/RPC: internal invocation seam, not authority.
- Fiber: optional actor-local recoverable work.
- Queue: optional buffering/fan-out; at-least-once, so deterministic idempotency required.
- AI Gateway: optional model routing/observability/policy; not required for durability proof.

## G1 acceptance assay
Use one deterministic no-effect `work_id`.
1. Persist `{work_id,status,checkpoint,effect_ceiling,version}` in one Agent/DO.
2. Start one AgentWorkflow; durable step A persists checkpoint 1 then waits.
3. Kill caller/carrier A completely.
4. Fresh carrier B gets only Gateway pointer + `work_id`, resolves the same actor/work and resumes after checkpoint 1.
5. Step B derives deterministic `effect_hash` and invokes the reducer twice with the same `(work_id,effect_hash)`.
6. Reducer admits at most one accepted effect and persists one durable ConsumerAck/use receipt.

PASS only if same durable actor/work identity survives caller replacement, completed checkpoint is not redone, `accepted_effect_count == 1`, ConsumerAck is durable, and Tao/Lenovo are absent from the runtime path. Any failure keeps Cloudflare/Burrow/Hive LIVE on HOLD.

## After G1
G2 = admitted/default-path VPS execution proof with Lenovo unavailable. G3 = one two-generation COTS evolution cell with frozen evaluator + runtime/dependency fingerprint, bounded disk, durable lineage, zero duplicate accepted effects and zero Tao routing.

Proposed G2 portability profile: [Hatchery and Larva ABI R0](HATCHERY_LARVA_ABI.md).
Laptop and VPS implement one host-independent contract; Ollama is an optional
cognition adapter. This profile does not advance G1/G2/G3 runtime admission.
