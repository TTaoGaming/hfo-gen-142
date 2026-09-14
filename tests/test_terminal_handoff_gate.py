import unittest
from tools import terminal_handoff_gate as gate


class TerminalHandoffGateTests(unittest.TestCase):
    def base(self):
        return {
            "schema": gate.SCHEMA,
            "mission_id": "M1",
            "actor_id": "A1",
            "terminal_state": "PASS",
            "tao_relay_required": False,
            "operator_action_required": "NONE",
            "next": {
                "mode": "AUTO_DISPATCH",
                "owner": "github-actions",
                "work_ref": "github:TTaoGaming/hfo-gen-142#13/item-B",
                "dispatch_receipt": "actions-run:123",
            },
        }

    def test_auto_dispatch_passes(self):
        self.assertEqual(gate.evaluate(self.base()), 0)

    def test_tao_hot_loop_fails(self):
        d = self.base()
        d["operator_action_required"] = "Tao launch next agent"
        self.assertNotEqual(gate.evaluate(d), 0)

    def test_unbounded_human_relay_fails(self):
        d = self.base()
        d["tao_relay_required"] = True
        d["human_boundary"] = "decision"
        d["operator_action_required"] = "Tao decide"
        d["next"] = {"mode": "HUMAN_BOUNDARY"}
        self.assertNotEqual(gate.evaluate(d), 0)

    def test_named_secret_boundary_passes(self):
        d = self.base()
        d["tao_relay_required"] = True
        d["human_boundary"] = "secret"
        d["operator_action_required"] = "Provision SVA_TOKEN in approved secret store"
        d["next"] = {"mode": "HUMAN_BOUNDARY"}
        self.assertEqual(gate.evaluate(d), 0)

    def test_reconcile_requires_receipt(self):
        d = self.base()
        d["next"] = {"mode": "RECONCILE", "owner": "github-actions"}
        self.assertNotEqual(gate.evaluate(d), 0)

    def test_mission_complete_requires_evidence(self):
        d = self.base()
        d["next"] = {"mode": "MISSION_COMPLETE"}
        d["mission_complete"] = True
        self.assertNotEqual(gate.evaluate(d), 0)


if __name__ == "__main__":
    unittest.main()
