export type ScoutLane = "CROWN" | "DONOR" | "BENCHMARK" | "REDUCER";

export function emptySynthesisNoClaim(lane: ScoutLane, observedUtc: string) {
  return {
    observed_utc: observedUtc,
    lane,
    canonical_recovery: "github:TTaoGaming/hfo-gen-142#13",
    survivors: [] as string[],
    finding: "No reducer synthesis was produced; no research claim was admitted.",
    strongest_falsifier: "EMPTY_SYNTHESIS at the neural reducer boundary.",
    blocker: "EMPTY_SYNTHESIS",
    next_executable_assay: "Change reducer strategy or provider path before treating repeated empty synthesis as useful work.",
  };
}
