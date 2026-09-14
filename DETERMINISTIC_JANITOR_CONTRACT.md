# Gen142 Deterministic Janitor Contract v0

Purpose: remove routine cleanup from Tao without allowing a cleanup agent to become a destructive control plane.

The janitor is a **leaf effect guard**, not an actor, scheduler, queue, memory system, or authority owner.

`JANITOR_GATE != RECONCILER != SIGRUN_ACTOR != WORKER != AUTHORITY`.

## Ownership law

The deterministic reconciler may select at most one already-admitted cleanup candidate per wake. It may not delete anything itself.

Actual cleanup is performed by a bounded leaf executor after `tools/janitor_gate.py` returns `ADMIT_CLEANUP`. The executor must re-read target identity immediately before effect.

Tao is never asked to inspect scratch directories, check whether a worktree is stale, kill ordinary expired jobs, prune caches, or remember what can be deleted.

## Cleanup candidate

A cleanup request is `hfo.cleanup-request.v1` and binds exactly one resource to one durable WorkItem.

Required facts:
- `cleanup_id` and `work_ref`;
- `actor_owner == hfo-sigrun-va-r0`;
- exact `resource_id`, `kind`, `target`, and `owner_work_ref`;
- explicit `requested_action` matching the resource kind;
- resource is disposable, not protected, and has no external-effect authority;
- TTL is expired at the trusted observation time;
- no active lease remains;
- no verifier/ConsumerAck/other declared consumer is pending;
- durable terminal evidence exists and is not self-attested;
- the current OS/Git observation matches the recorded target identity;
- target resolves strictly *below* a trusted runtime-supplied allow-root.

Missing, stale, contradictory, self-attested, broad-path, or identity-mismatched cleanup evidence is `HOLD`.

## R0 action surface

R0 supports only:
- `DELETE_TEMP_DIR` for `TEMP_DIR`;
- `DELETE_CACHE_DIR` for `CACHE_DIR`;
- `REMOVE_WORKTREE` for a clean Git-registered `WORKTREE`.

R0 deliberately does **not** kill arbitrary processes, remove containers, delete repositories/branches, clear provider state, rotate secrets, or mutate external services. Those need provider-native ownership and separate admission.

For `REMOVE_WORKTREE`, the leaf executor must prove the target is a registered worktree and `git status --porcelain` is empty. Removal uses normal `git worktree remove` without `--force`; the branch/ref survives.

For directory deletion, the target must contain a matching `.hfo-cleanup-owner.json` ownership marker immediately before deletion.

## Path safety

The allow-root is supplied by trusted runtime configuration, never by the candidate request.

The gate refuses:
- filesystem roots;
- the user home directory as an allow-root;
- target equal to allow-root;
- target outside all allow-roots;
- relative targets;
- symlink/realpath escape;
- protected resources;
- non-disposable resources.

## Evidence preservation

Cleanup may remove execution residue only after the durable evidence needed to reconstruct the WorkItem lives elsewhere.

`DELETE_RESIDUE != DELETE_HISTORY`.

GitHub evidence, verifier receipts, ConsumerAck, lineage/heritage, public proof, and canonical actor state are never janitor targets.

Every admitted cleanup writes a receipt containing request hash, observed target identity, action, result, and UTC. A failed cleanup remains visible and is reconciled later; it is never silently treated as success.

## Reconciler priority

After terminal evidence is consumed and before new unrelated demand, the reconciler may emit one `CLEAN_RESOURCE` action for the lexically first admitted cleanup candidate. One cleanup per wake prevents cleanup storms.

If cleanup is blocked, useful admitted work may continue only when the blocked residue is below resource/host safety thresholds. Capacity Andon can independently stop new work.

## Retry law

Cleanup retries are bounded. Same hypothesis + same failure may not loop forever.

Default ladder:
1. one normal cleanup attempt;
2. one fresh-observation retry if target identity is unchanged;
3. terminal `HOLD_CLEANUP` with evidence.

No neural agent may reinterpret a refused target into an easier delete command.

## Acceptance

R0 is admitted only after hostile tests prove:
- expired owned temp residue is admitted;
- pre-TTL residue is refused;
- active lease is refused;
- pending consumer is refused;
- missing/non-durable evidence is refused;
- self-attested evidence is refused;
- target outside allow-root is refused;
- target equal to allow-root is refused;
- ownership-marker mismatch is refused;
- dirty/unregistered worktree cannot be removed;
- same canonical request + observation produces the same gate decision;
- no cleanup path can target canonical GitHub evidence or actor state.

Target operator metric: `routine_cleanup_actions_by_tao = 0`.
