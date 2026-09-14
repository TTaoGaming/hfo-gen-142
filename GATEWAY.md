# Gen142 Gateway — JIT Morph

A fresh chat/thread is **uncommitted capacity**, not an actor and not authority.

Canonical ingress:

`GEN142 PICKUP — recover TTaoGaming/hfo-gen-142#13 newest-first, read AGENTS.md + GATEWAY.md + HOLON_MISSION_COMMAND_CONTRACT.md, generate a fresh UUID, emit + validate a Carrier Capability Envelope, then JIT-morph only after ADMIT.`

`TTaoGaming/hfo-gen-142#13` is the active recovery/rendezvous SSOT. `WORLD_STATE/latest.md` and older issue/Wave documents are timestamped projections/evidence only; if they conflict with #13, #13 wins and the conflict must be surfaced without asking Tao to reconcile it.

## Hard admission gate
No carrier may claim, morph, launch a tool/process, or perform a protected effect before a current `hfo.carrier-capability-envelope.v1` passes `tools/gateway_preflight.py`.

Required order:
`RECOVER -> UUID -> OBSERVE CAPABILITIES -> ENVELOPE -> PREFLIGHT ADMIT -> WORKLOAD CLAIM -> MORPH -> SKILL LOAD -> EXECUTE`.

Fail closed as `HOLD`; never infer missing reachability, target binding, admission, Skill load, freshness, or authority. Persist the envelope SHA-256 in the durable claim/result so a later carrier can reproduce the admission decision.

Example:
`python tools/gateway_preflight.py --envelope <file> --workload-id <id> --required-skill <skill> --required-target <target> --required-effect-ceiling <ceiling>`

## Placement default
Oracle VPS is the preferred stable gateway/headquarters/ingress target when its current Carrier Capability Envelope proves compatibility. See `ORACLE_HQ.md` and `ORACLE_GATEWAY.md`.

Default preference:
`oracle-vps -> Cloudflare-native durable execution -> ovh-vps overflow/verifier -> laptop edge/UI`.

This is placement preference only. `PREFERRED_TARGET != REACHABLE != ADMITTED != AUTHORIZED`. If Oracle is unavailable or mismatched, HOLD or select another currently evidenced target; never fabricate reachability.

Cloudflare remains the preferred durable actor/workflow state owner. GitHub remains institutional coordination/evidence. Oracle local disk must not become the only copy of durable work state.

## Morph law
1. Recover #13 newest-first plus `AGENTS.md`, `HOLON_MISSION_COMMAND_CONTRACT.md`, `GENE_SEED.md`, `STANDARDS_PROFILE.md`, `STRIFE_SPLENDOR.md`, and only the evidence/profile files required by the selected current edge. Load `ORACLE_HQ.md` / `ORACLE_GATEWAY.md` only when Oracle placement is actually being considered. Treat `WORLD_STATE/latest.md` as advisory/timestamped only.
2. Generate immutable `carrier_episode_uuid`; record self-attested model/harness and UTC.
3. Observe this carrier's actual Skill/tool/runtime/provider/target capabilities and emit a fresh Carrier Capability Envelope.
4. Run the executable preflight. Non-zero exit or decision other than `ADMIT` means `HOLD`; do not claim work.
5. Treat capacity as supply only: `AVAILABLE_CAPACITY != WORK_DEMAND`.
6. Select one current unresolved Workload/edge compatible with the admitted envelope and placement policy.
7. Morph late into exactly one phenotype: `TWINLING_GATHERER | TWINLING_FALSIFIER | ROACH | REDUCER | VERIFIER`.
8. Load only the admitted required Skill; Skill discovery/loading never enlarges permission.
9. Earlier durable GitHub claim wins. Collision => keep UUID, self-reshard; never ask Tao to arbitrate.
10. Recheck admission before every protected operation.
11. Run one PDSA cycle; target 30 minutes, stop early when falsified or reduced.
12. Before declaring terminal, materialize an `hfo.terminal-handoff.v1` packet and require `python tools/terminal_handoff_gate.py <handoff.json>` to return `ADMIT_TERMINAL`. A prose `next_consumer` is not enough.
13. `TAO_RELAY_REQUIRED=false` by default. Without a genuine enumerated human-only boundary, terminal work must already carry an automatic dispatch/reconcile receipt or a verified mission-complete receipt.

## PDSA
**PLAN** — state the exact question, expected delta, falsifier, evidence needed, effect ceiling, target binding, and acceptance/kill criterion.

**DO** — perform the smallest lawful bounded experiment or evidence recovery. Prefer COTS/native owners and immutable refs. Do not create a new control plane.

**STUDY** — compare evidence against the prediction; preserve UNKNOWN, contradictions, minority falsifiers, correlated-source limits, and operator burden.

**ACT** — `ADOPT | ADAPT | HOLD | KILL`; emit Strife/Splendor events, world-state delta, machine-routable next handoff, and release/yield the carrier.
