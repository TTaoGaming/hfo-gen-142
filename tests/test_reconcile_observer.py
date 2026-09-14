import unittest
from datetime import datetime, timedelta, timezone

from tools import reconcile_kernel as rk
from tools import reconcile_observer as ro


class TrustedObserverTests(unittest.TestCase):
    def now(self):
        return datetime(2026, 9, 14, 22, 0, tzinfo=timezone.utc)

    def receipt(self, *, age=0, self_attested=False):
        t = self.now() - timedelta(seconds=age)
        return {
            "source_ref": "https://authority.example/fixed",
            "body_sha256": "a" * 64,
            "observed_at": ro.iso_utc(t),
            "self_attested": self_attested,
        }

    def cf(self, phase="IDLE"):
        return {
            "actor": "SIGRUN/C2",
            "phase": phase,
            "mission": None,
            "worker_job": None,
        }

    def build(self, **overrides):
        args = {
            "cf_state": self.cf(),
            "demand_rows": [],
            "comments": [],
            "route_pr": {"merged": False},
            "latest_route_run": None,
            "receipts": [self.receipt()],
            "now": self.now(),
        }
        args.update(overrides)
        return ro.build_snapshot(**args)

    def test_caller_metadata_cannot_self_declare_authority(self):
        with self.assertRaisesRegex(ro.ObservationError, "OBSERVATION_SELF_ATTESTED"):
            self.build(receipts=[self.receipt(self_attested=True)])

    def test_stale_readback_holds_before_kernel(self):
        with self.assertRaisesRegex(ro.ObservationError, "OBSERVATION_STALE"):
            self.build(receipts=[self.receipt(age=ro.MAX_OBSERVATION_AGE_SECONDS + 1)])

    def test_wrong_cloudflare_actor_identity_is_refused(self):
        bad = self.cf()
        bad["actor"] = "caller-supplied-fake"
        with self.assertRaisesRegex(ro.ObservationError, "CLOUDFLARE_ACTOR_IDENTITY_INVALID"):
            self.build(cf_state=bad)

    def test_unmerged_route_is_not_admitted(self):
        cf = self.cf("WAITING_WORKER")
        cf["mission"] = {"workitem_id": "W1"}
        cf["worker_job"] = {"job_id": "abc"}
        snap = self.build(cf_state=cf, route_pr={"merged": False})
        self.assertEqual(snap["worker_routes"], [])
        result = rk.evaluate(snap)
        self.assertEqual(result["action"]["kind"], "WAIT_WORKER_DEADLINE")

    def test_live_route_requires_merged_pr_and_fresh_success_on_main(self):
        cf = self.cf("WAITING_WORKER")
        cf["mission"] = {"workitem_id": "W1"}
        cf["worker_job"] = {"job_id": "abc"}
        run = {
            "conclusion": "success",
            "head_branch": "main",
            "updated_at": ro.iso_utc(self.now() - timedelta(minutes=5)),
        }
        snap = self.build(cf_state=cf, route_pr={"merged": True}, latest_route_run=run)
        self.assertEqual(
            snap["worker_routes"],
            [{"route_id": ro.ROUTE_ID, "live": True, "admitted": True}],
        )
        result = rk.evaluate(snap)
        self.assertEqual(result["action"]["kind"], "DISPATCH_WORKER")
        self.assertEqual(result["action"]["route_id"], ro.ROUTE_ID)

    def test_terminal_is_not_silently_marked_consumed(self):
        cf = self.cf("TERMINAL")
        cf["mission"] = {"workitem_id": "W0"}
        snap = self.build(cf_state=cf)
        self.assertFalse(snap["actor"]["terminal_consumed"])
        result = rk.evaluate(snap)
        self.assertEqual(result["action"]["kind"], "CONSUME_TERMINAL")

    def test_github_consumer_ack_marker_retires_exact_task_revision(self):
        body = b'{"schema":"hfo.research-workitem.v1"}'
        row = {
            "work_id": "GEN142-X",
            "path": "WORKCELLS/research-r0/x.json",
            "priority": 50,
            "admitted": True,
            "blocked": False,
            "spec_sha256": ro.sha256_bytes(body),
        }
        marker = f"<!-- hfo-research-cell-r0:{row['work_id']}:{row['spec_sha256']} -->"
        snap = self.build(demand_rows=[row], comments=[{"body": marker}])
        self.assertTrue(snap["demand"][0]["blocked"])
        result = rk.evaluate(snap)
        self.assertEqual(result["decision"], "IDLE")

    def test_only_fixed_dispatch_markers_create_active_dispatch(self):
        comments = [
            {"body": "I think dispatch foo is active"},
            {"body": "<!-- hfo-reconcile-dispatch:actions:123:ACTIVE -->"},
            {"body": "<!-- hfo-reconcile-dispatch:actions:456:ACTIVE -->"},
            {"body": "<!-- hfo-reconcile-dispatch:actions:123:TERMINAL -->"},
        ]
        snap = self.build(comments=comments)
        self.assertEqual(snap["dispatches"], [{"active": True, "dispatch_ref": "actions:456"}])

    def test_observer_has_no_caller_authority_url_argument(self):
        parser_exit = None
        try:
            ro.main(["--cloudflare-url", "https://evil.example/status", "out.json"])
        except SystemExit as exc:
            parser_exit = exc.code
        self.assertEqual(parser_exit, 2)

    def test_snapshot_replay_is_deterministic(self):
        a = self.build()
        b = self.build()
        self.assertEqual(a, b)
        self.assertEqual(rk.evaluate(a), rk.evaluate(b))


if __name__ == "__main__":
    unittest.main()
