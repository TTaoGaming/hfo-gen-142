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
| Parent selection, mutations, archive, lineage, viewer | ShinkaEvolve | Installed 0.0.7 with opt-in accepted-proposal recovery; installed-package fixture passed, unattended live recovery unproven |
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
evolution**. The Oracle recovery patch is installed and its cached-response
two-generation assay passed. Local native workerd cancellation passed; hosted
cancellation remains outstanding. See `hatchery/shinka-cell/INSTALL_R1.json` and
`RECOVERY_GOAL_R1.md`. These do not prove automatic production restart, useful
live adaptation, algorithm isolation or shared-account fencing.

## Overnight mission proposal — 2026-09-14

Status: **PLAN ONLY; no new admission, provider calls, scheduler or runtime change**.
Decision record within PR4, based on source revision
`12436c52a32b7ead9e8c6f507475d0fcaa030d51`. Hindsight/insight are complete enough
to select the next experiment; implementation, joined validation and integration
remain open. Consumer and integrator: Sigrun's next expressly launched mission.
The trigger is not installed by this plan.

The desired outcome is a finite overnight search that produces retrievable,
verified experiments and preserves any improvement without routine Tao routing.
Eight hours is the planning window, not permission to extend an existing cap or
renew allowances. Budget exhaustion can end it sooner. A champion is a desired
scientific outcome, not a promised completion criterion.

### Diagnosis from current code

- `pdsa-budget.mjs` is a specific expired pilot: fixed work ID, five hard-coded
  vendor slots, ten-minute deadline, and any provider error stops the mission.
  Relabelling it or repeatedly resetting it cannot admit an overnight campaign.
- `run.py` permits a six-field dictionary selecting `shell` or `full`. It cannot
  invent a new search algorithm. Six total generations include the baseline.
- `evaluate.py` always starts from one hash-pinned `parent.pck`. Recipe evolution
  is possible, but discovered geometry does not automatically become the next
  parent. The evaluator currently stops the mission when it finds an improvement.
- `combined_score` retains the incumbent for every non-improving proposal. This
  removes much of the feedback needed to distinguish failed approaches. Detailed
  diagnostics exist, but their consumption by the next proposer is unverified.
- Replacement is currently demonstrated by the test harness. The production
  Cloudflare-to-carrier restart and completion path has not passed the joined test.

Observed conclusion: the deployed/tested pieces are not yet an overnight cell.
Inference to test: flat feedback and restricted mutations can explain weak search
even when transport works. They do not establish that Kimi is an inferior model.
Falsifier: matched manual/automated experiments using the same kernel, input,
feedback and resource bounds show no meaningful difference in valid outcomes.

### Smallest composition

Build decisions: CONFIGURE_INCUMBENT, THIN_ADAPTER, ADMISSION_HARNESS.
Keep the Hatchery/Larva ABI, one Cloudflare actor/Workflow, Shinka, native systemd
limits, existing artifact storage and fixed exact verifier. No new orchestrator,
queue, dashboard or persona framework is needed for this mission.

| Responsibility | Proposed binding | Bedtime evidence |
|---|---|---|
| Mission, admission, one authoritative continuation | Existing Cloudflare DO/Workflow | Same work and budget survive caller loss; stop/expiry blocks dispatch |
| Search and same-host process recovery | One Oracle Shinka cell under existing native supervisor | Complete process group stopped before one bounded replacement; no laptop launcher |
| Proposals | Kimi plus a freshly verified alternate | Known task format, fresh pool evidence, all requests share the admitted ledger |
| Geometry acceptance | Fixed checker; OVH verifier if its current route is proved | Exact candidate bytes verified outside candidate execution and acknowledged durably |
| Morning result | Existing artifacts, receipts and telemetry reducer | Report retrievable with caller gone; true failures and unknowns retained |

For the first night there is one search writer. OVH verification is not permission
to run a second independent proposer against the same account or archive. A
same-host verifier is an explicit lower-assurance option, not a distinct carrier
claim. Cross-host failover stays disabled until fencing is tested.

Workflow retry configuration must be explicit: Cloudflare documents default
step retries. A durable wake is not authorization to repeat inference. Reserve
before dispatch, retain uncertain reservations, and reconcile before proceeding.
Use the existing Workflow for logical continuation and systemd for process
containment; neither may independently restart the same logical attempt.
Reference: https://developers.cloudflare.com/workflows/build/sleeping-and-retrying/

### Make the scientific loop useful

Recover and reproduce one actual champion-producing manual workflow as the
control. Keep its algorithm, starting artifact and measured result available;
do not compare open-ended manual algorithm design to automated parameter tuning
and call that a model-quality test.

First-night search should use trusted, reviewed kernels with distinct hypotheses,
bounded seed trials and a matched control. Kimi spends calls on proposing or
revising hypotheses; CPU trials do not each require a new inference call. The
next proposal must receive the prior verified result and useful failure metrics.
Deduplicate the canonical recipe together with parent, evaluator and seed set.
An additional seed is a replication, not a new algorithm.

