import json
import unittest
from tools.scout_fanin_v1 import sha256, validate_ready


class ScoutFaninTests(unittest.TestCase):
    def state(self):
        value = {
            "observed_utc": "2026-09-15T00:00:00Z",
            "lane": "CROWN",
            "canonical_recovery": "#13",
            "survivors": ["one"],
            "finding": "bounded finding",
            "strongest_falsifier": "bounded falsifier",
            "blocker": "none",
            "next_executable_assay": "one canary",
        }
        text = json.dumps(value, separators=(",", ":"))
        return {
            "actorId": "SIGRUN-GEN142-SCOUT-R0",
            "phase": "READY",
            "epoch": 11,
            "lastLane": "CROWN",
            "lastAttemptLane": "CROWN",
            "lastResult": text,
            "lastResultSha256": sha256(text),
        }, value

    def test_valid_ready_is_admitted(self):
        state, expected = self.state()
        digest, value = validate_ready(state)
        self.assertEqual(digest, state["lastResultSha256"])
        self.assertEqual(value, expected)

    def test_hash_mismatch_is_rejected(self):
        state, _ = self.state()
        state["lastResultSha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "RESULT_HASH_MISMATCH"):
            validate_ready(state)

    def test_outer_lane_mismatch_is_rejected(self):
        state, _ = self.state()
        state["lastAttemptLane"] = "DONOR"
        with self.assertRaisesRegex(ValueError, "READY_OUTER_LANE_MISMATCH"):
            validate_ready(state)

    def test_inner_lane_mismatch_is_rejected(self):
        state, value = self.state()
        value["lane"] = "DONOR"
        text = json.dumps(value, separators=(",", ":"))
        state["lastResult"] = text
        state["lastResultSha256"] = sha256(text)
        with self.assertRaisesRegex(ValueError, "RESULT_LANE_MISMATCH"):
            validate_ready(state)


if __name__ == "__main__":
    unittest.main()
