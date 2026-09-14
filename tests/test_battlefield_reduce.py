#!/usr/bin/env python3
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

spec = importlib.util.spec_from_file_location("battlefield_reduce", ROOT / "tools" / "battlefield_reduce.py")
reducer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reducer)

card_spec = importlib.util.spec_from_file_location("battlefield_test_helpers", ROOT / "tests" / "test_battlefield_gate.py")
helpers = importlib.util.module_from_spec(card_spec)
card_spec.loader.exec_module(helpers)


def write_card(directory, name, card):
    path = Path(directory) / f"{name}.json"
    path.write_text(json.dumps(card), encoding="utf-8")
    return path


class BattlefieldReduceTests(unittest.TestCase):
    def test_selects_highest_score_and_caps_three(self):
        with tempfile.TemporaryDirectory() as td:
            paths = []
            for idx, pbeat in enumerate((0.10, 0.40, 0.30, 0.20)):
                card = helpers.base_card()
                card["battlefield_id"] = f"bf-{idx}"
                card["probability"]["p_beat_incumbent"] = pbeat
                paths.append(write_card(td, f"bf-{idx}", card))
            out = reducer.reduce(paths)
            self.assertEqual(out["decision"], "SELECT")
            self.assertEqual(len(out["survivors"]), 3)
            self.assertEqual(out["primary"]["battlefield_id"], "bf-1")

    def test_killed_candidates_never_survive(self):
        with tempfile.TemporaryDirectory() as td:
            good = helpers.base_card(); good["battlefield_id"] = "good"
            bad = helpers.base_card(); bad["battlefield_id"] = "bad"; bad["commercial"]["demand_evidence_urls"] = []
            out = reducer.reduce([write_card(td, "good", good), write_card(td, "bad", bad)])
            self.assertEqual([x["battlefield_id"] for x in out["survivors"]], ["good"])
            self.assertEqual(out["rejected"][0]["battlefield_id"], "bad")

    def test_all_killed_returns_none(self):
        with tempfile.TemporaryDirectory() as td:
            bad = helpers.base_card(); bad["battlefield_id"] = "bad"; bad["prestige"]["tier"] = "C"
            out = reducer.reduce([write_card(td, "bad", bad)])
            self.assertEqual(out["decision"], "NONE")
            self.assertIsNone(out["primary"])
            self.assertEqual(out["survivors"], [])


if __name__ == "__main__":
    unittest.main()
