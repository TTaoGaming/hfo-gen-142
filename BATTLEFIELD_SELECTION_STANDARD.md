# Battlefield Selection Standard v1

**Purpose:** stop the swarm from choosing random fights, proxy trophies, demo-only work, or technically interesting work with no plausible path to income.

This standard sits **before** execution. A battlefield is not a recommendation until it has a machine-readable card and passes the gate.

## Core doctrine

The swarm is domain-agnostic. Agents are leverage, not the business domain.

Choose fights in this order:

`MISSION INTENT -> MAP -> HARD GATES -> GAP ANALYSIS -> DONOR HARVEST -> CHEAP CANARY -> SUCCESSIVE HALVING -> FULL ATTACK -> PUBLIC PROOF -> CASE STUDY -> INCOME CONVERSION`

No battlefield is selected because it is familiar, AI-adjacent, easy to demo, or has a zero incumbent.

## Three mission classes

### `prestige_crown`
Goal: public, attributable, independently verified #1 or incumbent-beating evidence that is legible to serious buyers.

Hard floor:
- prestige tier A or B;
- independent verifier;
- public attribution;
- durable public evidence;
- real incumbent competition;
- accepted submission protocol;
- buyer legibility >= 0.60;
- explicit commercial translation;
- at least two legal donor genes;
- specific weakness hypothesis backed by evidence.

### `case_study`
Goal: technical proof package with external verifier receipts and a concrete commercial claim.

A private demo is not a case study.

### `income_contract`
Goal: paid conversation / contract / cash. Requires declared demand evidence, a specific offer, and a measurable 7d/30d commercial hypothesis.

## Prestige tiers

Prestige is evaluated **before** win probability.

- **Tier A:** widely recognized institution/platform or domain-standard benchmark; independent evaluation; real competitive field; result understandable without internal context.
- **Tier B:** credible specialist institution/platform with independent evaluation and a real field; strong buyer mapping but less general brand recognition.
- **Tier C:** thin/unknown platform, toy contest, zero-incumbent board without meaningful competition, self-scored surface, or result that requires explanation to establish legitimacy.

`prestige_crown` missions may not execute at Tier C.

## Hard kills

The gate MUST stop the lane with the named verdict.

- `KILL_RANDOM_FIGHT` — no specific weakness hypothesis or no gap evidence.
- `KILL_PROXY` — prestige floor fails.
- `KILL_DEMO` — no independent external verifier / public proof.
- `KILL_NO_BUYER` — no named buyer persona.
- `KILL_NO_INCOME_PATH` — no specific offer, no declared-demand evidence, or expected 30d cash <= 0.
- `KILL_NO_DONOR_DENSITY` — fewer than two legal public donors for an evolutionary mission.
- `KILL_DONOR_POLICY` — donor legality/rules are not explicit.
- `KILL_NOT_EVOLVABLE` — fewer than two mutable axes.
- `KILL_PUBLICATION_TRAP` — proof is hostage to an unbounded maintainer-only path and cannot create timely durable public evidence.
- `KILL_SUBSTITUTION` — frontier mission permits weak/local fallback.
- `BLOCKED_PROVIDER_AUTH` / `BLOCKED_PROVIDER_CLASS` — required frontier carrier is not actually admitted.
- `BLOCKED_EXTERNAL_AUTH` — external run cannot legally/operationally be submitted.
- `HOLD_CANARY_FIRST` — full attack requested before canary promotion.
- `REJECT_UNPROVEN_CROWN` — crown claim lacks accepted-protocol public evidence beating the incumbent.

A killed lane may not be verbally re-recommended in the same cycle unless new evidence changes the failed field.

## Battlefield card

Every target MUST be represented by `schemas/battlefield.v1.schema.json`.

Before recommendation or execution:

```bash
python tools/battlefield_gate.py BATTLEFIELDS/<battlefield_id>.json
```

Only `ADMIT_*` may proceed.

The card forces explicit evidence for:
- current incumbent and timestamp;
- rules/submission/verifier URLs;
- prestige and buyer legibility;
- declared-demand evidence;
- case-study claim and offer;
- donor genes and mutable axes;
- weakness/gap evidence;
- frontier-provider readiness;
- canary/full-run cost and runtime;
- Bayesian estimates **with a written evidence basis**;
- operator-minute budget.

## Freshness

For `canary`, `attack`, and `claim`, incumbent truth must have been checked in the previous 24 hours.

