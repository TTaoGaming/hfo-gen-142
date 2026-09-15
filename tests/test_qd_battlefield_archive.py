#!/usr/bin/env python3
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

spec = importlib.util.spec_from_file_location("qd_battlefield_archive", ROOT / "tools" / "qd_battlefield_archive.py")
qd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qd)

card_spec = importlib.util.spec_from_file_location("battlefield_test_helpers", ROOT / "tests" / "test_battlefield_gate.py")
helpers = importlib.util.module_from_spec(card_spec)
card_spec.loader.exec_module(helpers)


def write_card(directory, name, card):
    path = Path(directory) / f"{name}.json"
    path.write_text(json.dumps(card), encoding="utf-8")
    return path


class QDBattlefieldArchiveTests(unittest.TestCase):
    def test_distinct_niches_survive_without_global_primary(self):
        with tempfile.TemporaryDirectory() as td:
            paths = []
            for idx, domain in enumerate(("geometry", "scheduling", "document intelligence", "compiler kernels")):
                card = helpers.base_card()
                card["battlefield_id"] = f"bf-{idx}"
                card["domain"] = domain
                card["probability"]["p_beat_incumbent"] = 0.10 + idx * 0.10
                paths.append(write_card(td, f"bf-{idx}", card))
            out = qd.illuminate(paths)
            self.assertEqual(out["decision"], "ILLUMINATE")
            self.assertEqual(out["mode"], "QD_EXPLORE")
            self.assertIsNone(out["primary"])
            self.assertEqual(out["coverage"]["occupied_niches"], 4)
            self.assertEqual(out["coverage"]["elite_count"], 4)
            self.assertTrue(out["poka_yoke"]["global_primary_forbidden"])

    def test_dominated_candidate_does_not_displace_niche_champion(self):
        with tempfile.TemporaryDirectory() as td:
            weak = helpers.base_card(); weak["battlefield_id"] = "weak"
            strong = helpers.base_card(); strong["battlefield_id"] = "strong"
            strong["probability"]["p_beat_incumbent"] = 0.9
            strong["probability"]["p_public_proof_7d"] = 0.9
            strong["prestige"]["buyer_legibility"] = 0.95
            strong["evolution"]["canary"]["runtime_minutes"] = 1
            strong["evolution"]["canary"]["cost_usd"] = 0
            out = qd.illuminate([
                write_card(td, "weak", weak),
                write_card(td, "strong", strong),
            ])
            self.assertEqual(len(out["archive"]), 1)
            ids = [e["battlefield_id"] for e in out["archive"][0]["elites"]]
            self.assertEqual(ids, ["strong"])

    def test_crowded_cell_is_bounded_and_signals_morph(self):
        with tempfile.TemporaryDirectory() as td:
            paths = []
            # Trade off objectives so the cell has several nondominated candidates.
            for idx, (pbeat, p7, buyer) in enumerate(((0.9, 0.3, 0.7), (0.6, 0.8, 0.8), (0.3, 0.9, 0.95))):
                card = helpers.base_card()
                card["battlefield_id"] = f"trade-{idx}"
                card["probability"]["p_beat_incumbent"] = pbeat
                card["probability"]["p_public_proof_7d"] = p7
                card["prestige"]["buyer_legibility"] = buyer
                paths.append(write_card(td, f"trade-{idx}", card))
            out = qd.illuminate(paths, max_elites_per_niche=2)
            self.assertEqual(len(out["archive"]), 1)
            self.assertEqual(len(out["archive"][0]["elites"]), 2)
            self.assertEqual(len(out["coverage"]["crowded_niches"]), 1)
            self.assertIn("MORPH", out["poka_yoke"]["crowded_cell_action"])

    def test_replay_is_deterministic(self):
        with tempfile.TemporaryDirectory() as td:
            a = helpers.base_card(); a["battlefield_id"] = "a"; a["domain"] = "alpha"
            b = helpers.base_card(); b["battlefield_id"] = "b"; b["domain"] = "beta"
            paths = [write_card(td, "a", a), write_card(td, "b", b)]
            x = qd.illuminate(paths)
            y = qd.illuminate(paths)
            self.assertEqual(x["archive_sha256"], y["archive_sha256"])
            self.assertEqual(x["archive"], y["archive"])

    def test_killed_cards_are_rejected_not_archived(self):
        with tempfile.TemporaryDirectory() as td:
            good = helpers.base_card(); good["battlefield_id"] = "good"
            bad = helpers.base_card(); bad["battlefield_id"] = "bad"; bad["prestige"]["tier"] = "C"
            out = qd.illuminate([write_card(td, "good", good), write_card(td, "bad", bad)])
            self.assertEqual(out["coverage"]["admitted_candidates"], 1)
            self.assertEqual([x["battlefield_id"] for x in out["rejected"]], ["bad"])


if __name__ == "__main__":
    unittest.main()
