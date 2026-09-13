# Gen142 Interoperability Standards Profile

Gen142 uses existing standards for transport, time, provenance, validation, and traceability. HFO-specific concepts such as STRIFE and SPLENDOR are payload semantics, not replacement protocols.

## Required baseline

- **CloudEvents 1.0.2 stable** for event envelopes. Required context: `specversion`, `id`, `source`, `type`; use `subject`, `time`, `datacontenttype`, and `dataschema` where useful.
- **RFC 3339 UTC** for event time. Emit uppercase `T` and `Z`, e.g. `2026-09-13T22:45:00Z`. Preserve original source time separately only when materially useful.
- **W3C PROV-O / PROV-DM** for provenance semantics: Entity, Activity, Agent, `wasGeneratedBy`, `wasDerivedFrom`, `wasAssociatedWith`, `used`, and invalidation/supersession relationships where applicable.
- **W3C Trace Context** (`traceparent`, optional `tracestate`) for cross-service/cross-agent correlation. Use the CloudEvents Distributed Tracing extension when carrying trace context in events.
- **JSON Schema 2020-12** for machine validation of Gen142 payloads.
- **JSON-LD 1.1** is optional for graph/linked-data export. Do not require JSON-LD in the hot path when plain validated JSON is sufficient.

## Event naming

Use reverse-DNS style CloudEvents types:
- `dev.worldweaver.strife.v1`
- `dev.worldweaver.splendor.v1`
- `dev.worldweaver.claim.v1`
- `dev.worldweaver.consumerack.v1`
- `dev.worldweaver.worldstate.v1`

`source` identifies the producing system/actor surface, not effect authority. `id` is globally unique and immutable.

## STRIFE and SPLENDOR

Every recovered heritage item is classified at the highest useful level as one of:

- **STRIFE** — observed failure, pain, contradiction, operator burden, unsafe behavior, false-green, regression, wasted spend/compute, unrecoverable state, or evidence of a harmful assumption.
- **SPLENDOR** — observed success, externally or independently verified useful outcome, robust recovery, proven guard, repeatable improvement, accepted artifact, or evidence that a mechanism works under stated conditions.

Neither class is automatically a gene. Both require evidence and ablation before slow-canon promotion.

## Evidence law

Every material event should bind:
- immutable `id` and content hash;
- UTC observation time and freshness/validity window when time-sensitive;
- source/evidence references;
- producer Agent and generating Activity provenance;
- claim ceiling / effect ceiling;
- strongest falsifier or unresolved conflict;
- parent/supersedes relations;
- ConsumerAck when downstream work actually used the knowledge.

`SELF_REPORT != PROOF`. `CONSENSUS != TRUTH`. Same-source repetitions do not increase independence.

## Privacy boundary

`hfo-gen-142` is public. Private repository names, secrets, credentials, personal records, and sensitive infrastructure details MUST NOT be copied into public events. Public reduction may use sanitized descriptions, content hashes, opaque source IDs, and counts. Full private source mapping must remain in an authorized private surface; absence of a public raw ref does not downgrade valid private evidence if the reducer can re-verify it through authorized access.

## Canonical projection

Cloudflare may hold hot/private state and working indexes. GitHub holds the small durable public germline/projection. Do not mirror every event into canonical files. Reducers materialize only accepted deltas into `GENE_SEED.md`, `WORLD_STATE/*`, `HERITAGE/MANIFEST.md`, and STRIFE/SPLENDOR indexes.
