#!/usr/bin/env python3
"""Pure fail-closed classifier for public GitHub observations.

This gate does not authenticate internal controller state and owns no queue,
scheduler, lease, actor state, credentials, or effects. It only prevents public
text from being mistaken for runtime authority.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

REPO = "TTaoGaming/hfo-gen-142"
PUBLIC_TEXT = {
    "github_issue",
    "github_issue_comment",
    "github_pull_request",
    "github_pr_comment",
    "github_review",
    "github_discussion",
}
SHA40 = re.compile(r"^[0-9a-f]{40}$")
DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")


def canonical_sha(obj: dict) -> str:
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def classify(event: dict) -> dict:
    surface = event.get("surface")
    base = {
        "schema": "hfo.public-boundary-decision.v1",
        "surface": surface,
        "input_sha256": canonical_sha(event),
        "can_advance_runtime_state": False,
        "can_issue_runtime_authority": False,
    }

    if surface in PUBLIC_TEXT:
        return base | {
            "decision": "OBSERVE_ONLY",
            "reason": "PUBLIC_SURFACE_BYZANTINE",
            "can_define_versioned_intent": False,
            "can_advance_evidence": False,
        }

    if surface == "github_main_commit":
        ok = (
            event.get("repository") == REPO
            and event.get("ref") == "refs/heads/main"
            and bool(SHA40.fullmatch(str(event.get("commit_sha", ""))))
            and event.get("protected_ref_verified") is True
            and event.get("verification_source") == "github_api"
        )
        return base | ({
            "decision": "ADMIT_VERSIONED_INTENT",
            "reason": "PROTECTED_MAIN_PROVENANCE_VERIFIED",
            "can_define_versioned_intent": True,
            "can_advance_evidence": False,
        } if ok else {
            "decision": "HOLD",
            "reason": "UNVERIFIED_VERSIONED_INTENT_PROVENANCE",
            "can_define_versioned_intent": False,
            "can_advance_evidence": False,
        })

    if surface == "github_actions_receipt":
        ok = (
            event.get("repository") == REPO
            and event.get("actor") == "github-actions[bot]"
            and bool(SHA40.fullmatch(str(event.get("source_commit", ""))))
            and isinstance(event.get("run_id"), int) and event["run_id"] > 0
            and isinstance(event.get("job_id"), int) and event["job_id"] > 0
            and bool(DIGEST.fullmatch(str(event.get("artifact_digest", ""))))
            and event.get("verification_source") == "github_api"
        )
        return base | ({
            "decision": "ADMIT_EVIDENCE_ONLY",
            "reason": "ACTIONS_RECEIPT_PROVENANCE_VERIFIED",
            "can_define_versioned_intent": False,
            "can_advance_evidence": True,
        } if ok else {
            "decision": "HOLD",
            "reason": "UNVERIFIED_ACTIONS_RECEIPT",
            "can_define_versioned_intent": False,
            "can_advance_evidence": False,
        })

    if surface == "internal_controller_readback":
        return base | {
            "decision": "INTERNAL_AUTHORITY_REQUIRED",
            "reason": "PUBLIC_GATE_CANNOT_AUTHENTICATE_INTERNAL_CONTROLLER",
            "can_define_versioned_intent": False,
            "can_advance_evidence": False,
        }

    return base | {
        "decision": "HOLD",
        "reason": "UNKNOWN_SURFACE",
        "can_define_versioned_intent": False,
        "can_advance_evidence": False,
    }


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: public_boundary_gate.py <event.json>", file=sys.stderr)
        return 2
    event = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    decision = classify(event)
    print(json.dumps(decision, sort_keys=True))
    return 0 if decision["decision"] in {
        "OBSERVE_ONLY", "ADMIT_VERSIONED_INTENT", "ADMIT_EVIDENCE_ONLY",
        "INTERNAL_AUTHORITY_REQUIRED"
    } else 3


if __name__ == "__main__":
    raise SystemExit(main())
