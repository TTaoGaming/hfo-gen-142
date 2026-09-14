#!/usr/bin/env python3
import importlib.util
import io
import json
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("battlefield_gate", ROOT / "tools" / "battlefield_gate.py")
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)

NOW = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def base_card():
    return {
        "schema_version": "battlefield.v1",
        "battlefield_id": "test-prestige-crown",
        "observed_at_utc": NOW,
        "mission_class": "prestige_crown",
        "stage": "canary",
        "domain": "domain-agnostic-test",
        "target": {
            "board": "Credible Board",
            "track": "buyer-legible track",
            "metric": "score",
            "direction": "maximize",
            "incumbent_name": "incumbent",
            "incumbent_score": 84.0,
            "incumbent_checked_at_utc": NOW,
            "incumbent_url": "https://example.com/incumbent",
            "rules_url": "https://example.com/rules",
            "submission_url": "https://example.com/submit",
            "open_to_user": True,
            "public_proof_before_merge": True,
            "proof_latency_hours": 24,
        },
        "prestige": {
            "tier": "A",
            "institution_or_platform": "Recognized Institution",
            "independent_verifier": True,
            "verifier_url": "https://example.com/verifier",
            "public_attribution": True,
            "durable_public_evidence": True,
            "real_incumbent_competition": True,
            "competitor_count": 8,
            "accepted_submission_protocol": True,
            "buyer_legibility": 0.9,
        },
        "commercial": {
            "buyer_personas": ["operations buyer"],
            "offer": "verified optimization and reliability engagement",
            "demand_evidence_urls": ["https://example.com/demand"],
            "p_paid_conversation_7d": 0.20,
            "expected_cash_30d": 2000,
            "expected_cash_90d": 10000,
            "case_study_claim": "beat a public incumbent under accepted protocol",
        },
        "evolution": {
            "donors": [
                {"url": "https://example.com/donor1", "allowed": True},
                {"url": "https://example.com/donor2", "allowed": True},
            ],
            "mutable_axes": ["prompt", "tool_policy"],
            "weakness_hypothesis": "The public incumbent leaves an evidenced gap in orchestration and tool policy.",
            "gap_evidence_urls": ["https://example.com/gap"],
            "canary": {
                "runtime_minutes": 20,
                "cost_usd": 5,
                "status": "NOT_RUN",
                "promotion_rule": "promote only if score >= threshold",
            },
            "full_run": {"runtime_minutes": 720, "cost_usd": 150},
        },
        "execution": {
            "frontier_required": True,
            "provider_live": True,
            "provider_class": "frontier_subscription_bridge",
            "provider_route": "qualified-frontier",
            "no_weak_fallback": True,
            "evaluator_frozen": True,
            "local_reproduction_ready": True,
            "external_auth_ready": True,
            "carrier": "admitted-carrier",
        },
        "probability": {
            "p_beat_incumbent": 0.25,
            "p_public_proof_24h": 0.20,
            "p_public_proof_7d": 0.50,
            "confidence": 0.40,
            "basis": "Current field strength, donor density, canary cost, and publication path support this routing prior.",
        },
        "budget": {
            "max_spend_usd": 200,
            "max_operator_minutes": 45,
            "max_wallclock_hours": 12,
        },
        "evidence": [
            "https://example.com/e1",
            "https://example.com/e2",
            "https://example.com/e3",
        ],
    }


def verdict(card):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = gate.evaluate(card)
    return rc, json.loads(buf.getvalue())


class BattlefieldGateTests(unittest.TestCase):
    def test_qualified_canary_admitted(self):
        rc, out = verdict(base_card())
        self.assertEqual(rc, 0)
        self.assertEqual(out["verdict"], "ADMIT_CANARY")

    def test_low_prestige_proxy_killed(self):
        card = base_card()
        card["prestige"]["tier"] = "C"
        rc, out = verdict(card)
        self.assertNotEqual(rc, 0)
        self.assertEqual(out["verdict"], "KILL_PROXY")

    def test_no_income_path_killed(self):
        card = base_card()
        card["commercial"]["demand_evidence_urls"] = []
        rc, out = verdict(card)
        self.assertNotEqual(rc, 0)
        self.assertEqual(out["verdict"], "KILL_NO_INCOME_PATH")

    def test_frontier_substitution_killed(self):
        card = base_card()
        card["execution"]["no_weak_fallback"] = False
        rc, out = verdict(card)
        self.assertNotEqual(rc, 0)
        self.assertEqual(out["verdict"], "KILL_SUBSTITUTION")

    def test_random_fight_killed(self):
        card = base_card()
        card["evolution"]["gap_evidence_urls"] = []
        rc, out = verdict(card)
        self.assertNotEqual(rc, 0)
        self.assertEqual(out["verdict"], "KILL_RANDOM_FIGHT")

    def test_attack_requires_canary_pass(self):
        card = base_card()
        card["stage"] = "attack"
        rc, out = verdict(card)
        self.assertNotEqual(rc, 0)
        self.assertEqual(out["verdict"], "HOLD_CANARY_FIRST")

    def test_unproven_crown_rejected(self):
        card = base_card()
        card["stage"] = "claim"
        card["evolution"]["canary"]["status"] = "PASS"
        card["claim"] = {
            "crown_won": True,
            "public_result_url": "https://example.com/result",
            "accepted_protocol_result": True,
            "beats_incumbent": False,
            "attributable_identity": "Tommy Tai / Sigrun",
        }
        rc, out = verdict(card)
        self.assertNotEqual(rc, 0)
        self.assertEqual(out["verdict"], "REJECT_UNPROVEN_CROWN")


if __name__ == "__main__":
    unittest.main()
