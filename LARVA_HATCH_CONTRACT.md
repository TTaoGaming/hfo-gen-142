# Gen142 Larva Hatch Contract v0

Purpose: reduce swarm launch to a stable pointer. Tao supplies intent/authority only; Tao does not choose roles, relay context, collision-resolve, gather terminals, or restart continuation work.

## Canonical launch surface
A fresh carrier starts at `TTaoGaming/hfo-gen-142#13` newest-first, then reads `AGENTS.md`, `GENE_SEED.md`, and this contract. Chat prompts are pointers only and MUST NOT carry orchestration state.

## Hatch law
1. Recover current durable state and build one authoritative `hfo.reconcile_snapshot.v0`.
2. Generate a fresh `carrier_uuid`; never inherit another carrier UUID.
3. Run `python tools/larva_hatch.py <snapshot.json>`.
4. The hatch adapter delegates all next-action selection to `tools/reconcile_kernel.py`; it does not own state, scheduling, leases, authority, or fitness.
5. Morph only into the emitted role/action. If current work is active/collided, the reconciler emits WAIT rather than duplicate work.
6. Execute one bounded edge through admitted owners/capabilities.
7. Terminalize through the existing handoff/verifier/ConsumerAck path and return durable evidence to #13.

## Ownership
`LARVA_HATCH != QUEEN_POLICY != SIGRUN_ACTOR != WORKER != SCHEDULER != QUEUE != AUTHORITY`.

The hatch adapter is disposable glue. GitHub remains intent/evidence rendezvous; Sigrun DO remains semantic claim/fence/deadline/terminal owner; the deterministic reconciler owns cross-boundary next-action policy; workers execute bounded payloads.

## Role derivation
Roles are projections of the deterministic reconcile plan, not independent decisions. If the selected admitted demand declares `role`, that role is emitted; otherwise action kinds map to generic roles (`mission_carrier`, `worker`, `reducer`, `janitor`, `observer`, `resume_watcher`, `idle`).

## Versioning / evolution
Every hatch receipt records `hatch_version`, `policy_version`, `carrier_uuid`, `snapshot_sha256`, and `plan_sha256`. Candidate hatch/policy changes evolve by replay -> failure injection -> canary -> soak -> promotion. No candidate may widen authority or create a second state owner.

## Acceptance
PASS only when a pointer-only launch can repeatedly recover #13, hatch a fresh UUID, receive a machine-selected action/role, execute/terminalize, and permit the next carrier to continue with `tao_hot_loop_actions=0`. Human involvement is valid only for an explicit authority boundary with machine resume already armed.
