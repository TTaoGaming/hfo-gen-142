import unittest
from tools.hatchery_reduce_v1 import reduce_event, sha256


def event(entries):
    return {
        "schema": "hfo.hatchery-event.v1",
        "policy": "bounded-four-slot-hatchery-v1",
        "entries": entries,
        "entries_sha256": sha256(entries),
    }


class HatcheryReducerTest(unittest.TestCase):
    def test_rate_limit_becomes_machine_backpressure(self):
        entries = [
            {"slot": "CROWN", "phase": "FAILED", "error": "3021: rate limiting: inference request per min rate reached"},
            {"slot": "BENCHMARK", "phase": "FAILED", "error": "3021: rate limiting: inference request per min rate reached"},
        ]
        out = reduce_event(event(entries))
        self.assertEqual(out["decision"], "BACKPRESSURE_PROVIDER_RATE_LIMIT")
        self.assertEqual(out["operator_action_required"], "NONE")
        self.assertFalse(out["tao_relay_required"])

    def test_valid_reducer_ready_wins_deterministically(self):
        base = {"survivors": ["A"], "finding": "f", "blocker": "", "next_executable_assay": "assay"}
        entries = [
            {"slot": "CROWN", "lane": "CROWN", "result_sha256": "a" * 64, "result": base},
            {"slot": "REDUCER", "lane": "REDUCER", "result_sha256": "b" * 64, "result": {**base, "next_executable_assay": "reduce-next"}},
        ]
        out = reduce_event(event(entries))
        self.assertEqual(out["decision"], "NEXT_RESEARCH_EDGE")
        self.assertEqual(out["source_slot"], "REDUCER")
        self.assertEqual(out["next_executable_assay"], "reduce-next")

    def test_no_ready_is_bounded_hold(self):
        entries = [{"slot": "DONOR", "phase": "READY", "error": "SCOUT_ADMISSION_REFUSED"}]
        out = reduce_event(event(entries))
        self.assertEqual(out["decision"], "HOLD_NO_ADMITTED_READY")
        self.assertEqual(out["next_transition"], "WAIT_NEXT_SCHEDULED_HATCH")

    def test_event_hash_mismatch_fails_closed(self):
        doc = event([])
        doc["entries_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "HATCHERY_EVENT_HASH_MISMATCH"):
            reduce_event(doc)


if __name__ == "__main__":
    unittest.main()