Old leaderboard lore is not current battlefield intelligence.

## Donor doctrine

Public champions/incumbents/baselines/papers/prompts/harnesses/tool policies/repos are gene donors **only when rules allow**.

Do not copy prohibited/private code. Preserve source and contribution lineage.

A donor gene is useful only if it exposes a mutable axis such as:
- prompt / policy;
- orchestration / routing;
- tool selection;
- search / optimizer;
- memory/context strategy;
- verifier/guardrail;
- algorithmic heuristic;
- feature/model ensemble;
- sampling/seed/budget policy.

## Gap analysis

A battlefield needs a falsifiable reason we can win.

The weakness hypothesis must name the gap, e.g.:
- stale incumbent generation;
- weak scaffold despite frontier model;
- sparse search over harness/prompt/tool policy;
- exploitable cost/latency/quality Pareto frontier recognized by the board;
- public baseline materially below known donor family;
- underexplored domain/subtrack with accepted public protocol.

“Frontier model is smart” is not a gap hypothesis.

## Successive-halving law

No full attack from vibes.

Default progression:

1. `SCOUT` — prove battlefield, donors, buyer path, and execution route exist.
2. `CANARY` — smallest official-shaped assay under frozen evaluator.
3. `ATTACK` — only after canary `PASS`; expand survivors, not the population.
4. `CLAIM` — only after public accepted-protocol result beats current incumbent.

The canary must have a predeclared promotion rule.

## Commercial forcing

Every primary battlefield must answer:

1. **Who pays?**
2. **What painful outcome does the result prove we can improve?**
3. **What narrow offer can we sell tomorrow?**
4. **Where is declared demand visible now?**
5. **What exact case-study sentence becomes true if we win?**

No “interesting demo” is a primary target.

Primary system fitness remains:

`externally_verified_useful_progress / Tao_operator_minute`

For commercial ranking also track:

- `P(paid conversation <= 7d)`
- `expected_cash_30d`
- `expected_cash_90d`
- prestige
- buyer legibility
- repeatability
- operator minutes

## Routing score

Hard gates dominate. The numeric score only ranks survivors.

The executable gate emits a routing score using:

`prestige × buyer_legibility × P(beat incumbent) × P(public proof <=7d) × donor_factor × publication_speed / burden`

The score is a routing heuristic, never evidence.

## Anti-Goodhart forcing

- Do not lower prestige to increase crown probability unless mission intent explicitly changes.
- Do not substitute “public PR” for “leaderboard #1”.
- Do not substitute “demo works” for independent evaluator success.
- Do not substitute liveness/wakes for useful terminal work.
- Do not substitute AI-reliability work merely because the machinery is AI.
- Do not substitute small/local models for `FRONTIER_REQUIRED`.
- Do not report probability without the evidence basis field.
- Do not create new infrastructure merely to make a battlefield easier to run.

## Required scout output

One scout cycle returns **at most 3 survivors** and exactly one primary.

For each survivor:
- battlefield ID;
- gate verdict;
- routing score;
- incumbent + metric + timestamp;
- prestige tier;
- buyer/offer/demand evidence;
- donor set;
- weakness hypothesis;
- canary;
- P24 / P7d with basis;
- strongest falsifier;
- exact next action.

If no candidate passes: output `NONE`. Never fill the slot with a worse proxy.

## Case-study consolidation

After a verified result, create one compact packet:
- problem / incumbent;
- accepted protocol;
- donor lineage;
- evolutionary search tree;
- winning configuration;
- external score / ranking;
- cost, runtime, operator-minutes;
- reproducibility receipt;
- transfer lesson;
- buyer-facing offer.

The case study is the bridge from prestige to income. The crown alone is not the product.

## Executable reducer forcing

Materialize cards under `BATTLEFIELDS/`. After individual gate admission, run:

```bash
python tools/battlefield_reduce.py BATTLEFIELDS/*.json
```

The reducer is deterministic: killed/blocked cards cannot survive, survivors are sorted by gate routing score, output is capped at three, and the first survivor is the only primary. If every card fails, the only valid decision is `NONE`.

Repository CI in `.github/workflows/battlefield-contract.yml` validates the schema, battlefield forcing tests, reducer tests, and every materialized non-template battlefield card on relevant pushes/PRs. CI feedback does not replace external-verifier truth or branch-protection policy.