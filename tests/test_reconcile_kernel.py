import copy
import unittest
from tools import reconcile_kernel as rk


class ReconcileKernelTests(unittest.TestCase):
    def base(self):
        return {
            "schema": rk.SCHEMA,
            "policy_version": rk.POLICY_VERSION,
            "actor": {
                "owner": rk.ACTOR_OWNER,
                "phase": "IDLE",
                "workitem_id": None,
                "worker_job_available": False,
                "terminal_consumed": True,
                "terminal_ref": None,
            },
            "demand": [],
            "dispatches": [],
            "worker_routes": [],
            "human_boundary": {"active": False},
        }

    def test_idle_without_demand_does_not_invent_work(self):
        r = rk.evaluate(self.base())
        self.assertEqual(r["decision"], "IDLE")
        self.assertEqual(r["action"]["kind"], "NONE")
        self.assertFalse(r["tao_relay_required"])

    def test_highest_priority_admitted_demand_wins_deterministically(self):
        d = self.base()
        d["demand"] = [
            {"work_ref": "work:z", "priority": 10, "admitted": True, "blocked": False},
            {"work_ref": "work:b", "priority": 20, "admitted": True, "blocked": False},
            {"work_ref": "work:a", "priority": 20, "admitted": True, "blocked": False},
            {"work_ref": "work:blocked", "priority": 99, "admitted": True, "blocked": True},
            {"work_ref": "work:unadmitted", "priority": 100, "admitted": False, "blocked": False},
        ]
        r = rk.evaluate(d)
        self.assertEqual(r["action"]["kind"], "SUBMIT_NEXT")
        self.assertEqual(r["action"]["work_ref"], "work:a")

    def test_semantic_owner_phases_are_not_micromanaged(self):
        for phase in sorted(rk.ACTIVE_OWNER_PHASES):
            with self.subTest(phase=phase):
                d = self.base()
                d["actor"]["phase"] = phase
                r = rk.evaluate(d)
                self.assertEqual(r["action"]["kind"], "WAIT_ACTOR")
                self.assertFalse(r["tao_relay_required"])

    def test_waiting_worker_dispatches_one_live_admitted_route(self):
        d = self.base()
        d["actor"].update({"phase": "WAITING_WORKER", "workitem_id": "W1", "worker_job_available": True})
        d["worker_routes"] = [
            {"route_id": "z-route", "live": True, "admitted": True},
            {"route_id": "a-route", "live": True, "admitted": True},
            {"route_id": "bad", "live": False, "admitted": True},
        ]
        r = rk.evaluate(d)
        self.assertEqual(r["action"]["kind"], "DISPATCH_WORKER")
        self.assertEqual(r["action"]["route_id"], "a-route")

    def test_waiting_worker_without_route_waits_for_owner_deadline_not_tao(self):
        d = self.base()
        d["actor"].update({"phase": "WAITING_WORKER", "workitem_id": "W1", "worker_job_available": True})
        r = rk.evaluate(d)
        self.assertEqual(r["action"]["kind"], "WAIT_WORKER_DEADLINE")
        self.assertFalse(r["tao_relay_required"])

    def test_terminal_must_be_consumed_before_next_demand(self):
        d = self.base()
        d["actor"].update({"phase": "TERMINAL", "workitem_id": "W0", "terminal_consumed": False, "terminal_ref": "sigrun-history:W0"})
        d["demand"] = [{"work_ref": "work:next", "priority": 10, "admitted": True, "blocked": False}]
        r = rk.evaluate(d)
        self.assertEqual(r["action"]["kind"], "CONSUME_TERMINAL")
        self.assertEqual(r["action"]["workitem_id"], "W0")

    def test_active_dispatch_suppresses_duplicate_dispatch(self):
        d = self.base()
        d["dispatches"] = [{"active": True, "dispatch_ref": "actions-run:123"}]
        d["demand"] = [{"work_ref": "work:next", "priority": 10, "admitted": True, "blocked": False}]
        r = rk.evaluate(d)
        self.assertEqual(r["action"]["kind"], "WAIT_DISPATCH")

    def test_multiple_active_dispatches_fail_closed(self):
        d = self.base()
        d["dispatches"] = [
            {"active": True, "dispatch_ref": "A"},
            {"active": True, "dispatch_ref": "B"},
        ]
        r = rk.evaluate(d)
        self.assertEqual(r["decision"], "HOLD")
        self.assertEqual(r["reason"], "DUPLICATE_ACTIVE_DISPATCH")

    def test_human_boundary_requires_machine_resume_armed(self):
        d = self.base()
        d["human_boundary"] = {
            "active": True,
            "type": "secret",
            "minimal_action": "Provision SVA_TOKEN in approved secret store",
            "resume_armed": False,
            "watch_ref": None,
        }
        r = rk.evaluate(d)
        self.assertEqual(r["decision"], "HOLD")
        self.assertEqual(r["reason"], "HUMAN_BOUNDARY_RESUME_NOT_ARMED")
        self.assertFalse(r["tao_relay_required"])

    def test_human_unlock_never_requires_human_restart(self):
        d = self.base()
        d["human_boundary"] = {
            "active": True,
            "type": "secret",
            "minimal_action": "Provision SVA_TOKEN in approved secret store",
            "resume_armed": True,
            "watch_ref": "github-actions-watch:gen142-autocell-r0",
        }
        r = rk.evaluate(d)
        self.assertEqual(r["action"]["kind"], "WAIT_HUMAN_UNLOCK")
        self.assertTrue(r["tao_relay_required"])
        self.assertNotIn("restart", r["operator_action_required"].lower())
        self.assertNotIn("retry", r["operator_action_required"].lower())

    def test_replay_is_deterministic(self):
        d = self.base()
        d["demand"] = [{"work_ref": "work:1", "priority": 1, "admitted": True, "blocked": False}]
        a = rk.evaluate(copy.deepcopy(d))
        b = rk.evaluate(copy.deepcopy(d))
        self.assertEqual(a, b)
        self.assertEqual(a["snapshot_sha256"], b["snapshot_sha256"])
        self.assertEqual(a["plan_sha256"], b["plan_sha256"])


if __name__ == "__main__":
    unittest.main()
