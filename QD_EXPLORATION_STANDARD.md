# GEN142 QD / MOME exploration standard

Status: candidate forcing function for **exploration**, not a new scheduler, queue, lease owner, memory store, or submission authority.

## Why this exists

The incumbent crown reducer intentionally returns at most three survivors and exactly one primary. That behavior is useful near an irreversible submission decision, but it is destructive during broad search: different domains, proof horizons, compute regimes, and verifier surfaces are incomparable niches. Premature global ranking collapses useful diversity before the swarm has measured it.

During an `EXPLORE_QD_MOME` mission, **no global primary exists**. A battlefield can only displace another candidate inside the same behavioral niche, and only under the frozen admission/evaluation policy. Submission packaging remains a separate later mode.

## Donor patterns assimilated

- **pyRibs** (`icaros-usc/pyribs`): explicit Archive / Emitter / Scheduler separation. We borrow the separation of *where elites live* from *how variants are proposed*; Gen142 keeps its incumbent GitHub/Cloudflare clocks instead of importing another scheduler.
- **QDax MOME** (`adaptive-intelligent-robotics/qdax`): a Pareto front is maintained per behavioral cell instead of choosing one global winner.
- **MOME-PGX** (`adaptive-intelligent-robotics/mome_pgx`): crowding-based pressure preserves diverse Pareto elites when a cell becomes overfull.
- **GEPA** (`gepa-ai/gepa`): proposal/reflection is separate from Pareto-aware acceptance; execution traces may inform mutation but do not become evaluator authority.

These are design donors, not authority. Gen142's `battlefield_gate.py`, public incumbent/evaluator evidence, verifier/ConsumerAck rules, and existing effect ceilings remain frozen owners.

## Archive behavior

`tools/battlefield_qd_archive.py` is a pure deterministic projection over versioned battlefield cards:

1. Reuse the existing `battlefield_gate.py`; a killed/held card cannot enter the archive.
2. Derive a behavioral niche from `domain × proof-latency band × canary-compute band × verifier band`.
3. Within each niche, preserve the non-dominated set over routing score, prestige, buyer legibility, crown probability, public-proof probability, and canary efficiency.
4. If a niche exceeds its bounded elite count, use deterministic multi-objective crowding distance to preserve extremes rather than highest scalar score only.
5. Retain dominated and crowding-evicted rows as evidence; do not rewrite them as failed experiments.
6. Emit `global_primary: null` and `collapse_forbidden: true` in exploration mode.

## Swarm pressure

Different Hluti should preferentially explore different or underfilled niches. A collision inside a populated niche should mutate a different axis, falsify an incumbent, mine a distinct legal donor, or move to another niche rather than duplicate material work. Manual waves may remain broad while the archive is sparse.

A later explicit `PACKAGE/SUBMIT` mission may invoke the incumbent scalar reducer, but that transition must be visible and must not retroactively erase the QD archive.

## Acceptance

- Three admitted cards in three different niches all survive simultaneously.
- A dominated candidate is removed only from its own niche champion set and remains in evidence.
- Crowding preserves objective extremes when a niche is overfull.
- No exploration output names a global primary.
- No new wake/scheduler/control-plane owner is introduced.