Keep exact valid radius as the championship criterion. Feasibility residuals,
search progress and diversity may guide exploration in separate diagnostics;
none may substitute for valid geometry or inflate a champion score. Failed
experiments should state what was tested and what their measured outcome rules
out, rather than merely emitting another retained-incumbent PASS.

For compounding improvements, the controller must select a verified artifact as
the next immutable parent and bind its hash in a new admitted generation. Do not
overwrite `parent.pck` under an existing checkpoint or weaken its hash guard.
Separate campaign-best retention from the choice of diverse next-search parents.
If this transition is not implemented, label the first night as fixed-parent
multistart search and stop on the first verified improvement as currently defined.

Open-ended generated algorithm execution requires the already planned isolated
candidate capability and its rejection tests. It is a separate readiness target.
Do not silently call the current two-kernel parameter search unrestricted MOME
or claim that personas/web access alone widen its executable search space.

### Budget, cadence and overnight dispositions

Fresh admission must bind the mission, deadline, allowed models, source/input/
verifier hashes, existing request/USD/quota/resource ceilings, reserve floor and
stop policy. Preserve every smaller existing cap; no paid fallback, implicit
reset, provider retry loop or allowance multiplication across VPSs. The proposed
overnight window itself grants no calls. Unknown quota is not free capacity.

Cadence is completion-driven: finish evaluation and verification, persist the
result, then admit the next eligible experiment. Kimi need not be called every
minute. Derive the desired number of verified experiments from a live calibration
and the admitted budget, not from the 59-second cached-response test. If the
available budget supports only a short run, disclose that before launch; do not
pad eight hours with duplicate tests or silently replenish it. Predeclared CPU
work may continue after model budget exhaustion only within its own admission.

| Event | Proposed first-night disposition |
|---|---|
| Malformed or invalid candidate | Record rejection; consume its actual call allowance; next distinct admitted experiment may proceed |
| Known provider refusal | Disable that lane for the campaign; use only an already admitted alternate with remaining capacity |
| Uncertain model outcome | Retain reservation and stop new model dispatch; no blind retry or refund; independently admitted CPU work may finish |
| Caller loss after accepted checkpoint | Supervisor terminates the whole owned process group; one bounded same-host replacement uses that checkpoint |
| Missing checkpoint, hash mismatch, ownership uncertainty | Stop affected work and preserve evidence |
| New verified best | Preserve artifact and verifier receipt; continue only if verified-parent continuation was admitted and tested; otherwise stop-on-win |
| Deadline, resource/quota reserve or output limit reached | Stop admission, settle/retain pending state, terminate owned work within limits, produce terminal report |
| No admitted work left | End or sleep until an already authorized event; do not invent work, renew budget or poll identical errors |

### Bedtime acceptance and implementation order

1. Join the current Cloudflare admission/cancellation and Oracle installed
   recovery path. The first delivery is one real model proposal, numerical
   evaluation, separate verifier receipt and durable terminal disposition.
   Recover the existing carrier binding rather than introduce a second launcher.
2. Complete two genuine live feedback generations within fresh admission. The
   second consumes the first result; cached responses, baseline rows and duplicate
   experiments do not count. Measure phase times and operator interventions.
3. Inject caller interruption, invalid output, duplicate delivery, provider
   failure and exhausted admission on that same deployed route. Safe deterministic
   fixtures may test destructive error branches without spending more model calls.
   Prove no repeated uncertain effects and no acceptance of stale or invalid work.
4. Disconnect the laptop and run a proposed 60-90 minute supervised soak within
   approved bounds. Any routine manual restart, repair, approval or context ferry
   fails the autonomy criterion. A safe early stop proves containment, not useful
   operation for the entire soak. Require stable forward progress as well.
5. Freeze the night manifest, exact deadline and remaining budget. Launch once
   only after the prior evidence passes. Keep the existing process/resource limits
   and one search writer. Morning report must survive laptop/caller loss.

Suggested engineering checkpoint: after the first focused implementation block,
show a joined live verified disposition, not more independent readiness demos.
If that cannot be shown, the precise remaining edge determines the next block.
Useful overnight readiness is better estimated as several focused engineering
hours plus a soak than promised in 30-60 minutes. This is an estimate; no launch
date follows from this planning record. Do not buy compute until measurements
show queued admitted evaluations waiting on saturated CPU or memory.

Morning output: starting/ending best artifact hashes and valid radii, number of
distinct hypotheses and seed replications, verified dispositions and failures,
gain or no gain, calls/known usage by pool, phase/cycle times, recovery events,
operator interventions, exact stop reason, and one next scientific experiment.
Heartbeat-only success is excluded. No champion is an honest result; no verified
experiments is a failed usefulness test. With zero champions, time-to-first-win
is censored and cost per champion is undefined, not zero.
