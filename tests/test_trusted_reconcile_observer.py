import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from tools import trusted_reconcile_observer as tro


NOW = datetime(2026, 9, 14, 22, 10, tzinfo=timezone.utc)
SHA = "a" * 40


def iso(dt):
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def rb(name, payload, *, when=NOW, url=None):
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return tro.Readback(
        name=name,
        url=url or tro.AUTHORITY_URLS[name],
        observed_utc=iso(when),
        server_date_utc=iso(when),
        body_sha256=hashlib.sha256(raw).hexdigest(),
        payload=payload,
    )


class FakeReader:
    def __init__(self, *, actor_phase="IDLE", runner_id=7, merged=True, active_runs=None, stale=None, bad_url=None, fail=None):
        mission = None
        worker_job = None
        if actor_phase == "WAITING_WORKER":
            mission = {"workitem_id": "W-1"}
            worker_job = {"job_id": "job-1"}
        self.rows = {
            "cf_health": rb("cf_health", {"ok": True, "actor": "SIGRUN/C2", "mode": "TEXT_WORKER_R1", "effect_ceiling": "NONE"}),
            "cf_status": rb("cf_status", {"actor": "SIGRUN/C2", "phase": actor_phase, "mission": mission, "worker_job": worker_job, "ack": None}),
            "gh_main": rb("gh_main", {"commit": {"sha": SHA}}),
            "gh_runs": rb("gh_runs", {"workflow_runs": active_runs or []}),
            "cdev_pr": rb("cdev_pr", {"number": 5, "state": "closed" if merged else "open", "merged_at": "2026-09-14T22:00:00Z" if merged else None}),
            "cdev_runners": rb("cdev_runners", {"runners": [{"id": runner_id, "status": "online", "busy": False, "labels": [{"name": "self-hosted"}]}]}),
        }
        self.comment_rows = [rb("gh_comments", [])]
        if stale:
            old = NOW - timedelta(seconds=tro.MAX_RESPONSE_AGE_SECONDS + 1)
            prior = self.rows[stale]
            self.rows[stale] = tro.Readback(prior.name, prior.url, iso(old), iso(old), prior.body_sha256, prior.payload)
        if bad_url:
            prior = self.rows[bad_url]
            self.rows[bad_url] = tro.Readback(prior.name, "https://example.invalid/fake", prior.observed_utc, prior.server_date_utc, prior.body_sha256, prior.payload)
        self.fail = fail

    def read(self, name):
        if name == self.fail:
            raise tro.AuthorityHold("SVA_TOKEN_MISSING")
        return self.rows[name]

    def comments(self):
        return self.comment_rows


