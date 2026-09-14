import json
import tempfile
import unittest
from pathlib import Path

from tools import reconcile_observer as ro


class ReconcileObserverTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.task_dir = Path(self.tmp.name)
        self.task = {
            "schema": "hfo.research-workitem.v1",
            "work_id": "OBS-1",
            "priority": 7,
            "admitted": True,
            "blocked": False,
        }
        self.task_path = self.task_dir / "task.json"
        self.task_path.write_text(json.dumps(self.task, indent=2), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def actor(self, phase="IDLE", workitem_id=None):
        return {
            "actor": ro.ACTOR_ID,
            "phase": phase,
            "mission": None if workitem_id is None else {"workitem_id": workitem_id},
            "worker_job": None,
        }

    def derive(self, actor=None, comments=None, runs=None):
        return ro.derive_snapshot(
            actor_status=actor or self.actor(),
            comments=comments or [],
            workflow_runs={"workflow_runs": runs or []},
            task_dir=self.task_dir,
            fetched_utc="2026-09-14T22:10:00Z",
            source_hashes={"actor": "a" * 64, "comments": "b" * 64, "runs": "c" * 64},
            repo_commit="d" * 40,
        )

    def test_fixed_source_provenance_ignores_payload_claims(self):
        actor = self.actor()
        actor.update({"source_ref": "evil://caller", "self_attested": False, "payload_sha256": "0" * 64})
        snapshot = self.derive(actor=actor)
        source = snapshot["observation"]["sources"]["actor"]
        self.assertEqual(source["ref"], ro.ACTOR_STATUS_URL)
        self.assertNotIn("evil://caller", json.dumps(snapshot))
        self.assertNotIn("self_attested", json.dumps(snapshot))

    def test_idle_actor_with_admitted_demand_produces_submit_next(self):
        snapshot = self.derive()
        plan = ro.rk.evaluate(snapshot)
        self.assertEqual(plan["decision"], "ACT")
        self.assertEqual(plan["action"]["kind"], "SUBMIT_NEXT")
        self.assertEqual(plan["action"]["priority"], 7)

    def test_waiting_worker_without_authoritative_route_waits(self):
        actor = self.actor("WAITING_WORKER", "W1")
        actor["worker_job"] = {"job_id": "J1"}
        snapshot = self.derive(actor=actor)
        plan = ro.rk.evaluate(snapshot)
        self.assertTrue(snapshot["actor"]["worker_job_available"])
        self.assertEqual(snapshot["worker_routes"], [])
        self.assertEqual(plan["action"]["kind"], "WAIT_WORKER_DEADLINE")

    def test_duplicate_authoritative_active_runs_fail_closed(self):
        runs = [
            {"id": 10, "status": "in_progress"},
            {"id": 11, "status": "queued"},
        ]
        snapshot = self.derive(runs=runs)
        plan = ro.rk.evaluate(snapshot)
        self.assertEqual(plan["decision"], "HOLD")
        self.assertEqual(plan["reason"], "DUPLICATE_ACTIVE_DISPATCH")

    def test_actor_identity_mismatch_is_refused(self):
        actor = self.actor()
        actor["actor"] = "caller-claimed-owner"
        with self.assertRaisesRegex(ro.ObservationHold, "ACTOR_IDENTITY_REFUSED"):
            self.derive(actor=actor)

    def test_terminal_is_not_silently_marked_consumed(self):
        snapshot = self.derive(actor=self.actor("TERMINAL", "W0"))
        plan = ro.rk.evaluate(snapshot)
        self.assertFalse(snapshot["actor"]["terminal_consumed"])
        self.assertEqual(plan["action"]["kind"], "CONSUME_TERMINAL")
        self.assertTrue(snapshot["actor"]["terminal_ref"].endswith("/history/W0"))

    def test_retirement_marker_removes_demand(self):
        raw = self.task_path.read_bytes()
        marker = f"<!-- hfo-research-cell-r0:OBS-1:{ro.sha256_bytes(raw)} -->"
        snapshot = self.derive(comments=[{"body": "done\n" + marker}])
        self.assertEqual(snapshot["demand"], [])
        plan = ro.rk.evaluate(snapshot)
        self.assertEqual(plan["decision"], "IDLE")


if __name__ == "__main__":
    unittest.main()
