# Hive Integration Wave 1 — Ten Roaches

Target population: 10 Roach carriers, one per H0..H9 lane where possible.

Parent inputs:
- issue #1 — Twinling evidence lake
- issue #2 — future durable Burrow/fan-in surface
- `GATEWAY.md`
- `HIVE.md`
- `ZERG_CAPACITY_ARCHETYPES.md`
- `A2A_SKILLS_TOOLS_PROFILE.md`
- `a2a/HIVE_AGENT_CARD_REQUIREMENTS.md`
- `.agents/skills/hive-integration/SKILL.md`

Goal: integrate the pieces already recovered into the smallest standards-native Hive contract. This wave is allowed to search old generations for missing donors, but its fitness is integration and deletion, not archaeology volume.

## Self-shard

Generate fresh UUID. `start = SHA256(UUID) mod 10` over H0..H9. Read current claims newest-first. Take the first under-covered lane walking cyclically. Earlier durable claim wins; loser keeps UUID and walks onward. H9 Reducer should normally wait until several H0..H8 terminals exist; an early H9 carrier may instead map gaps and HOLD.

## Required rhythm

`PLAN -> DO -> STUDY -> ACT`

Target 30 minutes, early terminal allowed after decisive falsification/reduction.

Every terminal must say what should be ADOPTED, ADAPTED, HELD and KILLED and name the exact next consumer.

## Wave acceptance

The wave succeeds when a reducer can answer, without Tao:
1. what the canonical Zerg capacity archetypes mean;
2. which are actors vs phenotypes vs Skills vs platform-owned mechanisms;
3. what gets an A2A Agent Card and what explicitly does not;
4. what Skill packages exist and when they activate;
5. how tools are discovered/admitted without authority leakage;
6. how Cloudflare owns durable actor/Burrow/workflow state;
7. how GitHub/WorldWeaver own institutional/public recovery;
8. how Strife/Splendor + ConsumerAck make the Hive learn;
9. what one smallest end-to-end Hive R0 assay is;
10. which Gen140/141 mechanisms should stay dead.

No runtime deployment, external effect, spend expansion, secret access, or custom control-plane implementation is authorized by this wave.