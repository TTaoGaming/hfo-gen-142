# Gen142 Zerg Capacity Archetypes

These are engineering archetypes and coordination semantics. They are not fictional authority and they are not automatically A2A agents.

Hard law:

`ARCHETYPE != ACTOR != AGENT_CARD != SKILL != TOOL != AUTHORITY`

## Canonical archetypes

| Archetype | Engineering meaning | Default representation | Durable owner | A2A card by default? |
|---|---|---|---|---|
| LARVA | uncommitted compatible capacity before work selection | Gateway state + admission procedure | none; disposable carrier | No |
| LING | bounded gather/discovery phenotype | Agent Skill / workload phenotype | current carrier | No |
| TWINLING | paired gatherer/falsifier formation | `twinling-pdsa` Skill + paired evidence | current carriers + GitHub receipts | No |
| ROACH | recoverable continuation/fan-in lineage | `roach-fanin` Skill + Burrow checkpoint | Cloudflare Agent/DO when admitted; GitHub shadow until then | Only if actually served |
| RED_QUEEN | hostile falsifier / adversarial pressure | Skill / evaluator role | current carrier or admitted verifier actor | No by default |
| REDUCER | fan-in, dedupe, canonical compression | Skill + reducer workload | durable actor/workflow if admitted | Only if actually served |
| VERIFIER | independent correctness/currentness boundary | Skill + frozen assay/evaluator | distinct failure domain where possible | Only if actually served |
| EXTRACTOR | resource/current-state sensing | Skill + native telemetry/tools | native telemetry owner | No by default |
| QUEEN | match admitted demand to eligible capacity | thin policy over native workflow/queue/runtime | Cloudflare Agent/Workflow or other native owner if needed | Only if served as a durable service |
| HATCHERY | launch/admission/replacement mechanism | platform workflow/scheduler, Gateway contract | native platform | No |
| OVERLORD | observation/current-state projection, not effect authority | OTel/Trace Context + world-state reducer | telemetry/projection owners | No by default |
| BURROW | durable responsibility/state slot for a Roach | Cloudflare Agent/DO state; GitHub shadow/receipt | Cloudflare Agent/DO after assay | No; topology/state is not identity |
| EVOLUTION_CHAMBER | QD/MOME mutate/evaluate/select mechanisms | COTS evolution engine + frozen evaluator + behavior archive + per-niche Pareto reducer | COTS engine/workflow | No |
| HIVE | integrated organism / control loop | composition of Gateway, actors, skills, tools, evidence, reducers | multiple native owners | One card only if an actual Hive gateway/service endpoint exists |

## Larva law

A fresh carrier is **not work** and is **not an actor**.

`AVAILABLE_CAPACITY != WORK_DEMAND`

Larva sequence:

`RECOVER -> SELECT_EXISTING_WORKLOAD -> CHECK_CAPABILITY -> CHECK_AUTHORITY -> MORPH`

It must not invent tasks just to use quota or compute.

## Morph law

Morphology is demand- and evidence-driven, never provider-brand-driven.

Examples:
- missing evidence -> LING / Twinling Gatherer;
- attractive unchallenged claim -> Twinling Falsifier / RED_QUEEN;
- stranded durable work -> ROACH;
- terminal population waiting for fan-in -> REDUCER;
- correctness or freshness boundary -> VERIFIER;
- resource/currentness uncertainty -> EXTRACTOR;
- multiple eligible carriers for admitted demand -> QUEEN policy may become relevant.

## QD / MOME exploration law

The evolution chamber has three distinct phases:

`EXPLORE -> DEVELOP -> SEND`

- **EXPLORE:** maximize behavior-space coverage and measured novelty. Maintain islands/niches. There is no global champion and no global primary.
- **DEVELOP:** spend more budget on measured elites **within multiple niches** while preserving the archive and independent falsifiers.
- **SEND:** only after an explicit phase transition, choose protocol-complete package(s) for external submission. Global convergence is legal here, not before.

A `MOME champion` is a nondominated elite inside a behavior cell. The archive itself is the product of exploration; one scalar routing score may not erase orthogonal niches. Exact-cell crowding beyond the admitted producer/falsifier or elite budget forces the next carrier to morph.

Canonical donor patterns to assimilate without importing authority:
- isolated islands, archive inspirations, crowding replacement, bounded migration, stagnation-triggered new islands;
- archive / emitter / scheduler separation and novelty/local competition;
- Pareto-efficient proposal selection from full execution traces;
- a bounded Pareto front inside each behavior cell.

The frozen benchmark/verifier remains authoritative for fitness. QD preserves diversity; it does not preserve invalid candidates.

## A2A projection law

A2A describes a **served agent**, not every internal phenotype.

When a durable endpoint is real and admitted, its Agent Card may truthfully expose a small set of skills/capabilities that are current for that runtime. Internal morphology may change without minting a new identity/card each time.

For example, one durable Sigrun/Hive actor may expose skills such as:
- bounded PDSA investigation;
- evidence-bound falsification;
- durable fan-in/recovery;
- heritage reduction;
- world-state reduction.

Whether those are separate Agent Skills should be decided by progressive-disclosure value and held-out activation traces, not by the Zerg vocabulary alone.

## Authority law

None of these imply effect permission.

- Role does not grant authority.
- Skill load does not grant authority.
- Tool visibility does not grant authority.
- Agent Card advertisement does not grant authority.
- Durable actor identity does not grant arbitrary authority.

Every protected effect still requires the current admitted effect ceiling/reference monitor.

## Fitness

An archetype survives only if it changes behavior at a useful fork and reduces measurable failure/operator burden.

Ablation question:

> What measurable failure returns if this archetype/contract is removed?

If no distinct failure returns and an upstream/native owner already covers the behavior, fold or kill the archetype rather than growing the Hive vocabulary.
