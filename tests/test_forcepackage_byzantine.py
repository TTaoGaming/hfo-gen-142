import copy
import unittest

from tests.test_forcepackage_gate import base_package
from tools.forcepackage_gate import Refused, compile_actor_intents


class ForcePackageByzantineRegressionTests(unittest.TestCase):
    def assert_verdict(self, package, expected):
        with self.assertRaises(Refused) as ctx:
            compile_actor_intents(package)
        self.assertEqual(expected, ctx.exception.verdict)

    def test_unhashable_archetype_values_fail_closed(self):
        for value in ([], {}, ["LING"], {"name": "LING"}):
            with self.subTest(value=value):
                p = base_package()
                p["formations"][0]["archetype"] = copy.deepcopy(value)
                self.assert_verdict(p, "ARCHETYPE_UNVERSIONED")

    def test_unhashable_human_boundary_values_fail_closed(self):
        for value in ([], {}, ["secret"], {"kind": "secret"}):
            with self.subTest(value=value):
                p = base_package()
                p["human_boundaries"] = [copy.deepcopy(value)]
                self.assert_verdict(p, "HUMAN_BOUNDARY_INVALID")

    def test_duplicate_human_boundaries_fail_closed(self):
        p = base_package()
        p["human_boundaries"] = ["secret", "secret"]
        self.assert_verdict(p, "HUMAN_BOUNDARY_INVALID")

    def test_known_boundary_is_admitted(self):
        p = base_package()
        p["human_boundaries"] = ["secret"]
        self.assertEqual("ADMIT", compile_actor_intents(p)["decision"])


if __name__ == "__main__":
    unittest.main()
