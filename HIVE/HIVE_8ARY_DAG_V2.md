# HIVE 8-ARY DOUBLE-DIAMOND DAG v2

UTC checkpoint: `2026-09-15`
Status: canonical semantic/recovery contract for Gen142 HIVE geometry.
Supersedes the flattened interpretation of `HIVE_META_LOOP_V1`; preserves the historical HIVE8/PREY8 h-POMDP roots.

## Core correction
HIVE is **not** a four-step sequential workflow. It is an **8-ary recursive double-diamond / hourglass search geometry** operated by a heterogeneous ecology of MOME champions.

The invariant strategic phases remain:

`HINDSIGHT -> INSIGHT -> VALIDATED_FORESIGHT -> EVOLVE -> HINDSIGHT+1`

But their geometry is:

- **Hindsight = fan-out / divergence**
- **Insight = fan-in / convergence**
- **Validated Foresight = fan-out / divergence**
- **Evolve = fan-in / convergence**

The atomic geometric primitive inherited from older HFO is the scatter-gather diamond `1 -> 8 -> 1`. HIVE recursively composes that primitive at `8^N` scale.

## 8-ary schedule code
Represent one HIVE generation by an exponent tuple

`HIVE[h i v e]`

with phase widths

`W_H = 8^h`, `W_I = 8^i`, `W_V = 8^v`, `W_E = 8^e`.

Example requested by operator:

`HIVE[2120] = 64 Hindsight -> 8 Insight -> 64 Validated-Foresight -> 1 Evolve execution champion`

So the information geometry is:

`1 -> 64 -> 8 -> 64 -> 1`

This is the canonical double diamond: diverge, converge, diverge, converge.

Allowed degradation preserves powers of eight and phase semantics. A sequential emergency mode is `HIVE[0000] = 1 -> 1 -> 1 -> 1`; a minimal swarm diamond is `HIVE[1010] = 8 -> 1 -> 8 -> 1`. Do not choose arbitrary widths such as 5, 17, or 31. If capacity is insufficient, reduce an exponent rather than breaking the 8-ary topology.

Normal topology constraints are `h > i` and `v > e` for real divergence/convergence. The archive/ecology size itself is not constrained to a power of eight; only execution-layer fan-out/fan-in geometry is.

## Phase semantics
### H — Hindsight / 8^h fan-out
Purpose: expose the past and the true incumbent landscape before invention.

Hindsight workers independently recover and reverse-engineer:
- prior attempts, failures, scars, champions, heritage, receipts;
- public incumbents and battlefields;
- best-known architectures and exemplars;
- lawful public/COTS implementations;
- cross-industry donor genes;
- hidden assumptions, constraints and prior-art failure modes.

This is not generic research. Each H node emits provenance-bound donor genes and falsifiable observations.

Output: a wide `donor_population` / `donor_pack` with lineage and evidence.

### I — Insight / 8^i fan-in
Purpose: compress many donors into a smaller number of structurally meaningful transformations.

Insight is a bridge operation, not summary. It creates typed cross-domain mappings such as:
- donor architecture -> target ABI;
- control-theory pattern -> actor/reconciler interface;
- hexagonal/ports-and-adapters -> provider-neutral carrier boundary;
- evolutionary operator -> target search surface;
- formal method -> executable invariant;
- one domain's elite mechanism -> another domain's compatible slot.

Each Insight node should gather a partition of H nodes and emit a transformation sub-DAG:

`donor(s) -> abstraction -> interface -> hypothesized mechanism -> target artifact`

Output: `transformation_graph` / candidate mechanism families.

### V — Validated Foresight / 8^v fan-out
Purpose: explode each Insight family into **alternate futures** and kill unsupported futures before expensive evolution.

V fans out into independent experiments, falsifiers, red teams, counterfactuals, canaries, verifier paths and scenario branches. Each future branch freezes:
- baseline/incumbent;
- evaluator and protocol;
- authority/effect ceiling;
- budget and stop condition;
- reproducibility contract;
- independent verifier identity;
- success/failure thresholds.

