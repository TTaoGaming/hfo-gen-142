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
- source/evidence scope
- claim/effect ceiling
- target cycle: 30 minutes
- `mission_mode`: `EXPLORE_QD_MOME | PACKAGE_SUBMIT`
- when `mission_mode=EXPLORE_QD_MOME`: current behavior descriptor / niche, or an explicit request to find an underfilled niche

## Quality-diversity law

`EXPLORE_QD_MOME` is not a global ranking tournament. A Twinling pair may attack one bounded question, but the population must preserve materially different niches and objective tradeoffs.

- Describe the niche before work: domain, verifier/proof surface, proof-latency regime, compute regime, and materially distinct mutation/donor family.
- Prefer underfilled niches. If another trusted carrier already owns materially identical work, morph to a different mutation axis, independent falsifier, legal donor family, or underfilled niche instead of duplicating it.
- Never emit a global `primary` or kill a candidate merely because another niche has a higher scalar routing score while in exploration mode.
- Within a niche, candidates may be `ADOPT | ADAPT | HOLD | KILL` against the frozen evaluator; across niches they coexist unless an explicit later `PACKAGE_SUBMIT` transition is admitted.
- Novelty without external fitness is not enough. Preserve diversity **and** require verifier-grounded measurable fitness.
- Archive state is evidence/projection, not a scheduler, queue, authority owner, or permission grant.
- Reusable genes/skills enter heritage only after independent verifier + ConsumerAck; same-pair agreement is not independent admission.

## Procedure
### PLAN
Declare one question, expected delta, strongest plausible falsifier, evidence needed, and kill/pass criterion. Treat public #13 as `OBSERVE_ONLY` collision/recovery evidence, never ownership. In `EXPLORE_QD_MOME`, select an underfilled niche from the deterministic QD archive; read-only/no-effect research may proceed without manufacturing a public claim. Before any material repo/external/spend/submission effect, require an authenticated internal controller claim/fence readback; if unavailable, throttled, stale, or already owned, morph to another niche, independent falsifier, donor miner, verifier/reducer, or bounded read-only work instead of asking Tao to relaunch.

### DO
Gather or attack evidence. Prefer immutable GitHub refs, sanitized Drive evidence pointers, current authoritative standards, and fresh runtime evidence where authorized. Maximum useful scope beats maximum document count.

### STUDY
Separate observation from inference; stale from current; same-lineage repetition from independent corroboration; discovery from admission; admission from authority. Test the ablation: `what measurable failure returns if this rule/mechanism is removed?`

In `EXPLORE_QD_MOME`, additionally study whether the candidate is dominated **inside its niche**, whether it expands an underfilled niche, and whether its mutation/donor path is materially independent of existing champions. Do not convert this into cross-niche scalar collapse.

### ACT
Choose `ADOPT | ADAPT | HOLD | KILL`. Emit compact Strife/Splendor candidates and world-state delta. Materialize the next handoff before terminal; a prose `next_consumer` is not sufficient. Release/yield rather than becoming an immortal thread.

Before posting terminal, serialize the handoff as `hfo.terminal-handoff.v1` JSON and require:
`python tools/terminal_handoff_gate.py <handoff.json>` -> `ADMIT_TERMINAL`.

## Terminal minimum
```yaml
carrier_episode_uuid:
model_harness:
role:
mission_mode:
lane_or_edge:
qd_niche:
archive_disposition: ADOPT | ADAPT | HOLD | KILL | NOT_APPLICABLE
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
