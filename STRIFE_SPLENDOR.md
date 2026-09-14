# STRIFE / SPLENDOR Heritage Reduction

Gen142 reduces two years of heritage into two top-level evidence classes before deciding what becomes canon.

## STRIFE

A Strife item records pain with evidence. Examples: disk exhaustion, duplicate effects, broken regeneration, context loss, false autonomy claims, stale credentials, operator CPR, branch/repo sprawl, self-verification, missing retirement, evaluator drift, or a control plane that added more failure boundaries than value.

A useful Strife record answers:
1. What happened?
2. What assumption failed?
3. What evidence proves it happened?
4. What harm/operator burden resulted?
5. What guard would have prevented or contained it?
6. What measurable failure returns if that guard is removed?

## SPLENDOR

A Splendor item records something that actually worked under stated conditions. Examples: independent replay, durable restart, accepted external result, bounded cleanup with readback, successful recovery by a fresh carrier, proven native COTS ownership, a guard that blocked a hostile case, or a capability that produced verified useful work.

A useful Splendor record answers:
1. What worked?
2. Under what exact conditions?
3. What evidence independently supports it?
4. What consumer used it?
5. Did it survive restart, transfer, or held-out use?
6. What breaks if the mechanism is removed?

## Promotion ladder

`OBSERVED -> SOURCED -> FALSIFIED -> CORROBORATED -> CONSUMED -> ADOPTED`

STRIFE and SPLENDOR can both yield genes. A failure may yield a safety invariant; a success may yield a reusable mechanism. Neither is promoted by narrative importance, model agreement, age, or sentiment.

## Heritage age bands for recovery waves

- **RECENT:** Gen137-140 and 2026-08/09 operational work. High currentness, high risk of local overfitting.
- **MIDDLE:** Gen130-136 and 2026-05/08 lineage. Strong identity/memory/skills ancestry; must be revalidated against current COTS owners.
- **DEEP:** Gen89-129, 2025 repositories, early Hive Fleet / Swarmlord / MAPE-K lineage. Mine for recurring scars and rediscovered laws; do not import old infrastructure literally.

Reducers should prefer a law that appears independently across age bands only when the underlying failures/evidence are genuinely distinct. Repetition within one copied lineage is not independent proof.

## Work-cell cycle — 2026-09-14

Consumer: the next admitted Hatchery/Larva workload and its supervisor.
Evidence: [WORK_CELL_R1.json](hatchery/shinka-cell/WORK_CELL_R1.json).

- **Strife: available quota did not imply timely Kimi completion.** The first
  request exceeded the existing 90-second transport bound. Its reservation stayed
  spent/uncertain and no inference retry occurred. Shinka nevertheless waited
  for an unavailable next proposal and attempted one futile process replacement.
  Cure: terminate the owned caller on a handoff error, close the native job as
  rejected, and exclude exit 78 from systemd restart. A network-disabled native
  falsifier now exercises that actual supervisor path and proves child cleanup.
- **Strife: an entire system message was mistaken for immutable context.**
  Shinka randomly selects rewrite-format suffixes. After successful checkpoint
  recovery, the changed suffix correctly triggered the overly broad hash guard.
  Cure: pin the task prefix in the manifest and preserve the varying suffix as
  another system message in the bounded delta. Two format variants replay the
  exact fixed prefix while preserving every instruction byte and role.
- **Strife: Workflow completion is not result acceptance.** A rejected result
  also yields a completed native Workflow. The supervisor now checks the nested
  acceptance verdict and result hash; an actual native-process fixture with a
  completed-but-rejected result exits 78 and closes once.
- **Splendor: one finite input-driven cell closed two generations.** Native
  systemd replaced a killed caller; installed Shinka recovered its accepted
  checkpoint; two distinct eight-trial recipes reached separate Cloudflare exact
  geometry checks and native Workflow acceptance in 29.01 seconds. There were
  zero model calls and zero operator interventions during this repaired run.
  Both artifacts retained the incumbent. This proves a bounded work-cell
  primitive, not a champion, overnight neural evolution or general multi-host ABI
  conformance. Keep one active writer and preserve the unproven boundaries.

## Public/private rule

The public Gen142 repo contains sanitized reductions only. For private heritage, publish the lesson, age band, immutable content hash/opaque evidence ID, confidence, and disposition without leaking private repo names/content or secrets. Full private source lookup belongs to an authorized private index/hot state.
