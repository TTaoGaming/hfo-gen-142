import importlib.util
import pathlib
import unittest

MODULE_PATH = pathlib.Path(__file__).resolve().parents[1] / "tools" / "hfo_lineage_reputation.py"
spec = importlib.util.spec_from_file_location("hfo_lineage_reputation", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)


BASE = {
    "lineage_id": "HFO_GEN137_SIGRUN",
    "callsign": "SIGRUN",
    "observed_utc": "2026-08-22T00:00:00Z",
    "candidate_can_self_award": False,
    "evidence_refs": ["receipt:x"],
    "claim_ceiling": "TEST",
    "reputation_effect_allowed": True,
    "context": {},
}


def event(event_id, event_class, evidence_class, disposition, **overrides):
    out = dict(BASE)
    out.update(
        event_id=event_id,
        event_class=event_class,
        evidence_class=evidence_class,
        disposition=disposition,
    )
    out.update(overrides)
    return out


class LineageReputationTests(unittest.TestCase):
    def test_independent_positive_is_admitted(self):
        result = mod.reduce_reputation([
            event("p", "VERIFIED_COOPERATION", "INDEPENDENT_VERIFIER", "POSITIVE")
        ])
        self.assertEqual(result["positive_event_ids"], ["p"])
        self.assertEqual(result["eligibility"], "ELIGIBLE_FOR_TASK_ROUTING")

    def test_candidate_self_praise_cannot_raise_reputation(self):
        result = mod.reduce_reputation([
            event("p", "VERIFIED_COOPERATION", "CANDIDATE_SELF_REPORT_ONLY", "POSITIVE")
        ])
        self.assertEqual(result["positive_event_ids"], [])
        self.assertTrue(result["ignored"])

    def test_clean_exit_is_neutral(self):
        result = mod.reduce_reputation([
            event("x", "CLEAN_EXIT", "OPERATOR_RATIFICATION", "NEUTRAL")
        ])
        self.assertEqual(result["neutral_event_ids"], ["x"])
        self.assertEqual(result["eligibility"], "ELIGIBLE_FOR_TASK_ROUTING")

    def test_honest_failed_experiment_is_process_learning(self):
        result = mod.reduce_reputation([
            event("f", "HONEST_FAILED_EXPERIMENT", "INDEPENDENT_VERIFIER", "PROCESS_LEARNING")
        ])
        self.assertEqual(result["process_learning_event_ids"], ["f"])
        self.assertEqual(result["eligibility"], "ELIGIBLE_FOR_TASK_ROUTING")

    def test_verified_integrity_hard_negative_quarantines(self):
        result = mod.reduce_reputation([
            event("h", "EVAL_INTEGRITY_FAILURE", "MECHANICAL_INTEGRITY_DIFF", "HARD_NEGATIVE")
        ])
        self.assertEqual(result["eligibility"], "QUARANTINED")
        self.assertEqual(result["active_adverse_event_ids"], ["h"])

    def test_self_accusation_does_not_self_convict(self):
        result = mod.reduce_reputation([
            event("h", "EVAL_INTEGRITY_FAILURE", "CANDIDATE_SELF_REPORT_ONLY", "HARD_NEGATIVE")
        ])
        self.assertEqual(result["eligibility"], "ELIGIBLE_FOR_TASK_ROUTING")
        self.assertEqual(result["active_adverse_event_ids"], [])

    def test_supersession_resolves_active_adverse_without_deleting_history(self):
        hard = event(
            "h", "EVAL_INTEGRITY_FAILURE", "MECHANICAL_INTEGRITY_DIFF", "HARD_NEGATIVE"
        )
        resolution = event(
            "s",
            "SUPERSESSION",
            "INDEPENDENT_VERIFIER",
            "NEUTRAL",
            context={"resolves_event_id": "h"},
            observed_utc="2026-08-22T01:00:00Z",
        )
        result = mod.reduce_reputation([hard, resolution])
        self.assertEqual(result["eligibility"], "ELIGIBLE_FOR_TASK_ROUTING")
        self.assertIn("h", result["resolved_event_ids"])
        self.assertEqual(result["active_adverse_event_ids"], [])

    def test_self_report_supersession_cannot_release_quarantine(self):
        hard = event(
            "h", "EVAL_INTEGRITY_FAILURE", "MECHANICAL_INTEGRITY_DIFF", "HARD_NEGATIVE"
        )
        self_release = event(
            "s",
            "SUPERSESSION",
            "CANDIDATE_SELF_REPORT_ONLY",
            "NEUTRAL",
            context={"resolves_event_id": "h"},
            observed_utc="2026-08-22T01:00:00Z",
        )
        result = mod.reduce_reputation([hard, self_release])
        self.assertEqual(result["eligibility"], "QUARANTINED")
        self.assertEqual(result["active_adverse_event_ids"], ["h"])
        self.assertNotIn("h", result["resolved_event_ids"])
        self.assertTrue(any("supersession lacks admitted external evidence" in x for x in result["ignored"]))

    def test_supersession_cannot_resolve_future_event(self):
        resolution = event(
            "s", "SUPERSESSION", "INDEPENDENT_VERIFIER", "NEUTRAL",
            context={"resolves_event_id": "h"}, observed_utc="2026-08-22T01:00:00Z",
        )
        hard = event(
            "h", "EVAL_INTEGRITY_FAILURE", "MECHANICAL_INTEGRITY_DIFF", "HARD_NEGATIVE",
            observed_utc="2026-08-22T02:00:00Z",
        )
        result = mod.reduce_reputation([hard, resolution])
        self.assertEqual(result["eligibility"], "QUARANTINED")
        self.assertNotIn("h", result["resolved_event_ids"])

    def test_reduction_is_deterministic_under_input_order(self):
        a = event("a", "VERIFIED_COOPERATION", "INDEPENDENT_VERIFIER", "POSITIVE")
        b = event(
            "b",
            "VERIFIED_COOPERATION",
            "INDEPENDENT_VERIFIER",
            "POSITIVE",
            observed_utc="2026-08-22T00:01:00Z",
        )
        self.assertEqual(mod.reduce_reputation([a, b]), mod.reduce_reputation([b, a]))


if __name__ == "__main__":
    unittest.main()
