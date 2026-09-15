import importlib.util
from datetime import datetime, timedelta, timezone
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "tools" / "holon_gate.py"
spec = importlib.util.spec_from_file_location("holon_gate", GATE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def admitted():
    deadline = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat().replace("+00:00", "Z")
    return {
        "schema": "hfo.holon-mission.v1",
        "mission_id": "test-mission",
        "actor_id": "sigrun",
        "parent_actor_id": None,
        "carrier_id": "kimi-carrier-01",
        "domain": "domain_agnostic",
        "domain_explicit": False,
        "intent": "Find externally verified useful work without Tao CPR.",
        "fitness": {
            "primary": "externally_verified_useful_progress_per_tao_minute",
            "external_verification_required": True,
        },
        "verifier": {"id": "frozen-test-verifier", "frozen": True},
        "deadline_utc": deadline,
        "max_attempts": 2,
        "max_spend_usd": 0.0,
        "effect_ceiling": "NO_EXTERNAL_EFFECT",
        "receipt_sink": "github:TTaoGaming/hfo-gen-142#13",
        "semantic_owner": "hfo-sigrun-va-r0",
        "provider_policy": {
            "role": "leaf",
            "frontier_required": True,
            "provider_live": True,
            "provider_class": "frontier_subscription_bridge",
            "allow_local_fallback": False,
            "billing_class": "ZERO_MARGINAL",
            "allow_paid_fallback": False,
            "zero_marginal_verified": True,
            "billing_evidence_ref": "test:billing-zero",
            "quota_source": "test:free-quota",
            "quota_exhaustion": "ROTATE_OR_HOLD",
        },
        "human_boundaries": [],
        "tao_relay_required": False,
        "control_plane": {
            "new_control_plane": False,
            "recover_probe_repair_completed": True,
            "retired_owner": None,
            "gap_evidence_ref": None,
        },
        "promotion": {
            "requested": False,
            "verifier_receipt": None,
            "consumer_ack": None,
        },
    }

class HolonGateTests(unittest.TestCase):
    def test_admitted_mission_passes(self):
        self.assertEqual(mod.evaluate(admitted()), 0)

    def test_actor_cannot_be_carrier(self):
        m = admitted(); m["carrier_id"] = m["actor_id"]
        self.assertEqual(mod.evaluate(m), 1)

    def test_unselected_domain_is_blocked(self):
        m = admitted(); m["domain"] = "ai_reliability"
        self.assertEqual(mod.evaluate(m), 1)

    def test_frontier_cannot_fallback_local(self):
        m = admitted(); m["provider_policy"]["allow_local_fallback"] = True
        self.assertEqual(mod.evaluate(m), 1)

    def test_incremental_spend_above_standing_authority_is_blocked(self):
        m = admitted(); m["max_spend_usd"] = 0.01
        self.assertEqual(mod.evaluate(m), 1)

    def test_paid_provider_fallback_is_blocked(self):
        m = admitted(); m["provider_policy"]["allow_paid_fallback"] = True
        self.assertEqual(mod.evaluate(m), 1)

    def test_nonzero_marginal_provider_is_blocked_at_zero_daily_spend(self):
        m = admitted(); m["provider_policy"]["billing_class"] = "METERED_PAID"
        self.assertEqual(mod.evaluate(m), 1)

    def test_zero_marginal_provider_requires_billing_evidence(self):
        m = admitted(); m["provider_policy"]["billing_evidence_ref"] = None
        self.assertEqual(mod.evaluate(m), 1)

    def test_new_control_plane_is_blocked(self):
        m = admitted(); m["control_plane"]["new_control_plane"] = True
        self.assertEqual(mod.evaluate(m), 1)

    def test_recover_probe_repair_is_mandatory(self):
        m = admitted(); m["control_plane"]["recover_probe_repair_completed"] = False
        self.assertEqual(mod.evaluate(m), 1)

    def test_promotion_requires_verifier_and_ack(self):
        m = admitted(); m["promotion"]["requested"] = True
        self.assertEqual(mod.evaluate(m), 1)

    def test_tao_relay_requires_human_boundary(self):
        m = admitted(); m["tao_relay_required"] = True
        self.assertEqual(mod.evaluate(m), 1)

if __name__ == "__main__":
    unittest.main()
