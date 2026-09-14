import copy
import unittest
from adapter import ABI, PROFILE, digest, reduce_packet

class BoundaryTests(unittest.TestCase):
    def setUp(self):
        data = ["b", "a", "b"]
        self.packet = {"abi": ABI, "work_id": "test-1", "profile": PROFILE,
                       "effect_ceiling": "NONE", "input": data, "input_sha256": digest(data)}

    def test_external_oracle_and_replay(self):
        result = reduce_packet(self.packet)
        self.assertEqual(result["output"], {"items": [{"text": "a", "count": 1}, {"text": "b", "count": 2}], "total": 3})
        self.assertEqual(reduce_packet(self.packet), result)

    def test_changed_input_without_binding(self):
        self.packet["input"].append("c")
        with self.assertRaisesRegex(ValueError, "INPUT_HASH"):
            reduce_packet(self.packet)

    def test_forbidden_effects_and_profiles(self):
        for field, value in [("effect_ceiling", "SEND"), ("profile", "shell"), ("abi", "future")]:
            with self.subTest(field=field):
                p = copy.deepcopy(self.packet)
                p[field] = value
                with self.assertRaises(ValueError):
                    reduce_packet(p)

    def test_payload_limits_and_injection(self):
        for values in [[], ["x"] * 65, ["x" * 129], [True]]:
            p = copy.deepcopy(self.packet)
            p["input"] = values
            p["input_sha256"] = digest(values)
            with self.assertRaises(ValueError):
                reduce_packet(p)
        self.packet["command"] = "synthetic forbidden command"
        with self.assertRaisesRegex(ValueError, "PACKET_SHAPE"):
            reduce_packet(self.packet)

if __name__ == "__main__":
    unittest.main()
