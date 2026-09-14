# One small neurosymbolic cell

The unit to reproduce is a bounded **Shinka job plus a task package**, not a VPS
image full of new agent services. A VPS supplies capacity for that unit.

| Responsibility | Existing owner |
|---|---|
| Mutate, sample parents, evaluate, select, retain lineage | ShinkaEvolve 0.0.7 |
| Process lifetime, CPU, RAM, process and file limits | systemd |
| Five-call mission admission and replay protection | Existing Cloudflare Durable Object |
| Free-provider transport | Existing Cloudflare AI Gateway |
| Task truth | Frozen evaluator and immutable packing fixture |

MAPE-K names the same behavior: **Monitor** results and limits; **Analyze** fitness
and failure feedback; **Plan** a model-proposed recipe; **Execute** its permitted
scientific operations; **Knowledge** is Shinka's SQLite archive and immutable
results. PDSA is the experiment around that loop: freeze a hypothesis and budget,
run it, compare evidence, then retain or change the next configuration. These
names do not introduce another controller, database, scheduler or agent service.

## What can evolve

This first genome is a Python dictionary parsed with `ast.literal_eval`. It is
never imported or executed. It selects shell or full-center SciPy optimization,
noise, smoothing/target gain, seed and iteration count. The symbolic boundary
validates exact fields and numeric bounds, runs eight trials, and verifies all
119 containment and 7,021 pair constraints using rational arithmetic.

A task package contains its immutable input, evaluator, genome schema, initial
genome, budget and success condition. For packing the winner threshold is radius
strictly greater than `0.3099639332166260 + 1e-8`. Retaining the old champion is
valid but not a win. Other tasks need their own evaluator and effect boundary.

Cell/loadout evolution follows the same pattern: mutate declarative configuration
on an isolated candidate, then evaluate useful output, failures, resource use and
operator interventions against a frozen reliability test. Candidates cannot edit
their own evaluator, credentials, budget or promotion policy. No self-promotion.

## First measured PDSA — 2026-09-14

Operator budget: one cell, ten minutes maximum, at most two Kimi calls and three
free-provider calls total. No paid fallback and no provider retry. The stock
Shinka runner was configured for one proposal and one evaluation worker; embeddings,
meta recommendations and prompt evolution were disabled. Provider order was an
explicit pilot loadout: Kimi, Google, Groq, OpenRouter, Kimi. This is not an adaptive
vendor allocator or an admission to clone provider budgets.

The actual run dispatched one Kimi K3 call and three free-lane calls. Kimi,
Gemini and Groq returned matching model identities. OpenRouter reached a 95-second
transport deadline, leaving its provider outcome uncertain. The durable guard
stopped the mission without retry and refused the remaining Kimi call. The native
service then exited. The old `Restart=always` service remained stopped; this job
used `Restart=no` and a 600-second hard lifetime.

Native start/end were 01:50:44Z and 01:54:22Z: **218 seconds**. Time to winner is
unknown because this finite experiment found none. Raw measured evidence is in
[`hatchery/shinka-cell/PDSA_R1.json`](hatchery/shinka-cell/PDSA_R1.json).

Gemini's recipe completed eight trials with no improvement. Groq omitted Shinka's
required full-rewrite envelope, so it did not become a generation. Kimi produced
a valid full-center recipe, but the native run had no evaluation receipt for it;
a separate CPU-only replay with the unchanged evaluator completed eight trials
and retained the incumbent. The missing native receipt remains an integration
failure, not evidence that Kimi's proposal was bad. No winner or keeper submission.

The terminated service reported 17.752 CPU seconds and 219 MiB peak memory.
Buying a larger VPS would not fix the observed format/receipt failures. The
runner's displayed $0 cost for a local-compatible endpoint is not billing proof;
provider usage and the ambiguous OpenRouter request remain separate evidence.

## Reuse boundary and next experiment

This is a working bounded pilot, **not yet a reliable cloneable deployment**.
The next test must close the missing evaluator receipt, reject malformed proposal
envelopes without another model call, prove stop-on-winner, and recover the native
archive after interruption. Cross-cell account reservations are still unproven;
copying a VPS does not copy an allowance. Do not scale past one cell yet.

The winner stop branch uses an HTTP client that was not exercised by this no-win
run. An observation using urllib received 403 while curl worked; that branch
must be repaired and tested before a new mission. Bubblewrap was installed during
the code-execution feasibility check, but this data-only pilot did not need or
use it; no sandbox-execution claim is made.

Custom code is limited to the task-specific SciPy evaluator and a thin bounded
provider-admission adapter. Shinka's native dollar accounting reports unknown
local model prices as zero, so it cannot enforce the operator's per-provider
request allowance by itself. That measured gap justifies the adapter; it does
not justify a replacement evolution framework. The pilot adapter fixes one
mission id and cannot be reused to mint another allowance.

Implementation: `hatchery/shinka-cell/run.py`, `initial.py`, `evaluate.py`, and
`hatchery/pdsa-budget.mjs`. The current adapter is intentionally pilot-specific;
moving its mission binding into the existing admission owner is required before
this becomes a one-command reusable cell package.

References: [ShinkaEvolve](https://github.com/SakanaAI/ShinkaEvolve) and
[Cloudflare Agent Workflows](https://developers.cloudflare.com/agents/runtime/execution/run-workflows/).
