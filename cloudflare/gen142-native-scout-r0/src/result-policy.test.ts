import assert from "node:assert/strict";
import test from "node:test";
import { emptySynthesisNoClaim, parseFalsifier, parseProposer, reduceDebate } from "./result-policy.ts";

const EXPECTED_KEYS = [
  "observed_utc", "lane", "canonical_recovery", "survivors", "evidence_urls", "finding",
  "strongest_falsifier", "blocker", "next_executable_assay",
].sort();

test("EMPTY_SYNTHESIS terminal remains strict no-claim evidence", () => {
  const result = emptySynthesisNoClaim("CROWN", "2026-09-15T07:00:00.000Z");
  assert.deepEqual(Object.keys(result).sort(), EXPECTED_KEYS);
  assert.deepEqual(result.survivors, []);
  assert.deepEqual(result.evidence_urls, []);
  assert.equal(result.blocker, "EMPTY_SYNTHESIS");
  assert.equal(result.lane, "CROWN");
  assert.match(result.finding, /no research claim was admitted/i);
});

test("deterministic reducer admits only falsifier-surviving proposer candidates", () => {
  const proposer = parseProposer(JSON.stringify({
    role: "PROPOSER", lane: "CROWN", claims: ["claim"], evidence_urls: ["https://a.example"],
    candidate_survivors: ["A", "B"], uncertainty: "medium",
  }), "CROWN");
  const falsifier = parseFalsifier(JSON.stringify({
    role: "FALSIFIER", lane: "CROWN", kills: ["A"], surviving_candidates: ["B"],
    strongest_falsifier: "A fails verifier", blocker: "", next_executable_assay: "assay B",
    evidence_urls: ["https://b.example"], uncertainty: "low",
  }), "CROWN", proposer.candidate_survivors);
  const result = reduceDebate(proposer, falsifier, "2026-09-15T13:40:00.000Z");
  assert.deepEqual(result.survivors, ["B"]);
  assert.deepEqual(result.evidence_urls, ["https://a.example", "https://b.example"]);
  assert.equal(result.next_executable_assay, "assay B");
});

test("falsifier cannot invent or omit candidate decisions", () => {
  const candidates = ["A", "B"];
  assert.throws(() => parseFalsifier(JSON.stringify({
    role: "FALSIFIER", lane: "DONOR", kills: ["A"], surviving_candidates: ["C"],
    strongest_falsifier: "x", blocker: "", next_executable_assay: "y",
    evidence_urls: [], uncertainty: "z",
  }), "DONOR", candidates), /FALSIFIER_INVENTED_CANDIDATE/);
  assert.throws(() => parseFalsifier(JSON.stringify({
    role: "FALSIFIER", lane: "DONOR", kills: ["A"], surviving_candidates: [],
    strongest_falsifier: "x", blocker: "", next_executable_assay: "y",
    evidence_urls: [], uncertainty: "z",
  }), "DONOR", candidates), /FALSIFIER_PARTITION_INCOMPLETE/);
});

test("proposer candidates are bounded and unique", () => {
  assert.throws(() => parseProposer(JSON.stringify({
    role: "PROPOSER", lane: "BENCHMARK", claims: [], evidence_urls: [],
    candidate_survivors: ["A", "A"], uncertainty: "low",
  }), "BENCHMARK"), /PROPOSER_DUPLICATE_CANDIDATE/);
});
