# Gen142 ForcePackage Contract v1

Status: `CANDIDATE_R0 / PURE_ADMISSION_COMPILER / NO_DISPATCH`

Purpose: give HQ/voice one small vendor-neutral object that can express a bounded force shape without turning prose, a carrier, or package emission into runtime authority.

## Position in the existing system

This is **not** a new scheduler, queue, actor runtime, state owner, provider router, or verifier.

It composes existing owners:

`TAO_INTENT -> HQ_COMPILE -> FORCEPACKAGE_GATE -> ACTOR_INTENTS -> EXISTING GATEWAY/QUEEN/WORKCELL -> Sigrun semantic claim -> carrier binding -> execution -> verifier -> ConsumerAck`

Canonical laws remain:

- GitHub: versioned intent, evidence, WorkItems, recovery.
- Sigrun Cloudflare Durable Object: semantic claim/fence/deadline/terminal state.
- Gateway + carrier envelope: carrier/target/authority admission.
- Queen/reconciler: deterministic demand-to-capacity allocation.
- WorkCell runtime: bounded native wake/selection/execution/verification/retirement.
- Providers/models: leaf carriers only.

`FORCEPACKAGE != QUEUE != SCHEDULER != RUNTIME_STATE != AUTHORITY`.

## Transition law

`EMIT != ACCEPT != CLAIM != ASSIGN != EXECUTE != VERIFY != SUCCESS`.

`tools/forcepackage_gate.py` proves only the **EMIT -> package-admission** transition. Its successful receipt says:

- package schema/policy/budgets/topology passed;
- deterministic desired actor intents were materialized;
- no carrier/provider has been selected;
- no Sigrun semantic claim exists yet;
- no child was dispatched;
- no verifier has run;
- no ConsumerAck or success exists.

A downstream controller must produce new receipts for every later transition.

## Why actor intents, not executable child missions

A ForcePackage is compiled before capacity allocation. An executable `hfo.holon-mission.v1` requires a `carrier_id`; binding one during HQ compilation would collapse desired actor identity into an unverified carrier.

R0 therefore emits `hfo.actor-intent.v1` records with:

- deterministic actor identity and lineage;
- requested archetype/skill/intent;
- inherited domain, fitness, frozen verifier, deadline/runtime, provider policy, human boundaries, stop conditions and ConsumerAck requirement;
- per-child budget and effect ceiling;
- independent verifier actor relation;
- `carrier_id=null`;
- `provider_binding=null`;
- `status=DESIRED_NOT_CLAIMED`.

The existing Gateway/Queen path later binds admitted capacity and the Sigrun semantic owner claims executable work.

## Package bounds

Schema: `hfo.forcepackage.v1`.

The package binds:

- `package_id`, `mission_id`, `root_actor_id`;
- domain + intent + externally verified fitness;
- frozen final verifier policy (`id`, `frozen=true`);
- deadline, runtime, attempts, spend;
- package effect ceiling;
- canonical receipt sink + Sigrun semantic owner;
- provider policy (`role=leaf`);
- declared human authority boundaries;
- stop conditions;
- maximum children + concurrency;
- one or more formations.

Aggregate bounds are real bounds: the sum of `count * per-child attempts/spend` cannot exceed package limits.

R0 supports at most 128 desired child actors. This is an admission limit, not a throughput claim.

## Formation / verifier law

R0 executable worker archetypes are only the worker/verification phenotypes already defined in `ZERG_CAPACITY_ARCHETYPES.md`:

`LING | TWINLING | ROACH | RED_QUEEN | REDUCER | VERIFIER | EXTRACTOR`

Mechanism/state archetypes (`QUEEN`, `HATCHERY`, `OVERLORD`, `BURROW`, `EVOLUTION_CHAMBER`, `HIVE`) are not child worker formations.

`HYDRA` and `ULTRALISK` remain semantic handles in the voice anchor but do not yet have a versioned engineering contract. R0 fails closed with `ARCHETYPE_UNVERSIONED` rather than guessing their behavior.

Every non-VERIFIER formation must reference a distinct formation whose archetype is `VERIFIER`. A verifier formation cannot recursively designate itself. Distinct actor identity is required here; distinct provider/host/failure-domain binding is a downstream capability-admission obligation and is **not** claimed by this gate.

## Effect / authority law

- Child effect ceiling must exactly equal the package ceiling in R0. A later version may add a versioned partial order for narrowing.
- `new_control_plane=true` is refused.
- `tao_relay_required=true` is refused at package-admission time. A later executable mission may honestly HOLD at a declared human-only boundary and arm its machine resume watcher.
- Unknown fields fail closed. New semantics require a schema/version change.
- The gate performs no network calls and owns no durable state.

## Determinism

Semantic normalization sorts:

- formations by `formation_id`;
- human boundary names;
- stop-condition strings.

Equivalent reordering therefore produces the same package hash, actor IDs, actor-intent hash, and admission hash.

Actor IDs include a prefix of the normalized package hash. Editing package semantics creates a new desired actor lineage instead of silently reusing actor IDs.

## R0 acceptance assay

ADMIT requires at least:

1. future deadline and finite package bounds;
2. frozen final verifier policy plus externally verified fitness;
3. exact Sigrun semantic owner and #13 receipt sink;
4. provider role remains leaf;
5. no new control plane and recover/probe/repair already completed;
6. at least two materialized children;
7. at least one versioned VERIFIER formation;
8. each non-verifier formation points to a VERIFIER formation;
9. aggregate attempts/spend remain inside package bounds;
10. no child effect widening;
11. deterministic replay.

The R0 gate must also prove its negative statement: an admitted receipt contains `execution_status=NOT_DISPATCHED` and no success/ConsumerAck claim.

## Next adapter after R0

Do **not** create a ForcePackage scheduler.

The next edge is one thin materializer/controller adapter:

`ADMITTED actor intents -> existing WorkItem schema(s) + Gateway preflight -> Sigrun semantic claim -> existing WorkCell/native owner`

That adapter must be controller/API-observed, idempotent, and prove at least two child actors + verifier closure with `TAO_HOT_LOOP_ACTIONS=0` before scale is increased.
