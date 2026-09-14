import copy
import json
import os
import unittest
from datetime import datetime, timezone
from unittest.mock import patch

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
        return {kind: binding["url"] for kind, binding in ro.SOURCE_REGISTRY.items()}

    def source_doc(self):
        return {
            "schema": ro.SOURCE_SCHEMA,
            "sources": [{"kind": kind} for kind in ro.REQUIRED_KINDS],
        }

    def payloads(self):
        return {
            self.urls()["actor"]: {
                "actor": "SIGRUN/C2",
                "owner": "evil-self-claim",
                "phase": "IDLE",
                "mission": None,
                "mission_sha256": None,
                "fence": 7,
                "created_utc": "2026-09-14T21:00:00Z",
                "last_wake_utc": "2026-09-14T22:01:00Z",
                "terminal_utc": None,
                "alarm_at": None,
                "worker_deadline_at": None,
                "workitem_id": None,
                "worker_job_available": False,
                "terminal_consumed": True,
                "terminal_ref": None,
                "source_owner": "evil",
                "provenance_ref": "https://evil.invalid/fake",
                "self_attested": False,
                "source_receipt_sha256": "0" * 64,
            },
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

    def test_actor_registry_is_exact_authenticated_status(self):
        self.assertEqual(
            self.urls()["actor"],
            "https://hfo-sigrun-va-r0.tommytai3.workers.dev/status",
        )
        self.assertTrue(ro.trusted_registry_url("actor", self.urls()["actor"]))
        self.assertFalse(
            ro.trusted_registry_url(
                "actor", "https://hfo-sigrun-va-r0.tommytai3.workers.dev/health"
            )
        )
        self.assertFalse(
            ro.trusted_registry_url(
                "actor",
                "https://hfo-sigrun-va-r0.tommytai3.workers.dev/history/old-item",
            )
        )

    def test_missing_sva_token_holds_before_fetch(self):
        fetcher = FakeFetcher({})
        with patch.dict(os.environ, {}, clear=True):
            result = ro.observe(self.source_doc(), fetcher=fetcher)
        self.assertEqual(result["decision"], "HOLD")
        self.assertEqual(result["reason"], "HOLD_SECRET")
        self.assertEqual(result["secret"], "SVA_TOKEN")
        self.assertEqual(result["resume"], "existing_scheduled_wake")
        self.assertEqual(fetcher.calls, [])

    def test_fake_payload_provenance_cannot_claim_authority(self):
        fetcher = FakeFetcher(self.payloads())
        now = datetime(2026, 9, 14, 22, 2, tzinfo=timezone.utc)
        with patch.dict(os.environ, {"SVA_TOKEN": "test-sva"}, clear=False):
            result = ro.observe(self.source_doc(), fetcher=fetcher, now=now)
        self.assertEqual(result["decision"], "PASS")
        snapshot = result["snapshot"]
        self.assertEqual(snapshot["actor"]["owner"], "hfo-sigrun-va-r0")
        self.assertNotIn("source_owner", snapshot["actor"])
        self.assertNotIn("provenance_ref", snapshot["actor"])
        evidence = snapshot["observation"]["evidence"]["actor"]
        self.assertEqual(evidence["source_owner"], "hfo-sigrun-va-r0")
        self.assertEqual(evidence["provenance_ref"], self.urls()["actor"])
        self.assertEqual(evidence["source_native"]["fence"], 7)
        self.assertEqual(
            evidence["source_native"]["last_wake_utc"], "2026-09-14T22:01:00Z"
        )
        self.assertFalse(evidence["self_attested"])
        self.assertNotEqual(evidence["provenance_ref"], "https://evil.invalid/fake")
        actor_call = next(call for call in fetcher.calls if call[0] == self.urls()["actor"])
        self.assertEqual(actor_call[1]["Authorization"], "Bearer test-sva")

    def test_caller_selected_url_holds_before_fetch(self):
        doc = self.source_doc()
        doc["sources"][0]["url"] = "https://evil.invalid/state"
        fetcher = FakeFetcher({})
        result = ro.observe(doc, fetcher=fetcher)
        self.assertEqual(result["decision"], "HOLD")
        self.assertEqual(result["reason"], "CALLER_AUTHORITY_FORBIDDEN")
        self.assertEqual(fetcher.calls, [])

    def test_falsifier_three_semantic_forgeries_hold_before_kernel(self):
        forged = {
            "demand": {"data": [{
                "work_ref": "github:attacker/forged#1",
                "priority": 999,
                "admitted": True,
                "blocked": False,
            }]},
            "worker_routes": {"payload": [{
                "route_id": "attacker-route",
                "live": True,
                "admitted": True,
            }]},
            "human_boundary": {"data": {
                "active": True,
                "type": "permission",
                "minimal_action": "grant attacker",
                "resume_armed": True,
                "watch_ref": "attacker",
            }},
        }
        for kind, injected in forged.items():
            with self.subTest(kind=kind):
                doc = self.source_doc()
                spec = next(x for x in doc["sources"] if x["kind"] == kind)
                spec.update(injected)
                fetcher = FakeFetcher({})
                result = ro.observe(doc, fetcher=fetcher)
                self.assertEqual(result["decision"], "HOLD")
                self.assertEqual(result["reason"], "CALLER_AUTHORITY_FORBIDDEN")
                self.assertEqual(fetcher.calls, [])

    def test_caller_supplied_stale_observation_time_holds_before_fetch(self):
        doc = self.source_doc()
        doc["sources"][0]["observed_utc"] = "2000-01-01T00:00:00Z"
        fetcher = FakeFetcher({})
        result = ro.observe(doc, fetcher=fetcher)
        self.assertEqual(result["decision"], "HOLD")
        self.assertEqual(result["reason"], "CALLER_AUTHORITY_FORBIDDEN")
        self.assertEqual(fetcher.calls, [])

    def test_missing_required_source_holds(self):
        doc = self.source_doc()
        doc["sources"] = [x for x in doc["sources"] if x["kind"] != "dispatches"]
        result = ro.observe(doc, fetcher=FakeFetcher(self.payloads()))
        self.assertEqual(result["decision"], "HOLD")
        self.assertEqual(result["reason"], "REQUIRED_SOURCE_MISSING")
        self.assertEqual(result["missing"], ["dispatches"])

    def test_observed_snapshot_feeds_kernel(self):
        with patch.dict(os.environ, {"SVA_TOKEN": "test-sva"}, clear=False):
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
        with patch.dict(os.environ, {"SVA_TOKEN": "test-sva"}, clear=False):
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
