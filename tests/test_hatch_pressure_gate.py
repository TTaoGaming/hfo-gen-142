import copy
import unittest

from tools.hatch_pressure_gate import evaluate


def base_snapshot():
    return {
        "schema": "hfo.hatch-pressure-snapshot.v1",
        "policy_version": "gen142-hatch-pressure-r0",
        "observed_utc": "2026-09-15T07:00:00Z",
        "requested": {
            "semantic_key": "crown:trafficflow:canary",
            "formation": "TWINLING",
            "count": 2,
            "provider": "cloudflare-ai-gateway",
            "tao_hot_loop_required": False,
            "verifier_bound": True,
            "consumer_bound": True,
        },
        "flow": {
            "active_claims": [],
            "unconsumed_terminals": 0,
            "pending_verifiers": 0,
            "pending_consumer_acks": 0,
            "recent_launches": [],
            "repeated_failures": [],
            "provider_state": {"provider": "cloudflare-ai-gateway", "state": "READY"},
        },
    }


class HatchPressureGateTests(unittest.TestCase):
    def test_admits_quiet_twinling(self):
        out = evaluate(base_snapshot())
        self.assertEqual(out["decision"], "ADMIT")
        self.assertEqual(out["reason"], "ADMIT_HATCH")

    def test_duplicate_active_semantic_work_holds(self):
        s = base_snapshot()
        s["flow"]["active_claims"] = [{"semantic_key": "crown:trafficflow:canary"}]
        self.assertEqual(evaluate(s)["reason"], "HOLD_DUPLICATE_ACTIVE_SEMANTIC_WORK")

    def test_wip_limit_holds(self):
        s = base_snapshot()
        s["flow"]["active_claims"] = [{"semantic_key": f"x:{i}"} for i in range(3)]
        self.assertEqual(evaluate(s)["reason"], "HOLD_WIP_LIMIT")

    def test_unconsumed_terminal_backlog_holds(self):
        s = base_snapshot()
        s["flow"]["unconsumed_terminals"] = 2
        self.assertEqual(evaluate(s)["reason"], "HOLD_UNCONSUMED_TERMINAL_BACKLOG")

    def test_pending_fanin_holds(self):
        s = base_snapshot()
        s["flow"]["pending_verifiers"] = 2
        s["flow"]["pending_consumer_acks"] = 1
        self.assertEqual(evaluate(s)["reason"], "HOLD_FANIN_BACKLOG")

    def test_provider_throttle_holds(self):
        s = base_snapshot()
        s["flow"]["provider_state"] = {
            "provider": "cloudflare-ai-gateway", "state": "THROTTLED", "retry_after_seconds": 900
        }
        self.assertEqual(evaluate(s)["reason"], "HOLD_PROVIDER_THROTTLED")

    def test_unknown_provider_holds(self):
        s = base_snapshot()
        s["flow"]["provider_state"]["state"] = "UNKNOWN"
        self.assertEqual(evaluate(s)["reason"], "HOLD_PROVIDER_UNKNOWN")

    def test_recent_duplicate_holds(self):
        s = base_snapshot()
        s["flow"]["recent_launches"] = [{"semantic_key": "crown:trafficflow:canary", "age_minutes": 42}]
        self.assertEqual(evaluate(s)["reason"], "HOLD_RECENT_DUPLICATE_SEMANTIC_WORK")

    def test_launch_burst_holds(self):
        s = base_snapshot()
        s["flow"]["recent_launches"] = [
            {"semantic_key": f"other:{i}", "age_minutes": 5 + i} for i in range(4)
        ]
        self.assertEqual(evaluate(s)["reason"], "HOLD_HATCH_BURST")

    def test_repeat_failure_without_mutation_holds(self):
        s = base_snapshot()
        s["flow"]["repeated_failures"] = [{
            "semantic_key": "crown:trafficflow:canary", "fingerprint": "abc", "count": 2,
            "strategy_changed": False,
        }]
        self.assertEqual(evaluate(s)["reason"], "HOLD_REPEATED_FAILURE_WITHOUT_MUTATION")

    def test_strategy_change_allows_recovery(self):
        s = base_snapshot()
        s["flow"]["repeated_failures"] = [{
            "semantic_key": "crown:trafficflow:canary", "fingerprint": "abc", "count": 4,
            "strategy_changed": True,
        }]
        self.assertEqual(evaluate(s)["decision"], "ADMIT")

    def test_missing_verifier_holds(self):
        s = base_snapshot()
        s["requested"]["verifier_bound"] = False
        self.assertEqual(evaluate(s)["reason"], "HOLD_VERIFIER_UNBOUND")

    def test_missing_consumer_holds(self):
        s = base_snapshot()
        s["requested"]["consumer_bound"] = False
        self.assertEqual(evaluate(s)["reason"], "HOLD_CONSUMER_UNBOUND")

    def test_tao_hot_loop_holds(self):
        s = base_snapshot()
        s["requested"]["tao_hot_loop_required"] = True
        self.assertEqual(evaluate(s)["reason"], "HOLD_OPERATOR_RUNTIME")

    def test_formation_count_mismatch_holds(self):
        s = base_snapshot()
        s["requested"]["count"] = 7
        self.assertEqual(evaluate(s)["reason"], "HATCH_REQUEST_INVALID")


if __name__ == "__main__":
    unittest.main()
