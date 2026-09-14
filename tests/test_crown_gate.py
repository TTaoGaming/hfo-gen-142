import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "tools" / "crown_gate.py"
spec = importlib.util.spec_from_file_location("crown_gate", GATE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def qualified():
    return {
        "independent_verifier": True,
        "public_attribution": True,
        "real_incumbent_competition": True,
        "buyer_mapping": True,
        "durable_public_evidence": True,
        "accepted_submission_protocol": True,
        "frontier_required": True,
        "provider_live": True,
        "provider_class": "frontier_subscription_bridge",
    }

class CrownGateTests(unittest.TestCase):
    def test_proxy_crown_rejected(self):
        c = qualified(); c["real_incumbent_competition"] = False
        self.assertEqual(mod.evaluate(c), 1)
    def test_frontier_unavailable_rejected(self):
        c = qualified()
        c["provider_live"] = False
        self.assertEqual(mod.evaluate(c), 1)

    def test_qualified_candidate_admitted(self):
        self.assertEqual(mod.evaluate(qualified()), 0)
