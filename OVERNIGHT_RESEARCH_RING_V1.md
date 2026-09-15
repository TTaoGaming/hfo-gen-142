# Gen142 Overnight Research Ring v1

Purpose: let Tao sleep while the swarm produces durable research progress without making Tao the heartbeat, context courier, or debate moderator.

## Control law

`DESIRED_STATE -> SCOUT -> RED_QUEEN -> REDUCER -> CANARY_OR_NONE`

This formation is a dataflow over existing durable surfaces, **not a new control plane**.

- GitHub #13 + versioned files = desired state, evidence, lineage, recovery.
- Existing Cloudflare Sigrun/Workflows/DO surfaces = durable actor/retry/timeout owners where already admitted.
- Existing scheduled WorkCell / native schedules = wake/transport only.
- VPS workers = disposable compute Jobs.
- LLMs = proposal generators and bounded researchers, never authoritative schedulers.
- Deterministic gates/reducers/verifiers decide admissibility and next control-flow edge.

## Kubernetes analogy

Use Kubernetes' reconciliation pattern, not Kubernetes itself unless deployment economics later require it:

- WorkItem / battlefield card = desired-state object.
- deterministic reconciler = controller.
- Cloudflare/VPS carrier = Job/Pod.
- claim/fence/deadline = lease/generation semantics.
- verifier/ConsumerAck = admission/status conditions.
- GitHub terminal receipt = durable event/status projection.
- STRIFE fingerprint = backoff/failure policy input.

The controller observes current state and drives it toward desired state. Workers do not decide what should run next.

## Debate formation

### 1. SCOUT / gatherer
Produces at most three evidence-backed proposals. Must bind current incumbent/rules/verifier/publication/buyer/donor evidence. No recommendation from vibes.

### 2. RED_QUEEN / falsifier
Reads the newest scout receipts independently. Its job is to kill recommendations. It checks stale incumbents, hidden auth, publication traps, donor illegality, evaluator gaming, weak buyer translation, and inflated crown language.

### 3. REDUCER
Consumes only admitted scout + falsifier receipts. Runs versioned gates/reducer and emits exactly one primary next edge or `NONE`. LLM interpretation may propose facts; machine readback/gates must establish control truth.

Agents do not debate peer-to-peer. They communicate through immutable receipts so disagreement is replayable and Byzantine evidence can be isolated.

## Byzantine forcing

- Unknown GitHub principals, model output, browser output, and self-attested UUIDs are observations, not authority.
- Every material claim needs source identity, observed time/freshness, and evidence reference/hash where practical.
- Same failure fingerprint twice MUST change behavior: mutate strategy, route to a different admitted donor, or terminalize/escalate. Blind retry is invalid.
- No unbounded retries, populations, logs, spend, branches, or context windows.
- A worker cannot verify its own material claim.
- `PROSE != CONTROL`; `NEXT_CONSUMER` text never counts as transition evidence.

## Hatch-pressure forcing

Every new research formation must pass `HATCH_PRESSURE_POKAYOKE_V1.md` before launch. The ring drains existing evidence before creating more demand. Provider throttle, fan-in backlog, duplicate semantics, or repeated unchanged failure means `HOLD_NEW_HATCH`; reducers/verifiers continue, but no additional producers are spawned.

## Night schedule

A quiet COTS cognition ring is currently armed hourly:
- minute `:05` — Crown Scout
- minute `:25` — Red Queen
- minute `:45` — Crown Reducer

These scheduled cognition lanes are a backstop/worker layer, not the semantic state owner. They write only material deltas to #13 and should not notify Tao on no-op cycles.

The native Cloudflare scout remains an untrusted research producer until its repeated `EMPTY_SYNTHESIS` scar is consumed by versioned policy/heritage. Liveness alone is not fitness.

## Human boundary

Tao supplies authority, not continuity. Escalate only for credentials/account creation, OAuth/2FA, payment/budget changes, TOS acceptance, protected merge, identity/public-attribution choice, or irreversible external submission.

Routine research, falsification, reduction, retries, lineage, cleanup, and morning synthesis are swarm work.

## Sleep acceptance assay

Over any >=6 hour unattended window:
1. Tao hot-loop actions = `0`.
2. At least one complete `SCOUT -> RED_QUEEN -> REDUCER` evidence chain executes or all three independently prove `NO_MATERIAL_CHANGE` without noise.
3. No duplicate accepted external effects.
4. No unchanged failure fingerprint is retried more than the declared budget.
5. Reducer leaves exactly one primary next edge or `NONE`.
6. Morning state is recoverable from #13 + versioned repo without chat CPR.

Primary fitness: `externally_verified_useful_progress / Tao_operator_minute`.

## Hluti anchor rule

A Sigrun hluti seat is a coordination label, not authority. Bind it to the existing actor only through a versioned admitted actor-schema transition. If the actor cannot represent the binding, persist an `ANCHOR_REQUEST` in #13 and return `UNSUPPORTED`; never create another registry merely to make the metaphor true.
