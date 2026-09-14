# Crown Fitness Contract

Objective: obtain high-prestige, buyer-legible public #1 evidence. An easier low-value crown is not an acceptable substitute.

This contract is subordinate to `BATTLEFIELD_SELECTION_STANDARD.md`. Every crown target must have a `battlefield.v1` card and pass `tools/battlefield_gate.py` before recommendation or execution.

## Admission gate
A target passes only when all are true:
- independent verifier
- attributable public result
- real incumbent competition
- clear buyer mapping
- durable public evidence
- accepted submission protocol
- prestige tier A or B under the battlefield standard
- declared demand evidence and a specific sellable offer
- at least two legal donor genes and two mutable axes
- falsifiable weakness hypothesis with gap evidence

If any prestige item fails, verdict is `KILL_PROXY`.

A zero incumbent alone does not pass the prestige gate.
A technically interesting demo with no commercial translation does not pass.
A target chosen only because the swarm already knows the domain does not pass.

## Provider gate
If `FRONTIER_REQUIRED=true`, a frontier provider must be live and admitted before execution. Do not silently fall back to local Ollama or a weaker model. If the frontier route is unavailable, stop with `BLOCKED_PROVIDER_AUTH`.

`no_weak_fallback=true` is mandatory for frontier crown work. A weak substitution is `KILL_SUBSTITUTION`.

## Donor evolution
Public incumbent and champion harnesses, prompts, tool policies, papers, repos, and other public artifacts may be used as donor genes when the benchmark rules allow it. Mutations must be evaluated on the frozen official protocol.

Use successive halving: scout -> cheap official-shaped canary -> kill most -> promote survivors -> full run.

No full run is admitted until the battlefield card's canary status is `PASS` under its predeclared promotion rule.

## Crown proof
`CROWN_WON=true` requires a public accepted-protocol result that strictly beats the current incumbent and is attributable to the submitting identity. A prepared submission, self-score, private run, public PR without the accepted score, or demo is not a crown.

For `canary`, `attack`, and `claim`, the incumbent must have been re-checked within the previous 24 hours.

## Commercial proof
Every crown target must state:
- buyer persona;
- narrow offer;
- declared demand evidence;
- case-study claim unlocked by the win;
- `P(paid conversation <= 7d)`;
- positive `expected_cash_30d`;
- operator-minute budget.

The crown is prestige inventory. The case study + offer is the income bridge.

## Ranking order
Hard gates first. Rank only survivors in this order:
1. prestige-floor pass;
2. buyer legibility and commercial translation;
3. probability of beating current incumbent;
4. verifier credibility;
5. donor density / evolvability;
6. attribution and reproducibility;
7. public-proof latency;
8. expected 7d conversation / 30d cash;
9. compute cost and Tao operator-minutes.

If no target survives, output `NONE`. Never fill the slot with an easier proxy trophy.
