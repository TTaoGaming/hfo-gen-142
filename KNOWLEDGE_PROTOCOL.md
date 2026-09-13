# Gen142 Compounding Knowledge Protocol v0

## Purpose
Make swarm knowledge compound across carrier death without making Tao repeat context. GitHub is the durable germline; Cloudflare is hot working memory. Neither agent prose nor model consensus is truth.

## Unit of compounding
`EVIDENCE -> CLAIM -> FALSIFICATION -> ACCEPTED KNOWLEDGE -> CAPSULE -> CONSUMER_ACK -> REPRODUCTION_WEIGHT`

An item compounds only when it is reused by a distinct consumer and the outcome is recorded. Storage without reuse is archive, not learning.

## Knowledge event
Every worker may propose events; no worker may self-promote a material claim.
Required fields: `event_id`, `carrier_uuid`, `kind`, `domain`, `statement`, `observed_utc`, `source_refs`, `content_hash`, `parent_ids`, `fresh_until`, `visibility`, `claim_ceiling`, `strongest_falsifier`.
Kinds: `OBSERVATION | CLAIM | SCAR | RULE | SKILL | DECISION | CONFLICT | CONSUMER_ACK | SUPERSEDE`.

## Promotion
`PROPOSED -> CORROBORATED -> ACCEPTED` only after an independent deterministic check or independent verifier where material. Conflicting evidence stays `CONFLICT`; voting does not resolve truth. Stale claims become `STALE_UNKNOWN`, not false.

## Capsules
Two canonical projections exist:
1. **Identity capsule**: slow-changing mission, ontology, invariants, recovery protocol, authority laws. Current source: `GENE_SEED.md`.
2. **Partial world-state capsule**: bounded domain snapshot containing current accepted claims, unknowns, conflicts, active edges, evidence refs, freshness, and next tests.

Capsules are materialized views, not raw history. They must point backward by hash/parent, state the delta from parent, and remain small enough for a fresh carrier to load quickly.

## GitHub role
GitHub stores sanitized, durable institutional memory: gene seed, capsule schema, rolling public partials, heritage pointers, scars, and commit history. Raw archives are referenced, not copied. Public Gen142 never receives credentials, private personal data, or secret values.

Canonical public files stay few: `GENE_SEED.md`, `WORLD_STATE/index.json`, `WORLD_STATE/partials/*.json`, `HERITAGE/MANIFEST.md`, this protocol, and schemas. Agents submit proposals to coordination issue #1; reducer-owned writes update canonical projections.

## Cloudflare role
Start with one `KnowledgeAgent` using Agents SDK / Durable Object SQLite as the hot serialized knowledge head. Store events, claim status, conflicts, capsule heads, consumer acknowledgements, dedupe keys, and leases. Use a durable Workflow for reduction/materialization. Do not create a second scheduler, queue, actor runtime, or state store.

Suggested tables: `events`, `claims`, `edges`, `conflicts`, `capsules`, `consumer_acks`, `work_leases`. Enforce unique content hashes/idempotency keys. Secret material remains in Cloudflare Secrets; only secret references may enter knowledge state.

## Reducer loop
`MONITOR new events -> ANALYZE dedupe/conflict/freshness -> PLAN discriminating tests -> EXECUTE bounded verifier work -> UPDATE claim status -> MATERIALIZE changed partial capsule -> PUBLISH sanitized GitHub projection -> MEASURE consumer outcome`.

Reducer rules: no recommendation before falsification; no UNKNOWN->TRUE; no self-verification; no unbounded growth; no rewrite of evidence; supersede by link instead of erasure; `REDISCOVERY_NO_DELTA` does not enter the canonical capsule.

## Boundedness
Default targets: identity capsule <= 8 KiB; each partial <= 32 KiB; at most 3 next edges per partial; at most 10 unresolved conflicts per partial. Overflow is reduced by value-of-information and current mission relevance, with evicted items remaining recoverable by source refs/commit history.

## Byzantine safety
Producer identity, verifier identity, evidence source, and effect authority are separate fields. Independent failure domains outrank agent count. Consensus is advisory. Deterministic evidence outranks model judgment. A contradiction creates a conflict object and a next discriminating test.

## Success assay
A fresh carrier with no chat memory can read issue #1 + `GENE_SEED.md` + one relevant partial and correctly state: mission, current known/unknown/conflict state, strongest blocker, evidence refs, and next bounded edge in under one minute without asking Tao for context.
