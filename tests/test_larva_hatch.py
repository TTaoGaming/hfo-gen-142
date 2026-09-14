import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"

spec_r = importlib.util.spec_from_file_location("reconcile_kernel", TOOLS / "reconcile_kernel.py")
reconcile_kernel = importlib.util.module_from_spec(spec_r)
spec_r.loader.exec_module(reconcile_kernel)

import sys
sys.modules["reconcile_kernel"] = reconcile_kernel
spec_h = importlib.util.spec_from_file_location("larva_hatch", TOOLS / "larva_hatch.py")
larva_hatch = importlib.util.module_from_spec(spec_h)
spec_h.loader.exec_module(larva_hatch)


def base_snapshot():
    return {
        "schema": "hfo.reconcile_snapshot.v0",
        "policy_version": "gen142-reconciler-r0",
        "actor": {"owner": "hfo-sigrun-va-r0", "phase": "IDLE"},
        "human_boundary": {"active": False},
        "dispatches": [],
        "cleanup_candidates": [],
        "worker_routes": [],
        "demand": [],
    }


class LarvaHatchTests(unittest.TestCase):
    def test_fresh_uuid_and_idle(self):
        receipt = larva_hatch.hatch(base_snapshot())
        self.assertEqual(receipt["decision"], "IDLE")
        self.assertEqual(receipt["morph_role"], "idle")
        self.assertTrue(receipt["carrier_uuid"])

    def test_demand_role_is_projected_not_chosen(self):
        s = base_snapshot()
        s["demand"] = [{
            "work_ref": "#13:edge-1",
            "priority": 10,
            "admitted": True,
            "blocked": False,
            "role": "falsifier",
        }]
        receipt = larva_hatch.hatch(s, "00000000-0000-4000-8000-000000000001")
        self.assertEqual(receipt["action"]["kind"], "SUBMIT_NEXT")
        self.assertEqual(receipt["morph_role"], "falsifier")

    def test_active_dispatch_suppresses_duplicate_morph(self):
        s = base_snapshot()
        s["dispatches"] = [{"active": True, "dispatch_ref": "run-1"}]
        receipt = larva_hatch.hatch(s)
        self.assertEqual(receipt["decision"], "WAIT")
        self.assertEqual(receipt["morph_role"], "observer")
        self.assertEqual(receipt["action"]["kind"], "WAIT_DISPATCH")

    def test_plan_is_stable_across_carrier_identity(self):
        s = base_snapshot()
        a = larva_hatch.hatch(s, "00000000-0000-4000-8000-000000000001")
        b = larva_hatch.hatch(s, "00000000-0000-4000-8000-000000000002")
        self.assertEqual(a["plan_sha256"], b["plan_sha256"])
        self.assertEqual(a["action"], b["action"])
        self.assertNotEqual(a["carrier_uuid"], b["carrier_uuid"])


if __name__ == "__main__":
    unittest.main()
