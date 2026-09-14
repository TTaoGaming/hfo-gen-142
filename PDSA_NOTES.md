# Evolution PDSA notes and blocker handoff

Consumer: Sigrun and the next carrier continuing PR4. Repeated operator messages
request sequential notes/blocker cycles, not duplicate provider campaigns or a
new scheduler. Read the last entry, inspect one unresolved edge, append a delta
or explicit no-change result. Do not rerun unchanged probes merely to fill a turn.

## Cycle N1 — 2026-09-14T03:30:56Z

**Plan:** distinguish what blocks a new campaign from what merely lacks evidence;
identify the smallest zero-provider next check. Scope: notes, source review and
GitHub readback. Provider requests, installations and runtime mutations: zero.

**Do:** read PR4 head `72fe9d5a69a60fe4d75fa96554e72702cb01b27e`, current
campaign/budget/recovery records, and the provider adapter. PR4 is OPEN/DRAFT;
GitHub reports no checks on the branch. This is absent CI evidence, not failed CI.
Runtime assays and quota figures below retain their original timestamps; neither
VPS nor live model availability was reprobed in this cycle.

**Study:** a new source-level concern was identified. `pdsa-budget.mjs` reserves
a row, awaits quota/catalog checks, sets `dispatched`, saves, then performs the
provider call. Its `save()` retains `stop_requested` but does not abort that
dispatch path. The existing stop test covers a response already in flight, not a
stop arriving during quota checking. Classify this as **suspected stop-before-
dispatch race, not reproduced**. Do not label it a live leak or a completed fix.

### Blockers in execution order

| ID | State and evidence | Owner / next action | Exit evidence |
|---|---|---|---|
| B1 | Suspected stop-before-dispatch race in current candidate source | Implementation carrier: hold a mock quota response, issue stop, release quota, count dispatches | Zero provider dispatch after stop in that window; retain existing in-flight completion test |
| B2 | Interrupted generation skipped; archived r2d caller exits 0 with only generation 0 | Implementation carrier: inspect native unfinished generation metadata and retained response; no fresh inference | Expected generation plus evaluator receipt after recovery; no repeated uncertain call |
| B3 | Arbitrary algorithm isolation unproved; Oracle Docker installation approval still absent in this task | Operator approval only for that exact installation; implementation carrier owns sandbox negative tests afterward | Explicit installation authorization if using Oracle Docker; network/credential/write/resource isolation assays |
| B4 | Longer campaign and vendor allocations are planning records; account-wide races/fences unproved | Implementation carrier: test two callers against one remaining mock allowance; bind a fresh mission in existing owner | One dispatch maximum, stale-holder rejection, finite reservation; never reset R1 |
| B5 | Verified cycle phase/ACK times and human-intervention counts unknown | Implementation carrier: instrument existing receipts on the two-generation path | Two consecutive verified dispositions with timing and zero operator routing; failures remain in denominator |

B3 is not a reason to stop B1/B2/B4's zero-provider work. Automatic approval
review previously rejected installing Docker on Oracle because it adds a
persistent privileged daemon and changes the VPS attack surface. That exact
installation remains pending explicit approval; this notes cycle does not retry
it or request approval again. Earlier general deployment approvals are not
recorded as resolving that specific rejection.

Other evidence gaps: no reported PR checks; free-vendor remaining quotas unknown;
OpenRouter's old completion remains uncertain; current champion keeper acceptance
and independent approval of the normalized descendant remain unproved. The
03:15 Kimi quota snapshot is historical and exceeds the five-minute admission
freshness window at this entry. It must not authorize a later request unchanged.

**Act / next queued cycle:** execute B1's local mock falsifier and record the
result before expanding scope. A failure justifies a narrow fix and replay; a
pass narrows the concern without proving full account safety. Then proceed to B2.
Do not infer that the next queued message authorizes additional provider spend.

**Strife:** stop-state persistence was almost treated as complete cancellation
coverage. Smallest guard: test stop before dispatch separately from stop after
dispatch. **Splendor:** existing immutable receipts expose incomplete recovery
without spending more quota; the earlier champion lineage remains preserved.
No new champion or increase in runtime stability is claimed this cycle.
