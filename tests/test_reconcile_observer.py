import copy
import json
import unittest
from datetime import datetime, timezone

from tools import reconcile_observer as ro


class FakeFetcher:
    def __init__(self, payloads):
        self.payloads = payloads
        self.calls = []

    def __call__(self, url, headers):
        self.calls.append((url, dict(headers)))
        return json.dumps(self.payloads[url], sort_keys=True).encode()


class TrustedObserverTests(unittest.TestCase):
    def urls(self):
        return {
            "actor": "https://hfo-sigrun-va-r0.tommytai3.workers.dev/state",
            "demand": "https://api.github.com/repos/TTaoGaming/hfo-gen-142/contents/RECONCILE/demand.json",
            "dispatches": "https://api.github.com/repos/TTaoGaming/hfo-gen-142/actions/runs?event=workflow_dispatch",
            "worker_routes": "https://raw.githubusercontent.com/TTaoGaming/hfo-gen-142/main/RECONCILE/worker-routes.json",
            "human_boundary": "https://raw.githubusercontent.com/TTaoGaming/hfo-gen-142/main/RECONCILE/human-boundary.json",
        }

    def source_doc(self):
        return {
            "schema": ro.SOURCE_SCHEMA,
            "sources": [
                {"kind": kind, "url": url, "pointer": ["data"]}
                for kind, url in self.urls().items()
            ],
        }

    def payloads(self):
        return {
            self.urls()["actor"]: {"data": {
                "owner": "evil-self-claim",
                "phase": "IDLE",
                "workitem_id": None,
                "worker_job_available": False,
                "terminal_consumed": True,
                "terminal_ref": None,
                "source_owner": "evil",
                "provenance_ref": "https://evil.invalid/fake",
                "self_attested": False,
                "source_receipt_sha256": "0" * 64,
            }},
            self.urls()["demand"]: {"data": [
                {
                    "work_ref": "github:TTaoGaming/hfo-gen-142#13:next",
                    "priority": 7,
                    "admitted": True,
                    "blocked": False,
                }
            ]},
            self.urls()["dispatches"]: {"data": []},
            self.urls()["worker_routes"]: {"data": []},
            self.urls()["human_boundary"]: {"data": {"active": False}},
        }

    def test_fake_payload_provenance_cannot_claim_authority(self):
        fetcher = FakeFetcher(self.payloads())
        now = datetime(2026, 9, 14, 22, 2, tzinfo=timezone.utc)
        result = ro.observe(self.source_doc(), fetcher=fetcher, now=now)
        self.assertEqual(result["decision"], "PASS")
        snapshot = result["snapshot"]
        self.assertEqual(snapshot["actor"]["owner"], "hfo-sigrun-va-r0")
        self.assertNotIn("source_owner", snapshot["actor"])
        self.assertNotIn("provenance_ref", snapshot["actor"])
        evidence = snapshot["observation"]["evidence"]["actor"]
        self.assertEqual(evidence["source_owner"], "hfo-sigrun-va-r0")
        self.assertEqual(evidence["provenance_ref"], self.urls()["actor"])
        self.assertFalse(evidence["self_attested"])
        self.assertNotEqual(evidence["provenance_ref"], "https://evil.invalid/fake")

    def test_untrusted_url_holds_before_fetch(self):
        doc = self.source_doc()
        doc["sources"][0]["url"] = "https://evil.invalid/state"
        fetcher = FakeFetcher({})
        result = ro.observe(doc, fetcher=fetcher)
        self.assertEqual(result["decision"], "HOLD")
        self.assertEqual(result["reason"], "UNTRUSTED_SOURCE_URL")
        self.assertEqual(fetcher.calls, [])

    def test_missing_required_source_holds(self):
        doc = self.source_doc()
        doc["sources"] = [x for x in doc["sources"] if x["kind"] != "dispatches"]
        result = ro.observe(doc, fetcher=FakeFetcher(self.payloads()))
        self.assertEqual(result["decision"], "HOLD")
        self.assertEqual(result["reason"], "REQUIRED_SOURCE_MISSING")
        self.assertEqual(result["missing"], ["dispatches"])

    def test_observed_snapshot_feeds_kernel(self):
        result = ro.observe(
            self.source_doc(),
            fetcher=FakeFetcher(self.payloads()),
            now=datetime(2026, 9, 14, 22, 2, tzinfo=timezone.utc),
        )
        self.assertEqual(result["decision"], "PASS")
        self.assertEqual(result["plan"]["decision"], "ACT")
        self.assertEqual(result["plan"]["action"]["kind"], "SUBMIT_NEXT")

    def test_observer_replay_is_deterministic_for_same_fetches_and_time(self):
        now = datetime(2026, 9, 14, 22, 2, tzinfo=timezone.utc)
        a = ro.observe(
            self.source_doc(),
            fetcher=FakeFetcher(copy.deepcopy(self.payloads())),
            now=now,
        )
        b = ro.observe(
            self.source_doc(),
            fetcher=FakeFetcher(copy.deepcopy(self.payloads())),
            now=now,
        )
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
