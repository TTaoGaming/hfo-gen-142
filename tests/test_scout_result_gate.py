import hashlib, json, unittest
from tools.scout_result_gate import verdict


def ready_state(lane="CROWN"):
    result = {
        "observed_utc": "2026-09-15T00:00:00Z",
        "lane": lane,
        "finding": "candidate",
        "strongest_falsifier": "none yet",
        "blocker": "none",
        "next_executable_assay": "verify incumbent",
    }
    raw = json.dumps(result, separators=(",", ":"))
    return {
        "actorId": "SIGRUN-GEN142-SCOUT-R0",
        "phase": "READY",
        "epoch": 11,
        "lastLane": lane,
        "lastError": None,
        "lastResult": raw,
        "lastResultSha256": hashlib.sha256(raw.encode()).hexdigest(),
    }


class ScoutResultGateTests(unittest.TestCase):
    def test_valid_ready_result_admitted(self):
        self.assertEqual(verdict(ready_state())["decision"], "ADMIT_RESEARCH_RESULT")

    def test_failed_hashed_payload_refused(self):
        state = ready_state(); state["phase"] = "FAILED"; state["lastError"] = "EMPTY_SYNTHESIS"
        self.assertEqual(verdict(state), {"decision": "HOLD", "code": "SCOUT_NOT_READY"})
    def test_hash_mismatch_refused(self):
        state = ready_state(); state["lastResultSha256"] = "0" * 64
        self.assertEqual(verdict(state)["code"], "RESULT_HASH_MISMATCH")

    def test_lane_mismatch_refused(self):
        state = ready_state(); state["lastLane"] = "DONOR"
        self.assertEqual(verdict(state)["code"], "RESULT_LANE_MISMATCH")

    def test_missing_shape_refused(self):
        state = ready_state()
        obj = json.loads(state["lastResult"]); obj.pop("strongest_falsifier")
        state["lastResult"] = json.dumps(obj, separators=(",", ":"))
        state["lastResultSha256"] = hashlib.sha256(state["lastResult"].encode()).hexdigest()
        self.assertEqual(verdict(state)["code"], "RESULT_SHAPE_REFUSED")

    def test_recovery_required_refused(self):
        state = ready_state(); state["phase"] = "RECOVERY_REQUIRED"
        self.assertEqual(verdict(state)["code"], "SCOUT_NOT_READY")

    def test_malformed_json_refused(self):
        state = ready_state(); state["lastResult"] = "{";
        state["lastResultSha256"] = hashlib.sha256(b"{").hexdigest()
        self.assertEqual(verdict(state)["code"], "RESULT_JSON_REFUSED")


if __name__ == "__main__":
    unittest.main()
