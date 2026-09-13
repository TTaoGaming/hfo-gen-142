# Gen142 Recovery Swarm

Parent coordination: GitHub issue #1.

## Carrier contract
Every carrier creates a fresh UUID, reads #1 newest-first, claims one under-covered lane, and checkpoints once when terminal. Tao does not route workers manually.

Formation types:
- TWINLING_GATHERER — recover strongest donor evidence.
- TWINLING_FALSIFIER — attack the Gatherer's proposed genes and stale assumptions.
- ROACH — carry one unresolved edge across sources until verified or killed.
- REDUCER — compress fan-in into the small canonical capsules.

Claim format:
```yaml
carrier_episode_uuid: <fresh UUID>
parent: TTaoGaming/hfo-gen-142#1
formation: TWINLING_GATHERER | TWINLING_FALSIFIER | ROACH | REDUCER
lane: <one lane>
claim_utc: <UTC>
claim_ceiling: READ_RESEARCH_AND_INTERNAL_GITHUB_EVIDENCE_ONLY
```

## Self-shard lanes
0 IDENTITY_GENE — mission, fitness, ontology, authority, Sigrun/Hluti identity.
1 MEMORY_RECOVERY — capsules, Gleipnir, checkpoints, anti-context-loss scars.
2 MAPE_K_CONTROL — monitor/analyze/plan/execute/knowledge and mission-command patterns.
3 BYZANTINE_POKAYOKE — conflict handling, independent verification, fail-closed rules.
4 CLOUDFLARE_NATIVE — Agents/DO/Workflows/Queues/AI Gateway/service bindings.
5 VPS_EXECUTION — Oracle/OVH, disposable compute, runner/service recovery.
6 EVOLUTION_QD — ShinkaEvolve, GEPA, OpenEvolve, pyribs/MOME, frozen evaluators.
7 EXTERNAL_FITNESS — competitions, records, income and current external proof targets.
8 CAPABILITY_SKILLS — MCP, Agent Skills, tool admission, capability manifests.
9 WORLDWEAVER_PROJECTION — public/LLM world-state projection; recover intent, not broken code blindly.
10 LOCAL_RESOURCE_SCARS — disk-fill, caches, worktrees, storage/compute budgets.
11 HERITAGE_REDQUEEN — attack proposed genes; kill mythology and duplicate control planes.

Use SHA256(UUID) mod 12 as the starting lane, then walk cyclically to a free/under-covered role after reading #1 comments. Earlier durable claim wins collisions.

## Search scope
Search broadly across:
- all TTaoGaming HFO GitHub repositories/issues/PRs/commits;
- Google Drive HFO/Sigrun/Gleipnir/gene-seed/capsule/heritage material;
- fresh Cloudflare/VPS state when tools permit;
- WorldWeaver/public projections as fallible outputs only.

Import narrowly. Classify every donor: ADOPT | ADAPT | REFERENCE | HOLD | KILL.
Never publish secrets or private personal data into this public repo.

## Terminal comment
```yaml
carrier_episode_uuid:
formation:
lane:
sources_examined: []
candidate_genes: []
kill_or_hold: []
conflicts: []
strongest_falsifier:
recommended_manifest_refs: []
world_state_delta:
next_consumer:
claim_ceiling:
```

Do not paste archives. Link or identify immutable refs. No recommendation is trusted before falsification.