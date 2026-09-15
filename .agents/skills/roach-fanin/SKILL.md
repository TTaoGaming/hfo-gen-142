---
name: roach-fanin
description: Continue an existing Gen142 durable fan-in or recovery workload by consuming prior terminal evidence, reconciling stale canonical state, checkpointing compact durable state, and releasing. Use when work/evidence already exists and continuation or reduction is needed; do not use for new discovery.
---

# Roach Fan-In Skill

Use when a fresh carrier should continue durable reduction/fan-in rather than start a new discovery lane.

## Trigger
- #13 identifies an under-covered/stale fan-in edge;
- linked historical issues contain terminal evidence waiting for reduction;
- canonical Gen142 state is stale versus accepted evidence;
- a prior Roach carrier ended and durable continuation is needed.

## Contract
A fresh thread is disposable cognition. It does not become durable by staying alive. Recover #13 newest-first, continue one bounded PDSA cycle, checkpoint, materialize the next machine transition, and release.

### PLAN
- recover #13 newest-first; follow linked historical evidence only when needed;
- select/recover one fan-in edge;
- generate fresh `carrier_episode_uuid`;
- state exact fan-in question, expected delta, strongest falsifier, evidence needed, and effect ceiling;
- acquire the semantic claim/fence through the authenticated internal controller and immediately read back owner, fence/generation, and deadline; earlier authoritative claim/fence wins. Only then project a sanitized claim to #13; public issue/comment ordering never decides ownership.

### DO
Prefer reducer work:
- consume unconsumed terminals;
- normalize Strife/Splendor to pinned schemas;
- deduplicate repeated genes/scars;
- update source catalog dispositions;
- reconcile currentness/UNKNOWN;
- produce the smallest canonical delta.

Do not create a new scheduler, queue, state database, tool bus, or actor runtime when a native owner exists.

### STUDY
Check provenance, source independence, freshness, schema validity, contradictions, redundancy, and whether the delta actually reduces operator/context burden.

### ACT
Choose `ADOPT | ADAPT | HOLD | KILL`.

`next_consumer` is descriptive metadata only. It is never proof that work was handed off. Before release, serialize `hfo.terminal-handoff.v1` and require:

`python tools/terminal_handoff_gate.py <handoff.json>` -> `ADMIT_TERMINAL`.

Checkpoint current state to #13:
```yaml
fan_in_edge:
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
next_handoff:
  mode: AUTO_DISPATCH | RECONCILE | MISSION_COMPLETE | HUMAN_BOUNDARY
  owner:
  work_ref:
  dispatch_receipt:
claim_ceiling:
effect_ceiling:
operator_action_required: NONE
TAO_RELAY_REQUIRED: false
```

A machine continuation must carry a structured, non-self-attested transition receipt accepted by `terminal_handoff_gate.py`. A genuine human-only authority wall must already have an automatic resume watcher armed before escalation. Tao may unlock authority; Tao must not launch, retry, route, monitor, gather, or restart the next carrier.

Then release/yield. A later carrier must be able to continue without Tao restating context.

## Fitness
Highest value:
1. canonical stale state becomes current;
2. many terminal comments collapse into few evidence-bound events/genes;
3. an unresolved conflict becomes sharply HOLD/KILL/PASS;
4. a fresh carrier successfully consumes prior knowledge without Tao relay;
5. accepted knowledge earns a ConsumerAck;
6. terminal-to-next transition happens without Tao.

Low value: more prose, duplicate summaries, model agreement without independent evidence, or keeping a chat alive for appearance of continuity.
