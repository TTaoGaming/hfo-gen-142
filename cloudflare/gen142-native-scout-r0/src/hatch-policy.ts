export type HatchCandidate = {
  name: string;
  phase: string;
  pressured: boolean;
};

export type HatchDecision =
  | { mode: "HATCH_ONE"; name: string; rotation: number }
  | { mode: "BACKPRESSURE_HOLD"; pressured: string[]; busy: string[] };

export function selectHatchCandidate(
  candidates: HatchCandidate[],
  scheduledTime: number,
  cadenceMinutes = 5,
): HatchDecision {
  if (!Number.isFinite(scheduledTime) || candidates.length === 0) {
    return { mode: "BACKPRESSURE_HOLD", pressured: [], busy: [] };
  }
  const quantum = cadenceMinutes * 60_000;
  const rotation = Math.floor(scheduledTime / quantum) % candidates.length;
  const ordered = candidates.map((_, offset) => candidates[(rotation + offset) % candidates.length]);
  const chosen = ordered.find((candidate) =>
    candidate.phase !== "COGNITION_RUNNING" && !candidate.pressured
  );
  if (chosen) return { mode: "HATCH_ONE", name: chosen.name, rotation };
  return {
    mode: "BACKPRESSURE_HOLD",
    pressured: candidates.filter((x) => x.pressured).map((x) => x.name),
    busy: candidates.filter((x) => x.phase === "COGNITION_RUNNING").map((x) => x.name),
  };
}

export function carrierUuidFromDigest(digest: string): string {
  if (!/^[0-9a-f]{64}$/i.test(digest)) throw new Error("CARRIER_DIGEST_REFUSED");
  const chars = digest.slice(0, 32).toLowerCase().split("");
  chars[12] = "5";
  chars[16] = ((parseInt(chars[16], 16) & 0x3) | 0x8).toString(16);
  const hex = chars.join("");
  return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
}
