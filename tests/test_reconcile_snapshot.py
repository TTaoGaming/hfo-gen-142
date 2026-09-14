import copy
import hashlib
import unittest

from tools import reconcile_kernel as rk
from tools import reconcile_snapshot as rs


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


class ReconcileSnapshotTests(unittest.TestCase):
    def base(self):
        observed = "2026-09-14T21:50:00Z"
        return {
            "schema": rs.INPUT_SCHEMA,
            "policy_version": rs.POLICY_VERSION,
            "snapshot_observed_utc": observed,
            "max_age_seconds": 300,
            "observations": [
                {
                    "kind": "actor",
                    "source_owner": "hfo-sigrun-va-r0",
                    "observed_utc": observed,
                    "provenance_ref": "sigrun-history:W0",
                    "source_receipt_sha256": sha("actor"),
                    "self_attested": False,
                    "data": {
                        "owner": rk.ACTOR_OWNER,
                        "phase": "IDLE",
                        "workitem_id": None,
                        "worker_job_available": False,
                        "terminal_consumed": True,
                        "terminal_ref": None,
                    },
                },
                {
                    "kind": "demand",
                    "source_owner": "github",
                    "observed_utc": observed,
                    "provenance_ref": "github:TTaoGaming/hfo-gen-142#13",
                    "source_receipt_sha256": sha("demand"),
                    "self_attested": False,
                    "data": [],
                },
                {
                    "kind": "dispatches",
                    "source_owner": "github-actions",
                    "observed_utc": observed,
                    "provenance_ref": "github:TTaoGaming/cdev-control/actions/runs/1",
                    "source_receipt_sha256": sha("dispatches"),
                    "self_attested": False,
                    "data": [],
                },
                {
                    "kind": "worker_routes",
                    "source_owner": "github",
                    "observed_utc": observed,
                    "provenance_ref": "github:TTaoGaming/hfo-gen-142/worker-routes",
                    "source_receipt_sha256": sha("routes"),
                    "self_attested": False,
                    "data": [],
                },
                {
                    "kind": "human_boundary",
                    "source_owner": "github-actions",
                    "observed_utc": observed,
                    "provenance_ref": "github:TTaoGaming/cdev-control/actions/workflows/gen142-autocell-r0.yml",
                    "source_receipt_sha256": sha("boundary"),
                    "self_attested": False,
                    "data": {"active": False},
                },
            ],
        }

    def observation(self, doc, kind):
        return next(x for x in doc["observations"] if x["kind"] == kind)

    def test_assembles_snapshot_accepted_by_kernel(self):
        result = rs.assemble(self.base())
        self.assertEqual(result["decision"], "PASS")
        snap = result["snapshot"]
        self.assertEqual(snap["schema"], rk.SCHEMA)
        self.assertEqual(snap["policy_version"], rk.POLICY_VERSION)
        self.assertIn("observation", snap)
        plan = rk.evaluate(snap)
        self.assertEqual(plan["decision"], "IDLE")
        self.assertEqual(plan["reason"], "NO_ADMITTED_DEMAND")

    def test_self_attested_observation_fails_closed(self):
        d = self.base()
        self.observation(d, "actor")["self_attested"] = True
        r = rs.assemble(d)
        self.assertEqual(r["decision"], "HOLD")
        self.assertEqual(r["reason"], "SELF_ATTESTED_OBSERVATION_FORBIDDEN")

    def test_stale_observation_fails_closed(self):
        d = self.base()
        self.observation(d, "demand")["observed_utc"] = "2026-09-14T21:40:00Z"
        r = rs.assemble(d)
        self.assertEqual(r["decision"], "HOLD")
        self.assertEqual(r["reason"], "STALE_OBSERVATION")
        self.assertEqual(r["kind"], "demand")

    def test_duplicate_kind_fails_closed(self):
        d = self.base()
        d["observations"].append(copy.deepcopy(self.observation(d, "actor")))
        r = rs.assemble(d)
        self.assertEqual(r["decision"], "HOLD")
        self.assertEqual(r["reason"], "DUPLICATE_OBSERVATION_KIND")

    def test_missing_kind_fails_closed(self):
        d = self.base()
        d["observations"] = [x for x in d["observations"] if x["kind"] != "dispatches"]
        r = rs.assemble(d)
        self.assertEqual(r["decision"], "HOLD")
        self.assertEqual(r["reason"], "REQUIRED_OBSERVATION_MISSING")
        self.assertEqual(r["missing"], ["dispatches"])

    def test_wrong_source_owner_fails_closed(self):
        d = self.base()
        self.observation(d, "actor")["source_owner"] = "github"
        r = rs.assemble(d)
        self.assertEqual(r["decision"], "HOLD")
        self.assertEqual(r["reason"], "SOURCE_OWNER_INVALID")

    def test_invalid_receipt_hash_fails_closed(self):
        d = self.base()
        self.observation(d, "worker_routes")["source_receipt_sha256"] = "not-a-hash"
        r = rs.assemble(d)
        self.assertEqual(r["decision"], "HOLD")
        self.assertEqual(r["reason"], "SOURCE_RECEIPT_SHA256_INVALID")

    def test_replay_is_deterministic(self):
        d = self.base()
        a = rs.assemble(copy.deepcopy(d))
        b = rs.assemble(copy.deepcopy(d))
        self.assertEqual(a, b)
        self.assertEqual(a["snapshot_sha256"], b["snapshot_sha256"])


if __name__ == "__main__":
    unittest.main()
