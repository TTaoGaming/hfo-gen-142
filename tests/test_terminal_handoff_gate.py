import unittest
from tools import terminal_handoff_gate as gate


class TerminalHandoffGateTests(unittest.TestCase):
    def receipt(self, *, owner="github-actions", work_ref="github:TTaoGaming/hfo-gen-142#13/item-B", status="ACCEPTED", self_attested=False):
        return {
            "receipt_type": "github_actions_run",
            "owner": owner,
            "receipt_id": "34899999999",
            "status": status,
            "observed_utc": "2026-09-14T21:20:00Z",
            "provenance_ref": "https://github.com/TTaoGaming/hfo-gen-142/actions/runs/34899999999",
            "receipt_sha256": "a" * 64,
            "self_attested": self_attested,
            "work_ref": work_ref,
        }

    def base(self):
        work_ref = "github:TTaoGaming/hfo-gen-142#13/item-B"
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
                "work_ref": work_ref,
                "dispatch_receipt": self.receipt(work_ref=work_ref),
            },
        }

    def armed_resume(self):
        return {
            "owner": "github-actions",
            "resume_condition": "secret_present:SVA_TOKEN",
            "watch_ref": "github:TTaoGaming/cdev-control/actions/workflows/gen142-autocell-r0.yml",
            "resume_receipt": {
                "receipt_type": "github_actions_watch",
                "owner": "github-actions",
                "receipt_id": "gen142-autocell-r0",
                "status": "ARMED",
                "observed_utc": "2026-09-14T21:20:00Z",
                "provenance_ref": "https://github.com/TTaoGaming/cdev-control/actions/workflows/gen142-autocell-r0.yml",
                "receipt_sha256": "b" * 64,
                "self_attested": False,
            },
        }

    def test_structured_auto_dispatch_passes(self):
        self.assertEqual(gate.evaluate(self.base()), 0)

    def test_string_receipt_reward_hack_fails(self):
        d = self.base()
        d["next"]["dispatch_receipt"] = "actions-run:123"
        self.assertNotEqual(gate.evaluate(d), 0)

    def test_self_attested_transition_fails(self):
        d = self.base()
        d["next"]["dispatch_receipt"]["self_attested"] = True
        self.assertNotEqual(gate.evaluate(d), 0)

    def test_receipt_work_ref_mismatch_fails(self):
        d = self.base()
        d["next"]["dispatch_receipt"]["work_ref"] = "github:wrong/item-C"
        self.assertNotEqual(gate.evaluate(d), 0)

    def test_auto_dispatch_cannot_only_be_armed(self):
        d = self.base()
        d["next"]["dispatch_receipt"]["status"] = "ARMED"
        self.assertNotEqual(gate.evaluate(d), 0)

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

    def test_secret_boundary_without_auto_resume_fails(self):
        d = self.base()
        action = "Provision SVA_TOKEN in approved secret store"
        d.update({
            "tao_relay_required": True,
            "human_boundary": "secret",
            "operator_action_required": action,
            "human_boundary_evidence": {
                "target": "cdev-control Actions secret store",
                "machine_attempt_ref": "actions-run:34889286895/SVA_TOKEN_MISSING",
                "why_human_only": "secret write authority is not delegated",
                "minimal_action": action,
            },
            "next": {"mode": "HUMAN_BOUNDARY"},
        })
        self.assertNotEqual(gate.evaluate(d), 0)

    def test_secret_boundary_with_armed_resume_passes(self):
        d = self.base()
        action = "Provision SVA_TOKEN in approved secret store"
        d.update({
            "tao_relay_required": True,
            "human_boundary": "secret",
            "operator_action_required": action,
            "human_boundary_evidence": {
                "target": "cdev-control Actions secret store",
                "machine_attempt_ref": "actions-run:34889286895/SVA_TOKEN_MISSING",
                "why_human_only": "secret write authority is not delegated",
                "minimal_action": action,
            },
            "next": {"mode": "HUMAN_BOUNDARY", "resume": self.armed_resume()},
        })
        self.assertEqual(gate.evaluate(d), 0)

    def test_human_boundary_cannot_hide_operator_work(self):
        d = self.base()
        action = "Tao launch next agent after approving permission"
        d.update({
            "tao_relay_required": True,
            "human_boundary": "permission",
            "operator_action_required": action,
            "human_boundary_evidence": {
                "target": "protected workflow",
                "machine_attempt_ref": "github:blocked",
                "why_human_only": "protected permission",
                "minimal_action": action,
            },
            "next": {"mode": "HUMAN_BOUNDARY", "resume": self.armed_resume()},
        })
        self.assertNotEqual(gate.evaluate(d), 0)

    def test_reconcile_requires_structured_receipt(self):
        d = self.base()
        d["next"] = {"mode": "RECONCILE", "owner": "github-actions", "dispatch_receipt": "watcher-armed"}
        self.assertNotEqual(gate.evaluate(d), 0)

    def test_mission_complete_requires_evidence(self):
        d = self.base()
        d["next"] = {"mode": "MISSION_COMPLETE"}
        d["mission_complete"] = True
        self.assertNotEqual(gate.evaluate(d), 0)


if __name__ == "__main__":
    unittest.main()
