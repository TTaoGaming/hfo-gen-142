import unittest
from pathlib import Path


SKILL = Path(__file__).parents[1] / ".agents" / "skills" / "twinling-pdsa" / "SKILL.md"


def synthetic_race(claims):
    """Policy canary only: first admitted durable claim owns material work."""
    admitted = [c for c in claims if c["admitted"] and c["readback"]]
    winner = min(admitted, key=lambda c: c["sequence"])["carrier"] if admitted else None
    return {
        c["carrier"]: {
            "material_work": c["carrier"] == winner,
            "morph_before_effect": winner is not None and c["carrier"] != winner,
            "terminal_count": 1,
        }
        for c in claims
    }


class TwinlingClaimRaceContractTests(unittest.TestCase):
    def test_skill_binds_hatch_pointer_to_admitted_claim_readback(self):
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("ZERG LARVA HATCH CONTRACT `5671214300`", text)
        self.assertIn("admitted durable claim", text)
        self.assertIn("immediately read that claim back", text)
        self.assertIn("arbitrary issue/comment claim never wins authority", text)
        self.assertIn("final newest-first collision/readback check", text)
        self.assertIn("independent verifier and downstream ConsumerAck", text)

    def test_two_carrier_same_lane_race_has_one_material_worker(self):
        result = synthetic_race([
            {"carrier": "A", "sequence": 10, "admitted": True, "readback": True},
            {"carrier": "B", "sequence": 11, "admitted": True, "readback": True},
        ])
        self.assertTrue(result["A"]["material_work"])
        self.assertFalse(result["B"]["material_work"])
        self.assertTrue(result["B"]["morph_before_effect"])
        self.assertEqual(1, result["A"]["terminal_count"])
        self.assertEqual(1, result["B"]["terminal_count"])

    def test_unreadable_claim_never_owns_work(self):
        result = synthetic_race([
            {"carrier": "A", "sequence": 10, "admitted": True, "readback": False},
            {"carrier": "B", "sequence": 11, "admitted": True, "readback": True},
        ])
        self.assertFalse(result["A"]["material_work"])
        self.assertTrue(result["B"]["material_work"])


if __name__ == "__main__":
    unittest.main()
