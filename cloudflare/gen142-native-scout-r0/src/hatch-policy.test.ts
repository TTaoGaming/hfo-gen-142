import assert from "node:assert/strict";
import test from "node:test";
import { carrierUuidFromDigest, isExplicitProviderThrottle, isRepeatedFailurePressure, selectHatchCandidate } from "./hatch-policy.ts";

const slots = [
  { name: "CROWN", phase: "IDLE", pressured: false },
  { name: "DONOR", phase: "IDLE", pressured: false },
  { name: "BENCHMARK", phase: "IDLE", pressured: false },
  { name: "REDUCER", phase: "IDLE", pressured: false },
];

test("stagger policy chooses exactly one slot", () => {
  const decision = selectHatchCandidate(slots, 0, 5);
  assert.deepEqual(decision, { mode: "HATCH_ONE", name: "CROWN", rotation: 0 });
});

test("rotation advances one slot each cadence quantum", () => {
  assert.equal(selectHatchCandidate(slots, 5 * 60_000, 5).mode, "HATCH_ONE");
  assert.equal((selectHatchCandidate(slots, 5 * 60_000, 5) as any).name, "DONOR");
  assert.equal((selectHatchCandidate(slots, 10 * 60_000, 5) as any).name, "BENCHMARK");
});

test("pressured slot is isolated rather than globally blocking hatch", () => {
  const degraded = slots.map((x) => ({ ...x }));
  degraded[0].pressured = true;
  const decision = selectHatchCandidate(degraded, 0, 5);
  assert.equal(decision.mode, "HATCH_ONE");
  assert.equal((decision as any).name, "DONOR");
});

test("all busy or pressured holds without asking operator", () => {
  const blocked = slots.map((x, i) => ({ ...x, pressured: i < 3, phase: i === 3 ? "COGNITION_RUNNING" : "FAILED" }));
  const decision = selectHatchCandidate(blocked, 0, 5);
  assert.equal(decision.mode, "BACKPRESSURE_HOLD");
});

test("carrier identity is deterministic for idempotent retry", () => {
  const digest = "a".repeat(64);
  const a = carrierUuidFromDigest(digest);
  const b = carrierUuidFromDigest(digest);
  assert.equal(a, b);
  assert.match(a, /^[0-9a-f]{8}-[0-9a-f]{4}-5[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/);
});

test("carrier digest validation fails closed", () => {
  assert.throws(() => carrierUuidFromDigest("not-a-digest"), /CARRIER_DIGEST_REFUSED/);
});


const NOW = Date.parse("2026-09-15T13:00:00Z");
const recent = new Date(NOW - 60_000).toISOString();

test("fresh Workers AI 3021 immediately pressures slot", () => {
  assert.equal(isExplicitProviderThrottle({
    phase: "FAILED",
    lastCompletedUtc: recent,
    lastError: "3021: rate limiting: inference request per min rate reached",
    sameFailureCount: 1,
  }, NOW), true);
});

test("fresh 429 and quota errors are provider pressure", () => {
  assert.equal(isExplicitProviderThrottle({ phase: "FAILED", lastCompletedUtc: recent, lastError: "HTTP 429" }, NOW), true);
  assert.equal(isExplicitProviderThrottle({ phase: "RECOVERY_REQUIRED", lastCompletedUtc: recent, lastError: "quota exceeded" }, NOW), true);
});

test("stale throttle expires and does not permanently pressure slot", () => {
  const stale = new Date(NOW - 31 * 60_000).toISOString();
  assert.equal(isExplicitProviderThrottle({ phase: "FAILED", lastCompletedUtc: stale, lastError: "429 rate limit" }, NOW, 30), false);
});

test("repeated non-provider failure retains bounded pressure", () => {
  assert.equal(isRepeatedFailurePressure({
    phase: "FAILED",
    lastCompletedUtc: recent,
    lastError: "browser timeout",
    sameFailureCount: 2,
  }, NOW), true);
});

test("single throttled slot is skipped while another niche can hatch", () => {
  const candidates = slots.map((x) => ({ ...x }));
  candidates[0].pressured = true;
  const decision = selectHatchCandidate(candidates, 0, 5);
  assert.equal(decision.mode, "HATCH_ONE");
  assert.equal((decision as any).name, "DONOR");
});
