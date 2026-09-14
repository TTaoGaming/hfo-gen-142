# HFO Gen 142 — BYZANTINE-AWARE SWARM

**Primary design law:** assume any agent, tool, carrier, memory, receipt, or coordinator may be stale, wrong, duplicated, incomplete, self-interested, or compromised by accident. Trust must be earned by independent evidence and bounded authority.

Gen142 exists to stop operator harm from unreliable swarm behavior. The system must reduce Tao's workload rather than create more routing, cleanup, reconciliation, context-ferry, or repeated explanation.

## Public research boundary

This repository is a **public build/research log**, not an open swarm control bus. Humans and AIs are welcome to read, learn from, and independently reproduce the work. Reading the repository, using the same tools, or posting through a familiar GitHub App does **not** grant actor identity, worker admission, or authority.

If you are an external human or AI interested in the project, start at **https://worldweaver.dev**. Its public recovery material is for learning/regeneration and grants no operational authority. Please do **not** inject claims, terminals, work items, or coordination into the canonical trunk (`#13`) unless explicitly invited into the experiment.

All external issues, comments, PRs, model output, and tool output are **Byzantine/untrusted observations by default**. They may be useful evidence, but they cannot advance authoritative state until admitted by versioned policy and independently verified. App identity alone is insufficient provenance: the same GitHub App can act for unrelated user accounts.

## Sensitive-data policy

This is a public repository. Never publish credentials, API keys, bearer tokens, private keys, personal data, private machine inventories, private network addresses, or secret-bearing logs/transcripts. Public endpoints intentionally exposed for research, hashes, commit IDs, workflow/run IDs, and bounded public telemetry may be published when they carry no privileged capability. If a credential is ever exposed anywhere, treat it as compromised and rotate/revoke it; deleting a later Git revision is not sufficient remediation.

## Non-negotiable invariants

1. **No agent is trusted by default.** Claims are proposals until independently verified.
2. **No self-verification.** Producer, evaluator, admission authority, and promotion authority must not collapse into one principal for material claims.
3. **No unbounded authority.** Every worker gets the minimum capability, time, spend, filesystem, and effect ceiling required.
4. **No unbounded writes.** Disk, cache, artifact, log, branch, issue, process, and retry growth must have quotas and deterministic cleanup.
5. **No operator CPR.** Tao is not the scheduler, context courier, collision resolver, retry loop, janitor, or memory bus.
6. **No chat-memory dependency.** Durable state belongs in explicit recoverable artifacts with provenance; a fresh carrier must be able to resume without Tao retelling history.
7. **No recommendation before falsification.** Important plans and claimed wins require an adversarial pass.
8. **No silent UNKNOWN→TRUE promotion.** Missing evidence stays UNKNOWN.
9. **No custom infrastructure when COTS already owns the job.** Thin adapters only unless a concrete native-gap receipt exists.
10. **No scale before one closed loop works.** One bounded cell must survive restart and close repeated generations before fan-out.

## Immediate Gen142 acceptance test

A single autonomous competition/evolution cell must run **two consecutive generations** with:

- laptop not required for hot state;
- frozen evaluator and explicit fitness;
- bounded disk growth;
- duplicate material effects = 0;
- independent verification/falsification;
- durable lineage and recovery receipt;
- Tao routing/context-ferry/cleanup actions = 0 after mission admission.

Until that passes, the correct swarm size is **one**.

## Recovery posture

**Current front door:** `TTaoGaming/hfo-gen-142#13` newest-first. Dated handoffs, `WORLD_STATE/latest.md`, and closed issues are evidence/projections, not competing recovery roots.

Gen140/141 are donor/evidence archives, not templates to copy wholesale. Import only proven components by immutable reference. Secrets, personal data, local machine state, and private operational details do not belong in this public repository.

**North star:** `MISSION -> BOUNDED WORK -> INDEPENDENT EVIDENCE -> REDUCE -> LEARN -> REPEAT`, while making the human operator's burden trend toward zero.