Validated Foresight is where the system earns permission to believe a future. A narrative forecast has zero promotion authority.

Output: a population of `validation_envelope` branches with posterior evidence and typed failure fingerprints.

### E — Evolve / 8^e fan-in
Purpose: turn the validated future population into measured elites, not merely mutations.

E may use Shinka Evolve, OpenEvolve, GEPA, AFlow, MAP-Elites/MOME, custom search, or other search operators, but those engines are subordinate plugins.

E performs bounded mutation/recombination/selection under the frozen V envelopes. It collapses execution toward one or a few admitted champions while preserving the wider non-dominated archive.

Important distinction:
- `execution_champion`: the artifact(s) admitted for the next action;
- `MOME_archive`: the persistent ecology of non-dominated elites and niches.

Therefore `HIVE[2120]` may emit one execution champion while retaining many MOME champions for future recombination. `HIVE[2121]` can explicitly emit eight execution champions while keeping the same 64->8->64 double-diamond body.

Output: measured lineage, Pareto/MOME archive, champion/kill/park decisions, verifier receipts and ConsumerAck.

## MOME / Pareto formalism
Let each candidate artifact `x` have:
- behavioral/niche descriptor `b(x)`;
- objective vector `f(x) = [f1(x), ..., fm(x)]`;
- provenance/lineage `g(x)`;
- temporal horizon `tau(x)`;
- scenario/counterfactual id `omega(x)`;
- evidence/receipt set `r(x)`.

Candidate `x` Pareto-dominates `y` when it is no worse on all normalized objectives and strictly better on at least one. HIVE should maintain a non-dominated archive per niche rather than collapsing all fitness to one scalar prematurely.

`A_t[b] = ND({x : b(x)=b})`

The actor ecology can therefore contain arbitrary numbers of champions even though execution widths are powers of eight.

Current known ecology includes operator-described **8 APEX + 32 Valkyrie virtual-actor champions**, plus evolving donor families encoded by HFO handles such as Zerg, Tyranid and Sliver. Treat these as genotype/archetype donor families, not vendor/model identities. Crossbreeding means recombination of admitted behavioral/capability genes under V-stage verification; mythology does not grant authority.

## Higher-dimensional hourglass / Pareto lens
HIVE's intended product is not merely a winner. It is a navigable Pareto lens over four coupled domains:

1. **Past** — historical receipts, failed paths, donors, previous elites.
2. **Present** — reconciled current belief/state and active constraints.
3. **Future** — experimentally supported predicted outcomes.
4. **Alternate futures** — mutually exclusive or competing scenario branches and evolved candidates.

Represent an archive item as a point in an augmented state space:

`z = (artifact, niche, objective_vector, time_horizon, scenario, provenance, confidence, receipts)`.

The higher-dimensional HIVE archive is then a set of non-dominated points indexed by niche, time and scenario. Different projections of that archive answer different owner questions: cheapest path, fastest crown, safest architecture, highest buyer value, best long-run lineage, strongest verifier confidence, etc.

This is the practical meaning of the "higher-dimensional hourglass": fan-out increases diversity/entropy and exposes alternate histories/futures; fan-in compresses them into sufficient structures/elites **without deleting the archive that made the decision possible**.

## h-POMDP interpretation
Historical HIVE8 already modeled the outer loop as a hierarchical POMDP. Preserve that:

- latent world state: `s_t`;
- durable evidence: `D_<=t`;
- belief: `B_t = P(s_t | D_<=t)`;
- Hindsight obtains diverse observations/donors;
- Insight constructs latent transformation hypotheses;
- Validated Foresight runs experiments and Bayesian/falsification updates;
- Evolve searches under the updated belief and frozen constraints;
- receipts from E become observations for `H_{t+1}`.

No LLM owns the belief state. Durable receipts do.

## DAG semantics
One generation MUST be representable as an acyclic graph:

