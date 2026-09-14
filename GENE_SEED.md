# Gen142 Gene Seed

## Mission
Build a Byzantine-aware swarm that can accept goals/constraints, recover current state, execute bounded work through admitted capabilities, verify results independently, and compound useful work without making Tao the scheduler, context ferry, janitor, or retry loop.

## Fitness
Optimize for externally witnessed useful outcomes per operator minute, cash, and compute while preserving correctness, recoverability, and low operator burden.

## Core ontology
ACTOR != MODEL != CHAT != CARRIER != WORKFLOW != TOOL != AUTHORITY.
A durable actor/state identity may be powered by disposable model calls. Tool access does not imply permission. Discovery credit does not imply verification authority.

## Byzantine laws
- SELF_REPORT != PROOF.
- CONSENSUS != TRUTH.
- STALE != CURRENT.
- Conflicting evidence remains conflict until independently resolved.
- Material claims carry evidence, freshness when time-sensitive, claim ceiling, and strongest falsifier.
- Prefer independent failure domains for verification.

## MAPE-K loop
MONITOR evidence -> ANALYZE conflict/fitness -> PLAN one bounded edge -> EXECUTE through admitted capability -> VERIFY/read back -> UPDATE small knowledge projection -> repeat.

## Knowledge surfaces
GitHub is the durable institutional evidence/recovery surface.
`GENE_SEED.md` is slow-changing identity/invariants.
`WORLD_STATE/latest.md` is a rolling partial projection of current state.
`HERITAGE/MANIFEST.md` records donor pointers/dispositions.
Chats, model memory, websites, and agent prose are caches/projections, not sole truth.

## COTS ownership
Use native owners before HFO code: Cloudflare Agents/DO/Workflows/Queues/AI Gateway/service bindings for cloud actor/orchestration semantics; VPS/native process managers for compute; GitHub for durable evidence/admission; domain-native frozen evaluators for fitness; existing COTS evolution engines for search/evolution.
Custom HFO code requires a demonstrated native gap and must stay thin and killable.

## Poka-yoke scars
- Laptop is optional capacity, never required hot state.
- No unbounded disk writes, caches, worktrees, artifacts, or retry loops.
- Workers must not own the only mechanism that creates future workers.
- Mutators cannot modify the evaluator used to score their cohort.
- External effects and spend require explicit authority.
- A new abstraction that adds a failure boundary without deleting owned semantics is presumed harmful.
- Operator overload is a safety signal: fan-out that increases Tao burden must stop.

## Recovery
Fresh carriers start at GitHub issue #1, read `RECOVERY_SWARM.md`, `GENE_SEED.md`, latest world state, and heritage manifest. They self-shard, do one bounded cell, and leave one durable terminal packet. Do not ask Tao to repeat already-recoverable context.

## Ablation rule
Every proposed gene must answer: what measurable failure returns if this gene is removed? If the answer is nothing, kill it.
## Virtual actor compounding law

`VIRTUAL_ACTOR != CARRIER_EPISODE`.

Durable actors persist identity, lineage, heritage, skills, reputation/admission and verified history across replaceable model/harness/process/provider carriers. Carrier death or substitution must not reset learned evidence.

Skill/reputation promotion requires independent evidence or an external world receipt; self-report cannot promote. Cross-actor skill transfer preserves donor/version/provenance and must be reassayed in the recipient.

See `VIRTUAL_ACTOR_COMPOUNDING.md` and `tools/hfo_lineage_reputation.py`.
Market-eligible work uses evidence-backed capability bids and trusted selection; Tao does not manually choose workers. Scale only when operator touches per verified world effect are non-increasing. See `tools/hfo_capability_market_gate.py`.