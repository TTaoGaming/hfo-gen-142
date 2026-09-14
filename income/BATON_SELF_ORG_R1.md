# GEN142 Income Self-Organization Baton — R1

Control: issue #9. Income mission: issue #7.

## Current state
- `income/self_org_r0.json` and `income/self_org_r0.py` are on main.
- Oracle capability-aware self-selection is working.
- I7 is held on Oracle when `drive_read` is unavailable; I8 is the next Oracle-compatible lane.
- Existing GEN142 gateway remains the execution admission membrane.
- Local Ollama is advisory only; symbolic rules own eligibility and authority.
- Oracle HQ bridge can queue hash-bound intent in fail-closed state until a durable writer consumes it.

## Next PDSA
Close only this seam:
`Oracle HQ intent -> unattended GEN142 durable write -> exact GitHub readback`.

Then rerun one bounded I8 cycle:
`self-select -> claim -> execute -> terminal -> readback`, with no Tao morphing or routine routing.

## Rules
- reuse existing GitHub/runner primitives; do not create another scheduler, queue, or state store;
- no external send or spend;
- neural advice cannot widen authority;
- missing write authorization remains HOLD, not fake green.

## Pickup
`GEN142 SELF-ORG BATON — recover TTaoGaming/hfo-gen-142#9 newest-first + income/BATON_SELF_ORG_R1.md -> fresh UUID -> close only the Oracle-to-GEN142 durable-write seam -> rerun one I8 claim/terminal with exact readback -> terminal once to #9. Do not ask Tao to morph or route.`

TAO_RELAY_REQUIRED=false except for a genuine authorization wall.