`ROOT -> H[8^h] -> I[8^i] -> V[8^v] -> E[8^e] -> VERIFY -> CONSUMER_ACK -> RECEIPTS`

Edges may be many-to-many, but fan-in reducers must identify which parents they consumed. Every node carries lineage and provenance. The recursive/strange-loop edge is temporal only:

`RECEIPTS_t -> H_(t+1)`

Thus each generation is replayable and acyclic while the sequence of generations forms recursive self-improvement.

## Fractal recursion
Any H/I/V/E node may itself execute an inner 8-ary scatter-gather diamond or ForcePackage. The topology is self-similar:

`8^0 -> 8^1 -> 8^0`

and recursively composes into `8^N` structures. Older HFO explicitly described the scatter-gather diamond `1->8->1` as the atomic unit and the Obsidian Hourglass as the nested strategic/tactical geometry.

## Deterministic control law
The runtime topology MUST be deterministic even when node cognition is stochastic.

Deterministic surfaces own:
- schedule code / widths;
- slot identities and lineage;
- leases, retries, timeouts and deduplication;
- budgets/effect ceilings;
- fan-in membership;
- evaluator versions;
- verifier separation;
- Pareto/MOME archive admission;
- terminal/ConsumerAck semantics.

LLMs may research, propose, transform, mutate, critique and synthesize inside admitted nodes. They may not silently change topology, authority, evaluator, success criteria or lineage.

## Operational anti-pattern
Current-generation LLMs repeatedly flatten HIVE into a sequential prompt chain because natural-language conversation collapses the high-dimensional archive and topology into one narrative path. This is a representation failure.

The fix is not more prompt prose. Encode HIVE as a versioned DAG contract with 8^N slot geometry and let models inhabit nodes.

## Canonical configuration examples
- `0000`: sequential degraded semantics, `1 -> 1 -> 1 -> 1`.
- `1010`: minimal double diamond, `8 -> 1 -> 8 -> 1`.
- `2120`: standard deep crown/search geometry, `64 -> 8 -> 64 -> 1`.
- `2121`: same search body but eight execution champions, `64 -> 8 -> 64 -> 8`.
- Larger schedules are allowed only when budget, evidence and capacity justify the exponent increase.

## Swarm standing rule
For substantial search/evolution missions, shards should recover this file before designing the force package. The mission should declare a HIVE schedule code and preserve H/I/V/E geometry. Sequential execution is a degraded compatibility mode, not the conceptual architecture.

`HIVE_GEOMETRY=8ARY_DOUBLE_DIAMOND_HOURGLASS`
`DEFAULT_EXAMPLE=2120__64_8_64_1`
`FANOUT=H,V`
`FANIN=I,E`
`ARCHIVE=MOME_PARETO_ECOLOGY`
`GENERATION=DAG`
`RECURSION=RECEIPTS_t_TO_H_t+1`
`STATE=PAST_PRESENT_FUTURE_ALTERNATE_FUTURES`
`TOPOLOGY_AUTHORITY=DETERMINISTIC`
`LLM_ROLE=NODE_COGNITION_NOT_GOVERNOR`

## Historical provenance
- `TTaoGaming/hfo_dev_2026_4/docs/8X0_TRANSMISSION_PROTOCOL.md` — atomic `1->8->1`, hourglass, `8^N` self-similarity.
- `TTaoGaming/hfo_dev_2026_4/PIT_OF_SUCCESS.md` — HIVE phase/port mapping and scale table including `8^2 = 64 APEXes`.
- `TTaoGaming/hfo_dev_2026_4/HFO_GEN_101_FORGE/alpha_infrastructure/hive8_loop.py` — h-POMDP and H/I/V/E loop implementation.
- `TTaoGaming/hfo_dev_2026_4/HFO_GEN_101_FORGE/alpha_infrastructure/mome_archive.py` — MOME/Pareto champion archive.
- `TTaoGaming/hfo_dev_2026_4/docs/topology/F6_mermaid_hive_prey_cycle.md` — Obsidian Hourglass / nested strategic+tactical topology.
