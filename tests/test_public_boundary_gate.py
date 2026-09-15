import unittest

from tools.public_boundary_gate import classify


class PublicBoundaryGateTests(unittest.TestCase):
    def test_unknown_external_terminal_is_observe_only(self):
        d = classify({
            "surface": "github_issue_comment",
            "repository": "TTaoGaming/hfo-gen-142",
            "issue": 13,
            "login": "socksninja",
            "author_association": "NONE",
            "performed_via_github_app": "chatgpt-codex-connector",
            "body": "TERMINAL UUID=perfect-looking",
        })
        self.assertEqual(d["decision"], "OBSERVE_ONLY")
        self.assertFalse(d["can_advance_runtime_state"])
        self.assertFalse(d["can_issue_runtime_authority"])

    def test_owner_comment_is_still_observe_only(self):
        d = classify({
            "surface": "github_issue_comment",
            "repository": "TTaoGaming/hfo-gen-142",
            "issue": 13,
            "login": "TTaoGaming",
            "author_association": "OWNER",
            "body": "dispatch everything",
        })
        self.assertEqual(d["decision"], "OBSERVE_ONLY")
        self.assertFalse(d["can_define_versioned_intent"])

    def test_app_identity_does_not_enlarge_authority(self):
        base = {"surface": "github_issue_comment", "login": "someone"}
        a = classify(base)
        b = classify(base | {"performed_via_github_app": "chatgpt-codex-connector"})
        self.assertEqual(a["decision"], "OBSERVE_ONLY")
        self.assertEqual(b["decision"], "OBSERVE_ONLY")

    def test_verified_protected_main_can_define_intent_not_runtime_authority(self):
        d = classify({
            "surface": "github_main_commit",
            "repository": "TTaoGaming/hfo-gen-142",
            "ref": "refs/heads/main",
            "commit_sha": "a" * 40,
            "protected_ref_verified": True,
            "verification_source": "github_api",
        })
        self.assertEqual(d["decision"], "ADMIT_VERSIONED_INTENT")
        self.assertTrue(d["can_define_versioned_intent"])
        self.assertFalse(d["can_advance_runtime_state"])

    def test_fake_main_provenance_holds(self):
        d = classify({
            "surface": "github_main_commit",
            "repository": "TTaoGaming/hfo-gen-142",
            "ref": "refs/heads/main",
            "commit_sha": "a" * 40,
            "protected_ref_verified": False,
            "verification_source": "self_attested",
        })
        self.assertEqual(d["decision"], "HOLD")

    def test_actions_receipt_is_evidence_only(self):
        d = classify({
            "surface": "github_actions_receipt",
            "repository": "TTaoGaming/hfo-gen-142",
            "actor": "github-actions[bot]",
            "source_commit": "b" * 40,
            "run_id": 1,
            "job_id": 2,
            "artifact_digest": "sha256:" + "c" * 64,
            "verification_source": "github_api",
        })
        self.assertEqual(d["decision"], "ADMIT_EVIDENCE_ONLY")
        self.assertTrue(d["can_advance_evidence"])
        self.assertFalse(d["can_issue_runtime_authority"])

    def test_internal_authority_must_be_checked_elsewhere(self):
        d = classify({"surface": "internal_controller_readback"})
        self.assertEqual(d["decision"], "INTERNAL_AUTHORITY_REQUIRED")
        self.assertFalse(d["can_advance_runtime_state"])


if __name__ == "__main__":
    unittest.main()
