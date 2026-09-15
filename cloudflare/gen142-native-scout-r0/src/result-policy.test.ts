import assert from "node:assert/strict";
import test from "node:test";
import { emptySynthesisNoClaim } from "./result-policy.ts";

const EXPECTED_KEYS = [
  "observed_utc", "lane", "canonical_recovery", "survivors", "finding",
  "strongest_falsifier", "blocker", "next_executable_assay",
].sort();

test("EMPTY_SYNTHESIS terminal is strict no-claim evidence", () => {
  const result = emptySynthesisNoClaim("CROWN", "2026-09-15T07:00:00.000Z");
  assert.deepEqual(Object.keys(result).sort(), EXPECTED_KEYS);
  assert.deepEqual(result.survivors, []);
  assert.equal(result.blocker, "EMPTY_SYNTHESIS");
  assert.equal(result.lane, "CROWN");
  assert.match(result.finding, /no research claim was admitted/i);
  assert.equal(result.canonical_recovery, "github:TTaoGaming/hfo-gen-142#13");
});

test("policy preserves the requested lane without inventing candidates", () => {
  for (const lane of ["CROWN", "DONOR", "BENCHMARK", "REDUCER"] as const) {
    const result = emptySynthesisNoClaim(lane, "2026-09-15T07:00:00.000Z");
    assert.equal(result.lane, lane);
    assert.equal(result.survivors.length, 0);
  }
});
