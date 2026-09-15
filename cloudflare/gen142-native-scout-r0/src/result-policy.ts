export type ScoutLane = "CROWN" | "DONOR" | "BENCHMARK" | "REDUCER";

export type ProposerTrace = {
  role: "PROPOSER";
  lane: ScoutLane;
  claims: string[];
  evidence_urls: string[];
  candidate_survivors: string[];
  uncertainty: string;
};

export type FalsifierTrace = {
  role: "FALSIFIER";
  lane: ScoutLane;
  kills: string[];
  surviving_candidates: string[];
  strongest_falsifier: string;
  blocker: string;
  next_executable_assay: string;
  evidence_urls: string[];
  uncertainty: string;
};

function parseObject(text: string): Record<string, unknown> {
  const trimmed = text.trim().replace(/^```(?:json)?\s*/i, "").replace(/\s*```$/, "");
  const value = JSON.parse(trimmed);
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error("DEBATE_OBJECT_REQUIRED");
  return value as Record<string, unknown>;
}

function exactKeys(obj: Record<string, unknown>, expected: string[], code: string) {
  if (Object.keys(obj).sort().join("|") !== [...expected].sort().join("|")) throw new Error(code);
}

function strings(obj: Record<string, unknown>, key: string, max = 32): string[] {
  const value = obj[key];
  if (!Array.isArray(value) || value.length > max || !value.every((x) => typeof x === "string" && x.length <= 4000)) {
    throw new Error(`DEBATE_${key.toUpperCase()}_REFUSED`);
  }
  return value as string[];
}

function stringField(obj: Record<string, unknown>, key: string): string {
  const value = obj[key];
  if (typeof value !== "string" || value.length > 8000) throw new Error(`DEBATE_${key.toUpperCase()}_REFUSED`);
  return value;
}

export function parseProposer(text: string, lane: ScoutLane): ProposerTrace {
  const obj = parseObject(text);
  exactKeys(obj, ["role", "lane", "claims", "evidence_urls", "candidate_survivors", "uncertainty"], "PROPOSER_FIELDS_REFUSED");
  if (obj.role !== "PROPOSER" || obj.lane !== lane) throw new Error("PROPOSER_BINDING_REFUSED");
  const candidates = strings(obj, "candidate_survivors", 3);
  if (new Set(candidates).size !== candidates.length) throw new Error("PROPOSER_DUPLICATE_CANDIDATE");
  return {
    role: "PROPOSER", lane, claims: strings(obj, "claims"), evidence_urls: strings(obj, "evidence_urls"),
    candidate_survivors: candidates, uncertainty: stringField(obj, "uncertainty"),
  };
}

export function parseFalsifier(text: string, lane: ScoutLane, candidates: string[]): FalsifierTrace {
  const obj = parseObject(text);
  exactKeys(obj, ["role", "lane", "kills", "surviving_candidates", "strongest_falsifier", "blocker", "next_executable_assay", "evidence_urls", "uncertainty"], "FALSIFIER_FIELDS_REFUSED");
  if (obj.role !== "FALSIFIER" || obj.lane !== lane) throw new Error("FALSIFIER_BINDING_REFUSED");
  const kills = strings(obj, "kills", 3);
  const survivors = strings(obj, "surviving_candidates", 3);
  const known = new Set(candidates);
  const combined = [...kills, ...survivors];
  if (combined.some((x) => !known.has(x))) throw new Error("FALSIFIER_INVENTED_CANDIDATE");
  if (new Set(combined).size !== combined.length) throw new Error("FALSIFIER_DUPLICATE_DECISION");
  if (combined.length !== candidates.length) throw new Error("FALSIFIER_PARTITION_INCOMPLETE");
  return {
    role: "FALSIFIER", lane, kills, surviving_candidates: survivors,
    strongest_falsifier: stringField(obj, "strongest_falsifier"), blocker: stringField(obj, "blocker"),
    next_executable_assay: stringField(obj, "next_executable_assay"), evidence_urls: strings(obj, "evidence_urls"),
    uncertainty: stringField(obj, "uncertainty"),
  };
}

export function reduceDebate(proposer: ProposerTrace, falsifier: FalsifierTrace, observedUtc: string) {
  if (proposer.lane !== falsifier.lane) throw new Error("DEBATE_LANE_DRIFT");
  const evidence_urls = [...new Set([...proposer.evidence_urls, ...falsifier.evidence_urls])].slice(0, 20);
  const survivors = falsifier.surviving_candidates;
  return {
    observed_utc: observedUtc,
    lane: proposer.lane,
    canonical_recovery: "github:TTaoGaming/hfo-gen-142#13",
    survivors,
    evidence_urls,
    finding: survivors.length
      ? `${survivors.length} proposer candidate(s) survived the deterministic falsifier partition.`
      : "No proposer candidate survived the deterministic falsifier partition.",
    strongest_falsifier: falsifier.strongest_falsifier,
    blocker: falsifier.blocker,
    next_executable_assay: falsifier.next_executable_assay,
  };
}

export function emptySynthesisNoClaim(lane: ScoutLane, observedUtc: string) {
  return {
    observed_utc: observedUtc, lane, canonical_recovery: "github:TTaoGaming/hfo-gen-142#13",
    survivors: [] as string[], evidence_urls: [] as string[],
    finding: "No reducer synthesis was produced; no research claim was admitted.",
    strongest_falsifier: "EMPTY_SYNTHESIS at the neural reducer boundary.", blocker: "EMPTY_SYNTHESIS",
    next_executable_assay: "Change reducer strategy or provider path before treating repeated empty synthesis as useful work.",
  };
}
