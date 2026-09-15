# HIVE META LOOP v1

UTC checkpoint: `2026-09-15T22:01:53Z`
Authority: public semantic/recovery contract only. Runtime authority still comes from authenticated controller state + verifier receipts.

## Purpose
HIVE is the **meta evolutionary search loop** for HFO. It is not an evolutionary engine, model, vendor, scheduler, or worker archetype. Engines such as Shinka Evolve, OpenEvolve, GEPA, AFlow, MAP-Elites, etc. may occupy the **Evolve** stage as interchangeable search operators.

Historical donor/root: Gen101 already implemented HIVE8 as a hierarchical POMDP with durable trail state and `HINDSIGHT -> INSIGHT -> VALIDATED_FORESIGHT -> EVOLVE -> HINDSIGHT+1`, with belief state = trail and observation = rehydrated context. Current Gen142 retains that mathematics but updates the stage semantics around donor mining, cross-domain transformation, deterministic validation, and bounded evolution.

## Strategic phases
| Phase | Port pair | Gen142 meaning | Required output |
|---|---|---|---|
| **H — Hindsight** | P0 OBSERVE + P7 NAVIGATE | Recover **all relevant past evidence**: current state, heritage, prior failures, benchmark incumbents, public exemplars, best-known architectures, external research, previous champions, and reverse-engineered donor genes. Prefer lawful public/COTS exemplars over invention. | `donor_pack.v1` with provenance, evidence URLs/SHAs, failure scars, incumbents, and extractable genes |
| **I — Insight** | P1 BRIDGE + P6 ASSIMILATE | Transform the present by **cross-domain translation and composition**. Bridge donor genes into the current problem through compatible interfaces: e.g. hexagonal architecture, strangler fig, actor model, evolutionary search, control theory, optimization, formal verification. Insight is not brainstorming; every transformation must name source donor -> target abstraction -> expected mechanism. | `transformation_graph.v1` / DAG of candidate compositions with explicit interfaces and hypotheses |
| **V — Validated Foresight** | P4 DISRUPT + P5 IMMUNIZE | Turn hypotheses into **falsifiable forward claims**. Freeze evaluator, constraints, authority envelope, budget, stop conditions, and independent verifier. Red-team before scale. Results are evidence, not vibes. Promotion requires reproducible measurements/receipts; no self-awarded success. | `validation_envelope.v1`: tests, evaluator, baselines, thresholds, falsifiers, verifier identity, receipts, confidence |
| **E — Evolve** | P2 SHAPE + P3 INJECT | Execute bounded search using the validated envelope. Mutate/recombine/select among candidate artifacts; preserve lineage, novelty and failure scars. Evolution engines are replaceable plugins here. Success/failure yields durable receipts that become the next cycle's Hindsight. | `evolution_manifest.v1` + lineage + measured fitness + champion/kill/park decisions + ConsumerAck |

## Formal model
Let `D_t` be durable evidence at cycle `t`; `C_t` the current problem/context; `A_t` the authority/budget envelope.

- `H_t = R(D_<=t, C_t)` — retrieve, reverse-engineer, deduplicate and provenance-bind donor evidence.
- `I_t = T(H_t, C_t)` — cross-domain transformation/composition into candidate mechanisms.
- `V_t = G(I_t, A_t)` — adversarial validation; freeze evaluator and reject unsupported foresight.
- `E_t = S(V_t)` — bounded evolutionary/search operator under the frozen validation envelope.
- `D_{t+1} = D_t U receipts(E_t)` — only measured receipts/lineage update durable belief.
- Then `H_{t+1} = R(D_<=t+1, C_{t+1})`.

Per-generation execution should be represented as a **DAG** rather than an ambiguous runtime cycle:

`Sources -> Hindsight donor extraction -> Insight transformation DAG -> Validated Foresight gates -> Evolve/search branches -> Independent Verify/ConsumerAck -> Durable receipts`

The **strange loop exists across versions**, via the temporal edge `receipts(E_t) -> H_{t+1}`. This keeps each generation acyclic/replayable while allowing recursive self-improvement over time.

## HIVE DAG invariants
1. **No Hindsight bypass**: do not mutate before recovering incumbents, donors, heritage, and prior scars.
2. **No Insight without provenance**: every cross-domain transform names its donor(s) and interface.
3. **No evolution on vibes**: Validated Foresight freezes metric/evaluator/constraints before expensive search.
4. **Producer != verifier**: a distinct verifier owns final promotion evidence.
5. **EMIT != ACCEPT != CLAIM != ASSIGN != EXECUTE != VERIFY != SUCCESS**.
6. **Public observation is Byzantine**: GitHub/web evidence is input; authenticated runtime state/receipts decide authority.
7. **Failure is genetic material**: identical failure fingerprints are deduped and retained as repulsors; do not blind-retry.
8. **Evolution engine is subordinate**: Shinka/OpenEvolve/GEPA/etc. cannot redefine mission, authority, evaluator, or success semantics.
9. **Candidate heritage requires verifier PASS + downstream ConsumerAck** before reuse as an admitted gene/skill.
10. **TAO_HOT_LOOP_ACTIONS target=0**: Tao sets mission/authority boundaries; HIVE should own research -> transform -> validate -> evolve -> reconcile.

## Tactical nesting
Historical HIVE8 nested PREY8 inside each strategic stage:
`PERCEIVE -> REACT -> EXECUTE -> YIELD`.
Gen142 may use WorkCells/ForcePackages instead, but the semantic mapping remains useful: every strategic phase must perceive current receipts, decide under its contract, execute bounded work, and yield durable state.

## Engine placement
Examples, not mandates:
- **Shinka Evolve / OpenEvolve**: executable-code population search inside E.
- **GEPA / DSPy optimizers**: prompt/policy/workflow mutation inside E.
- **AFlow / architecture search**: workflow/graph candidate generator, normally I -> E only after V freezes evaluation.
- **MAP-Elites / MOME**: archive/selection strategy inside E.
- **LLM carriers**: semantic mutation/research operators; never the source of truth.

## Gen142 operating rule
Every new mission or crown lane SHOULD begin with a HIVE packet, even if stages are tiny:

`H: donor_pack -> I: transformation_graph -> V: validation_envelope -> E: bounded evolution -> verifier -> receipts -> H+1`

Do not create a new control plane to implement HIVE. Express these as versioned artifacts/ForcePackage metadata on the existing Sigrun + WorkCell surfaces.

## Historical provenance
- `TTaoGaming/hfo_dev_2026_4/HFO_GEN_101_FORGE/alpha_infrastructure/hive8_loop.py` — h-POMDP implementation and H/I/V/E phase directives.
- `TTaoGaming/hfo_dev_2026_4/HFO_GEN_101_FORGE/alpha_infrastructure/hive8_prey8_registry.py` — phase enum/registry.
- `TTaoGaming/hfo_dev_2026_4/docs/topology/F6_mermaid_hive_prey_cycle.md` — HIVE8/PREY8 topology and H->I->V->E->H+1 strange-loop view.
- `TTaoGaming/hfo_dev_2026_4/PIT_OF_SUCCESS.md` — canonical older phase-to-port mapping.

`HIVE_META_LOOP=HINDSIGHT__INSIGHT__VALIDATED_FORESIGHT__EVOLVE`
`MODEL=H_POMDP_PLUS_VERSIONED_DAG`
`EVOLUTION_ENGINE=PLUGIN_NOT_GOVERNOR`
`SUCCESS=VERIFIED_RECEIPT_NOT_NARRATIVE`
