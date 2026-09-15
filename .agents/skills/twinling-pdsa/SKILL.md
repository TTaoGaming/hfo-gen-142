---
name: twinling-pdsa
description: Investigate one disputed or uncertain Gen142 evidence edge with a bounded gatherer/falsifier PDSA and leave one compact terminal packet. Use when independent evidence gathering and adversarial falsification are needed; do not use for durable continuation/fan-in or broad Hive integration.
---

# Twinling PDSA

Use only after recovering `TTaoGaming/hfo-gen-142#13` newest-first and `GATEWAY.md`.

## Inputs
- current unresolved Workload/edge
- `carrier_episode_uuid`
- selected role: `TWINLING_GATHERER` or `TWINLING_FALSIFIER`
- `qd_cell_id`: `<domain_family>::<search_regime>::<proof_clock>::<compute_regime>` during `EXPLORE`
- source/evidence scope
- claim/effect ceiling
- target cycle: 30 minutes

## Procedure
### PLAN
Declare one question, expected delta, strongest plausible falsifier, evidence needed, and kill/pass criterion.

During `EXPLORE`, first compute/read the battlefield QD behavior cell. Claim one under-covered **cell**, not merely an attractive role. Read back the claim. If the exact cell already has a live gatherer+falsifier pair (or the configured niche elite budget is full), morph to a different domain/search/proof/compute cell rather than becoming a third reducer/verifier in the same niche. `AVAILABLE_CAPACITY != PERMISSION_TO_CROWD`.

Routing score is not global authority in EXPLORE. A different niche survives even when its current scalar score is lower. Only an explicit `SEND` phase may invoke global convergence.

### DO
Gather or attack evidence. Prefer immutable GitHub refs, sanitized Drive evidence pointers, current authoritative standards, and fresh runtime evidence where authorized. Maximum useful scope beats maximum document count. Preserve the declared QD cell; if evidence changes the phenotype, emit the new cell ID rather than silently collapsing into a crowded lane.

### STUDY
Separate observation from inference; stale from current; same-lineage repetition from independent corroboration; discovery from admission; admission from authority. Test the ablation: `what measurable failure returns if this rule/mechanism is removed?`

### ACT
Choose `ADOPT | ADAPT | HOLD | KILL`. Emit compact Strife/Splendor candidates and world-state delta. In EXPLORE, the terminal updates one QD cell/Pareto candidate and must not name a global primary. Materialize the next handoff before terminal; a prose `next_consumer` is not sufficient. Release/yield rather than becoming an immortal thread.

Before posting terminal, serialize the handoff as `hfo.terminal-handoff.v1` JSON and require:
`python tools/terminal_handoff_gate.py <handoff.json>` -> `ADMIT_TERMINAL`.

## Terminal minimum
```yaml
carrier_episode_uuid:
model_harness:
role:
lane_or_edge:
qd_cell_id:
utc_start:
utc_terminal:
pdsa_plan:
sources: []
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
