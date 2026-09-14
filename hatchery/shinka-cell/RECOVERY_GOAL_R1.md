# Bounded stabilization: cancellation and recovery

**Approved follow-up:** the Oracle module was installed at 2026-09-14 04:24:07 UTC
with exact candidate and rollback hashes verified. The installed-package assay
passed in 59.141 seconds: two verified generations, zero repeat requests for the
resumed proposal, all three negative cases and single-writer exclusion passed.
See [INSTALL_R1.json](INSTALL_R1.json). Feature activation was confined to the
isolated cached-response assay. No live campaign or Cloudflare deployment started.
The original bounded-goal account below remains historical evidence.

The first installed-package test revealed a harness shutdown race: the caller
could commit while its descendants were being killed. The harness now freezes
the caller first and asserts the archive is unchanged during shutdown. The
installed module required no further change. Production supervisors must stop
the complete process group before replacement; automatic production recovery
is still unproven. The prior installation approval blocker is now resolved.

Goal started 2026-09-14 03:52:46 UTC; deadline 04:22:46 UTC.
Evidence: [GOAL_R1.json](GOAL_R1.json). This cycle made **zero live model calls**,
changed no spending caps, and installed no production changes.

## Outcome

Two native Shinka generations completed after an interruption in a temporary
Oracle library copy, using cached proposal responses. Both ran eight numerical
trials and passed a separate exact rational check of 119 sphere containments and
7,021 pairs. Both retained the incumbent; neither is a new champion.

The test harness killed the caller and its evaluator descendants, launched a
replacement, and checked the archive. The interrupted generation reused its
accepted proposal without a model request. The following generation consumed one
fixture response. A final restart left the archive and request count unchanged.
The expanded assay took 53.934 seconds, including negative tests and restarts;
this is not live generation latency or steady-state takt time.

**Two verified fixture generations: YES. An unattended live campaign: UNPROVEN.**
The harness supplied restart orchestration. Production recovery, hosted
cancellation, shared-account admission and the joined two-generation acceptance
test remain outstanding. This is useful repair evidence, not fleet readiness.

## Small changes to the existing engine

`shinka-evaluation-checkpoint.patch` adds an opt-in accepted-proposal checkpoint
to the installed Shinka 0.0.7 runner. It preserves the existing proposal,
evaluation and database paths; it introduces no search engine or scheduler.

- Before evaluation, atomically persist the accepted candidate's hash, pinned
  task-file hashes, parent references and proposal/cost metadata; fsync the file
  and containing directory.
- On restart, reuse that proposal for evaluation without requesting it again.
- Refuse unfinished generations with missing checkpoints, changed candidates or
  changed evaluators before any model request. An ambiguous proposal is a HOLD.
- `run.py` uses Linux `flock` for one caller per work directory when
  `SHINKA_EVAL_CHECKPOINT=1`. The feature is off by default. This lock does not
  fence separate directories or hosts, and surviving evaluator processes must
  be stopped by the supervisor before replacement.

This opt-in is intentionally limited to the pinned data-only packing task.
It does not authorize arbitrary generated code, recover an uncertain provider
effect, renew a campaign budget or provide cross-host ownership fencing.

## Verification

`checkpoint_assay.py` passed in a network-isolated, time/resource-bounded
temporary VPS copy. The installed system package's hash was unchanged afterward.
It rejected all three negative cases with exit 1 and zero new fixture requests:
missing checkpoint, changed candidate, changed evaluator. A competing caller
failed with `BlockingIOError`. The separate checker is separate code, not a
distinct security principal or independent human review.

`../pdsa-native-assay.mjs` passed with real local workerd Durable Objects and R2
and mocked egress. A stop acknowledged during quota wait prevented dispatch;
an acknowledged stop during an in-flight request survived its late response and
prevented subsequent dispatch. Five existing cancellation tests also passed.
Five recipe-boundary/telemetry tests passed. Installed workerd supports
compatibility date 2026-09-02, older than production's 2026-09-11. No hosted
deployment, eviction, persistence-failure or joined VPS/DO proof is inferred.

Local commands, with existing dependencies supplied:

```powershell
node --test --test-isolation=none hatchery/pdsa-budget.test.mjs
# MINIFLARE_MODULE may point to the installed Miniflare module.
node hatchery/pdsa-native-assay.mjs
Set-Location hatchery/shinka-cell
$env:PYTHONPATH='..'
python -m unittest test_recipe.py test_telemetry.py
```

The VPS assay requires a fresh private fixture directory containing `run.py`
(configured for three total generations, including baseline), `evaluate.py`,
`initial.py`, `packing_generations.py`, the admitted `parent.pck` and a saved
OpenAI-shaped `cached-response.json`. Supply the temporary patched Shinka copy
through `PYTHONPATH`. Run the assay under the existing bounded native supervisor
with networking disabled. It intentionally kills only its owned child processes.
Do not point it at a live campaign directory or provider endpoint.

## Reviewable installation boundary

The candidate targets `/opt/hfo-evolution/venv/lib/python3.12/site-packages/shinka/core/async_runner.py`:

- Required original SHA-256: `0ae3308ebf16f910f82883d1d15255aa32622c5f0503017fd8d5a4d9108d1691`
- Tested candidate SHA-256: `4ea52abb2c46da529ea3e06fd51ba39918205820d05dfbd3cf5fb3df1602f6b3`

Applying the committed patch with `git -c core.autocrlf=false apply` to the
required original reproduced the candidate exactly and passed Python compilation.
Preserve a hash-checked original for rollback, refuse source drift, and verify the
installed readback. Enabling the feature also requires the tested `run.py` lock.
Installation must not start a campaign or alter an existing allowance.

Automatic approval review rejected the persistent sudo installation, citing
the remote modification, workspace routing and the earlier source guard failure.
That installation was not retried. Explicit approval of the tested installation
is the remaining deployment step; the isolated experiment did not alter the
system package. Cloudflare cancellation likewise remains a tested local candidate
requiring a current-version-guarded deployment and hosted verification.

## Strife and retained guardrails

- The original runner treated an unfinished generation directory as unavailable
  and could exit successfully with a missing generation. Check expected archive
  generations and their verifier results, not process exit alone.
- One expanded fixture delayed the kill to test the lock and allowed a second
  proposal to start. That run failed its request-count assertion and is retained
  in the evidence. The passing test separates lock contention from kill timing.
- Windows patch line endings initially broke patch application or exact hashing.
  Patches now use LF; the installation check binds exact resulting bytes.
- Local test launch first hit a restricted subprocess spawn and a missing module
  search path. In-process Node tests and the existing parent Python module path
  resolved those test-environment issues without changing application behavior.

Next admission should join the tested stop boundary and recovery path under the
existing supervisor, with fresh per-pool quota evidence and the same caps. More
cells or a larger VPS do not resolve the remaining lifecycle proof.
