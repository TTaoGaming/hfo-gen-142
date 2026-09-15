---
name: twinling-pdsa
description: Investigate one disputed or uncertain Gen142 evidence edge with a bounded gatherer/falsifier PDSA and leave one compact terminal packet. Use when independent evidence gathering and adversarial falsification are needed; do not use for durable continuation/fan-in or broad Hive integration.
---

# Twinling PDSA

Use only after recovering `TTaoGaming/hfo-gen-142#13` newest-first and `GATEWAY.md`.

If ingress came through ZERG LARVA HATCH CONTRACT `5671214300` (or a successor pointer that cites this Skill), this Skill is mandatory before lane selection or material work. The hatch pointer is rendezvous context, not claim authority.

## Inputs
- current unresolved Workload/edge
- `carrier_episode_uuid`
- selected role: `TWINLING_GATHERER` or `TWINLING_FALSIFIER`
- source/evidence scope
- claim/effect ceiling
- target cycle: 30 minutes

## Procedure
### PLAN
Declare one question, expected delta, strongest plausible falsifier, evidence needed, and kill/pass criterion.

Before material work:
1. establish one **admitted durable claim** bound to protected versioned intent and/or authenticated actor state, as required by `GATEWAY.md`;
2. immediately read that claim back from its authoritative owner and retain the claim/receipt reference;
3. re-read #13 newest-first as collision evidence; an arbitrary issue/comment claim never wins authority;
4. if a prior admitted claimant owns the same edge, keep the UUID and morph/reshard before repo mutation, external evaluation, spend, or submission.

A claim that cannot be authoritatively read back is `UNKNOWN`, not ownership. Do not start material work on `UNKNOWN`.

### DO
Gather or attack evidence. Prefer immutable GitHub refs, sanitized Drive evidence pointers, current authoritative standards, and fresh runtime evidence where authorized. Maximum useful scope beats maximum document count.

For a synthetic collision assay, two carriers targeting the same lane must demonstrate: exactly one admitted claimant may perform material work; the loser observes the winning claim and morphs before material effects; each carrier may still emit exactly one terminal for its final role.

### STUDY
Separate observation from inference; stale from current; same-lineage repetition from independent corroboration; discovery from admission; admission from authority. Test the ablation: `what measurable failure returns if this rule/mechanism is removed?`

Before terminal, perform one final newest-first collision/readback check. If a newer admitted owner now exists for the same material edge, do not duplicate it: morph to a non-conflicting verifier/reducer edge or retire with an evidence-bounded terminal.

### ACT
Choose `ADOPT | ADAPT | HOLD | KILL`. Emit compact Strife/Splendor candidates and world-state delta. Materialize the next handoff before terminal; a prose `next_consumer` is not sufficient. Release/yield rather than becoming an immortal thread.

Before posting terminal, serialize the handoff as `hfo.terminal-handoff.v1` JSON and require:
`python tools/terminal_handoff_gate.py <handoff.json>` -> `ADMIT_TERMINAL`.

Reusable Skill/heritage changes remain `genes_hold` until an independent verifier and downstream ConsumerAck both exist. A producer may propose a gene but must not self-admit it.

## Terminal minimum
```yaml
carrier_episode_uuid:
model_harness:
role:
lane_or_edge:
utc_start:
utc_terminal:
pdsa_plan:
sources: []
claim_receipt:
final_collision_check:
strife: []
splendor: []
conflicts: []
genes_promote: []
genes_hold: []
genes_kill: []
strongest_falsifier:
world_state_delta:
next_consumer:
next_handoff:
  mode: AUTO_DISPATCH | RECONCILE | MISSION_COMPLETE | HUMAN_BOUNDARY
  owner:
  work_ref:
  dispatch_receipt:
operator_action_required: NONE
TAO_RELAY_REQUIRED: false
```

If `TAO_RELAY_REQUIRED=false`, terminal requires an already-materialized automatic dispatch/reconcile receipt or verified mission-complete evidence. If true, the boundary must be one of the enumerated human-only authority walls in `tools/terminal_handoff_gate.py`; generic “Tao decide/launch/check” is invalid.

Do not publish secrets/private raw evidence into the public repo. Do not treat same-carrier gather/falsify as independent corroboration.
