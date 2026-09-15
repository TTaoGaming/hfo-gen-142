import importlib.util
import unittest
from pathlib import Path

MOD_PATH = Path(__file__).resolve().parents[1] / "tools" / "hexagonal_runtime_gate.py"
SPEC = importlib.util.spec_from_file_location("hexagonal_runtime_gate", MOD_PATH)
mod = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(mod)


def fixture():
    job = {
        "job_sha256": "j" * 64,
        "task_sha256": "t" * 64,
        "capability_contract_sha256": "c" * 64,
        "semantic_output_sha256": "o" * 64,
        "verifier_id": "frozen-exact-output-v1",
        "semantic_owner": "hfo-sigrun-va-r0",
    }
    def receipt(adapter, provider, harness, host):
        return {
            "schema": mod.RECEIPT_SCHEMA,
            "adapter_id": adapter,
            "provider_id": provider,
            "harness_id": harness,
            "host_id": host,
            "job_sha256": job["job_sha256"],
            "task_sha256": job["task_sha256"],
            "capability_contract_sha256": job["capability_contract_sha256"],
            "semantic_output_sha256": job["semantic_output_sha256"],
            "completion_schema": mod.COMPLETION_SCHEMA,
            "verifier_id": job["verifier_id"],
            "verifier_receipt_sha256": "v" * 64,
            "consumer_ack_sha256": "a" * 64,
            "billing_class": mod.ZERO_MARGINAL,
            "effect_ceiling": "NONE",
            "terminal": True,
            "controller_observed": True,
            "independent_verifier": True,
            "tao_hot_loop_actions": 0,
        }
    return {
        "schema": mod.SCHEMA,
        "job": job,
        "receipts": [
            receipt("kimi-r1", "kimi", "kimi-cli", "lenovo"),
            receipt("codex-r1", "openai", "codex-cli", "oracle"),
        ],
        "require_distinct_hosts": True,
    }


class GateTests(unittest.TestCase):
    def assert_hold(self, value, code):
        rc, out = mod.evaluate(value)
        self.assertEqual(rc, 1)
        self.assertEqual(out["verdict"], code)

    def test_passes_two_distinct_closed_adapters(self):
        rc, out = mod.evaluate(fixture())
        self.assertEqual(rc, 0)
        self.assertEqual(out["verdict"], "HEXAGONAL_RUNTIME_PASS")

    def test_direct_leaf_canary_is_not_enough(self):
        value = fixture()
        value["receipts"][1]["controller_observed"] = False
        self.assert_hold(value, "CONTROLLER_OBSERVATION_REQUIRED")

    def test_consumer_ack_is_required(self):
        value = fixture()
        value["receipts"][1]["consumer_ack_sha256"] = ""
        self.assert_hold(value, "RECEIPT_BINDING_REQUIRED")

    def test_same_provider_is_not_hexagonal(self):
        value = fixture()
        value["receipts"][1]["provider_id"] = "kimi"
        self.assert_hold(value, "DISTINCT_PROVIDER_REQUIRED")

    def test_same_harness_is_not_hexagonal(self):
        value = fixture()
        value["receipts"][1]["harness_id"] = "kimi-cli"
        self.assert_hold(value, "DISTINCT_HARNESS_REQUIRED")

    def test_output_drift_holds(self):
        value = fixture()
        value["receipts"][1]["semantic_output_sha256"] = "x" * 64
        self.assert_hold(value, "RECEIPT_JOB_BINDING_MISMATCH")

    def test_paid_route_holds_under_zero_incremental_budget(self):
        value = fixture()
        value["receipts"][1]["billing_class"] = "PAID_API"
        self.assert_hold(value, "BILLING_CLASS_REFUSED")

    def test_host_substitution_can_be_required(self):
        value = fixture()
        value["receipts"][1]["host_id"] = "lenovo"
        self.assert_hold(value, "DISTINCT_HOST_REQUIRED")

    def test_tao_hot_loop_must_remain_zero(self):
        value = fixture()
        value["receipts"][0]["tao_hot_loop_actions"] = 1
        self.assert_hold(value, "TAO_HOT_LOOP_NOT_ZERO")


if __name__ == "__main__":
    unittest.main()
