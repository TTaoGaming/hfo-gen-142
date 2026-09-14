---
name: roach-fanin
description: Continue an existing Gen142 durable fan-in or recovery workload by consuming prior terminal evidence, reconciling stale canonical state, checkpointing compact durable state, and releasing. Use when work/evidence already exists and continuation or reduction is needed; do not use for new discovery.
---

# Roach Fan-In Skill

Use when a fresh carrier should continue durable reduction/fan-in rather than start a new discovery lane.

## Trigger
- issue #2 has an under-covered/stale burrow;
- #1 contains terminal evidence waiting for reduction;
- canonical Gen142 state is stale versus accepted evidence;
- a prior Roach carrier ended and durable continuation is needed.

## Contract
A fresh thread is disposable cognition. It does not become durable by staying alive. Recover the burrow state, continue one bounded PDSA cycle, checkpoint, and release.

### PLAN
- recover #2 and #1 newest-first;
- select/recover one burrow B0..B7;
- generate fresh `carrier_episode_uuid`;
- state exact fan-in question, expected delta, strongest falsifier, evidence needed, and effect ceiling;
- claim + immediate readback; earlier durable claim wins.

### DO
Prefer reducer work:
- consume unconsumed Twinling terminals;
- normalize Strife/Splendor to pinned schemas;
- deduplicate repeated genes/scars;
- update source catalog dispositions;
- reconcile currentness/UNKNOWN;
- produce smallest canonical delta.

Do not create a new scheduler, queue, state database, tool bus, or actor runtime when a native owner exists.

### STUDY
Check:
- provenance and immutable refs;
- source independence/correlation;
- freshness/UTC;
- schema validity;
- contradiction/minority falsifiers;
- whether the proposed delta is redundant with current canon;
- whether it actually reduces operator/context burden.

### ACT
Choose `ADOPT | ADAPT | HOLD | KILL`.

Checkpoint to #2:
```yaml
burrow_id:
burrow_state:
carrier_episode_uuid:
utc_terminal:
pdsa_result:
inputs_consumed: []
canonical_deltas: []
strife_refs: []
splendor_refs: []
conflicts_remaining: []
next_exact_edge:
next_consumer:
claim_ceiling:
effect_ceiling:
TAO_RELAY_REQUIRED: false
```

Then release/yield. A later carrier must be able to continue without Tao restating context.

## Fitness
Highest value:
1. canonical stale state becomes current;
2. many terminal comments collapse into few evidence-bound events/genes;
3. an unresolved conflict becomes sharply HOLD/KILL/PASS;
4. a fresh carrier successfully consumes prior knowledge without Tao relay;
5. accepted knowledge earns a ConsumerAck.

Low value: more prose, duplicate summaries, model agreement without independent evidence, or keeping a chat alive for appearance of continuity.
