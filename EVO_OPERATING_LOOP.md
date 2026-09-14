# One measured evolution cell, supervised by Sigrun

Sequential notes/blocker cycles continue in [PDSA_NOTES.md](PDSA_NOTES.md).

Consumer: Sigrun's next packing campaign and the implementer closing PR4. The
objective is to automate the useful manual research/proposal/verification loop,
not maximize launches or spend. This is a reduced operating decision and measured
baseline, not a claim that the complete actor loop is deployed.

## Preserve the champions

There is an existing HSP6/N119 champion candidate. The original serialized radius
is **0.3099639323166259**, SHA256
`bc31e041f029b8b429f64fb688c0e06ce85e20680383a883b5b95b37d2e1efaf`.
A [distinct carrier replay](https://github.com/TTaoGaming/hfo-gen-140/issues/315#issuecomment-5626875404)
verified 119 containment and 7,021 pair constraints without importing the producer
checker. It reported approximately 0.125165% improvement over the then-observed
keeper row, while retaining currentness, format and backend-independence holds.

The current task fixture is a later normalized descendant with radius
**0.3099639332166260**, SHA256
`8ed8148be615d06c4bf37bf8fe5715248923486b93ab36d2d49b3d503b9da517`.
Its exact replay does not inherit independent approval of the ancestor's bytes.
No keeper acceptance, global optimum or fresh public-record claim is made here.
The recovered portfolio also records earlier N117/N118 contenders later overtaken;
the Kimi pilot is not a census of all previous champions.

Tao reports that Sigrun using GPT produced champions. Recover each original
proposal, model/session identity and verifier before assigning provider credit.
Use that successful workflow as the control; do not discard it because the new
automation is weaker. The recent Kimi pilot found no new champion.

## Smallest COTS ownership

| Job | Owner | Current ceiling |
|---|---|---|
| Durable Roach identity, task state, reservations | Existing Cloudflare Agent/DO | Pilot admission exists; account-wide races remain unproven |
| Campaign steps, waits, completion events | Existing Workflow | Native assay passed; complete scientific loop remains unjoined |
| Agent-internal recoverable work | Agents SDK fibers if needed | Upstream capability; not deployed for this cell |
| Parent selection, mutations, archive, lineage, viewer | ShinkaEvolve | Installed 0.0.7; bounded pilot ran; restart defect remains |
| Model latency/tokens/errors | AI Gateway for routed calls; native meter/DO receipts for Kimi | Not every vendor has a remaining-quota meter |
| CPU/memory/lifetime | systemd and existing sandbox runtime | Algorithm sandbox admission unfinished |
| Scientific truth | Frozen exact verifier + distinct acceptance | Never delegated to the proposal's own prose |
| Durable lessons and supervision | Existing GitHub receipts/Strife-Splendor schema | No second event bus or memory database |

Use [Shinka's existing WebUI](https://sakanaai.github.io/ShinkaEvolve/webui/) for
archive inspection and [AI Gateway observability](https://developers.cloudflare.com/ai-gateway/observability/)
for routed calls. Neither a cost estimate nor a graph enforces a shared budget.
The small receipt reducer below fills the current measurement gap without a new
dashboard service. Do not install another telemetry stack yet.

[Fibers](https://developers.cloudflare.com/agents/runtime/execution/durable-execution/)
checkpoint agent-internal work; Workflows own independent multi-step orchestration.
Neither automatically resolves an uncertain external model call. Preserve its
reservation, reconcile its receipt and never blindly replay it after recovery.
Do not nest a new retry loop around Shinka or introduce a second scheduler.

## One Larva ABI, composed loadouts

Retain `HATCHERY_LARVA_ABI.md`; do not create a competing ABI. A hatchery supplies
capacity, an adapter invokes a harness/model, a Roach is recoverable work identity,
and a Valkyrie persona is a versioned behavioral profile. Kimi supplies cognition;
Cloudflare hosts durable state. A model change must not reset work or quota.

Record loadout identity in the existing pinned manifest: callsign/persona digest,
research/proposal/verifier role, provider and returned model, harness version,
tool allowlist, prompt digest, input/evaluator digests, seed set and reservation.
Calls to every model/tool inside a research turn consume the same finite budget;
one agent turn is not necessarily one API request.

Start with three roles, not three new services:

- Researcher: gather sources and propose distinct mechanisms with falsifiable
  predictions. Desired bias: explore alternatives; risk: attractive but unusable ideas.
- Proposer: turn one hypothesis into an executable candidate and inspect feedback.
  Desired bias: finish experiments; risk: local optimization and premature confidence.
- Verifier: exact geometry, corruption controls and distinct acceptance.
  Desired bias: find counterexamples; risk: rejecting useful novelty too early.

Existing Valkyrie callsigns can carry these versioned profiles. Gunnr is this
implementation carrier, not evidence of a deployed Kimi persona. Do not invent
measured strengths from names. First hold persona/tools fixed and compare models;
then hold the model fixed and compare purposeful biases. Score an unadorned
control as well. Sigrun supervises objectives, budgets and promotion exceptions.

## The PDSA / MAPE-K loop

1. Monitor/recover: read champion, prior lesson, quota, unfinished work and current
   fence. Missing recovery evidence blocks that attempt, not all independent work.
2. Analyze/plan: choose a hypothesis and predicted effect. Research uses bounded
   web tools and records sources. Freeze the evaluator and experiment budget.
3. Execute: Shinka proposes, isolated VPS workers evaluate seeds, exact checker
   rejects invalid output. A failed hypothesis is useful evidence, not a champion.
4. Study: compare to the frozen parent and matched control; record runtime,
   quota, novelty, validity, failures and operator interventions.
5. Act/knowledge: retain result and Strife/Splendor; accept improvements only with
   the required verifier receipt. The existing Workflow may admit the next step
   only within its remaining reservation. Sigrun receives completion, a verified
   improvement, or an actionable failure; Tao does not relay individual tasks.

## Measure cycle time and takt separately

| Measure | Definition |
|---|---|
| Candidate cycle time | Reservation to durable verified disposition, including rejection; missing end stamp is censored/unknown |
| Lead time | Work eligible in queue to verified disposition |
| Phase time | Research, proposal, queue wait, evaluation, verification, persistence, recovery measured separately |
| Takt target | Available campaign time / desired verified dispositions; a planning target, not observed latency |
| Throughput | Verified dispositions per elapsed hour; report champions separately |
| Yield | Valid evaluated proposals / all dispatched proposals; include malformed and timed-out attempts |
| Champion efficiency | Verified fitness gain per quota unit, token and CPU time; unknown cost remains unknown |
| Reliability | Completed intended generations, recovery success, duplicate effects, operator interventions and blocked time |

Provisional next target: two verified dispositions in one hour, hence **30-minute
takt**. This does not promise two champions or authorize automatic hourly renewal.
Time to first champion remains right-censored if the campaign finds none. Use
median/tail latency only after enough complete samples; never silently omit failures.

Minimum correlation fields belong on existing logs/receipts: work, attempt,
generation, parent/candidate hash, loadout, phase, start/end UTC, monotonic elapsed,
outcome, quota observation/reservation, gateway call ID, verifier ACK and operator
intervention count. Use existing Trace Context/CloudEvents, no new envelope bus.

Historical measurement can be reproduced with:

```text
python hatchery/shinka-cell/telemetry.py hatchery/shinka-cell/PDSA_R1.json
```

`TELEMETRY_R1.json` is a snapshot of that reduction. The campaign lasted 218s;
four requests were dispatched, three returned, and only one non-baseline native
proposal has a complete evaluation receipt. The separate Kimi replay is excluded.
The two returned slots include Kimi at 85.940s and Gemini at 2.502s (including
admission overhead). End-to-end verified cycle times and human intervention
counts were not instrumented. We cannot claim a reliable throughput from this.

## Later adapters and loadout tournament

[Shinka](https://github.com/SakanaAI/ShinkaEvolve) already documents headless
Codex/Claude mutation adapters. Check the installed version's compatibility
before adopting them. [Headless](https://github.com/RobertTLange/headless-cli)
provides normalized usage output; its documented automatic paid fallback and
capacity retries require explicit disabling under this campaign's policy. Do not
adopt its scheduler; the existing Cloudflare owner remains the scheduler.

ChatGPT cloud conversations, requested Sol/xhigh or Astra/Pro sessions, and
Claude-produced artifacts can later enter as externally produced candidates.
They must carry artifact hashes, source-session provenance, requested/observed
model, tools, timestamps and known usage. Unknown usage remains unknown and the
same frozen verifier runs again. CLI support is not proof of browser/cloud-chat
harvesting or permission to invoke those accounts. These adapters are deferred.

Compare loadouts on matched parent/evaluator/seed sets and equal budgets, rotate
order, and keep invalid results and timeouts in the denominator. Retain a Pareto
set of gain, diversity, quota use, runtime and reliability; choose MOME only when
this produces enough genuine observations. One win does not establish a superior
persona/vendor, and pipeline failures must be separated from algorithm quality.

## Stability and the next implementation boundary

Current cell status: **bounded experimental prototype, not stable unattended
evolution**. Genuine wins: finite pilot, exact checking, ambiguous-call stop and
live quota reads. Open failures: unfinished generation recovery, isolated broader
algorithms, complete phase/ACK telemetry, shared-account race and stale-fence
assays. A successful bootstrap or quota probe does not close these failures.

Next implementation: close one interrupted generation using the existing archive
and retained provider receipt, then complete two consecutive verified generations
without Tao routing. Add the above timing fields to that same path. Preserve the
already specified campaign budget. Only then admit repeat campaigns and compare
more loadouts. Do not scale actor count or buy compute to mask recovery failure.
