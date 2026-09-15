import contextlib
import io
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import terminal_handoff_gate as gate
import workcell_runtime_v1 as runtime


class WorkCellRuntimeTest(unittest.TestCase):
    def gate(self, doc):
        with contextlib.redirect_stdout(io.StringIO()):
            return gate.evaluate(doc)

    def test_mission_complete_handoff_passes(self):
        result = {"work_id": "W1", "result_sha256": "a" * 64, "sources": [], "verdict": "PASS"}
        handoff = runtime.build_handoff(result, "https://github.com/x/y/issues/1#issuecomment-1", None)
        self.assertEqual(self.gate(handoff), 0)
        self.assertEqual(handoff["next"]["mode"], "MISSION_COMPLETE")

    def test_scheduled_reconcile_handoff_passes(self):
        receipt = {
            "receipt_type": "github_actions_watch", "owner": "github-actions",
            "receipt_id": "workflow:123", "status": "ARMED",
            "observed_utc": "2026-09-14T22:00:00Z",
            "provenance_ref": "https://api.github.com/repos/x/y/actions/workflows/workcell-runtime-v1.yml",
            "receipt_sha256": "b" * 64, "self_attested": False,
        }
        result = {"work_id": "W1", "result_sha256": "a" * 64, "sources": [{}], "verdict": "PASS"}
        handoff = runtime.build_handoff(result, "https://github.com/x/y/issues/1#issuecomment-1", receipt)
        self.assertEqual(self.gate(handoff), 0)
        self.assertEqual(handoff["next"]["mode"], "RECONCILE")

    def test_hold_result_is_bounded_terminal_not_controller_failure(self):
        result = {
            "work_id": "W-HOLD", "result_sha256": "c" * 64, "sources": [],
            "verdict": "FAIL", "next_state": "HOLD",
        }
        handoff = runtime.build_handoff(result, "https://github.com/x/y/issues/1#issuecomment-2", None)
        self.assertEqual(handoff["terminal_state"], "HOLD")
        self.assertEqual(self.gate(handoff), 0)

    def test_result_binding_and_hash_are_forcing_functions(self):
        selected = {"work_id": "W1", "spec_sha256": "b" * 64}
        result = {
            "schema": "hfo.research-cell-result.v1", "work_id": "W1",
            "spec_sha256": "b" * 64, "verdict": "FAIL", "next_state": "HOLD",
            "sources": [],
        }
        result["result_sha256"] = runtime.sha256(result)
        runtime.validate_worker_result(result, selected)
        bad = dict(result); bad["work_id"] = "W2"
        with self.assertRaisesRegex(RuntimeError, "WORK_ID_MISMATCH"):
            runtime.validate_worker_result(bad, selected)
        bad = dict(result); bad["result_sha256"] = "0" * 64
        with self.assertRaisesRegex(RuntimeError, "HASH_MISMATCH"):
            runtime.validate_worker_result(bad, selected)

    def test_undeclared_terminal_state_fails_closed(self):
        with self.assertRaisesRegex(RuntimeError, "TERMINAL_STATE_UNDECLARED"):
            runtime.terminal_state_for({"next_state": "MAYBE", "verdict": "UNKNOWN"})

    def test_unknown_worker_schema_fails_closed(self):
        with self.assertRaises(RuntimeError):
            runtime.worker_for({"schema": "hfo.unknown.v9"})


if __name__ == "__main__":
    unittest.main()
