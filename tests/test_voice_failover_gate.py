import copy
import json
import unittest
from pathlib import Path

from tools import voice_failover_gate as vg

ROOT = Path(__file__).resolve().parents[1]
POLICY = json.loads((ROOT / "VOICE" / "VOICE_FAILOVER_POLICY_V1.json").read_text())


def checkpoint():
    return {
        "schema": "hfo.voice-carrier-checkpoint.v1",
        "carrier_uuid": "5848d5dd-8792-443c-a9d3-c60b9cbaf8c2",
        "predecessor_uuid": None,
        "observed_utc": "2026-09-15T16:28:23Z",
        "anchor_commit": "b62307c6676b1c113cc9c7b55c6000d3164ada52",
        "cursor_comment_id": 5683943580,
        "state": "RECOVERED",
        "recovery_reason": "CARRIER_ERROR",
        "authority_inherited": False,
        "canonical_recovery": "github:TTaoGaming/hfo-gen-142#13",
        "next_machine_edge": "VOICE_FAILOVER_REDUCER",
    }


class VoiceFailoverGateTests(unittest.TestCase):
    def test_policy_is_recovery_only(self):
        self.assertEqual(vg.validate_policy(POLICY)["authority_class"], "RECOVERY_EVIDENCE_ONLY")

    def test_replacement_carrier_is_admitted_as_evidence_only(self):
        result = vg.validate_checkpoint(checkpoint(), POLICY)
        self.assertEqual(result["decision"], "ADMIT_RECOVERY_EVIDENCE")
        self.assertFalse(result["authority_granted"])

    def test_carrier_uuid_reuse_is_refused(self):
        value = checkpoint()
        value["predecessor_uuid"] = value["carrier_uuid"]
        with self.assertRaisesRegex(vg.FailoverError, "UUID_REUSE"):
            vg.validate_checkpoint(value, POLICY)

    def test_authority_inheritance_is_refused(self):
        value = checkpoint()
        value["authority_inherited"] = True
        with self.assertRaisesRegex(vg.FailoverError, "AUTHORITY_REFUSED"):
            vg.validate_checkpoint(value, POLICY)

    def test_wrong_recovery_surface_is_refused(self):
        value = checkpoint()
        value["canonical_recovery"] = "github:somewhere/else#1"
        with self.assertRaisesRegex(vg.FailoverError, "AUTHORITY_REFUSED"):
            vg.validate_checkpoint(value, POLICY)

    def test_unknown_fields_are_refused(self):
        value = checkpoint()
        value["authority"] = "Sigrun"
        with self.assertRaisesRegex(vg.FailoverError, "FIELDS_REFUSED"):
            vg.validate_checkpoint(value, POLICY)

    def test_anchor_must_be_immutable_commit(self):
        value = checkpoint()
        value["anchor_commit"] = "main"
        with self.assertRaisesRegex(vg.FailoverError, "ANCHOR_REFUSED"):
            vg.validate_checkpoint(value, POLICY)

    def test_policy_cannot_grant_actor_or_seat(self):
        for field in ("inherit_actor", "inherit_seat", "inherit_authority"):
            bad = copy.deepcopy(POLICY)
            bad[field] = True
            with self.assertRaisesRegex(vg.FailoverError, "INHERITANCE_REFUSED"):
                vg.validate_policy(bad)


if __name__ == "__main__":
    unittest.main()

# Anchor-level regression: durable identity must never point at one live carrier.
class VoiceAnchorFailoverTests(unittest.TestCase):
    def test_anchor_has_no_mutable_current_carrier_pointer(self):
        text = (ROOT / "VOICE" / "SIGRUN_VOICE_ANCHOR.md").read_text(encoding="utf-8")
        self.assertNotIn("Current carrier UUID:", text)
        self.assertIn("VOICE/VOICE_FAILOVER_POLICY_V1.json", text)
        self.assertIn("Do not maintain a mutable \"current voice carrier\" registry", text)

    def test_agents_startup_requires_voice_failover_policy(self):
        text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("VOICE/SIGRUN_HQ_LATEST.md", text)
        self.assertIn("VOICE/VOICE_FAILOVER_POLICY_V1.json", text)
        self.assertIn("voice_failover_gate.py", text)

class VoiceFailoverRedQueenTests(unittest.TestCase):
    def test_policy_sequence_tamper_is_refused(self):
        bad = copy.deepcopy(POLICY)
        bad["required_sequence"] = bad["required_sequence"][:-1]
        with self.assertRaisesRegex(vg.FailoverError, "SEQUENCE_REFUSED"):
            vg.validate_policy(bad)

    def test_naive_timestamp_is_refused(self):
        value = checkpoint()
        value["observed_utc"] = "2026-09-15T16:28:23"
        with self.assertRaisesRegex(vg.FailoverError, "TIME_REFUSED"):
            vg.validate_checkpoint(value, POLICY)

    def test_checkout_head_must_match_anchor_commit(self):
        value = checkpoint()
        value["anchor_commit"] = "0" * 40
        with self.assertRaisesRegex(vg.FailoverError, "ANCHOR_COMMIT_MISMATCH"):
            vg.verify_checkout(value, ROOT)
