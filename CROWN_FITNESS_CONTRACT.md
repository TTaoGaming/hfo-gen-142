# Crown Fitness Contract

Objective: obtain high-prestige, buyer-legible public #1 evidence. An easier low-value crown is not an acceptable substitute.

## Admission gate
A target passes only when all are true:
- independent verifier
- attributable public result
- real incumbent competition
- clear buyer mapping
- durable public evidence
- accepted submission protocol

If any item fails, verdict is `KILL_PROXY`.

A zero incumbent alone does not pass the prestige gate.

## Provider gate
If `FRONTIER_REQUIRED=true`, a frontier provider must be live and admitted before execution. Do not silently fall back to local Ollama or a weaker model. If the frontier route is unavailable, stop with `BLOCKED_PROVIDER_AUTH`.

## Donor evolution
Public incumbent and champion harnesses, prompts, tool policies, papers, repos, and other public artifacts may be used as donor genes when the benchmark rules allow it. Mutations must be evaluated on the frozen official protocol.

Use successive halving: cheap canary, kill most, promote survivors, then pay for a full run.

## Crown proof
`CROWN_WON=true` requires a public accepted-protocol result that strictly beats the current incumbent and is attributable to the submitting identity. A prepared submission, self-score, or private run is not a crown.

Rank surviving targets in this order: prestige-floor pass, probability of public #1, buyer legibility, verifier credibility, attribution, reproducibility, publication speed, then cost and Tao operator-minutes.
