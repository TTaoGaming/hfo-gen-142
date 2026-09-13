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

## Public/private rule

The public Gen142 repo contains sanitized reductions only. For private heritage, publish the lesson, age band, immutable content hash/opaque evidence ID, confidence, and disposition without leaking private repo names/content or secrets. Full private source lookup belongs to an authorized private index/hot state.
