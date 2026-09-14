# Storage recovery and heritage learning — proposal

Consumer: Gen142 LOCAL_RESOURCE_SCARS workers and the existing issue #1 heritage reducer.
Status: ADAPT proposal. No canon promotion, deployed enforcement, complete backup, or consumer acknowledgement is claimed.

## Recovery target

Reach 30% free disk space, using 20% as the first checkpoint. This is a proposed operating target, not a claim about any host's current capacity. Record actual allocation changes: logical file sizes and deduplicated upload sizes do not prove local space reclaimed.

For each bounded batch: inventory literal paths privately; preserve current source state; deduplicate exact hashes; upload through the incumbent backup tool; verify recoverability and unchanged sources; independently review; delete only authorized eligible copies; record actual free-space gain and restoration results. An event never grants deletion authority. Preserve active dependencies, credentials and uncommitted work. Database journals require a consistent snapshot. Do not bulk-delete worktrees or treat generation age as deletion proof.

The laptop retains active work. Private Drive retains archive objects, versioned manifests and restore mappings. External drives provide independently verified copies of irreplaceable history when available. GitHub receives appropriate code and sanitized reductions. No external backup is proven merely by describing this layout.

## Reuse existing standards and owners

Use `STANDARDS_PROFILE.md`, `STRIFE_SPLENDOR.md`, `KNOWLEDGE_PROTOCOL.md` and the existing `schemas/strife-splendor-event-v1.schema.json`. CloudEvents is a CNCF specification; W3C PROV and Trace Context provide provenance/correlation semantics. Envelope `specversion` remains `1.0` for the stable 1.0.2 specification. Add real trace context only when a real trace exists; never fabricate it for cosmetic completeness.

These events are file-backed proposals for the existing reducer, not a new bus, database, scheduler or canonical index. Promotion remains OBSERVED -> SOURCED -> FALSIFIED -> CORROBORATED -> CONSUMED -> ADOPTED. No caller may infer independence from repeated copies or declare ConsumerAck on another consumer's behalf.

## Progressive heritage reduction

1. Original source objects/snapshots remain immutable.
2. A private package manifest binds package ID, original paths, hashes, object IDs, snapshot consistency, visibility, provenance, verification and disposition.
3. A short package capsule records purpose, age band, decisions, gaps, restore method and opaque evidence IDs.
4. Useful STRIFE/SPLENDOR lessons become schema-validated proposals with source hashes, falsifiers and claim ceilings.
5. The existing reducer admits only falsified, corroborated and consumed deltas to existing canonical projections.

Summaries point to sources; they never replace backups. Same-source copies are one evidence lineage. Different generations can contain distinct useful work. Summarize a package when it aids retrieval or a current task; do not generate one verbose summary per file.

## Manual kata before automation

Weekly: measure growth/free space; select one batch and predict recovery; execute; compare actual results; record one lesson. Monthly: restore a useful sample; reconcile manifests and deletions; review working sets/models/caches; check external-backup coverage. Trial three weekly cycles and one monthly restore exercise before automating proven steps. No schedule is installed here.

Proposed guardrails: aim for 25–35% free; prioritize cleanup below 25%; defer optional bulk downloads/workspace replication below 20%. These thresholds are not currently enforced by this proposal.

## Validation and consumption

The paired JSON files are explicitly synthetic OBSERVED examples, supported only by the public workflow document. They contain no private receipt hashes or private-derived identifiers. Real receipt-linked SOURCED events and their authorized evidence resolver remain in the private Drive archive. This public PR does not establish private byte recovery. Run `validate.py` with Python and jsonschema against the pinned repo schema. The validation report is local schema/contract evidence only, not semantic truth or runtime deployment.

The next existing reducer should re-verify evidence through authorized access, challenge the strongest falsifier, and record a real downstream consumer result before promotion. Do not edit GENE_SEED or WORLD_STATE on the strength of this proposal alone.

References: https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md ; https://www.w3.org/TR/prov-o/ ; https://www.w3.org/TR/trace-context/
