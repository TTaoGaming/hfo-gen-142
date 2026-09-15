import copy
import importlib.util
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
spec = importlib.util.spec_from_file_location("battlefield_qd_archive", ROOT / "tools" / "battlefield_qd_archive.py")
qd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qd)


class QDArchiveTests(unittest.TestCase):
    def test_pareto_keeps_tradeoffs_and_drops_dominated(self):
        def row(name, vals):
            return {"battlefield_id": name, "objectives": dict(zip(qd.OBJECTIVE_NAMES, vals))}
        a = row("a", [1, 1, 1, 0.2, 0.9, 0.9])
        b = row("b", [0.8, 1, 1, 0.8, 0.8, 0.8])
        c = row("c", [0.7, 0.9, 0.9, 0.1, 0.7, 0.7])
        front, dominated = qd.pareto_partition([a, b, c])
        self.assertEqual({r["battlefield_id"] for r in front}, {"a", "b"})
        self.assertEqual([r["battlefield_id"] for r in dominated], ["c"])

    def test_crowding_preserves_extremes(self):
        rows = []
        for i in range(5):
            vals = {k: 0.5 for k in qd.OBJECTIVE_NAMES}
            vals["routing_score"] = i / 4
            vals["p_beat_incumbent"] = 1 - i / 4
            rows.append({"battlefield_id": f"r{i}", "objectives": vals})
        keep, evict = qd.truncate_front(rows, 2)
        self.assertEqual({r["battlefield_id"] for r in keep}, {"r0", "r4"})
        self.assertEqual(len(evict), 3)

    def test_niche_descriptor_separates_domains_and_resource_shapes(self):
        base = {
            "domain": "alpha",
            "target": {"proof_latency_hours": 0.5},
            "prestige": {"independent_verifier": True, "public_attribution": True},
            "evolution": {"canary": {"runtime_minutes": 30, "cost_usd": 0}},
        }
        other = copy.deepcopy(base)
        other["domain"] = "beta"
        other["evolution"]["canary"]["runtime_minutes"] = 1200
        self.assertNotEqual(qd.niche_key(qd.niche_descriptor(base)), qd.niche_key(qd.niche_descriptor(other)))

    def test_live_cards_are_not_collapsed_to_one_primary(self):
        paths = [
            ROOT / "BATTLEFIELDS" / "micro2026-moa-npu-stage1.json",
            ROOT / "BATTLEFIELDS" / "ieee-bigdata-traffic-flow-bench-2026.json",
            ROOT / "BATTLEFIELDS" / "tartanimu-iros2026.json",
        ]
        result = qd.archive(paths, max_elites_per_niche=4)
        self.assertTrue(result["collapse_forbidden"])
        self.assertIsNone(result["global_primary"])
        self.assertEqual(result["admitted_candidates"], 3)
        self.assertEqual(result["niche_count"], 3)
        self.assertEqual(result["champion_count"], 3)

    def test_public_coordination_is_not_material_authority(self):
        skill = (ROOT / ".agents/skills/twinling-pdsa/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("public #13 as `OBSERVE_ONLY`", skill)
        self.assertIn("authenticated internal controller claim/fence readback", skill)
        self.assertNotIn("Claim one under-covered edge on #13", skill)

    def test_backpressure_morphs_instead_of_relaunching(self):
        standard = (ROOT / "QD_EXPLORATION_STANDARD.md").read_text(encoding="utf-8")
        self.assertIn("SCHEDULE_FAILURE != SWARM_STALL", standard)
        self.assertIn("forbids replacement waves on that route", standard)
        self.assertIn("More larvae than useful unowned niches is backpressure", standard)
        self.assertIn("STALL_CONFIRMED", standard)
        self.assertIn("Never ask Tao to gather threads", standard)


if __name__ == "__main__":
    unittest.main()
