import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TWINLING = ROOT / ".agents/skills/twinling-pdsa/SKILL.md"
ROACH = ROOT / ".agents/skills/roach-fanin/SKILL.md"
BOUNDARY = ROOT / "PUBLIC_AUTHORITY_BOUNDARY.md"


def synthetic_race(results):
    """Policy canary: ambiguity or split-brain must fail closed."""
    authoritative = [r for r in results if r.get("admitted") and r.get("readback") and r.get("fence")]
    if len(authoritative) != 1:
        return {r["carrier"]: {"material_work": False, "morph_before_effect": False, "terminal_count": 1} for r in results}
    winner = authoritative[0]["carrier"]
    return {
        r["carrier"]: {
            "material_work": r["carrier"] == winner,
            "morph_before_effect": r["carrier"] != winner and r.get("observed_owner") == winner,
            "terminal_count": 1,
        }
        for r in results
    }


class SkillClaimBoundaryTests(unittest.TestCase):
    def test_skills_bind_claims_to_internal_authority(self):
        twinling = TWINLING.read_text(encoding="utf-8")
        roach = ROACH.read_text(encoding="utf-8")
        boundary = BOUNDARY.read_text(encoding="utf-8")
        self.assertIn("ZERG LARVA HATCH CONTRACT `5671214300`", twinling)
        self.assertIn("authenticated internal controller", twinling)
        self.assertIn("authenticated internal controller", roach)
        self.assertIn("public comment is evidence only and never selects ownership", twinling)
        self.assertIn("public issue/comment ordering never decides ownership", roach)
        self.assertIn("independent verifier and downstream ConsumerAck", twinling)
        self.assertNotIn("claim one under-covered edge on #13", twinling.lower())
        self.assertNotIn("earlier durable claim wins", roach.lower())
        self.assertIn("OBSERVE_ONLY", boundary)
        self.assertIn("INTERNAL_AUTHORITY_REQUIRED", boundary)

    def test_one_fenced_winner_loser_morphs_before_effect(self):
        result = synthetic_race([
            {"carrier": "A", "admitted": True, "readback": True, "fence": "f1", "observed_owner": "A"},
            {"carrier": "B", "admitted": False, "readback": True, "fence": None, "observed_owner": "A"},
        ])
        self.assertTrue(result["A"]["material_work"])
        self.assertFalse(result["B"]["material_work"])
        self.assertTrue(result["B"]["morph_before_effect"])
        self.assertEqual(1, result["A"]["terminal_count"])
        self.assertEqual(1, result["B"]["terminal_count"])

    def test_split_brain_and_unreadable_authority_fail_closed(self):
        split = synthetic_race([
            {"carrier": "A", "admitted": True, "readback": True, "fence": "f1"},
            {"carrier": "B", "admitted": True, "readback": True, "fence": "f2"},
        ])
        self.assertFalse(any(v["material_work"] for v in split.values()))
        unreadable = synthetic_race([
            {"carrier": "A", "admitted": True, "readback": False, "fence": "f1"},
            {"carrier": "B", "admitted": False, "readback": True, "fence": None, "observed_owner": "A"},
        ])
        self.assertFalse(any(v["material_work"] for v in unreadable.values()))


if __name__ == "__main__":
    unittest.main()
