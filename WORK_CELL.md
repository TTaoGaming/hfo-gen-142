# Work-cell projection into the Hatchery/Larva ABI

This is a thin binding of [HATCHERY_LARVA_ABI.md](HATCHERY_LARVA_ABI.md), not a
second ABI or scheduler. The first admitted profile is `packing.recipe.v1`.
Image generation, research and executable algorithm generation remain unsupported
until an adapter and its independent acceptance test are admitted.

Current [evidence receipt](hatchery/shinka-cell/WORK_CELL_R1.json): hosted input
cell PASS, live model cell HOLD. Two numerical generations and 16 trials completed
in 29.01 seconds including a supervisor replacement. No champion was found.

## Ownership and context

| Owner | Responsibility |
|---|---|
| Existing Cloudflare DO | Immutable admission, deadline, shared call reservations, cancellation, verified generation receipts and compact result memory |
| Existing NativeJob AgentWorkflow | Durable job identity, wait for result, structural identity/hash validation and terminal result |
| R2 | Content-addressed input context, model prefix and accepted artifacts |
| Oracle systemd | Resource limits, process-group cleanup and one bounded process replacement |
| Installed Shinka | Proposal/evaluation sequence, accepted-proposal checkpoint and numerical archive |
| Frozen VPS evaluator | Data-only recipe validation, eight bounded numerical trials, candidate artifact |
| Cloudflare integer checker | Independent exact geometry acceptance outside the candidate runtime |

The `gen142.work-context/0` projection binds the parent, evaluator and executable
adapter file hashes. The caller checks those files before starting. A restart
gets a fresh supervisor episode UUID; it keeps the work ID, original deadline,
model reservations and accepted checkpoint. It cannot renew any allowance.

Context cleaving happens at a verified generation boundary. The task's system
prefix is pinned in the manifest. Shinka randomly varies its rewrite-format
suffix; `context.py` separates that suffix into another system message while
preserving its bytes and instruction role. Later turns must use the same task
prefix and a bounded delta. Accepted results update compact DO memory;
Shinka's next turn consumes its evaluated archive. Full prompt history is not
copied into a second memory system. R2 stores the prefix once and responses can
be replayed by request hash without a second inference effect.

This proves application input reuse only. The adapter still sends the required
prefix to each provider. Provider prompt-cache hits, discounted tokens and
cross-provider cache sharing are not inferred from an R2 object or a hash match.

## Finite admission and operations

The initial hosted assay is deliberately a single fixed admission: two model
requests, two evaluated generations, 600 seconds, no additional paid spend,
existing Kimi then free Google lanes, and no inference retries. Its admission
window expires at 2026-09-14 07:00 UTC. Two separately identified engineering
assays accept two explicit input recipes each and grant **zero** model calls.
Their input receipts are separate from provider reservations; serving a recipe
through Shinka's completion-shaped interface is not model inference. These
assays do not refill the failed Kimi mission's allowance.
Changing a work ID or restarting a process
does not create another allowance. This is not an overnight campaign grant.

The authenticated `/vps/work-cell` projection supports `admit`, `status`, `model`,
`generation`, `finish`, `fail` and `stop`. It inherits the existing private VPS route.
An identical admission, request or generation can be read back; conflicting
content under the same identity is refused. A pending model effect is held,
never blindly replayed. The next distinct proposal is refused until its previous
result is independently verified. Stop closes admission even with a reservation
in flight; an already returned bounded result can still be verified.

The runtime accepts a complete eight-trial evaluation and a non-regressing
artifact. The checker independently verifies all 119 containment constraints
and 7,021 pair distances using scaled integers. A retained incumbent is a valid
disposition, not a new champion. A strict improvement above the existing 1e-8
threshold stops the mission. `RESULT_SUBMITTED` is not proof of native Workflow
completion; the supervisor requires the Workflow's terminal status.

The supervisor is an adapter around Shinka, not another evolutionary engine.
It uses systemd restart-on-failure, a two-start cap, 300 seconds per episode,
768 MiB memory, one CPU, 32 tasks and 1 MiB per output file. A known failure exits
78, which systemd must exclude from restart. A rejected job is closed in the
native Workflow, not left waiting for another proposal. The DO's original
600-second deadline covers both episodes. The test kills the owned caller and
descendants after its accepted proposal checkpoint; systemd starts the replacement.

## Evidence boundaries

Unit fixtures verify refusal, immutability, cancellation, exact geometry and
duplicate handling without live calls. The native local workerd assay replaces
the runtime and restores DO/R2 state; its provider and NativeJob service are
fixtures, so it is not hosted Workflow proof. Hosted evidence is recorded
separately in the run receipt.

The initial slice is same-host recovery with one active writer. Cross-host
migration, general fencing, laptop/OVH parity, recovery during ambiguous Workflow
creation, an overnight soak and general profile admission are not proven here.
An uncertain `START_RESERVED` state remains a hold, not permission to recreate
the Workflow. Material result validity is checked by a separate runtime
principal; this is not a claim of separate human authorship or keeper acceptance.

Do not clone active cells until the shared account reservation and recovery
evidence justify concurrency. The next extension should populate the existing
admission from a pinned workload manifest, not add a queue, router or scheduler.
