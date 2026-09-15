# FJSPLib `behnke48` — optimum-125 proof packet

Status: **INTERNAL_TECHNICAL_CROWN_VERIFIED / EXTERNAL SCHEDULEOPT REVIEW SUBMITTED**.

External public review: https://github.com/ScheduleOpt/benchmarks/issues/6

This packet supports one narrow claim only: under the frozen public ScheduleOpt/FJSPLib `behnke48` instance, makespan `125` is feasible and makespan `<=124` is infeasible. External maintainer review/archive update remains the public crown gate.

## Frozen public state

- Archive: ScheduleOpt / FJSPLib
- Public source commit: `7b3f6fb1384309bd4abca866fe3bef2993139b91`
- Fresh `main` read immediately before external reporting: still the same commit
- Instance: `behnke48`, 20 jobs x 60 machines, 100 operations, 1,768 machine-duration modes, 80 chain precedences
- Public status: `open`
- Public lower bound: `124` (`DOFP2026a`, 2026-08, certificate `no`)
- Public upper bound: `125` (`OptalCP`, 2026-01, certificate `no`)
- Instance SHA-256: `4ded969f2695ef8be7d4bdb8963d9b3063bd392bcf03f465e145030c0c5905ef`
- BKS SHA-256: `3b0dd080fdc966b556830538d776590bf58b333d000425aceadc15ab62b0353f`

## Evolution / producer evidence

Generation R1 tried strict-improvement search without an incumbent and failed. That failure was compiled as `NO_INCUMBENT_BEFORE_IMPROVEMENT_SEARCH`.

Generation R3 changed behavior: generate 256 cheap feasible constructive donors, select the best donor, supply a complete machine/start/end hint, then let OR-Tools CP-SAT improve it.

GitHub Actions run `34921926574`, job `104231761158`, artifact `10378048638`:

- constructive donor: `134`
- observed improvement chain: `134 -> 130 -> 129 -> 128 -> 127 -> 126 -> 125`
- OR-Tools CP-SAT `9.15.6755`
- final status: `OPTIMAL`
- objective: `125`
- best objective bound: `125`
- solver wall time: `574.479 s`
- solution fingerprint: `0x60d4c5685696864e`
- artifact zip digest: `sha256:8c4e8e2673214cd9a97e8ff4433f8a563c9687214cf0be6b7bf88b789a3615fa`

Producer output alone is not treated as proof.

## Independent primal verification

`experiments/fjsplib/verify_certificate_independent.py` does not use the producer solver model. It independently downloads the frozen public instance/BKS and checks operation cardinality, machine eligibility, exact machine-dependent durations, all precedence edges, per-machine no-overlap, makespan, and source hashes.

It passed both locally and on a separate GitHub-hosted job.

Public replay: run `34923588992`, job `104236765690`, verifier artifact `10378259000`:

- verdict `CERTIFICATE_FEASIBLE`
- 100/100 operations exactly once
- 46 machines used
- recomputed makespan `125`
- certificate SHA-256 `8ba641446ecc51e28fc07743a0745084aa8c0e4d485cbefc11b6380ab78168b8`
- artifact zip digest `sha256:aa9c5a481628802026ea7003eec997f2e62bc3c274c494886c459129bd5923f8`

## Independent dual proof

The decisive falsifier uses **PyJobShop 0.0.9 as a separate modeling layer** over the same frozen public JSON:

- one task per public operation;
- one mode per eligible machine/duration;
- all 80 public end-before-start constraints;
- machine no-overlap resources;
- `latest_end=124` for every task, turning the assay into the decision problem “does any valid schedule with makespan <=124 exist?”

Public GitHub run `34923588992`, job `104236765464`, ran for `807.937 s` and returned raw solver status:

**`SolveStatus.INFEASIBLE`**

Therefore no schedule with makespan `<=124` exists under that independent formulation. The dual artifact is `10379885027`, zip digest `sha256:86381a0d50836fc5cd0bbb1554d215e5faeb6f448f17a8c5d00aad0ce4eb85d6`.

The original wrapper contained a presentation-only bug: it tested the mixed-case string `"Infeasible"` against the uppercase status `"SolveStatus.INFEASIBLE"`, so one convenience Boolean in the artifact was false despite the raw solver status being conclusive. Commit `1f540d4624b11ac7d33a9b3b4688256cc787ea49` fixes status normalization. The expensive proof was not rerun merely to change that derived Boolean; the raw log/status is the durable evidence.

## Additional falsification / negative evidence

A separately coded reified target-124 CP-SAT formulation ran for 900 seconds and returned `UNKNOWN`, not proof. Run `34923871072`, job `104237615485`, artifact `10379606479`, digest `sha256:85cd7e4d91359ce59561db9aa415765238b95dd2e39de843dc982d5313232e9e`. This inconclusive result is intentionally preserved rather than hidden.

A seeded PyJobShop optimization replay independently reproduced the feasible 125 schedule but only raised its lower bound to 121 in 300 seconds; again, it is supporting evidence, not the dual proof.

## External submission

The standing authority envelope admitted one free/reversible benchmark report after a fresh read confirmed ScheduleOpt `main` had not changed and `behnke48` remained open at `124..125`.

Submitted public maintainer report:

**https://github.com/ScheduleOpt/benchmarks/issues/6**

The report asks maintainers to review the proof for updating `behnke48` to `lower_bound=125`, `upper_bound=125` / closed. No payment, identity change, terms acceptance, or irreversible effect was required.

## Conclusion and claim ceiling

Internal evidence now supports:

> `behnke48` has optimum makespan 125 under the frozen ScheduleOpt/FJSPLib instance; the frozen public archive's `124..125` open gap is technically closed by this proof packet.

Current state: **internal technical crown verified, external public review submitted**.

Public crown status remains **pending** until ScheduleOpt maintainers independently review the evidence and update/accept the archive result. Do not inflate this into “world's best scheduler” or a generic world-#1 claim.
