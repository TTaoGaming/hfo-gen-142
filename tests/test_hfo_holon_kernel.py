from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "tools" / "hfo_holon_kernel.py"
SPEC = importlib.util.spec_from_file_location("hfo_holon_kernel", MODULE)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)


def payload() -> dict:
    return {
        "actor": {"actor_id": "SIGRUN", "skills": [], "heritage_event_ids": []},
        "mission": {
            "mission_id": "M1",
            "objective": "bounded frontier canary",
            "frontier_required": True,
        },
        "carrier": {
            "carrier_episode_id": "E1",
            "provider": "KIMI_CODE",
            "model": "kimi-for-coding",
            "provider_tier": "FRONTIER",
            "qualification_receipts": ["receipt:kimi-live"],
        },
        "result": {
            "terminal_state": "TERMINAL_SUCCESS",
            "output_ref": "artifact:1",
            "output_sha256": "abc",
            "verifier_class": "FROZEN_MECHANICAL_VERIFIER",
            "verifier_pass": True,
            "verifier_receipt_ref": "verifier:1",
            "consumer_ack_ref": "ack:1",
            "observed_utc": "2026-09-14T19:00:00Z",
            "operator_touches": 0,
            "candidate_self_awarded": False,
        },
        "skill_candidate": {
            "skill_id": "carrier.frontier.exact-output",
            "skill_version": "v1",
            "donor_actor_id": "SIGRUN",
        },
    }


class HolonKernelTests(unittest.TestCase):
    def test_verified_effect_promotes_skill(self) -> None:
        out = mod.reduce_transition(payload())
        self.assertEqual(out["state"], "PROMOTE")
        self.assertTrue(out["next_mission_ready"])
        self.assertEqual(out["promoted_skill"]["skill_id"], "carrier.frontier.exact-output")
        self.assertTrue(out["heritage_event"]["event_id"].startswith("sha256:"))

    def test_frontier_mission_blocks_local_substitution(self) -> None:
        p = payload(); p["carrier"]["provider_tier"] = "LOCAL"
        out = mod.reduce_transition(p)
        self.assertEqual(out["code"], "BLOCK_FRONTIER_SUBSTITUTION")
        self.assertFalse(out["next_mission_ready"])

    def test_missing_verifier_blocks_promotion(self) -> None:
        p = payload(); p["result"]["verifier_pass"] = False
        out = mod.reduce_transition(p)
        self.assertEqual(out["code"], "BLOCK_UNVERIFIED_PROMOTION")
        self.assertFalse(out["promotion_allowed"])

    def test_missing_ack_blocks_next_mission(self) -> None:
        p = payload(); p["result"]["consumer_ack_ref"] = None
        out = mod.reduce_transition(p)
        self.assertEqual(out["code"], "BLOCK_MISSING_CONSUMER_ACK")
        self.assertFalse(out["next_mission_ready"])

    def test_failure_becomes_scar_not_skill(self) -> None:
        p = payload(); p["result"]["terminal_state"] = "TERMINAL_FAILURE"
        p["result"]["failure_ref"] = "failure:timeout"
        out = mod.reduce_transition(p)
        self.assertEqual(out["state"], "SCAR")
        self.assertFalse(out["promotion_allowed"])
        self.assertEqual(out["heritage_event"]["event_class"], "MISSION_SCAR")

    def test_self_award_is_denied(self) -> None:
        p = payload(); p["result"]["candidate_self_awarded"] = True
        out = mod.reduce_transition(p)
        self.assertEqual(out["code"], "BLOCK_SELF_AWARD")


    def test_replay_event_id_is_deterministic(self) -> None:
        first = mod.reduce_transition(payload())
        second = mod.reduce_transition(payload())
        self.assertEqual(first["heritage_event"]["event_id"], second["heritage_event"]["event_id"])

    def test_required_skill_survives_into_next_mission(self) -> None:
        first = mod.reduce_transition(payload())
        p = payload()
        p["actor"] = first["actor_state_patch"]
        p["mission"]["mission_id"] = "M2"
        p["mission"]["required_skills"] = [{"skill_id":"carrier.frontier.exact-output","skill_version":"v1"}]
        p["carrier"]["carrier_episode_id"] = "E2"
        p.pop("skill_candidate")
        out = mod.reduce_transition(p)
        self.assertEqual(out["state"], "PROMOTE")
        self.assertTrue(out["next_mission_ready"])
        self.assertEqual(len(out["actor_state_patch"]["heritage_event_ids"]), 2)

    def test_missing_required_skill_holds_before_effect(self) -> None:
        p = payload()
        p["mission"]["required_skills"] = [{"skill_id":"missing","skill_version":"v9"}]
        out = mod.reduce_transition(p)
        self.assertEqual(out["code"], "BLOCK_REQUIRED_SKILL_MISSING")

    def test_event_id_matches_immutable_event_payload(self) -> None:
        out = mod.reduce_transition(payload())
        event = dict(out["heritage_event"])
        event_id = event.pop("event_id")
        self.assertEqual(event_id, mod._event_id(event))


if __name__ == "__main__":
    unittest.main()
