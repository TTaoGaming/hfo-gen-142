# Gen142 Burrow — Durable Roach Fan-In

Parent/control: GitHub issue #2. Input evidence lake: issue #1 newest-first.

## Ontology
`BURROW != ROACH != CARRIER != MODEL != AUTHORITY`.

- **Burrow** = durable logical state slot for one long-lived fan-in responsibility.
- **Roach** = the recoverable work lineage occupying that slot.
- **Carrier** = disposable chat/model episode that temporarily continues the Roach.
- **Cloudflare Agent / Durable Object** = intended hot durable owner when independently deployed and assayed.
- **GitHub** = institutional evidence, recovery, admission and shadow ledger.

Do not claim a live Cloudflare burrow merely because this contract exists. Until a live persistence/restart assay passes, burrow runtime state is `GITHUB_SHADOW_ONLY`.

## Initial burrows
- `B0 TERMINAL_FANIN` — census #1 claims/terminals, deduplicate, route reducer inputs.
- `B1 STRIFE` — normalize scar/pain/failure evidence into canonical Strife records.
- `B2 SPLENDOR` — normalize success/proof/mechanism evidence into canonical Splendor records.
- `B3 HERITAGE_CATALOG` — source census across GitHub/Drive; track UNSCANNED -> TRIAGED -> REDUCED.
- `B4 WORLD_STATE` — roll accepted deltas into small fresh world-state capsules; preserve UNKNOWN/staleness.
- `B5 IDENTITY_A2A_SKILLS` — identity, A2A Agent Card, Agent Skills, MCP/tool admission boundaries.
- `B6 CLOUDFLARE_VPS_CURRENTNESS` — current runtime/dependency truth; no historical liveness laundering.
- `B7 WORLDWEAVER` — public regeneration/delivery path and GitHub fallback.

Burrows are responsibilities, not authority domains. A carrier may self-reshard when another current carrier already owns the same edge.

## Durable state minimum
A burrow checkpoint should fit in one compact record:

```yaml
burrow_id: B0..B7
burrow_state: GITHUB_SHADOW_ONLY | CLOUDFLARE_ASSAY | CLOUDFLARE_LIVE | HOLD
carrier_episode_uuid:
observed_utc:
source_cursor:
current_pdsa_phase: PLAN | DO | STUDY | ACT
current_question:
accepted_event_refs: []
pending_conflicts: []
pending_inputs: []
world_state_delta:
next_exact_edge:
next_consumer:
checkpoint_hash:
claim_ceiling:
effect_ceiling:
TAO_RELAY_REQUIRED: false
```

If Cloudflare backing becomes live, the same semantic record belongs in Agent/DO durable state; GitHub receives compact receipts/material transitions, not every hot mutation.

## Carrier pickup
1. Read #2 newest-first, then #1 newest-first.
2. Read `GATEWAY.md`, `BURROW.md`, and `.agents/skills/roach-fanin/SKILL.md`.
3. Generate a fresh `carrier_episode_uuid`.
4. Recover an existing burrow needing continuation, or take the highest-value under-covered burrow.
5. Post claim, read back, and yield/self-reshard on an earlier durable owner. Readback is not CAS/atomic exclusion.
6. Continue from the burrow checkpoint; do not restart research from zero.
7. Run one bounded PDSA cycle, target 30 minutes; stop early on decisive reduction.
8. Checkpoint compact state to #2 and release the carrier.

## Fan-in law
Roaches are rewarded for **compression and consumption**, not comment count.

Prefer:
`terminal -> normalize -> dedupe -> falsify -> canonical event/gene/world-state delta -> ConsumerAck`

over:
`terminal -> another summary -> another summary`.

No accepted canonical mutation should depend on Tao repeating context.

## Cloudflare acceptance
A burrow may be marked `CLOUDFLARE_LIVE` only after one admitted assay demonstrates:
1. stable burrow/actor identity survives transient carrier death;
2. required checkpoint state persists and is recoverable;
3. duplicate accepted effects = 0 across retry/restart;
4. GitHub recovery receipt can rehydrate a fresh carrier;
5. Lenovo is unavailable during the proof;
6. no Tao context ferry/routine restart is required.

Use Cloudflare-native Agent/DO state and Workflows/Fibers where appropriate. Do not build another HFO persistence/runtime layer unless an exact native gap is evidenced.

## Current gateway requirement
For new pickups, follow `GATEWAY.md`: generate the carrier UUID, emit the current Carrier Capability Envelope, and run the gateway preflight before taking a burrow. A failed preflight means `HOLD`. Record the preflight envelope hash in the burrow checkpoint.