class TrustedObserverTests(unittest.TestCase):
    def task_dir(self, retired=False):
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        task = {
            "schema": "hfo.research-workitem.v1",
            "work_id": "GEN142-TEST-OBSERVE-1",
            "priority": 9,
            "admitted": True,
        }
        raw = (json.dumps(task, indent=2) + "\n").encode()
        path = root / "task.json"
        path.write_bytes(raw)
        marker = f"<!-- hfo-research-cell-r0:{task['work_id']}:{hashlib.sha256(raw).hexdigest()} -->"
        return tmp, root, marker if retired else None

    def test_caller_cannot_supply_authority_or_provenance(self):
        result = tro.observe(
            FakeReader(), now=NOW, canonical_sha=SHA,
            caller_authority={"cf_status_url": "https://evil.invalid/status", "self_attested": False},
        )
        self.assertEqual(result["status"], "HOLD")
        self.assertEqual(result["reason"], "CALLER_AUTHORITY_OVERRIDE_REFUSED")
        self.assertEqual(result["sources"], [])

    def test_redirect_or_wrong_authority_url_holds(self):
        result = tro.observe(FakeReader(bad_url="cf_status"), now=NOW, canonical_sha=SHA)
        self.assertEqual(result["status"], "HOLD")
        self.assertEqual(result["reason"], "AUTHORITY_URL_MISMATCH")

    def test_stale_readback_holds(self):
        result = tro.observe(FakeReader(stale="gh_main"), now=NOW, canonical_sha=SHA)
        self.assertEqual(result["status"], "HOLD")
        self.assertEqual(result["reason"], "STALE_READBACK")
        self.assertEqual(result["source"], "gh_main")

    def test_missing_actor_capability_holds_without_fake_snapshot(self):
        result = tro.observe(FakeReader(fail="cf_status"), now=NOW, canonical_sha=SHA)
        self.assertEqual(result["status"], "HOLD")
        self.assertEqual(result["reason"], "SVA_TOKEN_MISSING")
        self.assertNotIn("snapshot", result)

    def test_checkout_must_equal_authoritative_main(self):
        result = tro.observe(FakeReader(), now=NOW, canonical_sha="b" * 40)
        self.assertEqual(result["status"], "HOLD")
        self.assertEqual(result["reason"], "CHECKOUT_NOT_CANONICAL_MAIN")

    def test_fixed_sources_derive_all_five_snapshot_fields(self):
        tmp, root, _ = self.task_dir()
        try:
            result = tro.observe(FakeReader(), now=NOW, canonical_sha=SHA, task_dir=root)
        finally:
            tmp.cleanup()
        self.assertEqual(result["status"], "SNAPSHOT")
        snapshot = result["snapshot"]
        self.assertEqual(set(snapshot), {"schema", "policy_version", "actor", "demand", "dispatches", "worker_routes", "human_boundary"})
        self.assertEqual(snapshot["actor"]["owner"], "hfo-sigrun-va-r0")
        self.assertEqual(len(snapshot["demand"]), 1)
        self.assertEqual(snapshot["worker_routes"][0]["route_id"], "cdev-control:runner:7")
        self.assertFalse(snapshot["human_boundary"]["active"])
        self.assertEqual(result["plan"]["action"]["kind"], "SUBMIT_NEXT")

    def test_controller_worker_replacement_changes_only_derived_route(self):
        tmp, root, marker = self.task_dir(retired=True)
        try:
            r1 = FakeReader(actor_phase="WAITING_WORKER", runner_id=7)
            r2 = FakeReader(actor_phase="WAITING_WORKER", runner_id=19)
            r1.comment_rows = [rb("gh_comments", [{"body": marker}])]
            r2.comment_rows = [rb("gh_comments", [{"body": marker}])]
            first = tro.observe(r1, now=NOW, canonical_sha=SHA, task_dir=root, current_run_id="100")
            second = tro.observe(r2, now=NOW, canonical_sha=SHA, task_dir=root, current_run_id="101")
        finally:
            tmp.cleanup()
        self.assertEqual(first["plan"]["action"]["kind"], "DISPATCH_WORKER")
        self.assertEqual(second["plan"]["action"]["kind"], "DISPATCH_WORKER")
        self.assertEqual(first["plan"]["action"]["route_id"], "cdev-control:runner:7")
        self.assertEqual(second["plan"]["action"]["route_id"], "cdev-control:runner:19")
        self.assertNotEqual(first["observation_sha256"], second["observation_sha256"])

    def test_unmerged_protected_transport_is_not_admitted(self):
        tmp, root, marker = self.task_dir(retired=True)
        try:
            reader = FakeReader(actor_phase="WAITING_WORKER", merged=False)
            reader.comment_rows = [rb("gh_comments", [{"body": marker}])]
            result = tro.observe(reader, now=NOW, canonical_sha=SHA, task_dir=root)
        finally:
            tmp.cleanup()
        self.assertEqual(result["status"], "SNAPSHOT")
        self.assertFalse(result["snapshot"]["worker_routes"][0]["admitted"])
        self.assertTrue(result["snapshot"]["human_boundary"]["active"])
        self.assertEqual(result["plan"]["decision"], "HOLD")
        self.assertEqual(result["plan"]["reason"], "HUMAN_BOUNDARY_RESUME_NOT_ARMED")


if __name__ == "__main__":
    unittest.main()
