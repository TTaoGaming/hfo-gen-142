# Draft external report — DO NOT POST UNTIL DUAL GATE PASSES

Suggested title:

`FJSPLib behnke48: reproducible optimum 125 / candidate lower-bound update 124 -> 125`

Suggested body:

> Hi — thanks for maintaining the ScheduleOpt benchmark collection.
>
> I independently reproduced a feasible makespan-125 schedule for FJSPLib `behnke48` and obtained an exact CP-SAT optimum result of 125 on the frozen public instance. The current public BKS row at the version tested is still `lower_bound=124`, `upper_bound=125`, `status=open`.
>
> I have kept the result fully reproducible and separated the producer from the certificate verifier. The public proof packet includes:
>
> - exact ScheduleOpt source commit and SHA-256 of the instance/BKS files;
> - a complete 100-operation makespan-125 certificate;
> - an independent checker for machine eligibility/durations, all precedence constraints, per-machine no-overlap and makespan;
> - producer run/job/artifact provenance and immutable hashes;
> - independent decision-model attempts to falsify any schedule at makespan <=124.
>
> If the final independent dual verifier in the proof packet reports infeasible at 124, would you be willing to review the evidence for updating `behnke48` to `lower_bound=125`, `upper_bound=125` / closed?
>
> Proof packet: `<PUBLIC_HFO_PROOF_URL_AFTER_FINAL_GATE>`
> Producer artifact: `<PUBLIC_ACTIONS_ARTIFACT_OR_DURABLE_FILE>`
> Certificate SHA-256: `8ba641446ecc51e28fc07743a0745084aa8c0e4d485cbefc11b6380ab78168b8`
>
> I am deliberately not asking for the archive to be changed until the independent lower-bound evidence is complete; this issue is intended to make the verification path inspectable.
>
> Thanks for maintaining FJSPLib.

## Gate before posting

Do not post this draft unless:

1. frozen public BKS still says `behnke48` is open at `124..125` immediately before posting;
2. independent primal certificate verifier still passes;
3. at least one independent decision/optimization formulation produces a conclusive lower-bound proof at 125 / infeasibility at 124;
4. no newer public ScheduleOpt update already closes the instance;
5. the standing authority envelope still admits this reversible public benchmark report and there are no new terms/account/payment/identity requirements.
