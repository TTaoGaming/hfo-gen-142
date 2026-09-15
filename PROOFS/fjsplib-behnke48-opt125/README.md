# FJSPLib `behnke48` — candidate optimum-125 proof packet

Status: **CANDIDATE / INDEPENDENT DUAL FALSIFICATION RUNNING**. Do not claim a crown from this packet yet.

## Frozen public state

- Archive: ScheduleOpt / FJSPLib
- Public source commit: `7b3f6fb1384309bd4abca866fe3bef2993139b91`
- Instance: `behnke48`, 20 jobs x 60 machines, 100 operations, 1,768 machine-duration modes, 80 chain precedences
- Public status at the frozen commit: `open`
- Public lower bound: `124` (`DOFP2026a`, 2026-08, certificate `no`)
- Public upper bound: `125` (`OptalCP`, 2026-01, certificate `no`)
- Instance SHA-256: `4ded969f2695ef8be7d4bdb8963d9b3063bd392bcf03f465e145030c0c5905ef`
- BKS SHA-256: `3b0dd080fdc966b556830538d776590bf58b333d000425aceadc15ab62b0353f`

## Producer evidence

Evolution generation R3 used 256 cheap constructive feasible donors, selected the best donor, then supplied a complete machine/start/end hint to OR-Tools CP-SAT 9.15.6755.

GitHub Actions run `34921926574`, job `104231761158`, artifact `10378048638`:

- constructive donor: `134`
- observed improvement chain: `134 -> 130 -> 129 -> 128 -> 127 -> 126 -> 125`
- final status: `OPTIMAL`
- objective: `125`
- best objective bound: `125`
- solver wall time: `574.479 s`
- solution fingerprint: `0x60d4c5685696864e`
- artifact zip digest: `sha256:8c4e8e2673214cd9a97e8ff4433f8a563c9687214cf0be6b7bf88b789a3615fa`

Producer output alone is not accepted as proof.

## Independent primal verification

`experiments/fjsplib/verify_certificate_independent.py` independently downloads the frozen public instance/BKS and checks operation cardinality, machine eligibility, exact machine-dependent durations, all precedence edges, per-machine no-overlap, makespan, and source hashes without using the producer solver model.

Lenovo replay against the original R3 artifact returned:

- `CERTIFICATE_FEASIBLE`
- 100/100 operations exactly once
- 46 machines used
- recomputed makespan `125`
- certificate SHA-256 `8ba641446ecc51e28fc07743a0745084aa8c0e4d485cbefc11b6380ab78168b8`
- matches frozen public UB `125`

## Dual falsification

Required crown gate: independently establish that **no schedule with makespan <=124 exists**.

A second formulation in `experiments/fjsplib/prove_bound_pyjobshop.py` uses PyJobShop 0.0.9's separate modeling layer with the same frozen public JSON: one task per public operation, one mode per eligible machine/duration, arbitrary public precedence edges, no-overlap machine resources, and `latest_end=124` for every task. Its output must return a real infeasibility/optimality result before this packet can advance.

Public GitHub workflow `.github/workflows/fjsplib-dual-proof.yml` additionally reproduces the primal verifier and dual falsifier on GitHub-hosted runners.

## Claim ceiling

Until the dual falsifier passes: **candidate proof only**.

If independent dual verification proves 124 infeasible, the evidence supports the narrow technical statement:

> `behnke48` has optimum makespan 125 under the frozen ScheduleOpt/FJSPLib instance; this closes the archive's frozen `124..125` open gap.

External ScheduleOpt acceptance/update remains the public crown gate. Do not inflate this into a generic "world's best scheduler" claim.
